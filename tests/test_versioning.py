import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_SCRIPT = ROOT / "scripts" / "version.py"
CHANGELOG_HELPER = ROOT / "scripts" / "changelog_update.py"
INSTALL = ROOT / "scripts" / "install.py"
UPDATE = ROOT / "scripts" / "update.py"


def run(cmd, cwd, check=False):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def init_repo(path: Path):
    run(["git", "init", "-q"], path, check=True)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    run(["git", "add", "README.md"], path, check=True)
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
        check=True,
    )


class VersioningTests(unittest.TestCase):
    def test_valid_semver_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "VERSION").write_text("1.2.3\n", encoding="utf-8")

            result = run([sys.executable, str(VERSION_SCRIPT), "check"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("VERSION is valid SemVer: 1.2.3", result.stdout)

    def test_valid_prerelease_semver_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "VERSION").write_text("1.2.3-beta.1\n", encoding="utf-8")

            result = run([sys.executable, str(VERSION_SCRIPT), "check"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("VERSION is valid SemVer: 1.2.3-beta.1", result.stdout)

    def test_invalid_version_fails_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "VERSION").write_text("v1.2\n", encoding="utf-8")

            result = run([sys.executable, str(VERSION_SCRIPT), "check"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid SemVer", result.stderr)

    def test_invalid_prerelease_identifier_fails_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "VERSION").write_text("1.2.3-beta.01\n", encoding="utf-8")

            result = run([sys.executable, str(VERSION_SCRIPT), "check"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid SemVer", result.stderr)

    def test_version_bump_updates_version_and_changelog_stub(self):
        cases = {
            "patch": "1.2.4",
            "minor": "1.3.0",
            "major": "2.0.0",
        }
        for bump, expected in cases.items():
            with self.subTest(bump=bump):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = Path(tmp)
                    (repo / "VERSION").write_text("1.2.3\n", encoding="utf-8")
                    (repo / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

                    result = run([sys.executable, str(VERSION_SCRIPT), "bump", "--bump", bump], repo)

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual((repo / "VERSION").read_text(encoding="utf-8"), expected + "\n")
                    changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
                    self.assertIn(f"## {expected} - ", changelog)
                    self.assertIn("TODO: describe changes since 1.2.3", changelog)

    def test_version_bump_from_prerelease_uses_base_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "VERSION").write_text("1.2.3-beta.1\n", encoding="utf-8")
            (repo / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

            result = run([sys.executable, str(VERSION_SCRIPT), "bump", "--bump", "patch"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "VERSION").read_text(encoding="utf-8"), "1.2.4\n")
            changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertIn("TODO: describe changes since 1.2.3-beta.1", changelog)

    def test_changelog_update_bump_proposal_does_not_write_version_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (repo / "CHANGELOG.md").write_text("# Changelog\n\n", encoding="utf-8")

            result = run(
                [
                    sys.executable,
                    str(CHANGELOG_HELPER),
                    "--repo",
                    str(repo),
                    "--changed-file",
                    "cli/new_command.py",
                    "--bump",
                    "minor",
                    "--format",
                    "json",
                ],
                ROOT,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "VERSION").read_text(encoding="utf-8"), "1.2.3\n")
            self.assertEqual((repo / "CHANGELOG.md").read_text(encoding="utf-8"), "# Changelog\n\n")
            self.assertIn("1.3.0", result.stdout)

    def test_target_owned_version_files_are_not_overwritten_by_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            (repo / "VERSION").write_text("9.8.7\n", encoding="utf-8")
            (repo / "CHANGELOG.md").write_text("# Existing changelog\n", encoding="utf-8")

            install_result = run([sys.executable, str(INSTALL), str(repo), "--preset", "agentic"], ROOT)
            self.assertEqual(install_result.returncode, 0, install_result.stderr)

            update_result = run([sys.executable, str(UPDATE), str(repo)], ROOT)

            self.assertEqual(update_result.returncode, 0, update_result.stderr)
            self.assertEqual((repo / "VERSION").read_text(encoding="utf-8"), "9.8.7\n")
            self.assertEqual((repo / "CHANGELOG.md").read_text(encoding="utf-8"), "# Existing changelog\n")


if __name__ == "__main__":
    unittest.main()
