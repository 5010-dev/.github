# Developer Tooling conformance

- Status: Accepted
- Standard version: `2026.08.7`
- Active central checker: none

Conformance is the owning repository's reviewable agreement between the central
contract and repository-native As-built behavior.

## Required evidence

An applicable repository demonstrates conformance through:

- truthful root commands;
- native manifests, locks or integrity records, and exact toolchain selectors;
- the repository's canonical CI running `just ci` once;
- release, deployment, and security evidence only when those outcomes apply;
  and
- approved, bounded, expiring exceptions for unmet normative requirements.

A passing structural or syntax check does not prove release, deployment,
hosting enforcement, vulnerability closure, or runtime behavior.

## Validation boundary

Repositories SHOULD use ecosystem-native and off-the-shelf checks in their
canonical CI. The central governance repository validates only its own
documentation and retained JSON sources; it does not run consumer CI.

There is no organization reusable conformance workflow, checker output schema,
rule catalog, live GitHub report, or central status registry. A repository MUST
NOT add a second `just ci` run merely to report central conformance.

## Enforcement language

Keep these states distinct:

- `report-only`: evidence is visible but not an accepted merge requirement;
- `policy-required`: maintainers require positive evidence through review; and
- `platform-enforced`: the hosting platform technically blocks the protected
  action.

Do not claim `platform-enforced` from a green Actions job alone.

## Incomplete or ambiguous scope

When applicability is unclear, stop only the affected repository-owned surface
and classify it. Do not synthesize dummy manifests, central mappings, no-op
commands, or organization approval queues to obtain a pass.
