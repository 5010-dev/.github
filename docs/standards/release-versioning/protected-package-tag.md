# Protected package-tag publication

This profile is a narrow opt-in for a monorepo that contains an independently
released registry package and an independently deployed service or application.
It binds package prereleases to `dev` and final package publication to `main`
without coupling either package publication to the sibling release unit.

Validated `main` remains the organization default. A repository that does not
explicitly select and enforce this profile continues to publish only from
validated `main`. Selecting this profile does not make `dev` a deployment target
or change the branch roles in `CONTRIBUTING.md`.

## Selection criteria

A repository MAY select this profile only when all of the following are true:

- a registry package and a service or application are separate release units
  under [Artifact and version profiles](./profiles.md);
- the package has independent consumers, compatibility surface, version,
  publication cadence, correction boundary, and production effect;
- repository-wide `main` promotion would otherwise couple package validation or
  publication to an unrelated sibling release effect;
- immutable package prereleases provide a real development integration boundary
  before final publication; and
- the repository owns the package closure, branch/channel contract, workflow,
  tag protection, credentials, evidence, and correction path described below.

This profile MUST NOT be selected merely to publish every `dev` commit, avoid
validation, create a shared development deployment, or preserve an unreleased
intermediate contract. A pull request before merge MAY build, pack, and test a
package but MUST NOT publish it.

## Release-unit authority and package closure

The repository-local contract MUST declare:

- exactly one package release unit, its native package identity and manifest or
  staging-manifest strategy, compatibility surface, changelog or release notes,
  and tag pattern;
- the package build-input closure, including transitive source, generated
  payload, public exports, release metadata, and build/pack inputs that can
  change the published package;
- protected `dev` and `main` branch boundaries and their required checks;
- the repository-owned publication engine and serialized concurrency identity;
- the Stable target source, unique prerelease sequence, prerelease and final
  registry channels, and version materialization rule;
- every sibling release unit and mutation path that publication must not
  change; and
- release, credential, and correction owners.

Package-only and shared-input changes inside the declared closure are
package-relevant. Sibling service-only and documentation-only changes outside
the closure are package-neutral. A simple path filter MAY avoid unnecessary
workflow startup, but a repository-owned closure checker is authoritative for
publication and prerelease-to-final equivalence.

The organization standard does not select a package name, version, tag pattern,
path layout, Stable-target file, sequence source, staging implementation,
credential, or current release state for a repository. The repository MAY
express its opt-in contract in prose, configuration, workflow tests, or another
reviewable repository-native form. No central schema or checker is required.

The package tag is authority only for the declared package version. `main`
remains the production source for sibling services and applications. Package
publication MUST NOT version, commit, tag, publish, deploy, or invoke a workflow
for a sibling release unit and MUST NOT publish an OCI image or object-storage
artifact outside the declared package release unit.

The repository MUST protect existing package-specific tags with hosting rules or
an equivalent control that prevents update, deletion, and non-fast-forward
mutation. Missing or unverified protection fails before tag creation. The
supported publication workflow MUST re-read tag and registry state immediately
before mutation and create only the exact absent tag for its verified source.

The organization does not require hosting-level exclusive tag-creator identity.
For GitHub Packages, the default is a job-scoped repository `GITHUB_TOKEN` with
`contents: write` only in the tag-creation job and `packages: write` only in the
separate registry-publication job. The workflow MUST NOT perform a branch-ref or
sibling release-unit mutation with the tag credential. A repository MAY adopt a
stronger dedicated credential or creation restriction when concrete risk or an
external obligation justifies it, but that control is not an independent release
authorization merely because it uses another application identity.

## Branch and channel authority

The protected branch merge is publication authorization; there is no separate
release-intent control plane.

### Development prerelease

A required-check-passing pull request that changes the package closure and
merges to `dev` authorizes one unique prerelease for that merged package state.
The pull request SHOULD update the owning changelog or release notes and MUST
leave the repository-owned Stable target consistent with the intended final
compatibility version. An authorized maintainer's explicit merge is sufficient;
the author and merger MAY be the same identity.

The prerelease MUST:

- use native SemVer prerelease syntax derived from the Stable target and a
  serialized repository-owned unique sequence;
- use the repository-declared non-`latest` channel, normally `next`;
- build, test, pack, and publish only the declared package release unit;
- verify registry identity, integrity, exact-version clean installation, and
  representative package execution;
- verify that `latest` and every sibling release unit remain unchanged; and
- emit the native evidence defined below.

A package-neutral merge to `dev` MUST NOT publish a package. A distinct
package-relevant merge receives a distinct prerelease identity. A retry of the
same authorized publication reuses the same resolved version and never allocates
a successor merely because the workflow was retried.

### Final publication

Fast-forward promotion of `dev` to `main` is authorization to publish the
repository-owned Stable target only when the promoted package state matches an
eligible prerelease under the equivalence contract below. A final package MUST
NOT be published from `dev`, a feature branch, a manual version input, or a
separate version-only release pull request.

The final publication MUST:

- use the exact Stable SemVer target and `latest`;
- build from the promoted `main` package closure;
- verify an eligible prerelease with the same package-closure and runtime-payload
  identities before mutation;
- verify that every source change between the prerelease and final sources is
  package-neutral, or require a new prerelease;
- preserve sibling release-unit isolation; and
- follow the same idempotent tag/registry state model as prerelease publication.

A promotion whose package closure is unchanged from the previous final, when
one exists, MUST NOT publish a package. Final package publication is a package
release effect of the production branch, but it does not itself deploy or
authorize a sibling service, application, or environment.

Independent approval is not an organization minimum. A repository MAY require a
distinct qualified approver when its operating model, concrete risk,
regulatory, audit, or contractual obligations justify that stronger control. It
MUST NOT manufacture a second-person gate merely as a generic supply-chain
convention.

Direct-push publication, arbitrary version or source input, a comment, Linear,
a manually created tag, and a standalone evidence change are not publication
authorization.

## Version materialization

The repository MUST own one Stable target for the package. It MAY keep a
non-publishable template version in source and inject the resolved prerelease or
final version only into package staging output, or use another repository-native
strategy that preserves the same branch/channel contract.

The prerelease sequence MUST be serialized, unique, and durable enough that:

- two distinct package-relevant `dev` merges cannot publish the same version;
- a retry of the same authorized merge resolves the same version;
- a published version is never overwritten or reused;
- a new prerelease identity is never derived from a Stable target whose final
  version is already published; and
- final publication resolves the exact Stable target rather than deriving a
  new version from a moving channel.

Changing the Stable target and the human-readable package change record belongs
to ordinary package-relevant work. This profile MUST NOT require a second
version-only or evidence-only pull request after feature integration.

## Prerelease-to-final equivalence

The prerelease and final registry archives need not be byte-identical because
the native version and version-derived metadata differ. The final workflow MUST
instead prove:

- equal package build-input closure identity or digest;
- equal compiled runtime payload identity or digest;
- equal public export and type surface;
- equal package file set except for declared version-derived generated metadata;
  and
- a package-neutral diff between the recorded prerelease source and the final
  `main` source.

The prerelease and final source SHAs MUST be recorded separately. Identical
repository SHAs are not required when intervening changes affect only a sibling
service or documentation outside the package closure. If any package or shared
input changed, the repository MUST publish and validate a new prerelease before
final publication.

## Repository-owned idempotent publication engine

Prerelease and final channels MUST use the same repository-owned publication
engine and state model. Branch, version form, channel, and equivalence checks are
inputs to that engine rather than separate recovery workflows.

For each authorized exact version, the engine MUST:

1. derive the package identity, version, channel, source, package closure,
   changelog or release notes, and tag from protected repository state;
2. verify required checks, closure routing, deterministic build, content
   allowlist, credential hygiene, tag protection, and sibling isolation;
3. materialize the version in staging and build, test, and pack from the selected
   immutable source;
4. read the protected tag and exact registry version before mutation;
5. apply the state table below in a serialized, non-canceling publication
   section;
6. re-read registry state immediately before and after publication; and
7. verify native integrity, expected channel, clean exact-version installation
   and representative execution, and absence of sibling effects.

| Protected tag | Registry exact version | Outcome |
| --- | --- | --- |
| Absent | Absent | Create the tag from the verified source, then publish the exact version |
| Exact source | Absent | Keep the tag unchanged and resume registry publication from the same immutable source |
| Exact source | Exact version and integrity | Verification success; do not republish |
| Missing, moved, or conflicting | Present or unknown | Fail closed |
| Any | Version or integrity conflict | Fail closed and use a new SemVer correction |

The workflow MUST treat a registry-only state as conflicting and fail closed.
An ambiguous or unauthorized tag or registry query also fails closed. It MUST
NOT delete, move, recreate, overwrite, or reuse a published tag or version.

A workflow rerun is not a new release authorization. It MAY idempotently finish
or verify only the exact source and version already authorized by the branch
merge.
The same rules apply when an earlier run stopped before either identity existed
or after the exact tag was created but before registry publication completed.
No parallel publication control plane is required. A different source, version,
package, integrity, channel, or conflicting remote state requires a new package
version as applicable.

Under Standard `2026.08.10`, the former custom intent, admission, recovery, and
completion control plane remains retired; repositories MUST NOT keep a
compatibility mode or dual policy for it.

## Consumer exactness and artifact provenance

Development integration artifacts MUST consume an exact prerelease. Production
artifacts MUST consume an exact final version. A mutable `next`, `latest`, or
equivalent channel MAY be used to discover a new candidate, but MUST NOT be the
install identity for a retry, replay, rebuild, or redeployment.

The exact consumer input MUST carry at least the package version and native
registry integrity. When the selecting repository publishes closure and runtime
payload identities, the consumer SHOULD retain those identities and the package
tag/source in its artifact provenance. The exact input MAY be materialized in a
native lockfile or in a repository-owned immutable build-input record and
generated dependency layer.

The organization does not require a consumer source commit that replaces every
prerelease pin with the corresponding final pin. A branch-aware resolver MAY
discover a candidate once and record the exact immutable input outside the root
manifest/lockfile, provided that:

- its channel policy is repository-owned and reviewable;
- ordinary dependency bootstrap remains frozen;
- installation uses the recorded exact version rather than a floating channel;
- retries and rebuilds reuse the same record; and
- the resulting artifact records its source and exact package input.

Production rebuild and redeployment use the immutable consumer artifact or its
retained exact build-input record, not a fresh resolution of `latest`.

## Permissions and credentials

Permissions and credentials MUST be explicit and limited to the responsibility
that needs them:

| Responsibility | Minimum authority |
| --- | --- |
| Source and policy validation | `contents: read` and repository-required read access |
| Protected tag creation | Job-scoped repository token with `contents: write`; the job creates only the verified exact package tag and performs no branch mutation |
| Native registry publication | `packages: write` or native equivalent, exposed only to the publish step |
| Private package installation | `packages: read` or native equivalent, exposed only to the install step |
| Post-publication execution | No registry credential or token environment after installation |

Write-capable credentials MUST be absent from feature validation and consumer
execution. Secrets MUST NOT be written to manifests, lockfiles, generated
dependency state, logs, evidence artifacts, or packed package contents. A
repository MAY split validation, tag creation, registry publication, and
verification into jobs when needed to enforce these boundaries; they remain one
repository-owned idempotent publication engine and state machine.

A tag ruleset for this profile MUST reject update, deletion, and
non-fast-forward mutation of the declared package tags. It MAY allow creation
without bypass actors when the repository workflow applies the exact-source and
fresh-state checks above. The profile does not require a dedicated GitHub App,
private key, App-token mint action, or an additional all-branch exclusion
ruleset. Repositories that retire such optional controls remove them only after
the replacement workflow and live protection have been verified.

## Registry-native evidence

The minimum evidence is:

- branch channel, exact package version, recorded source SHA, and immutable
  package tag;
- GitHub Actions publication run;
- registry exact version and native integrity;
- applicable changelog or release notes;
- clean exact-version install, import, initialization, and representative
  execution; and
- workflow isolation showing that no Calculator, service, OCI/ECS,
  object-storage, or other sibling release-unit mutation occurred.

Final publication additionally records the selected prerelease, both source
SHAs, package-closure identity, runtime-payload identity, and the package-neutral
source-diff result. This is the smallest evidence that distinguishes package
equivalence from repository-SHA equality; it is not a new evidence control
plane.

This evidence MUST distinguish new publication, safe tag-only resume,
verification-only exact state, and fail-closed conflict. GitHub, the registry,
and the repository's changelog are the durable native surfaces. Linear, a
separate evidence pull request, or a repository evidence file does not create
or extend publication authority.

Package visibility, repository association, and consumer grants are setup and
access configuration. Repositories verify them when establishing or changing
access and during consumer handoff. They are not artifact provenance and MUST
NOT be a terminal gate for every otherwise exact publication.

## Correction and recovery

Published tags, versions, and package contents are immutable. A defective or
conflicting prerelease uses a new prerelease version; a defective or conflicting
final release uses a new final SemVer. A registry-native mutable channel MAY move
only through an authorized, evidenced repository workflow and never changes the
underlying immutable package identity.

Runtime or durable state is non-disposable. This profile does not authorize
deletion, reset, reseed, truncation, rewriting, or migration of deployed state.
It also does not authorize manual publication, tag movement, tag deletion,
registry overwrite, credential expansion, ruleset weakening, or sibling
deployment as a recovery shortcut.

## Default-profile regression

Opt-in is repository-local and has no central auto-enrollment workflow. A
repository without the profile contract continues to publish only from
validated `main` under its existing release workflow.

The Design System does not select this profile. Its existing Changesets
preparation on `dev`, `dev` to `main` promotion, and `main` package publication
contract remain unchanged. This profile MUST NOT change its repository files,
tag format, workflow trigger, approval policy, release permissions, or
Changesets behavior.

The historical validation records in this directory preserve time-bounded
evidence for superseded policy versions. They are non-normative and their prior
runs, source SHAs, files, and implementation details are not requirements of the
current profile.

Selecting repositories MUST align their repository-owned workflow with this
profile before their next package-relevant merge. They migrate directly to this
lifecycle without dual workflows, compatibility mode, custom intent records, or
a central migration control plane. Existing published versions and immutable
tags remain unchanged.

## Out of scope

This profile does not create a central release queue, repository current-version
registry, package-name registry, shared publication workflow, cross-repository
approval gate, or evidence database. It does not publish a package, deploy a
service, clean object storage, mutate durable state, or define a repository's
package name, current version, path layout, or prerelease sequence implementation.
