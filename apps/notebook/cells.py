from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

NBFORMAT = 4
NBFORMAT_MINOR = 4


@dataclass(frozen=True, slots=True)
class Cell:
    kind: str
    source: str
    hidden: bool = False

    def to_json(self) -> dict[str, object]:
        lines = self.source.strip("\n").splitlines(keepends=True)
        if self.kind == "markdown":
            return {"cell_type": "markdown", "metadata": {}, "source": lines}
        metadata: dict[str, object] = {}
        if self.hidden:
            metadata = {"cellView": "form", "jupyter": {"source_hidden": True}}
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": metadata,
            "outputs": [],
            "source": lines,
        }


def markdown(source: str) -> Cell:
    return Cell("markdown", source)


def code(source: str, *, hidden: bool = False) -> Cell:
    return Cell("code", source, hidden=hidden)


@dataclass(frozen=True, slots=True)
class Notebook:
    filename: str
    title: str
    cells: tuple[Cell, ...] = field(default_factory=tuple)

    def to_json(self) -> dict[str, object]:
        return {
            "cells": [cell.to_json() for cell in self.cells],
            "metadata": {
                "colab": {"name": self.filename, "toc_visible": True},
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {"name": "python"},
            },
            "nbformat": NBFORMAT,
            "nbformat_minor": NBFORMAT_MINOR,
        }

    def render(self) -> str:
        return json.dumps(self.to_json(), ensure_ascii=False, indent=1) + "\n"

    def write(self, directory: Path) -> Path:
        target = directory / self.filename
        target.write_text(self.render(), encoding="utf-8")
        return target
