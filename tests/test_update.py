import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"
UPDATE = ROOT / "scripts" / "update.py"


def run(cmd, cwd, check=False):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def sha256_text(value: str):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def init_repo(path: Path):
    run(["git", "init", "-q"], path, check=True)
    (path / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    run(["git", "add", "README.md"], path, check=True)
    run(
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
        path,
        check=True,
    )


def install_agentic(repo: Path):
    result = run([sys.executable, str(INSTALL), str(repo), "--preset", "agentic"], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def install_private_context(repo: Path):
    result = run([sys.executable, str(INSTALL), str(repo), "--profile", "private-context"], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def install_node(repo: Path):
    result = run([sys.executable, str(INSTALL), str(repo), "--profile", "node"], ROOT)
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def commit_all(repo: Path, message: str = "Commit kit install"):
    run(["git", "add", "."], repo, check=True)
    run(
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
        repo,
        check=True,
    )


def clone_local_kit(tmp_root: Path):
    kit = tmp_root / "repo-contract-kit"
    run(["git", "clone", "-q", str(ROOT), str(kit)], ROOT, check=True)
    return kit


def manifest_path(repo: Path):
    return repo / ".doc-contract-kit" / "manifest.json"


def receipt_path(repo: Path):
    return repo / ".doc-contract-kit" / "install.json"


def read_manifest(repo: Path):
    return json.loads(manifest_path(repo).read_text(encoding="utf-8"))


def write_manifest(repo: Path, manifest: dict):
    manifest_path(repo).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_receipt(repo: Path):
    return json.loads(receipt_path(repo).read_text(encoding="utf-8"))


def write_receipt(repo: Path, receipt: dict):
    receipt_path(repo).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mark_managed_baseline(repo: Path, rel_path: str, content: str):
    target = repo / rel_path
    target.write_text(content, encoding="utf-8")
    manifest = read_manifest(repo)
    for item in manifest["files"]:
        if item["path"] == rel_path:
            item["installed_sha256"] = sha256_text(content)
            item["managed"] = True
            item["owner"] = "kit"
            break
    write_manifest(repo, manifest)


class UpdateTests(unittest.TestCase):
    def test_default_update_is_plan_only_for_plain_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)

            result = run([sys.executable, str(UPDATE), str(repo), "--plan-json"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["detected_state"]["kind"], "not_installed")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["actions"][0]["action"], "install-required")
            self.assertFalse((repo / ".doc-contract-kit").exists())

    def test_clean_managed_file_updates_automatically(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            mark_managed_baseline(repo, "AGENTS.md", "# Old managed agents\n")
            commit_all(repo)

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), "# Old managed agents\n")
            self.assertIn("# AGENTS.md", (repo / "AGENTS.md").read_text(encoding="utf-8"))
            manifest = read_manifest(repo)
            receipt = json.loads((repo / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["prompt_snapshot"]["name"], "workflow-source")
            self.assertEqual(
                manifest["prompt_snapshot"]["snapshot_sha256"],
                receipt["prompt_snapshot"]["snapshot_sha256"],
            )

    def test_customized_file_preserves_target_and_writes_conflict_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)
            original = (repo / "AGENTS.md").read_text(encoding="utf-8")
            customized = original + "\nLocal custom instruction.\n"
            (repo / "AGENTS.md").write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized)
            reports = sorted((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json"))
            self.assertTrue(reports)
            report = json.loads(reports[-1].read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == "AGENTS.md" for item in report["conflicts"]))
            self.assertTrue(any(item["path"] == "AGENTS.md" for item in report["read_next"]))
            self.assertTrue(any(item["scope"] == "kit" and item["path"].endswith("CHANGELOG.md") for item in report["read_next"]))
            self.assertTrue(any("sidecar-init" in item["command"] for item in report["after_update"]))
            self.assertTrue(any("--write-sidecar" in item["command"] for item in report["after_update"]))
            self.assertTrue(any(".agent-workflows/runs" in item["message"] for item in report["after_update_notes"]))
            report_md = reports[-1].with_suffix(".md")
            report_md_text = report_md.read_text(encoding="utf-8")
            self.assertIn("## Read Next", report_md_text)
            self.assertIn("## After Updating", report_md_text)
            self.assertIn("sidecar-init", report_md_text)
            self.assertIn("--write-sidecar", report_md_text)
            proposed = sorted((repo / ".doc-contract-kit" / "updates").glob("*/proposed/AGENTS.md"))
            self.assertTrue(proposed)

    def test_customized_private_context_example_is_preserved_with_conflict_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_private_context(repo)
            commit_all(repo)
            rel_path = ".agent-context/project-context.example.md"
            target = repo / rel_path
            customized = target.read_text(encoding="utf-8") + "\nLocal safe wording.\n"
            target.write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_text(encoding="utf-8"), customized)
            reports = sorted((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json"))
            self.assertTrue(reports)
            report = json.loads(reports[-1].read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == rel_path for item in report["conflicts"]))
            proposed = sorted((repo / ".doc-contract-kit" / "updates").glob("*/proposed/.agent-context/project-context.example.md"))
            self.assertTrue(proposed)

    def test_customized_stack_profile_doc_is_preserved_with_conflict_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_node(repo)
            commit_all(repo)
            rel_path = "docs/ops/node-stack-profile.md"
            target = repo / rel_path
            customized = target.read_text(encoding="utf-8") + "\nLocal Node policy.\n"
            target.write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_text(encoding="utf-8"), customized)
            reports = sorted((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json"))
            self.assertTrue(reports)
            report = json.loads(reports[-1].read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == rel_path for item in report["conflicts"]))
            proposed = sorted((repo / ".doc-contract-kit" / "updates").glob("*/proposed/docs/ops/node-stack-profile.md"))
            self.assertTrue(proposed)

    def test_missing_managed_file_is_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)
            target = repo / "scripts" / "kit_status.py"
            target.unlink()

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists())

    def test_new_core_script_missing_from_old_manifest_is_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            helper = repo / "scripts" / "_agent_scope.py"
            helper.unlink()
            manifest = read_manifest(repo)
            manifest["files"] = [item for item in manifest["files"] if item.get("path") != "scripts/_agent_scope.py"]
            write_manifest(repo, manifest)
            commit_all(repo)

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(helper.exists())
            files = {item["path"]: item for item in read_manifest(repo)["files"]}
            self.assertTrue(files["scripts/_agent_scope.py"]["managed"])
            self.assertEqual(files["scripts/_agent_scope.py"]["owner"], "kit")

    def test_update_can_add_selected_runtime_adapters_to_existing_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)

            result = run(
                [
                    sys.executable,
                    str(UPDATE),
                    str(repo),
                    "--apply",
                    "--runtime-adapters",
                    "claude-code,github-copilot",
                ],
                ROOT,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((repo / "CLAUDE.md").exists())
            self.assertTrue((repo / ".github" / "copilot-instructions.md").exists())
            self.assertIn("restore: CLAUDE.md", result.stdout)
            self.assertIn("restore: .github/copilot-instructions.md", result.stdout)

            receipt = json.loads((repo / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["runtime_adapters"], ["claude-code", "github-copilot"])

            manifest = read_manifest(repo)
            self.assertEqual(manifest["runtime_adapters"], ["claude-code", "github-copilot"])
            files = {item["path"]: item for item in manifest["files"]}
            self.assertTrue(files["CLAUDE.md"]["managed"])
            self.assertEqual(files["CLAUDE.md"]["runtime_adapter"], "claude-code")
            self.assertTrue(files[".github/copilot-instructions.md"]["managed"])
            self.assertEqual(files[".github/copilot-instructions.md"]["runtime_adapter"], "github-copilot")

    def test_customized_runtime_adapter_is_preserved_with_conflict_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install = run(
                [
                    sys.executable,
                    str(INSTALL),
                    str(repo),
                    "--preset",
                    "agentic",
                    "--runtime-adapter",
                    "claude-code",
                ],
                ROOT,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            commit_all(repo)
            customized = (repo / "CLAUDE.md").read_text(encoding="utf-8") + "\nLocal Claude note.\n"
            (repo / "CLAUDE.md").write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "CLAUDE.md").read_text(encoding="utf-8"), customized)
            reports = sorted((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json"))
            self.assertTrue(reports)
            report = json.loads(reports[-1].read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == "CLAUDE.md" for item in report["conflicts"]))
            proposed = sorted((repo / ".doc-contract-kit" / "updates").glob("*/proposed/CLAUDE.md"))
            self.assertTrue(proposed)

    def test_old_clean_managed_makefile_migrates_to_target_owned_bridge(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            mark_managed_baseline(repo, "Makefile", "# Old managed kit Makefile\n")
            commit_all(repo)

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("migrate-target-owned: Makefile", result.stdout)
            self.assertIn(
                "include .doc-contract-kit/make/repo-contract.mk",
                (repo / "Makefile").read_text(encoding="utf-8"),
            )
            manifest = read_manifest(repo)
            files = {item["path"]: item for item in manifest["files"]}
            self.assertFalse(files["Makefile"]["managed"])
            self.assertEqual(files["Makefile"]["owner"], "target")
            self.assertTrue(files[".doc-contract-kit/make/repo-contract.mk"]["managed"])

    def test_customized_old_managed_makefile_is_preserved_with_bridge_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)
            manifest = read_manifest(repo)
            for item in manifest["files"]:
                if item["path"] == "Makefile":
                    item["installed_sha256"] = sha256_text("# Old managed kit Makefile\n")
                    item["managed"] = True
                    item["owner"] = "kit"
                    break
            write_manifest(repo, manifest)
            customized = "app-test:\n\t@echo app\n"
            (repo / "Makefile").write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "Makefile").read_text(encoding="utf-8"), customized)
            self.assertIn("target-owned: Makefile", result.stdout)
            reports = sorted((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json"))
            self.assertTrue(reports)
            report = json.loads(reports[-1].read_text(encoding="utf-8"))
            report_md = reports[-1].with_suffix(".md")
            self.assertTrue(report_md.exists())
            self.assertIn("root Makefile is target-owned", report_md.read_text(encoding="utf-8"))
            makefile_actions = [item for item in report["actions"] if item["path"] == "Makefile"]
            self.assertTrue(makefile_actions)
            self.assertIn("root Makefile is target-owned", makefile_actions[0]["reason"])
            self.assertTrue((repo / makefile_actions[0]["proposed"]).exists())

    def test_legacy_install_without_manifest_adopts_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)
            manifest_path(repo).unlink()
            customized = "# Legacy custom agents\n"
            (repo / "AGENTS.md").write_text(customized, encoding="utf-8")

            result = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Legacy install adopted", result.stdout)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized)
            manifest = read_manifest(repo)
            receipt = json.loads((repo / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertIn("workflow-source", receipt["source_components"])
            self.assertEqual(manifest["prompt_snapshot"]["name"], "workflow-source")
            agents = next(item for item in manifest["files"] if item["path"] == "AGENTS.md")
            self.assertTrue(agents["managed"])
            self.assertEqual(agents["installed_sha256"], sha256_text(customized))

    def test_guided_upgrade_from_older_metadata_preserves_custom_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)
            customized_agents = (repo / "AGENTS.md").read_text(encoding="utf-8") + "\nTarget-specific instruction.\n"
            (repo / "AGENTS.md").write_text(customized_agents, encoding="utf-8")
            receipt = read_receipt(repo)
            manifest = read_manifest(repo)
            receipt.pop("profile_config_schema_version", None)
            manifest.pop("profile_config_schema_version", None)
            write_receipt(repo, receipt)
            write_manifest(repo, manifest)

            plan = run([sys.executable, str(UPDATE), str(repo), "--dry-run"], ROOT)

            self.assertEqual(plan.returncode, 0, plan.stderr)
            payload = json.loads(plan.stdout)
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["detected_state"]["profile_config_schema"]["status"], "missing")
            self.assertTrue(any(item["action"] == "migrate-profile-config" for item in payload["actions"]))
            self.assertTrue(any(item["path"] == "AGENTS.md" for item in payload["conflicts"]))
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized_agents)

            migrate = run([sys.executable, str(UPDATE), str(repo), "--apply", "--metadata-only"], ROOT)

            self.assertEqual(migrate.returncode, 0, migrate.stderr)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized_agents)
            self.assertEqual(read_receipt(repo)["profile_config_schema_version"], 1)
            self.assertEqual(read_manifest(repo)["profile_config_schema_version"], 1)

            apply = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(apply.returncode, 0, apply.stderr)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized_agents)
            reports = sorted((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json"))
            self.assertTrue(reports)
            report = json.loads(reports[-1].read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == "AGENTS.md" for item in report["conflicts"]))
            self.assertTrue(sorted((repo / ".doc-contract-kit" / "updates").glob("*/proposed/AGENTS.md")))
            self.assertTrue((repo / "docs" / "upgrade-flow.md").exists())
            self.assertIn("AGENTS.md", (repo / "docs" / "upgrade-flow.md").read_text(encoding="utf-8"))

    def test_dry_run_writes_no_target_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            mark_managed_baseline(repo, "AGENTS.md", "# Old managed agents\n")

            result = run([sys.executable, str(UPDATE), str(repo), "--dry-run"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), "# Old managed agents\n")
            self.assertFalse(list((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json")))
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "update-plan")
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertTrue(any("sidecar-init" in item["command"] for item in payload["after_update"]))

    def test_update_plan_reports_missing_profile_config_schema_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            receipt = read_receipt(repo)
            manifest = read_manifest(repo)
            receipt.pop("profile_config_schema_version", None)
            manifest.pop("profile_config_schema_version", None)
            write_receipt(repo, receipt)
            write_manifest(repo, manifest)

            result = run([sys.executable, str(UPDATE), str(repo), "--plan-json"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["target_repo_writes"]["performed"])
            self.assertEqual(payload["detected_state"]["profile_config_schema"]["status"], "missing")
            self.assertTrue(any(item["action"] == "migrate-profile-config" for item in payload["actions"]))
            self.assertTrue(any("--metadata-only" in command for command in payload["next_commands"]))
            self.assertNotIn("profile_config_schema_version", read_receipt(repo))
            self.assertNotIn("profile_config_schema_version", read_manifest(repo))

    def test_update_plan_reports_outdated_profile_config_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            receipt = read_receipt(repo)
            manifest = read_manifest(repo)
            receipt["profile_config_schema_version"] = 0
            manifest["profile_config_schema_version"] = 0
            write_receipt(repo, receipt)
            write_manifest(repo, manifest)

            result = run([sys.executable, str(UPDATE), str(repo), "--plan-json"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            schema = payload["detected_state"]["profile_config_schema"]
            self.assertEqual(schema["status"], "outdated")
            self.assertEqual(schema["current_version"], 1)
            self.assertTrue(any(item["action"] == "migrate-profile-config" for item in payload["actions"]))

    def test_metadata_only_apply_preserves_customized_managed_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)
            manifest = read_manifest(repo)
            receipt = read_receipt(repo)
            agents_entry = next(item for item in manifest["files"] if item["path"] == "AGENTS.md")
            old_agents_hash = agents_entry["installed_sha256"]
            old_receipt_provenance = {
                "kit_version": "0.0.1",
                "source_ref": "old-receipt-ref",
                "prompt_snapshot": {"name": "agent-workflow-kit", "source_ref": "old-receipt-prompt"},
            }
            old_manifest_provenance = {
                "kit_version": "0.0.1",
                "source_ref": "old-manifest-ref",
                "prompt_snapshot": {"name": "agent-workflow-kit", "source_ref": "old-manifest-prompt"},
            }
            customized = (repo / "AGENTS.md").read_text(encoding="utf-8") + "\nLocal custom instruction.\n"
            (repo / "AGENTS.md").write_text(customized, encoding="utf-8")
            receipt["profile_config_schema_version"] = 0
            receipt.update(old_receipt_provenance)
            manifest["profile_config_schema_version"] = 0
            manifest.update(old_manifest_provenance)
            write_receipt(repo, receipt)
            write_manifest(repo, manifest)

            result = run([sys.executable, str(UPDATE), str(repo), "--apply", "--metadata-only"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "AGENTS.md").read_text(encoding="utf-8"), customized)
            receipt = read_receipt(repo)
            manifest = read_manifest(repo)
            self.assertEqual(receipt["profile_config_schema_version"], 1)
            self.assertEqual(manifest["profile_config_schema_version"], 1)
            for key, value in old_receipt_provenance.items():
                self.assertEqual(receipt[key], value)
            for key, value in old_manifest_provenance.items():
                self.assertEqual(manifest[key], value)
            agents_entry = next(item for item in manifest["files"] if item["path"] == "AGENTS.md")
            self.assertEqual(agents_entry["installed_sha256"], old_agents_hash)
            self.assertFalse(list((repo / ".doc-contract-kit" / "updates").glob("*/update-report.json")))

    def test_invalid_profile_config_schema_blocks_plan_and_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            receipt = read_receipt(repo)
            receipt["profile_config_schema_version"] = "future"
            write_receipt(repo, receipt)

            plan = run([sys.executable, str(UPDATE), str(repo), "--plan-json"], ROOT)
            apply = run([sys.executable, str(UPDATE), str(repo), "--apply", "--metadata-only"], ROOT)

            self.assertEqual(plan.returncode, 1)
            payload = json.loads(plan.stdout)
            self.assertEqual(payload["detected_state"]["profile_config_schema"]["status"], "blocked")
            self.assertTrue(any(item["code"] == "profile_config_schema_blocked" for item in payload["blockers"]))
            self.assertEqual(apply.returncode, 2)

    def test_plan_reports_customized_missing_makefile_and_dirty_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            commit_all(repo)
            manifest = read_manifest(repo)
            for item in manifest["files"]:
                if item["path"] == "Makefile":
                    item["installed_sha256"] = sha256_text("# Old managed kit Makefile\n")
                    item["managed"] = True
                    item["owner"] = "kit"
                if item["path"] == "scripts/kit_status.py":
                    item["installed_sha256"] = sha256_text("old kit status\n")
                    item["managed"] = True
                    item["owner"] = "kit"
            write_manifest(repo, manifest)
            (repo / "Makefile").write_text("app-test:\n\t@echo app\n", encoding="utf-8")
            (repo / "scripts" / "kit_status.py").unlink()

            result = run([sys.executable, str(UPDATE), str(repo), "--plan-json"], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["detected_state"]["kind"], "current_manifest")
            self.assertTrue(payload["detected_state"]["dirty"])
            self.assertTrue(any(item["code"] == "dirty_target_repo" for item in payload["warnings"]))
            actions = {item["path"]: item["action"] for item in payload["actions"]}
            self.assertEqual(actions["Makefile"], "target-owned")
            self.assertEqual(actions["scripts/kit_status.py"], "restore")
            self.assertTrue(any(item["path"] == "AGENTS.md" for item in payload["read_next"]))
            self.assertTrue(any(item["path"] == "docs/ops/agent-workflow.md" for item in payload["read_next"]))
            self.assertTrue(any("--write-sidecar" in item["command"] for item in payload["after_update"]))

    def test_plain_update_plan_prints_upgrade_reading(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)

            result = run([sys.executable, str(UPDATE), str(repo)], ROOT)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("read next:", result.stdout)
            self.assertIn("AGENTS.md", result.stdout)
            self.assertIn("CHANGELOG.md", result.stdout)
            self.assertIn("after updating:", result.stdout)
            self.assertIn("sidecar-init", result.stdout)
            self.assertIn("--write-sidecar", result.stdout)

    def test_makefile_boundary_recognizes_direct_kit_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            direct_targets = (
                "agent-start:\n\t@echo local\n"
                "kit-status:\n\t@echo local\n"
                "kit-update:\n\t@echo local\n"
                "kit-refresh:\n\t@echo local\n"
            )
            (repo / "Makefile").write_text(direct_targets, encoding="utf-8")

            plan = run([sys.executable, str(UPDATE), str(repo), "--plan-json"], ROOT)
            status = run([sys.executable, str(repo / "scripts" / "kit_status.py")], repo)

            self.assertEqual(plan.returncode, 0, plan.stderr)
            payload = json.loads(plan.stdout)
            self.assertEqual(
                payload["detected_state"]["makefile_boundary"],
                "target-owned-root-makefile-direct-kit-targets",
            )
            makefile = next(item for item in payload["actions"] if item["path"] == "Makefile")
            self.assertIn("defines kit targets directly", makefile["reason"])
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn("defines kit targets directly", status.stdout)

    def test_invalid_manifest_blocks_plan_and_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            init_repo(repo)
            install_agentic(repo)
            (repo / ".doc-contract-kit" / "manifest.json").write_text("{bad json", encoding="utf-8")

            plan = run([sys.executable, str(UPDATE), str(repo), "--plan-json"], ROOT)
            apply = run([sys.executable, str(UPDATE), str(repo), "--apply"], ROOT)

            self.assertEqual(plan.returncode, 1)
            payload = json.loads(plan.stdout)
            self.assertEqual(payload["detected_state"]["kind"], "invalid_metadata")
            self.assertTrue(payload["blockers"])
            self.assertEqual(apply.returncode, 2)

    def test_kit_refresh_refuses_dirty_kit_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            repo = tmp_root / "target"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            kit = clone_local_kit(tmp_root)
            (kit / "DIRTY.txt").write_text("dirty\n", encoding="utf-8")

            result = run(["make", "kit-refresh", f"KIT={kit}"], repo)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Kit checkout has local changes", result.stderr + result.stdout)

    def test_kit_refresh_pulls_status_and_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            repo = tmp_root / "target"
            repo.mkdir()
            init_repo(repo)
            install_agentic(repo)
            kit = clone_local_kit(tmp_root)

            result = run(["make", "kit-refresh", f"KIT={kit}"], repo)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("repo-contract-kit installed version:", result.stdout)
            self.assertIn("Update complete.", result.stdout)

    def test_kit_update_stack_updates_target_and_workflow_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            target = tmp_root / "target"
            workflow = tmp_root / "Codex_CodeReview"
            target.mkdir()
            workflow.mkdir()
            init_repo(target)
            init_repo(workflow)
            install_agentic(target)
            install_agentic(workflow)
            commit_all(target, "Install kit in target")
            commit_all(workflow, "Install kit in workflow source")

            result = run(
                [
                    "make",
                    "kit-update-stack",
                    f"KIT={ROOT}",
                    f"WORKFLOW={workflow}",
                    "STACK_UPDATE_COMPAT=1",
                    "STACK_UPDATE_JSON=1",
                ],
                target,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["target_repo"], str(target.resolve()))
            self.assertEqual(payload["workflow_source"], str(workflow.resolve()))
            self.assertEqual([step["label"] for step in payload["steps"]], ["update target repo", "update workflow source repo"])
            self.assertTrue(list((target / ".doc-contract-kit" / "updates").glob("*/update-report.json")))
            self.assertTrue(list((workflow / ".doc-contract-kit" / "updates").glob("*/update-report.json")))

    def test_kit_update_stack_requires_compat_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_repo(target)
            install_agentic(target)
            commit_all(target, "Install kit in target")

            result = run(["make", "kit-update-stack"], target)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("deprecated maintainer compatibility target", result.stdout)
            self.assertIn("kit update --dry-run", result.stdout)
            self.assertIn("STACK_UPDATE_COMPAT=1", result.stdout)

    def test_kit_update_stack_discovers_local_checkouts_without_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            target = tmp_root / "target"
            workflow = tmp_root / "Codex_CodeReview"
            kit_link = tmp_root / "Hermes" / "doc-contract-kit"
            target.mkdir()
            workflow.mkdir()
            kit_link.parent.mkdir()
            kit_link.symlink_to(ROOT, target_is_directory=True)
            init_repo(target)
            init_repo(workflow)
            install_agentic(target)
            install_agentic(workflow)
            (workflow / "workflows" / "prompts").mkdir(parents=True)
            (workflow / "scripts" / "check_self_dogfood_boundary.py").write_text("# marker\n", encoding="utf-8")
            commit_all(target, "Install kit in target")
            commit_all(workflow, "Install kit in workflow source")

            result = run(["make", "kit-update-stack", "STACK_UPDATE_COMPAT=1", "STACK_UPDATE_JSON=1"], target)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["target_repo"], str(target.resolve()))
            self.assertEqual(payload["workflow_source"], str(workflow.resolve()))
            self.assertEqual(payload["kit"], str(ROOT.resolve()))
            self.assertEqual([step["label"] for step in payload["steps"]], ["update target repo", "update workflow source repo"])
            self.assertTrue(list((target / ".doc-contract-kit" / "updates").glob("*/update-report.json")))
            self.assertTrue(list((workflow / ".doc-contract-kit" / "updates").glob("*/update-report.json")))


if __name__ == "__main__":
    unittest.main()
