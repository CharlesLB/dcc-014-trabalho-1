from __future__ import annotations

import ast
import io
import tokenize

MAGIC_PREFIXES = ("%%", "#@title")
PLACEHOLDER = "..."
_DOCUMENTED = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def without_comments(source: str) -> str:
    head, body = _split_magic(source)
    lines = body.splitlines()
    dropped, replaced = _docstring_lines(body)
    for number, column in _comments(body):
        if number in dropped:
            continue
        kept = lines[number - 1][:column].rstrip()
        if kept:
            replaced[number] = kept
        else:
            dropped.add(number)
    kept_lines = [
        replaced.get(number, line)
        for number, line in enumerate(lines, start=1)
        if number not in dropped
    ]
    return head + "\n".join(_tidy(kept_lines))


def _split_magic(source: str) -> tuple[str, str]:
    head, separator, rest = source.partition("\n")
    if head.startswith(MAGIC_PREFIXES):
        return head + separator, rest
    return "", source


def _docstring_lines(body: str) -> tuple[set[int], dict[int, str]]:
    dropped: set[int] = set()
    replaced: dict[int, str] = {}
    for node in ast.walk(ast.parse(body)):
        if not isinstance(node, _DOCUMENTED) or not node.body:
            continue
        first = node.body[0]
        if not (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue
        end = first.end_lineno or first.lineno
        dropped.update(range(first.lineno, end + 1))
        if len(node.body) == 1 and not isinstance(node, ast.Module):
            dropped.discard(first.lineno)
            replaced[first.lineno] = " " * first.col_offset + PLACEHOLDER
    return dropped, replaced


def _comments(body: str) -> list[tuple[int, int]]:
    return [
        token.start
        for token in tokenize.generate_tokens(io.StringIO(body).readline)
        if token.type == tokenize.COMMENT
    ]


def _tidy(lines: list[str]) -> list[str]:
    tidy: list[str] = []
    blanks = 0
    for index, line in enumerate(lines):
        if line.strip():
            tidy.append(line)
            blanks = 0
            continue
        following = next((item for item in lines[index + 1 :] if item.strip()), "")
        opens_block = bool(tidy) and tidy[-1].rstrip().endswith(":")
        limit = 1 if following.startswith((" ", "\t")) else 2
        if not tidy or opens_block or not following or blanks >= limit:
            continue
        tidy.append("")
        blanks += 1
    return tidy
