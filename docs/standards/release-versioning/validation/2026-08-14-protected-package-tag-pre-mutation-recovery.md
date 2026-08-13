# Protected package-tag pre-mutation recovery validation — 2026-08-14

- Status: Passed
- Observed at: `2026-08-14T01:28:50+09:00`
- Central change base: `5010-dev/.github@7531b36f84c28524555bd13bd5a710a85ee87162`
- Incident source: `5010-dev/fiftyten-indicators-core@6c4a4f459f3114b99c154dc708b0f73ac8daddee`
- Incident workflow run: `5010-dev/fiftyten-indicators-core#31718098147`
- Intended identity: `@5010-dev/technical-indicators@0.1.0-next.0`
- Design System regression subject: `5010-dev/design-system@6f13fe8be81909150c91ba494da443807b6f9f2d`
- Evidence scope: central policy, schemas, local Git admission, read-only Actions,
  tag, package, and exact remote-ref observations; no publication, ruleset,
  repository setting, credential, release, Linear, or consumer mutation

## Question

May a protected package release preserve its intended version when the first
admitted attempt failed terminally before creating any immutable package tag or
registry version, without reusing the historical release intent or weakening
the immutable-identity contract?

## Incident classification

Yes, through one new PR-mediated pre-mutation recovery authorization. The
read-only Actions query for
[run 31718098147](https://github.com/5010-dev/fiftyten-indicators-core/actions/runs/31718098147)
reported event `push`, terminal conclusion `failure`, and exact head
`6c4a4f459f3114b99c154dc708b0f73ac8daddee`. Release-intent admission,
toolchain setup, package contract, and parity validation succeeded. The first
artifact build command then passed relative output `pkg/technical-indicators`
to a script that required an absolute repository `pkg` or `/tmp` destination.
It failed before artifact creation. The authority, tag, publish, and consumer
jobs were skipped, and terminal outcome evidence reported no immutable
publication identity.

Read-only state at the observation time returned no matching
`technical-indicators-v0.1.0-next.0` tag and the organization GitHub Packages
endpoint returned HTTP 404 for `technical-indicators`. This is a terminal
pre-mutation/no-identity failure, not a published prerelease defect. Preserving
`0.1.0-next.0` does not overwrite or reuse an immutable release identity.

The other states remain distinct:

- tag-only or registry-only state is partial immutable publication and fails
  closed under the existing owner-recovery rules;
- conflicting tag, version, source, or integrity is an immutable-identity
  incident and fails closed; and
- an exact immutable tag/version pair followed by evidence, installation, or
  consumer verification failure remains a completed publication identity and
  receives verification or a successor correction, not pre-mutation recovery.

## Corrected central contract

Standard `2026.08.4` keeps the existing v1 family and adds the separate
`package-release-recovery-intent/v1` discriminator. The profile contract now
declares a distinct recovery directory and owning workflow. A recovery record
binds release unit, version, channel, the unchanged historical intent, exact
failed source and Actions run, current full base commit and `dev` ref, and the
`pre-mutation-no-immutable-identity` reason.

The exact protected `before..after` diff may add only one new recovery record.
The native manifest, changelog, historical intent, profile, workflows, and all
other paths remain unchanged. The recovery `after` is the new publication
source, so any resulting tag, registry version, and integrity must bind to that
exact commit. One record may start at most one attempt. A later terminal
pre-mutation failure requires another new PR-mediated record; no historical
release or recovery intent is edited or reused.

Normal Actions rerun, `workflow_dispatch`, comments, and arbitrary release-unit,
version, channel, source, or tag inputs are not publication authority. The path
does not permit manual tag/package creation, deletion, movement, overwrite,
ruleset relaxation, historical intent modification, sibling release-unit
effects, or automatic advancement to a successor version.

## Executable boundary and regression

The dependency-free reference checker derives normal versus recovery admission
from the exact diff. For recovery it validates one direct append-only record,
current base/ref, unchanged manifest identity and version, one unambiguous
historical intent, byte identity with no intervening protected-history mutation,
a failed source on protected first-parent history that no earlier recovery
record names, addition-only recovery-record history, and the derived tag. A
different run URL does not create a second authorization for the same failed
source. The checker does not query Actions, rulesets, required checks,
authorization-use history, tags, or registries.

The repository publication workflow must perform those live checks, prove that
the prior run is terminal and stopped before immutable mutation, prove that both
identities remain absent, and prove that the authorization has not started a
prior attempt. The central tests exercise valid initial and successive
same-version recovery plus rejection of stale base/ref, manifest mismatch,
missing or ambiguous historical intent, modified original intent, duplicate or
reused recovery authorization, unrelated and sibling changes, tag-present,
registry-present, tag-only, registry-only, conflicting, non-terminal, and
mutation-reaching claims. They also reject delete/restore intent history,
modify/restore recovery history, same-source authorization under another run,
and identity CLI inputs; normal repositories remain explicit opt-in only.

```bash
python3 scripts/docs/test-protected-package-tag-admission.py
scripts/docs/check-repository.sh
git diff --check
```

- focused admission suite: 64 tests, `OK`;
- complete documentation gate: 64 embedded admission tests, `OK`, followed by
  `organization documentation check: OK`; and
- whitespace/error-marker check: exit 0 with no output.

## Default-profile and historical-evidence regression

The 2026-08-12 and 2026-08-13 validation records remain byte-unchanged. The
read-only Design System query returned the same exact revision for `main` and
`dev`, `6f13fe8be81909150c91ba494da443807b6f9f2d`. Its contribution,
release-preparation, and publication workflow blobs remain
`8d8c1581dac20ce7be26c6da25ba6b32497a3812`,
`9ca5cf966941ba7f37f13b1d60f26afe62457cbf`, and
`7ab0f15b4bacd92bc4efea5dbf34c8ad0095ecf4`. It has no
`.github/release-policy/protected-package-tag.v1.json`, so it remains on its
unchanged validated-`main` publication profile.

## Downstream reconciliation contract

This central change does not modify downstream repositories.

- `indicator-platform` must separately update its exact central authority pin
  from `main@7531b36f84c28524555bd13bd5a710a85ee87162` to the eventual merged
  `2026.08.4` central revision and narrowly distinguish pre-mutation recovery
  from partial or completed immutable publication in its L0 wording. It must not
  copy Core package paths, workflow mechanics, current version, or live state.
- `fiftyten-indicators-core` must separately adopt the corrected v1 profile,
  materialize its repository-owned recovery directory and workflow logic, fix
  the package build invocation, add live Actions/tag/registry and one-attempt
  checks, and prove the repository-specific negative cases. That implementation
  PR must not add the actual recovery authorization or publish the package.
- After the Core recovery implementation is merged and revalidated, another
  protected PR may add exactly one recovery record for
  `@5010-dev/technical-indicators@0.1.0-next.0`. Only that PR's admitted `after`
  may become the new publication source. Actual tag creation, package
  publication, registry verification, and consumer evidence belong to that
  later attempt.

No central PR, Platform reconciliation, or Core implementation PR authorizes a
package, tag, registry, credential, ruleset, release, deployment, failed-run
rerun, or Linear mutation.

## Result and boundary

The correction passed. It preserves the original append-only release intent and
the intended unpublished version while restoring a new protected merge as the
only mutation authority. It does not weaken fail-closed handling after any
immutable identity exists.

Boundary classification: unreleased — corrected in place.
