import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


def run(cmd, cwd, check=False):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


def init_repo(path: Path):
    run(["git", "init", "-q"], path, check=True)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    run(["git", "add", "README.md"], path, check=True)
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


def install_agentic(repo: Path):
    result = run([sys.executable, str(INSTALL), str(repo), "--preset", "agentic"], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    run(["git", "add", "."], repo, check=True)
    run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Install repo contract kit",
        ],
        repo,
        check=True,
    )


def latest_run(repo: Path):
    runs = sorted(path for path in (repo / ".agent-workflows" / "runs").iterdir() if path.is_dir())
    if not runs:
        raise AssertionError("No run directory found")
    return runs[-1]


class AgentReviewRunTests(unittest.TestCase):
    def test_manual_runner_creates_prompts_and_placeholder_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)

            result = run(["make", "agent-run-review", "MODE=drift"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Manual mode generated prompts only", result.stdout)
            run_dir = latest_run(repo)
            runner = json.loads((run_dir / "review-run" / "review-run.json").read_text(encoding="utf-8"))
            self.assertEqual(runner["agent"], "manual")
            self.assertEqual(runner["mode"], "drift")
            self.assertEqual(runner["status"], "pass-with-caveats")
            self.assertTrue((run_dir / "review-run" / "personas" / "doc-code-delta" / "prompt.md").exists())
            self.assertTrue((run_dir / "review-run" / "personas" / "ai-code-slop" / "findings.json").exists())
            synthesis = json.loads(
                (run_dir / "review-run" / "synthesis" / "review-synthesis.json").read_text(encoding="utf-8")
            )
            self.assertEqual(synthesis["disposition"]["overall_status"], "not-run")
            receipt = json.loads((run_dir / "review-run" / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["run"]["status"], "pass-with-caveats")
            verify = run(["make", "agent-receipt-verify"], repo)
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

            status = run(["git", "status", "--short"], repo)
            self.assertEqual(status.stdout.strip(), "")

    def test_amp_runner_uses_stream_json_and_writes_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)

            fake_amp = Path(tmp) / "fake_amp.py"
            fake_amp.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env python3
                    import json
                    import sys

                    prompt = sys.stdin.read()
                    if "schemas/review-synthesis.schema.json" in prompt:
                        payload = {
                            "schema_version": 1,
                            "run": {
                                "run_id": "fake-run",
                                "mode": "bootstrap",
                                "synthesized_at": "2026-01-01T00:00:00+00:00",
                                "source_artifacts": []
                            },
                            "summary": ["One synthesized finding."],
                            "findings": [],
                            "remediation_batches": [],
                            "needs_human_decision": [],
                            "not_recommended": [],
                            "disposition": {
                                "overall_status": "pass",
                                "summary": "ok",
                                "next_actions": []
                            }
                        }
                    else:
                        payload = {
                            "schema_version": 1,
                            "run_id": "fake-run",
                            "persona_id": "fake-persona",
                            "status": "complete",
                            "findings": [
                                {
                                    "id": "FINDING_001",
                                    "priority": "P2",
                                    "area": "docs",
                                    "title": "Example finding",
                                    "confidence": "medium",
                                    "evidence": ["README.md:1 example"],
                                    "recommendation": "Review the example.",
                                    "status": "open",
                                    "false_positive_notes": "none found"
                                }
                            ],
                            "notes": []
                        }
                    event = {
                        "type": "result",
                        "subtype": "success",
                        "duration_ms": 1,
                        "is_error": False,
                        "num_turns": 1,
                        "result": json.dumps(payload),
                        "session_id": "T-test"
                    }
                    print(json.dumps(event))
                    """
                ),
                encoding="utf-8",
            )
            os.chmod(fake_amp, 0o755)

            result = run(["make", "agent-run-review", "AGENT=amp", f"AMP={fake_amp}"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            run_dir = latest_run(repo)
            runner = json.loads((run_dir / "review-run" / "review-run.json").read_text(encoding="utf-8"))
            self.assertEqual(runner["agent"], "amp")
            self.assertEqual(runner["status"], "pass")
            self.assertFalse(runner["validation_errors"])
            self.assertGreaterEqual(len(runner["findings"]), 4)

            receipt = json.loads((run_dir / "review-run" / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["run"]["status"], "pass")
            self.assertEqual(receipt["tooling"]["agent_tool"], "amp")

            status = run(["git", "status", "--short"], repo)
            self.assertEqual(status.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
