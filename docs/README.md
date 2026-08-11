# Engineering documentation

This directory contains canonical organization standards, platform contracts,
adoption guidance, and cross-repository architecture decisions.

## Authority

- Organization standards own default cross-repository invariants.
- Platform contracts own reusable platform-specific invariants and
  responsibility boundaries.
- Guides explain adoption and migration; they do not override standards,
  platform contracts, accepted ADRs, or repository-local authorities.
- Repository code, native manifests and locks, workflows, release units, and
  configuration remain authoritative for executable As-built behavior.
- Architecture decisions preserve why consequential choices were accepted.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
organization contracts are interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14) when they appear in all capitals.

## Standards

- [Developer Tooling Standard](./standards/developer-tooling/README.md)
- [Developer Tooling schemas](./standards/developer-tooling/schemas/README.md)
- [Release and Versioning Standard](./standards/release-versioning/README.md)
- [Engineering documentation standard](./standards/engineering-documentation/README.md)

## Guides

- [Developer Tooling Golden Path](./golden-path/README.md)
- [Organization guides](./guides/README.md)
- [Adopting the Developer Tooling Standard](./guides/adopting-developer-tooling.md)
- [Bootstrapping a new repository](./guides/bootstrap-new-repository.md)
- [Migrating existing developer tooling](./guides/migrating-developer-tooling.md)
- [GitHub hosting capability profile](./guides/github-hosting-capabilities.md)
- [Adopting the organization arc42 profile](./guides/adopting-arc42.md)
- [Migrating existing documentation](./guides/migrating-existing-documentation.md)

## Platform contracts and decisions

- [Platform contracts](./platform/README.md)
- [Organization architecture decisions](./decisions/README.md)

## Templates and repository checks

- [Engineering documentation templates](../templates/engineering-documentation/README.md)
- [Governance repository checks](../scripts/docs/README.md)

## Changing a contract

Change an organization standard when a shared invariant changes. Change
repository-local commands, mappings, workflows, and current evidence only in
their owning repository. Consequential cross-repository changes add a new ADR;
historical ADRs and published release artifacts remain immutable.
