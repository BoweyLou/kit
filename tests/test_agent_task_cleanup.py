import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


def run(cmd, cwd, check=False):
    return subprocess.run(
        cmd,
        cwd=cwd,
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


def finish_task(repo: Path, task_id: str, receipt: bool = True):
    command = ["make", "agent-task-finish", f"TASK={task_id}", "TASK_LIFECYCLE_JSON=1"]
    if receipt:
        slug = task_id.lower()
        receipt_path = Path(".agent-workflows") / "tasks" / slug / "receipt.json"
        abs_receipt = repo / receipt_path
        abs_receipt.parent.mkdir(parents=True, exist_ok=True)
        abs_receipt.write_text('{"status":"done"}\n', encoding="utf-8")
        command.append(f"TASK_RECEIPT={receipt_path.as_posix()}")
    result = run(command, repo)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


class AgentTaskCleanupTests(unittest.TestCase):
    def test_cleanup_reports_nested_worktree_without_mutating_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            nested_path = Path(tmp) / "repo-agent-worktrees" / "agw-001-agent-worktrees" / "agw-002-20260525000000"
            branch = "codex/task-agw-002-20260525000000"
            run(["git", "worktree", "add", "-b", branch, str(nested_path), "HEAD"], repo, check=True)

            result = run(["make", "agent-task-cleanup", "TASK_CLEANUP_JSON=1"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["primary_checkout"], str(repo.resolve()))
            self.assertEqual(report["move_candidate_count"], 1)
            self.assertEqual(report["move_candidates"][0]["path"], str(nested_path.resolve()))
            self.assertTrue(nested_path.exists())

    def test_cleanup_moves_nested_worktree_to_flat_pool_when_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            nested_path = Path(tmp) / "repo-agent-worktrees" / "agw-001-agent-worktrees" / "agw-002-20260525000000"
            flat_path = Path(tmp) / "repo-agent-worktrees" / "agw-002-20260525000000"
            branch = "codex/task-agw-002-20260525000000"
            run(["git", "worktree", "add", "-b", branch, str(nested_path), "HEAD"], repo, check=True)

            result = run(
                [
                    "make",
                    "agent-task-cleanup",
                    "TASK_CLEANUP_JSON=1",
                    "TASK_CLEANUP_MOVE_NESTED=1",
                    "TASK_CLEANUP_APPLY=1",
                ],
                repo,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["applied_actions"][0]["from"], str(nested_path.resolve()))
            self.assertEqual(report["applied_actions"][0]["to"], str(flat_path.resolve()))
            self.assertFalse(nested_path.exists())
            self.assertTrue(flat_path.exists())
            self.assertEqual(report["move_candidate_count"], 0)
            worktrees = run(["git", "worktree", "list", "--porcelain"], repo, check=True)
            self.assertIn(str(flat_path.resolve()), worktrees.stdout)

    def test_closeout_reports_finished_clean_worktree_without_mutating_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            prepare = run(["make", "agent-task-prepare", "TASK=AGW-080", "SCOPE=scripts"], repo)
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
            metadata_path = repo / ".agent-workflows" / "tasks" / "agw-080.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            worktree = Path(metadata["worktree"])
            finish_task(repo, "AGW-080")

            result = run(["make", "agent-task-closeout", "TASK_CLOSEOUT_JSON=1"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["closeout_candidate_count"], 1)
            self.assertEqual(report["closeout_candidates"][0]["path"], str(worktree.resolve()))
            self.assertTrue(worktree.exists())
            self.assertTrue(metadata_path.exists())

    def test_closeout_removes_clean_finished_worktree_and_metadata_when_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            prepare = run(["make", "agent-task-prepare", "TASK=AGW-081", "SCOPE=scripts"], repo)
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
            metadata_path = repo / ".agent-workflows" / "tasks" / "agw-081.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            worktree = Path(metadata["worktree"])
            finish_task(repo, "AGW-081")

            result = run(["make", "agent-task-closeout", "TASK_CLOSEOUT_JSON=1", "TASK_CLOSEOUT_APPLY=1"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["applied_actions"][0]["action"], "closeout-remove")
            self.assertEqual(report["applied_actions"][0]["path"], str(worktree.resolve()))
            self.assertFalse(worktree.exists())
            self.assertFalse(metadata_path.exists())
            self.assertEqual(report["closeout_candidate_count"], 0)
            worktrees = run(["git", "worktree", "list", "--porcelain"], repo, check=True)
            self.assertNotIn(str(worktree.resolve()), worktrees.stdout)

    def test_closeout_blocks_dirty_worktrees_and_missing_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            dirty_prepare = run(["make", "agent-task-prepare", "TASK=AGW-082", "SCOPE=README.md"], repo)
            self.assertEqual(dirty_prepare.returncode, 0, dirty_prepare.stdout + dirty_prepare.stderr)
            dirty_metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-082.json").read_text(encoding="utf-8"))
            dirty_worktree = Path(dirty_metadata["worktree"])
            (dirty_worktree / "README.md").write_text("# Changed in worktree\n", encoding="utf-8")
            finish_task(repo, "AGW-082")

            no_receipt_prepare = run(["make", "agent-task-prepare", "TASK=AGW-083", "SCOPE=docs"], repo)
            self.assertEqual(no_receipt_prepare.returncode, 0, no_receipt_prepare.stdout + no_receipt_prepare.stderr)
            no_receipt_metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-083.json").read_text(encoding="utf-8"))
            no_receipt_worktree = Path(no_receipt_metadata["worktree"])
            finish_task(repo, "AGW-083", receipt=False)

            result = run(["make", "agent-task-closeout", "TASK_CLOSEOUT_JSON=1"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["closeout_candidate_count"], 0)
            blocked = {item["path"]: item["reasons"] for item in report["closeout_blocked"]}
            self.assertIn("worktree has uncommitted changes", blocked[str(dirty_worktree.resolve())])
            self.assertIn("terminal task has no linked final receipt", blocked[str(no_receipt_worktree.resolve())])
            dispositions = {item["task_id"]: item["disposition"] for item in report["task_reconciliation"]}
            self.assertEqual(dispositions["AGW-082"], "dirty-needs-review")
            self.assertEqual(dispositions["AGW-083"], "blocked-by-receipt")
            self.assertTrue(no_receipt_worktree.exists())

    def test_cleanup_classifies_missing_worktree_without_mutating_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            prepare = run(["make", "agent-task-prepare", "TASK=AGW-086", "SCOPE=docs"], repo)
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-086.json").read_text(encoding="utf-8"))
            worktree = Path(metadata["worktree"])
            run(["git", "worktree", "remove", "--force", str(worktree)], repo, check=True)

            result = run(["make", "agent-task-cleanup", "TASK_CLEANUP_JSON=1"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            dispositions = {item["task_id"]: item for item in report["task_reconciliation"]}
            self.assertEqual(dispositions["AGW-086"]["disposition"], "missing-worktree")
            self.assertFalse(dispositions["AGW-086"]["apply_supported"])
            self.assertTrue((repo / ".agent-workflows" / "tasks" / "agw-086.json").exists())

    def test_closeout_keep_count_retains_newest_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            for task_id, completed_at in (
                ("AGW-084", "2026-01-01T00:00:00+00:00"),
                ("AGW-085", "2026-01-02T00:00:00+00:00"),
            ):
                prepare = run(["make", "agent-task-prepare", f"TASK={task_id}", "SCOPE=scripts"], repo)
                self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
                finish_task(repo, task_id)
                metadata_path = repo / ".agent-workflows" / "tasks" / f"{task_id.lower()}.json"
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                metadata["completed_at"] = completed_at
                metadata["updated_at"] = completed_at
                metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = run(["make", "agent-task-closeout", "TASK_CLOSEOUT_JSON=1", "TASK_CLOSEOUT_KEEP=1"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["closeout_candidate_count"], 1)
            self.assertEqual(report["closeout_candidates"][0]["task_id"], "AGW-084")
            self.assertEqual(report["closeout_retained"][0]["task_id"], "AGW-085")


if __name__ == "__main__":
    unittest.main()
