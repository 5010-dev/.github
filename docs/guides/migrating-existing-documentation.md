# Migrating existing documentation

Use this guide when a repository already has architecture content, ADRs,
runbooks, or local READMEs.

## 1. Preserve the checkout and inventory the corpus

List tracked Markdown, generated schemas, executable contracts, development
guides, runbooks, validation evidence, and external planning references. Record
which documents are current, stale, duplicated, or historical before moving
anything.

Do not delete, rename, or rewrite historical material merely to make the target
tree look clean.

## 2. Build an authority map

For every recurring concern, select the actual canonical owner. Keep executable
behavior with code and schemas, operational action with runbooks, observed
results with validation records, and decision history with ADRs.

The arc42 corpus becomes the consolidated engineering current view. It links to
those owners and does not absorb complete volatile inventories.

## 3. Create the L0 skeleton

Add the architecture index and twelve required chapter paths. Mark unverified
content `Open`; an honest navigation skeleton is preferable to invented
As-built claims.

Preserve established filenames and anchors when they already satisfy the
profile. The recommended paths are a compatibility default, not permission to
break inbound links.

## 4. Map before extracting

Create a temporary migration map when content must move across layers. For each
source section, record its target canonical owner and extraction condition.

Add the target document and inbound links before slimming the old parent.
Retain a black-box summary or compatibility pointer at the old location until
dependent links have migrated.

## 5. Separate current view from history

Architecture chapters describe the current As-built, accepted Target, and Open
state. ADRs preserve why consequential choices were made.

Do not edit an accepted ADR to match a newer architecture. Add a superseding ADR
and update both decision indexes and the consolidated current view.

## 6. Add profiles incrementally

Promote a component to Compact, Standard, or Full L1 documentation only after
its independent boundaries are evident. A large directory tree alone is not
evidence for a deeper architecture hierarchy.

## 7. Close the migration

Before declaring migration complete:

- verify every As-built claim against its owner;
- ensure Target and Open content cannot be mistaken for implementation;
- resolve local links and indexes;
- remove duplicate normative text in favor of links;
- run the documentation conformance check and repository quality gate; and
- keep the completed migration map when it materially helps later reviewers
  understand retained compatibility paths.
