from __future__ import annotations


class AuthService:
    """Authentication and MFA service boundary."""

    def issue_session(self, username: str) -> dict[str, str]:
        return {"username": username, "sessionToken": "scaffold-session-token"}

