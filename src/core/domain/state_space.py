"""Enumeração exaustiva do espaço de estados.

Não participa de busca alguma: descreve o espaço por força bruta e serve de
oráculo independente aos testes.

Contagem:
    3! = 6 permutações x 10 cortes em três partes = 60 disposições
    as capacidades (3, 2, 1) deixam 6 distribuições:
        (3,0,0)  (2,1,0)  (2,0,1)  (1,2,0)  (1,1,1)  (0,2,1)
    6 distribuições x 6 arranjos = 36 estados válidos

Propriedades:
    - Grafo não dirigido: toda regra tem inversa exata.
    - Grafo conexo: todo objetivo é alcançável de qualquer inicial. Logo
      backtracking e largura sempre terminam em SUCESSO neste problema; só a
      busca irrevogável pode terminar em IMPASSE.
    - Fator de ramificação: 2 a 4 regras aplicáveis por estado.
    - Profundidade máxima de um caminho sem repetição: 36.

`shortest_distance` é uma busca em largura escrita à parte do motor, sem árvore,
nó ou estratégia. É o oráculo contra o qual a otimalidade de `breadth_first` é
verificada.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from itertools import permutations

from core.domain.state import Disk, State, is_valid
from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULES


def all_states() -> tuple[State, ...]:
    return tuple(_generate_states())


def _generate_states() -> Iterator[State]:
    disks = tuple(Disk)
    for arrangement in permutations(disks):
        for first in range(len(disks) + 1):
            for second in range(first, len(disks) + 1):
                candidate: State = (
                    arrangement[:first],
                    arrangement[first:second],
                    arrangement[second:],
                )
                if is_valid(candidate):
                    yield candidate


def applicable_rules(state: State) -> tuple[TransitionRule, ...]:
    return tuple(rule for rule in RULES if rule.is_applicable(state))


def successors(state: State) -> tuple[tuple[TransitionRule, State], ...]:
    return tuple((rule, rule.apply(state)) for rule in applicable_rules(state))


def reachable_from(source: State) -> frozenset[State]:
    seen = {source}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for _, successor in successors(current):
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return frozenset(seen)


def shortest_distance(source: State, target: State) -> int | None:
    if source == target:
        return 0
    depths = {source: 0}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for _, successor in successors(current):
            if successor in depths:
                continue
            depths[successor] = depths[current] + 1
            if successor == target:
                return depths[successor]
            queue.append(successor)
    return None
