import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_agentic_regression_artifacts as regression_artifacts


class TaskPacketContractTests(unittest.TestCase):
    def fixture_packet(self) -> dict:
        suite = regression_artifacts.load_json(regression_artifacts.FIXTURE_SUITE)
        return regression_artifacts.build_task_packet(suite["fixtures"][0])

    def test_schema_requires_goal_alignment_contract(self):
        schema = json.loads((ROOT / "schemas" / "task-packet.schema.json").read_text(encoding="utf-8"))
        self.assertIn("goal_alignment", schema["required"])

        alignment = schema["properties"]["goal_alignment"]
        for field in [
            "repo_goal",
            "area_contracts",
            "alignment_decision",
            "adaptation_needed",
            "stop_conditions",
        ]:
            self.assertIn(field, alignment["required"])

        self.assertEqual(alignment["properties"]["adaptation_needed"]["type"], "boolean")
        self.assertEqual(
            alignment["properties"]["alignment_decision"]["enum"],
            ["aligned", "unknown", "conflict", "adaptation-needed"],
        )

        area = alignment["properties"]["area_contracts"]["items"]
        for field in ["path", "purpose", "status"]:
            self.assertIn(field, area["required"])
        self.assertIn("unknown", area["properties"]["status"]["enum"])
        self.assertIn("conflict", area["properties"]["status"]["enum"])

    def test_schema_requires_closeout_first_contract(self):
        schema = json.loads((ROOT / "schemas" / "task-packet.schema.json").read_text(encoding="utf-8"))
        self.assertIn("previous_task_state", schema["required"])
        self.assertIn("closeout_required_before_start", schema["required"])

        previous = schema["properties"]["previous_task_state"]
        for field in [
            "report_sources",
            "active_tasks",
            "unresolved_blockers",
            "dirty_or_stale_state",
            "finalizer_receipt_paths",
            "blocker_receipt_paths",
            "allowed_to_start",
        ]:
            self.assertIn(field, previous["required"])

        gate = schema["properties"]["closeout_required_before_start"]
        self.assertEqual(
            gate["properties"]["decision"]["enum"],
            ["safe-start", "refuse-start", "blocker-escalation"],
        )

    def test_schema_allows_optional_phase_files_contract(self):
        schema = json.loads((ROOT / "schemas" / "task-packet.schema.json").read_text(encoding="utf-8"))
        self.assertIn("phase_files", schema["properties"])
        self.assertNotIn("phase_files", schema["required"])

        phase_files = schema["properties"]["phase_files"]
        for field in ["needed", "reason", "phases"]:
            self.assertIn(field, phase_files["required"])
        phase = phase_files["properties"]["phases"]["items"]
        for field in ["id", "title", "objective", "allowed_scope", "completion_evidence"]:
            self.assertIn(field, phase["required"])

    def test_task_packet_prompts_and_template_name_goal_alignment_stop_states(self):
        prompt_paths = [
            ROOT / "workflows" / "prompts" / "task-packet.md",
            ROOT / "workflows" / "prompts" / "templates" / "task-packet.md",
            ROOT / ".codex" / "prompts" / "task-packet.md",
            ROOT / ".codex" / "prompts" / "templates" / "task-packet.md",
        ]
        for path in prompt_paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                for field in [
                    "repo_goal",
                    "area_contracts",
                    "alignment_decision",
                    "adaptation_needed",
                ]:
                    self.assertIn(field, content)
                self.assertIn("unknown", content)
                self.assertIn("conflict", content)
                self.assertIn("stop", content.lower())

    def test_task_packet_prompts_and_template_name_closeout_first_gate(self):
        prompt_paths = [
            ROOT / "workflows" / "prompts" / "task-packet.md",
            ROOT / "workflows" / "prompts" / "templates" / "task-packet.md",
            ROOT / ".codex" / "prompts" / "task-packet.md",
            ROOT / ".codex" / "prompts" / "templates" / "task-packet.md",
        ]
        for path in prompt_paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                for phrase in [
                    "previous_task_state",
                    "closeout_required_before_start",
                    "safe-start",
                    "refuse-start",
                    "blocker-escalation",
                    "finalizer",
                    "blocker receipt",
                ]:
                    self.assertIn(phrase, content)

    def test_task_packet_prompts_and_template_name_phase_files(self):
        prompt_paths = [
            ROOT / "workflows" / "prompts" / "task-packet.md",
            ROOT / "workflows" / "prompts" / "templates" / "task-packet.md",
            ROOT / ".codex" / "prompts" / "task-packet.md",
            ROOT / ".codex" / "prompts" / "templates" / "task-packet.md",
        ]
        for path in prompt_paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                for phrase in [
                    "phase_files",
                    "completion_evidence",
                    "handoff_notes",
                    "fresh session",
                ]:
                    self.assertIn(phrase, content)

    def test_implementation_and_verification_prompts_consume_phase_files(self):
        prompt_paths = [
            ROOT / "workflows" / "prompts" / "fix-planner.md",
            ROOT / "workflows" / "prompts" / "fix-implementer.md",
            ROOT / "workflows" / "prompts" / "verification-sentinel.md",
            ROOT / ".codex" / "prompts" / "fix-planner.md",
            ROOT / ".codex" / "prompts" / "fix-implementer.md",
            ROOT / ".codex" / "prompts" / "verification-sentinel.md",
        ]
        for path in prompt_paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn("phase_files", content)
                self.assertIn("phase", content.lower())

    def test_generated_regression_task_packets_include_goal_alignment_defaults(self):
        packet = self.fixture_packet()
        alignment = packet["goal_alignment"]

        self.assertEqual(alignment["alignment_decision"], "aligned")
        self.assertFalse(alignment["adaptation_needed"])
        self.assertTrue(alignment["repo_goal"])
        self.assertTrue(alignment["area_contracts"])
        self.assertTrue(alignment["stop_conditions"])

        errors: list[str] = []
        schema = regression_artifacts.load_json(regression_artifacts.TASK_PACKET_SCHEMA)
        regression_artifacts.validate_task_packet(packet, schema, "test packet", errors)
        self.assertEqual([], errors)

    def test_generated_regression_task_packets_include_closeout_first_defaults(self):
        packet = self.fixture_packet()
        previous = packet["previous_task_state"]
        gate = packet["closeout_required_before_start"]

        self.assertTrue(previous["allowed_to_start"])
        self.assertTrue(previous["report_sources"])
        self.assertTrue(previous["finalizer_receipt_paths"])
        self.assertEqual(gate["decision"], "safe-start")

        errors: list[str] = []
        schema = regression_artifacts.load_json(regression_artifacts.TASK_PACKET_SCHEMA)
        regression_artifacts.validate_task_packet(packet, schema, "safe packet", errors)
        self.assertEqual([], errors)

    def test_missing_closeout_first_fields_fail_contract_validation(self):
        schema = regression_artifacts.load_json(regression_artifacts.TASK_PACKET_SCHEMA)

        for field in ["previous_task_state", "closeout_required_before_start"]:
            packet = self.fixture_packet()
            packet.pop(field)
            errors: list[str] = []
            regression_artifacts.validate_task_packet(packet, schema, f"missing {field}", errors)
            self.assertTrue(any(field in error for error in errors), errors)

    def test_blocker_escalation_packet_with_blocker_receipt_validates(self):
        packet = self.fixture_packet()
        packet["previous_task_state"]["allowed_to_start"] = False
        packet["previous_task_state"]["finalizer_receipt_paths"] = []
        packet["previous_task_state"]["blocker_receipt_paths"] = [
            ".agent-workflows/tasks/agw-056-arf-001/blocker-receipt.json"
        ]
        packet["previous_task_state"]["unresolved_blockers"] = [
            "previous task finalizer is missing"
        ]
        packet["closeout_required_before_start"] = {
            "decision": "blocker-escalation",
            "reason": "Previous task closeout is unresolved.",
            "required_next_step": "Run the task finalizer or record an owner blocker before implementation.",
            "evidence_paths": [
                ".agent-workflows/tasks/agw-056-arf-001/blocker-receipt.json"
            ],
        }

        errors: list[str] = []
        schema = regression_artifacts.load_json(regression_artifacts.TASK_PACKET_SCHEMA)
        regression_artifacts.validate_task_packet(packet, schema, "blocker packet", errors)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
