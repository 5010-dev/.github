# Engineering documentation

This directory contains canonical engineering contracts and cross-repository
architecture decisions for the `5010-dev` organization.

## Authority

- Organization contracts own default cross-repository invariants and reusable
  exposure-profile and runtime-modifier definitions.
- Architecture decision records preserve why consequential cross-repository
  decisions were accepted.
- Repository code, workflow definitions, infrastructure definitions, and
  configuration remain authoritative for current executable As-built behavior.
- Canonical service documentation owns exact runtime health semantics,
  deployment workflow, verification, and repository-local As-built, Target, and
  Open status.
- Canonical Infrastructure documentation owns deployment-unit membership,
  structural inputs, ECS/ALB/SSM mappings, placeholder configuration,
  classification implementation, and repository-local status.
- The organization ownership directory is a non-authoritative discovery aid. It
  links to canonical locations without copying exact values or implementation
  progress.
- Repository documentation should link here instead of copying an organization
  contract.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
organization contracts are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14), when and only when they appear
in all capitals.

## Contracts

- [ECS deployment contract](./platform/ecs-deployment-contract.md)
- [ECS health and readiness profiles](./platform/ecs-health-readiness-profiles.md)
- [ECS service contract ownership directory](./platform/ecs-service-health-matrix.md)

## Decisions

- [ADR-0001: Adopt a hybrid ECS deployment model](./decisions/0001-adopt-hybrid-ecs-deployment-model.md)
- [ADR-0002: Adopt state-aware ECS health profiles (Superseded)](./decisions/0002-adopt-state-aware-ecs-health-profiles.md)
- [ADR-0003: Adopt current-state ECS bootstrap classification](./decisions/0003-adopt-current-state-ecs-bootstrap-classification.md)

## Changing a contract

Update an organization contract when a shared invariant, reusable profile, or
cross-repository responsibility boundary changes. Service-local endpoints,
commands, mappings, workflows, and implementation status are updated only in
their owning repositories.

Add or supersede an architecture decision record when an organization change is
consequential, cross-repository, or hard to reverse. Do not use issue trackers,
pull request descriptions, or chat history as a second canonical source.
