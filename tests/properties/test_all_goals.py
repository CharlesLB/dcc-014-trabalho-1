from __future__ import annotations

from statistics import fmean, median

import pytest

from core.algorithms.domain.registry import ALGORITHMS
from core.domain.problem import INITIAL_STATE, all_goal_problems
from core.domain.state_space import all_states, shortest_distance
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.result import SearchResult
from core.search_tree.tree import SearchTree
from libs.ranking.leaderboard import Highlight, Summary, SummaryRow, build_summary

COMPLETE_METHODS = ("backtracking", "breadth_first", "ordered")


@pytest.fixture(scope="module")
def executions() -> tuple[SearchResult, ...]:
    return tuple(
        ALGORITHMS[algorithm](SearchTree(), STRATEGIES[strategy]).solve(problem)
        for problem in all_goal_problems()
        for algorithm in ALGORITHMS
        for strategy in STRATEGIES
    )


@pytest.fixture(scope="module")
def summary(executions: tuple[SearchResult, ...]) -> Summary:
    return build_summary(executions)


def _row(summary: Summary, algorithm: str, strategy: str) -> SummaryRow:
    return next(
        row
        for row in summary.rows
        if row.algorithm == algorithm and row.strategy == strategy
    )


def _highlight(summary: Summary, criterion: str) -> Highlight:
    return next(h for h in summary.highlights if h.criterion == criterion)


def _algorithms(winners: tuple[SummaryRow, ...]) -> set[str]:
    return {row.algorithm for row in winners}


def test_the_battery_covers_every_goal_once() -> None:
    goals = [problem.goal for problem in all_goal_problems()]
    assert sorted(goals) == sorted(all_states())
    assert len(set(goals)) == len(goals)


def test_every_combination_runs_against_every_goal(summary: Summary) -> None:
    assert len(summary.rows) == len(ALGORITHMS) * len(STRATEGIES)
    assert all(row.runs == len(all_states()) for row in summary.rows)


@pytest.mark.parametrize("algorithm", COMPLETE_METHODS)
def test_complete_methods_solve_every_goal(summary: Summary, algorithm: str) -> None:
    for strategy in STRATEGIES:
        row = _row(summary, algorithm, strategy)
        assert row.successes == row.runs


def test_stats_match_the_raw_executions(
    executions: tuple[SearchResult, ...], summary: Summary
) -> None:
    for row in summary.rows:
        group = [
            r
            for r in executions
            if r.algorithm == row.algorithm and r.strategy == row.strategy
        ]
        iterations = [r.metrics.iterations for r in group]
        assert row.iterations.mean == pytest.approx(fmean(iterations))
        assert row.iterations.median == median(iterations)
        moves = [r.solution_length for r in group if r.solution_length is not None]
        if row.moves is not None:
            assert row.moves.mean == pytest.approx(fmean(moves))
            assert row.moves.median == median(moves)


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_breadth_first_averages_the_optimal_number_of_moves(
    summary: Summary, strategy: str
) -> None:
    optimum = [shortest_distance(INITIAL_STATE, goal) or 0 for goal in all_states()]
    moves = _row(summary, "breadth_first", strategy).moves
    assert moves is not None
    assert moves.mean == pytest.approx(fmean(optimum))
    assert moves.median == median(optimum)


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_cost_is_the_number_of_moves(summary: Summary, strategy: str) -> None:
    for row in summary.rows:
        assert row.cost == row.moves


def test_only_breadth_first_wins_on_moves(summary: Summary) -> None:
    highlight = _highlight(summary, "moves")
    assert _algorithms(highlight.by_mean) == {"breadth_first"}


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_ordered_stays_close_to_the_optimum(summary: Summary, strategy: str) -> None:
    optimum = fmean(
        shortest_distance(INITIAL_STATE, goal) or 0 for goal in all_states()
    )
    moves = _row(summary, "ordered", strategy).moves
    assert moves is not None
    assert optimum < moves.mean < optimum + 0.2


def test_ordered_wins_on_iterations(summary: Summary) -> None:
    highlight = _highlight(summary, "iterations")
    assert _algorithms(highlight.by_mean) == {"ordered"}


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_greedy_deadlocks_on_some_goals(summary: Summary, strategy: str) -> None:
    row = _row(summary, "greedy", strategy)
    assert row.deadlocks > 0
    assert row.successes + row.deadlocks == row.runs


def test_backtracking_and_irrevocable_never_beat_the_optimal_methods(
    summary: Summary,
) -> None:
    best_moves = _highlight(summary, "moves").by_mean[0].moves
    best_cost = _highlight(summary, "cost").by_mean[0].cost
    assert best_moves is not None and best_cost is not None
    for strategy in STRATEGIES:
        row = _row(summary, "backtracking", strategy)
        assert row.moves is not None and row.cost is not None
        assert row.moves.mean > best_moves.mean
        assert row.cost.mean > best_cost.mean


@pytest.mark.parametrize("algorithm", ["irrevocable", "greedy"])
def test_incomplete_methods_are_excluded_from_the_winners(
    summary: Summary, algorithm: str
) -> None:
    for highlight in summary.highlights:
        assert algorithm not in _algorithms(highlight.by_mean)
        assert algorithm not in _algorithms(highlight.by_median)


@pytest.mark.parametrize("algorithm", ["breadth_first"])
def test_mean_iterations_is_the_same_for_methods_that_visit_each_state_once(
    summary: Summary, algorithm: str
) -> None:
    states = len(all_states())
    for strategy in STRATEGIES:
        iterations = _row(summary, algorithm, strategy).iterations
        assert iterations.mean == pytest.approx((states + 1) / 2)
