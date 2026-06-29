import json
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "repo_contract_kit.py"
INSTALL = ROOT / "scripts" / "install.py"


def init_git_repo(path: Path):
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            "Initial sample repo",
        ],
        cwd=path,
        check=True,
    )


def commit_all(path: Path, message: str = "Commit changes"):
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=repo-contract-kit test",
            "-c",
            "user.email=repo-contract-kit@example.invalid",
            "commit",
            "-qm",
            message,
        ],
        cwd=path,
        check=True,
    )


def sha256_text(value: str):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json_file(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, payload: dict):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mark_managed_baseline(repo: Path, rel_path: str, content: str):
    target = repo / rel_path
    target.write_text(content, encoding="utf-8")
    manifest_path = repo / ".doc-contract-kit" / "manifest.json"
    manifest = read_json_file(manifest_path)
    for item in manifest["files"]:
        if item["path"] == rel_path:
            item["installed_sha256"] = sha256_text(content)
            item["managed"] = True
            item["owner"] = "kit"
            break
    write_json_file(manifest_path, manifest)


def init_repo_contract_source(path: Path):
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    (path / "scripts").mkdir(parents=True)
    (path / "scripts" / "repo_contract_kit.py").write_text("# source marker\n", encoding="utf-8")
    (path / "scripts" / "install.py").write_text("# install marker\n", encoding="utf-8")
    commit_all(path, "Initial source checkout")


def add_git_worktree(repo: Path, worktree: Path, branch: str = "codex/automation-handoff"):
    subprocess.run(
        ["git", "worktree", "add", "-q", "-b", branch, str(worktree)],
        cwd=repo,
        check=True,
    )


def load_cli_module():
    spec = importlib.util.spec_from_file_location("repo_contract_kit_under_test", CLI)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class RepoContractKitCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old_xdg_state_home = os.environ.get("XDG_STATE_HOME")
        cls._state_home = tempfile.TemporaryDirectory()
        os.environ["XDG_STATE_HOME"] = cls._state_home.name

    @classmethod
    def tearDownClass(cls):
        if cls._old_xdg_state_home is None:
            os.environ.pop("XDG_STATE_HOME", None)
        else:
            os.environ["XDG_STATE_HOME"] = cls._old_xdg_state_home
        cls._state_home.cleanup()

    def test_executable_entrypoint_reports_version_json(self):
        result = subprocess.run(
            [str(CLI), "version", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "version")
        self.assertEqual(payload["cli"]["entrypoint"], str(CLI))
        self.assertEqual(payload["cli"]["invocation"], str(CLI))
        self.assertFalse(payload["cli"]["writes_target_repo_by_default"])
        self.assertFalse(payload["target_repo_writes"]["performed"])
        self.assertFalse(payload["sidecar_writes"]["performed"])
        self.assertEqual(
            payload["cli"]["mutating_commands"],
            [
                "agent-self-heal --apply",
                "install",
                "setup",
                "start",
                "self update",
                "target add",
                "target import --apply",
                "target prune-missing --apply",
                "target repair-source-clone --apply",
                "target update",
                "target update-all --apply",
                "update",
                "update --all --apply",
                "update --global",
                "worktree prune --apply",
                "migrate-config",
            ],
        )
        self.assertIn("sidecar-init", payload["cli"]["sidecar_write_commands"])
        self.assertIn("feedback", payload["cli"]["sidecar_write_commands"])
        self.assertIn("agent-self-heal --apply", payload["cli"]["sidecar_write_commands"])
        self.assertIn("agent-preflight --write-sidecar", payload["cli"]["sidecar_write_commands"])
        self.assertIn("target import --apply", payload["cli"]["sidecar_write_commands"])
        self.assertIn("target prune-missing --apply", payload["cli"]["sidecar_write_commands"])

    def test_no_args_prints_non_tty_guide_outside_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CLI)],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("kit guide", result.stdout)
            self.assertIn("repo: not a git repo", result.stdout)
            self.assertIn("kit setup", result.stdout)
            self.assertIn("kit options", result.stdout)

    def test_no_args_prints_target_repo_guide_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(CLI)],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status: target-not-installed", result.stdout)
            self.assertIn("installed: false", result.stdout)
            self.assertIn("kit setup", result.stdout)
            self.assertFalse((target / ".doc-contract-kit").exists())

    def test_no_args_guide_surfaces_dirty_installed_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "setup", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install kit")
            (target / "README.md").write_text("# dirty\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI)],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status: target-installed-dirty", result.stdout)
            self.assertIn("dirty: true", result.stdout)
            self.assertIn("git status --short", result.stdout)
            self.assertIn("kit doctor", result.stdout)
            self.assertIn("kit update --dry-run", result.stdout)

    def test_tty_guide_requires_explicit_choice(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            module = load_cli_module()
            payload = module.guide_payload(target)
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                    with mock.patch.object(module.sys.stdout, "isatty", return_value=True):
                        with mock.patch("builtins.input", return_value="q"):
                            exit_code = module.run_guide_interactive(payload)

            self.assertEqual(exit_code, 0)
            self.assertIn("Choose an action:", output.getvalue())
            self.assertIn("No action run.", output.getvalue())
            self.assertFalse((target / ".doc-contract-kit").exists())

    def test_no_input_global_flag_disables_tty_prompt(self):
        module = load_cli_module()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                with mock.patch.object(module.sys.stdout, "isatty", return_value=True):
                    with mock.patch("builtins.input", side_effect=AssertionError("prompted")):
                        exit_code = module.main(["--no-input"])

        self.assertEqual(exit_code, 0)
        self.assertIn("kit guide", output.getvalue())
        self.assertIn("repo role:", output.getvalue())
        self.assertIn("journey:", output.getvalue())
        self.assertIn("Run `kit options`", output.getvalue())
        self.assertNotIn("Choose an action:", output.getvalue())

    def test_kit_agent_mode_disables_tty_prompt(self):
        module = load_cli_module()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            with mock.patch.dict(module.os.environ, {"KIT_AGENT": "1"}):
                with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                    with mock.patch.object(module.sys.stdout, "isatty", return_value=True):
                        with mock.patch("builtins.input", side_effect=AssertionError("prompted")):
                            exit_code = module.main([])

        self.assertEqual(exit_code, 0)
        self.assertIn("kit guide", output.getvalue())
        self.assertIn("Run `kit options`", output.getvalue())
        self.assertNotIn("Choose an action:", output.getvalue())

    def test_palette_is_disabled_without_tty_or_when_no_input(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "palette", "--query", "status", "--print-command"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("kit palette is TTY-only", result.stdout)
        self.assertIn("kit command-map --json", result.stdout)

        module = load_cli_module()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                with mock.patch.object(module.sys.stdout, "isatty", return_value=True):
                    with mock.patch("builtins.input", side_effect=AssertionError("prompted")):
                        exit_code = module.main(["--no-input", "palette"])

        self.assertEqual(exit_code, 0)
        self.assertIn("kit palette is TTY-only", output.getvalue())
        self.assertIn("non-interactive mode", output.getvalue())

        agent_output = io.StringIO()
        with contextlib.redirect_stdout(agent_output):
            with mock.patch.dict(module.os.environ, {"KIT_AGENT": "1"}):
                with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                    with mock.patch.object(module.sys.stdout, "isatty", return_value=True):
                        with mock.patch("builtins.input", side_effect=AssertionError("prompted")):
                            exit_code = module.main(["palette"])

        self.assertEqual(exit_code, 0)
        self.assertIn("kit palette is TTY-only", agent_output.getvalue())
        self.assertIn("non-interactive mode", agent_output.getvalue())

    def test_palette_tty_prints_exact_command_for_query(self):
        module = load_cli_module()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                with mock.patch.object(module.sys.stdout, "isatty", return_value=True):
                    with mock.patch("builtins.input", side_effect=AssertionError("prompted")):
                        exit_code = module.main(["palette", "--query", "status", "--print-command"])

        self.assertEqual(exit_code, 0)
        self.assertIn("kit palette", output.getvalue())
        self.assertIn("Exact command:", output.getvalue())
        self.assertIn("kit status --repo /path/to/repo --json", output.getvalue())
        self.assertNotIn("Choose an item", output.getvalue())

    def test_palette_requires_confirmation_before_printing_mutating_command(self):
        module = load_cli_module()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            with mock.patch.object(module.sys.stdin, "isatty", return_value=True):
                with mock.patch.object(module.sys.stdout, "isatty", return_value=True):
                    with mock.patch("builtins.input", side_effect=["1", "no"]):
                        exit_code = module.main(["palette", "--query", "setup"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Mutating command requires confirmation", output.getvalue())
        self.assertIn("Command not printed.", output.getvalue())

    def test_options_and_help_all_show_human_and_advanced_commands(self):
        options = subprocess.run(
            [sys.executable, str(CLI), "options"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(options.returncode, 0, options.stderr)
        self.assertIn("Daily commands:", options.stdout)
        self.assertIn("kit setup", options.stdout)
        self.assertNotIn("agent-context-bundle", options.stdout)

        help_all = subprocess.run(
            [sys.executable, str(CLI), "help", "--all"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(help_all.returncode, 0, help_all.stderr)
        self.assertIn("Advanced commands remain available", help_all.stdout)
        self.assertIn("kit agent-context-bundle", help_all.stdout)
        self.assertIn("kit command-map --json", help_all.stdout)

    def test_top_level_help_is_scenario_grouped_not_argparse_inventory(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Daily commands:", result.stdout)
        self.assertIn("Agent and automation:", result.stdout)
        self.assertIn("Maintainer commands:", result.stdout)
        self.assertIn("kit help --all", result.stdout)
        self.assertNotIn("positional arguments:", result.stdout)

    def test_options_are_scenario_first_without_advanced_inventory(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "options"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Common scenarios:", result.stdout)
        self.assertIn("New or uncertain repo:", result.stdout)
        self.assertIn("kit start", result.stdout)
        self.assertIn("Existing enrolled repo:", result.stdout)
        self.assertIn("Agent and automation:", result.stdout)
        self.assertNotIn("Advanced commands remain available", result.stdout)

    def test_help_all_includes_advanced_lanes_and_recovery_guidance(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "help", "--all"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Advanced commands remain available", result.stdout)
        self.assertIn("Advanced agent and automation commands:", result.stdout)
        self.assertIn("Maintainer commands:", result.stdout)
        self.assertIn("Parse-error recovery:", result.stdout)
        self.assertIn("KIT_AGENT=1", result.stdout)

    def test_status_text_distinguishes_version_roles_for_installed_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "setup", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            result = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Version roles:", result.stdout)
            self.assertIn("running tool version:", result.stdout)
            self.assertIn("target install version:", result.stdout)
            self.assertIn("target repo version:", result.stdout)
            self.assertIn("prompt snapshot:", result.stdout)
            self.assertIn("source refs:", result.stdout)
            self.assertIn("Worktree state:", result.stdout)
            self.assertIn("Kit managed state:", result.stdout)
            self.assertIn("kit managed state is not Git dirty state", result.stdout)
            self.assertIn("next: kit update --dry-run --repo", result.stdout)

    def test_status_json_splits_git_worktree_state_from_kit_managed_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "setup", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            result = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["git_worktree_state"]["state"], "dirty")
            self.assertTrue(payload["git_worktree_state"]["dirty"])
            self.assertGreater(payload["git_worktree_state"]["untracked_count"], 0)
            self.assertEqual(payload["kit_managed_state"]["state"], "clean")
            self.assertFalse(payload["kit_managed_state"]["dirty_equivalent"])

    def test_status_text_guides_not_installed_repo_to_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("repo-contract-kit installed: false", result.stdout)
        self.assertIn("target install version: not installed", result.stdout)
        self.assertIn("next: kit setup --repo", result.stdout)

    def test_status_json_classifies_stale_target_install_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            receipt_path = target / ".doc-contract-kit" / "install.json"
            manifest_path = target / ".doc-contract-kit" / "manifest.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            receipt["source_version"] = "0.0.1"
            receipt["kit_version"] = "0.0.1"
            receipt["source_ref"] = "old-receipt-ref"
            receipt["prompt_snapshot"]["source_ref"] = "old-prompt-ref"
            receipt["prompt_snapshot"]["snapshot_sha256"] = "old-snapshot"
            manifest["source_ref"] = "old-manifest-ref"
            manifest["prompt_snapshot"]["source_ref"] = "old-prompt-ref"
            manifest["prompt_snapshot"]["snapshot_sha256"] = "old-snapshot"
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        drift = payload["kit_drift"]
        self.assertEqual(drift["classification"], "stale")
        self.assertEqual(drift["reason_code"], "target_older_than_global")
        self.assertEqual(drift["target_install"]["version"], "0.0.1")
        self.assertEqual(drift["global_tool"]["version"], payload["local_kit"]["version"])
        self.assertEqual(drift["comparisons"]["source_ref"], "different")
        self.assertEqual(drift["comparisons"]["prompt_snapshot"], "different")
        commands = [item["command"] for item in drift["next_commands"]]
        self.assertIn(f"kit update --dry-run --repo {payload['repo']}", commands)
        self.assertIn(f"kit update --repo {payload['repo']}", commands)
        self.assertFalse(drift["target_repo_writes"]["performed"])

    def test_status_json_classifies_newer_target_install_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            receipt_path = target / ".doc-contract-kit" / "install.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["source_version"] = "99.0.0"
            receipt["kit_version"] = "99.0.0"
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        drift = payload["kit_drift"]
        self.assertEqual(drift["classification"], "newer-target")
        commands = [item["command"] for item in drift["next_commands"]]
        self.assertIn("kit update --global", commands)
        self.assertIn("kit self update", commands)

    def test_status_text_prints_drift_classification_and_safe_repairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            receipt_path = target / ".doc-contract-kit" / "install.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["source_version"] = "0.0.1"
            receipt["kit_version"] = "0.0.1"
            receipt["source_ref"] = "old-receipt-ref"
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Kit drift:", result.stdout)
        self.assertIn(" - classification: stale", result.stdout)
        self.assertIn(" - reason: target install is older than the running global tool", result.stdout)
        self.assertIn(f"   - kit update --dry-run --repo {target.resolve()}", result.stdout)
        self.assertIn(f"   - kit update --repo {target.resolve()}", result.stdout)

    def test_status_json_reports_non_interactive_and_agent_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            default = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            no_input = subprocess.run(
                [sys.executable, str(CLI), "--no-input", "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            env = os.environ.copy()
            env["KIT_AGENT"] = "1"
            agent = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertEqual(no_input.returncode, 0, no_input.stderr)
        self.assertEqual(agent.returncode, 0, agent.stderr)
        default_payload = json.loads(default.stdout)
        no_input_payload = json.loads(no_input.stdout)
        agent_payload = json.loads(agent.stdout)
        self.assertFalse(default_payload["non_interactive"])
        self.assertFalse(default_payload["agent_mode"])
        self.assertTrue(no_input_payload["non_interactive"])
        self.assertFalse(no_input_payload["agent_mode"])
        self.assertTrue(agent_payload["non_interactive"])
        self.assertTrue(agent_payload["agent_mode"])

    def test_command_map_json_catalogs_commands_without_repo_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CLI), "command-map", "--json"],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["command"], "command-map")
        self.assertEqual(payload["alias_of"], None)
        self.assertFalse(payload["target_repo_writes"]["performed"])
        self.assertFalse(payload["sidecar_writes"]["performed"])
        self.assertEqual(payload["parser_consistency"]["status"], "passed")
        self.assertIn("sidecar_state", payload)

        commands = {" ".join(command["path"]): command for command in payload["commands"]}
        for expected in (
            "status",
            "update",
            "target update",
            "target update-all",
            "task-packet",
            "mode-check",
            "calibration",
            "retention",
            "agent-context-bundle",
            "command-map",
            "start",
        ):
            self.assertIn(expected, commands)

        status = commands["status"]
        self.assertEqual(status["audience"], ["human", "agent"])
        self.assertEqual(status["mutation"], "read-only")
        self.assertTrue(status["json_supported"])
        self.assertEqual(status["sidecar_write"], "never")
        self.assertIn("--repo", [flag["option"] for flag in status["flags"]])
        self.assertIn("kit status --repo /path/to/repo --json", status["examples"])
        self.assertEqual(status["exit_codes"]["0"], "success")
        self.assertEqual(status["output_schema"], "status_payload")
        self.assertIn("README.md#installed-commands", status["docs"])

        start = commands["start"]
        self.assertEqual(start["mutation"], "writes-target-conditionally")
        self.assertIn("local-safe", start["target_repo_write"])
        self.assertIn("local_update", start["json_contract"]["stable_payload_fields"])
        self.assertIn("kit start --no-update", start["examples"])

        update = commands["update"]
        self.assertEqual(update["mutation"], "writes-target-by-default")
        self.assertEqual(update["sidecar_write"], "never")
        self.assertIn("kit update --dry-run --json", update["examples"])

        command_map = commands["command-map"]
        self.assertEqual(command_map["output_schema"], "command_map_payload")
        self.assertEqual(command_map["aliases"], ["agent-context"])
        self.assertIn("kit command-map --json", command_map["examples"])

        start = commands["start"]
        self.assertEqual(start["audience"], ["human", "agent"])
        self.assertEqual(start["mutation"], "writes-target-conditionally")
        self.assertIn("local-safe", start["target_repo_write"])
        self.assertEqual(start["sidecar_write"], "never")
        self.assertEqual(start["output_schema"], "start_payload")
        self.assertIn("kit start --repo /path/to/repo --json", start["examples"])
        self.assertIn("mode", start["json_contract"]["stable_payload_fields"])
        self.assertIn("recommended_setup_preset", start["json_contract"]["stable_payload_fields"])
        self.assertIn("mode_next_commands", start["json_contract"]["stable_payload_fields"])
        self.assertIn("local_update", start["json_contract"]["stable_payload_fields"])

        mode_check = commands["mode-check"]
        self.assertEqual(mode_check["mutation"], "read-only")
        self.assertEqual(mode_check["sidecar_write"], "never")
        self.assertEqual(mode_check["output_schema"], "harness_mode_selection_payload")
        self.assertIn("kit mode-check --repo /path/to/repo --json", mode_check["examples"])

    def test_command_map_catalogs_palette_as_tty_only_human_route(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        commands = {" ".join(command["path"]): command for command in payload["commands"]}
        palette = commands["palette"]
        self.assertEqual(palette["audience"], ["human"])
        self.assertEqual(palette["mutation"], "read-only")
        self.assertEqual(palette["target_repo_write"], "never")
        self.assertEqual(palette["sidecar_write"], "never")
        self.assertFalse(palette["json_supported"])
        self.assertEqual(palette["output_schema"], "tty_command_palette")
        self.assertIn("kit palette --query status", palette["examples"])

    def test_command_map_catalogs_cli_reference_as_generated_docs_route(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        commands = {" ".join(command["path"]): command for command in payload["commands"]}
        cli_reference = commands["cli-reference"]
        self.assertEqual(cli_reference["audience"], ["human", "agent"])
        self.assertEqual(cli_reference["mutation"], "read-only")
        self.assertEqual(cli_reference["target_repo_write"], "with --write")
        self.assertTrue(cli_reference["json_supported"])
        self.assertEqual(cli_reference["output_schema"], "cli_reference_payload")
        self.assertIn("docs/cli-reference.md", cli_reference["docs"])

    def test_command_map_catalogs_agent_tool_manifest_as_read_only_agent_route(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        commands = {" ".join(command["path"]): command for command in payload["commands"]}
        manifest = commands["agent-tool-manifest"]
        self.assertEqual(manifest["audience"], ["agent"])
        self.assertEqual(manifest["mutation"], "read-only")
        self.assertEqual(manifest["target_repo_write"], "never")
        self.assertEqual(manifest["sidecar_write"], "never")
        self.assertTrue(manifest["json_supported"])
        self.assertEqual(manifest["output_schema"], "agent_tool_manifest_payload")
        self.assertIn("kit agent-tool-manifest --json", manifest["examples"])

    def test_cli_reference_generates_markdown_and_json_from_command_map(self):
        markdown = subprocess.run(
            [sys.executable, str(CLI), "cli-reference"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        payload_result = subprocess.run(
            [sys.executable, str(CLI), "cli-reference", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(markdown.returncode, 0, markdown.stderr)
        self.assertIn("# kit CLI Reference", markdown.stdout)
        self.assertIn("Generated from `kit command-map --json`.", markdown.stdout)
        self.assertIn("### kit status", markdown.stdout)
        self.assertIn("`--repo`", markdown.stdout)
        self.assertIn("Target writes:", markdown.stdout)

        self.assertEqual(payload_result.returncode, 0, payload_result.stderr)
        payload = json.loads(payload_result.stdout)
        self.assertEqual(payload["command"], "cli-reference")
        self.assertEqual(payload["source_command"], "kit command-map --json")
        self.assertFalse(payload["target_repo_writes"]["performed"])
        self.assertGreater(payload["command_count"], 40)
        self.assertTrue(any(claim["selector"]["text"] == "### kit status" for claim in payload["docs_as_tests_claims"]))

    def test_cli_reference_check_detects_generated_doc_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            reference = Path(tmp) / "cli-reference.md"
            reference.write_text("# stale\n", encoding="utf-8")

            stale = subprocess.run(
                [sys.executable, str(CLI), "cli-reference", "--check", str(reference)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            generated = subprocess.run(
                [sys.executable, str(CLI), "cli-reference"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            reference.write_text(generated.stdout, encoding="utf-8")
            fresh = subprocess.run(
                [sys.executable, str(CLI), "cli-reference", "--check", str(reference)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(stale.returncode, 1)
        self.assertIn("CLI reference drift", stale.stdout)
        self.assertEqual(fresh.returncode, 0, fresh.stdout + fresh.stderr)
        self.assertIn("CLI reference is current", fresh.stdout)

    def test_command_map_catalogs_completion_as_read_only_human_route(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        commands = {" ".join(command["path"]): command for command in payload["commands"]}
        completion = commands["completion"]
        self.assertEqual(completion["audience"], ["human"])
        self.assertEqual(completion["mutation"], "read-only")
        self.assertEqual(completion["target_repo_write"], "never")
        self.assertEqual(completion["sidecar_write"], "never")
        self.assertFalse(completion["json_supported"])
        self.assertEqual(completion["output_schema"], "shell_completion_script")
        self.assertIn("kit completion zsh", completion["examples"])

    def test_completion_generates_shell_scripts_from_command_map_without_writes(self):
        command_map = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(command_map.returncode, 0, command_map.stderr)
        command_names = [command["name"] for command in json.loads(command_map.stdout)["commands"]]

        with tempfile.TemporaryDirectory() as tmp:
            outputs = {}
            for shell in ("bash", "zsh", "fish"):
                result = subprocess.run(
                    [sys.executable, str(CLI), "completion", shell],
                    cwd=tmp,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(list(Path(tmp).iterdir()), [])
                outputs[shell] = result.stdout

        self.assertIn("complete -F _kit_completion kit", outputs["bash"])
        self.assertIn("#compdef kit", outputs["zsh"])
        self.assertIn("complete -c kit", outputs["fish"])
        for output in outputs.values():
            self.assertIn("--no-input", output)
            self.assertIn("--repo", output)
            self.assertIn("--json", output)
            self.assertIn("bash", output)
            self.assertIn("zsh", output)
            self.assertIn("fish", output)
            for command_name in command_names:
                self.assertIn(command_name, output)

    def test_command_map_publishes_json_contracts_and_stable_fields(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["json_contract"]["schema_version_field"], "schema_version")
        self.assertIn("commands", payload["json_contract"]["stable_payload_fields"])
        self.assertIn("target_repo_writes", payload["json_contract"]["stable_payload_fields"])
        self.assertIn("sidecar_writes", payload["json_contract"]["stable_payload_fields"])

        commands = {" ".join(command["path"]): command for command in payload["commands"]}
        for command in commands.values():
            contract = command["json_contract"]
            self.assertEqual(contract["supported"], command["json_supported"])
            self.assertEqual(contract["output_schema"], command["output_schema"])
            self.assertIn("json_supported", contract["command_map_fields"])
            self.assertIn("output_schema", contract["command_map_fields"])
            self.assertIn("target_repo_write", contract["command_map_fields"])
            self.assertIn("sidecar_write", contract["command_map_fields"])

            if command["json_supported"]:
                self.assertEqual(contract["schema_version_field"], "schema_version")
                self.assertIn("schema_version", contract["stable_payload_fields"])
                self.assertIn("target_repo_writes", contract["stable_payload_fields"])
                self.assertIn("sidecar_writes", contract["stable_payload_fields"])
                self.assertTrue(contract["schema_pointer"].startswith("README.md#json-payload-contracts"))
            else:
                self.assertIsNone(contract["schema_pointer"])
                self.assertIn("does not expose a JSON payload", contract["reason"])

        self.assertEqual(
            commands["target"]["json_contract"]["reason"],
            "Namespace command; it does not expose a JSON payload. Inspect its subcommands.",
        )
        self.assertEqual(
            commands["help"]["json_contract"]["reason"],
            "Text-only command; it does not expose a JSON payload. "
            "Use command-map --json for machine-readable help metadata.",
        )

    def test_command_map_publishes_kit_drift_json_contract_fields(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        commands = {" ".join(command["path"]): command for command in payload["commands"]}
        for name in ("status", "target status"):
            fields = commands[name]["json_contract"]["stable_payload_fields"]
            self.assertIn("kit_drift", fields)
            self.assertIn("install", fields)
            self.assertIn("local_kit", fields)
        for name in ("doctor", "agent-preflight", "agent-doctor", "target doctor"):
            fields = commands[name]["json_contract"]["stable_payload_fields"]
            self.assertIn("kit_drift", fields)
            self.assertIn("warnings", fields)
            self.assertIn("warning_details", fields)

    def test_command_map_marks_canonical_alias_agent_and_maintainer_routes(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "command-map", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        commands = {" ".join(command["path"]): command for command in payload["commands"]}

        setup = commands["setup"]
        self.assertEqual(setup["route_role"], "canonical")
        self.assertEqual(setup["canonical_command"], "setup")
        self.assertEqual(setup["alias_group"], "target-enrollment")
        self.assertIn("target add", setup["aliases"])
        self.assertIn("install", setup["aliases"])

        target_add = commands["target add"]
        self.assertEqual(target_add["route_role"], "alias")
        self.assertEqual(target_add["canonical_command"], "setup")
        self.assertEqual(target_add["alias_group"], "target-enrollment")
        self.assertIn("canonical human route", target_add["route_note"])

        install = commands["install"]
        self.assertEqual(install["route_role"], "agent-only")
        self.assertEqual(install["canonical_command"], "setup")
        self.assertEqual(install["alias_group"], "target-enrollment")
        self.assertIn("explicit install", install["route_note"])

        doctor = commands["doctor"]
        self.assertEqual(doctor["route_role"], "canonical")
        self.assertEqual(doctor["canonical_command"], "doctor")
        self.assertEqual(doctor["alias_group"], "target-diagnostics")

        agent_preflight = commands["agent-preflight"]
        self.assertEqual(agent_preflight["route_role"], "agent-only")
        self.assertEqual(agent_preflight["canonical_command"], "doctor")
        self.assertEqual(agent_preflight["alias_group"], "target-diagnostics")

        agent_doctor = commands["agent-doctor"]
        self.assertEqual(agent_doctor["route_role"], "agent-only")
        self.assertEqual(agent_doctor["canonical_command"], "doctor")

        target_doctor = commands["target doctor"]
        self.assertEqual(target_doctor["route_role"], "alias")
        self.assertEqual(target_doctor["canonical_command"], "doctor")

        self_update = commands["self update"]
        self.assertEqual(self_update["route_role"], "maintainer")
        self.assertEqual(self_update["canonical_command"], "self update")
        self.assertIn("global tool checkout", self_update["route_note"])

        migrate_config = commands["migrate-config"]
        self.assertEqual(migrate_config["route_role"], "compatibility")
        self.assertEqual(migrate_config["canonical_command"], "update --metadata-only")
        self.assertIn("metadata-only", migrate_config["route_note"])

    def test_agent_context_alias_returns_command_map_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            command_map = subprocess.run(
                [sys.executable, str(CLI), "command-map", "--json"],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=False,
            )
            alias = subprocess.run(
                [sys.executable, str(CLI), "agent-context", "--json"],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(command_map.returncode, 0, command_map.stderr)
        self.assertEqual(alias.returncode, 0, alias.stderr)
        command_map_payload = json.loads(command_map.stdout)
        alias_payload = json.loads(alias.stdout)
        self.assertEqual(alias_payload["command"], "agent-context")
        self.assertEqual(alias_payload["alias_of"], "command-map")
        self.assertEqual(alias_payload["commands"], command_map_payload["commands"])
        self.assertFalse(alias_payload["target_repo_writes"]["performed"])
        self.assertFalse(alias_payload["sidecar_writes"]["performed"])

    def test_unknown_command_text_error_is_concise_and_suggests_nearest_command(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "statuz"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("Unknown command: statuz", result.stderr)
        self.assertIn("Did you mean: kit status", result.stderr)
        self.assertIn("kit command-map --json", result.stderr)
        self.assertNotIn("choose from", result.stderr)

    def test_unknown_nested_command_text_error_suggests_nested_command(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "target", "updat"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("Unknown command: target updat", result.stderr)
        self.assertIn("Did you mean: kit target update", result.stderr)
        self.assertNotIn("choose from", result.stderr)

    def test_json_parse_error_envelope_for_unknown_command(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "statuz", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["command"], "parse-error")
        self.assertEqual(payload["error"]["kind"], "unknown-command")
        self.assertEqual(payload["error"]["offending_token"], "statuz")
        self.assertEqual(payload["argv"], ["statuz", "--json"])
        self.assertIn({"type": "command", "value": "status", "command": "kit status"}, payload["suggestions"])
        self.assertIn("kit command-map --json", payload["next_commands"])
        self.assertFalse(payload["target_repo_writes"]["performed"])
        self.assertFalse(payload["sidecar_writes"]["performed"])

    def test_kit_agent_parse_error_envelope_for_invalid_option(self):
        env = os.environ.copy()
        env["KIT_AGENT"] = "1"
        result = subprocess.run(
            [sys.executable, str(CLI), "status", "--jsno"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "parse-error")
        self.assertEqual(payload["error"]["kind"], "invalid-option")
        self.assertEqual(payload["error"]["command_path"], ["status"])
        self.assertEqual(payload["error"]["offending_token"], "--jsno")
        self.assertIn({"type": "option", "value": "--json", "command": "kit status --json"}, payload["suggestions"])

    def test_json_parse_error_envelope_for_invalid_enum_choice(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "agent-context-bundle", "--mode", "branche", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["error"]["kind"], "invalid-choice")
        self.assertEqual(payload["error"]["command_path"], ["agent-context-bundle"])
        self.assertEqual(payload["error"]["offending_token"], "branche")
        self.assertEqual(payload["error"]["argument"], "--mode")
        self.assertEqual(payload["error"]["valid_choices"], ["working-tree", "staged", "branch"])
        self.assertIn({"type": "choice", "value": "branch", "command": "kit agent-context-bundle --mode branch --json"}, payload["suggestions"])

    def test_setup_alias_enrolls_target_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(CLI), "setup", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["returncode"], 0)
            self.assertTrue(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["setup_closeout"]["status"], "needs-commit-or-park")
            self.assertIn("kit closeout-plan --repo", " ".join(payload["setup_closeout"]["next_commands"]))
            self.assertTrue((target / ".doc-contract-kit" / "install.json").exists())

    def test_setup_registers_target_for_update_all_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            setup = subprocess.run(
                [sys.executable, str(CLI), "setup", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)
            setup_payload = json.loads(setup.stdout)
            self.assertEqual(setup_payload["target_registry"]["entry"]["root"], str(target.resolve()))
            registry_path = Path(setup_payload["target_registry"]["path"])
            self.assertTrue(registry_path.exists())

            result = subprocess.run(
                [sys.executable, str(CLI), "update", "--all", "--dry-run", "--json"],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "target-update-all")
            self.assertEqual(payload["mode"], "dry-run")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["registry"]["target_count"], 1)
            self.assertEqual(payload["summary"]["statuses"]["planned"], 1)
            self.assertEqual(payload["targets"][0]["root"], str(target.resolve()))

    def test_target_update_all_apply_skips_dirty_registered_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            setup = subprocess.run(
                [sys.executable, str(CLI), "setup", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "update-all", "--apply", "--json"],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "apply")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["summary"]["statuses"]["skipped-dirty"], 1)
            self.assertEqual(payload["targets"][0]["status"], "skipped-dirty")

    def test_target_prune_missing_cleans_stale_registry_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            setup = subprocess.run(
                [sys.executable, str(CLI), "setup", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)
            registry_path = Path(json.loads(setup.stdout)["target_registry"]["path"])
            shutil.rmtree(target)

            blocked = subprocess.run(
                [sys.executable, str(CLI), "update", "--all", "--dry-run", "--json"],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
            blocked_payload = json.loads(blocked.stdout)
            self.assertEqual(blocked_payload["summary"]["statuses"]["missing"], 1)
            self.assertIn("kit target prune-missing --dry-run", blocked_payload["next_commands"])

            preview = subprocess.run(
                [sys.executable, str(CLI), "target", "prune-missing", "--dry-run", "--json"],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            preview_payload = json.loads(preview.stdout)
            self.assertFalse(preview_payload["target_repo_writes"]["performed"])
            self.assertFalse(preview_payload["sidecar_writes"]["performed"])
            self.assertEqual(preview_payload["summary"]["prunable"], 1)
            self.assertEqual(json.loads(registry_path.read_text(encoding="utf-8"))["targets"][0]["root"], str(target.resolve()))

            apply = subprocess.run(
                [sys.executable, str(CLI), "target", "prune-missing", "--apply", "--json"],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(apply.returncode, 0, apply.stderr)
            apply_payload = json.loads(apply.stdout)
            self.assertFalse(apply_payload["target_repo_writes"]["performed"])
            self.assertTrue(apply_payload["sidecar_writes"]["performed"])
            self.assertEqual(apply_payload["summary"]["pruned"], 1)
            self.assertEqual(json.loads(registry_path.read_text(encoding="utf-8"))["targets"], [])

    def test_target_import_seeds_primary_repos_and_excludes_agent_worktrees(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            primary = root / "primary"
            primary.mkdir()
            init_git_repo(primary)
            worktree_like = root / "primary-agent-worktrees" / "task-001"
            worktree_like.mkdir(parents=True)
            init_git_repo(worktree_like)
            state_home = root / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}
            for repo in (primary, worktree_like):
                install = subprocess.run(
                    [sys.executable, str(INSTALL), str(repo), "--preset", "minimal"],
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(install.returncode, 0, install.stderr)

            preview = subprocess.run(
                [sys.executable, str(CLI), "target", "import", "--root", str(root), "--dry-run", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            preview_payload = json.loads(preview.stdout)
            self.assertFalse(preview_payload["sidecar_writes"]["performed"])
            self.assertEqual(preview_payload["summary"]["would_import"], 1)
            self.assertEqual(preview_payload["summary"]["skip_reasons"]["excluded"], 1)
            self.assertIn(str(primary.resolve()), {item["root"] for item in preview_payload["targets"] if item["status"] == "would-import"})

            apply = subprocess.run(
                [sys.executable, str(CLI), "target", "import", "--root", str(root), "--apply", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(apply.returncode, 0, apply.stderr)
            apply_payload = json.loads(apply.stdout)
            self.assertTrue(apply_payload["sidecar_writes"]["performed"])
            self.assertFalse(apply_payload["target_repo_writes"]["performed"])
            self.assertEqual(apply_payload["summary"]["imported"], 1)
            self.assertEqual(apply_payload["registry"]["target_count"], 1)

            listed = subprocess.run(
                [sys.executable, str(CLI), "target", "list", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            list_payload = json.loads(listed.stdout)
            self.assertEqual(list_payload["registry"]["target_count"], 1)
            self.assertEqual(list_payload["targets"][0]["root"], str(primary.resolve()))

    def test_worktree_audit_and_prune_remove_only_clean_linked_agent_worktrees(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "primary"
            repo.mkdir()
            init_git_repo(repo)
            worktree = root / "primary-agent-worktrees" / "task-001"
            worktree.parent.mkdir()
            add_git_worktree(repo, worktree, branch="codex/task-001")
            state_home = root / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            audit = subprocess.run(
                [sys.executable, str(CLI), "worktree", "audit", "--root", str(root), "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(audit.returncode, 0, audit.stderr)
            audit_payload = json.loads(audit.stdout)
            self.assertEqual(audit_payload["summary"]["removable"], 1)
            self.assertEqual(audit_payload["worktrees"][0]["root"], str(worktree.resolve()))

            preview = subprocess.run(
                [sys.executable, str(CLI), "worktree", "prune", "--root", str(root), "--dry-run", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            preview_payload = json.loads(preview.stdout)
            self.assertFalse(preview_payload["filesystem_writes"]["performed"])
            self.assertEqual(preview_payload["summary"]["would_remove"], 1)
            self.assertTrue(worktree.exists())

            apply = subprocess.run(
                [sys.executable, str(CLI), "worktree", "prune", "--root", str(root), "--apply", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(apply.returncode, 0, apply.stdout + apply.stderr)
            apply_payload = json.loads(apply.stdout)
            self.assertTrue(apply_payload["filesystem_writes"]["performed"])
            self.assertEqual(apply_payload["summary"]["removed"], 1)
            self.assertFalse(worktree.exists())

    def test_doctor_alias_reports_preflight_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# dirty\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "doctor", "--repo", str(target), "--strict", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "doctor")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertIn("Current checkout has uncommitted changes.", payload["blockers"])

    def test_doctor_text_leads_with_compact_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# dirty\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "doctor", "--repo", str(target), "--strict"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertTrue(result.stdout.startswith("kit doctor summary for "))
            self.assertIn(" - result: blocked", result.stdout)
            self.assertIn(" - blockers: 1", result.stdout)
            self.assertIn(" - changed files: 1", result.stdout)
            self.assertIn(" - target writes: false", result.stdout)
            self.assertIn(" - sidecar writes: false", result.stdout)
            self.assertIn("Details:", result.stdout)
            self.assertIn("   - Current checkout has uncommitted changes.", result.stdout)

    def test_doctor_json_warns_about_stale_target_install_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            receipt_path = target / ".doc-contract-kit" / "install.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["source_version"] = "0.0.1"
            receipt["kit_version"] = "0.0.1"
            receipt["source_ref"] = "old-receipt-ref"
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "doctor", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["kit_drift"]["classification"], "stale")
        self.assertIn("Target kit install is stale relative to the running global tool.", payload["warnings"])
        details = [item for item in payload["warning_details"] if item.get("code") == "kit_drift_stale"]
        self.assertEqual(len(details), 1)
        self.assertIn(f"kit update --dry-run --repo {payload['repo']}", [item["command"] for item in payload["kit_drift"]["next_commands"]])

    def test_doctor_pretty_style_adds_ansi_without_changing_text_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# dirty\n", encoding="utf-8")
            env = os.environ.copy()
            env.pop("NO_COLOR", None)

            result = subprocess.run(
                [sys.executable, str(CLI), "--style", "pretty", "doctor", "--repo", str(target), "--strict"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("\x1b[", result.stdout)
            self.assertIn("kit doctor summary for ", result.stdout)
            self.assertIn(" - blockers: 1", result.stdout)
            self.assertIn("Details:", result.stdout)

    def test_no_color_disables_pretty_style_for_human_summaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# dirty\n", encoding="utf-8")
            env = os.environ.copy()
            env["NO_COLOR"] = "1"

            result = subprocess.run(
                [sys.executable, str(CLI), "--style", "pretty", "doctor", "--repo", str(target), "--strict"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn("\x1b[", result.stdout)
            self.assertTrue(result.stdout.startswith("kit doctor summary for "))

    def test_json_output_ignores_pretty_style(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# dirty\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "--style", "pretty", "doctor", "--repo", str(target), "--strict", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn("\x1b[", result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "doctor")

    def test_self_status_json_does_not_require_target_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CLI), "self", "status", "--json"],
                cwd=tmp,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "self-status")
            self.assertEqual(payload["tool"]["root"], str(ROOT))
            self.assertFalse(payload["target_repo_writes"]["performed"])

    def test_status_json_reports_plain_repo_without_installing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "status")
            self.assertEqual(payload["repo"], str(target.resolve()))
            self.assertEqual(payload["cli"]["entrypoint"], str(CLI))
            self.assertFalse(payload["install"]["installed"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(
                payload["sidecar_state"]["base_dir"],
                str((state_home / "repo-contract-kit").resolve()),
            )
            self.assertTrue(payload["sidecar_state"]["repo_state_dir"].startswith(str(state_home.resolve())))
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_read_only_commands_do_not_create_target_or_sidecar_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            commands = [
                [str(CLI), "start", "--repo", str(target), "--json"],
                [str(CLI), "orient", "--repo", str(target), "--json"],
                [str(CLI), "mode-check", "--repo", str(target), "--json"],
                [str(CLI), "review-plan", "--repo", str(target), "--json"],
                [str(CLI), "agent-preflight", "--repo", str(target), "--json"],
                [str(CLI), "agent-self-heal", "--repo", str(target), "--json"],
                [
                    str(CLI),
                    "doc-impact",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "README.md",
                    "--json",
                ],
                [
                    str(CLI),
                    "changelog-update",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "README.md",
                    "--json",
                ],
                [
                    str(CLI),
                    "docs-explain",
                    "--repo",
                    str(target),
                    "--question",
                    "What docs policy exists?",
                    "--json",
                ],
                [
                    str(CLI),
                    "goal-check",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "README.md",
                    "--json",
                ],
                [str(CLI), "agent-context-bundle", "--repo", str(target), "--json"],
                [str(CLI), "calibration", "--repo", str(target), "--json"],
                [str(CLI), "retention", "--repo", str(target), "--json"],
                [str(CLI), "instruction-diet", "--repo", str(target), "--json"],
                [str(CLI), "verify", "--repo", str(target), "--changed-file", "README.md", "--json"],
                [
                    str(CLI),
                    "task-packet",
                    "--repo",
                    str(target),
                    "--task-id",
                    "AGW-076",
                    "--title",
                    "Sidecar state",
                    "--problem",
                    "Read-only commands need state paths outside the target repo.",
                    "--json",
                ],
                [str(CLI), "onboarding-pr", "--repo", str(target), "--json"],
            ]

            state_dirs = []
            for command in commands:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertFalse(payload["target_repo_writes"]["performed"])
                state_dirs.append(payload["sidecar_state"]["repo_state_dir"])

            self.assertEqual(len(set(state_dirs)), 1)
            self.assertTrue(state_dirs[0].startswith(str(state_home.resolve())))
            self.assertNotIn(str(target.resolve()), state_dirs[0])
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_start_json_guides_unenrolled_repo_to_lite_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "start")
            self.assertEqual(payload["repo"], str(target.resolve()))
            self.assertEqual(payload["repo_role"], "target-unenrolled")
            self.assertEqual(payload["journey"]["id"], "new-repo")
            self.assertEqual(payload["mode"]["selected"], "lite")
            self.assertEqual(payload["recommended_setup_preset"], "lite")
            self.assertFalse(payload["repo_status"]["installed"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertIn(f"kit setup --preset lite --repo {target.resolve()}", payload["next_commands"])
            self.assertIn(f"kit start --repo {target.resolve()} --json", payload["next_commands"])
            self.assertEqual(payload["agent_next_commands"], [f"kit start --repo {target.resolve()} --json"])
            self.assertIn(f"kit mode-check --repo {target.resolve()} --json", payload["mode_next_commands"])
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_start_lite_alias_matches_mode_lite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            mode_result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--mode", "lite", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            alias_result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--lite", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(mode_result.returncode, 0, mode_result.stderr)
            self.assertEqual(alias_result.returncode, 0, alias_result.stderr)
            mode_payload = json.loads(mode_result.stdout)
            alias_payload = json.loads(alias_result.stdout)
            self.assertEqual(alias_payload["mode"], mode_payload["mode"])
            self.assertEqual(alias_payload["next_commands"], mode_payload["next_commands"])
            self.assertEqual(alias_payload["mode"]["requested"], "lite")

    def test_start_applies_local_safe_update_for_installed_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "agentic", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            mark_managed_baseline(target, "AGENTS.md", "# Old managed agents\n")
            commit_all(target, "Commit old managed baseline")

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            local_update = payload["local_update"]
            self.assertTrue(local_update["checked"])
            self.assertTrue(local_update["available"])
            self.assertTrue(local_update["applied"])
            self.assertEqual(local_update["mode"], "local-safe")
            self.assertTrue(payload["target_repo_writes"]["performed"])
            self.assertIn("AGENTS.md", payload["target_repo_writes"]["paths"])
            self.assertIn(".doc-contract-kit/install.json", payload["target_repo_writes"]["paths"])
            self.assertIn(".doc-contract-kit/manifest.json", payload["target_repo_writes"]["paths"])
            self.assertNotEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "# Old managed agents\n")
            self.assertIn("# AGENTS.md", (target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_start_no_update_skips_local_update_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "agentic", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            mark_managed_baseline(target, "AGENTS.md", "# Old managed agents\n")
            commit_all(target, "Commit old managed baseline")

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--no-update", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["local_update"]["checked"])
            self.assertFalse(payload["local_update"]["available"])
            self.assertFalse(payload["local_update"]["applied"])
            self.assertEqual(payload["local_update"]["mode"], "disabled")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "# Old managed agents\n")

    def test_start_check_only_reports_local_update_without_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "agentic", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            mark_managed_baseline(target, "AGENTS.md", "# Old managed agents\n")
            commit_all(target, "Commit old managed baseline")

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--update-policy", "check-only", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["local_update"]["checked"])
            self.assertTrue(payload["local_update"]["available"])
            self.assertFalse(payload["local_update"]["applied"])
            self.assertEqual(payload["local_update"]["mode"], "check-only")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "# Old managed agents\n")

    def test_start_blocks_customized_update_conflict_without_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "agentic", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Commit kit install")
            customized = (target / "AGENTS.md").read_text(encoding="utf-8") + "\nTarget-specific instruction.\n"
            (target / "AGENTS.md").write_text(customized, encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["local_update"]["checked"])
            self.assertTrue(payload["local_update"]["available"])
            self.assertFalse(payload["local_update"]["applied"])
            self.assertIn("customized-managed-file:AGENTS.md", payload["local_update"]["blocked_by"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), customized)

    def test_start_json_detects_running_source_checkout(self):
        result = subprocess.run(
            [str(CLI), "start", "--repo", str(ROOT), "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["repo_role"], "kit-source")
        self.assertEqual(payload["journey"]["id"], "maintainer-source")
        self.assertIsNone(payload["recommended_setup_preset"])
        self.assertIn("make docs-check", payload["human_next_commands"])
        self.assertIn("kit command-map --json", payload["agent_next_commands"])

    def test_guide_json_includes_start_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [str(CLI), "guide", "--json"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "guide")
            self.assertEqual(payload["start"]["repo_role"], "target-unenrolled")
            self.assertEqual(payload["start"]["journey"]["id"], "new-repo")
            self.assertEqual(payload["start"]["mode"]["selected"], "lite")
            self.assertIn(f"kit start --repo {target.resolve()} --json", payload["start"]["agent_next_commands"])

    def test_start_text_prints_journey_mode_and_next_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("kit start", result.stdout)
            self.assertIn("repo role: target-unenrolled", result.stdout)
            self.assertIn("journey: new-repo", result.stdout)
            self.assertIn("mode: lite", result.stdout)
            self.assertIn("kit setup --preset lite", result.stdout)
            self.assertIn(f"json: kit start --repo {target.resolve()} --json", result.stdout)

    def test_start_json_recommends_agentic_setup_for_unenrolled_public_contract_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "scripts").mkdir()
            (target / "scripts" / "repo_contract_kit.py").write_text("# initial\n", encoding="utf-8")
            commit_all(target, "Add CLI script")
            (target / "scripts" / "repo_contract_kit.py").write_text("# public cli change\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["journey"]["id"], "new-repo")
            self.assertEqual(payload["mode"]["selected"], "release-gated")
            self.assertEqual(payload["recommended_setup_preset"], "agentic")
            self.assertIn(f"kit setup --preset agentic --repo {target.resolve()}", payload["next_commands"])

    def test_start_json_escalates_public_contract_change_to_release_gated(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "scripts").mkdir()
            (target / "scripts" / "repo_contract_kit.py").write_text("# initial\n", encoding="utf-8")
            commit_all(target, "Add CLI script")
            (target / ".doc-contract-kit").mkdir()
            (target / ".doc-contract-kit" / "install.json").write_text(
                json.dumps({"kit_version": "0.6.25", "preset": "agentic"}) + "\n",
                encoding="utf-8",
            )
            (target / "scripts" / "repo_contract_kit.py").write_text("# public cli change\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "start", "--repo", str(target), "--mode", "lite", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["journey"]["id"], "work-in-progress")
            self.assertEqual(payload["mode"]["requested"], "lite")
            self.assertEqual(payload["mode"]["selected"], "release-gated")
            self.assertIn("release-gated", payload["mode"]["trigger_reasons"])
            self.assertIn("make version-check", payload["mode_next_commands"])
            self.assertIn(
                f"kit task-packet --harness-mode release-gated --repo {target.resolve()} --json",
                payload["next_commands"],
            )
            self.assertIn(
                f"kit verify --harness-mode release-gated --repo {target.resolve()} --json",
                payload["agent_next_commands"],
            )

    def test_mode_check_selects_lite_for_clean_low_risk_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [str(CLI), "mode-check", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "mode-check")
            self.assertEqual(payload["requested_mode"], "auto")
            self.assertEqual(payload["selected_mode"], "lite")
            self.assertEqual(payload["trigger_reasons"], [])
            self.assertTrue(payload["human_override"]["can_choose_stricter"])
            self.assertTrue(payload["human_override"]["can_downgrade"])
            self.assertIn("kit task-packet --harness-mode lite --repo <repo> --json", payload["next_commands"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])

    def test_mode_check_forces_release_gated_for_public_contract_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "scripts").mkdir()
            (target / "scripts" / "repo_contract_kit.py").write_text("# initial\n", encoding="utf-8")
            commit_all(target, "Add CLI script")
            (target / "scripts" / "repo_contract_kit.py").write_text("# public cli change\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "mode-check", "--repo", str(target), "--mode", "lite", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["requested_mode"], "lite")
            self.assertEqual(payload["selected_mode"], "release-gated")
            self.assertFalse(payload["human_override"]["can_downgrade"])
            self.assertIn("scripts/repo_contract_kit.py", payload["human_override"]["downgrade_blockers"][0])
            self.assertIn("release-gated", payload["trigger_reasons"])
            self.assertIn("make version-check", payload["next_commands"])

    def test_mode_check_selects_standard_for_local_implementation_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "src").mkdir()
            (target / "src" / "app.py").write_text("print('initial')\n", encoding="utf-8")
            commit_all(target, "Add app source")
            (target / "src" / "app.py").write_text("print('changed')\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "mode-check", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["selected_mode"], "standard")
            self.assertIn("standard", payload["trigger_reasons"])
            self.assertIn("make docs-check", payload["next_commands"])

    def test_mode_check_allows_human_forced_stricter_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [str(CLI), "mode-check", "--repo", str(target), "--mode", "release-gated", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["requested_mode"], "release-gated")
            self.assertEqual(payload["detected_mode"], "lite")
            self.assertEqual(payload["selected_mode"], "release-gated")
            self.assertTrue(payload["human_override"]["can_downgrade"])
            self.assertEqual(payload["trigger_reasons"], [])

    def test_task_packet_lite_harness_mode_emits_compact_note_with_escalation_triggers(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "task-packet",
                    "--repo",
                    str(target),
                    "--task-id",
                    "LITE-001",
                    "--title",
                    "Tighten local README copy",
                    "--problem",
                    "A small docs-only edit needs a bounded note.",
                    "--harness-mode",
                    "lite",
                    "--docs-impact",
                    "yes",
                    "--acceptance",
                    "README wording is updated and docs checks pass.",
                    "--validation",
                    "make docs-check",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode_selection"]["selected_mode"], "lite")
            self.assertEqual(payload["lite_task_note"]["task_id"], "LITE-001")
            self.assertEqual(payload["lite_task_note"]["minimum_validation"], ["make docs-check"])
            self.assertIn(
                "public CLI/API/config/schema/release metadata changes",
                payload["lite_task_note"]["escalation_triggers"],
            )
            self.assertNotIn("closeout_requirements", payload)

    def test_verify_auto_harness_mode_reports_selected_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    str(CLI),
                    "verify",
                    "--repo",
                    str(target),
                    "--harness-mode",
                    "auto",
                    "--changed-file",
                    "README.md",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode_selection"]["selected_mode"], "lite")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])

    def test_calibration_and_retention_reports_are_read_only_and_schema_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            calibration = subprocess.run(
                [str(CLI), "calibration", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            retention = subprocess.run(
                [str(CLI), "retention", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(calibration.returncode, 0, calibration.stderr)
            self.assertEqual(retention.returncode, 0, retention.stderr)
            calibration_payload = json.loads(calibration.stdout)
            retention_payload = json.loads(retention.stdout)
            for key in (
                "time_to_orient",
                "commands_to_green",
                "stale_start_prevention",
                "packet_escalation_reasons",
                "skipped_checks",
                "false_positive_disposition",
                "human_burden",
            ):
                self.assertIn(key, calibration_payload["metrics"])
            self.assertEqual(retention_payload["retention_policy"]["default_retention_days"], 90)
            self.assertIn("private-local", retention_payload["retention_policy"]["privacy_labels"])
            self.assertFalse(retention_payload["purge_preview"]["deletes_by_default"])
            self.assertFalse(calibration_payload["target_repo_writes"]["performed"])
            self.assertFalse(retention_payload["target_repo_writes"]["performed"])

    def test_changelog_update_json_reports_candidate_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            (target / "VERSION").write_text("1.2.3\n", encoding="utf-8")
            (target / "CHANGELOG.md").write_text("# Changelog\n\n", encoding="utf-8")
            original_version = (target / "VERSION").read_text(encoding="utf-8")
            original_changelog = (target / "CHANGELOG.md").read_text(encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "changelog-update",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "cli/new_command.py",
                    "--bump",
                    "minor",
                    "--summary",
                    "Add the local changelog helper.",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "changelog-update")
            self.assertEqual(payload["result"], "changelog-update-required")
            self.assertEqual(payload["candidate_changelog_entry"]["heading"], "## 1.3.0 - <date>")
            self.assertIn("Add the local changelog helper.", payload["candidate_changelog_entry"]["text"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse((state_home / "repo-contract-kit").exists())
            self.assertEqual((target / "VERSION").read_text(encoding="utf-8"), original_version)
            self.assertEqual((target / "CHANGELOG.md").read_text(encoding="utf-8"), original_changelog)

    def test_docs_explain_json_reports_cited_prompt_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            docs_dir = target / "docs" / "ops"
            docs_dir.mkdir(parents=True)
            (docs_dir / "agent-workflow.md").write_text(
                "# Agent Workflow\n\n"
                "## Docs Policy\n\n"
                "Run docs-impact before waiving docs work. Agents must route missing "
                "coverage to docs-propose or `/add-docs --mode propose`; waiver approval "
                "requires a human reason.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    str(CLI),
                    "docs-explain",
                    "--repo",
                    str(target),
                    "--question",
                    "Can an agent waive docs work?",
                    "--focus",
                    "waiver",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "docs-explain")
            self.assertEqual(payload["result"], "matched")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse(payload["network"]["used"])
            self.assertEqual(payload["repo"], str(target.resolve()))
            self.assertEqual(payload["sidecar_state"]["repo"]["root"], str(target.resolve()))
            self.assertTrue(payload["citations"])
            self.assertEqual(payload["citations"][0]["path"], "docs/ops/agent-workflow.md")
            self.assertIn("human reason", payload["citations"][0]["snippet"])
            self.assertIn("Do not waive documentation work", payload["local_prompt"]["text"])
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_docs_as_tests_json_reports_local_api_assertions_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            (target / "docs").mkdir()
            (target / "docs" / "api.md").write_text("# API\n\nGET /health\n", encoding="utf-8")
            (target / "openapi.json").write_text(
                json.dumps({"openapi": "3.1.0", "paths": {"/health": {"get": {"responses": {}}}}}),
                encoding="utf-8",
            )
            config = target / ".agent-workflows" / "docs-as-tests.json"
            config.parent.mkdir()
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "assertions": [
                            {
                                "id": "api-health-get",
                                "kind": "openapi_operation_exists",
                                "source_doc": "docs/api.md",
                                "spec": "openapi.json",
                                "selector": {"method": "GET", "path": "/health"},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            original_config = config.read_text(encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "docs-as-tests",
                    "--repo",
                    str(target),
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "docs-as-tests")
            self.assertEqual(payload["result"], "passed")
            self.assertFalse(payload["target_repo_writes"])
            self.assertFalse(payload["network_used"])
            self.assertEqual(payload["assertions"][0]["id"], "api-health-get")
            self.assertEqual(payload["assertions"][0]["source_doc_path"], "docs/api.md")
            self.assertEqual(payload["assertions"][0]["spec_path"], "openapi.json")
            self.assertIn("sidecar_state", payload)
            self.assertEqual(config.read_text(encoding="utf-8"), original_config)
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_instruction_diet_reports_offload_recommendations_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            (target / "Makefile").write_text(".PHONY: agent-start\nagent-start:\n\t@true\n", encoding="utf-8")
            (target / ".agent-workflows").mkdir()
            (target / ".agent-workflows" / "instruction-budgets.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "budgets": [
                            {
                                "pattern": "AGENTS.md",
                                "max_lines": 4,
                                "max_rule_bullets": 1,
                                "severity": "warning",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            command_block = "\n".join("make agent-start" for _ in range(5))
            (target / "AGENTS.md").write_text(
                f"# AGENTS\n\n```bash\n{command_block}\n```\n"
                "- Agents must preserve receipts because dirty-start failures need evidence.\n",
                encoding="utf-8",
            )
            (target / "REVIEW.md").write_text("```bash\nmake agent-start\n```\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "instruction-diet",
                    "--repo",
                    str(target),
                    "--strict-paths",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "instruction-diet")
            self.assertEqual(payload["status"], "review")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            categories = {item["category"] for item in payload["recommendations"]}
            self.assertIn("budget_pressure", categories)
            self.assertIn("route_map_violation", categories)
            self.assertIn("duplicated_procedural_detail", categories)
            self.assertTrue(any(item["suggested_destination"] for item in payload["recommendations"]))
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_agent_context_bundle_json_composes_compact_sections_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            (target / "BACKLOG.md").write_text("- [ ] AGW-001: Add compact context P1\n", encoding="utf-8")
            config = target / ".agent-workflows" / "area-contracts.json"
            config.parent.mkdir(parents=True)
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_goal": "Keep target context compact.",
                        "path_contracts": [
                            {"path": "src/", "purpose": "Application source", "status": "aligned"},
                            {"path": ".agent-workflows/", "purpose": "Agent workflow config", "status": "aligned"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "BACKLOG.md", ".agent-workflows/area-contracts.json"], cwd=target, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Add backlog and area contracts",
                ],
                cwd=target,
                check=True,
            )
            (target / "src").mkdir()
            (target / "src" / "app.py").write_text("print('one')\n", encoding="utf-8")
            (target / "src" / "other.py").write_text("print('two')\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "agent-context-bundle",
                    "--repo",
                    str(target),
                    "--json",
                    "--max-files",
                    "1",
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "agent-context-bundle")
            self.assertEqual(payload["summary"]["changed_file_count"], 2)
            self.assertEqual(payload["summary"]["next_item_id"], "AGW-001")
            self.assertEqual(payload["sections"]["dirty_state"]["status"], "warning")
            self.assertEqual(payload["sections"]["goal_check"]["data"]["summary"]["aligned"], 2)
            self.assertEqual(payload["sections"]["docs_impact"]["data"]["result"], "covered-or-no-impact")
            self.assertEqual(payload["sections"]["task_status"]["data"]["active_task_count"], 0)
            self.assertEqual(payload["sections"]["token_budget"]["data"]["result"], "passed")
            self.assertTrue(any(item["section"] == "dirty_state" for item in payload["omissions"]))
            self.assertTrue(any(item["section"] == "goal_check" for item in payload["omissions"]))
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_agent_context_bundle_text_reports_sections_and_omissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "src").mkdir()
            (target / "src" / "app.py").write_text("print('one')\n", encoding="utf-8")
            (target / "src" / "other.py").write_text("print('two')\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "agent-context-bundle",
                    "--repo",
                    str(target),
                    "--max-files",
                    "1",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Agent context bundle", result.stdout)
            self.assertIn(" - sections:", result.stdout)
            self.assertIn(" - omissions:", result.stdout)
            self.assertIn("make agent-context-bundle", result.stdout)

    def test_agent_preflight_reports_clean_repo_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "agent-preflight", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "agent-preflight")
            self.assertEqual(payload["result"], "passed")
            self.assertFalse(payload["dirty"]["dirty"])
            self.assertEqual(payload["worktrees"]["registered_count"], 1)
            self.assertIn("make agent-task-prepare TASK=<id> SCOPE=<paths>", payload["recommendations"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_agent_preflight_strict_blocks_dirty_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# Dirty repo\n", encoding="utf-8")
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "agent-preflight", "--repo", str(target), "--strict", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertTrue(payload["dirty"]["dirty"])
            self.assertEqual(payload["dirty"]["tracked_files"], ["README.md"])
            self.assertEqual(payload["dirty"]["attribution"]["source"], "unknown")
            self.assertIn("Current checkout has uncommitted changes.", payload["blockers"])
            dirty_detail = next(item for item in payload["blocker_details"] if item["code"] == "dirty_checkout")
            self.assertEqual(dirty_detail["attribution"]["source"], "unknown")
            self.assertIn("git status --short", payload["recommendations"])
            self.assertIn(
                "Preserve current changes: identify the owner from attribution/receipts, then get explicit closeout or handoff before changing the dirty state; use DIRTY_PRIMARY_BASELINE=1 only when that risk is intentional.",
                payload["recommendations"],
            )
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_agent_preflight_write_sidecar_writes_receipt_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "agent-doctor", "--repo", str(target), "--write-sidecar", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "agent-doctor")
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            receipt_path = Path(payload["receipt"]["path"])
            self.assertTrue(receipt_path.exists())
            saved = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["command"], "agent-doctor")
            self.assertTrue(saved["sidecar"]["available"])
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())

    def test_feedback_add_writes_sidecar_jsonl_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "feedback",
                    "--repo",
                    str(target),
                    "--message",
                    "status recovery was unclear",
                    "--context-command",
                    "kit statuz",
                    "--last-error",
                    "Unknown command: statuz",
                    "--source",
                    "agent",
                    "--tag",
                    "parse-error",
                    "--json",
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "feedback")
            self.assertEqual(payload["action"], "add")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertFalse(payload["privacy"]["upstream_submission"])
            self.assertFalse(payload["privacy"]["network_calls"])
            self.assertEqual(payload["entry"]["message"], "status recovery was unclear")
            self.assertEqual(payload["entry"]["context"]["command"], "kit statuz")
            self.assertEqual(payload["entry"]["last_error"], "Unknown command: statuz")
            self.assertEqual(payload["entry"]["source"], "agent")
            self.assertEqual(payload["entry"]["tags"], ["parse-error"])
            self.assertEqual(payload["entry"]["target_version"], None)
            ledger_path = Path(payload["ledger"]["path"])
            self.assertTrue(ledger_path.exists())
            self.assertIn(str(ledger_path), payload["sidecar_writes"]["paths"])
            lines = ledger_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            saved = json.loads(lines[0])
            self.assertEqual(saved["id"], payload["entry"]["id"])
            status = subprocess.run(["git", "status", "--short"], cwd=target, capture_output=True, text=True, check=False)
            self.assertEqual(status.stdout, "")

    def test_feedback_export_reads_ledger_without_sidecar_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}
            add = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "feedback",
                    "--repo",
                    str(target),
                    "--message",
                    "doctor summary needs clearer next command",
                    "--source",
                    "human",
                    "--json",
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(add.returncode, 0, add.stderr)

            result = subprocess.run(
                [sys.executable, str(CLI), "feedback", "--repo", str(target), "--export-json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["action"], "export")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["entries"][0]["message"], "doctor summary needs clearer next command")

    def test_feedback_empty_export_does_not_create_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            env = {**os.environ, "XDG_STATE_HOME": str(state_home)}

            result = subprocess.run(
                [sys.executable, str(CLI), "feedback", "--repo", str(target), "--export-json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["entries"], [])
            self.assertFalse(payload["ledger"]["exists"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse(Path(payload["sidecar_state"]["repo_state_dir"]).exists())

    def test_agent_tool_manifest_json_is_command_map_derived_and_read_only(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "agent-tool-manifest", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "agent-tool-manifest")
        self.assertEqual(payload["source_command"], "kit command-map --json")
        self.assertFalse(payload["target_repo_writes"]["performed"])
        self.assertFalse(payload["sidecar_writes"]["performed"])
        self.assertFalse(payload["integration_contract"]["network_calls"])
        self.assertFalse(payload["integration_contract"]["hosted_model_calls"])
        self.assertFalse(payload["integration_contract"]["credentials_required"])
        self.assertEqual(payload["no_input_contract"]["flag"], "--no-input")
        self.assertEqual(payload["no_input_contract"]["agent_env"], "KIT_AGENT=1")
        self.assertIn("status", payload["safe_commands"])
        self.assertIn("command-map", payload["safe_commands"])
        self.assertIn("start", payload["target_write_commands"])
        self.assertIn("setup", payload["target_write_commands"])
        self.assertIn("update", payload["target_write_commands"])
        self.assertIn("feedback", payload["sidecar_write_commands"])
        schema_names = {schema["name"] for schema in payload["schemas"]}
        self.assertIn("command_map_payload", schema_names)
        self.assertIn("feedback_payload", schema_names)
        self.assertEqual(payload["journey_contract"]["front_door_command"], "kit start --json")
        self.assertIn("repo_role", payload["journey_contract"]["stable_start_fields"])
        self.assertIn("local_update", payload["journey_contract"]["stable_start_fields"])
        route_rules = {rule["route"]: rule["use_when"] for rule in payload["journey_contract"]["route_rules"]}
        self.assertIn("kit start --no-update --json", route_rules)
        self.assertIn("make agent-start", route_rules)
        self.assertIn("startup packet", route_rules["make agent-start"])
        self.assertIn("kit agent-context --json", route_rules)
        self.assertIn("command-map metadata", route_rules["kit agent-context --json"])
        self.assertEqual(payload["parser_consistency"]["status"], "passed")

    def test_agent_tool_manifest_text_points_to_json_contract(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "agent-tool-manifest"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("kit agent tool manifest", result.stdout)
        self.assertIn(" - source: kit command-map --json", result.stdout)
        self.assertIn(" - safe commands:", result.stdout)
        self.assertIn(" - target-write commands:", result.stdout)
        self.assertIn(" - journey front door: kit start --json", result.stdout)
        self.assertIn(" - json: kit agent-tool-manifest --json", result.stdout)

    def test_sidecar_init_creates_external_state_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "sidecar-init", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "sidecar-init")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertTrue(payload["sidecar_state"]["available"])
            self.assertTrue(Path(payload["sidecar_state"]["paths"]["runs_dir"]).is_dir())
            self.assertTrue(Path(payload["sidecar_state"]["paths"]["receipts_dir"]).is_dir())
            self.assertTrue(Path(payload["sidecar_state"]["paths"]["review_artifacts_dir"]).is_dir())
            self.assertTrue(Path(payload["sidecar_state"]["paths"]["docs_patch_proposals_dir"]).is_dir())
            self.assertTrue(Path(payload["sidecar_state"]["paths"]["task_packets_dir"]).is_dir())
            self.assertTrue(Path(payload["sidecar_state"]["paths"]["feedback_dir"]).is_dir())
            self.assertTrue(Path(payload["sidecar_state"]["paths"]["quarantine_dir"]).is_dir())
            status_path = Path(payload["sidecar_state"]["paths"]["status_json"])
            self.assertTrue(status_path.exists())
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())

    def test_agent_self_heal_preview_reports_actions_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            task_dir = target / ".agent-workflows" / "tasks"
            task_dir.mkdir(parents=True)
            (task_dir / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")
            stale_metadata = task_dir / "agw-096.json"
            stale_metadata.write_text(
                json.dumps({"task_id": "AGW-096", "status": "done", "worktree": str(Path(tmp) / "missing")}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [str(CLI), "agent-self-heal", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "preview")
            self.assertFalse(payload["apply"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertTrue(any(action["action"] == "sidecar-init" for action in payload["actions"]))
            self.assertTrue(any(action["action"] == "quarantine-stale-task-metadata" for action in payload["actions"]))
            self.assertTrue(stale_metadata.exists())
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_agent_self_heal_apply_writes_sidecar_receipt_without_target_writes_when_sidecar_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "agent-self-heal", "--repo", str(target), "--apply", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "applied")
            self.assertTrue(payload["apply"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertTrue(any(action["action"] == "sidecar-init" for action in payload["applied_actions"]))
            receipt_path = Path(payload["receipt"]["path"])
            self.assertTrue(receipt_path.exists())
            saved = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertIn("before", saved)
            self.assertIn("after", saved)
            self.assertFalse(saved["target_repo_writes"]["performed"])
            self.assertTrue(saved["sidecar_writes"]["performed"])

    def test_agent_self_heal_apply_quarantines_stale_terminal_task_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            task_dir = target / ".agent-workflows" / "tasks"
            task_dir.mkdir(parents=True)
            (task_dir / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")
            stale_metadata = task_dir / "agw-096.json"
            stale_metadata.write_text(
                json.dumps({"task_id": "AGW-096", "status": "blocked", "worktree": str(Path(tmp) / "missing")}),
                encoding="utf-8",
            )

            result = subprocess.run(
                [str(CLI), "agent-self-heal", "--repo", str(target), "--apply", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["target_repo_writes"]["paths"], [".agent-workflows/tasks/agw-096.json"])
            self.assertFalse(stale_metadata.exists())
            moved = [action for action in payload["applied_actions"] if action["action"] == "quarantine-stale-task-metadata"]
            self.assertEqual(len(moved), 1)
            quarantine_path = Path(moved[0]["quarantine_path"])
            self.assertTrue(quarantine_path.exists())
            self.assertEqual(json.loads(quarantine_path.read_text(encoding="utf-8"))["task_id"], "AGW-096")
            saved = json.loads(Path(payload["receipt"]["path"]).read_text(encoding="utf-8"))
            self.assertEqual(saved["target_repo_writes"]["paths"], [".agent-workflows/tasks/agw-096.json"])
            self.assertTrue(any("quarantine" in path for path in saved["sidecar_writes"]["paths"]))

    def test_agent_self_heal_apply_refuses_unrelated_tracked_source_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            (target / "README.md").write_text("# Dirty source\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "agent-self-heal", "--repo", str(target), "--apply", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertIn("Tracked source changes are outside guarded self-heal scope.", payload["blockers"])
            self.assertEqual(payload["plan"]["blocked_tracked_changes"][0]["path"], "README.md")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_agent_self_heal_apply_allows_exact_operator_scoped_generated_tracked_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            task_dir = target / ".agent-workflows" / "tasks"
            task_dir.mkdir(parents=True)
            tracked_path = task_dir / ".gitignore"
            tracked_path.write_text("*\n!.gitignore\n", encoding="utf-8")
            subprocess.run(["git", "add", ".agent-workflows/tasks/.gitignore"], cwd=target, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Track task ignore file",
                ],
                cwd=target,
                check=True,
            )
            tracked_path.write_text("*\n!.gitignore\n# local generated-state note\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "agent-self-heal",
                    "--repo",
                    str(target),
                    "--apply",
                    "--allow-path",
                    ".agent-workflows/tasks/.gitignore",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "applied")
            self.assertEqual(payload["plan"]["blocked_tracked_changes"], [])
            self.assertEqual(payload["plan"]["allowed_tracked_changes"][0]["path"], ".agent-workflows/tasks/.gitignore")
            self.assertTrue(Path(payload["receipt"]["path"]).exists())
            self.assertIn("# local generated-state note", tracked_path.read_text(encoding="utf-8"))

    def test_agent_self_heal_reports_unrecognized_untracked_files_without_deleting(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"
            note = target / "notes.txt"
            note.write_text("keep me\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "agent-self-heal", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["plan"]["unrecognized_untracked"][0]["path"], "notes.txt")
            self.assertIn(
                "Unrecognized untracked files are outside generated-state allowlist; self-heal will not delete them.",
                payload["warnings"],
            )
            self.assertTrue(note.exists())

    def test_orient_write_sidecar_writes_run_artifacts_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "orient", "--repo", str(target), "--write-sidecar", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            run_dir = Path(payload["state"]["sidecar_run_dir"])
            self.assertTrue((run_dir / "session-start.json").exists())
            self.assertTrue((run_dir / "agent-brief.md").exists())
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())

    def test_task_packet_write_sidecar_writes_packet_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [
                    str(CLI),
                    "task-packet",
                    "--repo",
                    str(target),
                    "--task-id",
                    "AGW-080",
                    "--title",
                    "Sidecar-backed workflow storage",
                    "--problem",
                    "Agent artifacts should stay outside target repos.",
                    "--write-sidecar",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            packet_path = Path(payload["sidecar_state"]["paths"]["task_packets_dir"]) / "AGW-080.json"
            self.assertTrue(packet_path.exists())
            saved = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["task"]["id"], "AGW-080")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertFalse((target / ".agent-workflows").exists())

    def test_review_plan_write_sidecar_writes_review_artifact_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "review-plan", "--repo", str(target), "--write-sidecar", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            artifacts_dir = Path(payload["sidecar_state"]["paths"]["review_artifacts_dir"])
            artifacts = list(artifacts_dir.glob("*-review-plan.json"))
            self.assertEqual(len(artifacts), 1)
            saved = json.loads(artifacts[0].read_text(encoding="utf-8"))
            self.assertEqual(saved["command"], "review-plan")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertFalse((target / ".agent-workflows").exists())

    def test_docs_propose_write_sidecar_writes_patch_artifacts_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [
                    str(CLI),
                    "docs-propose",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "cli/new_command.py",
                    "--write-sidecar",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "docs-propose")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertTrue(payload["proposal"]["needed"])
            self.assertEqual(payload["missing_categories"], ["cli"])
            artifacts = payload["proposal"]["artifacts"]
            self.assertTrue(Path(artifacts["json"]).exists())
            self.assertTrue(Path(artifacts["markdown"]).exists())
            self.assertTrue(Path(artifacts["patch"]).exists())
            self.assertIn("git apply", artifacts["apply_command"])
            self.assertIn("Documentation Update Proposal: cli", Path(artifacts["patch"]).read_text(encoding="utf-8"))
            patch_check = subprocess.run(
                ["git", "apply", "--check", artifacts["patch"]],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(patch_check.returncode, 0, patch_check.stderr)
            self.assertIn("README.md", payload["proposal"]["recommendations"][0]["proposal_path"])
            self.assertEqual(
                subprocess.run(["git", "status", "--porcelain"], cwd=target, capture_output=True, text=True).stdout,
                "",
            )
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())

    def test_onboarding_pr_generates_branch_instructions_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [
                    str(CLI),
                    "onboarding-pr",
                    "--repo",
                    str(target),
                    "--preset",
                    "agentic",
                    "--runtime-adapters",
                    "claude-code,github-copilot",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "onboarding-pr")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])
            self.assertFalse(payload["onboarding_pr"]["opens_pull_request"])
            self.assertFalse(payload["onboarding_pr"]["uses_github_api"])
            self.assertEqual(payload["instructions"]["branch"], "codex/kit-onboarding")
            self.assertEqual(payload["install_plan"]["profiles"], ["minimal", "local-agentic", "review-prompts", "test-first", "versioning"])
            self.assertEqual(payload["install_plan"]["runtime_adapters"], ["claude-code", "github-copilot"])
            self.assertIn("--preset agentic", payload["instructions"]["install_command"])
            self.assertIn("--runtime-adapters claude-code,github-copilot", payload["instructions"]["install_command"])
            self.assertIn("AGENTS.md", payload["install_plan"]["expected_paths"])
            self.assertIn(".doc-contract-kit/install.json", payload["install_plan"]["expected_paths"])
            self.assertIn("CLAUDE.md", payload["install_plan"]["expected_paths"])
            self.assertIn(".github/copilot-instructions.md", payload["install_plan"]["expected_paths"])
            commands = "\n".join(step["command"] for step in payload["instructions"]["steps"])
            self.assertNotIn("gh pr create", commands)
            self.assertNotIn("api.github.com", commands)
            self.assertIn("Open a PR manually", payload["instructions"]["pr_instructions"][0])
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())
            self.assertFalse((state_home / "repo-contract-kit").exists())
            self.assertEqual(
                subprocess.run(["git", "status", "--short"], cwd=target, capture_output=True, text=True).stdout,
                "",
            )

    def test_onboarding_pr_write_sidecar_writes_review_bundle_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [
                    str(CLI),
                    "onboarding-pr",
                    "--repo",
                    str(target),
                    "--profile",
                    "minimal",
                    "--branch",
                    "codex/onboarding-test",
                    "--write-sidecar",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            artifacts = payload["onboarding_pr"]["artifacts"]
            json_path = Path(artifacts["json"])
            markdown_path = Path(artifacts["markdown"])
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            saved = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["command"], "onboarding-pr")
            self.assertEqual(saved["instructions"]["branch"], "codex/onboarding-test")
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("# repo-contract-kit Onboarding PR", markdown)
            self.assertIn("git switch -c codex/onboarding-test", markdown)
            self.assertIn("--profile minimal", markdown)
            self.assertFalse((target / ".doc-contract-kit").exists())
            self.assertFalse((target / ".agent-workflows").exists())
            self.assertEqual(
                subprocess.run(["git", "status", "--short"], cwd=target, capture_output=True, text=True).stdout,
                "",
            )

    def test_verify_write_sidecar_records_receipt_even_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [
                    str(CLI),
                    "verify",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "cli/new_command.py",
                    "--write-sidecar",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            receipts_dir = Path(payload["sidecar_state"]["paths"]["receipts_dir"])
            receipts = list(receipts_dir.glob("*-verify.json"))
            self.assertEqual(len(receipts), 1)
            saved = json.loads(receipts[0].read_text(encoding="utf-8"))
            self.assertEqual(saved["result"], "failed")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertFalse((target / ".agent-workflows").exists())

    def test_orient_next_commands_use_executable_entrypoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [str(CLI), "orient", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["next_commands"])
            self.assertTrue(all(command.startswith(f"{CLI} ") for command in payload["next_commands"]))
            self.assertNotIn("python3 ", "\n".join(payload["next_commands"]))

    def test_doc_impact_json_fails_for_cli_change_without_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "doc-impact",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "cli/new_command.py",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "missing-docs")
            self.assertEqual(payload["missing_categories"], ["cli"])

    def test_doc_impact_sarif_reports_missing_docs_for_code_scanning(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "doc-impact",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "cli/new_command.py",
                    "--format",
                    "sarif",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["version"], "2.1.0")
            sarif_results = payload["runs"][0]["results"]
            self.assertEqual(len(sarif_results), 1)
            self.assertEqual(sarif_results[0]["ruleId"], "docs-contract-cli")
            self.assertEqual(
                sarif_results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
                "cli/new_command.py",
            )

    def test_doc_impact_json_passes_when_docs_cover_cli_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "doc-impact",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "cli/new_command.py",
                    "--changed-file",
                    "README.md",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "covered-or-no-impact")
            self.assertEqual(payload["missing_categories"], [])

    def test_goal_check_json_maps_changed_files_to_area_contract_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            config = target / ".agent-workflows" / "area-contracts.json"
            config.parent.mkdir(parents=True)
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_goal": "Keep the repo contract deterministic.",
                        "path_contracts": [
                            {"path": "docs/", "purpose": "Docs", "status": "aligned"},
                            {"path": "scripts/new/", "purpose": "New CLI extensions", "status": "extends"},
                            {"path": "legacy/", "purpose": "Deprecated area", "status": "conflict"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "goal-check",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "docs/guide.md",
                    "--changed-file",
                    "scripts/new/tool.py",
                    "--changed-file",
                    "legacy/old.py",
                    "--changed-file",
                    "src/app.py",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "goal-check")
            self.assertEqual(payload["config"]["repo_goal"], "Keep the repo contract deterministic.")
            states = {item["path"]: item["state"] for item in payload["files"]}
            self.assertEqual(states["docs/guide.md"], "aligned")
            self.assertEqual(states["scripts/new/tool.py"], "extends")
            self.assertEqual(states["legacy/old.py"], "conflict")
            self.assertEqual(states["src/app.py"], "unknown")
            self.assertEqual(payload["summary"]["aligned"], 1)
            self.assertEqual(payload["summary"]["extends"], 1)
            self.assertEqual(payload["summary"]["conflict"], 1)
            self.assertEqual(payload["summary"]["unknown"], 1)
            self.assertFalse(payload["target_repo_writes"]["performed"])

    def test_goal_check_text_uses_most_specific_area_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            config = target / ".agent-workflows" / "area-contracts.json"
            config.parent.mkdir(parents=True)
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_goal": "Prefer specific contracts.",
                        "path_contracts": [
                            {"path": "scripts/", "purpose": "General scripts", "status": "aligned"},
                            {"path": "scripts/goal_check.py", "purpose": "Goal checker", "status": "extends"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    str(CLI),
                    "goal-check",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "scripts/goal_check.py",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Goal check:", result.stdout)
            self.assertIn("scripts/goal_check.py: extends", result.stdout)
            self.assertIn("Goal checker", result.stdout)

    def test_task_packet_emits_machine_readable_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            config = target / ".agent-workflows" / "area-contracts.json"
            config.parent.mkdir(parents=True)
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_goal": "Ship installed CLI behavior.",
                        "path_contracts": [
                            {
                                "path": "scripts/",
                                "purpose": "Installed command scripts.",
                                "source": "docs/harness-engineering.md",
                                "status": "extends",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "task-packet",
                    "--repo",
                    str(target),
                    "--task-id",
                    "AGW-075",
                    "--title",
                    "Add AI-first CLI",
                    "--problem",
                    "Agents need a deterministic CLI entrypoint.",
                    "--priority",
                    "P0",
                    "--source-reference",
                    "AGW-075",
                    "--story-type",
                    "job-to-be-done",
                    "--story-actor",
                    "release operator",
                    "--story-need",
                    "Prepare a deterministic implementation handoff.",
                    "--story-outcome",
                    "The CLI scaffold carries executable task context.",
                    "--story-acceptance-summary",
                    "The packet records story context before implementation starts.",
                    "--scope",
                    "scripts/repo_contract_kit.py",
                    "--docs-impact",
                    "yes",
                    "--docs-surface",
                    "docs/cli-reference.md",
                    "--release-metadata",
                    "CHANGELOG.md",
                    "--generated-doc",
                    "docs/cli-reference.md",
                    "--contract-reference",
                    "workflows/schemas/task-packet.schema.json",
                    "--docs-validation-command",
                    "make docs-freshness",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["task"]["id"], "AGW-075")
            self.assertEqual(payload["task"]["priority"], "P0")
            self.assertEqual(
                payload["context"]["non_goals"],
                ["Do not expand beyond the stated task packet scope."],
            )
            self.assertEqual(
                payload["story"],
                {
                    "type": "job-to-be-done",
                    "actor": "release operator",
                    "need": "Prepare a deterministic implementation handoff.",
                    "outcome": "The CLI scaffold carries executable task context.",
                    "acceptance_summary": "The packet records story context before implementation starts.",
                    "source": "AGW-075",
                },
            )
            self.assertEqual(payload["scope"]["allowed_files"], ["scripts/repo_contract_kit.py"])
            self.assertEqual(payload["docs_impact"]["expected"], "yes")
            self.assertEqual(payload["docs_impact"]["documentation_surfaces"], ["docs/cli-reference.md"])
            self.assertEqual(payload["docs_impact"]["release_metadata"], ["CHANGELOG.md"])
            self.assertEqual(payload["docs_impact"]["generated_docs"], ["docs/cli-reference.md"])
            self.assertEqual(payload["docs_impact"]["contract_references"], ["workflows/schemas/task-packet.schema.json"])
            self.assertEqual(payload["docs_impact"]["verification_commands"], ["make docs-freshness"])
            self.assertEqual(payload["goal_alignment"]["repo_goal"], "Ship installed CLI behavior.")
            self.assertEqual(payload["goal_alignment"]["alignment_decision"], "adaptation-needed")
            self.assertTrue(payload["goal_alignment"]["adaptation_needed"])
            self.assertEqual(payload["goal_alignment"]["area_contracts"][0]["status"], "aligned")
            self.assertIn("extends", payload["goal_alignment"]["area_contracts"][0]["notes"])
            self.assertIn("closeout_requirements", payload)
            self.assertEqual(payload["closeout_requirements"]["lifecycle_action"]["action"], "finish")

    def test_goal_check_unknown_policy_block_fails_unknown_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            config = target / ".agent-workflows" / "area-contracts.json"
            config.parent.mkdir(parents=True)
            config.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "repo_goal": "Require declared areas.",
                        "unknown_policy": "block",
                        "path_contracts": [],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    str(CLI),
                    "goal-check",
                    "--repo",
                    str(target),
                    "--changed-file",
                    "src/app.py",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "unknown")
            self.assertEqual(payload["summary"]["unknown"], 1)

    def test_backlog_status_reads_csv_source_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            backlog = target / "research" / "agentic-workflow-review" / "backlog.csv"
            backlog.parent.mkdir(parents=True)
            backlog.write_text(
                "id,priority,repo,theme,item,status,completion_note\n"
                "AGW-001,P1,repo-contract-kit,done,Finished item,done,complete\n"
                "AGW-002,P0,repo-contract-kit,next,Next item,open,\n",
                encoding="utf-8",
            )
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "backlog-status", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["selected_source"], "research/agentic-workflow-review/backlog.csv")
            self.assertEqual(payload["counts"]["open"], 1)
            self.assertEqual(payload["counts"]["done"], 1)
            self.assertEqual(payload["next_open_item"]["id"], "AGW-002")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse((state_home / "repo-contract-kit").exists())

    def test_backlog_check_fails_for_markdown_checkbox_without_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "docs").mkdir()
            (target / "docs" / "backlog.md").write_text("- [ ] Missing stable id\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "backlog-check", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "backlog-check")
            self.assertIn("missing-ids", payload["check"]["errors"])

    def test_agent_next_recommends_top_backlog_item_and_packet_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "docs").mkdir()
            (target / "docs" / "backlog.md").write_text(
                "- [ ] AGW-010: P2 Later item\n"
                "- [ ] AGW-009: P1 Earlier item\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [str(CLI), "agent-next", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["selected_item"]["id"], "AGW-009")
            self.assertIn("make agent-task-packet-from-backlog BACKLOG_ID=AGW-009", payload["recommended_commands"])

    def test_task_packet_from_backlog_prefills_selected_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "docs").mkdir()
            (target / "docs" / "backlog.md").write_text("- [ ] AGW-010: P1 Implement backlog handoff\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "agent-task-packet-from-backlog",
                    "--repo",
                    str(target),
                    "--backlog-id",
                    "AGW-010",
                    "--json",
                    "--approved",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "agent-task-packet-from-backlog")
            self.assertEqual(payload["task"]["id"], "AGW-010")
            self.assertEqual(payload["task"]["priority"], "P1")
            self.assertEqual(payload["backlog_item"]["source_path"], "docs/backlog.md")
            self.assertEqual(
                payload["context"]["non_goals"],
                ["Do not expand beyond the stated task packet scope."],
            )
            self.assertEqual(payload["story"]["type"], "operator-story")
            self.assertEqual(payload["story"]["actor"], "implementation agent")
            self.assertEqual(payload["story"]["need"], payload["task"]["title"])
            self.assertEqual(payload["story"]["outcome"], payload["task"]["title"])
            self.assertEqual(payload["story"]["source"], payload["task"]["source"]["reference"])
            self.assertIn("README.md", payload["docs_impact"]["documentation_surfaces"])
            self.assertIn("CHANGELOG.md", payload["docs_impact"]["release_metadata"])
            self.assertIn("docs/cli-reference.md", payload["docs_impact"]["generated_docs"])
            self.assertTrue(
                any("schema" in reference for reference in payload["docs_impact"]["contract_references"])
            )
            self.assertIn("make docs-freshness", payload["docs_impact"]["verification_commands"])

    def test_automation_handoff_writes_patch_for_allowed_worktree_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            worktree = Path(tmp) / "target-auto"
            add_git_worktree(target, worktree)
            backlog = worktree / "research" / "agentic-workflow-review" / "backlog.csv"
            backlog.parent.mkdir(parents=True)
            backlog.write_text(
                "id,priority,repo,theme,item,status,completion_note\n"
                "AGW-082,P0,repo-contract-kit,automation,Preserve automation backlog edits,open,\n",
                encoding="utf-8",
            )
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "automation-handoff", "--repo", str(worktree), "--label", "AGW-082", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "automation-handoff")
            self.assertEqual(payload["result"], "passed")
            self.assertTrue(payload["worktree"]["linked_worktree"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(payload["sidecar_writes"]["performed"])
            self.assertEqual(payload["disallowed_changed_files"], [])
            patch_path = Path(payload["patch"]["path"])
            receipt_path = Path(payload["receipt"]["path"])
            self.assertTrue(patch_path.exists())
            self.assertTrue(receipt_path.exists())
            self.assertIn("AGW-082", patch_path.read_text(encoding="utf-8"))
            saved = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["result"], "passed")
            self.assertEqual(subprocess.run(["git", "status", "--short"], cwd=target, capture_output=True, text=True).stdout, "")

    def test_automation_handoff_blocks_primary_checkout_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            backlog = target / "research" / "agentic-workflow-review" / "backlog.csv"
            backlog.parent.mkdir(parents=True)
            backlog.write_text("id,priority,repo,theme,item,status,completion_note\n", encoding="utf-8")
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "automation-handoff", "--repo", str(target), "--label", "nightly", "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertFalse(payload["worktree"]["linked_worktree"])
            self.assertEqual(payload["attribution"]["automation_id"], "nightly")
            self.assertEqual(payload["attribution"]["source"], "receipt")
            self.assertIn("Automation handoff must run from a linked worktree, not the primary checkout.", payload["blockers"])
            self.assertIsNone(payload["patch"])
            self.assertTrue(Path(payload["receipt"]["path"]).exists())

            preflight = subprocess.run(
                [str(CLI), "agent-preflight", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(preflight.returncode, 0, preflight.stderr)
            preflight_payload = json.loads(preflight.stdout)
            self.assertIn("Latest automation handoff receipt was blocked.", preflight_payload["blockers"])
            receipt_detail = next(item for item in preflight_payload["blocker_details"] if item["code"] == "automation_handoff_blocked")
            self.assertEqual(receipt_detail["attribution"]["automation_id"], "nightly")
            self.assertEqual(receipt_detail["attribution"]["source"], "receipt")
            self.assertEqual(receipt_detail["attribution"]["latest_receipt"]["path"], payload["receipt"]["path"])

    def test_automation_handoff_blocks_disallowed_worktree_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            worktree = Path(tmp) / "target-auto"
            add_git_worktree(target, worktree)
            source = worktree / "src" / "app.py"
            source.parent.mkdir()
            source.write_text("print('not backlog')\n", encoding="utf-8")
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [str(CLI), "automation-handoff", "--repo", str(worktree), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertEqual(payload["disallowed_changed_files"], ["src/app.py"])
            self.assertIn("Changed files outside automation handoff scope.", payload["blockers"])
            self.assertIsNone(payload["patch"])

    def test_automation_handoff_blocks_dirty_original_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            worktree = Path(tmp) / "target-auto"
            add_git_worktree(target, worktree)
            backlog = worktree / "research" / "agentic-workflow-review" / "backlog.csv"
            backlog.parent.mkdir(parents=True)
            backlog.write_text("id,priority,repo,theme,item,status,completion_note\n", encoding="utf-8")
            (target / "README.md").write_text("# Dirty original\n", encoding="utf-8")
            state_home = Path(tmp) / "state"

            result = subprocess.run(
                [
                    str(CLI),
                    "automation-handoff",
                    "--repo",
                    str(worktree),
                    "--original-root",
                    str(target),
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertTrue(payload["original_checkout"]["dirty"])
            self.assertIn("Original checkout is dirty; automation handoff must leave it clean.", payload["blockers"])
            self.assertIsNone(payload["patch"])

    def test_automation_handoff_allows_dirty_original_matching_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# Pre-existing dirty original\n", encoding="utf-8")
            state_home = Path(tmp) / "state"

            baseline_result = subprocess.run(
                [
                    str(CLI),
                    "automation-handoff",
                    "--repo",
                    str(target),
                    "--original-root",
                    str(target),
                    "--capture-original-baseline",
                    "--label",
                    "baseline",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(baseline_result.returncode, 0, baseline_result.stderr)
            baseline_payload = json.loads(baseline_result.stdout)
            self.assertTrue(baseline_payload["original_checkout"]["dirty"])
            baseline_path = baseline_payload["receipt"]["path"]

            worktree = Path(tmp) / "target-auto"
            add_git_worktree(target, worktree)
            backlog = worktree / "research" / "agentic-workflow-review" / "backlog.csv"
            backlog.parent.mkdir(parents=True)
            backlog.write_text("id,priority,repo,theme,item,status,completion_note\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "automation-handoff",
                    "--repo",
                    str(worktree),
                    "--original-root",
                    str(target),
                    "--original-baseline",
                    baseline_path,
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "passed")
            self.assertTrue(payload["original_checkout"]["dirty"])
            self.assertFalse(payload["original_checkout"]["changed_since_baseline"])
            self.assertEqual(payload["original_checkout"]["baseline"]["path"], baseline_path)
            self.assertTrue(Path(payload["receipt"]["path"]).exists())
            self.assertTrue(Path(payload["patch"]["path"]).exists())

    def test_automation_handoff_blocks_original_changes_since_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            baseline_result = subprocess.run(
                [
                    str(CLI),
                    "automation-handoff",
                    "--repo",
                    str(target),
                    "--original-root",
                    str(target),
                    "--capture-original-baseline",
                    "--label",
                    "baseline",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(baseline_result.returncode, 0, baseline_result.stderr)
            baseline_path = json.loads(baseline_result.stdout)["receipt"]["path"]
            (target / "README.md").write_text("# Mutated original\n", encoding="utf-8")

            worktree = Path(tmp) / "target-auto"
            add_git_worktree(target, worktree)
            backlog = worktree / "research" / "agentic-workflow-review" / "backlog.csv"
            backlog.parent.mkdir(parents=True)
            backlog.write_text("id,priority,repo,theme,item,status,completion_note\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "automation-handoff",
                    "--repo",
                    str(worktree),
                    "--original-root",
                    str(target),
                    "--original-baseline",
                    baseline_path,
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "blocked")
            self.assertTrue(payload["original_checkout"]["changed_since_baseline"])
            self.assertIn("README.md", payload["original_checkout"]["baseline_comparison"]["new_changed_files"])
            self.assertIn("Original checkout changed since baseline; automation handoff must leave original checkout untouched.", payload["blockers"])
            self.assertIsNone(payload["patch"])
            self.assertTrue(Path(payload["receipt"]["path"]).exists())

    def test_automation_handoff_allows_explicit_original_baseline_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            baseline_result = subprocess.run(
                [
                    str(CLI),
                    "automation-handoff",
                    "--repo",
                    str(target),
                    "--original-root",
                    str(target),
                    "--capture-original-baseline",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(baseline_result.returncode, 0, baseline_result.stderr)
            baseline_path = json.loads(baseline_result.stdout)["receipt"]["path"]
            (target / "README.md").write_text("# Accepted original drift\n", encoding="utf-8")

            worktree = Path(tmp) / "target-auto"
            add_git_worktree(target, worktree)
            backlog = worktree / "research" / "agentic-workflow-review" / "backlog.csv"
            backlog.parent.mkdir(parents=True)
            backlog.write_text("id,priority,repo,theme,item,status,completion_note\n", encoding="utf-8")

            result = subprocess.run(
                [
                    str(CLI),
                    "automation-handoff",
                    "--repo",
                    str(worktree),
                    "--original-root",
                    str(target),
                    "--original-baseline",
                    baseline_path,
                    "--allow-original-baseline-drift",
                    "--json",
                ],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "passed")
            self.assertTrue(payload["original_checkout"]["changed_since_baseline"])
            self.assertTrue(Path(payload["patch"]["path"]).exists())

    def test_install_wrapper_is_explicit_and_reports_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "install",
                    "--repo",
                    str(target),
                    "--preset",
                    "minimal",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["returncode"], 0)
            self.assertTrue((target / ".doc-contract-kit" / "install.json").exists())

    def test_target_add_defaults_to_current_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "target",
                    "add",
                    "--preset",
                    "minimal",
                    "--json",
                ],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["returncode"], 0)
            self.assertTrue((target / ".doc-contract-kit" / "install.json").exists())

    def test_target_status_alias_reports_install_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "target", "add", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "status")
            self.assertTrue(payload["install"]["installed"])

    def test_installed_kit_status_uses_workflow_snapshot_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "target", "add", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            result = subprocess.run(
                ["make", "kit-status"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("workflow prompt snapshot:", result.stdout)
            self.assertNotIn("agent-workflow-kit snapshot:", result.stdout)

    def test_workflow_source_check_passes_for_in_repo_source(self):
        result = subprocess.run(
            ["make", "workflow-source-check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("workflow source check: current", result.stdout)

    def test_target_help_lists_doctor(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "target", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("add", "status", "list", "import", "doctor", "repair-source-clone", "update", "update-all", "prune-missing"):
            self.assertIn(command, result.stdout)

    def test_target_doctor_alias_reports_preflight_without_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            (target / "README.md").write_text("# dirty\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "doctor", "--repo", str(target), "--strict", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "target-doctor")
            self.assertEqual(payload["result"], "blocked")
            self.assertIn("Current checkout has uncommitted changes.", payload["blockers"])
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertFalse(payload["sidecar_writes"]["performed"])

    def test_target_update_applies_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "target", "add", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "update", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("--apply", payload["command"])
            self.assertTrue(payload["target_repo_writes"]["performed"])

    def test_target_update_dry_run_does_not_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "target", "add", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "update", "--repo", str(target), "--dry-run", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("--dry-run", payload["command"])
            self.assertNotIn("--apply", payload["command"])
            self.assertFalse(payload["target_repo_writes"]["performed"])

    def test_update_json_applies_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")

            result = subprocess.run(
                [str(CLI), "update", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("--apply", payload["command"])
            self.assertTrue(payload["target_repo_writes"]["performed"])

    def test_update_json_dry_run_does_not_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")

            result = subprocess.run(
                [str(CLI), "update", "--repo", str(target), "--dry-run", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("--dry-run", payload["command"])
            self.assertNotIn("--apply", payload["command"])
            self.assertFalse(payload["target_repo_writes"]["performed"])

    def test_target_repair_source_clone_previews_without_removing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            nested_source = target / "repo-contract-kit"
            nested_source.mkdir()
            init_repo_contract_source(nested_source)

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "repair-source-clone", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "target repair-source-clone")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["nested_source_clones"][0]["path"], "repo-contract-kit")
            self.assertTrue(nested_source.exists())

    def test_target_repair_source_clone_apply_removes_clean_nested_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            nested_source = target / "repo-contract-kit"
            nested_source.mkdir()
            init_repo_contract_source(nested_source)

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "repair-source-clone", "--repo", str(target), "--apply", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["applied_paths"], ["repo-contract-kit"])
            self.assertFalse(nested_source.exists())

    def test_target_repair_source_clone_refuses_root_source_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp) / "repo-contract-kit"
            source_root.mkdir()
            init_repo_contract_source(source_root)

            result = subprocess.run(
                [sys.executable, str(CLI), "target", "repair-source-clone", "--repo", str(source_root), "--apply", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["blockers"][0]["code"], "root-source-checkout")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue((source_root / "scripts" / "repo_contract_kit.py").exists())

    def test_global_install_script_skips_workflow_source_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            data_home = Path(tmp) / "data"
            env = os.environ.copy()
            env["XDG_DATA_HOME"] = str(data_home)
            result = subprocess.run(
                [
                    "sh",
                    str(ROOT / "install.sh"),
                    "--source",
                    str(ROOT),
                    "--bin-dir",
                    str(bin_dir),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("agent-workflow-kit source", result.stdout)
            self.assertNotIn("workflow source:", result.stdout)
            launcher = bin_dir / "kit"
            self.assertTrue(launcher.exists())

            self_status_text = subprocess.run(
                [str(launcher), "self", "status"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(self_status_text.returncode, 0, self_status_text.stderr)
            self.assertIn("kit global tool:", self_status_text.stdout)
            status_without_dirty_entries = "\n".join(
                line for line in self_status_text.stdout.splitlines() if not line.startswith("   ")
            )
            self.assertNotIn("agent-workflow-kit", status_without_dirty_entries)
            self.assertNotIn("optional workflow source checkout", self_status_text.stdout)

            self_status = subprocess.run(
                [str(launcher), "self", "status", "--json"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(self_status.returncode, 0, self_status.stderr)
            payload = json.loads(self_status.stdout)
            self.assertEqual(payload["workflow_source"]["root"], str((data_home / "agent-workflow-kit" / "source").resolve()))
            self.assertFalse(payload["workflow_source"]["exists"])
            self.assertFalse(payload["workflow_source"]["is_git_checkout"])

    def test_global_install_script_writes_launcher_for_target_add(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            workflow_source = Path(tmp) / "agent-workflow-kit"
            (workflow_source / "workflows").mkdir(parents=True)
            (workflow_source / "workflows" / "manifest.json").write_text("{}\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=workflow_source, check=True)
            commit_all(workflow_source, "Initial workflow source")
            result = subprocess.run(
                [
                    "sh",
                    str(ROOT / "install.sh"),
                    "--source",
                    str(ROOT),
                    "--workflow-source",
                    str(workflow_source),
                    "--bin-dir",
                    str(bin_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"workflow source: {workflow_source.resolve()}", result.stdout)
            self.assertNotIn("agent-workflow-kit source", result.stdout)
            launcher = bin_dir / "kit"
            self.assertTrue(launcher.exists())

            version = subprocess.run(
                [str(launcher), "version", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(version.returncode, 0, version.stderr)
            self.assertEqual(json.loads(version.stdout)["command"], "version")

            self_status = subprocess.run(
                [str(launcher), "self", "status", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(self_status.returncode, 0, self_status.stderr)
            self_payload = json.loads(self_status.stdout)
            self.assertEqual(self_payload["workflow_source"]["root"], str(workflow_source.resolve()))
            self.assertTrue(self_payload["workflow_source"]["is_git_checkout"])

            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            add_target = subprocess.run(
                [str(launcher), "target", "add", "--preset", "minimal", "--json"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(add_target.returncode, 0, add_target.stderr)
            self.assertTrue((target / ".doc-contract-kit" / "install.json").exists())

    def test_global_install_script_honors_new_command_env_and_old_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            env = os.environ.copy()
            env["KIT_COMMAND"] = "project-kit"
            result = subprocess.run(
                [
                    "sh",
                    str(ROOT / "install.sh"),
                    "--source",
                    str(ROOT),
                    "--bin-dir",
                    str(bin_dir),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((bin_dir / "project-kit").exists())
            self.assertIn("Installed project-kit", result.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            env = os.environ.copy()
            env.pop("KIT_COMMAND", None)
            env["REPO_CONTRACT_KIT_COMMAND"] = "legacy-kit"
            result = subprocess.run(
                [
                    "sh",
                    str(ROOT / "install.sh"),
                    "--source",
                    str(ROOT),
                    "--bin-dir",
                    str(bin_dir),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((bin_dir / "legacy-kit").exists())
            self.assertIn("Installed legacy-kit", result.stdout)

    def test_global_install_script_refuses_non_owned_default_kit_launcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            launcher = bin_dir / "kit"
            launcher.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
            launcher.chmod(0o755)

            result = subprocess.run(
                [
                    "sh",
                    str(ROOT / "install.sh"),
                    "--source",
                    str(ROOT),
                    "--bin-dir",
                    str(bin_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Existing launcher is not owned by repo-contract-kit", result.stderr)
            self.assertIn("--command-name NAME", result.stderr)

    def test_install_wrapper_forwards_runtime_adapter_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "install",
                    "--repo",
                    str(target),
                    "--preset",
                    "minimal",
                    "--runtime-adapter",
                    "claude-code",
                    "--runtime-adapter",
                    "github-copilot",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["returncode"], 0)
            self.assertTrue((target / "CLAUDE.md").exists())
            self.assertTrue((target / ".github" / "copilot-instructions.md").exists())

            status = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            status_payload = json.loads(status.stdout)
            self.assertEqual(status_payload["install"]["runtime_adapters"], ["claude-code", "github-copilot"])

    def test_install_wrapper_forwards_private_context_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "install",
                    "--repo",
                    str(target),
                    "--profile",
                    "private-context",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["returncode"], 0)
            self.assertTrue((target / ".agent-context" / "README.md").exists())
            self.assertTrue((target / ".agent-context" / ".gitignore").exists())

            status = subprocess.run(
                [sys.executable, str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            status_payload = json.loads(status.stdout)
            self.assertEqual(status_payload["install"]["profiles"], ["private-context"])
            self.assertNotIn("agentic", status_payload["install"]["profiles"])

    def test_update_dry_run_text_renders_compact_summary_without_raw_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")

            result = subprocess.run(
                [str(CLI), "update", "--repo", str(target), "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.startswith("kit update summary for "))
            self.assertIn(" - mode: dry-run", result.stdout)
            self.assertIn(" - blockers: 0", result.stdout)
            self.assertIn(" - conflicts: 0", result.stdout)
            self.assertIn(" - direct updates:", result.stdout)
            self.assertIn(" - target-owned files:", result.stdout)
            self.assertIn(" - proposal paths: 0", result.stdout)
            self.assertIn(" - target writes: false", result.stdout)
            self.assertIn(" - sidecar writes: false", result.stdout)
            self.assertIn(" - next commands:", result.stdout)
            self.assertNotIn('"schema_version"', result.stdout)

    def test_update_pretty_style_adds_ansi_without_changing_summary_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")
            env = os.environ.copy()
            env.pop("NO_COLOR", None)

            result = subprocess.run(
                [str(CLI), "update", "--style", "pretty", "--repo", str(target), "--dry-run"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("\x1b[", result.stdout)
            self.assertIn("kit update summary for ", result.stdout)
            self.assertIn(" - mode: dry-run", result.stdout)
            self.assertIn(" - target writes: false", result.stdout)
            self.assertNotIn('"schema_version"', result.stdout)

    def test_update_text_reports_conflicts_and_proposal_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")
            agents = target / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8") + "\nLocal custom instruction.\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "update", "--repo", str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.startswith("kit update summary for "))
            self.assertIn(" - mode: apply", result.stdout)
            self.assertIn(" - conflicts: 1", result.stdout)
            self.assertIn(" - proposal paths:", result.stdout)
            self.assertIn(".doc-contract-kit/updates/", result.stdout)
            self.assertIn("proposed/AGENTS.md", result.stdout)
            self.assertIn(" - target writes: true", result.stdout)
            self.assertIn(" - sidecar writes: false", result.stdout)
            self.assertIn(" - next commands:", result.stdout)
            self.assertIn("kit doctor --repo", result.stdout)

    def test_update_verbose_text_keeps_raw_script_detail_after_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(target, "Install repo-contract-kit")

            result = subprocess.run(
                [str(CLI), "update", "--repo", str(target), "--verbose"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.startswith("kit update summary for "))
            self.assertIn("Details:", result.stdout)
            self.assertIn("Update complete.", result.stdout)

    def test_update_dry_run_reports_no_target_repo_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "update",
                    "--repo",
                    str(target),
                    "--dry-run",
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["target_repo_writes"]["paths"], [])
            self.assertFalse((target / ".doc-contract-kit").exists())

    def test_update_plan_reports_plain_repo_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)

            result = subprocess.run(
                [str(CLI), "update-plan", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "update-plan")
            self.assertEqual(payload["detected_state"]["kind"], "not_installed")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["sidecar_state"]["repo"]["root"], str(target.resolve()))
            self.assertEqual(payload["actions"][0]["action"], "install-required")
            self.assertFalse((target / ".doc-contract-kit").exists())

    def test_update_plan_reports_profile_config_migration_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            receipt_path = target / ".doc-contract-kit" / "install.json"
            manifest_path = target / ".doc-contract-kit" / "manifest.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            receipt.pop("profile_config_schema_version", None)
            manifest.pop("profile_config_schema_version", None)
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "update-plan", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["detected_state"]["profile_config_schema"]["status"], "missing")
            self.assertTrue(any(item["action"] == "migrate-profile-config" for item in payload["actions"]))
            self.assertNotIn("profile_config_schema_version", json.loads(receipt_path.read_text(encoding="utf-8")))

    def test_migrate_config_wrapper_applies_metadata_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            agents = target / "AGENTS.md"
            customized = agents.read_text(encoding="utf-8") + "\nLocal note.\n"
            agents.write_text(customized, encoding="utf-8")
            receipt_path = target / ".doc-contract-kit" / "install.json"
            manifest_path = target / ".doc-contract-kit" / "manifest.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            receipt["profile_config_schema_version"] = 0
            receipt["kit_version"] = "0.0.1"
            receipt["source_ref"] = "old-receipt-ref"
            manifest["profile_config_schema_version"] = 0
            manifest["kit_version"] = "0.0.1"
            manifest["source_ref"] = "old-manifest-ref"
            manifest_agents_hash = next(item for item in manifest["files"] if item["path"] == "AGENTS.md")["installed_sha256"]
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "migrate-config", "--repo", str(target), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["target_repo_writes"]["performed"])
            self.assertEqual(agents.read_text(encoding="utf-8"), customized)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["profile_config_schema_version"], 1)
            self.assertEqual(manifest["profile_config_schema_version"], 1)
            self.assertEqual(receipt["kit_version"], "0.0.1")
            self.assertEqual(receipt["source_ref"], "old-receipt-ref")
            self.assertEqual(manifest["kit_version"], "0.0.1")
            self.assertEqual(manifest["source_ref"], "old-manifest-ref")
            self.assertEqual(
                next(item for item in manifest["files"] if item["path"] == "AGENTS.md")["installed_sha256"],
                manifest_agents_hash,
            )

    def test_update_apply_json_includes_report_and_write_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            install = subprocess.run(
                [sys.executable, str(CLI), "install", "--repo", str(target), "--preset", "minimal", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            receipt_path = target / ".doc-contract-kit" / "install.json"
            manifest_path = target / ".doc-contract-kit" / "manifest.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            receipt.pop("profile_config_schema_version", None)
            manifest.pop("profile_config_schema_version", None)
            receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            result = subprocess.run(
                [str(CLI), "update", "--repo", str(target), "--apply", "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["target_repo_writes"]["performed"])
            self.assertIn(".doc-contract-kit/install.json", payload["target_repo_writes"]["paths"])
            self.assertIn(".doc-contract-kit/manifest.json", payload["target_repo_writes"]["paths"])
            self.assertIn("update_report", payload)
            self.assertTrue(payload["update_report"]["actions"])
            self.assertTrue(payload["update_report"]["path"].endswith("update-report.json"))
            self.assertNotEqual(payload["target_repo_writes"]["paths"], [".doc-contract-kit"])

    def test_update_plan_reports_sidecar_only_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_git_repo(target)
            state_home = Path(tmp) / "state"

            status = subprocess.run(
                [str(CLI), "status", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            state_payload = json.loads(status.stdout)["sidecar_state"]
            Path(state_payload["repo_state_dir"]).mkdir(parents=True)

            result = subprocess.run(
                [str(CLI), "update-plan", "--repo", str(target), "--json"],
                cwd=ROOT,
                env={**os.environ, "XDG_STATE_HOME": str(state_home)},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["detected_state"]["kind"], "sidecar_only")
            self.assertTrue(payload["sidecar_state"]["available"])
            self.assertTrue(any(item["code"] == "sidecar_only" for item in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
