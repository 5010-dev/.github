# Golden Path Agent-assisted application

- Status: Supported
- Package: `@5010-dev/golden-path-agent@1.0.1`
- Visibility: Private
- Owner: `5010-dev/engineering-tooling` maintainers
- Last reviewed: 2026-08-14
- General support: [create an Engineering issue in Linear](https://linear.new?team=ENG) for triage by the `engineering-tooling` maintainers
- Sensitive security reports: [use the organization private vulnerability-reporting route](https://github.com/5010-dev/engineering-tooling/security/advisories/new)

Linear is the support intake and work-tracking system. Reviewed source at
`5010-dev/.github@main` remains the policy and Golden Path authority.

This journey is an optional developer-host aid for applying the
[Developer Tooling Standard](../standards/developer-tooling/README.md). It does
not change the standard's normative meaning, become repository or CI authority,
or replace the manual bootstrap, adoption, and retirement journeys.

## Exact installation and invocation

Persist the supported private package at its exact coordinate, then install and
check both host Skills:

```bash
pnpm add --global @5010-dev/golden-path-agent@1.0.1
golden-path-agent skill install --host all
golden-path-agent skill check --host all
```

Before installing, obtain package `Read`, configure a personal access token
(classic) with `read:packages`, authorize it for organization SSO when
applicable, configure the user-level `@5010-dev` npm scope, and confirm that
pnpm's global bin directory is on `PATH`. GitHub CLI `gh` must be
authenticated to `github.com` with read access to `5010-dev/.github`.
Follow the exact released package
[access, authentication, and setup instructions](https://github.com/5010-dev/engineering-tooling/blob/8dfdac46dc9886e69dc4f33cf0a658c86353d3a3/README.md#package-access-and-authentication).
Package and `gh` credentials are separate; neither belongs in a consumer
repository.

Invocation is always explicit:

| Host | Invocation |
| --- | --- |
| Codex | `$golden-path` |
| Claude Code | `/golden-path` |

Implicit invocation is disabled. Installing the host integration does not add
the package to a consumer manifest or lock, pin a consumer version, or install a
repository-managed runtime.

Update or roll back by replacing the coordinate in `pnpm add --global` with a
newer or prior exact version, then rerun `skill install --host all` and
`skill check --host all`.

Do not use `latest`, a range, or another moving selector. Installation does not
automatically regenerate repository files or open consumer upgrade pull
requests.

## Authority binding and write boundary

At execution time, the Agent resolves the current `5010-dev/.github` `main`
authority read-only. It binds the resulting plan to the exact authority commit
SHA and the SHA-256 digest of each authority document it used. A branch name
by itself is not a sufficient binding for a later write.

`plan` does not write to the repository. Only an `apply` that follows the plan
and receives explicit approval may write repository files. If the authority
binding can no longer be reproduced, the Agent must resolve and plan again
before an `apply`.

Every file created or changed by an approved `apply` is immediately owned by
the repository. The Agent retains no managed-file boundary or ongoing ownership
and provides no automatic regeneration or upgrade pull requests.

`check` is report-only. It does not execute or replace the repository-owned
`just ci`; the owning repository runs that canonical gate through its normal
local and CI paths.

## Control-plane exclusions

This supported journey does not add a locator, central checker,
generator/upgrader, approval queue, organization registry, or shared workflow.
It creates no consumer dependency or version pin, owns no managed runtime, and
does not make the Agent or its package a source of normative policy.

## Release identity

The supported `1.0.1` package is identified by the following release evidence:

| Evidence | Identity |
| --- | --- |
| Source commit | [`8dfdac46dc9886e69dc4f33cf0a658c86353d3a3`](https://github.com/5010-dev/engineering-tooling/commit/8dfdac46dc9886e69dc4f33cf0a658c86353d3a3) |
| Source tag | [`golden-path-agent-v1.0.1`](https://github.com/5010-dev/engineering-tooling/tree/golden-path-agent-v1.0.1) |
| Publication workflow | [`31758196133`](https://github.com/5010-dev/engineering-tooling/actions/runs/31758196133) |
| Package visibility | Private |
| Package SHA-256 | `a52dba9f89ff32eb07d58bf89c6f6724ca4dfce234bae633877f9be41bd801f7` |
| Registry SRI | `sha512-nrvyu5OC4k4wZN6W9Gnis3T5v4JdTx3PiRjDjvrC1gFFnasMD2PmbeJ1bG4AzQUOJKpQhwfBN6TLm079gPT6jA==` |

These identities document the supported release; they are not a machine
locator or an automatic update instruction. Public `engineering-tooling`
releases `v0.1.0` through `v1.6.1` remain immutable audit history for the
retired Go executable line; this package is not a version of, locator for, or
compatibility bridge to that line. General questions use the
[Engineering Linear intake](https://linear.new?team=ENG) for triage by the
`engineering-tooling` maintainers. Credentials, vulnerability details, and
other sensitive material must use the private security-reporting route instead
of a general support issue or pull request.
