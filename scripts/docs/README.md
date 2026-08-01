# Governance repository tooling

This directory contains dependency-light reference tooling for the
[`5010-arc42-v1`](../../docs/standards/engineering-documentation/README.md)
organization profile and validation of the canonical
[Developer Tooling Standard](../../docs/standards/developer-tooling/README.md)
source.

## Organization source check

Validate this `.github` repository's standards, guides, decisions, templates,
links, shell syntax, and generated scaffold:

```bash
scripts/docs/check-repository.sh
```

The check scaffolds a temporary example, verifies it with the consumer
conformance checker, confirms that a second scaffold refuses to overwrite the
generated files, and validates the Developer Tooling documents, stable rule
catalog, runtime catalog, schemas, examples, bootstrap locator, and workflow
template. It also validates both governance workflows' complete trigger paths,
least-privilege permissions, immutable actions, pinned runners, and checkout
credential handling.

The
[documentation governance workflow](../../.github/workflows/docs.yml) runs this
same gate for pull requests targeting `main` and pushes to `main`. The workflow
is read-only, uses explicit least-privilege permissions, and does not replace
repository-owner review of factual or architectural claims.

## Developer Tooling source check

Validate only the normative Developer Tooling source set:

```bash
python3 scripts/docs/check-developer-tooling-standard.py
```

This governance check verifies source completeness, JSON syntax, every Draft
2020-12 keyword used by the local schemas, schema validation of catalogs and
examples, negative contract fixtures, stable rule IDs, GP-006 through GP-020
traceability, source headings, version alignment, runtime baseline invariants,
example consistency, and repository-independence scans across the standard,
guides, and owning ADR.

The embedded schema evaluator intentionally supports exactly the keyword set
used by these dependency-light source contracts. The gate fails if a schema
introduces an unsupported keyword, so it cannot silently accept a constraint it
does not implement.

It is not the cross-repository Golden Path conformance checker. That separately
versioned implementation will consume the catalog and schemas to evaluate
repository-local metadata, native files, commands, and evidence.

## Golden Path integration checks

Validate the policy-owned bootstrap locator, workflow-template metadata, exact
release and automation pins, Free private baseline, dry-run fixture, guide
coverage, and governance-workflow wiring without network access:

```bash
python3 scripts/docs/check-golden-path-integration.py
```

The path-scoped
[Golden Path bootstrap workflow](../../.github/workflows/golden-path-bootstrap.yml)
additionally installs the exact, checksum- and provenance-verified Golden Path
`0.2.0` release and runs:

```bash
GOLDEN_PATH_BIN=/path/to/verified/golden-path \
  scripts/docs/check-golden-path-bootstrap.sh
```

That release check verifies the pinned release and standard-snapshot manifests,
their digests and attestations, and every policy-owned machine snapshot file.
It then previews and materializes the documentation fixture in a temporary
directory, compares the deterministic plans, executes the generated bootstrap
wrapper, checks the candidate with the released checker, and proves that the
workflow-template profile sentinel exits as a usage error until replaced. It
never writes to a consumer repository and does not duplicate checker or
generator source in this policy repository.

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
