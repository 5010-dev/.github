#!/usr/bin/env python3

"""Validate the canonical Developer Tooling Standard source contract."""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
STANDARD_ROOT = REPO_ROOT / "docs/standards/developer-tooling"
STANDARD_VERSION = "2026.07"
CONTRACT_VERSION = "golden-path/v1"
EXPECTED_DECISIONS = {f"GP-{number:03d}" for number in range(6, 21)}

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
    "docs/standards/developer-tooling/schemas/golden-path-exceptions-v1.schema.json",
    "docs/standards/developer-tooling/schemas/golden-path-checker-output-v1.schema.json",
    "docs/standards/developer-tooling/schemas/golden-path-rule-catalog-v1.schema.json",
    "docs/standards/developer-tooling/schemas/runtime-support-v1.schema.json",
    "docs/standards/developer-tooling/schemas/examples/golden-path-metadata-v1.valid.json",
    "docs/standards/developer-tooling/schemas/examples/golden-path-exceptions-v1.valid.json",
    "docs/standards/developer-tooling/schemas/examples/golden-path-checker-output-v1.valid.json",
    "docs/guides/adopting-developer-tooling.md",
    "docs/guides/migrating-developer-tooling.md",
    "docs/decisions/0006-adopt-developer-tooling-golden-path.md",
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


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        report(f"{path.relative_to(REPO_ROOT)}: invalid JSON: {error}")
        return None


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

        expected = expected_versions.get(path.name)
        schema_version = data.get("properties", {}).get("schemaVersion", {})
        if schema_version.get("const") != expected:
            report(
                f"{context}: schemaVersion const must be {expected!r}"
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
        report(f"{context}: expected an ISO date")
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        report(f"{context}: expected an ISO date")
        return None


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
        if rule["introducedIn"] != STANDARD_VERSION:
            report(
                f"{item_context}.introducedIn: initial catalog must use "
                f"{STANDARD_VERSION}"
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
        selectors: set[str] = set()
        for version_index, version in enumerate(versions):
            version_context = f"{item_context}.versions[{version_index}]"
            if not require_keys(
                version,
                {
                    "selector",
                    "upstreamLifecycle",
                    "organizationDisposition",
                    "migrationState",
                },
                version_context,
            ):
                continue
            selector = version["selector"]
            if not isinstance(selector, str) or selector in selectors:
                report(f"{version_context}.selector: must be a unique string")
            else:
                selectors.add(selector)
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

    python_selectors = {
        item["selector"]: item
        for item in data["profiles"].get("python", {}).get("versions", [])
        if isinstance(item, dict) and "selector" in item
    }
    if python_selectors.get("3.11", {}).get(
        "organizationDisposition"
    ) != "supported":
        report(f"{context}: Python 3.11 must remain supported in 2026.07")
    if python_selectors.get("3.10", {}).get("supportEndsAt") != "2026-10-31":
        report(
            f"{context}: Python 3.10 compatibility window must end 2026-10-31"
        )
    if data["profiles"].get("rust", {}).get("policy", {}).get(
        "graceDays"
    ) != 90:
        report(f"{context}: Rust N-1/N-2 grace must be 90 days")
    zig_selectors = {
        item.get("selector")
        for item in data["profiles"].get("zig", {}).get("versions", [])
        if isinstance(item, dict)
    }
    if "0.16.0" not in zig_selectors:
        report(f"{context}: Zig 0.16.0 baseline is missing")


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
        r"\b(?:fiftyten-indicators-core|indicator-data-collector|"
        r"indicator-ecs-infra|5010-indicator-server)\b": "product repository",
    }
    for path in sorted(STANDARD_ROOT.rglob("*.md")):
        source = path.read_text(encoding="utf-8")
        for pattern, label in forbidden_patterns.items():
            if re.search(pattern, source, re.IGNORECASE):
                report(
                    f"{path.relative_to(REPO_ROOT)}: central standard contains "
                    f"a repository-coupled {label}"
                )


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
    validate_metadata_example()
    validate_exceptions_example()
    validate_checker_example()
    validate_rule_catalog()
    validate_runtime_catalog()
    validate_traceability_and_scope()

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
