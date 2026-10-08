"""FRONTEIRA — a lista de ABERTOS.

Os nós já gerados que ainda não foram processados. A busca tira um daqui,
olha em volta e devolve os filhos. Fronteira vazia, busca encerrada.

Quem sai primeiro define o algoritmo: pilha afunda, fila varre por nível,
fila de prioridade sai pelo menor custo.

Aqui fica só o contrato. Cada implementação mora ao lado do algoritmo que a
usa: core/algorithms/<algoritmo>/frontier.py.
"""

from __future__ import annotations

from typing import Protocol

from core.search_tree.node import Node


class EmptyFrontierError(Exception):
    """Tentou tirar um nó de uma fronteira vazia."""

    def __init__(self) -> None:
        super().__init__("cannot pop from an empty frontier")


class Frontier(Protocol):
    """Guardar um nó, tirar um nó, contar quantos faltam. Só isso.

    Sem índice, sem busca por estado, sem percorrer o conteúdo: o único
    acesso é pela ponta. O contrato não diz QUAL nó o pop devolve — é a
    única coisa que muda entre as implementações, e é o que define a busca.
    """

    def push(self, node: Node) -> None:
        """Guarda um nó. Ele sempre entra pelo fim."""
        ...

    def pop(self) -> Node:
        """Tira um nó e devolve. QUAL nó é o que muda entre as fronteiras."""
        ...

    def __len__(self) -> int:
        """Quantos nós ainda esperam. Zero encerra a busca."""
        ...
