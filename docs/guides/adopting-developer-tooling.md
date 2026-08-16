# Adopting the Developer Tooling Standard

Adoption is the existing-repository journey of the
[Developer Tooling Golden Path](../golden-path/README.md). It means implementing the
[Developer Tooling Standard](../standards/developer-tooling/README.md) through
repository-owned native files and workflows. It does not install or follow a
central executable, release, locator, template, or approval queue.

## 1. Establish applicability

Read the base standard and only the language or IaC profiles that match actual
source and manifests. Do not create metadata to claim unused profiles,
artifacts, or capabilities.

Use the [stack defaults](../golden-path/stack-defaults.md) to choose the closest
supported starting point. Inventory the current repository before copying an
example; adoption preserves working native authorities instead of replacing
them with a uniform central layout.

## 2. Preserve native authorities

Use the ecosystem's native manifest, lock or integrity record, and toolchain
selector. Keep one operational owner for each dependency surface. Existing
repository-owned `release-units.json` remains authoritative for its release
units.

If operational native roots are ambiguous, record only their stable ID,
repository-relative path, and native profiles in
`.github/golden-path-native-roots.yaml` using the
[native-root schema](../standards/developer-tooling/schemas/golden-path-native-roots-v1.schema.json).
Do not invent package mappings or component-path impact rules.

## 3. Implement repository commands

Provide truthful root `just init`, `just check`, and `just ci` commands.
The root Just graph delegates to repository-native tools. `just ci` is
deterministic, non-interactive, fail-closed, and non-mutating.

## 4. Own CI, release, and security behavior

The repository owns its canonical quality workflow, exact runner and action
pins, release flow, Dependabot or Renovate configuration, and security routing.
Run canonical CI once. A central conformance job does not replay it.

Prefer GitHub-native controls or ecosystem-native validation. Add a custom
validator only after a separate accepted decision proves repeated errors,
off-the-shelf insufficiency, a favorable operating-cost comparison, a named
owner, and a removal condition.

## 5. Record exceptions deliberately

Use canonical repository documentation for a bounded, owned, approved,
expiring deviation. Reference the exact normative document and section. The
central repository does not maintain a machine rule catalog, consumer registry,
or exception queue.

## Completion

Adoption is complete when native manifests and locks, toolchain ownership,
truthful commands, canonical CI, required release behavior, and any accepted
exceptions are reviewable in the owning repository.
Before declaring completion, reconcile every applicable normative profile
requirement with repository As-built source or an accepted exception, and verify
the documented first-run bootstrap from the declared platform prerequisite
rather than inferring either result from a passing gate.
Link to the central standard; do not copy or materialize a managed central
footprint. Apply the
[release-readiness checklist](../golden-path/release-readiness.md) only to real
repository boundaries, and keep its evidence in the repository's normal pull
request, release, and deployment records.
