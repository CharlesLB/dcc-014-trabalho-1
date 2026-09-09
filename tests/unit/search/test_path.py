from __future__ import annotations

from core.domain.state import State
from core.rules.domain.catalog import inverse_of
from core.search_tree import path
from core.search_tree.tree import SearchTree


def test_path_to_root_is_the_root_alone(initial_state: State) -> None:
    root = SearchTree().root(initial_state)
    assert path.path_to(root) == (root,)
    assert list(path.ancestors(root)) == []


def test_path_is_ordered_from_root_to_node(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    rule = next(r for r in tree.rules if r.is_applicable(root.state))
    child = tree.expand(root, rule)
    grandchild_rule = next(
        r
        for r in tree.rules
        if r.is_applicable(child.state) and r is not inverse_of(rule)
    )
    grandchild = tree.expand(child, grandchild_rule)

    assert path.path_to(grandchild) == (root, child, grandchild)
    assert [node.depth for node in path.path_to(grandchild)] == [0, 1, 2]


def test_states_on_path_collects_every_state(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    rule = next(r for r in tree.rules if r.is_applicable(root.state))
    child = tree.expand(root, rule)
    assert path.states_on_path(child) == frozenset({root.state, child.state})


def test_contains_state_detects_the_node_itself(initial_state: State) -> None:
    root = SearchTree().root(initial_state)
    assert path.contains_state(root, initial_state)


def test_contains_state_detects_an_ancestor(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    rule = next(r for r in tree.rules if r.is_applicable(root.state))
    child = tree.expand(root, rule)
    back = tree.expand(child, inverse_of(rule))

    assert back.state == initial_state
    assert path.contains_state(child, initial_state)
    assert path.contains_state(back, initial_state)


def test_contains_state_is_false_for_an_unrelated_state(
    initial_state: State, states: tuple[State, ...]
) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    unseen = next(state for state in states if state != initial_state)
    assert not path.contains_state(root, unseen)


def test_applied_rules_lists_the_moves_in_order(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    rule = next(r for r in tree.rules if r.is_applicable(root.state))
    child = tree.expand(root, rule)
    assert path.applied_rules(root) == ()
    assert path.applied_rules(child) == (rule.id,)
