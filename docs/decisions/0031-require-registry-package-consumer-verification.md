# ADR-0031: Require registry package consumer verification

- Status: Accepted
- Date: 2026-09-15
- Owners: `5010-dev/.github` maintainers
- Refines: ADR-0007

## Context

The shared release sequence requires validated source, exact artifact identity,
immutable publication, and profile-appropriate verification. The Node library
profile requires fresh consumer smoke tests of a real tarball. Those checks can
pass before publication without proving that the registry's exact version can
be installed and used. The protected package-tag profile already states that
post-publication requirement explicitly; the general registry package profile
does not state the same minimum clearly.

Repositories may implement publication with different maintained tools and job
layouts. Common completion evidence can close this gap without standardizing
their publisher, tag format, build-input comparison, or result schema.

## Decision

Extend the shared package profile in Release and Versioning Standard `2026.09`
with [registry consumer verification](../standards/release-versioning/profiles.md#registry-package-consumer-verification).
Before completing a newly published version, or an interrupted publication with
unfinished verification, install the exact registry version in a fresh consumer
context, match the native integrity or digest when provided, and exercise a
small consumer use appropriate to the package. Representative execution has no
publication or registry authentication credentials.

Retain publication and consumer verification as distinct outcomes in native
release evidence. A failed check leaves the immutable version published with
incomplete verification. An authorized retry verifies the same published
identity without substituting a rebuilt archive or republishing it. Completed
unchanged older versions do not need repeated checks for unrelated releases.
Existing adoption rules preserve historical records without inventing missing
evidence.

Keep representative commands, consumer environments, job layout, build-input
change detection, and evidence storage repository-owned. Package visibility,
association, and consumer grants remain access-configuration and handoff checks.
The new minimum does not require full product end-to-end tests, production data,
or every supported platform; other applicable profile obligations remain.

## Consequences

Release completion includes evidence that consumers can obtain and use the
published package, in addition to pre-publication packaging checks. A registry
or consumer failure after publication remains visible and cannot be repaired by
overwriting the version.

Registry verification adds a bounded consumer check for each new version. It
does not require a common release implementation or add a second publication
authority. Existing source, artifact identity, permissions, and recovery rules
remain in force. The protected package-tag profile retains its additional
branch/channel, equivalence, and sibling-isolation requirements.

Repository adoption remains separately owned and reviewable. This policy change
does not modify consumer repositories, publish packages, change access settings,
or establish an organization-wide migration program.

## Alternatives considered

- Keep registry consumption entirely optional: local tarball checks would
  continue to permit completion without exercising the published distribution
  path.
- Standardize one publisher or shared workflow now: repository-specific
  implementation choices are not needed to define this common result. Shared
  implementation still follows the existing admission criteria.
- Require full consumer suites, all platforms, and repeated checks of every
  unchanged package: that exceeds the minimum evidence of a new version's
  registry consumption and remains subject to owning product and runtime rules.
