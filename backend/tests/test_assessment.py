import json
import os
import unittest
from unittest.mock import patch

from app.main import assess


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.get("timeout")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, url, headers=None, json=None):
        return _FakeResponse({
            "choices": [{
                "message": {
                    "content": json_module.dumps({
                        "status": "current",
                        "summary": "The supplied evidence supports the claim.",
                        "freshness_score": 82,
                        "rationale": "The sources directly support the claim."
                    })
                }
            }]
        })


json_module = json


class AssessmentContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_without_bifrost_returns_retrieval_only_not_a_verdict(self):
        env = {
            "TAVILY_API_KEY": "test",
            "BIFROST_BASE_URL": "",
            "BIFROST_MODEL": "",
            "BIFROST_API_KEY": "",
        }
        with patch.dict(os.environ, env, clear=True):
            result = await assess("A sufficiently long claim for testing.", [{"title": "Source"}], None)

        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["method"], "retrieval_only")
        self.assertIsNone(result["freshness_score"])

    async def test_empty_evidence_remains_insufficient(self):
        with patch.dict(os.environ, {}, clear=True):
            result = await assess("A sufficiently long claim for testing.", [], None)

        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertIsNone(result["freshness_score"])

    async def test_bifrost_response_obeys_assessment_contract(self):
        env = {
            "BIFROST_BASE_URL": "http://bifrost.test/v1",
            "BIFROST_MODEL": "test-model",
            "BIFROST_API_KEY": "test-key",
        }
        with patch.dict(os.environ, env, clear=True), patch("app.main.httpx.AsyncClient", _FakeAsyncClient):
            result = await assess(
                "A sufficiently long claim for testing.",
                [{"title": "Official source", "content": "Supporting evidence"}],
                "Search summary",
            )

        self.assertEqual(result["status"], "current")
        self.assertEqual(result["method"], "bifrost")
        self.assertEqual(result["freshness_score"], 82)
        self.assertTrue(result["rationale"])


if __name__ == "__main__":
    unittest.main()
