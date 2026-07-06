#!/usr/bin/env python3
"""
构建论文索引：从 Papers/ 提取元数据 + Summary/Key Results，供 BibTeX 生成与 auto-cite 检索。

用 lib_frontmatter（pyyaml）解析，正确处理多行 authors（修掉旧裸解析 bug）。
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import lib_frontmatter as lf

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPERS_DIR = PROJECT_ROOT / "Papers"
OUTPUT_FILE = Path(__file__).resolve().parent / "paper_index.json"


def extract_section(content: str, heading: str) -> str:
    """提取 `## <heading>` 到下一个 `##` 之间的正文（去掉 %% 注释行）。"""
    m = re.search(rf"## {re.escape(heading)}\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not m:
        return ""
    text = m.group(1)
    # 去掉 Obsidian %% 注释和 markdown 引用块标记
    text = re.sub(r"%%.*?%%", "", text, flags=re.DOTALL)
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith(">")]
    return " ".join(" ".join(lines).split()).strip()


def build_index() -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []
    for paper_file in sorted(PAPERS_DIR.glob("*.md")):
        try:
            content = paper_file.read_text(encoding="utf-8")
        except OSError as e:
            print(f"Warning: cannot read {paper_file.name}: {e}")
            continue
        fm = lf.parse_frontmatter(content)
        if not fm:
            continue
        arxiv_id = str(fm.get("arxiv_id") or "").strip()
        index.append({
            "filename": paper_file.name,
            "cite_key": str(fm.get("cite_key") or "").strip(),
            "title": str(fm.get("title") or ""),
            "authors": lf.as_author_list(fm.get("authors")),
            "year": lf.effective_year(fm.get("date_publish"), arxiv_id),
            "venue": str(fm.get("venue") or ""),
            "arxiv_id": arxiv_id,
            "doi": str(fm.get("doi") or "").strip(),
            "tags": fm.get("tags") if isinstance(fm.get("tags"), list) else [],
            "url": str(fm.get("url") or ""),
            "rating": fm.get("rating", ""),
            "summary": extract_section(content, "Summary"),
            "key_results": extract_section(content, "Key Results"),
        })
    return index


def main() -> int:
    if not PAPERS_DIR.exists():
        print(f"Error: Papers directory not found at {PAPERS_DIR}")
        return 1
    print(f"Building paper index from {PAPERS_DIR}...")
    index = build_index()
    OUTPUT_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    with_key = sum(1 for p in index if p["cite_key"])
    print(f"Indexed {len(index)} papers ({with_key} with cite_key) -> {OUTPUT_FILE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
