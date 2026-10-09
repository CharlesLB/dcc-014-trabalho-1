from __future__ import annotations

from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent, TraceStep
from libs.outputs import state_render, theme
from libs.outputs.tree_render import kept_generations


def render_dot(result: SearchResult) -> str:
    trace = result.trace
    root_steps = trace.of_event(TraceEvent.ROOT)
    if not root_steps:
        return ""

    goal_orders = trace.orders_of(TraceEvent.GOAL)
    deadlock_orders = trace.orders_of(TraceEvent.DEADLOCK)
    visited_orders = trace.orders_of(TraceEvent.VISIT)
    solution_orders = {node.order for node in result.solution_path}

    lines = [
        "digraph search {",
        f'  label="{_title(result)}"; labelloc=t; fontname="{theme.GRAPH_FONT}";',
        f'  node [shape=box, style="rounded,filled", fontname="{theme.GRAPH_MONO_FONT}", fontsize=10];',
        f'  edge [fontname="{theme.GRAPH_FONT}", fontsize=9];',
        _node(root_steps[0], theme.GRAPH_ROOT_FILL, on_path=bool(solution_orders)),
    ]

    for step in kept_generations(trace):
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
    parts = [result.problem, result.label]
    if not result.pruned:
        parts.append(theme.GRAPH_NO_PRUNE_LABEL)
    parts.append(theme.outcome_label(result.outcome))
    if result.solution_length is not None:
        parts.append(f"{result.solution_length} {theme.GRAPH_MOVES_LABEL}")
    if result.solution_cost is not None:
        parts.append(f"{theme.GRAPH_COST_LABEL} {result.solution_cost}")
    return " · ".join(parts)


def _node(step: TraceStep, fill: str, *, on_path: bool) -> str:
    label = f"#{step.node_order}\\n{state_render.render_inline(step.state)}"
    color, width = _stroke(on_path=on_path)
    return (
        f'  n{step.node_order} [label="{label}", fillcolor="{fill}", '
        f'color="{color}", penwidth={width}];'
    )


def _edge(step: TraceStep, *, on_path: bool) -> str:
    color, width = _stroke(on_path=on_path)
    return (
        f'  n{step.parent_order} -> n{step.node_order} [label="{step.rule_id}", '
        f'color="{color}", fontcolor="{color}", penwidth={width}];'
    )


def _stroke(*, on_path: bool) -> tuple[str, float]:
    """Cor e espessura do contorno: o caminho solução sai destacado."""
    if on_path:
        return theme.GRAPH_PATH_COLOR, theme.GRAPH_PATH_WIDTH
    return theme.GRAPH_NODE_COLOR, 1


def _pruned(step: TraceStep) -> str:
    ghost = f"p{step.node_order}_{step.rule_id}"
    return (
        f'  {ghost} [label="{step.rule_id}", shape=plaintext, style=solid, '
        f'fontcolor="{theme.GRAPH_PRUNED_COLOR}", fontsize=8];\n'
        f"  n{step.node_order} -> {ghost} [style=dotted, "
        f'color="{theme.GRAPH_PRUNED_COLOR}", arrowhead=none];'
    )
