from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final

from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult

OUTCOME_ORDER: Final[Mapping[Outcome, int]] = {
    Outcome.SUCCESS: 0,
    Outcome.DEADLOCK: 1,
    Outcome.CUTOFF: 2,
    Outcome.FAILURE: 3,
}

NO_SOLUTION: Final = 10**6


def outcome_rank(result: SearchResult) -> int:
    return OUTCOME_ORDER[result.outcome]


def solution_length(result: SearchResult) -> int:
    length = result.solution_length
    return NO_SOLUTION if length is None else length


def iterations(result: SearchResult) -> int:
    return result.metrics.iterations


def nodes_generated(result: SearchResult) -> int:
    return result.metrics.nodes_generated


def label(result: SearchResult) -> str:
    return f"{result.algorithm}:{result.strategy}"


@dataclass(frozen=True, slots=True)
class Criterion:
    name: str
    measure: Callable[[SearchResult], int]
    weight: float


CRITERIA: Final[tuple[Criterion, ...]] = (
    Criterion("outcome", outcome_rank, 0.50),
    Criterion("solution_length", solution_length, 0.25),
    Criterion("iterations", iterations, 0.15),
    Criterion("nodes_generated", nodes_generated, 0.10),
)
