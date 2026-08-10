# GitHub hosting capability profile

- Baseline: GitHub Free organization with private repositories
- Standard: `2026.08.7`
- Status: Informative platform capability mapping

GitHub plan capabilities are not normative rule authority and can change.
Re-verify current GitHub documentation before changing hosting controls.

## Baseline

| Surface | Baseline use | Boundary |
| --- | --- | --- |
| GitHub Actions | Run repository-owned canonical CI through `just ci` once | A passing job does not prove that the platform blocks merge. |
| Repository Actions secrets | Forward only explicitly named secrets | Never use `secrets: inherit` as a default. |
| OpenID Connect | Prefer short-lived credentials with exact repository, ref, and workflow claims | Cloud IAM and the repository workflow own authorization. |
| Dependency graph | Enable where supported | It is an input, not complete vulnerability or license evidence. |
| Dependabot alerts and security updates | Preserve repository alerts and security update routing | Repository owners still triage and validate remediation. |

Protected branches, rulesets, required checks, Environments, Dependency Review,
and private artifact attestations may depend on plan and repository settings.
They can strengthen repository-owned controls but are not prerequisites for the
Developer Tooling contract.

A repository that enables an optional hosting feature records owner, scope,
expected outcome, evidence, review date, and rollback condition in its own
canonical documentation. No central adapter selection schema, inventory,
approval queue, or enforcement workflow is required.
