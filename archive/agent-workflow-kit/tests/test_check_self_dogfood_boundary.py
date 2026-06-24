import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_self_dogfood_boundary as boundary


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class SelfDogfoodBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.build_repo()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel_path: str, text: str):
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def build_repo(self):
        prompt = "# Prompt Index\n"
        self.write("workflows/prompts/README.md", prompt)
        self.write(".codex/prompts/README.md", prompt)
        self.write(
            "workflows/manifest.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "name": "agent-workflow-kit",
                    "source_root": "workflows/prompts",
                    "generated_adapters": [
                        {
                            "id": "codex",
                            "target_root": ".codex/prompts",
                            "strategy": "mirror",
                        }
                    ],
                }
            ),
        )
        self.write(
            "Makefile",
            "validate:\n\t@echo ok\n\n"
            "self-check:\n\t@python3 scripts/check_self_dogfood_boundary.py\n\n"
            "agent-verify: self-check validate\n\t@echo ok\n\n"
            "kit-update:\n\t@echo explicit only\n",
        )
        self.write(".githooks/pre-commit", "python3 scripts/check_self_dogfood_boundary.py\n")
        self.write(".pre-commit-config.yaml", "repos: []\n")
        self.write(
            "AGENTS.md",
            (
                "Use repo-contract-kit/workflows/ for new workflow source. "
                "Treat workflows/prompts/ as legacy archive material and run "
                "prompt-adapters-export for archive edits. kit-update is explicit.\n"
            ),
        )
        self.write(
            ".agent-workflows/README.md",
            (
                "Use repo-contract-kit/workflows/ for new source. "
                "This legacy source repo keeps workflows/prompts/ and .codex/prompts/ "
                "as archive mirrors while using repo-contract-kit guardrails.\n"
            ),
        )
        self.write(
            "docs/adr/0002-self-dogfood-boundary.md",
            (
                "repo-contract-kit/workflows/ is live source. workflows/prompts/ is "
                "legacy archive material. repo-contract-kit guardrails are explicit; "
                "kit-update is manual.\n"
            ),
        )
        for rel_path in boundary.INTENTIONAL_LOCALIZED_MANAGED_FILES:
            if not (self.root / rel_path).exists():
                self.write(rel_path, "localized\n")

        files = []
        for rel_path in sorted(boundary.INTENTIONAL_LOCALIZED_MANAGED_FILES):
            files.append(
                {
                    "path": rel_path,
                    "managed": True,
                    "owner": "kit",
                    "installed_sha256": sha256_text("kit-template\n"),
                }
            )
        files.append(
            {
                "path": ".agent-workflows/agent-permission-policy.json",
                "managed": True,
                "owner": "kit",
                "installed_sha256": sha256_text("clean\n"),
            }
        )
        self.write(".agent-workflows/agent-permission-policy.json", "clean\n")
        files.append(
            {
                "path": ".codex/prompts/README.md",
                "managed": False,
                "owner": "target",
                "installed_sha256": sha256_text(prompt),
            }
        )
        self.write(".doc-contract-kit/manifest.json", json.dumps({"files": files}))

    def failures(self):
        return [result for result in boundary.run_checks(self.root) if not result.ok]

    def test_valid_self_dogfood_boundary_passes(self):
        self.assertEqual(self.failures(), [])

    def test_receipt_validator_override_is_intentional(self):
        self.assertIn("scripts/verify_agent_receipt.py", boundary.INTENTIONAL_LOCALIZED_MANAGED_FILES)

    def test_operator_workflow_runbook_override_is_intentional(self):
        self.assertIn("docs/ops/agent-workflow.md", boundary.INTENTIONAL_LOCALIZED_MANAGED_FILES)

    def test_adapter_drift_fails(self):
        self.write(".codex/prompts/README.md", "# Drifted\n")
        failures = self.failures()
        self.assertTrue(any(result.check_id == "codex-adapter-sync" for result in failures))

    def test_unexpected_managed_override_fails(self):
        self.write(".agent-workflows/agent-permission-policy.json", "customized unexpectedly\n")
        failures = self.failures()
        self.assertTrue(any(result.check_id == "managed-local-overrides" for result in failures))

    def test_automatic_kit_update_fails(self):
        self.write(
            "Makefile",
            "validate:\n\t@$(MAKE) kit-update\n\n"
            "self-check:\n\t@python3 scripts/check_self_dogfood_boundary.py\n\n"
            "agent-verify: self-check validate\n\t@echo ok\n",
        )
        failures = self.failures()
        self.assertTrue(any(result.check_id == "kit-update-not-automatic" for result in failures))


if __name__ == "__main__":
    unittest.main()
