from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from statistics import fmean

from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from libs.ranking import criteria
from libs.ranking.comparator import lexicographic_key, sort_results
from libs.ranking.scorer import score_all


@dataclass(frozen=True, slots=True)
class LeaderboardRow:
    position: int
    result: SearchResult
    score: float | None


@dataclass(frozen=True, slots=True)
class Leaderboard:
    problem_id: str
    mode: str
    rows: tuple[LeaderboardRow, ...]

    @property
    def winner(self) -> LeaderboardRow | None:
        return self.rows[0] if self.rows else None


@dataclass(frozen=True, slots=True)
class SummaryRow:
    algorithm: str
    strategy: str
    runs: int
    successes: int
    deadlocks: int
    mean_moves: float | None
    mean_iterations: float


@dataclass(frozen=True, slots=True)
class Summary:
    rows: tuple[SummaryRow, ...]


def build_leaderboard(
    problem_id: str, results: Sequence[SearchResult], mode: str
) -> Leaderboard:
    scores = score_all(results) if mode == "score" else {}
    ordered = (
        _sorted_by_score(results, scores) if mode == "score" else sort_results(results)
    )
    rows = tuple(
        LeaderboardRow(
            position=position,
            result=result,
            score=scores.get(criteria.label(result)),
        )
        for position, result in enumerate(ordered, start=1)
    )
    return Leaderboard(problem_id=problem_id, mode=mode, rows=rows)


def build_summary(results: Sequence[SearchResult]) -> Summary:
    grouped: dict[tuple[str, str], list[SearchResult]] = {}
    for result in results:
        grouped.setdefault((result.algorithm, result.strategy), []).append(result)

    rows = tuple(
        _summarise(algorithm, strategy, group)
        for (algorithm, strategy), group in grouped.items()
    )
    return Summary(rows=tuple(sorted(rows, key=_summary_key)))


def _sorted_by_score(
    results: Sequence[SearchResult], scores: Mapping[str, float]
) -> tuple[SearchResult, ...]:
    return tuple(
        sorted(
            results,
            key=lambda result: (
                -scores[criteria.label(result)],
                lexicographic_key(result),
            ),
        )
    )


def _summarise(
    algorithm: str, strategy: str, group: Sequence[SearchResult]
) -> SummaryRow:
    successes = [result for result in group if result.outcome.is_success]
    moves = [
        result.solution_length
        for result in successes
        if result.solution_length is not None
    ]
    return SummaryRow(
        algorithm=algorithm,
        strategy=strategy,
        runs=len(group),
        successes=len(successes),
        deadlocks=sum(result.outcome is Outcome.DEADLOCK for result in group),
        mean_moves=fmean(moves) if moves else None,
        mean_iterations=fmean(result.metrics.iterations for result in group),
    )


def _summary_key(row: SummaryRow) -> tuple[int, float, float, str, str]:
    return (
        -row.successes,
        row.mean_moves if row.mean_moves is not None else float(criteria.NO_SOLUTION),
        row.mean_iterations,
        row.algorithm,
        row.strategy,
    )
