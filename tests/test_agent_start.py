import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"
sys.path.insert(0, str(ROOT / "scripts"))

import agent_start
from classify_review_risk import classify_paths


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


def install(repo: Path, preset="agentic"):
    result = run([sys.executable, str(INSTALL), str(repo), "--preset", preset], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def commit_all(repo: Path):
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


def latest_run_dir(repo: Path):
    runs = sorted(path for path in (repo / ".agent-workflows" / "runs").iterdir() if path.is_dir())
    if not runs:
        raise AssertionError("No agent-start run directory found")
    return runs[-1]


def read_packet(repo: Path):
    run_dir = latest_run_dir(repo)
    return (
        json.loads((run_dir / "session-start.json").read_text(encoding="utf-8")),
        json.loads((run_dir / "receipt.template.json").read_text(encoding="utf-8")),
        (run_dir / "agent-brief.md").read_text(encoding="utf-8"),
    )


class AgentStartTests(unittest.TestCase):
    def test_agent_start_uses_standalone_classifier_routing(self):
        paths = ["api/users.py", "scripts/purge_accounts.py"]

        result = agent_start.classify_review_risk(paths)
        expected = classify_paths(paths)

        for key in ["changed_files", "risk_tier", "trust_profile", "recommended_personas", "triggers", "guidance"]:
            self.assertEqual(result[key], expected[key])
        self.assertIn(".codex/prompts/policies/review-risk-classifier.md", result["policy_docs"])

    def test_default_packet_creation_includes_adr_and_receipt_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            commit_all(repo)

            result = run([sys.executable, "scripts/agent_start.py"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, receipt, brief = read_packet(repo)
            self.assertEqual(packet["mode"], "bootstrap")
            self.assertEqual(packet["latest_adr"]["path"], "docs/adr/0001-testing-philosophy.md")
            self.assertIn("Treat latest ADRs as constraints/defaults", brief)
            self.assertEqual(receipt["schema_version"], 1)
            self.assertEqual(receipt["run"]["mode"], "bootstrap")
            self.assertEqual(receipt["tooling"]["local_only"], True)
            self.assertIn("evidence", receipt)
            self.assertEqual(packet["kit"]["status"], "managed")
            self.assertEqual(packet["versioning"]["target_version"]["current"], "0.1.0")
            self.assertEqual(packet["backlog"]["task_packet_prompt"], ".codex/prompts/task-packet.md")
            self.assertEqual(packet["backlog"]["task_packet_schema"], "schemas/task-packet.schema.json")
            self.assertTrue(packet["goal_check"]["config"]["exists"])
            self.assertEqual(packet["goal_check"]["summary"]["total"], 0)
            freshness = packet["task_start_freshness"]
            self.assertEqual(freshness["policy"]["selected"], "report-only")
            self.assertFalse(freshness["policy"]["auto_apply_performed"])
            self.assertFalse(freshness["policy"]["target_repo_writes"]["performed"])
            self.assertFalse(freshness["repo_cleanliness"]["dirty"])
            self.assertEqual(freshness["backlog_source"]["selected_source"], packet["backlog"]["selected_source"])
            self.assertIn("global_tool", freshness["kit_drift"])
            self.assertIn("target_install", freshness["kit_drift"])
            self.assertIn("make agent-task-packet", packet["next_commands"])
            self.assertEqual(packet["review_risk"]["risk_tier"], "low")
            self.assertEqual(packet["review_risk"]["trust_profile"], "read-only-review")
            self.assertEqual(receipt["review_risk"]["risk_tier"], "low")
            self.assertIn("Kit And Versioning", brief)
            self.assertIn("Task Start Freshness", brief)
            self.assertIn("Backlog And Task Packets", brief)
            self.assertIn("Goal And Area Check", brief)
            self.assertIn("Review Risk And Tool Boundary", brief)

    def test_agentic_packet_includes_backlog_mirror_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            (repo / "docs").mkdir(exist_ok=True)
            (repo / "docs" / "backlog.md").write_text(
                "# Backlog\n\n- [ ] AGW-001 Add a portable review runner\n",
                encoding="utf-8",
            )
            commit_all(repo)

            result = run([sys.executable, "scripts/agent_start.py"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, _, brief = read_packet(repo)
            self.assertTrue(packet["backlog"]["mirror_present"])
            self.assertEqual(packet["backlog"]["mirror_path"], "docs/backlog.md")
            self.assertGreater(packet["backlog"]["open_item_count"], 0)
            self.assertEqual(packet["backlog"]["task_packet_prompt"], ".codex/prompts/task-packet.md")
            self.assertIn("docs/backlog.md", brief)
            self.assertIn("task packet", brief.lower())

    def test_agentic_packet_uses_csv_backlog_source_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            backlog_dir = repo / "research" / "agentic-workflow-review"
            backlog_dir.mkdir(parents=True)
            (backlog_dir / "backlog.csv").write_text(
                "id,priority,repo,theme,item,status,completion_note\n"
                "AGW-001,P1,repo-contract-kit,docs,Align startup backlog source,open,\n"
                "AGW-002,P2,repo-contract-kit,docs,Document old flow,done,Shipped\n",
                encoding="utf-8",
            )
            commit_all(repo)

            result = run([sys.executable, "scripts/agent_start.py"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, _, brief = read_packet(repo)
            self.assertTrue(packet["backlog"]["mirror_present"])
            self.assertEqual(packet["backlog"]["mirror_path"], "research/agentic-workflow-review/backlog.csv")
            self.assertEqual(packet["backlog"]["open_item_count"], 1)
            self.assertEqual(packet["backlog"]["done_item_count"], 1)
            self.assertEqual(packet["backlog"]["next_open_item"]["id"], "AGW-001")
            self.assertEqual(
                packet["task_start_freshness"]["backlog_source"]["selected_source"],
                "research/agentic-workflow-review/backlog.csv",
            )
            self.assertIn("research/agentic-workflow-review/backlog.csv", brief)
            self.assertIn("Backlog source", brief)

    def test_task_start_freshness_reports_stale_target_without_auto_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            receipt_path = repo / ".doc-contract-kit" / "install.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["kit_version"] = "0.0.1"
            receipt["source_version"] = "0.0.1"
            receipt["source_ref"] = "old-source-ref"
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            commit_all(repo)

            result = run([sys.executable, "scripts/agent_start.py"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, _, brief = read_packet(repo)
            freshness = packet["task_start_freshness"]
            self.assertEqual(freshness["kit_drift"]["classification"], "stale")
            self.assertEqual(freshness["policy"]["recommended"], "dry-run")
            self.assertFalse(freshness["policy"]["auto_apply_performed"])
            modes = {mode["id"]: mode for mode in freshness["safe_update_modes"]}
            self.assertTrue(modes["dry-run"]["enabled"])
            self.assertTrue(modes["dry-run"]["eligible"])
            self.assertEqual(modes["dry-run"]["writes"], "none")
            self.assertFalse(modes["auto-update-clean"]["enabled"])
            self.assertTrue(modes["auto-update-clean"]["eligible"])
            self.assertIn("kit update --dry-run", modes["dry-run"]["command"])
            self.assertTrue(any("Task-start freshness found kit drift" in warning for warning in packet["warnings"]))
            self.assertIn("recommended next mode: `dry-run`", brief)

    def test_make_mode_override_sets_packet_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            commit_all(repo)

            result = run(["make", "agent-start", "MODE=test-first"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, receipt, _ = read_packet(repo)
            self.assertEqual(packet["mode"], "test-first")
            self.assertEqual(packet["prompt_paths"], [".codex/prompts/tdd/README.md"])
            self.assertEqual(receipt["run"]["mode"], "test-first")

    def test_repeated_agent_start_in_same_second_uses_unique_run_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            commit_all(repo)

            first = run(["make", "agent-start"], repo)
            second = run(["make", "agent-start"], repo)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            runs = sorted(path for path in (repo / ".agent-workflows" / "runs").iterdir() if path.is_dir())
            self.assertGreaterEqual(len(runs), 2)
            self.assertNotEqual(runs[-2].name, runs[-1].name)

    def test_no_adr_fallback_warns_but_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "minimal")
            commit_all(repo)

            result = run(["make", "agent-start"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, _, _ = read_packet(repo)
            self.assertIsNone(packet["latest_adr"])
            self.assertTrue(any("No current ADR found" in warning for warning in packet["warnings"]))

    def test_check_failures_are_recorded_as_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            commit_all(repo)
            with (repo / "AGENTS.md").open("a", encoding="utf-8") as handle:
                handle.write("\nRead `docs/missing.md` before editing.\n")

            result = run(["make", "agent-start"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, _, _ = read_packet(repo)
            lint_check = next(check for check in packet["checks"] if check["name"] == "agent-docs-lint")
            self.assertEqual(lint_check["result"], "fail")
            self.assertTrue(any("agent-docs-lint returned fail" in warning for warning in packet["warnings"]))

    def test_persona_recommendation_adds_specialists_for_changed_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            commit_all(repo)
            (repo / "api").mkdir()
            (repo / "api" / "users.py").write_text("USERS = []\n", encoding="utf-8")

            result = run(["make", "agent-start"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, _, _ = read_packet(repo)
            persona_ids = [persona["id"] for persona in packet["recommended_personas"]]
            self.assertEqual(persona_ids[:4], ["doc-code-delta", "ai-code-slop", "test-behavior-risk", "reuse-architecture"])
            self.assertIn("api-data-contracts", persona_ids)
            self.assertEqual(packet["review_risk"]["risk_tier"], "high")
            self.assertTrue(any(trigger["rule_id"] == "public-api-or-contract" for trigger in packet["review_risk"]["triggers"]))
            self.assertTrue(packet["versioning"]["consider_bump"])
            self.assertEqual(packet["goal_check"]["summary"]["unknown"], 1)
            self.assertTrue(any("Goal-check found changed paths" in warning for warning in packet["warnings"]))

    def test_review_risk_marks_destructive_paths_critical(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "agentic")
            commit_all(repo)
            (repo / "scripts").mkdir(exist_ok=True)
            (repo / "scripts" / "purge_accounts.py").write_text("print('purge')\n", encoding="utf-8")

            result = run(["make", "agent-start"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, receipt, brief = read_packet(repo)
            self.assertEqual(packet["review_risk"]["risk_tier"], "critical")
            self.assertEqual(packet["review_risk"]["trust_profile"], "untrusted-pr")
            self.assertEqual(receipt["review_risk"]["risk_tier"], "critical")
            self.assertIn("agent-tool-network-allowlist.md", brief)

    def test_minimal_profile_warns_when_prompt_files_are_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install(repo, "minimal")
            commit_all(repo)

            result = run(["make", "agent-start"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet, _, _ = read_packet(repo)
            self.assertTrue(any("--preset agentic" in warning for warning in packet["warnings"]))


if __name__ == "__main__":
    unittest.main()
