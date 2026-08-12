# ADR-0023: Adopt protected package-tag publication profile

- Status: Accepted
- Date: 2026-08-12
- Owners: `5010-dev/.github` maintainers and selecting repository maintainers
- Planning authority: [ENG-226](https://linear.app/5010-tech/issue/ENG-226)

## Context

The organization default publishes governed software from validated `main`.
That remains the right boundary for repositories whose release units move
together and for services or applications whose `main` promotion is the
production effect.

A mixed monorepo can instead contain a reusable registry package and a service
or application with independent consumers, compatibility surfaces, cadence,
correction, and production effects. Requiring repository-wide `main` promotion
to publish that package can unintentionally couple package delivery to sibling
service deployment. Publishing every `dev` commit, accepting arbitrary workflow
inputs, or introducing a central release queue would replace that coupling with
ambiguous or centralized authority.

A reviewed release-preparation change needs a deterministic admission boundary.
JSON Schema can validate intent shape but cannot prove the exact Git diff,
manifest version-only change, source base, or sibling mutation exclusion. A
small repository-state checker is therefore useful without becoming a
publication workflow or current-version service.

## Decision

1. Preserve validated `main` as the default publication profile.
2. Allow only a monorepo with an independently released registry package and an
   independently released service or application to select the
   [protected package-tag profile](../standards/release-versioning/protected-package-tag.md).
3. Treat the immutable package-specific protected tag as authority only for the
   declared package version. `dev` remains a non-deployed integration branch,
   and `main` remains production authority for sibling services and applications.
4. Require a repository-local profile contract and one newly added immutable
   release intent. Derive release unit, channel, exact version, source, and tag
   from the protected `dev` merge event and reviewed repository state rather than
   arbitrary workflow inputs.
5. Bind contract package identity and version to one JSON or TOML native
   manifest. Require each admitted version to have greater SemVer precedence
   than its materialized predecessor. Admit only one exact intent and one
   version-field change in the merge diff. Use segment-aware path patterns and
   reject stale, modified, renamed, duplicate, conflicting, or mismatched intent,
   destructive or non-regular release-preparation entries, and every declared
   sibling release-unit mutation.
6. Use the same package identity for prerelease and final publication. A
   prerelease uses native SemVer and a non-`latest` channel; a final release uses
   a new final SemVer and `latest`. Consumers pin exact versions.
7. Create the immutable tag and publish in one serialized protected state
   machine. Retries verify identical remote state; conflicts fail closed and
   published tags or versions are never overwritten or reused.
8. Split minimum permissions by responsibility: validation uses
   `contents: read`, private-package consumption uses `packages: read`, and only
   the package publication job receives `packages: write`. Hosting-specific tag
   mutation authority remains narrowly scoped and cannot push branches.
9. Keep exact package name, initial and current version, registry access, tag
   pattern, workflows, credentials, recovery, history, and package/service
   release-unit inventory repository-owned.
10. Provide versioned schemas and a Python-standard-library exact-diff reference
    checker in the governance repository. The checker supports JSON Pointer and
    TOML dotted-key native manifest selectors, reads source-controlled local
    inputs and Git objects only, and does not publish, query registries, inspect
    hosting approvals, or run consumer CI.
11. Do not create a central release queue, repository current-version registry,
    package-name registry, shared publication workflow, or cross-repository
    approval gate.

## Consequences

- Existing repositories do not change unless they materialize and enforce the
  opt-in contract.
- The Design System retains its Changesets preparation on `dev`, fast-forward
  promotion, and `main` publication workflow.
- A selecting repository can publish its package without deploying a sibling
  service, while every untagged `dev` commit remains unreleased.
- Release preparation becomes intentionally narrow: version, changelog, one
  intent, and repository-declared supporting paths.
- The checker has a bounded responsibility and dependency surface. A repository
  still owns review protection, rulesets, package closure, registry uniqueness,
  publication, evidence, and recovery.
- Schema or checker incompatibility is corrected in place until a real released
  consumer exists; after that boundary, consumers coordinate or select a new
  compatibility major.

## Alternatives considered

### Require `main` for every package in every monorepo

Rejected because it couples an independent package release to unrelated service
or application production effects.

### Publish every `dev` commit or use manual version inputs

Rejected because a mutable branch or arbitrary input is not reviewed immutable
release intent and cannot establish exact package identity.

### Build a central release queue or current-version registry

Rejected because repository-native manifests, tags, registries, workflows, and
release history already own those facts. A central copy would drift and become a
second publication authority.

### Use JSON Schema without an exact-diff checker

Rejected because structural validation cannot establish source ancestry, a
single newly added intent, a version-only manifest change, or sibling isolation.

Boundary classification: unreleased — corrected in place. This decision adds a
new opt-in profile before its first package publication; it does not rewrite an
existing package, tag, Design System release, service deployment, or durable
state.
