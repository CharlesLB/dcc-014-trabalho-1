from __future__ import annotations

import pytest

from core.domain.state import State
from core.search_tree.metrics import MetricsCollector, SearchMetrics
from core.search_tree.trace import Trace, TraceEvent, TraceRecorder
from core.search_tree.tree import SearchTree


def test_collector_starts_at_zero() -> None:
    metrics = MetricsCollector().seal(elapsed_ms=0.0)
    assert metrics == SearchMetrics(0, 0, 0, 0, 0, 0, 0, 0.0)


def test_each_counter_is_independent() -> None:
    collector = MetricsCollector()
    collector.count_iteration()
    collector.count_generated(depth=3)
    collector.count_visited()
    collector.count_rule_test()
    collector.count_backtrack()
    collector.count_deadlock()

    metrics = collector.seal(elapsed_ms=1.5)
    assert metrics.iterations == 1
    assert metrics.nodes_generated == 1
    assert metrics.nodes_visited == 1
    assert metrics.rules_tested == 1
    assert metrics.backtracks == 1
    assert metrics.deadlocks == 1
    assert metrics.max_depth == 3
    assert metrics.elapsed_ms == 1.5


def test_max_depth_keeps_the_highest_value() -> None:
    collector = MetricsCollector()
    for depth in (2, 5, 1):
        collector.count_generated(depth)
    assert collector.seal(0.0).max_depth == 5


def test_sealed_metrics_are_immutable() -> None:
    metrics = MetricsCollector().seal(0.0)
    with pytest.raises(AttributeError):
        metrics.iterations = 9  # type: ignore[misc]


def test_trace_records_events_in_order(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    recorder = TraceRecorder()
    recorder.record(iteration=0, event=TraceEvent.ROOT, node=root)
    recorder.record(iteration=1, event=TraceEvent.VISIT, node=root)

    trace = recorder.seal()
    assert [step.event for step in trace] == [TraceEvent.ROOT, TraceEvent.VISIT]
    assert len(trace) == 2


def test_trace_step_carries_the_parent_link(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    rule = next(r for r in tree.rules if r.is_applicable(root.state))
    child = tree.expand(root, rule)

    recorder = TraceRecorder()
    recorder.record(iteration=1, event=TraceEvent.GENERATE, node=child)
    step = recorder.seal().steps[0]

    assert step.parent_order == root.order
    assert step.node_order == child.order
    assert step.rule_id == rule.id
    assert step.depth == 1


def test_trace_records_pruned_transitions(initial_state: State) -> None:
    tree = SearchTree()
    root = tree.root(initial_state)
    rule = next(r for r in tree.rules if r.is_applicable(root.state))

    recorder = TraceRecorder()
    recorder.record_prune(
        iteration=2, node=root, rule_id=rule.id, state=rule.apply(root.state)
    )
    trace = recorder.seal()
    assert trace.of_event(TraceEvent.PRUNE)[0].rule_id == rule.id


def test_empty_trace_is_falsy_in_length() -> None:
    assert len(Trace()) == 0
