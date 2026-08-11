set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
pnpm := "./scripts/pnpm"

init:
    mise install --locked
    {{pnpm}} install --frozen-lockfile

check:
    {{pnpm}} format:check
    {{pnpm}} lint
    {{pnpm}} typecheck
    {{pnpm}} test

ci: check
    {{pnpm}} build
