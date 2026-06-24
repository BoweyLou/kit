#!/usr/bin/env python3
"""Manage the repository's local SemVer baseline."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


# Script flow:
# 1. Read and validate the current VERSION file.
# 2. Either check the baseline or calculate a SemVer bump.
# 3. Ensure CHANGELOG.md exists before writing release notes.
# 4. Persist VERSION and prepend a dated changelog entry.
#
# Function guide:
# - version_path/changelog_path locate version metadata.
# - read_version/validate_version parse the current SemVer value.
# - bump_version computes major/minor/patch bumps.
# - ensure_changelog/prepend_changelog_entry maintain release notes.
# - parse_args/main expose check and bump commands.
ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def version_path() -> Path:
    return ROOT / "VERSION"


def changelog_path() -> Path:
    return ROOT / "CHANGELOG.md"


def read_version() -> str:
    path = version_path()
    if not path.exists():
        raise SystemExit("Missing VERSION")
    return path.read_text(encoding="utf-8").strip()


def validate_version(value: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise SystemExit(f"Invalid SemVer in VERSION: {value}")
    return tuple(int(part) for part in match.groups()[:3])


def bump_version(value: str, bump: str) -> str:
    major, minor, patch = validate_version(value)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise SystemExit(f"Unknown bump: {bump}")


def ensure_changelog() -> Path:
    path = changelog_path()
    if not path.exists():
        path.write_text("# Changelog\n", encoding="utf-8")
    return path


def prepend_changelog_entry(new_version: str, old_version: str) -> None:
    path = ensure_changelog()
    text = path.read_text(encoding="utf-8")
    heading = (
        f"## {new_version} - {date.today().isoformat()}\n\n"
        f"- TODO: describe changes since {old_version}.\n\n"
    )
    if text.startswith("# Changelog\n\n"):
        text = text.replace("# Changelog\n\n", f"# Changelog\n\n{heading}", 1)
    elif text.startswith("# Changelog\n"):
        text = text.replace("# Changelog\n", f"# Changelog\n\n{heading}", 1)
    else:
        text = f"# Changelog\n\n{heading}{text}"
    path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    subparsers.add_parser("check")
    bump_parser = subparsers.add_parser("bump")
    bump_parser.add_argument("--bump", choices=["patch", "minor", "major"], default="patch")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    current = read_version()
    validate_version(current)

    if args.command == "status":
        print(f"version: {current}")
        return 0

    if args.command == "check":
        changelog = changelog_path()
        if not changelog.exists():
            raise SystemExit("Missing CHANGELOG.md")
        if f"## {current}" not in changelog.read_text(encoding="utf-8"):
            raise SystemExit(f"CHANGELOG.md is missing an entry for VERSION {current}")
        print(f"VERSION is valid SemVer: {current}")
        return 0

    new_version = bump_version(current, args.bump)
    version_path().write_text(new_version + "\n", encoding="utf-8")
    prepend_changelog_entry(new_version, current)
    print(f"Bumped version: {current} -> {new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
