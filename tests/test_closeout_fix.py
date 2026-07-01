import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "repo_contract_kit.py"
sys.path.insert(0, str(ROOT / "scripts"))
import closeout_fix  # noqa: E402


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)


def init_git_repo(path: Path) -> None:
    run(["git", "init", "-q"], cwd=path)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=path)
    result = run(
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
        cwd=path,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def write_agent(path: Path, body: str) -> Path:
    script = path / "agent.py"
    script.write_text("#!/usr/bin/env python3\n" + textwrap.dedent(body), encoding="utf-8")
    script.chmod(0o755)
    return script


def write_fake_codex(path: Path, help_text: str) -> Path:
    script = path / "codex"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "if sys.argv[1:3] == ['exec', '--help']:\n"
        f"    print({help_text!r})\n"
        "    raise SystemExit(0)\n"
        "print('fake codex')\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def cli(args: list[str], *, cwd: Path, state_home: Path) -> subprocess.CompletedProcess[str]:
    return run([sys.executable, str(CLI), *args], cwd=cwd, env={**os.environ, "XDG_STATE_HOME": str(state_home)})


def json_payload(result: subprocess.CompletedProcess[str]) -> dict:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON stdout:\n{result.stdout}\nstderr:\n{result.stderr}") from exc


class CloseoutFixCliTests(unittest.TestCase):
    def test_codex_runner_uses_current_noninteractive_flag_when_advertised(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = write_fake_codex(root, "--dangerously-bypass-approvals-and-sandbox\n--sandbox")
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{root}{os.pathsep}{old_path}"
            try:
                runner, blockers = closeout_fix.resolve_runner("codex", None)
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(blockers, [])
            self.assertEqual(runner["binary"], str(codex))
            self.assertIn("--dangerously-bypass-approvals-and-sandbox", runner["command"])
            self.assertNotIn("--ask-for-approval", runner["command"])

    def test_codex_runner_keeps_legacy_approval_flags_when_needed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = write_fake_codex(root, "--sandbox\n--ask-for-approval")
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{root}{os.pathsep}{old_path}"
            try:
                runner, blockers = closeout_fix.resolve_runner("codex", None)
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(blockers, [])
            self.assertEqual(runner["binary"], str(codex))
            self.assertIn("--ask-for-approval", runner["command"])
            self.assertIn("never", runner["command"])

    def test_preview_reports_plan_without_target_or_sidecar_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            state_home = root / "state"
            init_git_repo(repo)
            (repo / "feature.txt").write_text("dirty\n", encoding="utf-8")
            agent = write_agent(root, "import sys\nsys.stdin.read()\n")

            result = cli(
                [
                    "closeout-fix",
                    "--repo",
                    str(repo),
                    "--json",
                    "--agent",
                    "custom",
                    "--agent-command",
                    str(agent),
                ],
                cwd=ROOT,
                state_home=state_home,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json_payload(result)
            self.assertEqual(payload["command"], "closeout-fix")
            self.assertEqual(payload["mode"], "preview")
            self.assertEqual(payload["result"], "preview")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse(Path(payload["sidecar_state"]["repo_state_dir"]).exists())
            self.assertEqual(run(["git", "rev-list", "--count", "HEAD"], cwd=repo).stdout.strip(), "1")

    def test_apply_with_stub_agent_creates_multiple_commits_and_receipt_without_push(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            state_home = root / "state"
            init_git_repo(repo)
            (repo / "README.md").write_text("# Sample repo\n\nDocs lane.\n", encoding="utf-8")
            (repo / "src.py").write_text("print('code lane')\n", encoding="utf-8")
            agent = write_agent(
                root,
                """
                import json
                import os
                import subprocess
                import sys
                from pathlib import Path

                sys.stdin.read()
                repo = Path(os.environ["KIT_CLOSEOUT_FIX_REPO"])
                identity = ["-c", "user.name=stub agent", "-c", "user.email=stub@example.invalid"]
                subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
                subprocess.run(["git", *identity, "commit", "-qm", "Document closeout lane"], cwd=repo, check=True)
                subprocess.run(["git", "add", "src.py"], cwd=repo, check=True)
                subprocess.run(["git", *identity, "commit", "-qm", "Add code lane"], cwd=repo, check=True)
                print(json.dumps({"event": "stub-agent", "status": "committed"}))
                """,
            )

            result = cli(
                [
                    "closeout-fix",
                    "--repo",
                    str(repo),
                    "--apply",
                    "--no-push",
                    "--json",
                    "--agent",
                    "custom",
                    "--agent-command",
                    str(agent),
                ],
                cwd=ROOT,
                state_home=state_home,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json_payload(result)
            self.assertEqual(payload["result"], "applied")
            self.assertTrue(payload["no_push"])
            self.assertEqual([commit["subject"] for commit in payload["commits"]], ["Document closeout lane", "Add code lane"])
            self.assertEqual(payload["branches_pushed"], [])
            self.assertTrue(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertEqual(payload["after"]["status_entries"], [])
            receipt = Path(payload["receipts"][0]["path"])
            self.assertTrue(receipt.exists())
            saved = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(saved["job_id"], payload["job_id"])
            self.assertEqual(saved["final_closeout"]["can_claim_done"], True)

    def test_apply_jsonl_streams_events_and_final_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            state_home = root / "state"
            init_git_repo(repo)
            (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
            agent = write_agent(
                root,
                """
                import json
                import os
                import subprocess
                import sys
                from pathlib import Path

                sys.stdin.read()
                repo = Path(os.environ["KIT_CLOSEOUT_FIX_REPO"])
                subprocess.run(["git", "add", "feature.txt"], cwd=repo, check=True)
                subprocess.run([
                    "git",
                    "-c",
                    "user.name=stub agent",
                    "-c",
                    "user.email=stub@example.invalid",
                    "commit",
                    "-qm",
                    "Add feature",
                ], cwd=repo, check=True)
                print(json.dumps({"event": "stub-agent", "status": "done"}))
                """,
            )

            result = cli(
                [
                    "closeout-fix",
                    "--repo",
                    str(repo),
                    "--apply",
                    "--no-push",
                    "--jsonl",
                    "--agent",
                    "custom",
                    "--agent-command",
                    str(agent),
                ],
                cwd=ROOT,
                state_home=state_home,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
            self.assertIn("job-started", [event["event"] for event in events])
            self.assertIn("runner-started", [event["event"] for event in events])
            self.assertIn("agent-output", [event["event"] for event in events])
            self.assertEqual(events[-1]["event"], "final-payload")
            self.assertEqual(events[-1]["payload"]["result"], "applied")

    def test_apply_blocks_when_custom_runner_is_not_configured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            state_home = root / "state"
            init_git_repo(repo)

            result = cli(
                ["closeout-fix", "--repo", str(repo), "--apply", "--json", "--agent", "custom"],
                cwd=ROOT,
                state_home=state_home,
            )

            self.assertEqual(result.returncode, 1)
            payload = json_payload(result)
            self.assertEqual(payload["result"], "blocked")
            self.assertIn("--agent custom requires --agent-command.", payload["blockers"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertTrue(Path(payload["receipts"][0]["path"]).exists())

    def test_final_closeout_failure_blocks_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            state_home = root / "state"
            init_git_repo(repo)
            (repo / "still_dirty.txt").write_text("dirty\n", encoding="utf-8")
            agent = write_agent(root, "import sys\nsys.stdin.read()\nprint('{\"event\":\"noop\"}')\n")

            result = cli(
                [
                    "closeout-fix",
                    "--repo",
                    str(repo),
                    "--apply",
                    "--no-push",
                    "--json",
                    "--agent",
                    "custom",
                    "--agent-command",
                    str(agent),
                ],
                cwd=ROOT,
                state_home=state_home,
            )

            self.assertEqual(result.returncode, 1)
            payload = json_payload(result)
            self.assertEqual(payload["result"], "blocked")
            self.assertIn("Final strict closeout-plan did not pass.", payload["blockers"])
            self.assertIn("?? still_dirty.txt", "\n".join(run(["git", "status", "--short"], cwd=repo).stdout.splitlines()))

    def test_push_rejection_is_reported_without_force_push(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            remote = root / "remote.git"
            repo.mkdir()
            state_home = root / "state"
            init_git_repo(repo)
            run(["git", "init", "--bare", "-q", str(remote)], cwd=root)
            hooks = remote / "hooks"
            hook = hooks / "pre-receive"
            hook.write_text("#!/bin/sh\necho rejected by test hook >&2\nexit 1\n", encoding="utf-8")
            hook.chmod(0o755)
            run(["git", "remote", "add", "origin", str(remote)], cwd=repo)
            (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
            agent = write_agent(
                root,
                """
                import os
                import subprocess
                import sys
                from pathlib import Path

                sys.stdin.read()
                repo = Path(os.environ["KIT_CLOSEOUT_FIX_REPO"])
                subprocess.run(["git", "add", "feature.txt"], cwd=repo, check=True)
                subprocess.run([
                    "git",
                    "-c",
                    "user.name=stub agent",
                    "-c",
                    "user.email=stub@example.invalid",
                    "commit",
                    "-qm",
                    "Add rejected push feature",
                ], cwd=repo, check=True)
                """,
            )

            result = cli(
                [
                    "closeout-fix",
                    "--repo",
                    str(repo),
                    "--apply",
                    "--json",
                    "--agent",
                    "custom",
                    "--agent-command",
                    str(agent),
                ],
                cwd=ROOT,
                state_home=state_home,
            )

            self.assertEqual(result.returncode, 1)
            payload = json_payload(result)
            self.assertEqual(payload["result"], "blocked")
            self.assertEqual(payload["branches_pushed"][0]["exit_code"], 1)
            self.assertNotIn("--force", payload["branches_pushed"][0]["command"])
            self.assertTrue(any("git push failed" in blocker for blocker in payload["blockers"]))

    def test_apply_prunes_only_clean_disposable_worktrees(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            worktree = root / "repo-agent-worktrees" / "TASK-1"
            repo.mkdir()
            state_home = root / "state"
            init_git_repo(repo)
            add = run(["git", "worktree", "add", "-q", "-b", "codex/task-1", str(worktree)], cwd=repo)
            self.assertEqual(add.returncode, 0, add.stderr)
            agent = write_agent(root, "import sys\nsys.stdin.read()\nprint('{\"event\":\"noop\"}')\n")

            result = cli(
                [
                    "closeout-fix",
                    "--repo",
                    str(repo),
                    "--apply",
                    "--no-push",
                    "--json",
                    "--agent",
                    "custom",
                    "--agent-command",
                    str(agent),
                ],
                cwd=ROOT,
                state_home=state_home,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json_payload(result)
            self.assertEqual(payload["result"], "applied")
            self.assertEqual(payload["worktrees_pruned"], [{"branch": "codex/task-1", "path": str(worktree.resolve())}])
            self.assertFalse(worktree.exists())


if __name__ == "__main__":
    unittest.main()
