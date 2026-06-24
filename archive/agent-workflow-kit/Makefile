BUMP ?= patch
RECEIPT ?=
CONTEXT_ROOT ?= .
RISK_PATHS ?=
MODE ?= bootstrap
KIT ?=
WORKFLOW ?=
AGENT ?= manual
AMP ?= amp
TASK ?=
TITLE ?=
SCOPE ?=
RESEARCH_TITLE ?=
RESEARCH_QUESTION ?=
RESEARCH_CONTEXT ?=
RESEARCH_SOURCES ?= github,arxiv,hacker-news,official-docs
RESEARCH_SOURCE ?= github
RESEARCH_OUTPUT ?= backlog
RESEARCH_QUERY ?=
RESEARCH_SCOPE ?=
BASE_REF ?= HEAD
WORKTREE_ROOT ?=
OVERLAP ?= warn
ALLOW_DIRTY ?= 0
STATE_LEDGER_JSON ?= 0
BRANCH_READY_JSON ?= 0
BRANCH_READY_BASE_REF ?=
BRANCH_READY_HEAD_REF ?= HEAD
BRANCH_READY_TARGET_REF ?=
BRANCH_READY_CHECKS_JSON ?=
BRANCH_READY_RECEIPT ?=
BRANCH_READY_REVIEW_DISPOSITION_JSON ?=
BRANCH_READY_NO_DOCS_NEEDED ?=
BRANCH_READY_TASK_RECEIPT ?=
PREFLIGHT_JSON ?= 0
PREFLIGHT_STRICT ?= 0
PREFLIGHT_WRITE_SIDECAR ?= 0
SELF_HEAL_JSON ?= 0
SELF_HEAL_APPLY ?= 0
SELF_HEAL_ALLOW_PATHS ?=
AUTOMATION_HANDOFF_JSON ?= 0
AUTOMATION_HANDOFF_MODE ?= patch
AUTOMATION_HANDOFF_LABEL ?=
AUTOMATION_HANDOFF_ORIGINAL_ROOT ?=
AUTOMATION_HANDOFF_ORIGINAL_BASELINE ?=
AUTOMATION_HANDOFF_CAPTURE_ORIGINAL_BASELINE ?= 0
AUTOMATION_HANDOFF_ALLOW_PRIMARY ?= 0
AUTOMATION_HANDOFF_ALLOW_DIRTY_ORIGINAL ?= 0
AUTOMATION_HANDOFF_ALLOW_ORIGINAL_DRIFT ?= 0
AUTOMATION_HANDOFF_DRY_RUN ?= 0
TASK_READY_JSON ?= 0
TASK_READY_RECEIPT ?=
TASK_STATUS_JSON ?= 0
TASK_STATUS_STRICT ?= 0
TASK_STATUS_INCLUDE_CLOSED ?= 0
TASK_CLEANUP_JSON ?= 0
TASK_CLEANUP_APPLY ?= 0
TASK_CLEANUP_MOVE_NESTED ?= 0
TASK_CLEANUP_PRUNE ?= 0
TASK_CLOSEOUT_JSON ?= 0
TASK_CLOSEOUT_APPLY ?= 0
TASK_CLOSEOUT_PRUNE ?= 0
TASK_CLOSEOUT_KEEP ?=
TASK_CLOSEOUT_OLDER_THAN_DAYS ?=
TASK_CLOSEOUT_ALLOW_NO_RECEIPT ?= 0
BACKLOG_ID ?=
BACKLOG_JSON ?= 0
TASK_LIFECYCLE_JSON ?= 0
TASK_LIFECYCLE_APPLY ?= 0
TASK_FINALIZE_ACTION ?= finish
TASK_FINALIZE_JSON ?= 0
TASK_FINALIZE_SKIP_READY ?= 0
TASK_FINALIZE_CLOSEOUT_APPLY ?= 0
TASK_OWNER ?=
TASK_OWNER_LABEL ?=
TASK_SESSION_ID ?=
TASK_THREAD_ID ?=
TASK_AUTOMATION_ID ?=
TASK_REASON ?=
TASK_RECEIPT ?=
TASK_LEASE_MINUTES ?= 240
DOCS_FRESHNESS_JSON ?= 0
DOCS_REQUIRE_SEMANTIC ?= 0
DOCS_SEMANTIC_RECEIPT ?=
DOCS_AS_TESTS_JSON ?= 0
DOCS_AS_TESTS_CONFIG ?= .agent-workflows/docs-as-tests.json
DOCS_EXPLAIN_JSON ?= 0
DOCS_EXPLAIN_CHECK ?= 0
DOCS_EXPLAIN_QUESTION ?=
DOCS_EXPLAIN_FOCUS ?=
DOCS_EXPLAIN_PATH ?=
DOCS_PROPOSE_JSON ?= 0
DOCS_PROPOSE_WRITE_SIDECAR ?= 1
CHANGELOG_UPDATE_JSON ?= 0
CHANGELOG_UPDATE_CHECK ?= 0
CHANGELOG_UPDATE_BUMP ?=
CHANGELOG_UPDATE_VERSION ?=
CHANGELOG_UPDATE_SECTION ?=
CHANGELOG_UPDATE_SUMMARY ?=
GOAL_CHECK_JSON ?= 0
GOAL_CHECK_MODE ?= working-tree
GOAL_CHECK_CONFIG ?= .agent-workflows/area-contracts.json
CONTEXT_BUNDLE_JSON ?= 0
CONTEXT_BUNDLE_MODE ?= working-tree
CONTEXT_BUNDLE_MAX_FILES ?= 25
INSTRUCTION_DIET_JSON ?= 0
INSTRUCTION_DIET_STRICT_PATHS ?= 1
TOKEN_BUDGET_JSON ?= 0
TOKEN_BUDGET_STRICT ?= 0
STACK_UPDATE_JSON ?= 0
STACK_UPDATE_FORCE_MANAGED ?= 0
SKILL_PACK_OUTPUT ?=
SKILL_PACK_SKILLS ?=

.PHONY: help workflow-help stack-status validate prompt-adapters-export prompt-adapters-check skill-pack-export skill-pack-check skill-pack-list backlog-split backlog-split-check receipt-summary context-packet review-risk self-check docs-lint docs-build docs-generate docs-freshness docs-as-tests docs-check goal-check backlog-status backlog-check agent-next agent-context-bundle agent-state-ledger agent-branch-readiness agent-preflight agent-doctor agent-self-heal agent-start agent-task-prepare agent-task-ready agent-automation-handoff agent-task-status agent-task-cleanup agent-task-closeout agent-task-finalize agent-task-finish agent-task-block agent-task-abandon agent-task-heartbeat agent-task-link-receipt agent-task-prune agent-task-packet-from-backlog agent-run-review agent-research-plan agent-research-run agent-research-synthesize agent-research-to-task-packet agent-receipt-verify agent-docs-lint agent-instruction-diet agent-docs-localize agent-docs-explain agent-docs-propose agent-changelog-update agent-token-budget agent-review agent-learn agent-review-risk agent-task-packet agent-test-first agent-verify kit-status kit-explain kit-migrate-config kit-update kit-refresh kit-update-stack kit-refresh-stack version-status version-check version-bump version-commit-check install-git-hooks

help: workflow-help

workflow-help:
	@printf "%s\n" \
		"agent-workflow-kit legacy checkout working rhythm" \
		"" \
		"1. Orient" \
		"   make agent-start" \
		"   make kit-status" \
		"   make stack-status KIT=/path/to/repo-contract-kit   # cross-repo coordination" \
		"   make agent-next" \
		"2. Review" \
		"   make agent-run-review AGENT=manual" \
		"3. Scope" \
		"   make agent-task-packet" \
		"   make agent-task-packet-from-backlog BACKLOG_ID=<id>" \
		"4. Execute" \
		"   make agent-task-status" \
		"   make agent-task-prepare TASK=<id> SCOPE=<paths>   # installed target repos" \
		"   make agent-task-heartbeat TASK=<id>" \
		"   make agent-task-finish TASK=<id> TASK_RECEIPT=<path>" \
			"   make agent-task-closeout" \
			"   make agent-token-budget" \
			"   make skill-pack-export" \
			"   make agent-verify" \
			"   make kit-update-stack" \
		"" \
		"Read docs/agent-workflow-stack.md for repo ownership and docs/working-rhythm.md for common paths."

stack-status:
	@if test -n "$(KIT)"; then \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/stack_status.py --kit "$(KIT)"; \
	else \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/stack_status.py; \
	fi

validate:
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/export_workflow_adapters.py --check
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/split_backlog_by_repo.py --check
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_agentic_regression_artifacts.py
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_agentic_regression_fixtures.py
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_prompt_regression_fixtures.py

prompt-adapters-export:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/export_workflow_adapters.py

prompt-adapters-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/export_workflow_adapters.py --check

skill-pack-export:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/export_codex_skill_pack.py \
		$(if $(SKILL_PACK_OUTPUT),--output "$(SKILL_PACK_OUTPUT)",) \
		$(foreach skill,$(SKILL_PACK_SKILLS),--skill "$(skill)")

skill-pack-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/export_codex_skill_pack.py --check \
		$(if $(SKILL_PACK_OUTPUT),--output "$(SKILL_PACK_OUTPUT)",) \
		$(foreach skill,$(SKILL_PACK_SKILLS),--skill "$(skill)")

skill-pack-list:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/export_codex_skill_pack.py --list \
		$(foreach skill,$(SKILL_PACK_SKILLS),--skill "$(skill)")

backlog-split:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/split_backlog_by_repo.py

backlog-split-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/split_backlog_by_repo.py --check

receipt-summary:
	@test -n "$(RECEIPT)" || (echo "Set RECEIPT=/path/to/receipt.json"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/render_session_receipt_summary.py "$(RECEIPT)"

context-packet:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_context_packet.py --root "$(CONTEXT_ROOT)"

review-risk:
	@if [ -n "$(RISK_PATHS)" ]; then \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/classify_review_risk.py $(RISK_PATHS); \
	else \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/classify_review_risk.py --working-tree; \
	fi

self-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_self_dogfood_boundary.py

docs-lint:
	@echo "Running basic docs lint checks..."
	@test -f AGENTS.md || (echo "Missing AGENTS.md" && exit 1)
	@test -f REVIEW.md || (echo "Missing REVIEW.md" && exit 1)
	@test -f doc-contract.json || (echo "Missing doc-contract.json" && exit 1)
	@test -f docs/documentation-contract.md || (echo "Missing docs/documentation-contract.md" && exit 1)
	@test -d docs/adr || (echo "Missing docs/adr/" && exit 1)
	@echo "Basic docs lint checks passed."

docs-build:
	@echo "No docs site configured yet. Skipping build."

docs-generate:
	@echo "No generated docs configured yet. Skipping generation."

docs-freshness:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_docs_freshness.py \
		$(if $(filter 1 true yes,$(DOCS_FRESHNESS_JSON)),--json,) \
		$(if $(filter 1 true yes,$(DOCS_REQUIRE_SEMANTIC)),--require-semantic-receipt,) \
		$(if $(DOCS_SEMANTIC_RECEIPT),--semantic-receipt "$(DOCS_SEMANTIC_RECEIPT)",)

docs-as-tests:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_docs_as_tests.py \
		--repo "$(CURDIR)" \
		--config "$(DOCS_AS_TESTS_CONFIG)" \
		$(if $(filter 1 true yes,$(DOCS_AS_TESTS_JSON)),--json,)

docs-check: docs-lint docs-build docs-generate docs-freshness
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_doc_impact.py

goal-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py goal-check --repo "$(CURDIR)" \
		--config "$(GOAL_CHECK_CONFIG)" \
		$(if $(filter staged,$(GOAL_CHECK_MODE)),--staged,) \
		$(if $(filter working-tree,$(GOAL_CHECK_MODE)),--working-tree,) \
		$(if $(filter 1 true yes,$(GOAL_CHECK_JSON)),--json,)

backlog-status:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py backlog-status --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(BACKLOG_JSON)),--json,)

backlog-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py backlog-check --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(BACKLOG_JSON)),--json,)

agent-next:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py agent-next --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(BACKLOG_JSON)),--json,)

agent-context-bundle:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py agent-context-bundle --repo "$(CURDIR)" \
		--mode "$(CONTEXT_BUNDLE_MODE)" \
		--max-files "$(CONTEXT_BUNDLE_MAX_FILES)" \
		$(if $(filter 1 true yes,$(CONTEXT_BUNDLE_JSON)),--json,)

agent-state-ledger:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py agent-state-ledger --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(STATE_LEDGER_JSON)),--json,)

agent-branch-readiness:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py branch-readiness --repo "$(CURDIR)" \
		$(if $(BRANCH_READY_BASE_REF),--base-ref "$(BRANCH_READY_BASE_REF)",) \
		$(if $(BRANCH_READY_HEAD_REF),--head-ref "$(BRANCH_READY_HEAD_REF)",) \
		$(if $(BRANCH_READY_TARGET_REF),--target-ref "$(BRANCH_READY_TARGET_REF)",) \
		$(if $(BRANCH_READY_CHECKS_JSON),--checks-json "$(BRANCH_READY_CHECKS_JSON)",) \
		$(if $(BRANCH_READY_RECEIPT),--receipt "$(BRANCH_READY_RECEIPT)",) \
		$(if $(BRANCH_READY_REVIEW_DISPOSITION_JSON),--review-disposition-json "$(BRANCH_READY_REVIEW_DISPOSITION_JSON)",) \
		$(if $(BRANCH_READY_NO_DOCS_NEEDED),--no-docs-needed "$(BRANCH_READY_NO_DOCS_NEEDED)",) \
		$(if $(TASK),--task "$(TASK)",) \
		$(if $(BRANCH_READY_TASK_RECEIPT),--task-receipt "$(BRANCH_READY_TASK_RECEIPT)",) \
		$(if $(filter 1 true yes,$(BRANCH_READY_JSON)),--json,)

agent-preflight:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py agent-preflight --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(PREFLIGHT_JSON)),--json,) \
		$(if $(filter 1 true yes,$(PREFLIGHT_STRICT)),--strict,) \
		$(if $(filter 1 true yes,$(PREFLIGHT_WRITE_SIDECAR)),--write-sidecar,)

agent-doctor:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py agent-doctor --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(PREFLIGHT_JSON)),--json,) \
		$(if $(filter 1 true yes,$(PREFLIGHT_STRICT)),--strict,) \
		$(if $(filter 1 true yes,$(PREFLIGHT_WRITE_SIDECAR)),--write-sidecar,)

agent-self-heal:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py agent-self-heal --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(SELF_HEAL_JSON)),--json,) \
		$(if $(filter 1 true yes,$(SELF_HEAL_APPLY)),--apply,) \
		$(if $(SELF_HEAL_ALLOW_PATHS),--allow-path "$(SELF_HEAL_ALLOW_PATHS)",)

agent-start:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_start.py --mode "$(MODE)"

agent-task-prepare:
	@test -n "$(TASK)" || (echo "Set TASK=<id>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_prepare.py \
		--task "$(TASK)" \
		--title "$(TITLE)" \
		--scope "$(SCOPE)" \
		--mode "$(MODE)" \
		--base-ref "$(BASE_REF)" \
		--worktree-root "$(WORKTREE_ROOT)" \
		--overlap-policy "$(OVERLAP)" \
		--owner "$(TASK_OWNER)" \
		--session-id "$(TASK_SESSION_ID)" \
		--lease-minutes "$(TASK_LEASE_MINUTES)" \
		$(if $(filter 1 true yes,$(ALLOW_DIRTY)),--allow-dirty,)

agent-task-status:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_status.py \
		$(if $(filter 1 true yes,$(TASK_STATUS_JSON)),--json,) \
		$(if $(filter 1 true yes,$(TASK_STATUS_STRICT)),--strict,) \
		$(if $(filter 1 true yes,$(TASK_STATUS_INCLUDE_CLOSED)),--include-closed,)

agent-task-ready:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_ready.py \
		$(if $(TASK),--task "$(TASK)",) \
		$(if $(BASE_REF),--base-ref "$(BASE_REF)",) \
		$(if $(TASK_READY_RECEIPT),--receipt "$(TASK_READY_RECEIPT)",) \
		$(if $(filter 1 true yes,$(TASK_READY_JSON)),--json,)

agent-automation-handoff:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py automation-handoff \
		--repo "$(CURDIR)" \
		--mode "$(AUTOMATION_HANDOFF_MODE)" \
		$(if $(AUTOMATION_HANDOFF_LABEL),--label "$(AUTOMATION_HANDOFF_LABEL)",) \
		$(if $(AUTOMATION_HANDOFF_ORIGINAL_ROOT),--original-root "$(AUTOMATION_HANDOFF_ORIGINAL_ROOT)",) \
		$(if $(AUTOMATION_HANDOFF_ORIGINAL_BASELINE),--original-baseline "$(AUTOMATION_HANDOFF_ORIGINAL_BASELINE)",) \
		$(if $(filter 1 true yes,$(AUTOMATION_HANDOFF_CAPTURE_ORIGINAL_BASELINE)),--capture-original-baseline,) \
		$(if $(filter 1 true yes,$(AUTOMATION_HANDOFF_ALLOW_PRIMARY)),--allow-primary-checkout,) \
		$(if $(filter 1 true yes,$(AUTOMATION_HANDOFF_ALLOW_DIRTY_ORIGINAL)),--allow-dirty-original,) \
		$(if $(filter 1 true yes,$(AUTOMATION_HANDOFF_ALLOW_ORIGINAL_DRIFT)),--allow-original-baseline-drift,) \
		$(if $(filter 1 true yes,$(AUTOMATION_HANDOFF_DRY_RUN)),--dry-run,) \
		$(if $(filter 1 true yes,$(AUTOMATION_HANDOFF_JSON)),--json,)

agent-task-cleanup:
	@if test -f scripts/agent_task_cleanup.py; then \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_cleanup.py \
			$(if $(filter 1 true yes,$(TASK_CLEANUP_JSON)),--json,) \
			$(if $(filter 1 true yes,$(TASK_CLEANUP_APPLY)),--apply,) \
			$(if $(filter 1 true yes,$(TASK_CLEANUP_MOVE_NESTED)),--move-nested,) \
			$(if $(filter 1 true yes,$(TASK_CLEANUP_PRUNE)),--prune,); \
	else \
		echo "Use workflows/prompts/task-worktree-cleanup.md, or update repo-contract-kit to install scripts/agent_task_cleanup.py."; \
	fi

agent-task-closeout:
	@if test -f scripts/agent_task_cleanup.py; then \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_cleanup.py --closeout \
			$(if $(filter 1 true yes,$(TASK_CLOSEOUT_JSON)),--json,) \
			$(if $(filter 1 true yes,$(TASK_CLOSEOUT_APPLY)),--apply,) \
			$(if $(filter 1 true yes,$(TASK_CLOSEOUT_PRUNE)),--prune,) \
			$(if $(TASK_CLOSEOUT_KEEP),--keep-count "$(TASK_CLOSEOUT_KEEP)",) \
			$(if $(TASK_CLOSEOUT_OLDER_THAN_DAYS),--older-than-days "$(TASK_CLOSEOUT_OLDER_THAN_DAYS)",) \
			$(if $(filter 1 true yes,$(TASK_CLOSEOUT_ALLOW_NO_RECEIPT)),--allow-no-receipt,); \
	else \
		echo "Use workflows/prompts/task-worktree-cleanup.md, or update repo-contract-kit to install scripts/agent_task_cleanup.py."; \
	fi

agent-task-finalize:
	@test -n "$(TASK)" || (echo "Set TASK=<id>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_finalize.py \
		--task "$(TASK)" \
		--action "$(TASK_FINALIZE_ACTION)" \
		$(if $(TASK_RECEIPT),--receipt "$(TASK_RECEIPT)",) \
		$(if $(BASE_REF),--base-ref "$(BASE_REF)",) \
		$(if $(TASK_REASON),--reason "$(TASK_REASON)",) \
		$(if $(TASK_OWNER),--owner "$(TASK_OWNER)",) \
		$(if $(TASK_OWNER_LABEL),--owner-label "$(TASK_OWNER_LABEL)",) \
		$(if $(TASK_SESSION_ID),--session-id "$(TASK_SESSION_ID)",) \
		$(if $(TASK_THREAD_ID),--thread-id "$(TASK_THREAD_ID)",) \
		$(if $(TASK_AUTOMATION_ID),--automation-id "$(TASK_AUTOMATION_ID)",) \
		$(if $(filter 1 true yes,$(TASK_FINALIZE_JSON)),--json,) \
		$(if $(filter 1 true yes,$(TASK_FINALIZE_SKIP_READY)),--skip-ready,) \
		$(if $(filter 1 true yes,$(TASK_FINALIZE_CLOSEOUT_APPLY)),--closeout-apply,)

agent-task-finish:
	@test -n "$(TASK)" || (echo "Set TASK=<id>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_lifecycle.py finish --task "$(TASK)" \
		--reason "$(TASK_REASON)" --receipt "$(TASK_RECEIPT)" --owner "$(TASK_OWNER)" --session-id "$(TASK_SESSION_ID)" \
		$(if $(filter 1 true yes,$(TASK_LIFECYCLE_JSON)),--json,)

agent-task-block:
	@test -n "$(TASK)" || (echo "Set TASK=<id>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_lifecycle.py block --task "$(TASK)" \
		--reason "$(TASK_REASON)" --owner "$(TASK_OWNER)" --session-id "$(TASK_SESSION_ID)" \
		$(if $(filter 1 true yes,$(TASK_LIFECYCLE_JSON)),--json,)

agent-task-abandon:
	@test -n "$(TASK)" || (echo "Set TASK=<id>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_lifecycle.py abandon --task "$(TASK)" \
		--reason "$(TASK_REASON)" --owner "$(TASK_OWNER)" --session-id "$(TASK_SESSION_ID)" \
		$(if $(filter 1 true yes,$(TASK_LIFECYCLE_JSON)),--json,)

agent-task-heartbeat:
	@test -n "$(TASK)" || (echo "Set TASK=<id>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_lifecycle.py heartbeat --task "$(TASK)" \
		--reason "$(TASK_REASON)" --owner "$(TASK_OWNER)" --session-id "$(TASK_SESSION_ID)" \
		--lease-minutes "$(TASK_LEASE_MINUTES)" \
		$(if $(filter 1 true yes,$(TASK_LIFECYCLE_JSON)),--json,)

agent-task-link-receipt:
	@test -n "$(TASK)" || (echo "Set TASK=<id>"; exit 1)
	@test -n "$(TASK_RECEIPT)" || (echo "Set TASK_RECEIPT=<path>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_lifecycle.py link-receipt --task "$(TASK)" \
		--receipt "$(TASK_RECEIPT)" --reason "$(TASK_REASON)" --owner "$(TASK_OWNER)" --session-id "$(TASK_SESSION_ID)" \
		$(if $(filter 1 true yes,$(TASK_LIFECYCLE_JSON)),--json,)

agent-task-prune:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_task_lifecycle.py prune \
		$(if $(filter 1 true yes,$(TASK_LIFECYCLE_APPLY)),--apply,) \
		$(if $(filter 1 true yes,$(TASK_LIFECYCLE_JSON)),--json,)

agent-task-packet-from-backlog:
	@test -n "$(BACKLOG_ID)" || (echo "Set BACKLOG_ID=<id>"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py agent-task-packet-from-backlog \
		--repo "$(CURDIR)" \
		--backlog-id "$(BACKLOG_ID)" \
		--mode "$(MODE)" \
		$(if $(filter 1 true yes,$(BACKLOG_JSON)),--json,)

agent-run-review:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_review_run.py --mode "$(MODE)" --agent "$(AGENT)" --amp-command "$(AMP)"

agent-research-plan:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_research.py plan \
		--title "$(RESEARCH_TITLE)" \
		--question "$(RESEARCH_QUESTION)" \
		--context "$(RESEARCH_CONTEXT)" \
		--sources "$(RESEARCH_SOURCES)" \
		--output "$(RESEARCH_OUTPUT)" \
		--query "$(RESEARCH_QUERY)" \
		--scope "$(RESEARCH_SCOPE)"

agent-research-run:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_research.py run \
		--source "$(RESEARCH_SOURCE)" \
		--query "$(RESEARCH_QUERY)" \
		--scope "$(RESEARCH_SCOPE)"

agent-research-synthesize:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_research.py synthesize

agent-research-to-task-packet:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/agent_research.py to-task-packet

agent-receipt-verify:
	@if test -n "$(RECEIPT)"; then \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_agent_receipt.py --strict --receipt "$(RECEIPT)"; \
	else \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_agent_receipt.py --strict; \
	fi

agent-docs-lint:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/lint_agent_docs.py --strict-paths

agent-instruction-diet:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py instruction-diet --repo "$(CURDIR)" \
		$(if $(filter 1 true yes,$(INSTRUCTION_DIET_STRICT_PATHS)),--strict-paths,) \
		$(if $(filter 1 true yes,$(INSTRUCTION_DIET_JSON)),--json,)

agent-docs-localize:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/localize_doc_impact.py --working-tree --json

agent-docs-explain:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py docs-explain \
		--repo "$(CURDIR)" \
		$(if $(DOCS_EXPLAIN_QUESTION),--question "$(DOCS_EXPLAIN_QUESTION)",) \
		$(if $(DOCS_EXPLAIN_FOCUS),--focus "$(DOCS_EXPLAIN_FOCUS)",) \
		$(if $(DOCS_EXPLAIN_PATH),--path "$(DOCS_EXPLAIN_PATH)",) \
		$(if $(filter 1 true yes,$(DOCS_EXPLAIN_CHECK)),--check,) \
		$(if $(filter 1 true yes,$(DOCS_EXPLAIN_JSON)),--json,)

agent-docs-propose:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py docs-propose \
		--repo "$(CURDIR)" \
		--working-tree \
		$(if $(filter 1 true yes,$(DOCS_PROPOSE_WRITE_SIDECAR)),--write-sidecar,) \
		$(if $(filter 1 true yes,$(DOCS_PROPOSE_JSON)),--json,)

agent-changelog-update:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/repo_contract_kit.py changelog-update \
		--repo "$(CURDIR)" \
		--working-tree \
		$(if $(filter 1 true yes,$(CHANGELOG_UPDATE_CHECK)),--check,) \
		$(if $(CHANGELOG_UPDATE_BUMP),--bump "$(CHANGELOG_UPDATE_BUMP)",) \
		$(if $(CHANGELOG_UPDATE_VERSION),--version "$(CHANGELOG_UPDATE_VERSION)",) \
		$(if $(CHANGELOG_UPDATE_SECTION),--section "$(CHANGELOG_UPDATE_SECTION)",) \
		$(if $(CHANGELOG_UPDATE_SUMMARY),--summary "$(CHANGELOG_UPDATE_SUMMARY)",) \
		$(if $(filter 1 true yes,$(CHANGELOG_UPDATE_JSON)),--json,)

agent-token-budget:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_token_budget.py \
		$(if $(filter 1 true yes,$(TOKEN_BUDGET_JSON)),--json,) \
		$(if $(filter 1 true yes,$(TOKEN_BUDGET_STRICT)),--strict,)

agent-review:
	@if test -f .agent-workflows/repo-review.md; then \
		printf "%s\n" \
			"Read AGENTS.md, REVIEW.md, and .agent-workflows/README.md." \
			"Then follow .agent-workflows/repo-review.md in bootstrap mode." \
			"Use the companion repo-contract-kit repo's workflows directory for new workflow-source edits." \
			"Treat workflows/prompts/ as legacy/archive material and .codex/prompts/ as its generated Codex mirror." \
			"Start by running make agent-verify and make agent-docs-localize." \
			"Optionally run make agent-run-review AGENT=manual to generate review artifacts." \
			"Produce a findings backlog before editing code."; \
	else \
		echo "Missing local review workflow; reinstall the local-agentic profile."; exit 1; \
	fi

agent-learn:
	@test -f .codex/prompts/codebase-learning-comments.md || (echo "Missing .codex/prompts/codebase-learning-comments.md; run make prompt-adapters-export." && exit 1)
	@echo "For new workflow-source edits, use the companion repo-contract-kit repo's workflows directory. This checkout's workflows/prompts/codebase-learning-comments.md is legacy/archive material; .codex/prompts/codebase-learning-comments.md is its generated Codex mirror."

agent-review-risk:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/classify_review_risk.py --working-tree

agent-task-packet:
	@test -f .codex/prompts/task-packet.md || (echo "Missing .codex/prompts/task-packet.md; run make prompt-adapters-export." && exit 1)
	@echo "For new workflow-source edits, use the companion repo-contract-kit repo's workflows directory. This checkout's workflows/prompts/task-packet.md is legacy/archive material; use make agent-task-packet-from-backlog for current backlog handoff."

agent-test-first:
	@test -f .codex/prompts/tdd/README.md || (echo "Missing .codex/prompts/tdd/README.md; run make prompt-adapters-export." && exit 1)
	@echo "For new workflow-source edits, use the companion repo-contract-kit repo's workflows directory. This checkout's workflows/prompts/tdd/README.md is legacy/archive material."

agent-verify: self-check docs-check agent-docs-lint agent-token-budget validate version-check
	@echo "Agent verification checks passed."

kit-status:
	@if test -n "$(KIT)"; then \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_status.py --kit "$(KIT)"; \
	else \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_status.py; \
	fi

kit-explain:
	@if test -n "$(KIT)"; then \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_status.py --explain --kit "$(KIT)"; \
	else \
		PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_status.py --explain; \
	fi

kit-migrate-config:
	@test -n "$(KIT)" || (echo "Set KIT=/path/to/repo-contract-kit"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 "$(KIT)/scripts/update.py" "$(CURDIR)" --apply --metadata-only

kit-update:
	@test -n "$(KIT)" || (echo "Set KIT=/path/to/repo-contract-kit"; exit 1)
	@PYTHONDONTWRITEBYTECODE=1 python3 "$(KIT)/scripts/update.py" "$(CURDIR)" --apply

kit-refresh:
	@test -n "$(KIT)" || (echo "Set KIT=/path/to/repo-contract-kit"; exit 1)
	@git -C "$(KIT)" rev-parse --is-inside-work-tree >/dev/null 2>&1 || (echo "KIT is not a git checkout: $(KIT)"; exit 1)
	@test -f "$(KIT)/scripts/update.py" || (echo "KIT does not look like repo-contract-kit: $(KIT)"; exit 1)
	@test -z "$$(git -C "$(KIT)" status --porcelain)" || (echo "Kit checkout has local changes; commit, stash, or use kit-update explicitly: $(KIT)"; exit 1)
	@git -C "$(KIT)" pull --ff-only
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_status.py --kit "$(KIT)"
	@PYTHONDONTWRITEBYTECODE=1 python3 "$(KIT)/scripts/update.py" "$(CURDIR)" --apply

kit-update-stack:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_update_stack.py --target "$(CURDIR)" \
		$(if $(KIT),--kit "$(KIT)",) \
		$(if $(WORKFLOW),--workflow "$(WORKFLOW)",) \
		$(if $(filter 1 true yes,$(STACK_UPDATE_JSON)),--json,) \
		$(if $(filter 1 true yes,$(STACK_UPDATE_FORCE_MANAGED)),--force-managed,)

kit-refresh-stack:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/kit_update_stack.py --target "$(CURDIR)" --refresh \
		$(if $(KIT),--kit "$(KIT)",) \
		$(if $(WORKFLOW),--workflow "$(WORKFLOW)",) \
		$(if $(filter 1 true yes,$(STACK_UPDATE_JSON)),--json,) \
		$(if $(filter 1 true yes,$(STACK_UPDATE_FORCE_MANAGED)),--force-managed,)

version-status:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py status

version-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py check

version-bump:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/version.py bump --bump "$(BUMP)"

version-commit-check:
	@PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_versioning.py --staged

install-git-hooks:
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-commit
	@echo "Git hooks installed from .githooks"
