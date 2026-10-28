"""BUSCA A*

Expande sempre o nó de ABERTOS com a MENOR função de avaliação

    f(n) = g(n) + h(n)

g(n) é o custo real do caminho da raiz até n, o que ordena a busca ordenada.
h(n) é a heurística, o custo estimado de n até o objetivo, o que ordena a
gulosa. f(n) estima o custo da solução mais barata que passa por n.

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

g = 10 por jogada + peso do disco x distância (core/costs/step_weight_distance.py).
h = custo dos discos mal posicionados (core/heuristics/misplacement_cost.py):
movimentos que faltam a cada disco x a jogada mais barata dele, 10 + peso. As
duas na mesma unidade, custo real.

Árvore da carta P1, regras em ordem crescente. (n) é a ordem de expansão:

    #0 ([V, R], [A], [])  g=0  h=36  f=36  (1)
    ├── R1 → #1 ([V], [A, R], [])  g=12  h=48  f=60
    ├── R2 → #2 ([V], [A], [R])  g=14  h=36  f=50
    ├── R3 → #3 ([V, R, A], [], [])  g=13  h=36  f=49
    └── R4 → #4 ([V, R], [], [A])  g=13  h=23  f=36  (2)
        ├── R1 → #5 ([V], [R], [A])  g=25  h=11  f=36  (3)
        │   ├── R1 → #6 ([], [R, V], [A])  g=36  h=0  f=36  (4) objetivo
        │   ├── R3 ✗ poda: estado de #4, já gerado com custo menor
        │   ├── R5 → #7 ([V, A], [R], [])  g=41  h=24  f=65
        │   └── R6 → #8 ([V], [R, A], [])  g=38  h=24  f=62
        ├── R5 ✗ poda: estado de #3, já gerado com custo menor
        └── R6 ✗ poda: estado de #0, já gerado com custo menor

    Solução: R4 → R1 → R1, custo real 13 + 12 + 11 = 36

Em S0 h vale 36, exatamente o custo da solução: ao longo do caminho f não sai
de 36, e todo nó fora dele tem f maior. #1, #2 e #3 ficam em ABERTOS sem nunca
serem expandidos. No empate de f, sai o nó gerado primeiro. A busca só encerra
quando o objetivo vira o estado atual, não quando ele é gerado.

Com h admissível (nunca passa do custo que falta), o primeiro objetivo a sair
de ABERTOS é o de menor custo real, como na ordenada. Com h consistente, um
estado já expandido nunca reaparece mais barato.

Poda: a da busca ordenada, com o vetor de menor custo. Entre dois nós do mesmo
estado h é a mesma, então fica o de menor g. Um estado fechado só voltaria a
ABERTOS por um caminho mais barato, o que não acontece com h consistente.
"""

from __future__ import annotations

from typing import ClassVar

from core.algorithms.ordered.algorithm import OrderedSearch
from core.domain.problem import Problem
from core.heuristics.domain.base import Heuristic
from core.heuristics.misplacement_cost import MISPLACEMENT_COST
from core.search_tree.node import Node


class AStarSearch(OrderedSearch):
    name: ClassVar[str] = "astar"
    default_heuristic: ClassVar[Heuristic] = MISPLACEMENT_COST

    def _priority(self, node: Node, problem: Problem) -> int:
        """A função de avaliação: f = g + h, custo real mais heurística."""
        return node.cost + self._heuristic.estimate(node.state, problem.goal)
