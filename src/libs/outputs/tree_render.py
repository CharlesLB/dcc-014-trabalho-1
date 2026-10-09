from __future__ import annotations

from core.search_tree.trace import Trace, TraceEvent, TraceStep
from libs.outputs import state_render, theme


def render_tree(trace: Trace) -> str:
    root_steps = trace.of_event(TraceEvent.ROOT)
    if not root_steps:
        return ""

    root = root_steps[0]
    children: dict[int, list[TraceStep]] = {}
    for step in kept_generations(trace):
        assert step.parent_order is not None
        children.setdefault(step.parent_order, []).append(step)

    goal_orders = trace.orders_of(TraceEvent.GOAL)
    deadlock_orders = trace.orders_of(TraceEvent.DEADLOCK)

    def mark(order: int) -> str:
        if order in goal_orders:
            return f"  ({theme.event_label(TraceEvent.GOAL)})"
        if order in deadlock_orders:
            return f"  ({theme.event_label(TraceEvent.DEADLOCK)})"
        return ""

    lines = [f"#{root.node_order} {state_render.render_inline(root.state)}"]

    def append_children(parent_order: int, prefix: str) -> None:
        siblings = children.get(parent_order, [])
        for position, step in enumerate(siblings):
            is_last = position == len(siblings) - 1
            connector = theme.TREE_LAST_BRANCH if is_last else theme.TREE_BRANCH
            label = state_render.render_inline(step.state)
            lines.append(
                f"{prefix}{connector}{step.rule_id} → #{step.node_order} "
                f"{label}{mark(step.node_order)}"
            )
            append_children(
                step.node_order,
                prefix + (theme.TREE_GAP if is_last else theme.TREE_TRUNK),
            )

    append_children(root.node_order, "")
    return "\n".join(lines)


def kept_generations(trace: Trace) -> tuple[TraceStep, ...]:
    """Os nós gerados que continuam na árvore, cada um com o pai.

    Fica de fora o nó que a busca ordenada substituiu por um caminho mais
    curto: o trace registra a aresta dele como poda do pai.
    """
    removed = {
        (step.node_order, step.rule_id) for step in trace.of_event(TraceEvent.PRUNE)
    }
    return tuple(
        step
        for step in trace.of_event(TraceEvent.GENERATE)
        if step.parent_order is not None
        and (step.parent_order, step.rule_id) not in removed
    )
