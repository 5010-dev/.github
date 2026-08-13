# Contributing

Repositories in the `5010-dev` organization use a simplified Gitflow model. The
model keeps production history linear and auditable while allowing lightweight
maintenance work to move quickly.

## Branch roles

| Branch        | Role                                                                         |
| ------------- | ---------------------------------------------------------------------------- |
| `main`        | Production branch and the only deployment source                             |
| `dev`         | Development and integration branch for the next production release           |
| Work branches | Isolated feature, fix, refactoring, documentation, test, or maintenance work |

`main` must contain only commits promoted from `dev`. Do not implement product
changes directly on `main`.

This branch model and integration flow are organization policy. Repositories own
their CI and deployment triggers, path filters, and ref-to-environment mappings
within this model; those choices do not redefine branch roles or pull request
targets.

A repository that cannot follow this branch model must record an explicit
exception in its canonical repository documentation or an ADR. The exception
must state its scope, rationale, risks, approval authority, review conditions,
exit conditions, and relationship to this policy. An implicit or undocumented
branch model is not an accepted repository variation.

## Repository setup and quality gates

Follow the repository's README or development guide after cloning the repository
or creating a worktree. Install the pinned dependencies and toolchains, enable
repository-managed Git hooks, and run the documented check, test, and build gates
for the change.

Do not bypass repository-managed hooks with `git commit --no-verify`.

## Organization engineering standards

Active buildable repositories must follow the
[Developer Tooling Standard](https://github.com/5010-dev/.github/blob/main/docs/standards/developer-tooling/README.md).
It defines the root Just command contract, toolchain and native dependency
authority, language and IaC profiles, runtime support, repository-owned
validation, and time-bounded exceptions. The active central executable tooling
identity is `none`: repositories link to the contract and keep their exact
commands, manifests, locks, native roots, release units, workflows, current
evidence, and approved exceptions local. The
[contract-backed, repository-owned Golden Path](https://github.com/5010-dev/.github/blob/main/docs/golden-path/README.md)
provides the supported bootstrap and adoption journeys, stack defaults,
copy-once examples, and release-readiness checklist. New repositories follow
its
[bootstrap journey](https://github.com/5010-dev/.github/blob/main/docs/guides/bootstrap-new-repository.md)
and the
[GitHub hosting capability profile](https://github.com/5010-dev/.github/blob/main/docs/guides/github-hosting-capabilities.md)
without installing a central binary, locator-selected release, reusable
conformance workflow, or managed asset bundle.

Changes to shared platform boundaries, deployment workflows, or infrastructure
integration must follow the relevant organization engineering contract. ECS
services must follow the
[ECS deployment contract](https://github.com/5010-dev/.github/blob/main/docs/platform/ecs-deployment-contract.md).
ECS service release workflows must also follow the
[ECS service delivery workflow standard](https://github.com/5010-dev/.github/blob/main/docs/platform/ecs-service-delivery-workflow-standard.md),
including its repository-local exception and pull request conformance formats.

Engineering systems and independently governed engineering layers must follow
the
[engineering documentation standard](https://github.com/5010-dev/.github/blob/main/docs/standards/engineering-documentation/README.md).
The organization arc42 profile is the canonical engineering-documentation spine
for architecture goals, boundaries, responsibilities, runtime and deployment
views, cross-cutting concepts, quality requirements, risks, and accepted target
state.

Concern-specific authorities remain with their owners. Executable code, schemas,
generated contracts, runbooks, deployment evidence, scientific designs, and
empirical results are linked from the architecture corpus rather than absorbed
into it. A package, process, provider, model, or directory does not require a
separate arc42 corpus unless it has an independently reviewable responsibility,
failure, security, change, or quality boundary.

Repository documentation should link to organization contracts and describe
only repository- or layer-specific resource names, configuration paths,
deployment commands, authority mappings, implementation status, and accepted
exceptions. Do not copy an organization contract into individual repositories.
A repository-specific exception must be explicit, justified, and linked to an
architecture decision record or equivalent review.

## Choosing direct development or a pull request

Direct commits to `dev` are allowed. They are commonly appropriate for small
fixes, documentation, and routine maintenance, but they are not restricted to
those categories.

Use a dedicated work branch and pull request when a change is substantial, risky,
benefits from review, or should be discussed independently. Work branches must
start from the latest `origin/dev`.

Recommended branch prefixes include:

- `feature/...`
- `fix/...`
- `refactoring/...`
- `docs/...`
- `test/...`
- `chore/...`

The list is descriptive rather than exhaustive. Prefer a clear branch purpose
over a generic name. Do not include a Linear issue identifier in the branch name;
link planning context in the pull request instead.

## Direct commits to dev

Synchronize `dev`, make the change, run the repository's required quality gates,
and create a Conventional Commit:

```bash
git switch dev
git pull --ff-only origin dev
git add <paths>
git commit
git push origin dev
```

Do not force-push `dev`.

## Pull requests

1. Synchronize `dev`.
2. Create a work branch from the latest `origin/dev`.
3. Commit with Conventional Commits.
4. Run the repository's documented quality gates after rebases and before
   opening or updating a multi-commit pull request.
5. Push the work branch and open a pull request targeting `dev`.
6. Complete the organization pull request template.
7. Merge with rebase merge after review and required checks pass.

```bash
git switch dev
git pull --ff-only origin dev
git switch -c feature/example
```

Rebase a work branch onto an updated `dev`; do not merge `dev` into the work
branch. Do not use merge commits or squash merge. Keep commits independently
understandable and ready for rebase and fast-forward integration.

## Commit messages

All commits follow Conventional Commits.

```text
type(scope): imperative summary

- Explain the behavior that changed and why.
- Add implementation or operational details that are not obvious from the diff.
- Call out compatibility, migration, deployment, or follow-up considerations.
```

Common commit types are:

- `feat`: new user- or consumer-facing capability
- `fix`: bug fix
- `docs`: documentation-only change
- `refactor`: internal restructuring without a behavior change
- `test`: test-only change
- `build`: build system or dependency change
- `ci`: CI/CD configuration change
- `chore`: repository maintenance that does not fit another type
- `perf`: performance improvement
- `revert`: revert of an earlier commit

Use a short, lowercase, kebab-case scope when a package or subsystem is clear.
The summary should be imperative and describe the outcome. Separate the body from
the header with a blank line, and prefer concrete bullet points for non-trivial
changes.

Do not include a Linear issue identifier in the commit subject. Link Linear
issues, ADRs, GitHub issues, and related pull requests in the pull request body.

## Promoting dev to main

Promotion is a fast-forward-only operation. Synchronize and validate `dev`, then
update `main` without creating a merge commit:

```bash
git switch dev
git pull --ff-only origin dev

# Run the repository's documented validation gates.

git switch main
git pull --ff-only origin main
git merge --ff-only dev
git push origin main

git switch dev
```

If the fast-forward merge fails, stop and resolve the branch divergence
deliberately. Do not replace `--ff-only` with a merge commit.

Production hotfixes must not bypass the `dev` to `main` promotion flow without
explicit maintainer direction.

## Releases and versioning

Validated-`main` publication is the organization default. Once a release tag,
registry version, or artifact is published, treat it as immutable; publish a
correction version and use an ecosystem-native deprecate, yank, or retract
operation when appropriate.

A monorepo that independently releases a registry package and a service or
application MAY opt in to the narrowly scoped
[protected package-tag publication profile](https://github.com/5010-dev/.github/blob/main/docs/standards/release-versioning/protected-package-tag.md).
The opt-in is valid only for the declared package release unit and does not make
`dev` a deployment target, change `main` as the production source for sibling
services or applications, or alter repositories that omit the profile contract.
The repository must materialize a PR-based release intent through a protected,
explicit merge and satisfy the profile's exact merge-diff, protected-tag,
immutability, isolation, evidence, and least-privilege requirements before
publication.

If an admitted package publication attempt fails before creating any package
tag or registry version, the repository MAY preserve the same version only
through the profile's separate append-only, PR-mediated pre-mutation recovery
authorization. A normal workflow rerun and the historical release intent are
not renewed publication authority. Any tag, registry version, partial immutable
state, or successful publication followed by verification failure remains under
the immutable-identity correction and verification rules.

Organization release units must follow the
[Release and Versioning Standard](https://github.com/5010-dev/.github/blob/main/docs/standards/release-versioning/README.md).
It defines artifact profiles, version and release identity, compatibility
lifecycle, release evidence, automation boundaries, and exceptions.

Each repository owns its exact versions, release units, native manifests, tag
format, changelog policy, release automation, current support state, and release
history. Document those details in the repository README or development guide.

Every production release must be traceable to its source commit, an applicable
tag or ref or a repository-native release identifier, and its exact artifact
or deployment identity. Git tags, GitHub Releases, changelog files, checksums,
SBOMs, provenance, and attestations apply according to the artifact profile;
they are not universal requirements for every deployment.

## Repository-specific instructions

Repositories should document setup, validation, architecture, release, and
deployment details in their README or development guide. A repository-local
`CONTRIBUTING.md` overrides this organization default and should be used only when
the repository genuinely requires a different contribution model. An
engineering system's canonical documentation entry point, arc42 scope, adopted
organization profile, and concern-based authority map remain repository-local
even when the organization templates are used to create them.
