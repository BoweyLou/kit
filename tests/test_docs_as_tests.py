import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_docs_as_tests.py"


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_api_repo(repo: Path, config_payload):
    (repo / "docs").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "api.md").write_text("# API\n\nGET /health is documented.\n", encoding="utf-8")
    write_json(
        repo / "openapi.json",
        {
            "openapi": "3.1.0",
            "components": {
                "schemas": {
                    "Health": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"}
                        },
                        "required": ["status"],
                    }
                }
            },
            "paths": {
                "/health": {
                    "get": {
                        "operationId": "getHealth",
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Health"}
                                    }
                                },
                            }
                        }
                    }
                }
            },
        },
    )
    write_json(repo / ".agent-workflows" / "docs-as-tests.json", config_payload)


def passing_config():
    return {
        "schema_version": 1,
        "assertions": [
            {
                "id": "api-health-get",
                "kind": "openapi_operation_exists",
                "source_doc": "docs/api.md",
                "spec": "openapi.json",
                "selector": {
                    "method": "GET",
                    "path": "/health",
                },
            }
        ],
    }


class DocsAsTestsTests(unittest.TestCase):
    def test_openapi_operation_exists_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            write_api_repo(repo, passing_config())

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["command"], "docs-as-tests")
            self.assertEqual(payload["result"], "passed")
            self.assertFalse(payload["target_repo_writes"])
            self.assertFalse(payload["network_used"])
            self.assertEqual(payload["assertions"][0]["id"], "api-health-get")
            self.assertEqual(payload["assertions"][0]["source_doc_path"], "docs/api.md")
            self.assertEqual(payload["assertions"][0]["spec_path"], "openapi.json")
            self.assertEqual(payload["assertions"][0]["result"], "passed")

    def test_manifest_v2_openapi_and_json_claims_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "docs").mkdir(parents=True)
            (repo / "docs" / "api.md").write_text("# API\n\nGET /health returns status.\n", encoding="utf-8")
            write_json(repo / "settings.schema.json", {"server": {"port": 8080}})
            config = {
                "schema_version": 2,
                "assertions": [
                    {
                        "claim_id": "api-health-200",
                        "kind": "openapi_response_status_exists",
                        "source_doc": {"path": "docs/api.md", "anchor": "health"},
                        "evidence": {"spec": "openapi.json"},
                        "selector": {"method": "GET", "path": "/health", "status": "200"},
                        "safety_tier": "local-read-only",
                        "confidence": "high",
                    },
                    {
                        "claim_id": "health-status-property",
                        "kind": "openapi_schema_property_exists",
                        "source_doc": "docs/api.md",
                        "spec": "openapi.json",
                        "selector": {
                            "schema": "#/components/schemas/Health",
                            "property": "status",
                        },
                    },
                    {
                        "claim_id": "config-port",
                        "kind": "json_key_exists",
                        "source_doc": "docs/api.md",
                        "evidence": {"config": "settings.schema.json"},
                        "selector": {"key": "/server/port"},
                        "expected": 8080,
                    },
                    {
                        "claim_id": "future-claim",
                        "kind": "json_key_exists",
                        "source_doc": "docs/api.md",
                        "config": "settings.schema.json",
                        "selector": {"key": "/server/host"},
                        "enabled": False,
                        "skip_reason": "documented future config",
                    },
                ],
            }
            write_api_repo(repo, config)

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "passed")
            self.assertFalse(payload["target_repo_writes"])
            self.assertFalse(payload["network_used"])
            by_id = {item["id"]: item for item in payload["assertions"]}
            self.assertEqual(by_id["api-health-200"]["result"], "passed")
            self.assertEqual(by_id["api-health-200"]["safety_tier"], "local-read-only")
            self.assertEqual(by_id["health-status-property"]["result"], "passed")
            self.assertEqual(by_id["config-port"]["config_path"], "settings.schema.json")
            self.assertEqual(by_id["config-port"]["result"], "passed")
            self.assertEqual(by_id["future-claim"]["result"], "skipped")

    def test_richer_claim_failures_are_reported_without_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            config = {
                "schema_version": 2,
                "assertions": [
                    {
                        "claim_id": "missing-status",
                        "kind": "openapi_response_status_exists",
                        "source_doc": "docs/api.md",
                        "spec": "openapi.json",
                        "selector": {"method": "GET", "path": "/health", "status": "404"},
                    },
                    {
                        "claim_id": "missing-property",
                        "kind": "openapi_schema_property_exists",
                        "source_doc": "docs/api.md",
                        "spec": "openapi.json",
                        "selector": {"schema": "#/components/schemas/Health", "property": "missing"},
                    },
                    {
                        "claim_id": "missing-key",
                        "kind": "json_key_exists",
                        "source_doc": "docs/api.md",
                        "config": "settings.schema.json",
                        "selector": {"key": "/server/host"},
                    },
                ],
            }
            write_api_repo(repo, config)
            write_json(repo / "settings.schema.json", {"server": {"port": 8080}})

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertEqual(payload["refusals"], [])
            codes = {item["code"] for item in payload["failures"]}
            self.assertIn("response-status-not-found", codes)
            self.assertIn("schema-property-not-found", codes)
            self.assertIn("json-key-not-found", codes)

    def test_openapi_missing_operation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            config = passing_config()
            config["assertions"][0]["selector"]["method"] = "POST"
            write_api_repo(repo, config)

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "failed")
            self.assertEqual(payload["failures"][0]["id"], "api-health-get")
            self.assertEqual(payload["failures"][0]["code"], "operation-not-found")
            self.assertEqual(payload["assertions"][0]["result"], "failed")

    def test_missing_config_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "refused")
            self.assertEqual(payload["refusals"][0]["code"], "missing-config")
            self.assertFalse(payload["network_used"])

    def test_invalid_config_json_is_refused_with_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            config = repo / ".agent-workflows" / "docs-as-tests.json"
            config.parent.mkdir()
            config.write_text("{not-json\n", encoding="utf-8")

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "refused")
            self.assertEqual(payload["refusals"][0]["code"], "invalid-json")

    def test_unsupported_unsafe_network_and_selector_cases_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "docs").mkdir()
            (repo / "docs" / "api.md").write_text("# API\n", encoding="utf-8")
            write_json(repo / "openapi.json", {"openapi": "3.1.0", "paths": {}})
            write_json(
                repo / ".agent-workflows" / "docs-as-tests.json",
                {
                    "schema_version": 1,
                    "assertions": [
                        {
                            "id": "unsupported",
                            "kind": "markdown_claim",
                            "source_doc": "docs/api.md",
                            "spec": "openapi.json",
                            "selector": {"method": "GET", "path": "/health"},
                        },
                        {
                            "id": "network-spec",
                            "kind": "openapi_operation_exists",
                            "source_doc": "docs/api.md",
                            "spec": "https://example.invalid/openapi.json",
                            "selector": {"method": "GET", "path": "/health"},
                        },
                        {
                            "id": "unsafe-doc",
                            "kind": "openapi_operation_exists",
                            "source_doc": "docs/api.md; rm -rf /",
                            "spec": "openapi.json",
                            "selector": {"method": "GET", "path": "/health"},
                        },
                        {
                            "id": "missing-selector",
                            "kind": "openapi_operation_exists",
                            "source_doc": "docs/api.md",
                            "spec": "openapi.json",
                            "selector": {"method": "GET"},
                        },
                        {
                            "id": "ambiguous-selector",
                            "kind": "openapi_operation_exists",
                            "source_doc": "docs/api.md",
                            "spec": "openapi.json",
                            "selector": {"method": "GET", "path": "/health", "operation_id": "getHealth"},
                        },
                    ],
                },
            )

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["result"], "refused")
            codes = {item["code"] for item in payload["refusals"]}
            self.assertIn("unsupported-assertion-kind", codes)
            self.assertIn("network-url", codes)
            self.assertIn("unsafe-input", codes)
            self.assertIn("missing-selector", codes)
            self.assertIn("ambiguous-selector", codes)
            self.assertEqual(len(payload["omissions"]), len(payload["refusals"]))

    def test_missing_local_spec_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            config = passing_config()
            write_api_repo(repo, config)
            (repo / "openapi.json").unlink()

            result = run([sys.executable, str(CHECK), "--repo", str(repo), "--json"], repo)

            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["refusals"][0]["code"], "missing-spec")


if __name__ == "__main__":
    unittest.main()
