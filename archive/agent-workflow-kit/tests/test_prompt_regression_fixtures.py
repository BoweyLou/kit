import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_prompt_regression_fixtures.py"
FIXTURE = ROOT / "research" / "prompt-regression-fixtures" / "prompt-regression-fixtures.json"
sys.path.insert(0, str(ROOT / "scripts"))

import run_prompt_regression_fixtures as fixtures  # noqa: E402


class PromptRegressionFixtureTests(unittest.TestCase):
    def test_fixture_shape_records_required_intents_and_expectations(self):
        suite = fixtures.load_suite(FIXTURE)
        cases = suite["cases"]
        intents = {case["intent"] for case in cases}

        self.assertIn("valid-persona-finding", intents)
        self.assertIn("malformed-persona-payload", intents)
        self.assertIn("low-signal-nit-finding", intents)
        self.assertIn("synthesis-duplicate-merged", intents)
        self.assertIn("duplicate-synthesis-findings", intents)
        self.assertIn("comment-docstring-drift-labels", intents)

        for case in cases:
            with self.subTest(case_id=case["id"]):
                self.assertIn(case["payload_type"], {"persona", "synthesis"})
                self.assertIsInstance(case["payload"], dict)
                self.assertIn(case["expected"]["status"], {"pass", "fail"})
                self.assertIn("reason_contains", case["expected"])
                if case["expected"]["status"] == "fail":
                    self.assertTrue(case["expected"]["reason_contains"])

    def test_canonical_fixture_suite_passes(self):
        report = fixtures.run_suite(FIXTURE)
        actual_statuses = {result["case_id"]: result["actual"]["status"] for result in report["results"]}

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["failure_count"], 0)
        self.assertEqual(report["case_count"], len(report["results"]))
        self.assertEqual(actual_statuses["PRF-001"], "pass")
        self.assertEqual(actual_statuses["PRF-002"], "fail")
        self.assertEqual(actual_statuses["PRF-003"], "fail")
        self.assertEqual(actual_statuses["PRF-004"], "pass")
        self.assertEqual(actual_statuses["PRF-005"], "fail")
        self.assertEqual(actual_statuses["PRF-006"], "pass")

    def test_comment_docstring_drift_fixture_preserves_labels(self):
        suite = fixtures.load_suite(FIXTURE)
        case = next(case for case in suite["cases"] if case["id"] == "PRF-006")
        labels = {
            label
            for finding in case["payload"]["findings"]
            for label in finding.get("labels", [])
        }

        self.assertIn("comment-drift", labels)
        self.assertIn("docstring-drift", labels)
        self.assertIn("stale-comment", labels)
        self.assertIn("misleading-comment", labels)
        self.assertIn("stale-docstring", labels)

    def test_runner_exits_nonzero_when_expected_output_is_wrong(self):
        suite = fixtures.load_suite(FIXTURE)
        failing_suite = {
            "schema_version": suite["schema_version"],
            "suite": suite["suite"],
            "cases": [json.loads(json.dumps(suite["cases"][0]))],
        }
        failing_suite["cases"][0]["expected"]["status"] = "fail"
        failing_suite["cases"][0]["expected"]["reason_contains"] = ["missing required fields"]

        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = Path(tmp) / "bad-prompt-regression-fixtures.json"
            fixture_path.write_text(json.dumps(failing_suite), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--fixture",
                    str(fixture_path),
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["failure_count"], 1)
        self.assertIn("expected actual status", payload["results"][0]["failures"][0])

    def test_fixture_shape_errors_are_reported(self):
        invalid_suite = {
            "schema_version": 1,
            "suite": {
                "name": "prompt-regression-fixtures",
                "purpose": "invalid shape test",
                "source_backlog": "AGW-047",
            },
            "cases": [
                {
                    "id": "bad-id",
                    "title": "Invalid id",
                    "intent": "valid-persona-finding",
                    "payload_type": "persona",
                    "persona_id": "test-behavior-risk",
                    "payload": {
                        "schema_version": 1,
                        "findings": [],
                    },
                    "expected": {
                        "status": "pass",
                        "reason_contains": [],
                    },
                    "rationale": "Shape should fail before evaluation.",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = Path(tmp) / "invalid-prompt-regression-fixtures.json"
            fixture_path.write_text(json.dumps(invalid_suite), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--fixture",
                    str(fixture_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("case id must use PRF-000 format", result.stderr)


if __name__ == "__main__":
    unittest.main()
