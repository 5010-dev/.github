# Protected package-tag publication

This profile is a narrow opt-in for a monorepo that contains an independently
released registry package and an independently deployed service or application.
It allows the package to use an immutable, release-unit-specific protected tag
as publication authority without promoting or deploying the sibling release
unit.

Validated `main` remains the organization default. A repository that does not
materialize and enforce this profile's repository-local contract remains on the
validated-`main` profile. Selecting this profile does not make `dev` a deployment
target and does not change the branch roles in `CONTRIBUTING.md`.

## Selection criteria

A repository MAY select this profile only when all of the following are true:

- a registry package and a service or application are separate release units
  under [Artifact and version profiles](./profiles.md);
- the package has independent consumers, compatibility surface, version,
  publication cadence, correction boundary, and production effect;
- repository-wide `main` promotion would couple package publication to an
  unrelated service or application production effect;
- reviewed package prereleases provide a real package-delivery validation
  boundary before final publication; and
- the repository owns the contract, workflows, rulesets, credentials, evidence,
  and recovery described below.

This profile MUST NOT be selected merely to publish every `dev` commit, avoid
validation, create a shared development deployment, or preserve an unreleased
intermediate contract. A feature pull request MAY build, pack, and test a package
but MUST NOT publish it to a registry.

## Authority and release-unit isolation

The repository-local contract MUST declare exactly one package release unit per
profile document. It MUST also declare every sibling release unit whose mutation
paths or workflows could create another production effect.

For the declared package:

- a reviewed release-preparation change is admitted from the exact `dev`
  `before..after` merge diff;
- the admitted `after` commit is the immutable publication source;
- the workflow derives an immutable package tag from the declared tag pattern
  and exact manifest version; and
- tag creation and registry publication occur in one protected, serialized run.

The repository MUST protect the declared tag namespace with hosting rules or an
equivalent control that limits creation to the approved publication authority
and prevents routine update or deletion. A missing or unverified protection
state fails before tag creation. Any hosting-specific tag-write credential MUST
be isolated to the tag mutation step and MUST NOT authorize branch pushes.

The protected tag is authority only for that package version. `main` remains the
production source for sibling services and applications. Package publication
MUST NOT version, commit, tag, publish, deploy, or invoke a workflow for a sibling
release unit and MUST NOT publish an OCI image or object-storage artifact unless
that artifact belongs to the same declared package release unit.

## Repository-local opt-in contract

The repository SHOULD store the contract at
`.github/release-policy/protected-package-tag.v1.json`. The contract MUST conform
to [`protected-package-tag-profile/v1`](./schemas/protected-package-tag-profile-v1.schema.json)
and declare:

- the package release-unit ID, native package identity, registry, compatibility
  contract, build-input closure, native manifest identity and version selectors,
  changelog, and tag pattern;
- the `dev` source ref, release-intent directory, validation workflow, and
  publication workflow;
- the allowed release-preparation paths and every sibling release-unit mutation
  path;
- prerelease and final registry channels;
- the fixed least-privilege and publication-effect invariants; and
- release, credential, and recovery owners.

The contract contains no current version or pending-release queue. Exact
versions live in native manifests and individual reviewed intents. The
organization standard does not select a package name, version, tag pattern,
trigger path, credential, or current release state for a repository.

## Release intent and exact merge-diff admission

A release-preparation pull request MUST add one immutable intent conforming to
[`package-release-intent/v1`](./schemas/package-release-intent-v1.schema.json).
The intent contains only the release-unit ID, channel, exact version, and source
boundary needed for admission. Its `source.baseCommit` is the full commit SHA on
which the reviewed release-preparation diff is based; its `source.ref` is
`refs/heads/dev`.

The admission workflow MUST take `before`, `after`, and ref from the protected
merge event. It MUST derive release unit, channel, version, and tag from the
contract, intent, manifest, and Git diff. It MUST NOT accept those values from
`workflow_dispatch`, a comment, a mutable tag, or another arbitrary input.

Admission succeeds only when all of the following are true:

1. `before` and `after` are exact full commits, `before` is an ancestor of
   `after`, and the event ref and intent ref are the contract's `dev` ref.
2. The intent's base commit equals `before`. A rebase or intervening merge makes
   the intent stale until the reviewed intent is refreshed.
3. The exact `before..after` diff adds one intent and does not modify, rename, or
   delete another intent.
4. The added intent is the only repository intent for the same release-unit and
   version identity.
5. The declared JSON or TOML native manifest exists at both commits, its package
   identity equals the contract at both commits, and exactly one semantic
   manifest value changes: the configured version field.
6. The intent version equals the materialized `after` version, differs from the
   `before` version, and matches the requested channel.
7. Every diff entry adds or modifies an allowed release-preparation path. A
   deletion, rename, copy, type change, or sibling mutation fails closed even
   when its path otherwise matches an allowed pattern.
8. The derived tag, native manifest, intent, source, channel, and registry state
   are unambiguous and mutually consistent.

Missing, previously present, modified, stale, duplicate, or conflicting intent
fails closed. Multiple release units or versions in one admission diff fail
closed. A structurally valid intent is not publication permission unless the
exact diff, protected review boundary, remote tag and registry state, package
closure, and evidence checks also pass.

The dependency-free reference checker
[`check-protected-package-tag-admission.py`](../../../scripts/docs/check-protected-package-tag-admission.py)
implements the local Git, JSON, and TOML admission rules. It does not publish, inspect
rulesets or pull-request approvals, query a registry, or replace repository-owned
workflow checks. Repositories own a pinned invocation or an equivalent tested
implementation.

## Development prerelease

A prerelease MUST:

- use the final package identity rather than a separate development package or
  registry;
- use native SemVer prerelease syntax and the repository-declared non-`latest`
  channel;
- build, test, and pack once from the admitted source commit;
- create an immutable package-specific tag and publish the matching version in
  the same serialized run;
- verify registry identity, integrity, clean exact-version installation, and
  representative package execution;
- verify that `latest` and every sibling release unit remain unchanged; and
- emit durable evidence.

Consumers MUST use an exact version and lockfile integrity. A mutable channel is
discovery metadata and MUST NOT appear as the production dependency identity.

## Final package publication

A final release-preparation change MUST materialize a new final native SemVer,
changelog, and `final` intent on `dev`. Before publication, the repository MUST
verify the package closure and evidence selected by its package profile,
including clean installation and execution outside the package build workspace
when that is the declared consumer gate.

The protected workflow creates the immutable final package tag from the admitted
commit and publishes that exact version to `latest`. It MUST NOT promote
prerelease bytes in place, create source, version, or changelog commits, push
`dev` or `main`, or require repository-wide `main` promotion for the package.

## Permissions and credentials

Permissions MUST be explicit and job-scoped:

| Responsibility | Minimum permission |
| --- | --- |
| Source and policy validation | `contents: read` |
| Private package installation or consumer execution | `packages: read` |
| Native registry publication | `packages: write` |

`packages: write` MUST be absent from validation and consumer jobs. The
write-capable token or credential MUST be exposed only to the native publication
step in its publication job. A consumer job MAY also receive `contents: read`
only when checkout is required. Secrets MUST NOT be written to manifests,
lockfiles, logs, evidence artifacts, or packed package contents.

GitHub Actions permissions are job-scoped, so publication MUST use a dedicated
job with `packages: write` and only trusted setup, mutation, and verification
steps. A separately minted registry credential is passed only to the native
publish step. A hosting-specific tag credential follows the narrower tag rule
above; it is not a general source-write permission.

## Serialization, immutability, and recovery

Publication MUST serialize on release-unit and version identity. Concurrency
cancellation MUST be disabled before the first irreversible tag or registry
mutation.

Before mutation, the workflow MUST read the tag and registry. If neither exists,
it may create and publish. If both already identify the same source, version,
package, and integrity, a retry performs idempotent verification and records that
outcome. If either identity is partial or conflicting, the workflow fails closed
and records the completed phase and owner action.

Published versions and tags MUST NOT be moved, overwritten, deleted for routine
recovery, or reused. A prerelease correction uses a new prerelease version. A
final correction uses a new final SemVer. A registry-native dist-tag correction
MAY move a mutable alias only through an authorized, evidenced recovery action;
it never changes immutable package identity.

## Default-profile regression

Opt-in is repository-local and has no central auto-enrollment workflow. A
repository without the profile contract continues to publish only from validated
`main` under its existing release workflow.

The Design System does not select this profile. Its existing `dev` release
preparation, `dev` to `main` promotion, and `main` package publication contract
remain unchanged. This profile MUST NOT change its tag format, workflow trigger,
Changesets behavior, package version, or release permissions.

The time-bounded exact-ref observation and central executable regression are in
the [2026-08-12 validation record](./validation/2026-08-12-protected-package-tag-profile.md).

## Out of scope

This profile does not create a central release queue, repository current-version
registry, package-name registry, tag-pattern registry, publication workflow, or
cross-repository approval gate. It does not publish a package, deploy a service,
clean object storage, mutate durable state, or define a repository's initial
package name or version.
