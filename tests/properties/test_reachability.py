from __future__ import annotations

from core.domain.state import State
from core.domain.state_space import reachable_from, shortest_distance

EXPECTED_STATE_COUNT = 36
MAX_PATH_LENGTH = EXPECTED_STATE_COUNT


def test_every_state_reaches_every_other(states: tuple[State, ...]) -> None:
    universe = set(states)
    for state in states:
        assert reachable_from(state) == universe


def test_no_shortest_path_exceeds_the_state_count(states: tuple[State, ...]) -> None:
    source = states[0]
    for target in states:
        distance = shortest_distance(source, target)
        assert distance is not None
        assert 0 <= distance <= MAX_PATH_LENGTH
