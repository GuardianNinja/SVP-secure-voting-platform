from __future__ import annotations

from typing import Any


def verification_response(ballot: dict[str, Any]) -> dict[str, Any]:
    return {
        "ballotId": ballot["ballotId"],
        "ballotHash": ballot["ballotHash"],
        "districtId": ballot["districtId"],
        "electionId": ballot["electionId"],
        "timestamp": ballot["timestamp"],
    }

