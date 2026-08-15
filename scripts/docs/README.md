# Governance repository checks

This directory contains repository-owned, dependency-light checks for this
`.github` governance repository and the organization arc42 scaffold.

## Canonical documentation gate

Run:

```bash
scripts/docs/check-repository.sh
```

The gate checks required sources, including the Golden Path journeys and
reference examples, local Markdown links, trailing whitespace, JSON syntax,
Draft 2020-12 schema conformance with pinned Ajv dependencies, YAML syntax
through Ruby's standard parser, TOML syntax through Python `tomllib`, Just
example syntax through Just itself, shell syntax, and the
engineering-documentation scaffold. It also runs the dependency-free protected
package-tag admission regression suite against temporary Git repositories. The
workflow pins Node `24.19.0` and Just `1.57.0`; local validation requires Python
3.11 or newer plus compatible `node`, `npm`, `ruby`, `git`, and `just` commands.
Install the schema validator dependencies before running the gate:

```bash
npm ci --prefix scripts/docs --ignore-scripts --no-audit --no-fund
```

The gate does not execute a Golden Path binary or any reference-example recipe,
validate consumer repositories, call live GitHub APIs, or replay another
repository's `just ci`.

The [documentation governance workflow](../../.github/workflows/docs.yml) runs
this gate for pull requests and pushes to `main`.

## Protected package-tag admission

Run the exact-diff checker from a repository that has explicitly selected the
profile:

```bash
python3 scripts/docs/check-protected-package-tag-admission.py \
  --repository . \
  --base "$BEFORE_SHA" \
  --head "$AFTER_SHA" \
  --event-ref refs/heads/dev
```

The checker derives package identity from the repository contract, a newly added
normal, recovery, tag-only completion, or completion-recovery intent, JSON or TOML native manifest,
historical intent, and exact Git diff. Normal admission rejects stale, multiple,
changed, duplicate,
or conflicting intent; contract/native package identity mismatch;
non-increasing SemVer precedence; non-version manifest mutation; deletion,
rename, exact-content copy, type change, non-regular files; paths outside
release preparation; and sibling release-unit mutation. Recovery admission
requires one newly added record and no other change, an unchanged manifest and
byte-identical, addition-only original intent, exact current base/ref, a failed
source on protected first-parent history that structurally reconstructs the
original or latest recovery admission and that no prior recovery record names,
addition-only recovery history, and declared terminal pre-mutation absence of
tag and registry identities. The initial failed source must be the exact commit
that added the original release intent; a preparation-only successor is not
authority. Recovery and completion record paths must remain outside every
declared sibling mutation surface. A different run URL or unrelated later
commit cannot split one authorization source into another. JSON input must be
strict UTF-8 without duplicate keys or non-standard numeric constants.

Tag-only completion admission requires one newly added record and no other
change, an unchanged manifest and original intent, a failed publication source
on protected first-parent history that reconstructs the named exact release or
latest recovery admission, one record per release-unit/version and failed run,
an exact derived tag and dist-tag, and a digest-bound retained artifact whose
embedded source equals the failed publication source. The checker validates the
recorded attempt-1 tag-present/registry-absent shape but does not claim that
remote state is true.

Completion-recovery admission requires one newly added direct record and no
other change. It binds the immutable original completion path and SHA-256,
original failed-publication and retained-artifact chain, exact failed completion
source/run/attempt/phase, proof that artifact retrieval and registry mutation did
not start, authorization-run ordinal `1`, unchanged
tag-present/registry-absent state, and exact current base/ref. The first record
must follow the original completion addition; every later record must follow the
latest recovery addition. Reuse, branching, duplicates, stale bases, and
multiple-file authorization diffs fail closed. Repository live admission must
prove that ordinal from workflow history; run attempt `1` alone is insufficient.

The checker intentionally does not publish, query Actions, remote tag, or
registry state, inspect authorization-use history, inspect hosting rulesets or
permissions, or inspect pull-request approvals. The hosting layer owns the
PR-only protected merge boundary. The repository publication workflow must pass
the exact merge `before` and `after` commits to this checker and revalidate
rulesets, required checks, the prior run's repository, declared workflow,
event/ref, source, attempt, outcome, and tag-only phase evidence, record
non-reuse, tag and registry state, retained-artifact identity and expiry, package
closure, permissions, and every other publication prerequisite before mutation.
A normal rerun or arbitrary workflow input is not publication authority. A
tag-only completion workflow must additionally mutation-disable every rerun and
second workflow run before credential setup and must never receive tag mutation
authority. Its profile fixes separate exact permissions for admission and live
verification (`contents: read`, `actions: read`, `pull-requests: read`,
`packages: read`), retained
artifact retrieval (`actions: read`), registry mutation (`packages: write`),
and post-publication verification (`contents: read`, `packages: read`).

Before a completion-recovery authorization PR can merge, the selecting
repository's foundation PR must execute the profile's zero-mutation live
permission preflight. It calls every Actions run/job/artifact/history,
commit-associated pull request, Git tag/ref, and authenticated registry
version/dist-tag endpoint used by admission with the exact four-read set. The
preflight fails on HTTP 403 or ambiguity and receives no package-write or tag App
credential.

The invocation requires the exact base and head commit objects plus their
ancestry. An adopting checkout MUST fetch sufficient history, normally with
`fetch-depth: 0`; a shallow checkout that cannot resolve or relate both commits
fails closed. Contract patterns are segment-aware: `*`, `?`, and bracket
expressions stay within one segment, while a complete `**` segment crosses zero
or more segments.

Run its repository-owned tests directly with:

```bash
python3 scripts/docs/test-protected-package-tag-admission.py
```

Validate the Draft 2020-12 schemas and their examples directly with:

```bash
npm run check:schemas --prefix scripts/docs
```

## Engineering documentation scaffold

```bash
scripts/docs/scaffold-arc42.sh \
  --target /path/to/repository \
  --system-name "Example System" \
  --scope "Repository-wide engineering system"
```

Use `--dry-run` to inspect destinations. The scaffold refuses to overwrite an
existing generated tree.

Validate an adopted documentation tree with:

```bash
scripts/docs/check-contract.sh --target /path/to/repository
```

This checker belongs to the engineering-documentation standard. It is not a
Developer Tooling conformance checker.
