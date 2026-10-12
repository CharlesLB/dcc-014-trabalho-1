"""Custo de peso e distância: o peso do disco movido vezes a distância.

    peso        verde 1, vermelho 2, azul 3
    distância   1 entre hastes vizinhas, 2 de H1 para H3 (ou de H3 para H1)

    custo(regra, estado) = peso do disco no topo da origem x distância

Exemplo, em ([V, R], [A], []):
    R1  vermelho de H1 para H2   2 x 1 = 2
    R2  vermelho de H1 para H3   2 x 2 = 4
    R4  azul de H2 para H3       3 x 1 = 3

Mover um disco pesado para longe é o que custa mais: o caminho mais barato
pode ter mais movimentos que o mais curto.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from core.domain.state import Disk, State
from core.rules.domain.base import TransitionRule

WEIGHTS: Mapping[Disk, int] = MappingProxyType(
    {Disk.GREEN: 1, Disk.RED: 2, Disk.BLUE: 3}
)


@dataclass(frozen=True, slots=True)
class WeightDistance:
    name: str = "weight_distance"

    def cost(self, rule: TransitionRule, state: State) -> int:
        disk = state[rule.origin][-1]
        return WEIGHTS[disk] * abs(rule.destination - rule.origin)


WEIGHT_DISTANCE = WeightDistance()
