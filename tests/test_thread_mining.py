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
            url = "https://example.invalid/private/path?token=abc"
            email = "person@example.invalid"
            ip = "192.168.1.55"
            high_entropy = "abc123DEF456ghi789JKL012mno345PQR678"
            write_jsonl(
                codex_home / "sessions/2026/06/thread.jsonl",
                [
                    {"type": "session_meta", "timestamp": "2026-06-26T00:00:01Z", "payload": {"type": "session_meta", "id": raw_thread_id, "cwd": "/Users/example/private/repo"}},
                    {"type": "event_msg", "timestamp": "2026-06-26T00:00:02Z", "payload": {"type": "user_message", "message": f"Fix kit command not found with token {secret} at {url} for {email} from {ip} using {high_entropy}"}},
                    {"type": "response_item", "timestamp": "2026-06-26T00:00:03Z", "payload": {"type": "function_call", "name": "exec_command", "arguments": json.dumps({"cmd": "python3 /Users/example/private/repo/tool.py --token abc123DEF456ghi789JKL012mno345PQR678", "workdir": "/Users/example/private/repo"})}},
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
            summary_json = (state_dir / "thread-mining-summary.json").read_text(encoding="utf-8")
            self.assertNotIn(raw_thread_id, report)
            self.assertNotIn(secret, report)
            for sensitive in (secret, url, email, ip, high_entropy, "/Users/example/private/repo"):
                self.assertNotIn(sensitive, samples)
                self.assertNotIn(sensitive, summary_json)
            self.assertIn("<redacted-secret>", samples)
            self.assertIn("<redacted-url>", samples)
            self.assertIn("<redacted-email>", samples)
            self.assertIn("<redacted-ip>", samples)
            self.assertIn("<redacted-token>", samples)
            self.assertEqual(oct(state_dir.stat().st_mode & 0o777), "0o700")
            self.assertEqual(oct((state_dir / "thread-mining-summary.json").stat().st_mode & 0o777), "0o600")
            self.assertEqual(oct((state_dir / "thread-mining-samples.jsonl").stat().st_mode & 0o777), "0o600")
            self.assertEqual(summary["corpus"]["dev_threads"], 1)
            self.assertIn("outputs", json.loads(summary_json))

    def test_public_summary_omits_observations_by_default(self):
        record = self.module.ThreadRecord(thread_id="thread-kit", title="kit start", cwd="/repo/kit")
        record.add_command("kit start --json")
        summary = self.module.build_summary({"thread-kit": record})

        aggregate_only = self.module.public_summary(summary)
        with_observations = self.module.public_summary(summary, include_observations=True)

        self.assertNotIn("observations", aggregate_only)
        self.assertIn("observations", with_observations)

    def test_filters_kit_related_since_cwd_prefix_and_current_kit_era(self):
        old = self.module.ThreadRecord(thread_id="old", title="kit old", cwd="/repo/kit")
        old.timestamps.append("2026-06-24T23:59:00Z")
        old.add_command("kit status --json")
        current = self.module.ThreadRecord(thread_id="current", title="kit current", cwd="/repo/kit")
        current.timestamps.append("2026-06-25T00:01:00Z")
        current.add_command("kit start --json")
        other = self.module.ThreadRecord(thread_id="other", title="plain dev", cwd="/repo/other")
        other.timestamps.append("2026-06-26T00:01:00Z")
        other.add_command("git status")

        summary = self.module.build_summary(
            {"old": old, "current": current, "other": other},
            kit_related=True,
            since=self.module.CURRENT_KIT_ERA_START,
            cwd_prefixes=["/repo/kit"],
        )

        self.assertEqual(summary["corpus"]["dev_threads"], 1)
        self.assertEqual(summary["observations"][0]["thread_id_hash"], self.module.thread_hash("current"))
        self.assertEqual(summary["filters"]["kit_related"], True)
        self.assertEqual(summary["filters"]["since"], self.module.CURRENT_KIT_ERA_START)

    def test_command_buckets_split_kit_make_shell_and_agent_tools(self):
        record = self.module.ThreadRecord(thread_id="commands", title="command buckets", cwd="/repo/kit")
        record.add_command("kit start --json")
        record.add_command("make agent-start")
        record.add_command("git status --short")
        record.add_command("write_stdin")

        summary = self.module.build_summary({"commands": record})

        self.assertEqual(summary["aggregate"]["kit_commands"]["kit start"], 1)
        self.assertEqual(summary["aggregate"]["make_commands"]["make agent-start"], 1)
        self.assertEqual(summary["aggregate"]["shell_commands"]["git status"], 1)
        self.assertEqual(summary["aggregate"]["agent_tool_calls"]["write_stdin"], 1)

    def test_redaction_and_command_normalization_collapse_private_arguments(self):
        text = (
            "token=sk-proj-abc123456789SECRETSECRET "
            "https://example.invalid/a person@example.invalid 10.0.0.5 "
            "/Volumes/Myrtle/private/repo/tool.py "
            "abc123DEF456ghi789JKL012mno345PQR678"
        )

        redacted = self.module.redact_text(text)

        self.assertIn("<redacted-secret>", redacted)
        self.assertIn("<redacted-url>", redacted)
        self.assertIn("<redacted-email>", redacted)
        self.assertIn("<redacted-ip>", redacted)
        self.assertIn("<redacted-path>", redacted)
        self.assertIn("<redacted-token>", redacted)
        self.assertEqual(
            self.module.normalize_command("python3 /Volumes/Myrtle/private/repo/tool.py --token abc123DEF456ghi789JKL012mno345PQR678"),
            "python3",
        )

    def test_false_positive_friction_patterns_are_not_marked(self):
        record = self.module.ThreadRecord(thread_id="false-positive", title="normal verification", cwd="/repo/kit")
        record.add_text("target_repo_writes=false. Rerun checks after successful usage: kit start --help.")
        record.add_command("kit start --help")

        observation = self.module.observation_for(record)

        self.assertNotIn("unexpected-mutation-risk", observation["friction_markers"])
        self.assertNotIn("retry-loop", observation["friction_markers"])
        self.assertNotIn("command-confusion", observation["friction_markers"])

    def test_direct_script_maintainer_usage_is_not_fallback_friction(self):
        record = self.module.ThreadRecord(thread_id="maintainer-script", title="source checkout", cwd="/repo/kit")
        record.add_text("Use the source-checkout fallback from maintainer direct script docs.")
        record.add_command("python3 scripts/repo_contract_kit.py status --json")

        observation = self.module.observation_for(record)

        self.assertEqual(observation["route_used"], "direct-script")
        self.assertNotIn("direct-script-fallback", observation["friction_markers"])


if __name__ == "__main__":
    unittest.main()
