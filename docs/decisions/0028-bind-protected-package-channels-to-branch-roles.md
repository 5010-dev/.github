# ADR-0028: Bind protected package prerelease and final channels to branch roles

- Status: Accepted
- Date: 2026-08-17
- Owners: `5010-dev/.github` maintainers and selecting repository maintainers
- Supersedes: ADR-0027

## Context

The protected package-tag profile correctly separates an independently consumed
registry package from a sibling service or application in the same monorepo. It
also correctly requires immutable versions and tags, a deterministic package
closure, least-privilege credentials, sibling isolation, and one idempotent
repository-owned publication engine.

Standard `2026.08.8`, however, allowed a selecting repository to publish both a
prerelease and a final package from `dev` through separate release pull requests.
That model detached Stable publication from the organization production branch,
treated service-only source movement as a reason to couple package publication
to release ceremony, and encouraged consumers to replace a prerelease source pin
with a final source pin before `dev` to `main` promotion.

A mixed monorepo has three materially different change classes: package-only
inputs, sibling service-only inputs, and shared inputs that affect both release
units. The repository can classify these changes through its declared package
build-input closure. Branch role and closure membership are therefore sufficient
to select the package channel without a parallel release-intent control plane or
a second integration cycle for final bytes.

The central standard is a released governance contract, and Core and Platform
already adopted `2026.08.8`. This decision is an explicit coordinated
supersession. It does not preserve a dual policy because the affected
cross-repository `dev` integration is unreleased and can align directly before
production promotion. Existing registry versions and immutable tags remain
released identities and are not changed.

## Decision

1. Retain validated `main` publication as the organization default. For a
   repository selecting the protected package-tag profile, bind package
   prereleases to `dev` and final package versions to `main`.
2. Require the selecting repository to declare one authoritative package
   build-input closure. Package-only and shared-input changes are
   package-relevant. Sibling service-only and documentation-only changes outside
   that closure are package-neutral and do not publish the package.
3. Treat a required-check-passing package-relevant pull request merge to `dev`
   as authorization for one unique SemVer prerelease on the repository-declared
   non-`latest` channel. Pre-merge validation builds and packs without
   publication. No separate version-only, release-intent, or evidence pull
   request is required.
4. Treat fast-forward promotion to `main` as authorization for the exact Stable
   target on `latest` only when the repository proves that an eligible
   prerelease and the promoted source have the same package-closure and runtime
   payload identities. A `dev` workflow cannot publish a final version.
5. Allow prerelease and final source SHAs to differ when the intervening diff is
   package-neutral. Record both sources and require the closure checker to prove
   that no package or shared input changed. If any package-relevant input
   changed, publish and validate a new prerelease before final promotion.
6. Require a repository-owned Stable target and a serialized unique prerelease
   sequence. The publication engine materializes the exact native version only
   in its package staging output. The same authorized retry reuses the same
   version; a distinct package-relevant merge receives a distinct prerelease.
7. Use the same serialized, idempotent publication engine and immutable
   tag/registry state model for both channels. Branch, version form, dist-tag,
   and prerelease-to-final equivalence are channel policy inputs, not separate
   workflow state machines.
8. Keep package publication and every sibling service or application release as
   separate release units, triggers, credentials, mutations, and terminal
   outcomes. A shared-input commit may validate or release both units through
   separate workflows, but neither workflow authorizes the other.
9. Require development integration artifacts to consume an exact prerelease and
   production artifacts to consume an exact final version. A mutable dist-tag
   may discover a candidate, but retries, rebuilds, and redeployments use a
   recorded exact version and native integrity. A native lockfile or immutable
   artifact build-input record may carry that identity; the organization does
   not require per-release consumer source-pin replacement commits.
10. Preserve the existing protected tag namespace, published versions, and
    registry history. Selecting repositories align directly to this model
    without a compatibility workflow, custom intent schema, evidence-only pull
    request, or release-history rewrite.
11. Keep repositories that do not select this profile unchanged. In particular,
    Design System continues its existing Changesets preparation on `dev`,
    fast-forward promotion, and package publication from `main`.

## Consequences

- `dev` remains a non-deployed integration branch while supporting immutable
  prerelease package validation.
- Stable package publication is again aligned with the production branch, but
  it remains independent from a sibling service deployment.
- Package-neutral service commits may appear between prerelease and final source
  SHAs without forcing a new package candidate.
- Final validation compares package closure and runtime payload rather than
  requiring byte-identical tarballs or identical repository SHAs. Version-bound
  generated metadata may differ.
- Consumer builds remain reproducible without adding a prerelease pin commit and
  a final pin commit for each package release.
- Closure declaration, Stable-target storage, prerelease sequence, staging
  injection, exact trigger paths, and current release state remain
  repository-owned implementation details.

## Alternatives considered

### Continue publishing final versions from `dev`

Rejected because it makes Stable package availability precede the organization
production source boundary and requires additional policy to explain when a
development-only final is actually releasable.

### Publish only from `main`

Rejected for selecting repositories because an independently consumed package
needs an immutable prerelease that development consumers can validate before
coordinated production promotion.

### Commit prerelease and final pins into each consumer branch

Rejected as an organization requirement. Exact artifact identity can be carried
by a native lockfile or immutable build-input record and resulting artifact
provenance without two source commits or a duplicate final integration matrix.

### Require identical prerelease and final source SHAs

Rejected because sibling service-only and documentation-only commits are outside
the package release unit. Package-closure and runtime-payload equivalence is the
relevant invariant.

Boundary classification: released governance contract — coordinated
supersession required because Core and Platform consume Standard `2026.08.8`;
no dual-policy compatibility mode is retained for unreleased `dev` integration.
