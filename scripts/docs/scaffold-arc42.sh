#!/usr/bin/env bash

set -euo pipefail

profile_id="5010-arc42-v1"
scaffold_date="$(date -u +%F)"
target_dir="$(pwd)"
system_name=""
scope=""
dry_run=0

usage() {
    cat <<'EOF'
Usage:
  scaffold-arc42.sh --target PATH --system-name NAME --scope SCOPE [--dry-run]

Options:
  --target PATH       Existing repository or engineering-layer root.
  --system-name NAME  Reader-facing engineering-system name.
  --scope SCOPE       Exact scope owned by the arc42 corpus.
  --dry-run           Print destination paths without writing.
  -h, --help          Show this help.
EOF
}

require_value() {
    local option="$1"
    local value="${2:-}"
    if [[ -z "$value" ]]; then
        echo "error: $option requires a value" >&2
        usage >&2
        exit 2
    fi
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --target)
            require_value "$1" "${2:-}"
            target_dir="$2"
            shift 2
            ;;
        --system-name)
            require_value "$1" "${2:-}"
            system_name="$2"
            shift 2
            ;;
        --scope)
            require_value "$1" "${2:-}"
            scope="$2"
            shift 2
            ;;
        --dry-run)
            dry_run=1
            shift
            ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            echo "error: unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ -z "$system_name" || -z "$scope" ]]; then
    echo "error: --system-name and --scope are required" >&2
    usage >&2
    exit 2
fi

if [[ ! -d "$target_dir" ]]; then
    echo "error: target directory does not exist: $target_dir" >&2
    exit 2
fi

if ! command -v perl >/dev/null 2>&1; then
    echo "error: perl is required to render scaffold tokens" >&2
    exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
source_repo="$(cd "$script_dir/../.." && pwd -P)"
template_root="$source_repo/templates/engineering-documentation/repository"
target_root="$(cd "$target_dir" && pwd -P)"

if [[ ! -d "$template_root" ]]; then
    echo "error: repository template is missing: $template_root" >&2
    exit 2
fi

if [[ "$target_root" == "/" ]]; then
    echo "error: refusing to scaffold into the filesystem root" >&2
    exit 2
fi

collision=0
while IFS= read -r -d '' source_file; do
    relative_path="${source_file#"$template_root"/}"
    destination="$target_root/$relative_path"
    if [[ -e "$destination" ]]; then
        echo "error: destination already exists: $destination" >&2
        collision=1
    fi
done < <(find "$template_root" -type f -print0)

if [[ "$collision" -ne 0 ]]; then
    echo "error: scaffold preflight failed; no files were written" >&2
    exit 1
fi

if [[ "$dry_run" -eq 1 ]]; then
    while IFS= read -r -d '' source_file; do
        relative_path="${source_file#"$template_root"/}"
        printf '%s\n' "$target_root/$relative_path"
    done < <(find "$template_root" -type f -print0)
    exit 0
fi

created=0
while IFS= read -r -d '' source_file; do
    relative_path="${source_file#"$template_root"/}"
    destination="$target_root/$relative_path"
    mkdir -p "$(dirname "$destination")"
    SYSTEM_NAME="$system_name" \
        SCOPE="$scope" \
        PROFILE_ID="$profile_id" \
        SCAFFOLD_DATE="$scaffold_date" \
        perl -pe '
            s/\{\{SYSTEM_NAME\}\}/$ENV{SYSTEM_NAME}/g;
            s/\{\{SCOPE\}\}/$ENV{SCOPE}/g;
            s/\{\{PROFILE_ID\}\}/$ENV{PROFILE_ID}/g;
            s/\{\{DATE\}\}/$ENV{SCAFFOLD_DATE}/g;
        ' "$source_file" >"$destination"
    created=$((created + 1))
done < <(find "$template_root" -type f -print0)

printf 'arc42 scaffold: created %d files under %s\n' "$created" "$target_root"
printf 'next: replace Open skeletons with evidence-backed content and record profile adoption in an ADR\n'
