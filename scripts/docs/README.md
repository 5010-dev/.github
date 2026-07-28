# Documentation tooling

This directory contains dependency-light reference tooling for the
[`5010-arc42-v1`](../../docs/standards/engineering-documentation/README.md)
organization profile.

## Organization source check

Validate this `.github` repository's standards, guides, decisions, templates,
links, shell syntax, and generated scaffold:

```bash
scripts/docs/check-repository.sh
```

The check scaffolds a temporary example, verifies it with the consumer
conformance checker, and confirms that a second scaffold refuses to overwrite
the generated files.

The
[documentation governance workflow](../../.github/workflows/docs.yml) runs this
same gate for pull requests targeting `main` and pushes to `main`. The workflow
is read-only, uses explicit least-privilege permissions, and does not replace
repository-owner review of factual or architectural claims.

## Scaffold

Create the base L0 documentation tree in a new repository or engineering layer:

```bash
scripts/docs/scaffold-arc42.sh \
  --target /path/to/repository \
  --system-name "Example System" \
  --scope "Repository-wide engineering system"
```

The scaffold:

- renders the repository template with the fixed current organization profile;
- creates only missing directories and files;
- performs a complete collision preflight before writing; and
- never overwrites existing documentation.

Use `--dry-run` to show destination paths without writing. Existing
documentation should follow the
[migration guide](../../docs/guides/migrating-existing-documentation.md)
instead of forcing the scaffold.

## Conformance check

Check an adopted repository:

```bash
scripts/docs/check-contract.sh --target /path/to/repository
```

The reference check validates the base files, profile metadata, chapter states,
ADR indexing, unresolved scaffold tokens, local links, and trailing whitespace.
It does not prove factual accuracy or deployed state.

Repositories may copy, wrap, or reimplement the checker in their native task
system. A replacement must preserve the minimum validation contract and record
material exceptions.
