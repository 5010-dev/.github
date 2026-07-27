# Engineering documentation contract

Organization profile: **`5010-arc42-v1`**

## Purpose

This contract makes engineering architecture discoverable, reviewable, and
maintainable without forcing every kind of canonical knowledge into one
document tree. Arc42 provides the canonical engineering-documentation spine;
concern-specific authorities remain with the artifacts that own those facts.

## Applicability

An engineering system that is owned within the `5010-dev` organization MUST
adopt the [organization arc42 profile](./arc42-profile.md) when either:

1. the repository's primary purpose is to build, operate, or distribute that
   engineering system; or
2. a mixed-purpose repository contains an independently governed engineering
   layer.

An independently governed engineering layer has an explicit responsibility
boundary and at least one distinct lifecycle, failure or recovery boundary,
security or authority boundary, deployment boundary, change cadence, stable
cross-boundary contract, or set of quality requirements.

A package, crate, process, provider, model, directory, or team boundary MUST NOT
be treated as a separate engineering system solely because it exists. Detail
that remains understandable within a parent system belongs in a local README or
an L1 profile under that system's arc42 corpus.

Repositories that contain only organization governance, community defaults, or
canonical standards MAY act as the source of this contract without describing
themselves as a product engineering system.

## Canonical documentation spine

Each in-scope engineering system MUST provide a repository-local documentation
entry point and a canonical arc42 current view. That spine owns:

- engineering goals, stakeholders, and constraints;
- system and responsibility boundaries;
- solution strategy and stable invariants;
- building-block, runtime, and deployment views;
- cross-cutting concepts and cross-boundary semantics;
- quality requirements and evidence expectations;
- architectural risks, technical debt, and open decisions;
- the accepted target state and its distinction from As-built behavior; and
- navigation to the concern-specific authorities that substantiate the view.

The spine MUST remain understandable without access to Linear, pull-request
discussion, chat history, an agent session, or local machine state.

## Concern-based authority

Arc42 MUST NOT become a second source tree or silently override another
canonical owner. Repositories MUST identify the authority for each relevant
concern, including as applicable:

| Concern | Typical canonical owner |
| --- | --- |
| Implemented behavior | Executable code, tests, schemas, and configuration |
| Generated API or message shape | Generated contract or schema |
| Current deployment resources | Deployment manifests, infrastructure code, and observed platform state |
| Production diagnosis and recovery | Runbook |
| Dated verification result | Validation record and reproducible evidence |
| Scientific intent | Scientific design or paper |
| Experiment design and verdict | Owning preregistration, findings, or synthesis artifact |
| Consequential decision rationale | Accepted ADR |
| Repository architecture current view | The adopted arc42 corpus |

When sources disagree, authors MUST identify the concern, verify the owning
evidence, correct the canonical owner, and replace duplicate non-owning detail
with a link or explicit state label.

## Required repository capabilities

An adopted system MUST provide:

1. `docs/README.md` or an equivalent repository-local documentation index;
2. a canonical arc42 corpus that implements all L0 chapters in the organization
   profile;
3. an explicit system scope and adopted profile identifier;
4. a concern-based authority map;
5. the shared As-built, Target, Open, and Deprecated state vocabulary;
6. an indexed ADR system that preserves accepted decision history;
7. a documentation completion rule for architecture-significant changes;
8. repository-local validation for structure, status, indexes, and links, or an
   equivalent organization-approved check; and
9. links to organization standards and platform contracts instead of copied
   normative text.

The physical architecture root SHOULD be `docs/architecture/`. A mixed-purpose
repository MAY use another stable path when multiple engineering systems would
otherwise collide, but the repository documentation index MUST make each scope
and authority discoverable.

## Mixed-purpose repositories

A mixed-purpose repository MUST preserve domain-specific canonical authorities.
For example, a research repository may keep its scientific paper and
phase-local empirical artifacts as scientific authorities while applying arc42
only to its research-operation or implemented-engineering layer.

The engineering arc42 corpus MUST state what it does not own. It MUST NOT claim
scientific, legal, product-policy, or empirical authority merely because those
artifacts share a repository.

## Local exceptions

A repository MAY deviate from a file location, profile depth, or validation
mechanism when the standard outcome is preserved. A material exception MUST:

1. state the exact rule being replaced;
2. explain why the default does not fit the engineering system;
3. identify the replacement authority or validation;
4. record consequences and a review condition in an ADR or equivalent durable
   review; and
5. link the exception from the repository documentation index.

An exception MUST NOT weaken concern-based authority, state honesty, decision
history, or the ability to locate the canonical engineering current view.
