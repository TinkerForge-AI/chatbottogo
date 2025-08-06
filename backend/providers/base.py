from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    """
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the LLM given a prompt.
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the provider.
        """
        pass
