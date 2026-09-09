from __future__ import annotations

import pytest

from core.domain.state import CAPACITIES, Peg, State, disks_of, is_valid
from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULES, inverse_of
from core.rules.domain.exceptions import RuleNotApplicableError
from core.rules.moves import R1, R2, R3, R4, R5, R6, Move


def test_catalog_covers_every_ordered_pair_of_pegs() -> None:
    pairs = {(rule.origin, rule.destination) for rule in RULES}
    expected = {
        (origin, destination)
        for origin in Peg
        for destination in Peg
        if origin != destination
    }
    assert pairs == expected


@pytest.mark.parametrize(
    ("rule", "origin", "destination"),
    [
        (R1, Peg.H1, Peg.H2),
        (R2, Peg.H1, Peg.H3),
        (R3, Peg.H2, Peg.H1),
        (R4, Peg.H2, Peg.H3),
        (R5, Peg.H3, Peg.H1),
        (R6, Peg.H3, Peg.H2),
    ],
)
def test_each_rule_declares_its_pegs(rule: Move, origin: Peg, destination: Peg) -> None:
    assert rule.origin is origin
    assert rule.destination is destination


def test_rules_are_immutable() -> None:
    with pytest.raises(AttributeError):
        R1.id = "RX"  # type: ignore[misc]


def test_apply_moves_the_top_disk_only(states: tuple[State, ...]) -> None:
    for state in states:
        for rule in RULES:
            if not rule.is_applicable(state):
                continue
            moved = state[rule.origin][-1]
            result = rule.apply(state)
            assert result[rule.origin] == state[rule.origin][:-1]
            assert result[rule.destination] == (*state[rule.destination], moved)


def test_apply_preserves_validity_and_disks(states: tuple[State, ...]) -> None:
    for state in states:
        for rule in RULES:
            if not rule.is_applicable(state):
                continue
            result = rule.apply(state)
            assert is_valid(result)
            assert disks_of(result) == disks_of(state)


def test_apply_changes_exactly_two_pegs(states: tuple[State, ...]) -> None:
    for state in states:
        for rule in RULES:
            if not rule.is_applicable(state):
                continue
            result = rule.apply(state)
            changed = {peg for peg in Peg if result[peg] != state[peg]}
            assert changed == {rule.origin, rule.destination}


def test_apply_never_exceeds_capacity(states: tuple[State, ...]) -> None:
    for state in states:
        for rule in RULES:
            if not rule.is_applicable(state):
                continue
            result = rule.apply(state)
            assert all(len(result[peg]) <= CAPACITIES[peg] for peg in Peg)


def test_apply_does_not_mutate_the_source_state(states: tuple[State, ...]) -> None:
    for state in states:
        snapshot = tuple(tuple(stack) for stack in state)
        for rule in RULES:
            if rule.is_applicable(state):
                rule.apply(state)
        assert tuple(tuple(stack) for stack in state) == snapshot


def test_apply_rejects_non_applicable_rule(states: tuple[State, ...]) -> None:
    for state in states:
        for rule in RULES:
            if rule.is_applicable(state):
                continue
            with pytest.raises(RuleNotApplicableError) as raised:
                rule.apply(state)
            assert raised.value.rule_id == rule.id


def test_every_rule_has_an_exact_inverse(rules: tuple[TransitionRule, ...]) -> None:
    for rule in rules:
        inverse = inverse_of(rule)
        assert inverse.origin is rule.destination
        assert inverse.destination is rule.origin
        assert inverse_of(inverse) is rule
