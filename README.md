# .github

Org-wide **community health defaults and engineering governance** for the
`5010-dev` organization.

Supported community health files here are inherited by any repository in the
organization that does **not** provide its own equivalent. A repository's own
file always takes precedence. Engineering documents under `docs/` are canonical
organization references and must be linked explicitly from participating
repositories; GitHub does not inherit them automatically.

## Contents

- [`CONTRIBUTING.md`](./CONTRIBUTING.md) — default contribution and Git workflow policy
- [`pull_request_template.md`](./pull_request_template.md) — default pull request template
- [`docs/README.md`](./docs/README.md) — organization engineering documentation index
- [`ECS deployment contract`](./docs/platform/ecs-deployment-contract.md) — shared CDK and service-repository deployment model
- [`ECS health and readiness profiles`](./docs/platform/ecs-health-readiness-profiles.md) — state-aware health semantics by service shape
- [`ECS service profile and transition matrix`](./docs/platform/ecs-service-health-matrix.md) — canonical profiles, transition status, and pinned evidence
- [`ADR-0001`](./docs/decisions/0001-adopt-hybrid-ecs-deployment-model.md) — decision record for the hybrid ECS deployment model
- [`ADR-0002`](./docs/decisions/0002-adopt-state-aware-ecs-health-profiles.md) — decision record for state-aware ECS health profiles

## Notes

- To customize for a specific repo, add the equivalent file to that repo — it overrides this default.
- Defaults apply to repos without their own version and don't appear in each repo's file tree.
- GitHub reads these from this repo's **default branch**.
- Repository documentation should link to organization engineering contracts
  rather than copy them. Keep only repository-specific mappings and documented
  exceptions locally.
