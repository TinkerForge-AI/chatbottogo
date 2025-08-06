from .base import LLMProvider
import random

class MockLLMProvider(LLMProvider):
    """
    Mock provider for testing. Returns canned responses.
    """
    def __init__(self):
        self.responses = [
            "This is a mock response.",
            "Hello from the mock LLM!",
            "Test response: everything is working.",
            "[MOCK] LLM output."
        ]

    def generate(self, prompt: str, **kwargs) -> str:
        return random.choice(self.responses)

    def name(self) -> str:
        return "mock"
