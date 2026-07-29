"""Tests for auto-cite helpers: candidate retrieval + tex cite ops."""
import sys
from pathlib import Path
from types import SimpleNamespace

_AC_DIR = Path(__file__).resolve().parent.parent / "skills" / "4-writing" / "auto-cite"
sys.path.insert(0, str(_AC_DIR))

import retrieve_candidates as rc  # noqa: E402
import tex_cite_ops as tco  # noqa: E402


# ---------------------------------------------------------------------------
# retrieve_candidates
# ---------------------------------------------------------------------------

SYNTH_INDEX = [
    {"cite_key": "shi2026saas", "title": "SaaS-Bench: Computer-Use Agents on SaaS Workflows",
     "tags": ["GUI", "benchmark"], "summary": "long-horizon SaaS workflows, resolved 3.8%",
     "year": "2026", "venue": "arXiv", "key_results": ""},
    {"cite_key": "li2026verifier", "title": "OpenComputer: Programmatic Verifier for CUA",
     "tags": ["verifier"], "summary": "programmatic verifier 94.1% human alignment vs LLM judge 79.2%",
     "year": "2026", "venue": "arXiv", "key_results": ""},
    {"cite_key": "wang2025diffusion", "title": "Diffusion Policy for Robot Manipulation",
     "tags": ["robotics"], "summary": "visuomotor diffusion policy for manipulation",
     "year": "2025", "venue": "RSS", "key_results": ""},
]


def test_retrieve_ranks_relevant_paper_first():
    res = rc.retrieve("long-horizon SaaS workflows have very low success", SYNTH_INDEX, k=3)
    assert res[0]["cite_key"] == "shi2026saas"
    assert "saas" in res[0]["matched_terms"]


def test_retrieve_skips_papers_without_cite_key():
    idx = SYNTH_INDEX + [{"cite_key": "", "title": "No Key SaaS", "summary": "saas", "tags": []}]
    res = rc.retrieve("saas", idx, k=5)
    assert all(r["cite_key"] for r in res)


def test_retrieve_returns_nothing_for_unrelated_query():
    res = rc.retrieve("quantum chromodynamics lattice", SYNTH_INDEX, k=3)
    assert res == []


def test_retrieve_idf_downweights_common_terms():
    # "verifier" 很 distinctive，应让 verifier 论文胜出
    res = rc.retrieve("programmatic verifier alignment", SYNTH_INDEX, k=3)
    assert res[0]["cite_key"] == "li2026verifier"


# ---------------------------------------------------------------------------
# tex_cite_ops
# ---------------------------------------------------------------------------

TEX = r"""
\section{Intro}
Long-horizon GUI tasks remain brittle~\cite{shi2026saas}.
Verifiers beat LLM judges \citep{li2026verifier, someoldkey}.
This sentence has no citation yet.
"""


def test_existing_cite_keys_parses_all_forms():
    keys = tco.existing_cite_keys(TEX)
    assert set(keys) == {"shi2026saas", "li2026verifier", "someoldkey"}


def test_bib_keys_extraction():
    bib = "@misc{shi2026saas,\n title={X},\n}\n@article{li2026verifier, title={Y}}"
    assert tco.bib_keys(bib) == {"shi2026saas", "li2026verifier"}


def test_parse_cache_entries():
    cache = ("% cite_key=shi2026saas source=arxiv\n@misc{shi2026saas,\n title={X},\n}\n"
             "% cite_key=li2026verifier source=reconstructed\n@article{li2026verifier,\n title={Y},\n}\n")
    entries = tco.parse_cache_entries(cache)
    assert set(entries) == {"shi2026saas", "li2026verifier"}
    assert entries["shi2026saas"].startswith("@misc{shi2026saas,")


def test_verify_detects_missing(tmp_path):
    tex = tmp_path / "d.tex"
    tex.write_text(TEX, encoding="utf-8")
    bib = tmp_path / "r.bib"
    bib.write_text("@misc{shi2026saas, title={X}}", encoding="utf-8")  # 缺 li2026verifier, someoldkey
    rc_code = tco.cmd_verify(SimpleNamespace(tex=str(tex), bib=str(bib)))
    assert rc_code == 1  # 有缺失


def test_ensure_bib_appends_from_cache(tmp_path):
    bib = tmp_path / "r.bib"
    bib.write_text("@misc{shi2026saas, title={X}}\n", encoding="utf-8")
    cache = tmp_path / "cache.bib"
    cache.write_text("% cite_key=li2026verifier source=arxiv\n@article{li2026verifier,\n title={Y},\n}\n",
                     encoding="utf-8")
    code = tco.cmd_ensure_bib(SimpleNamespace(
        keys=["shi2026saas", "li2026verifier"], bib=str(bib), cache=str(cache)))
    assert code == 0
    result = bib.read_text(encoding="utf-8")
    assert "@article{li2026verifier," in result  # 新增
    assert result.count("shi2026saas") == 1       # 已有的不重复


def test_ensure_bib_reports_key_not_in_cache(tmp_path):
    bib = tmp_path / "r.bib"
    bib.write_text("", encoding="utf-8")
    cache = tmp_path / "cache.bib"
    cache.write_text("", encoding="utf-8")
    code = tco.cmd_ensure_bib(SimpleNamespace(keys=["ghost2099key"], bib=str(bib), cache=str(cache)))
    assert code == 1  # 报告缺失
