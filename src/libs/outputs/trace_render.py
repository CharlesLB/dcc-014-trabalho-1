from __future__ import annotations

from core.search_tree.trace import Trace
from libs.outputs import state_render, theme
from libs.outputs.table import render_table

_HEADERS = ("ITER", "EVENTO", "NÓ", "PROF", "REGRA", "ESTADO")


def render_trace(trace: Trace) -> str:
    rows = [
        (
            str(step.iteration),
            theme.event_label(step.event),
            f"#{step.node_order}",
            str(step.depth),
            step.rule_id or theme.ABSENT,
            state_render.render_inline(step.state),
        )
        for step in trace
    ]
    return render_table(_HEADERS, tuple(rows))
