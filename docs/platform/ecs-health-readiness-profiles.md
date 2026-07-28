# ECS health and readiness profiles

- Status: Accepted
- Last updated: 2026-07-29
- Applies to: `5010-dev` services provisioned on the shared AWS ECS platform

This contract defines a common vocabulary for selecting ECS container health,
routing health, rollout evidence, readiness, and operational evidence. It is
used with the [ECS deployment contract](./ecs-deployment-contract.md), not as a
replacement for service-owned health semantics.

The
[ECS service delivery workflow standard](./ecs-service-delivery-workflow-standard.md)
owns the minimum evidence required for a conforming service release. This
profile owns signal meaning and selection; it does not weaken a required
delivery gate.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this document are to be interpreted as described in BCP 14.

## State vocabulary

Owning repositories use these labels in their canonical documents:

- **As-built:** implemented in current executable code or workflow.
- **Target:** accepted behavior that is not yet fully implemented.
- **Open:** unresolved behavior that MUST NOT be inferred as accepted.

A statement MAY carry more than one label when current behavior, accepted target
behavior, and an unresolved mechanism differ. The organization repository does
not maintain a central implementation-status registry.

## Signal vocabulary

The following signals are independent. A deployment report MUST name the signal
it observed and MUST NOT collapse them into an unqualified "healthy" claim.

| Signal                                | What it can establish                                                                                 | What it cannot establish by itself                                               |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Bootstrap health                      | A placeholder task can run long enough for initial infrastructure provisioning                        | Real-image liveness, readiness, routing, or correctness                          |
| Container/process liveness            | The selected process boundary is alive and a task restart is a useful response to failure             | Dependency readiness, rollout convergence, or business correctness               |
| ECS task and rollout convergence      | The service selected the expected task definition and reached its desired running state               | ALB routing, application readiness, or semantic progress                         |
| ALB or Service Connect routing health | A registered endpoint is routable according to the configured routing probe                           | Background-role readiness, downstream dependency health, or business correctness |
| Application readiness                 | The application-specific prerequisites for accepting its intended work are currently satisfied        | Historical correctness, completeness, or sustained operational progress          |
| Semantic/operational correctness      | Service-specific state effects, freshness, backlog, ownership, or other business evidence meet policy | It does not replace liveness or structural rollout evidence                      |

CloudFormation completion, ECS `runningCount`, ECS container health, target-group
health, and application correctness are therefore separate observations.

## Container and routing-health boundaries

The bootstrap `CMD-SHELL exit 0` command is only placeholder container health.
It MUST NOT be copied into a real-image task definition.

For every accepted released-image liveness contract:

- service and CDK deployment paths MUST render the same container-health
  command and timing policy;
- a later deployment MUST NOT regress that command to bootstrap health; and
- application readiness or semantic correctness MUST remain separately named
  even when deployment verification observes them after liveness.

For every ALB-routed role:

- the target-group routing-health path SHOULD remain fixed across placeholder
  and real-image transitions;
- both images MUST return the configured success status on that endpoint;
- the matcher MUST express the intended success status and MUST NOT be widened
  to ranges such as `200-404` to accept an unimplemented endpoint; and
- an unconditionally successful routing probe MUST NOT substitute for a real
  routable endpoint.

A placeholder may implement only the registered routing-health endpoint. It is
not required to implement the real application's business API.

## Exposure profiles

Every ECS application role MUST select exactly one exposure profile.

### `alb-http-service`

An HTTP service receives application traffic from the shared ALB.

- The container liveness command SHOULD use a loopback process-liveness endpoint
  or an equivalent local command.
- The target-group health check MUST test a routable application endpoint.
- The container and target-group probes MAY use the same endpoint only when the
  endpoint semantics are correct for both restart and routing decisions.
- Dependency or domain readiness MUST remain a separate signal when its failure
  should not restart the task.

### `internal-http-service`

An HTTP service is normally reachable only through an internal network path or
service discovery contract. The `health-only-alb-route` modifier permits only
the narrow operational-health exception defined below.

- Container liveness SHOULD use a loopback endpoint or equivalent local command.
- Any deployment-time readiness probe MUST use an explicitly authorized access
  path.
- ECS Exec MAY be an explicitly approved repository-specific diagnostic, but it
  MUST NOT be an organization-wide prerequisite or routine required deployment
  gate.
- Service Connect membership alone MUST NOT be reported as routing or readiness
  evidence.

### `background-service`

The role performs background work and has no public application endpoint.

- Public subnets or public task IPs used for outbound exchange connectivity do
  not change this role into a public HTTP service.
- Container liveness SHOULD test the process supervisor or a loopback endpoint.
- Deployment verification MUST NOT create traffic exposure or scale a
  zero-capacity service merely to obtain a probe.
- Progress, ownership, registration, queue, and freshness checks belong to
  application readiness or semantic evidence.

### `alb-control-plane`

The ALB exposes an operator or query control plane rather than the background
engine's business-work readiness.

- At non-zero desired capacity, deployment verification MUST prove that the HTTP
  control plane is routable.
- Engine running state, operator activation, tokens, query availability, and
  business readiness MUST NOT be universal container-health requirements.
- A service MAY define stricter semantic gates after rollout, but it MUST name
  them separately from ALB and container health.

## Runtime modifiers

A service MAY select multiple modifiers. Modifiers refine rollout and evidence
rules; they do not replace the exposure profile.

| Modifier                  | Required interpretation                                                                                                                                                                                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `replicated-stateless`    | Rolling overlap is normally safe; every replacement task still needs the selected liveness and routing contract.                                                                                                                                                       |
| `singleton`               | Desired capacity is one for the mapped topology. The mapping MUST state whether overlap, stop-then-start, or fencing makes replacement safe.                                                                                                                           |
| `lease-fenced-singleton`  | Only the lease owner may perform active work. A replacement task can be live while legitimately standing by, so ownership readiness MUST NOT be ECS container liveness.                                                                                                |
| `elastic-to-zero`         | Desired count zero is a valid steady state. Verification MUST accept `0/0` and MUST NOT scale up only to probe.                                                                                                                                                        |
| `operator-controlled`     | The process may wait for an operator command. `running`, `is_ready`, or equivalent engine state MUST NOT be required for deployment success unless the repository explicitly defines a separate activation operation.                                                  |
| `multi-process-container` | The service MUST identify which supervisor or process boundary container liveness covers. Child-process and semantic checks that are not restart conditions remain separate.                                                                                           |
| `sidecar-bearing`         | Image replacement and health evidence MUST identify containers by stable name. Sidecar presence, essentiality, and health MUST NOT be inferred from array order or application-container health.                                                                       |
| `health-only-alb-route`   | The service remains an `internal-http-service`, while the shared ALB exposes only explicitly mapped operational-health endpoints. Business APIs, data endpoints, and metrics MUST remain unexposed. The target-group routing probe follows the fixed-path rules above. |

## Selecting a profile

Each service repository's canonical runtime contract MUST document:

1. one exposure profile and all applicable runtime modifiers;
2. the application process boundary and any relevant sidecars or supervised
   processes;
3. the exact released-image container liveness command, timing, and failure
   semantics;
4. application readiness and semantic/operational evidence;
5. overlap, singleton, fencing, operator-control, or zero-scale behavior;
6. repository-local As-built, Target, and Open status; and
7. a link to the Infrastructure mapping.

The Infrastructure mapping MUST document the bootstrap image and health,
task-definition health rendering, routing health, network exposure, and a link
back to the service runtime contract.

For a released image, the selected liveness check MUST contain only conditions
for which restarting the task is a useful recovery action. A transient external
dependency failure SHOULD NOT be promoted to a universal ECS restart condition.

An application readiness endpoint MAY be stricter than liveness. It MUST NOT be
used as ECS container health merely because it exists. The repository MUST
evaluate restart behavior, rollout overlap, and dependency failure semantics
first.

The owning repositories MUST state whether service and Infrastructure deployment
paths currently reproduce the selected command. A contract that is accepted but
not yet implemented is Target, not Open.

## Deployment evidence

A real-image deployment MUST record, without sensitive values:

- source revision and immutable image identity;
- SSM image parameter path and parameter version or observation time;
- task-definition revision and named application container;
- desired, running, and pending counts plus rollout state;
- container health and target-group health where applicable;
- the readiness or semantic observation required by repository policy; and
- any accepted zero-scale, standby, operator-controlled, or stop-then-start
  outcome.

Deployment logs MUST NOT print decrypted SSM values, bearer tokens, private
endpoint response bodies containing sensitive state, or complete task
environment maps.

## Ownership and discovery

Profile assignments and exact health contracts are maintained by the owning
service repositories. ECS, ALB, SSM, placeholder, and task-definition mappings
are maintained by the Infrastructure repository.

The
[service contract ownership directory](./ecs-service-health-matrix.md) links to
those mutable canonical locations. It is a navigation aid, not a canonical
profile, transition, or implementation-status registry. A service behavior
change does not require an organization-document update unless it changes this
taxonomy or another organization-wide invariant.

## Related decisions

- [ADR-0001: Adopt a hybrid ECS deployment model](../decisions/0001-adopt-hybrid-ecs-deployment-model.md)
- [ADR-0002: Adopt state-aware ECS health profiles (Superseded)](../decisions/0002-adopt-state-aware-ecs-health-profiles.md)
- [ADR-0003: Adopt current-state ECS bootstrap classification](../decisions/0003-adopt-current-state-ecs-bootstrap-classification.md)
- [ADR-0005: Adopt an ECS service delivery workflow envelope](../decisions/0005-adopt-ecs-service-delivery-workflow-envelope.md)
