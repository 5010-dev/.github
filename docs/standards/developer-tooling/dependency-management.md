# Dependency management

- Status: Accepted
- Standard version: `2026.08.5`

Each ecosystem's native manager owns dependency resolution. mise owns selected
runtime and support-tool bootstrap; Just exposes stable commands. Neither
redeclares dependency graphs.

## Common contract

For each ecosystem build root:

- exactly one approved native dependency manager MUST be the operational owner;
- native manifests and the ecosystem's resolution or integrity records MUST be
  committed when the ecosystem produces them;
- competing lockfiles for the same graph MUST NOT coexist;
- CI and `just ci` MUST prepare dependencies in explicit locked, frozen, or
  read-only mode;
- a missing, stale, or rewritten lock MUST fail CI;
- locks MUST be changed only through their native manager;
- a dependency update MUST include manifest, resolution record, required
  generated outputs, and validation in one reviewable change;
- direct Git, URL, or archive dependencies MUST use immutable commits, content
  hashes, or exact artifact digests;
- credentials and private keys MUST NOT be committed in manifests, locks, or
  package-manager configuration; and
- native workspace and lock boundaries MUST be preserved.

A native dependency root is an ecosystem manager's operational project or
workspace boundary, not necessarily the Git repository root or an artifact
component path. Several artifacts MAY share one native root, and one artifact
MAY participate in more than one ecosystem root. Roots for disjoint profiles
MAY use the same repository-relative path. Two roots for the same profile MUST
NOT overlap because that would create competing authority for one dependency
graph. A native root MUST resolve to exactly one dependency-automation adapter
ecosystem. When disjoint ecosystems use the same path, they remain separate
native roots; this does not create package-level mapping or another release-unit
model.

A repository whose native roots differ from its generated component paths MUST
declare `.github/golden-path-native-roots.yaml`. Each declared root selects the
native profiles evaluated at that path, and each selected profile MUST also
appear in the aggregate declaration in `.github/golden-path.yaml`. Every
selected native profile MUST be covered by at least one root. Artifact types
and capabilities remain component or aggregate metadata; they MUST NOT be
duplicated onto dependency roots. The native-root file is repository-owned and
MUST preserve the generated ownership and digest of
`.github/golden-path.yaml`.

Dependency groups SHOULD separate runtime, development, test, and optional
surfaces. Caches MAY accelerate installation, but cache hits MUST NOT be
correctness requirements.

Vendoring MAY be used for offline, regulated, or air-gapped requirements. A
vendored tree is generated output and MUST be reproducible from, and checked
against, its native manifest and resolution record.

## Profile map

| Profile | Manager | Manifest | Resolution or integrity record | CI preparation |
| --- | --- | --- | --- | --- |
| Node.js/TypeScript | pnpm | `package.json`, conditional `pnpm-workspace.yaml` | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` |
| Python | uv | `pyproject.toml` | `uv.lock` | `uv sync --locked` and applicable `uv run --locked` |
| Go | Go modules | `go.mod`, conditional `go.work` | `go.sum` | `go mod tidy -diff`, `go mod verify`, read-only build/test |
| Rust | Cargo | `Cargo.toml` | root `Cargo.lock` | applicable Cargo commands with `--locked` |
| Zig | Zig build system | `build.zig` and `build.zig.zon` | ZON content hashes and exact compiler lock | tagged-compiler build/test |
| AWS CDK | CDK and host-language manager | `cdk.json`, host manifest | host lock; conditional reviewed `cdk.context.json` | locked install and deterministic synth |
| Terraform/OpenTofu | native CLI | `.tf` and `required_version` | `.terraform.lock.hcl` | backend-disabled, read-only-lock init and validate |
| Pulumi | Pulumi and host-language manager | `Pulumi.yaml`, host manifest | host lock and provider pins | locked install/static checks; stateful preview belongs to delivery |

## Node.js and TypeScript

- pnpm is the only default package manager.
- Each Node.js project or workspace root `package.json` MUST declare exact
  `packageManager: pnpm@x.y.z`.
- pnpm MUST NOT be independently versioned in mise.
- `pnpm-lock.yaml` MUST be committed and CI MUST explicitly use
  `--frozen-lockfile`.
- A pnpm workspace MUST use its root `pnpm-workspace.yaml`, one workspace-root
  lock, and
  `workspace:` for internal packages.
- pnpm 11 project settings belong in `pnpm-workspace.yaml`.
- Install scripts MUST be approved through `allowBuilds`;
  `dangerouslyAllowAllBuilds: true` is prohibited.
- `minimumReleaseAge: 1440` non-strict is the default quarantine.
  `minimumReleaseAgeStrict: true` is a SHOULD for production/external release
  profiles and a conditional MUST only when the threat model or regulation
  requires it. Narrow package/version exclusions cover private registries,
  unavailable mature versions, and emergency security fixes.
- Repositories accepting external lock changes MUST NOT use
  `trustLockfile: true`.
- Corepack bundled with Node MUST NOT be assumed; bootstrap derives exact pnpm
  from `packageManager` through a verified userland mechanism.

## Python

- `pyproject.toml` and `uv.lock` are the dependency authority.
- uv owns the Python interpreter, `.venv`, resolution, and synchronization.
- Development dependencies use PEP 735 dependency groups; consumer-facing
  published features use `project.optional-dependencies`.
- Regular CI uses `--locked`. `--frozen` is limited to a bounded packaging or
  Docker layer that intentionally consumes a lock without a complete manifest.
- Requirements files MAY be generated for external consumers but MUST NOT
  become the authority for a new project.
- `.venv`, caches, and machine-local Python installations MUST NOT be committed.

## Go

- `go.mod` is the manifest authority; `go.sum` is downloaded-content integrity,
  not an exact-version lockfile.
- A generated non-empty `go.sum` MUST be committed; an empty file is not
  required for a dependency-free module.
- CI uses `go mod tidy -diff`, `go mod verify`, and read-only module semantics.
- Go 1.24+ project tools use the `tool` directive and `go tool`.
- New projects MUST NOT use `tools.go` blank imports or global
  `go install ...@latest`.
- `go.work` is committed only for an intentional multi-module repository
  boundary.

## Rust

- `Cargo.toml` is the manifest authority and every Golden Path Rust project
  commits root `Cargo.lock`.
- Workspaces use one root lock.
- Fetch, check, test, lint, build, and package commands use `--locked`.
- Git dependencies SHOULD declare immutable `rev` values and MUST NOT depend
  only on moving branches.

## Zig

Zig is a conditional profile. Every Zig package commits both `build.zig` and
`build.zig.zon`; the latter owns package identity, exact minimum Zig line,
fingerprint, distributable paths, and any dependency URL/hash. No organization
pseudo-lockfile is introduced.

## Infrastructure

- AWS CDK v2 remains the default for AWS IaC and combines its local project
  dependencies with the host-language lock.
- Terraform/OpenTofu use one engine per root, commit
  `.terraform.lock.hcl`, and pin modules separately because the provider lock
  does not lock modules.
- Pulumi commits `Pulumi.yaml`, uses its host-language lock, and pins CLI, SDK,
  and providers.
- One cloud resource MUST have one IaC engine and state write owner.
- Moving from one IaC engine to another requires a separate architecture and
  state/resource-identity migration decision.

## Generated output

Generated exports, vendor trees, and SBOMs are derived artifacts. If they form a
delivery or external consumer contract, the dependency update MUST regenerate
and drift-check them in the same review.

Rule IDs: `DT-DEP-*`.

Dependency automation classification, root-to-release-unit references, PR
budgets, security routing, deterministic preview, and live reporting are defined
in [Dependency operations](./dependency-operations.md).
