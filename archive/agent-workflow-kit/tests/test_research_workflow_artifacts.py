import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResearchWorkflowArtifactTests(unittest.TestCase):
    def test_research_prompts_exist_in_canonical_source(self):
        prompt_root = ROOT / "workflows" / "prompts" / "research"
        for name in [
            "README.md",
            "research-brief.md",
            "source-github.md",
            "source-arxiv.md",
            "source-hacker-news.md",
            "source-official-docs.md",
            "research-synthesis.md",
            "research-to-backlog.md",
        ]:
            with self.subTest(name=name):
                path = prompt_root / name
                self.assertTrue(path.exists(), f"missing {path}")
                self.assertIn("research", path.read_text(encoding="utf-8").lower())

    def test_research_schemas_are_valid_json_with_expected_boundaries(self):
        schemas = {
            "research-brief.schema.json": ["research", "sources", "novelty_ledger", "boundaries", "outputs", "approval"],
            "research-source-report.schema.json": ["run", "source", "sources_visited", "findings"],
            "research-synthesis.schema.json": ["run", "summary", "candidate_ideas", "proposals", "rejected_leads"],
        }
        for name, required in schemas.items():
            with self.subTest(name=name):
                payload = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
                self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(payload["type"], "object")
                self.assertEqual(payload["additionalProperties"], False)
                for field in required:
                    self.assertIn(field, payload["required"])

    def test_research_brief_schema_requires_bounded_source_plan(self):
        payload = json.loads((ROOT / "schemas" / "research-brief.schema.json").read_text(encoding="utf-8"))
        source_required = payload["properties"]["sources"]["items"]["required"]
        for field in [
            "purpose",
            "search_queries",
            "required_artifact_types",
            "min_results",
            "max_results",
            "quality_floor",
        ]:
            self.assertIn(field, source_required)

    def test_research_brief_schema_includes_novelty_ledger_contract(self):
        payload = json.loads((ROOT / "schemas" / "research-brief.schema.json").read_text(encoding="utf-8"))
        ledger_ref = payload["properties"]["novelty_ledger"]["$ref"]
        self.assertEqual(ledger_ref, "#/$defs/novelty_ledger")
        ledger = payload["$defs"]["novelty_ledger"]
        for field in [
            "prior_question_fingerprints",
            "recent_topics",
            "novelty_threshold",
            "carry_forward_leads",
        ]:
            self.assertIn(field, ledger["required"])
        self.assertEqual(ledger["properties"]["prior_question_fingerprints"]["maxItems"], 50)
        self.assertEqual(ledger["properties"]["recent_topics"]["maxItems"], 25)
        self.assertEqual(ledger["properties"]["novelty_threshold"]["minimum"], 0)
        self.assertEqual(ledger["properties"]["novelty_threshold"]["maximum"], 100)
        carry_forward = payload["$defs"]["carry_forward_lead"]
        self.assertIn("state", carry_forward["required"])
        self.assertIn("next_run_action", carry_forward["required"])
        self.assertEqual(carry_forward["properties"]["state"]["enum"], ["rejected", "deferred"])

    def test_research_synthesis_schema_includes_candidate_scoring_contract(self):
        payload = json.loads((ROOT / "schemas" / "research-synthesis.schema.json").read_text(encoding="utf-8"))
        candidate_score = payload["$defs"]["candidate_score"]
        for field in [
            "novelty",
            "evidence_strength",
            "fit",
            "effort",
            "risk",
            "recommendation_state",
            "rationale",
        ]:
            self.assertIn(field, candidate_score["required"])
        proposal_required = payload["$defs"]["proposal"]["required"]
        self.assertIn("candidate_score", proposal_required)
        candidate_idea = payload["$defs"]["candidate_idea"]
        self.assertIn("candidate_score", candidate_idea["required"])
        rejected_lead = payload["$defs"]["rejected_lead"]
        self.assertIn("state", rejected_lead["required"])
        self.assertIn("carry_forward", rejected_lead["required"])

    def test_research_prompts_block_random_search(self):
        brief = (ROOT / "workflows" / "prompts" / "research" / "research-brief.md").read_text(encoding="utf-8")
        github = (ROOT / "workflows" / "prompts" / "research" / "source-github.md").read_text(encoding="utf-8")
        self.assertIn("Do not let a source agent improvise broad web searches", brief)
        self.assertIn("seed URLs", brief)
        self.assertIn("If the brief has no GitHub seed URLs or queries", github)

    def test_research_prompts_require_novelty_gate_and_candidate_scoring(self):
        source_root = ROOT / "workflows" / "prompts" / "research"
        adapter_root = ROOT / ".codex" / "prompts" / "research"
        for root in [source_root, adapter_root]:
            with self.subTest(root=root):
                brief = (root / "research-brief.md").read_text(encoding="utf-8")
                synthesis = (root / "research-synthesis.md").read_text(encoding="utf-8")
                handoff = (root / "research-to-backlog.md").read_text(encoding="utf-8")
                self.assertIn("Novelty Planning Rule", brief)
                self.assertIn("prior-question fingerprints", brief)
                self.assertIn("novelty_threshold", synthesis)
                self.assertIn("Score several candidate ideas", synthesis)
                self.assertIn("carry_forward: true", synthesis)
                self.assertIn("candidate score must clear the novelty threshold", handoff)

    def test_agent_research_templates_include_novelty_and_candidate_scores(self):
        run_dir = None
        plan = subprocess.run(
            [
                sys.executable,
                "scripts/agent_research.py",
                "plan",
                "--research-id",
                "TEST-NOVELTY-LEDGER",
                "--title",
                "Novelty ledger template test",
                "--question",
                "Which new backlog ideas are novel enough?",
                "--sources",
                "github",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        try:
            marker = "Research plan written: "
            line = next(line for line in plan.stdout.splitlines() if line.startswith(marker))
            research_dir = ROOT / line.removeprefix(marker)
            run_dir = research_dir.parent
            brief = json.loads((research_dir / "research-brief.template.json").read_text(encoding="utf-8"))
            ledger = brief["novelty_ledger"]
            self.assertEqual(ledger["novelty_threshold"], 70)
            self.assertEqual(ledger["prior_question_fingerprints"], [])
            self.assertEqual(ledger["recent_topics"], [])
            self.assertEqual(ledger["carry_forward_leads"], [])

            subprocess.run(
                [sys.executable, "scripts/agent_research.py", "synthesize"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            synthesis = json.loads(
                (research_dir / "synthesis" / "research-synthesis.template.json").read_text(encoding="utf-8")
            )
            candidate = synthesis["candidate_ideas"][0]
            score = candidate["candidate_score"]
            self.assertEqual(candidate["id"], "CANDIDATE-001")
            for field in ["novelty", "evidence_strength", "fit", "effort", "risk"]:
                self.assertEqual(score[field], 0)
            self.assertEqual(score["recommendation_state"], "defer")
            self.assertEqual(score["rationale"], "Not scored yet.")
        finally:
            if run_dir and run_dir.is_dir() and run_dir.parent == ROOT / ".agent-workflows" / "runs":
                shutil.rmtree(run_dir)

    def test_research_prompt_adapter_projection_is_manifest_driven(self):
        manifest = json.loads((ROOT / "workflows" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_root"], "workflows/prompts")
        self.assertEqual(manifest["generated_adapters"][0]["target_root"], ".codex/prompts")


if __name__ == "__main__":
    unittest.main()
