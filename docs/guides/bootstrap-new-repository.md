# Bootstrap a new repository

Bootstrap is the new-repository journey of the
[Developer Tooling Golden Path](../golden-path/README.md). It applies the
[Developer Tooling Standard](../standards/developer-tooling/README.md) through
repository-owned files. There is no active locator, binary, generator, reusable
conformance workflow, or organization workflow template.

Before editing files, choose the closest supported stack from the
[stack defaults](../golden-path/stack-defaults.md) and read only its applicable
normative profiles. Use the
[copy-once reference examples](../golden-path/reference-examples.md) as a
starting point; after copying, the repository owns every byte and future
change.

1. Start from the repository's actual language, infrastructure, artifact, and
   release needs.
2. Add native manifests, locks or integrity records, and exact toolchain
   selectors.
3. Add a root Justfile with truthful `init`, `check`, and `ci` recipes.
4. Add one repository-owned canonical CI workflow that runs `just ci` once.
5. Add repository-owned release and deployment workflows only when the
   repository has those boundaries.
6. Enable supported GitHub-native vulnerability visibility and a usable
   security remediation path. Routine version-update automation is optional;
   if adopted, choose its roots, cadence, grouping, owner, target branch, and
   queue limits from the repository's actual review and release capacity. Keep
   security visibility and routing independent from routine update budgets.
7. Add `.github/golden-path-native-roots.yaml` only when native dependency
   roots are otherwise ambiguous.
8. Run the repository's documented initialization and canonical CI locally.
9. Complete the
   [release-readiness checklist](../golden-path/release-readiness.md) for the
   boundaries the repository actually has, then review the change through its
   normal contribution flow.

Do not add a dummy manifest, central command registry, package-by-package manual
mapping, central approval queue, or generated control-plane metadata. A new
repository links to organization contracts and owns its executable As-built.
