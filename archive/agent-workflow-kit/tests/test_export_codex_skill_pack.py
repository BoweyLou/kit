import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / "scripts" / "export_codex_skill_pack.py"


def run(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def write_fixture(root: Path, unsafe_name: str | None = None) -> None:
    source = root / "workflows" / "prompts"
    (source / "templates").mkdir(parents=True)
    (source / "task-packet.md").write_text("# Task Packet\n\nScope work.\n", encoding="utf-8")
    (source / "review.md").write_text("# Review\n\nFind risks.\n", encoding="utf-8")
    (source / "templates" / "task.md").write_text("# Task Template\n", encoding="utf-8")
    (root / "VERSION").write_text("1.2.3\n", encoding="utf-8")
    (root / "workflows" / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "fixture-workflow-kit",
                "source_root": "workflows/prompts",
                "generated_adapters": [],
                "codex_skill_pack": {
                    "id": "fixture-skills",
                    "name": "Fixture Skills",
                    "description": "Fixture pack.",
                    "default_output": "dist/codex-skill-pack",
                    "skills": [
                        {
                            "id": "task",
                            "name": unsafe_name or "fixture-task",
                            "display_name": "Fixture Task",
                            "description": "Use when turning work into a task packet.",
                            "entrypoint": "task-packet.md",
                            "include": ["task-packet.md", "templates/*.md"],
                        },
                        {
                            "id": "review",
                            "name": "fixture-review",
                            "display_name": "Fixture Review",
                            "description": "Use when reviewing a repository.",
                            "entrypoint": "review.md",
                            "include": ["review.md"],
                        },
                    ],
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


class ExportCodexSkillPackTests(unittest.TestCase):
    def test_export_creates_skill_pack_and_check_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture(repo)

            result = run([sys.executable, str(EXPORTER), "--root", str(repo)])
            self.assertEqual(result.returncode, 0, result.stderr)

            output = repo / "dist" / "codex-skill-pack"
            skill = output / "fixture-task"
            skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: fixture-task", skill_text)
            self.assertIn("agent-workflow-kit version 1.2.3", skill_text)
            self.assertEqual(
                (skill / "references" / "task-packet.md").read_text(encoding="utf-8"),
                "# Task Packet\n\nScope work.\n",
            )
            self.assertTrue((skill / "references" / "templates" / "task.md").exists())

            manifest = json.loads((output / "pack-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["version"], "1.2.3")
            self.assertEqual(manifest["pack"]["id"], "fixture-skills")
            self.assertIn("fixture-task/SKILL.md", manifest["generated_files"])
            task_record = next(item for item in manifest["skills"] if item["id"] == "task")
            self.assertEqual(task_record["source_entrypoint"], "workflows/prompts/task-packet.md")
            self.assertTrue(all("sha256" in item for item in task_record["files"]))

            check = run([sys.executable, str(EXPORTER), "--root", str(repo), "--check"])
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertIn("Codex skill pack is current", check.stdout)

    def test_check_fails_when_skill_pack_drifts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture(repo)
            run([sys.executable, str(EXPORTER), "--root", str(repo)])
            (repo / "dist" / "codex-skill-pack" / "fixture-task" / "SKILL.md").write_text("stale\n", encoding="utf-8")

            result = run([sys.executable, str(EXPORTER), "--root", str(repo), "--check"])

            self.assertEqual(result.returncode, 1)
            self.assertIn("outdated target file", result.stderr)

    def test_subset_export_prunes_previous_generated_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture(repo)
            run([sys.executable, str(EXPORTER), "--root", str(repo)])

            result = run([sys.executable, str(EXPORTER), "--root", str(repo), "--skill", "task"])

            self.assertEqual(result.returncode, 0, result.stderr)
            output = repo / "dist" / "codex-skill-pack"
            self.assertTrue((output / "fixture-task").exists())
            self.assertFalse((output / "fixture-review").exists())
            manifest = json.loads((output / "pack-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual([item["id"] for item in manifest["skills"]], ["task"])

    def test_list_and_unknown_skill_reporting(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture(repo)

            listed = run([sys.executable, str(EXPORTER), "--root", str(repo), "--list"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("task\tfixture-task\ttask-packet.md", listed.stdout)
            self.assertIn("review\tfixture-review\treview.md", listed.stdout)

            unknown = run([sys.executable, str(EXPORTER), "--root", str(repo), "--skill", "missing"])
            self.assertEqual(unknown.returncode, 2)
            self.assertIn("unknown skill(s): missing", unknown.stderr)

    def test_rejects_unsafe_skill_directory_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture(repo, unsafe_name="../outside")

            result = run([sys.executable, str(EXPORTER), "--root", str(repo)])

            self.assertEqual(result.returncode, 2)
            self.assertIn("name must be a single safe directory name", result.stderr)
            self.assertFalse((repo / "outside").exists())


if __name__ == "__main__":
    unittest.main()
