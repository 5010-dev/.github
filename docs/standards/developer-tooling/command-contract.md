# Developer tooling command contract

- Status: Accepted
- Standard version: `2026.07`
- Contract version: `golden-path/v1`

This contract defines the stable commands that developers and CI use. Native
package managers, build systems, test runners, and repository-local scripts
remain implementation owners; the root Justfile composes them.

## Base commands

Every applicable repository MUST provide a discoverable root `justfile` with:

| Command | Requirement | Semantics |
| --- | --- | --- |
| `just init` | MUST | Repeatedly prepares repository-local dependencies, declared development tools, and hooks. It MUST NOT mutate production/shared state or require production secrets. |
| `just check` | MUST | Runs the canonical local, non-mutating quality gate. It MAY write ignored caches and isolated test artifacts, but MUST NOT modify tracked source or shared external state. |
| `just ci` | MUST | Runs `check` through the same implementation path and adds applicable clean build, package, generated-artifact, or other deterministic CI validation. It MUST NOT deploy, release, or mutate production. |

The following commands become MUST requirements when their capability exists or
the selected profile requires them:

| Command | Required semantics |
| --- | --- |
| `just format` | The explicit source-writing formatter command |
| `just format-check` | Read-only formatting drift detection |
| `just lint` | Read-only lint; automatic fixes use a separate command |
| `just typecheck` | Non-mutating language or project static analysis |
| `just test` | Deterministic default automated test suite |
| `just build` | Local build using the declared toolchain and locked dependencies |

A repository MUST NOT add a successful no-op recipe for a capability it does
not implement.

## `check` and `ci`

- `check` MUST be complete enough for normal local iteration.
- `ci` MUST call `check` or the same underlying implementation.
- Both commands MUST be non-interactive and MUST fail when a required gate is
  not established.
- Formatting, lint fixes, code generation, migrations, deployment, publication,
  destructive integration tests, production smoke tests, and notification are
  separate explicit commands or workflows.
- CI SHOULD be thin orchestration that prepares the exact environment and calls
  `just ci`; workflow YAML SHOULD NOT reimplement the quality graph.
- External, credentialed, long-running, or destructive suites MUST use
  separately named commands such as `test-e2e` or a namespaced command.

## Command behavior

Applicable commands MUST:

- use repository-local native manifests, locks, and exact toolchain selectors;
- run from a documented working-directory boundary;
- propagate failure without converting missing evidence into success;
- avoid printing secrets, credentials, or personal absolute paths;
- bound polling, retry, and temporary-resource cleanup; and
- remain callable without an editor or developer-specific global configuration.

Commands MAY create ignored caches, virtual environments, build output, coverage
reports, or isolated local test resources when their cleanup and authority
boundaries are explicit.

## Extension commands

Profiles MAY require commands such as `package-check`, `test-race`,
`test-features`, `test-msrv`, `coverage`, or `generate-check`. These are stable
capability interfaces only when the corresponding profile declares them.

Deployment-related `preview`, `deploy`, `destroy`, `drift`, or state-repair
commands are not universal base commands. If provided, they MUST remain
separate from `check` and `ci` and follow the owning deployment contract.

## Conformance

The conformance checker evaluates at least:

- the root Justfile and base recipe presence;
- profile-required command presence without successful no-ops;
- non-mutating `check`, `ci`, format-check, lint, and typecheck paths;
- `ci` composition through `check`;
- separation of deployment/release mutation;
- deterministic repository-local imports, modules, and scripts; and
- the caller workflow's use of `just ci`.

Rule IDs: `DT-CMD-*`.
