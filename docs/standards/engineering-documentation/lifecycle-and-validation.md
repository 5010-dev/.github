# Documentation lifecycle and validation

Organization profile: **`5010-arc42-v1`**

## Adoption

New engineering systems MUST adopt the current organization profile when their
first stable architecture boundary is established. Existing systems SHOULD
migrate through planned documentation work or the next architecture-significant
change; unrelated maintenance MUST NOT be blocked solely to perform a wholesale
documentation rewrite.

Adoption consists of:

1. inventorying current canonical and duplicate sources;
2. defining the engineering-system scope and concern-based authority map;
3. creating the L0 corpus and ADR index;
4. classifying every claim as As-built, Target, Open, or Deprecated;
5. linking executable, generated, operational, scientific, and empirical
   authorities instead of copying them;
6. adding a local documentation completion rule;
7. recording adoption or a material exception in an ADR; and
8. enabling a structural and link-integrity check.

The [adoption guide](../../guides/adopting-arc42.md) and
[migration guide](../../guides/migrating-existing-documentation.md) provide
non-normative procedures.

## Same-change completion

An architecture-significant change is incomplete when its implementation lands
without updating affected canonical documentation. The same change MUST:

- update L0 or L1 when boundaries, responsibilities, invariants, runtime,
  deployment, security, compatibility, quality, or risk change;
- add or supersede an ADR for a consequential, hard-to-reverse decision;
- update a runbook when diagnosis, recovery, rollout, rollback, or operator
  action changes;
- update generated or executable contracts through their owning workflow;
- add dated validation evidence when a stable claim depends on a reproduced
  observation; and
- move completed Target claims to As-built only after their owning evidence is
  verified.

Accepted ADRs are historical records. A later change MUST add a replacement
decision and update the consolidated current view instead of rewriting the
earlier rationale.

## Template lifecycle

Organization templates are scaffold sources, not remotely synchronized
documents. A generated repository owns its adopted files after creation.

Template changes:

- MUST preserve the meaning of the published profile identifier;
- MUST receive a new profile identifier when they introduce an incompatible
  required structure or semantic rule;
- MUST NOT require repositories to remain byte-identical to the template; and
- SHOULD include a migration note when an adopted repository needs action.

Repositories record their adopted profile in the architecture index. A profile
upgrade is explicit and reviewable; updating the organization template does not
silently upgrade existing repositories.

## Minimum validation

An adopted repository MUST run a check that verifies:

1. the documentation index, architecture index, L0 chapters, and ADR index
   exist;
2. the architecture scope and organization profile are declared;
3. every L0 chapter has a recognized default state;
4. ADR lifecycle states are recognized and ADRs are indexed;
5. repository-local Markdown links resolve;
6. unresolved scaffold tokens are absent;
7. trailing whitespace is absent; and
8. repository-specific required documents or profiles are indexed.

The organization [reference checker](../../../scripts/docs/check-contract.sh)
implements the common minimum. A repository MAY use a different language or
tool when it preserves these checks and records any material exception.

Validation proves structural conformance, not factual accuracy. Reviewers must
still compare As-built claims with executable, generated, or observed
authorities and must not treat a passing link checker as deployment evidence.

## Compatibility during migration

Existing paths and anchors SHOULD remain stable while consumers still link to
them. Add and validate the new canonical child before slimming its former
parent. When content moves, preserve a short compatibility explanation and link
at the old location until affected inbound references have migrated.

Historical ADRs, scientific artifacts, and empirical verdicts MUST retain their
original ownership and history.
