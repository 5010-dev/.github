# ADR-0004: Adopt arc42 as the canonical engineering documentation system

- Status: Accepted
- Date: 2026-07-27

## Context

Engineering architecture had begun to converge across several `5010-dev`
repositories, but the organization did not define a common documentation
contract. Repositories could independently choose document locations, state
vocabulary, decision handling, authority boundaries, and validation, making
cross-repository navigation and review inconsistent.

Existing repositories demonstrate two important requirements. Product and
infrastructure repositories need a consolidated current architecture view that
can grow from whole-system chapters into subsystem and boundary-contract detail.
Mixed-purpose repositories may also contain scientific or empirical authorities
that must not be replaced by engineering documentation.

A repository-only rule is therefore too narrow, while requiring a full arc42
corpus for every directory, package, process, or model would create
documentation layers without real architectural boundaries.

## Decision

The organization adopts **`5010-arc42-v1`** as the canonical documentation
profile for engineering systems.

1. An engineering repository applies the profile to its repository-level
   engineering system.
2. A mixed-purpose repository applies the profile to each independently
   governed engineering layer without replacing scientific, empirical, legal,
   or other domain-specific canonical authorities.
3. The canonical arc42 spine owns engineering goals, boundaries,
   responsibilities, strategy, runtime and deployment views, cross-cutting
   concepts, quality, risks, and accepted target state.
4. Executable code, schemas, generated contracts, runbooks, validation evidence,
   scientific design, and empirical results remain concern-specific authorities
   and are linked rather than copied.
5. L0 uses the organization twelve-chapter profile. L1 subsystem and boundary
   documentation is added only when independent responsibility, failure,
   security, lifecycle, contract, change, or quality complexity justifies it.
6. Architecture state uses As-built, Target, Open, and Deprecated. ADR lifecycle
   remains a separate status system.
7. Architecture-significant changes update affected current views, ADRs,
   runbooks, generated contracts, and evidence in the same change.
8. The organization provides scaffold templates and a reference conformance
   checker. Adopted repositories own their generated documents and do not remain
   byte-identical to the templates.
9. New systems adopt the current profile when establishing a stable
   architecture boundary. Existing systems migrate through planned
   documentation work or an architecture-significant change rather than
   blocking unrelated maintenance.
10. Material local exceptions require a durable rationale and replacement
    authority or validation.

The normative requirements are maintained in the
[engineering documentation standard](../standards/engineering-documentation/README.md).

## Consequences

### Positive

- Contributors can locate the canonical engineering current view across
  repositories and mixed-purpose layers.
- Shared chapter names, state vocabulary, and validation reduce structural
  fragmentation.
- Scientific, empirical, executable, generated, and operational authorities
  remain explicit instead of being flattened into architecture prose.
- Repositories can grow from a simple L0 view to hierarchical subsystem and
  boundary-contract documentation only when evidence warrants it.
- Templates make the standard actionable without turning copied boilerplate into
  organization policy.

### Negative

- Existing repositories must record profile adoption and close structural gaps
  over time.
- Reviewers must still verify As-built claims against their owning evidence;
  structural conformance cannot prove factual accuracy.
- Profile and template evolution requires compatibility and migration
  discipline.
- Mixed-purpose repositories must maintain an explicit authority map to prevent
  engineering documents from claiming unrelated domain authority.

## Alternatives considered

### Require only a repository-local architecture current view

Rejected because a mixed-purpose repository may contain an independently
governed engineering layer beside scientific or empirical canonical artifacts.
The engineering-system boundary, not the Git repository alone, is the relevant
unit.

### Treat every canonical document as part of arc42

Rejected because code, schemas, generated APIs, runbooks, scientific papers, and
experiment verdicts have different ownership and lifecycle semantics.

### Require a separate full arc42 corpus for every component

Rejected because directory and process boundaries do not establish independent
architecture. It would make documentation more complex than the system.

### Publish guidance without templates or validation

Rejected because each repository would recreate filenames, metadata, state
rules, and checks, preserving the fragmentation this decision is intended to
remove.

## Adoption status

The organization standard, templates, and reference tooling are As-built in the
`.github` repository. Individual repository conformance remains owned and
reported by each participating repository.
