"""FRONTEIRA — a lista de ABERTOS.

Os nós já gerados que ainda não foram processados. A busca tira um daqui,
olha em volta e devolve os filhos. Fronteira vazia, busca encerrada.

Quem sai primeiro define o algoritmo: pilha afunda, fila varre por nível,
fila de prioridade sai pelo menor custo.
"""

from __future__ import annotations

import heapq
from collections import deque
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
