from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "main.py", *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_list_reports_the_catalogues() -> None:
    completed = _run("--list")
    assert completed.returncode == settings.EXIT_OK
    assert settings.LIST_PROBLEMS_HEADER in completed.stdout
    assert settings.LIST_ALGORITHMS_HEADER in completed.stdout
    assert settings.LIST_STRATEGIES_HEADER in completed.stdout


def test_help_is_written_to_stdout() -> None:
    completed = _run("--help")
    assert completed.returncode == settings.EXIT_OK
    assert settings.USAGE_PREFIX in completed.stdout


@pytest.mark.slow
def test_all_runs_the_complete_matrix() -> None:
    completed = _run("--all")
    assert completed.returncode == settings.EXIT_OK
    assert completed.stdout


def test_single_algorithm_runs() -> None:
    completed = _run("--algorithm", "backtracking")
    assert completed.returncode == settings.EXIT_OK
    assert "backtracking" in completed.stdout


def test_algorithm_and_strategy_run() -> None:
    completed = _run("--algorithm", "irrevocable", "--strategy", "descending")
    assert completed.returncode == settings.EXIT_OK
    assert "irrevocable · descending" in completed.stdout


def test_svg_dir_writes_one_tree_per_execution(tmp_path: Path) -> None:
    completed = _run("--algorithm", "irrevocable", "--svg-dir", str(tmp_path))
    assert completed.returncode == settings.EXIT_OK
    assert str(tmp_path) in completed.stdout
    assert sorted(tmp_path.rglob("*.dot"))


def test_display_flags_add_sections() -> None:
    completed = _run("--algorithm", "backtracking", "--show-tree", "--show-trace")
    assert completed.returncode == settings.EXIT_OK
    assert "Árvore de busca" in completed.stdout
    assert "Passo a passo" in completed.stdout


def test_json_output_is_written_to_a_file(tmp_path: Path) -> None:
    target = tmp_path / "resultados.json"
    completed = _run("--all", "--format", "json", "--output", str(target))
    assert completed.returncode == settings.EXIT_OK
    assert json.loads(target.read_text(encoding="utf-8"))["problemas"]


def test_custom_order_is_accepted() -> None:
    completed = _run("--strategy", "custom", "--order", "R2,R4,R6,R1,R3,R5")
    assert completed.returncode == settings.EXIT_OK


def test_unknown_algorithm_fails_with_a_portuguese_message() -> None:
    completed = _run("--algorithm", "astar")
    assert completed.returncode == settings.EXIT_INVALID_INPUT
    assert settings.KIND_LABELS["algorithm"] in completed.stderr
    assert settings.ERROR_HINT in completed.stderr


def test_invalid_order_fails() -> None:
    completed = _run("--order", "R1,R2")
    assert completed.returncode == settings.EXIT_INVALID_INPUT
    assert settings.ERROR_PREFIX in completed.stderr


def test_running_without_arguments_covers_every_axis() -> None:
    bare = _run()
    explicit = _run("--all")
    assert bare.returncode == settings.EXIT_OK
    assert bare.stdout.count("PROBLEMA") == explicit.stdout.count("PROBLEMA")
