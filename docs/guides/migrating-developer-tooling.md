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

## 1. Inventory the executable As-built

Inspect:

- runtime selectors and installer ownership;
- native manifests, locks, workspace files, and generated dependency records;
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

## 3. Choose safe sequencing

A useful default order is:

1. metadata that truthfully describes the current target;
2. one toolchain owner and exact supported versions;
3. native manifests, locks, and frozen preparation;
4. root Just commands over existing real checks;
5. profile quality and artifact gates;
6. shared asset materialization and immutable references;
7. dependency, vulnerability, cache, supply-chain, and platform controls; and
8. removal of superseded selectors, locks, scripts, and temporary exceptions.

Repository constraints may require a different order. A toolchain or lock
migration should not be mixed with unrelated behavior changes when separation
improves review and rollback.

## 4. Preserve operational authority

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

## 5. Handle unavoidable deviations

Fix MUST gaps in the migration when practical. When a bounded MUST deviation
must remain, create a schema-valid exception with an owner, durable approval,
risk class, and expiry. Add tracking, risk, controls, and independent approval
only for high-risk deviations.

Do not create exceptions for SHOULD guidance, inapplicable capabilities, or
work that is already conformant under an equivalent allowed adapter.

## 6. Verify and hand off

Run native checks and `just ci` from a clean checkout. Then run the compatible
Golden Path checker and review manual or external evidence separately.

The repository owner closes its migration work only after the executable
change, locks, generated files, documentation links, exceptions, and bounded
verification agree. Future migrations are created by the repository owner as
needed; they are not children required for closing the central standard issue.
