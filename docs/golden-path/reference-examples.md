# Golden Path reference examples

These snippets are deliberately small. Copy only the applicable part, replace
the named choices, and commit the result as repository-owned source. They are
not generated assets and are not updated by a central release.

## Exact toolchain selector

Choose exact versions from the applicable profile and runtime-support catalog.
Do not paste the angle-bracket tokens unchanged.

```toml
min_version = "<EXACT_SUPPORTED_MISE_VERSION>"

[tools]
just = "<EXACT_JUST_VERSION>"
node = "<EXACT_SUPPORTED_NODE_PATCH>"

[settings]
lockfile = true
```

Replace `node` with or add `go`, `uv`, Rust support tools, IaC CLIs, and workflow
linters only when the repository uses them. The native runtime declaration must
agree with this selector.

## Root Just façade

Use native commands rather than copying their semantics into a central wrapper.
These compact examples show the command shape, not a universal build graph.

Node.js/TypeScript:

```just
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
```

Here `scripts/pnpm` is a repository-owned, reviewed userland bootstrap that
derives the exact pnpm version from `package.json#packageManager` and verifies
what it executes. Keep an equivalent mechanism if the repository uses another
path; do not assume bundled Corepack or add pnpm as an independent mise pin.

Go:

```just
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
export GOTOOLCHAIN := "local"

init:
    mise install --locked
    go mod download

check:
    go mod tidy -diff
    go mod verify
    go vet ./...
    golangci-lint run
    go test -mod=readonly ./...

ci: check
    go build ./...
```

Python:

```just
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
```

Adjust source paths, artifact builds, supported-runtime matrices, race or native
extension lanes, and credentialed tests to the real repository. Never represent
an unavailable capability with a successful no-op.

For a polyglot repository, keep those recipes in repository-local modules and
let the root `check` and `ci` call each applicable module. Do not merge native
locks or make one package manager authoritative over another.

## Repository-owned canonical CI

Pin reviewed actions to immutable commit SHAs. This example runs the canonical
gate exactly once; add repository-specific permissions, auth, service, matrix,
and release steps only when required.

```yaml
name: CI

on:
  pull_request:

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout repository
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false

      - name: Install pinned toolchain
        uses: jdx/mise-action@7e36c90d9ab29c415a2384db3006f3ec8a8cc654 # v4.2.4
        with:
          install: true
          cache: true

      - name: Install locked dependencies
        run: just init

      - name: Run canonical CI
        run: just ci
```

Review action pins at adoption time. A central conformance workflow must not
call this workflow or run `just ci` again.

## Dependabot starting point

Dependabot is the default adapter. Enumerate actual native roots and ecosystems;
do not add entries for absent manifests. The `3` below is a non-normative
starting budget for each configured ecosystem entry, not an organization-wide
queue or a per-repository guarantee. The repository may change it based on its
review capacity.

```yaml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    target-branch: dev
    open-pull-requests-limit: 3
    schedule:
      interval: weekly
    groups:
      development-toolchain:
        dependency-type: development
```

Replace `npm` and `/` with the actual ecosystem and native root. Use one
operational bot owner per dependency surface. Renovate may replace Dependabot
for a documented need; it must not duplicate the same surface.

Dependabot security-update pull requests are based on the repository's default
branch. Preserve alerts and security updates even when routine updates target
`dev`. If the repository's accepted branch model requires retargeting a
security pull request to `dev`, keep that workflow repository-owned, give it
only `pull-requests: write`, authenticate the Dependabot head repository and
branch, and verify final alert closure only after the fixed lock reaches the
default branch. Security work never waits for routine grouping.

## Ambiguous native roots

Use this file only when manifests and native workspace files do not make the
roots unambiguous:

```yaml
schemaVersion: golden-path-native-roots/v1
roots:
  - id: python-workspace
    path: .
    profiles:
      - python
  - id: web-app
    path: apps/web
    profiles:
      - node-typescript
```

Validate the owned copy against the
[native-root schema](../standards/developer-tooling/schemas/golden-path-native-roots-v1.schema.json).

## Bounded exception record

Keep an exception in repository canonical documentation or an ADR:

```markdown
### Developer Tooling exception: <short name>

- Requirement: <document and section>
- Scope: <exact repository surface>
- Reason and risk: <why and what can fail>
- Compensating control: <current protection>
- Owner: <accountable person or team>
- Approved by: <authority and date>
- Expires: <date>
- Exit condition: <observable condition that removes the exception>
```

An exception is not a central queue item. Its owner closes, renews, or removes it
through the repository's normal review process.
