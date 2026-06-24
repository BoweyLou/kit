import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StackStatusTests(unittest.TestCase):
    def test_stack_status_prints_source_and_snapshot_sections(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "stack_status.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Agent workflow stack status", result.stdout)
        self.assertIn("agent-workflow-kit source repo", result.stdout)
        self.assertIn("source-repo boundary check", result.stdout)
        self.assertIn("installed guardrail snapshot in this repo", result.stdout)
        self.assertIn("Set KIT=/path/to/repo-contract-kit", result.stdout)


if __name__ == "__main__":
    unittest.main()
