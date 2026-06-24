import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "changelog_update.py"


def run(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def init_repo(path: Path):
    run(["git", "init", "-q"], path)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    run(["git", "add", "README.md"], path)
    run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Initial sample repo",
        ],
        path,
    )
    (path / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    (path / "CHANGELOG.md").write_text("# Changelog\n\n", encoding="utf-8")


class ChangelogUpdateTests(unittest.TestCase):
    def test_docs_impacting_change_proposes_changelog_without_writing_target_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            original_version = (repo / "VERSION").read_text(encoding="utf-8")
            original_changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")

            result = run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(repo),
                    "--changed-file",
                    "cli/new_command.py",
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "changelog-update-required")
            self.assertTrue(payload["release_note"]["needed"])
            self.assertTrue(payload["release_note"]["required"])
            self.assertEqual(payload["versioning"]["version"], "1.2.3")
            self.assertEqual(payload["candidate_changelog_entry"]["heading"], "## 1.2.3 - Unreleased")
            self.assertIn("cli/new_command.py", payload["candidate_changelog_entry"]["text"])
            self.assertIn("make version-check", payload["next_commands"]["safe"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertEqual((repo / "VERSION").read_text(encoding="utf-8"), original_version)
            self.assertEqual((repo / "CHANGELOG.md").read_text(encoding="utf-8"), original_changelog)

    def test_check_mode_fails_when_release_note_is_required_but_changelog_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)

            result = run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(repo),
                    "--changed-file",
                    "cli/new_command.py",
                    "--check",
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "check")
            self.assertTrue(payload["release_note"]["required"])

    def test_check_mode_passes_when_no_docs_impacting_change_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)

            result = run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(repo),
                    "--changed-file",
                    "README.md",
                    "--check",
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "no-release-note-needed")
            self.assertFalse(payload["release_note"]["needed"])
            self.assertEqual(payload["candidate_changelog_entry"]["text"], "")

    def test_check_mode_passes_when_changelog_is_in_changed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)

            result = run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(repo),
                    "--changed-file",
                    "cli/new_command.py",
                    "--changed-file",
                    "CHANGELOG.md",
                    "--check",
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "changelog-present")
            self.assertFalse(payload["release_note"]["required"])
            self.assertTrue(payload["versioning"]["changelog_changed"])

    def test_docs_impact_json_and_bump_create_deterministic_candidate_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            (repo / "docs-impact.json").write_text(
                json.dumps(
                    {
                        "changed_files": ["api/server.py"],
                        "docs_changed": [],
                        "categories": [
                            {
                                "category": "api",
                                "changed_files": ["api/server.py"],
                                "suggested_doc_paths": ["docs/api/"],
                                "covered": False,
                            }
                        ],
                        "missing_categories": ["api"],
                        "result": "missing-docs",
                    }
                ),
                encoding="utf-8",
            )

            result = run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(repo),
                    "--docs-impact-json",
                    "docs-impact.json",
                    "--bump",
                    "patch",
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["docs_impact"]["source"], "docs-impact-json")
            self.assertEqual(payload["candidate_changelog_entry"]["heading"], "## 1.2.4 - <date>")
            self.assertEqual(payload["next_commands"]["explicit_write_only"], [
                "make version-bump BUMP=patch",
                "edit CHANGELOG.md under accepted release-note scope",
            ])

    def test_text_output_includes_candidate_and_no_write_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)

            result = run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(repo),
                    "--changed-file",
                    "cli/new_command.py",
                ]
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Changelog update: changelog-update-required", result.stdout)
            self.assertIn("Target writes performed: false", result.stdout)
            self.assertIn("Candidate changelog entry:", result.stdout)


if __name__ == "__main__":
    unittest.main()
