#!/usr/bin/env python3
"""Split the ecosystem backlog into repo-owned backlog views."""

from __future__ import annotations

import argparse
import csv
import sys
from io import StringIO
from pathlib import Path


# Script flow:
# 1. Read the shared ecosystem backlog CSV.
# 2. Group rows by the repo owner declared in the repo column.
# 3. Render each repo-owned view with the original column order.
# 4. Either check that outputs are current or write the split files.
#
# Function guide:
# - read_rows/render_csv handle CSV parsing and stable output.
# - split_backlog builds the repo-keyed CSV payloads.
# - parse_args/main implement check and write modes.
ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "research" / "agentic-workflow-review" / "backlog.csv"
OUTPUTS = {
    "agent-workflow-kit": ROOT / "research" / "agentic-workflow-review" / "agent-workflow-kit-backlog.csv",
    "repo-contract-kit": ROOT / "research" / "agentic-workflow-review" / "repo-contract-kit-backlog.csv",
}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no CSV header")
        rows = list(reader)
    return reader.fieldnames, rows


def render_csv(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def split_backlog(backlog: Path) -> dict[str, str]:
    fieldnames, rows = read_rows(backlog)
    if "repo" not in fieldnames:
        raise ValueError(f"{backlog} must include a repo column")

    known_repos = set(OUTPUTS)
    actual_repos = {row["repo"] for row in rows}
    unknown = sorted(actual_repos - known_repos)
    if unknown:
        raise ValueError(f"unknown repo value(s) in {backlog}: {', '.join(unknown)}")

    return {
        repo: render_csv(fieldnames, [row for row in rows if row["repo"] == repo])
        for repo in OUTPUTS
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when split backlog files are out of date")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or [])
    try:
        outputs = split_backlog(BACKLOG)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    stale: list[Path] = []
    for repo, content in outputs.items():
        path = OUTPUTS[repo]
        if args.check:
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            if existing != content:
                stale.append(path)
        else:
            path.write_text(content, encoding="utf-8")
            print(f"{repo}: wrote {path.relative_to(ROOT)}")

    if stale:
        print("Split backlog files are out of date:", file=sys.stderr)
        for path in stale:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python3 scripts/split_backlog_by_repo.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
