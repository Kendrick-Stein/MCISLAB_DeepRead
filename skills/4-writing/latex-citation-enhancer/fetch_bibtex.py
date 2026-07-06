#!/usr/bin/env python3
"""
为每篇论文获取**权威 BibTeX**，存入 references/bibtex-cache.bib（按 cite_key 索引）。

来源优先级（混合策略，能抓就抓，抓不到重建）：
  1. arxiv_id → https://arxiv.org/bibtex/<id>（arXiv 官方导出，@misc）
  2. doi      → https://doi.org/<doi>（Crossref content negotiation）
  3. 都无/失败 → 从 frontmatter 重建（标 source=reconstructed）

每个 cache entry 前有 provenance 注释：`% cite_key=<k> source=<arxiv|crossref|reconstructed>`。
缓存里已存在的 cite_key 默认跳过（不重复抓网）；`--force` 全部重抓；
`--upgrade` 只重抓当前是 reconstructed 的条目。

用法：
    python3 fetch_bibtex.py                  # 全库，缺啥补啥
    python3 fetch_bibtex.py Papers/2606-OpenRath.md   # 单篇（供 paper-digest 集成）
    python3 fetch_bibtex.py --offline        # 不联网，只重建缺失项
"""
from __future__ import annotations

import argparse
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

import lib_frontmatter as lf

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPERS_DIR = PROJECT_ROOT / "Papers"
CACHE_PATH = PROJECT_ROOT / "references" / "bibtex-cache.bib"

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


# ---------------------------------------------------------------------------
# 纯函数（可测，无网络）
# ---------------------------------------------------------------------------

_ENTRY_HEAD_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.DOTALL)


def rewrite_key(bibtex: str, cite_key: str) -> str:
    """把 BibTeX 条目的 citation key 改成我们 pinned 的 cite_key（保留 entry type）。"""
    return _ENTRY_HEAD_RE.sub(lambda m: f"@{m.group(1)}{{{cite_key},", bibtex, count=1)


def looks_like_bibtex(text: str) -> bool:
    return bool(text) and bool(_ENTRY_HEAD_RE.search(text))


def _bib_escape(text: str) -> str:
    return (text or "").replace("{", "(").replace("}", ")").strip()


def reconstruct_bibtex(fm: dict, cite_key: str) -> str:
    """从 frontmatter 字段无幻觉地重建一个 BibTeX 条目。"""
    title = _bib_escape(str(fm.get("title") or ""))
    authors = lf.as_author_list(fm.get("authors"))
    author_str = " and ".join(authors)
    arxiv_id = str(fm.get("arxiv_id") or "").strip()
    year = lf.effective_year(fm.get("date_publish"), arxiv_id)
    venue = str(fm.get("venue") or "").strip()
    url = str(fm.get("url") or "").strip()
    doi = str(fm.get("doi") or "").strip()

    is_arxiv = bool(arxiv_id) or "arxiv" in venue.lower()
    lines = []
    if is_arxiv:
        lines.append(f"@misc{{{cite_key},")
        lines.append(f"  title = {{{title}}},")
        if author_str:
            lines.append(f"  author = {{{author_str}}},")
        if year:
            lines.append(f"  year = {{{year}}},")
        if arxiv_id:
            lines.append(f"  eprint = {{{arxiv_id}}},")
            lines.append("  archivePrefix = {arXiv},")
        if url:
            lines.append(f"  url = {{{url}}},")
    else:
        etype = "inproceedings" if venue else "article"
        lines.append(f"@{etype}{{{cite_key},")
        lines.append(f"  title = {{{title}}},")
        if author_str:
            lines.append(f"  author = {{{author_str}}},")
        if year:
            lines.append(f"  year = {{{year}}},")
        if venue:
            field = "booktitle" if etype == "inproceedings" else "journal"
            lines.append(f"  {field} = {{{_bib_escape(venue)}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        if url:
            lines.append(f"  url = {{{url}}},")
    lines.append("}")
    return "\n".join(lines)


def parse_cache(text: str) -> dict[str, dict]:
    """解析 cache 文件，返回 {cite_key: {"source": str, "bibtex": str}}。"""
    out: dict[str, dict] = {}
    # 按 provenance 注释切块；没有注释的裸条目也兜底解析
    blocks = re.split(r"(?m)^(?=% cite_key=)", text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        src_m = re.match(r"% cite_key=(\S+)\s+source=(\S+)", block)
        m = _ENTRY_HEAD_RE.search(block)
        if not m:
            continue
        key = m.group(2)
        source = src_m.group(2) if src_m else "unknown"
        bib = block[m.start():].strip()
        out[key] = {"source": source, "bibtex": bib}
    return out


def serialize_cache(entries: dict[str, dict]) -> str:
    """把 {cite_key: {...}} 序列化成 cache 文件文本（按 cite_key 排序）。"""
    parts = ["% BibTeX cache for ReadPaperMachine — 按 cite_key 索引，权威源优先。",
             "% 由 fetch_bibtex.py 维护，勿手改（手改会在下次运行被覆盖）。\n"]
    for key in sorted(entries):
        e = entries[key]
        parts.append(f"% cite_key={key} source={e['source']}")
        parts.append(e["bibtex"].strip())
        parts.append("")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# 网络抓取
# ---------------------------------------------------------------------------

def _http_get(url: str, headers: dict | None = None, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_arxiv_bibtex(arxiv_id: str) -> str | None:
    try:
        text = _http_get(f"https://arxiv.org/bibtex/{arxiv_id}")
    except (urllib.error.URLError, OSError, TimeoutError):
        return None
    return text.strip() if looks_like_bibtex(text) else None


def fetch_crossref_bibtex(doi: str) -> str | None:
    try:
        text = _http_get(f"https://doi.org/{doi}",
                         headers={"Accept": "application/x-bibtex"})
    except (urllib.error.URLError, OSError, TimeoutError):
        return None
    return text.strip() if looks_like_bibtex(text) else None


def obtain_bibtex(fm: dict, cite_key: str, offline: bool) -> tuple[str, str]:
    """返回 (bibtex_text, source)。会把 key 改写成 cite_key。"""
    arxiv_id = str(fm.get("arxiv_id") or "").strip()
    doi = str(fm.get("doi") or "").strip()

    if not offline and arxiv_id:
        raw = fetch_arxiv_bibtex(arxiv_id)
        if raw:
            return rewrite_key(raw, cite_key), "arxiv"
    if not offline and doi:
        raw = fetch_crossref_bibtex(doi)
        if raw:
            return rewrite_key(raw, cite_key), "crossref"
    return reconstruct_bibtex(fm, cite_key), "reconstructed"


# ---------------------------------------------------------------------------
# 驱动
# ---------------------------------------------------------------------------

def load_papers(targets: list[str]) -> list[Path]:
    if targets:
        return [Path(t) if Path(t).is_absolute() else PROJECT_ROOT / t for t in targets]
    return sorted(PAPERS_DIR.glob("*.md"))


def run(targets: list[str], *, offline: bool, force: bool, upgrade: bool,
        delay: float = 0.34) -> int:
    cache = parse_cache(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    files = load_papers(targets)
    counts = {"arxiv": 0, "crossref": 0, "reconstructed": 0, "skipped": 0, "no_key": 0}

    for f in files:
        if not f.exists():
            continue
        fm = lf.parse_frontmatter(f.read_text(encoding="utf-8"))
        cite_key = str(fm.get("cite_key") or "").strip()
        if not cite_key:
            counts["no_key"] += 1
            continue

        cached = cache.get(cite_key)
        need = force or cached is None or (upgrade and cached["source"] == "reconstructed")
        if not need:
            counts["skipped"] += 1
            continue

        bibtex, source = obtain_bibtex(fm, cite_key, offline)
        cache[cite_key] = {"source": source, "bibtex": bibtex}
        counts[source] += 1
        # 抓网后礼貌性 sleep（重建/离线不 sleep）
        if not offline and source in ("arxiv", "crossref"):
            time.sleep(delay)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(serialize_cache(cache), encoding="utf-8")

    print(f"cache: {CACHE_PATH.relative_to(PROJECT_ROOT)} | total entries: {len(cache)}")
    print(f"  fetched arxiv={counts['arxiv']} crossref={counts['crossref']} "
          f"reconstructed={counts['reconstructed']} "
          f"skipped(cached)={counts['skipped']} no_cite_key={counts['no_key']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="抓取/重建权威 BibTeX 到 cache")
    ap.add_argument("targets", nargs="*", help="指定论文（默认全库）")
    ap.add_argument("--offline", action="store_true", help="不联网，只重建缺失项")
    ap.add_argument("--force", action="store_true", help="忽略缓存，全部重抓")
    ap.add_argument("--upgrade", action="store_true",
                    help="只重抓当前是 reconstructed 的条目（联网升级）")
    ap.add_argument("--delay", type=float, default=0.34,
                    help="每次联网抓取后的礼貌性延迟秒数（默认 0.34）")
    args = ap.parse_args()
    return run(args.targets, offline=args.offline, force=args.force,
               upgrade=args.upgrade, delay=args.delay)


if __name__ == "__main__":
    raise SystemExit(main())
