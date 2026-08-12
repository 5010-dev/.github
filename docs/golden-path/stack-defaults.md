# Golden Path stack defaults

These defaults reduce setup decisions without replacing the normative
[Developer Tooling profiles](../standards/developer-tooling/profiles/README.md)
or repository-owned native configuration. Select every profile backed by real
source or a native manifest, and no others.

## Common base

Every active buildable repository starts with:

1. a root `mise.toml` with exact supported tool pins and its lock;
2. native manifests and locks or integrity records;
3. truthful root `just init`, `just check`, and `just ci` recipes;
4. one repository-owned canonical CI workflow that prepares locked
   dependencies and runs `just ci` once;
5. repository-owned security visibility and remediation, plus optional
   repository-owned routine dependency automation; and
6. release or deployment automation only for boundaries the repository
   actually owns.

Exact runtime patches come from the current
[runtime-support catalog](../standards/developer-tooling/runtime-support.md) and
the selected profile. The repository records the chosen exact versions; this
guide intentionally does not create a second version catalog.

## Stack choices

| Repository shape | Starting default | Native authority | Root command delegation |
| --- | --- | --- | --- |
| Node.js/TypeScript | Node 24 LTS, exact pnpm 11, TypeScript 6, ESLint flat config, Prettier, Vitest | `package.json`, `pnpm-lock.yaml`, workspace files | `pnpm` scripts own format, lint, typecheck, test, and build |
| Go | Latest supported Go 1.26 patch, module-native tools, golangci-lint v2 | `go.mod`, `go.sum`, optional intentional `go.work` | `go` and pinned support CLIs own tidy drift, vet, lint, test, race, and build |
| Python | Python 3.14, uv, Ruff, mypy, pytest | `pyproject.toml`, `uv.lock`, `.python-version` | `uv run --locked` owns format checks, lint, typecheck, test, and build |
| Rust | Current preferred Rust profile, rustup components, Cargo-native quality | `Cargo.toml`, `Cargo.lock` according to artifact policy, toolchain selector | Cargo owns format, clippy, test, and build |
| Polyglot | Combine only the applicable rows; do not invent a merged dependency graph | Each ecosystem retains its own manifests, locks, and roots | Root Just orchestrates named repository-local recipes without reimplementing native semantics |

Read the full [Node.js/TypeScript](../standards/developer-tooling/profiles/node-typescript.md),
[Go](../standards/developer-tooling/profiles/go.md),
[Python](../standards/developer-tooling/profiles/python.md), or
[Rust](../standards/developer-tooling/profiles/rust.md) profile before claiming
conformance. Infrastructure and documentation repositories use their
corresponding profiles instead of adding a dummy application manifest.

## Polyglot and multi-root rule

Keep one operational owner for each dependency surface. Use
`.github/golden-path-native-roots.yaml` only when the native roots are ambiguous
from manifests and workspaces. The file records stable IDs, paths, and profiles;
it does not map packages to release units or infer impact from component paths.

If one root cannot be classified, stop only that root as
`pending-classification`. Continue visibility and security routing for the rest
of the repository; do not create placeholder manifests or a central approval
wait state.
