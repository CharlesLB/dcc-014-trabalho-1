from __future__ import annotations

from dataclasses import dataclass

from cells import Cell, code, markdown

REPOSITORY = "CharlesLB/dcc-014-trabalho-1"
BRANCH = "main"
NOTEBOOK_DIR = "apps/notebook/notebooks"
COLAB_BASE = f"https://colab.research.google.com/github/{REPOSITORY}/blob/{BRANCH}/{NOTEBOOK_DIR}"
COLAB_BADGE = "https://colab.research.google.com/assets/colab-badge.svg"


@dataclass(frozen=True, slots=True)
class Page:
    filename: str
    title: str


PROJECT = Page("00_projeto.ipynb", "Projeto: problema, regras e motor de busca")
IRREVOCABLE = Page("01_busca_irrevogavel.ipynb", "Busca irrevogável")
BACKTRACKING = Page("02_backtracking.ipynb", "Backtracking")
BREADTH_FIRST = Page("03_busca_em_largura.ipynb", "Busca em largura")
ORDERED = Page("04_busca_ordenada.ipynb", "Busca ordenada")
ANALYSIS = Page("05_analise.ipynb", "Gráficos e análise")

PAGES: tuple[Page, ...] = (
    PROJECT,
    IRREVOCABLE,
    BACKTRACKING,
    BREADTH_FIRST,
    ORDERED,
    ANALYSIS,
)


def header(page: Page, intro: str) -> Cell:
    navigation = " · ".join(
        f"**{item.title}**"
        if item == page
        else f"[{item.title}]({COLAB_BASE}/{item.filename})"
        for item in PAGES
    )
    return markdown(
        f"""# Torre de Londres · {page.title}

[![Abrir no Colab]({COLAB_BADGE})]({COLAB_BASE}/{page.filename})

DCC014 Inteligência Artificial · UFJF · Trabalho 1 · Grupo 5

Páginas: {navigation}

{intro}"""
    )


def setup_note(*, own_module: str | None = None) -> Cell:
    if own_module is None:
        detail = "Ela grava todo o `src/` do repositório"
    else:
        detail = (
            "Ela grava todo o `src/` do repositório, menos "
            f"`{own_module}`, que aparece por inteiro logo abaixo"
        )
    return markdown(
        f"""## Preparação

Rode a célula a seguir antes de qualquer outra. {detail}, nos mesmos caminhos, e põe `src/` no `sys.path`. A página roda sozinha: não depende de outra página nem de clonar o repositório. Para ver o código de cada pasta, abra a página [{PROJECT.title}]({COLAB_BASE}/{PROJECT.filename})."""
    )


VIEW_HELPERS = code(
    """#@title Funções de apresentação
import shutil
import subprocess

import pandas as pd
from IPython.display import SVG, display

from libs.outputs import dot_render, state_render, theme, trace_render, tree_render

LABELS = theme.REPORT_LABELS


def metrics_table(results):
    rows = []
    for result in results:
        metrics = result.metrics
        rows.append(
            {
                "Estratégia": result.strategy,
                LABELS["outcome"]: theme.outcome_label(result.outcome),
                LABELS["moves"]: result.solution_length,
                LABELS["cost"]: result.solution_cost,
                LABELS["path"]: " → ".join(result.applied_rules) or theme.ABSENT,
                LABELS["iterations"]: metrics.iterations,
                LABELS["nodes_generated"]: metrics.nodes_generated,
                LABELS["nodes_visited"]: metrics.nodes_visited,
                LABELS["backtracks"]: metrics.backtracks,
                LABELS["deadlocks"]: metrics.deadlocks,
                LABELS["max_depth"]: metrics.max_depth,
            }
        )
    return (
        pd.DataFrame(rows)
        .set_index("Estratégia")
        .astype({LABELS["moves"]: "Int64", LABELS["cost"]: "Int64"})
    )


def show_path(result):
    for step, node in enumerate(result.solution_path):
        rule = "início" if node.rule is None else f"{node.rule.id}: {node.rule.origin.name} → {node.rule.destination.name}"
        print(f"passo {step}  {rule}  (custo acumulado {node.cost})")
        print(state_render.render_pegs(node.state))
        print()


def show_tree(result):
    source = dot_render.render_dot(result)
    if shutil.which("dot") is None:
        print(tree_render.render_tree(result.trace))
        return
    svg = subprocess.run(
        ["dot", "-Tsvg"], input=source, capture_output=True, text=True, check=True
    ).stdout
    display(SVG(svg))


def show_trace(result):
    print(trace_render.render_trace(result.trace))
""",
    hidden=True,
)
