import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_agent_receipt import validate_receipt  # noqa: E402


def learning_receipt():
    return {
        "schema_version": 1,
        "run": {
            "id": "learning-123",
            "started_at": "2026-06-15T00:00:00+00:00",
            "completed_at": "2026-06-15T00:05:00+00:00",
            "mode": "learning-comments",
            "status": "pass",
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
            "behavior_change": False,
            "changed_files": ["src/example.py"],
            "allowed_files": ["src/example.py"],
            "protected_files": [],
        },
        "evidence": {
            "files_inspected": ["src/example.py", "docs/adr/0001-example.md"],
            "commands": [
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
            ],
            "docs_impact": {
                "checked": True,
                "result": "pass",
                "categories": ["comments"],
                "waiver_reason": None,
            },
            "tests": {
                "result": "green-only",
                "failing_test_evidence": None,
                "passing_test_evidence": "Comment-only receipt validation passed.",
                "generated_test_provenance": None,
                "skip_reason": "Learning-comments run changed comments only; red/green behavior tests were not applicable.",
            },
            "comment_only_verification": {
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
            },
        },
        "findings": [],
        "disposition": {
            "summary": "Learning-comments run changed only explanatory comments.",
            "next_actions": [],
            "human_approval_required": False,
        },
    }


class VerifyAgentReceiptTests(unittest.TestCase):
    def assert_valid(self, receipt):
        self.assertEqual(validate_receipt(receipt, strict=True), [])

    def assert_error_contains(self, receipt, expected):
        errors = validate_receipt(receipt, strict=True)
        self.assertTrue(
            any(expected in error for error in errors),
            f"Expected error containing {expected!r}, got {errors}",
        )

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

    def test_optional_harness_metrics_accept_review_outcome_and_effort(self):
        receipt = learning_receipt()
        receipt["harness_metrics"] = {
            "context_file_count": 2,
            "commands_run_count": 2,
            "changed_file_count": 1,
            "review_outcome": {
                "findings_total": 4,
                "findings_open": 0,
                "findings_accepted": 2,
                "findings_rejected": 1,
                "findings_fixed": 1,
                "findings_deferred": 0,
                "findings_duplicate": 1,
                "findings_false_positive": 1,
                "false_positive_rate": 0.25,
                "duplicate_rate": 0.25,
                "review_yield_count": 3,
                "review_yield_rate": 0.75,
                "human_decision_count": 4,
                "notes": "Rates use emitted findings as the denominator.",
            },
            "effort": {
                "duration_ms": 120000,
                "first_finding_latency_ms": 15000,
                "time_to_green_ms": 90000,
                "commands_run_count": 2,
                "model_input_tokens": 1000,
                "model_output_tokens": 400,
                "estimated_cost_usd": 0.05,
                "human_review_minutes": 8.5,
                "human_interruption_count": 1,
                "notes": "Cost is provider-reported.",
            },
        }

        self.assert_valid(receipt)

    def test_optional_harness_metrics_reject_malformed_values(self):
        receipt = learning_receipt()
        receipt["harness_metrics"] = {
            "context_file_count": True,
            "review_outcome": {
                "findings_total": -1,
                "false_positive_rate": 1.5,
            },
            "effort": {
                "duration_ms": 1.5,
                "estimated_cost_usd": -0.01,
            },
        }

        errors = validate_receipt(receipt, strict=True)
        expected = [
            "harness_metrics.context_file_count must be a non-negative integer",
            "harness_metrics.review_outcome.findings_total must be a non-negative integer",
            "harness_metrics.review_outcome.false_positive_rate must be a number from 0 to 1",
            "harness_metrics.effort.duration_ms must be a non-negative integer",
            "harness_metrics.effort.estimated_cost_usd must be a non-negative number",
        ]
        for message in expected:
            self.assertTrue(any(message in error for error in errors), f"Expected {message!r}, got {errors}")

    def test_optional_harness_metrics_reject_non_object_groups(self):
        receipt = learning_receipt()
        receipt["harness_metrics"] = {
            "review_outcome": [],
            "effort": "unknown",
        }

        errors = validate_receipt(receipt, strict=True)
        self.assertTrue(any("harness_metrics.review_outcome must be an object" in error for error in errors), errors)
        self.assertTrue(any("harness_metrics.effort must be an object" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
