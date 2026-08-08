# Dependency operations

- Status: Accepted
- Standard version: `2026.08.4`
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

Routine changes MAY group only when ecosystem, native root, affected artifact
release-unit set, validation boundary, and risk class are identical. Major and
pre-1.0 minor changes are manual-review classes by default. Generated defers
MUST retain current and available version, reason, owner, observation time, last
review, and next review in
`.github/golden-path-dependency-defers.yaml` using
[`golden-path-dependency-defers/v1`](./schemas/golden-path-dependency-defers-v1.schema.json).

Dependabot is the default adapter. Renovate MAY be selected only where a
repository records why Dependabot cannot express its required policy. The same
dependency surface MUST NOT be managed by both tools.

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
[`golden-path-dependency-observation/v1`](./schemas/golden-path-dependency-observation-v1.schema.json)
and the derived report uses
[`golden-path-dependency-report/v1`](./schemas/golden-path-dependency-report-v1.schema.json).

Per-repository report artifacts are owned by repository maintainers and retained
for 90 days. Incident pre/post snapshots are also attached to the planning
record that owns the bounded remediation. Live staleness, budget pressure,
owner reachability, queue age, and security action time remain report-only
findings: they warn with exit `0` and do not make the offline checker depend on
GitHub or a central registry.

Rule IDs: `DT-DEP-005` through `DT-DEP-011`.
