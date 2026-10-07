from __future__ import annotations

from dataclasses import dataclass

from cells import Cell, Notebook, code, markdown
from pages.common import (
    BACKTRACKING,
    BREADTH_FIRST,
    IRREVOCABLE,
    ORDERED,
    VIEW_HELPERS,
    Page,
    header,
    setup_note,
)
from source import SOURCE_DIR, all_files, install_cell, writefile_cell


@dataclass(frozen=True, slots=True)
class AlgorithmPage:
    page: Page
    name: str
    module: str
    intro: str
    flowchart: str
    code_note: str
    trace_strategy: str
    path_strategy: str
    conclusion: str


FLOW_STYLE = """  rankdir=TB; fontname="Helvetica"; bgcolor="transparent";
  node [fontname="Helvetica", fontsize=11, shape=box, style="rounded,filled", fillcolor="#ffffff", color="#333333"];
  edge [fontname="Helvetica", fontsize=10, color="#333333"];"""

IRREVOCABLE_PAGE = AlgorithmPage(
    page=IRREVOCABLE,
    name="irrevocable",
    module="core/algorithms/irrevocable.py",
    intro="""Um caminho só. A regra preferida da estratégia é aplicada e as outras são esquecidas: cada passo é definitivo e não há retorno. Uma regra que levaria a um estado já percorrido é podada.

Sempre para, no máximo depois dos 36 estados, porque nunca repete estado no caminho. Parar não é chegar: é o único método em que a estratégia muda o desfecho.""",
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
    code_note="O laço inteiro cabe em poucas linhas: testa o objetivo, visita, pega as regras permitidas e aplica a primeira. Sem regra, é impasse e a busca acaba. O docstring do módulo traz a execução de P1 resolvida à mão, com a ordem decrescente.",
    trace_strategy="descending",
    path_strategy="ascending",
    conclusion="""## Conclusão

- Em P1, `descending` trava na 3ª iteração: R4 e R5 levam a `H1[V,R,A]`, e de lá as duas regras aplicáveis voltam a estados do caminho. `custom` também termina em impasse.
- `ascending` chega, mas com 14 movimentos, quando o ótimo tem 3.
- A busca é barata (no máximo um nó gerado por iteração), mas não garante solução nem qualidade. A estratégia decide tudo.""",
)

BACKTRACKING_PAGE = AlgorithmPage(
    page=BACKTRACKING,
    name="backtracking",
    module="core/algorithms/backtracking.py",
    intro="""A mesma descida da busca irrevogável, com as alternativas de cada vértice guardadas numa pilha. Travou, volta ao ancestral mais próximo que ainda tem alternativa.

Impasse vira desvio e a solução sempre aparece, porque todo estado alcança todo estado. Mas é a primeira encontrada, não a mais curta.""",
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
    code_note="A fronteira é uma `StackFrontier`: o topo da pilha é a ponta do caminho. `untried` guarda, para cada nó do caminho, as regras que ele ainda não tentou; é o que permite voltar e continuar de onde parou. O docstring traz a execução de P1 com a ordem decrescente.",
    trace_strategy="descending",
    path_strategy="descending",
    conclusion="""## Conclusão

- Em P1 as três estratégias chegam ao objetivo. Com `descending` são 51 iterações, 14 retrocessos e 22 movimentos para um ótimo de 3.
- Com `ascending` não há retrocesso: o caminho é o mesmo da busca irrevogável, com 14 movimentos.
- O backtracking resolve o problema da irrevogável (o impasse não encerra a busca), mas a busca para no primeiro objetivo que encontra, tenha o caminho o comprimento que tiver.""",
)

BREADTH_FIRST_PAGE = AlgorithmPage(
    page=BREADTH_FIRST,
    name="breadth_first",
    module="core/algorithms/breadth_first.py",
    intro="""Não escolhe regra: aplica todas, os filhos esperam numa fila e a árvore é varrida por níveis.

Nada de profundidade d+1 é visitado antes de esgotar a profundidade d, então o primeiro caminho até um estado é o mais curto até ele. O objetivo encontrado é o ótimo em número de movimentos.""",
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
    code_note="A fronteira é uma `QueueFrontier`. A poda é global: `_is_repetition` é sobrescrita para descartar qualquer estado que já esteja em ABERTOS ou FECHADOS, não só os do caminho. O docstring traz a expansão de P1 nível por nível.",
    trace_strategy="ascending",
    path_strategy="ascending",
    conclusion="""## Conclusão

- Em P1 as três estratégias acham R4, R1, R1: 3 movimentos, o ótimo. A estratégia só muda a ordem dentro de um nível e, com ela, quantas iterações a busca leva.
- O preço é a memória: a fila guarda o nível inteiro, e a busca gera mais nós que a irrevogável e o backtracking com `ascending`.
- Por achar o caminho mais curto, este método é a referência de comprimento para os outros. Em custo, a referência é a busca ordenada.""",
)

ORDERED_PAGE = AlgorithmPage(
    page=ORDERED,
    name="ordered",
    module="core/algorithms/ordered.py",
    intro="""Cada regra tem um custo, a distância entre as hastes que ela liga: R1, R3, R4 e R6 custam 1; R2 e R5, que pulam a haste do meio, custam 2. ABERTOS vira uma fila ordenada pelo custo acumulado desde a raiz.

O objetivo só encerra a busca quando vira o estado atual, não quando é gerado. Por isso a solução é a de menor custo, que nem sempre é a de menos movimentos.""",
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
    code_note="A fronteira é uma `PriorityFrontier`, um heap por (custo, ordem de geração). `_best_cost` é o vetor de menor custo: cobre ABERTOS e FECHADOS de uma vez. Quando um caminho mais barato até um estado ainda aberto aparece, o nó antigo é removido. O docstring traz a execução de P1 com as listas ABERTOS e FECHADOS.",
    trace_strategy="ascending",
    path_strategy="ascending",
    conclusion="""## Conclusão

- Em P1: R4, R1, R1, custo 3. Com `ascending` são 10 iterações; com `descending` e `custom`, o mesmo caminho em 11.
- Com custo unitário, a busca ordenada seria a busca em largura. Aqui as duas acham o mesmo caminho em P1, mas a ordenada deixa para depois os ramos que começam por R2, que custa 2.
- A estratégia só desempata irmãos de mesmo custo: nunca muda o custo da solução.""",
)

ALGORITHM_PAGES: tuple[AlgorithmPage, ...] = (
    IRREVOCABLE_PAGE,
    BACKTRACKING_PAGE,
    BREADTH_FIRST_PAGE,
    ORDERED_PAGE,
)


def build(spec: AlgorithmPage) -> Notebook:
    own_path = f"{SOURCE_DIR}/{spec.module}"
    others = tuple(item for item in all_files() if item.path != own_path)
    own = next(item for item in all_files() if item.path == own_path)
    cells: tuple[Cell, ...] = (
        header(spec.page, spec.intro),
        setup_note(own_module=own_path),
        install_cell("Grava o código do projeto", others),
        VIEW_HELPERS,
        markdown("## Fluxograma"),
        code(
            f"""#@title Desenha o fluxograma
FLOW = '''{spec.flowchart % FLOW_STYLE}'''
if shutil.which("dot"):
    display(SVG(subprocess.run(["dot", "-Tsvg"], input=FLOW, capture_output=True, text=True, check=True).stdout))
else:
    print(FLOW)""",
            hidden=True,
        ),
        markdown(f"## O código\n\n{spec.code_note}"),
        writefile_cell(own),
        markdown(
            """## Execução em P1

Uma execução por estratégia de controle, sobre a carta P1. O motor conta as métricas; a tabela só as organiza."""
        ),
        code(
            f"""from core.algorithms.domain.registry import get_algorithm
from core.domain.problem import get_problem
from core.rules.strategies.domain.registry import STRATEGIES
from core.search_tree.tree import SearchTree

problem = get_problem("P1")
Algorithm = get_algorithm("{spec.name}")
results = {{
    name: Algorithm(SearchTree(), strategy).solve(problem)
    for name, strategy in STRATEGIES.items()
}}
metrics_table(results.values())"""
        ),
        markdown(
            f"""## Passo a passo

O trace da execução com a estratégia `{spec.trace_strategy}`: cada evento do motor (visita, gera, poda, impasse, retrocesso, objetivo), com a iteração, o nó, a profundidade, a regra e o estado. Legenda dos discos: V verde, R vermelho, A azul."""
        ),
        code(f'show_trace(results["{spec.trace_strategy}"])'),
        markdown(
            """## Árvores de busca

Uma árvore por estratégia. O caminho solução está em azul, o objetivo em verde, os impasses em vermelho, os nós gerados e não visitados em cinza e as regras podadas em pontilhado."""
        ),
        code(
            """for result in results.values():
    show_tree(result)"""
        ),
        markdown(
            f"""## Caminho solução

O caminho da execução com a estratégia `{spec.path_strategy}`, estado por estado."""
        ),
        code(f'show_path(results["{spec.path_strategy}"])'),
        markdown(
            """## Experimente

Troque a ordem das regras ou a carta e rode de novo. `all_goal_problems()` traz os 36 objetivos possíveis (G01 a G36)."""
        ),
        code(
            """from core.domain.problem import all_goal_problems
from core.rules.strategies.custom_order import CustomOrderStrategy

order = ("R1", "R4", "R2", "R6", "R3", "R5")
target = all_goal_problems()[20]
result = Algorithm(SearchTree(), CustomOrderStrategy(sequence=order)).solve(target)
print(target.id, state_render.render_inline(target.goal))
print(theme.outcome_label(result.outcome), " → ".join(result.applied_rules) or theme.ABSENT)
show_tree(result)"""
        ),
        markdown(spec.conclusion),
    )
    return Notebook(spec.page.filename, spec.page.title, cells)
