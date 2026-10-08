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
STRATEGY_MODULES = (
    "core/rules/strategies/ascending.py",
    "core/rules/strategies/descending.py",
)
SLIDE_STRATEGIES = (("ascending", "crescente"), ("descending", "decrescente"))


@dataclass(frozen=True, slots=True)
class AlgorithmSection:
    title: str
    name: str
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
    complexity: str
    symbols: tuple[str, ...]
    conclusion: str
    flowchart: str
    no_prune_limit: int | None = None
    shows_frontier: bool = False
    frontier_demo: bool = False


FLOW_STYLE = """  rankdir=TB; fontname="Helvetica"; bgcolor="transparent";
  node [fontname="Helvetica", fontsize=11, shape=box, style="rounded,filled", fillcolor="#ffffff", color="#333333"];
  edge [fontname="Helvetica", fontsize=10, color="#333333"];"""

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
    module="core/algorithms/irrevocable.py",
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
    complexity="""| Tempo | Memória | | Por quê | Solução |
|---|---|---|---|---|
| não termina | O(1) | **Irrevogável sem poda** | pode girar num ciclo para sempre | pode não achar |
| O(b·m²) | O(m) | **Irrevogável com poda** | um nó por iteração, no máximo m; cada regra é comparada com o caminho | pode não achar |""",
    symbols=("b", "m", "V"),
    conclusion="""## Conclusão

- Em P1, `descending` trava na 3ª iteração: R4 e R5 levam a `H1[V,R,A]`, e de lá as duas regras aplicáveis voltam a estados do caminho. `ascending` chega, mas com 14 movimentos, quando o ótimo tem 3.
- Nos 36 objetivos, resolve 18 com `ascending` e 3 com `descending`. É o único algoritmo que deixa objetivos sem solução.
- É barata (um nó gerado por iteração), mas não garante solução nem qualidade: a estratégia decide tudo.""",
    flowchart="""digraph flow {
%s
  root [label="raiz", shape=oval, fillcolor="#dbe9ff"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="#c6f0c6"];
  visit [label="visita: regras aplicáveis na ordem da estratégia,\\nmenos as que repetem estado do caminho"];
  left [label="sobrou regra?", shape=diamond];
  deadlock [label="IMPASSE", shape=oval, fillcolor="#f7c6c6"];
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
    module="core/algorithms/backtracking.py",
    subtitle="A mesma descida da busca irrevogável, com as alternativas de cada nó guardadas numa pilha.",
    idea="""**Desça enquanto houver regra; sem regra, volte ao ancestral mais próximo que ainda tem alternativa.**

Backtracking: pilha, sai o último que entrou. Afunda num ramo.

A fronteira do projeto, em `core/search_tree/frontier.py`, tem as três filas usadas pelos algoritmos: a pilha do backtracking, a fila da largura e a fila por custo da ordenada.""",
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
    complexity="""| Tempo | Memória | | Por quê | Solução |
|---|---|---|---|---|
| não termina | O(L) | **Backtracking sem poda** | o ciclo cresce a pilha até o limite L de iterações | pode não achar |
| O(bᵐ) | O(m) | **Backtracking com poda** | só guarda o caminho atual | a primeira achada |""",
    symbols=("b", "m"),
    conclusion="""## Conclusão

- Em P1 as duas estratégias chegam ao objetivo. Com `descending` são 51 iterações, 14 retrocessos e 22 movimentos para um ótimo de 3; com `ascending` não há retrocesso e o caminho é o mesmo da irrevogável, com 14 movimentos.
- Nos 36 objetivos resolve todos, mas com média de 12,81 a 16,5 movimentos, contra 4,14 do ótimo. Com `descending`, a média de iterações é 82,92 e a mediana 21,5: um objetivo passa de 2 mil iterações.
- Resolve o problema da irrevogável (o impasse vira desvio), mas para no primeiro objetivo que encontra, tenha o caminho o comprimento que tiver.""",
    flowchart="""digraph flow {
%s
  root [label="raiz na pilha", shape=oval, fillcolor="#dbe9ff"];
  goal [label="topo da pilha\\né o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="#c6f0c6"];
  first [label="primeira vez nele?", shape=diamond];
  visit [label="visita e guarda a lista de regras aplicáveis,\\nna ordem da estratégia, sem as que repetem estado do caminho"];
  empty [label="lista vazia?", shape=diamond];
  deadlock [label="impasse", fillcolor="#f7c6c6"];
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
    module="core/algorithms/breadth_first.py",
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
    complexity="""| Tempo | Memória | | Por quê | Solução |
|---|---|---|---|---|
| O(bᵈ) | O(bᵈ) | **Largura sem poda** | a fila guarda o nível inteiro | ótima |
| O(V + E) | O(V) | **Largura com poda** | cada estado entra uma vez | ótima |
| O(bᵐ) | O(m) | **Backtracking** | só guarda o caminho atual | a primeira achada |""",
    symbols=("b", "d", "m", "V", "E"),
    conclusion="""## Conclusão

- Em P1 as duas estratégias acham R4, R1, R1: 3 movimentos, o ótimo. A estratégia só muda a ordem dentro de um nível e, com ela, o número de iterações.
- Nos 36 objetivos acha sempre o mínimo de movimentos (média 4,14). No custo, passa do menor em 1 das 72 execuções, porque não olha o custo das regras.
- É a referência de comprimento para os outros algoritmos. Em custo, a referência é a busca ordenada.""",
    flowchart="""digraph flow {
%s
  root [label="raiz na fila", shape=oval, fillcolor="#dbe9ff"];
  pop [label="tira o primeiro da fila"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="#c6f0c6"];
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

ORDERED_SECTION = AlgorithmSection(
    title="Busca ordenada",
    name="ordered",
    module="core/algorithms/ordered.py",
    subtitle="Cada regra tem um custo, e ABERTOS vira uma fila ordenada pelo custo acumulado desde a raiz.",
    idea="""**Expanda sempre o nó aberto de menor custo acumulado.**

Largura: fila, sai o primeiro que entrou.

Ordenada: fila por custo, sai o mais barato; no empate, o gerado primeiro. Com o mesmo custo em todas as regras, seria a busca em largura.""",
    loop="""1. Tira de ABERTOS o nó de menor custo; no empate, o gerado primeiro.
2. É o objetivo? **SUCESSO**.
3. Não é: coloca o nó em FECHADOS.
4. Aplica todas as regras válidas, na ordem da estratégia. O custo do filho é o do pai mais o da regra.
5. Os filhos entram em ABERTOS na posição do seu custo. Volta ao passo 1.

**ABERTOS**: fila dos nós gerados que ainda não foram analisados, ordenada por custo.

**FECHADOS**: nós já expandidos. Com poda, o vetor de menor custo cobre ABERTOS e FECHADOS de uma vez.""",
    strategy_note="Na ordenada a estratégia só desempata irmãos de mesmo custo: decide quem fica na frente em ABERTOS, nunca o custo da solução. A coluna **Custo** da tabela de regras é a distância entre as hastes: R2 e R5 pulam a haste do meio e custam 2.",
    root_note="Na raiz, R1, R3 e R4 custam 1 e R2 custa 2. A estratégia ordena os três de custo 1; R2 fica atrás de todos nas duas ordens.",
    no_prune="""Sem poda, estados repetidos entram de novo em ABERTOS, cada um com o custo do caminho que o gerou. A busca ainda acha o menor custo, porque só para quando o objetivo sai da fila, mas gera muito mais nós.""",
    prune="""Técnica de poda da busca ordenada, com o **vetor de menor custo**: toda vez que um nó é gerado,

- se é a primeira vez que o estado aparece, guarda o estado com o custo atual;
- se o estado aparece repetido com custo maior ou igual ao do vetor, poda o nó;
- se aparece com custo menor, atualiza o vetor, tira o nó antigo de ABERTOS e da árvore e inclui o novo.

Com os custos deste problema o terceiro caso nunca acontece em P1: R1 seguida de R4 custa o mesmo que R2, e empate é podado.""",
    pseudocode="""busca_ordenada(problema, estratégia, poda)
    ABERTOS = fila por custo com a raiz (custo 0)
    MENOR_CUSTO = {raiz: 0}
    enquanto ABERTOS não estiver vazia:
        nó = tira o de menor custo de ABERTOS (no empate, o mais antigo)
        se nó é o objetivo: SUCESSO
        coloca nó em FECHADOS
        para cada regra válida, na ordem da estratégia:
            custo = custo(nó) + custo(regra)
            se poda e custo >= MENOR_CUSTO[estado do filho]:
                descarta a regra
            senão:
                se o estado do filho está em ABERTOS: tira o nó antigo
                MENOR_CUSTO[estado do filho] = custo
                põe o filho em ABERTOS, na posição do custo
    FRACASSO""",
    path_strategy="ascending",
    path_note="R4, R1, R1: custo 1 + 1 + 1 = 3, o menor possível. As duas estratégias, com e sem poda, chegam a este mesmo caminho.",
    complexity="""| Tempo | Memória | | Por quê | Solução |
|---|---|---|---|---|
| O(b^(1 + C*/ε)) | O(b^(1 + C*/ε)) | **Ordenada sem poda** | a fila guarda todo nó mais barato que o objetivo, repetido ou não | menor custo |
| O((V + E) log V) | O(V) | **Ordenada com poda** | cada estado entra uma vez; o heap custa log V por operação | menor custo |""",
    symbols=("b", "C*", "ε", "V", "E"),
    conclusion="""## Conclusão

- Em P1: R4, R1, R1, custo 3. Com `ascending` são 10 iterações, a execução mais rápida de P1; com `descending`, o mesmo caminho em 11.
- Nos 36 objetivos acha sempre o menor custo (média 5,22, a menor de todas) e também o mínimo de movimentos. A média de iterações é 18,5, a mesma da largura.
- A estratégia só desempata irmãos de mesmo custo: nunca muda o custo da solução.""",
    flowchart="""digraph flow {
%s
  root [label="raiz em ABERTOS", shape=oval, fillcolor="#dbe9ff"];
  pop [label="tira o de menor custo;\\nno empate, o gerado primeiro"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="#c6f0c6"];
  visit [label="visita: regras aplicáveis na ordem da estratégia,\\nmenos as que não baixam o menor custo conhecido do estado"];
  apply [label="aplica todas; se um filho chega mais barato a um estado ainda aberto,\\no nó antigo sai de ABERTOS e da árvore"];
  root -> pop;
  pop -> goal;
  goal -> success [label="sim"];
  goal -> visit [label="não"];
  visit -> apply;
  apply -> pop;
}""",
    frontier_demo=True,
)

ALGORITHM_SECTIONS: tuple[AlgorithmSection, ...] = (
    IRREVOCABLE_SECTION,
    BACKTRACKING_SECTION,
    BREADTH_FIRST_SECTION,
    ORDERED_SECTION,
)


def slide_modules() -> tuple[str, ...]:
    return (
        *PROBLEM_MODULES,
        *FRONTIER_MODULES,
        *ENGINE_MODULES,
        *RULE_MODULES,
        *STRATEGY_MODULES,
        *(spec.module for spec in ALGORITHM_SECTIONS),
    )


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
    if spec.frontier_demo:
        cells.append(code(f'frontier_demo("{spec.name}")'))

    cells.append(markdown(f"## O laço e as listas\n\n{spec.loop}"))
    if first:
        cells.append(
            markdown(
                "O motor que os quatro algoritmos compartilham: testar as regras, ordenar pela estratégia, podar, gerar o filho e contar. Cada algoritmo implementa só o próprio laço, em `_search`."
            )
        )
        cells.extend(_writefiles(ENGINE_MODULES))

    cells.append(
        markdown(
            "## As regras: seis regras, uma para cada par origem e destino\n\n"
            "Vale se a origem tem disco e o destino tem espaço. Toda regra tem inversa: aplicar as duas em seguida volta ao mesmo estado."
            f"\n\n{RULES_LIST}"
        )
    )
    if first:
        cells.extend(_writefiles(RULE_MODULES))
    cells.extend((code("rules_table()"), code('show_rule_example("R4")')))

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
            markdown(f"## Complexidade\n\n{spec.complexity}"),
            code(f'complexity_values("{spec.name}", {spec.symbols!r})'),
            markdown(spec.conclusion),
            *_extras(spec),
        )
    )
    return tuple(cells)


def flowcharts() -> Cell:
    entries = "\n".join(
        f"    {spec.name!r}: r'''{spec.flowchart % FLOW_STYLE}''',"
        for spec in ALGORITHM_SECTIONS
    )
    return code(
        f"""#@title Fluxogramas
FLOWCHARTS = {{
{entries}
}}


def show_flowchart(algorithm):
    show_dot(FLOWCHARTS[algorithm])""",
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
            "### Comparação nos 36 objetivos\n\nCada métrica: média / mediana; movimentos e custo contam só os sucessos."
        ),
        code(f'goals_comparison("{spec.name}")'),
    )
