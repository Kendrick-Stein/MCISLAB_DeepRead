#!/usr/bin/env python3
"""digest→survey 记账：论文笔记按 keywords 匹配 survey，写入 Workbench/survey-updates.json。

用法:
    python3 scripts/survey_updates.py record <paper-note.md>
    python3 scripts/survey_updates.py pending [--survey NAME]
    python3 scripts/survey_updates.py clear --survey NAME --papers a.md b.md
"""
import argparse
import datetime
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _frontmatter(path: Path) -> dict:
    """轻量 frontmatter 解析：只取 title/tags/keywords（避免 yaml 依赖差异）。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm, out = m.group(1), {}
    lines = fm.split("\n")
    for key in ("title", "tags", "keywords"):
        km = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.MULTILINE)
        if not km:
            continue
        val = km.group(1).strip()
        if val.startswith("["):
            out[key] = [v.strip().strip("'\"") for v in val.strip("[]").split(",") if v.strip()]
        elif val:
            out[key] = val.strip("'\"")
        else:
            # 多行 YAML list：收集紧随其后的缩进 "- item" 行，遇非缩进行停止
            items = []
            idx = next(i for i, ln in enumerate(lines) if re.match(rf"^{key}:[ \t]*$", ln))
            for ln in lines[idx + 1:]:
                im = re.match(r"^\s+-\s*(.+)$", ln)
                if not im:
                    break
                items.append(im.group(1).strip().strip("'\""))
            out[key] = items
    return out


def _norm(s: str) -> str:
    """匹配归一化：小写 + 连字符视为空格（vault tag 用连字符、标题/keyword 用空格）。"""
    return s.lower().replace("-", " ")


def _json_path(root: Path) -> Path:
    return root / "Workbench" / "survey-updates.json"


def _load(root: Path) -> dict:
    p = _json_path(root)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("pending"), list):
                raise ValueError("wrong shape")
            return data
        except (json.JSONDecodeError, ValueError):
            # 损坏/结构错误：备份后重建，不静默丢弃（spec §9）
            bak = p.with_suffix(p.suffix + ".bak")
            os.replace(p, bak)
            print(f"[survey_updates] warning: corrupt ledger backed up to {bak}", file=sys.stderr)
    return {"version": 1, "pending": []}


def _save(root: Path, data: dict) -> None:
    p = _json_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=p.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        os.replace(tmp, p)  # 原子替换
    except BaseException:
        os.unlink(tmp)
        raise


def load_pending(root: Path = ROOT) -> list:
    return _load(root)["pending"]


def match_surveys(paper: Path, root: Path = ROOT) -> list:
    fm = _frontmatter(paper)
    tags = [str(t) for t in fm.get("tags", [])]
    title = str(fm.get("title", ""))
    # tags 用 ", " 连接：_norm 后逗号保留，阻止多词 keyword 跨 tag 边界拼接命中
    haystack = _norm(", ".join(tags) + ", " + title)
    matched = []
    for survey in sorted(root.glob("Topics/*-Survey.md")):
        kws = [str(k) for k in _frontmatter(survey).get("keywords", [])]
        # 词边界 + 可选复数 s（"vlm" 命中 "vlms"，但 "cua" 不命中 "evacuation"）
        if any(re.search(rf"\b{re.escape(_norm(kw))}s?\b", haystack) for kw in kws if kw):
            matched.append(survey.stem)
    return matched


def record(paper: Path, root: Path = ROOT) -> list:
    data = _load(root)
    rel = str(paper.resolve().relative_to(root.resolve()))
    today = datetime.date.today().isoformat()
    matched = match_surveys(paper, root)
    existing = {(e["survey"], e["paper"]) for e in data["pending"]}
    for s in matched:
        if (s, rel) not in existing:
            data["pending"].append({"survey": s, "paper": rel, "added_at": today})
    _save(root, data)
    return matched


def clear(survey: str, papers: list, root: Path = ROOT) -> None:
    data = _load(root)
    drop = {(survey, p) for p in papers}
    data["pending"] = [e for e in data["pending"] if (e["survey"], e["paper"]) not in drop]
    _save(root, data)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_rec = sub.add_parser("record"); p_rec.add_argument("paper")
    p_pen = sub.add_parser("pending"); p_pen.add_argument("--survey")
    p_clr = sub.add_parser("clear"); p_clr.add_argument("--survey", required=True); p_clr.add_argument("--papers", required=True, nargs="+")
    args = ap.parse_args()
    if args.cmd == "record":
        matched = record(Path(args.paper))
        print(json.dumps(matched, ensure_ascii=False))
    elif args.cmd == "pending":
        rows = load_pending()
        if args.survey:
            rows = [r for r in rows if r["survey"] == args.survey]
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        clear(args.survey, args.papers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
