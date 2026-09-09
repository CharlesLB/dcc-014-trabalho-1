from __future__ import annotations

from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent, TraceStep
from libs.outputs import state_render, theme


def render_dot(result: SearchResult) -> str:
    trace = result.trace
    root_steps = trace.of_event(TraceEvent.ROOT)
    if not root_steps:
        return ""

    goal_orders = {step.node_order for step in trace.of_event(TraceEvent.GOAL)}
    deadlock_orders = {step.node_order for step in trace.of_event(TraceEvent.DEADLOCK)}
    visited_orders = {step.node_order for step in trace.of_event(TraceEvent.VISIT)}
    solution_orders = {node.order for node in result.solution_path}

    lines = [
        "digraph search {",
        f'  label="{_title(result)}"; labelloc=t; fontname="{theme.GRAPH_FONT}";',
        f'  node [shape=box, style="rounded,filled", fontname="{theme.GRAPH_MONO_FONT}", fontsize=10];',
        f'  edge [fontname="{theme.GRAPH_FONT}", fontsize=9];',
        _node(root_steps[0], theme.GRAPH_ROOT_FILL, on_path=bool(solution_orders)),
    ]

    for step in trace.of_event(TraceEvent.GENERATE):
        if step.parent_order is None:
            continue
        on_path = step.node_order in solution_orders
        if step.node_order in goal_orders:
            fill = theme.GRAPH_GOAL_FILL
        elif step.node_order in deadlock_orders:
            fill = theme.GRAPH_DEADLOCK_FILL
        elif step.node_order in visited_orders:
            fill = theme.GRAPH_VISITED_FILL
        else:
            fill = theme.GRAPH_GENERATED_FILL
        lines.append(_node(step, fill, on_path=on_path))
        lines.append(_edge(step, on_path=on_path))

    lines.extend(_pruned(step) for step in trace.of_event(TraceEvent.PRUNE))
    lines.append("}")
    return "\n".join(lines)


def _title(result: SearchResult) -> str:
    parts = [result.problem, result.label, theme.outcome_label(result.outcome)]
    if result.solution_length is not None:
        parts.append(f"{result.solution_length} {theme.GRAPH_MOVES_LABEL}")
    return " · ".join(parts)


def _node(step: TraceStep, fill: str, *, on_path: bool) -> str:
    label = f"#{step.node_order}\\n{state_render.render_inline(step.state)}"
    width = theme.GRAPH_PATH_WIDTH if on_path else 1
    color = theme.GRAPH_PATH_COLOR if on_path else theme.GRAPH_NODE_COLOR
    return (
        f'  n{step.node_order} [label="{label}", fillcolor="{fill}", '
        f'color="{color}", penwidth={width}];'
    )


def _edge(step: TraceStep, *, on_path: bool) -> str:
    width = theme.GRAPH_PATH_WIDTH if on_path else 1
    color = theme.GRAPH_PATH_COLOR if on_path else theme.GRAPH_NODE_COLOR
    return (
        f'  n{step.parent_order} -> n{step.node_order} [label="{step.rule_id}", '
        f'color="{color}", fontcolor="{color}", penwidth={width}];'
    )


def _pruned(step: TraceStep) -> str:
    ghost = f"p{step.node_order}_{step.rule_id}"
    return (
        f'  {ghost} [label="{step.rule_id}", shape=plaintext, style=solid, '
        f'fontcolor="{theme.GRAPH_PRUNED_COLOR}", fontsize=8];\n'
        f"  n{step.node_order} -> {ghost} [style=dotted, "
        f'color="{theme.GRAPH_PRUNED_COLOR}", arrowhead=none];'
    )
