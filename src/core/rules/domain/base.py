"""Legenda do problema.

Discos: VERDE, VERMELHO, AZUL. Distintos por cor; NÃO há ordenação por tamanho.
Hastes: H1, H2, H3.

Pesos, usados só no custo das regras (busca ordenada):
    VERDE: 1    VERMELHO: 2    AZUL: 3

Capacidades:
    H1: até 3 discos
    H2: até 2 discos
    H3: até 1 disco

A capacidade é a única restrição estrutural: é o que substitui a ordenação por
tamanho da Torre de Hanói.

Estado: tupla de três pilhas, cada uma da base para o topo. Imutável, hashable e
canônica: uma configuração física tem exatamente uma escrita.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import IntEnum, unique
from types import MappingProxyType
from typing import Protocol


@unique
class Disk(IntEnum):
    GREEN = 0
    RED = 1
    BLUE = 2


@unique
class Peg(IntEnum):
    H1 = 0
    H2 = 1
    H3 = 2


CAPACITIES: Mapping[Peg, int] = MappingProxyType({Peg.H1: 3, Peg.H2: 2, Peg.H3: 1})

DISK_WEIGHTS: Mapping[Disk, int] = MappingProxyType(
    {Disk.GREEN: 1, Disk.RED: 2, Disk.BLUE: 3}
)

TOTAL_DISKS: int = len(Disk)

type Stack = tuple[Disk, ...]
type State = tuple[Stack, Stack, Stack]


class TransitionRule(Protocol):
    """Um movimento: tira o disco do topo de uma haste e põe no topo de outra.

        is_applicable(estado)  ->  posso mover agora? (origem tem disco e
                                   destino tem espaço)
        apply(estado)          ->  o estado que resulta do movimento
        distance               ->  quantas hastes o disco atravessa (1 ou 2)
        cost(estado)           ->  quanto custa mover agora (só a busca
                                   ordenada usa; depende do disco movido)

    `apply` não mexe no estado recebido, devolve um novo -- por isso um nó da
    árvore nunca perde a configuração que guardava. São seis regras fixas, R1
    a R6, uma por par origem/destino, definidas em `moves.py`.

    A busca não sabe o que é disco nem haste: ela só testa a regra, aplica a
    que passou, e segue. Trocar o problema é trocar as regras, não o motor.
    """

    @property
    def id(self) -> str: ...

    @property
    def origin(self) -> Peg: ...

    @property
    def destination(self) -> Peg: ...

    @property
    def distance(self) -> int: ...

    def cost(self, state: State) -> int: ...

    def is_applicable(self, state: State) -> bool: ...

    def apply(self, state: State) -> State: ...
