# Developer Tooling Golden Path

- Status: Supported
- Model: Contract-backed, repository-owned
- Owner: `5010-dev/.github` maintainers
- Last reviewed: 2026-08-14
- Review by: 2027-02-11
- Support: [create an Engineering issue in Linear](https://linear.new?team=ENG) for triage by the `engineering-tooling` maintainers

Linear is the support intake and work-tracking system. Reviewed source at
`5010-dev/.github@main` remains the policy and Golden Path authority.

The Developer Tooling Golden Path is the recommended, supported route from a
repository's actual needs to a working repository-owned developer experience.
It explains how to apply the
[Developer Tooling Standard](../standards/developer-tooling/README.md) without
turning the organization repository into an execution control plane.

## Authority boundary

| Layer | Responsibility |
| --- | --- |
| Developer Tooling Standard | Normative cross-repository requirements: what must be true |
| Golden Path | Opinionated journeys, defaults, examples, and checklists: the supported way to get there |
| Repository implementation | Manifests, locks, Just recipes, workflows, releases, and observed evidence: executable As-built authority |

If guidance conflicts with the standard, the standard wins. If a reference
example differs from working repository-owned configuration, inventory the
repository and change only what is required by the standard. Another
repository's implementation is evidence of one valid shape, not a template
authority.

## Supported journeys

- [Bootstrap](../guides/bootstrap-new-repository.md) starts a new repository
  from its real language, artifact, infrastructure, and release needs.
- [Adoption](../guides/adopting-developer-tooling.md) closes concrete gaps in an
  existing repository while preserving native authorities.
- [Executable-footprint retirement](../guides/migrating-developer-tooling.md)
  removes the former control plane without removing repository-owned behavior.
- [Agent-assisted application](./agent.md) uses an explicitly invoked,
  exact-version developer tool to prepare a bound plan and apply only an
  approved repository-owned change.
- [Stack defaults](./stack-defaults.md) map common Node.js/TypeScript, Go,
  Python, Rust, and polyglot shapes to the applicable standard profiles.
- [Reference examples](./reference-examples.md) provide small copy-once
  snippets for toolchain selection, Just, CI, dependency automation, security
  routing, native roots, and exceptions.
- [Release readiness](./release-readiness.md) checks only the merge, release,
  deployment, and security boundaries a repository actually has.

## Copy-once support contract

Reference examples are not installed, vendored, synchronized, or upgraded by
the organization repository. Copy only an applicable snippet, replace its
explicit choices, and review it through the owning repository. Whether a file
is copied manually or written by an explicitly approved Agent `apply`, it is
immediately repository-owned source. A later Golden Path documentation or Agent
package change does not create a managed regeneration, upgrade campaign, or
automatic consumer pull request.

The Golden Path does not provide a locator, binary, generator/upgrader, managed
file boundary, reusable conformance workflow, adoption registry, live
organization report, dependency queue compiler, release-unit impact inference,
security-closure orchestrator, or central approval queue. The optional
developer-invoked Agent does not alter this boundary: repositories and CI do not
select it, and its bounded copy-once `apply` neither manages consumer files nor
provides a generated upgrade lifecycle.

## Getting support

For a repository-specific implementation problem, use that repository's normal
issue or pull request flow and involve its owner. For a gap or ambiguity in the
shared journey, [create an Engineering issue in
Linear](https://linear.new?team=ENG) with the affected stack, repository shape,
standard section, observed failure, and the smallest example that reproduces
it. The `engineering-tooling` maintainers triage the issue with the relevant
owner. A proposed normative change belongs in the standard; an example-only
improvement stays in the Golden Path.
