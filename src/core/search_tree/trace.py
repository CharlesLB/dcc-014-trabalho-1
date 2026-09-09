from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum, unique

from core.domain.state import State
from core.search_tree.node import Node


@unique
class TraceEvent(Enum):
    ROOT = "ROOT"
    VISIT = "VISIT"
    GENERATE = "GENERATE"
    PRUNE = "PRUNE"
    GOAL = "GOAL"
    DEADLOCK = "DEADLOCK"
    BACKTRACK = "BACKTRACK"
    CUTOFF = "CUTOFF"
    EXHAUSTED = "EXHAUSTED"


@dataclass(frozen=True, slots=True)
class TraceStep:
    iteration: int
    event: TraceEvent
    node_order: int
    parent_order: int | None
    depth: int
    rule_id: str | None
    state: State


@dataclass(frozen=True, slots=True)
class Trace:
    steps: tuple[TraceStep, ...] = ()

    def __iter__(self) -> Iterator[TraceStep]:
        return iter(self.steps)

    def __len__(self) -> int:
        return len(self.steps)

    def of_event(self, event: TraceEvent) -> tuple[TraceStep, ...]:
        return tuple(step for step in self.steps if step.event is event)


@dataclass(slots=True)
class TraceRecorder:
    _steps: list[TraceStep] = field(default_factory=list)

    def record(
        self,
        *,
        iteration: int,
        event: TraceEvent,
        node: Node,
        rule_id: str | None = None,
    ) -> None:
        parent = node.parent
        self._steps.append(
            TraceStep(
                iteration=iteration,
                event=event,
                node_order=node.order,
                parent_order=None if parent is None else parent.order,
                depth=node.depth,
                rule_id=rule_id if rule_id is not None else _rule_id_of(node),
                state=node.state,
            )
        )

    def record_prune(
        self, *, iteration: int, node: Node, rule_id: str, state: State
    ) -> None:
        self._steps.append(
            TraceStep(
                iteration=iteration,
                event=TraceEvent.PRUNE,
                node_order=node.order,
                parent_order=None if node.parent is None else node.parent.order,
                depth=node.depth,
                rule_id=rule_id,
                state=state,
            )
        )

    def seal(self) -> Trace:
        return Trace(steps=tuple(self._steps))


def _rule_id_of(node: Node) -> str | None:
    return None if node.rule is None else node.rule.id
