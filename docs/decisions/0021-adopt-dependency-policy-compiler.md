# GP-021: Adopt the dependency policy compiler contract

- Status: Accepted
- Date: 2026-08-09

## Context

Dependency automation was enabled without a complete contract connecting native
roots, affected release units, validation boundaries, owner routes, lifecycle,
and bounded PR volume. Routine queues accumulated while security routing and
repository ownership had to remain available.

## Decision

Adopt the authority and serialized contracts in
`docs/standards/developer-tooling/dependency-operations.md`. The compiler binds
existing repository-owned native-root and release-unit IDs; it does not create
or infer release units. Unknown roots stop only their routine lane. Security
visibility and remediation routing are independent of routine budget and
grouping.

The first complete published contract remains `golden-path/v1` and is released
as standard `2026.08.3` with a new immutable tooling release. Published
`2026.08.2` and tooling `1.4.0` remain unchanged.

## Consequences

- Repository owners can classify a root and preview candidates without central
  approval or package-level mapping.
- Central conformance validates references and adapter semantics but does not
  rerun repository `just ci`.
- Live organization state remains digest-bound report evidence rather than an
  offline checker input or central ledger.
- Dependabot remains the default; duplicate Dependabot/Renovate ownership is a
  conformance failure.

Boundary classification: released — `2026.08.2` and `engineering-tooling 1.4.0`
are immutable; this contract is published in a new standard/tooling release.
