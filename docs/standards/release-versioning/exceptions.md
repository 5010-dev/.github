# Adoption and exceptions

Standard publication establishes the target contract. It does not assert that
an existing repository conforms and does not authorize repository migration or
release-history rewriting.

## New release units

A new release unit MUST select its artifact profile, version or record-identifier
source, exact identity, lifecycle or research status, evidence, and automation
boundary before its first Stable release, production deployment, external
research publication, or immutable research-record finalization. It SHOULD begin
with the full target contract rather than creating a planned exception for work
that has not yet shipped or been finalized.

## Existing release units

Existing repositories adopt through repository-owned, reviewable work.

- The owning repository evaluates current consumers, published history,
  registry constraints, active changes, and release risk.
- Adoption MUST preserve published and finalized history and SHOULD apply the
  standard from the next safe release or immutable research boundary.
- A repository MUST NOT renumber compatible existing releases merely to resemble
  a preferred scheme.
- Existing native-client build numbers, store records, research snapshots,
  experiment runs, persistent identifiers, and published data or model identities
  MUST NOT be renumbered, rewritten, or recreated merely to conform to a new
  profile.
- Adoption MUST NOT fabricate unavailable historical lineage or provenance.
  Unknown historical fields remain explicitly unknown, and the full evidence
  contract applies from the next safe release or immutable research boundary.
- Exact migration tasks, current versions or research-record identifiers,
  current support or research status, and adoption status remain local.
- An organization-wide migration program requires a separate approved scope and
  MUST NOT be inferred from this standard.

Repository adoption SHOULD link this standard and document only local release
units, version or record-identifier sources, tag or snapshot format, registries
or archives, commands, workflow locations, support or research-status lines,
lineage policy, current migration state, and exceptions. It MUST NOT copy this
standard into repository documentation.

## Exception record

An exception MUST be explicit, reviewable, time-bounded where remediation is
possible, and stored with the affected repository or release unit. It MUST
record:

- affected release unit, artifact profile, version line or research-record
  identity and status, and rule;
- owner and approval authority;
- reason and affected consumers;
- risk and failure mode;
- compensating evidence or controls;
- migration, correction, or exit condition;
- approval date and review or expiry date; and
- links to related compatibility, scientific-scope, correction, supersession,
  deprecation, or incident evidence.

An exception MUST NOT permit a release or research record to claim an identity,
compatibility level, scientific status, publication state, or verification result
that has not been established. It MUST NOT overwrite a published or finalized
identity or reuse it for different content.

An exception MUST NOT convert tag-only, registry-only, conflicting, or completed
immutable package publication into the protected package-tag profile's
pre-mutation same-version recovery path. That path is available only through its
normal PR-mediated authorization while both immutable identities are absent.

A `SHOULD` deviation MAY be documented in normal repository decision, release,
or research records when the rationale and impact are clear. A `MUST` or `MUST
NOT` deviation requires an explicit approved exception before publication or
finalization unless an emergency makes prior approval impossible.

## Emergency exception

An emergency MAY authorize a bounded deviation required to contain a security,
legal, privacy, regulatory, or integrity incident. The operator MUST record the
scope, action, reason, affected consumers, replacement, approval or emergency
authority, and follow-up review as soon as it is safe to do so.

Emergency handling does not authorize version, artifact, or research-record
identifier reuse, fabricated evidence, or an undocumented permanent policy
change. The follow-up review MUST either close the deviation, create a normal
time-bounded exception, or propose a change to this standard.

## Closing an exception

The owner closes an exception only after verifying the exit condition against
the affected release, research record, or workflow. Expiry without verification
is a failed exception, not automatic conformance. A policy change that makes an
exception obsolete SHOULD link the superseding standard version or decision.
