from __future__ import annotations

import pytest

from core.domain.state import (
    EMPTY_STATE,
    Disk,
    InvalidStateError,
    Peg,
    State,
    build_state,
    disks_of,
    is_valid,
    stack_of,
    top_of,
    validate,
)


def test_state_is_hashable_and_compares_structurally() -> None:
    first = build_state((Disk.GREEN, Disk.RED), (Disk.BLUE,), ())
    second = build_state((Disk.GREEN, Disk.RED), (Disk.BLUE,), ())
    assert first == second
    assert first is not second
    assert len({first, second}) == 1


def test_state_is_immutable(initial_state: State) -> None:
    with pytest.raises(TypeError):
        initial_state[Peg.H1] = ()  # type: ignore[index]


def test_build_state_rejects_capacity_violation() -> None:
    with pytest.raises(InvalidStateError):
        build_state((), (), (Disk.GREEN, Disk.RED, Disk.BLUE))


def test_build_state_rejects_missing_disk() -> None:
    with pytest.raises(InvalidStateError):
        build_state((Disk.GREEN, Disk.RED), (), ())


def test_build_state_rejects_duplicated_disk() -> None:
    with pytest.raises(InvalidStateError):
        build_state((Disk.GREEN, Disk.GREEN), (Disk.RED,), ())


def test_validate_rejects_wrong_arity() -> None:
    with pytest.raises(InvalidStateError):
        validate(((Disk.GREEN,), (Disk.RED,)))  # type: ignore[arg-type]


def test_empty_state_is_not_valid() -> None:
    assert not is_valid(EMPTY_STATE)


def test_every_enumerated_state_is_valid(states: tuple[State, ...]) -> None:
    assert all(is_valid(state) for state in states)


def test_stack_and_top_accessors(initial_state: State) -> None:
    for peg in Peg:
        stack = stack_of(initial_state, peg)
        assert top_of(initial_state, peg) == (stack[-1] if stack else None)


def test_disks_of_returns_the_three_disks(states: tuple[State, ...]) -> None:
    assert all(disks_of(state) == frozenset(Disk) for state in states)
