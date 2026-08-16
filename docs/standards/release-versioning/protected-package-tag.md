# Protected package-tag publication

This profile is a narrow opt-in for a monorepo that contains an independently
released registry package and an independently deployed service or application.
It allows the package to use an immutable, release-unit-specific protected tag
without promoting or deploying the sibling release unit.

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
- repository-wide `main` promotion would couple package publication to an
  unrelated service or application production effect;
- PR-mediated package prereleases provide a real package-delivery validation
  boundary before final publication; and
- the repository owns the package contract, workflow, tag protection,
  credentials, evidence, and correction path described below.

This profile MUST NOT be selected merely to publish every `dev` commit, avoid
validation, create a shared development deployment, or preserve an unreleased
intermediate contract. A feature pull request MAY build, pack, and test a
package but MUST NOT publish it.

## Release-unit authority and isolation

The repository-local contract MUST declare:

- exactly one package release unit, its native package identity and manifest,
  compatibility surface, build-input closure, changelog, and tag pattern;
- the protected `dev` release-preparation branch and its required checks;
- the repository-owned publication workflow and its serialized concurrency
  identity;
- prerelease and final registry channels;
- every sibling release unit and mutation path that publication must not
  change; and
- release, credential, and correction owners.

The organization standard does not select a package name, version, tag pattern,
trigger path, credential, or current release state for a repository. The
repository MAY express its opt-in contract in prose, configuration, workflow
tests, or another reviewable repository-native form. No central schema or
checker is required.

The package tag is authority only for the declared package version. `main`
remains the production source for sibling services and applications. Package
publication MUST NOT version, commit, tag, publish, deploy, or invoke a workflow
for a sibling release unit and MUST NOT publish an OCI image or object-storage
artifact outside the declared package release unit.

The repository MUST protect the package-specific tag namespace with hosting
rules or an equivalent control that limits creation to the approved publication
workflow and prevents routine update or deletion. Missing or unverified
protection fails before tag creation. Tag publication MUST NOT use a credential
that can push branches or mutate sibling release units.

## PR-mediated publication authorization

A package release pull request MUST change the native package version and its
changelog or release notes. It MAY include only repository-declared supporting
changes that are necessary to build, validate, or publish that same package
release unit. Feature work is validated separately and is not implicitly made a
release merely because it exists on `dev`.

The release change reaches `dev` through a protected pull request after
repository-required checks pass. An authorized maintainer's explicit merge is
publication authorization for the exact merged source and materialized package
version. The pull-request author and the maintainer performing the merge MAY be
the same GitHub identity.

Independent approval is not an organization minimum. A repository MAY require a
distinct qualified approver when its operating model, concrete risk,
regulatory, audit, or contractual obligations justify that stronger control. It
MUST NOT manufacture a second-person gate merely as a generic supply-chain
convention.

Direct-push publication, arbitrary version or source input, a comment, Linear,
a manually created tag, and a standalone evidence change are not publication
authorization.

## Repository-owned idempotent workflow

After the release pull request merges, one repository-owned workflow MUST:

1. derive the package identity, version, channel, source, changelog, and tag
   from the merged repository state;
2. verify required checks, package closure, deterministic build, content
   allowlist, credential hygiene, tag protection, and sibling isolation;
3. build, test, and pack from that immutable source;
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
or verify only the exact source and version already authorized by the merge.
The same rules apply when an earlier run stopped before either identity existed
or after the exact tag was created but before registry publication completed.
No parallel publication control plane is required. A different source, version,
package, integrity, or conflicting remote state requires a new release pull
request and SemVer correction as applicable.

Standard `2026.08.8` retires the former custom intent, admission, recovery, and
completion control plane; repositories MUST NOT keep a compatibility mode or
dual policy for it.

## Development prerelease and final publication

A prerelease MUST:

- use the final package identity rather than a separate development package;
- use native SemVer prerelease syntax and the repository-declared non-`latest`
  channel, normally `next`;
- build, test, pack, and publish only the declared package release unit;
- verify registry identity, integrity, clean exact-version installation, and
  representative package execution;
- verify that `latest` and every sibling release unit remain unchanged; and
- emit the native evidence defined below.

Consumers MUST use an exact version and lockfile integrity. A mutable channel is
discovery metadata and MUST NOT be the production dependency identity.

A final release pull request materializes a new final native SemVer and
changelog. The same idempotent workflow publishes that exact version to
`latest`. It MUST NOT promote prerelease bytes in place, create source, version,
or changelog commits, push `dev` or `main`, or require repository-wide `main`
promotion for the package.

## Permissions and credentials

Permissions and credentials MUST be explicit and limited to the responsibility
that needs them:

| Responsibility | Minimum authority |
| --- | --- |
| Source and policy validation | `contents: read` and repository-required read access |
| Protected tag creation | Package-tag mutation credential scoped to the declared tag namespace; no branch-push authority |
| Native registry publication | `packages: write` or native equivalent, exposed only to the publish step |
| Private package installation | `packages: read` or native equivalent, exposed only to the install step |
| Post-publication execution | No registry credential or token environment after installation |

Write-capable credentials MUST be absent from feature validation and consumer
execution. Secrets MUST NOT be written to manifests, lockfiles, logs, evidence
artifacts, or packed package contents. A repository MAY split validation, tag
creation, registry publication, and verification into jobs when that is needed
to enforce these boundaries; they remain one repository-owned idempotent
publication workflow and state machine.

## Registry-native evidence

The minimum evidence is:

- merged source SHA and immutable package tag;
- GitHub Actions publication run;
- registry exact version and native integrity;
- applicable changelog or release notes;
- clean exact-version install, import, initialization, and representative
  execution; and
- workflow isolation showing that no Calculator, service, OCI/ECS,
  object-storage, or other sibling release-unit mutation occurred.

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

Selecting repositories, including Core, MUST align their repository-owned
workflow with this profile before their next publication. They migrate directly
to this lifecycle without dual readers, dual workflows, compatibility mode, or
a central migration control plane.

## Out of scope

This profile does not create a central release queue, repository current-version
registry, package-name registry, shared publication workflow, cross-repository
approval gate, or evidence database. It does not publish a package, deploy a
service, clean object storage, mutate durable state, or define a repository's
initial package name or version.
