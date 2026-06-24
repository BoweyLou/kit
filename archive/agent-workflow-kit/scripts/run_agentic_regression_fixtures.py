#!/usr/bin/env python3
"""Run deterministic checks for the seed agentic-regression fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# Script flow:
# 1. Load the seed regression fixture suite and supporting repo artifacts.
# 2. Resolve schema references and validate each fixture's expected controls.
# 3. Check that prompts, schemas, policies, research notes, and plan files exist.
# 4. Exit non-zero if any fixture no longer matches the repo contract.
#
# Function guide:
# - load_json/read_text load fixture and repo files.
# - resolve_ref/schema_path_exists inspect JSON schema paths.
# - require records validation failures.
# - profiles_by_name/check_control/run_fixture enforce fixture expectations.
# - parse_args/main run the suite from the CLI.
ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SUITE = ROOT / "research/agentic-regression-research/fixtures/agentic-regression-seed.json"
RECEIPT_SCHEMA = ROOT / "schemas/session-receipt.schema.json"
REVIEW_SYNTHESIS_SCHEMA = ROOT / "schemas/review-synthesis.schema.json"
REVIEW_SYNTHESIS_PROMPT = ROOT / ".codex/prompts/review-synthesis.md"
PERSONA_MANIFEST = ROOT / ".codex/prompts/personas/manifest.json"
TDD_PROMPT_DIR = ROOT / ".codex/prompts/tdd"
PERMISSION_SCHEMA = ROOT / "schemas/agent-permission-policy.schema.json"
PERMISSION_EXAMPLE = ROOT / "examples/agent-permission-policy.local-first.json"
FINDINGS_REPORT = ROOT / "research/agentic-regression-research/2026-05-06-findings.md"
PLAN = ROOT / "docs/local-tool-agnostic-plan.md"
PROMPT_INDEX = ROOT / ".codex/prompts/README.md"
TASK_PACKET_PROMPT = ROOT / ".codex/prompts/task-packet.md"
MAINTAINER_QUEUE_PROMPT = ROOT / ".codex/prompts/maintainer-queue.md"
FIX_IMPLEMENTER_PROMPT = ROOT / ".codex/prompts/fix-implementer.md"
VERIFICATION_SENTINEL_PROMPT = ROOT / ".codex/prompts/verification-sentinel.md"
HARNESS_DOC = ROOT / "docs/harness-engineering.md"
WORKING_RHYTHM_DOC = ROOT / "docs/working-rhythm.md"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Missing required file: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def resolve_ref(schema: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    ref = node.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/$defs/"):
        return node
    target = schema.get("$defs", {}).get(ref.removeprefix("#/$defs/"))
    return target if isinstance(target, dict) else node


def schema_path_exists(schema: dict[str, Any], dotted_path: str) -> bool:
    node: dict[str, Any] = schema
    for raw_part in dotted_path.split("."):
        array_part = raw_part.endswith("[]")
        part = raw_part[:-2] if array_part else raw_part
        node = resolve_ref(schema, node)
        properties = node.get("properties")
        if not isinstance(properties, dict) or part not in properties:
            return False
        next_node = properties[part]
        if not isinstance(next_node, dict):
            return False
        next_node = resolve_ref(schema, next_node)
        if array_part:
            if next_node.get("type") != "array":
                return False
            items = next_node.get("items")
            if not isinstance(items, dict):
                return False
            next_node = resolve_ref(schema, items)
        node = next_node
    return True


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def profiles_by_name() -> dict[str, dict[str, Any]]:
    policy = load_json(PERMISSION_EXAMPLE)
    profiles = policy.get("profiles", []) if isinstance(policy, dict) else []
    return {
        profile.get("name"): profile
        for profile in profiles
        if isinstance(profile, dict) and profile.get("name")
    }


def check_control(control: str, fixture: dict[str, Any], receipt_schema: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    synthesis_text = read_text(REVIEW_SYNTHESIS_PROMPT)
    findings_text = read_text(FINDINGS_REPORT)
    plan_text = read_text(PLAN)

    if control == "receipt-validation":
        require((ROOT / "scripts/validate_agentic_regression_artifacts.py").exists(), "fixture validator script is missing", failures)
        for field in fixture["expected_outputs"]["required_receipt_fields"]:
            require(schema_path_exists(receipt_schema, field), f"receipt field is missing: {field}", failures)
    elif control == "closeout-first-startup":
        combined = "\n".join(
            read_text(path).lower()
            for path in [
                PROMPT_INDEX,
                TASK_PACKET_PROMPT,
                MAINTAINER_QUEUE_PROMPT,
                FIX_IMPLEMENTER_PROMPT,
                VERIFICATION_SENTINEL_PROMPT,
                HARNESS_DOC,
                WORKING_RHYTHM_DOC,
            ]
        )
        for phrase in [
            "previous_task_state",
            "closeout_required_before_start",
            "safe-start",
            "refuse-start",
            "blocker-escalation",
            "finalizer",
            "blocker receipt",
            "before edits",
        ]:
            require(phrase in combined, f"closeout-first startup is missing phrase: {phrase}", failures)
    elif control == "review-synthesis-schema":
        schema = load_json(REVIEW_SYNTHESIS_SCHEMA)
        required = set(schema.get("required", []))
        require({"findings", "not_recommended", "disposition"} <= required, "review synthesis schema is missing noise/disposition fields", failures)
        require(
            "false_positive" in synthesis_text or "false-positive" in synthesis_text,
            "review synthesis prompt no longer asks for false-positive handling",
            failures,
        )
        require("not_recommended" in json.dumps(schema), "review synthesis schema is missing not_recommended", failures)
    elif control == "tdd-red-green":
        require(schema_path_exists(receipt_schema, "evidence.tests.failing_test_evidence"), "receipt schema lacks failing test evidence", failures)
        require(schema_path_exists(receipt_schema, "evidence.tests.passing_test_evidence"), "receipt schema lacks passing test evidence", failures)
        require("red/green" in read_text(TDD_PROMPT_DIR / "README.md").lower(), "TDD prompt README no longer mentions red/green evidence", failures)
    elif control == "permission-policy":
        require(PERMISSION_SCHEMA.exists(), "permission policy schema is missing", failures)
        require(PERMISSION_EXAMPLE.exists(), "permission policy example is missing", failures)
    elif control == "read-only-policy":
        profiles = profiles_by_name()
        read_only = profiles.get("read-only-review")
        require(bool(read_only), "read-only-review policy profile is missing", failures)
        if read_only:
            require(read_only["filesystem"]["write"] == "deny", "read-only-review must deny filesystem writes", failures)
            require(read_only["git"]["commit"] == "deny", "read-only-review must deny git commit", failures)
            require(read_only["browser"]["account_mutation"] == "deny", "read-only-review must deny browser account mutation", failures)
    elif control == "finding-budget":
        manifest = load_json(PERSONA_MANIFEST)
        personas = manifest.get("personas", []) if isinstance(manifest, dict) else []
        require(all("max_findings" in persona for persona in personas if isinstance(persona, dict)), "one or more personas lack max_findings", failures)
        require("Suppress nits" in synthesis_text, "synthesis prompt no longer suppresses nits by default", failures)
    elif control == "context-packet":
        context_words = ["changed files", "callers", "tests", "docs", "ADRs", "runtime configs"]
        lower = findings_text.lower() + "\n" + plan_text.lower()
        for word in context_words:
            require(word.lower() in lower, f"context-packet evidence is missing term: {word}", failures)
    elif control == "deterministic-report-routing":
        combined = "\n".join(
            read_text(path).lower()
            for path in [
                PROMPT_INDEX,
                TASK_PACKET_PROMPT,
                MAINTAINER_QUEUE_PROMPT,
                VERIFICATION_SENTINEL_PROMPT,
                HARNESS_DOC,
                WORKING_RHYTHM_DOC,
            ]
        )
        for phrase in [
            "agent-context-bundle",
            "deterministic reports",
            "broad repo rereads",
            "scoped source",
            "omission",
        ]:
            require(phrase in combined, f"deterministic report routing is missing phrase: {phrase}", failures)
        require(
            "missing, stale, blocked, ambiguous" in combined or "missing, stale, blocked, or ambiguous" in combined,
            "deterministic report routing lacks fallback language for missing/stale/blocked/ambiguous reports",
            failures,
        )
    elif control == "docs-impact-localizer":
        combined = plan_text.lower() + "\n" + findings_text.lower()
        require("docs-impact" in combined or "docs impact" in combined, "docs-impact localizer guidance is missing", failures)
    elif control == "instruction-lint":
        require("instruction drift" in findings_text.lower(), "instruction-drift finding rationale is missing", failures)
    else:
        failures.append(f"unknown control: {control}")
    return failures


def run_fixture(fixture: dict[str, Any], receipt_schema: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    for control in fixture["expected_controls"]:
        failures.extend(f"{control}: {failure}" for failure in check_control(control, fixture, receipt_schema))
    return {
        "fixture_id": fixture["id"],
        "title": fixture["title"],
        "failure_mode": fixture["failure_mode"],
        "status": "fail" if failures else "pass",
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable fixture results")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    suite = load_json(FIXTURE_SUITE)
    receipt_schema = load_json(RECEIPT_SCHEMA)
    fixtures = suite.get("fixtures", []) if isinstance(suite, dict) else []
    results = [run_fixture(fixture, receipt_schema) for fixture in fixtures]
    failures = [result for result in results if result["status"] == "fail"]
    report = {
        "schema_version": 1,
        "suite": suite.get("suite", {}).get("name") if isinstance(suite, dict) else None,
        "status": "fail" if failures else "pass",
        "fixture_count": len(results),
        "failure_count": len(failures),
        "results": results,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for result in results:
            print(f"{result['status'].upper()} {result['fixture_id']}: {result['title']}")
            for failure in result["failures"]:
                print(f"  - {failure}")
        print(f"Agentic regression fixtures {report['status']} ({len(results) - len(failures)}/{len(results)} passing).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
