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


# ── Venue 源：OpenAlex 期刊 + CVF 顶会 ────────────────────────────────────


def test_reconstruct_abstract_orders_by_position():
    module = load_module()
    inverted = {"world": [1], "Hello": [0], "again": [2]}
    assert module.reconstruct_abstract(inverted) == "Hello world again"
    assert module.reconstruct_abstract(None) == ""
    assert module.reconstruct_abstract({}) == ""


def test_is_frontmatter_matches_journal_noise():
    module = load_module()
    assert module.is_frontmatter("IEEE Computational Intelligence Society")
    assert module.is_frontmatter("Table of Contents")
    assert module.is_frontmatter("Corrections to “Learning From M-Tuple”")
    assert module.is_frontmatter("")
    # 真实论文标题不应被误杀
    assert not module.is_frontmatter("MPANet: Motion Pattern Aggregation Network")


def test_paper_key_prefers_arxiv_then_doi_then_cvf_then_title():
    module = load_module()
    assert module.paper_key({"url": "https://arxiv.org/abs/2606.12345"}) == "2606.12345"
    assert (
        module.paper_key({"url": "https://doi.org/10.1007/x", "doi": "https://doi.org/10.1007/X"})
        == "doi:10.1007/x"
    )
    assert (
        module.paper_key(
            {
                "source": "cvf:CVPR2026",
                "url": "https://openaccess.thecvf.com/content/CVPR2026/html/A_Foo_paper.html",
            }
        )
        == "cvf:A_Foo_paper"
    )
    k = module.paper_key({"title": "Some Unindexed Title", "url": "", "source": "openalex:IJCV"})
    assert k.startswith("title:")


def test_cap_and_truncate_limits_per_source(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "MAX_PER_SOURCE", {"cvf": 2})
    cands = [{"source": "cvf:CVPR2026", "score": s} for s in (10, 9, 8, 7)]
    cands += [{"source": "arxiv", "score": s} for s in (6, 5, 4)]
    out = module.cap_and_truncate(cands, top_n=100)
    cvf = [p for p in out if p["source"].startswith("cvf")]
    assert len(cvf) == 2  # cvf 被截到 2
    assert len(out) == 5  # 2 cvf + 3 arxiv（arxiv 无 cap）


def test_cap_and_truncate_reserves_slots_for_venue(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "MAX_PER_SOURCE", {"openalex": 8})
    monkeypatch.setattr(module, "RESERVE_PER_SOURCE", {"openalex": 2})
    # 高分 HF 会塞满 top_n；低分期刊若无保底将全部被挤出
    cands = [{"source": "hf-trending", "score": 9999} for _ in range(5)]
    cands += [{"source": "openalex:IJCV", "score": 3} for _ in range(4)]
    out = module.cap_and_truncate(cands, top_n=5)
    oa = [p for p in out if p["source"].startswith("openalex")]
    assert len(out) == 5
    assert len(oa) == 2  # 保底纳入 2 篇期刊，即便分数远低于 HF


def test_merge_and_rank_dedups_arxiv_and_openalex(tmp_path):
    module = load_module()
    history_path = tmp_path / ".history.json"
    arxiv = [{"title": "Same Paper", "url": "https://arxiv.org/abs/2606.00001", "score": 3, "source": "arxiv"}]
    venue = [
        {
            "title": "Same Paper",
            "url": "https://arxiv.org/abs/2606.00001",  # OpenAlex 返回的 arxiv 链接
            "doi": "https://doi.org/10.1007/same",
            "score": 5,
            "source": "openalex:IJCV",
        }
    ]
    top = module.merge_and_rank(venue, [], arxiv, _date(2026, 6, 26), days=1, top_n=30, history_path=history_path)
    assert len(top) == 1  # 跨源合并为一篇
    assert top[0]["score"] == 5  # 保留高分的 venue 版本


def test_fetch_cvf_papers_parses_listing(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "CVF_PROCEEDINGS", ["ICCV2025"])
    listing = (
        '<dt class="ptitle"><br><a href="/content/ICCV2025/html/Doe_A_Vision_'
        'Language_Model_for_Grounding_ICCV_2025_paper.html">'
        "A Vision Language Model for Grounding</a></dt>"
    )
    monkeypatch.setattr(module, "fetch_url", lambda url, timeout=30: listing)
    papers = module.fetch_cvf_papers()
    assert len(papers) == 1
    p = papers[0]
    assert p["source"] == "cvf:ICCV2025"
    assert p["url"].endswith("_paper.html")
    assert p["pdf_url"].endswith("_paper.pdf") and "/papers/" in p["pdf_url"]
    assert p["score"] >= module.MIN_SCORE  # 标题含 "vision language model"


def test_fetch_openalex_papers_filters_frontmatter(monkeypatch):
    module = load_module()
    monkeypatch.setattr(module, "OPENALEX_VENUES", [{"name": "IJCV", "issn": "0920-5691"}])
    payload = {
        "results": [
            {  # front-matter：标题命中黑名单 → 丢弃
                "title": "IEEE Computational Intelligence Society",
                "authorships": [],
                "abstract_inverted_index": None,
                "locations": [],
                "doi": None,
            },
            {  # 真实论文：保留
                "title": "A Vision Language Model for Grounding",
                "authorships": [{"author": {"display_name": "Jane Doe"}}],
                "abstract_inverted_index": {"vision": [0], "language": [1]},
                "locations": [{"landing_page_url": "https://arxiv.org/abs/2606.55555"}],
                "doi": "https://doi.org/10.1007/real",
                "publication_date": "2026-06-20",
            },
        ]
    }
    monkeypatch.setattr(module, "fetch_url", lambda url, timeout=30: json.dumps(payload))
    papers = module.fetch_openalex_papers(_date(2026, 6, 26))
    assert len(papers) == 1
    p = papers[0]
    assert p["source"] == "openalex:IJCV"
    assert p["url"] == "https://arxiv.org/abs/2606.55555"  # 优先 arxiv 链接
    assert p["abstract"] == "vision language"
    assert p["score"] >= module.MIN_SCORE


def _date(y, m, d):
    import datetime

    return datetime.date(y, m, d)


def test_load_config_merges_team_interests(tmp_path, monkeypatch):
    """team-config.json 存在 interests 时，keywords = 本地 keywords ∪ interests 展开。"""
    module = load_module()
    team = tmp_path / "team-config.json"
    team.write_text('{"interests": [{"name": "X", "keywords": ["quantum gui"]}]}')
    monkeypatch.setattr(module, "TEAM_CONFIG_PATH", team)
    cfg = module.load_config()
    assert "quantum gui" in cfg["keywords"]
