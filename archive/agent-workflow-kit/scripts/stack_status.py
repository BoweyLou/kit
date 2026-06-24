#!/usr/bin/env python3
"""Show the local status of the agent workflow source and install-layer stack."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


# Script flow:
# 1. Print source-repo version and git cleanliness.
# 2. Run the self-dogfood boundary check for this source repo.
# 3. If a kit checkout is provided, print its version and git cleanliness.
# 4. Delegate to kit_status.py so installed provenance stays in one place.
#
# Function guide:
# - run_command captures subprocess output without raising.
# - read_text/read_version/gmut summarize local repo metadata.
# - print_repo_status renders one repo's version, branch, and dirty count.
# - print_self_check/print_installed_snapshot run the existing guardrail commands.
ROOT = Path(__file__).resolve().parents[1]


def run_command(args: list[str], cwd: Path, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def read_text(path: Path, default: str = "unknown") -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return default
    return value or default


def read_version(root: Path) -> str:
    return read_text(root / "VERSION")


def git_status(root: Path) -> tuple[str, list[str]]:
    result = run_command(["git", "status", "--short", "--branch"], root)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or "git status failed"
        return f"unknown ({detail})", []
    lines = [line for line in result.stdout.splitlines() if line]
    branch = lines[0] if lines else "unknown"
    return branch, lines[1:]


def print_repo_status(label: str, root: Path) -> None:
    branch, dirty = git_status(root)
    print(label)
    print(f"  path: {root}")
    print(f"  version: {read_version(root)}")
    print(f"  git: {branch}")
    if dirty:
        print(f"  worktree: dirty ({len(dirty)} paths)")
    else:
        print("  worktree: clean")


def print_self_check() -> bool:
    result = run_command(["make", "self-check"], ROOT)
    ok = result.returncode == 0
    print("source-repo boundary check")
    print(f"  self-check: {'pass' if ok else 'fail'}")
    output = result.stdout.strip() if ok else (result.stderr.strip() or result.stdout.strip())
    if output:
        for line in output.splitlines()[:6]:
            print(f"  {line}")
    return ok


def print_installed_snapshot(kit: Path | None) -> bool:
    print("installed guardrail snapshot in this repo")
    if kit is None:
        print("  Set KIT=/path/to/repo-contract-kit to compare against a local kit checkout.")
        result = run_command([sys.executable, "scripts/kit_status.py"], ROOT)
    else:
        result = run_command([sys.executable, "scripts/kit_status.py", "--kit", str(kit)], ROOT)
    ok = result.returncode == 0
    output = result.stdout.strip() if ok else (result.stderr.strip() or result.stdout.strip())
    if output:
        for line in output.splitlines():
            print(f"  {line}")
    return ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", help="Local repo-contract-kit checkout to compare against")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    kit = Path(args.kit).expanduser().resolve() if args.kit else None

    print("Agent workflow stack status")
    print("")
    print_repo_status("agent-workflow-kit source repo", ROOT)
    print("")

    self_check_ok = print_self_check()
    print("")

    kit_ok = True
    if kit is not None:
        if not kit.exists():
            print("repo-contract-kit install layer")
            print(f"  path: {kit}")
            print("  status: missing")
            kit_ok = False
        else:
            print_repo_status("repo-contract-kit install layer", kit)
    else:
        print("repo-contract-kit install layer")
        print("  Set KIT=/path/to/repo-contract-kit to include the companion checkout.")
    print("")

    snapshot_ok = print_installed_snapshot(kit if kit and kit.exists() else None)
    return 0 if self_check_ok and kit_ok and snapshot_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
