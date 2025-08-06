import os
import logging
import time
from typing import Optional, List, Type

from providers.base import LLMProvider
from providers.mock import MockLLMProvider
from providers.googleai import GoogleAIProvider

# Add additional providers here as needed
PROVIDER_REGISTRY = {
    "mock": MockLLMProvider,
    "googleai": GoogleAIProvider,
    # "openai": OpenAIProvider,  # Example for future
}

class LLMOrchestrator:
    def __init__(self, provider_names: Optional[List[str]] = None, max_retries: int = 3, backoff_base: float = 0.5, usage_db=None):
        if provider_names is None:
            provider_names = [os.getenv("LLM_PROVIDER", "mock")]
        self.providers = [self._init_provider(name) for name in provider_names]
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.usage_db = usage_db

    def _init_provider(self, name: str) -> LLMProvider:
        if name not in PROVIDER_REGISTRY:
            raise ValueError(f"Unknown provider: {name}")
        return PROVIDER_REGISTRY[name]()

    def generate(self, prompt: str, stream: bool = False, user_id: str = None, **kwargs):
        last_exc = None
        for provider in self.providers:
            for attempt in range(self.max_retries):
                try:
                    if stream:
                        response = provider.generate(prompt, stream=True, **kwargs)
                        # Optionally track usage per chunk
                        if self.usage_db and user_id:
                            for chunk in response:
                                self._track_usage(user_id, provider, prompt, chunk)
                                yield chunk
                            return
                        else:
                            yield from response
                            return
                    else:
                        result = provider.generate(prompt, **kwargs)
                        if self.usage_db and user_id:
                            self._track_usage(user_id, provider, prompt, result)
                        return result
                except Exception as exc:
                    last_exc = exc
                    sleep_time = self.backoff_base * (2 ** attempt)
                    logging.warning(f"Provider {provider.name()} failed (attempt {attempt+1}): {exc}. Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
            logging.error(f"Provider {provider.name()} failed after {self.max_retries} attempts. Trying next provider...")
        raise RuntimeError(f"All providers failed. Last error: {last_exc}")

    def _track_usage(self, user_id, provider, prompt, output):
        tokens = provider.count_tokens(prompt)
        cost = provider.estimate_cost(prompt)
        usage = {
            "user_id": user_id,
            "provider": provider.name(),
            "tokens": tokens,
            "cost": cost,
            "timestamp": time.time(),
        }
        if self.usage_db:
            self.usage_db.insert_one(usage)

    def get_active_provider_names(self) -> List[str]:
        return [p.name() for p in self.providers]
