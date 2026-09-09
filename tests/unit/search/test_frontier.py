from __future__ import annotations

import pytest

from core.domain.state import State
from core.search_tree.frontier import (
    EmptyFrontierError,
    Frontier,
    QueueFrontier,
    StackFrontier,
)
from core.search_tree.node import Node
from core.search_tree.tree import SearchTree


def _three_nodes(initial_state: State) -> tuple[Node, Node, Node]:
    tree = SearchTree()
    root = tree.root(initial_state)
    applicable = [rule for rule in tree.rules if rule.is_applicable(root.state)]
    first = tree.expand(root, applicable[0])
    second = tree.expand(root, applicable[1])
    return root, first, second


def test_stack_is_last_in_first_out(initial_state: State) -> None:
    root, first, second = _three_nodes(initial_state)
    frontier = StackFrontier()
    for node in (root, first, second):
        frontier.push(node)
    assert [frontier.pop() for _ in range(3)] == [second, first, root]


def test_queue_is_first_in_first_out(initial_state: State) -> None:
    root, first, second = _three_nodes(initial_state)
    frontier = QueueFrontier()
    for node in (root, first, second):
        frontier.push(node)
    assert [frontier.pop() for _ in range(3)] == [root, first, second]


@pytest.mark.parametrize("factory", [StackFrontier, QueueFrontier])
def test_length_tracks_the_content(
    factory: type[Frontier], initial_state: State
) -> None:
    root, first, _ = _three_nodes(initial_state)
    frontier = factory()
    assert len(frontier) == 0
    frontier.push(root)
    frontier.push(first)
    assert len(frontier) == 2
    frontier.pop()
    assert len(frontier) == 1


@pytest.mark.parametrize("factory", [StackFrontier, QueueFrontier])
def test_pop_on_empty_frontier_raises(factory: type[Frontier]) -> None:
    frontier = factory()
    with pytest.raises(EmptyFrontierError):
        frontier.pop()
