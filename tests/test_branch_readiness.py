import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "repo_contract_kit.py"


def run(cmd, cwd, check=False, env=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=check,
    )


def init_repo(path: Path):
    run(["git", "init", "-q", "-b", "main"], path, check=True)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    (path / "doc-contract.json").write_text(
        json.dumps(
            {
                "required_files": [],
                "doc_paths": ["README.md", "docs/"],
                "impact_rules": {"cli": ["src/"]},
                "category_doc_paths": {"cli": ["docs/cli/"]},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (path / "VERSION").write_text("1.0.0\n", encoding="utf-8")
    (path / "CHANGELOG.md").write_text("# Changelog\n\n", encoding="utf-8")
    run(["git", "add", "."], path, check=True)
    run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Initial sample repo",
        ],
        path,
        check=True,
    )


def commit(path: Path, message: str):
    run(["git", "add", "."], path, check=True)
    run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            message,
        ],
        path,
        check=True,
    )


def checkout_feature(path: Path):
    run(["git", "switch", "-q", "-c", "feature/readiness"], path, check=True)


def write_success_checks(directory: Path):
    checks = directory / "checks.json"
    checks.write_text(
        json.dumps({"checks": [{"name": "unit", "required": True, "state": "success"}]}) + "\n",
        encoding="utf-8",
    )
    return checks


def branch_readiness(repo: Path, *extra, state_home: Path | None = None):
    env = {**os.environ}
    if state_home is not None:
        env["XDG_STATE_HOME"] = str(state_home)
    return run(
        [
            sys.executable,
            str(CLI),
            "branch-readiness",
            "--repo",
            str(repo),
            "--base-ref",
            "main",
            "--json",
            *extra,
        ],
        ROOT,
        env=env,
    )


class BranchReadinessTests(unittest.TestCase):
    def test_branch_readiness_ready_json_is_no_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            state_home = Path(tmp) / "state"
            init_repo(repo)
            checkout_feature(repo)
            (repo / "README.md").write_text("# Ready branch\n", encoding="utf-8")
            commit(repo, "Update docs")
            checks = write_success_checks(Path(tmp))

            result = branch_readiness(repo, "--checks-json", str(checks), state_home=state_home)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "branch-readiness")
            self.assertTrue(payload["ready"])
            self.assertEqual(payload["result"], "ready")
            self.assertFalse(payload["target_repo_writes"])
            self.assertFalse(payload["sidecar_writes"])
            self.assertFalse(payload["network_calls"])
            self.assertFalse(payload["no_write_proof"]["github_api_calls"])
            self.assertEqual(payload["evidence"]["checks"]["result"], "passed")
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_branch_readiness_blocks_dirty_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            checkout_feature(repo)
            (repo / "README.md").write_text("# Dirty branch\n", encoding="utf-8")

            result = branch_readiness(repo)

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ready"])
            self.assertIn("dirty_checkout", {item["code"] for item in payload["blockers"]})

    def test_branch_readiness_blocks_missing_docs_without_waiver_and_records_waiver(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            checkout_feature(repo)
            (repo / "src").mkdir()
            (repo / "src" / "tool.py").write_text("print('new cli')\n", encoding="utf-8")
            with (repo / "CHANGELOG.md").open("a", encoding="utf-8") as handle:
                handle.write("- Add CLI tool.\n")
            commit(repo, "Add CLI without docs")
            checks = write_success_checks(Path(tmp))

            blocked = branch_readiness(repo, "--checks-json", str(checks))
            self.assertNotEqual(blocked.returncode, 0, blocked.stdout + blocked.stderr)
            blocked_payload = json.loads(blocked.stdout)
            self.assertIn("missing_docs", {item["code"] for item in blocked_payload["blockers"]})

            waived = branch_readiness(
                repo,
                "--checks-json",
                str(checks),
                "--no-docs-needed",
                "internal-only generated CLI shim",
            )
            self.assertEqual(waived.returncode, 0, waived.stdout + waived.stderr)
            waived_payload = json.loads(waived.stdout)
            self.assertTrue(waived_payload["ready"])
            self.assertEqual(
                waived_payload["evidence"]["docs_impact"]["no_docs_needed"]["reason"],
                "internal-only generated CLI shim",
            )
            self.assertNotIn("missing_docs", {item["code"] for item in waived_payload["blockers"]})

    def test_branch_readiness_blocks_required_ci_and_warns_on_advisory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            checkout_feature(repo)
            (repo / "README.md").write_text("# CI branch\n", encoding="utf-8")
            commit(repo, "Update docs")
            checks = Path(tmp) / "checks.json"
            checks.write_text(
                json.dumps(
                    {
                        "checks": [
                            {"name": "unit", "required": True, "state": "pending"},
                            {"name": "lint", "advisory": True, "state": "failed"},
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = branch_readiness(repo, "--checks-json", str(checks))

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("required_check_not_passing", {item["code"] for item in payload["blockers"]})
            self.assertIn("advisory_check_not_passing", {item["code"] for item in payload["warnings"]})

    def test_branch_readiness_blocks_invalid_receipt_and_failing_review_disposition(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            checkout_feature(repo)
            (repo / "README.md").write_text("# Evidence branch\n", encoding="utf-8")
            commit(repo, "Update docs")
            checks = write_success_checks(Path(tmp))
            receipt = repo / "receipt.json"
            receipt.write_text('{"schema_version": 1, "run": {"status": "fail"}}\n', encoding="utf-8")
            review = repo / "review.json"
            review.write_text('{"status": "changes-requested"}\n', encoding="utf-8")

            result = branch_readiness(
                repo,
                "--checks-json",
                str(checks),
                "--receipt",
                str(receipt),
                "--review-disposition-json",
                str(review),
            )

            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("receipt_invalid", codes)
            self.assertIn("review_disposition_blocked", codes)


if __name__ == "__main__":
    unittest.main()
