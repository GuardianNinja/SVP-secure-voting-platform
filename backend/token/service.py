from __future__ import annotations

from dataclasses import dataclass
from time import time
from uuid import uuid4


@dataclass(frozen=True)
class VotingToken:
    token_id: str
    election_id: str
    expires_at: int


class TokenService:
    def issue(self, election_id: str, ttl_seconds: int = 600) -> VotingToken:
        return VotingToken(token_id=str(uuid4()), election_id=election_id, expires_at=int(time()) + ttl_seconds)

