# Dependency operations

- Status: Accepted
- Standard version: `2026.08.6`
- Contract version: `golden-path/v1`

This profile binds repository-owned dependency facts to organization risk
policy without making the organization tooling the owner of repository release
units, native dependency graphs, validation commands, or pull request approval.

## Authority boundaries

The following sources have separate authority:

1. This standard and the immutable policy bundle own requirement levels,
   default routine PR budget, risk classes, grouping constraints, and serialized
   contract meaning.
2. `.github/golden-path-native-roots.yaml` owns existing native root IDs and
   paths. Native manifests and locks remain the dependency-graph authority.
3. `.github/release-units.json` owns existing artifact, contract, and migration
   release-unit IDs and semantics.
4. `.github/golden-path-dependency-policy.yaml` owns root-to-release-unit
   references, validation-only invariant references, owner routes, release-flow
   references, canonical gate references, and explicit root overrides.
5. Repository workflows and `just ci` remain the executable validation
   authority. The compiler and central conformance MUST NOT rerun `just ci`.
6. A digest-bound live observation and repository-owned defer files are current
   operating evidence. They MUST NOT be copied into repository policy or treated
   as normative facts.

The repository policy uses
[`golden-path-dependency-policy/v1`](./schemas/golden-path-dependency-policy-v1.schema.json).
It MUST reference existing native-root and release-unit IDs and MUST NOT define a
second release-unit model, package-level mapping, dummy manifest, component-path
impact inference, CI command registry, or central approval queue.

## Root binding

A `classified` root binds its existing `nativeRootRef` to one or more existing
`affectedArtifacts[].releaseUnitRef`. A contract or migration that must be validated but is
not an artifact impact is listed separately in `validationOnly` with relationship
kind `contract` or `migration` and `invariantReleaseUnitRef`. The compiler MUST reject references not present
in the repository-owned files.

Owner and release flow have repository defaults and MAY be overridden at root
scope. The owner reference MUST identify a reachable team, CODEOWNERS surface,
GitHub user, or operational queue; a literal string alone is not proof that the
route is currently reachable.

Manifest and lock discovery MAY propose a root candidate. It MUST NOT infer
affected release units, validation invariants, owner, release flow, or gate. An
unbound or incomplete root is `pending-classification`; only that root's routine
automation lane stops. Other roots, product CI, security visibility, and
repository self-service continue.

## Canonical gate reference

The canonical gate is a typed reference:

```yaml
canonicalGate:
  command:
    kind: just-recipe
    workingDirectory: .
    recipe: ci
  ciEvidence:
    - kind: github-actions-job
      workflow: .github/workflows/ci.yml
      job: check
```

The command reference identifies repository-owned `just ci`. Optional
`ciEvidence` identifies the workflow/job that proves it ran. Conformance checks
the references and workflow linkage; it MUST NOT execute the command.

## Routine update policy

A classified native root has `maxOpenPullRequests: 3` by default. The
budget is a **MUST**, is expressed through the selected adapter's native
configuration, and excludes security updates and manual security remediation.
An override MUST be a positive integer and MUST record reason, owner, and
`reviewAfter`. Invalid schema/reference is configuration `error` with exit `2`;
a valid configuration that bypasses the compiled budget is an unwaived MUST
`fail` with exit `1`.

The budget is total per classified native root. A root MUST resolve to exactly
one adapter ecosystem so one budget cannot be multiplied across independently
limited adapter blocks. Disjoint ecosystem roots MAY share the same
repository-relative path, but they MUST use separate existing native-root IDs.
A root that resolves to more than one adapter ecosystem is a configuration
`error` with exit `2`; the compiler MUST NOT invent package-level mappings to
disambiguate it.

Routine changes MAY group only when ecosystem, native root, affected artifact
release-unit set, validation boundary, and risk class are identical. Major and
pre-1.0 minor changes are manual-review classes by default. Generated defers
MUST retain current and available version, reason, owner, observation time, last
review, and next review in
`.github/golden-path-dependency-defers.yaml` using
[`golden-path-dependency-defers/v1`](./schemas/golden-path-dependency-defers-v1.schema.json).

Dependabot is the default adapter. A repository MAY select Renovate only when
the locator-selected immutable tooling release explicitly implements the
Renovate adapter and the repository records why Dependabot cannot express its
required policy. Until such a release is selected, `adapter: renovate` is a
configuration `error` with exit `2` and MUST NOT be interpreted as Dependabot.
The same dependency surface MUST NOT be managed by both tools.

## Security route

Security updates are a separate lane and MUST NOT wait for routine grouping,
routine budget, or pending root classification. Security changes MAY group only
when ecosystem, root, affected release-unit set, validation boundary, and
urgency are identical and grouping introduces no delay.

Every repository declares a reachable security fallback owner and either a
canonical gate or an explicit manual-remediation route. A conditional hosting
adapter MAY retarget bot-created, same-repository security pull requests to the
integration branch when the repository has an explicit integration/release
flow. It MUST preserve security alerts, must not close or discard the security
change, and must not run for unrelated actors or fork heads.

### Security remediation closure

The completion unit for a dependency security remediation is every open
default-branch alert instance with the same repository, advisory identity, and
affected package ecosystem and name. A bot pull request, a direct manifest
edit, or one alert link is an input to that scope; it MUST NOT redefine the
scope. Before review, the digest-bound observation MUST enumerate the matching
alert numbers, manifest or lock paths when available, the source-provided
`direct`, `transitive`, or `unknown` relationship, and security pull-request
associations. An `unknown` relationship remains visible and MUST NOT be guessed;
it increases the repository-owned graph proof needed for closure but does not
invalidate or suppress the observation.

The observation projects the GitHub API `auto_dismissed` alert state as
`auto-dismissed`. It remains distinct from `fixed` and therefore cannot satisfy
post-promotion fixed verification.

For a security route with a `canonicalGate`, its typed `ciEvidence` MUST
identify the repository-owned conditional workflow job that proves the exact
integration head no longer resolves a vulnerable version through any native
dependency path in scope. The repository owns the ecosystem-native graph
command and result. Central conformance validates only that the declared
workflow and job exist; it MUST NOT parse every ecosystem lock, execute the
job, or rerun `just ci`. A manual-remediation route MUST retain equivalent
durable evidence and independent review.

The live observation MUST preserve each executed conditional proof as
`securityClosureEvidence` with its workflow path, stable job ID, run ID and URL,
exact head SHA, status, conclusion, and observation time. A proof counts toward
closure only when its workflow and job match the declared `ciEvidence`, its
head SHA equals the exact candidate head, and it completed successfully. This
source-bound evidence identity does not make the central tooling the job runner
or approval authority.

Any same-scope instance not covered by the candidate-head proof, or any
vulnerable native graph path that remains on that head, makes the remediation
`partial`. The fact that the default-branch alert is still `open` before
promotion does not by itself make a clean candidate partial; GitHub can mark
that alert `fixed` only after the corrected graph reaches the default branch. A
partial remediation MUST NOT be reported as security-complete or
promotion-ready even when ordinary CI is green. A deliberately retained
instance remains visibly partial and can proceed only under a scoped, expiring
high-risk exception with its owner, affected alert numbers, exit condition, and
independent approvals. Routine defer records do not authorize a security
residual.

This gate is conditional on the advisory being remediated. Unrelated
advisories, routine queue pressure, pending root classification, or a different
dependency MUST NOT block that remediation. Immediately before integration,
the repository MUST repeat the proof against the exact candidate head. After
promotion to `main`, the owner MUST verify that every expected alert number is
`fixed`; a green development check does not close a default-branch alert.

A repository publishes a consumer artifact only when its existing
repository-owned release-unit authority says the remediation changed that
artifact. Security closure MUST NOT manufacture package releases or a serial
follow-up release chain.

## Deterministic compiler and preview

The compiler combines only the immutable policy bundle and checked-in
repository facts. It produces deterministic adapter configuration, root
classification, owner/release routing, and queue intent. The adoption preview
is non-mutating by default and classifies every affected path as managed,
repository-owned, preserved, or conflicting. An explicit write mode MAY place a
candidate in a separate staging directory; it MUST NOT overwrite the repository.

Synthetic fixtures prove compiler semantics. Observations from named live pilot
repositories are operational evidence and MUST NOT be used as normative
fixtures.

## Live organization report

The live report is generated from a canonical GitHub observation using exact
query, API version, observation time, collection scope, source identity, and
SHA-256 digest, plus repository-owned defer files. The observation uses
[`golden-path-dependency-observation/v2`](./schemas/golden-path-dependency-observation-v2.schema.json)
and the derived report uses
[`golden-path-dependency-report/v2`](./schemas/golden-path-dependency-report-v2.schema.json).

Report v2 retains open alerts as deterministic groups keyed by repository,
advisory identity, package ecosystem, and package name, with each alert number,
severity, manifest path, source-provided direct, transitive, or unknown
relationship, fixed version, and linked security pull request when observed.
It also preserves source-bound `securityClosureEvidence` so a reviewer can
distinguish the declared closure job on the exact candidate head from an
aggregate green CI rollup. Its
`remediationCoverage` value is `none`, `partial`, or `all-linked` and describes
pull-request association only. `all-linked` does not prove native graph closure;
the repository-owned conditional gate remains authoritative. At repository
summary level, `openAdvisoryGroups` counts the open groups present in
`securityAdvisories`, while `partiallyLinkedAdvisoryGroups` counts groups whose
`remediationCoverage` is `partial`. Both are association-reporting counters and
MUST NOT be interpreted as native graph closure verdicts. The published
observation v1 and report v1 schemas remain immutable and are not rewritten.

Per-repository report artifacts are owned by repository maintainers and retained
for 90 days. Incident pre/post snapshots are also attached to the planning
record that owns the bounded remediation. Live staleness, budget pressure,
owner reachability, queue age, and security action time remain report-only
findings: they warn with exit `0` and do not make the offline checker depend on
GitHub or a central registry. The report MUST NOT become a global zero-alert
gate, central approval queue, cross-ecosystem dependency resolver, or substitute
for repository-owned native manifests, locks, and canonical CI.

Rule IDs: `DT-DEP-005` through `DT-DEP-012`.
