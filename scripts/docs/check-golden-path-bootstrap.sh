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
    "true" if "adoption" in release["explicitMaterializationModes"] else "false",
    locator["discovery"]["adoptionFixture"],
]
for value in values:
    if not isinstance(value, str) or not value or "\n" in value:
        raise SystemExit("invalid bootstrap locator string")
    print(value)
PY
)

if [[ "${#locator_values[@]}" -ne 12 ]]; then
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
supports_adoption="${locator_values[10]}"
adoption_fixture_path="${locator_values[11]}"
adoption_fixture="$repo_root/$adoption_fixture_path"

if [[ "$supports_adoption" != "true" && "$supports_adoption" != "false" ]]; then
    echo "error: bootstrap locator returned an invalid adoption-support flag" >&2
    exit 2
fi
if [[ ! -f "$adoption_fixture" ]]; then
    echo "error: bootstrap locator adoption fixture is missing" >&2
    exit 2
fi

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
    --snapshot-manifest "$snapshot_manifest" \
    --release-manifest "$release_manifest"

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

placeholder_status=0
"$binary" check \
    --root "$candidate" \
    --evaluated-at 2026-08-01T00:00:00Z \
    --expected-profiles REPLACE_WITH_EXACT_PROFILES \
    >/dev/null 2>&1 || placeholder_status=$?
if [[ "$placeholder_status" -ne 2 ]]; then
    echo "error: workflow-template profile sentinel did not fail with a usage error" >&2
    exit 1
fi

if [[ "$supports_adoption" == "true" ]]; then
    adoption_preview_plan="$test_root/adoption-preview-plan.json"
    adoption_write_plan="$test_root/adoption-write-plan.json"
    adoption_candidate="$test_root/adoption-candidate"

    "$binary" generate \
        --request "$adoption_fixture" \
        --release-manifest "$release_manifest" \
        >"$adoption_preview_plan"

    "$binary" generate \
        --request "$adoption_fixture" \
        --release-manifest "$release_manifest" \
        --write \
        --output "$adoption_candidate" \
        >"$adoption_write_plan"

    test "$(GOLDEN_PATH_BIN="$binary" "$adoption_candidate/scripts/golden-path" --version)" = "golden-path $release_version"

    python3 - \
        "$adoption_fixture" \
        "$adoption_preview_plan" \
        "$adoption_write_plan" \
        "$adoption_candidate" \
        "$release_version" <<'PY'
import json
import pathlib
import stat
import sys

(
    fixture_path,
    preview_path,
    write_path,
    candidate_path,
) = map(pathlib.Path, sys.argv[1:5])
release_version = sys.argv[5]

def read_json(path):
    with path.open(encoding="utf-8") as source:
        return json.load(source)

def require(condition, message):
    if not condition:
        raise SystemExit(f"released adoption validation failed: {message}")

fixture = read_json(fixture_path)
preview = read_json(preview_path)
written = read_json(write_path)
candidate = candidate_path.resolve()
request = read_json(candidate / ".github/golden-path-request.json")
metadata = read_json(candidate / ".github/golden-path.yaml")
assets = read_json(candidate / ".github/golden-path-assets.json")

expected_managed_paths = {
    ".github/golden-path-assets.json",
    ".github/golden-path-request.json",
    ".github/golden-path.yaml",
    ".github/workflows/developer-tooling.yml",
    "scripts/golden-path",
}
expected_inventory_paths = expected_managed_paths - {
    ".github/golden-path-assets.json"
}
actual_files = {
    str(path.relative_to(candidate))
    for path in candidate.rglob("*")
    if path.is_file()
}

require(preview == written, "deterministic stdout plans")
require(preview["schemaVersion"] == "golden-path-materialization-plan/v1", "plan schema")
require(preview["operation"] == "generate", "plan operation")
require(preview["releaseVersion"] == release_version, "plan release version")
require(preview["conflictCount"] == 0, "plan conflicts")
require({change["path"] for change in preview["changes"]} == expected_managed_paths, "plan paths")
require(all(change["status"] == "create" for change in preview["changes"]), "plan changes")
require(actual_files == expected_managed_paths, "candidate files")
require(not (candidate / "golden-path-plan.json").exists(), "plan excluded from candidate")
require(assets["schemaVersion"] == "golden-path-generated-assets/v1", "asset inventory schema")
require(assets["releaseVersion"] == release_version, "asset inventory release version")
require({asset["path"] for asset in assets["files"]} == expected_inventory_paths, "asset inventory")
require("golden-path-plan.json" not in {asset["path"] for asset in assets["files"]}, "plan exclusion")
require(stat.S_IMODE((candidate / "scripts/golden-path").stat().st_mode) == 0o755, "script mode")

require(fixture["materializationMode"] == "adoption", "fixture materialization mode")
require(request["materializationMode"] == "adoption", "canonical materialization mode")
require(request["targets"] == fixture["targets"], "canonical targets")
require(len(request["components"]) == len(fixture["components"]), "canonical components")
for actual, expected in zip(request["components"], fixture["components"]):
    for field in ("profiles", "artifactTypes", "capabilities"):
        require(sorted(actual[field]) == sorted(expected[field]), f"canonical component {field}")

expected_profiles = sorted({value for item in fixture["components"] for value in item["profiles"]})
expected_artifacts = sorted({value for item in fixture["components"] for value in item["artifactTypes"]})
expected_capabilities = sorted({value for item in fixture["components"] for value in item["capabilities"]})
require(metadata["profiles"] == expected_profiles, "metadata profiles")
require(metadata["artifactTypes"] == expected_artifacts, "metadata artifact types")
require(metadata["capabilities"] == expected_capabilities, "metadata capabilities")
require(metadata["targets"] == fixture["targets"], "metadata targets")
require(
    metadata["extensions"]["dev.fiftyten.generator"]["materializationMode"] == "adoption",
    "metadata materialization mode",
)
PY
fi

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
expected_standard_version = expected_release["standardVersion"]
expected_contract_version = expected_release["contractVersion"]
expected_catalog_digest = expected_release["catalogDigest"]
expected_source = {
    "repository": implementation["repository"],
    "commit": expected_release["sourceCommit"],
    "tag": expected_release["tag"],
}

require(release["schemaVersion"] == "golden-path-release-manifest/v2", "release manifest schema")
require(release["releaseVersion"] == expected_release["version"], "release version")
require(release["lifecycle"] == "stable", "release lifecycle")
require(release["enforcement"] == ["report-only"], "release enforcement")
require(release["standardVersion"] == expected_standard_version, "standard version")
require(release["contractVersion"] == expected_contract_version, "contract version")
require(release["source"] == expected_source, "release source identity")
require(release["catalogDigest"] == expected_catalog_digest, "release catalog digest")
standard_snapshot = release["standardSnapshot"]
require(standard_snapshot["file"] == {
    "name": expected_release["snapshotManifest"]["name"],
    "sha256": expected_release["snapshotManifest"]["sha256"],
}, "release standard snapshot manifest identity")
require(
    standard_snapshot["source"]["repository"] == locator["standard"]["repository"],
    "snapshot source repository",
)
require(
    standard_snapshot["source"]["path"] == locator["standard"]["snapshotPath"],
    "snapshot source path",
)
require(
    standard_snapshot["aggregateDigest"] == expected_release["snapshotAggregateDigest"],
    "snapshot aggregate digest",
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
require(release["components"]["checker"]["lifecycle"] == "stable", "checker lifecycle")
require(release["components"]["checker"]["enforcement"] == ["report-only"], "checker enforcement")
require(release["components"]["generator"]["version"] == expected_release["version"], "generator component")
require(release["components"]["generator"]["lifecycle"] == "stable", "generator lifecycle")
require(release["components"]["generator"]["enforcement"] == ["report-only"], "generator enforcement")
require(release["components"]["assetBundle"]["version"] == expected_release["version"], "asset bundle component")
require(release["components"]["automation"]["version"] == expected_release["version"], "automation component")

require(preview == written, "deterministic stdout plans")
require(preview["schemaVersion"] == "golden-path-materialization-plan/v1", "plan schema")
require(preview["operation"] == "generate", "plan operation")
require(preview["standardVersion"] == expected_standard_version, "plan standard version")
require(preview["releaseVersion"] == expected_release["version"], "plan release version")
require(preview["assetBundleVersion"] == expected_release["version"], "plan asset bundle version")
require(preview["conflictCount"] == 0, "plan conflicts")
require(preview["changes"] and all(change["status"] == "create" for change in preview["changes"]), "plan changes")
actual_files = {
    str(path.relative_to(candidate))
    for path in candidate.rglob("*")
    if path.is_file()
}
require({change["path"] for change in preview["changes"]} == actual_files, "plan paths")
require(not (candidate / "golden-path-plan.json").exists(), "plan excluded from candidate")

assets = read_json(candidate / ".github/golden-path-assets.json")
require(assets["schemaVersion"] == "golden-path-generated-assets/v1", "generated assets schema")
require(assets["standardVersion"] == expected_standard_version, "generated standard version")
require(assets["releaseVersion"] == expected_release["version"], "generated release version")
require(assets["assetBundleVersion"] == expected_release["version"], "generated asset bundle version")
require(assets["source"] == expected_source, "generated source identity")
managed_paths = {asset["path"] for asset in assets["files"]}
expected_managed_paths = {
    ".github/golden-path-assets.json",
    ".github/golden-path.yaml",
    ".github/golden-path-request.json",
    ".github/workflows/developer-tooling.yml",
    "scripts/golden-path",
}
expected_inventory_paths = expected_managed_paths - {".github/golden-path-assets.json"}
expected_repository_owned_paths = {
    ".github/dependabot.yml",
    ".github/golden-path-exceptions.yaml",
    ".github/workflows/quality.yml",
    "README.md",
    "justfile",
    "mise.toml",
    "mise.lock",
}
require(managed_paths == expected_inventory_paths, "bounded managed inventory")
require(expected_managed_paths <= actual_files, "required managed files")
require(expected_repository_owned_paths <= actual_files, "repository-owned bootstrap scaffold")

workflow = (candidate / ".github/workflows/developer-tooling.yml").read_text()
require(f"uses: {implementation['automation']['reusableWorkflow']}" in workflow, "generated workflow pin")
require("runner: ubuntu-24.04" in workflow, "generated runner")
require("working-directory: ." in workflow, "generated working directory")
require("profiles: '[\"documentation\"]'" in workflow, "generated profiles")
for retired_input in (
    "checker-version",
    "source-commit",
    "github-cli-version",
    "darwin-amd64-sha256",
    "darwin-arm64-sha256",
    "linux-amd64-sha256",
    "linux-arm64-sha256",
):
    require(f"{retired_input}:" not in workflow, f"retired generated input {retired_input}")
for forbidden in ("@main", "@dev", "@latest", "secrets: inherit", "environment:"):
    require(forbidden not in workflow, f"generated workflow forbidden text {forbidden}")

quality_workflow = (candidate / ".github/workflows/quality.yml").read_text()
for required_text in (
    "name: Repository / Quality",
    "      - dev",
    "      - main",
    "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
    "uses: jdx/mise-action@7e36c90d9ab29c415a2384db3006f3ec8a8cc654",
    "run: just init",
    "run: just ci",
):
    require(required_text in quality_workflow, f"repository quality workflow {required_text}")
require(quality_workflow.count("run: just ci") == 1, "single repository quality gate")

readme = (candidate / "README.md").read_text()
for required_text in (
    "Work starts\nfrom `dev`",
    "the repository quality workflow—are repository-owned scaffolding",
):
    require(required_text in readme, f"bootstrap README {required_text}")

require(result["schemaVersion"] == "golden-path-checker-output/v1", "checker output schema")
require(result["contractVersion"] == expected_contract_version, "checker contract version")
require(result["standardVersion"] == expected_standard_version, "checker standard version")
require(result["checkerVersion"] == expected_release["version"], "checker version")
require(result["catalogDigest"] == expected_catalog_digest, "checker catalog digest")
require(result["profiles"] == ["documentation"], "checker profiles")
require(result["enforcement"] == "report-only", "checker enforcement")
require(result["exitCode"] == 0, "checker exit code")
require(result["complete"] is True, "checker completeness")
require(result["summary"]["fail"] == 0, "checker failures")
require(result["summary"]["error"] == 0, "checker errors")
PY

printf 'Golden Path released bootstrap check: OK (%s)\n' "$release_tag"
