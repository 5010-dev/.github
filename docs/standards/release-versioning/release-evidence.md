# Release records and evidence

A release or research record connects a compatibility, ordering, or status
signal to exact source, artifact, research-record, and deployment identities. It
is a logical record and MAY be materialized through repository files, a registry,
an archive or persistent-identifier service, an immutable GitHub Release, a
deployment system, or linked evidence. This standard does not require a central
release database.

## Minimum release record

A minimum record for every in-scope release or immutable research artifact MUST
include:

- release unit and version, repository-native release identifier, or research-
  record identifier;
- immutable source commit;
- exact published artifact, research-record, or deployment identity required by
  the selected profile;
- publication, deployment, registration, or record-finalization timestamp;
- applicable maturity channel and support state, or repository-defined research
  record status;
- release or revision summary and compatibility or scientific-scope
  classification when applicable;
- an owner and durable location for the evidence.

The record MUST include the following when applicable:

- release tag or ref;
- artifact name, registry location, digest, integrity value, or checksum;
- migration, deprecation, rollback, replacement, or recovery guidance;
- supported runtime, platform, architecture, or dependency range;
- build workflow, build invocation, or provenance evidence; and
- known security, integrity, compatibility, scientific-scope, or use
  limitations.

A protected package-tag release record MUST additionally include the immutable
release intent, admitted base and head commits, exact merge-diff identity,
derived package tag, registry version and integrity, selected channel, workflow
run, package-only effect verification, and retry or recovery state. The record
MUST distinguish a successful new publication from an idempotent verification
of an already-published identical identity.

A pre-mutation recovery record MUST additionally preserve the unchanged original
release-intent path, prior failed source and workflow run, terminal pre-mutation
outcome, observed absence of both immutable identities, newly admitted base and
head, recovery-record path, authorization-use result, and final tag/registry
state. Evidence MUST distinguish an unpublished pre-mutation failure from
tag-only or registry-only partial publication and from successful immutable
publication followed by verification failure.

A tag-only completion record MUST additionally preserve the unchanged original
release intent; the exact failed publication source, selecting repository,
declared publication or recovery workflow, `dev` push event/ref, workflow run,
run attempt, authorization type and path, and trusted job or terminal evidence
that its tag-creation phase completed before registry publication failed; the
existing tag and observed absent registry version; retained Actions artifact ID,
name, expiry, archive digest, tarball file name and SHA-256, native package
integrity, and embedded source; newly admitted base and head; authorization-use
result; and final tag, registry integrity, and dist-tag state. Evidence MUST
distinguish a new registry publication from verification-only exact state and
MUST prove that no rebuild, tag mutation, rerun mutation, second-run mutation,
sibling effect, or tag credential occurred.

A completion-recovery record MUST additionally preserve the immutable original
completion path and bytes, the direct predecessor authorization path, exact
failed run, authorization-run ordinal `1`, run attempt `1`, terminal
pre-mutation phase outcomes, and live workflow-history evidence used to derive
that ordinal. Evidence MUST distinguish the predecessor's first distinct run
from a rerun and from a later distinct run whose attempt number also equals
`1`.

A native client release record MUST additionally identify the application or
bundle, platform-native display version and build identifier, signed build or
archive, distribution channel, supported platform range, and applicable store
submission or release record.

A research artifact record MUST additionally identify its snapshot, run, result,
dataset, or model type; immutable repository-native identifier; exact content
identity required by its profile; input and output lineage; predecessor,
amendment, retry, correction, or supersession relationships; and citation or
persistent archive metadata when applicable. Exact content identity MAY be an
immutable Git source and snapshot boundary, exact native registration identity,
or applicable manifest and content digests. A repository MAY link these fields
from an owning research manifest rather than duplicate them in a general release
record. The [research snapshot profile](./profiles.md#study-compendium-and-preregistration-snapshots)
defines when an additional manifest or content digest is required.

Routine internal service deployments MAY keep the change summary in a
machine-readable deployment record. A human-readable note MUST be linked when a
deployment changes a consumer or operations contract.

## Authority of release surfaces

| Surface | Authority | Boundary |
| --- | --- | --- |
| Native manifest, release metadata, or research metadata | Human-readable version, ordering, or record-status source | Does not prove publication, finalization, or exact bytes |
| Source commit | Immutable release or research-record input | Does not prove build output, external payload, registry, archive, or deployment state |
| Git tag or ref | Applicable source, release-event, or snapshot boundary | Is not exact artifact identity for external payloads and is not universal for deployments |
| Registry package version and integrity | Publication state for registry-native artifacts | Changelog and support meaning remain repository-owned |
| OCI digest | Exact container manifest or index identity | Mutable aliases remain discovery only |
| Archive checksum | Exact distributed file identity | Platform and compatibility claims remain release metadata |
| Native store or signed distribution record | Publication and rollout state for an exact platform build | Does not replace source, signed build, backend-contract, or customer communication evidence |
| GitHub Release | Canonical distribution record only when the profile selects it | Is not required for every package, service, API, or IaC deployment |
| Deployment evidence | Observed environment selection and execution state | Does not replace independently versioned API or schema contracts |
| Research snapshot, run, registry, or persistent archive record | Exact research artifact identity, lineage, status, and availability according to its owning system | Does not establish scientific validity or replace repository-local scientific authority |
| Changelog, release note, or research revision note | Human-readable change, compatibility, or scientific-scope explanation | Does not replace registry, artifact, research-record, or deployment identity |

If two authoritative surfaces disagree, automation MUST fail closed before
publication or finalization. After publication or finalization, the repository
MUST preserve the discrepancy as an incident and issue a correction or successor
record rather than rewriting history.

## Changelogs, product release notes, and research revision notes

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

Developer-facing changelogs and product-facing release notes are distinct
surfaces:

- developer-facing records explain technical compatibility, migration,
  deprecation, operations, API, schema, dependency, and recovery impact; and
- product-facing notes explain user-observable changes in language appropriate
  for the audience and distribution channel without exposing sensitive internal
  details.

A native client stable release distributed to end users MUST provide
product-facing release notes when its distribution channel supports them. Those
notes MAY be drafted from the reviewed developer-facing release plan, changelog,
or pull-request metadata, but a human owner MUST approve externally published
text. A product-facing note MAY aggregate multiple coordinated release units,
including independently distributed native clients, web applications, and
backend changes. Each claimed change MUST map to its exact release unit and
version, build, artifact, or deployment record, and the note MUST NOT present one
product version as the exact identity of every covered unit. For each covered
unit, the product-facing and developer-facing sources MUST agree on the
applicable user-visible change set. Security-sensitive remediation details MAY
remain only in an appropriately restricted developer or incident record.

An externally published or cited research snapshot, result, dataset, model, or
research-software release MUST provide a human-readable revision note. A
corrected or superseding immutable research record MUST do so even when it
remains internal. The note MUST identify applicable protocol amendments, input
or data selection changes, analysis or software corrections, supersession, and
the assessed effect on findings, including an explicit unknown or
not-yet-evaluated state. Automation MAY draft this note from manifests and
developer changelogs, but the owning human research authority MUST approve
scientific claims. A software changelog MUST NOT silently rewrite a research
record.

## Checksums, SBOMs, and provenance

- A portable binary, archive, installer, or equivalent downloaded file MUST
  have a published cryptographic checksum.
- A native store build MUST preserve the signed archive or build identity used
  for submission. A public standalone checksum is not required when the native
  distribution system supplies the only supported verification and installation
  path.
- A research manifest MUST bind experiment outputs, dataset or model payloads,
  generated bundles, and other contents outside a self-contained immutable Git
  snapshot with cryptographic digests when the owning format, registry, archive,
  or registration service does not already provide immutable content identities.
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

The portable software and deployment baseline is source SHA, applicable tag or
ref, registry identity or digest/checksum, and a durable release record. The
portable research baseline is source SHA, immutable record identifier and
status, exact native registration or content identity, applicable lineage, and a
durable research record. GitHub-native private artifact attestations and paid
enforcement features MUST NOT be universal requirements for the organization's
GitHub Free private baseline. An available external provenance or signing system
MAY strengthen the same outcome.

## Immutable release and research records

When GitHub Releases are the canonical distribution record for binaries or
archives, repository release immutability MUST be enabled. Automation MUST
create a draft, attach and verify all intended assets and checksums, and only
then publish the release.

Signed Git tags MAY strengthen source attribution but are not a universal
requirement. A published tag used as a release boundary MUST be immutable and
MUST identify the recorded source revision. A moved or recreated release tag is
an integrity incident.

Registry versions, released files, tags, published release assets, and immutable
research-record identities MUST NOT be overwritten or, after deletion, reused
for different content. Correction, supersession, withdrawal, deprecation, yank,
retraction, and emergency deletion follow the
[Compatibility lifecycle](./lifecycle.md).

## Relevant upstream specifications

- [Semantic Versioning 2.0.0](https://semver.org/)
- [SLSA provenance](https://slsa.dev/spec/v1.2/provenance)
- [GitHub immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
- [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
- [OCI image descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)
- [Apple bundle version](https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleversion)
- [Android app versioning](https://developer.android.com/studio/publish/versioning)
- [Citation File Format](https://citation-file-format.github.io/)
- [RO-Crate 1.3](https://www.researchobject.org/ro-crate/specification/1.3/)
