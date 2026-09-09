from __future__ import annotations

from dataclasses import dataclass

from core.search_tree.metrics import SearchMetrics
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome
from core.search_tree.trace import Trace


@dataclass(frozen=True, slots=True)
class SearchResult:
    algorithm: str
    strategy: str
    problem: str
    outcome: Outcome
    solution_path: tuple[Node, ...]
    applied_rules: tuple[str, ...]
    metrics: SearchMetrics
    trace: Trace

    @property
    def solution_length(self) -> int | None:
        return len(self.applied_rules) if self.outcome.is_success else None

    @property
    def label(self) -> str:
        return f"{self.algorithm} · {self.strategy}"
