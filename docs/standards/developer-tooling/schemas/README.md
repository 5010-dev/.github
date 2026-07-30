# Developer tooling schemas

These JSON Schemas are normative serialized-contract sources for standard
`2026.07`.

| Schema | Contract |
| --- | --- |
| [`golden-path-metadata/v1`](./golden-path-metadata-v1.schema.json) | Repository-local profile, artifact, capability, and version declaration |
| [`golden-path-exceptions/v1`](./golden-path-exceptions-v1.schema.json) | Scoped, approved, expiring MUST-rule waivers |
| [`golden-path-checker-output/v1`](./golden-path-checker-output-v1.schema.json) | Deterministic machine-readable checker result |
| [`golden-path-rule-catalog/v1`](./golden-path-rule-catalog-v1.schema.json) | Stable machine rule catalog |
| [`runtime-support/v1`](./runtime-support-v1.schema.json) | Versioned lifecycle/disposition catalog |

Schemas use JSON Schema Draft 2020-12. YAML repository inputs MUST deserialize
to the same data model before validation. YAML tags, duplicate keys, and
implementation-specific object types are not part of the contract.

Examples:

- [`golden-path-metadata/v1`](./examples/golden-path-metadata-v1.valid.json)
- [`golden-path-exceptions/v1`](./examples/golden-path-exceptions-v1.valid.json)
- [`golden-path-checker-output/v1`](./examples/golden-path-checker-output-v1.valid.json)

Schema IDs are stable compatibility identifiers. Published release manifests
bind the exact file content by source ref and digest; consumers MUST NOT fetch a
mutable default branch as a runtime dependency.
