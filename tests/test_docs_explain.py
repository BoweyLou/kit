import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "docs_explain.py"


def init_git_repo(path: Path):
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(
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
        cwd=path,
        check=True,
    )


def write_sample_docs(repo: Path):
    (repo / "README.md").write_text(
        "# Sample Repo\n\n"
        "## Documentation Policy\n\n"
        "Run docs-impact before deciding whether docs changed. Agents must not approve "
        "`/waive-docs`; a human reviewer needs a specific `No docs needed:` reason.\n\n"
        "## Docs Patch Flow\n\n"
        "When docs coverage is missing, use docs-propose or `/add-docs --mode propose` "
        "to create a reviewable proposal before write-capable work starts.\n",
        encoding="utf-8",
    )
    docs = repo / "docs" / "ops"
    docs.mkdir(parents=True)
    (docs / "agent-workflow.md").write_text(
        "# Agent Workflow\n\n"
        "## Docs Proposal\n\n"
        "`make agent-docs-propose` writes sidecar proposal artifacts and does not modify "
        "the target checkout. Apply any docs patch only after review.\n",
        encoding="utf-8",
    )


class DocsExplainTests(unittest.TestCase):
    def test_json_matches_policy_with_citations_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            write_sample_docs(target)
            init_git_repo(target)
            before_files = sorted(path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file())

            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(target),
                    "--question",
                    "Can an agent waive docs work?",
                    "--focus",
                    "waiver",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "docs-explain")
            self.assertEqual(payload["result"], "matched")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse(payload["network"]["used"])
            self.assertFalse(payload["network"]["hosted_model_used"])
            self.assertTrue(payload["citations"])
            self.assertEqual(payload["citations"][0]["path"], "README.md")
            self.assertEqual(payload["citations"][0]["heading"], "Documentation Policy")
            self.assertIn("/waive-docs", payload["citations"][0]["snippet"])
            self.assertIn("Do not waive documentation work", payload["local_prompt"]["text"])
            self.assertIn("make agent-docs-propose", payload["next_commands"]["proposal"])
            after_files = sorted(path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file())
            self.assertEqual(after_files, before_files)
            status = subprocess.run(["git", "status", "--porcelain"], cwd=target, capture_output=True, text=True)
            self.assertEqual(status.stdout, "")

    def test_path_filter_limits_scanned_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            write_sample_docs(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(target),
                    "--question",
                    "How do I request a docs patch?",
                    "--focus",
                    "docs-propose",
                    "--path",
                    "docs/ops/",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["scanned_paths"], ["docs/ops/agent-workflow.md"])
            self.assertEqual(payload["path_filters"], ["docs/ops"])
            self.assertEqual(payload["citations"][0]["path"], "docs/ops/agent-workflow.md")
            self.assertIn("agent-docs-propose", payload["citations"][0]["snippet"])

    def test_default_scan_omits_agent_workflow_schema_noise(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            write_sample_docs(target)
            schema_dir = target / ".agent-workflows" / "schemas"
            schema_dir.mkdir(parents=True)
            (schema_dir / "session-receipt.schema.json").write_text(
                '{"properties":{"waiver_reason":{"type":["string","null"]}}}\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(target),
                    "--question",
                    "Can an agent waive docs work?",
                    "--focus",
                    "waiver",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertNotIn(".agent-workflows/schemas/session-receipt.schema.json", payload["scanned_paths"])
            self.assertFalse(
                any(citation["path"] == ".agent-workflows/schemas/session-receipt.schema.json" for citation in payload["citations"])
            )

    def test_check_mode_fails_when_no_matching_docs_are_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            write_sample_docs(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(target),
                    "--question",
                    "Where is the quantum lunchbox plutonium?",
                    "--path",
                    "README.md",
                    "--check",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "no-matching-docs")
            self.assertEqual(payload["citations"], [])
            self.assertTrue(payload["uncertainty"])
            self.assertIn("No matching excerpts were found", payload["local_prompt"]["text"])

    def test_snippet_prefers_specific_policy_line_over_generic_agent_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "README.md").write_text(
                "# Sample Repo\n\n"
                "## Docs Governance\n\n"
                "Agents can inspect repository documentation and local docs commands.\n"
                "The local docs workflow records changed files and source paths.\n"
                "Only a human reviewer can approve `/waive-docs` with a specific reason.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(target),
                    "--question",
                    "Can an agent waive docs work?",
                    "--focus",
                    "waiver",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "matched")
            self.assertIn("/waive-docs", payload["citations"][0]["snippet"])

    def test_text_output_includes_citations_prompt_and_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            write_sample_docs(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--repo",
                    str(target),
                    "--question",
                    "What is docs-propose for?",
                    "--focus",
                    "docs-propose",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Docs explainer: matched", result.stdout)
            self.assertIn("Target writes performed: false", result.stdout)
            self.assertIn("Network/model calls: false", result.stdout)
            self.assertIn("Matched source evidence:", result.stdout)
            self.assertIn("Local prompt:", result.stdout)
            self.assertIn("Write follow-up requires explicit scope/review:", result.stdout)


if __name__ == "__main__":
    unittest.main()
