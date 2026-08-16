# ADR-0023: Adopt protected package-tag publication profile

- Status: Superseded
- Superseded by: ADR-0027
- Date: 2026-08-12
- Last amended: 2026-08-14
- Owners: `5010-dev/.github` maintainers and selecting repository maintainers

## Context

The organization default publishes governed software from validated `main`.
That remains the right boundary for repositories whose release units move
together and for services or applications whose `main` promotion is the
production effect.

A mixed monorepo can instead contain a reusable registry package and a service
or application with independent consumers, compatibility surfaces, cadence,
correction, and production effects. Requiring repository-wide `main` promotion
to publish that package can unintentionally couple package delivery to sibling
service deployment. Publishing every `dev` commit, accepting arbitrary workflow
inputs, or introducing a central release queue would replace that coupling with
ambiguous or centralized authority.

A PR-mediated release-preparation change needs a deterministic admission
boundary. JSON Schema can validate intent shape but cannot prove the exact Git
diff, manifest version-only change, source base, or sibling mutation exclusion.
A small repository-state checker is therefore useful without becoming a
publication workflow or current-version service.

The original wording also used `reviewed` for both PR visibility and a distinct
person's approval. That ambiguity caused a selecting repository without a
qualified independent reviewer to materialize a mandatory second-person gate.
An uninformed or rubber-stamp approval adds latency without improving assurance;
the central contract needs explicit maintainer merge authorization, not a
generic two-person convention.

The first Core prerelease attempt then exposed a separate recovery ambiguity.
Its protected release intent was admitted, but the workflow failed while
constructing the artifact and before it created a package tag or registry
version. The historical intent was already merged and append-only, while a
normal Actions rerun would execute the historical event source rather than a
new reviewed source containing the fix. Requiring a successor prerelease would
mistake an unpublished attempt for an immutable release; reusing the intent or
rerunning it would omit a new PR-mediated authorization boundary.

## Decision

1. Preserve validated `main` as the default publication profile.
2. Allow only a monorepo with an independently released registry package and an
   independently released service or application to select the
   [protected package-tag profile](../standards/release-versioning/protected-package-tag.md).
3. Treat the immutable package-specific protected tag as authority only for the
   declared package version. `dev` remains a non-deployed integration branch,
   and `main` remains production authority for sibling services and applications.
4. Require a repository-local profile contract and one newly added immutable
   release intent. Derive release unit, channel, exact version, source, and tag
   from the protected `dev` update produced by an explicit pull-request merge
   rather than arbitrary workflow inputs.
5. Require release-intent changes to reach `dev` only through a protected pull
   request after repository-required checks pass. The authorized maintainer's
   explicit merge is sufficient release authorization; the author and merger
   may be the same identity. Zero required approving reviews and no last-push
   approval are conformant when pull requests remain mandatory and direct-push
   bypass is absent.
6. Define minimum publication authority as the combination of explicit PR
   merge, exact merge-diff admission, repository-required checks, a protected
   package tag, and isolated publication credentials. A structurally valid
   intent alone is not publication permission.
7. Keep independent or two-person approval as an optional repository-owned
   strengthening control for qualified reviewer capacity, concrete risk, or a
   regulatory, audit, or contractual requirement. Do not mandate a distinct
   reviewer as a generic supply-chain convention.
8. Bind contract package identity and version to one JSON or TOML native
   manifest. Require each admitted version to have greater SemVer precedence
   than its materialized predecessor. Admit only one exact intent and one
   version-field change in the merge diff. Use segment-aware path patterns and
   reject stale, modified, renamed, duplicate, conflicting, or mismatched intent,
   destructive or non-regular release-preparation entries, and every declared
   sibling release-unit mutation.
9. Use the same package identity for prerelease and final publication. A
   prerelease uses native SemVer and a non-`latest` channel; a final release uses
   a new final SemVer and `latest`. Consumers pin exact versions.
10. Create the immutable tag and publish in one serialized protected state
   machine. Retries verify identical remote state; conflicts fail closed and
   published tags or versions are never overwritten or reused.
11. Split minimum permissions by responsibility: validation uses
   `contents: read`, private-package consumption uses `packages: read`, and only
   the package publication job receives `packages: write`. Hosting-specific tag
   mutation authority remains narrowly scoped and cannot push branches.
12. Keep exact package name, initial and current version, registry access, tag
   pattern, workflows, credentials, recovery, history, and package/service
   release-unit inventory repository-owned.
13. Provide versioned schemas and a Python-standard-library exact-diff reference
    checker in the governance repository. The checker supports JSON Pointer and
    TOML dotted-key native manifest selectors, reads source-controlled local
    inputs and Git objects only, and does not publish, query registries, inspect
    hosting approvals, or run consumer CI.
14. Do not create a central release queue, repository current-version registry,
    package-name registry, shared publication workflow, or cross-repository
    approval gate.
15. Add a distinct append-only `package-release-recovery-intent/v1` for the
    narrow case where an admitted attempt reached terminal failure before tag or
    registry mutation and both immutable identities remain absent. Preserve the
    original release intent byte-for-byte and permit the same exact version only
    through a new protected pull-request merge.
16. Bind the recovery record to the original intent, failed source and Actions
    run, exact current base and ref, release unit, version, channel, and the
    pre-mutation/no-identity reason. Admit only the one newly added record; the
    admitted `after` becomes the new publication source. One record may start at
    most one attempt, and another pre-mutation failure requires another record.
17. Keep live ruleset, required-check, Actions-run, tag, registry, authorization-
    use, and integrity validation repository-owned. Reject recovery when either
    immutable identity exists, including tag-only, registry-only, conflicting,
    or successfully published then verification-failed state. Do not authorize
    reruns, manual dispatch, tag/package mutation, ruleset relaxation, or an
    automatic successor version through this path.

## Consequences

- Existing repositories do not change unless they materialize and enforce the
  opt-in contract.
- The Design System retains its Changesets preparation on `dev`, fast-forward
  promotion, and `main` publication workflow.
- A selecting repository can publish its package without deploying a sibling
  service, while every untagged `dev` commit remains unreleased.
- A selecting repository must enforce the PR-only merge boundary but need not
  manufacture a second approver. It may opt into qualified independent approval
  when its operating model or concrete obligations support that control.
- Release preparation becomes intentionally narrow: version, changelog, one
  intent, and repository-declared supporting paths.
- Pre-mutation recovery is also narrow: a separate PR adds one immutable
  recovery record and changes no manifest, historical intent, workflow,
  changelog, or sibling path. An unpublished version may be preserved without
  converting a failed attempt into a release.
- The checker has a bounded responsibility and dependency surface. A repository
  still owns PR-only merge protection, optional independent-approval policy,
  rulesets, Actions outcome and attempt-use validation, package closure,
  registry uniqueness, publication, evidence, and recovery.
- Schema or checker incompatibility is corrected in place until a real released
  consumer exists; after that boundary, consumers coordinate or select a new
  compatibility major.

## Alternatives considered

### Require `main` for every package in every monorepo

Rejected because it couples an independent package release to unrelated service
or application production effects.

### Publish every `dev` commit or use manual version inputs

Rejected because a mutable branch or arbitrary input is not explicit PR-merged
immutable release intent and cannot establish exact package identity.

### Require an independent second-person approval everywhere

Rejected because repositories without a qualified reviewer or real two-person
operating model would add a rubber-stamp delay rather than assurance. A
repository may still require independent approval when concrete risk or
compliance evidence justifies it.

### Build a central release queue or current-version registry

Rejected because repository-native manifests, tags, registries, workflows, and
release history already own those facts. A central copy would drift and become a
second publication authority.

### Use JSON Schema without an exact-diff checker

Rejected because structural validation cannot establish source ancestry, a
single newly added intent, a version-only manifest change, or sibling isolation.

### Rerun the failed release intent or always advance the version

Rejected because a normal rerun is not a new protected merge and may execute the
historical workflow source, while a forced successor version would treat a
pre-mutation failure with no immutable identity as though it had published. A
separate recovery record preserves both the original intent and explicit
authorization without weakening immutable-state handling.

Boundary classification: unreleased — corrected in place. This decision adds a
new opt-in profile before its first package publication; it does not rewrite an
existing package, tag, Design System release, service deployment, or durable
state.
