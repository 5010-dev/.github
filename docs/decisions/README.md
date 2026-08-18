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
| [ADR-0022](./0022-retire-golden-path-executable-tooling.md) | Accepted | Retire executable control plane and retain a repository-owned Golden Path |
| [ADR-0023](./0023-adopt-protected-package-tag-publication-profile.md) | Superseded by ADR-0027 | Adopt the opt-in protected package-tag publication profile |
| [ADR-0024](./0024-separate-dependency-risk-from-routine-automation.md) | Accepted | Separate dependency-risk outcomes from routine-update automation |
| [ADR-0025](./0025-adopt-retained-artifact-tag-only-package-completion.md) | Superseded by ADR-0027 | Adopt retained-artifact tag-only package completion |
| [ADR-0026](./0026-recover-failed-tag-only-completion-with-new-authorization.md) | Superseded by ADR-0027 | Recover failed tag-only completion with a new authorization |
| [ADR-0027](./0027-simplify-protected-package-tag-publication.md) | Superseded by ADR-0028 | Simplify protected package-tag publication to an idempotent registry-native lifecycle |
| [ADR-0028](./0028-bind-protected-package-channels-to-branch-roles.md) | Accepted | Bind protected package prerelease and final channels to `dev` and `main` |
| [ADR-0029](./0029-default-package-tags-to-repository-token.md) | Accepted | Default protected package-tag creation to a job-scoped repository workflow token |

Organization standards and platform contracts hold the current normative view.
ADRs explain why those views were accepted.
