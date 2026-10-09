from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from core.rules.domain.base import TransitionRule
from core.rules.domain.exceptions import UnknownRuleError
from core.rules.moves import R1, R2, R3, R4, R5, R6

RULES: tuple[TransitionRule, ...] = (R1, R2, R3, R4, R5, R6)

RULE_BY_ID: Mapping[str, TransitionRule] = MappingProxyType(
    {rule.id: rule for rule in RULES}
)

# A inversa de uma regra é a que faz o caminho oposto: troca origem e destino.
INVERSE_RULE_ID: Mapping[str, str] = MappingProxyType(
    {
        rule.id: inverse.id
        for rule in RULES
        for inverse in RULES
        if (inverse.origin, inverse.destination) == (rule.destination, rule.origin)
    }
)


def get_rule(rule_id: str) -> TransitionRule:
    try:
        return RULE_BY_ID[rule_id]
    except KeyError:
        raise UnknownRuleError(rule_id) from None


def inverse_of(rule: TransitionRule) -> TransitionRule:
    return RULE_BY_ID[INVERSE_RULE_ID[rule.id]]
