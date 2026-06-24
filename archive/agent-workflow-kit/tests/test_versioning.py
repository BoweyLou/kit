import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

import version
import check_versioning


class VersioningTests(unittest.TestCase):
    def test_semver_prerelease_is_valid(self):
        self.assertEqual(version.validate_version("0.2.0-beta.1"), (0, 2, 0))

    def test_workflow_source_requires_version_update(self):
        self.assertTrue(check_versioning.requires_version_update("workflows/prompts/task-packet.md"))

    def test_backlog_split_requires_version_update(self):
        self.assertTrue(
            check_versioning.requires_version_update(
                "research/agentic-workflow-review/agent-workflow-kit-backlog.csv"
            )
        )


if __name__ == "__main__":
    unittest.main()
