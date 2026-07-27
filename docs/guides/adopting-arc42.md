# Adopting the organization arc42 profile

Use this guide for a new engineering repository or an independently governed
engineering layer inside a mixed-purpose repository.

## 1. Define the engineering-system boundary

Write one sentence that names the system, its owner, and what is outside it.
Confirm that the boundary is architectural rather than a directory, provider,
model, process, or team boundary.

For a mixed-purpose repository, identify the other canonical authorities before
creating engineering documentation. A scientific paper or empirical result does
not move into arc42 merely because an engineering layer is added beside it.

## 2. Inventory authority

Locate the current owners for:

- implemented behavior and schemas;
- deployment topology and observed runtime state;
- API or event contracts;
- development and release procedures;
- diagnosis and recovery;
- dated validation evidence;
- scientific, empirical, legal, or product-policy facts; and
- consequential decision rationale.

Record conflicts and duplicates. Do not resolve them by choosing the most
convenient prose document; verify the concern's actual owner.

## 3. Scaffold the repository structure

From a checkout of the organization `.github` repository:

```bash
scripts/docs/scaffold-arc42.sh \
  --target /path/to/repository \
  --system-name "Example System" \
  --scope "Repository-wide engineering system"
```

The command fails before writing when any destination file already exists. Use
the [migration guide](./migrating-existing-documentation.md) instead of forcing
the scaffold over an established documentation tree.

## 4. Fill the L0 current view

Start with chapters 1, 3, and 4 to establish purpose, boundary, and strategy.
Then document building blocks and significant runtime/deployment scenarios.
Classify claims before adding detail:

- As-built claims cite current executable, generated, or observed evidence.
- Target claims state the remaining gap and promotion condition.
- Open claims state what is unresolved.
- Deprecated claims link the replacement or preservation rule.

Keep complete endpoint, environment, resource, and symbol inventories in their
owning generated or executable sources.

## 5. Record adoption

Add a repository ADR that:

- adopts `5010-arc42-v1`;
- declares the system scope;
- records the concern-based authority model;
- explains any local exception; and
- identifies the documentation validation gate.

## 6. Add L1 only when needed

Use the Compact, Standard, or Full templates when an internal boundary has
independent responsibility and meaningful failure, security, lifecycle,
contract, change, or quality complexity. Do not create twelve files for every
subsystem.

## 7. Validate and integrate

Run the organization reference check or the repository's equivalent:

```bash
/path/to/.github/scripts/docs/check-contract.sh --target .
```

Then run the repository's complete quality gate. Add the documentation check to
the repository's normal pre-commit or pull-request validation rather than
leaving it as an optional migration command.
