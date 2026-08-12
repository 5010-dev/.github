# Protected package-tag authorization semantics validation — 2026-08-13

- Status: Passed
- Observed at: `2026-08-13T08:45:58+09:00`
- Central change base: `5010-dev/.github@0858f8a40f254cd6a311f8b4f3fb444e3b8a94b2`
- Design System regression subject: `5010-dev/design-system@6f13fe8be81909150c91ba494da443807b6f9f2d`
- Core downstream subject: `5010-dev/fiftyten-indicators-core@f4ae3ea106c75b56f74856cbf9019cd5455ae766`
- Evidence scope: central contract semantics, executable admission regression,
  exact remote refs, and read-only hosting state; no publication, repository
  setting, or consumer mutation

## Question

Can the profile preserve explicit release authorization and every existing
publication invariant without requiring a distinct approving reviewer in every
selecting repository?

## Corrected authority

Yes. The minimum authority is the combination of:

1. an explicit pull-request merge into protected `dev` by an authorized
   maintainer after repository-required checks pass;
2. exact `before..after` release-intent admission and exact
   `source.baseCommit` matching;
3. an immutable, package-specific protected tag;
4. package-only publication effects and paired tag/registry state validation;
   and
5. isolated tag and registry publication credentials.

The author and merger may be the same identity. A ruleset with
`required_approving_review_count: 0` and `require_last_push_approval: false` is
conformant when pull requests remain required, the publication path has no
direct-push bypass, and repository-required checks remain enforced. A distinct
qualified approval remains an optional repository-owned strengthening control;
it is not a central default.

The profile now distinguishes reviewability, PR mediation, maintainer merge
authorization, and independent approval. This prevents an uninformed approval
from being represented as assurance while retaining an auditable PR diff, CI,
explicit merge act, deterministic admission, protected tag, and least-privilege
publication boundary.

## Current source and hosting observations

The central schemas and examples contain no reviewer identity, approval state,
or reviewer-count field. The reference checker reads local Git objects, JSON,
and TOML only. It intentionally does not call a hosting API or inspect pull-
request approvals; the hosting layer owns the PR-only merge boundary, and the
repository workflow revalidates the exact diff and all remote publication
prerequisites before mutation.

The read-only GitHub ruleset query for Core returned active branch ruleset
`20768784`, `dev-reviewed-pull-requests`, targeting exactly `refs/heads/dev`
with no bypass actors. Its current pull-request rule has
`required_approving_review_count: 1` and `require_last_push_approval: true`.
Those values are an optional stronger control under the corrected contract, not
an organization minimum. This central correction does not mutate that ruleset;
Core owns the follow-up decision and read-back before any release-intent merge.
The branch query reported classic protection disabled and required status checks
`off`; the classic protection endpoint returned HTTP 404. This record therefore
does not claim that current Core hosting already satisfies the corrected
required-check clause. Core must preserve or establish its exact repository-
required checks when it reconciles the pull-request rule. The separately missing
package-tag ruleset remains a fail-closed publication gate and is not weakened by
this semantic correction.

Platform `dev@4f6de5171732346496841daf56e9afcf634fa20e` still uses `reviewed`
for the package publication boundary in canonical runtime, deployment, and
quality text. Platform owns a later wording-only reconciliation so those Target
documents use the same PR-mediated terminology. This central change does not
modify Platform.

## Design System regression

The read-only query of Design System remote heads returned the same exact
revision for `main` and `dev`:

```text
6f13fe8be81909150c91ba494da443807b6f9f2d refs/heads/dev
6f13fe8be81909150c91ba494da443807b6f9f2d refs/heads/main
```

The opt-in contract
`.github/release-policy/protected-package-tag.v1.json` is absent at that
revision. The contribution, release-preparation, and release workflow blobs are
still `8d8c1581dac20ce7be26c6da25ba6b32497a3812`,
`9ca5cf966941ba7f37f13b1d60f26afe62457cbf`, and
`7ab0f15b4bacd92bc4efea5dbf34c8ad0095ecf4`. Design System therefore remains
outside the opt-in profile and retains its existing `dev` preparation to `main`
publication flow.

## Executable regression

The unchanged admission behavior and complete repository gate passed:

```bash
python3 scripts/docs/test-protected-package-tag-admission.py
scripts/docs/check-repository.sh
git diff --check
```

- focused admission suite: 39 tests, `OK`;
- complete documentation gate: 39 embedded admission tests, `OK`, followed by
  `organization documentation check: OK`; and
- whitespace/error-marker check: exit 0 with no output.

The schemas keep compatibility major `v1`, and no reviewer-count field or
approval checker is added. The 2026-08-12 record remains the historical evidence
of its original observation rather than being rewritten to claim this later
clarification.

## Result and evidence boundary

This correction changes authorization semantics only. It does not publish a
package, create or move a tag, add a release intent, change a ruleset, mutate a
GitHub Package setting or credential, update Linear, or modify Core, Platform,
Server, App, or Design System. Passing central checks proves the organization
contract and local exact-diff admission remain coherent; it does not prove a
Core package publication or a future hosting-state change.
