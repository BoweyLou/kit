#!/usr/bin/env python3
"""Render a concise Markdown summary from a session receipt JSON file."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


# Script flow:
# 1. Load one session receipt JSON file.
# 2. Normalize optional receipt sections into safe dict/list values.
# 3. Count and format review findings, command results, and labels.
# 4. Print a concise Markdown summary for humans.
#
# Function guide:
# - load_json/as_dict/as_list safely coerce receipt input.
# - count_by/format_counts/format_label_counts summarize repeated fields.
# - bullet_items renders bounded Markdown lists.
# - render_summary/parse_args/main assemble and print the report.
def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Missing receipt: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("Receipt must be a JSON object")
    return payload


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def count_by(items: list[Any], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for item in items:
        if isinstance(item, dict):
            value = item.get(key)
            if isinstance(value, str) and value:
                counter[value] += 1
    return counter


def format_counts(counter: Counter[str], preferred_order: list[str]) -> str:
    parts = []
    for key in preferred_order:
        if counter.get(key):
            parts.append(f"{counter[key]} {key}")
    for key in sorted(counter):
        if key not in preferred_order:
            parts.append(f"{counter[key]} {key}")
    return ", ".join(parts) if parts else "none"


def format_label_counts(counter: Counter[str], preferred_order: list[str]) -> str:
    parts = []
    for key in preferred_order:
        if counter.get(key):
            parts.append(f"{key}: {counter[key]}")
    for key in sorted(counter):
        if key not in preferred_order:
            parts.append(f"{key}: {counter[key]}")
    return ", ".join(parts) if parts else "none"


def bullet_items(items: list[Any], limit: int = 5) -> list[str]:
    values = [str(item) for item in items if str(item).strip()]
    clipped = values[:limit]
    if len(values) > limit:
        clipped.append(f"...and {len(values) - limit} more")
    return clipped


def metric_value(value: Any) -> str:
    return str(value)


def metric_rate(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        rendered = f"{value * 100:.1f}".rstrip("0").rstrip(".")
        return f"{rendered}%"
    return str(value)


def metric_ms(value: Any) -> str:
    return f"{value} ms"


def metric_usd(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"${value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def append_metric(parts: list[str], group: dict[str, Any], field: str, label: str, formatter=metric_value) -> None:
    if field in group:
        parts.append(f"{label} {formatter(group[field])}")


def render_metrics_section(harness_metrics: Any) -> list[str]:
    if not isinstance(harness_metrics, dict):
        return []

    review_outcome = as_dict(harness_metrics.get("review_outcome"))
    effort = as_dict(harness_metrics.get("effort"))
    lines: list[str] = []

    outcome_parts: list[str] = []
    append_metric(outcome_parts, review_outcome, "findings_total", "findings")
    append_metric(outcome_parts, review_outcome, "review_yield_count", "yield")
    append_metric(outcome_parts, review_outcome, "review_yield_rate", "yield rate", metric_rate)
    append_metric(outcome_parts, review_outcome, "findings_false_positive", "false positives")
    append_metric(outcome_parts, review_outcome, "false_positive_rate", "false-positive rate", metric_rate)
    append_metric(outcome_parts, review_outcome, "findings_duplicate", "duplicates")
    append_metric(outcome_parts, review_outcome, "duplicate_rate", "duplicate rate", metric_rate)
    append_metric(outcome_parts, review_outcome, "human_decision_count", "human decisions")
    if outcome_parts:
        lines.append(f"- Review outcome: {'; '.join(outcome_parts)}")

    disposition_parts: list[str] = []
    append_metric(disposition_parts, review_outcome, "findings_open", "open")
    append_metric(disposition_parts, review_outcome, "findings_accepted", "accepted")
    append_metric(disposition_parts, review_outcome, "findings_fixed", "fixed")
    append_metric(disposition_parts, review_outcome, "findings_deferred", "deferred")
    append_metric(disposition_parts, review_outcome, "findings_rejected", "rejected")
    if disposition_parts:
        lines.append(f"- Finding dispositions: {'; '.join(disposition_parts)}")

    effort_parts: list[str] = []
    append_metric(effort_parts, effort, "duration_ms", "duration", metric_ms)
    append_metric(effort_parts, effort, "first_finding_latency_ms", "first finding latency", metric_ms)
    append_metric(effort_parts, effort, "time_to_green_ms", "time to green", metric_ms)
    append_metric(effort_parts, effort, "commands_run_count", "commands")
    if "model_input_tokens" in effort or "model_output_tokens" in effort:
        input_tokens = effort.get("model_input_tokens", "unknown")
        output_tokens = effort.get("model_output_tokens", "unknown")
        effort_parts.append(f"tokens {input_tokens} in / {output_tokens} out")
    append_metric(effort_parts, effort, "estimated_cost_usd", "estimated cost", metric_usd)
    if "human_review_minutes" in effort:
        effort_parts.append(f"human review {effort['human_review_minutes']} min")
    append_metric(effort_parts, effort, "human_interruption_count", "interruptions")
    if effort_parts:
        lines.append(f"- Effort: {'; '.join(effort_parts)}")

    notes = [note for note in (review_outcome.get("notes"), effort.get("notes")) if isinstance(note, str) and note.strip()]
    if notes:
        lines.append(f"- Notes: {'; '.join(notes)}")

    if not lines:
        return []
    return ["", "## Metrics", "", *lines]


def render_summary(receipt: dict[str, Any]) -> str:
    run = as_dict(receipt.get("run"))
    tooling = as_dict(receipt.get("tooling"))
    scope = as_dict(receipt.get("scope"))
    evidence = as_dict(receipt.get("evidence"))
    docs_impact = as_dict(evidence.get("docs_impact"))
    tests = as_dict(evidence.get("tests"))
    disposition = as_dict(receipt.get("disposition"))

    changed_files = as_list(scope.get("changed_files"))
    files_inspected = as_list(evidence.get("files_inspected"))
    commands = as_list(evidence.get("commands"))
    findings = as_list(receipt.get("findings"))
    next_actions = as_list(disposition.get("next_actions"))

    command_counts = count_by(commands, "result")
    finding_priorities = count_by(findings, "priority")
    finding_statuses = count_by(findings, "status")
    priority_summary = format_label_counts(finding_priorities, ["P0", "P1", "P2", "P3"])
    status_summary = format_label_counts(
        finding_statuses,
        ["open", "accepted", "fixed", "deferred", "rejected", "duplicate"],
    )

    lines = [
        "# Session Receipt Summary",
        "",
        f"- Run: `{run.get('id', 'unknown')}`",
        f"- Mode: `{run.get('mode', 'unknown')}`",
        f"- Status: `{run.get('status', 'unknown')}`",
        f"- Tool: `{tooling.get('agent_tool', 'unknown')}`",
        f"- Local only: `{str(tooling.get('local_only', False)).lower()}`",
        f"- Changed files: {len(changed_files)}",
        f"- Files inspected: {len(files_inspected)}",
        f"- Commands: {format_counts(command_counts, ['pass', 'fail', 'blocked', 'not-run'])}",
        f"- Docs impact: `{docs_impact.get('result', 'not-run')}`",
        f"- Tests: {tests.get('result', 'not-run')}",
        f"- Findings: {len(findings)} ({priority_summary}; {status_summary})",
        "",
        "## Disposition",
        "",
        str(disposition.get("summary") or "No disposition summary recorded."),
    ]

    if next_actions:
        lines.extend(["", "## Next Actions", ""])
        lines.extend(f"- {item}" for item in bullet_items(next_actions))

    lines.extend(render_metrics_section(receipt.get("harness_metrics")))

    if findings:
        lines.extend(["", "## Findings", ""])
        for finding in findings[:5]:
            if not isinstance(finding, dict):
                continue
            lines.append(
                f"- `{finding.get('priority', 'P?')}` {finding.get('title', 'Untitled finding')} "
                f"({finding.get('status', 'unknown')}, {finding.get('confidence', 'unknown')} confidence)"
            )
        if len(findings) > 5:
            lines.append(f"- ...and {len(findings) - 5} more")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path, help="Path to a session receipt JSON file")
    parser.add_argument("--output", type=Path, default=None, help="Optional Markdown output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = render_summary(load_json(args.receipt))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(summary, encoding="utf-8")
    else:
        print(summary, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
