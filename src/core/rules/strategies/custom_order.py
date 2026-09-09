from __future__ import annotations

from dataclasses import dataclass, field

from core.rules.domain.base import TransitionRule
from core.rules.domain.catalog import RULE_BY_ID, RULES
from core.rules.domain.exceptions import InvalidRuleOrderError

DEFAULT_CUSTOM_ORDER: tuple[str, ...] = ("R2", "R4", "R6", "R1", "R3", "R5")


@dataclass(frozen=True, slots=True)
class CustomOrderStrategy:
    sequence: tuple[str, ...] = DEFAULT_CUSTOM_ORDER
    name: str = field(default="custom")

    def __post_init__(self) -> None:
        known = set(RULE_BY_ID)
        given = set(self.sequence)
        if len(self.sequence) != len(given):
            raise InvalidRuleOrderError("duplicated rule identifiers")
        unknown = given - known
        if unknown:
            raise InvalidRuleOrderError(f"unknown rule identifiers: {sorted(unknown)}")
        missing = known - given
        if missing:
            raise InvalidRuleOrderError(f"missing rule identifiers: {sorted(missing)}")

    def order(self, rules: tuple[TransitionRule, ...]) -> tuple[TransitionRule, ...]:
        position = {rule_id: index for index, rule_id in enumerate(self.sequence)}
        return tuple(sorted(rules, key=lambda rule: position[rule.id]))


def parse_order(raw: str) -> tuple[str, ...]:
    identifiers = tuple(
        token.strip().upper() for token in raw.split(",") if token.strip()
    )
    if len(identifiers) != len(RULES):
        raise InvalidRuleOrderError(
            f"expected {len(RULES)} identifiers, got {len(identifiers)}"
        )
    return CustomOrderStrategy(sequence=identifiers).sequence


CUSTOM = CustomOrderStrategy()
