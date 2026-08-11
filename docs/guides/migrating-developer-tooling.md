# Migrating existing developer tooling

This guide removes the retired central Golden Path executable footprint while
preserving repository-owned behavior. It is a bounded retirement journey inside
the [Developer Tooling Golden Path](../golden-path/README.md), not the removal of
the Golden Path itself.

## Boundary classification

Check whether each footprint exists on unreleased `dev`, on `main`, or in a
released artifact. Unreleased development intermediates are corrected directly.
Published `engineering-tooling` tags and release artifacts remain immutable
audit history; they do not create an ongoing consumer-support obligation.

## Remove only the central managed footprint

When present, remove:

- `.github/golden-path-assets.json`;
- `.github/golden-path-request.json`;
- generated `.github/golden-path.yaml`;
- the central-calling `.github/workflows/developer-tooling.yml`;
- `scripts/golden-path` and its dedicated Just wrapper; and
- dependency policy, defer, observation, report, or security-closure files that
  exist only for the retired compiler.

An empty generated `.github/golden-path-exceptions.yaml` is also removable. If
it contains a real approved exception, preserve the exact requirement, scope,
owner, approval, expiry, and risk record in repository canonical documentation
before removing the generated schema-bound file.

Do not remove a similarly named repository-owned workflow merely because its
name contains `developer-tooling`. Inspect whether it calls
`5010-dev/engineering-tooling` or only the repository's own canonical CI.

## Preserve repository authorities

Preserve native roots, manifests, locks, `release-units.json`, root and imported
Just recipes, canonical quality CI, release/deployment workflows, and
repository-owned GitHub security visibility and routing.

End routine freezes and temporary defers according to their owner, expiry, and
exit condition. Security pull requests and default-branch alerts do not wait for
routine regrouping.

## Validate

Run only the owning repository's canonical CI after the removal. Confirm that no
remaining workflow or script installs, downloads, calls, or selects
`engineering-tooling`. Do not add a compatibility wrapper or issue a new
central tooling release to perform the removal. Re-enter the
[adoption journey](./adopting-developer-tooling.md) only for a concrete gap in
the repository-owned implementation; retirement alone does not require a
general rewrite.
