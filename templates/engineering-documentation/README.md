# Engineering documentation templates

These templates implement the
[`5010-arc42-v1`](../../docs/standards/engineering-documentation/README.md)
organization profile.

## Template sets

- [`repository/`](./repository/) — base repository or independently governed
  engineering-layer documentation system.
- [`subsystem/`](./subsystem/README.md) — optional Compact, Standard, and Full L1
  architecture profiles.
- [`adr.md`](./adr.md) — consequential decision record.
- [`boundary-contract.md`](./boundary-contract.md) — stable semantics between
  independently governed systems.
- [`runbook.md`](./runbook.md) — production diagnosis and recovery procedure.
- [`validation-record.md`](./validation-record.md) — dated reproducible
  verification evidence.

The repository template contains the following scaffold tokens:

- `{{SYSTEM_NAME}}`
- `{{SCOPE}}`
- `{{PROFILE_ID}}`
- `{{DATE}}`

Use [`scripts/docs/scaffold-arc42.sh`](../../scripts/docs/scaffold-arc42.sh) to
render those tokens safely. The command refuses to overwrite existing files.

Templates are starting points, not normative copies. After generation, the
adopting repository owns the documents and may evolve them within the
organization contract. Repositories do not synchronize generated files
byte-for-byte with this directory.
