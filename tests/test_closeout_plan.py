import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "repo_contract_kit.py"
INSTALL = ROOT / "scripts" / "install.py"


def run(cmd, cwd, env=None, check=False):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=check,
    )


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


def install_agentic(repo: Path):
    result = run([sys.executable, str(INSTALL), str(repo), "--preset", "agentic"], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    run(["git", "add", "."], repo, check=True)
    run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Install repo contract kit",
        ],
        repo,
        check=True,
    )


def make_env(state_home: Path):
    return {**os.environ, "XDG_STATE_HOME": str(state_home)}


def closeout_plan(repo: Path, state_home: Path, *extra):
    return run(
        [sys.executable, str(CLI), "closeout-plan", "--repo", str(repo), "--json", *extra],
        ROOT,
        env=make_env(state_home),
    )


class CloseoutPlanTests(unittest.TestCase):
    def test_clean_repo_can_claim_done_without_sidecar_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"

            result = closeout_plan(repo, state_home, "--strict")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "closeout-plan")
            self.assertTrue(payload["can_claim_done"])
            self.assertEqual(payload["completion_state"], "clean")
            self.assertFalse(payload["target_repo_writes"])
            self.assertFalse(payload["sidecar_writes"])
            self.assertFalse(payload["write_guarantees"]["target_repo_writes"]["performed"])
            self.assertFalse(payload["write_guarantees"]["sidecar_writes"]["performed"])
            self.assertEqual(payload["next_action"]["command"], "none")
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_dirty_primary_checkout_blocks_done_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"
            (repo / "README.md").write_text("# Dirty repo\n", encoding="utf-8")

            result = closeout_plan(repo, state_home, "--strict")

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["can_claim_done"])
            self.assertEqual(payload["completion_state"], "needs-integration")
            self.assertEqual(payload["next_action"]["command"], "git status --short")
            blocker_codes = {item["code"] for item in payload["claim_blockers"]}
            self.assertIn("dirty_primary_checkout", blocker_codes)
            self.assertEqual(payload["dirty_file_groups"][0]["group"], "(root)")
            self.assertEqual(payload["dirty_file_groups"][0]["files"][0]["path"], "README.md")

    def test_active_task_requires_receipt_or_finalizer_before_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"
            prepare = run(["make", "agent-task-prepare", "TASK=AGW-200", "SCOPE=README.md"], repo)
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)

            result = closeout_plan(repo, state_home, "--strict")

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["can_claim_done"])
            self.assertEqual(payload["completion_state"], "needs-receipt")
            self.assertEqual(payload["active_tasks"][0]["task_id"], "AGW-200")
            self.assertIn("make agent-task-ready TASK=AGW-200", payload["next_action"]["command"])
            self.assertFalse(payload["next_action"]["mutating"])
            blocker_codes = {item["code"] for item in payload["claim_blockers"]}
            self.assertIn("active_tasks", blocker_codes)

    def test_terminal_task_missing_receipt_requires_linked_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"
            prepare = run(["make", "agent-task-prepare", "TASK=AGW-201", "SCOPE=README.md"], repo)
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
            finish = run(["make", "agent-task-finish", "TASK=AGW-201", "TASK_LIFECYCLE_JSON=1"], repo)
            self.assertEqual(finish.returncode, 0, finish.stdout + finish.stderr)

            result = closeout_plan(repo, state_home, "--strict")

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["can_claim_done"])
            self.assertEqual(payload["completion_state"], "needs-receipt")
            self.assertEqual(payload["terminal_missing_receipts"][0]["task_id"], "AGW-201")
            self.assertEqual(
                payload["next_action"]["command"],
                "make agent-task-link-receipt TASK=AGW-201 TASK_RECEIPT=<path>",
            )
            blocker_codes = {item["code"] for item in payload["claim_blockers"]}
            self.assertIn("missing_final_receipts", blocker_codes)


if __name__ == "__main__":
    unittest.main()
