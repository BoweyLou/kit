.PHONY: help workflow-help test cli-ux-fixtures docs-freshness docs-check version-check workflow-source-check workflow-source-export macos-build macos-test macos-dmg macos-package-check

help: workflow-help

workflow-help:
	@printf "%s\n" \
		"kit maintainer commands" \
		"" \
		"Global install surface:" \
		"   sh install.sh" \
		"   kit" \
		"   kit start" \
		"   kit options" \
		"   kit update --global" \
		"   kit setup" \
		"   kit status" \
		"   kit update --dry-run" \
		"   kit target repair-source-clone" \
		"   kit update" \
		"   kit doctor" \
		"" \
		"Source-checkout fallback CLI:" \
		"   ./scripts/repo_contract_kit.py version --json" \
		"   ./scripts/repo_contract_kit.py start --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py command-map --json" \
		"   ./scripts/repo_contract_kit.py agent-context --json" \
		"   ./scripts/repo_contract_kit.py orient --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py status --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py backlog-status --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py agent-next --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py instruction-diet --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py agent-preflight --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py branch-readiness --repo /path/to/repo --json" \
		"   ./scripts/repo_contract_kit.py automation-handoff --repo /path/to/worktree --json" \
		"   ./scripts/repo_contract_kit.py doc-impact --repo /path/to/repo --working-tree --json" \
		"   ./scripts/repo_contract_kit.py update-plan --repo /path/to/repo --json" \
		"   Read-only JSON reports sidecar state under XDG_STATE_HOME or ~/.local/state." \
		"" \
		"Install into a target repo:" \
		"   kit setup --repo /path/to/target/repo --preset agentic" \
		"   python3 scripts/install.py /path/to/target/repo --preset agentic" \
		"" \
		"Cross-repo map:" \
		"   docs/agent-workflow-stack.md" \
		"" \
		"In the installed target repo, use the four-move rhythm:" \
		"1. Orient" \
		"   make agent-start" \
		"   make kit-status" \
		"2. Review" \
		"   make agent-run-review AGENT=manual" \
		"3. Scope" \
		"   make agent-task-packet" \
		"4. Execute" \
		"   make agent-task-status" \
		"   make agent-preflight" \
		"   make agent-task-prepare TASK=<id> SCOPE=<paths>" \
		"   make agent-task-ready" \
		"   make agent-branch-readiness" \
		"   make agent-automation-handoff" \
		"   make agent-task-cleanup" \
		"   make agent-task-closeout" \
		"   make agent-verify" \
		"   kit status" \
		"   kit update --dry-run" \
		"   kit update" \
		"   kit doctor" \
		"" \
		"Maintainer checks:" \
		"   make workflow-source-check" \
		"   make workflow-source-export" \
		"   make test" \
		"   make cli-ux-fixtures" \
		"   make docs-freshness" \
		"   make docs-check" \
		"   make version-check" \
		"" \
		"Optional macOS companion:" \
		"   make macos-build" \
		"   make macos-test" \
		"   make macos-dmg"

test:
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

cli-ux-fixtures:
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_cli_ux_fixtures

workflow-source-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_workflow_source.py

workflow-source-export:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_workflow_source.py --write

docs-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_doc_impact.py --working-tree

docs-freshness:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_docs_freshness.py
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py cli-reference --check docs/cli-reference.md

version-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py check

macos-build:
	./script/build_macos_app.sh

macos-test:
	swift build --package-path macos/KitCompanion

macos-dmg:
	./script/package_macos_dmg.sh

macos-package-check:
	codesign --verify --deep --strict --verbose=2 dist/KitCompanion.app
	codesign -dvvv --entitlements :- dist/KitCompanion.app
	spctl -a -vv --type execute dist/KitCompanion.app || true
