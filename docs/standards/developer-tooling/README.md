# Developer Tooling Standard

- Status: Accepted
- Standard version: `2026.08.7`
- Contract version: `golden-path/v1`
- Last reviewed: 2026-08-11
- Owner: `5010-dev/.github` maintainers

This standard defines organization defaults for repository-owned developer
tooling. It is a contract, not a central executable control plane.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are
interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14) when
they appear in all capitals.

## Authority

The normative source is this directory on `5010-dev/.github`, changed through
a reviewed pull request under the organization contribution policy and this
repository's documented main-only exception.

Authority order:

1. this human-readable standard and its retained schema/catalog sources;
2. repository-local native-root declarations and documented exceptions;
3. repository-local manifests, locks, toolchain selectors, commands,
   `release-units.json`, workflows, and release configuration as executable
   As-built authority; and
4. repository CI, releases, deployments, and GitHub security state as current
   evidence.

Issue descriptions, generators, checkers, templates, historical release
artifacts, and another repository's implementation do not redefine this
standard.

## Active implementation boundary

Active central executable tooling: **none**.

The organization does not select or support a Golden Path binary, locator,
generator, updater, shared conformance workflow, managed asset bundle, live
report, or central dependency/security queue. Published
`engineering-tooling` tags and releases are immutable audit history only.

A future shared validator requires a separate accepted decision proving repeated
errors, off-the-shelf insufficiency, lower net operating cost, explicit file
inputs, a named owner, and a removal condition. Its maximum scope is
stateless deterministic read-only schema and explicit cross-reference
validation. It MUST NOT inspect live GitHub state, infer branch topology or
dependency graphs, interpret release-unit impact, assess alert closure,
orchestrate queues, or run repository CI.

## Applicability

The base contract applies to active, buildable organization-managed
repositories. Read only the language or IaC profiles that match actual source,
manifests, and infrastructure. Do not create metadata or no-op commands to claim
unused capabilities.

## Standard map

| Document | Normative responsibility |
| --- | --- |
| [Command contract](./command-contract.md) | Root `just` façade and local/CI semantics |
| [Task runner](./task-runner.md) | Just import, module, script, and namespace boundaries |
| [Toolchain management](./toolchain-management.md) | Runtime owners, exact pins, and lifecycle |
| [Dependency management](./dependency-management.md) | Native managers, manifests, locks, and frozen CI |
| [Distribution](./distribution.md) | Contract-only source, repository ownership, and retired release meaning |
| [Build hygiene](./build-hygiene.md) | Dependency automation, vulnerability, cache, SBOM, provenance, and platform rules |
| [Runtime support](./runtime-support.md) | Runtime lifecycle and organization disposition |
| [Conformance](./conformance.md) | Repository self-validation and evidence boundaries |
| [Exceptions](./exceptions.md) | Scoped, approved, expiring deviations |
| [Profiles](./profiles/README.md) | Language and IaC contracts |
| [Schemas](./schemas/README.md) | Repository-owned native-root and runtime-support data |

## Repository-owned contract

An applicable repository MUST:

- expose truthful root `just init`, `just check`, and `just ci` commands;
- use one native authority for each toolchain and dependency surface;
- commit required manifests, locks or integrity records, and exact selectors;
- keep canonical CI, release/deployment workflows, security state, and
  automation configuration local; and
- link to this standard instead of copying a generated central footprint.

A repository with ambiguous native roots additionally records
`.github/golden-path-native-roots.yaml` using the
[native-root schema](./schemas/golden-path-native-roots-v1.schema.json). The
file records only stable root IDs, repository-relative paths, and native
profiles. Existing repository-owned native-root files remain valid after the
central executable retirement.

## Ownership planes

| Plane | Owns | Does not own |
| --- | --- | --- |
| Organization policy | This standard, retained schemas, guides, and ADRs | Repository commands, status, or executable orchestration |
| Repository execution | Native manifests/locks, roots, Just graph, CI, release units, release/deployment workflows, dependency automation, security routing | Organization policy |
| Current evidence | Repository CI, releases, deployments, alerts, and pull requests | Permanent policy meaning |

## Adoption and change

New repositories follow the
[contract-only bootstrap guide](../../guides/bootstrap-new-repository.md).
Existing repositories follow the
[retirement migration guide](../../guides/migrating-developer-tooling.md).
No central registry tracks adoption.

`2026.08.7` retires the active executable Golden Path control plane and
removes dependency compiler, live report, generated metadata, locator, and
shared conformance contracts from the active standard. Historical standard
commits and published releases remain available as audit history and are not a
compatibility commitment.

Product, service, library, and API release versioning is outside this standard.
