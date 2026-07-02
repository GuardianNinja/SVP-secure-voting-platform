from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class NodeRole(str, Enum):
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"


@dataclass
class RaftNode:
    node_id: str
    current_term: int = 0
    role: NodeRole = NodeRole.FOLLOWER
    voted_for: str | None = None

    def begin_election(self) -> None:
        self.current_term += 1
        self.role = NodeRole.CANDIDATE
        self.voted_for = self.node_id

    def become_leader(self) -> None:
        self.role = NodeRole.LEADER

    def become_follower(self) -> None:
        self.role = NodeRole.FOLLOWER

