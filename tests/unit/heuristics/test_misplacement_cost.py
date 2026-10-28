from __future__ import annotations

import heapq

import pytest

from core.costs.step_weight_distance import STEP_WEIGHT_DISTANCE
from core.domain.state import State, build_state
from core.heuristics.misplacement import contributions as moves_left
from core.heuristics.misplacement import misplacement
from core.heuristics.misplacement_cost import (
    cheapest_move,
    contributions,
    misplacement_cost,
)
from core.rules.domain.base import Disk
from core.rules.domain.catalog import RULES, inverse_of

GREEN, RED, BLUE = Disk.GREEN, Disk.RED, Disk.BLUE
P1_GOAL = build_state((), (RED, GREEN), (BLUE,))


def _cheapest_costs_to(goal: State) -> dict[State, int]:
    best: dict[State, int] = {goal: 0}
    queue = [(0, goal)]
    while queue:
        cost, state = heapq.heappop(queue)
        if cost > best[state]:
            continue
        for rule in RULES:
            if not rule.is_applicable(state):
                continue
            previous = rule.apply(state)
            inverse = inverse_of(rule)
            reached = cost + STEP_WEIGHT_DISTANCE.cost(inverse, previous)
            if reached < best.get(previous, reached + 1):
                best[previous] = reached
                heapq.heappush(queue, (reached, previous))
    return best


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (build_state((GREEN, RED), (BLUE,), ()), 36),
        (build_state((GREEN, RED), (), (BLUE,)), 23),
        (build_state((GREEN,), (RED,), (BLUE,)), 11),
        (build_state((), (GREEN, RED), (BLUE,)), 46),
        (build_state((), (RED, GREEN), (BLUE,)), 0),
    ],
)
def test_examples_from_the_docstring(state: State, expected: int) -> None:
    assert misplacement_cost(state, P1_GOAL) == expected


def test_the_cheapest_move_of_each_disk_is_ten_plus_its_weight() -> None:
    assert {disk: cheapest_move(disk) for disk in Disk} == {
        GREEN: 11,
        RED: 12,
        BLUE: 13,
    }


def test_each_disk_weighs_its_missing_moves_times_its_cheapest_move(
    states: tuple[State, ...],
) -> None:
    for goal in states:
        for state in states:
            expected = {
                disk: moves * cheapest_move(disk)
                for disk, moves in moves_left(state, goal).items()
            }
            assert contributions(state, goal) == expected


def test_is_zero_only_on_the_goal(states: tuple[State, ...]) -> None:
    for goal in states:
        for state in states:
            assert (misplacement_cost(state, goal) == 0) == (state == goal)


def test_never_falls_below_eleven_per_missing_move(states: tuple[State, ...]) -> None:
    for goal in states:
        for state in states:
            assert misplacement_cost(state, goal) >= 11 * misplacement(state, goal)


def test_is_admissible_with_the_default_cost(states: tuple[State, ...]) -> None:
    for goal in states:
        cheapest = _cheapest_costs_to(goal)
        for state in states:
            assert misplacement_cost(state, goal) <= cheapest[state]


def test_hits_the_optimal_cost_of_p1_from_the_initial_state(
    initial_state: State,
) -> None:
    cheapest = _cheapest_costs_to(P1_GOAL)
    assert misplacement_cost(initial_state, P1_GOAL) == cheapest[initial_state] == 36


def test_is_consistent_with_the_default_cost(states: tuple[State, ...]) -> None:
    for goal in states:
        for state in states:
            for rule in RULES:
                if not rule.is_applicable(state):
                    continue
                step = STEP_WEIGHT_DISTANCE.cost(rule, state)
                after = misplacement_cost(rule.apply(state), goal)
                assert misplacement_cost(state, goal) <= step + after
