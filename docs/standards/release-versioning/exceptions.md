# Adoption and exceptions

Standard publication establishes the target contract. It does not assert that
an existing repository conforms and does not authorize repository migration or
release-history rewriting.

## New release units

A new release unit MUST select its artifact profile, version source, exact
identity, lifecycle, evidence, and automation boundary before its first stable
or production publication. It SHOULD begin with the full target contract rather
than creating a planned exception for work that has not yet shipped.

## Existing release units

Existing repositories adopt through repository-owned, reviewable work.

- The owning repository evaluates current consumers, published history,
  registry constraints, active changes, and release risk.
- Adoption MUST preserve published history and SHOULD apply the standard from
  the next safe release boundary.
- A repository MUST NOT renumber compatible existing releases merely to resemble
  a preferred scheme.
- Exact migration tasks, current versions, and adoption status remain local.
- An organization-wide migration program requires a separate approved scope and
  MUST NOT be inferred from this standard.

Repository adoption SHOULD link this standard and document only local release
units, version sources, tag format, registries, commands, workflow locations,
support lines, current migration state, and exceptions. It MUST NOT copy this
standard into repository documentation.

## Exception record

An exception MUST be explicit, reviewable, time-bounded where remediation is
possible, and stored with the affected repository or release unit. It MUST
record:

- affected release unit, artifact profile, version line, and rule;
- owner and approval authority;
- reason and affected consumers;
- risk and failure mode;
- compensating evidence or controls;
- migration, correction, or exit condition;
- approval date and review or expiry date; and
- links to related compatibility, deprecation, or incident evidence.

An exception MUST NOT permit a release to claim an identity, compatibility
level, publication state, or verification result that has not been established.
It MUST NOT silently overwrite published history.

A `SHOULD` deviation MAY be documented in normal repository decision or release
records when the rationale and impact are clear. A `MUST` or `MUST NOT`
deviation requires an explicit approved exception before publication unless an
emergency makes prior approval impossible.

## Emergency exception

An emergency MAY authorize a bounded deviation required to contain a security,
legal, privacy, regulatory, or integrity incident. The operator MUST record the
scope, action, reason, affected consumers, replacement, approval or emergency
authority, and follow-up review as soon as it is safe to do so.

Emergency handling does not authorize silent version reuse, fabricated
evidence, or an undocumented permanent policy change. The follow-up review MUST
either close the deviation, create a normal time-bounded exception, or propose a
change to this standard.

## Closing an exception

The owner closes an exception only after verifying the exit condition against
the affected release or workflow. Expiry without verification is a failed
exception, not automatic conformance. A policy change that makes an exception
obsolete SHOULD link the superseding standard version or decision.
