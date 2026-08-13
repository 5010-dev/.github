# Golden Path Agent-assisted application

- Status: Supported
- Package: `@5010-dev/golden-path-agent@1.0.0`
- Visibility: Private
- Owner: `5010-dev/engineering-tooling` maintainers
- Last reviewed: 2026-08-14
- General support: [open a `5010-dev/.github` issue](https://github.com/5010-dev/.github/issues/new) for triage by the `engineering-tooling` maintainers
- Sensitive security reports: [use the organization private vulnerability-reporting route](https://github.com/5010-dev/engineering-tooling/security/advisories/new)

This journey is an optional developer-host aid for applying the
[Developer Tooling Standard](../standards/developer-tooling/README.md). It does
not change the standard's normative meaning, become repository or CI authority,
or replace the manual bootstrap, adoption, and retirement journeys.

## Exact installation and invocation

Install the supported private package at its exact coordinate for both
supported developer hosts:

```bash
pnpm dlx @5010-dev/golden-path-agent@1.0.0 skill install --host all
```

Before installing, authenticate the `@5010-dev` scope to GitHub Packages and
authenticate GitHub CLI `gh` to `github.com` with read access to
`5010-dev/.github`; follow the exact released package
[setup instructions](https://github.com/5010-dev/engineering-tooling/blob/a1a7af61fe89434c1288a69b3114ba5725c6576d/README.md#install-the-package).

Invocation is always explicit:

| Host | Invocation |
| --- | --- |
| Codex | `$golden-path` |
| Claude Code | `/golden-path` |

Implicit invocation is disabled. Installing the host integration does not add
the package to a consumer manifest or lock, pin a consumer version, or install a
repository-managed runtime.

Update by replacing the package coordinate in that command with a newer exact
version and running `skill install --host all` again. Roll back by doing the
same with a prior exact version.

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

The supported `1.0.0` package is identified by the following release evidence:

| Evidence | Identity |
| --- | --- |
| Source commit | [`a1a7af61fe89434c1288a69b3114ba5725c6576d`](https://github.com/5010-dev/engineering-tooling/commit/a1a7af61fe89434c1288a69b3114ba5725c6576d) |
| Source tag | [`golden-path-agent-v1.0.0`](https://github.com/5010-dev/engineering-tooling/tree/golden-path-agent-v1.0.0) |
| Publication workflow | [`31736789411`](https://github.com/5010-dev/engineering-tooling/actions/runs/31736789411) |
| Package visibility | Private |
| Package SHA-256 | `62b0f85b775e929ec225bd90306720fc9e4d165ce664f7cb136ad3f61f96ced9` |
| Registry SRI | `sha512-Fhi7knxicEuHrsa/UOkcT9dxFrBzf+HVJYMMexl6eA0eXoVu6/jT+kPhQZ8iaB892ZFJEXE3a91RagYz1UboYQ==` |

These identities document the supported release; they are not a machine
locator or an automatic update instruction. Public `engineering-tooling`
releases `v0.1.0` through `v1.6.1` remain immutable audit history for the
retired Go executable line; this package is not a version of, locator for, or
compatibility bridge to that line. General questions use `5010-dev/.github`
Issues for triage by the `engineering-tooling` maintainers. Credentials,
vulnerability details, and other sensitive material must use the private
security-reporting route instead of a public issue or pull request.
