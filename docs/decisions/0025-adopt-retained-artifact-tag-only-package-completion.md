# ADR-0025: Adopt retained-artifact tag-only package completion

- Status: Accepted
- Date: 2026-08-14
- Owners: `5010-dev/.github` maintainers and selecting repository maintainers
- Refines: ADR-0023 decisions 10, 15, 16, and 17 for exact tag-only partial publication

## Context

ADR-0023 separated a pre-mutation failure with no immutable identity from a
published or partial package state. It correctly prohibited rerunning a merged
intent and required a new PR-mediated record before another same-version attempt
when both tag and registry version were absent.

The first protected prerelease of `@5010-dev/technical-indicators` exposed the
next state. The admitted attempt-1 run built and retained the exact package,
created the protected immutable tag, and then failed before registry mutation
because a relative tarball path was interpreted as a Git dependency. The tag
points to the admitted source, the registry version remains absent, and the
retained artifact has independently recorded archive, tarball, npm-integrity,
and embedded-source identities.

Forcing a successor version would preserve immutability but abandon an exact
artifact whose package publication never occurred. Rerunning the failed
workflow, manually publishing, rebuilding, deleting or moving the tag, or
loosening rulesets would reuse historical authority or change immutable state.
A narrow completion contract can preserve both truths: the tag is immutable and
the missing registry identity may be created only from the exact retained bytes
under a new protected authorization.

## Decision

1. Keep pre-mutation recovery limited to the state where both tag and registry
   version are absent. Tag-only completion is a separate protocol.
2. Add `package-release-tag-only-completion-intent/v1` and require one new
   PR-mediated, append-only record with an exact `before..after` diff and no
   other changed path.
3. Bind the record to release unit, version, channel, original intent, exact
   failed publication source/run/attempt, the release or recovery record that
   admitted that source, existing tag, expected dist-tag, current base/ref, and
   reason `tag-only-partial-publication`.
4. Bind the retained Actions artifact by ID, name, expiry, archive digest,
   tarball file name and SHA-256, npm integrity, and embedded source commit.
   Rebuild, repack, artifact substitution, and automatic successor creation are
   forbidden.
5. Require the failed publication to be terminal attempt `1`, the source to be
   on protected first-parent history, and the named authorization to
   structurally reconstruct the exact failed publication source.
6. Permit only the first workflow run triggered by the newly merged completion
   record, and only its run attempt `1`, to mutate. Reruns and second workflow
   runs are mutation-disabled before credential setup under every remote state.
7. Immediately before mutation, read tag and registry together. An exact tag
   plus absent exact version permits publishing only the retained bytes. An
   already exact tag/version/source/integrity/dist-tag pair is
   verification-only. Every missing, registry-only, conflicting, mismatched,
   ambiguous, or unverifiable state fails closed.
8. Never delete, move, recreate, or overwrite the existing tag. Completion
   receives no tag-mutation credential.
9. Use a distinct completion workflow. Its registry mutation job receives
   `packages: write` as its only write capability, and the credential is exposed
   only to the native publish step. Tag creation, branch/source mutation,
   sibling release-unit effects, service/application deployment, OCI
   publication, and object-storage publication remain forbidden.
10. If the retained artifact expires, disappears, or fails any identity check,
    stop and return to central policy ownership. Do not rebuild or silently
    advance the version.
11. After publication, verify registry visibility and repository association,
    exact integrity, expected dist-tag, unchanged unrelated aliases, clean exact
    installation and execution, package-only effects, and terminal evidence.
    Later verification failure preserves the exact pair and uses verification
    or correction, not another same-version mutation.
12. Keep Linear and incident records as coordination evidence only. Actual
    registry mutation authority exists only when the protected one-record
    authorization PR is explicitly merged by an authorized maintainer after
    required checks pass.

## Consequences

- One exact tag-only incident can be completed without moving the tag or
  rebuilding the package.
- The repository must retain the failed run artifact long enough to review,
  implement, authorize, and execute completion.
- Completion adds a third append-only intent directory and a distinct workflow,
  increasing local release-policy surface in exchange for an explicit and
  testable authority boundary.
- Static central admission proves Git history and record consistency only.
  Actions-run, artifact, ruleset, registry, credential, dist-tag, and
  authorization-use truth remain repository-owned live checks.
- Registry-only and conflicting states remain fail closed. The decision does
  not create a generic partial-publication repair framework.

## Alternatives considered

### Rerun the failed publication workflow

Rejected because a rerun reuses the historical event and mutation authority and
can repeat tag-capable jobs. It is mutation-disabled by this contract.

### Manually publish the retained tarball

Rejected because manual publication bypasses exact-diff admission,
authorization-use tracking, least-privilege workflow boundaries, and terminal
evidence.

### Delete or move the tag and restart

Rejected because the protected tag is already an immutable release identity.
Deletion, movement, or recreation would rewrite history.

### Rebuild the same version from source

Rejected because source reproducibility is not proof of byte identity. The
completion authority is bound to the retained artifact from the admitted run.

### Always publish a successor prerelease

Rejected as an automatic response because the exact retained artifact is
available and the registry version was never published. If the retained
artifact becomes unavailable or invalid, successor handling requires a new
central decision rather than automatic policy.

Boundary classification: unreleased — corrected in place. The registry package
does not yet exist, and this decision preserves rather than mutates the existing
immutable tag.
