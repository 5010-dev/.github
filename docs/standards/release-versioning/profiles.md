# Artifact and version profiles

This document defines how a release unit selects a version signal, exact release
identity, and compatibility surface. A repository MUST select every profile
that applies to the artifacts it independently publishes or deploys.

## Selecting a release unit

A release unit is the smallest set that shares one version, compatibility
promise, publication event, support policy, and retirement decision.

Two artifacts SHOULD be separate release units when they have independent
consumers, compatibility surfaces, publication cadence, rollback boundaries, or
support lines. Sharing a repository, build, owner, or programming language is
not sufficient reason to version them together.

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
major.

### Monotonic and source identifiers

A migration number, deployment sequence, build number, or source SHA MAY
identify ordering or exact source. It MUST NOT be presented as a compatibility
version unless the release unit separately defines that promise.

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

| Profile | Default version signal | Exact release identity | Compatibility surface |
| --- | --- | --- | --- |
| Registry package or library | Ecosystem-native SemVer | Native version, source SHA, registry or VCS distribution identity, and native integrity when provided | Public API or ABI, dependency range, runtime and platform support |
| CLI, binary, archive, or installer | SemVer when a documented consumer contract exists | Version, source SHA, applicable tag, immutable distribution record, checksum | Flags, exit status, output, configuration, file format, and platform support |
| Service or application | No automatic SemVer requirement; source or release sequence, CalVer, or product version only when meaningful | Source SHA, exact executable or OCI digest, and deployment record | API, event, configuration, operational, and data contracts tracked independently |
| OCI image | Human-readable immutable release tag MAY accompany publication | Manifest or index digest | Platform set, entry point, configuration, and exposed runtime behavior |
| HTTP or RPC API | Compatibility major or ecosystem-native contract version | Contract revision plus producer deployment identity | Resources, methods, requests, responses, auth, errors, and promised behavior |
| Event or message schema | Independent schema or contract version | Schema digest or registry revision plus producer identity | Wire compatibility, field meaning, ordering, and delivery semantics |
| Database migration | Monotonic immutable migration identifier | Migration content digest plus applied-state evidence | Forward and backward application, data compatibility, and rollback limits |
| Terraform or OpenTofu module | SemVer | Immutable registry version or VCS source revision | Inputs, outputs, provider constraints, resources, and state migration |
| CDK construct library | Ecosystem-native SemVer | Package version plus registry identity | Construct API and documented synthesis compatibility |
| Pulumi package, component, or provider | SemVer | Package version plus schema, plugin, and SDK identity as applicable | Package schema, provider or component behavior, and SDK compatibility |
| IaC application or stack | No automatic SemVer requirement | Source SHA, plan or change-set identity, and deployment or state evidence | Resource identity, state, operations, and externally consumed outputs |
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

## API, event, and schema profile

An independently consumed contract MUST declare its compatibility unit and
change rules. A service image version or deployment timestamp MUST NOT silently
stand in for that contract version.

The owning contract MUST define how consumers discover its current revision,
how compatible and breaking changes are classified, and how migration and
deprecation are communicated. The release record MUST link the contract
revision to the producer artifact or deployment identity.

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

- are always published and consumed together;
- share one compatibility surface and cadence;
- do not support meaningful partial upgrades; and
- share rollback and support policy.

Independent versioning SHOULD be selected when consumers, compatibility
surfaces, publication cadence, or support lines differ. A breaking change in one
independent unit MUST NOT force an unrelated major version in another solely
because they share a repository.

A monorepo MUST make the selected unit boundaries and tag or registry naming
unambiguous. Dependency updates between independent units MUST be represented
through their native manifests and release notes. Tooling convenience MUST NOT
silently turn unrelated packages into one compatibility promise.

## Relevant upstream specifications

- [Python version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/)
- [Go module version numbering](https://go.dev/doc/modules/version-numbers)
- [Go major-version modules](https://go.dev/doc/modules/major-version)
- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
- [OCI image descriptors](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)
- [Terraform module registry protocol](https://developer.hashicorp.com/terraform/internals/module-registry-protocol)
- [AWS CDK versioning](https://docs.aws.amazon.com/cdk/v2/guide/versioning.html)
- [Pulumi package repository strategy](https://www.pulumi.com/docs/iac/guides/building-extending/packages/repository-strategy/)
