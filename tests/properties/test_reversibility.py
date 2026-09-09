from __future__ import annotations

from core.domain.state import State
from core.rules.domain.catalog import RULES, inverse_of


def test_inverse_rule_restores_the_original_state(states: tuple[State, ...]) -> None:
    for state in states:
        for rule in RULES:
            if not rule.is_applicable(state):
                continue
            moved = rule.apply(state)
            inverse = inverse_of(rule)
            assert inverse.is_applicable(moved)
            assert inverse.apply(moved) == state


def test_transition_graph_is_undirected(states: tuple[State, ...]) -> None:
    edges = {
        (state, rule.apply(state))
        for state in states
        for rule in RULES
        if rule.is_applicable(state)
    }
    assert all((target, source) in edges for source, target in edges)
