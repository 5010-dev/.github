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
- [`Developer Tooling Standard`](./docs/standards/developer-tooling/README.md) — canonical Golden Path for commands, toolchains, dependencies, language and IaC profiles, conformance, and exceptions
- [`Golden Path bootstrap`](./docs/guides/bootstrap-new-repository.md) — immutable implementation locator, new-repository materialization, and validation procedure
- [`GitHub hosting capability profile`](./docs/guides/github-hosting-capabilities.md) — Free private baseline and optional paid-adapter boundaries
- [`Golden Path workflow template`](./workflow-templates/golden-path-quality.yml) — organization discovery starter for a repository-owned thin caller
- [`Engineering documentation standard`](./docs/standards/engineering-documentation/README.md) — canonical arc42 documentation contract
- [`Organization adoption guides`](./docs/guides/README.md) — Developer Tooling and engineering-documentation adoption and migration procedures
- [`Engineering documentation templates`](./templates/engineering-documentation/README.md) — repository, subsystem, ADR, runbook, and validation starters
- [`Governance repository tooling`](./scripts/docs/README.md) — standard source validation, documentation scaffold, and conformance checks
- [`Documentation governance workflow`](./.github/workflows/docs.yml) — automated validation for pull requests and `main`
- [`Golden Path bootstrap workflow`](./.github/workflows/golden-path-bootstrap.yml) — released implementation and dry-run fixture integration gate
- [`ECS deployment contract`](./docs/platform/ecs-deployment-contract.md) — shared CDK and service-repository deployment model
- [`ECS service delivery workflow standard`](./docs/platform/ecs-service-delivery-workflow-standard.md) — service release workflow invariants, variation, and conformance
- [`ECS health and readiness profiles`](./docs/platform/ecs-health-readiness-profiles.md) — state-aware health semantics by service shape
- [`ECS service contract ownership directory`](./docs/platform/ecs-service-health-matrix.md) — navigation to service runtime contracts and Infrastructure mappings
- [`Organization decisions`](./docs/decisions/README.md) — cross-repository ADR index

## Repository branch-policy exception

- Status: Accepted
- Accepted on: 2026-07-29
- Owner: `5010-dev` organization maintainers
- Scope: this `.github` governance repository only
- Effect on other repositories: none. They continue to follow
  `CONTRIBUTING.md` unless they maintain their own accepted exception.
- Organization policy:
  [`CONTRIBUTING.md`](./CONTRIBUTING.md#branch-roles) defines `dev` as the
  integration branch, work branches from `origin/dev`, pull requests to `dev`,
  and fast-forward promotion from `dev` to `main`.
- Exception: this repository currently has no `dev` branch. Normal changes use
  work branches from the latest `origin/main` and pull requests targeting
  `main`.
- Rationale: the repository has historically operated as a main-only source for
  inherited community defaults and linked organization governance. Maintainers
  are preserving that topology until they deliberately adopt an integration
  branch rather than creating a ceremonial branch without an operating need.
- Risks: merged governance changes become the organization default immediately,
  and this repository has no separate integration buffer before `main`.
- Controls: normal changes use focused work branches and review against `main`;
  the documentation governance workflow validates canonical sources and links.
  Direct commits to `main` remain disallowed unless an organization maintainer
  grants an explicit one-time exception for a bounded change.
- Approval authority: `5010-dev` organization maintainers. Presence of this
  accepted record on `main` establishes the repository exception.
- Review conditions: review when the organization Git policy changes, when this
  repository needs a sustained integration phase, or when its contributor or
  change volume makes a main-only model materially risky.
- Exit conditions: create and operate `dev`, move work branches and pull
  requests to it, and resume the standard `dev` to `main` fast-forward
  promotion flow.

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
