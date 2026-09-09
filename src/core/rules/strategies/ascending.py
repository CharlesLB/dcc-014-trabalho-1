from __future__ import annotations

from dataclasses import dataclass

from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULES

_CANONICAL_POSITION = {rule.id: position for position, rule in enumerate(RULES)}


@dataclass(frozen=True, slots=True)
class AscendingStrategy:
    name: str = "ascending"

    def order(self, rules: tuple[TransitionRule, ...]) -> tuple[TransitionRule, ...]:
        return tuple(sorted(rules, key=lambda rule: _CANONICAL_POSITION[rule.id]))


ASCENDING = AscendingStrategy()
