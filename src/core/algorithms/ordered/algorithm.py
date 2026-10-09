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
"""

from __future__ import annotations

from typing import ClassVar

from core.algorithms.domain.base import SearchAlgorithm
from core.algorithms.ordered.frontier import PriorityFrontier
from core.domain.heuristic import misplacement
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome


class OrderedSearch(SearchAlgorithm):
    name: ClassVar[str] = "ordered"

    # Estado da execução corrente, reiniciado no começo de cada `_search`.
    _best_cost: dict[State, int]
    _open: dict[State, Node]
    _closed: set[State]

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
        parent, rule = node.parent, node.rule
        assert parent is not None and rule is not None
        self._record_prune(parent, rule.id, node.state)
