from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from libs.outputs import dot_render
from libs.outputs.formatter import Report

DOT_EXECUTABLE = "dot"


def graphviz_available() -> bool:
    return shutil.which(DOT_EXECUTABLE) is not None


def write_graphs(report: Report, directory: Path) -> tuple[Path, ...]:
    render = graphviz_available()
    written: list[Path] = []
    for entry in report.problems:
        target = directory / entry.problem_id
        target.mkdir(parents=True, exist_ok=True)
        for result in entry.results:
            source = dot_render.render_dot(result)
            stem = target / f"{result.algorithm}_{result.strategy}"
            dot_path = stem.with_suffix(".dot")
            dot_path.write_text(source, encoding="utf-8")
            written.append(dot_path)
            if render:
                written.append(_render_svg(dot_path, stem.with_suffix(".svg")))
    return tuple(written)


def _render_svg(dot_path: Path, svg_path: Path) -> Path:
    subprocess.run(
        [DOT_EXECUTABLE, "-Tsvg", str(dot_path), "-o", str(svg_path)],
        check=True,
        capture_output=True,
    )
    return svg_path
