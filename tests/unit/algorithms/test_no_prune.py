from __future__ import annotations

import pytest

from core.algorithms.breadth_first.algorithm import BreadthFirstSearch
from core.algorithms.domain.registry import ALGORITHMS
from core.domain.problem import Problem, all_goal_problems
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.path import contains_state
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


@pytest.mark.parametrize("algorithm", sorted(ALGORITHMS))
def test_peak_frontier_is_at_least_one(
    problems: tuple[Problem, ...], algorithm: str
) -> None:
    result = ALGORITHMS[algorithm](SearchTree(), STRATEGIES["ascending"]).solve(
        problems[0]
    )
    assert result.metrics.max_frontier >= 1


@pytest.mark.parametrize(
    ("algorithm", "iterations", "generated"),
    [("ordered", 16, 28), ("greedy", 4, 10), ("astar", 4, 10)],
)
def test_queue_methods_on_p1_without_pruning_match_the_presentation(
    problems: tuple[Problem, ...], algorithm: str, iterations: int, generated: int
) -> None:
    for strategy in STRATEGIES.values():
        search = ALGORITHMS[algorithm](SearchTree(), strategy, prune=False)
        result = search.solve(problems[0])
        assert result.applied_rules == ("R4", "R1", "R1")
        assert result.metrics.iterations == iterations
        assert result.metrics.nodes_generated == generated


@pytest.mark.parametrize("algorithm", ["ordered", "greedy", "astar"])
def test_queue_methods_never_return_to_a_state_of_their_own_path(
    algorithm: str,
) -> None:
    for problem in all_goal_problems():
        for strategy in STRATEGIES.values():
            tree = SearchTree()
            result = ALGORITHMS[algorithm](tree, strategy, prune=False).solve(problem)
            assert result.outcome is Outcome.SUCCESS
            for node in tree.nodes:
                assert node.parent is None or not contains_state(
                    node.parent, node.state
                )


def test_ordered_without_pruning_repeats_states_but_keeps_the_lowest_cost() -> None:
    repeated = 0
    for problem in all_goal_problems():
        pruned_tree, free_tree = SearchTree(), SearchTree()
        strategy = STRATEGIES["ascending"]
        pruned = ALGORITHMS["ordered"](pruned_tree, strategy).solve(problem)
        free = ALGORITHMS["ordered"](free_tree, strategy, prune=False).solve(problem)
        assert free.solution_cost == pruned.solution_cost
        states = [node.state for node in free_tree.nodes]
        repeated += len(states) - len(set(states))
    assert repeated
