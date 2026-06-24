import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_docs_impact_benchmarks.py"
FIXTURE = ROOT / "research" / "docs-impact-benchmarks" / "docs-impact-benchmarks.json"
sys.path.insert(0, str(ROOT / "scripts"))

import run_docs_impact_benchmarks as benchmarks  # noqa: E402


class DocsImpactBenchmarkTests(unittest.TestCase):
    def test_fixture_shape_records_required_intents_and_expectations(self):
        suite = benchmarks.load_suite(FIXTURE)
        cases = suite["cases"]
        intents = {case["intent"] for case in cases}

        self.assertIn("true-positive", intents)
        self.assertIn("false-positive-guard", intents)
        self.assertIn("false-negative-guard", intents)
        self.assertIn("no-docs-needed-waiver", intents)

        for case in cases:
            with self.subTest(case_id=case["id"]):
                self.assertTrue(case["changed_files"])
                self.assertIn(case["expected"]["status"], {"pass", "fail"})
                self.assertIn("categories", case["expected"])
                self.assertIn("missing_categories", case["expected"])
                self.assertIn("no_docs_declaration", case["expected"])

    def test_canonical_fixture_suite_passes(self):
        report = benchmarks.run_suite(FIXTURE, ROOT / "doc-contract.json")

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["failure_count"], 0)
        self.assertEqual(report["case_count"], len(report["results"]))

    def test_fixture_covers_source_task_packet_summary_handoff(self):
        suite = benchmarks.load_suite(FIXTURE)
        cases = {case["id"]: case for case in suite["cases"]}

        for case_id in ["DIB-006", "DIB-007", "DIB-008"]:
            self.assertIn(case_id, cases)
            self.assertTrue(
                any(
                    path.startswith("research/agentic-workflow-review/task-packets/")
                    for path in cases[case_id]["changed_files"]
                )
            )

        self.assertEqual(cases["DIB-006"]["expected"]["status"], "fail")
        self.assertEqual(cases["DIB-006"]["expected"]["missing_categories"], ["research"])
        self.assertIn("research/agentic-workflow-review/summary.md", cases["DIB-007"]["changed_files"])
        self.assertEqual(cases["DIB-007"]["expected"]["covered_categories"], ["research"])
        self.assertTrue(cases["DIB-008"].get("no_docs_needed"))
        self.assertTrue(cases["DIB-008"]["expected"]["no_docs_declaration"])

    def test_runner_exits_nonzero_when_expected_output_is_wrong(self):
        suite = benchmarks.load_suite(FIXTURE)
        failing_suite = {
            "schema_version": suite["schema_version"],
            "suite": suite["suite"],
            "cases": [json.loads(json.dumps(suite["cases"][0]))],
        }
        failing_suite["cases"][0]["expected"]["status"] = "pass"

        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = Path(tmp) / "bad-docs-impact-benchmark.json"
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
        self.assertIn("expected status", payload["results"][0]["failures"][0])

    def test_fixture_shape_errors_are_reported(self):
        invalid_suite = {
            "schema_version": 1,
            "suite": {
                "name": "docs-impact-benchmarks",
                "purpose": "invalid shape test",
                "source_backlog": "AGW-046",
            },
            "cases": [
                {
                    "id": "bad-id",
                    "title": "Invalid id",
                    "intent": "true-positive",
                    "changed_files": ["scripts/example.py"],
                    "expected": {
                        "status": "fail",
                        "categories": ["tooling"],
                        "missing_categories": ["tooling"],
                        "no_docs_declaration": False,
                    },
                    "rationale": "Shape should fail before evaluation.",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = Path(tmp) / "invalid-docs-impact-benchmark.json"
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
        self.assertIn("case id must use DIB-000 format", result.stderr)


if __name__ == "__main__":
    unittest.main()
