from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from config import settings
from config.logging import configure_logging
from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.domain.problem import PROBLEMS
from core.rules.domain.exceptions import InvalidRuleOrderError
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from libs.inputs import parser, validator
from libs.inputs.exceptions import (
    InputError,
    InvalidArgumentError,
    UnknownSelectionError,
)
from libs.inputs.selection import ExecutionRequest
from libs.outputs import console, graph_writer, state_render
from libs.outputs.console import ConsoleFormatter
from libs.outputs.formatter import Formatter, Report
from libs.outputs.json_writer import JsonFormatter, write_file
from runner.pipeline import build_report

_FORMATTERS: dict[str, Formatter] = {
    ConsoleFormatter.name: ConsoleFormatter(),
    JsonFormatter.name: JsonFormatter(),
}


def main(argv: Sequence[str] | None = None) -> int:
    arguments = [] if argv is None else list(argv)
    try:
        request = validator.validate(parser.parse(arguments))
    except (InputError, InvalidRuleOrderError) as error:
        console.write_error(_error_message(error))
        console.write_error(settings.ERROR_HINT)
        return settings.EXIT_INVALID_INPUT

    configure_logging(verbose=request.verbose)

    if request.show_help:
        console.write(parser.help_text())
        return settings.EXIT_OK

    if request.list_only:
        console.write(_render_catalogues())
        return settings.EXIT_OK

    report = build_report(request)
    _emit(report, request)
    if request.svg_dir is not None:
        _write_graphs(report, request.svg_dir)
    return settings.EXIT_OK


def _write_graphs(report: Report, directory: Path) -> None:
    written = graph_writer.write_graphs(report, directory)
    console.write(settings.GRAPHS_WRITTEN.format(count=len(written), path=directory))
    if not graph_writer.graphviz_available():
        console.write_error(settings.GRAPHVIZ_MISSING)


def _emit(report: Report, request: ExecutionRequest) -> None:
    text = _FORMATTERS[request.output_format].render(report)
    if request.output_path is None:
        console.write(text)
        return
    write_file(request.output_path, text)
    console.write(settings.OUTPUT_WRITTEN.format(path=request.output_path))


def _render_catalogues() -> str:
    problems = "\n".join(
        f"  {problem.id}  {state_render.render_inline(problem.goal)}"
        for problem in PROBLEMS
    )
    return "\n\n".join(
        [
            console.render_section(settings.LIST_PROBLEMS_HEADER, problems),
            console.render_section(
                settings.LIST_ALGORITHMS_HEADER,
                "\n".join(f"  {name}" for name in ALGORITHM_NAMES),
            ),
            console.render_section(
                settings.LIST_STRATEGIES_HEADER,
                "\n".join(f"  {name}" for name in STRATEGY_NAMES),
            ),
        ]
    )


def _error_message(error: Exception) -> str:
    match error:
        case UnknownSelectionError():
            detail = settings.ERROR_UNKNOWN_SELECTION.format(
                kind=settings.KIND_LABELS[error.kind],
                name=error.name,
                available=", ".join(error.available),
            )
        case InvalidRuleOrderError():
            detail = settings.ERROR_INVALID_RULE_ORDER.format(reason=error.reason)
        case InvalidArgumentError():
            detail = settings.ERROR_INVALID_ARGUMENT.format(detail=error.detail)
        case _:
            detail = str(error)
    return f"{settings.ERROR_PREFIX} {detail}"
