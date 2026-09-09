from __future__ import annotations

from enum import Enum, unique


@unique
class Outcome(Enum):
    SUCCESS = "SUCCESS"
    DEADLOCK = "DEADLOCK"
    CUTOFF = "CUTOFF"
    FAILURE = "FAILURE"

    @property
    def is_success(self) -> bool:
        return self is Outcome.SUCCESS
