# Human Guide

Use this page when you want to operate kit directly.

## First Install

Install the launcher once:

```bash
curl -fsSL https://raw.githubusercontent.com/BoweyLou/kit/main/install.sh | sh
```

Then enroll a target repo:

```bash
cd /path/to/repo
kit start
kit setup --preset lite
kit status
```

Use `--repo /path/to/repo` when you are not already inside the target repo.

## Choose A Preset

Start with `lite` for small repos and low-risk local work.

Use `agentic` when you expect agents to use task packets, receipts, review
workflows, or local startup packets regularly:

```bash
kit setup --preset agentic
```

Use optional profiles only when you know the repo needs them. Examples include
runtime adapters, private local context, Python or Node stack hints, or
docs-as-tests.

## Daily Commands

```bash
kit start
kit status
kit mode-check
kit update --dry-run
kit doctor
kit closeout-plan
```

Use `kit start` when you are unsure whether this is a fresh setup, normal
maintenance, dirty work in progress, or a release-sensitive change. It reports
the selected journey, the suggested mode, and the next human and agent commands.
In an installed target repo, it may also apply an already-local, local-safe kit
update before returning those commands.

Use this when you want startup with no target writes:

```bash
kit start --no-update
```

Use this when you want to see whether a local update is available without
applying it:

```bash
kit start --update-policy check-only
```

If the update plan is clear and expected:

```bash
kit update
```

## Update Rules

`kit start` only uses the already-local kit checkout. It does not fetch from
GitHub, update the global launcher, or refresh a source checkout.

Remote/global updates are explicit. A global tool update does not rewrite
target repos by itself.

Update the global cached tool:

```bash
kit update --global
```

Preview a target update:

```bash
kit update --dry-run
```

Apply a target update:

```bash
kit update
```

Review proposed replacements under `.doc-contract-kit/updates/` instead of
copying them blindly over target-owned decisions.

## If You Are Lost

Use this order:

```bash
kit status
kit mode-check
kit doctor
kit closeout-plan
kit help
```

For full update detail, read [upgrade-flow.md](upgrade-flow.md).

For exact command flags, read [cli-reference.md](cli-reference.md).
