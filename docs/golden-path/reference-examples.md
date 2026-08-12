# Golden Path reference examples

These examples are deliberately small. Copy only the applicable file or part,
replace the named choices, and commit the result as repository-owned source.
They are not generated assets and are not updated by a central release. The
governance repository parses the linked YAML and TOML files with standard
language parsers and the Just files with Just itself; it does not execute their
recipes or validate a consumer repository.

## Exact toolchain selector

Choose exact versions from the applicable profile and runtime-support catalog.
Do not paste the angle-bracket tokens unchanged.

Start from the syntax-checked
[Node toolchain selector](./examples/toolchain-node.toml).

Replace `node` with or add `go`, `uv`, Rust support tools, IaC CLIs, and workflow
linters only when the repository uses them. The native runtime declaration must
agree with this selector.

## Root Just façade

Use native commands rather than copying their semantics into a central wrapper.
These compact examples show the command shape, not a universal build graph.

Start from the syntax-checked [Node.js/TypeScript](./examples/node.just),
[Go](./examples/go.just), or [Python](./examples/python.just) Just example.

Here `scripts/pnpm` is a repository-owned, reviewed userland bootstrap that
derives the exact pnpm version from `package.json#packageManager` and verifies
what it executes. Keep an equivalent mechanism if the repository uses another
path; do not assume bundled Corepack or add pnpm as an independent mise pin.

Adjust source paths, artifact builds, supported-runtime matrices, race or native
extension lanes, and credentialed tests to the real repository. Never represent
an unavailable capability with a successful no-op.

For a polyglot repository, keep those recipes in repository-local modules and
let the root `check` and `ci` call each applicable module. Do not merge native
locks or make one package manager authoritative over another.

## Repository-owned canonical CI

Pin reviewed actions to immutable commit SHAs. This example runs the canonical
gate exactly once; add repository-specific permissions, auth, service, matrix,
and release steps only when required.

Start from the syntax-checked
[repository-owned canonical CI example](./examples/canonical-ci.yml).

Review action pins at adoption time. A central conformance workflow must not
call this workflow or run `just ci` again.

## Dependabot starting point

Dependabot is the default adapter when a repository chooses an automated
dependency adapter. Enumerate actual native roots and ecosystems; do not add
entries for absent manifests. The example disables routine version-update pull
requests with `open-pull-requests-limit: 0` while preserving Dependabot security
updates. Its required `schedule` field is not an organization routine cadence
because the example has no positive routine pull-request budget.

Start from the syntax-checked [Dependabot example](./examples/dependabot.yml).

Replace `npm` and `/` with the actual ecosystem and native root. Use one
operational bot owner per dependency surface. Renovate may replace Dependabot
for a documented need; it must not duplicate the same surface.

Automated routine version-update pull requests are a repository opt-in. To
enable them, deliberately choose a positive per-entry limit and a cadence that
fits repository activity, release and deployment effects, test confidence, and
review capacity, then add the repository's routine target branch. Define
compatible groups where they reduce review load, and keep runtime, major,
pre-1.0, base-image, IaC, and release-impacting changes reviewable. The Golden
Path does not prescribe a weekly cadence or numeric budget.

Dependabot security-update pull requests are based on the repository's default
branch. The security-only example therefore omits `target-branch`; GitHub states
that an entry with a non-default `target-branch` applies only to version updates.
Preserve alerts and security updates even when routine updates target `dev`. If
the repository's accepted branch model requires retargeting a security pull
request to `dev`, keep that workflow repository-owned, give it only
`pull-requests: write`, authenticate the Dependabot head repository and branch,
and verify final alert closure only after the fixed lock reaches the default
branch. Security work never waits for routine grouping.

## Ambiguous native roots

Use this file only when manifests and native workspace files do not make the
roots unambiguous:

Start from the syntax-checked
[ambiguous native-roots example](./examples/native-roots.yml).

Validate the owned copy against the
[native-root schema](../standards/developer-tooling/schemas/golden-path-native-roots-v1.schema.json).

## Bounded exception record

Keep an exception in repository canonical documentation or an ADR:

```markdown
### Developer Tooling exception: <short name>

- Requirement: <document and section>
- Scope: <exact repository surface>
- Reason and risk: <why and what can fail>
- Compensating control: <current protection>
- Owner: <accountable person or team>
- Approved by: <authority and date>
- Expires: <date>
- Exit condition: <observable condition that removes the exception>
```

An exception is not a central queue item. Its owner closes, renews, or removes it
through the repository's normal review process.
