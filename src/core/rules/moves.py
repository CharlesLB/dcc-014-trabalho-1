"""Regras de transição de estado.

    R1: mover o disco do topo da H1 para a H2.
    R2: mover o disco do topo da H1 para a H3.
    R3: mover o disco do topo da H2 para a H1.
    R4: mover o disco do topo da H2 para a H3.
    R5: mover o disco do topo da H3 para a H1.
    R6: mover o disco do topo da H3 para a H2.

Toda regra tem inversa exata: R1<->R3, R2<->R5, R4<->R6.

Custo de aplicar uma regra num estado:

    custo = 10 + peso do disco movido x distância entre as hastes

    10           toda jogada custa o mesmo tanto, e esse tanto pesa mais que o
                 esforço (de 1 a 6 por jogada). Em todos os 1.260 pares início
                 -> objetivo deste espaço, o caminho mais barato é um dos mais
                 curtos: a busca ordenada não troca movimentos por esforço.
                 Sem o 10, isso falha em 3,7% das execuções.
    distância    hastes vizinhas (H1 <-> H2, H2 <-> H3): 1; H1 <-> H3, que pula
                 a do meio: 2.
    peso         VERDE 1, VERMELHO 2, AZUL 3 (`DISK_WEIGHTS`).

Entre caminhos com o mesmo número de movimentos, vence o que carrega os discos
mais pesados por menos distância. Uma regra e sua inversa custam o mesmo: movem
o mesmo disco pela mesma distância. Só a busca ordenada olha o custo.

Exemplo: em ([V, R], [A], []), R4 leva o azul de H2 para H3: 10 + 3 x 1 = 13.

`apply` exige `is_applicable` como pré-condição: aplicar regra inválida é erro de
programação e falha alto.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from core.rules.domain.base import DISK_WEIGHTS, Peg, State
from core.rules.domain.constraints import is_move_allowed
from core.rules.domain.exceptions import RuleNotApplicableError

MOVE_COST: Final = 10


@dataclass(frozen=True, slots=True)
class Move:
    id: str
    origin: Peg
    destination: Peg

    @property
    def distance(self) -> int:
        return abs(self.destination - self.origin)

    def cost(self, state: State) -> int:
        if not self.is_applicable(state):
            raise RuleNotApplicableError(self.id)
        disk = state[self.origin][-1]
        return MOVE_COST + DISK_WEIGHTS[disk] * self.distance

    def is_applicable(self, state: State) -> bool:
        return is_move_allowed(state, self.origin, self.destination)

    def apply(self, state: State) -> State:
        if not self.is_applicable(state):
            raise RuleNotApplicableError(self.id)

        stacks = list(state)
        disk = stacks[self.origin][-1]
        stacks[self.origin] = stacks[self.origin][:-1]
        stacks[self.destination] = (*stacks[self.destination], disk)
        return (stacks[0], stacks[1], stacks[2])


R1 = Move("R1", Peg.H1, Peg.H2)
R2 = Move("R2", Peg.H1, Peg.H3)
R3 = Move("R3", Peg.H2, Peg.H1)
R4 = Move("R4", Peg.H2, Peg.H3)
R5 = Move("R5", Peg.H3, Peg.H1)
R6 = Move("R6", Peg.H3, Peg.H2)
