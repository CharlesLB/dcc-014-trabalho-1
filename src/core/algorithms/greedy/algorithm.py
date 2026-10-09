"""BUSCA GULOSA

1. Estado inicial e objetivo (carta P1)

    S0 = ([V, R], [A], [])          Sf = ([], [R, V], [A])

2. Heurística: a mesma da busca ordenada (core/domain/heuristic.py)

    0 por disco bem posicionado, 1 em outra haste, 2 na haste certa mas mal
    posicionado. h(estado) = soma dos três discos.

3. Critério

    A mesma descida da busca irrevogável, mas a regra aplicada é a que leva
    ao filho de MENOR heurística, não a primeira da estratégia. A estratégia
    só desempata filhos de mesma heurística. Não guarda as outras: cada
    passo é definitivo e não há retorno. Uma regra que leva a um estado já
    percorrido é descartada (poda).
"""

from __future__ import annotations

from typing import ClassVar

from core.algorithms.irrevocable.algorithm import IrrevocableSearch
from core.domain.heuristic import misplacement
from core.domain.problem import Problem
from core.rules.domain.base import TransitionRule
from core.search_tree.node import Node


class GreedySearch(IrrevocableSearch):
    name: ClassVar[str] = "greedy"

    def _choose(
        self, node: Node, candidates: tuple[TransitionRule, ...], problem: Problem
    ) -> TransitionRule:
        """O filho de menor heurística; sem voltar atrás, como na irrevogável.

        A estratégia só desempata filhos de mesma heurística: `min` fica com
        o primeiro deles na ordem dela.
        """
        return min(
            candidates,
            key=lambda rule: misplacement(rule.apply(node.state), problem.goal),
        )
