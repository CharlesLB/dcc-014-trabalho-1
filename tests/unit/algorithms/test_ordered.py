from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

import pytest

from core.algorithms.domain.registry import ALGORITHMS
from core.algorithms.ordered import OrderedSearch
from core.domain.problem import INITIAL_STATE, Problem
from core.domain.state import State
from core.domain.state_space import all_states, cheapest_cost, shortest_distance
from core.rules.domain.base import Disk
from core.rules.moves import R1, R2, R3, R4, R5, R6, Move
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree
from libs.outputs.tree_render import render_tree


@dataclass(frozen=True, slots=True)
class _PricedMove(Move):
    price: int

    def cost(self, state: State) -> int:
        return self.price


def _solve(
    strategy_name: str, problem: Problem, tree: SearchTree | None = None
) -> SearchResult:
    search = OrderedSearch(tree or SearchTree(), STRATEGIES[strategy_name])
    return search.solve(problem)


def test_always_succeeds(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            assert _solve(name, problem).outcome is Outcome.SUCCESS


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
def test_cost_matches_the_independent_cheapest_cost(
    strategy_name: str, initial_state: State
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        result = _solve(strategy_name, problem)
        assert result.solution_cost == cheapest_cost(initial_state, goal)


def test_solution_cost_is_the_sum_of_its_rules(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            result = _solve(name, problem)
            path = result.solution_path
            assert result.solution_cost == sum(
                child.rule.cost(parent.state)
                for parent, child in pairwise(path)
                if child.rule is not None
            )


def test_expansion_order_is_by_non_decreasing_cost(
    problems: tuple[Problem, ...],
) -> None:
    for problem in problems:
        for name in STRATEGIES:
            tree = SearchTree()
            result = _solve(name, problem, tree)
            cost_of = {node.order: node.cost for node in tree.nodes}
            costs = [
                cost_of[step.node_order]
                for step in result.trace.of_event(TraceEvent.VISIT)
            ]
            assert costs == sorted(costs)


def test_no_state_is_expanded_twice(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            visited = [
                step.state
                for step in _solve(name, problem).trace.of_event(TraceEvent.VISIT)
            ]
            assert len(set(visited)) == len(visited)


def test_no_method_finds_a_cheaper_solution(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for strategy_name, strategy in STRATEGIES.items():
            optimum = _solve(strategy_name, problem).solution_cost
            assert optimum is not None
            for algorithm in ALGORITHMS.values():
                cost = algorithm(SearchTree(), strategy).solve(problem).solution_cost
                if cost is not None:
                    assert cost >= optimum


def test_a_goal_equal_to_the_initial_state_costs_nothing() -> None:
    for state in all_states():
        problem = Problem("SYNTHETIC", state, initial=state)
        assert _solve("ascending", problem).solution_cost == 0


def test_never_backtracks(problems: tuple[Problem, ...]) -> None:
    for problem in problems:
        for name in STRATEGIES:
            assert _solve(name, problem).metrics.backtracks == 0


def test_cheaper_path_replaces_the_open_node() -> None:
    expensive_r2 = _PricedMove(R2.id, R2.origin, R2.destination, price=30)
    tree = SearchTree(rules=(R1, expensive_r2, R3, R4, R5, R6))
    direct = R2.apply(INITIAL_STATE)
    detour = R4.apply(R1.apply(INITIAL_STATE))
    assert direct == detour

    result = _solve("ascending", Problem("SYNTHETIC", direct), tree)

    assert result.applied_rules == ("R1", "R4")
    assert result.solution_cost == R1.cost(INITIAL_STATE) + R4.cost(
        R1.apply(INITIAL_STATE)
    )
    replaced = next(
        node for node in tree.nodes if node.state == direct and node.cost == 30
    )
    visited = {step.node_order for step in result.trace.of_event(TraceEvent.VISIT)}
    assert replaced.order not in visited
    assert any(
        step.node_order == 0 and step.rule_id == "R2" and step.state == direct
        for step in result.trace.of_event(TraceEvent.PRUNE)
    )
    assert f"#{replaced.order} " not in render_tree(result.trace)


def test_never_trades_moves_for_effort(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            result = _solve(name, problem)
            assert result.solution_length == shortest_distance(initial_state, goal)


def test_p1_replaces_an_open_node_with_a_cheaper_one(
    problems: tuple[Problem, ...],
) -> None:
    result = _solve("ascending", problems[0])
    replaced = [
        step
        for step in result.trace.of_event(TraceEvent.PRUNE)
        if step.state == ((Disk.GREEN, Disk.BLUE), (Disk.RED,), ())
        and step.rule_id == "R5"
    ]
    assert replaced
