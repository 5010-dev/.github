set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
export GOTOOLCHAIN := "local"

init:
    mise install --locked
    go mod download

check:
    go mod tidy -diff
    go mod verify
    go vet ./...
    golangci-lint run
    go test -mod=readonly ./...

ci: check
    go build ./...
