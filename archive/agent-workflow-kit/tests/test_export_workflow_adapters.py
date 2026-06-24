import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / "scripts" / "export_workflow_adapters.py"


def run(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def write_fixture(root: Path) -> None:
    source = root / "workflows" / "prompts"
    source.mkdir(parents=True)
    (source / "README.md").write_text("# Prompt Index\n", encoding="utf-8")
    (source / "personas").mkdir()
    (source / "personas" / "manifest.json").write_text('{"personas": []}\n', encoding="utf-8")
    (root / "workflows" / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_root": "workflows/prompts",
                "generated_adapters": [
                    {
                        "id": "codex",
                        "target_root": ".codex/prompts",
                        "strategy": "mirror",
                    },
                    {
                        "id": "copilot",
                        "target_path": ".github/copilot-instructions.md",
                        "strategy": "copilot-instructions",
                    }
                ],
                "planned_adapters": [
                    {
                        "id": "claude",
                        "targets": ["CLAUDE.md", ".claude/commands/"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class ExportWorkflowAdaptersTests(unittest.TestCase):
    def test_export_creates_codex_mirror_and_check_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture(repo)

            export_result = run([sys.executable, str(EXPORTER), "--root", str(repo)])
            self.assertEqual(export_result.returncode, 0, export_result.stderr)
            self.assertEqual((repo / ".codex" / "prompts" / "README.md").read_text(encoding="utf-8"), "# Prompt Index\n")
            self.assertTrue((repo / ".codex" / "prompts" / "personas" / "manifest.json").exists())
            copilot = repo / ".github" / "copilot-instructions.md"
            self.assertIn("Generated from `workflows/manifest.json`", copilot.read_text(encoding="utf-8"))

            check_result = run([sys.executable, str(EXPORTER), "--root", str(repo), "--check"])
            self.assertEqual(check_result.returncode, 0, check_result.stderr)

    def test_check_fails_when_codex_projection_drifts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture(repo)
            run([sys.executable, str(EXPORTER), "--root", str(repo)])
            (repo / ".codex" / "prompts" / "README.md").write_text("# Stale\n", encoding="utf-8")

            result = run([sys.executable, str(EXPORTER), "--root", str(repo), "--check"])
            self.assertEqual(result.returncode, 1)
            self.assertIn("outdated target file", result.stderr)

    def test_list_reports_generated_and_planned_adapters(self):
        result = run([sys.executable, str(EXPORTER), "--list"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("codex\tgenerated\t.codex/prompts", result.stdout)
        self.assertIn("copilot\tgenerated\t.github/copilot-instructions.md", result.stdout)
        self.assertIn("claude\tplanned\tCLAUDE.md, .claude/commands/", result.stdout)
        self.assertNotIn("copilot\tplanned", result.stdout)


if __name__ == "__main__":
    unittest.main()
