from __future__ import annotations

import pytest

from core.algorithms.breadth_first import BreadthFirstSearch
from core.algorithms.domain.registry import ALGORITHMS
from core.algorithms.ordered import OrderedSearch
from core.domain.problem import Problem
from core.domain.state_space import all_states, cheapest_cost
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree


def _breadth_first(problem: Problem, strategy: str, *, prune: bool) -> SearchResult:
    return BreadthFirstSearch(SearchTree(), STRATEGIES[strategy], prune=prune).solve(
        problem
    )


@pytest.mark.parametrize(
    ("strategy", "prune", "iterations", "generated", "visited", "peak"),
    [
        ("ascending", False, 47, 148, 46, 102),
        ("descending", False, 27, 85, 26, 59),
        ("ascending", True, 14, 17, 13, 7),
        ("descending", True, 12, 16, 11, 6),
    ],
)
def test_breadth_first_on_p1_matches_the_presentation(
    problems: tuple[Problem, ...],
    strategy: str,
    prune: bool,
    iterations: int,
    generated: int,
    visited: int,
    peak: int,
) -> None:
    result = _breadth_first(problems[0], strategy, prune=prune)
    assert result.applied_rules == ("R4", "R1", "R1")
    assert result.metrics.iterations == iterations
    assert result.metrics.nodes_generated == generated
    assert result.metrics.nodes_visited == visited
    assert result.metrics.max_frontier == peak


@pytest.mark.parametrize("algorithm", sorted(ALGORITHMS))
def test_without_pruning_nothing_is_pruned(
    problems: tuple[Problem, ...], algorithm: str
) -> None:
    search = ALGORITHMS[algorithm](
        SearchTree(), STRATEGIES["ascending"], max_iterations=50, prune=False
    )
    result = search.solve(problems[0])
    assert not result.pruned
    assert not result.trace.of_event(TraceEvent.PRUNE)


@pytest.mark.parametrize("algorithm", ["irrevocable", "backtracking"])
def test_path_methods_cycle_until_the_limit_without_pruning(
    problems: tuple[Problem, ...], algorithm: str
) -> None:
    search = ALGORITHMS[algorithm](
        SearchTree(), STRATEGIES["ascending"], max_iterations=40, prune=False
    )
    result = search.solve(problems[0])
    assert result.outcome is Outcome.CUTOFF
    assert result.metrics.max_depth == 40


def test_pruning_is_on_by_default(problems: tuple[Problem, ...]) -> None:
    for algorithm in ALGORITHMS.values():
        search = algorithm(SearchTree(), STRATEGIES["ascending"])
        assert search.prune
        assert search.solve(problems[0]).pruned


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_ordered_stays_optimal_without_pruning(strategy: str) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal)
        result = OrderedSearch(SearchTree(), STRATEGIES[strategy], prune=False).solve(
            problem
        )
        assert result.solution_cost == cheapest_cost(problem.initial, goal)


@pytest.mark.parametrize("algorithm", sorted(ALGORITHMS))
def test_peak_frontier_is_at_least_one(
    problems: tuple[Problem, ...], algorithm: str
) -> None:
    result = ALGORITHMS[algorithm](SearchTree(), STRATEGIES["ascending"]).solve(
        problems[0]
    )
    assert result.metrics.max_frontier >= 1
