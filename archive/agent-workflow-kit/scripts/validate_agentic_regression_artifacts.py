#!/usr/bin/env python3
"""Validate and materialize seed agentic-regression artifacts.

The harness intentionally stays stdlib-only so it can run in locked-down target
repos before any project dependency bootstrap has happened.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


# Script flow:
# 1. Load backlog, fixture, permission-policy, and schema artifacts.
# 2. Validate IDs, references, controls, and expected source files.
# 3. Optionally materialize task packets from fixtures for downstream review.
# 4. Fail fast when any generated or hand-maintained artifact drifts.
#
# Function guide:
# - load_json/load_backlog_ids read source artifacts.
# - local_source_exists/resolve_ref/schema_path_exists support reference checks.
# - require accumulates validation errors.
# - validate_fixtures/validate_permission_policy/validate_task_packet enforce contracts.
# - build_task_packet/emit_task_packets produce derived JSON packets.
# - parse_args/main drive validation and optional packet emission.
ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "research/agentic-workflow-review/backlog.csv"
FIXTURE_SUITE = ROOT / "research/agentic-regression-research/fixtures/agentic-regression-seed.json"
PERMISSION_EXAMPLE = ROOT / "examples/agent-permission-policy.local-first.json"
SESSION_RECEIPT_SCHEMA = ROOT / "schemas/session-receipt.schema.json"
TASK_PACKET_SCHEMA = ROOT / "schemas/task-packet.schema.json"

FIXTURE_ID_RE = re.compile(r"^ARF-[0-9]{3}$")
BACKLOG_ID_RE = re.compile(r"^AGW-[0-9]{3}$")

ALLOWED_FAILURE_MODES = {
    "context-drift",
    "unfinished-prior-task-start",
    "instruction-drift",
    "false-positive-review",
    "missing-red-green-evidence",
    "unsafe-tool-use",
    "duplicate-multi-agent-findings",
    "docs-impact-miss",
}

ALLOWED_CONTROLS = {
    "closeout-first-startup",
    "context-packet",
    "deterministic-report-routing",
    "instruction-lint",
    "permission-policy",
    "receipt-validation",
    "review-synthesis-schema",
    "tdd-red-green",
    "finding-budget",
    "read-only-policy",
    "docs-impact-localizer",
}

CONTROL_HINTS = {
    "closeout-first-startup": "Confirm task packets and implementation prompts require previous task state, finalizer or blocker receipts, and safe/refuse/escalate startup decisions.",
    "context-packet": "Confirm the run includes changed files, callers, tests, docs, ADRs, scripts, and runtime/config context where applicable.",
    "deterministic-report-routing": "Confirm prompts prefer compact deterministic reports before broad repo rereads and preserve omission evidence.",
    "instruction-lint": "Confirm prompt and instruction changes preserve required fields, avoid contradiction, and do not drop policy language.",
    "permission-policy": "Confirm the selected permission profile denies mutations outside the approved trust level.",
    "receipt-validation": "Confirm the run writes or validates the receipt fields named by this fixture.",
    "review-synthesis-schema": "Confirm synthesis output can be represented by schemas/review-synthesis.schema.json.",
    "tdd-red-green": "Confirm failing-before and passing-after evidence is captured, or an exception reason is explicit.",
    "finding-budget": "Confirm low-signal or duplicate findings are capped, merged, or rejected.",
    "read-only-policy": "Confirm read-only reviewers do not write files, stage commits, push, or mutate accounts.",
    "docs-impact-localizer": "Confirm docs-impact evidence is present when shared contracts are touched.",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_backlog_ids() -> set[str]:
    with BACKLOG.open(newline="", encoding="utf-8") as handle:
        return {row["id"] for row in csv.DictReader(handle)}


def local_source_exists(source: str) -> bool:
    if source.startswith(("http://", "https://")):
        return True
    return (ROOT / source).exists()


def resolve_ref(schema: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    ref = node.get("$ref")
    if not isinstance(ref, str):
        return node
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        return node
    target = schema.get("$defs", {}).get(ref.removeprefix(prefix))
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


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_fixtures(errors: list[str]) -> None:
    backlog_ids = load_backlog_ids()
    receipt_schema = load_json(SESSION_RECEIPT_SCHEMA)
    task_packet_schema = load_json(TASK_PACKET_SCHEMA)
    require(isinstance(receipt_schema, dict), "session receipt schema must be an object", errors)
    require(isinstance(task_packet_schema, dict), "task packet schema must be an object", errors)

    suite = load_json(FIXTURE_SUITE)
    require(isinstance(suite, dict), "fixture suite must be an object", errors)
    if not isinstance(suite, dict):
        return

    require(suite.get("schema_version") == 1, "fixture suite schema_version must be 1", errors)
    suite_meta = suite.get("suite")
    require(isinstance(suite_meta, dict), "fixture suite needs suite metadata", errors)
    if isinstance(suite_meta, dict):
        source_reports = suite_meta.get("source_reports")
        require(isinstance(source_reports, list) and bool(source_reports), "suite.source_reports must be non-empty", errors)
        for source in source_reports if isinstance(source_reports, list) else []:
            require(isinstance(source, str) and local_source_exists(source), f"suite source report is missing: {source}", errors)

    fixtures = suite.get("fixtures")
    require(isinstance(fixtures, list) and bool(fixtures), "fixture suite needs fixtures", errors)
    if not isinstance(fixtures, list):
        return

    seen_ids: set[str] = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            errors.append("fixture entries must be objects")
            continue
        fixture_id = fixture.get("id")
        require(isinstance(fixture_id, str) and bool(FIXTURE_ID_RE.fullmatch(fixture_id)), "fixture id must use ARF-000 format", errors)
        require(fixture_id not in seen_ids, f"duplicate fixture id {fixture_id}", errors)
        seen_ids.add(str(fixture_id))
        require(fixture.get("failure_mode") in ALLOWED_FAILURE_MODES, f"{fixture_id} has invalid failure_mode", errors)

        source_examples = fixture.get("source_examples", [])
        require(isinstance(source_examples, list) and bool(source_examples), f"{fixture_id} needs source_examples", errors)
        for source in source_examples if isinstance(source_examples, list) else []:
            require(isinstance(source, str) and local_source_exists(source), f"{fixture_id} source example is missing: {source}", errors)

        scenario = fixture.get("scenario")
        require(isinstance(scenario, dict), f"{fixture_id} needs scenario", errors)
        if isinstance(scenario, dict):
            for key in ["request", "repo_state"]:
                require(isinstance(scenario.get(key), str) and bool(scenario[key].strip()), f"{fixture_id} scenario.{key} must be non-empty", errors)
            inputs = scenario.get("inputs")
            require(isinstance(inputs, list) and bool(inputs), f"{fixture_id} scenario.inputs must be non-empty", errors)

        controls = fixture.get("expected_controls", [])
        require(isinstance(controls, list) and bool(controls), f"{fixture_id} needs expected_controls", errors)
        for control in controls if isinstance(controls, list) else []:
            require(control in ALLOWED_CONTROLS, f"{fixture_id} has invalid control {control}", errors)

        outputs = fixture.get("expected_outputs")
        require(isinstance(outputs, dict), f"{fixture_id} needs expected_outputs", errors)
        if isinstance(outputs, dict):
            for key in ["must_include", "must_reject", "required_receipt_fields"]:
                require(isinstance(outputs.get(key), list), f"{fixture_id} expected_outputs.{key} must be a list", errors)
            if isinstance(receipt_schema, dict):
                for field in outputs.get("required_receipt_fields", []):
                    require(
                        isinstance(field, str) and schema_path_exists(receipt_schema, field),
                        f"{fixture_id} references missing receipt field {field}",
                        errors,
                    )

        for backlog_id in fixture.get("target_backlog", []):
            require(isinstance(backlog_id, str) and bool(BACKLOG_ID_RE.fullmatch(backlog_id)), f"{fixture_id} has invalid backlog id {backlog_id}", errors)
            require(backlog_id in backlog_ids, f"{fixture_id} references missing backlog id {backlog_id}", errors)

        validate_task_packet(build_task_packet(fixture), task_packet_schema, f"{fixture_id} generated task packet", errors)


def validate_permission_policy(errors: list[str]) -> None:
    policy = load_json(PERMISSION_EXAMPLE)
    require(isinstance(policy, dict), "permission policy must be an object", errors)
    if not isinstance(policy, dict):
        return

    profiles = policy.get("profiles")
    require(isinstance(profiles, list) and bool(profiles), "permission policy needs profiles", errors)
    if not isinstance(profiles, list):
        return

    by_name = {profile.get("name"): profile for profile in profiles if isinstance(profile, dict)}
    default_profile = policy.get("default_profile")
    require(default_profile in by_name, "default_profile must exist in profiles", errors)

    read_only = by_name.get("read-only-review")
    require(isinstance(read_only, dict), "read-only-review profile is required", errors)
    if isinstance(read_only, dict):
        require(read_only["filesystem"]["write"] == "deny", "read-only-review must deny filesystem writes", errors)
        require(read_only["filesystem"]["delete"] == "deny", "read-only-review must deny filesystem deletes", errors)
        for action in ["stage", "commit", "push"]:
            require(read_only["git"][action] == "deny", f"read-only-review must deny git {action}", errors)
        require(read_only["browser"]["account_mutation"] == "deny", "read-only-review must deny browser account mutation", errors)

    browser_research = by_name.get("browser-research")
    require(isinstance(browser_research, dict), "browser-research profile is required", errors)
    if isinstance(browser_research, dict):
        require(browser_research["browser"]["account_mutation"] == "deny", "browser-research must deny account mutation", errors)
        require(browser_research["browser"]["captcha_bypass"] == "deny", "browser-research must deny captcha bypass", errors)
        require(browser_research["git"]["commit"] == "deny", "browser-research must deny git commit", errors)
        require(browser_research["git"]["push"] == "deny", "browser-research must deny git push", errors)


def build_task_packet(fixture: dict[str, Any]) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    scenario = fixture["scenario"]
    expected_outputs = fixture["expected_outputs"]
    controls = list(fixture["expected_controls"])
    target_backlog = list(fixture["target_backlog"])

    acceptance_criteria = [
        {
            "description": f"Control is present: {control}",
            "verification": CONTROL_HINTS[control],
        }
        for control in controls
    ]
    acceptance_criteria.extend(
        {
            "description": f"Output includes: {item}",
            "verification": "Inspect the generated receipt, synthesis output, or runner artifact for this fixture.",
        }
        for item in expected_outputs["must_include"]
    )
    acceptance_criteria.extend(
        {
            "description": f"Output rejects: {item}",
            "verification": "Confirm the final artifact either omits this failure pattern or records it as rejected/not recommended.",
        }
        for item in expected_outputs["must_reject"]
    )

    return {
        "schema_version": 1,
        "task": {
            "id": f"AGW-056-{fixture_id}",
            "title": f"Regression fixture: {fixture['title']}",
            "priority": "P0",
            "status": "draft",
            "source": {
                "type": "backlog",
                "reference": ",".join(target_backlog),
            },
        },
        "context": {
            "repo_root": ".",
            "mode": "verification",
            "problem_statement": scenario["request"],
            "background": [
                f"Failure mode: {fixture['failure_mode']}",
                f"Repo state: {scenario['repo_state']}",
                "Source examples: " + ", ".join(fixture["source_examples"]),
            ],
            "non_goals": [
                "Do not mutate repository files during read-only review fixtures.",
                "Do not treat anecdotal source examples as proof of model behavior without local evidence.",
            ],
        },
        "previous_task_state": {
            "report_sources": [
                "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
                f".agent-workflows/tasks/agw-056-{fixture_id.lower()}/finalizer-receipt.json",
            ],
            "active_tasks": [],
            "unresolved_blockers": [],
            "dirty_or_stale_state": [],
            "finalizer_receipt_paths": [
                f".agent-workflows/tasks/agw-056-{fixture_id.lower()}/finalizer-receipt.json"
            ],
            "blocker_receipt_paths": [],
            "allowed_to_start": True,
            "notes": "Generated fixture packet assumes previous task state is closed before this draft is implemented.",
        },
        "closeout_required_before_start": {
            "decision": "safe-start",
            "reason": "Generated fixture packet includes a finalizer receipt path and no unresolved previous-task blockers.",
            "required_next_step": "Proceed only after confirming the finalizer receipt path or replace this with blocker-escalation evidence.",
            "evidence_paths": [
                f".agent-workflows/tasks/agw-056-{fixture_id.lower()}/finalizer-receipt.json"
            ],
        },
        "goal_alignment": {
            "repo_goal": (
                "Keep agent-workflow-kit regression fixtures aligned with the local-first harness contract "
                "so prompt and schema changes preserve bounded, evidence-backed agent behavior."
            ),
            "area_contracts": [
                {
                    "path": "research/agentic-regression-research/**",
                    "purpose": "Fixture data captures known agent workflow failure modes and expected controls.",
                    "source": (
                        "docs/harness-engineering.md; "
                        "research/agentic-regression-research/fixtures/agentic-regression-seed.json"
                    ),
                    "status": "aligned",
                },
                {
                    "path": "scripts/validate_agentic_regression_artifacts.py",
                    "purpose": "Stdlib validator materializes and checks source-owned regression task packets.",
                    "source": "scripts/validate_agentic_regression_artifacts.py",
                    "status": "aligned",
                },
                {
                    "path": ".codex/prompts/**",
                    "purpose": "Generated adapter mirror of canonical workflow prompts, refreshed from workflows/prompts.",
                    "source": "workflows/manifest.json",
                    "status": "aligned",
                },
            ],
            "alignment_decision": "aligned",
            "adaptation_needed": False,
            "stop_conditions": [
                "Stop if fixture work requires changing installed repo-contract-kit task-packet generators instead of source-owned fixtures.",
                "Stop if an affected area purpose is unknown or conflicts with the read-only regression fixture boundary.",
            ],
        },
        "scope": {
            "allowed_files": [
                ".codex/prompts/**",
                "schemas/**",
                "research/agentic-regression-research/**",
                "scripts/validate_agentic_regression_artifacts.py",
            ],
            "protected_files": [".git/**", ".env", ".secrets"],
            "inspect_first": scenario["inputs"],
            "expected_outputs": expected_outputs["must_include"] + expected_outputs["must_reject"],
        },
        "acceptance_criteria": acceptance_criteria,
        "validation": {
            "commands": [
                {
                    "command": "python3 scripts/validate_agentic_regression_artifacts.py",
                    "required": True,
                    "expected_result": "passes all fixture, permission-policy, and generated task-packet checks",
                }
            ],
            "evidence_to_capture": expected_outputs["required_receipt_fields"],
        },
        "closeout_requirements": {
            "final_receipt_path": f".agent-workflows/tasks/agw-056-{fixture_id.lower()}/receipt.json",
            "readiness_check": {
                "command": f"make agent-task-ready TASK=AGW-056-{fixture_id} TASK_READY_JSON=1",
                "expected_result": "readiness passes or records fixture-specific blockers before handoff",
            },
            "lifecycle_action": {
                "action": "finish",
                "command": (
                    f"make agent-task-finalize TASK=AGW-056-{fixture_id} "
                    f"TASK_RECEIPT=.agent-workflows/tasks/agw-056-{fixture_id.lower()}/receipt.json "
                    "TASK_FINALIZE_JSON=1"
                ),
                "expected_result": "task metadata is terminal and the fixture receipt is linked",
            },
            "final_task_status": {
                "command": "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
                "expected_result": "closed task metadata, final receipt, and active overlap state are visible",
            },
            "closeout_preview": {
                "command": "make agent-task-closeout TASK_CLOSEOUT_JSON=1",
                "expected_result": "finished worktree cleanup is eligible, retained, or blocked with reasons",
                "apply_requires_explicit_approval": True,
            },
            "dirty_state_explanation": "Record whether the checkout is clean, contains only expected fixture artifacts, or preserves unrelated dirty work.",
        },
        "docs_impact": {
            "expected": "yes",
            "paths": [
                "research/agentic-regression-research/fixtures/README.md",
                "research/agentic-workflow-review/backlog.csv",
            ],
            "waiver_allowed": False,
            "notes": "Fixture harness changes should update the fixture documentation and backlog status.",
        },
        "risk": {
            "level": "medium",
            "known_risks": [
                "A fixture can pass shape validation while still being too vague to catch a real prompt regression.",
                "A policy fixture can describe denied actions that the eventual runner does not enforce.",
            ],
            "stop_conditions": [
                "A fixture references missing local source reports or missing backlog IDs.",
                "A required receipt field cannot be found in schemas/session-receipt.schema.json.",
            ],
        },
        "approval": {
            "human_approval_required": True,
            "state": "not-requested",
            "approver": None,
            "notes": "Generated packets are draft execution handoffs until a human selects one for implementation.",
        },
        "handoff": {
            "recommended_prompt": ".codex/prompts/task-packet.md",
            "owner": "agent-workflow-kit",
            "dependencies": target_backlog,
            "next_packet_hint": "Promote this fixture into a runnable golden prompt test once the runner exists.",
        },
    }


def validate_task_packet(packet: dict[str, Any], schema: Any, label: str, errors: list[str]) -> None:
    required_keys = set(schema.get("required", [])) if isinstance(schema, dict) else set()
    require(set(packet) >= required_keys, f"{label} is missing required task-packet keys", errors)
    require(packet.get("schema_version") == 1, f"{label} schema_version must be 1", errors)
    task = packet.get("task")
    require(isinstance(task, dict), f"{label} task must be an object", errors)
    if isinstance(task, dict):
        require(task.get("priority") in {"P0", "P1", "P2", "P3"}, f"{label} task priority is invalid", errors)
        require(task.get("status") in {"draft", "approved", "in-progress", "blocked", "done", "deferred"}, f"{label} task status is invalid", errors)
    context = packet.get("context")
    require(isinstance(context, dict) and context.get("mode") == "verification", f"{label} context.mode must be verification", errors)
    previous_task_state = packet.get("previous_task_state")
    require(isinstance(previous_task_state, dict), f"{label} needs previous_task_state", errors)
    if isinstance(previous_task_state, dict):
        for key in [
            "report_sources",
            "active_tasks",
            "unresolved_blockers",
            "dirty_or_stale_state",
            "finalizer_receipt_paths",
            "blocker_receipt_paths",
            "allowed_to_start",
        ]:
            require(key in previous_task_state, f"{label} previous_task_state.{key} is required", errors)
        report_sources = previous_task_state.get("report_sources")
        require(
            isinstance(report_sources, list) and bool(report_sources),
            f"{label} previous_task_state.report_sources must be non-empty",
            errors,
        )
        for key in [
            "active_tasks",
            "unresolved_blockers",
            "dirty_or_stale_state",
            "finalizer_receipt_paths",
            "blocker_receipt_paths",
        ]:
            require(isinstance(previous_task_state.get(key), list), f"{label} previous_task_state.{key} must be a list", errors)
        require(
            isinstance(previous_task_state.get("allowed_to_start"), bool),
            f"{label} previous_task_state.allowed_to_start must be boolean",
            errors,
        )
    closeout_gate = packet.get("closeout_required_before_start")
    require(isinstance(closeout_gate, dict), f"{label} needs closeout_required_before_start", errors)
    if isinstance(closeout_gate, dict):
        for key in ["decision", "reason", "required_next_step"]:
            require(bool(closeout_gate.get(key)), f"{label} closeout_required_before_start.{key} is required", errors)
        decision = closeout_gate.get("decision")
        require(
            decision in {"safe-start", "refuse-start", "blocker-escalation"},
            f"{label} closeout_required_before_start.decision is invalid",
            errors,
        )
        if isinstance(previous_task_state, dict):
            finalizer_paths = previous_task_state.get("finalizer_receipt_paths")
            blocker_paths = previous_task_state.get("blocker_receipt_paths")
            allowed = previous_task_state.get("allowed_to_start")
            if decision == "safe-start":
                require(allowed is True, f"{label} safe-start requires previous_task_state.allowed_to_start=true", errors)
                require(
                    isinstance(finalizer_paths, list) and bool(finalizer_paths),
                    f"{label} safe-start requires finalizer receipt evidence",
                    errors,
                )
            elif decision in {"refuse-start", "blocker-escalation"}:
                require(allowed is False, f"{label} {decision} requires previous_task_state.allowed_to_start=false", errors)
                require(
                    isinstance(blocker_paths, list) and bool(blocker_paths),
                    f"{label} {decision} requires blocker receipt evidence",
                    errors,
                )
    goal_alignment = packet.get("goal_alignment")
    require(isinstance(goal_alignment, dict), f"{label} needs goal_alignment", errors)
    if isinstance(goal_alignment, dict):
        for key in ["repo_goal", "area_contracts", "alignment_decision", "adaptation_needed", "stop_conditions"]:
            require(key in goal_alignment, f"{label} goal_alignment.{key} is required", errors)
        require(
            goal_alignment.get("alignment_decision") in {"aligned", "unknown", "conflict", "adaptation-needed"},
            f"{label} goal_alignment.alignment_decision is invalid",
            errors,
        )
        require(
            isinstance(goal_alignment.get("adaptation_needed"), bool),
            f"{label} goal_alignment.adaptation_needed must be boolean",
            errors,
        )
        area_contracts = goal_alignment.get("area_contracts")
        require(
            isinstance(area_contracts, list) and bool(area_contracts),
            f"{label} goal_alignment.area_contracts must be non-empty",
            errors,
        )
        for area in area_contracts if isinstance(area_contracts, list) else []:
            require(isinstance(area, dict), f"{label} goal_alignment.area_contracts entries must be objects", errors)
            if isinstance(area, dict):
                for key in ["path", "purpose", "status"]:
                    require(bool(area.get(key)), f"{label} goal_alignment.area_contracts[].{key} is required", errors)
                require(
                    area.get("status") in {"aligned", "unknown", "conflict", "not-applicable"},
                    f"{label} goal_alignment.area_contracts[].status is invalid",
                    errors,
                )
        stop_conditions = goal_alignment.get("stop_conditions")
        require(
            isinstance(stop_conditions, list) and bool(stop_conditions),
            f"{label} goal_alignment.stop_conditions must be non-empty",
            errors,
        )
    criteria = packet.get("acceptance_criteria")
    require(isinstance(criteria, list) and bool(criteria), f"{label} needs acceptance criteria", errors)
    validation = packet.get("validation")
    require(isinstance(validation, dict) and bool(validation.get("commands")), f"{label} needs validation commands", errors)
    closeout = packet.get("closeout_requirements")
    require(isinstance(closeout, dict), f"{label} needs closeout requirements", errors)
    if isinstance(closeout, dict):
        for key in [
            "final_receipt_path",
            "readiness_check",
            "lifecycle_action",
            "final_task_status",
            "closeout_preview",
            "dirty_state_explanation",
        ]:
            require(bool(closeout.get(key)), f"{label} closeout_requirements.{key} is required", errors)


def emit_task_packets(output_dir: Path) -> int:
    suite = load_json(FIXTURE_SUITE)
    if not isinstance(suite, dict) or not isinstance(suite.get("fixtures"), list):
        raise ValueError("fixture suite is malformed; run validation first")

    output_dir.mkdir(parents=True, exist_ok=True)
    for fixture in suite["fixtures"]:
        packet = build_task_packet(fixture)
        packet_path = output_dir / f"{fixture['id'].lower()}-task-packet.json"
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return len(suite["fixtures"])


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit-task-packets",
        type=Path,
        metavar="DIR",
        help="Write one draft task-packet JSON artifact per regression fixture.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    errors: list[str] = []
    validate_fixtures(errors)
    validate_permission_policy(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    fixture_count = len(load_json(FIXTURE_SUITE)["fixtures"])  # type: ignore[index]
    profile_count = len(load_json(PERMISSION_EXAMPLE)["profiles"])  # type: ignore[index]
    if args.emit_task_packets:
        emitted = emit_task_packets(args.emit_task_packets)
        print(f"emitted {emitted} task packets to {args.emit_task_packets}")
    print(f"validated {fixture_count} regression fixtures, {fixture_count} generated task packets, and {profile_count} permission profiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
