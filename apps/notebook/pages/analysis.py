from __future__ import annotations

from cells import Notebook, code, markdown
from pages.common import ANALYSIS, VIEW_HELPERS, header, setup_note
from source import all_files, install_cell

INTRO = """Uma carta só não diz qual método é melhor. Esta página roda a matriz completa (4 algoritmos × 3 estratégias) primeiro na carta P1 e depois em todos os 36 estados do espaço como objetivo, sempre a partir da mesma posição inicial (cartas G01 a G36). Os gráficos comparam desfecho, qualidade da solução e esforço da busca, e a análise no fim só afirma o que as células verificam."""

PLOT_STYLE = code(
    """#@title Estilo dos gráficos
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

MATPLOTLIB_VERSION = tuple(int(part) for part in matplotlib.__version__.split(".")[:2])
HORIZONTAL = {"orientation": "horizontal"} if MATPLOTLIB_VERSION >= (3, 10) else {"vert": False}

ALGORITHMS = ("irrevocable", "backtracking", "breadth_first", "ordered")
STRATEGIES = ("ascending", "descending", "custom")
ALGORITHM_LABELS = {
    "irrevocable": "Irrevogável",
    "backtracking": "Backtracking",
    "breadth_first": "Largura",
    "ordered": "Ordenada",
}
STRATEGY_LABELS = {"ascending": "crescente", "descending": "decrescente", "custom": "custom"}
ALGORITHM_COLORS = {
    "irrevocable": "#2a78d6",
    "backtracking": "#eb6834",
    "breadth_first": "#1baf7a",
    "ordered": "#eda100",
}
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


def combination_label(algorithm, strategy):
    return f"{ALGORITHM_LABELS[algorithm]} · {STRATEGY_LABELS[strategy]}"


def legend_on_top(fig, axes):
    handles = [plt.Rectangle((0, 0), 1, 1, color=ALGORITHM_COLORS[name]) for name in ALGORITHMS]
    fig.legend(handles, [ALGORITHM_LABELS[name] for name in ALGORITHMS], loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.02))


def grouped_bars(ax, frame, column, title, missing="—"):
    width = 0.2
    positions = np.arange(len(STRATEGIES))
    for index, algorithm in enumerate(ALGORITHMS):
        values = [frame.loc[(algorithm, strategy), column] for strategy in STRATEGIES]
        heights = [0 if pd.isna(value) else value for value in values]
        bars = ax.bar(
            positions + (index - 1.5) * width,
            heights,
            width * 0.9,
            color=ALGORITHM_COLORS[algorithm],
        )
        labels = [missing if pd.isna(value) else f"{value:g}" for value in values]
        ax.bar_label(bars, labels=labels, fontsize=8, color=INK, padding=2)
    ax.set_xticks(positions, [STRATEGY_LABELS[name] for name in STRATEGIES])
    ax.set_title(title, loc="left")
    ax.grid(axis="x", visible=False)


def boxplots(ax, frame, column, title, *, log=False):
    order = [(algorithm, strategy) for algorithm in ALGORITHMS for strategy in STRATEGIES]
    data, labels, colors = [], [], []
    for algorithm, strategy in order:
        values = frame.loc[(frame.algorithm == algorithm) & (frame.strategy == strategy), column].dropna()
        if values.empty:
            continue
        data.append(values.to_numpy())
        labels.append(combination_label(algorithm, strategy))
        colors.append(ALGORITHM_COLORS[algorithm])
    parts = ax.boxplot(
        data,
        **HORIZONTAL,
        patch_artist=True,
        showmeans=True,
        widths=0.6,
        medianprops={"color": "#0b0b0b", "linewidth": 1.5},
        meanprops={"marker": "D", "markerfacecolor": "#ffffff", "markeredgecolor": "#0b0b0b", "markersize": 5},
        flierprops={"marker": "o", "markersize": 3, "markerfacecolor": MUTED, "markeredgecolor": "none"},
        whiskerprops={"color": MUTED},
        capprops={"color": MUTED},
    )
    for patch, color in zip(parts["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_edgecolor(color)
        patch.set_alpha(0.85)
    ax.set_yticks(range(1, len(labels) + 1), labels)
    ax.invert_yaxis()
    if log:
        ax.set_xscale("log")
    ax.set_title(title, loc="left")
    ax.grid(axis="y", visible=False)""",
    hidden=True,
)

P1_CELLS = (
    markdown(
        """## 1. A carta P1

As 12 execuções de P1, ordenadas pelo placar lexicográfico: desfecho, movimentos, iterações e nós gerados, nessa ordem de prioridade."""
    ),
    code(
        """from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from libs.inputs.selection import ExecutionRequest
from runner.pipeline import build_report

p1_report = build_report(
    ExecutionRequest(problem_ids=("P1",), algorithm_names=ALGORITHM_NAMES, strategy_names=STRATEGY_NAMES)
)
p1 = p1_report.problems[0]
leaderboard = pd.DataFrame(
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
        for row in p1.leaderboard.rows
    ]
).set_index("#").astype({LABELS["moves"]: "Int64", LABELS["cost"]: "Int64"})
leaderboard"""
    ),
    markdown(
        """Movimentos, iterações e nós gerados de cada algoritmo, agrupados por estratégia. A linha tracejada é o ótimo de P1 (3 movimentos); "impasse" marca as execuções sem solução."""
    ),
    code(
        """p1_frame = pd.DataFrame(
    [
        {
            "algorithm": result.algorithm,
            "strategy": result.strategy,
            "moves": result.solution_length,
            "iterations": result.metrics.iterations,
            "generated": result.metrics.nodes_generated,
        }
        for result in p1.results
    ]
).set_index(["algorithm", "strategy"]).astype({"moves": "Int64"})

fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
grouped_bars(axes[0], p1_frame, "moves", "Movimentos da solução (tracejado: ótimo)", missing="impasse")
axes[0].axhline(3, color=MUTED, linestyle="--", linewidth=1, zorder=0)
grouped_bars(axes[1], p1_frame, "iterations", "Iterações")
grouped_bars(axes[2], p1_frame, "generated", "Nós gerados")
legend_on_top(fig, axes)
fig.tight_layout(rect=(0, 0, 1, 0.92))
plt.show()"""
    ),
    markdown(
        """Em P1, largura e ordenada acham o ótimo com as três estratégias, e a ordenada com `ascending` é a mais rápida (10 iterações). A irrevogável trava em `descending` e `custom`. O backtracking sempre chega, mas com 14 a 22 movimentos. Uma carta, porém, é uma amostra de um: a próxima seção repete tudo para os 36 objetivos possíveis."""
    ),
)

ALL_GOALS_CELLS = (
    markdown(
        """## 2. Todos os 36 objetivos

Cada estado do espaço vira o objetivo de uma carta sintética (G01 a G36), todas a partir da posição inicial: 36 cartas × 4 algoritmos × 3 estratégias = 432 execuções. O ótimo de cada carta vem dos oráculos de `state_space`, escritos fora do motor: `shortest_distance` (menor número de movimentos) e `cheapest_cost` (menor custo)."""
    ),
    code(
        """from core.domain.state_space import cheapest_cost, shortest_distance

goals_report = build_report(
    ExecutionRequest(problem_ids=(), algorithm_names=ALGORITHM_NAMES, strategy_names=STRATEGY_NAMES, all_goals=True)
)
rows = []
for entry in goals_report.problems:
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
print(len(runs), "execuções")"""
    ),
    markdown(
        """### Resumo consolidado

O mesmo resumo de `python main.py --all-goals`: para cada combinação, média / mediana. Movimentos e custo contam só os sucessos."""
    ),
    code(
        """def stat(value):
    return theme.ABSENT if value is None else f"{value.mean:.2f} / {value.median:g}"


summary = pd.DataFrame(
    [
        {
            "Algoritmo": ALGORITHM_LABELS[row.algorithm],
            "Estratégia": STRATEGY_LABELS[row.strategy],
            "Sucessos": f"{row.successes}/{row.runs}",
            "Impasses": row.deadlocks,
            LABELS["moves"]: stat(row.moves),
            LABELS["cost"]: stat(row.cost),
            LABELS["iterations"]: stat(row.iterations),
            LABELS["nodes_generated"]: stat(row.nodes_generated),
        }
        for row in goals_report.summary.rows
    ]
)
summary"""
    ),
    markdown(
        """### Melhor por critério

Menor valor vence, pela média e pela mediana. Só concorre quem tem o maior número de sucessos, para a irrevogável não vencer resolvendo apenas os objetivos fáceis."""
    ),
    code(
        """def names(rows):
    return "; ".join(combination_label(row.algorithm, row.strategy) for row in rows)


pd.DataFrame(
    [
        {
            "Critério": theme.CRITERION_LABELS[item.criterion],
            "Melhor pela média": names(item.by_mean),
            "Melhor pela mediana": names(item.by_median),
        }
        for item in goals_report.summary.highlights
    ]
).set_index("Critério")"""
    ),
    markdown(
        """### Desfecho

Quantos dos 36 objetivos cada combinação resolve. Só a irrevogável deixa objetivos sem solução, e quanto deixa depende da estratégia."""
    ),
    code(
        """successes = runs.groupby(["algorithm", "strategy"]).success.sum()
labels = [combination_label(a, s) for a in ALGORITHMS for s in STRATEGIES]
values = [successes[(a, s)] for a in ALGORITHMS for s in STRATEGIES]
colors = [ALGORITHM_COLORS[a] for a in ALGORITHMS for s in STRATEGIES]

fig, ax = plt.subplots(figsize=(8, 4.2))
bars = ax.barh(labels, values, color=colors, height=0.7)
ax.bar_label(bars, labels=[f"{v}/36" for v in values], fontsize=8, color=INK, padding=3)
ax.invert_yaxis()
ax.set_xlim(0, 40)
ax.set_xlabel("objetivos resolvidos")
ax.set_title("Sucessos em 36 objetivos", loc="left")
ax.grid(axis="y", visible=False)
plt.show()"""
    ),
    markdown(
        """### Qualidade da solução

Quanto cada solução passa do ótimo, em movimentos e em custo, só nos sucessos. Zero é a solução ótima. A caixa vai do 1º ao 3º quartil, a barra preta é a mediana e o losango branco é a média."""
    ),
    code(
        """fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
boxplots(axes[0], runs, "extra_moves", "Movimentos acima do ótimo")
boxplots(axes[1], runs, "extra_cost", "Custo acima do ótimo")
legend_on_top(fig, axes)
fig.tight_layout(rect=(0, 0, 1, 0.94))
plt.show()"""
    ),
    code(
        """def count(algorithm, column):
    selected = runs[(runs.algorithm == algorithm) & runs.success]
    return int((selected[column] > 0).sum()), len(selected)


for algorithm in ("breadth_first", "ordered"):
    for column, label in (("extra_moves", "movimentos"), ("extra_cost", "custo")):
        above, total = count(algorithm, column)
        print(f"{ALGORITHM_LABELS[algorithm]:<9} acima do ótimo em {label:<10} {above:>2} de {total} execuções")"""
    ),
    markdown(
        """### Esforço da busca

Iterações e nós gerados de cada execução, em escala logarítmica. Quando o losango (média) se afasta da barra (mediana), poucos objetivos puxam a média: a mediana é a medida mais robusta."""
    ),
    code(
        """fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
boxplots(axes[0], runs, "iterations", "Iterações", log=True)
boxplots(axes[1], runs, "generated", "Nós gerados", log=True)
legend_on_top(fig, axes)
fig.tight_layout(rect=(0, 0, 1, 0.94))
plt.show()"""
    ),
    markdown(
        """### Por que largura e ordenada têm a mesma média de iterações

As duas visitam cada estado no máximo uma vez e só encerram quando o objetivo vira o estado atual. Com a mesma estratégia, a ordem em que visitam os 36 estados não depende do objetivo: o objetivo i é encontrado na posição dele nessa ordem, que é uma permutação de 1 a 36. A média é (1 + 36) / 2 = 18,5 para qualquer ordem de visita. O critério que as separa é o número de nós gerados."""
    ),
    code(
        """for algorithm in ("breadth_first", "ordered"):
    for strategy in STRATEGIES:
        selected = runs[(runs.algorithm == algorithm) & (runs.strategy == strategy)]
        positions = sorted(selected.iterations)
        print(f"{combination_label(algorithm, strategy):<24} iterações = 1..36: {positions == list(range(1, 37))}   média {selected.iterations.mean():.1f}")"""
    ),
)

CONCLUSION = markdown(
    """## 3. Análise

**Garantias.** Largura e ordenada resolvem os 36 objetivos com o número mínimo de movimentos, com qualquer estratégia. A ordenada também acha sempre o menor custo; a largura passa do menor custo em 2 das 108 execuções, porque conta movimentos e não olha o custo das regras. Isso confere com a teoria: largura é ótima em comprimento, ordenada é ótima em custo, e no empate de comprimento as duas coincidem.

**A irrevogável depende da estratégia.** Ela é barata (um nó gerado por iteração), mas não garante solução: resolve 18, 7 ou 3 dos 36 objetivos conforme a estratégia. Quando resolve, o caminho pode ser bem mais longo que o ótimo.

**O backtracking sempre resolve, mas não bem.** O espaço é conexo, então o retrocesso sempre acha um caminho. Só que é o primeiro, não o mais curto: a média fica entre 12 e 16,5 movimentos, contra 4,14 do ótimo. O esforço é irregular: com `custom` a média de iterações passa de 200, enquanto a mediana fica perto de 20. Poucos objetivos exigem milhares de passos de ida e volta.

**Esforço.** Largura e ordenada empatam em iterações (média 18,5, pelo argumento da permutação acima) e ficam próximas em nós gerados. O backtracking com `ascending` gera menos nós, mas paga com as soluções mais longas de todas.

**Recomendação.** Para este problema, a busca ordenada é a escolha: resolve tudo, com o menor custo e o menor número de movimentos, e com esforço igual ao da largura. Quando as regras têm o mesmo custo, a largura dá o mesmo resultado. A irrevogável e o backtracking servem para mostrar o que acontece sem memória da fronteira e sem garantia de otimalidade."""
)


def build() -> Notebook:
    return Notebook(
        ANALYSIS.filename,
        ANALYSIS.title,
        (
            header(ANALYSIS, INTRO),
            setup_note(),
            install_cell("Grava o código do projeto", all_files()),
            VIEW_HELPERS,
            PLOT_STYLE,
            *P1_CELLS,
            *ALL_GOALS_CELLS,
            CONCLUSION,
        ),
    )
