# ADR-0006: Adopt the organization Developer Tooling Golden Path

- Status: Accepted
- Date: 2026-07-30

## Context

Organization repositories use multiple languages, artifact types, package
managers, task layouts, shared automation patterns, and Infrastructure as Code
engines. Repository inspection is useful for discovering actual constraints and
identifying practices worth retaining, but treating an existing repository as
the authority creates a distributed and unstable policy:

- workers copy repository-specific implementation instead of applying a
  category rule;
- central guidance drifts whenever a repository moves, changes, or disappears;
- local exceptions and historical compromises become accidental defaults; and
- migration status is confused with the target standard.

At the same time, a central document that ignores native ecosystem authority or
requires one identical implementation for every repository is too rigid.
Language managers, artifact risks, IaC state mutation, and externally released
software require different contracts.

The organization also intends to remain usable with private repositories on
GitHub Free. Paid branch, environment, reviewer, dependency-review, and private
attestation features cannot be universal prerequisites.

## Decision

We adopt a versioned organization Developer Tooling Golden Path.

1. The central standard owns normative cross-repository requirements,
   applicability, language and IaC profiles, stable rule IDs, schemas, runtime
   support, and exception semantics.
2. Repository code, native manifests and locks, toolchain selectors, root
   commands, and caller workflows remain the executable As-built authority.
3. Existing repositories inform investigation but are not named as reference
   implementations and do not redefine the target.
4. Applicable repositories expose a root Just façade with `init`, `check`, and
   `ci`; modular composition is used as complexity grows.
5. Toolchain ownership is explicit: mise owns Node.js, Go, Zig, and generic
   repository tools; uv owns Python; rustup owns Rust. Language-native package
   managers and lock or integrity records remain authoritative.
6. Shared implementation is materialized or consumed through immutable,
   integrity-verifiable releases. Templates, generators, checkers, and reusable
   automation implement the standard but do not become normative authority.
7. Conformance composes base, profile, artifact, and capability rules.
   Conditional controls apply only when their trigger is present.
8. MUST and MUST NOT violations fail when applicable and unwaived; SHOULD and
   SHOULD NOT findings warn; MAY choices do not create ceremonial work.
9. Exceptions are scoped, approved, owned, tracked, and expiring. Independent
   two-person approval and compensating controls are required only for
   classified high-risk deviations.
10. Structural conformance remains offline, deterministic, read-only, and
    separate from time-sensitive security, hosting-plan, deployment, and
    runtime evidence.
11. The normative standard uses Calendar Versioning. Schemas, asset bundles,
    checkers, and release artifacts retain separate compatibility versions and
    immutable release identities.
12. The baseline remains fully usable for GitHub Free private repositories.
    Paid features may strengthen outcomes but are neither the authority nor the
    only conforming implementation.
13. The central standard does not maintain repository migration schedules,
    current conformance status, or repository-specific rules. Each repository
    owns adoption and future migration work.
14. Shared implementation begins under one release, ownership, visibility, and
    trust boundary. It is split only when an independently governed owner,
    security boundary, release lifecycle, visibility, or failure domain
    emerges.

The normative requirements are maintained in the
[Developer Tooling Standard](../standards/developer-tooling/README.md).

## Consequences

### Positive

- Workers have one stable policy entry point independent of repository
  lifecycle and naming.
- Native ecosystem ownership and language differences remain explicit.
- Stable rule IDs and versioned schemas permit deterministic checkers,
  generators, upgrades, and exceptions without turning implementation into
  policy.
- Conditional applicability prevents release, supply-chain, platform, IaC, and
  development-container controls from becoming universal ceremony.
- Existing repositories can migrate incrementally without weakening the target
  or blocking standard publication.
- GitHub Free private repositories can satisfy outcomes through repository,
  Actions, cloud IAM, and durable external evidence.

### Negative

- The organization must maintain normative text, catalog, schemas, runtime
  lifecycle data, and implementation releases as separate but compatible
  surfaces.
- Existing repositories may temporarily diverge and require owned migration or
  exceptions.
- Some manual and external outcomes cannot be proven by the offline checker.
- Exact pins and immutable materialization create deliberate update work.
- Polyglot and released artifacts require more configuration than a
  single-language internal application.

## Alternatives considered

### Use one mature repository as the central reference

Rejected because repository-specific history, topology, and lifecycle would
become hidden policy. Workers would copy that repository, and its change or
removal would force central documentation synchronization.

### Put all shared implementation in the `.github` repository

Rejected because policy/discovery, executable shared implementation, and
repository-local execution have different release, visibility, permission, and
ownership needs. The implementation locator is an operational choice rather
than a normative identity.

### Standardize only command names

Rejected because identical command names can hide different runtime owners,
moving selectors, competing locks, mutable downloads, no-op validation, or
unsafe state mutation.

### Require every strongest control in every repository

Rejected because SBOM, provenance, complete platform matrices, two-person
approval, stateful IaC procedures, and Dev Containers have conditional
applicability. Universal requirements would create ceremony and false
conformance without proportional risk reduction.

### Delay the standard until all repositories are migrated

Rejected because migration needs a stable target. Repository adoption is
separate owned work and does not determine whether the organization has
accepted the target contract.

### Adopt a developer portal as the initial control plane

Backstage Software Templates remain a possible future discovery and creation
surface, but are deferred because the initial requirement is a small,
repository-independent policy and release contract rather than a portal,
service catalog, or plugin platform.

### Adopt another IaC abstraction as an organization default

SST, Alchemy, Nitric, and CDK for Terraform are not organization defaults.
AWS CDK remains the AWS authoring default; Terraform/OpenTofu and Pulumi retain
their explicit profiles. A future provider or engine change requires a separate
architecture and state-identity decision rather than an implicit Golden Path
tool substitution.

## Adoption status

This decision and the organization standard are As-built in the `.github`
governance repository. Shared implementation release `0.2.0` is consumed by an
immutable operational locator, and workflow-template discovery plus the
released bootstrap fixture are As-built in the policy repository. Each
participating repository still owns its metadata, commands, manifests, locks,
exceptions, migration, evidence, hosting adapters, and conformance status.
