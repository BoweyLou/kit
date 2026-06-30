#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import shlex
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import install  # noqa: E402

KIT_MAKE_TARGETS = ("agent-start", "kit-status", "kit-update", "kit-refresh")

# Script flow:
# 1. Read the existing install manifest and desired update profiles.
# 2. Adopt older installs into the current managed-file manifest format when needed.
# 3. Copy proposed kit files into the target repo's .doc-contract-kit update area.
# 4. Write an update receipt and manifest so humans can review before applying.
#
# Function guide:
# - read_json/write_json/now/run_id provide IO and timestamps.
# - manifest_payload/source_metadata/write_manifest_payload describe the source kit.
# - resolve_profiles/resolve_runtime_adapters/adoption_files/adopt_legacy decide what the target should manage.
# - copy_proposed/update_receipt/write_update_report/merged_manifest_files assemble update artifacts.
# - makefile_includes_kit_bridge/makefile_boundary_reason handle root Makefile ownership migration.
# - apply_update/main orchestrate the update command.


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"_error": str(exc)}


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def has_json_error(payload):
    return isinstance(payload, dict) and "_error" in payload


def profile_config_schema_source(payload, source: str):
    if payload is None:
        return {"source": source, "status": "missing", "version": None}
    if has_json_error(payload):
        return {"source": source, "status": "blocked", "version": None, "reason": "invalid_json"}

    value = payload.get(install.PROFILE_CONFIG_SCHEMA_FIELD)
    if value is None:
        return {"source": source, "status": "missing", "version": None}
    if isinstance(value, bool) or not isinstance(value, int):
        return {"source": source, "status": "blocked", "version": value, "reason": "invalid_version"}
    if value < install.PROFILE_CONFIG_SCHEMA_VERSION:
        return {"source": source, "status": "outdated", "version": value}
    if value > install.PROFILE_CONFIG_SCHEMA_VERSION:
        return {"source": source, "status": "blocked", "version": value, "reason": "future_version"}
    return {"source": source, "status": "current", "version": value}


def profile_config_schema_status(receipt, manifest):
    if receipt is None and manifest is None:
        return {
            "status": "not_applicable",
            "current_version": install.PROFILE_CONFIG_SCHEMA_VERSION,
            "field": install.PROFILE_CONFIG_SCHEMA_FIELD,
            "sources": [],
        }

    sources = [
        profile_config_schema_source(receipt, "install.json"),
        profile_config_schema_source(manifest, "manifest.json"),
    ]
    blocked = [item for item in sources if item["status"] == "blocked"]
    missing = [item for item in sources if item["status"] == "missing"]
    outdated = [item for item in sources if item["status"] == "outdated"]
    if blocked:
        status = "blocked"
    elif missing:
        status = "missing"
    elif outdated:
        status = "outdated"
    else:
        status = "current"
    return {
        "status": status,
        "current_version": install.PROFILE_CONFIG_SCHEMA_VERSION,
        "field": install.PROFILE_CONFIG_SCHEMA_FIELD,
        "sources": sources,
    }


def profile_config_schema_needs_migration(status: dict):
    return status.get("status") in {"missing", "outdated"}


def profile_config_migration_action(schema_status: dict):
    status = schema_status.get("status")
    reason = (
        f"profile/config metadata schema is {status}; explicit metadata migration "
        f"will stamp {install.PROFILE_CONFIG_SCHEMA_FIELD}={install.PROFILE_CONFIG_SCHEMA_VERSION} "
        "without rewriting target-owned files or customized managed files"
    )
    return {
        "id": "migrate-profile-config:.doc-contract-kit",
        "action": "migrate-profile-config",
        "path": ".doc-contract-kit/install.json",
        "managed": False,
        "reason": reason,
        "schema_status": schema_status,
        "writes_on_apply": [".doc-contract-kit/install.json", ".doc-contract-kit/manifest.json"],
    }


def git_status_files(target: Path):
    result = subprocess.run(
        ["git", "-C", str(target), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    files = []
    for line in result.stdout.splitlines():
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            files.append(path)
    return sorted(files)


def kit_payload():
    return {
        "root": str(install.ROOT),
        "version": install.read_kit_version(),
        "source_ref": install.current_source_ref(),
        "prompt_snapshot": install.prompt_snapshot_metadata(),
    }


def manifest_payload(files: list[dict], profiles: list[str], preset: str | None, runtime_adapters: list[str]):
    generated_at = now()
    return {
        "schema_version": 1,
        install.PROFILE_CONFIG_SCHEMA_FIELD: install.PROFILE_CONFIG_SCHEMA_VERSION,
        "kit_version": install.read_kit_version(),
        "source_version": install.read_kit_version(),
        "source_ref": install.current_source_ref(),
        "source_components": install.source_components(),
        "prompt_snapshot": install.prompt_snapshot_metadata(),
        "generated_at": generated_at,
        "preset": preset,
        "profiles": profiles,
        "runtime_adapters": runtime_adapters,
        "files": files,
    }


def source_metadata(entry: dict):
    source_path = entry["source"]
    item = {
        "profile": entry["profile"],
        "source": install.relative_source(source_path),
        "source_sha256": install.sha256_path(source_path),
    }
    if entry.get("runtime_adapter"):
        item["runtime_adapter"] = entry["runtime_adapter"]
    return item


def write_manifest_payload(
    target: Path,
    files: list[dict],
    profiles: list[str],
    preset: str | None,
    runtime_adapters: list[str],
):
    write_json(
        target / ".doc-contract-kit" / "manifest.json",
        manifest_payload(files, profiles, preset, runtime_adapters),
    )


def resolve_profiles(args, receipt):
    if args.preset:
        class Args:
            preset = args.preset
            profiles = None
            profile = None

        return install.resolve_requested_profiles(Args()), args.preset
    if args.profiles:
        class Args:
            preset = None
            profiles = args.profiles
            profile = None

        return install.resolve_requested_profiles(Args()), None
    if receipt and receipt.get("profiles"):
        return receipt["profiles"], receipt.get("preset")
    return [install.DEFAULT_PROFILE], None


def runtime_adapter_flag_values(args):
    values = []
    if getattr(args, "runtime_adapters", None):
        values.append(args.runtime_adapters)
    values.extend(getattr(args, "runtime_adapter", None) or [])
    return values


def resolve_runtime_adapters(args, receipt, manifest):
    values = runtime_adapter_flag_values(args)
    if values:
        return install.parse_runtime_adapter_values(values)
    for source in (receipt, manifest):
        if isinstance(source, dict) and isinstance(source.get("runtime_adapters"), list):
            return install.parse_runtime_adapter_values(source["runtime_adapters"])
    return []


def adoption_files(target: Path, entries: list[dict]):
    files = []
    for rel_target, entry in sorted(install.final_entries_by_target(entries).items()):
        target_path = target / rel_target
        if not target_path.exists():
            continue

        target_owned = rel_target in install.TARGET_OWNED_PATHS
        item = {
            "path": rel_target,
            **source_metadata(entry),
            "installed_sha256": install.sha256_path(target_path),
            "managed": not target_owned,
            "owner": "target" if target_owned else "kit",
        }
        files.append(item)
    return files


def adopt_legacy(target: Path, entries: list[dict], profiles: list[str], preset: str | None, runtime_adapters: list[str]):
    write_manifest_payload(target, adoption_files(target, entries), profiles, preset, runtime_adapters)
    receipt = read_json(target / ".doc-contract-kit" / "install.json") or {}
    receipt.update(
        {
            "schema_version": 1,
            install.PROFILE_CONFIG_SCHEMA_FIELD: install.PROFILE_CONFIG_SCHEMA_VERSION,
            "kit_version": install.read_kit_version(),
            "source_version": install.read_kit_version(),
            "source_ref": install.current_source_ref(),
            "source_components": install.source_components(),
            "prompt_snapshot": install.prompt_snapshot_metadata(),
            "last_updated_at": now(),
            "preset": preset,
            "profiles": profiles,
            "runtime_adapters": runtime_adapters,
        }
    )
    receipt.setdefault("installed_at", now())
    receipt["source_commits"] = {
        "repo-contract-kit": install.current_source_ref(),
        "workflow-source": install.prompt_snapshot_metadata().get("source_ref"),
    }
    write_json(target / ".doc-contract-kit" / "install.json", receipt)
    print("Legacy install adopted. No managed files were overwritten. Re-run update to apply safe updates.")


def copy_proposed(report_dir: Path, rel_target: str, source: Path):
    proposed = report_dir / "proposed" / rel_target
    install.copy_path(source, proposed)
    return proposed


def update_receipt(target: Path, profiles: list[str], preset: str | None, runtime_adapters: list[str]):
    path = target / ".doc-contract-kit" / "install.json"
    receipt = read_json(path) or {}
    receipt.update(
        {
            "schema_version": 1,
            install.PROFILE_CONFIG_SCHEMA_FIELD: install.PROFILE_CONFIG_SCHEMA_VERSION,
            "kit_version": install.read_kit_version(),
            "source_version": install.read_kit_version(),
            "source_ref": install.current_source_ref(),
            "source_components": install.source_components(),
            "prompt_snapshot": install.prompt_snapshot_metadata(),
            "last_updated_at": now(),
            "preset": preset,
            "profiles": profiles,
            "runtime_adapters": runtime_adapters,
            "source_commits": {
                "repo-contract-kit": install.current_source_ref(),
                "workflow-source": install.prompt_snapshot_metadata().get("source_ref"),
            },
        }
    )
    receipt.setdefault("installed_at", now())
    write_json(path, receipt)


def read_next_docs(target: Path):
    docs = []
    target_docs = (
        ("AGENTS.md", "repo-specific agent instructions and kit update rules"),
        (".agent-workflows/README.md", "installed workflow mechanics and update/versioning commands"),
        ("docs/working-rhythm.md", "operator rhythm and kit maintenance path"),
        ("docs/ops/agent-workflow.md", "detailed local agent workflow, update, and versioning runbook"),
    )
    for rel_path, reason in target_docs:
        if (target / rel_path).exists():
            docs.append({"scope": "target", "path": rel_path, "reason": reason})

    changelog = install.ROOT / "CHANGELOG.md"
    if changelog.exists():
        docs.append(
            {
                "scope": "kit",
                "path": str(changelog),
                "reason": "repo-contract-kit release notes for the checkout used by this update",
            }
        )
    return docs


def shell_command(*parts):
    return " ".join(shlex.quote(str(part)) for part in parts)


def after_update_steps(target: Path):
    cli = install.ROOT / "scripts" / "repo_contract_kit.py"
    return [
        {
            "id": "initialize-sidecar",
            "command": shell_command("python3", cli, "sidecar-init", "--repo", target, "--json"),
            "reason": "create repo-external directories for future agent artifacts",
        },
        {
            "id": "write-startup-packet-to-sidecar",
            "command": shell_command("python3", cli, "orient", "--repo", target, "--write-sidecar", "--json"),
            "reason": "write the next startup packet outside the target checkout",
        },
        {
            "id": "write-verify-receipt-to-sidecar",
            "command": shell_command("python3", cli, "verify", "--repo", target, "--write-sidecar", "--json"),
            "reason": "write the next verification receipt outside the target checkout",
        },
    ]


def after_update_notes():
    return [
        {
            "id": "legacy-repo-local-artifacts",
            "message": (
                "Existing .agent-workflows/runs/*, .agent-workflows/tasks/*, and "
                ".doc-contract-kit/updates/* artifacts are not moved automatically; "
                "review them before archiving or moving them to the sidecar."
            ),
        }
    ]


def write_update_report(
    report_dir: Path,
    actions: list[dict],
    conflicts: list[dict],
    dry_run: bool,
    read_next: list[dict],
    after_update: list[dict],
    after_update_note_items: list[dict],
):
    payload = {
        "schema_version": 1,
        "generated_at": now(),
        "dry_run": dry_run,
        "actions": actions,
        "conflicts": conflicts,
        "read_next": read_next,
        "after_update": after_update,
        "after_update_notes": after_update_note_items,
    }
    write_json(report_dir / "update-report.json", payload)

    lines = [
        "# repo-contract-kit update report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- dry_run: {str(dry_run).lower()}",
        f"- actions: {len(actions)}",
        f"- conflicts: {len(conflicts)}",
        "",
        "## Actions",
        "",
    ]
    for action in actions:
        reason = f" - {action['reason']}" if action.get("reason") else ""
        proposed = f" Proposed replacement: `{action['proposed']}`." if action.get("proposed") else ""
        lines.append(f"- {action['action']}: `{action['path']}`{reason}{proposed}")
    if conflicts:
        lines.extend(["", "## Conflicts", ""])
        for conflict in conflicts:
            proposed = f" Proposed replacement: `{conflict['proposed']}`." if conflict.get("proposed") else ""
            lines.append(f"- `{conflict['path']}` differs from the last managed hash.{proposed}")
    if read_next:
        lines.extend(["", "## Read Next", ""])
        for item in read_next:
            lines.append(f"- {item['scope']}: `{item['path']}` - {item['reason']}")
    if after_update:
        lines.extend(["", "## After Updating", ""])
        for item in after_update:
            lines.append(f"- `{item['command']}` - {item['reason']}")
    if after_update_note_items:
        lines.extend(["", "## Notes", ""])
        for item in after_update_note_items:
            lines.append(f"- {item['message']}")
    (report_dir / "update-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def makefile_includes_kit_bridge(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    return install.MAKEFILE_INCLUDE_LINE in text


def makefile_declared_targets(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return set()
    targets = set()
    for line in text.splitlines():
        if not line or line[0].isspace() or line.startswith("#") or ":" not in line:
            continue
        head = line.split(":", 1)[0]
        targets.update(part for part in head.split() if part)
    return targets


def makefile_defines_kit_targets(path: Path):
    targets = makefile_declared_targets(path)
    return all(target in targets for target in KIT_MAKE_TARGETS)


def makefile_boundary_reason(path=None):
    if path and makefile_defines_kit_targets(path):
        return (
            "root Makefile defines kit targets directly; keep maintaining those local targets "
            f"or include `{install.MAKEFILE_INCLUDE_LINE}` to receive future managed kit target updates"
        )
    return (
        "root Makefile is target-owned; keep product targets there and include "
        f"`{install.MAKEFILE_INCLUDE_LINE}` to receive kit make targets"
    )


def makefile_boundary_status(root: Path, manifest):
    makefile = root / "Makefile"
    bridge = root / install.MAKEFILE_BRIDGE_PATH
    makefile_item = None
    bridge_item = None
    if isinstance(manifest, dict):
        for item in manifest.get("files", []):
            if not isinstance(item, dict):
                continue
            if item.get("path") == "Makefile":
                makefile_item = item
            if item.get("path") == install.MAKEFILE_BRIDGE_PATH:
                bridge_item = item

    if not makefile.exists():
        return "missing-root-makefile"
    if not bridge.exists():
        return "missing-kit-make-fragment"
    if not makefile_includes_kit_bridge(makefile):
        if makefile_defines_kit_targets(makefile):
            return "target-owned-root-makefile-direct-kit-targets"
        return "target-owned-root-makefile-missing-include"
    if makefile_item and makefile_item.get("owner") == "target" and bridge_item and bridge_item.get("managed"):
        return "target-owned-root-makefile-bridge-managed"
    return "bridge-present"


def merged_manifest_files(target: Path, entries: list[dict], old_files: dict, actions: list[dict]):
    actions_by_path = {action["path"]: action for action in actions}
    files = []
    for rel_target, entry in sorted(install.final_entries_by_target(entries).items()):
        target_path = target / rel_target
        if not target_path.exists():
            continue

        old = old_files.get(rel_target, {})
        action = actions_by_path.get(rel_target, {})
        target_owned = rel_target in install.TARGET_OWNED_PATHS or old.get("owner") == "target"
        old_managed = bool(old.get("managed"))
        action_name = action.get("action")

        if action_name == "conflict" and old_managed:
            item = dict(old)
            item.update({"path": rel_target, **source_metadata(entry), "managed": True, "owner": "kit"})
            files.append(item)
            continue

        managed = not target_owned and (
            old_managed or action_name in {"update", "restore", "force-update"}
        )
        owner = "kit" if managed else "target"
        item = {
            "path": rel_target,
            **source_metadata(entry),
            "installed_sha256": install.sha256_path(target_path),
            "managed": managed,
            "owner": owner,
        }
        files.append(item)
    return files


def planned_update_actions(target: Path, entries: list[dict], manifest: dict, force_managed: bool, report_dir: Path | None = None):
    old_files = {item["path"]: item for item in manifest.get("files", []) if "path" in item}
    final_entries = install.final_entries_by_target(entries)
    actions = []
    conflicts = []

    for rel_target, entry in sorted(final_entries.items()):
        target_path = target / rel_target
        source_path = entry["source"]
        source_sha = install.sha256_path(source_path)
        old = old_files.get(rel_target)
        target_owned = rel_target in install.TARGET_OWNED_PATHS or (old and old.get("owner") == "target")

        if target_owned:
            if rel_target == "Makefile":
                current_sha = install.sha256_path(target_path) if target_path.exists() else None
                expected_sha = old.get("installed_sha256") if old else None
                old_managed = bool(old and old.get("managed"))
                clean_old_managed = bool(target_path.exists() and old_managed and current_sha == expected_sha)

                if clean_old_managed or (old and old_managed and not target_path.exists()):
                    action_name = "migrate-target-owned" if target_path.exists() else "create-target-owned-bridge"
                    actions.append(
                        {
                            "path": rel_target,
                            "action": action_name,
                            "managed": False,
                            "reason": makefile_boundary_reason(target_path),
                            "writes_on_apply": [rel_target],
                        }
                    )
                    continue

                if target_path.exists() and not makefile_includes_kit_bridge(target_path):
                    action = {
                        "path": rel_target,
                        "action": "target-owned",
                        "managed": False,
                        "reason": makefile_boundary_reason(target_path),
                    }
                    if report_dir:
                        action["proposed"] = str((report_dir / "proposed" / rel_target).relative_to(target))
                        action["writes_on_apply"] = [action["proposed"]]
                    actions.append(action)
                    continue

            action_name = "target-owned-missing" if not target_path.exists() else "target-owned"
            actions.append({"path": rel_target, "action": action_name, "managed": False})
            continue

        current_sha = install.sha256_path(target_path) if target_path.exists() else None
        expected_sha = old.get("installed_sha256") if old else None
        clean = target_path.exists() and old and current_sha == expected_sha

        if target_path.exists() and not clean and not force_managed:
            action = {
                "path": rel_target,
                "action": "conflict",
                "reason": "target file differs from last managed hash",
                "current_sha256": current_sha,
                "expected_sha256": expected_sha,
            }
            if report_dir:
                action["proposed"] = str((report_dir / "proposed" / rel_target).relative_to(target))
                action["writes_on_apply"] = [action["proposed"]]
            conflicts.append(action)
            actions.append(action)
            continue

        if target_path.exists() and current_sha == source_sha and not force_managed:
            actions.append({"path": rel_target, "action": "current", "managed": True})
            continue

        if force_managed and target_path.exists() and not clean:
            action_name = "force-update"
        else:
            action_name = "restore" if not target_path.exists() else "update"
        actions.append({"path": rel_target, "action": action_name, "managed": True, "writes_on_apply": [rel_target]})

    return actions, conflicts


def detected_state(target: Path, receipt, manifest, dirty_files: list[str]):
    receipt_present = receipt is not None
    manifest_present = manifest is not None
    receipt_error = receipt.get("_error") if has_json_error(receipt) else None
    manifest_error = manifest.get("_error") if has_json_error(manifest) else None
    if receipt_error or manifest_error:
        kind = "invalid_metadata"
    elif not receipt_present and not manifest_present:
        kind = "not_installed"
    elif receipt_present and not manifest_present:
        kind = "legacy_receipt_no_manifest"
    elif not receipt_present and manifest_present:
        kind = "manifest_without_receipt"
    else:
        kind = "current_manifest"
    return {
        "kind": kind,
        "installed": bool(receipt_present and not receipt_error),
        "receipt_present": receipt_present,
        "receipt_error": receipt_error,
        "manifest_present": manifest_present,
        "manifest_error": manifest_error,
        "dirty": bool(dirty_files),
        "dirty_files": dirty_files,
        "profile_config_schema": profile_config_schema_status(receipt, manifest),
        "makefile_boundary": makefile_boundary_status(target, manifest)
        if isinstance(manifest, dict) and not has_json_error(manifest)
        else None,
    }


def build_update_plan(
    target: Path,
    profiles: list[str],
    preset: str | None,
    runtime_adapters: list[str],
    entries: list[dict],
    receipt,
    manifest,
    args,
):
    dirty_files = git_status_files(target)
    state = detected_state(target, receipt, manifest, dirty_files)
    actions = []
    conflicts = []
    blockers = []
    warnings = []
    report_dir = target / ".doc-contract-kit" / "updates" / run_id()

    if dirty_files:
        warnings.append(
            {
                "code": "dirty_target_repo",
                "message": "Target repo has local changes; review before applying updates.",
                "paths": dirty_files,
            }
        )

    if state["kind"] == "invalid_metadata":
        blockers.append(
            {
                "code": "invalid_metadata",
                "message": "Install receipt or manifest JSON is invalid; repair metadata before applying updates.",
            }
        )
    elif state["profile_config_schema"]["status"] == "blocked":
        blockers.append(
            {
                "code": "profile_config_schema_blocked",
                "message": "Profile/config schema metadata is invalid or newer than this kit; inspect install.json and manifest.json before applying updates.",
                "schema_status": state["profile_config_schema"],
            }
        )
    elif state["kind"] == "not_installed":
        actions.append(
            {
                "id": "install:repo-contract-kit",
                "action": "install-required",
                "path": ".doc-contract-kit/install.json",
                "managed": False,
                "reason": "repo-contract-kit is not installed; use the explicit install command if the repo owner wants checked-in kit files.",
            }
        )
    elif state["kind"] == "manifest_without_receipt":
        blockers.append(
            {
                "code": "manifest_without_receipt",
                "message": "Managed manifest exists without install receipt; repair metadata before applying updates.",
            }
        )
    elif state["kind"] == "legacy_receipt_no_manifest":
        actions.append(
            {
                "id": "adopt-legacy:.doc-contract-kit/manifest.json",
                "action": "adopt-legacy",
                "path": ".doc-contract-kit/manifest.json",
                "managed": True,
                "reason": "legacy install has no manifest; apply adopts current target files without overwriting them.",
                "writes_on_apply": [".doc-contract-kit/manifest.json", ".doc-contract-kit/install.json"],
            }
        )
    elif isinstance(manifest, dict):
        actions, conflicts = planned_update_actions(
            target,
            entries,
            manifest,
            force_managed=args.force_managed,
            report_dir=report_dir,
        )
        if profile_config_schema_needs_migration(state["profile_config_schema"]):
            actions.append(profile_config_migration_action(state["profile_config_schema"]))

    action_count = len(actions)
    conflict_count = len(conflicts)
    return {
        "schema_version": 1,
        "command": "update-plan",
        "repo": str(target),
        "kit": kit_payload(),
        "runtime_adapters": runtime_adapters,
        "target_repo_writes": {
            "performed": False,
            "paths": [],
            "reason": "plan-only command",
        },
        "detected_state": state,
        "summary": {
            "actions": action_count,
            "conflicts": conflict_count,
            "blockers": len(blockers),
            "warnings": len(warnings),
            "would_write": False,
            "apply_command": f"python3 {install.ROOT / 'scripts' / 'update.py'} {target} --apply",
            "config_migration_command": f"python3 {install.ROOT / 'scripts' / 'update.py'} {target} --apply --metadata-only",
        },
        "actions": actions,
        "conflicts": conflicts,
        "blockers": blockers,
        "warnings": warnings,
        "read_next": read_next_docs(target),
        "after_update": after_update_steps(target),
        "after_update_notes": after_update_notes(),
        "next_commands": next_commands_for_plan(target, state, blockers),
    }


def next_commands_for_plan(target: Path, state: dict, blockers: list[dict]):
    if blockers:
        return []
    if profile_config_schema_needs_migration(state.get("profile_config_schema") or {}):
        return [
            f"python3 {install.ROOT / 'scripts' / 'update.py'} {target} --apply --metadata-only",
            f"python3 {install.ROOT / 'scripts' / 'update.py'} {target} --apply",
        ]
    if state["kind"] == "not_installed":
        return [f"python3 {install.ROOT / 'scripts' / 'install.py'} {target} --preset agentic"]
    if state["kind"] in {"legacy_receipt_no_manifest", "current_manifest"}:
        return [f"python3 {install.ROOT / 'scripts' / 'update.py'} {target} --apply"]
    return []


def render_update_plan(plan: dict):
    state = plan["detected_state"]
    print(f"repo: {plan['repo']}")
    print(f"state: {state['kind']}")
    print(f"dirty: {str(state['dirty']).lower()}")
    print(f"actions: {plan['summary']['actions']}")
    print(f"conflicts: {plan['summary']['conflicts']}")
    print(f"blockers: {plan['summary']['blockers']}")
    schema_status = state.get("profile_config_schema")
    if schema_status:
        print(
            "profile/config schema: "
            f"{schema_status['status']} "
            f"(current {schema_status['current_version']})"
        )
    for blocker in plan["blockers"]:
        print(f"blocker: {blocker['code']} - {blocker['message']}")
    for warning in plan["warnings"]:
        print(f"warning: {warning['code']} - {warning['message']}")
    for action in plan["actions"]:
        print(f" - {action['action']}: {action['path']}")
    if plan["read_next"]:
        print("read next:")
        for item in plan["read_next"]:
            print(f" - {item['scope']}: {item['path']} - {item['reason']}")
    if plan.get("after_update"):
        print("after updating:")
        for item in plan["after_update"]:
            print(f" - {item['command']} - {item['reason']}")
    if plan.get("after_update_notes"):
        print("notes:")
        for item in plan["after_update_notes"]:
            print(f" - {item['message']}")


def migrate_manifest_metadata(manifest: dict, profiles: list[str], preset: str | None, runtime_adapters: list[str]):
    payload = dict(manifest)
    payload["schema_version"] = 1
    payload[install.PROFILE_CONFIG_SCHEMA_FIELD] = install.PROFILE_CONFIG_SCHEMA_VERSION
    payload.setdefault("files", [])
    return payload


def migrate_receipt_metadata(receipt: dict, profiles: list[str], preset: str | None, runtime_adapters: list[str]):
    payload = dict(receipt)
    payload["schema_version"] = 1
    payload[install.PROFILE_CONFIG_SCHEMA_FIELD] = install.PROFILE_CONFIG_SCHEMA_VERSION
    return payload


def apply_config_metadata_migration(
    target: Path,
    receipt: dict,
    manifest: dict,
    profiles: list[str],
    preset: str | None,
    runtime_adapters: list[str],
    schema_status: dict,
):
    if not profile_config_schema_needs_migration(schema_status):
        print("Profile/config metadata schema is already current.")
        return

    write_json(
        target / ".doc-contract-kit" / "manifest.json",
        migrate_manifest_metadata(manifest, profiles, preset, runtime_adapters),
    )
    write_json(
        target / ".doc-contract-kit" / "install.json",
        migrate_receipt_metadata(receipt, profiles, preset, runtime_adapters),
    )
    print("Profile/config metadata migration complete.")
    print(f" - {install.PROFILE_CONFIG_SCHEMA_FIELD}: {install.PROFILE_CONFIG_SCHEMA_VERSION}")


def apply_update(
    target: Path,
    entries: list[dict],
    manifest: dict,
    profiles: list[str],
    preset: str | None,
    runtime_adapters: list[str],
    args,
):
    report_dir = target / ".doc-contract-kit" / "updates" / run_id()
    old_files = {item["path"]: item for item in manifest.get("files", []) if "path" in item}
    actions, conflicts = planned_update_actions(
        target,
        entries,
        manifest,
        force_managed=args.force_managed,
        report_dir=report_dir,
    )
    schema_status = profile_config_schema_status(
        read_json(target / ".doc-contract-kit" / "install.json"),
        manifest,
    )
    if profile_config_schema_needs_migration(schema_status):
        actions.append(profile_config_migration_action(schema_status))
    final_entries = install.final_entries_by_target(entries)

    for action in actions:
        rel_target = action["path"]
        entry = final_entries.get(rel_target)
        if not entry:
            continue
        source_path = entry["source"]
        action_name = action["action"]
        if action_name in {"migrate-target-owned", "create-target-owned-bridge", "update", "restore", "force-update"}:
            install.copy_path(source_path, target / rel_target)
        elif action_name in {"target-owned", "conflict"} and action.get("proposed"):
            proposed = copy_proposed(report_dir, rel_target, source_path)
            action["proposed"] = str(proposed.relative_to(target))

    write_update_report(
        report_dir,
        actions,
        conflicts,
        dry_run=False,
        read_next=read_next_docs(target),
        after_update=after_update_steps(target),
        after_update_note_items=after_update_notes(),
    )
    if conflicts:
        print(f"Conflicts preserved. Review {report_dir.relative_to(target)}/update-report.md")

    write_manifest_payload(
        target,
        merged_manifest_files(target, entries, old_files, actions),
        profiles,
        preset,
        runtime_adapters,
    )
    update_receipt(target, profiles, preset, runtime_adapters)

    print("Update complete.")
    for action in actions:
        print(f" - {action['action']}: {action['path']}")


def main():
    parser = argparse.ArgumentParser(description="Safely update repo-contract-kit files in a target repo")
    parser.add_argument("target", help="Path to target repository")
    parser.add_argument("--dry-run", action="store_true", help="Alias for the default non-mutating update plan")
    parser.add_argument("--plan-json", action="store_true", help="Emit the non-mutating update plan as JSON")
    parser.add_argument("--apply", action="store_true", help="Apply safe updates. Without this flag, update.py only plans.")
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="With --apply, migrate only repo-contract-kit profile/config metadata schema markers.",
    )
    parser.add_argument("--preset", help="Override installed preset")
    parser.add_argument("--profiles", help="Override installed profile list")
    parser.add_argument(
        "--runtime-adapter",
        action="append",
        help=(
            "Runtime instruction adapter to manage. Repeat or use --runtime-adapters. "
            f"Available: {install.available_runtime_adapters()}."
        ),
    )
    parser.add_argument(
        "--runtime-adapters",
        help="Comma-separated runtime instruction adapters to manage. Use `none` to clear explicit selection.",
    )
    parser.add_argument("--force-managed", action="store_true", help="Overwrite customized kit-managed files")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    install.ensure_git_repo(target)
    receipt = read_json(target / ".doc-contract-kit" / "install.json")
    receipt_for_profiles = receipt if isinstance(receipt, dict) and not has_json_error(receipt) else None
    manifest_path = target / ".doc-contract-kit" / "manifest.json"
    manifest = read_json(manifest_path)
    manifest_for_adapters = manifest if isinstance(manifest, dict) and not has_json_error(manifest) else None
    profiles, preset = resolve_profiles(args, receipt_for_profiles)
    runtime_adapters = resolve_runtime_adapters(args, receipt_for_profiles, manifest_for_adapters)
    entries = install.desired_entries(profiles, runtime_adapters)
    plan = build_update_plan(target, profiles, preset, runtime_adapters, entries, receipt, manifest, args)

    if args.plan_json or args.dry_run or not args.apply:
        if args.plan_json or args.dry_run:
            print(json.dumps(plan, indent=2, sort_keys=True))
        else:
            render_update_plan(plan)
        return 1 if plan["blockers"] else 0

    if plan["blockers"]:
        render_update_plan(plan)
        return 2

    if plan["detected_state"]["kind"] == "not_installed":
        print("repo-contract-kit is not installed; run install explicitly before update.", file=sys.stderr)
        return 2

    if plan["detected_state"]["kind"] == "manifest_without_receipt":
        print("repo-contract-kit manifest exists without install receipt; repair metadata before update.", file=sys.stderr)
        return 2

    if args.metadata_only:
        if manifest is None:
            adopt_legacy(target, entries, profiles, preset, runtime_adapters)
            return 0
        apply_config_metadata_migration(
            target,
            receipt_for_profiles or {},
            manifest,
            profiles,
            preset,
            runtime_adapters,
            plan["detected_state"]["profile_config_schema"],
        )
        return 0

    if manifest is None:
        adopt_legacy(target, entries, profiles, preset, runtime_adapters)
        return 0

    apply_update(target, entries, manifest, profiles, preset, runtime_adapters, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
