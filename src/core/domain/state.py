from __future__ import annotations

from collections.abc import Iterable

from core.rules.domain.base import CAPACITIES, TOTAL_DISKS, Disk, Peg, Stack, State

__all__ = [
    "CAPACITIES",
    "EMPTY_STATE",
    "TOTAL_DISKS",
    "Disk",
    "InvalidStateError",
    "Peg",
    "Stack",
    "State",
    "build_state",
    "disks_of",
    "is_valid",
    "stack_of",
    "top_of",
    "validate",
]

EMPTY_STATE: State = ((), (), ())


class InvalidStateError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(f"invalid state: {reason}")
        self.reason = reason


def build_state(h1: Iterable[Disk], h2: Iterable[Disk], h3: Iterable[Disk]) -> State:
    state: State = (tuple(h1), tuple(h2), tuple(h3))
    validate(state)
    return state


def validate(state: State) -> None:
    if len(state) != len(Peg):
        raise InvalidStateError(f"expected {len(Peg)} pegs, got {len(state)}")

    for peg in Peg:
        capacity = CAPACITIES[peg]
        if len(state[peg]) > capacity:
            raise InvalidStateError(
                f"peg {peg.name} holds {len(state[peg])} disks, capacity is {capacity}"
            )

    disks = disks_of(state)
    if len(disks) != TOTAL_DISKS:
        raise InvalidStateError(
            f"expected {TOTAL_DISKS} distinct disks, got {len(disks)}"
        )


def is_valid(state: State) -> bool:
    try:
        validate(state)
    except InvalidStateError:
        return False
    return True


def disks_of(state: State) -> frozenset[Disk]:
    return frozenset(disk for stack in state for disk in stack)


def stack_of(state: State, peg: Peg) -> Stack:
    return state[peg]


def top_of(state: State, peg: Peg) -> Disk | None:
    stack = state[peg]
    return stack[-1] if stack else None
