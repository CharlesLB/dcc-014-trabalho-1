"""FRONTEIRA DA BUSCA EM LARGURA — fila.

O contrato (push, pop, len) está em core/search_tree/frontier.py.
"""

from __future__ import annotations

from collections import deque

from core.search_tree.frontier import EmptyFrontierError
from core.search_tree.node import Node


class QueueFrontier:
    """FILA (FIFO): sai o primeiro que entrou. Usada pela busca em largura.

    ```
    push S1, S2, S3  ->  [S1 S2 S3]  ->  pop devolve S1
    ```

    Entra por um lado, sai pelo outro, então os filhos esperam atrás de todo
    o nível atual: a busca varre nível por nível e acha o caminho mais curto.

    Usa deque, não list, porque popleft é O(1) e list.pop(0) é O(n).
    """

    __slots__ = ("_nodes",)

    def __init__(self) -> None:
        self._nodes: deque[Node] = deque()

    def push(self, node: Node) -> None:
        """Enfileira o nó no fim da fila."""
        self._nodes.append(node)

    def pop(self) -> Node:
        """Tira e devolve o nó do início: o PRIMEIRO que entrou.

        É a única linha que difere da StackFrontier, e é ela que troca
        profundidade por largura.
        """
        if not self._nodes:
            raise EmptyFrontierError
        return self._nodes.popleft()

    def __len__(self) -> int:
        """Quantos nós estão na fila."""
        return len(self._nodes)
