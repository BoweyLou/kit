import json
import os
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_doc_impact as check


def base_config():
    return deepcopy(check.DEFAULT_CONFIG)


class CheckDocImpactTests(unittest.TestCase):
    def test_api_change_requires_matching_doc_path(self):
        config = base_config()

        missing_docs = check.evaluate(["api/users.py"], config)
        self.assertTrue(missing_docs.failed)
        self.assertEqual(missing_docs.missing_categories, {"api"})

        unrelated_docs = check.evaluate(["api/users.py", "docs/roadmap.md"], config)
        self.assertTrue(unrelated_docs.failed)
        self.assertEqual(unrelated_docs.missing_categories, {"api"})

        covered = check.evaluate(["api/users.py", "README.md"], config)
        self.assertFalse(covered.failed)
        self.assertEqual(covered.covered_categories, {"api"})

    def test_no_docs_declaration_waives_missing_docs(self):
        config = base_config()

        result = check.evaluate(["cli/main.py"], config, no_docs_declaration=True)

        self.assertFalse(result.failed)
        self.assertEqual(result.missing_categories, {"cli"})
        self.assertTrue(result.no_docs_declaration)

    def test_sarif_payload_reports_missing_docs_by_changed_file(self):
        config = base_config()
        result = check.evaluate(["cli/main.py"], config)

        payload = check.sarif_payload(result, config)

        self.assertEqual(payload["version"], "2.1.0")
        sarif_results = payload["runs"][0]["results"]
        self.assertEqual(len(sarif_results), 1)
        self.assertEqual(sarif_results[0]["ruleId"], "docs-contract-cli")
        self.assertEqual(
            sarif_results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
            "cli/main.py",
        )

    def test_custom_config_can_add_rules_and_expected_docs(self):
        config = check.deep_merge(
            base_config(),
            {
                "impact_rules": {
                    "public_behavior": ["src/"],
                },
                "category_doc_paths": {
                    "public_behavior": ["docs/behavior/"],
                },
            },
        )

        result = check.evaluate(["src/login.py", "docs/behavior/login.md"], config)

        self.assertFalse(result.failed)
        self.assertEqual(result.covered_categories, {"public_behavior"})

    def test_expected_doc_paths_count_as_docs(self):
        config = base_config()

        result = check.evaluate(["config/app.yaml", ".env.example"], config)

        self.assertFalse(result.failed)
        self.assertEqual(result.covered_categories, {"config"})

    def test_no_docs_marker_requires_reason(self):
        markers = base_config()["no_docs_needed_markers"]

        self.assertTrue(check.has_no_docs_marker("No docs needed: internal refactor", markers))
        self.assertFalse(check.has_no_docs_marker("No docs needed:", markers))
        self.assertFalse(check.has_no_docs_marker("No docs needed: <!-- required -->", markers))

    def test_no_docs_declaration_reads_environment(self):
        config = base_config()
        old_value = os.environ.get("DOC_CONTRACT_PR_BODY")
        try:
            os.environ["DOC_CONTRACT_PR_BODY"] = "No docs needed: tests only"
            self.assertTrue(check.has_no_docs_declaration(None, config))
        finally:
            if old_value is None:
                os.environ.pop("DOC_CONTRACT_PR_BODY", None)
            else:
                os.environ["DOC_CONTRACT_PR_BODY"] = old_value

    def test_load_config_merges_defaults_with_file_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "doc-contract.json"
            config_path.write_text(
                json.dumps(
                    {
                        "impact_rules": {
                            "architecture": ["architecture/"],
                        }
                    }
                ),
                encoding="utf-8",
            )

            config = check.load_config(config_path)

        self.assertIn("api", config["impact_rules"])
        self.assertEqual(config["impact_rules"]["architecture"], ["architecture/"])

    def test_get_changed_files_includes_branch_staged_and_unstaged_files(self):
        def fake_run(cmd):
            if cmd == ["git", "merge-base", "HEAD", "origin/main"]:
                return "base-sha"
            if cmd == ["git", "diff", "--name-only", "base-sha...HEAD"]:
                return "api/users.py\n"
            if cmd == ["git", "diff", "--name-only", "--cached"]:
                return "cli/main.py\n"
            if cmd == ["git", "diff", "--name-only"]:
                return "docs/cli/main.md\n"
            if cmd == ["git", "ls-files", "--others", "--exclude-standard"]:
                return "docs/new-guide.md\n"
            raise AssertionError(f"unexpected command: {cmd}")

        with patch.object(check, "run", side_effect=fake_run):
            files = check.get_changed_files()

        self.assertEqual(files, ["api/users.py", "cli/main.py", "docs/cli/main.md", "docs/new-guide.md"])


if __name__ == "__main__":
    unittest.main()
