import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Version1ConsolidationTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_v1_identity_doc_declares_single_repo_surface(self):
        doc = self.read("docs/version-1-consolidation.md")

        self.assertIn("https://github.com/BoweyLou/kit.git", doc)
        self.assertIn("https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh", doc)
        self.assertIn("public CLI: `kit`", doc)
        self.assertIn("The `kit` repository owns the installer", doc)
        self.assertIn("`kit/workflows/`", doc)
        self.assertIn("old `agent-workflow-kit` / `Codex_CodeReview` checkout is legacy", doc)
        self.assertIn("Rollback path:", doc)

    def test_docs_route_operators_to_v1_contract(self):
        for relative in ("README.md", "docs/agent-workflow-stack.md", "docs/rollout-guide.md"):
            with self.subTest(relative=relative):
                self.assertIn("docs/version-1-consolidation.md", self.read(relative))

    def test_single_installer_and_optional_legacy_workflow_path(self):
        install = self.read("install.sh")

        self.assertIn("REPO_CONTRACT_KIT_REPO_URL:-https://github.com/BoweyLou/kit.git", install)
        self.assertIn('COMMAND_NAME="${KIT_COMMAND:-${REPO_CONTRACT_KIT_COMMAND:-kit}}"', install)
        self.assertIn("INSTALL_WORKFLOW=0", install)
        self.assertIn("--with-workflow", install)
        self.assertIn("--no-workflow", install)

    def test_workflow_source_and_single_release_stream_exist_in_this_repo(self):
        self.assertTrue((ROOT / "workflows" / "prompts" / "task-packet.md").exists())
        self.assertTrue((ROOT / "workflows" / "schemas" / "task-packet.schema.json").exists())
        self.assertTrue((ROOT / "install.sh").exists())
        self.assertTrue((ROOT / "scripts" / "repo_contract_kit.py").exists())
        self.assertTrue((ROOT / "VERSION").exists())
        self.assertTrue((ROOT / "CHANGELOG.md").exists())

        version = self.read("VERSION").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
        self.assertIn(f"## {version} - ", self.read("CHANGELOG.md"))

    def test_task_packet_contract_rejects_vague_docs_release_requirements(self):
        prompt = self.read("workflows/prompts/task-packet.md")
        template = self.read("workflows/prompts/templates/task-packet.md")
        schema = json.loads(self.read("workflows/schemas/task-packet.schema.json"))

        self.assertIn("Do not leave vague", prompt)
        self.assertIn("requirements such as", prompt)
        self.assertIn("exact documentation and release metadata surfaces", prompt)
        self.assertIn("- Documentation surfaces:", template)
        self.assertIn("- Release metadata:", template)
        self.assertIn("- Verification commands:", template)

        docs_required = set(schema["properties"]["docs_impact"]["required"])
        for field in (
            "documentation_surfaces",
            "release_metadata",
            "generated_docs",
            "contract_references",
            "verification_commands",
        ):
            self.assertIn(field, docs_required)
