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


class AgentStateLedgerTests(unittest.TestCase):
    def test_clean_ledger_is_read_only_and_reports_missing_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"

            result = run(["make", "agent-state-ledger", "STATE_LEDGER_JSON=1"], repo, env=make_env(state_home))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "agent-state-ledger")
            self.assertIs(payload["target_repo_writes"], False)
            self.assertIs(payload["sidecar_writes"], False)
            self.assertFalse(payload["write_guarantees"]["target_repo_writes"]["performed"])
            self.assertFalse(payload["write_guarantees"]["sidecar_writes"]["performed"])
            self.assertFalse(payload["dirty"]["dirty"])
            self.assertFalse(payload["sidecar"]["available"])
            self.assertIn("make agent-self-heal", payload["next_safe_commands"])
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_ledger_reports_active_dirty_missing_and_overlapping_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"

            first = run(
                [
                    "make",
                    "agent-task-prepare",
                    "TASK=AGW-097",
                    "SCOPE=docs",
                    "OVERLAP=ignore",
                    "TASK_OWNER=codex",
                    "TASK_OWNER_LABEL=Codex ledger",
                    "TASK_SESSION_ID=session-ledger",
                    "TASK_THREAD_ID=thread-ledger",
                ],
                repo,
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            second = run(["make", "agent-task-prepare", "TASK=AGW-098", "SCOPE=docs/README.md", "OVERLAP=ignore"], repo)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-097.json").read_text(encoding="utf-8"))
            worktree = Path(metadata["worktree"])
            (worktree / "README.md").write_text("# Dirty task\n", encoding="utf-8")
            missing = repo / ".agent-workflows" / "tasks" / "agw-099.json"
            missing.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "task_id": "AGW-099",
                        "status": "in-progress",
                        "worktree": str(Path(tmp) / "missing-worktree"),
                        "scope": ["scripts"],
                        "lease_expires_at": "2000-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )

            result = run(["make", "agent-state-ledger", "STATE_LEDGER_JSON=1"], repo, env=make_env(state_home))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            tasks = {task["task_id"]: task for task in payload["task_status"]["tasks"]}
            self.assertTrue(tasks["AGW-097"]["dirty"])
            self.assertTrue(tasks["AGW-097"]["active_overlap"])
            self.assertEqual(tasks["AGW-097"]["attribution"]["owner"], "codex")
            self.assertEqual(tasks["AGW-097"]["attribution"]["owner_label"], "Codex ledger")
            self.assertEqual(tasks["AGW-097"]["attribution"]["session_id"], "session-ledger")
            self.assertEqual(tasks["AGW-097"]["attribution"]["thread_id"], "thread-ledger")
            self.assertTrue(tasks["AGW-099"]["missing_worktree"])
            self.assertTrue(tasks["AGW-099"]["stale_lease"])
            self.assertEqual(tasks["AGW-099"]["attribution"]["source"], "unknown")
            codes = {item["code"] for item in payload["unresolved"]["blockers"] + payload["unresolved"]["warnings"]}
            self.assertIn("dirty_worktree", codes)
            self.assertIn("missing_worktree", codes)
            self.assertIn("stale_lease", codes)
            self.assertIn("active_overlap", codes)
            dirty_warning = next(item for item in payload["unresolved"]["warnings"] if item["code"] == "dirty_worktree")
            self.assertEqual(dirty_warning["attribution"]["owner"], "codex")
            missing_blocker = next(item for item in payload["unresolved"]["blockers"] if item["code"] == "missing_worktree")
            self.assertEqual(missing_blocker["attribution"]["source"], "unknown")
            self.assertEqual(payload["task_status"]["dirty_worktree_tasks"][0]["attribution"]["owner"], "codex")
            self.assertIn("make agent-task-status TASK_STATUS_STRICT=1", payload["next_safe_commands"])

    def test_ledger_reports_terminal_task_missing_final_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"

            prepare = run(["make", "agent-task-prepare", "TASK=AGW-100", "SCOPE=README.md"], repo)
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
            finish = run(["make", "agent-task-finish", "TASK=AGW-100", "TASK_LIFECYCLE_JSON=1"], repo)
            self.assertEqual(finish.returncode, 0, finish.stdout + finish.stderr)

            result = run(["make", "agent-state-ledger", "STATE_LEDGER_JSON=1"], repo, env=make_env(state_home))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            task = next(item for item in payload["task_status"]["tasks"] if item["task_id"] == "AGW-100")
            self.assertTrue(task["missing_final_receipt"])
            self.assertIn("make agent-task-closeout", payload["next_safe_commands"])
            codes = {item["code"] for item in payload["unresolved"]["blockers"]}
            self.assertIn("missing_final_receipt", codes)

    def test_ledger_indexes_sidecar_receipts_and_tolerates_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            state_home = Path(tmp) / "state"
            env = make_env(state_home)

            init = run([sys.executable, str(CLI), "sidecar-init", "--repo", str(repo), "--json"], ROOT, env=env)
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            sidecar = json.loads(init.stdout)["sidecar_state"]
            receipts_dir = Path(sidecar["paths"]["receipts_dir"])
            handoff_dir = Path(sidecar["paths"]["automation_handoffs_dir"])
            receipts_dir.joinpath("20260101T000000000000Z-agent-preflight.json").write_text(
                json.dumps({"command": "agent-preflight", "created_at": "2026-01-01T00:00:00Z", "result": "passed"}),
                encoding="utf-8",
            )
            receipts_dir.joinpath("20260101T000100000000Z-agent-self-heal.json").write_text(
                json.dumps({"command": "agent-self-heal", "created_at": "2026-01-01T00:01:00Z", "result": "blocked"}),
                encoding="utf-8",
            )
            receipts_dir.joinpath("invalid.json").write_text("{not-json", encoding="utf-8")
            handoff_dir.joinpath("20260101T000200000000Z-original.json").write_text(
                json.dumps(
                    {
                        "command": "automation-handoff",
                        "action": "capture-original-baseline",
                        "created_at": "2026-01-01T00:02:00Z",
                        "result": "passed",
                    }
                ),
                encoding="utf-8",
            )
            handoff_dir.joinpath("20260101T000300000000Z-handoff.json").write_text(
                json.dumps({"command": "automation-handoff", "created_at": "2026-01-01T00:03:00Z", "result": "blocked", "label": "nightly"}),
                encoding="utf-8",
            )
            task_receipt_dir = repo / ".agent-workflows" / "tasks" / "agw-101"
            task_receipt_dir.mkdir(parents=True)
            task_receipt_dir.joinpath("finalize-receipt.json").write_text(
                json.dumps({"command": "agent-task-finalize", "created_at": "2026-01-01T00:04:00Z", "task_id": "AGW-101", "result": "blocked"}),
                encoding="utf-8",
            )
            before = sorted(path.relative_to(state_home).as_posix() for path in state_home.rglob("*"))

            result = run(["make", "agent-state-ledger", "STATE_LEDGER_JSON=1"], repo, env=env)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            categories = payload["receipts"]["categories"]
            self.assertIn("preflight_doctor", categories)
            self.assertIn("self_heal", categories)
            self.assertIn("automation_baseline", categories)
            self.assertIn("automation_handoff", categories)
            self.assertIn("finalizer", categories)
            self.assertEqual(categories["automation_handoff"]["latest"]["attribution"]["automation_id"], "nightly")
            self.assertEqual(categories["automation_handoff"]["latest"]["attribution"]["source"], "receipt")
            automation_blocker = next(item for item in payload["unresolved"]["blockers"] if item["code"] == "automation_handoff_blocked")
            self.assertEqual(automation_blocker["attribution"]["automation_id"], "nightly")
            self.assertTrue(any("Invalid receipt JSON" in warning for warning in payload["receipts"]["warnings"]))
            self.assertIn("make agent-automation-handoff", payload["next_safe_commands"])
            after = sorted(path.relative_to(state_home).as_posix() for path in state_home.rglob("*"))
            self.assertEqual(after, before)

    def test_ledger_text_is_concise(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            result = run(["make", "agent-state-ledger"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Agent state ledger", result.stdout)
            self.assertIn("writes: target=false sidecar=false", result.stdout)
            self.assertIn("next safe commands", result.stdout)


if __name__ == "__main__":
    unittest.main()
