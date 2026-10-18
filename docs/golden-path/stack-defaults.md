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
corresponding profiles instead of adding a dummy application manifest; see
[Infrastructure as code](#infrastructure-as-code).

## Infrastructure as code

Use the [IaC profile](../standards/developer-tooling/profiles/infrastructure.md)
with the host-language profile. AWS CDK v2 with TypeScript remains the starting
default for new AWS IaC. Use Pulumi only under the profile's conditions, such as
an accepted ADR for the IaC owner.

A Pulumi with TypeScript repository keeps three concepts apart:

| Concept | What it is | Native root? |
| --- | --- | --- |
| Program (Pulumi project) | A directory with `Pulumi.yaml` and its entry point | Yes, `infrastructure-pulumi` |
| Stack | Configuration, state, and lock target of one program, such as `Pulumi.<stack>.yaml` | No |
| Host dependency root | The actual host-language root, such as a pnpm workspace whose single lock covers programs that share it and their shared library | Yes, `node-typescript` |

With more than one program, declare the roots explicitly. Use the actual paths;
the program names below are illustrative:

```yaml
schemaVersion: golden-path-native-roots/v1
roots:
  - id: workspace
    path: .
    profiles:
      - node-typescript
  - id: program-network
    path: programs/network
    profiles:
      - infrastructure-pulumi
  - id: program-runtime
    path: programs/runtime
    profiles:
      - infrastructure-pulumi
```

`just init` prepares the locked host dependencies and tools. Root `just ci`
then runs `check` (format, lint, typecheck, and tests) and any applicable
build or package validation, without cloud, backend, or state credentials, as
the [command contract](../standards/developer-tooling/command-contract.md)
defines. Preview, import,
refresh, and apply belong to repository-owned stateful delivery for one named
project and stack at a time. A shared code, lock, or provider change previews
every consuming stack before an explicitly selected apply.

IaC that owns shared ECS services also follows the
[ECS deployment contract](../platform/ecs-deployment-contract.md) and the
[service delivery workflow standard](../platform/ecs-service-delivery-workflow-standard.md).
Other IaC does not need ECS rules.

## Polyglot and multi-root rule

Keep one operational owner for each dependency surface. Use
`.github/golden-path-native-roots.yaml` only when the native roots are ambiguous
from manifests and workspaces. The file records stable IDs, paths, and profiles;
it does not map packages to release units or infer impact from component paths.

If one root cannot be classified, stop only that root as
`pending-classification`. Continue visibility and security routing for the rest
of the repository; do not create placeholder manifests or a central approval
wait state.
