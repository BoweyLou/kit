# Agent Context

This directory is optional local context for coding agents. It is installed only
when the repo owner explicitly selects the `private-context` profile.

The checked-in files here are examples and guidance only. Real local context
files are ignored by default by this directory's `.gitignore`.

## Privacy Boundary

Do not put secrets, tokens, cookies, passwords, private URLs, account
identifiers, customer data, personal messages, medical or financial data, or
proprietary snippets that should not leave the machine in this directory.

This is not a password manager, secret store, customer-record system, browser
profile, hosted sync folder, or memory database. Keep credentials in an approved
secret manager. Keep durable shared repo instructions in `AGENTS.md`,
`REVIEW.md`, or normal project docs.

## Suggested Files

Copy an example to a local non-example filename only when you need that context
for local work:

- `project-context.example.md` -> `project-context.md`
- `user-preferences.example.md` -> `user-preferences.md`
- `private-local-context.example.md` -> `private-local-context.md`

The copied files stay ignored by default. Before pasting context into hosted
models, browser tools, GitHub comments, pull requests, issues, external tickets,
or chat tools, reread it and remove anything sensitive or machine-specific.

Use `AGENTS.md` and `REVIEW.md` for durable shared rules. Use runtime adapters
such as `CLAUDE.md` only as thin tool-specific pointers back to the shared
instructions. Use Keryx, Obsidian, or another memory system through its own
governed workflow instead of copying raw notes into this directory.
