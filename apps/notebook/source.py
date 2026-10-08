from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from cells import Cell, code, ignore, markdown

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
    "core/algorithms/irrevocable",
    "core/algorithms/backtracking",
    "core/algorithms/breadth_first",
    "core/algorithms/ordered",
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


def install_cell(title: str, files: Iterable[ProjectFile]) -> Cell:
    entries = "\n".join(f"    {item.path!r}: {item.text!r}," for item in files)
    return code(
        f"""#@title {title}
from pathlib import Path

FILES = {{
{entries}
}}
for name, text in FILES.items():
    Path(name).write_text(text, encoding="utf-8")""",
        hidden=True,
    )


def setup_cells(
    *, shown: Iterable[str], extras: Iterable[Cell] = ()
) -> tuple[Cell, ...]:
    files = all_files()
    on_slides = {f"{SOURCE_DIR}/{path}" for path in shown}
    cells: list[Cell] = [
        ignore(
            markdown(
                "# Setup\n\nRode esta seção inteira antes do resto do notebook. Nada "
                "aqui aparece nos slides: são os módulos de apoio do projeto e as "
                "funções que desenham tabelas e gráficos."
            )
        ),
        ignore(
            code(
                f"""#@title Prepara as pastas
import sys
from pathlib import Path

for folder in {FOLDERS!r}:
    Path("{SOURCE_DIR}", folder).mkdir(parents=True, exist_ok=True)
if str(Path("{SOURCE_DIR}").resolve()) not in sys.path:
    sys.path.insert(0, str(Path("{SOURCE_DIR}").resolve()))""",
                hidden=True,
            )
        ),
    ]
    for folder in FOLDERS:
        support = [item for item in files_in(folder) if item.path not in on_slides]
        if not support:
            continue
        cells.append(ignore(markdown(f"## {folder}/")))
        cells.extend(ignore(writefile_cell(item)) for item in support)
    cells.append(ignore(markdown("## Módulos dos slides")))
    cells.append(
        ignore(
            install_cell(
                "Grava os módulos que aparecem nos slides (o código de cada um está no ponto do slide)",
                (item for item in files if item.path in on_slides),
            )
        )
    )
    extra = tuple(extras)
    if extra:
        cells.append(ignore(markdown("## Apresentação")))
        cells.extend(ignore(cell) for cell in extra)
    return tuple(cells)


def _read(path: Path) -> ProjectFile:
    return ProjectFile(
        path=path.relative_to(PROJECT_ROOT).as_posix(),
        text=path.read_text(encoding="utf-8"),
    )
