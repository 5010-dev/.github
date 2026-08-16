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
2. Verify validated `main` for a governed publication, an exact package-relevant
   `dev` merge for a protected-package prerelease, or the exact immutable source
   boundary selected by the owning research contract for internal record
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

For the protected package-tag profile, a required-check-passing package-relevant
merge to `dev` authorizes a unique prerelease, while fast-forward promotion to
`main` authorizes the corresponding final only after package-closure and
runtime-payload equivalence to an eligible prerelease is established. A
package-neutral `dev` merge or a `main` promotion whose package closure is
unchanged from the previous final, when one exists, MUST NOT publish a package.
One repository-owned engine MUST derive release unit, branch channel, Stable
target, prerelease sequence, exact version, source, changelog or release notes,
closure, and protected tag from repository state. It MUST NOT accept arbitrary
publication inputs, create version or changelog commits, push a branch, invoke a
sibling deployment, or cancel an older run after irreversible mutation begins.
The hosting layer owns the protected `dev` merge and fast-forward `main`
promotion boundaries; an independent GitHub approval is not an organization
minimum.

The engine MUST materialize the resolved version only in the package staging
output or through an equivalent repository-owned native strategy. A distinct
package-relevant `dev` merge receives a distinct prerelease. A retry of the same
authorized merge reuses its exact version. Final publication uses the
repository-owned Stable target and MUST NOT occur from `dev`.

Before any final-package mutation, the engine MUST verify equal package-closure
and runtime-payload identities and a package-neutral diff between the separately
recorded prerelease and final sources.

The workflow MUST serialize publication, build deterministically from the exact
source, and read tag and registry state before mutation. If both identities are
absent, it may create the protected tag and publish. If the exact tag already
selects that source while the registry version is absent, it may keep the tag
unchanged and resume registry publication from the same immutable source. If
the exact tag, version, source, integrity, and channel already agree, it MUST
return verification success without republishing. Registry-only, missing or
moved expected tag, conflicting source/version/integrity, and ambiguous state
fail closed.

The registry state MUST be re-read immediately before and after publication.
The workflow then verifies the native integrity and channel, clean exact-version
installation and representative execution, credential removal, and absence of
sibling effects. A workflow rerun is not new authorization, but it MAY
idempotently complete or verify only the exact source and version authorized by
the branch merge or promotion. It does not require a parallel publication
control plane.

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
- A protected package run that stopped while both tag and registry version were
  absent MAY be rerun idempotently for the same merged source and version.
- A protected package run that created the exact immutable tag but stopped
  before registry publication MAY keep that tag unchanged and resume the absent
  registry publication from the same immutable source.
- An exact tag/version/source/integrity pair is verification success. A rerun
  MUST NOT republish it or expose an unnecessary mutation credential.
- After a package version, tag, image digest, accepted native build, immutable
  release, or immutable research record is published or finalized, recovery
  MUST NOT overwrite it. Use the applicable correction, successor, deprecate,
  yank, retract, supersession, or withdrawal operation.
- A partial result MUST retain source, intended version or research-record
  identifier, completed publication or finalization identities, failed phase,
  owner action, and retry, correction, or successor path.
- A retry MUST re-read remote state and fail when it would create a conflicting
  identity or claim success for a different artifact.
- Registry-only, conflicting immutable state, and a successful exact publication
  followed by verification failure retain the existing identities and use
  fail-closed verification, a new SemVer correction, or owner action without
  deletion, movement, overwrite, or reuse.

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
- A protected package-tag workflow scopes tag mutation authority to the declared
  tag namespace without branch-push authority. Registry write authority is
  exposed only to the native publish step. Private-registry read credentials
  are exposed only to the install step and removed before representative
  execution.
- The workflow reads protected tag and registry state before publication,
  re-reads the registry immediately before and after publish, and keeps
  validation and consumer execution free of write credentials.
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
