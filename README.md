# Torre de Londres

Resolvedor do problema da Torre de Londres (3 hastes, 3 discos) com busca irrevogável, backtracking, busca em largura e busca ordenada sobre uma mesma abstração de árvore de busca, com estratégia de controle parametrizável, métricas instrumentadas e placar comparativo.

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
python main.py --show-states
python main.py --rank-mode score
python main.py --all-goals             # os 36 estados finais; só o resumo, com média e mediana
python main.py --no-prune              # sem poda: a árvore aceita estados repetidos
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
│   │       ├── ascending.py
│   │       └── descending.py
│   ├── domain/                estados, invariantes, cartas, enumeração
│   ├── search_tree/           nó, árvore, contrato da fronteira, caminho, métricas, trace
│   └── algorithms/
│       ├── domain/            contrato e registro
│       ├── irrevocable/       algorithm.py
│       ├── backtracking/      algorithm.py + frontier.py (pilha)
│       ├── breadth_first/     algorithm.py + frontier.py (fila)
│       └── ordered/           algorithm.py + frontier.py (fila por custo)
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
- **A modelagem do problema é documentada no topo dos módulos que a carregam**, e só neles: [problem.py](src/core/domain/problem.py) (posição inicial e catálogo de cartas), [state_space.py](src/core/domain/state_space.py) (os 36 estados, conexidade, o oráculo) e os quatro algoritmos, cada um com a execução de P1 resolvida passo a passo, listas ABERTOS e FECHADOS, árvore de busca e caminho solução.
- Estado imutável em todo lugar: `tuple`, frozen dataclass, enum.
- Texto apresentado ao usuário só em `libs/outputs/theme.py` e `config/settings.py`.

## Algoritmos

Os quatro compartilham o motor: `visita` conta e registra o vértice, `gera` cria um filho pela regra, `poda` descarta a regra cujo sucessor repetiria um estado. Estourar o limite de iterações encerra qualquer um deles com LIMITE. O que muda é a fronteira e a decisão em cada vértice.

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

Nada de profundidade d+1 antes de esgotar d, então o primeiro caminho até um estado é o mais curto. O objetivo encontrado é o ótimo em número de movimentos, e por isso este método é a referência dos outros em comprimento; em custo, a referência é a busca ordenada. A poda aqui é global: um estado descoberto por qualquer ramo nunca é gerado de novo. Em P1: R4, R1, R1, 3 movimentos em 12 iterações.

### Busca ordenada

Aplicar uma regra custa **10 + peso do disco × distância**: 10 por jogada; distância 1 entre hastes vizinhas e 2 de H1 para H3; peso 1 para o verde, 2 para o vermelho e 3 para o azul. ABERTOS vira uma fila ordenada pelo custo acumulado desde a raiz.

- **10 por jogada** pesa mais que o esforço, que vai de 1 a 6 por jogada: em todos os 1.260 pares início → objetivo, o caminho mais barato é um dos mais curtos, e a ordenada não troca movimentos por esforço. Sem o 10, isso falha em 3,7% das execuções.
- **Peso × distância** escolhe, entre os caminhos mais curtos, o que carrega os discos mais pesados por menos distância. Como depende de qual disco se move, separa caminhos que a largura trata como iguais.

A escolha veio de um estudo com 13 modelos de custo em todos os 1.260 pares início → objetivo. Com distância pura, a ordenada só achava algo mais barato que a largura em 0,5% dos casos e a resposta mudava com a estratégia em 15%. Com este modelo, acha em 10,3%, o ótimo é único em 85% dos pares e a resposta só muda com a estratégia em 4,6%, sempre com o mínimo de movimentos.

```mermaid
flowchart TD
    A([raiz em ABERTOS]) --> B[tira o de menor custo; no empate, o gerado primeiro]
    B --> C{é o objetivo?}
    C -- sim --> S([SUCESSO])
    C -- não --> V[visita: regras aplicáveis na ordem da estratégia, menos as que não baixam o menor custo conhecido do estado]
    V --> E[aplica todas; se um filho chega mais barato a um estado ainda aberto, o nó antigo sai de ABERTOS e da árvore]
    E --> B
```

O objetivo só encerra a busca quando vira o estado atual, não quando é gerado, e por isso a solução é a de menor custo. A estratégia só desempata irmãos de mesmo custo. A poda segue o vetor de menor custo do material: um estado gerado de novo com custo maior ou igual é descartado, e um estado ainda aberto que reaparece mais barato troca de nó. Em P1: R4, R1, R1, custo 13 + 12 + 11 = 36 em 11 iterações, com uma troca na iteração 9.

## Comparação em todos os objetivos

Uma carta só não diz qual método é melhor. `--all-goals` resolve cada um dos 36 estados do espaço como objetivo, sempre a partir da mesma posição inicial (cartas G01 a G36), com todo algoritmo e toda estratégia. A saída é só o resumo consolidado:

- **Resumo**: para movimentos, custo, iterações e nós gerados, a média e a mediana de cada combinação. Movimentos e custo contam só os sucessos.
- **Melhor por critério**: o menor valor pela média e pela mediana. Só concorre quem tem o maior número de sucessos, para a irrevogável não vencer resolvendo apenas os objetivos fáceis.

O resultado: largura e ordenada empatam em movimentos, e a ordenada tem o menor custo médio nas duas estratégias (51,33, contra 51,72 e 51,67 da largura); a largura passa do menor custo em 9 das 72 execuções. A média de iterações das duas é sempre 18,5, porque cada uma visita cada estado uma única vez, e por isso o objetivo i é encontrado na i-ésima posição de uma permutação de 1 a 36. O critério que as separa é o número de nós gerados. [tests/properties/test_all_goals.py](tests/properties/test_all_goals.py) verifica tudo isso.

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

- **Tabela contra os outros algoritmos** com o vencedor de cada critério (custo, nível da solução, iterações, nós gerados e expandidos, pico de ABERTOS, retrocessos) em verde.
- **Lógica dos custos na busca ordenada**, uma parte por vez: o 10 por jogada; a distância, com o exemplo G17 (dois caminhos de 4 movimentos que empatam em 46 só com o peso e se separam em 48 e 50 com a distância); o peso, com o exemplo G11 (41 na largura contra 39 na ordenada). Cada jogada aparece desenhada com o cálculo do seu custo.
- **Ganho real do modelo de custo**: nos 1.260 pares, a ordenada sai em média 0,4% mais barata que a largura. O estudo compara os modelos também pela maior economia, nós gerados em relação à largura, trocas de nó por execução e movimentos a mais.
- **Comparativo nos 36 objetivos** na seção da ordenada: boxplot e quartis de nós expandidos, iterações, nós gerados e custo da solução, para todas as combinações de algoritmo e estratégia, além do custo da solução só em P1.
- **Tabelas de complexidade** com o algoritmo na primeira coluna, no mesmo formato da tabela consolidada da comparação.

```bash
make notebooks
```

## Documentação

- [SPEC.md](SPEC.md): especificação técnica completa.
- [src/core/domain/state_space.py](src/core/domain/state_space.py): contagem dos 36 estados, propriedades do grafo e o papel de oráculo.
- [src/core/algorithms/](src/core/algorithms/): cada algoritmo traz a execução de P1 resolvida passo a passo, com árvore de busca e caminho solução, tudo tirado do `--show-trace`. Os fluxogramas em Mermaid estão na seção Algoritmos acima.

`docs/` existe no disco mas está fora do versionamento.
