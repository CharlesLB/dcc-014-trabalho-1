from __future__ import annotations

import pytest

from core.domain.problem import (
    INITIAL_STATE,
    PROBLEM_IDS,
    PROBLEMS,
    Problem,
    UnknownProblemError,
    get_problem,
)
from core.domain.state import InvalidStateError, build_state, is_valid
from core.domain.state_space import reachable_from
from core.rules.domain.base import Disk


def test_initial_state_is_valid() -> None:
    assert is_valid(INITIAL_STATE)


def test_catalog_is_not_empty() -> None:
    assert PROBLEMS


def test_problem_identifiers_are_unique() -> None:
    assert len(PROBLEM_IDS) == len(PROBLEMS)


def test_every_goal_is_a_valid_state() -> None:
    assert all(is_valid(problem.goal) for problem in PROBLEMS)


def test_every_goal_is_reachable_from_the_initial_state() -> None:
    reachable = reachable_from(INITIAL_STATE)
    assert all(problem.goal in reachable for problem in PROBLEMS)


def test_is_goal_recognises_only_the_goal_configuration() -> None:
    for problem in PROBLEMS:
        assert problem.is_goal(problem.goal)
        assert not problem.is_goal(
            build_state((Disk.GREEN, Disk.RED, Disk.BLUE), (), ())
        )


def test_get_problem_returns_the_catalog_instance() -> None:
    for problem in PROBLEMS:
        assert get_problem(problem.id) is problem


def test_get_problem_rejects_unknown_identifier() -> None:
    with pytest.raises(UnknownProblemError):
        get_problem("P999")


def test_problem_rejects_invalid_goal() -> None:
    with pytest.raises(InvalidStateError):
        Problem("PX", ((Disk.GREEN,), (), ()))


def test_problem_is_immutable() -> None:
    with pytest.raises(AttributeError):
        PROBLEMS[0].id = "PX"  # type: ignore[misc]
