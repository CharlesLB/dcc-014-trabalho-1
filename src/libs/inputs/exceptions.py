from __future__ import annotations


class InputError(Exception): ...


class InvalidArgumentError(InputError):
    def __init__(self, detail: str) -> None:
        super().__init__(f"invalid argument: {detail}")
        self.detail = detail


class UnknownSelectionError(InputError):
    def __init__(self, kind: str, name: str, available: tuple[str, ...]) -> None:
        super().__init__(f"unknown {kind}: {name!r}")
        self.kind = kind
        self.name = name
        self.available = available
