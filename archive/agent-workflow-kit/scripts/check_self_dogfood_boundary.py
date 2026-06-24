#!/usr/bin/env python3
"""Check that dogfooding does not reopen this legacy source repo as live source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from export_workflow_adapters import (  # noqa: E402
    adapters_from_manifest,
    compare_mirror,
    load_manifest,
    source_root,
)


# These files are intentionally localized after the repo-contract-kit install.
# If this set changes, update ADR 0002 and the tests in the same change.
INTENTIONAL_LOCALIZED_MANAGED_FILES = {
    ".agent-workflows/README.md",
    ".agent-workflows/repo-review.md",
    "AGENTS.md",
    "doc-contract.json",
    "docs/ops/agent-workflow.md",
    "scripts/verify_agent_receipt.py",
}

NORMAL_VALIDATION_TARGETS = {
    "validate",
    "agent-verify",
    "self-check",
}

AUTOMATION_FILES = {
    ".githooks/pre-commit",
    ".pre-commit-config.yaml",
}


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    ok: bool
    message: str


def pass_result(check_id: str, message: str) -> CheckResult:
    return CheckResult(check_id, True, message)


def fail_result(check_id: str, message: str) -> CheckResult:
    return CheckResult(check_id, False, message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Missing required JSON file: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_prompt_source_manifest(root: Path) -> CheckResult:
    manifest = load_manifest(root)
    source = manifest.get("source_root")
    generated = {
        adapter.get("id"): adapter
        for adapter in manifest.get("generated_adapters", [])
        if isinstance(adapter, dict)
    }
    codex = generated.get("codex")

    if source != "workflows/prompts":
        return fail_result(
            "prompt-source-manifest",
            f"workflows/manifest.json source_root is {source!r}; expected 'workflows/prompts'",
        )
    if not codex:
        return fail_result("prompt-source-manifest", "workflows/manifest.json is missing the codex adapter")
    if codex.get("target_root") != ".codex/prompts" or codex.get("strategy") != "mirror":
        return fail_result(
            "prompt-source-manifest",
            "codex adapter must mirror workflows/prompts into .codex/prompts",
        )
    if not source_root(root, manifest).is_dir():
        return fail_result("prompt-source-manifest", "legacy workflows/prompts directory is missing")
    return pass_result(
        "prompt-source-manifest",
        "workflows/prompts remains the legacy mirror source for this checkout",
    )


def check_codex_adapter_sync(root: Path) -> CheckResult:
    manifest = load_manifest(root)
    source = source_root(root, manifest)
    generated = adapters_from_manifest(root, manifest)
    adapter = generated.get("codex")
    if not adapter:
        return fail_result("codex-adapter-sync", "codex generated adapter is missing from manifest")

    problems = compare_mirror(source, adapter.target_root)
    if problems:
        return fail_result(
            "codex-adapter-sync",
            "generated Codex adapter is out of sync; run make prompt-adapters-export: "
            + "; ".join(problems[:5]),
        )
    return pass_result("codex-adapter-sync", ".codex/prompts mirrors workflows/prompts")


def check_codex_adapter_target_owned(root: Path) -> CheckResult:
    manifest = read_json(root / ".doc-contract-kit" / "manifest.json")
    codex_entries = [
        item
        for item in manifest.get("files", [])
        if isinstance(item, dict) and str(item.get("path", "")).startswith(".codex/prompts/")
    ]
    if not codex_entries:
        return fail_result(
            "codex-adapter-ownership",
            ".doc-contract-kit/manifest.json does not record .codex/prompts ownership",
        )

    violations = [
        item["path"]
        for item in codex_entries
        if item.get("managed") or item.get("owner") != "target"
    ]
    if violations:
        return fail_result(
            "codex-adapter-ownership",
            ".codex/prompts must remain target-owned in this source repo: "
            + ", ".join(sorted(violations)[:8]),
        )
    return pass_result("codex-adapter-ownership", ".codex/prompts is target-owned, not kit-managed")


def managed_manifest_drift(root: Path) -> tuple[set[str], list[str]]:
    manifest = read_json(root / ".doc-contract-kit" / "manifest.json")
    modified: set[str] = set()
    missing: list[str] = []
    for item in manifest.get("files", []):
        if not isinstance(item, dict) or not item.get("managed"):
            continue
        rel_path = item.get("path")
        expected = item.get("installed_sha256")
        if not rel_path or not expected:
            continue
        path = root / rel_path
        if not path.exists():
            missing.append(rel_path)
        elif sha256_path(path) != expected:
            modified.add(rel_path)
    return modified, missing


def check_intentional_managed_overrides(root: Path) -> CheckResult:
    modified, missing = managed_manifest_drift(root)
    expected = INTENTIONAL_LOCALIZED_MANAGED_FILES
    extra = modified - expected
    absent = expected - modified

    problems: list[str] = []
    if missing:
        problems.append("missing managed files: " + ", ".join(sorted(missing)))
    if extra:
        problems.append("unexpected localized managed files: " + ", ".join(sorted(extra)))
    if absent:
        problems.append("expected localized files no longer differ from kit install: " + ", ".join(sorted(absent)))
    if problems:
        return fail_result("managed-local-overrides", "; ".join(problems))
    return pass_result(
        "managed-local-overrides",
        "only intentional source-repo localizations differ from the kit manifest",
    )


def make_target_block(makefile_text: str, target: str) -> str:
    target_re = re.compile(rf"^{re.escape(target)}\s*:(?:\s.*)?$", re.MULTILINE)
    next_target_re = re.compile(r"^[A-Za-z0-9_.-]+\s*:(?![=])", re.MULTILINE)
    match = target_re.search(makefile_text)
    if not match:
        return ""
    next_match = next_target_re.search(makefile_text, match.end())
    end = next_match.start() if next_match else len(makefile_text)
    return makefile_text[match.start() : end]


def check_kit_update_not_automatic(root: Path) -> CheckResult:
    makefile = (root / "Makefile").read_text(encoding="utf-8")
    offenders = []
    for target in sorted(NORMAL_VALIDATION_TARGETS):
        block = make_target_block(makefile, target)
        if not block:
            offenders.append(f"missing Make target: {target}")
        elif "kit-update" in block:
            offenders.append(f"Make target {target} references kit-update")

    for rel_path in sorted(AUTOMATION_FILES):
        path = root / rel_path
        if path.exists() and "kit-update" in path.read_text(encoding="utf-8"):
            offenders.append(f"{rel_path} references kit-update")

    if offenders:
        return fail_result("kit-update-not-automatic", "; ".join(offenders))
    return pass_result("kit-update-not-automatic", "kit-update is explicit and not part of normal validation")


def check_source_guidance(root: Path) -> CheckResult:
    required_files = {
        "AGENTS.md": [
            "repo-contract-kit",
            "workflows",
            "workflows/prompts/",
            "legacy",
            "prompt-adapters-export",
            "kit-update",
        ],
        ".agent-workflows/README.md": [
            "repo-contract-kit",
            "workflows",
            "workflows/prompts/",
            ".codex/prompts/",
            "legacy",
            "repo-contract-kit",
        ],
        "docs/adr/0002-self-dogfood-boundary.md": [
            "repo-contract-kit",
            "workflows",
            "workflows/prompts/",
            "legacy",
            "repo-contract-kit",
            "kit-update",
        ],
    }
    missing = []
    for rel_path, needles in required_files.items():
        path = root / rel_path
        if not path.exists():
            missing.append(f"{rel_path} is missing")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel_path} does not mention {needle}")

    if missing:
        return fail_result("source-guidance", "; ".join(missing))
    return pass_result(
        "source-guidance",
        "legacy source-route boundary is documented in agent guidance and ADR 0002",
    )


def run_checks(root: Path) -> list[CheckResult]:
    root = root.resolve()
    return [
        check_prompt_source_manifest(root),
        check_codex_adapter_sync(root),
        check_codex_adapter_target_owned(root),
        check_intentional_managed_overrides(root),
        check_kit_update_not_automatic(root),
        check_source_guidance(root),
    ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    results = run_checks(args.root)
    failed = [result for result in results if not result.ok]
    for result in results:
        prefix = "PASS" if result.ok else "FAIL"
        print(f"{prefix} {result.check_id}: {result.message}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
