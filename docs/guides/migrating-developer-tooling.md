# Migrating existing developer tooling

This guide describes repository-owned migration to the
[Developer Tooling Standard](../standards/developer-tooling/README.md). It is
informative and does not authorize a central bulk rewrite.

Existing implementations are useful evidence of current constraints and
working patterns. They do not become normative authority, and the central
standard does not name a repository as the implementation to copy.

## Migration principles

- Compare the executable As-built to the current standard and stable rule IDs.
- Preserve working product, release, deployment, and infrastructure ownership
  boundaries unless the owning contract explicitly changes them.
- Migrate in reviewable steps that leave truthful commands and locks.
- Do not add green placeholders, competing package managers, mutable remote
  fetches, or ceremonial files only to satisfy a structural check.
- Record repository-specific sequencing, blockers, owners, and evidence in the
  owning repository, not in the central standard.
- Existing repository work continues on its own schedule. Standard acceptance
  does not imply automatic migration or conformance.
- Do not run the full new-repository `bootstrap` materialization over an
  existing source tree.

## 1. Inventory the executable As-built

Inspect:

- runtime selectors and installer ownership;
- artifact component boundaries separately from native project and workspace
  roots;
- native manifests, locks, workspace files, and generated dependency records,
  including independent graphs for the same profile;
- root and CI commands;
- format, lint, typecheck, test, build, package, publish, and release paths;
- IaC static and stateful workflows;
- shared actions, workflows, scripts, templates, and mutable remote inputs;
- dependency update, vulnerability, cache, SBOM, provenance, and platform
  controls; and
- documented exceptions and hosting-plan assumptions.

This inventory establishes migration scope. It does not override the central
target contract.

## 2. Classify gaps by stable rule

For each applicable rule, record:

- current evidence;
- target outcome;
- whether the gap is structural, behavioral, external, or manual;
- risk and dependency order;
- the repository-owned change or accepted exception; and
- verification required to remove the gap.

Use profile, artifact, and capability applicability to avoid universalizing
conditional controls.

## 3. Establish the generated adoption baseline

First determine whether the repository already has a valid generated asset
inventory:

- Without `.github/golden-path-assets.json`, use `generate` with explicit
  `materializationMode: adoption` for the first baseline.
- With a committed, valid inventory and its canonical
  `.github/golden-path-request.json`, use `upgrade`; do not generate a second
  baseline.

If an inventory exists but its release identity, request digest, file digests,
or modes cannot be verified, stop and recover its provenance. An unverified
inventory authorizes neither `upgrade` nor replacement with a new baseline.

Use only the immutable stable release selected by the
[bootstrap locator](./golden-path-bootstrap.v1.json). Confirm that the release
locator declares `adoption` in `explicitMaterializationModes` and that its
published request schema supports the mode. If the selected release does not
support it yet, continue repository-local preparation but do not emulate it
with a development build or hand-edited metadata. A fabricated asset inventory
is not an adoption baseline.

Start from the validated
[existing-service adoption fixture](../../scripts/docs/fixtures/golden-path-adoption/existing-service.v1.json)
and replace every example value with the repository's real classification. The
request must:

- keep artifact component paths separate from native dependency roots;
- declare each component's real profiles and artifact types;
- declare each component's implemented capabilities exactly, including an
  explicit empty array when none apply; and
- declare real production or release representative targets, including at
  least one `primary` or `secondary` target, without inferring support from CI
  runners or compilation alone.

### Repository without a generated inventory

Preview the external adoption request first, then write only to a separate
empty candidate:

```bash
"$GOLDEN_PATH_BIN" generate \
  --request /path/to/adoption-request.json \
  --release-manifest "$RELEASE_MANIFEST"

"$GOLDEN_PATH_BIN" generate \
  --request /path/to/adoption-request.json \
  --release-manifest "$RELEASE_MANIFEST" \
  --write \
  --output /path/to/empty-adoption-candidate
```

### Existing adoption baseline

When the committed canonical request already selects `adoption`, use that
request for both the preview and the candidate:

```bash
"$GOLDEN_PATH_BIN" upgrade \
  --root /path/to/existing-repository \
  --request /path/to/existing-repository/.github/golden-path-request.json \
  --release-manifest "$RELEASE_MANIFEST"

"$GOLDEN_PATH_BIN" upgrade \
  --root /path/to/existing-repository \
  --request /path/to/existing-repository/.github/golden-path-request.json \
  --release-manifest "$RELEASE_MANIFEST" \
  --write \
  --output /path/to/empty-upgrade-candidate
```

### Legacy or bootstrap baseline changing to adoption

Do not use the legacy canonical request unchanged, because it retains implicit
bootstrap behavior. Create a separate reviewed adoption request from the
fixture, keeping the repository identity and real component classification,
then pass that external request to `upgrade`:

```bash
"$GOLDEN_PATH_BIN" upgrade \
  --root /path/to/existing-repository \
  --request /path/to/adoption-request.json \
  --release-manifest "$RELEASE_MANIFEST"

"$GOLDEN_PATH_BIN" upgrade \
  --root /path/to/existing-repository \
  --request /path/to/adoption-request.json \
  --release-manifest "$RELEASE_MANIFEST" \
  --write \
  --output /path/to/empty-adoption-upgrade-candidate
```

The source repository's canonical request remains unchanged during preview and
candidate construction. It is replaced by the candidate's generated canonical
request only when the reviewed adoption change is integrated.

For `golden-path-generator-request/v1`, the candidate's managed asset set
contains only the fixed Golden Path control-plane files:

- `.github/golden-path-request.json`;
- `.github/golden-path.yaml`;
- `.github/golden-path-assets.json`;
- `.github/workflows/developer-tooling.yml`; and
- `scripts/golden-path`.

The candidate also contains `golden-path-plan.json`; treat it as staging
evidence rather than managed repository configuration. Integrate the
control-plane files through the repository's normal review without copying
starter source, native manifests or locks, mise or Just configuration, or
product-specific smoke and release behavior.

If a control-plane path already exists, compare it with the candidate instead
of overwriting it mechanically. Preserve the generated inventory unchanged. A
deliberately customized managed file remains reviewable, but the next `upgrade`
will report it as a conflict that must be resolved; do not change the recorded
digest to hide that fact.

After the baseline is committed, later releases use `upgrade` with the
canonical request and a separate candidate. The inventory distinguishes
unchanged generated files from repository customization. Deleted managed files
and executable-mode changes are conflicts. When a prior bootstrap baseline is
changed to adoption, unchanged starter-only assets may be proposed for removal,
while customized retired assets must conflict and prevent candidate staging.
Review every proposed removal against repository ownership; never treat the
plan as authorization to delete product source, durable state, or operational
configuration.

## 4. Choose safe sequencing

A useful default order is:

1. a reviewed adoption request and generated control-plane baseline that
   truthfully describe the policy target;
2. a repository-owned `.github/golden-path-native-roots.yaml` only when actual
   dependency roots differ from generated component paths;
3. one toolchain owner and exact supported versions;
4. native manifests, locks, and frozen preparation;
5. root Just commands over existing real checks;
6. profile quality and artifact gates;
7. immutable shared references and control-plane integration;
8. dependency, vulnerability, cache, supply-chain, and platform controls; and
9. removal of superseded selectors, locks, scripts, and temporary exceptions.

Repository constraints may require a different order. A toolchain or lock
migration should not be mixed with unrelated behavior changes when separation
improves review and rollback.

The native-root sidecar records only stable IDs, repository-relative paths,
and native profiles. Profiles with disjoint dependency authority MAY share a
path, while independent roots for one profile remain separate. Preserve
whole-file generated metadata and its asset digest; repository-specific root
layout belongs in the sidecar rather than a custom metadata extension.

## 5. Preserve operational authority

The Developer Tooling Standard owns authoring and validation boundaries, not
all production operations.

- A root `ci` migration does not add deployment.
- The IaC profile does not silently replace an accepted deployment workflow,
  approval model, cloud role, state owner, or recovery procedure.
- A package-manager migration does not silently change public package
  compatibility.
- Shared templates do not overwrite repository-local implementation without a
  reviewed materialized diff.

Changes to those authorities require their own owning decision and
verification.

## 6. Handle unavoidable deviations

Fix MUST gaps in the migration when practical. When a bounded MUST deviation
must remain, create a schema-valid exception with an owner, durable approval,
risk class, and expiry. Add tracking, risk, controls, and independent approval
only for high-risk deviations.

Do not create exceptions for SHOULD guidance, inapplicable capabilities, or
work that is already conformant under an equivalent allowed adapter.

## 7. Verify and hand off

Run native checks and `just ci` from a clean checkout. Then run the compatible
Golden Path checker and review manual or external evidence separately.

The repository owner closes its migration work only after the executable
change, locks, generated files, documentation links, exceptions, and bounded
verification agree. Future migrations are created by the repository owner as
needed; they are not children required for closing the central standard issue.
