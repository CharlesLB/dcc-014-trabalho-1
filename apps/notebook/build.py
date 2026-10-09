from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from cells import Notebook
from pages import analysis
from pages.algorithm import ALGORITHM_SECTIONS, flowcharts, section, slide_modules
from pages.common import NOTEBOOK, TITLE, header, members, style_cell, view_helpers
from source import setup_cells

OUTPUT_DIR = Path(__file__).resolve().parent / "notebooks"


def notebooks() -> tuple[Notebook, ...]:
    cells = (
        header(ALGORITHM_SECTIONS),
        *setup_cells(
            shown=slide_modules(),
            extras=(
                style_cell(ALGORITHM_SECTIONS),
                view_helpers(ALGORITHM_SECTIONS),
                analysis.PLOT_HELPERS,
                flowcharts(),
            ),
        ),
        *(
            cell
            for index, spec in enumerate(ALGORITHM_SECTIONS, start=1)
            for cell in section(spec, index, first=index == 1)
        ),
        *analysis.section(len(ALGORITHM_SECTIONS) + 1),
        members(ALGORITHM_SECTIONS),
    )
    return (Notebook(NOTEBOOK, TITLE, cells),)


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
