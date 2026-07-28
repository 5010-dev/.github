# ECS service contract ownership directory

- Status: Navigation index; non-authoritative discovery aid
- Last updated: 2026-07-29
- Applies to: `5010-dev` services using the shared AWS ECS platform

This directory connects the organization
[ECS deployment contract](./ecs-deployment-contract.md),
[service delivery workflow standard](./ecs-service-delivery-workflow-standard.md),
and [health profiles](./ecs-health-readiness-profiles.md) to the repositories
that own exact runtime and Infrastructure contracts.

This file is not a service-state SSOT. It does not record exact endpoints,
commands, timing, ports, parameter paths, revisions, pull-request state,
implementation progress, profile assignments, or conformance status.

## Ownership model

- The runtime owner maintains exact liveness, readiness, failure semantics,
  Docker health, deployment workflow, verification, and repository-local
  As-built, Target, and Open status.
- The Infrastructure owner maintains deployment-unit membership, structural
  inputs, SSM input classes, placeholder identity, ECS mappings, ALB and network
  exposure, task-definition health rendering, classification implementation,
  and repository-local status.
- This organization repository maintains only cross-repository ownership
  boundaries, workflow invariants, reusable profiles, current-state
  classification principles, and organization-wide invariants.

## Service ownership directory

| Service family      | Runtime owner                                                                      | Infrastructure owner                                                     | Runtime contract                                                                                                                                  | Infrastructure mapping                                                                                                   |
| ------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Indicator API       | [`5010-indicator-server`](https://github.com/5010-dev/5010-indicator-server)       | [`indicator-ecs-infra`](https://github.com/5010-dev/indicator-ecs-infra) | [Repository documentation](https://github.com/5010-dev/5010-indicator-server/blob/HEAD/README.md)                                                 | [ECS deployment view](https://github.com/5010-dev/indicator-ecs-infra/blob/HEAD/docs/architecture/07-deployment-view.md) |
| Academy Dashboard   | [`5010-academy-dashboard`](https://github.com/5010-dev/5010-academy-dashboard)     | [`indicator-ecs-infra`](https://github.com/5010-dev/indicator-ecs-infra) | [Backend documentation](https://github.com/5010-dev/5010-academy-dashboard/blob/HEAD/backend/README.md)                                           | [ECS deployment view](https://github.com/5010-dev/indicator-ecs-infra/blob/HEAD/docs/architecture/07-deployment-view.md) |
| Calculator          | [`fiftyten-indicators-core`](https://github.com/5010-dev/fiftyten-indicators-core) | [`indicator-ecs-infra`](https://github.com/5010-dev/indicator-ecs-infra) | [Calculator service documentation](https://github.com/5010-dev/fiftyten-indicators-core/blob/HEAD/apps/calculator-service/README.md)              | [ECS deployment view](https://github.com/5010-dev/indicator-ecs-infra/blob/HEAD/docs/architecture/07-deployment-view.md) |
| Data Collector      | [`indicator-data-collector`](https://github.com/5010-dev/indicator-data-collector) | [`indicator-ecs-infra`](https://github.com/5010-dev/indicator-ecs-infra) | [Deployment view](https://github.com/5010-dev/indicator-data-collector/blob/dev/docs/architecture/07-deployment-view.md)                          | [ECS deployment view](https://github.com/5010-dev/indicator-ecs-infra/blob/HEAD/docs/architecture/07-deployment-view.md) |
| Quant Bot           | [`fiftyten-quant`](https://github.com/5010-dev/fiftyten-quant)                     | [`indicator-ecs-infra`](https://github.com/5010-dev/indicator-ecs-infra) | [Engine deployment contract](https://github.com/5010-dev/fiftyten-quant/blob/dev/docs/architecture/subsystems/engine/deployment.md)               | [ECS deployment view](https://github.com/5010-dev/indicator-ecs-infra/blob/HEAD/docs/architecture/07-deployment-view.md) |
| Quant Observability | [`fiftyten-quant`](https://github.com/5010-dev/fiftyten-quant)                     | [`indicator-ecs-infra`](https://github.com/5010-dev/indicator-ecs-infra) | [Observability deployment contract](https://github.com/5010-dev/fiftyten-quant/blob/dev/docs/architecture/subsystems/observability/deployment.md) | [ECS deployment view](https://github.com/5010-dev/indicator-ecs-infra/blob/HEAD/docs/architecture/07-deployment-view.md) |

The linked repositories remain authoritative even when a linked landing document
needs further repository-local refinement. Executable code and workflows are
the current As-built authority; canonical repository architecture and ADRs own
accepted Target and Open decisions.

## Cross-link requirement

Each runtime contract MUST link to the organization ECS contract and its
canonical Infrastructure mapping. Each Infrastructure mapping MUST link to the
service-owned runtime contract. Exact values MUST be documented by their owner,
not copied into this directory.

## Directory maintenance

Update this file only when:

- a runtime or Infrastructure owner changes;
- a service family is added or retired; or
- a canonical document location changes.

Do not update this directory merely because:

- an endpoint, command, timing, port, path, or parameter changes;
- a workflow or task-definition strategy changes;
- implementation or conformance status changes; or
- a pull request opens, merges, or closes.

Those changes belong only in the owning repositories unless they also change an
organization-wide invariant or ownership boundary.

## Related decisions

- [ADR-0001: Adopt a hybrid ECS deployment model](../decisions/0001-adopt-hybrid-ecs-deployment-model.md)
- [ADR-0002: Adopt state-aware ECS health profiles (Superseded)](../decisions/0002-adopt-state-aware-ecs-health-profiles.md)
- [ADR-0003: Adopt current-state ECS bootstrap classification](../decisions/0003-adopt-current-state-ecs-bootstrap-classification.md)
- [ADR-0005: Adopt an ECS service delivery workflow envelope](../decisions/0005-adopt-ecs-service-delivery-workflow-envelope.md)
