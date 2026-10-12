"""Custo de jogada, peso e distância: 10 por jogada, mais peso x distância.

    por jogada  10
    peso        verde 1, vermelho 2, azul 3
    distância   1 entre hastes vizinhas, 2 de H1 para H3 (ou de H3 para H1)

    custo(regra, estado) = 10 + peso do disco no topo da origem x distância

Exemplo, em ([V, R], [A], []):
    R1  vermelho de H1 para H2   10 + 2 x 1 = 12
    R2  vermelho de H1 para H3   10 + 2 x 2 = 14
    R4  azul de H2 para H3       10 + 3 x 1 = 13

O peso x distância vai de 1 a 6, sempre menos que os 10 da jogada: um caminho
com um movimento a mais nunca sai mais barato. O caminho de menor custo é
sempre um dos de menos movimentos, e o peso x distância só desempata entre
eles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from core.costs.weight_distance import WEIGHT_DISTANCE
from core.domain.state import State
from core.rules.domain.base import TransitionRule

STEP_COST: Final = 10


@dataclass(frozen=True, slots=True)
class StepWeightDistance:
    name: str = "step_weight_distance"

    def cost(self, rule: TransitionRule, state: State) -> int:
        return STEP_COST + WEIGHT_DISTANCE.cost(rule, state)


STEP_WEIGHT_DISTANCE = StepWeightDistance()
