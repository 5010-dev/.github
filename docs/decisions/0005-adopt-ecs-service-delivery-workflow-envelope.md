# ADR-0005: Adopt an ECS service delivery workflow envelope

- Status: Accepted
- Date: 2026-07-29

## Context

ADR-0001 adopted a hybrid ECS deployment model but deliberately did not select
a universal task-definition generation strategy. Service repositories
subsequently developed several valid service-specific shapes:

- inline and script-backed GitHub Actions workflows;
- one-service and fleet deployment units;
- placeholder-first and already-Released services;
- ALB, internal HTTP, background, zero-scale, singleton, and sidecar-bearing
  runtime profiles; and
- different readiness, diagnostics, rollback, and notification policies.

The variation is not itself a defect. However, executable workflow review found
that essential safety properties can also vary: ref and account guards,
immutable deployment identity, task-definition structural preservation,
named-container mutation, bootstrap health promotion, bounded verification, and
sensitive-value handling.

Mandating one reusable workflow now would hide service-specific policy behind a
large parameter surface. Leaving every implementation unconstrained would
continue to permit Infrastructure-owned structure or health semantics to drift
during an application release.

## Decision

We adopt an organization-wide ECS service delivery workflow envelope.

1. GitHub Actions owns event, permission, OIDC, concurrency, summary, and
   notification orchestration.
2. Non-trivial deployment behavior is locally executable and deterministically
   testable. `scripts/ci` is the default location, with documented equivalents
   permitted.
3. A release records source provenance and deploys an immutable registry digest.
4. The default task-definition strategy clones the revision selected by the
   intended service, targets release-owned containers by stable name, mutates
   only authorized fields, and preserves Infrastructure-owned structure.
5. An alternative task-definition generator requires structural-equivalence,
   named-container, preservation, and fail-closed evidence plus an accepted
   exception.
6. A real-image revision promotes the service-owned liveness contract and does
   not retain bootstrap-only `CMD-SHELL exit 0`.
7. Rollout, routing, readiness, and semantic evidence remain separate and are
   selected through the service's health profile and runtime modifiers.
8. OIDC identity, concurrency, execution, polling, diagnostics, cleanup, and
   sensitive-value non-exposure follow the common bounded envelope.
9. Trigger policy, fleet ordering, missing-service handling, readiness,
   rollback, and notification remain repository-owned variation.
10. Repository-local exceptions use a durable, reviewable record with
    compensating evidence and exit conditions.
11. We do not create a universal reusable workflow or central conformance
    registry as part of this decision. Reuse may be evaluated after the
    envelope has stable implementations in multiple repositories.
12. Organization documents retain only stable guidance, comparison dimensions,
    and ownership links. Exact implementation, current status, mutable evidence,
    and conformance remain canonical in the owning repository.

The normative requirements are maintained in the
[ECS service delivery workflow standard](../platform/ecs-service-delivery-workflow-standard.md).

## Consequences

### Positive

- Service workflow reviews use one safety and evidence vocabulary without
  erasing service-specific topology.
- Application releases preserve Infrastructure-owned task structure and
  sidecars by default.
- Image provenance, deployment digest, task revision, liveness, rollout,
  routing, readiness, and semantics remain distinguishable.
- Deployment logic can be exercised locally with deterministic transforms,
  fixtures, and fake AWS responses.
- Sensitive-value protection is explicit on the GitHub Actions surface without
  forcing a runtime secret-architecture migration.
- Follow-up repository work can report As-built gaps against a stable target
  instead of copying another service's workflow.

### Negative

- Existing workflows may require substantial follow-up refactoring before they
  conform.
- Repositories must maintain local scripts, tests, canonical deployment
  documentation, and exception records.
- Current task-definition cloning can preserve pre-existing drift; service and
  Infrastructure owners still need independent structural reconciliation.
- Shared-state and ECS mutations are not atomic, so repositories must document
  partial failures and retain recovery inputs.
- A common envelope does not remove the need for service-specific deployment
  review.

## Alternatives considered

### Require one reusable workflow immediately

Rejected because current services differ in fleet topology, build inputs,
health profiles, zero-scale behavior, readiness, and rollback. A universal
interface would either overfit one service or expose most implementation detail
as parameters before the organization envelope has stabilized in use.

### Permit any repository-local workflow without an organization envelope

Rejected because source identity, structural preservation, health promotion,
bounded verification, and sensitive-value handling are cross-repository safety
properties rather than optional style.

### Require complete task-definition reassembly from service-owned templates

Rejected as the default because service repositories can silently duplicate or
discard Infrastructure-owned roles, sidecars, volumes, logging, runtime
platform, and later structural additions. It remains available only with
equivalence evidence and an accepted exception.

### Require all application releases through CDK

Rejected because it reverses the hybrid deployment model and couples
application release cadence to Infrastructure deployment.

### Move ECS runtime secrets as part of workflow standardization

Rejected from this decision because GitHub Actions surface protection and ECS
runtime secret architecture have different owners, migration risks, and
verification requirements.

## Adoption status

The organization standard and this decision are As-built in the `.github`
repository. Each participating service repository owns its implementation,
evidence, exception, and conformance status. Organization acceptance does not
mark any existing service workflow conformant.
