from __future__ import annotations

import pytest

from core.domain.state import State
from core.rules.domain.exceptions import RuleNotApplicableError
from core.rules.moves import R1, R5
from core.search_tree.node import Node
from core.search_tree.tree import SearchTree


def test_root_has_no_parent_and_zero_depth(initial_state: State) -> None:
    root = SearchTree().root(initial_state)
    assert root.is_root
    assert root.parent is None
    assert root.rule is None
    assert root.depth == 0
    assert root.order == 0


def test_child_records_its_origin(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    child = tree.expand(root, R1)
    assert child.parent is root
    assert child.rule is R1
    assert child.depth == 1
    assert child.state == R1.apply(initial_state)


def test_node_is_immutable(initial_state: State) -> None:
    root = SearchTree().root(initial_state)
    with pytest.raises(AttributeError):
        root.depth = 7  # type: ignore[misc]


def test_node_is_hashable(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    child = tree.expand(root, R1)
    assert len({root, child, root}) == 2


def test_orders_are_unique_within_a_run(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    children = [
        tree.expand(root, rule) for rule in tree.rules if rule.is_applicable(root.state)
    ]
    orders = [node.order for node in (root, *children)]
    assert len(set(orders)) == len(orders)


def test_root_resets_the_numbering(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    tree.expand(root, R1)
    restarted = tree.root(initial_state)
    assert restarted.order == 0
    assert len(tree.nodes) == 1


def test_tree_records_generated_nodes(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    child = tree.expand(root, R1)
    assert tree.nodes == (root, child)


def test_tree_ancestors_walks_up_to_the_root(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    child = tree.expand(root, R1)
    assert list(tree.ancestors(child)) == [root]


def test_expand_rejects_non_applicable_rule(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    assert not R5.is_applicable(initial_state)
    with pytest.raises(RuleNotApplicableError):
        tree.expand(root, R5)


def test_node_equality_is_structural(initial_state: State) -> None:
    first = Node(state=initial_state, parent=None, rule=None, depth=0, order=0)
    second = Node(state=initial_state, parent=None, rule=None, depth=0, order=0)
    assert first == second
