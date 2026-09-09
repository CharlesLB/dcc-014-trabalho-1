from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class SearchMetrics:
    iterations: int
    nodes_generated: int
    nodes_visited: int
    rules_tested: int
    backtracks: int
    deadlocks: int
    max_depth: int
    elapsed_ms: float


@dataclass(slots=True)
class MetricsCollector:
    iterations: int = 0
    nodes_generated: int = 0
    nodes_visited: int = 0
    rules_tested: int = 0
    backtracks: int = 0
    deadlocks: int = 0
    max_depth: int = field(default=0)

    def count_iteration(self) -> None:
        self.iterations += 1

    def count_generated(self, depth: int) -> None:
        self.nodes_generated += 1
        self.max_depth = max(self.max_depth, depth)

    def count_visited(self) -> None:
        self.nodes_visited += 1

    def count_rule_test(self) -> None:
        self.rules_tested += 1

    def count_backtrack(self) -> None:
        self.backtracks += 1

    def count_deadlock(self) -> None:
        self.deadlocks += 1

    def seal(self, elapsed_ms: float) -> SearchMetrics:
        return SearchMetrics(
            iterations=self.iterations,
            nodes_generated=self.nodes_generated,
            nodes_visited=self.nodes_visited,
            rules_tested=self.rules_tested,
            backtracks=self.backtracks,
            deadlocks=self.deadlocks,
            max_depth=self.max_depth,
            elapsed_ms=elapsed_ms,
        )
