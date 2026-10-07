from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from statistics import fmean, median

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
class Stat:
    mean: float
    median: float


@dataclass(frozen=True, slots=True)
class SummaryRow:
    algorithm: str
    strategy: str
    runs: int
    successes: int
    deadlocks: int
    moves: Stat | None
    cost: Stat | None
    iterations: Stat
    nodes_generated: Stat


@dataclass(frozen=True, slots=True)
class Highlight:
    criterion: str
    by_mean: tuple[SummaryRow, ...]
    by_median: tuple[SummaryRow, ...]


@dataclass(frozen=True, slots=True)
class Summary:
    rows: tuple[SummaryRow, ...]
    highlights: tuple[Highlight, ...] = ()


SUMMARY_CRITERIA: tuple[tuple[str, Callable[[SummaryRow], Stat | None]], ...] = (
    ("moves", lambda row: row.moves),
    ("cost", lambda row: row.cost),
    ("iterations", lambda row: row.iterations),
    ("nodes_generated", lambda row: row.nodes_generated),
)


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
    return Summary(
        rows=tuple(sorted(rows, key=_summary_key)), highlights=_highlights(rows)
    )


def _highlights(rows: Sequence[SummaryRow]) -> tuple[Highlight, ...]:
    if not rows:
        return ()
    most = max(row.successes for row in rows)
    contenders = [row for row in rows if row.successes == most]
    highlights: list[Highlight] = []
    for name, measure in SUMMARY_CRITERIA:
        measured: list[tuple[SummaryRow, Stat]] = []
        for row in contenders:
            stat = measure(row)
            if stat is not None:
                measured.append((row, stat))
        if not measured:
            continue
        best_mean = min(stat.mean for _, stat in measured)
        best_median = min(stat.median for _, stat in measured)
        highlights.append(
            Highlight(
                criterion=name,
                by_mean=tuple(r for r, s in measured if s.mean == best_mean),
                by_median=tuple(r for r, s in measured if s.median == best_median),
            )
        )
    return tuple(highlights)


def _stat(values: Sequence[int]) -> Stat | None:
    if not values:
        return None
    return Stat(mean=fmean(values), median=float(median(values)))


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
    moves = [r.solution_length for r in group if r.solution_length is not None]
    costs = [r.solution_cost for r in group if r.solution_cost is not None]
    iterations = _stat([result.metrics.iterations for result in group])
    generated = _stat([result.metrics.nodes_generated for result in group])
    assert iterations is not None and generated is not None
    return SummaryRow(
        algorithm=algorithm,
        strategy=strategy,
        runs=len(group),
        successes=sum(result.outcome.is_success for result in group),
        deadlocks=sum(result.outcome is Outcome.DEADLOCK for result in group),
        moves=_stat(moves),
        cost=_stat(costs),
        iterations=iterations,
        nodes_generated=generated,
    )


def _summary_key(row: SummaryRow) -> tuple[int, float, float, float, str, str]:
    no_solution = float(criteria.NO_SOLUTION)
    return (
        -row.successes,
        row.moves.mean if row.moves is not None else no_solution,
        row.moves.median if row.moves is not None else no_solution,
        row.iterations.mean,
        row.algorithm,
        row.strategy,
    )
