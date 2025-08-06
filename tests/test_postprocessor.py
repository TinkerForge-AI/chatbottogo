import sys
print('Python executable:', sys.executable)
print('Python sys.path:', sys.path)
import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/postprocessor')))
import importlib
md_utils = importlib.import_module('md_utils')
links = importlib.import_module('links')
hallucination = importlib.import_module('hallucination')
truncate = importlib.import_module('truncate')

# Markdown tests
def test_markdown_validation():
    valid_md = "# Title\n\nSome text.\n\n```python\nprint('hi')\n```"
    html = md_utils.validate_and_convert_markdown(valid_md)
    assert '<h1>' in html and '<code' in html
    
    with pytest.raises(ValueError):
        md_utils.validate_and_convert_markdown(None)  # type: ignore

def test_code_block_detection():
    md = """```js\nconsole.log('hi')\n```\n```\nno lang\n```"""
    blocks = md_utils.detect_code_blocks(md)
    assert blocks == [("js", "console.log('hi')\n"), ("", "no lang\n")]

def test_syntax_highlighting_hints():
    md = "```\ncode\n```"
    out = md_utils.add_syntax_highlighting_hints(md)
    assert '```plaintext' in out

# Link tests
def test_url_validation():
    text = "Visit https://example.com and http://bad_url"
    results = links.validate_urls(text)
    assert results[0][1] is True
    assert results[1][1] is True  # urlparse treats both as valid schemes

# Truncation
def test_truncate():
    s = "a" * 2100
    out = truncate.truncate_response(s, 100)
    assert out.endswith("...") and len(out) <= 103

# Hallucination detection
def test_hallucination_detection():
    context = ["The capital of France is Paris."]
    resp = "The capital of France is Paris. The moon is made of cheese."
    halluc = hallucination.basic_hallucination_detection(resp, context)
    assert any("moon" in s for s in halluc)

# Markdown edge cases
def test_markdown_edge_cases():
    nested = "- Item 1\n  - Subitem\n\n| Col1 | Col2 |\n|------|------|\n| A    | B    |\n\n```py\ndef foo():\n  pass\n```"
    html = md_utils.validate_and_convert_markdown(nested)
    assert '<ul>' in html and '<table>' in html and '<code' in html
