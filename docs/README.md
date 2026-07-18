# Engineering documentation

This directory contains canonical engineering contracts and cross-repository
architecture decisions for the `5010-dev` organization.

## Authority

- Organization contracts define the default requirements shared by participating
  repositories.
- Architecture decision records preserve why consequential cross-repository
  decisions were accepted.
- Repository code, workflow definitions, infrastructure definitions, and
  configuration remain authoritative for what is deployed today.
- Repository documentation owns service-specific mappings, procedures, and
  explicitly accepted exceptions. It should link here instead of copying an
  organization contract.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
organization contracts are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14), when and only when they appear
in all capitals.

## Contracts

- [ECS deployment contract](./platform/ecs-deployment-contract.md)

## Decisions

- [ADR-0001: Adopt a hybrid ECS deployment model](./decisions/0001-adopt-hybrid-ecs-deployment-model.md)

## Changing a contract

Update a contract and its affected repositories together when a shared
invariant or responsibility boundary changes. Add or supersede an architecture
decision record when the change is consequential, cross-repository, or hard to
reverse. Do not use issue trackers, pull request descriptions, or chat history
as a second canonical source.
