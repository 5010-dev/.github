# ECS deployment contract

- Status: Accepted
- Last updated: 2026-10-18
- Applies to: `5010-dev` services provisioned on the shared AWS ECS platform

This contract defines how the ECS Infrastructure repository, service
repositories, and deployment-time configuration cooperate without requiring
every application release to be preceded by an infrastructure deployment.

The contract is independent of the IaC engine. **Infrastructure-owned source**
means the version-controlled IaC source, such as AWS CDK or Pulumi programs,
and the documented structural inputs of the repository that owns a unit's ECS
structure. Exact engines, programs, stacks, paths, and fields remain in that
repository.

Health signal semantics and reusable service shapes are defined in the
[ECS health and readiness profiles](./ecs-health-readiness-profiles.md).
Service release workflow mechanics and conformance evidence are defined in the
[ECS service delivery workflow standard](./ecs-service-delivery-workflow-standard.md).

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this document are to be interpreted as described in BCP 14.

## Deployment model

The organization uses a hybrid deployment model:

- The ECS Infrastructure repository owns initial infrastructure bootstrap, ECS
  service lifecycle, and structural platform changes.
- A service repository owns its application image release and may release it
  independently after the required infrastructure exists.
- Both deployment paths use the same environment-scoped deployment-state
  contract and the same [common revision path](#common-revision-path) to
  register, select, and apply task-definition revisions.
- Either path may run after bootstrap without requiring the other path to run
  immediately beforehand.

The model separates infrastructure structure from application release cadence.
Neither entry point exclusively owns task-definition revisions; both delegate
them to one common path.

## Ownership boundary

| Concern | Primary owner | Organization invariant |
| --- | --- | --- |
| Cluster, networking, security groups, IAM resources, ECS services, service discovery, volumes, sidecars, ALB configuration, and other structural state | ECS Infrastructure repository | Structural changes MUST be reproducible from Infrastructure-owned source. |
| Deployment-unit membership and structural inputs | ECS Infrastructure repository | Accepted Infra desired state MUST be derived from Infrastructure-owned source. |
| Placeholder identity and bootstrap-compatible configuration | ECS Infrastructure repository | Every placeholder and bootstrap-compatible input state MUST be explicit in the Infra mapping. |
| Bootstrap and Released structural shapes | ECS Infrastructure repository | Both shapes, including Released-only references, MUST be defined explicitly; promotion MUST NOT depend on cloning the placeholder. |
| ECS service creation and lifetime | ECS Infrastructure repository | The Infrastructure lifecycle owner creates a service once with the revision selected by the common path. A service release MUST NOT create or recreate a service. |
| Task-definition registration, selection, and workload application | Common revision path | Both entry points MUST use the one path. No other writer, including an IaC task-definition resource, may register or select revisions for the unit. |
| Application runtime and health semantics | Service repository | The service owns exact endpoints, commands, timing, readiness, and failure semantics, bound to the released image's source. |
| Application image build and publication | Service repository | Images MUST be immutable and traceable to source. |
| Application rollout and verification | Service repository | A release MUST publish shared deployment state and request the common path according to repository policy. |
| Structural rollout | ECS Infrastructure repository | A later Infrastructure deployment MUST preserve the current real image, runtime configuration, and service-owned liveness contract. |

## Accepted Infra desired state

Accepted Infra desired state, derived from Infrastructure-owned source,
authorizes creation or recreation of a deployment unit.

Structural inputs may be external to IaC program source when Infrastructure
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
- Both paths MUST use the latest valid shared input observed at execution and
  resolve images to immutable digests. Latest does not mean a mutable tag, the
  newest ACTIVE revision of a task family, or an application repository HEAD.
- A service release MUST publish its policy-compliant immutable image identity
  before or as part of updating ECS.
- A later Infrastructure deployment MUST consume the current image identity
  and MUST NOT restore a stale source-embedded image.
- A mutable tag such as `latest` MUST NOT establish real-image identity.
- Runtime values MUST NOT be independently duplicated across Infrastructure
  source and service workflow definitions.
- A parameter version change whose validated, rendered value is unchanged is
  not a task input change.
- Deployment workflows MUST NOT expose decrypted or sensitive values in logs,
  summaries, or artifacts.

This is deployment-time state. The contract does not require application
containers to query the parameter store directly at runtime.

## Repository-local deployment-unit mapping

A deployment unit is the smallest set of ECS resources and deployment inputs
that must be classified together. The Infrastructure repository MUST maintain a
canonical mapping for each unit that defines:

1. membership derived from Infrastructure-owned source;
2. required released image inputs;
3. required released runtime inputs;
4. optional runtime inputs;
5. bootstrap-compatible defaults or absence;
6. approved placeholder identity and configuration;
7. ECS service, task family, and application-container identity;
8. structural network, ALB, and service-discovery configuration;
9. the Bootstrap and Released structural shapes and the owner of each field;
   and
10. a link to the service-owned exact runtime health contract.

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
records. They are distinct from the
[operation outcome](#classification-and-operation-outcomes) of a run.

### Bootstrap

Bootstrap applies only when:

- accepted Infra desired state includes the unit;
- every mapped required released image input is absent with an explicit
  `ParameterNotFound` result;
- required released runtime inputs are in the mapping's documented
  bootstrap-compatible absence or default state;
- optional inputs satisfy their mapped bootstrap policy;
- every current ECS service in the unit is observed absent or unambiguously
  uses its approved placeholder;
- the selected placeholder matches the Infra-owned mapping; and
- placeholder container health uses the bootstrap-only
  `CMD-SHELL exit 0` contract.

Current accepted Infra desired state is sufficient authority to create or
recreate the unit. No DynamoDB lifecycle ledger, historical Released record,
Protected GitHub Environment, workflow bootstrap input, or separate
authorization marker is an organization requirement. Bootstrap MUST NOT require
real-only credentials, real image behavior, or their secret versions.

If Infrastructure-owned source continues to select a deployment unit while all
mapped application-release SSM inputs and current ECS service state for that
unit have been deleted, the unit may be created again as Bootstrap. Deleting a
structural input that removes the unit from accepted Infra desired state does
not authorize Bootstrap. Classification MUST NOT count or branch on prior
bootstrap or release events.

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

Invalid applies when the mapped inputs are partial, contradictory, unreadable,
malformed, disallowed, or ambiguous, or when observed actual state contradicts
them.

Inability to obtain or identify required actual service, deployment, revision,
or structural spec evidence is not a fourth classification and is never
absence. The unit is blocked as unknown, and its mutation stops; see
[Fail-closed rules](#fail-closed-rules).

Each deployment unit MUST be classified from its own mapping. One unit's state
MUST NOT be used to reinterpret another unit, and an Invalid unit MUST NOT be
weakened to Bootstrap because a different unit is bootstrap-compatible.

This classification independence does not guarantee partial progress within a
single stack deployment. Whether a run stops entirely, preserves the Invalid
unit while applying safe changes elsewhere, or uses another reviewed strategy
is an Infrastructure implementation and operating-policy decision. A run that
stops MUST NOT omit an existing service from IaC desired state in a way that
deletes it.

## Fail-closed rules

Configuration assembly MUST classify the affected unit as Invalid and stop its
mutation when:

- a read of a mapped input, such as an SSM parameter, an image identity, or
  secret metadata, fails with access denial, transport failure, throttling, or
  any error other than explicit `ParameterNotFound`;
- only part of the mapped required released input set exists;
- a required value is empty, malformed, mutable where immutability is required,
  or outside repository policy;
- members required to share an image resolve to inconsistent identities;
- an observed real application ECS service exists while any mapped required
  released input is missing; or
- the unit cannot be classified unambiguously from its mapping.

The common revision path MUST instead report the unit as blocked as unknown and
perform no mutation when it cannot read or unambiguously identify required
actual evidence: the ECS service, whether it is the approved placeholder or the
real application, its current deployment and target revision, or the required
applied or pending structural spec. Unreadable actual state MUST NOT be treated
as absence, as Bootstrap, or as a no-op.

`ParameterNotFound`, empty output, and a generic command failure are distinct
results. Infrastructure lookup and configuration assembly MUST preserve that
distinction.

Bootstrap-compatible absence or defaults explicitly declared by the unit
mapping are not missing Released configuration. Any other partial required
state is Invalid.

## Common revision path

Service and Infrastructure entry points invoke one common path that observes
current state, synthesizes the complete task definition, decides, registers
when needed, and applies the selected revision. A runtime target is the set
of units that share one Infrastructure runtime state. The path runs in one
execution location for each runtime target; that location, its interfaces, and
its implementation are repository-owned.

### Field ownership and synthesis

- The path MUST synthesize the complete task definition from the applied
  structural shape for the unit's current state and the current shared inputs,
  using explicit field ownership declared by the unit mapping for each release
  slot. Infrastructure owns structure. A slot's release owns its immutable
  image. Only where the mapping assigns behavior to the release does it also
  own the command, entry point, and liveness bound to that image's release
  source. For an image-only slot, such as an auxiliary container image,
  Infrastructure retains its behavior, and the absence of release-owned
  behavior is not missing input. Infrastructure-published runtime bindings and
  operator inputs supply the remaining declared values.
- It MUST NOT blind-merge the selected revision. Environment entries, secret
  references, and sidecars removed from their owning source MUST NOT be
  restored from an earlier revision.
- Keyed collections such as environment, secrets, and tags are keyed by unique
  name; a duplicate is Invalid. Order-significant fields such as command and
  entry point preserve their order.
- Containers MUST be selected by stable name. Array position MUST NOT identify a
  container.
- Unknown field ownership, conflicting sources, incompatible port, platform, or
  health requirements, and any actual field outside the owner's modeled fields
  and verified defaults MUST stop the unit before registration.

### Applied structural spec and current release inputs

- Infrastructure publishes a secret-free applied structural spec for each unit
  only after that structure is prepared and verified. A pending structural spec
  MUST NOT be consumed by a service release.
- The applied spec records structure, source identity, resolved structural
  references, both state shapes, and the allowed runtime binding sources. It
  MUST NOT fix the image selection, operator values, secret values or their
  hashes, or secret version identifiers; both paths read those at execution.
- A service release verifies that the actual Infrastructure-owned structure
  matches the applied spec and never applies pending structure or Infrastructure
  HEAD. Differences in image, operator, binding, or secret-version inputs are
  ordinary desired changes, not structural mismatch.
- When the actual unit is Bootstrap and only the Released shape changes,
  Infrastructure publishes the new spec without registering or rolling the
  placeholder. A structural change to a Released unit is published only after
  its mutation is verified.

### Selection, comparison, and no-op

- The actual revision is the one selected by the service's current deployment.
  The path MUST NOT select the newest ACTIVE revision of a family; an unselected
  revision not proven to belong to the same attempt is ignored.
- Comparison MUST cover the complete registrable task payload, with
  server-computed fields removed and values normalized by field meaning, plus
  the Service settings related to the change. Absent and empty values remain
  distinct unless pinned SDK or provider evidence makes them equivalent. Image
  identity compares digests; a tag in the selected revision equals a digest
  only with evidence from the running task or active revision.
- When the actual service is stably converged and the synthesized task and
  related Service settings are equal, the result is a no-op: no registration,
  no service update, and no forced deployment. Parameter versions, run or
  source metadata, and keyed-collection order MUST NOT cause a rollout.
- Only units whose effective inputs changed are mutated. Units unrelated to a
  change, including those that do not consume a changed shared input, MUST
  retain their selected revision and deployment.
- A Service-only change applies without registering a revision. A coupled task
  and Service change uses one update with the exact new revision and the exact
  Service delta through one apply adapter. The entry points and the IaC provider
  MUST NOT issue competing workload updates or resend stale desired state.
- A run performs at most one rollout per unit. Transient API errors use bounded
  SDK retry. After a lost register or update response, the path observes actual
  state before any further mutation and does not assume exactly-once delivery.

### Initial service lifecycle

- A Bootstrap unit without a service registers the approved placeholder through
  the common path; the Infrastructure lifecycle owner creates the service with
  that exact revision.
- A Released unit without a service is registered with its real image and
  created directly; a placeholder stage MUST NOT be forced.
- A service release targeting an absent service MAY stage its image when the
  mapping allows it. Staging is not a service deployment.

### Failed, in-progress, and unknown deployments

| Observation | Infrastructure entry point | Owner of the change |
| --- | --- | --- |
| Stable, equal inputs | No-op | No-op unless another change is intended |
| Valid input change that is not the current failed candidate | One normal attempt | One normal attempt |
| Deployment in progress or rolling back, without failure evidence for the current attempt | Observe within the mapped bounded deadline without overlapping mutation; still unconverged without failure evidence is blocked as unknown, not a no-op | Observe and resolve first |
| Deployment without a circuit breaker whose current attempt is observed stalled and failed (bounded-stalled) | Treated as the current failed deployment; the next two rows apply | Treated as the current failed deployment |
| The current failed deployment's target equals the candidate | Blocked, non-zero; service and inputs preserved | One explicit retry through the common path after the same validation |
| Different valid candidate, such as a forward fix, a republished earlier release, or changed structure or secret version | One normal attempt | One normal attempt |
| Required actual service, deployment, revision, or structural spec evidence unreadable or ambiguous | Blocked as unknown; no mutation | No mutation until resolved |
| Mapped input read error, partial input, or policy violation | Invalid | Invalid; an explicit retry cannot bypass it |

- The failed target is the revision and Service configuration that the failed
  deployment attempted, not its rollback destination. Candidate equality uses
  the complete task payload, secret references, and related Service settings.
- A deployment without a circuit breaker is failed only when its current
  attempt has passed the mapped deadline and bounded native observation of that
  same attempt shows persistent start or health failure without progress.
  Elapsed time alone, or an earlier isolated task failure, is not failure; an
  ambiguous relation between the evidence and the current attempt is unknown.
- Republishing identical effective release bytes, or changing only source or
  run metadata, does not make a different candidate or an implicit retry. The
  candidate still equals the failed target and stays blocked until its owner
  explicitly retries it.
- Retry is requested by the owner of the failed input: the service path for
  release inputs and the Infrastructure path for structure. No approval token,
  failure ledger, or deny list is introduced, and the absence of a record is
  not retry permission.
- An equal selected revision does not make a failed, in-progress, or unknown
  deployment a no-op.
- Rollback republishes the previous image and its bound behavior as the current
  shared desired input through the normal path. It does not rewind operator
  inputs, structure, other units, secrets, or data. When ECS rolled back while a
  failed image remains the shared desired input, the result reports that
  desired is not current.

### Structural publication recovery

- When a mutation succeeds but structural publication fails, the result reports
  the actual change and the pending spec. A service release then blocks on the
  spec mismatch and MUST NOT revert to the earlier applied spec.
- A later Infrastructure run first verifies that actual matches the pending
  attempt's source, revision, payload, Service settings, and deployment, then
  publishes that spec without registering or forcing a deployment. Only then is
  any newer source evaluated as a new candidate.
- Newer source MUST NOT be published as the earlier pending spec. When actual
  matches neither the applied spec nor the pending attempt, the unit is blocked
  as unknown.

### Late-bound secret versions

- This applies to ECS late-bound secret references to Secrets Manager. Image
  and ordinary environment inputs keep their existing parameter contract, and a
  unit that renders values into its task definition keeps that rendering.
- The common resolver reads secret metadata, not values, and renders the
  service's reference with the native version identifier of the current
  version. References to several keys of one secret use one observed version.
- Secret values and their hashes MUST NOT appear in state, outputs, logs,
  artifacts, or task labels.
- A version identifier change is a task input change for the actual consumers
  only. The next run with unchanged inputs is a no-op.
- A metadata read error or ambiguous current version is Invalid and MUST NOT
  fall back to a placeholder.
- The guarantee is that a deployment injects the version it observed. It does
  not provide hot reload, a globally latest value, or continued credential
  validity. If the current version changes before convergence is verified, the
  result reports that desired is not current without starting another rollout.
- An adopted reference without version selection stays unchanged until a
  reviewed change scoped to its actual consumers converts it. A parameter-store
  reference with actual consumers moves to Secrets Manager only through a
  value-preserving change; the path never synchronizes values between stores.
- Credential rotation includes deployment of the actual consumers in the same
  operating procedure.

### Infrastructure ownership transfer

- When a unit moves to a different IaC engine, state, or repository, the first
  applied spec MUST represent the actual As-built structure and selected inputs.
  Import performs no ECS mutation and no reference or secret rewrite. A
  previously consumed secret version that cannot be proven remains unknown.
- Intended cleanup is a separate reviewed Infrastructure change or normal
  release scoped to its units. The first unrelated Infrastructure run MUST NOT
  apply it as drift.
- The previous writer is stopped before the common path is activated for the
  unit; competing writers MUST NOT run concurrently.

### Serialization

Runs of both entry points that can mutate the same runtime target MUST be
serialized in the repository that executes the common path, from shared-state
publication through ECS mutation and structural publication. An in-progress run
MUST NOT be cancelled by a newer run. A cancelled, rejected, or undelivered
request is reported as not applied or unknown, never success. A stale request
MUST NOT overwrite newer published intent. This serialization is mutual
exclusion among registered entry points, not distributed fencing.

## Classification and operation outcomes

A run reports the current-state classification and the operation outcome as
separate facts. Outcomes include no-op, applied and converged, structural spec
published without ECS mutation, staged image, blocked (known failure, unknown evidence, structural
mismatch, or stale input), superseded, and failed. Invalid classification
always stops the unit's mutation. Blocked, Invalid, superseded, and failed
results exit non-zero. Converged means ECS convergence and liveness for the
state; it is not application readiness. Exact outcome names, fields, and
evidence formats are repository-owned.

## Health promotion and routing

### Placeholder container health

Infrastructure MAY use an approved placeholder only for a unit classified as
Bootstrap. The organization bootstrap health command is `CMD-SHELL exit 0`.

This signal proves only that a placeholder task can participate in
infrastructure provisioning. It does not establish real-image liveness,
routing health, readiness, or semantic correctness.

### Real-image container health

The real-image revision MUST use the exact application liveness contract owned
by the service repository and bound to the selected image's release source.
Service and Infrastructure deployment paths MUST render the same command and
timing policy.

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
- Structural changes MUST remain reproducible from Infrastructure-owned source.
- Both paths MUST leave shared state and ECS in a form the next path can consume
  safely.
- A second run of either path with unchanged inputs on a stable service MUST be
  a no-op.

For each Released unit, immutable image identity, required runtime
configuration, and application container liveness MUST remain non-regressing
across both sequences. Routing health, readiness, and semantic evidence remain
separate repository-owned contracts.

## Conformance

A deployment unit conforms only when:

1. the Infrastructure mapping defines membership, input classes, placeholder
   identity, both structural shapes with field ownership, ECS/ALB structure,
   and the runtime-owner link;
2. current-state classification distinguishes Bootstrap, Released, and Invalid
   without collapsing input read errors or unknown actual state into absence;
3. both entry points use the common revision path, and no competing
   task-definition writer remains;
4. the service runtime contract defines exact liveness and any separate
   readiness or semantic evidence;
5. the real image contains the selected liveness mechanism;
6. service and Infrastructure deployment paths reproduce the same real-image
   health contract;
7. placeholder and real image satisfy the fixed routing-health contract where
   applicable;
8. both independent deployment sequences, the unchanged-input no-op, and
   preservation of unrelated units pass repository-owned verification;
9. the service release path satisfies the
   [ECS service delivery workflow standard](./ecs-service-delivery-workflow-standard.md);
   and
10. the owning repositories record current implementation status against their
    canonical documents.

Organization-document acceptance does not establish executable or production
conformance.

## Repository documentation requirements

### Service repository

Each service repository MUST document:

- exact liveness and readiness endpoints or commands, timing, and failure
  semantics;
- Docker image health behavior and how release behavior is bound to the image
  source;
- how its release requests the common revision path;
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
- both structural shapes, field ownership, and where the applied and pending
  structural specs are published;
- the common revision path's location, serialization, failure, recovery, and
  secret-version behavior;
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
- common revision path, failure, recovery, or secret-version invariants change;
- an exposure profile or reusable modifier is introduced or changed;
- organization-wide health, routing, evidence, or non-regression rules change;
- a cross-repository ownership boundary changes; or
- an exception affecting multiple repositories is accepted.

The following repository-local changes do not by themselves require an
organization-contract update:

- an endpoint path or health command changes;
- Docker health timing changes;
- workflow polling, task-definition rendering, or common-path implementation
  details change;
- a pull request merges or implementation status changes;
- service readiness or semantic policy changes; or
- an individual ALB port/path or parameter mapping changes.

Those changes belong in the owning service and Infrastructure documents.

## Organization-wide Open decisions

No organization-wide Open mechanism is currently recorded. Repository-local
implementation choices, such as the common path's executor, adapters, state
backend, and exact outcome fields, are not organization Open decisions unless
they change the invariants or ownership boundaries above.

## Related documents

- [ADR-0001: Adopt a hybrid ECS deployment model](../decisions/0001-adopt-hybrid-ecs-deployment-model.md)
- [ADR-0002: Adopt state-aware ECS health profiles (Superseded)](../decisions/0002-adopt-state-aware-ecs-health-profiles.md)
- [ADR-0003: Adopt current-state ECS bootstrap classification](../decisions/0003-adopt-current-state-ecs-bootstrap-classification.md)
- [ADR-0005: Adopt an ECS service delivery workflow envelope](../decisions/0005-adopt-ecs-service-delivery-workflow-envelope.md)
- [ADR-0033: Adopt a common ECS task revision path](../decisions/0033-adopt-a-common-ecs-task-revision-path.md)
- [ADR-0034: Adopt Pulumi for the integrated ECS Infrastructure repository](../decisions/0034-adopt-pulumi-for-the-integrated-ecs-infrastructure-repository.md)
- [ECS service delivery workflow standard](./ecs-service-delivery-workflow-standard.md)
- [ECS health and readiness profiles](./ecs-health-readiness-profiles.md)
- [Service contract ownership directory](./ecs-service-health-matrix.md)
