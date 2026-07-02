from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Election:
    election_id: str
    name: str
    state: str

