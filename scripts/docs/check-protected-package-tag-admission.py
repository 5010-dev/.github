#!/usr/bin/env python3
"""Fail-closed admission checker for protected package-tag publication.

The checker is intentionally dependency-free. It validates one repository-local
profile contract and derives publication identity from an exact Git diff. It
does not publish, inspect hosting rulesets, or query a package registry.
"""

from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn


DEFAULT_CONTRACT = ".github/release-policy/protected-package-tag.v1.json"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
TOML_DOTTED_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

EXPECTED_PERMISSIONS = {
    "validation": ["contents: read"],
    "consumption": ["packages: read"],
    "publication": ["packages: write"],
}
EXPECTED_EFFECTS = {
    "allowed": [
        "package-tag-creation",
        "registry-package-publication",
    ],
    "forbidden": [
        "branch-push",
        "source-commit",
        "service-deployment",
        "application-deployment",
        "oci-publication",
        "object-storage-publication",
        "sibling-release-unit-mutation",
    ],
}


class AdmissionError(Exception):
    """A deterministic admission failure."""


@dataclass(frozen=True)
class DiffEntry:
    status: str
    paths: tuple[str, ...]


def reject(message: str) -> NoReturn:
    raise AdmissionError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        reject(message)


def require_object(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def require_string(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value), f"{label} must be a non-empty string")
    return value


def require_exact_keys(
    value: dict[str, Any], required: set[str], label: str, optional: set[str] | None = None
) -> None:
    optional = optional or set()
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - required - optional)
    require(not missing, f"{label} is missing required fields: {', '.join(missing)}")
    require(not unknown, f"{label} has unknown fields: {', '.join(unknown)}")


def validate_id(value: Any, label: str) -> str:
    text = require_string(value, label)
    require(len(text) <= 64 and ID_RE.fullmatch(text) is not None, f"{label} is not a valid release-unit ID")
    return text


def validate_relative(value: Any, label: str, *, allow_glob: bool = False) -> str:
    text = require_string(value, label)
    require(len(text) <= 300, f"{label} is too long")
    require("\\" not in text, f"{label} must use POSIX separators")
    path = PurePosixPath(text)
    require(not path.is_absolute(), f"{label} must be repository-relative")
    require(".." not in path.parts, f"{label} must not traverse outside the repository")
    if not allow_glob:
        require(not any(char in text for char in "*?["), f"{label} must not contain glob syntax")
    return text


def validate_patterns(value: Any, label: str) -> list[str]:
    require(isinstance(value, list) and bool(value), f"{label} must be a non-empty array")
    patterns = [validate_relative(item, f"{label} item", allow_glob=True) for item in value]
    require(len(patterns) == len(set(patterns)), f"{label} must not contain duplicates")
    return patterns


def validate_workflow(value: Any, label: str) -> str:
    path = validate_relative(value, label)
    require(
        path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")),
        f"{label} must name a repository workflow",
    )
    require(PurePosixPath(path).parent == PurePosixPath(".github/workflows"), f"{label} must name a top-level workflow file")
    return path


def validate_contract(document: Any) -> dict[str, Any]:
    contract = require_object(document, "profile contract")
    required = {
        "schemaVersion",
        "profile",
        "source",
        "intentDirectory",
        "releaseUnit",
        "siblingReleaseUnits",
        "channels",
        "minimumPermissions",
        "publicationEffects",
        "serialization",
        "owners",
    }
    require_exact_keys(contract, required, "profile contract", {"$schema"})
    if "$schema" in contract:
        require_string(contract["$schema"], "profile contract.$schema")
    require(contract["schemaVersion"] == "protected-package-tag-profile/v1", "unsupported profile schemaVersion")
    require(contract["profile"] == "protected-package-tag", "unsupported release profile")

    source = require_object(contract["source"], "profile source")
    require_exact_keys(source, {"branch", "ref", "admissionEvent"}, "profile source")
    require(source == {"branch": "dev", "ref": "refs/heads/dev", "admissionEvent": "push"}, "profile source must select the dev push boundary")

    contract["intentDirectory"] = validate_relative(contract["intentDirectory"], "intentDirectory")

    unit = require_object(contract["releaseUnit"], "releaseUnit")
    unit_fields = {
        "id",
        "artifactProfile",
        "packageName",
        "registry",
        "compatibilityContract",
        "buildClosure",
        "versionSource",
        "changelog",
        "tagPattern",
        "validationWorkflow",
        "publicationWorkflow",
        "releasePreparationPaths",
    }
    require_exact_keys(unit, unit_fields, "releaseUnit")
    unit["id"] = validate_id(unit["id"], "releaseUnit.id")
    require(unit["artifactProfile"] == "registry-package", "releaseUnit.artifactProfile must be registry-package")
    package_name = require_string(unit["packageName"], "releaseUnit.packageName")
    require(len(package_name) <= 214, "releaseUnit.packageName is too long")
    registry = require_string(unit["registry"], "releaseUnit.registry")
    require(registry.startswith("https://"), "releaseUnit.registry must use https")
    unit["compatibilityContract"] = validate_relative(unit["compatibilityContract"], "releaseUnit.compatibilityContract")
    unit["buildClosure"] = validate_patterns(unit["buildClosure"], "releaseUnit.buildClosure")
    unit["changelog"] = validate_relative(unit["changelog"], "releaseUnit.changelog")
    unit["validationWorkflow"] = validate_workflow(unit["validationWorkflow"], "releaseUnit.validationWorkflow")
    unit["publicationWorkflow"] = validate_workflow(unit["publicationWorkflow"], "releaseUnit.publicationWorkflow")
    require(unit["validationWorkflow"] != unit["publicationWorkflow"], "validation and publication workflows must be separate")
    unit["releasePreparationPaths"] = validate_patterns(unit["releasePreparationPaths"], "releaseUnit.releasePreparationPaths")

    version_source = require_object(unit["versionSource"], "releaseUnit.versionSource")
    source_type = require_string(version_source.get("type"), "releaseUnit.versionSource.type")
    if source_type == "json-pointer":
        require_exact_keys(
            version_source,
            {"type", "path", "versionPointer", "packageNamePointer"},
            "releaseUnit.versionSource",
        )
        version_pointer = require_string(
            version_source["versionPointer"], "releaseUnit.versionSource.versionPointer"
        )
        package_name_pointer = require_string(
            version_source["packageNamePointer"], "releaseUnit.versionSource.packageNamePointer"
        )
        require(version_pointer.startswith("/"), "releaseUnit.versionSource.versionPointer must be a non-root JSON Pointer")
        require(package_name_pointer.startswith("/"), "releaseUnit.versionSource.packageNamePointer must be a non-root JSON Pointer")
        require(version_pointer != package_name_pointer, "package name and version JSON Pointers must differ")
    elif source_type == "toml-key":
        require_exact_keys(
            version_source,
            {"type", "path", "versionKey", "packageNameKey"},
            "releaseUnit.versionSource",
        )
        version_key = require_string(version_source["versionKey"], "releaseUnit.versionSource.versionKey")
        package_name_key = require_string(version_source["packageNameKey"], "releaseUnit.versionSource.packageNameKey")
        require(TOML_DOTTED_KEY_RE.fullmatch(version_key) is not None, "releaseUnit.versionSource.versionKey must be a dotted bare TOML key")
        require(TOML_DOTTED_KEY_RE.fullmatch(package_name_key) is not None, "releaseUnit.versionSource.packageNameKey must be a dotted bare TOML key")
        require(version_key != package_name_key, "package name and version TOML keys must differ")
    else:
        reject("releaseUnit.versionSource.type must be json-pointer or toml-key")
    version_source["path"] = validate_relative(version_source["path"], "releaseUnit.versionSource.path")

    tag_pattern = require_string(unit["tagPattern"], "releaseUnit.tagPattern")
    require(10 <= len(tag_pattern) <= 200, "releaseUnit.tagPattern must contain 10 to 200 characters")
    require(tag_pattern.count("{version}") == 1, "releaseUnit.tagPattern must contain {version} exactly once")
    require(not any(character.isspace() for character in tag_pattern), "releaseUnit.tagPattern must not contain whitespace")
    without_version = tag_pattern.replace("{version}", "")
    require("{" not in without_version and "}" not in without_version, "releaseUnit.tagPattern has an unsupported placeholder")

    siblings = contract["siblingReleaseUnits"]
    require(isinstance(siblings, list) and bool(siblings), "siblingReleaseUnits must be a non-empty array")
    sibling_ids: set[str] = set()
    for index, raw_sibling in enumerate(siblings):
        sibling = require_object(raw_sibling, f"siblingReleaseUnits[{index}]")
        require_exact_keys(sibling, {"id", "kind", "mutationPaths"}, f"siblingReleaseUnits[{index}]")
        sibling_id = validate_id(sibling["id"], f"siblingReleaseUnits[{index}].id")
        require(sibling_id != unit["id"], "a sibling release unit cannot be the package release unit")
        require(sibling_id not in sibling_ids, "siblingReleaseUnits contains duplicate IDs")
        sibling_ids.add(sibling_id)
        require(
            sibling["kind"] in {"registry-package", "service", "application", "oci-image", "other"},
            f"siblingReleaseUnits[{index}].kind is invalid",
        )
        sibling["mutationPaths"] = validate_patterns(sibling["mutationPaths"], f"siblingReleaseUnits[{index}].mutationPaths")
    require(
        any(sibling["kind"] in {"service", "application"} for sibling in siblings),
        "the profile requires at least one sibling service or application release unit",
    )

    channels = require_object(contract["channels"], "channels")
    require_exact_keys(channels, {"prerelease", "final"}, "channels")
    prerelease = require_object(channels["prerelease"], "channels.prerelease")
    final = require_object(channels["final"], "channels.final")
    require_exact_keys(prerelease, {"distTag"}, "channels.prerelease")
    require_exact_keys(final, {"distTag"}, "channels.final")
    prerelease_tag = require_string(prerelease["distTag"], "channels.prerelease.distTag")
    require(prerelease_tag != "latest", "prerelease dist-tag must not be latest")
    require(final["distTag"] == "latest", "final dist-tag must be latest")

    require(contract["minimumPermissions"] == EXPECTED_PERMISSIONS, "minimumPermissions must preserve the profile's least-privilege contract")
    require(contract["publicationEffects"] == EXPECTED_EFFECTS, "publicationEffects must preserve package-only effects")
    require(contract["serialization"] == {"scope": "release-unit-version", "cancelInProgress": False}, "serialization must be release-unit-version with cancellation disabled")

    owners = require_object(contract["owners"], "owners")
    require_exact_keys(owners, {"release", "credentials", "recovery"}, "owners")
    for owner_kind, owner in owners.items():
        owner_name = require_string(owner, f"owners.{owner_kind}")
        require(len(owner_name) <= 128, f"owners.{owner_kind} is too long")

    preparation = unit["releasePreparationPaths"]
    required_paths = [version_source["path"], unit["changelog"]]
    for required_path in required_paths:
        require(any(path_matches(required_path, pattern) for pattern in preparation), f"releasePreparationPaths does not admit required path: {required_path}")
    intent_probe = f"{contract['intentDirectory']}/intent.json"
    require(any(path_matches(intent_probe, pattern) for pattern in preparation), "releasePreparationPaths does not admit JSON release intents")
    return contract


def validate_intent(document: Any, label: str = "release intent") -> dict[str, Any]:
    intent = require_object(document, label)
    required = {"schemaVersion", "releaseUnit", "channel", "version", "source"}
    require_exact_keys(intent, required, label, {"$schema"})
    if "$schema" in intent:
        require_string(intent["$schema"], f"{label}.$schema")
    require(intent["schemaVersion"] == "package-release-intent/v1", f"{label} has an unsupported schemaVersion")
    intent["releaseUnit"] = validate_id(intent["releaseUnit"], f"{label}.releaseUnit")
    require(intent["channel"] in {"prerelease", "final"}, f"{label}.channel is invalid")
    version = require_string(intent["version"], f"{label}.version")
    require(len(version) <= 128, f"{label}.version is too long")
    match = SEMVER_RE.fullmatch(version)
    require(match is not None, f"{label}.version is not exact SemVer")
    if intent["channel"] == "prerelease":
        require(match.group(4) is not None, f"{label} prerelease channel requires a SemVer prerelease")
    else:
        require(match.group(4) is None, f"{label} final channel requires a final SemVer")

    source = require_object(intent["source"], f"{label}.source")
    require_exact_keys(source, {"ref", "baseCommit"}, f"{label}.source")
    require(source["ref"] == "refs/heads/dev", f"{label}.source.ref must be refs/heads/dev")
    require(isinstance(source["baseCommit"], str) and FULL_SHA_RE.fullmatch(source["baseCommit"]) is not None, f"{label}.source.baseCommit must be a lowercase full commit SHA")
    return intent


def path_matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def is_below(path: str, directory: str) -> bool:
    return path.startswith(f"{directory}/")


def git(repo: Path, *args: str, binary: bool = False, allow_failure: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0 and not allow_failure:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        reject(f"git {' '.join(args)} failed: {detail}")
    if allow_failure:
        return str(result.returncode)
    if binary:
        return result.stdout
    return result.stdout.decode("utf-8")


def git_json(repo: Path, revision: str, path: str, label: str) -> Any:
    raw = git(repo, "show", f"{revision}:{path}", binary=True)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        reject(f"{label} is not valid UTF-8 JSON: {error}")


def git_toml(repo: Path, revision: str, path: str, label: str) -> Any:
    raw = git(repo, "show", f"{revision}:{path}", binary=True)
    try:
        return tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
        reject(f"{label} is not valid UTF-8 TOML: {error}")


def git_path_exists(repo: Path, revision: str, path: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}:{path}"],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def parse_diff(repo: Path, base: str, head: str) -> list[DiffEntry]:
    raw = git(
        repo,
        "diff",
        "--name-status",
        "-z",
        "--find-renames",
        "--find-copies-harder",
        base,
        head,
        "--",
        binary=True,
    )
    parts = raw.split(b"\0")
    if parts and parts[-1] == b"":
        parts.pop()
    entries: list[DiffEntry] = []
    index = 0
    while index < len(parts):
        status = parts[index].decode("ascii", errors="strict")
        index += 1
        path_count = 2 if status.startswith(("R", "C")) else 1
        require(index + path_count <= len(parts), "git diff produced an incomplete name-status record")
        paths = tuple(parts[index + offset].decode("utf-8") for offset in range(path_count))
        index += path_count
        entries.append(DiffEntry(status=status, paths=paths))
    return entries


def json_pointer_tokens(pointer: str) -> list[str]:
    require(pointer.startswith("/"), "version JSON Pointer must start with /")
    return [token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/")]


def pointer_get(document: Any, pointer: str, label: str) -> Any:
    current = document
    for token in json_pointer_tokens(pointer):
        if isinstance(current, dict):
            require(token in current, f"{label} JSON Pointer does not exist: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            require(token.isdigit(), f"{label} JSON Pointer has a non-numeric array index: {pointer}")
            index = int(token)
            require(index < len(current), f"{label} JSON Pointer array index is out of range: {pointer}")
            current = current[index]
        else:
            reject(f"{label} JSON Pointer traverses a scalar: {pointer}")
    return current


def pointer_set(document: Any, pointer: str, value: Any, label: str) -> None:
    tokens = json_pointer_tokens(pointer)
    require(bool(tokens), f"{label} JSON Pointer must not select the document root")
    current = document
    for token in tokens[:-1]:
        if isinstance(current, dict):
            require(token in current, f"{label} JSON Pointer does not exist: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            require(token.isdigit() and int(token) < len(current), f"{label} JSON Pointer array index is invalid: {pointer}")
            current = current[int(token)]
        else:
            reject(f"{label} JSON Pointer traverses a scalar: {pointer}")
    last = tokens[-1]
    if isinstance(current, dict):
        require(last in current, f"{label} JSON Pointer does not exist: {pointer}")
        current[last] = value
    elif isinstance(current, list):
        require(last.isdigit() and int(last) < len(current), f"{label} JSON Pointer array index is invalid: {pointer}")
        current[int(last)] = value
    else:
        reject(f"{label} JSON Pointer traverses a scalar: {pointer}")


def dotted_get(document: Any, key: str, label: str) -> Any:
    current = document
    for token in key.split("."):
        require(isinstance(current, dict) and token in current, f"{label} TOML key does not exist: {key}")
        current = current[token]
    return current


def dotted_set(document: Any, key: str, value: Any, label: str) -> None:
    tokens = key.split(".")
    current = document
    for token in tokens[:-1]:
        require(isinstance(current, dict) and token in current, f"{label} TOML key does not exist: {key}")
        current = current[token]
    last = tokens[-1]
    require(isinstance(current, dict) and last in current, f"{label} TOML key does not exist: {key}")
    current[last] = value


def require_repository_file(repo: Path, revision: str, path: str, label: str) -> None:
    require(git_path_exists(repo, revision, path), f"{label} is missing at {revision}: {path}")


def admission(repo: Path, contract_path: str, base: str, head: str, event_ref: str) -> dict[str, Any]:
    require(repo.is_dir(), f"repository does not exist: {repo}")
    contract_path = validate_relative(contract_path, "contract path")
    require(FULL_SHA_RE.fullmatch(base) is not None, "base must be a lowercase full commit SHA")
    require(FULL_SHA_RE.fullmatch(head) is not None, "head must be a lowercase full commit SHA")
    require(base != head, "base and head must differ")
    require(git(repo, "rev-parse", "--verify", f"{base}^{{commit}}").strip() == base, "base does not resolve to the exact commit")
    require(git(repo, "rev-parse", "--verify", f"{head}^{{commit}}").strip() == head, "head does not resolve to the exact commit")
    ancestor_status = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, head],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode
    require(ancestor_status == 0, "base must be an ancestor of head")

    require_repository_file(repo, head, contract_path, "opt-in profile contract")
    contract = validate_contract(git_json(repo, head, contract_path, "profile contract"))
    require(event_ref == contract["source"]["ref"], "event ref does not match the profile source ref")

    unit = contract["releaseUnit"]
    for path_key in ("compatibilityContract", "changelog", "validationWorkflow", "publicationWorkflow"):
        require_repository_file(repo, head, unit[path_key], f"releaseUnit.{path_key}")

    entries = parse_diff(repo, base, head)
    require(bool(entries), "admission diff is empty")
    changed_paths = {path for entry in entries for path in entry.paths}
    require(contract_path not in changed_paths, "profile contract must be reviewed separately from release preparation")
    require(unit["validationWorkflow"] not in changed_paths, "validation workflow must be reviewed separately from release preparation")
    require(unit["publicationWorkflow"] not in changed_paths, "publication workflow must be reviewed separately from release preparation")

    for entry in entries:
        require(
            entry.status in {"A", "M"},
            f"release preparation may only add or modify files: {entry.status} {' -> '.join(entry.paths)}",
        )

    for sibling in contract["siblingReleaseUnits"]:
        for path in sorted(changed_paths):
            if any(path_matches(path, pattern) for pattern in sibling["mutationPaths"]):
                reject(f"sibling release-unit mutation is forbidden: {sibling['id']} changed {path}")

    for path in sorted(changed_paths):
        require(
            any(path_matches(path, pattern) for pattern in unit["releasePreparationPaths"]),
            f"changed path is outside release preparation: {path}",
        )

    intent_entries = [entry for entry in entries if any(is_below(path, contract["intentDirectory"]) for path in entry.paths)]
    require(len(intent_entries) == 1, "exactly one release intent change is required")
    intent_entry = intent_entries[0]
    require(intent_entry.status == "A" and len(intent_entry.paths) == 1, "release intent must be newly added; modification, rename, copy, or deletion is stale")
    intent_path = intent_entry.paths[0]
    require(PurePosixPath(intent_path).parent == PurePosixPath(contract["intentDirectory"]), "release intent must be directly inside intentDirectory")
    require(intent_path.endswith(".json"), "release intent must be a JSON file")
    intent = validate_intent(git_json(repo, head, intent_path, intent_path), intent_path)
    require(intent["releaseUnit"] == unit["id"], "release intent targets a different release unit")
    require(intent["source"]["ref"] == event_ref, "release intent source ref does not match the event ref")
    require(intent["source"]["baseCommit"] == base, "release intent is stale: source baseCommit does not equal the event before commit")

    listed = git(repo, "ls-tree", "-r", "--name-only", "-z", head, "--", contract["intentDirectory"], binary=True)
    intent_paths = [part.decode("utf-8") for part in listed.split(b"\0") if part]
    matching_identity: list[str] = []
    for historical_path in intent_paths:
        historical = validate_intent(git_json(repo, head, historical_path, historical_path), historical_path)
        if historical["releaseUnit"] == intent["releaseUnit"] and historical["version"] == intent["version"]:
            matching_identity.append(historical_path)
    require(matching_identity == [intent_path], "duplicate or conflicting release intent exists for the same release-unit and version")

    version_source = unit["versionSource"]
    version_path = version_source["path"]
    version_entries = [entry for entry in entries if version_path in entry.paths]
    require(len(version_entries) == 1 and version_entries[0].status == "M", "version source must be modified exactly once")
    if version_source["type"] == "json-pointer":
        base_manifest = git_json(repo, base, version_path, "base version source")
        head_manifest = git_json(repo, head, version_path, "head version source")
        base_version = pointer_get(base_manifest, version_source["versionPointer"], "base version source")
        head_version = pointer_get(head_manifest, version_source["versionPointer"], "head version source")
        base_package_name = pointer_get(base_manifest, version_source["packageNamePointer"], "base version source")
        head_package_name = pointer_get(head_manifest, version_source["packageNamePointer"], "head version source")
        expected_manifest = copy.deepcopy(base_manifest)
        pointer_set(expected_manifest, version_source["versionPointer"], head_version, "version source")
    else:
        base_manifest = git_toml(repo, base, version_path, "base version source")
        head_manifest = git_toml(repo, head, version_path, "head version source")
        base_version = dotted_get(base_manifest, version_source["versionKey"], "base version source")
        head_version = dotted_get(head_manifest, version_source["versionKey"], "head version source")
        base_package_name = dotted_get(base_manifest, version_source["packageNameKey"], "base version source")
        head_package_name = dotted_get(head_manifest, version_source["packageNameKey"], "head version source")
        expected_manifest = copy.deepcopy(base_manifest)
        dotted_set(expected_manifest, version_source["versionKey"], head_version, "version source")

    require(isinstance(base_package_name, str) and bool(base_package_name), "base native manifest package name is invalid")
    require(isinstance(head_package_name, str) and bool(head_package_name), "head native manifest package name is invalid")
    require(base_package_name == head_package_name, "native manifest package name changed during release preparation")
    require(head_package_name == unit["packageName"], "native manifest package name does not match releaseUnit.packageName")
    require(isinstance(base_version, str) and SEMVER_RE.fullmatch(base_version) is not None, "base manifest version is not exact SemVer")
    require(isinstance(head_version, str) and SEMVER_RE.fullmatch(head_version) is not None, "head manifest version is not exact SemVer")
    require(base_version != head_version, "manifest version did not change")
    require(head_version == intent["version"], "release intent version does not match the head manifest")
    require(expected_manifest == head_manifest, "version source changed outside the configured version field")

    changelog_entries = [entry for entry in entries if unit["changelog"] in entry.paths]
    require(len(changelog_entries) == 1 and changelog_entries[0].status in {"A", "M"}, "release changelog must be added or modified exactly once")

    rendered_tag = unit["tagPattern"].replace("{version}", head_version)
    tag_status = subprocess.run(
        ["git", "check-ref-format", f"refs/tags/{rendered_tag}"],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode
    require(tag_status == 0, "derived package tag is not a valid Git tag")

    channel = intent["channel"]
    dist_tag = contract["channels"][channel]["distTag"]
    return {
        "schemaVersion": "protected-package-tag-admission/v1",
        "status": "admitted",
        "releaseUnit": unit["id"],
        "packageName": unit["packageName"],
        "registry": unit["registry"],
        "channel": channel,
        "distTag": dist_tag,
        "version": head_version,
        "tag": rendered_tag,
        "intentPath": intent_path,
        "source": {
            "ref": event_ref,
            "baseCommit": base,
            "commit": head,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=".", help="repository root (default: current directory)")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT, help=f"fixed repository-local profile path (default: {DEFAULT_CONTRACT})")
    parser.add_argument("--base", required=True, help="exact merge-event before commit")
    parser.add_argument("--head", required=True, help="exact merge-event after commit")
    parser.add_argument("--event-ref", required=True, help="exact merge-event ref")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = admission(Path(args.repository).resolve(), args.contract, args.base, args.head, args.event_ref)
    except AdmissionError as error:
        print(f"protected package-tag admission: REJECTED: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
