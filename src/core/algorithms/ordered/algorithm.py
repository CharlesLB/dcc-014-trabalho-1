"""BUSCA ORDENADA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Custo real (core/costs/)

    Cada jogada tem um custo real, dado pela função de custo escolhida. O
    custo de um nó é a soma dos custos das jogadas da raiz até ele.

    Padrão, jogada, peso e distância (core/costs/step_weight_distance.py):
    10 por jogada, mais o peso do disco movido (verde 1, vermelho 2, azul 3)
    x distância em hastes. Em S0, R4 leva o azul de H2 para H3:
    10 + 3 x 1 = 13. Com ela, o caminho de menor custo é sempre um dos de
    menos movimentos.

    Alternativas: só peso x distância (core/costs/weight_distance.py) e
    unitário, 1 por jogada (core/costs/unit.py).

3. Critério

    ABERTOS é ordenada pelo MENOR custo real acumulado. No empate, sai o nó
    gerado primeiro; entre irmãos de mesmo custo, decide a estratégia (aqui,
    a ordem crescente R1 → R2 → R3 → R4 → R5 → R6). A busca só encerra quando
    o objetivo vira o estado atual, não quando ele é gerado: por isso a
    solução encontrada é a de menor custo.

    Um nó nunca gera um estado que já está no seu próprio caminho, da raiz
    até ele. Fora isso, sem a técnica de poda, estados repetidos entram de
    novo em ABERTOS e em FECHADOS.

    Um nó em impasse, sem filhos, vai para FECHADOS e a busca segue com o
    próximo de ABERTOS.

4. Técnica de poda

    O vetor de menor custo guarda, para cada estado já gerado, o menor custo
    com que ele apareceu. Toda vez que um nó é gerado:

        primeira vez do estado    entra no vetor com o seu custo
        repetido, custo >=        o nó novo é podado
        repetido, custo <         o vetor é atualizado, o nó antigo sai da
                                  árvore e de ABERTOS e o novo entra
"""

from __future__ import annotations

from typing import ClassVar

from core.algorithms.domain.base import SearchAlgorithm
from core.algorithms.ordered.frontier import PriorityFrontier
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.search_tree import path
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome


class OrderedSearch(SearchAlgorithm):
    name: ClassVar[str] = "ordered"

    # Estado da execução corrente, reiniciado no começo de cada `_search`.
    _best_cost: dict[State, int]
    _open: dict[State, Node]
    _closed: set[State]

    def _search(self, problem: Problem) -> Outcome:
        """Sempre expande o nó aberto de menor prioridade.

        O objetivo só encerra a busca quando vira o estado atual, não quando
        é gerado, como em toda busca com fila ordenada.
        """
        context = self._require_context()
        frontier = PriorityFrontier(lambda node: self._priority(node, problem))
        frontier.push(context.root)

        # Vetor de menor custo: o caminho mais barato já gerado até cada
        # estado. Decide qual de dois nós do mesmo estado fica em ABERTOS.
        self._best_cost = {context.root.state: 0}
        # O nó de cada estado que ainda espera em ABERTOS, para poder tirá-lo
        # de lá quando um caminho mais barato até o mesmo estado aparecer.
        self._open = {context.root.state: context.root}
        # FECHADOS: os estados já expandidos.
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
                    # Chegou mais barato a um estado que ainda está aberto:
                    # o nó antigo sai de ABERTOS e da árvore.
                    frontier.remove(older)
                    self._discard(older)
                self._best_cost[child.state] = child.cost
                self._open[child.state] = child
                frontier.push(child)
            self._observe_frontier(len(frontier))

        return self._exhausted()

    def _priority(self, node: Node, problem: Problem) -> int:
        """O que ordena ABERTOS: aqui, o custo real acumulado até o nó.

        A gulosa sobrescreve para ordenar pela heurística, e a A* pela soma do
        custo com a heurística.
        """
        return node.cost

    def _is_repetition(
        self, node: Node, rule: TransitionRule, successor: State
    ) -> bool:
        """A técnica de poda: o filho que não barateia o custo do vetor.

        Um estado já expandido saiu de ABERTOS pelo menor custo, então nenhum
        caminho novo até ele é mais barato: o vetor sozinho já o barra.
        """
        best = self._best_cost.get(successor)
        return (
            best is not None
            and node.cost + self._tree.step_cost(rule, node.state) >= best
        )

    def _is_never_generated(self, node: Node, successor: State) -> bool:
        """Um nó não gera um estado do seu próprio caminho, com ou sem poda."""
        return path.contains_state(node, successor)

    def _discard(self, node: Node) -> None:
        """Só contabilidade: registra o nó substituído como poda do pai."""
        parent, rule = node.parent, node.rule
        assert parent is not None and rule is not None
        self._record_prune(parent, rule.id, node.state)
