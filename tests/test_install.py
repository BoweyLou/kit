import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "install.py"


def init_real_git_repo(path: Path):
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


class InstallTests(unittest.TestCase):
    def test_install_writes_config_and_skips_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()
            agents = target / "AGENTS.md"
            agents.write_text("existing agents\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"), "existing agents\n")
            self.assertTrue((target / "doc-contract.json").exists())
            self.assertTrue((target / "scripts" / "_agent_scope.py").exists())
            self.assertTrue((target / "scripts" / "agent_start.py").exists())
            self.assertTrue((target / "scripts" / "agent_task_cleanup.py").exists())
            self.assertTrue((target / "scripts" / "agent_task_finalize.py").exists())
            self.assertTrue((target / "scripts" / "agent_task_prepare.py").exists())
            self.assertTrue((target / "scripts" / "agent_task_status.py").exists())
            self.assertTrue((target / "scripts" / "agent_research.py").exists())
            self.assertTrue((target / "scripts" / "branch_readiness.py").exists())
            self.assertTrue((target / "scripts" / "classify_review_risk.py").exists())
            self.assertTrue((target / "scripts" / "check_docs_as_tests.py").exists())
            self.assertTrue((target / "scripts" / "check_doc_impact.py").exists())
            self.assertTrue((target / "scripts" / "changelog_update.py").exists())
            self.assertTrue((target / "scripts" / "docs_explain.py").exists())
            self.assertTrue((target / "scripts" / "goal_check.py").exists())
            self.assertTrue((target / "scripts" / "kit_status.py").exists())
            self.assertTrue((target / "scripts" / "kit_update_stack.py").exists())
            self.assertTrue((target / "REVIEW.md").exists())
            self.assertTrue((target / "scripts" / "version.py").exists())
            self.assertTrue((target / "scripts" / "lint_agent_docs.py").exists())
            self.assertTrue((target / "scripts" / "localize_doc_impact.py").exists())
            self.assertTrue((target / "scripts" / "render_docs_contract_comment.py").exists())
            self.assertTrue((target / "scripts" / "verify_agent_receipt.py").exists())
            self.assertTrue((target / ".doc-contract-kit" / "make" / "repo-contract.mk").exists())
            self.assertTrue((target / "schemas" / "session-receipt.schema.json").exists())
            self.assertTrue((target / "schemas" / "area-contracts.schema.json").exists())
            self.assertTrue((target / "schemas" / "review-risk.schema.json").exists())
            self.assertTrue((target / "schemas" / "research-brief.schema.json").exists())
            self.assertTrue((target / "schemas" / "research-source-report.schema.json").exists())
            self.assertTrue((target / "schemas" / "research-synthesis.schema.json").exists())
            self.assertTrue((target / "schemas" / "persona-manifest.schema.json").exists())
            self.assertTrue((target / "schemas" / "agent-permission-policy.schema.json").exists())
            self.assertTrue((target / ".agent-workflows" / "agent-permission-policy.json").exists())
            self.assertTrue((target / ".agent-workflows" / "area-contracts.json").exists())
            self.assertTrue((target / ".agent-workflows" / "instruction-budgets.json").exists())
            self.assertTrue((target / ".agent-workflows" / "schemas" / "safe-output.schema.json").exists())
            self.assertTrue((target / ".github" / "workflows" / "docs-contract-comment.yml").exists())
            self.assertTrue((target / ".github" / "workflows" / "agent-review-readonly.yml").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-instruction-hygiene.md").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-tool-network-allowlist.md").exists())
            self.assertTrue((target / "docs" / "ops" / "slash-command-grammar.md").exists())
            self.assertTrue((target / "docs" / "harness-engineering.md").exists())
            self.assertTrue((target / "docs" / "planning-adapters.md").exists())
            self.assertTrue((target / "docs" / "upgrade-flow.md").exists())
            self.assertTrue((target / ".agent-workflows" / "runs" / ".gitignore").exists())
            self.assertTrue((target / ".agent-workflows" / "tasks" / ".gitignore").exists())
            self.assertTrue((target / ".doc-contract-kit" / "manifest.json").exists())
            self.assertTrue((target / ".doc-contract-kit" / "updates" / ".gitignore").exists())

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertIn("source_version", receipt)
            self.assertIn("source_ref", receipt)
            self.assertIn("last_updated_at", receipt)
            self.assertEqual(receipt["profile_config_schema_version"], 1)
            self.assertIn("prompt_snapshot", receipt)
            self.assertEqual(receipt["prompt_snapshot"]["name"], "workflow-source")
            self.assertIn("snapshot_sha256", receipt["prompt_snapshot"])

    def test_install_preserves_existing_makefile_and_installs_kit_fragment(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()
            makefile = target / "Makefile"
            makefile.write_text("app-test:\n\t@echo app\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(makefile.read_text(encoding="utf-8"), "app-test:\n\t@echo app\n")
            self.assertTrue((target / ".doc-contract-kit" / "make" / "repo-contract.mk").exists())
            self.assertIn("include .doc-contract-kit/make/repo-contract.mk", result.stdout)

    def test_install_force_overwrites_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()
            agents = target / "AGENTS.md"
            agents.write_text("existing agents\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--force"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(agents.read_text(encoding="utf-8").startswith("# AGENTS.md"))

    def test_install_rejects_non_git_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Target is not a git repository", result.stderr)

    def test_install_test_first_profile_writes_executable_spec_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "test-first"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "README.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "regression-first-bugfix.md").exists())
            self.assertTrue((target / "docs" / "testing-strategy.md").exists())
            self.assertTrue((target / "docs" / "adr" / "0001-testing-philosophy.md").exists())

            pr_template = (target / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
            self.assertIn("Test-first evidence", pr_template)
            self.assertIn("No tests needed:", pr_template)
            self.assertIn("review docs/testing-strategy.md", result.stdout)

    def test_install_lite_preset_writes_minimal_mode_guidance_without_prompt_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "lite"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "docs" / "lite-mode.md").exists())
            self.assertTrue((target / "docs" / "sidecar-retention.md").exists())
            self.assertFalse((target / ".codex" / "prompts").exists())
            self.assertFalse((target / "VERSION").exists())
            self.assertFalse((target / "CHANGELOG.md").exists())

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["preset"], "lite")
            self.assertEqual(receipt["profiles"], ["minimal"])

    def test_install_docs_as_tests_profile_writes_config_and_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "docs-as-tests"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".agent-workflows" / "docs-as-tests.json").exists())
            self.assertTrue((target / "docs" / "ops" / "docs-as-tests.md").exists())
            self.assertTrue((target / "scripts" / "check_docs_as_tests.py").exists())
            self.assertTrue((target / ".doc-contract-kit" / "make" / "repo-contract.mk").exists())
            profile_doc = (target / "docs" / "ops" / "docs-as-tests.md").read_text(encoding="utf-8")
            self.assertIn("openapi_operation_exists", profile_doc)
            self.assertIn("target_repo_writes=false", profile_doc)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["profiles"], ["docs-as-tests"])
            self.assertIsNone(receipt["preset"])

            config = json.loads((target / ".agent-workflows" / "docs-as-tests.json").read_text(encoding="utf-8"))
            self.assertEqual(config["assertions"], [])

    def test_install_node_profile_writes_stack_hints_without_scaffolding(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "node"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            profile_config = target / ".agent-workflows" / "stack-profiles" / "node.json"
            profile_doc = target / "docs" / "ops" / "node-stack-profile.md"
            self.assertTrue(profile_config.exists())
            self.assertTrue(profile_doc.exists())
            self.assertFalse((target / "package.json").exists())
            self.assertFalse((target / "package-lock.json").exists())
            self.assertFalse((target / "node_modules").exists())

            config = json.loads(profile_config.read_text(encoding="utf-8"))
            self.assertEqual(config["stack"], "node")
            self.assertIn("package.json", config["detection"]["primary_files"])
            self.assertIn("No dependency installation.", config["non_goals"])
            doc_text = profile_doc.read_text(encoding="utf-8")
            self.assertIn("does not install packages", doc_text)
            self.assertIn("Do not run dependency installation", doc_text)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["profiles"], ["node"])
            self.assertIsNone(receipt["preset"])

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            manifest_files = {item["path"]: item for item in manifest["files"]}
            for rel_path in (
                ".agent-workflows/stack-profiles/node.json",
                "docs/ops/node-stack-profile.md",
            ):
                self.assertIn(rel_path, manifest_files)
                self.assertTrue(manifest_files[rel_path]["managed"])
                self.assertEqual(manifest_files[rel_path]["profile"], "node")

    def test_install_python_profile_writes_stack_hints_without_scaffolding(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "python"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            profile_config = target / ".agent-workflows" / "stack-profiles" / "python.json"
            profile_doc = target / "docs" / "ops" / "python-stack-profile.md"
            self.assertTrue(profile_config.exists())
            self.assertTrue(profile_doc.exists())
            self.assertFalse((target / "pyproject.toml").exists())
            self.assertFalse((target / "requirements.txt").exists())
            self.assertFalse((target / ".venv").exists())

            config = json.loads(profile_config.read_text(encoding="utf-8"))
            self.assertEqual(config["stack"], "python")
            self.assertIn("pyproject.toml", config["detection"]["primary_files"])
            self.assertIn("No virtual environment creation.", config["non_goals"])
            doc_text = profile_doc.read_text(encoding="utf-8")
            self.assertIn("does not create virtual environments", doc_text)
            self.assertIn("Do not install dependencies", doc_text)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["profiles"], ["python"])
            self.assertIsNone(receipt["preset"])

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            manifest_files = {item["path"]: item for item in manifest["files"]}
            for rel_path in (
                ".agent-workflows/stack-profiles/python.json",
                "docs/ops/python-stack-profile.md",
            ):
                self.assertIn(rel_path, manifest_files)
                self.assertTrue(manifest_files[rel_path]["managed"])
                self.assertEqual(manifest_files[rel_path]["profile"], "python")

    def test_stack_profiles_are_absent_from_presets_and_default_install(self):
        cases = [
            ("default", []),
            ("minimal", ["--preset", "minimal"]),
            ("learning", ["--preset", "learning"]),
            ("test-first", ["--preset", "test-first"]),
            ("agentic", ["--preset", "agentic"]),
        ]
        for name, args in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp) / "target"
                    target.mkdir()
                    (target / ".git").mkdir()

                    result = subprocess.run(
                        [sys.executable, str(INSTALL), str(target), *args],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertFalse((target / ".agent-workflows" / "stack-profiles" / "node.json").exists())
                    self.assertFalse((target / ".agent-workflows" / "stack-profiles" / "python.json").exists())
                    self.assertFalse((target / "docs" / "ops" / "node-stack-profile.md").exists())
                    self.assertFalse((target / "docs" / "ops" / "python-stack-profile.md").exists())
                    receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
                    self.assertNotIn("node", receipt["profiles"])
                    self.assertNotIn("python", receipt["profiles"])

    def test_install_private_context_profile_writes_examples_and_ignores_real_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "private-context"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            context_dir = target / ".agent-context"
            expected_files = {
                ".agent-context/.gitignore",
                ".agent-context/README.md",
                ".agent-context/project-context.example.md",
                ".agent-context/user-preferences.example.md",
                ".agent-context/private-local-context.example.md",
            }
            for rel_path in expected_files:
                self.assertTrue((target / rel_path).exists(), rel_path)

            combined_text = "\n".join((target / rel_path).read_text(encoding="utf-8") for rel_path in expected_files if rel_path.endswith(".md"))
            normalized_text = " ".join(combined_text.split())
            for warning in (
                "secrets",
                "tokens",
                "cookies",
                "passwords",
                "private URLs",
                "account identifiers",
                "customer data",
                "personal messages",
                "medical or financial data",
                "proprietary snippets",
            ):
                self.assertIn(warning, normalized_text)
            for live_looking in ("sk-", "ghp_", "xoxb-", "AKIA", "-----BEGIN"):
                self.assertNotIn(live_looking, combined_text)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["profiles"], ["private-context"])
            self.assertIsNone(receipt["preset"])

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            manifest_files = {item["path"]: item for item in manifest["files"]}
            for rel_path in expected_files:
                self.assertIn(rel_path, manifest_files)
                self.assertTrue(manifest_files[rel_path]["managed"])
                self.assertEqual(manifest_files[rel_path]["profile"], "private-context")

            subprocess.run(["git", "add", "."], cwd=target, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Install private context profile",
                ],
                cwd=target,
                check=True,
            )

            real_files = [
                context_dir / "project-context.md",
                context_dir / "user-preferences.md",
                context_dir / "private-local-context.md",
                context_dir / "local-notes.txt",
            ]
            for path in real_files:
                path.write_text("local non-secret note\n", encoding="utf-8")
                ignored = subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=target, check=False)
                self.assertEqual(ignored.returncode, 0, str(path))

            status = subprocess.run(["git", "status", "--short"], cwd=target, capture_output=True, text=True, check=False)
            self.assertEqual(status.stdout, "")

    def test_install_private_context_can_compose_with_local_agentic_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL),
                    str(target),
                    "--profiles",
                    "local-agentic,private-context",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".agent-workflows" / "README.md").exists())
            self.assertTrue((target / ".agent-context" / "README.md").exists())
            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["profiles"], ["local-agentic", "private-context"])
            self.assertIsNone(receipt["preset"])

    def test_private_context_profile_is_absent_from_presets_and_default_install(self):
        cases = [
            ("default", []),
            ("minimal", ["--preset", "minimal"]),
            ("learning", ["--preset", "learning"]),
            ("test-first", ["--preset", "test-first"]),
            ("agentic", ["--preset", "agentic"]),
        ]
        for name, args in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp) / "target"
                    target.mkdir()
                    (target / ".git").mkdir()

                    result = subprocess.run(
                        [sys.executable, str(INSTALL), str(target), *args],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertFalse((target / ".agent-context").exists())
                    receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
                    self.assertNotIn("private-context", receipt["profiles"])

    def test_install_composed_profiles_write_review_and_tdd_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL),
                    str(target),
                    "--profiles",
                    "review-prompts,test-first",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".codex" / "prompts" / "multi-agent-repo-review.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "codebase-learning-comments.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "personas" / "doc-code-delta.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "README.md").exists())

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["profiles"], ["review-prompts", "test-first"])
            self.assertIsNone(receipt["preset"])
            self.assertIn("repo-contract-kit", receipt["source_commits"])

    def test_install_agentic_preset_writes_commands_and_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".codex" / "prompts" / "multi-agent-repo-review.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "policies" / "review-risk-classifier.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "research-brief.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-github.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-arxiv.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-hacker-news.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "research" / "source-official-docs.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "task-packet.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "task-worktree-cleanup.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "templates" / "task-packet.md").exists())
            self.assertTrue((target / ".codex" / "prompts" / "tdd" / "test-quality-sentinel.md").exists())
            self.assertTrue((target / ".agent-workflows" / "README.md").exists())
            self.assertTrue((target / ".agent-workflows" / "repo-review.md").exists())
            self.assertTrue((target / ".agent-workflows" / "schemas" / "session-receipt.schema.json").exists())
            self.assertTrue((target / ".agent-workflows" / "area-contracts.json").exists())
            self.assertTrue((target / "schemas" / "task-packet.schema.json").exists())
            self.assertTrue((target / "schemas" / "area-contracts.schema.json").exists())
            self.assertTrue((target / "schemas" / "review-risk.schema.json").exists())
            self.assertTrue((target / "schemas" / "review-synthesis.schema.json").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-workflow.md").exists())
            self.assertTrue((target / "docs" / "ops" / "agent-tool-network-allowlist.md").exists())
            self.assertTrue((target / "docs" / "ops" / "slash-command-grammar.md").exists())
            self.assertTrue((target / "docs" / "working-rhythm.md").exists())
            self.assertTrue((target / "docs" / "harness-engineering.md").exists())
            self.assertTrue((target / "docs" / "planning-adapters.md").exists())
            self.assertTrue((target / "docs" / "upgrade-flow.md").exists())
            slash_command_spec = (target / "docs" / "ops" / "slash-command-grammar.md").read_text(encoding="utf-8")
            self.assertIn("/docs-impact", slash_command_spec)
            self.assertIn("/waive-docs", slash_command_spec)
            self.assertIn("/review-docs", slash_command_spec)
            self.assertIn("/add-docs", slash_command_spec)
            self.assertIn("/update-changelog", slash_command_spec)
            self.assertIn("specification only", slash_command_spec)
            self.assertIn(".agent-workflows/agent-permission-policy.json", slash_command_spec)
            self.assertTrue((target / "VERSION").exists())
            self.assertTrue((target / "CHANGELOG.md").exists())
            self.assertTrue((target / "docs" / "versioning.md").exists())
            readonly_workflow = (target / ".github" / "workflows" / "agent-review-readonly.yml").read_text(encoding="utf-8")
            self.assertIn("persist-credentials: false", readonly_workflow)
            self.assertIn("AGENT_TRUST_PROFILE: untrusted-pr", readonly_workflow)
            self.assertIn("docs-impact.sarif", readonly_workflow)
            self.assertIn("agent-docs-lint.sarif", readonly_workflow)
            comment_workflow = (target / ".github" / "workflows" / "docs-contract-comment.yml").read_text(encoding="utf-8")
            self.assertIn("pull_request_target:", comment_workflow)
            self.assertIn("issues: write", comment_workflow)
            self.assertIn("pull-requests: write", comment_workflow)
            self.assertIn("ref: ${{ github.event.pull_request.base.sha }}", comment_workflow)
            self.assertIn("render_docs_contract_comment.py", comment_workflow)
            self.assertIn("docs-contract-comment.md", comment_workflow)

            makefile = (target / "Makefile").read_text(encoding="utf-8")
            kit_makefile = (target / ".doc-contract-kit" / "make" / "repo-contract.mk").read_text(encoding="utf-8")
            self.assertIn("include .doc-contract-kit/make/repo-contract.mk", makefile)
            self.assertIn("help: workflow-help", kit_makefile)
            self.assertIn("workflow-help:", kit_makefile)
            self.assertIn("GOAL_CHECK_JSON ?= 0", kit_makefile)
            self.assertIn("CONTEXT_BUNDLE_JSON ?= 0", kit_makefile)
            self.assertIn("BRANCH_READY_JSON ?= 0", kit_makefile)
            self.assertIn("INSTRUCTION_DIET_JSON ?= 0", kit_makefile)
            self.assertIn("SELF_HEAL_JSON ?= 0", kit_makefile)
            self.assertIn("SELF_HEAL_APPLY ?= 0", kit_makefile)
            self.assertIn("SELF_HEAL_ALLOW_PATHS ?=", kit_makefile)
            self.assertIn("TASK_PREPARE_JSON ?= 0", kit_makefile)
            self.assertIn("DIRTY_PRIMARY_BASELINE ?= 0", kit_makefile)
            self.assertIn("TASK_OWNER_LABEL ?=", kit_makefile)
            self.assertIn("TASK_THREAD_ID ?=", kit_makefile)
            self.assertIn("TASK_AUTOMATION_ID ?=", kit_makefile)
            self.assertIn("AUTOMATION_HANDOFF_ORIGINAL_BASELINE ?=", kit_makefile)
            self.assertIn("AUTOMATION_HANDOFF_CAPTURE_ORIGINAL_BASELINE ?= 0", kit_makefile)
            self.assertIn("AUTOMATION_HANDOFF_ALLOW_ORIGINAL_DRIFT ?= 0", kit_makefile)
            self.assertIn("agent-start:", kit_makefile)
            self.assertIn("goal-check:", kit_makefile)
            self.assertIn("agent-context-bundle:", kit_makefile)
            self.assertIn("agent-branch-readiness:", kit_makefile)
            self.assertIn("agent-task-cleanup:", kit_makefile)
            self.assertIn("agent-task-closeout:", kit_makefile)
            self.assertIn("agent-task-finalize:", kit_makefile)
            self.assertIn("agent-task-prepare:", kit_makefile)
            self.assertIn('--owner-label "$(TASK_OWNER_LABEL)"', kit_makefile)
            self.assertIn('--thread-id "$(TASK_THREAD_ID)"', kit_makefile)
            self.assertIn('--automation-id "$(TASK_AUTOMATION_ID)"', kit_makefile)
            self.assertIn("agent-task-ready:", kit_makefile)
            self.assertIn("agent-automation-handoff:", kit_makefile)
            self.assertIn("agent-preflight:", kit_makefile)
            self.assertIn("agent-doctor:", kit_makefile)
            self.assertIn("agent-self-heal:", kit_makefile)
            self.assertIn("agent-task-status:", kit_makefile)
            self.assertIn("agent-run-review:", kit_makefile)
            self.assertIn("agent-research-plan:", kit_makefile)
            self.assertIn("agent-research-run:", kit_makefile)
            self.assertIn("agent-research-synthesize:", kit_makefile)
            self.assertIn("agent-research-to-task-packet:", kit_makefile)
            self.assertIn("agent-receipt-verify:", kit_makefile)
            self.assertIn("kit-status:", kit_makefile)
            self.assertIn("kit-explain:", kit_makefile)
            self.assertIn("kit-migrate-config:", kit_makefile)
            self.assertIn("kit-update:", kit_makefile)
            self.assertIn("kit-refresh:", kit_makefile)
            self.assertIn("STACK_UPDATE_COMPAT ?= 0", kit_makefile)
            self.assertIn("kit-update-stack:", kit_makefile)
            self.assertIn("deprecated maintainer compatibility target", kit_makefile)
            self.assertIn("kit-refresh-stack:", kit_makefile)
            self.assertIn("agent-review:", kit_makefile)
            self.assertIn("agent-learn:", kit_makefile)
            self.assertIn("agent-review-risk:", kit_makefile)
            self.assertIn("agent-task-packet:", kit_makefile)
            self.assertIn("agent-test-first:", kit_makefile)
            self.assertIn("agent-verify:", kit_makefile)
            self.assertIn("agent-docs-lint:", kit_makefile)
            self.assertIn("agent-instruction-diet:", kit_makefile)
            self.assertIn("agent-docs-localize:", kit_makefile)
            self.assertIn("DOCS_EXPLAIN_JSON ?= 0", kit_makefile)
            self.assertIn("DOCS_AS_TESTS_JSON ?= 0", kit_makefile)
            self.assertIn("docs-as-tests:", kit_makefile)
            self.assertIn("agent-docs-explain:", kit_makefile)
            self.assertIn("agent-docs-propose:", kit_makefile)
            self.assertIn("CHANGELOG_UPDATE_JSON ?= 0", kit_makefile)
            self.assertIn("agent-changelog-update:", kit_makefile)
            self.assertIn("version-status:", kit_makefile)
            self.assertIn("version-check:", kit_makefile)
            self.assertIn("version-bump:", kit_makefile)
            self.assertFalse((target / "scripts" / "install.py").exists())
            installed_cli_status = subprocess.run(
                [
                    sys.executable,
                    str(target / "scripts" / "repo_contract_kit.py"),
                    "status",
                    "--repo",
                    str(target),
                    "--json",
                ],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(installed_cli_status.returncode, 0, installed_cli_status.stderr)
            self.assertEqual(json.loads(installed_cli_status.stdout)["command"], "status")

            branch_ready = subprocess.run(
                ["make", "agent-branch-readiness", "BRANCH_READY_JSON=1"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(branch_ready.returncode, 0)
            branch_payload = json.loads(branch_ready.stdout)
            self.assertEqual(branch_payload["command"], "branch-readiness")
            self.assertFalse(branch_payload["target_repo_writes"])
            self.assertFalse(branch_payload["sidecar_writes"])
            self.assertIn("dirty_checkout", {item["code"] for item in branch_payload["blockers"]})

            for target_name in (
                "help",
                "workflow-help",
                "goal-check",
                "agent-context-bundle",
                "agent-start",
                "agent-preflight",
                "agent-doctor",
                "agent-self-heal",
                "agent-task-status",
                "agent-task-closeout",
                "agent-run-review",
                "agent-research-plan",
                "agent-research-run",
                "agent-research-synthesize",
                "agent-research-to-task-packet",
                "kit-status",
                "kit-explain",
                "agent-review",
                "agent-learn",
                "agent-review-risk",
                "agent-task-packet",
                "agent-test-first",
                "agent-docs-lint",
                "agent-instruction-diet",
                "agent-docs-localize",
                "agent-docs-explain",
                "agent-changelog-update",
                "version-status",
                "version-check",
                "agent-verify",
            ):
                make_result = subprocess.run(
                    ["make", target_name],
                    cwd=target,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(make_result.returncode, 0, make_result.stderr)

                if target_name in {"help", "workflow-help"}:
                    self.assertIn("Orient", make_result.stdout)
                    self.assertIn("Review", make_result.stdout)
                    self.assertIn("Scope", make_result.stdout)
                    self.assertIn("Execute", make_result.stdout)

                if target_name == "agent-start":
                    self.assertIn("Agent start packet written", make_result.stdout)

                if target_name == "goal-check":
                    self.assertIn("Goal check:", make_result.stdout)

                if target_name == "agent-context-bundle":
                    self.assertIn("Agent context bundle", make_result.stdout)

                if target_name == "agent-review":
                    self.assertIn("Read AGENTS.md, REVIEW.md", make_result.stdout)
                    self.assertIn(".agent-workflows/repo-review.md in bootstrap mode", make_result.stdout)
                    self.assertIn("make agent-run-review AGENT=manual", make_result.stdout)
                    self.assertIn("Produce a findings backlog before editing code", make_result.stdout)

                if target_name == "agent-run-review":
                    self.assertIn("Agent review runner artifacts written", make_result.stdout)
                    run_dirs = [
                        path
                        for path in (target / ".agent-workflows" / "runs").iterdir()
                        if path.is_dir()
                    ]
                    self.assertTrue(run_dirs)
                    latest = sorted(run_dirs)[-1]
                    self.assertTrue((latest / "review-run" / "review-run.json").exists())
                    self.assertTrue((latest / "review-run" / "synthesis" / "review-synthesis.json").exists())

                if target_name == "agent-research-plan":
                    self.assertIn("Research plan written", make_result.stdout)

                if target_name == "agent-research-run":
                    self.assertIn("Source research prompt written", make_result.stdout)

                if target_name == "agent-research-synthesize":
                    self.assertIn("Research synthesis prompt written", make_result.stdout)

                if target_name == "agent-research-to-task-packet":
                    self.assertIn("Research handoff prompt written", make_result.stdout)

                if target_name == "kit-status":
                    self.assertIn("workflow prompt snapshot:", make_result.stdout)
                    self.assertNotIn("agent-workflow-kit snapshot:", make_result.stdout)
                    self.assertIn("managed file status: clean", make_result.stdout)
                    self.assertIn("makefile boundary:", make_result.stdout)

                if target_name == "kit-explain":
                    self.assertIn("Boundary", make_result.stdout)
                    self.assertIn("Existing Repo Update Path", make_result.stdout)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["preset"], "agentic")
            self.assertEqual(receipt["profiles"], ["minimal", "local-agentic", "review-prompts", "test-first", "versioning"])
            self.assertNotIn("docs-as-tests", receipt["profiles"])
            self.assertEqual(receipt["source_version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
            self.assertEqual(receipt["prompt_snapshot"]["source_ref"], receipt["source_ref"])
            self.assertIn("workflow-source", receipt["source_components"])
            self.assertEqual(
                receipt["source_commits"]["workflow-source"],
                receipt["prompt_snapshot"]["source_ref"],
            )

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["profile_config_schema_version"], 1)
            self.assertEqual(manifest["prompt_snapshot"]["name"], "workflow-source")
            self.assertEqual(
                manifest["prompt_snapshot"]["snapshot_sha256"],
                receipt["prompt_snapshot"]["snapshot_sha256"],
            )
            manifest_files = {item["path"]: item for item in manifest["files"]}
            self.assertTrue(manifest_files["AGENTS.md"]["managed"])
            self.assertFalse(manifest_files["Makefile"]["managed"])
            self.assertEqual(manifest_files["Makefile"]["owner"], "target")
            self.assertTrue(manifest_files[".doc-contract-kit/make/repo-contract.mk"]["managed"])
            self.assertTrue(manifest_files["docs/planning-adapters.md"]["managed"])
            self.assertTrue(manifest_files["docs/upgrade-flow.md"]["managed"])
            self.assertFalse(manifest_files["VERSION"]["managed"])
            self.assertEqual(manifest_files["VERSION"]["owner"], "target")
            self.assertFalse(manifest_files["CHANGELOG.md"]["managed"])
            self.assertEqual(manifest_files["CHANGELOG.md"]["owner"], "target")

    def test_install_agentic_preserves_existing_target_version_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)
            (target / "VERSION").write_text("9.8.7\n", encoding="utf-8")
            (target / "CHANGELOG.md").write_text("# Existing changelog\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((target / "VERSION").read_text(encoding="utf-8"), "9.8.7\n")
            self.assertEqual((target / "CHANGELOG.md").read_text(encoding="utf-8"), "# Existing changelog\n")

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            manifest_files = {item["path"]: item for item in manifest["files"]}
            self.assertEqual(manifest_files["VERSION"]["owner"], "target")
            self.assertFalse(manifest_files["VERSION"]["managed"])

    def test_install_agentic_with_runtime_adapters_writes_managed_adapter_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [
                    sys.executable,
                    str(INSTALL),
                    str(target),
                    "--preset",
                    "agentic",
                    "--runtime-adapters",
                    "claude-code,github-copilot",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "CLAUDE.md").exists())
            self.assertTrue((target / ".github" / "copilot-instructions.md").exists())
            self.assertIn("thin Claude Code adapter", (target / "CLAUDE.md").read_text(encoding="utf-8"))
            self.assertIn(
                "thin Copilot adapter",
                (target / ".github" / "copilot-instructions.md").read_text(encoding="utf-8"),
            )
            self.assertIn("Runtime adapters: claude-code, github-copilot", result.stdout)

            receipt = json.loads((target / ".doc-contract-kit" / "install.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["runtime_adapters"], ["claude-code", "github-copilot"])

            manifest = json.loads((target / ".doc-contract-kit" / "manifest.json").read_text(encoding="utf-8"))
            manifest_files = {item["path"]: item for item in manifest["files"]}
            self.assertEqual(manifest["runtime_adapters"], ["claude-code", "github-copilot"])
            self.assertTrue(manifest_files["CLAUDE.md"]["managed"])
            self.assertEqual(manifest_files["CLAUDE.md"]["runtime_adapter"], "claude-code")
            self.assertTrue(manifest_files[".github/copilot-instructions.md"]["managed"])
            self.assertEqual(
                manifest_files[".github/copilot-instructions.md"]["runtime_adapter"],
                "github-copilot",
            )

            status = subprocess.run(
                [sys.executable, str(target / "scripts" / "kit_status.py")],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn("runtime adapters: claude-code, github-copilot", status.stdout)

            lint = subprocess.run(
                [sys.executable, str(target / "scripts" / "lint_agent_docs.py"), "--strict-paths"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_install_agentic_agent_start_runs_are_ignored_after_bootstrap_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run(["git", "add", "."], cwd=target, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=repo-contract-kit test",
                    "-c",
                    "user.email=repo-contract-kit@example.invalid",
                    "commit",
                    "-qm",
                    "Install kit",
                ],
                cwd=target,
                check=True,
            )

            make_result = subprocess.run(
                ["make", "agent-start"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(make_result.returncode, 0, make_result.stderr)
            run_dirs = [
                path
                for path in (target / ".agent-workflows" / "runs").iterdir()
                if path.is_dir()
            ]
            self.assertEqual(len(run_dirs), 1)
            run_dir = run_dirs[0]
            self.assertTrue((run_dir / "agent-brief.md").exists())
            self.assertTrue((run_dir / "session-start.json").exists())
            self.assertTrue((run_dir / "receipt.template.json").exists())

            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.stdout.strip(), "")

    def test_kit_status_compares_against_local_kit(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            init_real_git_repo(target)

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "agentic"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            status = subprocess.run(
                ["make", "kit-status", f"KIT={ROOT}"],
                cwd=target,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn("kit update: current", status.stdout)
            self.assertIn("prompt snapshot update: current", status.stdout)

    def test_lint_agent_docs_detects_hidden_unicode(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            bad = target / "AGENTS.md"
            bad.write_text("safe text\u202e\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "lint_agent_docs.py"), "--root", str(target)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("hidden Unicode", result.stdout)

    def test_lint_agent_docs_strict_paths_detects_missing_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text("Read `docs/missing.md` first.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--strict-paths",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("referenced path does not exist: docs/missing.md", result.stdout)

    def test_lint_agent_docs_detects_unsafe_commands_and_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text("Run `git reset --hard` if the agent gets stuck.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(any(issue["rule_id"] == "git-reset-hard" for issue in payload["issues"]))

    def test_lint_agent_docs_emits_sarif_for_agent_safety_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text("Run `git reset --hard` if the agent gets stuck.\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "sarif",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["version"], "2.1.0")
            self.assertEqual(payload["runs"][0]["results"][0]["ruleId"], "git-reset-hard")

    def test_lint_agent_docs_resolves_make_targets_from_included_makefiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            kit_make_dir = target / ".doc-contract-kit" / "make"
            kit_make_dir.mkdir(parents=True)
            (target / "Makefile").write_text(
                ".PHONY: local-check\n"
                "local-check:\n"
                "\t@true\n"
                "\n"
                "include .doc-contract-kit/make/repo-contract.mk\n",
                encoding="utf-8",
            )
            (kit_make_dir / "repo-contract.mk").write_text(
                ".PHONY: agent-docs-lint\n"
                "agent-docs-lint:\n"
                "\t@PYTHONDONTWRITEBYTECODE=1 python3 scripts/lint_agent_docs.py --strict-paths\n",
                encoding="utf-8",
            )
            (target / "AGENTS.md").write_text(
                "# AGENTS.md\n\n"
                "Run:\n\n"
                "```bash\n"
                "make agent-docs-lint\n"
                "```\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--file",
                    "AGENTS.md",
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertFalse(any(issue["rule_id"] == "stale-command" for issue in payload["issues"]))

    def test_lint_agent_docs_warns_on_contradictory_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / "AGENTS.md").write_text(
                "Do not commit from review mode.\nAgents may commit after review mode.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(any(issue["rule_id"] == "contradiction" for issue in payload["issues"]))

    def test_lint_agent_docs_warns_when_instruction_budget_is_exceeded(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            bullets = "\n".join(
                f"- Agents must follow rule {index} because repeated local failures showed this is needed."
                for index in range(1, 43)
            )
            (target / "AGENTS.md").write_text(f"# AGENTS.md\n\n{bullets}\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertTrue(any(issue["rule_id"] == "rule-budget" for issue in payload["issues"]))

    def test_lint_agent_docs_budget_config_can_escalate_to_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".agent-workflows").mkdir()
            (target / "AGENTS.md").write_text("# AGENTS.md\n\nMore detail than this repo allows.\n", encoding="utf-8")
            (target / ".agent-workflows" / "instruction-budgets.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "budgets": [
                            {
                                "pattern": "AGENTS.md",
                                "max_lines": 1,
                                "max_rule_bullets": 10,
                                "severity": "error",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "lint_agent_docs.py"),
                    "--root",
                    str(target),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(any(issue["rule_id"] == "instruction-budget" for issue in payload["issues"]))

    def test_localize_doc_impact_outputs_json_categories(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "localize_doc_impact.py"),
                "--changed-file",
                "api/users.py",
                "--json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["result"], "missing-docs")
        self.assertEqual(payload["missing_categories"], ["api"])
        self.assertEqual(payload["categories"][0]["category"], "api")

    def test_install_rejects_unknown_preset(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--preset", "missing"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unknown preset: missing", result.stderr)

    def test_install_rejects_unknown_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            (target / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(INSTALL), str(target), "--profile", "missing"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unknown profile: missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
