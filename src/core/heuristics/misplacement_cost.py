"""Heurística do custo dos discos mal posicionados.

A contagem de core/heuristics/misplacement.py convertida em custo real. Cada
movimento que um disco ainda precisa fazer custa, no mínimo, uma jogada de uma
haste só com aquele disco (core/costs/step_weight_distance.py):

    verde 10 + 1 x 1 = 11    vermelho 10 + 2 x 1 = 12    azul 10 + 3 x 1 = 13

    h(estado) = soma, por disco, de movimentos que faltam x (10 + peso)

Exemplo, objetivo ([], [R, V], [A]):
    ([V, R], [A], [])   V: 1 x 11; R: 1 x 12; A: 1 x 13           h = 36
    ([V, R], [], [A])   V: 1 x 11; R: 1 x 12; A bem posicionado   h = 23
    ([V], [R], [A])     V: 1 x 11; R e A bem posicionados         h = 11
    ([], [V, R], [A])   V e R na H2, trocados: 2 x 11 + 2 x 12    h = 46

Em ([V, R], [A], []) h vale 36, exatamente o custo da solução ótima de P1.

Admissível com o custo padrão: nenhum disco faz menos movimentos que os
contados, e nenhum movimento dele custa menos que 10 + peso. Consistente: uma
jogada só muda a contribuição do disco movido, em no máximo um movimento, e
custa pelo menos o que ela cai.

Fica na unidade do custo real g, e por isso é a heurística padrão da busca A*:
f = g + h soma custo com custo. Com --cost unit ou weight_distance, que cobram
menos que 10 + peso por jogada, ela superestima o que falta e a A* perde a
garantia do menor custo.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.costs.step_weight_distance import STEP_COST
from core.costs.weight_distance import WEIGHTS
from core.domain.state import Disk, State
from core.heuristics.misplacement import contributions as moves_left


def misplacement_cost(state: State, goal: State) -> int:
    return sum(contributions(state, goal).values())


def contributions(state: State, goal: State) -> dict[Disk, int]:
    """O que cada disco soma em h: movimentos que faltam x a jogada mais barata."""
    return {
        disk: moves * cheapest_move(disk)
        for disk, moves in moves_left(state, goal).items()
    }


def cheapest_move(disk: Disk) -> int:
    """A jogada mais barata do disco: uma haste só, 10 + peso x 1."""
    return STEP_COST + WEIGHTS[disk]


@dataclass(frozen=True, slots=True)
class MisplacedDisksCost:
    name: str = "misplacement_cost"

    def estimate(self, state: State, goal: State) -> int:
        return misplacement_cost(state, goal)


MISPLACEMENT_COST = MisplacedDisksCost()
