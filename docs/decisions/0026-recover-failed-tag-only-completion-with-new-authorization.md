# ADR-0026: Recover failed tag-only completion with a new authorization

- Status: Accepted
- Date: 2026-08-15
- Owners: `5010-dev/.github` maintainers and selecting repository maintainers
- Refines: ADR-0025 decisions 2, 6, 9, and 12

## Context

Core completion authorization PR `5010-dev/fiftyten-indicators-core#65` added
one immutable `package-release-tag-only-completion-intent/v1` record and merged
as `e2e679715ec19e8ac6ba9a45b08ea9a467d607c5`. Its first workflow run
`31877967715`, attempt `1`, failed during admission/live verification. The job
called `GET /repos/5010-dev/fiftyten-indicators-core/commits/e2e6797.../pulls`
with Contents read, Actions read, and Packages read. GitHub requires Pull
requests read for that endpoint, so the installation token received HTTP 403.

The failure occurred before retained-artifact retrieval and before registry
mutation. The immutable tag still identifies
`099edf52740633a200c9d57abf8c7a4310fe1507`, the registry package remains absent,
and retained artifact `9202971363` remains unexpired and unchanged. The original
completion record and its first run are consumed authority. A rerun or second
run from that record cannot safely regain mutation authority.

Static permission assertions did not prove that the token could call every
endpoint used by live admission. A new completion authorization with the same
defect would repeat the failure without improving assurance.

## Decision

1. Correct completion admission/live verification to the exact permission set
   Contents read, Actions read, Pull requests read, and Packages read. Preserve
   Actions read only for artifact retrieval, Packages write only for registry
   mutation, and Contents read plus Packages read for post-publication
   verification.
2. Add the distinct
   `package-release-tag-only-completion-recovery-intent/v1` contract and a
   fourth non-overlapping authorization directory. Do not edit, reuse, rename,
   or delete the original completion record.
3. Bind every recovery record to release unit, channel, version, tag, dist-tag,
   original release intent, the original publication source/run, retained
   artifact identities, the immutable original completion path and SHA-256,
   the exact failed completion source/run/attempt/phase, not-started retrieval,
   not-started registry mutation, not-started post-publication verification,
   unchanged tag-present/registry-version-absent state, and current protected
   base/ref.
4. The first recovery names the original completion authorization. If that new
   run also fails before retrieval and mutation, a later record must name the
   latest recovery authorization. Protected first-parent history must form one
   append-only chain. Duplicate, reused, branched, stale, or multi-file
   authorization is rejected.
5. Only the first run/attempt `1` selected by the newly merged record may regain
   registry-only mutation authority after live state and provenance are
   revalidated. Every rerun, second run, and old-record run remains
   mutation-disabled before credential setup.
6. Before any recovery authorization PR merges, the selecting repository's
   implementation/foundation PR must execute a zero-mutation live permission
   preflight with the exact four-read admission set. It calls every Actions run,
   job, artifact and completion-history endpoint, the commit-associated pull
   requests endpoint, Git tag/ref endpoint, and authenticated package
   version/dist-tag reads used by admission. HTTP 403 or ambiguous response
   fails the required PR check.
7. The preflight receives neither Packages write nor the tag App credential and
   creates no artifact, package, tag, branch, source, deployment, OCI object, or
   sibling release-unit effect.
8. An exact tag plus absent registry version is publish-eligible only for the
   new record's first run/attempt `1`. An already exact pair is verification-only.
   Missing, moved, conflicting, registry-only, ambiguous, expired, or mismatched
   state fails closed.
9. Manual dispatch, Actions rerun, manual npm publication, rebuild, repack, tag
   mutation, successor version escape, ruleset relaxation, destructive rollback,
   and broader deployment effects remain forbidden.

## Consequences

- The real permission defect is repaired without broadening mutation jobs.
- A consumed completion authorization can be followed by one reviewed successor
  without treating the old record or run as renewable authority.
- Each additional pre-mutation completion failure costs another protected PR
  and immutable record, keeping the recovery path bounded and auditable.
- The repository must prove live permission access before asking a maintainer to
  merge a mutation-capable recovery authorization.
- Linear evidence remains coordination context. It is never package publication
  authority.

## Alternatives considered

### Rerun or reuse the original completion record

Rejected because run attempt `1` consumed the record's sole mutation authority.

### Add only Pull requests read

Rejected because the incident also demonstrated that static permission lists do
not prove executable access to every live-admission endpoint.

### Publish manually or rebuild the same version

Rejected because either path bypasses protected exact-diff authority or changes
the retained byte identity.

### Advance to `0.1.0-next.1`

Rejected as an escape path because the immutable tag and exact retained package
for `0.1.0-next.0` remain valid while the registry identity is still absent.

Boundary classification: released — compatibility required because the
immutable `technical-indicators-v0.1.0-next.0` tag and a consumed completion
authorization already exist while the registry version remains absent.
