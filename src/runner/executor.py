from __future__ import annotations

from core.algorithms.domain.registry import get_algorithm
from core.domain.problem import Problem, get_problem
from core.rules.strategies.custom_order import CUSTOM, CustomOrderStrategy
from core.rules.strategies.domain.base import ControlStrategy
from core.rules.strategies.domain.registry import get_strategy
from core.search_tree.result import SearchResult
from core.search_tree.tree import SearchTree
from libs.inputs.selection import ExecutionRequest


def run_problem(
    problem: Problem, request: ExecutionRequest
) -> tuple[SearchResult, ...]:
    return tuple(
        get_algorithm(algorithm_name)(
            SearchTree(),
            resolve_strategy(strategy_name, request.custom_order),
            max_iterations=request.max_iterations,
        ).solve(problem)
        for algorithm_name in request.algorithm_names
        for strategy_name in request.strategy_names
    )


def run_matrix(
    request: ExecutionRequest,
) -> tuple[tuple[Problem, tuple[SearchResult, ...]], ...]:
    return tuple(
        (problem, run_problem(problem, request))
        for problem in (get_problem(problem_id) for problem_id in request.problem_ids)
    )


def resolve_strategy(
    name: str, custom_order: tuple[str, ...] | None
) -> ControlStrategy:
    if name == CUSTOM.name and custom_order is not None:
        return CustomOrderStrategy(sequence=custom_order)
    return get_strategy(name)
