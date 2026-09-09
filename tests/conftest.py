from __future__ import annotations

import pytest

from core.domain.problem import INITIAL_STATE, PROBLEMS, Problem
from core.domain.state import State
from core.domain.state_space import all_states
from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULES
from core.rules.strategies.domain.base import ControlStrategy
from core.rules.strategies.domain.registry import STRATEGIES


@pytest.fixture(scope="session")
def states() -> tuple[State, ...]:
    return all_states()


@pytest.fixture(scope="session")
def rules() -> tuple[TransitionRule, ...]:
    return RULES


@pytest.fixture(scope="session")
def initial_state() -> State:
    return INITIAL_STATE


@pytest.fixture(scope="session")
def problems() -> tuple[Problem, ...]:
    return PROBLEMS


@pytest.fixture(params=sorted(STRATEGIES), ids=sorted(STRATEGIES))
def strategy(request: pytest.FixtureRequest) -> ControlStrategy:
    name: str = request.param
    return STRATEGIES[name]
