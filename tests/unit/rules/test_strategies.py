from __future__ import annotations

import pytest

from core.rules.domain.base import TransitionRule
from core.rules.domain.exceptions import UnknownStrategyError
from core.rules.strategies.ascending import ASCENDING
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


def test_registry_exposes_the_two_strategies() -> None:
    assert set(STRATEGIES) == {"ascending", "descending"}


def test_get_strategy_returns_the_registered_instance() -> None:
    for name, registered in STRATEGIES.items():
        assert get_strategy(name) is registered


def test_get_strategy_rejects_unknown_name() -> None:
    with pytest.raises(UnknownStrategyError):
        get_strategy("random")
