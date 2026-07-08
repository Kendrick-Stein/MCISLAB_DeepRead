#!/usr/bin/env python3
"""按 team-config news.wechat 用搜狗微信搜索抓公众号文章，按中文关键词打分 + 账号白名单过滤，输出候选 JSON。

用法: python3 scripts/wechat_search/fetch_wechat.py [--days 3] [--output Workbench/daily/.wechat-candidates.json]

依赖: Node.js + 本目录 node_modules（首次需 `cd scripts/wechat_search && npm install`）。
底层调用 ./search_wechat.js（爬搜狗微信搜索 weixin.sogou.com，无需 API key）。

设计要点（见 CLAUDE.md 研究原则 3：evidence-driven）：
- 搜狗只支持"按关键词搜全网公众号"，无"列某账号最新文章"模式 → 账号当白名单，关键词驱动查询。
- 裸关键词搜出大量大众媒体旧文（21世纪经济报道/新华网…）→ 必须叠加账号白名单 + 时间窗口过滤。
- 反爬会偶发返回空/限流 → 单关键词失败跳过不阻塞，记入 errors；查询间加延迟。
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEAM_CONFIG = ROOT / "Workbench" / "config" / "team-config.json"
NODE_SCRIPT = Path(__file__).resolve().parent / "search_wechat.js"
NODE_MODULES = Path(__file__).resolve().parent / "node_modules"
CHINA_TZ = timezone(timedelta(hours=8))  # 搜狗返回的 datetime 为中国时间


def _norm(s: str) -> str:
    """匹配归一化：小写 + 连字符视为空格（与 fetch_news.py / survey_updates.py 一致）。"""
    return s.lower().replace("-", " ")


def score_item(item: dict, keywords: list[str]) -> int:
    hay = _norm(item.get("title", "") + " " + item.get("summary", ""))
    return sum(1 for kw in keywords if _norm(kw) in hay)


def _parse_dt(s: str):
    """解析 '2024-01-15 10:30:00'（中国时间）→ aware datetime；失败返回 None。"""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=CHINA_TZ)
    except (ValueError, TypeError):
        return None


def run_search(query: str, num: int, timeout: int = 60) -> list[dict]:
    """调用 node 脚本搜一个关键词，返回 articles 列表；抛异常交由上层记 errors。"""
    proc = subprocess.run(
        ["node", str(NODE_SCRIPT), query, "-n", str(num)],
        capture_output=True, text=True, timeout=timeout, cwd=str(NODE_SCRIPT.parent),
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[-300:] or f"exit {proc.returncode}")
    data = json.loads(proc.stdout)  # 脚本把进度打到 stderr，JSON 在 stdout
    return data.get("articles", [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--output", default="Workbench/daily/.wechat-candidates.json")
    args = ap.parse_args()

    cfg = json.loads(TEAM_CONFIG.read_text(encoding="utf-8"))
    wx = cfg.get("news", {}).get("wechat", {})
    if not wx.get("enabled", False):
        print("wechat source disabled in team-config", file=sys.stderr)
        _write(ROOT / args.output, {"enabled": False, "candidates": [], "errors": []})
        return 0

    days = args.days or cfg.get("news", {}).get("days", 3)
    keywords = wx.get("keywords", [])
    accounts = set(wx.get("accounts", []))
    per_kw = wx.get("per_keyword", 10)
    max_queries = wx.get("max_queries", 12)
    whitelist_only = wx.get("whitelist_only", True) and bool(accounts)
    delay = wx.get("query_delay_sec", 1.5)
    cutoff = datetime.now(CHINA_TZ) - timedelta(days=days)

    # 前置环境检查：给出可执行的报错，而非在每个关键词上失败
    if not NODE_MODULES.exists():
        _write(ROOT / args.output, {"enabled": True, "candidates": [], "errors": [
            {"query": "*", "error": "node_modules 缺失，先执行: cd scripts/wechat_search && npm install"}]})
        print("ERROR: node_modules missing (run npm install)", file=sys.stderr)
        return 1

    seen, candidates, errors = set(), [], []
    for i, kw in enumerate(keywords[:max_queries]):
        try:
            arts = run_search(kw, per_kw)
        except Exception as e:  # 单关键词失败跳过，不阻塞
            errors.append({"query": kw, "error": str(e)})
            continue
        for a in arts:
            key = (a.get("title", ""), a.get("source", ""))
            if not key[0] or key in seen:
                continue
            seen.add(key)
            source = a.get("source", "")
            watched = source in accounts
            if whitelist_only and not watched:
                continue
            pub = _parse_dt(a.get("datetime", ""))
            if pub and pub < cutoff:  # 有日期且过期 → 丢；无日期保留（可能是最新但缺时间戳）
                continue
            candidates.append({
                "title": a.get("title", ""),
                "link": a.get("url", ""),
                "summary": a.get("summary", ""),
                "source": source,
                "published": pub.isoformat() if pub else None,
                "date_description": a.get("date_description", ""),
                "score": score_item(a, keywords) + (10 if watched else 0),
                "watched": watched,
                "matched_query": kw,
            })
        if i < len(keywords[:max_queries]) - 1:
            time.sleep(delay)  # 反爬礼貌延迟

    candidates.sort(key=lambda c: (c["watched"], c["score"], c["published"] or ""), reverse=True)
    out = {
        "enabled": True,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "queries": keywords[:max_queries],
        "accounts": sorted(accounts),
        "whitelist_only": whitelist_only,
        "candidates": candidates,
        "errors": errors,
    }
    _write(ROOT / args.output, out)
    print(f"{len(candidates)} wechat candidates "
          f"({sum(c['watched'] for c in candidates)} from watched accounts), "
          f"{len(errors)} query errors", file=sys.stderr)
    return 0


def _write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
