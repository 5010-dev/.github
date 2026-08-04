#!/usr/bin/env python3
"""Validate the policy-owned Golden Path bootstrap and discovery surfaces."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LOCATOR_PATH = ROOT / "docs/guides/golden-path-bootstrap.v1.json"
SHA256 = re.compile(r"^[a-f0-9]{64}$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
COMMIT = re.compile(r"^[a-f0-9]{40}$")
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
CALVER = re.compile(r"^(?P<year>[0-9]{4})\.(?P<month>0[1-9]|1[0-2])(?:\.(?P<ordinal>[1-9][0-9]*))?$")
CONTRACT = re.compile(r"^golden-path/v[1-9][0-9]*$")
PROFILE_PLACEHOLDER = "REPLACE_WITH_EXACT_PROFILES"


class ValidationError(Exception):
    """A deterministic local integration-contract violation."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(), object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        try:
            display_path = path.relative_to(ROOT)
        except ValueError:
            display_path = path
        raise ValidationError(f"cannot read valid JSON from {display_path}: {error}") from error


def require_object(value: Any, name: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{name} must be an object")
    actual = set(value)
    if actual != keys:
        raise ValidationError(
            f"{name} keys differ: missing={sorted(keys - actual)}, extra={sorted(actual - keys)}"
        )
    return value


def require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{name} must be a non-empty string")
    return value


def calver_key(value: str, name: str) -> tuple[int, int, int]:
    match = CALVER.fullmatch(require_text(value, name))
    if match is None:
        raise ValidationError(f"{name} must be a stable YYYY.MM[.N] CalVer")
    return (
        int(match.group("year")),
        int(match.group("month")),
        int(match.group("ordinal") or "0"),
    )


def local_file(locator: str, name: str) -> Path:
    relative = Path(require_text(locator, name))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValidationError(f"{name} must be a repository-relative path")
    resolved = (ROOT / relative).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValidationError(f"{name} escapes the policy repository") from error
    if not resolved.is_file() or resolved.stat().st_size == 0:
        raise ValidationError(f"{name} is missing or empty: {relative}")
    return resolved


def validate_locator() -> dict[str, Any]:
    locator = require_object(
        load_json(LOCATOR_PATH),
        "bootstrap locator",
        {"schemaVersion", "baseline", "standard", "implementation", "discovery"},
    )
    if locator["schemaVersion"] != "golden-path-bootstrap/v1":
        raise ValidationError("bootstrap locator has an unsupported schemaVersion")
    if locator["baseline"] != "github-free-private":
        raise ValidationError("bootstrap locator must preserve the GitHub Free private baseline")

    standard = require_object(
        locator["standard"],
        "standard locator",
        {
            "version",
            "contractVersion",
            "repository",
            "snapshotPath",
            "entrypoint",
            "ruleCatalog",
            "catalogDigest",
            "metadataSchema",
            "nativeRootsSchema",
            "exceptionSchema",
        },
    )
    entrypoint = local_file(standard["entrypoint"], "standard.entrypoint")
    if standard["repository"] != "https://github.com/5010-dev/.github":
        raise ValidationError("bootstrap standard repository is not the policy authority")
    snapshot_path = Path(require_text(standard["snapshotPath"], "standard.snapshotPath"))
    if snapshot_path.is_absolute() or ".." in snapshot_path.parts:
        raise ValidationError("standard.snapshotPath must be a repository-relative path")
    if (ROOT / snapshot_path).resolve() != entrypoint.parent.resolve():
        raise ValidationError("bootstrap snapshot path differs from the canonical standard directory")
    rule_catalog = local_file(standard["ruleCatalog"], "standard.ruleCatalog")
    local_file(standard["metadataSchema"], "standard.metadataSchema")
    local_file(standard["nativeRootsSchema"], "standard.nativeRootsSchema")
    local_file(standard["exceptionSchema"], "standard.exceptionSchema")
    standard_source = entrypoint.read_text()
    version_match = re.search(r"^- Standard version: `([^`]+)`$", standard_source, re.MULTILINE)
    contract_match = re.search(r"^- Contract version: `([^`]+)`$", standard_source, re.MULTILINE)
    if not version_match or version_match.group(1) != standard["version"]:
        raise ValidationError("bootstrap standard version differs from the canonical entrypoint")
    current_standard_key = calver_key(standard["version"], "standard.version")
    if not contract_match or contract_match.group(1) != standard["contractVersion"]:
        raise ValidationError("bootstrap contract version differs from the canonical entrypoint")
    actual_catalog_digest = f"sha256:{hashlib.sha256(rule_catalog.read_bytes()).hexdigest()}"
    if require_text(standard["catalogDigest"], "standard.catalogDigest") != actual_catalog_digest:
        raise ValidationError("bootstrap catalog digest differs from the canonical rule catalog bytes")

    implementation = require_object(
        locator["implementation"],
        "implementation locator",
        {"repository", "repositorySlug", "release", "automation", "verifier"},
    )
    if implementation["repository"] != f"https://github.com/{implementation['repositorySlug']}":
        raise ValidationError("implementation repository URL and slug differ")
    release = require_object(
        implementation["release"],
        "release locator",
        {
            "version",
            "tag",
            "standardVersion",
            "contractVersion",
            "catalogDigest",
            "sourceCommit",
            "snapshotAggregateDigest",
            "url",
            "manifest",
            "snapshotManifest",
            "archives",
        },
    )
    version = require_text(release["version"], "release.version")
    release_standard_key = calver_key(
        release["standardVersion"], "release.standardVersion"
    )
    if release_standard_key > current_standard_key:
        raise ValidationError("release standardVersion is newer than the current standard")
    if not CONTRACT.fullmatch(
        require_text(release["contractVersion"], "release.contractVersion")
    ):
        raise ValidationError("release contractVersion is invalid")
    if not DIGEST.fullmatch(
        require_text(release["catalogDigest"], "release.catalogDigest")
    ):
        raise ValidationError("release catalogDigest is invalid")
    commit = require_text(release["sourceCommit"], "release.sourceCommit")
    if not SEMVER.fullmatch(version) or release["tag"] != f"v{version}":
        raise ValidationError("release version and tag are not an exact stable SemVer pair")
    if not COMMIT.fullmatch(commit):
        raise ValidationError("release source commit is not a full lowercase commit SHA")
    snapshot_digest = require_text(release["snapshotAggregateDigest"], "release.snapshotAggregateDigest")
    if not DIGEST.fullmatch(snapshot_digest):
        raise ValidationError("release snapshot aggregate digest is invalid")
    expected_release_url = f"{implementation['repository']}/releases/tag/{release['tag']}"
    if release["url"] != expected_release_url:
        raise ValidationError("release URL does not match the exact tag")

    manifest = require_object(release["manifest"], "release manifest locator", {"name", "url", "sha256"})
    if manifest["name"] != "release-manifest.json":
        raise ValidationError("release manifest name is not stable")
    expected_manifest_url = (
        f"{implementation['repository']}/releases/download/{release['tag']}/{manifest['name']}"
    )
    if manifest["url"] != expected_manifest_url or not SHA256.fullmatch(manifest["sha256"]):
        raise ValidationError("release manifest URL or SHA-256 is invalid")

    snapshot_manifest = require_object(
        release["snapshotManifest"],
        "standard snapshot manifest locator",
        {"name", "url", "sha256"},
    )
    if snapshot_manifest["name"] != "standard-snapshot-manifest.json":
        raise ValidationError("standard snapshot manifest name is not stable")
    expected_snapshot_url = (
        f"{implementation['repository']}/releases/download/{release['tag']}/"
        f"{snapshot_manifest['name']}"
    )
    if (
        snapshot_manifest["url"] != expected_snapshot_url
        or not SHA256.fullmatch(snapshot_manifest["sha256"])
    ):
        raise ValidationError("standard snapshot manifest URL or SHA-256 is invalid")

    archives = release["archives"]
    if not isinstance(archives, list) or len(archives) != 4:
        raise ValidationError("release locator must contain exactly four platform archives")
    platforms: set[tuple[str, str]] = set()
    for index, value in enumerate(archives):
        archive = require_object(value, f"release archive {index}", {"os", "architecture", "name", "sha256"})
        platform = (archive["os"], archive["architecture"])
        platforms.add(platform)
        expected_name = f"golden-path_{version}_{platform[0]}_{platform[1]}.tar.gz"
        if archive["name"] != expected_name or not SHA256.fullmatch(archive["sha256"]):
            raise ValidationError(f"release archive identity is invalid for {platform}")
    expected_platforms = {
        ("darwin", "amd64"),
        ("darwin", "arm64"),
        ("linux", "amd64"),
        ("linux", "arm64"),
    }
    if platforms != expected_platforms:
        raise ValidationError("release archive platform set is incomplete or duplicated")

    automation = require_object(
        implementation["automation"], "automation locator", {"reusableWorkflow", "setupAction"}
    )
    expected_workflow = (
        f"{implementation['repositorySlug']}/.github/workflows/golden-path-quality.yml@{commit}"
    )
    expected_action = f"{implementation['repositorySlug']}/actions/setup-golden-path@{commit}"
    if automation["reusableWorkflow"] != expected_workflow or automation["setupAction"] != expected_action:
        raise ValidationError("shared automation is not pinned to the release source commit")

    verifier = require_object(
        implementation["verifier"], "verifier locator", {"githubCliVersion", "signerWorkflow"}
    )
    if not SEMVER.fullmatch(verifier["githubCliVersion"]):
        raise ValidationError("GitHub CLI verifier is not an exact stable SemVer")
    expected_signer = f"{implementation['repositorySlug']}/.github/workflows/release.yml"
    if verifier["signerWorkflow"] != expected_signer:
        raise ValidationError("release signer workflow differs from the implementation repository")

    discovery = require_object(
        locator["discovery"],
        "discovery locator",
        {
            "bootstrapGuide",
            "capabilityMatrix",
            "workflowTemplate",
            "workflowTemplateProperties",
            "dryRunFixture",
            "hostingAdapterSchema",
            "hostingAdapterExample",
        },
    )
    for key, value in discovery.items():
        local_file(value, f"discovery.{key}")
    return locator


def validate_workflow_template(locator: dict[str, Any]) -> None:
    implementation = locator["implementation"]
    release = implementation["release"]
    workflow_path = local_file(locator["discovery"]["workflowTemplate"], "workflow template")
    workflow = workflow_path.read_text()
    required = [
        f"uses: {implementation['automation']['reusableWorkflow']}",
        "permissions:\n  contents: read",
        "working-directory: .",
        f"profiles: '{PROFILE_PLACEHOLDER}'",
        f"checker-version: '{release['version']}'",
        f"source-commit: '{release['sourceCommit']}'",
        f"github-cli-version: '{implementation['verifier']['githubCliVersion']}'",
    ]
    archive_inputs = {
        ("darwin", "amd64"): "darwin-amd64-sha256",
        ("darwin", "arm64"): "darwin-arm64-sha256",
        ("linux", "amd64"): "linux-amd64-sha256",
        ("linux", "arm64"): "linux-arm64-sha256",
    }
    for archive in release["archives"]:
        required.append(
            f"{archive_inputs[(archive['os'], archive['architecture'])]}: '{archive['sha256']}'"
        )
    for text in required:
        if text not in workflow:
            raise ValidationError(f"workflow template omits immutable caller text: {text}")
    try:
        json.loads(PROFILE_PLACEHOLDER)
    except json.JSONDecodeError:
        pass
    else:
        raise ValidationError("workflow template profile placeholder must be invalid JSON")
    if workflow.count("$default-branch") != 2:
        raise ValidationError("workflow template must use the default-branch placeholder for push and pull request")
    forbidden = [
        r"@(main|master|dev|latest|v[0-9])(?:\s|$)",
        r"raw\.githubusercontent\.com",
        r"\bsecrets:\s*inherit\b",
        r"\benvironment:\s*",
        r"\bid-token:\s*write\b",
        r"\battestations:\s*write\b",
    ]
    for pattern in forbidden:
        if re.search(pattern, workflow, re.IGNORECASE | re.MULTILINE):
            raise ValidationError(f"workflow template contains a mutable or paid-baseline construct: {pattern}")
    if permission_mapping(workflow, 0, "workflow template") != {"contents": "read"}:
        raise ValidationError("workflow template permissions must be exactly contents: read")

    properties_path = local_file(
        locator["discovery"]["workflowTemplateProperties"], "workflow template properties"
    )
    properties = require_object(
        load_json(properties_path),
        "workflow template properties",
        {"name", "description", "iconName", "categories"},
    )
    if properties_path.name != workflow_path.stem + ".properties.json":
        raise ValidationError("workflow template and properties file names do not match")
    if not all(isinstance(properties[key], str) and properties[key] for key in ("name", "description", "iconName")):
        raise ValidationError("workflow template display metadata is incomplete")
    if not properties["iconName"].startswith("octicon "):
        raise ValidationError("workflow template icon is not an explicit Octicon")
    if properties["categories"] != ["Continuous integration"]:
        raise ValidationError("workflow template category is not the stable CI discovery category")


def validate_snapshot_source_binding(
    snapshot_source: dict[str, Any], release_source: dict[str, Any]
) -> None:
    if snapshot_source != release_source:
        differing_fields = sorted(
            key
            for key in snapshot_source.keys() | release_source.keys()
            if snapshot_source.get(key) != release_source.get(key)
        )
        raise ValidationError(
            "standard snapshot source differs from the release manifest: "
            + ", ".join(differing_fields)
        )


def validate_snapshot_source_binding_self_test() -> None:
    baseline = {
        "repository": "https://github.com/5010-dev/.github",
        "commit": "1" * 40,
        "path": "docs/standards/developer-tooling",
        "gitTree": "2" * 40,
    }
    validate_snapshot_source_binding(baseline, baseline.copy())
    for field in ("commit", "gitTree"):
        mutation = baseline.copy()
        mutation[field] = "0" * 40
        try:
            validate_snapshot_source_binding(baseline, mutation)
        except ValidationError:
            continue
        raise ValidationError(
            f"standard snapshot source binding self-test accepted a changed {field}"
        )


def validate_standard_snapshot(
    locator: dict[str, Any], manifest_path: Path, release_manifest_path: Path
) -> None:
    release_manifest = load_json(release_manifest_path)
    if not isinstance(release_manifest, dict):
        raise ValidationError("release manifest must be an object")
    if release_manifest.get("schemaVersion") != "golden-path-release-manifest/v2":
        raise ValidationError("release manifest schemaVersion differs")
    release_snapshot = require_object(
        release_manifest.get("standardSnapshot"),
        "release standard snapshot",
        {"file", "source", "aggregateDigest"},
    )
    release_source = require_object(
        release_snapshot["source"],
        "release standard snapshot source",
        {"repository", "commit", "path", "gitTree"},
    )
    snapshot = require_object(
        load_json(manifest_path),
        "standard snapshot manifest",
        {"schemaVersion", "standardVersion", "contractVersion", "source", "aggregate", "files"},
    )
    standard = locator["standard"]
    release = locator["implementation"]["release"]
    expected_release_source = {
        "repository": locator["implementation"]["repository"],
        "commit": release["sourceCommit"],
        "tag": release["tag"],
    }
    if release_manifest.get("standardVersion") != release["standardVersion"]:
        raise ValidationError("release manifest standard version differs")
    if release_manifest.get("contractVersion") != release["contractVersion"]:
        raise ValidationError("release manifest contract version differs")
    if release_manifest.get("catalogDigest") != release["catalogDigest"]:
        raise ValidationError("release manifest catalog digest differs")
    if release_manifest.get("source") != expected_release_source:
        raise ValidationError("release manifest source identity differs")
    if snapshot["schemaVersion"] != "golden-path-standard-snapshot/v1":
        raise ValidationError("standard snapshot manifest schemaVersion differs")
    if snapshot["standardVersion"] != release["standardVersion"]:
        raise ValidationError("standard snapshot manifest version differs")
    if snapshot["contractVersion"] != release["contractVersion"]:
        raise ValidationError("standard snapshot manifest contract differs")
    source = require_object(
        snapshot["source"],
        "standard snapshot source",
        {"repository", "commit", "path", "gitTree"},
    )
    if source["repository"] != standard["repository"] or source["path"] != standard["snapshotPath"]:
        raise ValidationError("standard snapshot source authority differs")
    if not COMMIT.fullmatch(require_text(source["commit"], "standard snapshot source commit")):
        raise ValidationError("standard snapshot source commit is invalid")
    if not COMMIT.fullmatch(require_text(source["gitTree"], "standard snapshot source tree")):
        raise ValidationError("standard snapshot source tree is invalid")
    validate_snapshot_source_binding(source, release_source)
    aggregate = require_object(
        snapshot["aggregate"],
        "standard snapshot aggregate",
        {"algorithm", "definition", "digest"},
    )
    if aggregate["algorithm"] != "sha256":
        raise ValidationError("standard snapshot aggregate algorithm differs")
    expected_aggregate_definition = (
        "SHA-256 of UTF-8 lines sorted by snapshot-relative path, each formatted as "
        f"<file-sha256>  standards/snapshots/{release['standardVersion']}/"
        "<snapshot-relative-path>\\n, "
        "excluding manifest.json"
    )
    if aggregate["definition"] != expected_aggregate_definition:
        raise ValidationError("standard snapshot aggregate definition differs")
    aggregate_digest = require_text(aggregate["digest"], "standard snapshot aggregate digest")
    if not SHA256.fullmatch(aggregate_digest):
        raise ValidationError("standard snapshot aggregate digest is invalid")
    if f"sha256:{aggregate_digest}" != release["snapshotAggregateDigest"]:
        raise ValidationError("standard snapshot aggregate differs from the release locator")
    if release_snapshot["aggregateDigest"] != release["snapshotAggregateDigest"]:
        raise ValidationError("release manifest standard snapshot aggregate differs")

    declared_files = snapshot["files"]
    if not isinstance(declared_files, dict) or not declared_files:
        raise ValidationError("standard snapshot file inventory is empty")
    if release["standardVersion"] != standard["version"]:
        return

    snapshot_root = (ROOT / standard["snapshotPath"]).resolve()
    actual_machine_files = {
        path.relative_to(snapshot_root).as_posix()
        for parent in (snapshot_root / "rules", snapshot_root / "schemas")
        for path in parent.rglob("*.json")
        if path.is_file()
    }
    if set(declared_files) != actual_machine_files:
        raise ValidationError("standard snapshot machine file inventory differs from policy source")
    aggregate_lines: list[str] = []
    for relative, expected_digest in sorted(declared_files.items()):
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValidationError(f"standard snapshot path is unsafe: {relative}")
        if not isinstance(expected_digest, str) or not SHA256.fullmatch(expected_digest):
            raise ValidationError(f"standard snapshot file digest is invalid: {relative}")
        policy_file = (snapshot_root / relative_path).resolve()
        try:
            policy_file.relative_to(snapshot_root)
        except ValueError as error:
            raise ValidationError(f"standard snapshot path escapes policy source: {relative}") from error
        if not policy_file.is_file():
            raise ValidationError(f"standard snapshot file is missing: {relative}")
        actual_digest = hashlib.sha256(policy_file.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            raise ValidationError(f"standard snapshot file digest differs: {relative}")
        aggregate_lines.append(
            f"{actual_digest}  standards/snapshots/{release['standardVersion']}/{relative}\n"
        )
    actual_aggregate = hashlib.sha256("".join(aggregate_lines).encode()).hexdigest()
    if actual_aggregate != aggregate_digest:
        raise ValidationError("standard snapshot aggregate cannot be reproduced from policy source")


def validate_fixture_and_docs(locator: dict[str, Any]) -> None:
    fixture_path = local_file(locator["discovery"]["dryRunFixture"], "dry-run fixture")
    fixture = fixture_path.read_text()
    required_fixture = [
        "schemaVersion: golden-path-generator-request/v1",
        "layout: documentation",
        "profiles: [documentation]",
        "artifactTypes: [documentation]",
    ]
    for text in required_fixture:
        if fixture.count(text) != 1:
            raise ValidationError(f"dry-run fixture must contain exactly one {text!r}")

    bootstrap_path = local_file(locator["discovery"]["bootstrapGuide"], "bootstrap guide")
    capability_path = local_file(locator["discovery"]["capabilityMatrix"], "capability matrix")
    bootstrap = bootstrap_path.read_text()
    capability = capability_path.read_text()
    bootstrap_script = (ROOT / "scripts/docs/check-golden-path-bootstrap.sh").read_text()
    for text in (
        "golden-path-bootstrap.v1.json",
        "golden-path-quality.yml",
        "golden-path-exceptions.yaml",
        "golden-path-native-roots.yaml",
        "GitHub capability matrix",
        "exact GitHub CLI version",
        "exact release version declared by",
        "--write",
        "separate empty candidate",
    ):
        if text not in bootstrap:
            raise ValidationError(f"bootstrap guide omits required adoption boundary: {text}")
    for text in (
        "github-free-private",
        "report-only",
        "policy-required",
        "platform-enforced",
        "Organization Actions secrets",
        "Dependency Review",
        "private artifact attestations",
        "golden-path-hosting-adapter-selection/v1",
        "schemas/golden-path-hosting-adapter-selection-v1.schema.json",
        "Require an environment claim only when a paid Environment adapter is selected",
        "immutable OIDC",
        "Rollout and rollback",
    ):
        if text not in capability:
            raise ValidationError(f"capability matrix omits required boundary: {text}")
    for text in (
        f"--expected-profiles {PROFILE_PLACEHOLDER}",
        '[[ "$placeholder_status" -ne 2 ]]',
        'release["schemaVersion"] == "golden-path-release-manifest/v2"',
        'release["lifecycle"] == "stable"',
        'release["enforcement"] == ["report-only"]',
        'release["components"]["assetBundle"]["version"]',
    ):
        if text not in bootstrap_script:
            raise ValidationError(
                f"released bootstrap check omits required assertion: {text}"
            )


def validate_hosting_adapter_schema(locator: dict[str, Any]) -> None:
    schema_path = local_file(
        locator["discovery"]["hostingAdapterSchema"], "hosting adapter schema"
    )
    example_path = local_file(
        locator["discovery"]["hostingAdapterExample"], "hosting adapter example"
    )
    schema = load_json(schema_path)
    example = load_json(example_path)
    if not isinstance(schema, dict) or not isinstance(example, dict):
        raise ValidationError("hosting adapter schema and example must be JSON objects")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValidationError("hosting adapter schema must use JSON Schema Draft 2020-12")
    if schema.get("$id") != "urn:5010-dev:golden-path:hosting-adapter-selection:v1":
        raise ValidationError("hosting adapter schema has an unexpected stable ID")
    schema_version = schema.get("properties", {}).get("schemaVersion", {})
    if schema_version.get("const") != "golden-path-hosting-adapter-selection/v1":
        raise ValidationError("hosting adapter schemaVersion const is missing")

    validator_path = ROOT / "scripts/docs/check-developer-tooling-standard.py"
    spec = importlib.util.spec_from_file_location(
        "developer_tooling_standard_validator", validator_path
    )
    if spec is None or spec.loader is None:
        raise ValidationError("cannot load the dependency-light schema validator")
    validator = importlib.util.module_from_spec(spec)
    previous_bytecode_setting = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(validator)
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
    validator.errors.clear()
    validator.validate_schema_definition(schema, schema, "hosting adapter schema")
    if validator.errors:
        raise ValidationError(
            "hosting adapter schema definition is invalid: " + "; ".join(validator.errors)
        )

    findings: list[str] = []
    validator.validate_json_schema_instance(example, schema, schema, "$", findings)
    if findings:
        raise ValidationError("hosting adapter example is invalid: " + "; ".join(findings))

    adapters = example.get("adapters")
    if not isinstance(adapters, dict) or len(adapters) != 1:
        raise ValidationError("hosting adapter example must contain exactly one keyed adapter")
    adapter_id = next(iter(adapters))

    invalid_examples: list[tuple[str, dict[str, Any]]] = []
    missing_owner = copy.deepcopy(example)
    del missing_owner["adapters"][adapter_id]["owner"]
    invalid_examples.append(("missing owner", missing_owner))
    missing_enabled_at = copy.deepcopy(example)
    del missing_enabled_at["adapters"][adapter_id]["enabledAt"]
    invalid_examples.append(("missing activation time", missing_enabled_at))
    secret_property = copy.deepcopy(example)
    secret_property["adapters"][adapter_id]["secretValue"] = "must-not-be-recorded"
    invalid_examples.append(("secret-like extra property", secret_property))
    invalid_state = copy.deepcopy(example)
    invalid_state["adapters"][adapter_id]["state"] = "unknown"
    invalid_examples.append(("unknown state", invalid_state))
    invalid_adapter_id = copy.deepcopy(example)
    invalid_adapter = invalid_adapter_id["adapters"].pop(adapter_id)
    invalid_adapter_id["adapters"]["Invalid Adapter"] = invalid_adapter
    invalid_examples.append(("invalid adapter ID", invalid_adapter_id))
    for label, invalid in invalid_examples:
        negative_findings: list[str] = []
        validator.validate_json_schema_instance(
            invalid, schema, schema, "$", negative_findings
        )
        if not negative_findings:
            raise ValidationError(f"hosting adapter schema accepted {label}")


def workflow_event_paths(workflow: str, event: str) -> list[str]:
    lines = workflow.splitlines()
    event_start = next(
        (index for index, line in enumerate(lines) if line == f"  {event}:"), None
    )
    if event_start is None:
        raise ValidationError(f"governance workflow omits the {event} event")
    event_end = next(
        (
            index
            for index in range(event_start + 1, len(lines))
            if lines[index]
            and not lines[index].startswith("    ")
            and lines[index].startswith("  ")
        ),
        len(lines),
    )
    paths_start = next(
        (
            index
            for index in range(event_start + 1, event_end)
            if lines[index] == "    paths:"
        ),
        None,
    )
    if paths_start is None:
        raise ValidationError(f"governance workflow {event} event omits paths")
    values: list[str] = []
    for line in lines[paths_start + 1 : event_end]:
        match = re.fullmatch(r'      - "([^"]+)"', line)
        if match:
            values.append(match.group(1))
            continue
        if line and not line.startswith("      "):
            break
    if not values or len(values) != len(set(values)):
        raise ValidationError(f"governance workflow {event} paths are empty or duplicated")
    return values


def permission_mapping(workflow: str, indent: int, context: str) -> dict[str, str]:
    prefix = " " * indent
    lines = workflow.splitlines()
    starts = [index for index, line in enumerate(lines) if line == f"{prefix}permissions:"]
    if len(starts) != 1:
        raise ValidationError(f"{context} must contain exactly one permissions mapping")
    values: dict[str, str] = {}
    item_prefix = " " * (indent + 2)
    for line in lines[starts[0] + 1 :]:
        if not line.startswith(item_prefix):
            break
        match = re.fullmatch(rf"{re.escape(item_prefix)}([a-z-]+): ([a-z-]+)", line)
        if not match or match.group(1) in values:
            raise ValidationError(f"{context} permissions mapping is malformed")
        values[match.group(1)] = match.group(2)
    return values


def validate_governance_workflow(locator: dict[str, Any]) -> None:
    workflow = (ROOT / ".github/workflows/golden-path-bootstrap.yml").read_text()
    implementation = locator["implementation"]
    release = implementation["release"]
    required = [
        f"uses: {implementation['automation']['setupAction']}",
        "run: python3 scripts/docs/check-golden-path-integration.py",
        "run: scripts/docs/check-golden-path-bootstrap.sh",
        "GOLDEN_PATH_BIN: ${{ steps.golden-path.outputs.binary-path }}",
        f"checker-version: '{release['version']}'",
        f"source-commit: '{release['sourceCommit']}'",
        f"github-cli-version: '{implementation['verifier']['githubCliVersion']}'",
        'actionlint = "1.7.12"',
        "actionlint .github/workflows/docs.yml \\",
    ]
    archive_inputs = {
        ("darwin", "amd64"): "darwin-amd64-sha256",
        ("darwin", "arm64"): "darwin-arm64-sha256",
        ("linux", "amd64"): "linux-amd64-sha256",
        ("linux", "arm64"): "linux-arm64-sha256",
    }
    for archive in release["archives"]:
        required.append(
            f"{archive_inputs[(archive['os'], archive['architecture'])]}: '{archive['sha256']}'"
        )
    for text in required:
        if text not in workflow:
            raise ValidationError(f"governance workflow omits bootstrap integration text: {text}")
    for match in re.finditer(r"^\s*uses:\s+([^\s#]+)", workflow, re.MULTILINE):
        reference = match.group(1)
        if reference.startswith("./"):
            continue
        if not re.search(r"@[a-f0-9]{40}$", reference):
            raise ValidationError(f"governance workflow action is not full-SHA pinned: {reference}")
    required_paths = {
        ".github/workflows/golden-path-bootstrap.yml",
        ".github/workflows/docs.yml",
        "docs/decisions/0006-adopt-developer-tooling-golden-path.md",
        "docs/guides/adopting-developer-tooling.md",
        "docs/guides/bootstrap-new-repository.md",
        "docs/guides/github-hosting-capabilities.md",
        "docs/guides/golden-path-bootstrap.v1.json",
        "docs/guides/schemas/**",
        "docs/standards/developer-tooling/**",
        "scripts/docs/check-golden-path-bootstrap.sh",
        "scripts/docs/check-golden-path-integration.py",
        "scripts/docs/fixtures/golden-path-bootstrap/**",
        "workflow-templates/**",
    }
    pull_request_paths = workflow_event_paths(workflow, "pull_request")
    push_paths = workflow_event_paths(workflow, "push")
    if set(pull_request_paths) != required_paths or set(push_paths) != required_paths:
        raise ValidationError("governance workflow trigger paths differ from the complete integration source set")
    if pull_request_paths != push_paths:
        raise ValidationError("governance workflow pull_request and push path ordering differs")
    if workflow.count("permissions: {}") != 1:
        raise ValidationError("governance workflow top-level permissions must be exactly empty")
    if permission_mapping(workflow, 4, "governance bootstrap job") != {"contents": "read"}:
        raise ValidationError("governance bootstrap job permissions must be exactly contents: read")


def validate_documentation_workflow_source(workflow: str) -> None:
    required = [
        "runs-on: ubuntu-24.04",
        "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "run: scripts/docs/check-repository.sh",
        "persist-credentials: false",
    ]
    for text in required:
        if workflow.count(text) != 1:
            raise ValidationError(
                f"documentation workflow must contain exactly one required control: {text}"
            )
    for match in re.finditer(r"^\s*uses:\s+([^\s#]+)", workflow, re.MULTILINE):
        reference = match.group(1)
        if reference.startswith("./"):
            continue
        if not re.search(r"@[a-f0-9]{40}$", reference):
            raise ValidationError(
                f"documentation workflow action is not full-SHA pinned: {reference}"
            )

    required_paths = {
        "**/*.md",
        ".github/workflows/docs.yml",
        ".github/workflows/golden-path-bootstrap.yml",
        "docs/guides/golden-path-bootstrap.v1.json",
        "docs/guides/schemas/**",
        "docs/standards/developer-tooling/**",
        "docs/standards/release-versioning/**",
        "scripts/docs/**",
        "workflow-templates/**",
    }
    pull_request_paths = workflow_event_paths(workflow, "pull_request")
    push_paths = workflow_event_paths(workflow, "push")
    if set(pull_request_paths) != required_paths or set(push_paths) != required_paths:
        raise ValidationError(
            "documentation workflow trigger paths differ from the complete governance source set"
        )
    if pull_request_paths != push_paths:
        raise ValidationError(
            "documentation workflow pull_request and push path ordering differs"
        )
    if workflow.count("permissions: {}") != 1:
        raise ValidationError(
            "documentation workflow top-level permissions must be exactly empty"
        )
    if permission_mapping(workflow, 4, "documentation governance job") != {"contents": "read"}:
        raise ValidationError(
            "documentation governance job permissions must be exactly contents: read"
        )


def validate_documentation_workflow() -> None:
    workflow = (ROOT / ".github/workflows/docs.yml").read_text()
    validate_documentation_workflow_source(workflow)
    mutations = [
        (
            "additional write permission",
            workflow.replace(
                "      contents: read\n",
                "      contents: read\n      actions: write\n",
                1,
            ),
        ),
        (
            "missing workflow-template path",
            workflow.replace('      - "workflow-templates/**"\n', ""),
        ),
        (
            "mutable runner",
            workflow.replace("runs-on: ubuntu-24.04", "runs-on: ubuntu-latest", 1),
        ),
        (
            "credential-persisting checkout",
            workflow.replace(
                "        with:\n          persist-credentials: false\n",
                "",
                1,
            ),
        ),
    ]
    for label, mutation in mutations:
        if mutation == workflow:
            raise ValidationError(
                f"documentation workflow self-test could not construct {label}"
            )
        try:
            validate_documentation_workflow_source(mutation)
        except ValidationError:
            continue
        raise ValidationError(f"documentation workflow validator accepted {label}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the policy-owned Golden Path bootstrap integration"
    )
    parser.add_argument(
        "--snapshot-manifest",
        type=Path,
        help="verified released standard-snapshot-manifest.json to compare with policy source",
    )
    parser.add_argument(
        "--release-manifest",
        type=Path,
        help="verified release-manifest.json that binds the standard snapshot source",
    )
    arguments = parser.parse_args()
    try:
        validate_snapshot_source_binding_self_test()
        if (arguments.snapshot_manifest is None) != (arguments.release_manifest is None):
            raise ValidationError(
                "snapshot and release manifests must be provided together"
            )
        locator = validate_locator()
        validate_workflow_template(locator)
        validate_fixture_and_docs(locator)
        validate_hosting_adapter_schema(locator)
        validate_governance_workflow(locator)
        validate_documentation_workflow()
        if arguments.snapshot_manifest is not None and arguments.release_manifest is not None:
            validate_standard_snapshot(
                locator,
                arguments.snapshot_manifest,
                arguments.release_manifest,
            )
    except ValidationError as error:
        print(f"Golden Path integration check: FAILED: {error}", file=sys.stderr)
        return 1
    print("Golden Path integration check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
