from __future__ import annotations


def render_table(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> str:
    widths = [
        max([len(header), *(len(row[column]) for row in rows)])
        for column, header in enumerate(headers)
    ]
    return "\n".join(_render_line(line, widths) for line in (headers, *rows))


def _render_line(cells: tuple[str, ...], widths: list[int]) -> str:
    return "  ".join(
        cell.ljust(width) for cell, width in zip(cells, widths, strict=True)
    ).rstrip()
