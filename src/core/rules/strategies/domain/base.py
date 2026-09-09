from __future__ import annotations

from typing import Protocol

from core.rules.domain.base import TransitionRule


class ControlStrategy(Protocol):
    @property
    def name(self) -> str: ...

    def order(
        self, rules: tuple[TransitionRule, ...]
    ) -> tuple[TransitionRule, ...]: ...
