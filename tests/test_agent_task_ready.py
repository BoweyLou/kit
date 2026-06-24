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


def current_branch(repo: Path):
    result = run(["git", "branch", "--show-current"], repo, check=True)
    return result.stdout.strip()


def write_valid_receipt(worktree: Path, task_id: str, changed_files: list[str], docs_result="not-applicable"):
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in task_id).strip("-")
    receipt_dir = worktree / ".agent-workflows" / "tasks" / slug
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / "receipt.json"
    payload = {
        "schema_version": 1,
        "run": {
            "id": f"{slug}-run",
            "started_at": "2026-06-13T00:00:00+00:00",
            "completed_at": "2026-06-13T00:05:00+00:00",
            "mode": "test-first",
            "status": "pass",
        },
        "tooling": {
            "agent_tool": "manual",
            "agent_tool_version": None,
            "local_only": True,
            "network_used": False,
            "notes": "test receipt",
        },
        "scope": {
            "repo_root": str(worktree),
            "base_ref": current_branch(worktree),
            "behavior_change": False,
            "changed_files": changed_files,
            "allowed_files": changed_files,
            "protected_files": [".git", ".env", ".secrets"],
        },
        "evidence": {
            "files_inspected": changed_files,
            "commands": [
                {"command": "git status --short", "result": "pass", "exit_code": 0, "notes": "clean enough for handoff"}
            ],
            "docs_impact": {"checked": True, "result": docs_result, "categories": [], "waiver_reason": None},
            "tests": {
                "result": "not-applicable",
                "failing_test_evidence": None,
                "passing_test_evidence": None,
                "generated_test_provenance": None,
                "skip_reason": None,
            },
        },
        "findings": [],
        "disposition": {
            "summary": "Ready for handoff.",
            "next_actions": [],
        },
    }
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt_path


def prepare_task(repo: Path, task_id: str, scope: str):
    base = current_branch(repo)
    result = run(["make", "agent-task-prepare", f"TASK={task_id}", f"SCOPE={scope}", f"BASE_REF={base}"], repo)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    metadata = json.loads((repo / ".agent-workflows" / "tasks" / f"{task_id.lower()}.json").read_text(encoding="utf-8"))
    return Path(metadata["worktree"]), base


class AgentTaskReadyTests(unittest.TestCase):
    def test_agent_task_ready_passes_for_in_scope_fresh_branch_with_valid_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            worktree, _ = prepare_task(repo, "AGW-090", "README.md")

            (worktree / "README.md").write_text("# Updated in task worktree\n", encoding="utf-8")
            run(["git", "add", "README.md"], worktree, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Task change",
                ],
                worktree,
                check=True,
            )
            write_valid_receipt(worktree, "AGW-090", ["README.md"])

            result = run(["make", "agent-task-ready", "TASK_READY_JSON=1"], worktree)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["ready"])
            self.assertEqual(report["scope_drift_files"], [])
            self.assertTrue(report["receipt_validation"]["passed"])
            self.assertEqual(report["goal_check"]["summary"]["unknown"], 1)
            self.assertTrue(any("Goal-check found changed paths" in warning for warning in report["warnings"]))

    def test_agent_task_ready_blocks_goal_check_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            config = repo / ".agent-workflows" / "area-contracts.json"
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_goal": "Do not change README in this task lane.",
                        "path_contracts": [
                            {"path": "README.md", "purpose": "Frozen public overview", "status": "conflict"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            run(["git", "add", ".agent-workflows/area-contracts.json"], repo, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Declare README conflict area",
                ],
                repo,
                check=True,
            )
            worktree, _ = prepare_task(repo, "AGW-091", "README.md")

            (worktree / "README.md").write_text("# Conflict change\n", encoding="utf-8")
            run(["git", "add", "README.md"], worktree, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Task change",
                ],
                worktree,
                check=True,
            )
            write_valid_receipt(worktree, "AGW-091", ["README.md"])

            result = run(["make", "agent-task-ready", "TASK_READY_JSON=1"], worktree)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["ready"])
            self.assertEqual(report["goal_check"]["summary"]["conflict"], 1)
            self.assertIn("Goal-check found changed paths marked as conflict with the repo goal.", report["blockers"])

    def test_agent_task_ready_blocks_scope_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            worktree, _ = prepare_task(repo, "AGW-091", "docs")

            (worktree / "README.md").write_text("# Drifted change\n", encoding="utf-8")
            run(["git", "add", "README.md"], worktree, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Out of scope change",
                ],
                worktree,
                check=True,
            )
            write_valid_receipt(worktree, "AGW-091", ["README.md"])

            result = run(["make", "agent-task-ready", "TASK_READY_JSON=1"], worktree)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertIn("README.md", report["scope_drift_files"])

    def test_agent_task_ready_blocks_stale_base_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            worktree, _ = prepare_task(repo, "AGW-092", "README.md")

            (worktree / "README.md").write_text("# Task change\n", encoding="utf-8")
            run(["git", "add", "README.md"], worktree, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Task change",
                ],
                worktree,
                check=True,
            )
            (repo / "README.md").write_text("# Main moved ahead\n", encoding="utf-8")
            run(["git", "add", "README.md"], repo, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Advance base branch",
                ],
                repo,
                check=True,
            )
            write_valid_receipt(worktree, "AGW-092", ["README.md"])

            result = run(["make", "agent-task-ready", "TASK_READY_JSON=1"], worktree)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["branch_freshness"]["fresh"])

    def test_agent_task_ready_blocks_invalid_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            worktree, _ = prepare_task(repo, "AGW-093", "README.md")

            (worktree / "README.md").write_text("# Changed\n", encoding="utf-8")
            run(["git", "add", "README.md"], worktree, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Task change",
                ],
                worktree,
                check=True,
            )
            slug = "agw-093"
            receipt_dir = worktree / ".agent-workflows" / "tasks" / slug
            receipt_dir.mkdir(parents=True, exist_ok=True)
            (receipt_dir / "receipt.json").write_text('{"schema_version":1,"run":{"status":"not-run"}}\n', encoding="utf-8")

            result = run(["make", "agent-task-ready", "TASK_READY_JSON=1"], worktree)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["receipt_validation"]["passed"])

    def test_agent_task_ready_blocks_dirty_primary_baseline_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            base = current_branch(repo)
            (repo / "README.md").write_text("# Pre-existing primary dirt\n", encoding="utf-8")
            (repo / "notes.txt").write_text("pre-existing\n", encoding="utf-8")
            prepare = run(
                [
                    "make",
                    "agent-task-prepare",
                    "TASK=AGW-095",
                    "SCOPE=README.md",
                    f"BASE_REF={base}",
                    "DIRTY_PRIMARY_BASELINE=1",
                ],
                repo,
            )
            self.assertEqual(prepare.returncode, 0, prepare.stdout + prepare.stderr)
            metadata = json.loads((repo / ".agent-workflows" / "tasks" / "agw-095.json").read_text(encoding="utf-8"))
            worktree = Path(metadata["worktree"])

            (worktree / "README.md").write_text("# Task change\n", encoding="utf-8")
            run(["git", "add", "README.md"], worktree, check=True)
            run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Task change",
                ],
                worktree,
                check=True,
            )
            write_valid_receipt(worktree, "AGW-095", ["README.md"])

            unchanged = run(["make", "agent-task-ready", "TASK_READY_JSON=1"], worktree)
            self.assertEqual(unchanged.returncode, 0, unchanged.stdout + unchanged.stderr)
            unchanged_report = json.loads(unchanged.stdout)
            self.assertFalse(unchanged_report["primary_checkout_baseline"]["comparison"]["changed_since_baseline"])

            (repo / "README.md").write_text("# Mutated primary dirt\n", encoding="utf-8")
            result = run(["make", "agent-task-ready", "TASK_READY_JSON=1"], worktree)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["primary_checkout_baseline"]["comparison"]["changed_since_baseline"])
            self.assertIn(
                "Primary checkout changed since dirty baseline; inspect the primary checkout before handoff or finalize.",
                report["blockers"],
            )


if __name__ == "__main__":
    unittest.main()
