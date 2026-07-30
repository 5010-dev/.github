# Rust profile

- Status: Accepted
- Profile ID: `rust`
- Standard version: `2026.07`

rustup and Cargo are the Rust operational owners. mise prepares Just and
external support CLIs but MUST NOT repin Rust or Cargo dependencies.

## Toolchain authority

The initial preferred exact stable is Rust 1.97.1. A repository commits:

```toml
[toolchain]
channel = "1.97.1"
profile = "minimal"
components = ["rustfmt", "clippy"]
```

Host-external targets are listed only when the artifact supports them.
Moving `stable`, moving `nightly`, user overrides, and global defaults MUST NOT
be repository authorities.

Authority order is:

1. `rust-toolchain.toml` for exact compiler, Cargo, components, and targets;
2. `Cargo.toml` for edition, resolver, MSRV, features, and artifact metadata;
3. root `Cargo.lock` for dependency resolution;
4. root Just commands for composition; and
5. Golden Path metadata/release manifest for conditional support CLIs and dated
   nightly lanes.

rust-analyzer is an optional editor capability, not a merge gate.

## Package, workspace, and lock

New packages use Edition 2024, explicit `rust-version`, resolver 3, and a
committed root `Cargo.lock`. All applicable validation, build, and package
commands use `--locked`.

Applications/services/internal CLIs align `rust-version` with the preferred
development line by default. A published library MAY declare a lower consumer
MSRV only when:

- every published package declares it;
- the edition and dependency graph load and build there;
- supported targets/features run in an exact MSRV lane;
- preferred stable validates the same contract; and
- MSRV change policy and consumer impact are documented.

A lower library MSRV does not extend organization support for development
toolchains.

## Format, analysis, and lint

Required base commands are:

```text
cargo fmt --all -- --check
cargo check --workspace --all-targets --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
```

`rustfmt.toml` declares Edition/Style Edition 2024 and stable options only.
Clippy uses compiler warnings plus default `clippy::all`; full `pedantic`,
`restriction`, or `nursery` categories are not enabled wholesale.

Additional lints are named and justified. Suppressions name the lint and give a
nearby reason. Workspace-wide `allow(warnings)`, broad `clippy::all` allows, or
CI `RUSTFLAGS` that hide warnings are prohibited.

`cargo fix`, Clippy fix, edition migration, and formatting writes are explicit
source-changing commands and MUST NOT run within `check` or `ci`.

## Safety profile

Every Rust project declares `safe-only` or `unsafe-permitted`.

### `safe-only`

- Uses `unsafe_code = "forbid"` at the relevant crate/workspace policy.
- Introducing unsafe requires an explicit profile change and justification.

### `unsafe-permitted`

- Declares packages/modules, capability, and owner.
- Uses `unsafe_op_in_unsafe_fn = "deny"`.
- Requires explicit unsafe blocks and nearby `SAFETY:` rationale.
- Documents public unsafe caller/implementor contracts.
- Enables named undocumented-unsafe and missing-safety-doc lints.
- Uses exact dated-nightly Miri where supported.
- Uses target integration tests, sanitizer, or native validation when Miri
  cannot cover the path.

A mixed workspace keeps safe crates forbidden and grants permission narrowly.
Miri never replaces the stable base toolchain, and moving nightly is prohibited.

## Tests, features, fuzz, and coverage

Base tests use `cargo test --workspace --locked`.

Feature validation includes applicable default, no-default, all-features, and
bounded selected combinations. Mutually exclusive features use cargo-hack or an
equivalent declared matrix rather than an invalid universal `--all-features`.

nextest is conditional on scale, isolation, sharding, timeout, or reporting. It
uses an exact version and repository configuration, retains a separate doctest
lane, defaults retries to zero, and exposes a known-flaky retry as non-clean
evidence.

Coverage MAY use exact cargo-llvm-cov and produces LCOV or JSON; no universal
percentage applies.

cargo-fuzz is conditional for untrusted or security-sensitive inputs and uses
an exact tool plus dated nightly, bounded scheduled execution, committed seed
corpus, crash retention, and deterministic regression conversion.

## Commands

| Command | Meaning |
| --- | --- |
| `init` | Exact rustup toolchain/components/targets/support CLI and locked fetch |
| `format` / `format-check` | Stable rustfmt write/read |
| `typecheck` | Locked workspace/all-target check |
| `lint` | Toolchain Clippy with warnings denied |
| `test` | Native Cargo unit/integration/doctest |
| `test-features` | Declared feature matrix |
| `test-msrv` | Applicable published-library MSRV |
| `test-miri` | Applicable exact dated-nightly Miri |
| `fuzz` | Bounded explicit fuzz capability |
| `coverage` | Machine-readable coverage artifact |
| `doc` | Public-feature rustdoc warning gate |
| `build` | Declared artifact/target/profile |
| `package-check` | Artifact smoke or extracted crate verification |
| `check` | format-check + typecheck + lint + native test |
| `ci` | check + applicable feature/MSRV/doc/build/package matrix |

## Artifact contracts

Applications/services/internal CLIs declare `publish = false`, exact target,
features, release profile, linker/native inputs, and artifact smoke. LTO,
codegen units, stripping, panic, and debug info are product decisions. Service
containers validate the target image rather than treating a host Cargo build as
the production artifact.

Published crates:

- include required package metadata;
- gate public docs with warnings denied;
- run `cargo package --locked` and extracted-package verification;
- MUST NOT use `--allow-dirty` or `--no-verify` normally;
- test path/workspace dependency transformation for external consumers;
- test declared MSRV and preferred stable;
- MAY use exact cargo-semver-checks as a supplement; and
- use crates.io OIDC Trusted Publishing when available.

External support CLIs use exact immutable assets and digests. A source fallback
uses exact `cargo install --locked --version ...` into a repository tool root,
not global Cargo home.

Rule IDs: `DT-RUST-*`, plus common `DT-CMD-*`, `DT-TOOL-*`, and `DT-DEP-*`.
