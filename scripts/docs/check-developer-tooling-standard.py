#!/usr/bin/env python3

"""Validate the canonical Developer Tooling Standard source contract."""

from __future__ import annotations

import copy
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARD_ROOT = REPO_ROOT / "docs/standards/developer-tooling"
STANDARD_VERSION = "2026.08.1"
CONTRACT_VERSION = "golden-path/v1"
EXPECTED_DECISIONS = {f"GP-{number:03d}" for number in range(6, 21)}
FULL_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
CALVER = re.compile(r"^(?P<year>[0-9]{4})\.(?P<month>0[1-9]|1[0-2])(?:\.(?P<ordinal>[1-9][0-9]*))?$")

REQUIRED_PATHS = [
    "docs/standards/developer-tooling/README.md",
    "docs/standards/developer-tooling/command-contract.md",
    "docs/standards/developer-tooling/task-runner.md",
    "docs/standards/developer-tooling/toolchain-management.md",
    "docs/standards/developer-tooling/dependency-management.md",
    "docs/standards/developer-tooling/distribution.md",
    "docs/standards/developer-tooling/build-hygiene.md",
    "docs/standards/developer-tooling/runtime-support.md",
    "docs/standards/developer-tooling/conformance.md",
    "docs/standards/developer-tooling/exceptions.md",
    "docs/standards/developer-tooling/profiles/README.md",
    "docs/standards/developer-tooling/profiles/node-typescript.md",
    "docs/standards/developer-tooling/profiles/python.md",
    "docs/standards/developer-tooling/profiles/go.md",
    "docs/standards/developer-tooling/profiles/rust.md",
    "docs/standards/developer-tooling/profiles/zig.md",
    "docs/standards/developer-tooling/profiles/infrastructure.md",
    "docs/standards/developer-tooling/rules/README.md",
    "docs/standards/developer-tooling/rules/catalog.v1.json",
    "docs/standards/developer-tooling/rules/runtime-support.v1.json",
    "docs/standards/developer-tooling/schemas/README.md",
    "docs/standards/developer-tooling/schemas/golden-path-metadata-v1.schema.json",
    "docs/standards/developer-tooling/schemas/golden-path-native-roots-v1.schema.json",
    "docs/standards/developer-tooling/schemas/golden-path-exceptions-v1.schema.json",
    "docs/standards/developer-tooling/schemas/golden-path-checker-output-v1.schema.json",
    "docs/standards/developer-tooling/schemas/golden-path-rule-catalog-v1.schema.json",
    "docs/standards/developer-tooling/schemas/runtime-support-v1.schema.json",
    "docs/standards/developer-tooling/schemas/examples/golden-path-metadata-v1.valid.json",
    "docs/standards/developer-tooling/schemas/examples/golden-path-native-roots-v1.valid.json",
    "docs/standards/developer-tooling/schemas/examples/golden-path-exceptions-v1.valid.json",
    "docs/standards/developer-tooling/schemas/examples/golden-path-checker-output-v1.valid.json",
    "docs/guides/adopting-developer-tooling.md",
    "docs/guides/migrating-developer-tooling.md",
    "docs/guides/github-hosting-capabilities.md",
    "scripts/docs/fixtures/golden-path-adoption/existing-service.v1.json",
    "docs/decisions/0006-adopt-developer-tooling-golden-path.md",
    "docs/decisions/0008-separate-artifact-components-from-native-dependency-roots.md",
]

KNOWN_PROFILE_IDS = {
    "node-typescript",
    "python",
    "go",
    "rust",
    "zig",
    "zig-toolchain",
    "infrastructure-aws-cdk",
    "infrastructure-terraform",
    "infrastructure-opentofu",
    "infrastructure-pulumi",
    "documentation",
}

KNOWN_ARTIFACT_TYPES = {
    "application",
    "service",
    "library",
    "cli",
    "package",
    "binary",
    "container",
    "infrastructure",
    "tooling",
    "documentation",
}

KNOWN_CAPABILITIES = {
    "format",
    "lint",
    "typecheck",
    "test",
    "build",
    "package",
    "publish",
    "coverage",
    "fuzz",
    "unsafe",
    "native-extension",
    "cgo",
    "released-artifact",
    "dependency-automation",
    "cache",
    "devcontainer",
}

errors: list[str] = []


def report(message: str) -> None:
    errors.append(message)


def calver_key(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = CALVER.fullmatch(value)
    if match is None:
        return None
    return (
        int(match.group("year")),
        int(match.group("month")),
        int(match.group("ordinal") or "0"),
    )


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate object key {key!r}")
        value[key] = item
    return value


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle, object_pairs_hook=reject_duplicate_json_keys)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        report(f"{path.relative_to(REPO_ROOT)}: invalid JSON: {error}")
        return None


def json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def resolve_local_ref(root_schema: dict[str, Any], ref: str) -> Any:
    if not ref.startswith("#/"):
        raise ValueError(f"only local JSON pointers are supported: {ref}")
    value: Any = root_schema
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or part not in value:
            raise ValueError(f"unresolved JSON pointer: {ref}")
        value = value[part]
    return value


def parse_full_date(value: str) -> dt.date | None:
    if FULL_DATE.fullmatch(value) is None:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def validate_format(value: str, format_name: str) -> bool:
    if format_name == "date":
        return parse_full_date(value) is not None
    if format_name == "date-time":
        try:
            parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None
        except ValueError:
            return False
    if format_name == "uri":
        parsed = urlparse(value)
        return bool(parsed.scheme and (parsed.netloc or parsed.scheme == "urn"))
    return False


def validate_json_schema_instance(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    context: str,
    output: list[str],
) -> None:
    if "$ref" in schema:
        try:
            target = resolve_local_ref(root_schema, schema["$ref"])
        except ValueError as error:
            output.append(f"{context}: {error}")
            return
        validate_json_schema_instance(value, target, root_schema, context, output)
        return

    expected_type = schema.get("type")
    if expected_type is not None:
        types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(json_type_matches(value, item) for item in types):
            output.append(f"{context}: expected type {expected_type!r}")
            return

    if "const" in schema and value != schema["const"]:
        output.append(f"{context}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        output.append(f"{context}: value {value!r} is outside the enum")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            output.append(f"{context}: string is shorter than minLength")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            output.append(f"{context}: string is longer than maxLength")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            output.append(f"{context}: string does not match {schema['pattern']!r}")
        if "format" in schema and not validate_format(value, schema["format"]):
            output.append(f"{context}: invalid {schema['format']} value")

    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and "minimum" in schema
        and value < schema["minimum"]
    ):
        output.append(f"{context}: number is below minimum")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            output.append(f"{context}: array is shorter than minItems")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            output.append(f"{context}: array is longer than maxItems")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                output.append(f"{context}: array items must be unique")
        if isinstance(schema.get("items"), dict):
            for index, item in enumerate(value):
                validate_json_schema_instance(
                    item,
                    schema["items"],
                    root_schema,
                    f"{context}[{index}]",
                    output,
                )
        if "contains" in schema:
            if not any(
                schema_is_valid(item, schema["contains"], root_schema)
                for item in value
            ):
                output.append(f"{context}: array does not satisfy contains")

    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = sorted(set(required) - set(value))
        if missing:
            output.append(
                f"{context}: missing required keys: {', '.join(missing)}"
            )
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate_json_schema_instance(
                    item,
                    properties[key],
                    root_schema,
                    f"{context}.{key}",
                    output,
                )
            elif schema.get("additionalProperties") is False:
                output.append(f"{context}: unexpected property {key!r}")
            elif isinstance(schema.get("additionalProperties"), dict):
                validate_json_schema_instance(
                    item,
                    schema["additionalProperties"],
                    root_schema,
                    f"{context}.{key}",
                    output,
                )
        if len(value) < schema.get("minProperties", 0):
            output.append(f"{context}: object has fewer than minProperties")
        if isinstance(schema.get("propertyNames"), dict):
            for key in value:
                validate_json_schema_instance(
                    key,
                    schema["propertyNames"],
                    root_schema,
                    f"{context}.<property-name>",
                    output,
                )

    for branch in schema.get("allOf", []):
        validate_json_schema_instance(value, branch, root_schema, context, output)
    if "anyOf" in schema and not any(
        schema_is_valid(value, branch, root_schema)
        for branch in schema["anyOf"]
    ):
        output.append(f"{context}: value does not satisfy anyOf")
    if "if" in schema:
        branch_name = "then" if schema_is_valid(value, schema["if"], root_schema) else "else"
        if branch_name in schema:
            validate_json_schema_instance(
                value, schema[branch_name], root_schema, context, output
            )


def schema_is_valid(
    value: Any, schema: dict[str, Any], root_schema: dict[str, Any]
) -> bool:
    scratch: list[str] = []
    validate_json_schema_instance(value, schema, root_schema, "$", scratch)
    return not scratch


SUPPORTED_SCHEMA_KEYWORDS = {
    "$defs",
    "$id",
    "$ref",
    "$schema",
    "additionalProperties",
    "allOf",
    "anyOf",
    "const",
    "contains",
    "else",
    "enum",
    "format",
    "if",
    "items",
    "maxItems",
    "maxLength",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "pattern",
    "properties",
    "propertyNames",
    "required",
    "then",
    "title",
    "type",
    "uniqueItems",
}


def validate_schema_definition(
    schema: Any,
    root_schema: dict[str, Any],
    context: str,
) -> None:
    if not isinstance(schema, dict):
        report(f"{context}: schema node must be an object")
        return
    unknown = sorted(set(schema) - SUPPORTED_SCHEMA_KEYWORDS)
    if unknown:
        report(f"{context}: unsupported schema keywords: {', '.join(unknown)}")
    if "$ref" in schema:
        try:
            resolve_local_ref(root_schema, schema["$ref"])
        except ValueError as error:
            report(f"{context}: {error}")
    for key in ("properties", "$defs"):
        for name, child in schema.get(key, {}).items():
            validate_schema_definition(
                child, root_schema, f"{context}.{key}.{name}"
            )
    for key in ("items", "additionalProperties", "propertyNames", "contains"):
        child = schema.get(key)
        if isinstance(child, dict):
            validate_schema_definition(child, root_schema, f"{context}.{key}")
    for key in ("allOf", "anyOf"):
        for index, child in enumerate(schema.get(key, [])):
            validate_schema_definition(
                child, root_schema, f"{context}.{key}[{index}]"
            )
    for key in ("if", "then", "else"):
        child = schema.get(key)
        if isinstance(child, dict):
            validate_schema_definition(child, root_schema, f"{context}.{key}")


def validate_instance_file(instance_path: Path, schema_path: Path) -> None:
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    if instance is None or schema is None:
        return
    findings: list[str] = []
    context = str(instance_path.relative_to(REPO_ROOT))
    validate_json_schema_instance(instance, schema, schema, context, findings)
    for finding in findings:
        report(finding)


def require_keys(value: Any, keys: set[str], context: str) -> bool:
    if not isinstance(value, dict):
        report(f"{context}: expected an object")
        return False
    missing = sorted(keys - set(value))
    if missing:
        report(f"{context}: missing required keys: {', '.join(missing)}")
        return False
    return True


def require_unique_strings(
    value: Any,
    context: str,
    *,
    allowed: set[str] | None = None,
    allow_wildcard: bool = False,
) -> bool:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        report(f"{context}: expected an array of non-empty strings")
        return False
    if len(value) != len(set(value)):
        report(f"{context}: values must be unique")
        return False
    if allowed is not None:
        unknown = sorted(
            item
            for item in value
            if item not in allowed and not (allow_wildcard and item == "*")
        )
        if unknown:
            report(f"{context}: unknown values: {', '.join(unknown)}")
            return False
    return True


def github_anchor(heading: str) -> str:
    heading = re.sub(r"<[^>]+>", "", heading)
    heading = heading.replace("`", "").strip().lower()
    heading = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
    return re.sub(r"\s+", "-", heading)


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        report(f"{path.relative_to(REPO_ROOT)}: cannot read: {error}")
        return anchors
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            anchors.add(github_anchor(match.group(1)))
    return anchors


def validate_schema_sources() -> None:
    schema_paths = sorted((STANDARD_ROOT / "schemas").glob("*.schema.json"))
    seen_ids: set[str] = set()
    expected_versions = {
        "golden-path-metadata-v1.schema.json": "golden-path-metadata/v1",
        "golden-path-native-roots-v1.schema.json": "golden-path-native-roots/v1",
        "golden-path-exceptions-v1.schema.json": "golden-path-exceptions/v1",
        "golden-path-checker-output-v1.schema.json": "golden-path-checker-output/v1",
        "golden-path-rule-catalog-v1.schema.json": "golden-path-rule-catalog/v1",
        "runtime-support-v1.schema.json": "runtime-support/v1",
    }
    if {path.name for path in schema_paths} != set(expected_versions):
        report("schemas: source set does not match the required v1 contract")

    for path in schema_paths:
        data = load_json(path)
        context = str(path.relative_to(REPO_ROOT))
        if not require_keys(
            data,
            {"$schema", "$id", "title", "type", "properties"},
            context,
        ):
            continue
        if data["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            report(f"{context}: schema draft must be 2020-12")
        schema_id = data["$id"]
        if not isinstance(schema_id, str) or schema_id in seen_ids:
            report(f"{context}: $id must be a unique string")
        else:
            seen_ids.add(schema_id)
            if not schema_id.startswith("urn:5010-dev:golden-path:"):
                report(f"{context}: $id must be repository-independent")

        expected = expected_versions.get(path.name)
        schema_version = data.get("properties", {}).get("schemaVersion", {})
        if schema_version.get("const") != expected:
            report(
                f"{context}: schemaVersion const must be {expected!r}"
            )
        validate_schema_definition(data, data, context)


def validate_contract_instances() -> None:
    mappings = [
        (
            STANDARD_ROOT
            / "schemas/examples/golden-path-metadata-v1.valid.json",
            STANDARD_ROOT / "schemas/golden-path-metadata-v1.schema.json",
        ),
        (
            STANDARD_ROOT
            / "schemas/examples/golden-path-native-roots-v1.valid.json",
            STANDARD_ROOT / "schemas/golden-path-native-roots-v1.schema.json",
        ),
        (
            STANDARD_ROOT
            / "schemas/examples/golden-path-exceptions-v1.valid.json",
            STANDARD_ROOT / "schemas/golden-path-exceptions-v1.schema.json",
        ),
        (
            STANDARD_ROOT
            / "schemas/examples/golden-path-checker-output-v1.valid.json",
            STANDARD_ROOT
            / "schemas/golden-path-checker-output-v1.schema.json",
        ),
        (
            STANDARD_ROOT / "rules/catalog.v1.json",
            STANDARD_ROOT / "schemas/golden-path-rule-catalog-v1.schema.json",
        ),
        (
            STANDARD_ROOT / "rules/runtime-support.v1.json",
            STANDARD_ROOT / "schemas/runtime-support-v1.schema.json",
        ),
    ]
    for instance_path, schema_path in mappings:
        validate_instance_file(instance_path, schema_path)


def require_schema_rejection(
    instance: Any,
    schema_path: Path,
    label: str,
) -> None:
    schema = load_json(schema_path)
    if schema is not None and schema_is_valid(instance, schema, schema):
        report(f"schema validator self-test accepted invalid {label}")


def validate_schema_validator_self_tests() -> None:
    metadata = load_json(
        STANDARD_ROOT
        / "schemas/examples/golden-path-metadata-v1.valid.json"
    )
    invalid_metadata = copy.deepcopy(metadata)
    invalid_metadata["profiles"] = ["unknown-profile"]
    require_schema_rejection(
        invalid_metadata,
        STANDARD_ROOT / "schemas/golden-path-metadata-v1.schema.json",
        "metadata profile",
    )

    native_roots = load_json(
        STANDARD_ROOT
        / "schemas/examples/golden-path-native-roots-v1.valid.json"
    )
    invalid_native_roots = copy.deepcopy(native_roots)
    invalid_native_roots["roots"][0]["profiles"] = ["documentation"]
    require_schema_rejection(
        invalid_native_roots,
        STANDARD_ROOT / "schemas/golden-path-native-roots-v1.schema.json",
        "native-root profile",
    )
    conflated_native_roots = copy.deepcopy(native_roots)
    conflated_native_roots["roots"][0]["artifactTypes"] = ["library"]
    require_schema_rejection(
        conflated_native_roots,
        STANDARD_ROOT / "schemas/golden-path-native-roots-v1.schema.json",
        "artifact classification in a native-root declaration",
    )

    exceptions = load_json(
        STANDARD_ROOT
        / "schemas/examples/golden-path-exceptions-v1.valid.json"
    )
    invalid_exceptions = copy.deepcopy(exceptions)
    invalid_exceptions["exceptions"][0]["id"] = "invalid"
    require_schema_rejection(
        invalid_exceptions,
        STANDARD_ROOT / "schemas/golden-path-exceptions-v1.schema.json",
        "exception ID",
    )
    for label, value in (
        ("compact exception date", "20260801"),
        ("ISO week exception date", "2026-W31-5"),
    ):
        invalid_exception_date = copy.deepcopy(exceptions)
        invalid_exception_date["exceptions"][0]["expiresAt"] = value
        require_schema_rejection(
            invalid_exception_date,
            STANDARD_ROOT / "schemas/golden-path-exceptions-v1.schema.json",
            label,
        )

    output = load_json(
        STANDARD_ROOT
        / "schemas/examples/golden-path-checker-output-v1.valid.json"
    )
    invalid_output = copy.deepcopy(output)
    invalid_output["catalogDigest"] = "sha256:invalid"
    require_schema_rejection(
        invalid_output,
        STANDARD_ROOT
        / "schemas/golden-path-checker-output-v1.schema.json",
        "catalog digest",
    )
    invalid_checker_version = copy.deepcopy(output)
    invalid_checker_version["checkerVersion"] = "latest"
    require_schema_rejection(
        invalid_checker_version,
        STANDARD_ROOT
        / "schemas/golden-path-checker-output-v1.schema.json",
        "checker SemVer",
    )
    invalid_evaluation_time = copy.deepcopy(output)
    invalid_evaluation_time["evaluatedAt"] = "2026-07-30T09:00:00+09:00"
    require_schema_rejection(
        invalid_evaluation_time,
        STANDARD_ROOT
        / "schemas/golden-path-checker-output-v1.schema.json",
        "non-canonical evaluation timezone",
    )

    catalog = load_json(STANDARD_ROOT / "rules/catalog.v1.json")
    invalid_catalog = copy.deepcopy(catalog)
    invalid_catalog["rules"][0]["applicability"]["profiles"] = ["*", "go"]
    require_schema_rejection(
        invalid_catalog,
        STANDARD_ROOT / "schemas/golden-path-rule-catalog-v1.schema.json",
        "mixed wildcard profile",
    )

    runtime = load_json(STANDARD_ROOT / "rules/runtime-support.v1.json")
    invalid_runtime = copy.deepcopy(runtime)
    invalid_runtime["profiles"]["node"]["versions"][0][
        "upstreamLifecycle"
    ] = "invalid"
    require_schema_rejection(
        invalid_runtime,
        STANDARD_ROOT / "schemas/runtime-support-v1.schema.json",
        "runtime lifecycle",
    )


def validate_metadata_enum_alignment() -> None:
    expected = {
        "profile": KNOWN_PROFILE_IDS,
        "artifactType": KNOWN_ARTIFACT_TYPES,
        "capability": KNOWN_CAPABILITIES,
    }
    paths = [
        STANDARD_ROOT / "schemas/golden-path-metadata-v1.schema.json",
        STANDARD_ROOT / "schemas/golden-path-rule-catalog-v1.schema.json",
    ]
    for path in paths:
        data = load_json(path)
        if data is None:
            continue
        for definition, known_values in expected.items():
            schema_values = set(
                data.get("$defs", {}).get(definition, {}).get("enum", [])
            )
            if schema_values != known_values:
                report(
                    f"{path.relative_to(REPO_ROOT)}: {definition} enum and "
                    "validator constants have drifted"
                )

    native_path = STANDARD_ROOT / "schemas/golden-path-native-roots-v1.schema.json"
    native_schema = load_json(native_path)
    if native_schema is not None:
        native_values = set(
            native_schema.get("$defs", {}).get("nativeProfile", {}).get("enum", [])
        )
        expected_native = KNOWN_PROFILE_IDS - {"documentation"}
        if native_values != expected_native:
            report(
                f"{native_path.relative_to(REPO_ROOT)}: nativeProfile enum and "
                "validator constants have drifted"
            )


def validate_metadata_example() -> None:
    path = (
        STANDARD_ROOT
        / "schemas/examples/golden-path-metadata-v1.valid.json"
    )
    data = load_json(path)
    context = str(path.relative_to(REPO_ROOT))
    if not require_keys(
        data,
        {
            "schemaVersion",
            "contractVersion",
            "standardVersion",
            "assetBundleVersion",
            "profiles",
            "artifactTypes",
            "capabilities",
        },
        context,
    ):
        return
    expected = {
        "schemaVersion": "golden-path-metadata/v1",
        "contractVersion": CONTRACT_VERSION,
        "standardVersion": STANDARD_VERSION,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            report(f"{context}: {key} must be {value!r}")
    require_unique_strings(
        data["profiles"], f"{context}.profiles", allowed=KNOWN_PROFILE_IDS
    )
    require_unique_strings(
        data["artifactTypes"],
        f"{context}.artifactTypes",
        allowed=KNOWN_ARTIFACT_TYPES,
    )
    require_unique_strings(
        data["capabilities"],
        f"{context}.capabilities",
        allowed=KNOWN_CAPABILITIES,
    )


def parse_date(value: Any, context: str) -> dt.date | None:
    if not isinstance(value, str):
        report(f"{context}: expected an RFC 3339 full-date")
        return None
    parsed = parse_full_date(value)
    if parsed is None:
        report(f"{context}: expected an RFC 3339 full-date")
    return parsed


def validate_exceptions_example() -> None:
    path = (
        STANDARD_ROOT
        / "schemas/examples/golden-path-exceptions-v1.valid.json"
    )
    data = load_json(path)
    context = str(path.relative_to(REPO_ROOT))
    if not require_keys(
        data,
        {"schemaVersion", "exceptions"},
        context,
    ):
        return
    if data["schemaVersion"] != "golden-path-exceptions/v1":
        report(f"{context}: unexpected schemaVersion")
    if not isinstance(data["exceptions"], list) or not data["exceptions"]:
        report(f"{context}.exceptions: expected at least one exception")
        return

    catalog = load_json(STANDARD_ROOT / "rules/catalog.v1.json")
    catalog_rules = {
        rule.get("id"): rule
        for rule in catalog.get("rules", [])
        if isinstance(rule, dict) and isinstance(rule.get("id"), str)
    }

    identifiers: set[str] = set()
    common = {
        "id",
        "rules",
        "scope",
        "reason",
        "owner",
        "riskClass",
        "approval",
        "expiresAt",
    }
    for index, exception in enumerate(data["exceptions"]):
        item_context = f"{context}.exceptions[{index}]"
        if not require_keys(exception, common, item_context):
            continue
        identifier = exception["id"]
        if not isinstance(identifier, str) or identifier in identifiers:
            report(f"{item_context}.id: must be a unique string")
        else:
            identifiers.add(identifier)
        require_unique_strings(exception["rules"], f"{item_context}.rules")
        referenced_rules = [
            catalog_rules.get(rule_id) for rule_id in exception["rules"]
        ]
        unknown_rules = [
            rule_id
            for rule_id, rule in zip(exception["rules"], referenced_rules)
            if rule is None
        ]
        if unknown_rules:
            report(
                f"{item_context}.rules: unknown catalog rules "
                f"{', '.join(unknown_rules)}"
            )
        for rule in referenced_rules:
            if rule is not None and rule.get("waivable") is not True:
                report(
                    f"{item_context}.rules: {rule['id']} is not waivable"
                )
        catalog_high_risk = any(
            rule is not None and rule.get("highRisk") is True
            for rule in referenced_rules
        )
        if catalog_high_risk and exception["riskClass"] != "high":
            report(
                f"{item_context}.riskClass: catalog-high-risk rule requires high"
            )
        expires = parse_date(exception["expiresAt"], f"{item_context}.expiresAt")
        if expires is None:
            report(f"{item_context}: expiresAt must be a valid date")
        approval = exception["approval"]
        if not require_keys(
            approval, {"authorities"}, f"{item_context}.approval"
        ):
            continue
        authorities = approval["authorities"]
        if not isinstance(authorities, list) or not authorities:
            report(f"{item_context}.authorities: expected approval evidence")
        else:
            authority_keys: list[tuple[Any, Any]] = []
            for authority_index, authority in enumerate(authorities):
                authority_context = (
                    f"{item_context}.approval.authorities[{authority_index}]"
                )
                if not require_keys(
                    authority,
                    {"role", "reference", "approvedAt"},
                    authority_context,
                ):
                    continue
                authority_keys.append(
                    (authority.get("role"), authority.get("reference"))
                )
                parse_date(
                    authority.get("approvedAt"),
                    f"{authority_context}.approvedAt",
                )
            if len(authority_keys) != len(set(authority_keys)):
                report(
                    f"{item_context}.authorities: approvers must be distinct"
                )
        if exception["riskClass"] == "high":
            if not require_keys(
                exception,
                common | {"trackingIssue", "risk", "compensatingControls"},
                item_context,
            ):
                continue
            controls = exception["compensatingControls"]
            if not isinstance(controls, list) or not controls:
                report(
                    f"{item_context}.compensatingControls: expected controls"
                )
            if not isinstance(authorities, list) or len(authorities) < 2:
                report(
                    f"{item_context}.authorities: high risk needs two approvals"
                )


def validate_checker_example() -> None:
    path = (
        STANDARD_ROOT
        / "schemas/examples/golden-path-checker-output-v1.valid.json"
    )
    data = load_json(path)
    context = str(path.relative_to(REPO_ROOT))
    required = {
        "schemaVersion",
        "contractVersion",
        "standardVersion",
        "checkerVersion",
        "catalogDigest",
        "evaluatedAt",
        "enforcement",
        "profiles",
        "exitCode",
        "complete",
        "summary",
        "findings",
    }
    if not require_keys(data, required, context):
        return
    if data["schemaVersion"] != "golden-path-checker-output/v1":
        report(f"{context}: unexpected schemaVersion")
    if data["contractVersion"] != CONTRACT_VERSION:
        report(f"{context}: unexpected contractVersion")
    if data["standardVersion"] != STANDARD_VERSION:
        report(f"{context}: unexpected standardVersion")
    require_unique_strings(
        data["profiles"],
        f"{context}.profiles",
        allowed=KNOWN_PROFILE_IDS,
    )

    statuses = ["pass", "fail", "warn", "skip", "waived", "error"]
    findings = data["findings"]
    if not isinstance(findings, list):
        report(f"{context}.findings: expected an array")
        return
    actual = {status: 0 for status in statuses}
    for index, finding in enumerate(findings):
        item_context = f"{context}.findings[{index}]"
        if not require_keys(
            finding,
            {
                "ruleId",
                "status",
                "severity",
                "assessment",
                "path",
                "message",
                "remediation",
                "exceptionId",
            },
            item_context,
        ):
            continue
        status = finding["status"]
        if status not in actual:
            report(f"{item_context}.status: unknown status {status!r}")
        else:
            actual[status] += 1
    if data["summary"] != actual:
        report(f"{context}.summary: counts must match findings")
    has_failure = actual["fail"] > 0 or actual["error"] > 0
    if has_failure and data["exitCode"] == 0:
        report(f"{context}.exitCode: fail or error cannot exit successfully")


def validate_rule_catalog() -> None:
    path = STANDARD_ROOT / "rules/catalog.v1.json"
    data = load_json(path)
    context = str(path.relative_to(REPO_ROOT))
    if not require_keys(
        data,
        {"schemaVersion", "contractVersion", "standardVersion", "rules"},
        context,
    ):
        return
    expected = {
        "schemaVersion": "golden-path-rule-catalog/v1",
        "contractVersion": CONTRACT_VERSION,
        "standardVersion": STANDARD_VERSION,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            report(f"{context}: {key} must be {value!r}")
    rules = data["rules"]
    if not isinstance(rules, list) or not rules:
        report(f"{context}.rules: expected at least one rule")
        return

    required = {
        "id",
        "title",
        "level",
        "source",
        "applicability",
        "assessment",
        "severity",
        "waivable",
        "highRisk",
        "assertion",
        "remediation",
        "introducedIn",
        "retiredIn",
        "replacement",
    }
    identifiers: set[str] = set()
    decisions: set[str] = set()
    anchors_by_path: dict[Path, set[str]] = {}

    for index, rule in enumerate(rules):
        item_context = f"{context}.rules[{index}]"
        if not require_keys(rule, required, item_context):
            continue
        identifier = rule["id"]
        if not isinstance(identifier, str) or not re.fullmatch(
            r"DT-[A-Z]+-[0-9]{3}", identifier
        ):
            report(f"{item_context}.id: invalid stable rule ID")
        elif identifier in identifiers:
            report(f"{item_context}.id: duplicate stable rule ID {identifier}")
        else:
            identifiers.add(identifier)

        level = rule["level"]
        severity = rule["severity"]
        expected_severity = {
            "MUST": "error",
            "MUST_NOT": "error",
            "SHOULD": "warning",
            "SHOULD_NOT": "warning",
            "MAY": "info",
        }.get(level)
        if expected_severity is None:
            report(f"{item_context}.level: invalid requirement level")
        elif severity != expected_severity:
            report(
                f"{item_context}.severity: {level} must use {expected_severity}"
            )
        if rule["assessment"] not in {"automated", "manual", "hybrid"}:
            report(f"{item_context}.assessment: invalid assessment mode")
        if not isinstance(rule["waivable"], bool):
            report(f"{item_context}.waivable: expected a boolean")
        if not isinstance(rule["highRisk"], bool):
            report(f"{item_context}.highRisk: expected a boolean")
        introduced = calver_key(rule["introducedIn"])
        current_standard = calver_key(STANDARD_VERSION)
        if introduced is None or current_standard is None or introduced > current_standard:
            report(
                f"{item_context}.introducedIn: must be a valid standard release "
                f"no later than {STANDARD_VERSION}"
            )

        source = rule["source"]
        if not require_keys(
            source, {"decision", "document", "anchor"}, f"{item_context}.source"
        ):
            continue
        decision = source["decision"]
        if decision not in EXPECTED_DECISIONS:
            report(f"{item_context}.source.decision: unknown decision")
        else:
            decisions.add(decision)
        document = source["document"]
        if (
            not isinstance(document, str)
            or document.startswith("/")
            or ".." in Path(document).parts
            or not document.endswith(".md")
        ):
            report(f"{item_context}.source.document: invalid relative path")
            continue
        document_path = STANDARD_ROOT / document
        if not document_path.is_file():
            report(
                f"{item_context}.source.document: missing standard document "
                f"{document}"
            )
            continue
        if document_path not in anchors_by_path:
            anchors_by_path[document_path] = markdown_anchors(document_path)
        if source["anchor"] not in anchors_by_path[document_path]:
            report(
                f"{item_context}.source.anchor: #{source['anchor']} is not a "
                f"heading in {document}"
            )

        applicability = rule["applicability"]
        if not require_keys(
            applicability,
            {"profiles", "artifactTypes", "capabilities", "condition"},
            f"{item_context}.applicability",
        ):
            continue
        require_unique_strings(
            applicability["profiles"],
            f"{item_context}.applicability.profiles",
            allowed=KNOWN_PROFILE_IDS,
            allow_wildcard=True,
        )
        if "*" in applicability["profiles"] and len(
            applicability["profiles"]
        ) != 1:
            report(
                f"{item_context}.applicability.profiles: wildcard must be the "
                "only value"
            )
        require_unique_strings(
            applicability["artifactTypes"],
            f"{item_context}.applicability.artifactTypes",
            allowed=KNOWN_ARTIFACT_TYPES,
        )
        require_unique_strings(
            applicability["capabilities"],
            f"{item_context}.applicability.capabilities",
            allowed=KNOWN_CAPABILITIES,
        )
        if not isinstance(applicability["condition"], str) or len(
            applicability["condition"]
        ) < 3:
            report(
                f"{item_context}.applicability.condition: expected a condition"
            )

    if decisions != EXPECTED_DECISIONS:
        missing = sorted(EXPECTED_DECISIONS - decisions)
        extra = sorted(decisions - EXPECTED_DECISIONS)
        if missing:
            report(f"{context}: missing decision coverage: {', '.join(missing)}")
        if extra:
            report(f"{context}: unexpected decisions: {', '.join(extra)}")


def validate_runtime_catalog() -> None:
    path = STANDARD_ROOT / "rules/runtime-support.v1.json"
    data = load_json(path)
    context = str(path.relative_to(REPO_ROOT))
    if not require_keys(
        data,
        {"schemaVersion", "standardVersion", "asOf", "profiles", "sources"},
        context,
    ):
        return
    if data["schemaVersion"] != "runtime-support/v1":
        report(f"{context}: unexpected schemaVersion")
    if data["standardVersion"] != STANDARD_VERSION:
        report(f"{context}: unexpected standardVersion")
    parse_date(data["asOf"], f"{context}.asOf")
    if set(data["profiles"]) != {"node", "python", "go", "rust", "zig"}:
        report(f"{context}.profiles: expected node, python, go, rust, and zig")
    sources = data["sources"]
    if not isinstance(sources, list) or not sources:
        report(f"{context}.sources: expected official lifecycle sources")
        return
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        item_context = f"{context}.sources[{index}]"
        if not require_keys(source, {"id", "url", "checkedAt"}, item_context):
            continue
        identifier = source["id"]
        if not isinstance(identifier, str) or identifier in source_ids:
            report(f"{item_context}.id: must be a unique string")
        else:
            source_ids.add(identifier)
        if not isinstance(source["url"], str) or not source["url"].startswith(
            "https://"
        ):
            report(f"{item_context}.url: expected an HTTPS source")
        parse_date(source["checkedAt"], f"{item_context}.checkedAt")

    for profile_id, profile in data["profiles"].items():
        item_context = f"{context}.profiles.{profile_id}"
        if not require_keys(profile, {"sourceIds", "versions"}, item_context):
            continue
        require_unique_strings(profile["sourceIds"], f"{item_context}.sourceIds")
        unknown_sources = sorted(set(profile["sourceIds"]) - source_ids)
        if unknown_sources:
            report(
                f"{item_context}.sourceIds: unknown sources "
                f"{', '.join(unknown_sources)}"
            )
        versions = profile["versions"]
        if not isinstance(versions, list) or not versions:
            report(f"{item_context}.versions: expected lifecycle entries")
            continue
        selectors: set[tuple[str, str]] = set()
        for version_index, version in enumerate(versions):
            version_context = f"{item_context}.versions[{version_index}]"
            if not require_keys(
                version,
                {
                    "selector",
                    "upstreamLifecycle",
                    "organizationDisposition",
                },
                version_context,
            ):
                continue
            selector = version["selector"]
            if not require_keys(
                selector, {"kind", "value"}, f"{version_context}.selector"
            ):
                continue
            selector_key = (selector["kind"], selector["value"])
            if selector_key in selectors:
                report(f"{version_context}.selector: must be unique")
            else:
                selectors.add(selector_key)
            if "migrationState" in version:
                report(
                    f"{version_context}: repository migrationState is not "
                    "allowed in the central catalog"
                )
            if version["organizationDisposition"] not in {
                "preferred",
                "supported",
                "compatibility-only",
                "blocked",
            }:
                report(
                    f"{version_context}.organizationDisposition: invalid value"
                )
            if version.get("supportEndsAt") is not None:
                parse_date(
                    version["supportEndsAt"],
                    f"{version_context}.supportEndsAt",
                )
            for key in ("graceStartedAt", "graceEndsAt"):
                if version.get(key) is not None:
                    parse_date(version[key], f"{version_context}.{key}")

    python_selectors = {
        item["selector"]["value"]: item
        for item in data["profiles"].get("python", {}).get("versions", [])
        if isinstance(item, dict)
        and isinstance(item.get("selector"), dict)
        and "value" in item["selector"]
    }
    if python_selectors.get("3.11", {}).get(
        "organizationDisposition"
    ) != "supported":
        report(
            f"{context}: Python 3.11 must remain supported in {STANDARD_VERSION}"
        )
    if python_selectors.get("3.10", {}).get("supportEndsAt") != "2026-10-31":
        report(
            f"{context}: Python 3.10 compatibility window must end 2026-10-31"
        )
    if data["profiles"].get("rust", {}).get("policy", {}).get(
        "graceDays"
    ) != 90:
        report(f"{context}: Rust N-1/N-2 grace must be 90 days")
    rust_grace = next(
        (
            item
            for item in data["profiles"].get("rust", {}).get("versions", [])
            if item.get("selector")
            == {"kind": "relative", "value": "n-1-n-2"}
        ),
        None,
    )
    if rust_grace is None:
        report(f"{context}: Rust N-1/N-2 grace selector is missing")
    else:
        started = parse_date(
            rust_grace.get("graceStartedAt"),
            f"{context}.profiles.rust.graceStartedAt",
        )
        ended = parse_date(
            rust_grace.get("graceEndsAt"),
            f"{context}.profiles.rust.graceEndsAt",
        )
        if started is not None and ended is not None:
            if (ended - started).days != 90:
                report(f"{context}: Rust grace dates must span 90 days")
    zig_selectors = {
        (
            item.get("selector", {}).get("kind"),
            item.get("selector", {}).get("value"),
        )
        for item in data["profiles"].get("zig", {}).get("versions", [])
        if isinstance(item, dict)
    }
    if ("channel", "latest-tagged-stable") not in zig_selectors:
        report(f"{context}: Zig latest tagged stable baseline is missing")


def validate_traceability_and_scope() -> None:
    readme_path = STANDARD_ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    for decision in sorted(EXPECTED_DECISIONS):
        if not re.search(rf"^\| {re.escape(decision)} \|", text, re.MULTILINE):
            report(
                "docs/standards/developer-tooling/README.md: "
                f"missing traceability row for {decision}"
            )

    forbidden_patterns = {
        r"https://linear\.app/": "issue tracker URL",
        r"\bENG-[0-9]+\b": "issue identifier",
        r"https://github\.com/5010-dev/(?!\.github(?:/|$))[^)\s]+": (
            "consumer repository URL"
        ),
        r"\b(?:fiftyten-indicators-core|indicator-data-collector|"
        r"indicator-ecs-infra|5010-indicator-server)\b": "product repository",
    }
    scope_paths = list(STANDARD_ROOT.rglob("*.md"))
    scope_paths.extend(
        [
            REPO_ROOT / "docs/guides/adopting-developer-tooling.md",
            REPO_ROOT / "docs/guides/migrating-developer-tooling.md",
            REPO_ROOT
            / "docs/decisions/0006-adopt-developer-tooling-golden-path.md",
            REPO_ROOT
            / "docs/decisions/0008-separate-artifact-components-from-native-dependency-roots.md",
        ]
    )
    for path in sorted(set(scope_paths)):
        source = path.read_text(encoding="utf-8")
        for pattern, label in forbidden_patterns.items():
            if re.search(pattern, source, re.IGNORECASE):
                report(
                    f"{path.relative_to(REPO_ROOT)}: central standard contains "
                    f"a repository-coupled {label}"
                )


def validate_adoption_guides() -> None:
    capability_path = REPO_ROOT / "docs/guides/github-hosting-capabilities.md"
    capability = capability_path.read_text(encoding="utf-8")
    if not re.search(
        rf"^- Standard: `{re.escape(STANDARD_VERSION)}`$",
        capability,
        re.MULTILINE,
    ):
        report(
            f"{capability_path.relative_to(REPO_ROOT)}: standard version must be "
            f"{STANDARD_VERSION}"
        )

    required_boundaries = {
        "docs/guides/adopting-developer-tooling.md": (
            ".github/golden-path-native-roots.yaml",
            "Do not copy artifact types or capabilities",
            "do not edit generated `.github/golden-path.yaml`",
            "`adoption` creates the first Golden Path control-plane baseline",
        ),
        "docs/guides/migrating-developer-tooling.md": (
            ".github/golden-path-native-roots.yaml",
            "whole-file generated metadata",
            "independent roots for one profile",
            "materializationMode: adoption",
            "customized retired assets must conflict",
        ),
    }
    for relative, phrases in required_boundaries.items():
        source = (REPO_ROOT / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in source:
                report(f"{relative}: missing native-root adoption boundary {phrase!r}")


def main() -> int:
    for relative in REQUIRED_PATHS:
        path = REPO_ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            report(f"required source missing or empty: {relative}")

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(
            f"developer tooling standard check: FAILED ({len(errors)} problem(s))",
            file=sys.stderr,
        )
        return 1

    validate_schema_sources()
    validate_contract_instances()
    validate_schema_validator_self_tests()
    validate_metadata_enum_alignment()
    validate_metadata_example()
    validate_exceptions_example()
    validate_checker_example()
    validate_rule_catalog()
    validate_runtime_catalog()
    validate_traceability_and_scope()
    validate_adoption_guides()

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(
            f"developer tooling standard check: FAILED ({len(errors)} problem(s))",
            file=sys.stderr,
        )
        return 1

    print("developer tooling standard check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
