from __future__ import annotations

from itertools import pairwise

import pytest

from core.algorithms.domain.registry import ALGORITHMS
from core.algorithms.ordered.algorithm import OrderedSearch
from core.costs.domain.base import CostFunction
from core.costs.domain.registry import COSTS, DEFAULT_COST
from core.costs.unit import UNIT
from core.domain.problem import Problem
from core.domain.state import State
from core.domain.state_space import all_states, shortest_distance
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree
from libs.outputs.tree_render import render_tree

COST_IDS = list(COSTS)


def _solve(
    strategy_name: str,
    problem: Problem,
    tree: SearchTree | None = None,
    cost: CostFunction = DEFAULT_COST,
) -> SearchResult:
    search = OrderedSearch(tree or SearchTree(cost=cost), STRATEGIES[strategy_name])
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
    assert result.solution_cost == 3 + 2 + 1
    assert result.metrics.iterations == 10
    assert result.metrics.nodes_generated == 17


def test_with_unit_cost_the_solution_cost_is_the_number_of_moves(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        for name in STRATEGIES:
            result = _solve(name, problem, cost=UNIT)
            assert result.solution_cost == result.solution_length


def test_with_unit_cost_the_solution_is_the_shortest(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            found = _solve(name, problem, cost=UNIT).solution_length
            assert found == shortest_distance(initial_state, goal)


@pytest.mark.parametrize("cost", COSTS.values(), ids=COST_IDS)
def test_no_method_finds_a_cheaper_solution(
    cost: CostFunction, initial_state: State
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name, strategy in STRATEGIES.items():
            cheapest = _solve(name, problem, cost=cost).solution_cost
            assert cheapest is not None
            for algorithm in ALGORITHMS.values():
                other = algorithm(SearchTree(cost=cost), strategy).solve(problem)
                if other.solution_cost is not None:
                    assert other.solution_cost >= cheapest


def test_nodes_leave_the_open_list_in_order_of_cost(initial_state: State) -> None:
    for goal in all_states():
        tree = SearchTree()
        result = _solve("ascending", Problem("SYNTHETIC", goal), tree)
        visited = [
            tree.nodes[step.node_order].cost
            for step in result.trace.of_event(TraceEvent.VISIT)
        ]
        assert visited == sorted(visited)


def test_the_cheapest_path_can_have_more_moves_than_the_shortest(
    initial_state: State,
) -> None:
    longer = [
        goal
        for goal in all_states()
        if _solve("ascending", Problem("SYNTHETIC", goal)).solution_length
        != shortest_distance(initial_state, goal)
    ]
    assert longer


def test_no_state_is_expanded_twice(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            visited = [
                step.state
                for step in _solve(name, problem).trace.of_event(TraceEvent.VISIT)
            ]
            assert len(set(visited)) == len(visited)


def test_a_goal_equal_to_the_initial_state_costs_nothing() -> None:
    for state in all_states():
        problem = Problem("SYNTHETIC", state, initial=state)
        assert _solve("ascending", problem).solution_cost == 0


def test_never_backtracks(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            assert _solve(name, problem).metrics.backtracks == 0


def test_cheaper_path_replaces_the_open_node(initial_state: State) -> None:
    replaced = 0
    for goal in all_states():
        tree = SearchTree()
        result = _solve("ascending", Problem("SYNTHETIC", goal), tree)
        visited = {s.node_order for s in result.trace.of_event(TraceEvent.VISIT)}
        rendered = render_tree(result.trace)
        by_state: dict[State, list[int]] = {}
        for node in tree.nodes:
            by_state.setdefault(node.state, []).append(node.order)
        for orders in by_state.values():
            for older, newer in pairwise(orders):
                assert tree.nodes[newer].cost < tree.nodes[older].cost
                assert older not in visited
                assert f"#{older} " not in rendered
                replaced += 1
    assert replaced
