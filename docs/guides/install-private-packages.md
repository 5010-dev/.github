# Install private GitHub packages

This guide applies the [private package authentication contract](../standards/release-versioning/package-authentication.md)
to interactive developer installations. The package repository owns its exact
version, supported Node/package-manager versions, installation command, runtime
prerequisites, and support contact. CI uses its job-scoped repository token and
package Read grant instead of this interactive login flow.

## Check the intended login

Use the package's supported tools, then inspect GitHub CLI without showing the
token:

```sh
gh auth status --hostname github.com
```

Confirm the active account and host. Reuse an approved browser/OAuth login.
Environment overrides such as `GH_TOKEN` or `GITHUB_TOKEN`, or a token previously
imported into GitHub CLI, are not evidence that the browser login was selected.
Resolve that ambiguity before continuing; do not print their values or silently
switch to a different credential. A login failure is not a request to create a
PAT. When login is missing or expired, the developer completes:

```sh
gh auth login --hostname github.com --web --scopes read:packages
```

Use the OS credential store. If GitHub CLI reports plaintext credential storage,
restore a working credential store before using this flow. Do not choose
`--insecure-storage` as a workaround.

## Resolve scope and access separately

For an existing browser login missing `read:packages`, the developer consents to
the additional scope:

```sh
gh auth refresh --hostname github.com --scopes read:packages
gh auth status --hostname github.com
```

The administrator does not add a scope to the user's stored OAuth credential.
Conversely, OAuth scope consent does not grant package or organization access.
If the selected account/team lacks package Read, contact the package
administrator. If organizational OAuth approval is missing, request approval
from the organization owner. Complete SSO when required; ask the administrator
about an entitlement or policy denial.

Do not replace these actions with PAT issuance, another user's token, or shared
credentials. If the cause is unclear, stop and provide the owning support
contact with the package/version, account, registry, safe error code, and checks
already performed. Never include a token, a full environment/configuration
dump, or an unreviewed log. A private-package `404` can mean denied access or a
missing version; it is not sufficient evidence to choose either explanation.

## Registry routing and exact access

Follow the owning repository's routing setup. A repository-owned installer may
create and remove a private temporary npm configuration. A trusted user npm
configuration can instead contain these entries, merged with unrelated settings
and with the placeholder kept literal:

```ini
@5010-dev:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```

The scope route selects GitHub Packages while other npm packages keep their
normal registry. `gh auth status` does not inject a token into npm or pnpm.
An installer has to pass the selected GitHub CLI credential to its native
package-manager process.

The following **bash/zsh example is for a globally installed CLI**, after the
login/access checks and routing setup above. Replace the illustrative coordinate
with the exact one from the owning package guide before running it. Libraries
and repository dependencies use their owning installation command instead of
`pnpm add --global`.

```sh
(
  set +x
  set -eu
  package_spec='@5010-dev/REPLACE_PACKAGE@REPLACE_EXACT_VERSION'
  case "$package_spec" in
    *REPLACE_*) printf 'Set the exact package coordinate first.\n' >&2; exit 1 ;;
  esac

  # Select the previously checked stored login, not an ambient token override.
  unset GH_TOKEN GITHUB_TOKEN NODE_AUTH_TOKEN
  NODE_AUTH_TOKEN="$(gh auth token --hostname github.com)"
  test -n "$NODE_AUTH_TOKEN"
  export NODE_AUTH_TOKEN

  registry="$(pnpm config get '@5010-dev:registry')"
  case "$registry" in
    https://npm.pkg.github.com|https://npm.pkg.github.com/) ;;
    *) printf 'Fix the private scope route before installing.\n' >&2; exit 1 ;;
  esac
  pnpm view "$package_spec" version --registry=https://npm.pkg.github.com
  pnpm add --global "$package_spec"
)
```

The example does not print the token or leave its assignment in the parent
shell. A configuration substitution warning, failed lookup, or failed install
requires diagnosis before continuing; it is not a reason to retry against public
npm or create another credential. Run the package's version/help or consumer
check after installation with registry credential variables absent. Existing
credentials in a parent shell are not removed by the example's subshell. Runtime
AWS, database, or source-repository authentication follows the package's own
guide and is not granted by package installation.

## New-package documentation check

Check a new package's guide from a fresh installation context with only its
declared prerequisites and approved access. Record the exact version and actual
install/consumer result. A metadata lookup proves access to that metadata; it
does not prove tarball download, installation, or execution. Report synthetic
fixtures, CI registry verification, and developer-machine evidence separately.
Keep exact commands and evidence in the owning repository rather than adding
consumer inventories to this central guide.

## GitHub references

- [GitHub CLI browser login](https://cli.github.com/manual/gh_auth_login)
- [GitHub CLI scope refresh](https://cli.github.com/manual/gh_auth_refresh)
- [Package Read permissions and inheritance](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)
- [Request organization OAuth approval](https://docs.github.com/en/account-and-profile/how-tos/organization-membership/requesting-organization-approval-for-oauth-apps)

GitHub's [npm registry guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry)
documents PAT-based authentication. This organization selects approved GitHub
CLI OAuth reuse for developer installation; that selection is not a claim that
every token type or GitHub host supports the same route. An unavailable or
policy-blocked route is escalated to the owner instead of silently falling back
to PAT creation.
