from __future__ import annotations

import pytest

from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.domain.problem import PROBLEM_IDS
from core.rules.strategies.custom_order import CUSTOM, CustomOrderStrategy
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from core.search_tree.outcome import Outcome
from libs.inputs.parser import parse
from libs.inputs.validator import validate
from runner.executor import resolve_strategy, run_matrix


@pytest.fixture(scope="module")
def matrix() -> tuple[tuple[str, tuple[object, ...]], ...]:
    request = validate(parse(["--all"]))
    return tuple((problem.id, results) for problem, results in run_matrix(request))


def test_every_combination_is_executed() -> None:
    request = validate(parse(["--all"]))
    executed = run_matrix(request)
    assert len(executed) == len(PROBLEM_IDS)
    for _, results in executed:
        assert len(results) == len(ALGORITHM_NAMES) * len(STRATEGY_NAMES)


def test_every_execution_reports_its_own_labels() -> None:
    for problem, results in run_matrix(validate(parse(["--all"]))):
        for result in results:
            assert result.problem == problem.id
            assert result.algorithm in ALGORITHM_NAMES
            assert result.strategy in STRATEGY_NAMES
            assert result.outcome in Outcome


def test_combinations_are_unique() -> None:
    for _, results in run_matrix(validate(parse(["--all"]))):
        labels = [(result.algorithm, result.strategy) for result in results]
        assert len(set(labels)) == len(labels)


def test_narrowed_request_runs_a_single_execution() -> None:
    request = validate(
        parse(
            [
                "--problem",
                PROBLEM_IDS[0],
                "--algorithm",
                "backtracking",
                "--strategy",
                "ascending",
            ]
        )
    )
    executed = run_matrix(request)
    assert len(executed) == 1
    assert len(executed[0][1]) == 1


def test_custom_order_overrides_the_registered_strategy() -> None:
    sequence = ("R6", "R5", "R4", "R3", "R2", "R1")
    strategy = resolve_strategy("custom", sequence)
    assert isinstance(strategy, CustomOrderStrategy)
    assert strategy.sequence == sequence


def test_custom_strategy_without_order_uses_the_default() -> None:
    assert resolve_strategy("custom", None) is CUSTOM


def test_each_execution_uses_a_fresh_tree() -> None:
    for _, results in run_matrix(validate(parse(["--all"]))):
        for result in results:
            root_steps = [step for step in result.trace if step.node_order == 0]
            assert root_steps
            assert root_steps[0].parent_order is None
