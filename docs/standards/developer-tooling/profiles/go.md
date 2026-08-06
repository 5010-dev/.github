# Go profile

- Status: Accepted
- Profile ID: `go`
- Standard version: `2026.08.1`

The Go profile prioritizes the official Go toolchain and module system over an
additional build framework.

## Toolchain authority

- Preferred is the latest patch of Go 1.26; Go 1.25 is supported.
- `go.mod#go` declares minimum language/module semantics.
- `go.mod#toolchain` declares the preferred development toolchain.
- mise installs the exact aligned base Go and MUST NOT force a lower or
  contradictory toolchain.
- Applications/services/internal CLIs validate the exact production toolchain.
- Published libraries validate their minimum supported Go and preferred Go.
- The preferred lane MUST use `GOTOOLCHAIN=local` or equivalent fail-closed
  behavior; a library minimum-version lane explicitly selects that older exact
  toolchain.

## Dependencies and tools

- `go.mod` and applicable `go.sum` are committed.
- CI uses `go mod tidy -diff`, `go mod verify`, and read-only module semantics.
- Project generators and Go commands use the Go 1.24+ `tool` directive and
  `go tool`.
- New profiles MUST NOT use legacy `tools.go` blank imports or global
  `go install ...@latest`.
- golangci-lint is an external support CLI because upstream does not recommend
  normal source installation. It uses an exact official binary verified through
  the toolchain/release contract.

## Format and lint

- `.golangci.yaml` MUST declare schema `version: "2"`.
- gofmt semantics and goimports are the default formatters.
- `format` writes and `format-check` emits a diff without writing.
- `lint` runs standalone `go vet ./...` and exact golangci-lint v2.
- golangci-lint starts from `default: none` with explicit `staticcheck`,
  `errcheck`, `ineffassign`, `unused`, `nolintlint`, and `errorlint`.
- `govet` is not duplicated inside golangci-lint.
- `default: all`, unreviewed new-linter adoption, global exclusions, and
  reasonless `nolint` are prohibited.

`gofumpt`, gci, and line-length formatting are conditional project conventions,
not organization defaults.

`go fix`, `go generate`, and formatter writes are explicit source-writing
commands and MUST NOT run inside `check`.

## Tests, race, fuzz, and coverage

- Base test is `go test -mod=readonly ./...`.
- Applications/services and concurrent libraries provide a supported Linux
  race lane unless inapplicable or covered by an exception.
- Fuzz seed corpora run through regular tests.
- Active fuzzing is a bounded scheduled capability for untrusted parser,
  protocol, serialization, file-format, or security boundaries.
- Discovered fuzz cases become deterministic regression tests.
- Coverage uses native profiles when selected; no universal percentage is
  required.
- Benchmarks and PGO are conditional product-performance capabilities.
- Build tags, cgo, GOOS/GOARCH, and optional integration paths are declared and
  tested when they create supported code paths.

## Commands

| Command | Meaning |
| --- | --- |
| `init` | Exact mise Go/support CLI and module download |
| `format` / `format-check` | gofmt/goimports write/diff |
| `lint` | `go vet` plus exact explicit golangci-lint set |
| `typecheck` | Package/test compilation using production-equivalent flags |
| `test` | Native test suite with read-only module graph |
| `test-race` | Applicable race lane |
| `generate` / `generate-check` | Explicit pinned generation and isolated drift check |
| `build` | Declared main/library build verification |
| `package-check` | Applicable binary or public-module consumer checks |
| `check` | module drift + format-check + lint + test |
| `ci` | check + applicable race/generate/build/artifact matrix |

## Module and workspace boundary

- One release/dependency boundary uses one module by default.
- Executables use explicit `cmd/<name>` packages; non-public application code
  belongs under `internal/`.
- Multiple modules require independent consumers, versions, graphs, or release
  lifecycles.
- A committed `go.work` represents an intentional repository multi-module
  build boundary; personal cross-repository workspaces are ignored.
- Workspace CI checks `go work sync` drift and each module's tidy, verify, test,
  and build behavior.
- Public modules pass `GOWORK=off` consumer resolution and MUST NOT ship local
  filesystem `replace` directives.
- Private module access uses narrow `GOPRIVATE`/`GONOSUMDB`; it MUST NOT disable
  checksum verification globally.

## Artifact contracts

### Applications, services, and internal CLIs

- `build` produces each declared main package at an explicit path.
- Pure-Go artifacts SHOULD use cgo-off and `-trimpath`.
- cgo requires an exact native compiler, library, and base-image profile.
- Clean release builds preserve verifiable VCS/module metadata and are inspected
  with `go version -m` or equivalent.
- Build timestamps, absolute paths, and moving dependencies MUST NOT undermine
  reproducibility claims.
- `-s -w` MUST NOT be applied universally for size; stripping is an explicit
  artifact choice that preserves the required debugging and symbolization
  contract.
- Services smoke-test the target container's startup/liveness contract.
- GoReleaser is conditional on cross-platform CLI distribution needs.
- PGO requires representative profile provenance and a refresh owner.

### Published modules

- Minimum and preferred Go lanes run tests and consumer import/compile smoke.
- v1+ breaking releases use the `/vN` module path.
- Release candidates pass tidy, test, and `GOWORK=off` resolution.
- Published tag content is immutable.
- API-diff tooling MAY supplement, but not replace, consumer and human review.

Rule IDs: `DT-GO-*`, plus common `DT-CMD-*`, `DT-TOOL-*`, and `DT-DEP-*`.
