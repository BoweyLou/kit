import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mine_codex_threads.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mine_codex_threads_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            if isinstance(row, str):
                handle.write(row + "\n")
            else:
                handle.write(json.dumps(row) + "\n")


class ThreadMiningTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_parses_session_index_history_sessions_and_malformed_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / ".codex"
            write_jsonl(
                codex_home / "session_index.jsonl",
                [{"id": "thread-1", "thread_name": "Implement kit start", "updated_at": "2026-06-26T00:00:00Z"}],
            )
            write_jsonl(
                codex_home / "history.jsonl",
                [{"session_id": "thread-1", "ts": "1780000000", "text": "please review this repo"}],
            )
            write_jsonl(
                codex_home / "sessions/2026/06/rollout-thread-1.jsonl",
                [
                    {"type": "session_meta", "timestamp": "2026-06-26T00:00:01Z", "payload": {"type": "session_meta", "id": "thread-1", "cwd": "/Volumes/Myrtle/Code/04_Code/kit"}},
                    {"type": "event_msg", "timestamp": "2026-06-26T00:00:02Z", "payload": {"type": "user_message", "message": "Run kit start --json before editing"}},
                    "{bad json",
                ],
            )
            write_jsonl(
                codex_home / "archived_sessions/rollout-archive.jsonl",
                [
                    {"type": "session_meta", "timestamp": "2026-06-25T00:00:01Z", "payload": {"type": "session_meta", "id": "thread-archive", "cwd": "/Volumes/Myrtle/Code/04_Code/kit"}},
                    {"type": "response_item", "timestamp": "2026-06-25T00:00:02Z", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": "python3 scripts/repo_contract_kit.py status --json"})}},
                ],
            )

            records, source_counts = self.module.collect_threads(codex_home)

            self.assertEqual(source_counts["session_index"], 1)
            self.assertEqual(source_counts["history"], 1)
            self.assertEqual(source_counts["session_files"], 2)
            self.assertIn("thread-1", records)
            self.assertIn("thread-archive", records)
            record = records["thread-1"]
            self.assertEqual(record.title, "Implement kit start")
            self.assertEqual(record.cwd, "/Volumes/Myrtle/Code/04_Code/kit")
            self.assertTrue(any("invalid json line" in warning for warning in record.parse_warnings))

    def test_classifies_kit_start_route(self):
        record = self.module.ThreadRecord(thread_id="thread-kit", title="Start kit flow", cwd="/repo/kit")
        record.add_text("Agent should use kit start --json and then kit mode-check --json")
        record.add_command("kit start --json")
        record.task_complete = True

        observation = self.module.observation_for(record)

        self.assertEqual(observation["route_used"], "kit")
        self.assertIn("kit start", observation["commands_run"])
        self.assertEqual(observation["journey"], "clean-maintenance")
        self.assertEqual(observation["outcome"], "completed")

    def test_classifies_make_agent_route(self):
        record = self.module.ThreadRecord(thread_id="thread-make", title="Agent startup", cwd="/repo/app")
        record.add_text("Use make agent-start and make agent-verify in this repo")
        record.add_command("make agent-start")
        record.add_command("make agent-verify")

        observation = self.module.observation_for(record)

        self.assertEqual(observation["route_used"], "make-agent")
        self.assertIn("make agent-start", observation["commands_run"])
        self.assertEqual(observation["recommended_action"], "no action")

    def test_classifies_direct_script_fallback(self):
        record = self.module.ThreadRecord(thread_id="thread-script", title="Direct script fallback", cwd="/repo/app")
        record.add_command("python3 scripts/repo_contract_kit.py status --repo . --json")

        observation = self.module.observation_for(record)

        self.assertEqual(observation["route_used"], "direct-script")
        self.assertIn("direct-script-fallback", observation["friction_markers"])
        self.assertEqual(observation["recommended_action"], "cli change")

    def test_classifies_release_gated_evidence(self):
        record = self.module.ThreadRecord(thread_id="thread-release", title="Public CLI release", cwd="/repo/kit")
        record.add_text("This changes public CLI behavior, VERSION, CHANGELOG.md, and generated schema docs.")
        record.add_command("make version-check")

        observation = self.module.observation_for(record)

        self.assertEqual(observation["intent"], "release")
        self.assertEqual(observation["journey"], "release-gated")
        self.assertEqual(observation["recommended_action"], "test fixture")

    def test_classifies_blocked_retry_and_parse_error(self):
        record = self.module.ThreadRecord(thread_id="thread-error", title="Parse error", cwd="/repo/kit")
        record.add_text("Retry after unrecognized arguments. The work is blocked by command confusion.")
        record.add_command("kit start --bad-flag")
        record.exit_codes.append(2)
        record.turn_aborted = True

        observation = self.module.observation_for(record)

        self.assertEqual(observation["journey"], "recovery")
        self.assertEqual(observation["outcome"], "blocked")
        self.assertIn("command-confusion", observation["friction_markers"])
        self.assertIn("failed-command", observation["friction_markers"])
        self.assertIn("retry-loop", observation["friction_markers"])

    def test_outputs_are_redacted_and_report_omits_raw_thread_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / ".codex"
            state_dir = Path(tmp) / "state"
            report_path = Path(tmp) / "report.md"
            raw_thread_id = "123e4567-e89b-12d3-a456-426614174000"
            secret = "sk-proj-abc123456789SECRETSECRET"
            write_jsonl(
                codex_home / "sessions/2026/06/thread.jsonl",
                [
                    {"type": "session_meta", "timestamp": "2026-06-26T00:00:01Z", "payload": {"type": "session_meta", "id": raw_thread_id, "cwd": "/Users/example/private/repo"}},
                    {"type": "event_msg", "timestamp": "2026-06-26T00:00:02Z", "payload": {"type": "user_message", "message": f"Fix kit command not found with token {secret}"}},
                    {"type": "response_item", "timestamp": "2026-06-26T00:00:03Z", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": "kit unknown", "workdir": "/Users/example/private/repo"})}},
                    {"type": "response_item", "timestamp": "2026-06-26T00:00:04Z", "payload": {"type": "exec_command_end", "command": ["kit", "unknown"], "exit_code": 2, "aggregated_output": "unknown command"}},
                ],
            )

            summary = self.module.mine_codex_threads(
                codex_home=codex_home,
                state_dir=state_dir,
                report_path=report_path,
                write=True,
            )

            report = report_path.read_text(encoding="utf-8")
            samples = (state_dir / "thread-mining-samples.jsonl").read_text(encoding="utf-8")
            self.assertNotIn(raw_thread_id, report)
            self.assertNotIn(secret, report)
            self.assertNotIn(secret, samples)
            self.assertIn("<redacted-secret>", samples)
            self.assertEqual(summary["corpus"]["dev_threads"], 1)


if __name__ == "__main__":
    unittest.main()
