from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import perf_counter
from typing import ClassVar

from config import settings
from core.domain.problem import Problem
from core.domain.state import State
from core.rules.domain.base import TransitionRule
from core.rules.strategies.domain.base import ControlStrategy
from core.search_tree import path
from core.search_tree.metrics import MetricsCollector
from core.search_tree.node import Node
from core.search_tree.outcome import Outcome
from core.search_tree.result import SearchResult
from core.search_tree.trace import TraceEvent, TraceRecorder
from core.search_tree.tree import SearchTree


class SearchNotStartedError(Exception):
    def __init__(self) -> None:
        super().__init__("search context is only available during solve()")


@dataclass(slots=True)
class _RunContext:
    problem: Problem
    root: Node
    metrics: MetricsCollector = field(default_factory=MetricsCollector)
    trace: TraceRecorder = field(default_factory=TraceRecorder)
    goal_node: Node | None = None


class SearchAlgorithm(ABC):
    name: ClassVar[str] = "abstract"

    def __init__(
        self,
        tree: SearchTree,
        strategy: ControlStrategy,
        *,
        max_iterations: int = settings.MAX_ITERATIONS,
    ) -> None:
        self._tree = tree
        self._strategy = strategy
        self._max_iterations = max_iterations
        self._context: _RunContext | None = None

    @property
    def strategy(self) -> ControlStrategy:
        return self._strategy

    @property
    def max_iterations(self) -> int:
        return self._max_iterations

    def solve(self, problem: Problem) -> SearchResult:
        context = _RunContext(problem=problem, root=self._tree.root(problem.initial))
        self._context = context
        context.metrics.count_generated(context.root.depth)
        context.trace.record(iteration=0, event=TraceEvent.ROOT, node=context.root)

        started = perf_counter()
        try:
            outcome = self._search(problem)
        finally:
            elapsed_ms = (perf_counter() - started) * 1000.0
            self._context = None

        goal_node = context.goal_node if outcome.is_success else None
        solution = () if goal_node is None else path.path_to(goal_node)
        return SearchResult(
            algorithm=self.name,
            strategy=self._strategy.name,
            problem=problem.id,
            outcome=outcome,
            solution_path=solution,
            applied_rules=() if goal_node is None else path.applied_rules(goal_node),
            metrics=context.metrics.seal(elapsed_ms),
            trace=context.trace.seal(),
        )

    @abstractmethod
    def _search(self, problem: Problem) -> Outcome: ...

    def _applicable_rules(self, node: Node) -> tuple[TransitionRule, ...]:
        context = self._require_context()
        applicable: list[TransitionRule] = []
        for rule in self._tree.rules:
            context.metrics.count_rule_test()
            if rule.is_applicable(node.state):
                applicable.append(rule)

        allowed: list[TransitionRule] = []
        for rule in self._strategy.order(tuple(applicable)):
            successor = rule.apply(node.state)
            if self._is_repetition(node, successor):
                context.trace.record_prune(
                    iteration=context.metrics.iterations,
                    node=node,
                    rule_id=rule.id,
                    state=successor,
                )
                continue
            allowed.append(rule)
        return tuple(allowed)

    def _is_repetition(self, node: Node, successor: State) -> bool:
        return path.contains_state(node, successor)

    def _require_context(self) -> _RunContext:
        if self._context is None:
            raise SearchNotStartedError
        return self._context

    def _next_iteration(self) -> bool:
        context = self._require_context()
        if context.metrics.iterations >= self._max_iterations:
            context.trace.record(
                iteration=context.metrics.iterations,
                event=TraceEvent.CUTOFF,
                node=context.root,
            )
            return False
        context.metrics.count_iteration()
        return True

    def _visit(self, node: Node) -> None:
        context = self._require_context()
        context.metrics.count_visited()
        context.trace.record(
            iteration=context.metrics.iterations, event=TraceEvent.VISIT, node=node
        )

    def _expand(self, node: Node, rule: TransitionRule) -> Node:
        context = self._require_context()
        child = self._tree.expand(node, rule)
        context.metrics.count_generated(child.depth)
        context.trace.record(
            iteration=context.metrics.iterations, event=TraceEvent.GENERATE, node=child
        )
        return child

    def _succeed(self, node: Node) -> Outcome:
        context = self._require_context()
        context.goal_node = node
        context.trace.record(
            iteration=context.metrics.iterations, event=TraceEvent.GOAL, node=node
        )
        return Outcome.SUCCESS

    def _deadlock(self, node: Node) -> None:
        context = self._require_context()
        context.metrics.count_deadlock()
        context.trace.record(
            iteration=context.metrics.iterations, event=TraceEvent.DEADLOCK, node=node
        )

    def _backtrack(self, node: Node) -> None:
        context = self._require_context()
        context.metrics.count_backtrack()
        context.trace.record(
            iteration=context.metrics.iterations, event=TraceEvent.BACKTRACK, node=node
        )

    def _exhausted(self) -> Outcome:
        context = self._require_context()
        context.trace.record(
            iteration=context.metrics.iterations,
            event=TraceEvent.EXHAUSTED,
            node=context.root,
        )
        return Outcome.FAILURE
