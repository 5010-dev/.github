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
engineering-documentation scaffold. The workflow pins Just `1.57.0`; local
validation requires compatible `python3`, `ruby`, and `just` commands.

The gate does not execute a Golden Path binary or any reference-example recipe,
validate consumer repositories, call live GitHub APIs, replay another
repository's `just ci`, or implement package publication admission. Package
release workflows remain repository-owned under the
[Release and Versioning Standard](../../docs/standards/release-versioning/README.md).

The [documentation governance workflow](../../.github/workflows/docs.yml) runs
this gate for pull requests and pushes to `main`.

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
Developer Tooling conformance checker or a package publication workflow.
