# Organization architecture decisions

This directory preserves consequential, cross-repository engineering decisions.
Accepted ADRs retain their original rationale and are not rewritten to match a
later current view. A later decision adds a superseding ADR and updates this
index.

| ADR                                                                    | Status                 | Decision                                                      |
| ---------------------------------------------------------------------- | ---------------------- | ------------------------------------------------------------- |
| [ADR-0001](./0001-adopt-hybrid-ecs-deployment-model.md)                | Accepted               | Adopt a hybrid ECS deployment model                           |
| [ADR-0002](./0002-adopt-state-aware-ecs-health-profiles.md)            | Superseded by ADR-0003 | Adopt state-aware ECS health profiles                         |
| [ADR-0003](./0003-adopt-current-state-ecs-bootstrap-classification.md) | Accepted               | Adopt current-state ECS bootstrap classification              |
| [ADR-0004](./0004-adopt-arc42-engineering-documentation-system.md)     | Accepted               | Adopt arc42 as the canonical engineering documentation system |
| [ADR-0005](./0005-adopt-ecs-service-delivery-workflow-envelope.md)     | Accepted               | Adopt an ECS service delivery workflow envelope               |
| [ADR-0006](./0006-adopt-developer-tooling-golden-path.md)              | Superseded in part by ADR-0022 | Adopt the organization Developer Tooling Golden Path |
| [ADR-0007](./0007-adopt-release-and-versioning-standard.md)             | Accepted               | Adopt the organization Release and Versioning Standard        |
| [ADR-0008](./0008-separate-artifact-components-from-native-dependency-roots.md) | Superseded in part by ADR-0022 | Separate artifact components from native dependency roots |
| [ADR-0021](./0021-adopt-dependency-policy-compiler.md) | Superseded by ADR-0022 | Adopt the dependency policy compiler contract |
| [ADR-0022](./0022-retire-golden-path-executable-tooling.md) | Accepted | Retire Golden Path executable tooling and operate contract-only |

Organization standards and platform contracts hold the current normative view.
ADRs explain why those views were accepted.
