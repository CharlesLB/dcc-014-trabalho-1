"""BUSCA ORDENADA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Custos

    Cada regra custa a distância entre as hastes que ela liga:

        R1 = H1 → H2: 1     R3 = H2 → H1: 1     R4 = H2 → H3: 1
        R2 = H1 → H3: 2     R5 = H3 → H1: 2     R6 = H3 → H2: 1

    O custo de um nó é a soma das regras do caminho da raiz até ele.

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
        R1 → S1 = ([V], [A, R], [])      1
        R2 → S2 = ([V], [A], [R])        2
        R3 → S3 = ([V, R, A], [], [])    1
        R4 → S4 = ([V, R], [], [A])      1
        R5, R6: inválidas, H3 vazia
        ABERTOS  = [S1(1), S3(1), S4(1), S2(2)]
        FECHADOS = [S0(0)]

    Expansão de S1 = ([V], [A, R], []), custo 1
        R2 → S5 = ([], [A, R], [V])      3
        R3 → S0 (2 ≥ 0): poda
        R4 → estado de S2 (2 ≥ 2): poda
        ABERTOS  = [S3(1), S4(1), S2(2), S5(3)]
        FECHADOS = [S0(0), S1(1)]

    Expansão de S3 = ([V, R, A], [], []), custo 1
        R1 → S0, R2 → S4: poda.  Nada novo.
        ✗ impasse: S3 só vai para FECHADOS
        ABERTOS  = [S4(1), S2(2), S5(3)]
        FECHADOS = [S0(0), S1(1), S3(1)]

    Expansão de S4 = ([V, R], [], [A]), custo 1
        R1 → S6 = ([V], [R], [A])        2
        R5 → S3, R6 → S0: poda
        ABERTOS  = [S2(2), S6(2), S5(3)]
        FECHADOS = [S0(0), S1(1), S3(1), S4(1)]

    Expansão de S2 = ([V], [A], [R]), custo 2
        R1 → S7 = ([], [A, V], [R])      3
        R3 → S8 = ([V, A], [], [R])      3
        R5 → S0, R6 → S1: poda
        ABERTOS  = [S6(2), S5(3), S7(3), S8(3)]
        FECHADOS = [S0(0), S1(1), S3(1), S4(1), S2(2)]

    Expansão de S6 = ([V], [R], [A]), custo 2
        R1 → S9  = ([], [R, V], [A])     3   ← é Sf, mas só entra na fila
        R5 → S10 = ([V, A], [R], [])     4
        R6 → S11 = ([V], [R, A], [])     3
        R3 → S4: poda
        ABERTOS  = [S5(3), S7(3), S8(3), S9(3), S11(3), S10(4)]
        FECHADOS = [S0(0), S1(1), S3(1), S4(1), S2(2), S6(2)]

    S5, S7 e S8 custam 3 como S9, mas foram gerados antes e saem primeiro.
        S5 gera S12(4).  S7 gera S13(5).  S8 gera S14(5).
        ABERTOS  = [S9(3), S11(3), S10(4), S12(4), S13(5), S14(5)]
        FECHADOS = [S0(0), S1(1), S3(1), S4(1), S2(2), S6(2), S5(3),
                    S7(3), S8(3)]

    Chega a vez de S9 = ([], [R, V], [A])
        ✓ SUCESSO

5. Árvore de busca (custo acumulado entre parênteses)

    S0 ([V,R], [A], [])  (0)
    ├── R1 → S1 ([V], [A,R], [])  (1)
    │   └── R2 → S5 ([], [A,R], [V])  (3)
    │       └── R3 → S12  (4)
    ├── R2 → S2 ([V], [A], [R])  (2)
    │   ├── R1 → S7 ([], [A,V], [R])  (3)
    │   │   └── R5 → S13  (5)
    │   └── R3 → S8 ([V,A], [], [R])  (3)
    │       └── R5 → S14  (5)
    ├── R3 → S3 ([V,R,A], [], [])  (1)   (impasse)
    └── R4 → S4 ([V,R], [], [A])  (1)
        └── R1 → S6 ([V], [R], [A])  (2)
            ├── R1 → S9 ([], [R,V], [A])  (3)   (objetivo)
            ├── R5 → S10 ([V,A], [R], [])  (4)
            └── R6 → S11 ([V], [R,A], [])  (3)

6. Caminho solução

    S0 ([V,R], [A], [])
     │ R4: azul H2 → H3        custo 1
     ↓
    S4 ([V,R], [], [A])
     │ R1: vermelho H1 → H2    custo 1
     ↓
    S6 ([V], [R], [A])
     │ R1: verde H1 → H2       custo 1
     ↓
    Sf ([], [R,V], [A])

    Custo da solução: 1 + 1 + 1 = 3
    Número de movimentos: 3      Iterações: 10      Gerados: 15

    Com a ordem decrescente: o mesmo caminho em 11 iterações.

7. Conclusão

    Um nó só é expandido depois de todos os mais baratos, então quando o
    objetivo vira o estado atual nenhum nó aberto chega nele mais barato:
    a solução é a de MENOR CUSTO, que nem sempre é a de menos movimentos.
    Com custo unitário ela seria a busca em largura. Aqui, em P1, as duas
    acham o mesmo caminho, mas a ordenada deixa para depois os ramos que
    começam por R2 e chega em 10 iterações contra 14.
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
        return best is not None and node.cost + rule.cost >= best

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
