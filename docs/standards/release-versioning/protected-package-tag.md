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
- PR-mediated package prereleases provide a real package-delivery validation
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

- a release-preparation pull request reaches `dev` through a protected, explicit
  maintainer merge after repository-required checks pass;
- that PR-merged change is admitted from the exact `dev` `before..after` diff;
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
- the `dev` source ref, release-intent directory, validation workflow,
  publication workflow, distinct recovery-authorization directory, and workflow
  that owns recovery admission;
- a third, non-overlapping tag-only completion-intent directory and a distinct
  completion workflow whose only allowed mutation is registry package
  publication and whose tag mutation is explicitly forbidden;
- a fourth, non-overlapping tag-only completion-recovery directory, distinct
  workflow, exact successor chain, and executable permission preflight for a
  completion failure that stopped before artifact retrieval and mutation;
- the allowed release-preparation paths and every sibling release-unit mutation
  path;
- prerelease and final registry channels;
- the fixed least-privilege and publication-effect invariants; and
- release, credential, and recovery owners.

The contract contains no current version or pending-release queue. Exact
versions live in native manifests and individual PR-merged intents. The
organization standard does not select a package name, version, tag pattern,
trigger path, credential, or current release state for a repository.

Contract path patterns are segment-aware. `*`, `?`, and bracket expressions
match characters within one path segment and never match `/`. A `**` segment
matches zero or more complete path segments. Repositories MUST use `**` when a
declared closure or mutation boundary intentionally includes arbitrary depth.

## Protected PR merge boundary

A selecting repository MUST require pull requests for the declared `dev` source
ref and MUST prevent a direct push or bypass from creating an admitted
release-intent update. The repository's required validation checks MUST remain
enforced before merge. An authorized maintainer's explicit merge after those
checks pass is sufficient release authorization. The pull-request author and
the maintainer performing the merge MAY be the same GitHub identity.

Independent approval is not part of the minimum organization contract. A
GitHub ruleset with `required_approving_review_count: 0` and
`require_last_push_approval: false` is conformant when it still requires pull
requests for `dev`, admits no direct-push bypass for the publication path, and
preserves repository-required checks. This profile-local restriction does not
change the organization allowance for direct `dev` development in repositories
that do not select the profile.

A repository MAY strengthen this boundary with one or more independent
approvals when it has a qualified reviewer and a real two-person operating
model, or when concrete risk, regulatory, audit, or contractual evidence
requires separation. It MUST NOT impose a distinct reviewer merely as a generic
supply-chain convention. An uninformed or rubber-stamp approval is not a
meaningful control.

These terms are distinct in this profile:

- **reviewable** means a PR exposes the diff, CI, and evidence;
- **PR-mediated** means the change can reach `dev` only through that protected
  pull-request path;
- **authorized** means an authorized maintainer explicitly merges the PR after
  required checks pass; and
- **independently approved** means a distinct qualified person approves it.

Reviewability, PR mediation, and explicit merge authorization are mandatory.
Independent approval is repository-owned and optional unless a concrete
requirement makes it mandatory.

## Release intent and exact merge-diff admission

A release-preparation pull request MUST add one immutable intent conforming to
[`package-release-intent/v1`](./schemas/package-release-intent-v1.schema.json).
The intent contains only the release-unit ID, channel, exact version, and source
boundary needed for admission. Its `source.baseCommit` is the full commit SHA on
which the pull-request release-preparation diff is based; its `source.ref` is
`refs/heads/dev`.

The intent directory is an append-only protocol directory. Every entry MUST use
an unambiguous UTF-8 repository path and be a regular UTF-8 JSON file conforming
to `package-release-intent/v1`; placeholder, README, symlink, mixed-version, and
unrelated files are forbidden. Historical intents remain present so a later
admission can detect duplicate release-unit and version identity.

The admission workflow MUST take `before`, `after`, and ref from the protected
merge event. It MUST derive release unit, channel, version, and tag from the
contract, intent, manifest, and Git diff. It MUST NOT accept those values from
`workflow_dispatch`, a comment, a mutable tag, or another arbitrary input.

Admission succeeds only when all of the following are true:

1. `before` and `after` are exact full commits, `before` is an ancestor of
   `after`, and the event ref and intent ref are the contract's `dev` ref.
2. The intent's base commit equals `before`. A rebase or intervening merge makes
   the intent stale until the pull-request intent is refreshed.
3. The exact `before..after` diff adds one intent and does not modify, rename, or
   delete another intent.
4. The added intent is the only repository intent for the same release-unit and
   version identity.
5. The declared JSON or TOML native manifest is a regular file at both commits,
   its package identity equals the contract at both commits, and exactly one
   semantic manifest value changes: the configured version field.
6. The intent version equals the materialized `after` version, has strictly
   greater SemVer precedence than the `before` version, and matches the requested
   channel. Build metadata alone does not increase precedence.
7. Every diff entry adds or modifies an allowed release-preparation path. A
   deletion, rename, exact-content copy, type change, non-regular file, or sibling
   mutation fails closed even when its path otherwise matches an allowed pattern.
8. The derived tag, native manifest, intent, source, channel, and registry state
   are unambiguous and mutually consistent.

Missing, previously present, modified, stale, duplicate, or conflicting intent
fails closed. Multiple release units or versions in one admission diff fail
closed. A structurally valid intent is not publication permission unless the
protected PR merge boundary, repository-required checks, exact diff, remote tag
and registry state, package closure, and evidence checks also pass.

One admitted release intent may start at most one publication attempt. A normal
Actions rerun, `workflow_dispatch`, comment, manual tag, or repeated evaluation
of the historical `before..after` diff does not renew mutation authority. An
identical existing tag and registry version may be verified idempotently, but an
attempt that ended before either identity existed requires the separate recovery
authorization below before the same version may be attempted again.

## Pre-mutation recovery authorization

A terminal failed attempt is not a published release when it created neither
the protected package tag nor the exact registry version. The repository MAY
preserve the intended version only through a new protected pull request that
adds one immutable record conforming to
[`package-release-recovery-intent/v1`](./schemas/package-release-recovery-intent-v1.schema.json).
The historical package release intent remains byte-identical, present, and
append-only; it is referenced by the recovery record and is never edited,
renamed, deleted, or treated as a new intent.

The recovery record binds:

- release unit, exact version, and channel;
- the original release-intent path;
- the exact source commit and GitHub Actions run that failed terminally;
- reviewed claims that immutable mutation did not start and that both the
  derived package tag and exact registry version are absent;
- the exact current `dev` ref and full base commit; and
- reason `pre-mutation-no-immutable-identity`.

Recovery admission succeeds only when the protected `before..after` diff adds
exactly that one record directly under the declared recovery directory. The
profile contract, native manifest, original intent, workflows, changelog, and
every other repository path remain unchanged. The record's base equals
`before`; release unit, version, channel, package identity, manifest, historical
intent, and derived tag agree; the failed source is on the protected source's
first-parent history, structurally matches either the original normal admission
or the latest recovery admission for that identity, and has not already been
named by another recovery record; and the historical intent is byte-identical
without any intervening protected-history mutation from the failed source
through recovery `after`.
The admitted recovery `after` commit becomes the new publication source.

The repository workflow MUST then re-read the protected branch and tag rules,
required checks, failed Actions run, authorization-use history, tag, registry
version, manifest, intent, and exact `before..after` admission before mutation.
The record's no-identity fields are authorization claims, not a substitute for
those live queries. Recovery is permitted only when the prior run is terminal,
failed before tag or registry mutation, and both remote identities are still
absent without ambiguity or conflict. The resulting tag and registry version
MUST bind to the admitted recovery source and its built integrity.

Each recovery record may start at most one admitted attempt. It MUST NOT be
modified, reused by an Actions rerun, or replayed through manual dispatch. If
that attempt also fails before immutable mutation, another protected pull
request must add another recovery record bound to the newly failed run and
source. A different run URL does not permit another record to name a previously
used failed source, an unrelated later commit, or a source that skips the latest
recovery authorization. Neither the historical release intent nor a previous
recovery record is renewed authority, and their protected-history paths remain
addition-only.

This path rejects tag-only, registry-only, conflicting, or otherwise partial
immutable state. An exact tag-only attempt-1 failure may use only the separate
completion contract below; it never becomes pre-mutation recovery. An exact
tag/version pair whose publication completed but later verification failed
remains under immutable-identity verification or correction. Pre-mutation
recovery never permits rebuilding, deleting, moving, overwriting, or reusing an
identity, a manual tag or package, ruleset relaxation, automatic successor
version, or sibling release-unit effect.

## Tag-only partial-publication completion authorization

A terminal failed publication is tag-only when its admitted attempt 1 created
the exact derived immutable package tag and terminated before the exact registry
version existed. The repository MAY complete only the missing registry identity
through a new protected pull request that adds one immutable record conforming
to
[`package-release-tag-only-completion-intent/v1`](./schemas/package-release-tag-only-completion-intent-v1.schema.json).
This is neither a workflow rerun nor pre-mutation recovery. The tag and the
original failed publication remain immutable evidence.

The completion record binds:

- release unit, exact version, channel, derived tag, and expected dist-tag;
- the unchanged original release-intent path;
- the exact failed publication source, Actions run URL, run attempt `1`,
  terminal failure, tag-present state, and registry-version-absent state;
- the exact release intent or pre-mutation recovery record that admitted the
  failed publication source;
- the retained Actions artifact ID, name, expiry, archive SHA-256 digest,
  tarball file name and SHA-256, native package integrity, and embedded source
  commit;
- the exact current `dev` ref and full base commit; and
- reason `tag-only-partial-publication`.

The profile contract MUST declare a tag-only completion directory that is
distinct and non-overlapping with the normal and pre-mutation recovery intent
directories. It MUST also declare a distinct completion workflow. The workflow
MUST NOT be the normal validation, publication, or recovery workflow. Its only
allowed publication effect is the missing registry package version; tag
creation, branch or source mutation, sibling release-unit effects, OCI or
object-storage publication, and service or application deployment remain
forbidden.

Completion admission succeeds only when the protected `before..after` diff adds
exactly one record directly under that directory and changes no other path. The
profile, workflow, native manifest, changelog, original intent, prior recovery
records, and all prior completion records remain unchanged and append-only. The
record base equals `before`; the unchanged manifest version, package identity,
channel, original intent, derived tag, expected dist-tag, failed source, failed
authorization, retained-artifact source, and record all agree. The failed source
must be on protected first-parent history and structurally reconstruct the exact
normal release or latest pre-mutation recovery admission named by the record. A
release-unit/version identity and failed run may each be named by at most one
completion record.

The static record fields are reviewed claims, not remote truth. Before
publication, repository automation MUST re-read and prove all of the following:

1. the protected source, required checks, exact completion admission, protected
   tag rules, and one-record authorization-use history remain valid;
2. the named failed run belongs to the selecting repository, was triggered by a
   `push` to the declared `dev` ref, has the exact failed source, is run attempt
   `1`, is terminal `failure`, and executed the declared normal publication or
   pre-mutation recovery workflow selected by the record's authorization type;
   its trusted job or terminal evidence proves that the exact tag-creation phase
   completed and registry publication failed before creating the exact version;
3. the existing immutable tag has the exact derived name and failed-publication
   source and has not moved, been deleted, or been recreated;
4. the exact registry version is absent without ambiguity;
5. the retained artifact is unexpired, belongs to that run and source, and its
   artifact ID, name, archive digest, tarball file name and SHA-256, native
   integrity, and embedded source exactly match the record; and
6. the expected dist-tag prerequisite, package identity, registry, credentials,
   package-only effects, and sibling isolation still hold.

The workflow MUST download that exact retained artifact and MUST NOT rebuild,
repack, substitute, or otherwise derive replacement bytes. If the artifact is
missing, expired, unavailable, ambiguous, or mismatched, automation fails closed
and returns to the central policy owner; it does not rebuild or automatically
advance the version.

Only the first workflow run triggered by the newly merged completion record,
and only run attempt `1` of that workflow, may expose the write credential and
create the absent exact registry version. An Actions rerun or a second workflow
run MUST be mutation-disabled before credential setup regardless of remote
state. A rerun or later run MAY perform read-only verification but never
publication.

Immediately before releasing the registry mutation job, admission and live
verification MUST read tag and registry together and use exactly this state
table:

| Tag state | Exact registry version | Required outcome |
| --- | --- | --- |
| Exact derived tag at the failed source | Absent | The first authorized completion run at attempt 1 MAY publish only the retained exact version |
| Exact derived tag at the failed source | Present with exact package, integrity, source, and dist-tag | Verification-only; do not publish or expose mutation authority |
| Missing, moved, recreated, or conflicting | Any | Fail closed |
| Any | Present but package, integrity, source, or dist-tag differs | Fail closed |
| Registry-only or ambiguous query state | Present or unknown | Fail closed |

The registry mutation job MUST depend directly on that successful read-only job
in the same serialized workflow run. Using the read capability included in
`packages: write`, it MUST re-read the exact registry version immediately before
the native publish step and fail closed unless the version is still absent. It
does not receive `contents: read` or re-read the tag; the mutation gate relies on
the exact protected immutable tag verified by its predecessor, while the
registry re-read closes the inter-job publication window.

After a new publication, the workflow MUST verify private visibility or the
declared registry visibility, releasing-repository association, exact registry
version and integrity, expected dist-tag, unchanged unrelated aliases, clean
exact-version installation and representative execution, package-only effects,
and terminal evidence. Verification failure preserves the created exact pair
and follows verification or correction; it does not authorize another
same-version mutation.

The completion workflow MUST use these exact job-scoped permission sets:

| Completion responsibility | Exact permission set |
| --- | --- |
| Admission and live verification | `contents: read`, `actions: read`, `pull-requests: read`, `packages: read` |
| Retained-artifact retrieval | `actions: read` |
| Registry mutation | `packages: write` |
| Post-publication verification | `contents: read`, `packages: read` |

The registry mutation job exposes its credential only to the native publish
step. It receives no `contents` or `actions` permission and never performs
source checkout, Actions inspection, or retained-artifact retrieval. The
tag-mutation GitHub App credential or equivalent tag-write authority MUST NOT be
minted, forwarded, referenced, or made available anywhere in the completion
workflow.

### Pre-mutation failure of tag-only completion

A completion authorization is consumed when its first workflow run/attempt `1`
terminates during admission/live verification before retained-artifact retrieval
and before registry mutation. The workflow MUST NOT rerun or reuse that record.
When the original tag-only state and retained artifact remain exact, a selecting
repository MAY request a new attempt only through a protected pull request that
adds one immutable
[`package-release-tag-only-completion-recovery-intent/v1`](./schemas/package-release-tag-only-completion-recovery-intent-v1.schema.json)
record and no other path.

The recovery record binds:

- release unit, channel, version, derived tag, and expected dist-tag;
- the unchanged original release-intent path;
- the original failed publication source/run/attempt, its exact release or
  pre-mutation-recovery authorization, and the retained-artifact chain;
- the immutable original completion-intent path and SHA-256 of its exact bytes;
- the failed completion source, exact Actions run URL, attempt `1`, terminal
  failure, and failure phase `admission-live-verification`;
- not-started retained-artifact retrieval, registry mutation, and
  post-publication verification;
- the unchanged tag-present and registry-version-absent state;
- the current protected `dev` ref and full base commit; and
- reason `pre-mutation-tag-only-completion-failure`.

The first recovery record names the original completion record as its immediate
authorization. A later record names only the latest completion-recovery record
whose exact addition commit started the newly failed run. All records and the
original completion remain byte-identical and addition-only on protected
first-parent history. A reused predecessor, duplicate failed run, stale base,
branching successor, multiple-record diff, unrelated change, or sibling effect
fails static admission.

Only the first workflow run selected by the newly merged recovery record, and
only run attempt `1`, may regain registry-only mutation authority after all live
state and provenance are revalidated. Every rerun and second workflow run from
the original completion or any prior recovery record remains mutation-disabled
before credential setup. An exact tag plus absent registry version may be
publish-eligible; an already exact pair is verification-only; every missing,
moved, registry-only, conflicting, expired, mismatched, or ambiguous state fails
closed.

Before the implementation/foundation PR can make any completion-recovery record
mergeable, its required validation workflow MUST execute a zero-mutation live
permission preflight with exactly `contents: read`, `actions: read`,
`pull-requests: read`, and `packages: read`. It invokes every endpoint used by
live admission and fails on HTTP 403 or ambiguity:

| Live admission query | Required permission |
| --- | --- |
| Actions run metadata | `actions: read` |
| Actions job metadata | `actions: read` |
| Actions artifact metadata | `actions: read` |
| Completion workflow-run history | `actions: read` |
| Commit-associated pull requests | `pull-requests: read` |
| Git tag/ref | `contents: read` |
| Authenticated registry version and dist-tag | `packages: read` |

The preflight receives no `packages: write` permission, registry write
credential, or tag App credential. It creates no package, tag, branch, source,
artifact, deployment, OCI object, object-storage object, or sibling release-unit
effect. A static workflow or profile assertion is not preflight evidence.

The recovery workflow uses the same four exact job permission sets as corrected
completion. It never receives `contents: write`, tag authority, manual-dispatch
authority, or broader production effects. Manual npm publication, rebuild,
repack, tag deletion/movement/recreation, successor-version escape, ruleset
relaxation, and destructive rollback remain forbidden.

The dependency-free reference checker
[`check-protected-package-tag-admission.py`](../../../scripts/docs/check-protected-package-tag-admission.py)
implements the local Git, JSON, and TOML rules for normal, pre-mutation recovery,
tag-only completion, and tag-only completion-recovery admission.
It does not publish, inspect Actions outcome or authorization-use history,
inspect rulesets or pull-request approvals, query a registry, or replace
repository-owned workflow checks. This is intentional: the hosting layer owns
the PR-only merge boundary, while the publication workflow passes the protected
update's exact `before` and `after` commits to the checker and revalidates every
remaining publication prerequisite. Repositories own a pinned invocation or an
equivalent tested implementation.

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
| Tag-only admission and live verification | `contents: read`, `actions: read`, `pull-requests: read`, `packages: read` |
| Tag-only retained-artifact retrieval | `actions: read` |
| Tag-only registry mutation | `packages: write`; no tag credential |
| Tag-only post-publication verification | `contents: read`, `packages: read` |

`packages: write` MUST be absent from validation and consumer jobs. The
write-capable token or credential MUST be exposed only to the native publication
step in its publication job. A consumer job MAY also receive `contents: read`
only when checkout is required. Secrets MUST NOT be written to manifests,
lockfiles, logs, evidence artifacts, or packed package contents.

Private-registry credentials in post-publication verification MUST be scoped to
the installation step. Representative package execution MUST run after registry
credentials and token environment variables are removed.

For normal package publication outside tag-only completion, GitHub Actions
permissions are job-scoped, so publication MUST use a dedicated job with
`packages: write` and only trusted setup, mutation, and verification steps. A
separately minted registry credential is passed only to the native publish step.
Tag-only completion instead follows the exact four-job partition above; its
post-publication verification never runs in the write-capable mutation job. A
hosting-specific tag credential follows the narrower tag rule above; it is not
a general source-write permission.

## Serialization, immutability, and recovery

Publication MUST serialize on release-unit and version identity. Concurrency
cancellation MUST be disabled before the first irreversible tag or registry
mutation.

Before mutation, the workflow MUST read the tag and registry. On the first
attempt authorized by a new release intent, if neither exists it may create and
publish. If that attempt terminates before either immutable identity exists, an
ordinary rerun MUST NOT mutate; a new recovery authorization is required. On an
attempt authorized by a new recovery record, the workflow again requires both
identities to be absent and must prove that record has not started a prior
attempt.

If both identities already identify the same source, version, package, and
integrity, a retry performs idempotent verification and records that outcome; it
does not enter pre-mutation recovery. If either identity is partial or
conflicting, the normal or pre-mutation recovery workflow fails closed and
records the completed phase and owner action. The sole same-version partial
completion is the separately admitted tag-only retained-artifact path above.
Registry-only or conflicting state remains ineligible. A successful immutable
publication followed by evidence or consumer verification failure likewise
keeps the exact pair and uses verification or a new correction version rather
than same-version publication recovery.

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

The original time-bounded exact-ref observation and central executable
regression remain in the
[2026-08-12 validation record](./validation/2026-08-12-protected-package-tag-profile.md).
The authorization-semantics correction is recorded separately in the
[2026-08-13 validation record](./validation/2026-08-13-protected-package-tag-authorization.md).
The pre-mutation recovery correction and incident boundary are recorded in the
[2026-08-14 validation record](./validation/2026-08-14-protected-package-tag-pre-mutation-recovery.md).
The retained-artifact tag-only completion refinement is recorded in the
[2026-08-14 tag-only completion validation record](./validation/2026-08-14-protected-package-tag-only-completion.md).
The admission permission correction and consumed-completion recovery are
recorded in the
[2026-08-15 completion-recovery validation record](./validation/2026-08-15-protected-package-tag-completion-recovery.md).

## Out of scope

This profile does not create a central release queue, repository current-version
registry, package-name registry, tag-pattern registry, publication workflow, or
cross-repository approval gate. It does not publish a package, deploy a service,
clean object storage, mutate durable state, or define a repository's initial
package name or version.
