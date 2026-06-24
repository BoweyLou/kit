import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


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


def prepare_task(repo: Path, task_id: str):
    result = run(["make", "agent-task-prepare", f"TASK={task_id}", "SCOPE=README.md"], repo)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    metadata_path = repo / ".agent-workflows" / "tasks" / f"{task_id.lower()}.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return metadata_path, metadata, Path(metadata["worktree"])


def prepare_dirty_baseline_task(repo: Path, task_id: str):
    result = run(
        [
            "make",
            "agent-task-prepare",
            f"TASK={task_id}",
            "SCOPE=README.md",
            "DIRTY_PRIMARY_BASELINE=1",
        ],
        repo,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    metadata_path = repo / ".agent-workflows" / "tasks" / f"{task_id.lower()}.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return metadata_path, metadata, Path(metadata["worktree"])


def write_receipt(repo: Path, task_id: str):
    receipt_path = Path(".agent-workflows") / "tasks" / task_id.lower() / "receipt.json"
    abs_path = repo / receipt_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text('{"status":"done"}\n', encoding="utf-8")
    return receipt_path.as_posix()


class AgentTaskFinalizeTests(unittest.TestCase):
    def test_finalize_finish_updates_lifecycle_and_writes_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            metadata_path, _, worktree = prepare_task(repo, "AGW-087")
            receipt = write_receipt(repo, "AGW-087")

            result = run(
                [
                    "make",
                    "agent-task-finalize",
                    "TASK=AGW-087",
                    f"TASK_RECEIPT={receipt}",
                    "TASK_OWNER=codex",
                    "TASK_OWNER_LABEL=Codex finalizer",
                    "TASK_SESSION_ID=session-final",
                    "TASK_THREAD_ID=thread-final",
                    "TASK_AUTOMATION_ID=automation-final",
                    "TASK_FINALIZE_SKIP_READY=1",
                    "TASK_FINALIZE_JSON=1",
                ],
                repo,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "passed")
            self.assertEqual(payload["action"], "finish")
            self.assertIsNone(payload["ready"])
            self.assertEqual(payload["lifecycle"]["status"], "done")
            self.assertEqual(payload["attribution"]["owner"], "codex")
            self.assertEqual(payload["attribution"]["owner_label"], "Codex finalizer")
            self.assertEqual(payload["attribution"]["session_id"], "session-final")
            self.assertEqual(payload["attribution"]["thread_id"], "thread-final")
            self.assertEqual(payload["attribution"]["automation_id"], "automation-final")
            self.assertEqual(payload["attribution"]["latest_receipt"]["path"], receipt)
            self.assertEqual(payload["attribution"]["latest_receipt"]["provenance"], "finalize-argument")
            self.assertEqual(payload["closeout"]["closeout_apply"], False)
            finalize_receipt = Path(payload["finalizer_receipt"])
            self.assertTrue(finalize_receipt.exists())
            updated = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["status"], "done")
            self.assertEqual(updated["final_receipt"], receipt)
            self.assertEqual(updated["attribution"]["owner"], "codex")
            self.assertEqual(updated["attribution"]["thread_id"], "thread-final")
            self.assertEqual(updated["attribution"]["automation_id"], "automation-final")
            self.assertEqual(updated["attribution"]["latest_receipt"]["path"], receipt)
            self.assertTrue(worktree.exists())

    def test_finalize_finish_blocks_when_readiness_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            metadata_path, _metadata, _ = prepare_task(repo, "AGW-088")
            receipt = write_receipt(repo, "AGW-088")

            result = run(
                [
                    "make",
                    "agent-task-finalize",
                    "TASK=AGW-088",
                    f"TASK_RECEIPT={receipt}",
                    "TASK_FINALIZE_JSON=1",
                ],
                repo,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertEqual(payload["steps"]["readiness"]["returncode"], 1)
            updated = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["status"], "in-progress")

    def test_finalize_block_skips_readiness_and_records_blocked_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            metadata_path, _metadata, _ = prepare_task(repo, "AGW-089")

            result = run(
                [
                    "make",
                    "agent-task-finalize",
                    "TASK=AGW-089",
                    "TASK_FINALIZE_ACTION=block",
                    "TASK_FINALIZE_JSON=1",
                    "TASK_REASON=waiting",
                ],
                repo,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "passed")
            self.assertIsNone(payload["ready"])
            self.assertEqual(payload["lifecycle"]["status"], "blocked")
            updated = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["status"], "blocked")

    def test_finalize_skip_ready_still_blocks_dirty_primary_baseline_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            (repo / "README.md").write_text("# Dirty baseline\n", encoding="utf-8")
            metadata_path, _metadata, _worktree = prepare_dirty_baseline_task(repo, "AGW-095")
            receipt = write_receipt(repo, "AGW-095")
            (repo / "README.md").write_text("# Mutated dirty baseline\n", encoding="utf-8")

            result = run(
                [
                    "make",
                    "agent-task-finalize",
                    "TASK=AGW-095",
                    f"TASK_RECEIPT={receipt}",
                    "TASK_FINALIZE_SKIP_READY=1",
                    "TASK_FINALIZE_JSON=1",
                ],
                repo,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertEqual(payload["steps"]["primary_baseline"]["returncode"], 1)
            self.assertIn("Primary checkout changed since dirty baseline", payload["steps"]["primary_baseline"]["stderr"])
            updated = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["status"], "in-progress")


if __name__ == "__main__":
    unittest.main()
