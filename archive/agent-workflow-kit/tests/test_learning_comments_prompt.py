import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PROMPT = ROOT / "workflows" / "prompts" / "codebase-learning-comments.md"
CODEX_PROMPT = ROOT / ".codex" / "prompts" / "codebase-learning-comments.md"


class LearningCommentsPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prompt = SOURCE_PROMPT.read_text(encoding="utf-8")
        cls.normalized_prompt = " ".join(cls.prompt.split())

    def assertPromptContains(self, phrase):
        self.assertIn(" ".join(phrase.split()), self.normalized_prompt)

    def test_declares_deterministic_decision_discovery_order(self):
        required_phrases = [
            "Use deterministic decision-source discovery before broad scanning",
            "`make agent-start` output",
            "the session-start latest-ADR field",
            "Agent Start Brief latest-ADR or no-ADR warnings",
            "context-packet or context-bundle ADR",
            "task-packet, backlog-row, issue, or",
            "the repo's ADR directory when present",
            "plural ADR directories under docs",
            "top-level adr/adrs directories",
            "architecture/design/decision docs",
            "Treat the latest/current ADR or decision record as a constraint/default",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertPromptContains(phrase)

    def test_declares_no_adr_fallback_and_uncertainty_rules(self):
        required_phrases = [
            "`No ADR or decision record found`",
            "Fall back to README, docs,",
            "tests, code, config, changelog, issue/task context, and operator",
            "Do not fabricate architecture intent, product rationale, or",
            "Proceed only with evidence-backed comments or explanation",
            "mark unresolved architecture or terminology questions as",
            "unsupported claims that must stay out of comments",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertPromptContains(phrase)

    def test_requires_adr_reader_output_and_verification_evidence(self):
        required_phrases = [
            "ADR Reader: starts from existing agent-start/latest-ADR evidence",
            "files inspected, the latest/current decision source if any",
            "superseded or conflicting decisions",
            "no-ADR fallback evidence used",
            "unsupported claims that must stay out of comments",
            "Decision evidence inspected: latest/current decision source",
            "Decision-source check: latest/current/superseded ADR state",
            "explicit no-ADR fallback evidence",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertPromptContains(phrase)

    def test_codex_adapter_matches_canonical_prompt(self):
        self.assertEqual(
            CODEX_PROMPT.read_text(encoding="utf-8"),
            SOURCE_PROMPT.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
