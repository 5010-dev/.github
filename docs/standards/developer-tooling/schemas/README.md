# Developer Tooling schemas

- Status: Accepted
- Standard version: `2026.08.7`

Only repository-owned facts that benefit from a stable source-controlled shape
remain machine-readable:

| Schema | Purpose |
| --- | --- |
| [`golden-path-native-roots/v1`](./golden-path-native-roots-v1.schema.json) | Stable native dependency root IDs, paths, and profiles |
| [`runtime-support/v1`](./runtime-support-v1.schema.json) | Organization runtime-support catalog shape |

The runtime-support data is
[`rules/runtime-support.v1.json`](../rules/runtime-support.v1.json). A valid
native-root example is under [`examples/`](./examples/).

These are Draft 2020-12 JSON Schemas. A repository MAY validate an explicit JSON
or YAML document with an off-the-shelf validator. Exceptions reference the
exact normative document and section in repository canonical documentation;
they do not depend on a retired machine rule catalog. The organization provides
no active custom checker, generated metadata schema, checker output schema,
dependency compiler schema, exception schema, or rule-catalog schema.

Schema compatibility is required only for a real released consumer or durable
state. Otherwise, correct the source and its consumers together before the
repository's release boundary.
