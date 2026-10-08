"""BUSCA ORDENADA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Custos

    custo da regra = 10 + peso do disco movido x distância entre as hastes

        10          por jogada; pesa mais que o esforço, e em todo par do
                    espaço o caminho mais barato é um dos mais curtos
        distância   hastes vizinhas: 1; H1 <-> H3, que pula a do meio: 2
        peso        verde 1, vermelho 2, azul 3

    Na raiz: R1 (vermelho, 1) 12, R2 (vermelho, 2) 14, R3 (azul, 1) 13,
    R4 (azul, 1) 13. O custo de um nó é a soma das regras desde a raiz.

3. Critério

    ABERTOS é ordenada pelo MENOR custo. No empate, sai o nó gerado primeiro;
    entre irmãos de mesmo custo, decide a estratégia (aqui, a ordem crescente
    R1 → R2 → R3 → R4 → R5 → R6). A busca só encerra quando o objetivo vira
    o estado atual, não quando ele é gerado.

    Poda pelo vetor de menor custo: o filho cujo estado já foi gerado com
    custo menor ou igual é descartado. Se o novo custo for menor, o nó
    antigo sai de ABERTOS e da árvore e o novo entra no lugar.

4. Execução

    Expansão de S0 = ([V, R], [A], []), custo 0
        R1 → S1 = ([V], [A, R], [])      12
        R2 → S2 = ([V], [A], [R])        14
        R3 → S3 = ([V, R, A], [], [])    13
        R4 → S4 = ([V, R], [], [A])      13
        ABERTOS  = [S1(12), S3(13), S4(13), S2(14)]
        FECHADOS = [S0]

    Expansão de S1 = ([V], [A, R], []), custo 12
        R2 → S5 = ([], [A, R], [V])      24
        R3 → S0, R4 → estado de S2 (24 ≥ 14): poda
        ABERTOS  = [S3(13), S4(13), S2(14), S5(24)]

    Expansão de S3 = ([V, R, A], [], []), custo 13
        R1 → S0, R2 → S4: poda.  ✗ impasse
        ABERTOS  = [S4(13), S2(14), S5(24)]

    Expansão de S4 = ([V, R], [], [A]), custo 13
        R1 → S6 = ([V], [R], [A])        25
        R5, R6: poda
        ABERTOS  = [S2(14), S5(24), S6(25)]

    Expansão de S2 = ([V], [A], [R]), custo 14
        R1 → S7 = ([], [A, V], [R])      25
        R3 → S8 = ([V, A], [], [R])      27
        ABERTOS  = [S5(24), S6(25), S7(25), S8(27)]

    Expansão de S5 = ([], [A, R], [V]), custo 24
        R3 → S9 = ([R], [A], [V])        36

    Expansão de S6 = ([V], [R], [A]), custo 25
        R1 → S10 = ([], [R, V], [A])     36   ← é Sf, mas só entra na fila
        R5 → S11 = ([V, A], [R], [])     41   (azul, 2 hastes: 10 + 6)
        R6 → S12 = ([V], [R, A], [])     38
        ABERTOS  = [S7(25), S8(27), S9(36), S10(36), S12(38), S11(41)]

    Expansão de S7 = ([], [A, V], [R]), custo 25
        R5 → S13 = ([R], [A, V], [])     39

    Expansão de S8 = ([V, A], [], [R]), custo 27
        R5 → S14 = ([V, A, R], [], [])   41
        R6 → S15 = ([V, A], [R], [])     39   (vermelho, 1 haste: 10 + 2)
        ✓ TROCA: S15 chega ao estado de S11 por 39, menos que 41. S11 sai
          de ABERTOS e da árvore; S15 entra no lugar.
        ABERTOS  = [S9(36), S10(36), S12(38), S13(39), S15(39), S14(41)]

    Expansão de S9 = ([R], [A], [V]), custo 36
        S9 e S10 custam 36; S9 foi gerado antes e sai primeiro.
        R3 → S16 (49), R5 → S17 (48)

    Chega a vez de S10 = ([], [R, V], [A])
        ✓ SUCESSO

5. Árvore de busca (custo acumulado entre parênteses)

    S0 ([V,R], [A], [])  (0)
    ├── R1 → S1 ([V], [A,R], [])  (12)
    │   └── R2 → S5 ([], [A,R], [V])  (24)
    │       └── R3 → S9 ([R], [A], [V])  (36)
    │           ├── R3 → S16  (49)
    │           └── R5 → S17  (48)
    ├── R2 → S2 ([V], [A], [R])  (14)
    │   ├── R1 → S7 ([], [A,V], [R])  (25)
    │   │   └── R5 → S13  (39)
    │   └── R3 → S8 ([V,A], [], [R])  (27)
    │       ├── R5 → S14  (41)
    │       └── R6 → S15 ([V,A], [R], [])  (39)   (substituiu S11)
    ├── R3 → S3 ([V,R,A], [], [])  (13)   (impasse)
    └── R4 → S4 ([V,R], [], [A])  (13)
        └── R1 → S6 ([V], [R], [A])  (25)
            ├── R1 → S10 ([], [R,V], [A])  (36)   (objetivo)
            ├── R5 → S11  (41)   (removido pela troca)
            └── R6 → S12 ([V], [R,A], [])  (38)

6. Caminho solução

    S0 ([V,R], [A], [])
     │ R4: azul H2 → H3        10 + 3 x 1 = 13
     ↓
    S4 ([V,R], [], [A])
     │ R1: vermelho H1 → H2    10 + 2 x 1 = 12
     ↓
    S6 ([V], [R], [A])
     │ R1: verde H1 → H2       10 + 1 x 1 = 11
     ↓
    Sf ([], [R,V], [A])

    Custo da solução: 13 + 12 + 11 = 36
    Número de movimentos: 3      Iterações: 11      Gerados: 18

    Com a ordem decrescente: o mesmo caminho, o mesmo custo e também 11
    iterações.

7. Conclusão

    Um nó só é expandido depois de todos os mais baratos, então quando o
    objetivo vira o estado atual nenhum nó aberto chega nele mais barato:
    a solução é a de MENOR CUSTO. Como cada jogada custa 10 e o esforço de
    uma jogada varia só de 1 a 6, a de menor custo é, em todo par do
    espaço, uma das de menos movimentos; entre as de mesmo tamanho, vence a
    que carrega os discos mais pesados por menos distância.
"""

from __future__ import annotations

from typing import ClassVar

from config import settings
from core.algorithms.domain.base import SearchAlgorithm
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.rules.strategies.domain.base import ControlStrategy
from core.search_tree.frontier import PriorityFrontier
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

    def _search(self, problem: Problem) -> Outcome:
        """Sempre expande o nó aberto de menor custo acumulado.

        O objetivo só encerra a busca quando vira o estado atual, não quando
        é gerado: só aí nenhum nó aberto pode chegar nele mais barato.
        """
        context = self._require_context()
        frontier = PriorityFrontier()
        frontier.push(context.root)

        # Vetor de menor custo: o custo do caminho mais barato já gerado até
        # cada estado. Cobre ABERTOS e FECHADOS de uma vez.
        self._best_cost = {context.root.state: 0}
        # O nó de cada estado que ainda espera em ABERTOS, para poder tirá-lo
        # de lá quando um caminho mais barato até o mesmo estado aparecer.
        self._open = {context.root.state: context.root}
        self._observe_frontier(len(frontier))

        while len(frontier):
            if not self._next_iteration():
                return Outcome.CUTOFF

            node = frontier.pop()
            if self._open.get(node.state) is node:
                del self._open[node.state]
            if problem.is_goal(node.state):
                return self._succeed(node)

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

    def _is_repetition(
        self, node: Node, rule: TransitionRule, successor: State
    ) -> bool:
        """Poda o filho que não melhora o menor custo conhecido do estado.

        Com custos positivos, um estado já fechado nunca é alcançado mais
        barato depois, então ele sempre cai aqui.
        """
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
