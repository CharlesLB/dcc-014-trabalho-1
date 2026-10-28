from __future__ import annotations

from dataclasses import dataclass

import pytest

from core.algorithms.astar.algorithm import AStarSearch
from core.algorithms.greedy.algorithm import GreedySearch
from core.algorithms.ordered.algorithm import OrderedSearch
from core.costs.domain.base import CostFunction
from core.costs.domain.registry import COSTS, DEFAULT_COST
from core.costs.unit import UNIT
from core.costs.weight_distance import WEIGHT_DISTANCE
from core.domain.problem import Problem
from core.domain.state import State
from core.domain.state_space import all_states, shortest_distance
from core.heuristics.domain.base import Heuristic
from core.heuristics.domain.registry import DEFAULT_HEURISTIC, HEURISTICS
from core.heuristics.misplacement import MISPLACEMENT
from core.heuristics.misplacement_cost import MISPLACEMENT_COST
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree

HEURISTIC_IDS = list(HEURISTICS)


@dataclass(frozen=True, slots=True)
class _Zero:
    name: str = "zero"

    def estimate(self, state: State, goal: State) -> int:
        return 0


def _solve(
    strategy_name: str,
    problem: Problem,
    tree: SearchTree | None = None,
    heuristic: Heuristic | None = None,
    cost: CostFunction = DEFAULT_COST,
) -> SearchResult:
    search = AStarSearch(
        tree or SearchTree(cost=cost), STRATEGIES[strategy_name], heuristic=heuristic
    )
    return search.solve(problem)


def _cheapest(strategy_name: str, problem: Problem, cost: CostFunction) -> int:
    found = OrderedSearch(SearchTree(cost=cost), STRATEGIES[strategy_name]).solve(
        problem
    )
    assert found.solution_cost is not None
    return found.solution_cost


def test_uses_the_heuristic_in_cost_units_by_default() -> None:
    tree, strategy = SearchTree(), STRATEGIES["ascending"]
    chosen = AStarSearch(tree, strategy, heuristic=MISPLACEMENT)
    assert AStarSearch(tree, strategy).heuristic is MISPLACEMENT_COST
    assert GreedySearch(tree, strategy).heuristic is DEFAULT_HEURISTIC
    assert chosen.heuristic is MISPLACEMENT


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
@pytest.mark.parametrize(("prune", "generated"), [(True, 9), (False, 10)])
def test_p1_matches_the_presentation(
    strategy_name: str, prune: bool, generated: int, problems: tuple[Problem, ...]
) -> None:
    search = AStarSearch(SearchTree(), STRATEGIES[strategy_name], prune=prune)
    result = search.solve(problems[0])
    assert result.outcome is Outcome.SUCCESS
    assert result.applied_rules == ("R4", "R1", "R1")
    assert result.solution_cost == 13 + 12 + 11
    assert result.metrics.iterations == 4
    assert result.metrics.nodes_generated == generated
    assert result.metrics.nodes_visited == 3


def test_on_the_p1_path_the_evaluation_never_leaves_the_solution_cost(
    problems: tuple[Problem, ...],
) -> None:
    problem = problems[0]
    result = _solve("ascending", problem)
    evaluations = {
        node.cost + MISPLACEMENT_COST.estimate(node.state, problem.goal)
        for node in result.solution_path
    }
    assert evaluations == {36}


@pytest.mark.parametrize("heuristic", HEURISTICS.values(), ids=HEURISTIC_IDS)
def test_every_heuristic_finds_the_cheapest_solution_with_the_default_cost(
    heuristic: Heuristic, initial_state: State
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            result = _solve(name, problem, heuristic=heuristic)
            assert result.outcome is Outcome.SUCCESS
            assert result.solution_cost == _cheapest(name, problem, DEFAULT_COST)


@pytest.mark.parametrize("cost", COSTS.values(), ids=list(COSTS))
def test_with_the_count_of_moves_it_is_optimal_under_every_cost(
    cost: CostFunction, initial_state: State
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            found = _solve(name, problem, heuristic=MISPLACEMENT, cost=cost)
            assert found.solution_cost == _cheapest(name, problem, cost)


@pytest.mark.parametrize(
    "cost", [UNIT, WEIGHT_DISTANCE], ids=["unit", "weight_distance"]
)
def test_with_a_cheaper_cost_the_default_heuristic_overestimates(
    cost: CostFunction, initial_state: State
) -> None:
    dearer = 0
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        found = _solve("ascending", problem, cost=cost).solution_cost
        dearer += found != _cheapest("ascending", problem, cost)
    assert dearer


def test_with_unit_cost_and_the_count_of_moves_the_solution_is_the_shortest(
    initial_state: State,
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            found = _solve(name, problem, heuristic=MISPLACEMENT, cost=UNIT)
            assert found.solution_length == shortest_distance(initial_state, goal)


def test_nodes_leave_the_open_list_in_order_of_evaluation(initial_state: State) -> None:
    for goal in all_states():
        for name in STRATEGIES:
            tree = SearchTree()
            result = _solve(name, Problem("SYNTHETIC", goal), tree)
            evaluations = [
                tree.nodes[step.node_order].cost
                + MISPLACEMENT_COST.estimate(step.state, goal)
                for step in result.trace.of_event(TraceEvent.VISIT)
            ]
            assert evaluations == sorted(evaluations)


def test_never_needs_more_iterations_than_the_ordered_search(
    initial_state: State,
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name, strategy in STRATEGIES.items():
            ordered = OrderedSearch(SearchTree(), strategy).solve(problem)
            found = _solve(name, problem)
            assert found.metrics.iterations <= ordered.metrics.iterations


def test_with_a_zero_heuristic_it_is_the_ordered_search(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name, strategy in STRATEGIES.items():
            ordered = OrderedSearch(SearchTree(), strategy).solve(problem)
            found = _solve(name, problem, heuristic=_Zero())
            assert found.applied_rules == ordered.applied_rules
            assert [(s.event, s.node_order) for s in found.trace] == [
                (s.event, s.node_order) for s in ordered.trace
            ]


def test_the_heuristic_in_cost_units_saves_iterations(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            in_cost = _solve(name, problem).metrics.iterations
            in_moves = _solve(name, problem, heuristic=MISPLACEMENT).metrics.iterations
            assert in_cost <= in_moves


def test_the_solution_cost_is_the_real_cost_of_the_path(initial_state: State) -> None:
    for goal in all_states():
        result = _solve("ascending", Problem("SYNTHETIC", goal))
        total, state = 0, initial_state
        for node in result.solution_path[1:]:
            assert node.rule is not None
            total += DEFAULT_COST.cost(node.rule, state)
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


def test_a_goal_equal_to_the_initial_state_costs_nothing() -> None:
    for state in all_states():
        problem = Problem("SYNTHETIC", state, initial=state)
        result = _solve("ascending", problem)
        assert result.solution_cost == 0
        assert result.metrics.iterations == 1


def test_never_backtracks(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            assert _solve(name, problem).metrics.backtracks == 0
