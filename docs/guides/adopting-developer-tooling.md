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
verify the exact implementation release, preview materialization, and connect
repository-local validation. Existing repositories continue with the migration
guide after this policy classification.

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
Record the exact standard, contract, and stable asset bundle versions.

Metadata describes applicable policy. It does not store repository names,
teams, current commits, pull requests, rollout status, or product version.

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

## 7. Validate and review

Run the repository root gate:

```bash
just ci
```

Run the version-compatible Golden Path checker when available. Review manual
and hybrid rules using durable evidence rather than interpreting a structural
green result as proof of runtime, hosting-plan, advisory, release, or
deployment state.

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
