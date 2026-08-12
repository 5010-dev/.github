# Golden Path exceptions

- Status: Accepted
- Standard version: `2026.08.8`

An exception is a repository-local, reviewable, time-bounded waiver for one or
more waivable MUST rules. It does not change the rule, runtime lifecycle,
organization disposition, or another repository's conformance.

## Common requirements

Every exception MUST include:

- a stable unique exception ID;
- one or more exact normative document and section references;
- the minimum affected profile, artifact, capability, and/or path scope;
- a bounded reason;
- an accountable owner;
- at least one approval authority, durable reference, and approval date;
- a risk class; and
- an expiry date.

A finding evaluated at an explicit native dependency root is identified by its
native profile and repository-relative finding path. An exception for such a
finding MUST use profile and/or path scope; artifact-type or capability scope
does not identify a dependency root because those dimensions describe
repository behavior rather than native dependency authority.

An exception MUST NOT:

- suppress every rule or the entire repository without a bounded scope;
- waive a SHOULD recommendation;
- be permanent, self-approved, pending, or structurally incomplete;
- hide its original finding from output; or
- contain secrets, personal contact data, or sensitive operational details.

A valid, unexpired exception makes the bounded requirement waived for its
declared scope. An expired, structurally invalid, semantically invalid, unknown,
or non-waivable reference is not an accepted exception. Evaluation uses an
explicit review or CI timestamp; do not hide expiry behind an implicit local
clock or a permanently passing check.

## High-risk exceptions

An exception is high risk when it affects security, deployment, supply chain,
or a destructive/state-repair operation.
It additionally MUST include:

- a current risk statement;
- at least one compensating control;
- a remediation tracking issue; and
- approval from both the Developer Tooling owner and the affected domain owner.

The requester and two-person approvers MUST be meaningfully independent where
the underlying rule requires two-person control.

Repository review MUST apply the high-risk classification from the affected
human-readable rule and domain boundary. Repository self-classification cannot
lower an applicable security, deployment, supply-chain, or destructive-state
risk.

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

The repository owns its exception record and history. No central exception list
is maintained.
