"""Condições de validade.

    1. Origem: a haste de origem possui pelo menos um disco no momento exato da
       ação.
    2. Destino: a haste de destino não ultrapassa sua capacidade estrita de
       volume (H1 até 3, H2 até 2, H3 até 1).

As duas são estáticas: dependem apenas do estado corrente.

A terceira condição do material, que proíbe produzir estado já presente no
caminho, é contextual: depende do percurso, e por isso vive no algoritmo
(`core/search_tree/path.py`), não aqui.
"""

from __future__ import annotations

from core.rules.domain.base import CAPACITIES, Peg, State


def has_disk_to_move(state: State, origin: Peg) -> bool:
    return len(state[origin]) >= 1


def has_room_for_disk(state: State, destination: Peg) -> bool:
    return len(state[destination]) + 1 <= CAPACITIES[destination]


def is_move_allowed(state: State, origin: Peg, destination: Peg) -> bool:
    return has_disk_to_move(state, origin) and has_room_for_disk(state, destination)
