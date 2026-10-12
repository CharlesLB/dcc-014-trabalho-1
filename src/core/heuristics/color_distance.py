"""Heurística de cor e distância.

Cada disco fora da haste do objetivo contribui com o peso da sua cor vezes a
distância, em hastes, até a haste em que ele deve ficar:

    peso        verde 1, vermelho 2, azul 3
    distância   1 entre hastes vizinhas, 2 de H1 para H3 (ou de H3 para H1)

    h(estado) = soma de peso x distância dos três discos

O disco que já está na haste do objetivo contribui com 0, mesmo fora da altura
certa: esta heurística só olha a haste, não a ordem dentro dela. Por isso h pode
ser 0 num estado que ainda não é o objetivo.

Exemplo, objetivo ([], [R, V], [A]):
    ([V, R], [A], [])   V: 1 x 1; R: 2 x 1; A: 3 x 1             h = 6
    ([V, R], [], [A])   V: 1 x 1; R: 2 x 1; A na H3: 0           h = 3
    ([], [V, R], [A])   V e R na H2, trocados: 0 + 0; A: 0       h = 0

Não é admissível: um disco pesado a duas hastes do destino soma 6, mas chega lá
com um movimento só.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.costs.weight_distance import WEIGHTS
from core.domain.state import Disk, Peg, State


def color_distance(state: State, goal: State) -> int:
    return sum(contributions(state, goal).values())


def contributions(state: State, goal: State) -> dict[Disk, int]:
    """O que cada disco soma em h: peso da cor x hastes até a do objetivo."""
    target = _peg_of_each_disk(goal)
    return {
        disk: WEIGHTS[disk] * abs(peg - target[disk])
        for disk, peg in _peg_of_each_disk(state).items()
    }


def _peg_of_each_disk(state: State) -> dict[Disk, Peg]:
    return {disk: peg for peg in Peg for disk in state[peg]}


@dataclass(frozen=True, slots=True)
class ColorDistance:
    name: str = "color_distance"

    def estimate(self, state: State, goal: State) -> int:
        return color_distance(state, goal)


COLOR_DISTANCE = ColorDistance()
