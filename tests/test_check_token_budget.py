import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_token_budget.py"


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def init_repo(path: Path):
    run(["git", "init", "-q"], path)
    (path / ".agent-workflows").mkdir()
    (path / ".agent-workflows" / "token-budgets.json").write_text(
        json.dumps({"budgets": {"AGENTS.md": 2}}),
        encoding="utf-8",
    )
    (path / "AGENTS.md").write_text("# Agent rules\n\nThis file is intentionally over budget.\n", encoding="utf-8")
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


class TokenBudgetTests(unittest.TestCase):
    def test_non_strict_reports_over_budget_without_failing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["failure_count"], 1)
            self.assertEqual(payload["result"], "passed")

    def test_strict_fails_over_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--strict", "--json"], repo)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertEqual(payload["failures"][0]["path"], "AGENTS.md")


if __name__ == "__main__":
    unittest.main()
