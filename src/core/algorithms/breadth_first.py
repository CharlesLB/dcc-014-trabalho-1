"""BUSCA EM LARGURA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Critério

    As regras são analisadas na ordem crescente R1 → R2 → R3 → R4 → R5 → R6.
    Em vez de escolher uma, a busca aplica todas as válidas e coloca os
    filhos no fim de ABERTOS. O estado visitado vai para FECHADOS. Uma
    regra cujo resultado já está em ABERTOS ou FECHADOS é descartada (poda).

3. Execução

    Nível 0
        ABERTOS = [S0]               FECHADOS = []

    Expansão de S0 = ([V, R], [A], [])
        R1 → S1 = ([V], [A, R], [])
        R2 → S2 = ([V], [A], [R])
        R3 → S3 = ([V, R, A], [], [])
        R4 → S4 = ([V, R], [], [A])
        R5, R6: inválidas, H3 vazia
        ABERTOS = [S1, S2, S3, S4]   FECHADOS = [S0]

    Nível 1

    Expansão de S1 = ([V], [A, R], [])
        R1: inválida, H2 cheia
        R2 → S5 = ([], [A, R], [V])
        R3 → S0: poda
        R4 → S2: poda
        ABERTOS = [S2, S3, S4, S5]   FECHADOS = [S0, S1]

    Expansão de S2 = ([V], [A], [R])
        R1 → S6 = ([], [A, V], [R])
        R3 → S7 = ([V, A], [], [R])
        R5 → S0, R6 → S1: poda
        ABERTOS = [S3, S4, S5, S6, S7]

    Expansão de S3 = ([V, R, A], [], [])
        R1 → S0, R2 → S4: poda.  Nada novo.

    Expansão de S4 = ([V, R], [], [A])
        R1 → S8 = ([V], [R], [A])
        R5 → S3, R6 → S0: poda
        ABERTOS = [S5, S6, S7, S8]   FECHADOS = [S0, S1, S2, S3, S4]

    Nível 2
        S5 gera S9.  S6 gera S10.  S7 gera S11 e S12.
        S8 = ([V], [R], [A]) gera:
            R1 → S13 = ([], [R, V], [A])   ← é Sf, entra na fila
            R6 → S14 = ([V], [R, A], [])
        ABERTOS = [S9, S10, S11, S12, S13, S14]

    Nível 3
        S9 gera S15 e S16.  S10, S11 e S12 só geram repetidos.
        Chega a vez de S13 = ([], [R, V], [A])
        ✓ SUCESSO

4. Árvore de busca

    S0 ([V,R], [A], [])
    ├── R1 → S1 ([V], [A,R], [])
    │   └── R2 → S5 ([], [A,R], [V])
    │       └── R3 → S9 ([R], [A], [V])
    │           ├── R3 → S15
    │           └── R5 → S16
    ├── R2 → S2 ([V], [A], [R])
    │   ├── R1 → S6 ([], [A,V], [R])
    │   │   └── R5 → S10
    │   └── R3 → S7 ([V,A], [], [R])
    │       ├── R5 → S11
    │       └── R6 → S12
    ├── R3 → S3 ([V,R,A], [], [])
    └── R4 → S4 ([V,R], [], [A])
        └── R1 → S8 ([V], [R], [A])
            ├── R1 → S13 ([], [R,V], [A])   (objetivo)
            └── R6 → S14 ([V], [R,A], [])

5. Caminho solução

    S0 ([V,R], [A], [])
     │ R4: azul H2 → H3
     ↓
    S4 ([V,R], [], [A])
     │ R1: vermelho H1 → H2
     ↓
    S8 ([V], [R], [A])
     │ R1: verde H1 → H2
     ↓
    Sf ([], [R,V], [A])

    Número de movimentos: 3      Iterações: 14      Gerados: 17

6. Conclusão

    Nada de profundidade d+1 é visitado antes de esgotar a profundidade d,
    então o primeiro caminho até um estado é o mais curto até ele. O objetivo
    encontrado é o ótimo, e por isso este método serve de referência para os
    outros dois. A estratégia só muda a ordem dentro de um nível.

    A poda aqui é global: um estado descoberto por qualquer ramo nunca é
    gerado de novo. Os outros dois métodos só evitam repetir dentro do
    próprio caminho.
"""

from __future__ import annotations

from typing import ClassVar

from config import settings
from core.algorithms.domain.base import SearchAlgorithm
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.strategies.domain.base import ControlStrategy
from core.search_tree.frontier import QueueFrontier
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome
from core.search_tree.tree import SearchTree


class BreadthFirstSearch(SearchAlgorithm):
    name: ClassVar[str] = "breadth_first"

    def __init__(
        self,
        tree: SearchTree,
        strategy: ControlStrategy,
        *,
        max_iterations: int = settings.MAX_ITERATIONS,
    ) -> None:
        super().__init__(tree, strategy, max_iterations=max_iterations)
        self._closed: set[State] = set()
        self._open_states: set[State] = set()

    def _search(self, problem: Problem) -> Outcome:
        context = self._require_context()
        frontier = QueueFrontier()
        frontier.push(context.root)

        self._closed = set()
        self._open_states = {context.root.state}

        while len(frontier):
            if not self._next_iteration():
                return Outcome.CUTOFF

            node = frontier.pop()
            self._open_states.discard(node.state)
            if problem.is_goal(node.state):
                return self._succeed(node)

            self._closed.add(node.state)
            self._visit(node)
            for rule in self._applicable_rules(node):
                child = self._expand(node, rule)
                self._open_states.add(child.state)
                frontier.push(child)

        return self._exhausted()

    def _is_repetition(self, node: Node, successor: State) -> bool:
        return successor in self._closed or successor in self._open_states
