#!/usr/bin/env python3
"""Repository-owned regression tests for protected package-tag admission."""

from __future__ import annotations

import json
import re
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
EXAMPLE_RECOVERY_INTENT = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/examples/package-release-recovery-intent-v1.valid.json"
)
EXAMPLE_TAG_ONLY_COMPLETION_INTENT = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/examples/package-release-tag-only-completion-intent-v1.valid.json"
)
PROFILE_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/protected-package-tag-profile-v1.schema.json"
)
INTENT_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/package-release-intent-v1.schema.json"
)
RECOVERY_INTENT_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/package-release-recovery-intent-v1.schema.json"
)
TAG_ONLY_COMPLETION_INTENT_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "docs/standards/release-versioning/schemas/package-release-tag-only-completion-intent-v1.schema.json"
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
        self.write(Path(".github/workflows/complete-browser-package.yml"), "name: complete\non: push\n")
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

    def recovery_intent(
        self,
        *,
        version: str,
        original_intent_path: str,
        failed_source: str,
        source_base: str,
        channel: str = "prerelease",
        run_id: int = 123456789,
    ) -> dict[str, Any]:
        intent = json.loads(EXAMPLE_RECOVERY_INTENT.read_text(encoding="utf-8"))
        intent["channel"] = channel
        intent["version"] = version
        intent["originalIntentPath"] = original_intent_path
        intent["failedAttempt"]["sourceCommit"] = failed_source
        intent["failedAttempt"]["workflowRunUrl"] = (
            f"https://github.com/example/repository/actions/runs/{run_id}"
        )
        intent["source"]["baseCommit"] = source_base
        return intent

    def tag_only_completion_intent(
        self,
        *,
        version: str,
        original_intent_path: str,
        failed_source: str,
        source_base: str,
        authorization_type: str,
        authorization_path: str,
        channel: str = "prerelease",
        run_id: int = 234567890,
    ) -> dict[str, Any]:
        intent = json.loads(
            EXAMPLE_TAG_ONLY_COMPLETION_INTENT.read_text(encoding="utf-8")
        )
        intent["channel"] = channel
        intent["version"] = version
        intent["originalIntentPath"] = original_intent_path
        intent["tag"] = f"browser-package-v{version}"
        intent["distTag"] = "next" if channel == "prerelease" else "latest"
        intent["failedPublication"]["sourceCommit"] = failed_source
        intent["failedPublication"]["workflowRunUrl"] = (
            f"https://github.com/example/repository/actions/runs/{run_id}"
        )
        intent["failedPublication"]["authorization"] = {
            "type": authorization_type,
            "path": authorization_path,
        }
        intent["retainedArtifact"]["artifactId"] = run_id
        intent["retainedArtifact"]["artifactName"] = (
            f"example-browser-package-{version}"
        )
        intent["retainedArtifact"]["tarballFileName"] = (
            f"example-browser-package-{version}.tgz"
        )
        intent["retainedArtifact"]["embeddedSourceCommit"] = failed_source
        intent["source"]["baseCommit"] = source_base
        return intent

    def write(self, path: Path, content: str) -> None:
        destination = self.repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    def write_json(self, path: Path, content: Any) -> None:
        self.write(path, json.dumps(content, indent=2, sort_keys=True) + "\n")

    def write_bytes(self, path: Path, content: bytes) -> None:
        destination = self.repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    def write_symlink(self, path: Path, target: str) -> None:
        destination = self.repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(target)

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
        self.write_json(Path(f".github/release-intents/{path}"), self.intent(version, self.base))
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
        modify_release_support: bool = False,
        deep_release_support: bool = False,
        typechange_release_support: bool = False,
        utf16_intent: bool = False,
        duplicate_intent_key: bool = False,
        nonstandard_intent_number: bool = False,
        symlink_intent: bool = False,
        control_character_path: bool = False,
    ) -> str:
        package = {"name": "@example/browser-package", "version": manifest_version}
        if mutate_manifest_metadata:
            package["description"] = "not a version-only change"
        self.write_json(Path("packages/browser/package.json"), package)
        self.write(Path("packages/browser/CHANGELOG.md"), f"# Changelog\n\n- Release {manifest_version}\n")
        intent = self.intent(intent_version or manifest_version, source_base or self.base, channel)
        intent_path = Path(f".github/release-intents/{manifest_version}.json")
        if utf16_intent:
            self.write_bytes(intent_path, (json.dumps(intent, indent=2, sort_keys=True) + "\n").encode("utf-16"))
        elif duplicate_intent_key:
            encoded = json.dumps(intent, indent=2, sort_keys=True) + "\n"
            channel_line = f'  "channel": "{channel}",'
            self.write(intent_path, encoded.replace(channel_line, f"{channel_line}\n{channel_line}", 1))
        elif nonstandard_intent_number:
            encoded = json.dumps(intent, indent=2, sort_keys=True) + "\n"
            version_line = f'  "version": "{intent["version"]}"'
            self.write(intent_path, encoded.replace(version_line, '  "version": NaN', 1))
        elif symlink_intent:
            self.write_symlink(intent_path, json.dumps(intent, separators=(",", ":")))
        else:
            self.write_json(intent_path, intent)
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
        if modify_release_support:
            self.write(Path("docs/release-support/record.md"), "updated release support evidence\n")
        if deep_release_support:
            self.write(Path("docs/release-support/nested/record.md"), "nested release support evidence\n")
        if typechange_release_support:
            support_path = self.repo / "docs/release-support/record.md"
            support_path.unlink()
            support_path.symlink_to("missing-release-support")
        if control_character_path:
            self.write(Path("docs/release-support/bad\nname.md"), "ambiguous release support path\n")
        return self.commit("prepare package release")

    def prepare_toml_release(self, version: str = "1.4.0-next.1") -> str:
        self.write(
            Path("packages/browser/pyproject.toml"),
            f'[project]\nname = "@example/browser-package"\nversion = "{version}"\n',
        )
        self.write(Path("packages/browser/CHANGELOG.md"), f"# Changelog\n\n- Release {version}\n")
        self.write_json(Path(f".github/release-intents/{version}.json"), self.intent(version, self.base))
        return self.commit("prepare TOML package release")

    def materialize_failed_release(
        self, *, version: str = "1.4.0-next.1", channel: str = "prerelease"
    ) -> tuple[str, str]:
        failed_source = self.prepare_release(channel=channel, manifest_version=version)
        result = self.check(failed_source)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.base = failed_source
        return failed_source, f".github/release-intents/{version}.json"

    def prepare_recovery(
        self,
        *,
        version: str = "1.4.0-next.1",
        channel: str = "prerelease",
        original_intent_path: str | None = None,
        failed_source: str | None = None,
        source_base: str | None = None,
        run_id: int = 123456789,
        recovery_name: str = "recovery-1.json",
        second_recovery: bool = False,
        mutate_sibling: bool = False,
        unrelated_change: bool = False,
    ) -> str:
        recovery = self.recovery_intent(
            version=version,
            original_intent_path=original_intent_path
            or f".github/release-intents/{version}.json",
            failed_source=failed_source or self.base,
            source_base=source_base or self.base,
            channel=channel,
            run_id=run_id,
        )
        self.write_json(Path(f".github/release-recovery-intents/{recovery_name}"), recovery)
        if second_recovery:
            second = json.loads(json.dumps(recovery))
            second["failedAttempt"]["workflowRunUrl"] = (
                "https://github.com/example/repository/actions/runs/987654321"
            )
            self.write_json(
                Path(".github/release-recovery-intents/recovery-2.json"), second
            )
        if mutate_sibling:
            self.write(Path("services/calculator/service.txt"), "mutated calculator\n")
        if unrelated_change:
            self.write(Path("README.md"), "unrelated recovery change\n")
        return self.commit("authorize package release recovery")

    def prepare_tag_only_completion(
        self,
        *,
        version: str = "1.4.0-next.1",
        channel: str = "prerelease",
        original_intent_path: str,
        failed_source: str,
        authorization_type: str,
        authorization_path: str,
        source_base: str | None = None,
        run_id: int = 234567890,
        completion_name: str = "completion-1.json",
        second_completion: bool = False,
        unrelated_change: bool = False,
    ) -> str:
        completion = self.tag_only_completion_intent(
            version=version,
            original_intent_path=original_intent_path,
            failed_source=failed_source,
            source_base=source_base or self.base,
            authorization_type=authorization_type,
            authorization_path=authorization_path,
            channel=channel,
            run_id=run_id,
        )
        self.write_json(
            Path(f".github/release-tag-only-completion-intents/{completion_name}"),
            completion,
        )
        if second_completion:
            duplicate = json.loads(json.dumps(completion))
            duplicate["failedPublication"]["workflowRunUrl"] = (
                "https://github.com/example/repository/actions/runs/345678901"
            )
            self.write_json(
                Path(".github/release-tag-only-completion-intents/completion-2.json"),
                duplicate,
            )
        if unrelated_change:
            self.write(Path("README.md"), "unrelated tag-only completion change\n")
        return self.commit("authorize tag-only package completion")

    def materialize_tag_only_recovery_source(
        self,
    ) -> tuple[str, str, str]:
        failed_source, original_path = self.materialize_failed_release()
        recovery_path = ".github/release-recovery-intents/recovery-1.json"
        recovery_source = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
        )
        self.assertEqual(self.check(recovery_source).returncode, 0)
        self.base = recovery_source
        return recovery_source, original_path, recovery_path

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

    def test_admits_successive_release_with_historical_intent(self) -> None:
        first_head = self.prepare_release(manifest_version="1.4.0-next.1")
        self.assertEqual(self.check(first_head).returncode, 0)
        self.base = first_head

        second_head = self.prepare_release(manifest_version="1.4.0-next.2")
        second_result = self.check(second_head)
        self.assertEqual(second_result.returncode, 0, msg=second_result.stderr)
        self.assertEqual(json.loads(second_result.stdout)["version"], "1.4.0-next.2")

    def test_admits_numeric_prerelease_progression(self) -> None:
        self.write_json(
            Path("packages/browser/package.json"),
            {"name": "@example/browser-package", "version": "1.4.0-next.2"},
        )
        self.base = self.commit("materialize numeric prerelease predecessor")
        result = self.check(self.prepare_release(manifest_version="1.4.0-next.10"))
        self.assertEqual(result.returncode, 0, msg=result.stderr)

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

    def test_admits_direct_child_for_single_segment_pattern(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["releasePreparationPaths"][-1] = "docs/release-support/*.md"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("select single-segment support pattern")

        result = self.check(self.prepare_release(modify_release_support=True))
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_admits_nested_child_for_recursive_pattern(self) -> None:
        result = self.check(self.prepare_release(deep_release_support=True))
        self.assertEqual(result.returncode, 0, msg=result.stderr)

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

    def test_rejects_semver_downgrade(self) -> None:
        self.write_json(
            Path("packages/browser/package.json"),
            {"name": "@example/browser-package", "version": "2.0.0"},
        )
        self.base = self.commit("materialize later package version")
        head = self.prepare_release(channel="final", manifest_version="1.9.9")
        self.assert_rejected(self.check(head), "greater SemVer precedence")

    def test_rejects_build_metadata_only_version_change(self) -> None:
        self.write_json(
            Path("packages/browser/package.json"),
            {"name": "@example/browser-package", "version": "1.4.0+build.1"},
        )
        self.base = self.commit("materialize package build metadata")
        head = self.prepare_release(channel="final", manifest_version="1.4.0+build.2")
        self.assert_rejected(self.check(head), "greater SemVer precedence")

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

    def test_rejects_nested_child_for_single_segment_pattern(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["releasePreparationPaths"][-1] = "docs/release-support/*.md"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("select single-segment support pattern")
        head = self.prepare_release(deep_release_support=True)
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

    def test_rejects_typechange_within_release_preparation(self) -> None:
        head = self.prepare_release(typechange_release_support=True)
        self.assert_rejected(self.check(head), "may only add or modify files")

    def test_rejects_symlink_release_intent(self) -> None:
        head = self.prepare_release(symlink_intent=True)
        self.assert_rejected(self.check(head), "must be a regular file")

    def test_rejects_utf16_release_intent(self) -> None:
        head = self.prepare_release(utf16_intent=True)
        self.assert_rejected(self.check(head), "not valid UTF-8 JSON")

    def test_rejects_duplicate_json_key(self) -> None:
        head = self.prepare_release(duplicate_intent_key=True)
        self.assert_rejected(self.check(head), "duplicate object key")

    def test_rejects_nonstandard_json_number(self) -> None:
        head = self.prepare_release(nonstandard_intent_number=True)
        self.assert_rejected(self.check(head), "non-standard numeric constant")

    def test_rejects_non_intent_file_in_intent_directory(self) -> None:
        self.write(Path(".github/release-intents/README.md"), "not a release intent\n")
        self.base = self.commit("add invalid intent directory entry")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "not valid UTF-8 JSON")

    def test_profile_is_explicit_opt_in(self) -> None:
        head = self.prepare_release(remove_contract=True)
        self.assert_rejected(self.check(head), "opt-in profile contract is missing")

    def test_rejects_profile_without_recovery_contract(self) -> None:
        profile = self.profile()
        profile.pop("recovery")
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("omit recovery contract")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "missing required fields: recovery")

    def test_rejects_overlapping_release_and_recovery_directories(self) -> None:
        profile = self.profile()
        profile["recovery"]["intentDirectory"] = ".github/release-intents/recovery"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("overlap release authorization directories")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "must be distinct and non-overlapping")

    def test_rejects_release_paths_that_admit_recovery_records(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["releasePreparationPaths"].append(
            ".github/release-recovery-intents/*.json"
        )
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("admit recovery records as release preparation")
        head = self.prepare_release()
        self.assert_rejected(
            self.check(head), "must not admit recovery authorization records"
        )

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

    def test_rejects_git_pathspec_magic(self) -> None:
        profile = self.profile()
        profile["intentDirectory"] = ":(exclude)release-intents"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("misconfigure intent directory pathspec")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "must not use Git pathspec magic")

    def test_rejects_control_character_in_plain_path(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["changelog"] = "packages/browser/CHANGELOG.md\nother"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("misconfigure changelog path")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "must not contain control characters")

    def test_rejects_control_character_in_changed_path(self) -> None:
        head = self.prepare_release(control_character_path=True)
        self.assert_rejected(self.check(head), "changed path must not contain control characters")

    def test_rejects_hidden_stem_workflow(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["validationWorkflow"] = ".github/workflows/.yml"
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("misconfigure validation workflow")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "top-level repository workflow")

    def test_rejects_invalid_derived_tag(self) -> None:
        head = self.prepare_release(channel="final", manifest_version="1.4.0+release.lock")
        self.assert_rejected(self.check(head), "derived package tag is not a valid Git tag")

    def test_admits_same_version_pre_mutation_recovery(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        result = self.check(head)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        admitted = json.loads(result.stdout)
        self.assertEqual(
            admitted["schemaVersion"],
            "protected-package-tag-recovery-admission/v1",
        )
        self.assertEqual(admitted["version"], "1.4.0-next.1")
        self.assertEqual(admitted["tag"], "browser-package-v1.4.0-next.1")
        self.assertEqual(admitted["originalIntentPath"], original_path)
        self.assertEqual(admitted["source"]["commit"], head)

    def test_admits_new_record_after_second_pre_mutation_failure(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        first_head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            run_id=123456789,
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        self.base = first_head
        second_head = self.prepare_recovery(
            failed_source=first_head,
            original_intent_path=original_path,
            run_id=987654321,
            recovery_name="recovery-2.json",
        )
        result = self.check(second_head)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(json.loads(result.stdout)["failedAttempt"]["sourceCommit"], first_head)

    def test_recovery_preserves_original_intent_bytes(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        before = self.git("show", f"{failed_source}:{original_path}")
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assertEqual(self.check(head).returncode, 0)
        self.assertEqual(before, self.git("show", f"{head}:{original_path}"))

    def test_rejects_stale_recovery_base(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            source_base="1" * 40,
        )
        self.assert_rejected(self.check(head), "release recovery intent is stale")

    def test_rejects_recovery_ref_mismatch(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assert_rejected(
            self.check(head, ref="refs/heads/main"),
            "event ref does not match the profile source ref",
        )

    def test_rejects_failed_source_off_first_parent_history(self) -> None:
        release_base = self.base
        self.git("switch", "-c", "side-release")
        failed_source = self.prepare_release()
        self.assertEqual(self.check(failed_source, base=release_base).returncode, 0)
        self.git("switch", "dev")
        self.git(
            "merge",
            "--no-ff",
            "side-release",
            "-m",
            "merge side release as second parent",
        )
        self.base = self.git("rev-parse", "HEAD")
        original_path = ".github/release-intents/1.4.0-next.1.json"
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assert_rejected(self.check(head), "protected source first-parent history")

    def test_rejects_recovery_manifest_version_mismatch(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        self.write_json(
            Path("packages/browser/package.json"),
            {"name": "@example/browser-package", "version": "1.4.0-next.2"},
        )
        self.base = self.commit("drift package version after failed publication")
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assert_rejected(
            self.check(head), "recovery version does not match the unchanged native manifest"
        )

    def test_rejects_missing_original_release_intent(self) -> None:
        failed_source, _original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=".github/release-intents/missing.json",
        )
        self.assert_rejected(self.check(head), "original release intent is missing")

    def test_rejects_ambiguous_original_release_intent(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        duplicate = self.intent("1.4.0-next.1", "0" * 40)
        self.write_json(Path(".github/release-intents/duplicate.json"), duplicate)
        self.base = self.commit("add ambiguous historical release intent")
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assert_rejected(self.check(head), "missing or ambiguous")

    def test_rejects_modified_original_release_intent(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        intent_file = self.repo / original_path
        self.write(Path(original_path), intent_file.read_text(encoding="utf-8") + "\n")
        self.base = self.commit("rewrite historical release intent bytes")
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assert_rejected(self.check(head), "must remain byte-identical")

    def test_rejects_deleted_and_restored_original_release_intent(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        original_bytes = (self.repo / original_path).read_bytes()
        (self.repo / original_path).unlink()
        self.base = self.commit("delete historical release intent")
        self.write_bytes(Path(original_path), original_bytes)
        self.base = self.commit("restore historical release intent")
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assert_rejected(
            self.check(head), "must remain append-only in protected source history"
        )

    def test_rejects_renamed_and_restored_original_release_intent(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        temporary_path = ".github/release-intents/temporarily-renamed.json"
        self.git("mv", original_path, temporary_path)
        self.base = self.commit("rename historical release intent")
        self.git("mv", temporary_path, original_path)
        self.base = self.commit("restore historical release intent path")
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assert_rejected(
            self.check(head), "must remain append-only in protected source history"
        )

    def test_rejects_multiple_recovery_authorizations(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            second_recovery=True,
        )
        self.assert_rejected(self.check(head), "exactly one recovery record")

    def test_rejects_reused_recovery_authorization(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        first_head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        self.base = first_head
        path = Path(".github/release-recovery-intents/recovery-1.json")
        reused = json.loads((self.repo / path).read_text(encoding="utf-8"))
        reused["$schema"] = "package-release-recovery-intent-v1.schema.json"
        self.write_json(path, reused)
        head = self.commit("reuse recovery authorization")
        self.assert_rejected(self.check(head), "modification, rename, copy, or deletion is reuse")

    def test_rejects_duplicate_authorization_for_failed_attempt(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        first_head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        self.base = first_head
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            recovery_name="recovery-2.json",
        )
        self.assert_rejected(self.check(head), "duplicate recovery authorization")

    def test_rejects_same_failed_source_with_different_run(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        first_head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            run_id=123456789,
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        self.base = first_head
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            run_id=987654321,
            recovery_name="recovery-2.json",
        )
        self.assert_rejected(self.check(head), "same failed publication source")

    def test_rejects_unrelated_commit_as_initial_failed_source(self) -> None:
        _failed_source, original_path = self.materialize_failed_release()
        self.write(Path("README.md"), "unrelated protected-source commit\n")
        unrelated_source = self.commit("add unrelated commit after failed attempt")
        self.base = unrelated_source
        head = self.prepare_recovery(
            failed_source=unrelated_source, original_intent_path=original_path
        )
        self.assert_rejected(
            self.check(head),
            "failed publication source must be the exact commit that added the original release intent",
        )

    def test_rejects_unrelated_commit_after_prior_recovery_as_failed_source(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        first_head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        self.write(Path("README.md"), "unrelated commit after recovery\n")
        unrelated_source = self.commit("add unrelated commit after recovery")
        self.base = unrelated_source
        head = self.prepare_recovery(
            failed_source=unrelated_source,
            original_intent_path=original_path,
            run_id=987654321,
            recovery_name="recovery-2.json",
        )
        self.assert_rejected(
            self.check(head), "exact source authorized by the latest recovery record"
        )

    def test_rejects_modified_and_restored_recovery_authorization(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        first_head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        recovery_path = Path(".github/release-recovery-intents/recovery-1.json")
        original_bytes = (self.repo / recovery_path).read_bytes()
        recovery = json.loads(original_bytes)
        recovery["failedAttempt"]["workflowRunUrl"] = (
            "https://github.com/example/repository/actions/runs/111111111"
        )
        self.write_json(recovery_path, recovery)
        self.base = self.commit("modify historical recovery authorization")
        self.write_bytes(recovery_path, original_bytes)
        self.base = self.commit("restore historical recovery authorization")
        head = self.prepare_recovery(
            failed_source=first_head,
            original_intent_path=original_path,
            run_id=987654321,
            recovery_name="recovery-2.json",
        )
        self.assert_rejected(
            self.check(head), "recovery intent directory must remain append-only"
        )

    def test_rejects_renamed_and_restored_recovery_authorization(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        first_head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        recovery_path = ".github/release-recovery-intents/recovery-1.json"
        temporary_path = ".github/release-recovery-intents/temporarily-renamed.json"
        self.git("mv", recovery_path, temporary_path)
        self.base = self.commit("rename historical recovery authorization")
        self.git("mv", temporary_path, recovery_path)
        self.base = self.commit("restore historical recovery authorization path")
        head = self.prepare_recovery(
            failed_source=first_head,
            original_intent_path=original_path,
            run_id=987654321,
            recovery_name="recovery-2.json",
        )
        self.assert_rejected(
            self.check(head), "recovery intent directory must remain append-only"
        )

    def test_rejects_release_and_recovery_intents_in_one_diff(self) -> None:
        version = "1.4.0-next.1"
        original_path = f".github/release-intents/{version}.json"
        self.write_json(
            Path("packages/browser/package.json"),
            {"name": "@example/browser-package", "version": version},
        )
        self.write(
            Path("packages/browser/CHANGELOG.md"),
            f"# Changelog\n\n- Release {version}\n",
        )
        self.write_json(Path(original_path), self.intent(version, self.base))
        self.write_json(
            Path(".github/release-recovery-intents/recovery-1.json"),
            self.recovery_intent(
                version=version,
                original_intent_path=original_path,
                failed_source=self.base,
                source_base=self.base,
            ),
        )
        head = self.commit("mix release and recovery authorization")
        self.assert_rejected(
            self.check(head),
            "release, recovery, and tag-only completion authorizations cannot share",
        )

    def test_rejects_recovery_with_unrelated_change(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            unrelated_change=True,
        )
        self.assert_rejected(self.check(head), "no other paths")

    def test_rejects_recovery_with_sibling_mutation(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
            mutate_sibling=True,
        )
        self.assert_rejected(self.check(head), "no other paths")

    def test_rejects_recovery_directory_overlapping_sibling_mutation(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        profile = json.loads((self.repo / CONTRACT_PATH).read_text(encoding="utf-8"))
        profile["siblingReleaseUnits"][0]["mutationPaths"].append(
            ".github/release-recovery-intents/**"
        )
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("overlap recovery and sibling mutation paths")
        head = self.prepare_recovery(
            failed_source=failed_source,
            original_intent_path=original_path,
        )
        self.assert_rejected(
            self.check(head),
            "sibling release-unit mutation is forbidden",
        )

    def test_rejects_recovery_when_tag_is_present(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        recovery = self.recovery_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
        )
        recovery["failedAttempt"]["tagState"] = "present"
        self.write_json(Path(".github/release-recovery-intents/tag-present.json"), recovery)
        self.assert_rejected(
            self.check(self.commit("claim tag-present recovery")),
            "requires the package tag to be absent",
        )

    def test_rejects_recovery_when_registry_version_is_present(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        recovery = self.recovery_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
        )
        recovery["failedAttempt"]["registryVersionState"] = "present"
        self.write_json(Path(".github/release-recovery-intents/registry-present.json"), recovery)
        self.assert_rejected(
            self.check(self.commit("claim registry-present recovery")),
            "requires the registry version to be absent",
        )

    def test_rejects_tag_only_partial_state(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        recovery = self.recovery_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
        )
        recovery["failedAttempt"]["tagState"] = "present"
        recovery["failedAttempt"]["registryVersionState"] = "absent"
        self.write_json(Path(".github/release-recovery-intents/tag-only.json"), recovery)
        self.assert_rejected(self.check(self.commit("claim tag-only state")), "tag to be absent")

    def test_rejects_registry_only_partial_state(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        recovery = self.recovery_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
        )
        recovery["failedAttempt"]["registryVersionState"] = "present"
        self.write_json(Path(".github/release-recovery-intents/registry-only.json"), recovery)
        self.assert_rejected(
            self.check(self.commit("claim registry-only state")), "registry version to be absent"
        )

    def test_rejects_conflicting_immutable_identity(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        recovery = self.recovery_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
        )
        recovery["failedAttempt"]["tagState"] = "conflicting"
        self.write_json(Path(".github/release-recovery-intents/conflict.json"), recovery)
        self.assert_rejected(
            self.check(self.commit("claim conflicting identity")), "tag to be absent"
        )

    def test_rejects_non_terminal_prior_run(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        recovery = self.recovery_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
        )
        recovery["failedAttempt"]["outcome"] = "in-progress"
        self.write_json(Path(".github/release-recovery-intents/non-terminal.json"), recovery)
        self.assert_rejected(
            self.check(self.commit("claim non-terminal recovery")), "terminal failed attempt"
        )

    def test_rejects_mutation_reaching_prior_run(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        recovery = self.recovery_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
        )
        recovery["failedAttempt"]["mutationState"] = "started"
        self.write_json(Path(".github/release-recovery-intents/mutated.json"), recovery)
        self.assert_rejected(
            self.check(self.commit("claim mutation-reaching recovery")),
            "failure before immutable mutation",
        )

    def test_admits_tag_only_completion_from_recovery_source(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        result = self.check(head)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        admitted = json.loads(result.stdout)
        self.assertEqual(
            admitted["schemaVersion"],
            "protected-package-tag-tag-only-completion-admission/v1",
        )
        self.assertEqual(admitted["authorization"], "tag-only-completion")
        self.assertEqual(admitted["packageSource"]["commit"], failed_source)
        self.assertEqual(admitted["authorizationSource"]["commit"], head)
        self.assertEqual(admitted["distTag"], "next")

    def test_admits_tag_only_completion_from_initial_release_source(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="release-intent",
            authorization_path=original_path,
        )
        result = self.check(head)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            json.loads(result.stdout)["failedPublication"]["authorization"]["type"],
            "release-intent",
        )

    def test_rejects_preparation_only_successor_as_initial_failed_source(self) -> None:
        initial_source, original_path = self.materialize_failed_release()
        self.write(
            Path("packages/browser/CHANGELOG.md"),
            "# Changelog\n\n- Polish release notes\n",
        )
        successor = self.commit("polish release notes")
        self.assertNotEqual(initial_source, successor)
        self.base = successor
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=successor,
            authorization_type="release-intent",
            authorization_path=original_path,
        )
        self.assert_rejected(
            self.check(head),
            "failed publication source must be the exact commit that added the original release intent",
        )

    def test_rejects_initial_source_after_later_recovery_authorization(self) -> None:
        initial_source, original_path = self.materialize_failed_release()
        recovery_source = self.prepare_recovery(
            failed_source=initial_source,
            original_intent_path=original_path,
        )
        self.assertEqual(self.check(recovery_source).returncode, 0)
        self.base = recovery_source
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=initial_source,
            authorization_type="release-intent",
            authorization_path=original_path,
        )
        self.assert_rejected(
            self.check(head),
            "failed publication source must be the exact source authorized by the latest recovery record",
        )

    def test_rejects_stale_tag_only_completion_base(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
            source_base="1" * 40,
        )
        self.assert_rejected(self.check(head), "tag-only completion intent is stale")

    def test_rejects_tag_only_completion_run_attempt_two(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["failedPublication"]["runAttempt"] = 2
        self.write_json(
            Path(".github/release-tag-only-completion-intents/run-attempt-2.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim second failed publication attempt")),
            "requires failed publication run attempt 1",
        )

    def test_rejects_tag_only_completion_without_tag(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["failedPublication"]["tagState"] = "absent"
        self.write_json(
            Path(".github/release-tag-only-completion-intents/tag-absent.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim tag-absent completion")),
            "requires the package tag to be present",
        )

    def test_rejects_tag_only_completion_with_registry_version(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["failedPublication"]["registryVersionState"] = "present"
        self.write_json(
            Path(".github/release-tag-only-completion-intents/registry-present.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim registry-present completion")),
            "requires the exact registry version to be absent",
        )

    def test_rejects_tag_only_completion_source_mismatch(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["retainedArtifact"]["embeddedSourceCommit"] = "9" * 40
        self.write_json(
            Path(".github/release-tag-only-completion-intents/source-mismatch.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim mismatched retained source")),
            "retained artifact embedded source does not match",
        )

    def test_rejects_tag_only_completion_tag_mismatch(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["tag"] = "browser-package-v9.9.9"
        self.write_json(
            Path(".github/release-tag-only-completion-intents/tag-mismatch.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim mismatched package tag")),
            "does not match the derived package tag",
        )

    def test_rejects_tag_only_completion_dist_tag_mismatch(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["distTag"] = "latest"
        self.write_json(
            Path(".github/release-tag-only-completion-intents/dist-tag-mismatch.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim mismatched dist-tag")),
            "dist-tag does not match the profile channel",
        )

    def test_rejects_non_rfc3339_retained_artifact_expiry(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["retainedArtifact"]["expiresAt"] = "2026-09-13 00:14:53+00:00"
        self.write_json(
            Path(".github/release-tag-only-completion-intents/non-rfc3339-expiry.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim non-RFC3339 artifact expiry")),
            "expiresAt must be an RFC 3339 date-time",
        )

    def test_rejects_invalid_retained_tarball_sha256(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["retainedArtifact"]["tarballSha256"] = "not-a-digest"
        self.write_json(
            Path(".github/release-tag-only-completion-intents/bad-sha.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim invalid tarball digest")),
            "tarballSha256 must be 64 lowercase hex characters",
        )

    def test_rejects_invalid_retained_npm_integrity(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        completion = self.tag_only_completion_intent(
            version="1.4.0-next.1",
            original_intent_path=original_path,
            failed_source=failed_source,
            source_base=self.base,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        completion["retainedArtifact"]["npmIntegrity"] = "sha512-AAAA"
        self.write_json(
            Path(".github/release-tag-only-completion-intents/bad-integrity.json"),
            completion,
        )
        self.assert_rejected(
            self.check(self.commit("claim invalid npm integrity")),
            "must encode a SHA-512 digest",
        )

    def test_rejects_tag_only_completion_with_unrelated_change(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
            unrelated_change=True,
        )
        self.assert_rejected(self.check(head), "exactly one record and no other paths")

    def test_rejects_multiple_tag_only_completion_records(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
            second_completion=True,
        )
        self.assert_rejected(self.check(head), "exactly one record")

    def test_rejects_second_completion_authorization_for_identity(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        first_head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        self.assertEqual(self.check(first_head).returncode, 0)
        self.base = first_head
        second_head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
            completion_name="completion-2.json",
            run_id=345678901,
        )
        self.assert_rejected(
            self.check(second_head),
            "duplicate tag-only completion authorization exists for the same release-unit and version",
        )

    def test_rejects_modified_failed_recovery_authorization(self) -> None:
        failed_source, original_path, recovery_path = (
            self.materialize_tag_only_recovery_source()
        )
        recovery = json.loads(
            (self.repo / recovery_path).read_text(encoding="utf-8")
        )
        recovery["$schema"] = "rewritten-after-failed-publication"
        self.write_json(Path(recovery_path), recovery)
        self.base = self.commit("rewrite failed publication authorization")
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="pre-mutation-recovery",
            authorization_path=recovery_path,
        )
        self.assert_rejected(
            self.check(head),
            "failed publication recovery authorization must remain byte-identical",
        )

    def test_rejects_profile_without_tag_only_completion_contract(self) -> None:
        profile = self.profile()
        profile.pop("tagOnlyCompletion")
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("omit tag-only completion contract")
        head = self.prepare_release()
        self.assert_rejected(
            self.check(head), "missing required fields: tagOnlyCompletion"
        )

    def test_rejects_weakened_completion_admission_permissions(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["jobPermissions"][
            "admissionAndLiveVerification"
        ].remove("actions: read")
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("weaken completion admission permissions")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "exact job-scoped permissions")

    def test_rejects_broadened_artifact_retrieval_permissions(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["jobPermissions"][
            "retainedArtifactRetrieval"
        ].append("contents: read")
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("broaden artifact retrieval permissions")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "exact job-scoped permissions")

    def test_rejects_broadened_completion_mutation_permissions(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["jobPermissions"][
            "registryMutation"
        ].append("contents: read")
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("broaden completion mutation permissions")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "exact job-scoped permissions")

    def test_rejects_weakened_post_publication_permissions(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["jobPermissions"][
            "postPublicationVerification"
        ].remove("packages: read")
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("weaken post-publication permissions")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "exact job-scoped permissions")

    def test_rejects_reordered_completion_permissions(self) -> None:
        profile = self.profile()
        permissions = profile["tagOnlyCompletion"]["jobPermissions"][
            "admissionAndLiveVerification"
        ]
        permissions[0], permissions[1] = permissions[1], permissions[0]
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("reorder completion permissions")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "exact job-scoped permissions")

    def test_rejects_missing_completion_permission_job(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["jobPermissions"].pop(
            "retainedArtifactRetrieval"
        )
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("omit completion permission job")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "exact job-scoped permissions")

    def test_rejects_unknown_completion_permission_job(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["jobPermissions"]["unknownJob"] = [
            "actions: read"
        ]
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("add unknown completion permission job")
        head = self.prepare_release()
        self.assert_rejected(self.check(head), "exact job-scoped permissions")

    def test_rejects_overlapping_completion_and_recovery_directories(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["intentDirectory"] = (
            ".github/release-recovery-intents/completions"
        )
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("overlap completion and recovery directories")
        head = self.prepare_release()
        self.assert_rejected(
            self.check(head),
            "tag-only completion and recovery intent directories must be distinct",
        )

    def test_rejects_completion_directory_overlapping_sibling_mutation(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        profile = json.loads((self.repo / CONTRACT_PATH).read_text(encoding="utf-8"))
        profile["siblingReleaseUnits"][0]["mutationPaths"].append(
            ".github/release-tag-only-completion-intents/**"
        )
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("overlap completion and sibling mutation paths")
        head = self.prepare_tag_only_completion(
            original_intent_path=original_path,
            failed_source=failed_source,
            authorization_type="release-intent",
            authorization_path=original_path,
        )
        self.assert_rejected(
            self.check(head),
            "sibling release-unit mutation is forbidden",
        )

    def test_rejects_shared_completion_and_publication_workflow(self) -> None:
        profile = self.profile()
        profile["tagOnlyCompletion"]["workflow"] = (
            profile["releaseUnit"]["publicationWorkflow"]
        )
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("share completion and publication workflow")
        head = self.prepare_release()
        self.assert_rejected(
            self.check(head), "tag-only completion workflow must be distinct"
        )

    def test_rejects_release_paths_that_admit_completion_records(self) -> None:
        profile = self.profile()
        profile["releaseUnit"]["releasePreparationPaths"].append(
            ".github/release-tag-only-completion-intents/*.json"
        )
        self.write_json(CONTRACT_PATH, profile)
        self.base = self.commit("admit completion records as release preparation")
        head = self.prepare_release()
        self.assert_rejected(
            self.check(head),
            "must not admit tag-only completion authorization records",
        )

    def test_arbitrary_workflow_inputs_are_not_admission_authority(self) -> None:
        failed_source, original_path = self.materialize_failed_release()
        head = self.prepare_recovery(
            failed_source=failed_source, original_intent_path=original_path
        )
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--repository",
                str(self.repo),
                "--base",
                self.base,
                "--head",
                head,
                "--event-ref",
                "refs/heads/dev",
                "--version",
                "1.4.0-next.1",
                "--workflow-dispatch",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_schema_matches_checker_path_and_registry_boundaries(self) -> None:
        schema = json.loads(PROFILE_SCHEMA.read_text(encoding="utf-8"))
        intent_schema = json.loads(INTENT_SCHEMA.read_text(encoding="utf-8"))
        recovery_schema = json.loads(RECOVERY_INTENT_SCHEMA.read_text(encoding="utf-8"))
        completion_schema = json.loads(
            TAG_ONLY_COMPLETION_INTENT_SCHEMA.read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["intentDirectory"]["$ref"], "#/$defs/plainRelativePath")
        self.assertEqual(
            schema["properties"]["recovery"]["properties"]["intentDirectory"]["$ref"],
            "#/$defs/plainRelativePath",
        )
        self.assertEqual(
            schema["properties"]["tagOnlyCompletion"]["properties"]["intentDirectory"]["$ref"],
            "#/$defs/plainRelativePath",
        )
        completion_permissions = schema["properties"]["tagOnlyCompletion"][
            "properties"
        ]["jobPermissions"]
        self.assertEqual(
            completion_permissions["required"],
            [
                "admissionAndLiveVerification",
                "retainedArtifactRetrieval",
                "registryMutation",
                "postPublicationVerification",
            ],
        )
        self.assertEqual(
            {
                name: definition["const"]
                for name, definition in completion_permissions["properties"].items()
            },
            {
                "admissionAndLiveVerification": [
                    "contents: read",
                    "actions: read",
                    "packages: read",
                ],
                "retainedArtifactRetrieval": ["actions: read"],
                "registryMutation": ["packages: write"],
                "postPublicationVerification": [
                    "contents: read",
                    "packages: read",
                ],
            },
        )
        self.assertEqual(schema["$defs"]["pathPatterns"]["items"]["$ref"], "#/$defs/pathPattern")
        self.assertEqual(schema["properties"]["releaseUnit"]["properties"]["registry"]["pattern"], "^https://")
        self.assertTrue(schema["properties"]["siblingReleaseUnits"]["uniqueItems"])
        constrained_channels = {
            condition["if"]["properties"]["channel"]["const"]
            for condition in intent_schema["allOf"]
        }
        self.assertEqual(constrained_channels, {"prerelease", "final"})
        plain_path_pattern = schema["$defs"]["plainRelativePath"]["pattern"]
        workflow_pattern = schema["$defs"]["workflowPath"]["pattern"]
        self.assertIsNone(re.fullmatch(plain_path_pattern, ":(exclude)release-intents"))
        self.assertIsNone(re.fullmatch(plain_path_pattern, "packages/browser/CHANGELOG.md\nother"))
        self.assertIsNone(re.fullmatch(workflow_pattern, ".github/workflows/.yml"))
        self.assertIsNotNone(re.fullmatch(workflow_pattern, ".github/workflows/release.yml"))
        channel_patterns = {
            condition["if"]["properties"]["channel"]["const"]: condition["then"]["properties"]["version"]["pattern"]
            for condition in intent_schema["allOf"]
        }
        self.assertIsNotNone(re.fullmatch(channel_patterns["prerelease"], "1.2.3-rc.1"))
        self.assertIsNone(re.fullmatch(channel_patterns["prerelease"], "1.2.3"))
        self.assertIsNotNone(re.fullmatch(channel_patterns["final"], "1.2.3+build.1"))
        self.assertIsNone(re.fullmatch(channel_patterns["final"], "1.2.3-rc.1"))
        self.assertEqual(
            recovery_schema["properties"]["reason"]["const"],
            "pre-mutation-no-immutable-identity",
        )
        self.assertEqual(
            recovery_schema["properties"]["failedAttempt"]["properties"]["tagState"]["const"],
            "absent",
        )
        self.assertEqual(
            completion_schema["properties"]["reason"]["const"],
            "tag-only-partial-publication",
        )
        self.assertEqual(
            completion_schema["properties"]["failedPublication"]["properties"]["runAttempt"]["const"],
            1,
        )
        self.assertEqual(
            completion_schema["properties"]["failedPublication"]["properties"]["tagState"]["const"],
            "present",
        )
        self.assertEqual(
            completion_schema["properties"]["failedPublication"]["properties"]["registryVersionState"]["const"],
            "absent",
        )


if __name__ == "__main__":
    unittest.main()
