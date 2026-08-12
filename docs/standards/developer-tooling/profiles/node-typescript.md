# Node.js and TypeScript profile

- Status: Accepted
- Profile ID: `node-typescript`
- Standard version: `2026.08.8`

This profile combines a common TypeScript quality contract with artifact-specific
module, build, workspace, and publishing behavior.

## Operating line

| Area | Default |
| --- | --- |
| Runtime | Exact Node 24 LTS satisfying the runtime catalog |
| Package manager | Exact pnpm 11 from `packageManager` and `pnpm-lock.yaml` |
| TypeScript | Exact TypeScript 6.x catalog entry |
| Formatter | Exact Prettier 3.9 line |
| Lint | ESLint 10 flat config plus typescript-eslint typed lint |
| Type analysis | Separate `tsc` gate |
| Tests | Vitest 4 |

Node 22 is supported. TypeScript 7 is evaluation-only until compiler API,
typescript-eslint, formatter, test, and framework fixtures support it.
Side-by-side TS 6 compatibility tooling for a TS 7 evaluation requires an
expiring evaluation exception.

Biome is evaluation-only for this baseline. Jest is a compatibility variation
for framework integration or a bounded migration. A small Node-native library,
CLI, or script MAY use `node:test` when Vitest capabilities are unnecessary.

## Formatting, lint, and type analysis

- Prettier configuration and exact dependency resolution MUST be committed.
- Editor integration MUST resolve the same repository-local exact Prettier
  version as CI rather than a user-global formatter.
- `format` writes and `format-check` reads.
- New projects MUST use ESLint flat config, not `.eslintrc`.
- Typed lint SHOULD use typescript-eslint Project Service with explicit
  `tsconfigRootDir` and project boundaries.
- `lint` MUST be read-only; `lint-fix` is an explicit write command.
- Generated/vendor/build/coverage output SHOULD be explicitly ignored without
  broad patterns that hide source.
- Every production TypeScript artifact MUST provide a separate `typecheck`.
- A single project SHOULD use `tsc --noEmit --pretty false`; a reference graph
  SHOULD use a non-emitting or build-mode check that stops on build errors.
- A bundler, transpiler, test runner, or Node type stripping MUST NOT replace
  `tsc`.

## TypeScript configuration

A versioned strict base and artifact overlay SHOULD be materialized rather than
copying one universal tsconfig.

The strict base includes:

- `strict`
- `noUncheckedIndexedAccess`
- `exactOptionalPropertyTypes`
- `noImplicitOverride`
- `noFallthroughCasesInSwitch`
- `noUncheckedSideEffectImports`
- `verbatimModuleSyntax`
- `forceConsistentCasingInFileNames`
- `isolatedModules` when a non-tsc transform is used
- explicit ambient `types` and source boundaries
- declaration/composite settings when the artifact emits them

Disabling a source-error-revealing strict option requires an approved exception.

## Modules and build

| Artifact | Module/resolution | Build owner |
| --- | --- | --- |
| Node service/CLI | Explicit ESM, NodeNext | `tsc` unless bundling has an artifact requirement |
| Published Node library | ESM-first, explicit `exports` and declarations | Library build profile |
| Browser/framework app | Framework ESM and bundler resolution | Framework/application builder |
| Tooling script | Node erasable TypeScript or compiled JS | Node runtime plus separate typecheck |
| Mixed workspace | Explicit package-local `type` and overlays | Package-local builds, root orchestration |

New Node-native artifacts MUST declare `package.json#type`. Runtime-visible
relative ESM imports use the correct extension. New packages define public
entry points through `exports`; accidental deep imports are not API.

CJS or dual packages require a demonstrated consumer need and import/require
smoke matrix. `target` is selected from the actual runtime/support floor, not
`latest`. A path alias MUST NOT become a runtime contract unless runtime or
bundler resolution matches it.

Node-native TypeScript MAY run bounded repository scripts only when syntax is
erasable and configuration is compatible. It MUST NOT replace package builds,
declaration emit, or typecheck.

## Tests and coverage

- Vitest is the default unit/integration runner.
- Workspaces use Vitest `projects`, not a deprecated workspace file.
- `just test` runs the deterministic default suite.
- Credentialed, browser-farm, network, long-running, and shared-environment tests
  use separately named commands.
- A published library tests its public entry point at the minimum supported and
  preferred Node lines; an application tests its exact deployed runtime.
- V8 coverage is the default when coverage is selected.
- Numeric coverage thresholds belong to product quality policy, not this
  language profile.

## pnpm workspace

- `packageManager` MUST declare the exact pnpm version and any
  `devEngines.packageManager` constraint MUST accept that same version.
- pnpm MUST NOT download or select the Node runtime; mise remains the runtime
  owner.
- A multi-package Node dependency graph MUST use one pnpm workspace with
  `pnpm-workspace.yaml` and `pnpm-lock.yaml` at that workspace root.
- Independent Node dependency graphs MAY retain separate project or workspace
  roots and locks when they do not use cross-root `workspace:` dependencies and
  each root independently satisfies exact-manager and frozen-install rules.
- Internal dependencies MUST use `workspace:`.
- Repeated third-party versions MAY use the default pnpm catalog. Named catalogs
  are reserved for an intentional compatibility or migration matrix.
- Workspace cycles MUST be rejected.
- Every package owns its dependencies, module type, artifact type, and
  build/typecheck/test contract.
- A deployable workspace package MAY use framework output or `pnpm deploy` to
  create an isolated portable artifact when its delivery profile validates that
  output.
- Turborepo or Nx is conditional on measured graph, affected-execution, or
  remote-cache needs; pnpm workspace alone is sufficient by default.

## Library and publishing

Every library distributed outside its workspace:

- MUST declare its actual `name`, `type`, `exports`, `types`, `files`,
  `sideEffects`, version, repository, license, and Node support range;
- MUST generate declarations and define map policy;
- MUST build, create a real tarball, inspect contents, and pass fresh
  install/import consumer smoke;
- MUST keep build, pack, validate, and publish as explicit stages; and
- MUST NOT hide publication mutation in a general lifecycle or quality command.

For registry/external packages:

- `publint` is a SHOULD;
- Are the Types Wrong is a conditional MUST for declarations, conditional
  exports, dual packages, or multiple module consumers;
- ESM-only packages test an ESM consumer and type resolution;
- dual packages test both import and require/type resolution;
- registry authentication is supplied only through a trusted repository-local
  `.npmrc` contract or CI secret injection and MUST NOT be committed as a token;
- npm OIDC trusted publishing is the default where supported;
- supported public npm packages MUST generate provenance;
- publish MUST run only from an immutable release ref through an approved
  workflow; local-developer and pull-request-origin publish are prohibited; and
- a long-lived token requires a scoped, rotated, expiring high-risk exception.

An internal workspace-only package does not require registry metadata, OIDC,
provenance, publint, or ATTW. Its build, typecheck, and actual workspace consumer
tests are authoritative until the distribution boundary changes.

## Commands

| Command | Meaning |
| --- | --- |
| `init` | Exact Node/pnpm bootstrap and frozen install |
| `format` / `format-check` | Prettier write/read |
| `lint` / `lint-fix` | ESLint typed read/fix |
| `typecheck` | Artifact compiler gate |
| `test` | Deterministic Vitest or approved runner |
| `build` | Artifact-owner clean build |
| `package-check` | Applicable library tarball/type/consumer validation |
| `check` | format-check + lint + typecheck + test |
| `ci` | check + clean build + applicable package-check |

Rule IDs: `DT-NODE-*`, plus common `DT-CMD-*`, `DT-TOOL-*`, and `DT-DEP-*`.
