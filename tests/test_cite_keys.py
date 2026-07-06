"""Tests for lib_frontmatter: frontmatter parsing + deterministic cite_key generation."""
import sys
from pathlib import Path

import pytest

# 让测试能 import skills/4-writing/latex-citation-enhancer/lib_frontmatter.py
_LIB_DIR = Path(__file__).resolve().parent.parent / "skills" / "4-writing" / "latex-citation-enhancer"
sys.path.insert(0, str(_LIB_DIR))

import lib_frontmatter as lf  # noqa: E402


# ---------------------------------------------------------------------------
# Frontmatter 解析：多行 authors（旧裸解析器读不了的格式）
# ---------------------------------------------------------------------------

MULTILINE = """---
title: "OpenRath: Session-Centered Runtime State for Agent Systems"
authors:
  - Fukang Wen
  - Zhijie Wang
  - Ruilin Xu
date_publish: 2026-06-17
venue: arXiv
url: "https://arxiv.org/abs/2606.19409"
---
## Summary
body here
"""

INLINE = """---
title: "Foo Bar"
authors: [Alice Smith, Bob Jones]
date_publish: 2025-03
url: "https://arxiv.org/abs/2503.18065"
---
body
"""


def test_parse_multiline_authors():
    fm = lf.parse_frontmatter(MULTILINE)
    authors = lf.as_author_list(fm["authors"])
    assert authors == ["Fukang Wen", "Zhijie Wang", "Ruilin Xu"]


def test_parse_inline_authors():
    fm = lf.parse_frontmatter(INLINE)
    authors = lf.as_author_list(fm["authors"])
    assert authors == ["Alice Smith", "Bob Jones"]


def test_as_author_list_from_comma_string():
    assert lf.as_author_list("Wei Zhou, Xuanhe Zhou, Fan Wu") == [
        "Wei Zhou", "Xuanhe Zhou", "Fan Wu"
    ]


def test_as_author_list_empty():
    assert lf.as_author_list(None) == []
    assert lf.as_author_list("") == []
    assert lf.as_author_list([]) == []


def test_split_frontmatter_no_fm():
    fm_text, body = lf.split_frontmatter("no frontmatter here")
    assert fm_text == ""
    assert body == "no frontmatter here"


def test_parse_bad_yaml_returns_empty():
    assert lf.parse_frontmatter("---\n: : : bad\n---\nbody") == {}


# ---------------------------------------------------------------------------
# arXiv id 抽取
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("src,expected", [
    ("https://arxiv.org/abs/2606.19409", "2606.19409"),
    ("https://arxiv.org/abs/2503.18065v2", "2503.18065"),
    ("http://arxiv.org/abs/2406.19255", "2406.19255"),
    ("https://example.com/paper", ""),
    ("", ""),
])
def test_extract_arxiv_id(src, expected):
    assert lf.extract_arxiv_id(src) == expected


def test_extract_arxiv_id_multi_source():
    # 第一个来源无，第二个有
    assert lf.extract_arxiv_id("https://foo.com", "2503.18065") == "2503.18065"


# ---------------------------------------------------------------------------
# cite_key 生成：确定性 + 格式
# ---------------------------------------------------------------------------

def test_base_cite_key_basic():
    key = lf.base_cite_key(["Fukang Wen", "Zhijie Wang"], "2026-06-17",
                           "OpenRath: Session-Centered Runtime State")
    assert key == "wen2026openrath"


def test_base_cite_key_skips_stopwords():
    key = lf.base_cite_key(["Jane Doe"], "2025", "Towards Robust GUI Grounding")
    # "Towards" 是停用词 → 取 "robust"
    assert key == "doe2025robust"


def test_base_cite_key_deterministic():
    args = (["Alice Smith"], "2024-01", "Deep Learning for Vision")
    assert lf.base_cite_key(*args) == lf.base_cite_key(*args)


def test_base_cite_key_no_authors_fallback():
    key = lf.base_cite_key([], "2025", "Mysterious Anonymous Report")
    assert key == "mysterious2025"


def test_base_cite_key_never_empty():
    assert lf.base_cite_key([], "", "") != ""


def test_lastname_handles_surname_comma_initial():
    # "Isabella, A." → 姓是逗号前的 Isabella，不是缩写 A
    assert lf.first_author_lastname(["Isabella, A."]) == "isabella"
    assert lf.first_author_lastname(["Bredell, F."]) == "bredell"


def test_lastname_handles_chinese_surnames():
    assert lf.first_author_lastname(["Toby Jia-Jun Li"]) == "li"
    assert lf.first_author_lastname(["Dong An"]) == "an"


def test_year_from_arxiv_id():
    assert lf.year_from_arxiv_id("2403.17918") == "2024"
    assert lf.year_from_arxiv_id("1404.6779") == "2014"
    assert lf.year_from_arxiv_id("2205.11029") == "2022"
    assert lf.year_from_arxiv_id("") == ""
    assert lf.year_from_arxiv_id("notanid") == ""


def test_effective_year_prefers_date_then_arxiv():
    assert lf.effective_year("2025-03-01", "2403.17918") == "2025"
    assert lf.effective_year(None, "2403.17918") == "2024"
    assert lf.effective_year("", "") == ""


def test_year_fallback_in_base_key():
    # date_publish 缺失，但 arXiv 推断年份补上
    key = lf.base_cite_key(["Jane Doe"], None, "AgentStudio Toolkit",
                           year_fallback=lf.year_from_arxiv_id("2403.17918"))
    assert key == "doe2024agentstudio"


# ---------------------------------------------------------------------------
# 碰撞解析 + 稳定性（核心不变量）
# ---------------------------------------------------------------------------

def test_resolve_no_collision():
    assert lf.resolve_cite_key("wen2026openrath", set()) == "wen2026openrath"


def test_resolve_collision_appends_suffix():
    used = {"smith2024deep"}
    assert lf.resolve_cite_key("smith2024deep", used) == "smith2024deepa"
    used.add("smith2024deepa")
    assert lf.resolve_cite_key("smith2024deep", used) == "smith2024deepb"


def test_stability_existing_keys_never_change():
    """核心不变量：已 pinned 的 key 在新论文加入后绝不改变。

    模拟：先有一篇 paper A 已分配 smith2024deep；新论文 B base key 相同，
    必须让 B 退让（拿后缀），A 保持不变。
    """
    used = set()
    # paper A 先分配并 pin
    key_a = lf.resolve_cite_key("smith2024deep", used)
    used.add(key_a)
    assert key_a == "smith2024deep"

    # 之后 paper B base 相同 → B 退让
    key_b = lf.resolve_cite_key("smith2024deep", used)
    used.add(key_b)
    assert key_b == "smith2024deepa"

    # A 的 key 仍是原值（从未重算）
    assert key_a == "smith2024deep"


def test_collision_resolution_order_independent_given_used_set():
    """只要 used 集合相同，解析结果确定（与论文遍历顺序无关）。"""
    base = "li2026agent"
    used1 = {"li2026agent", "li2026agenta"}
    used2 = {"li2026agenta", "li2026agent"}  # 不同插入顺序
    assert lf.resolve_cite_key(base, used1) == lf.resolve_cite_key(base, used2) == "li2026agentb"


# ---------------------------------------------------------------------------
# set_frontmatter_field：写回不破坏其余内容
# ---------------------------------------------------------------------------

FM_TEXT = (
    'title: "Foo"\n'
    "authors:\n"
    "  - Alice Smith\n"
    "date_publish: 2025-03\n"
    "venue: arXiv\n"
    'url: "https://arxiv.org/abs/2503.18065"\n'
    "code:\n"
    'date_added: "2025-03-10"'
)


def test_set_field_inserts_after_url():
    new, changed = lf.set_frontmatter_field(FM_TEXT, "cite_key", "smith2025foo")
    assert changed
    lines = new.split("\n")
    url_idx = next(i for i, l in enumerate(lines) if l.startswith("url:"))
    assert lines[url_idx + 1] == "cite_key: smith2025foo"
    # 其余行保持
    assert 'title: "Foo"' in new
    assert "  - Alice Smith" in new


def test_set_field_quotes_when_requested():
    new, _ = lf.set_frontmatter_field(FM_TEXT, "arxiv_id", "2503.18065", quote=True)
    assert 'arxiv_id: "2503.18065"' in new


def test_set_field_fills_empty_existing():
    new, changed = lf.set_frontmatter_field(FM_TEXT, "code", "https://github.com/x/y")
    assert changed
    assert "code: https://github.com/x/y" in new


def test_set_field_does_not_overwrite_nonempty():
    new, changed = lf.set_frontmatter_field(FM_TEXT, "venue", "NeurIPS 2025")
    assert not changed
    assert new == FM_TEXT


def test_set_field_idempotent():
    once, _ = lf.set_frontmatter_field(FM_TEXT, "cite_key", "smith2025foo")
    twice, changed = lf.set_frontmatter_field(once, "cite_key", "smith2025foo")
    assert not changed
    assert twice == once


def test_set_field_parses_back_with_yaml():
    """写回后仍是合法 YAML，且新字段可被解析。"""
    new, _ = lf.set_frontmatter_field(FM_TEXT, "arxiv_id", "2503.18065", quote=True)
    new, _ = lf.set_frontmatter_field(new, "cite_key", "smith2025foo")
    fm = lf.parse_frontmatter(f"---\n{new}\n---\nbody")
    assert fm["arxiv_id"] == "2503.18065"
    assert fm["cite_key"] == "smith2025foo"
    assert lf.as_author_list(fm["authors"]) == ["Alice Smith"]
