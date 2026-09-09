from __future__ import annotations

from core.domain.state import CAPACITIES, Peg, State, build_state
from core.rules.domain.base import Disk
from core.rules.domain.catalog import RULES
from core.rules.domain.constraints import (
    has_disk_to_move,
    has_room_for_disk,
    is_move_allowed,
)


def test_empty_origin_blocks_the_move() -> None:
    state = build_state((Disk.GREEN, Disk.RED, Disk.BLUE), (), ())
    assert not has_disk_to_move(state, Peg.H2)
    assert not is_move_allowed(state, Peg.H2, Peg.H1)


def test_full_destination_blocks_the_move() -> None:
    state = build_state((Disk.GREEN,), (Disk.RED,), (Disk.BLUE,))
    assert not has_room_for_disk(state, Peg.H3)
    assert not is_move_allowed(state, Peg.H1, Peg.H3)


def test_applicability_matches_brute_force(states: tuple[State, ...]) -> None:
    for state in states:
        for rule in RULES:
            expected = (
                len(state[rule.origin]) >= 1
                and len(state[rule.destination]) + 1 <= CAPACITIES[rule.destination]
            )
            assert rule.is_applicable(state) is expected


def test_branching_factor_stays_between_two_and_four(
    states: tuple[State, ...],
) -> None:
    for state in states:
        applicable = sum(rule.is_applicable(state) for rule in RULES)
        assert 2 <= applicable <= 4
