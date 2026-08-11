#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "$script_dir/../.." && pwd -P)"
errors=0

report() {
    echo "error: $*" >&2
    errors=$((errors + 1))
}

required_sources=(
    .github/workflows/docs.yml
    README.md
    CONTRIBUTING.md
    pull_request_template.md
    docs/README.md
    docs/decisions/0001-adopt-hybrid-ecs-deployment-model.md
    docs/decisions/0002-adopt-state-aware-ecs-health-profiles.md
    docs/decisions/0003-adopt-current-state-ecs-bootstrap-classification.md
    docs/decisions/0004-adopt-arc42-engineering-documentation-system.md
    docs/decisions/0005-adopt-ecs-service-delivery-workflow-envelope.md
    docs/decisions/0006-adopt-developer-tooling-golden-path.md
    docs/decisions/0007-adopt-release-and-versioning-standard.md
    docs/decisions/0008-separate-artifact-components-from-native-dependency-roots.md
    docs/decisions/README.md
    docs/decisions/0022-retire-golden-path-executable-tooling.md
    docs/golden-path/README.md
    docs/golden-path/stack-defaults.md
    docs/golden-path/reference-examples.md
    docs/golden-path/release-readiness.md
    docs/golden-path/examples/toolchain-node.toml
    docs/golden-path/examples/node.just
    docs/golden-path/examples/go.just
    docs/golden-path/examples/python.just
    docs/golden-path/examples/canonical-ci.yml
    docs/golden-path/examples/dependabot.yml
    docs/golden-path/examples/native-roots.yml
    docs/platform/README.md
    docs/platform/ecs-deployment-contract.md
    docs/platform/ecs-health-readiness-profiles.md
    docs/platform/ecs-service-delivery-workflow-standard.md
    docs/platform/ecs-service-health-matrix.md
    docs/standards/README.md
    docs/standards/developer-tooling/README.md
    docs/standards/developer-tooling/command-contract.md
    docs/standards/developer-tooling/task-runner.md
    docs/standards/developer-tooling/toolchain-management.md
    docs/standards/developer-tooling/dependency-management.md
    docs/standards/developer-tooling/distribution.md
    docs/standards/developer-tooling/build-hygiene.md
    docs/standards/developer-tooling/runtime-support.md
    docs/standards/developer-tooling/conformance.md
    docs/standards/developer-tooling/exceptions.md
    docs/standards/developer-tooling/profiles/README.md
    docs/standards/developer-tooling/rules/runtime-support.v1.json
    docs/standards/developer-tooling/schemas/README.md
    docs/standards/developer-tooling/schemas/golden-path-native-roots-v1.schema.json
    docs/standards/developer-tooling/schemas/runtime-support-v1.schema.json
    docs/standards/engineering-documentation/README.md
    docs/standards/engineering-documentation/contract.md
    docs/standards/engineering-documentation/arc42-profile.md
    docs/standards/engineering-documentation/lifecycle-and-validation.md
    docs/standards/release-versioning/README.md
    docs/standards/release-versioning/profiles.md
    docs/standards/release-versioning/lifecycle.md
    docs/standards/release-versioning/release-evidence.md
    docs/standards/release-versioning/automation.md
    docs/standards/release-versioning/exceptions.md
    docs/guides/README.md
    docs/guides/adopting-developer-tooling.md
    docs/guides/bootstrap-new-repository.md
    docs/guides/migrating-developer-tooling.md
    docs/guides/github-hosting-capabilities.md
    docs/guides/adopting-arc42.md
    docs/guides/migrating-existing-documentation.md
    templates/engineering-documentation/README.md
    templates/engineering-documentation/repository/docs/README.md
    templates/engineering-documentation/repository/docs/architecture/README.md
    templates/engineering-documentation/repository/docs/decisions/README.md
    templates/engineering-documentation/repository/docs/decisions/0001-adopt-organization-arc42-profile.md
    templates/engineering-documentation/subsystem/README.md
    scripts/docs/README.md
    scripts/docs/scaffold-arc42.sh
    scripts/docs/check-contract.sh
    scripts/docs/check-repository.sh
)

for required_source in "${required_sources[@]}"; do
    if [[ ! -s "$repo_root/$required_source" ]]; then
        report "required organization documentation source missing or empty: $required_source"
    fi
done

decisions_index="$repo_root/docs/decisions/README.md"

if compgen -G "$repo_root/docs/decisions/[0-9][0-9][0-9][0-9]-*.md" >/dev/null; then
    for adr_file in "$repo_root"/docs/decisions/[0-9][0-9][0-9][0-9]-*.md; do
        filename="$(basename "$adr_file")"
        if ! grep -Eq '^- Status: (Accepted|Superseded|Deprecated|Rejected|Proposed)$' "$adr_file"; then
            report "organization ADR has no recognized lifecycle status: docs/decisions/$filename"
        fi
        if ! grep -Fq "$filename" "$decisions_index"; then
            report "organization ADR is missing from docs/decisions/README.md: $filename"
        fi
    done
fi

check_markdown_file() {
    local file="$1"
    local display="${file#"$repo_root"/}"
    local destination path resolved

    if grep -nE '[[:blank:]]+$' "$file" >/dev/null; then
        report "trailing whitespace: $display"
    fi

    while IFS= read -r destination; do
        case "$destination" in
            http://* | https://* | mailto:* | \#*)
                continue
                ;;
        esac

        path="${destination%%#*}"
        path="${path%%\?*}"
        path="${path#<}"
        path="${path%>}"
        [[ -z "$path" ]] && continue

        if [[ "$path" == /* ]]; then
            resolved="$repo_root$path"
        else
            resolved="$(dirname "$file")/$path"
        fi

        if [[ ! -e "$resolved" ]]; then
            report "broken local Markdown link in $display: $destination"
        fi
    done < <(perl -ne 'while (/\]\(([^)]+)\)/g) { print "$1\n" }' "$file")
}

while IFS= read -r -d '' markdown_file; do
    check_markdown_file "$markdown_file"
done < <(
    find \
        "$repo_root" \
        -path "$repo_root/.git" -prune -o \
        -type f -name '*.md' -print0
)

while IFS= read -r -d '' json_file; do
    if ! python3 -m json.tool "$json_file" >/dev/null; then
        report "invalid JSON: ${json_file#"$repo_root"/}"
    fi
done < <(
    find \
        "$repo_root" \
        -path "$repo_root/.git" -prune -o \
        -type f -name '*.json' -print0
)

if command -v ruby >/dev/null 2>&1; then
    while IFS= read -r -d '' yaml_file; do
        if ! ruby -e 'require "yaml"; YAML.parse_file(ARGV.fetch(0))' "$yaml_file" >/dev/null; then
            report "invalid YAML: ${yaml_file#"$repo_root"/}"
        fi
    done < <(
        find \
            "$repo_root" \
            -path "$repo_root/.git" -prune -o \
            -type f \( -name '*.yml' -o -name '*.yaml' \) -print0
    )
else
    report "Ruby with its standard YAML parser is required"
fi

while IFS= read -r -d '' toml_file; do
    if ! python3 -c \
        'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' \
        "$toml_file"; then
        report "invalid TOML: ${toml_file#"$repo_root"/}"
    fi
done < <(
    find \
        "$repo_root" \
        -path "$repo_root/.git" -prune -o \
        -type f -name '*.toml' -print0
)

if command -v just >/dev/null 2>&1; then
    for reference_justfile in "$repo_root"/docs/golden-path/examples/*.just; do
        if ! just --justfile "$reference_justfile" --summary >/dev/null; then
            report "invalid Just syntax: ${reference_justfile#"$repo_root"/}"
        fi
    done
else
    report "Just is required to validate Golden Path reference examples"
fi

for shell_script in \
    "$script_dir/check-contract.sh" \
    "$script_dir/scaffold-arc42.sh" \
    "$script_dir/check-repository.sh"; do
    if ! bash -n "$shell_script"; then
        report "invalid Bash syntax: ${shell_script#"$repo_root"/}"
    fi
done

temp_parent="${TMPDIR:-/tmp}"
test_root="$(mktemp -d "$temp_parent/5010-arc42-check.XXXXXX")"

cleanup() {
    case "$test_root" in
        "$temp_parent"/5010-arc42-check.*)
            rm -rf -- "$test_root"
            ;;
        *)
            echo "warning: refusing to remove unexpected temporary path: $test_root" >&2
            ;;
    esac
}
trap cleanup EXIT

"$script_dir/scaffold-arc42.sh" \
    --target "$test_root" \
    --system-name "Contract Test System" \
    --scope "Temporary repository-wide engineering system" \
    >/dev/null

"$script_dir/check-contract.sh" --target "$test_root" >/dev/null

if "$script_dir/scaffold-arc42.sh" \
    --target "$test_root" \
    --system-name "Contract Test System" \
    --scope "Temporary repository-wide engineering system" \
    >/dev/null 2>&1; then
    report "scaffold overwrote an existing generated documentation tree"
fi

if [[ "$errors" -ne 0 ]]; then
    printf 'organization documentation check: FAILED (%d problem(s))\n' "$errors" >&2
    exit 1
fi

printf 'organization documentation check: OK\n'
