from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from core.algorithms.backtracking import BacktrackingSearch
from core.algorithms.breadth_first import BreadthFirstSearch
from core.algorithms.domain.base import SearchAlgorithm
from core.algorithms.irrevocable import IrrevocableSearch


class UnknownAlgorithmError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"unknown search algorithm: {name!r}")
        self.name = name


ALGORITHMS: Mapping[str, type[SearchAlgorithm]] = MappingProxyType(
    {
        IrrevocableSearch.name: IrrevocableSearch,
        BacktrackingSearch.name: BacktrackingSearch,
        BreadthFirstSearch.name: BreadthFirstSearch,
    }
)

ALGORITHM_NAMES: tuple[str, ...] = tuple(ALGORITHMS)


def get_algorithm(name: str) -> type[SearchAlgorithm]:
    try:
        return ALGORITHMS[name]
    except KeyError:
        raise UnknownAlgorithmError(name) from None
