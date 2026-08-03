# ADR-0007: Adopt the organization Release and Versioning Standard

- Status: Accepted
- Date: 2026-08-03

## Context

The organization produces packages, CLIs, services, containers, APIs, schemas,
database migrations, IaC artifacts, native client applications, research
snapshots, experiment results, datasets, models, policy snapshots, and shared
tooling. These artifacts do not share one useful version signal or release
identity.

Repository inspection found useful constraints but cannot establish central
authority. A repository can change, disappear, or contain a historical
compromise. Copying its workflow into policy would make workers depend on that
repository rather than stable organization rules.

The existing contribution policy requires validated `main` and immutable
published releases, while the Developer Tooling Golden Path versions its own
standard and assets. Platform delivery standards identify deployed services by
source revision, immutable image digest, and deployment evidence. A general
standard must preserve those boundaries rather than require SemVer, a Git tag, a
GitHub Release, a changelog file, or one workflow for every artifact.

The organization also expects a GitHub Free private-repository baseline. Paid
private attestations, protected environments, and enforcement features cannot
be the only way to establish a conforming release.

## Decision

We adopt the organization
[Release and Versioning Standard](../standards/release-versioning/README.md).

1. The central standard owns artifact profiles, version or record-identifier
   selection rules, lifecycle defaults, release-evidence outcomes, automation
   boundaries, and exception semantics.
2. Repositories own exact versions or research-record identifiers, release
   units, native manifests, tag or snapshot formats, credentials, executable
   automation, publication or finalization, recovery, current support or
   research status, lineage, and history.
3. Existing repository implementations are non-normative evidence and are not
   named as organization reference implementations.
4. Version or ordering signal, source revision, tag, ref, or snapshot boundary,
   artifact or research-record identity, and deployment identity are separate
   linked axes.
5. Reusable packages follow ecosystem-native version and compatibility
   semantics. Services and deployed IaC stacks do not receive SemVer merely
   because they are deployed.
6. API, event, schema, and database contracts evolve independently of service
   deployment versions.
7. Monorepos choose fixed or independent versions and record identifiers by
   independently consumed or finalized release unit rather than repository
   boundary.
8. Maturity channel and support state are separate from repository-defined
   research-record status. Consumer reach determines deprecation defaults, and
   published or finalized identities are corrected, superseded, withdrawn,
   deprecated, yanked, or retracted under their applicable profile rather than
   overwritten.
9. A portable source, artifact or research-record identity, and release or
   research-record baseline applies without paid hosting features. Stronger
   checksums, SBOMs, provenance, attestations, signatures, persistent archives,
   and immutable GitHub Releases apply by artifact profile and capability.
10. Developer changelogs, product release notes, and research revision notes
    explain changes but do not replace registry, artifact, research-record, or
    deployment identity. Git tags and GitHub Releases are not universal
    publication requirements.
11. Release and record automation fails closed on identity mismatch, serializes
    conflicting publication or finalization by release unit and intended
    identifier, preserves partial-operation state, and never overwrites a
    published version, artifact, or finalized research record.
12. No single release tool or universal reusable workflow is required. Shared
    automation is admitted only after multiple stable implementations establish
    a small contract, and repositories retain thin callers and least-privilege
    credentials.
13. New release units implement the target from their first Stable release,
    production deployment, external research publication, or immutable research-
    record finalization. Existing release units migrate through repository-owned
    work without rewriting history.
14. The organization standard does not maintain current repository versions,
    research-record status, migration status, or a central release or research
    registry.
15. Native client applications retain separate user-facing versions, platform
    build identifiers, signed build identities, and store or distribution
    records. Store rollout state and coordinated product versions do not replace
    those exact identities or independent backend compatibility contracts.
16. Research repositories do not receive repository-wide SemVer merely to
    express scientific progress. Immutable snapshots, runs, datasets, models,
    and results retain exact identity and lineage, while reusable research
    software follows its applicable package, CLI, service, or schema profile.
    Scientific interpretation remains with the owning research authority.

## Consequences

### Positive

- Workers apply stable artifact-category rules without consulting a mutable
  reference repository.
- Compatibility versions and exact delivery identities remain truthful and
  useful for their separate consumers.
- Release evidence scales from registry packages and service deployments to
  native distribution and research-record finalization without duplicating
  irrelevant ceremony.
- Native client and research artifacts retain profile-appropriate identities
  without conflating product marketing, software compatibility, and scientific
  record state.
- GitHub Free private repositories retain a complete portable baseline.
- Shared automation can emerge from proven common contracts without hiding
  repository publication authority.

### Negative

- Repositories must explicitly select release units and profiles rather than
  inheriting one universal workflow.
- Evidence is materialized in different native systems and must be linked
  deliberately.
- Existing repositories may temporarily diverge and require local migration or
  exceptions.
- Immutable publication or finalization makes correction and recovery more
  deliberate.

## Alternatives considered

### Use one repository as the release reference implementation

Rejected because local history, tools, artifact mix, and exceptions would become
unstated organization policy and drift whenever that repository changed.

### Require SemVer, Git tags, GitHub Releases, and changelogs everywhere

Rejected because service deployments, database migrations, API contracts,
containers, IaC state, native builds, and research artifacts have different
identity, compatibility, ordering, and status units. The result would create
duplicate records and false guarantees.

### Require the strongest supply-chain evidence for every release

Rejected because checksums, SBOMs, provenance, signatures, and attestations have
artifact-specific value and hosting constraints. Portable identity remains
mandatory while stronger evidence is profile- and capability-dependent.

### Adopt one organization reusable release workflow immediately

Rejected because version or record-identifier sources, registries or archives,
credentials, irreversible publication or finalization steps, and recovery
semantics differ. Reuse begins only after multiple stable implementations prove
a bounded common contract.

### Delay the standard until all repositories migrate

Rejected because migration requires a stable target. Acceptance of the target
does not claim current conformance or authorize an organization-wide migration.

## Adoption status

The decision and normative standard are As-built in this governance repository.
Repository release and research-publication automation, migration, current
versions or research status, and conformance remain repository-owned and are
outside this decision's completion scope.
