#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "$script_dir/../.." && pwd -P)"
locator="$repo_root/docs/guides/golden-path-bootstrap.v1.json"
binary="${GOLDEN_PATH_BIN:-}"

if [[ -z "$binary" || ! -x "$binary" ]]; then
    echo "error: GOLDEN_PATH_BIN must name an executable verified Golden Path release" >&2
    exit 2
fi

locator_values=()
while IFS= read -r value; do
    locator_values+=("$value")
done < <(
    python3 - "$locator" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as source:
    locator = json.load(source)

implementation = locator["implementation"]
release = implementation["release"]
values = [
    release["version"],
    release["tag"],
    release["sourceCommit"],
    release["manifest"]["url"],
    release["manifest"]["sha256"],
    release["snapshotManifest"]["url"],
    release["snapshotManifest"]["sha256"],
    implementation["repositorySlug"],
    implementation["verifier"]["githubCliVersion"],
    implementation["verifier"]["signerWorkflow"],
]
for value in values:
    if not isinstance(value, str) or not value or "\n" in value:
        raise SystemExit("invalid bootstrap locator string")
    print(value)
PY
)

if [[ "${#locator_values[@]}" -ne 10 ]]; then
    echo "error: bootstrap locator did not produce the expected release identity" >&2
    exit 2
fi

release_version="${locator_values[0]}"
release_tag="${locator_values[1]}"
source_commit="${locator_values[2]}"
manifest_url="${locator_values[3]}"
manifest_sha256="${locator_values[4]}"
snapshot_manifest_url="${locator_values[5]}"
snapshot_manifest_sha256="${locator_values[6]}"
repository_slug="${locator_values[7]}"
github_cli_version="${locator_values[8]}"
signer_workflow="${locator_values[9]}"

temp_parent="${RUNNER_TEMP:-${TMPDIR:-/tmp}}"
test_root="$(mktemp -d "$temp_parent/5010-golden-path-bootstrap.XXXXXX")"

cleanup() {
    case "$test_root" in
        "$temp_parent"/5010-golden-path-bootstrap.*)
            rm -rf -- "$test_root"
            ;;
        *)
            echo "warning: refusing to remove unexpected temporary path: $test_root" >&2
            ;;
    esac
}
trap cleanup EXIT HUP INT TERM

release_manifest="$test_root/release-manifest.json"
snapshot_manifest="$test_root/standard-snapshot-manifest.json"
curl --fail --location --proto '=https' --tlsv1.2 --retry 3 --max-time 120 \
    --output "$release_manifest" \
    "$manifest_url"
curl --fail --location --proto '=https' --tlsv1.2 --retry 3 --max-time 120 \
    --output "$snapshot_manifest" \
    "$snapshot_manifest_url"

sha256_file() {
    local path="$1"
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$path" | awk '{print $1}'
    elif command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$path" | awk '{print $1}'
    else
        echo "error: no SHA-256 utility is available" >&2
        return 2
    fi
}

actual_manifest_sha256="$(sha256_file "$release_manifest")"
actual_snapshot_manifest_sha256="$(sha256_file "$snapshot_manifest")"
test "$actual_manifest_sha256" = "$manifest_sha256"
test "$actual_snapshot_manifest_sha256" = "$snapshot_manifest_sha256"
test "$(gh version | awk 'NR == 1 { print $3 }')" = "$github_cli_version"
test "$("$binary" --version)" = "golden-path $release_version"

gh attestation verify "$release_manifest" \
    --repo "$repository_slug" \
    --signer-workflow "$signer_workflow" \
    --source-digest "$source_commit" \
    --signer-digest "$source_commit" \
    --source-ref "refs/tags/$release_tag" \
    --deny-self-hosted-runners >/dev/null
gh attestation verify "$snapshot_manifest" \
    --repo "$repository_slug" \
    --signer-workflow "$signer_workflow" \
    --source-digest "$source_commit" \
    --signer-digest "$source_commit" \
    --source-ref "refs/tags/$release_tag" \
    --deny-self-hosted-runners >/dev/null
python3 "$repo_root/scripts/docs/check-golden-path-integration.py" \
    --snapshot-manifest "$snapshot_manifest"

fixture="$repo_root/scripts/docs/fixtures/golden-path-bootstrap/documentation.yaml"
preview_plan="$test_root/preview-plan.json"
write_plan="$test_root/write-plan.json"
candidate="$test_root/candidate"

"$binary" generate \
    --request "$fixture" \
    --release-manifest "$release_manifest" \
    >"$preview_plan"

"$binary" generate \
    --request "$fixture" \
    --release-manifest "$release_manifest" \
    --write \
    --output "$candidate" \
    >"$write_plan"

test "$(GOLDEN_PATH_BIN="$binary" "$candidate/scripts/golden-path" --version)" = "golden-path $release_version"

checker_result="$test_root/checker-result.json"
checker_text="$test_root/checker-text.txt"
"$binary" check \
    --root "$candidate" \
    --evaluated-at 2026-08-01T00:00:00Z \
    --expected-profiles '["documentation"]' \
    --json-output "$checker_result" \
    >"$checker_text"

python3 - \
    "$locator" \
    "$release_manifest" \
    "$preview_plan" \
    "$write_plan" \
    "$candidate" \
    "$checker_result" <<'PY'
import json
import pathlib
import sys

(
    locator_path,
    release_path,
    preview_path,
    write_path,
    candidate_path,
    result_path,
) = map(pathlib.Path, sys.argv[1:])

def read_json(path):
    with path.open(encoding="utf-8") as source:
        return json.load(source)

def require(condition, message):
    if not condition:
        raise SystemExit(f"released bootstrap validation failed: {message}")

locator = read_json(locator_path)
release = read_json(release_path)
preview = read_json(preview_path)
written = read_json(write_path)
candidate = candidate_path.resolve()
result = read_json(result_path)

implementation = locator["implementation"]
expected_release = implementation["release"]
expected_source = {
    "repository": implementation["repository"],
    "commit": expected_release["sourceCommit"],
    "tag": expected_release["tag"],
}

require(release["schemaVersion"] == "golden-path-release-manifest/v1", "release manifest schema")
require(release["releaseVersion"] == expected_release["version"], "release version")
require(release["standardVersion"] == locator["standard"]["version"], "standard version")
require(release["contractVersion"] == locator["standard"]["contractVersion"], "contract version")
require(release["source"] == expected_source, "release source identity")
require(release["catalogDigest"] == locator["standard"]["catalogDigest"], "release catalog digest")
require(
    release["standardSnapshotManifest"] == expected_release["snapshotManifest"]["name"],
    "release standard snapshot manifest name",
)
require(
    release["snapshotAggregateDigest"] == expected_release["snapshotAggregateDigest"],
    "release snapshot aggregate digest",
)

actual_archives = {
    (asset["os"], asset["architecture"]): (asset["name"], asset["sha256"])
    for asset in release["assets"]
}
expected_archives = {
    (asset["os"], asset["architecture"]): (asset["name"], asset["sha256"])
    for asset in expected_release["archives"]
}
require(actual_archives == expected_archives, "release archive set")
require(release["components"]["checker"]["version"] == expected_release["version"], "checker component")
require(release["components"]["templateBundle"]["version"] == expected_release["version"], "template component")
require(release["components"]["automation"]["version"] == expected_release["version"], "automation component")

require(preview == written == read_json(candidate / "golden-path-plan.json"), "deterministic plans")
require(preview["schemaVersion"] == "golden-path-materialization-plan/v1", "plan schema")
require(preview["operation"] == "generate", "plan operation")
require(preview["standardVersion"] == locator["standard"]["version"], "plan standard version")
require(preview["releaseVersion"] == expected_release["version"], "plan release version")
require(preview["assetBundleVersion"] == expected_release["version"], "plan asset bundle version")
require(preview["conflictCount"] == 0, "plan conflicts")
require(preview["changes"] and all(change["status"] == "create" for change in preview["changes"]), "plan changes")

assets = read_json(candidate / ".github/golden-path-assets.json")
require(assets["schemaVersion"] == "golden-path-generated-assets/v1", "generated assets schema")
require(assets["standardVersion"] == locator["standard"]["version"], "generated standard version")
require(assets["releaseVersion"] == expected_release["version"], "generated release version")
require(assets["assetBundleVersion"] == expected_release["version"], "generated asset bundle version")
require(assets["source"] == expected_source, "generated source identity")
managed_paths = {asset["path"] for asset in assets["files"]}
required_paths = {
    ".github/golden-path.yaml",
    ".github/golden-path-request.json",
    ".github/golden-path-exceptions.yaml",
    ".github/workflows/developer-tooling.yml",
    "justfile",
    "mise.toml",
    "mise.lock",
    "scripts/golden-path",
}
require(required_paths <= managed_paths, "required managed paths")

workflow = (candidate / ".github/workflows/developer-tooling.yml").read_text()
require(f"uses: {implementation['automation']['reusableWorkflow']}" in workflow, "generated workflow pin")
require(f"checker-version: '{expected_release['version']}'" in workflow, "generated checker version")
require(f"source-commit: '{expected_release['sourceCommit']}'" in workflow, "generated source commit")
require("profiles: '[\"documentation\"]'" in workflow, "generated profiles")
for archive in expected_release["archives"]:
    require(archive["sha256"] in workflow, f"generated archive checksum {archive['name']}")
for forbidden in ("@main", "@dev", "@latest", "secrets: inherit", "environment:"):
    require(forbidden not in workflow, f"generated workflow forbidden text {forbidden}")

require(result["schemaVersion"] == "golden-path-checker-output/v1", "checker output schema")
require(result["contractVersion"] == locator["standard"]["contractVersion"], "checker contract version")
require(result["standardVersion"] == locator["standard"]["version"], "checker standard version")
require(result["checkerVersion"] == expected_release["version"], "checker version")
require(result["catalogDigest"] == locator["standard"]["catalogDigest"], "checker catalog digest")
require(result["profiles"] == ["documentation"], "checker profiles")
require(result["enforcement"] == "report-only", "checker enforcement")
require(result["exitCode"] == 0, "checker exit code")
require(result["complete"] is True, "checker completeness")
require(result["summary"]["fail"] == 0, "checker failures")
require(result["summary"]["error"] == 0, "checker errors")
PY

printf 'Golden Path released bootstrap check: OK (%s)\n' "$release_tag"
