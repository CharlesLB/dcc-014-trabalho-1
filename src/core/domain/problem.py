"""Estado inicial e catálogo de cartas.

Inicial, fixo pelo aparato:  H1[VERDE, VERMELHO]  H2[AZUL]  H3[]
Cada carta define um objetivo a alcançar a partir dele.

`Problem` valida inicial e objetivo na construção: carta impossível falha na
importação do módulo, não no meio de uma busca. O campo `initial` tem padrão para
que testes montem cenários sintéticos sem tocar no catálogo.

Único ponto a alterar quando o conjunto de cartas muda: os testes usam
propriedades relativas, nunca o literal do objetivo.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from core.domain.state import State, build_state, validate
from core.rules.domain.base import Disk

GREEN = Disk.GREEN
RED = Disk.RED
BLUE = Disk.BLUE


class UnknownProblemError(Exception):
    def __init__(self, problem_id: str) -> None:
        super().__init__(f"unknown problem identifier: {problem_id!r}")
        self.problem_id = problem_id


INITIAL_STATE: State = build_state((GREEN, RED), (BLUE,), ())


@dataclass(frozen=True, slots=True)
class Problem:
    id: str
    goal: State
    initial: State = INITIAL_STATE

    def __post_init__(self) -> None:
        validate(self.goal)
        validate(self.initial)

    def is_goal(self, state: State) -> bool:
        return state == self.goal


PROBLEMS: tuple[Problem, ...] = (Problem("P1", build_state((), (RED, GREEN), (BLUE,))),)

PROBLEM_BY_ID: Mapping[str, Problem] = MappingProxyType(
    {problem.id: problem for problem in PROBLEMS}
)

PROBLEM_IDS: tuple[str, ...] = tuple(PROBLEM_BY_ID)


def get_problem(problem_id: str) -> Problem:
    try:
        return PROBLEM_BY_ID[problem_id]
    except KeyError:
        raise UnknownProblemError(problem_id) from None
