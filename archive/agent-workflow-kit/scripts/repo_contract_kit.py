#!/usr/bin/env python3
"""Human-guided and automation-safe command surface for repo-contract-kit."""

from __future__ import annotations

import argparse
import csv
import difflib
import fnmatch
import hashlib
import importlib.util
import json
import os
import re
import shutil
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
CLI_ENTRYPOINT = ROOT / "scripts" / "repo_contract_kit.py"
STATE_APP_DIR = "repo-contract-kit"
PUBLIC_COMMAND = "kit"
INTERNAL_PRODUCT_NAME = "repo-contract-kit"
DEFAULT_WORKFLOW_SOURCE = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "agent-workflow-kit" / "source"
SIDECAR_DIR_KEYS = (
    "runs_dir",
    "receipts_dir",
    "review_artifacts_dir",
    "docs_patch_proposals_dir",
    "task_packets_dir",
    "automation_handoffs_dir",
    "quarantine_dir",
)
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_doc_impact  # noqa: E402
import check_docs_as_tests  # noqa: E402
import check_token_budget  # noqa: E402
import branch_readiness  # noqa: E402
import changelog_update  # noqa: E402
import docs_explain  # noqa: E402
import goal_check  # noqa: E402
import kit_status  # noqa: E402
import lint_agent_docs  # noqa: E402

BACKLOG_PRIMARY_CANDIDATES = (
    "docs/backlog.md",
    "BACKLOG.md",
    "backlog.md",
    "research/agentic-workflow-review/backlog.csv",
)
BACKLOG_MIRROR_CANDIDATES = (
    "research/agentic-workflow-review/agent-workflow-kit-backlog.csv",
    "research/agentic-workflow-review/repo-contract-kit-backlog.csv",
)
AUTOMATION_HANDOFF_DEFAULT_PATHS = (
    "docs/backlog.md",
    "BACKLOG.md",
    "backlog.md",
    "research/agentic-workflow-review/",
)
DEFAULT_BRANCH_NAMES = {"main", "master", "trunk", "develop"}
DONE_STATUSES = {"done", "complete", "completed", "closed", "shipped"}
OPEN_STATUSES = {"", "open", "todo", "not-started", "not_started", "planned"}
PARTIAL_STATUSES = {"partial", "in-progress", "in_progress", "active", "blocked"}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
SELF_HEAL_TERMINAL_STATUSES = DONE_STATUSES | {"blocked", "abandoned"}
SELF_HEAL_GENERATED_PREFIXES = (
    ".agent-workflows/runs/",
    ".agent-workflows/tasks/",
    ".doc-contract-kit/updates/",
)
SELF_HEAL_GENERATED_EXACT_PATHS = {
    ".agent-workflows/runs/.gitignore",
    ".agent-workflows/tasks/.gitignore",
    ".doc-contract-kit/updates/.gitignore",
}
CONTEXT_BUNDLE_DEFAULT_LIMITS = {
    "files": 25,
    "open_items": 5,
    "tasks": 10,
    "token_files": 10,
    "warnings": 10,
    "commands": 12,
}
SOURCE_CLONE_SKIP_DIRS = {
    ".agent-workflows",
    ".doc-contract-kit",
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "node_modules",
    "venv",
}
SOURCE_CLONE_REMOTE_HINTS = {
    "repo-contract-kit": "repo-contract-kit",
    "agent-workflow-kit": "agent-workflow-kit",
}


class CliError(Exception):
    def __init__(self, message: str, exit_code: int = 2):
        super().__init__(message)
        self.exit_code = exit_code


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"_error": str(exc)}


def read_text(path: Path) -> str | None:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return value or None


def kit_version() -> str:
    return read_text(ROOT / "VERSION") or "0.0.0-local"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean_optional(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def attribution_object(
    *,
    owner: Any = None,
    owner_label: Any = None,
    session_id: Any = None,
    thread_id: Any = None,
    automation_id: Any = None,
    run_id: Any = None,
    metadata_path: Any = None,
    latest_receipt_path: Any = None,
    latest_receipt_provenance: Any = None,
    source: str = "metadata",
) -> dict[str, Any]:
    payload = {
        "owner": clean_optional(owner),
        "owner_label": clean_optional(owner_label),
        "session_id": clean_optional(session_id),
        "thread_id": clean_optional(thread_id),
        "automation_id": clean_optional(automation_id),
        "run_id": clean_optional(run_id),
        "metadata_path": clean_optional(metadata_path),
        "latest_receipt": {
            "path": clean_optional(latest_receipt_path),
            "provenance": clean_optional(latest_receipt_provenance),
        },
    }
    identity_fields = ("owner", "owner_label", "session_id", "thread_id", "automation_id", "run_id")
    if any(payload.get(field) for field in identity_fields):
        confidence = "metadata" if source == "unknown" else source
    elif source == "inferred":
        confidence = "inferred"
    elif source == "receipt" and payload["latest_receipt"]["path"]:
        confidence = "receipt"
    else:
        confidence = "unknown"
    payload["confidence"] = confidence
    payload["source"] = confidence
    return payload


def attribution_from_task(task: dict[str, Any]) -> dict[str, Any]:
    existing = task.get("attribution")
    if isinstance(existing, dict):
        latest = existing.get("latest_receipt") if isinstance(existing.get("latest_receipt"), dict) else {}
        return attribution_object(
            owner=existing.get("owner") or task.get("owner"),
            owner_label=existing.get("owner_label") or task.get("owner_label"),
            session_id=existing.get("session_id") or task.get("session_id"),
            thread_id=existing.get("thread_id") or task.get("thread_id"),
            automation_id=existing.get("automation_id") or task.get("automation_id"),
            run_id=existing.get("run_id") or task.get("run_id"),
            metadata_path=existing.get("metadata_path") or task.get("_metadata_path") or task.get("metadata_path"),
            latest_receipt_path=latest.get("path") or task.get("final_receipt"),
            latest_receipt_provenance=latest.get("provenance") or ("metadata" if task.get("final_receipt") else None),
            source=existing.get("source") or "metadata",
        )
    return attribution_object(
        owner=task.get("owner"),
        owner_label=task.get("owner_label"),
        session_id=task.get("session_id"),
        thread_id=task.get("thread_id"),
        automation_id=task.get("automation_id"),
        run_id=task.get("run_id"),
        metadata_path=task.get("_metadata_path") or task.get("metadata_path"),
        latest_receipt_path=task.get("final_receipt"),
        latest_receipt_provenance="metadata" if task.get("final_receipt") else None,
        source="metadata",
    )


def attribution_from_receipt(payload: dict[str, Any], path: Path | str | None = None) -> dict[str, Any]:
    existing = payload.get("attribution")
    if isinstance(existing, dict):
        latest = existing.get("latest_receipt") if isinstance(existing.get("latest_receipt"), dict) else {}
        return attribution_object(
            owner=existing.get("owner"),
            owner_label=existing.get("owner_label"),
            session_id=existing.get("session_id"),
            thread_id=existing.get("thread_id"),
            automation_id=existing.get("automation_id"),
            run_id=existing.get("run_id"),
            metadata_path=existing.get("metadata_path") or payload.get("metadata_path"),
            latest_receipt_path=latest.get("path") or str(path or ""),
            latest_receipt_provenance=latest.get("provenance") or "receipt",
            source=existing.get("source") or "receipt",
        )
    command = clean_optional(payload.get("command"))
    automation_id = payload.get("automation_id")
    owner_label = payload.get("owner_label")
    if command == "automation-handoff":
        automation_id = automation_id or payload.get("label")
        owner_label = owner_label or "automation-handoff"
    return attribution_object(
        owner=payload.get("owner"),
        owner_label=owner_label,
        session_id=payload.get("session_id"),
        thread_id=payload.get("thread_id"),
        automation_id=automation_id,
        run_id=payload.get("run_id"),
        metadata_path=payload.get("metadata_path"),
        latest_receipt_path=str(path) if path else None,
        latest_receipt_provenance="receipt" if path else None,
        source="receipt",
    )


def unknown_attribution() -> dict[str, Any]:
    return attribution_object(source="unknown")


def inferred_attribution() -> dict[str, Any]:
    return attribution_object(source="inferred")


def render_attribution(attribution: dict[str, Any]) -> str:
    return (
        f"owner={attribution.get('owner') or '(unknown)'} "
        f"label={attribution.get('owner_label') or '(unknown)'} "
        f"session={attribution.get('session_id') or '(unknown)'} "
        f"thread={attribution.get('thread_id') or '(unknown)'} "
        f"automation={attribution.get('automation_id') or '(unknown)'} "
        f"source={attribution.get('source') or 'unknown'}"
    )


def artifact_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def state_base_dir() -> Path:
    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    if xdg_state_home:
        return Path(xdg_state_home).expanduser().resolve() / STATE_APP_DIR
    return Path.home().expanduser().resolve() / ".local" / "state" / STATE_APP_DIR


def repo_slug(repo: Path) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", repo.name).strip(".-")
    return slug or "repo"


def repo_identity(repo: Path) -> dict[str, Any]:
    root = str(repo.resolve())
    stable_id = hashlib.sha256(root.encode("utf-8")).hexdigest()
    return {
        "root": root,
        "id": stable_id[:16],
        "hash_algorithm": "sha256",
        "hash": stable_id,
    }


def sidecar_state(repo: Path | None = None) -> dict[str, Any]:
    base = state_base_dir()
    payload: dict[str, Any] = {
        "base_dir": str(base),
        "xdg_state_home": os.environ.get("XDG_STATE_HOME"),
    }
    if repo is None:
        return payload

    identity = repo_identity(repo)
    repo_dir = base / f"{repo_slug(repo)}-{identity['id']}"
    payload.update(
        {
            "repo": identity,
            "repo_state_dir": str(repo_dir),
            "available": repo_dir.exists(),
            "paths": {
                "runs_dir": str(repo_dir / "runs"),
                "receipts_dir": str(repo_dir / "receipts"),
                "review_artifacts_dir": str(repo_dir / "review-artifacts"),
                "docs_patch_proposals_dir": str(repo_dir / "docs-patch-proposals"),
                "task_packets_dir": str(repo_dir / "task-packets"),
                "automation_handoffs_dir": str(repo_dir / "automation-handoffs"),
                "quarantine_dir": str(repo_dir / "quarantine"),
                "status_json": str(repo_dir / "status.json"),
            },
            "created": False,
            "note": "Non-mutating commands report sidecar paths but do not create state directories. Use sidecar-init or --write-sidecar to create them explicitly.",
        }
    )
    return payload


def write_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def target_repo_writes(performed: bool, paths: list[str] | None = None, reason: str | None = None) -> dict[str, Any]:
    return {
        "performed": performed,
        "paths": paths or [],
        "reason": reason or ("explicit mutating command" if performed else "non-mutating command"),
    }


def sidecar_writes(performed: bool, paths: list[str] | None = None, reason: str | None = None) -> dict[str, Any]:
    return {
        "performed": performed,
        "paths": paths or [],
        "reason": reason or ("explicit sidecar write" if performed else "non-mutating command"),
    }


def ensure_sidecar(repo: Path, reason: str) -> tuple[dict[str, Any], list[str]]:
    before = sidecar_state(repo)
    repo_dir = Path(before["repo_state_dir"])
    created = not repo_dir.exists()
    paths = [repo_dir]
    for key in SIDECAR_DIR_KEYS:
        path = Path(before["paths"][key])
        path.mkdir(parents=True, exist_ok=True)
        paths.append(path)
    status_path = Path(before["paths"]["status_json"])
    status_payload = {
        "schema_version": 1,
        "repo": before["repo"],
        "kit": {
            "version": kit_version(),
            "entrypoint": str(CLI_ENTRYPOINT),
        },
        "paths": before["paths"],
        "created": created,
        "reason": reason,
        "updated_at": now(),
    }
    write_json_file(status_path, status_payload)
    paths.append(status_path)
    after = sidecar_state(repo)
    after["created"] = created
    after["note"] = "Sidecar directories are available for external agent artifacts."
    return after, [str(path) for path in paths]


def sidecar_init_payload(repo: Path) -> dict[str, Any]:
    state, paths = ensure_sidecar(repo, "sidecar-init")
    return {
        "schema_version": 1,
        "command": "sidecar-init",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False, reason="sidecar-init writes outside the target repo"),
        "sidecar_state": state,
        "sidecar_writes": sidecar_writes(True, paths=paths, reason="explicit sidecar-init command"),
        "exit_code": 0,
    }


def cli_metadata() -> dict[str, Any]:
    return {
        "name": PUBLIC_COMMAND,
        "internal_name": INTERNAL_PRODUCT_NAME,
        "version": kit_version(),
        "entrypoint": str(CLI_ENTRYPOINT),
        "invocation": str(CLI_ENTRYPOINT),
        "writes_target_repo_by_default": False,
        "mutating_commands": [
            "agent-self-heal --apply",
            "install",
            "setup",
            "self update",
            "target add",
            "target repair-source-clone --apply",
            "target update",
            "update",
            "update --global",
            "migrate-config",
        ],
        "sidecar_write_commands": [
            "sidecar-init",
            "agent-self-heal --apply",
            "automation-handoff",
            "agent-preflight --write-sidecar",
            "agent-doctor --write-sidecar",
            "orient --write-sidecar",
            "review-plan --write-sidecar",
            "docs-propose --write-sidecar",
            "onboarding-pr --write-sidecar",
            "task-packet --write-sidecar",
            "agent-task-packet-from-backlog --write-sidecar",
            "verify --write-sidecar",
        ],
        "state": sidecar_state(),
    }


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def short_git_ref(ref: str | None) -> str | None:
    if not ref:
        return None
    return ref[:12]


def workflow_source_root() -> Path:
    configured = os.environ.get("AGENT_WORKFLOW_KIT") or os.environ.get("WORKFLOW")
    if configured:
        return Path(configured).expanduser().resolve()
    return DEFAULT_WORKFLOW_SOURCE.expanduser().resolve()


def workflow_source_requested(root: Path | None = None) -> bool:
    if os.environ.get("AGENT_WORKFLOW_KIT") or os.environ.get("WORKFLOW"):
        return True
    return (root or workflow_source_root()).exists()


def checkout_status(root: Path, *, entrypoint: Path | None = None) -> dict[str, Any]:
    exists = root.exists()
    inside_git = exists and run_git(root, ["rev-parse", "--is-inside-work-tree"]).returncode == 0
    source_ref = git_text(root, ["rev-parse", "HEAD"]) if inside_git else None
    status_entries = git_lines(root, ["status", "--porcelain"]) if inside_git else []
    payload = {
        "root": str(root),
        "exists": exists,
        "source_ref": source_ref,
        "short_ref": short_git_ref(source_ref),
        "branch": git_text(root, ["branch", "--show-current"]) if inside_git else None,
        "remote": git_text(root, ["remote", "get-url", "origin"]) if inside_git else None,
        "is_git_checkout": inside_git,
        "dirty": bool(status_entries),
        "status_entries": status_entries,
    }
    if entrypoint is not None:
        payload["entrypoint"] = str(entrypoint)
    version_file = root / "VERSION"
    if version_file.exists():
        payload["version"] = version_file.read_text(encoding="utf-8").strip()
    return payload


def self_status_payload() -> dict[str, Any]:
    tool = checkout_status(ROOT, entrypoint=CLI_ENTRYPOINT)
    tool["version"] = kit_version()
    return {
        "schema_version": 1,
        "command": "self-status",
        "tool": tool,
        "workflow_source": checkout_status(workflow_source_root()),
        "target_repo_writes": target_repo_writes(False, reason="self status inspects only the global repo-contract-kit checkout"),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(),
        "exit_code": 0,
    }


def render_self_status(payload: dict[str, Any]) -> None:
    tool = payload["tool"]
    print(f"{PUBLIC_COMMAND} global tool:")
    print(f" - root: {tool['root']}")
    print(f" - version: {tool['version']}")
    print(f" - git checkout: {str(tool['is_git_checkout']).lower()}")
    print(f" - ref: {tool['short_ref'] or 'unknown'}")
    print(f" - branch: {tool['branch'] or '(detached or unknown)'}")
    print(f" - remote: {tool['remote'] or 'unknown'}")
    print(f" - dirty: {str(tool['dirty']).lower()}")
    if tool["status_entries"]:
        print(" - dirty entries:")
        for entry in tool["status_entries"]:
            print(f"   {entry}")
    workflow = payload.get("workflow_source") or {}
    if workflow.get("exists") or workflow.get("is_git_checkout"):
        print("optional workflow source checkout:")
        print(f" - root: {workflow.get('root') or 'unknown'}")
        print(f" - git checkout: {str(workflow.get('is_git_checkout', False)).lower()}")
        print(f" - ref: {workflow.get('short_ref') or 'unknown'}")
        print(f" - branch: {workflow.get('branch') or '(detached or unknown)'}")
        print(f" - remote: {workflow.get('remote') or 'unknown'}")
        print(f" - dirty: {str(workflow.get('dirty', False)).lower()}")
    if workflow.get("status_entries"):
        print(" - dirty entries:")
        for entry in workflow["status_entries"]:
            print(f"   {entry}")


def update_checkout(root: Path, ref: str, label: str) -> tuple[list[dict[str, Any]], dict[str, Any] | None, str | None, int]:
    before = checkout_status(root)
    if not before["exists"]:
        if label == "legacy workflow-source":
            return [], before, f"{label} checkout is missing; rerun install.sh --with-workflow to provision it for maintainer work.", 0
        return [], before, f"{label} checkout is missing; rerun install.sh to provision it.", 0
    if not before["is_git_checkout"]:
        return [], before, f"{label} root is not a git checkout: {root}", 2
    if before["dirty"]:
        return [], before, f"{label} checkout has local changes; self update refuses to overwrite them.", 2

    fetch = run_git(root, ["fetch", "--depth", "1", "origin", ref])
    steps = [
        {
            "label": f"fetch {label}",
            "command": f"git fetch --depth 1 origin {ref}",
            "returncode": fetch.returncode,
            "stdout": fetch.stdout,
            "stderr": fetch.stderr,
        }
    ]
    if fetch.returncode != 0:
        return steps, checkout_status(root), f"Failed to fetch requested ref for {label}.", fetch.returncode

    checkout = run_git(root, ["checkout", "-q", "--detach", "FETCH_HEAD"])
    steps.append(
        {
            "label": f"checkout {label}",
            "command": "git checkout -q --detach FETCH_HEAD",
            "returncode": checkout.returncode,
            "stdout": checkout.stdout,
            "stderr": checkout.stderr,
        }
    )
    error = f"Failed to switch {label} checkout to fetched ref." if checkout.returncode != 0 else None
    return steps, checkout_status(root), error, checkout.returncode


def self_update_payload(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    before = self_status_payload()["tool"]
    workflow_before = self_status_payload()["workflow_source"]
    payload: dict[str, Any] = {
        "schema_version": 1,
        "command": "self-update",
        "tool_before": before,
        "workflow_source_before": workflow_before,
        "ref": args.ref,
        "target_repo_writes": target_repo_writes(False, reason="self update writes only the global repo-contract-kit checkout"),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(),
        "steps": [],
        "warnings": [],
    }
    tool_steps, tool_after, tool_error, tool_exit = update_checkout(ROOT, args.ref, "repo-contract-kit")
    payload["steps"].extend(tool_steps)
    payload["tool_after"] = tool_after or self_status_payload()["tool"]
    if tool_error:
        payload["error"] = tool_error
        payload["exit_code"] = tool_exit
        return payload, tool_exit

    workflow_root = workflow_source_root()
    if workflow_source_requested(workflow_root):
        workflow_steps, workflow_after, workflow_error, workflow_exit = update_checkout(workflow_root, args.workflow_ref or args.ref, "legacy workflow-source")
        payload["steps"].extend(workflow_steps)
        payload["workflow_source_after"] = workflow_after or self_status_payload()["workflow_source"]
        if workflow_error:
            if workflow_exit == 0:
                payload["warnings"].append(workflow_error)
            else:
                payload["error"] = workflow_error
                payload["exit_code"] = workflow_exit
                return payload, workflow_exit
    else:
        payload["workflow_source_after"] = workflow_before
        payload["workflow_source_skipped"] = True
    payload["exit_code"] = 0
    return payload, 0


def render_self_update(payload: dict[str, Any]) -> None:
    before = payload["tool_before"]
    after = payload.get("tool_after") or before
    print(f"{PUBLIC_COMMAND} global update:")
    print(f" - root: {before['root']}")
    print(f" - ref: {before.get('short_ref') or 'unknown'} -> {after.get('short_ref') or 'unknown'}")
    workflow_before = payload.get("workflow_source_before") or {}
    workflow_after = payload.get("workflow_source_after") or workflow_before
    if workflow_before.get("exists") or workflow_after.get("exists") or workflow_before.get("is_git_checkout") or workflow_after.get("is_git_checkout"):
        print("optional workflow source update:")
        print(f" - root: {workflow_before.get('root') or workflow_after.get('root') or 'unknown'}")
        print(f" - ref: {workflow_before.get('short_ref') or 'unknown'} -> {workflow_after.get('short_ref') or 'unknown'}")
    for warning in payload.get("warnings", []):
        print(f" - warning: {warning}")
    if payload.get("error"):
        print(f" - error: {payload['error']}")
    for step in payload.get("steps", []):
        print(f" - {step['label']}: {'passed' if step['returncode'] == 0 else 'failed'}")


def require_git_repo(path: str) -> Path:
    repo = Path(path).expanduser().resolve()
    if not repo.exists():
        raise CliError(f"Repository path does not exist: {repo}")
    result = run_git(repo, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        raise CliError(f"Not a git repository: {repo}")
    return Path(result.stdout.strip()).resolve()


def git_lines(repo: Path, args: list[str]) -> list[str]:
    result = run_git(repo, args)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def git_text(repo: Path, args: list[str]) -> str:
    result = run_git(repo, args)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def shell_command(*parts: object) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def public_command(*parts: object) -> str:
    return shell_command(PUBLIC_COMMAND, *parts)


def git_ref_exists(repo: Path, ref: str) -> bool:
    if not ref:
        return False
    result = run_git(repo, ["show-ref", "--verify", "--quiet", ref])
    return result.returncode == 0


def load_install_module():
    install_path = SCRIPT_DIR / "install.py"
    if not install_path.exists():
        raise CliError(
            "onboarding-pr requires a full repo-contract-kit checkout with scripts/install.py; "
            "run it from the kit checkout, not an installed target copy.",
            exit_code=2,
        )
    spec = importlib.util.spec_from_file_location("repo_contract_kit_install", install_path)
    if spec is None or spec.loader is None:
        raise CliError(f"Unable to load installer helpers from {install_path}", exit_code=2)
    install_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(install_module)
    return install_module


def git_status_entries(repo: Path) -> list[dict[str, Any]]:
    result = run_git(repo, ["status", "--porcelain=v1", "--untracked-files=all"])
    if result.returncode != 0:
        return []
    entries = []
    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue
        code = raw_line[:2]
        path = raw_line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        entries.append({"code": code, "path": path})
    return entries


def git_worktree_metadata(repo: Path) -> dict[str, Any]:
    git_dir = git_text(repo, ["rev-parse", "--path-format=absolute", "--git-dir"])
    common_dir = git_text(repo, ["rev-parse", "--path-format=absolute", "--git-common-dir"])
    branch = git_text(repo, ["rev-parse", "--abbrev-ref", "HEAD"]) or "HEAD"
    return {
        "git_dir": git_dir,
        "git_common_dir": common_dir,
        "branch": branch,
        "detached": branch == "HEAD",
        "linked_worktree": bool(git_dir and common_dir and Path(git_dir).resolve() != Path(common_dir).resolve()),
    }


def parse_worktree_porcelain(output: str) -> list[dict[str, str]]:
    worktrees = []
    current: dict[str, str] | None = None
    for line in output.splitlines():
        if not line.strip():
            if current:
                worktrees.append(current)
                current = None
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            if current:
                worktrees.append(current)
            current = {"path": value}
        elif current is not None:
            current[key] = value
    if current:
        worktrees.append(current)
    return worktrees


def git_worktrees(repo: Path) -> list[dict[str, str]]:
    result = run_git(repo, ["worktree", "list", "--porcelain"])
    if result.returncode != 0:
        return []
    return parse_worktree_porcelain(result.stdout)


def primary_checkout(repo: Path) -> Path:
    common_dir = git_text(repo, ["rev-parse", "--path-format=absolute", "--git-common-dir"])
    common = Path(common_dir) if common_dir else None
    if common and common.name == ".git":
        return common.parent.resolve()
    return repo.resolve()


def path_matches_allowed(path: str, allowed_paths: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    for raw_pattern in allowed_paths:
        pattern = raw_pattern.strip().replace("\\", "/")
        if not pattern:
            continue
        if pattern.endswith("/"):
            if normalized.startswith(pattern):
                return True
            continue
        if normalized == pattern or fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def split_allowed_changes(entries: list[dict[str, Any]], allowed_paths: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    allowed = []
    disallowed = []
    for entry in entries:
        target = allowed if path_matches_allowed(entry["path"], allowed_paths) else disallowed
        target.append(entry)
    return allowed, disallowed


def changed_files(repo: Path, mode: str) -> list[str]:
    if mode == "staged":
        return git_lines(repo, ["diff", "--name-only", "--cached"])
    if mode == "working-tree":
        return sorted(
            set(
                git_lines(repo, ["diff", "--name-only", "--cached"])
                + git_lines(repo, ["diff", "--name-only"])
                + git_lines(repo, ["ls-files", "--others", "--exclude-standard"])
            )
        )

    files: list[str] = []
    for ref in ("origin/main", "origin/master"):
        base = run_git(repo, ["merge-base", "HEAD", ref])
        if base.returncode == 0 and base.stdout.strip():
            files = git_lines(repo, ["diff", "--name-only", f"{base.stdout.strip()}...HEAD"])
            if files:
                break
    if not files:
        files = git_lines(repo, ["diff", "--name-only", "HEAD~1..HEAD"])
    return sorted(set(files + changed_files(repo, "working-tree")))


def untracked_content_hashes(repo: Path, entries: list[dict[str, Any]]) -> list[dict[str, str]]:
    hashes: list[dict[str, str]] = []
    for entry in sorted(entries, key=lambda item: item["path"]):
        if entry["code"] != "??":
            continue
        relpath = entry["path"]
        path = repo / relpath
        if path.is_file():
            hashes.append({"path": relpath, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return hashes


def checkout_status_snapshot(repo: Path) -> dict[str, Any]:
    entries = sorted(git_status_entries(repo), key=lambda item: (item["path"], item["code"]))
    changed = sorted(entry["path"] for entry in entries)
    head = git_text(repo, ["rev-parse", "HEAD"])
    branch = git_text(repo, ["rev-parse", "--abbrev-ref", "HEAD"]) or "HEAD"
    tracked_diff = run_git(repo, ["diff", "--binary", "HEAD", "--"])
    diff_bytes = tracked_diff.stdout.encode("utf-8", "surrogateescape") if tracked_diff.returncode == 0 else b""
    untracked_hashes = untracked_content_hashes(repo, entries)

    digest = hashlib.sha256()
    digest.update(head.encode("utf-8", "surrogateescape"))
    digest.update(b"\0")
    for entry in entries:
        digest.update(f"{entry['code']}\0{entry['path']}\0".encode("utf-8", "surrogateescape"))
    digest.update(diff_bytes)
    for item in untracked_hashes:
        digest.update(f"{item['path']}\0{item['sha256']}\0".encode("utf-8", "surrogateescape"))
    state_hash = digest.hexdigest()

    return {
        "root": str(repo),
        "captured_at": now(),
        "head": head,
        "branch": branch,
        "dirty": bool(entries),
        "changed_files": changed,
        "status_entries": entries,
        "tracked_diff_sha256": hashlib.sha256(diff_bytes).hexdigest(),
        "untracked_content": untracked_hashes,
        "state_sha256": state_hash,
        "status_sha256": state_hash,
    }


def original_checkout_summary(repo: Path, automation_repo: Path) -> dict[str, Any]:
    snapshot = checkout_status_snapshot(repo)
    return {
        **snapshot,
        "same_as_repo": repo == automation_repo,
        "baseline": None,
        "baseline_comparison": None,
        "changed_since_baseline": None,
    }


def load_original_baseline(path: str) -> tuple[dict[str, Any] | None, str | None]:
    baseline_path = Path(path).expanduser()
    payload = read_json(baseline_path)
    if payload is None:
        return None, f"Original checkout baseline does not exist: {baseline_path}"
    if payload.get("_error"):
        return None, f"Original checkout baseline is not valid JSON: {baseline_path}: {payload['_error']}"
    original = payload.get("original_checkout")
    if not isinstance(original, dict):
        return None, f"Original checkout baseline is missing original_checkout: {baseline_path}"
    if not original.get("root") or not original.get("state_sha256"):
        return None, f"Original checkout baseline is missing root or state hash: {baseline_path}"
    baseline = dict(original)
    baseline["path"] = str(baseline_path)
    baseline["receipt_created_at"] = payload.get("created_at")
    return baseline, None


def compare_original_baseline(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    current_entries = {f"{entry['code']}\0{entry['path']}" for entry in current.get("status_entries", [])}
    baseline_entries = {f"{entry['code']}\0{entry['path']}" for entry in baseline.get("status_entries", [])}
    current_paths = set(current.get("changed_files", []))
    baseline_paths = set(baseline.get("changed_files", []))
    state_match = current.get("state_sha256") == baseline.get("state_sha256")
    return {
        "baseline_path": baseline.get("path"),
        "baseline_created_at": baseline.get("receipt_created_at") or baseline.get("captured_at"),
        "state_sha256_match": state_match,
        "head_match": current.get("head") == baseline.get("head"),
        "changed_since_baseline": not state_match,
        "new_changed_files": sorted(current_paths - baseline_paths),
        "removed_changed_files": sorted(baseline_paths - current_paths),
        "new_status_entries": sorted(current_entries - baseline_entries),
        "removed_status_entries": sorted(baseline_entries - current_entries),
    }


def normalize_status(value: str | None) -> str:
    status = (value or "").strip().lower()
    if status in DONE_STATUSES:
        return "done"
    if status in PARTIAL_STATUSES:
        return "partial"
    if status in OPEN_STATUSES:
        return "open"
    return status or "open"


def normalize_priority(value: str | None) -> str:
    priority = (value or "").strip().upper()
    return priority if priority in PRIORITY_ORDER else "P2"


def priority_rank(value: str | None) -> int:
    return PRIORITY_ORDER.get(normalize_priority(value), 99)


def source_relpath(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def discover_backlog_sources(repo: Path) -> dict[str, Any]:
    primary = [repo / candidate for candidate in BACKLOG_PRIMARY_CANDIDATES if (repo / candidate).exists()]
    mirrors = [repo / candidate for candidate in BACKLOG_MIRROR_CANDIDATES if (repo / candidate).exists()]
    selected = primary[0] if primary else None
    return {
        "selected": selected,
        "primary_candidates": [source_relpath(repo, path) for path in primary],
        "mirrors": [source_relpath(repo, path) for path in mirrors],
        "contract": {
            "markdown_checkbox": "- [ ] TASK-ID: title with optional priority/status text nearby",
            "csv_fields": ["id", "priority", "repo", "theme", "item", "status", "completion_note"],
            "status_values": sorted(DONE_STATUSES | OPEN_STATUSES | PARTIAL_STATUSES),
            "selection": "Use the first available primary source in priority order; split CSV views are treated as mirrors.",
        },
    }


def parse_csv_backlog(repo: Path, path: Path) -> dict[str, Any]:
    warnings: list[str] = []
    items: list[dict[str, Any]] = []
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            for line_index, row in enumerate(reader, start=2):
                item_id = (row.get("id") or row.get("task_id") or "").strip()
                title = (row.get("item") or row.get("title") or row.get("description") or "").strip()
                if not item_id:
                    warnings.append(f"{source_relpath(repo, path)}:{line_index} missing id")
                items.append(
                    {
                        "id": item_id or f"{source_relpath(repo, path)}:{line_index}",
                        "title": title,
                        "priority": normalize_priority(row.get("priority")),
                        "status": normalize_status(row.get("status")),
                        "repo": (row.get("repo") or "").strip(),
                        "theme": (row.get("theme") or "").strip(),
                        "source_path": source_relpath(repo, path),
                        "source_line": line_index,
                        "source_type": "csv",
                        "why": (row.get("why") or "").strip(),
                        "delivery_shape": (row.get("delivery_shape") or "").strip(),
                        "completion_note": (row.get("completion_note") or "").strip(),
                    }
                )
    except OSError as exc:
        warnings.append(f"{source_relpath(repo, path)} could not be read: {exc}")
        fields = []
    missing_fields = [field for field in ("id", "status") if field not in fields]
    for field in missing_fields:
        warnings.append(f"{source_relpath(repo, path)} missing recommended csv field: {field}")
    return {
        "path": source_relpath(repo, path),
        "type": "csv",
        "supported": True,
        "fieldnames": fields,
        "item_count": len(items),
        "warnings": warnings,
        "items": items,
    }


def parse_markdown_backlog(repo: Path, path: Path) -> dict[str, Any]:
    warnings: list[str] = []
    items: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\s*[-*]\s+\[(?P<mark>[ xX-])\]\s+"
        r"(?:(?P<id>[A-Z][A-Z0-9_-]+-\d+)\s*[:|-]\s*)?"
        r"(?P<title>.+?)\s*$"
    )
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        warnings.append(f"{source_relpath(repo, path)} could not be read: {exc}")
        lines = []
    for line_index, line in enumerate(lines, start=1):
        match = pattern.match(line)
        if not match:
            continue
        mark = match.group("mark")
        item_id = match.group("id") or ""
        title = match.group("title").strip()
        if not item_id:
            warnings.append(f"{source_relpath(repo, path)}:{line_index} checkbox item missing id")
        status = "done" if mark.lower() == "x" else "partial" if mark == "-" else "open"
        priority_match = re.search(r"\b(P[0-3])\b", title)
        items.append(
            {
                "id": item_id or f"{source_relpath(repo, path)}:{line_index}",
                "title": title,
                "priority": normalize_priority(priority_match.group(1) if priority_match else None),
                "status": status,
                "repo": "",
                "theme": "",
                "source_path": source_relpath(repo, path),
                "source_line": line_index,
                "source_type": "markdown",
                "why": "",
                "delivery_shape": "",
                "completion_note": "",
            }
        )
    return {
        "path": source_relpath(repo, path),
        "type": "markdown",
        "supported": True,
        "item_count": len(items),
        "warnings": warnings,
        "items": items,
    }


def parse_backlog_source(repo: Path, path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".csv":
        return parse_csv_backlog(repo, path)
    if path.suffix.lower() in {".md", ".markdown"}:
        return parse_markdown_backlog(repo, path)
    return {
        "path": source_relpath(repo, path),
        "type": path.suffix.lstrip(".") or "unknown",
        "supported": False,
        "item_count": 0,
        "warnings": [f"Unsupported backlog source type: {source_relpath(repo, path)}"],
        "items": [],
    }


def backlog_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"total": len(items), "open": 0, "partial": 0, "done": 0, "other": 0}
    for item in items:
        status = item.get("status")
        if status in counts:
            counts[status] += 1
        else:
            counts["other"] += 1
    return counts


def duplicate_backlog_ids(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        item_id = item.get("id") or ""
        if not item_id or ":" in item_id and item_id.endswith(str(item.get("source_line"))):
            continue
        seen.setdefault(item_id, []).append(item)
    duplicates = []
    for item_id, matches in sorted(seen.items()):
        if len(matches) > 1:
            duplicates.append(
                {
                    "id": item_id,
                    "locations": [f"{item['source_path']}:{item['source_line']}" for item in matches],
                }
            )
    return duplicates


def build_backlog_report(repo: Path, include_items: bool = False) -> dict[str, Any]:
    discovery = discover_backlog_sources(repo)
    selected = discovery["selected"]
    source_report = parse_backlog_source(repo, selected) if selected else None
    items = list(source_report["items"]) if source_report else []
    duplicates = duplicate_backlog_ids(items)
    warnings = []
    if not selected:
        warnings.append("No supported backlog source found.")
    if source_report:
        warnings.extend(source_report.get("warnings") or [])
    if duplicates:
        warnings.append("Duplicate backlog ids found.")
    open_items = [item for item in items if item.get("status") != "done"]
    open_items.sort(key=lambda item: (priority_rank(item.get("priority")), 0 if item.get("status") == "partial" else 1, item.get("id") or ""))
    payload = {
        "schema_version": 1,
        "command": "backlog-status",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "source_contract": discovery["contract"],
        "selected_source": source_relpath(repo, selected) if selected else None,
        "primary_candidates": discovery["primary_candidates"],
        "mirror_sources": discovery["mirrors"],
        "counts": backlog_counts(items),
        "open_by_priority": {
            priority: sum(1 for item in open_items if item.get("priority") == priority)
            for priority in sorted(PRIORITY_ORDER)
        },
        "duplicates": duplicates,
        "warnings": warnings,
        "next_open_item": open_items[0] if open_items else None,
        "open_items": open_items[:25],
        "check": {
            "passed": bool(selected) and not duplicates and not [warning for warning in warnings if "missing id" in warning or "missing recommended" in warning],
            "errors": [],
        },
    }
    if not selected:
        payload["check"]["errors"].append("no-backlog-source")
    if duplicates:
        payload["check"]["errors"].append("duplicate-ids")
    if source_report and any("missing id" in warning for warning in source_report.get("warnings", [])):
        payload["check"]["errors"].append("missing-ids")
    if source_report and any("missing recommended" in warning for warning in source_report.get("warnings", [])):
        payload["check"]["errors"].append("missing-fields")
    if include_items:
        payload["items"] = items
    return payload


def active_task_summary(repo: Path) -> dict[str, Any]:
    task_dir = repo / ".agent-workflows" / "tasks"
    active = []
    if task_dir.exists():
        for path in sorted(task_dir.glob("*.json")):
            payload = read_json(path)
            if isinstance(payload, dict) and payload.get("status") == "in-progress":
                active.append(
                    {
                        "task_id": payload.get("task_id") or payload.get("id") or path.stem,
                        "scope": payload.get("scope") or [],
                        "worktree": payload.get("worktree"),
                        "metadata_path": source_relpath(repo, path),
                    }
                )
    return {"active_task_count": len(active), "active_tasks": active}


def agent_next_payload(repo: Path) -> dict[str, Any]:
    status = status_payload(repo)
    backlog = build_backlog_report(repo, include_items=False)
    tasks = active_task_summary(repo)
    selected = backlog.get("next_open_item")
    notes: list[str] = []
    if status["git"]["dirty"]:
        notes.append("Working tree is dirty; preserve unrelated changes before write-capable work.")
    if tasks["active_task_count"]:
        notes.append("Active task metadata exists; inspect overlap before preparing another writer.")
    if not selected:
        notes.append("No open backlog item was selected from the current source contract.")
    recommended_commands = [
        "make agent-task-status",
        "make backlog-status",
    ]
    if selected:
        recommended_commands.append(f"make agent-task-packet-from-backlog BACKLOG_ID={selected['id']}")
    payload = {
        "schema_version": 1,
        "command": "agent-next",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "status": {
            "dirty": status["git"]["dirty"],
            "changed_file_count": len(status["git"]["changed_files"]),
            "installed": status["install"]["installed"],
        },
        "backlog": {
            "selected_source": backlog["selected_source"],
            "counts": backlog["counts"],
            "open_by_priority": backlog["open_by_priority"],
            "warnings": backlog["warnings"],
        },
        "task_status": tasks,
        "selected_item": selected,
        "recommended_commands": recommended_commands,
        "notes": notes,
    }
    return payload


def dirty_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    tracked = []
    untracked = []
    staged = []
    unstaged = []
    for entry in entries:
        code = entry["code"]
        path = entry["path"]
        if code == "??":
            untracked.append(path)
            continue
        tracked.append(path)
        if code[0] != " ":
            staged.append(path)
        if len(code) > 1 and code[1] != " ":
            unstaged.append(path)
    return {
        "dirty": bool(entries),
        "count": len(entries),
        "tracked_count": len(set(tracked)),
        "untracked_count": len(set(untracked)),
        "staged_count": len(set(staged)),
        "unstaged_count": len(set(unstaged)),
        "entries": entries,
        "tracked_files": sorted(set(tracked)),
        "untracked_files": sorted(set(untracked)),
        "staged_files": sorted(set(staged)),
        "unstaged_files": sorted(set(unstaged)),
    }


def worktree_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"available": False, "dirty": None, "entries": [], "error": "worktree path is missing"}
    result = run_git(path, ["status", "--porcelain=v1", "--untracked-files=all"])
    if result.returncode != 0:
        return {
            "available": False,
            "dirty": None,
            "entries": [],
            "error": result.stderr.strip() or result.stdout.strip() or "git status failed",
        }
    entries = []
    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue
        code = raw_line[:2]
        path_value = raw_line[3:].strip()
        if " -> " in path_value:
            path_value = path_value.split(" -> ", 1)[1].strip()
        entries.append({"code": code, "path": path_value})
    return {"available": True, "dirty": bool(entries), "entries": entries, "error": None}


def task_metadata_items(repo: Path) -> list[dict[str, Any]]:
    task_dir = repo / ".agent-workflows" / "tasks"
    if not task_dir.exists():
        return []
    items = []
    for path in sorted(task_dir.glob("*.json")):
        payload = read_json(path)
        if isinstance(payload, dict):
            payload["_metadata_path"] = source_relpath(repo, path)
            items.append(payload)
    return items


def preflight_worktrees(repo: Path) -> list[dict[str, Any]]:
    primary = primary_checkout(repo)
    items = []
    for raw in git_worktrees(primary):
        path = Path(raw["path"]).resolve()
        status = worktree_status(path)
        branch = raw.get("branch", "")
        items.append(
            {
                "path": str(path),
                "primary": path == primary,
                "current": path == repo.resolve(),
                "branch": branch,
                "head": raw.get("HEAD", ""),
                "detached": "detached" in raw or not branch,
                "dirty": status["dirty"],
                "changed_count": len(status["entries"]),
                "status_entries": status["entries"],
                "status_error": status["error"],
            }
        )
    return items


def preflight_tasks(repo: Path, worktrees: list[dict[str, Any]]) -> dict[str, Any]:
    primary = primary_checkout(repo)
    status_by_path = {item["path"]: item for item in worktrees}
    tasks = []
    for task in task_metadata_items(primary):
        worktree_value = str(task.get("worktree") or "").strip()
        worktree_path = str(Path(worktree_value).expanduser().resolve()) if worktree_value else ""
        worktree = status_by_path.get(worktree_path)
        status = task.get("status") or "unknown"
        scope = task.get("scope") or []
        warnings = []
        if status == "in-progress" and not scope:
            warnings.append("active task has unknown scope")
        if worktree_value and not Path(worktree_value).expanduser().exists():
            warnings.append("worktree path is missing")
        if worktree and worktree.get("dirty"):
            warnings.append("task worktree is dirty")
        tasks.append(
            {
                "task_id": task.get("task_id") or task.get("id") or Path(task["_metadata_path"]).stem,
                "status": status,
                "run_id": task.get("run_id"),
                "owner": task.get("owner"),
                "owner_label": task.get("owner_label"),
                "session_id": task.get("session_id"),
                "thread_id": task.get("thread_id"),
                "automation_id": task.get("automation_id"),
                "attribution": attribution_from_task(task),
                "scope": scope,
                "worktree": worktree_path,
                "worktree_registered": bool(worktree),
                "worktree_dirty": worktree.get("dirty") if worktree else None,
                "final_receipt": task.get("final_receipt"),
                "metadata_path": task["_metadata_path"],
                "warnings": warnings,
            }
        )
    active = [task for task in tasks if task["status"] == "in-progress"]
    terminal = [task for task in tasks if task["status"] in DONE_STATUSES or task["status"] in {"blocked", "abandoned"}]
    return {
        "count": len(tasks),
        "active_count": len(active),
        "terminal_count": len(terminal),
        "dirty_worktree_count": len([task for task in tasks if task.get("worktree_dirty")]),
        "unknown_scope_count": len([task for task in active if not task.get("scope")]),
        "missing_worktree_count": len(
            [task for task in tasks if task.get("worktree") and not Path(task["worktree"]).exists()]
        ),
        "items": tasks,
    }


def add_worktree_attribution(worktrees: list[dict[str, Any]], tasks: dict[str, Any]) -> list[dict[str, Any]]:
    by_path = {
        item.get("worktree"): item.get("attribution")
        for item in tasks.get("items", [])
        if item.get("worktree") and isinstance(item.get("attribution"), dict)
    }
    for item in worktrees:
        if item.get("primary") or item.get("current"):
            item["attribution"] = unknown_attribution()
        else:
            item["attribution"] = by_path.get(item.get("path")) or inferred_attribution()
    return worktrees


def preflight_sidecar_summary(state: dict[str, Any]) -> dict[str, Any]:
    paths = state.get("paths") or {}
    directories = {}
    for key in SIDECAR_DIR_KEYS:
        raw_path = paths.get(key)
        path = Path(raw_path) if raw_path else None
        if path and path.exists():
            directories[key] = {"path": str(path), "exists": True, "entry_count": sum(1 for _ in path.iterdir())}
        else:
            directories[key] = {"path": str(path) if path else "", "exists": False, "entry_count": 0}
    status_path = Path(paths["status_json"]) if paths.get("status_json") else None
    return {
        "available": bool(state.get("available")),
        "repo_state_dir": state.get("repo_state_dir"),
        "directories": directories,
        "status_json_exists": bool(status_path and status_path.exists()),
    }


def preflight_recommendations(blockers: list[str], warnings: list[str], payload: dict[str, Any]) -> list[str]:
    commands = ["make agent-task-status", "make backlog-status", "make agent-next"]
    if payload["dirty"]["dirty"]:
        commands.append("git status --short")
        commands.append(
            "Preserve current changes: identify the owner from attribution/receipts, then get explicit closeout or handoff before changing the dirty state; use DIRTY_PRIMARY_BASELINE=1 only when that risk is intentional."
        )
    if payload["tasks"]["dirty_worktree_count"] or payload["tasks"]["missing_worktree_count"]:
        commands.append("make agent-task-closeout")
        commands.append("make agent-task-cleanup")
    if payload["tasks"]["unknown_scope_count"]:
        commands.append("make agent-task-status TASK_STATUS_STRICT=1")
    if not payload["sidecar"]["available"]:
        commands.append("python3 scripts/repo_contract_kit.py sidecar-init --repo . --json")
    if not blockers and not warnings:
        commands.append("make agent-task-prepare TASK=<id> SCOPE=<paths>")
    return commands


def preflight_receipt_blockers(state: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    paths = state.get("paths") or {}
    receipt_paths: list[tuple[Path, str, str]] = []
    if paths.get("receipts_dir"):
        receipt_paths.append((Path(paths["receipts_dir"]), "sidecar-receipts", "*.json"))
    if paths.get("automation_handoffs_dir"):
        receipt_paths.append((Path(paths["automation_handoffs_dir"]), "sidecar-automation-handoffs", "*.json"))
    receipts = scan_json_receipts(receipt_paths) if receipt_paths else {"latest": {}, "count": 0, "warnings": [], "categories": {}, "items": []}
    blockers = []
    for category, message in (
        ("automation_baseline", "Latest automation baseline receipt was blocked."),
        ("automation_handoff", "Latest automation handoff receipt was blocked."),
    ):
        latest = (receipts.get("latest") or {}).get(category)
        if latest and latest.get("result") == "blocked":
            blockers.append(
                {
                    "code": f"{category}_blocked",
                    "message": message,
                    "receipt": latest.get("path"),
                    "attribution": latest.get("attribution") or unknown_attribution(),
                }
            )
    return blockers, receipts


def write_preflight_sidecar(repo: Path, payload: dict[str, Any]) -> dict[str, Any]:
    reason = f"{payload['command']} --write-sidecar"
    state, init_paths = ensure_sidecar(repo, reason)
    receipt_path = Path(state["paths"]["receipts_dir"]) / f"{artifact_stamp()}-{payload['command']}.json"
    payload["sidecar_state"] = state
    payload["sidecar"] = preflight_sidecar_summary(state)
    payload["receipt"] = {"path": str(receipt_path)}
    payload["sidecar_writes"] = sidecar_writes(True, paths=init_paths + [str(receipt_path)], reason=reason)
    write_json_file(receipt_path, payload)
    return payload


def agent_preflight_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    entries = git_status_entries(repo)
    worktrees = preflight_worktrees(repo)
    tasks = preflight_tasks(repo, worktrees)
    worktrees = add_worktree_attribution(worktrees, tasks)
    state = sidecar_state(repo)
    receipt_blockers, receipt_report = preflight_receipt_blockers(state)
    dirty = dirty_summary(entries)
    dirty["attribution"] = unknown_attribution()
    blockers = []
    warnings = []
    blocker_details: list[dict[str, Any]] = []
    warning_details: list[dict[str, Any]] = []

    if entries:
        blockers.append("Current checkout has uncommitted changes.")
        blocker_details.append({"code": "dirty_checkout", "message": "Current checkout has uncommitted changes.", "attribution": dirty["attribution"], "count": dirty["count"]})
    dirty_siblings = [item for item in worktrees if item.get("dirty") and not item.get("current")]
    if dirty_siblings:
        blockers.append("Registered sibling worktrees have uncommitted changes.")
        blocker_details.extend(
            {
                "code": "dirty_sibling_worktree",
                "message": "Registered sibling worktree has uncommitted changes.",
                "path": item.get("path"),
                "branch": item.get("branch"),
                "attribution": item.get("attribution") or unknown_attribution(),
            }
            for item in dirty_siblings
        )
    if tasks["missing_worktree_count"]:
        blockers.append("Task metadata references missing worktrees.")
        blocker_details.extend(
            {
                "code": "missing_worktree",
                "message": "Task metadata references a missing worktree.",
                "task_id": task.get("task_id"),
                "worktree": task.get("worktree"),
                "attribution": task.get("attribution") or unknown_attribution(),
            }
            for task in tasks["items"]
            if task.get("worktree") and not Path(task["worktree"]).exists()
        )
    for detail in receipt_blockers:
        blockers.append(detail["message"])
        blocker_details.append(detail)
    if tasks["unknown_scope_count"]:
        warnings.append("Active task metadata has unknown scope.")
        warning_details.extend(
            {
                "code": "unknown_scope",
                "message": "Active task metadata has unknown scope.",
                "task_id": task.get("task_id"),
                "attribution": task.get("attribution") or unknown_attribution(),
            }
            for task in tasks["items"]
            if task.get("status") == "in-progress" and not task.get("scope")
        )
    if tasks["active_count"]:
        warnings.append("Active task metadata exists; inspect overlap before starting another writer.")
        warning_details.extend(
            {
                "code": "active_task",
                "message": "Active task metadata exists; inspect overlap before starting another writer.",
                "task_id": task.get("task_id"),
                "attribution": task.get("attribution") or unknown_attribution(),
            }
            for task in tasks["items"]
            if task.get("status") == "in-progress"
        )

    payload: dict[str, Any] = {
        "schema_version": 1,
        "command": args.command,
        "repo": str(repo),
        "created_at": now(),
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False, reason="non-mutating command"),
        "sidecar_state": state,
        "dirty": dirty,
        "worktrees": {
            "registered_count": len(worktrees),
            "dirty_count": len([item for item in worktrees if item.get("dirty")]),
            "items": worktrees,
        },
        "tasks": tasks,
        "receipts": receipt_report,
        "receipt_blockers": receipt_blockers,
        "sidecar": preflight_sidecar_summary(state),
        "blockers": blockers,
        "blocker_details": blocker_details,
        "warnings": warnings,
        "warning_details": warning_details,
        "strict": args.strict,
    }
    payload["recommendations"] = preflight_recommendations(blockers, warnings, payload)
    exit_code = 1 if args.strict and blockers else 0
    payload["result"] = "blocked" if blockers else "passed"
    payload["exit_code"] = exit_code
    if args.write_sidecar:
        payload = write_preflight_sidecar(repo, payload)
    return payload, exit_code


def self_heal_allowed_path_args(args: argparse.Namespace) -> list[str]:
    values: list[str] = []
    for value in args.allow_path or []:
        values.extend(part.strip() for part in value.split(",") if part.strip())
    return values


def self_heal_is_generated_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized in SELF_HEAL_GENERATED_EXACT_PATHS or any(
        normalized.startswith(prefix) for prefix in SELF_HEAL_GENERATED_PREFIXES
    )


def self_heal_exact_operator_scope(path: str, allowed_paths: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized == item.strip().replace("\\", "/") for item in allowed_paths if item.strip())


def self_heal_tracked_change_report(entries: list[dict[str, Any]], allowed_paths: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    allowed = []
    blocked = []
    for entry in entries:
        if entry["code"] == "??":
            continue
        if self_heal_is_generated_path(entry["path"]) and self_heal_exact_operator_scope(entry["path"], allowed_paths):
            allowed.append(
                {
                    **entry,
                    "reason": "tracked generated path was explicitly operator-scoped",
                }
            )
        else:
            blocked.append(
                {
                    **entry,
                    "reason": "tracked source changes are outside guarded self-heal scope",
                }
            )
    return allowed, blocked


def self_heal_untracked_report(entries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    recognized = []
    unrecognized = []
    for entry in entries:
        if entry["code"] != "??":
            continue
        target = recognized if self_heal_is_generated_path(entry["path"]) else unrecognized
        target.append(entry)
    return recognized, unrecognized


def process_is_running(pid: object) -> bool:
    try:
        value = int(pid)
    except (TypeError, ValueError):
        return False
    if value <= 0:
        return False
    try:
        os.kill(value, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def self_heal_stale_task_metadata(repo: Path) -> list[dict[str, Any]]:
    task_dir = repo / ".agent-workflows" / "tasks"
    candidates = []
    if not task_dir.exists():
        return candidates
    for path in sorted(task_dir.glob("*.json")):
        payload = read_json(path)
        if not isinstance(payload, dict):
            continue
        status = str(payload.get("status") or "").strip().lower()
        worktree_value = str(payload.get("worktree") or "").strip()
        worktree_exists = bool(worktree_value and Path(worktree_value).expanduser().exists())
        if status in SELF_HEAL_TERMINAL_STATUSES and not worktree_exists:
            candidates.append(
                {
                    "action": "quarantine-stale-task-metadata",
                    "path": source_relpath(repo, path),
                    "task_id": payload.get("task_id") or payload.get("id") or path.stem,
                    "status": status,
                    "worktree": worktree_value,
                    "reason": "terminal task metadata no longer references an existing worktree",
                }
            )
    return candidates


def self_heal_stale_prepare_lock(repo: Path) -> list[dict[str, Any]]:
    path = repo / ".agent-workflows" / "tasks" / ".prepare.lock"
    if not path.exists():
        return []
    payload = read_json(path)
    pid = payload.get("pid") if isinstance(payload, dict) else None
    if process_is_running(pid):
        return []
    return [
        {
            "action": "quarantine-stale-prepare-lock",
            "path": source_relpath(repo, path),
            "pid": pid,
            "reason": "prepare lock PID is absent or no longer running",
        }
    ]


def self_heal_sidecar_needs_init(sidecar: dict[str, Any]) -> bool:
    if not sidecar.get("available"):
        return True
    paths = sidecar.get("paths") or {}
    for key in SIDECAR_DIR_KEYS:
        raw_path = paths.get(key)
        if not raw_path or not Path(raw_path).is_dir():
            return True
    status_path = paths.get("status_json")
    return not bool(status_path and Path(status_path).is_file())


def self_heal_plan(args: argparse.Namespace, repo: Path, sidecar: dict[str, Any]) -> dict[str, Any]:
    entries = git_status_entries(repo)
    allowed_paths = self_heal_allowed_path_args(args)
    allowed_tracked, blocked_tracked = self_heal_tracked_change_report(entries, allowed_paths)
    recognized_untracked, unrecognized_untracked = self_heal_untracked_report(entries)
    actions = []
    if self_heal_sidecar_needs_init(sidecar):
        actions.append(
            {
                "action": "sidecar-init",
                "target": sidecar.get("repo_state_dir"),
                "reason": "sidecar state directory is not initialized",
            }
        )
    actions.extend(self_heal_stale_task_metadata(repo))
    actions.extend(self_heal_stale_prepare_lock(repo))
    blockers = []
    if blocked_tracked:
        blockers.append("Tracked source changes are outside guarded self-heal scope.")
    warnings = []
    if unrecognized_untracked:
        warnings.append("Unrecognized untracked files are outside generated-state allowlist; self-heal will not delete them.")
    return {
        "status_entries": entries,
        "allowed_paths": allowed_paths,
        "allowed_tracked_changes": allowed_tracked,
        "blocked_tracked_changes": blocked_tracked,
        "recognized_untracked_generated": recognized_untracked,
        "unrecognized_untracked": unrecognized_untracked,
        "actions": actions,
        "blockers": blockers,
        "warnings": warnings,
    }


def quarantine_target_path(quarantine_root: Path, relpath: str) -> Path:
    safe_parts = [part for part in Path(relpath).parts if part not in ("", ".", "..")]
    return quarantine_root.joinpath(*safe_parts)


def apply_self_heal_actions(repo: Path, state: dict[str, Any], actions: list[dict[str, Any]], stamp: str) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    applied = []
    target_paths = []
    sidecar_paths = []
    quarantine_root = Path(state["paths"]["quarantine_dir"]) / stamp
    for action in actions:
        if action["action"] == "sidecar-init":
            continue
        relpath = action["path"]
        source = repo / relpath
        if not source.exists():
            skipped = {**action, "applied": False, "skip_reason": "source path no longer exists"}
            applied.append(skipped)
            continue
        destination = quarantine_target_path(quarantine_root, relpath)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        target_paths.append(relpath)
        sidecar_paths.append(str(destination))
        applied.append({**action, "applied": True, "quarantine_path": str(destination)})
    if quarantine_root.exists():
        sidecar_paths.append(str(quarantine_root))
    return applied, target_paths, sidecar_paths


def write_self_heal_receipt(
    repo: Path,
    payload: dict[str, Any],
    state: dict[str, Any],
    init_paths: list[str],
    sidecar_paths: list[str],
    stamp: str,
) -> dict[str, Any]:
    receipt_path = Path(state["paths"]["receipts_dir"]) / f"{stamp}-agent-self-heal.json"
    payload["receipt"] = {"path": str(receipt_path)}
    payload["sidecar_state"] = state
    payload["sidecar_writes"] = sidecar_writes(
        True,
        paths=sorted(set(init_paths + sidecar_paths + [str(receipt_path)])),
        reason="agent-self-heal --apply",
    )
    write_json_file(receipt_path, payload)
    return payload


def agent_self_heal_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    apply = bool(args.apply)
    before_sidecar = sidecar_state(repo)
    before_checkout = checkout_status_snapshot(repo)
    plan = self_heal_plan(args, repo, before_sidecar)
    exit_code = 1 if apply and plan["blockers"] else 0
    payload: dict[str, Any] = {
        "schema_version": 1,
        "command": "agent-self-heal",
        "repo": str(repo),
        "created_at": now(),
        "apply": apply,
        "target_repo_writes": target_repo_writes(False, reason="preview/no-write default" if not apply else "blocked before target writes"),
        "sidecar_writes": sidecar_writes(False, reason="preview/no-write default" if not apply else "blocked before sidecar write"),
        "sidecar_state": before_sidecar,
        "receipt": None,
        "before": {
            "checkout": before_checkout,
            "sidecar": before_sidecar,
        },
        "after": None,
        "plan": plan,
        "actions": plan["actions"],
        "applied_actions": [],
        "blockers": plan["blockers"],
        "warnings": plan["warnings"],
        "result": "blocked" if apply and plan["blockers"] else ("applied" if apply else "preview"),
        "exit_code": exit_code,
        "notes": [
            "Preview mode is the default and performs no writes.",
            "Self-heal quarantines generated state only; it does not stash, reset, delete source files, or remove task worktrees.",
        ],
    }
    if not apply or plan["blockers"]:
        return payload, exit_code

    stamp = artifact_stamp()
    state, init_paths = ensure_sidecar(repo, "agent-self-heal --apply")
    applied_actions, target_paths, sidecar_paths = apply_self_heal_actions(repo, state, plan["actions"], stamp)
    if any(action["action"] == "sidecar-init" for action in plan["actions"]):
        applied_actions.insert(
            0,
            {
                "action": "sidecar-init",
                "applied": True,
                "paths": init_paths,
                "reason": "sidecar state directory was initialized",
            },
        )
    payload["applied_actions"] = applied_actions
    payload["target_repo_writes"] = target_repo_writes(
        bool(target_paths),
        paths=target_paths,
        reason="quarantined generated-state files" if target_paths else "no target repo generated files needed quarantine",
    )
    payload["after"] = {
        "checkout": checkout_status_snapshot(repo),
        "sidecar": sidecar_state(repo),
    }
    payload = write_self_heal_receipt(repo, payload, state, init_paths, sidecar_paths, stamp)
    return payload, payload["exit_code"]


def backlog_item_by_id(repo: Path, backlog_id: str) -> dict[str, Any] | None:
    report = build_backlog_report(repo, include_items=True)
    for item in report.get("items", []):
        if (item.get("id") or "").lower() == backlog_id.lower():
            return item
    return None


def install_state(repo: Path) -> dict[str, Any]:
    receipt = read_json(repo / ".doc-contract-kit" / "install.json")
    manifest = read_json(repo / ".doc-contract-kit" / "manifest.json")
    receipt_valid = isinstance(receipt, dict) and "_error" not in receipt
    manifest_valid = isinstance(manifest, dict) and "_error" not in manifest
    files = manifest.get("files", []) if manifest_valid else []
    managed_status = kit_status.managed_file_status(repo, manifest) if manifest_valid else None
    prompt_snapshot = kit_status.snapshot_from_install(receipt, manifest) if receipt_valid else None

    return {
        "installed": receipt_valid,
        "receipt_present": receipt is not None,
        "receipt_error": receipt.get("_error") if isinstance(receipt, dict) and "_error" in receipt else None,
        "manifest_present": manifest is not None,
        "manifest_error": manifest.get("_error") if isinstance(manifest, dict) and "_error" in manifest else None,
        "kit_version": (receipt or {}).get("source_version") or (receipt or {}).get("kit_version") if receipt_valid else None,
        "source_ref": (receipt or {}).get("source_ref")
        or (receipt or {}).get("source_commits", {}).get("repo-contract-kit")
        if receipt_valid
        else None,
        "preset": (receipt or {}).get("preset") if receipt_valid else None,
        "profiles": (receipt or {}).get("profiles", []) if receipt_valid else [],
        "runtime_adapters": (receipt or {}).get("runtime_adapters", []) if receipt_valid else [],
        "prompt_snapshot": prompt_snapshot,
        "managed_file_count": sum(1 for item in files if isinstance(item, dict) and item.get("managed")),
        "target_owned_file_count": sum(1 for item in files if isinstance(item, dict) and item.get("owner") == "target"),
        "managed_file_status": managed_status,
        "makefile_boundary": kit_status.makefile_boundary_status(repo, manifest) if manifest_valid else None,
    }


def status_payload(repo: Path) -> dict[str, Any]:
    changed = changed_files(repo, "working-tree")
    local_kit = kit_status.local_kit_state(ROOT)
    return {
        "schema_version": 1,
        "command": "status",
        "cli": cli_metadata(),
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "git": {
            "root": str(repo),
            "dirty": bool(changed),
            "changed_files": changed,
        },
        "install": install_state(repo),
        "target_version": read_text(repo / "VERSION"),
        "local_kit": {
            "root": str(ROOT),
            "version": local_kit["version"],
            "source_ref": local_kit["source_ref"],
            "prompt_snapshot": local_kit["prompt_snapshot"],
        },
    }


def config_for(repo: Path, config: str) -> dict[str, Any]:
    config_path = Path(config).expanduser()
    if not config_path.is_absolute():
        config_path = repo / config_path
    return check_doc_impact.load_config(config_path)


def doc_impact_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    config = config_for(repo, args.config)
    if args.changed_files:
        files = sorted(set(check_doc_impact.normalize_path(path) for path in args.changed_files))
    elif args.staged:
        files = changed_files(repo, "staged")
    elif args.working_tree:
        files = changed_files(repo, "working-tree")
    else:
        files = changed_files(repo, "branch")

    no_docs_declaration = bool(args.no_docs_needed and args.no_docs_needed.strip())
    evaluation = check_doc_impact.evaluate(files, config, no_docs_declaration)
    categories = [
        {
            "category": category,
            "changed_files": sorted(paths),
            "suggested_doc_paths": config["category_doc_paths"].get(category, config["doc_paths"]),
            "covered": category in evaluation.covered_categories,
        }
        for category, paths in sorted(evaluation.categories.items())
    ]
    exit_code = 1 if evaluation.failed else 0
    payload = {
        "schema_version": 1,
        "command": "doc-impact",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "changed_files": evaluation.changed_files,
        "docs_changed": evaluation.docs_changed,
        "categories": categories,
        "missing_categories": sorted(evaluation.missing_categories),
        "no_docs_declaration": no_docs_declaration,
        "result": "missing-docs" if evaluation.failed else "covered-or-no-impact",
        "exit_code": exit_code,
    }
    return payload, exit_code


def changed_files_from_args(args: argparse.Namespace, repo: Path) -> list[str]:
    if getattr(args, "changed_files", None):
        return sorted(
            {
                normalized
                for path in args.changed_files
                if (normalized := goal_check.normalize_changed_path(repo, path))
            }
        )
    if getattr(args, "staged", False):
        return changed_files(repo, "staged")
    if getattr(args, "working_tree", False):
        return changed_files(repo, "working-tree")
    return changed_files(repo, "branch")


def goal_check_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    files = changed_files_from_args(args, repo)
    payload = goal_check.build_goal_check_report(repo, files, args.config)
    payload.update(
        {
            "target_repo_writes": target_repo_writes(False),
            "sidecar_writes": sidecar_writes(False),
            "sidecar_state": sidecar_state(repo),
        }
    )
    return payload, int(payload.get("exit_code") or 0)


def bounded_list(
    values: list[Any],
    limit: int,
    omissions: list[dict[str, Any]],
    section: str,
    field: str,
    reason: str,
) -> list[Any]:
    effective_limit = max(0, limit)
    if len(values) > effective_limit:
        omissions.append(
            {
                "section": section,
                "field": field,
                "omitted_count": len(values) - effective_limit,
                "limit": effective_limit,
                "reason": reason,
            }
        )
    return values[:effective_limit]


def section_status(base: str, warnings: list[Any] | None = None, exit_code: int = 0) -> str:
    if base in {"blocked", "error"}:
        return base
    if exit_code:
        return "blocked"
    if warnings:
        return "warning"
    return base


def bundle_section(
    status: str,
    source_command: str,
    data: dict[str, Any],
    warnings: list[Any] | None = None,
    exit_code: int = 0,
) -> dict[str, Any]:
    return {
        "status": section_status(status, warnings, exit_code),
        "source_command": source_command,
        "exit_code": exit_code,
        "warnings": warnings or [],
        "data": data,
    }


def compact_doc_impact_payload(repo: Path, files: list[str]) -> tuple[dict[str, Any], int]:
    config = config_for(repo, check_doc_impact.CONFIG_FILE)
    evaluation = check_doc_impact.evaluate(files, config, False)
    categories = [
        {
            "category": category,
            "changed_files": sorted(paths),
            "suggested_doc_paths": config["category_doc_paths"].get(category, config["doc_paths"]),
            "covered": category in evaluation.covered_categories,
        }
        for category, paths in sorted(evaluation.categories.items())
    ]
    exit_code = 1 if evaluation.failed else 0
    return (
        {
            "changed_files": evaluation.changed_files,
            "docs_changed": evaluation.docs_changed,
            "categories": categories,
            "missing_categories": sorted(evaluation.missing_categories),
            "result": "missing-docs" if evaluation.failed else "covered-or-no-impact",
        },
        exit_code,
    )


def compact_task_status(repo: Path, limits: dict[str, int], omissions: list[dict[str, Any]]) -> dict[str, Any]:
    script = ROOT / "scripts" / "agent_task_status.py"
    command = [sys.executable, str(script), "--json", "--include-closed"]
    if not script.exists():
        return bundle_section(
            "warning",
            "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
            {"available": False},
            [f"Task status script not found: {script}"],
            0,
        )
    result = subprocess.run(command, cwd=repo, capture_output=True, text=True, check=False)
    try:
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return bundle_section(
            "error",
            "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
            {
                "available": False,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            ["Unable to parse task status JSON."],
            result.returncode or 2,
        )
    tasks = payload.get("tasks", []) if isinstance(payload.get("tasks"), list) else []
    compact_tasks = [
        {
            "task_id": task.get("task_id"),
            "status": task.get("status"),
            "owner": task.get("owner"),
            "owner_label": task.get("owner_label"),
            "session_id": task.get("session_id"),
            "thread_id": task.get("thread_id"),
            "automation_id": task.get("automation_id"),
            "attribution": task.get("attribution") or unknown_attribution(),
            "worktree": task.get("worktree"),
            "scope": task.get("scope") or [],
            "dirty": task.get("dirty"),
            "warnings": task.get("warnings") or [],
            "final_receipt": task.get("final_receipt"),
        }
        for task in tasks
    ]
    hazards = payload.get("hazards", []) if isinstance(payload.get("hazards"), list) else []
    warnings = []
    if result.returncode:
        warnings.append(result.stderr.strip() or result.stdout.strip() or "agent-task-status returned non-zero")
    if hazards:
        warnings.append("Task status reported coordination hazards.")
    if payload.get("stale_tasks"):
        warnings.append("Task status reported stale task metadata.")
    status = "warning" if warnings else "ok"
    return bundle_section(
        status,
        "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
        {
            "active_task_count": payload.get("active_task_count", 0),
            "task_count": payload.get("task_count", 0),
            "registered_worktree_count": payload.get("registered_worktree_count", 0),
            "hazards": bounded_list(hazards, limits["tasks"], omissions, "task_status", "hazards", "task hazards were truncated"),
            "stale_task_count": len(payload.get("stale_tasks", []) or []),
            "unknown_scope_task_count": len(payload.get("unknown_scope_tasks", []) or []),
            "untracked_agent_worktree_count": len(payload.get("untracked_agent_worktrees", []) or []),
            "tasks": bounded_list(compact_tasks, limits["tasks"], omissions, "task_status", "tasks", "task list was truncated"),
        },
        warnings,
        result.returncode,
    )


def run_json_script(command: list[str], cwd: Path, source_command: str) -> tuple[dict[str, Any], list[str], int]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    warnings = []
    if result.returncode:
        warnings.append(result.stderr.strip() or result.stdout.strip() or f"{source_command} returned non-zero")
    try:
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return (
            {
                "available": False,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            warnings + [f"Unable to parse JSON from {source_command}."],
            result.returncode or 2,
        )
    return payload if isinstance(payload, dict) else {"value": payload}, warnings, result.returncode


def sidecar_directory_availability(state: dict[str, Any]) -> dict[str, Any]:
    paths = state.get("paths") or {}
    directories = {}
    for key in SIDECAR_DIR_KEYS:
        raw_path = paths.get(key)
        exists = bool(raw_path and Path(raw_path).is_dir())
        directories[key] = {
            "path": raw_path or "",
            "exists": exists,
            "entry_count": sum(1 for _ in Path(raw_path).iterdir()) if exists else 0,
        }
    status_path = paths.get("status_json")
    return {
        "available": bool(state.get("available")),
        "repo_state_dir": state.get("repo_state_dir"),
        "paths": paths,
        "directories": directories,
        "status_json": {
            "path": status_path or "",
            "exists": bool(status_path and Path(status_path).is_file()),
        },
    }


def receipt_category(path: Path, payload: dict[str, Any], location: str) -> str:
    command = str(payload.get("command") or "").strip()
    action = str(payload.get("action") or "").strip()
    name = path.name
    if command in {"agent-preflight", "agent-doctor"}:
        return "preflight_doctor"
    if command == "agent-self-heal":
        return "self_heal"
    if command == "automation-handoff" and action == "capture-original-baseline":
        return "automation_baseline"
    if command == "automation-handoff":
        return "automation_handoff"
    if command == "agent-task-finalize" or name == "finalize-receipt.json":
        return "finalizer"
    if location == "target-final-receipts":
        return "final_receipt"
    return "other"


def receipt_summary(path: Path, payload: dict[str, Any], location: str) -> dict[str, Any]:
    category = receipt_category(path, payload, location)
    blockers = payload.get("blockers") if isinstance(payload.get("blockers"), list) else []
    warnings = payload.get("warnings") if isinstance(payload.get("warnings"), list) else []
    task_payload = payload.get("task") if isinstance(payload.get("task"), dict) else {}
    attribution = attribution_from_receipt(payload, path)
    return {
        "path": str(path),
        "location": location,
        "category": category,
        "command": payload.get("command"),
        "action": payload.get("action"),
        "task_id": payload.get("task_id") or task_payload.get("id"),
        "result": payload.get("result") or payload.get("status"),
        "exit_code": payload.get("exit_code"),
        "created_at": payload.get("created_at") or payload.get("generated_at"),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "receipt_path": (payload.get("receipt") or {}).get("path") if isinstance(payload.get("receipt"), dict) else None,
        "attribution": attribution,
    }


def receipt_sort_key(item: dict[str, Any]) -> tuple[str, str]:
    return (str(item.get("created_at") or ""), str(item.get("path") or ""))


def read_receipt_file(path: Path, location: str) -> tuple[dict[str, Any] | None, str | None]:
    payload = read_json(path)
    if payload is None:
        return None, f"Receipt disappeared while scanning: {path}"
    if not isinstance(payload, dict):
        return None, f"Receipt is not a JSON object: {path}"
    if payload.get("_error"):
        return None, f"Invalid receipt JSON: {path}: {payload['_error']}"
    return receipt_summary(path, payload, location), None


def scan_json_receipts(paths: list[tuple[Path, str, str]]) -> dict[str, Any]:
    warnings = []
    items = []
    for directory, location, pattern in paths:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob(pattern)):
            summary, warning = read_receipt_file(path, location)
            if warning:
                warnings.append(warning)
                continue
            if summary:
                items.append(summary)
    categories: dict[str, list[dict[str, Any]]] = {}
    for item in sorted(items, key=receipt_sort_key, reverse=True):
        categories.setdefault(item["category"], []).append(item)
    latest = {category: values[0] for category, values in categories.items() if values}
    return {
        "count": len(items),
        "categories": {category: {"count": len(values), "latest": values[0]} for category, values in sorted(categories.items())},
        "latest": latest,
        "items": items,
        "warnings": warnings,
    }


def resolve_task_receipt(primary: Path, task: dict[str, Any]) -> dict[str, Any]:
    receipt = str(task.get("final_receipt") or "").strip()
    if not receipt:
        return {"path": "", "resolved_path": "", "exists": False, "missing": True, "reason": "no linked final receipt"}
    raw_path = Path(receipt).expanduser()
    candidates = [raw_path] if raw_path.is_absolute() else [primary / raw_path]
    worktree_value = str(task.get("worktree") or "").strip()
    if worktree_value and not raw_path.is_absolute():
        candidates.append(Path(worktree_value).expanduser() / raw_path)
    for candidate in candidates:
        if candidate.exists():
            return {
                "path": receipt,
                "resolved_path": str(candidate.resolve()),
                "exists": True,
                "missing": False,
                "reason": "",
            }
    return {
        "path": receipt,
        "resolved_path": "",
        "exists": False,
        "missing": True,
        "reason": "linked final receipt was not found",
    }


def task_terminal(status: str) -> bool:
    normalized = status.strip().lower()
    return normalized in DONE_STATUSES or normalized in {"blocked", "abandoned"}


def task_next_command(task: dict[str, Any], receipt: dict[str, Any], active_hazard: bool) -> str:
    task_id = task.get("task_id") or "unknown"
    status = str(task.get("status") or "").strip().lower()
    if active_hazard or task.get("lease_expired") or not task.get("worktree_exists"):
        return "make agent-task-status TASK_STATUS_STRICT=1"
    if task.get("dirty"):
        return f"make agent-task-ready TASK={task_id} TASK_READY_JSON=1"
    if status == "in-progress":
        if receipt.get("exists"):
            return f"make agent-task-finalize TASK={task_id} TASK_RECEIPT={receipt['path']} TASK_FINALIZE_JSON=1"
        return f"make agent-task-ready TASK={task_id} TASK_READY_JSON=1"
    if task_terminal(status):
        return "make agent-task-closeout"
    return "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1"


def ledger_task_summaries(primary: Path, task_status: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    hazards = task_status.get("hazards", []) if isinstance(task_status.get("hazards"), list) else []
    hazard_tasks = {
        task_id
        for hazard in hazards
        for task_id in hazard.get("tasks", [])
    }
    blockers = []
    warnings = []
    summaries = []
    for task in task_status.get("tasks", []) if isinstance(task_status.get("tasks"), list) else []:
        task_id = task.get("task_id") or "unknown"
        receipt = resolve_task_receipt(primary, task)
        attribution = task.get("attribution") if isinstance(task.get("attribution"), dict) else attribution_from_task(task)
        attribution = {
            **attribution,
            "latest_receipt": {
                "path": receipt.get("path") or (attribution.get("latest_receipt") or {}).get("path"),
                "resolved_path": receipt.get("resolved_path") or "",
                "exists": bool(receipt.get("exists")),
                "provenance": "metadata" if receipt.get("path") else (attribution.get("latest_receipt") or {}).get("provenance"),
            },
        }
        status = str(task.get("status") or "unknown")
        active_hazard = task_id in hazard_tasks
        missing_worktree = not bool(task.get("worktree_exists"))
        dirty_worktree = bool(task.get("dirty"))
        stale_lease = bool(task.get("lease_expired"))
        missing_final_receipt = task_terminal(status) and receipt.get("missing")
        active_overlap = active_hazard
        unresolved = []
        if missing_worktree:
            unresolved.append("missing-worktree")
            blockers.append({"code": "missing_worktree", "task_id": task_id, "message": "Task metadata references a missing worktree.", "attribution": attribution})
        if dirty_worktree:
            unresolved.append("dirty-worktree")
            warnings.append({"code": "dirty_worktree", "task_id": task_id, "message": "Task worktree has uncommitted changes.", "attribution": attribution})
        if stale_lease:
            unresolved.append("stale-lease")
            warnings.append({"code": "stale_lease", "task_id": task_id, "message": "Task lease has expired.", "attribution": attribution})
        if missing_final_receipt:
            unresolved.append("missing-final-receipt")
            blockers.append({"code": "missing_final_receipt", "task_id": task_id, "message": "Terminal task is missing a linked final receipt.", "attribution": attribution, "latest_receipt": attribution.get("latest_receipt")})
        if active_overlap:
            unresolved.append("active-overlap")
            blockers.append({"code": "active_overlap", "task_id": task_id, "message": "Task scope overlaps another active task.", "attribution": attribution})
        summaries.append(
            {
                "task_id": task_id,
                "status": status,
                "owner": task.get("owner"),
                "owner_label": task.get("owner_label"),
                "session_id": task.get("session_id"),
                "thread_id": task.get("thread_id"),
                "automation_id": task.get("automation_id"),
                "attribution": attribution,
                "run_id": task.get("run_id"),
                "metadata_path": task.get("metadata_path"),
                "scope": task.get("scope") or [],
                "worktree": task.get("worktree"),
                "worktree_exists": bool(task.get("worktree_exists")),
                "worktree_registered": bool(task.get("worktree_registered")),
                "dirty": task.get("dirty"),
                "dirty_count": len(task.get("status_entries") or []),
                "lease": {
                    "heartbeat_at": task.get("heartbeat_at"),
                    "lease_expires_at": task.get("lease_expires_at"),
                    "stale": stale_lease,
                },
                "final_receipt": receipt,
                "latest_receipt": attribution.get("latest_receipt"),
                "missing_worktree": missing_worktree,
                "missing_final_receipt": missing_final_receipt,
                "stale_lease": stale_lease,
                "active_overlap": active_overlap,
                "warnings": task.get("warnings") or [],
                "unresolved": unresolved,
                "next_safe_command": task_next_command(task, receipt, active_hazard),
            }
        )
    return summaries, blockers, warnings


def ledger_next_commands(blockers: list[dict[str, Any]], warnings: list[dict[str, Any]], tasks: list[dict[str, Any]], closeout: dict[str, Any], receipts: dict[str, Any], sidecar_available: bool) -> list[str]:
    commands = []
    codes = {item.get("code") for item in blockers + warnings}
    if not sidecar_available or "dirty_checkout" in codes or "self_heal_blocked" in codes:
        commands.append("make agent-self-heal")
    if {"missing_worktree", "stale_lease", "active_overlap"} & codes:
        commands.append("make agent-task-status TASK_STATUS_STRICT=1")
    if any(task.get("status") == "in-progress" and not task.get("unresolved") for task in tasks):
        commands.append("make agent-task-ready TASK=<id> TASK_READY_JSON=1")
    if any(task.get("status") == "in-progress" and task.get("final_receipt", {}).get("exists") for task in tasks):
        commands.append("make agent-task-finalize TASK=<id> TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1")
    if closeout.get("closeout_candidate_count") or "missing_final_receipt" in codes or "dirty_worktree" in codes:
        commands.append("make agent-task-closeout")
    latest_handoff = (receipts.get("latest") or {}).get("automation_handoff") or (receipts.get("latest") or {}).get("automation_baseline")
    if latest_handoff and latest_handoff.get("result") == "blocked":
        commands.append("make agent-automation-handoff")
    if "automation_baseline_blocked" in codes:
        commands.append("make agent-automation-handoff")
    if "finalizer_blocked" in codes:
        commands.append("make agent-task-finalize TASK=<id> TASK_RECEIPT=<path> TASK_FINALIZE_JSON=1")
    if not commands:
        commands.extend(["make agent-task-status", "make agent-task-ready TASK=<id> TASK_READY_JSON=1"])
    deduped = []
    for command in commands:
        if command not in deduped:
            deduped.append(command)
    return deduped


def agent_state_ledger_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    primary = primary_checkout(repo)
    sidecar = sidecar_state(primary)
    dirty = dirty_summary(git_status_entries(primary))
    task_status, task_status_warnings, task_status_code = run_json_script(
        [sys.executable, str(ROOT / "scripts" / "agent_task_status.py"), "--json", "--include-closed"],
        primary,
        "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
    )
    closeout, closeout_warnings, closeout_code = run_json_script(
        [sys.executable, str(ROOT / "scripts" / "agent_task_cleanup.py"), "--closeout", "--json"],
        primary,
        "make agent-task-closeout TASK_CLOSEOUT_JSON=1",
    )
    sidecar_paths = sidecar.get("paths") or {}
    receipt_paths = [
        (Path(sidecar_paths["receipts_dir"]), "sidecar-receipts", "*.json")
        for key in ("receipts_dir",)
        if sidecar_paths.get(key)
    ]
    if sidecar_paths.get("automation_handoffs_dir"):
        receipt_paths.append((Path(sidecar_paths["automation_handoffs_dir"]), "sidecar-automation-handoffs", "*.json"))
    finalizer_dir = primary / ".agent-workflows" / "tasks"
    if finalizer_dir.exists():
        receipt_paths.append((finalizer_dir, "target-finalizer-receipts", "finalize-receipt.json"))
        receipt_paths.append((finalizer_dir, "target-final-receipts", "receipt.json"))
    receipts = scan_json_receipts(receipt_paths)
    tasks, task_blockers, task_warnings = ledger_task_summaries(primary, task_status)
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    blockers.extend(task_blockers)
    warnings.extend(task_warnings)
    if dirty["dirty"]:
        warnings.append({"code": "dirty_checkout", "message": "Primary checkout has uncommitted changes.", "count": dirty["count"], "attribution": unknown_attribution()})
    if not sidecar.get("available"):
        warnings.append({"code": "missing_sidecar", "message": "Sidecar state directory is not initialized."})
    if task_status_code:
        warnings.append({"code": "task_status_error", "message": "Task status report returned non-zero.", "details": task_status_warnings})
    else:
        warnings.extend({"code": "task_status_warning", "message": item} for item in task_status_warnings)
    if closeout_code:
        warnings.append({"code": "closeout_error", "message": "Closeout preview returned non-zero.", "details": closeout_warnings})
    else:
        warnings.extend({"code": "closeout_warning", "message": item} for item in closeout_warnings)
    warnings.extend({"code": "receipt_warning", "message": item} for item in receipts.get("warnings", []))
    latest_self_heal = (receipts.get("latest") or {}).get("self_heal")
    latest_preflight = (receipts.get("latest") or {}).get("preflight_doctor")
    latest_finalizer = (receipts.get("latest") or {}).get("finalizer")
    latest_baseline = (receipts.get("latest") or {}).get("automation_baseline")
    if latest_self_heal and latest_self_heal.get("result") == "blocked":
        warnings.append({"code": "self_heal_blocked", "message": "Latest self-heal receipt was blocked.", "receipt": latest_self_heal.get("path"), "attribution": latest_self_heal.get("attribution") or unknown_attribution()})
    if latest_preflight and latest_preflight.get("result") == "blocked":
        warnings.append({"code": "preflight_blocked", "message": "Latest preflight/doctor receipt was blocked.", "receipt": latest_preflight.get("path"), "attribution": latest_preflight.get("attribution") or unknown_attribution()})
    if latest_finalizer and latest_finalizer.get("result") == "blocked":
        warnings.append({"code": "finalizer_blocked", "message": "Latest finalizer receipt was blocked.", "receipt": latest_finalizer.get("path"), "task_id": latest_finalizer.get("task_id"), "attribution": latest_finalizer.get("attribution") or unknown_attribution()})
    if latest_baseline and latest_baseline.get("result") == "blocked":
        blockers.append({"code": "automation_baseline_blocked", "message": "Latest automation baseline receipt was blocked.", "receipt": latest_baseline.get("path"), "attribution": latest_baseline.get("attribution") or unknown_attribution()})
    latest_handoff = (receipts.get("latest") or {}).get("automation_handoff")
    if latest_handoff and latest_handoff.get("result") == "blocked":
        blockers.append({"code": "automation_handoff_blocked", "message": "Latest automation handoff receipt was blocked.", "receipt": latest_handoff.get("path"), "attribution": latest_handoff.get("attribution") or unknown_attribution()})
    commands = ledger_next_commands(blockers, warnings, tasks, closeout, receipts, bool(sidecar.get("available")))
    return {
        "schema_version": 1,
        "command": "agent-state-ledger",
        "repo": str(primary),
        "invoked_from": str(repo),
        "created_at": now(),
        "target_repo_writes": False,
        "sidecar_writes": False,
        "write_guarantees": {
            "target_repo_writes": target_repo_writes(False, reason="agent-state-ledger is read-only"),
            "sidecar_writes": sidecar_writes(False, reason="agent-state-ledger is read-only"),
        },
        "sidecar_state": sidecar,
        "sidecar": sidecar_directory_availability(sidecar),
        "dirty": dirty,
        "task_status": {
            "source_command": "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
            "exit_code": task_status_code,
            "summary": {
                "task_count": task_status.get("task_count", 0),
                "active_task_count": task_status.get("active_task_count", 0),
                "registered_worktree_count": task_status.get("registered_worktree_count", 0),
                "hazard_count": len(task_status.get("hazards", []) or []),
                "stale_task_count": len(task_status.get("stale_tasks", []) or []),
                "unknown_scope_task_count": len(task_status.get("unknown_scope_tasks", []) or []),
                "dirty_worktree_task_count": len(task_status.get("dirty_worktree_tasks", []) or []),
                "untracked_agent_worktree_count": len(task_status.get("untracked_agent_worktrees", []) or []),
            },
            "hazards": task_status.get("hazards", []),
            "stale_tasks": task_status.get("stale_tasks", []),
            "unknown_scope_tasks": task_status.get("unknown_scope_tasks", []),
            "dirty_worktree_tasks": task_status.get("dirty_worktree_tasks", []),
            "untracked_agent_worktrees": task_status.get("untracked_agent_worktrees", []),
            "tasks": tasks,
        },
        "closeout_state": {
            "source_command": "make agent-task-closeout TASK_CLOSEOUT_JSON=1",
            "exit_code": closeout_code,
            "closeout_candidate_count": closeout.get("closeout_candidate_count", 0),
            "closeout_blocked_count": closeout.get("closeout_blocked_count", 0),
            "closeout_retained_count": closeout.get("closeout_retained_count", 0),
            "closeout_candidates": closeout.get("closeout_candidates", []),
            "closeout_blocked": closeout.get("closeout_blocked", []),
        },
        "receipts": receipts,
        "unresolved": {
            "blockers": blockers,
            "warnings": warnings,
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
        },
        "next_safe_commands": commands,
        "result": "blocked" if blockers else ("warning" if warnings else "ok"),
        "exit_code": 0,
    }


def render_agent_state_ledger(payload: dict[str, Any]) -> None:
    unresolved = payload.get("unresolved") or {}
    dirty = payload.get("dirty") or {}
    task_summary = (payload.get("task_status") or {}).get("summary") or {}
    print(f"Agent state ledger for {payload['repo']}:")
    print(f" - result: {payload['result']}")
    print(f" - writes: target=false sidecar=false")
    print(f" - dirty checkout: {str(dirty.get('dirty')).lower()} ({dirty.get('count', 0)} changed)")
    print(f" - sidecar available: {str((payload.get('sidecar') or {}).get('available')).lower()}")
    print(f" - tasks: {task_summary.get('active_task_count', 0)} active / {task_summary.get('task_count', 0)} total")
    print(f" - closeout candidates: {(payload.get('closeout_state') or {}).get('closeout_candidate_count', 0)}")
    if unresolved.get("blockers"):
        print(" - blockers:")
        for item in unresolved["blockers"][:10]:
            task = f" [{item['task_id']}]" if item.get("task_id") else ""
            print(f"   - {item.get('code')}{task}: {item.get('message')}")
            if item.get("attribution"):
                print(f"     attribution: {render_attribution(item['attribution'])}")
    if unresolved.get("warnings"):
        print(" - warnings:")
        for item in unresolved["warnings"][:10]:
            task = f" [{item['task_id']}]" if item.get("task_id") else ""
            print(f"   - {item.get('code')}{task}: {item.get('message')}")
            if item.get("attribution"):
                print(f"     attribution: {render_attribution(item['attribution'])}")
        if len(unresolved["warnings"]) > 10:
            print(f"   - omitted {len(unresolved['warnings']) - 10} additional warning(s); use STATE_LEDGER_JSON=1")
    print(" - next safe commands:")
    for command in payload.get("next_safe_commands") or []:
        print(f"   - {command}")


def compact_token_budget(repo: Path, limits: dict[str, int], omissions: list[dict[str, Any]]) -> dict[str, Any]:
    args = argparse.Namespace(repo=str(repo), strict=False)
    report, exit_code = check_token_budget.build_report(args)
    files = report.get("files", []) if isinstance(report.get("files"), list) else []
    failures = report.get("failures", []) if isinstance(report.get("failures"), list) else []
    warnings = ["Some agent-facing files exceed token budgets."] if failures else []
    return bundle_section(
        "warning" if failures else "ok",
        "make agent-token-budget TOKEN_BUDGET_JSON=1",
        {
            "file_count": report.get("file_count", 0),
            "total_estimated_tokens": report.get("total_estimated_tokens", 0),
            "failure_count": report.get("failure_count", 0),
            "result": report.get("result"),
            "failures": failures,
            "largest_files": bounded_list(
                sorted(files, key=lambda item: item.get("estimated_tokens", 0), reverse=True),
                limits["token_files"],
                omissions,
                "token_budget",
                "largest_files",
                "token-budget file list was truncated",
            ),
        },
        warnings,
        exit_code,
    )


def compact_doc_categories(
    categories: list[dict[str, Any]],
    limits: dict[str, int],
    omissions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    compact = []
    for category in categories:
        item = dict(category)
        category_name = str(item.get("category") or "unknown")
        item["changed_files"] = bounded_list(
            list(item.get("changed_files") or []),
            limits["files"],
            omissions,
            "docs_impact",
            f"categories.{category_name}.changed_files",
            "docs-impact category file list was truncated",
        )
        compact.append(item)
    return compact


def compact_goal_summary(
    summary: dict[str, Any],
    limits: dict[str, int],
    omissions: list[dict[str, Any]],
) -> dict[str, Any]:
    compact = dict(summary)
    for field in ("unknown_paths", "conflict_paths"):
        compact[field] = bounded_list(
            list(summary.get(field) or []),
            limits["files"],
            omissions,
            "goal_check",
            f"summary.{field}",
            "goal-check summary path list was truncated",
        )
    return compact


def agent_context_bundle_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    limits = {
        "files": args.max_files,
        "open_items": args.max_open_items,
        "tasks": args.max_tasks,
        "token_files": args.max_token_files,
        "warnings": args.max_warnings,
        "commands": args.max_commands,
    }
    omissions: list[dict[str, Any]] = []
    files = changed_files(repo, args.mode)
    doc_source_command = "repo_contract_kit.py doc-impact --json"
    if args.mode == "working-tree":
        doc_source_command = "repo_contract_kit.py doc-impact --working-tree --json"
    elif args.mode == "staged":
        doc_source_command = "repo_contract_kit.py doc-impact --staged --json"
    status = status_payload(repo)
    backlog = build_backlog_report(repo, include_items=False)
    next_work = agent_next_payload(repo)

    doc_payload: dict[str, Any]
    doc_exit_code = 0
    doc_warnings: list[str] = []
    try:
        doc_payload, doc_exit_code = compact_doc_impact_payload(repo, files)
    except SystemExit as exc:
        doc_payload = {"available": False, "error": str(exc)}
        doc_exit_code = int(exc.code) if isinstance(exc.code, int) else 2
        doc_warnings.append(str(exc))

    goal_payload: dict[str, Any]
    goal_exit_code = 0
    goal_warnings: list[str] = []
    try:
        goal_payload = goal_check.build_goal_check_report(repo, files, goal_check.CONFIG_FILE)
        goal_exit_code = int(goal_payload.get("exit_code") or 0)
        goal_warnings = list(goal_payload.get("warnings") or [])
    except Exception as exc:  # pragma: no cover - defensive fallback for malformed local configs
        goal_payload = {"available": False, "error": str(exc)}
        goal_exit_code = 2
        goal_warnings = [str(exc)]

    token_section = compact_token_budget(repo, limits, omissions)
    task_section = compact_task_status(repo, limits, omissions)

    changed_entries = [
        {"path": path, "doc_impact": None, "goal_state": None}
        for path in bounded_list(files, limits["files"], omissions, "dirty_state", "changed_files", "changed files were truncated")
    ]
    doc_categories_by_path: dict[str, list[str]] = {}
    doc_categories = doc_payload.get("categories", []) if isinstance(doc_payload, dict) else []
    for category in doc_categories:
        for path in category.get("changed_files", []):
            doc_categories_by_path.setdefault(path, []).append(category.get("category"))
    goal_states = {
        item.get("path"): item.get("state")
        for item in goal_payload.get("files", []) if isinstance(goal_payload, dict)
    }
    for entry in changed_entries:
        path = entry["path"]
        entry["doc_impact"] = sorted(doc_categories_by_path.get(path, []))
        entry["goal_state"] = goal_states.get(path)

    backlog_warnings = list(backlog.get("warnings") or [])
    next_notes = list(next_work.get("notes") or [])
    recommended_commands = [
        "make agent-context-bundle",
        "make agent-preflight",
        "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1",
        "make goal-check",
        "make agent-token-budget",
    ]
    if next_work.get("selected_item"):
        recommended_commands.append(
            f"make agent-task-packet-from-backlog BACKLOG_ID={next_work['selected_item']['id']}"
        )
    if files:
        recommended_commands.append("make agent-task-ready TASK=<id> TASK_READY_JSON=1")
    recommended_commands = bounded_list(
        recommended_commands,
        limits["commands"],
        omissions,
        "readiness_hints",
        "recommended_commands",
        "recommended command list was truncated",
    )

    sections = {
        "repo": bundle_section(
            "ok",
            "repo_contract_kit.py status --json",
            {
                "root": status["repo"],
                "branch": git_worktree_metadata(repo)["branch"],
                "installed": status["install"]["installed"],
                "kit_version": status["install"].get("kit_version"),
                "target_version": status.get("target_version"),
            },
        ),
        "dirty_state": bundle_section(
            "warning" if status["git"]["dirty"] else "ok",
            f"git changed files ({args.mode})",
            {
                "mode": args.mode,
                "dirty": status["git"]["dirty"],
                "changed_file_count": len(files),
                "changed_files": changed_entries,
            },
            ["Working tree has changed files."] if status["git"]["dirty"] else [],
        ),
        "backlog": bundle_section(
            "warning" if backlog_warnings else "ok",
            "make backlog-status BACKLOG_JSON=1",
            {
                "selected_source": backlog.get("selected_source"),
                "counts": backlog.get("counts"),
                "open_by_priority": backlog.get("open_by_priority"),
                "next_open_item": backlog.get("next_open_item"),
                "open_items": bounded_list(
                    list(backlog.get("open_items") or []),
                    limits["open_items"],
                    omissions,
                    "backlog",
                    "open_items",
                    "open backlog item list was truncated",
                ),
            },
            backlog_warnings,
        ),
        "next_work": bundle_section(
            "warning" if next_notes else "ok",
            "make agent-next BACKLOG_JSON=1",
            {
                "selected_item": next_work.get("selected_item"),
                "status": next_work.get("status"),
                "notes": bounded_list(next_notes, limits["warnings"], omissions, "next_work", "notes", "agent-next notes were truncated"),
            },
            next_notes,
        ),
        "task_status": task_section,
        "docs_impact": bundle_section(
            "blocked" if doc_exit_code else "ok",
            doc_source_command,
            {
                "result": doc_payload.get("result"),
                "changed_file_count": len(doc_payload.get("changed_files", []) or []),
                "docs_changed": bounded_list(
                    list(doc_payload.get("docs_changed", []) or []),
                    limits["files"],
                    omissions,
                    "docs_impact",
                    "docs_changed",
                    "docs-changed list was truncated",
                ),
                "categories": compact_doc_categories(list(doc_payload.get("categories", []) or []), limits, omissions),
                "missing_categories": doc_payload.get("missing_categories", []),
            },
            doc_warnings,
            doc_exit_code,
        ),
        "goal_check": bundle_section(
            "blocked" if goal_exit_code else "ok",
            "make goal-check GOAL_CHECK_JSON=1",
            {
                "result": goal_payload.get("result"),
                "config": goal_payload.get("config", {}),
                "summary": compact_goal_summary(goal_payload.get("summary", {}), limits, omissions),
                "files": bounded_list(
                    list(goal_payload.get("files", []) or []),
                    limits["files"],
                    omissions,
                    "goal_check",
                    "files",
                    "goal-check file list was truncated",
                ),
            },
            bounded_list(goal_warnings, limits["warnings"], omissions, "goal_check", "warnings", "goal-check warnings were truncated"),
            goal_exit_code,
        ),
        "token_budget": token_section,
        "sidecar": bundle_section(
            "ok" if sidecar_state(repo).get("available") else "warning",
            "repo_contract_kit.py status --json",
            {
                "available": sidecar_state(repo).get("available"),
                "repo_state_dir": sidecar_state(repo).get("repo_state_dir"),
                "paths": sidecar_state(repo).get("paths", {}),
            },
            [] if sidecar_state(repo).get("available") else ["Sidecar state directory is not initialized."],
        ),
    }
    section_statuses = {name: section["status"] for name, section in sections.items()}
    attention = any(value in {"warning", "blocked", "error"} for value in section_statuses.values())
    payload = {
        "schema_version": 1,
        "command": "agent-context-bundle",
        "repo": str(repo),
        "generated_at": now(),
        "mode": args.mode,
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "limits": limits,
        "summary": {
            "result": "attention" if attention else "ok",
            "dirty": status["git"]["dirty"],
            "changed_file_count": len(files),
            "next_item_id": (next_work.get("selected_item") or {}).get("id"),
            "active_task_count": (task_section.get("data") or {}).get("active_task_count", 0),
            "docs_result": doc_payload.get("result"),
            "goal_result": goal_payload.get("result"),
            "token_estimated": (token_section.get("data") or {}).get("total_estimated_tokens", 0),
            "section_statuses": section_statuses,
            "omission_count": len(omissions),
        },
        "sections": sections,
        "readiness_hints": {
            "recommended_commands": recommended_commands,
            "notes": [
                "This bundle is report-only; run readiness/finalizer commands before handoff.",
                "Blocked or warning sections require operator review before write-capable work continues.",
            ],
        },
        "omissions": omissions,
        "exit_code": 0,
    }
    return payload


def instruction_diet_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    payload = lint_agent_docs.build_instruction_diet_report(
        repo,
        explicit_files=args.files,
        strict_paths=args.strict_paths,
        budget_config_file=args.budget_config,
    )
    payload["target_repo_writes"] = target_repo_writes(False)
    payload["sidecar_writes"] = sidecar_writes(False)
    payload["sidecar_state"] = sidecar_state(repo)
    payload["exit_code"] = 0
    return payload


def doc_impact_sarif_payload(payload: dict[str, Any]) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    missing = set(payload.get("missing_categories", []))
    for category in payload.get("categories", []):
        category_id = category.get("category")
        if category_id not in missing:
            continue
        rule_id = f"docs-contract-{category_id}"
        suggested = category.get("suggested_doc_paths", [])
        rules[rule_id] = {
            "id": rule_id,
            "name": f"Missing documentation coverage for {category_id}",
            "shortDescription": {"text": f"Documentation impact for {category_id} is not covered."},
            "help": {"text": "Update the expected docs or declare an explicit no-docs-needed reason."},
        }
        for path in category.get("changed_files", []):
            results.append(
                {
                    "ruleId": rule_id,
                    "level": "error",
                    "message": {
                        "text": (
                            f"{path} is categorized as {category_id}, but no matching documentation "
                            f"was changed. Suggested docs: {', '.join(suggested)}."
                        )
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": path}
                            }
                        }
                    ],
                    "properties": {
                        "category": category_id,
                        "suggested_doc_paths": suggested,
                    },
                }
            )
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "repo-contract-kit docs contract",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }


def preferred_docs_proposal_path(repo: Path, category: str, suggested_paths: list[str]) -> str:
    for rel_path in suggested_paths:
        if rel_path.endswith("/"):
            continue
        if (repo / rel_path).exists():
            return rel_path
    for rel_path in suggested_paths:
        if rel_path.endswith("/"):
            return f"{rel_path.rstrip('/')}/{category}-docs-update.md"
    return suggested_paths[0] if suggested_paths else f"docs/{category}-docs-update.md"


def docs_proposal_sections(categories: list[dict[str, Any]], missing_categories: list[str]) -> list[dict[str, Any]]:
    missing = set(missing_categories)
    sections = []
    for category in categories:
        category_id = category["category"]
        if category_id not in missing:
            continue
        sections.append(
            {
                "category": category_id,
                "changed_files": category["changed_files"],
                "suggested_doc_paths": category["suggested_doc_paths"],
            }
        )
    return sections


def render_docs_proposal_section(section: dict[str, Any]) -> str:
    lines = [
        f"## Documentation Update Proposal: {section['category']}",
        "",
        "Review this scaffold before applying. Replace proposal language with",
        "specific documentation for the actual behavior, API, config, or",
        "operations change.",
        "",
        "Changed files needing coverage:",
    ]
    for path in section["changed_files"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "Suggested coverage:",
            "- Explain what changed and who is affected.",
            "- Link or mention the validation command or evidence.",
            "- Update release notes when the change is user-visible.",
            "",
        ]
    )
    return "\n".join(lines)


def build_docs_patch(repo: Path, sections: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    sections_by_path: dict[str, list[dict[str, Any]]] = {}
    recommendations = []
    for section in sections:
        rel_path = preferred_docs_proposal_path(repo, section["category"], section["suggested_doc_paths"])
        sections_by_path.setdefault(rel_path, []).append(section)
        recommendations.append(
            {
                "category": section["category"],
                "changed_files": section["changed_files"],
                "suggested_doc_paths": section["suggested_doc_paths"],
                "proposal_path": rel_path,
            }
        )

    patch_parts = []
    for rel_path, path_sections in sorted(sections_by_path.items()):
        target = repo / rel_path
        existed = target.exists()
        old_text = target.read_text(encoding="utf-8") if existed else ""
        addition = "\n".join(render_docs_proposal_section(section) for section in path_sections)
        if existed:
            separator = "" if old_text.endswith("\n") else "\n"
            new_text = old_text + separator + "\n" + addition
            from_file = f"a/{rel_path}"
        else:
            title = Path(rel_path).stem.replace("-", " ").replace("_", " ").title()
            new_text = f"# {title}\n\n{addition}"
            from_file = "/dev/null"
        diff = difflib.unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=from_file,
            tofile=f"b/{rel_path}",
            lineterm="",
        )
        header = [f"diff --git a/{rel_path} b/{rel_path}\n"]
        if not existed:
            header.append("new file mode 100644\n")
        patch_parts.append("".join(header + [line if line.endswith("\n") else f"{line}\n" for line in diff]))

    return "".join(patch_parts), recommendations


def render_docs_proposal_markdown(payload: dict[str, Any]) -> str:
    proposal = payload["proposal"]
    lines = [
        "# Docs Patch Proposal",
        "",
        f"- repo: `{payload['repo']}`",
        f"- result: `{payload['result']}`",
        f"- patch needed: `{str(proposal['needed']).lower()}`",
        "",
        "This artifact is a proposal only. Review and edit the patch before",
        "applying it, then run the normal docs checks. Do not commit generated",
        "scaffold text without replacing it with accurate documentation.",
        "",
        "## Changed Files",
        "",
    ]
    for path in payload["changed_files"] or ["(none)"]:
        lines.append(f"- `{path}`")
    if proposal["recommendations"]:
        lines.extend(["", "## Recommended Doc Updates", ""])
        for item in proposal["recommendations"]:
            lines.append(f"- `{item['proposal_path']}` for `{item['category']}`")
            changed = ", ".join(f"`{path}`" for path in item["changed_files"])
            suggested = ", ".join(f"`{path}`" for path in item["suggested_doc_paths"])
            lines.append(f"  - changed files: {changed}")
            lines.append(f"  - suggested paths: {suggested}")
    else:
        lines.extend(["", "No missing documentation categories were detected."])
    lines.extend(
        [
            "",
            "## Validation",
            "",
            "- Run `make docs-check` after applying and editing any patch.",
            "- Run `git diff --check` before committing.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_docs_proposal_sidecar(repo: Path, payload: dict[str, Any], patch_text: str, markdown_text: str) -> dict[str, Any]:
    state, init_paths = ensure_sidecar(repo, "docs-propose --write-sidecar")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    proposal_dir = Path(state["paths"]["docs_patch_proposals_dir"]) / stamp
    json_path = proposal_dir / "docs-patch-proposal.json"
    markdown_path = proposal_dir / "docs-patch-proposal.md"
    paths = init_paths + [str(json_path), str(markdown_path)]
    patch_path = None
    if patch_text.strip():
        patch_path = proposal_dir / "docs.patch"
        paths.append(str(patch_path))
        write_text_file(patch_path, patch_text)
    payload["sidecar_state"] = state
    payload["proposal"]["artifacts"] = {
        "directory": str(proposal_dir),
        "json": str(json_path),
        "markdown": str(markdown_path),
        "patch": str(patch_path) if patch_path else None,
        "apply_command": f"git apply {patch_path}" if patch_path else None,
    }
    payload["sidecar_writes"] = sidecar_writes(True, paths=paths, reason="docs-propose --write-sidecar")
    write_text_file(markdown_path, markdown_text)
    write_json_file(json_path, payload)
    return payload


def docs_propose_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    impact_args = argparse.Namespace(
        config=args.config,
        changed_files=args.changed_files,
        staged=args.staged,
        working_tree=args.working_tree,
        no_docs_needed=None,
    )
    impact, _ = doc_impact_payload(impact_args, repo)
    sections = docs_proposal_sections(impact["categories"], impact["missing_categories"])
    patch_text, recommendations = build_docs_patch(repo, sections) if sections else ("", [])
    payload = {
        "schema_version": 1,
        "command": "docs-propose",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False, reason="docs proposal writes sidecar artifacts only"),
        "sidecar_writes": sidecar_writes(False, reason="dry run" if not args.write_sidecar else "before sidecar write"),
        "sidecar_state": sidecar_state(repo),
        "changed_files": impact["changed_files"],
        "docs_changed": impact["docs_changed"],
        "categories": impact["categories"],
        "missing_categories": impact["missing_categories"],
        "result": impact["result"],
        "proposal": {
            "needed": bool(sections),
            "recommendations": recommendations,
            "artifacts": None,
            "patch_preview": {
                "bytes": len(patch_text.encode("utf-8")),
                "line_count": len(patch_text.splitlines()),
            },
        },
        "next_commands": ["make docs-check", "git diff --check"],
        "exit_code": 0,
    }
    markdown_text = render_docs_proposal_markdown(payload)
    if args.write_sidecar:
        payload = write_docs_proposal_sidecar(repo, payload, patch_text, markdown_text)
    return payload, 0


def safe_artifact_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-") or "artifact"


def onboarding_install_selection(args: argparse.Namespace) -> tuple[list[str], list[str], list[str]]:
    install_module = load_install_module()
    try:
        profiles = install_module.resolve_requested_profiles(args)
        runtime_adapters = install_module.resolve_runtime_adapters(args)
    except SystemExit as exc:
        raise CliError(str(exc), exit_code=2) from exc

    option_args: list[str] = []
    if args.preset:
        option_args.extend(["--preset", args.preset])
    elif args.profiles:
        option_args.extend(["--profiles", args.profiles])
    elif args.profile:
        option_args.extend(["--profile", args.profile])
    else:
        option_args.extend(["--profile", install_module.DEFAULT_PROFILE])

    runtime_selection_explicit = bool(args.runtime_adapter or args.runtime_adapters)
    if runtime_selection_explicit:
        option_args.extend(["--runtime-adapters", ",".join(runtime_adapters) if runtime_adapters else "none"])

    if args.force:
        option_args.append("--force")

    return profiles, runtime_adapters, option_args


def onboarding_stage_paths(profiles: list[str], runtime_adapters: list[str]) -> list[str]:
    install_module = load_install_module()
    try:
        entries = install_module.desired_entries(profiles, runtime_adapters)
    except SystemExit as exc:
        raise CliError(str(exc), exit_code=2) from exc
    paths = set(install_module.final_entries_by_target(entries))
    paths.update({".doc-contract-kit/install.json", ".doc-contract-kit/manifest.json"})
    return sorted(paths)


def onboarding_pr_body(payload: dict[str, Any]) -> str:
    install_plan = payload["install_plan"]
    validation = payload["instructions"]["validation_commands"]
    profile_text = ", ".join(install_plan["profiles"])
    adapter_text = ", ".join(install_plan["runtime_adapters"]) or "none"
    lines = [
        "## What Changed",
        "",
        "- Install repo-contract-kit using the generated onboarding branch instructions.",
        f"- Profiles: {profile_text}.",
        f"- Runtime adapters: {adapter_text}.",
        "",
        "## Docs",
        "",
        "- Documentation is installed or updated by the repo-contract-kit templates included in this PR.",
        "",
        "## ADR",
        "",
        "- No ADR added; this is an onboarding PR for repository guardrails and local workflow files.",
        "",
        "## Validation",
        "",
    ]
    lines.extend(f"- [ ] `{command}`" for command in validation)
    return "\n".join(lines) + "\n"


def onboarding_pr_markdown(payload: dict[str, Any]) -> str:
    instructions = payload["instructions"]
    lines = [
        "# repo-contract-kit Onboarding PR",
        "",
        f"- Repo: `{payload['repo']}`",
        f"- Branch: `{instructions['branch']}`",
        f"- Base ref: `{instructions['base_ref']}`",
        f"- Target writes performed by generator: `{str(payload['target_repo_writes']['performed']).lower()}`",
        "",
        "## Commands",
        "",
    ]
    for step in instructions["steps"]:
        lines.extend([f"### {step['title']}", "", "```bash", step["command"], "```", ""])
        if step.get("note"):
            lines.extend([step["note"], ""])
    lines.extend(
        [
            "## Pull Request",
            "",
            f"Title: `{instructions['pr_title']}`",
            "",
            "Body:",
            "",
            "```markdown",
            instructions["pr_body"].rstrip(),
            "```",
            "",
        ]
    )
    if payload["warnings"]:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
        lines.append("")
    return "\n".join(lines)


def write_onboarding_pr_sidecar(repo: Path, payload: dict[str, Any]) -> dict[str, Any]:
    reason = "onboarding-pr --write-sidecar"
    state, init_paths = ensure_sidecar(repo, reason)
    artifact_dir = Path(state["paths"]["review_artifacts_dir"])
    label = safe_artifact_name(payload["instructions"]["branch"])
    json_path = artifact_dir / f"onboarding-pr-{label}.json"
    markdown_path = artifact_dir / f"onboarding-pr-{label}.md"
    payload["sidecar_state"] = state
    payload["onboarding_pr"]["artifacts"] = {
        "json": str(json_path),
        "markdown": str(markdown_path),
    }
    payload["sidecar_writes"] = sidecar_writes(
        True,
        paths=init_paths + [str(json_path), str(markdown_path)],
        reason=reason,
    )
    write_text_file(markdown_path, onboarding_pr_markdown(payload))
    write_json_file(json_path, payload)
    return payload


def onboarding_pr_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    profiles, runtime_adapters, install_options = onboarding_install_selection(args)
    stage_paths = onboarding_stage_paths(profiles, runtime_adapters)
    status = status_payload(repo)
    current_branch = git_text(repo, ["rev-parse", "--abbrev-ref", "HEAD"]) or "HEAD"
    base_ref = args.base_ref or (current_branch if current_branch and current_branch != "HEAD" else "HEAD")
    branch = args.branch or "codex/repo-contract-kit-onboarding"
    commit_message = args.commit_message or "Install repo-contract-kit onboarding"
    pr_title = args.pr_title or "Install repo-contract-kit"
    remote = args.remote

    install_command = shell_command(CLI_ENTRYPOINT, "install", "--repo", ".", *install_options)
    stage_command = shell_command("git", "add", "-A", "--", *stage_paths)
    validation_commands = ["git diff --check", "make docs-check", "make kit-status"]
    if "local-agentic" in profiles:
        validation_commands.append("make agent-verify")
    if "versioning" in profiles:
        validation_commands.append("make version-check")

    steps = [
        {
            "id": "preflight-clean-worktree",
            "title": "Confirm clean worktree",
            "command": "git status --short",
            "note": "Continue only when this prints no unrelated changes.",
        },
        {
            "id": "create-branch",
            "title": "Create onboarding branch",
            "command": shell_command("git", "switch", "-c", branch, base_ref),
        },
        {
            "id": "install-kit",
            "title": "Install repo-contract-kit files",
            "command": install_command,
        },
        {
            "id": "review-diff",
            "title": "Review generated diff",
            "command": "git status --short && git diff --stat",
        },
    ]
    steps.extend(
        {
            "id": f"validate-{index}",
            "title": f"Validate: {command}",
            "command": command,
        }
        for index, command in enumerate(validation_commands, start=1)
    )
    steps.extend(
        [
            {
                "id": "stage-onboarding-files",
                "title": "Stage onboarding files",
                "command": stage_command,
            },
            {
                "id": "commit-onboarding",
                "title": "Commit onboarding branch",
                "command": shell_command("git", "commit", "-m", commit_message),
            },
            {
                "id": "push-onboarding",
                "title": "Push onboarding branch",
                "command": shell_command("git", "push", "-u", remote, branch),
            },
        ]
    )

    payload: dict[str, Any] = {
        "schema_version": 1,
        "command": "onboarding-pr",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False, reason="onboarding generator emits instructions only"),
        "sidecar_writes": sidecar_writes(False, reason="dry run" if not args.write_sidecar else "before sidecar write"),
        "sidecar_state": sidecar_state(repo),
        "onboarding_pr": {
            "artifacts": None,
            "opens_pull_request": False,
            "uses_github_api": False,
            "note": "The generator does not install files, create a branch, commit, push, or open a PR.",
        },
        "install_plan": {
            "preset": args.preset,
            "profile": args.profile,
            "profiles_arg": args.profiles,
            "profiles": profiles,
            "runtime_adapters": runtime_adapters,
            "force": bool(args.force),
            "expected_paths": stage_paths,
        },
        "instructions": {
            "working_directory": str(repo),
            "branch": branch,
            "base_ref": base_ref,
            "remote": remote,
            "commit_message": commit_message,
            "pr_title": pr_title,
            "pr_body": "",
            "install_command": install_command,
            "stage_command": stage_command,
            "validation_commands": validation_commands,
            "steps": steps,
            "pr_instructions": [
                f"Open a PR manually from `{branch}` into the repository default branch after pushing.",
                "Use the generated title and body; do not create the PR through this CLI.",
            ],
        },
        "status": {
            "dirty": status["git"]["dirty"],
            "branch": current_branch,
            "installed": status["install"]["installed"],
            "kit_version": status["install"]["kit_version"],
        },
        "warnings": [],
        "exit_code": 0,
    }
    payload["instructions"]["pr_body"] = onboarding_pr_body(payload)

    if status["git"]["dirty"]:
        payload["warnings"].append("Target repo is dirty; start from a clean worktree before following the branch instructions.")
    if status["install"]["installed"]:
        payload["warnings"].append("repo-contract-kit already appears installed; use update-plan or update for maintenance changes.")
    if git_ref_exists(repo, f"refs/heads/{branch}"):
        payload["warnings"].append(f"Local branch already exists: {branch}")
    if remote and remote not in git_lines(repo, ["remote"]):
        payload["warnings"].append(f"Remote is not configured locally: {remote}")

    if args.write_sidecar:
        return write_onboarding_pr_sidecar(repo, payload)
    return payload


def agent_brief(payload: dict[str, Any]) -> str:
    lines = [
        "# Agent Brief",
        "",
        f"- Command: `{payload['command']}`",
        f"- Repo: `{payload['repo']}`",
        f"- Kit version: `{kit_version()}`",
    ]
    next_commands = payload.get("next_commands") or payload.get("recommended_commands") or []
    if next_commands:
        lines.extend(["", "## Next Commands", ""])
        lines.extend(f"- `{command}`" for command in next_commands)
    return "\n".join(lines) + "\n"


def write_sidecar_json_artifact(repo: Path, payload: dict[str, Any], directory_key: str, filename: str, reason: str) -> dict[str, Any]:
    state, init_paths = ensure_sidecar(repo, reason)
    artifact_path = Path(state["paths"][directory_key]) / filename
    payload["sidecar_state"] = state
    payload["sidecar_writes"] = sidecar_writes(True, paths=init_paths + [str(artifact_path)], reason=reason)
    write_json_file(artifact_path, payload)
    return payload


def unified_new_file_patch(repo: Path, relpath: str) -> str:
    path = repo / relpath
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise CliError(f"Untracked file is not UTF-8 text and cannot be included in automation patch: {relpath}") from exc
    except OSError as exc:
        raise CliError(f"Untracked file could not be read for automation patch: {relpath}: {exc}") from exc

    lines = text.splitlines(keepends=True)
    count = len(lines)
    header_count = f",{count}" if count != 1 else ""
    patch_lines = [
        f"diff --git a/{relpath} b/{relpath}\n",
        "new file mode 100644\n",
        "--- /dev/null\n",
        f"+++ b/{relpath}\n",
        f"@@ -0,0 +1{header_count} @@\n",
    ]
    if not lines:
        return "".join(patch_lines)
    for line in lines:
        patch_lines.append("+" + line)
        if not line.endswith("\n"):
            patch_lines.append("\n\\ No newline at end of file\n")
    return "".join(patch_lines)


def automation_patch(repo: Path, allowed_entries: list[dict[str, Any]]) -> tuple[str, list[str]]:
    allowed_paths = sorted({entry["path"] for entry in allowed_entries})
    untracked_paths = sorted(entry["path"] for entry in allowed_entries if entry["code"] == "??")
    result = run_git(repo, ["diff", "--binary", "HEAD", "--", *allowed_paths])
    if result.returncode != 0:
        raise CliError(result.stderr.strip() or "Unable to generate automation handoff patch.")
    patch_parts = [result.stdout] if result.stdout else []
    for relpath in untracked_paths:
        patch_parts.append(unified_new_file_patch(repo, relpath))
    return "".join(patch_parts), untracked_paths


def write_automation_handoff_artifacts(repo: Path, payload: dict[str, Any], patch_text: str | None) -> dict[str, Any]:
    state, init_paths = ensure_sidecar(repo, "automation-handoff")
    handoff_dir = Path(state["paths"]["automation_handoffs_dir"])
    stamp = artifact_stamp()
    label = safe_artifact_name(payload.get("label") or payload["worktree"].get("branch") or "automation")
    receipt_path = handoff_dir / f"{stamp}-{label}.json"
    paths = init_paths + [str(receipt_path)]
    payload["sidecar_state"] = state

    if patch_text is not None:
        patch_path = handoff_dir / f"{stamp}-{label}.patch"
        write_text_file(patch_path, patch_text)
        payload["patch"] = {
            "path": str(patch_path),
            "bytes": len(patch_text.encode("utf-8")),
            "line_count": len(patch_text.splitlines()),
            "apply_command": f"git apply {patch_path}",
        }
        paths.append(str(patch_path))
    else:
        payload["patch"] = None

    payload["receipt"] = {"path": str(receipt_path)}
    payload["run_id"] = payload.get("run_id") or stamp
    payload["automation_id"] = payload.get("automation_id") or payload.get("label")
    payload["owner_label"] = payload.get("owner_label") or "automation-handoff"
    payload["attribution"] = attribution_object(
        owner=payload.get("owner"),
        owner_label=payload.get("owner_label"),
        session_id=payload.get("session_id"),
        thread_id=payload.get("thread_id"),
        automation_id=payload.get("automation_id"),
        run_id=payload.get("run_id"),
        latest_receipt_path=str(receipt_path),
        latest_receipt_provenance="receipt",
        source="receipt",
    )
    payload["sidecar_writes"] = sidecar_writes(True, paths=paths, reason="automation-handoff")
    write_json_file(receipt_path, payload)
    return payload


def automation_original_baseline_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    original_root = require_git_repo(args.original_root) if args.original_root else primary_checkout(repo)
    original = original_checkout_summary(original_root, repo)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "command": "automation-handoff",
        "action": "capture-original-baseline",
        "repo": str(repo),
        "label": args.label or "original-baseline",
        "mode": args.mode,
        "created_at": now(),
        "target_repo_writes": target_repo_writes(False, reason="automation baseline writes sidecar artifacts only"),
        "sidecar_writes": sidecar_writes(False, reason="dry run" if args.dry_run else "baseline before sidecar write"),
        "sidecar_state": sidecar_state(repo),
        "allowed_paths": args.allow_path or list(AUTOMATION_HANDOFF_DEFAULT_PATHS),
        "changed_files": [],
        "allowed_changed_files": [],
        "disallowed_changed_files": [],
        "untracked_included": [],
        "worktree": git_worktree_metadata(repo),
        "original_checkout": original,
        "blockers": [],
        "warnings": [],
        "result": "passed",
        "exit_code": 0,
        "patch": None,
        "receipt": None,
    }
    if args.dry_run:
        return payload, 0
    payload = write_automation_handoff_artifacts(repo, payload, None)
    return payload, payload["exit_code"]


def automation_handoff_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    if args.capture_original_baseline:
        return automation_original_baseline_payload(args, repo)

    allowed_paths = args.allow_path or list(AUTOMATION_HANDOFF_DEFAULT_PATHS)
    status_entries = git_status_entries(repo)
    allowed_entries, disallowed_entries = split_allowed_changes(status_entries, allowed_paths)
    worktree = git_worktree_metadata(repo)
    blockers: list[str] = []
    warnings: list[str] = []
    original: dict[str, Any] | None = None

    if not status_entries:
        blockers.append("No changed files to hand off.")
    if disallowed_entries:
        blockers.append("Changed files outside automation handoff scope.")
    if args.require_linked_worktree and not worktree["linked_worktree"] and not args.allow_primary_checkout:
        blockers.append("Automation handoff must run from a linked worktree, not the primary checkout.")
    if args.mode == "branch":
        branch = worktree.get("branch") or ""
        if worktree.get("detached"):
            blockers.append("Branch handoff requires a named branch; current HEAD is detached.")
        elif branch in DEFAULT_BRANCH_NAMES and not args.allow_default_branch:
            blockers.append(f"Branch handoff refuses default branch {branch!r}.")
    if args.original_root or args.original_baseline:
        original_root = require_git_repo(args.original_root) if args.original_root else primary_checkout(repo)
        original = original_checkout_summary(original_root, repo)
        if args.original_baseline:
            baseline, baseline_error = load_original_baseline(args.original_baseline)
            if baseline_error:
                blockers.append(baseline_error)
            elif baseline and Path(str(baseline.get("root"))).resolve() != original_root:
                blockers.append("Original checkout baseline root does not match --original-root.")
                original["baseline"] = baseline
            elif baseline:
                comparison = compare_original_baseline(original, baseline)
                original["baseline"] = {
                    "path": baseline.get("path"),
                    "root": baseline.get("root"),
                    "dirty": baseline.get("dirty"),
                    "changed_files": baseline.get("changed_files", []),
                    "state_sha256": baseline.get("state_sha256"),
                    "captured_at": baseline.get("captured_at"),
                    "receipt_created_at": baseline.get("receipt_created_at"),
                }
                original["baseline_comparison"] = comparison
                original["changed_since_baseline"] = comparison["changed_since_baseline"]
        if original_root == repo:
            blockers.append("Original checkout and automation repo are the same path.")
        if args.original_baseline:
            if original and original.get("changed_since_baseline"):
                if not (args.allow_dirty_original or args.allow_original_baseline_drift):
                    blockers.append("Original checkout changed since baseline; automation handoff must leave original checkout untouched.")
        elif original["dirty"] and not args.allow_dirty_original:
            blockers.append("Original checkout is dirty; automation handoff must leave it clean.")

    patch_text: str | None = None
    untracked_included: list[str] = []
    if not blockers:
        patch_text, untracked_included = automation_patch(repo, allowed_entries)
        if not patch_text.strip():
            blockers.append("No patch content was generated for the changed files.")

    changed_path_list = sorted(entry["path"] for entry in status_entries)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "command": "automation-handoff",
        "repo": str(repo),
        "label": args.label,
        "mode": args.mode,
        "created_at": now(),
        "target_repo_writes": target_repo_writes(False, reason="automation handoff writes sidecar artifacts only"),
        "sidecar_writes": sidecar_writes(False, reason="dry run" if args.dry_run else "blocked before sidecar write"),
        "sidecar_state": sidecar_state(repo),
        "allowed_paths": allowed_paths,
        "changed_files": changed_path_list,
        "allowed_changed_files": sorted(entry["path"] for entry in allowed_entries),
        "disallowed_changed_files": sorted(entry["path"] for entry in disallowed_entries),
        "untracked_included": untracked_included,
        "worktree": worktree,
        "original_checkout": original,
        "blockers": blockers,
        "warnings": warnings,
        "result": "blocked" if blockers else "passed",
        "exit_code": 1 if blockers else 0,
    }

    if args.dry_run:
        payload["patch"] = {
            "bytes": len(patch_text.encode("utf-8")) if patch_text else 0,
            "line_count": len(patch_text.splitlines()) if patch_text else 0,
            "path": None,
        }
        payload["receipt"] = None
        return payload, payload["exit_code"]

    payload = write_automation_handoff_artifacts(repo, payload, None if blockers else patch_text)
    return payload, payload["exit_code"]


def write_orient_sidecar(repo: Path, payload: dict[str, Any]) -> dict[str, Any]:
    reason = "orient --write-sidecar"
    state, init_paths = ensure_sidecar(repo, reason)
    run_dir = Path(state["paths"]["runs_dir"]) / f"{artifact_stamp()}-orient"
    session_path = run_dir / "session-start.json"
    brief_path = run_dir / "agent-brief.md"
    payload["sidecar_state"] = state
    payload["state"]["sidecar_state"] = state
    payload["state"]["sidecar_run_dir"] = str(run_dir)
    payload["sidecar_writes"] = sidecar_writes(
        True,
        paths=init_paths + [str(run_dir), str(session_path), str(brief_path)],
        reason=reason,
    )
    write_json_file(session_path, payload)
    write_text_file(brief_path, agent_brief(payload))
    return payload


def orient_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    cli = str(CLI_ENTRYPOINT)
    doc_args = argparse.Namespace(
        config=args.config,
        changed_files=None,
        staged=False,
        working_tree=True,
        no_docs_needed=None,
    )
    docs, _ = doc_impact_payload(doc_args, repo)
    payload = {
        "schema_version": 1,
        "command": "orient",
        "repo": str(repo),
        "mode": args.mode,
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "status": status_payload(repo),
        "doc_impact": docs,
        "state": {
            "write_performed": False,
            "sidecar_state": sidecar_state(repo),
            "note": "Orient reports deterministic sidecar paths and creates run packets only when --write-sidecar is set.",
        },
        "next_commands": [
            f"{cli} sidecar-init --repo <repo> --json",
            f"{cli} doc-impact --repo <repo> --working-tree --json",
            f"{cli} review-plan --repo <repo> --mode pull-request --json",
            f"{cli} verify --repo <repo> --json",
        ],
    }
    if args.write_sidecar:
        return write_orient_sidecar(repo, payload)
    return payload


def review_plan_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    cli = str(CLI_ENTRYPOINT)
    status = status_payload(repo)
    installed = status["install"]["installed"]
    payload = {
        "schema_version": 1,
        "command": "review-plan",
        "repo": str(repo),
        "mode": args.mode,
        "trust_profile": args.trust_profile,
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "installed": installed,
        "recommended_prompts": [
            ".agent-workflows/repo-review.md",
            ".codex/prompts/multi-agent-repo-review.md",
        ]
        if installed
        else [],
        "recommended_commands": [
            f"{cli} doc-impact --repo <repo> --working-tree --json",
            f"{cli} status --repo <repo> --json",
        ],
        "notes": [
            "No repo files are written by review-plan.",
            "Install repo-contract-kit only when the repository owner wants the contract checked in.",
        ],
    }
    if args.write_sidecar:
        filename = f"{artifact_stamp()}-review-plan.json"
        return write_sidecar_json_artifact(repo, payload, "review_artifacts_dir", filename, "review-plan --write-sidecar")
    return payload


def task_packet_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    scopes = args.scope or []
    goal_report = goal_check.build_goal_check_report(repo, scopes, goal_check.CONFIG_FILE)
    task_slug = safe_artifact_name(args.task_id)
    payload = {
        "schema_version": 1,
        "command": "task-packet",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "task": {
            "id": args.task_id,
            "title": args.title,
            "priority": args.priority,
            "status": "draft",
            "source": {
                "type": args.source_type,
                "reference": args.source_reference,
            },
        },
        "context": {
            "repo_root": str(repo),
            "mode": args.mode,
            "problem_statement": args.problem,
            "background": args.background or [],
            "non_goals": args.non_goal or [],
        },
        "scope": {
            "allowed_files": scopes,
            "protected_files": args.protected_file or [],
            "inspect_first": args.inspect_first or [],
            "expected_outputs": args.expected_output or [],
        },
        "goal_alignment": goal_check.goal_alignment_from_report(goal_report),
        "acceptance_criteria": [
            {
                "description": item,
                "verification": "Capture command output or file diff evidence.",
            }
            for item in (args.acceptance or ["Implementation scope is explicit and verifiable."])
        ],
        "validation": {
            "commands": [
                {"command": command, "required": True}
                for command in (args.validation or ["make test", "make docs-check", "make version-check"])
            ],
            "evidence_to_capture": [
                "git diff --check",
                "test output",
                "docs-impact result",
            ],
        },
        "closeout_requirements": {
            "final_receipt_path": f".agent-workflows/tasks/{task_slug}/receipt.json or sidecar equivalent",
            "readiness_check": {
                "command": f"make agent-task-ready TASK={args.task_id} TASK_READY_JSON=1 or record why unavailable",
                "expected_result": "readiness passes or blocker is recorded before handoff",
            },
            "lifecycle_action": {
                "action": "finish",
                "command": (
                    f"make agent-task-finalize TASK={args.task_id} "
                    f"TASK_RECEIPT=.agent-workflows/tasks/{task_slug}/receipt.json TASK_FINALIZE_JSON=1"
                ),
                "expected_result": "task metadata is terminal and the final receipt is linked, or fallback receipt is durable",
            },
            "final_task_status": {
                "command": "make agent-task-status TASK_STATUS_INCLUDE_CLOSED=1 TASK_STATUS_JSON=1",
                "expected_result": "terminal task state, final receipt, and active overlaps are visible",
            },
            "closeout_preview": {
                "command": "make agent-task-closeout TASK_CLOSEOUT_JSON=1",
                "expected_result": "eligible, retained, or blocked cleanup state is recorded",
                "apply_requires_explicit_approval": True,
            },
            "dirty_state_explanation": (
                "Record whether the checkout is clean, contains only expected task artifacts, "
                "or preserves unrelated dirty work."
            ),
        },
        "docs_impact": {
            "expected": args.docs_impact,
            "paths": args.docs_path or [],
            "waiver_allowed": args.docs_impact == "no",
            "notes": "Update docs when CLI behavior, commands, flags, output, or migration workflow changes.",
        },
        "risk": {
            "level": args.risk,
            "known_risks": args.known_risk or [],
            "stop_conditions": args.stop_condition
            or [
                "The task needs repository-owner approval to write kit files into a third-party repo.",
                "The implementation would combine sidecar state or migration behavior into the initial CLI slice.",
            ],
        },
        "approval": {
            "human_approval_required": True,
            "state": "approved" if args.approved else "not-requested",
            "approver": args.approver,
            "notes": args.approval_note or "",
        },
        "handoff": {
            "recommended_prompt": "workflows/prompts/task-packet.md",
            "owner": args.owner,
            "dependencies": args.dependency or [],
            "next_packet_hint": args.next_packet_hint,
        },
    }
    if args.write_sidecar:
        filename = f"{task_slug}.json"
        return write_sidecar_json_artifact(repo, payload, "task_packets_dir", filename, "task-packet --write-sidecar")
    return payload


def verify_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    doc_args = argparse.Namespace(
        config=args.config,
        changed_files=args.changed_files,
        staged=args.staged,
        working_tree=args.working_tree,
        no_docs_needed=args.no_docs_needed,
    )
    docs, docs_exit = doc_impact_payload(doc_args, repo)
    payload = {
        "schema_version": 1,
        "command": "verify",
        "repo": str(repo),
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(repo),
        "status": status_payload(repo),
        "doc_impact": docs,
        "result": "failed" if docs_exit else "passed",
        "exit_code": docs_exit,
    }
    if args.write_sidecar:
        filename = f"{artifact_stamp()}-verify.json"
        payload = write_sidecar_json_artifact(repo, payload, "receipts_dir", filename, "verify --write-sidecar")
    return payload, docs_exit


def backlog_task_packet_payload(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    item = backlog_item_by_id(repo, args.backlog_id)
    if item is None:
        raise CliError(f"Backlog item not found: {args.backlog_id}", exit_code=1)
    source_ref = f"{item['source_path']}:{item['source_line']}"
    task_args = argparse.Namespace(
        task_id=item["id"],
        title=item.get("title") or item["id"],
        problem=item.get("why") or item.get("title") or item["id"],
        priority=normalize_priority(item.get("priority")),
        mode=args.mode,
        source_type="backlog",
        source_reference=source_ref,
        scope=args.scope or [],
        protected_file=args.protected_file or [],
        inspect_first=args.inspect_first or ["AGENTS.md", "REVIEW.md", item["source_path"]],
        expected_output=args.expected_output or [],
        background=[value for value in [item.get("delivery_shape")] if value],
        non_goal=args.non_goal or [],
        acceptance=args.acceptance or [f"Backlog item {item['id']} is implemented and its status can be marked done."],
        validation=args.validation or ["make agent-verify"],
        docs_impact=args.docs_impact,
        docs_path=args.docs_path or [],
        risk=args.risk,
        known_risk=args.known_risk or [],
        stop_condition=args.stop_condition or [],
        approved=args.approved,
        approver=args.approver,
        approval_note=args.approval_note,
        owner=args.owner,
        dependency=args.dependency or [],
        next_packet_hint=args.next_packet_hint,
        write_sidecar=args.write_sidecar,
    )
    payload = task_packet_payload(task_args, repo)
    payload["command"] = "agent-task-packet-from-backlog"
    payload["backlog_item"] = item
    return payload


def update_plan_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    kit = Path(args.kit).expanduser().resolve()
    command = [sys.executable, str(kit / "scripts" / "update.py"), str(repo), "--plan-json"]
    for option in ("preset", "profiles", "runtime_adapters"):
        value = getattr(args, option, None)
        if value:
            command.extend([f"--{option.replace('_', '-')}", value])
    for value in getattr(args, "runtime_adapter", None) or []:
        command.extend(["--runtime-adapter", value])
    if getattr(args, "force_managed", False):
        command.append("--force-managed")

    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    try:
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}

    if not isinstance(payload, dict) or not payload:
        return (
            {
                "schema_version": 1,
                "command": "update-plan",
                "repo": str(repo),
                "kit": str(kit),
                "target_repo_writes": target_repo_writes(False, reason="plan command failed before target writes"),
                "sidecar_writes": sidecar_writes(False),
                "sidecar_state": sidecar_state(repo),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": "Unable to parse update plan JSON.",
            },
            result.returncode or 2,
        )

    state = sidecar_state(repo)
    payload["sidecar_state"] = state
    payload["target_repo_writes"] = target_repo_writes(False, reason="plan-only command")
    payload["sidecar_writes"] = sidecar_writes(False)
    detected = payload.get("detected_state")
    if isinstance(detected, dict) and detected.get("kind") == "not_installed" and state.get("available"):
        detected["kind"] = "sidecar_only"
        detected["sidecar_only"] = True
        payload.setdefault("warnings", []).append(
            {
                "code": "sidecar_only",
                "message": "Sidecar state exists, but repo-contract-kit is not installed in the target repo.",
                "path": state["repo_state_dir"],
            }
        )
        if isinstance(payload.get("summary"), dict):
            payload["summary"]["warnings"] = len(payload.get("warnings", []))
    return payload, result.returncode


def render_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def render_status(payload: dict[str, Any]) -> None:
    install = payload["install"]
    print(f"repo: {payload['repo']}")
    print(f"dirty: {str(payload['git']['dirty']).lower()}")
    print(f"repo-contract-kit installed: {str(install['installed']).lower()}")
    if install["installed"]:
        print(f"kit version: {install['kit_version'] or 'unknown'}")
        print(f"runtime adapters: {', '.join(install['runtime_adapters']) or 'none'}")
        print(f"managed files: {install['managed_file_count']}")
        print(f"target-owned files: {install['target_owned_file_count']}")
    if install["makefile_boundary"]:
        print(install["makefile_boundary"])


def render_doc_impact(payload: dict[str, Any]) -> None:
    if not payload["changed_files"]:
        print("No changed files detected.")
        return
    print("Changed files:")
    for path in payload["changed_files"]:
        print(f" - {path}")
    if not payload["categories"]:
        print("No doc-impacting paths detected.")
        return
    print("Detected possible doc-impact categories:")
    for category in payload["categories"]:
        print(f" - {category['category']}: {', '.join(category['changed_files'])}")
    if payload["missing_categories"]:
        print(f"Missing documentation coverage for: {', '.join(payload['missing_categories'])}")


def render_backlog_status(payload: dict[str, Any]) -> None:
    print(f"Backlog status for {payload['repo']}:")
    print(f" - selected source: {payload['selected_source'] or '(none)'}")
    counts = payload["counts"]
    print(
        " - counts: "
        f"{counts['open']} open, {counts['partial']} partial, {counts['done']} done, {counts['total']} total"
    )
    if payload.get("next_open_item"):
        item = payload["next_open_item"]
        print(f" - next open: {item['id']} [{item['priority']}] {item['title']}")
    if payload["warnings"]:
        print(" - warnings:")
        for warning in payload["warnings"]:
            print(f"   - {warning}")


def render_agent_next(payload: dict[str, Any]) -> None:
    print(f"Agent next for {payload['repo']}:")
    selected = payload.get("selected_item")
    if selected:
        print(f" - selected: {selected['id']} [{selected['priority']}] {selected['title']}")
        print(f" - source: {selected['source_path']}:{selected['source_line']}")
    else:
        print(" - selected: (none)")
    print(f" - dirty: {str(payload['status']['dirty']).lower()}")
    print(f" - active tasks: {payload['task_status']['active_task_count']}")
    if payload["notes"]:
        print(" - notes:")
        for note in payload["notes"]:
            print(f"   - {note}")
    print(" - recommended commands:")
    for command in payload["recommended_commands"]:
        print(f"   - {command}")


def render_agent_context_bundle(payload: dict[str, Any]) -> None:
    summary = payload.get("summary") or {}
    print(f"Agent context bundle for {payload['repo']}:")
    print(f" - result: {summary.get('result')}")
    print(f" - mode: {payload.get('mode')}")
    print(f" - dirty: {str(summary.get('dirty')).lower()} ({summary.get('changed_file_count', 0)} changed)")
    if summary.get("next_item_id"):
        print(f" - next item: {summary['next_item_id']}")
    print(f" - active tasks: {summary.get('active_task_count', 0)}")
    print(f" - docs result: {summary.get('docs_result')}")
    print(f" - goal result: {summary.get('goal_result')}")
    print(f" - estimated context tokens: {summary.get('token_estimated', 0)}")
    print(" - sections:")
    for name, status in (summary.get("section_statuses") or {}).items():
        print(f"   - {name}: {status}")
    if payload.get("omissions"):
        print(" - omissions:")
        for item in payload["omissions"]:
            print(
                "   - "
                f"{item['section']}.{item['field']}: omitted {item['omitted_count']} "
                f"after limit {item['limit']}"
            )
    print(" - recommended commands:")
    for command in (payload.get("readiness_hints") or {}).get("recommended_commands", []):
        print(f"   - {command}")


def render_instruction_diet(payload: dict[str, Any]) -> None:
    print(f"Instruction diet audit for {payload['repo']}:")
    print(f" - status: {payload['status']}")
    print(f" - files checked: {payload['files_checked']}")
    print(f" - recommendations: {payload['recommendation_count']}")
    lint_summary = payload.get("lint_summary") or {}
    print(
        " - lint issues: "
        f"{lint_summary.get('error_count', 0)} error, "
        f"{lint_summary.get('warning_count', 0)} warning"
    )
    if payload.get("omissions"):
        print(" - omissions:")
        for item in payload["omissions"]:
            print(f"   - {item['section']}: {item['reason']}")
    if not payload.get("recommendations"):
        print(" - no instruction diet recommendations")
        return
    print(" - recommendations:")
    for item in payload["recommendations"][:20]:
        line = f":{item['line']}" if item.get("line") else ""
        print(
            f"   - [{item['severity']}] {item['path']}{line} "
            f"{item['category']} -> {item['suggested_destination']}"
        )
        print(f"     reason: {item['reason']}")
        print(f"     action: {item['action']}")
    if len(payload["recommendations"]) > 20:
        print(f"   - omitted {len(payload['recommendations']) - 20} additional recommendation(s); use --json")


def render_agent_preflight(payload: dict[str, Any]) -> None:
    print(f"Agent preflight for {payload['repo']}:")
    print(f" - result: {payload['result']}")
    print(f" - dirty: {str(payload['dirty']['dirty']).lower()} ({payload['dirty']['count']} changed)")
    print(f" - tracked/untracked: {payload['dirty']['tracked_count']} / {payload['dirty']['untracked_count']}")
    print(f" - registered worktrees: {payload['worktrees']['registered_count']}")
    print(f" - dirty worktrees: {payload['worktrees']['dirty_count']}")
    print(f" - active tasks: {payload['tasks']['active_count']}")
    print(f" - task metadata records: {payload['tasks']['count']}")
    print(f" - sidecar available: {str(payload['sidecar']['available']).lower()}")
    if payload.get("receipt"):
        print(f" - receipt: {payload['receipt']['path']}")
    if payload["dirty"]["entries"]:
        print(" - changed files:")
        for entry in payload["dirty"]["entries"]:
            print(f"   - {entry['code']} {entry['path']}")
        print(f" - dirty attribution: {render_attribution(payload['dirty'].get('attribution') or unknown_attribution())}")
    if payload["blockers"]:
        print(" - blockers:")
        for blocker in payload["blockers"]:
            print(f"   - {blocker}")
    if payload.get("blocker_details"):
        print(" - blocker attribution:")
        for detail in payload["blocker_details"]:
            label = detail.get("task_id") or detail.get("path") or detail.get("receipt") or detail.get("code")
            print(f"   - {label}: {render_attribution(detail.get('attribution') or unknown_attribution())}")
    if payload["warnings"]:
        print(" - warnings:")
        for warning in payload["warnings"]:
            print(f"   - {warning}")
    if payload.get("warning_details"):
        print(" - warning attribution:")
        for detail in payload["warning_details"]:
            label = detail.get("task_id") or detail.get("path") or detail.get("code")
            print(f"   - {label}: {render_attribution(detail.get('attribution') or unknown_attribution())}")
    print(" - recommended commands:")
    for command in payload["recommendations"]:
        print(f"   - {command}")


def render_agent_self_heal(payload: dict[str, Any]) -> None:
    print(f"Agent self-heal for {payload['repo']}:")
    print(f" - result: {payload['result']}")
    print(f" - apply: {str(payload['apply']).lower()}")
    if payload.get("receipt"):
        print(f" - receipt: {payload['receipt']['path']}")
    plan = payload.get("plan") or {}
    print(f" - planned actions: {len(plan.get('actions') or [])}")
    for action in plan.get("actions") or []:
        target = action.get("path") or action.get("target") or "(sidecar)"
        print(f"   - {action['action']}: {target}")
        print(f"     reason: {action['reason']}")
    if plan.get("allowed_tracked_changes"):
        print(" - operator-scoped tracked generated paths:")
        for entry in plan["allowed_tracked_changes"]:
            print(f"   - {entry['code']} {entry['path']}")
    if plan.get("blocked_tracked_changes"):
        print(" - blocked tracked changes:")
        for entry in plan["blocked_tracked_changes"]:
            print(f"   - {entry['code']} {entry['path']}")
    if plan.get("unrecognized_untracked"):
        print(" - unrecognized untracked files:")
        for entry in plan["unrecognized_untracked"]:
            print(f"   - {entry['path']}")
    if payload.get("applied_actions"):
        print(" - applied actions:")
        for action in payload["applied_actions"]:
            if action["action"] == "sidecar-init":
                print(f"   - initialized sidecar ({len(action.get('paths') or [])} paths)")
            elif action.get("applied"):
                print(f"   - moved {action['path']} -> {action['quarantine_path']}")
            else:
                print(f"   - skipped {action.get('path') or action['action']}: {action.get('skip_reason')}")
    if payload["blockers"]:
        print(" - blockers:")
        for blocker in payload["blockers"]:
            print(f"   - {blocker}")
    if payload["warnings"]:
        print(" - warnings:")
        for warning in payload["warnings"]:
            print(f"   - {warning}")
    if not payload["apply"]:
        print(" - apply command: make agent-self-heal SELF_HEAL_APPLY=1")


def render_automation_handoff(payload: dict[str, Any]) -> None:
    print(f"Automation handoff for {payload['repo']}:")
    if payload.get("action"):
        print(f" - action: {payload['action']}")
    print(f" - result: {payload['result']}")
    print(f" - mode: {payload['mode']}")
    print(f" - changed files: {len(payload['changed_files'])}")
    original = payload.get("original_checkout")
    if original:
        print(f" - original checkout dirty: {str(original['dirty']).lower()}")
        comparison = original.get("baseline_comparison")
        if comparison:
            print(f" - original changed since baseline: {str(comparison['changed_since_baseline']).lower()}")
    if payload["patch"]:
        print(f" - patch: {payload['patch']['path'] or '(dry-run)'}")
    if payload.get("receipt"):
        print(f" - receipt: {payload['receipt']['path']}")
    if payload["blockers"]:
        print(" - blockers:")
        for blocker in payload["blockers"]:
            print(f"   - {blocker}")
    if payload["disallowed_changed_files"]:
        print(" - disallowed files:")
        for path in payload["disallowed_changed_files"]:
            print(f"   - {path}")


def render_onboarding_pr(payload: dict[str, Any]) -> None:
    instructions = payload["instructions"]
    print(f"Onboarding PR for {payload['repo']}:")
    print(f" - branch: {instructions['branch']}")
    print(f" - base ref: {instructions['base_ref']}")
    print(f" - target writes performed: {str(payload['target_repo_writes']['performed']).lower()}")
    if payload["onboarding_pr"].get("artifacts"):
        artifacts = payload["onboarding_pr"]["artifacts"]
        print(f" - markdown: {artifacts['markdown']}")
        print(f" - json: {artifacts['json']}")
    if payload["warnings"]:
        print(" - warnings:")
        for warning in payload["warnings"]:
            print(f"   - {warning}")
    print(" - commands:")
    for step in instructions["steps"]:
        print(f"   # {step['title']}")
        print(f"   {step['command']}")
    print(" - PR title:")
    print(f"   {instructions['pr_title']}")


def path_inside(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def repo_relative(repo: Path, path: Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()


def path_under_candidate(path: str, candidate_rel: str) -> bool:
    normalized = path.replace("\\", "/").strip("/")
    candidate = candidate_rel.replace("\\", "/").strip("/")
    return normalized == candidate or normalized.startswith(candidate + "/")


def source_clone_kind(path: Path) -> str | None:
    markers = {
        "repo-contract-kit": [
            path / "scripts" / "repo_contract_kit.py",
            path / "scripts" / "install.py",
        ],
        "agent-workflow-kit": [
            path / "workflows" / "manifest.json",
            path / "workflows" / "prompts",
        ],
    }
    for kind, paths in markers.items():
        if any(marker.exists() for marker in paths):
            return kind
    if (path / ".git").exists():
        remote = git_text(path, ["remote", "get-url", "origin"]).lower()
        for kind, hint in SOURCE_CLONE_REMOTE_HINTS.items():
            if hint in remote:
                return kind
    return None


def discover_nested_source_clones(repo: Path, max_depth: int) -> list[dict[str, Any]]:
    root = repo.resolve()
    discovered: list[dict[str, Any]] = []
    queue: list[tuple[Path, int]] = [(root, 0)]
    seen: set[Path] = {root}
    while queue:
        current, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name)
        except OSError:
            continue
        for child in children:
            if child.name in SOURCE_CLONE_SKIP_DIRS or child.is_symlink() or not child.is_dir():
                continue
            resolved = child.resolve()
            if resolved in seen or not path_inside(root, resolved):
                continue
            seen.add(resolved)
            kind = source_clone_kind(resolved)
            if kind:
                discovered.append(
                    {
                        "path": repo_relative(root, resolved),
                        "abs_path": str(resolved),
                        "kind": kind,
                        "is_git_checkout": (resolved / ".git").exists(),
                        "remote": git_text(resolved, ["remote", "get-url", "origin"]) if (resolved / ".git").exists() else "",
                    }
                )
                continue
            queue.append((resolved, depth + 1))
    return discovered


def source_clone_repair_payload(args: argparse.Namespace, repo: Path) -> tuple[dict[str, Any], int]:
    max_depth = max(1, args.scan_depth)
    nested = discover_nested_source_clones(repo, max_depth)
    nested_paths = [item["path"] for item in nested]
    status_entries = git_status_entries(repo)
    root_kind = source_clone_kind(repo)
    root_remote = git_text(repo, ["remote", "get-url", "origin"])
    installed = (repo / ".doc-contract-kit" / "install.json").exists()
    blockers: list[dict[str, Any]] = []
    warnings: list[str] = []
    actions: list[dict[str, Any]] = []

    if root_kind and not installed:
        blockers.append(
            {
                "code": "root-source-checkout",
                "path": ".",
                "message": (
                    "Repository root looks like a source checkout. This command will not delete root files; "
                    "choose the real target repo or move the source checkout aside manually."
                ),
                "kind": root_kind,
                "remote": root_remote,
            }
        )
    elif root_kind:
        warnings.append("Repository root has source-repo markers; only nested source clone directories are eligible for automated cleanup.")

    unrelated_dirty = [
        entry
        for entry in status_entries
        if not any(path_under_candidate(entry["path"], candidate) for candidate in nested_paths)
    ]
    if unrelated_dirty:
        blockers.append(
            {
                "code": "unrelated-dirty-state",
                "message": "Target repo has dirty paths outside detected source clones.",
                "paths": [entry["path"] for entry in unrelated_dirty],
            }
        )

    for candidate in nested:
        rel_path = candidate["path"]
        abs_path = Path(candidate["abs_path"])
        tracked_paths = git_lines(repo, ["ls-files", "--", rel_path])
        nested_status = git_lines(abs_path, ["status", "--porcelain=v1", "--untracked-files=all"]) if candidate["is_git_checkout"] else []
        blocked = []
        if tracked_paths and not args.allow_tracked:
            blocked.append("tracked-in-target")
        if nested_status:
            blocked.append("dirty-nested-checkout")
        action = {
            "action": "remove-source-clone",
            "path": rel_path,
            "kind": candidate["kind"],
            "is_git_checkout": candidate["is_git_checkout"],
            "tracked_in_target": bool(tracked_paths),
            "blocked": blocked,
        }
        actions.append(action)
        if blocked:
            blockers.append(
                {
                    "code": "blocked-source-clone",
                    "path": rel_path,
                    "reasons": blocked,
                }
            )

    applied_paths: list[str] = []
    if args.apply and not blockers:
        for action in actions:
            path = (repo / action["path"]).resolve()
            if not path_inside(repo, path) or path == repo.resolve():
                blockers.append({"code": "unsafe-path", "path": action["path"], "message": "Refusing to remove an unsafe path."})
                break
            shutil.rmtree(path)
            applied_paths.append(action["path"])

    exit_code = 0
    if args.apply and blockers:
        exit_code = 2
    target_writes = target_repo_writes(
        bool(applied_paths),
        paths=applied_paths,
        reason=(
            "removed nested source clone directories"
            if applied_paths
            else ("blocked before target writes" if args.apply and blockers else "preview/no-write default")
        ),
    )
    next_commands = []
    if not installed:
        next_commands.append(public_command("setup"))
    else:
        next_commands.append(public_command("update", "--dry-run"))
        next_commands.append(public_command("update"))
    return (
        {
            "schema_version": 1,
            "command": "target repair-source-clone",
            "repo": str(repo),
            "apply": args.apply,
            "scan_depth": max_depth,
            "root_source_clone": {
                "detected": bool(root_kind),
                "kind": root_kind,
                "remote": root_remote,
            },
            "nested_source_clones": nested,
            "actions": actions,
            "applied_paths": applied_paths,
            "blockers": blockers,
            "warnings": warnings,
            "next_commands": next_commands,
            "target_repo_writes": target_writes,
            "sidecar_writes": sidecar_writes(False),
            "sidecar_state": sidecar_state(repo),
            "exit_code": exit_code,
        },
        exit_code,
    )


def render_source_clone_repair(payload: dict[str, Any]) -> None:
    print(f"Source-clone repair for {payload['repo']}:")
    print(f" - apply: {str(payload['apply']).lower()}")
    print(f" - root source checkout: {str(payload['root_source_clone']['detected']).lower()}")
    print(f" - nested source clones: {len(payload['nested_source_clones'])}")
    for item in payload["nested_source_clones"]:
        print(f"   - {item['path']} ({item['kind']})")
    if payload["blockers"]:
        print(" - blockers:")
        for blocker in payload["blockers"]:
            path = blocker.get("path")
            suffix = f" [{path}]" if path else ""
            print(f"   - {blocker['code']}{suffix}")
    if payload["applied_paths"]:
        print(" - removed:")
        for path in payload["applied_paths"]:
            print(f"   - {path}")
    print(" - next commands:")
    for command in payload["next_commands"]:
        print(f"   {command}")


def guide_payload(cwd: Path | None = None) -> dict[str, Any]:
    current = (cwd or Path.cwd()).expanduser().resolve()
    tool = self_status_payload()["tool"]
    payload: dict[str, Any] = {
        "schema_version": 1,
        "command": "guide",
        "tool": {
            "name": PUBLIC_COMMAND,
            "internal_name": INTERNAL_PRODUCT_NAME,
            "version": tool.get("version"),
            "root": tool.get("root"),
            "dirty": tool.get("dirty"),
            "ref": tool.get("short_ref"),
        },
        "cwd": str(current),
        "repo": None,
        "status": "outside-git",
        "summary": "Not inside a git repository.",
        "recommended_commands": [
            "git init",
            public_command("setup"),
            public_command("options"),
        ],
        "actions": [],
        "target_repo_writes": target_repo_writes(False),
        "sidecar_writes": sidecar_writes(False),
        "sidecar_state": sidecar_state(),
        "exit_code": 0,
    }
    try:
        repo = require_git_repo(str(current))
    except CliError:
        payload["actions"] = [
            {"key": "1", "label": "Show options", "command": [PUBLIC_COMMAND, "options"], "mutating": False},
            {"key": "q", "label": "Quit", "command": [], "mutating": False},
        ]
        return payload

    status = status_payload(repo)
    installed = bool(status["install"]["installed"])
    dirty = bool(status["git"]["dirty"])
    payload["repo"] = status["repo"]
    payload["sidecar_state"] = status["sidecar_state"]
    payload["repo_status"] = {
        "installed": installed,
        "dirty": dirty,
        "changed_file_count": len(status["git"]["changed_files"]),
        "kit_version": status["install"].get("kit_version"),
        "managed_file_count": status["install"].get("managed_file_count"),
        "runtime_adapters": status["install"].get("runtime_adapters") or [],
    }
    if not installed:
        payload["status"] = "target-not-installed"
        payload["summary"] = "This git repo is not enrolled yet."
        payload["recommended_commands"] = [
            public_command("setup"),
            public_command("status"),
            public_command("options"),
        ]
        payload["actions"] = [
            {"key": "1", "label": "Show repo status", "command": [PUBLIC_COMMAND, "status"], "mutating": False},
            {"key": "2", "label": "Set up this repo", "command": [PUBLIC_COMMAND, "setup"], "mutating": True},
            {"key": "3", "label": "Show options", "command": [PUBLIC_COMMAND, "options"], "mutating": False},
            {"key": "q", "label": "Quit", "command": [], "mutating": False},
        ]
        return payload

    if dirty:
        payload["status"] = "target-installed-dirty"
        payload["summary"] = "This repo is enrolled and has local changes."
        payload["recommended_commands"] = [
            "git status --short",
            public_command("status"),
            public_command("doctor"),
            public_command("update", "--dry-run"),
        ]
    else:
        payload["status"] = "target-installed"
        payload["summary"] = "This repo is enrolled and ready for normal management."
        payload["recommended_commands"] = [
            public_command("status"),
            public_command("update", "--dry-run"),
            public_command("update"),
            public_command("doctor"),
        ]
    payload["actions"] = [
        {"key": "1", "label": "Show repo status", "command": [PUBLIC_COMMAND, "status"], "mutating": False},
        {"key": "2", "label": "Preview repo update", "command": [PUBLIC_COMMAND, "update", "--dry-run"], "mutating": False},
        {"key": "3", "label": "Update this repo", "command": [PUBLIC_COMMAND, "update"], "mutating": True},
        {"key": "4", "label": "Run diagnostics", "command": [PUBLIC_COMMAND, "doctor"], "mutating": False},
        {"key": "5", "label": "Show options", "command": [PUBLIC_COMMAND, "options"], "mutating": False},
        {"key": "q", "label": "Quit", "command": [], "mutating": False},
    ]
    return payload


def render_guide(payload: dict[str, Any]) -> None:
    tool = payload["tool"]
    print(f"{PUBLIC_COMMAND} guide")
    print(f" - tool version: {tool.get('version') or 'unknown'}")
    print(f" - tool root: {tool.get('root') or 'unknown'}")
    print(f" - current path: {payload['cwd']}")
    if payload.get("repo"):
        repo_status = payload.get("repo_status") or {}
        print(f" - repo: {payload['repo']}")
        print(f" - installed: {str(repo_status.get('installed')).lower()}")
        print(f" - dirty: {str(repo_status.get('dirty')).lower()} ({repo_status.get('changed_file_count', 0)} changed)")
        if repo_status.get("installed"):
            print(f" - installed kit version: {repo_status.get('kit_version') or 'unknown'}")
    else:
        print(" - repo: not a git repo")
    print(f" - status: {payload['status']}")
    print(f" - next: {payload['summary']}")
    print(" - recommended commands:")
    for command in payload["recommended_commands"]:
        print(f"   {command}")


def render_options(include_advanced: bool = False) -> None:
    print(f"{PUBLIC_COMMAND} command guide")
    print("")
    print("Daily commands:")
    print(f"  {PUBLIC_COMMAND}                         Show the guided dashboard")
    print(f"  {PUBLIC_COMMAND} setup                   Enroll the current repo")
    print(f"  {PUBLIC_COMMAND} status                  Show repo install and git state")
    print(f"  {PUBLIC_COMMAND} update --dry-run        Preview managed-file updates")
    print(f"  {PUBLIC_COMMAND} update                  Apply safe managed-file updates")
    print(f"  {PUBLIC_COMMAND} doctor                  Diagnose dirty state and task blockers")
    print("")
    print("Tool management:")
    print(f"  {PUBLIC_COMMAND} update --global         Update the global tool checkout")
    print(f"  {PUBLIC_COMMAND} options                 Show this guide")
    print(f"  {PUBLIC_COMMAND} help --all              Show advanced commands")
    print("")
    print("Setup scenarios:")
    print(f"  Existing old target repo: install the new launcher, read docs/upgrade-flow.md, then run {PUBLIC_COMMAND} status and {PUBLIC_COMMAND} update --dry-run")
    print(f"  New repo before Codex or Amp: run {PUBLIC_COMMAND} setup, then make agent-start")
    print(f"  Old repo with no kit setup: run {PUBLIC_COMMAND} setup, then {PUBLIC_COMMAND} status")
    if not include_advanced:
        return
    print("")
    print("Advanced commands remain available for agents and automation:")
    for command in (
        "version --json",
        "self status --json",
        "self update --json",
        "target add/status/update/doctor",
        "orient --repo /path/to/repo --json",
        "sidecar-init --repo /path/to/repo --json",
        "agent-preflight --repo /path/to/repo --json",
        "agent-context-bundle --repo /path/to/repo --json",
        "agent-state-ledger --repo /path/to/repo --json",
        "branch-readiness --repo /path/to/repo --json",
        "doc-impact --repo /path/to/repo --working-tree --json",
        "update-plan --repo /path/to/repo --json",
    ):
        print(f"  {PUBLIC_COMMAND} {command}")


def run_guide_interactive(payload: dict[str, Any]) -> int:
    render_guide(payload)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print(f"Run `{PUBLIC_COMMAND} options` for the full command guide.")
        return 0

    actions = payload.get("actions") or []
    if not actions:
        return 0
    print("")
    print("Choose an action:")
    for action in actions:
        print(f"  {action['key']}. {action['label']}")
    choice = input("> ").strip().lower()
    selected = next((action for action in actions if action["key"] == choice), None)
    if selected is None or selected["key"] == "q":
        print("No action run.")
        return 0
    command = list(selected["command"])
    if command and command[0] == PUBLIC_COMMAND:
        command = command[1:]
    if selected.get("mutating"):
        print(f"This will run: {public_command(*command)}")
        confirmation = input("Type yes to continue: ").strip()
        if confirmation != "yes":
            print("Skipped.")
            return 0
    return main(command)


def run_mutating_script(command: list[str], repo: Path, json_output: bool, writes_on_success: bool) -> int:
    before_status = git_status_entries(repo)
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    writes_performed = writes_on_success and result.returncode == 0
    if writes_performed:
        write_reason = "explicit install/update command"
    elif result.returncode != 0:
        write_reason = "command failed before successful target writes"
    else:
        write_reason = "explicit dry-run command"
    if json_output:
        after_status = git_status_entries(repo)
        before_by_path = {entry["path"]: entry for entry in before_status}
        changed_paths = sorted(
            entry["path"]
            for entry in after_status
            if before_by_path.get(entry["path"]) != entry
        )
        update_report = latest_update_report(repo) if writes_performed else None
        report_paths = update_report_write_paths(update_report) if update_report else []
        metadata_paths = (
            [".doc-contract-kit/install.json", ".doc-contract-kit/manifest.json"]
            if writes_performed and "--metadata-only" in command
            else []
        )
        write_paths = sorted(set(report_paths or changed_paths or metadata_paths))
        payload = {
            "schema_version": 1,
            "repo": str(repo),
            "command": command,
            "target_repo_writes": target_repo_writes(
                writes_performed,
                paths=write_paths if writes_performed else [],
                reason=write_reason,
            ),
            "sidecar_writes": sidecar_writes(False),
            "sidecar_state": sidecar_state(repo),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        if update_report:
            payload["update_report"] = update_report
        render_json(
            payload
        )
    else:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def latest_update_report(repo: Path) -> dict[str, Any] | None:
    updates_dir = repo / ".doc-contract-kit" / "updates"
    if not updates_dir.exists():
        return None
    candidates = sorted(
        updates_dir.glob("*/update-report.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None
    report_path = candidates[0]
    payload = read_json(report_path)
    if not isinstance(payload, dict) or payload.get("_error"):
        return None
    payload["path"] = str(report_path.relative_to(repo))
    return payload


def update_report_write_paths(report: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for action in report.get("actions") or []:
        for path in action.get("writes_on_apply") or []:
            paths.add(path)
    if paths:
        paths.add(".doc-contract-kit/install.json")
        paths.add(".doc-contract-kit/manifest.json")
        report_path = report.get("path")
        if report_path:
            paths.add(report_path)
            paths.add(str(Path(report_path).with_suffix(".md")))
    return sorted(paths)


def add_common_repo_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=".", help="Target git repository. Defaults to the current directory.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")


def add_install_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile")
    parser.add_argument("--profiles")
    parser.add_argument("--preset")
    parser.add_argument("--runtime-adapter", action="append")
    parser.add_argument("--runtime-adapters")
    parser.add_argument("--force", action="store_true")


def install_script_command(args: argparse.Namespace, repo: Path) -> list[str]:
    command = [sys.executable, str(ROOT / "scripts" / "install.py"), str(repo)]
    for option in ("profile", "profiles", "preset", "runtime_adapters"):
        value = getattr(args, option)
        if value:
            command.extend([f"--{option.replace('_', '-')}", value])
    for value in getattr(args, "runtime_adapter", None) or []:
        command.extend(["--runtime-adapter", value])
    if getattr(args, "force", False):
        command.append("--force")
    return command


def update_script_command(args: argparse.Namespace, repo: Path, apply_default: bool = False) -> list[str]:
    kit = Path(getattr(args, "kit", str(ROOT))).expanduser().resolve()
    command = [sys.executable, str(kit / "scripts" / "update.py"), str(repo)]
    for option in ("preset", "profiles", "runtime_adapters"):
        value = getattr(args, option)
        if value:
            command.extend([f"--{option.replace('_', '-')}", value])
    for value in getattr(args, "runtime_adapter", None) or []:
        command.extend(["--runtime-adapter", value])
    if getattr(args, "dry_run", False):
        command.append("--dry-run")
    apply_update = getattr(args, "apply", False) or (apply_default and not getattr(args, "dry_run", False))
    if apply_update:
        command.append("--apply")
    if getattr(args, "metadata_only", False):
        command.append("--metadata-only")
    if getattr(args, "force_managed", False):
        command.append("--force-managed")
    return command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PUBLIC_COMMAND,
        description="Guided repo management CLI for repo-contract-kit.",
        epilog=f"Run `{PUBLIC_COMMAND}` for a guided dashboard or `{PUBLIC_COMMAND} options` for common commands.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {kit_version()}")
    subparsers = parser.add_subparsers(dest="command", required=False)

    version = subparsers.add_parser("version", help="Show CLI and kit version metadata.")
    version.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    guide = subparsers.add_parser("guide", help="Show the guided dashboard.")
    guide.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    options = subparsers.add_parser("options", help="Show the human command guide.")
    options.add_argument("--all", action="store_true", help="Include advanced automation commands.")

    help_cmd = subparsers.add_parser("help", help="Show the human command guide.")
    help_cmd.add_argument("--all", action="store_true", help="Include advanced automation commands.")

    setup = subparsers.add_parser("setup", help="Enroll the current or selected git repo.")
    add_common_repo_args(setup)
    add_install_args(setup)

    doctor = subparsers.add_parser("doctor", help="Diagnose dirty state and task blockers for the current repo.")
    add_common_repo_args(doctor)
    doctor.add_argument("--strict", action="store_true", help="Exit non-zero when startup blockers are present.")
    doctor.add_argument("--write-sidecar", action="store_true", help="Write a doctor receipt under the repo sidecar.")

    self_cmd = subparsers.add_parser("self", help="Inspect or update the global repo-contract-kit tool checkout.")
    self_subparsers = self_cmd.add_subparsers(dest="self_command", required=True)
    self_status = self_subparsers.add_parser("status", help="Show global tool checkout status.")
    self_status.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    self_update = self_subparsers.add_parser("update", help="Fetch and switch the global tool checkout to a ref.")
    self_update.add_argument("--ref", default=os.environ.get("REPO_CONTRACT_KIT_REF", "main"), help="Branch or tag to fetch from origin. Default: main.")
    self_update.add_argument(
        "--workflow-ref",
        default=os.environ.get("AGENT_WORKFLOW_KIT_REF", ""),
        help="Branch or tag for the legacy external workflow-source checkout. Defaults to --ref.",
    )
    self_update.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    sidecar_init = subparsers.add_parser("sidecar-init", help="Create sidecar directories for repo-external agent artifacts.")
    add_common_repo_args(sidecar_init)

    orient = subparsers.add_parser("orient", help="Inspect a repo and print startup context without writing files.")
    add_common_repo_args(orient)
    orient.add_argument("--mode", default="drift")
    orient.add_argument("--config", default=check_doc_impact.CONFIG_FILE)
    orient.add_argument("--write-sidecar", action="store_true", help="Write session-start.json and agent-brief.md under the repo sidecar.")

    status = subparsers.add_parser("status", help="Show git, install, and kit state.")
    add_common_repo_args(status)

    backlog_status = subparsers.add_parser("backlog-status", help="Report the repo backlog source contract and open work.")
    add_common_repo_args(backlog_status)
    backlog_status.add_argument("--include-items", action="store_true", help="Include all parsed backlog items in JSON output.")

    backlog_check = subparsers.add_parser("backlog-check", help="Validate the selected backlog source contract.")
    add_common_repo_args(backlog_check)
    backlog_check.add_argument("--include-items", action="store_true", help="Include all parsed backlog items in JSON output.")

    agent_next = subparsers.add_parser("agent-next", help="Recommend the next backlog item after checking dirty state and active tasks.")
    add_common_repo_args(agent_next)

    context_bundle = subparsers.add_parser(
        "agent-context-bundle",
        help="Emit a compact deterministic startup and handoff context bundle.",
    )
    add_common_repo_args(context_bundle)
    context_bundle.add_argument("--mode", choices=["working-tree", "staged", "branch"], default="working-tree")
    context_bundle.add_argument("--format", choices=["text", "json"], default=None)
    context_bundle.add_argument("--max-files", type=int, default=CONTEXT_BUNDLE_DEFAULT_LIMITS["files"])
    context_bundle.add_argument("--max-open-items", type=int, default=CONTEXT_BUNDLE_DEFAULT_LIMITS["open_items"])
    context_bundle.add_argument("--max-tasks", type=int, default=CONTEXT_BUNDLE_DEFAULT_LIMITS["tasks"])
    context_bundle.add_argument("--max-token-files", type=int, default=CONTEXT_BUNDLE_DEFAULT_LIMITS["token_files"])
    context_bundle.add_argument("--max-warnings", type=int, default=CONTEXT_BUNDLE_DEFAULT_LIMITS["warnings"])
    context_bundle.add_argument("--max-commands", type=int, default=CONTEXT_BUNDLE_DEFAULT_LIMITS["commands"])

    state_ledger = subparsers.add_parser(
        "agent-state-ledger",
        help="Emit a read-only ledger of dirty state, tasks, receipts, closeout state, and next safe commands.",
    )
    add_common_repo_args(state_ledger)
    state_ledger.add_argument("--format", choices=["text", "json"], default=None)

    branch_ready = subparsers.add_parser(
        "branch-readiness",
        help="Aggregate local branch/PR readiness evidence without writes or hosted governance actions.",
    )
    add_common_repo_args(branch_ready)
    branch_ready.add_argument("--base-ref", default="", help="Base ref for local branch diff and freshness.")
    branch_ready.add_argument("--head-ref", default="HEAD", help="Head ref for local branch diff.")
    branch_ready.add_argument("--target-ref", default="", help="Target ref metadata to report. Defaults to the resolved base ref.")
    branch_ready.add_argument("--config", default=check_doc_impact.CONFIG_FILE, help="Docs contract config path.")
    branch_ready.add_argument("--no-docs-needed", default="", help="Explicit no-docs-needed reason to record for this readiness run.")
    branch_ready.add_argument("--checks-json", default="", help="Local JSON export of required/advisory checks.")
    branch_ready.add_argument("--receipt", action="append", help="Local agent receipt JSON to validate. Can be repeated.")
    branch_ready.add_argument("--review-disposition-json", default="", help="Local review disposition JSON to validate.")
    branch_ready.add_argument("--task", default="", help="Prepared task id to aggregate through agent-task-ready when available.")
    branch_ready.add_argument("--task-receipt", default="", help="Receipt path passed through to agent-task-ready.")
    branch_ready.add_argument("--format", choices=["text", "json"], default=None)

    instruction_diet = subparsers.add_parser(
        "instruction-diet",
        help="Audit agent-facing instruction files and propose no-write offload targets.",
    )
    add_common_repo_args(instruction_diet)
    instruction_diet.add_argument("--file", action="append", dest="files", help="Specific instruction file to inspect.")
    instruction_diet.add_argument("--strict-paths", action="store_true", help="Treat missing path references as strict evidence.")
    instruction_diet.add_argument(
        "--budget-config",
        default=lint_agent_docs.DEFAULT_BUDGET_CONFIG,
        help="Instruction budget config relative to the repo root.",
    )
    instruction_diet.add_argument("--format", choices=["text", "json"], default=None)

    for name in ("agent-preflight", "agent-doctor"):
        preflight = subparsers.add_parser(
            name,
            help="Diagnose dirty-state startup blockers, task/worktree state, and safe recovery commands.",
        )
        add_common_repo_args(preflight)
        preflight.add_argument("--strict", action="store_true", help="Exit non-zero when startup blockers are present.")
        preflight.add_argument("--write-sidecar", action="store_true", help="Write a preflight receipt under the repo sidecar.")

    self_heal = subparsers.add_parser(
        "agent-self-heal",
        help="Preview or apply guarded generated-state repair and stale metadata quarantine.",
    )
    add_common_repo_args(self_heal)
    self_heal.add_argument("--apply", action="store_true", help="Apply the planned generated-state repairs and write a sidecar receipt.")
    self_heal.add_argument(
        "--allow-path",
        action="append",
        help="Exact generated path allowed to remain dirty during apply. Can be repeated or comma-separated.",
    )

    automation_handoff = subparsers.add_parser(
        "automation-handoff",
        help="Write an automation-safe backlog/research patch and receipt to the sidecar.",
    )
    add_common_repo_args(automation_handoff)
    automation_handoff.add_argument("--mode", choices=["patch", "branch"], default="patch")
    automation_handoff.add_argument("--label", help="Short label used in sidecar artifact filenames.")
    automation_handoff.add_argument("--allow-path", action="append", help="Allowed changed path, glob, or directory prefix. Can be repeated.")
    automation_handoff.add_argument("--original-root", help="Primary checkout that must remain clean.")
    automation_handoff.add_argument("--capture-original-baseline", action="store_true", help="Write an original-checkout baseline receipt and exit.")
    automation_handoff.add_argument("--original-baseline", help="Original-checkout baseline receipt path to compare before handoff.")
    automation_handoff.add_argument("--allow-dirty-original", action="store_true", help="Do not block when --original-root is already dirty or baseline drift is accepted.")
    automation_handoff.add_argument("--allow-original-baseline-drift", action="store_true", help="Do not block when the original checkout changed since --original-baseline.")
    automation_handoff.add_argument("--allow-primary-checkout", action="store_true", help="Allow running from the primary checkout.")
    automation_handoff.add_argument("--allow-default-branch", action="store_true", help="Allow branch mode on default branch names.")
    automation_handoff.add_argument(
        "--no-require-linked-worktree",
        action="store_false",
        dest="require_linked_worktree",
        help="Do not require a linked git worktree.",
    )
    automation_handoff.add_argument("--dry-run", action="store_true", help="Validate and report without writing sidecar artifacts.")
    automation_handoff.set_defaults(require_linked_worktree=True)

    doc_impact = subparsers.add_parser("doc-impact", help="Evaluate documentation impact for changed files.")
    add_common_repo_args(doc_impact)
    doc_impact.add_argument("--config", default=check_doc_impact.CONFIG_FILE)
    doc_impact.add_argument("--changed-file", action="append", dest="changed_files")
    doc_impact.add_argument("--staged", action="store_true")
    doc_impact.add_argument("--working-tree", action="store_true")
    doc_impact.add_argument("--no-docs-needed")
    doc_impact.add_argument("--format", choices=["text", "json", "sarif"], default=None)

    docs_explain_parser = subparsers.add_parser(
        "docs-explain",
        help="Explain local repository docs with deterministic source citations and no writes.",
    )
    add_common_repo_args(docs_explain_parser)
    docs_explain_parser.add_argument("--question", "-q", help="Question to ground in local docs.")
    docs_explain_parser.add_argument(
        "--focus",
        action="append",
        help="Topic to boost, for example docs-impact, waiver, docs-propose, add-docs, or changelog.",
    )
    docs_explain_parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        help="Repo-relative docs path, directory, or glob to scan.",
    )
    docs_explain_parser.add_argument("--max-results", type=int, default=docs_explain.DEFAULT_MAX_RESULTS)
    docs_explain_parser.add_argument("--max-snippet-lines", type=int, default=docs_explain.DEFAULT_SNIPPET_LINES)
    docs_explain_parser.add_argument("--check", action="store_true", help="Exit non-zero when no matching docs are found.")
    docs_explain_parser.add_argument("--format", choices=["text", "json"], default=None)

    docs_as_tests = subparsers.add_parser(
        "docs-as-tests",
        help="Run explicit local docs-as-tests assertions without target writes or network calls.",
    )
    add_common_repo_args(docs_as_tests)
    docs_as_tests.add_argument(
        "--config",
        default=check_docs_as_tests.DEFAULT_CONFIG,
        help=f"Config path relative to the repo root. Default: {check_docs_as_tests.DEFAULT_CONFIG}.",
    )
    docs_as_tests.add_argument("--format", choices=["text", "json"], default=None)

    goal = subparsers.add_parser("goal-check", help="Map changed files to local repo goal and area contracts.")
    add_common_repo_args(goal)
    goal.add_argument("--config", default=goal_check.CONFIG_FILE)
    goal.add_argument("--changed-file", action="append", dest="changed_files")
    goal.add_argument("--staged", action="store_true")
    goal.add_argument("--working-tree", action="store_true")
    goal.add_argument("--format", choices=["text", "json"], default=None)

    docs_propose = subparsers.add_parser(
        "docs-propose",
        help="Write reviewable docs patch proposal artifacts without modifying the target repo.",
    )
    add_common_repo_args(docs_propose)
    docs_propose.add_argument("--config", default=check_doc_impact.CONFIG_FILE)
    docs_propose.add_argument("--changed-file", action="append", dest="changed_files")
    docs_propose.add_argument("--staged", action="store_true")
    docs_propose.add_argument("--working-tree", action="store_true")
    docs_propose.add_argument(
        "--write-sidecar",
        action="store_true",
        help="Write proposal JSON, Markdown, and patch artifacts under the repo sidecar.",
    )

    changelog = subparsers.add_parser(
        "changelog-update",
        help="Propose or check changelog work from docs-impact context without modifying target files.",
    )
    add_common_repo_args(changelog)
    changelog.add_argument("--config", default=check_doc_impact.CONFIG_FILE)
    changelog.add_argument("--changed-file", action="append", dest="changed_files")
    changelog.add_argument("--staged", action="store_true")
    changelog.add_argument("--working-tree", action="store_true")
    changelog.add_argument("--docs-impact-json")
    changelog.add_argument("--summary", action="append")
    changelog.add_argument("--section")
    changelog.add_argument("--version")
    changelog.add_argument("--bump", choices=["patch", "minor", "major"])
    changelog.add_argument("--check", action="store_true")
    changelog.add_argument("--format", choices=["text", "json"], default=None)

    onboarding_pr = subparsers.add_parser(
        "onboarding-pr",
        help="Generate reviewable branch and PR instructions for installing repo-contract-kit.",
    )
    add_common_repo_args(onboarding_pr)
    onboarding_pr.add_argument("--profile")
    onboarding_pr.add_argument("--profiles")
    onboarding_pr.add_argument("--preset")
    onboarding_pr.add_argument("--runtime-adapter", action="append")
    onboarding_pr.add_argument("--runtime-adapters")
    onboarding_pr.add_argument("--branch", help="Onboarding branch name. Defaults to codex/repo-contract-kit-onboarding.")
    onboarding_pr.add_argument("--base-ref", help="Base ref for the branch instruction. Defaults to the current branch.")
    onboarding_pr.add_argument("--remote", default="origin", help="Remote name for the push instruction. Defaults to origin.")
    onboarding_pr.add_argument("--commit-message", help="Commit message for the generated instructions.")
    onboarding_pr.add_argument("--pr-title", help="Pull request title for the generated instructions.")
    onboarding_pr.add_argument("--force", action="store_true", help="Include install --force in the generated install command.")
    onboarding_pr.add_argument(
        "--write-sidecar",
        action="store_true",
        help="Write onboarding JSON and Markdown artifacts under the repo sidecar.",
    )

    review_plan = subparsers.add_parser("review-plan", help="Emit a read-only review plan for an agent.")
    add_common_repo_args(review_plan)
    review_plan.add_argument("--mode", default="pull-request")
    review_plan.add_argument("--trust-profile", default="read-only-review")
    review_plan.add_argument("--write-sidecar", action="store_true", help="Write the review plan under the repo sidecar.")

    task_packet = subparsers.add_parser("task-packet", help="Emit a task-packet JSON scaffold.")
    add_common_repo_args(task_packet)
    task_packet.add_argument("--task-id", required=True)
    task_packet.add_argument("--title", required=True)
    task_packet.add_argument("--problem", required=True)
    task_packet.add_argument("--priority", choices=["P0", "P1", "P2", "P3"], default="P1")
    task_packet.add_argument("--mode", default="drift")
    task_packet.add_argument("--source-type", choices=["backlog", "issue", "review-finding", "decision", "human-request"], default="backlog")
    task_packet.add_argument("--source-reference")
    task_packet.add_argument("--scope", action="append")
    task_packet.add_argument("--protected-file", action="append")
    task_packet.add_argument("--inspect-first", action="append")
    task_packet.add_argument("--expected-output", action="append")
    task_packet.add_argument("--background", action="append")
    task_packet.add_argument("--non-goal", action="append")
    task_packet.add_argument("--acceptance", action="append")
    task_packet.add_argument("--validation", action="append")
    task_packet.add_argument("--docs-impact", choices=["yes", "no", "unknown"], default="unknown")
    task_packet.add_argument("--docs-path", action="append")
    task_packet.add_argument("--risk", choices=["low", "medium", "high"], default="medium")
    task_packet.add_argument("--known-risk", action="append")
    task_packet.add_argument("--stop-condition", action="append")
    task_packet.add_argument("--approved", action="store_true")
    task_packet.add_argument("--approver")
    task_packet.add_argument("--approval-note")
    task_packet.add_argument("--owner")
    task_packet.add_argument("--dependency", action="append")
    task_packet.add_argument("--next-packet-hint")
    task_packet.add_argument("--write-sidecar", action="store_true", help="Write the task packet under the repo sidecar.")

    from_backlog = subparsers.add_parser("agent-task-packet-from-backlog", help="Emit a task packet scaffold for a selected backlog item.")
    add_common_repo_args(from_backlog)
    from_backlog.add_argument("--backlog-id", required=True)
    from_backlog.add_argument("--mode", default="test-first")
    from_backlog.add_argument("--scope", action="append")
    from_backlog.add_argument("--protected-file", action="append")
    from_backlog.add_argument("--inspect-first", action="append")
    from_backlog.add_argument("--expected-output", action="append")
    from_backlog.add_argument("--non-goal", action="append")
    from_backlog.add_argument("--acceptance", action="append")
    from_backlog.add_argument("--validation", action="append")
    from_backlog.add_argument("--docs-impact", choices=["yes", "no", "unknown"], default="unknown")
    from_backlog.add_argument("--docs-path", action="append")
    from_backlog.add_argument("--risk", choices=["low", "medium", "high"], default="medium")
    from_backlog.add_argument("--known-risk", action="append")
    from_backlog.add_argument("--stop-condition", action="append")
    from_backlog.add_argument("--approved", action="store_true")
    from_backlog.add_argument("--approver")
    from_backlog.add_argument("--approval-note")
    from_backlog.add_argument("--owner")
    from_backlog.add_argument("--dependency", action="append")
    from_backlog.add_argument("--next-packet-hint")
    from_backlog.add_argument("--write-sidecar", action="store_true", help="Write the task packet under the repo sidecar.")

    verify = subparsers.add_parser("verify", help="Run non-mutating local verification checks.")
    add_common_repo_args(verify)
    verify.add_argument("--config", default=check_doc_impact.CONFIG_FILE)
    verify.add_argument("--changed-file", action="append", dest="changed_files")
    verify.add_argument("--staged", action="store_true")
    verify.add_argument("--working-tree", action="store_true")
    verify.add_argument("--no-docs-needed")
    verify.add_argument("--write-sidecar", action="store_true", help="Write the verification receipt under the repo sidecar.")

    update_plan = subparsers.add_parser("update-plan", help="Emit a non-mutating migration/update plan.")
    add_common_repo_args(update_plan)
    update_plan.add_argument("--kit", default=str(ROOT), help="repo-contract-kit checkout to plan from. Defaults to this checkout.")
    update_plan.add_argument("--preset")
    update_plan.add_argument("--profiles")
    update_plan.add_argument("--runtime-adapter", action="append")
    update_plan.add_argument("--runtime-adapters")
    update_plan.add_argument("--force-managed", action="store_true")

    install = subparsers.add_parser("install", help="Explicitly install kit files into a target repo.")
    add_common_repo_args(install)
    add_install_args(install)

    target = subparsers.add_parser("target", help="Manage target repo enrollment.")
    target_subparsers = target.add_subparsers(dest="target_command", required=True)
    target_add = target_subparsers.add_parser(
        "add",
        help="Enroll the current or selected git repo by installing kit target files.",
    )
    add_common_repo_args(target_add)
    add_install_args(target_add)
    target_status = target_subparsers.add_parser("status", help="Show current or selected target repo install status.")
    add_common_repo_args(target_status)
    target_doctor = target_subparsers.add_parser(
        "doctor",
        help="Diagnose dirty state, task/worktree state, and safe recovery commands for a target repo.",
    )
    add_common_repo_args(target_doctor)
    target_doctor.add_argument("--strict", action="store_true", help="Exit non-zero when startup blockers are present.")
    target_doctor.add_argument("--write-sidecar", action="store_true", help="Write a doctor receipt under the repo sidecar.")
    target_repair_source = target_subparsers.add_parser(
        "repair-source-clone",
        help="Preview or remove accidental nested repo-contract-kit/agent-workflow-kit source clones from a target repo.",
    )
    add_common_repo_args(target_repair_source)
    target_repair_source.add_argument("--apply", action="store_true", help="Remove eligible nested source clone directories.")
    target_repair_source.add_argument(
        "--allow-tracked",
        action="store_true",
        help="Allow removal when detected source clone paths are tracked by the target repo.",
    )
    target_repair_source.add_argument(
        "--scan-depth",
        type=int,
        default=2,
        help="Directory depth to scan for nested source clones. Default: 2.",
    )
    target_update = target_subparsers.add_parser(
        "update",
        help="Apply safe managed updates to the current or selected target repo from the global tool checkout.",
    )
    add_common_repo_args(target_update)
    target_update.add_argument("--dry-run", action="store_true", help="Plan the target update without writing files.")
    target_update.add_argument("--preset")
    target_update.add_argument("--profiles")
    target_update.add_argument("--runtime-adapter", action="append")
    target_update.add_argument("--runtime-adapters")
    target_update.add_argument("--metadata-only", action="store_true")
    target_update.add_argument("--force-managed", action="store_true")

    migrate_config = subparsers.add_parser(
        "migrate-config",
        help="Explicitly migrate installed profile/config metadata schema without managed-file updates.",
    )
    add_common_repo_args(migrate_config)
    migrate_config.add_argument("--kit", default=str(ROOT), help="repo-contract-kit checkout to migrate from. Defaults to this checkout.")

    update = subparsers.add_parser("update", help="Update the current repo, or use --global to update the tool checkout.")
    add_common_repo_args(update)
    update.add_argument("--kit", default=str(ROOT), help="repo-contract-kit checkout to update from. Defaults to this checkout.")
    update.add_argument("--global", action="store_true", dest="global_update", help="Update the global tool checkout instead of a target repo.")
    update.add_argument("--ref", default=os.environ.get("REPO_CONTRACT_KIT_REF", "main"), help="Branch or tag to fetch for --global. Default: main.")
    update.add_argument(
        "--workflow-ref",
        default=os.environ.get("AGENT_WORKFLOW_KIT_REF", ""),
        help="Branch or tag for the optional legacy workflow-source checkout when --global is used. Defaults to --ref.",
    )
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--apply", action="store_true")
    update.add_argument("--preset")
    update.add_argument("--profiles")
    update.add_argument("--runtime-adapter", action="append")
    update.add_argument("--runtime-adapters")
    update.add_argument("--metadata-only", action="store_true")
    update.add_argument("--force-managed", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None or args.command == "guide":
        payload = guide_payload()
        if getattr(args, "json", False):
            render_json(payload)
            return 0
        return run_guide_interactive(payload)

    if args.command in {"options", "help"}:
        render_options(include_advanced=getattr(args, "all", False))
        return 0

    if args.command == "version":
        payload = {
            "schema_version": 1,
            "command": "version",
            "cli": cli_metadata(),
            "exit_code": 0,
        }
        if args.json:
            render_json(payload)
        else:
            print(payload["cli"]["version"])
        return 0

    if args.command == "self":
        if args.self_command == "status":
            payload = self_status_payload()
            render_json(payload) if args.json else render_self_status(payload)
            return 0
        if args.self_command == "update":
            payload, exit_code = self_update_payload(args)
            render_json(payload) if args.json else render_self_update(payload)
            return exit_code

    if args.command == "update" and getattr(args, "global_update", False):
        payload, exit_code = self_update_payload(args)
        render_json(payload) if args.json else render_self_update(payload)
        return exit_code

    try:
        repo = require_git_repo(args.repo)
    except CliError as exc:
        if getattr(args, "json", False):
            render_json({"schema_version": 1, "error": str(exc), "exit_code": exc.exit_code})
        else:
            print(str(exc), file=sys.stderr)
        return exc.exit_code

    if args.command == "status":
        payload = status_payload(repo)
        render_json(payload) if args.json else render_status(payload)
        return 0
    if args.command == "backlog-status":
        payload = build_backlog_report(repo, include_items=args.include_items)
        render_json(payload) if args.json else render_backlog_status(payload)
        return 0
    if args.command == "backlog-check":
        payload = build_backlog_report(repo, include_items=args.include_items)
        exit_code = 0 if payload["check"]["passed"] else 1
        payload["command"] = "backlog-check"
        payload["exit_code"] = exit_code
        render_json(payload) if args.json else render_backlog_status(payload)
        return exit_code
    if args.command == "agent-next":
        payload = agent_next_payload(repo)
        render_json(payload) if args.json else render_agent_next(payload)
        return 0
    if args.command == "agent-context-bundle":
        payload = agent_context_bundle_payload(args, repo)
        output_format = args.format or ("json" if args.json else "text")
        render_json(payload) if output_format == "json" else render_agent_context_bundle(payload)
        return 0
    if args.command == "agent-state-ledger":
        payload = agent_state_ledger_payload(args, repo)
        output_format = args.format or ("json" if args.json else "text")
        render_json(payload) if output_format == "json" else render_agent_state_ledger(payload)
        return 0
    if args.command == "branch-readiness":
        payload, exit_code = branch_readiness.build_report(args, repo)
        output_format = args.format or ("json" if args.json else "text")
        render_json(payload) if output_format == "json" else print(branch_readiness.render_text(payload))
        return exit_code
    if args.command == "instruction-diet":
        payload = instruction_diet_payload(args, repo)
        output_format = args.format or ("json" if args.json else "text")
        render_json(payload) if output_format == "json" else render_instruction_diet(payload)
        return 0
    if args.command in {"agent-preflight", "agent-doctor"}:
        payload, exit_code = agent_preflight_payload(args, repo)
        render_json(payload) if args.json else render_agent_preflight(payload)
        return exit_code
    if args.command == "doctor":
        doctor_args = argparse.Namespace(**vars(args))
        doctor_args.command = "doctor"
        payload, exit_code = agent_preflight_payload(doctor_args, repo)
        render_json(payload) if args.json else render_agent_preflight(payload)
        return exit_code
    if args.command == "agent-self-heal":
        payload, exit_code = agent_self_heal_payload(args, repo)
        render_json(payload) if args.json else render_agent_self_heal(payload)
        return exit_code
    if args.command == "automation-handoff":
        try:
            payload, exit_code = automation_handoff_payload(args, repo)
        except CliError as exc:
            payload = {
                "schema_version": 1,
                "command": args.command,
                "repo": str(repo),
                "error": str(exc),
                "target_repo_writes": target_repo_writes(False, reason="automation handoff failed before target writes"),
                "sidecar_writes": sidecar_writes(False),
                "sidecar_state": sidecar_state(repo),
                "exit_code": exc.exit_code,
            }
            render_json(payload) if args.json else render_json(payload)
            return exc.exit_code
        render_json(payload) if args.json else render_automation_handoff(payload)
        return exit_code
    if args.command == "sidecar-init":
        payload = sidecar_init_payload(repo)
        render_json(payload) if args.json else render_json(payload)
        return 0
    if args.command == "doc-impact":
        payload, exit_code = doc_impact_payload(args, repo)
        output_format = args.format or ("json" if args.json else "text")
        if output_format == "sarif":
            render_json(doc_impact_sarif_payload(payload))
        elif output_format == "json":
            render_json(payload)
        else:
            render_doc_impact(payload)
        return exit_code
    if args.command == "docs-explain":
        payload, exit_code = docs_explain.build_report(args, repo)
        payload["sidecar_state"] = sidecar_state(repo)
        output_format = args.format or ("json" if args.json else "text")
        if output_format == "json":
            render_json(payload)
        else:
            print(docs_explain.render_text(payload), end="")
        return exit_code
    if args.command == "docs-as-tests":
        payload, exit_code = check_docs_as_tests.build_report(args, repo)
        payload["sidecar_state"] = sidecar_state(repo)
        output_format = args.format or ("json" if args.json else "text")
        if output_format == "json":
            render_json(payload)
        else:
            print(check_docs_as_tests.render_text(payload), end="")
        return exit_code
    if args.command == "goal-check":
        payload, exit_code = goal_check_payload(args, repo)
        output_format = args.format or ("json" if args.json else "text")
        if output_format == "json":
            render_json(payload)
        else:
            print(goal_check.render_text(payload))
        return exit_code
    if args.command == "docs-propose":
        payload, exit_code = docs_propose_payload(args, repo)
        render_json(payload)
        return exit_code
    if args.command == "changelog-update":
        payload, exit_code = changelog_update.build_report(args, repo)
        payload["sidecar_state"] = sidecar_state(repo)
        output_format = args.format or ("json" if args.json else "text")
        if output_format == "json":
            render_json(payload)
        else:
            print(changelog_update.render_text(payload), end="")
        return exit_code
    if args.command == "onboarding-pr":
        try:
            payload = onboarding_pr_payload(args, repo)
        except CliError as exc:
            payload = {
                "schema_version": 1,
                "command": args.command,
                "repo": str(repo),
                "error": str(exc),
                "target_repo_writes": target_repo_writes(False, reason="onboarding generator failed before target writes"),
                "sidecar_writes": sidecar_writes(False),
                "sidecar_state": sidecar_state(repo),
                "exit_code": exc.exit_code,
            }
            render_json(payload) if args.json else render_json(payload)
            return exc.exit_code
        render_json(payload) if args.json else render_onboarding_pr(payload)
        return 0
    if args.command == "orient":
        payload = orient_payload(args, repo)
        render_json(payload) if args.json else render_json(payload)
        return 0
    if args.command == "review-plan":
        payload = review_plan_payload(args, repo)
        render_json(payload) if args.json else render_json(payload)
        return 0
    if args.command == "task-packet":
        payload = task_packet_payload(args, repo)
        render_json(payload)
        return 0
    if args.command == "agent-task-packet-from-backlog":
        try:
            payload = backlog_task_packet_payload(args, repo)
        except CliError as exc:
            if args.json:
                render_json({"schema_version": 1, "command": args.command, "error": str(exc), "exit_code": exc.exit_code})
            else:
                print(str(exc), file=sys.stderr)
            return exc.exit_code
        render_json(payload)
        return 0
    if args.command == "verify":
        payload, exit_code = verify_payload(args, repo)
        render_json(payload) if args.json else render_doc_impact(payload["doc_impact"])
        return exit_code
    if args.command == "update-plan":
        payload, exit_code = update_plan_payload(args, repo)
        render_json(payload)
        return exit_code
    if args.command == "install":
        return run_mutating_script(install_script_command(args, repo), repo, args.json, writes_on_success=True)
    if args.command == "setup":
        return run_mutating_script(install_script_command(args, repo), repo, args.json, writes_on_success=True)
    if args.command == "target":
        if args.target_command == "add":
            return run_mutating_script(install_script_command(args, repo), repo, args.json, writes_on_success=True)
        if args.target_command == "status":
            payload = status_payload(repo)
            render_json(payload) if args.json else render_status(payload)
            return 0
        if args.target_command == "doctor":
            doctor_args = argparse.Namespace(**vars(args))
            doctor_args.command = "target-doctor"
            payload, exit_code = agent_preflight_payload(doctor_args, repo)
            render_json(payload) if args.json else render_agent_preflight(payload)
            return exit_code
        if args.target_command == "repair-source-clone":
            payload, exit_code = source_clone_repair_payload(args, repo)
            render_json(payload) if args.json else render_source_clone_repair(payload)
            return exit_code
        if args.target_command == "update":
            command = update_script_command(args, repo, apply_default=True)
            return run_mutating_script(command, repo, args.json, writes_on_success=not args.dry_run)
    if args.command == "migrate-config":
        kit = Path(args.kit).expanduser().resolve()
        command = [sys.executable, str(kit / "scripts" / "update.py"), str(repo), "--apply", "--metadata-only"]
        return run_mutating_script(command, repo, args.json, writes_on_success=True)
    if args.command == "update":
        apply_default = True
        command = update_script_command(args, repo, apply_default=apply_default)
        writes_on_success = (args.apply or apply_default) and not args.dry_run
        return run_mutating_script(command, repo, args.json, writes_on_success=writes_on_success)

    parser.error(f"Unhandled command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
