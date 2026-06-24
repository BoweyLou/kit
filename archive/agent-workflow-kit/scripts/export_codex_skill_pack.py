#!/usr/bin/env python3
"""Export workflow prompts as a Codex-compatible skill pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Script flow:
# 1. Load the workflow manifest and Codex skill-pack export configuration.
# 2. Resolve selected skills and their referenced prompt files from source_root.
# 3. Render deterministic SKILL.md files plus copied references under the output.
# 4. Write or check the generated pack manifest and generated file contents.
#
# Function guide:
# - load_manifest/source_root/skill_pack_config read repository configuration.
# - resolve_skill_specs/resolve_source_files validate selected skills and files.
# - render_skill/build_expected_files construct deterministic artifact content.
# - compare_expected/export_expected implement check/write behavior.
ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SUFFIXES = {".json", ".md"}
PACK_MANIFEST = "pack-manifest.json"
SAFE_SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class SkillSpec:
    id: str
    name: str
    display_name: str
    description: str
    entrypoint: str
    include: tuple[str, ...]


def load_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / "workflows" / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def source_root(root: Path, manifest: dict[str, Any]) -> Path:
    return root / manifest["source_root"]


def read_version(root: Path) -> str:
    version_path = root / "VERSION"
    if not version_path.exists():
        return "0.0.0"
    return version_path.read_text(encoding="utf-8").strip()


def skill_pack_config(manifest: dict[str, Any]) -> dict[str, Any]:
    config = manifest.get("codex_skill_pack")
    if not isinstance(config, dict):
        raise ValueError("workflows/manifest.json is missing codex_skill_pack")
    if not isinstance(config.get("skills"), list) or not config["skills"]:
        raise ValueError("codex_skill_pack.skills must contain at least one skill")
    return config


def parse_skill(raw: dict[str, Any]) -> SkillSpec:
    required = ("id", "name", "display_name", "description", "entrypoint", "include")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"skill export is missing required field(s): {', '.join(missing)}")
    include = raw["include"]
    if not isinstance(include, list) or not all(isinstance(item, str) for item in include):
        raise ValueError(f"{raw.get('id', '(unknown)')}: include must be a list of paths or globs")
    name = str(raw["name"])
    if not SAFE_SKILL_NAME_RE.fullmatch(name):
        raise ValueError(f"{raw.get('id', '(unknown)')}: name must be a single safe directory name")
    return SkillSpec(
        id=str(raw["id"]),
        name=name,
        display_name=str(raw["display_name"]),
        description=str(raw["description"]),
        entrypoint=str(raw["entrypoint"]),
        include=tuple(include),
    )


def resolve_skill_specs(config: dict[str, Any], requested: list[str]) -> list[SkillSpec]:
    all_specs = [parse_skill(raw) for raw in config["skills"]]
    by_id = {spec.id: spec for spec in all_specs}
    by_name = {spec.name: spec for spec in all_specs}
    if not requested:
        return all_specs

    selected: list[SkillSpec] = []
    unknown: list[str] = []
    for item in requested:
        spec = by_id.get(item) or by_name.get(item)
        if spec is None:
            unknown.append(item)
        elif spec not in selected:
            selected.append(spec)
    if unknown:
        known = sorted(set(by_id) | set(by_name))
        raise ValueError(f"unknown skill(s): {', '.join(unknown)}; known skills: {', '.join(known)}")
    return selected


def validate_relative_pattern(pattern: str, skill: SkillSpec) -> None:
    parts = Path(pattern).parts
    if Path(pattern).is_absolute() or ".." in parts:
        raise ValueError(f"{skill.id}: include path must stay inside source_root: {pattern}")


def resolve_source_files(source: Path, skill: SkillSpec) -> list[Path]:
    patterns = [skill.entrypoint, *skill.include]
    files: dict[str, Path] = {}
    for pattern in patterns:
        validate_relative_pattern(pattern, skill)
        matches = sorted(path for path in source.glob(pattern) if path.is_file())
        if not matches:
            raise FileNotFoundError(f"{skill.id}: no source files matched {pattern}")
        for path in matches:
            if path.suffix not in ALLOWED_SUFFIXES:
                raise ValueError(f"{skill.id}: unsupported source file suffix: {path}")
            rel_path = path.relative_to(source).as_posix()
            files[rel_path] = path
    return [files[key] for key in sorted(files)]


def fold_frontmatter(value: str) -> str:
    lines = textwrap.wrap(value, width=76) or [""]
    return "\n".join(f"  {line}" for line in lines)


def render_skill(spec: SkillSpec, references: list[Path], source: Path, version: str) -> str:
    rel_refs = [path.relative_to(source).as_posix() for path in references]
    entrypoint = f"references/{spec.entrypoint}"
    lines = [
        "---",
        f"name: {spec.name}",
        "description: >-",
        fold_frontmatter(spec.description),
        "---",
        "",
        f"# {spec.display_name}",
        "",
        (
            "This generated skill packages selected agent-workflow-kit prompts for "
            f"Codex runtimes. The canonical source remains `workflows/prompts/` in "
            f"agent-workflow-kit version {version}."
        ),
        "",
        "## Workflow",
        "",
        f"1. Start with `{entrypoint}`.",
        "2. Load the other reference files only when the task needs that workflow detail.",
        "3. Preserve any repository-local guardrails, task packets, docs impact, and validation requirements.",
        "4. Treat this skill pack as a runtime projection; update the source repo and re-export when behavior changes.",
        "",
        "## Included References",
        "",
    ]
    lines.extend(f"- `references/{rel_path}`" for rel_path in rel_refs)
    return "\n".join(lines) + "\n"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def pack_output_path(root: Path, config: dict[str, Any], requested_output: Path | None) -> Path:
    raw = requested_output or Path(config.get("default_output", "dist/codex-skill-pack"))
    return raw if raw.is_absolute() else root / raw


def display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def build_expected_files(
    root: Path,
    manifest: dict[str, Any],
    config: dict[str, Any],
    skills: list[SkillSpec],
) -> dict[Path, bytes]:
    source = source_root(root, manifest)
    version = read_version(root)
    expected: dict[Path, bytes] = {}
    skill_records: list[dict[str, Any]] = []

    for skill in skills:
        references = resolve_source_files(source, skill)
        skill_file = render_skill(skill, references, source, version).encode("utf-8")
        skill_root = Path(skill.name)
        expected[skill_root / "SKILL.md"] = skill_file

        file_records = [
            {
                "path": "SKILL.md",
                "bytes": len(skill_file),
                "sha256": sha256_bytes(skill_file),
            }
        ]
        source_files: list[str] = []
        for source_file in references:
            rel_source = source_file.relative_to(source).as_posix()
            content = source_file.read_bytes()
            rel_output = Path(skill.name) / "references" / rel_source
            expected[rel_output] = content
            source_files.append(f"{manifest['source_root']}/{rel_source}")
            file_records.append(
                {
                    "path": f"references/{rel_source}",
                    "bytes": len(content),
                    "sha256": sha256_bytes(content),
                }
            )

        skill_records.append(
            {
                "id": skill.id,
                "name": skill.name,
                "display_name": skill.display_name,
                "description": skill.description,
                "path": skill.name,
                "entrypoint": f"{skill.name}/references/{skill.entrypoint}",
                "source_entrypoint": f"{manifest['source_root']}/{skill.entrypoint}",
                "source_files": source_files,
                "files": sorted(file_records, key=lambda item: item["path"]),
            }
        )

    generated_files = sorted(path.as_posix() for path in [*expected, Path(PACK_MANIFEST)])
    pack_manifest = {
        "schema_version": 1,
        "pack": {
            "id": config.get("id", "agent-workflow-kit-codex-skills"),
            "name": config.get("name", "Agent Workflow Kit Codex Skills"),
            "description": config.get(
                "description",
                "Codex skill folders generated from agent-workflow-kit prompts.",
            ),
            "target_runtime": "codex",
        },
        "source": {
            "name": manifest.get("name", "agent-workflow-kit"),
            "version": version,
            "manifest": "workflows/manifest.json",
            "source_root": manifest["source_root"],
        },
        "install": {
            "shape": "copy or symlink selected skill directories into a Codex skill discovery directory",
            "repo_scope": ".agents/skills",
            "user_scope": "$HOME/.agents/skills",
            "note": "The exporter writes only to its output directory; it does not install into Codex by default.",
        },
        "skills": skill_records,
        "generated_files": generated_files,
    }
    expected[Path(PACK_MANIFEST)] = (json.dumps(pack_manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return dict(sorted(expected.items(), key=lambda item: item[0].as_posix()))


def previous_generated_files(output: Path) -> set[Path]:
    manifest_path = output / PACK_MANIFEST
    if not manifest_path.exists():
        return set()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    files = payload.get("generated_files", [])
    if not isinstance(files, list):
        return set()
    safe_files: set[Path] = set()
    for item in files:
        if not isinstance(item, str):
            continue
        path = Path(item)
        if path.is_absolute() or ".." in path.parts:
            continue
        safe_files.add(path)
    return safe_files


def compare_expected(output: Path, expected: dict[Path, bytes]) -> list[str]:
    problems: list[str] = []
    expected_paths = set(expected)
    stale_paths = previous_generated_files(output) - expected_paths

    for rel_path in sorted(expected_paths):
        target = output / rel_path
        if not target.exists():
            problems.append(f"missing target file: {target}")
            continue
        if target.read_bytes() != expected[rel_path]:
            problems.append(f"outdated target file: {target}")

    for rel_path in sorted(stale_paths):
        target = output / rel_path
        if target.exists():
            problems.append(f"stale target file: {target}")
    return problems


def prune_empty_dirs(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted((item for item in root.rglob("*") if item.is_dir()), reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass


def export_expected(output: Path, expected: dict[Path, bytes]) -> list[Path]:
    changed: list[Path] = []
    expected_paths = set(expected)

    for rel_path in sorted(previous_generated_files(output) - expected_paths):
        target = output / rel_path
        if target.exists():
            target.unlink()
            changed.append(target)

    for rel_path, content in expected.items():
        target = output / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() == content:
            continue
        target.write_bytes(content)
        changed.append(target)

    prune_empty_dirs(output)
    return changed


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--output", type=Path, help="output directory for the generated skill pack")
    parser.add_argument("--skill", action="append", default=[], help="skill id or name to export; repeat to select multiple")
    parser.add_argument("--check", action="store_true", help="fail if the output skill pack is out of date")
    parser.add_argument("--list", action="store_true", help="list configured Codex skill-pack exports")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    try:
        manifest = load_manifest(root)
        config = skill_pack_config(manifest)
        skills = resolve_skill_specs(config, args.skill)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.list:
        for skill in skills:
            print(f"{skill.id}\t{skill.name}\t{skill.entrypoint}")
        return 0

    try:
        expected = build_expected_files(root, manifest, config, skills)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    output = pack_output_path(root, config, args.output).resolve()
    if args.check:
        problems = compare_expected(output, expected)
        if problems:
            print("Codex skill pack is out of date:", file=sys.stderr)
            for problem in problems:
                print(f"- {problem}", file=sys.stderr)
            print(
                f"Run: python3 scripts/export_codex_skill_pack.py --output {display_path(root, output)}",
                file=sys.stderr,
            )
            return 1
        print(f"Codex skill pack is current at {display_path(root, output)}.")
        return 0

    changed = export_expected(output, expected)
    print(f"codex-skill-pack: exported {len(changed)} changed file(s) to {display_path(root, output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
