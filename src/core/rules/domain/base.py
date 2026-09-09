"""Legenda do problema.

Discos: VERDE, VERMELHO, AZUL. Distintos por cor; NÃO há ordenação por tamanho.
Hastes: H1, H2, H3.

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

TOTAL_DISKS: int = len(Disk)

type Stack = tuple[Disk, ...]
type State = tuple[Stack, Stack, Stack]


class TransitionRule(Protocol):
    @property
    def id(self) -> str: ...

    @property
    def origin(self) -> Peg: ...

    @property
    def destination(self) -> Peg: ...

    def is_applicable(self, state: State) -> bool: ...

    def apply(self, state: State) -> State: ...
