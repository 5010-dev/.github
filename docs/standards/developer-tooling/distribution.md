# Developer Tooling contract distribution

- Status: Accepted
- Standard version: `2026.08.7`

## Normative source

The active Developer Tooling contract is distributed as reviewed source in
`5010-dev/.github/docs/standards/developer-tooling`. Consumer repositories
link to the applicable documents and implement them with repository-owned native
files and workflows.

There is no active machine locator, executable implementation release, asset
bundle, generator, updater, reusable conformance workflow, or managed file set.
A repository MUST NOT fetch and execute mutable central content from routine
local commands or CI.

## Repository ownership

Repositories own:

- native manifests, locks, and integrity records;
- toolchain selectors;
- `.github/golden-path-native-roots.yaml` when needed;
- `release-units.json` when used;
- the root and imported Just graph;
- canonical CI, release, deployment, and security workflows;
- dependency automation configuration; and
- accepted repository-local exceptions and current evidence.

A guide or historical generator inventory does not make repository-owned files
centrally managed. Removal of the retired control plane MUST preserve the
authorities above.

## Retained machine-readable contracts

The active machine-readable sources are limited to the native-root, exception,
and runtime-support contracts listed in
[the schema index](./schemas/README.md). Repositories MAY validate these explicit
files with an off-the-shelf JSON Schema implementation. The organization does
not require a shared custom validator.

## Historical releases

Existing `5010-dev/engineering-tooling` tags, GitHub Releases, checksums,
attestations, and embedded standard snapshots are immutable audit history. They
are not active, preferred, supported, or compatibility boundaries for current
consumers. The retirement does not publish a corrective tooling release or a
replacement locator.

## Change procedure

A normative change:

1. updates the human-readable rule and any retained schema/catalog in one
   reviewed `5010-dev/.github` pull request;
2. states the repository-owned migration impact;
3. does not create consumer pull requests unless an actual repository change is
   required; and
4. does not interpret a documentation version change as a request to upgrade a
   central binary.

Repository CI remains the repository's own release and merge evidence.
