# Developer tooling profiles

Profiles define language or IaC-specific native authorities and quality/build
contracts. Artifact types and capabilities remain independent metadata axes.

## Profile identifiers

| Identifier | Document | Activation |
| --- | --- | --- |
| `node-typescript` | [Node.js and TypeScript](./node-typescript.md) | Node/TypeScript source or manifest |
| `python` | [Python](./python.md) | Python project or package |
| `go` | [Go](./go.md) | Go module/workspace |
| `rust` | [Rust](./rust.md) | Cargo package/workspace |
| `zig` | [Zig](./zig.md) | Intentionally adopted Zig artifact |
| `zig-toolchain` | [Zig](./zig.md) | C/C++ project using Zig only as a compiler |
| `infrastructure-aws-cdk` | [Infrastructure](./infrastructure.md) | AWS CDK app |
| `infrastructure-terraform` | [Infrastructure](./infrastructure.md) | Terraform root |
| `infrastructure-opentofu` | [Infrastructure](./infrastructure.md) | OpenTofu root |
| `infrastructure-pulumi` | [Infrastructure](./infrastructure.md) | Pulumi project |
| `documentation` | [Command contract](../command-contract.md) | Documentation repository with deterministic validation |

`base` is implicit and MUST NOT be listed as a profile.

## Artifact types

The initial catalog supports:

- `application`
- `service`
- `library`
- `cli`
- `package`
- `binary`
- `container`
- `infrastructure`
- `tooling`
- `documentation`

Artifact type controls build, package, support-matrix, and release rules without
creating combined profile IDs.

## Capability identifiers

The initial catalog supports:

- `format`
- `lint`
- `typecheck`
- `test`
- `build`
- `package`
- `publish`
- `coverage`
- `fuzz`
- `unsafe`
- `native-extension`
- `cgo`
- `released-artifact`
- `dependency-automation`
- `cache`
- `devcontainer`

A repository declares only capabilities it actually implements. A selected
profile may make a capability mandatory for an artifact type.

## Polyglot repositories

A polyglot repository MAY select multiple profiles and independent native build
roots. Each toolchain and dependency graph retains one operational owner. Root
Just commands orchestrate the selected profiles without copying native
semantics into the central standard.

Profile conflicts are configuration errors. A combined repository MUST NOT make
one ecosystem's lockfile, runtime installer, or formatter authoritative over an
unrelated ecosystem.
