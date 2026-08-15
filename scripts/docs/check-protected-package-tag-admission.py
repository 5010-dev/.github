#!/usr/bin/env python3
"""Fail-closed admission checker for protected package-tag publication.

The checker is intentionally dependency-free. It validates one repository-local
profile contract and derives normal, pre-mutation recovery, tag-only completion,
or pre-mutation completion-recovery identity from an exact Git diff. It does not publish,
inspect Actions or authorization-use history, inspect hosting rulesets or
pull-request approvals, download retained artifacts, or query a package registry.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import copy
import datetime as dt
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn


DEFAULT_CONTRACT = ".github/release-policy/protected-package-tag.v1.json"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
TOML_DOTTED_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")
WORKFLOW_RE = re.compile(r"^\.github/workflows/[^/]+\.ya?ml$")
WORKFLOW_RUN_URL_RE = re.compile(
    r"^https://github\.com/[^/\s]+/[^/\s]+/actions/runs/[1-9][0-9]*$"
)
DIGEST_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
INTEGRITY_SHA512_RE = re.compile(r"^sha512-[A-Za-z0-9+/]+={0,2}$")
RFC3339_DATE_TIME_RE = re.compile(
    r"^(?P<date>[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01]))"
    r"[Tt](?:[01][0-9]|2[0-3]):[0-5][0-9]:(?:[0-5][0-9]|60)"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
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
EXPECTED_TAG_ONLY_COMPLETION = {
    "jobPermissions": {
        "admissionAndLiveVerification": [
            "contents: read",
            "actions: read",
            "pull-requests: read",
            "packages: read",
        ],
        "retainedArtifactRetrieval": ["actions: read"],
        "registryMutation": ["packages: write"],
        "postPublicationVerification": [
            "contents: read",
            "packages: read",
        ],
    },
    "publicationEffects": {
        "allowed": ["registry-package-publication"],
        "forbidden": [
            "package-tag-creation",
            "branch-push",
            "source-commit",
            "service-deployment",
            "application-deployment",
            "oci-publication",
            "object-storage-publication",
            "sibling-release-unit-mutation",
        ],
    },
    "stateOutcomes": {
        "exactTagRegistryAbsent": "publish-eligible",
        "exactPair": "verification-only",
        "tagMissingMovedOrConflicting": "fail-closed",
        "registryOnlyMismatchedOrAmbiguous": "fail-closed",
    },
}
EXPECTED_COMPLETION_PERMISSION_PREFLIGHT = {
    "jobPermissions": [
        "contents: read",
        "actions: read",
        "pull-requests: read",
        "packages: read",
    ],
    "endpointPermissions": [
        {"endpoint": "actions-run-metadata", "permission": "actions: read"},
        {"endpoint": "actions-job-metadata", "permission": "actions: read"},
        {"endpoint": "actions-artifact-metadata", "permission": "actions: read"},
        {
            "endpoint": "completion-workflow-run-history",
            "permission": "actions: read",
        },
        {
            "endpoint": "commit-associated-pull-requests",
            "permission": "pull-requests: read",
        },
        {"endpoint": "git-tag-ref", "permission": "contents: read"},
        {
            "endpoint": "registry-version-and-dist-tag",
            "permission": "packages: read",
        },
    ],
    "credentials": {
        "allowed": ["github-token"],
        "forbidden": ["tag-app-credential", "registry-write-credential"],
    },
    "publicationEffects": {
        "allowed": [],
        "forbidden": [
            "registry-package-publication",
            "package-tag-creation",
            "branch-push",
            "source-commit",
            "artifact-creation",
            "service-deployment",
            "application-deployment",
            "oci-publication",
            "object-storage-publication",
            "sibling-release-unit-mutation",
        ],
    },
}
EXPECTED_TAG_ONLY_COMPLETION_RECOVERY = {
    "jobPermissions": EXPECTED_TAG_ONLY_COMPLETION["jobPermissions"],
    "publicationEffects": EXPECTED_TAG_ONLY_COMPLETION["publicationEffects"],
    "stateOutcomes": EXPECTED_TAG_ONLY_COMPLETION["stateOutcomes"],
}
REGULAR_FILE_MODES = {"100644", "100755"}


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
    require(not text.startswith(":"), f"{label} must not use Git pathspec magic")
    require(
        not any(ord(character) < 32 or ord(character) == 127 for character in text),
        f"{label} must not contain control characters",
    )
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
    require(WORKFLOW_RE.fullmatch(path) is not None, f"{label} must name a top-level repository workflow")
    return path


def validate_rfc3339_date_time(value: Any, label: str) -> str:
    text = require_string(value, label)
    match = RFC3339_DATE_TIME_RE.fullmatch(text)
    require(match is not None, f"{label} must be an RFC 3339 date-time")
    try:
        dt.date.fromisoformat(match.group("date"))
    except ValueError:
        reject(f"{label} must be an RFC 3339 date-time")
    return text


def validate_contract(document: Any) -> dict[str, Any]:
    contract = require_object(document, "profile contract")
    required = {
        "schemaVersion",
        "profile",
        "source",
        "intentDirectory",
        "recovery",
        "tagOnlyCompletion",
        "tagOnlyCompletionRecovery",
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

    recovery = require_object(contract["recovery"], "recovery")
    require_exact_keys(recovery, {"intentDirectory", "workflow"}, "recovery")
    recovery["intentDirectory"] = validate_relative(
        recovery["intentDirectory"], "recovery.intentDirectory"
    )
    recovery["workflow"] = validate_workflow(recovery["workflow"], "recovery.workflow")
    require(
        recovery["intentDirectory"] != contract["intentDirectory"]
        and not recovery["intentDirectory"].startswith(f"{contract['intentDirectory']}/")
        and not contract["intentDirectory"].startswith(f"{recovery['intentDirectory']}/"),
        "release and recovery intent directories must be distinct and non-overlapping",
    )

    completion = require_object(contract["tagOnlyCompletion"], "tagOnlyCompletion")
    require_exact_keys(
        completion,
        {
            "intentDirectory",
            "workflow",
            "jobPermissions",
            "publicationEffects",
            "stateOutcomes",
        },
        "tagOnlyCompletion",
    )
    completion["intentDirectory"] = validate_relative(
        completion["intentDirectory"], "tagOnlyCompletion.intentDirectory"
    )
    completion["workflow"] = validate_workflow(
        completion["workflow"], "tagOnlyCompletion.workflow"
    )
    for label, other_directory in (
        ("release", contract["intentDirectory"]),
        ("recovery", recovery["intentDirectory"]),
    ):
        require(
            completion["intentDirectory"] != other_directory
            and not completion["intentDirectory"].startswith(f"{other_directory}/")
            and not other_directory.startswith(f"{completion['intentDirectory']}/"),
            f"tag-only completion and {label} intent directories must be distinct and non-overlapping",
        )
    require(
        {
            "jobPermissions": completion["jobPermissions"],
            "publicationEffects": completion["publicationEffects"],
            "stateOutcomes": completion["stateOutcomes"],
        }
        == EXPECTED_TAG_ONLY_COMPLETION,
        "tagOnlyCompletion must preserve exact job-scoped permissions and registry-only effects",
    )

    completion_recovery = require_object(
        contract["tagOnlyCompletionRecovery"], "tagOnlyCompletionRecovery"
    )
    require_exact_keys(
        completion_recovery,
        {
            "intentDirectory",
            "workflow",
            "jobPermissions",
            "permissionPreflight",
            "publicationEffects",
            "stateOutcomes",
        },
        "tagOnlyCompletionRecovery",
    )
    completion_recovery["intentDirectory"] = validate_relative(
        completion_recovery["intentDirectory"],
        "tagOnlyCompletionRecovery.intentDirectory",
    )
    completion_recovery["workflow"] = validate_workflow(
        completion_recovery["workflow"], "tagOnlyCompletionRecovery.workflow"
    )
    for label, other_directory in (
        ("release", contract["intentDirectory"]),
        ("recovery", recovery["intentDirectory"]),
        ("tag-only completion", completion["intentDirectory"]),
    ):
        require(
            completion_recovery["intentDirectory"] != other_directory
            and not completion_recovery["intentDirectory"].startswith(
                f"{other_directory}/"
            )
            and not other_directory.startswith(
                f"{completion_recovery['intentDirectory']}/"
            ),
            f"tag-only completion recovery and {label} intent directories must be distinct and non-overlapping",
        )
    require(
        {
            "jobPermissions": completion_recovery["jobPermissions"],
            "publicationEffects": completion_recovery["publicationEffects"],
            "stateOutcomes": completion_recovery["stateOutcomes"],
        }
        == EXPECTED_TAG_ONLY_COMPLETION_RECOVERY,
        "tagOnlyCompletionRecovery must preserve exact job-scoped permissions, state outcomes, and registry-only effects",
    )
    preflight = require_object(
        completion_recovery["permissionPreflight"],
        "tagOnlyCompletionRecovery.permissionPreflight",
    )
    require_exact_keys(
        preflight,
        {
            "workflow",
            "jobPermissions",
            "endpointPermissions",
            "credentials",
            "publicationEffects",
        },
        "tagOnlyCompletionRecovery.permissionPreflight",
    )
    preflight["workflow"] = validate_workflow(
        preflight["workflow"],
        "tagOnlyCompletionRecovery.permissionPreflight.workflow",
    )
    require(
        {
            key: preflight[key]
            for key in (
                "jobPermissions",
                "credentials",
                "publicationEffects",
            )
        }
        == {
            key: EXPECTED_COMPLETION_PERMISSION_PREFLIGHT[key]
            for key in (
                "jobPermissions",
                "credentials",
                "publicationEffects",
            )
        },
        "completion permission preflight must preserve the exact read-only permissions and zero-mutation boundary",
    )
    endpoint_permissions = preflight["endpointPermissions"]
    require(
        isinstance(endpoint_permissions, list) and bool(endpoint_permissions),
        "completion permission preflight endpoint inventory must be a non-empty array",
    )
    endpoint_names: set[str] = set()
    allowed_preflight_permissions = set(preflight["jobPermissions"])
    for index, raw_endpoint in enumerate(endpoint_permissions):
        endpoint = require_object(
            raw_endpoint,
            f"tagOnlyCompletionRecovery.permissionPreflight.endpointPermissions[{index}]",
        )
        require_exact_keys(
            endpoint,
            {"endpoint", "permission"},
            f"tagOnlyCompletionRecovery.permissionPreflight.endpointPermissions[{index}]",
        )
        endpoint_name = require_string(
            endpoint["endpoint"],
            f"tagOnlyCompletionRecovery.permissionPreflight.endpointPermissions[{index}].endpoint",
        )
        require(
            len(endpoint_name) <= 128 and ID_RE.fullmatch(endpoint_name) is not None,
            "completion permission preflight endpoint names must be lowercase kebab-case",
        )
        require(
            endpoint_name not in endpoint_names,
            "completion permission preflight endpoint inventory must not contain duplicates",
        )
        endpoint_names.add(endpoint_name)
        require(
            endpoint["permission"] in allowed_preflight_permissions,
            "completion permission preflight endpoints may use only declared read permissions",
        )
    require(
        all(
            required_endpoint in endpoint_permissions
            for required_endpoint in EXPECTED_COMPLETION_PERMISSION_PREFLIGHT[
                "endpointPermissions"
            ]
        ),
        "completion permission preflight must include every required endpoint-to-permission mapping",
    )

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
    require(
        completion["workflow"]
        not in {
            unit["validationWorkflow"],
            unit["publicationWorkflow"],
            recovery["workflow"],
        },
        "tag-only completion workflow must be distinct from validation, publication, and recovery workflows",
    )
    require(
        completion_recovery["workflow"]
        not in {
            unit["validationWorkflow"],
            unit["publicationWorkflow"],
            recovery["workflow"],
            completion["workflow"],
        },
        "tag-only completion recovery workflow must be distinct from validation, publication, recovery, and completion workflows",
    )
    require(
        preflight["workflow"] == unit["validationWorkflow"],
        "completion permission preflight must run in the repository validation workflow",
    )
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
    recovery_probe = f"{recovery['intentDirectory']}/recovery.json"
    require(
        not any(path_matches(recovery_probe, pattern) for pattern in preparation),
        "releasePreparationPaths must not admit recovery authorization records",
    )
    completion_probe = f"{completion['intentDirectory']}/completion.json"
    require(
        not any(path_matches(completion_probe, pattern) for pattern in preparation),
        "releasePreparationPaths must not admit tag-only completion authorization records",
    )
    completion_recovery_probe = (
        f"{completion_recovery['intentDirectory']}/completion-recovery.json"
    )
    require(
        not any(
            path_matches(completion_recovery_probe, pattern)
            for pattern in preparation
        ),
        "releasePreparationPaths must not admit tag-only completion recovery authorization records",
    )
    reject_sibling_mutation(
        contract,
        {
            intent_probe,
            recovery_probe,
            completion_probe,
            completion_recovery_probe,
        },
    )
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


def validate_recovery_intent(
    document: Any, label: str = "release recovery intent"
) -> dict[str, Any]:
    intent = require_object(document, label)
    required = {
        "schemaVersion",
        "releaseUnit",
        "channel",
        "version",
        "originalIntentPath",
        "failedAttempt",
        "source",
        "reason",
    }
    require_exact_keys(intent, required, label, {"$schema"})
    if "$schema" in intent:
        require_string(intent["$schema"], f"{label}.$schema")
    require(
        intent["schemaVersion"] == "package-release-recovery-intent/v1",
        f"{label} has an unsupported schemaVersion",
    )
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

    intent["originalIntentPath"] = validate_relative(
        intent["originalIntentPath"], f"{label}.originalIntentPath"
    )
    require(
        intent["originalIntentPath"].endswith(".json"),
        f"{label}.originalIntentPath must name a JSON file",
    )

    failed = require_object(intent["failedAttempt"], f"{label}.failedAttempt")
    require_exact_keys(
        failed,
        {
            "sourceCommit",
            "workflowRunUrl",
            "outcome",
            "mutationState",
            "tagState",
            "registryVersionState",
        },
        f"{label}.failedAttempt",
    )
    require(
        isinstance(failed["sourceCommit"], str)
        and FULL_SHA_RE.fullmatch(failed["sourceCommit"]) is not None,
        f"{label}.failedAttempt.sourceCommit must be a lowercase full commit SHA",
    )
    run_url = require_string(failed["workflowRunUrl"], f"{label}.failedAttempt.workflowRunUrl")
    require(
        WORKFLOW_RUN_URL_RE.fullmatch(run_url) is not None,
        f"{label}.failedAttempt.workflowRunUrl must identify an exact GitHub Actions run",
    )
    require(failed["outcome"] == "terminal-failure", f"{label} requires a terminal failed attempt")
    require(
        failed["mutationState"] == "not-started",
        f"{label} requires failure before immutable mutation",
    )
    require(failed["tagState"] == "absent", f"{label} requires the package tag to be absent")
    require(
        failed["registryVersionState"] == "absent",
        f"{label} requires the registry version to be absent",
    )

    source = require_object(intent["source"], f"{label}.source")
    require_exact_keys(source, {"ref", "baseCommit"}, f"{label}.source")
    require(source["ref"] == "refs/heads/dev", f"{label}.source.ref must be refs/heads/dev")
    require(
        isinstance(source["baseCommit"], str)
        and FULL_SHA_RE.fullmatch(source["baseCommit"]) is not None,
        f"{label}.source.baseCommit must be a lowercase full commit SHA",
    )
    require(
        intent["reason"] == "pre-mutation-no-immutable-identity",
        f"{label}.reason must select pre-mutation no-identity recovery",
    )
    return intent


def validate_tag_only_completion_intent(
    document: Any, label: str = "tag-only completion intent"
) -> dict[str, Any]:
    intent = require_object(document, label)
    required = {
        "schemaVersion",
        "releaseUnit",
        "channel",
        "version",
        "originalIntentPath",
        "tag",
        "distTag",
        "failedPublication",
        "retainedArtifact",
        "source",
        "reason",
    }
    require_exact_keys(intent, required, label, {"$schema"})
    if "$schema" in intent:
        require_string(intent["$schema"], f"{label}.$schema")
    require(
        intent["schemaVersion"]
        == "package-release-tag-only-completion-intent/v1",
        f"{label} has an unsupported schemaVersion",
    )
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

    intent["originalIntentPath"] = validate_relative(
        intent["originalIntentPath"], f"{label}.originalIntentPath"
    )
    require(
        intent["originalIntentPath"].endswith(".json"),
        f"{label}.originalIntentPath must name a JSON file",
    )
    tag = require_string(intent["tag"], f"{label}.tag")
    require(
        len(tag) <= 200 and not any(character.isspace() for character in tag),
        f"{label}.tag must be a non-whitespace Git tag",
    )
    dist_tag = require_string(intent["distTag"], f"{label}.distTag")
    require(
        len(dist_tag) <= 128 and not any(character.isspace() for character in dist_tag),
        f"{label}.distTag must be a non-whitespace registry tag",
    )

    failed = require_object(intent["failedPublication"], f"{label}.failedPublication")
    require_exact_keys(
        failed,
        {
            "sourceCommit",
            "workflowRunUrl",
            "runAttempt",
            "outcome",
            "publicationState",
            "tagState",
            "registryVersionState",
            "authorization",
        },
        f"{label}.failedPublication",
    )
    require(
        isinstance(failed["sourceCommit"], str)
        and FULL_SHA_RE.fullmatch(failed["sourceCommit"]) is not None,
        f"{label}.failedPublication.sourceCommit must be a lowercase full commit SHA",
    )
    run_url = require_string(
        failed["workflowRunUrl"], f"{label}.failedPublication.workflowRunUrl"
    )
    require(
        WORKFLOW_RUN_URL_RE.fullmatch(run_url) is not None,
        f"{label}.failedPublication.workflowRunUrl must identify an exact GitHub Actions run",
    )
    require(
        isinstance(failed["runAttempt"], int)
        and not isinstance(failed["runAttempt"], bool)
        and failed["runAttempt"] == 1,
        f"{label} requires failed publication run attempt 1",
    )
    require(
        failed["outcome"] == "terminal-failure",
        f"{label} requires a terminal failed publication",
    )
    require(
        failed["publicationState"] == "tag-only",
        f"{label} requires tag-only partial publication",
    )
    require(failed["tagState"] == "present", f"{label} requires the package tag to be present")
    require(
        failed["registryVersionState"] == "absent",
        f"{label} requires the exact registry version to be absent",
    )
    authorization = require_object(
        failed["authorization"], f"{label}.failedPublication.authorization"
    )
    require_exact_keys(
        authorization,
        {"type", "path"},
        f"{label}.failedPublication.authorization",
    )
    require(
        authorization["type"] in {"release-intent", "pre-mutation-recovery"},
        f"{label}.failedPublication.authorization.type is invalid",
    )
    authorization["path"] = validate_relative(
        authorization["path"], f"{label}.failedPublication.authorization.path"
    )
    require(
        authorization["path"].endswith(".json"),
        f"{label}.failedPublication.authorization.path must name a JSON file",
    )

    artifact = require_object(intent["retainedArtifact"], f"{label}.retainedArtifact")
    require_exact_keys(
        artifact,
        {
            "artifactId",
            "artifactName",
            "expiresAt",
            "archiveDigest",
            "tarballFileName",
            "tarballSha256",
            "npmIntegrity",
            "embeddedSourceCommit",
        },
        f"{label}.retainedArtifact",
    )
    require(
        isinstance(artifact["artifactId"], int)
        and not isinstance(artifact["artifactId"], bool)
        and artifact["artifactId"] > 0,
        f"{label}.retainedArtifact.artifactId must be a positive integer",
    )
    artifact_name = require_string(
        artifact["artifactName"], f"{label}.retainedArtifact.artifactName"
    )
    require(
        len(artifact_name) <= 255
        and "/" not in artifact_name
        and "\\" not in artifact_name
        and not any(ord(character) < 32 or ord(character) == 127 for character in artifact_name),
        f"{label}.retainedArtifact.artifactName must be a plain file name",
    )
    validate_rfc3339_date_time(
        artifact["expiresAt"], f"{label}.retainedArtifact.expiresAt"
    )
    require(
        isinstance(artifact["archiveDigest"], str)
        and DIGEST_SHA256_RE.fullmatch(artifact["archiveDigest"]) is not None,
        f"{label}.retainedArtifact.archiveDigest must be sha256 plus 64 lowercase hex characters",
    )
    tarball_name = require_string(
        artifact["tarballFileName"], f"{label}.retainedArtifact.tarballFileName"
    )
    require(
        5 <= len(tarball_name) <= 255
        and tarball_name.endswith(".tgz")
        and "/" not in tarball_name
        and "\\" not in tarball_name
        and not any(ord(character) < 32 or ord(character) == 127 for character in tarball_name),
        f"{label}.retainedArtifact.tarballFileName must be a plain .tgz file name",
    )
    require(
        isinstance(artifact["tarballSha256"], str)
        and SHA256_RE.fullmatch(artifact["tarballSha256"]) is not None,
        f"{label}.retainedArtifact.tarballSha256 must be 64 lowercase hex characters",
    )
    integrity = require_string(
        artifact["npmIntegrity"], f"{label}.retainedArtifact.npmIntegrity"
    )
    require(
        INTEGRITY_SHA512_RE.fullmatch(integrity) is not None,
        f"{label}.retainedArtifact.npmIntegrity must be an npm sha512 integrity",
    )
    try:
        integrity_bytes = base64.b64decode(integrity.removeprefix("sha512-"), validate=True)
    except (binascii.Error, ValueError):
        reject(f"{label}.retainedArtifact.npmIntegrity must contain valid base64")
    require(
        len(integrity_bytes) == 64,
        f"{label}.retainedArtifact.npmIntegrity must encode a SHA-512 digest",
    )
    require(
        isinstance(artifact["embeddedSourceCommit"], str)
        and FULL_SHA_RE.fullmatch(artifact["embeddedSourceCommit"]) is not None,
        f"{label}.retainedArtifact.embeddedSourceCommit must be a lowercase full commit SHA",
    )

    source = require_object(intent["source"], f"{label}.source")
    require_exact_keys(source, {"ref", "baseCommit"}, f"{label}.source")
    require(source["ref"] == "refs/heads/dev", f"{label}.source.ref must be refs/heads/dev")
    require(
        isinstance(source["baseCommit"], str)
        and FULL_SHA_RE.fullmatch(source["baseCommit"]) is not None,
        f"{label}.source.baseCommit must be a lowercase full commit SHA",
    )
    require(
        intent["reason"] == "tag-only-partial-publication",
        f"{label}.reason must select tag-only partial publication",
    )
    return intent


def validate_tag_only_completion_recovery_intent(
    document: Any, label: str = "tag-only completion recovery intent"
) -> dict[str, Any]:
    intent = require_object(document, label)
    required = {
        "schemaVersion",
        "releaseUnit",
        "channel",
        "version",
        "originalIntentPath",
        "tag",
        "distTag",
        "originalPublication",
        "originalCompletionIntent",
        "failedCompletion",
        "retainedArtifact",
        "source",
        "reason",
    }
    require_exact_keys(intent, required, label, {"$schema"})
    if "$schema" in intent:
        require_string(intent["$schema"], f"{label}.$schema")
    require(
        intent["schemaVersion"]
        == "package-release-tag-only-completion-recovery-intent/v1",
        f"{label} has an unsupported schemaVersion",
    )

    shared = validate_tag_only_completion_intent(
        {
            "schemaVersion": "package-release-tag-only-completion-intent/v1",
            "releaseUnit": intent["releaseUnit"],
            "channel": intent["channel"],
            "version": intent["version"],
            "originalIntentPath": intent["originalIntentPath"],
            "tag": intent["tag"],
            "distTag": intent["distTag"],
            "failedPublication": intent["originalPublication"],
            "retainedArtifact": intent["retainedArtifact"],
            "source": intent["source"],
            "reason": "tag-only-partial-publication",
        },
        f"{label} shared completion identity",
    )
    for key in (
        "releaseUnit",
        "channel",
        "version",
        "originalIntentPath",
        "tag",
        "distTag",
        "retainedArtifact",
        "source",
    ):
        intent[key] = shared[key]
    intent["originalPublication"] = shared["failedPublication"]

    original_completion = require_object(
        intent["originalCompletionIntent"], f"{label}.originalCompletionIntent"
    )
    require_exact_keys(
        original_completion,
        {"path", "sha256"},
        f"{label}.originalCompletionIntent",
    )
    original_completion["path"] = validate_relative(
        original_completion["path"], f"{label}.originalCompletionIntent.path"
    )
    require(
        original_completion["path"].endswith(".json"),
        f"{label}.originalCompletionIntent.path must name a JSON file",
    )
    require(
        isinstance(original_completion["sha256"], str)
        and SHA256_RE.fullmatch(original_completion["sha256"]) is not None,
        f"{label}.originalCompletionIntent.sha256 must be 64 lowercase hex characters",
    )

    failed = require_object(intent["failedCompletion"], f"{label}.failedCompletion")
    require_exact_keys(
        failed,
        {
            "sourceCommit",
            "workflowRunUrl",
            "runAttempt",
            "outcome",
            "failurePhase",
            "retainedArtifactRetrievalState",
            "registryMutationState",
            "postPublicationVerificationState",
            "tagState",
            "registryVersionState",
            "authorization",
        },
        f"{label}.failedCompletion",
    )
    require(
        isinstance(failed["sourceCommit"], str)
        and FULL_SHA_RE.fullmatch(failed["sourceCommit"]) is not None,
        f"{label}.failedCompletion.sourceCommit must be a lowercase full commit SHA",
    )
    run_url = require_string(
        failed["workflowRunUrl"], f"{label}.failedCompletion.workflowRunUrl"
    )
    require(
        WORKFLOW_RUN_URL_RE.fullmatch(run_url) is not None,
        f"{label}.failedCompletion.workflowRunUrl must identify an exact GitHub Actions run",
    )
    require(
        isinstance(failed["runAttempt"], int)
        and not isinstance(failed["runAttempt"], bool)
        and failed["runAttempt"] == 1,
        f"{label} requires failed completion run attempt 1",
    )
    require(
        failed["outcome"] == "terminal-failure",
        f"{label} requires a terminal failed completion",
    )
    require(
        failed["failurePhase"] == "admission-live-verification",
        f"{label} requires failure during admission/live verification",
    )
    for state_field in (
        "retainedArtifactRetrievalState",
        "registryMutationState",
        "postPublicationVerificationState",
    ):
        require(
            failed[state_field] == "not-started",
            f"{label} requires {state_field} to remain not-started",
        )
    require(
        failed["tagState"] == "present",
        f"{label} requires the immutable package tag to remain present",
    )
    require(
        failed["registryVersionState"] == "absent",
        f"{label} requires the exact registry version to remain absent",
    )
    authorization = require_object(
        failed["authorization"], f"{label}.failedCompletion.authorization"
    )
    require_exact_keys(
        authorization,
        {"type", "path"},
        f"{label}.failedCompletion.authorization",
    )
    require(
        authorization["type"]
        in {"tag-only-completion", "tag-only-completion-recovery"},
        f"{label}.failedCompletion.authorization.type is invalid",
    )
    authorization["path"] = validate_relative(
        authorization["path"], f"{label}.failedCompletion.authorization.path"
    )
    require(
        authorization["path"].endswith(".json"),
        f"{label}.failedCompletion.authorization.path must name a JSON file",
    )
    require(
        intent["reason"] == "pre-mutation-tag-only-completion-failure",
        f"{label}.reason must select pre-mutation tag-only completion failure",
    )
    return intent


def compare_semver_precedence(left: str, right: str) -> int:
    left_match = SEMVER_RE.fullmatch(left)
    right_match = SEMVER_RE.fullmatch(right)
    require(left_match is not None and right_match is not None, "cannot compare invalid SemVer")

    left_core = tuple(int(left_match.group(index)) for index in range(1, 4))
    right_core = tuple(int(right_match.group(index)) for index in range(1, 4))
    if left_core != right_core:
        return -1 if left_core < right_core else 1

    left_prerelease = left_match.group(4)
    right_prerelease = right_match.group(4)
    if left_prerelease is None or right_prerelease is None:
        if left_prerelease == right_prerelease:
            return 0
        return 1 if left_prerelease is None else -1

    left_identifiers = left_prerelease.split(".")
    right_identifiers = right_prerelease.split(".")
    for left_identifier, right_identifier in zip(left_identifiers, right_identifiers):
        if left_identifier == right_identifier:
            continue
        left_numeric = left_identifier.isdigit()
        right_numeric = right_identifier.isdigit()
        if left_numeric and right_numeric:
            return -1 if int(left_identifier) < int(right_identifier) else 1
        if left_numeric != right_numeric:
            return -1 if left_numeric else 1
        return -1 if left_identifier < right_identifier else 1
    if len(left_identifiers) == len(right_identifiers):
        return 0
    return -1 if len(left_identifiers) < len(right_identifiers) else 1


def path_matches(path: str, pattern: str) -> bool:
    path_parts = PurePosixPath(path).parts
    pattern_parts = PurePosixPath(pattern).parts

    @lru_cache(maxsize=None)
    def match(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        segment = pattern_parts[pattern_index]
        if segment == "**":
            return match(path_index, pattern_index + 1) or (
                path_index < len(path_parts) and match(path_index + 1, pattern_index)
            )
        return (
            path_index < len(path_parts)
            and fnmatch.fnmatchcase(path_parts[path_index], segment)
            and match(path_index + 1, pattern_index + 1)
        )

    return match(0, 0)


def is_below(path: str, directory: str) -> bool:
    return path.startswith(f"{directory}/")


def reject_sibling_mutation(contract: dict[str, Any], paths: set[str]) -> None:
    for sibling in contract["siblingReleaseUnits"]:
        for path in sorted(paths):
            if any(
                path_matches(path, pattern)
                for pattern in sibling["mutationPaths"]
            ):
                reject(
                    f"sibling release-unit mutation is forbidden: {sibling['id']} changed {path}"
                )


def git(repo: Path, *args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        reject(f"git {' '.join(args)} failed: {detail}")
    if binary:
        return result.stdout
    return result.stdout.decode("utf-8")


def git_json(repo: Path, revision: str, path: str, label: str) -> Any:
    raw = git(repo, "show", f"{revision}:{path}", binary=True)

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        document: dict[str, Any] = {}
        for key, value in pairs:
            if key in document:
                raise ValueError(f"duplicate object key: {key}")
            document[key] = value
        return document

    def reject_constant(value: str) -> NoReturn:
        raise ValueError(f"non-standard numeric constant: {value}")

    try:
        text = raw.decode("utf-8")
        return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
        reject(f"{label} is not valid UTF-8 JSON: {error}")


def git_toml(repo: Path, revision: str, path: str, label: str) -> Any:
    raw = git(repo, "show", f"{revision}:{path}", binary=True)
    try:
        return tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
        reject(f"{label} is not valid UTF-8 TOML: {error}")


def git_file_mode(repo: Path, revision: str, path: str, label: str) -> str:
    raw = git(repo, "ls-tree", "-z", revision, "--", f":(literal){path}", binary=True)
    records = [record for record in raw.split(b"\0") if record]
    require(len(records) == 1, f"{label} is missing or ambiguous at {revision}: {path}")
    try:
        metadata, encoded_path = records[0].split(b"\t", 1)
        mode, object_type, _object_id = metadata.decode("ascii").split(" ", 2)
        actual_path = encoded_path.decode("utf-8")
    except (UnicodeDecodeError, ValueError) as error:
        reject(f"{label} has invalid Git tree metadata at {revision}: {error}")
    require(actual_path == path, f"{label} resolved to an unexpected path at {revision}: {actual_path}")
    require(object_type == "blob", f"{label} must be a Git blob at {revision}: {path}")
    return mode


def require_regular_file(repo: Path, revision: str, path: str, label: str) -> None:
    mode = git_file_mode(repo, revision, path, label)
    require(mode in REGULAR_FILE_MODES, f"{label} must be a regular file at {revision}: {path} ({mode})")


def parse_diff(repo: Path, base: str, head: str) -> list[DiffEntry]:
    raw = git(
        repo,
        "diff",
        "--name-status",
        "-z",
        "--find-renames",
        "--find-copies=100%",
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
        try:
            status = parts[index].decode("ascii", errors="strict")
        except UnicodeDecodeError as error:
            reject(f"git diff produced an invalid status: {error}")
        index += 1
        path_count = 2 if status.startswith(("R", "C")) else 1
        require(index + path_count <= len(parts), "git diff produced an incomplete name-status record")
        try:
            paths = tuple(parts[index + offset].decode("utf-8") for offset in range(path_count))
        except UnicodeDecodeError as error:
            reject(f"git diff path is not UTF-8: {error}")
        index += path_count
        entries.append(DiffEntry(status=status, paths=paths))
    return entries


def git_commit_list(repo: Path, *args: str, label: str) -> list[str]:
    commits = [line for line in git(repo, "rev-list", *args).splitlines() if line]
    require(
        all(FULL_SHA_RE.fullmatch(commit) is not None for commit in commits),
        f"{label} contains an invalid commit identity",
    )
    require(len(commits) == len(set(commits)), f"{label} contains duplicate commits")
    return commits


def path_change_commits(
    repo: Path, head: str, path: str, label: str, *, start: str | None = None
) -> list[str]:
    revision = f"{start}..{head}" if start is not None else head
    return git_commit_list(
        repo,
        "--first-parent",
        "--full-history",
        revision,
        "--",
        f":(literal){path}",
        label=label,
    )


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


def tree_paths(repo: Path, revision: str, directory: str, label: str) -> list[str]:
    listed = git(
        repo,
        "ls-tree",
        "-r",
        "--name-only",
        "-z",
        revision,
        "--",
        f":(literal){directory}",
        binary=True,
    )
    try:
        return [part.decode("utf-8") for part in listed.split(b"\0") if part]
    except UnicodeDecodeError as error:
        reject(f"{label} contains a non-UTF-8 path: {error}")


def read_native_manifest(
    repo: Path, revision: str, unit: dict[str, Any], label: str
) -> tuple[Any, Any, Any]:
    version_source = unit["versionSource"]
    version_path = version_source["path"]
    require_regular_file(repo, revision, version_path, label)
    if version_source["type"] == "json-pointer":
        manifest = git_json(repo, revision, version_path, label)
        version = pointer_get(manifest, version_source["versionPointer"], label)
        package_name = pointer_get(manifest, version_source["packageNamePointer"], label)
    else:
        manifest = git_toml(repo, revision, version_path, label)
        version = dotted_get(manifest, version_source["versionKey"], label)
        package_name = dotted_get(manifest, version_source["packageNameKey"], label)
    return manifest, package_name, version


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=repo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def admit_release(
    repo: Path,
    contract_path: str,
    contract: dict[str, Any],
    base: str,
    head: str,
    event_ref: str,
    entries: list[DiffEntry],
) -> dict[str, Any]:
    unit = contract["releaseUnit"]
    require(bool(entries), "release admission diff is empty")
    changed_paths = {path for entry in entries for path in entry.paths}
    for path in changed_paths:
        validate_relative(path, "changed path", allow_glob=True)
    require(contract_path not in changed_paths, "profile contract must be established separately from release preparation")
    require(unit["validationWorkflow"] not in changed_paths, "validation workflow must be established separately from release preparation")
    require(unit["publicationWorkflow"] not in changed_paths, "publication workflow must be established separately from release preparation")
    require(
        contract["recovery"]["workflow"] not in changed_paths,
        "recovery workflow must be established separately from release preparation",
    )
    require(
        not any(
            is_below(path, contract["recovery"]["intentDirectory"])
            for path in changed_paths
        ),
        "release preparation cannot contain a recovery authorization",
    )
    require(
        not any(
            is_below(path, contract["tagOnlyCompletion"]["intentDirectory"])
            for path in changed_paths
        ),
        "release preparation cannot contain a tag-only completion authorization",
    )

    for entry in entries:
        require(
            entry.status in {"A", "M"},
            f"release preparation may only add or modify files: {entry.status} {' -> '.join(entry.paths)}",
        )
        require_regular_file(repo, head, entry.paths[0], "release-preparation path")
    reject_sibling_mutation(contract, changed_paths)
    for path in sorted(changed_paths):
        require(
            any(path_matches(path, pattern) for pattern in unit["releasePreparationPaths"]),
            f"changed path is outside release preparation: {path}",
        )

    intent_entries = [
        entry
        for entry in entries
        if any(is_below(path, contract["intentDirectory"]) for path in entry.paths)
    ]
    require(len(intent_entries) == 1, "exactly one release intent change is required")
    intent_entry = intent_entries[0]
    require(intent_entry.status == "A" and len(intent_entry.paths) == 1, "release intent must be newly added; modification, rename, copy, or deletion is stale")
    intent_path = intent_entry.paths[0]
    require(PurePosixPath(intent_path).parent == PurePosixPath(contract["intentDirectory"]), "release intent must be directly inside intentDirectory")
    require(intent_path.endswith(".json"), "release intent must be a JSON file")
    require_regular_file(repo, head, intent_path, "release intent")
    intent = validate_intent(git_json(repo, head, intent_path, intent_path), intent_path)
    require(intent["releaseUnit"] == unit["id"], "release intent targets a different release unit")
    require(intent["source"]["ref"] == event_ref, "release intent source ref does not match the event ref")
    require(intent["source"]["baseCommit"] == base, "release intent is stale: source baseCommit does not equal the event before commit")

    intent_paths = tree_paths(repo, head, contract["intentDirectory"], "intent directory")
    matching_identity: list[str] = []
    for historical_path in intent_paths:
        validate_relative(historical_path, "historical release intent path", allow_glob=True)
        require_regular_file(repo, head, historical_path, "historical release intent")
        historical = validate_intent(git_json(repo, head, historical_path, historical_path), historical_path)
        if historical["releaseUnit"] == intent["releaseUnit"] and historical["version"] == intent["version"]:
            matching_identity.append(historical_path)
    require(matching_identity == [intent_path], "duplicate or conflicting release intent exists for the same release-unit and version")

    version_source = unit["versionSource"]
    version_path = version_source["path"]
    version_entries = [entry for entry in entries if version_path in entry.paths]
    require(len(version_entries) == 1 and version_entries[0].status == "M", "version source must be modified exactly once")
    require_regular_file(repo, base, version_path, "base version source")
    require_regular_file(repo, head, version_path, "head version source")
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
    require(
        compare_semver_precedence(head_version, base_version) > 0,
        "head manifest version must have greater SemVer precedence than the base version",
    )
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
    return {
        "schemaVersion": "protected-package-tag-admission/v1",
        "status": "admitted",
        "releaseUnit": unit["id"],
        "packageName": unit["packageName"],
        "registry": unit["registry"],
        "channel": channel,
        "distTag": contract["channels"][channel]["distTag"],
        "version": head_version,
        "tag": rendered_tag,
        "intentPath": intent_path,
        "source": {"ref": event_ref, "baseCommit": base, "commit": head},
    }


def validate_initial_publication_source(
    repo: Path,
    contract_path: str,
    contract: dict[str, Any],
    original: dict[str, Any],
    original_path: str,
    failed_source: str,
    event_ref: str,
) -> None:
    """Prove a claimed first failed source could pass normal exact-diff admission."""
    intent_additions = path_change_commits(
        repo,
        failed_source,
        original_path,
        "initial release intent history",
    )
    require(
        intent_additions == [failed_source],
        "failed publication source must be the exact commit that added the original release intent",
    )
    original_base = original["source"]["baseCommit"]
    entries = parse_diff(repo, original_base, failed_source)
    admitted = admit_release(
        repo,
        contract_path,
        contract,
        original_base,
        failed_source,
        event_ref,
        entries,
    )
    require(
        admitted["intentPath"] == original_path
        and admitted["version"] == original["version"],
        "initial failed publication source does not match the original release intent",
    )


def admit_recovery(
    repo: Path,
    contract_path: str,
    contract: dict[str, Any],
    base: str,
    head: str,
    event_ref: str,
    entries: list[DiffEntry],
) -> dict[str, Any]:
    recovery = contract["recovery"]
    unit = contract["releaseUnit"]
    require(
        len(entries) == 1,
        "recovery authorization diff must add exactly one recovery record and no other paths",
    )
    entry = entries[0]
    require(
        entry.status == "A" and len(entry.paths) == 1,
        "recovery authorization must be newly added; modification, rename, copy, or deletion is reuse",
    )
    recovery_path = entry.paths[0]
    require(
        PurePosixPath(recovery_path).parent == PurePosixPath(recovery["intentDirectory"]),
        "recovery authorization must be directly inside recovery.intentDirectory",
    )
    require(recovery_path.endswith(".json"), "recovery authorization must be a JSON file")
    reject_sibling_mutation(contract, {recovery_path})
    require_regular_file(repo, head, recovery_path, "release recovery intent")
    authorization = validate_recovery_intent(
        git_json(repo, head, recovery_path, recovery_path), recovery_path
    )
    require(
        authorization["releaseUnit"] == unit["id"],
        "release recovery intent targets a different release unit",
    )
    require(
        authorization["source"]["ref"] == event_ref,
        "release recovery intent source ref does not match the event ref",
    )
    require(
        authorization["source"]["baseCommit"] == base,
        "release recovery intent is stale: source baseCommit does not equal the event before commit",
    )

    original_path = authorization["originalIntentPath"]
    require(
        PurePosixPath(original_path).parent == PurePosixPath(contract["intentDirectory"]),
        "original release intent must be directly inside intentDirectory",
    )
    require_regular_file(repo, head, original_path, "original release intent")
    original = validate_intent(git_json(repo, head, original_path, original_path), original_path)
    require(original["releaseUnit"] == authorization["releaseUnit"], "original release intent release unit does not match recovery")
    require(original["channel"] == authorization["channel"], "original release intent channel does not match recovery")
    require(original["version"] == authorization["version"], "original release intent version does not match recovery")

    intent_paths = tree_paths(repo, head, contract["intentDirectory"], "intent directory")
    matching_originals: list[str] = []
    for historical_path in intent_paths:
        validate_relative(historical_path, "historical release intent path", allow_glob=True)
        require_regular_file(repo, head, historical_path, "historical release intent")
        historical = validate_intent(
            git_json(repo, head, historical_path, historical_path), historical_path
        )
        if (
            historical["releaseUnit"] == authorization["releaseUnit"]
            and historical["version"] == authorization["version"]
        ):
            matching_originals.append(historical_path)
    require(
        matching_originals == [original_path],
        "original release intent is missing or ambiguous for the recovery identity",
    )

    failed_source = authorization["failedAttempt"]["sourceCommit"]
    require(
        git(repo, "rev-parse", "--verify", f"{failed_source}^{{commit}}").strip()
        == failed_source,
        "failed attempt source does not resolve to the exact commit",
    )
    require(
        is_ancestor(repo, failed_source, base),
        "failed attempt source must be an ancestor of the recovery base",
    )
    protected_source_history = git_commit_list(
        repo, "--first-parent", head, label="protected source first-parent history"
    )
    require(
        failed_source in protected_source_history,
        "failed attempt source must be on the protected source first-parent history",
    )
    require_regular_file(repo, failed_source, original_path, "failed-source original release intent")
    failed_original_bytes = git(repo, "show", f"{failed_source}:{original_path}", binary=True)
    current_original_bytes = git(repo, "show", f"{head}:{original_path}", binary=True)
    require(
        failed_original_bytes == current_original_bytes,
        "original release intent must remain byte-identical after the failed attempt",
    )
    require(
        not path_change_commits(
            repo,
            head,
            original_path,
            "original release intent history",
            start=failed_source,
        ),
        "original release intent must remain append-only in protected source history",
    )
    original_base = original["source"]["baseCommit"]
    require(
        is_ancestor(repo, original_base, failed_source),
        "original release intent base must be an ancestor of the failed attempt source",
    )
    original_entries = parse_diff(repo, original_base, failed_source)
    require(
        any(
            historical_entry.status == "A"
            and historical_entry.paths == (original_path,)
            for historical_entry in original_entries
        ),
        "original release intent was not newly added for the failed publication source",
    )

    recovery_paths = tree_paths(
        repo, head, recovery["intentDirectory"], "recovery intent directory"
    )
    matching_failed_sources: list[str] = []
    historical_recoveries: list[tuple[str, dict[str, Any]]] = []
    for historical_path in recovery_paths:
        validate_relative(historical_path, "historical recovery intent path", allow_glob=True)
        require(
            PurePosixPath(historical_path).parent
            == PurePosixPath(recovery["intentDirectory"])
            and historical_path.endswith(".json"),
            "recovery intent directory may contain only direct JSON recovery records",
        )
        require_regular_file(repo, head, historical_path, "historical recovery intent")
        historical = validate_recovery_intent(
            git_json(repo, head, historical_path, historical_path), historical_path
        )
        historical_recoveries.append((historical_path, historical))
        if historical["failedAttempt"]["sourceCommit"] == failed_source:
            matching_failed_sources.append(historical_path)
    require(
        matching_failed_sources == [recovery_path],
        "duplicate recovery authorization exists for the same failed publication source",
    )
    recovery_history = path_change_commits(
        repo,
        head,
        recovery["intentDirectory"],
        "recovery intent directory history",
    )
    require(
        len(recovery_history) == len(recovery_paths),
        "recovery intent directory must remain append-only in protected source history",
    )
    for historical_path in recovery_paths:
        require(
            len(
                path_change_commits(
                    repo,
                    head,
                    historical_path,
                    f"historical recovery intent history: {historical_path}",
                )
            )
            == 1,
            f"historical recovery intent must be added once and never modified, renamed, or deleted: {historical_path}",
        )

    prior_recoveries = [
        (historical_path, historical)
        for historical_path, historical in historical_recoveries
        if historical_path != recovery_path
        and historical["releaseUnit"] == authorization["releaseUnit"]
        and historical["channel"] == authorization["channel"]
        and historical["version"] == authorization["version"]
        and historical["originalIntentPath"] == original_path
    ]
    if prior_recoveries:
        history_positions = {
            commit: index for index, commit in enumerate(protected_source_history)
        }
        prior_additions: list[tuple[int, str, dict[str, Any]]] = []
        for historical_path, historical in prior_recoveries:
            addition_commits = path_change_commits(
                repo,
                head,
                historical_path,
                f"historical recovery intent history: {historical_path}",
            )
            require(
                len(addition_commits) == 1
                and addition_commits[0] in history_positions,
                "historical recovery intent addition must be on protected source first-parent history",
            )
            prior_additions.append(
                (history_positions[addition_commits[0]], historical_path, historical)
            )
        _position, latest_path, latest_recovery = min(prior_additions)
        latest_base = latest_recovery["source"]["baseCommit"]
        require(
            is_ancestor(repo, latest_base, failed_source),
            "failed attempt source must descend from the latest recovery base",
        )
        latest_entries = parse_diff(repo, latest_base, failed_source)
        require(
            len(latest_entries) == 1
            and latest_entries[0].status == "A"
            and latest_entries[0].paths == (latest_path,),
            "failed attempt source must be the exact source authorized by the latest recovery record",
        )
    else:
        validate_initial_publication_source(
            repo,
            contract_path,
            contract,
            original,
            original_path,
            failed_source,
            event_ref,
        )

    base_manifest, base_package_name, base_version = read_native_manifest(
        repo, base, unit, "recovery base version source"
    )
    head_manifest, head_package_name, head_version = read_native_manifest(
        repo, head, unit, "recovery head version source"
    )
    require(base_manifest == head_manifest, "native manifest must remain unchanged during recovery authorization")
    require(base_package_name == head_package_name == unit["packageName"], "native manifest package name does not match releaseUnit.packageName")
    require(isinstance(base_version, str) and SEMVER_RE.fullmatch(base_version) is not None, "recovery base manifest version is not exact SemVer")
    require(base_version == head_version == authorization["version"], "recovery version does not match the unchanged native manifest")

    rendered_tag = unit["tagPattern"].replace("{version}", authorization["version"])
    tag_status = subprocess.run(
        ["git", "check-ref-format", f"refs/tags/{rendered_tag}"],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode
    require(tag_status == 0, "derived package tag is not a valid Git tag")

    channel = authorization["channel"]
    return {
        "schemaVersion": "protected-package-tag-recovery-admission/v1",
        "status": "admitted",
        "authorization": "pre-mutation-recovery",
        "releaseUnit": unit["id"],
        "packageName": unit["packageName"],
        "registry": unit["registry"],
        "channel": channel,
        "distTag": contract["channels"][channel]["distTag"],
        "version": authorization["version"],
        "tag": rendered_tag,
        "originalIntentPath": original_path,
        "recoveryIntentPath": recovery_path,
        "failedAttempt": authorization["failedAttempt"],
        "source": {
            "ref": event_ref,
            "baseCommit": base,
            "commit": head,
        },
    }


def admit_tag_only_completion(
    repo: Path,
    contract_path: str,
    contract: dict[str, Any],
    base: str,
    head: str,
    event_ref: str,
    entries: list[DiffEntry],
) -> dict[str, Any]:
    completion = contract["tagOnlyCompletion"]
    recovery = contract["recovery"]
    unit = contract["releaseUnit"]
    require(
        len(entries) == 1,
        "tag-only completion authorization diff must add exactly one record and no other paths",
    )
    entry = entries[0]
    require(
        entry.status == "A" and len(entry.paths) == 1,
        "tag-only completion authorization must be newly added; modification, rename, copy, or deletion is reuse",
    )
    completion_path = entry.paths[0]
    require(
        PurePosixPath(completion_path).parent
        == PurePosixPath(completion["intentDirectory"]),
        "tag-only completion authorization must be directly inside tagOnlyCompletion.intentDirectory",
    )
    require(
        completion_path.endswith(".json"),
        "tag-only completion authorization must be a JSON file",
    )
    reject_sibling_mutation(contract, {completion_path})
    require_regular_file(repo, head, completion_path, "tag-only completion intent")
    authorization = validate_tag_only_completion_intent(
        git_json(repo, head, completion_path, completion_path), completion_path
    )
    require(
        authorization["releaseUnit"] == unit["id"],
        "tag-only completion intent targets a different release unit",
    )
    require(
        authorization["source"]["ref"] == event_ref,
        "tag-only completion intent source ref does not match the event ref",
    )
    require(
        authorization["source"]["baseCommit"] == base,
        "tag-only completion intent is stale: source baseCommit does not equal the event before commit",
    )

    original_path = authorization["originalIntentPath"]
    require(
        PurePosixPath(original_path).parent == PurePosixPath(contract["intentDirectory"]),
        "original release intent must be directly inside intentDirectory",
    )
    require_regular_file(repo, head, original_path, "original release intent")
    original = validate_intent(
        git_json(repo, head, original_path, original_path), original_path
    )
    require(
        original["releaseUnit"] == authorization["releaseUnit"],
        "original release intent release unit does not match tag-only completion",
    )
    require(
        original["channel"] == authorization["channel"],
        "original release intent channel does not match tag-only completion",
    )
    require(
        original["version"] == authorization["version"],
        "original release intent version does not match tag-only completion",
    )

    intent_paths = tree_paths(repo, head, contract["intentDirectory"], "intent directory")
    matching_originals: list[str] = []
    for historical_path in intent_paths:
        validate_relative(historical_path, "historical release intent path", allow_glob=True)
        require_regular_file(repo, head, historical_path, "historical release intent")
        historical = validate_intent(
            git_json(repo, head, historical_path, historical_path), historical_path
        )
        if (
            historical["releaseUnit"] == authorization["releaseUnit"]
            and historical["version"] == authorization["version"]
        ):
            matching_originals.append(historical_path)
    require(
        matching_originals == [original_path],
        "original release intent is missing or ambiguous for the tag-only completion identity",
    )

    failed = authorization["failedPublication"]
    failed_source = failed["sourceCommit"]
    require(
        git(repo, "rev-parse", "--verify", f"{failed_source}^{{commit}}").strip()
        == failed_source,
        "failed publication source does not resolve to the exact commit",
    )
    require(
        is_ancestor(repo, failed_source, base),
        "failed publication source must be an ancestor of the completion base",
    )
    protected_source_history = git_commit_list(
        repo, "--first-parent", head, label="protected source first-parent history"
    )
    require(
        failed_source in protected_source_history,
        "failed publication source must be on the protected source first-parent history",
    )
    require_regular_file(
        repo, failed_source, original_path, "failed-publication original release intent"
    )
    require(
        git(repo, "show", f"{failed_source}:{original_path}", binary=True)
        == git(repo, "show", f"{head}:{original_path}", binary=True),
        "original release intent must remain byte-identical after the failed publication",
    )
    require(
        not path_change_commits(
            repo,
            head,
            original_path,
            "original release intent history",
            start=failed_source,
        ),
        "original release intent must remain append-only after the failed publication",
    )

    failed_authorization = failed["authorization"]
    failed_authorization_path = failed_authorization["path"]
    if failed_authorization["type"] == "release-intent":
        require(
            failed_authorization_path == original_path,
            "release-intent failed publication authorization must name originalIntentPath",
        )
        validate_initial_publication_source(
            repo,
            contract_path,
            contract,
            original,
            original_path,
            failed_source,
            event_ref,
        )
    else:
        require(
            PurePosixPath(failed_authorization_path).parent
            == PurePosixPath(recovery["intentDirectory"]),
            "pre-mutation recovery authorization must be directly inside recovery.intentDirectory",
        )
        require_regular_file(
            repo, failed_source, failed_authorization_path, "failed-publication recovery intent"
        )
        require_regular_file(
            repo, head, failed_authorization_path, "current recovery intent"
        )
        require(
            git(repo, "show", f"{failed_source}:{failed_authorization_path}", binary=True)
            == git(repo, "show", f"{head}:{failed_authorization_path}", binary=True),
            "failed publication recovery authorization must remain byte-identical",
        )
        require(
            not path_change_commits(
                repo,
                head,
                failed_authorization_path,
                "failed publication recovery authorization history",
                start=failed_source,
            ),
            "failed publication recovery authorization must remain append-only",
        )
        recovery_record = validate_recovery_intent(
            git_json(
                repo,
                failed_source,
                failed_authorization_path,
                failed_authorization_path,
            ),
            failed_authorization_path,
        )
        require(
            recovery_record["originalIntentPath"] == original_path
            and recovery_record["releaseUnit"] == authorization["releaseUnit"]
            and recovery_record["channel"] == authorization["channel"]
            and recovery_record["version"] == authorization["version"],
            "failed publication recovery authorization does not match the completion identity",
        )
        recovery_base = recovery_record["source"]["baseCommit"]
        admitted_recovery = admit_recovery(
            repo,
            contract_path,
            contract,
            recovery_base,
            failed_source,
            event_ref,
            parse_diff(repo, recovery_base, failed_source),
        )
        require(
            admitted_recovery["recoveryIntentPath"] == failed_authorization_path
            and admitted_recovery["source"]["commit"] == failed_source,
            "failed publication source is not the exact admitted recovery authorization",
        )

    matching_recoveries: list[tuple[int, str]] = []
    recovery_paths = tree_paths(
        repo, head, recovery["intentDirectory"], "recovery intent directory"
    )
    history_positions = {
        commit: index for index, commit in enumerate(protected_source_history)
    }
    for historical_path in recovery_paths:
        require_regular_file(repo, head, historical_path, "historical recovery intent")
        historical_recovery = validate_recovery_intent(
            git_json(repo, head, historical_path, historical_path), historical_path
        )
        if (
            historical_recovery["releaseUnit"] == authorization["releaseUnit"]
            and historical_recovery["channel"] == authorization["channel"]
            and historical_recovery["version"] == authorization["version"]
            and historical_recovery["originalIntentPath"] == original_path
        ):
            additions = path_change_commits(
                repo,
                head,
                historical_path,
                f"historical recovery intent history: {historical_path}",
            )
            require(
                len(additions) == 1 and additions[0] in history_positions,
                "historical recovery intent addition must be unique on protected source first-parent history",
            )
            matching_recoveries.append(
                (history_positions[additions[0]], historical_path)
            )
    if matching_recoveries:
        _position, latest_recovery_path = min(matching_recoveries)
        latest_addition = path_change_commits(
            repo,
            head,
            latest_recovery_path,
            f"latest recovery intent history: {latest_recovery_path}",
        )[0]
        require(
            failed_authorization["type"] == "pre-mutation-recovery"
            and failed_authorization_path == latest_recovery_path
            and failed_source == latest_addition,
            "failed publication source must be the exact source authorized by the latest recovery record",
        )
    else:
        require(
            failed_authorization["type"] == "release-intent",
            "release intent must be the failed publication authority when no recovery record exists",
        )

    base_manifest, base_package_name, base_version = read_native_manifest(
        repo, base, unit, "tag-only completion base version source"
    )
    head_manifest, head_package_name, head_version = read_native_manifest(
        repo, head, unit, "tag-only completion head version source"
    )
    require(
        base_manifest == head_manifest,
        "native manifest must remain unchanged during tag-only completion authorization",
    )
    require(
        base_package_name == head_package_name == unit["packageName"],
        "native manifest package name does not match releaseUnit.packageName",
    )
    require(
        isinstance(base_version, str) and SEMVER_RE.fullmatch(base_version) is not None,
        "tag-only completion base manifest version is not exact SemVer",
    )
    require(
        base_version == head_version == authorization["version"],
        "tag-only completion version does not match the unchanged native manifest",
    )

    rendered_tag = unit["tagPattern"].replace("{version}", authorization["version"])
    require(
        authorization["tag"] == rendered_tag,
        "tag-only completion tag does not match the derived package tag",
    )
    tag_status = subprocess.run(
        ["git", "check-ref-format", f"refs/tags/{rendered_tag}"],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode
    require(tag_status == 0, "derived package tag is not a valid Git tag")
    expected_dist_tag = contract["channels"][authorization["channel"]]["distTag"]
    require(
        authorization["distTag"] == expected_dist_tag,
        "tag-only completion dist-tag does not match the profile channel",
    )
    require(
        authorization["retainedArtifact"]["embeddedSourceCommit"] == failed_source,
        "retained artifact embedded source does not match the failed publication source",
    )

    completion_paths = tree_paths(
        repo, head, completion["intentDirectory"], "tag-only completion intent directory"
    )
    matching_identity: list[str] = []
    matching_failed_runs: list[str] = []
    for historical_path in completion_paths:
        validate_relative(
            historical_path, "historical tag-only completion path", allow_glob=True
        )
        require(
            PurePosixPath(historical_path).parent
            == PurePosixPath(completion["intentDirectory"])
            and historical_path.endswith(".json"),
            "tag-only completion directory may contain only direct JSON records",
        )
        require_regular_file(repo, head, historical_path, "historical tag-only completion intent")
        historical = validate_tag_only_completion_intent(
            git_json(repo, head, historical_path, historical_path), historical_path
        )
        if (
            historical["releaseUnit"] == authorization["releaseUnit"]
            and historical["version"] == authorization["version"]
        ):
            matching_identity.append(historical_path)
        if (
            historical["failedPublication"]["workflowRunUrl"]
            == failed["workflowRunUrl"]
        ):
            matching_failed_runs.append(historical_path)
    require(
        matching_identity == [completion_path],
        "duplicate tag-only completion authorization exists for the same release-unit and version",
    )
    require(
        matching_failed_runs == [completion_path],
        "duplicate tag-only completion authorization exists for the same failed publication run",
    )
    completion_history = path_change_commits(
        repo,
        head,
        completion["intentDirectory"],
        "tag-only completion intent directory history",
    )
    require(
        len(completion_history) == len(completion_paths),
        "tag-only completion intent directory must remain append-only in protected source history",
    )
    for historical_path in completion_paths:
        require(
            len(
                path_change_commits(
                    repo,
                    head,
                    historical_path,
                    f"historical tag-only completion intent history: {historical_path}",
                )
            )
            == 1,
            f"historical tag-only completion intent must be added once and never modified, renamed, or deleted: {historical_path}",
        )

    return {
        "schemaVersion": "protected-package-tag-tag-only-completion-admission/v1",
        "status": "admitted",
        "authorization": "tag-only-completion",
        "releaseUnit": unit["id"],
        "packageName": unit["packageName"],
        "registry": unit["registry"],
        "channel": authorization["channel"],
        "distTag": expected_dist_tag,
        "version": authorization["version"],
        "tag": rendered_tag,
        "originalIntentPath": original_path,
        "completionIntentPath": completion_path,
        "failedPublication": failed,
        "retainedArtifact": authorization["retainedArtifact"],
        "packageSource": {"commit": failed_source},
        "authorizationSource": {
            "ref": event_ref,
            "baseCommit": base,
            "commit": head,
        },
    }


def admit_tag_only_completion_recovery(
    repo: Path,
    contract_path: str,
    contract: dict[str, Any],
    base: str,
    head: str,
    event_ref: str,
    entries: list[DiffEntry],
) -> dict[str, Any]:
    completion = contract["tagOnlyCompletion"]
    recovery = contract["tagOnlyCompletionRecovery"]
    unit = contract["releaseUnit"]
    require(
        len(entries) == 1,
        "tag-only completion recovery authorization diff must add exactly one recovery record and no other paths",
    )
    entry = entries[0]
    require(
        entry.status == "A" and len(entry.paths) == 1,
        "tag-only completion recovery authorization must be newly added; modification, rename, copy, or deletion is reuse",
    )
    recovery_path = entry.paths[0]
    require(
        PurePosixPath(recovery_path).parent
        == PurePosixPath(recovery["intentDirectory"]),
        "tag-only completion recovery authorization must be directly inside tagOnlyCompletionRecovery.intentDirectory",
    )
    require(
        recovery_path.endswith(".json"),
        "tag-only completion recovery authorization must be a JSON file",
    )
    reject_sibling_mutation(contract, {recovery_path})
    require_regular_file(
        repo, head, recovery_path, "tag-only completion recovery intent"
    )
    authorization = validate_tag_only_completion_recovery_intent(
        git_json(repo, head, recovery_path, recovery_path), recovery_path
    )
    require(
        authorization["releaseUnit"] == unit["id"],
        "tag-only completion recovery intent targets a different release unit",
    )
    require(
        authorization["source"]["ref"] == event_ref,
        "tag-only completion recovery intent source ref does not match the event ref",
    )
    require(
        authorization["source"]["baseCommit"] == base,
        "tag-only completion recovery intent is stale: source baseCommit does not equal the event before commit",
    )

    original_completion_path = authorization["originalCompletionIntent"]["path"]
    require(
        PurePosixPath(original_completion_path).parent
        == PurePosixPath(completion["intentDirectory"]),
        "original tag-only completion intent must be directly inside tagOnlyCompletion.intentDirectory",
    )
    require_regular_file(
        repo, head, original_completion_path, "original tag-only completion intent"
    )
    original_completion_bytes = git(
        repo, "show", f"{head}:{original_completion_path}", binary=True
    )
    require(
        hashlib.sha256(original_completion_bytes).hexdigest()
        == authorization["originalCompletionIntent"]["sha256"],
        "original tag-only completion intent bytes do not match the bound SHA-256",
    )
    original_completion = validate_tag_only_completion_intent(
        git_json(
            repo,
            head,
            original_completion_path,
            original_completion_path,
        ),
        original_completion_path,
    )
    require(
        authorization["releaseUnit"] == original_completion["releaseUnit"]
        and authorization["channel"] == original_completion["channel"]
        and authorization["version"] == original_completion["version"]
        and authorization["originalIntentPath"]
        == original_completion["originalIntentPath"]
        and authorization["tag"] == original_completion["tag"]
        and authorization["distTag"] == original_completion["distTag"],
        "original tag-only completion intent does not match the recovery identity",
    )
    require(
        authorization["originalPublication"]
        == original_completion["failedPublication"],
        "original failed publication chain does not match the completion intent",
    )
    require(
        authorization["retainedArtifact"]
        == original_completion["retainedArtifact"],
        "retained artifact chain does not match the completion intent",
    )

    original_completion_history = path_change_commits(
        repo,
        head,
        original_completion_path,
        "original tag-only completion intent history",
    )
    require(
        len(original_completion_history) == 1,
        "original tag-only completion intent must be added once and remain append-only",
    )
    original_completion_source = original_completion_history[0]
    original_completion_base = original_completion["source"]["baseCommit"]
    original_admission = admit_tag_only_completion(
        repo,
        contract_path,
        contract,
        original_completion_base,
        original_completion_source,
        event_ref,
        parse_diff(repo, original_completion_base, original_completion_source),
    )
    require(
        original_admission["completionIntentPath"] == original_completion_path,
        "original completion source is not the exact admitted tag-only completion authorization",
    )

    failed = authorization["failedCompletion"]
    failed_source = failed["sourceCommit"]
    require(
        git(repo, "rev-parse", "--verify", f"{failed_source}^{{commit}}").strip()
        == failed_source,
        "failed completion source does not resolve to the exact commit",
    )
    require(
        is_ancestor(repo, failed_source, base),
        "failed completion source must be an ancestor of the recovery base",
    )
    protected_source_history = git_commit_list(
        repo, "--first-parent", head, label="protected source first-parent history"
    )
    require(
        failed_source in protected_source_history,
        "failed completion source must be on the protected source first-parent history",
    )

    predecessor = failed["authorization"]
    predecessor_path = predecessor["path"]
    if predecessor["type"] == "tag-only-completion":
        require(
            predecessor_path == original_completion_path,
            "initial completion recovery must name the immutable original completion intent",
        )
        require(
            failed_source == original_completion_source,
            "failed completion source must be the exact original completion authorization source",
        )
    else:
        require(
            PurePosixPath(predecessor_path).parent
            == PurePosixPath(recovery["intentDirectory"]),
            "predecessor completion recovery must be directly inside tagOnlyCompletionRecovery.intentDirectory",
        )
        require_regular_file(
            repo,
            failed_source,
            predecessor_path,
            "failed completion predecessor recovery intent",
        )
        require_regular_file(
            repo, head, predecessor_path, "current predecessor recovery intent"
        )
        require(
            git(repo, "show", f"{failed_source}:{predecessor_path}", binary=True)
            == git(repo, "show", f"{head}:{predecessor_path}", binary=True),
            "predecessor completion recovery intent must remain byte-identical",
        )
        require(
            not path_change_commits(
                repo,
                head,
                predecessor_path,
                "predecessor completion recovery intent history",
                start=failed_source,
            ),
            "predecessor completion recovery intent must remain append-only",
        )
        predecessor_record = validate_tag_only_completion_recovery_intent(
            git_json(repo, failed_source, predecessor_path, predecessor_path),
            predecessor_path,
        )
        require(
            predecessor_record["releaseUnit"] == authorization["releaseUnit"]
            and predecessor_record["channel"] == authorization["channel"]
            and predecessor_record["version"] == authorization["version"]
            and predecessor_record["originalCompletionIntent"]
            == authorization["originalCompletionIntent"]
            and predecessor_record["originalPublication"]
            == authorization["originalPublication"]
            and predecessor_record["retainedArtifact"]
            == authorization["retainedArtifact"],
            "predecessor completion recovery does not match the immutable recovery chain",
        )
        predecessor_base = predecessor_record["source"]["baseCommit"]
        admitted_predecessor = admit_tag_only_completion_recovery(
            repo,
            contract_path,
            contract,
            predecessor_base,
            failed_source,
            event_ref,
            parse_diff(repo, predecessor_base, failed_source),
        )
        require(
            admitted_predecessor["completionRecoveryIntentPath"]
            == predecessor_path,
            "failed completion source is not the exact admitted predecessor recovery authorization",
        )

    base_manifest, base_package_name, base_version = read_native_manifest(
        repo, base, unit, "tag-only completion recovery base version source"
    )
    head_manifest, head_package_name, head_version = read_native_manifest(
        repo, head, unit, "tag-only completion recovery head version source"
    )
    require(
        base_manifest == head_manifest,
        "native manifest must remain unchanged during tag-only completion recovery authorization",
    )
    require(
        base_package_name == head_package_name == unit["packageName"],
        "native manifest package name does not match releaseUnit.packageName",
    )
    require(
        isinstance(base_version, str) and SEMVER_RE.fullmatch(base_version) is not None,
        "tag-only completion recovery base manifest version is not exact SemVer",
    )
    require(
        base_version == head_version == authorization["version"],
        "tag-only completion recovery version does not match the unchanged native manifest",
    )
    rendered_tag = unit["tagPattern"].replace("{version}", authorization["version"])
    require(
        authorization["tag"] == rendered_tag,
        "tag-only completion recovery tag does not match the derived package tag",
    )
    expected_dist_tag = contract["channels"][authorization["channel"]]["distTag"]
    require(
        authorization["distTag"] == expected_dist_tag,
        "tag-only completion recovery dist-tag does not match the profile channel",
    )

    recovery_paths = tree_paths(
        repo,
        head,
        recovery["intentDirectory"],
        "tag-only completion recovery intent directory",
    )
    historical_recoveries: list[tuple[str, dict[str, Any], str]] = []
    matching_failed_runs: list[str] = []
    for historical_path in recovery_paths:
        validate_relative(
            historical_path,
            "historical tag-only completion recovery path",
            allow_glob=True,
        )
        require(
            PurePosixPath(historical_path).parent
            == PurePosixPath(recovery["intentDirectory"])
            and historical_path.endswith(".json"),
            "tag-only completion recovery directory may contain only direct JSON records",
        )
        require_regular_file(
            repo, head, historical_path, "historical tag-only completion recovery intent"
        )
        historical = validate_tag_only_completion_recovery_intent(
            git_json(repo, head, historical_path, historical_path), historical_path
        )
        additions = path_change_commits(
            repo,
            head,
            historical_path,
            f"historical tag-only completion recovery intent history: {historical_path}",
        )
        require(
            len(additions) == 1,
            f"historical tag-only completion recovery intent must be added once and never modified, renamed, or deleted: {historical_path}",
        )
        if (
            historical["releaseUnit"] == authorization["releaseUnit"]
            and historical["channel"] == authorization["channel"]
            and historical["version"] == authorization["version"]
            and historical["originalCompletionIntent"]
            == authorization["originalCompletionIntent"]
        ):
            historical_recoveries.append((historical_path, historical, additions[0]))
        if (
            historical["failedCompletion"]["workflowRunUrl"]
            == failed["workflowRunUrl"]
        ):
            matching_failed_runs.append(historical_path)
    require(
        matching_failed_runs == [recovery_path],
        "duplicate completion recovery authorization exists for the same failed completion run",
    )
    recovery_history = path_change_commits(
        repo,
        head,
        recovery["intentDirectory"],
        "tag-only completion recovery intent directory history",
    )
    require(
        len(recovery_history) == len(recovery_paths),
        "tag-only completion recovery intent directory must remain append-only in protected source history",
    )

    prior_recoveries = [
        item for item in historical_recoveries if item[0] != recovery_path
    ]
    if prior_recoveries:
        history_positions = {
            commit: index for index, commit in enumerate(protected_source_history)
        }
        require(
            all(addition in history_positions for _path, _record, addition in prior_recoveries),
            "historical completion recovery additions must be on protected source first-parent history",
        )
        latest_path, _latest_record, latest_addition = min(
            prior_recoveries, key=lambda item: history_positions[item[2]]
        )
        require(
            predecessor["type"] == "tag-only-completion-recovery"
            and predecessor_path == latest_path
            and failed_source == latest_addition,
            "failed completion must be the exact source authorized by the latest completion recovery record",
        )
    else:
        require(
            predecessor["type"] == "tag-only-completion"
            and predecessor_path == original_completion_path
            and failed_source == original_completion_source,
            "initial completion recovery must follow the exact original completion authorization",
        )

    return {
        "schemaVersion": "protected-package-tag-completion-recovery-admission/v1",
        "status": "admitted",
        "authorization": "tag-only-completion-recovery",
        "releaseUnit": unit["id"],
        "packageName": unit["packageName"],
        "registry": unit["registry"],
        "channel": authorization["channel"],
        "distTag": expected_dist_tag,
        "version": authorization["version"],
        "tag": rendered_tag,
        "originalIntentPath": authorization["originalIntentPath"],
        "originalCompletionIntent": authorization["originalCompletionIntent"],
        "completionRecoveryIntentPath": recovery_path,
        "originalPublication": authorization["originalPublication"],
        "failedCompletion": failed,
        "retainedArtifact": authorization["retainedArtifact"],
        "packageSource": {
            "commit": authorization["originalPublication"]["sourceCommit"]
        },
        "authorizationSource": {
            "ref": event_ref,
            "baseCommit": base,
            "commit": head,
        },
    }


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

    require_regular_file(repo, head, contract_path, "opt-in profile contract")
    contract = validate_contract(git_json(repo, head, contract_path, "profile contract"))
    require(event_ref == contract["source"]["ref"], "event ref does not match the profile source ref")

    unit = contract["releaseUnit"]
    for path_key in ("compatibilityContract", "changelog", "validationWorkflow", "publicationWorkflow"):
        require_regular_file(repo, head, unit[path_key], f"releaseUnit.{path_key}")
    require_regular_file(repo, head, contract["recovery"]["workflow"], "recovery.workflow")
    require_regular_file(
        repo,
        head,
        contract["tagOnlyCompletion"]["workflow"],
        "tagOnlyCompletion.workflow",
    )
    require_regular_file(
        repo,
        head,
        contract["tagOnlyCompletionRecovery"]["workflow"],
        "tagOnlyCompletionRecovery.workflow",
    )

    entries = parse_diff(repo, base, head)
    require(bool(entries), "admission diff is empty")
    changed_paths = {path for entry in entries for path in entry.paths}
    for path in changed_paths:
        validate_relative(path, "changed path", allow_glob=True)
    require(contract_path not in changed_paths, "profile contract must be established separately from release preparation")
    require(unit["validationWorkflow"] not in changed_paths, "validation workflow must be established separately from release preparation")
    require(unit["publicationWorkflow"] not in changed_paths, "publication workflow must be established separately from release preparation")
    require(
        contract["recovery"]["workflow"] not in changed_paths,
        "recovery workflow must be established separately from recovery authorization",
    )
    require(
        contract["tagOnlyCompletion"]["workflow"] not in changed_paths,
        "tag-only completion workflow must be established separately from completion authorization",
    )
    require(
        contract["tagOnlyCompletionRecovery"]["workflow"] not in changed_paths,
        "tag-only completion recovery workflow must be established separately from recovery authorization",
    )

    release_intent_entries = [
        entry
        for entry in entries
        if any(is_below(path, contract["intentDirectory"]) for path in entry.paths)
    ]
    recovery_intent_entries = [
        entry
        for entry in entries
        if any(
            is_below(path, contract["recovery"]["intentDirectory"])
            for path in entry.paths
        )
    ]
    completion_intent_entries = [
        entry
        for entry in entries
        if any(
            is_below(path, contract["tagOnlyCompletion"]["intentDirectory"])
            for path in entry.paths
        )
    ]
    completion_recovery_intent_entries = [
        entry
        for entry in entries
        if any(
            is_below(
                path,
                contract["tagOnlyCompletionRecovery"]["intentDirectory"],
            )
            for path in entry.paths
        )
    ]
    require(
        sum(
            bool(group)
            for group in (
                release_intent_entries,
                recovery_intent_entries,
                completion_intent_entries,
                completion_recovery_intent_entries,
            )
        )
        <= 1,
        "release, recovery, tag-only completion, and completion recovery authorizations cannot share one admission diff",
    )
    if completion_recovery_intent_entries:
        return admit_tag_only_completion_recovery(
            repo, contract_path, contract, base, head, event_ref, entries
        )
    if completion_intent_entries:
        return admit_tag_only_completion(
            repo, contract_path, contract, base, head, event_ref, entries
        )
    if recovery_intent_entries:
        return admit_recovery(
            repo, contract_path, contract, base, head, event_ref, entries
        )
    return admit_release(
        repo, contract_path, contract, base, head, event_ref, entries
    )


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
