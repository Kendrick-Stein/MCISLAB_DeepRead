#!/usr/bin/env python3
"""按 team-config news.sources 抓取 RSS/Atom，按 interests 关键词打分，输出候选 JSON。

用法: python3 skills/1-literature/news-digest/fetch_news.py \
        [--days 3] [--output Workbench/daily/.news-candidates.json]
type=web 的源不在此抓取（脚本只列出其 URL，由 agent 用 WebFetch/lexmount 处理）。
"""
import argparse
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEAM_CONFIG = ROOT / "Workbench" / "config" / "team-config.json"
UA = {"User-Agent": "ReadPaperMachine-news/1.0"}


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def _parse_date(s: str):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)  # RFC822 (RSS2)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))  # ISO (Atom)
    except ValueError:
        return None


def _atom_link(entry, ns) -> str:
    """选 Atom entry 的正文链接：rel="alternate" 或无 rel 优先，否则退回第一个 link。"""
    links = entry.findall("a:link", ns)
    for el in links:
        if el.get("rel") in (None, "alternate"):
            return el.get("href", "")
    return links[0].get("href", "") if links else ""


def parse_feed(xml_text: str) -> list[dict]:
    """解析 RSS2 <item> 与 Atom <entry>，返回 {title, link, summary, published}。"""
    root = ET.fromstring(xml_text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for it in root.iter("item"):  # RSS2
        items.append({
            "title": _text(it.find("title")),
            "link": _text(it.find("link")),
            "summary": _text(it.find("description")),
            "published": _parse_date(_text(it.find("pubDate"))),
        })
    for it in root.findall(".//a:entry", ns):  # Atom
        items.append({
            "title": _text(it.find("a:title", ns)),
            "link": _atom_link(it, ns),
            "summary": _text(it.find("a:summary", ns)) or _text(it.find("a:content", ns)),
            "published": _parse_date(_text(it.find("a:updated", ns)) or _text(it.find("a:published", ns))),
        })
    return items


def _norm(s: str) -> str:
    """匹配归一化：小写 + 连字符视为空格（与 scripts/survey_updates.py 一致）。"""
    return s.lower().replace("-", " ")


def score_item(item: dict, keywords: list[str]) -> int:
    hay = _norm(item.get("title", "") + " " + item.get("summary", ""))
    return sum(1 for kw in keywords if _norm(kw) in hay)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--output", default="Workbench/daily/.news-candidates.json")
    args = ap.parse_args()

    cfg = json.loads(TEAM_CONFIG.read_text(encoding="utf-8"))
    news_cfg = cfg.get("news", {})
    days = args.days or news_cfg.get("days", 3)
    keywords = [kw for it in cfg.get("interests", []) for kw in it.get("keywords", [])]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    candidates, web_sources, errors = [], [], []
    for src in news_cfg.get("sources", []):
        if src.get("type") == "web":
            web_sources.append(src)
            continue
        try:
            with urllib.request.urlopen(
                urllib.request.Request(src["url"], headers=UA), timeout=30
            ) as resp:
                items = parse_feed(resp.read().decode("utf-8", errors="replace"))
        except Exception as e:  # 单源失败跳过，不阻塞（spec §9）
            errors.append({"source": src["name"], "error": str(e)})
            continue
        if not items:  # 抓到了但解析出 0 条 → 显式报告，避免静默失败
            errors.append({"source": src["name"],
                           "error": "0 items parsed (RSS1.0/RDF or empty feed?)"})
            continue
        for it in items:
            pub = it.pop("published")
            if pub and pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub and pub < cutoff:
                continue
            score = score_item(it, keywords)
            if score >= news_cfg.get("min_score", 1):
                candidates.append({**it, "source": src["name"],
                                   "published": pub.isoformat() if pub else None,
                                   "score": score})

    candidates.sort(key=lambda c: (c["score"], c["published"] or ""), reverse=True)
    out = {"fetched_at": datetime.now(timezone.utc).isoformat(),
           "days": days,
           "candidates": candidates[: news_cfg.get("top_n", 20)],
           "web_sources": web_sources,
           "errors": errors}
    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(out['candidates'])} candidates, {len(web_sources)} web sources, {len(errors)} errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
