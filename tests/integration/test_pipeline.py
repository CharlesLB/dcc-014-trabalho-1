from __future__ import annotations

import json
from pathlib import Path

import pytest

from config import settings
from core.domain.problem import PROBLEM_IDS
from libs.inputs.parser import parse
from libs.inputs.validator import validate
from libs.outputs import theme
from libs.outputs.console import ConsoleFormatter
from libs.outputs.json_writer import JsonFormatter
from runner.cli import main
from runner.pipeline import build_report


def test_report_covers_every_selected_problem() -> None:
    report = build_report(validate(parse(["--all"])))
    assert tuple(entry.problem_id for entry in report.problems) == PROBLEM_IDS


def test_report_carries_the_display_flags() -> None:
    report = build_report(validate(parse(["--show-tree", "--show-states"])))
    assert report.show_tree
    assert report.show_states
    assert not report.show_trace


def test_console_rendering_mentions_every_execution() -> None:
    request = validate(parse(["--all"]))
    text = ConsoleFormatter().render(build_report(request))
    for problem_id in request.problem_ids:
        assert problem_id in text


def test_json_rendering_matches_the_execution_count() -> None:
    request = validate(parse(["--all"]))
    payload = json.loads(JsonFormatter().render(build_report(request)))
    total = sum(len(entry["execucoes"]) for entry in payload["problemas"])
    assert total == request.execution_count


def test_cli_writes_the_report_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--problem", PROBLEM_IDS[0]]) == settings.EXIT_OK
    assert theme.LEADERBOARD_HEADER in capsys.readouterr().out


def test_cli_lists_the_catalogues(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list"]) == settings.EXIT_OK
    output = capsys.readouterr().out
    assert settings.LIST_PROBLEMS_HEADER in output
    assert settings.LIST_ALGORITHMS_HEADER in output


def test_cli_prints_the_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--help"]) == settings.EXIT_OK
    assert settings.USAGE_PREFIX in capsys.readouterr().out


def test_cli_with_no_arguments_runs_everything(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main() == settings.EXIT_OK
    assert capsys.readouterr().out


def test_cli_writes_a_file_and_reports_the_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "saida.json"
    assert main(["--format", "json", "--output", str(target)]) == settings.EXIT_OK
    assert settings.OUTPUT_WRITTEN.format(path=target) in capsys.readouterr().out
    assert json.loads(target.read_text(encoding="utf-8"))["problemas"]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--algorithm", "astar"],
        ["--strategy", "aleatoria"],
        ["--problem", "P999"],
        ["--format", "xml"],
        ["--rank-mode", "elo"],
        ["--order", "R1,R2"],
        ["--max-iterations", "zero"],
        ["--flag-inexistente"],
    ],
)
def test_cli_rejects_invalid_input(
    arguments: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(arguments) == settings.EXIT_INVALID_INPUT
    assert settings.ERROR_PREFIX in capsys.readouterr().err


def test_cli_honours_the_score_rank_mode(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--rank-mode", "score"]) == settings.EXIT_OK
    assert "ESCORE" in capsys.readouterr().out


def test_cli_renders_the_optional_sections(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--show-tree", "--show-trace", "--show-states", "--verbose"]) == (
        settings.EXIT_OK
    )
    output = capsys.readouterr().out
    assert theme.TREE_HEADER in output
    assert theme.TRACE_HEADER in output
    assert theme.STATES_HEADER in output
