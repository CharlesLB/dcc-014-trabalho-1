"""BUSCA GULOSA

Expande sempre o nó de ABERTOS com a MENOR heurística h, a estimativa de
quanto falta até o objetivo. O custo real não entra na escolha: a solução
encontrada não é garantidamente a de menor custo.

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

h = discos mal posicionados (core/heuristics/misplacement.py): por disco, 0 se
bem posicionado, 1 se em outra haste, 2 se na haste certa mas mal posicionado.

Árvore da carta P1, regras em ordem crescente. (n) é a ordem de expansão:

    #0 ([V, R], [A], [])  h=3  (1)
    ├── R1 → #1 ([V], [A, R], [])  h=4
    ├── R2 → #2 ([V], [A], [R])  h=3
    ├── R3 → #3 ([V, R, A], [], [])  h=3
    └── R4 → #4 ([V, R], [], [A])  h=2  (2)
        ├── R1 → #5 ([V], [R], [A])  h=1  (3)
        │   ├── R1 → #6 ([], [R, V], [A])  h=0  (4) objetivo
        │   ├── R3 ✗ poda: estado de #4, já em FECHADOS
        │   ├── R5 → #7 ([V, A], [R], [])  h=2
        │   └── R6 → #8 ([V], [R, A], [])  h=2
        ├── R5 ✗ poda: estado de #3, já gerado com custo menor
        └── R6 ✗ poda: estado de #0, já em FECHADOS

    Solução: R4 → R1 → R1, custo real 13 + 12 + 11 = 36

Em cada passo sai de ABERTOS o menor h: #4 (2), depois #5 (1), depois #6 (0).
#1, #2 e #3 ficam em ABERTOS sem nunca serem expandidos. No empate de h, sai o
nó gerado primeiro. A busca só encerra quando o objetivo vira o estado atual,
não quando ele é gerado.

Poda: a da busca ordenada (entre dois nós do mesmo estado, fica o de menor
custo real), mais o filho cujo estado já está em FECHADOS, que não é reaberto.
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
