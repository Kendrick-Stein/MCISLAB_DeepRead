import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


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
    module.LOCK_PATH = tmp_path / "Workbench" / ".queue.lock"
    module.QUEUE_PATH.parent.mkdir(parents=True)
    (tmp_path / "Papers").mkdir()
    module.save_queue(module.load_queue())


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

    _, dropped = module.prune_and_cap(queue)

    assert dropped == 1
    assert [item["task"]["task_type"] for item in queue["queue"]] == ["review_insight"]

