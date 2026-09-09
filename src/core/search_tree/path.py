from __future__ import annotations

from collections.abc import Iterator

from core.domain.state import State
from core.search_tree.node import Node


def ancestors(node: Node) -> Iterator[Node]:
    current = node.parent
    while current is not None:
        yield current
        current = current.parent


def path_to(node: Node) -> tuple[Node, ...]:
    reversed_path = [node, *ancestors(node)]
    reversed_path.reverse()
    return tuple(reversed_path)


def states_on_path(node: Node) -> frozenset[State]:
    return frozenset(step.state for step in path_to(node))


def contains_state(node: Node, state: State) -> bool:
    if node.state == state:
        return True
    return any(ancestor.state == state for ancestor in ancestors(node))


def applied_rules(node: Node) -> tuple[str, ...]:
    return tuple(step.rule.id for step in path_to(node) if step.rule is not None)
