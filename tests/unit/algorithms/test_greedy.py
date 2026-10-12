from __future__ import annotations

import pytest

from core.algorithms.greedy.algorithm import GreedySearch
from core.algorithms.ordered.algorithm import OrderedSearch
from core.costs.domain.base import CostFunction
from core.costs.domain.registry import COSTS, DEFAULT_COST
from core.domain.problem import Problem
from core.domain.state import State
from core.domain.state_space import all_states, shortest_distance
from core.heuristics.domain.base import Heuristic
from core.heuristics.domain.registry import DEFAULT_HEURISTIC, HEURISTICS
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree

HEURISTIC_IDS = list(HEURISTICS)


def _solve(
    strategy_name: str,
    problem: Problem,
    tree: SearchTree | None = None,
    heuristic: Heuristic = DEFAULT_HEURISTIC,
    cost: CostFunction = DEFAULT_COST,
) -> SearchResult:
    search = GreedySearch(
        tree or SearchTree(cost=cost), STRATEGIES[strategy_name], heuristic=heuristic
    )
    return search.solve(problem)


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
def test_p1_matches_the_presentation(
    strategy_name: str, problems: tuple[Problem, ...]
) -> None:
    result = _solve(strategy_name, problems[0])
    assert result.outcome is Outcome.SUCCESS
    assert result.applied_rules == ("R4", "R1", "R1")
    assert result.solution_cost == 13 + 12 + 11
    assert result.metrics.iterations == 4
    assert result.metrics.nodes_generated == 9
    assert result.metrics.nodes_visited == 3


@pytest.mark.parametrize("heuristic", HEURISTICS.values(), ids=HEURISTIC_IDS)
def test_solves_every_goal_in_the_space(
    heuristic: Heuristic, initial_state: State
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            result = _solve(name, problem, heuristic=heuristic)
            assert result.outcome is Outcome.SUCCESS


@pytest.mark.parametrize("heuristic", HEURISTICS.values(), ids=HEURISTIC_IDS)
def test_the_second_expansion_is_the_root_child_with_the_lowest_heuristic(
    heuristic: Heuristic, initial_state: State
) -> None:
    for goal in all_states():
        if goal == initial_state:
            continue
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            tree = SearchTree()
            result = _solve(name, problem, tree, heuristic=heuristic)
            visits = result.trace.of_event(TraceEvent.VISIT)
            children = [node for node in tree.nodes if node.depth == 1]
            lowest = min(heuristic.estimate(node.state, goal) for node in children)
            second = visits[1].state if len(visits) > 1 else goal
            assert heuristic.estimate(second, goal) == lowest


def test_the_cost_function_does_not_change_the_path(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            paths = {
                _solve(name, problem, cost=cost).applied_rules
                for cost in COSTS.values()
            }
            assert len(paths) == 1


def test_the_solution_cost_is_the_real_cost_of_the_path(initial_state: State) -> None:
    for cost in COSTS.values():
        for goal in all_states():
            result = _solve("ascending", Problem("SYNTHETIC", goal), cost=cost)
            total, state = 0, initial_state
            for node in result.solution_path[1:]:
                assert node.rule is not None
                total += cost.cost(node.rule, state)
                state = node.state
            assert result.solution_cost == total


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
    longer, dearer = 0, 0
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        found = _solve("ascending", problem)
        cheapest = OrderedSearch(SearchTree(), STRATEGIES["ascending"]).solve(problem)
        longer += found.solution_length != shortest_distance(initial_state, goal)
        assert found.solution_cost is not None and cheapest.solution_cost is not None
        dearer += found.solution_cost > cheapest.solution_cost
    assert longer and dearer


def test_never_backtracks(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            assert _solve(name, problem).metrics.backtracks == 0
