from __future__ import annotations

from collections.abc import Iterable

from config import settings
from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.costs.domain.registry import COST_NAMES
from core.domain.problem import PROBLEM_IDS
from core.heuristics.domain.registry import HEURISTIC_NAMES
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from libs.inputs.exceptions import UnknownSelectionError
from libs.inputs.selection import ExecutionRequest


def validate(request: ExecutionRequest) -> ExecutionRequest:
    _require_known("problem", request.problem_ids, PROBLEM_IDS)
    _require_known("algorithm", request.algorithm_names, ALGORITHM_NAMES)
    _require_known("strategy", request.strategy_names, STRATEGY_NAMES)
    if request.heuristic_name is not None:
        _require_known("heuristic", (request.heuristic_name,), HEURISTIC_NAMES)
    _require_known("cost", (request.cost_name,), COST_NAMES)
    _require_known("format", (request.output_format,), settings.OUTPUT_FORMATS)
    _require_known("rank_mode", (request.rank_mode,), settings.RANK_MODES)
    return request


def _require_known(
    kind: str, selected: Iterable[str], available: tuple[str, ...]
) -> None:
    known = set(available)
    for name in selected:
        if name not in known:
            raise UnknownSelectionError(kind, name, available)
