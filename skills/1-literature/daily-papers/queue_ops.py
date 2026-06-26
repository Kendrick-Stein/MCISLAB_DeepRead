#!/usr/bin/env python3
"""queue_ops.py — 维护 Workbench/queue.json，作为论文 digest 的持久 backlog。

把 daily-papers（生产者）重新接到 autoresearch（消费者）：daily-papers 把必读
论文入队为 pending summarize_paper 任务；inline digest 完成（笔记落地）后，下一次
enqueue 会自动把已有笔记的任务剪除；剩余 pending 由 autoresearch 的 paper-digest 消费。

零 token，纯 Python，无外部依赖。

Usage:
    # 入队必读论文（按 arXiv id，从 candidates.json 取元数据）
    python3 queue_ops.py enqueue --candidates Workbench/daily/.candidates.json \
        --ids 2604.12345 2605.67890

    # 仅做自清理（剪除已有笔记的 pending 任务）+ 容量裁剪
    python3 queue_ops.py prune
"""

import argparse
import glob
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[3]
QUEUE_PATH = VAULT_ROOT / "Workbench" / "queue.json"
ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


def arxiv_id(text: str) -> str:
    m = ARXIV_RE.search(text or "")
    return m.group(1) if m else ""


def load_queue() -> dict:
    if QUEUE_PATH.exists():
        return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    return {"queue": [], "version": "0.1.0", "updated_at": "",
            "settings": {"max_queue_size": 100, "max_attempts": 3, "retry_delay_minutes": 30}}


def save_queue(q: dict) -> None:
    q["updated_at"] = now_iso()
    QUEUE_PATH.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def existing_note_ids() -> set:
    """已有论文笔记的 arXiv id 集合（扫描 Papers/ 与 Papers/Archive/ 的 url）。"""
    ids = set()
    for p in glob.glob(str(VAULT_ROOT / "Papers" / "*.md")) + \
             glob.glob(str(VAULT_ROOT / "Papers" / "Archive" / "*.md")):
        aid = arxiv_id(Path(p).read_text(encoding="utf-8"))
        if aid:
            ids.add(aid)
    return ids


def queued_ids(q: dict) -> set:
    return {arxiv_id(t["task"]["metadata"].get("paper_url", "")) for t in q["queue"]} - {""}


def make_task(cand: dict) -> dict:
    title = cand.get("title", "")
    return {
        "task": {
            "task_id": uuid.uuid4().hex[:8],
            "task_type": "summarize_paper",
            "title": f"Summarize: {title}",
            "goal": f"Generate structured note for paper '{title}'",
            "topic": None,
            "input_refs": [f"{cand.get('date', '')[:4]}-{title}"],
            "output_path": None,
            "priority": min(99, 50 + int(cand.get("score", 0))),
            "status": "pending",
            "dependencies": [],
            "metadata": {
                "paper_url": cand.get("url", ""),
                "paper_id": title,
                "title": title,
                "abstract": cand.get("abstract", ""),
                "source": cand.get("source"),
                "year": (cand.get("date", "") or "")[:4],
                "authors": cand.get("authors", ""),
            },
        },
        "added_at": now_iso(),
        "source": "daily-papers",
        "attempts": 0,
        "last_attempt": None,
    }


def prune_and_cap(q: dict) -> tuple[int, int]:
    """剪除已有笔记的 pending 任务；超出 max_queue_size 时丢弃优先级最低的 pending。"""
    notes = existing_note_ids()
    before = len(q["queue"])
    q["queue"] = [
        t for t in q["queue"]
        if not (t["task"]["status"] == "pending" and arxiv_id(t["task"]["metadata"].get("paper_url", "")) in notes)
    ]
    pruned = before - len(q["queue"])

    cap = q.get("settings", {}).get("max_queue_size", 100)
    dropped = 0
    if len(q["queue"]) > cap:
        pend = [t for t in q["queue"] if t["task"]["status"] == "pending"]
        keep_other = [t for t in q["queue"] if t["task"]["status"] != "pending"]
        pend.sort(key=lambda t: t["task"]["priority"], reverse=True)
        room = max(0, cap - len(keep_other))
        dropped = max(0, len(pend) - room)
        q["queue"] = keep_other + pend[:room]
    return pruned, dropped


def cmd_enqueue(args):
    q = load_queue()
    cands = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    by_id = {arxiv_id(c.get("url", "")): c for c in cands if arxiv_id(c.get("url", ""))}

    want = args.ids if args.ids else list(by_id.keys())
    have = existing_note_ids() | queued_ids(q)
    added = 0
    for cid in want:
        cid = arxiv_id(cid) or cid
        if cid in have or cid not in by_id:
            continue
        q["queue"].append(make_task(by_id[cid]))
        have.add(cid)
        added += 1

    pruned, dropped = prune_and_cap(q)
    save_queue(q)
    pending = sum(1 for t in q["queue"] if t["task"]["status"] == "pending")
    print(f"enqueue: +{added} added, -{pruned} pruned (note exists), -{dropped} dropped (cap); "
          f"{pending} pending now")


def cmd_prune(args):
    q = load_queue()
    pruned, dropped = prune_and_cap(q)
    save_queue(q)
    pending = sum(1 for t in q["queue"] if t["task"]["status"] == "pending")
    print(f"prune: -{pruned} pruned (note exists), -{dropped} dropped (cap); {pending} pending now")


def main():
    ap = argparse.ArgumentParser(description="Manage queue.json paper backlog")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enqueue", help="append pending tasks for must-read papers")
    e.add_argument("--candidates", required=True, help="path to .candidates.json")
    e.add_argument("--ids", nargs="*", default=None, help="arXiv ids of must-reads (default: all candidates)")
    e.set_defaults(func=cmd_enqueue)
    p = sub.add_parser("prune", help="self-clean: drop pending tasks whose note exists; enforce cap")
    p.set_defaults(func=cmd_prune)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
