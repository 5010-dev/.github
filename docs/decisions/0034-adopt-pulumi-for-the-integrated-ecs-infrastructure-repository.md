# ADR-0034: Adopt Pulumi for the integrated ECS Infrastructure repository

- Status: Accepted
- Date: 2026-10-18
- Owners: `5010-dev/.github` maintainers and the ECS Infrastructure owner

## Context

The shared ECS platform, its storage, and its retained credential resources are
defined with AWS CDK in separate Infrastructure repositories. The accepted
Infrastructure plan consolidates them into one integrated Infrastructure
repository, adopts the remaining resources, and builds new deployments there.

The [Infrastructure as Code profile](../standards/developer-tooling/profiles/infrastructure.md)
keeps AWS CDK v2 as the default for new AWS IaC, allows Pulumi conditionally,
and requires a separate ADR and resource-identity, import, replacement,
secret/state, rollback, and verification plan for an engine migration. It did
not describe a repository with several Pulumi projects in one host-language
workspace.

## Decision

1. The integrated ECS Infrastructure repository uses Pulumi with TypeScript and
   combines the `infrastructure-pulumi` and `node-typescript` profiles.
2. Its programs are Pulumi projects, each with its own `Pulumi.yaml` and
   `infrastructure-pulumi` native root. Stacks are configuration and state
   targets of a project, not native roots. The programs and their shared
   library use one pnpm workspace and lock. The repository declares these roots
   in `.github/golden-path-native-roots.yaml` with the existing v1 schema.
3. This ADR is the engine-migration decision that the profile requires. The
   repository owns the resource-identity, import, replacement, secret/state,
   rollback, and verification plan and its evidence.
4. Each transferred resource keeps one engine, state, and writer. Existing
   resources are imported without replacement or physical identity change, and
   the previous writer is retired before the new one applies changes.
5. Static `just ci` stays credential-free. Preview, import, refresh, and apply
   are stateful delivery.
6. ECS task-definition revisions follow
   [ADR-0033](./0033-adopt-a-common-ecs-task-revision-path.md); the programs do
   not declare a competing task-definition writer.
7. AWS CDK v2 remains the default for other new AWS IaC. No other repository is
   required to migrate. Another repository that selects Pulumi follows the
   profile's conditions or its own accepted ADR.
8. This decision does not establish the repository's name, location, or
   transfer of any unit. Organization directories keep linking current
   canonical owners until the owning repositories record that transfer.

[ADR-0008](./0008-separate-artifact-components-from-native-dependency-roots.md)
already separates native roots from artifacts; this decision applies that model
to several Pulumi projects in one workspace.

## Consequences

### Positive

- The ECS platform and related resources have one IaC owner and repository.
- A multi-project Pulumi workspace has an unambiguous native-root model that the
  existing schema and Golden Path Agent can inventory.
- Other repositories keep their current IaC engines and defaults.

### Negative

- Imports, state backend, secrets provider, and per-stack delivery identities
  become new operational responsibilities.
- A change to shared program code or the lock requires preview of every
  consuming stack.
- Organization documents keep linking current owners until transfer evidence
  exists, so they lag the integrated repository during migration.

## Alternatives considered

### Continue with AWS CDK

Not retained for this owner. The accepted Infrastructure plan selected Pulumi,
and its comparison and evidence remain with that plan. This ADR records the
organization-level effect of that selection and does not reopen it.

### Make Pulumi the organization default

Outside this decision. One owner's engine selection does not establish a new
organization default for new IaC; changing the default would need its own ADR
and profile change. A default for new work would not by itself require
existing repositories to migrate.

### Give each Pulumi program its own lock

Rejected because the programs share one library and toolchain; duplicated
locks would create competing dependency authority.

## Adoption status

This decision accepts organization Target architecture. It does not verify the
integrated repository, its programs, imports, or delivery workflows; their
implementation status belongs to the owning repository. Current canonical owners
remain authoritative until the owning repositories record the transfer.
