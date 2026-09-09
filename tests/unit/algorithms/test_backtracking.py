from __future__ import annotations

from core.algorithms.backtracking import BacktrackingSearch
from core.domain.problem import Problem
from core.domain.state_space import all_states
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree


def _solve(strategy_name: str, problem: Problem) -> SearchResult:
    return BacktrackingSearch(SearchTree(), STRATEGIES[strategy_name]).solve(problem)


def _backtracking_case() -> tuple[Problem, str]:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal)
        for name in STRATEGIES:
            if _solve(name, problem).metrics.backtracks > 0:
                return problem, name
    raise AssertionError("no backtracking configuration found")


def test_always_succeeds_because_the_graph_is_connected(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        for name in STRATEGIES:
            assert _solve(name, problem).outcome is Outcome.SUCCESS


def test_forced_scenario_backtracks() -> None:
    problem, strategy_name = _backtracking_case()
    result = _solve(strategy_name, problem)
    assert result.metrics.backtracks > 0
    assert result.trace.of_event(TraceEvent.BACKTRACK)


def test_abandoned_branches_are_absent_from_the_solution() -> None:
    problem, strategy_name = _backtracking_case()
    result = _solve(strategy_name, problem)

    abandoned = {
        step.node_order for step in result.trace.of_event(TraceEvent.BACKTRACK)
    }
    solution_orders = {node.order for node in result.solution_path}
    assert abandoned.isdisjoint(solution_orders)


def test_solution_remains_a_contiguous_chain() -> None:
    problem, strategy_name = _backtracking_case()
    result = _solve(strategy_name, problem)
    for parent, child in zip(
        result.solution_path, result.solution_path[1:], strict=False
    ):
        assert child.parent is parent


def test_deadlock_leaves_are_counted_and_backtracked() -> None:
    problem, strategy_name = _backtracking_case()
    result = _solve(strategy_name, problem)
    assert result.metrics.deadlocks <= result.metrics.backtracks


def test_no_state_repeats_along_any_explored_path(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        result = _solve("descending", problem)
        for step in result.trace.of_event(TraceEvent.GENERATE):
            assert step.depth >= 1
        assert len({node.state for node in result.solution_path}) == len(
            result.solution_path
        )


def test_visits_each_node_at_most_once(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            result = _solve(name, problem)
            visited = [
                step.node_order for step in result.trace.of_event(TraceEvent.VISIT)
            ]
            assert len(set(visited)) == len(visited)


def test_solution_is_not_shorter_than_the_optimum(
    problems: tuple[Problem, ...],
) -> None:
    from core.domain.state_space import shortest_distance

    for problem in problems:
        optimum = shortest_distance(problem.initial, problem.goal)
        assert optimum is not None
        for name in STRATEGIES:
            length = _solve(name, problem).solution_length
            assert length is not None
            assert length >= optimum
