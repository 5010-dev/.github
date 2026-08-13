# Release and Versioning Standard

- Status: Accepted
- Standard version: `2026.08.4`
- Last reviewed: 2026-08-14

This standard defines how the `5010-dev` organization versions, identifies,
publishes, evolves, and retires software, Infrastructure as Code, native client,
and research artifacts. It separates compatibility and ordering signals from
exact source, artifact, research-record, and deployment identities so that
releases remain understandable and auditable without making one repository,
registry, workflow, or tool the organization authority.

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

1. this standard and an applicable native ecosystem, registry, archive, or
   persistent-identifier specification;
2. repository-local version or research-record policy and release-unit
   declarations;
3. repository-native manifests, release metadata, or research metadata as the
   human-readable version, ordering, or status source;
4. the immutable source revision and exact registry, artifact, research-record,
   or deployment identity as publication or finalization evidence; and
5. repository-local release history, executable automation, and current
   support-state, research-status, and lineage records.

When an ecosystem, registry, archive, or persistent-identifier service defines
more specific version parsing, dependency resolution, major-version namespace,
prerelease ordering, correction, supersession, yanking, or retraction semantics,
repositories MUST follow that native contract. Native rules do not weaken this
standard's requirements for traceability, immutability, compatibility or scope
classification, and lifecycle evidence.

Issue descriptions, research inventories, changelogs, release notes, templates,
generators, checkers, reusable workflows, and existing repository
implementations do not redefine this standard. Current repository behavior MAY
inform adoption planning but is not a reference implementation or normative
precedent.

## Applicability

This standard applies when an organization-managed release unit is published,
distributed, selected by a consumer, deployed to a shared or production
environment, or finalized as an immutable research record. It covers:

- reusable libraries and registry packages;
- CLIs, binaries, archives, and installers;
- services, applications, and OCI images;
- native mobile and desktop client applications distributed through stores or
  signed installers;
- HTTP, RPC, event, and schema compatibility contracts;
- database migrations;
- reusable IaC modules, constructs, components, packages, and providers;
- deployed IaC applications, stacks, plans, state, and change sets;
- immutable research snapshots, experiment runs, datasets, models, result
  artifacts, and reusable research software; and
- organization standards, schemas, policy snapshots, and shared tooling.

Local development attempts, ephemeral pull request builds, and unpublished test
artifacts MAY use development identifiers without becoming production releases.
They MUST NOT be presented through a stable or preferred channel.

## Core terms

| Term | Meaning |
| --- | --- |
| Version | A human-readable compatibility, ordering, or release-line signal |
| Release | Publication from a validated source boundary that makes an artifact, research-record, or deployment identity available to a consumer, archive, or environment |
| Governed publication | A consumer-facing Stable release, production deployment, or externally published or cited research artifact that must satisfy the core contract |
| Release unit | The smallest independently versioned or identified artifact set that shares publication or finalization, compatibility or scientific-scope, retention or support, and retirement or supersession decisions |
| Compatibility surface | A promised API, ABI, CLI, configuration, schema, protocol, behavior, platform, or dependency contract |
| Scientific-scope surface | The declared protocol, included evidence or data, analysis meaning, provenance boundary, and contents whose change requires a new or corrected research record |
| Source revision | The immutable commit SHA used as release input |
| Artifact identity | An immutable registry, signed-build, archive, or distribution identity plus the native integrity, digest, checksum, or verification state required by its profile |
| Deployment identity | The selected source revision, artifact or change identity, configuration evidence, and target environment state |
| Research record identity | The immutable snapshot, run, result, dataset, model, or persistent identifier plus manifest or content digests and lineage required by its profile |
| Maturity channel | Development/Snapshot, Alpha, Beta, RC, Incubating, or Stable release expectation |
| Support state | Preferred, Supported, Deprecated, or EOL status of a version line |
| Research record status | Repository-defined state that distinguishes mutable work from immutable registered, terminal, corrected, superseded, or withdrawn research records without making a software compatibility claim |

## Core contract

A governed publication MUST:

1. originate from validated `main` under the organization contribution policy,
   unless an independently released registry package has explicitly selected
   the [protected package-tag profile](./protected-package-tag.md) and its exact
   source commit was admitted under that profile;
2. identify its release unit and repository-native version, release identifier,
   or research-record identifier;
3. record the immutable source revision;
4. record the exact artifact, research record, or deployment identity required
   by its profile;
5. declare its applicable maturity channel and compatibility impact, or its
   research record status when the research artifact profile applies;
6. preserve published versions, tags, artifacts, research record identities,
   and registry, archive, and research history rather than overwriting them;
7. provide the release evidence required by
   [Release records and evidence](./release-evidence.md); and
8. fail closed when requested version or identifier, source, tag or ref, registry
   or research metadata, artifact identity, record status, or target environment
   is inconsistent or ambiguous.

Recording an internal experiment run or terminal research result does not by
itself create a governed publication. It still follows the applicable research
profile's identity, immutability, lineage, and evidence rules. An externally
published or cited research artifact is a governed publication and follows the
complete contract above, including validated `main` provenance.

Version or ordering signal, source, artifact or research-record identity, and
deployment identity are distinct axes:

```text
repository-native version, release identifier, or research record ID
                       |
                       v
             immutable source SHA
                       |
                       v
     applicable tag, ref, or snapshot boundary
                       |
                       v
 registry, artifact, research manifest, digest, or deployment identity
                       |
                       v
 release, research-record, and deployment evidence
```

A version does not identify exact bytes. A commit SHA does not prove which bytes
were published. A mutable tag does not replace an immutable registry digest. A
deployment record does not redefine an API or schema compatibility version. A
structurally valid or terminal research record does not prove scientific
validity.

## Standard map

| Document | Normative responsibility |
| --- | --- |
| [Artifact and version profiles](./profiles.md) | Version and ordering schemes, exact release or research-record identities, compatibility or scientific-scope surfaces, and monorepo release units |
| [Protected package-tag publication](./protected-package-tag.md) | Narrow opt-in authority, intent, exact merge-diff admission, package-only effects, permissions, and recovery for mixed package/service monorepos |
| [Compatibility lifecycle](./lifecycle.md) | Maturity, support, research-record status, correction, deprecation, EOL, bad releases, and emergency changes |
| [Release records and evidence](./release-evidence.md) | Authority of manifests, tags, registries, archives, changelogs, release and revision notes, checksums, SBOMs, provenance, and attestations |
| [Release automation](./automation.md) | Repository ownership, shared automation criteria, publication and finalization sequencing, permissions, and recovery |
| [Adoption and exceptions](./exceptions.md) | New-unit adoption, existing-repository migration, exception records, and emergency review |

## Ownership boundary

| Plane | Owns | Does not own |
| --- | --- | --- |
| Organization policy | This standard, artifact profiles, selection criteria, evidence outcomes, lifecycle defaults, and exception semantics | Exact versions or record identifiers, credentials, current repository or research status, scientific meaning, lineage contents, or release history |
| Shared implementation | Optional schemas, checkers, adapters, templates, actions, workflows, and immutable implementation releases | Normative rule meaning, scientific judgment, or repository publication or finalization authority |
| Repository execution | Exact version or record identifier, release unit, manifests, tag or snapshot format, triggers, credentials, publication or finalization, recovery, history, support or research status, lineage, and migration | Organization-wide policy |
| Registry, archive, or environment | Published artifact, persistent research-record, or native distribution identity, or observed deployment state | Compatibility, scientific meaning, or support promises not expressed by the owning release unit |

The organization MUST NOT maintain a central matrix of current repository
versions, release or research-record status, lineage, or migration progress as
part of this standard.

## Cross-standard boundaries

- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) owns branch roles, validated
  `main`, commit, pull request, and promotion policy.
- The [Developer Tooling Standard](../developer-tooling/README.md) owns Golden
  Path standard, schema, asset-bundle, checker, and shared-tooling compatibility
  versions. This standard governs general project artifacts and relates those
  assets to the same immutable release principles without redefining GP-009 or
  GP-020.
- [Platform delivery standards](../../platform/README.md) own deployment
  mutation, rollout, rollback, readiness, and runtime verification. This
  standard owns only the release identity and evidence that those workflows
  carry.
- The [Engineering documentation standard](../engineering-documentation/README.md)
  owns documentation placement, lifecycle, and canonical authority maps.
- Product launches, business milestones, and customer-facing product names are
  not software compatibility versions unless an owning product contract says
  otherwise.
- Repository-local scientific designs, preregistrations, empirical evidence,
  findings, and human evaluation remain authoritative for scientific meaning.
  This standard governs their release-unit identity, immutability, lineage, and
  release evidence; it does not validate scientific truth or replace the
  applicable organization or repository-local research-artifact and
  reproducibility authority.

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
| RV-011 | [Protected package-tag publication](./protected-package-tag.md) |

## Standard revision history

| Version | Normative change |
| --- | --- |
| `2026.08.4` | Add a separate PR-mediated pre-mutation recovery authorization that may preserve an unpublished version only while both immutable identities are absent |
| `2026.08.3` | Clarify that the protected package-tag profile requires PR-mediated maintainer merge authorization, not an organization-wide independent approval |
| `2026.08.2` | Preserve validated-`main` as the default and add the opt-in protected package-tag profile for independently released packages in mixed package/service monorepos |
| `2026.08.1` | Add native client application and research artifact profiles, product and research release-note surfaces, and profile-specific lifecycle and automation boundaries |
| `2026.08` | Establish the RV-001 through RV-010 authority, identity, profile, lifecycle, evidence, automation, adoption, and exception contract |

The governing decision is
[ADR-0007: Adopt the organization Release and Versioning Standard](../../decisions/0007-adopt-release-and-versioning-standard.md).
The protected package-tag opt-in is introduced by
[ADR-0023: Adopt protected package-tag publication profile](../../decisions/0023-adopt-protected-package-tag-publication-profile.md).

## Adoption

New release units MUST select and implement the applicable profile before their
first Stable release, production deployment, external research publication, or
immutable research-record finalization. Existing release units adopt through
repository-owned work under [Adoption and exceptions](./exceptions.md). Standard
publication does not assert that an existing repository conforms and does not
authorize an organization-wide migration program.
