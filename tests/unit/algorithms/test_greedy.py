from __future__ import annotations

import pytest

from core.algorithms.greedy.algorithm import GreedySearch
from core.domain.heuristic import misplacement
from core.domain.problem import Problem
from core.domain.state import State
from core.domain.state_space import all_states
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree


def _solve(
    strategy_name: str, problem: Problem, tree: SearchTree | None = None
) -> SearchResult:
    return GreedySearch(tree or SearchTree(), STRATEGIES[strategy_name]).solve(problem)


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
def test_p1_matches_the_presentation(
    strategy_name: str, problems: tuple[Problem, ...]
) -> None:
    result = _solve(strategy_name, problems[0])
    assert result.outcome is Outcome.SUCCESS
    assert result.applied_rules == ("R4", "R1", "R1")
    assert result.metrics.iterations == 4
    assert result.metrics.nodes_generated == 4


def test_each_step_takes_the_child_with_the_lowest_heuristic(
    initial_state: State,
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            result = _solve(name, problem)
            generated = result.trace.of_event(TraceEvent.GENERATE)
            states = [initial_state, *(step.state for step in generated)]
            for index in range(1, len(states)):
                parent, child = states[index - 1], states[index]
                options = [
                    rule.apply(parent)
                    for rule in SearchTree().rules
                    if rule.is_applicable(parent)
                    and rule.apply(parent) not in states[:index]
                ]
                assert misplacement(child, goal) == min(
                    misplacement(option, goal) for option in options
                )


def test_generates_one_node_per_step(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            result = _solve(name, problem)
            generated = result.trace.of_event(TraceEvent.GENERATE)
            assert [step.depth for step in generated] == list(
                range(1, len(generated) + 1)
            )
            assert result.metrics.max_frontier == 1


def test_can_end_in_deadlock(initial_state: State) -> None:
    outcomes = {
        _solve(name, Problem("SYNTHETIC", goal, initial=initial_state)).outcome
        for goal in all_states()
        for name in STRATEGIES
    }
    assert outcomes == {Outcome.SUCCESS, Outcome.DEADLOCK}


def test_never_backtracks(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        for name in STRATEGIES:
            assert _solve(name, problem).metrics.backtracks == 0
