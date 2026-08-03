# Release and Versioning Standard

- Status: Accepted
- Standard version: `2026.08`
- Last reviewed: 2026-08-03

This standard defines how the `5010-dev` organization versions, identifies,
publishes, evolves, and retires software and Infrastructure as Code artifacts.
It separates compatibility signals from exact source, artifact, and deployment
identities so that releases remain understandable and auditable without making
one repository, registry, workflow, or tool the organization authority.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this standard are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14) when, and only when, they appear
in all capitals.

The standard version uses Calendar Versioning in `YYYY.MM` form. A later
normative change in the same month appends a positive sequence such as
`YYYY.MM.1`. Editorial changes that do not change rule meaning retain the
version. Future machine-readable schemas, checkers, and automation artifacts
MUST retain their own compatibility versions and immutable release identities.

## Authority

This directory is the normative authority for organization release and
versioning rules. Its documents define artifact profiles, selection criteria,
release evidence, compatibility lifecycle, automation boundaries, and
exceptions.

The authority order is:

1. this standard and an applicable native ecosystem specification;
2. repository-local version policy and release-unit declarations;
3. repository-native manifests or release metadata as the human-readable
   version source;
4. the immutable source revision and exact registry, artifact, or deployment
   identity as publication evidence; and
5. repository-local release history, executable automation, and current
   support-state records.

When an ecosystem defines more specific version parsing, dependency resolution,
major-version namespace, prerelease ordering, yanking, or retraction semantics,
repositories MUST follow that native contract. Native rules do not weaken this
standard's requirements for traceability, immutability, compatibility
classification, and lifecycle evidence.

Issue descriptions, research inventories, changelogs, release notes, templates,
generators, checkers, reusable workflows, and existing repository
implementations do not redefine this standard. Current repository behavior MAY
inform adoption planning but is not a reference implementation or normative
precedent.

## Applicability

This standard applies when an organization-managed release unit is published,
distributed, selected by a consumer, or deployed to a shared or production
environment. It covers:

- reusable libraries and registry packages;
- CLIs, binaries, archives, and installers;
- services, applications, and OCI images;
- HTTP, RPC, event, and schema compatibility contracts;
- database migrations;
- reusable IaC modules, constructs, components, packages, and providers;
- deployed IaC applications, stacks, plans, state, and change sets; and
- organization standards, schemas, policy snapshots, and shared tooling.

Local development attempts, ephemeral pull request builds, and unpublished test
artifacts MAY use development identifiers without becoming production releases.
They MUST NOT be presented through a stable or preferred channel.

## Core terms

| Term | Meaning |
| --- | --- |
| Version | A human-readable compatibility, ordering, or release-line signal |
| Release | Publication from a validated source boundary that makes an artifact or deployment identity available to a consumer or environment |
| Release unit | The smallest independently versioned, published, supported, and retired artifact set |
| Compatibility surface | A promised API, ABI, CLI, configuration, schema, protocol, behavior, platform, or dependency contract |
| Source revision | The immutable commit SHA used as release input |
| Artifact identity | A registry identity plus digest, integrity value, or checksum that identifies exact published bytes |
| Deployment identity | The selected source revision, artifact or change identity, configuration evidence, and target environment state |
| Maturity channel | Development/Snapshot, Alpha, Beta, RC, or Stable release expectation |
| Support state | Preferred, Supported, Deprecated, or EOL status of a version line |

## Core contract

A production release MUST:

1. originate from validated `main` under the organization contribution policy;
2. identify its release unit and repository-native version or release
   identifier;
3. record the immutable source revision;
4. record the exact artifact or deployment identity required by its profile;
5. declare its maturity channel and compatibility impact;
6. preserve published versions, tags, artifacts, and registry history rather
   than overwriting them;
7. provide the release evidence required by
   [Release records and evidence](./release-evidence.md); and
8. fail closed when requested version, source, tag or ref, registry metadata,
   artifact identity, or target environment is inconsistent or ambiguous.

Version, source, artifact, and deployment identity are distinct axes:

```text
repository-native version or release identifier
                       |
                       v
             immutable source SHA
                       |
          applicable tag/ref boundary
                       |
                       v
       registry identity + digest/checksum
                       |
                       v
      release record and deployment evidence
```

A version does not identify exact bytes. A commit SHA does not prove which bytes
were published. A mutable tag does not replace an immutable registry digest. A
deployment record does not redefine an API or schema compatibility version.

## Standard map

| Document | Normative responsibility |
| --- | --- |
| [Artifact and version profiles](./profiles.md) | Version schemes, release identities, compatibility surfaces, and monorepo release units |
| [Compatibility lifecycle](./lifecycle.md) | Maturity, support, deprecation, EOL, bad releases, and emergency changes |
| [Release records and evidence](./release-evidence.md) | Authority of manifests, tags, registries, changelogs, release notes, checksums, SBOMs, provenance, and attestations |
| [Release automation](./automation.md) | Repository ownership, shared automation criteria, publication sequencing, permissions, and recovery |
| [Adoption and exceptions](./exceptions.md) | New-unit adoption, existing-repository migration, exception records, and emergency review |

## Ownership boundary

| Plane | Owns | Does not own |
| --- | --- | --- |
| Organization policy | This standard, artifact profiles, selection criteria, evidence outcomes, lifecycle defaults, and exception semantics | Exact versions, credentials, repository status, or release history |
| Shared implementation | Optional schemas, checkers, adapters, templates, actions, workflows, and immutable implementation releases | Normative rule meaning or repository publication authority |
| Repository execution | Exact version, release unit, manifests, tag format, triggers, credentials, publication, recovery, history, support state, and migration | Organization-wide policy |
| Registry or environment | Published artifact or native distribution identity, or observed deployment state | Compatibility promises not expressed by the owning release unit |

The organization MUST NOT maintain a central matrix of current repository
versions, release status, or migration progress as part of this standard.

## Cross-standard boundaries

- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) owns branch roles, validated
  `main`, commit, pull request, and promotion policy.
- The [Developer Tooling Standard](../developer-tooling/README.md) owns Golden
  Path standard, schema, asset-bundle, checker, and shared-tooling compatibility
  versions. This standard governs general project artifacts and relates those
  assets to the same immutable release principles without redefining GP-009 or
  GP-020.
- Platform delivery standards own deployment mutation, rollout, rollback,
  readiness, and runtime verification. This standard owns only the release
  identity and evidence that those workflows carry.
- The [Engineering documentation standard](../engineering-documentation/README.md)
  owns documentation placement, lifecycle, and canonical authority maps.
- Product launches, business milestones, and customer-facing product names are
  not software compatibility versions unless an owning product contract says
  otherwise.

## Decision traceability

| Decision | Final authority |
| --- | --- |
| RV-001 | Authority and ownership in this document |
| RV-002 | Core contract and identity separation in this document |
| RV-003 | Package profile in [Artifact and version profiles](./profiles.md) |
| RV-004 | Service and container profiles in [Artifact and version profiles](./profiles.md) |
| RV-005 | API, event, and schema profiles in [Artifact and version profiles](./profiles.md) |
| RV-006 | IaC profiles in [Artifact and version profiles](./profiles.md) |
| RV-007 | Monorepo release units in [Artifact and version profiles](./profiles.md) |
| RV-008 | [Compatibility lifecycle](./lifecycle.md) |
| RV-009 | [Release records and evidence](./release-evidence.md) |
| RV-010 | [Release automation](./automation.md) |

The governing decision is
[ADR-0007: Adopt the organization Release and Versioning Standard](../../decisions/0007-adopt-release-and-versioning-standard.md).

## Adoption

New release units MUST select and implement the applicable profile before their
first stable or production publication. Existing release units adopt through
repository-owned work under [Adoption and exceptions](./exceptions.md). Standard
publication does not assert that an existing repository conforms and does not
authorize an organization-wide migration program.
