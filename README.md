# Torre de Londres

Resolvedor do problema da Torre de Londres (3 hastes, 3 discos) com busca irrevogável, backtracking, busca em largura, busca ordenada, busca gulosa e busca A* sobre uma mesma abstração de árvore de busca, com estratégia de controle parametrizável, métricas instrumentadas e placar comparativo.

Python 3.12+, zero dependências de runtime.

Trabalho 1 da disciplina DCC014 (Inteligência Artificial) da Universidade Federal de Juiz de Fora, ministrada pela professora Luciana.

## Grupo 5

| Integrante | Matrícula |
|---|---|
| Charles Lelis Braga | 202035015 |
| Darlan Henrique da Costa Silva | 202176038 |
| Isaac Dizolele Kapela João | 202376017 |
| Fábio do Vale Affonso | 202076021 |
| Felipe Iglesias Cordeiro Leite | 202465031AB |
| Rafaela Oliveira de Souza | 202365133C |
| Rian Cesar Quintanilha | 202465080AC |
| Gustavo Dias de Almeida | 202165571C |
| Larissa Rezende Fazza | 202335021 |
| Ian Félix Fernandes | 202376007 |
| Michel Gomes de Andrade | 201876037 |

## Instalação

```bash
make install
```

## Uso

```bash
python main.py                      # tudo: cada eixo omitido significa "todos"
python main.py --list               # cartas, algoritmos e estratégias disponíveis
python main.py --problem P1
python main.py --algorithm backtracking --strategy descending
python main.py --algorithm backtracking --show-tree --show-trace
python main.py --algorithm astar --problem P1 --show-tree   # A*: f = g + h
python main.py --show-states
python main.py --rank-mode score
python main.py --all-goals             # os 36 estados finais; só o resumo, com média e mediana
python main.py --heuristic color_distance  # troca a heurística da gulosa e da A* (sem ela, cada uma usa a sua)
python main.py --cost unit             # troca a função de custo real (padrão: step_weight_distance)
python main.py --no-prune              # sem poda: a árvore aceita estados repetidos (na ordenada, na gulosa e na A*, menos os do próprio caminho)
python main.py --format json --output resultados.json
python main.py --svg-dir data          # árvore de cada execução em data/<carta>/<algoritmo>_<estratégia>.svg
python main.py --help
```

## Estrutura

```
src/
├── core/                      problema e motor
│   ├── rules/
│   │   ├── domain/            tipos, restrições, catálogo, erros
│   │   ├── moves.py           R1..R6
│   │   └── strategies/
│   │       ├── domain/        contrato e registro
│   │       └── canonical.py   ascending e descending
│   ├── domain/                estados, invariantes, cartas, enumeração
│   ├── costs/
│   │   ├── domain/            contrato e registro
│   │   ├── step_weight_distance.py  10 por jogada + peso × distância (padrão)
│   │   ├── weight_distance.py peso do disco × distância
│   │   └── unit.py            1 por jogada
│   ├── heuristics/
│   │   ├── domain/            contrato e registro
│   │   ├── misplacement.py    discos mal posicionados (padrão)
│   │   ├── color_distance.py  peso da cor × distância
│   │   └── misplacement_cost.py  custo dos discos mal posicionados (padrão da A*)
│   ├── search_tree/           nó, árvore, contrato da fronteira, caminho, métricas, trace
│   └── algorithms/
│       ├── domain/            contrato e registro
│       ├── irrevocable/       algorithm.py
│       ├── backtracking/      algorithm.py + frontier.py (pilha)
│       ├── breadth_first/     algorithm.py + frontier.py (fila)
│       ├── ordered/           algorithm.py + frontier.py (fila de prioridade, pelo custo real)
│       ├── greedy/            algorithm.py (a fila da ordenada, pela heurística)
│       └── astar/             algorithm.py (a fila da ordenada, por custo + heurística)
├── libs/                      bibliotecas de borda
│   ├── inputs/                linha de comando → requisição validada
│   ├── outputs/               única camada que escreve no terminal e em disco
│   └── ranking/               placar por carta e resumo consolidado
├── runner/                    orquestração; conhece todas as outras camadas
└── config/                    limites, padrões e textos da interface
```

Duas convenções sustentam a leitura da árvore:

- **Uma pasta no plural contém apenas implementações.** `algorithms/` tem uma pasta por algoritmo, com o laço (`algorithm.py`) e a fronteira que ele usa (`frontier.py`) lado a lado. O contrato e o registro de cada família vivem num `domain/` interno.
- **Não há `__init__.py`.** O que cada camada é fica documentado aqui e nos ADRs, e é verificado por teste, não por um arquivo vazio em cada pasta.

### Regra de dependência

```
core/rules/  ←  core/  ←  runner/  →  libs/
```

- `core/rules/` não importa nada do projeto fora do próprio pacote.
- `core/` não conhece `libs/` nem `runner/`.
- `core/search_tree/` não conhece `core/algorithms/`.
- Nenhum `print` existe fora de `libs/outputs/`.
- Todo `algorithm.py` de `algorithms/` e todo módulo direto de `strategies/` declara uma implementação registrada.

Tudo isso é verificado na AST por [tests/architecture/test_dependencies.py](tests/architecture/test_dependencies.py), não por convenção.

## Convenções

- Código inteiramente em inglês.
- **Sem comentários e sem docstrings de função.** O contrato de cada função é a assinatura tipada, garantida por `mypy --strict`. Só diretivas de ferramenta (`# noqa`, `# type:`) aparecem no meio do código.
- **A modelagem do problema é documentada no topo dos módulos que a carregam**, e só neles: [problem.py](src/core/domain/problem.py) (posição inicial e catálogo de cartas), [state_space.py](src/core/domain/state_space.py) (os 36 estados, conexidade, o oráculo) [step_weight_distance.py](src/core/costs/step_weight_distance.py), [weight_distance.py](src/core/costs/weight_distance.py) e [unit.py](src/core/costs/unit.py) (as funções de custo real), [misplacement.py](src/core/heuristics/misplacement.py), [color_distance.py](src/core/heuristics/color_distance.py) e [misplacement_cost.py](src/core/heuristics/misplacement_cost.py) (as heurísticas) e os seis algoritmos, cada um com a carta P1 e o critério de busca.
- Estado imutável em todo lugar: `tuple`, frozen dataclass, enum.
- Texto apresentado ao usuário só em `libs/outputs/theme.py` e `config/settings.py`.

## Algoritmos

Os seis compartilham o motor: `visita` conta e registra o vértice, `gera` cria um filho pela regra, `poda` descarta a regra cujo sucessor repetiria um estado. Estourar o limite de iterações encerra qualquer um deles com LIMITE. O que muda é a fronteira e a decisão em cada vértice.

### Busca irrevogável

Um caminho só. A regra preferida da estratégia é aplicada e as outras são esquecidas.

```mermaid
flowchart TD
    A([raiz]) --> B{é o objetivo?}
    B -- sim --> S([SUCESSO])
    B -- não --> C[visita: regras aplicáveis na ordem da estratégia, menos as que repetem estado do caminho]
    C --> D{sobrou regra?}
    D -- não --> X([IMPASSE])
    D -- sim --> E[aplica só a primeira e gera o filho]
    E --> B
```

Sempre para, no máximo depois dos 36 estados, porque nunca repete estado no caminho. É o único método em que a estratégia muda o desfecho: em P1, `descending` trava na 3ª iteração e `ascending` chega em 14 movimentos.

### Backtracking

A mesma descida, com as alternativas de cada vértice guardadas numa pilha. Travou, volta ao ancestral mais próximo que ainda tem alternativa.

```mermaid
flowchart TD
    A([raiz na pilha]) --> B{topo da pilha é o objetivo?}
    B -- sim --> S([SUCESSO])
    B -- não --> C{primeira vez nele?}
    C -- sim --> V[visita e guarda a lista de regras aplicáveis, na ordem da estratégia, sem as que repetem estado do caminho]
    V --> W{lista vazia?}
    W -- sim --> I[impasse]
    W -- não --> D
    I --> D
    C -- não --> D{ainda tem regra guardada?}
    D -- não --> R[retrocesso: sai da pilha, o pai volta ao topo]
    R --> B
    D -- sim --> E[tira a próxima, gera o filho e o empilha]
    E --> B
```

Impasse vira desvio e a solução sempre aparece, mas é a primeira encontrada, não a mais curta. Em P1 com `descending`: 51 iterações, 14 retrocessos, 22 movimentos para um ótimo de 3.

### Busca em largura

Não escolhe regra: aplica todas, os filhos esperam numa fila e a árvore é varrida por níveis.

```mermaid
flowchart TD
    A([raiz na fila]) --> B[tira o primeiro da fila]
    B --> C{é o objetivo?}
    C -- sim --> S([SUCESSO])
    C -- não --> V[visita: regras aplicáveis na ordem da estratégia, menos as que levam a um estado já gerado por qualquer ramo]
    V --> E[aplica todas e coloca os filhos no fim da fila]
    E --> B
```

Nada de profundidade d+1 antes de esgotar d, então o primeiro caminho até um estado é o mais curto. O objetivo encontrado é o ótimo em número de movimentos, e por isso este método é a referência dos outros em comprimento. Menos movimentos não é menor custo real: essa referência é a busca ordenada. A poda aqui é global: um estado descoberto por qualquer ramo nunca é gerado de novo. Em P1: R4, R1, R1, 3 movimentos em 12 iterações.

### Custo real

Cada jogada tem um custo real, e o custo de um nó é a soma dos custos das jogadas da raiz até ele. A função de custo é um módulo de [core/costs/](src/core/costs/), registrado pelo nome e escolhido com `--cost`. São três:

| função | custo de uma jogada |
|---|---|
| `step_weight_distance` (padrão) | 10 + peso do disco movido (verde 1, vermelho 2, azul 3) × distância em hastes (1 entre vizinhas, 2 entre H1 e H3) |
| `weight_distance` | peso do disco movido × distância em hastes, sem os 10 |
| `unit` | 1 |

O custo real ordena a busca ordenada, entra no f = g + h da A* e dá o custo da solução de todas as buscas. Em P1, o caminho R4, R1, R1 custa 13 + 12 + 11 = 36 com `step_weight_distance`, 6 com `weight_distance` e 3 com `unit`.

Os 10 por jogada pesam mais que o peso × distância, que vai de 1 a 6: um caminho com um movimento a mais nunca sai mais barato. Com a função padrão, o caminho de menor custo é sempre um dos de menos movimentos, e o peso × distância só desempata entre eles.

### Busca ordenada

ABERTOS vira uma fila ordenada pelo menor custo real acumulado.

```mermaid
flowchart TD
    A([raiz em ABERTOS]) --> B[tira o de menor custo; no empate, o gerado primeiro]
    B --> C{é o objetivo?}
    C -- sim --> S([SUCESSO])
    C -- não --> V[visita: regras aplicáveis na ordem da estratégia, menos as que voltam a um estado do próprio caminho e as que não barateiam o custo do vetor de menor custo]
    V --> E[aplica todas; se um filho chega por um caminho mais barato a um estado ainda aberto, o nó antigo sai de ABERTOS e da árvore]
    E --> B
```

O objetivo só encerra a busca quando vira o estado atual, não quando é gerado: por isso a solução é a de menor custo real. A estratégia só desempata irmãos de mesmo custo. Um nó nunca gera um estado do seu próprio caminho; a técnica de poda, com o vetor de menor custo, descarta o nó repetido que não chega mais barato e troca o nó antigo pelo novo quando chega (sem ela, `--no-prune`, os repetidos entram de novo em ABERTOS: 16 iterações em P1 em vez de 11). Com a função padrão e com `unit` ela acha sempre o mínimo de movimentos. Sem os 10 por jogada (`weight_distance`), o caminho mais barato nem sempre é o mais curto: em um dos 36 objetivos a ordenada faz um movimento a mais que a largura para gastar menos (custo 7 em 4 movimentos, contra custo 9 em 3). Em P1: R4, R1, R1, custo 36, em 11 iterações.

| 36 objetivos, com poda, `ascending` | `step_weight_distance` | `weight_distance` | `unit` |
|---|---|---|---|
| ordenada: custo (média) | 51,33 | 9,89 | 4,14 |
| A*: custo (média) | 51,33 | 10,17 | 4,19 |
| ordenada: movimentos (média) | 4,14 | 4,17 | 4,14 |
| largura: custo (média) | 51,72 | 10,33 | 4,14 |
| gulosa: custo (média) | 52,33 | 10,39 | 4,19 |

### Heurística

A busca gulosa e a A* recebem a heurística por parâmetro: cada uma é um módulo de [core/heuristics/](src/core/heuristics/), registrado pelo nome e escolhido com `--heuristic`. Sem `--heuristic`, cada busca usa a sua: a gulosa, a de discos mal posicionados ([misplacement.py](src/core/heuristics/misplacement.py)); a A*, a do custo dos discos mal posicionados ([misplacement_cost.py](src/core/heuristics/misplacement_cost.py)). Cada disco contribui com o mínimo de movimentos que ainda precisa fazer:

| disco | contribui |
|---|---|
| bem posicionado: haste e altura certas, e tudo abaixo dele também | 0 |
| em outra haste | 1 |
| na haste certa, mas mal posicionado | 2 |

**h(estado)** é a soma dos três discos. Estar na haste certa fora do lugar pesa mais que estar na haste errada, porque o disco precisa sair e voltar. A heurística é admissível em número de movimentos: cada movimento leva um disco só, então h nunca passa do número de movimentos que falta. Os testes verificam isso nos 1.296 pares de estados.

A segunda heurística é a de cor e distância ([color_distance.py](src/core/heuristics/color_distance.py)), escolhida com `--heuristic color_distance`. Cada disco fora da haste do objetivo contribui com o peso da sua cor (verde 1, vermelho 2, azul 3) vezes a distância em hastes até a haste em que deve ficar (1 entre vizinhas, 2 entre H1 e H3). Ela só olha a haste, não a altura: um disco na haste certa contribui com 0 mesmo fora do lugar, então h pode ser 0 fora do objetivo.

| gulosa, 36 objetivos, com poda, `ascending` | discos mal posicionados | cor e distância |
|---|---|---|
| objetivos resolvidos | 36 | 36 |
| iterações (média) | 7,44 | 10,39 |
| movimentos (média) | 4,19 | 5,17 |
| custo real (média) | 52,33 | 64,28 |

Em P1 as duas levam ao mesmo caminho, R4, R1, R1.

A terceira é a do custo dos discos mal posicionados ([misplacement_cost.py](src/core/heuristics/misplacement_cost.py)), a padrão da A*. É a mesma contagem de movimentos, convertida em custo real: cada movimento que falta a um disco custa no mínimo a jogada mais barata dele, uma haste só, 10 + peso (verde 11, vermelho 12, azul 13). Em S0 de P1 vale 11 + 12 + 13 = 36, exatamente o custo da solução ótima. Com a função de custo padrão ela é admissível e consistente: os testes conferem as duas coisas nos 1.296 pares de estados contra um Dijkstra escrito à parte.

### Busca gulosa

O laço e as duas listas da busca ordenada, mas ABERTOS é ordenada pela menor heurística, não pelo custo real. O custo real não entra na escolha: ele é somado nas arestas do caminho solução e dá o custo da solução.

```mermaid
flowchart TD
    A([raiz em ABERTOS]) --> B[tira o de menor heurística; no empate, o gerado primeiro]
    B --> C{é o objetivo?}
    C -- sim --> S([SUCESSO])
    C -- não --> V[visita: regras aplicáveis na ordem da estratégia, menos as que levam a um estado fechado ou a um estado aberto sem baratear o caminho]
    V --> E[aplica todas e põe os filhos em ABERTOS na posição da sua heurística]
    E --> B
```

A estratégia só desempata irmãos de mesma heurística. A poda é a da ordenada, mais o filho de estado já fechado, que aqui pode reaparecer mais barato e não é reaberto. A gulosa sempre encontra uma solução: resolve os 36 objetivos, com 7,44 iterações em média, contra 18,5 da ordenada e da largura. Não garante a melhor: acha o menor custo real em 31 dos 36 objetivos com `ascending` e em 28 com `descending`. Em P1: R4, R1, R1, custo 36, em 4 iterações e 9 nós gerados.

### Busca A*

O laço e as duas listas da busca ordenada, com ABERTOS ordenada pela menor função de avaliação **f(n) = g(n) + h(n)**: g é o custo real da raiz até o nó, o que ordena a ordenada; h é a heurística, o custo estimado do nó até o objetivo, o que ordena a gulosa. f estima o custo da solução mais barata que passa pelo nó.

```mermaid
flowchart TD
    A([raiz em ABERTOS]) --> B[tira o de menor f = g + h; no empate, o gerado primeiro]
    B --> C{é o objetivo?}
    C -- sim --> S([SUCESSO])
    C -- não --> V[visita: regras aplicáveis na ordem da estratégia, menos as que voltam a um estado do próprio caminho e as que não barateiam o custo do vetor de menor custo]
    V --> E[aplica todas e põe os filhos em ABERTOS na posição da sua f]
    E --> B
```

Como f soma h com g, h precisa estar na unidade do custo: por isso a padrão da A* é a do custo dos discos mal posicionados, não a contagem de movimentos da gulosa. Com h admissível, o primeiro objetivo a sair de ABERTOS é o de menor custo real; com h consistente, um estado já expandido nunca reaparece mais barato, e a poda da ordenada basta. A estratégia só desempata irmãos de mesma f.

Em P1: R4, R1, R1, custo 36, em 4 iterações e 9 nós gerados, os mesmos números da gulosa. f vale 36 em todo o caminho e todo nó fora dele tem f maior. Nos 36 objetivos a A* acha sempre o menor custo real, como a ordenada (média 51,33), com 8,78 iterações em média, contra 18,5 da ordenada e 7,44 da gulosa. No objetivo G07, em que a gulosa faz 8 movimentos e paga 99, a A* acha o caminho de 7 movimentos e custo 87 com as mesmas 18 iterações; a ordenada precisa de 34.

| A*, 36 objetivos, com poda, `ascending` | custo dos mal posicionados | discos mal posicionados | cor e distância |
|---|---|---|---|
| iterações em P1 | 4 | 10 | 10 |
| iterações (média) | 8,78 | 17,06 | 16,89 |
| nós gerados (média) | 14,53 | 21,97 | 21,28 |
| custo real (média) | 51,33 | 51,33 | 51,33 |

As três são admissíveis com o custo padrão, e a A* acha sempre o menor custo com qualquer uma; o que muda é o esforço. Em movimentos, de 0 a 6, a heurística quase não pesa perto de g, de 11 a 16 por jogada, e a A* fica perto da ordenada. Com `--cost weight_distance` ou `--cost unit` a heurística padrão superestima o que falta (as jogadas custam menos que 10 + peso) e a A* perde a garantia: custo médio 10,17 e 4,19, contra 9,89 e 4,14 da ordenada. Com `--heuristic misplacement`, admissível nas três funções de custo, ela volta ao ótimo.

## Comparação em todos os objetivos

Uma carta só não diz qual método é melhor. `--all-goals` resolve cada um dos 36 estados do espaço como objetivo, sempre a partir da mesma posição inicial (cartas G01 a G36), com todo algoritmo e toda estratégia. A saída é só o resumo consolidado:

- **Resumo**: para movimentos, custo, iterações e nós gerados, a média e a mediana de cada combinação. Movimentos e custo contam só os sucessos.
- **Melhor por critério**: o menor valor pela média e pela mediana. Só concorre quem tem o maior número de sucessos, para a irrevogável não vencer resolvendo apenas os objetivos fáceis.

O resultado: a largura, a ordenada e a A* vencem em movimentos (média 4,14; a gulosa fica em 4,19 e 4,25). A ordenada e a A* vencem em custo real (média 51,33, contra 51,7 da largura e 52,3 a 53,0 da gulosa). A gulosa vence em iterações e em nós gerados: 7,44 iterações em média, contra 8,78 da A* e 18,5 da largura e da ordenada. A A* fica com o custo da ordenada e menos da metade das iterações. [tests/properties/test_all_goals.py](tests/properties/test_all_goals.py) verifica tudo isso.

## Qualidade

```bash
make check     # ruff + mypy --strict + pytest com cobertura mínima de 95%
make test
make lint
make types
make run
make clean
```

## Árvores de busca em SVG

`make graphs` grava em `data/` um `.dot` e um `.svg` por execução, com o caminho solução em azul, o objetivo em verde, os impasses em vermelho e as regras podadas em pontilhado. O `.dot` é gerado pelo projeto; o `.svg` vem do Graphviz (`dot`), que precisa estar instalado. Sem ele, só o `.dot` é gravado e um aviso aparece.

```bash
sudo apt install graphviz     # ou: brew install graphviz
make graphs
```

## Notebooks para o Colab

`apps/notebook/` gera a apresentação num notebook. Cada seção de algoritmo segue a ordem dos slides (problema, ideia, laço e listas, regras, estratégia, árvore sem e com poda, pseudocódigo com o código do projeto, caminho solução, comparativos e complexidade). O que é código e não está nos slides, como o Setup, vem marcado com (ignore). O notebook é gerado a partir de `src/` e roda sozinho no Colab, sem clonar o repositório. Veja [apps/notebook/README.md](apps/notebook/README.md).

Destaques:

- **Tabela contra os outros algoritmos** com o vencedor de cada critério (nível da solução, iterações, nós gerados e expandidos, pico de ABERTOS, retrocessos, impasses) em verde.
- **O custo real na busca ordenada**: a regra de 10 por jogada mais peso × distância, o código das três funções de custo e o custo de cada jogada na raiz.
- **A heurística na busca gulosa**: a regra dos discos mal posicionados, o código de `misplacement.py`, a conta de h em S0 disco a disco e a h de cada filho da raiz.
- **f = g + h na busca A\***: a heurística na unidade do custo, o código de `misplacement_cost.py`, g, h e f de cada filho da raiz e de cada nível do caminho, e o caso G07, em que a A* acha o custo 87 com as iterações da gulosa.
- **Comparativo nos 36 objetivos** na seção da ordenada: boxplot e quartis de nós expandidos, iterações e nós gerados, para todas as combinações de algoritmo e estratégia.
- **Tabelas de complexidade** com o algoritmo na primeira coluna, no mesmo formato da tabela consolidada da comparação.

```bash
make notebooks
```

## Documentação

- [SPEC.md](SPEC.md): especificação técnica completa.
- [src/core/domain/state_space.py](src/core/domain/state_space.py): contagem dos 36 estados, propriedades do grafo e o papel de oráculo.
- [src/core/algorithms/](src/core/algorithms/): cada algoritmo traz a execução de P1 resolvida passo a passo, com árvore de busca e caminho solução, tudo tirado do `--show-trace`. Os fluxogramas em Mermaid estão na seção Algoritmos acima.

`docs/` existe no disco mas está fora do versionamento.
