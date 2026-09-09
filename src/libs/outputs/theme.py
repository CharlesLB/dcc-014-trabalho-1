from __future__ import annotations

from collections.abc import Mapping
from typing import Final

from core.rules.domain.base import Disk, Peg
from core.search_tree.outcome import Outcome
from core.search_tree.trace import TraceEvent

DISK_NAMES: Final[Mapping[Disk, str]] = {
    Disk.GREEN: "VERDE",
    Disk.RED: "VERMELHO",
    Disk.BLUE: "AZUL",
}

DISK_SYMBOLS: Final[Mapping[Disk, str]] = {
    Disk.GREEN: "V",
    Disk.RED: "R",
    Disk.BLUE: "A",
}

PEG_NAMES: Final[Mapping[Peg, str]] = {
    Peg.H1: "H1",
    Peg.H2: "H2",
    Peg.H3: "H3",
}

OUTCOME_LABELS: Final[Mapping[Outcome, str]] = {
    Outcome.SUCCESS: "SUCESSO",
    Outcome.DEADLOCK: "IMPASSE",
    Outcome.CUTOFF: "LIMITE",
    Outcome.FAILURE: "FALHA",
}

EVENT_LABELS: Final[Mapping[TraceEvent, str]] = {
    TraceEvent.ROOT: "raiz",
    TraceEvent.VISIT: "visita",
    TraceEvent.GENERATE: "gera",
    TraceEvent.PRUNE: "poda",
    TraceEvent.GOAL: "objetivo",
    TraceEvent.DEADLOCK: "impasse",
    TraceEvent.BACKTRACK: "retrocesso",
    TraceEvent.CUTOFF: "limite",
    TraceEvent.EXHAUSTED: "esgotado",
}

REPORT_LABELS: Final[Mapping[str, str]] = {
    "outcome": "Desfecho",
    "moves": "Movimentos",
    "path": "Caminho",
    "iterations": "Iterações",
    "nodes_generated": "Nós gerados",
    "nodes_visited": "Nós visitados",
    "rules_tested": "Regras testadas",
    "backtracks": "Retrocessos",
    "deadlocks": "Impasses",
    "max_depth": "Profundidade máx",
    "elapsed": "Tempo (ms)",
}

LEADERBOARD_HEADERS: Final[tuple[str, ...]] = (
    "#",
    "ALGORITMO",
    "ESTRATÉGIA",
    "DESFECHO",
    "MOV",
    "ITER",
    "GERADOS",
    "ESCORE",
)

SUMMARY_HEADERS: Final[tuple[str, ...]] = (
    "ALGORITMO",
    "ESTRATÉGIA",
    "SUCESSOS",
    "IMPASSES",
    "MOV. MÉDIO",
    "ITER. MÉDIO",
)

TREE_HEADER: Final = "Árvore de busca"
TRACE_HEADER: Final = "Passo a passo"
STATES_HEADER: Final = "Estados do caminho solução"
LEADERBOARD_HEADER: Final = "Placar"
SUMMARY_HEADER: Final = "Resumo consolidado"
PROBLEM_HEADER: Final = "PROBLEMA"
INITIAL_STATE_HEADER: Final = "Posição inicial"
GOAL_STATE_HEADER: Final = "Objetivo"

ABSENT: Final = "—"
ARROW: Final = " → "
EMPTY_PEG: Final = "·"

BOX_TOP_LEFT: Final = "╭"
BOX_TOP_RIGHT: Final = "╮"
BOX_BOTTOM_LEFT: Final = "╰"
BOX_BOTTOM_RIGHT: Final = "╯"
BOX_HORIZONTAL: Final = "─"
BOX_VERTICAL: Final = "│"

TREE_BRANCH: Final = "├── "
TREE_LAST_BRANCH: Final = "└── "
TREE_TRUNK: Final = "│   "
TREE_GAP: Final = "    "

GRAPH_FONT: Final = "Helvetica"
GRAPH_MONO_FONT: Final = "monospace"
GRAPH_MOVES_LABEL: Final = "movimentos"
GRAPH_ROOT_FILL: Final = "#dbe9ff"
GRAPH_GOAL_FILL: Final = "#c6f0c6"
GRAPH_DEADLOCK_FILL: Final = "#f7c6c6"
GRAPH_VISITED_FILL: Final = "#ffffff"
GRAPH_GENERATED_FILL: Final = "#eeeeee"
GRAPH_NODE_COLOR: Final = "#333333"
GRAPH_PATH_COLOR: Final = "#1a56b8"
GRAPH_PRUNED_COLOR: Final = "#999999"
GRAPH_PATH_WIDTH: Final = 2.5

LABEL_WIDTH: Final = 18
MIN_BOX_WIDTH: Final = 56
MAX_BOX_WIDTH: Final = 76


def disk_symbol(disk: Disk) -> str:
    return DISK_SYMBOLS[disk]


def disk_name(disk: Disk) -> str:
    return DISK_NAMES[disk]


def outcome_label(outcome: Outcome) -> str:
    return OUTCOME_LABELS[outcome]


def event_label(event: TraceEvent) -> str:
    return EVENT_LABELS[event]
