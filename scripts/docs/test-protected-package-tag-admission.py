#!/usr/bin/env python3
"""Repository-owned regression tests for protected package-tag admission."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).with_name("check-protected-package-tag-admission.py")
CONTRACT_PATH = Path(".github/release-policy/protected-package-tag.v1.json")
EXAMPLE_PROFILE = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/examples/protected-package-tag-profile-v1.valid.json"
)
EXAMPLE_INTENT = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/examples/package-release-intent-v1.valid.json"
)
PROFILE_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/protected-package-tag-profile-v1.schema.json"
)


class AdmissionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="protected-package-tag-test.")
        self.repo = Path(self.temporary.name)
        self.git("init", "-b", "dev")
        self.git("config", "user.name", "Release Contract Test")
        self.git("config", "user.email", "release-contract@example.invalid")

        self.write_json(CONTRACT_PATH, self.profile())
        self.write_json(Path("packages/browser/package.json"), {"name": "@example/browser-package", "version": "1.4.0-next.0"})
        self.write(Path("packages/browser/CHANGELOG.md"), "# Changelog\n")
        self.write(Path("docs/browser-package.md"), "# Browser package contract\n")
        self.write(Path("docs/release-support/record.md"), "release support evidence\n" * 12)
        self.write(Path(".github/workflows/validate-browser-package.yml"), "name: validate\non: pull_request\n")
        self.write(Path(".github/workflows/publish-browser-package.yml"), "name: publish\non: push\n")
        self.write(Path("services/calculator/service.txt"), "calculator\n")
        self.base = self.commit("base repository contract")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def profile(self) -> dict[str, Any]:
        return json.loads(EXAMPLE_PROFILE.read_text(encoding="utf-8"))

    def intent(self, version: str, base: str, channel: str = "prerelease") -> dict[str, Any]:
        intent = json.loads(EXAMPLE_INTENT.read_text(encoding="utf-8"))
        intent["channel"] = channel
        intent["version"] = version
        intent["source"]["baseCommit"] = base
        return intent

    def write(self, path: Path, content: str) -> None:
        destination = self.repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    def write_json(self, path: Path, content: Any) -> None:
        self.write(path, json.dumps(content, indent=2, sort_keys=True) + "\n")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        return result.stdout.strip()

    def commit(self, message: str) -> str:
        self.git("add", "--all")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def add_historical_intent(self, path: str, version: str = "1.4.0-next.1") -> None:
        self.write(
            Path(f".github/release-intents/{path}"),
            json.dumps(self.intent(version, self.base), separators=(",", ":")) + "\n",
        )
        self.base = self.commit("record historical release intent")

    def prepare_release(
        self,
        *,
        channel: str = "prerelease",
        manifest_version: str = "1.4.0-next.1",
        intent_version: str | None = None,
        source_base: str | None = None,
        second_intent: bool = False,
        mutate_sibling: bool = False,
        mutate_manifest_metadata: bool = False,
        unrelated_change: bool = False,
        remove_contract: bool = False,
        delete_release_support: bool = False,
        rename_release_support: bool = False,
        copy_release_support: bool = False,
    ) -> str:
        package = {"name": "@example/browser-package", "version": manifest_version}
        if mutate_manifest_metadata:
            package["description"] = "not a version-only change"
        self.write_json(Path("packages/browser/package.json"), package)
        self.write(Path("packages/browser/CHANGELOG.md"), f"# Changelog\n\n- Release {manifest_version}\n")
        intent = self.intent(intent_version or manifest_version, source_base or self.base, channel)
        self.write_json(Path(f".github/release-intents/{manifest_version}.json"), intent)
        if second_intent:
            duplicate = dict(intent)
            duplicate["version"] = "1.4.0-next.2"
            self.write_json(Path(".github/release-intents/second.json"), duplicate)
        if mutate_sibling:
            self.write(Path("services/calculator/service.txt"), "mutated calculator\n")
        if unrelated_change:
            self.write(Path("README.md"), "unrelated\n")
        if remove_contract:
            (self.repo / CONTRACT_PATH).unlink()
        if delete_release_support:
            (self.repo / "docs/release-support/record.md").unlink()
        if rename_release_support:
            self.git("mv", "docs/release-support/record.md", "docs/release-support/renamed.md")
        if copy_release_support:
            support = (self.repo / "docs/release-support/record.md").read_text(encoding="utf-8")
            self.write(Path("docs/release-support/copied.md"), support)
        return self.commit("prepare package release")

    def prepare_toml_release(self, version: str = "1.4.0-next.1") -> str:
        self.write(
            Path("packages/browser/pyproject.toml"),
            f'[project]\nname = "@example/browser-package"\nversion = "{version}"\n',
        )
        self.write(Path("packages/browser/CHANGELOG.md"), f"# Changelog\n\n- Release {version}\n")
        self.write_json(Path(f".github/release-intents/{version}.json"), self.intent(version, self.base))
        return self.commit("prepare TOML package release")

    def check(self, head: str, *, base: str | None = None, ref: str = "refs/heads/dev") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--repository",
                str(self.repo),
                "--base",
                base or self.base,
                "--head",
                head,
                "--event-ref",
                ref,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def assert_rejected(self, result: subprocess.CompletedProcess[str], fragment: str) -> None:
        self.assertNotEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn(fragment, result.stderr)

    def test_admits_exact_prerelease_diff(self) -> None:
        head = self.prepare_release()
        result = self.check(head)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        admitted = json.loads(result.stdout)
        self.assertEqual(admitted["version"], "1.4.0-next.1")
        self.assertEqual(admitted["distTag"], "next")
        self.assertEqual(admitted["tag"], "browser-package-v1.4.0-next.1")
        self.assertEqual(admitted["source"]["commit"], head)

    def test_admits_new_final_version(self) -> None:
        head = self.prepare_release(channel="final", manifest_version="1.4.0")
        result = self.check(head)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        admitted = json.loads(result.stdout)
        self.assertEqual(admitted["channel"], "final")
        self.assertEqual(admitted["distTag"], "latest")

    def test_admits_toml_native_manifest(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["versionSource"] = {
            "type": "toml-key",
            "path": "packages/browser/pyproject.toml",
            "versionKey": "project.version",
            "packageNameKey": "project.name",
        }
        profile["releaseUnit"]["releasePreparationPaths"] = [
            ".github/release-intents/*.json",
            "packages/browser/pyproject.toml",
            "packages/browser/CHANGELOG.md",
        ]
        self.write_json(CONTRACT_PATH, profile)
        self.write(
            Path("packages/browser/pyproject.toml"),
            '[project]\nname = "@example/browser-package"\nversion = "1.4.0-next.0"\n',
        )
        self.base = self.commit("select TOML native manifest")

        result = self.check(self.prepare_toml_release())
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(json.loads(result.stdout)["version"], "1.4.0-next.1")

    def test_rejects_stale_source_boundary(self) -> None:
        head = self.prepare_release(source_base="1" * 40)
        self.assert_rejected(self.check(head), "release intent is stale")

    def test_rejects_multiple_intents(self) -> None:
        head = self.prepare_release(second_intent=True)
        self.assert_rejected(self.check(head), "exactly one release intent change")

    def test_rejects_duplicate_historical_identity(self) -> None:
        self.add_historical_intent("historical.json")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "duplicate or conflicting release intent")

    def test_rejects_modified_historical_intent(self) -> None:
        self.add_historical_intent("1.4.0-next.1.json")
        historical = json.loads((self.repo / ".github/release-intents/1.4.0-next.1.json").read_text(encoding="utf-8"))
        historical["source"]["baseCommit"] = self.base
        self.write_json(Path(".github/release-intents/1.4.0-next.1.json"), historical)
        self.write_json(Path("packages/browser/package.json"), {"name": "@example/browser-package", "version": "1.4.0-next.1"})
        self.write(Path("packages/browser/CHANGELOG.md"), "# Changelog\n\n- Release 1.4.0-next.1\n")
        head = self.commit("modify existing release intent")
        self.assert_rejected(self.check(head), "release intent must be newly added")

    def test_rejects_channel_version_conflict(self) -> None:
        head = self.prepare_release(channel="prerelease", manifest_version="1.4.0")
        self.assert_rejected(self.check(head), "prerelease channel requires")

    def test_rejects_intent_manifest_mismatch(self) -> None:
        head = self.prepare_release(intent_version="1.4.0-next.2")
        self.assert_rejected(self.check(head), "does not match the head manifest")

    def test_rejects_non_version_manifest_mutation(self) -> None:
        head = self.prepare_release(mutate_manifest_metadata=True)
        self.assert_rejected(self.check(head), "changed outside the configured version field")

    def test_rejects_contract_package_name_mismatch(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["packageName"] = "@example/wrong-package"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("misconfigure package identity")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "native manifest package name does not match")

    def test_rejects_sibling_release_unit_mutation(self) -> None:
        head = self.prepare_release(mutate_sibling=True)
        self.assert_rejected(self.check(head), "sibling release-unit mutation is forbidden")

    def test_rejects_path_outside_release_preparation(self) -> None:
        head = self.prepare_release(unrelated_change=True)
        self.assert_rejected(self.check(head), "outside release preparation")

    def test_rejects_deletion_within_release_preparation(self) -> None:
        head = self.prepare_release(delete_release_support=True)
        self.assert_rejected(self.check(head), "may only add or modify files")

    def test_rejects_rename_within_release_preparation(self) -> None:
        head = self.prepare_release(rename_release_support=True)
        self.assert_rejected(self.check(head), "may only add or modify files")

    def test_rejects_copy_within_release_preparation(self) -> None:
        head = self.prepare_release(copy_release_support=True)
        self.assert_rejected(self.check(head), "may only add or modify files")

    def test_profile_is_explicit_opt_in(self) -> None:
        head = self.prepare_release(remove_contract=True)
        self.assert_rejected(self.check(head), "opt-in profile contract is missing")

    def test_rejects_weakened_minimum_permissions(self) -> None:
        profile = self.profile()
        profile["minimumPermissions"]["validation"] = []
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("weaken profile permissions")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "least-privilege contract")

    def test_rejects_glob_in_plain_manifest_path(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["versionSource"]["path"] = "packages/*/package.json"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("misconfigure native manifest path")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "must not contain glob syntax")

    def test_rejects_non_https_registry(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["registry"] = "http://packages.example.invalid"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("misconfigure registry transport")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "must use https")

    def test_schema_matches_checker_path_and_registry_boundaries(self) -> None:
        schema = json.loads(PROFILE_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["intentDirectory"]["$ref"], "#/$defs/plainRelativePath")
        self.assertEqual(schema["$defs"]["pathPatterns"]["items"]["$ref"], "#/$defs/pathPattern")
        self.assertEqual(schema["properties"]["releaseUnit"]["properties"]["registry"]["pattern"], "^https://")


if __name__ == "__main__":
    unittest.main()
