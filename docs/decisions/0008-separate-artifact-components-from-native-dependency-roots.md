# ADR-0008: Separate artifact components from native dependency roots

- Status: Accepted
- Date: 2026-08-04

## Context

Golden Path metadata describes repository artifacts and capabilities, while
native package managers resolve dependencies from ecosystem-specific project or
workspace roots. These boundaries often coincide in a small repository, but
they are not the same architectural concept.

A polyglot monorepo can contain several deployable artifacts inside one uv or
Cargo workspace, one artifact can participate in more than one native graph,
and unrelated Node.js projects can intentionally retain separate manifests and
locks. Treating every artifact component as a native root creates duplicate
locks and toolchain files. Treating the repository root as every ecosystem root
instead loses independently owned graphs.

Generated Golden Path metadata is a whole-file asset. Repository-specific
native-root declarations cannot be inserted into that generated file without
breaking its digest and future upgrade ownership.

## Decision

1. Artifact components and native dependency roots are separate axes.
2. A native dependency root is the directory from which one approved native
   manager owns a dependency graph, manifests, resolution records, and locked
   preparation semantics.
3. Multiple ecosystem roots MAY share the same repository-relative path when
   their profiles are disjoint. Two roots for the same profile MUST NOT overlap.
4. Multiple artifacts MAY use one native root, and an artifact MAY participate
   in more than one ecosystem root.
5. Packages in one native workspace use that workspace's root manifest and
   resolution record. Independent graphs are not required to merge merely
   because they share a Git repository.
6. Simple repositories MAY infer native roots from generated artifact
   components. A repository whose actual roots differ MUST declare them in the
   repository-owned `.github/golden-path-native-roots.yaml` contract.
7. The native-root declaration selects native-profile applicability for each
   root and MUST remain consistent with the aggregate profiles in
   `.github/golden-path.yaml`. Artifact types and capabilities remain owned by
   generated component or aggregate metadata.
8. The checker evaluates native manifest, dependency, runtime, and language
   authority rules at declared native roots. It does not infer a successful
   result from an unrelated repository-root file.
9. Generated metadata remains unmodified. The native-root declaration is an
   independent As-built input and is not part of the generated-asset inventory.

The normative requirements are maintained in the
[Developer Tooling Standard](../standards/developer-tooling/README.md).

## Consequences

### Positive

- Polyglot and multi-workspace repositories can describe their actual native
  dependency authorities without fake root manifests or duplicate locks.
- Generated metadata retains deterministic ownership and upgrade integrity.
- One checker model covers root workspaces, nested independent projects, and
  cross-language native-extension boundaries.
- New single-root repositories keep the existing compact declaration.

### Negative

- Complex repositories have one additional repository-owned contract to
  maintain.
- Native-root profiles must be validated against aggregate metadata to prevent
  contradictory applicability.
- Tooling must retain the legacy component inference path for repositories that
  do not need an explicit declaration.

## Alternatives considered

### Require one dependency root per Git repository

Rejected because native workspace boundaries are ecosystem-specific and
independent graphs can have different owners, credentials, update cadence, or
failure domains.

### Treat every artifact component as a dependency root

Rejected because several artifacts can share one lock and one artifact can
participate in multiple language graphs.

### Add repository-specific fields to generated metadata

Rejected because editing a whole-file generated asset invalidates its recorded
digest and makes future upgrades conflict with repository-owned state.

### Discover all roots recursively

Rejected because discovery is ambiguous in vendored, generated, example, and
nested-project trees. Explicit declaration is bounded and reviewable.

## Adoption status

The organization standard and serialized native-root contract define the
target. Shared checker support and a versioned tooling release implement the
contract. Individual repositories retain ownership of whether an explicit root
file is required and of their migration to it.
