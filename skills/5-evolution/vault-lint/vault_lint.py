#!/usr/bin/env python3
"""vault-lint: 对 vault 内容目录跑机械质量检查。

检查项（对应 Workbench/memory 中反复出现的故障类）：
  yaml         frontmatter 可解析、authors/institute 为 list、title/venue 未被误解析为 dict
  cite-key     Papers/ 笔记 cite_key 缺失或为空（含 "" 引号陷阱：assign_cite_keys 会静默跳过）
  wikilink     [[...]] 与 ![[...]] 指向的文件存在（跨内容目录 + assets/）
  abstract     content_scope: abstract-only 的笔记清单 + 是否被其他笔记引用（引用→补全文，未引用→删除候选）
  dollar       正文字面 $ 后跟数字（Quartz 会当行内公式起始符，需转义甄别）
  placeholder  Papers/ 残留 %% 模板注释 / [TODO] / [待补充]

用法:
    python3 vault_lint.py               # 全部检查
    python3 vault_lint.py --build       # 额外跑 npx quartz build 冒烟
    python3 vault_lint.py --check cite-key wikilink   # 只跑指定检查

退出码: 0 = 无 ERROR（WARN 允许）; 1 = 有 ERROR。
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: 需要 pyyaml (pip3 install pyyaml)")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[3]
CONTENT_DIRS = ["Papers", "Topics", "Ideas", "Reports", "News", "DomainMaps", "Projects",
                "Experiments", "Meetings"]
# 上站目录（website/quartz.config.ts ignorePatterns 之外的部分）——dollar 检查只对这些跑
PUBLISHED_DIRS = ["Papers", "Topics", "Ideas", "Reports", "News", "DomainMaps", "Projects"]
ASSET_DIRS = ["assets"]

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
WIKILINK_RE = re.compile(r"!?\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
DOLLAR_RE = re.compile(r"(?<!\\)\$\d")

ERRORS: list[str] = []
WARNS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNS.append(msg)


def content_files() -> list[Path]:
    files = []
    for d in CONTENT_DIRS:
        p = ROOT / d
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
    return files


def split_frontmatter(text: str):
    """返回 (fm_dict 或 None, 解析错误或 None, body)。"""
    if not text.startswith("---"):
        return None, None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "frontmatter 未闭合（缺第二个 ---）", text
    try:
        return yaml.safe_load(parts[1]), None, parts[2]
    except yaml.YAMLError as e:
        return None, str(e).split("\n")[0], parts[2]


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def check_yaml(files):
    for f in files:
        fm, e, _ = split_frontmatter(f.read_text(encoding="utf-8"))
        if e:
            err(f"[yaml] {rel(f)}: {e}")
            continue
        if fm is None:
            continue
        for field in ("authors", "institute"):
            if field in fm and isinstance(fm[field], str):
                err(f"[yaml] {rel(f)}: {field} 应为 list，实际是 string")
        for field in ("title", "venue"):
            if field in fm and isinstance(fm[field], dict):
                err(f"[yaml] {rel(f)}: {field} 含未加引号的冒号，被解析成嵌套 map")


def check_cite_key(files):
    for f in files:
        if f.parent.name != "Papers":
            continue
        fm, e, _ = split_frontmatter(f.read_text(encoding="utf-8"))
        if e or not isinstance(fm, dict):
            continue
        ck = fm.get("cite_key")
        if ck is None or (isinstance(ck, str) and not ck.strip()):
            raw = f.read_text(encoding="utf-8")
            trap = ' ""' in raw.split("---", 2)[1] and 'cite_key: ""' in raw
            hint = "（'\"\"' 引号陷阱：assign_cite_keys 会静默跳过，先删引号）" if trap else ""
            err(f"[cite-key] {rel(f)}: cite_key 缺失或为空{hint}——跑 "
                f"python3 skills/4-writing/latex-citation-enhancer/assign_cite_keys.py {rel(f)}")


def build_target_index():
    """所有可被 wikilink 引用的目标：内容 md 的 stem 与相对路径、内容目录与 assets/ 下任意非 md 文件。"""
    targets = set()
    for f in content_files():
        targets.add(f.stem.lower())
        targets.add(str(f.relative_to(ROOT)).removesuffix(".md").lower())
    for d in ASSET_DIRS + CONTENT_DIRS:
        p = ROOT / d
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix != ".md":
                    targets.add(f.name.lower())
                    targets.add(f.stem.lower())
                    targets.add(str(f.relative_to(ROOT)).lower())
    # Workbench 是合法链接目标（如 [[Workbench/memory/patterns.md]]），但不作为被 lint 的内容
    wb = ROOT / "Workbench"
    if wb.is_dir():
        for f in wb.rglob("*"):
            if f.is_file() and ".git" not in f.parts:
                targets.add(str(f.relative_to(ROOT)).lower())
                targets.add(str(f.relative_to(ROOT)).removesuffix(".md").lower())
    return targets


def extract_links(body: str):
    """抽取 wikilink 目标；过滤明显非链接（数学记号、省略号、Mermaid 转义尾巴）。"""
    out = []
    for m in WIKILINK_RE.finditer(FENCE_RE.sub("", body)):
        t = m.group(1).strip().rstrip("\\").strip()
        if not t or ", " in t or t == "..." or t.startswith("..."):
            continue
        out.append(t)
    return out


def check_wikilink(files):
    targets = build_target_index()
    for f in files:
        _, _, body = split_frontmatter(f.read_text(encoding="utf-8"))
        for link in extract_links(body):
            key = link.lower().removesuffix(".md")
            if key in targets or key.split("/")[-1] in targets:
                continue
            warn(f"[wikilink] {rel(f)}: [[{link}]] 未解析到任何文件")


def check_abstract_only(files):
    abstract_notes = []
    for f in files:
        if f.parent.name != "Papers":
            continue
        fm, e, _ = split_frontmatter(f.read_text(encoding="utf-8"))
        if not e and isinstance(fm, dict) and fm.get("content_scope") == "abstract-only":
            abstract_notes.append(f)
    if not abstract_notes:
        return
    # 建立入链表：谁引用了这些笔记
    inbound: dict[str, list[str]] = {f.stem.lower(): [] for f in abstract_notes}
    for f in files:
        _, _, body = split_frontmatter(f.read_text(encoding="utf-8"))
        for link in extract_links(body):
            key = link.lower().removesuffix(".md").split("/")[-1]
            if key in inbound and f.stem.lower() != key:
                inbound[key].append(rel(f))
    for f in abstract_notes:
        refs = inbound[f.stem.lower()]
        if refs:
            warn(f"[abstract] {rel(f)}: abstract-only 且被 {len(refs)} 处引用（{', '.join(refs[:3])}"
                 f"{'…' if len(refs) > 3 else ''}）→ 应重抓全文 re-digest")
        else:
            warn(f"[abstract] {rel(f)}: abstract-only 且无入链 → 删除候选（列清单给 Supervisor 确认）")


def check_dollar(files):
    for f in files:
        if f.parts[len(ROOT.parts)] not in PUBLISHED_DIRS:
            continue
        _, _, body = split_frontmatter(f.read_text(encoding="utf-8"))
        body = FENCE_RE.sub("", body)
        for i, line in enumerate(body.splitlines(), 1):
            if DOLLAR_RE.search(line) and line.count("$") % 2 == 1:
                warn(f"[dollar] {rel(f)}:{i}: 未转义的 $+数字 且行内 $ 为奇数个"
                     f"（Quartz 会当行内公式）: {line.strip()[:80]}")


def check_placeholder(files):
    for f in files:
        if f.parent.name != "Papers":
            continue
        _, _, body = split_frontmatter(f.read_text(encoding="utf-8"))
        body = FENCE_RE.sub("", body)
        if "%%" in body:
            warn(f"[placeholder] {rel(f)}: 残留 %% 模板注释")
        for token in ("[TODO]", "[待补充]", "[TBD]"):
            if token in body:
                warn(f"[placeholder] {rel(f)}: 残留 {token}")


def check_build():
    site = ROOT / "website"
    if not site.is_dir():
        warn("[build] website/ 不存在，跳过")
        return
    r = subprocess.run(["npx", "quartz", "build"], cwd=site,
                       capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        tail = "\n".join((r.stderr or r.stdout).splitlines()[-15:])
        err(f"[build] npx quartz build 失败:\n{tail}")


CHECKS = {
    "yaml": check_yaml,
    "cite-key": check_cite_key,
    "wikilink": check_wikilink,
    "abstract": check_abstract_only,
    "dollar": check_dollar,
    "placeholder": check_placeholder,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", nargs="*", choices=list(CHECKS), default=list(CHECKS))
    ap.add_argument("--build", action="store_true", help="额外跑 npx quartz build 冒烟")
    args = ap.parse_args()

    files = content_files()
    for name in args.check:
        CHECKS[name](files)
    if args.build:
        check_build()

    for m in ERRORS:
        print(f"ERROR {m}")
    for m in WARNS:
        print(f"WARN  {m}")
    print(f"\n{len(files)} files scanned | {len(ERRORS)} error(s), {len(WARNS)} warning(s)")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
