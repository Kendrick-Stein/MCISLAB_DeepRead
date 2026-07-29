#!/usr/bin/env python3
"""
LaTeX 引用辅助：抽取已有 \\cite、校验 key 是否在 bib、把缺失 key 从缓存补进 references.bib。

**不做**：判断该不该引、引哪篇（那是 Agent 的判断）；也不做正文插入
（插入由 Agent 用 Edit 在精确位置完成）。本脚本只做机械、安全的校验与补全。

子命令：
    existing <tex>                     列出 .tex 里已有的 cite key
    verify   <tex> [--bib references.bib]   报告 \\cite 里在 bib 中缺失的 key
    ensure-bib <key...> [--bib ...] [--cache ...]   把缺失 key 的条目从缓存补进 bib
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BIB = PROJECT_ROOT / "references.bib"
DEFAULT_CACHE = PROJECT_ROOT / "references" / "bibtex-cache.bib"

# \cite, \citep, \citet, \citeauthor, \cite[p.3]{a,b} 等
_CITE_RE = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")
_BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def existing_cite_keys(tex: str) -> list[str]:
    keys: list[str] = []
    for m in _CITE_RE.finditer(tex):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
    return keys


def bib_keys(bib_text: str) -> set[str]:
    return {m.group(1) for m in _BIB_KEY_RE.finditer(bib_text)}


def parse_cache_entries(cache_text: str) -> dict[str, str]:
    """从 bibtex-cache.bib 解析 {key: entry_text}。"""
    out: dict[str, str] = {}
    blocks = re.split(r"(?m)^(?=@)", cache_text)
    for block in blocks:
        m = _BIB_KEY_RE.search(block)
        if m:
            out[m.group(1)] = block.strip()
    return out


def cmd_existing(args) -> int:
    tex = Path(args.tex).read_text(encoding="utf-8")
    for k in existing_cite_keys(tex):
        print(k)
    return 0


def cmd_verify(args) -> int:
    tex = Path(args.tex).read_text(encoding="utf-8")
    bib = Path(args.bib).read_text(encoding="utf-8") if Path(args.bib).exists() else ""
    have = bib_keys(bib)
    cited = existing_cite_keys(tex)
    missing = [k for k in cited if k not in have]
    print(f"cited keys: {len(cited)} | in bib: {len(cited) - len(missing)} | missing: {len(missing)}")
    for k in missing:
        print(f"  MISSING: {k}")
    return 1 if missing else 0


def cmd_ensure_bib(args) -> int:
    bib_path = Path(args.bib)
    cache_path = Path(args.cache)
    bib_text = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
    have = bib_keys(bib_text)
    cache = parse_cache_entries(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    appended, not_found = [], []
    additions = []
    for key in args.keys:
        if key in have:
            continue
        if key in cache:
            additions.append(cache[key])
            appended.append(key)
        else:
            not_found.append(key)

    if additions:
        sep = "" if bib_text.endswith("\n") or not bib_text else "\n"
        bib_path.write_text(bib_text + sep + "\n".join(additions) + "\n", encoding="utf-8")

    print(f"appended {len(appended)} key(s) to {bib_path.name}: {appended}")
    if not_found:
        print(f"  ⚠ not in cache (run fetch_bibtex.py first): {not_found}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="LaTeX 引用机械辅助（校验/补全，不做判断）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ex = sub.add_parser("existing", help="列出已有 cite key")
    p_ex.add_argument("tex")
    p_ex.set_defaults(func=cmd_existing)

    p_vf = sub.add_parser("verify", help="校验 cite key 是否都在 bib 里")
    p_vf.add_argument("tex")
    p_vf.add_argument("--bib", default=str(DEFAULT_BIB))
    p_vf.set_defaults(func=cmd_verify)

    p_eb = sub.add_parser("ensure-bib", help="把缺失 key 从缓存补进 bib")
    p_eb.add_argument("keys", nargs="+")
    p_eb.add_argument("--bib", default=str(DEFAULT_BIB))
    p_eb.add_argument("--cache", default=str(DEFAULT_CACHE))
    p_eb.set_defaults(func=cmd_ensure_bib)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
