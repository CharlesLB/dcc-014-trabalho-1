from __future__ import annotations

from typing import Protocol

from core.domain.state import State


class Heuristic(Protocol):
    """Uma estimativa de quanto falta do estado até o objetivo.

    A busca ordenada e a gulosa só conhecem este contrato: trocar a heurística
    é trocar a implementação, não o algoritmo. As implementações ficam em
    `core/heuristics/`, uma por módulo, e são escolhidas pelo nome no registro.
    """

    @property
    def name(self) -> str: ...

    def estimate(self, state: State, goal: State) -> int: ...
