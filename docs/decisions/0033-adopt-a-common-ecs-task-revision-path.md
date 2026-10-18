# ADR-0033: Adopt a common ECS task revision path

- Status: Accepted
- Date: 2026-10-18
- Owners: `5010-dev/.github` maintainers, the ECS Infrastructure owner, and
  participating service repository maintainers
- Supersedes in part: ADR-0005 decisions 4 and 5
- Refines: ADR-0001 and ADR-0003

## Context

[ADR-0001](./0001-adopt-hybrid-ecs-deployment-model.md) let the Infrastructure
and service paths deploy independently through shared state, and accepted that
both could register task-definition revisions. It named AWS CDK as the
Infrastructure engine and left the generation strategy open.
[ADR-0005](./0005-adopt-ecs-service-delivery-workflow-envelope.md) then made
cloning the selected revision the default service strategy, with reassembly
permitted only through a repository exception.

Executable review of the current Infrastructure and service paths found that
two independent writers cannot provide stable no-op behavior. A clone keeps
drift and cannot add references that exist only in the Released shape, such as
real-only credentials. Image-centred fingerprints miss environment, secret, and
Service changes. Several paths rebuild structure in workflow code. Repeated
runs can roll unrelated services, and a later run can re-apply a candidate that
already failed. The planned move of the Infrastructure owner to a different IaC
engine also makes the CDK-specific wording inaccurate.

## Decision

1. Infrastructure-owned source, independent of the IaC engine, is the
   authority for unit membership, structure, and both the Bootstrap and the
   Released structural shapes.
2. Service and Infrastructure entry points remain independent but use one
   common revision path that synthesizes, registers, selects, and applies
   task-definition revisions. No other writer, including an IaC task-definition
   resource, registers or selects revisions for a unit on that path. The
   Infrastructure lifecycle owner still creates and owns the ECS service.
3. The path synthesizes the complete task definition from the applied
   structural spec and current shared inputs by the explicit field ownership of
   the unit mapping. A release always owns its slot's image; it owns the bound
   command, entry point, and liveness only where the mapping assigns behavior
   to it, and image-only slots keep Infrastructure-owned behavior. This
   replaces current-revision cloning as the default and removes the
   alternative-generation exception. Unknown ownership and unmodeled actual
   fields fail closed.
4. Infrastructure publishes a secret-free applied structural spec separately
   from pending structure. Image selection, operator values, secret values, and
   secret version identifiers are read at execution and not fixed in that spec.
5. Selection uses the service's actual revision, never the newest ACTIVE
   revision of a family. A complete semantic comparison makes an unchanged,
   stable unit a no-op, a Service-only change reuses the selected revision, a
   task change registers exactly one revision, and unrelated units keep their
   selected revision.
6. A known failed candidate blocks the Infrastructure entry point. The owner of
   the failed input may retry it once explicitly; a different valid candidate
   proceeds normally. Unreadable or ambiguous actual evidence blocks mutation as
   unknown and is never treated as absence; mapped input errors remain Invalid.
   No ledger or token is added.
7. After a mutation whose structural publication failed, the next
   Infrastructure run publishes the verified attempt without another rollout
   before evaluating newer source. Such a publication is a successful outcome
   without ECS mutation, not a rollout.
8. ECS late-bound Secrets Manager references select the current version by its
   native version identifier, observed from metadata without reading values.
9. Ownership transfer adopts actual structure unchanged; intended cleanup is a
   separate reviewed change, and competing writers do not run concurrently.
10. Bootstrap, Released, and Invalid remain current-state classifications.
    Run outcomes such as no-op, staged, structural spec published, blocked, and
    superseded are reported separately.

The normative requirements are maintained in the
[ECS deployment contract](../platform/ecs-deployment-contract.md#common-revision-path)
and the
[ECS service delivery workflow standard](../platform/ecs-service-delivery-workflow-standard.md#task-definition-synthesis).
Exact fields, service mappings, adapters, and evidence remain in the owning
repositories.

## Consequences

### Positive

- Repeated runs with unchanged inputs do not register or roll anything.
- Promotion from a placeholder can add Released-only structure without making
  real credentials a Bootstrap prerequisite.
- Removed environment, secret, and sidecar entries stay removed.
- A failed candidate is not repeatedly re-applied by unrelated runs.
- A secret version change rolls only its consumers and is observable without
  exposing values.

### Negative

- The Infrastructure owner must implement and operate a shared executor,
  structural spec publication, and typed field ownership before services
  conform.
- Services on the same runtime target wait for one another's serialized runs.
- Existing service workflows that clone or rebuild task definitions become
  As-built gaps until they migrate.
- An actual field outside the modeled set blocks a unit until its owner models
  it.

## Alternatives considered

### Keep current-revision cloning as the default

Rejected because cloning preserves drift and cannot add Released-only
references to a placeholder, and the two writers still compare different
facts.

### Let only service releases write revisions

Rejected because Infrastructure could not create a Released unit directly or
apply structural changes without a service release.

### Declare revisions as IaC task-definition resources

Rejected because the IaC writer would compete with service releases and could
send stale image or input state.

### Record failures in a ledger or approval token

Rejected because native ECS deployment evidence and the owning release path
are sufficient, and another control plane would need its own recovery.

## Adoption status

This decision accepts organization Target architecture. The common path,
structural spec publication, and service adapters are not implemented by this
change. Implementation, adoption, conformance, and production no-roll evidence
remain with the owning Infrastructure and service repositories. ADR-0001,
ADR-0003, and ADR-0005 keep their original text.
