# Release automation

Release automation implements the artifact profile and evidence contract. It is
not the source of normative policy and does not transfer publication ownership
away from the releasing repository.

## Ownership

| Organization standard or shared implementation | Releasing repository |
| --- | --- |
| Artifact-profile outcomes and portable evidence fields | Exact release unit and version decision |
| Optional schemas, checker contracts, and adapter interfaces | Native manifests and release metadata |
| Selection criteria for reusable automation | Trigger, approval, environment, and publication timing |
| Immutable implementation release and compatibility information | Credentials, registry and cloud access, and least-privilege permissions |
| Generic failure and evidence semantics | Build, publish, deploy, verify, recover, and current history |

Production deployment mutation, rollout, rollback, runtime readiness, and
operational verification remain owned by applicable platform delivery standards
and repository workflows. Release automation MUST carry the required release
identity into those workflows but MUST NOT replace their safety contract.

## Required publication sequence

Automation MUST perform the applicable phases in this order or prove an
equivalent fail-closed order:

1. Resolve the release unit, profile, version source, requested version, and
   target channel.
2. Verify validated `main`, exact source revision, and required source or
   manifest state.
3. Verify version, tag or ref, registry, and channel uniqueness and consistency.
4. Build, test, and package once from the selected source boundary.
5. Compute the exact artifact identity and the checksum, SBOM, or provenance
   evidence required or selected by the applicable profile and capability.
6. Create a draft or staging record where the distribution system permits it.
7. Publish the immutable artifact and release record without overwriting an
   existing identity.
8. Verify registry lookup, pull, install, execution, digest, or deployment state
   according to the profile.
9. Emit durable release evidence and an explicit success, staged, partial, or
   failed state.

Publication of the same release unit MUST be serialized. A workflow MUST NOT use
concurrency cancellation that can interrupt an older run after irreversible
publication begins. Every remote mutation and verification loop MUST be bounded
and report an unambiguous failure when its result cannot be established.

## Partial publication and recovery

Release publication is not generally transactional. Automation MUST identify
which steps are reversible and which registry operations are permanent.

- Before immutable publication, a draft MAY be completed, replaced, or removed
  under the distribution system's documented recovery semantics.
- After a package version, tag, image digest, or immutable release is published,
  recovery MUST NOT overwrite it. Use a correction release and an applicable
  deprecate, yank, or retract operation.
- A partial result MUST retain source, intended version, completed publication
  identities, failed phase, owner action, and retry or correction path.
- A retry MUST re-read remote state and fail when it would create a conflicting
  identity or claim success for a different artifact.

## Shared automation admission

The organization MUST NOT mandate one universal release workflow or tool.

A reusable workflow or shared release adapter MAY become an organization shared
implementation only when all of the following are true:

1. at least two stable implementations of the same artifact profile demonstrate
   the same outcome and recovery semantics;
2. the common interface has a small, typed input and named-secret surface;
3. the caller retains version, trigger, credentials, publication, and recovery
   decisions;
4. non-trivial logic has a deterministic local or shared-core test path; and
5. the implementation has an immutable version or commit pin, compatibility
   record, upgrade path, and rollback path.

A caller MUST pin a reusable workflow or action to an immutable full commit SHA
or an organization-approved immutable release locator. A moving branch or tag
MUST NOT be the execution identity for publication-capable shared automation.

The releasing repository MUST own an intentionally thin caller. Thin describes
the responsibility boundary, not a line-count target: GitHub Actions owns event,
permissions, credential setup, concurrency, invocation, and summaries, while
deterministic release logic remains locally or independently executable.

## Permissions and credentials

- Caller permissions MUST be explicit and least privilege.
- Secrets MUST be forwarded by name. `secrets: inherit` MUST NOT be the default.
- OIDC or repository-scoped `GITHUB_TOKEN` SHOULD replace long-lived publication
  credentials when the registry or cloud supports it.
- Public npm publication SHOULD use npm trusted publishing and registry
  provenance when the release topology is supported.
- GitHub Packages publication SHOULD use the releasing repository's
  `GITHUB_TOKEN`; consumer repositories retain explicit package read access.
- A called workflow MUST NOT assume it can elevate permissions the caller did
  not grant.
- Private shared workflow access and any hosting-plan configuration are
  operational adapters, not normative authority.
- Third-party actions used in a publication workflow MUST be pinned to a full
  commit SHA and reviewed for required permissions and output handling.

## Tool selection

Ecosystem-native build and publish commands remain the final publication
authority. Repositories MAY select tools that satisfy this contract; the tool
does not replace native registry state or release evidence.

- Changesets is the default candidate for Node.js multi-package repositories
  that need per-package release intent, internal dependency coordination,
  version updates, and changelogs.
- Release Please is the default candidate for Conventional Commit-based release
  pull requests, version updates, changelogs, tags, and GitHub Releases across
  supported ecosystems. Registry publication remains a separate native step.
- A CLI or binary release MAY use GoReleaser, cargo-dist, or a repository-local
  implementation that meets the applicable profile.
- New automation MUST NOT adopt a deprecated or unmaintained release tool.

These are recommended adapters, not required organization products. A
repository MAY use another maintained tool or a small native implementation
when it produces the same evidence, immutability, failure, and recovery outcomes.

## Relevant upstream guidance

- [GitHub reusable workflow reference](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
- [GitHub secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub OIDC with reusable workflows](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows)
- [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/)
- [GitHub Packages with GitHub Actions](https://docs.github.com/en/packages/managing-github-packages-using-github-actions-workflows/publishing-and-installing-a-package-with-github-actions)
- [Changesets](https://github.com/changesets/changesets)
- [Release Please](https://github.com/googleapis/release-please)
