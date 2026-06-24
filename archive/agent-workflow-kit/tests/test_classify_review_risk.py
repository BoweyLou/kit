import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLASSIFIER = ROOT / "scripts" / "classify_review_risk.py"
sys.path.insert(0, str(ROOT / "scripts"))

import agent_start  # noqa: E402
from classify_review_risk import classify_paths  # noqa: E402


def run_classifier(*paths: str):
    result = subprocess.run(
        [sys.executable, str(CLASSIFIER), *paths],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class ReviewRiskClassifierTests(unittest.TestCase):
    def test_auth_and_token_paths_are_high_risk_security_reviews(self):
        result = run_classifier("src/auth/session_tokens.py")

        self.assertEqual(result["risk_tier"], "high")
        self.assertEqual(result["trust_profile"], "read-only-review")
        self.assertIn("security-privacy", result["recommended_personas"])
        self.assertTrue(any(trigger["rule_id"] == "auth-or-secrets" for trigger in result["triggers"]))

    def test_destructive_paths_are_critical(self):
        result = run_classifier("scripts/purge_old_accounts.py")

        self.assertEqual(result["risk_tier"], "critical")
        self.assertEqual(result["trust_profile"], "untrusted-pr")
        self.assertIn("api-data-contracts", result["recommended_personas"])

    def test_docs_only_paths_keep_default_personas_with_medium_contract_trigger(self):
        result = run_classifier("AGENTS.md", "docs/adr/0003-policy.md")

        self.assertEqual(result["risk_tier"], "medium")
        self.assertIn("doc-code-delta", result["recommended_personas"])
        self.assertTrue(all(persona in result["recommended_personas"] for persona in ("ai-code-slop", "test-behavior-risk")))

    def test_no_paths_are_low_risk_defaults(self):
        result = run_classifier()

        self.assertEqual(result["risk_tier"], "low")
        self.assertEqual(result["triggers"], [])
        self.assertEqual(result["recommended_personas"][:4], ["doc-code-delta", "ai-code-slop", "test-behavior-risk", "reuse-architecture"])

    def test_agent_start_uses_standalone_classifier_routing(self):
        paths = ["src/auth/session_tokens.py", "docs/adr/0003-policy.md"]
        expected = classify_paths(paths)
        result = agent_start.classify_review_risk(paths)

        for key in ["changed_files", "risk_tier", "trust_profile", "recommended_personas", "triggers", "guidance"]:
            self.assertEqual(result[key], expected[key])
        self.assertIn(".codex/prompts/policies/review-risk-classifier.md", result["policy_docs"])


if __name__ == "__main__":
    unittest.main()
