# Developer tooling schemas

These JSON Schemas are normative serialized-contract sources for standard
`2026.08.4`.

| Schema | Contract |
| --- | --- |
| [`golden-path-metadata/v1`](./golden-path-metadata-v1.schema.json) | Repository-local profile, artifact, capability, and version declaration |
| [`golden-path-native-roots/v1`](./golden-path-native-roots-v1.schema.json) | Optional repository-owned native dependency root declaration |
| [`golden-path-dependency-policy/v1`](./golden-path-dependency-policy-v1.schema.json) | Root binding, owner/release flow, typed gate, routine budget, and security fallback facts |
| [`golden-path-dependency-defers/v1`](./golden-path-dependency-defers-v1.schema.json) | Repository-owned major/pre-1.0/manual defer records |
| [`golden-path-dependency-observation/v1`](./golden-path-dependency-observation-v1.schema.json) | Digest-bound GitHub dependency queue observation |
| [`golden-path-dependency-candidate/v1`](./golden-path-dependency-candidate-v1.schema.json) | Deterministic non-mutating adoption preview |
| [`golden-path-dependency-report/v1`](./golden-path-dependency-report-v1.schema.json) | Derived organization dependency operations report |
| [`golden-path-exceptions/v1`](./golden-path-exceptions-v1.schema.json) | Scoped, approved, expiring MUST-rule waivers |
| [`golden-path-checker-output/v1`](./golden-path-checker-output-v1.schema.json) | Deterministic machine-readable checker result |
| [`golden-path-rule-catalog/v1`](./golden-path-rule-catalog-v1.schema.json) | Stable machine rule catalog |
| [`runtime-support/v1`](./runtime-support-v1.schema.json) | Versioned lifecycle/disposition catalog |

Schemas use JSON Schema Draft 2020-12. YAML repository inputs MUST deserialize
to the same data model before validation. YAML tags, duplicate keys, and
implementation-specific object types are not part of the contract.

Examples:

- [`golden-path-metadata/v1`](./examples/golden-path-metadata-v1.valid.json)
- [`golden-path-native-roots/v1`](./examples/golden-path-native-roots-v1.valid.json)
- [`golden-path-exceptions/v1`](./examples/golden-path-exceptions-v1.valid.json)
- [`golden-path-checker-output/v1`](./examples/golden-path-checker-output-v1.valid.json)

Schema IDs are stable compatibility identifiers. Published release manifests
bind the exact file content by source ref and digest; consumers MUST NOT fetch a
mutable default branch as a runtime dependency.

Schema `$id` values use repository-independent `urn:5010-dev:golden-path:...`
identifiers. Repository names and hosting paths are operational locators and do
not change serialized contract identity.
