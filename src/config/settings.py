from __future__ import annotations

from collections.abc import Mapping
from typing import Final

MAX_ITERATIONS: Final = 10_000

DEFAULT_OUTPUT_FORMAT: Final = "console"
DEFAULT_RANK_MODE: Final = "lexicographic"

OUTPUT_FORMATS: Final[tuple[str, ...]] = ("console", "json")
RANK_MODES: Final[tuple[str, ...]] = ("lexicographic", "score")

EXIT_OK: Final = 0
EXIT_INVALID_INPUT: Final = 2


PROGRAM_NAME: Final = "main.py"

DESCRIPTION: Final = (
    "Resolvedor da Torre de Londres: executa busca irrevogável, backtracking e "
    "busca em largura sobre as cartas do problema, variando a estratégia de "
    "controle, e ranqueia os resultados."
)

EPILOG: Final = (
    'Cada eixo omitido significa "todos": sem --problem roda todas as cartas, '
    "sem --algorithm roda todos os algoritmos, sem --strategy roda todas as "
    "estratégias."
)

HELP_HELP: Final = "Mostra esta ajuda e encerra."
HELP_PROBLEM: Final = "Cartas a resolver (repetível ou separado por vírgula)."
HELP_ALGORITHM: Final = "Algoritmos a executar (repetível ou separado por vírgula)."
HELP_STRATEGY: Final = "Estratégias de controle (repetível ou separado por vírgula)."
HELP_ALL: Final = (
    "Produto cartesiano completo: todas as cartas, algoritmos e estratégias."
)
HELP_ORDER: Final = "Ordem das regras para a estratégia custom, ex.: R2,R4,R6,R1,R3,R5."
HELP_SHOW_TREE: Final = "Renderiza a árvore de busca de cada execução."
HELP_SHOW_TRACE: Final = (
    "Mostra o passo a passo com regra aplicada e estado resultante."
)
HELP_SHOW_STATES: Final = "Desenha as hastes em cada estado do caminho solução."
HELP_FORMAT: Final = "Formato da saída."
HELP_OUTPUT: Final = "Arquivo de destino da saída; sem ele, escreve no terminal."
HELP_SVG_DIR: Final = (
    "Pasta onde gravar a árvore de busca de cada execução em DOT e SVG "
    "(o SVG exige o Graphviz instalado)."
)
HELP_RANK_MODE: Final = "Critério do placar."
HELP_MAX_ITERATIONS: Final = "Guarda contra execução patológica."
HELP_SEED: Final = "Reservado; a execução é determinística por construção."
HELP_LIST: Final = "Lista cartas, algoritmos e estratégias disponíveis e encerra."
HELP_VERBOSE: Final = "Habilita log de diagnóstico na saída de erro."

KIND_LABELS: Final[Mapping[str, str]] = {
    "problem": "Carta não reconhecida",
    "algorithm": "Algoritmo não reconhecido",
    "strategy": "Estratégia não reconhecida",
    "format": "Formato de saída não reconhecido",
    "rank_mode": "Modo de ranqueamento não reconhecido",
}

ERROR_PREFIX: Final = "Erro:"
ERROR_UNKNOWN_SELECTION: Final = "{kind}: {name}. Disponíveis: {available}."
ERROR_INVALID_ARGUMENT: Final = "argumento inválido: {detail}."
ERROR_INVALID_RULE_ORDER: Final = "ordem de regras inválida: {reason}."
ERROR_HINT: Final = "Use --help para ver as opções."

USAGE_PREFIX: Final = "Uso: "
OPTIONS_TITLE: Final = "Opções"

LIST_PROBLEMS_HEADER: Final = "Cartas disponíveis"
LIST_ALGORITHMS_HEADER: Final = "Algoritmos disponíveis"
LIST_STRATEGIES_HEADER: Final = "Estratégias disponíveis"
OUTPUT_WRITTEN: Final = "Saída gravada em {path}"
GRAPHS_WRITTEN: Final = "{count} arquivos de árvore gravados em {path}"
GRAPHVIZ_MISSING: Final = (
    "Aviso: Graphviz (dot) não encontrado; só os arquivos .dot foram gravados."
)
