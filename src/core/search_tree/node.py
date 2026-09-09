from __future__ import annotations

from dataclasses import dataclass

from core.domain.state import State
from core.rules.domain.base import TransitionRule


@dataclass(frozen=True, slots=True)
class Node:
    state: State
    parent: Node | None
    rule: TransitionRule | None
    depth: int
    order: int

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def __hash__(self) -> int:
        return hash((self.order, self.state))
