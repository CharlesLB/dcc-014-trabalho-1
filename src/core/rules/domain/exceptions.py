class RuleError(Exception): ...


class RuleNotApplicableError(RuleError):
    def __init__(self, rule_id: str) -> None:
        super().__init__(f"rule {rule_id} is not applicable to the given state")
        self.rule_id = rule_id


class UnknownRuleError(RuleError):
    def __init__(self, rule_id: str) -> None:
        super().__init__(f"unknown rule identifier: {rule_id!r}")
        self.rule_id = rule_id


class InvalidRuleOrderError(RuleError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"invalid rule order: {reason}")
        self.reason = reason


class UnknownStrategyError(RuleError):
    def __init__(self, name: str) -> None:
        super().__init__(f"unknown control strategy: {name!r}")
        self.name = name
