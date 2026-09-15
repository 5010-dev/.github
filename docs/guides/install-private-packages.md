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

Prefer a private temporary npm configuration that exists only for the install
session. The example below creates one with the GitHub Packages scope route and
a literal token-variable reference, then removes it on exit. It runs from its
temporary directory so a checkout's npm configuration does not override it.
`gh auth status` does not inject a token into npm or pnpm; the example passes the
selected GitHub CLI credential to the package-manager process.

This temporary user configuration replaces the usual user npm file for these
commands. Follow the owning repository's setup for any additional private
registries, proxies, or custom global directories; include required non-secret
settings explicitly in the temporary configuration. Resolve conflicting
package-manager environment overrides before running the example. Public npm
dependencies continue to use the package manager's default registry unless
explicitly configured otherwise.

Do not add the token-variable reference to a persistent user `.npmrc` for this
flow. When `NODE_AUTH_TOKEN` is unset outside installation, pnpm can warn on
unrelated commands; pnpm 10 can also ignore that file's scope route. If an older
setup already contains this reference, move its authentication entries into the
temporary setup while preserving unrelated user settings. Do not keep a token
exported merely to suppress these warnings.

The following **bash/zsh example is for a globally installed CLI**, after the
login/access checks and package-manager setup above. Replace the illustrative
coordinate with the exact one from the owning package guide before running it.
Library and repository-dependency installation must use the target directory
and installation procedure documented by its owner, not this temporary directory.

```sh
(
  set +x
  set -eu
  package_spec='@5010-dev/REPLACE_PACKAGE@REPLACE_EXACT_VERSION'
  case "$package_spec" in
    *REPLACE_*) printf 'Set the exact package coordinate first.\n' >&2; exit 1 ;;
  esac

  umask 077
  install_dir="$(mktemp -d "${TMPDIR:-/tmp}/private-package-install.XXXXXX")"
  trap 'rm -rf -- "$install_dir"' EXIT
  trap 'exit 129' HUP
  trap 'exit 130' INT
  trap 'exit 143' TERM
  cat > "$install_dir/npmrc" <<'NPMRC'
@5010-dev:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
NPMRC
  unset NPM_CONFIG_USERCONFIG npm_config_userconfig
  export NPM_CONFIG_USERCONFIG="$install_dir/npmrc"
  cd "$install_dir"

  # Select the previously checked stored login, not an ambient token override.
  unset GH_TOKEN GITHUB_TOKEN NODE_AUTH_TOKEN
  NODE_AUTH_TOKEN="$(gh auth token --hostname github.com)"
  test -n "$NODE_AUTH_TOKEN"
  export NODE_AUTH_TOKEN

  # pnpm can warn about invalid configuration and still exit successfully.
  # Capture both streams; only a clean, expected registry value may proceed.
  if ! registry="$(pnpm config get '@5010-dev:registry' 2>&1)"; then
    printf 'Could not read npm configuration. Diagnose it before installing.\n' >&2
    exit 1
  fi
  case "$registry" in
    https://npm.pkg.github.com|https://npm.pkg.github.com/) ;;
    *) printf 'Fix npm configuration warnings or the private scope route before installing.\n' >&2; exit 1 ;;
  esac
  pnpm view "$package_spec" version --registry=https://npm.pkg.github.com
  pnpm add --global "$package_spec"
)
```

The example does not print the token or leave its assignment in the parent
shell. The temporary directory and configuration are private to the current
user and removed on normal exit, command failure, or a handled interrupt. The
file contains only a literal environment reference, never the expanded token.
It rejects registry-check diagnostics even when pnpm returns exit code
zero, stopping before lookup or installation. Inspect the scope route and
variable references in your npm configuration locally without printing expanded
authentication values. A configuration substitution warning, failed lookup, or
failed install requires diagnosis before continuing; it is not a reason to retry
against public npm or create another credential. Run the package's version/help
or consumer check after installation with registry credential variables absent.
Existing credentials in a parent shell are not removed by the example's
subshell. Runtime AWS, database, or source-repository authentication follows the
package's own guide and is not granted by package installation.

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
