from __future__ import annotations

import pytest

from core.domain.state import State, build_state
from core.heuristics.color_distance import color_distance, contributions
from core.rules.domain.base import Disk

GREEN, RED, BLUE = Disk.GREEN, Disk.RED, Disk.BLUE
P1_GOAL = build_state((), (RED, GREEN), (BLUE,))


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (build_state((GREEN, RED), (BLUE,), ()), 6),
        (build_state((GREEN, RED), (), (BLUE,)), 3),
        (build_state((), (GREEN, RED), (BLUE,)), 0),
        (build_state((), (RED, GREEN), (BLUE,)), 0),
    ],
)
def test_examples_from_the_docstring(state: State, expected: int) -> None:
    assert color_distance(state, P1_GOAL) == expected


def test_each_disk_adds_its_weight_times_the_distance() -> None:
    goal = build_state((BLUE,), (RED,), (GREEN,))
    state = build_state((GREEN,), (RED,), (BLUE,))
    assert contributions(state, goal) == {GREEN: 1 * 2, RED: 0, BLUE: 3 * 2}


def test_is_zero_on_the_goal(states: tuple[State, ...]) -> None:
    for goal in states:
        assert color_distance(goal, goal) == 0


def test_is_zero_whenever_every_disk_is_on_its_goal_peg(
    states: tuple[State, ...],
) -> None:
    for goal in states:
        for state in states:
            same_pegs = all(set(state[peg]) == set(goal[peg]) for peg in range(3))
            assert (color_distance(state, goal) == 0) == same_pegs
