from __future__ import annotations

from dataclasses import replace

import pytest

from config import settings
from core.algorithms.domain.base import SearchAlgorithm
from core.algorithms.domain.registry import ALGORITHMS
from core.domain.problem import INITIAL_STATE, PROBLEMS, Problem
from core.rules.domain.catalog import RULES, get_rule
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.tree import SearchTree

MATRIX = [
    (algorithm_name, strategy_name)
    for algorithm_name in sorted(ALGORITHMS)
    for strategy_name in sorted(STRATEGIES)
]
MATRIX_IDS = [f"{algorithm}-{strategy}" for algorithm, strategy in MATRIX]


def _run(algorithm_name: str, strategy_name: str, problem: Problem) -> SearchResult:
    algorithm: SearchAlgorithm = ALGORITHMS[algorithm_name](
        SearchTree(), STRATEGIES[strategy_name]
    )
    return algorithm.solve(problem)


@pytest.fixture(params=MATRIX, ids=MATRIX_IDS)
def result(
    request: pytest.FixtureRequest, problems: tuple[Problem, ...]
) -> SearchResult:
    algorithm_name, strategy_name = request.param
    return _run(algorithm_name, strategy_name, problems[0])


def test_result_is_well_formed(result: SearchResult) -> None:
    assert isinstance(result, SearchResult)
    assert result.outcome in Outcome
    assert result.algorithm in ALGORITHMS
    assert result.strategy in STRATEGIES


def test_solution_path_is_empty_unless_successful(result: SearchResult) -> None:
    if result.outcome.is_success:
        assert result.solution_path
    else:
        assert result.solution_path == ()
        assert result.applied_rules == ()
        assert result.solution_length is None


def test_successful_path_starts_at_the_initial_state(
    result: SearchResult, problems: tuple[Problem, ...]
) -> None:
    if not result.outcome.is_success:
        pytest.skip("sem solucao para verificar")
    assert result.solution_path[0].state == problems[0].initial


def test_successful_path_ends_at_the_goal(
    result: SearchResult, problems: tuple[Problem, ...]
) -> None:
    if not result.outcome.is_success:
        pytest.skip("sem solucao para verificar")
    assert problems[0].is_goal(result.solution_path[-1].state)


def test_solution_is_replayable_from_scratch(
    result: SearchResult, problems: tuple[Problem, ...]
) -> None:
    if not result.outcome.is_success:
        pytest.skip("sem solucao para verificar")

    state = problems[0].initial
    for rule_id in result.applied_rules:
        rule = get_rule(rule_id)
        assert rule.is_applicable(state)
        state = rule.apply(state)
    assert problems[0].is_goal(state)


def test_each_step_is_justified_by_its_rule(result: SearchResult) -> None:
    if not result.outcome.is_success:
        pytest.skip("sem solucao para verificar")

    for parent, child in zip(
        result.solution_path, result.solution_path[1:], strict=False
    ):
        assert child.rule is not None
        assert child.parent is parent
        assert child.depth == parent.depth + 1
        assert child.rule.is_applicable(parent.state)
        assert child.rule.apply(parent.state) == child.state


def test_solution_path_has_no_repeated_state(result: SearchResult) -> None:
    states = [node.state for node in result.solution_path]
    assert len(set(states)) == len(states)


def test_applied_rules_match_the_path(result: SearchResult) -> None:
    assert len(result.applied_rules) == max(len(result.solution_path) - 1, 0)


def test_visited_never_exceeds_generated(result: SearchResult) -> None:
    assert result.metrics.nodes_visited <= result.metrics.nodes_generated


def test_iterations_respect_the_guard(result: SearchResult) -> None:
    assert result.metrics.iterations <= settings.MAX_ITERATIONS


def test_counters_are_non_negative(result: SearchResult) -> None:
    metrics = result.metrics
    assert (
        min(
            metrics.iterations,
            metrics.nodes_generated,
            metrics.nodes_visited,
            metrics.rules_tested,
            metrics.backtracks,
            metrics.deadlocks,
            metrics.max_depth,
        )
        >= 0
    )
    assert metrics.elapsed_ms >= 0.0


@pytest.mark.parametrize(("algorithm_name", "strategy_name"), MATRIX, ids=MATRIX_IDS)
def test_execution_is_deterministic(
    algorithm_name: str, strategy_name: str, problems: tuple[Problem, ...]
) -> None:
    first = _run(algorithm_name, strategy_name, problems[0])
    second = _run(algorithm_name, strategy_name, problems[0])

    assert first.outcome is second.outcome
    assert first.applied_rules == second.applied_rules
    assert replace(first.metrics, elapsed_ms=0.0) == replace(
        second.metrics, elapsed_ms=0.0
    )
    assert [step.event for step in first.trace] == [step.event for step in second.trace]


@pytest.mark.parametrize(("algorithm_name", "strategy_name"), MATRIX, ids=MATRIX_IDS)
def test_execution_mutates_neither_the_initial_state_nor_the_catalog(
    algorithm_name: str, strategy_name: str, problems: tuple[Problem, ...]
) -> None:
    initial_snapshot = INITIAL_STATE
    catalog_snapshot = tuple((rule.id, rule.origin, rule.destination) for rule in RULES)

    _run(algorithm_name, strategy_name, problems[0])

    assert initial_snapshot == INITIAL_STATE
    assert tuple((r.id, r.origin, r.destination) for r in RULES) == catalog_snapshot


@pytest.mark.parametrize(("algorithm_name", "strategy_name"), MATRIX, ids=MATRIX_IDS)
def test_iteration_limit_produces_cutoff(
    algorithm_name: str, strategy_name: str, problems: tuple[Problem, ...]
) -> None:
    algorithm = ALGORITHMS[algorithm_name](
        SearchTree(), STRATEGIES[strategy_name], max_iterations=1
    )
    result = algorithm.solve(problems[0])
    assert result.outcome is Outcome.CUTOFF
    assert result.metrics.iterations <= 1


@pytest.mark.parametrize(("algorithm_name", "strategy_name"), MATRIX, ids=MATRIX_IDS)
def test_every_catalogued_problem_is_handled(
    algorithm_name: str, strategy_name: str
) -> None:
    for problem in PROBLEMS:
        result = _run(algorithm_name, strategy_name, problem)
        assert result.outcome in Outcome
        assert result.problem == problem.id


def test_root_node_is_counted_as_generated(result: SearchResult) -> None:
    assert result.metrics.nodes_generated >= 1


def test_nodes_carry_increasing_orders(result: SearchResult) -> None:
    orders = [node.order for node in result.solution_path]
    assert orders == sorted(orders)
    assert all(isinstance(node, Node) for node in result.solution_path)
