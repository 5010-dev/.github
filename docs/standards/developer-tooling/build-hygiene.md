# Dependency and build hygiene

- Status: Accepted
- Standard version: `2026.08.8`

This cross-cutting profile separates three applicability layers:

1. core dependency hygiene for every active buildable repository;
2. released-artifact supply-chain controls for packages, binaries, containers,
   and customer-delivered software; and
3. compatibility validation for platforms the repository actually claims to
   support.

A bot, scanner, cache backend, or SBOM generator is an implementation adapter,
not a separate policy authority.

## Core dependency hygiene

Every applicable repository:

- MUST maintain the native manifests and resolution/integrity records required
  by its selected profiles;
- MUST use locked or frozen dependency preparation in CI;
- MUST provide an automated known-vulnerability signal and an accountable
  remediation or exception path;
- MUST subject automated dependency changes to the same configured CI and
  review/merge policy as human changes;
- MUST make automation failures, suppressed findings, and long-unresolved
  security updates visible to an owner;
- MUST declare and validate at least one canonical production or release
  representative target; and
- MUST record dependency exceptions with affected rule/package/version or
  advisory, scope, reason, owner, approval, and expiry.

Risk, compensating controls, remediation tracking, and independent two-person
approval are additionally required only for security, release, or supply-chain
exceptions classified as high risk. A SHOULD deviation does not require an
exception.

Findings do not block every change merely because they exist. An approved
severity, exploitability, scope, and release-gate policy determines failure.

## Update automation

When a repository chooses an automated dependency adapter, Dependabot is the
GitHub-native default.

- Security alerts and security-update paths MUST be enabled where the ecosystem
  supports them.
- Active buildable repositories MUST track known vulnerabilities and
  unsupported dependencies and remediate them or record an approved risk
  exception.
- Dependency drift SHOULD be reviewed periodically. Each repository selects a
  cadence that fits its activity, release lifecycle, exposure, runtime
  criticality, test confidence, and owner capacity.
- Automated routine version-update pull requests MAY be used. When enabled,
  the repository MUST enumerate only actual native roots, use one automation
  owner for each dependency surface, select an explicit target branch and a
  bounded positive per-entry pull-request limit, and apply its normal CI and
  review/merge policy.
- Routine updates SHOULD be grouped when grouping reduces review load without
  hiding incompatible runtime, major, pre-1.0, base-image, IaC, or release
  effects. A repository MUST NOT combine the entire dependency graph merely to
  reduce pull-request count.
- Security updates MUST NOT be delayed behind a routine batch.
- When routine automation is enabled, GitHub Actions, base images, package
  ecosystems, and IaC dependencies SHOULD be included where supported and
  applicable.

There is no organization-wide routine cadence or numeric pull-request budget.
A repository MAY choose a security-only Dependabot configuration by setting
routine version-update limits to `0`; this does not require an expiry or exit
condition merely because routine automation is absent. Security visibility and
the remediation path remain required.

Renovate MAY replace Dependabot when a monorepo, advanced grouping, extracted
versions, or a dependency dashboard requires it and the repository records that
rationale. Both tools MUST NOT manage the same dependency surface.

A self-hosted Renovate lock refresh can execute repository-defined manager or
post-update behavior. It MUST use an explicit trusted-repository allowlist,
reviewed execution policy, minimum credentials, and an isolated runner before
unsafe execution is enabled.

An ecosystem not covered by the selected automated adapter MUST still have an
owned dependency-review and explicit update path that achieves the same
security and lifecycle outcomes.

## Automerge

Automerge is a conditional MAY for low-risk patch, digest, lock maintenance, or
bounded development-dependency updates when:

- applicable configured checks pass;
- configured review/merge policy is not bypassed;
- the update class is pre-approved;
- failure and rollback are clear; and
- production behavior and public compatibility are unlikely to change.

Major updates, runtime migrations, production-critical dependencies, public
compatibility changes, and changes requiring human release analysis retain
human review. A repository with inadequate tests MUST NOT automerge.

## Vulnerability review

Known-vulnerability alerting is a MUST. Reviewing dependency delta and newly
introduced known vulnerabilities is a SHOULD and becomes a conditional MUST for
a deployable or released artifact.

GitHub Dependency Review is an optional adapter only when the repository's plan
and ecosystem support it. A GitHub Free private repository MAY use native
lockfile diff, ecosystem audit, or an approved shared scanner. Paid capability
MUST NOT be a conformance requirement.

A newly introduced vulnerability over the approved threshold MUST be fixed or
covered by an approved exception before merge or release. Scheduled SCA or a
native full-graph audit is a SHOULD.

Source-controlled configuration review and time-sensitive advisory verdicts are
separate. A security service or approved audit provides current advisory
evidence; static configuration alone does not prove closure.

## License hygiene

- Dependency license inventory and reporting are a SHOULD.
- An approved license-policy check is a conditional MUST for public packages,
  customer-delivered software, redistributed binaries/containers, and
  contractually or legally regulated artifacts.
- No arbitrary allow/deny list becomes a universal gate without approved
  central policy.
- Unknown, custom, and dual licensing enters owner/legal review rather than
  automatic rejection.

## Cache contract

Cache use is optional. When a repository uses a CI cache, it:

- MUST exclude secrets, credentials, signing material, state, plans, and
  sensitive output;
- MUST prevent low-trust fork, `pull_request_target`, and issue-driven workflows
  from writing a trusted shared cache;
- MUST limit shared-cache writes to hardened trusted triggers;
- MUST key on relevant OS, architecture, toolchain/manager line, lock digest,
  and other result-affecting inputs;
- MUST remain rebuildable from native manifests and locks after a miss or
  eviction;
- MUST NOT treat cache content as a release artifact, provenance, test evidence,
  or dependency authority; and
- MUST separate reusable native stores from generated executable output.

Broad restore keys require an explicit stale/poisoning assessment. Exact keys
and trusted producers are stronger requirements when cached output will run.

## Released artifact supply chain

This layer applies to registry packages, executable binaries/CLIs,
customer-delivered or externally deployed containers/bundles,
contractually regulated artifacts, and canonical production packages,
binaries, or containers. It does not automatically apply to documentation,
source-only changes, templates, static image assets, or every test build.

### SBOM

- A compiled external, customer-delivered, or regulated release artifact MUST
  have an SBOM.
- An internal production container, binary, or package SHOULD have an SBOM
  until reusable generation, storage, and verification are mature enough for a
  future standard revision to strengthen the rule.
- An SBOM MUST describe components resolved in the final build and bind to the
  artifact digest; a source manifest snapshot is insufficient.
- SPDX or CycloneDX MUST be used.
- Secrets and unnecessary internal paths MUST NOT appear.

### Provenance

Build provenance is a SHOULD for an external or production release artifact.
It SHOULD connect artifact digest, source commit, builder/workflow identity, and
build evidence.

GitHub-native attestation is an optional adapter. A GitHub Free private
repository MAY use a signed manifest, immutable release metadata, or an
independent build record.

When a producer supplies a usable provenance record for required build,
bootstrap, deployment, or release consumption, the consumer MUST verify
signature, subject digest, builder identity, and source/workflow expectations.
A plan-compatible signed manifest or immutable build record satisfies the same
outcome when native attestation is unavailable. Creating an attestation without
verification does not establish trust.

## Supported execution platforms

A repository declares only the platforms it actually guarantees.

Repository metadata `targets` declares the supported OS, architecture, runtime
or target triple, support tier, and whether semantic execution is claimed.
`execution: true` means the artifact is actually run on a representative
runner, emulator, device, or production-equivalent environment; compilation
alone does not establish that claim.

- An internal service or IaC repository MAY begin with one primary
  OS/architecture lane equivalent to production or release.
- A public library, CLI, native extension, or cross-platform binary MUST test
  every platform combination it publicly supports.
- If both `amd64` and `arm64` artifacts are delivered, both MUST be validated.
- Preview runner images MUST NOT be the required compatibility baseline.
- A stability-sensitive release SHOULD use explicit stable runner images rather
  than assuming `*-latest` means the newest OS.

The complete OS × architecture × runtime × feature Cartesian product is not a
universal requirement. Primary support uses a policy-required lane; secondary
support may be required or scheduled according to risk and public claims.

## Containerized development

A Dev Container or equivalent environment is optional. If adopted:

- configuration MUST be repository-local and contain team-required behavior,
  not personal themes or preferences;
- images/features MUST use approved exact versions or digests;
- native manifests/locks, toolchain owners, and root Just commands remain the
  authority;
- local/CI parity uses the same commands, but CI need not run inside the
  development container;
- development and production images MUST remain separate;
- secrets MUST be injected, not committed into image or feature configuration;
- non-root and minimum capabilities SHOULD be the default;
- privileged mode, broad capabilities, host Docker sockets, credential mounts,
  and public forwarding require risk review or a time-bounded exception; and
- features, extensions, and post-create commands are reviewed as executable
  dependency code.

Absence of a Dev Container is not a violation.

## GitHub Free private baseline

Free-compatible controls such as Actions, OIDC, dependency graph, Dependabot,
and repository-local evidence are the baseline. Protected branches, rulesets,
required checks, Environments/reviewers, Dependency Review, and private
GitHub-native attestation MUST NOT be assumed.

A CI failure is policy evidence; it is `platform-enforced` only when the hosting
platform actually blocks the change.

Rule IDs: `DT-HYGIENE-*`, `DT-SUPPLY-*`, `DT-PLATFORM-*`.
