# Zig profile

- Status: Accepted
- Profile IDs: `zig`, `zig-toolchain`
- Standard version: `2026.08.4`

Zig is conditional. It is enabled only for an intentionally adopted Zig
artifact with an owner, supported targets, and maintenance capacity.

## Lifecycle and upgrade

The initial comparison baseline is exact Zig 0.16.0. A coordinated release
reconfirms the latest stable patch and matching ZLS artifact before pinning.

Moving `master`, `nightly`, `latest`, and unbounded automatic minor upgrades are
prohibited. A compiler upgrade is a reviewed migration that checks:

- `build.zig`/ZON schema, hashes, and fingerprints;
- source, standard library, I/O, and C integration changes;
- target, libc, linker, and generated bindings;
- formatting, tests, and fuzz corpora;
- ReleaseSafe/selected-production artifact smoke; and
- matching ZLS/editor behavior.

## Authority

1. `mise.toml`/release manifest select an exact verified Zig asset.
2. `build.zig.zon` owns package identity, minimum Zig, fingerprint,
   dependency URL/hash, and distributable paths.
3. `build.zig` owns the build graph, target, optimization, artifacts, generated
   source, and tests.
4. root Just commands expose stable organization semantics.

ZLS uses the same minor line and an exact verified release. It is editor-only
and not a CI authority.

## Package and generated surface

A Zig package commits root `build.zig` and `build.zig.zon`, an enum-literal
package name, fingerprint, exact minimum Zig line, immutable remote dependency
URLs/revisions with content hashes, and explicit distributable paths.

No organization pseudo-lockfile is added. `.zig-cache`, `zig-out`, and
`zig-pkg` are ignored generated surfaces. Vendored/offline dependency bundles
require the common provenance, refresh, license, advisory, and cache contract.

`just init` fetches/verifies dependencies without shared/production mutation.
`check` and `ci` MUST NOT rewrite dependency hashes or declarations.

## Commands

| Command | Meaning |
| --- | --- |
| `init` | Exact verified Zig and optional ZLS; declared dependency fetch |
| `format` / `format-check` | Native `zig fmt` write/read |
| `typecheck` | Named compile-only build step covering declared roots |
| `test` | Named test step that actually runs test artifacts |
| `build` | Exact target/CPU/ABI/libc/optimization build |
| `fuzz` | Applicable bounded fuzz capability |
| `check` | format-check + compile analysis + test |
| `ci` | check + ReleaseSafe build + supported-target/artifact smoke |

An empty test, ignored failure, compile-only test step, or source-writing check
is nonconformant. A `build.zig` test step uses `addRunArtifact` or equivalent to
execute tests.

Per-test or per-suite timeouts MAY be selected from actual runner and resource
behavior, but MUST be bounded for required CI. Allocator-aware code uses
`std.testing.allocator` leak detection; code with an OOM contract adds a failing-
allocator test.

Native `zig fmt` is the only base formatter. No universal third-party linter is
required until an exact compatible maintained tool, deterministic output, rule
taxonomy, and suppression contract are approved.

## Safety and optimization

Debug validation and ReleaseSafe artifact build are the base. ReleaseFast or
ReleaseSmall requires performance/size evidence, safety-risk review,
Debug/ReleaseSafe validation retention, production-mode artifact smoke,
observability/rollback, and a reevaluation owner.

Broad `@setRuntimeSafety(false)` is prohibited. Narrow disablement requires a
measured reason, explicit invariant, tests, and an approved exception when it
affects a required profile.

Incremental compilation is disabled in required CI/release for this baseline.
It requires a later explicit profile change after upstream stability review.

## Targets and C integration

Repository metadata declares target triple, CPU baseline/features, ABI, libc,
linker, system libraries, and runner for supported artifacts. Compiler target
tier is not a product support promise.

The profile distinguishes:

- compile evidence for an exact supported target;
- semantic execution on a host/emulator/device/runner; and
- release artifact smoke.

C/C++ integration records headers, translated source, include paths, libc,
libraries, link inputs, and binding freshness in the build graph. New
integration SHOULD prefer reviewed translate-C or explicit bindings over new
deprecated import usage.

A C/C++ repository using `zig cc`/`zig c++` only selects `zig-toolchain`, not
the full language profile. It declares exact compiler, target, libc/headers,
flags, and artifact smoke without Zig formatter/ZLS/package requirements.

## Artifacts

Applications/services/CLIs record compiler, dependency hash graph, target,
optimization, linker/libc, build options, and artifact smoke.

Source libraries declare exact minimum Zig, explicit paths, immutable package
identity, and dependency hashes. A pre-1.0 minor compatibility promise is never
implicit.

A C ABI library additionally defines headers, symbols/calling conventions,
targets/libc, ABI tests, and consumer fixtures.

Fuzzing is risk-based, bounded, and scheduled. Crashes and minimized corpora are
reviewed and promoted to deterministic regression tests. Infinite or random
fuzzing MUST NOT run inside `just ci` or count as deterministic correctness
evidence. Generated documentation is conditional and not the only release
gate.

Rule IDs: `DT-ZIG-*`, plus common `DT-CMD-*`, `DT-TOOL-*`, and `DT-DEP-*`.
