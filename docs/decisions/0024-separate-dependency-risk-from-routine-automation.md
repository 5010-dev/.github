# ADR-0024: Separate dependency risk from routine-update automation

- Status: Accepted
- Date: 2026-08-13
- Owners: `5010-dev/.github` maintainers and repository maintainers
- Normative contract: [Dependency and build hygiene](../standards/developer-tooling/build-hygiene.md)
- Supported guidance: [Golden Path dependency examples](../golden-path/reference-examples.md)

## Context

The Developer Tooling Standard previously recommended weekly routine version
updates and the Golden Path Dependabot example supplied a positive per-entry
pull-request limit. Those settings made one update mechanism look like an
organization operating requirement.

Dependabot applies a pull-request limit to each configured update entry, not to
the repository as a whole. Adding ecosystems and native roots therefore
multiplies the possible routine queue. Creating a pull request also does not
approve, merge, promote, release, or deploy it. Those later effects remain
subject to repository-owned CI, review capacity, branch flow, release units,
and deployment triggers.

Known-vulnerability visibility, unsupported-dependency handling, remediation,
and accepted-risk decisions are security and lifecycle outcomes. Routine
version-update cadence, grouping, queue size, merge, promotion, release, and
deployment are repository-owned DevOps mechanisms. Conflating the two expanded
the Golden Path from supported adoption guidance into an operational control
plane and created work without establishing end-to-end automation.

No single weekly cadence or numeric queue budget was established as suitable
for repositories with different activity, exposure, test confidence, review
capacity, release boundaries, and production effects. A Golden Path example is
not sufficient evidence to create that organization default.

## Decision

1. The Developer Tooling Standard owns dependency-risk outcomes: locked native
   authority, known-vulnerability visibility, remediation or accepted risk,
   dependency lifecycle review, and release safety.
2. Active buildable repositories MUST track and triage known vulnerabilities
   under an approved severity, exploitability, scope, and release-gate policy.
   Findings over that policy's remediation threshold MUST be fixed or covered
   by an approved dependency exception.
3. Repositories SHOULD review dependency drift and upstream support status
   periodically. Each repository selects its cadence from actual activity,
   exposure, runtime criticality, test confidence, review capacity, and release
   or deployment effects.
4. Automated routine version-update pull requests are an opt-in MAY. There is
   no organization-wide weekly cadence or numeric pull-request budget.
5. When routine automation is enabled, the repository owns actual native roots,
   one adapter per dependency surface, target branch, cadence, grouping,
   bounded positive per-entry limits, CI, review, merge, promotion, release,
   deployment, and current evidence.
6. A repository MAY keep a stable security-only Dependabot configuration with
   routine version-update limits set to `0`. The absence of routine automation
   alone does not require an expiry or exit condition; security visibility and
   an owned dependency-review and update path remain required.
7. Security remediation MUST remain independent from routine batching, freezes,
   positive limits, or opt-out decisions.
8. The Golden Path provides a security-only copy-once starting example and
   explains repository opt-in. It does not own routine queue throughput,
   approval, promotion, release, or deployment.
9. Higher dependency-operations automation maturity is a separate,
   evidence-driven DevOps capability decision. It is neither a Golden Path
   obligation nor deferred completion work for this decision and requires a
   separate repository-backed decision before implementation.

## Consequences

- Security accountability remains mandatory and periodic dependency-lifecycle
  review remains expected even when a repository chooses not to generate
  routine version-update pull requests.
- Repository teams may adopt Dependabot, Renovate, grouping, cooldowns,
  automerge, or other delivery automation when their tests, review capacity,
  and release boundaries support it.
- A pilot or reference configuration does not create an organization rollout or
  a consumer upgrade obligation.
- No central dependency compiler, live organization report, approval queue,
  merge service, consumer CI replay, or deployment coordinator is created.
- Future DevOps automation work starts only from a separate repository-owned
  decision and does not reopen this Golden Path boundary by implication.

## Alternatives considered

### Keep weekly updates and a positive limit as organization defaults

Rejected because one cadence and per-entry limit do not establish a bounded
repository queue or fit different review, release, and deployment boundaries.

### Disable dependency maintenance

Rejected because vulnerability visibility, risk-based remediation, and
periodic lifecycle review remain required or expected outcomes.

### Build a central queue, compiler, or approval service

Rejected because repositories already own manifests, locks, CI, reviewers,
branches, release units, and deployment effects. A central execution layer would
duplicate those authorities and recreate the coordination cost retired by
[ADR-0022](./0022-retire-golden-path-executable-tooling.md).

### Require mature end-to-end routine automation now

Rejected as a Golden Path requirement. It is a DevOps capability that must be
designed from demonstrated repository demand, tests, risk, review capacity, and
delivery boundaries rather than inferred from a reference configuration.

## Authority and evidence boundary

This ADR and the linked repository standards are the authority for the
decision. Git history preserves the superseded weekly and positive-limit source
as development history. External planning systems are neither authority nor
evidence. This decision creates no organization snapshot, evidence repository,
or retention obligation; current operational state is observed from its owning
repositories when needed.

Boundary classification: released policy — Standard `2026.08.8` supersedes
`2026.08.7`; no runtime compatibility or migration path applies because this
decision changes no wire contract, durable state, released artifact, or
mixed-version deployment.
