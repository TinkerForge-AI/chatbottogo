
import os
import sys
import pytest
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from providers.googleai import GoogleAIProvider

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="No Gemini API key set")
def test_googleai_basic():
    provider = GoogleAIProvider()
    prompt = "Say hello in one sentence."
    result = provider.generate(prompt)
    assert isinstance(result, str)
    assert len(result) > 0
    tokens = provider.count_tokens(prompt)
    assert tokens > 0
    cost = provider.estimate_cost(prompt)
    assert cost >= 0

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="No Gemini API key set")
def test_googleai_stream():
    provider = GoogleAIProvider()
    prompt = "List three colors."
    stream = provider.generate(prompt, stream=True)
    chunks = []
    print("--- Gemini streaming debug output ---")
    for i, chunk in enumerate(stream):
        print(f"Chunk {i}: {repr(chunk)}")
        chunks.append(chunk)
    print(f"Total chunks: {len(chunks)}")
    print(f"All chunks: {chunks}")
    assert sum(len(c) for c in chunks) > 0
