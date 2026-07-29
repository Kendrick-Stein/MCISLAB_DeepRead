#!/usr/bin/env python3
"""
共享工具：frontmatter 解析 + cite_key 生成。

被 assign_cite_keys.py / build_paper_index.py / generate_bibtex.py / fetch_bibtex.py 复用。
解析用 pyyaml（正确处理多行 `authors:` 列表，修掉旧 build_paper_index.py 的裸解析 bug）。

核心不变量（见 plan）：
- cite_key 由论文自身元数据**确定性**生成，不依赖语料库遍历顺序。
- 碰撞 tiebreak 用 a/b/c 后缀，针对一个**已用 key 集合**解析——调用方负责把已 pinned 的
  key 放进 used 集合，从而保证"已写入的 key 永不改变"。
"""
from __future__ import annotations

import re
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Frontmatter 解析
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def split_frontmatter(content: str) -> tuple[str, str]:
    """返回 (frontmatter_text, body)。无 frontmatter 时 frontmatter_text 为空串。"""
    m = _FM_RE.match(content)
    if not m:
        return "", content
    return m.group(1), m.group(2)


def parse_frontmatter(content: str) -> dict[str, Any]:
    """用 pyyaml 解析 frontmatter，返回 dict（解析失败返回 {}）。"""
    fm_text, _ = split_frontmatter(content)
    if not fm_text.strip():
        return {}
    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def as_author_list(value: Any) -> list[str]:
    """把 frontmatter 的 authors 字段规整成字符串列表。

    支持三种来源：YAML 列表（多行或 inline [])、逗号分隔字符串、单个字符串。
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(a).strip() for a in value if str(a).strip()]
    if isinstance(value, str):
        # 逗号分隔（daily-papers 候选格式）或单作者
        parts = [p.strip() for p in value.split(",")]
        return [p for p in parts if p]
    return []


# ---------------------------------------------------------------------------
# arXiv id 抽取
# ---------------------------------------------------------------------------

# 现代 arXiv id：YYMM.NNNNN（4 位月份 . 4-5 位序号），可带版本后缀 vN
_ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(?:v\d+)?")


def extract_arxiv_id(*sources: str) -> str:
    """从 url / 文件名等来源里抽 arXiv id（无则返回 ""）。"""
    for s in sources:
        if not s:
            continue
        m = _ARXIV_RE.search(str(s))
        if m:
            return m.group(1)
    return ""


# ---------------------------------------------------------------------------
# cite_key 生成
# ---------------------------------------------------------------------------

# 仅冠词/介词/连词等功能词，不含 learning/deep 等内容词
_STOPWORDS = {
    "a", "an", "the", "on", "of", "for", "to", "in", "with", "and", "or",
    "via", "at", "by", "from", "towards", "toward", "into", "over", "under",
    "is", "are", "be", "as", "that", "this", "we", "our", "using", "use",
}


def first_author_lastname(authors: list[str]) -> str:
    """取第一作者的姓，只留字母，小写。

    两种格式：
    - "Firstname Lastname"（如 "Fukang Wen"）→ 取最后一个 token。
    - "Lastname, F."（BibTeX 风格，如 "Isabella, A."）→ 取逗号前的部分。
    """
    if not authors:
        return ""
    a = authors[0]
    surname_part = a.split(",")[0] if "," in a else a
    tokens = re.sub(r"[^A-Za-z\s]", "", surname_part).split()
    if not tokens:
        return ""
    return tokens[-1].lower()


def first_title_word(title: str) -> str:
    """取标题里第一个非停用词、长度>1 的实词，只留字母数字，小写。"""
    words = re.split(r"[^0-9A-Za-z]+", title or "")
    for w in words:
        wl = w.lower()
        if len(wl) > 1 and wl not in _STOPWORDS:
            return re.sub(r"[^0-9a-z]", "", wl)
    return ""


def year_of(date_publish: Any) -> str:
    """从 date_publish 取 4 位年份。"""
    s = str(date_publish or "")
    m = re.match(r"(\d{4})", s)
    return m.group(1) if m else ""


def year_from_arxiv_id(arxiv_id: str) -> str:
    """从 arXiv id 的 YYMM 前缀推年份（现代 id：25xx→2025）。无法判断返回 ""。"""
    m = re.match(r"(\d{2})(\d{2})\.", str(arxiv_id or ""))
    if not m:
        return ""
    yy = int(m.group(1))
    # arXiv 新方案始于 2007（0704）；两位年份一律视为 20xx
    return f"20{yy:02d}"


def effective_year(date_publish: Any, arxiv_id: str = "") -> str:
    """优先 date_publish 的年份，缺失则回退到 arXiv id 前缀。"""
    return year_of(date_publish) or year_from_arxiv_id(arxiv_id)


def base_cite_key(authors: list[str], date_publish: Any, title: str,
                  *, year_fallback: str = "") -> str:
    """生成基础 cite_key：{lastname}{year}{firstTitleWord}，全小写。

    缺字段时优雅降级：无作者→用标题词；无年→用 year_fallback（如 arXiv 推断的年份），
    仍无则省略年；最终保证非空。
    """
    lastname = first_author_lastname(authors)
    year = year_of(date_publish) or year_fallback
    word = first_title_word(title)

    if lastname:
        key = f"{lastname}{year}{word}"
    elif word:
        # 无作者：用标题词兜底
        key = f"{word}{year}"
    else:
        key = f"paper{year}"
    return key or "paper"


def resolve_cite_key(base: str, used: set[str]) -> str:
    """对已用 key 集合解析碰撞：base 空闲则用 base，否则依次试 base+a/b/c…

    调用方必须把"已 pinned 的 key + 本批已分配的 key"都放进 used，
    才能保证已写入的 key 永不变。
    """
    if base not in used:
        return base
    # a, b, ..., z, aa, ab, ...
    import string
    suffixes = list(string.ascii_lowercase)
    i = 0
    while True:
        if i < len(suffixes):
            suf = suffixes[i]
        else:
            # 超过 26 个碰撞：用双字母
            q, r = divmod(i, len(suffixes))
            suf = suffixes[q - 1] + suffixes[r]
        cand = f"{base}{suf}"
        if cand not in used:
            return cand
        i += 1


# ---------------------------------------------------------------------------
# 写回 frontmatter（外科手术式，保留其余行/注释/格式不变）
# ---------------------------------------------------------------------------

def _format_value(value: str, quote: bool) -> str:
    return f'"{value}"' if quote else value


def set_frontmatter_field(
    fm_text: str,
    key: str,
    value: str,
    *,
    quote: bool = False,
    insert_after: tuple[str, ...] = ("url", "date_publish", "venue"),
) -> tuple[str, bool]:
    """在 frontmatter 文本里设置 key=value，返回 (new_fm_text, changed)。

    规则（保证幂等 + 不覆盖已 pinned 值）：
    - 已有 `key:` 且值非空 → 不动（返回 changed=False）。
    - 已有 `key:` 但值为空 → 原地填值。
    - 无该行 → 在 insert_after 里第一个出现的字段行后插入；都没有则追加到末尾。
    """
    if not value:
        return fm_text, False

    lines = fm_text.split("\n")
    line_re = re.compile(rf"^{re.escape(key)}:\s*(.*)$")
    formatted = f"{key}: {_format_value(value, quote)}"

    for idx, line in enumerate(lines):
        m = line_re.match(line)
        if m:
            if m.group(1).strip():
                return fm_text, False  # 已有非空值，不覆盖
            lines[idx] = formatted
            return "\n".join(lines), True

    # 未找到 → 选插入位置
    insert_idx = len(lines)
    for anchor in insert_after:
        anchor_re = re.compile(rf"^{re.escape(anchor)}:")
        hit = next((i for i, ln in enumerate(lines) if anchor_re.match(ln)), None)
        if hit is not None:
            insert_idx = hit + 1
            break
    lines.insert(insert_idx, formatted)
    return "\n".join(lines), True
