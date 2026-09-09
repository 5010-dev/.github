# Engineering documentation contract

Organization profile: **`5010-arc42-v1`**

## Purpose

This contract makes engineering architecture discoverable, reviewable, and
maintainable without forcing every kind of canonical knowledge into one
document tree. Arc42 provides the canonical engineering-documentation spine;
concern-specific authorities remain with the artifacts that own those facts.

## Applicability

An engineering system that is owned within the `5010-dev` organization MUST
adopt the [organization arc42 profile](./arc42-profile.md) when either:

1. the repository's primary purpose is to build, operate, or distribute that
   engineering system; or
2. a mixed-purpose repository contains an independently governed engineering
   layer.

An independently governed engineering layer has an explicit responsibility
boundary and at least one distinct lifecycle, failure or recovery boundary,
security or authority boundary, deployment boundary, change cadence, stable
cross-boundary contract, or set of quality requirements.

A package, crate, process, provider, model, directory, or team boundary MUST NOT
be treated as a separate engineering system solely because it exists. Detail
that remains understandable within a parent system belongs in a local README or
an L1 profile under that system's arc42 corpus.

Repositories that contain only organization governance, community defaults, or
canonical standards MAY act as the source of this contract without describing
themselves as a product engineering system.

## Canonical documentation spine

Each in-scope engineering system MUST provide a repository-local documentation
entry point and a canonical arc42 current view. That spine owns:

- engineering goals, stakeholders, and constraints;
- system and responsibility boundaries;
- solution strategy and stable invariants;
- building-block, runtime, and deployment views;
- cross-cutting concepts and cross-boundary semantics;
- quality requirements and evidence expectations;
- architectural risks, technical debt, and open decisions;
- the accepted target state and its distinction from As-built behavior; and
- navigation to the concern-specific authorities that substantiate the view.

The spine MUST remain understandable without access to Linear, pull-request
discussion, chat history, an agent session, or local machine state.

## Concern-based authority

Arc42 MUST NOT become a second source tree or silently override another
canonical owner. Repositories MUST identify the authority for each relevant
concern, including as applicable:

| Concern | Typical canonical owner |
| --- | --- |
| Implemented behavior | Executable code, tests, schemas, and configuration |
| Generated API or message shape | Generated contract or schema |
| Current deployment resources | Deployment manifests, infrastructure code, and observed platform state |
| Production diagnosis and recovery | Runbook |
| Dated verification result | Validation record and reproducible evidence |
| Scientific intent | Scientific design or paper |
| Experiment design and verdict | Owning preregistration, findings, or synthesis artifact |
| Consequential decision rationale | Accepted ADR |
| Repository architecture current view | The adopted arc42 corpus |

When sources disagree, authors MUST identify the concern, verify the owning
evidence, correct the canonical owner, and replace duplicate non-owning detail
with a link or explicit state label.

## Engineering diagrams

### Scope and default authoring tool

Authors SHOULD use the [Archify skill](https://github.com/tt-a1i/archify) for
new or substantively revised architecture, workflow, sequence, data-flow, and
lifecycle/state diagrams in canonical engineering documentation. A substantive
revision changes participants, responsibilities, boundaries, relationships,
conditions, ordering, or failure/recovery meaning. Typographical, link, or
surrounding prose edits alone do not require conversion of an existing diagram.

These authoring rules preserve the existing arc42 corpus structure, authority
map, and state vocabulary. They do not require a new diagram in every document
or layer, wholesale conversion or revalidation of existing diagrams, or a
profile migration. Unrelated maintenance MUST NOT be blocked by diagram
conversion.

The tool-conversion scope above is separate from maintenance review. Changes
to a diagram's generation path, viewer, layout, navigation, or evidence links
MUST receive the applicable
[regeneration and review checks](./lifecycle-and-validation.md#diagram-authoring-and-review)
for the affected surface even when architectural meaning is unchanged. This
does not require tool conversion or revalidation of unaffected diagrams.

### Authority and meaning

The diagram source owns its visual representation; the existing
[concern-based authorities](#concern-based-authority) continue to own the facts
it depicts. A diagram MUST follow its owning section's As-built, Target, Open,
or Deprecated state, with explicit labels for any differing elements or paths.
Authorship, accepted design, or successful rendering MUST NOT imply verified
implementation, deployment, or runtime behavior.

Within its stated scope, a diagram MUST preserve meaningful participants,
responsibilities, boundaries, relationship directions and protocols,
request/response and synchronous/asynchronous distinctions, branch conditions,
ordering, state transitions, failure/recovery behavior, and final invariants.
Authors MUST NOT remove meaningful labels or paths to satisfy layout checks,
invent unverified consumers or recovery paths, or imply a total order between
independent asynchronous events.

Authors MAY split a complex view into linked overview and detail diagrams when
each scope and the location of omitted detail are clear. Essential meaning MUST
remain understandable from the static figure and adjacent prose, without
requiring hover, interaction, or animation. An unsupported notation MAY be
replaced with another representation when responsibility, action, conditions,
and ordering remain explicit; otherwise use the fallback below.

### Artifacts and exploration

For Archify diagrams, authors MUST keep JSON as the editable source, embed a
static SVG in the document, and provide adjacent links to the explorable HTML
and source. HTML MUST be generated from that JSON through the documented
generation path. The static SVG MUST be derived from the exact delivered HTML
through a repository-documented export step, using the viewer's SVG export or
a script. It MUST preserve the diagram's meaning when embedded independently
of the HTML viewer. Authors MUST update the source and affected generated or
exported artifacts in the same change and MUST NOT edit only the generated
HTML or SVG. The
[diagram authoring and review lifecycle](./lifecycle-and-validation.md#diagram-authoring-and-review)
defines regeneration and evidence requirements.

Complex diagrams SHOULD offer question-based Guided Views, role and
responsibility descriptions, named source references, and explanations of
invariants and failure/recovery behavior where these help the reader. The
number of views, cards, nodes, or references is determined by the questions and
scope; no fixed count is an organization requirement.

Repositories MAY provide HTML through existing documentation hosting or explain
how to download and open it locally. A dedicated hosting service is not
required. Organization diagram guidance and examples MUST remain independent
of consumer repository names, paths, implementation code, revisions, and
adoption or review status. Repositories own their generation commands and any
viewer corrections; this standard does not require copying another
repository's runtime or validation implementation.

### Mermaid fallback

Authors MAY use Mermaid when the Archify skill is unavailable, execution is
constrained, required notation is unsupported, or meaning and readability
cannot be adequately preserved through an alternative representation or split
views. Record the reason briefly in the pull request or change description.

This fallback is an allowed choice under the standard, not a material local
exception: it requires no separate ADR, approval, or follow-up conversion issue.
The same authority, state, meaning, readability, and truthful review requirements
apply. Markdown or a dedicated Mermaid file is the editable source; Archify
JSON and HTML artifacts are not required for the fallback.

## Required repository capabilities

An adopted system MUST provide:

1. `docs/README.md` or an equivalent repository-local documentation index;
2. a canonical arc42 corpus that implements all L0 chapters in the organization
   profile;
3. an explicit system scope and adopted profile identifier;
4. a concern-based authority map;
5. the shared As-built, Target, Open, and Deprecated state vocabulary;
6. an indexed ADR system that preserves accepted decision history;
7. a documentation completion rule for architecture-significant changes;
8. repository-local validation for structure, status, indexes, and links, or an
   equivalent organization-approved check; and
9. links to organization standards and platform contracts instead of copied
   normative text.

The physical architecture root SHOULD be `docs/architecture/`. A mixed-purpose
repository MAY use another stable path when multiple engineering systems would
otherwise collide, but the repository documentation index MUST make each scope
and authority discoverable.

## Mixed-purpose repositories

A mixed-purpose repository MUST preserve domain-specific canonical authorities.
For example, a research repository may keep its scientific paper and
phase-local empirical artifacts as scientific authorities while applying arc42
only to its research-operation or implemented-engineering layer.

The engineering arc42 corpus MUST state what it does not own. It MUST NOT claim
scientific, legal, product-policy, or empirical authority merely because those
artifacts share a repository.

## Local exceptions

A repository MAY deviate from a file location, profile depth, or validation
mechanism when the standard outcome is preserved. A material exception MUST:

1. state the exact rule being replaced;
2. explain why the default does not fit the engineering system;
3. identify the replacement authority or validation;
4. record consequences and a review condition in an ADR or equivalent durable
   review; and
5. link the exception from the repository documentation index.

An exception MUST NOT weaken concern-based authority, state honesty, decision
history, or the ability to locate the canonical engineering current view.
