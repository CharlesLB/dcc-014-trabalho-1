from __future__ import annotations

from cells import IGNORE, Cell, code, markdown

REPOSITORY = "CharlesLB/dcc-014-trabalho-1"
BRANCH = "main"
NOTEBOOK_DIR = "apps/notebook/notebooks"
NOTEBOOK = "torre_de_londres.ipynb"
TITLE = "Torre de Londres"
COLAB_URL = f"https://colab.research.google.com/github/{REPOSITORY}/blob/{BRANCH}/{NOTEBOOK_DIR}/{NOTEBOOK}"
COLAB_BADGE = "https://colab.research.google.com/assets/colab-badge.svg"

SECTIONS = (
    "Busca irrevogável",
    "Backtracking",
    "Busca em largura",
    "Busca ordenada",
    f"Gráficos e análise {IGNORE}",
    "Integrantes",
)

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


def header() -> Cell:
    contents = "\n".join(f"{index}. {name}" for index, name in enumerate(SECTIONS, 1))
    return markdown(
        f"""# {TITLE}

[![Abrir no Colab]({COLAB_BADGE})]({COLAB_URL})

DCC014 Inteligência Artificial · UFJF · Trabalho 1 · Grupo 5 · Profa. Luciana

Resolvedor da Torre de Londres (3 hastes, 3 discos) com quatro algoritmos de busca sobre o mesmo motor. Cada seção de algoritmo segue a ordem dos slides: o problema, a ideia, o laço e as listas, as regras, a estratégia, a árvore sem poda e com poda, o pseudocódigo com o código do projeto, o caminho solução, os comparativos e a complexidade.

{contents}

Tudo o que é código e não aparece nos slides está marcado com **{IGNORE}**: o Setup, as funções que desenham tabelas e gráficos e os extras de cada seção. O código que aparece nos slides (problema, regras, estratégias, fronteira, motor e algoritmos) fica no ponto do slide correspondente, sem marcação.

Rode **Ambiente de execução → Executar tudo**."""
    )


def members() -> Cell:
    rows = "\n".join(f"| {name} | {number} |" for name, number in MEMBERS)
    return markdown(
        f"""# {len(SECTIONS)}. Integrantes

| Integrante | Matrícula |
|---|---|
{rows}

DCC014 · Inteligência Artificial · Universidade Federal de Juiz de Fora · Profa. Luciana"""
    )


VIEW_HELPERS = code(
    """#@title Funções de apresentação
import shutil
import subprocess
from collections import Counter
from functools import cache
from pathlib import Path

import pandas as pd
from IPython.display import SVG, display

from config import settings
from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.domain.problem import INITIAL_STATE, get_problem
from core.domain.state_space import all_states, applicable_rules, successors
from core.rules.domain.catalog import INVERSE_RULE_ID, RULE_BY_ID, RULES
from core.rules.strategies.domain.registry import STRATEGIES as STRATEGY_REGISTRY
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from core.search_tree.frontier import PriorityFrontier, QueueFrontier, StackFrontier
from core.search_tree.outcome import Outcome
from core.search_tree.trace import TraceEvent
from core.search_tree.tree import SearchTree
from libs.inputs.selection import ExecutionRequest
from libs.outputs import graph_writer, state_render, theme, trace_render, tree_render
from libs.outputs.formatter import ProblemReport, Report
from runner.pipeline import build_report

LABELS = theme.REPORT_LABELS
ALGORITHM_LABELS = {
    "irrevocable": "Irrevogável",
    "backtracking": "Backtracking",
    "breadth_first": "Largura",
    "ordered": "Ordenada",
}
STRATEGY_LABELS = {"ascending": "crescente", "descending": "decrescente", "custom": "custom"}
SHORT = {"ascending": "cresc.", "descending": "decr.", "custom": "custom"}
SLIDE_STRATEGIES = ("ascending", "descending")
GRAPH_DIR = Path("data")
P1 = get_problem("P1")
LIST_MODES = {
    "irrevocable": "single",
    "backtracking": "stack",
    "breadth_first": "queue",
    "ordered": "priority",
}
LONG_LIST = 8


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


def compact(state):
    return "/".join("".join(theme.disk_symbol(disk) for disk in stack) or "–" for stack in state)


def side_by_side(blocks, gap="      "):
    columns = [block.splitlines() for block in blocks]
    height = max(len(lines) for lines in columns)
    columns = [[""] * (height - len(lines)) + lines for lines in columns]
    widths = [max(len(line) for line in lines) for lines in columns]
    return "\\n".join(
        gap.join(lines[row].ljust(width) for lines, width in zip(columns, widths)).rstrip()
        for row in range(height)
    )


def show_problem(problem=P1):
    print(
        side_by_side(
            [
                f"INICIAL  {compact(problem.initial)}\\n\\n{state_render.render_pegs(problem.initial)}",
                "\\n\\n\\n  ——→",
                f"OBJETIVO {problem.id}  {compact(problem.goal)}\\n\\n{state_render.render_pegs(problem.goal)}",
            ]
        )
    )


def rules_table():
    return pd.DataFrame(
        [
            {
                "Regra": rule.id,
                "Move de": rule.origin.name,
                "Para": rule.destination.name,
                "Inversa": INVERSE_RULE_ID[rule.id],
                "Custo": rule.cost,
            }
            for rule in RULES
        ]
    ).set_index("Regra")


def show_rule_example(rule_id="R4", state=INITIAL_STATE):
    rule = RULE_BY_ID[rule_id]
    after = rule.apply(state)
    print(
        side_by_side(
            [
                f"S0  {compact(state)}\\n\\n{state_render.render_pegs(state)}",
                f"\\n\\n\\n  —{rule.id}→",
                f"{compact(after)}\\n\\n{state_render.render_pegs(after)}",
            ]
        )
    )
    moved = theme.disk_name(state[rule.origin][-1]).lower()
    print(f"\\nExemplo: {rule.id} em S0 leva o {moved} de {rule.origin.name} para {rule.destination.name}.")


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


def _costs(nodes):
    costs = {}
    for order in sorted(nodes):
        step = nodes[order]
        costs[order] = 0 if step.parent_order is None else costs[step.parent_order] + RULE_BY_ID[step.rule_id].cost
    return costs


def _names(orders, costs=None):
    if costs is None:
        return " ".join(f"S{order}" for order in orders)
    return " ".join(f"S{order}({costs[order]})" for order in orders)


def _shorten(orders, costs=None):
    if len(orders) <= LONG_LIST:
        return _names(orders, costs)
    ordered = sorted(orders)
    if costs is None and ordered == list(range(ordered[0], ordered[-1] + 1)):
        return f"S{ordered[0]} … S{ordered[-1]}"
    return f"{len(orders)}: {_names(orders[:3], costs)} …"


def lists_table(result):
    mode = LIST_MODES[result.algorithm]
    nodes = _nodes(result)
    costs = _costs(nodes) if mode == "priority" else None
    steps = {}
    for step in result.trace:
        steps.setdefault(step.iteration, []).append(step)

    titles = {
        "stack": ("TOPO DA PILHA", "PILHA", "RETROCEDIDOS"),
        "single": ("NÓ ATUAL", "ABERTOS", "FECHADOS"),
    }.get(mode, ("SAI DE ABERTOS", "ABERTOS", "FECHADOS"))
    opened, closed = [0], []
    rows = [{"IT": 0, titles[0]: "", "NÍV": "", "GERA": "", "PODA": "", titles[1]: _names(opened, costs), titles[2]: ""}]
    for iteration in range(1, result.metrics.iterations + 1):
        events = steps.get(iteration, [])
        generated = [step for step in events if step.event is TraceEvent.GENERATE]
        goal = next((step for step in events if step.event is TraceEvent.GOAL), None)
        visit = next((step for step in events if step.event is TraceEvent.VISIT), None)
        back = next((step for step in events if step.event is TraceEvent.BACKTRACK), None)
        if goal is not None:
            current = goal.node_order
        elif visit is not None:
            current = visit.node_order
        elif back is not None:
            current = back.node_order
        else:
            current = generated[0].parent_order
        pruned = [step.rule_id for step in events if step.event is TraceEvent.PRUNE and step.node_order == current]
        replaced = [step for step in events if step.event is TraceEvent.PRUNE and step.node_order != current]
        node = nodes[current]
        row = {
            "IT": iteration,
            titles[0]: f"S{current}  {compact(node.state)}",
            "NÍV": node.depth,
            "PODA": " ".join(pruned),
        }
        if goal is not None:
            rows.append({**row, "GERA": "objetivo: SUCESSO", titles[1]: "", titles[2]: ""})
            break
        if mode == "stack":
            if back is not None:
                opened.remove(current)
                closed.append(current)
            opened.extend(step.node_order for step in generated)
        elif mode == "single":
            closed.append(current)
            opened = [step.node_order for step in generated]
        else:
            opened.remove(current)
            closed.append(current)
            for step in replaced:
                old = next(o for o in opened if nodes[o].parent_order == step.node_order and nodes[o].rule_id == step.rule_id)
                opened.remove(old)
            opened.extend(step.node_order for step in generated)
            if mode == "priority":
                opened.sort(key=lambda order: (costs[order], order))
        made = "  ".join(f"{step.rule_id}: S{step.node_order}" for step in generated)
        deadlock = any(step.event is TraceEvent.DEADLOCK for step in events)
        if back is not None:
            made = "impasse, retrocesso" if deadlock else "retrocesso"
        elif not generated:
            made = "nada (impasse)" if deadlock else "nada"
        rows.append({**row, "GERA": made, titles[1]: _shorten(opened, costs), titles[2]: _shorten(closed)})
    frame = pd.DataFrame(rows).set_index("IT")
    if result.outcome is Outcome.CUTOFF:
        print(f"Parou no limite de {result.metrics.iterations} iterações (LIMITE).")
    return frame


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
        parts.append(f"caminho de {result.solution_length} movimentos, custo {result.solution_cost}")
    return " · ".join(parts)


def frontier_demo(algorithm):
    tree = SearchTree()
    root = tree.root(INITIAL_STATE)
    children = [tree.expand(root, rule) for rule in applicable_rules(INITIAL_STATE)]
    frontier = {"backtracking": StackFrontier, "breadth_first": QueueFrontier, "ordered": PriorityFrontier}[algorithm]()
    for child in children:
        frontier.push(child)
    print("entram, nesta ordem:", "  ".join(f"S{c.order} ({c.rule.id}, custo {c.cost})" for c in children))
    print("saem, nesta ordem:  ", "  ".join(f"S{frontier.pop().order}" for _ in children))


def root_children(algorithm):
    rows = []
    for strategy in SLIDE_STRATEGIES:
        ordered = STRATEGY_REGISTRY[strategy].order(applicable_rules(INITIAL_STATE))
        first = lists_table(solve(algorithm, strategy)).loc[1]
        opened_title = "PILHA" if LIST_MODES[algorithm] == "stack" else "ABERTOS"
        rows.append(
            {
                "Estratégia": STRATEGY_LABELS[strategy],
                "Regras válidas na ordem": "  ".join(f"{rule.id} → {compact(rule.apply(INITIAL_STATE))}" for rule in ordered),
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
    if len(counts) <= 8:
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
    gray = ax.bar([level - width / 2 for level in levels], without, width * 0.95, color="#c5c7cc", label="sem poda")
    blue = ax.bar([level + width / 2 for level in levels], with_prune, width * 0.95, color=ALGORITHM_COLORS[algorithm], label="com poda")
    ax.bar_label(gray, fontsize=8, color=INK, padding=2)
    ax.bar_label(blue, fontsize=8, color=INK, padding=2)
    ax.set_xticks(list(levels), [f"nível {level}" for level in levels])
    ax.set_title(f"nós gerados por nível, {STRATEGY_LABELS[strategy]}", loc="left")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left")
    plt.show()


def show_path(result):
    if not result.solution_path:
        print(f"{theme.outcome_label(result.outcome)}: não há caminho solução.")
        return
    drawings = []
    for node in result.solution_path:
        title = f"nível {node.depth}" if node.rule is None else f"nível {node.depth}  ({node.rule.id})"
        drawings.append(f"{title}\\n{compact(node.state)}\\n\\n{state_render.render_pegs(node.state)}")
    for start in range(0, len(drawings), 4):
        print(side_by_side(drawings[start:start + 4]))
        print()
    for node in result.solution_path[1:]:
        moved = theme.disk_name(node.state[node.rule.destination][-1]).lower()
        print(f"{node.rule.id}: {moved} de {node.rule.origin.name} para {node.rule.destination.name}  (custo acumulado {node.cost})")
    print(f"\\n{result.solution_length} movimentos, custo {result.solution_cost}.")


def _bold_columns(frame, algorithm):
    label = ALGORITHM_LABELS[algorithm]
    columns = [column for column in frame.columns if column.startswith(label)]
    return frame.style.set_properties(subset=columns, **{"font-weight": "bold"})


def _metrics_column(result):
    metrics = result.metrics
    return {
        "Desfecho": theme.outcome_label(result.outcome),
        "Nível da solução": theme.ABSENT if result.solution_length is None else str(result.solution_length),
        "Caminho": " ".join(result.applied_rules) or theme.ABSENT,
        "Custo": theme.ABSENT if result.solution_cost is None else str(result.solution_cost),
        "Iterações": str(metrics.iterations),
        "Nós gerados": str(metrics.nodes_generated),
        "Nós expandidos": str(metrics.nodes_visited),
        "Pico de ABERTOS": str(metrics.max_frontier),
        "Profundidade máx": str(metrics.max_depth),
        "Retrocessos / impasses": f"{metrics.backtracks} / {metrics.deadlocks}",
    }


def strategy_table(algorithm):
    columns = {}
    for prune in (False, True):
        for strategy in SLIDE_STRATEGIES:
            label = f"{SHORT[strategy]} {'com' if prune else 'sem'} poda"
            columns[label] = _metrics_column(solve(algorithm, strategy, prune))
    return pd.DataFrame(columns)


def algorithms_table(algorithm):
    columns = {
        f"{ALGORITHM_LABELS[name]} {SHORT[strategy]}": _metrics_column(solve(name, strategy))
        for name in ALGORITHM_NAMES
        for strategy in SLIDE_STRATEGIES
    }
    return _bold_columns(pd.DataFrame(columns), algorithm)


def paths_plot(algorithm):
    rows = [(name, strategy, solve(name, strategy)) for name in ALGORITHM_NAMES for strategy in SLIDE_STRATEGIES]
    colors = {"ascending": "#2a78d6", "descending": "#c87400"}
    longest = max(len(result.applied_rules) for _, _, result in rows)
    fig, ax = plt.subplots(figsize=(min(3 + 0.45 * longest, 14), 0.75 * len(rows) + 0.6))
    for row, (name, strategy, result) in enumerate(rows):
        y = len(rows) - row
        rules = result.applied_rules
        label = f"{ALGORITHM_LABELS[name]} {SHORT[strategy]}"
        weight = "bold" if name == algorithm else "normal"
        ax.text(-0.6, y, label, ha="right", va="center", color=colors[strategy], fontweight=weight, fontsize=10)
        count = str(len(rules)) if result.outcome.is_success else theme.outcome_label(result.outcome).lower()
        ax.text(-0.3, y, count, ha="right", va="center", fontweight="bold", fontsize=10, color="#0b0b0b")
        if rules:
            ax.plot(range(len(rules)), [y] * len(rules), color="#c5c7cc", linewidth=1, zorder=1)
        for position, rule_id in enumerate(rules):
            last = position == len(rules) - 1
            ax.scatter(position, y, s=60, color="#1baf7a" if last else colors[strategy], zorder=2)
            ax.text(position, y + 0.28, rule_id, ha="center", fontsize=7, color=MUTED)
    ax.set_xlim(-4.5, longest)
    ax.set_ylim(0.3, len(rows) + 0.7)
    ax.axis("off")
    ax.set_title("caminhos encontrados em P1 (com poda); o número é o total de movimentos", loc="left", fontsize=10, color=INK)
    plt.show()


def expanded_chart(algorithm):
    bars = []
    for prune in (True, False):
        for strategy in SLIDE_STRATEGIES:
            result = solve(algorithm, strategy, prune)
            label = f"{ALGORITHM_LABELS[algorithm]} {SHORT[strategy]} {'com' if prune else 'sem'} poda"
            bars.append((label, result, algorithm))
    for name in ALGORITHM_NAMES:
        if name == algorithm:
            continue
        for strategy in SLIDE_STRATEGIES:
            bars.append((f"{ALGORITHM_LABELS[name]} {SHORT[strategy]} com poda", solve(name, strategy), name))
    finished = [bar for bar in bars if bar[1].outcome is not Outcome.CUTOFF]
    finished.sort(key=lambda bar: bar[1].metrics.nodes_visited)
    fig, ax = plt.subplots(figsize=(9, 0.4 * len(finished) + 1))
    shown = ax.barh(
        [label for label, _, _ in finished],
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
    for label, result, _ in bars:
        if result.outcome is Outcome.CUTOFF:
            print(f"{label}: fora do gráfico, gira até o limite de {result.metrics.iterations} iterações.")
    solved = [bar for bar in finished if bar[1].outcome.is_success]
    shortest = min(result.solution_length for _, result, _ in solved)
    print("Menor nível:", "; ".join(label for label, result, _ in solved if result.solution_length == shortest), f"(nível {shortest})")
    fewest = min(result.metrics.nodes_visited for _, result, _ in solved)
    print("Menos nós expandidos:", "; ".join(label for label, result, _ in solved if result.metrics.nodes_visited == fewest), f"({fewest})")


SYMBOLS = {
    "b": ("fator de ramificação", "quantas regras valem, em média, em cada nó expandido"),
    "d": ("nível da solução", "profundidade do objetivo mais raso"),
    "m": ("profundidade máxima", "até onde o caminho desce"),
    "V": ("vértices", "os estados possíveis"),
    "E": ("arestas", "movimentos entre estados"),
    "C*": ("custo ótimo", "custo da solução mais barata"),
    "ε": ("menor custo de regra", "a regra mais barata"),
}


def complexity_values(algorithm, symbols):
    states = all_states()
    loose = solve("breadth_first", "ascending", False)
    expanded = [step.state for step in loose.trace.of_event(TraceEvent.VISIT)]
    values = {
        "b": f"cerca de {sum(len(successors(state)) for state in expanded) / len(expanded):.1f}".replace(".", ","),
        "d": str(solve("breadth_first", "ascending").solution_length),
        "m": " · ".join(f"{solve(algorithm, strategy).metrics.max_depth} no {SHORT[strategy]}" for strategy in SLIDE_STRATEGIES),
        "V": str(len(states)),
        "E": str(sum(len(successors(state)) for state in states) // 2),
        "C*": str(solve("ordered", "ascending").solution_cost),
        "ε": str(min(rule.cost for rule in RULES)),
    }
    return pd.DataFrame(
        [{"Símbolo": symbol, "Nome": SYMBOLS[symbol][0], "O que é": SYMBOLS[symbol][1], "Em P1": values[symbol]} for symbol in symbols]
    ).set_index("Símbolo")


def _stat(value):
    return theme.ABSENT if value is None else f"{value.mean:.2f} / {value.median:g}"


def _bold_rows(frame, algorithm):
    label = ALGORITHM_LABELS[algorithm]
    return frame.style.apply(
        lambda row: ["font-weight: bold" if row["Algoritmo"] == label else "" for _ in row],
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
                LABELS["cost"]: row.result.solution_cost,
                LABELS["iterations"]: row.result.metrics.iterations,
                LABELS["nodes_generated"]: row.result.metrics.nodes_generated,
            }
            for row in p1_report().problems[0].leaderboard.rows
        ]
    ).astype({LABELS["moves"]: "Int64", LABELS["cost"]: "Int64"})
    return frame if algorithm is None else _bold_rows(frame, algorithm)


def goals_comparison(algorithm=None):
    frame = pd.DataFrame(
        [
            {
                "Algoritmo": ALGORITHM_LABELS[row.algorithm],
                "Estratégia": STRATEGY_LABELS[row.strategy],
                "Sucessos": f"{row.successes}/{row.runs}",
                "Impasses": row.deadlocks,
                LABELS["moves"]: _stat(row.moves),
                LABELS["cost"]: _stat(row.cost),
                LABELS["iterations"]: _stat(row.iterations),
                LABELS["nodes_generated"]: _stat(row.nodes_generated),
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
""",
    hidden=True,
)
