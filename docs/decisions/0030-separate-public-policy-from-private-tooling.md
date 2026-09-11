# ADR-0030: Separate public policy from private tooling

- Status: Accepted
- Date: 2026-09-12
- Owners: `5010-dev/.github` and `5010-dev/engineering-tooling` maintainers

## Context

ADR-0022 retired the central Go Golden Path executable and its managed consumer
footprint. Its whole-repository archive wording also encompassed the later
active developer-installed Agent and the accepted development/operations tooling
monorepo. That is broader than the executable retirement now intended.

## Decision

Keep `.github` public as the organization policy, standard, guide, and copy-once
example repository. Make `engineering-tooling` private and retain it as the
active development and operations tooling monorepo. Packages own their runtime,
user interfaces, versions, support, and publication; repository-local commands
and workflows own development and delivery.

Narrow ADR-0022 decision 6 to the retired Go `golden-path` releases `v0.1.0`
through `v1.6.1` and their audit artifacts. Supersede only the whole-repository
archive instruction in decision 7. Preserve published history. The Agent and
other independent tooling packages are not retired by ADR-0022.

The active central executable control plane remains `none`. This decision does
not restore a locator, generated consumer footprint, shared conformance runner,
organization queue, or central execution of consumer CI. An explicitly invoked
local Agent remains guidance support under its existing contract.

Public policy links may point to private implementation evidence that requires
repository access. Package read permissions remain separate from source access.
Private tooling security reports follow the tooling repository's current
security policy; public-only private vulnerability reporting is not its route.
General support remains Engineering Linear intake.

## Consequences

The repository continues evolving without conflating its retired Go artifact
line with its active packages. Repository-owned canonical architecture and ADRs
record package layout and the staged publication implementation; those details
do not become organization-wide standards or consumer obligations.

This corrects the source/retirement scope and support route without changing the
Developer Tooling Standard's executable conformance rules or contract version.
