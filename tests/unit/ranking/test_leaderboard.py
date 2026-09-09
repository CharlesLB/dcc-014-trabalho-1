from __future__ import annotations

import pytest

from core.algorithms.domain.registry import ALGORITHMS
from core.domain.problem import Problem
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.tree import SearchTree
from libs.ranking import criteria
from libs.ranking.comparator import lexicographic_key, sort_results
from libs.ranking.leaderboard import build_leaderboard, build_summary
from libs.ranking.scorer import MAX_SCORE, score_all


@pytest.fixture(scope="module")
def executions(problems: tuple[Problem, ...]) -> tuple[SearchResult, ...]:
    return tuple(
        ALGORITHMS[algorithm](SearchTree(), STRATEGIES[strategy]).solve(problem)
        for problem in problems
        for algorithm in ALGORITHMS
        for strategy in STRATEGIES
    )


def test_lexicographic_order_puts_success_first(
    executions: tuple[SearchResult, ...],
) -> None:
    ordered = sort_results(executions)
    ranks = [criteria.outcome_rank(result) for result in ordered]
    assert ranks == sorted(ranks)


def test_shorter_solution_wins_among_successes(
    executions: tuple[SearchResult, ...],
) -> None:
    successes = [r for r in sort_results(executions) if r.outcome.is_success]
    lengths = [criteria.solution_length(result) for result in successes]
    assert lengths == sorted(lengths)


def test_key_is_fully_deterministic(executions: tuple[SearchResult, ...]) -> None:
    keys = [lexicographic_key(result) for result in executions]
    assert len(set(keys)) == len(keys)


def test_leaderboard_positions_are_contiguous(
    problems: tuple[Problem, ...], executions: tuple[SearchResult, ...]
) -> None:
    board = build_leaderboard(problems[0].id, executions, "lexicographic")
    assert [row.position for row in board.rows] == list(range(1, len(executions) + 1))


def test_lexicographic_leaderboard_has_no_scores(
    problems: tuple[Problem, ...], executions: tuple[SearchResult, ...]
) -> None:
    board = build_leaderboard(problems[0].id, executions, "lexicographic")
    assert all(row.score is None for row in board.rows)


def test_winner_is_the_first_row(
    problems: tuple[Problem, ...], executions: tuple[SearchResult, ...]
) -> None:
    board = build_leaderboard(problems[0].id, executions, "lexicographic")
    assert board.winner is not None
    assert board.winner.position == 1
    assert board.winner.result is sort_results(executions)[0]


def test_empty_leaderboard_has_no_winner() -> None:
    assert build_leaderboard("P0", (), "lexicographic").winner is None


def test_score_mode_puts_the_highest_score_first(
    problems: tuple[Problem, ...], executions: tuple[SearchResult, ...]
) -> None:
    board = build_leaderboard(problems[0].id, executions, "score")
    assert board.rows[0].score == max(
        row.score for row in board.rows if row.score is not None
    )


def test_a_lone_execution_scores_the_maximum(
    problems: tuple[Problem, ...], executions: tuple[SearchResult, ...]
) -> None:
    board = build_leaderboard(problems[0].id, executions[:1], "score")
    assert board.rows[0].score == MAX_SCORE


def test_scores_are_monotonically_non_increasing(
    problems: tuple[Problem, ...], executions: tuple[SearchResult, ...]
) -> None:
    board = build_leaderboard(problems[0].id, executions, "score")
    scores = [row.score for row in board.rows]
    assert all(score is not None for score in scores)
    assert scores == sorted(scores, reverse=True)  # type: ignore[type-var]


def test_scores_stay_within_bounds(executions: tuple[SearchResult, ...]) -> None:
    assert all(0.0 <= score <= MAX_SCORE for score in score_all(executions).values())


def test_score_of_an_empty_cohort_is_empty() -> None:
    assert score_all(()) == {}


def test_summary_groups_by_algorithm_and_strategy(
    executions: tuple[SearchResult, ...],
) -> None:
    summary = build_summary(executions)
    labels = {(row.algorithm, row.strategy) for row in summary.rows}
    assert labels == {(r.algorithm, r.strategy) for r in executions}


def test_summary_counts_match_the_executions(
    executions: tuple[SearchResult, ...],
) -> None:
    summary = build_summary(executions)
    assert sum(row.runs for row in summary.rows) == len(executions)
    assert sum(row.successes for row in summary.rows) == sum(
        result.outcome.is_success for result in executions
    )
    assert sum(row.deadlocks for row in summary.rows) == sum(
        result.outcome is Outcome.DEADLOCK for result in executions
    )


def test_summary_orders_the_most_successful_first(
    executions: tuple[SearchResult, ...],
) -> None:
    successes = [row.successes for row in build_summary(executions).rows]
    assert successes == sorted(successes, reverse=True)


def test_summary_of_no_executions_is_empty() -> None:
    assert build_summary(()).rows == ()
