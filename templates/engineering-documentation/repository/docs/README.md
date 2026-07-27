# {{SYSTEM_NAME}} documentation

This directory is the repository-local documentation entry point for
**{{SYSTEM_NAME}}**.

## Authority model

1. [`architecture/`](./architecture/README.md) is the canonical engineering
   current view for **{{SCOPE}}**.
2. Executable code, tests, schemas, generated contracts, configuration, and
   deployment manifests are authoritative for implemented behavior.
3. [`decisions/`](./decisions/README.md) preserves why consequential choices
   were made. Accepted ADRs are historical records; the consolidated current
   view remains in the architecture corpus.
4. Development guides own normal contributor procedures.
5. Runbooks own production diagnosis, recovery, rollout, and rollback.
6. Dated validation records own reproduced evidence and its limitations.
7. Planning systems, pull-request discussion, chat history, and agent sessions
   are supporting provenance, not canonical engineering architecture.

<!-- Add scientific, empirical, legal, product-policy, or other domain-specific
authorities when this is a mixed-purpose repository. State explicitly what the
engineering arc42 corpus does not own. -->

When sources conflict, identify the concern, verify its owning evidence, correct
the canonical owner, and replace duplicate non-owning detail with a link or
explicit state label.

## State vocabulary

- **As-built:** verified current repository, executable, generated, or observed
  behavior.
- **Target:** accepted direction that is not fully implemented.
- **Open:** unresolved or unverified and unsafe to treat as implemented.
- **Deprecated:** historical or transitional behavior that is no longer the
  active direction.

ADR lifecycle terms are separate: `Proposed`, `Accepted`, `Superseded`,
`Deprecated`, and `Rejected`.

## Navigation

- [Architecture](./architecture/README.md)
- [Architecture decisions](./decisions/README.md)

<!-- Add development, runbook, validation, generated-contract, and subsystem
indexes when they exist. -->

## Reading guide

| Goal | Required reading |
| --- | --- |
| Understand the system | Architecture chapters 1, 3, 4, and 5 |
| Change runtime behavior | Chapters 2, 5, 6, 8, and 10 |
| Change deployment | Chapters 3, 6, 7, 8, and 10 |
| Revisit a consequential choice | Chapter 9 and `decisions/` |

## Documentation completion rule

An architecture-significant change is incomplete when its implementation lands
without updating affected canonical documentation. In the same change:

- update the relevant architecture current view;
- add or supersede an ADR for a consequential, hard-to-reverse decision;
- update generated contracts through their owning workflow;
- update runbooks when operator action or recovery changes;
- record dated validation evidence when a stable claim depends on a reproduced
  observation; and
- promote Target to As-built only after verifying its owning evidence.
