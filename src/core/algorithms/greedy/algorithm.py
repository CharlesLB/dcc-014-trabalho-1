"""BUSCA GULOSA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Heurística: a mesma da busca ordenada (core/domain/heuristic.py)

    0 por disco bem posicionado, 1 em outra haste, 2 na haste certa mas mal
    posicionado. h(estado) = soma dos três discos.

3. Critério

    A mesma descida da busca irrevogável, mas a regra aplicada é a que leva
    ao filho de MENOR heurística, não a primeira da estratégia. A estratégia
    só desempata filhos de mesma heurística. Não guarda as outras: cada
    passo é definitivo e não há retorno. Uma regra que leva a um estado já
    percorrido é descartada (poda).
"""

from __future__ import annotations

from typing import ClassVar

from core.algorithms.domain.base import SearchAlgorithm
from core.domain.heuristic import misplacement
from core.domain.problem import Problem
from core.search_tree.outcome import Outcome


class GreedySearch(SearchAlgorithm):
    name: ClassVar[str] = "greedy"

    def _search(self, problem: Problem) -> Outcome:
        """Desce sempre pelo filho de menor heurística, sem voltar atrás.

        A estratégia só desempata filhos de mesma heurística: `min` fica com
        o primeiro deles na ordem dela.
        """
        node = self._require_context().root
        self._observe_frontier(1)
        while True:
            if not self._next_iteration():
                return Outcome.CUTOFF
            if problem.is_goal(node.state):
                return self._succeed(node)

            self._visit(node)
            candidates = self._applicable_rules(node)
            if not candidates:
                self._deadlock(node)
                return Outcome.DEADLOCK

            best = min(
                candidates,
                key=lambda rule: misplacement(rule.apply(node.state), problem.goal),
            )
            node = self._expand(node, best)
