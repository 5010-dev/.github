# Bootstrap a new repository with the Golden Path

This guide creates a reviewable repository-local Developer Tooling contract
from the immutable shared implementation. It is informative; the
[Developer Tooling Standard](../standards/developer-tooling/README.md), stable
rule catalog, and schemas remain normative.

The machine-readable
[bootstrap locator](./golden-path-bootstrap.v1.json) binds this procedure to an
exact release, source commit, archive checksums, verifier version, and reusable
automation commit. It is an operational locator, not a second policy source.

## Before generating files

1. Classify the repository using the standard's independent profile, artifact,
   and capability axes. Do not infer policy from an existing repository.
2. Use `applicability.status: applicable` for a buildable repository. Use
   `not-applicable` only for the bounded archived, generated-only, asset-only,
   or non-buildable cases allowed by the
   [conformance contract](../standards/developer-tooling/conformance.md#applicability).
3. Select the latest preferred runtime lines from the
   [runtime support catalog](../standards/developer-tooling/runtime-support.md)
   unless compatibility requirements justify a supported line.
4. Identify any required deviation before generation. Exceptions are recorded
   in `.github/golden-path-exceptions.yaml` and must satisfy the
   [exception contract](../standards/developer-tooling/exceptions.md); a local
   override or disabled check is not an exception.
5. Confirm the hosting baseline and optional adapters in the
   [GitHub capability matrix](./github-hosting-capabilities.md).

## Obtain the exact implementation

Use the release identity in the bootstrap locator. Download the archive for the
operator's OS and architecture and `release-manifest.json` from the exact tag.
The policy repository separately verifies the release's
`standard-snapshot-manifest.json` against its machine-readable rule, runtime,
schema, and example sources. Before execution:

- compare each downloaded file with the locator's SHA-256;
- run `gh attestation verify` with the exact GitHub CLI version, repository,
  signer workflow, source and signer digest, and tag ref declared by the
  locator; and
- confirm that the executable reports the exact release version declared by
  the locator.

Do not execute a moving tag, default-branch checkout, redirecting raw file, or
network-to-interpreter pipeline. A later release is adopted by reviewing an
updated central locator and generated diff, not by changing a local download to
`latest`.

## Preview and materialize

Download the
[documentation fixture](../../scripts/docs/fixtures/golden-path-bootstrap/documentation.yaml)
to an operator-owned path such as `/path/to/golden-path-request.yaml`, or create
an equivalent request there that reflects the real classification. Do not rely
on a repository-relative path into a checkout of this policy repository. The
fixture is intentionally small and exists to exercise the bootstrap path; it is
not the organization default profile.

With `GOLDEN_PATH_BIN` pointing to the verified executable and
`RELEASE_MANIFEST` pointing to the verified release manifest, preview without
writing:

```bash
"$GOLDEN_PATH_BIN" generate \
  --request /path/to/golden-path-request.yaml \
  --release-manifest "$RELEASE_MANIFEST"
```

Review the complete plan. Then materialize into a separate empty candidate
directory, never directly over an existing repository:

```bash
"$GOLDEN_PATH_BIN" generate \
  --request /path/to/golden-path-request.yaml \
  --release-manifest "$RELEASE_MANIFEST" \
  --write \
  --output /path/to/empty-candidate
```

The candidate owns its generated request, asset inventory, metadata, Just and
toolchain files, native manifests and locks, bootstrap script, and caller
workflow. Inspect these as repository code, set the caller's exact profile
array, customize only repository-owned behavior, and commit the reviewed files
through that repository's normal contribution flow.

## Enable repository-local validation

The preferred path is the caller generated with the release. The organization
[workflow template](../../workflow-templates/golden-path-quality.yml) is a
discovery starter for a repository that already has materialized Golden Path
files. It intentionally contains the invalid JSON sentinel
`profiles: 'REPLACE_WITH_EXACT_PROFILES'`. The reusable workflow propagates the
resulting checker usage error, so the job fails closed until the repository
replaces that value with the exact profile array from `.github/golden-path.yaml`.

Keep the caller's triggers, default-branch choice, path filters, concurrency,
permissions, runner, working directory, profile input, environment adapter, and
named secret forwarding repository-local. Keep the reusable workflow and setup
action on their full source commit and keep every release checksum exact.

Run the following before merging the repository's adoption change:

```bash
just init
just ci

"$GOLDEN_PATH_BIN" check \
  --root . \
  --evaluated-at 2026-08-01T00:00:00Z \
  --expected-profiles '["documentation"]'
```

Replace the example timestamp and profile array with the evaluation time and
actual declared profiles. A stable lifecycle does not by itself make
conformance platform-enforced. Under report-only enforcement, evidence is
visible without claiming that the hosting platform blocks merge. Repository
owners separately decide when their adoption becomes policy-required or uses a
paid platform-enforcement adapter.

## Existing repositories

Do not run new-repository generation over an existing tree. Follow
[Migrating existing developer tooling](./migrating-developer-tooling.md) and use
the released upgrade preview with a separate candidate directory. Migration
scope, scheduling, exceptions, and current conformance remain owned by that
repository and are not tracked by this central repository.
