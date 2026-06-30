import json
import importlib
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


class AgentTaskPrepareTests(unittest.TestCase):
    def test_prepare_and_status_share_scope_helpers(self):
        scripts_path = str(ROOT / "scripts")
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)

        scope = importlib.import_module("_agent_scope")
        prepare = importlib.import_module("agent_task_prepare")
        status = importlib.import_module("agent_task_status")

        self.assertIs(prepare.parse_scope, scope.parse_scope)
        self.assertIs(prepare.paths_overlap, scope.paths_overlap)
        self.assertIs(status.paths_overlap, scope.paths_overlap)
        self.assertTrue(scope.paths_overlap("scripts", "./scripts/agent_task_prepare.py"))
        self.assertFalse(scope.paths_overlap("docs", "scripts/agent_task_prepare.py"))
        self.assertEqual(scope.parse_scope("README.md docs/ops"), ["README.md", "docs/ops"])

    def test_prepare_creates_sibling_worktree_and_local_task_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            result = run(
                ["make", "agent-task-prepare", "TASK=AGW-061", "TITLE=Add task launcher", "SCOPE=scripts/agent_task_prepare.py"],
                repo,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Agent task worktree prepared", result.stdout)

            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-061.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["task_id"], "AGW-061")
            self.assertTrue(metadata["run_id"].startswith("agw-061-"))
            self.assertEqual(metadata["status"], "in-progress")
            self.assertEqual(metadata["scope"], ["scripts/agent_task_prepare.py"])
            self.assertTrue(metadata["branch"].startswith("codex/task-agw-061-"))
            self.assertIn("heartbeat_at", metadata)
            self.assertIn("lease_expires_at", metadata)

            worktree = Path(metadata["worktree"])
            self.assertTrue(worktree.exists())
            self.assertFalse(str(worktree).startswith(str(repo / ".agent-workflows")))
            packet = json.loads((worktree / metadata["task_packet"]).read_text(encoding="utf-8"))
            receipt = json.loads((worktree / metadata["receipt_template"]).read_text(encoding="utf-8"))
            self.assertEqual(packet["task"]["id"], "AGW-061")
            self.assertEqual(packet["story"]["type"], "operator-story")
            self.assertEqual(packet["story"]["actor"], "write-capable implementation agent")
            self.assertEqual(packet["story"]["source"], "AGW-061")
            self.assertIn("validation evidence", packet["story"]["acceptance_summary"])
            self.assertIn("README.md", packet["docs_impact"]["documentation_surfaces"])
            self.assertIn("CHANGELOG.md", packet["docs_impact"]["release_metadata"])
            self.assertIn("docs/cli-reference.md", packet["docs_impact"]["generated_docs"])
            self.assertTrue(any("schema" in reference for reference in packet["docs_impact"]["contract_references"]))
            self.assertIn("make docs-freshness", packet["docs_impact"]["verification_commands"])
            self.assertEqual(packet["scope"]["allowed_files"], ["scripts/agent_task_prepare.py"])
            self.assertEqual(packet["goal_alignment"]["alignment_decision"], "unknown")
            self.assertEqual(packet["goal_alignment"]["area_contracts"][0]["status"], "unknown")
            self.assertEqual(packet["closeout_requirements"]["lifecycle_action"]["action"], "finish")
            self.assertIn("agent-task-finalize", packet["closeout_requirements"]["lifecycle_action"]["command"])
            self.assertEqual(packet["coordination"]["active_task_count"], 0)
            self.assertEqual(packet["parallel_context"]["active_task_count"], 0)
            self.assertTrue(packet["parallel_context"]["can_start_write_task"])
            self.assertEqual(packet["parallel_context"]["blockers"], [])
            self.assertEqual(receipt["review_risk"]["trust_profile"], "write-worker")
            self.assertEqual(receipt["run"]["id"], metadata["run_id"])
            self.assertEqual(receipt["coordination"]["active_task_count"], 0)
            self.assertTrue(receipt["parallel_context"]["can_start_write_task"])

            status = run(["git", "status", "--short"], repo)
            self.assertEqual(status.stdout.strip(), "")

    def test_prepare_blocks_overlapping_scope_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            first = run(["make", "agent-task-prepare", "TASK=AGW-061", "SCOPE=scripts"], repo)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            second = run(
                ["make", "agent-task-prepare", "TASK=AGW-062", "SCOPE=scripts/agent_task_prepare.py", "OVERLAP=block"],
                repo,
            )

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("Parallel task coordination blocks this write worktree", second.stdout)
            self.assertIn("active_scope_overlap", second.stdout)

    def test_prepare_allows_unrelated_expired_task_but_records_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            first = run(["make", "agent-task-prepare", "TASK=AGW-061", "SCOPE=docs"], repo)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            metadata_path = repo / ".agent-workflows" / "tasks" / "agw-061.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["lease_expires_at"] = "2020-01-01T00:00:00+00:00"
            metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            second = run(["make", "agent-task-prepare", "TASK=AGW-062", "SCOPE=scripts"], repo)

            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            next_metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-062.json").read_text(encoding="utf-8"))
            packet = json.loads((Path(next_metadata["worktree"]) / next_metadata["task_packet"]).read_text(encoding="utf-8"))
            self.assertTrue(packet["parallel_context"]["can_start_write_task"])
            warning_codes = {item["code"] for item in packet["parallel_context"]["warnings"]}
            self.assertIn("stale_task", warning_codes)

    def test_prepare_blocks_missing_same_scope_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            first = run(["make", "agent-task-prepare", "TASK=AGW-061", "SCOPE=docs"], repo)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            metadata_path = repo / ".agent-workflows" / "tasks" / "agw-061.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            run(["git", "worktree", "remove", "--force", metadata["worktree"]], repo, check=True)

            second = run(["make", "agent-task-prepare", "TASK=AGW-062", "SCOPE=docs/guide.md"], repo)

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("missing_task_worktree", second.stdout)

    def test_status_reports_active_task_worktrees_as_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            prepare = run(
                [
                    "make",
                    "agent-task-prepare",
                    "TASK=AGW-061",
                    "SCOPE=scripts/agent_task_prepare.py",
                    "TASK_OWNER=codex",
                    "TASK_OWNER_LABEL=Codex worker",
                    "TASK_SESSION_ID=session-061",
                    "TASK_THREAD_ID=thread-061",
                ],
                repo,
            )
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)

            result = run(["make", "agent-task-status", "TASK_STATUS_JSON=1"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["active_task_count"], 1)
            self.assertEqual(report["tasks"][0]["task_id"], "AGW-061")
            self.assertTrue(report["tasks"][0]["run_id"].startswith("agw-061-"))
            self.assertEqual(report["tasks"][0]["scope"], ["scripts/agent_task_prepare.py"])
            self.assertEqual(report["tasks"][0]["owner"], "codex")
            self.assertEqual(report["tasks"][0]["owner_label"], "Codex worker")
            self.assertEqual(report["tasks"][0]["session_id"], "session-061")
            self.assertEqual(report["tasks"][0]["thread_id"], "thread-061")
            self.assertEqual(report["tasks"][0]["attribution"]["owner"], "codex")
            self.assertEqual(report["tasks"][0]["attribution"]["owner_label"], "Codex worker")
            self.assertEqual(report["tasks"][0]["attribution"]["session_id"], "session-061")
            self.assertEqual(report["tasks"][0]["attribution"]["thread_id"], "thread-061")
            self.assertEqual(report["tasks"][0]["attribution"]["source"], "metadata")
            self.assertFalse(report["tasks"][0]["lease_expired"])
            self.assertTrue(report["tasks"][0]["worktree_exists"])
            self.assertTrue(report["tasks"][0]["worktree_registered"])
            self.assertFalse(report["tasks"][0]["dirty"])
            self.assertEqual(report["hazards"], [])
            self.assertIn("parallel_context", report)
            self.assertTrue(report["parallel_context"]["can_start_write_task"])
            self.assertEqual(report["parallel_context"]["recommended_next_command"], "make agent-task-prepare TASK=<id> SCOPE=<paths>")

            text = run(["make", "agent-task-status"], repo)
            self.assertEqual(text.returncode, 0, text.stdout + text.stderr)
            self.assertIn("attribution: owner=codex", text.stdout)
            self.assertIn("thread=thread-061", text.stdout)

    def test_prepare_records_owner_session_and_lifecycle_finish(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            prepare = run(
                [
                    "make",
                    "agent-task-prepare",
                    "TASK=AGW-067",
                    "SCOPE=docs",
                    "TASK_OWNER=codex",
                    "TASK_OWNER_LABEL=Codex reviewer",
                    "TASK_SESSION_ID=session-123",
                    "TASK_THREAD_ID=thread-123",
                    "TASK_AUTOMATION_ID=automation-nightly",
                ],
                repo,
            )
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)

            heartbeat = run(["make", "agent-task-heartbeat", "TASK=AGW-067", "TASK_LIFECYCLE_JSON=1"], repo)
            self.assertEqual(heartbeat.returncode, 0, heartbeat.stdout + heartbeat.stderr)
            self.assertEqual(json.loads(heartbeat.stdout)["status"], "in-progress")

            finish = run(
                [
                    "make",
                    "agent-task-finish",
                    "TASK=AGW-067",
                    "TASK_RECEIPT=.agent-workflows/tasks/agw-067/receipt.json",
                    "TASK_LIFECYCLE_JSON=1",
                ],
                repo,
            )
            self.assertEqual(finish.returncode, 0, finish.stdout + finish.stderr)
            payload = json.loads(finish.stdout)
            self.assertEqual(payload["status"], "done")

            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-067.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["owner"], "codex")
            self.assertEqual(metadata["owner_label"], "Codex reviewer")
            self.assertEqual(metadata["session_id"], "session-123")
            self.assertEqual(metadata["thread_id"], "thread-123")
            self.assertEqual(metadata["automation_id"], "automation-nightly")
            self.assertEqual(metadata["attribution"]["owner"], "codex")
            self.assertEqual(metadata["attribution"]["owner_label"], "Codex reviewer")
            self.assertEqual(metadata["attribution"]["session_id"], "session-123")
            self.assertEqual(metadata["attribution"]["thread_id"], "thread-123")
            self.assertEqual(metadata["attribution"]["automation_id"], "automation-nightly")
            self.assertEqual(metadata["attribution"]["source"], "metadata")
            self.assertEqual(metadata["attribution"]["latest_receipt"]["path"], ".agent-workflows/tasks/agw-067/receipt.json")
            self.assertEqual(metadata["status"], "done")
            self.assertEqual(metadata["final_receipt"], ".agent-workflows/tasks/agw-067/receipt.json")
            self.assertEqual(metadata["lifecycle_events"][-1]["event"], "finish")
            self.assertEqual(payload["attribution"]["automation_id"], "automation-nightly")

            prune_preview = run(["make", "agent-task-prune", "TASK_LIFECYCLE_JSON=1"], repo)
            self.assertEqual(prune_preview.returncode, 0, prune_preview.stdout + prune_preview.stderr)
            self.assertEqual(len(json.loads(prune_preview.stdout)["pruned"]), 1)
            self.assertTrue((repo / ".agent-workflows" / "tasks" / "agw-067.json").exists())

    def test_status_strict_fails_on_active_scope_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            first = run(["make", "agent-task-prepare", "TASK=AGW-061", "SCOPE=scripts"], repo)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            first_metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-061.json").read_text(encoding="utf-8"))
            second_metadata = dict(first_metadata)
            second_metadata["task_id"] = "AGW-062"
            second_metadata["scope"] = ["scripts/agent_task_prepare.py"]
            second_metadata["branch"] = "codex/task-agw-062-synthetic"
            (repo / ".agent-workflows" / "tasks" / "agw-062.json").write_text(
                json.dumps(second_metadata, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            result = run(["make", "agent-task-status", "TASK_STATUS_STRICT=1"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Strict mode failures", result.stdout)
            self.assertIn("AGW-061:scripts overlaps AGW-062:scripts/agent_task_prepare.py", result.stdout)

    def test_status_strict_fails_on_missing_task_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            task_dir = repo / ".agent-workflows" / "tasks"
            task_dir.mkdir(parents=True, exist_ok=True)
            (task_dir / "agw-063.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "task_id": "AGW-063",
                        "status": "in-progress",
                        "worktree": str(Path(tmp) / "missing-worktree"),
                        "scope": ["docs"],
                    }
                ),
                encoding="utf-8",
            )

            result = run(["make", "agent-task-status", "TASK_STATUS_STRICT=1"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AGW-063", result.stdout)
            self.assertIn("worktree path is missing", result.stdout)

            json_result = run(["make", "agent-task-status", "TASK_STATUS_JSON=1"], repo)
            self.assertEqual(json_result.returncode, 0, json_result.stdout + json_result.stderr)
            payload = json.loads(json_result.stdout)
            task = payload["tasks"][0]
            self.assertEqual(task["attribution"]["source"], "unknown")
            self.assertEqual(task["attribution"]["metadata_path"], ".agent-workflows/tasks/agw-063.json")
            self.assertEqual(payload["stale_tasks"][0]["attribution"]["source"], "unknown")

    def test_prepare_requires_clean_main_checkout_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            (repo / "README.md").write_text("# Dirty repo\n", encoding="utf-8")

            result = run(["make", "agent-task-prepare", "TASK=AGW-061"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Main checkout must be clean", result.stderr)
            self.assertIn("README.md", result.stderr)
            self.assertIn("make agent-preflight", result.stderr)
            self.assertIn("make agent-task-status", result.stderr)
            self.assertIn("make agent-task-closeout", result.stderr)
            self.assertIn("DIRTY_PRIMARY_BASELINE=1 make agent-task-prepare TASK=AGW-061", result.stderr)

    def test_prepare_dirty_checkout_json_reports_blocker_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            (repo / "README.md").write_text("# Dirty repo\n", encoding="utf-8")
            (repo / "notes.txt").write_text("untracked\n", encoding="utf-8")

            result = run(["make", "agent-task-prepare", "TASK=AGW-061", "TASK_PREPARE_JSON=1"], repo)

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "agent-task-prepare")
            self.assertEqual(payload["result"], "blocked")
            self.assertIn("Main checkout must be clean before preparing a write-capable task worktree.", payload["blockers"])
            paths = {entry["path"] for entry in payload["dirty"]["entries"]}
            self.assertEqual(paths, {"README.md", "notes.txt"})
            self.assertEqual(payload["dirty"]["tracked_count"], 1)
            self.assertEqual(payload["dirty"]["untracked_count"], 1)
            self.assertEqual(payload["dirty"]["attribution"]["source"], "unknown")
            self.assertIn("make agent-preflight", payload["recommendations"])
            self.assertIn("DIRTY_PRIMARY_BASELINE=1 make agent-task-prepare TASK=AGW-061", payload["recommendations"])

    def test_prepare_dirty_primary_baseline_records_metadata_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            head = run(["git", "rev-parse", "HEAD"], repo, check=True).stdout.strip()
            (repo / "README.md").write_text("# Dirty baseline\n", encoding="utf-8")
            (repo / "notes.txt").write_text("pre-existing\n", encoding="utf-8")

            result = run(
                [
                    "make",
                    "agent-task-prepare",
                    "TASK=AGW-095",
                    "SCOPE=README.md",
                    "DIRTY_PRIMARY_BASELINE=1",
                ],
                repo,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("primary checkout dirty baseline recorded", result.stdout)
            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-095.json").read_text(encoding="utf-8"))
            baseline = metadata["primary_checkout_baseline"]
            self.assertTrue(baseline["dirty"])
            self.assertEqual(baseline["head"], head)
            self.assertEqual(set(baseline["changed_files"]), {"README.md", "notes.txt"})
            self.assertEqual(baseline["counts"]["tracked"], 1)
            self.assertEqual(baseline["counts"]["untracked"], 1)
            self.assertEqual(len(baseline["state_sha256"]), 64)
            self.assertTrue(baseline["untracked_content"])

            worktree = Path(metadata["worktree"])
            receipt = json.loads((worktree / metadata["receipt_template"]).read_text(encoding="utf-8"))
            packet = json.loads((worktree / metadata["task_packet"]).read_text(encoding="utf-8"))
            self.assertEqual(receipt["primary_checkout_baseline"]["state_sha256"], baseline["state_sha256"])
            self.assertEqual(packet["primary_checkout_baseline"]["state_sha256"], baseline["state_sha256"])

            status_paths = {line[3:] for line in run(["git", "status", "--porcelain=v1", "--untracked-files=all"], repo).stdout.splitlines()}
            self.assertEqual(status_paths, {"README.md", "notes.txt"})

    def test_prepare_dirty_primary_baseline_blocks_untracked_scoped_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            frontend = repo / "frontend" / "app"
            frontend.mkdir(parents=True)
            (frontend / "main.tsx").write_text("export const value = 1;\n", encoding="utf-8")

            result = run(
                [
                    "make",
                    "agent-task-prepare",
                    "TASK=AGW-096",
                    "SCOPE=frontend",
                    "DIRTY_PRIMARY_BASELINE=1",
                    "TASK_PREPARE_JSON=1",
                ],
                repo,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertIn("untracked files inside the task scope", payload["blockers"][0])
            self.assertEqual(payload["untracked_scope_files"][0]["path"], "frontend/app/main.tsx")
            self.assertEqual(payload["untracked_scope_files"][0]["scope"], "frontend")

    def test_prepare_rejects_existing_task_worktree_as_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            first = run(["make", "agent-task-prepare", "TASK=AGW-061", "SCOPE=scripts"], repo)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-061.json").read_text(encoding="utf-8"))
            worktree = Path(metadata["worktree"])

            second = run(["make", "agent-task-prepare", "TASK=AGW-062", "SCOPE=docs"], worktree)

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("must run from the primary checkout", second.stderr)
            self.assertIn(str(repo), second.stderr)


if __name__ == "__main__":
    unittest.main()
