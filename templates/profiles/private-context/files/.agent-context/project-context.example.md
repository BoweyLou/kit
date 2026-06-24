# Shareable Project Context Example

Use this example for non-sensitive project context that helps local agents
understand terminology, architecture, or working conventions. Prefer moving
durable shared guidance into `AGENTS.md`, `REVIEW.md`, or `docs/` after it
stabilizes.

Do not include secrets, tokens, cookies, passwords, private URLs, account
identifiers, customer data, personal messages, medical or financial data, or
proprietary snippets that should not leave the machine.

Before sharing any copied file with hosted models, browser tools, GitHub
comments, pull requests, issues, external tickets, or chat tools, review and
redact it.

## Safe To Record

- Product terms that already appear in public or checked-in docs.
- Architecture notes that are safe for all repo collaborators.
- Non-sensitive naming conventions or glossary entries.
- Links to checked-in docs by relative path.

## Example Notes

- Primary docs start in `README.md`.
- Durable agent rules belong in `AGENTS.md` and `REVIEW.md`.
- Runtime-specific files should stay thin and point back to shared docs.
