# ADR-0001: Adopt a hybrid ECS deployment model

- Status: Accepted
- Date: 2026-07-18

## Context

The organization deploys multiple application repositories onto shared ECS
infrastructure provisioned by an AWS CDK repository. ECS services, networking,
IAM, service discovery, and other structural resources must exist before a real
application can run. Requiring a full CDK deployment for every application
release would unnecessarily couple infrastructure and service release cadence.

Allowing the CDK and service repositories to deploy independently without shared
state creates a different failure mode: a later CDK deployment can restore a
stale image or runtime configuration, while a service workflow can overwrite a
structural setting introduced by CDK.

The platform also uses a dummy-first bootstrap. CDK may initially create an ECS
service with a placeholder image, then the service repository deploys the real
image after the infrastructure is stable. The placeholder cannot be assumed to
implement the application's health endpoint.

## Decision

We adopt a hybrid ECS deployment model:

1. The ECS CDK repository bootstraps services and owns reproducible structural
   infrastructure changes.
2. Service repositories own application image publication and can update their
   provisioned ECS services without an immediately preceding CDK deployment.
3. Environment-scoped SSM parameters are the shared source for application image
   URIs and runtime environment configuration consumed by both paths.
4. A subsequent CDK deployment reads current SSM state so it does not roll back
   a service repository's latest release.
5. Dummy-first CDK constructs use a bootstrap-safe `CMD-SHELL exit 0` container
   health check when the placeholder image cannot satisfy a real application
   health contract. This signal stabilizes initial infrastructure only and is
   not application readiness evidence.

The operational requirements are maintained in the
[ECS deployment contract](../platform/ecs-deployment-contract.md).

## Consequences

### Positive

- Application releases do not need to wait for an unrelated CDK deployment.
- Infrastructure changes can still be deployed independently and reproducibly.
- SSM prevents a later infrastructure deployment from silently selecting a
  stale application image or runtime configuration.
- Dummy-first bootstrap avoids a circular dependency between a provisioned ECS
  service and an application image that has not yet been released.

### Negative

- Two deployment paths can register task definition revisions, so their mutable
  and structural fields require an explicit contract.
- Drift is possible when a workflow hardcodes values instead of consuming the
  shared SSM and CDK contracts.
- `exit 0` cannot provide application health evidence; real-image rollouts need
  separate verification.
- Cross-repository changes require coordinated documentation and validation.

## Alternatives considered

### CDK-only application deployment

Rejected because every application release would require an infrastructure
deployment and unnecessarily couple two release cadences.

### Service repositories own all ECS infrastructure

Rejected because networking, IAM, service discovery, and structural task
configuration would be duplicated across application repositories and cease to
be reproducible from the infrastructure repository.

### Independent paths without shared SSM state

Rejected because either path could overwrite the other's latest image or
runtime configuration.

## Out of scope

This decision does not select a universal task definition generation strategy,
IAM trust remediation policy, production container health-check promotion
policy, or missing-service result policy. Those mechanisms remain open in the
deployment contract until separately reviewed.
