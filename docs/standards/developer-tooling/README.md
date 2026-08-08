# Developer Tooling Standard

- Status: Accepted
- Standard version: `2026.08.4`
- Contract version: `golden-path/v1`
- Last reviewed: 2026-08-09

This standard defines the organization Golden Path for developer tooling,
repository-local build and quality commands, language and Infrastructure as Code
profiles, dependency hygiene, conformance, and time-bounded exceptions.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this standard are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14) when, and only when, they appear
in all capitals.

## Authority

This directory is the normative authority for organization Developer Tooling
rules and profiles. The machine-readable
[rule catalog](./rules/catalog.v1.json) and [schemas](./schemas/README.md) are
reviewed in the same change boundary as the human-readable rules.

The authority order is:

1. this standard and its versioned rule and schema sources;
2. a released immutable snapshot of this standard consumed by shared tooling;
3. repository-local Golden Path metadata, explicit native-root declarations,
   and approved exceptions;
4. repository-local native manifests, locks, toolchain selectors, commands, and
   caller workflows as the executable As-built authority; and
5. CI results and optional hosting-platform enforcement as current evidence.

Templates, generators, checkers, reusable automation, issue descriptions, and
repository implementations do not redefine this standard. A repository is an
adoption and migration unit, not a reference implementation for organization
rules.

## Applicability

The base contract applies to active, buildable, organization-managed
repositories, including applications, services, libraries, CLIs, buildable
tooling, and IaC.

An archived or generated-only mirror, asset-only repository, or documentation
repository with no executable validation contract MAY declare
`not-applicable`. A documentation repository with deterministic lint, link, or
contract checks MAY adopt the `documentation` profile.

A repository MUST NOT use successful no-op commands to appear conformant with
an inapplicable language, artifact, or capability. Applicability is declared in
`.github/golden-path.yaml` and checked against the repository's native files.

## Contract composition

Golden Path conformance is a composition of:

- the organization base command, toolchain, dependency, distribution,
  conformance, and exception contracts;
- one or more [language or IaC profiles](./profiles/README.md);
- one or more artifact types such as `service`, `library`, `cli`,
  `infrastructure`, or `documentation`; and
- declared capabilities such as format, lint, typecheck, test, build, package,
  publish, coverage, fuzz, cache, or released-artifact handling.

Profiles and artifact types are separate axes. Identifiers such as
`node-typescript/service` MUST NOT be invented for every combination.

## Standard map

| Document | Normative responsibility |
| --- | --- |
| [Command contract](./command-contract.md) | Root `just` façade and local/CI semantics |
| [Task runner](./task-runner.md) | Just import, module, script, and namespace boundaries |
| [Toolchain management](./toolchain-management.md) | `mise`, native runtime owners, exact pins, and EOL |
| [Dependency management](./dependency-management.md) | Native managers, manifests, locks, and frozen CI |
| [Dependency operations](./dependency-operations.md) | Root binding, owner/release routing, PR budget, security route, preview, and live report contracts |
| [Distribution](./distribution.md) | Materialization, immutable references, shared implementation, and release identity |
| [Build hygiene](./build-hygiene.md) | Dependency automation, vulnerability, cache, SBOM, provenance, platform, and Dev Container rules |
| [Runtime support](./runtime-support.md) | Lifecycle, organization disposition, migration, and initial support catalog |
| [Conformance](./conformance.md) | Metadata, rule evaluation, output, exit codes, and enforcement states |
| [Exceptions](./exceptions.md) | Scoped, approved, expiring deviations |
| [Profiles](./profiles/README.md) | Node.js/TypeScript, Python, Go, Rust, Zig, and IaC contracts |
| [Rules](./rules/README.md) | Stable rule ID lifecycle and machine catalog |
| [Schemas](./schemas/README.md) | Versioned metadata, exception, output, catalog, and runtime-support schemas |

## Repository-local contract

An applicable repository records at least:

```yaml
schemaVersion: golden-path-metadata/v1
contractVersion: golden-path/v1
standardVersion: "2026.08.4"
assetBundleVersion: "1.0.0"
profiles:
  - node-typescript
artifactTypes:
  - service
capabilities:
  - format
  - lint
  - typecheck
  - test
  - build
```

This example shows the current normative contract shape, not the version
implemented by every released checker. During a bounded publication lag, a
repository MUST keep the `standardVersion` implemented by the locator-selected
tooling release and MUST NOT hand-copy a newer value from this example. See
[version axes](./distribution.md#version-axes) for the ordered publication
rules.

The schema does not store repository names, teams, current commits, pull
requests, migration state, or a central conformance registry.

Artifact components describe what a repository builds or releases. Native
dependency roots describe where ecosystem managers own manifests, locks, and
locked preparation. A simple repository infers roots from its generated
components. A repository whose native roots do not match those component paths
MUST additionally declare
`.github/golden-path-native-roots.yaml` using
[`golden-path-native-roots/v1`](./schemas/golden-path-native-roots-v1.schema.json).
Each entry records only a stable root ID, repository-relative path, and native
profiles. That file is repository-owned As-built configuration and MUST NOT be
inserted into or replace whole-file generated metadata.

## Ownership planes

| Plane | Owns | Does not own |
| --- | --- | --- |
| Policy and discovery | This standard, rule/schema source, guides, ADRs, workflow-template discovery | Shared executable implementation or repository status |
| Shared implementation | Checker, generator/upgrader, template bundle, reusable action/workflow, fixtures, immutable releases | Normative rule meaning |
| Repository execution | Metadata, exceptions, materialized config, native manifests/locks, commands, caller workflows, current migration state | Organization policy |

The shared implementation's repository name and visibility are operational
locators, not normative identities. Generic tooling that passes disclosure
review SHOULD be public when that improves access from private consumers;
private or restricted distribution remains conformant when its trust boundary
requires it.

## GitHub Free private baseline

The standard MUST be fully usable by private repositories in a GitHub Free
organization.

- GitHub Actions, repository or organization secrets, OIDC, dependency graph,
  and Dependabot capabilities MAY be used where available.
- Protected branches, rulesets, required status checks, GitHub Environments and
  required reviewers, Dependency Review, and GitHub-native private artifact
  attestations MUST NOT be assumed to exist.
- A checker or CI job can fail a policy gate without proving that the hosting
  platform technically blocks a merge.
- Cloud IAM, exact OIDC trust, separated operator roles, bounded manual
  workflows, or external approval evidence MAY provide equivalent controls.
- Paid-plan features MAY strengthen an existing outcome, but MUST NOT become
  the normative authority or the only conforming implementation.

## Decision traceability

| Decision | Final authority |
| --- | --- |
| GP-006 | [Command contract](./command-contract.md) and [task runner](./task-runner.md) |
| GP-007 | [Toolchain management](./toolchain-management.md) |
| GP-008 | [Dependency management](./dependency-management.md) and profile documents |
| GP-009 | [Distribution](./distribution.md) |
| GP-010 | [Conformance](./conformance.md), [exceptions](./exceptions.md), rules, and schemas |
| GP-011 | Ownership planes and [distribution](./distribution.md) |
| GP-012 | [Runtime support](./runtime-support.md) |
| GP-013 | [Node.js and TypeScript](./profiles/node-typescript.md) |
| GP-014 | [Python](./profiles/python.md) |
| GP-015 | [Go](./profiles/go.md) |
| GP-016 | [Rust](./profiles/rust.md) |
| GP-017 | [Zig](./profiles/zig.md) |
| GP-018 | [Infrastructure as Code](./profiles/infrastructure.md) |
| GP-019 | [Build hygiene](./build-hygiene.md) |
| GP-020 | Versioning in this document, [distribution](./distribution.md), and [conformance](./conformance.md) |
| GP-021 | [Dependency operations](./dependency-operations.md) and dependency schemas |

Product, service, library, and API release versioning is outside this standard.

## Adoption and migration

New repositories use the latest preferred standard and stable asset bundle.
Existing repositories adopt through repository-owned, reviewable work. The
standard does not maintain repository migration schedules or conformance
status.

`2026.08.4` completes the dependency evidence serialization accepted by
GP-021. It adds repository/default-branch identity, PR node and ref SHAs, check
rollups, alert identities, exact defer review fields, and source-bound report
identity that were incomplete in `2026.08.3`. The serialized contract remains
v1; no consumer had an immutable tooling release for the incomplete source.

`2026.08.3` adds the repository-owned dependency policy compiler contract. It
references existing native roots and release units, preserves repository-owned
canonical CI, keeps security routing independent from routine queue limits, and
keeps live queue state outside offline conformance. It does not create a second
release-unit system or a central approval queue.

`2026.08.2` completes the new-repository bootstrap ownership boundary. Only
the canonical request, metadata, managed inventory, bootstrap script, and
structural-conformance caller remain generator-managed. Source, onboarding,
native manifests and locks, mise/Just files, dependency automation, and the
repository quality workflow are repository-owned scaffold. Bootstrap quality
CI runs `just ci` once; independent conformance remains checker-only and
report-only. This is a compatible `golden-path/v1` correction and does not
require existing consumers to upgrade on locator movement alone.

`2026.08.1` narrows the caller-workflow contract so quality CI owns
repository execution through `just ci`, while structural conformance runs the
checker without repeating the quality graph. It also makes the shared tooling
support cadence and ECS checklist trigger explicit. These are compatible
corrections to `golden-path/v1`; they do not invalidate repositories or tooling
releases that implement `2026.08`.

`DT-CMD-005` and `DT-ASSET-007` retain their original meanings and retire in
`2026.08.1` without replacement. The quality/conformance execution split is a
workflow implementation contract, not a new consumer conformance rule.

- [Adopting the Developer Tooling Standard](../../guides/adopting-developer-tooling.md)
- [Bootstrapping a new repository](../../guides/bootstrap-new-repository.md)
- [GitHub hosting capability profile](../../guides/github-hosting-capabilities.md)
- [Migrating existing developer tooling](../../guides/migrating-developer-tooling.md)
- [ADR-0006: Adopt the organization Developer Tooling Golden Path](../../decisions/0006-adopt-developer-tooling-golden-path.md)
