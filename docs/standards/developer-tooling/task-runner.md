# Just task-runner contract

- Status: Accepted
- Standard version: `2026.08.7`

Just is the organization command façade. It does not replace native manifests,
locks, package scripts, build systems, test tools, repository-local programs, or
GitHub Actions orchestration.

## Root responsibility

The root `justfile` MUST own public command discovery and composition. It SHOULD
remain thin enough that meaningful logic can be tested outside Just.

Modularization is based on responsibility and namespace, not line count.

## Flat imports

Use `import` when a recipe must remain a flat root command such as `init`,
`check`, `ci`, `format`, `lint`, `typecheck`, `test`, or `build`.

An imported file:

- SHOULD own one responsibility such as setup, quality, or documentation;
- MAY share the root variable and dependency graph; and
- MUST resolve from a declared repository-local path or an immutable
  materialized asset.

Duplicate recipe and variable overrides MUST NOT be a general extension
mechanism. `allow-duplicate-recipes` and `allow-duplicate-variables` require an
explicit standard rule or approved exception.

## Namespaced modules

Use `mod` when an independent domain benefits from a user-visible namespace,
such as `ui`, `docker`, `release`, `deployment`, `documentation`, `database`, or
a bounded subsystem.

A module MAY own its settings, working directory, and internal recipes. It MUST
NOT be introduced only to reduce the number of lines in the root file. Module
source-directory and cross-module reference semantics MUST be accounted for.

## Repository-local scripts

Move logic to a checked-in script or native program when it contains substantial
branching, polling, retry, JSON transformation, diagnostics, cross-platform
behavior, or an independently testable safety boundary.

Just SHOULD retain only:

- the stable command name;
- argument validation and documented defaults;
- dependency composition; and
- invocation of the script or native program.

Deployment, release, migration, and state-repair implementations SHOULD be
locally executable outside workflow YAML.

## Simple repositories

A repository with one responsibility and a few short recipes MAY use one root
`justfile`. Splitting every Justfile into imports or modules is not required.

## Version and source

- A repository using Just modules MUST select a Just release that supports
  stable modules.
- The required minimum Just feature version MUST be declared by the
  repository's toolchain contract.
- Required recipes MUST NOT fetch and execute a mutable remote Justfile,
  default branch, `latest` URL, or redirecting raw URL at runtime.
- A shared Just asset MUST be materialized from a versioned bundle or delegated
  to a separately released, integrity-verified implementation.
- User home directories, parent repositories, and global Just search paths MUST
  NOT be correctness dependencies.

Rule IDs: `DT-CMD-*`, `DT-ASSET-*`.
