from __future__ import annotations

from core.search_tree.trace import Trace, TraceEvent
from libs.outputs import state_render, theme


def render_tree(trace: Trace) -> str:
    root_steps = trace.of_event(TraceEvent.ROOT)
    if not root_steps:
        return ""

    root = root_steps[0]
    children: dict[int, list[tuple[int, str | None, str]]] = {}
    for step in trace.of_event(TraceEvent.GENERATE):
        if step.parent_order is None:
            continue
        label = state_render.render_inline(step.state)
        children.setdefault(step.parent_order, []).append(
            (step.node_order, step.rule_id, label)
        )

    goal_orders = {step.node_order for step in trace.of_event(TraceEvent.GOAL)}
    deadlock_orders = {step.node_order for step in trace.of_event(TraceEvent.DEADLOCK)}

    lines = [f"#{root.node_order} {state_render.render_inline(root.state)}"]
    _append_children(lines, root.node_order, children, goal_orders, deadlock_orders, "")
    return "\n".join(lines)


def _append_children(
    lines: list[str],
    parent_order: int,
    children: dict[int, list[tuple[int, str | None, str]]],
    goal_orders: set[int],
    deadlock_orders: set[int],
    prefix: str,
) -> None:
    siblings = children.get(parent_order, ())
    for position, (order, rule_id, label) in enumerate(siblings):
        is_last = position == len(siblings) - 1
        connector = theme.TREE_LAST_BRANCH if is_last else theme.TREE_BRANCH
        marks = ""
        if order in goal_orders:
            marks = f"  ({theme.event_label(TraceEvent.GOAL)})"
        elif order in deadlock_orders:
            marks = f"  ({theme.event_label(TraceEvent.DEADLOCK)})"
        lines.append(f"{prefix}{connector}{rule_id} → #{order} {label}{marks}")
        _append_children(
            lines,
            order,
            children,
            goal_orders,
            deadlock_orders,
            prefix + (theme.TREE_GAP if is_last else theme.TREE_TRUNK),
        )
