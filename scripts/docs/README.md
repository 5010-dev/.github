# Governance repository checks

This directory contains repository-owned, dependency-light checks for this
`.github` governance repository and the organization arc42 scaffold.

## Canonical documentation gate

Run:

```bash
scripts/docs/check-repository.sh
```

The gate checks required sources, including the Golden Path journeys and
reference examples, local Markdown links, trailing whitespace, shell syntax,
JSON syntax, and the engineering-documentation scaffold. It does not install or
execute a Golden Path binary, validate consumer repositories, call live GitHub
APIs, or replay another repository's `just ci`.

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
Developer Tooling conformance checker.
