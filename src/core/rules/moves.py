"""Regras de transição de estado.

    R1: mover o disco do topo da H1 para a H2.
    R2: mover o disco do topo da H1 para a H3.
    R3: mover o disco do topo da H2 para a H1.
    R4: mover o disco do topo da H2 para a H3.
    R5: mover o disco do topo da H3 para a H1.
    R6: mover o disco do topo da H3 para a H2.

Toda regra tem inversa exata: R1<->R3, R2<->R5, R4<->R6.

`apply` exige `is_applicable` como pré-condição: aplicar regra inválida é erro de
programação e falha alto.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.rules.domain.base import Peg, State
from core.rules.domain.constraints import is_move_allowed
from core.rules.domain.exceptions import RuleNotApplicableError


@dataclass(frozen=True, slots=True)
class Move:
    id: str
    origin: Peg
    destination: Peg

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
