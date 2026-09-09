from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import NoReturn

from config import settings
from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.domain.problem import PROBLEM_IDS
from core.rules.strategies.custom_order import parse_order
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from libs.inputs.exceptions import InvalidArgumentError
from libs.inputs.selection import ExecutionRequest


class _HelpFormatter(argparse.HelpFormatter):
    def add_usage(
        self,
        usage: str | None,
        actions: Iterable[argparse.Action],
        groups: Iterable[argparse._MutuallyExclusiveGroup],
        prefix: str | None = None,
    ) -> None:
        super().add_usage(usage, actions, groups, settings.USAGE_PREFIX)


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise InvalidArgumentError(message)

    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        raise InvalidArgumentError(message or "")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog=settings.PROGRAM_NAME,
        description=settings.DESCRIPTION,
        epilog=settings.EPILOG,
        add_help=False,
        formatter_class=_HelpFormatter,
    )
    group = parser.add_argument_group(settings.OPTIONS_TITLE)
    group.add_argument("-h", "--help", action="store_true", help=settings.HELP_HELP)
    group.add_argument("--problem", action="append", help=settings.HELP_PROBLEM)
    group.add_argument("--algorithm", action="append", help=settings.HELP_ALGORITHM)
    group.add_argument("--strategy", action="append", help=settings.HELP_STRATEGY)
    group.add_argument("--all", action="store_true", help=settings.HELP_ALL)
    group.add_argument("--order", help=settings.HELP_ORDER)
    group.add_argument("--show-tree", action="store_true", help=settings.HELP_SHOW_TREE)
    group.add_argument(
        "--show-trace", action="store_true", help=settings.HELP_SHOW_TRACE
    )
    group.add_argument(
        "--show-states", action="store_true", help=settings.HELP_SHOW_STATES
    )
    group.add_argument(
        "--format", default=settings.DEFAULT_OUTPUT_FORMAT, help=settings.HELP_FORMAT
    )
    group.add_argument("--output", help=settings.HELP_OUTPUT)
    group.add_argument("--svg-dir", help=settings.HELP_SVG_DIR)
    group.add_argument(
        "--rank-mode", default=settings.DEFAULT_RANK_MODE, help=settings.HELP_RANK_MODE
    )
    group.add_argument(
        "--max-iterations",
        default=str(settings.MAX_ITERATIONS),
        help=settings.HELP_MAX_ITERATIONS,
    )
    group.add_argument("--seed", help=settings.HELP_SEED)
    group.add_argument("--list", action="store_true", help=settings.HELP_LIST)
    group.add_argument("--verbose", action="store_true", help=settings.HELP_VERBOSE)
    return parser


def help_text() -> str:
    return build_parser().format_help()


def parse(argv: Sequence[str]) -> ExecutionRequest:
    namespace = build_parser().parse_args(list(argv))

    select_all: bool = namespace.all
    problems = _selected(namespace.problem, PROBLEM_IDS, select_all, upper=True)
    algorithms = _selected(namespace.algorithm, ALGORITHM_NAMES, select_all)
    strategies = _selected(namespace.strategy, STRATEGY_NAMES, select_all)
    order = parse_order(namespace.order) if namespace.order else None

    return ExecutionRequest(
        problem_ids=problems,
        algorithm_names=algorithms,
        strategy_names=strategies,
        custom_order=order,
        show_tree=namespace.show_tree,
        show_trace=namespace.show_trace,
        show_states=namespace.show_states,
        output_format=namespace.format.lower(),
        rank_mode=namespace.rank_mode.lower(),
        max_iterations=_positive_int("--max-iterations", namespace.max_iterations),
        output_path=Path(namespace.output) if namespace.output else None,
        svg_dir=Path(namespace.svg_dir) if namespace.svg_dir else None,
        list_only=namespace.list,
        show_help=namespace.help,
        verbose=namespace.verbose,
        seed=None
        if namespace.seed is None
        else _positive_int("--seed", namespace.seed),
    )


def _selected(
    raw: list[str] | None,
    available: tuple[str, ...],
    select_all: bool,
    *,
    upper: bool = False,
) -> tuple[str, ...]:
    if select_all or not raw:
        return available
    names = [
        token.strip().upper() if upper else token.strip().lower()
        for entry in raw
        for token in entry.split(",")
        if token.strip()
    ]
    return tuple(dict.fromkeys(names))


def _positive_int(flag: str, raw: str) -> int:
    try:
        value = int(raw)
    except ValueError:
        raise InvalidArgumentError(f"{flag}={raw!r}") from None
    if value <= 0:
        raise InvalidArgumentError(f"{flag}={raw!r}")
    return value
