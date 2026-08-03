# Release records and evidence

A release record connects a compatibility or ordering signal to exact source,
artifact, and deployment identities. It is a logical record and MAY be
materialized through repository files, a registry, an immutable GitHub Release,
a deployment system, or linked evidence. This standard does not require a
central release database.

## Minimum release record

Every production release MUST record:

- release unit and version or repository-native release identifier;
- immutable source commit;
- exact published artifact or deployment identity required by the selected
  profile;
- publication or deployment timestamp;
- maturity channel and applicable support state;
- change summary and compatibility classification; and
- an owner and durable location for the evidence.

The record MUST include the following when applicable:

- release tag or ref;
- artifact name, registry location, digest, integrity value, or checksum;
- migration, deprecation, rollback, replacement, or recovery guidance;
- supported runtime, platform, architecture, or dependency range;
- build workflow, build invocation, or provenance evidence; and
- known security, integrity, or compatibility limitations.

Routine internal service deployments MAY keep the change summary in a
machine-readable deployment record. A human-readable note MUST be linked when a
deployment changes a consumer or operations contract.

## Authority of release surfaces

| Surface | Authority | Boundary |
| --- | --- | --- |
| Native manifest or release metadata | Human-readable version source | Does not prove publication or exact bytes |
| Source commit | Immutable release input | Does not prove build output or registry state |
| Git tag or ref | Applicable source and release-event boundary | Is not exact artifact identity and is not universal for deployments |
| Registry package version and integrity | Publication state for registry-native artifacts | Changelog and support meaning remain repository-owned |
| OCI digest | Exact container manifest or index identity | Mutable aliases remain discovery only |
| Archive checksum | Exact distributed file identity | Platform and compatibility claims remain release metadata |
| GitHub Release | Canonical distribution record only when the profile selects it | Is not required for every package, service, API, or IaC deployment |
| Deployment evidence | Observed environment selection and execution state | Does not replace independently versioned API or schema contracts |
| Changelog or release note | Human-readable change and compatibility explanation | Does not replace registry, artifact, or deployment identity |

If two authoritative surfaces disagree, automation MUST fail closed before
publication. After publication, the repository MUST preserve the discrepancy as
an incident and issue a correction rather than rewriting history.

## Changelog and release notes

Every consumer-facing versioned stable release MUST provide human-readable
release notes that identify compatibility, migration, and deprecation impact.

A committed `CHANGELOG` is:

- `SHOULD` for reusable packages, distributed CLIs, and independently consumed
  monorepo release units; and
- `MAY` for services, internal applications, and deployed IaC stacks when their
  deployment records provide the canonical change history.

When both a changelog and GitHub Release notes exist, they MUST derive from one
reviewed release plan or otherwise agree on release unit, version, change
classification, and migration impact. Generated release notes MAY provide a
draft, but a maintainer or deterministic release policy MUST ensure they contain
only the intended release-unit changes.

## Checksums, SBOMs, and provenance

- A portable binary, archive, installer, or equivalent downloaded file MUST
  have a published cryptographic checksum.
- A registry integrity value or OCI digest satisfies exact-byte identity for
  its native artifact. A duplicate standalone checksum is not universally
  required.
- An executable artifact, container, or package with third-party runtime
  dependencies SHOULD publish an SBOM when the ecosystem and distribution path
  provide a usable consumer workflow.
- Build provenance SHOULD be published when consumers can verify it and link it
  to the exact artifact identity and source revision.
- An attestation MUST NOT be treated as sufficient evidence unless a consumer
  verification path is documented and exercised at the required assurance
  level.

The portable baseline is source SHA, applicable tag or ref, registry identity or
digest/checksum, and a durable release record. GitHub-native private artifact
attestations and paid enforcement features MUST NOT be universal requirements
for the organization's GitHub Free private baseline. An available external
provenance or signing system MAY strengthen the same outcome.

## Immutable release records

When GitHub Releases are the canonical distribution record for binaries or
archives, repository release immutability MUST be enabled. Automation MUST
create a draft, attach and verify all intended assets and checksums, and only
then publish the release.

Signed Git tags MAY strengthen source attribution but are not a universal
requirement. A published tag used as a release boundary MUST be immutable and
MUST identify the recorded source revision. A moved or recreated release tag is
an integrity incident.

Registry versions, released files, tags, and published release assets MUST NOT
be overwritten or, after deletion, reused for different content. Correction,
deprecation, yank, retraction, and emergency deletion follow the
[Compatibility lifecycle](./lifecycle.md).

## Relevant upstream specifications

- [Semantic Versioning 2.0.0](https://semver.org/)
- [SLSA provenance](https://slsa.dev/spec/v1.2/provenance)
- [GitHub immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
- [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
- [OCI image descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)
