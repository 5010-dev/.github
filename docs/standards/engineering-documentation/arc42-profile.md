# 5010 arc42 profile

Profile identifier: **`5010-arc42-v1`**

## L0 whole-system structure

The canonical engineering current view MUST cover the following arc42-aligned
chapters. The recommended filenames are normative for new adoptions and SHOULD
be retained during migration to preserve links.

| # | Recommended file | Required concern |
| --- | --- | --- |
| 1 | `01-introduction-goals.md` | Purpose, stakeholders, goals, and top quality goals |
| 2 | `02-constraints.md` | Technical, organizational, regulatory, and operating constraints |
| 3 | `03-context-scope.md` | System scope, external context, interfaces, and non-goals |
| 4 | `04-solution-strategy.md` | Fundamental solution choices and dependency direction |
| 5 | `05-building-block-view.md` | Static responsibilities, ownership, and building-block relationships |
| 6 | `06-runtime-view.md` | Normal, degraded, failure, recovery, and shutdown scenarios |
| 7 | `07-deployment-view.md` | Runtime units, infrastructure topology, release, and rollback boundaries |
| 8 | `08-crosscutting-concepts.md` | Security, identity, configuration, observability, consistency, and other cross-cutting rules |
| 9 | `09-architecture-decisions.md` | Current-view decision index and links to accepted ADR history |
| 10 | `10-quality.md` | Quality scenarios, validation expectations, and evidence ownership |
| 11 | `11-risks-technical-debt.md` | Known risks, debt, open decisions, and mitigation ownership |
| 12 | `12-glossary.md` | Stable domain and architecture terminology |

Each corpus MUST have an architecture index. A newly scaffolded index uses:

```text
Authority: **Canonical**
Scope: **<the engineering system or independently governed layer>**
Organization profile: **5010-arc42-v1**
```

Each chapter MUST declare a default state near its title:

```text
State: **As-built | Target | Open | Deprecated**
```

An architecture document MAY contain mixed states when individual sections
override the default explicitly. `Canonical` describes authority; it is not an
implementation state.

## State vocabulary

| State | Meaning | Required treatment |
| --- | --- | --- |
| **As-built** | Verified current repository, executable, generated, or observed behavior | Link the owning evidence and avoid generalizing beyond it. |
| **Target** | Accepted direction that is not fully implemented | Identify the remaining gap, implementation owner, and promotion condition. |
| **Open** | Unverified, undecided, or intentionally deferred | State what evidence or decision would close it. |
| **Deprecated** | Historical or transitional behavior that is no longer the active direction | Link the replacement or retention rule. |

ADR lifecycle terms such as `Proposed`, `Accepted`, `Superseded`, `Deprecated`,
`Rejected` are separate from architecture state. An accepted ADR MAY describe a
Target whose implementation remains incomplete.

## Documentation layers

### L0: system architecture

L0 treats internal systems as black boxes and owns whole-system goals,
boundaries, end-to-end scenarios, topology, quality outcomes, and systemic
risks.

### L1: independently reviewable architecture

L1 is added only when a subsystem or boundary has independently reviewable
responsibilities and failure, security, lifecycle, change, contract, or quality
complexity. L1 documents MUST link back to the L0 current view and MUST NOT copy
neighboring internals.

The organization provides three optional subsystem profiles:

| Profile | Intended use | Recommended documents |
| --- | --- | --- |
| **Compact** | A bounded component with modest internal structure | `README.md`, `architecture.md`, `quality-risks.md` |
| **Standard** | A subsystem with durable state, command, trust, or recovery behavior | Compact plus dedicated runtime/security and decision views |
| **Full** | An independently deployed or restarted failure domain with substantial internal architecture | Goals/context, building blocks, runtime, deployment, cross-cutting, quality/risks, and decisions |

Profile selection changes documentation depth, not system architecture. A
profile SHOULD be promoted when its grouping obscures ownership or review.

Stable semantics between independently governed systems belong in a boundary
contract. A boundary contract SHOULD cover ownership, source of truth,
compatibility, ordering, delivery, retry, idempotency, readiness, staleness,
failure, and security without copying complete generated inventories.

### L2: implementation, operation, evidence, and design

L2 remains closest to executable work:

- app, package, and construct READMEs;
- development guides and handbooks;
- production runbooks;
- generated APIs and schemas;
- configuration models and examples;
- design-system screen contracts;
- dated validation evidence; and
- executable code, tests, manifests, and observed runtime state.

L2 documents MAY summarize architectural context for orientation but MUST link
to L0 or L1 for the canonical architecture explanation.

## Stable and volatile information

Architecture SHOULD record stable responsibility, boundary, invariant,
compatibility, failure, recovery, quality, and risk information. It SHOULD link
to rather than copy volatile endpoint lists, environment-variable inventories,
resource identifiers, exact thresholds, dependency versions, generated
schemas, or implementation symbol inventories.

A small implementation pointer is useful evidence. A second prose copy of the
source tree is not.
