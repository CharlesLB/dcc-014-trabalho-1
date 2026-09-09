from __future__ import annotations

import ast
import importlib
import inspect
from collections.abc import Iterator, Mapping
from pathlib import Path

import pytest

from core.algorithms.domain.registry import ALGORITHMS
from core.rules.strategies.domain.registry import STRATEGIES

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"

PACKAGES = ("core", "libs", "runner", "config")

FORBIDDEN_BY_LAYER: dict[str, frozenset[str]] = {
    "core": frozenset({"runner", "libs"}),
}

EDGE_LIBRARIES = ("libs.inputs", "libs.outputs", "libs.ranking")


def _modules() -> Iterator[Path]:
    for package in PACKAGES:
        yield from sorted((SOURCE_ROOT / package).rglob("*.py"))


def _imported_modules(module: Path) -> set[str]:
    tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
    imported: set[str] = set()
    for statement in ast.walk(tree):
        if isinstance(statement, ast.Import):
            imported.update(alias.name for alias in statement.names)
        elif isinstance(statement, ast.ImportFrom) and statement.module:
            imported.add(statement.module)
    return imported


def _roots(module: Path) -> set[str]:
    return {name.split(".")[0] for name in _imported_modules(module)}


def _dotted_name(module: Path) -> str:
    return ".".join(module.relative_to(SOURCE_ROOT).with_suffix("").parts)


def _direct_children(package: str) -> tuple[Path, ...]:
    return tuple(sorted((SOURCE_ROOT / Path(package)).glob("*.py")))


MODULES = tuple(_modules())
MODULE_IDS = tuple(str(module.relative_to(PROJECT_ROOT)) for module in MODULES)


def test_the_project_has_modules_to_inspect() -> None:
    assert MODULES


def test_no_init_files_remain() -> None:
    assert not list(SOURCE_ROOT.rglob("__init__.py"))


@pytest.mark.parametrize("module", MODULES, ids=MODULE_IDS)
def test_layer_does_not_import_forbidden_packages(module: Path) -> None:
    layer = module.relative_to(SOURCE_ROOT).parts[0]
    assert not _roots(module) & FORBIDDEN_BY_LAYER.get(layer, frozenset())


def test_rules_imports_nothing_but_itself() -> None:
    for module in MODULES:
        if module.relative_to(SOURCE_ROOT).parts[:2] != ("core", "rules"):
            continue
        outside = {
            name
            for name in _imported_modules(module)
            if name.split(".")[0] in PACKAGES and not name.startswith("core.rules")
        }
        assert not outside, f"{module} importa {sorted(outside)}"


def test_core_does_not_import_the_layers_that_consume_it() -> None:
    for module in MODULES:
        if module.relative_to(SOURCE_ROOT).parts[0] != "core":
            continue
        assert not _roots(module) & {"libs", "runner"}


def test_search_tree_does_not_depend_on_the_algorithms() -> None:
    for module in _direct_children("core/search_tree"):
        assert not any(
            name.startswith("core.algorithms") for name in _imported_modules(module)
        )


def test_no_package_is_named_io() -> None:
    assert not (SOURCE_ROOT / "io").exists()
    assert all(module.parent.name != "io" for module in MODULES)


def test_no_print_outside_outputs() -> None:
    for module in MODULES:
        if module.relative_to(SOURCE_ROOT).parts[:2] == ("libs", "outputs"):
            continue
        tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ]
        assert not calls, f"print encontrado em {module}"


def test_runner_is_the_only_layer_that_knows_every_other() -> None:
    for module in MODULES:
        layer = module.relative_to(SOURCE_ROOT).parts[0]
        imported = _imported_modules(module)
        touches_all = all(
            any(name.startswith(library) for name in imported)
            for library in EDGE_LIBRARIES
        )
        assert not touches_all or layer == "runner", f"{module} conhece todas as libs"


@pytest.mark.parametrize(
    ("package", "registry"),
    [
        ("core/algorithms", ALGORITHMS),
        ("core/rules/strategies", STRATEGIES),
    ],
    ids=["algorithms", "strategies"],
)
def test_plural_package_holds_only_registered_implementations(
    package: str, registry: Mapping[str, object]
) -> None:
    registered = {
        value if isinstance(value, type) else type(value) for value in registry.values()
    }
    children = _direct_children(package)
    assert children
    for module in children:
        namespace = importlib.import_module(_dotted_name(module))
        declared = {
            member
            for _, member in inspect.getmembers(namespace, inspect.isclass)
            if member.__module__ == namespace.__name__
        }
        assert declared & registered, f"{module} nao declara implementacao registrada"
