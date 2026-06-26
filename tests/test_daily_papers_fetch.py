import importlib.util
import json
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "1-literature"
    / "daily-papers"
    / "fetch_and_score.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("fetch_and_score", MODULE_PATH)
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


def test_fetch_url_uses_direct_response_when_available(monkeypatch):
    module = load_module()
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request)
        return FakeResponse("direct ok")

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    monkeypatch.delenv("LEXMOUNT_API_KEY", raising=False)

    assert module.fetch_url("https://arxiv.org/abs/2604.06126") == "direct ok"
    assert len(calls) == 1


def test_fetch_url_falls_back_to_lexmount_dom_dump(monkeypatch):
    module = load_module()
    calls = []

    def fake_urlopen(request, timeout):
        url = request.full_url if hasattr(request, "full_url") else request
        calls.append(request)
        if url == "https://webfetch.lexmount.com/v1/dom/dump":
            assert request.get_header("X-api-key") == "test-key"
            body = json.loads(request.data.decode("utf-8"))
            assert body["url"] == "https://huggingface.co/api/daily_papers?date=2026-06-25&limit=100"
            return FakeResponse(
                json.dumps(
                    {
                        "html": '<html><body><pre>{"papers":[{"id":"2606.00001"}]}</pre></body></html>',
                        "engine": "http",
                    }
                )
            )
        raise TimeoutError("direct fetch stalled")

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    monkeypatch.setenv("LEXMOUNT_API_KEY", "test-key")

    text = module.fetch_url("https://huggingface.co/api/daily_papers?date=2026-06-25&limit=100")

    assert text == '{"papers":[{"id":"2606.00001"}]}'
    assert len(calls) == 2


def test_fetch_url_fallback_reads_ignored_env_file(monkeypatch, tmp_path):
    module = load_module()
    (tmp_path / ".env").write_text("LEXMOUNT_API_KEY=test-key\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LEXMOUNT_API_KEY", raising=False)

    def fake_urlopen(request, timeout):
        url = request.full_url if hasattr(request, "full_url") else request
        if url == "https://webfetch.lexmount.com/v1/dom/dump":
            assert request.get_header("X-api-key") == "test-key"
            return FakeResponse(json.dumps({"html": "<pre>[]</pre>"}))
        raise TimeoutError("direct fetch stalled")

    monkeypatch.setattr(module, "urlopen", fake_urlopen)

    assert module.fetch_url("https://export.arxiv.org/api/query?search_query=cat:cs.AI") == "[]"
