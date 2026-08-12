# Runtime support and lifecycle

- Status: Accepted
- Standard version: `2026.08.8`
- Runtime catalog: [`runtime-support.v1.json`](./rules/runtime-support.v1.json)

Runtime policy uses three independent axes. It does not collapse upstream
status, organization adoption, and repository migration into one tier.

## Upstream lifecycle

| Value | Meaning |
| --- | --- |
| `current` | Stable current release not yet transitioned to an LTS or other long-support line |
| `active` | Stable with normal bugfix/security support |
| `maintenance` | Maintenance/security support without normal feature work |
| `security` | Security-only or otherwise restricted support |
| `prerelease` | Alpha, beta, RC, nightly, or other pre-stable release |
| `eol` | Upstream bugfix/security support ended |
| `unknown` | Upstream has no reliable maintenance window |

`current`, `prerelease`, and `unknown` are production-blocked by default and MAY
be used only in an explicitly declared evaluation context. A previous tagged
Zig stable with `unknown` lifecycle may be `compatibility-only` for a bounded
consumer or migration check with an owner and review date; it is not a
production default.

## Organization disposition

| Value | New repositories | Conformance |
| --- | --- | --- |
| `preferred` | Default | Pass |
| `supported` | Allowed | Pass |
| `compatibility-only` | Not a default | Pass with reason, owner, and review date |
| `blocked` | Prohibited | Fail unless a time-bounded exception applies |

An upstream-supported release is not automatically organization-supported.
Organization disposition does not rewrite upstream lifecycle.

## Migration state

| Value | Meaning |
| --- | --- |
| `none` | No migration required |
| `warning` | Support end is announced |
| `required` | Migration issue, owner, target, and deadline required |
| `exception` | Approved time-bounded operation beyond the deadline |

Migration state belongs to repository-local tracking. The central catalog MUST
NOT list repositories, their exact pins, or their current migration state.
`evaluation-only` describes an allowed usage context, not a migration state.

## Range and exact pin

Applications and deployable artifacts use one exact runtime for development,
CI, and production. Libraries declare a consumer support range and test matrix
while retaining an exact development/CI toolchain.

| Profile | Compatibility declaration | Exact execution authority |
| --- | --- | --- |
| Node.js/TypeScript | `package.json#engines.node` | Node in `mise.toml`/`mise.lock`; pnpm in `packageManager` |
| Python | `pyproject.toml#requires-python` | `.python-version` and uv-managed interpreter |
| Go | `go.mod#go` minimum | `toolchain` plus aligned mise pin |
| Rust | `Cargo.toml#rust-version` MSRV | `rust-toolchain.toml` exact stable |
| Zig | Explicit profile and ZON minimum | Exact tagged Zig and matching ZLS in mise lock |
| AWS CDK | Supported Node host and library compatibility | Exact Node and local dependency lock |
| Terraform/OpenTofu | `required_version` and provider constraints | Exact CLI and provider lock |
| Pulumi | Project, host-language, and provider compatibility | Exact CLI, host runtime, and dependency lock |

## Initial 2026.07 baseline

| Profile | Preferred | Supported | Compatibility-only | Blocked/evaluation |
| --- | --- | --- | --- | --- |
| Node.js | 24 LTS | 22 LTS | — | 26 Current evaluation-only; 20 and older EOL |
| Python | 3.14 | 3.13, 3.12, 3.11 | 3.10 until 2026-10 EOL with required migration | 3.15 prerelease |
| Go | 1.26 | 1.25 | — | 1.24 and older |
| Rust | Latest stable exact | N-1/N-2 for at most 90 days after a new stable | Lower consumer MSRV is a separate library contract | Older development toolchains and moving nightly |
| Zig | Latest tagged stable, initially 0.16.0 | — | Previous tagged stable with owner/review date | master/nightly |

Node's release schedule and LTS cadence may evolve; the catalog follows the
official lifecycle rather than assuming that every future annual major becomes
an organization LTS. A framework or AWS CDK host-runtime compatibility statement
does not extend Node support after upstream EOL.

The current exact release patch remains repository-owned and is recorded in its
native manifest, lock, or toolchain selector. The catalog uses typed line,
range, relative, or channel selectors whose grammar is defined by its schema.
The table is not permission to use a moving channel.

IaC tools combine native constraints with exact CLI, SDK, and provider pins.
Changing cloud provider or IaC engine is an architecture/state migration, not a
runtime-tier upgrade.

## EOL lifecycle

| Time before EOL | Migration state | Required action | Result |
| --- | --- | --- | --- |
| 180 days | `warning` | Stable warning and update work begins | Pass with warning |
| 90 days | `required` | Owner, migration issue, target, and deadline | Pass when evidence exists |
| 30 days | `required` escalated | Blocker review and owner escalation | Strong warning |
| EOL | `exception` or blocked | Approved exception required to continue | Fail without exception |

If upstream gives less notice, the same stages begin as early as possible.
When a security advisory, withdrawal, compromise, or integrity failure makes a
release unsafe, immediate prohibition takes precedence over the normal notice
window. The emergency update MUST record source, impact, replacement, and
exception guidance.

An EOL exception additionally records affected runtime and artifacts, operational
impact, migration issue and target, accountable owner, review date, and expiry.

Rust's N-1/N-2 supported grace is a maximum 90-day cadence buffer, not an
upstream LTS claim. The catalog records the stable-release anchor and exact
grace end date for deterministic review. It does not require a repository
exception during the grace.

## Catalog

The runtime catalog records official source metadata, check date, typed
selector, normalized lifecycle, organization disposition, policy deadlines,
and compatibility. Review the source links before changing it; consumer CI does
not query live release pages to reinterpret a committed pin.

Updates to runtime lines and IaC tooling arrive through reviewable compatibility
changes. Automation SHOULD open reviewable pull requests for supported patch
releases and new Rust stable releases, and MAY do so for other catalog changes.
It MUST NOT overwrite repository pins or deploy.

Rule IDs: `DT-RUNTIME-*`.
