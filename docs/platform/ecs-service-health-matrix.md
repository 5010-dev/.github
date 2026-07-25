# ECS service profile and transition matrix

- Status: Canonical profile and transition registry
- Last updated: 2026-07-25
- Applies to: current `5010-dev` services on the shared AWS ECS platform

This document maps the organization
[deployment contract](./ecs-deployment-contract.md) and
[health profiles](./ecs-health-readiness-profiles.md) to current repositories.
Its exposure-profile assignments, runtime modifiers, accepted Target contracts,
and transition status are canonical organization records.

The detailed resource, image, endpoint, workflow, and health descriptions are
fixed-revision evidence snapshots. Current executable code, workflows, and
canonical repository documentation remain authoritative for As-built details.
This matrix links those authorities and does not replace them or claim that
source behavior has run successfully in a particular AWS environment.

## Evidence baseline

The mapping was reviewed against these exact local source revisions:

| Repository | Revision and inspected branch | Primary authority |
| --- | --- | --- |
| `indicator-ecs-infra` | [`be419ff`](https://github.com/5010-dev/indicator-ecs-infra/tree/be419ffcd45bb735744c8af1b14d571ba4b61c4a) (`dev`) | [Deployment view](https://github.com/5010-dev/indicator-ecs-infra/blob/be419ffcd45bb735744c8af1b14d571ba4b61c4a/docs/architecture/07-deployment-view.md), [constructs](https://github.com/5010-dev/indicator-ecs-infra/tree/be419ffcd45bb735744c8af1b14d571ba4b61c4a/lib/constructs), and [configuration scripts](https://github.com/5010-dev/indicator-ecs-infra/tree/be419ffcd45bb735744c8af1b14d571ba4b61c4a/scripts) |
| `5010-indicator-server` | [`ebca736`](https://github.com/5010-dev/5010-indicator-server/tree/ebca7369b5f8813451b88a70b23b52c33db44599) (`dev`) | [API controller](https://github.com/5010-dev/5010-indicator-server/blob/ebca7369b5f8813451b88a70b23b52c33db44599/src/app.controller.ts) and [deployment workflow](https://github.com/5010-dev/5010-indicator-server/blob/ebca7369b5f8813451b88a70b23b52c33db44599/.github/workflows/deploy.yml) |
| `5010-academy-dashboard` | [`a6c99b2`](https://github.com/5010-dev/5010-academy-dashboard/tree/a6c99b2a94a54f1b39d77d9921c6ad97c56c75b1) (`main`) | [Backend controller](https://github.com/5010-dev/5010-academy-dashboard/blob/a6c99b2a94a54f1b39d77d9921c6ad97c56c75b1/backend/src/app.controller.ts) and [deployment workflow](https://github.com/5010-dev/5010-academy-dashboard/blob/a6c99b2a94a54f1b39d77d9921c6ad97c56c75b1/.github/workflows/deploy-backend.yml) |
| `fiftyten-indicators-core` | [`e54e206`](https://github.com/5010-dev/fiftyten-indicators-core/tree/e54e20649eb6fb17be331e0a21e568792414ea90) (`dev`) | [Deployment view](https://github.com/5010-dev/fiftyten-indicators-core/blob/e54e20649eb6fb17be331e0a21e568792414ea90/docs/architecture/07-deployment-view.md), [health routes](https://github.com/5010-dev/fiftyten-indicators-core/blob/e54e20649eb6fb17be331e0a21e568792414ea90/apps/calculator-service/src/http.rs), and [deployment scripts](https://github.com/5010-dev/fiftyten-indicators-core/tree/e54e20649eb6fb17be331e0a21e568792414ea90/scripts/ci) |
| `indicator-data-collector` | [`4fde056`](https://github.com/5010-dev/indicator-data-collector/tree/4fde056fb5c69eeab1961eea18fa807b66a40167) (`dev`) | [Deployment view](https://github.com/5010-dev/indicator-data-collector/blob/4fde056fb5c69eeab1961eea18fa807b66a40167/docs/architecture/07-deployment-view.md), [task-definition renderer](https://github.com/5010-dev/indicator-data-collector/blob/4fde056fb5c69eeab1961eea18fa807b66a40167/scripts/ci/lib/task-definition.sh), and [deployment verification](https://github.com/5010-dev/indicator-data-collector/blob/4fde056fb5c69eeab1961eea18fa807b66a40167/scripts/ci/verify-deployment.sh) |
| `fiftyten-quant` | [`3910234`](https://github.com/5010-dev/fiftyten-quant/tree/3910234e67b26d971ec34fbac0c11677357ca281) (`dev`) | [Bot deployment](https://github.com/5010-dev/fiftyten-quant/blob/3910234e67b26d971ec34fbac0c11677357ca281/scripts/ci/deploy-bots.sh), [Bot health route](https://github.com/5010-dev/fiftyten-quant/blob/3910234e67b26d971ec34fbac0c11677357ca281/apps/trading-bot/src/trading_bot/api/routes/health.py), and [Obs deployment](https://github.com/5010-dev/fiftyten-quant/blob/3910234e67b26d971ec34fbac0c11677357ca281/docs/architecture/subsystems/observability/deployment.md) |

Collector PR
[#20](https://github.com/5010-dev/indicator-data-collector/pull/20) at
[`93d6d24`](https://github.com/5010-dev/indicator-data-collector/tree/93d6d24fdf330bb48abfe8e80c95f9d28b8b897c)
implements digest-pinned delivery, `/healthcheck.sh` promotion, and ECS task
health verification on an unmerged work branch. It is pending implementation
evidence for the Target, not accepted As-built authority.

## Identity, profile, and image state

| Service and owner | ECS construct / application container | Exposure profile | Runtime modifiers | Bootstrap image and current state selection | Released image selection | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Indicator API · `5010-indicator-server` | `ApiService` / `ApiContainer` | `alb-http-service` | `replicated-stateless` | `hello-app-runner:latest`; Infra selects it whenever the image read is empty, without proving explicit `ParameterNotFound`, current service absence, and bootstrap authorization. | `/indicator/api/{env}/image`; service workflow writes a commit-SHA tag. | **As-built:** fallback is error- and authorization-ambiguous. **Target:** authorized state-aware selection and immutable-image validation. |
| Academy Dashboard · `5010-academy-dashboard` | `AcademyDashboardService` / `AcademyDashboardContainer` | `alb-http-service` | `replicated-stateless` | `hello-app-runner:latest`; same error-ambiguous Infra fallback. | `/indicator/academy-dashboard/{env}/image`; service workflow writes a commit-SHA tag. | **As-built / Target:** same split as API. |
| Calculator · `fiftyten-indicators-core` | `CalculatorService` / `CalculatorContainer` | `internal-http-service` | `singleton` | `nginx-unprivileged:stable-alpine`; Infra permits it when the image is absent and permits missing Plan documents only with that fallback. Partial Plan pairs fail. | `/indicator/calculator/{env}/image`; service workflow requires a digest URI and a complete Universe/profile pair. | **As-built:** digest release automation exists; production execution is recorded by the owner as pending. **Target:** error-aware state selection. |
| Collector Master · `indicator-data-collector` | `CollectorMasterService` / `CollectorMasterContainer` | `internal-http-service` | `singleton` for the current main topology | `amazon-ecs-sample:latest`; selected independently from the other Collector roles. | `/indicator/data-collector/{env}/master-image`; accepted `dev` writes one commit-SHA-tagged image URI to all three role parameters. | **As-built:** current topology is one task but the construct does not hard-enforce singleton. **Target:** atomically classify the three-role unit and require a shared digest identity. |
| Collector Worker · `indicator-data-collector` | `CollectorWorkerService` / `CollectorWorkerContainer` | `background-service` | `elastic-to-zero` | `amazon-ecs-sample:latest`; selected independently. Public IP is exchange egress, not an application endpoint. | `/indicator/data-collector/{env}/worker-image`; accepted `dev` writes the same commit-SHA-tagged URI as master/realtime. | **As-built:** zero capacity is valid. **Target:** atomic group classification and shared digest identity remain Infra and service work. |
| Collector Realtime · `indicator-data-collector` | `CollectorRealtimeService` / `CollectorRealtimeContainer` | `background-service` | `lease-fenced-singleton` | `amazon-ecs-sample:latest`; selected independently. Public IP is WebSocket egress; there is no ALB or Service Connect endpoint. | `/indicator/data-collector/{env}/realtime-image`; accepted `dev` writes the same commit-SHA-tagged URI as master/worker. | **As-built:** desired count is construct-enforced at one. **Target:** complete group classification and shared digest validation. |
| Quant Bot fleet · `fiftyten-quant` | `QuantBotService` / `QuantBotContainer` plus optional `VectorSidecar` | `alb-control-plane` | `singleton`, `operator-controlled`, `sidecar-bearing` | Per-bot `nginx-unprivileged:stable-alpine`; Infra selects it when a per-bot image read is empty. | `/indicator/quant/{env}/bots/{bot}/image`; one SHA-tagged image is written across enabled bots. A missing service is reported as SSM-only staging. | **As-built:** per-bot service staging is supported. **Target:** validate complete enabled-fleet image selection for each fleet release. |
| Obs fleet · `fiftyten-quant` | `ObsService` / `ObsContainer` | `alb-control-plane` | `singleton`, `multi-process-container` | Per-bot `nginx-unprivileged:stable-alpine`; Infra selects it when `obs-image` is empty. | `/indicator/quant/{env}/bots/{bot}/obs-image`; one SHA-tagged Obs image is written across observed bots. Missing services are SSM-only. | **As-built:** denylisted bots are outside the observed unit. **Target:** validate complete observed-fleet selection for each release. |

The current fallback strings identify the existing placeholders; they are not
evidence of immutable allowlisting. Infra follow-up MUST define the approved
placeholder registry/image references and MUST reject unapproved or ambiguous
values. No current Infra selector requires explicit initial-bootstrap
authorization, so parameter and service absence alone MUST NOT be treated as a
conformant Bootstrap path.

## Health, routing, and evidence

| Service | ECS container liveness | ALB / Service Connect routing health | Deployment convergence evidence | Application readiness / semantic evidence | Rolling, singleton, or zero-scale behavior | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Indicator API | Service workflow renders `curl -f http://localhost:3000/api/health`; current CDK renders `exit 0`. | Shared ALB target group probes `/`, because the Infra workflow explicitly sets that path. | Workflow observes `ACTIVE`, running/desired, primary deployment, selected task definition, and commit-SHA image. Its timeout fallback accepts running/desired without proving all earlier conditions. | `/api/health` reports API process status only; database, Valkey, and domain readiness are not established. | Autoscaled replicated service; normal rolling overlap. | **As-built:** service deploy applies application liveness, then CDK regresses it. **Target:** CDK reproduces `/api/health`. **Open:** retain `/` or align ALB to `/api/health`. |
| Academy Dashboard | Service workflow renders `curl -f http://localhost:3000/api/health`; current CDK renders `exit 0`. | Shared ALB target group probes `/`. | ECS `services-stable`, task-definition selection, status, and counts. A public `/api/health` retry runs after deployment but does not fail the job after exhausting retries. | `/api/health` is a process response and does not prove database or Discord integration readiness. | Autoscaled replicated service; normal rolling overlap. | **As-built:** service deploy applies application liveness, then CDK regresses it. **Target:** CDK reproduces `/api/health`; make any claimed endpoint gate enforce its result. **Open:** ALB path policy. |
| Calculator | Current CDK task definition uses `exit 0`. The image Dockerfile declares `/health/live`, but the service workflow derives the current ECS revision and preserves its ECS health check. | No ALB or Service Connect endpoint. | Workflow checks rollout state, exact task definition, digest identity, running tasks, then uses ECS Exec to require `/health/live=200` and `/health/ready=200` for every task. | `/health/live` is process liveness. `/health/ready` remains 503 until Plan bootstrap and source/work/live workers converge; it is intentionally stricter. | Desired count one. The runtime supports safe overlap, but the construct does not declare stop-then-start bounds. | **As-built:** ECS liveness remains bootstrap-only; readiness automation depends on ECS Exec. **Target:** real-image ECS health uses `/health/live`. **Open:** accepted private readiness access mechanism and production evidence. |
| Collector Master | Accepted `dev` service and CDK task definitions render `exit 0`. The image bundles role-aware `/healthcheck.sh`, but the accepted runtime does not install `curl` and ECS revisions do not select the script. | Publishes a Service Connect endpoint. No separate routing-health gate is implemented. | Accepted workflow requires expected task definition, stable counts, and the commit-SHA image URI. It does not require ECS container `HEALTHY`. | `/api/health` proves the HTTP process. Control-loop progress, worker coordination, canonical dispatch, backlog, and state effects require separate logs/metrics/status evidence. | Current main capacity is one; ordinary ECS replacement can overlap and singleton enforcement is not structural. | **As-built:** bootstrap-only ECS health on both paths. **Pending implementation:** PR #20 installs `curl` and promotes `/healthcheck.sh` in the service path. **Target:** CDK and service paths reproduce it. **Open:** steady-state control-plane evidence and overlap policy. |
| Collector Worker | Accepted `dev` service and CDK task definitions render `exit 0`; the bundled role-aware script would probe port 3040 `/api/health`, but the accepted runtime lacks `curl`. | Client-only Service Connect membership; no published application route. | Accepted workflow verifies expected revision and image when tasks exist. Desired count zero succeeds without scaling or a running-image check. | Registration, queue consumption, progress, result reporting, and freshness are semantic evidence, not process liveness. | Desired count zero is normal. Verification does not scale up to probe; positive capacity may roll with overlap. | **As-built:** zero-scale-aware convergence with bootstrap-only ECS health. **Pending implementation:** PR #20 installs `curl`, selects `/healthcheck.sh`, and adds task-health verification. **Target:** both deployment paths reproduce the liveness contract. |
| Collector Realtime | Accepted `dev` derives the current task definition and preserves the Infra `exit 0`; the bundled role-aware script would probe port 3050 `/api/health`, but the accepted runtime lacks `curl`. | Standalone: no ALB or Service Connect. | Accepted workflow verifies the expected revision, stable counts, and image URI, but not ECS container health. | `/api/ready` requires current lease ownership and ready connectors. A live replacement may be legitimate standby; post-rollout ownership, connector state, write progress, and freshness are separate evidence. | Construct-enforced desired count one; rolling overlap may briefly create a live standby protected by lease/fencing. | **As-built:** correct application liveness/readiness separation, but bootstrap-only ECS health. **Pending implementation:** PR #20 installs `curl` and promotes service-side `/healthcheck.sh`. **Target:** CDK reproduces it. **Open:** bounded post-rollout ownership/readiness evidence. |
| Quant Bot fleet | Current CDK and image-derived service revisions use `exit 0`. The API exposes `/api/health`, which returns HTTP 200 with `ok` or `degraded` body state, but no ECS liveness command has been accepted for it. | ALB probes `/` on the API/UI port. This establishes control-plane routing, not Engine readiness. | Deployment derives the current task definition by named container, swaps image/config, and waits for ECS rollout `COMPLETED`. It does not independently verify container health, digest, or operator state. | Engine `state=running`, `is_ready=true`, strategy activity, venue connectivity, and trading correctness are operational signals. A task waiting for an operator start is valid after deployment. | Per-bot desired count is intended one; Infra uses stop-then-start bounds. Optional Vector is selected by stable container name. | **As-built:** control-plane routing plus bootstrap-only container health. **Target:** select and reproduce an HTTP/API process liveness probe. **Open:** exact command and post-rollout operational evidence. |
| Obs fleet | Current CDK and image-derived service revisions use `exit 0`. s6 supervises writer, evaluator, and MCP; writer `/` and `/health` are available, but exact aggregate ECS liveness remains unresolved. | MCP traffic targets port 8091, while target-group health deliberately probes unauthenticated writer `/` on port 8080. | Deployment derives the current `ObsContainer`, swaps image/config, and waits for ECS rollout `COMPLETED`. It does not verify child processes or semantic availability. | MCP may park when no token is configured. Token validity, evaluator progress, WAL/flush/compaction freshness, cold query correctness, and alerts are not deployment health. | Per-bot singleton with stop-then-start. A short Obs gap is accepted while trading continues separately. | **As-built:** ALB writer routing is distinct from MCP and semantic health; container health is still bootstrap-only. **Target:** application-specific writer/supervisor liveness. **Open:** exact multi-process failure boundary and semantic gate. |

## Cross-sequence audit and transition status

| Deployment unit | Accepted As-built `service -> CDK -> service` result | Required Target | Registry status |
| --- | --- | --- | --- |
| API and Academy | Service revision installs `/api/health`; CDK replaces it with `exit 0`; the next service deployment restores `/api/health`. | Both paths render the released-image `/api/health` contract. | **Transitioning — not conformant:** service path exists; CDK and state authorization remain. |
| Calculator | Service deployment preserves the current task definition's `exit 0`; CDK also emits `exit 0`. Docker image liveness and ECS readiness checks do not change the ECS container contract. | Both paths render `/health/live` for released images; readiness remains separate. | **Transitioning — not conformant:** exact liveness is accepted; both task-definition paths remain. |
| Collector master/worker/realtime | Accepted `dev` keeps `exit 0` through both service and CDK deployments. PR #20 would promote `/healthcheck.sh` only in the service path and is not As-built until merged. | Both paths render `/healthcheck.sh` for an authorized, complete, same-digest Collector unit. | **Transitioning — not conformant:** service implementation is pending; CDK and state authorization remain. |
| Quant Bot | Both paths currently retain `exit 0`. | Both paths render an accepted API process liveness probe without requiring operator activation. | **Open before transition:** exact liveness is unresolved; Infra MUST NOT invent a probe. |
| Obs | Both paths currently retain `exit 0`; ALB independently probes writer `/`. | Both paths render an accepted writer/supervisor liveness while keeping MCP and semantic signals separate. | **Open before transition:** exact multi-process liveness is unresolved; Infra MUST NOT invent a probe. |

The current implementation therefore does not yet satisfy the non-regression
invariant for any released deployment unit and MUST NOT be described as
conformant. These entries track transition work; they do not change repository
ownership of current As-built details.

## Required follow-up implementation

### Infrastructure

1. Replace catch-all empty SSM reads with error-aware results that distinguish
   `ParameterNotFound` from authorization, transport, throttling, and other AWS
   failures.
2. Require current ECS service absence plus explicit initial-bootstrap
   authorization before selecting Bootstrap. Define and preserve an auditable
   workflow input, durable lifecycle marker, or equivalent approved mechanism;
   absence alone MUST fail closed.
3. Reject lost or contradictory Released lifecycle state rather than
   reclassifying deleted services and parameters as Bootstrap.
4. Classify complete deployment units and validate partial parameters,
   immutable URI policy, allowed placeholders, and required shared-image
   digests.
5. Add a typed health-profile input used by every construct to render
   `exit 0` only for Bootstrap and the mapped application liveness for
   Released state.
6. Add script and CDK tests for both independent deployment sequences,
   including `ParameterNotFound` plus absent service without authorization,
   lost Released state, service-exists/image-missing, partial group, mismatched
   digest, and AWS error cases.
7. Update the Infra deployment view and bootstrap runbook after executable
   behavior changes. Do not describe this Target as already implemented.

### Service repositories

- API and Academy SHOULD decide whether ALB routing remains `/` or moves to the
  existing `/api/health`, harden immutable-image verification, and make any
  claimed external health gate enforce its result.
- Calculator MUST arrange for service and CDK revisions to converge on
  `/health/live`. The repository SHOULD replace or explicitly accept its
  ECS-Exec-dependent readiness gate without making ECS Exec an organization
  requirement.
- Collector PR #20 is pending implementation evidence, not As-built. After it
  merges, the repository SHOULD update its authority documents and this registry
  from the accepted branch. The transition still requires CDK convergence on
  `/healthcheck.sh`, atomic digest/state classification, and bounded semantic
  evidence for Master progress and Realtime ownership/connector convergence
  while preserving Worker zero scale and standby-safe liveness.
- Quant MUST select an API process liveness command that remains healthy while
  operator-controlled trading is stopped, and SHOULD verify the selected image
  plus named application container after rollout.
- Obs MUST select the multi-process container failure boundary and SHOULD add
  bounded writer/evaluator/pipeline evidence without making MCP tokens or query
  availability a container deployment gate.

These are transition follow-ups, not As-built claims in this organization
repository. Repository code, workflows, and canonical repository documentation
remain the current As-built authority.
