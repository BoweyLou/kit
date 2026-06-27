#!/usr/bin/env python3
"""Mine local Codex thread history for kit CLI journey research.

The miner is intentionally local-first:
- raw Codex thread text is read from local files only
- raw/intermediate artifacts are written under local state
- the tracked Markdown report contains aggregate counts and recommendations
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import hashlib
import json
import os
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
DEFAULT_CODEX_HOME = Path.home() / ".codex"
DEFAULT_REPORT = Path("docs/cli-journey-research.md")
DEFAULT_SAMPLE_LIMIT = 75
MAX_TEXT_CHARS_PER_THREAD = 200_000
CURRENT_KIT_ERA_START = "2026-06-25T00:00:00Z"

SECRET_PATTERNS = [
    re.compile(r"sk-proj-[A-Za-z0-9_-]{12,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{12,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{12,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
]
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
HOME_RE = re.compile(re.escape(str(Path.home())))
URL_RE = re.compile(r"https?://[^\s'\"<>]+")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ABSOLUTE_PATH_RE = re.compile(r"(?<![\w.-])/(?:[^\s'\"<>:]+/)+[^\s'\"<>:]*")
TILDE_PATH_RE = re.compile(r"(?<![\w.-])~/(?:[^\s'\"<>:]+/)*[^\s'\"<>:]*")
HIGH_ENTROPY_RE = re.compile(r"\b(?=[A-Za-z0-9_=-]{32,}\b)(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9_=-]{32,}\b")
SAFE_COMMAND_VERBS = {
    "apply_patch",
    "cat",
    "find",
    "git",
    "grep",
    "ls",
    "make",
    "nl",
    "node",
    "npm",
    "pwd",
    "python",
    "python3",
    "rg",
    "sed",
    "update_plan",
    "wc",
    "write_stdin",
}
AGENT_TOOL_COMMANDS = {
    "apply_patch",
    "patch_apply_end",
    "update_plan",
    "write_stdin",
}

COMMAND_NORMALIZERS: list[tuple[str, re.Pattern[str]]] = [
    ("kit start", re.compile(r"(?<![\w.-])kit\s+start\b")),
    ("kit command-map", re.compile(r"(?<![\w.-])kit\s+command-map\b")),
    ("kit agent-tool-manifest", re.compile(r"(?<![\w.-])kit\s+agent-tool-manifest\b")),
    ("kit agent-context", re.compile(r"(?<![\w.-])kit\s+agent-context\b")),
    ("kit mode-check", re.compile(r"(?<![\w.-])kit\s+mode-check\b")),
    ("kit task-packet", re.compile(r"(?<![\w.-])kit\s+task-packet\b")),
    ("kit verify", re.compile(r"(?<![\w.-])kit\s+verify\b")),
    ("kit status", re.compile(r"(?<![\w.-])kit\s+status\b")),
    ("kit update", re.compile(r"(?<![\w.-])kit\s+update\b")),
    ("kit doctor", re.compile(r"(?<![\w.-])kit\s+doctor\b")),
    ("kit setup", re.compile(r"(?<![\w.-])kit\s+setup\b")),
    ("make agent-start", re.compile(r"\bmake\s+agent-start\b")),
    ("make agent-task-packet", re.compile(r"\bmake\s+agent-task-packet\b")),
    ("make agent-verify", re.compile(r"\bmake\s+agent-verify\b")),
    ("make kit-status", re.compile(r"\bmake\s+kit-status\b")),
    ("make kit-update", re.compile(r"\bmake\s+kit-update\b")),
    ("python3 scripts/repo_contract_kit.py", re.compile(r"\bpython3\s+scripts/repo_contract_kit\.py\b")),
    ("scripts/repo_contract_kit.py", re.compile(r"(?<![\w/.-])scripts/repo_contract_kit\.py\b")),
    ("git status", re.compile(r"\bgit\s+status\b")),
    ("git diff", re.compile(r"\bgit\s+diff\b")),
    ("make test", re.compile(r"\bmake\s+test\b")),
    ("make docs-check", re.compile(r"\bmake\s+docs-check\b")),
    ("make docs-freshness", re.compile(r"\bmake\s+docs-freshness\b")),
    ("make version-check", re.compile(r"\bmake\s+version-check\b")),
]

DEV_TERMS = (
    "repo",
    "code",
    "script",
    "cli",
    "test",
    "docs",
    "bug",
    "fix",
    "review",
    "commit",
    "branch",
    "pull request",
    "make ",
    "git ",
    "python3 ",
    "kit ",
)


@dataclasses.dataclass
class ThreadRecord:
    thread_id: str
    title: str = ""
    cwd: str = ""
    source_paths: set[str] = dataclasses.field(default_factory=set)
    timestamps: list[str] = dataclasses.field(default_factory=list)
    texts: list[str] = dataclasses.field(default_factory=list)
    commands: list[str] = dataclasses.field(default_factory=list)
    exit_codes: list[int] = dataclasses.field(default_factory=list)
    payload_types: collections.Counter[str] = dataclasses.field(default_factory=collections.Counter)
    parse_warnings: list[str] = dataclasses.field(default_factory=list)
    patch_applied: bool = False
    task_complete: bool = False
    turn_aborted: bool = False

    def add_text(self, value: Any) -> None:
        text = text_from_any(value)
        if not text:
            return
        current_size = sum(len(item) for item in self.texts)
        if current_size >= MAX_TEXT_CHARS_PER_THREAD:
            return
        remaining = max(MAX_TEXT_CHARS_PER_THREAD - current_size, 0)
        self.texts.append(text[:remaining])

    def add_command(self, value: Any) -> None:
        command = command_from_any(value)
        if command:
            self.commands.append(command)


def state_home() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state"))


def default_state_dir() -> Path:
    return state_home() / "repo-contract-kit" / "thread-mining"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        number = int(text)
        if number > 10_000_000_000:
            number = number / 1000
        return parse_timestamp(number)
    if text.endswith("Z"):
        return text
    return text


def text_from_any(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return "\n".join(text_from_any(item) for item in value if text_from_any(item))
    if isinstance(value, dict):
        for key in ("text", "message", "content", "summary", "last_agent_message"):
            if key in value:
                result = text_from_any(value[key])
                if result:
                    return result
        return "\n".join(text_from_any(item) for item in value.values() if isinstance(item, (str, list, dict)))
    return str(value)


def command_from_any(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return " ".join(shlex.quote(str(part)) for part in value)
    if isinstance(value, dict):
        if "cmd" in value:
            return command_from_any(value["cmd"])
        if "command" in value:
            return command_from_any(value["command"])
    return str(value).strip()


def safe_json_line(line: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(line)
    except json.JSONDecodeError as exc:
        return None, f"invalid json line: {exc.msg}"
    if not isinstance(value, dict):
        return None, "json line is not an object"
    return value, None


def get_record(records: dict[str, ThreadRecord], thread_id: str) -> ThreadRecord:
    if thread_id not in records:
        records[thread_id] = ThreadRecord(thread_id=thread_id)
    return records[thread_id]


def merge_record(records: dict[str, ThreadRecord], source: ThreadRecord, target_id: str) -> ThreadRecord:
    target = get_record(records, target_id)
    if source is target:
        return target
    if source.title and not target.title:
        target.title = source.title
    if source.cwd and not target.cwd:
        target.cwd = source.cwd
    target.source_paths.update(source.source_paths)
    target.timestamps.extend(source.timestamps)
    target.texts.extend(source.texts)
    target.commands.extend(source.commands)
    target.exit_codes.extend(source.exit_codes)
    target.payload_types.update(source.payload_types)
    target.parse_warnings.extend(source.parse_warnings)
    target.patch_applied = target.patch_applied or source.patch_applied
    target.task_complete = target.task_complete or source.task_complete
    target.turn_aborted = target.turn_aborted or source.turn_aborted
    if source.thread_id in records and source.thread_id != target_id:
        del records[source.thread_id]
    return target


def read_jsonl(path: Path) -> Iterable[tuple[dict[str, Any] | None, str | None]]:
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                line = raw.strip()
                if not line:
                    continue
                yield safe_json_line(line)
    except OSError as exc:
        yield None, f"could not read {path}: {exc}"


def ingest_session_index(path: Path, records: dict[str, ThreadRecord]) -> int:
    if not path.exists():
        return 0
    count = 0
    for obj, warning in read_jsonl(path):
        if obj is None:
            record = get_record(records, f"session-index-warning-{count}")
            if warning:
                record.parse_warnings.append(warning)
            continue
        thread_id = str(obj.get("id") or "").strip()
        if not thread_id:
            continue
        record = get_record(records, thread_id)
        record.source_paths.add(str(path))
        record.title = str(obj.get("thread_name") or record.title or "")
        timestamp = parse_timestamp(obj.get("updated_at"))
        if timestamp:
            record.timestamps.append(timestamp)
        count += 1
    return count


def ingest_history(path: Path, records: dict[str, ThreadRecord]) -> int:
    if not path.exists():
        return 0
    count = 0
    for obj, warning in read_jsonl(path):
        if obj is None:
            record = get_record(records, f"history-warning-{count}")
            if warning:
                record.parse_warnings.append(warning)
            continue
        thread_id = str(obj.get("session_id") or obj.get("thread_id") or "").strip()
        if not thread_id:
            continue
        record = get_record(records, thread_id)
        record.source_paths.add(str(path))
        record.add_text(obj.get("text"))
        timestamp = parse_timestamp(obj.get("ts"))
        if timestamp:
            record.timestamps.append(timestamp)
        count += 1
    return count


def payload_type(obj: dict[str, Any], payload: Any) -> str:
    if isinstance(payload, dict):
        return str(payload.get("type") or obj.get("type") or "unknown")
    return str(obj.get("type") or "unknown")


def parse_function_call(record: ThreadRecord, payload: dict[str, Any]) -> None:
    name = str(payload.get("name") or "")
    namespace = str(payload.get("namespace") or "")
    arguments = payload.get("arguments")
    if name == "exec_command":
        if isinstance(arguments, str):
            parsed, _ = safe_json_line(arguments)
            if parsed:
                record.add_command(parsed.get("cmd"))
                if parsed.get("workdir") and not record.cwd:
                    record.cwd = str(parsed["workdir"])
                return
        record.add_text(arguments)
        return
    if name:
        command = f"{namespace}.{name}" if namespace else name
        record.add_command(command)
    record.add_text(arguments)


def parse_session_event(obj: dict[str, Any], record: ThreadRecord) -> str | None:
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return None
    ptype = payload_type(obj, payload)
    record.payload_types[ptype] += 1
    timestamp = parse_timestamp(obj.get("timestamp") or payload.get("timestamp") or payload.get("completed_at"))
    if timestamp:
        record.timestamps.append(timestamp)

    if ptype == "session_meta":
        if payload.get("cwd") and not record.cwd:
            record.cwd = str(payload["cwd"])
        return str(payload.get("id") or "").strip() or None
    if ptype == "turn_context":
        if payload.get("cwd") and not record.cwd:
            record.cwd = str(payload["cwd"])
    elif ptype == "thread_name_updated":
        record.title = str(payload.get("thread_name") or record.title or "")
        return str(payload.get("thread_id") or "").strip() or None
    elif ptype in {"user_message", "agent_message", "agent_reasoning", "task_complete"}:
        record.add_text(payload)
        if ptype == "task_complete":
            record.task_complete = True
    elif ptype == "message":
        if payload.get("role") in {"user", "assistant"}:
            record.add_text(payload)
    elif ptype == "function_call":
        parse_function_call(record, payload)
    elif ptype == "function_call_output":
        output = text_from_any(payload.get("output"))
        if failure_text(output):
            record.add_text(output)
    elif ptype == "exec_command_end":
        record.add_command(payload.get("command") or payload.get("parsed_cmd"))
        if payload.get("cwd") and not record.cwd:
            record.cwd = str(payload["cwd"])
        exit_code = int_or_none(payload.get("exit_code"))
        if exit_code is not None:
            record.exit_codes.append(exit_code)
        if exit_code and failure_text(text_from_any(payload.get("aggregated_output") or payload.get("stderr") or payload.get("stdout"))):
            record.add_text(payload.get("aggregated_output") or payload.get("stderr") or payload.get("stdout"))
    elif ptype == "mcp_tool_call_end":
        invocation = payload.get("invocation") or {}
        if isinstance(invocation, dict):
            server = invocation.get("server")
            tool = invocation.get("tool")
            if server or tool:
                record.add_command(".".join(str(part) for part in (server, tool) if part))
    elif ptype in {"custom_tool_call", "patch_apply_end"}:
        if ptype == "patch_apply_end":
            record.patch_applied = bool(payload.get("success"))
        record.add_command(payload.get("name") or ptype)
        if ptype == "custom_tool_call":
            record.add_text(payload.get("input"))
    elif ptype == "turn_aborted":
        record.turn_aborted = True
        record.add_text(payload.get("reason"))
    return None


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def failure_text(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in ("error", "failed", "traceback", "exception", "unknown command", "unrecognized arguments"))


def ingest_session_file(path: Path, records: dict[str, ThreadRecord]) -> int:
    provisional_id = path.stem
    record = get_record(records, provisional_id)
    record.source_paths.add(str(path))
    seen = 0
    for obj, warning in read_jsonl(path):
        if obj is None:
            if warning:
                record.parse_warnings.append(warning)
            continue
        new_id = parse_session_event(obj, record)
        if new_id and new_id != record.thread_id:
            record = merge_record(records, record, new_id)
        seen += 1
    return seen


def iter_session_files(codex_home: Path) -> list[Path]:
    files: list[Path] = []
    sessions = codex_home / "sessions"
    archived = codex_home / "archived_sessions"
    if sessions.exists():
        files.extend(sorted(sessions.glob("**/*.jsonl")))
    if archived.exists():
        files.extend(sorted(archived.glob("*.jsonl")))
    return files


def collect_threads(codex_home: Path) -> tuple[dict[str, ThreadRecord], dict[str, int]]:
    records: dict[str, ThreadRecord] = {}
    source_counts = {
        "session_index": ingest_session_index(codex_home / "session_index.jsonl", records),
        "history": ingest_history(codex_home / "history.jsonl", records),
        "session_files": 0,
        "session_events": 0,
    }
    for path in iter_session_files(codex_home):
        source_counts["session_files"] += 1
        source_counts["session_events"] += ingest_session_file(path, records)
    return records, source_counts


def thread_hash(thread_id: str) -> str:
    return hashlib.sha256(thread_id.encode("utf-8")).hexdigest()[:16]


def redact_text(text: str) -> str:
    result = HOME_RE.sub("~", text)
    result = URL_RE.sub("<redacted-url>", result)
    result = EMAIL_RE.sub("<redacted-email>", result)
    result = IP_RE.sub("<redacted-ip>", result)
    result = TILDE_PATH_RE.sub("<redacted-path>", result)
    result = ABSOLUTE_PATH_RE.sub("<redacted-path>", result)
    result = UUID_RE.sub("<uuid>", result)
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("<redacted-secret>", result)
    result = HIGH_ENTROPY_RE.sub("<redacted-token>", result)
    return result


def normalize_command(command: str) -> str:
    redacted = redact_text(command.strip())
    for label, pattern in COMMAND_NORMALIZERS:
        if pattern.search(redacted):
            return label
    try:
        parts = shlex.split(redacted)
    except ValueError:
        parts = redacted.split()
    if not parts:
        return ""
    verb = parts[0]
    if verb not in SAFE_COMMAND_VERBS:
        return verb.split(".")[-1] if "." in verb else verb
    if verb in AGENT_TOOL_COMMANDS:
        return verb
    if verb == "git" and len(parts) > 1:
        return f"git {parts[1]}"
    if verb == "make" and len(parts) > 1 and re.match(r"^[A-Za-z0-9_.:-]+$", parts[1]):
        return f"make {parts[1]}"
    if verb in {"rg", "sed", "nl", "python3"} and len(parts) > 1 and not parts[1].startswith("<redacted-"):
        if verb == "python3" and parts[1] not in {"-", "-m"}:
            return "python3"
        if verb == "python3" and parts[1] == "-m" and len(parts) > 2 and re.match(r"^[A-Za-z0-9_.-]+$", parts[2]):
            return f"python3 -m {parts[2]}"
        return f"{verb} {parts[1]}"
    return verb


def unique_in_order(values: Iterable[str], limit: int = 20) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def combined_text(record: ThreadRecord) -> str:
    parts = [record.title, record.cwd, *record.texts, *record.commands]
    return "\n".join(part for part in parts if part)


def is_dev_thread(record: ThreadRecord) -> bool:
    blob = combined_text(record).lower()
    if record.commands:
        return True
    if "/code/" in record.cwd.lower() or "/codex/" in record.cwd.lower() or "/worktrees/" in record.cwd.lower():
        return True
    return any(term in blob for term in DEV_TERMS)


def is_kit_related(record: ThreadRecord) -> bool:
    blob = combined_text(record).lower()
    return any(
        term in blob
        for term in (
            "kit start",
            "repo-contract-kit",
            "repo_contract_kit.py",
            "agent-workflow-kit",
            "make agent-",
            "make kit-",
            "/04_code/kit",
        )
    )


def record_date_end(record: ThreadRecord) -> str | None:
    timestamps = sorted(set(record.timestamps))
    return timestamps[-1] if timestamps else None


def record_matches_since(record: ThreadRecord, since: str | None) -> bool:
    if not since:
        return True
    end = record_date_end(record)
    if not end:
        return False
    return end >= since


def record_matches_cwd_prefix(record: ThreadRecord, prefixes: list[str] | None) -> bool:
    if not prefixes:
        return True
    cwd = record.cwd
    if not cwd:
        return False
    try:
        resolved = str(Path(cwd).expanduser().resolve())
    except OSError:
        resolved = cwd
    return any(resolved.startswith(prefix) for prefix in prefixes)


def classify_intent(blob: str) -> str:
    rules = [
        ("release", ("release-gated", "version-check", "version bump", "release metadata", "changelog", "semver", "public cli", "public api", "public config", "public schema")),
        ("fix", ("fix", "bug", "failed", "failure", "error", "debug", "repair")),
        ("update", ("update", "upgrade", "refresh", "migrate")),
        ("setup", ("setup", "install", "enroll", "bootstrap", "start")),
        ("review", ("review", "audit", "scan", "inspect")),
        ("docs", ("docs", "documentation", "readme", "guide")),
        ("research", ("research", "mine", "analy", "investigate", "find")),
    ]
    for label, needles in rules:
        if any(needle in blob for needle in needles):
            return label
    return "unknown"


def route_categories(commands: list[str], blob: str) -> set[str]:
    command_evidence = "\n".join(commands)
    evidence = command_evidence if command_evidence.strip() else blob
    categories: set[str] = set()
    if re.search(
        r"(?<![\w.-])kit\s+(start|command-map|agent-tool-manifest|agent-context|mode-check|task-packet|verify|status|update|doctor|setup|help|options)\b",
        evidence,
    ):
        categories.add("kit")
    if re.search(r"\bmake\s+(agent-|kit-|version-|docs-)", evidence):
        categories.add("make-agent")
    if re.search(r"\bpython3\s+scripts/repo_contract_kit\.py\b|(?<![\w/.-])scripts/repo_contract_kit\.py\b", evidence):
        categories.add("direct-script")
    shell_commands = [cmd for cmd in commands if re.match(r"\s*(git|rg|sed|cat|ls|find|python3 -m|make test|make docs|make version)", cmd)]
    if shell_commands and not categories:
        categories.add("shell-git-only")
    return categories


def classify_route(categories: set[str]) -> str:
    primary = categories & {"kit", "make-agent", "direct-script"}
    if len(primary) > 1:
        return "mixed"
    if primary:
        return next(iter(primary))
    if "shell-git-only" in categories:
        return "shell-git-only"
    return "unknown"


def classify_journey(blob: str, commands: list[str]) -> str:
    evidence = blob + "\n" + "\n".join(commands)
    if any(term in evidence for term in ("release-gated", "version-check", "version bump", "release metadata", "changelog", "semver", "public cli", "public api", "public config", "public schema")):
        return "release-gated"
    if any(term in evidence for term in ("doctor", "self-heal", "repair", "blocked", "command not found", "unrecognized arguments", "traceback")):
        return "recovery"
    if any(term in evidence for term in ("setup --preset", "kit setup", "not installed", "enroll", "fresh repo", "new repo")):
        return "fresh-repo"
    if any(term in evidence for term in ("dirty", "work-in-progress", "git status --short", "changed files", "working tree")):
        return "dirty-work"
    if any(term in evidence for term in ("update --dry-run", "kit status", "verify", "mode-check")):
        return "clean-maintenance"
    return "unknown"


def classify_friction(record: ThreadRecord, blob: str, categories: set[str]) -> list[str]:
    markers: list[str] = []
    if any(term in blob for term in ("clarify", "clarification", "need to ask", "ask the user", "which repo")):
        markers.append("clarification-needed")
    if any(term in blob for term in ("wrong repo", "wrong cwd", "which repo", "source repo vs target repo", "source-repo vs target-repo", "companion repo confusion")):
        markers.append("wrong-repo-risk")
    if any(term in blob for term in ("docs freshness", "stale docs", "missing-script-reference", "docs drift")):
        markers.append("stale-docs")
    failed_command = any(code != 0 for code in record.exit_codes)
    if any(term in blob for term in ("command not found", "unknown command", "unrecognized arguments", "parse error")) or ("usage:" in blob and failed_command):
        markers.append("command-confusion")
    if "direct-script" in categories and not any(term in blob for term in ("source-checkout fallback", "source checkout fallback", "maintainer direct script")):
        markers.append("direct-script-fallback")
    if any(term in blob for term in ("keyerror", "missing json", "missing field")):
        markers.append("missing-json-field")
    if any(term in blob for term in ("unexpected write", "mutation risk", "dirty target")):
        markers.append("unexpected-mutation-risk")
    if failed_command:
        markers.append("failed-command")
    if failed_command and any(term in blob for term in ("retry", "rerun", "run again", "try again")):
        markers.append("retry-loop")
    return unique_in_order(markers)


def classify_outcome(record: ThreadRecord, blob: str, friction: list[str]) -> str:
    if record.turn_aborted or "blocked" in blob:
        return "blocked"
    if "redirected" in blob or "newest request" in blob:
        return "redirected"
    if friction and record.task_complete:
        return "partially-completed"
    if record.task_complete or any(term in blob for term in ("pushed", "committed", "implemented", "completed", "all tests pass")):
        return "completed"
    return "unknown"


def recommended_action(route: str, journey: str, friction: list[str]) -> str:
    if "command-confusion" in friction or "direct-script-fallback" in friction or route in {"direct-script", "mixed"}:
        return "cli change"
    if "stale-docs" in friction or "missing-json-field" in friction:
        return "docs change"
    if "failed-command" in friction or journey == "release-gated":
        return "test fixture"
    if friction:
        return "docs change"
    return "no action"


def observation_for(record: ThreadRecord) -> dict[str, Any]:
    blob_raw = combined_text(record)
    blob = blob_raw.lower()
    commands = unique_in_order(normalize_command(command) for command in record.commands if command)
    categories = route_categories(record.commands, blob)
    route = classify_route(categories)
    intent = classify_intent(blob)
    journey = classify_journey(blob, record.commands)
    friction = classify_friction(record, blob, categories)
    outcome = classify_outcome(record, blob, friction)
    recommendation = recommended_action(route, journey, friction)
    timestamps = sorted(set(record.timestamps))
    return {
        "thread_id_hash": thread_hash(record.thread_id),
        "title_redacted": redact_text(record.title)[:120] if record.title else "",
        "date_start": timestamps[0] if timestamps else None,
        "date_end": timestamps[-1] if timestamps else None,
        "cwd_hint": cwd_hint(record.cwd),
        "intent": intent,
        "route_used": route,
        "route_categories": sorted(categories),
        "journey": journey,
        "commands_run": commands,
        "failed_command_count": sum(1 for code in record.exit_codes if code != 0),
        "friction_markers": friction,
        "outcome": outcome,
        "recommended_action": recommendation,
        "payload_type_count": dict(record.payload_types),
        "parse_warning_count": len(record.parse_warnings),
        "source_count": len(record.source_paths),
    }


def cwd_hint(cwd: str) -> str:
    if not cwd:
        return ""
    path = Path(cwd)
    parts = path.parts
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return path.name


def command_family(command: str) -> str:
    if command.startswith("kit "):
        return "kit_commands"
    if command.startswith("make "):
        return "make_commands"
    if command in AGENT_TOOL_COMMANDS or command.startswith(("functions.", "multi_agent_v1.", "codex_app.", "tool_search.")):
        return "agent_tool_calls"
    return "shell_commands"


def normalize_cwd_prefixes(prefixes: list[str] | None) -> list[str]:
    result: list[str] = []
    for prefix in prefixes or []:
        for item in str(prefix).split(","):
            item = item.strip()
            if not item:
                continue
            try:
                result.append(str(Path(item).expanduser().resolve()))
            except OSError:
                result.append(item)
    return result


def observation_passes_filters(
    record: ThreadRecord,
    *,
    kit_related: bool = False,
    since: str | None = None,
    cwd_prefixes: list[str] | None = None,
) -> bool:
    if kit_related and not is_kit_related(record):
        return False
    if not record_matches_since(record, since):
        return False
    if not record_matches_cwd_prefix(record, cwd_prefixes):
        return False
    return True


def build_summary(
    records: dict[str, ThreadRecord],
    include_non_dev: bool = False,
    *,
    kit_related: bool = False,
    since: str | None = None,
    cwd_prefixes: list[str] | None = None,
    label: str = "all-dev",
) -> dict[str, Any]:
    observations = []
    skipped_non_dev = 0
    skipped_by_filter = 0
    normalized_prefixes = normalize_cwd_prefixes(cwd_prefixes)
    for record in records.values():
        if not include_non_dev and not is_dev_thread(record):
            skipped_non_dev += 1
            continue
        if not observation_passes_filters(record, kit_related=kit_related, since=since, cwd_prefixes=normalized_prefixes):
            skipped_by_filter += 1
            continue
        observations.append(observation_for(record))
    observations.sort(key=lambda item: (item.get("date_end") or "", item["thread_id_hash"]))
    commands = [command for item in observations for command in item["commands_run"]]

    aggregate = {
        "intent": counter_dict(item["intent"] for item in observations),
        "route_used": counter_dict(item["route_used"] for item in observations),
        "journey": counter_dict(item["journey"] for item in observations),
        "friction_markers": counter_dict(marker for item in observations for marker in item["friction_markers"]),
        "outcome": counter_dict(item["outcome"] for item in observations),
        "recommended_action": counter_dict(item["recommended_action"] for item in observations),
        "commands_run": counter_dict(commands),
        "kit_commands": counter_dict(command for command in commands if command_family(command) == "kit_commands"),
        "make_commands": counter_dict(command for command in commands if command_family(command) == "make_commands"),
        "shell_commands": counter_dict(command for command in commands if command_family(command) == "shell_commands"),
        "agent_tool_calls": counter_dict(command for command in commands if command_family(command) == "agent_tool_calls"),
    }
    all_dates = sorted(date for item in observations for date in (item.get("date_start"), item.get("date_end")) if date)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "label": label,
        "filters": {
            "include_non_dev": include_non_dev,
            "kit_related": kit_related,
            "since": since,
            "cwd_prefixes": normalized_prefixes,
        },
        "corpus": {
            "threads_seen": len(records),
            "dev_threads": len(observations),
            "skipped_non_dev_threads": skipped_non_dev,
            "skipped_by_filter_threads": skipped_by_filter,
            "date_start": all_dates[0] if all_dates else None,
            "date_end": all_dates[-1] if all_dates else None,
        },
        "aggregate": aggregate,
        "observations": observations,
    }


def summary_without_observations(summary: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in summary.items() if key != "observations"}


def counter_dict(values: Iterable[str]) -> dict[str, int]:
    return dict(collections.Counter(value for value in values if value).most_common())


def top_items(counter: dict[str, int], limit: int = 10) -> list[tuple[str, int]]:
    return list(counter.items())[:limit]


def render_table(counter: dict[str, int], empty_label: str = "No signals found.") -> str:
    if not counter:
        return empty_label + "\n"
    lines = ["| Signal | Count |", "| --- | ---: |"]
    for label, count in top_items(counter):
        lines.append(f"| `{label}` | {count} |")
    return "\n".join(lines) + "\n"


def render_backlog(summary: dict[str, Any]) -> list[str]:
    route_counts = summary["aggregate"]["route_used"]
    friction_counts = summary["aggregate"]["friction_markers"]
    recommendations = []
    if route_counts.get("direct-script", 0) or route_counts.get("mixed", 0):
        recommendations.append("Prioritize CLI-first wrappers so agents do not need direct `python3 scripts/repo_contract_kit.py` fallbacks.")
    if route_counts.get("make-agent", 0) > route_counts.get("kit", 0):
        recommendations.append("Keep `make agent-*` compatibility, but document the equivalent `kit` JSON route beside each target.")
    if friction_counts.get("command-confusion", 0):
        recommendations.append("Add or expand CLI UX fixtures around commands that produced parse errors or unknown-command failures.")
    if friction_counts.get("stale-docs", 0):
        recommendations.append("Treat stale-doc findings as docs-contract backlog and add freshness checks where possible.")
    if friction_counts.get("wrong-repo-risk", 0):
        recommendations.append("Make source-repo vs target-repo language more explicit in `kit start`, setup, update, and maintainer docs.")
    if friction_counts.get("missing-json-field", 0):
        recommendations.append("Promote frequently consumed JSON fields into stable payload contracts or generated schema files.")
    if not recommendations:
        recommendations.append("No high-confidence CLI backlog emerged from this corpus; rerun after more `kit start` usage.")
    return recommendations


def render_signal_section(summary: dict[str, Any], title: str, note: str) -> list[str]:
    corpus = summary["corpus"]
    aggregate = summary["aggregate"]
    filters = summary.get("filters") or {}
    lines = [
        f"## {title}",
        "",
        note,
        "",
        f"- Threads scanned: {corpus['threads_seen']}",
        f"- Developer threads classified: {corpus['dev_threads']}",
        f"- Skipped as non-dev: {corpus['skipped_non_dev_threads']}",
        f"- Skipped by filter: {corpus.get('skipped_by_filter_threads', 0)}",
        f"- Date range: {corpus['date_start'] or 'unknown'} to {corpus['date_end'] or 'unknown'}",
    ]
    if filters.get("since"):
        lines.append(f"- Since filter: latest thread timestamp at or after {filters['since']}")
    if filters.get("kit_related"):
        lines.append("- Kit-related filter: enabled")
    if filters.get("cwd_prefixes"):
        lines.append(f"- CWD prefix filters: {', '.join(filters['cwd_prefixes'])}")
    lines.extend(
        [
            "",
            "### Route Signals",
            "",
            render_table(aggregate["route_used"]).rstrip(),
            "",
            "### Journey Signals",
            "",
            render_table(aggregate["journey"]).rstrip(),
            "",
            "### Intent Signals",
            "",
            render_table(aggregate["intent"]).rstrip(),
            "",
            "### Friction Signals",
            "",
            render_table(aggregate["friction_markers"]).rstrip(),
            "",
            "### Kit Commands",
            "",
            render_table(aggregate.get("kit_commands", {})).rstrip(),
            "",
            "### Make Commands",
            "",
            render_table(aggregate.get("make_commands", {})).rstrip(),
            "",
            "### Shell Commands",
            "",
            render_table(aggregate.get("shell_commands", {})).rstrip(),
            "",
            "### Agent Tool Calls",
            "",
            render_table(aggregate.get("agent_tool_calls", {})).rstrip(),
            "",
        ]
    )
    return lines


def render_report(summary: dict[str, Any]) -> str:
    sections = summary.get("report_sections") or [
        {
            "title": "Corpus",
            "note": "This section reflects the selected mining filters.",
            "summary": summary_without_observations(summary),
        }
    ]
    lines = [
        "# CLI Journey Research",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "This report summarizes local Codex thread history to improve kit CLI",
        "journeys. Raw thread text stays in local Codex storage and local mining",
        "artifacts; this tracked report contains aggregate, redacted findings only.",
        "",
        "The baseline section covers all local development-looking threads. The",
        "kit/current-era section narrows the view to kit-related evidence since",
        f"{CURRENT_KIT_ERA_START}.",
        "",
    ]
    for section in sections:
        lines.extend(render_signal_section(section["summary"], section["title"], section["note"]))
    lines.extend([
        "## Recommended Backlog",
        "",
    ])
    for item in render_backlog(summary):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Confidence Notes",
            "",
            "- Classification is deterministic and heuristic-based.",
            "- Counts indicate repeated signals, not statistically clean telemetry.",
            "- Thread ids are hashed in local summaries and omitted from this report.",
            "- Command names are normalized; raw prompts, raw outputs, secrets, and full paths are not included here.",
        ]
    )
    return "\n".join(lines) + "\n"


def sample_excerpt(record: ThreadRecord) -> str:
    for text in record.texts:
        redacted = redact_text(" ".join(text.split()))
        if redacted:
            return redacted[:320]
    return ""


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)


def write_private_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    path.chmod(0o600)


def write_outputs(
    summary: dict[str, Any],
    records: dict[str, ThreadRecord],
    state_dir: Path,
    report_path: Path,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, str]:
    ensure_private_dir(state_dir)
    summary_path = state_dir / "thread-mining-summary.json"
    samples_path = state_dir / "thread-mining-samples.jsonl"
    outputs = {
        "summary_json": str(summary_path),
        "samples_jsonl": str(samples_path),
        "report": str(report_path),
    }
    summary["outputs"] = outputs
    write_private_text(summary_path, json.dumps(summary, indent=2, sort_keys=True) + "\n")

    records_by_hash = {thread_hash(record.thread_id): record for record in records.values()}
    samples_written = 0
    sample_lines: list[str] = []
    for observation in summary["observations"]:
        if samples_written >= sample_limit:
            break
        if not observation["friction_markers"]:
            continue
        record = records_by_hash.get(observation["thread_id_hash"])
        if not record:
            continue
        sample_lines.append(
            json.dumps(
                {
                    "thread_id_hash": observation["thread_id_hash"],
                    "date_end": observation["date_end"],
                    "friction_markers": observation["friction_markers"],
                    "route_used": observation["route_used"],
                    "journey": observation["journey"],
                    "commands_run": observation["commands_run"],
                    "failed_command_count": observation["failed_command_count"],
                    "excerpt_redacted": sample_excerpt(record),
                },
                sort_keys=True,
            )
        )
        samples_written += 1
    write_private_text(samples_path, "\n".join(sample_lines) + ("\n" if sample_lines else ""))

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(summary), encoding="utf-8")
    return outputs


def mine_codex_threads(
    codex_home: Path = DEFAULT_CODEX_HOME,
    state_dir: Path | None = None,
    report_path: Path = DEFAULT_REPORT,
    include_non_dev: bool = False,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    write: bool = True,
    kit_related: bool = False,
    since: str | None = None,
    cwd_prefixes: list[str] | None = None,
    current_kit_era: bool = False,
) -> dict[str, Any]:
    records, source_counts = collect_threads(codex_home)
    effective_since = since or (CURRENT_KIT_ERA_START if current_kit_era else None)
    summary = build_summary(
        records,
        include_non_dev=include_non_dev,
        kit_related=kit_related,
        since=effective_since,
        cwd_prefixes=cwd_prefixes,
        label="selected",
    )
    summary["sources"] = source_counts
    baseline = build_summary(records, include_non_dev=include_non_dev, label="baseline-all-dev")
    kit_current = build_summary(
        records,
        include_non_dev=include_non_dev,
        kit_related=True,
        since=CURRENT_KIT_ERA_START,
        label="kit-current-era",
    )
    summary["report_sections"] = [
        {
            "title": "Baseline All-Dev Corpus",
            "note": "All local development-looking Codex threads, including non-kit work. Use this as agent workflow telemetry rather than pure kit telemetry.",
            "summary": summary_without_observations(baseline),
        },
        {
            "title": "Kit-Related Current-Era Corpus",
            "note": "Kit-related threads since the unified public kit repo work began. Use this narrower slice for current CLI journey decisions.",
            "summary": summary_without_observations(kit_current),
        },
    ]
    if write:
        write_outputs(summary, records, state_dir or default_state_dir(), report_path, sample_limit)
    return summary


def public_summary(summary: dict[str, Any], include_observations: bool = False) -> dict[str, Any]:
    if include_observations:
        return summary
    result = summary_without_observations(summary)
    result["report_sections"] = [
        {
            **section,
            "summary": summary_without_observations(section["summary"]),
        }
        for section in summary.get("report_sections", [])
    ]
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mine local Codex thread history for kit CLI journey research.")
    parser.add_argument("--codex-home", default=str(DEFAULT_CODEX_HOME), help="Codex local data directory.")
    parser.add_argument("--state-dir", default=str(default_state_dir()), help="Local output directory for JSON artifacts.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Tracked aggregate Markdown report path.")
    parser.add_argument("--include-non-dev", action="store_true", help="Include threads that do not look development-related.")
    parser.add_argument("--kit-related", action="store_true", help="Only include threads with kit/repo-contract command or repo evidence.")
    parser.add_argument("--since", help="Only include threads whose latest timestamp is at or after this ISO timestamp.")
    parser.add_argument("--cwd-prefix", action="append", help="Only include threads whose cwd starts with this path. Can be repeated or comma-separated.")
    parser.add_argument("--current-kit-era", action="store_true", help=f"Shortcut for --since {CURRENT_KIT_ERA_START}.")
    parser.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT, help="Maximum redacted sample rows to write.")
    parser.add_argument("--no-write", action="store_true", help="Compute and print a summary without writing files.")
    parser.add_argument("--include-observations", action="store_true", help="Include hashed per-thread observations in --json stdout.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary to stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = mine_codex_threads(
        codex_home=Path(args.codex_home).expanduser(),
        state_dir=Path(args.state_dir).expanduser(),
        report_path=Path(args.report),
        include_non_dev=args.include_non_dev,
        sample_limit=max(args.sample_limit, 0),
        write=not args.no_write,
        kit_related=args.kit_related,
        since=args.since,
        cwd_prefixes=args.cwd_prefix,
        current_kit_era=args.current_kit_era,
    )
    if args.json:
        print(json.dumps(public_summary(summary, include_observations=args.include_observations), indent=2, sort_keys=True))
    else:
        corpus = summary["corpus"]
        print("Codex thread mining complete")
        print(f" - threads scanned: {corpus['threads_seen']}")
        print(f" - dev threads: {corpus['dev_threads']}")
        if summary.get("outputs"):
            print(f" - summary: {summary['outputs']['summary_json']}")
            print(f" - samples: {summary['outputs']['samples_jsonl']}")
            print(f" - report: {summary['outputs']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
