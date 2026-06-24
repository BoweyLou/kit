#!/usr/bin/env python3
"""Validate versioning rules for staged commits."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


# Script flow:
# 1. Read the staged and working-tree paths for the current commit attempt.
# 2. Check VERSION and CHANGELOG formatting when those files are touched.
# 3. Decide whether any staged file changes require a version bump.
# 4. Fail with a clear message unless the required version metadata is staged.
#
# Function guide:
# - run_git centralizes git subprocess calls.
# - staged_paths/working_tree_paths discover the affected files.
# - read_index_or_worktree reads staged content when available, then falls back to disk.
# - validate_baseline checks VERSION/CHANGELOG shape.
# - requires_version_update/main enforce the commit gate.
ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
VERSIONED_FILES = {"VERSION", "CHANGELOG.md"}
VERSION_IMPACT_PREFIXES = (
    ".codex/prompts/",
    ".githooks/",
    "examples/",
    "schemas/",
    "scripts/",
    "workflows/",
)
VERSION_IMPACT_FILES = {
    ".pre-commit-config.yaml",
    ".github/copilot-instructions.md",
    "Makefile",
    "research/agentic-workflow-review/backlog.csv",
    "research/agentic-workflow-review/agent-workflow-kit-backlog.csv",
    "research/agentic-workflow-review/repo-contract-kit-backlog.csv",
}


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def staged_paths() -> list[str]:
    result = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    return [line for line in result.stdout.splitlines() if line]


def working_tree_paths() -> list[str]:
    result = run_git(["diff", "--name-only", "--diff-filter=ACMR"])
    return [line for line in result.stdout.splitlines() if line]


def read_index_or_worktree(path: str, staged: bool) -> str:
    if staged:
        result = run_git(["show", f":{path}"], check=False)
        if result.returncode == 0:
            return result.stdout
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"Missing {path}") from None


def validate_baseline(staged: bool) -> str:
    version = read_index_or_worktree("VERSION", staged).strip()
    if not SEMVER_RE.fullmatch(version):
        raise SystemExit(f"Invalid SemVer in VERSION: {version}")

    changelog = read_index_or_worktree("CHANGELOG.md", staged)
    if f"## {version}" not in changelog:
        raise SystemExit(f"CHANGELOG.md is missing an entry for VERSION {version}")
    return version


def requires_version_update(path: str) -> bool:
    if path in VERSIONED_FILES:
        return False
    if path in VERSION_IMPACT_FILES:
        return True
    return any(path.startswith(prefix) for prefix in VERSION_IMPACT_PREFIXES)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Inspect staged paths and staged file contents")
    parser.add_argument("--working-tree", action="store_true", help="Inspect unstaged working-tree paths")
    args = parser.parse_args(argv)

    staged = args.staged or not args.working_tree
    changed_paths = staged_paths() if staged else working_tree_paths()
    version = validate_baseline(staged=staged)
    impact_paths = [path for path in changed_paths if requires_version_update(path)]

    if not impact_paths:
        print(f"Versioning check passed for VERSION {version}.")
        return 0

    changed_version_files = VERSIONED_FILES.intersection(changed_paths)
    if VERSIONED_FILES <= changed_version_files:
        print(f"Versioning check passed for VERSION {version}.")
        return 0

    if os.environ.get("VERSION_CHECK_ALLOW_UNCHANGED") == "1":
        print(f"Version unchanged for VERSION {version}; override accepted.")
        return 0

    print("Version-impacting files are staged without VERSION and CHANGELOG.md.", file=sys.stderr)
    print("Run `make version-bump BUMP=patch|minor|major`, edit the changelog entry, then stage both files.", file=sys.stderr)
    print("Set VERSION_CHECK_ALLOW_UNCHANGED=1 only for an intentional no-version-change commit.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Impacting files:", file=sys.stderr)
    for path in impact_paths:
        print(f"  - {path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
