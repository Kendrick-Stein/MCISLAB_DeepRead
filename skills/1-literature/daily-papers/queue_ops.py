#!/usr/bin/env python3
"""queue_ops.py — 维护 Workbench/queue.json，作为研究任务的持久 backlog。

把 daily-papers（生产者）重新接到 autoresearch（消费者）：daily-papers 把必读
论文入队为 pending summarize_paper 任务；coordinator 在笔记安全落地后用 `complete`
标记 done，`enqueue` / `prune` 仍会清理历史遗留的“笔记已存在但任务仍 pending”状态。
剩余 pending 由 autoresearch 的 paper-digest 消费。

queue.json 只持有**活动 backlog**（pending）。done 任务在每次 enqueue / prune 时移入
append-only 的 `Workbench/queue-archive.jsonl`：所有消费者都只读 pending，而 done 留在
队列里会占掉 max_queue_size 的配额，把尚未消化的论文挤掉。容量淘汰同样写入归档并在
stdout 列出标题——被挤掉的是还没做的工作，不能静默消失。

零 token，纯 Python，无外部依赖。

Usage:
    # 入队必读论文（按 arXiv id，从 candidates.json 取元数据）
    python3 queue_ops.py enqueue --candidates Workbench/daily/.candidates.json \
        --ids 2604.12345 2605.67890

    # 仅做自清理（剪除已有笔记的 pending 任务）+ 容量裁剪
    python3 queue_ops.py prune

    # 把 validated insight 的 DomainMap 晋升交给 Human review
    python3 queue_ops.py enqueue-review --insight-ref "Workbench/memory/insights.md#..." \
        --claim "..." --suggested-map DomainMaps/GUI-Agent.md

    # coordinator 在 artifact 已安全落库后完成任务
    python3 queue_ops.py complete --task-id 0123abcd --output-path Papers/2607-Example.md
"""

import argparse
from contextlib import contextmanager
import fcntl
import glob
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[3]
QUEUE_PATH = VAULT_ROOT / "Workbench" / "queue.json"
ARCHIVE_PATH = VAULT_ROOT / "Workbench" / "queue-archive.jsonl"
LOCK_PATH = VAULT_ROOT / "Workbench" / ".queue.lock"
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


@contextmanager
def queue_lock():
    """Serialize CLI mutations; orchestrators still own the higher-level commit order."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def save_queue(q: dict) -> None:
    q["updated_at"] = now_iso()
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = QUEUE_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(QUEUE_PATH)


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


def make_review_task(args) -> dict:
    title = args.title or args.claim[:80]
    return {
        "task": {
            "task_id": uuid.uuid4().hex[:8],
            "task_type": "review_insight",
            "title": f"Review insight promotion: {title}",
            "goal": "Human review before promoting a validated insight to a DomainMap",
            "topic": args.suggested_map,
            "input_refs": [args.insight_ref],
            "output_path": args.suggested_map,
            "priority": args.priority,
            "status": "pending",
            "dependencies": [],
            "metadata": {
                "claim": args.claim,
                "suggested_map": args.suggested_map,
                "verification": "human-required",
            },
        },
        "added_at": now_iso(),
        "source": args.source,
        "attempts": 0,
        "last_attempt": None,
    }


def archived_ids() -> set:
    """归档中已完成任务的 arXiv id，用于 enqueue 去重（等价于旧结构里留在队列的 done）。"""
    if not ARCHIVE_PATH.exists():
        return set()
    ids = set()
    for line in ARCHIVE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        # 只有真正完成的任务才算去重依据；被容量淘汰的记录必须保持可重新入队
        if item.get("dropped_reason") or item.get("task", {}).get("status") != "done":
            continue
        aid = arxiv_id(item.get("task", {}).get("metadata", {}).get("paper_url", ""))
        if aid:
            ids.add(aid)
    return ids


def archive_done(q: dict) -> int:
    """把 done 任务移出活动队列，追加写入 append-only 归档。

    所有消费者（autoresearch / agenda-evolve / research-team）都只读 pending，done 留在
    队列里没有消费价值，却会占掉 max_queue_size 的配额，把尚未消化的 pending 挤掉。
    归档用 jsonl 而非 json，是为了让每日提交只产生追加行，不再整文件重排。
    """
    done = [t for t in q["queue"] if t["task"]["status"] == "done"]
    if not done:
        return 0
    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARCHIVE_PATH.open("a", encoding="utf-8") as fh:
        for item in done:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    q["queue"] = [t for t in q["queue"] if t["task"]["status"] != "done"]
    return len(done)


def prune_and_cap(q: dict) -> tuple[int, list, int]:
    """剪除已有笔记的 pending digest、归档 done，再按容量裁剪 paper backlog。

    容量只丈量 pending：已完成的工作不该和待办抢配额。淘汰对象也只有 pending 的
    summarize_paper——review_insight 是 Human gate，任何情况下都不淘汰。
    """
    notes = existing_note_ids()
    before = len(q["queue"])
    q["queue"] = [
        t for t in q["queue"]
        if not (t["task"]["status"] == "pending" and arxiv_id(t["task"]["metadata"].get("paper_url", "")) in notes)
    ]
    pruned = before - len(q["queue"])

    archived = archive_done(q)

    cap = q.get("settings", {}).get("max_queue_size", 100)
    pending = [t for t in q["queue"] if t["task"]["status"] == "pending"]
    dropped = []
    if len(pending) > cap:
        paper_pending = [t for t in pending if t["task"]["task_type"] == "summarize_paper"]
        protected = sum(1 for t in pending if t["task"]["task_type"] != "summarize_paper")
        paper_pending.sort(key=lambda t: t["task"]["priority"], reverse=True)
        room = max(0, cap - protected)
        dropped = paper_pending[room:]
        evicted = {id(t) for t in dropped}
        # 按 id 剔除而非重建列表，保留原有顺序，避免整文件 diff churn
        q["queue"] = [t for t in q["queue"] if id(t) not in evicted]
        # 淘汰必须留痕：被挤掉的是尚未消化的论文，静默丢弃过去已造成实际损失
        record_dropped(dropped)
    return pruned, dropped, archived


def record_dropped(items: list) -> None:
    """把被容量淘汰的 pending 任务写进归档，标记原因，使其可追溯、可重新入队。"""
    if not items:
        return
    ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARCHIVE_PATH.open("a", encoding="utf-8") as fh:
        for item in items:
            record = dict(item)
            record["dropped_at"] = now_iso()
            record["dropped_reason"] = "max_queue_size"
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def cmd_enqueue(args):
    with queue_lock():
        q = load_queue()
        cands = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        by_id = {arxiv_id(c.get("url", "")): c for c in cands if arxiv_id(c.get("url", ""))}

        want = args.ids if args.ids else list(by_id.keys())
        have = existing_note_ids() | queued_ids(q) | archived_ids()
        added = 0
        for cid in want:
            cid = arxiv_id(cid) or cid
            if cid in have or cid not in by_id:
                continue
            q["queue"].append(make_task(by_id[cid]))
            have.add(cid)
            added += 1

        pruned, dropped, archived = prune_and_cap(q)
        save_queue(q)
    pending = sum(1 for t in q["queue"] if t["task"]["status"] == "pending")
    print(f"enqueue: +{added} added, -{pruned} pruned (note exists), "
          f"-{len(dropped)} dropped (cap), {archived} archived (done); {pending} pending now")
    report_dropped(dropped)


def report_dropped(dropped: list) -> None:
    """容量淘汰必须在 stdout 可见，否则调用方无从得知 backlog 被削掉了什么。"""
    for item in dropped:
        task = item["task"]
        print(f"  DROPPED p{task['priority']} {task['title']}  <{task['metadata'].get('paper_url', '')}>")
    if dropped:
        print(f"  ^ {len(dropped)} 条未消化任务被 cap 挤出，已记入 {ARCHIVE_PATH.name}，可重新入队")


def cmd_prune(args):
    with queue_lock():
        q = load_queue()
        pruned, dropped, archived = prune_and_cap(q)
        save_queue(q)
    pending = sum(1 for t in q["queue"] if t["task"]["status"] == "pending")
    print(f"prune: -{pruned} pruned (note exists), -{len(dropped)} dropped (cap), "
          f"{archived} archived (done); {pending} pending now")
    report_dropped(dropped)


def cmd_enqueue_review(args):
    with queue_lock():
        q = load_queue()
        duplicate = any(
            item["task"].get("task_type") == "review_insight"
            and args.insight_ref in item["task"].get("input_refs", [])
            and item["task"].get("status") == "pending"
            for item in q["queue"]
        )
        if duplicate:
            print("enqueue-review: duplicate pending review; no change")
            return
        task = make_review_task(args)
        q["queue"].append(task)
        save_queue(q)
    print(f"enqueue-review: +1 added ({task['task']['task_id']})")


def cmd_complete(args):
    with queue_lock():
        q = load_queue()
        matched = []
        for item in q["queue"]:
            task = item["task"]
            url_match = args.paper_url and task.get("metadata", {}).get("paper_url") == args.paper_url
            if task.get("task_id") == args.task_id or url_match:
                task["status"] = "done"
                task["output_path"] = args.output_path or task.get("output_path")
                item["last_attempt"] = now_iso()
                matched.append(task["task_id"])
        if not matched:
            # 任务可能已被归档（done 不再留在活动队列）——这不是失败，不应中断 coordinator
            if already_archived(args):
                print("complete: task already done (archived); no change")
                return
            raise SystemExit("complete: no matching task")
        save_queue(q)
    print(f"complete: {', '.join(matched)} -> done")


def already_archived(args) -> bool:
    if not ARCHIVE_PATH.exists():
        return False
    for line in ARCHIVE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            task = json.loads(line).get("task", {})
        except json.JSONDecodeError:
            continue
        if task.get("status") != "done":
            continue
        if task.get("task_id") == args.task_id or (
            args.paper_url and task.get("metadata", {}).get("paper_url") == args.paper_url
        ):
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Manage queue.json research tasks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enqueue", help="append pending tasks for must-read papers")
    e.add_argument("--candidates", required=True, help="path to .candidates.json")
    e.add_argument("--ids", nargs="*", default=None, help="arXiv ids of must-reads (default: all candidates)")
    e.set_defaults(func=cmd_enqueue)
    p = sub.add_parser("prune", help="self-clean: drop pending tasks whose note exists; enforce cap")
    p.set_defaults(func=cmd_prune)
    r = sub.add_parser("enqueue-review", help="append a pending Human review task for an insight")
    r.add_argument("--insight-ref", required=True)
    r.add_argument("--claim", required=True)
    r.add_argument("--suggested-map", required=True)
    r.add_argument("--title")
    r.add_argument("--priority", type=int, default=90)
    r.add_argument("--source", default="memory-distill")
    r.set_defaults(func=cmd_enqueue_review)
    c = sub.add_parser("complete", help="mark a queue task done after its artifact is committed")
    target = c.add_mutually_exclusive_group(required=True)
    target.add_argument("--task-id")
    target.add_argument("--paper-url")
    c.add_argument("--output-path")
    c.set_defaults(func=cmd_complete)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
