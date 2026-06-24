import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify_agent_receipt.py"
sys.path.insert(0, str(ROOT / "scripts"))

from verify_agent_receipt import validate_receipt  # noqa: E402


def valid_receipt():
    return {
        "schema_version": 1,
        "run": {
            "id": "run-test",
            "started_at": "2026-01-01T00:00:00+00:00",
            "completed_at": "2026-01-01T00:01:00+00:00",
            "mode": "verification",
            "status": "pass",
        },
        "tooling": {
            "agent_tool": "manual",
            "agent_tool_version": None,
            "local_only": True,
            "network_used": False,
            "notes": "",
        },
        "scope": {
            "repo_root": ".",
            "base_ref": None,
            "behavior_change": False,
            "changed_files": ["README.md"],
            "allowed_files": [],
            "protected_files": [],
        },
        "harness_metrics": {
            "context_file_count": 1,
            "commands_run_count": 1,
            "changed_file_count": 1,
        },
        "evidence": {
            "files_inspected": ["README.md"],
            "commands": [
                {
                    "command": "python3 scripts/verify_agent_receipt.py --strict --receipt receipt.json",
                    "result": "pass",
                    "exit_code": 0,
                    "notes": "",
                }
            ],
            "docs_impact": {
                "checked": True,
                "result": "pass",
                "categories": [],
                "waiver_reason": None,
            },
            "tests": {
                "result": "not-applicable",
                "failing_test_evidence": None,
                "passing_test_evidence": None,
                "generated_test_provenance": None,
                "skip_reason": "Receipt-only validation; no behavior change under test.",
            },
        },
        "findings": [
            {
                "id": "FINDING_001",
                "priority": "P2",
                "area": "docs",
                "title": "Example finding",
                "confidence": "medium",
                "evidence": ["README.md:1 example"],
                "recommendation": "Review the example.",
                "status": "open",
                "false_positive_notes": "none found",
            }
        ],
        "disposition": {
            "summary": "Validated receipt evidence.",
            "next_actions": [],
            "human_approval_required": False,
        },
    }


def learning_receipt():
    payload = valid_receipt()
    payload["run"]["mode"] = "learning-comments"
    payload["scope"].update(
        {
            "behavior_change": False,
            "changed_files": ["src/example.py"],
            "allowed_files": ["src/example.py"],
        }
    )
    payload["evidence"]["files_inspected"] = ["src/example.py", "docs/adr/0001-example.md"]
    payload["evidence"]["commands"] = [
        {
            "command": "git diff -- src/example.py",
            "result": "pass",
            "exit_code": 0,
            "notes": "Only comment lines changed.",
        },
        {
            "command": "git diff --check",
            "result": "pass",
            "exit_code": 0,
            "notes": "",
        },
    ]
    payload["evidence"]["docs_impact"]["categories"] = ["comments"]
    payload["evidence"]["tests"] = {
        "result": "green-only",
        "failing_test_evidence": None,
        "passing_test_evidence": "Comment-only receipt validation passed.",
        "generated_test_provenance": None,
        "skip_reason": "Learning-comments run changed comments only; red/green behavior tests were not applicable.",
    }
    payload["evidence"]["comment_only_verification"] = {
        "checked": True,
        "result": "comment-only",
        "diff_scope": ["src/example.py"],
        "behavior_change_assertion": False,
        "changed_files_reviewed": ["src/example.py"],
        "comment_only_paths": ["src/example.py"],
        "explanation_note_paths": [],
        "non_comment_paths": [],
        "non_comment_path_explanations": [],
        "source_files_changed": True,
        "no_source_edit_reason": None,
        "evidence_commands": ["git diff -- src/example.py", "git diff --check"],
        "uncertainties": [],
    }
    payload["findings"] = []
    payload["disposition"] = {
        "summary": "Learning-comments run changed only explanatory comments.",
        "next_actions": [],
        "human_approval_required": False,
    }
    return payload


class VerifyAgentReceiptTests(unittest.TestCase):
    def assert_valid(self, receipt):
        self.assertEqual(validate_receipt(receipt, strict=True), [])

    def assert_error_contains(self, receipt, expected):
        errors = validate_receipt(receipt, strict=True)
        self.assertTrue(
            any(expected in error for error in errors),
            f"Expected error containing {expected!r}, got {errors}",
        )

    def test_strict_receipt_passes_with_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps(valid_receipt()), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(VERIFY), "--strict", "--receipt", str(receipt_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("validation passed", result.stdout)

    def test_strict_receipt_fails_without_required_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = valid_receipt()
            payload["evidence"]["commands"] = []
            payload["evidence"]["docs_impact"]["checked"] = False
            payload["evidence"]["tests"]["skip_reason"] = None
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps(payload), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(VERIFY), "--strict", "--receipt", str(receipt_path), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "fail")
            self.assertTrue(any("command" in error for error in output["errors"]))

    def test_strict_receipt_fails_behavior_change_without_red_green_or_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = valid_receipt()
            payload["scope"]["behavior_change"] = True
            payload["evidence"]["tests"]["result"] = "green-only"
            payload["evidence"]["tests"]["skip_reason"] = None
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps(payload), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(VERIFY), "--strict", "--receipt", str(receipt_path), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            output = json.loads(result.stdout)
            self.assertTrue(any("behavior-changing work" in error for error in output["errors"]))

    def test_strict_learning_comments_accepts_comment_only_proof(self):
        self.assert_valid(learning_receipt())

    def test_strict_learning_comments_requires_behavior_change_false(self):
        receipt = learning_receipt()
        receipt["scope"]["behavior_change"] = True

        self.assert_error_contains(receipt, "scope.behavior_change=false")

    def test_strict_learning_comments_requires_comment_only_verification(self):
        receipt = learning_receipt()
        del receipt["evidence"]["comment_only_verification"]

        self.assert_error_contains(receipt, "evidence.comment_only_verification")

    def test_strict_learning_comments_accepts_no_source_edit_explanation_note(self):
        receipt = learning_receipt()
        receipt["scope"]["changed_files"] = []
        receipt["scope"]["allowed_files"] = []
        verification = receipt["evidence"]["comment_only_verification"]
        verification.update(
            {
                "result": "explanation-note-only",
                "diff_scope": ["working tree"],
                "changed_files_reviewed": [],
                "comment_only_paths": [],
                "explanation_note_paths": [],
                "non_comment_paths": [],
                "source_files_changed": False,
                "no_source_edit_reason": "The explanation note was provided in the final response; no files changed.",
            }
        )

        self.assert_valid(receipt)

    def test_strict_learning_comments_requires_non_comment_path_explanations(self):
        receipt = learning_receipt()
        receipt["scope"]["changed_files"] = ["src/example.py", "notes/learning-note.md"]
        verification = receipt["evidence"]["comment_only_verification"]
        verification.update(
            {
                "result": "comment-and-explanation-note",
                "diff_scope": ["src/example.py", "notes/learning-note.md"],
                "changed_files_reviewed": ["src/example.py", "notes/learning-note.md"],
                "explanation_note_paths": ["notes/learning-note.md"],
                "non_comment_paths": ["notes/learning-note.md"],
                "non_comment_path_explanations": [],
            }
        )

        self.assert_error_contains(receipt, "non_comment_paths require behavior_safe explanations")

    def test_strict_learning_comments_accepts_explained_note_path(self):
        receipt = learning_receipt()
        receipt["scope"]["changed_files"] = ["src/example.py", "notes/learning-note.md"]
        verification = receipt["evidence"]["comment_only_verification"]
        verification.update(
            {
                "result": "comment-and-explanation-note",
                "diff_scope": ["src/example.py", "notes/learning-note.md"],
                "changed_files_reviewed": ["src/example.py", "notes/learning-note.md"],
                "explanation_note_paths": ["notes/learning-note.md"],
                "non_comment_paths": ["notes/learning-note.md"],
                "non_comment_path_explanations": [
                    {
                        "path": "notes/learning-note.md",
                        "reason": "Separate explanation note; no runtime source or behavior changed.",
                        "behavior_safe": True,
                    }
                ],
            }
        )

        self.assert_valid(receipt)

    def test_strict_learning_comments_rejects_uncertain_proof(self):
        receipt = learning_receipt()
        receipt["evidence"]["comment_only_verification"]["uncertainties"] = [
            "Could not inspect generated diff output."
        ]

        self.assert_error_contains(receipt, "uncertainties remain")

    def test_non_learning_receipts_do_not_need_comment_only_verification(self):
        receipt = copy.deepcopy(learning_receipt())
        receipt["run"]["mode"] = "pull-request"
        del receipt["evidence"]["comment_only_verification"]

        self.assert_valid(receipt)


if __name__ == "__main__":
    unittest.main()
