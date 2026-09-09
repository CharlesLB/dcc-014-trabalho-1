from __future__ import annotations

from libs.inputs.selection import ExecutionRequest
from libs.outputs.formatter import ProblemReport, Report
from libs.ranking.leaderboard import build_leaderboard, build_summary
from runner.executor import run_matrix


def build_report(request: ExecutionRequest) -> Report:
    executed = run_matrix(request)
    problems = tuple(
        ProblemReport(
            problem_id=problem.id,
            initial_state=problem.initial,
            goal_state=problem.goal,
            results=results,
            leaderboard=build_leaderboard(problem.id, results, request.rank_mode),
        )
        for problem, results in executed
    )
    every_result = [result for _, results in executed for result in results]
    return Report(
        problems=problems,
        summary=build_summary(every_result),
        show_tree=request.show_tree,
        show_trace=request.show_trace,
        show_states=request.show_states,
    )
