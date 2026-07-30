# Stable rule catalog

[`catalog.v1.json`](./catalog.v1.json) is the normative machine-readable catalog
for automatic and hybrid conformance rules in standard `2026.07`.

## Rule ID lifecycle

Rule IDs use `DT-<CATEGORY>-<NUMBER>`:

| Category | Responsibility |
| --- | --- |
| `META` | Repository metadata and declared applicability |
| `CMD` | Root Just commands and task composition |
| `TOOL` | Toolchain ownership, selectors, and locks |
| `DEP` | Native dependency management |
| `ASSET` | Materialization, immutable distribution, and caller boundaries |
| `CONF` | Checker execution and output |
| `EXC` | Exception validity and risk tiers |
| `RUNTIME` | Runtime lifecycle and disposition |
| `NODE`, `PY`, `GO`, `RUST`, `ZIG` | Language profile contracts |
| `IAC` | Infrastructure authoring and delivery outcomes |
| `HYGIENE` | Dependency automation, vulnerability, and cache |
| `SUPPLY` | SBOM and provenance |
| `PLATFORM` | Supported execution and development containers |
| `RELEASE` | Golden Path versioning and compatibility |

An ID is never reused with a different meaning. A retired rule remains in the
catalog with `retiredIn` and `replacement`; consumers can therefore interpret
historical findings.

## Evaluation

- `MUST` and `MUST_NOT` rules produce `fail` when applicable and unwaived.
- `SHOULD` and `SHOULD_NOT` rules produce `warn`.
- `MAY` rules produce `skip` or no finding when not selected.
- `assessment: automated` can be decided from checked-in repository data.
- `assessment: manual` requires named durable evidence.
- `assessment: hybrid` combines structural checks with external/current
  evidence.

`waivable` and `highRisk` drive the
[exception contract](../exceptions.md). Severity does not change the BCP 14
requirement level.

The human-readable document remains the explanatory authority. The catalog
binds each rule to a decision, document, and stable heading.
