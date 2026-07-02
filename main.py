from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
SESSION_TTL_SECONDS = 60 * 60
MFA_PENDING_TTL_SECONDS = 5 * 60
VOTING_TOKEN_TTL_SECONDS = 10 * 60
PASSWORD_HASH_ITERATIONS = 200_000


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt.hex()}${dk.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, iters_str, salt_hex, expected_hex = stored_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iters_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)
    except (ValueError, TypeError):
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(candidate, expected)


def _b32_decode(secret: str) -> bytes:
    padding = "=" * ((8 - (len(secret) % 8)) % 8)
    return base64.b32decode(secret + padding, casefold=True)


def _totp_code(secret: str, for_time: int | None = None, step: int = 30) -> str:
    now = int(time.time()) if for_time is None else for_time
    counter = now // step
    key = _b32_decode(secret)
    msg = counter.to_bytes(8, "big")
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = (
        ((digest[offset] & 0x7F) << 24)
        | ((digest[offset + 1] & 0xFF) << 16)
        | ((digest[offset + 2] & 0xFF) << 8)
        | (digest[offset + 3] & 0xFF)
    )
    return f"{binary % 1_000_000:06d}"


def _verify_totp(secret: str, code: str, drift_windows: int = 1) -> bool:
    if not code.isdigit() or len(code) != 6:
        return False
    now = int(time.time())
    for drift in range(-drift_windows, drift_windows + 1):
        if hmac.compare_digest(_totp_code(secret, for_time=now + drift * 30), code):
            return True
    return False


def _random_base32_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class MfaRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class TokenRequest(BaseModel):
    electionId: str = Field(min_length=1, max_length=64)


class BallotSubmitRequest(BaseModel):
    electionId: str = Field(min_length=1, max_length=64)
    districtId: str = Field(min_length=1, max_length=64)
    choices: list[str] = Field(min_length=1)
    tokenId: str = Field(min_length=1, max_length=128)


class TotpConfirmRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


app = FastAPI(title="SVP Secure Voting Platform API")

USERS: dict[str, dict[str, Any]] = {
    "demo": {
        "voterId": str(uuid4()),
        "username": "demo",
        "passwordHash": _hash_password("demo123"),
        "mfaEnabled": False,
        "mfaSecret": None,
    }
}
SESSIONS: dict[str, dict[str, Any]] = {}
PENDING_MFA: dict[str, int] = {}
VOTING_TOKENS: dict[str, dict[str, Any]] = {}
BALLOTS: dict[str, dict[str, Any]] = {}
LAST_BALLOT_HASH_BY_ELECTION: dict[str, str] = {}
AUDIT_LOG: list[dict[str, Any]] = []


def _audit(event_type: str, payload: dict[str, Any]) -> None:
    AUDIT_LOG.append({"eventType": event_type, "payload": payload, "ts": int(time.time())})


def _issue_session(username: str) -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = {"username": username, "expiresAt": int(time.time()) + SESSION_TTL_SECONDS}
    return token


def _active_username_from_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    session = SESSIONS.get(token)
    if not session or session["expiresAt"] < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    return session["username"]


@app.post("/api/auth/login")
def auth_login(body: LoginRequest) -> dict[str, Any]:
    user = USERS.get(body.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not _verify_password(body.password, user["passwordHash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if user["mfaEnabled"]:
        PENDING_MFA[body.username] = int(time.time()) + MFA_PENDING_TTL_SECONDS
        _audit("auth.login.password_ok", {"username": body.username, "mfaRequired": True})
        return {"mfaRequired": True}

    session_token = _issue_session(body.username)
    _audit("auth.login.success", {"username": body.username, "mfaRequired": False})
    return {"mfaRequired": False, "sessionToken": session_token}


@app.post("/api/auth/mfa")
def auth_mfa_verify(body: MfaRequest) -> dict[str, Any]:
    now = int(time.time())
    pending_users = [u for u, exp in PENDING_MFA.items() if exp >= now]
    if len(pending_users) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active MFA challenge")

    username = pending_users[0]
    user = USERS[username]
    if not user["mfaSecret"] or not _verify_totp(user["mfaSecret"], body.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")

    PENDING_MFA.pop(username, None)
    session_token = _issue_session(username)
    _audit("auth.mfa.success", {"username": username})
    return {"sessionToken": session_token}


@app.post("/api/auth/token")
def auth_token_request(body: TokenRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    username = _active_username_from_bearer(authorization)
    token_id = str(uuid4())
    expires_at = int(time.time()) + VOTING_TOKEN_TTL_SECONDS
    VOTING_TOKENS[token_id] = {
        "username": username,
        "electionId": body.electionId,
        "expiresAt": expires_at,
        "used": False,
    }
    _audit("token.issued", {"username": username, "electionId": body.electionId, "tokenId": token_id})
    return {"tokenId": token_id, "expiresAt": expires_at}


@app.post("/api/ballot/submit")
def ballot_submit(body: BallotSubmitRequest) -> dict[str, Any]:
    token = VOTING_TOKENS.get(body.tokenId)
    now = int(time.time())
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid voting token")
    if token["used"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Voting token already used")
    if token["expiresAt"] < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Voting token expired")
    if token["electionId"] != body.electionId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Election mismatch for token")

    ballot_id = str(uuid4())
    previous_hash = LAST_BALLOT_HASH_BY_ELECTION.get(body.electionId, "")
    record = {
        "ballotId": ballot_id,
        "electionId": body.electionId,
        "districtId": body.districtId,
        "choices": body.choices,
        "timestamp": now,
        "previousHash": previous_hash,
    }
    canonical = json.dumps(record, separators=(",", ":"), sort_keys=True)
    ballot_hash = hashlib.sha256((previous_hash + canonical).encode("utf-8")).hexdigest()
    record["ballotHash"] = ballot_hash

    BALLOTS[ballot_id] = record
    LAST_BALLOT_HASH_BY_ELECTION[body.electionId] = ballot_hash
    token["used"] = True
    _audit("ballot.submitted", {"ballotId": ballot_id, "electionId": body.electionId, "districtId": body.districtId})
    return {"ballotId": ballot_id, "ballotHash": ballot_hash}


@app.get("/api/verify/{ballot_id}")
def verify_ballot(ballot_id: str) -> dict[str, Any]:
    ballot = BALLOTS.get(ballot_id)
    if not ballot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ballot not found")
    return {
        "ballotId": ballot["ballotId"],
        "ballotHash": ballot["ballotHash"],
        "districtId": ballot["districtId"],
        "electionId": ballot["electionId"],
        "timestamp": ballot["timestamp"],
    }


@app.post("/api/auth/totp/setup")
def auth_totp_setup() -> dict[str, Any]:
    user = USERS["demo"]
    secret = _random_base32_secret()
    user["mfaSecret"] = secret
    username = user["username"]
    issuer = "Clear Voting Seal"
    otpauth_url = f"otpauth://totp/{issuer}:{username}?secret={secret}&issuer={issuer}&digits=6&period=30"
    _audit("totp.setup", {"username": username})
    return {"secret": secret, "otpauthUrl": otpauth_url, "qrImageUrl": None}


@app.post("/api/auth/totp/confirm")
def auth_totp_confirm(body: TotpConfirmRequest) -> dict[str, Any]:
    user = USERS["demo"]
    secret = user.get("mfaSecret")
    if not secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No TOTP setup in progress")
    if not _verify_totp(secret, body.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")
    user["mfaEnabled"] = True
    _audit("totp.confirmed", {"username": user["username"]})
    return {"enabled": True}


app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")
