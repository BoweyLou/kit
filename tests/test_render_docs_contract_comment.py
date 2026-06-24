import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_docs_contract_comment.py"


class RenderDocsContractCommentTests(unittest.TestCase):
    def run_renderer(self, payload, *extra_args):
        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "docs-impact.json"
            payload_path.write_text(json.dumps(payload), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--doc-impact-json",
                    str(payload_path),
                    *extra_args,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_renders_missing_docs_comment_with_policy_links_and_actions(self):
        payload = {
            "status": "fail",
            "changed_files": ["cli/new_command.py"],
            "docs_changed": [],
            "categories": [
                {
                    "category": "cli",
                    "changed_files": ["cli/new_command.py"],
                    "suggested_doc_paths": ["README.md", "docs/cli/"],
                    "covered": False,
                }
            ],
            "missing_categories": ["cli"],
            "no_docs_declaration": False,
            "result": "missing-docs",
        }

        comment = self.run_renderer(
            payload,
            "--repo-url",
            "https://github.com/example/project",
            "--ref",
            "abc123",
            "--run-url",
            "https://github.com/example/project/actions/runs/1",
        )

        self.assertTrue(comment.startswith("<!-- repo-contract-kit:docs-contract-comment -->"))
        self.assertIn("Status: FAIL", comment)
        self.assertIn("| cli | missing | cli/new_command.py |", comment)
        self.assertIn("[README.md](https://github.com/example/project/blob/abc123/README.md)", comment)
        self.assertIn(
            "[Documentation contract](https://github.com/example/project/blob/abc123/docs/documentation-contract.md)",
            comment,
        )
        self.assertIn("- Update one of the suggested docs for each missing category.", comment)
        self.assertIn("Workflow run: https://github.com/example/project/actions/runs/1", comment)

    def test_renders_no_impact_comment_deterministically(self):
        payload = {
            "status": "pass",
            "changed_files": ["tests/test_example.py"],
            "docs_changed": [],
            "categories": [],
            "missing_categories": [],
            "no_docs_declaration": False,
            "result": "covered-or-no-impact",
        }

        first = self.run_renderer(payload)
        second = self.run_renderer(payload)

        self.assertEqual(first, second)
        self.assertIn("Status: PASS", first)
        self.assertIn("No doc-impacting categories were detected.", first)
        self.assertIn("No docs-contract action is needed", first)

    def test_supports_direct_inputs_without_checker_json(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--status",
                "waived",
                "--changed-file",
                "cli/new_command.py",
                "--missing-category",
                "cli",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Status: WAIVED", result.stdout)
        self.assertIn("| No-docs declaration | yes |", result.stdout)
