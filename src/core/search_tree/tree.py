from __future__ import annotations

from core.costs.domain.base import CostFunction
from core.costs.domain.registry import DEFAULT_COST
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULES
from core.search_tree.node import Node


class SearchTree:
    __slots__ = ("_cost", "_nodes", "_rules")

    def __init__(
        self,
        rules: tuple[TransitionRule, ...] = RULES,
        cost: CostFunction = DEFAULT_COST,
    ) -> None:
        self._rules = rules
        self._cost = cost
        self._nodes: list[Node] = []

    @property
    def rules(self) -> tuple[TransitionRule, ...]:
        return self._rules

    @property
    def nodes(self) -> tuple[Node, ...]:
        return tuple(self._nodes)

    def root(self, state: State) -> Node:
        self._nodes = []
        node = Node(state=state, parent=None, rule=None, depth=0, order=0)
        self._nodes.append(node)
        return node

    def expand(self, node: Node, rule: TransitionRule) -> Node:
        child = Node(
            state=rule.apply(node.state),
            parent=node,
            rule=rule,
            depth=node.depth + 1,
            order=len(self._nodes),
            cost=node.cost + self.step_cost(rule, node.state),
        )
        self._nodes.append(child)
        return child

    def step_cost(self, rule: TransitionRule, state: State) -> int:
        return self._cost.cost(rule, state)
