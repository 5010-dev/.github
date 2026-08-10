# Bootstrap a new repository

Bootstrap is a repository-owned implementation of the
[Developer Tooling Standard](../standards/developer-tooling/README.md). There is
no active Golden Path locator, binary, generator, reusable conformance workflow,
or organization workflow template.

1. Start from the repository's actual language, infrastructure, artifact, and
   release needs.
2. Add native manifests, locks or integrity records, and exact toolchain
   selectors.
3. Add a root Justfile with truthful `init`, `check`, and `ci` recipes.
4. Add one repository-owned canonical CI workflow that runs `just ci` once.
5. Add repository-owned release and deployment workflows only when the
   repository has those boundaries.
6. Enable GitHub-native dependency and security features appropriate to the
   repository. Keep security visibility and routing independent from routine
   update budgets.
7. Add `.github/golden-path-native-roots.yaml` only when native dependency
   roots are otherwise ambiguous.
8. Run the repository's documented initialization and canonical CI locally,
   then review the change through its normal contribution flow.

Do not add a dummy manifest, central command registry, package-by-package manual
mapping, central approval queue, or generated control-plane metadata. A new
repository links to organization contracts and owns its executable As-built.
