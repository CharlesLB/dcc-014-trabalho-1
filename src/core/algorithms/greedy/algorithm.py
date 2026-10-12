"""BUSCA GULOSA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Heurística (core/heuristics/)

    Uma estimativa de quanto falta do estado até o objetivo, dada pela
    heurística escolhida.

    Padrão, discos mal posicionados (core/heuristics/misplacement.py): 0 por
    disco bem posicionado, 1 em outra haste, 2 na haste certa mas mal
    posicionado. h(estado) = soma dos três discos. Em S0: h = 1 + 1 + 1 = 3.

    Alternativa, cor e distância (core/heuristics/color_distance.py): peso da
    cor x hastes até a do objetivo, somado nos três discos.

3. Critério

    O laço e as duas listas da busca ordenada, mas ABERTOS é ordenada pela
    MENOR heurística, não pelo custo real: a busca expande sempre o nó que
    parece mais perto do objetivo. No empate, sai o nó gerado primeiro; entre
    irmãos de mesma heurística, decide a estratégia. A busca só encerra
    quando o objetivo vira o estado atual, não quando ele é gerado.

    O custo real não entra na escolha. Ele é somado nas arestas do caminho
    solução, da raiz até o objetivo, e dá o custo da solução, que por isso
    não é garantidamente o menor.

    Como na ordenada, um nó nunca gera um estado do seu próprio caminho.

4. Técnica de poda

    A da busca ordenada, com o vetor de menor custo: entre dois nós do mesmo
    estado, fica o de menor custo real. Como aqui a fila não sai por custo,
    um estado já expandido pode reaparecer mais barato; ele não é reaberto:
    o filho cujo estado está em FECHADOS também é podado.
"""

from __future__ import annotations

from typing import ClassVar

from core.algorithms.ordered.algorithm import OrderedSearch
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.search_tree.node import Node


class GreedySearch(OrderedSearch):
    name: ClassVar[str] = "greedy"

    def _priority(self, node: Node, problem: Problem) -> int:
        """A heurística do nó: só ela ordena ABERTOS."""
        return self._heuristic.estimate(node.state, problem.goal)

    def _is_repetition(
        self, node: Node, rule: TransitionRule, successor: State
    ) -> bool:
        """A poda da ordenada, mais o filho de estado já fechado."""
        return successor in self._closed or super()._is_repetition(
            node, rule, successor
        )
