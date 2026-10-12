"""BUSCA IRREVOGÁVEL

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

       H1      H2      H3              H1      H2      H3
      ┌───┐   ┌───┐   ┌───┐           ┌───┐   ┌───┐   ┌───┐
      │ R │   │   │   │   │           │   │   │ V │   │   │
      │ V │   │ A │   │   │           │   │   │ R │   │ A │
      └───┘   └───┘   └───┘           └───┘   └───┘   └───┘

2. Regras válidas em S0

    R1 = H1 → H2  ✓          R4 = H2 → H3  ✓
    R2 = H1 → H3  ✓          R5 = H3 → H1  ✗  H3 vazia
    R3 = H2 → H1  ✓          R6 = H3 → H2  ✗  H3 vazia

3. Critério

    A estratégia ordena as regras válidas e a busca aplica a primeira.
    Não guarda as outras: cada passo é definitivo e não há retorno.
    Uma regra que leva a um estado já percorrido é descartada (poda).
"""

from __future__ import annotations

from typing import ClassVar

from core.algorithms.domain.base import SearchAlgorithm
from core.domain.problem import Problem
from core.search_tree.outcome import Outcome


class IrrevocableSearch(SearchAlgorithm):
    name: ClassVar[str] = "irrevocable"

    def _search(self, problem: Problem) -> Outcome:
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

            node = self._expand(node, candidates[0])
