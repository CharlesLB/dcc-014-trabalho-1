from __future__ import annotations

import sys
import textwrap
from typing import TextIO

from core.search_tree.result import SearchResult
from libs.outputs import state_render, theme, trace_render, tree_render
from libs.outputs.formatter import ProblemReport, Report
from libs.outputs.trace_render import render_table
from libs.ranking.leaderboard import Leaderboard, Summary


class ConsoleFormatter:
    name = "console"

    def render(self, report: Report) -> str:
        blocks = [self._render_problem(entry, report) for entry in report.problems]
        if report.summary is not None and len(report.problems) > 1:
            blocks.append(self._render_summary(report.summary))
        return "\n\n".join(block for block in blocks if block)

    def _render_summary(self, summary: Summary) -> str:
        return render_section(theme.SUMMARY_HEADER, render_summary(summary))

    def _render_problem(self, entry: ProblemReport, report: Report) -> str:
        sections = [
            f"{theme.PROBLEM_HEADER} {entry.problem_id}",
            "",
            f"{theme.INITIAL_STATE_HEADER}: {state_render.render_inline(entry.initial_state)}",
            f"{theme.GOAL_STATE_HEADER}: {state_render.render_inline(entry.goal_state)}",
        ]
        for result in entry.results:
            sections.append("")
            sections.append(render_result_box(result))
            sections.extend(_render_details(result, report))
        if entry.leaderboard is not None:
            sections.extend(
                [
                    "",
                    render_section(
                        theme.LEADERBOARD_HEADER, render_leaderboard(entry.leaderboard)
                    ),
                ]
            )
        return "\n".join(sections)


def render_result_box(result: SearchResult) -> str:
    metrics = result.metrics
    moves = (
        theme.ABSENT if result.solution_length is None else str(result.solution_length)
    )
    path = (
        theme.ARROW.join(result.applied_rules) if result.applied_rules else theme.ABSENT
    )
    rows = (
        (theme.REPORT_LABELS["outcome"], theme.outcome_label(result.outcome)),
        (theme.REPORT_LABELS["moves"], moves),
        (theme.REPORT_LABELS["path"], path),
        (theme.REPORT_LABELS["iterations"], str(metrics.iterations)),
        (theme.REPORT_LABELS["nodes_generated"], str(metrics.nodes_generated)),
        (theme.REPORT_LABELS["nodes_visited"], str(metrics.nodes_visited)),
        (theme.REPORT_LABELS["rules_tested"], str(metrics.rules_tested)),
        (theme.REPORT_LABELS["backtracks"], str(metrics.backtracks)),
        (theme.REPORT_LABELS["deadlocks"], str(metrics.deadlocks)),
        (theme.REPORT_LABELS["max_depth"], str(metrics.max_depth)),
        (theme.REPORT_LABELS["elapsed"], f"{metrics.elapsed_ms:.3f}"),
    )
    lines = [line for label, value in rows for line in _wrap_row(label, value)]
    return render_box(result.label, tuple(lines))


def _wrap_row(label: str, value: str) -> list[str]:
    available = theme.MAX_BOX_WIDTH - 2 - theme.LABEL_WIDTH
    chunks = textwrap.wrap(value, width=available) or [""]
    head = f"{label.ljust(theme.LABEL_WIDTH)}{chunks[0]}"
    tail = [f"{''.ljust(theme.LABEL_WIDTH)}{chunk}" for chunk in chunks[1:]]
    return [head, *tail]


def render_leaderboard(leaderboard: Leaderboard) -> str:
    scored = leaderboard.mode == "score"
    headers = theme.LEADERBOARD_HEADERS if scored else theme.LEADERBOARD_HEADERS[:-1]
    rows = []
    for row in leaderboard.rows:
        result = row.result
        cells = [
            str(row.position),
            result.algorithm,
            result.strategy,
            theme.outcome_label(result.outcome),
            theme.ABSENT
            if result.solution_length is None
            else str(result.solution_length),
            str(result.metrics.iterations),
            str(result.metrics.nodes_generated),
        ]
        if scored:
            cells.append(theme.ABSENT if row.score is None else f"{row.score:.1f}")
        rows.append(tuple(cells))
    return render_table(headers, tuple(rows))


def render_summary(summary: Summary) -> str:
    rows = tuple(
        (
            row.algorithm,
            row.strategy,
            f"{row.successes}/{row.runs}",
            str(row.deadlocks),
            theme.ABSENT if row.mean_moves is None else f"{row.mean_moves:.1f}",
            f"{row.mean_iterations:.1f}",
        )
        for row in summary.rows
    )
    return render_table(theme.SUMMARY_HEADERS, rows)


def render_box(title: str, lines: tuple[str, ...]) -> str:
    content_width = max((len(line) for line in lines), default=0)
    width = min(
        max(content_width + 2, len(title) + 6, theme.MIN_BOX_WIDTH),
        max(theme.MAX_BOX_WIDTH, len(title) + 6, content_width + 2),
    )

    header = f"{theme.BOX_HORIZONTAL} {title} "
    top = (
        theme.BOX_TOP_LEFT
        + header
        + theme.BOX_HORIZONTAL * (width - len(header))
        + theme.BOX_TOP_RIGHT
    )
    body = [
        f"{theme.BOX_VERTICAL} {line.ljust(width - 2)} {theme.BOX_VERTICAL}"
        for line in lines
    ]
    bottom = (
        theme.BOX_BOTTOM_LEFT + theme.BOX_HORIZONTAL * width + theme.BOX_BOTTOM_RIGHT
    )
    return "\n".join([top, *body, bottom])


def render_section(title: str, body: str) -> str:
    return f"{title}\n{theme.BOX_HORIZONTAL * len(title)}\n{body}"


def _render_details(result: SearchResult, report: Report) -> list[str]:
    sections: list[str] = []
    if report.show_states and result.solution_path:
        drawings = "\n\n".join(
            state_render.render_pegs(node.state) for node in result.solution_path
        )
        sections.extend(["", render_section(theme.STATES_HEADER, drawings)])
    if report.show_tree:
        sections.extend(
            [
                "",
                render_section(
                    theme.TREE_HEADER, tree_render.render_tree(result.trace)
                ),
            ]
        )
    if report.show_trace:
        sections.extend(
            [
                "",
                render_section(
                    theme.TRACE_HEADER, trace_render.render_trace(result.trace)
                ),
            ]
        )
    return sections


def write(text: str, stream: TextIO | None = None) -> None:
    target = sys.stdout if stream is None else stream
    target.write(f"{text}\n")


def write_error(text: str) -> None:
    sys.stderr.write(f"{text}\n")
