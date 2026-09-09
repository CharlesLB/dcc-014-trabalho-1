from __future__ import annotations

import pytest

from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULE_BY_ID, get_rule, inverse_of
from core.rules.domain.exceptions import UnknownRuleError


def test_catalog_is_in_canonical_order(rules: tuple[TransitionRule, ...]) -> None:
    assert [rule.id for rule in rules] == ["R1", "R2", "R3", "R4", "R5", "R6"]


def test_identifiers_are_unique(rules: tuple[TransitionRule, ...]) -> None:
    assert len(RULE_BY_ID) == len(rules)


def test_get_rule_returns_the_catalog_instance(
    rules: tuple[TransitionRule, ...],
) -> None:
    for rule in rules:
        assert get_rule(rule.id) is rule


def test_get_rule_rejects_unknown_identifier() -> None:
    with pytest.raises(UnknownRuleError):
        get_rule("R9")


def test_inverse_pairs_are_symmetric(rules: tuple[TransitionRule, ...]) -> None:
    assert {(rule.id, inverse_of(rule).id) for rule in rules} == {
        ("R1", "R3"),
        ("R3", "R1"),
        ("R2", "R5"),
        ("R5", "R2"),
        ("R4", "R6"),
        ("R6", "R4"),
    }
