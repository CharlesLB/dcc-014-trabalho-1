from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from cells import Cell, code

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

ENTRY_POINT = "main.py"


@dataclass(frozen=True, slots=True)
class ProjectFile:
    path: str
    text: str

    @property
    def module(self) -> str:
        return Path(self.path).relative_to(SOURCE_DIR).with_suffix("").as_posix()


class UncoveredModuleError(Exception):
    def __init__(self, paths: Iterable[str]) -> None:
        super().__init__(f"modules outside FOLDERS: {sorted(paths)}")


def files_in(folder: str) -> tuple[ProjectFile, ...]:
    directory = PROJECT_ROOT / SOURCE_DIR / folder
    return tuple(_read(path) for path in sorted(directory.glob("*.py")))


def entry_point() -> ProjectFile:
    return _read(PROJECT_ROOT / ENTRY_POINT)


def all_files() -> tuple[ProjectFile, ...]:
    files = tuple(item for folder in FOLDERS for item in files_in(folder))
    listed = {item.path for item in files}
    on_disk = {
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in (PROJECT_ROOT / SOURCE_DIR).rglob("*.py")
    }
    if listed != on_disk:
        raise UncoveredModuleError(on_disk - listed)
    return (*files, entry_point())


def writefile_cell(item: ProjectFile) -> Cell:
    return code(f"%%writefile {item.path}\n{item.text}")


def install_cell(title: str, files: Iterable[ProjectFile]) -> Cell:
    entries = "\n".join(f"    {item.path!r}: {item.text!r}," for item in files)
    return code(
        f"""#@title {title}
import sys
from pathlib import Path

FILES = {{
{entries}
}}

for name, text in FILES.items():
    target = Path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")

if str(Path("{SOURCE_DIR}").resolve()) not in sys.path:
    sys.path.insert(0, str(Path("{SOURCE_DIR}").resolve()))
print(f"{{len(FILES)}} arquivos gravados em {{Path.cwd()}}")
""",
        hidden=True,
    )


def _read(path: Path) -> ProjectFile:
    return ProjectFile(
        path=path.relative_to(PROJECT_ROOT).as_posix(),
        text=path.read_text(encoding="utf-8"),
    )
