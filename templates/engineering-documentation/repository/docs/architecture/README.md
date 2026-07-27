# {{SYSTEM_NAME}} architecture

Authority: **Canonical**

Scope: **{{SCOPE}}**

Organization profile: **{{PROFILE_ID}}**

This corpus is the canonical engineering current view for the declared scope.
It links to executable, generated, operational, observed, and domain-specific
authorities instead of copying their complete inventories.

## Contents

1. [Introduction and goals](./01-introduction-goals.md)
2. [Constraints](./02-constraints.md)
3. [Context and scope](./03-context-scope.md)
4. [Solution strategy](./04-solution-strategy.md)
5. [Building-block view](./05-building-block-view.md)
6. [Runtime view](./06-runtime-view.md)
7. [Deployment view](./07-deployment-view.md)
8. [Cross-cutting concepts](./08-crosscutting-concepts.md)
9. [Architecture decisions](./09-architecture-decisions.md)
10. [Quality requirements](./10-quality.md)
11. [Risks and technical debt](./11-risks-technical-debt.md)
12. [Glossary](./12-glossary.md)

## Reading guide

Start with chapters 1, 3, and 4 for purpose, boundary, and strategy. Chapters 5
and 6 explain responsibilities and significant runtime scenarios. Chapters 7
and 8 cover topology and cross-cutting contracts. Chapters 9 through 11 cover
decisions, quality, evidence expectations, and remaining risk.

## Scope boundary

<!-- State what this corpus owns and explicitly does not own. For a mixed-purpose
repository, link scientific, empirical, legal, or product-policy authorities
that remain outside the engineering architecture. -->

## Architecture depth

The numbered chapters are the L0 whole-system view. Add L1 subsystem or boundary
documents only when independent responsibility, failure, security, lifecycle,
contract, change, or quality complexity makes L0 and local READMEs insufficient.
