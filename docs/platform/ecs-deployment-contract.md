# ECS deployment contract

- Status: Accepted
- Last updated: 2026-07-26
- Applies to: `5010-dev` services provisioned on the shared AWS ECS platform

This contract defines how the ECS Infrastructure repository, service
repositories, and deployment-time configuration cooperate without requiring
every application release to be preceded by an infrastructure deployment.

Health signal semantics and reusable service shapes are defined in the
[ECS health and readiness profiles](./ecs-health-readiness-profiles.md).

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this document are to be interpreted as described in BCP 14.

## Deployment model

The organization uses a hybrid deployment model:

- The ECS Infrastructure repository owns initial infrastructure bootstrap and
  structural platform changes.
- A service repository owns its application image release and may deploy it
  independently after the required infrastructure exists.
- Both deployment paths use the same environment-scoped deployment-state
  contract.
- Either path may run after bootstrap without requiring the other path to run
  immediately beforehand.

The model separates infrastructure structure from application release cadence;
it does not assign every task-definition revision exclusively to either
repository.

## Ownership boundary

| Concern                                                                                                                                                | Primary owner                 | Organization invariant                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Cluster, networking, security groups, IAM resources, ECS services, service discovery, volumes, sidecars, ALB configuration, and other structural state | ECS Infrastructure repository | Structural changes MUST be reproducible from Infrastructure-owned definitions.                                                      |
| Deployment-unit membership and structural inputs                                                                                                       | ECS Infrastructure repository | Accepted Infra desired state MUST be derived from version-controlled CDK source and documented Infra-owned structural inputs.       |
| Placeholder identity and bootstrap-compatible configuration                                                                                            | ECS Infrastructure repository | Every placeholder and bootstrap-compatible input state MUST be explicit in the Infra mapping.                                       |
| Application runtime and health semantics                                                                                                               | Service repository            | The service owns exact endpoints, commands, timing, readiness, and failure semantics.                                               |
| Application image build and publication                                                                                                                | Service repository            | Images MUST be immutable and traceable to source.                                                                                   |
| Application rollout and verification                                                                                                                   | Service repository            | A release MUST update the shared deployment state and provisioned ECS service according to repository policy.                       |
| Structural rollout                                                                                                                                     | ECS Infrastructure repository | A later Infrastructure deployment MUST preserve the current real image, runtime configuration, and service-owned liveness contract. |

## Accepted Infra desired state

Accepted Infra desired state, derived from version-controlled CDK source and
documented Infra-owned structural inputs, authorizes creation or recreation of
a deployment unit.

Structural inputs may be external to TypeScript source when Infrastructure
explicitly owns and documents them. Dynamic fleet membership is therefore
permitted, but its source, validation, and mapping remain Infrastructure
responsibilities.

Application image or runtime release values do not authorize their own
deployment unit. They are deployment state consumed after Infra desired-state
membership has been established and MUST NOT create a circular authorization
path.

## Shared deployment state

Environment-specific image and runtime values MUST use the parameter contract
documented by the owning repositories.

- Infrastructure and service deployment paths MUST read the same
  environment-scoped paths.
- A service release MUST publish its policy-compliant immutable image identity
  before or as part of updating ECS.
- A later Infrastructure deployment MUST consume the current image identity
  and MUST NOT restore a stale source-embedded image.
- A mutable tag such as `latest` MUST NOT establish real-image identity.
- Runtime values MUST NOT be independently duplicated across CDK source and
  service workflow definitions.
- Deployment workflows MUST NOT expose decrypted or sensitive values in logs,
  summaries, or artifacts.

This is deployment-time state. The contract does not require application
containers to query the parameter store directly at runtime.

## Repository-local deployment-unit mapping

A deployment unit is the smallest set of ECS resources and deployment inputs
that must be classified together. The Infrastructure repository MUST maintain a
canonical mapping for each unit that defines:

1. membership derived from CDK source and documented Infra-owned structural
   inputs;
2. required released image inputs;
3. required released runtime inputs;
4. optional runtime inputs;
5. bootstrap-compatible defaults or absence;
6. approved placeholder identity and configuration;
7. ECS service, task family, and application-container identity;
8. structural network, ALB, and service-discovery configuration; and
9. a link to the service-owned exact runtime health contract.

The service repository MUST maintain the exact liveness, readiness, semantic,
Docker image, and deployment-verification contract and link back to the Infra
mapping.

For a multi-input unit, configuration assembly MUST read and validate the
complete mapped input set before selecting a state. It MUST NOT independently
fall back individual members to placeholders.

## Current-state classification

Each deployment unit in accepted Infra desired state MUST be classified as
**Bootstrap**, **Released**, or **Invalid** before a task definition is
rendered. These are current-state classifications, not lifecycle-history
records.

### Bootstrap

Bootstrap applies only when:

- accepted Infra desired state includes the unit;
- every mapped required released image input is absent with an explicit
  `ParameterNotFound` result;
- required released runtime inputs are in the mapping's documented
  bootstrap-compatible absence or default state;
- optional inputs satisfy their mapped bootstrap policy;
- every current ECS service in the unit is absent or unambiguously uses its
  approved placeholder;
- the selected placeholder matches the Infra-owned mapping; and
- placeholder container health uses the bootstrap-only
  `CMD-SHELL exit 0` contract.

Current accepted Infra desired state is sufficient authority to create or
recreate the unit. No DynamoDB lifecycle ledger, historical Released record,
Protected GitHub Environment, workflow bootstrap input, or separate
authorization marker is an organization requirement.

If version-controlled CDK source and Infra-owned structural inputs continue to
select a deployment unit while all mapped application-release SSM inputs and
current ECS service state for that unit have been deleted, the unit may be
created again as Bootstrap. Deleting a structural input that removes the unit
from accepted Infra desired state does not authorize Bootstrap. Classification
MUST NOT count or branch on prior bootstrap or release events.

### Released

Released applies only when all mapped required released image and runtime inputs
are complete and valid. Optional inputs MUST satisfy their repository-local
policy. The term describes current complete real-image state and does not
preserve release history.

Released applies regardless of whether the ECS service currently exists. A
complete unit with no ECS service is a staged real-image state. Infrastructure
MUST create it directly with the real image, current runtime configuration, and
service-owned application liveness rather than fall back to a placeholder.

### Invalid

Invalid applies when the mapped current state is partial, contradictory,
inaccessible, malformed, disallowed, or ambiguous.

Each deployment unit MUST be classified from its own mapping. One unit's state
MUST NOT be used to reinterpret another unit, and an Invalid unit MUST NOT be
weakened to Bootstrap because a different unit is bootstrap-compatible.

This classification independence does not guarantee partial progress within a
single stack deployment. Whether a run stops entirely, preserves the Invalid
unit while applying safe changes elsewhere, or uses another reviewed strategy
is an Infrastructure implementation and operating-policy decision.

## Fail-closed rules

Configuration assembly MUST classify the affected unit as Invalid and stop its
mutation when:

- an SSM or AWS read fails with access denial, transport failure, throttling, or
  any error other than explicit `ParameterNotFound`;
- only part of the mapped required released input set exists;
- a required value is empty, malformed, mutable where immutability is required,
  or outside repository policy;
- members required to share an image resolve to inconsistent identities;
- a real application ECS service exists while any mapped required released
  input is missing;
- an existing ECS service cannot be identified unambiguously as the approved
  placeholder or real application; or
- the unit cannot be classified unambiguously from its mapping.

`ParameterNotFound`, empty output, and a generic command failure are distinct
results. Infrastructure lookup and configuration assembly MUST preserve that
distinction.

Bootstrap-compatible absence or defaults explicitly declared by the unit
mapping are not missing Released configuration. Any other partial required
state is Invalid.

## Health promotion and routing

### Placeholder container health

CDK MAY use an approved placeholder only for a unit classified as Bootstrap.
The organization bootstrap health command is `CMD-SHELL exit 0`.

This signal proves only that a placeholder task can participate in
infrastructure provisioning. It does not establish real-image liveness,
routing health, readiness, or semantic correctness.

### Real-image container health

The real-image revision MUST use the exact application liveness contract owned
by the service repository. Service and Infrastructure deployment paths MUST
render the same command and timing policy.

A later Infrastructure deployment MUST NOT replace real-image liveness with
`exit 0` or another bootstrap-only signal. Application readiness and semantic
evidence MAY be stricter but MUST remain separately named.

### Routing-health compatibility

If a placeholder is registered in a target group, placeholder and real image
MUST both implement the Infra-owned fixed routing-health endpoint. The path
SHOULD NOT change during image promotion.

A loose matcher such as `200-404` or an unconditionally successful routing
probe MUST NOT hide an unimplemented endpoint. A placeholder need not implement
the business API, but it MUST implement the registered routing-health contract.

Exact listener rules, target groups, ports, paths, matchers, and placeholder
configuration belong to the Infrastructure mapping.

## Independent subsequent deployments

After bootstrap, the following sequences MUST remain valid:

```text
Infrastructure deploy -> service deploy -> service deploy -> Infrastructure deploy
service deploy -> Infrastructure deploy -> service deploy
```

The required invariants are:

- A service deployment MUST NOT require an immediately preceding Infrastructure
  deployment.
- An Infrastructure deployment MUST NOT revert the latest valid shared image or
  operator runtime configuration.
- An Infrastructure deployment MUST NOT regress real-image liveness to
  bootstrap health.
- A service deployment MUST preserve or deliberately reapply Infrastructure
  structural settings outside service ownership.
- Structural changes MUST remain reproducible from Infrastructure-owned source
  and documented structural inputs.
- Both paths MUST leave shared state and ECS in a form the next path can consume
  safely.

For each Released unit, immutable image identity, required runtime
configuration, and application container liveness MUST remain non-regressing
across both sequences. Routing health, readiness, and semantic evidence remain
separate repository-owned contracts.

## Conformance

A deployment unit conforms only when:

1. the Infrastructure mapping defines membership, input classes, placeholder
   identity, ECS/ALB structure, and the runtime-owner link;
2. current-state classification distinguishes Bootstrap, Released, and Invalid
   without collapsing AWS errors into absence;
3. the service runtime contract defines exact liveness and any separate
   readiness or semantic evidence;
4. the real image contains the selected liveness mechanism;
5. service and Infrastructure deployment paths reproduce the same real-image
   health contract;
6. placeholder and real image satisfy the fixed routing-health contract where
   applicable;
7. both independent deployment sequences pass repository-owned verification;
   and
8. the owning repositories record current implementation status against their
   canonical documents.

Organization-document acceptance does not establish executable or production
conformance.

## Repository documentation requirements

### Service repository

Each service repository MUST document:

- exact liveness and readiness endpoints or commands, timing, and failure
  semantics;
- Docker image health behavior;
- rollout, readiness, and semantic verification;
- repository-local As-built, Target, Open, and conformance status;
- the selected organization exposure profile and runtime modifiers; and
- links to this contract and the canonical Infrastructure mapping.

### Infrastructure repository

The Infrastructure repository MUST document:

- deployment-unit membership and Infra-owned structural inputs;
- required released image and runtime inputs, optional inputs, and
  bootstrap-compatible defaults or absence;
- placeholder identity and configuration;
- ECS cluster, service, task-family, and application-container mappings;
- ALB, port, path, matcher, security-group, and network exposure;
- task-definition health rendering and classification implementation;
- repository-local As-built, Target, Open, and conformance status; and
- links to this contract and each service-owned runtime health contract.

The owning repositories MUST cross-link these documents. The
[service contract ownership directory](./ecs-service-health-matrix.md) is a
navigation aid only and does not duplicate exact values or implementation
status.

## When to change this organization contract

Update this repository when:

- the organization deployment model changes;
- Bootstrap, Released, or Invalid classification principles change;
- an exposure profile or reusable modifier is introduced or changed;
- organization-wide health, routing, evidence, or non-regression rules change;
- a cross-repository ownership boundary changes; or
- an exception affecting multiple repositories is accepted.

The following repository-local changes do not by themselves require an
organization-contract update:

- an endpoint path or health command changes;
- Docker health timing changes;
- workflow polling or task-definition rendering changes;
- a pull request merges or implementation status changes;
- service readiness or semantic policy changes; or
- an individual ALB port/path or parameter mapping changes.

Those changes belong in the owning service and Infrastructure documents.

## Organization-wide Open decisions

No organization-wide Open mechanism is currently recorded. Repository-local
implementation choices are not organization Open decisions unless they change
the invariants or ownership boundaries above.

## Related documents

- [ADR-0001: Adopt a hybrid ECS deployment model](../decisions/0001-adopt-hybrid-ecs-deployment-model.md)
- [ADR-0002: Adopt state-aware ECS health profiles (Superseded)](../decisions/0002-adopt-state-aware-ecs-health-profiles.md)
- [ADR-0003: Adopt current-state ECS bootstrap classification](../decisions/0003-adopt-current-state-ecs-bootstrap-classification.md)
- [ECS health and readiness profiles](./ecs-health-readiness-profiles.md)
- [Service contract ownership directory](./ecs-service-health-matrix.md)
