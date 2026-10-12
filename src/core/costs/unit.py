"""Custo unitário: toda jogada custa 1.

O custo de um caminho é o número de movimentos.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.domain.state import State
from core.rules.domain.base import TransitionRule


@dataclass(frozen=True, slots=True)
class UnitCost:
    name: str = "unit"

    def cost(self, rule: TransitionRule, state: State) -> int:
        return 1


UNIT = UnitCost()
