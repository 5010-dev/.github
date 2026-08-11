set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

init:
    mise install --locked
    uv sync --locked

check:
    uv lock --check
    uv run --locked ruff format --check .
    uv run --locked ruff check .
    uv run --locked mypy src
    uv run --locked pytest

ci: check
    uv build
