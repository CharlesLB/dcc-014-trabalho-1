from __future__ import annotations

from core.domain.state import CAPACITIES, Peg, State
from libs.outputs import theme


def render_inline(state: State) -> str:
    parts = []
    for peg in Peg:
        stack = state[peg]
        content = (
            ",".join(theme.disk_symbol(disk) for disk in stack)
            if stack
            else theme.EMPTY_PEG
        )
        parts.append(f"{theme.PEG_NAMES[peg]}[{content}]")
    return " ".join(parts)


def render_pegs(state: State) -> str:
    height = max(CAPACITIES.values())
    columns = [_column(state, peg, height) for peg in Peg]
    width = max(len(cell) for column in columns for cell in column)

    lines = [
        "  ".join(column[level].center(width) for column in columns).rstrip()
        for level in range(height)
    ]
    footer = "  ".join(
        f"{theme.PEG_NAMES[peg]}({CAPACITIES[peg]})".center(width) for peg in Peg
    )
    lines.append(footer.rstrip())
    return "\n".join(lines)


def _column(state: State, peg: Peg, height: int) -> list[str]:
    stack = state[peg]
    cells = ["" for _ in range(height - len(stack))]
    cells.extend(f"[{theme.disk_name(disk)}]" for disk in reversed(stack))
    capacity = CAPACITIES[peg]
    for level in range(height):
        if not cells[level] and height - level <= capacity:
            cells[level] = "|"
    return cells
