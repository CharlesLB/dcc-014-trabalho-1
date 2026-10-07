from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from cells import Notebook
from pages import analysis, project
from pages.algorithm import ALGORITHM_PAGES
from pages.algorithm import build as build_algorithm

OUTPUT_DIR = Path(__file__).resolve().parent / "notebooks"


def notebooks() -> tuple[Notebook, ...]:
    return (
        project.build(),
        *(build_algorithm(spec) for spec in ALGORITHM_PAGES),
        analysis.build(),
    )


def stale(directory: Path) -> tuple[str, ...]:
    return tuple(
        item.filename
        for item in notebooks()
        if not (directory / item.filename).exists()
        or (directory / item.filename).read_text(encoding="utf-8") != item.render()
    )


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Gera os notebooks da apresentação a partir de src/."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Só verifica se os notebooks gravados estão em dia com src/.",
    )
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    arguments = parser.parse_args(argv)

    if arguments.check:
        outdated = stale(arguments.output)
        for filename in outdated:
            print(f"desatualizado: {filename}", file=sys.stderr)
        return 1 if outdated else 0

    arguments.output.mkdir(parents=True, exist_ok=True)
    for item in notebooks():
        print(item.write(arguments.output).relative_to(Path.cwd(), walk_up=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
