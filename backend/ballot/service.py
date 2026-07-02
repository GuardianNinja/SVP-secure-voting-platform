from __future__ import annotations

import hashlib
import json
from typing import Any


def compute_ballot_hash(ballot_record: dict[str, Any], previous_hash: str = "") -> str:
    canonical = json.dumps(ballot_record, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256((previous_hash + canonical).encode("utf-8")).hexdigest()

