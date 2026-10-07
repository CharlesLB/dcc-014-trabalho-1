from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from cells import Cell, code, markdown

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = "src"

FOLDERS: tuple[str, ...] = (
    "config",
    "core/rules/domain",
    "core/rules",
    "core/rules/strategies/domain",
    "core/rules/strategies",
    "core/domain",
    "core/search_tree",
    "core/algorithms/domain",
    "core/algorithms",
    "libs/inputs",
    "libs/outputs",
    "libs/ranking",
    "runner",
)


@dataclass(frozen=True, slots=True)
class ProjectFile:
    path: str
    text: str


class UncoveredModuleError(Exception):
    def __init__(self, paths: Iterable[str]) -> None:
        super().__init__(f"modules outside FOLDERS: {sorted(paths)}")


def files_in(folder: str) -> tuple[ProjectFile, ...]:
    directory = PROJECT_ROOT / SOURCE_DIR / folder
    return tuple(_read(path) for path in sorted(directory.glob("*.py")))


def all_files() -> tuple[ProjectFile, ...]:
    files = tuple(item for folder in FOLDERS for item in files_in(folder))
    listed = {item.path for item in files}
    on_disk = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in (PROJECT_ROOT / SOURCE_DIR).rglob("*.py")
    }
    if listed != on_disk:
        raise UncoveredModuleError(on_disk - listed)
    return files


def find(path: str) -> ProjectFile:
    return next(item for item in all_files() if item.path == path)


def writefile_cell(item: ProjectFile) -> Cell:
    return code(f"%%writefile {item.path}\n{item.text}")


def setup_cells(
    *, exclude: str | None = None, extras: Iterable[Cell] = ()
) -> tuple[Cell, ...]:
    all_files()
    cells: list[Cell] = [
        markdown("# Setup\n\nRode esta seção inteira antes do resto da página."),
        code(
            f"""import sys
from pathlib import Path

for folder in {FOLDERS!r}:
    Path("{SOURCE_DIR}", folder).mkdir(parents=True, exist_ok=True)
if str(Path("{SOURCE_DIR}").resolve()) not in sys.path:
    sys.path.insert(0, str(Path("{SOURCE_DIR}").resolve()))"""
        ),
    ]
    for folder in FOLDERS:
        files = [item for item in files_in(folder) if item.path != exclude]
        if not files:
            continue
        cells.append(markdown(f"## {folder}/"))
        cells.extend(writefile_cell(item) for item in files)
    extra = tuple(extras)
    if extra:
        cells.append(markdown("## Apresentação"))
        cells.extend(extra)
    return tuple(cells)


def _read(path: Path) -> ProjectFile:
    return ProjectFile(
        path=path.relative_to(PROJECT_ROOT).as_posix(),
        text=path.read_text(encoding="utf-8"),
    )
