# ADR-0032: Reuse approved GitHub CLI authentication for package installation

- Status: Accepted
- Date: 2026-09-16
- Owners: `5010-dev/.github` maintainers
- Refines: ADR-0006 and ADR-0007

## Context

Publication and consumer verification already have organization contracts, but
developer installation authentication is described separately in package guides.
The Golden Path Agent journey explicitly asks for a PAT and user npm setup.
That can turn missing scope or access into instructions to create another
credential even when an approved GitHub CLI login can read the package.

Login identity, token scope, organizational approval, and package grants are
different responsibilities. A new token does not grant a missing account role.
Installation needs a common diagnostic and escalation path while exact package
commands, versions, and implementation remain repository-owned.

## Decision

Release and Versioning Standard `2026.09.1` establishes the
[private package authentication contract](../standards/release-versioning/package-authentication.md).
Developer Tooling Standard `2026.09` aligns the Node profile with that contract
and separates local read authentication from publication credential restrictions.

Default interactive local installation of private GitHub npm packages to an
approved GitHub CLI browser/OAuth login. Check host/account, package-read scope,
app/SSO approval, package access, and exact-version resolution. The developer
handles login and OAuth scope consent. Package administrators or organization
owners handle grants and organization approval. Unknown failures stop with
bounded diagnostic evidence. PAT issuance, another user's credentials, and
automatic identity changes are not recovery paths.

Keep registry credentials limited to installation, out of Git and diagnostics,
and absent from subsequent representative package execution. Environment
variables transport the selected identity; they do not authorize an unrelated
ambient credential. Preserve job-scoped CI read and publication tokens.

Link the central guide from package installation instructions and check the
documented route in a fresh context for new packages or substantive installation
changes. Preserve ADR-0031's separate registry consumer verification requirement.

## Consequences

Developers can reuse approved authentication without managing another PAT.
Failures identify the party that can fix the condition. Repository maintainers
retain installer implementation, native tool selection, exact coordinates, and
access-request contacts; this decision introduces no shared installer or central
execution service.

GitHub CLI availability, an approved OAuth login, and a working credential store
are prerequisites for the default local route. Hosts or organizational policies
that cannot support it require an explicit scoped decision through existing
exception handling, not an undocumented token fallback.

The current Golden Path journey is updated; historical ADRs, release artifacts,
and package records remain unchanged. Consumer adoption is separate work. This
central change neither updates installed packages nor changes account/package
permissions, and does not establish a new migration or release-approval program.

## Alternatives considered

- Require a separately managed PAT for every developer: duplicates credentials
  and does not distinguish scope consent from missing access grants.
- Send every failure to administrators: administrators cannot complete a
  developer's local login or OAuth consent, and not every failure is access denial.
- Treat successful `gh` login as sufficient: it does not prove package scope,
  organization approval, or access to the requested version.
- Standardize a shared installer: common outcomes and documentation are enough;
  repository-native implementation remains appropriate.
