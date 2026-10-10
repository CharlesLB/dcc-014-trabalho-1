from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from core.heuristics.color_distance import COLOR_DISTANCE
from core.heuristics.domain.base import Heuristic
from core.heuristics.misplacement import MISPLACEMENT


class UnknownHeuristicError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"unknown heuristic: {name!r}")
        self.name = name


HEURISTICS: Mapping[str, Heuristic] = MappingProxyType(
    {
        MISPLACEMENT.name: MISPLACEMENT,
        COLOR_DISTANCE.name: COLOR_DISTANCE,
    }
)

HEURISTIC_NAMES: tuple[str, ...] = tuple(HEURISTICS)

DEFAULT_HEURISTIC: Heuristic = MISPLACEMENT


def get_heuristic(name: str) -> Heuristic:
    try:
        return HEURISTICS[name]
    except KeyError:
        raise UnknownHeuristicError(name) from None
