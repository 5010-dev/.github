# Golden Path distribution and versioning

- Status: Accepted
- Standard version: `2026.07`
- Contract version: `golden-path/v1`

Golden Path assets use different distribution modes according to ownership,
execution risk, and release lifecycle.

## Distribution modes

| Mode | Assets | Consumption authority |
| --- | --- | --- |
| Materialized repository-local asset | mise/Just files, modules, scripts, language config, caller workflow, metadata skeleton | Reviewed files committed by the consumer repository |
| Immutable referenced automation | Stable reusable workflow or composite action | Full commit SHA plus caller-owned inputs and permissions |
| Versioned released implementation | Checker, generator, CLI, package, schema/template bundle | Exact SemVer and checksum/digest; available provenance record |
| Documentation link | This standard and adoption guides | Stable central normative path, not copied prose |

Materialization is the default. A generated file becomes repository-local
executable authority and is not required to remain byte-identical to its source
template.

## Immutable consumption

Required build, test, bootstrap, and validation logic:

- MUST resolve from checked-in files or immutable verified artifacts;
- MUST NOT fetch a central default branch, moving tag, `latest`, redirecting raw
  URL, or user-global path at runtime;
- MUST NOT use unverified network-to-interpreter pipelines such as
  `curl ... | sh`;
- MUST pin remote actions and reusable workflows to full commit SHAs;
- MUST verify released binaries and packages by exact version and checksum or
  digest; and
- SHOULD verify provenance when the distribution provides a usable,
  plan-compatible record.

Materialized updates MUST arrive as reviewable diffs. Central automation MUST
NOT push directly to a consumer default branch or overwrite repository-owned
customization.

## Caller and reusable automation

The consumer caller workflow MUST own and explicitly declare:

- trigger and path filters;
- explicit minimum permissions;
- concurrency and cancellation;
- applicable environment or approval adapter;
- profile and working-directory inputs;
- named secret forwarding; and
- the full-SHA execution reference.

A reusable workflow owns only stable shared orchestration and MUST NOT elevate
the caller token. Callers MUST pass named required secrets; `secrets: inherit`
MUST NOT be the default.

Use a reusable workflow only when multiple repositories require the same stable,
versioned, independently tested job contract. Use a composite action for a
bounded repeated step sequence. Keep repository-specific quality behavior in
`just ci`.

## Ownership planes

The organization policy repository owns:

- human-readable rules, profiles, guides, and ADRs;
- normative rule and schema sources;
- workflow-template discovery; and
- dependency-light validation of its own content.

The shared implementation plane owns:

- checker and generator/upgrader source;
- materialization templates and fixtures;
- reusable actions/workflows;
- immutable standard snapshots; and
- release assets, manifests, checksums, provenance, and migration notes.

Consumer repositories own materialized files, exact pins, metadata, exceptions,
and current status. No central repository maintains a live consumer inventory.

A shared executable belongs outside the policy repository when it is consumed
by multiple repositories, has an independent version or rollback, has runtime
dependencies, requires cross-platform tests or release artifacts, crosses
permission/secret boundaries, or creates shared failure blast radius.

## Visibility

Visibility is not a conformance requirement. Generic tooling with no secrets,
private endpoints, customer data, proprietary product logic, or restricted
dependencies SHOULD be published publicly after disclosure review when that
improves access from GitHub Free private consumers.

Restricted automation MAY use private distribution. Public and restricted
implementations SHOULD be separated when they have different trust,
permission, release, or consumer boundaries.

## Version axes

| Axis | Scheme |
| --- | --- |
| Coordinated normative release | CalVer `YYYY.MM[.N]` |
| Golden Path compatibility epoch | `golden-path/v1` |
| Serialized contracts | Independent schema IDs such as `golden-path-metadata/v1` |
| Executable tooling and asset bundle | SemVer |
| Actual execution identity | Exact version plus checksum, or full commit SHA |

`YYYY.MM.N` is a same-month release ordinal, not a compatibility signal.
Prereleases such as `YYYY.MM-rc.N` MUST NOT be production `standardVersion`
values. Published snapshots and assets are immutable; corrections receive a new
release.

## Standard lifecycle

| Lifecycle | New repository | Existing conformance |
| --- | --- | --- |
| `preferred` | Default | Pass |
| `supported` | Allowed | Pass |
| `deprecated` | Not allowed | Warning or pass with required migration evidence |
| `eol` | Not allowed | Fail without an approved exception |

CalVer age alone does not determine lifecycle. A support catalog records status,
announcement, support deadline, successor, and migration path.

A same-major EOL SHOULD be announced at least 180 days ahead. A breaking
contract/schema major MUST keep the previous stable major readable and
migratable for at least 12 months and two subsequent stable coordinated
releases, whichever is longer. Critical security or integrity events MAY
shorten a window with explicit impact and replacement guidance.

## Release manifest

An immutable coordinated release manifest connects:

- standard CalVer and contract/schema IDs;
- exact standard source ref and digest;
- checker, generator, and asset-bundle SemVer and digests;
- supported standard/contract/schema ranges;
- supported platforms;
- changelog and migration guidance; and
- source/build identity and provenance evidence.

The shared implementation imports an accepted standard snapshot by immutable
source ref and digest. It MUST NOT add, weaken, or remove normative rules on its
own.

Rule IDs: `DT-ASSET-*`, `DT-RELEASE-*`.
