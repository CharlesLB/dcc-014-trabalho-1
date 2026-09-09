from __future__ import annotations

from core.domain.state import CAPACITIES, Peg, State, is_valid
from core.domain.state_space import (
    all_states,
    applicable_rules,
    reachable_from,
    shortest_distance,
    successors,
)
from core.rules.domain.catalog import RULES

EXPECTED_STATE_COUNT = 36


def test_generator_produces_exactly_thirty_six_states(
    states: tuple[State, ...],
) -> None:
    assert len(states) == EXPECTED_STATE_COUNT


def test_generator_produces_no_duplicates(states: tuple[State, ...]) -> None:
    assert len(set(states)) == len(states)


def test_no_state_violates_capacity(states: tuple[State, ...]) -> None:
    for state in states:
        assert all(len(state[peg]) <= CAPACITIES[peg] for peg in Peg)


def test_distribution_shapes_match_the_analysis(states: tuple[State, ...]) -> None:
    shapes = {tuple(len(stack) for stack in state) for state in states}
    assert shapes == {(3, 0, 0), (2, 1, 0), (2, 0, 1), (1, 2, 0), (1, 1, 1), (0, 2, 1)}


def test_all_states_is_deterministic() -> None:
    assert all_states() == all_states()


def test_applicable_rules_agrees_with_brute_force(states: tuple[State, ...]) -> None:
    for state in states:
        expected = tuple(rule for rule in RULES if rule.is_applicable(state))
        assert applicable_rules(state) == expected


def test_successors_are_valid_states(states: tuple[State, ...]) -> None:
    for state in states:
        for rule, successor in successors(state):
            assert is_valid(successor)
            assert successor == rule.apply(state)


def test_graph_is_connected(states: tuple[State, ...]) -> None:
    for state in states:
        assert len(reachable_from(state)) == EXPECTED_STATE_COUNT


def test_shortest_distance_is_zero_to_itself(states: tuple[State, ...]) -> None:
    assert all(shortest_distance(state, state) == 0 for state in states)


def test_shortest_distance_is_symmetric(states: tuple[State, ...]) -> None:
    source = states[0]
    for target in states:
        assert shortest_distance(source, target) == shortest_distance(target, source)


def test_shortest_distance_is_defined_for_every_pair(
    states: tuple[State, ...],
) -> None:
    source = states[0]
    assert all(shortest_distance(source, target) is not None for target in states)
