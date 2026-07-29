#!/usr/bin/env python3
"""
候选检索：给一段 claim/query 文本，从 paper_index.json 里返回最相关的 top-K 论文。

**只做候选生成，不做最终判断**——是否真支撑某句 claim 由 Agent 读 summary 后决定
（见 auto-cite SKILL.md Step 4）。打分 = 字段加权 TF × IDF（IDF 压低 "agent"/"gui"
这类全库高频词，突出 distinctive 术语）。

用法：
    python3 retrieve_candidates.py "claim text ..." --k 5
    python3 retrieve_candidates.py --query-file claim.txt --k 8 --json
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

INDEX_FILE = Path(__file__).resolve().parents[1] / "latex-citation-enhancer" / "paper_index.json"

_STOP = {
    "the", "a", "an", "of", "for", "to", "in", "on", "with", "and", "or", "via",
    "is", "are", "be", "by", "that", "this", "we", "our", "as", "at", "from",
    "it", "its", "can", "than", "which", "these", "those", "their", "such",
    "using", "use", "used", "show", "shows", "shown", "propose", "proposed",
    "method", "approach", "paper", "model", "models", "results", "result",
}

_FIELD_WEIGHTS = {
    "title": 3.0,
    "tags": 3.0,
    "cite_key": 2.0,
    "authors": 1.0,
    "venue": 1.0,
    "summary": 1.0,
    "key_results": 1.0,
}


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", str(text).lower())
            if len(w) > 1 and w not in _STOP]


def _field_text(paper: dict, field: str) -> str:
    val = paper.get(field, "")
    if isinstance(val, list):
        return " ".join(str(v) for v in val)
    return str(val)


def build_df(papers: list[dict]) -> dict[str, int]:
    """文档频率：term 出现在多少篇论文的合并文本里。"""
    df: dict[str, int] = {}
    for p in papers:
        blob = " ".join(_field_text(p, f) for f in _FIELD_WEIGHTS)
        for term in set(tokenize(blob)):
            df[term] = df.get(term, 0) + 1
    return df


def score_paper(paper: dict, query_terms: list[str], idf: dict[str, float]) -> tuple[float, list[str]]:
    """返回 (score, matched_terms)。"""
    score = 0.0
    matched: set[str] = set()
    qset = set(query_terms)
    for field, weight in _FIELD_WEIGHTS.items():
        field_tokens = tokenize(_field_text(paper, field))
        if not field_tokens:
            continue
        tf: dict[str, int] = {}
        for t in field_tokens:
            if t in qset:
                tf[t] = tf.get(t, 0) + 1
        for t, count in tf.items():
            score += weight * (1 + math.log(count)) * idf.get(t, 1.0)
            matched.add(t)
    return score, sorted(matched)


def retrieve(query: str, papers: list[dict], k: int = 5) -> list[dict]:
    n = max(len(papers), 1)
    df = build_df(papers)
    idf = {t: math.log(1 + n / (1 + c)) for t, c in df.items()}
    query_terms = tokenize(query)

    scored = []
    for p in papers:
        if not p.get("cite_key"):
            continue  # 无 key 无法引用
        s, matched = score_paper(p, query_terms, idf)
        if s > 0:
            scored.append((s, matched, p))
    scored.sort(key=lambda x: x[0], reverse=True)

    out = []
    for s, matched, p in scored[:k]:
        summary = p.get("summary", "") or p.get("key_results", "")
        out.append({
            "cite_key": p["cite_key"],
            "title": p.get("title", ""),
            "year": p.get("year", ""),
            "venue": p.get("venue", ""),
            "score": round(s, 2),
            "matched_terms": matched,
            "summary": summary[:400],
            "filename": p.get("filename", ""),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="auto-cite 候选检索（候选生成，非最终判断）")
    ap.add_argument("query", nargs="?", default="", help="claim/query 文本")
    ap.add_argument("--query-file", help="从文件读 query")
    ap.add_argument("--k", type=int, default=5, help="返回候选数")
    ap.add_argument("--index", default=str(INDEX_FILE), help="paper_index.json 路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON（默认人类可读）")
    args = ap.parse_args()

    query = args.query
    if args.query_file:
        query = Path(args.query_file).read_text(encoding="utf-8")
    if not query.strip():
        ap.error("需要 query 文本或 --query-file")

    index_path = Path(args.index)
    if not index_path.exists():
        ap.error(f"{index_path} 不存在，请先跑 build_paper_index.py")
    papers = json.loads(index_path.read_text(encoding="utf-8"))
    results = retrieve(query, papers, args.k)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("（无候选——知识库可能没有相关论文，考虑先 paper-digest 补论文）")
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r['cite_key']}] ({r['year']}) {r['title']}")
            print(f"   score={r['score']} matched={r['matched_terms']}")
            if r["summary"]:
                print(f"   {r['summary'][:160]}")
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
