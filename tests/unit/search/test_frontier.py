from __future__ import annotations

import pytest

from core.domain.state import State
from core.search_tree.frontier import (
    EmptyFrontierError,
    Frontier,
    PriorityFrontier,
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


def _priced(initial_state: State, *costs: int) -> tuple[Node, ...]:
    return tuple(
        Node(
            state=initial_state, parent=None, rule=None, depth=0, order=order, cost=cost
        )
        for order, cost in enumerate(costs)
    )


def test_priority_pops_the_cheapest_first(initial_state: State) -> None:
    nodes = _priced(initial_state, 5, 6, 6, 1)
    frontier = PriorityFrontier()
    for node in nodes:
        frontier.push(node)
    assert [frontier.pop().order for _ in range(4)] == [3, 0, 1, 2]


def test_priority_breaks_ties_by_generation_order(initial_state: State) -> None:
    nodes = _priced(initial_state, 6, 6, 6)
    frontier = PriorityFrontier()
    for node in reversed(nodes):
        frontier.push(node)
    assert [frontier.pop().order for _ in range(3)] == [0, 1, 2]


def test_priority_skips_removed_nodes(initial_state: State) -> None:
    cheap, middle, dear = _priced(initial_state, 1, 2, 3)
    frontier = PriorityFrontier()
    for node in (cheap, middle, dear):
        frontier.push(node)
    frontier.remove(cheap)
    assert len(frontier) == 2
    assert frontier.pop() is middle
    assert frontier.pop() is dear
    assert len(frontier) == 0


@pytest.mark.parametrize("factory", [StackFrontier, QueueFrontier, PriorityFrontier])
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


@pytest.mark.parametrize("factory", [StackFrontier, QueueFrontier, PriorityFrontier])
def test_pop_on_empty_frontier_raises(factory: type[Frontier]) -> None:
    frontier = factory()
    with pytest.raises(EmptyFrontierError):
        frontier.pop()


def test_priority_pop_raises_when_only_removed_nodes_remain(
    initial_state: State,
) -> None:
    (node,) = _priced(initial_state, 1)
    frontier = PriorityFrontier()
    frontier.push(node)
    frontier.remove(node)
    with pytest.raises(EmptyFrontierError):
        frontier.pop()
