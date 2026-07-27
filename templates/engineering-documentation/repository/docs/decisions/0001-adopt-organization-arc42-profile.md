# ADR-0001: Adopt the organization arc42 profile for {{SYSTEM_NAME}}

- Status: Proposed
- Date: {{DATE}}

## Context

{{SYSTEM_NAME}} requires a repository-local canonical engineering current view
that remains understandable without external planning or session history.
Engineering architecture must be discoverable without replacing executable,
generated, operational, observed, or domain-specific canonical authorities.

## Decision

Adopt **{{PROFILE_ID}}** for **{{SCOPE}}**.

The repository will:

1. maintain the L0 arc42 current view under `docs/architecture/`;
2. use As-built, Target, Open, and Deprecated as architecture states;
3. preserve concern-specific authorities and link them from the arc42 corpus;
4. preserve accepted ADRs as decision history;
5. add L1 subsystem or boundary documents only when independent architecture
   complexity justifies them; and
6. run the organization conformance minimum or an equivalent repository-native
   check.

## Consequences

### Positive

- Engineering scope, responsibility, runtime, deployment, quality, and risk
  have one navigable current view.
- Target direction can be distinguished from verified As-built behavior.
- Existing canonical owners retain their authority.

### Negative

- Architecture-significant changes require same-change documentation review.
- The repository must maintain indexes, state labels, links, and validation.

## Adoption status

The generated corpus is an Open skeleton. Change this ADR to `Accepted` only
after repository review confirms the declared scope, authority map, validation
gate, and any local exceptions.
