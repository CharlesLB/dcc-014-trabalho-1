from __future__ import annotations

import pytest

from core.costs.domain.registry import (
    COST_NAMES,
    COSTS,
    DEFAULT_COST,
    UnknownCostError,
    get_cost,
)
from core.costs.unit import UNIT
from core.costs.weight_distance import WEIGHT_DISTANCE
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.rules.moves import R1, R2, R4
from core.search_tree.tree import SearchTree


def test_lists_the_two_costs_with_weight_distance_as_default() -> None:
    assert COST_NAMES == ("weight_distance", "unit")
    assert DEFAULT_COST is COSTS["weight_distance"]


def test_each_entry_is_registered_under_its_own_name() -> None:
    for name, cost in COSTS.items():
        assert get_cost(name) is cost
        assert cost.name == name


def test_unknown_name_is_an_error() -> None:
    with pytest.raises(UnknownCostError) as raised:
        get_cost("free")
    assert raised.value.name == "free"


def test_unit_charges_one_for_every_move(
    states: tuple[State, ...], rules: tuple[TransitionRule, ...]
) -> None:
    for state in states:
        for rule in rules:
            if rule.is_applicable(state):
                assert UNIT.cost(rule, state) == 1


def test_weight_distance_examples_from_the_docstring(initial_state: State) -> None:
    assert WEIGHT_DISTANCE.cost(R1, initial_state) == 2 * 1
    assert WEIGHT_DISTANCE.cost(R2, initial_state) == 2 * 2
    assert WEIGHT_DISTANCE.cost(R4, initial_state) == 3 * 1


def test_weight_distance_is_the_same_both_ways(
    states: tuple[State, ...], rules: tuple[TransitionRule, ...]
) -> None:
    for state in states:
        for rule in rules:
            if not rule.is_applicable(state):
                continue
            cost = WEIGHT_DISTANCE.cost(rule, state)
            assert 1 <= cost <= 6
            back = next(
                other
                for other in rules
                if (other.origin, other.destination) == (rule.destination, rule.origin)
            )
            assert WEIGHT_DISTANCE.cost(back, rule.apply(state)) == cost


def test_the_tree_charges_the_cost_function_it_was_given(initial_state: State) -> None:
    for cost in COSTS.values():
        tree = SearchTree(cost=cost)
        child = tree.expand(tree.root(initial_state), R4)
        assert child.cost == cost.cost(R4, initial_state)
        assert tree.step_cost(R4, initial_state) == child.cost
