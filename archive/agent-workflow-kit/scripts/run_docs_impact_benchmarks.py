#!/usr/bin/env python3
"""Run deterministic docs-impact benchmark fixtures."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any


# Script flow:
# 1. Load the docs-impact benchmark fixture suite.
# 2. Validate case shape before evaluating expected outputs.
# 3. Reuse check_doc_impact's config loading, waiver parsing, evaluation, and
#    JSON payload helpers for each fixture's synthetic changed-file list.
# 4. Compare actual status/categories/missing docs with fixture expectations.
# 5. Emit stable text or JSON and exit non-zero when any expectation is wrong.
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_doc_impact  # noqa: E402


DEFAULT_FIXTURE = ROOT / "research/docs-impact-benchmarks/docs-impact-benchmarks.json"
DEFAULT_CONFIG = ROOT / "doc-contract.json"
CASE_ID_RE = re.compile(r"^DIB-[0-9]{3}$")
ALLOWED_INTENTS = {
    "coverage-positive",
    "false-negative-guard",
    "false-positive-guard",
    "no-docs-needed-waiver",
    "true-positive",
}
REQUIRED_EXPECTED_KEYS = {
    "categories",
    "missing_categories",
    "no_docs_declaration",
    "status",
}
OPTIONAL_EXPECTED_KEYS = {
    "covered_categories",
    "docs_changed",
    "result",
}
VALID_STATUSES = {"fail", "pass"}


class FixtureError(ValueError):
    """Raised when a benchmark fixture has an invalid shape."""


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
    require(isinstance(case_id, str) and bool(CASE_ID_RE.fullmatch(case_id)), "case id must use DIB-000 format", errors)
    require(case_id not in seen_ids, f"duplicate case id: {case_id}", errors)
    seen_ids.add(str(case_id))
    prefix = str(case_id or "<unknown>")

    for field in ["title", "intent", "rationale"]:
        require(isinstance(case.get(field), str) and bool(case[field].strip()), f"{prefix} {field} must be a non-empty string", errors)
    require(case.get("intent") in ALLOWED_INTENTS, f"{prefix} intent is invalid: {case.get('intent')}", errors)
    validate_string_list(case.get("changed_files"), f"{prefix} changed_files", errors)

    no_docs_needed = case.get("no_docs_needed")
    require(no_docs_needed is None or isinstance(no_docs_needed, str), f"{prefix} no_docs_needed must be a string when present", errors)

    expected = case.get("expected")
    require(isinstance(expected, dict), f"{prefix} expected must be an object", errors)
    if not isinstance(expected, dict):
        return

    for key in sorted(REQUIRED_EXPECTED_KEYS):
        require(key in expected, f"{prefix} expected.{key} is required", errors)
    unknown = set(expected) - REQUIRED_EXPECTED_KEYS - OPTIONAL_EXPECTED_KEYS
    require(not unknown, f"{prefix} expected has unknown keys: {', '.join(sorted(unknown))}", errors)
    require(expected.get("status") in VALID_STATUSES, f"{prefix} expected.status must be pass or fail", errors)
    require(isinstance(expected.get("no_docs_declaration"), bool), f"{prefix} expected.no_docs_declaration must be boolean", errors)
    for key in ["categories", "covered_categories", "docs_changed", "missing_categories"]:
        if key in expected:
            validate_string_list(expected.get(key), f"{prefix} expected.{key}", errors)
    if "result" in expected:
        require(isinstance(expected["result"], str) and bool(expected["result"].strip()), f"{prefix} expected.result must be a string", errors)


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


@contextmanager
def deterministic_doc_env():
    keys = ["DOC_CONTRACT_NO_DOCS_NEEDED", "DOC_CONTRACT_PR_BODY"]
    saved = {key: os.environ.get(key) for key in keys}
    for key in keys:
        os.environ.pop(key, None)
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def actual_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    categories = payload.get("categories", [])
    return {
        "status": payload.get("status"),
        "result": payload.get("result"),
        "categories": sorted(category["category"] for category in categories),
        "missing_categories": sorted(payload.get("missing_categories", [])),
        "docs_changed": sorted(payload.get("docs_changed", [])),
        "covered_categories": sorted(category["category"] for category in categories if category.get("covered")),
        "no_docs_declaration": payload.get("no_docs_declaration"),
    }


def format_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def compare_expected(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    keys = sorted(REQUIRED_EXPECTED_KEYS | (set(expected) & OPTIONAL_EXPECTED_KEYS))
    for key in keys:
        expected_value = expected[key]
        actual_value = actual.get(key)
        if isinstance(expected_value, list):
            expected_value = sorted(expected_value)
        if expected_value != actual_value:
            failures.append(f"expected {key} {format_value(expected_value)}, got {format_value(actual_value)}")
    return failures


def run_case(case: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    with deterministic_doc_env():
        no_docs_declaration = check_doc_impact.has_no_docs_declaration(case.get("no_docs_needed"), config)
    result = check_doc_impact.evaluate(case["changed_files"], config, no_docs_declaration)
    payload = check_doc_impact.json_payload(result, config)
    actual = actual_from_payload(payload)
    expected = case["expected"]
    failures = compare_expected(expected, actual)
    return {
        "case_id": case["id"],
        "title": case["title"],
        "intent": case["intent"],
        "status": "fail" if failures else "pass",
        "failures": failures,
        "expected": expected,
        "actual": actual,
    }


def run_suite(fixture_path: Path, config_path: Path) -> dict[str, Any]:
    suite = load_suite(fixture_path)
    config = check_doc_impact.load_config(str(config_path))
    cases = suite["cases"]
    results = [run_case(case, config) for case in cases]
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
        actual = result["actual"]
        expected = result["expected"]
        categories = ", ".join(actual["categories"]) if actual["categories"] else "none"
        print(
            f"{result['status'].upper()} {result['case_id']}: {result['title']} "
            f"-> expected docs-impact {expected['status']}, actual {actual['status']} [{categories}]"
        )
        for failure in result["failures"]:
            print(f"  - {failure}")
    passing = report["case_count"] - report["failure_count"]
    print(f"Docs-impact benchmarks {report['status']} ({passing}/{report['case_count']} passing).")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE, help="Fixture suite path")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="doc-contract config path")
    parser.add_argument("--json", action="store_true", help="Print machine-readable benchmark results")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        report = run_suite(args.fixture, args.config)
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
