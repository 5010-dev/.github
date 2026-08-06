# GitHub hosting capability profile

- Baseline: GitHub Free organization with private repositories
- Standard: `2026.08.1`
- Verified: 2026-08-01
- Status: Informative platform capability mapping

This guide maps the Developer Tooling outcomes to the weakest hosting plan the
organization intends to use. GitHub plan capabilities are not normative rule
authority and can change independently. Re-verify the linked GitHub sources
before changing the baseline or enabling a paid adapter.

## Free private baseline

| Surface | Baseline use | Boundary |
| --- | --- | --- |
| GitHub Actions | Run repository-owned quality CI through `just ci` once and run the checker-only, report-only conformance caller independently | A failing job does not by itself prove that merge is blocked. Private-repository minutes and storage are plan quotas. |
| Repository Actions secrets | Forward only explicitly named secrets when a job needs them | Golden Path conformance itself needs no consumer secret. Never use `secrets: inherit` as the default. |
| OpenID Connect | Prefer short-lived cloud credentials with exact repository, ref, and workflow claims | Cloud IAM and the caller own authorization. Require an environment claim only when a paid Environment adapter is selected; OIDC availability does not create an approval boundary. |
| Dependency graph | Keep the repository dependency inventory enabled where supported | It is an input to dependency features, not complete vulnerability or license evidence. |
| Dependabot alerts and security updates | Use repository alerts and bounded automated security updates | Repository owners still triage findings and validate update pull requests. |
| Repository-local Golden Path metadata and evidence | Record profiles, artifacts, capabilities, exceptions, exact pins, and checker output in repository-owned surfaces | This is the portable baseline when no hosting enforcement feature is available. |

Current GitHub documentation describes Actions as available on all plans,
repository secrets as available to Actions, OIDC-based cloud authentication,
and Dependabot alerts and security updates for repositories. Organization-level
Actions secrets are not accessible to private repositories on GitHub Free, so
they are not part of this baseline:

- [GitHub Actions billing and plan availability](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
- [OpenID Connect in cloud providers](https://docs.github.com/en/actions/concepts/security/openid-connect)
- [OpenID Connect reference and immutable subject claims](https://docs.github.com/en/actions/reference/security/oidc)
- [About the dependency graph](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph)
- [Dependabot alerts](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts)
- [Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates)

GitHub repositories created after July 15, 2026, repositories that opt in, and
repositories renamed or transferred after that date use an immutable OIDC
`sub` format containing owner and repository IDs. Before enabling OIDC or
changing repository identity, inspect the issued subject and update the cloud
trust policy to match the repository's active format. Coordinate that migration
with the repository and cloud-IAM owners so the old trust is removed only after
the new subject succeeds.

## Features that are not baseline prerequisites

| Optional adapter | Why it is not required for Free private repositories | Conforming fallback |
| --- | --- | --- |
| Protected branches, rulesets, and required checks | Private-repository enforcement requires a paid organization plan | Policy-required review plus positive Actions evidence; never claim `platform-enforced` |
| GitHub Environments and required reviewers | Private-repository environment protection is not a universal Free capability | Bounded manual workflow, cloud-IAM role separation, or durable external approval evidence |
| Organization Actions secrets | Private repositories cannot access organization secrets on GitHub Free | Repository secrets or secretless OIDC; named forwarding only |
| Dependency Review action | Private use requires GitHub Code Security | Lockfile review, native audit tooling, Dependabot, and repository-owned evidence |
| GitHub-native private artifact attestations | Private/internal repository support requires GitHub Enterprise Cloud | Exact digest and source verification plus an available external provenance or signing system |
| Organization custom properties | Availability and enforcement depend on the plan and repository configuration | Repository-local metadata remains authoritative for applicability and versions |

The private-attestation boundary does not prevent a GitHub Free private
consumer from verifying the public `engineering-tooling` release attestation.
It means that attestations for artifacts produced by the private consumer
repository cannot be assumed as a baseline feature.

See GitHub's current plan boundaries for
[protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches),
[rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets),
[deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments),
[Dependency Review](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review),
and [artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).

## Paid-adapter selection record

A repository that enables a paid hosting feature keeps a repository-local
selection record in canonical documentation or a hosting-policy file. The
record MUST validate against the
[`golden-path-hosting-adapter-selection/v1` schema](./schemas/golden-path-hosting-adapter-selection-v1.schema.json).
It is an operational record, not Golden Path metadata and not an
organization-wide inventory:

```yaml
schemaVersion: golden-path-hosting-adapter-selection/v1
baseline: github-free-private
adapters:
  protected-ref:
    state: pilot # pilot | enabled | rollback | disabled
    owner: repository-maintainer
    scope: default branch
    expectedOutcome: platform-enforced conformance check
    evidence: https://github.com/example/example/settings/rules
    enabledAt: 2026-08-01
    reviewBy: 2026-09-01
    rollback:
      trigger: required check is unavailable or blocks emergency recovery
      action: disable this ruleset adapter and return to policy-required review
```

The record must not contain secret values. Each key under `adapters` is the
stable repository-local adapter ID and is therefore unique within the record.
`state`, `owner`, `scope`, `expectedOutcome`, `evidence`, `reviewBy`, and the
rollback trigger and action are required for every recorded adapter. `enabledAt`
is required for `pilot`, `enabled`, and `rollback`. A
[valid JSON example](./schemas/examples/golden-path-hosting-adapter-selection-v1.valid.json)
is provided; JSON is also valid YAML. Example adapter IDs include
`protected-ref`, `environment-review`, `organization-secret`,
`dependency-review`, or `private-attestation`.

## Rollout and rollback

1. Confirm the repository already passes the Free private baseline. A paid
   feature strengthens an outcome; it does not repair missing metadata,
   commands, or exact pins.
2. Record the selected adapter, owner, scope, expected outcome, evidence,
   review date, rollback trigger, and rollback action.
3. Pilot on a bounded repository or non-production path. Verify the stable
   `Developer Tooling / Conformance` identity, token permissions, secret flow,
   and recovery access.
4. Enable the adapter without changing the Golden Path rule meaning or caller's
   immutable implementation reference.
5. Roll back only the hosting enforcement layer when its trigger occurs. Keep
   repository-local CI and policy-required review running, record the reason,
   and move the selection state to `rollback` or `disabled`.

Organization-setting changes and consumer-repository migrations are outside
this central implementation. They require separately authorized,
repository-owned work.
