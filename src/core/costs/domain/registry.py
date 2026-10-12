from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from core.costs.domain.base import CostFunction
from core.costs.step_weight_distance import STEP_WEIGHT_DISTANCE
from core.costs.unit import UNIT
from core.costs.weight_distance import WEIGHT_DISTANCE


class UnknownCostError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"unknown cost function: {name!r}")
        self.name = name


COSTS: Mapping[str, CostFunction] = MappingProxyType(
    {
        STEP_WEIGHT_DISTANCE.name: STEP_WEIGHT_DISTANCE,
        WEIGHT_DISTANCE.name: WEIGHT_DISTANCE,
        UNIT.name: UNIT,
    }
)

COST_NAMES: tuple[str, ...] = tuple(COSTS)

DEFAULT_COST: CostFunction = STEP_WEIGHT_DISTANCE


def get_cost(name: str) -> CostFunction:
    try:
        return COSTS[name]
    except KeyError:
        raise UnknownCostError(name) from None
