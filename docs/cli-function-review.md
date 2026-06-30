# CLI And Function Review

Date: 2026-06-26

This review focuses on how humans and agents discover what to run, how clearly
the CLI exposes write behavior, and where the implementation should be split
next.

## Current Shape

- `kit command-map --json` exposes 66 command routes.
- 44 routes are read-only, 35 are canonical, 21 are agent-only, and 4 are
  aliases.
- `kit start` is now the first read-only journey selector for humans and
  agents.
- The main CLI implementation still lives in one 8,462-line Python file.
- Codex thread mining research is tracked in
  [cli-journey-research.md](cli-journey-research.md).

Largest functions in `scripts/repo_contract_kit.py`:

| Function | Lines | Review note |
| --- | ---: | --- |
| `command_map_annotations` | 528 | Product contract data mixed into executable code. |
| `build_parser` | 503 | Parser construction is too large to scan safely. |
| `main` | 335 | Dispatch, rendering, and error handling are coupled. |
| `agent_context_bundle_payload` | 227 | Bundle assembly wants its own module and tests. |
| `start_payload` | 192 | Journey policy should move into small data-driven helpers. |

## What Is Working

- The command map is the strongest machine contract. It exposes audience,
  mutation behavior, sidecar write behavior, examples, docs, schemas, and route
  roles.
- Most command routes are explicitly read-only, which is good for agent startup
  and inspection.
- The `lite`, `standard`, and `release-gated` harness selection is deterministic
  and test-covered.
- Generated CLI docs are checked by `make docs-freshness`, so parser/document
  drift is caught.

## Refinement Backlog

1. Make `kit start` the shared front door for no-arg `kit` and `kit guide`.
   Today the no-arg dashboard and `start` are separate experiences. Reusing the
   `start_payload` journey decision would reduce confusion.

2. Split the monolithic CLI file into modules:
   `kit_cli/command_map.py`, `kit_cli/parser.py`, `kit_cli/start.py`,
   `kit_cli/renderers.py`, and focused payload modules. Keep
   `scripts/repo_contract_kit.py` as the compatibility entrypoint.

3. Move journey policy into a table. The `outside-git`, `new-repo`,
   `work-in-progress`, and `ready` journeys should be explicit data plus small
   selectors, not one large branching function.

4. Publish JSON schema files for public payloads. The command map names schemas,
   but agents would benefit from concrete schema artifacts for `start_payload`,
   `command_map_payload`, `status_payload`, task packets, and verify reports.

5. Add golden CLI UX fixtures for `kit start`. Existing CLI fixtures cover help,
   parse errors, command-map JSON, update, doctor, and palette behavior. `start`
   should get the same regression protection.

6. Normalize command safety metadata with a registry or decorator. Write
   behavior currently appears in annotations, payload constructors, renderers,
   and tests. A single registry would make safety regressions harder.

7. Clarify canonical aliases in human output. `setup`, `install`, and
   `target add` are correctly grouped, but humans should always see the
   canonical route first and aliases as compatibility routes.

8. Extend `agent-tool-manifest --json` with journey-level metadata from
   `kit start`: `journey`, `mode`, `recommended_setup_preset`,
   `human_next_commands`, `agent_next_commands`, and `mode_next_commands`.

9. Plan the internal state naming migration. User-facing branding is now `kit`,
   while sidecar state still uses `repo-contract-kit` for compatibility. Keep
   reading old paths, but decide whether new installs should eventually write a
   `kit` state root with a documented migration path.

10. Add route-level examples for common user journeys:
    fresh repo setup, enrolled clean repo, dirty implementation work, public
    contract change, old install update, and agent startup.

## Suggested Next Implementation Slice

Start with the lowest-risk cleanup:

1. Add `kit start` CLI UX fixtures.
2. Make `kit guide --json` include the same `start_payload` summary without
   changing the no-arg human dashboard yet.
3. Extract `start_payload` and helpers into a dedicated start module with no
   behavior change.

That gives a clean path toward modularizing the CLI without rewriting the
entire command router at once.
