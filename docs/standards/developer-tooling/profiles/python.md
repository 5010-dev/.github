# Python profile

- Status: Accepted
- Profile ID: `python`
- Standard version: `2026.07`

uv owns Python project setup, interpreter selection, environments, dependency
resolution, locking, and tool execution. Packaging backends and native system
toolchains retain separate responsibilities.

## Runtime and metadata

- New projects use preferred Python 3.14 and commit an exact `.python-version`.
- `pyproject.toml#requires-python` declares the actual application runtime or
  validated library consumer range.
- Applications use one exact production runtime; libraries test the minimum and
  preferred supported minors.
- `pyproject.toml` uses PEP 621 metadata.
- Runtime dependencies, published optional features, and PEP 735 development
  groups MUST be separated.
- `uv.lock` MUST be committed.
- Regular CI uses `uv lock --check`, `uv sync --locked`, and applicable
  `uv run --locked`.
- A project-local `.venv` is excluded from version control; system Python is not
  modified.
- Named private or accelerator indexes use explicit package association and
  safe index priority. Credentials MUST NOT enter manifests or locks.
- Exact uv and quality-tool versions are resolved through the repository lock
  and release manifest.
- Build frontend/backend versions are bounded in `build-system` metadata and
  resolve exactly in CI. Pre-1.0 tools and tools with material minor-version
  behavior MUST NOT be followed through an unbounded major range.

A library's consumer dependency range MUST NOT be replaced with exact
transitive versions from its application/development lock.

## Quality stack

### Ruff

Ruff is the required formatter and linter for a new project.

- `ruff format --check` and `ruff check` are read-only gates.
- `ruff format` and an explicit safe-fix command write source.
- The baseline uses a curated stable rule set, not `ALL`, preview rules, or
  unsafe fixes.
- `target-version` is derived from runtime support and `requires-python`.
- Ruff's exact required version prevents formatting drift.
- A second linter is conditional on a missing domain capability and MUST NOT
  duplicate responsibility without reason.

### Type checking

Exact mypy 2.x is the required default. Configuration starts from a strict
baseline with narrow module/framework exceptions.

Global `ignore_missing_imports`, blanket `type: ignore`, and excluding an
untyped production package are not defaults. Missing types are addressed by
stubs, typed adapters, then narrow overrides.

Pyright is a conditional alternative when Node toolchain/editor parity,
standards behavior, or performance justifies it. Both are not universally
required. Astral ty is evaluation-only until stable, compatible with typing
fixtures, and ready for required use.

### Tests and coverage

- Exact pytest 9.x is the default test runner.
- Test paths and markers are explicit and unknown markers fail.
- Flaky retry requires a narrow owner, cause/tracking, and expiry; retry success
  MUST NOT be reported as a clean pass.
- The profile supports a branch-coverage command and machine-readable
  coverage.py artifact.
- Coverage artifact retention is a SHOULD and becomes a conditional MUST for
  product risk, external release, or a separate quality policy.
- No universal numeric threshold is defined here.

## Commands

| Command | Meaning |
| --- | --- |
| `init` | Exact uv and locked dependency-group sync |
| `format` / `format-check` | Ruff write/read |
| `lint` / `lint-fix` | Ruff read/safe fix |
| `typecheck` | Exact locked mypy or approved alternative |
| `test` | Exact locked pytest |
| `build` | Selected artifact profile clean build |
| `package-check` | Applicable metadata, archive, install, import, and wheel checks |
| `check` | format-check + lint + typecheck + test |
| `ci` | check + applicable clean build/package matrix |

An unavailable capability MUST NOT be represented by a successful no-op.

## Artifact profiles

| Artifact | Default | Validation |
| --- | --- | --- |
| Non-package script/internal one-off | No build system; MAY set `tool.uv.package = false` | Locked run, quality, deployment smoke |
| Installable app/service/CLI | `src/`, explicit backend; prefer `uv_build` for pure Python | Exact runtime, wheel/entry-point/runtime smoke |
| Published pure Python library | PEP 621, `src/`, bounded-minor `uv_build` | Support matrix, sdist→wheel, metadata, isolated install/import |
| Flexible pure Python package | Hatchling conditional | Layout/hook fixtures and package checks |
| Rust extension | maturin and appropriate binding | Native wheel matrix and isolated import |
| C/C++/Fortran extension | scikit-build-core and CMake | Native wheel, linkage, and ABI smoke |
| Existing legacy package | Existing backend as compatibility | Migration evidence and equivalent package checks |

An installable application/library uses `src/` to avoid accidental checkout
imports. A simple non-package script need not add packaging ceremony.

Published package validation MUST:

1. build sdist and wheel without local source overrides;
2. rebuild a wheel from the sdist;
3. inspect metadata and archive contents;
4. install the wheel into a clean isolated environment; and
5. exercise imports, public entry points, support minors, and target-platform
   smoke.

## Workspace and native boundary

A uv workspace is appropriate only when members share a compatible Python range,
dependency graph, and environment. It uses one root lock and explicit workspace
sources. Conflicting runtime, dependency, accelerator, or deployment
environments remain independent projects.

A shared uv environment does not prove workspace-member dependency isolation.
CI MUST verify that each member imports, checks, tests, and packages only from
its declared dependencies. Jobs and runtime images install only the locked
dependency groups their artifact needs; they MUST NOT install every development
group by default.

uv does not own compilers, C/C++/Rust libraries, CUDA/ROCm, OS packages,
immutable container bases, or platform repair tools. Prebuilt wheels are
preferred. Source builds retain PEP 517 isolation; disabling isolation requires
a package/version-scoped exception.

Native releases build and test their declared CPython/OS/architecture matrix and
apply the platform's wheel repair/audit tool. Build jobs executing arbitrary
package code are separated from upload credentials.

CUDA, ROCm, and CPU dependency variants MUST be selected deterministically by a
named index, marker, or profile input. CI and production locks MUST NOT change
their dependency graph through host-driver auto-detection.

## Publishing

Applications/services do not publish to a package index by default.
`Private :: Do Not Upload` is intent metadata, not an upload control. Workflow
permissions and a target-repository allowlist MUST prevent an application or
service from being uploaded to a package index.

A published library:

- builds once from a clean locked checkout and promotes the validated artifact;
- uses package-index OIDC trusted publishing where supported;
- records sdist/wheel digests and source/build provenance;
- supplements uv upload with a separate signed provenance step when necessary;
  and
- never rebuilds or overwrites an existing version.

Long-lived credentials require a bounded high-risk exception.

Pixi/Conda is not a second base dependency owner. A scientific/native
environment requiring Conda-only packages or multi-language binary locking
needs a separately approved conditional profile.

Rule IDs: `DT-PY-*`, plus common `DT-CMD-*`, `DT-TOOL-*`, and `DT-DEP-*`.
