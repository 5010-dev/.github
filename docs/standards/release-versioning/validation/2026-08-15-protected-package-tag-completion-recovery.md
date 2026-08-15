# Protected package-tag completion-recovery validation — 2026-08-15

- Status: Passed
- Observed at: `2026-08-15T19:19:50+09:00`
- Central base: `5010-dev/.github@28ba6509a61ba9a71f30843e6afbb0ea2eff4091`
- Starting Standard: `2026.08.6`
- Core completion source: `5010-dev/fiftyten-indicators-core@e2e679715ec19e8ac6ba9a45b08ea9a467d607c5`
- Failed completion run: `5010-dev/fiftyten-indicators-core#31877967715`, attempt `1`
- Intended identity: `@5010-dev/technical-indicators@0.1.0-next.0`
- Evidence scope: central policy, schemas, local Git admission, read-only GitHub
  Actions, pull request, artifact, tag, registry, and Design System workflow
  observations; no package, tag, artifact, source, workflow, ruleset, setting,
  credential, secret, deployment, Platform, Core, App, or Server mutation

## Incident classification

Core PR `#65` changed one direct completion-intent file, passed its exact-head
required check, and merged to protected `dev` as
`e2e679715ec19e8ac6ba9a45b08ea9a467d607c5`. Merge-triggered completion run
`31877967715` is completed `failure`, event `push`, run attempt `1`, and the only
run of workflow `Complete technical-indicators tag-only publication`.

The admission job declared exactly:

- `contents: read`;
- `actions: read`; and
- `packages: read`.

Its live query step called the Actions run, job, artifact and workflow-history
endpoints and then
`GET /repos/5010-dev/fiftyten-indicators-core/commits/e2e679715ec19e8ac6ba9a45b08ea9a467d607c5/pulls`.
GitHub documents that the commit-associated pull requests endpoint requires
Pull requests repository permission read. The job lacked that permission and
failed `Resource not accessible by integration (HTTP 403)`.

This was a pre-mutation authorization failure. The job matrix and step evidence
show:

- exact one-record static admission and current ruleset verification succeeded;
- failure occurred during admission/live verification;
- retained-artifact retrieval was zero-step skipped;
- registry mutation was zero-step skipped;
- post-publication install/execute checks were skipped; and
- the read-only terminal outcome recorded unresolved failure.

No package, tag, retained artifact, branch, source, workflow, ruleset, setting,
credential, secret, OCI image, object-storage object, sibling release unit, or
deployment was created, changed, deleted, or rerun by this incident analysis.

## Live immutable-state read-back

Read-only GitHub and registry queries confirmed:

- immutable tag `technical-indicators-v0.1.0-next.0` still resolves to
  `099edf52740633a200c9d57abf8c7a4310fe1507`;
- the organization package endpoint for `technical-indicators` returns HTTP 404;
- retained artifact `9202971363` remains unexpired with expiry
  `2026-09-13T00:14:53Z`, name `technical-indicators-0.1.0-next.0`, source
  `099edf52740633a200c9d57abf8c7a4310fe1507`, and archive digest
  `sha256:8762d74fcaedf12ef0629e97c9b45935229c42b07829e6c9a5af0ce8d8fc1104`;
- the retained tarball SHA-256 remains
  `669ee0898bff9b833bb49e22cb8208ff58669efb647089995796ee6b48155acd`;
- npm integrity remains
  `sha512-iL7N79DPpUUGCOBBgLPuGpnEeZOqWbL3Atyg3/VhLNGgd/wsGOg4K5VXK9re202ilriv4SXU6IM0pkoKOqZj4g==`;
- original completion record
  `.github/release-tag-only-completion-intents/technical-indicators/0.1.0-next.0.json`
  remains exact with SHA-256
  `915aafe8076d0630fb389ccf590c8c9fad0bfb8b5fb10e9f1ad949134bc6b066`;
  and
- protected `dev` remains
  `e2e679715ec19e8ac6ba9a45b08ea9a467d607c5`.

The immutable tag and registry-absent state are unchanged. The original
completion record and run attempt `1` are consumed authorization. Actions rerun,
a second workflow run from that record, manual publication, tag mutation, or
record reuse is forbidden.

## Corrected central contract

Standard `2026.08.7` corrects admission/live verification to exactly:

- `contents: read`;
- `actions: read`;
- `pull-requests: read`; and
- `packages: read`.

It preserves the remaining responsibility boundaries:

| Responsibility | Exact permission set |
| --- | --- |
| Admission and live verification | `contents: read`, `actions: read`, `pull-requests: read`, `packages: read` |
| Retained-artifact retrieval | `actions: read` |
| Registry mutation | `packages: write` |
| Post-publication verification | `contents: read`, `packages: read` |

No completion or recovery responsibility receives `contents: write`. Neither
workflow receives the tag App credential. Registry mutation remains the only
allowed effect, and only for the absent exact package version.

The new
`package-release-tag-only-completion-recovery-intent/v1` contract adds a fourth
non-overlapping, append-only authorization lane. Its exact current Core incident
shape is preserved as the non-authoritative schema fixture
[`fixtures/2026-08-15-core-tag-only-completion-recovery-intent.valid.json`](./fixtures/2026-08-15-core-tag-only-completion-recovery-intent.valid.json).
The fixture is validation evidence in the central repository; it is not a Core
authorization record and cannot trigger publication.

The first successor binds the immutable original completion path and bytes,
original publication and retained-artifact chain, failed completion source/run,
attempt `1`, terminal admission failure, not-started retrieval/mutation/consumer
phases, unchanged tag-present/registry-absent state, and current protected
base/ref. A later failure requires a new direct successor to the latest recovery
record. The checker rejects reuse, branching, duplicate failed runs, stale bases,
multiple-file authorization diffs, record mutation, and sibling effects.

## Executable permission preflight

Static permission declarations are insufficient. An adopting repository's
implementation/foundation PR must execute the following zero-mutation inventory
with the same four-read admission permission set before any recovery
authorization PR may merge:

| Endpoint responsibility | Permission |
| --- | --- |
| Actions run metadata | `actions: read` |
| Actions job metadata | `actions: read` |
| Actions artifact metadata | `actions: read` |
| Completion workflow-run history | `actions: read` |
| Commit-associated pull requests | `pull-requests: read` |
| Git tag/ref query | `contents: read` |
| Authenticated registry version/dist-tag query | `packages: read` |

Any HTTP 403 or ambiguous response fails the required check. The preflight has
no package-write or tag App credential and creates no package, tag, branch,
source, artifact, deployment, OCI object, object-storage object, or sibling
effect.

## Regression and non-applicability

The dependency-free checker covers corrected permission sets, endpoint
inventory, the current incident fixture, append-only successor admission, stale
base, rerun/attempt mismatch, retrieval or mutation having started, tag and
registry state drift, retained-artifact identity, original completion mutation,
duplicate or branched successors, multi-file diffs, sibling effects, and exact
pair verification-only state.

```bash
python3 scripts/docs/test-protected-package-tag-admission.py
scripts/docs/check-repository.sh
git diff --check
```

- focused admission suite: 133 tests, `OK`;
- complete documentation gate: 133 embedded admission tests, `OK`, followed by
  `organization documentation check: OK`; and
- whitespace/error-marker check: exit 0 with no output.

Design System remains outside the opt-in profile. Read-only observation at
`5010-dev/design-system@6f13fe8be81909150c91ba494da443807b6f9f2d`
confirmed `.github/workflows/release.yml` still triggers only on pushes to
`main` and retains its existing Changesets publication path. The explicit-opt-in
regression rejects profile admission in a repository with only that main release
workflow and preserves its workflow bytes.

## Authority and next step

This central correction, its validation fixture, ADR, and Linear evidence do not
authorize registry mutation. After this central PR is merged, Platform and Core
require separately authorized reconciliation. Core's implementation/foundation
PR must run the executable permission preflight. Only a later protected PR that
adds one direct completion-recovery record, passes required checks, and is
explicitly merged by an authorized maintainer can authorize another first
run/attempt `1`.

Linear evidence is coordination evidence, not publication authority. ENG-226
and its parent remain In Progress. Publication, external-consumer, final-release,
App handoff, and parent checklist items remain incomplete.

Boundary classification: released — compatibility required because the
immutable `technical-indicators-v0.1.0-next.0` tag and a consumed completion
authorization already exist while the registry version remains absent.
