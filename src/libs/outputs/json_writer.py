from __future__ import annotations

import json
from pathlib import Path

from core.domain.state import Peg, State
from core.search_tree.result import SearchResult
from libs.outputs import theme
from libs.outputs.formatter import ProblemReport, Report
from libs.ranking.leaderboard import Leaderboard, Summary

type JsonValue = (
    str | int | float | bool | list["JsonValue"] | dict[str, "JsonValue"] | None
)


class JsonFormatter:
    name = "json"

    def render(self, report: Report) -> str:
        payload: dict[str, JsonValue] = {
            "problemas": [_problem_to_json(entry) for entry in report.problems]
        }
        if report.summary is not None:
            payload["resumo"] = _summary_to_json(report.summary)
        return json.dumps(payload, ensure_ascii=False, indent=2)


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _problem_to_json(entry: ProblemReport) -> JsonValue:
    payload: dict[str, JsonValue] = {
        "id": entry.problem_id,
        "estado_inicial": _state_to_json(entry.initial_state),
        "objetivo": _state_to_json(entry.goal_state),
        "execucoes": [_result_to_json(result) for result in entry.results],
    }
    if entry.leaderboard is not None:
        payload["placar"] = _leaderboard_to_json(entry.leaderboard)
    return payload


def _leaderboard_to_json(leaderboard: Leaderboard) -> JsonValue:
    return {
        "modo": leaderboard.mode,
        "posicoes": [
            {
                "posicao": row.position,
                "algoritmo": row.result.algorithm,
                "estrategia": row.result.strategy,
                "desfecho": theme.outcome_label(row.result.outcome),
                "movimentos": row.result.solution_length,
                "escore": row.score,
            }
            for row in leaderboard.rows
        ],
    }


def _summary_to_json(summary: Summary) -> JsonValue:
    return [
        {
            "algoritmo": row.algorithm,
            "estrategia": row.strategy,
            "execucoes": row.runs,
            "sucessos": row.successes,
            "impasses": row.deadlocks,
            "movimentos_medios": row.mean_moves,
            "iteracoes_medias": round(row.mean_iterations, 2),
        }
        for row in summary.rows
    ]


def _result_to_json(result: SearchResult) -> JsonValue:
    metrics = result.metrics
    return {
        "algoritmo": result.algorithm,
        "estrategia": result.strategy,
        "desfecho": theme.outcome_label(result.outcome),
        "movimentos": result.solution_length,
        "caminho": list(result.applied_rules),
        "metricas": {
            "iteracoes": metrics.iterations,
            "nos_gerados": metrics.nodes_generated,
            "nos_visitados": metrics.nodes_visited,
            "regras_testadas": metrics.rules_tested,
            "retrocessos": metrics.backtracks,
            "impasses": metrics.deadlocks,
            "profundidade_maxima": metrics.max_depth,
            "tempo_ms": round(metrics.elapsed_ms, 3),
        },
        "estados": [_state_to_json(node.state) for node in result.solution_path],
    }


def _state_to_json(state: State) -> JsonValue:
    return {
        theme.PEG_NAMES[peg]: [theme.disk_name(disk) for disk in state[peg]]
        for peg in Peg
    }
