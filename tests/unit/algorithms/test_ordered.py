from __future__ import annotations

import pytest

from core.algorithms.ordered.algorithm import OrderedSearch
from core.domain.heuristic import misplacement
from core.domain.problem import Problem
from core.domain.state import State, build_state
from core.domain.state_space import all_states, shortest_distance
from core.rules.domain.base import Disk
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree
from libs.outputs.tree_render import render_tree


def _solve(
    strategy_name: str, problem: Problem, tree: SearchTree | None = None
) -> SearchResult:
    search = OrderedSearch(tree or SearchTree(), STRATEGIES[strategy_name])
    return search.solve(problem)


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
def test_solves_every_goal_in_the_space(
    strategy_name: str, initial_state: State
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        assert _solve(strategy_name, problem).outcome is Outcome.SUCCESS


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
def test_p1_matches_the_presentation(
    strategy_name: str, problems: tuple[Problem, ...]
) -> None:
    result = _solve(strategy_name, problems[0])
    assert result.applied_rules == ("R4", "R1", "R1")
    assert result.metrics.iterations == 4
    assert result.metrics.nodes_generated == 9
    assert result.metrics.nodes_visited == 3


def test_solution_cost_is_the_number_of_moves(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            result = _solve(name, problem)
            assert result.solution_cost == result.solution_length


def test_the_second_expansion_is_the_root_child_with_the_lowest_heuristic(
    initial_state: State,
) -> None:
    for goal in all_states():
        if goal == initial_state:
            continue
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            tree = SearchTree()
            result = _solve(name, problem, tree)
            visits = result.trace.of_event(TraceEvent.VISIT)
            children = [node for node in tree.nodes if node.depth == 1]
            lowest = min(misplacement(node.state, goal) for node in children)
            second = visits[1].state if len(visits) > 1 else goal
            assert misplacement(second, goal) == lowest


def test_no_state_is_expanded_twice(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            visited = [
                step.state
                for step in _solve(name, problem).trace.of_event(TraceEvent.VISIT)
            ]
            assert len(set(visited)) == len(visited)


def test_is_not_always_optimal(initial_state: State) -> None:
    longer = [
        goal
        for goal in all_states()
        if _solve("ascending", Problem("SYNTHETIC", goal)).solution_length
        != shortest_distance(initial_state, goal)
    ]
    assert longer


def test_a_goal_equal_to_the_initial_state_costs_nothing() -> None:
    for state in all_states():
        problem = Problem("SYNTHETIC", state, initial=state)
        assert _solve("ascending", problem).solution_cost == 0


def test_never_backtracks(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            assert _solve(name, problem).metrics.backtracks == 0


def test_shorter_path_replaces_the_open_node() -> None:
    goal = build_state((), (Disk.GREEN, Disk.BLUE), (Disk.RED,))
    tree = SearchTree()
    result = _solve("ascending", Problem("SYNTHETIC", goal), tree)

    older, newer = tree.nodes[10], tree.nodes[12]
    assert older.state == newer.state
    assert newer.cost < older.cost
    visited = {step.node_order for step in result.trace.of_event(TraceEvent.VISIT)}
    assert older.order not in visited
    assert any(
        step.node_order == older.parent.order and step.state == older.state
        for step in result.trace.of_event(TraceEvent.PRUNE)
        if older.parent is not None
    )
    assert f"#{older.order} " not in render_tree(result.trace)
