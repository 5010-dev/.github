# CI runner selection and cost responsibility

- Status: Accepted
- Last reviewed: 2026-10-19
- Owner: `5010-dev/.github` maintainers

This policy complements the [Developer Tooling Standard](./README.md). Organization policy is centralized; executable CI remains repository-owned. Operational inventories, repository-specific runner selections, budget amounts and billing evidence belong in access-controlled operations records.

## Default and larger-runner selections

For Linux x64 quality jobs in private repositories, the default SHOULD be the standard GitHub-hosted `ubuntu-24.04` runner, currently 2 vCPU. Public repositories receive GitHub's standard public-runner specification; their free standard 4-vCPU runner is not a paid larger-runner selection. Platform-specific testing requirements remain intact.

A larger tier selected under this policy is an allowed choice, not a waiver of a MUST rule. Actual waivers of MUST rules follow [Golden Path exceptions](./exceptions.md).

A repository MAY use a paid 4- or 8-vCPU runner when evidence supports the job's requirements and cost. Optimize the actual bottleneck first. Select the smallest suitable tier; a mandatory sequential upgrade through every tier is unnecessary when memory, disk or measured behavior already determines the choice. A larger machine is not an optimization by itself.

The change record MUST identify the job, owner, source revision, complete test/gate inventory, event and cache conditions, runner resources, observed durations and queue time, rounded execution cost, expected frequency, monthly cost increment and concurrency ceiling. Use three representative successful hosted observations for a new performance selection; retain failures and cancellations. Reuse valid measurements when restoring an identical validated tree instead of paying for a duplicate experiment.

Keep tests, correctness checks and the canonical root `just ci` contract. Do not remove tests, loosen timeouts or retries, or weaken cache trust to make a runner comparison pass. Report CPU, RAM, disk, image and source differences honestly.

Cost-neutral improvements are preferable. Additional spend may be justified by meaningful waiting-time or resource benefits, but the responsible repository and budget owners must accept the explicit monthly increment through the existing review process. There is no universal minimum percentage improvement or additional approval hierarchy.

## Access and configuration

Use standard runner labels for the default tier. Larger runners MUST use organization-managed groups with an explicit approved repository allowlist and a documented maximum concurrency; public access remains disabled unless separately justified. Workflow-specific restrictions MAY be used only when supported by the account plan and verified in the live API.

Do not provision an always-present paid tier merely to complete a tier catalogue. Keep current names and capacity when there is only one approved consumer and a rename would add no operational benefit. Extend an existing appropriate pool only for a real approved consumer and an explicit cost/capacity decision.

Repositories own workflow selectors, triggers, Just graphs, caches and timeout settings. Examples can be copied once; this policy does not introduce a runtime configuration loader, generated managed files, a central CI controller or a reusable conformance workflow. A document in `.github` does not automatically enforce arbitrary runner policy; runner-group access and budget settings provide actual controls.

## Cost and review

Compute job execution estimates using `ceil(job_seconds / 60) × runner_rate`, then sum jobs and attempts. Apply any included standard-runner allowance once per account billing period, across eligible jobs; larger runners do not use that allowance. Keep gross usage, discounts and net charges separate. Idle larger-runner definitions have no execution fee; removing them reduces accidental-use exposure rather than providing an idle-VM saving.

Use the existing organization Actions budget as the primary spending control. Do not silently increase it or replace it with overlapping repository/SKU hard budgets. Budget owners maintain native threshold alerts, review usage and demand at least weekly, and reconcile the previous UTC month's repository/SKU gross, discounts and net at month close. Forecast demand separately from spending that a hard stop permits. A concurrency ceiling limits simultaneous use, not monthly spend.

A larger-runner selection is reconsidered when a substantial CI/workload optimization changes its benefit, or during the normal cost review. This does not require a new performance experiment every month.

Before deleting a pool, verify current dev/main and open-PR workflow references, authorized repository access, and queued/running/waiting jobs. Coordinate real remaining consumers first. Archived commits or hypothetical future consumers do not require indefinite preservation. Preserve restoration information and delete an empty group only after its runner and live references are gone. Runner cleanup MUST NOT trigger a production promotion or modify another team's branch, runtime state or Git configuration.

## References

- [GitHub runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [GitHub runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing)
- [Runner-group access](https://docs.github.com/en/actions/using-github-hosted-runners/controlling-access-to-larger-runners)
- [Budgets and overlapping controls](https://docs.github.com/en/billing/how-tos/set-up-budgets)
- [FinOps principles](https://www.finops.org/framework/principles/)
