# Golden Path conformance

- Status: Accepted
- Standard version: `2026.07`
- Contract version: `golden-path/v1`

Conformance is evaluated from repository-local declarations and checked-in
files. There is no central repository inventory or live conformance registry.

## Inputs

| Input | Authority |
| --- | --- |
| `.github/golden-path.yaml` | Selected standard, asset bundle, profiles, artifact types, capabilities, and applicability |
| `.github/golden-path-exceptions.yaml` | Approved, scoped, expiring MUST-rule exceptions |
| Native manifests and locks | Actual toolchain, dependency, build, and package semantics |
| Bundled rule/runtime catalogs | Exact offline normative snapshot used by a checker release |

Manifest detection MAY suggest a profile and detect drift, but MUST NOT silently
activate or deactivate a profile. A declaration/native-file conflict is a
configuration failure.

The metadata schema is
[`golden-path-metadata/v1`](./schemas/golden-path-metadata-v1.schema.json).

## Rule semantics

Each machine-evaluable rule has an immutable stable ID, requirement level,
applicability, assertion or manual-check marker, severity, remediation, waiver
policy, and introduced standard version.

| Requirement | Unwaived result |
| --- | --- |
| MUST / MUST NOT | `fail` |
| SHOULD / SHOULD NOT | `warn` |
| MAY | `skip` or no finding |

A SHOULD deviation does not require an exception and does not fail solely
because the recommendation was not selected. A stronger conditional rule
requires explicit applicability and rationale.

Rule IDs are never reused with different meaning. Retired IDs remain reserved
and point to their replacement.

## Checker boundary

The shared checker:

- MUST be read-only, non-mutating, deterministic, and bounded;
- MUST evaluate from repository-local files and bundled immutable catalogs;
- MUST NOT require network, GitHub API, a central registry, user-global config,
  or the current clock for basic structural evaluation;
- MUST validate schema and standard compatibility before rule evaluation;
- MUST sort findings deterministically;
- MUST use repository-relative paths;
- MUST NOT emit secrets, credentials, personal absolute paths, or unnecessary
  source content;
- MUST NOT modify or push repository files; and
- MUST NOT reimplement format, lint, typecheck, test, or build behavior owned by
  `just ci`.

`just check` includes structural conformance in an adopted repository.
`just conformance` MAY be provided as a diagnostic alias, but it is not an
additional universal base command.

## Output

Text and
[`golden-path-checker-output/v1`](./schemas/golden-path-checker-output-v1.schema.json)
JSON are required and describe the same finding set. SARIF is an optional
derivative when code scanning is available.

Finding status is limited to:

- `pass`
- `fail`
- `warn`
- `skip`
- `waived`
- `error`

Exit codes are:

| Code | Meaning |
| --- | --- |
| `0` | Passes, warnings, skips, and valid waivers only |
| `1` | Unwaived MUST violation or expired/invalid exception |
| `2` | Metadata, exception, schema, or unsupported-version configuration error |
| `3` | Internal checker error or incomplete evaluation |

Text and JSON MUST use the same exit meaning. A report-only workflow preserves
the actual finding and exit evidence even when the workflow wrapper does not
block progress.

The stable CI display name is `Developer Tooling / Conformance`.

## Enforcement states

| State | Meaning |
| --- | --- |
| `report-only` | Findings and actual checker result are visible, but the workflow does not establish a merge policy |
| `policy-required` | Organization policy requires a passing checker; unwaived MUST violations return non-zero |
| `platform-enforced` | The hosting platform actually blocks merge on the stable check |

GitHub Free private repositories can run the same checker and CI but normally
cannot prove `platform-enforced` status through protected branches, rulesets, or
required checks. The standard MUST NOT describe a policy-required failure as
technical merge protection.

An optional organization custom property MAY mirror `not-applicable`,
`report-only`, `policy-required`, or `platform-enforced` on plans that support
it. The property is never a profile/version/exception authority or a local
checker prerequisite.

## Rollout

1. Existing repositories begin with report-only measurement.
2. New or explicitly adopted repositories use policy-required conformance.
3. A capable hosting plan MAY connect the stable check to platform enforcement.
4. Existing violations are resolved by a repository-owned migration or an
   approved exception.

Only rules with stable fixtures, acceptable false-positive rates, clear
remediation, and ready ownership move to policy-required. Repository adoption
and current results remain repository-local.

Rule IDs: `DT-META-*`, `DT-CONF-*`.
