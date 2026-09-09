from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from core.rules.domain.exceptions import UnknownStrategyError
from core.rules.strategies.ascending import ASCENDING
from core.rules.strategies.custom_order import CUSTOM
from core.rules.strategies.descending import DESCENDING
from core.rules.strategies.domain.base import ControlStrategy

STRATEGIES: Mapping[str, ControlStrategy] = MappingProxyType(
    {
        ASCENDING.name: ASCENDING,
        DESCENDING.name: DESCENDING,
        CUSTOM.name: CUSTOM,
    }
)

STRATEGY_NAMES: tuple[str, ...] = tuple(STRATEGIES)


def get_strategy(name: str) -> ControlStrategy:
    try:
        return STRATEGIES[name]
    except KeyError:
        raise UnknownStrategyError(name) from None
