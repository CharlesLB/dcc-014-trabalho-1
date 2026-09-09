from __future__ import annotations

from core.algorithms.irrevocable import IrrevocableSearch
from core.domain.problem import INITIAL_STATE, Problem
from core.domain.state import State, build_state
from core.rules.domain.base import Disk
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree


def _deadlocking_case() -> tuple[Problem, str]:
    from core.domain.state_space import all_states

    for goal in all_states():
        if goal == INITIAL_STATE:
            continue
        problem = Problem("SYNTHETIC", goal)
        for name in STRATEGIES:
            algorithm = IrrevocableSearch(SearchTree(), STRATEGIES[name])
            if algorithm.solve(problem).outcome is Outcome.DEADLOCK:
                return problem, name
    raise AssertionError("no deadlocking configuration found")


def test_deadlock_is_reported_without_exception() -> None:
    problem, strategy_name = _deadlocking_case()
    result = IrrevocableSearch(SearchTree(), STRATEGIES[strategy_name]).solve(problem)

    assert result.outcome is Outcome.DEADLOCK
    assert result.solution_path == ()
    assert result.metrics.deadlocks == 1


def test_deadlock_never_backtracks() -> None:
    problem, strategy_name = _deadlocking_case()
    result = IrrevocableSearch(SearchTree(), STRATEGIES[strategy_name]).solve(problem)
    assert result.metrics.backtracks == 0
    assert result.trace.of_event(TraceEvent.BACKTRACK) == ()


def test_never_backtracks_on_any_catalogued_problem(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        for name in STRATEGIES:
            result = IrrevocableSearch(SearchTree(), STRATEGIES[name]).solve(problem)
            assert result.metrics.backtracks == 0


def test_generates_a_single_child_per_visited_node(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        for name in STRATEGIES:
            result = IrrevocableSearch(SearchTree(), STRATEGIES[name]).solve(problem)
            generated = result.trace.of_event(TraceEvent.GENERATE)
            parents = [step.parent_order for step in generated]
            assert len(set(parents)) == len(parents)


def test_path_grows_by_one_level_each_iteration(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        result = IrrevocableSearch(SearchTree(), STRATEGIES["ascending"]).solve(problem)
        depths = [step.depth for step in result.trace.of_event(TraceEvent.GENERATE)]
        assert depths == list(range(1, len(depths) + 1))


def test_goal_reached_at_the_root_succeeds_immediately() -> None:
    goal: State = build_state((Disk.GREEN, Disk.RED), (Disk.BLUE,), ())
    result = IrrevocableSearch(SearchTree(), STRATEGIES["ascending"]).solve(
        Problem("TRIVIAL", goal, initial=goal)
    )
    assert result.outcome is Outcome.SUCCESS
    assert result.applied_rules == ()
    assert result.metrics.nodes_visited == 0
