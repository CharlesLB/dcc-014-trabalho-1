PYTHON ?= python3.12
VENV   := .venv
BIN    := $(VENV)/bin

.DEFAULT_GOAL := help
.PHONY: help install test lint types check run graphs clean

help:  ## Lista os alvos disponíveis
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

install:  ## Dependências de desenvolvimento
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip setuptools wheel
	$(BIN)/pip install -e ".[dev]"

test:  ## Suíte completa com cobertura
	$(BIN)/pytest

lint:  ## ruff check + format --check
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

types:  ## mypy --strict
	$(BIN)/mypy src main.py tests

check: lint types test  ## lint + types + test

run:  ## Executa a matriz completa
	$(BIN)/python main.py --all

graphs:  ## Grava a árvore de cada execução em data/ (DOT e SVG, exige Graphviz)
	$(BIN)/python main.py --all --svg-dir data

clean:  ## Remove artefatos
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	find . -type d -name __pycache__ -not -path "./$(VENV)/*" -exec rm -rf {} +
