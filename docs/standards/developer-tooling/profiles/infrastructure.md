# Infrastructure as Code profile

- Status: Accepted
- Profile IDs: `infrastructure-aws-cdk`, `infrastructure-terraform`,
  `infrastructure-opentofu`, `infrastructure-pulumi`
- Standard version: `2026.10`

This profile owns IaC authoring, exact tool/dependency authority, static
validation, and non-mutating commands. Deployment and Operations contracts own
promotion, identity implementation, state mutation, rollback, destroy,
recovery, drift, and runtime verification.

`preview`, `deploy`, and `drift` are optional façades, not universal base
commands. Application image or service delivery MUST NOT be forced into the IaC
lifecycle.

## Tool selection

- AWS CDK v2 is the default for new AWS-centered IaC.
- Terraform or OpenTofu is conditional for HCL modules/providers, existing
  state, or external integration.
- Pulumi is conditional for code-first abstractions, multi-cloud portability,
  an actual move beyond AWS, or an IaC owner whose accepted ADR selects it.
  Such a selection applies only to the named owner; it does not change the
  AWS CDK default or require other repositories to migrate.
- One resource MUST have one engine, state, and write owner.
- An engine migration requires a separate ADR and resource-identity, import,
  replacement, secret/state, rollback, and verification plan. The ADR records
  the cross-repository decision; the owning repository keeps the plan and its
  evidence.
- A transfer imports or adopts existing resources without replacement, physical
  identity change, data rewrite, or secret regeneration. Intended changes
  after transfer are separate reviewed deliveries. The previous engine's writer
  for a transferred resource is retired, not run concurrently with the new one.

The static lane MUST NOT mutate shared cloud or state and SHOULD be
credential-free. Dynamic architecture that requires current state belongs to a
stateful delivery lane. Captured dynamic input requires canonical source,
integrity, freshness, and cleanup. `cdk.context.json` is not a universal MUST.

## Stateful delivery outcomes

Every stateful IaC delivery MUST provide:

1. short-lived identity and least privilege;
2. exact account, region, stack, workspace, and backend validation;
3. collision safety for the same state/resource;
4. a preview, plan, or change set from current code and target immediately
   before apply;
5. protection of state, plans, outputs, and sensitive data;
6. no CDK hotswap, watch, or no-rollback mode in production;
7. separation of destroy, state repair, and backend migration from routine
   deploy; and
8. bounded success evidence applicable to the deployment, such as
   revision/digest, stack/output, and health evidence.

The following are SHOULD requirements:

- a protected boundary equivalent to a GitHub Environment;
- separate bootstrap/backend administration from routine deployment;
- saved-plan apply or managed/same-run equivalent linkage for HCL custom
  automation;
- strong production remote-state durability and locking;
- risk-based drift detection; and
- auditable destructive/state-repair procedures.

Approval is a conditional MUST for persistent delete/replace, IAM/network
exposure or protection weakening, production destroy, state/backend/provider/
region/owner changes, cross-account/large-blast-radius operations, or force
unlock during a collision.

Two-person approval applies only to high-impact, irreversible, or regulated
operations. It is not a universal requirement for all production deployment,
role separation, or drift jobs.

## GitHub Free private boundary

Environment/reviewer and protected-branch/ruleset capability MUST NOT be a
conformance prerequisite.

- Routine delivery uses short-lived OIDC, exact repository/workflow/ref or
  immutable release trust, cloud least-privilege roles, and concurrency.
- High-risk approval uses an independent operator role, cloud control plane,
  bounded manual workflow, or durable external approval evidence.
- When two-person approval applies, requester and approver MUST be distinct; a
  second input from the same user is insufficient.
- Paid GitHub controls MAY strengthen the same outcome without replacing
  deployment authority.

## AWS CDK

- TypeScript is the default CDK host language and combines this profile with
  `node-typescript`; another host language requires an actual repository or
  library constraint.
- CDK libraries and CLI are exact local project dependencies; a global CLI is
  not a prerequisite.
- `cdk.json` is committed.
- `cdk.context.json` is committed only when lookups are canonical deterministic
  inputs; refresh is explicit and reviewed, and secrets are prohibited.
- `cdk.out` is generated and not committed.
- `ci` uses locked install, typecheck/test, and deterministic synth without
  deployment.
- Stateful delivery uses CloudFormation change sets and rollback.
- `--require-approval never` is permitted when approval lives at an explicit
  PR/promotion/risk gate.
- Routine deployment MUST NOT bootstrap and MUST fail closed if bootstrap is
  absent.
- Stateful construct-ID or logical-ID refactors require replacement/retention
  review and a migration plan when they can change resource identity.

## Terraform and OpenTofu

- Each independently initialized root selects one engine and exact
  `required_version`.
- The root commits provider constraints and `.terraform.lock.hcl`.
- Static CI uses format check, backend-disabled/read-only-lock init, and
  validate.
- Multi-platform development/release prepopulates provider checksums.
- Registry modules use exact versions; VCS modules use immutable SHAs.
- `.terraform/` and provider binaries are not committed.
- Terraform and OpenTofu MUST NOT alternately rewrite one root's lock without an
  explicit compatibility profile.
- Saved-plan apply is a SHOULD for custom automation; managed or same-run
  equivalent linkage is allowed.
- Stored plans are sensitive artifacts.

## Pulumi

- `Pulumi.yaml`, exact CLI compatibility, host-language manifest/lock, SDK, and
  provider pins are committed.
- Host-language package-manager/toolchain options align with the selected
  language profile.
- A Pulumi project is the directory containing `Pulumi.yaml`; that directory is
  its `infrastructure-pulumi` native root. A stack is a configuration, state,
  and lock target of one project, not another project or native root.
- Several projects MAY share one host-language workspace and its single lock,
  for example one pnpm workspace whose packages are the programs and their
  shared library. When they do, projects MUST NOT duplicate that lock. A
  repository with more than one project declares each project root and its
  actual host-language dependency root or roots in
  `.github/golden-path-native-roots.yaml`.
- Stack configuration MAY be committed, but plaintext secrets, backend
  credentials, and decrypted state MUST NOT be.
- Static `ci` uses locked host dependencies and language quality gates without
  cloud, backend, or state credentials. `pulumi preview`, `import`, `refresh`,
  and `up` remain in the stateful delivery lane rather than `just ci`.
- Each delivery target names its project, stack, account, region, and backend.
  A change to shared program code, the host lock, providers, or delivery
  workflows previews every configured stack that consumes it; apply runs only
  for explicitly selected stacks.
- A stack reference reads the producer's last applied outputs. A consumer
  preview does not validate producer output that is not yet applied.
- An import preview MUST show no replacement or unintended property change
  before the import is applied.
- Production `up` MUST preview the current target and MUST NOT skip preview.
- A strict/saved plan remains an evaluation option, not a universal MUST.
- Drift operation is risk-based.

## Existing deployment contracts

Adopting this profile does not silently modify an existing deployment workflow,
approval boundary, role, automatic production policy, or executable As-built.
Such changes require the owning deployment decision and repository migration
work.

IaC that owns shared ECS structure, with any engine, follows the
[ECS deployment contract](../../../platform/ecs-deployment-contract.md). It
MUST NOT declare a task-definition writer that competes with the contract's
common revision path, and it does not run application releases.

Rule IDs: `DT-IAC-*`, plus common `DT-CMD-*`, `DT-TOOL-*`, and `DT-DEP-*`.
