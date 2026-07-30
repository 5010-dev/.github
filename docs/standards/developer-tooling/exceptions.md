# Golden Path exceptions

- Status: Accepted
- Standard version: `2026.07`
- Schema: [`golden-path-exceptions/v1`](./schemas/golden-path-exceptions-v1.schema.json)

An exception is a repository-local, reviewable, time-bounded waiver for one or
more waivable MUST rules. It does not change the rule, runtime lifecycle,
organization disposition, or another repository's conformance.

## Common requirements

Every exception MUST include:

- a stable unique exception ID;
- one or more stable MUST rule IDs;
- the minimum affected profile, artifact, capability, and/or path scope;
- a bounded reason;
- an accountable owner;
- at least one approval authority, durable reference, and approval date;
- a risk class; and
- an expiry date.

An exception MUST NOT:

- suppress every rule or the entire repository without a bounded scope;
- apply to a rule marked `waivable: false`;
- waive a SHOULD recommendation;
- be permanent, self-approved, pending, or schema-invalid;
- hide its original finding from output; or
- contain secrets, personal contact data, or sensitive operational details.

A valid exception changes an applicable finding to `waived`. An invalid or
expired exception leaves the violation failing. Approaching expiry produces a
warning.

## High-risk exceptions

An exception is high risk when it affects security, deployment, supply chain, a
destructive/state-repair operation, or a catalog rule marked `highRisk: true`.
It additionally MUST include:

- a current risk statement;
- at least one compensating control;
- a remediation tracking issue; and
- approval from both the Developer Tooling owner and the affected domain owner.

The requester and two-person approvers MUST be meaningfully independent where
the underlying rule requires two-person control.

A general tooling exception needs a tracking issue only when actual remediation
work is planned. A bounded, accepted variation SHOULD NOT create a ceremonial
issue.

## Renewal

Renewal is a new review. It MUST reassess reason, scope, current state, owner,
and expiry. A high-risk renewal also reassesses risk, controls, tracking, and
independent approvals.

Repeated renewal of the same rule and reason is a signal to propose a profile
or standard change rather than extending dates indefinitely.

## Hosting-platform enforcement

CODEOWNERS, protected review, or rulesets MAY technically enforce approval only
on hosting plans that support them. A GitHub Free private repository records PR
review or other durable approval evidence without claiming that the platform
enforced it.

The repository owns its exception file and history. No central exception list is
maintained.

Rule IDs: `DT-EXC-*`.
