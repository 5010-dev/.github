# Release and Versioning schemas

- Status: Accepted
- Standard version: `2026.08.2`

These Draft 2020-12 JSON Schemas support the opt-in
[protected package-tag publication profile](../protected-package-tag.md):

| Schema | Purpose |
| --- | --- |
| [`protected-package-tag-profile/v1`](./protected-package-tag-profile-v1.schema.json) | Repository-owned package release-unit, source, closure, tag, channel, isolation, permission, and ownership contract |
| [`package-release-intent/v1`](./package-release-intent-v1.schema.json) | Immutable reviewed release-unit, channel, exact version, and source-boundary intent |

Valid illustrative documents are under [`examples/`](./examples/). They use
reserved example identities and do not select a package name, initial version,
tag pattern, or current release state for any repository.

The profile binds both package identity and version to one native manifest. A
repository selects either JSON Pointer selectors for a JSON manifest or dotted
bare-key selectors for a TOML manifest. The native manifest remains the version
authority; the contract only tells admission where to read it.

The dependency-free reference checker requires Python 3.11 or newer and
validates the contract and the exact Git merge diff:

```bash
python3 scripts/docs/check-protected-package-tag-admission.py \
  --repository . \
  --base "$BEFORE_SHA" \
  --head "$AFTER_SHA" \
  --event-ref refs/heads/dev
```

The checker discovers the contract at
`.github/release-policy/protected-package-tag.v1.json` by default and derives
release unit, channel, version, and tag from repository state. It does not accept
those identities as command inputs. A repository MAY use a different canonical
contract path through `--contract`, but the workflow must keep that path fixed
rather than expose it as an untrusted dispatch input.

Schema and checker compatibility is `v1`. Correct them in place before a real
released consumer depends on their current shape. Once a repository pins a
released schema or checker identity, incompatible evolution requires a new
schema/checker major or a coordinated update before its publication boundary.

These schemas and the checker do not form a release queue or current-version
registry. They do not publish, inspect GitHub rulesets or pull-request approvals,
query a package registry, or prove workflow side effects. Those checks and all
credentials remain repository-owned.
