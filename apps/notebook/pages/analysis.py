from __future__ import annotations

from cells import Cell, code, markdown
from pages.algorithm import ALGORITHM_SECTIONS

TITLE = "Comparação dos algoritmos"

INTRO = """Uma carta só não diz qual método é melhor. Esta seção roda a matriz completa (4 algoritmos × 2 estratégias) primeiro na carta P1 e depois em todos os 36 estados do espaço como objetivo, sempre a partir da mesma posição inicial (cartas G01 a G36).

As tabelas trazem os quatro algoritmos. Os gráficos deixam a irrevogável de fora: ela não garante solução, e uma execução sem caminho não tem movimentos para comparar."""

PLOT_STYLE = code(
    """#@title Estilo e funções dos gráficos
from functools import cache

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from core.domain.state_space import cheapest_cost, shortest_distance
from core.rules.domain.base import CAPACITIES, Disk, Peg

MATPLOTLIB_VERSION = tuple(int(part) for part in matplotlib.__version__.split(".")[:2])
HORIZONTAL = {"orientation": "horizontal"} if MATPLOTLIB_VERSION >= (3, 10) else {"vert": False}

ALGORITHMS = CHART_ALGORITHMS
STRATEGIES = tuple(STRATEGY_LABELS)
ALGORITHM_COLORS = {
    "irrevocable": "#2a78d6",
    "backtracking": "#eb6834",
    "breadth_first": "#1baf7a",
    "ordered": "#eda100",
}
DISK_COLORS = {Disk.GREEN: "#2e9e44", Disk.RED: "#d63b3b", Disk.BLUE: "#2f6fd6"}
OPTIMUM_COLOR = "#b8b8b4"
INK = "#52514e"
MUTED = "#8a8984"

plt.rcParams.update(
    {
        "figure.dpi": 110,
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "axes.titlesize": 11,
        "axes.titlecolor": "#0b0b0b",
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#e6e6e3",
        "grid.linewidth": 0.8,
        "xtick.color": INK,
        "ytick.color": INK,
        "legend.frameon": False,
    }
)

BOX_STYLE = {
    "patch_artist": True,
    "showmeans": True,
    "medianprops": {"color": "#0b0b0b", "linewidth": 1.5},
    "meanprops": {"marker": "D", "markerfacecolor": "#ffffff", "markeredgecolor": "#0b0b0b", "markersize": 5},
    "flierprops": {"marker": "o", "markersize": 3, "markerfacecolor": MUTED, "markeredgecolor": "none"},
    "whiskerprops": {"color": MUTED},
    "capprops": {"color": MUTED},
}


def combination_label(algorithm, strategy):
    return f"{ALGORITHM_LABELS[algorithm]} · {STRATEGY_LABELS[strategy]}"


def algorithm_legend(fig, *, optimum=False, y=0.0):
    names = [ALGORITHM_LABELS[name] for name in ALGORITHMS]
    colors = [ALGORITHM_COLORS[name] for name in ALGORITHMS]
    if optimum:
        names.append("ótimo")
        colors.append(OPTIMUM_COLOR)
    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in colors]
    fig.legend(handles, names, loc="lower center", ncol=len(names), bbox_to_anchor=(0.5, y))


def paint(parts, colors):
    for patch, color in zip(parts["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor(color)
        patch.set_alpha(0.85)


def draw_state(ax, state, left, title):
    for peg in Peg:
        x = left + 1.2 * peg.value
        ax.plot([x, x], [0, 0.9 * CAPACITIES[peg] + 0.15], color=MUTED, linewidth=3, solid_capstyle="round", zorder=1)
        ax.text(x, -0.45, peg.name, ha="center", va="center", fontsize=9, color=INK)
        for level, disk in enumerate(state[peg]):
            ax.add_patch(plt.Circle((x, 0.45 + 0.9 * level), 0.4, color=DISK_COLORS[disk], zorder=2))
            ax.text(x, 0.45 + 0.9 * level, theme.disk_symbol(disk), ha="center", va="center", fontsize=9, fontweight="bold", color="#ffffff", zorder=3)
    ax.plot([left - 0.6, left + 3.0], [0, 0], color=INK, linewidth=2)
    ax.text(left + 1.2, 3.25, title, ha="center", va="center", fontsize=11, color="#0b0b0b")


def draw_problem(ax, problem):
    draw_state(ax, problem.initial, 0, f"INICIAL  {compact(problem.initial)}")
    ax.annotate("", xy=(5.2, 1.3), xytext=(3.8, 1.3), arrowprops={"arrowstyle": "-|>", "color": INK, "linewidth": 1.5})
    draw_state(ax, problem.goal, 6.4, f"OBJETIVO {problem.id}  {compact(problem.goal)}")
    ax.set_xlim(-1, 10)
    ax.set_ylim(-0.8, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")


def grouped_bars(ax, frame, column, title, missing="—"):
    width = 0.8 / len(ALGORITHMS)
    positions = np.arange(len(STRATEGIES))
    for index, algorithm in enumerate(ALGORITHMS):
        values = [frame.loc[(algorithm, strategy), column] for strategy in STRATEGIES]
        heights = [0 if pd.isna(value) else value for value in values]
        bars = ax.bar(
            positions + (index - (len(ALGORITHMS) - 1) / 2) * width,
            heights,
            width * 0.9,
            color=ALGORITHM_COLORS[algorithm],
        )
        labels = [missing if pd.isna(value) else f"{value:g}" for value in values]
        ax.bar_label(bars, labels=labels, fontsize=8, color=INK, padding=2)
    ax.set_xticks(positions, [STRATEGY_LABELS[name] for name in STRATEGIES])
    ax.set_title(title, loc="left")
    ax.grid(axis="x", visible=False)


def p1_chart():
    frame = pd.DataFrame(
        [
            {
                "algorithm": result.algorithm,
                "strategy": result.strategy,
                "moves": result.solution_length,
                "iterations": result.metrics.iterations,
                "generated": result.metrics.nodes_generated,
            }
            for result in p1_report().problems[0].results
        ]
    ).set_index(["algorithm", "strategy"]).astype({"moves": "Int64"})
    fig = plt.figure(figsize=(13, 6.8))
    grid = fig.add_gridspec(2, 3, height_ratios=(1, 2))
    draw_problem(fig.add_subplot(grid[0, :]), P1)
    axes = [fig.add_subplot(grid[1, column]) for column in range(3)]
    grouped_bars(axes[0], frame, "moves", "Movimentos da solução (tracejado: ótimo)")
    axes[0].axhline(shortest_distance(P1.initial, P1.goal), color=MUTED, linestyle="--", linewidth=1, zorder=0)
    grouped_bars(axes[1], frame, "iterations", "Iterações")
    grouped_bars(axes[2], frame, "generated", "Nós gerados")
    algorithm_legend(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    plt.show()


@cache
def goals_runs():
    rows = []
    for entry in goals_report().problems:
        best_moves = shortest_distance(entry.initial_state, entry.goal_state)
        best_cost = cheapest_cost(entry.initial_state, entry.goal_state)
        for result in entry.results:
            rows.append(
                {
                    "goal": entry.problem_id,
                    "algorithm": result.algorithm,
                    "strategy": result.strategy,
                    "success": result.outcome.is_success,
                    "moves": result.solution_length,
                    "cost": result.solution_cost,
                    "iterations": result.metrics.iterations,
                    "generated": result.metrics.nodes_generated,
                    "best_moves": best_moves,
                    "best_cost": best_cost,
                }
            )
    runs = pd.DataFrame(rows)
    runs["extra_moves"] = runs.moves - runs.best_moves
    runs["extra_cost"] = runs.cost - runs.best_cost
    return runs


def _values(runs, algorithm, strategy, column):
    return runs.loc[(runs.algorithm == algorithm) & (runs.strategy == strategy), column].dropna().to_numpy()


def goals_chart():
    runs = goals_runs()
    panels = (
        ("moves", "Movimentos da solução", False),
        ("iterations", "Iterações (escala log)", True),
        ("generated", "Nós gerados (escala log)", True),
    )
    width = 0.8 / len(ALGORITHMS)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    for ax, (column, title, log) in zip(axes, panels):
        for index, algorithm in enumerate(ALGORITHMS):
            positions = np.arange(len(STRATEGIES)) + (index - (len(ALGORITHMS) - 1) / 2) * width
            data = [_values(runs, algorithm, strategy, column) for strategy in STRATEGIES]
            paint(ax.boxplot(data, positions=positions, widths=width * 0.85, **BOX_STYLE), [ALGORITHM_COLORS[algorithm]] * len(data))
        ticks = [STRATEGY_LABELS[name] for name in STRATEGIES]
        if column == "moves":
            optimum = runs.drop_duplicates("goal").best_moves.to_numpy()
            paint(ax.boxplot([optimum], positions=[len(STRATEGIES)], widths=width * 0.85, **BOX_STYLE), [OPTIMUM_COLOR])
            ticks.append("ótimo")
        ax.set_xticks(range(len(ticks)), ticks)
        if log:
            ax.set_yscale("log")
        ax.set_title(title, loc="left")
        ax.grid(axis="x", visible=False)
    algorithm_legend(fig, optimum=True)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    plt.show()


def boxplots(ax, runs, column, title):
    data, labels, colors = [], [], []
    for algorithm in ALGORITHMS:
        for strategy in STRATEGIES:
            data.append(_values(runs, algorithm, strategy, column))
            labels.append(combination_label(algorithm, strategy))
            colors.append(ALGORITHM_COLORS[algorithm])
    paint(ax.boxplot(data, **HORIZONTAL, widths=0.6, **BOX_STYLE), colors)
    ax.set_yticks(range(1, len(labels) + 1), labels)
    ax.set_title(title, loc="left")
    ax.grid(axis="y", visible=False)


def quality_chart():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4), sharey=True)
    boxplots(axes[0], goals_runs(), "extra_moves", "Movimentos acima do ótimo")
    boxplots(axes[1], goals_runs(), "extra_cost", "Custo acima do ótimo")
    axes[0].invert_yaxis()
    algorithm_legend(fig)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    plt.show()


def above_optimum():
    runs = goals_runs()
    for algorithm in ("breadth_first", "ordered"):
        selected = runs[(runs.algorithm == algorithm) & runs.success]
        for column, label in (("extra_moves", "movimentos"), ("extra_cost", "custo")):
            above = int((selected[column] > 0).sum())
            print(f"{ALGORITHM_LABELS[algorithm]:<9} acima do ótimo em {label:<10} {above:>2} de {len(selected)} execuções")


def best_by_criterion():
    def names(rows):
        return "; ".join(combination_label(row.algorithm, row.strategy) for row in rows)

    return pd.DataFrame(
        [
            {
                "Critério": theme.CRITERION_LABELS[item.criterion],
                "Melhor pela média": names(item.by_mean),
                "Melhor pela mediana": names(item.by_median),
            }
            for item in goals_report().summary.highlights
        ]
    ).set_index("Critério")


def permutation_check():
    runs = goals_runs()
    for algorithm in ("breadth_first", "ordered"):
        for strategy in STRATEGIES:
            selected = runs[(runs.algorithm == algorithm) & (runs.strategy == strategy)]
            positions = sorted(selected.iterations)
            print(f"{combination_label(algorithm, strategy):<24} iterações = 1..36: {positions == list(range(1, 37))}   média {selected.iterations.mean():.1f}")""",
    hidden=True,
)


def _complexity_table() -> str:
    rows = []
    for spec in ALGORITHM_SECTIONS:
        for line in spec.complexity.splitlines()[2:]:
            time, memory, name, reason, solution = (
                cell.strip() for cell in line.strip("|").split("|")
            )
            if "poda" in name:
                rows.append(f"| {name} | {time} | {memory} | {solution} | {reason} |")
    return "\n".join(
        (
            "| Algoritmo | Tempo | Memória | Solução | Por quê |",
            "|---|---|---|---|---|",
            *rows,
        )
    )


SYMBOLS = ("b", "d", "m", "V", "E", "C*", "ε")

P1_CELLS = (
    markdown(
        """## A carta P1

As 8 execuções de P1, ordenadas pelo placar lexicográfico: desfecho, movimentos, iterações e nós gerados, nessa ordem de prioridade."""
    ),
    code('p1_comparison().set_index("#")'),
    markdown(
        """### P1 em gráfico

Em cima, a carta P1. Embaixo, movimentos, iterações e nós gerados de cada algoritmo, agrupados por estratégia. A linha tracejada é o ótimo de P1 (3 movimentos)."""
    ),
    code("p1_chart()"),
    markdown(
        """Em P1, largura e ordenada acham o ótimo com as duas estratégias, e a ordenada com `ascending` é a mais rápida (10 iterações). O backtracking sempre chega, mas com 14 a 22 movimentos. A irrevogável, fora do gráfico, trava em `descending`. Uma carta, porém, é uma amostra de um: a próxima parte repete tudo para os 36 objetivos possíveis."""
    ),
)

ALL_GOALS_CELLS = (
    markdown(
        """## Todos os 36 objetivos

Cada estado do espaço vira o objetivo de uma carta sintética (G01 a G36), todas a partir da posição inicial: 36 cartas × 4 algoritmos × 2 estratégias = 288 execuções. O ótimo de cada carta vem dos oráculos de `state_space`, escritos fora do motor: `shortest_distance` (menor número de movimentos) e `cheapest_cost` (menor custo).

### Resumo consolidado

O mesmo resumo de `python main.py --all-goals`: para cada combinação, média / mediana. Movimentos e custo contam só os sucessos. A irrevogável resolve 18 objetivos com `ascending` e 3 com `descending`; os outros três algoritmos resolvem os 36."""
    ),
    code("goals_comparison()"),
    markdown(
        """### Os 36 objetivos em gráfico

O mesmo gráfico de P1, agora com as 36 execuções de cada combinação. A caixa vai do 1º ao 3º quartil, a barra preta é a mediana e o losango branco é a média. Em movimentos, a caixa cinza é o ótimo de cada objetivo. Iterações e nós gerados estão em escala logarítmica: o backtracking com `descending` passa de 2 mil iterações num objetivo."""
    ),
    code("goals_chart()"),
    markdown(
        """### Melhor por critério

Menor valor vence, pela média e pela mediana. Só concorre quem tem o maior número de sucessos, para a irrevogável não vencer resolvendo apenas os objetivos fáceis."""
    ),
    code("best_by_criterion()"),
    markdown(
        """### Qualidade da solução

Quanto cada solução passa do ótimo, em movimentos e em custo. Zero é a solução ótima."""
    ),
    code("quality_chart()"),
    code("above_optimum()"),
    markdown(
        """### Por que largura e ordenada têm a mesma média de iterações

As duas visitam cada estado no máximo uma vez e só encerram quando o objetivo vira o estado atual. Com a mesma estratégia, a ordem em que visitam os 36 estados não depende do objetivo: o objetivo i é encontrado na posição dele nessa ordem, que é uma permutação de 1 a 36. A média é (1 + 36) / 2 = 18,5 para qualquer ordem de visita. O critério que as separa é o número de nós gerados."""
    ),
    code("permutation_check()"),
)

COMPLEXITY_CELLS = (
    markdown(
        f"""## Complexidade dos quatro algoritmos

{_complexity_table()}

Os símbolos, com os valores medidos em P1:"""
    ),
    code(f"complexity_values(None, {SYMBOLS!r})"),
)

CONCLUSION = markdown(
    """## Análise

**Garantias.** Largura e ordenada resolvem os 36 objetivos com o número mínimo de movimentos, com qualquer estratégia. A ordenada também acha sempre o menor custo; a largura passa do menor custo em 9 das 72 execuções, porque conta movimentos e não olha o custo das regras. Isso confere com a teoria: largura é ótima em comprimento, ordenada é ótima em custo, e no empate de comprimento as duas coincidem.

**A irrevogável depende da estratégia.** Ela é barata (um nó gerado por iteração), mas não garante solução: resolve 18 ou 3 dos 36 objetivos conforme a estratégia. Quando resolve, o caminho pode ser bem mais longo que o ótimo.

**O backtracking sempre resolve, mas não bem.** O espaço é conexo, então o retrocesso sempre acha um caminho. Só que é o primeiro, não o mais curto: a média fica entre 12,8 e 16,5 movimentos, contra 4,14 do ótimo. O esforço é irregular: com `descending` a média de iterações é 82,9, enquanto a mediana fica em 21,5. Poucos objetivos exigem milhares de passos de ida e volta.

**Esforço.** Largura e ordenada empatam em iterações (média 18,5, pelo argumento da permutação acima) e ficam próximas em nós gerados. O backtracking com `ascending` gera menos nós, mas paga com as soluções mais longas de todas.

**Recomendação.** Para este problema, a busca ordenada é a escolha: resolve tudo, com o menor custo e o menor número de movimentos, com as mesmas iterações médias da largura e cerca de 7% mais nós gerados. Quando as regras têm o mesmo custo, a largura dá o mesmo resultado. A irrevogável e o backtracking servem para mostrar o que acontece sem memória da fronteira e sem garantia de otimalidade."""
)


def section(index: int) -> tuple[Cell, ...]:
    return (
        markdown(f"# {index}. {TITLE}\n\n{INTRO}"),
        *P1_CELLS,
        *ALL_GOALS_CELLS,
        *COMPLEXITY_CELLS,
        CONCLUSION,
    )
