# Engineering documentation standard

The `5010-dev` organization uses arc42 as the canonical documentation system for
engineering systems, whether the system occupies an entire repository or an
independently governed layer inside a mixed-purpose repository.

The current organization profile is **`5010-arc42-v1`**.

## Normative documents

1. [Engineering documentation contract](./contract.md) — applicability,
   authority, required repository capabilities, layering, and exceptions.
2. [5010 arc42 profile](./arc42-profile.md) — required L0 chapters, metadata,
   state vocabulary, L1 profiles, and placement rules.
3. [Documentation lifecycle and validation](./lifecycle-and-validation.md) —
   adoption, migration, same-change completion, profile evolution, and
   conformance checks.

The governing decision is
[ADR-0004: Adopt arc42 as the canonical engineering documentation system](../../decisions/0004-adopt-arc42-engineering-documentation-system.md).

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
these documents are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14), when and only when they appear
in all capitals.

## Supporting material

- [Adoption guide](../../guides/adopting-arc42.md)
- [Migration guide](../../guides/migrating-existing-documentation.md)
- [Templates](../../../templates/engineering-documentation/README.md)
- [Scaffold and conformance tools](../../../scripts/docs/README.md)

Supporting material helps repositories implement the standard but does not
override it.
