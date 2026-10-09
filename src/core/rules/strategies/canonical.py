"""Estratégias de controle pela ordem canônica das regras (R1 a R6).

ascending   R1 → R2 → R3 → R4 → R5 → R6
descending  R6 → R5 → R4 → R3 → R2 → R1
"""

from __future__ import annotations

from dataclasses import dataclass

from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULES

_CANONICAL_POSITION = {rule.id: position for position, rule in enumerate(RULES)}


@dataclass(frozen=True, slots=True)
class CanonicalOrder:
    name: str
    reverse: bool = False

    def order(self, rules: tuple[TransitionRule, ...]) -> tuple[TransitionRule, ...]:
        return tuple(
            sorted(
                rules,
                key=lambda rule: _CANONICAL_POSITION[rule.id],
                reverse=self.reverse,
            )
        )


ASCENDING = CanonicalOrder("ascending")
DESCENDING = CanonicalOrder("descending", reverse=True)
