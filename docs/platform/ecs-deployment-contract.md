# ECS deployment contract

- Status: Accepted
- Conformance phase: Transitioning
- Last updated: 2026-07-25
- Applies to: `5010-dev` services provisioned on the shared AWS ECS platform

This contract defines how the ECS CDK repository, service repositories, and AWS
Systems Manager Parameter Store cooperate without requiring every application
release to be preceded by an infrastructure deployment.

Health signal semantics and service classification are defined in the
[ECS health and readiness profiles](./ecs-health-readiness-profiles.md).

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
| Structural rollout | ECS CDK repository | A later CDK deployment MUST consume current SSM image and runtime configuration state and reproduce the selected bootstrap or released-image health contract. |

## SSM configuration authority

Environment-specific application image URIs and runtime environment values MUST
be provided through the service's documented SSM parameter tree.

- CDK and service deployment workflows MUST read the same environment-scoped
  parameter paths.
- A service deployment that publishes a new image MUST write its immutable image
  URI to SSM before or as part of updating ECS.
- A later CDK deployment MUST read that image URI and MUST NOT roll the service
  back to a stale image embedded in source code or workflow YAML.
- Image selection MUST distinguish an approved placeholder from a
  service-policy-compliant immutable real image. A mutable tag such as `latest`
  MUST NOT establish released-image identity.
- Runtime values MUST NOT be independently duplicated in CDK source and service
  workflow YAML. Documented bootstrap defaults and construct-owned structural
  values are permitted when they cannot originate from operator configuration.
- Deployment workflows MUST NOT print decrypted or sensitive configuration
  values to logs.

SSM is the deployment-time configuration source. This contract does not require
application containers to query SSM directly at runtime. A deployment may read
SSM and materialize the resulting values into an ECS task definition.

### Deployment units

A deployment unit is the smallest set of ECS services and image parameters that
must be classified together. A repository-specific mapping MUST identify the
unit and any roles that are required to use the same image digest.

- An individual API, Academy Dashboard, or Calculator service is one unit.
- Collector master, realtime, and worker are one shared-image unit.
- Quant and Obs fleet mappings MUST state whether consistency is per bot or
  across the enabled fleet for a release.

For a multi-parameter unit, configuration assembly MUST read and validate the
complete parameter set before selecting a state. It MUST NOT independently
fallback individual roles to placeholders.

## Bootstrap protocol

### State classification

Each deployment unit MUST be classified as **Bootstrap** or
**Released** before a task definition is rendered.

**Bootstrap** is permitted only when all of the following are true:

- every real-image parameter in the deployment unit is absent with an explicit
  `ParameterNotFound` result;
- every ECS service in the deployment unit is currently absent;
- the deployment carries explicit authorization to perform the initial
  bootstrap for that environment and deployment unit;
- the selected image is an organization-approved placeholder for that role; and
- the container health check is `CMD-SHELL exit 0`.

`ParameterNotFound` plus current ECS service absence does not prove that the
unit has no release history and MUST NOT authorize Bootstrap by itself. The
authorization MUST be supplied by an explicit workflow input, durable lifecycle
marker, or equivalent repository-approved mechanism. Its exact transport is an
Infrastructure implementation decision, but explicit, auditable bootstrap
intent is an organization invariant.

An empty string, an unapproved image, a generic AWS CLI failure, or an absent
authorization MUST NOT be treated as evidence of Bootstrap. Loss or deletion of
state for a previously Released unit MUST NOT be interpreted as permission to
bootstrap again.

**Released** applies when the complete image parameter set contains
service-policy-compliant immutable real-image URIs. This classification applies
even if a service repository staged SSM before its ECS service exists. A
Released CDK deployment MUST use the real image, current runtime
configuration, and the repository-mapped application container liveness
contract.

Once a deployment unit has been Released, a later missing image parameter or
service MUST fail closed unless a separately accepted lifecycle operation
defines the transition. The deployment MUST NOT infer a return to Bootstrap
from current absence.

### Fail-closed classification

Configuration assembly MUST stop before synthesis or service update when any of
the following is true:

- an image parameter is missing for an already provisioned service;
- real-image parameters and ECS services are absent but explicit initial
  bootstrap authorization is missing, invalid, stale, or ambiguous;
- an SSM read fails with access denial, transport failure, throttling, or any
  AWS API error other than explicit `ParameterNotFound`;
- an image URI is empty, malformed, mutable where immutability is required, or
  outside the repository's allowed registry/image policy;
- only part of a deployment unit's required image parameter set exists;
- roles required to share an image resolve to different digests;
- required released runtime configuration is absent or partial; or
- known Released lifecycle state has been lost or contradicts current
  resources; or
- the deployment unit cannot be classified unambiguously.

The current infrastructure `fetch_ssm_parameter` helper converts every failed
AWS read to an empty value. That is **As-built technical debt**, not an allowed
Bootstrap classifier. Infrastructure MUST replace it with error-aware state
classification before claiming conformance to this section.

### Configuration staging

A service deployment MAY publish its image and configuration to SSM before the
ECS service exists. The repository MUST document whether this state is reported
as a successful SSM-only staging operation or as a deployment awaiting
infrastructure bootstrap.

Staging a complete real-image unit selects Released state for the next CDK
deployment. It does not authorize a placeholder fallback.

### Dummy-first CDK deployment

CDK MAY create the initial ECS service with a dummy or placeholder image only
for a deployment unit classified as Bootstrap.

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

The real-image revision MUST use the application container liveness contract
selected by the service's
[health profile](./ecs-health-readiness-profiles.md). Application readiness and
semantic evidence MAY be stricter, but MUST remain separately named signals.

The service deployment MAY derive a revision from the current task definition
or render one from a controlled template. In either case it MUST preserve
structural fields it does not own, target application and sidecar containers by
stable name, and apply the released-image liveness contract deliberately.

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
- A CDK deployment MUST NOT replace a released-image liveness contract with
  `CMD-SHELL exit 0` or any other bootstrap-only signal.
- A service deployment MUST preserve or deliberately reapply the structural
  settings required by the currently accepted CDK architecture.
- A structural change MUST remain reproducible from the ECS CDK repository.
- Both paths MUST leave SSM and the deployed ECS service in a state that the
  next path can consume safely.

For each released deployment unit, the following values MUST remain
non-regressing across both sequences:

1. immutable image identity;
2. operator runtime configuration plus construct-owned structural
   configuration; and
3. application container liveness.

Routing health, application readiness, and semantic evidence MUST also continue
to follow the repository mapping, but they are not interchangeable with those
three revision inputs.

## Conformance and transition

ADR-0002 accepts the Target architecture in this contract. It does not assert
that every current service or workflow already conforms.

- Current implementation gaps MUST be recorded in the
  [service matrix](./ecs-service-health-matrix.md) as As-built, Target, or Open.
- Recording an existing workflow as As-built is distinct from claiming
  conformance. A deployment unit whose Target is not implemented MUST NOT be
  described as conformant to this contract.
- A new service, or a material change to an existing health or deployment path,
  MUST follow this contract when introduced.
- Existing services MAY move incrementally through tracked transition items.
  Documentation-only acceptance before executable implementation is permitted,
  but it does not establish production conformance.
- Infrastructure MUST NOT invent a released-image probe for a service whose
  exact liveness contract remains Open.
- Bootstrap/Released classification, the service workflow, and the CDK
  construct MUST transition as one consistent deployment unit.

A service transition is complete only after all of the following are true:

1. its exact released-image liveness contract is accepted;
2. the real image contains the selected command or endpoint;
3. service and CDK deployment paths reproduce the same health contract;
4. both independent deployment sequences pass repository-owned verification;
   and
5. the matrix records the result as conformant As-built against current
   repository authority.

## Repository documentation

Each participating service repository MUST link to this contract and document:

- ECS cluster, service, task family, and application container mappings;
- image and runtime environment SSM parameter paths;
- automatic and manual deployment triggers;
- rollout, stability, and application health verification;
- exposure profile, runtime modifiers, container liveness, routing health,
  readiness, and semantic/operational evidence;
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
3. Whether a missing ECS service produces an SSM-only success or a failed
   deployment for each service category.
4. Which authorized private access mechanism, if any, each internal service uses
   for a deployment-time readiness probe.
5. Exact application container liveness commands for services whose matrix
   entry remains Open.
6. The exact Infrastructure mechanism that transports and durably preserves
   explicit initial-bootstrap authorization.

These decisions require comparison across affected services and infrastructure.
Once accepted, they must be recorded here and, when consequential, in a new or
superseding architecture decision record.

## Related decisions

- [ADR-0001: Adopt a hybrid ECS deployment model](../decisions/0001-adopt-hybrid-ecs-deployment-model.md)
- [ADR-0002: Adopt state-aware ECS health profiles](../decisions/0002-adopt-state-aware-ecs-health-profiles.md)
- [ECS service profile and transition matrix](./ecs-service-health-matrix.md)
