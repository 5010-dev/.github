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
YAML syntax through Ruby's standard parser, TOML syntax through Python
`tomllib`, Just example syntax through Just itself, shell syntax, and the
engineering-documentation scaffold. It also runs the dependency-free protected
package-tag admission regression suite against temporary Git repositories. The
workflow pins Just `1.57.0`; local validation requires Python 3.11 or newer plus
compatible `ruby`, `git`, and `just` commands.

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

The checker derives package identity from the repository contract, newly added
intent, JSON or TOML native manifest, and exact Git diff. It rejects stale,
multiple, changed, duplicate, or conflicting intent; contract/native package
identity mismatch; non-increasing SemVer precedence; non-version manifest
mutation; deletion, rename, exact-content copy, type change, non-regular files;
paths outside release preparation; and sibling release-unit mutation. JSON input
must be strict UTF-8 without duplicate keys or non-standard numeric constants.
The checker does not publish or query remote tag, registry, ruleset, permission,
or approval state.

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
