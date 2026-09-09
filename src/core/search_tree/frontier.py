from __future__ import annotations

from collections import deque
from typing import Protocol

from core.search_tree.node import Node


class EmptyFrontierError(Exception):
    def __init__(self) -> None:
        super().__init__("cannot pop from an empty frontier")


class Frontier(Protocol):
    def push(self, node: Node) -> None: ...

    def pop(self) -> Node: ...

    def __len__(self) -> int: ...


class StackFrontier:
    __slots__ = ("_nodes",)

    def __init__(self) -> None:
        self._nodes: list[Node] = []

    def push(self, node: Node) -> None:
        self._nodes.append(node)

    def pop(self) -> Node:
        if not self._nodes:
            raise EmptyFrontierError
        return self._nodes.pop()

    def __len__(self) -> int:
        return len(self._nodes)


class QueueFrontier:
    __slots__ = ("_nodes",)

    def __init__(self) -> None:
        self._nodes: deque[Node] = deque()

    def push(self, node: Node) -> None:
        self._nodes.append(node)

    def pop(self) -> Node:
        if not self._nodes:
            raise EmptyFrontierError
        return self._nodes.popleft()

    def __len__(self) -> int:
        return len(self._nodes)
