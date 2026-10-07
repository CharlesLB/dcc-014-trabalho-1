from __future__ import annotations

from cells import Cell, Notebook, code, markdown
from pages.common import (
    BACKTRACKING,
    BREADTH_FIRST,
    COLAB_BASE,
    IRREVOCABLE,
    ORDERED,
    PROJECT,
    header,
)
from source import (
    FOLDERS,
    SOURCE_DIR,
    entry_point,
    files_in,
    install_cell,
    writefile_cell,
)

INTRO = """Resolvedor do problema da Torre de Londres (3 hastes, 3 discos) com busca irrevogável, backtracking, busca em largura e busca ordenada sobre uma mesma abstração de árvore de busca. A estratégia de controle é um parâmetro, as métricas são coletadas pelo motor e um placar compara as execuções.

Esta página segue a árvore de `src/` pasta por pasta, na mesma ordem do repositório. Cada célula de código grava um arquivo no mesmo caminho que ele tem no projeto. No fim, uma demonstração usa o que foi gravado. Cada algoritmo tem uma página própria, e os gráficos e a análise ficam na última página."""

STRUCTURE = """## Estrutura

```
src/
├── core/                      problema e motor
│   ├── rules/
│   │   ├── domain/            tipos, restrições, catálogo, erros
│   │   ├── moves.py           R1..R6
│   │   └── strategies/
│   │       ├── domain/        contrato e registro
│   │       ├── ascending.py
│   │       ├── descending.py
│   │       └── custom_order.py
│   ├── domain/                estados, invariantes, cartas, enumeração
│   ├── search_tree/           nó, árvore, fronteira, caminho, métricas, trace
│   └── algorithms/
│       ├── domain/            contrato e registro
│       ├── irrevocable.py
│       ├── backtracking.py
│       ├── breadth_first.py
│       └── ordered.py
├── libs/                      bibliotecas de borda
│   ├── inputs/                linha de comando → requisição validada
│   ├── outputs/               única camada que escreve no terminal e em disco
│   └── ranking/               placar por carta e resumo consolidado
├── runner/                    orquestração; conhece todas as outras camadas
└── config/                    limites, padrões e textos da interface
```

Regra de dependência: `core/rules/  ←  core/  ←  runner/  →  libs/`. O `core/` não conhece `libs/` nem `runner/`, e `core/search_tree/` não conhece `core/algorithms/`. No repositório, um teste verifica isso na AST.

Não há `__init__.py`: as pastas são pacotes de namespace. O código não tem comentários nem docstrings de função, e a modelagem do problema fica documentada no topo dos módulos que a carregam."""

PREPARE = code(
    f"""import sys
from pathlib import Path

for folder in {FOLDERS!r}:
    Path("{SOURCE_DIR}", folder).mkdir(parents=True, exist_ok=True)

if str(Path("{SOURCE_DIR}").resolve()) not in sys.path:
    sys.path.insert(0, str(Path("{SOURCE_DIR}").resolve()))
print("pastas criadas em", Path("{SOURCE_DIR}").resolve())"""
)

SECTIONS: tuple[tuple[str, str], ...] = (
    (
        "config",
        """## config/

Limites, padrões e os textos da interface. `MAX_ITERATIONS` é a guarda contra execução patológica: estourar o limite encerra qualquer busca com LIMITE.""",
    ),
    (
        "core/rules/domain",
        """## core/

O problema e o motor de busca. Nada aqui escreve na tela nem lê argumentos.

### core/rules/

As regras ficam num pacote próprio, lido antes de tudo, e não importam nada do projeto fora dele. Trocar o problema é trocar as regras, não o motor.

#### core/rules/domain/

Os primitivos do domínio (discos, hastes, capacidades e o tipo `State`), as duas restrições estáticas de um movimento, o catálogo das seis regras e os erros.""",
    ),
    (
        "core/rules",
        """#### core/rules/moves.py

As seis regras R1 a R6, uma por par origem e destino. Cada uma custa a distância entre as hastes que liga.""",
    ),
    (
        "core/rules/strategies/domain",
        """#### core/rules/strategies/

A estratégia de controle decide em que ordem as regras aplicáveis são tentadas. É um parâmetro de entrada, não parte do algoritmo.

##### core/rules/strategies/domain/

O contrato `ControlStrategy` e o registro por nome.""",
    ),
    (
        "core/rules/strategies",
        """##### As três estratégias

`ascending` tenta R1 → R6, `descending` tenta R6 → R1 e `custom` segue uma ordem dada (por padrão R2, R4, R6, R1, R3, R5).""",
    ),
    (
        "core/domain",
        """### core/domain/

Estados e invariantes, o catálogo de cartas e a enumeração exaustiva dos 36 estados, que serve de oráculo independente aos testes.""",
    ),
    (
        "core/search_tree",
        """### core/search_tree/

A mecânica da árvore, compartilhada pelos quatro algoritmos: nó, árvore, fronteira (pilha, fila e fila de prioridade), caminho, métricas, trace e resultado.""",
    ),
    (
        "core/algorithms/domain",
        """### core/algorithms/

#### core/algorithms/domain/

`SearchAlgorithm` é o motor: visita, gera, poda, conta e registra. Cada algoritmo implementa só o próprio laço em `_search`. O registro liga cada nome à sua classe.""",
    ),
)

ALGORITHMS_NOTE = f"""#### Os quatro algoritmos

Cada algoritmo tem uma página com o código, a execução passo a passo em P1, a árvore de busca e o caminho solução:

- [{IRREVOCABLE.title}]({COLAB_BASE}/{IRREVOCABLE.filename}): `irrevocable.py`
- [{BACKTRACKING.title}]({COLAB_BASE}/{BACKTRACKING.filename}): `backtracking.py`
- [{BREADTH_FIRST.title}]({COLAB_BASE}/{BREADTH_FIRST.filename}): `breadth_first.py`
- [{ORDERED.title}]({COLAB_BASE}/{ORDERED.filename}): `ordered.py`

A célula a seguir só os grava, porque o registro acima importa os quatro."""

EDGE_SECTIONS: tuple[tuple[str, str], ...] = (
    (
        "libs/inputs",
        """## libs/

Bibliotecas de borda: entrada, saída e placar. O `core/` não as conhece.

### libs/inputs/

Linha de comando → requisição validada (`ExecutionRequest`).""",
    ),
    (
        "libs/outputs",
        """### libs/outputs/

A única camada que escreve no terminal e em disco: console, JSON, desenho dos estados, árvore em texto, trace em tabela e árvore em DOT para o Graphviz.""",
    ),
    (
        "libs/ranking",
        """### libs/ranking/

O placar de cada carta (lexicográfico ou por escore) e o resumo consolidado com média e mediana.""",
    ),
    (
        "runner",
        """## runner/

A orquestração: executa a matriz carta × algoritmo × estratégia, monta o relatório e chama a saída. É a única camada que conhece todas as outras.""",
    ),
)

DEMO: tuple[Cell, ...] = (
    markdown(
        """## Demonstração

### O problema

A posição inicial é fixa pelo aparato. Cada carta define um objetivo a alcançar a partir dela."""
    ),
    code(
        """from core.domain.problem import INITIAL_STATE, PROBLEMS
from libs.outputs import state_render

print("Posição inicial")
print(state_render.render_pegs(INITIAL_STATE))
for problem in PROBLEMS:
    print()
    print(f"Objetivo da carta {problem.id}")
    print(state_render.render_pegs(problem.goal))"""
    ),
    markdown(
        """### O espaço de estados

3! = 6 arranjos × 6 distribuições permitidas pelas capacidades (3, 2, 1) = 36 estados. O grafo é conexo: todo estado alcança todo estado."""
    ),
    code(
        """from core.domain.state_space import all_states, cheapest_cost, reachable_from, shortest_distance

states = all_states()
print("estados válidos:", len(states))
print("alcançáveis da posição inicial:", len(reachable_from(INITIAL_STATE)))
p1 = PROBLEMS[0]
print("menor número de movimentos até P1:", shortest_distance(p1.initial, p1.goal))
print("menor custo até P1:", cheapest_cost(p1.initial, p1.goal))"""
    ),
    markdown(
        """### Regras e estratégias

As regras aplicáveis na posição inicial, com o custo de cada uma, e a ordem em que cada estratégia as tenta."""
    ),
    code(
        """from core.domain.state_space import applicable_rules
from core.rules.domain.catalog import RULES
from core.rules.strategies.domain.registry import STRATEGIES

applicable = applicable_rules(INITIAL_STATE)
for rule in RULES:
    mark = "✓" if rule in applicable else "✗"
    print(f"{rule.id}  {rule.origin.name} → {rule.destination.name}  custo {rule.cost}  {mark}")
print()
for name, strategy in STRATEGIES.items():
    print(f"{name:<11}", " → ".join(rule.id for rule in strategy.order(applicable)))"""
    ),
    markdown(
        """### A linha de comando

O mesmo `main.py` do repositório roda aqui. `--help` lista todas as opções."""
    ),
    code(
        "!python main.py --problem P1 --algorithm breadth_first --strategy ascending --show-states"
    ),
)


def build() -> Notebook:
    cells: list[Cell] = [
        header(PROJECT, INTRO),
        markdown(STRUCTURE),
        markdown(
            "## Preparação\n\nCria as pastas de `src/` e põe `src/` no `sys.path`. Rode as células desta página em ordem."
        ),
        PREPARE,
    ]
    for folder, text in SECTIONS:
        cells.append(markdown(text))
        cells.extend(writefile_cell(item) for item in files_in(folder))
    cells.append(markdown(ALGORITHMS_NOTE))
    cells.append(
        install_cell("Grava os quatro algoritmos", files_in("core/algorithms"))
    )
    for folder, text in EDGE_SECTIONS:
        cells.append(markdown(text))
        cells.extend(writefile_cell(item) for item in files_in(folder))
    cells.append(
        markdown(
            "## main.py\n\nO ponto de entrada da linha de comando: põe `src/` no caminho e chama o `runner`."
        )
    )
    cells.append(writefile_cell(entry_point()))
    cells.extend(DEMO)
    return Notebook(PROJECT.filename, PROJECT.title, tuple(cells))
