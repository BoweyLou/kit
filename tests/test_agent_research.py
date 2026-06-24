import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


def run(cmd, cwd, check=False):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


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


def install_minimal(repo: Path):
    result = run([sys.executable, str(INSTALL), str(repo)], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def latest_research(repo: Path):
    candidates = sorted(
        path / "research"
        for path in (repo / ".agent-workflows" / "runs").iterdir()
        if (path / "research" / "research-run.json").exists()
    )
    if not candidates:
        raise AssertionError("No research run found")
    return candidates[-1]


class AgentResearchTests(unittest.TestCase):
    def test_research_plan_requires_installed_research_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_minimal(repo)

            result = run(["make", "agent-research-plan"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing prompt file", result.stderr or result.stdout)
            run_root = repo / ".agent-workflows" / "runs"
            self.assertFalse(any(run_root.glob("*/research/research-run.json")))

    def test_research_plan_rejects_unknown_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)

            result = run(["make", "agent-research-plan", "RESEARCH_SOURCES=unknown-source"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unknown research source", result.stderr or result.stdout)

    def test_research_targets_create_manual_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)

            plan = run(
                [
                    "make",
                    "agent-research-plan",
                    "RESEARCH_TITLE=Backlog discovery",
                    "RESEARCH_QUESTION=What should we research?",
                ],
                repo,
            )
            self.assertEqual(plan.returncode, 0, plan.stderr)
            self.assertIn("Research plan written", plan.stdout)

            source = run(["make", "agent-research-run", "RESEARCH_SOURCE=github"], repo)
            self.assertEqual(source.returncode, 0, source.stderr)
            self.assertIn("Source research prompt written", source.stdout)

            synthesis = run(["make", "agent-research-synthesize"], repo)
            self.assertEqual(synthesis.returncode, 0, synthesis.stderr)
            self.assertIn("Research synthesis prompt written", synthesis.stdout)

            handoff = run(["make", "agent-research-to-task-packet"], repo)
            self.assertEqual(handoff.returncode, 0, handoff.stderr)
            self.assertIn("Research handoff prompt written", handoff.stdout)

            research = latest_research(repo)
            brief = json.loads((research / "research-brief.template.json").read_text(encoding="utf-8"))
            self.assertEqual(brief["boundaries"]["trust_profile"], "browser-research")
            self.assertTrue(brief["approval"]["proposed_writes_only"])
            ledger = brief["novelty_ledger"]
            self.assertEqual(ledger["novelty_threshold"], 70)
            self.assertEqual(ledger["prior_question_fingerprints"], [])
            self.assertEqual(ledger["recent_topics"], [])
            self.assertEqual(ledger["carry_forward_leads"], [])
            github_source = next(item for item in brief["sources"] if item["source_type"] == "github")
            self.assertEqual(github_source["allowed_domains"], ["github.com"])
            self.assertFalse(github_source["allow_general_web"])
            self.assertIn("search_queries", github_source)
            self.assertIn("quality_floor", github_source)
            self.assertTrue((research / "sources" / "github" / "prompt.md").exists())
            report = json.loads((research / "sources" / "github" / "source-report.template.json").read_text(encoding="utf-8"))
            self.assertFalse(report["source"]["search_plan_followed"])
            self.assertTrue((research / "synthesis" / "research-synthesis.template.json").exists())
            synthesis_payload = json.loads(
                (research / "synthesis" / "research-synthesis.template.json").read_text(encoding="utf-8")
            )
            candidate = synthesis_payload["candidate_ideas"][0]
            score = candidate["candidate_score"]
            self.assertEqual(candidate["id"], "CANDIDATE-001")
            self.assertEqual(candidate["state"], "draft")
            for field in ["novelty", "evidence_strength", "fit", "effort", "risk"]:
                self.assertEqual(score[field], 0)
            self.assertEqual(score["recommendation_state"], "defer")
            self.assertEqual(score["rationale"], "Not scored yet.")
            self.assertTrue((research / "handoff" / "research-to-task-packet.prompt.md").exists())


if __name__ == "__main__":
    unittest.main()
