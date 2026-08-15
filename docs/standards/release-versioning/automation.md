# Release automation

Release automation and research-record publication or finalization automation
implement the artifact profile and evidence contract. They are not the source of
normative policy and do not transfer publication or finalization ownership away
from the owning repository.

## Ownership

| Organization standard or shared implementation | Owning repository |
| --- | --- |
| Artifact-profile outcomes and portable evidence fields | Exact release unit and version or research-record decision |
| Optional schemas, checker contracts, and adapter interfaces | Native manifests, release metadata, and research metadata |
| Selection criteria for reusable automation | Trigger, approval, environment, publication or finalization timing, and owning research authority |
| Immutable implementation release and compatibility information | Credentials, registry and cloud access, and least-privilege permissions |
| Generic failure and evidence semantics | Build or research execution ownership, publish, finalize, deploy, verify, recover, and current history |

Production deployment mutation, rollout, rollback, runtime readiness, and
operational verification remain owned by applicable
[platform delivery standards](../../platform/README.md) and repository
workflows. Release automation MUST carry the required release identity into
those workflows but MUST NOT replace their safety contract.

## Required publication sequence

Automation MUST perform the applicable phases in this order or prove an
equivalent fail-closed order:

1. Resolve the release unit, profile, version or research-record source,
   requested identifier, and applicable channel or record status.
2. Verify validated `main` for a governed publication, the exact admitted source
   commit selected by the protected package-tag profile, or the exact immutable
   source boundary selected by the owning research contract for internal record
   finalization, plus required source or manifest state.
3. Verify applicable version, research identifier, tag or ref, registry, channel,
   and status uniqueness and consistency.
4. Build, test, and package once from the selected source boundary, or select the
   already-produced research artifacts and frozen manifest from the owning
   research workflow.
5. Compute the exact artifact or research-record identity and the checksum, SBOM,
   digest, or provenance evidence required or selected by the applicable profile
   and capability.
6. Create a draft or staging record where the distribution system permits it.
7. Publish or finalize the immutable artifact and release or research record
   without overwriting an existing identity.
8. Verify registry lookup, pull, install, execution, digest, deployment, manifest,
   or terminal-record state according to the profile.
9. Emit durable release evidence and an explicit success, staged, partial, or
   failed state.

Publication or finalization of the same release unit and intended version or
repository-native identifier MUST be serialized. Independent research runs with
distinct preallocated immutable identities MAY execute concurrently. A workflow
MUST NOT use concurrency cancellation that can interrupt an older run after
irreversible publication or finalization begins. Every remote mutation and
verification loop MUST be bounded and report an unambiguous failure when its
result cannot be established.

For the protected package-tag profile, tag creation and registry publication
MUST occur in the same serialized state machine after exact merge-diff admission.
The workflow MUST derive release unit, channel, version, source, and tag from the
PR-merged repository state admitted by the exact `before..after` diff; it MUST
NOT accept them as arbitrary dispatch inputs, create a version or changelog
commit, push a branch, invoke a sibling deployment, or cancel an older run after
tag creation or publication begins. The hosting layer owns the PR-only merge
boundary. The publication workflow revalidates the exact diff and every
publication prerequisite before mutation; it does not infer or validate an
independent human approval.

One normal release intent may start only its first admitted publication
attempt. An Actions rerun, manual dispatch, comment, or repeated evaluation of
the old event is not renewed mutation authority. If that attempt reaches a
terminal failure before any tag or registry version exists, same-version
recovery requires one new PR-merged
`package-release-recovery-intent/v1`. The recovery workflow derives all
identities from the unchanged manifest, historical intent, recovery record, and
new exact `before..after` diff; the recovery `after` is the new source.

Before a recovery mutation, repository automation MUST query the prior Actions
run and prove terminal failure before immutable mutation, query the exact tag
and registry version and prove both absent, prove the recovery record has not
started another attempt, and revalidate the protected source branch, required
checks, protected tag authority, package closure, credentials, and sibling
isolation. Record fields declaring absent identities are reviewed authorization
claims, not replacements for live state. The central reference checker validates
only record structure and local Git history and MUST NOT query Actions,
rulesets, or registries.

Tag-only completion uses a different state machine and a different immutable
record conforming to `package-release-tag-only-completion-intent/v1`. Before any
registry mutation, repository automation MUST verify the exact existing tag and
its source; the failed run's selecting-repository identity, protected `dev` push
event/ref, exact source, attempt 1, terminal failure, and declared normal
publication or recovery workflow selected by its authorization type; the
run's trusted job or terminal evidence that the exact tag-creation phase
completed and registry publication failed before creating the version; the
original admitted release or recovery authorization; the unexpired retained
artifact ID and run, archive digest, tarball SHA-256, native integrity, embedded
source, unchanged manifest/version, expected dist-tag, authorization-use
history, rulesets, and current registry state. It MUST download the retained
artifact and MUST NOT rebuild or substitute bytes.

Only the first workflow run created by that newly merged completion record, and
only its run attempt 1, may create the absent exact registry version. A rerun or
second workflow run MUST be mutation-disabled before the publication credential
is exposed. If the exact version already exists and tag, source, integrity, and
dist-tag all match, every run is verification-only. Any mismatch, registry-only
state, unavailable or expired artifact, ambiguous query, or consumed
authorization fails closed without mutation.

If that first completion run/attempt `1` fails during admission/live
verification before retained-artifact retrieval and registry mutation, the
completion record is consumed. Another same-version attempt requires one new
PR-merged `package-release-tag-only-completion-recovery-intent/v1` record whose
exact diff changes no other path. The first record names the immutable original
completion path and bytes; every later record names the latest recovery source
and failed run. Rerun, second-run mutation, predecessor reuse, and branched
successors remain forbidden.

Before any completion-recovery authorization PR can merge, the repository's
implementation/foundation PR MUST run a zero-mutation live preflight with the
same read-only admission permissions. It must successfully call the Actions run,
job, artifact and completion-history endpoints, commit-associated pull requests,
Git tag/ref, and authenticated registry version/dist-tag queries used by live
admission. HTTP 403 or ambiguous responses fail the required check. The
preflight receives no package write or tag App credential and creates no
artifact or release/deployment effect.

## Native client distribution

Native client automation MUST treat signed build production, store submission,
store review, approval, phased release, and full availability as distinct states.
It MUST NOT report a build as publicly released solely because upload or review
submission succeeded. A retry MUST re-read platform state and MUST NOT reuse a
version and build identity for different content.

Store review and rollout are asynchronous external operations, so an automation
run MAY terminate in an explicit staged or pending state with durable evidence
and an owner action. Product-facing release notes MAY be generated as a draft,
but externally published customer text requires the human approval defined by
[Release records and evidence](./release-evidence.md).

## Research artifact publication

Research artifact publication automation MUST verify the exact source,
applicable manifest schema, artifact identities and digests, lineage, and owning
record status required by the selected profile before publishing or finalizing a
record whose status was established by the owning research workflow. It MUST
fail closed when a required input, output, digest, predecessor, amendment, retry,
or citation relationship is missing or ambiguous.

Automation MAY validate structure, integrity, completeness, and declared
relationships. It MUST NOT infer or publish scientific validity, interpretation,
or approval, execute the scientific protocol merely to satisfy this publication
sequence, or establish a terminal research status without the owning research
authority's recorded decision. The research workflow MAY invoke publication
automation in the same execution, but it retains scientific execution and status
authority. A retry, correction, or rerun MUST create or select an append-only
successor identity rather than mutate a terminal record.

## Partial publication or finalization and recovery

Release publication and research-record finalization are not generally
transactional. Automation MUST identify which steps are reversible and which
registry, archive, or record operations are permanent.

- Before immutable publication or finalization, a draft MAY be completed,
  replaced, or removed under the owning system's documented recovery semantics.
- A protected package attempt that failed terminally before creating either its
  tag or registry version MAY preserve the same version only through a new,
  unused, PR-mediated pre-mutation recovery record. The original intent and all
  previous recovery records remain immutable. A second such failure requires a
  second record bound to the newly failed run.
- A protected package attempt-1 run that created the exact immutable tag and
  then failed before registry publication MAY complete only the absent registry
  version through one unused PR-mediated tag-only completion record and the
  original run's retained artifact. It never rebuilds or mutates the tag.
- A tag-only completion run that failed before retained-artifact retrieval and
  registry mutation MAY start another attempt only from a new append-only,
  PR-mediated completion-recovery record. The original completion is consumed;
  each later pre-mutation failure requires another direct successor record.
- After a package version, tag, image digest, accepted native build, immutable
  release, or immutable research record is published or finalized, recovery
  MUST NOT overwrite it. Use the applicable correction, successor, deprecate,
  yank, retract, supersession, or withdrawal operation.
- A partial result MUST retain source, intended version or research-record
  identifier, completed publication or finalization identities, failed phase,
  owner action, and retry, correction, or successor path.
- A retry MUST re-read remote state and fail when it would create a conflicting
  identity or claim success for a different artifact.
- Tag-only state is not pre-mutation recovery and is eligible only for the
  narrower retained-artifact completion above. Registry-only, conflicting
  immutable state, and a successful exact publication followed by verification
  failure retain the existing identities and use fail-closed verification,
  correction, or owner action without deletion, movement, overwrite, or reuse.

## Shared automation admission

The organization MUST NOT mandate one universal release workflow or tool.

A reusable workflow or shared release adapter MAY become an organization shared
implementation only when all of the following are true:

1. at least two stable implementations of the same artifact profile demonstrate
   the same outcome and recovery semantics;
2. the common interface has a small, typed input and named-secret surface;
3. the caller retains version or research-record identifier, trigger,
   credentials, publication or finalization, and recovery decisions;
4. non-trivial logic has a deterministic local or shared-core test path; and
5. the implementation has an immutable version or commit pin, compatibility
   record, upgrade path, and rollback path.

A caller MUST pin a reusable workflow or action to an immutable full commit SHA
or an organization-approved immutable release locator. A moving branch or tag
MUST NOT be the execution identity for publication-capable shared automation.

The owning repository MUST own an intentionally thin caller. Thin describes
the responsibility boundary, not a line-count target: GitHub Actions owns event,
permissions, credential setup, concurrency, invocation, and summaries, while
deterministic release logic remains locally or independently executable.

## Permissions and credentials

- Caller permissions MUST be explicit and least privilege.
- A protected package-tag workflow additionally follows its profile-specific
  split: validation uses `contents: read`, private-package consumption uses
  `packages: read`, and `packages: write` exists only in the package publication
  job. Validation and consumer jobs MUST NOT receive package write access.
- A tag-only completion workflow uses four exact job permission sets: admission
  and live verification receive `contents: read`, `actions: read`,
  `pull-requests: read`, and `packages: read`; retained-artifact retrieval receives only `actions: read`;
  registry mutation receives only `packages: write`; and post-publication
  verification receives `contents: read` and `packages: read`. The registry
  credential is exposed only to the exact native publish step. Admission and
  live verification read tag and registry together before releasing the
  mutation job; that job re-reads only the registry immediately before publish.
  The tag-mutation App credential or equivalent tag authority MUST NOT be
  minted, forwarded, or referenced anywhere in the completion workflow.
- The completion permission preflight uses only that same four-read admission
  set and executes in the repository validation workflow. Its endpoint inventory
  maps Actions run/job/artifact/history to `actions: read`, commit-associated
  pull requests to `pull-requests: read`, Git tag/ref to `contents: read`, and
  authenticated registry version/dist-tag queries to `packages: read`. Any write
  permission, tag App credential, or mutation effect is non-conformant.
- Secrets MUST be forwarded by name. `secrets: inherit` MUST NOT be the default.
- OIDC or repository-scoped `GITHUB_TOKEN` SHOULD replace long-lived publication
  credentials when the registry or cloud supports it.
- Public npm publication SHOULD use npm trusted publishing and registry
  provenance when the release topology is supported.
- GitHub Packages publication SHOULD use the releasing repository's
  `GITHUB_TOKEN`; consumer repositories retain explicit package read access.
- A called workflow MUST NOT assume it can elevate permissions the caller did
  not grant.
- Private shared workflow access and any hosting-plan configuration are
  operational adapters, not normative authority.
- Third-party actions used in a publication workflow MUST be pinned to a full
  commit SHA and reviewed for required permissions and output handling.

## Tool selection

Ecosystem-native build and publish commands remain the final publication
authority. Repositories MAY select tools that satisfy this contract; the tool
does not replace native registry state or release evidence.

- Changesets is the default candidate for Node.js multi-package repositories
  that need per-package release intent, internal dependency coordination,
  version updates, and changelogs.
- Release Please is the default candidate for Conventional Commit-based release
  pull requests, version updates, changelogs, tags, and GitHub Releases across
  supported ecosystems. Registry publication remains a separate native step.
- A CLI or binary release MAY use GoReleaser, cargo-dist, or a repository-local
  implementation that meets the applicable profile.
- New automation MUST NOT adopt a deprecated or unmaintained release tool.

These are recommended adapters, not required organization products. A
repository MAY use another maintained tool or a small native implementation
when it produces the same evidence, immutability, failure, and recovery outcomes.

## Relevant upstream guidance

- [GitHub reusable workflow reference](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
- [GitHub secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub OIDC with reusable workflows](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows)
- [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/)
- [GitHub Packages with GitHub Actions](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions)
- [Changesets](https://github.com/changesets/changesets)
- [Release Please](https://github.com/googleapis/release-please)
- [Apple bundle version](https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleversion)
- [Android app versioning](https://developer.android.com/studio/publish/versioning)
- [FAIR Principles for Research Software](https://doi.org/10.15497/RDA00068)
- [FORCE11 Software Citation Principles](https://force11.org/info/software-citation-principles-published-2016/)
