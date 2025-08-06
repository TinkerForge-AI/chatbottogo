
import os
import requests
from .base import LLMProvider
from typing import Generator
import json



class GoogleAIProvider(LLMProvider):
    """
    Google Gemini LLM provider with streaming and cost estimation.
    """
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self.api_key = "AIzaSyCPDVUoHVR71BvX1-o_WfcyZIFvAQjIY4Q"
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
        self.token_cost_per_1k = 0.00025  # Example cost, update as needed

    def generate(self, prompt: str, stream: bool = False, **kwargs):
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        endpoint = f"{self.base_url}:generateContent"
        resp = requests.post(endpoint, headers=headers, json=data, stream=False)
        resp.raise_for_status()
        obj = resp.json()
        # Defensive: check for candidates and content
        candidates = obj.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"No candidates in Gemini response: {obj}")
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise RuntimeError(f"No parts in Gemini response: {obj}")
        return parts[0].get("text", "")

    def _stream_response(self, headers, params, data) -> Generator[str, None, None]:
        endpoint = f"{self.base_url}{self.model}:streamGenerateContent"
        with requests.post(endpoint, headers=headers, params=params, json=data, stream=True) as resp:
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            # If the response is a single JSON object/array, treat as fake streaming
            if "application/json" in content_type:
                body = resp.content
                try:
                    # Try to parse as a JSON array (true for Gemini 2.5)
                    arr = json.loads(body)
                    if isinstance(arr, list):
                        for obj in arr:
                            candidates = obj.get("candidates", [])
                            if not candidates:
                                continue
                            content = candidates[0].get("content", {})
                            parts = content.get("parts", [])
                            if not parts:
                                continue
                            text = parts[0].get("text", "")
                            yield text
                        return
                    elif isinstance(arr, dict):
                        # Defensive: handle dict (shouldn't happen for streaming)
                        candidates = arr.get("candidates", [])
                        if not candidates:
                            return
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if not parts:
                            return
                        text = parts[0].get("text", "")
                        yield text
                        return
                except Exception:
                    return
            # Otherwise, try to parse as NDJSON (true streaming)
            for line in resp.iter_lines():
                if line:
                    try:
                        chunk = line.decode()
                        obj = json.loads(chunk)
                        candidates = obj.get("candidates", [])
                        if not candidates:
                            continue
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if not parts:
                            continue
                        text = parts[0].get("text", "")
                        yield text
                    except Exception:
                        continue

    def name(self) -> str:
        return "googleai"

    def count_tokens(self, prompt: str) -> int:
        # Naive token count: 1 token per 4 chars (adjust for real tokenizer)
        return max(1, len(prompt) // 4)

    def estimate_cost(self, prompt: str) -> float:
        tokens = self.count_tokens(prompt)
        return (tokens / 1000) * self.token_cost_per_1k
