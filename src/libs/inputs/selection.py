from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import settings


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    problem_ids: tuple[str, ...]
    algorithm_names: tuple[str, ...]
    strategy_names: tuple[str, ...]
    custom_order: tuple[str, ...] | None = None
    show_tree: bool = False
    show_trace: bool = False
    show_states: bool = False
    output_format: str = settings.DEFAULT_OUTPUT_FORMAT
    rank_mode: str = settings.DEFAULT_RANK_MODE
    max_iterations: int = settings.MAX_ITERATIONS
    output_path: Path | None = None
    svg_dir: Path | None = None
    list_only: bool = False
    show_help: bool = False
    verbose: bool = False
    seed: int | None = None

    @property
    def execution_count(self) -> int:
        return (
            len(self.problem_ids) * len(self.algorithm_names) * len(self.strategy_names)
        )
