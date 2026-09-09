from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import pytest

from libs.inputs.exceptions import UnknownSelectionError
from libs.inputs.parser import parse
from libs.inputs.selection import ExecutionRequest
from libs.inputs.validator import validate


def test_default_request_is_valid() -> None:
    request = parse([])
    assert validate(request) is request


@pytest.mark.parametrize(
    ("mutate", "kind"),
    [
        (lambda r: replace(r, problem_ids=("P999",)), "problem"),
        (lambda r: replace(r, algorithm_names=("astar",)), "algorithm"),
        (lambda r: replace(r, strategy_names=("random",)), "strategy"),
        (lambda r: replace(r, output_format="xml"), "format"),
        (lambda r: replace(r, rank_mode="elo"), "rank_mode"),
    ],
)
def test_unknown_name_is_rejected(
    mutate: Callable[[ExecutionRequest], ExecutionRequest], kind: str
) -> None:
    with pytest.raises(UnknownSelectionError) as raised:
        validate(mutate(parse([])))
    assert raised.value.kind == kind
    assert raised.value.available
