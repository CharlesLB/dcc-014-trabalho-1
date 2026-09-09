from __future__ import annotations

from core.algorithms.breadth_first import BreadthFirstSearch
from core.domain.problem import Problem
from core.domain.state_space import all_states, shortest_distance
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree


def _solve(strategy_name: str, problem: Problem) -> SearchResult:
    return BreadthFirstSearch(SearchTree(), STRATEGIES[strategy_name]).solve(problem)


def test_always_succeeds(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            assert _solve(name, problem).outcome is Outcome.SUCCESS


def test_expansion_order_is_strictly_by_level(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            depths = [
                step.depth
                for step in _solve(name, problem).trace.of_event(TraceEvent.VISIT)
            ]
            assert depths == sorted(depths)


def test_no_state_is_expanded_twice(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            visited = [
                step.state
                for step in _solve(name, problem).trace.of_event(TraceEvent.VISIT)
            ]
            assert len(set(visited)) == len(visited)


def test_no_state_is_generated_twice(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            generated = [
                step.state
                for step in _solve(name, problem).trace.of_event(TraceEvent.GENERATE)
            ]
            assert len(set(generated)) == len(generated)


def test_never_backtracks(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            assert _solve(name, problem).metrics.backtracks == 0


def test_solution_matches_the_independent_shortest_distance(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        optimum = shortest_distance(problem.initial, problem.goal)
        for name in STRATEGIES:
            assert _solve(name, problem).solution_length == optimum


def test_a_goal_equal_to_the_initial_state_needs_no_move() -> None:
    for state in all_states():
        problem = Problem("SYNTHETIC", state, initial=state)
        assert _solve("ascending", problem).solution_length == 0


def test_strategy_changes_the_metrics_not_the_length(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        lengths = {_solve(name, problem).solution_length for name in STRATEGIES}
        assert len(lengths) == 1
