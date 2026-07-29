"""Tests for fetch_bibtex: key rewriting, reconstruction, cache parse/serialize, fallback."""
import sys
from pathlib import Path

_LIB_DIR = Path(__file__).resolve().parent.parent / "skills" / "4-writing" / "latex-citation-enhancer"
sys.path.insert(0, str(_LIB_DIR))

import fetch_bibtex as fb  # noqa: E402


ARXIV_SAMPLE = """@misc{wen2026openrathsessioncenteredruntimestate,
      title={OpenRath: Session-Centered Runtime State for Agent Systems},
      author={Fukang Wen and Zhijie Wang and Ruilin Xu},
      year={2026},
      eprint={2606.19409},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2606.19409},
}"""


def test_rewrite_key_replaces_citation_key():
    out = fb.rewrite_key(ARXIV_SAMPLE, "wen2026openrath")
    assert out.startswith("@misc{wen2026openrath,")
    # 其余内容保留
    assert "eprint={2606.19409}" in out
    assert "wen2026openrathsessioncenteredruntimestate" not in out


def test_rewrite_key_preserves_entry_type():
    art = "@article{Smith_2024, title={X}, year={2024}}"
    assert fb.rewrite_key(art, "smith2024x").startswith("@article{smith2024x,")


def test_looks_like_bibtex():
    assert fb.looks_like_bibtex(ARXIV_SAMPLE)
    assert not fb.looks_like_bibtex("<html>404 Not Found</html>")
    assert not fb.looks_like_bibtex("")


def test_reconstruct_arxiv_paper():
    fm = {
        "title": "OpenRath: Session State",
        "authors": ["Fukang Wen", "Zhijie Wang"],
        "date_publish": "2026-06-17",
        "venue": "arXiv",
        "arxiv_id": "2606.19409",
        "url": "https://arxiv.org/abs/2606.19409",
    }
    bib = fb.reconstruct_bibtex(fm, "wen2026openrath")
    assert bib.startswith("@misc{wen2026openrath,")
    assert "author = {Fukang Wen and Zhijie Wang}" in bib
    assert "eprint = {2606.19409}" in bib
    assert "year = {2026}" in bib


def test_reconstruct_conference_paper():
    fm = {
        "title": "Some Vision Paper",
        "authors": ["Alice Smith"],
        "date_publish": "2026",
        "venue": "CVPR 2026",
        "doi": "10.1109/CVPR.2026.00001",
    }
    bib = fb.reconstruct_bibtex(fm, "smith2026some")
    assert bib.startswith("@inproceedings{smith2026some,")
    assert "booktitle = {CVPR 2026}" in bib
    assert "doi = {10.1109/CVPR.2026.00001}" in bib


def test_reconstruct_escapes_braces_in_title():
    fm = {"title": "Title with {braces}", "authors": ["A B"], "arxiv_id": "2501.00001"}
    bib = fb.reconstruct_bibtex(fm, "b2025title")
    assert "{braces}" not in bib  # 花括号被转义为圆括号
    assert "(braces)" in bib


def test_cache_roundtrip():
    entries = {
        "wen2026openrath": {"source": "arxiv", "bibtex": "@misc{wen2026openrath,\n  title = {X},\n}"},
        "smith2024deep": {"source": "reconstructed", "bibtex": "@article{smith2024deep,\n  title = {Y},\n}"},
    }
    text = fb.serialize_cache(entries)
    parsed = fb.parse_cache(text)
    assert set(parsed) == {"wen2026openrath", "smith2024deep"}
    assert parsed["wen2026openrath"]["source"] == "arxiv"
    assert parsed["smith2024deep"]["source"] == "reconstructed"
    assert parsed["wen2026openrath"]["bibtex"].startswith("@misc{wen2026openrath,")


def test_obtain_bibtex_offline_reconstructs(monkeypatch):
    # 即使有 arxiv_id，offline 模式也不联网，直接重建
    called = {"n": 0}
    monkeypatch.setattr(fb, "fetch_arxiv_bibtex", lambda i: called.__setitem__("n", called["n"] + 1))
    fm = {"title": "T", "authors": ["A B"], "arxiv_id": "2501.00001", "venue": "arXiv"}
    bib, source = fb.obtain_bibtex(fm, "b2025t", offline=True)
    assert source == "reconstructed"
    assert called["n"] == 0  # 没联网


def test_obtain_bibtex_falls_back_when_fetch_fails(monkeypatch):
    # 联网但抓取返回 None → 回退重建
    monkeypatch.setattr(fb, "fetch_arxiv_bibtex", lambda i: None)
    fm = {"title": "T", "authors": ["A B"], "arxiv_id": "2501.00001", "venue": "arXiv"}
    bib, source = fb.obtain_bibtex(fm, "b2025t", offline=False)
    assert source == "reconstructed"


def test_obtain_bibtex_uses_arxiv_when_available(monkeypatch):
    monkeypatch.setattr(fb, "fetch_arxiv_bibtex", lambda i: ARXIV_SAMPLE)
    fm = {"title": "T", "authors": ["A B"], "arxiv_id": "2606.19409", "venue": "arXiv"}
    bib, source = fb.obtain_bibtex(fm, "wen2026openrath", offline=False)
    assert source == "arxiv"
    assert bib.startswith("@misc{wen2026openrath,")
