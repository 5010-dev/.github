# Protected package-tag profile validation — 2026-08-12

- Status: Passed
- Observed at: `2026-08-12T18:57:14+09:00`
- Central change base: `5010-dev/.github@e2d57914b9368e599327ab1d173edcf39526e813`
- Regression subject: `5010-dev/design-system@bad1017cd92999252a15ae27c8e073a1f19acc9a`
- Evidence scope: repository contracts and exact remote refs; no publication or
  registry mutation

## Question

Does adding the opt-in protected package-tag profile preserve validated `main`
as the default and leave the Design System's existing `dev` release preparation
to `main` publication flow unchanged?

## Source identity and observations

The read-only query
`git ls-remote --heads origin main dev` against
`https://github.com/5010-dev/design-system.git` returned the same exact commit
for both refs:

```text
bad1017cd92999252a15ae27c8e073a1f19acc9a refs/heads/dev
bad1017cd92999252a15ae27c8e073a1f19acc9a refs/heads/main
```

The exact source at that commit establishes:

- [repository contribution policy](https://github.com/5010-dev/design-system/blob/bad1017cd92999252a15ae27c8e073a1f19acc9a/CONTRIBUTING.md)
  blob `8d8c1581dac20ce7be26c6da25ba6b32497a3812` prepares package versions and
  changelogs on `dev`, fast-forwards `dev` to `main`, and publishes from `main`;
- [release preparation workflow](https://github.com/5010-dev/design-system/blob/bad1017cd92999252a15ae27c8e073a1f19acc9a/.github/workflows/release-prepare.yml)
  blob `9ca5cf966941ba7f37f13b1d60f26afe62457cbf` requires the `dev` ref and creates
  or updates the Changesets version pull request without publishing; and
- [release workflow](https://github.com/5010-dev/design-system/blob/bad1017cd92999252a15ae27c8e073a1f19acc9a/.github/workflows/release.yml)
  blob `7ab0f15b4bacd92bc4efea5dbf34c8ad0095ecf4` triggers only on `main` and owns
  package publication and release records.

The canonical opt-in path
`.github/release-policy/protected-package-tag.v1.json` does not exist at that
Design System revision.

## Executable regression

The central repository-owned test suite exercises a repository with and without
the opt-in contract. It proves that admission succeeds only for one exact
intent/version/changelog diff and fails when the contract is absent. It also
fails stale, multiple, channel-conflicting, version-mismatched, package-identity
mismatch, non-version manifest, destructive diff, schema/checker boundary,
unrelated-path, and sibling-release-unit mutations. It admits both supported
JSON and TOML native manifest selectors.

```bash
python3 scripts/docs/test-protected-package-tag-admission.py
scripts/docs/check-repository.sh
```

Both commands passed on the central change branch. The central diff does not
modify a Design System file, workflow, tag, package manifest, version, or
permission.

## Result and evidence boundary

Regression result: **passed**. The new profile is explicit opt-in; the observed
Design System remains on its existing validated-`main` publication profile.

This record is a time-bounded source and contract observation. It does not prove
that a Design System workflow ran, that a package was published, or that the
registry matches repository intent. Future Design System state remains owned by
that repository and must be re-read when a later decision depends on it. This
record is not a central current-version registry or release queue.
