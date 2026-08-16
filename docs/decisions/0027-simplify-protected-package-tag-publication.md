# ADR-0027: Simplify protected package-tag publication to an idempotent registry-native lifecycle

- Status: Accepted
- Date: 2026-08-16
- Owners: `5010-dev/.github` maintainers and selecting repository maintainers
- Supersedes: ADR-0023, ADR-0025, and ADR-0026

## Context

The protected package-tag opt-in solves a real release-unit boundary: a mixed
monorepo may need to publish an independently consumed registry package without
promoting or deploying its sibling service or application. The protected,
package-specific immutable tag, PR merge boundary, required checks,
least-privilege credentials, deterministic package closure, and sibling
isolation remain necessary.

The policy subsequently accumulated a central machine-readable intent and
multi-stage recovery control plane. Exact merge-diff admission, one-attempt
authorization, four append-only record types, retained-artifact digest chains,
workflow-run ordinals, endpoint permission preflights, and evidence-only
follow-up changes made the governance implementation more complex than the
publication invariant it protected. GitHub pull requests, Actions, immutable
tags, and the native registry already provide the durable authorization and
artifact surfaces needed for that invariant.

The central standard is a released governance contract. Simplifying it is an
intentional supersession, not an unreleased in-place correction. Selecting
repositories must adopt the new contract before their next package publication,
but a dual policy or compatibility mode would preserve the retired complexity
without protecting a released package consumer or durable runtime state.

## Decision

1. Retain validated `main` as the organization publication default and retain
   the protected package-tag profile as a narrow opt-in only for independently
   released registry packages in mixed package/service or package/application
   monorepos.
2. Require a package release pull request to materialize the package version and
   changelog. Repository-required checks followed by an authorized maintainer's
   explicit merge authorize publication of that exact source and version. A
   separate GitHub approval or two-person review is not an organization minimum.
3. Require one repository-owned, serialized, idempotent workflow after merge.
   It derives identity from repository state, validates the deterministic
   package closure and sibling isolation, reads tag and registry state before
   mutation, re-reads registry state immediately before and after publication,
   and performs clean exact-version installation and representative execution.
4. Apply one state model:
   - absent tag and absent exact version: create the protected tag from the
     verified source and publish;
   - exact tag at the verified source and absent exact version: keep the tag
     unchanged and resume registry publication from that same immutable source;
   - exact tag, version, source, integrity, and channel: verification success;
   - registry-only, missing or moved expected tag, conflicting identity, or
     ambiguous state: fail closed and use a new SemVer correction as applicable.
5. Treat a rerun as no new authorization while allowing it to idempotently
   complete or verify only the exact merge-authorized source and version.
   Published tags and versions are never moved, deleted, overwritten, or reused.
6. Preserve least-privilege boundaries. Tag mutation authority is scoped to the
   package tag and cannot push branches; registry write authority exists only in
   the native publish step; private install credentials exist only in the
   install step and are removed before representative execution.
7. Preserve Calculator, OCI/ECS, object-storage, and every sibling release-unit
   isolation. Package publication cannot invoke or mutate those release units.
8. Use GitHub and registry native minimum evidence: source SHA and immutable
   package tag, Actions run, exact registry version and integrity, changelog or
   release notes, clean exact-version execution, and workflow isolation.
   Linear, a separate evidence pull request, or a repository evidence file is
   not publication authority.
9. Treat package visibility, repository association, and consumer grants as
   setup and access configuration. Verify them when access is established or
   changed and during consumer handoff, not as a terminal gate for every
   release.
10. Retire the active central custom intent/recovery schemas, examples, admission
    checker, regression suite, schema validator, pinned validator dependencies,
    and CI installation path. Git history and the existing validation records
    preserve historical evidence; they are not current authority.
11. Require selecting repositories, including Core, to align their
    repository-owned workflow before the next publication. Do not retain a
    compatibility mode, dual workflow, successor schema, replacement checker,
    or central migration control plane.

## Consequences

- The opt-in keeps its immutable package identity, protected PR merge,
  least-privilege credential, deterministic-build, exact-version, and sibling
  isolation guarantees with a materially smaller policy and execution surface.
- A safe tag-only resume no longer requires a distinct record or workflow; the
  same workflow preserves the exact tag and converges the registry from the
  same immutable source.
- Registry-only, moved-tag, version, source, integrity, and ambiguous states
  remain fail closed. Simplification does not permit manual publication or
  mutable release identity.
- Repository and registry native surfaces are sufficient for release evidence.
  Access configuration remains important but does not redefine artifact
  provenance.
- Design System remains on its existing `dev` Changesets preparation,
  `dev`-to-`main` promotion, and `main` publication lifecycle because it
  does not select this opt-in profile.

## Alternatives considered

### Keep the custom control plane and simplify its schemas

Rejected because a successor schema, checker, or recovery record would preserve
the duplicate control plane and its operating cost.

### Allow manual completion when only the tag exists

Rejected because manual publication bypasses the repository-owned workflow,
credential boundary, state rechecks, native evidence, and sibling isolation.

### Delete or move a conflicting tag or overwrite a version

Rejected because released tags and registry versions are immutable identities.
A new SemVer correction is the smallest safe response.

### Require a distinct approver for every package release

Rejected as an organization minimum because required checks plus an authorized
maintainer's explicit merge provide the publication boundary. Repositories may
adopt stronger review when concrete evidence or obligations require it.

Boundary classification: released governance contract — intentionally
superseded; selecting repositories must migrate before their next publication.
No compatibility mode or dual policy is retained.
