# Torre de Londres — Especificação Técnica

**Versão:** 1.0
**Disciplina:** Inteligência Artificial — Espaço de Busca, Busca Irrevogável, Backtracking e Busca em Largura
**Problema:** Problema 5 — Torres de Londres (3 hastes, 3 discos)
**Linguagem:** Python 3.12+

---

## 1. Objetivo

Construir um resolvedor do problema da Torre de Londres que:

1. Represente formalmente o **espaço de estados** e o **espaço de busca** do problema.
2. Implemente múltiplos **métodos de busca** (irrevogável, backtracking, largura) sobre uma mesma abstração de árvore de busca.
3. Permita variar a **estratégia de controle** (critério de ordenação das regras de transição) independentemente do algoritmo.
4. Instrumente cada execução com **métricas** (iterações, nós gerados, nós visitados, impasses, retrocessos, profundidade).
5. **Ranqueie** as execuções, evidenciando o resultado didático central: o método irrevogável pode falhar onde o backtracking tem sucesso, e a busca em largura garante o caminho mais curto.

O projeto é uma implementação de referência: código de produção em qualidade sênior aplicado a um problema acadêmico.

---

## 2. Modelagem do problema

### 2.1 Elementos

| Elemento | Definição |
|---|---|
| Discos | 3, distintos por cor: `VERDE`, `VERMELHO`, `AZUL` |
| Hastes | `H1`, `H2`, `H3` |
| Capacidades | `H1 = 3`, `H2 = 2`, `H3 = 1` |

**Ponto crítico da modelagem:** ao contrário da Torre de Hanói, **não há ordenação por tamanho**. Qualquer disco pode repousar sobre qualquer outro. A única restrição estrutural é a **capacidade** de cada haste. Isso muda completamente o espaço de estados e deve estar explícito no código, não implícito.

### 2.2 Representação do estado

Um estado é uma tupla de três pilhas, cada pilha ordenada da **base para o topo**:

```python
State = tuple[tuple[Disk, ...], tuple[Disk, ...], tuple[Disk, ...]]
```

Exemplo — todos os discos em H1, com `AZUL` no topo:

```python
((VERDE, VERMELHO, AZUL), (), ())
```

Propriedades exigidas da representação:

- **Imutável** — `tuple` de `tuple`, nunca `list`. Uma transição produz um estado novo; nenhum algoritmo pode corromper o estado de outro.
- **Hashable** — indispensável para o teste de "estado já presente no caminho" em `O(1)` e para o conjunto de fechados da busca em largura.
- **Comparável por igualdade estrutural** — dois estados com a mesma configuração são o mesmo estado, independentemente de identidade de objeto.
- **Canônica** — não existem duas representações distintas para a mesma configuração física.

### 2.3 Regras de transição de estado

Seis regras, uma para cada par ordenado de hastes distintas:

| Regra | Origem | Destino |
|---|---|---|
| R1 | H1 | H2 |
| R2 | H1 | H3 |
| R3 | H2 | H1 |
| R4 | H2 | H3 |
| R5 | H3 | H1 |
| R6 | H3 | H2 |

Toda regra move **o disco do topo** da haste de origem para o **topo** da haste de destino.

### 2.4 Condições de validade

Uma regra `R(origem → destino)` é **aplicável** a um estado `s` se e somente se:

1. **Origem não vazia** — `len(s[origem]) >= 1` no momento exato da ação.
2. **Capacidade do destino respeitada** — `len(s[destino]) + 1 <= capacidade(destino)`.

Essas duas condições são **estáticas**: dependem apenas do estado corrente. Vivem em `rules/constraints.py` e são avaliadas por `Rule.is_applicable(state)`.

### 2.5 A terceira condição — e por que ela NÃO mora em `rules/`

O material define uma terceira condição para a busca: a regra não pode produzir um estado **já presente no caminho entre a raiz e o vértice atual**.

Essa condição é **contextual**, não estática: depende do caminho percorrido, não do estado. Colocá-la junto às restrições do problema é o erro estrutural mais comum neste tipo de projeto — acopla o domínio ao histórico da busca e impede que a mesma regra seja reaproveitada por algoritmos com políticas de repetição diferentes (a busca em largura usa um conjunto global de fechados, não o caminho).

**Decisão:** a condição 3 vive em `core/search/path.py` e é aplicada pelo algoritmo, não pela regra.

### 2.6 Propriedades do espaço de estados

Fatos que a implementação deve respeitar e os testes devem verificar:

- **Estados válidos: 36.** Sem restrição de capacidade seriam 60 arranjos (`3 × 4 × 5`, fatorial crescente para 3 itens distintos em 3 pilhas ordenadas). As distribuições que respeitam `(≤3, ≤2, ≤1)` são `(3,0,0)`, `(2,1,0)`, `(2,0,1)`, `(1,2,0)`, `(1,1,1)`, `(0,2,1)` — seis distribuições × `3! = 6` arranjos = **36**.
- **Grafo não dirigido.** Toda regra tem inversa exata: `R1↔R3`, `R2↔R5`, `R4↔R6`. Se `s → s'` é aplicável, `s' → s` também é.
- **Grafo conexo.** Consequência das duas anteriores: **todo estado objetivo é alcançável a partir de qualquer estado inicial**. Portanto o backtracking e a busca em largura sempre terminam em SUCESSO; apenas o método irrevogável pode terminar em IMPASSE.
- **Fator de ramificação:** entre 2 e 4 regras aplicáveis por estado.
- **Profundidade máxima de um caminho sem repetição:** 36.

O espaço é pequeno o bastante para permitir **verificação exaustiva nos testes** — uma vantagem rara que a suíte deve explorar.

### 2.7 Estado inicial e estado objetivo

```python
# core/domain/problem.py
INITIAL_STATE: State = ((VERDE, VERMELHO, AZUL), (), ())
GOAL_STATE: State = ((), (VERMELHO, VERDE), (AZUL,))
```

> **⚠ PONTO DE CONFIRMAÇÃO** — estas duas constantes correspondem à carta do problema e são o **único** ponto do sistema a ser ajustado se a configuração da carta for outra. Nenhum algoritmo, teste ou métrica depende de valores específicos: a suíte é escrita para ser agnóstica ao objetivo (ver §9.4). Confirme a carta antes da entrega e altere apenas este arquivo.

O estado inicial é fixo. O objetivo é único. Não há `data/problems/` — externalizar em YAML um problema que nunca muda é complexidade sem retorno. A definição é código, versionada e tipada.

---

## 3. Decisões arquiteturais

| # | Decisão | Justificativa |
|---|---|---|
| ADR-01 | Regras no **topo** do projeto, fora de `core/` | São a definição do problema, o insumo mais revisado pelo professor. Devem ser lidas primeiro, sem navegar por camadas. |
| ADR-02 | Estratégia de controle é **parâmetro de entrada**, não propriedade do algoritmo | O Cap. 3 afirma explicitamente que a estratégia é parâmetro de entrada do algoritmo de busca. A atividade da semana exige rodar o *mesmo* algoritmo com ordenação crescente e decrescente. |
| ADR-03 | Mecânica da árvore em `core/search/`, compartilhada | A árvore de busca é do domínio da busca, não de um algoritmo. Cada algoritmo decide apenas *como percorrê-la*. |
| ADR-04 | Estado imutável e hashable | Evita aliasing entre ramos da árvore; permite verificação de ciclo em `O(1)`. |
| ADR-05 | Condição de não repetição em `search/path.py`, não em `rules/` | Restrição contextual ≠ restrição do problema (§2.5). |
| ADR-06 | `inputs/` e `outputs/` como diretórios irmãos, **não** `io/` | `io` colide com o módulo homônimo da stdlib em layout flat, quebrando imports de terceiros. Dois diretórios também espelham literalmente o requisito de "uma lib para output e outra para input". |
| ADR-07 | `ranking/` fora de `core/` | Ranquear é política de apresentação de resultados, não parte do motor de busca. `core/` não conhece `ranking/`. |
| ADR-08 | Layout flat, sem pacote wrapper | Projeto de escopo fechado, entregue como repositório; um nível a menos de indireção. |
| ADR-09 | Métricas coletadas pelo **motor**, não pelos algoritmos | Se cada algoritmo contasse suas próprias iterações, a comparação seria inválida. Um único contador, uma única definição. |
| ADR-10 | Zero dependências de runtime obrigatórias | `rich` é opcional para renderização; o núcleo roda em stdlib pura. |

### 3.1 Regra de dependência

```
rules/  ←  core/  ←  runner/  →  outputs/
                ↑         ↓
            inputs/    ranking/
```

- `core/` importa `rules/`. **Nunca** o contrário.
- `ranking/`, `inputs/` e `outputs/` importam `core/`. **Nunca** o contrário.
- `runner/` é a única camada que conhece todas as outras.
- Violações dessa regra são detectadas por teste automatizado (§9.6).

---

## 4. Estrutura de diretórios

```
torre-de-londres/
├── pyproject.toml
├── README.md
├── Makefile
├── .python-version
├── .gitignore
├── main.py                         # entrypoint: delega para runner.cli
│
├── rules/                          # ── DEFINIÇÃO DO PROBLEMA ──
│   ├── __init__.py
│   ├── base.py                     # TransitionRule (Protocol)
│   ├── moves.py                    # R1..R6
│   ├── constraints.py              # origem não-vazia + capacidade
│   ├── catalog.py                  # RULES, ordem canônica R1..R6
│   ├── exceptions.py               # RuleNotApplicableError
│   └── strategies/                 # estratégias de controle
│       ├── __init__.py
│       ├── base.py                 # ControlStrategy (Protocol)
│       ├── ascending.py            # R1 → R6
│       ├── descending.py           # R6 → R1
│       ├── custom_order.py         # ordem arbitrária parametrizável
│       └── registry.py             # nome → estratégia
│
├── core/                           # ── MOTOR ──
│   ├── __init__.py
│   ├── domain/                     # estrutura do problema e estados
│   │   ├── __init__.py
│   │   ├── disk.py                 # enum Disk
│   │   ├── peg.py                  # enum Peg + CAPACITIES
│   │   ├── state.py                # State, factories, invariantes
│   │   ├── problem.py              # INITIAL_STATE, GOAL_STATE, is_goal
│   │   └── state_space.py          # enumeração exaustiva (testes/análise)
│   │
│   ├── search/                     # mecânica compartilhada da árvore
│   │   ├── __init__.py
│   │   ├── node.py                 # Node: estado, pai, regra, profundidade
│   │   ├── tree.py                 # SearchTree: raiz, expansão, ancestrais
│   │   ├── frontier.py             # Frontier / StackFrontier / QueueFrontier
│   │   ├── path.py                 # caminho raiz→nó, teste de repetição
│   │   ├── metrics.py              # SearchMetrics (contadores)
│   │   ├── trace.py                # log passo a passo da execução
│   │   ├── outcome.py              # enum: SUCCESS | DEADLOCK | FAILURE | CUTOFF
│   │   └── result.py               # SearchResult (agregado imutável)
│   │
│   └── algorithms/                 # ── ALGORITMOS ──
│       ├── __init__.py
│       ├── base.py                 # SearchAlgorithm (ABC) + template method
│       ├── registry.py             # nome → algoritmo
│       ├── irrevocable.py
│       ├── backtracking.py
│       └── breadth_first.py
│
├── inputs/                         # ── LIB DE ENTRADA ──
│   ├── __init__.py
│   ├── selection.py                # ExecutionRequest (o que rodar)
│   ├── parser.py                   # argv → ExecutionRequest
│   ├── validator.py                # nomes existem no registry?
│   └── exceptions.py
│
├── outputs/                        # ── LIB DE SAÍDA ──
│   ├── __init__.py
│   ├── formatter.py                # Formatter (Protocol)
│   ├── console.py                  # tabelas e relatórios em texto
│   ├── json_writer.py              # export estruturado
│   ├── state_render.py             # desenho ASCII das hastes
│   ├── tree_render.py              # árvore de busca em ASCII
│   ├── trace_render.py             # passo a passo
│   └── theme.py                    # símbolos, cores, larguras
│
├── ranking/                        # ── FORA DO CORE ──
│   ├── __init__.py
│   ├── criteria.py                 # critérios individuais
│   ├── scorer.py                   # composição ponderada
│   ├── comparator.py               # ordenação lexicográfica
│   └── leaderboard.py              # tabela final ordenada
│
├── runner/                         # ── ORQUESTRAÇÃO ──
│   ├── __init__.py
│   ├── cli.py                      # interface de linha de comando
│   ├── executor.py                 # matriz algoritmo × estratégia
│   └── pipeline.py                 # input → execução → ranking → output
│
├── config/
│   ├── __init__.py
│   ├── settings.py                 # limites, defaults
│   └── logging.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── rules/
│   │   │   ├── test_moves.py
│   │   │   ├── test_constraints.py
│   │   │   ├── test_catalog.py
│   │   │   └── test_strategies.py
│   │   ├── domain/
│   │   │   ├── test_state.py
│   │   │   ├── test_problem.py
│   │   │   └── test_state_space.py
│   │   ├── search/
│   │   │   ├── test_node.py
│   │   │   ├── test_path.py
│   │   │   ├── test_frontier.py
│   │   │   └── test_metrics.py
│   │   ├── algorithms/
│   │   │   ├── test_contract.py    # parametrizado sobre TODOS
│   │   │   ├── test_irrevocable.py
│   │   │   ├── test_backtracking.py
│   │   │   └── test_breadth_first.py
│   │   ├── ranking/
│   │   └── outputs/
│   ├── integration/
│   │   ├── test_matrix.py          # algoritmo × estratégia
│   │   └── test_pipeline.py
│   ├── e2e/
│   │   └── test_cli.py
│   ├── properties/
│   │   ├── test_reversibility.py
│   │   ├── test_reachability.py
│   │   └── test_optimality.py
│   ├── architecture/
│   │   └── test_dependencies.py
│   └── fixtures/
│
└── docs/
    ├── spec.md                     # este documento
    ├── modelagem.md                # espaço de estados para o relatório
    └── adr/
```

---

## 5. Contratos

### 5.1 `rules/base.py`

```python
class TransitionRule(Protocol):
    id: str  # "R1".."R6"
    origin: Peg
    destination: Peg

    def is_applicable(self, state: State) -> bool:
        """Verdadeiro se as condições estáticas (§2.4) são satisfeitas."""

    def apply(self, state: State) -> State:
        """Novo estado. Levanta RuleNotApplicableError se não aplicável."""
```

`apply` **não** verifica silenciosamente: chamar `apply` sobre estado inválido é erro de programação e falha alto. `is_applicable` é o guarda.

### 5.2 `rules/strategies/base.py`

```python
class ControlStrategy(Protocol):
    name: str

    def order(self, rules: Sequence[TransitionRule]) -> Sequence[TransitionRule]:
        """Ordena as regras aplicáveis segundo o critério de escolha."""
```

Estática por definição: ordena o conjunto de regras, sem consultar o estado. Mantém-se fiel ao material e garante determinismo. `custom_order` cobre ordenações arbitrárias sem quebrar o contrato.

### 5.3 `core/search/node.py`

```python
@dataclass(frozen=True, slots=True)
class Node:
    state: State
    parent: Node | None
    rule: TransitionRule | None  # regra que gerou este nó
    depth: int
    order: int  # ordem de criação na árvore
```

### 5.4 `core/search/frontier.py`

```python
class Frontier(Protocol):
    def push(self, node: Node) -> None: ...
    def pop(self) -> Node: ...
    def __len__(self) -> int: ...
```

`StackFrontier` (LIFO) para backtracking; `QueueFrontier` (FIFO) para largura. É aqui que a disciplina de exploração se materializa — não em `if` espalhados pelos algoritmos.

### 5.5 `core/search/metrics.py`

Definições fechadas, aplicadas identicamente a todos os algoritmos:

```python
@dataclass
class SearchMetrics:
    iterations: int  # ciclos do laço principal
    nodes_generated: int  # nós criados na árvore
    nodes_visited: int  # nós explorados (expandidos)
    rules_tested: int  # chamadas a is_applicable
    backtracks: int  # retrocessos (0 para irrevogável e largura)
    deadlocks: int  # folhas de impasse atingidas
    max_depth: int
    elapsed_ms: float
```

### 5.6 `core/search/result.py`

```python
@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    strategy: str
    outcome: Outcome  # SUCCESS | DEADLOCK | FAILURE | CUTOFF
    solution_path: tuple[Node, ...]  # vazio se não houve sucesso
    applied_rules: tuple[str, ...]  # ["R2", "R6", ...]
    metrics: SearchMetrics
    trace: Trace
```

### 5.7 `core/algorithms/base.py`

```python
class SearchAlgorithm(ABC):
    name: str

    def __init__(
        self,
        tree: SearchTree,
        strategy: ControlStrategy,
        *,
        max_iterations: int = settings.MAX_ITERATIONS,
    ) -> None: ...

    def solve(self, problem: Problem) -> SearchResult:
        """Template method: prepara métricas, delega, sela o resultado."""

    @abstractmethod
    def _search(self, problem: Problem) -> Outcome:
        """Ponto de variação: a disciplina de exploração."""

    def _applicable_rules(self, node: Node) -> Sequence[TransitionRule]:
        """Regras aplicáveis (§2.4), ordenadas pela estratégia,
        filtradas pela política de repetição do algoritmo."""
```

`solve` é `final` na prática: instrumentação, guarda de iterações e selagem do resultado são idênticos para todos, o que torna a comparação legítima (ADR-09). Cada algoritmo só implementa `_search`.

---

## 6. Algoritmos

### 6.1 Busca irrevogável

Gera **um único filho** por vértice, escolhido pela estratégia. Não retrocede.

```
nó ← raiz
enquanto verdadeiro:
    se nó.estado é objetivo: SUCESSO
    aplicáveis ← regras aplicáveis a nó, ordenadas pela estratégia,
                 excluindo as que geram estado já no caminho raiz→nó
    se aplicáveis vazio: IMPASSE
    nó ← expandir(nó, aplicáveis[0])
```

Terminação: o caminho é acíclico e o espaço tem 36 estados, logo o laço termina em no máximo 36 iterações. **Não garante solução**; quando encontra, não há garantia de que seja a mais curta.

### 6.2 Backtracking

Versão melhorada da irrevogável: ao atingir impasse, retrocede ao ancestral mais próximo com regra não tentada.

```
empilhar(raiz)
enquanto pilha não vazia:
    nó ← topo
    se nó.estado é objetivo: SUCESSO
    próxima ← próxima regra não tentada de nó (ordem da estratégia),
              que não gere estado já no caminho raiz→nó
    se próxima existe:
        empilhar(expandir(nó, próxima))
    senão:
        desempilhar(nó); backtracks += 1
        se nó é folha sem filhos: deadlocks += 1
FALHA  (pilha esvaziada)
```

Exaustivo sobre caminhos acíclicos: dada a conexidade do grafo (§2.6), **sempre termina em SUCESSO** neste problema. A primeira solução encontrada não é necessariamente a mais curta.

### 6.3 Busca em largura

Gera **todos** os filhos de uma vez; explora na ordem de criação. Mantém abertos (fila) e fechados (conjunto).

```
abertos ← fila([raiz]); fechados ← {}
enquanto abertos não vazia:
    nó ← desenfileirar()
    se nó.estado é objetivo: SUCESSO
    fechados ← fechados ∪ {nó.estado}
    para cada regra em aplicáveis(nó) ordenadas pela estratégia:
        filho ← expandir(nó, regra)
        se filho.estado ∉ fechados e ∉ estados em abertos:
            enfileirar(filho)
FALHA
```

Completa e **ótima** em número de movimentos. Serve de oráculo: o comprimento da solução da largura é o limite inferior contra o qual os demais são medidos.

### 6.4 Sobre a estratégia de controle

A estratégia **não altera a corretude** de backtracking e largura — altera a ordem de exploração e, portanto, as métricas e qual solução é encontrada primeiro. Já na busca irrevogável a estratégia é determinante: ela decide entre SUCESSO e IMPASSE. É exatamente esse contraste que a matriz de execução (§8) deve expor.

---

## 7. Ranqueamento

Vive em `ranking/`, isolado de `core/` (ADR-07).

### 7.1 Ordenação lexicográfica (padrão)

Comparação por critérios sucessivos, cada um desempatando o anterior:

1. **Desfecho** — `SUCCESS` > `DEADLOCK` > `CUTOFF` > `FAILURE`.
2. **Comprimento da solução** — menos movimentos é melhor.
3. **Iterações** — menos trabalho é melhor.
4. **Nós gerados** — menor consumo de memória.
5. **Nome** — desempate determinístico, para saída reprodutível.

O tempo (`elapsed_ms`) é **reportado mas não pontuado**: em espaço de 36 estados ele mede ruído de máquina, não qualidade de algoritmo.

### 7.2 Pontuação composta (alternativa)

`scorer.py` oferece um escore normalizado `0..100` com pesos configuráveis, para uma leitura de "quão bem foram" em número único. Critérios normalizados contra o melhor resultado da rodada. Selecionável por `--rank-mode=score`; o padrão é lexicográfico, por ser auditável a olho nu.

---

## 8. Execução e CLI

### 8.1 Matriz

Com problema único, a matriz é **algoritmo × estratégia**:

| | ascending | descending | custom |
|---|---|---|---|
| irrevocable | ✓ | ✓ | ✓ |
| backtracking | ✓ | ✓ | ✓ |
| breadth_first | ✓ | ✓ | ✓ |

`--all` executa o produto cartesiano completo e ranqueia as 9 execuções.

### 8.2 Comandos

```bash
python main.py --all
python main.py --algorithm backtracking
python main.py --algorithm irrevocable --strategy descending
python main.py --algorithm backtracking --show-tree --show-trace
python main.py --all --format json --output resultados.json
python main.py --list                      # algoritmos e estratégias disponíveis
python main.py --strategy custom --order R2,R4,R6,R1,R3,R5
```

| Flag | Efeito |
|---|---|
| `--algorithm` | Um algoritmo; omitido com `--all` roda todos |
| `--strategy` | Uma estratégia; omitida roda todas |
| `--all` | Produto cartesiano completo |
| `--show-tree` | Renderiza a árvore de busca |
| `--show-trace` | Passo a passo com regra aplicada e estado resultante |
| `--show-states` | Desenho ASCII das hastes no caminho solução |
| `--format` | `console` (padrão) \| `json` |
| `--rank-mode` | `lexicographic` (padrão) \| `score` |
| `--max-iterations` | Guarda contra execução patológica |
| `--seed` | Reservado; execução é determinística por construção |

### 8.3 Saída

Relatório por execução:

```
╭─ backtracking · descending ─────────────────────────────╮
│ Desfecho          SUCESSO                               │
│ Movimentos        6                                     │
│ Caminho           R6 → R4 → R1 → R2 → R3 → R4           │
│ Iterações         14                                    │
│ Nós gerados       11                                    │
│ Nós visitados     9                                     │
│ Retrocessos       3                                     │
│ Impasses          2                                     │
│ Profundidade máx  8                                     │
╰─────────────────────────────────────────────────────────╯
```

Placar consolidado:

```
#  ALGORITMO       ESTRATÉGIA   DESFECHO   MOV  ITER  GERADOS
1  breadth_first   ascending    SUCESSO      5    22       31
2  breadth_first   descending   SUCESSO      5    24       33
3  backtracking    descending   SUCESSO      6    14       11
4  backtracking    ascending    SUCESSO      8    19       15
5  irrevocable     descending   SUCESSO      9     9        9
6  irrevocable     ascending    IMPASSE      —     7        7
```

Os números acima são ilustrativos do formato, não resultados esperados.

---

## 9. Testes

### 9.1 Camadas

| Camada | Escopo | Alvo de cobertura |
|---|---|---|
| `unit/` | Módulo isolado | 100 % em `rules/` e `core/domain/` |
| `integration/` | Matriz completa e pipeline | Todas as combinações |
| `e2e/` | CLI via subprocess | Todos os comandos de §8.2 |
| `properties/` | Invariantes matemáticas | — |
| `architecture/` | Regra de dependência | — |

Meta global: **≥ 95 %**, com `--cov-fail-under=95` no CI.

### 9.2 Exaustividade — a vantagem do espaço pequeno

Com 36 estados válidos, os testes não amostram: **enumeram**.

- `test_state_space.py` — o gerador produz exatamente 36 estados; nenhum viola capacidade; nenhuma duplicata.
- Para **cada um dos 36 estados**: o conjunto de regras aplicáveis calculado por `is_applicable` bate com o cálculo independente por força bruta.
- Para **cada par (estado, regra aplicável)**: `apply` produz estado válido, preserva os 3 discos, altera exatamente 2 hastes, e o disco movido é o que estava no topo da origem.
- **Reversibilidade** — para todo `s` e regra `R` aplicável, a inversa de `R` é aplicável em `R(s)` e devolve `s`.
- **Conexidade** — BFS a partir de `INITIAL_STATE` alcança os 36 estados.

### 9.3 Contrato dos algoritmos

`test_contract.py` é parametrizado sobre `algorithms.registry × strategies.registry` — 9 combinações — e verifica, sem conhecer qual algoritmo está rodando:

- O resultado é `SearchResult` bem-formado; `outcome` é membro do enum.
- Se `SUCCESS`: o caminho começa em `INITIAL_STATE`, termina em estado objetivo, e **cada transição consecutiva é justificada por uma regra aplicável** — o caminho é replayable do zero.
- O caminho não contém estado repetido.
- `nodes_visited <= nodes_generated`.
- `iterations <= max_iterations`.
- Determinismo: duas execuções idênticas produzem resultados idênticos.
- Nenhum algoritmo muta `INITIAL_STATE` nem as regras do catálogo.

Todo algoritmo novo herda a suíte inteira ao se registrar. É esse teste que prova que a interface do requisito 3 é real.

### 9.4 Testes agnósticos ao objetivo

Nenhuma asserção depende do valor literal de `GOAL_STATE`. Onde o objetivo importa, os testes usam **propriedades relativas**:

- Backtracking e largura terminam em `SUCCESS` (garantido pela conexidade).
- O comprimento da solução da largura é `<=` ao de qualquer outro algoritmo, para toda estratégia.
- O comprimento da largura é igual à distância mínima calculada por BFS independente sobre o grafo de estados.

Consequência: **trocar a carta do problema não quebra a suíte**.

### 9.5 Testes específicos

- `test_irrevocable.py` — constrói um objetivo sintético e uma estratégia que provocadamente levam a IMPASSE, validando que o algoritmo reporta `DEADLOCK` sem exceção e sem retrocesso (`backtracks == 0`).
- `test_backtracking.py` — em cenário forçado, `backtracks > 0` e o caminho final não contém os ramos abandonados.
- `test_breadth_first.py` — ordem de expansão é estritamente por nível; nenhum nó de profundidade `d+1` é visitado antes de esgotados os de profundidade `d`.
- `test_strategies.py` — `ascending` e `descending` produzem ordens exatamente inversas; `custom_order` rejeita listas incompletas ou com regras desconhecidas.

### 9.6 Teste de arquitetura

`test_dependencies.py` percorre a AST de cada módulo e falha se:

- `rules/` importa qualquer coisa de `core/`, `runner/`, `ranking/`, `inputs/` ou `outputs/`.
- `core/` importa `runner/`, `ranking/`, `inputs/` ou `outputs/`.
- Qualquer módulo do projeto define um pacote chamado `io`.

A regra de dependência (§3.1) deixa de ser convenção e passa a ser verificada.

---

## 10. Qualidade e ferramental

```toml
# pyproject.toml (extrato)
[project]
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
console = ["rich>=13"]
dev = ["pytest>=8", "pytest-cov", "mypy>=1.11", "ruff>=0.6"]

[tool.mypy]
strict = true
warn_unreachable = true

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "PTH", "RUF"]

[tool.pytest.ini_options]
addopts = "--cov --cov-fail-under=95 --strict-markers"
```

Exigências não negociáveis:

- `mypy --strict` limpo. Sem `Any`, sem `type: ignore` sem justificativa em comentário.
- Toda função pública com docstring que declare **contrato**, não paráfrase do nome.
- Nenhum `print` fora de `outputs/`. O núcleo não sabe que existe terminal.
- Nenhuma mutação de estado após construção.
- Erros de domínio como exceções próprias, nunca `ValueError` genérico.

### 10.1 Makefile

```make
install:  ## dependências de desenvolvimento
test:     ## suíte completa com cobertura
lint:     ## ruff check + format --check
types:    ## mypy --strict
check:    ## lint + types + test
run:      ## python main.py --all
clean:    ## artefatos
```

---

## 11. Rastreabilidade dos requisitos

| # | Requisito | Onde é atendido |
|---|---|---|
| 1 | Regras em arquivos dedicados no topo | `rules/` — ADR-01 |
| 2 | Diretório com a estrutura do problema e estados | `core/domain/` |
| 3 | Interface recebendo lógica da árvore + estratégia de controle | `core/algorithms/base.py`, validada por `test_contract.py` |
| 4 | Formato Python idiomático e sênior | §10 — `mypy --strict`, ruff, tipagem total, imutabilidade |
| 5 | Uma lib para output, outra para input | `outputs/` e `inputs/` — ADR-06 |
| 6 | Testes para todos os casos, estado inicial fixo | §9 — exaustivos sobre os 36 estados |
| 7 | Rodar por algoritmo / por caso / tudo, com iterações, resultado e ranking fora de `core/` | `runner/cli.py`, `ranking/` — ADR-07 |

Requisitos do material didático:

| Origem | Exigência | Atendimento |
|---|---|---|
| Cap. 2 | Representação de estado inicial, final e regras de transição | `core/domain/`, `rules/` |
| Cap. 3 | Busca irrevogável; estratégia como parâmetro de entrada | `irrevocable.py`; ADR-02 |
| Cap. 3 | Variar o critério de ordenação e observar mudança | `--strategy` na matriz de execução |
| Cap. 4 | Backtracking com identificação de impasse e retrocesso | `backtracking.py`, métricas `deadlocks` e `backtracks` |
| Cap. 5 | Largura com abertos e fechados | `breadth_first.py`, `QueueFrontier` |

---

## 12. Fases de entrega

| Fase | Escopo | Entregável verificável |
|---|---|---|
| 1 | `rules/` + `core/domain/` | 36 estados enumerados; reversibilidade provada |
| 2 | `core/search/` + `algorithms/base.py` | Contrato definido; suíte parametrizada esqueleto |
| 3 | `irrevocable.py` + `backtracking.py` | Impasse e retrocesso observáveis |
| 4 | `inputs/` + `outputs/` + `runner/` | CLI executável ponta a ponta |
| 5 | `ranking/` | Placar consolidado |
| 6 | `breadth_first.py` | Prova de que a abstração aguenta fronteira em fila |
| 7 | Hardening | Cobertura ≥ 95 %, `make check` verde, `docs/modelagem.md` |

A fase 6 é deliberadamente posterior à 5: introduzir a busca em largura **depois** que a interface já está congelada é o que demonstra que a abstração do requisito 3 é genuína, e não moldada em torno de um algoritmo só.

---

## 13. Pontos abertos

1. **`INITIAL_STATE` e `GOAL_STATE`** (§2.7) — confirmar contra a carta do problema. Único ponto de alteração.
2. **Terceira estratégia de controle** — `custom_order` está previsto; definir se a apresentação exige uma ordem específica além de crescente e decrescente.
3. **Busca em profundidade** — o material cobre até largura. `depth_first.py` cabe na interface sem alteração, caso queira antecipar o próximo capítulo.
