import json
import re
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "review-map.schema.json"
TEMPLATE = ROOT / "workflows" / "prompts" / "templates" / "review-map.md"


def resolve_ref(schema: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    ref = node.get("$ref")
    if not ref:
        return node
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        raise AssertionError(f"unsupported ref: {ref}")
    target = schema.get("$defs", {}).get(ref.removeprefix(prefix))
    if not isinstance(target, dict):
        raise AssertionError(f"missing schema ref target: {ref}")
    return target


def validate_shape(schema: dict[str, Any], node: dict[str, Any], value: Any, path: str = "$") -> list[str]:
    node = resolve_ref(schema, node)
    errors: list[str] = []
    expected_type = node.get("type")
    if isinstance(expected_type, list):
        if value is None and "null" in expected_type:
            return []
        expected_type = next(item for item in expected_type if item != "null")
    if expected_type == "object":
        if not isinstance(value, dict):
            return [f"{path} must be object"]
        for key in node.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key} is required")
        properties = node.get("properties", {})
        if node.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}.{key} is not allowed")
        for key, child in properties.items():
            if key in value:
                errors.extend(validate_shape(schema, child, value[key], f"{path}.{key}"))
    elif expected_type == "array":
        if not isinstance(value, list):
            return [f"{path} must be array"]
        if len(value) < node.get("minItems", 0):
            errors.append(f"{path} must have at least {node['minItems']} item(s)")
        items = node.get("items")
        if isinstance(items, dict):
            for index, item in enumerate(value):
                errors.extend(validate_shape(schema, items, item, f"{path}[{index}]"))
    elif expected_type == "string":
        if not isinstance(value, str):
            return [f"{path} must be string"]
        if len(value) < node.get("minLength", 0):
            errors.append(f"{path} must not be empty")
        pattern = node.get("pattern")
        if pattern and not re.match(pattern, value):
            errors.append(f"{path} must match {pattern}")
    elif expected_type == "integer":
        if not isinstance(value, int):
            return [f"{path} must be integer"]
        if value < node.get("minimum", value):
            errors.append(f"{path} must be at least {node['minimum']}")
    if "const" in node and value != node["const"]:
        errors.append(f"{path} must equal {node['const']!r}")
    if "enum" in node and value not in node["enum"]:
        errors.append(f"{path} must be one of {node['enum']!r}")
    return errors


def sample_review_map() -> dict[str, Any]:
    artifact = {"status": "available", "reference": "local artifact", "notes": "used for routing"}
    target = {"target": "workflows/prompts/templates/review-map.md", "reason": "review artifact contract", "status": "inspected"}
    omission = {
        "item": "runtime smoke test",
        "reason": "not relevant for a template-only change",
        "residual_risk": "none for runtime behavior",
        "next_source_to_inspect": None,
    }
    return {
        "schema_version": 1,
        "review_map": {
            "id": "AGW-033",
            "repo": "/repo",
            "created_at": "2026-06-15T00:00:00Z",
            "status": "ready-for-review",
            "owner": "local worker",
        },
        "source_inputs": {
            "diff_range": "main..HEAD",
            "changed_files": [{"path": "workflows/prompts/templates/review-map.md", "note": "new template"}],
            "context_packet": {"status": "available", "reference": "make context-packet", "notes": "routing evidence"},
            "context_bundle": {"status": "not-applicable", "reference": None, "notes": "not installed in source repo"},
            "task_packet": {"status": "available", "reference": "research/agentic-workflow-review/task-packets/agw-033-review-map-artifact.md"},
            "receipts": [artifact],
            "manual_inspection_notes": ["Read the task packet and prompt index."],
        },
        "scope_summary": {
            "review_objective": "Map a broad diff into reviewable clusters.",
            "change_summary": ["Adds a review-map artifact contract."],
            "out_of_scope": ["No runner mutation."],
            "assumptions": ["Reviewers still inspect source directly."],
        },
        "change_clusters": [
            {
                "id": "prompt_contract",
                "title": "Review-map prompt contract",
                "rationale": "Template and schema define one artifact.",
                "owner_or_area": "agent-workflow-kit prompts",
                "changed_files": [{"path": "workflows/prompts/templates/review-map.md", "note": "Markdown artifact"}],
                "supporting_context": [artifact],
                "uncertainty": ["none"],
            }
        ],
        "inspection_plan": {
            "entrypoints": [target],
            "public_contracts": [target],
            "data_schema_boundaries": [{"target": "schemas/review-map.schema.json", "reason": "machine-readable contract", "status": "inspected"}],
            "operational_surfaces": [],
            "docs_and_adrs": [target],
            "scripts": [],
            "tests": [{"target": "tests/test_review_map_artifact.py", "reason": "schema/template coverage", "status": "inspected"}],
        },
        "risk_hotspots": [
            {
                "id": "source_review_bypass",
                "title": "Map mistaken for source review",
                "priority": "P2",
                "paths": ["workflows/prompts/templates/review-map.md"],
                "reason": "A map can hide uninspected files if omissions are not explicit.",
                "personas": ["doc-code-delta", "test-behavior-risk"],
                "evidence_needed": ["omissions_uncertainty is filled"],
            }
        ],
        "reviewer_routing": {
            "default_personas": [{"persona": "doc-code-delta", "scope": "docs and prompt contract"}],
            "specialist_personas": [{"persona": "api-data-contracts", "scope": "schema contract", "reason": "new JSON schema"}],
            "skipped_personas": [{"persona_or_area": "frontend-ux", "reason": "no UI", "residual_risk": "none"}],
        },
        "recommended_sequence": [
            {
                "step": 1,
                "objective": "Confirm artifact sections match the review goal.",
                "inspect": ["workflows/prompts/templates/review-map.md"],
                "exit_criteria": "Required navigation and omission sections are present.",
            }
        ],
        "validation_evidence": {
            "commands": [{"item": "python3 -m unittest tests.test_review_map_artifact", "expected_result": "pass", "status": "required"}],
            "receipts_to_capture": [artifact],
            "docs_and_adr_checks": [{"item": "make docs-check", "expected_result": "pass", "status": "required"}],
            "runtime_or_config_checks": [],
            "evidence_gaps": [omission],
        },
        "omissions_uncertainty": {
            "skipped_files": [],
            "unclassified_paths": [],
            "missing_context_data": [],
            "ambiguous_ownership": [],
            "validation_gaps": [omission],
            "other_unknowns": [],
        },
        "follow_up_task_packet_candidates": [
            {
                "title": "Add deeper codegraph lookup",
                "rationale": "Keep LSP work separate from the review-map artifact.",
                "likely_scope": ["AGW-034"],
                "priority": "P2",
                "trigger": "Need definition/usages beyond context packet hints.",
            }
        ],
        "disposition": {
            "map_status": "ready-for-review",
            "handoff_notes": ["Use the map for navigation, then inspect source evidence directly."],
        },
    }


class ReviewMapArtifactTests(unittest.TestCase):
    def test_schema_has_expected_contract_sections(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        required = set(schema["required"])
        self.assertTrue(
            {
                "source_inputs",
                "scope_summary",
                "change_clusters",
                "inspection_plan",
                "risk_hotspots",
                "reviewer_routing",
                "recommended_sequence",
                "validation_evidence",
                "omissions_uncertainty",
                "follow_up_task_packet_candidates",
            }
            <= required
        )
        omissions = schema["properties"]["omissions_uncertainty"]
        self.assertEqual(
            set(omissions["required"]),
            {
                "skipped_files",
                "unclassified_paths",
                "missing_context_data",
                "ambiguous_ownership",
                "validation_gaps",
                "other_unknowns",
            },
        )

    def test_schema_accepts_representative_review_map_shape(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

        errors = validate_shape(schema, schema, sample_review_map())

        self.assertEqual(errors, [])

    def test_markdown_template_names_navigation_and_omission_sections(self):
        template = TEMPLATE.read_text(encoding="utf-8")

        required_sections = [
            "## Source Inputs",
            "## Scope Summary And Review Objective",
            "## Changed-File Clusters",
            "## Entry Points And Contracts To Inspect",
            "## Risk Hotspots And Reviewer Routing",
            "## Recommended Review Sequence",
            "## Validation And Evidence To Capture",
            "## Omissions And Uncertainty",
            "## Follow-Up Task-Packet Candidates",
        ]
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, template)
        for phrase in (
            "make context-packet",
            "context bundle",
            "not a replacement for reading the changed source",
            "Skipped files",
            "Unclassified paths",
            "Missing context-packet or context-bundle data",
            "Ambiguous ownership",
            "Validation gaps",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, template)


if __name__ == "__main__":
    unittest.main()
