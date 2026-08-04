# Toolchain management

- Status: Accepted
- Standard version: `2026.08`

The root `mise.toml` is a thin repository-local bootstrap and tool-selection
entry point. It does not make mise the owner of every language runtime.

## Common contract

Every applicable repository:

- MUST commit a root `mise.toml`;
- MUST declare a hard `min_version` for the mise features it uses;
- MUST avoid correctness dependencies on user-global, parent-directory, or
  mutable system configuration;
- MUST NOT commit `mise.local.toml`, `mise.local.lock`, secrets, personal paths,
  or machine-specific overrides;
- MUST manage only tools for which the selected profile names mise as the
  operational owner;
- MUST enable and commit a non-local `mise.lock` whenever mise manages at least
  one tool;
- MUST install from committed configuration and lock data in CI and verify that
  installation does not rewrite them; and
- MUST retain one operational owner for each toolchain.

CI-critical tools SHOULD use exact patch selectors. A major or minor selector
MAY be used when a committed mise lock resolves it to an exact version and
updates arrive only through reviewable changes.

`latest`, `system`, moving prerelease channels, and unlocked fuzzy selectors
MUST NOT be default-branch or CI authorities.

## Operational owners

| Profile | Native authority | Operational owner |
| --- | --- | --- |
| Node.js/TypeScript | `package.json#engines.node` defines compatibility | mise selects an exact compatible Node; pnpm owns packages |
| Python | `pyproject.toml#requires-python`, `.python-version`, and `uv.lock` | uv owns Python installation, interpreter selection, `.venv`, and dependencies; mise MAY install uv |
| Go | `go.mod`/`go.work` `go` and `toolchain` directives | mise installs an exact base Go aligned with native directives |
| Rust | `Cargo.toml#rust-version` and `rust-toolchain.toml` | rustup owns the exact Rust toolchain; mise MUST NOT repin Rust |
| Zig | `build.zig`, `build.zig.zon`, and the profile's exact release | mise installs the exact tagged Zig and matching ZLS |
| IaC and support CLI | Native compatibility declaration where available | mise owns exact CLIs lacking a stronger repository-local selector |

In every profile, mise MAY prepare Just and common support tools such as
actionlint or ShellCheck. A tool installed by a native project dependency MUST
NOT receive an independent mise version pin.

## Authority order

1. This standard owns supported release lines, operational-owner selection,
   EOL, and exception policy.
2. Native manifests own compatibility, language level, and package metadata.
3. The profile-selected repository selector owns the exact development and CI
   toolchain.
4. `mise.lock` records exact mise resolution and available asset integrity
   metadata.
5. The root Justfile calls those tools through the stable command contract.

`mise.lock` does not replace `pnpm-lock.yaml`, `uv.lock`, `go.sum`,
`Cargo.lock`, `.terraform.lock.hcl`, or Zig content hashes.

## Bootstrap and CI

- `just init` starts bootstrap and orchestrates mise or the profile-native
  installer.
- CI uses the same committed selectors and locks.
- mise tasks MAY be internal helpers but MUST NOT become a second public
  interface competing with `just init`, `just check`, or `just ci`.
- Directory entry hooks MUST NOT install dependencies, modify source, mutate a
  network resource, or retrieve secrets as an implicit side effect.
- Editor integration is optional; every required action MUST remain available
  from the command line and CI.
- A backend's lock metadata MUST NOT be described as checksum or provenance
  protection when the backend does not provide that evidence.

## Updates and EOL

Tool updates change selectors, locks, native compatibility declarations, and
validation together in one reviewable change. Repositories own exact pins; this
standard owns support policy and MUST NOT copy repository-specific versions.

An EOL line follows the [runtime-support lifecycle](./runtime-support.md).
Repository adoption or migration is not performed by changing this standard.

Rule IDs: `DT-TOOL-*`, `DT-RUNTIME-*`.
