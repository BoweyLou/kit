# Docs As Tests

This repo has opted into the experimental docs-as-tests profile.

Run it explicitly:

```bash
make docs-as-tests
DOCS_AS_TESTS_JSON=1 make docs-as-tests
python3 scripts/repo_contract_kit.py docs-as-tests --repo "$(pwd)" --json
```

The profile is separate from `make docs-check`. It does not change
`docs-freshness`, `docs-impact`, `docs-propose`, semantic receipt review, or
release-version checks.

## Config

Assertions live in `.agent-workflows/docs-as-tests.json`. The checker reads only
declared JSON assertions. It does not scrape prose, run fenced examples, call
network URLs, start services, use hosted models, or execute shell commands.
Use schema version `2` for new claim manifests; schema version `1`
`openapi_operation_exists` assertions remain supported.

Example:

```json
{
  "schema_version": 2,
  "assertions": [
    {
      "claim_id": "api-health-get",
      "kind": "openapi_operation_exists",
      "source_doc": {"path": "docs/api.md", "anchor": "health"},
      "evidence": {"spec": "openapi.json"},
      "selector": {
        "method": "GET",
        "path": "/health"
      },
      "safety_tier": "local-read-only",
      "confidence": "high"
    },
    {
      "claim_id": "api-health-200",
      "kind": "openapi_response_status_exists",
      "source_doc": "docs/api.md",
      "spec": "openapi.json",
      "selector": {"method": "GET", "path": "/health", "status": "200"}
    },
    {
      "claim_id": "health-status-property",
      "kind": "openapi_schema_property_exists",
      "source_doc": "docs/api.md",
      "spec": "openapi.json",
      "selector": {
        "schema": "#/components/schemas/Health",
        "property": "status"
      }
    },
    {
      "claim_id": "documented-config-key",
      "kind": "json_key_exists",
      "source_doc": "docs/config.md",
      "evidence": {"config": "config.schema.json"},
      "selector": {"key": "/server/port"}
    }
  ]
}
```

Supported assertions are:

- `openapi_operation_exists`: a documented method/path exists in local OpenAPI
  `paths`.
- `openapi_response_status_exists`: a documented method/path/status exists in a
  local OpenAPI operation's `responses`.
- `openapi_schema_property_exists`: a declared local OpenAPI schema has a
  declared property.
- `json_key_exists`: a declared local JSON config/reference file has a declared
  key, optionally with an expected value.

The source doc, local evidence path, selector, safety tier, and confidence
should be explicit for each executable claim. Missing config, invalid JSON,
unsupported assertion kinds, network URLs, command-like input, missing local
artifacts, and missing or ambiguous selectors are reported as refused or
unsupported rather than guessed failures. Disabled claims can use
`"enabled": false` or `"skip": true` and will be reported as `skipped`.

JSON output includes assertion ids, source doc paths, local evidence paths, result,
failures, refusals, skipped and unsupported assertions, omissions,
`target_repo_writes=false`, and `network_used=false`.
