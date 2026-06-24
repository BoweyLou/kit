#!/usr/bin/env python3
"""Check or export in-repo workflow source into installed target templates."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_SOURCE = ROOT / "workflows" / "prompts"
SCHEMA_SOURCE = ROOT / "workflows" / "schemas"
REVIEW_PROMPT_TARGET = ROOT / "templates" / "profiles" / "review-prompts" / "files" / ".codex" / "prompts"
TDD_PROMPT_TARGET = ROOT / "templates" / "profiles" / "test-first" / "files" / ".codex" / "prompts" / "tdd"
COMMON_TARGET = ROOT / "templates" / "common"

ALLOWED_SUFFIXES = {".json", ".md"}
REVIEW_PROMPT_EXCLUDES: set[Path] = set()


def workflow_files(base: Path) -> list[Path]:
    if not base.exists():
        raise FileNotFoundError(f"workflow source root does not exist: {base}")
    return sorted(path for path in base.rglob("*") if path.is_file() and path.suffix in ALLOWED_SUFFIXES)


def relative_files(base: Path, exclude_tdd: bool = False, excluded: set[Path] | None = None) -> set[Path]:
    excluded = excluded or set()
    paths = set()
    for path in workflow_files(base):
        rel_path = path.relative_to(base)
        if rel_path in excluded:
            continue
        if exclude_tdd and rel_path.parts and rel_path.parts[0] == "tdd":
            continue
        paths.add(rel_path)
    return paths


def compare_mirror(source: Path, target: Path, source_files: set[Path]) -> list[str]:
    problems: list[str] = []
    target_files = relative_files(target) if target.exists() else set()

    for rel_path in sorted(source_files - target_files):
        problems.append(f"missing target file: {target / rel_path}")
    for rel_path in sorted(target_files - source_files):
        problems.append(f"stale target file: {target / rel_path}")
    for rel_path in sorted(source_files & target_files):
        if not filecmp.cmp(source / rel_path, target / rel_path, shallow=False):
            problems.append(f"outdated target file: {target / rel_path}")
    return problems


def export_mirror(source: Path, target: Path, source_files: set[Path]) -> list[Path]:
    changed: list[Path] = []
    target_files = relative_files(target) if target.exists() else set()

    for rel_path in sorted(source_files):
        source_file = source / rel_path
        target_file = target / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        if not target_file.exists() or not filecmp.cmp(source_file, target_file, shallow=False):
            shutil.copy2(source_file, target_file)
            changed.append(target_file)

    for rel_path in sorted(target_files - source_files):
        stale = target / rel_path
        stale.unlink()
        changed.append(stale)

    prune_empty_dirs(target)
    return changed


def schema_target_names() -> list[str]:
    return sorted(path.name for path in SCHEMA_SOURCE.glob("*.schema.json") if (COMMON_TARGET / path.name).exists())


def compare_schemas() -> list[str]:
    problems: list[str] = []
    for name in schema_target_names():
        source_file = SCHEMA_SOURCE / name
        target_file = COMMON_TARGET / name
        if not filecmp.cmp(source_file, target_file, shallow=False):
            problems.append(f"outdated target file: {target_file}")
    return problems


def export_schemas() -> list[Path]:
    changed: list[Path] = []
    for name in schema_target_names():
        source_file = SCHEMA_SOURCE / name
        target_file = COMMON_TARGET / name
        if not target_file.exists() or not filecmp.cmp(source_file, target_file, shallow=False):
            shutil.copy2(source_file, target_file)
            changed.append(target_file)
    return changed


def prune_empty_dirs(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted((item for item in root.rglob("*") if item.is_dir()), reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="refresh generated target-template copies from workflows/")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    review_files = relative_files(PROMPT_SOURCE, exclude_tdd=True, excluded=REVIEW_PROMPT_EXCLUDES)
    tdd_files = relative_files(PROMPT_SOURCE / "tdd")

    if args.write:
        changed = []
        changed.extend(export_mirror(PROMPT_SOURCE, REVIEW_PROMPT_TARGET, review_files))
        changed.extend(export_mirror(PROMPT_SOURCE / "tdd", TDD_PROMPT_TARGET, tdd_files))
        changed.extend(export_schemas())
        print(f"workflow source export: refreshed {len(changed)} file(s)")
        return 0

    problems = []
    problems.extend(compare_mirror(PROMPT_SOURCE, REVIEW_PROMPT_TARGET, review_files))
    problems.extend(compare_mirror(PROMPT_SOURCE / "tdd", TDD_PROMPT_TARGET, tdd_files))
    problems.extend(compare_schemas())

    if problems:
        print("workflow source templates are out of date:")
        for problem in problems:
            print(f"- {problem}")
        print("Run: make workflow-source-export")
        return 1

    print("workflow source check: current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
