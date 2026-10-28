from __future__ import annotations

from collections.abc import Callable
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
HEURISTIC_MODULES = ("core/heuristics/misplacement.py",)
COST_MODULES = (
    "core/costs/weight_distance.py",
    "core/costs/step_weight_distance.py",
    "core/costs/unit.py",
)
SLIDE_STRATEGIES = (("ascending", "crescente"), ("descending", "decrescente"))
COMPLEXITY_HEADER = ("Algoritmo", "Tempo", "Memória", "Solução", "Por quê")

ComplexityRow = tuple[str, str, str, str, str]
MarkedCell = tuple[str, str]
MarkedRow = tuple[str, tuple[MarkedCell, MarkedCell, MarkedCell], str]

MODULE_NOTES = {
    "core/rules/domain/base.py": """a legenda do problema.

- **Discos**: verde, vermelho e azul. São distintos só pela cor: não há ordem de tamanho.
- **Hastes**: H1 comporta até 3 discos, H2 até 2 e H3 até 1. A capacidade é a única restrição do problema e faz o papel da ordem de tamanho da Torre de Hanói.
- **Estado**: uma tupla de três pilhas, cada uma escrita da base para o topo. É imutável.
- **`TransitionRule`**: o contrato de uma regra. `is_applicable` diz se o movimento vale no estado, `apply` devolve o estado que resulta dele (um estado novo; o recebido não muda). A regra não sabe quanto custa: o custo real fica em `core/costs/`.

A busca só conhece esse contrato: ela testa a regra e aplica a que passou, sem saber o que é disco ou haste.""",
    "core/domain/problem.py": """o estado inicial e as cartas.

- **`INITIAL_STATE`**: o estado inicial, fixo: verde e vermelho em H1, azul em H2 e H3 vazia.
- **`Problem`**: uma carta, que é um objetivo a alcançar a partir do estado inicial. Inicial e objetivo são validados quando a carta é criada.
- **`PROBLEMS`**: o catálogo de cartas. Hoje só tem P1.
- **`all_goal_problems`**: cria uma carta para cada um dos 36 estados do espaço (G01 a G36), todas a partir do mesmo estado inicial. São as cartas usadas na comparação dos algoritmos.""",
    "core/algorithms/domain/base.py": """o motor que todos os algoritmos compartilham.

`solve` é a entrada da busca: cria a raiz, cronometra o `_search` do algoritmo e monta o resultado, com o desfecho, o caminho, as métricas e o trace. Cada algoritmo implementa só o próprio laço, em `_search`, e usa os métodos abaixo.

| Método | O que faz |
|---|---|
| `_applicable_rules` | Testa as seis regras no nó, ordena as válidas pela estratégia e, com poda, descarta as que repetem estado. |
| `_is_repetition` | O critério da poda. No motor: o estado já está no caminho do nó. A largura, a ordenada e a gulosa trocam esse critério. |
| `_next_iteration` | Conta mais uma iteração. Devolve falso quando o limite estoura, e a busca termina em LIMITE. |
| `_visit` | Registra que o nó foi expandido. |
| `_expand` | Aplica a regra e cria o nó filho. É o único ponto em que a árvore cresce. |
| `_succeed` | Guarda o nó objetivo, de onde o caminho solução é reconstruído, e devolve SUCESSO. |
| `_deadlock` | Registra um impasse: o nó não tem regra para aplicar. Não encerra a busca; quem decide o que fazer é o algoritmo. |
| `_backtrack` | Registra um retrocesso. O retrocesso em si é feito pelo algoritmo. |
| `_exhausted` | Não há mais nada a explorar e o objetivo não apareceu: devolve FRACASSO. |
| `_observe_frontier` | Guarda o maior tamanho que ABERTOS já teve. |
| `_record` e `_record_prune` | Anotam no trace cada evento e cada regra podada, com a iteração em que aconteceram. |""",
    "core/rules/domain/constraints.py": """as duas condições para uma regra valer.

1. A haste de origem tem pelo menos um disco.
2. A haste de destino ainda tem espaço: com mais um disco, não passa da capacidade.

As duas dependem só do estado atual. Não voltar a um estado do caminho depende do percurso, e por isso fica na poda dos algoritmos, não aqui.""",
    "core/rules/moves.py": """as seis regras.

`Move` guarda a origem e o destino de uma regra. `apply` tira o disco do topo da origem e o põe no topo do destino, devolvendo um estado novo. Aplicar uma regra que não vale no estado é erro.""",
    "core/rules/domain/catalog.py": """o catálogo das regras.

`RULES` tem as seis regras na ordem R1 a R6. `INVERSE_RULE_ID` dá a inversa de cada uma, que é a regra com origem e destino trocados: R1 e R3, R2 e R5, R4 e R6.""",
    "core/rules/strategies/canonical.py": """as duas estratégias de controle.

`CanonicalOrder` ordena as regras válidas pela posição no catálogo: `ascending` de R1 a R6 e `descending` de R6 a R1.""",
    "core/costs/weight_distance.py": """a parte de peso e distância do custo.

`WEIGHTS` dá o peso de cada disco. `WeightDistance.cost` olha o disco no topo da haste de origem e multiplica o peso dele pela distância entre a origem e o destino. Sozinha, é a segunda função de custo, escolhida com `--cost weight_distance`.""",
    "core/costs/step_weight_distance.py": """o custo real padrão.

`StepWeightDistance.cost` soma `STEP_COST`, os 10 de toda jogada, ao peso × distância da função anterior.""",
    "core/costs/unit.py": """a terceira função de custo real.

`UnitCost.cost` devolve 1 para qualquer jogada: o custo de um caminho vira o número de movimentos. É escolhida com `--cost unit`.""",
    "core/heuristics/misplacement.py": """a heurística no código.

- **`contributions`**: quanto cada disco soma em h (0, 1 ou 2), como na tabela acima.
- **`misplacement`**: h do estado, a soma das três contribuições.
- **`_common_base`**: quantos discos de uma haste, de baixo para cima, já coincidem com o objetivo. Esses são os bem posicionados.""",
    "core/search_tree/frontier.py": """o contrato da fronteira, a lista de ABERTOS.

A fronteira guarda os nós já gerados que ainda não foram analisados. São três operações: `push` guarda um nó, `pop` tira um nó e `len` conta quantos ainda esperam. Fronteira vazia encerra a busca.

O contrato não diz qual nó o `pop` devolve. É a única coisa que muda entre as implementações, e é o que define cada busca.""",
    "core/algorithms/backtracking/frontier.py": """a pilha do backtracking.

O nó entra e sai pelo topo: sai o último que entrou. Depois de `push` de S1, S2 e S3, o `pop` devolve S3. O filho recém-gerado é sempre o próximo a ser analisado, e por isso a busca afunda num ramo até o fim.""",
    "core/algorithms/breadth_first/frontier.py": """a fila da busca em largura.

O nó entra pelo fim e sai pelo início: sai o primeiro que entrou. Depois de `push` de S1, S2 e S3, o `pop` devolve S1. Os filhos esperam atrás de todo o nível atual, e por isso a busca varre nível por nível.

A única linha diferente da pilha é a do `pop`. A fila usa `deque` porque tirar do início de uma `list` custa O(n), e de um `deque`, O(1).""",
    "core/algorithms/ordered/frontier.py": """a fila de prioridade da busca ordenada e da gulosa.

Sai o nó de menor prioridade (na ordenada, o custo real acumulado; na gulosa, a heurística); no empate, o que foi gerado primeiro. Depois de `push` de S1(5), S2(6), S3(6) e S4(1), o `pop` devolve S4, S1, S2 e S3. Irmãos de mesma prioridade são gerados na ordem da estratégia, então é ela que desempata entre eles.

A fila é um heap de (prioridade, ordem de geração, nó). `remove` tira um nó que ainda está na fila, o que a poda usa quando um caminho mais curto chega ao mesmo estado. A remoção é adiada: o nó só é descartado quando chegaria a vez dele no `pop`.""",
}


def _writefiles(modules: tuple[str, ...]) -> tuple[Cell, ...]:
    """Cada módulo mostrado: o texto que o explica e, em seguida, o código."""
    return tuple(
        cell
        for module in modules
        for cell in (
            markdown(f"**`{SOURCE_DIR}/{module}`**: {MODULE_NOTES[module]}"),
            writefile_cell(find(f"{SOURCE_DIR}/{module}")),
        )
    )


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
    code_note: str
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
    marked_complexity: tuple[MarkedRow, ...] = ()
    deck: Callable[[AlgorithmSection, int], tuple[Cell, ...]] | None = None


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

PRUNE_FLAG = "**poda** vem de `--no-prune`: desligada, a linha da poda não roda (na ordenada e na gulosa, um nó ainda não gera um estado do próprio caminho). A **estratégia** só muda a ordem do *para cada*."

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
    code_note="""`_search` é o laço do pseudocódigo: a cada volta, aplica a primeira regra que sobrou, na ordem da estratégia.""",
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
- Nos 36 objetivos, resolve 18 com `ascending` e 3 com `descending`. É o único algoritmo que deixa objetivos sem solução.
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

O contrato da fronteira fica em `core/search_tree/frontier.py`. Cada algoritmo traz a sua implementação ao lado, na própria pasta: a pilha do backtracking, a fila da largura e a fila de prioridade da ordenada, que a gulosa reaproveita.""",
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
    code_note="""`path` é a PILHA, com o caminho atual. `untried` guarda, para cada nó do caminho, as regras que ele ainda não tentou.

A cada iteração o topo sai da pilha. Se ele ainda tem regra, volta para a pilha e o filho entra por cima: a busca desce. Se não tem, ele não volta: é o retrocesso, e o pai passa a ser o topo.

`_remaining_rules` monta a lista de regras na primeira vez no nó, já com a poda, e registra o impasse se ela nascer vazia. Nas voltas seguintes ao nó, só devolve o que sobrou da lista.""",
    path_strategy="descending",
    path_note="Com a ordem decrescente: 22 movimentos para um ótimo de 3, depois de 14 retrocessos.",
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
    code_note="""`_closed` guarda os estados de FECHADOS e `_open_states` os de ABERTOS. `_is_repetition` troca o critério de poda do motor: descarta a regra cujo estado gerado está em qualquer um dos dois.""",
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
- Nos 36 objetivos acha sempre o mínimo de movimentos (média 4,14). Menos movimentos não é menor custo: entre os caminhos mais curtos ela fica com o primeiro que acha, e paga em média 51,72 e 51,67, contra 51,33 da busca ordenada.
- É a referência de comprimento para os outros algoritmos. O preço é o esforço: 18,5 iterações em média, contra 7,44 da busca gulosa.""",
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

Na gulosa quem ordena ABERTOS é a heurística **h**: uma estimativa de quantos movimentos ainda faltam. O custo real não entra na escolha. Um disco está **bem posicionado** quando está na haste e na altura do objetivo e todos os discos abaixo dele também estão. Cada disco contribui com o mínimo de movimentos que ainda precisa fazer:

| Situação do disco | Contribui | Por quê |
|---|---|---|
| bem posicionado | 0 | não precisa sair dali |
| em outra haste | 1 | pode chegar ao destino com um movimento |
| na haste certa, mas mal posicionado | 2 | precisa sair e voltar |

**h(estado)** é a soma dos três discos. Nunca passa do número de movimentos que falta (é admissível): cada movimento leva um disco só.

A heurística é um módulo de `core/heuristics/`, escolhido com `--heuristic`. Esta é a padrão; a outra, `color_distance`, soma o peso de cada disco vezes a distância até a haste do objetivo.
"""
    ),
    *_writefiles(HEURISTIC_MODULES),
    code("explain_heuristic()"),
    markdown(
        "### Quanto cada disco soma em h\n\nOs quatro primeiros estados são o caminho de P1: h cai de 3 para 2, 1 e 0. Os dois últimos mostram a haste certa no lugar errado, que vale 2."
    ),
    code("heuristic_examples()"),
    markdown("### A heurística de cada filho da raiz"),
    code("children_heuristics()"),
    markdown(
        """### As duas heurísticas comparadas

A gulosa com cada heurística do registro, em P1 e nos 36 objetivos. A de cor e distância só olha a haste, não a altura: resolve todos os objetivos, mas com mais iterações, mais movimentos e mais custo."""
    ),
    code("heuristics_comparison()"),
    markdown(
        """## O custo real: jogada, peso e distância

A gulosa não usa o custo real para escolher o próximo nó. Ele é somado nas arestas do caminho solução, da raiz até o objetivo, e dá o custo real da solução. É a mesma função da busca ordenada: **10 + peso do disco movido × distância**."""
    ),
    code("children_costs()"),
)

GOALS_CELLS: tuple[Cell, ...] = (
    markdown(
        """## Comparativo: os 36 objetivos

Cada estado do espaço como objetivo, sempre a partir da mesma posição inicial, nas duas estratégias, da menor para a maior média.

### Nós expandidos nos 36 objetivos"""
    ),
    code('goals_boxplot("ordered", "expanded")'),
    markdown(
        "Na ordenada, na gulosa e na largura, expandidos = iterações − 1: o objetivo sai de ABERTOS, mas não é expandido."
    ),
    code('goals_stats("ordered", "expanded")'),
    markdown("### Iterações nos 36 objetivos"),
    code('goals_boxplot("ordered", "iterations")'),
    markdown(
        "Na largura e na ordenada, cada estado sai de ABERTOS uma vez, numa ordem que não depende do objetivo (por nível numa, por custo real na outra): nos 36 objetivos as iterações são sempre 1, 2, …, 36, só embaralhadas. Na gulosa a ordem depende do objetivo, porque a heurística é medida em relação a ele, e a busca vai mais direto: por isso a caixa dela fica à esquerda das outras duas."
    ),
    code('goals_stats("ordered", "iterations")'),
    markdown("### Nós gerados nos 36 objetivos"),
    code('goals_boxplot("ordered", "generated")'),
    code('goals_stats("ordered", "generated")'),
    markdown("### Custo real da solução em P1"),
    code('cost_chart("ordered")'),
    markdown(
        "### Custo real da solução nos 36 objetivos\n\nA ordenada tem sempre o menor custo real: é o que ela ordena."
    ),
    code('goals_boxplot("ordered", "cost")'),
    code('goals_stats("ordered", "cost")'),
)

GREEDY_GOALS_CELLS: tuple[Cell, ...] = (
    markdown(
        """## A gulosa não garante a melhor solução

A heurística olha o que parece faltar, não o que o caminho já custou. Abaixo, os objetivos em que a gulosa paga mais que a ordenada, com o pior caso desenhado."""
    ),
    code("dearer_than_ordered()"),
    markdown("## Comparativo: custo real da solução em P1"),
    code('cost_chart("greedy")'),
    markdown(
        """## Comparativo: os 36 objetivos

Cada estado do espaço como objetivo, sempre a partir da mesma posição inicial, nas duas estratégias, da menor para a maior média.

### Nós expandidos nos 36 objetivos"""
    ),
    code('goals_boxplot("greedy", "expanded")'),
    code('goals_stats("greedy", "expanded")'),
    markdown("### Iterações nos 36 objetivos"),
    code('goals_boxplot("greedy", "iterations")'),
    markdown(
        "Na largura e na ordenada as iterações são sempre 1, 2, …, 36, só embaralhadas. Na gulosa a ordem em que os estados saem de ABERTOS depende do objetivo, e a busca vai mais direto: a caixa dela fica à esquerda das outras."
    ),
    code('goals_stats("greedy", "iterations")'),
    markdown("### Nós gerados nos 36 objetivos"),
    code('goals_boxplot("greedy", "generated")'),
    code('goals_stats("greedy", "generated")'),
    markdown(
        "### Custo real da solução nos 36 objetivos\n\nAqui a gulosa não lidera: a ordenada tem o menor custo real."
    ),
    code('goals_boxplot("greedy", "cost")'),
    code('goals_stats("greedy", "cost")'),
)

COST_CELLS: tuple[Cell, ...] = (
    markdown(
        """## O custo real: jogada, peso e distância

Cada jogada tem um **custo real**, e o custo de um nó é a soma dos custos das jogadas da raiz até ele. É esse custo acumulado que ordena ABERTOS na busca ordenada.

| Parte | Vale | Por quê |
|---|---|---|
| por jogada | 10 | toda jogada conta, e conta mais que o esforço |
| peso do disco | verde 1, vermelho 2, azul 3 | mover um disco pesado custa mais |
| distância | 1 entre hastes vizinhas, 2 de H1 para H3 | ir mais longe custa mais |

**custo(jogada) = 10 + peso do disco movido × distância.** Vai de 11 (o verde, uma haste) a 16 (o azul, duas hastes).

O peso × distância vai de 1 a 6, sempre menos que os 10 da jogada: um caminho com um movimento a mais nunca sai mais barato. O caminho de menor custo é sempre um dos de menos movimentos, e o peso × distância só desempata entre eles.

A função de custo é um módulo de `core/costs/`, escolhido com `--cost`. Esta é a padrão. As outras duas são `weight_distance`, só o peso × distância, com que o caminho mais barato pode ter um movimento a mais, e `unit`, 1 por jogada.
"""
    ),
    *_writefiles(COST_MODULES),
    code("children_costs()"),
    markdown(
        """### As três funções de custo comparadas

A ordenada com cada função de custo do registro, em P1 e nos 36 objetivos. Com os 10 por jogada e com o custo unitário ela acha sempre o mínimo de movimentos; só com peso × distância, sem os 10, a média de movimentos sobe."""
    ),
    code("costs_comparison()"),
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
    subtitle="ABERTOS vira uma fila ordenada pelo custo real: sai primeiro o nó mais barato de alcançar.",
    idea="""**Expanda sempre o nó aberto de menor custo real acumulado.**

Largura: fila, sai o primeiro que entrou.

Ordenada: fila pelo custo, sai o mais barato; no empate, o gerado primeiro. O custo de um nó é a soma dos custos reais das jogadas da raiz até ele.""",
    loop="""1. Tira de ABERTOS o nó de menor custo; no empate, o gerado primeiro.
2. É o objetivo? **SUCESSO**.
3. Não é: coloca o nó em FECHADOS.
4. Aplica todas as regras válidas, na ordem da estratégia. Custo do filho = custo do pai + custo real da jogada.
5. Os filhos entram em ABERTOS na posição do seu custo. Volta ao passo 1.

**ABERTOS**: fila dos nós gerados que ainda não foram analisados, ordenada pelo custo acumulado (entre parênteses na tabela).

**FECHADOS**: nós já expandidos. Com poda, um filho cujo estado já está aqui é descartado.""",
    strategy_note="Na ordenada a estratégia só desempata irmãos de mesmo custo: decide quem fica na frente em ABERTOS, nunca o custo da solução. Em P1 as duas ordens fazem as mesmas 11 iterações e acham o mesmo caminho.",
    root_note="Na raiz, R1 custa 12 (o vermelho, uma haste), R3 e R4 custam 13 (o azul, uma haste) e R2 custa 14 (o vermelho, duas hastes). R1 sai primeiro nas duas ordens; a estratégia só decide entre R3 e R4, que empatam.",
    no_prune="""Sem a técnica de poda, estados repetidos entram de novo em ABERTOS e em FECHADOS, cada vez por outro caminho. Só uma coisa o método nunca faz: um nó não gera um estado que já está no seu próprio caminho, da raiz até ele. A busca ainda acha o caminho de menor custo, porque o objetivo só sai da fila quando nada mais barato resta, mas trabalha mais: em P1 são 16 iterações e 28 nós gerados, contra 11 e 18 com poda, e ABERTOS chega a 13 nós. Nos 36 objetivos resolve todos, com 69 iterações em média em vez de 18,5.""",
    prune="""Técnica de poda da busca ordenada, com o **vetor de menor custo** (o menor custo real com que cada estado já apareceu na busca). Toda vez que um nó é gerado,

- se é a primeira vez que o estado aparece, ele entra no vetor com o seu custo;
- se o estado é repetido e o custo do nó novo é maior ou igual ao do vetor, poda o nó novo;
- se o custo é menor, atualiza o vetor, tira o nó antigo da árvore e de ABERTOS e inclui o novo.

Em P1 o terceiro caso acontece 1 vez; nos 36 objetivos, 45 vezes com `ascending` e 46 com `descending`. Um estado que já saiu de ABERTOS saiu pelo menor custo, então nenhum caminho novo até ele passa pelo vetor.""",
    pseudocode="""busca_ordenada(problema, estratégia, poda)
    ABERTOS = fila pelo custo com a raiz (custo 0)
    MENOR_CUSTO = {raiz: 0}
    FECHADOS = vazio
    enquanto ABERTOS não estiver vazia:
        nó = tira o de menor custo de ABERTOS (no empate, o mais antigo)
        se nó é o objetivo: SUCESSO
        coloca nó em FECHADOS
        para cada regra válida, na ordem da estratégia:
            se o filho já está no caminho da raiz até nó: não gera
            custo = custo(nó) + custo_real(regra, nó)
            se poda e custo >= MENOR_CUSTO[filho]:
                descarta a regra
            senão:
                se poda e o estado do filho está em ABERTOS: tira o nó antigo
                MENOR_CUSTO[estado do filho] = custo
                põe o filho em ABERTOS, na posição do custo
    FRACASSO""",
    code_note="""- **`_priority`**: o que ordena ABERTOS. Aqui, o custo real acumulado do nó. A busca gulosa reaproveita este laço e troca só o `_priority`.
- **`_best_cost`**: o vetor de menor custo, com o menor custo real já gerado até cada estado.
- **`_open`**: o nó de cada estado que está em ABERTOS, para poder tirá-lo de lá quando um caminho mais barato aparece.
- **`_closed`**: os estados de FECHADOS.
- **`_is_never_generated`**: o que vale com ou sem poda. Um nó não gera um estado do seu próprio caminho.
- **`_is_repetition`**: a técnica de poda. Descarta o filho que não barateia o custo guardado no vetor.
- **`_discard`**: registra como poda o nó que foi trocado.

O terceiro caso da poda está no laço: quando o filho chega mais barato a um estado ainda aberto, `frontier.remove` tira o nó antigo.""",
    path_strategy="ascending",
    path_note="R4, R1, R1: 3 movimentos, custo 13 + 12 + 11 = 36, o menor custo possível. As duas estratégias, com e sem poda, chegam a este mesmo caminho.",
    complexity=(
        (
            "Ordenada sem poda",
            "exponencial",
            "exponencial",
            "menor custo",
            "o mesmo estado entra em ABERTOS por todo caminho sem repetição mais barato que o objetivo",
        ),
        (
            "Ordenada com poda",
            "O((V + E) log V)",
            "O(V)",
            "menor custo",
            "cada estado é expandido uma vez; o heap custa log V por operação",
        ),
    ),
    compared_with=("breadth_first",),
    symbols=("b", "m", "V", "E"),
    conclusion="""## Conclusão

- Em P1: R4, R1, R1 (3 movimentos, custo 36) em 11 iterações e 18 nós gerados, com as duas ordens. É o caminho de menor custo e também o mais curto.
- Nos 36 objetivos resolve todos, sempre com o menor custo real: média de 51,33, contra 51,72 e 51,67 da largura. Com os 10 por jogada, o caminho mais barato é sempre um dos mais curtos: a média é de 4,14 movimentos, a mesma da largura.
- Garante o menor custo, mas não olha para o objetivo: como a largura, faz 18,5 iterações em média. A busca gulosa, a seguir, troca essa garantia por velocidade.""",
    flowchart="""digraph flow {
%(style)s
  root [label="raiz em ABERTOS", shape=oval, fillcolor="%(root)s"];
  pop [label="tira o de menor custo;\\nno empate, o gerado primeiro"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="%(goal)s"];
  visit [label="visita: regras aplicáveis na ordem da estratégia, menos as que levam\\na estado fechado ou já aberto por um caminho de custo igual ou menor"];
  apply [label="aplica todas; se um filho chega mais barato a um estado ainda aberto,\\no nó antigo sai de ABERTOS e da árvore"];
  root -> pop;
  pop -> goal;
  goal -> success [label="sim"];
  goal -> visit [label="não"];
  visit -> apply;
  apply -> pop;
}""",
    frontier_demo=True,
    rule_cells=COST_CELLS,
    goals_cells=GOALS_CELLS,
)


GREEDY_MARKED_COMPLEXITY: tuple[MarkedRow, ...] = (
    (
        "Gulosa sem poda",
        (
            ("exponencial", "worst"),
            ("exponencial", "worst"),
            ("sempre acha; não garante o menor custo", "worst"),
        ),
        "o mesmo estado volta a ABERTOS por todo caminho sem repetição",
    ),
    (
        "Gulosa com poda",
        (
            ("O((V + E) log V)", ""),
            ("O(V)", "best"),
            ("sempre acha; não garante o menor custo", "worst"),
        ),
        "cada estado é expandido uma vez; a fila custa log V",
    ),
    (
        "Ordenada com poda",
        (("O((V + E) log V)", ""), ("O(V)", "best"), ("menor custo real", "best")),
        "a mesma fila, ordenada pelo custo acumulado",
    ),
    (
        "Largura com poda",
        (("O(V + E)", "best"), ("O(V)", "best"), ("menos movimentos", "")),
        "cada estado entra uma vez, por níveis",
    ),
)

GREEDY_STEPS = (
    "A raiz é o estado atual e vai para FECHADOS. As quatro regras válidas geram quatro filhos, e cada um entra em ABERTOS na posição da sua heurística, entre parênteses. S2 e S3 empatam em 3: fica na frente o que foi gerado primeiro.",
    "S4 tem a menor heurística e vira o estado atual. R6 voltaria ao estado inicial, que já está em FECHADOS. R5 levaria a VRA/–/–, que já está em ABERTOS como S3 por um caminho mais barato. Sobra R1, que gera S5 com h = 1.",
    "S5 gera três filhos; R3 voltaria ao estado de S4 e é podada. S6 é o objetivo e entra na frente de ABERTOS com h = 0, mas a busca ainda não terminou: ele só encerra a busca quando virar o estado atual, na próxima iteração. ABERTOS chega ao seu maior tamanho, 6 nós.",
    "O objetivo vira o estado atual e a busca encerra: 4 iterações, 9 nós gerados. O caminho, em verde, é reconstruído do nó objetivo até a raiz: S6, S5, S4, S0. Somando o custo real das três arestas: o azul uma haste, 13; o vermelho uma haste, 12; o verde uma haste, 11. Total 36. Cinco nós ficaram em ABERTOS sem nunca ser expandidos.",
)


def _greedy_deck(spec: AlgorithmSection, index: int) -> tuple[Cell, ...]:
    """A seção da gulosa na ordem e com o texto dos slides: cada slide vira um
    título, o texto que o apresentador fala e a célula que desenha o slide."""
    name = spec.name
    steps = tuple(
        cell
        for number, text in enumerate(GREEDY_STEPS, start=1)
        for cell in (
            markdown(f"### Iteração {number} de {len(GREEDY_STEPS)}\n\n{text}"),
            code(f'tree_at("{name}", "ascending", {number})'),
        )
    )
    return (
        markdown(f"# {index}. {spec.title}\n\n{spec.subtitle}"),
        markdown(
            """## O problema: carta P1, do estado inicial ao objetivo

Três hastes, com capacidades 3, 2 e 1, e três discos: verde, vermelho e azul. Cada haste é escrita de baixo para cima: VR / A / – quer dizer verde embaixo e vermelho em cima na H1, azul na H2 e H3 vazia. A carta P1 pede – / RV / A."""
        ),
        code("show_problem()"),
        markdown(
            """## A ideia da busca gulosa

**Expanda sempre o nó aberto de menor heurística.**

A árvore abaixo é P1 depois da primeira iteração: a raiz S0 gera quatro filhos, um por regra válida, e cada um recebe a sua heurística h. Sai primeiro S4, com h = 2, o que parece mais perto do objetivo. S2 e S3 empatam em 3; fica na frente o gerado primeiro.

- **Ordenada:** fila pelo custo real, sai o nó mais barato de alcançar.
- **Gulosa:** fila pela heurística, sai o de menor h; no empate, o gerado primeiro.

A gulosa avalia o nó usando apenas a heurística, e isso não garante a melhor solução. A estrutura é a da busca ordenada: a mesma fila de ABERTOS, com outra chave de ordenação."""
        ),
        code(f'tree_at("{name}", "ascending", 1, highlight="next")'),
        markdown(
            """## Heurística

h = soma dos discos mal posicionados. Cada disco contribui com o mínimo de movimentos que ainda precisa fazer:

| Situação do disco | Contribui | Por quê |
|---|---|---|
| bem posicionado | 0 | haste e altura do objetivo, e tudo abaixo dele também: não precisa sair dali |
| em outra haste | 1 | pode chegar ao destino com um movimento |
| haste certa, lugar errado | 2 | precisa sair e voltar: o disco de baixo só sai depois que ele sair |

A heurística estima quanto falta do estado até o objetivo; é ela, e só ela, que ordena ABERTOS na gulosa. Estar na haste certa fora do lugar é pior que estar na haste errada. A admissibilidade foi conferida por força bruta: 36 estados vezes 36 objetivos, nenhuma violação. No código é um módulo de `core/heuristics/`, escolhido com `--heuristic`."""
        ),
        *_writefiles(HEURISTIC_MODULES),
        code("explain_heuristic()"),
        markdown(
            """## O laço e as duas listas

1. Tira de ABERTOS o nó de menor heurística; no empate, o gerado primeiro.
2. É o objetivo? **SUCESSO**. O custo da solução é a soma dos custos reais das arestas do caminho.
3. Não é: coloca o nó em FECHADOS.
4. Aplica todas as regras válidas, na ordem da estratégia, e calcula a heurística de cada filho.
5. Os filhos entram em ABERTOS na posição da sua heurística. Volta ao passo 1.

**ABERTOS**: gerados, ainda não analisados, em ordem de h. **FECHADOS**: já expandidos; com poda, um filho de estado fechado é descartado.

Exemplo: P1 depois da iteração 2. S0 e S4 já saíram de ABERTOS e foram expandidos (cinza). S1, S2, S3 e S5 esperam em ABERTOS (branco), e S5, com h = 1, é o próximo a sair (azul). É o laço da busca ordenada com uma troca: a fila é ordenada pela heurística, não pelo custo real. O objetivo só encerra a busca quando vira o estado atual, não quando é gerado."""
        ),
        code(f'tree_at("{name}", "ascending", 2, highlight="next")'),
        markdown(
            """## O custo real: custo = 10 + peso do disco × distância

| Por jogada | Peso do disco | Distância | R4 em VR/A/– |
|---|---|---|---|
| 10: toda jogada conta | 1 · 2 · 3: verde, vermelho, azul | 1 ou 2: 2 só entre H1 e H3 | 13 = 10 + 3 × 1: o azul |

A gulosa **não usa o custo para escolher**. Na árvore abaixo, a raiz de P1 com o custo de cada aresta: a ordenada tiraria primeiro S1, o filho mais barato (12); a gulosa tira S4, o de menor h, mesmo custando 13. O custo real só é somado nas arestas do caminho solução.

O peso × distância vai de 1 a 6, sempre menos que os 10 da jogada: o caminho de menor custo é sempre um dos de menos movimentos, e é por esse custo que a busca ordenada ordena ABERTOS. No código a função de custo é um módulo de `core/costs/`, escolhido com `--cost`. Trocar a função de custo não muda o caminho da gulosa, só o número que ela reporta como custo da solução."""
        ),
        code(f'tree_at("{name}", "ascending", 1, highlight="next", costs=True)'),
        markdown(
            """## As regras: seis regras, cada uma com seu custo real

Cada regra move o disco do topo de uma haste para outra, se a haste de destino tiver espaço. As últimas colunas dão o custo real da jogada conforme o disco que ela move. As regras e as inversas são as mesmas das outras buscas."""
        ),
        code("rules_table()"),
        markdown(
            """## Estratégia de controle: a ordem em que as regras são aplicadas

Na gulosa a estratégia é o critério de desempate: irmãos de mesma heurística entram em ABERTOS na ordem em que foram gerados. Em P1 ela só troca V/A/R e VRA/–/–, que empatam em h = 3; VR/–/A, o menor h, sai primeiro nas duas e o caminho não muda.

As duas árvores abaixo são a raiz de P1 expandida em cada ordem. Os filhos são os mesmos; muda a ordem em que são gerados, e por isso a numeração. O material pede um critério de desempate definido pelo usuário para nós de mesma heurística. Aqui são dois níveis: sai primeiro o nó gerado antes, e entre irmãos quem define a ordem de geração é a estratégia de controle."""
        ),
        code("strategies_table()"),
        markdown("### Ascending"),
        code(f'tree_at("{name}", "ascending", 1, highlight="next")'),
        markdown("### Descending"),
        code(f'tree_at("{name}", "descending", 1, highlight="next")'),
        markdown(
            """## Árvore com poda, passo a passo

P1, ordem crescente, com poda. Em azul, o nó que saiu de ABERTOS na iteração; em cinza, os nós em FECHADOS; em branco, os que esperam em ABERTOS; entre parênteses na linha de ABERTOS, a heurística."""
        ),
        *steps,
        markdown("### ABERTOS e FECHADOS, iteração a iteração"),
        code(f'lists_table(solve("{name}", "ascending"))'),
        markdown(
            f"""## Pseudocódigo da busca gulosa

```text
{spec.pseudocode}
```

A diferença para a busca ordenada está em três linhas: ABERTOS é uma fila pela heurística, sai o nó de menor h e o filho entra na posição de h(filho). A ordenada usa o custo real acumulado no lugar de h. Na poda, a gulosa soma o teste de FECHADOS. O custo real continua sendo calculado, para a poda e para o custo da solução."""
        ),
        markdown(f"**`{SOURCE_DIR}/{spec.module}`**: {spec.code_note}"),
        writefile_cell(find(f"{SOURCE_DIR}/{spec.module}")),
        markdown(
            """## Caminho solução: custo real 36

3 movimentos, custo real 13 + 12 + 11 = 36: o azul, o vermelho e o verde, cada um por uma haste. As duas estratégias, com e sem poda, chegam a este caminho.

O custo da solução é a soma do custo real das arestas do caminho, da raiz ao objetivo. Em P1 a gulosa acerta em cheio: 36 é também o menor custo possível, o mesmo que a busca ordenada encontra, e 3 é o mínimo de movimentos. Isso não é garantido, como mostra o caso a seguir."""
        ),
        code(f'show_path(solve("{name}", "ascending"))'),
        markdown(
            """## O caso dos 8 movimentos: a gulosa não garante a melhor solução

Objetivo G07, –/VA/R, a partir da posição inicial VR/A/–, ordem crescente, com poda. Aqui h é medida em relação a este objetivo.

A gulosa segue o ramo de R4 e, em 3 movimentos, monta R e V na H2 (h volta a 4). Para chegar ao objetivo ela desfaz a montagem: **R5 e R3** levam o azul e o verde para a H1 e liberam a H2. Paga 1 movimento e 12 de custo a mais que a ordenada: 8 movimentos e custo 99, contra 7 e 87.

É a mesma conclusão do exemplo das cidades no material: a gulosa chega, mas o custo real do caminho não é necessariamente o menor. Neste objetivo nenhum caminho baixa h a cada passo, e a gulosa se perde: primeiro segue VA/–/R, que tem h = 2 e parece perto, mas é um beco; depois atravessa um platô de nós com h = 4 e sai dele pelo ramo de R4. Nos 36 objetivos a gulosa acha o menor custo real em 31 com ascending e em 28 com descending; o custo médio é 52,33, contra 51,33 da ordenada."""
        ),
        code('compare_paths("G07", "ascending")'),
        markdown(
            """## Duas heurísticas, a mesma busca

A gulosa com cada heurística nos 36 objetivos, ordem crescente, com poda. Em verde, o melhor valor de cada linha.

**Discos mal posicionados:** 0, 1 ou 2 por disco, olhando a haste e a altura. É a heurística da apresentação. **Cor e distância:** peso do disco × hastes até a do objetivo. Só olha a haste: um disco na haste certa, fora de ordem, soma 0. Em P1 as duas heurísticas levam ao mesmo caminho, R4 R1 R1, em 4 iterações. A diferença aparece nos objetivos em que a ordem dentro da haste importa: a de cor e distância vale zero em estados que ainda não são o objetivo e a busca perde o rumo."""
        ),
        code("heuristics_table()"),
        markdown(
            """## Gulosa: ascending contra descending

Em P1 a estratégia não muda nada: o menor h é único a cada passo, então as duas ordens tiram os mesmos estados de ABERTOS. A poda só economiza um nó, o repetido VRA/–/–. Em verde, o melhor valor de cada linha. Nos 36 objetivos a poda pesa mais: 7,4 iterações em média com poda, 13,2 sem."""
        ),
        code(f'strategy_table("{name}")'),
        markdown(
            """## Os caminhos encontrados

Cada ponto é um movimento; o verde é o objetivo. Gulosa, ordenada e largura acham o mesmo caminho de 3 movimentos e custo real 36, com as duas estratégias. O backtracking acha o primeiro caminho que aparece: 14 movimentos na ordem crescente, 22 na decrescente."""
        ),
        code(f'paths_plot("{name}")'),
        markdown(
            """## Gulosa × Ordenada × Largura × Backtracking

P1, com poda. Em verde, o melhor valor de cada linha. A gulosa acha o mesmo caminho da ordenada e da largura com menos da metade das iterações. Pico de ABERTOS: nós em ABERTOS; no backtracking, o tamanho do caminho. A irrevogável faz o caminho de 14 movimentos do backtracking com a ordem crescente e termina em impasse com a decrescente."""
        ),
        code(f'algorithms_table("{name}")'),
        markdown(
            """## Quem explorou menos nós

Nós expandidos são os que saíram de ABERTOS e geraram filhos. A gulosa expande só os 3 nós do caminho, com ou sem poda: em P1 a heurística cai um ponto a cada passo, então ela não abre nenhum nó fora do caminho solução. A ordenada, que segue o custo, abre 10; a largura, de 11 a 13. Sem poda a largura dispara porque a regra inversa gera de volta o pai."""
        ),
        code(f'expanded_chart("{name}")'),
        markdown(
            """## Nós expandidos nos 36 objetivos

Cada caixa resume as 36 execuções de uma combinação: vai do primeiro ao terceiro quartil, a barra preta é a mediana, o losango é a média e as hastes vão do mínimo ao máximo sem contar os pontos fora da curva. A primeira linha, em verde, não é um algoritmo: para cada objetivo pega o melhor valor que alguma das oito combinações conseguiu e resume esses 36 melhores.

A gulosa expande em média 6,4 a 6,6 nós por objetivo e chega ao melhor em 24 objetivos (crescente) e 26 (decrescente); ordenada, largura e backtracking crescente ficam em 17,5. Na ordenada e na largura os valores são sempre 0, 1, …, 35: a ordem em que os estados saem de ABERTOS não depende do objetivo. O backtracking decrescente chega a 1.044 nós expandidos num objetivo, fora da escala."""
        ),
        code(f'best_boxplot("{name}", "expanded", limit=50)'),
        markdown(
            """## Iterações nos 36 objetivos

A gulosa faz 7,4 a 7,6 iterações em média, nunca passa de 19 e chega ao melhor de cada objetivo em 24 (crescente) e 26 (decrescente). Ordenada e largura fazem 18,5: com poda, cada estado sai de ABERTOS uma vez, numa ordem fixa, então as iterações são sempre 1, 2, …, 36, só embaralhadas. O backtracking decrescente tem média 82,9, fora da escala, puxada por dois objetivos que passam de cem iterações, um deles com 2.078; a mediana dele é 21,5."""
        ),
        code(f'best_boxplot("{name}", "iterations", limit=80)'),
        markdown(
            """## Custo real da solução: só P1

Em P1 a gulosa, a ordenada e a largura acham o mesmo caminho, R4 R1 R1, de custo 13 + 12 + 11 = 36. O backtracking chega com 14 e 22 movimentos e paga 5 e quase 8 vezes mais. Em P1 não dá para separar gulosa de ordenada pelo custo: as duas chegam ao ótimo. A diferença aparece nos 36 objetivos."""
        ),
        code(f'cost_chart("{name}")'),
        markdown(
            """## Custo real da solução: os 36 objetivos

Em verde, o menor custo de cada objetivo entre todas as combinações (média 51,33). Aqui a gulosa não lidera: a ordenada tem o menor custo real, porque é o que ela ordena, e acha esse melhor em todos os 36. A gulosa acha em 31 (crescente) e 28 (decrescente), 2% a 3% acima na média; a largura, em 33 e 30. É o preço da velocidade: a gulosa escolhe pelo que parece faltar, não pelo que já gastou. O backtracking paga de três a quatro vezes mais."""
        ),
        code(f'best_boxplot("{name}", "cost", limit=500)'),
        markdown(
            """## Menos esforço, quase o mesmo custo

Médias nos 36 objetivos, com poda. Em verde, o melhor de cada linha entre quem resolve todos; em vermelho, quem deixa objetivos sem solução. A gulosa resolve todos e fica perto do ótimo: custo médio 2% acima da ordenada. Largura e ordenada fazem sempre 18,5 iterações em média, porque a ordem em que tiram os nós de ABERTOS não depende do objetivo; a da gulosa depende, porque a heurística é medida em relação a ele."""
        ),
        code(f'goals_means_table("{name}")'),
        markdown(
            """## Complexidade

No pior caso a gulosa com poda custa o mesmo que a ordenada: as duas usam a mesma fila de prioridade e expandem cada estado no máximo uma vez. A diferença é prática: uma boa heurística faz a gulosa expandir muito menos estados antes de chegar ao objetivo. O preço é a garantia de menor custo, que só a ordenada tem."""
        ),
        code(f'marked_complexity("{name}")'),
        code(f'complexity_values("{name}", {spec.symbols!r})'),
        *_greedy_extras(spec),
    )


def _greedy_extras(spec: AlgorithmSection) -> tuple[Cell, ...]:
    name = spec.name
    return (
        markdown(
            f"## Extras de {spec.title.lower()}\n\nO que não está nos slides: a busca sem poda, o fluxograma, o trace e as tabelas completas."
        ),
        markdown(spec.conclusion.replace("## Conclusão", "### Resumo")),
        markdown(f"### Sem poda\n\n{spec.no_prune}"),
        code(f'sem_poda_crescente = case("{name}", "ascending", prune=False)'),
        code("lists_table(sem_poda_crescente)"),
        markdown("### Os objetivos em que a gulosa paga mais que a ordenada"),
        code("dearer_than_ordered()"),
        markdown("### Quanto cada disco soma em h"),
        code("heuristic_examples()"),
        markdown("### Quartis nos 36 objetivos"),
        code(f'goals_stats("{name}", "expanded")'),
        code(f'goals_stats("{name}", "iterations")'),
        code(f'goals_stats("{name}", "cost")'),
        *_extras(spec)[1:],
    )


GREEDY_SECTION = AlgorithmSection(
    title="Busca gulosa",
    name="greedy",
    label="Gulosa",
    color="#8e5bd6",
    list_mode="priority",
    complete=True,
    module="core/algorithms/greedy/algorithm.py",
    frontier="core/algorithms/ordered/frontier.py",
    frontier_class="PriorityFrontier",
    frontier_demo=True,
    goals_cells=GREEDY_GOALS_CELLS,
    subtitle="ABERTOS vira uma fila ordenada pela heurística: sai primeiro o nó que parece mais perto do objetivo.",
    idea="""**Expanda sempre o nó aberto de menor heurística.**

Ordenada: fila pelo custo real, sai o nó mais barato de alcançar.

Gulosa: fila pela heurística h, sai o nó que parece mais perto do objetivo; no empate, o gerado primeiro. O custo real não entra na escolha: ele só é somado nas arestas do caminho solução, para dar o custo da solução.

No código, a gulosa herda o laço e as duas listas da ordenada e troca só o método que dá a prioridade, `_priority`. A fila é a mesma `PriorityFrontier`.""",
    loop="""1. Tira de ABERTOS o nó de menor heurística; no empate, o gerado primeiro.
2. É o objetivo? **SUCESSO**: o custo da solução é a soma dos custos reais das arestas do caminho.
3. Não é: coloca o nó em FECHADOS.
4. Aplica todas as regras válidas, na ordem da estratégia, e calcula a heurística de cada filho.
5. Os filhos entram em ABERTOS na posição da sua heurística. Volta ao passo 1.

**ABERTOS**: fila dos nós gerados que ainda não foram analisados, ordenada pela heurística (entre parênteses na tabela).

**FECHADOS**: nós já expandidos. Com poda, um filho cujo estado já está aqui é descartado.""",
    strategy_note="Na gulosa a estratégia só desempata irmãos de mesma heurística: decide quem fica na frente em ABERTOS. Em P1 as duas ordens fazem as mesmas 4 iterações e acham o mesmo caminho.",
    root_note="Em S0 a heurística vale 3. Na raiz, R4 leva a h = 2, R2 e R3 a h = 3 e R1 a h = 4. R4 sai primeiro nas duas ordens; a estratégia só decide entre R2 e R3, que empatam. A ordenada, pelo custo, tiraria R1 primeiro.",
    no_prune="""Sem a técnica de poda, estados repetidos entram de novo em ABERTOS; como na ordenada, um nó só não gera um estado do seu próprio caminho. Em P1 a heurística leva direto ao objetivo: as mesmas 4 iterações, com 10 nós gerados em vez de 9. Nos 36 objetivos resolve todos, mas a mesma heurística volta a atrair a busca para estados já expandidos: 13,2 e 13,8 iterações em média, contra 7,44 e 7,61 com poda.""",
    prune="""A poda é a técnica da busca ordenada, com o **vetor de menor custo** (o menor custo real com que cada estado já apareceu). Toda vez que um nó é gerado,

- se é a primeira vez que o estado aparece, ele entra no vetor com o seu custo;
- se o estado é repetido e o custo do nó novo é maior ou igual ao do vetor, poda o nó novo;
- se o custo é menor, atualiza o vetor, tira o nó antigo da árvore e de ABERTOS e inclui o novo.

Dois nós do mesmo estado têm a mesma heurística, então quem decide entre eles é o custo real. Há um acréscimo em relação à ordenada: aqui a fila não sai por custo, então um estado já expandido pode reaparecer mais barato. Ele não é reaberto: o filho cujo estado está em FECHADOS também é podado. Em P1 o terceiro caso não acontece; nos 36 objetivos ele aparece 3 vezes com `ascending` e 5 com `descending`.""",
    pseudocode="""busca_gulosa(problema, estratégia, poda)
    ABERTOS = fila pela heurística com a raiz
    MENOR_CUSTO = {raiz: 0}
    FECHADOS = vazio
    enquanto ABERTOS não estiver vazia:
        nó = tira o de menor h de ABERTOS (no empate, o mais antigo)
        se nó é o objetivo: SUCESSO
        coloca nó em FECHADOS
        para cada regra válida, na ordem da estratégia:
            se o filho já está no caminho da raiz até nó: não gera
            custo = custo(nó) + custo_real(regra, nó)
            se poda e (filho está em FECHADOS ou custo >= MENOR_CUSTO[filho]):
                descarta a regra
            senão:
                se poda e o estado do filho está em ABERTOS: tira o nó antigo
                MENOR_CUSTO[estado do filho] = custo
                põe o filho em ABERTOS, na posição de h(filho)
    FRACASSO""",
    code_note="""A classe herda o laço da ordenada e troca o `_priority`: ele devolve a heurística do nó em vez do custo acumulado. O `_is_repetition` soma à poda da ordenada o filho de estado já fechado. A heurística chega pelo motor (`self._heuristic`), escolhida no registro de `core/heuristics/`.""",
    uses_heuristic=True,
    rule_cells=HEURISTIC_CELLS,
    path_strategy="ascending",
    path_note="R4, R1, R1: 3 movimentos, custo real 13 + 12 + 11 = 36. Em P1 é também o caminho de menor custo, o mesmo da ordenada, achado em 4 iterações em vez de 11.",
    complexity=(
        (
            "Gulosa sem poda",
            "exponencial",
            "exponencial",
            "não garante a de menor custo",
            "o mesmo estado entra em ABERTOS por todo caminho sem repetição",
        ),
        (
            "Gulosa com poda",
            "O((V + E) log V)",
            "O(V)",
            "não garante a de menor custo",
            "cada estado é expandido uma vez; o heap custa log V por operação",
        ),
    ),
    compared_with=("ordered", "breadth_first"),
    marked_complexity=GREEDY_MARKED_COMPLEXITY,
    deck=_greedy_deck,
    symbols=("b", "m", "V", "E"),
    conclusion="""## Conclusão

- Em P1: R4, R1, R1 (3 movimentos, custo 36) em 4 iterações e 9 nós gerados, com as duas ordens. A ordenada precisa de 11 iterações e a largura de 12 a 14.
- Nos 36 objetivos resolve todos, com 7,44 e 7,61 iterações em média, contra 18,5 da ordenada e da largura.
- Não garante a melhor solução: o custo médio é 52,33 e 53,00, contra 51,33 da ordenada, e ela acha o menor custo em 31 (`ascending`) e 28 (`descending`) dos 36 objetivos. A busca segue o nó que parece mais perto do objetivo, não o que custou menos.""",
    flowchart="""digraph flow {
%(style)s
  root [label="raiz em ABERTOS", shape=oval, fillcolor="%(root)s"];
  pop [label="tira o de menor heurística;\\nno empate, o gerado primeiro"];
  goal [label="é o objetivo?", shape=diamond];
  success [label="SUCESSO", shape=oval, fillcolor="%(goal)s"];
  visit [label="visita: regras aplicáveis na ordem da estratégia, menos as que levam\\na estado fechado ou já aberto por um caminho de custo igual ou menor"];
  apply [label="aplica todas; se um filho chega mais barato a um estado ainda aberto,\\no nó antigo sai de ABERTOS e da árvore"];
  root -> pop;
  pop -> goal;
  goal -> success [label="sim"];
  goal -> visit [label="não"];
  visit -> apply;
  apply -> pop;
}""",
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
        *COST_MODULES,
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
    if spec.deck is not None:
        return spec.deck(spec, index)
    cells: list[Cell] = [
        markdown(f"# {index}. {spec.title}\n\n{spec.subtitle}"),
        markdown(
            "## O problema: carta P1, do estado inicial ao objetivo\n\n"
            "Cada estado lista as hastes da base para o topo. As seis regras R1 a R6 movem o disco do topo de uma haste para outra."
        ),
    ]
    if first:
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
        cells.extend(_writefiles(ENGINE_MODULES))

    cells.append(
        markdown(
            "## As regras: seis regras, uma para cada par origem e destino\n\n"
            "Vale se a origem tem disco e o destino tem espaço. O custo real de cada jogada vem da função de custo (`core/costs/`). Toda regra tem inversa: aplicar as duas em seguida volta ao mesmo estado."
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
                f"## Pseudocódigo\n\n```text\n{spec.pseudocode}\n```\n\n{PRUNE_FLAG}"
            ),
            markdown(f"**`{SOURCE_DIR}/{spec.module}`**: {spec.code_note}"),
            writefile_cell(find(f"{SOURCE_DIR}/{spec.module}")),
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
