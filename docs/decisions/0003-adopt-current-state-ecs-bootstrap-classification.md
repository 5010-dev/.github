# ADR-0003: Adopt current-state ECS bootstrap classification

- Status: Accepted
- Date: 2026-07-26
- Supersedes:
  [ADR-0002](./0002-adopt-state-aware-ecs-health-profiles.md)

## Context

[ADR-0001](./0001-adopt-hybrid-ecs-deployment-model.md) established a
dummy-first hybrid ECS deployment model. Service repositories may release real
images independently, while the ECS CDK repository owns desired structural
state and can create services with approved placeholders before a real image is
available.

ADR-0002 added state-aware health profiles and correctly separated bootstrap
health, real-image liveness, rollout convergence, routing health, application
readiness, and semantic correctness. It also required a separate workflow
authorization or durable lifecycle record to distinguish an initial bootstrap
from recreation after current SSM and ECS state had been deleted.

That historical authorization requirement is not part of the accepted
deployment model. Accepted Infra desired state already defines which deployment
units should exist. It is synthesized from version-controlled CDK source and
documented Infra-owned structural inputs, which may include dynamic fleet
membership.

Requiring a second lifecycle ledger or authorization marker would create another
control plane and make recovery depend on preserved history. The classifier
instead must preserve the distinction between `ParameterNotFound`, other AWS
failures, partial required input, and contradictory ECS state.

The classifier instead needs to answer a current-state question for each
deployment unit: does accepted desired state plus current SSM and ECS state
select an approved placeholder, a complete immutable real image, or a
fail-closed invalid state?

## Decision

We adopt current-state, deployment-unit-scoped bootstrap classification:

1. Accepted Infra desired state, derived from version-controlled CDK source and
   documented Infra-owned structural inputs, is the authority to create or
   recreate a deployment unit. Application image and runtime release values do
   not authorize their own unit.
2. The Infra-owned unit mapping defines membership, required released image
   inputs, required released runtime inputs, optional inputs,
   bootstrap-compatible defaults or absence, and approved placeholder identity.
3. Classification uses that mapping together with current SSM and ECS state. It
   does not read, preserve, count, or infer prior bootstrap or release events.
4. **Bootstrap** applies when accepted Infra desired state includes the unit,
   every required released image input returns explicit `ParameterNotFound`,
   runtime and optional inputs satisfy their mapped bootstrap-compatible state,
   every current ECS service is absent or unambiguously uses its approved
   placeholder, and the placeholder is paired with `CMD-SHELL exit 0`.
5. **Released** describes current complete real-image state only. It applies
   when all mapped required released image and runtime inputs are valid,
   regardless of whether the ECS service currently exists. With no ECS service,
   the unit is staged and Infrastructure creates it directly with the real
   image and service-owned liveness contract.
6. **Invalid** applies to partial required input, required shared-image identity
   mismatch, malformed or disallowed values, real application services with
   missing required released state, ambiguous placeholder identity, or any
   SSM/AWS failure other than explicit `ParameterNotFound`. Invalid fails closed
   for the affected unit before mutation.
7. One unit's state does not change another unit's classification. Multi-input
   mappings define what must be assessed atomically. Whether one Invalid unit
   stops a whole stack run or can be safely preserved while other changes
   proceed remains an Infrastructure implementation and operating-policy
   decision.
8. No DynamoDB lifecycle ledger, historical Released record, Protected GitHub
   Environment, workflow authorization input, or separate bootstrap marker is
   required by the organization contract.
9. If version-controlled CDK source and Infra-owned structural inputs continue
   to select a deployment unit while all mapped application-release SSM inputs
   and current ECS service state for that unit have been deleted, the unit may
   be recreated as Bootstrap. Removing a structural input so the unit is no
   longer selected does not authorize Bootstrap. The classifier does not treat
   a second or later bootstrap differently.
10. The non-conflicting health decisions from ADR-0002 remain accepted:
    placeholder `exit 0` is bootstrap container health only; real images use the
    service-selected application liveness contract; both deployment paths
    reproduce it; routing, readiness, and semantic correctness remain separate;
    and ECS Exec is not an organization-wide required deployment gate.
11. A placeholder registered in an ALB target group must implement that target
    group's fixed routing-health endpoint. The transition must not rely on a
    loose `200-404` matcher or an unconditionally successful routing probe.

The normative classifier, fail-closed rules, and deployment-path invariants are
maintained in the
[ECS deployment contract](../platform/ecs-deployment-contract.md). Exact runtime
contracts and implementation status are maintained by the owning service and
Infrastructure repositories linked from the
[service contract ownership directory](../platform/ecs-service-health-matrix.md).

## Consequences

### Positive

- Disaster recovery and intentional recreation use the same accepted desired
  state as ordinary infrastructure deployment.
- A complete immutable real-image state cannot regress to a placeholder merely
  because its ECS service is absent.
- Missing parameters are distinguished from AWS access or transport failures.
- Partial and contradictory multi-input states fail closed without borrowing or
  contaminating another unit's classification.
- No additional historical lifecycle database or authorization transport must
  be operated and recovered.
- Placeholder routing and real-image liveness are explicit, independently
  testable contracts.

### Negative

- Infrastructure configuration assembly must inspect current ECS service and
  container image identity as well as typed SSM results.
- Approved placeholder identities, deployment-unit membership, and structural
  input ownership must be maintained explicitly.
- Multi-role and fleet deployments need complete-set and digest-consistency
  validation.
- Stack-level failure and partial-progress behavior remains an Infrastructure
  implementation and operating-policy responsibility.

## Alternatives considered

### Preserve a durable historical lifecycle ledger

Rejected because accepted desired state already authorizes the unit's existence.
A second ledger would make recreation depend on separately recovered history
and introduce a release control plane that the hybrid model does not require.

### Require a Protected GitHub Environment or workflow bootstrap input

Rejected as an organization invariant. Such controls may protect a repository
workflow for unrelated operational reasons, but they are not evidence needed by
the desired-state classifier.

### Treat any failed SSM read as absence

Rejected because access denial, throttling, transport failure, and other AWS
errors are not `ParameterNotFound` and must fail closed.

### Fall back to placeholders whenever an ECS service is absent

Rejected because complete immutable real-image SSM state is authoritative even
before the service exists. The next CDK deployment must create the real-image
service directly.

### Make deleted current state permanently non-bootstrapable

Rejected because it conflicts with reproducible desired-state recovery and
would require historical state solely to distinguish an otherwise identical
current configuration.

## Implementation status

This decision accepts organization Target architecture. Current implementation
and transition status are recorded only in the owning Infrastructure and service
repositories. The organization ownership directory links to those canonical
locations without copying exact state.

## Relationship to earlier decisions

ADR-0001 remains Accepted and unchanged.

This ADR supersedes ADR-0002's historical lifecycle and separate bootstrap
authorization conclusions. It carries forward ADR-0002's non-conflicting
health-profile, signal-separation, fail-closed AWS-error, and ECS Exec decisions
so the accepted Target remains complete without rewriting ADR-0002's historical
text.
