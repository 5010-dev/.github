# Adopting the Developer Tooling Standard

This guide helps a new or newly buildable repository adopt the
[Developer Tooling Standard](../standards/developer-tooling/README.md). It is
informative; the standard, profiles, rule catalog, and schemas remain
normative.

Adoption creates a repository-local executable contract. It does not make the
repository a reference implementation and does not add its status to a central
registry.

For a new repository, use the
[Golden Path bootstrap guide](./bootstrap-new-repository.md) to select and
verify the exact implementation release, preview full starter materialization,
and connect repository-local validation. An existing repository uses the
[migration guide](./migrating-developer-tooling.md) and the release's explicit
`adoption` mode for its first generated control-plane baseline. It does not use
the new-repository starter as a source migration.

## 1. Classify the repository

Choose the independently composable axes that actually apply:

- language and IaC profiles;
- artifact types such as service, library, CLI, container, infrastructure, or
  documentation; and
- capabilities such as format, lint, typecheck, test, build, package, publish,
  coverage, fuzz, dependency automation, cache, or released-artifact handling.

Do not declare a capability to obtain a green no-op. Archived, generated-only,
asset-only, or non-buildable repositories may use the standard's explicit
not-applicable path.

## 2. Record versioned metadata

Create `.github/golden-path.yaml` from the
[metadata schema](../standards/developer-tooling/schemas/golden-path-metadata-v1.schema.json).
Record the exact standard, contract, and stable asset bundle versions. When the
approved implementation generates this file, preserve it as a whole generated
asset instead of editing it by hand.

Metadata describes applicable policy. It does not store repository names,
teams, current commits, pull requests, rollout status, or product version.

An existing repository's adoption request declares each component's actual
capabilities explicitly, including an empty array when none apply. It also
declares the production or release representative targets the repository
really supports, with at least one `primary` or `secondary` target. A target is
not inferred from a CI runner, profile, or successful compilation. The
generator aggregates these request declarations into metadata; it does not
inspect existing code and invent support claims.

Separately inventory the operational project or workspace root for every
selected native profile. When those roots match generated artifact component
paths, keep the inferred compact model. When workspaces are shared across
artifacts, different profiles share one directory, or one profile has several
independent dependency graphs, create
`.github/golden-path-native-roots.yaml` from the
[native-root schema](../standards/developer-tooling/schemas/golden-path-native-roots-v1.schema.json).
Each entry records only a stable ID, repository-relative path, and native
profiles. Do not copy artifact types or capabilities into the root declaration,
and do not edit generated `.github/golden-path.yaml` to describe As-built root
layout.

## 3. Establish the toolchain and dependencies

Apply the common contracts before profile details:

1. select one runtime owner for each toolchain;
2. pin supported exact runtime and tool versions;
3. commit native manifests and required locks or integrity records;
4. make dependency preparation locked or frozen in CI; and
5. remove competing managers for the same dependency surface.

Use the selected profile's native authority:

- Node.js and generic tool versions through mise, with pnpm for packages;
- Python and Python dependencies through uv;
- Go through mise with Go modules;
- Rust through rustup with Cargo;
- Zig through mise when the Zig profile applies; and
- the selected IaC engine plus its host-language profile.

## 4. Implement the root command contract

Add a root Justfile with truthful `init`, `check`, and `ci` commands. Keep it as
a stable façade over native commands. Extract cohesive implementation into
imports, namespaced modules, or repository-local scripts as complexity grows.

`ci` is deterministic, non-interactive, fail-closed, and non-mutating. Deploy,
destroy, state repair, and other shared-state operations remain outside the
base command.

## 5. Add profile and artifact gates

Implement every declared capability using the applicable language or IaC
profile. Add artifact-specific validation only when the artifact exists:

- packed output for published libraries and CLIs;
- representative platform lanes for supported binaries and public packages;
- stateful delivery outcomes for IaC mutation; and
- SBOM or provenance controls for the released-artifact tiers that require
  them.

The Golden Path does not require irrelevant commands, a universal platform
matrix, a Dev Container, automatic publishing, or every available security
adapter.

## 6. Materialize shared implementation

Use the approved generator, updater, or immutable distribution bundle when it
exists. Commit reviewable generated configuration and record its exact asset
bundle version. Do not fetch and execute mutable shared content in routine
local or CI commands.

Repository-native files remain the executable As-built authority. Shared
implementation does not redefine the standard.

Use the materialization path that matches the repository state:

- `bootstrap` creates a complete starter for a new repository;
- `adoption` creates the first Golden Path control-plane baseline for an
  existing repository; and
- `upgrade` updates a repository only after a generated asset inventory has
  been committed.

The `golden-path-generator-request/v1` adoption baseline contains the canonical
request, generated metadata, generated asset inventory, immutable bootstrap
script, and thin caller workflow. It does not create or replace source entry
points, native manifests or locks, mise or Just configuration, dependency
automation, or repository-specific build, smoke, release, deployment, and
state-management behavior. Generate it into a separate empty candidate and
integrate the reviewed files through the repository's own contribution flow.

Materialization plans are command output and external review evidence; the
candidate does not contain `golden-path-plan.json`. If an existing file
collides with a generated control-plane path, review the two files deliberately.
Do not rewrite the generated asset inventory or digest to bless
repository-local bytes. Either adopt the generated file, move local behavior
outside the managed path where the contract permits, or retain an intentional
customization knowing that a later upgrade must report and resolve the
conflict.

## 7. Validate and review

Run the repository root gate:

```bash
just ci
```

Run the version-compatible Golden Path checker separately. The quality workflow
runs `just ci` once; the structural conformance workflow MUST NOT run it again.
Use the default concise text or job summary for actionable findings. The
complete JSON result remains the canonical machine output and may be retained
when repository evidence policy needs it; routine passing runs do not require
a duplicate artifact. Request exhaustive passing and skipped detail only for
diagnosis.

Review manual and hybrid rules using durable evidence rather than interpreting
a structural green result as proof of runtime, hosting-plan, advisory, release,
or deployment state.

If an applicable MUST cannot be met, add the minimum schema-valid, approved,
expiring exception. High-risk deviations also require remediation tracking and
compensating controls. A SHOULD deviation does not require an exception.

## Completion

Adoption is complete for the repository when:

- metadata matches native evidence;
- base and declared capability commands are real and pass;
- exact toolchain and dependency authority is committed;
- required artifact and risk-specific outcomes are satisfied;
- exceptions are valid and time-bounded; and
- repository documentation links to the central standard for normative rules.

The owning repository records this completion in its own work item or canonical
documentation. The central standard does not track migration progress.
