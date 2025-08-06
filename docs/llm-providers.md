# LLM Provider Interface

This document describes the interface and orchestration logic for integrating LLM providers in the backend.

## Abstract Provider Interface

All LLM providers must inherit from `LLMProvider` and implement:

```
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM given a prompt."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
```

## Example: MockLLMProvider

```
class MockLLMProvider(LLMProvider):
    def generate(self, prompt: str, **kwargs) -> str:
        return "This is a mock response."
    def name(self) -> str:
        return "mock"
```

## Orchestration Layer

- Providers are registered in `PROVIDER_REGISTRY`.
- The orchestrator selects providers based on the `LLM_PROVIDER` environment variable (comma-separated for failover).
- Retry logic with exponential backoff is built-in.
- On failure, the orchestrator tries the next provider in the list.

## Usage

```
from orchestrator.orchestrator import LLMOrchestrator
orch = LLMOrchestrator(["mock"])  # or ["openai", "mock"] for failover
response = orch.generate("Your prompt here")
```

## Testing

- Use `MockLLMProvider` for tests.
- Tests should cover provider selection, retry, and failover logic.
