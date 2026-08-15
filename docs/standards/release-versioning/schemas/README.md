# Release and Versioning schemas

- Status: Accepted
- Standard version: `2026.08.7`

These Draft 2020-12 JSON Schemas support the opt-in
[protected package-tag publication profile](../protected-package-tag.md):

| Schema | Purpose |
| --- | --- |
| [`protected-package-tag-profile/v1`](./protected-package-tag-profile-v1.schema.json) | Repository-owned package release-unit, source, closure, tag, channel, isolation, permission, and ownership contract |
| [`package-release-intent/v1`](./package-release-intent-v1.schema.json) | Immutable PR-based release-unit, channel, exact version, and source-boundary intent |
| [`package-release-recovery-intent/v1`](./package-release-recovery-intent-v1.schema.json) | Separate immutable authorization for one same-version attempt after a terminal pre-mutation failure with no tag or registry version |
| [`package-release-tag-only-completion-intent/v1`](./package-release-tag-only-completion-intent-v1.schema.json) | Separate immutable authorization to publish only an absent registry version from an exact retained attempt-1 artifact while preserving the existing tag |
| [`package-release-tag-only-completion-recovery-intent/v1`](./package-release-tag-only-completion-recovery-intent-v1.schema.json) | Append-only successor authorization after a completion run fails before retained-artifact retrieval and registry mutation while the exact tag-only state remains unchanged |

Valid illustrative documents are under [`examples/`](./examples/). They use
reserved example identities and do not select a package name, initial version,
tag pattern, or current release state for any repository.

The profile binds both package identity and version to one native manifest. A
repository selects either JSON Pointer selectors for a JSON manifest or dotted
bare-key selectors for a TOML manifest. The native manifest remains the version
authority; the contract only tells admission where to read it.

The profile also declares a distinct recovery-intent directory and the
repository workflow that owns recovery admission. A recovery record binds the
historical release intent, exact failed source and Actions run, unchanged native
version, current base and ref, and the pre-mutation/no-identity recovery class.
Its absent tag and registry states are reviewed claims, not remote truth: the
repository workflow must query Actions, Git, and the registry again before any
mutation and reject a consumed authorization or changed state.

The profile additionally declares non-overlapping tag-only completion and
completion-recovery intent directories with distinct registry-only workflows. A completion record
binds the original intent, exact failed publication source/run/attempt and
admission record, existing tag, expected dist-tag, current base/ref, and the
retained artifact ID, expiry, archive digest, tarball SHA-256, npm integrity,
and embedded source. These are reviewed claims; the repository workflow must
re-read the run and prove its selecting-repository identity, declared normal or
recovery workflow, protected `dev` push event/ref, exact source, attempt, and
outcome together with trusted job or terminal evidence that tag creation
completed before registry publication failed. It must also re-read the tag,
registry, artifact, authorization-use history, rulesets, and credentials and
reject rebuilds, rerun mutation, second-run mutation, expired artifacts,
registry-only state, or any mismatch.

The completion profile fixes four exact job-scoped permission sets. Admission
and live verification receive `contents: read`, `actions: read`,
`pull-requests: read`, and `packages: read`; retained-artifact retrieval receives only `actions: read`;
registry mutation receives only `packages: write`; and post-publication
verification receives `contents: read` and `packages: read`. The schema rejects
missing, combined, reordered, or broadened permission sets rather than treating
the mutation credential as the whole workflow permission contract.

A completion-recovery record binds the immutable original completion path and
SHA-256, original publication and retained-artifact chain, exact failed
completion source/run/attempt/phase, proof that retrieval and mutation never
started, unchanged tag-present/registry-absent state, and the current protected
base/ref. The first successor names the original completion record; each later
successor names the latest recovery record. The checker rejects reuse, branching,
duplicate failed runs, stale bases, and any multi-path authorization diff.

Before any completion-recovery authorization PR can merge, the selecting
repository's foundation change must execute a live zero-mutation permission
preflight in its validation workflow. The profile fixes the same four read
permissions plus the endpoint-to-permission inventory for Actions run, job,
artifact and workflow-run history, commit-associated pull requests, Git tag/ref,
and authenticated registry version/dist-tag reads. Package write and tag App
credentials are forbidden.

Path patterns are segment-aware: `*`, `?`, and bracket expressions match within
one segment and never match `/`; a complete `**` segment matches zero or more
segments. Plain paths forbid glob syntax, Git pathspec magic, traversal,
backslashes, and control characters.

The dependency-free reference checker requires Python 3.11 or newer and
validates the contract and the exact Git merge diff:

```bash
python3 scripts/docs/check-protected-package-tag-admission.py \
  --repository . \
  --base "$BEFORE_SHA" \
  --head "$AFTER_SHA" \
  --event-ref refs/heads/dev
```

The checker discovers the contract at
`.github/release-policy/protected-package-tag.v1.json` by default and derives
release unit, channel, version, tag, and normal-versus-recovery admission from
repository state. It also derives tag-only completion or completion-recovery
admission when the exact diff adds one record in the corresponding declared
directory. It does not accept those
identities as command inputs. A
repository MAY use a different canonical contract path through `--contract`,
but the workflow must keep that path fixed rather than expose it as an untrusted
dispatch input.

Schemas validate serialized structure and directly express channel/version
shape where possible. Admission remains the narrower normative acceptor for
cross-field inequalities, unique sibling IDs, native-manifest equivalence,
repository file modes, exact Git history, and diff-derived constraints that JSON
Schema cannot establish alone.

Schema and checker compatibility is `v1`. Correct them in place before a real
released consumer depends on their current shape. Once a repository pins a
released schema or checker identity, incompatible evolution requires a new
schema/checker major or a coordinated update before its publication boundary.

These schemas and the checker do not form a release queue or current-version
registry. They do not publish, inspect GitHub rulesets or pull-request approvals,
query a package registry, or prove workflow side effects. Those checks and all
credentials remain repository-owned. They intentionally encode no reviewer,
approval-state, or reviewer-count field: the hosting layer owns the PR-only merge
boundary, and an independent approval is an optional repository control rather
than schema input.
