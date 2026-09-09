from __future__ import annotations

import pytest

from core.rules.domain.base import TransitionRule
from core.rules.domain.exceptions import InvalidRuleOrderError, UnknownStrategyError
from core.rules.strategies.ascending import ASCENDING
from core.rules.strategies.custom_order import (
    DEFAULT_CUSTOM_ORDER,
    CustomOrderStrategy,
    parse_order,
)
from core.rules.strategies.descending import DESCENDING
from core.rules.strategies.domain.base import ControlStrategy
from core.rules.strategies.domain.registry import STRATEGIES, get_strategy


def test_ascending_follows_the_catalog(rules: tuple[TransitionRule, ...]) -> None:
    assert ASCENDING.order(rules) == rules


def test_descending_is_the_exact_reverse(rules: tuple[TransitionRule, ...]) -> None:
    assert DESCENDING.order(rules) == tuple(reversed(rules))
    assert ASCENDING.order(rules) == tuple(reversed(DESCENDING.order(rules)))


def test_ordering_preserves_the_input_set(
    strategy: ControlStrategy, rules: tuple[TransitionRule, ...]
) -> None:
    subset = (rules[4], rules[1], rules[0])
    ordered = strategy.order(subset)
    assert set(ordered) == set(subset)
    assert len(ordered) == len(subset)


def test_ordering_is_independent_of_input_order(
    strategy: ControlStrategy, rules: tuple[TransitionRule, ...]
) -> None:
    assert strategy.order(rules) == strategy.order(tuple(reversed(rules)))


def test_custom_order_uses_its_sequence(rules: tuple[TransitionRule, ...]) -> None:
    strategy = CustomOrderStrategy(sequence=("R6", "R5", "R4", "R3", "R2", "R1"))
    assert [rule.id for rule in strategy.order(rules)] == list(strategy.sequence)


def test_custom_order_default_matches_the_documented_sequence() -> None:
    assert CustomOrderStrategy().sequence == DEFAULT_CUSTOM_ORDER


def test_custom_order_rejects_incomplete_sequence() -> None:
    with pytest.raises(InvalidRuleOrderError):
        CustomOrderStrategy(sequence=("R1", "R2", "R3"))


def test_custom_order_rejects_unknown_rule() -> None:
    with pytest.raises(InvalidRuleOrderError):
        CustomOrderStrategy(sequence=("R1", "R2", "R3", "R4", "R5", "R9"))


def test_custom_order_rejects_duplicates() -> None:
    with pytest.raises(InvalidRuleOrderError):
        CustomOrderStrategy(sequence=("R1", "R1", "R2", "R3", "R4", "R5"))


def test_parse_order_accepts_a_full_permutation() -> None:
    assert parse_order(" r2, r4 ,r6,r1,r3,r5 ") == ("R2", "R4", "R6", "R1", "R3", "R5")


@pytest.mark.parametrize("raw", ["R1,R2,R3", "", "R1,R2,R3,R4,R5,R6,R1"])
def test_parse_order_rejects_wrong_cardinality(raw: str) -> None:
    with pytest.raises(InvalidRuleOrderError):
        parse_order(raw)


def test_parse_order_rejects_unknown_identifier() -> None:
    with pytest.raises(InvalidRuleOrderError):
        parse_order("R1,R2,R3,R4,R5,RX")


def test_registry_exposes_the_three_strategies() -> None:
    assert set(STRATEGIES) == {"ascending", "descending", "custom"}


def test_get_strategy_returns_the_registered_instance() -> None:
    for name, registered in STRATEGIES.items():
        assert get_strategy(name) is registered


def test_get_strategy_rejects_unknown_name() -> None:
    with pytest.raises(UnknownStrategyError):
        get_strategy("random")
