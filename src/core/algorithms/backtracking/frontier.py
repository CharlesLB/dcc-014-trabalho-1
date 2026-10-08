"""FRONTEIRA DO BACKTRACKING — pilha.

O contrato (push, pop, len) está em core/search_tree/frontier.py.
"""

from __future__ import annotations

from core.search_tree.frontier import EmptyFrontierError
from core.search_tree.node import Node


class StackFrontier:
    """PILHA (LIFO): sai o último que entrou. Usada pelo backtracking.

    ```
    push S1, S2, S3  ->  [S1 S2 S3]  ->  pop devolve S3
    ```

    Entra e sai pelo mesmo lado, então o filho recém-gerado é sempre o
    próximo a ser olhado: a busca afunda num ramo até o fim.
    """

    __slots__ = ("_nodes",)

    def __init__(self) -> None:
        self._nodes: list[Node] = []

    def push(self, node: Node) -> None:
        """Empilha o nó no topo."""
        self._nodes.append(node)

    def pop(self) -> Node:
        """Tira e devolve o nó do topo: o ÚLTIMO que entrou."""
        if not self._nodes:
            raise EmptyFrontierError
        return self._nodes.pop()

    def __len__(self) -> int:
        """Quantos nós estão empilhados."""
        return len(self._nodes)
