from __future__ import annotations

import pytest

from core.domain.heuristic import misplacement
from core.domain.state import State, build_state
from core.domain.state_space import shortest_distance
from core.rules.domain.base import Disk

GREEN, RED, BLUE = Disk.GREEN, Disk.RED, Disk.BLUE
P1_GOAL = build_state((), (RED, GREEN), (BLUE,))


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (build_state((GREEN, RED), (BLUE,), ()), 3),
        (build_state((GREEN,), (RED,), (BLUE,)), 1),
        (build_state((), (GREEN, RED), (BLUE,)), 4),
        (build_state((), (RED, GREEN), (BLUE,)), 0),
    ],
)
def test_examples_from_the_docstring(state: State, expected: int) -> None:
    assert misplacement(state, P1_GOAL) == expected


def test_right_peg_out_of_place_weighs_two() -> None:
    goal = build_state((RED, GREEN), (BLUE,), ())
    on_top_of_the_wrong_disk = build_state((GREEN, RED), (BLUE,), ())
    assert misplacement(on_top_of_the_wrong_disk, goal) == 2 + 2


def test_a_disk_above_a_misplaced_one_is_misplaced_too() -> None:
    goal = build_state((RED, GREEN, BLUE), (), ())
    state = build_state((GREEN, RED, BLUE), (), ())
    assert misplacement(state, goal) == 2 + 2 + 2


def test_is_zero_only_on_the_goal(states: tuple[State, ...]) -> None:
    for goal in states:
        for state in states:
            assert (misplacement(state, goal) == 0) == (state == goal)


def test_is_admissible(states: tuple[State, ...]) -> None:
    for goal in states:
        for state in states:
            distance = shortest_distance(state, goal)
            assert distance is not None
            assert misplacement(state, goal) <= distance
