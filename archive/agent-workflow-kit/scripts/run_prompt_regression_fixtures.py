#!/usr/bin/env python3
"""Run deterministic prompt-output regression fixtures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# Script flow:
# 1. Load the prompt regression fixture suite.
# 2. Validate fixture shape before evaluating expected payload outcomes.
# 3. Reuse agent_review_run persona and synthesis payload validators.
# 4. Apply narrow deterministic quality checks for evidence, false-positive
#    notes, low-signal nits, source-persona preservation, and duplicate
#    synthesis findings.
# 5. Compare actual pass/fail outcomes with fixture expectations.
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from agent_review_run import validate_persona_payload, validate_synthesis_payload  # noqa: E402


DEFAULT_FIXTURE = ROOT / "research/prompt-regression-fixtures/prompt-regression-fixtures.json"
CASE_ID_RE = re.compile(r"^PRF-[0-9]{3}$")
FILE_PATH_RE = re.compile(r"(?:[\w./-]+\.(?:py|md|json|csv|ya?ml|toml|sh|txt)|Makefile)(?::\d+)?")
COMMAND_RE = re.compile(r"\b(?:make|python3?|pytest|unittest|git|rg)\b")
VALID_PAYLOAD_TYPES = {"persona", "synthesis"}
VALID_EXPECTED_STATUSES = {"pass", "fail"}
ALLOWED_INTENTS = {
    "comment-docstring-drift-labels",
    "duplicate-synthesis-findings",
    "low-signal-nit-finding",
    "malformed-persona-payload",
    "synthesis-duplicate-merged",
    "valid-persona-finding",
}
VALID_DISPOSITIONS = {"open", "accepted", "rejected", "fixed", "deferred", "duplicate"}
LOW_SIGNAL_TERMS = {"cosmetic", "formatting", "nit", "style", "typo", "whitespace", "wording"}
RISK_TERMS = {
    "api",
    "behavior",
    "broken",
    "contract",
    "correctness",
    "delivery",
    "documentation",
    "drift",
    "maintainability",
    "privacy",
    "public",
    "regression",
    "risk",
    "runtime",
    "security",
    "test",
    "validation",
}
PASSIVE_NIT_STATUSES = {"rejected", "deferred", "duplicate"}
INACTIVE_DUPLICATE_STATUSES = {"duplicate", "rejected"}
COMMENT_DRIFT_BASE_LABELS = {"comment-drift", "docstring-drift"}
COMMENT_DRIFT_DETAIL_LABELS = {"stale-comment", "misleading-comment", "stale-docstring"}
COMMENT_DRIFT_FALSE_POSITIVE_LABELS = {
    "generated-or-vendored-comment",
    "intentionally-stable-comment",
    "low-confidence-drift",
}
COMMENT_DRIFT_LABELS = COMMENT_DRIFT_BASE_LABELS | COMMENT_DRIFT_DETAIL_LABELS | COMMENT_DRIFT_FALSE_POSITIVE_LABELS
COMMENT_DRIFT_PHRASES = (
    "comment-drift",
    "docstring-drift",
    "comment drift",
    "docstring drift",
    "stale comment",
    "misleading comment",
    "stale docstring",
)
COMMENT_DRIFT_SOURCE_TERMS = ("comment", "docstring")
COMMENT_DRIFT_TRUTH_TERMS = (
    "adr",
    "current",
    "docs",
    "implementation",
    "runtime",
    "source",
    "test",
)
COMMENT_DRIFT_FALSE_POSITIVE_TERMS = (
    "example",
    "framework",
    "generated",
    "historical",
    "low confidence",
    "low-confidence",
    "speculative",
    "stable",
    "vendor",
    "vendored",
)


class FixtureError(ValueError):
    """Raised when a prompt regression fixture has an invalid shape."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FixtureError(f"missing fixture file: {path}") from None
    except json.JSONDecodeError as exc:
        raise FixtureError(f"invalid JSON in {path}: {exc}") from exc


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_string_list(value: Any, field: str, errors: list[str]) -> None:
    require(isinstance(value, list), f"{field} must be a list", errors)
    if isinstance(value, list):
        for item in value:
            require(isinstance(item, str) and bool(item.strip()), f"{field} entries must be non-empty strings", errors)


def validate_case(case: Any, seen_ids: set[str], errors: list[str]) -> None:
    if not isinstance(case, dict):
        errors.append("case entries must be objects")
        return

    case_id = case.get("id")
    require(isinstance(case_id, str) and bool(CASE_ID_RE.fullmatch(case_id)), "case id must use PRF-000 format", errors)
    require(case_id not in seen_ids, f"duplicate case id: {case_id}", errors)
    seen_ids.add(str(case_id))
    prefix = str(case_id or "<unknown>")

    for field in ["title", "intent", "payload_type", "rationale"]:
        require(isinstance(case.get(field), str) and bool(case[field].strip()), f"{prefix} {field} must be a non-empty string", errors)
    require(case.get("intent") in ALLOWED_INTENTS, f"{prefix} intent is invalid: {case.get('intent')}", errors)
    require(case.get("payload_type") in VALID_PAYLOAD_TYPES, f"{prefix} payload_type is invalid: {case.get('payload_type')}", errors)
    require(isinstance(case.get("payload"), dict), f"{prefix} payload must be an object", errors)
    if case.get("payload_type") == "persona":
        require(isinstance(case.get("persona_id"), str) and bool(case["persona_id"].strip()), f"{prefix} persona_id is required", errors)

    expected = case.get("expected")
    require(isinstance(expected, dict), f"{prefix} expected must be an object", errors)
    if not isinstance(expected, dict):
        return
    require(expected.get("status") in VALID_EXPECTED_STATUSES, f"{prefix} expected.status must be pass or fail", errors)
    validate_string_list(expected.get("reason_contains"), f"{prefix} expected.reason_contains", errors)
    if expected.get("status") == "fail":
        require(bool(expected.get("reason_contains")), f"{prefix} failing fixtures must name expected validation or quality reasons", errors)


def load_suite(path: Path) -> dict[str, Any]:
    suite = load_json(path)
    errors: list[str] = []
    require(isinstance(suite, dict), "fixture suite must be an object", errors)
    if isinstance(suite, dict):
        require(suite.get("schema_version") == 1, "fixture suite schema_version must be 1", errors)
        suite_meta = suite.get("suite")
        require(isinstance(suite_meta, dict), "fixture suite metadata is required", errors)
        if isinstance(suite_meta, dict):
            for field in ["name", "purpose", "source_backlog"]:
                require(isinstance(suite_meta.get(field), str) and bool(suite_meta[field].strip()), f"suite.{field} must be a non-empty string", errors)
        cases = suite.get("cases")
        require(isinstance(cases, list) and bool(cases), "fixture suite needs a non-empty cases list", errors)
        seen_ids: set[str] = set()
        if isinstance(cases, list):
            for case in cases:
                validate_case(case, seen_ids, errors)
    if errors:
        raise FixtureError("\n".join(errors))
    return suite


def has_concrete_evidence(value: str) -> bool:
    return bool(FILE_PATH_RE.search(value) or COMMAND_RE.search(value))


def normalized_words(value: str) -> set[str]:
    return {word for word in re.sub(r"[^a-z0-9]+", " ", value.lower()).split() if word}


def finding_text(finding: dict[str, Any]) -> str:
    evidence = finding.get("evidence")
    evidence_text = " ".join(item for item in evidence if isinstance(item, str)) if isinstance(evidence, list) else ""
    labels = finding.get("labels")
    labels_text = " ".join(item for item in labels if isinstance(item, str)) if isinstance(labels, list) else ""
    return " ".join(
        str(finding.get(field) or "")
        for field in ["title", "area", "recommendation", "false_positive_notes"]
    ) + " " + evidence_text + " " + labels_text


def contains_any_term(text: str, terms: set[str]) -> bool:
    words = normalized_words(text)
    return any(term in words or term in text.lower() for term in terms)


def normalized_labels(finding: dict[str, Any], index: int, errors: list[str]) -> list[str]:
    raw_labels = finding.get("labels")
    if raw_labels is None:
        return []
    if not isinstance(raw_labels, list):
        errors.append(f"finding {index} labels must be a list when present")
        return []
    labels: list[str] = []
    for label in raw_labels:
        if not isinstance(label, str) or not label.strip():
            errors.append(f"finding {index} labels entries must be non-empty strings")
            continue
        labels.append(label.strip())
    return labels


def is_comment_docstring_drift_candidate(text: str, labels: list[str]) -> bool:
    lowered = text.lower()
    return bool(set(labels) & COMMENT_DRIFT_LABELS) or any(phrase in lowered for phrase in COMMENT_DRIFT_PHRASES)


def validate_comment_docstring_drift_finding(
    finding: dict[str, Any],
    index: int,
    labels: list[str],
    errors: list[str],
) -> None:
    if not labels:
        errors.append(f"finding {index} comment/docstring drift must include advisory drift labels")
        return

    label_set = set(labels)
    if not (label_set & COMMENT_DRIFT_BASE_LABELS):
        errors.append(f"finding {index} comment/docstring drift must include comment-drift or docstring-drift label")
    if not (label_set & (COMMENT_DRIFT_DETAIL_LABELS | COMMENT_DRIFT_FALSE_POSITIVE_LABELS)):
        errors.append(f"finding {index} comment/docstring drift must include a specific drift or false-positive label")

    evidence = finding.get("evidence")
    evidence_items = [item for item in evidence if isinstance(item, str)] if isinstance(evidence, list) else []
    source_side = any(any(term in item.lower() for term in COMMENT_DRIFT_SOURCE_TERMS) for item in evidence_items)
    truth_side = any(any(term in item.lower() for term in COMMENT_DRIFT_TRUTH_TERMS) for item in evidence_items)
    if len(evidence_items) < 2 or not source_side or not truth_side:
        errors.append(f"finding {index} comment/docstring drift must include two-sided evidence")

    false_positive_notes = str(finding.get("false_positive_notes") or "").lower()
    if not any(term in false_positive_notes for term in COMMENT_DRIFT_FALSE_POSITIVE_TERMS):
        errors.append(f"finding {index} comment/docstring drift must name a false-positive category")


def validate_persona_quality(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        return errors

    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            continue
        status = finding.get("status")
        if status not in VALID_DISPOSITIONS:
            errors.append(f"finding {index} status is invalid: {status}")
        false_positive_notes = finding.get("false_positive_notes")
        if not isinstance(false_positive_notes, str) or not false_positive_notes.strip():
            errors.append(f"finding {index} must include false_positive_notes")
        labels = normalized_labels(finding, index, errors)
        evidence = finding.get("evidence")
        if isinstance(evidence, list) and evidence and not any(isinstance(item, str) and has_concrete_evidence(item) for item in evidence):
            errors.append(f"finding {index} evidence must cite a file path, line, or command")
        text = finding_text(finding)
        if is_comment_docstring_drift_candidate(text, labels):
            validate_comment_docstring_drift_finding(finding, index, labels, errors)
        if contains_any_term(text, LOW_SIGNAL_TERMS) and not contains_any_term(text, RISK_TERMS) and status not in PASSIVE_NIT_STATUSES:
            errors.append(
                f"finding {index} low-signal nit must be rejected, deferred, or marked duplicate unless it includes concrete risk"
            )
    return errors


def duplicate_key(finding: dict[str, Any]) -> str:
    file_value = str(finding.get("file") or "")
    line_value = str(finding.get("line") or "")
    evidence = finding.get("evidence")
    evidence_key = ""
    if isinstance(evidence, list):
        evidence_key = "|".join(sorted(" ".join(normalized_words(item)) for item in evidence if isinstance(item, str)))
    title_key = " ".join(normalized_words(str(finding.get("title") or "")))
    return f"{file_value}:{line_value}:{evidence_key or title_key}"


def validate_synthesis_quality(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        return errors

    active_keys: dict[str, int] = {}
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"finding {index} is not an object")
            continue

        status = finding.get("status")
        if status not in VALID_DISPOSITIONS:
            errors.append(f"finding {index} status is invalid: {status}")
        source_personas = finding.get("source_personas")
        if not isinstance(source_personas, list) or not source_personas or not all(isinstance(item, str) and item.strip() for item in source_personas):
            errors.append(f"finding {index} must preserve non-empty source_personas")
        false_positive_notes = finding.get("false_positive_notes")
        if not isinstance(false_positive_notes, str) or not false_positive_notes.strip():
            errors.append(f"finding {index} must include false_positive_notes")
        labels = normalized_labels(finding, index, errors)
        evidence = finding.get("evidence")
        if isinstance(evidence, list) and evidence and not any(isinstance(item, str) and has_concrete_evidence(item) for item in evidence):
            errors.append(f"finding {index} evidence must cite a file path, line, or command")
        text = finding_text(finding)
        if is_comment_docstring_drift_candidate(text, labels):
            validate_comment_docstring_drift_finding(finding, index, labels, errors)

        related_ids = finding.get("related_finding_ids")
        if status == "duplicate" and not related_ids:
            errors.append(f"finding {index} duplicate status must include related_finding_ids")
        if isinstance(related_ids, list) and len(related_ids) > 1 and isinstance(source_personas, list) and len(source_personas) < 2:
            errors.append(f"finding {index} merged related findings must preserve multiple source_personas")

        key = duplicate_key(finding)
        if status not in INACTIVE_DUPLICATE_STATUSES and key:
            previous = active_keys.get(key)
            if previous:
                errors.append(f"finding {index} duplicates finding {previous} without duplicate disposition or merge")
            else:
                active_keys[key] = index
    return errors


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    payload = case["payload"]
    validation_errors: list[str]
    quality_errors: list[str]
    if case["payload_type"] == "persona":
        normalized, validation_errors = validate_persona_payload(payload, case["persona_id"])
        quality_errors = validate_persona_quality(normalized)
    else:
        normalized, validation_errors = validate_synthesis_payload(payload)
        quality_errors = validate_synthesis_quality(normalized)

    reasons = [f"validation: {error}" for error in validation_errors] + [f"quality: {error}" for error in quality_errors]
    actual = {
        "status": "fail" if reasons else "pass",
        "reason_count": len(reasons),
        "reasons": reasons,
    }
    expected = case["expected"]
    failures: list[str] = []
    if actual["status"] != expected["status"]:
        failures.append(f"expected actual status {expected['status']}, got {actual['status']}")
    for expected_reason in expected["reason_contains"]:
        if not any(expected_reason in reason for reason in reasons):
            failures.append(f"expected reason containing {json.dumps(expected_reason)}, got {json.dumps(reasons, sort_keys=True)}")

    return {
        "case_id": case["id"],
        "title": case["title"],
        "intent": case["intent"],
        "payload_type": case["payload_type"],
        "status": "fail" if failures else "pass",
        "failures": failures,
        "expected": expected,
        "actual": actual,
    }


def run_suite(fixture_path: Path) -> dict[str, Any]:
    suite = load_suite(fixture_path)
    cases = suite["cases"]
    results = [evaluate_case(case) for case in cases]
    failures = [result for result in results if result["status"] == "fail"]
    return {
        "schema_version": 1,
        "suite": suite["suite"]["name"],
        "source_backlog": suite["suite"]["source_backlog"],
        "status": "fail" if failures else "pass",
        "case_count": len(results),
        "failure_count": len(failures),
        "results": results,
    }


def render_text(report: dict[str, Any]) -> None:
    for result in report["results"]:
        print(
            f"{result['status'].upper()} {result['case_id']}: {result['title']} "
            f"-> expected actual {result['expected']['status']}, actual {result['actual']['status']}"
        )
        for reason in result["actual"]["reasons"]:
            print(f"  actual: {reason}")
        for failure in result["failures"]:
            print(f"  - {failure}")
    passing = report["case_count"] - report["failure_count"]
    print(f"Prompt regression fixtures {report['status']} ({passing}/{report['case_count']} passing).")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE, help="Fixture suite path")
    parser.add_argument("--json", action="store_true", help="Print machine-readable fixture results")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        report = run_suite(args.fixture)
    except FixtureError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        render_text(report)
    return 1 if report["failure_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
