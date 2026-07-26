# ADR-0002: Adopt state-aware ECS health profiles

- Status: Superseded
- Date: 2026-07-25
- Superseded by:
  [ADR-0003](./0003-adopt-current-state-ecs-bootstrap-classification.md)

## Context

[ADR-0001](./0001-adopt-hybrid-ecs-deployment-model.md) established a
dummy-first hybrid deployment model. A CDK deployment may provision an ECS
service with a placeholder image and `CMD-SHELL exit 0`, after which the service
repository deploys a real image independently.

That bootstrap health check is valid only for a placeholder. The current CDK
constructs still emit `exit 0` when SSM already selects a real image. Several
service workflows install application-specific health checks, so the following
sequence can regress the health contract without changing the image:

```text
service deploy
-> real image + application liveness
-> subsequent CDK deploy
-> same real image + bootstrap-only exit 0
```

The platform also runs materially different service shapes: ALB-fronted HTTP
applications, internal HTTP services, background workers, operator control
planes, zero-scale workers, lease-fenced singletons, stop-then-start fleets, and
multi-process containers. Treating all of them as one generic "healthy" service
would confuse task restart, routing, readiness, and operational correctness.

SSM lookup failures are also ambiguous in the current infrastructure scripts.
The shared helper turns any AWS CLI failure into an empty value and may select a
placeholder. That behavior cannot safely distinguish a first bootstrap from
missing released state, access denial, transport failure, or an invalid partial
service group.

Current absence is not historical evidence. If both an ECS service and its SSM
image parameter were deleted after a release, their absence would look the same
as a first bootstrap unless a separate authorization or lifecycle record
distinguishes the two cases.

## Decision

We extend the hybrid deployment model with a state-aware health contract:

1. A deployment unit is in **Bootstrap** only when its complete real-image
   parameter set is explicitly `ParameterNotFound`, its ECS services are
   currently absent, explicit initial-bootstrap authorization is present, and
   its approved placeholder image and `CMD-SHELL exit 0` health check are
   selected together. Authorization is supplied through an explicit workflow
   input, durable lifecycle marker, or equivalent repository-approved
   mechanism.
2. A deployment unit is **Released** when its complete SSM image state
   identifies service-policy-compliant immutable real images. This selection
   applies even when a service workflow staged SSM before the ECS service
   exists.
3. A released image uses the service-selected application container liveness
   contract. Every later CDK deployment must reproduce that contract along with
   the current image and runtime configuration.
4. Missing authorization, lost or contradictory Released state, a partial
   deployment unit, inconsistent required shared-image digests, an invalid image
   URI, or any ambiguous state fails closed.
5. `ParameterNotFound` and current ECS service absence may contribute to
   classification but never authorize Bootstrap by themselves. Access denial,
   transport failure, and other AWS API errors are failures, not absence.
6. Every service selects one exposure profile and any applicable runtime
   modifiers from the organization
   [health profile contract](../platform/ecs-health-readiness-profiles.md).
7. Bootstrap health, container liveness, ECS rollout convergence, routing
   health, application readiness, and semantic/operational correctness remain
   separate named signals.
8. ECS Exec is not an organization-wide required deployment gate. A repository
   may use it through an explicitly authorized service-specific policy.

The normative state machine, fail-closed rules, and independent deployment
invariants are maintained in the
[ECS deployment contract](../platform/ecs-deployment-contract.md). Canonical
profile assignments and transition status are maintained in the
[ECS service profile and transition matrix](../platform/ecs-service-health-matrix.md).
Current executable As-built details remain owned by the linked repositories.

## Consequences

### Positive

- A later infrastructure deployment cannot silently weaken real-image
  liveness while retaining the same image.
- Placeholder health remains possible without requiring a placeholder to
  implement a real application endpoint.
- Deployment evidence can state exactly which signal was observed.
- Singleton, standby, zero-scale, operator-controlled, and multi-process
  services can keep their legitimate lifecycle semantics.
- SSM and AWS failures cannot be mistaken for permission to bootstrap.
- Deleted current state cannot silently authorize a second bootstrap for a
  previously Released unit.

### Negative

- Infrastructure configuration assembly must inspect SSM and current ECS state
  and validate a separate bootstrap authorization before selecting a profile.
- Infrastructure must choose and preserve an auditable authorization transport
  or lifecycle marker.
- CDK constructs need explicit released-image health inputs or a shared typed
  profile mapping.
- Multi-role and fleet deployments need completeness and image-consistency
  validation.
- Repository-specific readiness and operational evidence remain necessary;
  this decision does not create one universal probe.

## Alternatives considered

### Keep `exit 0` for every task revision

Rejected because real-image task health would prove nothing and a subsequent
CDK deployment could weaken a contract already installed by a service
deployment.

### Require the real endpoint during the first CDK bootstrap

Rejected because the approved placeholder does not implement the application
endpoint. It would recreate the circular dependency that dummy-first bootstrap
was introduced to avoid.

### Use readiness as container health for every service

Rejected because dependency outages, lease standby, operator-controlled stopped
state, and zero-scale roles are not universally repaired by restarting a task.

### Use ECS Exec as the common readiness mechanism

Rejected because private access, IAM, agent availability, and interactive
session behavior are service-specific concerns. It is useful for some
repository policies but is not a portable organization invariant.

### Treat all failed SSM reads as missing parameters

Rejected because it converts authorization, transport, and AWS service failures
into an unsafe placeholder fallback.

## Implementation status

The contracts and profile taxonomy are accepted Target architecture. Current
services are transitioning; their profile assignments, As-built evidence,
Target gaps, Open decisions, and conformance status are tracked in the service
matrix. No service may claim conformance before its bootstrap authorization,
released-image liveness, service workflow, CDK construct, and independent
deployment-sequence verification satisfy the contract as one unit.

Infrastructure changes that validate explicit bootstrap authorization,
classify state, fail closed, and render released-image health remain follow-up
work. Services whose exact liveness remains Open, including Quant and Obs, must
not receive an Infrastructure-invented probe merely to advance the transition.

## Relationship to ADR-0001

ADR-0001 remains historical and accepted. This ADR resolves its previously open
production health-promotion policy without rewriting the earlier decision.
