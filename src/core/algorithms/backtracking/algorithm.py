"""BUSCA COM BACKTRACKING

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Critério

    A mesma descida da busca irrevogável, mas as regras válidas de cada
    estado ficam guardadas numa pilha. Quando um estado não tem mais regra,
    ele sai da pilha (retrocesso) e o estado anterior tenta a próxima regra
    que tinha guardado. Uma regra que leva a um estado já no caminho atual
    é descartada (poda).
"""

from __future__ import annotations

from collections import deque
from typing import ClassVar

from core.algorithms.backtracking.frontier import StackFrontier
from core.algorithms.domain.base import SearchAlgorithm
from core.domain.problem import Problem
from core.rules.domain.base import TransitionRule
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome


class BacktrackingSearch(SearchAlgorithm):
    name: ClassVar[str] = "backtracking"

    def _search(self, problem: Problem) -> Outcome:
        """Desce enquanto houver regra; sem regra, retrocede.

        Cada iteração olha a ponta do caminho e faz uma coisa OU a outra:
        desce, e o nó continua no caminho com um filho por cima; ou retrocede,
        e o nó sai do caminho, deixando o pai como ponta.

        Sempre encontra solução, se existir — mas é a primeira que aparecer,
        não a mais curta.
        """
        context = self._require_context()

        path = StackFrontier()
        path.push(context.root)
        self._observe_frontier(len(path))

        # Para cada nó do caminho, as regras que ele ainda não tentou. Sem
        # isso não há retrocesso: o nó não saberia por onde continuar.
        untried: dict[int, deque[TransitionRule]] = {}

        while len(path):
            if not self._next_iteration():
                return Outcome.CUTOFF

            # Topo da pilha = ponta do caminho. Ele só volta para a pilha se
            # ainda tiver regra -- ver o if lá embaixo.
            node = path.pop()

            if problem.is_goal(node.state):
                return self._succeed(node)

            remaining = self._remaining_rules(node, untried)
            if remaining:
                # DESCE: o nó continua no caminho e o filho entra por cima.
                path.push(node)
                path.push(self._expand(node, remaining.popleft()))
                self._observe_frontier(len(path))
            else:
                # RETROCEDE: sem regras, o nó não volta e sai do caminho. Na
                # próxima iteração o topo é o pai, que tenta a regra seguinte.
                self._backtrack(node)

        return self._exhausted()

    def _remaining_rules(
        self, node: Node, untried: dict[int, deque[TransitionRule]]
    ) -> deque[TransitionRule]:
        """Na primeira visita monta a lista do nó; nas voltas seguintes apenas
        devolve o que sobrou dela. _applicable_rules já poda a regra que
        repetiria um estado do caminho.

        As seis regras que entram nessa lista:

        ```
        regra | de | para | inversa
        ------+----+------+--------
        R1    | H1 | H2   | R3
        R2    | H1 | H3   | R5
        R3    | H2 | H1   | R1
        R4    | H2 | H3   | R6
        R5    | H3 | H1   | R2
        R6    | H3 | H2   | R4
        ```

        Toda regra tem inversa exata, e é daí que vem a necessidade da poda:
        sem ela, R1 seguido de R3 devolveria a busca ao mesmo estado, sempre.
        """
        if node.order not in untried:
            self._visit(node)
            candidates = self._applicable_rules(node)
            untried[node.order] = deque(candidates)
            if not candidates:
                self._deadlock(node)
        return untried[node.order]
