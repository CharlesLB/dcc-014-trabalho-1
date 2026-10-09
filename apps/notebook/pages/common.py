from __future__ import annotations

from collections.abc import Sequence

from cells import IGNORE, Cell, code, markdown
from pages.algorithm import AlgorithmSection

REPOSITORY = "CharlesLB/dcc-014-trabalho-1"
BRANCH = "main"
NOTEBOOK_DIR = "apps/notebook/notebooks"
NOTEBOOK = "torre_de_londres.ipynb"
TITLE = "Torre de Londres"
COLAB_URL = f"https://colab.research.google.com/github/{REPOSITORY}/blob/{BRANCH}/{NOTEBOOK_DIR}/{NOTEBOOK}"
COLAB_BADGE = "https://colab.research.google.com/assets/colab-badge.svg"

CLOSING_SECTIONS = ("Comparação dos algoritmos", "Integrantes")

MEMBERS = (
    ("Charles Lelis Braga", "202035015"),
    ("Darlan Henrique da Costa Silva", "202176038"),
    ("Isaac Dizolele Kapela João", "202376017"),
    ("Fábio do Vale Affonso", "202076021"),
    ("Felipe Iglesias Cordeiro Leite", "202465031AB"),
    ("Rafaela Oliveira de Souza", "202365133C"),
    ("Rian Cesar Quintanilha", "202465080AC"),
    ("Gustavo Dias de Almeida", "202165571C"),
    ("Larissa Rezende Fazza", "202335021"),
    ("Ian Félix Fernandes", "202376007"),
    ("Michel Gomes de Andrade", "201876037"),
)


def _section_titles(sections: Sequence[AlgorithmSection]) -> tuple[str, ...]:
    return (*(spec.title for spec in sections), *CLOSING_SECTIONS)


def header(sections: Sequence[AlgorithmSection]) -> Cell:
    contents = "\n".join(
        f"{index}. {name}" for index, name in enumerate(_section_titles(sections), 1)
    )
    return markdown(
        f"""# {TITLE}

[![Abrir no Colab]({COLAB_BADGE})]({COLAB_URL})

DCC014 Inteligência Artificial · UFJF · Trabalho 1 · Grupo 5 · Profa. Luciana

Resolvedor da Torre de Londres (3 hastes, 3 discos) com {len(sections)} algoritmos de busca sobre o mesmo motor. Cada seção de algoritmo segue a ordem dos slides: o problema, a ideia, o laço e as listas, as regras, a estratégia, a árvore sem poda e com poda, o pseudocódigo com o código do projeto, o caminho solução, os comparativos e a complexidade.

{contents}

Todo o código marcado com **{IGNORE}** está no topo, na seção Setup: os módulos de apoio do projeto e as funções que desenham tabelas, figuras e gráficos. Rode **Ambiente de execução → Executar tudo** e comece a apresentação na seção 1. Dali em diante só aparece o código do projeto que vai para a apresentação (problema, regras, estratégias, heurística, fronteira, motor e algoritmos) e chamadas de uma linha que desenham as tabelas e os gráficos."""
    )


def members(sections: Sequence[AlgorithmSection]) -> Cell:
    rows = "\n".join(f"| {name} | {number} |" for name, number in MEMBERS)
    return markdown(
        f"""# {len(_section_titles(sections))}. Integrantes

| Integrante | Matrícula |
|---|---|
{rows}

DCC014 · Inteligência Artificial · Universidade Federal de Juiz de Fora · Profa. Luciana"""
    )


def style_cell(sections: Sequence[AlgorithmSection]) -> Cell:
    """Cores e estilo dos gráficos. Roda antes das funções de apresentação,
    que já desenham com eles."""
    colors = {spec.name: spec.color for spec in sections}
    return code(
        f"#@title Estilo dos gráficos\n{STYLE_IMPORTS}\nALGORITHM_COLORS = {colors!r}\n{STYLE_BODY}",
        hidden=True,
    )


def view_helpers(sections: Sequence[AlgorithmSection]) -> Cell:
    """As funções de apresentação, com os dados de cada algoritmo vindos das
    seções: rótulo, modo das listas, fronteira e quem entra nos gráficos."""
    data = {
        "ALGORITHM_LABELS": {spec.name: spec.label for spec in sections},
        "LIST_MODES": {spec.name: spec.list_mode for spec in sections},
        "FRONTIERS": {
            spec.name: (
                spec.frontier.removesuffix(".py").replace("/", "."),
                spec.frontier_class,
            )
            for spec in sections
            if spec.frontier and spec.frontier_class
        },
        "HEURISTIC_ALGORITHMS": tuple(
            spec.name for spec in sections if spec.uses_heuristic
        ),
        "CHART_ALGORITHMS": tuple(spec.name for spec in sections if spec.complete),
    }
    assignments = "\n".join(f"{name} = {value!r}" for name, value in data.items())
    return code(
        f"#@title Funções de apresentação\n{VIEW_IMPORTS}\n{assignments}\n{VIEW_BODY}",
        hidden=True,
    )


STYLE_IMPORTS = """import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from core.rules.domain.base import Disk
"""

STYLE_BODY = """STRATEGY_COLORS = {"ascending": "#2a78d6", "descending": "#c87400"}
DISK_COLORS = {Disk.GREEN: "#2e9e44", Disk.RED: "#d63b3b", Disk.BLUE: "#2f6fd6"}
GOAL_COLOR = "#1baf7a"
WIN_COLOR = "#1a8746"
OPTIMUM_COLOR = "#b8b8b4"
LINE_GRAY = "#c5c7cc"
GRID_GRAY = "#e6e6e3"
BLACK = "#0b0b0b"
WHITE = "#ffffff"
INK = "#52514e"
MUTED = "#8a8984"

MATPLOTLIB_VERSION = tuple(int(part) for part in matplotlib.__version__.split(".")[:2])
HORIZONTAL = {"orientation": "horizontal"} if MATPLOTLIB_VERSION >= (3, 10) else {"vert": False}

plt.rcParams.update(
    {
        "figure.dpi": 110,
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "axes.titlesize": 11,
        "axes.titlecolor": BLACK,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID_GRAY,
        "grid.linewidth": 0.8,
        "xtick.color": INK,
        "ytick.color": INK,
        "legend.frameon": False,
    }
)

BOX_STYLE = {
    "patch_artist": True,
    "showmeans": True,
    "medianprops": {"color": BLACK, "linewidth": 1.5},
    "meanprops": {"marker": "D", "markerfacecolor": WHITE, "markeredgecolor": BLACK, "markersize": 5},
    "flierprops": {"marker": "o", "markersize": 3, "markerfacecolor": MUTED, "markeredgecolor": "none"},
    "whiskerprops": {"color": MUTED},
    "capprops": {"color": MUTED},
}"""

VIEW_IMPORTS = """import shutil
import subprocess
from collections import Counter
from functools import cache
from importlib import import_module
from pathlib import Path

import pandas as pd
from IPython.display import SVG, display

from config import settings
from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.domain.heuristic import contributions, misplacement
from core.domain.problem import INITIAL_STATE, get_problem
from core.domain.state_space import all_states, applicable_rules, successors
from core.rules.domain.base import Peg
from core.rules.domain.catalog import INVERSE_RULE_ID, RULE_BY_ID, RULES
from core.rules.moves import MOVE_COST
from core.rules.strategies.domain.registry import STRATEGIES as STRATEGY_REGISTRY
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from core.search_tree.outcome import Outcome
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree
from libs.inputs.selection import ExecutionRequest
from libs.outputs import graph_writer, state_render, theme, trace_render, tree_render
from libs.outputs.console import render_stat
from libs.outputs.formatter import ProblemReport, Report
from runner.pipeline import build_report
"""

VIEW_BODY = """
LABELS = theme.REPORT_LABELS
STRATEGY_LABELS = {"ascending": "crescente", "descending": "decrescente"}
SHORT = {"ascending": "cresc.", "descending": "decr."}
SLIDE_STRATEGIES = tuple(STRATEGY_LABELS)
GRAPH_DIR = Path("data")
P1 = get_problem("P1")
LONG_LIST = 8
LIST_TITLES = {
    "stack": ("TOPO DA PILHA", "PILHA", "RETROCEDIDOS"),
    "single": ("NÓ ATUAL", "ABERTOS", "FECHADOS"),
    "queue": ("SAI DE ABERTOS", "ABERTOS", "FECHADOS"),
    "priority": ("SAI DE ABERTOS", "ABERTOS", "FECHADOS"),
}
SITUATIONS = {0: "bem posicionado", 1: "em outra haste", 2: "na haste certa, mal posicionado"}
compact = state_render.render_compact


def prune_label(prune):
    return "com poda" if prune else "sem poda"


def label(algorithm, strategy, *, short=True, prune=None):
    \"\"\"O nome de uma combinação, igual em todas as tabelas e gráficos.\"\"\"
    names = SHORT if short else STRATEGY_LABELS
    parts = [ALGORITHM_LABELS[algorithm], names[strategy]]
    if prune is not None:
        parts.append(prune_label(prune))
    return " ".join(parts)


def br(value, decimals=0):
    \"\"\"Número no formato brasileiro: 1.234,5.\"\"\"
    return f"{value:,.{decimals}f}".translate(str.maketrans(",.", ".,"))


def heuristic(state, goal=P1.goal):
    return misplacement(state, goal)


def moved_disk(state, rule):
    \"\"\"O disco que a regra tira do topo da origem, por extenso.\"\"\"
    return theme.disk_name(state[rule.origin][-1]).lower()


def run(problem_ids=("P1",), algorithms=ALGORITHM_NAMES, strategies=STRATEGY_NAMES, *, all_goals=False, prune=True, max_iterations=settings.MAX_ITERATIONS):
    return build_report(
        ExecutionRequest(
            problem_ids=tuple(problem_ids),
            algorithm_names=tuple(algorithms),
            strategy_names=tuple(strategies),
            all_goals=all_goals,
            prune=prune,
            max_iterations=max_iterations,
        )
    )


@cache
def solve(algorithm, strategy, prune=True, max_iterations=settings.MAX_ITERATIONS):
    return run(("P1",), (algorithm,), (strategy,), prune=prune, max_iterations=max_iterations).problems[0].results[0]


@cache
def p1_report():
    return run()


@cache
def goals_report():
    return run((), all_goals=True)


def side_by_side(blocks, gap="      "):
    columns = [block.splitlines() for block in blocks]
    height = max(len(lines) for lines in columns)
    columns = [[""] * (height - len(lines)) + lines for lines in columns]
    widths = [max(len(line) for line in lines) for lines in columns]
    return "\\n".join(
        gap.join(lines[row].ljust(width) for lines, width in zip(columns, widths)).rstrip()
        for row in range(height)
    )


def drawing(state, title=""):
    \"\"\"Título, o estado compacto e as hastes desenhadas.\"\"\"
    return f"{title}\\n{compact(state)}\\n\\n{state_render.render_pegs(state)}"


def arrow(text=""):
    return f"\\n\\n\\n  —{text}→" if text else "\\n\\n\\n  ——→"


def show_transition(before, after, *, text="", before_title="", after_title=""):
    print(side_by_side([drawing(before, before_title), arrow(text), drawing(after, after_title)]))


def show_problem(problem=P1):
    show_transition(problem.initial, problem.goal, before_title="INICIAL", after_title=f"OBJETIVO {problem.id}")


def rules_table():
    return pd.DataFrame(
        [
            {
                "Regra": rule.id,
                "Move de": rule.origin.name,
                "Para": rule.destination.name,
                "Inversa": INVERSE_RULE_ID[rule.id],
                "Custo": MOVE_COST,
            }
            for rule in RULES
        ]
    ).set_index("Regra")


def show_rule_example(rule_id="R4", state=INITIAL_STATE):
    rule = RULE_BY_ID[rule_id]
    show_transition(state, rule.apply(state), text=rule.id, before_title="S0")
    print(f"\\nExemplo: {rule.id} em S0 leva o {moved_disk(state, rule)} de {rule.origin.name} para {rule.destination.name}.")


def explain_heuristic(state=INITIAL_STATE, goal=P1.goal):
    show_transition(state, goal, before_title="ESTADO", after_title="OBJETIVO")
    shares = contributions(state, goal)
    rows = [
        {
            "Disco": theme.disk_name(disk).lower(),
            "Está em": f"{peg.name}, altura {height + 1}",
            "Situação": SITUATIONS[shares[disk]],
            "Contribui": shares[disk],
        }
        for peg in Peg
        for height, disk in enumerate(state[peg])
    ]
    terms = " + ".join(str(row["Contribui"]) for row in rows)
    print(f"\\nh = {terms} = {heuristic(state, goal)}")
    return pd.DataFrame(rows).set_index("Disco")


def children_heuristics(state=INITIAL_STATE, goal=P1.goal):
    return pd.DataFrame(
        [
            {"Regra": rule.id, "Filho": compact(rule.apply(state)), "h": heuristic(rule.apply(state), goal)}
            for rule in applicable_rules(state)
        ]
    ).set_index("Regra")


def strategies_table():
    return pd.DataFrame(
        [
            {
                "Estratégia": name,
                "Ordem das regras": "  ".join(rule.id for rule in STRATEGY_REGISTRY[name].order(RULES)),
                "Na linha de comando": f"--strategy {name}",
            }
            for name in STRATEGY_NAMES
        ]
    ).set_index("Estratégia")


def _nodes(result):
    return {
        step.node_order: step
        for step in result.trace
        if step.event in (TraceEvent.ROOT, TraceEvent.GENERATE)
    }


def _names(orders, priorities=None):
    if priorities is None:
        return " ".join(f"S{order}" for order in orders)
    return " ".join(f"S{order}({priorities[order]})" for order in orders)


def _shorten(orders, priorities=None):
    if len(orders) <= LONG_LIST:
        return _names(orders, priorities)
    ordered = sorted(orders)
    if priorities is None and ordered == list(range(ordered[0], ordered[-1] + 1)):
        return f"S{ordered[0]} … S{ordered[-1]}"
    return f"{len(orders)}: {_names(orders[:3], priorities)} …"


def _of(events, kind):
    return [step for step in events if step.event is kind]


def _current(events):
    \"\"\"O nó em que a iteração trabalhou.\"\"\"
    for kind in (TraceEvent.GOAL, TraceEvent.VISIT, TraceEvent.BACKTRACK):
        steps = _of(events, kind)
        if steps:
            return steps[0].node_order
    return _of(events, TraceEvent.GENERATE)[0].parent_order


def _replaced(events, current, opened, nodes):
    \"\"\"Os nós que um caminho mais curto tirou de ABERTOS (só na ordenada).\"\"\"
    return [
        next(order for order in opened if nodes[order].parent_order == step.node_order and nodes[order].rule_id == step.rule_id)
        for step in _of(events, TraceEvent.PRUNE)
        if step.node_order != current
    ]


def _advance(mode, opened, closed, current, events, nodes):
    \"\"\"Atualiza ABERTOS e FECHADOS com o que a iteração fez; devolve os nós trocados.\"\"\"
    generated = [step.node_order for step in _of(events, TraceEvent.GENERATE)]
    if mode == "single":
        closed.append(current)
        opened[:] = generated
        return []
    if mode == "stack":
        if _of(events, TraceEvent.BACKTRACK):
            opened.remove(current)
            closed.append(current)
        opened.extend(generated)
        return []
    opened.remove(current)
    closed.append(current)
    swaps = _replaced(events, current, opened, nodes)
    for order in swaps:
        opened.remove(order)
    opened.extend(generated)
    return swaps


def _made(events, swaps):
    \"\"\"A coluna GERA: os filhos da iteração, ou o que aconteceu no lugar deles.\"\"\"
    generated = _of(events, TraceEvent.GENERATE)
    deadlock = bool(_of(events, TraceEvent.DEADLOCK))
    if _of(events, TraceEvent.BACKTRACK):
        return "impasse, retrocesso" if deadlock else "retrocesso"
    if not generated:
        return "nada (impasse)" if deadlock else "nada"
    made = "  ".join(f"{step.rule_id}: S{step.node_order}" for step in generated)
    if swaps:
        made += "  (troca " + " ".join(f"S{order}" for order in swaps) + ")"
    return made


def lists_table(result):
    mode = LIST_MODES[result.algorithm]
    nodes = _nodes(result)
    priorities = {order: heuristic(step.state) for order, step in nodes.items()} if mode == "priority" else None
    current_title, opened_title, closed_title = LIST_TITLES[mode]
    by_iteration = {}
    for step in result.trace:
        by_iteration.setdefault(step.iteration, []).append(step)

    opened, closed = [0], []
    rows = [{"IT": 0, current_title: "", "NÍV": "", "GERA": "", "PODA": "", opened_title: _names(opened, priorities), closed_title: ""}]
    for iteration in range(1, result.metrics.iterations + 1):
        events = by_iteration.get(iteration, [])
        current = _current(events)
        node = nodes[current]
        row = {
            "IT": iteration,
            current_title: f"S{current}  {compact(node.state)}",
            "NÍV": node.depth,
            "PODA": " ".join(step.rule_id for step in _of(events, TraceEvent.PRUNE) if step.node_order == current),
        }
        if _of(events, TraceEvent.GOAL):
            rows.append({**row, "GERA": "objetivo: SUCESSO", opened_title: "", closed_title: ""})
            break
        swaps = _advance(mode, opened, closed, current, events, nodes)
        if priorities is not None:
            opened.sort(key=lambda order: (priorities[order], order))
        rows.append({**row, "GERA": _made(events, swaps), opened_title: _shorten(opened, priorities), closed_title: _shorten(closed)})
    if result.outcome is Outcome.CUTOFF:
        print(f"Parou no limite de {result.metrics.iterations} iterações (LIMITE).")
    return pd.DataFrame(rows).set_index("IT")


def case(algorithm, strategy, *, prune=True, max_iterations=settings.MAX_ITERATIONS):
    result = solve(algorithm, strategy, prune, max_iterations)
    report = Report(problems=(ProblemReport(P1.id, P1.initial, P1.goal, (result,)),))
    graph_writer.write_graphs(report, GRAPH_DIR)
    suffix = "" if prune else theme.GRAPH_NO_PRUNE_SUFFIX
    svg = GRAPH_DIR / P1.id / f"{algorithm}_{strategy}{suffix}.svg"
    if svg.exists():
        display(SVG(filename=str(svg)))
    else:
        print(tree_render.render_tree(result.trace))
    print(summary_line(result))
    return result


def summary_line(result):
    metrics = result.metrics
    parts = [
        theme.outcome_label(result.outcome),
        f"{metrics.iterations} iterações",
        f"{metrics.nodes_generated} nós gerados",
        f"{metrics.nodes_visited} expandidos",
        f"pico de ABERTOS {metrics.max_frontier}",
    ]
    if result.solution_length is not None:
        parts.append(f"caminho de {result.solution_length} movimentos")
    return " · ".join(parts)


def _describe(node, algorithm):
    if algorithm in HEURISTIC_ALGORITHMS:
        return f"S{node.order} ({node.rule.id}, h {heuristic(node.state)})"
    return f"S{node.order} ({node.rule.id})"


def frontier_demo(algorithm):
    module, name = FRONTIERS[algorithm]
    frontier_class = getattr(import_module(module), name)
    frontier = frontier_class(lambda node: heuristic(node.state)) if LIST_MODES[algorithm] == "priority" else frontier_class()
    tree = SearchTree()
    root = tree.root(INITIAL_STATE)
    children = [tree.expand(root, rule) for rule in applicable_rules(INITIAL_STATE)]
    for child in children:
        frontier.push(child)
    print("entram, nesta ordem:", "  ".join(_describe(child, algorithm) for child in children))
    print("saem, nesta ordem:  ", "  ".join(f"S{frontier.pop().order}" for _ in children))


def root_children(algorithm):
    opened_title = LIST_TITLES[LIST_MODES[algorithm]][1]
    shows_h = algorithm in HEURISTIC_ALGORITHMS
    rows = []
    for strategy in SLIDE_STRATEGIES:
        ordered = STRATEGY_REGISTRY[strategy].order(applicable_rules(INITIAL_STATE))
        first = lists_table(solve(algorithm, strategy)).loc[1]
        children = []
        for rule in ordered:
            child = rule.apply(INITIAL_STATE)
            children.append(f"{rule.id} → {compact(child)}" + (f" (h {heuristic(child)})" if shows_h else ""))
        rows.append(
            {
                "Estratégia": STRATEGY_LABELS[strategy],
                "Regras válidas na ordem": "  ".join(children),
                "Gera na iteração 1": first["GERA"],
                f"{opened_title} após a iteração 1": first[opened_title],
            }
        )
    return pd.DataFrame(rows).set_index("Estratégia")


def _levels(result, depth=None):
    nodes = _nodes(result)
    if depth is None:
        depth = max(step.depth for step in nodes.values())
    counts = Counter(step.depth for step in nodes.values() if step.depth <= depth)
    states = {step.state for step in nodes.values() if step.depth <= depth}
    return [counts[level] for level in range(depth + 1)], len(states)


def growth(algorithm, strategy="ascending", max_iterations=settings.MAX_ITERATIONS):
    result = solve(algorithm, strategy, False, max_iterations)
    depth = result.solution_length
    counts, distinct = _levels(result, depth)
    total = sum(counts)
    if len(counts) <= LONG_LIST:
        print("   →   ".join(f"{count} no nível {level}" for level, count in enumerate(counts)))
    else:
        print(f"{len(counts)} níveis: " + " ".join(str(count) for count in counts))
    where = f"até o nível {depth}" if depth is not None else f"em {result.metrics.iterations} iterações"
    print(f"\\n{total} nós {where}, só {distinct} estados distintos.")
    print(f"{1 - distinct / total:.0%} da árvore é repetição.")


def levels_chart(algorithm, strategy="ascending", max_iterations=settings.MAX_ITERATIONS):
    pruned = solve(algorithm, strategy, True)
    loose = solve(algorithm, strategy, False, max_iterations)
    depth = pruned.solution_length if pruned.solution_length is not None else pruned.metrics.max_depth
    with_prune, _ = _levels(pruned, depth)
    without, _ = _levels(loose, depth)
    levels = range(depth + 1)
    width = 0.4
    fig, ax = plt.subplots(figsize=(min(1.2 * len(levels) + 3, 13), 3.6))
    gray = ax.bar([level - width / 2 for level in levels], without, width * 0.95, color=LINE_GRAY, label=prune_label(False))
    colored = ax.bar([level + width / 2 for level in levels], with_prune, width * 0.95, color=ALGORITHM_COLORS[algorithm], label=prune_label(True))
    ax.bar_label(gray, fontsize=8, color=INK, padding=2)
    ax.bar_label(colored, fontsize=8, color=INK, padding=2)
    ax.set_xticks(list(levels), [f"nível {level}" for level in levels])
    ax.set_title(f"nós gerados por nível, {STRATEGY_LABELS[strategy]}", loc="left")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left")
    plt.show()


def show_path(result):
    path = result.solution_path
    if not path:
        print(f"{theme.outcome_label(result.outcome)}: não há caminho solução.")
        return
    drawings = [
        drawing(node.state, f"nível {node.depth}" if node.rule is None else f"nível {node.depth}  ({node.rule.id})")
        for node in path
    ]
    for start in range(0, len(drawings), 4):
        print(side_by_side(drawings[start:start + 4]))
        print()
    for parent, child in zip(path, path[1:]):
        rule = child.rule
        print(f"{rule.id}: {moved_disk(parent.state, rule)} de {rule.origin.name} para {rule.destination.name}")
    print(f"\\n{result.solution_length} movimentos.")


def _charted(algorithm):
    return [name for name in ALGORITHM_NAMES if name in CHART_ALGORITHMS or name == algorithm]


def _bold_columns(frame, algorithm):
    columns = [column for column in frame.columns if column.startswith(ALGORITHM_LABELS[algorithm])]
    return frame.style.set_properties(subset=columns, **{"font-weight": "bold"})


def _metrics_column(result):
    metrics = result.metrics
    return {
        "Desfecho": theme.outcome_label(result.outcome),
        "Nível da solução": result.solution_length,
        "Caminho": " ".join(result.applied_rules) or theme.ABSENT,
        "Iterações": metrics.iterations,
        "Nós gerados": metrics.nodes_generated,
        "Nós expandidos": metrics.nodes_visited,
        "Pico de ABERTOS": metrics.max_frontier,
        "Profundidade máx": metrics.max_depth,
        "Retrocessos": metrics.backtracks,
        "Impasses": metrics.deadlocks,
    }


def strategy_table(algorithm):
    columns = {
        f"{SHORT[strategy]} {prune_label(prune)}": _metrics_column(solve(algorithm, strategy, prune))
        for prune in (False, True)
        for strategy in SLIDE_STRATEGIES
    }
    return pd.DataFrame(columns).style.format(na_rep=theme.ABSENT)


CHAMPION_ROWS = ("Nível da solução", "Iterações", "Nós gerados", "Nós expandidos", "Pico de ABERTOS", "Retrocessos", "Impasses")


def _champions(row):
    if row.name not in CHAMPION_ROWS:
        return ["" for _ in row]
    best = min(value for value in row if not pd.isna(value))
    return [f"color: {WIN_COLOR}; font-weight: bold" if value == best else "" for value in row]


def algorithms_table(algorithm):
    combinations = [(name, strategy) for name in ALGORITHM_NAMES for strategy in SLIDE_STRATEGIES]
    frame = pd.DataFrame({label(name, strategy): _metrics_column(solve(name, strategy)) for name, strategy in combinations})
    contenders = [
        label(name, strategy)
        for name, strategy in combinations
        if name in _charted(algorithm) and solve(name, strategy).outcome.is_success
    ]
    styled = _bold_columns(frame, algorithm).apply(_champions, subset=contenders, axis=1)
    return styled.format(na_rep=theme.ABSENT)


def paths_plot(algorithm):
    rows = [(name, strategy, solve(name, strategy)) for name in _charted(algorithm) for strategy in SLIDE_STRATEGIES]
    longest = max(len(result.applied_rules) for _, _, result in rows)
    fig, ax = plt.subplots(figsize=(min(3 + 0.45 * longest, 14), 0.75 * len(rows) + 0.6))
    for row, (name, strategy, result) in enumerate(rows):
        y = len(rows) - row
        rules = result.applied_rules
        color = STRATEGY_COLORS[strategy]
        weight = "bold" if name == algorithm else "normal"
        ax.text(-3.6, y, label(name, strategy), ha="right", va="center", color=color, fontweight=weight, fontsize=10)
        count = str(len(rules)) if result.outcome.is_success else theme.outcome_label(result.outcome).lower()
        ax.text(-0.3, y, count, ha="right", va="center", fontweight="bold", fontsize=10, color=BLACK)
        if rules:
            ax.plot(range(len(rules)), [y] * len(rules), color=LINE_GRAY, linewidth=1, zorder=1)
        for position, rule_id in enumerate(rules):
            last = position == len(rules) - 1
            ax.scatter(position, y, s=60, color=GOAL_COLOR if last else color, zorder=2)
            ax.text(position, y + 0.28, rule_id, ha="center", fontsize=7, color=MUTED)
    ax.set_xlim(-7.5, longest)
    ax.set_ylim(0.3, len(rows) + 0.7)
    ax.axis("off")
    ax.set_title("caminhos encontrados em P1 (com poda) e o número de movimentos", loc="left", fontsize=10, color=INK)
    plt.show()


def _winners(solved, measure, unit):
    best = min(measure(result) for _, result, _ in solved)
    names = "; ".join(text for text, result, _ in solved if measure(result) == best)
    return f"{names} ({unit} {best})" if unit else f"{names} ({best})"


def expanded_chart(algorithm):
    bars = [
        (label(algorithm, strategy, prune=prune), solve(algorithm, strategy, prune), algorithm)
        for prune in (True, False)
        for strategy in SLIDE_STRATEGIES
    ]
    bars.extend(
        (label(name, strategy, prune=True), solve(name, strategy), name)
        for name in _charted(algorithm)
        if name != algorithm
        for strategy in SLIDE_STRATEGIES
    )
    finished = sorted((bar for bar in bars if bar[1].outcome is not Outcome.CUTOFF), key=lambda bar: bar[1].metrics.nodes_visited)
    fig, ax = plt.subplots(figsize=(9, 0.4 * len(finished) + 1))
    shown = ax.barh(
        [text for text, _, _ in finished],
        [result.metrics.nodes_visited for _, result, _ in finished],
        color=[ALGORITHM_COLORS[name] for _, _, name in finished],
        height=0.7,
    )
    ax.bar_label(shown, fontsize=8, color=INK, padding=3)
    for tick, (_, _, name) in zip(ax.get_yticklabels(), finished):
        tick.set_fontweight("bold" if name == algorithm else "normal")
    ax.invert_yaxis()
    ax.set_title("nós expandidos em P1", loc="left")
    ax.grid(axis="y", visible=False)
    plt.show()
    for text, result, _ in bars:
        if result.outcome is Outcome.CUTOFF:
            print(f"{text}: fora do gráfico, gira até o limite de {result.metrics.iterations} iterações.")
    solved = [bar for bar in finished if bar[1].outcome.is_success]
    print("Menor nível:", _winners(solved, lambda result: result.solution_length, "nível"))
    print("Menos nós expandidos:", _winners(solved, lambda result: result.metrics.nodes_visited, ""))


SYMBOLS = {
    "b": ("fator de ramificação", "quantas regras valem, em média, em cada nó expandido"),
    "d": ("nível da solução", "profundidade do objetivo mais raso"),
    "m": ("profundidade máxima", "até onde o caminho desce"),
    "V": ("vértices", "os estados possíveis"),
    "E": ("arestas", "movimentos entre estados"),
}


def _max_depths(algorithm):
    if algorithm is None:
        return "; ".join(
            f"{ALGORITHM_LABELS[name]} " + "/".join(str(solve(name, strategy).metrics.max_depth) for strategy in SLIDE_STRATEGIES)
            for name in ALGORITHM_NAMES
        ) + " (cresc./decr.)"
    return " · ".join(f"{solve(algorithm, strategy).metrics.max_depth} no {SHORT[strategy]}" for strategy in SLIDE_STRATEGIES)


def complexity_values(algorithm, symbols=tuple(SYMBOLS)):
    states = all_states()
    loose = solve("breadth_first", "ascending", False)
    expanded = [step.state for step in loose.trace.of_event(TraceEvent.VISIT)]
    values = {
        "b": f"cerca de {br(sum(len(successors(state)) for state in expanded) / len(expanded), 1)}",
        "d": str(solve("breadth_first", "ascending").solution_length),
        "m": _max_depths(algorithm),
        "V": str(len(states)),
        "E": str(sum(len(successors(state)) for state in states) // 2),
    }
    return pd.DataFrame(
        [{"Símbolo": symbol, "Nome": SYMBOLS[symbol][0], "O que é": SYMBOLS[symbol][1], "Em P1": values[symbol]} for symbol in symbols]
    ).set_index("Símbolo")


def _bold_rows(frame, algorithm):
    name = ALGORITHM_LABELS[algorithm]
    return frame.style.apply(
        lambda row: ["font-weight: bold" if row["Algoritmo"] == name else "" for _ in row],
        axis=1,
    ).hide(axis="index")


def p1_comparison(algorithm=None):
    frame = pd.DataFrame(
        [
            {
                "#": row.position,
                "Algoritmo": ALGORITHM_LABELS[row.result.algorithm],
                "Estratégia": STRATEGY_LABELS[row.result.strategy],
                LABELS["outcome"]: theme.outcome_label(row.result.outcome),
                LABELS["moves"]: row.result.solution_length,
                LABELS["iterations"]: row.result.metrics.iterations,
                LABELS["nodes_generated"]: row.result.metrics.nodes_generated,
            }
            for row in p1_report().problems[0].leaderboard.rows
        ]
    ).astype({LABELS["moves"]: "Int64"})
    return frame if algorithm is None else _bold_rows(frame, algorithm)


def goals_comparison(algorithm=None):
    frame = pd.DataFrame(
        [
            {
                "Algoritmo": ALGORITHM_LABELS[row.algorithm],
                "Estratégia": STRATEGY_LABELS[row.strategy],
                "Sucessos": f"{row.successes}/{row.runs}",
                "Impasses": row.deadlocks,
                LABELS["moves"]: render_stat(row.moves),
                LABELS["iterations"]: render_stat(row.iterations),
                LABELS["nodes_generated"]: render_stat(row.nodes_generated),
            }
            for row in goals_report().summary.rows
        ]
    )
    return frame if algorithm is None else _bold_rows(frame, algorithm)


def show_dot(source):
    if shutil.which("dot") is None:
        print(source)
        return
    display(SVG(subprocess.run(["dot", "-Tsvg"], input=source, capture_output=True, text=True, check=True).stdout))


def show_trace(result):
    print(trace_render.render_trace(result.trace))
"""
