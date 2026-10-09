"""BUSCA EM LARGURA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Critério

    As regras são analisadas na ordem crescente R1 → R2 → R3 → R4 → R5 → R6.
    Em vez de escolher uma, a busca aplica todas as válidas e coloca os
    filhos no fim de ABERTOS. O estado visitado vai para FECHADOS. Uma
    regra cujo resultado já está em ABERTOS ou FECHADOS é descartada (poda).
"""

from __future__ import annotations

from typing import ClassVar

from config import settings
from core.algorithms.breadth_first.frontier import QueueFrontier
from core.algorithms.domain.base import SearchAlgorithm
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.rules.strategies.domain.base import ControlStrategy
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome
from core.search_tree.tree import SearchTree


class BreadthFirstSearch(SearchAlgorithm):
    name: ClassVar[str] = "breadth_first"

    def __init__(
        self,
        tree: SearchTree,
        strategy: ControlStrategy,
        *,
        max_iterations: int = settings.MAX_ITERATIONS,
        prune: bool = True,
    ) -> None:
        super().__init__(tree, strategy, max_iterations=max_iterations, prune=prune)
        self._closed: set[State] = set()
        self._open_states: set[State] = set()

    def _search(self, problem: Problem) -> Outcome:
        context = self._require_context()
        frontier = QueueFrontier()
        frontier.push(context.root)

        self._closed = set()
        self._open_states = {context.root.state}
        self._observe_frontier(len(frontier))

        while len(frontier):
            if not self._next_iteration():
                return Outcome.CUTOFF

            node = frontier.pop()
            self._open_states.discard(node.state)
            if problem.is_goal(node.state):
                return self._succeed(node)

            self._closed.add(node.state)
            self._visit(node)
            for rule in self._applicable_rules(node):
                child = self._expand(node, rule)
                self._open_states.add(child.state)
                frontier.push(child)
            self._observe_frontier(len(frontier))

        return self._exhausted()

    def _is_repetition(
        self, node: Node, rule: TransitionRule, successor: State
    ) -> bool:
        return successor in self._closed or successor in self._open_states
