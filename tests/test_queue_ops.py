import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "1-literature" / "daily-papers" / "queue_ops.py"


def load_module():
    spec = importlib.util.spec_from_file_location("queue_ops_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def configure_tmp_queue(module, tmp_path):
    module.VAULT_ROOT = tmp_path
    module.QUEUE_PATH = tmp_path / "Workbench" / "queue.json"
    module.ARCHIVE_PATH = tmp_path / "Workbench" / "queue-archive.jsonl"
    module.LOCK_PATH = tmp_path / "Workbench" / ".queue.lock"
    module.QUEUE_PATH.parent.mkdir(parents=True)
    (tmp_path / "Papers").mkdir()
    module.save_queue(module.load_queue())


def paper_task(module, title, url, score=0):
    return module.make_task({
        "title": title, "url": url, "date": "2026-07-23",
        "score": score, "source": "arxiv", "abstract": "", "authors": "A. Author",
    })


def read_archive(module):
    if not module.ARCHIVE_PATH.exists():
        return []
    return [json.loads(l) for l in module.ARCHIVE_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_enqueue_review_is_deduplicated(tmp_path):
    module = load_module()
    configure_tmp_queue(module, tmp_path)
    args = SimpleNamespace(
        insight_ref="Workbench/memory/insights.md#claim-a",
        claim="Claim A",
        suggested_map="DomainMaps/GUI-Agent.md",
        title=None,
        priority=90,
        source="memory-distill",
    )

    module.cmd_enqueue_review(args)
    module.cmd_enqueue_review(args)

    queue = json.loads(module.QUEUE_PATH.read_text(encoding="utf-8"))["queue"]
    assert len(queue) == 1
    assert queue[0]["task"]["task_type"] == "review_insight"
    assert queue[0]["task"]["status"] == "pending"
    assert queue[0]["task"]["metadata"]["verification"] == "human-required"


def test_complete_marks_committed_task_done(tmp_path):
    module = load_module()
    configure_tmp_queue(module, tmp_path)
    task = module.make_task({
        "title": "Example Paper",
        "url": "https://arxiv.org/abs/2607.12345",
        "date": "2026-07-23",
        "score": 4,
        "source": "arxiv",
        "abstract": "",
        "authors": "A. Author",
    })
    queue = module.load_queue()
    queue["queue"].append(task)
    module.save_queue(queue)

    module.cmd_complete(SimpleNamespace(
        task_id=task["task"]["task_id"],
        paper_url=None,
        output_path="Papers/2607-Example.md",
    ))

    completed = module.load_queue()["queue"][0]
    assert completed["task"]["status"] == "done"
    assert completed["task"]["output_path"] == "Papers/2607-Example.md"
    assert completed["last_attempt"]


def test_capacity_pruning_preserves_human_review(tmp_path):
    module = load_module()
    configure_tmp_queue(module, tmp_path)
    review_args = SimpleNamespace(
        insight_ref="Workbench/memory/insights.md#claim-a",
        claim="Claim A",
        suggested_map="DomainMaps/GUI-Agent.md",
        title=None,
        priority=90,
        source="memory-distill",
    )
    queue = module.load_queue()
    queue["settings"]["max_queue_size"] = 1
    queue["queue"].append(module.make_review_task(review_args))
    queue["queue"].append(module.make_task({
        "title": "Low Priority Paper",
        "url": "https://arxiv.org/abs/2607.00001",
        "date": "2026-07-23",
        "score": 0,
        "source": "arxiv",
    }))

    _, dropped, _ = module.prune_and_cap(queue)

    assert len(dropped) == 1
    assert [item["task"]["task_type"] for item in queue["queue"]] == ["review_insight"]


def test_done_tasks_are_archived_and_do_not_consume_capacity(tmp_path):
    """done 不该和待办抢配额：cap=2 且已有 3 条 done 时，两条 pending 必须全部存活。"""
    module = load_module()
    configure_tmp_queue(module, tmp_path)
    queue = module.load_queue()
    queue["settings"]["max_queue_size"] = 2
    for i in range(3):
        finished = paper_task(module, f"Done Paper {i}", f"https://arxiv.org/abs/2607.1000{i}")
        finished["task"]["status"] = "done"
        queue["queue"].append(finished)
    queue["queue"].append(paper_task(module, "Pending A", "https://arxiv.org/abs/2607.20001"))
    queue["queue"].append(paper_task(module, "Pending B", "https://arxiv.org/abs/2607.20002"))

    _, dropped, archived = module.prune_and_cap(queue)

    assert archived == 3
    assert dropped == []
    assert [item["task"]["title"] for item in queue["queue"]] == \
        ["Summarize: Pending A", "Summarize: Pending B"]
    assert {r["task"]["title"] for r in read_archive(module)} == \
        {f"Summarize: Done Paper {i}" for i in range(3)}


def test_capacity_dropped_tasks_are_recorded_and_requeueable(tmp_path):
    """被 cap 挤掉的是尚未消化的工作：必须留痕，且不得被当成 done 永久拦住重新入队。"""
    module = load_module()
    configure_tmp_queue(module, tmp_path)
    queue = module.load_queue()
    queue["settings"]["max_queue_size"] = 1
    queue["queue"].append(paper_task(module, "Keep Me", "https://arxiv.org/abs/2607.30001", score=40))
    queue["queue"].append(paper_task(module, "Evict Me", "https://arxiv.org/abs/2607.30002", score=0))

    _, dropped, _ = module.prune_and_cap(queue)

    assert [d["task"]["title"] for d in dropped] == ["Summarize: Evict Me"]
    assert [item["task"]["title"] for item in queue["queue"]] == ["Summarize: Keep Me"]
    record = [r for r in read_archive(module) if r["task"]["title"] == "Summarize: Evict Me"]
    assert record and record[0]["dropped_reason"] == "max_queue_size"
    # 关键：淘汰记录不能污染去重集合，否则这篇论文再也无法重新入队
    assert "2607.30002" not in module.archived_ids()


def test_archived_done_still_blocks_reenqueue(tmp_path):
    """归档后仍要保住去重语义：已完成的论文不能因为移出队列而被重复入队。"""
    module = load_module()
    configure_tmp_queue(module, tmp_path)
    queue = module.load_queue()
    finished = paper_task(module, "Already Done", "https://arxiv.org/abs/2607.40001")
    finished["task"]["status"] = "done"
    queue["queue"].append(finished)
    module.prune_and_cap(queue)
    module.save_queue(queue)

    assert "2607.40001" in module.archived_ids()

    candidates = tmp_path / "cands.json"
    candidates.write_text(json.dumps([{
        "title": "Already Done", "url": "https://arxiv.org/abs/2607.40001",
        "date": "2026-07-23", "score": 9, "source": "arxiv", "abstract": "", "authors": "A",
    }]), encoding="utf-8")
    module.cmd_enqueue(SimpleNamespace(candidates=str(candidates), ids=["2607.40001"]))

    assert module.load_queue()["queue"] == []



def test_complete_on_archived_task_is_not_a_failure(tmp_path):
    """done 归档后再调 complete 不能硬失败——否则 coordinator 重试会被中断。"""
    module = load_module()
    configure_tmp_queue(module, tmp_path)
    queue = module.load_queue()
    finished = paper_task(module, "Archived Paper", "https://arxiv.org/abs/2607.50001")
    finished["task"]["status"] = "done"
    queue["queue"].append(finished)
    module.prune_and_cap(queue)
    module.save_queue(queue)

    module.cmd_complete(SimpleNamespace(
        task_id=finished["task"]["task_id"], paper_url=None, output_path=None))

    with pytest.raises(SystemExit):
        module.cmd_complete(SimpleNamespace(
            task_id="deadbeef", paper_url=None, output_path=None))
