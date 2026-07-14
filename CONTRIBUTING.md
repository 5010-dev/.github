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

## Repository setup and quality gates

Follow the repository's README or development guide after cloning the repository
or creating a worktree. Install the pinned dependencies and toolchains, enable
repository-managed Git hooks, and run the documented check, test, and build gates
for the change.

Do not bypass repository-managed hooks with `git commit --no-verify`.

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

## Repository-specific instructions

Repositories should document setup, validation, architecture, release, and
deployment details in their README or development guide. A repository-local
`CONTRIBUTING.md` overrides this organization default and should be used only when
the repository genuinely requires a different contribution model.
