# Private package authentication

This contract separates publication, CI consumption, and developer-machine
installation. It applies to organization-owned private GitHub npm packages;
other registries retain their native authentication contracts. The operational
[installation guide](../../guides/install-private-packages.md) explains the
GitHub CLI path without selecting package versions or a shared installer.

## Identity and authority

| Context | Authentication and access |
| --- | --- |
| Publication | Repository-owned workflow credentials under [Release automation](./automation.md#permissions-and-credentials); GitHub Packages publication uses the repository `GITHUB_TOKEN` by default |
| CI consumption | Job-scoped `GITHUB_TOKEN` with `packages: read` and package access granted to the consuming repository; publication-time verification retains its applicable release-profile permission rules |
| Developer installation | The developer's approved GitHub CLI browser/OAuth login, package-read scope, and account/team access to the package |

A workflow token is not a developer login. Repository membership, source read
access, token scope, OAuth application approval, and package access are distinct
facts. Source access establishes package access only when the package's actual
inheritance configuration grants it. A token cannot grant its user an access
role the user does not hold.

## Local installation and failure handling

Local installation instructions and tooling MUST default to reuse of the
developer's approved GitHub CLI browser/OAuth authentication. They MUST check:

1. the intended GitHub host and active account have a valid login;
2. the selected credential permits package reads (`read:packages` for this
   GitHub CLI flow), with required organization OAuth approval and SSO access;
3. the account or team can read the intended package, including any inherited
   access; and
4. the native package manager can resolve the exact package/version through the
   intended registry using that credential.

An authenticated registry lookup is executable access evidence, not proof of a
successful installation or of a separately inspected scope/ACL configuration.
Tools MUST distinguish what they observed from what remains unknown. They MUST
NOT require package-administration access merely to prove a consumer can read.

An unmet condition MUST stop installation and identify the responsible action:

| Condition | Responsible action |
| --- | --- |
| Missing/expired login or wrong active account | The developer signs in again or selects the intended account |
| Missing package-read scope | The developer consents to that scope through GitHub CLI OAuth refresh |
| Missing package/team access or organization OAuth approval | The developer requests access from the package administrator or organization owner |
| Incomplete SSO authentication | The developer completes the organization's SSO flow; an entitlement or policy denial goes to the administrator |
| Unresolved denial, unavailable version, registry/configuration error, or network failure | Report known evidence, stop, and ask the owning support contact to distinguish access, publication, configuration, and service state |

An HTTP `401`, `403`, or `404` alone MUST NOT be treated as a complete diagnosis.
If the required scope or access cannot be established, tooling MUST NOT assume
permission or silently switch identity. After remediation, repeat the exact
package/version access check before installation.

Guides and tools MUST NOT offer PAT creation or rotation, a different person's
token, shared credentials, or increased write/admin scopes as fallback remedies
for installation failure. A newly issued token does not repair missing account
access. An alternative authentication provider requires an explicit, scoped
decision under [Adoption and exceptions](./exceptions.md); an install error does
not create that exception or authorize an automatic switch.

## Credential handling

`NODE_AUTH_TOKEN` and native equivalents are transport mechanisms, not proof of
credential origin or authorization. Installers MUST use the selected approved
identity and MUST NOT silently prefer an unrelated ambient token over it.

Registry credentials MUST be limited to the installation process or its native
credential provider. Expanded tokens MUST NOT enter Git, command arguments,
logs, shell history, support transcripts, manifests, or locks. Temporary auth
files MUST be accessible only to the current user and removed after success or
failure. Committed registry routing MAY contain an environment-variable
reference, never an expanded credential. Instructions MUST NOT disable TLS or
integrity verification to repair access errors.

Registry credentials MUST be removed from the subsequent package execution
context. A tool's own runtime authentication, such as access to a source
repository or a database, remains a separate repository-owned contract. This
policy does not revoke the developer's GitHub CLI login after installation or
replace the workflow publication-credential rules.

## Repository adoption and evidence

For new packages and substantive installation-path changes, the owning
repository MUST link this contract and document its exact coordinate, supported
tools, registry routing, native install command, and access-request contact.
The documented route MUST be checked in a fresh installation context without
relying on undeclared user npm configuration, an unrelated ambient token, or a
workspace package. Keep the evidence in normal repository validation or handoff
records; synthetic auth fixtures and privileged publisher CI do not establish a
developer's actual access.

This check complements [registry consumer verification](./profiles.md#registry-package-consumer-verification).
It does not require a personal OAuth login in every CI run, a separate manual
approval for every version, a shared bootstrap binary, or another publication
gate. Existing repositories adopt through their owning changes; publication of
this standard does not claim their implementation or operator acceptance is
complete.
