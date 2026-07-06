import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "lexmount_fetch.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lexmount_fetch", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, payload: str):
        self.payload = payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_html_to_text_unwraps_pre_payload():
    module = load_module()

    assert module.html_to_text("<html><body><pre>{&quot;ok&quot;:true}</pre></body></html>") == '{"ok":true}'


def test_extract_posts_api_key_and_returns_result(monkeypatch):
    module = load_module()

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://webfetch.lexmount.com/v1/extract"
        assert request.get_header("X-api-key") == "test-key"
        body = json.loads(request.data.decode("utf-8"))
        assert body["extract"]["url"] == "https://arxiv.org/html/2604.06126"
        assert body["trace"]["include_steps"] is False
        return FakeResponse(json.dumps({"result": {"title": "A Paper", "main_text": "full text"}}))

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    monkeypatch.setenv("LEXMOUNT_API_KEY", "test-key")

    result = module.extract("https://arxiv.org/html/2604.06126")

    assert result["result"]["title"] == "A Paper"
    assert result["result"]["main_text"] == "full text"
