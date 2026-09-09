"""BUSCA COM BACKTRACKING

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Critério

    A mesma descida da busca irrevogável, mas as regras válidas de cada
    estado ficam guardadas numa pilha. Quando um estado não tem mais regra,
    ele sai da pilha (retrocesso) e o estado anterior tenta a próxima regra
    que tinha guardado. Uma regra que leva a um estado já no caminho atual
    é descartada (poda).

3. Execução com a ordem decrescente R6 → R5 → R4 → R3 → R2 → R1

    Passo 1   S0 = ([V, R], [A], [])
              guarda [R4, R3, R2, R1], aplica R4
              ↓
    Passo 2   S1 = ([V, R], [], [A])
              R6 volta a S0: poda.  Guarda [R5, R1], aplica R5
              ↓
    Passo 3   S2 = ([V, R, A], [], [])
              R2 volta a S1 e R1 volta a S0: poda.  Nada guardado.
              ✗ impasse → retrocesso: S2 sai da pilha
              ↑
    Passo 4   S1 = ([V, R], [], [A])   ainda tem [R1], aplica R1
              ↓
    Passo 5   S3 = ([V], [R], [A])
              R3 volta a S1: poda.  Guarda [R6, R5, R1], aplica R6
              ↓
              ...  continua descendo; a cada beco sem saída, um retrocesso

    Passo 51  S36 = ([], [R, V], [A])
              ✓ SUCESSO

4. Árvore de busca (início)

    S0 ([V,R], [A], [])
    └── R4 → S1 ([V,R], [], [A])
        ├── R5 → S2 ([V,R,A], [], [])   (impasse, retrocesso)
        └── R1 → S3 ([V], [R], [A])
            └── R6 → S4 ([V], [R,A], [])
                └── R3 → S5 ([V,A], [R], [])
                    └── R4 → S6 ([V,A], [], [R])
                        ├── R5 → S7 ([V,A,R], [], [])   (impasse, retrocesso)
                        └── R1 → S8 ([V], [A], [R])
                            └── ...  até S36 = Sf

5. Caminho encontrado

    R4 R1 R6 R3 R4 R1 R6 R2 R3 R6 R3 R4 R1 R6 R2 R3 R6 R3 R4 R1 R6 R2

    Número de movimentos: 22       Iterações: 51
    Retrocessos: 14                Impasses: 8

    Com a ordem crescente: 14 movimentos em 15 iterações, sem retrocesso.
    O caminho ótimo tem 3.

6. Conclusão

    O impasse da busca irrevogável vira um desvio: nenhum ramo é abandonado
    sem ser explorado e, como todo estado alcança todo estado, a solução
    sempre aparece. Só não é a melhor. A busca para no primeiro objetivo
    que encontra, tenha o caminho o comprimento que tiver.
"""

from __future__ import annotations

from collections import deque
from typing import ClassVar

from core.algorithms.domain.base import SearchAlgorithm
from core.domain.problem import Problem
from core.rules.domain.base import TransitionRule
from core.search_tree.frontier import StackFrontier
from core.search_tree.outcome import Outcome


class BacktrackingSearch(SearchAlgorithm):
    name: ClassVar[str] = "backtracking"

    def _search(self, problem: Problem) -> Outcome:
        context = self._require_context()
        frontier = StackFrontier()
        frontier.push(context.root)

        untried: dict[int, deque[TransitionRule]] = {}

        while len(frontier):
            if not self._next_iteration():
                return Outcome.CUTOFF

            node = frontier.pop()
            if problem.is_goal(node.state):
                return self._succeed(node)

            if node.order not in untried:
                self._visit(node)
                candidates = self._applicable_rules(node)
                untried[node.order] = deque(candidates)
                if not candidates:
                    self._deadlock(node)

            remaining = untried[node.order]
            if remaining:
                frontier.push(node)
                frontier.push(self._expand(node, remaining.popleft()))
            else:
                self._backtrack(node)

        return self._exhausted()
