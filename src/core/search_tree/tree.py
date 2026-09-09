from __future__ import annotations

from collections.abc import Iterator

from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULES
from core.search_tree.node import Node
from core.search_tree.path import ancestors


class SearchTree:
    __slots__ = ("_nodes", "_rules")

    def __init__(self, rules: tuple[TransitionRule, ...] = RULES) -> None:
        self._rules = rules
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
        )
        self._nodes.append(child)
        return child

    def ancestors(self, node: Node) -> Iterator[Node]:
        return ancestors(node)
