import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKER = ROOT / "scripts" / "build_context_packet.py"


def run(cmd, cwd, check=False):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def init_repo(repo: Path):
    run(["git", "init", "-q"], repo, check=True)
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "docs" / "adr").mkdir(parents=True)
    (repo / "src" / "widget.py").write_text("def render_widget():\n    return 'old'\n", encoding="utf-8")
    (repo / "src" / "dashboard.py").write_text("from src.widget import render_widget\n", encoding="utf-8")
    (repo / "tests" / "test_widget.py").write_text("from src.widget import render_widget\n", encoding="utf-8")
    (repo / "docs" / "adr" / "0001-widget-rendering.md").write_text("# Widget Rendering\n", encoding="utf-8")
    (repo / "docs" / "widget.md").write_text("Widget rendering calls `render_widget`.\n", encoding="utf-8")
    run(["git", "add", "."], repo, check=True)
    run(
        [
            "git",
            "-c",
            "user.name=context-packet test",
            "-c",
            "user.email=context-packet@example.invalid",
            "commit",
            "-qm",
            "Initial repo",
        ],
        repo,
        check=True,
    )
    (repo / "src" / "widget.py").write_text("def render_widget():\n    return 'new'\n", encoding="utf-8")


class BuildContextPacketTests(unittest.TestCase):
    def test_context_packet_includes_callers_tests_docs_and_adrs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)

            result = run([sys.executable, str(PACKER), "--root", str(repo), "--json"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["schema_version"], 1)
            self.assertEqual(packet["changed_files"], ["src/widget.py"])
            self.assertIn("src/dashboard.py", [item["path"] for item in packet["likely_callers"]])
            self.assertIn("tests/test_widget.py", [item["path"] for item in packet["likely_tests"]])
            self.assertIn("docs/widget.md", [item["path"] for item in packet["related_docs"]])
            self.assertIn("docs/adr/0001-widget-rendering.md", [item["path"] for item in packet["adrs"]])


if __name__ == "__main__":
    unittest.main()
