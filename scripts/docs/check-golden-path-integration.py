#!/usr/bin/env python3
"""Validate the policy-owned Golden Path bootstrap and discovery surfaces."""

from __future__ import annotations

import hashlib
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
        raise ValidationError(f"cannot read valid JSON from {path.relative_to(ROOT)}: {error}") from error


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
            "entrypoint",
            "ruleCatalog",
            "catalogDigest",
            "metadataSchema",
            "exceptionSchema",
        },
    )
    entrypoint = local_file(standard["entrypoint"], "standard.entrypoint")
    rule_catalog = local_file(standard["ruleCatalog"], "standard.ruleCatalog")
    local_file(standard["metadataSchema"], "standard.metadataSchema")
    local_file(standard["exceptionSchema"], "standard.exceptionSchema")
    standard_source = entrypoint.read_text()
    version_match = re.search(r"^- Standard version: `([^`]+)`$", standard_source, re.MULTILINE)
    contract_match = re.search(r"^- Contract version: `([^`]+)`$", standard_source, re.MULTILINE)
    if not version_match or version_match.group(1) != standard["version"]:
        raise ValidationError("bootstrap standard version differs from the canonical entrypoint")
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
        {"version", "tag", "sourceCommit", "snapshotAggregateDigest", "url", "manifest", "archives"},
    )
    version = require_text(release["version"], "release.version")
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
        "profiles: '[]'",
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
    for text in (
        "golden-path-bootstrap.v1.json",
        "golden-path-quality.yml",
        "golden-path-exceptions.yaml",
        "GitHub capability matrix",
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
        "Rollout and rollback",
    ):
        if text not in capability:
            raise ValidationError(f"capability matrix omits required boundary: {text}")


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
        '"workflow-templates/**"',
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


def main() -> int:
    try:
        locator = validate_locator()
        validate_workflow_template(locator)
        validate_fixture_and_docs(locator)
        validate_governance_workflow(locator)
    except ValidationError as error:
        print(f"Golden Path integration check: FAILED: {error}", file=sys.stderr)
        return 1
    print("Golden Path integration check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
