# .github

Org-wide **community health defaults and engineering governance** for the
`5010-dev` organization.

Supported community health files here are inherited by repositories that do not
provide an equivalent. Engineering contracts under `docs/` are linked
explicitly; GitHub does not copy them into consumer repositories.

## Contents

- [Contribution policy](./CONTRIBUTING.md)
- [Pull request template](./pull_request_template.md)
- [Engineering documentation index](./docs/README.md)
- [Developer Tooling Standard](./docs/standards/developer-tooling/README.md)
- [Release and Versioning Standard](./docs/standards/release-versioning/README.md)
- [Developer Tooling adoption guide](./docs/guides/adopting-developer-tooling.md)
- [Engineering documentation standard](./docs/standards/engineering-documentation/README.md)
- [Engineering documentation templates](./templates/engineering-documentation/README.md)
- [Governance repository checks](./scripts/docs/README.md)
- [Documentation governance workflow](./.github/workflows/docs.yml)
- [Platform contracts](./docs/platform/README.md)
- [Organization decisions](./docs/decisions/README.md)

## Repository branch-policy exception

- Status: Accepted
- Accepted on: 2026-07-29
- Owner: `5010-dev` organization maintainers
- Scope: this `.github` governance repository only
- Effect on other repositories: none. They continue to follow
  [`CONTRIBUTING.md`](./CONTRIBUTING.md) unless they maintain an accepted
  repository-local exception.
- Exception: this repository has no `dev` branch. Normal changes use focused
  work branches from the latest `origin/main` and reviewed pull requests
  targeting `main`.
- Rationale: this repository is the main-only source for inherited community
  defaults and linked organization governance.
- Risks: merged governance changes become the organization default immediately.
- Controls: focused work branches, review against `main`, and the
  documentation governance workflow. Direct commits to `main` remain
  disallowed without an explicit bounded maintainer exception.
- Approval authority: `5010-dev` organization maintainers.
- Review conditions: review when organization Git policy changes or this
  repository needs a sustained integration phase.
- Exit conditions: create and operate `dev`, move work branches and pull
  requests to it, and resume the standard fast-forward promotion flow.

## Notes

Repository documentation should link to organization contracts instead of
copying them. Exact commands, manifests, locks, deployment mappings, releases,
security state, and implementation status remain in their owning repositories.
