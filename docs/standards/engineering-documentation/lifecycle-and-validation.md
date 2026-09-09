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

## Diagram authoring and review

For new or substantively revised diagrams in the
[contract's scope](./contract.md#engineering-diagrams), use this authoring
sequence:

1. Define the reader's question, diagram scope, and owning canonical section.
2. Read the relevant contracts, code, schemas, configuration, and observation
   evidence. Distinguish verified behavior from Target or Open claims.
3. Model participants, relationships, conditions, ordering, states, and
   invariants before arranging the visual layout. Compare revisions with the
   previous explanation to detect lost meaning.
4. Compose a readable main path and the static explanation; add focused views,
   evidence links, and supporting explanations where they answer real questions.
5. Validate, regenerate affected artifacts through the repository-owned path,
   and review the final static figure and HTML when provided. Include the source,
   artifacts, and applicable evidence in the same change.

For maintenance that changes only generation, viewer behavior, layout,
navigation, or evidence links, apply the relevant regeneration and review
checks below to the affected surface. Architectural meaning need not change to
trigger those checks; tool conversion and repeating unchanged authoring steps
are not required.

### Evidence and regeneration

Authors MUST verify that cited evidence supports the named claim. For a link
with a revision and line range, read those lines at that exact revision; current
working-tree line numbers are not evidence for a historical link. A valid link
or a renderer's repository check alone does not establish semantic accuracy.

For generated HTML, repositories MUST record the exact generator version
or immutable revision and the HTML regeneration command in a reproducible
repository-local location. Any viewer corrections MUST be tracked as inputs to
that generation path.

For Archify, document static SVG export separately: identify the source HTML
and exported SVG by revision or hash, and record the export procedure or script
command and options needed to repeat it. A documented viewer export is sufficient; a
separate SVG CLI or custom exporter is not required. Inspect the exported SVG
in its document embedding context to verify that styles and essential meaning
remain intact without the HTML viewer.

Use a repository-owned check or a documented regeneration/export comparison
to detect stale source, generated artifacts, and navigation. Mermaid rendered
directly by the documentation platform does not require a separate generator
or build command. For separately generated Mermaid artifacts, record the exact
generator version or immutable revision and the regeneration command. The
organization does not prescribe a tool version, manifest format, checksum
scheme, receipt filename, or shared runtime implementation.

A generator, correction, or export-procedure change MUST regenerate or
re-export and recheck affected outputs.
Review evidence MUST identify the inspected artifact by revision or hash and
record its method, scope, result, and unresolved findings. When an artifact
changes, prior review MUST NOT automatically carry forward: verify identity or
state the unchanged scope for which earlier evidence remains applicable and
review the changed surface.

### Distinct verification claims

Authors MUST distinguish these claims in the change's evidence:

| Check or review | Establishes within its recorded scope | Does not establish |
| --- | --- | --- |
| Generation and structural validation | Source validity, successful generation, tool diagnostics, source/output consistency | Factual accuracy or visual readability |
| Code and document review | Meaning, state, and relationship alignment with owning evidence | Browser behavior or current production acceptance |
| Automated browser inspection | Measurements and behavior exercised against the exact final HTML | Complete perceptual or semantic review |
| Visual and interaction review | Readability and behavior actually inspected in the rendered artifact | Untested viewports, browsers, or interactions |

An inapplicable check MAY be recorded as `N/A` with a reason. For example, a
check of separately delivered HTML can be `N/A` for platform-rendered Mermaid;
semantic and rendered-readability review still apply. Environmental failures
or unavailable inspection are not `N/A`.

Perform automated validation and semantic review appropriate to the change,
then inspect actual rendering. When HTML is provided, inspect that final HTML
in a browser as well as the static figure; static SVG inspection does not cover
viewer layout or interaction. Modeled layout or focus tests are not browser
evidence. Tool-specific checks, including Archify delivery and browser receipts,
retain their own scope and outcome; passing one check MUST NOT imply another
passed.

For environmental failures or unavailable inspection, record the actual result,
reason, and untested scope. A failed, blocked, or unperformed check MUST NOT be
reported as passed. Automated validation can pass while visual defects remain
open; record those defects explicitly rather than claiming complete acceptance.

### Reading and interaction checks

Reviewers MUST check the changed surface for readable labels, unambiguous arrow
directions and endpoints, and clear boundaries. Inspect supported themes and
representative viewport sizes for the intended reading context. When HTML is
provided, check long detail panels, keyboard access, focus, navigation, and the
adopted exploration and export features affected by the change.

Long content MUST remain accessible to the end. Resizing MUST NOT clip required
content or cause persistent alternating shrink/expand behavior. Natural page or
detail-panel scrolling is allowed when needed. Authors MUST NOT hide content or
reduce it to unreadable size merely to fit one screen or pass a measurement.

Choose viewport coverage and tool quality profiles appropriate to the artifact;
fixed viewport dimensions, card counts, and viewer patches are not organization
requirements. Use existing pull-request or validation-record facilities for
review evidence. This workflow does not require a new receipt bundle, approval
stage, cross-service E2E gate, or central validation service for every diagram,
and MUST NOT turn unrelated maintenance into a viewer installation or exhaustive
browser-testing task.

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
