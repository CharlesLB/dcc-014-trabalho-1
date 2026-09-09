from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.domain.state import State
from core.search_tree.result import SearchResult
from libs.ranking.leaderboard import Leaderboard, Summary


@dataclass(frozen=True, slots=True)
class ProblemReport:
    problem_id: str
    initial_state: State
    goal_state: State
    results: tuple[SearchResult, ...]
    leaderboard: Leaderboard | None = None


@dataclass(frozen=True, slots=True)
class Report:
    problems: tuple[ProblemReport, ...]
    summary: Summary | None = None
    show_tree: bool = False
    show_trace: bool = False
    show_states: bool = False


class Formatter(Protocol):
    def render(self, report: Report) -> str: ...
