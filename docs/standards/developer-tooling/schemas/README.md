# Developer Tooling schemas

- Status: Accepted
- Standard version: `2026.08.7`

Only repository-owned facts that benefit from a stable source-controlled shape
remain machine-readable:

| Schema | Purpose |
| --- | --- |
| [`golden-path-native-roots/v1`](./golden-path-native-roots-v1.schema.json) | Stable native dependency root IDs, paths, and profiles |
| [`golden-path-exceptions/v1`](./golden-path-exceptions-v1.schema.json) | Bounded repository-local exceptions |
| [`runtime-support/v1`](./runtime-support-v1.schema.json) | Organization runtime-support catalog shape |

The runtime-support data is
[`rules/runtime-support.v1.json`](../rules/runtime-support.v1.json). Valid
native-root and exception examples are under [`examples/`](./examples/).

These are Draft 2020-12 JSON Schemas. A repository MAY validate an explicit JSON
or YAML document with an off-the-shelf validator. The organization provides no
active custom checker, generated metadata schema, checker output schema,
dependency compiler schema, or rule-catalog schema.

Schema compatibility is required only for a real released consumer or durable
state. Otherwise, correct the source and its consumers together before the
repository's release boundary.
