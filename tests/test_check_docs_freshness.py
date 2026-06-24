import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_docs_freshness.py"


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def init_repo(path: Path):
    run(["git", "init", "-q"], path)
    (path / "README.md").write_text("# Sample\n\nSee [missing](docs/missing.md).\n", encoding="utf-8")
    (path / "Makefile").write_text("docs-check:\n\t@echo ok\n", encoding="utf-8")
    run(["git", "add", "."], path)
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


class DocsFreshnessTests(unittest.TestCase):
    def test_missing_local_link_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertEqual(payload["failures"][0]["type"], "missing-local-link")

    def test_missing_make_target_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            (repo / "docs").mkdir(exist_ok=True)
            (repo / "docs" / "missing.md").write_text("# Exists\n\nRun `make missing-target`.\n", encoding="utf-8")

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertTrue(any(item["type"] == "missing-make-target" for item in payload["failures"]))

    def test_default_historical_paths_skip_command_reference_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            (repo / "docs").mkdir(exist_ok=True)
            (repo / "docs" / "missing.md").write_text("# Exists\n", encoding="utf-8")
            (repo / "docs" / "adr").mkdir()
            (repo / "docs" / "adr" / "0001-old-state.md").write_text(
                "# Old state\n\nAt the time, run `python3 scripts/retired_tool.py`.\n",
                encoding="utf-8",
            )

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "passed")
            self.assertIn("docs/adr/0001-old-state.md", payload["checks"]["scope"]["historical_docs"])

    def test_live_docs_still_fail_for_missing_script_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            (repo / "docs").mkdir(exist_ok=True)
            (repo / "docs" / "missing.md").write_text(
                "# Live spec\n\nRun `python3 scripts/current_tool.py`.\n",
                encoding="utf-8",
            )

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertTrue(
                any(
                    item["type"] == "missing-script-reference" and item["path"] == "docs/missing.md"
                    for item in payload["failures"]
                )
            )

    def test_configured_extra_historical_paths_skip_command_reference_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            (repo / "docs").mkdir(exist_ok=True)
            (repo / "docs" / "missing.md").write_text("# Exists\n", encoding="utf-8")
            (repo / "old-notes.md").write_text(
                "# Old notes\n\nAt the time, run `python3 scripts/retired_tool.py`.\n",
                encoding="utf-8",
            )
            (repo / "doc-contract.json").write_text(
                json.dumps({"docs_freshness": {"extra_historical_paths": ["old-notes.md"]}}),
                encoding="utf-8",
            )

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("old-notes.md", payload["checks"]["scope"]["historical_docs"])

    def test_configured_exclude_paths_skip_docs_entirely(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            (repo / "docs").mkdir(exist_ok=True)
            (repo / "docs" / "missing.md").write_text("# Exists\n", encoding="utf-8")
            (repo / "archived.md").write_text(
                "# Archived\n\nSee [gone](docs/gone.md). Run `python3 scripts/retired_tool.py`.\n",
                encoding="utf-8",
            )
            (repo / "doc-contract.json").write_text(
                json.dumps({"docs_freshness": {"exclude_paths": ["archived.md"]}}),
                encoding="utf-8",
            )

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("archived.md", payload["checks"]["scope"]["excluded_docs"])
            self.assertNotIn("archived.md", payload["docs_checked"])

    def test_semantic_receipt_requirement_can_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            (repo / "docs").mkdir(exist_ok=True)
            (repo / "docs" / "missing.md").write_text("# Exists\n", encoding="utf-8")
            (repo / "receipt.json").write_text("{}\n", encoding="utf-8")

            result = run(
                [
                    sys.executable,
                    str(CHECK),
                    "--repo",
                    str(repo),
                    "--require-semantic-receipt",
                    "--semantic-receipt",
                    "receipt.json",
                    "--json",
                ],
                repo,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["checks"]["semantic_receipt"]["passed"])


if __name__ == "__main__":
    unittest.main()
