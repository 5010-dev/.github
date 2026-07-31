# Engineering documentation

This directory contains canonical engineering standards, platform contracts,
adoption guidance, and cross-repository architecture decisions for the
`5010-dev` organization.

## Authority

- Organization standards own default cross-repository engineering invariants,
  required profiles, and conformance rules.
- Platform contracts own reusable platform-specific invariants, exposure
  profiles, runtime modifiers, and responsibility boundaries.
- Guides explain adoption and migration. They do not override a standard,
  platform contract, accepted ADR, or repository-local canonical owner.
- Templates are scaffold sources. After adoption, the resulting repository-local
  documents are maintained by that repository and are not synchronized
  byte-for-byte with the templates.
- Architecture decision records preserve why consequential cross-repository
  decisions were accepted.
- Repository code, workflow definitions, infrastructure definitions, and
  configuration remain authoritative for current executable As-built behavior.
- Canonical service documentation owns exact runtime health semantics,
  deployment workflow, verification, and repository-local As-built, Target, and
  Open status.
- Canonical Infrastructure documentation owns deployment-unit membership,
  structural inputs, ECS/ALB/SSM mappings, placeholder configuration,
  classification implementation, and repository-local status.
- The organization ownership directory is a non-authoritative discovery aid. It
  links to canonical locations without copying exact values or implementation
  progress.
- Repository documentation should link here instead of copying an organization
  contract.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
organization contracts are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14), when and only when they appear
in all capitals.

## Standards

- [Organization standards index](./standards/README.md)
- [Developer Tooling Standard](./standards/developer-tooling/README.md)
- [Developer Tooling stable rule catalog](./standards/developer-tooling/rules/README.md)
- [Developer Tooling schemas](./standards/developer-tooling/schemas/README.md)
- [Engineering documentation standard](./standards/engineering-documentation/README.md)
- [Engineering documentation contract](./standards/engineering-documentation/contract.md)
- [5010 arc42 profile](./standards/engineering-documentation/arc42-profile.md)
- [Documentation lifecycle and validation](./standards/engineering-documentation/lifecycle-and-validation.md)

## Guides

- [Organization guides index](./guides/README.md)
- [Adopting the Developer Tooling Standard](./guides/adopting-developer-tooling.md)
- [Bootstrapping a new repository](./guides/bootstrap-new-repository.md)
- [GitHub hosting capability profile](./guides/github-hosting-capabilities.md)
- [Migrating existing developer tooling](./guides/migrating-developer-tooling.md)
- [Adopting the organization arc42 profile](./guides/adopting-arc42.md)
- [Migrating existing documentation](./guides/migrating-existing-documentation.md)

## Platform contracts

- [Platform contracts index](./platform/README.md)
- [ECS deployment contract](./platform/ecs-deployment-contract.md)
- [ECS service delivery workflow standard](./platform/ecs-service-delivery-workflow-standard.md)
- [ECS health and readiness profiles](./platform/ecs-health-readiness-profiles.md)
- [ECS service contract ownership directory](./platform/ecs-service-health-matrix.md)

## Templates and tooling

- [Engineering documentation templates](../templates/engineering-documentation/README.md)
- [Golden Path workflow template](../workflow-templates/golden-path-quality.yml)
- [Governance repository tooling](../scripts/docs/README.md)

## Decisions

- [Organization architecture decision index](./decisions/README.md)

## Changing a contract

Update an organization standard or platform contract when a shared invariant,
reusable profile, or cross-repository responsibility boundary changes.
Repository-local endpoints, commands, mappings, workflows, scientific facts,
and implementation status are updated only in their owning repositories.

Add or supersede an architecture decision record when an organization change is
consequential, cross-repository, or hard to reverse. Do not use issue trackers,
pull request descriptions, or chat history as a second canonical source.
