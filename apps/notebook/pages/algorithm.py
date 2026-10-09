from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

from cells import Cell, code, markdown
from source import SOURCE_DIR, find, writefile_cell

PROBLEM_MODULES = ("core/rules/domain/base.py", "core/domain/problem.py")
FRONTIER_MODULES = ("core/search_tree/frontier.py",)
ENGINE_MODULES = ("core/algorithms/domain/base.py",)
RULE_MODULES = (
    "core/rules/domain/constraints.py",
    "core/rules/moves.py",
    "core/rules/domain/catalog.py",
)
STRATEGY_MODULES = ("core/rules/strategies/canonical.py",)
HEURISTIC_MODULES = ("core/domain/heuristic.py",)
SLIDE_STRATEGIES = (("ascending", "crescente"), ("descending", "decrescente"))
COMPLEXITY_HEADER = ("Algoritmo", "Tempo", "Memória", "Solução", "Por quê")

ComplexityRow = tuple[str, str, str, str, str]


@dataclass(frozen=True, slots=True)
class AlgorithmSection:
    """Uma seção do notebook e os dados do algoritmo que as funções de
    apresentação usam: rótulo, cor, como desenhar as listas e a fronteira."""

    title: str
    name: str
    label: str
    color: str
    list_mode: str
    complete: bool
    module: str
    subtitle: str
    idea: str
    loop: str
    strategy_note: str
    root_note: str
    no_prune: str
    prune: str
    pseudocode: str
    path_strategy: str
    path_note: str
    complexity: tuple[ComplexityRow, ...]
    symbols: tuple[str, ...]
    conclusion: str
    flowchart: str
    no_prune_limit: int | None = None
    frontier: str | None = None
    frontier_class: str | None = None
    uses_heuristic: bool = False
    shows_frontier: bool = False
    frontier_demo: bool = False
    compared_with: tuple[str, ...] = ()
    rule_cells: tuple[Cell, ...] = ()
    goals_cells: tuple[Cell, ...] = ()


# Os fluxogramas usam a fonte e as cores de `theme`, preenchidas no notebook.
FLOW_STYLE = """  rankdir=TB; fontname="%(font)s"; bgcolor="transparent";
  node [fontname="%(font)s", fontsize=11, shape=box, style="rounded,filled", fillcolor="%(fill)s", color="%(line)s"];
  edge [fontname="%(font)s", fontsize=10, color="%(line)s"];"""

RULES_LIST = "\n".join(
    f"    R{index}: mover o disco do topo da {origin} para a {destination}."
    for index, (origin, destination) in enumerate(
        permutations(("H1", "H2", "H3"), 2), start=1
    )
)

PRUNE_FLAG = "**poda** vem de `--no-prune`: desligada, a linha da poda não roda. A **estratégia** só muda a ordem do *para cada*."

IRREVOCABLE_SECTION = AlgorithmSection(
    title="Busca irrevogável",
    name="irrevocable",
    label="Irrevogável",
    color="#2a78d6",
    list_mode="single",
    complete=False,
    module="core/algorithms/irrevocable/algorithm.py",
    subtitle="Um caminho só: a regra preferida da estratégia é aplicada e as outras são esquecidas.",
    idea="""**Aplique a primeira regra válida e siga em frente, sem guardar alternativas.**

Não há fila nem pilha: ABERTOS tem no máximo um nó, o filho que acabou de ser gerado, e ele vira o próximo estado atual. Cada passo é definitivo. Um beco sem saída encerra a busca em IMPASSE.""",
    loop="""1. O estado atual é o objetivo? **SUCESSO**.
2. Não é: coloca o nó em FECHADOS.
3. Ordena as regras válidas pela estratégia e descarta as que voltam a um estado do caminho (poda).
4. Não sobrou regra: **IMPASSE**.
5. Aplica só a primeira: o filho vira o estado atual. Volta ao passo 1.

**ABERTOS**: o único filho gerado, que vira o próximo estado atual.

**FECHADOS**: o caminho percorrido. Com poda, serve para não voltar a um estado do caminho.""",
    strategy_note="Na irrevogável a estratégia decide tudo: só a primeira regra da ordem é aplicada, então trocar a ordem troca o caminho inteiro e até o desfecho.",
    root_note="As regras válidas são as mesmas nas duas ordens, mas a irrevogável gera só o filho da primeira. Em P1 a solução começa por R4: `descending` escolhe R4 já na raiz; `ascending` escolhe R1.",
    no_prune="""Sem poda, nada impede a irrevogável de aplicar uma regra e logo depois a inversa: a busca gira entre os mesmos dois estados até o limite de iterações e termina em LIMITE. Para caber no notebook, as execuções sem poda abaixo param em 30 iterações.""",
    prune="""A poda descarta a regra que leva a um estado que já está no caminho. Com ela a irrevogável nunca repete estado e sempre para, no máximo depois dos 36 estados. Parar não é chegar: ela ainda pode terminar em IMPASSE.""",
    pseudocode="""busca_irrevogavel(problema, estratégia, poda)
    nó = raiz
    enquanto verdadeiro:
        se nó é o objetivo: SUCESSO
        coloca nó em FECHADOS
        regras = regras válidas em nó, na ordem da estratégia
        se poda: descarta as que levam a um estado de FECHADOS
        se não sobrou regra: IMPASSE
        nó = aplica a primeira regra em nó""",
    path_strategy="ascending",
    path_note="Com `descending` a busca termina em impasse na 3ª iteração e não há caminho. O caminho abaixo é o da ordem crescente: chega, mas com 14 movimentos, quando o ótimo tem 3.",
    complexity=(
        (
            "Irrevogável sem poda",
            "não termina",
            "O(1)",
            "pode não achar",
            "pode girar num ciclo para sempre",
        ),
        (
            "Irrevogável com poda",
            "O(b·m²)",
            "O(m)",
            "pode não achar",
            "um nó por iteração, no máximo m; cada regra é comparada com o caminho",
        ),
    ),
    symbols=("b", "m", "V"),
    conclusion="""## Conclusão

- Em P1, `descending` trava na 3ª iteração: R4 e R5 levam a `H1[V,R,A]`, e de lá as duas regras aplicáveis voltam a estados do caminho. `ascending` chega, mas com 14 movimentos, quando o ótimo tem 3.
- Nos 36 objetivos, resolve 18 com `ascending` e 3 com `descending`. Com a gulosa, é um dos dois algoritmos que deixam objetivos sem solução.
- É barata (um nó gerado por iteração), mas não garante solução nem qualidade: a estratégia decide tudo.""",
    flowchart="""digraph flow {
%(style)s
  root [label="raiz", shape=oval, fillcolor="%(root)s"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="%(goal)s"];
  visit [label="visita: regras aplicáveis na ordem da estratégia,\\nmenos as que repetem estado do caminho"];
  left [label="sobrou regra?", shape=diamond];
  deadlock [label="IMPASSE", shape=oval, fillcolor="%(deadlock)s"];
  apply [label="aplica só a primeira e gera o filho"];
  root -> goal;
  goal -> success [label="sim"];
  goal -> visit [label="não"];
  visit -> left;
  left -> deadlock [label="não"];
  left -> apply [label="sim"];
  apply -> goal;
}""",
    no_prune_limit=30,
)

BACKTRACKING_SECTION = AlgorithmSection(
    title="Backtracking",
    name="backtracking",
    label="Backtracking",
    color="#eb6834",
    list_mode="stack",
    complete=True,
    module="core/algorithms/backtracking/algorithm.py",
    frontier="core/algorithms/backtracking/frontier.py",
    frontier_class="StackFrontier",
    subtitle="A mesma descida da busca irrevogável, com as alternativas de cada nó guardadas numa pilha.",
    idea="""**Desça enquanto houver regra; sem regra, volte ao ancestral mais próximo que ainda tem alternativa.**

Backtracking: pilha, sai o último que entrou. Afunda num ramo.

O contrato da fronteira fica em `core/search_tree/frontier.py`. Cada algoritmo traz a sua implementação ao lado, na própria pasta: a pilha do backtracking, a fila da largura e a fila pela heurística da ordenada.""",
    loop="""1. Olha o topo da pilha. É o objetivo? **SUCESSO**.
2. Primeira vez nele: guarda as regras válidas, na ordem da estratégia, sem as que voltam a um estado do caminho (poda). Lista vazia é impasse.
3. Ainda tem regra guardada: aplica a próxima e empilha o filho.
4. Não tem: desempilha o nó (retrocesso) e o pai volta ao topo. Volta ao passo 1.

**PILHA**: o caminho atual, da raiz ao topo. Faz o papel de ABERTOS.

**RETROCEDIDOS**: os nós que saíram da pilha sem levar ao objetivo. Fazem o papel de FECHADOS.""",
    strategy_note="No backtracking a estratégia decide qual ramo é descido primeiro. A solução é a primeira encontrada, então trocar a ordem troca o caminho e o número de retrocessos.",
    root_note="A raiz guarda as mesmas regras nas duas ordens; muda só qual filho é empilhado primeiro. Em P1 a solução começa por R4, que `descending` tenta primeiro.",
    no_prune="""Sem poda, a descida aceita voltar a estados do caminho: a busca entra num ciclo entre uma regra e a inversa, nunca chega a um beco sem saída e por isso nunca retrocede. Gira até o limite de iterações e termina em LIMITE. Para caber no notebook, as execuções sem poda abaixo param em 30 iterações.""",
    prune="""A poda descarta a regra que leva a um estado que já está no caminho atual. É uma poda local: o mesmo estado pode aparecer em ramos diferentes. Com ela não há ciclo e, como todo estado alcança todo estado, a solução sempre aparece.""",
    pseudocode="""backtracking(problema, estratégia, poda)
    PILHA = [raiz]
    enquanto PILHA não estiver vazia:
        nó = topo da PILHA
        se nó é o objetivo: SUCESSO
        se é a primeira vez em nó:
            guarda as regras válidas, na ordem da estratégia
            se poda: descarta as que levam a um estado do caminho
        se nó ainda tem regra guardada:
            tira a próxima, aplica e empilha o filho
        senão:
            desempilha nó (retrocesso)
    FRACASSO""",
    path_strategy="descending",
    path_note="A ordem decrescente, a do docstring do módulo: 22 movimentos para um ótimo de 3, depois de 14 retrocessos.",
    complexity=(
        (
            "Backtracking sem poda",
            "não termina",
            "O(L)",
            "pode não achar",
            "o ciclo cresce a pilha até o limite L de iterações",
        ),
        (
            "Backtracking com poda",
            "O(bᵐ)",
            "O(m)",
            "a primeira achada",
            "só guarda o caminho atual",
        ),
    ),
    symbols=("b", "m"),
    conclusion="""## Conclusão

- Em P1 as duas estratégias chegam ao objetivo. Com `descending` são 51 iterações, 14 retrocessos e 22 movimentos para um ótimo de 3; com `ascending` não há retrocesso e o caminho é o mesmo da irrevogável, com 14 movimentos.
- Nos 36 objetivos resolve todos, mas com média de 12,81 a 16,5 movimentos, contra 4,14 do ótimo. Com `descending`, a média de iterações é 82,92 e a mediana 21,5: um objetivo passa de 2 mil iterações.
- Resolve o problema da irrevogável (o impasse vira desvio), mas para no primeiro objetivo que encontra, tenha o caminho o comprimento que tiver.""",
    flowchart="""digraph flow {
%(style)s
  root [label="raiz na pilha", shape=oval, fillcolor="%(root)s"];
  goal [label="topo da pilha\\né o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="%(goal)s"];
  first [label="primeira vez nele?", shape=diamond];
  visit [label="visita e guarda a lista de regras aplicáveis,\\nna ordem da estratégia, sem as que repetem estado do caminho"];
  empty [label="lista vazia?", shape=diamond];
  deadlock [label="impasse", fillcolor="%(deadlock)s"];
  left [label="ainda tem\\nregra guardada?", shape=diamond];
  back [label="retrocesso: sai da pilha,\\no pai volta ao topo"];
  apply [label="tira a próxima, gera o filho e o empilha"];
  root -> goal;
  goal -> success [label="sim"];
  goal -> first [label="não"];
  first -> visit [label="sim"];
  first -> left [label="não"];
  visit -> empty;
  empty -> deadlock [label="sim"];
  empty -> left [label="não"];
  deadlock -> left;
  left -> back [label="não"];
  left -> apply [label="sim"];
  back -> goal;
  apply -> goal;
}""",
    no_prune_limit=30,
    shows_frontier=True,
    frontier_demo=True,
)

BREADTH_FIRST_SECTION = AlgorithmSection(
    title="Busca em largura",
    name="breadth_first",
    label="Largura",
    color="#1baf7a",
    list_mode="queue",
    complete=True,
    module="core/algorithms/breadth_first/algorithm.py",
    frontier="core/algorithms/breadth_first/frontier.py",
    frontier_class="QueueFrontier",
    subtitle="Torre de Londres: três hastes, três discos. A árvore é varrida nível por nível.",
    idea="""**Analise todos os nós de um nível antes de descer para o próximo.**

Backtracking: pilha, sai o último que entrou. Afunda num ramo.

Largura: fila, sai o primeiro que entrou. Varre por níveis.""",
    loop="""1. Tira o primeiro nó de ABERTOS.
2. É o objetivo? **SUCESSO**.
3. Não é: coloca o nó em FECHADOS.
4. Aplica todas as regras válidas, na ordem da estratégia.
5. Os filhos entram no fim de ABERTOS. Volta ao passo 1.

**ABERTOS**: fila dos nós gerados que ainda não foram analisados.

**FECHADOS**: nós já expandidos. Com poda, também servem para não gerar estados repetidos.""",
    strategy_note="Na largura a estratégia não muda quais nós existem em cada nível. Muda só a ordem deles dentro do nível, e portanto quantos nós são analisados antes do objetivo.",
    root_note="Os filhos são os mesmos, só a ordem na fila muda. Em P1 a solução começa por R4: `descending` já põe esse ramo na frente.",
    no_prune="""Sem poda, a árvore cresce sem parar: a regra inversa sempre gera de volta o avô. As árvores sem poda abaixo vão até o objetivo, no nível 3.""",
    prune="""Uma regra é descartada se o estado que ela gera já está em ABERTOS ou em FECHADOS.

**Poda global**: vale para a árvore toda, não só para o caminho, como no backtracking. Cada estado entra uma vez, então a árvore cabe inteira, sem limitar a profundidade.""",
    pseudocode="""busca_em_largura(problema, estratégia, poda)
    ABERTOS = fila com a raiz
    FECHADOS = vazio
    enquanto ABERTOS não estiver vazia:
        nó = tira o primeiro de ABERTOS
        se nó é o objetivo: SUCESSO
        coloca nó em FECHADOS
        para cada regra válida, na ordem da estratégia:
            filho = aplica a regra em nó
            se poda e filho está em ABERTOS ou FECHADOS:
                descarta a regra
            senão: põe filho no fim de ABERTOS
    FRACASSO""",
    path_strategy="ascending",
    path_note="3 movimentos. As duas estratégias, com e sem poda, chegam a este mesmo caminho, e ele é o menor possível.",
    complexity=(
        (
            "Largura sem poda",
            "O(bᵈ)",
            "O(bᵈ)",
            "ótima",
            "a fila guarda o nível inteiro",
        ),
        ("Largura com poda", "O(V + E)", "O(V)", "ótima", "cada estado entra uma vez"),
    ),
    compared_with=("backtracking",),
    symbols=("b", "d", "m", "V", "E"),
    conclusion="""## Conclusão

- Em P1 as duas estratégias acham R4, R1, R1: 3 movimentos, o ótimo. A estratégia só muda a ordem dentro de um nível e, com ela, o número de iterações.
- Nos 36 objetivos acha sempre o mínimo de movimentos (média 4,14). Como toda jogada custa 1, é também o menor custo.
- É a referência de comprimento para os outros algoritmos. O preço é o esforço: 18,5 iterações em média, contra 7,44 da busca ordenada.""",
    flowchart="""digraph flow {
%(style)s
  root [label="raiz na fila", shape=oval, fillcolor="%(root)s"];
  pop [label="tira o primeiro da fila"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="%(goal)s"];
  visit [label="visita: regras aplicáveis na ordem da estratégia,\\nmenos as que levam a um estado já gerado por qualquer ramo"];
  apply [label="aplica todas e coloca os filhos no fim da fila"];
  root -> pop;
  pop -> goal;
  goal -> success [label="sim"];
  goal -> visit [label="não"];
  visit -> apply;
  apply -> pop;
}""",
    frontier_demo=True,
)

HEURISTIC_CELLS: tuple[Cell, ...] = (
    markdown(
        """## A heurística: discos mal posicionados

Toda jogada custa 1, então o custo de um nó é só a sua profundidade. Quem ordena ABERTOS é a heurística **h**: uma estimativa de quantos movimentos ainda faltam. Um disco está **bem posicionado** quando está na haste e na altura do objetivo e todos os discos abaixo dele também estão. Cada disco contribui com o mínimo de movimentos que ainda precisa fazer:

| Situação do disco | Contribui | Por quê |
|---|---|---|
| bem posicionado | 0 | não precisa sair dali |
| em outra haste | 1 | pode chegar ao destino com um movimento |
| na haste certa, mas mal posicionado | 2 | precisa sair e voltar |

**h(estado)** é a soma dos três discos. Nunca passa do número de movimentos que falta (é admissível): cada movimento leva um disco só.

O código do projeto:"""
    ),
    *(writefile_cell(find(f"{SOURCE_DIR}/{module}")) for module in HEURISTIC_MODULES),
    code("explain_heuristic()"),
    code("children_heuristics()"),
)

GOALS_CELLS: tuple[Cell, ...] = (
    markdown(
        """## Comparativo: os 36 objetivos

Cada estado do espaço como objetivo, sempre a partir da mesma posição inicial, nas duas estratégias, da menor para a maior média.

### Nós expandidos nos 36 objetivos"""
    ),
    code('goals_boxplot("ordered", "expanded")'),
    markdown(
        "Na ordenada e na largura, expandidos = iterações − 1: o objetivo sai de ABERTOS, mas não é expandido."
    ),
    code('goals_stats("ordered", "expanded")'),
    markdown("### Iterações nos 36 objetivos"),
    code('goals_boxplot("ordered", "iterations")'),
    markdown(
        "Na largura, cada estado sai de ABERTOS uma vez, numa ordem que não depende do objetivo: nos 36 objetivos as iterações são sempre 1, 2, …, 36, só embaralhadas. Na ordenada a ordem depende do objetivo, porque a heurística é medida em relação a ele, e a busca vai mais direto: por isso a caixa dela fica à esquerda da largura."
    ),
    code('goals_stats("ordered", "iterations")'),
    markdown("### Nós gerados nos 36 objetivos"),
    code('goals_boxplot("ordered", "generated")'),
    code('goals_stats("ordered", "generated")'),
)

ORDERED_SECTION = AlgorithmSection(
    title="Busca ordenada",
    name="ordered",
    label="Ordenada",
    color="#eda100",
    list_mode="priority",
    complete=True,
    module="core/algorithms/ordered/algorithm.py",
    frontier="core/algorithms/ordered/frontier.py",
    frontier_class="PriorityFrontier",
    subtitle="ABERTOS vira uma fila ordenada pela heurística: sai primeiro o nó que parece mais perto do objetivo.",
    idea="""**Expanda sempre o nó aberto de menor heurística.**

Largura: fila, sai o primeiro que entrou.

Ordenada: fila pela heurística h, sai o de menor h; no empate, o gerado primeiro. Toda jogada custa 1, então o custo não ordena a fila: só decide qual de dois nós do mesmo estado fica.""",
    loop="""1. Tira de ABERTOS o nó de menor heurística; no empate, o gerado primeiro.
2. É o objetivo? **SUCESSO**.
3. Não é: coloca o nó em FECHADOS.
4. Aplica todas as regras válidas, na ordem da estratégia, e calcula a heurística de cada filho.
5. Os filhos entram em ABERTOS na posição da sua heurística. Volta ao passo 1.

**ABERTOS**: fila dos nós gerados que ainda não foram analisados, ordenada pela heurística (entre parênteses na tabela).

**FECHADOS**: nós já expandidos. Com poda, um filho cujo estado já está aqui é descartado.""",
    strategy_note="Na ordenada a estratégia só desempata irmãos de mesma heurística: decide quem fica na frente em ABERTOS. Em P1 as duas ordens fazem as mesmas 4 iterações e acham o mesmo caminho.",
    root_note="Em S0 a heurística vale 3. Na raiz, R4 leva a h = 2, R2 e R3 a h = 3 e R1 a h = 4. R4 sai primeiro nas duas ordens; a estratégia só decide entre R2 e R3, que empatam.",
    no_prune="""Sem poda, estados repetidos entram de novo em ABERTOS. Em P1 a heurística leva direto ao objetivo: 4 iterações, com 12 nós gerados em vez de 9. Nos 36 objetivos, porém, ordenar só pela heurística, sem poda, faz a busca girar entre estados de mesma h: 10 deles chegam ao limite de iterações.""",
    prune="""Técnica de poda da busca ordenada, com FECHADOS e o **vetor de menor custo** (aqui, o menor número de movimentos até cada estado). Toda vez que um nó é gerado,

- se o estado já foi expandido (está em FECHADOS), poda o nó;
- se o estado já está em ABERTOS por um caminho de mesmo tamanho ou menor, poda o nó;
- se o novo caminho é mais curto, tira o nó antigo de ABERTOS e da árvore e inclui o novo.

Em P1 o terceiro caso não acontece; nos 36 objetivos ele aparece 2 vezes com `ascending` e 1 com `descending`.""",
    pseudocode="""busca_ordenada(problema, estratégia, poda)
    ABERTOS = fila pela heurística com a raiz
    MENOR_CUSTO = {raiz: 0}
    FECHADOS = vazio
    enquanto ABERTOS não estiver vazia:
        nó = tira o de menor h de ABERTOS (no empate, o mais antigo)
        se nó é o objetivo: SUCESSO
        coloca nó em FECHADOS
        para cada regra válida, na ordem da estratégia:
            custo = custo(nó) + 1
            se poda e (filho está em FECHADOS ou custo >= MENOR_CUSTO[filho]):
                descarta a regra
            senão:
                se o estado do filho está em ABERTOS: tira o nó antigo
                MENOR_CUSTO[estado do filho] = custo
                põe o filho em ABERTOS, na posição de h(filho)
    FRACASSO""",
    path_strategy="ascending",
    path_note="R4, R1, R1: 3 movimentos, o ótimo. As duas estratégias, com e sem poda, chegam a este mesmo caminho.",
    complexity=(
        (
            "Ordenada sem poda",
            "pode não terminar",
            "cresce sem limite",
            "pode não achar",
            "sem FECHADOS, gira entre estados de mesma heurística",
        ),
        (
            "Ordenada com poda",
            "O((V + E) log V)",
            "O(V)",
            "não garante a mais curta",
            "cada estado é expandido uma vez; o heap custa log V por operação",
        ),
    ),
    compared_with=("breadth_first",),
    symbols=("b", "m", "V", "E"),
    conclusion="""## Conclusão

- Em P1: R4, R1, R1 (3 movimentos, o ótimo) em 4 iterações e 9 nós gerados, com as duas ordens. A largura precisa de 12 a 14 iterações.
- Nos 36 objetivos resolve todos e acha o mínimo de movimentos em 34 (`ascending`) e 33 (`descending`): média de 4,19 e 4,25 movimentos, contra 4,14 da largura. Em troca, faz 7,44 iterações em média, contra 18,5 da largura.
- Ordenar só pela heurística não garante o caminho mais curto: a busca segue o nó que parece mais perto do objetivo, não o que andou menos.""",
    flowchart="""digraph flow {
%(style)s
  root [label="raiz em ABERTOS", shape=oval, fillcolor="%(root)s"];
  pop [label="tira o de menor heurística;\\nno empate, o gerado primeiro"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="%(goal)s"];
  visit [label="visita: regras aplicáveis na ordem da estratégia, menos as que levam\\na estado fechado ou já aberto por um caminho igual ou menor"];
  apply [label="aplica todas; se um filho chega mais curto a um estado ainda aberto,\\no nó antigo sai de ABERTOS e da árvore"];
  root -> pop;
  pop -> goal;
  goal -> success [label="sim"];
  goal -> visit [label="não"];
  visit -> apply;
  apply -> pop;
}""",
    frontier_demo=True,
    uses_heuristic=True,
    rule_cells=HEURISTIC_CELLS,
    goals_cells=GOALS_CELLS,
)

GREEDY_SECTION = AlgorithmSection(
    title="Busca gulosa",
    name="greedy",
    label="Gulosa",
    color="#8e5bd6",
    list_mode="single",
    complete=False,
    module="core/algorithms/greedy/algorithm.py",
    subtitle="A descida da irrevogável, guiada pela heurística: cada passo vai para o filho que parece mais perto do objetivo.",
    idea="""**Aplique a regra que leva ao filho de menor heurística e siga em frente, sem guardar alternativas.**

A mesma descida da irrevogável: ABERTOS tem no máximo um nó e cada passo é definitivo. Muda só a escolha: em vez da primeira regra da estratégia, a que leva ao filho de menor h, a heurística da busca ordenada. Um beco sem saída encerra a busca em IMPASSE.

No código, a gulosa herda o laço da irrevogável e troca só o método que escolhe a regra, `_choose`.""",
    loop="""1. O estado atual é o objetivo? **SUCESSO**.
2. Não é: coloca o nó em FECHADOS.
3. Ordena as regras válidas pela estratégia e descarta as que voltam a um estado do caminho (poda).
4. Não sobrou regra: **IMPASSE**.
5. Aplica a regra que leva ao filho de menor heurística; no empate, a primeira da estratégia. O filho vira o estado atual. Volta ao passo 1.

**ABERTOS**: o único filho gerado, que vira o próximo estado atual.

**FECHADOS**: o caminho percorrido. Com poda, serve para não voltar a um estado do caminho.""",
    strategy_note="Na gulosa a estratégia só desempata filhos de mesma heurística. Ainda assim pode mudar o caminho e o desfecho: nos 36 objetivos, `ascending` resolve 29 e `descending` 28.",
    root_note="Na raiz, R4 leva a h = 2, o menor: as duas ordens aplicam R4. A irrevogável, sem a heurística, aplicaria R1 com `ascending`.",
    no_prune="""Sem poda, nada impede a gulosa de voltar a um estado já percorrido. Em P1 a heurística leva direto ao objetivo, em 4 iterações; nos 36 objetivos, porém, a gulosa sem poda gira até o limite de iterações em 12 (`ascending`) e 13 (`descending`) deles. Para caber no notebook, as execuções sem poda abaixo param em 30 iterações.""",
    prune="""A poda descarta a regra que leva a um estado que já está no caminho, como na irrevogável. Com ela a gulosa nunca repete estado e sempre para. Parar não é chegar: a heurística escolhe o filho que parece melhor agora, e esse caminho pode terminar em IMPASSE.""",
    pseudocode="""busca_gulosa(problema, estratégia, poda)
    nó = raiz
    enquanto verdadeiro:
        se nó é o objetivo: SUCESSO
        coloca nó em FECHADOS
        regras = regras válidas em nó, na ordem da estratégia
        se poda: descarta as que levam a um estado de FECHADOS
        se não sobrou regra: IMPASSE
        nó = aplica a regra de menor h(filho) em nó (no empate, a primeira)""",
    uses_heuristic=True,
    path_strategy="ascending",
    path_note="R4, R1, R1: 3 movimentos, o ótimo, com as duas estratégias. A irrevogável faz 14 movimentos com `ascending` e trava com `descending`.",
    complexity=(
        (
            "Gulosa sem poda",
            "não termina",
            "O(1)",
            "pode não achar",
            "pode girar num ciclo para sempre",
        ),
        (
            "Gulosa com poda",
            "O(b·m²)",
            "O(m)",
            "pode não achar",
            "um nó por iteração; h custa O(1) por filho, e cada regra é comparada com o caminho",
        ),
    ),
    compared_with=("irrevocable",),
    symbols=("b", "m"),
    conclusion="""## Conclusão

- Em P1: R4, R1, R1 (o ótimo) em 4 iterações e 4 nós gerados, com as duas ordens: o menor esforço entre todos os algoritmos.
- Nos 36 objetivos resolve 29 (`ascending`) e 28 (`descending`), contra 18 e 3 da irrevogável; o caminho é o mínimo em 20 deles. A média é de 6,0 e 5,33 iterações, contra 7,44 da ordenada.
- A heurística melhora muito a descida, mas não a garante: sem guardar as alternativas, um passo que parecia bom pode levar a um impasse.""",
    flowchart="""digraph flow {
%(style)s
  root [label="raiz", shape=oval, fillcolor="%(root)s"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="%(goal)s"];
  visit [label="visita: regras aplicáveis na ordem da estratégia,\\nmenos as que repetem estado do caminho"];
  left [label="sobrou regra?", shape=diamond];
  deadlock [label="IMPASSE", shape=oval, fillcolor="%(deadlock)s"];
  apply [label="aplica a que leva ao filho de menor heurística\\n(no empate, a primeira) e gera o filho"];
  root -> goal;
  goal -> success [label="sim"];
  goal -> visit [label="não"];
  visit -> left;
  left -> deadlock [label="não"];
  left -> apply [label="sim"];
  apply -> goal;
}""",
    no_prune_limit=30,
)

ALGORITHM_SECTIONS: tuple[AlgorithmSection, ...] = (
    IRREVOCABLE_SECTION,
    BACKTRACKING_SECTION,
    BREADTH_FIRST_SECTION,
    ORDERED_SECTION,
    GREEDY_SECTION,
)

SECTION_BY_NAME = {spec.name: spec for spec in ALGORITHM_SECTIONS}


def slide_modules() -> tuple[str, ...]:
    return (
        *PROBLEM_MODULES,
        *FRONTIER_MODULES,
        *ENGINE_MODULES,
        *RULE_MODULES,
        *STRATEGY_MODULES,
        *HEURISTIC_MODULES,
        *(spec.module for spec in ALGORITHM_SECTIONS),
        *(spec.frontier for spec in ALGORITHM_SECTIONS if spec.frontier),
    )


def complexity_table(rows: tuple[ComplexityRow, ...]) -> str:
    lines = [COMPLEXITY_HEADER, ("---",) * len(COMPLEXITY_HEADER)]
    lines.extend((f"**{name}**", *rest) for name, *rest in rows)
    return "\n".join(f"| {' | '.join(line)} |" for line in lines)


def all_complexity_rows() -> tuple[ComplexityRow, ...]:
    return tuple(row for spec in ALGORITHM_SECTIONS for row in spec.complexity)


def _complexity_rows(spec: AlgorithmSection) -> tuple[ComplexityRow, ...]:
    compared = (SECTION_BY_NAME[name] for name in spec.compared_with)
    return (*spec.complexity, *(row for other in compared for row in other.complexity))


def _writefiles(modules: tuple[str, ...]) -> tuple[Cell, ...]:
    return tuple(writefile_cell(find(f"{SOURCE_DIR}/{module}")) for module in modules)


def _limit(spec: AlgorithmSection) -> str:
    return (
        "" if spec.no_prune_limit is None else f", max_iterations={spec.no_prune_limit}"
    )


def _runs(spec: AlgorithmSection, *, prune: bool) -> tuple[Cell, ...]:
    cells: list[Cell] = []
    mode = "com" if prune else "sem"
    for strategy, label in SLIDE_STRATEGIES:
        variable = f"{mode}_poda_{label}"
        options = "" if prune else f", prune=False{_limit(spec)}"
        cells.extend(
            (
                markdown(f"### {mode.capitalize()} poda · {label}"),
                code(f'{variable} = case("{spec.name}", "{strategy}"{options})'),
                markdown(
                    f"#### ABERTOS e FECHADOS, iteração a iteração ({label}, {mode} poda)"
                ),
                code(f"lists_table({variable})"),
            )
        )
    return tuple(cells)


def section(spec: AlgorithmSection, index: int, *, first: bool) -> tuple[Cell, ...]:
    cells: list[Cell] = [
        markdown(f"# {index}. {spec.title}\n\n{spec.subtitle}"),
        markdown(
            "## O problema: carta P1, do estado inicial ao objetivo\n\n"
            "Cada estado lista as hastes da base para o topo. As seis regras R1 a R6 movem o disco do topo de uma haste para outra."
        ),
    ]
    if first:
        cells.append(
            markdown(
                "A legenda (discos, hastes e capacidades) e o catálogo de cartas, como estão no projeto:"
            )
        )
        cells.extend(_writefiles(PROBLEM_MODULES))
    cells.append(code("show_problem()"))

    cells.append(markdown(f"## A ideia\n\n{spec.idea}"))
    if spec.shows_frontier:
        cells.extend(_writefiles(FRONTIER_MODULES))
    if spec.frontier:
        cells.extend(_writefiles((spec.frontier,)))
    if spec.frontier_demo:
        cells.append(code(f'frontier_demo("{spec.name}")'))

    cells.append(markdown(f"## O laço e as listas\n\n{spec.loop}"))
    if first:
        cells.append(
            markdown(
                "O motor que todos os algoritmos compartilham: testar as regras, ordenar pela estratégia, podar, gerar o filho e contar. Cada algoritmo implementa só o próprio laço, em `_search`."
            )
        )
        cells.extend(_writefiles(ENGINE_MODULES))

    cells.append(
        markdown(
            "## As regras: seis regras, uma para cada par origem e destino\n\n"
            "Vale se a origem tem disco e o destino tem espaço. Toda jogada custa 1. Toda regra tem inversa: aplicar as duas em seguida volta ao mesmo estado."
            f"\n\n{RULES_LIST}"
        )
    )
    if first:
        cells.extend(_writefiles(RULE_MODULES))
    cells.extend((code("rules_table()"), code('show_rule_example("R4")')))
    cells.extend(spec.rule_cells)

    cells.append(
        markdown(
            f"## Estratégia de controle: a ordem em que as regras são aplicadas\n\n{spec.strategy_note}"
        )
    )
    if first:
        cells.extend(_writefiles(STRATEGY_MODULES))
    cells.append(code("strategies_table()"))

    limit = _limit(spec)
    cells.extend(
        (
            markdown(f"## As duas estratégias na mesma raiz\n\n{spec.root_note}"),
            code(f'root_children("{spec.name}")'),
            markdown(f"## Sem poda\n\n{spec.no_prune}"),
            code(f'growth("{spec.name}"{limit})'),
            *_runs(spec, prune=False),
            markdown(f"## Com poda\n\n{spec.prune}"),
            code(f'levels_chart("{spec.name}"{limit})'),
            *_runs(spec, prune=True),
            markdown(
                f"## Pseudocódigo\n\n```text\n{spec.pseudocode}\n```\n\n{PRUNE_FLAG}\n\nO código do projeto:"
            ),
            *_writefiles((spec.module,)),
            markdown(f"## Caminho solução\n\n{spec.path_note}"),
            code(f'show_path(solve("{spec.name}", "{spec.path_strategy}"))'),
            markdown(
                "## Comparativo: os caminhos encontrados\n\n"
                "Cada ponto é um movimento; o verde é o que chega ao objetivo."
            ),
            code(f'paths_plot("{spec.name}")'),
            markdown("## Comparativo: crescente contra decrescente"),
            code(f'strategy_table("{spec.name}")'),
            markdown(
                f"## Comparativo: {spec.title.lower()} contra os outros, mesmas estratégias"
            ),
            code(f'algorithms_table("{spec.name}")'),
            markdown("## Comparativo: quem explorou menos nós"),
            code(f'expanded_chart("{spec.name}")'),
            *spec.goals_cells,
            markdown(f"## Complexidade\n\n{complexity_table(_complexity_rows(spec))}"),
            code(f'complexity_values("{spec.name}", {spec.symbols!r})'),
            markdown(spec.conclusion),
            *_extras(spec),
        )
    )
    return tuple(cells)


def flowcharts() -> Cell:
    entries = "\n".join(
        f"    {spec.name!r}: r'''{spec.flowchart}'''," for spec in ALGORITHM_SECTIONS
    )
    return code(
        f"""#@title Fluxogramas
FLOW_COLORS = {{
    "font": theme.GRAPH_FONT,
    "fill": theme.GRAPH_VISITED_FILL,
    "line": theme.GRAPH_NODE_COLOR,
    "root": theme.GRAPH_ROOT_FILL,
    "goal": theme.GRAPH_GOAL_FILL,
    "deadlock": theme.GRAPH_DEADLOCK_FILL,
}}
FLOW_STYLE = r'''{FLOW_STYLE}''' % FLOW_COLORS
FLOWCHARTS = {{
{entries}
}}


def show_flowchart(algorithm):
    show_dot(FLOWCHARTS[algorithm] % {{**FLOW_COLORS, "style": FLOW_STYLE}})""",
        hidden=True,
    )


def _extras(spec: AlgorithmSection) -> tuple[Cell, ...]:
    return (
        markdown(f"## Extras de {spec.title.lower()}"),
        markdown("### Fluxograma"),
        code(f'show_flowchart("{spec.name}")'),
        markdown("### Passo a passo do trace, com poda e ordem crescente"),
        code(f'show_trace(solve("{spec.name}", "ascending"))'),
        markdown("### Comparação em P1, placar lexicográfico"),
        code(f'p1_comparison("{spec.name}")'),
        markdown(
            "### Comparação nos 36 objetivos\n\nCada métrica: média / mediana; movimentos contam só os sucessos."
        ),
        code(f'goals_comparison("{spec.name}")'),
    )
