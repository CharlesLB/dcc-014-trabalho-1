from __future__ import annotations

import pytest

from core.domain.state import State
from core.heuristics.color_distance import color_distance
from core.heuristics.domain.registry import (
    DEFAULT_HEURISTIC,
    HEURISTIC_NAMES,
    HEURISTICS,
    UnknownHeuristicError,
    get_heuristic,
)
from core.heuristics.misplacement import misplacement


def test_lists_the_two_heuristics_with_misplacement_as_default() -> None:
    assert HEURISTIC_NAMES == ("misplacement", "color_distance")
    assert DEFAULT_HEURISTIC is HEURISTICS["misplacement"]


def test_each_entry_is_registered_under_its_own_name() -> None:
    for name, heuristic in HEURISTICS.items():
        assert get_heuristic(name) is heuristic
        assert heuristic.name == name


def test_estimate_delegates_to_the_module_function(
    states: tuple[State, ...], initial_state: State
) -> None:
    for goal in states:
        assert get_heuristic("misplacement").estimate(
            initial_state, goal
        ) == misplacement(initial_state, goal)
        assert get_heuristic("color_distance").estimate(
            initial_state, goal
        ) == color_distance(initial_state, goal)


def test_unknown_name_is_an_error() -> None:
    with pytest.raises(UnknownHeuristicError) as raised:
        get_heuristic("manhattan")
    assert raised.value.name == "manhattan"
