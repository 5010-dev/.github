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
- [`Engineering documentation standard`](./docs/standards/engineering-documentation/README.md) — canonical arc42 documentation contract
- [`Documentation adoption guides`](./docs/guides/README.md) — adoption and migration procedures
- [`Engineering documentation templates`](./templates/engineering-documentation/README.md) — repository, subsystem, ADR, runbook, and validation starters
- [`Documentation tooling`](./scripts/docs/README.md) — source validation, scaffold, and conformance checks
- [`ECS deployment contract`](./docs/platform/ecs-deployment-contract.md) — shared CDK and service-repository deployment model
- [`ECS health and readiness profiles`](./docs/platform/ecs-health-readiness-profiles.md) — state-aware health semantics by service shape
- [`ECS service contract ownership directory`](./docs/platform/ecs-service-health-matrix.md) — navigation to service runtime contracts and Infrastructure mappings
- [`Organization decisions`](./docs/decisions/README.md) — cross-repository ADR index

## Notes

- To customize for a specific repo, add the equivalent file to that repo — it overrides this default.
- Defaults apply to repos without their own version and don't appear in each repo's file tree.
- GitHub reads these from this repo's **default branch**.
- Arbitrary standards, guides, and templates in this repository are not inherited
  automatically. Participating repositories link to the standards and adopt the
  templates or equivalent local structures explicitly.
- Repository documentation should link to organization engineering contracts
  rather than copy them. Exact endpoints, commands, mappings, and implementation
  status remain in their owning service or Infrastructure repository.
