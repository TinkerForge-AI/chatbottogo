
import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from orchestrator.orchestrator import LLMOrchestrator
from providers.mock import MockLLMProvider

class FailingProvider(MockLLMProvider):
    def generate(self, prompt: str, **kwargs) -> str:
        raise RuntimeError("Simulated failure")
    def name(self):
        return "failing"

def test_mock_provider_returns_canned_response():
    orch = LLMOrchestrator(["mock"])
    response = orch.generate("Hello?")
    assert response in MockLLMProvider().responses

def test_failover_to_next_provider(monkeypatch):
    # Register FailingProvider and MockLLMProvider
    from orchestrator.orchestrator import PROVIDER_REGISTRY
    PROVIDER_REGISTRY["failing"] = FailingProvider
    orch = LLMOrchestrator(["failing", "mock"], max_retries=2, backoff_base=0.01)
    response = orch.generate("Test failover")
    assert response in MockLLMProvider().responses
    del PROVIDER_REGISTRY["failing"]

def test_all_providers_fail():
    class AlwaysFail(MockLLMProvider):
        def generate(self, prompt: str, **kwargs):
            raise RuntimeError("fail")
        def name(self):
            return "alwaysfail"
    from orchestrator.orchestrator import PROVIDER_REGISTRY
    PROVIDER_REGISTRY["alwaysfail"] = AlwaysFail
    orch = LLMOrchestrator(["alwaysfail"], max_retries=2, backoff_base=0.01)
    with pytest.raises(RuntimeError):
        orch.generate("Should fail")
    del PROVIDER_REGISTRY["alwaysfail"]
