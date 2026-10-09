from __future__ import annotations

from cells import Cell, code, markdown
from pages.algorithm import (
    ALGORITHM_SECTIONS,
    SLIDE_STRATEGIES,
    all_complexity_rows,
    complexity_table,
)

TITLE = "Comparação dos algoritmos"
GOALS = 36
COMBINATIONS = len(ALGORITHM_SECTIONS) * len(SLIDE_STRATEGIES)
LEFT_OUT = " e a ".join(
    spec.title.removeprefix("Busca ").lower()
    for spec in ALGORITHM_SECTIONS
    if not spec.complete
)

INTRO = f"""Uma carta só não diz qual método é melhor. Esta seção roda a matriz completa ({len(ALGORITHM_SECTIONS)} algoritmos × {len(SLIDE_STRATEGIES)} estratégias) primeiro na carta P1 e depois em todos os {GOALS} estados do espaço como objetivo, sempre a partir da mesma posição inicial (cartas G01 a G{GOALS}).

As tabelas trazem todos os algoritmos. Os gráficos deixam de fora a {LEFT_OUT}: elas não garantem solução, e uma execução sem caminho não tem movimentos para comparar."""

PLOT_HELPERS = code(
    """#@title Funções dos gráficos
from core.domain.state_space import shortest_distance
from core.rules.domain.base import CAPACITIES, Peg

ALGORITHMS = CHART_ALGORITHMS
STRATEGIES = SLIDE_STRATEGIES
# Até onde vai o eixo de cada boxplot dos 36 objetivos; o que passa disso
# aparece escrito na borda do gráfico.
GOAL_COLUMNS = {
    "iterations": ("Iterações", 120),
    "generated": ("Nós gerados", 80),
    "expanded": ("Nós expandidos", 120),
}


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
            ax.text(x, 0.45 + 0.9 * level, theme.disk_symbol(disk), ha="center", va="center", fontsize=9, fontweight="bold", color=WHITE, zorder=3)
    ax.plot([left - 0.6, left + 3.0], [0, 0], color=INK, linewidth=2)
    ax.text(left + 1.2, 3.25, title, ha="center", va="center", fontsize=11, color=BLACK)


def draw_problem(ax, problem):
    draw_state(ax, problem.initial, 0, f"INICIAL  {compact(problem.initial)}")
    ax.annotate("", xy=(5.2, 1.3), xytext=(3.8, 1.3), arrowprops={"arrowstyle": "-|>", "color": INK, "linewidth": 1.5})
    draw_state(ax, problem.goal, 6.4, f"OBJETIVO {problem.id}  {compact(problem.goal)}")
    ax.set_xlim(-1, 10)
    ax.set_ylim(-0.8, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")


def grouped_bars(ax, frame, column, title, missing=theme.ABSENT):
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
        for result in entry.results:
            rows.append(
                {
                    "goal": entry.problem_id,
                    "algorithm": result.algorithm,
                    "strategy": result.strategy,
                    "success": result.outcome.is_success,
                    "moves": result.solution_length,
                    "iterations": result.metrics.iterations,
                    "generated": result.metrics.nodes_generated,
                    "expanded": result.metrics.nodes_visited,
                    "best_moves": best_moves,
                }
            )
    runs = pd.DataFrame(rows)
    runs["extra_moves"] = runs.moves - runs.best_moves
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
    rows = [(algorithm, strategy) for algorithm in ALGORITHMS for strategy in STRATEGIES]
    data = [_values(runs, *row, column) for row in rows]
    paint(ax.boxplot(data, **HORIZONTAL, widths=0.6, **BOX_STYLE), [ALGORITHM_COLORS[name] for name, _ in rows])
    ax.set_yticks(range(1, len(rows) + 1), [label(*row, short=False) for row in rows])
    ax.set_title(title, loc="left")
    ax.grid(axis="y", visible=False)


def _goal_rows(algorithm, column):
    names = [algorithm, *(name for name in ALGORITHMS if name != algorithm)]
    rows = [(name, strategy) for name in names for strategy in STRATEGIES]
    runs = goals_runs()
    return sorted(rows, key=lambda row: round(_values(runs, *row, column).mean(), 9))


def goals_boxplot(algorithm, column):
    title, limit = GOAL_COLUMNS[column]
    runs = goals_runs()
    rows = _goal_rows(algorithm, column)
    data = [_values(runs, name, strategy, column) for name, strategy in rows]
    fig, ax = plt.subplots(figsize=(11, 4.2))
    paint(ax.boxplot(data, **HORIZONTAL, widths=0.6, **BOX_STYLE), [ALGORITHM_COLORS[name] for name, _ in rows])
    ax.set_yticks(range(1, len(rows) + 1), [label(name, strategy, short=False) for name, strategy in rows])
    for tick, (name, _) in zip(ax.get_yticklabels(), rows):
        tick.set_fontweight("bold" if name == algorithm else "normal")
    ax.set_xlim(0, limit)
    for position, values in enumerate(data, start=1):
        mean = values.mean()
        ax.annotate(br(mean, 1), xy=(mean, position), xytext=(0, 13), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold", color=BLACK)
        beyond = sorted(value for value in values if value > limit)
        if beyond:
            text = " e ".join(br(value) for value in beyond) + " →"
            ax.annotate(text, xy=(limit, position), xytext=(-4, 0), textcoords="offset points", ha="right", va="center", fontsize=9, color=INK)
    ax.invert_yaxis()
    ax.set_title(f"{title} nos {len(all_states())} objetivos", loc="left")
    ax.grid(axis="y", visible=False)
    plt.show()


def goals_stats(algorithm, column):
    runs = goals_runs()
    rows = []
    for name, strategy in _goal_rows(algorithm, column):
        values = pd.Series(_values(runs, name, strategy, column))
        rows.append(
            {
                "Combinação": label(name, strategy, short=False),
                "Mínimo": values.min(),
                "1º quartil": values.quantile(0.25),
                "Mediana": values.median(),
                "3º quartil": values.quantile(0.75),
                "Máximo": values.max(),
                "Média": round(values.mean(), 2),
            }
        )
    return pd.DataFrame(rows).set_index("Combinação")


def quality_chart():
    fig, ax = plt.subplots(figsize=(9, 4))
    boxplots(ax, goals_runs(), "extra_moves", "Movimentos acima do ótimo")
    ax.invert_yaxis()
    algorithm_legend(fig)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    plt.show()


def above_optimum():
    runs = goals_runs()
    for algorithm in ALGORITHMS:
        for strategy in STRATEGIES:
            selected = runs[(runs.algorithm == algorithm) & (runs.strategy == strategy) & runs.success]
            above = int((selected.extra_moves > 0).sum())
            print(f"{label(algorithm, strategy, short=False):<26} acima do ótimo em {above:>2} de {len(selected)} execuções")


def best_by_criterion():
    def names(rows):
        return "; ".join(label(row.algorithm, row.strategy, short=False) for row in rows)

    return pd.DataFrame(
        [
            {
                "Critério": theme.CRITERION_LABELS[item.criterion],
                "Melhor pela média": names(item.by_mean),
                "Melhor pela mediana": names(item.by_median),
            }
            for item in goals_report().summary.highlights
            if item.criterion != "cost"
        ]
    ).set_index("Critério")


def permutation_check():
    runs = goals_runs()
    positions = list(range(1, len(all_states()) + 1))
    for algorithm in ("breadth_first", "ordered"):
        for strategy in STRATEGIES:
            selected = runs[(runs.algorithm == algorithm) & (runs.strategy == strategy)]
            print(f"{label(algorithm, strategy, short=False):<26} iterações = 1..{len(positions)}: {sorted(selected.iterations) == positions!s:<5}   média {br(selected.iterations.mean(), 2)}")""",
    hidden=True,
)

P1_CELLS = (
    markdown(
        f"""## A carta P1

As {COMBINATIONS} execuções de P1, ordenadas pelo placar lexicográfico: desfecho, movimentos, iterações e nós gerados, nessa ordem de prioridade."""
    ),
    code('p1_comparison().set_index("#")'),
    markdown(
        """### P1 em gráfico

Em cima, a carta P1. Embaixo, movimentos, iterações e nós gerados de cada algoritmo, agrupados por estratégia. A linha tracejada é o ótimo de P1 (3 movimentos)."""
    ),
    code("p1_chart()"),
    markdown(
        """Em P1, largura, ordenada e gulosa acham o ótimo (3 movimentos) com as duas estratégias. A gulosa é a mais barata (4 iterações e 4 nós gerados), seguida da ordenada (4 iterações e 9 nós); a largura precisa de 12 a 14 iterações. O backtracking sempre chega, mas com 14 a 22 movimentos. A irrevogável, fora do gráfico, trava em `descending`. Uma carta, porém, é uma amostra de um: a próxima parte repete tudo para os 36 objetivos possíveis."""
    ),
)

ALL_GOALS_CELLS = (
    markdown(
        f"""## Todos os {GOALS} objetivos

Cada estado do espaço vira o objetivo de uma carta sintética (G01 a G{GOALS}), todas a partir da posição inicial: {GOALS} cartas × {COMBINATIONS} combinações = {GOALS * COMBINATIONS} execuções. O ótimo de cada carta vem do oráculo `shortest_distance` de `state_space`, escrito fora do motor.

### Resumo consolidado

O mesmo resumo de `python main.py --all-goals`: para cada combinação, média / mediana. Movimentos contam só os sucessos; como toda jogada custa 1, o custo é igual aos movimentos e fica de fora. A irrevogável resolve 18 objetivos com `ascending` e 3 com `descending`; a gulosa, 29 e 28; os outros três algoritmos resolvem os {GOALS}."""
    ),
    code("goals_comparison()"),
    markdown(
        """### Os 36 objetivos em gráfico

O mesmo gráfico de P1, agora com as 36 execuções de cada combinação. A caixa vai do 1º ao 3º quartil, a barra preta é a mediana e o losango branco é a média. Em movimentos, a caixa cinza é o ótimo de cada objetivo. Iterações e nós gerados estão em escala logarítmica: o backtracking com `descending` passa de 2 mil iterações num objetivo."""
    ),
    code("goals_chart()"),
    markdown(
        """### Melhor por critério

Menor valor vence, pela média e pela mediana. Só concorre quem tem o maior número de sucessos, para a irrevogável e a gulosa não vencerem resolvendo apenas os objetivos fáceis."""
    ),
    code("best_by_criterion()"),
    markdown(
        """### Qualidade da solução

Quanto cada solução passa do ótimo, em movimentos. Zero é a solução ótima."""
    ),
    code("quality_chart()"),
    code("above_optimum()"),
    markdown(
        """### Por que a largura tem sempre a mesma média de iterações

A largura visita cada estado no máximo uma vez e só encerra quando o objetivo vira o estado atual. Com a mesma estratégia, a ordem em que ela visita os 36 estados não depende do objetivo: o objetivo i é encontrado na posição dele nessa ordem, que é uma permutação de 1 a 36. A média é (1 + 36) / 2 = 18,5 para qualquer ordem de visita.

A ordenada quebra esse argumento: a heurística é medida em relação ao objetivo, então a ordem de visita muda com ele e a busca chega antes."""
    ),
    code("permutation_check()"),
)

COMPLEXITY_CELLS = (
    markdown(
        f"""## Complexidade dos algoritmos

{complexity_table(all_complexity_rows())}

Os símbolos, com os valores medidos em P1:"""
    ),
    code("complexity_values(None)"),
)

CONCLUSION = markdown(
    """## Análise

**Garantias.** A largura resolve os 36 objetivos com o mínimo de movimentos, com qualquer estratégia: como toda jogada custa 1, ela é ótima. A ordenada também resolve todos, mas ordena ABERTOS só pela heurística e por isso não garante o caminho mais curto: passa do mínimo em 2 (`ascending`) e 3 (`descending`) dos 36 objetivos.

**A heurística corta o esforço.** A ordenada faz em média 7,44 iterações e 13,4 nós gerados, contra 18,5 e 22 da largura. A diferença vem do argumento da permutação acima: a largura visita os estados numa ordem fixa, a ordenada vai na direção do objetivo.

**Sem memória, a heurística não basta.** A gulosa é a mais barata (6,0 e 5,33 iterações em média), mas, como a irrevogável, não guarda alternativas: resolve 29 e 28 dos 36 objetivos. Ainda assim é muito melhor que a irrevogável, que resolve 18 ou 3 conforme a estratégia.

**O backtracking sempre resolve, mas não bem.** O espaço é conexo, então o retrocesso sempre acha um caminho. Só que é o primeiro, não o mais curto: a média fica entre 12,8 e 16,5 movimentos, contra 4,14 do ótimo. O esforço é irregular: com `descending` a média de iterações é 82,9, enquanto a mediana fica em 21,5. Poucos objetivos exigem milhares de passos de ida e volta.

**Recomendação.** Para este problema, a busca ordenada é a escolha: resolve tudo, quase sempre com o mínimo de movimentos (média de 4,19 a 4,25, contra 4,14 do ótimo), com menos da metade das iterações da largura. Quando o caminho precisa ser o mais curto, a largura garante. A irrevogável, a gulosa e o backtracking mostram o que acontece sem memória da fronteira e sem garantia de otimalidade."""
)


def section(index: int) -> tuple[Cell, ...]:
    return (
        markdown(f"# {index}. {TITLE}\n\n{INTRO}"),
        *P1_CELLS,
        *ALL_GOALS_CELLS,
        *COMPLEXITY_CELLS,
        CONCLUSION,
    )
