# Repo-Contract-Kit Lite Mode

Date: 2026-06-24

Status: implemented in `repo-contract-kit` 0.6.25, with this file retained as
the design rationale and backlog elaboration record.

## Problem

`repo-contract-kit` is a real harness: it gives agents startup context,
permission boundaries, backlog selection, task packets, isolated worktrees,
receipts, docs gates, version checks, and update provenance. That rigor is
valuable for multi-agent or release-impacting work, but it can feel too heavy
for small repos and low-risk local tasks.

Lite mode should reduce ceremony without becoming an unsafe bypass. It should
keep the local-first, read-only-by-default, docs-aware posture, then escalate to
the fuller harness when the work crosses clear risk boundaries.

## Mode Model

| Mode | Use when | Required artifact | Default verification | Escalates when |
| --- | --- | --- | --- | --- |
| Lite | Small repos, docs-only work, small internal fixes, single-agent local tasks, no public contract change. | A compact task note: title, why, files, done-when, validation, docs-needed or no-docs reason. | `kit status`, `kit mode-check --json`, project test or declared skip, `kit verify --harness-mode lite --json`, `git diff --check`. | Public behavior, CLI/API/config/schema, release metadata, security/privacy, dirty primary checkout, parallel work, broad scope, missing goal/docs evidence. |
| Standard | Normal agentic repo work where scope and handoff matter. | Full task packet with story, non-goals, scope, goal alignment, validation, docs impact, risk, approval. | Current agentic verification path plus relevant project tests. | Release, migration, public schema, managed update, automation, or high-risk evidence requirements. |
| Release-gated | Public CLI/API/config/schema/release changes, installer/update behavior, generated docs, migration, or security/privacy surfaces. | Strict task packet plus exact docs, release metadata, generated docs, contract references, and closeout receipt requirements. | Docs freshness, version/changelog gate, generated docs checks, docs-as-tests where configured, full tests. | Human approval remains required for release, migration, or destructive cleanup decisions. |

## Lite Mode User Story

As an operator using `kit` in a small or routine repo, I need a short path from
orientation to verification so that I can keep docs and safety guardrails
without filling a full implementation packet for every small task.

Acceptance summary: the operator can run one setup command, see the next safe
action, record a compact task note when needed, verify the work, and receive an
explicit escalation reason if the task is no longer lite.

## Implemented Operator Surface

Initial setup:

```bash
kit setup --preset lite
kit status --json
```

Daily path:

```bash
kit mode-check --json
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
kit update --dry-run --json
```

`kit mode-check --json` is the deterministic orientation surface. It reports
`selected_mode`, trigger evidence, allowed downgrades, forced escalations, and
next commands before task-packet or verification work starts.

## Mode Selection

Agents should not infer the mode from prose or personal judgement. The default
should be an automatic selector that chooses the strictest matching mode and
prints the reasons.

Candidate surface:

```bash
kit mode-check --json
kit task-packet --harness-mode auto --json
kit verify --harness-mode auto --json
```

Expected text shape:

```text
selected mode: release-gated
reasons:
- public CLI output changed
- generated CLI reference is implicated
next commands:
- kit task-packet --harness-mode release-gated
- kit verify --harness-mode release-gated
```

Expected JSON shape:

```json
{
  "selected_mode": "release-gated",
  "candidate_modes": ["lite", "standard", "release-gated"],
  "triggers": [
    {
      "mode": "release-gated",
      "reason": "public CLI output changed",
      "evidence": ["docs/cli-reference.md", "scripts/repo_contract_kit.py"]
    }
  ],
  "human_override": {
    "can_choose_stricter": true,
    "can_downgrade": false,
    "downgrade_blockers": ["release-gated trigger matched"]
  },
  "next_commands": [
    "kit task-packet --harness-mode release-gated --repo <repo> --json",
    "kit verify --harness-mode release-gated --repo <repo> --json"
  ]
}
```

Selection rule:

1. Start at `lite`.
2. Promote to `standard` if any handoff, breadth, dirty-state, goal-alignment,
   task-source, parallel-work, or validation uncertainty trigger matches.
3. Promote to `release-gated` if any public CLI/API/config/schema, installer,
   update, migration, release metadata, generated-doc, security, privacy, or
   destructive-cleanup trigger matches.
4. Allow a human or agent to choose a stricter mode.
5. Do not allow a silent downgrade below the strictest matched trigger.

The selector should consume deterministic local reports before broad source
inspection: `kit status`, `agent-next`, docs-impact, goal-check, task-status,
command-map metadata, and known docs/version surfaces. When evidence is
missing, stale, or contradictory, it should choose `standard` or
`release-gated` with an explicit uncertainty reason rather than defaulting to
lite.

## What Lite Installs

Lite should be closer to `minimal` than `agentic`.

Install by default:

- root `AGENTS.md` as a concise route map
- `REVIEW.md` with read-only review rules
- `doc-contract.json` and docs-impact checks
- instruction hygiene and command/path freshness checks
- `kit status`, `kit mode-check`, `kit verify`, and update/doctor metadata
- a compact `lite_task_note` JSON payload from
  `kit task-packet --harness-mode lite --json`

Do not install by default:

- the full `.codex/prompts/` review prompt pack
- TDD prompt pack
- task worktree lifecycle commands as the first visible path
- version files unless the `versioning` profile is also selected
- runtime adapters unless explicitly requested

Advanced commands can still exist through the global `kit` CLI. Lite mode is a
default posture and preset, not a different product.

## Compact Task Note

Lite should not require the full task-packet schema for every task. A lite note
should contain:

- title
- why this is being done
- allowed files or expected changed area
- done-when checks
- validation command or explicit skip reason
- docs-needed, docs-updated, or `No docs needed: <reason>`
- escalation check result

The lite note becomes invalid if escalation triggers fire. At that point `kit`
should say why a standard or release-gated packet is required.

## Escalation Triggers

Lite mode should refuse or escalate when any of these are true:

- public CLI, API, config, schema, installer, update, or migration behavior changes
- generated docs, release metadata, changelog, or version files are implicated
- security, privacy, credentials, network access, or hosted account mutation is involved
- a dirty primary checkout needs baseline handling
- parallel write-capable work or sibling worktrees exist
- scope crosses several unrelated areas or cannot name expected changed files
- docs impact is unknown and cannot be resolved by the local docs checks
- goal alignment is unknown, conflicting, or adaptation-needed
- tests or validation are unavailable without an explicit skip reason

Escalation should be explicit, not punitive: "this is standard because..." or
"this is release-gated because...".

## Verification Shape

`kit verify --harness-mode lite --json` is read-only by default and composes:

- repo cleanliness and changed-file summary
- docs-impact result or no-docs declaration
- instruction hygiene for installed agent files
- generated docs freshness when configured
- project-specific validation command if one is declared
- `git diff --check`

It should not run the full agentic fixture suite unless the repo selected the
standard or release-gated profile.

## Examples

Lite:

- Fix a typo in a README and run docs checks.
- Adjust an internal helper with one focused unit test and no public contract
  change.
- Add a small local docs note with `No docs needed` not applicable because docs
  are the change.

Standard:

- Implement a backlog item that changes several files and needs handoff.
- Run a write-capable agent in an isolated task worktree.
- Update agent-facing prompts or task-packet behavior.

Release-gated:

- Change `kit` CLI output, flags, or JSON schemas.
- Update installer, managed-file migration, or target-update behavior.
- Add release metadata, generated CLI reference, docs-as-tests claims, or
  public config/API contracts.

## Backlog Mapping

| ID | Purpose | Implementation |
| --- | --- | --- |
| `AGW-132` | Define the lite mode contract and mode matrix. | `docs/lite-mode.md` and installed template. |
| `AGW-133` | Add an installable lite preset and lite orientation path. | `kit setup --preset lite` plus `mode-check`. |
| `AGW-134` | Make task-packet requirements mode-aware. | `--harness-mode` and `lite_task_note`. |
| `AGW-135` | Compress the primary operator workflow into a five-command path. | `status`, `mode-check`, `task-packet`, `verify`, `update --dry-run`. |
| `AGW-136` | Add outcome calibration so the harness proves value. | `kit calibration --json`. |
| `AGW-137` | Define retention, privacy, and purge policy for sidecar evidence. | `docs/sidecar-retention.md` and `kit retention --json`. |
| `AGW-138` | Finish the legacy archive switch after v1 migration proof. | version 1 closeout checklist and old checkout notice update. |
| `AGW-139` | Add deterministic auto mode selection so agents know which mode to use. | `kit mode-check --json`. |

## Non-Goals

- Do not remove the standard or release-gated harness.
- Do not make lite mode skip docs-impact or mutation-boundary checks.
- Do not make lite mode an implicit auto-update path.
- Do not make target repos clone workflow-source history at runtime.
- Do not turn backlog CSV rows into a full planning application.

## Deferred Design Questions

- Should lite task notes be stored in the target repo, sidecar state, or both?
- Should `kit verify --harness-mode lite` discover project tests automatically or only run
  declared commands?
- Should a target repo be able to set lite as the default while still enabling
  standard packets for specific tasks?
- What threshold should convert "several files" or "broad scope" into standard
  mode?
