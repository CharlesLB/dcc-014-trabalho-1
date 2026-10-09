from __future__ import annotations

import sys
import textwrap
from typing import Final, TextIO

from core.search_tree.result import SearchResult
from libs.outputs import state_render, theme, trace_render, tree_render
from libs.outputs.formatter import ProblemReport, Report
from libs.outputs.table import render_table
from libs.ranking.leaderboard import Leaderboard, Stat, Summary, SummaryRow

# Métricas da caixa de cada execução, na ordem em que aparecem, depois de
# desfecho, movimentos, custo e caminho.
_BOX_METRICS: Final = (
    "iterations",
    "nodes_generated",
    "nodes_visited",
    "rules_tested",
    "backtracks",
    "deadlocks",
    "max_depth",
    "max_frontier",
)


class ConsoleFormatter:
    name = "console"

    def render(self, report: Report) -> str:
        blocks = (
            []
            if report.summary_only
            else [self._render_problem(entry, report) for entry in report.problems]
        )
        if report.summary is not None and (
            report.summary_only or len(report.problems) > 1
        ):
            blocks.append(self._render_summary(report.summary))
        return "\n\n".join(block for block in blocks if block)

    def _render_summary(self, summary: Summary) -> str:
        sections = [render_section(theme.SUMMARY_HEADER, render_summary(summary))]
        if summary.highlights:
            sections.append(
                render_section(theme.HIGHLIGHTS_HEADER, render_highlights(summary))
            )
        return "\n\n".join(sections)

    def _render_problem(self, entry: ProblemReport, report: Report) -> str:
        sections = [
            f"{theme.PROBLEM_HEADER} {entry.problem_id}",
            "",
            f"{theme.INITIAL_STATE_HEADER}: {state_render.render_inline(entry.initial_state)}",
            f"{theme.GOAL_STATE_HEADER}: {state_render.render_inline(entry.goal_state)}",
        ]
        for result in entry.results:
            sections.extend(["", render_result_box(result)])
            sections.extend(_render_details(result, report))
        if entry.leaderboard is not None:
            leaderboard = render_leaderboard(entry.leaderboard)
            sections.extend(["", render_section(theme.LEADERBOARD_HEADER, leaderboard)])
        return "\n".join(sections)


def render_result_box(result: SearchResult) -> str:
    metrics = result.metrics
    rows = [
        ("outcome", theme.outcome_label(result.outcome)),
        ("moves", _or_absent(result.solution_length)),
        ("cost", _or_absent(result.solution_cost)),
        ("path", theme.ARROW.join(result.applied_rules) or theme.ABSENT),
        *((name, str(getattr(metrics, name))) for name in _BOX_METRICS),
        ("elapsed", f"{metrics.elapsed_ms:.3f}"),
    ]
    lines = [
        line
        for key, value in rows
        for line in _wrap_row(theme.REPORT_LABELS[key], value)
    ]
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
            _or_absent(result.solution_length),
            str(result.metrics.iterations),
            str(result.metrics.nodes_generated),
        ]
        if scored:
            cells.append(_or_absent(row.score, "{:.1f}"))
        rows.append(tuple(cells))
    return render_table(headers, tuple(rows))


def render_summary(summary: Summary) -> str:
    rows = tuple(
        (
            row.algorithm,
            row.strategy,
            f"{row.successes}/{row.runs}",
            str(row.deadlocks),
            render_stat(row.moves),
            render_stat(row.cost),
            render_stat(row.iterations),
            render_stat(row.nodes_generated),
        )
        for row in summary.rows
    )
    table = render_table(theme.SUMMARY_HEADERS, rows)
    return f"{theme.SUMMARY_LEGEND}\n\n{table}"


def render_highlights(summary: Summary) -> str:
    strategies: dict[str, int] = {}
    for row in summary.rows:
        strategies[row.algorithm] = strategies.get(row.algorithm, 0) + 1
    rows = tuple(
        (
            theme.CRITERION_LABELS[highlight.criterion],
            _render_winners(highlight.by_mean, strategies),
            _render_winners(highlight.by_median, strategies),
        )
        for highlight in summary.highlights
    )
    table = render_table(theme.HIGHLIGHTS_HEADERS, rows)
    return f"{theme.HIGHLIGHTS_LEGEND}\n\n{table}"


def _render_winners(winners: tuple[SummaryRow, ...], strategies: dict[str, int]) -> str:
    grouped: dict[str, list[str]] = {}
    for row in winners:
        grouped.setdefault(row.algorithm, []).append(row.strategy)
    return "; ".join(
        f"{algorithm} {theme.ALL_STRATEGIES}"
        if len(names) == strategies[algorithm]
        else f"{algorithm} ({', '.join(names)})"
        for algorithm, names in grouped.items()
    )


def render_stat(stat: Stat | None) -> str:
    if stat is None:
        return theme.ABSENT
    return f"{stat.mean:.2f} / {stat.median:g}"


def render_box(title: str, lines: tuple[str, ...]) -> str:
    # As linhas chegam já quebradas por `_wrap_row` para caber em
    # MAX_BOX_WIDTH; a caixa só passa disso se o título não couber.
    content_width = max((len(line) for line in lines), default=0)
    width = max(content_width + 2, len(title) + 6, theme.MIN_BOX_WIDTH)

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
    details: list[tuple[str, str]] = []
    if report.show_states and result.solution_path:
        drawings = "\n\n".join(
            state_render.render_pegs(node.state) for node in result.solution_path
        )
        details.append((theme.STATES_HEADER, drawings))
    if report.show_tree:
        details.append((theme.TREE_HEADER, tree_render.render_tree(result.trace)))
    if report.show_trace:
        details.append((theme.TRACE_HEADER, trace_render.render_trace(result.trace)))
    return [
        part for title, body in details for part in ("", render_section(title, body))
    ]


def _or_absent(value: float | None, template: str = "{}") -> str:
    return theme.ABSENT if value is None else template.format(value)


def write(text: str, stream: TextIO | None = None) -> None:
    target = sys.stdout if stream is None else stream
    target.write(f"{text}\n")


def write_error(text: str) -> None:
    sys.stderr.write(f"{text}\n")
