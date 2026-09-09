from __future__ import annotations

from core.search_tree.trace import Trace
from libs.outputs import state_render, theme

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


def render_table(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    widths = [
        max(len(headers[column]), *(len(row[column]) for row in rows))
        if rows
        else len(headers[column])
        for column in range(len(headers))
    ]
    lines = [
        "  ".join(header.ljust(widths[i]) for i, header in enumerate(headers)).rstrip()
    ]
    lines.extend(
        "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip()
        for row in rows
    )
    return "\n".join(lines)
