# ECS service delivery workflow standard

- Status: Accepted
- Last updated: 2026-07-29
- Applies to: `5010-dev` service repositories that release application images
  to the shared AWS ECS platform

This standard defines the organization envelope for ECS service delivery
workflows. It complements the
[ECS deployment contract](./ecs-deployment-contract.md) and the
[ECS health and readiness profiles](./ecs-health-readiness-profiles.md).

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in
this document are to be interpreted as described in BCP 14.

## Scope and authority

This document owns stable cross-repository workflow invariants, required
evidence, allowed variation, and the exception process. Owning repositories
remain authoritative for exact:

- triggers, environment names, AWS accounts, roles, regions, and resource
  names;
- image repositories, SSM paths, task families, services, and container names;
- liveness commands, routing paths, readiness checks, and semantic evidence;
- rollout order for fleets, retry timing, rollback policy, and notifications;
- executable workflow and deployment-script implementation; and
- repository-local As-built, Target, Open, and conformance status.

Executable repository code is the current As-built authority. Acceptance of
this standard does not establish that any service workflow conforms.

This standard does not:

- combine the Infrastructure CDK pipeline with service release workflows;
- require one universal reusable workflow, composite action, or programming
  language;
- require identical triggers, health endpoints, readiness gates, rollback
  behavior, or notification providers;
- change ECS task environment representation or application secret
  consumption; or
- maintain a central registry of repository revisions, pull requests, or
  implementation status.

## Documentation ownership and freshness

Organization documents define guidance and stable comparison dimensions. They
MUST NOT duplicate mutable repository implementation facts.

| Information                                                                                | Canonical owner                      | Organization document treatment                                                        |
| ------------------------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------------------------------------------------------- |
| Cross-repository invariant, signal vocabulary, and exception rule                          | Organization platform contract       | Define normatively.                                                                    |
| Allowed workflow variation and required review evidence                                    | Organization workflow standard       | Define as guidance or a comparison matrix.                                             |
| Service and Infrastructure ownership                                                       | Owning repositories                  | Link through the non-authoritative ownership directory.                                |
| Canonical repository document location                                                     | Owning repository                    | Link for navigation; a branch-qualified link is not implementation-state evidence.     |
| Exact trigger, resource name, path, command, timeout, probe, and rollback behavior         | Owning repository                    | Do not copy; require repository-local documentation.                                   |
| Current workflow structure, implementation gap, profile assignment, and conformance status | Owning repository                    | Do not maintain a central status table.                                                |
| Pull request, commit, deployment run, and validation result                                | Owning repository or evidence system | Link only when needed by a durable decision; do not use as current organization state. |

An implementation inventory MAY inform an organization decision during
research, but the resulting normative document MUST retain only stable
invariants, variation axes, and ownership links. A service-only implementation
change MUST NOT require an organization-document update unless it also changes
an organization invariant, taxonomy, ownership boundary, or canonical document
location.

Examples and checklists in this standard MUST use placeholders or generic
shapes. Exact values and repository conformance evidence remain in the owning
repository so one implementation change has one canonical documentation update.

## Terms

- **Workflow orchestration:** GitHub event handling, job permissions, AWS
  authentication, concurrency, invocation, summaries, and notifications.
- **Deployment implementation:** locally executable logic that validates,
  builds, publishes, transforms, mutates AWS state, polls, verifies, and emits
  bounded diagnostics.
- **Structural state:** Infrastructure-owned task and service configuration,
  including roles, networking, resources, volumes, sidecars, logging, platform
  settings, and deployment topology.
- **Release-owned state:** the application image and the explicitly documented
  runtime and real-image liveness fields a service release is authorized to
  update.
- **Thin workflow:** a responsibility boundary, not a line-count target. GitHub
  Actions orchestrates while non-trivial deployment behavior is testable
  outside the workflow YAML.

## Responsibility boundary

Non-trivial service delivery MUST separate GitHub-specific orchestration from
locally executable deployment implementation.

| GitHub Actions owns                   | Locally executable implementation owns                 |
| ------------------------------------- | ------------------------------------------------------ |
| event and ref inputs                  | input validation beyond GitHub expression syntax       |
| least-privilege job permissions       | image build and publication behavior                   |
| OIDC credential setup                 | AWS preflight and account assertions                   |
| environment and concurrency selection | shared-state reads and writes                          |
| invoking repository commands          | task-definition transformation and registration        |
| GitHub step summary                   | service update, polling, verification, and diagnostics |
| notification integration              | deterministic transforms and test fixtures             |

The default location for the local implementation is `scripts/ci`. A repository
MAY use another documented location or tool when it provides the same review,
local execution, deterministic validation, and testability.

Inline YAML MAY contain simple environment assignment or direct invocation.
Loops, multi-step AWS mutation, task-definition JSON construction or
transformation, rollout polling, rollback, and failure classification SHOULD
NOT live only in YAML heredocs. If moving such logic out of YAML is not
practical, the repository MUST record an exception using the format below and
provide an equivalent deterministic validation path.

## Required delivery envelope

### Source, trigger, and environment guard

A deployment MUST bind the release to an identifiable source revision.

- The organization
  [`CONTRIBUTING.md`](../../CONTRIBUTING.md#branch-roles) owns branch roles and
  the integration flow: work branches start from `origin/dev`, normal pull
  requests target `dev`, and production promotion fast-forwards `dev` to `main`.
- A repository owns deployment triggers, path filters, and
  ref-to-environment mappings within that organization branch model.
- Automatic and manual entry points MUST derive an explicit target environment.
- A manual input MUST NOT silently deploy a different ref than the repository's
  documented environment policy permits.
- The workflow MUST fail before AWS mutation when the event, ref, and target
  environment combination is invalid or ambiguous.
- Whether `main` or `dev` deploys automatically, permits only manual deployment,
  or runs CI without deployment is repository-owned policy. That policy MUST NOT
  silently redefine the organization branch model.
- A repository that changes branch roles or the integration flow MUST record the
  organization-policy exception required by `CONTRIBUTING.md`, including scope,
  rationale, risks, approval, review conditions, and exit conditions.
- A `workflow_dispatch` run MAY select an environment only when the repository
  documents the allowed ref-to-environment relationship.

### Permissions and AWS identity

AWS access MUST use GitHub OIDC with a repository-scoped deployment role.
Long-lived AWS access keys MUST NOT be a normal deployment input.

- Workflow or job permissions MUST be explicit and least-privilege.
- A job that does not require a GitHub permission SHOULD declare no permission
  for it. Notification-only jobs SHOULD use `permissions: {}` when their action
  does not require repository access.
- The deployment implementation MUST call AWS STS before mutation and compare
  the observed account with the repository's expected target account.
- Region, partition, role, and account expectations MUST be repository-local
  configuration rather than inferred from a resource discovered by a broad
  list operation.
- Authentication, account validation, and preflight MUST complete before an ECR
  write or any shared-state, task-definition, or ECS service mutation.

Protected GitHub Environments MAY add approval or policy controls, but they are
not an organization-wide prerequisite.

### Concurrency and bounded execution

Two runs that can mutate the same deployment unit MUST share a concurrency
group. Independent environments or deployment units MAY use different groups.

- A mutating deployment SHOULD use `cancel-in-progress: false` so a newer run
  does not interrupt an older run between shared-state and ECS mutations.
- A different cancellation policy requires evidence that interruption cannot
  leave ambiguous or regressing state.
- Every mutating job MUST declare an explicit timeout.
- Every poll and retry loop MUST have a bounded deadline, bounded interval, and
  non-zero exit when its required condition is not established.
- Timeouts and failed observations MUST NOT be reported as success merely
  because a running count happens to match a desired count.

Exact timeout and polling values are repository-owned.

### Immutable source and image identity

The workflow MUST preserve both source provenance and deployment identity.

- A published image MUST be traceable to the selected source revision.
- A mutable tag such as `latest` MAY be published for operator convenience but
  MUST NOT establish the released image identity.
- Before task-definition registration, the workflow MUST resolve and retain the
  immutable registry digest of the image it will deploy.
- A successful release MUST leave shared deployment state and the registered
  application container selecting the same policy-compliant immutable image
  identity.
- Verification MUST compare the deployed named container with the expected
  digest. The presence of a source SHA in a mutable tag is provenance evidence,
  not a substitute for digest identity.

### Shared state and mutation safety

The workflow MUST use the environment-scoped shared deployment state defined by
the owning service and Infrastructure repositories.

Before the first mutation, it MUST capture enough non-sensitive rollback input
to identify:

- the previous shared image identity and observation or parameter version, or
  an explicit not-found result;
- the ECS service's previous task-definition revision and named
  application-container image, or an explicit unprovisioned-service result
  permitted by the repository's missing-service policy; and
- the intended new source revision and digest.

Publishing the image, updating shared state, registering a revision, and
updating the service cannot be one AWS transaction. A workflow therefore MUST:

1. complete authentication, target validation, required reads, and image
   publication before mutating shared deployment state;
2. fail visibly when any later phase is incomplete;
3. emit the non-sensitive previous and intended identities needed for operator
   recovery; and
4. leave state in a form that the next valid Infrastructure or service deploy
   can classify and consume safely.

The exact order of the shared-state write and task-definition registration MAY
vary. The repository MUST document the partial-failure behavior. A workflow
MUST NOT claim rollback unless it verified the state restored. Automatic
rollback is optional and repository-owned.

### Task-definition mutation

The default service-release strategy is:

1. resolve the task definition currently selected by the intended ECS service;
2. clone that revision;
3. select each release-owned application container by stable name;
4. apply only the authorized image, runtime, and real-image liveness changes;
5. preserve all other container and task-level structure;
6. remove only fields that ECS does not accept on registration;
7. validate the transformed definition; and
8. register a new revision.

A transformation MUST fail when the expected named container is missing,
duplicated, or ambiguous. It MUST NOT select `containerDefinitions[0]` or infer
the application container from array order.

Unless a reviewed cross-owner change says otherwise, service delivery MUST
preserve Infrastructure-owned fields, including:

- task and execution roles, network mode, compatibilities, CPU, memory, runtime
  platform, and ephemeral storage;
- sidecars, volumes, mount points, dependencies, essentiality, and container
  ordering semantics;
- port mappings, logging, secrets references, Linux parameters, user, and
  resource limits; and
- service-level networking, load balancers, discovery, placement, capacity,
  deployment controller, and desired-count policy.

Task-definition reassembly from a repository-owned template or generator MAY be
used only with a recorded exception. Its evidence MUST prove that the generated
revision:

- is structurally equivalent to the current Infrastructure-owned revision for
  every non-release-owned field;
- targets application containers by name;
- preserves unknown or newly added sidecars and structural fields;
- applies the same immutable digest and real-image liveness contract; and
- fails closed on an unrecognized structural difference.

Service delivery MUST NOT create, repair, or broadly discover missing
Infrastructure resources as a substitute for an Infrastructure deployment.
Repository policy MAY define an explicit staged-image result for a deployment
unit whose service is not yet provisioned.

### Bootstrap-to-Released health promotion

When a real image replaces an approved placeholder, the registered revision
MUST replace bootstrap-only `CMD-SHELL exit 0` health with the exact
service-owned real-image liveness command and timing.

- Cloning the current placeholder revision does not authorize retaining its
  bootstrap health.
- A subsequent service or Infrastructure deployment MUST preserve the same
  released-image liveness contract.
- Routing health, application readiness, and semantic correctness remain
  separately named signals.
- Exact commands, paths, timing, and failure semantics remain in the owning
  service repository.

### Rollout and evidence

A required deployment gate MUST exit non-zero when its evidence is absent or
contradictory. Each report MUST name the signal observed and MUST NOT collapse
the following into an unqualified "healthy" result.

| Evidence                            | Organization requirement                                                                                                                                                 |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Source and image                    | Always record the source revision and expected immutable digest.                                                                                                         |
| Task definition                     | Always prove the service selected the intended revision, the named application container selected the expected digest, and the revision renders released-image liveness. |
| ECS rollout                         | Always report desired, running, and pending counts plus the primary rollout state within a bounded deadline.                                                             |
| Observed container liveness         | Required when desired capacity is non-zero and ECS exposes container health; do not reinterpret bootstrap health as real-image liveness.                                 |
| Routing health                      | Required for a deployed ALB application, control-plane, or health-only route at non-zero desired capacity; it is not implied by rollout convergence.                     |
| Application readiness               | Required only when the service contract defines it as a deployment gate; it remains separate from liveness and routing.                                                  |
| Semantic or operational correctness | Required only when repository policy selects it; state the exact observation and time window.                                                                            |

Profile modifiers govern legitimate outcomes. For example, `elastic-to-zero`
verification MUST accept an intended `0/0` service without scaling it up, and a
lease-fenced or operator-controlled process MUST NOT fail deployment only
because it is on standby.

An `internal-http-service` or `background-service` MUST NOT gain a public probe
only to satisfy delivery verification. An `alb-http-service`,
`alb-control-plane`, or `health-only-alb-route` report MUST name routing evidence
separately whenever the routed role has non-zero desired capacity.

### Sensitive values on the GitHub Actions surface

This section protects the GitHub Actions execution surface. It does not require
converting ECS task environment entries to Secrets Manager or SSM secret
references, changing application secret schemas, or changing runtime secret
consumption. Those are separate security-architecture decisions.

Decrypted or otherwise sensitive values MAY exist in runner memory or protected
temporary files when the current repository deployment contract requires them.
When they do:

- shell tracing MUST be disabled while the value is read or used;
- a materialized value and any sensitive derived value MUST be registered with
  GitHub masking immediately, before later commands can echo it;
- temporary files MUST be owner-readable only and removed by a cleanup trap,
  including on failure and cancellation where GitHub permits cleanup;
- commands SHOULD pass protected files or masked variables without placing
  values in command-line diagnostics; and
- logs MAY name validated keys only when key names are not themselves sensitive.

Sensitive values MUST NOT appear in:

- command echo, shell trace, visible AWS CLI output, or error diagnostics;
- `$GITHUB_OUTPUT`, `$GITHUB_ENV`, or `$GITHUB_STEP_SUMMARY`;
- uploaded artifacts, caches, build metadata, or notification payloads;
- complete task-definition environment maps or decrypted configuration dumps;
  or
- private health or semantic response bodies.

`add-mask` is defense in depth, not permission to print a value.

### Diagnostics, cleanup, and notifications

Failure diagnostics MUST be bounded and relevant to the selected deployment
unit. They SHOULD include:

- the intended and observed task-definition revision;
- the expected and observed named-container digest;
- rollout state and desired, running, and pending counts;
- recent deployment events within a documented count or time window; and
- target health or repository-selected readiness evidence when applicable.

Diagnostics MUST NOT dump all clusters, services, task definitions,
environment variables, SSM values, or secret payloads.

Cleanup steps that protect sensitive temporary state MUST run under `always()`
or an equivalent trap. Notification steps MAY run under `always()`, but they:

- MUST NOT obscure the deployment job result;
- MUST NOT include sensitive values;
- SHOULD link to the run instead of copying unbounded logs; and
- SHOULD use a separate no-permissions job when practical.

The notification provider and whether notification failure is fatal are
repository-owned policies.

## Allowed repository variation

The following choices remain repository-owned when the required envelope above
is satisfied.

| Concern               | Allowed variation                                                                       | Required local record                                       |
| --------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Trigger               | automatic, manual, path-filtered, or a combination within the organization branch model | allowed deployment refs and environment mapping             |
| Deployment unit       | one service, several roles, or a dynamic fleet                                          | membership owner and mutation order                         |
| Fleet rollout         | serial, bounded parallel, canary, or staged                                             | failure aggregation and stop policy                         |
| Missing service       | fail, or stage immutable image state for later Infra creation                           | classification and operator-visible result                  |
| Readiness             | no deploy gate, endpoint gate, internal probe, or semantic gate                         | selected health profile and exact evidence                  |
| Zero scale or standby | accept intended `0/0`, standby, or operator-controlled state                            | applicable runtime modifiers                                |
| Rollback              | manual, automatic, or forward-fix                                                       | inputs, trigger, verification, and partial-failure behavior |
| Notification          | provider, audience, and failure policy                                                  | non-sensitive payload and job-result behavior               |

Variation does not permit weakening immutable digest identity, named-container
selection, structural preservation, real-image liveness promotion,
least-privilege OIDC, bounded execution, or sensitive-value non-exposure.

## Exception record

A repository that cannot meet an invariant MUST keep a durable exception beside
its canonical deployment documentation or in a repository ADR. A Linear issue
or pull request alone is not a durable exception.

Use this minimum format:

```markdown
## ECS service delivery exception: <short name>

- Status: Proposed | Accepted | Expired | Superseded
- Owner: <repository or subsystem owner>
- Scope: <workflow and deployment units>
- Invariant: <section and requirement being varied>
- Rationale: <why the default cannot be used>
- Risks: <failure and security consequences>
- Compensating evidence: <equivalent deterministic checks>
- Reviewers: <service and Infrastructure owners as applicable>
- Accepted on: <YYYY-MM-DD>
- Review by: <YYYY-MM-DD or event>
- Exit conditions: <what removes the exception>
- Links: <canonical docs, ADR, validation, and implementation>
```

An accepted exception MUST:

- identify a bounded scope and owner;
- preserve the deployment and health contracts' safety outcomes;
- define deterministic compensating evidence;
- state review and exit conditions; and
- be linked from the affected workflow's canonical documentation.

An exception that changes a cross-repository invariant requires an organization
ADR and a change to this standard rather than a repository-only record.

## Pull request conformance checklist

Repositories MAY copy this checklist into a pull request that changes an ECS
service delivery workflow or its local implementation.

```markdown
### ECS service delivery conformance

- [ ] Event, ref, and target environment are validated before AWS mutation.
- [ ] Permissions are explicit; OIDC and expected AWS account are verified.
- [ ] Mutating runs are collision-safe and all jobs and polls are bounded.
- [ ] Source provenance is recorded and deployment uses an immutable digest.
- [ ] Previous shared-state, task-definition, and named-container identities are captured.
- [ ] The task-definition strategy uses current-revision clone and named mutation, or links an accepted alternative-generation exception.
- [ ] Infrastructure-owned structure, sidecars, and unknown fields are preserved.
- [ ] A real image receives service-owned liveness; bootstrap `exit 0` is not retained.
- [ ] Task revision, named-container digest, and ECS rollout convergence are verified.
- [ ] Routing, readiness, semantic, zero-scale, and standby evidence follow the selected profile.
- [ ] Sensitive values cannot reach logs, outputs, summaries, artifacts, diagnostics, or notifications.
- [ ] Failure diagnostics are bounded and rollback inputs are operator-visible without secret material.
- [ ] Non-trivial deployment behavior is locally executable and deterministically tested.
- [ ] Canonical repository docs state As-built, Target, Open, and any accepted exception.
```

When the current task-definition clone strategy is not used, also include:

```markdown
- [ ] Alternative generation has structural-equivalence and fail-closed evidence.
- [ ] Accepted exception: <canonical link>
```

## Adoption and conformance

Organization acceptance establishes the Target contract. Each service
repository owns:

- its As-built inventory;
- its gap analysis and implementation plan;
- deterministic tests and deployment evidence;
- accepted repository exceptions; and
- the decision that a specific workflow conforms.

Do not add repository PRs, SHAs, mutable refs as implementation or conformance
evidence, or a service-by-service conformance table to this document or the
ownership directory. The ownership directory MAY use a branch-qualified URL
only to navigate to a canonical document maintained by its owning repository.

## Related documents

- [ECS deployment contract](./ecs-deployment-contract.md)
- [ECS health and readiness profiles](./ecs-health-readiness-profiles.md)
- [ECS service contract ownership directory](./ecs-service-health-matrix.md)
- [ADR-0001: Adopt a hybrid ECS deployment model](../decisions/0001-adopt-hybrid-ecs-deployment-model.md)
- [ADR-0005: Adopt an ECS service delivery workflow envelope](../decisions/0005-adopt-ecs-service-delivery-workflow-envelope.md)
