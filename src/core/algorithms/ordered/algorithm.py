"""BUSCA ORDENADA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Heurística (core/domain/heuristic.py)

    Cada disco contribui com o mínimo de movimentos que ainda precisa fazer:

        0   bem posicionado: haste e altura certas, e tudo abaixo dele também
        1   em outra haste
        2   na haste certa, mas mal posicionado: precisa sair e voltar

    h(estado) = soma dos três discos. Em S0: V e R em H1, A em H2, todos em
    haste errada: h = 1 + 1 + 1 = 3.

    Toda jogada custa 1, então o custo de um nó é a sua profundidade. O custo
    não ordena a fila: só decide qual de dois nós do mesmo estado fica.

3. Critério

    ABERTOS é ordenada pela MENOR heurística. No empate, sai o nó gerado
    primeiro; entre irmãos de mesma heurística, decide a estratégia (aqui, a
    ordem crescente R1 → R2 → R3 → R4 → R5 → R6). A busca só encerra quando
    o objetivo vira o estado atual, não quando ele é gerado.

    Poda: o filho cujo estado já foi expandido (FECHADOS) é descartado; o
    filho cujo estado já está em ABERTOS por um caminho de mesmo tamanho ou
    menor também. Se o novo caminho for mais curto, o nó antigo sai de
    ABERTOS e da árvore e o novo entra no lugar.

4. Execução (h entre parênteses)

    Expansão de S0 = ([V, R], [A], []), h 3
        R1 → S1 = ([V], [A, R], [])      4
        R2 → S2 = ([V], [A], [R])        3
        R3 → S3 = ([V, R, A], [], [])    3
        R4 → S4 = ([V, R], [], [A])      2
        ABERTOS  = [S4(2), S2(3), S3(3), S1(4)]
        FECHADOS = [S0]

    Expansão de S4 = ([V, R], [], [A]), h 2
        R5 → estado de S3, R6 → S0: poda
        R1 → S5 = ([V], [R], [A])        1
        ABERTOS  = [S5(1), S2(3), S3(3), S1(4)]

    Expansão de S5 = ([V], [R], [A]), h 1
        R3 → S4: poda
        R1 → S6 = ([], [R, V], [A])      0   ← é Sf, mas só entra na fila
        R5 → S7 = ([V, A], [R], [])      2
        R6 → S8 = ([V], [R, A], [])      2
        ABERTOS  = [S6(0), S7(2), S8(2), S2(3), S3(3), S1(4)]

    Chega a vez de S6 = ([], [R, V], [A])
        ✓ SUCESSO

5. Árvore de busca (heurística entre parênteses)

    S0 ([V,R], [A], [])  (3)
    ├── R1 → S1 ([V], [A,R], [])  (4)
    ├── R2 → S2 ([V], [A], [R])  (3)
    ├── R3 → S3 ([V,R,A], [], [])  (3)
    └── R4 → S4 ([V,R], [], [A])  (2)
        └── R1 → S5 ([V], [R], [A])  (1)
            ├── R1 → S6 ([], [R,V], [A])  (0)   (objetivo)
            ├── R5 → S7 ([V,A], [R], [])  (2)
            └── R6 → S8 ([V], [R,A], [])  (2)

6. Caminho solução

    S0 ([V,R], [A], [])   h 3
     │ R4: azul H2 → H3
     ↓
    S4 ([V,R], [], [A])   h 2
     │ R1: vermelho H1 → H2
     ↓
    S5 ([V], [R], [A])    h 1
     │ R1: verde H1 → H2
     ↓
    Sf ([], [R,V], [A])   h 0

    Número de movimentos: 3      Iterações: 4      Gerados: 9

    Com a ordem decrescente: o mesmo caminho, também em 4 iterações. A
    estratégia só muda a ordem dos irmãos empatados.

7. Conclusão

    A heurística leva direto ao objetivo em P1: 4 iterações, contra 12 a 14
    da busca em largura. Ordenar só por h não garante o caminho mais curto:
    nos 36 objetivos, a ordenada acha o mínimo de movimentos em 34 com a
    ordem crescente e em 33 com a decrescente. Como FECHADOS impede repetir
    estado e o espaço é conexo, ela sempre encontra uma solução.
"""

from __future__ import annotations

from typing import ClassVar

from config import settings
from core.algorithms.domain.base import SearchAlgorithm
from core.algorithms.ordered.frontier import PriorityFrontier
from core.domain.heuristic import misplacement
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.rules.strategies.domain.base import ControlStrategy
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome
from core.search_tree.tree import SearchTree


class OrderedSearch(SearchAlgorithm):
    name: ClassVar[str] = "ordered"

    def __init__(
        self,
        tree: SearchTree,
        strategy: ControlStrategy,
        *,
        max_iterations: int = settings.MAX_ITERATIONS,
        prune: bool = True,
    ) -> None:
        super().__init__(tree, strategy, max_iterations=max_iterations, prune=prune)
        self._best_cost: dict[State, int] = {}
        self._open: dict[State, Node] = {}
        self._closed: set[State] = set()

    def _search(self, problem: Problem) -> Outcome:
        """Sempre expande o nó aberto de menor heurística.

        O objetivo só encerra a busca quando vira o estado atual, não quando
        é gerado, como em toda busca com fila ordenada.
        """
        context = self._require_context()
        frontier = PriorityFrontier(lambda node: misplacement(node.state, problem.goal))
        frontier.push(context.root)

        # Vetor de menor custo: o caminho mais curto já gerado até cada
        # estado. Decide qual de dois nós do mesmo estado fica em ABERTOS.
        self._best_cost = {context.root.state: 0}
        # O nó de cada estado que ainda espera em ABERTOS, para poder tirá-lo
        # de lá quando um caminho mais curto até o mesmo estado aparecer.
        self._open = {context.root.state: context.root}
        # FECHADOS: a fila não sai por custo, então um estado expandido ainda
        # pode reaparecer mais barato. Ele não é reaberto: é podado.
        self._closed = set()
        self._observe_frontier(len(frontier))

        while len(frontier):
            if not self._next_iteration():
                return Outcome.CUTOFF

            node = frontier.pop()
            if self._open.get(node.state) is node:
                del self._open[node.state]
            if problem.is_goal(node.state):
                return self._succeed(node)

            self._closed.add(node.state)
            self._visit(node)
            candidates = self._applicable_rules(node)
            if not candidates:
                self._deadlock(node)

            for rule in candidates:
                child = self._expand(node, rule)
                older = self._open.get(child.state) if self.prune else None
                if older is not None:
                    # Chegou mais curto a um estado que ainda está aberto:
                    # o nó antigo sai de ABERTOS e da árvore.
                    frontier.remove(older)
                    self._discard(older)
                self._best_cost[child.state] = child.cost
                self._open[child.state] = child
                frontier.push(child)
            self._observe_frontier(len(frontier))

        return self._exhausted()

    def _is_repetition(
        self, node: Node, rule: TransitionRule, successor: State
    ) -> bool:
        """Poda o filho já fechado ou que não encurta o caminho conhecido."""
        if successor in self._closed:
            return True
        best = self._best_cost.get(successor)
        return best is not None and node.cost + rule.cost(node.state) >= best

    def _discard(self, node: Node) -> None:
        """Só contabilidade: registra o nó substituído como poda do pai."""
        context = self._require_context()
        parent, rule = node.parent, node.rule
        assert parent is not None and rule is not None
        context.trace.record_prune(
            iteration=context.metrics.iterations,
            node=parent,
            rule_id=rule.id,
            state=node.state,
        )
