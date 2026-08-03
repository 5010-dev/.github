# Artifact and version profiles

This document defines how a release unit selects a version or ordering signal,
exact release or research-record identity, and compatibility or scientific-scope
surface. A repository MUST select every profile that applies to the artifacts it
independently publishes, deploys, or finalizes as immutable research records.

## Selecting a release unit

A release unit is the smallest set that shares one version or record identifier,
compatibility or scientific-scope promise, publication or finalization event,
applicable support or retention policy, and retirement or supersession decision.

Two artifacts SHOULD be separate release units when they have independent
consumers, compatibility or scientific-scope surfaces, publication or
finalization cadence, rollback, correction, or supersession boundaries, support
or retention lines, or lineage. Sharing a repository, build, owner, or
programming language is not sufficient reason to version them together.

## Version scheme selection

### Semantic Versioning

A release unit SHOULD use its ecosystem-native form of Semantic Versioning when:

- consumers depend on a declared compatibility surface;
- breaking changes, compatible features, and compatible fixes can be
  distinguished;
- published contents are immutable; and
- consumers use exact versions, version ranges, or an upgrade policy.

A unit using SemVer MUST declare its compatibility surface. It MUST NOT use a
patch or minor increment to hide a change the native ecosystem or declared
surface classifies as breaking.

### Calendar Versioning

A release unit MAY use Calendar Versioning when time is the primary meaning of a
coordinated policy snapshot, support catalog, data release, or release train.
CalVer MUST NOT be treated as a compatibility guarantee. A serialized contract
with breaking evolution MUST maintain a separate compatibility epoch or schema
major. A CalVer release unit MUST define its calendar resolution and a
deterministic sequence or micro segment that disambiguates multiple releases or
corrections within one calendar period.

### Monotonic and source identifiers

A migration number, deployment sequence, build number, research snapshot or run
identifier, or source SHA MAY identify ordering, record identity, or exact
source. It MUST NOT be presented as a compatibility version unless the release
unit separately defines that promise.

## Compatibility classification

A release unit that claims SemVer or backward compatibility MUST declare the
surface it protects. Breaking-change review MUST consider every applicable
observable contract, including:

- public API, ABI, CLI flags, exit status, and machine-readable output;
- request, response, event, and schema fields whose removal, reinterpretation,
  or constraints affect consumers;
- authentication, authorization, error, retry, ordering, and idempotency
  semantics;
- configuration keys, defaults, environment variables, and secret contracts;
- reductions in supported runtimes, operating systems, architectures,
  databases, providers, or dependency ranges;
- persisted state, database migration behavior, and IaC resource identity; and
- documented behavior and security boundaries.

Change intent does not determine compatibility. A change described as a bug fix
is breaking when it invalidates an observable contract on which consumers were
permitted to rely.

## Profile requirements

| Profile | Default version or ordering signal | Exact release or record identity | Compatibility or scientific-scope surface |
| --- | --- | --- | --- |
| Registry package or library | Ecosystem-native SemVer | Native version, source SHA, registry or VCS distribution identity, and native integrity when provided | Public API or ABI, dependency range, runtime and platform support |
| CLI, binary, archive, or installer | SemVer when a documented consumer contract exists | Version, source SHA, applicable tag, immutable distribution record, checksum | Flags, exit status, output, configuration, file format, and platform support |
| Service or application | No automatic SemVer requirement; source or release sequence, CalVer, or product version only when meaningful | Source SHA, exact executable or OCI digest, and deployment record | API, event, configuration, operational, and data contracts tracked independently |
| Native client application | Platform-native user-facing version plus a platform-compliant build identifier | Source SHA, bundle or application identity, platform version and build identifiers, signed build identity, and store or distribution record | On-device behavior, persisted state and migration, deep links, authentication, backend contracts, and supported OS and device set |
| OCI image | Human-readable immutable release tag MAY accompany publication | Manifest or index digest | Platform set, entry point, configuration, and exposed runtime behavior |
| HTTP or RPC API | Compatibility major or ecosystem-native contract version | Contract revision plus producer deployment identity | Resources, methods, requests, responses, auth, errors, and promised behavior |
| Event or message schema | Independent schema or contract version | Schema digest or registry revision plus producer identity | Wire compatibility, field meaning, ordering, and delivery semantics |
| Database migration | Monotonic immutable migration identifier | Migration content digest plus applied-state evidence | Forward and backward application, data compatibility, and rollback limits |
| Terraform or OpenTofu module | SemVer | Immutable registry version or VCS source revision | Inputs, outputs, provider constraints, resources, and state migration |
| CDK construct library | Ecosystem-native SemVer | Package version plus registry identity | Construct API and documented synthesis compatibility |
| Pulumi package, component, or provider | SemVer | Package version plus schema, plugin, and SDK identity as applicable | Package schema, provider or component behavior, and SDK compatibility |
| IaC application or stack | No automatic SemVer requirement | Source SHA, plan or change-set identity, and deployment or state evidence | Resource identity, state, operations, and externally consumed outputs |
| Research study, compendium, or preregistration snapshot | No automatic SemVer requirement; immutable repository-native revision, monotonic edition, or CalVer snapshot | Snapshot identifier, source SHA, timestamp, predecessor or amendment relationship, exact native registration identity when applicable, manifest or content digest for content outside the immutable source boundary, and persistent archive or citation identity when applicable | Declared protocol, included evidence and data, analysis meaning, and snapshot contents; not software API compatibility |
| Experiment run or result artifact | Immutable run or result identifier; no automatic SemVer requirement | Run identifier, source SHA, input, configuration, environment, and output identities, terminal status, manifest digest, and predecessor or retry relationship | Record schema, input and output meaning, provenance, and reproducibility boundary; not scientific validity |
| Dataset, model, or derived artifact | Repository-native immutable revision, registry version, persistent identifier, or CalVer when a maintained lineage needs a human-readable signal | Content digest or immutable registry identity, source or generation identity, lineage, and persistent identifier when applicable | Schema, feature or label meaning, format, license and use restrictions, evaluation scope, and consumer integration contract |
| Standard, policy, schema, or shared tooling | Owning standard's CalVer, SemVer, or compatibility epoch | Immutable source snapshot plus released implementation digest | Normative rules, serialized contracts, and consumer-tool compatibility |

## Package and library profile

A published package or library MUST:

- use its ecosystem-native manifest or release metadata as the version source;
- publish a version that matches that source exactly;
- record the immutable source revision, registry or native distribution
  identity, and integrity or digest when the ecosystem provides one;
- follow native namespace, dependency-resolution, prerelease, and
  major-version rules;
- classify changes against its declared public compatibility surface; and
- provide release notes for consumer-visible stable releases.

A Git tag or GitHub Release MAY be used as an additional source or distribution
record. Neither replaces registry publication state. If the workflow uses a tag
as its release boundary, the tag MUST identify the same source and version and
MUST be immutable after publication.

## CLI and distributed executable profile

A distributed executable MUST record its version, source revision, applicable
release tag, supported platform set, and immutable artifact checksum. Its
canonical distribution record MAY be an immutable GitHub Release or another
immutable distribution service.

A CLI that promises flags, exit codes, machine-readable output, configuration,
or file formats SHOULD use SemVer. It MUST classify a removal or incompatible
meaning change against those surfaces rather than considering only language API
changes.

## Service, application, and container profile

A service or application MUST NOT adopt SemVer solely because it is deployed.
Its exact production identity is the immutable source revision, executable or
OCI digest, and deployment evidence.

A mutable image alias such as `latest`, an environment name, or a source-SHA tag
MAY aid discovery. It MUST NOT replace the OCI digest as the released container
identity. API, event, schema, and database compatibility versions remain
independent of the service deployment cadence.

## Native client application profile

A native client release unit MUST use the version and build identifiers required
by its target platform. Its user-facing or marketing version MAY follow SemVer,
CalVer, or a coordinated product release, but it MUST NOT be treated as proof of
backend API, schema, or data compatibility.

Each distributed build MUST record:

- immutable source revision and application or bundle identifier;
- platform-native user-facing version and build identifier;
- signed archive or build identity available before upload;
- target platform, supported operating-system range, device or architecture set,
  and distribution channel;
- store submission, review, release, withdrawal, or staged-rollout record when a
  store mediates distribution; and
- the backend, API, schema, persisted-state, and migration compatibility policy
  required to operate that build safely.

The release record MAY link to repository-owned compatibility and platform
policies rather than duplicate unchanged policy text for every build.

A platform build identifier MUST NOT be reused for different content and MUST
increase when the platform uses it for upgrade ordering. iOS, Android, desktop,
regional, branded, or otherwise independent distributions SHOULD be separate
release units when they have independent binaries, publication cadence,
rollback or withdrawal boundary, or support policy. Coordinated display versions
do not make independently distributed builds one artifact identity.

Store review, staged rollout percentage, and preferred distribution state are
mutable delivery state. They MUST NOT replace the immutable build and store
release identities. A web frontend that is deployed rather than installed uses
the service or application profile, not this profile.

## API, event, and schema profile

An independently consumed contract MUST declare its compatibility unit and
change rules. A service image version or deployment timestamp MUST NOT silently
stand in for that contract version.

The owning contract MUST define how consumers discover its current revision,
how compatible and breaking changes are classified, and how migration and
deprecation are communicated. The release record MUST link the contract
revision to the producer artifact or deployment identity.

## Research, dataset, and model artifact profiles

A research repository MUST NOT adopt a repository-wide SemVer solely to express
study progress, confidence, phase completion, publication status, or scientific
maturity. It MUST identify each organization-managed artifact that it
independently freezes, publishes, or finalizes using the applicable profile.
Development branches and mutable working documents remain source history rather
than released research snapshots.

An externally owned dataset, model, software release, or other input does not
become an organization release unit merely because a research workflow consumes
it. The owning run or snapshot manifest MUST reference the exact upstream
version, revision, digest, registry identity, or persistent identifier required
to resolve that input reproducibly.

### Study, compendium, and preregistration snapshots

An immutable research snapshot MUST record its repository-native snapshot or
edition identifier, source revision, creation or registration timestamp, and
relationship to any predecessor, amendment, correction, or superseded snapshot.
A snapshot whose complete contents are bound by an immutable Git source boundary
or an exact native registration identity MAY use that identity as its exact
content identity. A manifest or content digest is additionally required when the
snapshot includes generated bundles, payloads outside Git, or contents whose
native archive or registration identity does not establish exact immutability.
A later amendment or correction MUST create a new record and MUST NOT overwrite
a registered or published snapshot.

An externally cited snapshot SHOULD use a persistent archive and globally unique
identifier when an appropriate service is available. Citation metadata MUST
identify the exact snapshot or software version used; a project-level or latest
identifier MAY additionally connect the lineage but MUST NOT replace the exact
version reference.

### Experiment runs and result artifacts

An experiment run or result artifact MUST have an immutable identity and a
manifest that binds, when applicable:

- exact source revision and executable or environment identity;
- input dataset, model, dependency, configuration, and random-seed identities;
- output artifact identities and cryptographic digests;
- execution timestamps, runtime or hardware context needed for interpretation,
  and a truthful terminal or non-terminal status; and
- predecessor, retry, correction, or supersession relationships.

The owning research contract defines the exact manifest schema and the evidence
required for scientific interpretation. Structural validation, checksums, and
provenance establish identity and integrity; they MUST NOT be represented as
proof of scientific truth, relevance, or production authorization.

### Datasets, models, and derived artifacts

A published dataset, model, or derived artifact MUST preserve an exact content
digest or immutable native registry identity and enough generation and lineage
metadata to determine its inputs and producer. The owner MUST define which
changes create a new artifact revision and how consumers discover corrections,
supersession, schema changes, license or consent constraints, and evaluation
scope.

When a persistent-identifier service distinguishes minor metadata updates from
substantive content versions, the repository MUST follow that service's native
rules. A substantive content replacement MUST receive a new immutable identity;
updating metadata MUST NOT silently change the bytes or scientific meaning bound
to an existing identity.

A dataset or model retained solely as a scientific record uses the owning
research status and lineage contract. An independently consumed operational
dataset or model MUST additionally declare its consumer compatibility surface,
maturity and support policy, and registry or distribution lifecycle. A deployed
model MUST also select the applicable service, OCI, or deployment profile. Its
exact model identity remains independent of the service or application version
that selects it.

### Reusable research software

Research code that declares a consumer-facing library, CLI, service, workflow,
or serialized contract MUST additionally select the corresponding software,
service, or schema profile. Its compatibility version is independent of study,
run, dataset, model, paper, or research-snapshot revisions. An engineering patch
that affects published findings requires a new or corrected research artifact;
the software version increment alone does not rewrite the scientific record.

## Database migration profile

A database migration MUST have a unique, monotonic, immutable identifier. The
owning repository MUST retain the migration content and enough applied-state
evidence to determine whether it ran. An applied migration MUST NOT be edited,
renumbered, deleted as routine cleanup, or treated as a package release that can
be yanked. A later migration supersedes or repairs it.

## IaC profiles

Reusable modules, constructs, components, packages, and providers are consumer
artifacts and MUST follow their registry or language package profile.

An IaC application or stack is a deployment unit. It MUST retain source, plan or
change-set, target, state, and applied deployment identity. Environment names
such as `dev`, `staging`, and `production` are deployment environments, not
prerelease channels. State identity and mutation controls remain owned by the
applicable IaC and deployment standards.

## Monorepo fixed and independent versioning

Fixed versioning SHOULD be selected only when release units:

- are always published or finalized and consumed together;
- share one compatibility or scientific-scope surface and cadence;
- do not support meaningful partial upgrades, corrections, or supersession; and
- share rollback and support policy or retention and lineage policy.

Independent versioning SHOULD be selected when consumers, compatibility
or scientific-scope surfaces, publication or finalization cadence, correction or
supersession boundary, support or retention lines, or lineage differ. A breaking
or scope-changing revision in one independent unit MUST NOT force an unrelated
version or record revision in another solely because they share a repository.

A monorepo MUST make the selected unit boundaries and tag, snapshot, registry, or
archive naming unambiguous. Dependency updates between independent software
units MUST be represented through their native manifests and release notes.
Lineage, correction, and supersession relationships between research units MUST
be represented through their owning manifests or revision records. Tooling
convenience MUST NOT silently turn unrelated packages or research artifacts into
one compatibility or scientific-scope promise.

## Relevant upstream specifications

- [Python version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/)
- [Go module version numbering](https://go.dev/doc/modules/version-numbers)
- [Go major-version modules](https://go.dev/doc/modules/major-version)
- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
- [OCI image descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)
- [Terraform module registry protocol](https://developer.hashicorp.com/terraform/internals/module-registry-protocol)
- [AWS CDK versioning](https://docs.aws.amazon.com/cdk/v2/guide/versioning.html)
- [Pulumi package repository strategy](https://www.pulumi.com/docs/iac/guides/building-extending/packages/repository-strategy/)
- [Apple bundle version](https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleversion)
- [Android app versioning](https://developer.android.com/studio/publish/versioning)
- [FAIR Principles for Research Software](https://doi.org/10.15497/RDA00068)
- [FORCE11 Software Citation Principles](https://force11.org/info/software-citation-principles-published-2016/)
- [DataCite versioning guidance](https://support.datacite.org/docs/versioning)
- [OSF registrations and preregistrations](https://help.osf.io/article/330-welcome-to-registrations)
- [Citation File Format](https://citation-file-format.github.io/)
- [RO-Crate specification](https://www.researchobject.org/ro-crate/specification/1.3/)
