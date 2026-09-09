from __future__ import annotations

from collections.abc import Mapping, Sequence

from core.search_tree.result import SearchResult
from libs.ranking import criteria
from libs.ranking.criteria import Criterion

MAX_SCORE = 100.0


def score_all(results: Sequence[SearchResult]) -> Mapping[str, float]:
    if not results:
        return {}
    best = {
        criterion.name: min(criterion.measure(result) for result in results)
        for criterion in criteria.CRITERIA
    }
    return {criteria.label(result): _score(result, best) for result in results}


def _score(result: SearchResult, best: Mapping[str, int]) -> float:
    total = sum(
        criterion.weight * _normalise(criterion, result, best[criterion.name])
        for criterion in criteria.CRITERIA
    )
    return round(total * MAX_SCORE, 2)


def _normalise(criterion: Criterion, result: SearchResult, best: int) -> float:
    value = criterion.measure(result)
    if value == best:
        return 1.0
    if value <= 0:
        return 1.0
    return best / value if best > 0 else 1.0 / (1.0 + value)
