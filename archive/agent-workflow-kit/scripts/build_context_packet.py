#!/usr/bin/env python3
"""Build a deterministic diff-to-context packet for local agent review."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


# Script flow:
# 1. Ask git for the changed files that should be reviewed.
# 2. Read a bounded amount of nearby text from relevant repo files.
# 3. Classify each item into the packet sections an agent should inspect.
# 4. Render either JSON or Markdown so downstream tools get stable context.
#
# Function guide:
# - git/git_lines wrap git subprocess calls.
# - changed_files/repo_files find candidate paths.
# - is_text_candidate/read_text/terms_for_file/matches_terms decide what text is safe and useful to include.
# - add_item/classify/build_packet assemble the structured review payload.
# - render_markdown/parse_args/main handle CLI output.
TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".csv",
    ".env",
    ".go",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".vue",
    ".yaml",
    ".yml",
}
RUNTIME_CONFIG_NAMES = {
    ".github/workflows",
    "Dockerfile",
    "Makefile",
    "docker-compose.yml",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
}
MAX_FILE_SIZE = 200_000
MAX_ITEMS = 20


def git(root: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=check,
    )


def git_lines(root: Path, args: list[str]) -> list[str]:
    result = git(root, args)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def changed_files(root: Path) -> list[str]:
    files: list[str] = []
    for args in (["diff", "--name-only", "--cached"], ["diff", "--name-only"]):
        files.extend(git_lines(root, args))
    if not files:
        files.extend(git_lines(root, ["diff", "--name-only", "HEAD"]))
    return sorted(set(files))


def repo_files(root: Path) -> list[str]:
    return sorted(set(git_lines(root, ["ls-files"]) + git_lines(root, ["ls-files", "--others", "--exclude-standard"])))


def is_text_candidate(path: str) -> bool:
    rel = Path(path)
    if any(part in {".git", "__pycache__", "node_modules", ".agent-workflows"} for part in rel.parts):
        return False
    if rel.name.startswith(".") and rel.suffix == "":
        return rel.name in {".env", ".gitignore"}
    return rel.suffix in TEXT_SUFFIXES or rel.name in RUNTIME_CONFIG_NAMES


def read_text(root: Path, path: str) -> str:
    full = root / path
    try:
        if full.stat().st_size > MAX_FILE_SIZE:
            return ""
        return full.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return ""


def terms_for_file(root: Path, path: str) -> set[str]:
    rel = Path(path)
    terms = {path.lower(), rel.name.lower(), rel.stem.lower()}
    if rel.suffix == ".py":
        terms.add(".".join(rel.with_suffix("").parts).lower())
    text = read_text(root, path)
    for pattern in (
        r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"^\s*export\s+(?:function|class|const)\s+([A-Za-z_][A-Za-z0-9_]*)",
        r"^\s*(?:function|const|class)\s+([A-Za-z_][A-Za-z0-9_]*)",
    ):
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            terms.add(match.group(1).lower())
    return {term for term in terms if len(term) >= 3}


def matches_terms(text: str, terms: set[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def add_item(bucket: list[dict[str, str]], seen: set[str], path: str, reason: str) -> None:
    if path in seen or len(bucket) >= MAX_ITEMS:
        return
    seen.add(path)
    bucket.append({"path": path, "reason": reason})


def classify(root: Path, paths: list[str]) -> dict[str, Any]:
    changed = set(paths)
    terms: set[str] = set()
    for path in paths:
        terms.update(terms_for_file(root, path))

    buckets: dict[str, list[dict[str, str]]] = {
        "likely_callers": [],
        "likely_tests": [],
        "related_docs": [],
        "adrs": [],
        "runtime_configs": [],
        "scripts": [],
    }
    seen = {key: set() for key in buckets}

    for path in repo_files(root):
        if path in changed or not is_text_candidate(path):
            continue
        rel = Path(path)
        text = read_text(root, path)
        if not text:
            continue
        matched = matches_terms(text, terms)
        lowered = path.lower()

        if rel.parts[:2] == ("docs", "adr"):
            if matched or len(buckets["adrs"]) < 3:
                add_item(buckets["adrs"], seen["adrs"], path, "ADR context for changed terms or latest design constraints")
            continue
        if lowered.startswith("tests/") or "/tests/" in lowered or rel.name.startswith("test_"):
            if matched:
                add_item(buckets["likely_tests"], seen["likely_tests"], path, "test file references a changed symbol or path")
            continue
        if lowered.startswith("docs/") or rel.suffix == ".md":
            if matched:
                add_item(buckets["related_docs"], seen["related_docs"], path, "documentation references a changed symbol or path")
            continue
        if lowered.startswith("scripts/"):
            if matched:
                add_item(buckets["scripts"], seen["scripts"], path, "script references a changed symbol or path")
            continue
        if rel.name in RUNTIME_CONFIG_NAMES or any(lowered.startswith(prefix.lower()) for prefix in RUNTIME_CONFIG_NAMES):
            add_item(buckets["runtime_configs"], seen["runtime_configs"], path, "runtime or build configuration")
            continue
        if matched:
            add_item(buckets["likely_callers"], seen["likely_callers"], path, "code references a changed symbol or path")

    return buckets


def build_packet(root: Path) -> dict[str, Any]:
    paths = changed_files(root)
    context = classify(root, paths)
    return {
        "schema_version": 1,
        "repo_root": str(root),
        "changed_files": paths,
        **context,
        "guidance": [
            "Inspect likely_callers and likely_tests before making behavior claims.",
            "Inspect related_docs and adrs before changing public behavior or documentation.",
            "Inspect runtime_configs and scripts before changing workflow, build, or operations behavior.",
        ],
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines = ["# Diff Context Packet", ""]
    lines.append("## Changed Files")
    lines.extend(f"- `{path}`" for path in packet["changed_files"] or ["none"])
    for title, key in (
        ("Likely Callers", "likely_callers"),
        ("Likely Tests", "likely_tests"),
        ("Related Docs", "related_docs"),
        ("ADRs", "adrs"),
        ("Runtime Configs", "runtime_configs"),
        ("Scripts", "scripts"),
    ):
        lines.extend(["", f"## {title}"])
        items = packet[key]
        if not items:
            lines.append("- none found")
            continue
        lines.extend(f"- `{item['path']}` - {item['reason']}" for item in items)
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    packet = build_packet(root)
    output = json.dumps(packet, indent=2, sort_keys=True) + "\n" if args.json else render_markdown(packet)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
