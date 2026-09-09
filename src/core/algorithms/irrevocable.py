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

4. Execução com a ordem decrescente R6 → R5 → R4 → R3 → R2 → R1

    Passo 1   S0 = ([V, R], [A], [])
              válidas em ordem: R4, R3, R2, R1
              aplica R4 (azul: H2 → H3)
              ↓
    Passo 2   S1 = ([V, R], [], [A])
              válidas em ordem: R6, R5, R1
              R6 volta a S0: poda.  Aplica R5 (azul: H3 → H1)
              ↓
    Passo 3   S2 = ([V, R, A], [], [])
              válidas em ordem: R2, R1
              R2 volta a S1: poda.  R1 volta a S0: poda.
              Nenhuma regra sobrou.
              ↓
              ✗ IMPASSE

5. Árvore de busca

    S0 ([V,R], [A], [])
    └── R4 → S1 ([V,R], [], [A])
        └── R5 → S2 ([V,R,A], [], [])   (impasse)

6. A mesma carta com a ordem crescente R1 → R2 → R3 → R4 → R5 → R6

    S0 ([V,R],[A],[]) → R1 → R2 → R3 → R3 → R5 → R1 → R1 → R2 → R3 → R3
       → R5 → R1 → R1 → R2 → Sf ([],[R,V],[A])

    ✓ SUCESSO com 14 movimentos.  O caminho ótimo tem 3.

7. Conclusão

    O caminho nunca repete estado, então a busca sempre para, no máximo
    depois dos 36 estados. Parar não é chegar: a ordem decrescente termina
    em impasse e a crescente só chega depois de 14 movimentos.
    É o único método em que a estratégia decide o desfecho.
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
