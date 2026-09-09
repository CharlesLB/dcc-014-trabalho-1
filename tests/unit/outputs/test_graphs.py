from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from core.algorithms.backtracking import BacktrackingSearch
from core.algorithms.irrevocable import IrrevocableSearch
from core.domain.problem import Problem
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.metrics import MetricsCollector
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import Trace
from core.search_tree.tree import SearchTree
from libs.outputs import dot_render, graph_writer, theme
from libs.outputs.formatter import ProblemReport, Report


def _solve(problem: Problem, strategy_name: str) -> SearchResult:
    return BacktrackingSearch(SearchTree(), STRATEGIES[strategy_name]).solve(problem)


def _report(problem: Problem, *results: SearchResult) -> Report:
    return Report(
        problems=(
            ProblemReport(
                problem_id=problem.id,
                initial_state=problem.initial,
                goal_state=problem.goal,
                results=results,
            ),
        )
    )


def test_dot_declares_every_generated_node_and_edge(
    problems: tuple[Problem, ...],
) -> None:
    result = _solve(problems[0], "ascending")
    source = dot_render.render_dot(result)
    assert source.startswith("digraph search {")
    assert source.rstrip().endswith("}")
    for order in range(result.metrics.nodes_generated):
        assert f"n{order} [" in source
    assert source.count(" -> n") == result.metrics.nodes_generated - 1


def test_dot_highlights_the_solution_path(problems: tuple[Problem, ...]) -> None:
    result = _solve(problems[0], "ascending")
    source = dot_render.render_dot(result)
    highlighted = [
        line for line in source.splitlines() if theme.GRAPH_PATH_COLOR in line
    ]
    nodes_on_path = len(result.solution_path)
    assert len(highlighted) == nodes_on_path + (nodes_on_path - 1)
    assert theme.GRAPH_GOAL_FILL in source


def test_dot_marks_deadlocks_and_pruned_rules(problems: tuple[Problem, ...]) -> None:
    result = IrrevocableSearch(SearchTree(), STRATEGIES["descending"]).solve(
        problems[0]
    )
    assert result.outcome is Outcome.DEADLOCK
    source = dot_render.render_dot(result)
    assert theme.GRAPH_DEADLOCK_FILL in source
    assert theme.GRAPH_PATH_COLOR not in source
    assert "style=dotted" in source
    assert theme.outcome_label(Outcome.DEADLOCK) in source


def test_dot_of_an_empty_trace_is_empty() -> None:
    result = SearchResult(
        algorithm="x",
        strategy="y",
        problem="P0",
        outcome=Outcome.FAILURE,
        solution_path=(),
        applied_rules=(),
        metrics=MetricsCollector().seal(0.0),
        trace=Trace(),
    )
    assert dot_render.render_dot(result) == ""


def test_writer_always_writes_dot_files(
    problems: tuple[Problem, ...], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    report = _report(problems[0], _solve(problems[0], "ascending"))
    written = graph_writer.write_graphs(report, tmp_path)
    assert written == (tmp_path / problems[0].id / "backtracking_ascending.dot",)
    assert written[0].read_text(encoding="utf-8").startswith("digraph")
    assert not graph_writer.graphviz_available()


@pytest.mark.skipif(not graph_writer.graphviz_available(), reason="Graphviz ausente")
def test_writer_renders_svg_next_to_each_dot(
    problems: tuple[Problem, ...], tmp_path: Path
) -> None:
    report = _report(
        problems[0], _solve(problems[0], "ascending"), _solve(problems[0], "descending")
    )
    written = graph_writer.write_graphs(report, tmp_path)
    assert {path.suffix for path in written} == {".dot", ".svg"}
    assert len(written) == 4
    svg = next(path for path in written if path.suffix == ".svg")
    assert "<svg" in svg.read_text(encoding="utf-8")
