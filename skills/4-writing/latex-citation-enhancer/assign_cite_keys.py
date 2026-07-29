#!/usr/bin/env python3
"""
为 Papers/ 中的论文笔记分配稳定的引用身份：arxiv_id + cite_key，写回 frontmatter。

核心不变量：cite_key 一旦写入就**永久冻结**。本脚本只为没有 cite_key 的论文分配，
绝不改动已有 key；新 key 对"已 pinned key + 本批新分配 key"集合解析碰撞，保证稳定。

用法：
    # 全库 dry-run（不写文件，只打印将分配的 key + 碰撞）
    python3 assign_cite_keys.py --dry-run

    # 全库正式写回
    python3 assign_cite_keys.py

    # 单篇（供 paper-digest 集成）
    python3 assign_cite_keys.py Papers/2606-OpenRath.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import lib_frontmatter as lf

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPERS_DIR = PROJECT_ROOT / "Papers"


def iter_paper_files(targets: list[str]) -> list[Path]:
    """返回要处理的论文文件列表（按文件名排序，保证确定性）。"""
    if targets:
        return [Path(t) if Path(t).is_absolute() else PROJECT_ROOT / t for t in targets]
    return sorted(PAPERS_DIR.glob("*.md"))


def collect_used_keys(files: list[Path]) -> set[str]:
    """收集所有已 pinned 的 cite_key（这些永不改变）。"""
    used: set[str] = set()
    for f in files:
        try:
            fm = lf.parse_frontmatter(f.read_text(encoding="utf-8"))
        except OSError:
            continue
        key = str(fm.get("cite_key") or "").strip()
        if key:
            used.add(key)
    return used


def process(targets: list[str], dry_run: bool) -> int:
    # 全库扫描以建立完整的 used 集合（即使只处理单篇，也要避开全库已有 key）
    all_files = sorted(PAPERS_DIR.glob("*.md"))
    used = collect_used_keys(all_files)

    to_process = iter_paper_files(targets)
    assigned: list[tuple[str, str]] = []  # (filename, cite_key)
    changed_files = 0

    for f in to_process:
        if not f.exists():
            print(f"  skip (not found): {f}", file=sys.stderr)
            continue
        content = f.read_text(encoding="utf-8")
        fm_text, body = lf.split_frontmatter(content)
        if not fm_text:
            print(f"  skip (no frontmatter): {f.name}", file=sys.stderr)
            continue
        fm = lf.parse_frontmatter(content)

        new_fm = fm_text
        file_changed = False

        # arxiv_id（从 url 抽，缺则不写）；同时用于年份回退
        arxiv_id = str(fm.get("arxiv_id") or "").strip() or \
            lf.extract_arxiv_id(str(fm.get("url") or ""), f.name)

        # 1) 写回 arxiv_id（若 frontmatter 缺且能抽到）
        if not str(fm.get("arxiv_id") or "").strip() and arxiv_id:
            new_fm, ch = lf.set_frontmatter_field(new_fm, "arxiv_id", arxiv_id, quote=True)
            file_changed = file_changed or ch

        # 2) cite_key（缺则分配，幂等冻结）
        existing_key = str(fm.get("cite_key") or "").strip()
        if existing_key:
            cite_key = existing_key
        else:
            authors = lf.as_author_list(fm.get("authors"))
            base = lf.base_cite_key(
                authors, fm.get("date_publish"), str(fm.get("title") or ""),
                year_fallback=lf.year_from_arxiv_id(arxiv_id),
            )
            cite_key = lf.resolve_cite_key(base, used)
            used.add(cite_key)  # 立刻占位，避免本批后续碰撞
            new_fm, ch = lf.set_frontmatter_field(new_fm, "cite_key", cite_key)
            file_changed = file_changed or ch
            assigned.append((f.name, cite_key))

        if file_changed and not dry_run:
            f.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")
            changed_files += 1
        elif file_changed:
            changed_files += 1

    # 报告
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"\n[{mode}] processed {len(to_process)} file(s); "
          f"{len(assigned)} new cite_key(s); {changed_files} file(s) changed.")
    if assigned:
        print("新分配 cite_key（前 30）：")
        for name, key in assigned[:30]:
            print(f"  {key:32s} <- {name}")
        if len(assigned) > 30:
            print(f"  … 还有 {len(assigned) - 30} 个")
    # 碰撞统计
    suffixed = [k for _, k in assigned if k and k[-1].isalpha() and k[:-1] in used]
    if suffixed:
        print(f"\n碰撞（加后缀）的 key 数：{len(suffixed)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="分配 arxiv_id + cite_key 到论文 frontmatter")
    ap.add_argument("targets", nargs="*", help="指定论文文件（默认全库 Papers/*.md）")
    ap.add_argument("--dry-run", action="store_true", help="只打印不写文件")
    args = ap.parse_args()
    return process(args.targets, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
