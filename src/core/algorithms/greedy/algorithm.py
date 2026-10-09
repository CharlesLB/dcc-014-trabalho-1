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

4. Execução (h entre parênteses)

    Passo 1   S0 = ([V, R], [A], [])   (3)
              R1 (4), R2 (3), R3 (3), R4 (2): aplica R4
              ↓
    Passo 2   S1 = ([V, R], [], [A])   (2)
              R6 volta a S0: poda.  R1 (1), R5 (3): aplica R1
              ↓
    Passo 3   S2 = ([V], [R], [A])     (1)
              R3 volta a S1: poda.  R1 (0), R5 (2), R6 (2): aplica R1
              ↓
    Passo 4   S3 = ([], [R, V], [A])   (0)
              ✓ SUCESSO

5. Caminho encontrado

    R4 R1 R1

    Número de movimentos: 3      Iterações: 4      Gerados: 4

    Com a ordem decrescente: o mesmo caminho. Em P1 não há empate de
    heurística no menor valor, então a estratégia não muda nada.

6. Conclusão

    Quando a heurística aponta o caminho certo, é o método mais barato: um
    nó gerado por passo. Mas sem fronteira não há como desfazer uma escolha
    ruim: nos 36 objetivos ela trava em 7 com a ordem crescente e em 8 com
    a decrescente, como a irrevogável.
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
