from __future__ import annotations

import json
from pathlib import Path

from core.algorithms.backtracking import BacktrackingSearch
from core.domain.problem import Problem
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.tree import SearchTree
from libs.outputs import theme
from libs.outputs.formatter import ProblemReport, Report
from libs.outputs.json_writer import JsonFormatter, write_file


def _report(problem: Problem) -> Report:
    result = BacktrackingSearch(SearchTree(), STRATEGIES["ascending"]).solve(problem)
    return Report(
        problems=(
            ProblemReport(
                problem_id=problem.id,
                initial_state=problem.initial,
                goal_state=problem.goal,
                results=(result,),
            ),
        )
    )


def test_output_is_valid_json(problems: tuple[Problem, ...]) -> None:
    payload = json.loads(JsonFormatter().render(_report(problems[0])))
    assert payload["problemas"][0]["id"] == problems[0].id


def test_states_are_named_by_peg_and_disk(problems: tuple[Problem, ...]) -> None:
    payload = json.loads(JsonFormatter().render(_report(problems[0])))
    initial = payload["problemas"][0]["estado_inicial"]
    assert set(initial) == set(theme.PEG_NAMES.values())
    assert all(
        disk in theme.DISK_NAMES.values()
        for stack in initial.values()
        for disk in stack
    )


def test_metrics_are_exported(problems: tuple[Problem, ...]) -> None:
    payload = json.loads(JsonFormatter().render(_report(problems[0])))
    metrics = payload["problemas"][0]["execucoes"][0]["metricas"]
    assert set(metrics) == {
        "iteracoes",
        "nos_gerados",
        "nos_visitados",
        "regras_testadas",
        "retrocessos",
        "impasses",
        "profundidade_maxima",
        "tempo_ms",
    }


def test_write_file_creates_missing_directories(
    problems: tuple[Problem, ...], tmp_path: Path
) -> None:
    target = tmp_path / "nested" / "report.json"
    write_file(target, JsonFormatter().render(_report(problems[0])))
    assert json.loads(target.read_text(encoding="utf-8"))["problemas"]
