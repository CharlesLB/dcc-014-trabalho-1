from __future__ import annotations

from core.search_tree.outcome import Outcome
from libs.ranking import criteria


def test_outcome_order_prefers_success_over_everything() -> None:
    assert (
        criteria.OUTCOME_ORDER[Outcome.SUCCESS]
        < criteria.OUTCOME_ORDER[Outcome.DEADLOCK]
        < criteria.OUTCOME_ORDER[Outcome.CUTOFF]
        < criteria.OUTCOME_ORDER[Outcome.FAILURE]
    )


def test_every_outcome_is_ranked() -> None:
    assert set(criteria.OUTCOME_ORDER) == set(Outcome)


def test_weights_sum_to_one() -> None:
    assert sum(criterion.weight for criterion in criteria.CRITERIA) == 1.0


def test_criterion_names_are_unique() -> None:
    names = [criterion.name for criterion in criteria.CRITERIA]
    assert len(set(names)) == len(names)


def test_elapsed_time_is_not_a_criterion() -> None:
    assert "elapsed" not in {criterion.name for criterion in criteria.CRITERIA}
