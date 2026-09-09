from __future__ import annotations

from collections.abc import Iterable

from core.search_tree.result import SearchResult
from libs.ranking import criteria


def lexicographic_key(result: SearchResult) -> tuple[int, int, int, int, str]:
    return (
        criteria.outcome_rank(result),
        criteria.solution_length(result),
        criteria.iterations(result),
        criteria.nodes_generated(result),
        criteria.label(result),
    )


def sort_results(results: Iterable[SearchResult]) -> tuple[SearchResult, ...]:
    return tuple(sorted(results, key=lexicographic_key))
