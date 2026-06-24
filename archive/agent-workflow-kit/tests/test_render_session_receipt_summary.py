import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "scripts" / "render_session_receipt_summary.py"


def sample_receipt():
    return {
        "schema_version": 1,
        "run": {
            "id": "run-123",
            "started_at": "2026-05-13T00:00:00+00:00",
            "completed_at": "2026-05-13T00:04:00+00:00",
            "mode": "pull-request",
            "status": "pass-with-caveats",
        },
        "tooling": {
            "agent_tool": "codex",
            "agent_tool_version": "test",
            "local_only": True,
            "network_used": False,
            "notes": "",
        },
        "scope": {
            "repo_root": "/tmp/repo",
            "base_ref": "main",
            "changed_files": ["scripts/example.py", "README.md"],
            "allowed_files": [],
            "protected_files": [],
        },
        "evidence": {
            "files_inspected": ["scripts/example.py", "tests/test_example.py"],
            "commands": [
                {"command": "python3 -m unittest", "result": "pass", "exit_code": 0, "notes": ""},
                {"command": "make docs-check", "result": "blocked", "exit_code": None, "notes": "no Makefile"},
            ],
            "docs_impact": {
                "checked": True,
                "result": "pass",
                "categories": ["cli"],
                "waiver_reason": None,
            },
            "tests": {
                "result": "red-green",
                "failing_test_evidence": "test failed before implementation",
                "passing_test_evidence": "test passed after implementation",
                "generated_test_provenance": "human-authored",
                "skip_reason": None,
            },
        },
        "findings": [
            {
                "id": "FINDING_001",
                "priority": "P1",
                "area": "cli",
                "title": "Example finding",
                "confidence": "high",
                "evidence": ["scripts/example.py:1"],
                "recommendation": "Fix it.",
                "status": "accepted",
                "false_positive_notes": "none",
            }
        ],
        "disposition": {
            "summary": "Review completed with one accepted finding.",
            "next_actions": ["Ship the fix."],
            "human_approval_required": False,
        },
    }


class RenderSessionReceiptSummaryTests(unittest.TestCase):
    def test_receipt_summary_is_human_readable_and_concise(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps(sample_receipt()), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(RENDER), str(receipt_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Session Receipt Summary", result.stdout)
            self.assertIn("run-123", result.stdout)
            self.assertIn("pass-with-caveats", result.stdout)
            self.assertIn("Changed files: 2", result.stdout)
            self.assertIn("Commands: 1 pass, 1 blocked", result.stdout)
            self.assertIn("Tests: red-green", result.stdout)
            self.assertIn("P1: 1", result.stdout)
            self.assertIn("Ship the fix.", result.stdout)
            self.assertNotIn("## Metrics", result.stdout)

    def test_receipt_summary_renders_optional_metrics_when_present(self):
        receipt = copy.deepcopy(sample_receipt())
        receipt["harness_metrics"] = {
            "review_outcome": {
                "findings_total": 5,
                "findings_accepted": 2,
                "findings_fixed": 1,
                "findings_rejected": 1,
                "findings_duplicate": 1,
                "findings_false_positive": 1,
                "false_positive_rate": 0.2,
                "duplicate_rate": 0.2,
                "review_yield_count": 3,
                "review_yield_rate": 0.6,
                "human_decision_count": 4,
                "notes": "Rates use emitted findings as the denominator.",
            },
            "effort": {
                "duration_ms": 90000,
                "first_finding_latency_ms": 10000,
                "time_to_green_ms": 70000,
                "commands_run_count": 2,
                "model_input_tokens": 1200,
                "model_output_tokens": 300,
                "estimated_cost_usd": 0.0123,
                "human_review_minutes": 12.5,
                "human_interruption_count": 1,
                "notes": "Cost is known from the provider report.",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(RENDER), str(receipt_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Metrics", result.stdout)
            self.assertIn("Review outcome: findings 5", result.stdout)
            self.assertIn("yield rate 60%", result.stdout)
            self.assertIn("false-positive rate 20%", result.stdout)
            self.assertIn("duplicate rate 20%", result.stdout)
            self.assertIn("time to green 70000 ms", result.stdout)
            self.assertIn("tokens 1200 in / 300 out", result.stdout)
            self.assertIn("estimated cost $0.0123", result.stdout)
            self.assertIn("human review 12.5 min", result.stdout)
            self.assertIn("Rates use emitted findings as the denominator.", result.stdout)


if __name__ == "__main__":
    unittest.main()
