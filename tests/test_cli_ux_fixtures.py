import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "repo_contract_kit.py"
MANIFEST = ROOT / "tests" / "fixtures" / "cli_ux" / "manifest.json"


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    (path / "README.md").write_text("# Fixture Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit fixture",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Initial fixture repo",
        ],
        cwd=path,
        check=True,
    )


def install_kit_target(path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(CLI),
            "setup",
            "--repo",
            str(path),
            "--preset",
            "minimal",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def json_path(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


class CliUxFixtureTests(unittest.TestCase):
    def test_cli_ux_fixtures_pass(self):
        self.assertTrue(MANIFEST.exists(), f"Missing fixture manifest: {MANIFEST}")
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cases = manifest.get("cases") or []
        self.assertTrue(cases, "CLI UX fixture manifest must contain cases")

        for case in cases:
            with self.subTest(case=case["id"]):
                self.run_case(case)

    def run_case(self, case: dict[str, Any]) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cwd = ROOT
            args = list(case["args"])
            fixture = case.get("fixture")
            if fixture in {"git_repo", "installed_target"}:
                repo = tmp_path / "repo"
                repo.mkdir()
                init_git_repo(repo)
                if fixture == "installed_target":
                    install_kit_target(repo)
                cwd = repo
                args = [part.replace("{repo}", str(repo)) for part in args]
            elif fixture:
                self.fail(f"Unknown CLI UX fixture type: {fixture}")

            env = os.environ.copy()
            env.update(case.get("env") or {})
            result = subprocess.run(
                [sys.executable, str(CLI), *args],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, case["returncode"], result.stdout + result.stderr)
        for expected in case.get("stdout_contains", []):
            self.assertIn(expected, result.stdout)
        for unexpected in case.get("stdout_not_contains", []):
            self.assertNotIn(unexpected, result.stdout)
        for expected in case.get("stderr_contains", []):
            self.assertIn(expected, result.stderr)
        for unexpected in case.get("stderr_not_contains", []):
            self.assertNotIn(unexpected, result.stderr)
        for assertion in case.get("stdout_json_equals", []):
            payload = json.loads(result.stdout)
            self.assertEqual(json_path(payload, assertion["path"]), assertion["value"])


if __name__ == "__main__":
    unittest.main()
