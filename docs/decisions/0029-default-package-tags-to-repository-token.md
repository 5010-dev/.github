# ADR-0029: Default package-tag creation to the repository workflow token

- Status: Accepted
- Date: 2026-08-19
- Owners: `5010-dev/.github` maintainers and selecting repository maintainers
- Refines: ADR-0028

## Context

ADR-0028 establishes the branch/channel, package-closure, immutable identity,
idempotent publication, and sibling-isolation model for the protected
package-tag profile. One credential detail remained unnecessarily strong: the
profile required hosting rules to limit tag creation to an approved workflow
identity and required a credential that could not push branches.

On GitHub, a repository's ordinary Actions token cannot bypass a tag-creation
restriction that applies to that same repository. A dedicated GitHub App and
private key can provide the bypass, but the application is still configured by
repository or organization administrators and invoked by the same protected
workflow. It therefore adds a long-lived credential, key rotation, installation
state, App-token minting, and an additional branch-exclusion rule without
creating independent release approval.

Existing tag immutability, exact-source verification, protected branch merge,
registry integrity, clean-consumer execution, and sibling isolation are the
actual release invariants. They do not require hosting-level exclusive tag
creation.

## Decision

1. Keep protected branch merge and the repository-owned serialized,
   idempotent publication workflow as release authorization.
2. Keep the package-tag ruleset's update, deletion, and non-fast-forward
   protections. Do not require a tag-creation restriction or bypass actor as the
   organization default.
3. For GitHub Packages, use a job-scoped repository `GITHUB_TOKEN` with
   `contents: write` only in the exact tag-creation job. The job re-reads live
   tag and registry state immediately before mutation and creates one absent
   package tag for the verified source.
4. Keep registry publication in a separate job whose write authority is
   `packages: write`. The tag-creation job does not receive registry write
   authority, and the registry-publication job does not receive tag write
   authority.
5. Prohibit branch-ref and sibling release-unit mutations in the tag-creation
   job. Workflow tests and repository review verify that behavioral boundary;
   the policy does not claim that the token is structurally incapable of every
   other repository write.
6. Make a dedicated GitHub App, private key/PEM, App-token mint action, and
   additional all-branch exclusion ruleset optional repository-specific
   hardening. They require a concrete risk or external obligation and are not an
   organization minimum.
7. A repository removing those optional controls first aligns the central
   contract, canonical architecture, workflow, checker, and tests; verifies the
   merged replacement and live rules; then removes obsolete rulesets, secrets,
   installations, keys, and App registrations.
8. Do not mutate existing package versions, immutable tags, or dist-tags to
   prove the credential transition. The next real package-relevant publication
   proves the creation path.
9. Keep private-package consumer authentication unchanged. This decision
   concerns publication credentials, not `packages: read` access for local or CI
   installation.

## Consequences

- The release model and immutable artifact boundary remain unchanged.
- The supported workflow has fewer credentials and hosting-state dependencies.
- Existing tags remain protected against movement and deletion, while creation
  correctness is enforced by the protected workflow's exact-source and
  fresh-state checks.
- A maintainer with repository administration can still change workflows or
  hosting settings, as before. The policy states that authority boundary
  directly instead of presenting an administrator-controlled App as an
  independent authorization plane.
- Repositories with a demonstrated need for stronger creator isolation may keep
  or adopt it as an explicit repository-specific control.
- The Design System remains unchanged because it does not select this profile.

## Alternatives considered

### Keep the dedicated App as the organization minimum

Rejected because it adds a non-expiring private key and operational coupling
without adding an independent reviewer, owner, or release authorization.

### Remove tag protection entirely

Rejected because existing published tags are immutable release identities.
Update, deletion, and non-fast-forward protections remain necessary.

### Combine tag and registry writes in one job

Rejected because the mutations have different responsibilities and can retain
simple job-level least-privilege separation.

### Publish the private package publicly to avoid consumer authentication

Rejected as unrelated. Registry visibility and consumer read access are a
separate product and distribution decision.

Boundary classification: released governance contract — coordinated
supersession is required because Core and Platform currently consume the prior
credential profile; no dual-policy compatibility mode is retained for the
unreleased cross-repository `dev` integration.
