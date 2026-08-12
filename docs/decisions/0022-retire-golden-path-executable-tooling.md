# ADR-0022: Retire Golden Path executable tooling

- Status: Accepted
- Date: 2026-08-11
- Owners: `5010-dev/.github` maintainers and affected repository maintainers

## Context

The organization Golden Path grew from a shared contract into a locator-selected
binary, generator/upgrader, managed five-file footprint, reusable conformance
workflow, dependency compiler, live report, and security-closure orchestration.
Pilot work showed that keeping those layers aligned cost more review and release
coordination than the risks they reduced. Repeated follow-up releases also made
repository-owned changes appear dependent on a central tooling cadence.

The durable value is both the shared contract and a supported path for applying
it: truthful commands, native toolchain and dependency authority,
repository-owned CI and release flows, security visibility, bounded exceptions,
explicit native roots, stack defaults, examples, and end-to-end checklists.
Those outcomes do not require a custom central executable.

## Decision

1. Keep the Developer Tooling Standard and the retained native-root and
   runtime-support schemas in `5010-dev/.github` as normative authority.
2. Re-establish Golden Path as a contract-backed, repository-owned supported
   journey with bootstrap, adoption, stack defaults, copy-once examples,
   release-readiness guidance, a named owner, review date, and support channel.
3. Set the active central executable tooling identity to `none`.
4. Remove the active locator, bootstrap workflow, workflow template, executable
   integration checks, generated metadata/checker/dependency schemas, and
   consumer managed footprints.
5. Preserve repository-owned native manifests and locks, native roots,
   `release-units.json`, Just graphs, canonical CI, release/deployment workflows,
   and GitHub-native security visibility and routing.
6. Keep published `engineering-tooling` tags, releases, checksums, attestations,
   and snapshots immutable as audit history. They are not active, preferred,
   supported, or compatibility commitments.
7. Publish no retirement compatibility release. After all active consumers and
   locators are removed and verified, archive the implementation repository.
8. Permit a future thin validator only through a separate accepted decision with
   repeated-error evidence, off-the-shelf insufficiency, lower net operating
   cost, explicit source-controlled inputs, a named owner, and a removal
   condition.

## Consequences

- New repositories and adopters have an opinionated supported journey without
  acquiring a central runtime or upgrade dependency.
- Copied examples become repository-owned immediately; central changes do not
  generate or require consumer update pull requests.
- Existing consumers remove only the retired managed footprint and validate with
  their own canonical CI.
- There is no central adoption registry, organization PR queue, live report, or
  second execution of repository CI.
- Standards can still change through reviewed governance pull requests without
  forcing a binary release or consumer upgrade campaign.
- Any ambiguity stops only the affected repository-owned surface for
  classification.

## Supersession

This decision supersedes the executable implementation, locator, managed asset,
shared checker, and dependency compiler portions of ADR-0006, ADR-0008, and
ADR-0021. Their historical files remain unchanged.

Boundary classification: mixed — published tooling releases remain immutable
audit history; unreleased development intermediates and active repository source
are corrected directly to the contract-backed, repository-owned target.
