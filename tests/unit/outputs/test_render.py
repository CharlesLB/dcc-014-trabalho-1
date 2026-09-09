from __future__ import annotations

from core.algorithms.backtracking import BacktrackingSearch
from core.algorithms.irrevocable import IrrevocableSearch
from core.domain.problem import Problem
from core.domain.state import Peg, State
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.result import SearchResult
from core.search_tree.trace import Trace, TraceEvent
from core.search_tree.tree import SearchTree
from libs.outputs import console, state_render, theme, trace_render, tree_render
from libs.outputs.formatter import ProblemReport, Report


def _result(problem: Problem, strategy_name: str = "ascending") -> SearchResult:
    return BacktrackingSearch(SearchTree(), STRATEGIES[strategy_name]).solve(problem)


def _report(
    problem: Problem,
    *,
    show_tree: bool = False,
    show_trace: bool = False,
    show_states: bool = False,
) -> Report:
    return Report(
        problems=(
            ProblemReport(
                problem_id=problem.id,
                initial_state=problem.initial,
                goal_state=problem.goal,
                results=(_result(problem),),
            ),
        ),
        show_tree=show_tree,
        show_trace=show_trace,
        show_states=show_states,
    )


def test_inline_state_names_every_peg(initial_state: State) -> None:
    rendered = state_render.render_inline(initial_state)
    assert all(theme.PEG_NAMES[peg] in rendered for peg in Peg)


def test_inline_state_marks_the_empty_peg(initial_state: State) -> None:
    assert theme.EMPTY_PEG in state_render.render_inline(initial_state)


def test_pegs_drawing_shows_capacities_and_disk_names(initial_state: State) -> None:
    drawing = state_render.render_pegs(initial_state)
    assert "H1(3)" in drawing
    assert "H2(2)" in drawing
    assert "H3(1)" in drawing
    assert theme.DISK_NAMES[initial_state[Peg.H1][-1]] in drawing


def test_pegs_drawing_has_no_trailing_spaces(states: tuple[State, ...]) -> None:
    for state in states:
        for line in state_render.render_pegs(state).splitlines():
            assert line == line.rstrip()


def test_result_box_is_rectangular(problems: tuple[Problem, ...]) -> None:
    lines = console.render_result_box(_result(problems[0])).splitlines()
    assert len({len(line) for line in lines}) == 1


def test_result_box_shows_every_label(problems: tuple[Problem, ...]) -> None:
    box = console.render_result_box(_result(problems[0]))
    assert all(label in box for label in theme.REPORT_LABELS.values())


def test_result_box_reports_the_outcome_in_portuguese(
    problems: tuple[Problem, ...],
) -> None:
    result = _result(problems[0])
    assert theme.outcome_label(result.outcome) in console.render_result_box(result)


def test_deadlock_box_marks_absent_values(problems: tuple[Problem, ...]) -> None:
    result = IrrevocableSearch(SearchTree(), STRATEGIES["descending"]).solve(
        problems[0]
    )
    box = console.render_result_box(result)
    if not result.outcome.is_success:
        assert theme.ABSENT in box


def test_tree_render_shows_every_generated_node(
    problems: tuple[Problem, ...],
) -> None:
    result = _result(problems[0])
    drawing = tree_render.render_tree(result.trace)
    for step in result.trace.of_event(TraceEvent.GENERATE):
        assert f"#{step.node_order}" in drawing


def test_tree_render_marks_the_goal(problems: tuple[Problem, ...]) -> None:
    result = _result(problems[0])
    assert theme.event_label(TraceEvent.GOAL) in tree_render.render_tree(result.trace)


def test_tree_render_of_an_empty_trace_is_empty() -> None:
    assert tree_render.render_tree(Trace()) == ""


def test_trace_render_has_one_line_per_step(problems: tuple[Problem, ...]) -> None:
    result = _result(problems[0])
    lines = trace_render.render_trace(result.trace).splitlines()
    assert len(lines) == len(result.trace) + 1


def test_trace_render_of_an_empty_trace_keeps_the_header() -> None:
    assert trace_render.render_trace(Trace()).splitlines() == [
        "ITER  EVENTO  NÓ  PROF  REGRA  ESTADO"
    ]


def test_console_report_contains_the_problem_identifier(
    problems: tuple[Problem, ...],
) -> None:
    text = console.ConsoleFormatter().render(_report(problems[0]))
    assert f"{theme.PROBLEM_HEADER} {problems[0].id}" in text


def test_console_report_honours_the_display_flags(
    problems: tuple[Problem, ...],
) -> None:
    plain = console.ConsoleFormatter().render(_report(problems[0]))
    assert theme.TREE_HEADER not in plain

    detailed = console.ConsoleFormatter().render(
        _report(problems[0], show_tree=True, show_trace=True, show_states=True)
    )
    assert theme.TREE_HEADER in detailed
    assert theme.TRACE_HEADER in detailed
    assert theme.STATES_HEADER in detailed
