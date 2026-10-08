"""FRONTEIRA DA BUSCA ORDENADA — fila de prioridade por custo.

O contrato (push, pop, len) está em core/search_tree/frontier.py.
"""

from __future__ import annotations

import heapq

from core.search_tree.frontier import EmptyFrontierError
from core.search_tree.node import Node


class PriorityFrontier:
    """FILA ORDENADA POR CUSTO: sai o de menor custo acumulado. Usada pela
    busca ordenada.

    ```
    push S1(5), S2(6), S3(6), S4(1)  ->  pop devolve S4, S1, S2, S3
    ```

    Empate de custo sai o gerado primeiro (menor `order`). Irmãos de mesmo
    custo nascem na ordem da estratégia, então ela é o desempate entre eles.

    Heap de (custo, ordem, nó): a ordem é única, então o nó nunca é comparado.
    """

    __slots__ = ("_heap", "_removed")

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, Node]] = []
        self._removed: set[int] = set()

    def push(self, node: Node) -> None:
        """Insere o nó na posição do seu custo."""
        heapq.heappush(self._heap, (node.cost, node.order, node))

    def pop(self) -> Node:
        """Tira e devolve o nó de MENOR custo; no empate, o mais antigo."""
        while self._heap:
            _, order, node = heapq.heappop(self._heap)
            if order in self._removed:
                self._removed.discard(order)
                continue
            return node
        raise EmptyFrontierError

    def remove(self, node: Node) -> None:
        """Tira um nó que ainda está na fila, sem devolvê-lo.

        A remoção é preguiçosa: o nó só é descartado quando chegaria a vez
        dele no pop. O nó precisa estar na fila.
        """
        self._removed.add(node.order)

    def __len__(self) -> int:
        """Quantos nós ainda esperam, sem contar os removidos."""
        return len(self._heap) - len(self._removed)
