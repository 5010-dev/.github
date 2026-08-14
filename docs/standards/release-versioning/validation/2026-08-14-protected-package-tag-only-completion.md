# Protected package-tag tag-only completion validation — 2026-08-14

- Status: Passed
- Observed at: `2026-08-14T20:57:28+09:00`
- Central change base: `5010-dev/.github@f1cd525a5040ccd2c219eb044014d5b6eadf4f5f`
- Permission correction base: `5010-dev/.github@1462bff26a9ee3528cac32c4b1678bc9c59f1ff2`
- Tag-only partial-publication source: `5010-dev/fiftyten-indicators-core@099edf52740633a200c9d57abf8c7a4310fe1507`
- Failed publication run: `5010-dev/fiftyten-indicators-core#31756609971`, attempt `1`
- Intended identity: `@5010-dev/technical-indicators@0.1.0-next.0`
- Evidence scope: central policy, schemas, local Git admission, read-only
  Actions, retained-artifact, tag, and package observations; no package, tag,
  ruleset, repository setting, credential, release, deployment, Platform, or
  Core mutation

## Incident classification

The protected run is terminal `failure` at exact source
`099edf52740633a200c9d57abf8c7a4310fe1507`. Its admission, deterministic
package build, parity and clean-tarball consumer, live recovery authority,
paired-state, and tag ruleset checks succeeded. The dedicated tag authority
created `technical-indicators-v0.1.0-next.0` at that exact source. Registry
publication then passed a downloaded relative tarball path to `npm publish`;
npm interpreted it as a Git dependency and exited before creating the package.

Read-only state at the observation time confirmed:

- the tag still resolves exactly to
  `099edf52740633a200c9d57abf8c7a4310fe1507`;
- the organization GitHub Package and versions endpoints return HTTP 404;
- the run is completed failure, event `push`, run attempt `1`;
- retained artifact `technical-indicators-0.1.0-next.0` has ID `9202971363`,
  expiry `2026-09-13T00:14:53Z`, and archive digest
  `sha256:8762d74fcaedf12ef0629e97c9b45935229c42b07829e6c9a5af0ce8d8fc1104`;
- its tarball is
  `5010-dev-technical-indicators-0.1.0-next.0.tgz` with SHA-256
  `669ee0898bff9b833bb49e22cb8208ff58669efb647089995796ee6b48155acd`;
- its npm integrity is
  `sha512-iL7N79DPpUUGCOBBgLPuGpnEeZOqWbL3Atyg3/VhLNGgd/wsGOg4K5VXK9re202ilriv4SXU6IM0pkoKOqZj4g==`;
  and
- its embedded source is
  `099edf52740633a200c9d57abf8c7a4310fe1507`.

This is an exact tag-only partial publication. It is not a pre-mutation
no-identity failure, a registry-only state, a completed package publication, or
a failed completion workflow.

## Corrected central contract

Standard `2026.08.5` adds the separate
`package-release-tag-only-completion-intent/v1` discriminator and a third
non-overlapping profile directory with a distinct registry-only completion
workflow. The record freezes the failed publication admission and the retained
artifact identities above. The exact completion-authorization diff adds one
record and nothing else.

Standard `2026.08.6` closes the executable permission profile before downstream
adoption. It separates admission and live verification, retained-artifact
retrieval, registry mutation, and post-publication verification into four exact
job permission sets instead of modeling the mutation permission as the whole
completion workflow.

The first workflow run triggered by that record, at run attempt `1`, is the only
execution that may create the absent exact registry version. It downloads the
retained artifact and does not rebuild. Every rerun and second workflow run is
mutation-disabled before credential setup. The existing tag is always
verification-only and the completion workflow has no tag credential.

The pre-mutation recovery checker continues rejecting tag-present state. The new
completion admission accepts only tag-present/registry-absent claims and binds
the failed source to its exact normal or latest recovery admission. Live
repository automation must re-read and verify the failed run's selecting
repository, declared publication or recovery workflow, protected `dev` push
event/ref, exact source, attempt, outcome, and trusted evidence that its exact
tag-creation phase completed before registry publication failed. It must verify
those facts together with the immutable tag, registry, retained artifact,
rulesets, authorization-use history, credentials, package closure, dist-tags,
and sibling isolation before mutation.

## Four-state and permission outcomes

| Observed state immediately before mutation | Outcome |
| --- | --- |
| Exact tag at the failed source; registry version absent; first completion run attempt 1 | Publish retained artifact only |
| Exact tag and exact registry package, integrity, source, and dist-tag | Verification-only |
| Tag missing, moved, recreated, or conflicting | Fail closed |
| Registry-only, mismatched, ambiguous, or unverifiable state | Fail closed |

| Completion responsibility | Exact permission set |
| --- | --- |
| Admission and live verification | `contents: read`, `actions: read`, `packages: read` |
| Retained-artifact retrieval | `actions: read` |
| Registry mutation | `packages: write` |
| Post-publication verification | `contents: read`, `packages: read` |

Registry credentials are step-scoped, and representative package execution is
credential-free. The tag App private key and installation token are absent.
Package, OCI, object storage, service/application deployment, and branch/source
effects outside the exact registry version are forbidden.

## Executable boundary and regression

The dependency-free reference checker derives normal, pre-mutation recovery,
or tag-only completion admission from the exact diff. Completion tests cover
normal-release and recovery-admitted failed sources, source separation between
package and authorization commits, stale base, run-attempt mismatch,
tag-absent/registry-present claims, tag and dist-tag mismatch, retained source,
non-RFC 3339 artifact expiry, tarball digest and npm-integrity mismatch,
unrelated and multiple records,
duplicate identity authorization, modified recovery authority, missing or
overlapping profile boundaries, a superseded initial source after later
recovery authorization, a preparation-only successor claimed as an initial
failed source, sibling mutation-path overlap for recovery or completion records,
shared workflows, release-path overlap, and missing or broadened completion job
permissions.

```bash
python3 scripts/docs/test-protected-package-tag-admission.py
scripts/docs/check-repository.sh
git diff --check
```

- focused admission suite: 101 tests, `OK`;
- complete documentation gate: 101 embedded admission tests, `OK`, followed by
  `organization documentation check: OK`; and
- whitespace/error-marker check: exit 0 with no output.

## Downstream reconciliation contract

This central change does not modify downstream repositories.

1. `indicator-platform` separately aligns its canonical package recovery
   boundary to the exact merged central revision.
2. `fiftyten-indicators-core` then separately implements the distinct completion
   directory, checker pin, workflow, live artifact/run/tag/registry guards,
   no-rebuild behavior, first-run/attempt gate, credential isolation, four-state
   tests, runbook, and validation record. That implementation PR does not add a
   completion authorization or publish.
3. Only after those changes are merged and validated may another protected PR
   add the one exact completion record. Its explicit maintainer merge after
   required checks is publication authorization.

Linear incident evidence is coordination context, not authority. No central,
Platform, or Core implementation PR authorizes package publication, tag
mutation, ruleset change, failed-run rerun, or deployment.

## Result and boundary

The contract preserves the existing immutable tag and permits only the missing
registry identity from the exact retained artifact under a new one-record
authorization. Registry-only, conflicting, expired-artifact, rebuilt,
rerun-mutation, and second-run-mutation states remain fail closed.

Boundary classification: released — compatibility required because the
protected immutable tag `technical-indicators-v0.1.0-next.0` already exists at
`099edf52740633a200c9d57abf8c7a4310fe1507`, while the matching registry version
remains absent.
