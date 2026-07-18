# ECS deployment contract

- Status: Accepted
- Last updated: 2026-07-18
- Applies to: `5010-dev` services provisioned on the shared AWS ECS platform

This contract defines how the ECS CDK repository, service repositories, and AWS
Systems Manager Parameter Store cooperate without requiring every application
release to be preceded by an infrastructure deployment.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this document are to be interpreted as described in BCP 14.

## Deployment model

The organization uses a hybrid deployment model:

- The ECS CDK repository owns initial infrastructure bootstrap and structural
  platform changes.
- A service repository owns its application image release and may deploy it
  independently after the service has been bootstrapped.
- Both deployment paths use the same environment-scoped SSM parameters for
  image and runtime configuration state.
- Either path may run after bootstrap without requiring the other path to run
  immediately beforehand.

The model separates infrastructure structure from application release cadence;
it does not assign every task definition revision exclusively to either
repository.

## Responsibilities

| Concern | Primary responsibility | Contract |
| --- | --- | --- |
| Cluster, networking, security groups, IAM resources, ECS services, service discovery, volumes, and sidecars | ECS CDK repository | Structural changes MUST be expressed in CDK. |
| Initial ECS service and task definition | ECS CDK repository | CDK MUST be able to bootstrap the service before a real application image is running. |
| Application build and image publication | Service repository | Images MUST be immutable and traceable to their source revision. |
| Deployed application image | Service repository through SSM and ECS | A service release MUST update the environment's image parameter and the provisioned ECS service. |
| Runtime environment configuration | Environment-scoped SSM parameters | CDK and service deployment paths MUST consume the same parameter contract. |
| Application rollout and verification | Service repository | The workflow MUST register an appropriate task definition revision, update the service, and verify the rollout according to repository policy. |
| Structural rollout | ECS CDK repository | A later CDK deployment MUST consume current SSM image and runtime configuration state. |

## SSM configuration authority

Environment-specific application image URIs and runtime environment values MUST
be provided through the service's documented SSM parameter tree.

- CDK and service deployment workflows MUST read the same environment-scoped
  parameter paths.
- A service deployment that publishes a new image MUST write its immutable image
  URI to SSM before or as part of updating ECS.
- A later CDK deployment MUST read that image URI and MUST NOT roll the service
  back to a stale image embedded in source code or workflow YAML.
- Runtime values MUST NOT be independently duplicated in CDK source and service
  workflow YAML. Documented bootstrap defaults and construct-owned structural
  values are permitted when they cannot originate from operator configuration.
- Deployment workflows MUST NOT print decrypted or sensitive configuration
  values to logs.

SSM is the deployment-time configuration source. This contract does not require
application containers to query SSM directly at runtime. A deployment may read
SSM and materialize the resulting values into an ECS task definition.

## Bootstrap protocol

### Configuration staging

A service deployment MAY publish its image and configuration to SSM before the
ECS service exists. The repository MUST document whether this state is reported
as a successful SSM-only staging operation or as a deployment awaiting
infrastructure bootstrap.

### Dummy-first CDK deployment

CDK MAY create the initial ECS service with a dummy or placeholder image so the
platform can be provisioned before the real service image is available.

When a construct follows this dummy-first path, its initial container health
check MUST be bootstrap-safe. The organization uses `CMD-SHELL exit 0` so ECS
and CloudFormation can stabilize the initial service without depending on an
application endpoint that the dummy image does not implement.

This health check is intentional, but it has a deliberately narrow meaning:

- It proves only that the placeholder task can participate in infrastructure
  bootstrap.
- It MUST NOT be treated as evidence that the real application is ready,
  healthy, or serving its contract.
- Deployment verification MUST use additional service-appropriate evidence for
  a real application rollout.

### Real image deployment

After bootstrap, the service repository MUST be able to deploy a real image
without another CDK deployment. The deployment writes the image URI to SSM,
registers a task definition revision compatible with the existing service, and
updates the ECS service.

## Independent subsequent deployments

After bootstrap, the following sequences MUST remain valid:

```text
CDK deploy -> service deploy -> service deploy -> CDK deploy -> service deploy
service deploy -> CDK deploy -> service deploy
```

The required invariants are:

- A service deployment MUST NOT require an immediately preceding CDK deployment.
- A CDK deployment MUST NOT revert the latest SSM-backed image or operator
  runtime configuration.
- A service deployment MUST preserve or deliberately reapply the structural
  settings required by the currently accepted CDK architecture.
- A structural change MUST remain reproducible from the ECS CDK repository.
- Both paths MUST leave SSM and the deployed ECS service in a state that the
  next path can consume safely.

## Repository documentation

Each participating service repository MUST link to this contract and document:

- ECS cluster, service, task family, and application container mappings;
- image and runtime environment SSM parameter paths;
- automatic and manual deployment triggers;
- rollout, stability, and application health verification;
- pre-bootstrap behavior when the ECS service does not exist; and
- any approved exception to this contract.

Repository documentation MUST NOT duplicate this contract. Exceptions require
an explicit rationale and an architecture decision record or equivalent
cross-repository review.

## Open decisions

The following mechanisms remain open and MUST NOT be inferred from this
contract:

1. Whether a service deployment derives a new task definition from the current
   revision or reconstructs it from a controlled template.
2. Whether a service deployment only validates IAM trust relationships or may
   remediate them automatically.
3. Whether and when a real image deployment replaces the dummy-first `exit 0`
   container health check with an application-specific health check.
4. Whether a missing ECS service produces an SSM-only success or a failed
   deployment for each service category.

These decisions require comparison across affected services and infrastructure.
Once accepted, they must be recorded here and, when consequential, in a new or
superseding architecture decision record.

## Related decisions

- [ADR-0001: Adopt a hybrid ECS deployment model](../decisions/0001-adopt-hybrid-ecs-deployment-model.md)
