from __future__ import annotations

from pathlib import Path

import pytest

from config import settings
from core.algorithms.domain.registry import ALGORITHM_NAMES
from core.domain.problem import PROBLEM_IDS
from core.rules.domain.exceptions import InvalidRuleOrderError
from core.rules.strategies.domain.registry import STRATEGY_NAMES
from libs.inputs.exceptions import InvalidArgumentError
from libs.inputs.parser import help_text, parse


def test_no_arguments_selects_every_axis() -> None:
    request = parse([])
    assert request.problem_ids == PROBLEM_IDS
    assert request.algorithm_names == ALGORITHM_NAMES
    assert request.strategy_names == STRATEGY_NAMES
    assert request.execution_count == (
        len(PROBLEM_IDS) * len(ALGORITHM_NAMES) * len(STRATEGY_NAMES)
    )


def test_all_is_equivalent_to_omitting_every_filter() -> None:
    assert parse(["--all"]) == parse([])


def test_all_overrides_explicit_filters() -> None:
    assert parse(["--all", "--algorithm", "irrevocable"]).algorithm_names == (
        ALGORITHM_NAMES
    )


def test_single_selection_narrows_the_axis() -> None:
    request = parse(["--algorithm", "backtracking", "--strategy", "descending"])
    assert request.algorithm_names == ("backtracking",)
    assert request.strategy_names == ("descending",)
    assert request.problem_ids == PROBLEM_IDS


def test_comma_separated_and_repeated_flags_accumulate() -> None:
    request = parse(["--strategy", "ascending,descending", "--strategy", "custom"])
    assert request.strategy_names == ("ascending", "descending", "custom")


def test_duplicates_are_collapsed() -> None:
    assert parse(["--strategy", "ascending,ascending"]).strategy_names == ("ascending",)


def test_problem_identifiers_are_upper_cased() -> None:
    assert parse(["--problem", "p1"]).problem_ids == ("P1",)


def test_display_flags_default_to_false() -> None:
    request = parse([])
    assert not request.show_tree
    assert not request.show_trace
    assert not request.show_states


def test_display_flags_are_read() -> None:
    request = parse(["--show-tree", "--show-trace", "--show-states"])
    assert request.show_tree
    assert request.show_trace
    assert request.show_states


def test_svg_dir_is_a_path() -> None:
    assert parse([]).svg_dir is None
    assert parse(["--svg-dir", "data"]).svg_dir == Path("data")


def test_output_path_is_a_path() -> None:
    assert parse(["--output", "out.json"]).output_path == Path("out.json")


def test_defaults_come_from_settings() -> None:
    request = parse([])
    assert request.output_format == settings.DEFAULT_OUTPUT_FORMAT
    assert request.rank_mode == settings.DEFAULT_RANK_MODE
    assert request.max_iterations == settings.MAX_ITERATIONS
    assert request.output_path is None
    assert request.seed is None


def test_custom_order_is_parsed() -> None:
    request = parse(["--strategy", "custom", "--order", "R2,R4,R6,R1,R3,R5"])
    assert request.custom_order == ("R2", "R4", "R6", "R1", "R3", "R5")


def test_incomplete_custom_order_is_rejected() -> None:
    with pytest.raises(InvalidRuleOrderError):
        parse(["--order", "R1,R2"])


@pytest.mark.parametrize("raw", ["zero", "0", "-3"])
def test_max_iterations_must_be_a_positive_integer(raw: str) -> None:
    with pytest.raises(InvalidArgumentError):
        parse(["--max-iterations", raw])


def test_seed_must_be_a_positive_integer() -> None:
    with pytest.raises(InvalidArgumentError):
        parse(["--seed", "abc"])
    assert parse(["--seed", "7"]).seed == 7


def test_unknown_flag_is_rejected() -> None:
    with pytest.raises(InvalidArgumentError):
        parse(["--nope"])


def test_help_and_list_are_flags() -> None:
    assert parse(["--help"]).show_help
    assert parse(["--list"]).list_only


def test_help_text_is_in_portuguese() -> None:
    text = help_text()
    assert settings.USAGE_PREFIX in text
    assert settings.OPTIONS_TITLE in text
    assert "options:" not in text
