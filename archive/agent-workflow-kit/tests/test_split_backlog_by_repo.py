import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPLITTER = ROOT / "scripts" / "split_backlog_by_repo.py"
BACKLOG_DIR = ROOT / "research" / "agentic-workflow-review"


def run(cmd, cwd=ROOT):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class SplitBacklogByRepoTests(unittest.TestCase):
    def test_split_files_match_aggregate_backlog(self):
        aggregate = read_csv(BACKLOG_DIR / "backlog.csv")
        workflow = read_csv(BACKLOG_DIR / "agent-workflow-kit-backlog.csv")
        contract = read_csv(BACKLOG_DIR / "repo-contract-kit-backlog.csv")

        self.assertEqual(len(workflow), sum(1 for row in aggregate if row["repo"] == "agent-workflow-kit"))
        self.assertEqual(len(contract), sum(1 for row in aggregate if row["repo"] == "repo-contract-kit"))
        self.assertEqual(
            [row["id"] for row in workflow + contract],
            [row["id"] for row in aggregate if row["repo"] == "agent-workflow-kit"]
            + [row["id"] for row in aggregate if row["repo"] == "repo-contract-kit"],
        )

    def test_check_detects_stale_split_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            backlog_dir = repo / "research" / "agentic-workflow-review"
            scripts_dir = repo / "scripts"
            backlog_dir.mkdir(parents=True)
            scripts_dir.mkdir()
            (scripts_dir / "split_backlog_by_repo.py").write_text(SPLITTER.read_text(encoding="utf-8"), encoding="utf-8")
            (backlog_dir / "backlog.csv").write_text(
                "id,priority,repo,theme,item,why,source_examples,delivery_shape,status,completion_note\n"
                "AGW-900,P1,agent-workflow-kit,packaging,Workflow item,Why,Source,Shape,open,\n"
                "AGW-901,P1,repo-contract-kit,bootstrap,Install item,Why,Source,Shape,open,\n",
                encoding="utf-8",
            )
            (backlog_dir / "agent-workflow-kit-backlog.csv").write_text("stale\n", encoding="utf-8")
            (backlog_dir / "repo-contract-kit-backlog.csv").write_text("stale\n", encoding="utf-8")

            result = run([sys.executable, str(scripts_dir / "split_backlog_by_repo.py"), "--check"], cwd=repo)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Split backlog files are out of date", result.stderr)


if __name__ == "__main__":
    unittest.main()
