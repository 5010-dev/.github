# Golden Path conformance

- Status: Accepted
- Standard version: `2026.08.4`
- Contract version: `golden-path/v1`

Conformance is evaluated from repository-local declarations and checked-in
files. There is no central repository inventory or live conformance registry.

## Inputs

| Input | Authority |
| --- | --- |
| `.github/golden-path.yaml` | Selected standard, asset bundle, profiles, artifact types, capabilities, and applicability |
| `.github/golden-path-native-roots.yaml` | Optional repository-owned override for actual native dependency roots when generated component paths are not the native authority |
| `.github/golden-path-exceptions.yaml` | Approved, scoped, expiring MUST-rule exceptions |
| `.github/golden-path-dependency-policy.yaml` | Optional repository-owned root binding, owner/release flow, gate, routine budget, and security fallback facts |
| `.github/golden-path-dependency-defers.yaml` | Optional repository-owned manual-review records; live report input, not offline policy state |
| `.github/release-units.json` | Existing repository-owned release-unit IDs referenced by dependency policy |
| Native manifests and locks | Actual toolchain, dependency, build, and package semantics |
| Bundled rule/runtime catalogs | Exact offline normative snapshot used by a checker release |

Manifest detection MAY suggest a profile and detect drift, but MUST NOT silently
activate or deactivate a profile. A declaration/native-file conflict is a
configuration failure.

The metadata schema is
[`golden-path-metadata/v1`](./schemas/golden-path-metadata-v1.schema.json).

The optional native-root schema is
[`golden-path-native-roots/v1`](./schemas/golden-path-native-roots-v1.schema.json).
When the file is absent, the checker retains component-scoped inference for
generated layouts and repository-root evaluation for legacy aggregate metadata.
When present, its roots replace those inference paths only for native-root
scoped rules. The checker MUST reject unknown profiles, aggregate mismatches,
duplicate root IDs, and overlapping roots that claim the same profile.
Artifact-type and capability applicability continues to come from generated
component or aggregate metadata, not from the native-root declaration.

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
- MUST receive an explicit UTC evaluation time for expiry and lifecycle checks
  and record that value in machine output;
- MUST serialize the machine-output `evaluatedAt` value in canonical UTC `Z`
  form rather than an equivalent numeric-offset representation;
- MUST validate schema and standard compatibility before rule evaluation;
- MUST sort findings by `ruleId`, repository-relative `path`, and
  `secondaryKey`, using an empty secondary key when none applies;
- MUST use repository-relative paths;
- MUST NOT emit secrets, credentials, personal absolute paths, or unnecessary
  source content;
- MUST NOT modify or push repository files; and
- MUST NOT reimplement format, lint, typecheck, test, or build behavior owned by
  `just ci`.

Dependency semantic evaluation validates native-root and release-unit
references, typed canonical-gate references, adapter ownership, routine budget,
and security fallback without running the referenced gate. Schema-invalid or
unresolvable references are configuration `error` with exit `2`; a valid
repository configuration that bypasses a MUST policy is `fail` with exit `1`.
Incomplete internal evaluation is exit `3`. SHOULD deviations warn with exit
`0`. Live queue age, staleness, current budget pressure, and route reachability
are outside the offline checker and remain report-only warnings.

`just check` includes structural conformance in an adopted repository.
`just conformance` MAY be provided as a diagnostic alias, but it is not an
additional universal base command.

An autofix is never implicit checker behavior. A future fixer MUST be a
separate explicit command with a non-mutating preview and reviewable output.

## Output

[`golden-path-checker-output/v1`](./schemas/golden-path-checker-output-v1.schema.json)
JSON is the complete canonical finding set. Human-readable text is a faithful,
bounded projection of the same status, counts, and actionable findings. The
default text output SHOULD omit individual passing and skipped findings; an
explicit diagnostic option MUST make the exhaustive finding list available.
SARIF is an optional derivative when code scanning is available.

Consumers MUST ignore data inside the schema-defined `extensions` objects that
they do not understand. New v1 data fields are added only through those
extension points; required fields or established meanings do not change within
v1.

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
| `1` | Unwaived MUST violation, including one whose otherwise valid exception has expired |
| `2` | Schema-invalid metadata/exception, unknown or non-waivable rule reference, unsupported version, or other configuration error |
| `3` | Internal checker error or incomplete evaluation |

Text and JSON MUST use the same exit meaning and status counts. Concision MUST
NOT hide failures, warnings, errors, waivers, or expired exceptions. A
report-only workflow preserves the actual finding and exit evidence even when
the workflow wrapper does not block progress.

The stable CI display name is `Developer Tooling / Conformance`. The
conformance workflow MUST run the checker only and MUST NOT prepare consumer
toolchains, run `just init`, or run `just ci`; those belong to repository-owned
quality CI. It SHOULD run independently so a quality failure does not suppress
structural evidence.

The workflow SHOULD emit annotations. Every conformance CI run MUST emit a
bounded job summary containing the standard and checker versions, selected
profiles, counts by finding status, a categorized skipped-count summary,
applicable exception expiry dates, and remediation for actionable findings.
The workflow MAY retain the complete JSON result as a short-lived artifact
according to repository evidence policy. Artifact retention is not universal
conformance evidence and MUST NOT be required when the bounded summary and
check result satisfy the repository's evidence needs.

A missing, skipped, cancelled, or otherwise unexecuted checker/workflow is not a
passing result. Any policy or platform gate MUST require positive evidence from
the expected check identity and source revision.

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

An optional organization custom property named
`developer_tooling_enforcement` MAY mirror `not-applicable`,
`report-only`, `policy-required`, or `platform-enforced` on plans that support
it. The property is never a profile/version/exception authority or a local
checker prerequisite.

When platform enforcement is available, a repository MUST NOT lower, rename, or
replace the required organization check through repository-local configuration.
The hosting adapter may strengthen enforcement but does not redefine rule
meaning.

## Rollout

1. Existing, newly bootstrapped, and explicitly adopted repositories begin
   with report-only measurement.
2. A separate accepted policy change MAY move a defined repository scope to
   policy-required conformance after rule and ownership readiness is proven.
3. A capable hosting plan MAY connect a policy-required stable check to
   platform enforcement.
4. Existing violations are resolved by a repository-owned migration or an
   approved exception.

Only rules with stable fixtures, acceptable false-positive rates, clear
remediation, and ready ownership move to policy-required. Repository adoption
and current results remain repository-local.

Rule IDs: `DT-META-*`, `DT-CONF-*`.
