# kit CLI Reference

Generated from `kit command-map --json`.
Do not edit command sections by hand; run `kit cli-reference --write docs/cli-reference.md`.

- Schema version: `1`
- Command count: `63`

## Commands

### kit agent-context

Alias for command-map focused on agent bootstrap.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `command_map_payload`
- Route role: `alias`
- Canonical command: `command-map`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-context --json`

Flags:

- `--json` - Emit machine-readable JSON.

### kit agent-context-bundle

Emit a compact deterministic startup and handoff context bundle.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `agent_context_bundle_payload`
- Route role: `agent-only`
- Canonical command: `agent-context-bundle`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-context-bundle --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--mode`
- `--format`
- `--max-files`
- `--max-open-items`
- `--max-tasks`
- `--max-token-files`
- `--max-warnings`
- `--max-commands`

### kit agent-doctor

Diagnose dirty-state startup blockers, task/worktree state, and safe recovery commands.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `agent_preflight_payload`
- Route role: `agent-only`
- Canonical command: `doctor`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-doctor --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--strict` - Exit non-zero when startup blockers are present.
- `--write-sidecar` - Write a preflight receipt under the repo sidecar.

### kit agent-next

Recommend the next backlog item after checking dirty state and active tasks.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `agent_next_payload`
- Route role: `agent-only`
- Canonical command: `agent-next`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-next --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.

### kit agent-preflight

Diagnose dirty-state startup blockers, task/worktree state, and safe recovery commands.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `agent_preflight_payload`
- Route role: `agent-only`
- Canonical command: `doctor`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-preflight --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--strict` - Exit non-zero when startup blockers are present.
- `--write-sidecar` - Write a preflight receipt under the repo sidecar.

### kit agent-self-heal

Preview or apply guarded generated-state repair and stale metadata quarantine.

- Audience: `agent`
- Mutation: `conditional-sidecar-repair`
- Target writes: `never`
- Sidecar writes: `with --apply`
- JSON: `yes`
- Output schema: `agent_self_heal_payload`
- Route role: `agent-only`
- Canonical command: `agent-self-heal`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-self-heal --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--apply` - Apply the planned generated-state repairs and write a sidecar receipt.
- `--allow-path` - Exact generated path allowed to remain dirty during apply. Can be repeated or comma-separated.

### kit agent-state-ledger

Emit a read-only ledger of dirty state, tasks, receipts, closeout state, and next safe commands.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `agent_state_ledger_payload`
- Route role: `agent-only`
- Canonical command: `agent-state-ledger`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-state-ledger --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--format`

### kit agent-task-packet-from-backlog

Emit a task packet scaffold for a selected backlog item.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `task_packet_payload`
- Route role: `agent-only`
- Canonical command: `agent-task-packet-from-backlog`
- Docs: `README.md#installed-commands`

Examples:

- `kit agent-task-packet-from-backlog --repo /path/to/repo --backlog-id AGW-107 --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--backlog-id`
- `--harness-mode` - Harness strictness: auto selects lite, standard, or release-gated from repo state.
- `--mode`
- `--story-type`
- `--story-actor`
- `--story-need`
- `--story-outcome`
- `--story-acceptance-summary`
- `--scope`
- `--protected-file`
- `--inspect-first`
- `--expected-output`
- `--non-goal`
- `--acceptance`
- `--validation`
- `--docs-impact`
- `--docs-path`
- `--docs-surface`
- `--release-metadata`
- `--generated-doc`
- `--contract-reference`
- `--docs-validation-command`
- `--risk`
- `--known-risk`
- `--stop-condition`
- `--approved`
- `--approver`
- `--approval-note`
- `--owner`
- `--dependency`
- `--next-packet-hint`
- `--write-sidecar` - Write the task packet under the repo sidecar.

### kit agent-tool-manifest

Export command-map-derived manifest metadata for local agents.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `agent_tool_manifest_payload`
- Route role: `agent-only`
- Canonical command: `agent-tool-manifest`
- Docs: `README.md#agent-tool-manifest, README.md#installed-commands`

Examples:

- `kit agent-tool-manifest --json`

Flags:

- `--json` - Emit machine-readable JSON.

### kit automation-handoff

Write an automation-safe backlog/research patch and receipt to the sidecar.

- Audience: `agent`
- Mutation: `writes-sidecar-by-default`
- Target writes: `never`
- Sidecar writes: `unless --dry-run`
- JSON: `yes`
- Output schema: `automation_handoff_payload`
- Route role: `agent-only`
- Canonical command: `automation-handoff`
- Docs: `README.md#installed-commands`

Examples:

- `kit automation-handoff --repo /path/to/repo --dry-run --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--mode`
- `--label` - Short label used in sidecar artifact filenames.
- `--allow-path` - Allowed changed path, glob, or directory prefix. Can be repeated.
- `--original-root` - Primary checkout that must remain clean.
- `--capture-original-baseline` - Write an original-checkout baseline receipt and exit.
- `--original-baseline` - Original-checkout baseline receipt path to compare before handoff.
- `--allow-dirty-original` - Do not block when --original-root is already dirty or baseline drift is accepted.
- `--allow-original-baseline-drift` - Do not block when the original checkout changed since --original-baseline.
- `--allow-primary-checkout` - Allow running from the primary checkout.
- `--allow-default-branch` - Allow branch mode on default branch names.
- `--no-require-linked-worktree` - Do not require a linked git worktree.
- `--dry-run` - Validate and report without writing sidecar artifacts.

### kit backlog-check

Validate the selected backlog source contract.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `backlog_report_payload`
- Route role: `agent-only`
- Canonical command: `backlog-check`
- Docs: `README.md#installed-commands`

Examples:

- `kit backlog-check --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--include-items` - Include all parsed backlog items in JSON output.

### kit backlog-status

Report the repo backlog source contract and open work.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `backlog_report_payload`
- Route role: `canonical`
- Canonical command: `backlog-status`
- Docs: `README.md#installed-commands`

Examples:

- `kit backlog-status --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--include-items` - Include all parsed backlog items in JSON output.

### kit branch-readiness

Aggregate local branch/PR readiness evidence without writes or hosted governance actions.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `branch_readiness_payload`
- Route role: `agent-only`
- Canonical command: `branch-readiness`
- Docs: `README.md#installed-commands`

Examples:

- `kit branch-readiness --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--base-ref` - Base ref for local branch diff and freshness.
- `--head-ref` - Head ref for local branch diff.
- `--target-ref` - Target ref metadata to report. Defaults to the resolved base ref.
- `--config` - Docs contract config path.
- `--no-docs-needed` - Explicit no-docs-needed reason to record for this readiness run.
- `--checks-json` - Local JSON export of required/advisory checks.
- `--receipt` - Local agent receipt JSON to validate. Can be repeated.
- `--review-disposition-json` - Local review disposition JSON to validate.
- `--task` - Prepared task id to aggregate through agent-task-ready when available.
- `--task-receipt` - Receipt path passed through to agent-task-ready.
- `--format`

### kit calibration

Report local harness outcome calibration evidence without writes.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `calibration_payload`
- Route role: `canonical`
- Canonical command: `calibration`
- Docs: `docs/lite-mode.md`

Examples:

- `kit calibration --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.

### kit changelog-update

Propose or check changelog work from docs-impact context without modifying target files.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `changelog_update_payload`
- Route role: `agent-only`
- Canonical command: `changelog-update`
- Docs: `README.md#installed-commands`

Examples:

- `kit changelog-update --repo /path/to/repo --working-tree --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--config`
- `--changed-file`
- `--staged`
- `--working-tree`
- `--docs-impact-json`
- `--summary`
- `--section`
- `--version`
- `--bump`
- `--check`
- `--format`

### kit cli-reference

Generate or check the command-map-derived CLI reference.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `with --write`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `cli_reference_payload`
- Route role: `canonical`
- Canonical command: `cli-reference`
- Docs: `docs/cli-reference.md, README.md#installed-commands`

Examples:

- `kit cli-reference`
- `kit cli-reference --check docs/cli-reference.md`
- `kit cli-reference --json`

Flags:

- `--format`
- `--json` - Emit machine-readable JSON.
- `--check` - Compare generated Markdown with a reference file.
- `--write` - Write generated Markdown to a reference file.

### kit closeout-plan

Plan whether current work can be claimed done from dirty state, task, receipt, and closeout evidence.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `closeout_plan_payload`
- Route role: `canonical`
- Canonical command: `closeout-plan`
- Docs: `docs/agent-guide.md, docs/cli-reference.md`

Examples:

- `kit closeout-plan --repo /path/to/repo --json`
- `kit closeout-plan --repo /path/to/repo --strict`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--format`
- `--strict` - Exit non-zero when completion cannot be claimed cleanly.

### kit command-map

Emit structured command metadata for humans and agents.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `command_map_payload`
- Route role: `canonical`
- Canonical command: `command-map`
- Docs: `README.md#installed-commands`

Examples:

- `kit command-map --json`

Flags:

- `--json` - Emit machine-readable JSON.

### kit completion

Print shell completion code for bash, zsh, or fish.

- Audience: `human`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `no`
- Output schema: `shell_completion_script`
- Route role: `canonical`
- Canonical command: `completion`
- Docs: `README.md#shell-completions`

Examples:

- `kit completion bash`
- `kit completion zsh`
- `kit completion fish`

### kit doc-impact

Evaluate documentation impact for changed files.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `doc_impact_payload`
- Route role: `canonical`
- Canonical command: `doc-impact`
- Docs: `README.md#installed-commands`

Examples:

- `kit doc-impact --repo /path/to/repo --working-tree --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--config`
- `--changed-file`
- `--staged`
- `--working-tree`
- `--no-docs-needed`
- `--format`

### kit docs-as-tests

Run explicit local docs-as-tests assertions without target writes or network calls.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `docs_as_tests_payload`
- Route role: `agent-only`
- Canonical command: `docs-as-tests`
- Docs: `README.md#installed-commands`

Examples:

- `kit docs-as-tests --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--config` - Config path relative to the repo root. Default: .agent-workflows/docs-as-tests.json.
- `--format`

### kit docs-explain

Explain local repository docs with deterministic source citations and no writes.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `docs_explain_payload`
- Route role: `canonical`
- Canonical command: `docs-explain`
- Docs: `README.md#installed-commands`

Examples:

- `kit docs-explain --repo /path/to/repo --question 'Can we waive docs?' --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--question` - Question to ground in local docs.
- `-q` - Question to ground in local docs.
- `--focus` - Topic to boost, for example docs-impact, waiver, docs-propose, add-docs, or changelog.
- `--path` - Repo-relative docs path, directory, or glob to scan.
- `--max-results`
- `--max-snippet-lines`
- `--check` - Exit non-zero when no matching docs are found.
- `--format`

### kit docs-propose

Write reviewable docs patch proposal artifacts without modifying the target repo.

- Audience: `agent`
- Mutation: `writes-sidecar`
- Target writes: `never`
- Sidecar writes: `always`
- JSON: `yes`
- Output schema: `docs_propose_payload`
- Route role: `agent-only`
- Canonical command: `docs-propose`
- Docs: `README.md#installed-commands`

Examples:

- `kit docs-propose --repo /path/to/repo --working-tree --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--config`
- `--changed-file`
- `--staged`
- `--working-tree`
- `--write-sidecar` - Write proposal JSON, Markdown, and patch artifacts under the repo sidecar.

### kit doctor

Diagnose dirty state and task blockers for the current repo.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `agent_preflight_payload`
- Route role: `canonical`
- Canonical command: `doctor`
- Docs: `README.md#installed-commands`

Examples:

- `kit doctor --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--strict` - Exit non-zero when startup blockers are present.
- `--write-sidecar` - Write a doctor receipt under the repo sidecar.

### kit feedback

Record or export local CLI friction feedback in the repo sidecar.

- Audience: `human, agent`
- Mutation: `writes-sidecar-when-recording`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `feedback_payload`
- Route role: `canonical`
- Canonical command: `feedback`
- Docs: `README.md#installed-commands`

Examples:

- `kit feedback --repo /path/to/repo --message 'status recovery was unclear'`
- `kit feedback --repo /path/to/repo --export-json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--message` - Feedback note to append to the local sidecar JSONL ledger.
- `--context-command` - Command or recovery path the feedback is about.
- `--last-error` - Optional last error text or parse failure context.
- `--source` - Who or what observed the friction.
- `--tag` - Feedback tag. Can be repeated or comma-separated.
- `--list` - List local feedback entries without writing sidecar state.
- `--export-json` - Export local feedback entries as JSON without writing sidecar state.
- `--limit` - Maximum entries to list or export. Use 0 for all entries.

### kit goal-check

Map changed files to local repo goal and area contracts.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `goal_check_payload`
- Route role: `agent-only`
- Canonical command: `goal-check`
- Docs: `README.md#installed-commands`

Examples:

- `kit goal-check --repo /path/to/repo --working-tree --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--config`
- `--changed-file`
- `--staged`
- `--working-tree`
- `--format`

### kit guide

Show the guided dashboard.

- Audience: `human`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `guide_payload`
- Route role: `canonical`
- Canonical command: `guide`
- Docs: `README.md#getting-started`

Examples:

- `kit`
- `kit guide --json`

Flags:

- `--json` - Emit machine-readable JSON.

### kit help

Show the human command guide.

- Audience: `human`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `no`
- Output schema: `text_command_guide`
- Route role: `canonical`
- Canonical command: `help`
- Docs: `README.md#installed-commands`

Examples:

- `kit help --all`

Flags:

- `--all` - Include advanced automation commands.

### kit install

Explicitly install kit files into a target repo.

- Audience: `agent`
- Mutation: `writes-target`
- Target writes: `writes-target`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `install_update_payload`
- Route role: `agent-only`
- Canonical command: `setup`
- Docs: `README.md#installed-commands`

Examples:

- `kit install --repo /path/to/repo --preset agentic --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--profile`
- `--profiles`
- `--preset`
- `--runtime-adapter`
- `--runtime-adapters`
- `--force`

### kit instruction-diet

Audit agent-facing instruction files and propose no-write offload targets.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `instruction_diet_payload`
- Route role: `canonical`
- Canonical command: `instruction-diet`
- Docs: `README.md#installed-commands`

Examples:

- `kit instruction-diet --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--file` - Specific instruction file to inspect.
- `--strict-paths` - Treat missing path references as strict evidence.
- `--budget-config` - Instruction budget config relative to the repo root.
- `--format`

### kit migrate-config

Explicitly migrate installed profile/config metadata schema without managed-file updates.

- Audience: `agent`
- Mutation: `writes-target-metadata`
- Target writes: `writes-target-metadata`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `install_update_payload`
- Route role: `compatibility`
- Canonical command: `update --metadata-only`
- Docs: `README.md#installed-commands`

Examples:

- `kit migrate-config --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--kit` - kit checkout to migrate from. Defaults to this checkout.

### kit mode-check

Select lite, standard, or release-gated harness mode without writes.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `harness_mode_selection_payload`
- Route role: `canonical`
- Canonical command: `mode-check`
- Docs: `docs/lite-mode.md`

Examples:

- `kit mode-check --repo /path/to/repo --json`
- `kit mode-check --repo /path/to/repo --mode release-gated --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--mode` - Requested harness mode. auto lets kit choose.

### kit onboarding-pr

Generate reviewable branch and PR instructions for installing repo-contract-kit.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `onboarding_pr_payload`
- Route role: `canonical`
- Canonical command: `onboarding-pr`
- Docs: `README.md#installed-commands`

Examples:

- `kit onboarding-pr --repo /path/to/repo --preset agentic --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--profile`
- `--profiles`
- `--preset`
- `--runtime-adapter`
- `--runtime-adapters`
- `--branch` - Onboarding branch name. Defaults to codex/kit-onboarding.
- `--base-ref` - Base ref for the branch instruction. Defaults to the current branch.
- `--remote` - Remote name for the push instruction. Defaults to origin.
- `--commit-message` - Commit message for the generated instructions.
- `--pr-title` - Pull request title for the generated instructions.
- `--force` - Include install --force in the generated install command.
- `--write-sidecar` - Write onboarding JSON and Markdown artifacts under the repo sidecar.

### kit options

Show the human command guide.

- Audience: `human`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `no`
- Output schema: `text_command_guide`
- Route role: `canonical`
- Canonical command: `options`
- Docs: `README.md#installed-commands`

Examples:

- `kit options`

Flags:

- `--all` - Include advanced automation commands.

### kit orient

Inspect a repo and print startup context without writing files.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `orient_payload`
- Route role: `agent-only`
- Canonical command: `orient`
- Docs: `README.md#installed-commands`

Examples:

- `kit orient --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--mode`
- `--config`
- `--write-sidecar` - Write session-start.json and agent-brief.md under the repo sidecar.

### kit palette

Search commands in an interactive TTY palette.

- Audience: `human`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `no`
- Output schema: `tty_command_palette`
- Route role: `canonical`
- Canonical command: `palette`
- Docs: `README.md#tty-command-palette`

Examples:

- `kit palette`
- `kit palette --query status`
- `kit palette --query status --print-command`

Flags:

- `--query` - Initial search text for command names, summaries, and examples.
- `--print-command` - Print the first matched exact command without prompting.

### kit retention

Preview sidecar retention and privacy policy without deleting files.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `retention_payload`
- Route role: `canonical`
- Canonical command: `retention`
- Docs: `docs/sidecar-retention.md`

Examples:

- `kit retention --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.

### kit review-plan

Emit a read-only review plan for an agent.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `review_plan_payload`
- Route role: `agent-only`
- Canonical command: `review-plan`
- Docs: `README.md#installed-commands`

Examples:

- `kit review-plan --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--mode`
- `--trust-profile`
- `--write-sidecar` - Write the review plan under the repo sidecar.

### kit self

Inspect or update the global repo-contract-kit tool checkout.

- Audience: `human, agent`
- Mutation: `namespace`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `no`
- Output schema: `subcommand_namespace`
- Route role: `maintainer`
- Canonical command: `self`
- Docs: `README.md#installed-commands`

Examples:

- `kit self status --json`

### kit self status

Show global tool checkout status.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `self_status_payload`
- Route role: `maintainer`
- Canonical command: `self status`
- Docs: `README.md#installed-commands`

Examples:

- `kit self status --json`

Flags:

- `--json` - Emit machine-readable JSON.

### kit self update

Fetch and switch the global tool checkout to a ref.

- Audience: `human, agent`
- Mutation: `writes-global-tool-checkout`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `self_update_payload`
- Route role: `maintainer`
- Canonical command: `self update`
- Docs: `README.md#installed-commands`

Examples:

- `kit self update --json`

Flags:

- `--ref` - Branch or tag to fetch from origin. Default: main.
- `--workflow-ref` - Branch or tag for the legacy external workflow-source checkout. Defaults to --ref.
- `--json` - Emit machine-readable JSON.

### kit setup

Enroll the current or selected git repo.

- Audience: `human, agent`
- Mutation: `writes-target`
- Target writes: `writes-target`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `install_update_payload`
- Route role: `canonical`
- Canonical command: `setup`
- Docs: `README.md#installed-commands`

Examples:

- `kit setup --repo /path/to/repo --preset agentic --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--profile`
- `--profiles`
- `--preset`
- `--runtime-adapter`
- `--runtime-adapters`
- `--force`

### kit sidecar-init

Create sidecar directories for repo-external agent artifacts.

- Audience: `human, agent`
- Mutation: `writes-sidecar`
- Target writes: `never`
- Sidecar writes: `always`
- JSON: `yes`
- Output schema: `sidecar_init_payload`
- Route role: `canonical`
- Canonical command: `sidecar-init`
- Docs: `README.md#installed-commands`

Examples:

- `kit sidecar-init --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.

### kit start

Choose the next human or agent journey from repo state.

- Audience: `human, agent`
- Mutation: `writes-target-conditionally`
- Target writes: `local-safe managed-file update by default for installed target repos; never with --no-update`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `start_payload`
- Route role: `canonical`
- Canonical command: `start`
- Docs: `README.md#start-here, docs/human-guide.md, docs/agent-guide.md`

Examples:

- `kit start`
- `kit start --no-update`
- `kit start --lite`
- `kit start --json`
- `kit start --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--mode` - Requested harness mode. auto lets kit choose.
- `--lite` - Shortcut for --mode lite.
- `--update-policy` - Local update behavior for installed target repos: local-safe applies managed-file updates; check-only only reports.
- `--no-update` - Skip the local update check and apply step.

### kit status

Show git, install, and kit state.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `status_payload`
- Route role: `canonical`
- Canonical command: `status`
- Docs: `README.md#installed-commands`

Examples:

- `kit status --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.

### kit target

Manage target repo enrollment.

- Audience: `human, agent`
- Mutation: `namespace`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `no`
- Output schema: `subcommand_namespace`
- Route role: `namespace`
- Canonical command: `target`
- Docs: `README.md#installed-commands`

Examples:

- `kit target status --repo /path/to/repo --json`

### kit target add

Enroll the current or selected git repo by installing kit target files.

- Audience: `human, agent`
- Mutation: `writes-target`
- Target writes: `writes-target`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `install_update_payload`
- Route role: `alias`
- Canonical command: `setup`
- Docs: `README.md#installed-commands`

Examples:

- `kit target add --repo /path/to/repo --preset agentic --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--profile`
- `--profiles`
- `--preset`
- `--runtime-adapter`
- `--runtime-adapters`
- `--force`

### kit target doctor

Diagnose dirty state, task/worktree state, and safe recovery commands for a target repo.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `agent_preflight_payload`
- Route role: `alias`
- Canonical command: `doctor`
- Docs: `README.md#installed-commands`

Examples:

- `kit target doctor --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--strict` - Exit non-zero when startup blockers are present.
- `--write-sidecar` - Write a doctor receipt under the repo sidecar.

### kit target import

Seed the registered target list from installed kit repos under a scan root.

- Audience: `human, agent`
- Mutation: `writes-local-kit-registry-with-apply`
- Target writes: `never`
- Sidecar writes: `with --apply`
- JSON: `yes`
- Output schema: `target_import_payload`
- Route role: `canonical`
- Canonical command: `target import`
- Docs: `README.md#installed-commands`

Examples:

- `kit target import --root /Volumes/Myrtle/Code/04_Code --dry-run --json`
- `kit target import --root /Volumes/Myrtle/Code/04_Code --apply --json`

Flags:

- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--root` - Root directory to scan for installed target repos. Defaults to the current directory.
- `--exclude` - Additional fnmatch pattern to exclude from import.
- `--include-agent-worktrees` - Include paths containing agent-worktrees. Excluded by default.
- `--include-archive` - Include paths under archive directories. Excluded by default.
- `--dry-run` - Preview registry import without writing. This is the default.
- `--apply` - Write eligible installed primary repos to the local kit registry.

### kit target list

List registered target repos used by batch updates.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `target_list_payload`
- Route role: `canonical`
- Canonical command: `target list`
- Docs: `README.md#installed-commands`

Examples:

- `kit target list --json`

Flags:

- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.

### kit target prune-missing

Remove registered target repos whose paths no longer exist.

- Audience: `human, agent`
- Mutation: `writes-local-kit-registry-with-apply`
- Target writes: `never`
- Sidecar writes: `with --apply`
- JSON: `yes`
- Output schema: `target_prune_missing_payload`
- Route role: `canonical`
- Canonical command: `target prune-missing`
- Docs: `README.md#installed-commands`

Examples:

- `kit target prune-missing --dry-run --json`
- `kit target prune-missing --apply --json`

Flags:

- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--dry-run` - Preview missing registry entries without writing. This is the default.
- `--apply` - Remove missing registry entries from the local kit registry.

### kit target repair-source-clone

Preview or remove accidental nested repo-contract-kit/agent-workflow-kit source clones from a target repo.

- Audience: `agent`
- Mutation: `conditional-target-repair`
- Target writes: `conditional-target-repair`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `source_clone_repair_payload`
- Route role: `agent-only`
- Canonical command: `target repair-source-clone`
- Docs: `README.md#installed-commands`

Examples:

- `kit target repair-source-clone --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--apply` - Remove eligible nested source clone directories.
- `--allow-tracked` - Allow removal when detected source clone paths are tracked by the target repo.
- `--scan-depth` - Directory depth to scan for nested source clones. Default: 2.

### kit target status

Show current or selected target repo install status.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `status_payload`
- Route role: `alias`
- Canonical command: `status`
- Docs: `README.md#installed-commands`

Examples:

- `kit target status --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.

### kit target update

Apply safe managed updates to the current or selected target repo from the global tool checkout.

- Audience: `human, agent`
- Mutation: `writes-target-by-default`
- Target writes: `writes-target-by-default`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `install_update_payload`
- Route role: `canonical`
- Canonical command: `target update`
- Docs: `README.md#installed-commands`

Examples:

- `kit target update --repo /path/to/repo --dry-run --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--dry-run` - Plan the target update without writing files.
- `--preset`
- `--profiles`
- `--runtime-adapter`
- `--runtime-adapters`
- `--metadata-only`
- `--force-managed`
- `--verbose` - Show raw update script detail after the compact summary.

### kit target update-all

Dry-run or apply updates to every registered enrolled target repo.

- Audience: `human, agent`
- Mutation: `writes-targets-with-apply`
- Target writes: `with --apply`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `target_update_all_payload`
- Route role: `canonical`
- Canonical command: `target update-all`
- Docs: `README.md#installed-commands`

Examples:

- `kit target update-all --dry-run --json`
- `kit target update-all --apply --json`

Flags:

- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--dry-run` - Plan every registered target update without writing files. This is the default.
- `--apply` - Apply updates to clean registered targets. Dirty targets are skipped.
- `--preset`
- `--profiles`
- `--runtime-adapter`
- `--runtime-adapters`
- `--metadata-only`
- `--force-managed`

### kit task-packet

Emit a task-packet JSON scaffold.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `task_packet_payload`
- Route role: `agent-only`
- Canonical command: `task-packet`
- Docs: `README.md#installed-commands`

Examples:

- `kit task-packet --repo /path/to/repo --task-id TASK-1 --title Title --problem Problem --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--task-id`
- `--title`
- `--problem`
- `--priority`
- `--harness-mode` - Harness strictness: auto selects lite, standard, or release-gated from repo state.
- `--mode`
- `--source-type`
- `--source-reference`
- `--story-type`
- `--story-actor`
- `--story-need`
- `--story-outcome`
- `--story-acceptance-summary`
- `--scope`
- `--protected-file`
- `--inspect-first`
- `--expected-output`
- `--background`
- `--non-goal`
- `--acceptance`
- `--validation`
- `--docs-impact`
- `--docs-path`
- `--docs-surface`
- `--release-metadata`
- `--generated-doc`
- `--contract-reference`
- `--docs-validation-command`
- `--risk`
- `--known-risk`
- `--stop-condition`
- `--approved`
- `--approver`
- `--approval-note`
- `--owner`
- `--dependency`
- `--next-packet-hint`
- `--write-sidecar` - Write the task packet under the repo sidecar.

### kit update

Update the current repo, or use --global to update the tool checkout.

- Audience: `human, agent`
- Mutation: `writes-target-by-default`
- Target writes: `writes-target-by-default`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `install_update_payload`
- Route role: `canonical`
- Canonical command: `update`
- Docs: `README.md#installed-commands`

Examples:

- `kit update --dry-run --json`
- `kit update --json`
- `kit update --all --dry-run --json`
- `kit update --all --apply --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--kit` - kit checkout to update from. Defaults to this checkout.
- `--global` - Update the global tool checkout instead of a target repo.
- `--all` - Update every registered enrolled target repo. Defaults to dry-run unless --apply is set.
- `--ref` - Branch or tag to fetch for --global. Default: main.
- `--workflow-ref` - Branch or tag for the optional legacy workflow-source checkout when --global is used. Defaults to --ref.
- `--dry-run`
- `--apply`
- `--preset`
- `--profiles`
- `--runtime-adapter`
- `--runtime-adapters`
- `--metadata-only`
- `--force-managed`
- `--verbose` - Show raw update script detail after the compact summary.

### kit update-plan

Emit a non-mutating migration/update plan.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `update_plan_payload`
- Route role: `canonical`
- Canonical command: `update-plan`
- Docs: `README.md#installed-commands`

Examples:

- `kit update-plan --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--kit` - kit checkout to plan from. Defaults to this checkout.
- `--preset`
- `--profiles`
- `--runtime-adapter`
- `--runtime-adapters`
- `--force-managed`

### kit verify

Run non-mutating local verification checks.

- Audience: `agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `optional`
- JSON: `yes`
- Output schema: `verify_payload`
- Route role: `agent-only`
- Canonical command: `verify`
- Docs: `README.md#installed-commands`

Examples:

- `kit verify --repo /path/to/repo --json`

Flags:

- `--repo` - Target git repository. Defaults to the current directory.
- `--json` - Emit machine-readable JSON.
- `--config`
- `--harness-mode` - Harness strictness: auto selects lite, standard, or release-gated from repo state.
- `--changed-file`
- `--staged`
- `--working-tree`
- `--no-docs-needed`
- `--write-sidecar` - Write the verification receipt under the repo sidecar.

### kit version

Show CLI and kit version metadata.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `version_payload`
- Route role: `canonical`
- Canonical command: `version`
- Docs: `README.md#installed-commands`

Examples:

- `kit version`
- `kit version --json`

Flags:

- `--json` - Emit machine-readable JSON.

### kit worktree

Audit and prune disposable agent worktrees.

- Audience: `human, agent`
- Mutation: `namespace`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `no`
- Output schema: `subcommand_namespace`
- Route role: `namespace`
- Canonical command: `worktree`
- Docs: `README.md#installed-commands`

Examples:

- `kit worktree audit --root /path/to/repos --json`

### kit worktree audit

Audit disposable agent worktrees under one or more roots.

- Audience: `human, agent`
- Mutation: `read-only`
- Target writes: `never`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `worktree_audit_payload`
- Route role: `canonical`
- Canonical command: `worktree audit`
- Docs: `README.md#installed-commands`

Examples:

- `kit worktree audit --root /Volumes/Myrtle/Code/04_Code --json`

Flags:

- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--root` - Root directory to scan. Defaults to the current directory.

### kit worktree prune

Remove clean disposable linked worktrees under agent-worktrees paths.

- Audience: `human, agent`
- Mutation: `removes-clean-disposable-worktrees-with-apply`
- Target writes: `with --apply`
- Sidecar writes: `never`
- JSON: `yes`
- Output schema: `worktree_prune_payload`
- Route role: `canonical`
- Canonical command: `worktree prune`
- Docs: `README.md#installed-commands`

Examples:

- `kit worktree prune --root /Volumes/Myrtle/Code/04_Code --dry-run --json`
- `kit worktree prune --root /Volumes/Myrtle/Code/04_Code --apply --json`

Flags:

- `--json` - Emit machine-readable JSON.
- `--style` - Human output style: auto uses ANSI only on a TTY, plain disables it, pretty forces it unless NO_COLOR is set.
- `--root` - Root directory to scan. Defaults to the current directory.
- `--dry-run` - Preview removable worktrees without deleting them. This is the default.
- `--apply` - Remove eligible clean linked worktrees.
- `--force` - Pass --force to git worktree remove for eligible clean worktrees.
