from __future__ import annotations

from typing import Protocol

from core.domain.state import State
from core.rules.domain.base import TransitionRule


class CostFunction(Protocol):
    """O custo real de uma jogada: quanto custa aplicar a regra no estado.

    O custo de um nó é a soma dos custos das jogadas da raiz até ele, e o
    custo da solução é o custo do nó objetivo. A busca ordenada escolhe o nó
    por esse custo acumulado, e a A* por ele somado à heurística; as outras só
    o informam. As implementações ficam em `core/costs/`, uma por módulo, e são
    escolhidas pelo nome no registro.
    """

    @property
    def name(self) -> str: ...

    def cost(self, rule: TransitionRule, state: State) -> int: ...
