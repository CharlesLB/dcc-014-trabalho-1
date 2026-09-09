from __future__ import annotations

import pytest

from core.algorithms.breadth_first import BreadthFirstSearch
from core.algorithms.domain.registry import ALGORITHMS
from core.domain.problem import Problem
from core.domain.state import State
from core.domain.state_space import all_states, shortest_distance
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.tree import SearchTree


def _length(algorithm_name: str, strategy_name: str, problem: Problem) -> int | None:
    algorithm = ALGORITHMS[algorithm_name](SearchTree(), STRATEGIES[strategy_name])
    return algorithm.solve(problem).solution_length


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
def test_breadth_first_equals_the_independent_oracle(
    strategy_name: str, initial_state: State
) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        optimum = shortest_distance(initial_state, goal)
        found = (
            BreadthFirstSearch(SearchTree(), STRATEGIES[strategy_name])
            .solve(problem)
            .solution_length
        )
        assert found == optimum


@pytest.mark.parametrize("strategy_name", sorted(STRATEGIES))
def test_no_method_beats_breadth_first(
    strategy_name: str, problems: tuple[Problem, ...]
) -> None:
    for problem in problems:
        optimum = _length("breadth_first", strategy_name, problem)
        assert optimum is not None
        for algorithm_name in ALGORITHMS:
            length = _length(algorithm_name, strategy_name, problem)
            if length is not None:
                assert length >= optimum


@pytest.mark.slow
def test_breadth_first_solves_every_goal_in_the_space(initial_state: State) -> None:
    for goal in all_states():
        problem = Problem("SYNTHETIC", goal, initial=initial_state)
        result = BreadthFirstSearch(SearchTree(), STRATEGIES["ascending"]).solve(
            problem
        )
        assert result.outcome.is_success
        assert result.solution_length == shortest_distance(initial_state, goal)
