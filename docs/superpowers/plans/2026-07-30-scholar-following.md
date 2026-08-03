# Following 学者跟踪信道 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 ReadPaperMachine 增加一条 person-pull 论文发现信道——自动从 vault 已有笔记里识别 30-50 位高相关学者，按方向跟踪他们的新作，并为每人生成一页可上站的研究主线档案。

**Architecture:** 新增 skill `skills/1-literature/scholar-track/`，拆成「网络层 `sources.py` / 纯逻辑层 `roster.py` / 状态层 `store.py` / 渲染层 `pages.py`」四个模块加两个 CLI 入口（`build_roster.py` 月度建档、`fetch_followed.py` 日更抓取）。主键用 OpenAlex author ID（通过论文反解作者，规避姓名同名污染），日更走 arXiv + OpenAlex 双路，产出写进 `Following/*.md` 与 daily-papers 候选池。

**Tech Stack:** Python 3.10+ 纯 stdlib（与 `fetch_and_score.py` 一致，零外部依赖、零 token）、pytest 9、Quartz 4（站点）。

**设计依据:** `docs/superpowers/specs/2026-07-30-scholar-following-design.md`

---

## 背景：实现者必须先知道的事

**这是一个 Obsidian vault + Quartz 静态站，不是普通应用。** 论文笔记是 `Papers/YYMM-ShortTitle.md`，带 YAML frontmatter。站点由 GitHub Actions 跑 `npx quartz build --directory ../ --output dist`（见 `.github/workflows/deploy.yml`），**content 根目录是 repo 根**，`website/content/` 是 2026-04 的历史遗留目录，与构建无关，不要动它。

**已有代码里你需要复用的东西**，全在 `skills/1-literature/daily-papers/fetch_and_score.py`：

| 函数 | 作用 |
|:---|:---|
| `fetch_url(url, timeout)` | 带 Lexmount 兜底的 HTTP GET，失败返回空串不抛异常 |
| `paper_key(paper)` | 跨源稳定主键：arxiv id → doi → cvf id → 标题哈希 |
| `reconstruct_abstract(inverted_index)` | 还原 OpenAlex 的 `abstract_inverted_index` |
| `load_history` / `history_key` | `.history.json` 去重记录 |

该目录名含连字符（`daily-papers`），**不是合法 Python 包名**，必须用 `importlib.util.spec_from_file_location` 加载。`tests/test_daily_papers_fetch.py` 里有现成写法，照抄。

**测试约定**（见 `tests/test_daily_papers_fetch.py`）：用 `importlib` 加载被测脚本，用 `monkeypatch.setattr(module, "urlopen", fake)` 拦网络。**任何测试都不得发真实网络请求。**

**Secret 纪律**：`LEXMOUNT_API_KEY` 只从环境变量或 `.env` 读，永不写进日志/笔记/提交文件。

---

## File Structure

**新建：**

| 文件 | 职责 |
|:---|:---|
| `skills/1-literature/scholar-track/SKILL.md` | skill 协议定义（Purpose/Steps/Guard/Verify） |
| `skills/1-literature/scholar-track/config.json` | 所有阈值与权重 |
| `skills/1-literature/scholar-track/store.py` | `Workbench/scholars.json` 原子读写，无业务逻辑 |
| `skills/1-literature/scholar-track/roster.py` | 纯函数：打分、方向判定、入选、休眠。**不发网络请求、不碰文件** |
| `skills/1-literature/scholar-track/sources.py` | 唯一发网络请求的模块：OpenAlex + arXiv |
| `skills/1-literature/scholar-track/pages.py` | `Following/*.md` 渲染，保留人写的 review 章节 |
| `skills/1-literature/scholar-track/build_roster.py` | CLI：建档 / 月度重算 |
| `skills/1-literature/scholar-track/fetch_followed.py` | CLI：日更抓取 |
| `Following/_index.md` | 站点总览页（由 `pages.py` 生成） |
| `Workbench/scholars.json` | 状态文件（由 `store.py` 生成） |
| `tests/test_scholar_store.py` | |
| `tests/test_scholar_roster.py` | |
| `tests/test_scholar_sources.py` | |
| `tests/test_scholar_pages.py` | |
| `tests/test_scholar_cli.py` | 两个 CLI 的端到端（网络全 mock） |

**修改：**

| 文件 | 改动 |
|:---|:---|
| `website/quartz.layout.ts:44,84` | 两处 `order` 数组加 `"Following"` |
| `skills/1-literature/daily-papers/SKILL.md` | Step 1 后插入 followed 抓取步骤 |
| `skills/1-literature/daily-papers/config.json` | `max_per_source` 加 `followed` |
| `skills/6-orchestration/autoresearch/SKILL.md` | 调度加入日更 + review 重写触发 |
| `CLAUDE.md` | 目录结构补 `Following/`，skill 表补 `scholar-track` |
| `.gitignore` | 忽略 `Workbench/daily/.followed-candidates.json` |

**分层铁律：** `roster.py` 不 import `sources.py`、不读写文件。所有网络在 `sources.py`，所有文件 IO 在 `store.py` / `pages.py`。这样 `roster.py` 的全部逻辑可以零 mock 测试。

---

## Task 1: 配置与状态层

**Files:**
- Create: `skills/1-literature/scholar-track/config.json`
- Create: `skills/1-literature/scholar-track/store.py`
- Test: `tests/test_scholar_store.py`

- [ ] **Step 1: 写 config.json**

```json
{
  "position_weights": {"last": 3.0, "first": 2.0, "middle": 0.5},
  "min_score": 6.0,
  "min_vault_papers": 3,
  "require_lead_authorship": true,
  "direction_min_papers": 2,
  "direction_min_score": 3,
  "review_trigger_pending": 3,
  "inactive_months": 12,
  "max_followed_per_day": 10,
  "arxiv_lookback_days": 7,
  "openalex_lookback_days": 30,
  "openalex_mailto": "",
  "tag_direction_map": {
    "gui agent": "GUI Agent",
    "computer use": "GUI Agent",
    "vla": "Embodied AI",
    "agentic rl": "AI Agent"
  }
}
```

- [ ] **Step 2: 写 store 的失败测试**

Create `tests/test_scholar_store.py`:

```python
import importlib.util
import json
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills" / "1-literature" / "scholar-track" / "store.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("scholar_store", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_load_returns_empty_shape_when_missing(tmp_path):
    store = load_module()
    data = store.load(tmp_path / "nope.json")
    assert data == {"version": 1, "updated": "", "scholars": []}


def test_save_is_atomic_and_roundtrips(tmp_path):
    store = load_module()
    path = tmp_path / "scholars.json"
    data = {"version": 1, "updated": "2026-07-30", "scholars": [{"openalex_id": "A1"}]}
    store.save(data, path)
    assert json.loads(path.read_text(encoding="utf-8")) == data
    assert list(tmp_path.iterdir()) == [path]  # 无残留临时文件


def test_upsert_replaces_by_openalex_id_and_preserves_order():
    store = load_module()
    data = {"version": 1, "updated": "", "scholars": [
        {"openalex_id": "A1", "display_name": "Old"},
        {"openalex_id": "A2", "display_name": "Two"},
    ]}
    store.upsert(data, {"openalex_id": "A1", "display_name": "New"})
    assert [s["display_name"] for s in data["scholars"]] == ["New", "Two"]


def test_upsert_appends_unknown_id():
    store = load_module()
    data = {"version": 1, "updated": "", "scholars": []}
    store.upsert(data, {"openalex_id": "A9", "display_name": "Nine"})
    assert data["scholars"][0]["openalex_id"] == "A9"


def test_new_record_has_all_required_fields():
    store = load_module()
    rec = store.new_record("A1", "Sergey Levine")
    for field in (
        "openalex_id", "display_name", "aliases", "affiliation", "orcid",
        "scholar_url", "track_directions", "known_coauthors", "vault_papers",
        "score", "position_profile", "status", "last_paper_date",
        "pending_since_review", "seen_paper_keys", "off_direction_count",
        "recent_papers", "tracked_since", "last_refresh", "review_updated",
    ):
        assert field in rec, field
    assert rec["status"] == "active"
    assert rec["pending_since_review"] == 0
```

- [ ] **Step 3: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_store.py -v`
Expected: FAIL，`FileNotFoundError` 或 `spec.loader` 断言失败（store.py 还不存在）

- [ ] **Step 4: 实现 store.py**

```python
#!/usr/bin/env python3
"""scholars.json 状态层：原子读写，不含业务逻辑。

状态文件是 Following 信道的唯一真相源，日更与建档都靠它做增量。
写入必须原子（tempfile + os.replace），避免中断留下半截 JSON。
"""
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STORE_PATH = ROOT / "Workbench" / "scholars.json"

EMPTY = {"version": 1, "updated": "", "scholars": []}


def load(path: Path = STORE_PATH) -> dict:
    """读状态文件。不存在或损坏时返回空结构，不抛异常——日更不能因此中断。"""
    p = Path(path)
    if not p.exists():
        return json.loads(json.dumps(EMPTY))
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(EMPTY))
    data.setdefault("version", 1)
    data.setdefault("updated", "")
    data.setdefault("scholars", [])
    return data


def save(data: dict, path: Path = STORE_PATH) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, p)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def by_id(data: dict, openalex_id: str) -> dict | None:
    for s in data.get("scholars", []):
        if s.get("openalex_id") == openalex_id:
            return s
    return None


def upsert(data: dict, record: dict) -> dict:
    """按 openalex_id 就地替换，保持原顺序；未知 id 追加到末尾。"""
    scholars = data.setdefault("scholars", [])
    for i, s in enumerate(scholars):
        if s.get("openalex_id") == record.get("openalex_id"):
            scholars[i] = record
            return record
    scholars.append(record)
    return record


def new_record(openalex_id: str, display_name: str) -> dict:
    return {
        "openalex_id": openalex_id,
        "display_name": display_name,
        "aliases": [],
        "affiliation": "",
        "orcid": "",
        "scholar_url": "",
        "track_directions": [],
        "known_coauthors": [],
        "vault_papers": [],
        "score": 0.0,
        "position_profile": {"first": 0, "middle": 0, "last": 0},
        "status": "active",
        "last_paper_date": "",
        "pending_since_review": 0,
        "seen_paper_keys": [],
        "off_direction_count": 0,
        "recent_papers": [],
        # 三个时间戳对应 spec §8 的 page frontmatter
        "tracked_since": "",    # 首次进入名单的日期，重算不覆盖
        "last_refresh": "",     # 最近一次脚本刷新
        "review_updated": "",   # 最近一次 review 重写
    }
```

- [ ] **Step 5: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_store.py -v`
Expected: PASS，5 passed

- [ ] **Step 6: Commit**

```bash
git add skills/1-literature/scholar-track/config.json \
        skills/1-literature/scholar-track/store.py \
        tests/test_scholar_store.py
git commit -m "$(cat <<'EOF'
scholar-track: 状态层 scholars.json 原子读写 + 配置阈值

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: 作者位置统计与基础打分

**Files:**
- Create: `skills/1-literature/scholar-track/roster.py`
- Test: `tests/test_scholar_roster.py`

背景：OpenAlex 的 work 对象里 `authorships` 是一个列表，每项形如
`{"author_position": "first", "author": {"id": "https://openalex.org/A5024", "display_name": "..."}, "institutions": [...]}`。
注意 **id 是完整 URL**，我们统一裁成 `A5024` 存储。

- [ ] **Step 1: 写失败测试**

Create `tests/test_scholar_roster.py`:

```python
import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills" / "1-literature" / "scholar-track" / "roster.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("scholar_roster", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def work(*authors):
    """authors: (id, name, position) 三元组序列。"""
    return {
        "authorships": [
            {
                "author_position": pos,
                "author": {"id": f"https://openalex.org/{aid}", "display_name": name},
            }
            for aid, name, pos in authors
        ]
    }


def test_short_id_strips_url_prefix():
    r = load_module()
    assert r.short_id("https://openalex.org/A5024") == "A5024"
    assert r.short_id("A5024") == "A5024"
    assert r.short_id("") == ""


def test_position_counts_aggregates_across_works():
    r = load_module()
    works = [
        work(("A1", "X", "first"), ("A2", "Y", "last")),
        work(("A2", "Y", "first"), ("A3", "Z", "middle"), ("A1", "X", "last")),
    ]
    assert r.position_counts(works, "A1") == {"first": 1, "middle": 0, "last": 1}
    assert r.position_counts(works, "A2") == {"first": 1, "middle": 0, "last": 1}
    assert r.position_counts(works, "A3") == {"first": 0, "middle": 1, "last": 0}


def test_position_counts_unknown_author_is_all_zero():
    r = load_module()
    assert r.position_counts([work(("A1", "X", "first"))], "A9") == {
        "first": 0, "middle": 0, "last": 0
    }


def test_base_score_uses_position_weights():
    r = load_module()
    weights = {"last": 3.0, "first": 2.0, "middle": 0.5}
    assert r.base_score({"first": 1, "middle": 2, "last": 3}, weights) == 12.0
    assert r.base_score({"first": 0, "middle": 0, "last": 0}, weights) == 0.0
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_roster.py -v`
Expected: FAIL，roster.py 不存在

- [ ] **Step 3: 实现 roster.py 第一部分**

```python
#!/usr/bin/env python3
"""Following 名单的纯逻辑层：打分、方向判定、入选、休眠。

设计约束：本模块不发网络请求、不读写文件。所有输入都是已经取好的
dict/list，所有输出都是纯值。这样全部逻辑可以零 mock 测试。
"""
import math
import re

POSITIONS = ("first", "middle", "last")


def short_id(openalex_id: str) -> str:
    """OpenAlex 的 author/work id 是完整 URL，统一裁成 A5024 形式。"""
    if not openalex_id:
        return ""
    return openalex_id.rstrip("/").rsplit("/", 1)[-1]


def position_counts(works: list[dict], author_id: str) -> dict:
    """统计某作者在给定 works 里的一作/中间/末作次数。"""
    counts = {p: 0 for p in POSITIONS}
    target = short_id(author_id)
    for w in works:
        for a in w.get("authorships", []) or []:
            author = a.get("author") or {}
            if short_id(author.get("id", "")) != target:
                continue
            pos = a.get("author_position", "middle")
            if pos not in counts:
                pos = "middle"
            counts[pos] += 1
    return counts


def base_score(counts: dict, weights: dict) -> float:
    return float(sum(counts.get(p, 0) * weights.get(p, 0.0) for p in POSITIONS))
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_roster.py -v`
Expected: PASS，4 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/roster.py tests/test_scholar_roster.py
git commit -m "$(cat <<'EOF'
scholar-track: 作者位置统计与加权打分

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: 方向判定

**Files:**
- Modify: `skills/1-literature/scholar-track/roster.py`
- Modify: `tests/test_scholar_roster.py`

背景：`Workbench/config/team-config.json` 的 `interests` 是四个方向，每个带 `keywords` 列表（GUI Agent / VLM / Multimodal / AI Agent / Embodied AI）。论文笔记的 tag 是连字符形式（`gui-agent`），需要归一化后才能命中关键词 `GUI agent`。

- [ ] **Step 1: 追加失败测试**

Append to `tests/test_scholar_roster.py`:

```python
INTERESTS = [
    {"name": "GUI Agent", "keywords": ["GUI agent", "computer use", "web agent"]},
    {"name": "Embodied AI", "keywords": ["VLA", "manipulation", "navigation"]},
    {"name": "AI Agent", "keywords": ["LLM agent", "agentic RL"]},
]


def test_normalize_tag_converts_hyphen_and_case():
    r = load_module()
    assert r.normalize_tag("gui-agent") == "gui agent"
    assert r.normalize_tag("Computer_Use") == "computer use"
    assert r.normalize_tag("  vla  ") == "vla"


def test_match_directions_hits_via_title():
    r = load_module()
    hits = r.match_directions("A Web Agent for Long-Horizon Tasks", [], INTERESTS, {})
    assert hits == ["GUI Agent"]


def test_match_directions_hits_via_normalized_tag():
    r = load_module()
    hits = r.match_directions("Untitled", ["gui-agent"], INTERESTS, {})
    assert hits == ["GUI Agent"]


def test_match_directions_can_return_multiple():
    r = load_module()
    hits = r.match_directions("VLA meets LLM agent", [], INTERESTS, {})
    assert set(hits) == {"Embodied AI", "AI Agent"}


def test_match_directions_uses_tag_map_fallback():
    r = load_module()
    # "screen-grounding" 不在任何 keywords 字面里，靠显式映射兜底
    hits = r.match_directions("Untitled", ["screen-grounding"], INTERESTS,
                              {"screen grounding": "GUI Agent"})
    assert hits == ["GUI Agent"]


def test_match_directions_returns_empty_when_nothing_matches():
    r = load_module()
    assert r.match_directions("Sparse Matrix Factorization", ["math"], INTERESTS, {}) == []


def test_track_directions_requires_min_papers():
    r = load_module()
    per_paper = [["GUI Agent"], ["GUI Agent"], ["Embodied AI"]]
    assert r.track_directions(per_paper, min_papers=2) == ["GUI Agent"]


def test_track_directions_sorted_by_paper_count_desc():
    r = load_module()
    per_paper = [["A"], ["A"], ["B"], ["B"], ["B"]]
    assert r.track_directions(per_paper, min_papers=2) == ["B", "A"]
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_roster.py -v`
Expected: FAIL，`AttributeError: module has no attribute 'normalize_tag'`

- [ ] **Step 3: 追加实现**

Append to `roster.py`:

```python
def normalize_tag(tag: str) -> str:
    """gui-agent → gui agent。tag 用连字符，keywords 用空格，必须先归一。"""
    return re.sub(r"[-_]+", " ", (tag or "").strip().lower())


def match_directions(
    title: str, tags: list[str], interests: list[dict], tag_map: dict | None = None
) -> list[str]:
    """判断一篇论文命中哪些研究方向。

    先用 title + 归一化 tag 的合并文本去字面匹配各 interest 的 keywords；
    再用 config 的 tag_direction_map 给字面匹配不上的 tag 兜底。
    """
    normed_tags = [normalize_tag(t) for t in (tags or [])]
    text = (title or "").lower() + " " + " ".join(normed_tags)
    hits: list[str] = []
    for it in interests:
        name = it.get("name", "")
        if not name or name in hits:
            continue
        if any(kw.lower() in text for kw in it.get("keywords", [])):
            hits.append(name)
    for t in normed_tags:
        mapped = (tag_map or {}).get(t)
        if mapped and mapped not in hits:
            hits.append(mapped)
    return hits


def track_directions(per_paper_directions: list[list[str]], min_papers: int = 2) -> list[str]:
    """某学者跟踪哪些方向：其名下论文在该方向命中 >= min_papers 篇。

    返回按论文数降序（并列时按名称升序，保证确定性）。
    """
    counts: dict[str, int] = {}
    for dirs in per_paper_directions:
        for d in dirs:
            counts[d] = counts.get(d, 0) + 1
    kept = [(d, c) for d, c in counts.items() if c >= min_papers]
    kept.sort(key=lambda x: (-x[1], x[0]))
    return [d for d, _ in kept]
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_roster.py -v`
Expected: PASS，12 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/roster.py tests/test_scholar_roster.py
git commit -m "$(cat <<'EOF'
scholar-track: 方向判定——tag 归一化 + interests 关键词匹配 + 显式映射兜底

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: 聚焦度、入选判定、休眠判定

**Files:**
- Modify: `skills/1-literature/scholar-track/roster.py`
- Modify: `tests/test_scholar_roster.py`

设计意图：`focus_factor` 惩罚"什么方向都沾一点"的人。用方向分布的归一化熵，全集中→1.0，四方向均匀→0.6。

- [ ] **Step 1: 追加失败测试**

Append to `tests/test_scholar_roster.py`:

```python
def test_focus_factor_is_one_when_single_direction():
    r = load_module()
    assert r.focus_factor(["A", "A", "A"], total_directions=4) == 1.0


def test_focus_factor_is_one_for_empty_input():
    r = load_module()
    assert r.focus_factor([], total_directions=4) == 1.0


def test_focus_factor_penalizes_uniform_spread():
    r = load_module()
    spread = r.focus_factor(["A", "B", "C", "D"], total_directions=4)
    assert abs(spread - 0.6) < 1e-9


def test_focus_factor_is_monotonic():
    r = load_module()
    concentrated = r.focus_factor(["A", "A", "A", "B"], total_directions=4)
    spread = r.focus_factor(["A", "B", "C", "D"], total_directions=4)
    assert concentrated > spread


def test_is_eligible_accepts_qualified_author():
    r = load_module()
    cfg = {"min_score": 6.0, "min_vault_papers": 3, "require_lead_authorship": True}
    assert r.is_eligible(score=9.0, n_papers=4,
                         counts={"first": 1, "middle": 3, "last": 0}, cfg=cfg) is True


def test_is_eligible_rejects_low_score():
    r = load_module()
    cfg = {"min_score": 6.0, "min_vault_papers": 3, "require_lead_authorship": True}
    assert r.is_eligible(score=5.9, n_papers=4,
                         counts={"first": 1, "middle": 3, "last": 0}, cfg=cfg) is False


def test_is_eligible_rejects_middle_author_only():
    r = load_module()
    cfg = {"min_score": 6.0, "min_vault_papers": 3, "require_lead_authorship": True}
    # 12 篇中间作者，分数够，但从没挂过一作/末作 —— 这正是同名合并的典型特征
    assert r.is_eligible(score=6.0, n_papers=12,
                         counts={"first": 0, "middle": 12, "last": 0}, cfg=cfg) is False


def test_is_eligible_rejects_too_few_papers():
    r = load_module()
    cfg = {"min_score": 6.0, "min_vault_papers": 3, "require_lead_authorship": True}
    assert r.is_eligible(score=9.0, n_papers=2,
                         counts={"first": 0, "middle": 0, "last": 3}, cfg=cfg) is False


def test_is_dormant_when_beyond_threshold():
    r = load_module()
    assert r.is_dormant("2025-01-01", today="2026-07-30", inactive_months=12) is True


def test_is_not_dormant_within_threshold():
    r = load_module()
    assert r.is_dormant("2026-01-01", today="2026-07-30", inactive_months=12) is False


def test_is_dormant_treats_empty_date_as_dormant():
    r = load_module()
    assert r.is_dormant("", today="2026-07-30", inactive_months=12) is True
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_roster.py -v`
Expected: FAIL，`AttributeError: module has no attribute 'focus_factor'`

- [ ] **Step 3: 追加实现**

Append to `roster.py`:

```python
def focus_factor(direction_labels: list[str], total_directions: int = 4) -> float:
    """主线聚焦度：方向分布越集中系数越高，范围 [0.6, 1.0]。

    用归一化香农熵。目的是压低"四个方向各沾一篇"的人——他们通常是
    大组里的挂名合作者，而非某方向的主线人物。
    """
    if not direction_labels or total_directions < 2:
        return 1.0
    counts: dict[str, int] = {}
    for d in direction_labels:
        counts[d] = counts.get(d, 0) + 1
    n = sum(counts.values())
    entropy = -sum((c / n) * math.log(c / n) for c in counts.values())
    max_entropy = math.log(total_directions)
    return 1.0 - 0.4 * (entropy / max_entropy)


def score_author(counts: dict, direction_labels: list[str], cfg: dict) -> float:
    weights = cfg.get("position_weights", {"last": 3.0, "first": 2.0, "middle": 0.5})
    total_dirs = cfg.get("_total_directions", 4)
    return base_score(counts, weights) * focus_factor(direction_labels, total_dirs)


def is_eligible(score: float, n_papers: int, counts: dict, cfg: dict) -> bool:
    """入选 Following 名单的三条硬门槛。

    require_lead_authorship 那条不只是提高质量：一个只以中间作者身份出现
    几十次的 ID，在 OpenAlex 里往往是消歧失败的合并实体。
    """
    if score < cfg.get("min_score", 6.0):
        return False
    if n_papers < cfg.get("min_vault_papers", 3):
        return False
    if cfg.get("require_lead_authorship", True):
        if counts.get("first", 0) + counts.get("last", 0) < 1:
            return False
    return True


def is_dormant(last_paper_date: str, today: str, inactive_months: int = 12) -> bool:
    """超过 inactive_months 没有新论文即休眠。空日期视为休眠。

    日期都是 YYYY-MM-DD 字符串，用月数差比较，避免引入 dateutil 依赖。
    """
    if not last_paper_date:
        return True
    try:
        ly, lm = int(last_paper_date[0:4]), int(last_paper_date[5:7])
        ty, tm = int(today[0:4]), int(today[5:7])
    except (ValueError, IndexError):
        return True
    return (ty - ly) * 12 + (tm - lm) > inactive_months
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_roster.py -v`
Expected: PASS，23 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/roster.py tests/test_scholar_roster.py
git commit -m "$(cat <<'EOF'
scholar-track: 聚焦度熵系数 + 入选三门槛 + 休眠判定

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: 网络层——vault 论文反查 OpenAlex works

**Files:**
- Create: `skills/1-literature/scholar-track/sources.py`
- Test: `tests/test_scholar_sources.py`

背景：arXiv 论文自 2022 起都有 DataCite DOI，形如 `10.48550/arXiv.2601.12345`（可直接构造，不需查询）。OpenAlex 的 `filter=doi:a|b|c` 支持 OR，每请求最多 50 个。vault 里 711 篇有 `arxiv_id`、194 篇有 `doi`、274 篇两者皆无（走 `title.search` 兜底）。

- [ ] **Step 1: 写失败测试**

Create `tests/test_scholar_sources.py`:

```python
import importlib.util
import json
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills" / "1-literature" / "scholar-track" / "sources.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("scholar_sources", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_arxiv_doi_construction():
    s = load_module()
    assert s.arxiv_doi("2601.12345") == "10.48550/arXiv.2601.12345"
    assert s.arxiv_doi("2601.12345v2") == "10.48550/arXiv.2601.12345"
    assert s.arxiv_doi("") == ""


def test_chunked_splits_evenly():
    s = load_module()
    assert list(s.chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(s.chunked([], 2)) == []


def test_fetch_works_by_dois_batches_by_50(monkeypatch):
    s = load_module()
    urls = []

    def fake_fetch(url, timeout=40):
        urls.append(url)
        return json.dumps({"results": [{"id": "https://openalex.org/W1"}]})

    monkeypatch.setattr(s, "fetch_url", fake_fetch)
    dois = [f"10.48550/arXiv.2601.{i:05d}" for i in range(120)]
    works = s.fetch_works_by_dois(dois, fetch=fake_fetch)

    assert len(urls) == 3          # 120 → 50 + 50 + 20
    assert len(works) == 3         # 每批返回 1 条
    assert "filter=doi:" in urls[0]
    assert urls[0].count("|") == 49


def test_fetch_works_by_dois_survives_bad_json(monkeypatch):
    s = load_module()

    def fake_fetch(url, timeout=40):
        return "not json"

    assert s.fetch_works_by_dois(["10.48550/arXiv.2601.00001"], fetch=fake_fetch) == []


def test_fetch_works_by_dois_survives_empty_response(monkeypatch):
    s = load_module()
    assert s.fetch_works_by_dois(["10.1"], fetch=lambda url, timeout=40: "") == []


def test_search_work_by_title_returns_first_hit():
    s = load_module()
    payload = json.dumps({"results": [
        {"id": "https://openalex.org/W1", "title": "Exactly This Title"},
        {"id": "https://openalex.org/W2", "title": "Something Else"},
    ]})
    got = s.search_work_by_title("Exactly This Title", fetch=lambda url, timeout=40: payload)
    assert got["id"] == "https://openalex.org/W1"


def test_search_work_by_title_returns_none_on_empty():
    s = load_module()
    payload = json.dumps({"results": []})
    assert s.search_work_by_title("Nope", fetch=lambda url, timeout=40: payload) is None
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: FAIL，sources.py 不存在

- [ ] **Step 3: 实现 sources.py 第一部分**

```python
#!/usr/bin/env python3
"""Following 信道的网络层：OpenAlex + arXiv。

本模块是 scholar-track 里唯一发网络请求的地方。所有函数都接受可注入的
fetch 参数，测试时传假函数即可，不需要 monkeypatch 全局。

复用 daily-papers/fetch_and_score.py 的 fetch_url（含 Lexmount 兜底）、
paper_key（跨源去重主键）与 reconstruct_abstract（OpenAlex 摘要还原）。
该目录名含连字符不是合法包名，只能用 importlib 加载。
"""
import importlib.util
import json
import re
import sys
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote

_DAILY_PATH = (
    Path(__file__).resolve().parents[1] / "daily-papers" / "fetch_and_score.py"
)


def _load_daily():
    spec = importlib.util.spec_from_file_location("fetch_and_score", _DAILY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_daily = _load_daily()
fetch_url = _daily.fetch_url
paper_key = _daily.paper_key
reconstruct_abstract = _daily.reconstruct_abstract

OPENALEX = "https://api.openalex.org"


def arxiv_doi(arxiv_id: str) -> str:
    """arXiv id → DataCite DOI。版本后缀要去掉，OpenAlex 存的是无版本形式。"""
    aid = (arxiv_id or "").strip()
    if not aid:
        return ""
    aid = re.sub(r"v\d+$", "", aid)
    return f"10.48550/arXiv.{aid}"


def chunked(items: list, n: int):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def _get_json(url: str, fetch, timeout: int = 40) -> dict:
    """取 JSON，任何失败都返回空 dict——建档不能因单批失败整个中断。"""
    raw = fetch(url, timeout=timeout)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"  [WARN] bad JSON from {url[:120]}", file=sys.stderr)
        return {}


def fetch_works_by_dois(dois: list[str], fetch=None, per_page: int = 50) -> list[dict]:
    """按 DOI 批量反查 works。OpenAlex 的 doi filter 支持 | 做 OR，上限 50。"""
    fetch = fetch or fetch_url
    out: list[dict] = []
    clean = [d for d in dois if d]
    for batch in chunked(clean, per_page):
        url = (
            f"{OPENALEX}/works?filter=doi:{'|'.join(batch)}"
            f"&per-page={per_page}&select=id,doi,title,publication_date,authorships"
        )
        data = _get_json(url, fetch)
        out.extend(data.get("results", []) or [])
        print(f"  OpenAlex works: batch {len(batch)} → {len(out)} total", file=sys.stderr)
    return out


def search_work_by_title(title: str, fetch=None) -> dict | None:
    """无 DOI 的笔记兜底：按标题搜，取第一条。宁可漏不可错配。"""
    fetch = fetch or fetch_url
    if not title.strip():
        return None
    url = (
        f"{OPENALEX}/works?filter=title.search:{quote(title)}"
        f"&per-page=1&select=id,doi,title,publication_date,authorships"
    )
    results = _get_json(url, fetch).get("results", []) or []
    return results[0] if results else None
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: PASS，7 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/sources.py tests/test_scholar_sources.py
git commit -m "$(cat <<'EOF'
scholar-track: 网络层——vault 论文经 DOI 批量反查 OpenAlex works

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: 作者详情与合作者集合

**Files:**
- Modify: `skills/1-literature/scholar-track/sources.py`
- Modify: `tests/test_scholar_sources.py`

`known_coauthors` 是 Task 7 同名过滤的判据，必须在建档阶段就攒出来。

- [ ] **Step 1: 追加失败测试**

Append to `tests/test_scholar_sources.py`:

```python
def test_fetch_author_extracts_profile_fields():
    s = load_module()
    payload = json.dumps({
        "id": "https://openalex.org/A5024",
        "display_name": "Sergey Levine",
        "display_name_alternatives": ["S. Levine"],
        "ids": {"orcid": "https://orcid.org/0000-0001-2345-6789"},
        "works_count": 812,
        "last_known_institutions": [{"display_name": "UC Berkeley"}],
    })
    got = s.fetch_author("A5024", fetch=lambda url, timeout=40: payload)
    assert got["openalex_id"] == "A5024"
    assert got["display_name"] == "Sergey Levine"
    assert got["aliases"] == ["S. Levine"]
    assert got["orcid"] == "https://orcid.org/0000-0001-2345-6789"
    assert got["affiliation"] == "UC Berkeley"


def test_fetch_author_tolerates_missing_fields():
    s = load_module()
    payload = json.dumps({"id": "https://openalex.org/A1", "display_name": "X"})
    got = s.fetch_author("A1", fetch=lambda url, timeout=40: payload)
    assert got["affiliation"] == ""
    assert got["orcid"] == ""
    assert got["aliases"] == []


def test_fetch_author_returns_none_on_failure():
    s = load_module()
    assert s.fetch_author("A1", fetch=lambda url, timeout=40: "") is None


def test_collect_coauthors_excludes_self_and_dedupes():
    s = load_module()
    works = [
        {"authorships": [
            {"author": {"id": "https://openalex.org/A1"}},
            {"author": {"id": "https://openalex.org/A2"}},
        ]},
        {"authorships": [
            {"author": {"id": "https://openalex.org/A1"}},
            {"author": {"id": "https://openalex.org/A2"}},
            {"author": {"id": "https://openalex.org/A3"}},
        ]},
    ]
    assert s.collect_coauthors(works, "A1") == ["A2", "A3"]
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: FAIL，`AttributeError: module has no attribute 'fetch_author'`

- [ ] **Step 3: 追加实现**

Append to `sources.py`:

```python
def _short(oid: str) -> str:
    return (oid or "").rstrip("/").rsplit("/", 1)[-1]


def fetch_author(author_id: str, fetch=None) -> dict | None:
    """拉 OpenAlex author 档案。失败返回 None，调用方跳过该人不中断整轮。"""
    fetch = fetch or fetch_url
    url = f"{OPENALEX}/authors/{_short(author_id)}"
    data = _get_json(url, fetch)
    if not data.get("id"):
        return None
    insts = data.get("last_known_institutions") or []
    return {
        "openalex_id": _short(data["id"]),
        "display_name": data.get("display_name", ""),
        "aliases": data.get("display_name_alternatives", []) or [],
        "orcid": (data.get("ids") or {}).get("orcid", "") or "",
        "affiliation": insts[0].get("display_name", "") if insts else "",
        "works_count": data.get("works_count", 0),
    }


def collect_coauthors(works: list[dict], author_id: str) -> list[str]:
    """该学者在 vault 论文里的全部合作者 ID，去重后排序（保证确定性）。

    这是 arXiv 同名过滤的判据：一篇 arXiv 新论文若署名 "Yang Liu" 但
    合作者与我们跟踪的这个 Yang Liu 毫无交集，多半是另一个人。
    """
    target = _short(author_id)
    seen: set[str] = set()
    for w in works:
        for a in w.get("authorships", []) or []:
            cid = _short((a.get("author") or {}).get("id", ""))
            if cid and cid != target:
                seen.add(cid)
    return sorted(seen)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: PASS，11 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/sources.py tests/test_scholar_sources.py
git commit -m "$(cat <<'EOF'
scholar-track: OpenAlex 作者档案与合作者集合（同名过滤判据）

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: arXiv 按作者查询与同名过滤

**Files:**
- Modify: `skills/1-literature/scholar-track/sources.py`
- Modify: `tests/test_scholar_sources.py`

arXiv Atom API：`http://export.arxiv.org/api/query?search_query=au:"Sergey Levine"&sortBy=submittedDate&sortOrder=descending&max_results=50`。返回 Atom XML，命名空间与 `fetch_and_score.py:ATOM_NS` 一致。

**arXiv 不返回作者 ID，只有姓名。** 所以同名过滤只能靠姓名比对：把候选论文的作者姓名集合与该学者 `known_coauthors` 对应的姓名集合求交。因此 `known_coauthors` 需要同时存 ID 和姓名——本任务改为存 `{"id": ..., "name": ...}` 结构。

- [ ] **Step 1: 追加失败测试**

Append to `tests/test_scholar_sources.py`:

```python
ARXIV_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2607.11111v1</id>
    <title>A Real-Device GUI Agent</title>
    <summary>We study GUI agents on real devices.</summary>
    <published>2026-07-28T00:00:00Z</published>
    <author><name>Sergey Levine</name></author>
    <author><name>Chelsea Finn</name></author>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2607.22222v1</id>
    <title>Unrelated Paper By A Namesake</title>
    <summary>Nothing to do with our person.</summary>
    <published>2026-07-27T00:00:00Z</published>
    <author><name>Sergey Levine</name></author>
    <author><name>Nobody Weknow</name></author>
  </entry>
</feed>
"""


def test_fetch_arxiv_by_author_parses_entries():
    s = load_module()
    papers = s.fetch_arxiv_by_author("Sergey Levine", fetch=lambda url, timeout=40: ARXIV_FEED)
    assert len(papers) == 2
    assert papers[0]["title"] == "A Real-Device GUI Agent"
    assert papers[0]["url"] == "http://arxiv.org/abs/2607.11111v1"
    assert papers[0]["date"] == "2026-07-28"
    assert papers[0]["authors"] == ["Sergey Levine", "Chelsea Finn"]
    assert papers[0]["abstract"].startswith("We study GUI agents")


def test_fetch_arxiv_by_author_quotes_name_in_query():
    s = load_module()
    seen = []

    def fake(url, timeout=40):
        seen.append(url)
        return ARXIV_FEED

    s.fetch_arxiv_by_author("Sergey Levine", fetch=fake)
    assert "au:%22Sergey+Levine%22" in seen[0] or "au:%22Sergey%20Levine%22" in seen[0]


def test_fetch_arxiv_by_author_returns_empty_on_garbage():
    s = load_module()
    assert s.fetch_arxiv_by_author("X", fetch=lambda url, timeout=40: "<not xml") == []


def test_homonym_check_confirmed_when_coauthor_overlaps():
    s = load_module()
    known = [{"id": "A2", "name": "Chelsea Finn"}]
    assert s.homonym_check(["Sergey Levine", "Chelsea Finn"], "Sergey Levine", known) == "confirmed"


def test_homonym_check_suspect_without_overlap():
    s = load_module()
    known = [{"id": "A2", "name": "Chelsea Finn"}]
    assert s.homonym_check(["Sergey Levine", "Nobody Weknow"], "Sergey Levine", known) == "suspect"


def test_homonym_check_is_case_and_space_insensitive():
    s = load_module()
    known = [{"id": "A2", "name": "chelsea  finn"}]
    assert s.homonym_check(["Sergey Levine", "Chelsea Finn"], "Sergey Levine", known) == "confirmed"


def test_homonym_check_suspect_when_no_known_coauthors():
    s = load_module()
    assert s.homonym_check(["Sergey Levine"], "Sergey Levine", []) == "suspect"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: FAIL，`AttributeError: module has no attribute 'fetch_arxiv_by_author'`

- [ ] **Step 3: 追加实现**

Append to `sources.py`:

```python
import xml.etree.ElementTree as ET

ARXIV_API = "http://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_arxiv_by_author(name: str, fetch=None, max_results: int = 50) -> list[dict]:
    """按作者姓名查 arXiv 最新投稿。arXiv 只认姓名，同名过滤交给 homonym_check。"""
    fetch = fetch or fetch_url
    url = (
        f"{ARXIV_API}?search_query=au:{quote(f'"{name}"')}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )
    raw = fetch(url, timeout=40)
    if not raw:
        return []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        print(f"  [WARN] arXiv XML parse failed for {name}", file=sys.stderr)
        return []

    papers: list[dict] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        def text(tag: str) -> str:
            el = entry.find(f"atom:{tag}", ATOM_NS)
            return (el.text or "").strip() if el is not None else ""

        authors = [
            (a.findtext("atom:name", default="", namespaces=ATOM_NS) or "").strip()
            for a in entry.findall("atom:author", ATOM_NS)
        ]
        papers.append({
            "title": " ".join(text("title").split()),
            "abstract": " ".join(text("summary").split()),
            "url": text("id"),
            "date": text("published")[:10],
            "authors": [a for a in authors if a],
            "doi": "",
            "source": "arxiv",
        })
    return papers


def _norm_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip().lower())


def homonym_check(paper_authors: list[str], target_name: str, known_coauthors: list[dict]) -> str:
    """同名判定：论文作者里除目标本人外，是否出现过已知合作者。

    返回 "confirmed"（有交集，可直接收录）或 "suspect"（无交集，进人工待判）。
    宁可多标 suspect 也不静默丢弃——漏掉真论文比多一条待判更贵。
    """
    known = {_norm_name(c.get("name", "")) for c in known_coauthors if c.get("name")}
    if not known:
        return "suspect"
    target = _norm_name(target_name)
    for a in paper_authors:
        n = _norm_name(a)
        if n and n != target and n in known:
            return "confirmed"
    return "suspect"
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: PASS，18 passed

- [ ] **Step 5: 把 collect_coauthors 改成带姓名的结构**

`homonym_check` 需要姓名，Task 6 的 `collect_coauthors` 只返回了 ID。修改它并同步测试。

Replace `collect_coauthors` in `sources.py`:

```python
def collect_coauthors(works: list[dict], author_id: str) -> list[dict]:
    """该学者在 vault 论文里的全部合作者 {id, name}，按 id 去重排序。

    arXiv API 不返回作者 ID 只返回姓名，所以同名过滤必须靠姓名比对，
    这里必须把 display_name 一起存下来。
    """
    target = _short(author_id)
    seen: dict[str, str] = {}
    for w in works:
        for a in w.get("authorships", []) or []:
            author = a.get("author") or {}
            cid = _short(author.get("id", ""))
            if cid and cid != target:
                seen.setdefault(cid, author.get("display_name", ""))
    return [{"id": cid, "name": seen[cid]} for cid in sorted(seen)]
```

Replace `test_collect_coauthors_excludes_self_and_dedupes` in `tests/test_scholar_sources.py`:

```python
def test_collect_coauthors_excludes_self_and_dedupes():
    s = load_module()
    works = [
        {"authorships": [
            {"author": {"id": "https://openalex.org/A1", "display_name": "One"}},
            {"author": {"id": "https://openalex.org/A2", "display_name": "Two"}},
        ]},
        {"authorships": [
            {"author": {"id": "https://openalex.org/A1", "display_name": "One"}},
            {"author": {"id": "https://openalex.org/A2", "display_name": "Two"}},
            {"author": {"id": "https://openalex.org/A3", "display_name": "Three"}},
        ]},
    ]
    assert s.collect_coauthors(works, "A1") == [
        {"id": "A2", "name": "Two"},
        {"id": "A3", "name": "Three"},
    ]
```

- [ ] **Step 6: 跑测试确认全绿**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: PASS，18 passed

- [ ] **Step 7: Commit**

```bash
git add skills/1-literature/scholar-track/sources.py tests/test_scholar_sources.py
git commit -m "$(cat <<'EOF'
scholar-track: arXiv 按作者查询 + 基于合作者交集的同名过滤

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: OpenAlex 按作者增量拉新作

**Files:**
- Modify: `skills/1-literature/scholar-track/sources.py`
- Modify: `tests/test_scholar_sources.py`

这是双路的第二路：权威、带 ID（无同名问题）、但滞后数天；负责补 arXiv 上没有的期刊/会议产出。

- [ ] **Step 1: 追加失败测试**

Append to `tests/test_scholar_sources.py`:

```python
def test_fetch_openalex_by_author_builds_filter(monkeypatch):
    s = load_module()
    seen = []

    def fake(url, timeout=40):
        seen.append(url)
        return json.dumps({"results": []})

    s.fetch_openalex_by_author("A5024", since="2026-07-01", fetch=fake)
    assert "author.id:A5024" in seen[0]
    assert "from_publication_date:2026-07-01" in seen[0]


def test_fetch_openalex_by_author_normalizes_records():
    s = load_module()
    payload = json.dumps({"results": [{
        "id": "https://openalex.org/W9",
        "doi": "https://doi.org/10.48550/arxiv.2607.33333",
        "title": "Journal Version Of Something",
        "publication_date": "2026-07-20",
        "abstract_inverted_index": {"Hello": [0], "world": [1]},
        "authorships": [
            {"author": {"id": "https://openalex.org/A5024", "display_name": "Sergey Levine"}},
        ],
        "locations": [{"landing_page_url": "https://arxiv.org/abs/2607.33333"}],
    }]})
    got = s.fetch_openalex_by_author("A5024", since="2026-07-01",
                                     fetch=lambda url, timeout=40: payload)
    assert len(got) == 1
    p = got[0]
    assert p["title"] == "Journal Version Of Something"
    assert p["date"] == "2026-07-20"
    assert p["abstract"] == "Hello world"
    assert p["url"] == "https://arxiv.org/abs/2607.33333"
    assert p["authors"] == ["Sergey Levine"]
    assert p["source"] == "openalex"


def test_fetch_openalex_by_author_prefers_arxiv_landing_page():
    s = load_module()
    payload = json.dumps({"results": [{
        "id": "https://openalex.org/W9",
        "doi": "https://doi.org/10.1109/TPAMI.2026.1",
        "title": "T",
        "publication_date": "2026-07-20",
        "authorships": [],
        "locations": [
            {"landing_page_url": "https://ieeexplore.ieee.org/x"},
            {"landing_page_url": "https://arxiv.org/abs/2607.44444"},
        ],
    }]})
    got = s.fetch_openalex_by_author("A1", since="2026-01-01",
                                     fetch=lambda url, timeout=40: payload)
    assert got[0]["url"] == "https://arxiv.org/abs/2607.44444"


def test_fetch_openalex_by_author_returns_empty_on_failure():
    s = load_module()
    assert s.fetch_openalex_by_author("A1", since="2026-01-01",
                                      fetch=lambda url, timeout=40: "") == []
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: FAIL，`AttributeError: module has no attribute 'fetch_openalex_by_author'`

- [ ] **Step 3: 追加实现**

Append to `sources.py`:

```python
def fetch_openalex_by_author(author_id: str, since: str, fetch=None,
                             per_page: int = 50) -> list[dict]:
    """拉某作者 since 之后的新作，归一成与 arXiv 路一致的 paper dict。

    url 优先取 arXiv landing page——这样 paper_key() 能把两路结果归并到
    同一个 arxiv id 上，否则同一篇论文会重复计入。
    """
    fetch = fetch or fetch_url
    filt = f"author.id:{_short(author_id)},from_publication_date:{since}"
    url = (
        f"{OPENALEX}/works?filter={filt}&sort=publication_date:desc"
        f"&per-page={per_page}"
    )
    results = _get_json(url, fetch).get("results", []) or []

    papers: list[dict] = []
    for w in results:
        title = (w.get("title") or "").strip()
        if not title:
            continue
        arxiv_url = ""
        for loc in w.get("locations", []) or []:
            lp = loc.get("landing_page_url") or ""
            if "arxiv.org/abs/" in lp:
                arxiv_url = lp
                break
        doi = w.get("doi") or ""
        papers.append({
            "title": title,
            "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
            "url": arxiv_url or doi or "",
            "date": w.get("publication_date", "") or "",
            "authors": [
                (a.get("author") or {}).get("display_name", "")
                for a in (w.get("authorships") or [])
            ],
            "doi": doi,
            "source": "openalex",
        })
    return papers
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_sources.py -v`
Expected: PASS，22 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/sources.py tests/test_scholar_sources.py
git commit -m "$(cat <<'EOF'
scholar-track: OpenAlex 按 author.id 增量拉新作（双路第二路）

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: 页面渲染与 review 章节保留

**Files:**
- Create: `skills/1-literature/scholar-track/pages.py`
- Test: `tests/test_scholar_pages.py`

**最关键的约束：脚本每天重写 page，但绝不能覆盖 LLM 写的 `## 研究主线 review` 章节。** 渲染时先把旧文件的 review 段落抠出来原样放回。

**第二个约束：frontmatter 必须能被 Quartz 的 YAML 解析器吃下。** 历史上踩过坑（见 memory: Quartz build dollar & YAML）——含 `:` 的值不加引号会炸构建。这里一律给字符串加双引号并转义。

- [ ] **Step 1: 写失败测试**

Create `tests/test_scholar_pages.py`:

```python
import importlib.util
from pathlib import Path

import yaml

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills" / "1-literature" / "scholar-track" / "pages.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("scholar_pages", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def record():
    return {
        "openalex_id": "A5024",
        "display_name": "Sergey Levine",
        "aliases": [],
        "affiliation": "UC Berkeley",
        "orcid": "",
        "scholar_url": "https://scholar.google.com/citations?user=8R35",
        "track_directions": ["Embodied AI"],
        "known_coauthors": [],
        "vault_papers": [
            {"note": "Papers/2604-OpenVLA.md", "title": "OpenVLA", "position": "last"},
        ],
        "score": 12.0,
        "position_profile": {"first": 0, "middle": 4, "last": 9},
        "status": "active",
        "last_paper_date": "2026-07-28",
        "pending_since_review": 2,
        "seen_paper_keys": [],
        "off_direction_count": 2,
        "tracked_since": "2026-07-30",
        "last_refresh": "2026-07-30",
        "review_updated": "",
        "recent_papers": [
            {"date": "2026-07-28", "title": "A Real-Device GUI Agent",
             "position": "last", "note": "Papers/2607-Foo.md", "url": "https://arxiv.org/abs/2607.11111"},
            {"date": "2026-07-14", "title": "Bar", "position": "middle",
             "note": "", "url": "https://arxiv.org/abs/2607.22222"},
        ],
    }


def test_slug_is_filesystem_safe():
    p = load_module()
    assert p.slug("Sergey Levine") == "Sergey-Levine"
    assert p.slug("Kai-Wei  Chang") == "Kai-Wei-Chang"
    assert p.slug("José Álvarez") == "Jose-Alvarez"


def test_frontmatter_quotes_values_containing_colon():
    p = load_module()
    text = p.render_page(record(), review_body="")
    fm = yaml.safe_load(text.split("---")[1])
    assert fm["scholar_url"] == "https://scholar.google.com/citations?user=8R35"
    assert fm["track_directions"] == ["Embodied AI"]
    assert fm["status"] == "active"


def test_frontmatter_carries_spec_timestamps():
    p = load_module()
    fm = yaml.safe_load(p.render_page(record(), review_body="").split("---")[1])
    assert fm["tracked_since"] == "2026-07-30"
    assert fm["last_refresh"] == "2026-07-30"
    assert fm["review_updated"] == ""
    assert fm["position_profile"] == "末9 / 一0 / 中4"


def test_render_includes_recent_paper_table_rows():
    p = load_module()
    text = p.render_page(record(), review_body="")
    assert "| 2026-07-28 | A Real-Device GUI Agent | 末作 | [[2607-Foo]] |" in text
    assert "| 2026-07-14 | Bar | 中间 | 未消化 |" in text


def test_render_states_off_direction_count():
    p = load_module()
    text = p.render_page(record(), review_body="")
    assert "自上次 review 更新以来另有 2 篇非跟踪方向产出（未收录）" in text


def test_render_omits_off_direction_line_when_zero():
    p = load_module()
    rec = record()
    rec["off_direction_count"] = 0
    assert "非跟踪方向产出" not in p.render_page(rec, review_body="")


def test_render_uses_placeholder_when_review_empty():
    p = load_module()
    text = p.render_page(record(), review_body="")
    assert "尚未生成" in text


def test_extract_review_pulls_existing_section():
    p = load_module()
    old = (
        "---\nname: X\n---\n"
        "## 研究主线 review\n\n他的主线是 A 到 B。\n\n"
        "## 最新论文\n\n| date |\n"
    )
    assert p.extract_review(old).strip() == "他的主线是 A 到 B。"


def test_extract_review_returns_empty_when_absent():
    p = load_module()
    assert p.extract_review("---\nname: X\n---\n## 最新论文\n") == ""


def test_update_page_preserves_review_across_rewrite(tmp_path):
    p = load_module()
    path = tmp_path / "Sergey-Levine.md"
    first = p.render_page(record(), review_body="人写的主线分析，必须活下来。")
    path.write_text(first, encoding="utf-8")

    rec = record()
    rec["recent_papers"].insert(0, {
        "date": "2026-07-30", "title": "Newest", "position": "first",
        "note": "", "url": "https://arxiv.org/abs/2607.99999",
    })
    p.update_page(path, rec)

    after = path.read_text(encoding="utf-8")
    assert "人写的主线分析，必须活下来。" in after
    assert "| 2026-07-30 | Newest | 一作 | 未消化 |" in after


def test_update_page_creates_file_when_missing(tmp_path):
    p = load_module()
    path = tmp_path / "New-Person.md"
    p.update_page(path, record())
    assert path.exists()
    assert "尚未生成" in path.read_text(encoding="utf-8")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_pages.py -v`
Expected: FAIL，pages.py 不存在

- [ ] **Step 3: 实现 pages.py**

```python
#!/usr/bin/env python3
"""Following/*.md 渲染层。

铁律：脚本每天重写 page，但 `## 研究主线 review` 章节是 LLM 写的，
必须原样保留。渲染前先从旧文件抠出该章节再放回去。

frontmatter 一律给字符串加双引号——Quartz 的 YAML 解析器对含 ':' 的
裸值会报错，历史上炸过构建。
"""
import re
import unicodedata
from pathlib import Path

REVIEW_HEADING = "## 研究主线 review"
REVIEW_PLACEHOLDER = "> 尚未生成。累计 3 篇新论文后由 scholar-track 自动撰写。"

POSITION_CN = {"first": "一作", "middle": "中间", "last": "末作"}


def slug(name: str) -> str:
    """姓名 → 文件名。去掉变音符号，空白转连字符，只留 ASCII 字母数字与连字符。"""
    norm = unicodedata.normalize("NFKD", name or "")
    ascii_only = "".join(c for c in norm if not unicodedata.combining(c))
    ascii_only = ascii_only.encode("ascii", "ignore").decode("ascii")
    ascii_only = re.sub(r"[^A-Za-z0-9\s-]", "", ascii_only)
    return re.sub(r"[\s-]+", "-", ascii_only.strip()).strip("-")


def _scalar(value) -> str:
    """YAML 标量：字符串一律双引号并转义，数字/布尔原样。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value if value is not None else "")
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _seq(values) -> str:
    return "[" + ", ".join(_scalar(v) for v in (values or [])) + "]"


def _note_link(note_path: str) -> str:
    """Papers/2607-Foo.md → [[2607-Foo]]；空值 → 未消化。"""
    if not note_path:
        return "未消化"
    return "[[" + Path(note_path).stem + "]]"


def render_frontmatter(rec: dict) -> str:
    pp = rec.get("position_profile", {}) or {}
    profile = (
        f"末{pp.get('last', 0)} / 一{pp.get('first', 0)} / 中{pp.get('middle', 0)}"
    )
    lines = [
        "---",
        f"name: {_scalar(rec.get('display_name', ''))}",
        f"openalex_id: {_scalar(rec.get('openalex_id', ''))}",
        f"scholar_url: {_scalar(rec.get('scholar_url', ''))}",
        f"orcid: {_scalar(rec.get('orcid', ''))}",
        f"affiliation: {_scalar(rec.get('affiliation', ''))}",
        f"track_directions: {_seq(rec.get('track_directions'))}",
        f"position_profile: {_scalar(profile)}",
        f"score: {round(float(rec.get('score', 0.0)), 2)}",
        f"status: {_scalar(rec.get('status', 'active'))}",
        f"last_paper_date: {_scalar(rec.get('last_paper_date', ''))}",
        f"tracked_since: {_scalar(rec.get('tracked_since', ''))}",
        f"last_refresh: {_scalar(rec.get('last_refresh', ''))}",
        f"review_updated: {_scalar(rec.get('review_updated', ''))}",
        f"pending_since_review: {int(rec.get('pending_since_review', 0))}",
        "tags: [following, scholar]",
        "---",
    ]
    return "\n".join(lines)


def render_page(rec: dict, review_body: str = "") -> str:
    body = (review_body or "").strip() or REVIEW_PLACEHOLDER

    rows = []
    for p in rec.get("recent_papers", []) or []:
        rows.append(
            f"| {p.get('date', '')} | {p.get('title', '')} | "
            f"{POSITION_CN.get(p.get('position', 'middle'), '中间')} | "
            f"{_note_link(p.get('note', ''))} |"
        )
    table = "\n".join(rows) if rows else "| — | 暂无新论文 | — | — |"

    off = int(rec.get("off_direction_count", 0))
    off_line = (
        f"\n自上次 review 更新以来另有 {off} 篇非跟踪方向产出（未收录）。\n"
        if off > 0 else ""
    )

    vault_links = " · ".join(
        _note_link(v.get("note", "")) for v in (rec.get("vault_papers") or [])
    ) or "—"

    return f"""{render_frontmatter(rec)}

# {rec.get('display_name', '')}

{REVIEW_HEADING}

{body}

## 最新论文

| date | title | 角色 | vault |
|------|-------|------|-------|
{table}
{off_line}
## vault 内已有笔记 ({len(rec.get('vault_papers') or [])})

{vault_links}
"""


def extract_review(text: str) -> str:
    """从旧 page 里抠出 review 章节正文（到下一个 ## 为止）。"""
    m = re.search(
        rf"^{re.escape(REVIEW_HEADING)}\s*\n(.*?)(?=^## |\Z)",
        text or "",
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        return ""
    body = m.group(1).strip()
    return "" if body == REVIEW_PLACEHOLDER else body


def update_page(path: Path, rec: dict) -> None:
    """就地刷新 page：保留 review，重渲染其余部分。文件不存在则新建。"""
    p = Path(path)
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_page(rec, extract_review(old)), encoding="utf-8")
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_pages.py -v`
Expected: PASS，11 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/pages.py tests/test_scholar_pages.py
git commit -m "$(cat <<'EOF'
scholar-track: page 渲染层——review 章节跨重写保留 + frontmatter 引号安全

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Following/_index.md 总览页

**Files:**
- Modify: `skills/1-literature/scholar-track/pages.py`
- Modify: `tests/test_scholar_pages.py`

- [ ] **Step 1: 追加失败测试**

Append to `tests/test_scholar_pages.py`:

```python
def two_records():
    a = record()
    b = record()
    b.update({
        "openalex_id": "A9",
        "display_name": "Dormant Person",
        "status": "dormant",
        "last_paper_date": "2024-01-01",
        "track_directions": ["GUI Agent"],
    })
    return [a, b]


def test_index_groups_active_by_direction():
    p = load_module()
    text = p.render_index(two_records())
    assert "## Embodied AI" in text
    assert "[[Sergey-Levine]]" in text


def test_index_puts_dormant_in_its_own_section():
    p = load_module()
    text = p.render_index(two_records())
    dormant_at = text.index("## 休眠")
    assert text.index("[[Dormant-Person]]") > dormant_at
    assert text.index("[[Sergey-Levine]]") < dormant_at


def test_index_lists_scholar_under_each_tracked_direction():
    p = load_module()
    rec = record()
    rec["track_directions"] = ["Embodied AI", "AI Agent"]
    text = p.render_index([rec])
    assert text.count("[[Sergey-Levine]]") == 2


def test_index_handles_empty_roster():
    p = load_module()
    text = p.render_index([])
    assert "尚无跟踪学者" in text
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_pages.py -v`
Expected: FAIL，`AttributeError: module has no attribute 'render_index'`

- [ ] **Step 3: 追加实现**

Append to `pages.py`:

```python
def render_index(records: list[dict]) -> str:
    """Following 总览：活跃学者按方向分组，休眠学者单列一节。"""
    active = [r for r in records if r.get("status") != "dormant"]
    dormant = [r for r in records if r.get("status") == "dormant"]

    def row(r: dict) -> str:
        pp = r.get("position_profile", {}) or {}
        return (
            f"| [[{slug(r.get('display_name', ''))}]] | "
            f"{r.get('affiliation', '') or '—'} | "
            f"{len(r.get('vault_papers') or [])} | "
            f"末{pp.get('last', 0)}/一{pp.get('first', 0)} | "
            f"{r.get('last_paper_date', '') or '—'} |"
        )

    header = "| 学者 | 机构 | vault 论文 | 角色 | 最近产出 |\n|---|---|---|---|---|"

    sections: list[str] = []
    directions: list[str] = []
    for r in active:
        for d in r.get("track_directions") or []:
            if d not in directions:
                directions.append(d)

    for d in sorted(directions):
        members = [r for r in active if d in (r.get("track_directions") or [])]
        members.sort(key=lambda x: -float(x.get("score", 0)))
        sections.append(f"## {d}\n\n{header}\n" + "\n".join(row(m) for m in members))

    if dormant:
        dormant.sort(key=lambda x: x.get("display_name", ""))
        sections.append(
            "## 休眠\n\n"
            "> 超过配置的 inactive_months 无新产出，已退出日常轮询；"
            "月度重算时若重新有产出会自动复活。\n\n"
            f"{header}\n" + "\n".join(row(m) for m in dormant)
        )

    body = "\n\n".join(sections) if sections else "尚无跟踪学者。跑 `build_roster.py` 建档。"

    return f"""---
title: Following
tags: [following, index]
---

# Following

按研究方向跟踪的学者档案。名单由 `skills/1-literature/scholar-track/build_roster.py`
依据 vault 内论文的作者身份与角色自动产生，非手工维护。

{body}
"""
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_pages.py -v`
Expected: PASS，15 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/scholar-track/pages.py tests/test_scholar_pages.py
git commit -m "$(cat <<'EOF'
scholar-track: Following 总览页——按方向分组 + 休眠区

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: build_roster.py CLI

**Files:**
- Create: `skills/1-literature/scholar-track/build_roster.py`
- Test: `tests/test_scholar_cli.py`

流程：扫 `Papers/*.md` → 构造 DOI → 批量反查 works → 聚合作者 → 打分/方向/入选 → 拉 author 档案 → 写 store → 渲染 pages。

- [ ] **Step 1: 写失败测试**

Create `tests/test_scholar_cli.py`:

```python
import importlib.util
import json
from pathlib import Path

BUILD_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills" / "1-literature" / "scholar-track" / "build_roster.py"
)


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_note(papers_dir: Path, name: str, title: str, arxiv_id: str, tags: str):
    (papers_dir / name).write_text(
        f'---\ntitle: "{title}"\narxiv_id: {arxiv_id}\ndoi:\ntags: [{tags}]\n---\n内容\n',
        encoding="utf-8",
    )


def test_read_vault_notes_extracts_ids_and_tags(tmp_path):
    mod = load(BUILD_PATH)
    papers = tmp_path / "Papers"
    papers.mkdir()
    write_note(papers, "2604-A.md", "OpenVLA Something", "2604.11111", "vla, embodied-ai")
    write_note(papers, "2605-B.md", "No Id Here", "", "gui-agent")

    notes = mod.read_vault_notes(papers)
    assert len(notes) == 2
    a = [n for n in notes if n["path"].endswith("2604-A.md")][0]
    assert a["arxiv_id"] == "2604.11111"
    assert a["title"] == "OpenVLA Something"
    assert a["tags"] == ["vla", "embodied-ai"]


def test_build_produces_eligible_scholars_only(tmp_path, monkeypatch):
    mod = load(BUILD_PATH)
    papers = tmp_path / "Papers"
    papers.mkdir()
    for i in range(3):
        write_note(papers, f"260{i}-P.md", f"VLA Paper {i}", f"260{i}.1111{i}", "vla")

    def fake_works(dois, fetch=None, per_page=50):
        # 每篇论文：A1 末作（合格），A2 中间作者（不合格）
        return [
            {
                "id": f"https://openalex.org/W{i}",
                "doi": f"https://doi.org/{d.lower()}",
                "title": f"VLA Paper {i}",
                "publication_date": f"2026-0{i + 1}-01",
                "authorships": [
                    {"author_position": "middle",
                     "author": {"id": "https://openalex.org/A2", "display_name": "Middle Only"}},
                    {"author_position": "last",
                     "author": {"id": "https://openalex.org/A1", "display_name": "Lead Person"}},
                ],
            }
            for i, d in enumerate(dois)
        ]

    def fake_author(aid, fetch=None):
        return {"openalex_id": aid, "display_name": f"Name {aid}", "aliases": [],
                "orcid": "", "affiliation": "Somewhere", "works_count": 10}

    monkeypatch.setattr(mod.sources, "fetch_works_by_dois", fake_works)
    monkeypatch.setattr(mod.sources, "fetch_author", fake_author)
    monkeypatch.setattr(mod.sources, "search_work_by_title", lambda t, fetch=None: None)

    interests = [{"name": "Embodied AI", "keywords": ["VLA"]}]
    data = mod.build(papers_dir=papers, interests=interests, cfg=mod.DEFAULT_CFG)

    ids = [s["openalex_id"] for s in data["scholars"]]
    assert ids == ["A1"]                       # A2 只有中间作者身份，被 require_lead_authorship 挡掉
    assert data["scholars"][0]["track_directions"] == ["Embodied AI"]
    assert data["scholars"][0]["position_profile"] == {"first": 0, "middle": 0, "last": 3}


def test_build_preserves_existing_review_state(tmp_path, monkeypatch):
    """重算不能把 pending_since_review / seen_paper_keys 清零。"""
    mod = load(BUILD_PATH)
    papers = tmp_path / "Papers"
    papers.mkdir()
    for i in range(3):
        write_note(papers, f"260{i}-P.md", f"VLA Paper {i}", f"260{i}.1111{i}", "vla")

    monkeypatch.setattr(mod.sources, "fetch_works_by_dois", lambda dois, fetch=None, per_page=50: [
        {"id": "https://openalex.org/W1", "doi": f"https://doi.org/{d.lower()}",
         "title": "VLA Paper", "publication_date": "2026-05-01",
         "authorships": [{"author_position": "last",
                          "author": {"id": "https://openalex.org/A1",
                                     "display_name": "Lead Person"}}]}
        for d in dois
    ])
    monkeypatch.setattr(mod.sources, "fetch_author", lambda aid, fetch=None: {
        "openalex_id": aid, "display_name": "Lead Person", "aliases": [],
        "orcid": "", "affiliation": "", "works_count": 1})
    monkeypatch.setattr(mod.sources, "search_work_by_title", lambda t, fetch=None: None)

    prior = {"version": 1, "updated": "", "scholars": [{
        **mod.store.new_record("A1", "Lead Person"),
        "pending_since_review": 2,
        "seen_paper_keys": ["2607.99999"],
        "scholar_url": "https://scholar.google.com/citations?user=KEEPME",
    }]}

    interests = [{"name": "Embodied AI", "keywords": ["VLA"]}]
    data = mod.build(papers_dir=papers, interests=interests, cfg=mod.DEFAULT_CFG,
                     prior=prior)
    rec = data["scholars"][0]
    assert rec["pending_since_review"] == 2
    assert rec["seen_paper_keys"] == ["2607.99999"]
    assert rec["scholar_url"].endswith("KEEPME")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_cli.py -v`
Expected: FAIL，build_roster.py 不存在

- [ ] **Step 3: 实现 build_roster.py**

```python
#!/usr/bin/env python3
"""建档 / 月度重算 Following 名单。

零 token。流程：
  扫 Papers/*.md → 构造 DOI → OpenAlex 批量反查 works → 按 author id 聚合
  → 打分 + 方向判定 + 入选 → 拉 author 档案 → 写 scholars.json → 渲染 Following/

用法：
    python3 skills/1-literature/scholar-track/build_roster.py
    python3 skills/1-literature/scholar-track/build_roster.py --dry-run
    python3 skills/1-literature/scholar-track/build_roster.py --report   # 只打分布，不落盘
"""
import argparse
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"scholar_{name}", HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


store = _load("store")
roster = _load("roster")
sources = _load("sources")
pages = _load("pages")

DEFAULT_CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
TEAM_CONFIG = ROOT / "Workbench" / "config" / "team-config.json"
PAPERS_DIR = ROOT / "Papers"
FOLLOWING_DIR = ROOT / "Following"


def load_interests(path: Path = TEAM_CONFIG) -> list[dict]:
    """研究兴趣的唯一权威来源是 team-config.json（见 CLAUDE.md）。"""
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("interests", [])
    except (OSError, json.JSONDecodeError):
        print(f"[ERROR] cannot read interests from {path}", file=sys.stderr)
        return []


def read_vault_notes(papers_dir: Path = PAPERS_DIR) -> list[dict]:
    """扫论文笔记，取 title / arxiv_id / doi / tags。只做正则，不引 yaml 依赖。"""
    notes: list[dict] = []
    for p in sorted(Path(papers_dir).glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            continue
        fm = m.group(1)

        def field(key: str) -> str:
            km = re.search(rf"^{key}:\s*(.*)$", fm, re.MULTILINE)
            return km.group(1).strip().strip('"').strip("'") if km else ""

        tags_raw = field("tags")
        tags = [t.strip().strip('"').strip("'")
                for t in tags_raw.strip("[]").split(",") if t.strip()]
        notes.append({
            "path": str(p),
            "title": field("title"),
            "arxiv_id": field("arxiv_id"),
            "doi": field("doi"),
            "tags": tags,
        })
    return notes


def _note_doi(note: dict) -> str:
    if note.get("arxiv_id"):
        return sources.arxiv_doi(note["arxiv_id"])
    doi = (note.get("doi") or "").replace("https://doi.org/", "").strip()
    return doi


def build(papers_dir: Path = PAPERS_DIR, interests: list[dict] | None = None,
          cfg: dict | None = None, prior: dict | None = None) -> dict:
    interests = interests if interests is not None else load_interests()
    cfg = dict(cfg or DEFAULT_CFG)
    cfg["_total_directions"] = max(len(interests), 2)
    prior = prior or {"version": 1, "updated": "", "scholars": []}

    notes = read_vault_notes(papers_dir)
    print(f"  vault notes: {len(notes)}", file=sys.stderr)

    doi_to_note = {}
    for n in notes:
        d = _note_doi(n)
        if d:
            doi_to_note[d.lower()] = n

    works = sources.fetch_works_by_dois(list(doi_to_note.keys()))

    # 无 DOI 的笔记走标题兜底
    matched_dois = {(w.get("doi") or "").replace("https://doi.org/", "").lower()
                    for w in works}
    for n in notes:
        d = _note_doi(n)
        if d and d.lower() in matched_dois:
            continue
        if d:
            continue  # 有 DOI 但没查到，不做标题兜底以免错配
        hit = sources.search_work_by_title(n["title"])
        if hit:
            works.append(hit)
            doi_to_note[(hit.get("doi") or hit.get("id", "")).lower()] = n

    # work id/doi → note，供方向判定取 tags
    work_note: dict[str, dict] = {}
    for w in works:
        key = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        if key in doi_to_note:
            work_note[roster.short_id(w.get("id", ""))] = doi_to_note[key]

    # 按 author 聚合
    by_author: dict[str, dict] = {}
    for w in works:
        wid = roster.short_id(w.get("id", ""))
        note = work_note.get(wid, {})
        dirs = roster.match_directions(
            w.get("title", "") or note.get("title", ""),
            note.get("tags", []),
            interests,
            cfg.get("tag_direction_map", {}),
        )
        for a in w.get("authorships", []) or []:
            author = a.get("author") or {}
            aid = roster.short_id(author.get("id", ""))
            if not aid:
                continue
            entry = by_author.setdefault(aid, {
                "display_name": author.get("display_name", ""),
                "works": [], "dirs": [], "papers": [],
            })
            entry["works"].append(w)
            entry["dirs"].extend(dirs)
            entry["papers"].append({
                "note": note.get("path", ""),
                "title": w.get("title", ""),
                "position": a.get("author_position", "middle"),
                "directions": dirs,
                "date": w.get("publication_date", ""),
            })

    data = {"version": 1, "updated": str(date.today()), "scholars": []}
    for aid, entry in by_author.items():
        counts = roster.position_counts(entry["works"], aid)
        score = roster.score_author(counts, entry["dirs"], cfg)
        if not roster.is_eligible(score, len(entry["papers"]), counts, cfg):
            continue
        dirs = roster.track_directions(
            [p["directions"] for p in entry["papers"]],
            cfg.get("direction_min_papers", 2),
        )
        if not dirs:
            continue

        old = store.by_id(prior, aid) or store.new_record(aid, entry["display_name"])
        rec = dict(old)
        profile = sources.fetch_author(aid) or {}
        rec.update({
            "openalex_id": aid,
            "display_name": profile.get("display_name") or entry["display_name"],
            "aliases": profile.get("aliases", []),
            "orcid": profile.get("orcid", ""),
            "affiliation": profile.get("affiliation", ""),
            "track_directions": dirs,
            "known_coauthors": sources.collect_coauthors(entry["works"], aid),
            "vault_papers": sorted(entry["papers"], key=lambda x: x.get("date", ""),
                                   reverse=True),
            "score": round(score, 2),
            "position_profile": counts,
        })
        # 这些字段属于日更状态，重算必须原样保留
        for keep in ("scholar_url", "pending_since_review", "seen_paper_keys",
                     "off_direction_count", "last_paper_date", "status",
                     "recent_papers", "review_updated"):
            rec[keep] = old.get(keep, rec.get(keep))
        rec["tracked_since"] = old.get("tracked_since") or str(date.today())
        rec["last_refresh"] = str(date.today())
        latest = max((p.get("date", "") for p in entry["papers"]), default="")
        if latest > (rec.get("last_paper_date") or ""):
            rec["last_paper_date"] = latest
        if roster.is_dormant(rec["last_paper_date"], str(date.today()),
                             cfg.get("inactive_months", 12)):
            rec["status"] = "dormant"
        else:
            rec["status"] = "active"
        data["scholars"].append(rec)

    data["scholars"].sort(key=lambda x: -float(x.get("score", 0)))
    return data


def write_pages(data: dict, following_dir: Path = FOLLOWING_DIR) -> None:
    following_dir.mkdir(parents=True, exist_ok=True)
    for rec in data["scholars"]:
        rec_for_page = dict(rec)
        rec_for_page.setdefault("recent_papers", [])
        pages.update_page(following_dir / f"{pages.slug(rec['display_name'])}.md",
                          rec_for_page)
    (following_dir / "_index.md").write_text(
        pages.render_index(data["scholars"]), encoding="utf-8"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="不写 scholars.json / Following")
    ap.add_argument("--report", action="store_true", help="打印分数分布后退出")
    args = ap.parse_args()

    prior = store.load()
    data = build(prior=prior)
    print(f"  eligible scholars: {len(data['scholars'])}", file=sys.stderr)

    if args.report or args.dry_run:
        for rec in data["scholars"]:
            pp = rec["position_profile"]
            print(f"{rec['score']:6.2f}  {rec['display_name']:<28} "
                  f"末{pp['last']}/一{pp['first']}/中{pp['middle']}  "
                  f"{'/'.join(rec['track_directions'])}")
        if args.report:
            return 0

    if args.dry_run:
        return 0

    store.save(data)
    write_pages(data)
    print(f"  wrote {len(data['scholars'])} scholars → Workbench/scholars.json "
          f"+ Following/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest tests/test_scholar_cli.py -v`
Expected: PASS，3 passed

- [ ] **Step 5: 跑全套测试确认无回归**

Run: `python3 -m pytest tests/ -q`
Expected: 全绿

- [ ] **Step 6: Commit**

```bash
git add skills/1-literature/scholar-track/build_roster.py tests/test_scholar_cli.py
git commit -m "$(cat <<'EOF'
scholar-track: build_roster CLI——vault 反查建档，重算保留日更状态

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: fetch_followed.py CLI

**Files:**
- Create: `skills/1-literature/scholar-track/fetch_followed.py`
- Modify: `tests/test_scholar_cli.py`
- Modify: `.gitignore`

核心逻辑：双路取新作 → `paper_key` 归并 → 方向过滤 → 日上限延后 → 更新 store → 刷 pages → 写候选文件。

- [ ] **Step 1: 追加失败测试**

Append to `tests/test_scholar_cli.py`:

```python
FETCH_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills" / "1-literature" / "scholar-track" / "fetch_followed.py"
)

INTERESTS = [{"name": "Embodied AI", "keywords": ["VLA", "manipulation"]}]


def scholar(**over):
    mod = load(FETCH_PATH)
    rec = mod.store.new_record("A1", "Lead Person")
    rec.update({
        "track_directions": ["Embodied AI"],
        "known_coauthors": [{"id": "A2", "name": "Chelsea Finn"}],
        "last_paper_date": "2026-07-01",
    })
    rec.update(over)
    return rec


def test_direction_score_uses_only_tracked_direction_keywords():
    mod = load(FETCH_PATH)
    on = {"title": "A VLA for manipulation", "abstract": ""}
    off = {"title": "Sparse Matrix Factorization", "abstract": ""}
    assert mod.direction_score(on, ["Embodied AI"], INTERESTS) >= 3
    assert mod.direction_score(off, ["Embodied AI"], INTERESTS) == 0


def test_direction_score_ignores_untracked_directions():
    mod = load(FETCH_PATH)
    interests = INTERESTS + [{"name": "GUI Agent", "keywords": ["GUI agent"]}]
    paper = {"title": "A GUI agent paper", "abstract": ""}
    # 只跟踪 Embodied AI 的人发了 GUI 论文 → 不计分
    assert mod.direction_score(paper, ["Embodied AI"], interests) == 0


def test_collect_merges_two_routes_by_paper_key(monkeypatch):
    mod = load(FETCH_PATH)
    arxiv_paper = {"title": "A VLA Paper", "abstract": "", "url": "https://arxiv.org/abs/2607.11111",
                   "date": "2026-07-28", "authors": ["Lead Person", "Chelsea Finn"],
                   "doi": "", "source": "arxiv"}
    openalex_paper = {"title": "A VLA Paper", "abstract": "", "url": "https://arxiv.org/abs/2607.11111",
                      "date": "2026-07-28", "authors": ["Lead Person"], "doi": "",
                      "source": "openalex"}
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [arxiv_paper])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [openalex_paper])

    got = mod.collect(scholar(), since="2026-07-01", cfg=mod.DEFAULT_CFG)
    assert len(got) == 1
    assert got[0]["homonym"] == "confirmed"


def test_collect_marks_suspect_when_no_known_coauthor(monkeypatch):
    mod = load(FETCH_PATH)
    paper = {"title": "A VLA Paper", "abstract": "", "url": "https://arxiv.org/abs/2607.55555",
             "date": "2026-07-28", "authors": ["Lead Person", "Total Stranger"],
             "doi": "", "source": "arxiv"}
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [paper])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [])
    got = mod.collect(scholar(), since="2026-07-01", cfg=mod.DEFAULT_CFG)
    assert got[0]["homonym"] == "suspect"


def test_openalex_route_is_always_confirmed(monkeypatch):
    """OpenAlex 按 author.id 查，本身无同名问题。"""
    mod = load(FETCH_PATH)
    paper = {"title": "A VLA Paper", "abstract": "", "url": "https://arxiv.org/abs/2607.66666",
             "date": "2026-07-28", "authors": ["Lead Person"], "doi": "", "source": "openalex"}
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [paper])
    got = mod.collect(scholar(), since="2026-07-01", cfg=mod.DEFAULT_CFG)
    assert got[0]["homonym"] == "confirmed"


def test_apply_cap_defers_overflow_without_dropping():
    mod = load(FETCH_PATH)
    papers = [{"key": f"k{i}", "dscore": 10 - i} for i in range(5)]
    kept, deferred = mod.apply_cap(papers, limit=3)
    assert [p["key"] for p in kept] == ["k0", "k1", "k2"]
    assert [p["key"] for p in deferred] == ["k3", "k4"]


def test_apply_cap_no_limit_keeps_all():
    mod = load(FETCH_PATH)
    papers = [{"key": "k0", "dscore": 1}]
    assert mod.apply_cap(papers, limit=0) == (papers, [])


def test_run_updates_state_and_counts_off_direction(monkeypatch, tmp_path):
    mod = load(FETCH_PATH)
    on_dir = {"title": "A VLA Paper", "abstract": "", "url": "https://arxiv.org/abs/2607.11111",
              "date": "2026-07-28", "authors": ["Lead Person", "Chelsea Finn"],
              "doi": "", "source": "arxiv"}
    off_dir = {"title": "Sparse Matrix Factorization", "abstract": "",
               "url": "https://arxiv.org/abs/2607.22222", "date": "2026-07-27",
               "authors": ["Lead Person", "Chelsea Finn"], "doi": "", "source": "arxiv"}
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [on_dir, off_dir])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [])

    data = {"version": 1, "updated": "", "scholars": [scholar()]}
    candidates = mod.run(data, interests=INTERESTS, cfg=mod.DEFAULT_CFG,
                         today="2026-07-30")

    rec = data["scholars"][0]
    assert rec["pending_since_review"] == 1
    assert rec["off_direction_count"] == 1
    assert "2607.11111" in rec["seen_paper_keys"]
    assert "2607.22222" not in rec["seen_paper_keys"]
    assert rec["last_paper_date"] == "2026-07-28"
    assert len(candidates) == 1
    assert candidates[0]["source"] == "followed:Lead Person"


def test_run_keeps_history_papers_on_page_but_not_in_candidates(monkeypatch):
    """daily-papers 推过的论文仍是该学者的新作，进 page 与 pending，但不重复注入。"""
    mod = load(FETCH_PATH)
    paper = {"title": "A VLA Paper", "abstract": "", "url": "https://arxiv.org/abs/2607.11111",
             "date": "2026-07-28", "authors": ["Lead Person", "Chelsea Finn"],
             "doi": "", "source": "arxiv"}
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [paper])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [])

    data = {"version": 1, "updated": "", "scholars": [scholar()]}
    candidates = mod.run(data, interests=INTERESTS, cfg=mod.DEFAULT_CFG,
                         today="2026-07-30", history_keys={"2607.11111"})
    assert candidates == []
    rec = data["scholars"][0]
    assert rec["pending_since_review"] == 1
    assert rec["recent_papers"][0]["title"] == "A VLA Paper"


def test_load_history_keys_returns_empty_when_missing(tmp_path):
    mod = load(FETCH_PATH)
    assert mod.load_history_keys(tmp_path / "nope.json") == set()


def test_run_stamps_last_refresh(monkeypatch):
    mod = load(FETCH_PATH)
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [])
    data = {"version": 1, "updated": "", "scholars": [scholar()]}
    mod.run(data, interests=INTERESTS, cfg=mod.DEFAULT_CFG, today="2026-07-30")
    assert data["scholars"][0]["last_refresh"] == "2026-07-30"
    assert data["updated"] == "2026-07-30"


def test_run_skips_already_seen_papers(monkeypatch):
    mod = load(FETCH_PATH)
    paper = {"title": "A VLA Paper", "abstract": "", "url": "https://arxiv.org/abs/2607.11111",
             "date": "2026-07-28", "authors": ["Lead Person", "Chelsea Finn"],
             "doi": "", "source": "arxiv"}
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [paper])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [])

    data = {"version": 1, "updated": "",
            "scholars": [scholar(seen_paper_keys=["2607.11111"])]}
    assert mod.run(data, interests=INTERESTS, cfg=mod.DEFAULT_CFG,
                   today="2026-07-30") == []


def test_run_skips_dormant_scholars(monkeypatch):
    mod = load(FETCH_PATH)
    called = []
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: called.append(name) or [])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [])

    data = {"version": 1, "updated": "", "scholars": [scholar(status="dormant")]}
    mod.run(data, interests=INTERESTS, cfg=mod.DEFAULT_CFG, today="2026-07-30")
    assert called == []


def test_run_marks_scholar_dormant_when_stale(monkeypatch):
    mod = load(FETCH_PATH)
    monkeypatch.setattr(mod.sources, "fetch_arxiv_by_author",
                        lambda name, fetch=None, max_results=50: [])
    monkeypatch.setattr(mod.sources, "fetch_openalex_by_author",
                        lambda aid, since, fetch=None, per_page=50: [])

    data = {"version": 1, "updated": "",
            "scholars": [scholar(last_paper_date="2024-01-01")]}
    mod.run(data, interests=INTERESTS, cfg=mod.DEFAULT_CFG, today="2026-07-30")
    assert data["scholars"][0]["status"] == "dormant"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest tests/test_scholar_cli.py -v`
Expected: FAIL，fetch_followed.py 不存在

- [ ] **Step 3: 实现 fetch_followed.py**

```python
#!/usr/bin/env python3
"""Following 日更抓取。零 token。

对每个 active 学者双路取新作（arXiv 姓名查 + OpenAlex author.id 查），
按 paper_key 归并，用其被跟踪方向的关键词过滤，更新状态并刷新 page，
最后把通过的论文写成 daily-papers 候选格式。

用法：
    python3 skills/1-literature/scholar-track/fetch_followed.py
    python3 skills/1-literature/scholar-track/fetch_followed.py --dry-run
    python3 skills/1-literature/scholar-track/fetch_followed.py \\
        --merge-into Workbench/daily/.candidates.json
"""
import argparse
import importlib.util
import json
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"scholar_{name}", HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


store = _load("store")
roster = _load("roster")
sources = _load("sources")
pages = _load("pages")

DEFAULT_CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
TEAM_CONFIG = ROOT / "Workbench" / "config" / "team-config.json"
FOLLOWING_DIR = ROOT / "Following"
CANDIDATES_PATH = ROOT / "Workbench" / "daily" / ".followed-candidates.json"
SUSPECT_PATH = ROOT / "Workbench" / "daily" / ".followed-suspect.json"


def load_interests(path: Path = TEAM_CONFIG) -> list[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("interests", [])
    except (OSError, json.JSONDecodeError):
        return []


def direction_score(paper: dict, track_directions: list[str], interests: list[dict]) -> int:
    """只用被跟踪方向的 keywords 打分。标题命中 +3，摘要命中 +1。

    这是「方向绑定」的执行点：跟踪某人是因为某个方向，他在别的方向的
    产出不进我们的库。打分口径与 fetch_and_score.score_paper 保持一致。
    """
    keywords: list[str] = []
    for it in interests:
        if it.get("name") in track_directions:
            keywords.extend(kw.lower() for kw in it.get("keywords", []))
    if not keywords:
        return 0
    title = (paper.get("title") or "").lower()
    text = title + " " + (paper.get("abstract") or "").lower()
    score = 0
    for kw in keywords:
        if kw in title:
            score += 3
        elif kw in text:
            score += 1
    return score


def collect(rec: dict, since: str, cfg: dict) -> list[dict]:
    """双路取新作，按 paper_key 归并。OpenAlex 路天然 confirmed（按 ID 查）。"""
    merged: dict[str, dict] = {}

    for p in sources.fetch_arxiv_by_author(rec["display_name"]):
        if p.get("date", "") < since:
            continue
        key = sources.paper_key(p)
        if not key:
            continue
        p = dict(p)
        p["key"] = key
        p["homonym"] = sources.homonym_check(
            p.get("authors", []), rec["display_name"], rec.get("known_coauthors", [])
        )
        merged[key] = p

    for p in sources.fetch_openalex_by_author(rec["openalex_id"], since):
        key = sources.paper_key(p)
        if not key:
            continue
        if key in merged:
            merged[key]["homonym"] = "confirmed"  # ID 路证实了姓名路
            continue
        p = dict(p)
        p["key"] = key
        p["homonym"] = "confirmed"
        merged[key] = p

    return sorted(merged.values(), key=lambda x: x.get("date", ""), reverse=True)


def apply_cap(papers: list[dict], limit: int) -> tuple[list[dict], list[dict]]:
    """日上限。超出部分按方向分排序后延后到次日，**不丢弃**。"""
    if not limit or limit <= 0:
        return papers, []
    ordered = sorted(papers, key=lambda x: -int(x.get("dscore", 0)))
    return ordered[:limit], ordered[limit:]


def _position_in(paper: dict, name: str) -> str:
    authors = paper.get("authors") or []
    if not authors:
        return "middle"
    if authors[0] == name:
        return "first"
    if authors[-1] == name:
        return "last"
    return "middle"


def load_history_keys(path: Path = ROOT / "Workbench" / "daily" / ".history.json") -> set:
    """daily-papers 已推送过的论文 key。spec §7 要求两路结果也与它去重。"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if isinstance(data, dict):
        return set(data.keys())
    if isinstance(data, list):
        return {str(x) for x in data}
    return set()


def run(data: dict, interests: list[dict], cfg: dict, today: str | None = None,
        history_keys: set | None = None) -> list[dict]:
    """主流程。就地修改 data，返回 daily-papers 候选列表。

    history_keys 里的论文仍然进 page 与 pending 计数（它确实是该学者的新作），
    但不再注入候选池——daily-papers 已经推过一次了。
    """
    today = today or str(date.today())
    history_keys = history_keys or set()
    lookback = max(int(cfg.get("arxiv_lookback_days", 7)),
                   int(cfg.get("openalex_lookback_days", 30)))
    since = str(date.fromisoformat(today) - timedelta(days=lookback))
    min_score = int(cfg.get("direction_min_score", 3))

    accepted_all: list[dict] = []
    suspects: list[dict] = []

    for rec in data.get("scholars", []):
        if rec.get("status") == "dormant":
            continue

        found = collect(rec, since, cfg)
        seen = set(rec.get("seen_paper_keys", []))
        fresh = [p for p in found if p["key"] not in seen]

        on_direction: list[dict] = []
        for p in fresh:
            p["dscore"] = direction_score(p, rec.get("track_directions", []), interests)
            if p["dscore"] < min_score:
                rec["off_direction_count"] = rec.get("off_direction_count", 0) + 1
                continue
            if p["homonym"] == "suspect":
                suspects.append({"scholar": rec["display_name"], **p})
                continue
            on_direction.append(p)

        kept, deferred = apply_cap(on_direction, int(cfg.get("max_followed_per_day", 10)))
        if deferred:
            print(f"  [CAP] {rec['display_name']}: {len(deferred)} 篇延后到次日"
                  f"（未丢弃）", file=sys.stderr)

        recent = rec.get("recent_papers", []) or []
        for p in kept:
            rec.setdefault("seen_paper_keys", []).append(p["key"])
            rec["pending_since_review"] = rec.get("pending_since_review", 0) + 1
            if p.get("date", "") > (rec.get("last_paper_date") or ""):
                rec["last_paper_date"] = p["date"]
            recent.insert(0, {
                "date": p.get("date", ""),
                "title": p.get("title", ""),
                "position": _position_in(p, rec["display_name"]),
                "note": "",
                "url": p.get("url", ""),
            })
            if p["key"] in history_keys:
                continue  # daily-papers 已推过，进 page 但不重复注入候选池
            accepted_all.append({
                "title": p.get("title", ""),
                "authors": ", ".join(p.get("authors", [])),
                "abstract": p.get("abstract", ""),
                "url": p.get("url", ""),
                "doi": p.get("doi", ""),
                "date": p.get("date", ""),
                "score": p["dscore"],
                "source": f"followed:{rec['display_name']}",
            })
        rec["recent_papers"] = recent[:20]
        rec["last_refresh"] = today

        if roster.is_dormant(rec.get("last_paper_date", ""), today,
                             cfg.get("inactive_months", 12)):
            rec["status"] = "dormant"

    data["updated"] = today
    if suspects:
        SUSPECT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SUSPECT_PATH.write_text(json.dumps(suspects, ensure_ascii=False, indent=2),
                                encoding="utf-8")
        print(f"  [SUSPECT] {len(suspects)} 篇同名待判 → {SUSPECT_PATH}", file=sys.stderr)
    return accepted_all


def backfill_note_links(data: dict, papers_dir: Path = ROOT / "Papers") -> None:
    """已消化的论文回填 vault 链接：按 arxiv id 匹配 Papers/ 里的笔记。"""
    index: dict[str, str] = {}
    for p in sorted(Path(papers_dir).glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")[:2000]
        for token in sources.re.findall(r"(\d{4}\.\d{4,5})", text):
            index.setdefault(token, str(p))
    for rec in data.get("scholars", []):
        for item in rec.get("recent_papers", []) or []:
            if item.get("note"):
                continue
            aid = sources.re.search(r"(\d{4}\.\d{4,5})", item.get("url", ""))
            if aid and aid.group(1) in index:
                item["note"] = index[aid.group(1)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--merge-into", default="",
                    help="把候选合并进指定的 .candidates.json")
    args = ap.parse_args()

    data = store.load()
    if not data["scholars"]:
        print("  scholars.json 为空，先跑 build_roster.py", file=sys.stderr)
        return 1

    candidates = run(data, load_interests(), DEFAULT_CFG,
                     history_keys=load_history_keys())
    backfill_note_links(data)
    print(f"  followed candidates: {len(candidates)}", file=sys.stderr)

    if args.dry_run:
        print(json.dumps(candidates, ensure_ascii=False, indent=2))
        return 0

    store.save(data)
    FOLLOWING_DIR.mkdir(parents=True, exist_ok=True)
    for rec in data["scholars"]:
        pages.update_page(FOLLOWING_DIR / f"{pages.slug(rec['display_name'])}.md", rec)
    (FOLLOWING_DIR / "_index.md").write_text(
        pages.render_index(data["scholars"]), encoding="utf-8")

    CANDIDATES_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES_PATH.write_text(json.dumps(candidates, ensure_ascii=False, indent=2),
                               encoding="utf-8")

    if args.merge_into:
        target = Path(args.merge_into)
        existing = []
        if target.exists():
            try:
                existing = json.loads(target.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []
        keys = {sources.paper_key(p) for p in existing}
        merged = existing + [c for c in candidates if sources.paper_key(c) not in keys]
        target.write_text(json.dumps(merged, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        print(f"  merged → {target} ({len(merged)} total)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: `sources.py` 暴露 `re` 供 backfill 使用**

`backfill_note_links` 用了 `sources.re`。`sources.py` 顶部已 `import re`，模块属性天然可访问，无需改动。跑测试验证。

Run: `python3 -m pytest tests/test_scholar_cli.py -v`
Expected: PASS，16 passed

- [ ] **Step 5: 忽略运行时候选文件**

Append to `.gitignore`:

```
Workbench/daily/.followed-candidates.json
Workbench/daily/.followed-suspect.json
```

- [ ] **Step 6: 跑全套测试**

Run: `python3 -m pytest tests/ -q`
Expected: 全绿

- [ ] **Step 7: Commit**

```bash
git add skills/1-literature/scholar-track/fetch_followed.py \
        tests/test_scholar_cli.py .gitignore
git commit -m "$(cat <<'EOF'
scholar-track: 日更抓取——双路归并、方向过滤、上限延后不丢弃、休眠标记

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: SKILL.md

**Files:**
- Create: `skills/1-literature/scholar-track/SKILL.md`

格式规范见 `references/skill-protocol.md`，参照 `skills/1-literature/survey-refresh/SKILL.md` 的结构。

- [ ] **Step 1: 读协议**

Run: `cat references/skill-protocol.md`
确认 frontmatter 必填字段与 Guard/Verify 的写法要求。

- [ ] **Step 2: 写 SKILL.md**

```markdown
---
name: scholar-track
description: 学者跟踪信道。按 OpenAlex author ID 跟踪 30-50 位高相关学者在其被跟踪方向上的新作，维护 Following/ 下的个人研究主线档案。触发词："跟踪学者""更新 Following""重建学者名单""写 XXX 的研究主线"
argument-hint: "[build | fetch | review <学者名>]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

## Purpose

补上 vault 唯一缺失的 person-pull 论文发现信道。现有 daily-papers 四个源全是
topic-pull（关键词/venue 打分），会系统性漏掉两类论文：标题不含监控关键词的、
以及 HF 无热度且不在监控 venue 的。领域专家的新作高频落在这两类里。

跟踪单位是「某人在方向 D 上的产出」，不是「某人的全部产出」。

## Steps

### 模式 A：建档 / 月度重算（`build`）

```bash
python3 skills/1-literature/scholar-track/build_roster.py --report   # 先看分布
python3 skills/1-literature/scholar-track/build_roster.py            # 确认后落盘
```

`--report` 打印每人的分数、角色分布与方向，**不写任何文件**。首次运行或调阈值后
必须先跑 `--report` 人工看一眼再落盘：名单应落在 30-50 人，若明显偏离，调
`config.json` 的 `min_score` / `min_vault_papers`。

落盘后写 `Workbench/scholars.json` 与 `Following/*.md`。重算保留日更状态字段
（`pending_since_review` / `seen_paper_keys` / `scholar_url` / `off_direction_count`）。

### 模式 B：日更抓取（`fetch`）

```bash
python3 skills/1-literature/scholar-track/fetch_followed.py \
  --merge-into Workbench/daily/.candidates.json
```

零 token。双路取新作 → `paper_key` 归并 → 只用被跟踪方向的 keywords 过滤 →
更新状态与 page → 候选合流进 daily-papers。

跑完检查 stderr：
- `[CAP] X: N 篇延后到次日` → 正常泄洪，次日会重新评估
- `[SUSPECT] N 篇同名待判` → 读 `Workbench/daily/.followed-suspect.json`，
  逐条判断是否同名误收。确认是本人的，手动把其合作者补进该学者的
  `known_coauthors` 后重跑；确认不是的，忽略即可。

### 模式 C：重写研究主线 review（`review`）

读 `Workbench/scholars.json`，挑出 `pending_since_review >= 3` 的学者。
每人派发一个 subagent，输入：

1. 该学者 `vault_papers` 指向的笔记全文
2. `recent_papers` 里尚未消化论文的标题与摘要
3. 其 `track_directions`
4. `off_direction_count`

要求 subagent 产出 300-500 字，写进该 page 的 `## 研究主线 review` 章节：

- **主线是什么**：这些工作在解同一个什么问题，不是成果罗列
- **近期转向**：与早期工作相比方法或问题设定变了什么，证据是哪几篇
- **与本 vault 四个方向的接口**：哪里可以接上我们在做的事
- **内部矛盾或未解问题**：他自己的工作之间打架的地方，这是最有价值的信号
- 若 `off_direction_count` 显著（≥3），点明其注意力正在漂移出被跟踪方向

写完把该学者的 `pending_since_review` 与 `off_direction_count` 归零，
`review_updated` 置为今天。

## Guard

- **review 章节神圣**：脚本每天重写 page，但 `## 研究主线 review` 是人/LLM 写的，
  `pages.update_page` 会抠出旧内容放回。任何改动都不得破坏这个保留机制。
- **方向绑定不可绕过**：只用该学者 `track_directions` 的 keywords 打分。
  不得因为「这篇论文看起来有意思」就收录方向外的产出。
- **同名不静默丢弃**：`homonym: suspect` 的论文写进 `.followed-suspect.json` 待判，
  不得直接扔掉，也不得直接当作本人论文收录。
- **上限只延后不丢弃**：超 `max_followed_per_day` 的候选不写 `seen_paper_keys`，
  次日重新评估；且必须在 stderr 显式记录延后数量，不做静默截断。
- **名单不手工维护**：`Workbench/scholars.json` 的名单由 `build_roster.py` 产生。
  人只调 `config.json` 的阈值。手动加的人下次重算会被抹掉。
- **evidence 纪律**：review 中未读全文的论文不得写成定论，须标注推测。
- **秘钥零泄漏**：`LEXMOUNT_API_KEY` 只从环境变量或 `.env` 读，不写入任何可提交文件。

## Verify

- [ ] `Workbench/scholars.json` 存在，`scholars` 长度在 30-50
- [ ] 抽查 5 人：`openalex_id` 非空、`track_directions` 非空且与其 vault 论文主题一致
- [ ] 抽查同名高发姓名（Yang Liu / Wei Liu / Hao Li）：要么被拆成不同
      `openalex_id`，要么因 `require_lead_authorship` 落选，不得出现合并实体
- [ ] `Following/_index.md` 与每人 page 已生成，`## 研究主线 review` 章节存在
- [ ] 日更跑完后至少一位学者的 `recent_papers` 有新条目
- [ ] `off_direction_count` 有非零值（说明方向过滤真的在起作用）
- [ ] `npx quartz build --directory ../ --output dist` 在 `website/` 下成功，
      Explorer 中 Following 可见
```

- [ ] **Step 3: 确认没打破既有契约测试**

`tests/test_research_skill_contracts.py` **不做通用格式校验**——它是对若干指定文件的
固定断言集，不覆盖新建的 `scholar-track/SKILL.md`。这里跑它只是确认没有连带破坏。

Run: `python3 -m pytest tests/test_research_skill_contracts.py -v`
Expected: PASS

Run: `python3 -m pytest tests/test_sync_skills.py -v`
Expected: PASS。该测试校验 skills 与其分发副本的一致性；若新 skill 需要同步，
按报错提示跑对应的同步脚本后重跑。

- [ ] **Step 4: Commit**

```bash
git add skills/1-literature/scholar-track/SKILL.md
git commit -m "$(cat <<'EOF'
scholar-track: SKILL 协议——建档/日更/review 三模式与 Guard 约束

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: 首跑校准（人工 gate）

**Files:**
- Modify: `skills/1-literature/scholar-track/config.json`（按实测调阈值）
- Create: `Workbench/scholars.json`、`Following/*.md`（脚本产出）

**这一步会发真实网络请求，且必须由人看过结果才能继续。**

- [ ] **Step 1: 先跑 report 模式看分布**

Run: `python3 skills/1-literature/scholar-track/build_roster.py --report 2>&1 | tail -60`

Expected: 打印一列 `分数 姓名 角色分布 方向`。
检查三件事：
1. **入选人数**。目标 30-50。低于 20 → 调低 `min_score`；高于 60 → 调高。
2. **同名污染**。搜索输出里的 `Yang Liu` / `Wei Liu` / `Hao Li`：如果某个 ID
   显示「末0/一0/中12」这种纯中间作者高频，几乎肯定是 OpenAlex 消歧失败的
   合并实体，应当已被 `require_lead_authorship` 挡掉。若仍在名单里，记录下来。
3. **方向分布**。如果大量人横跨 3-4 个方向 → `direction_min_papers` 太松，调到 3。

- [ ] **Step 2: 调阈值直到分布合理**

改 `skills/1-literature/scholar-track/config.json`，重跑 Step 1，直到人数落在
30-50 且抽查的 5 个人方向标注正确。

- [ ] **Step 3: 落盘建档**

Run: `python3 skills/1-literature/scholar-track/build_roster.py`
Expected: stderr 打印 `wrote N scholars → Workbench/scholars.json + Following/`

Run: `ls Following/ | head -20 && python3 -c "import json;d=json.load(open('Workbench/scholars.json'));print(len(d['scholars']))"`
Expected: 目录下有 `_index.md` 与 N 个 `*.md`；N 在 30-50

- [ ] **Step 4: 跑一次日更**

Run: `python3 skills/1-literature/scholar-track/fetch_followed.py --dry-run 2>&1 | tail -40`
Expected: 打印候选 JSON 与 `followed candidates: N`。

**验收点**：至少要有 1 篇 vault 里还没有的论文。如果 N=0，检查
`arxiv_lookback_days`（默认 7 天可能太短，首跑可临时调到 30 看有没有产出）。

- [ ] **Step 5: 正式跑一次日更并检查 page**

Run: `python3 skills/1-literature/scholar-track/fetch_followed.py`
Run: `head -40 Following/_index.md`

检查：`_index.md` 按方向分组、表格行数与名单一致。

Run: 随便挑一个 page `cat Following/<某人>.md`
检查：frontmatter 完整、`## 研究主线 review` 有占位符、最新论文表有行。

- [ ] **Step 6: Commit**

```bash
git add skills/1-literature/scholar-track/config.json Workbench/scholars.json Following/
git commit -m "$(cat <<'EOF'
scholar-track: 首跑建档——N 位学者入选，阈值按实测分布校准

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

（把 N 换成实际人数。）

---

## Task 15: 站点与工作流集成

**Files:**
- Modify: `website/quartz.layout.ts:44,84`
- Modify: `skills/1-literature/daily-papers/SKILL.md`
- Modify: `skills/1-literature/daily-papers/config.json`
- Modify: `skills/6-orchestration/autoresearch/SKILL.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Explorer 加 Following**

`website/quartz.layout.ts` 里有**两处**完全相同的 `order` 数组（`defaultContentPageLayout`
在 44 行附近、`defaultListPageLayout` 在 84 行附近）。两处都要改：

```typescript
const order = ["DomainMaps", "Papers", "Following", "Topics", "Ideas", "Projects"]
```

- [ ] **Step 2: 本地构建验证**

Run: `cd website && npx quartz build --directory ../ --output dist 2>&1 | tail -20`
Expected: 无 error 退出。若报 YAML 相关错误，检查刚生成的 `Following/*.md`
frontmatter——`pages.py` 的 `_scalar` 应该已经全部加了引号，报错说明有漏网字段。

Run: `ls website/dist/Following/ | head`
Expected: 列出生成的 HTML。

- [ ] **Step 3: daily-papers 接入**

Modify `skills/1-literature/daily-papers/config.json`，`max_per_source` 加一项：

```json
"max_per_source": {"cvf": 12, "openalex": 8, "followed": 15},
```

Modify `skills/1-literature/daily-papers/SKILL.md`，在 Step 1 与 Step 1.5 之间插入。

> **只插入，不改写既有段落。** `tests/test_research_skill_contracts.py` 对这个文件
> 断言了四个字面串：`独立 Reviewer`、`Coordinator 串行 Commit`、`partial summary`。
> 删改任何一处都会让契约测试变红。

```markdown
### Step 1.2：Following 学者新作（零 token）

```bash
python3 skills/1-literature/scholar-track/fetch_followed.py \
  --merge-into Workbench/daily/.candidates.json
```

把跟踪学者在其被跟踪方向上的新作合流进候选池，`source` 为 `followed:{姓名}`。
这些论文已经过方向过滤，**不再受全局 `min_score` 约束**——跟踪对象的方向内产出
不需要关键词二次判断。

若 `Workbench/scholars.json` 不存在，脚本会提示先跑 `build_roster.py` 并返回 1，
此时跳过本步不阻塞主流程。

Step 3 的点评来源徽章加一条：`followed:{姓名}` → `👤 {姓名}`。
```

- [ ] **Step 4: autoresearch 接入**

Modify `skills/6-orchestration/autoresearch/SKILL.md`，在调度选项中加入：

```markdown
- **Following 日更**：每轮开始时跑
  `python3 skills/1-literature/scholar-track/fetch_followed.py --merge-into Workbench/daily/.candidates.json`。
  零 token，失败不阻塞。
- **Following review 重写**：读 `Workbench/scholars.json`，若有学者
  `pending_since_review >= 3`，按 `scholar-track` SKILL 模式 C 派发 subagent
  重写其研究主线 review。一轮最多处理 3 位，优先处理 pending 最多的。
```

- [ ] **Step 5: CLAUDE.md 更新**

在目录结构一节，`Papers/` 之后加一行：

```markdown
- `Following/` — 跟踪学者的研究主线档案（`_index.md` 为总览页）
```

在核心 Skills 表中加一行：

```markdown
| `scholar-track` | 学者跟踪信道：建档 / 日更新作 / 重写研究主线 review | 补 person-pull 信道；Following 档案超期 |
```

- [ ] **Step 6: 跑全套测试 + 构建**

Run: `python3 -m pytest tests/ -q`
Expected: 全绿

Run: `python3 scripts/validate-yaml.py`
Expected: 通过（该脚本只查 `Papers/`，但顺手确认没破坏别的）

- [ ] **Step 7: Commit**

```bash
git add website/quartz.layout.ts \
        skills/1-literature/daily-papers/SKILL.md \
        skills/1-literature/daily-papers/config.json \
        skills/6-orchestration/autoresearch/SKILL.md \
        CLAUDE.md
git commit -m "$(cat <<'EOF'
scholar-track: 集成——Explorer 加 Following、daily-papers 合流、autoresearch 调度

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 16: 写出第一篇研究主线 review

**Files:**
- Modify: `Following/<某位学者>.md`

验证模式 C 端到端可用。

- [ ] **Step 1: 挑一位 vault 论文最多的学者**

Run:
```bash
python3 -c "
import json
d = json.load(open('Workbench/scholars.json'))
top = sorted(d['scholars'], key=lambda s: -len(s['vault_papers']))[:3]
for s in top:
    print(s['display_name'], len(s['vault_papers']), s['track_directions'])
    for p in s['vault_papers'][:12]:
        print('   ', p['position'], p['note'])
"
```

- [ ] **Step 2: 读该学者的笔记并撰写 review**

读上一步列出的笔记全文，按 `scholar-track` SKILL 模式 C 的四点要求写 300-500 字：
主线是什么 / 近期转向 / 与四个方向的接口 / 内部矛盾或未解问题。

用 Edit 替换该 page 里 `## 研究主线 review` 下的占位符行
（`> 尚未生成。累计 3 篇新论文后由 scholar-track 自动撰写。`）。

**纪律**：只根据实际读到的笔记内容写。没读全文的论文若要提及，须明确标注是基于
摘要的推测。宁可写短也不要填充。

- [ ] **Step 3: 验证 review 能跨脚本重写存活**

Run: `python3 skills/1-literature/scholar-track/fetch_followed.py`
Run: `grep -A5 "## 研究主线 review" Following/<该学者>.md`

Expected: 刚写的 review 原样还在。**这是 `pages.py` 保留机制的端到端验证，
如果这里丢了内容，说明 `extract_review` 有 bug，必须修完再继续。**

- [ ] **Step 4: 归零 pending 计数并盖 review 时间戳**

把 `<该学者姓名>` 换成实际姓名，`<今天日期>` 换成 `YYYY-MM-DD`：

```bash
python3 -c "
import json, sys
p = 'Workbench/scholars.json'
d = json.load(open(p))
name, today = sys.argv[1], sys.argv[2]
for s in d['scholars']:
    if s['display_name'] == name:
        s['pending_since_review'] = 0
        s['off_direction_count'] = 0
        s['review_updated'] = today
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
" "<该学者姓名>" "<今天日期>"
```

这三个字段的归零是 SKILL 模式 C 的收尾动作，写进 SKILL.md 后每次 review 都照做。

- [ ] **Step 5: Commit**

```bash
git add Following/ Workbench/scholars.json
git commit -m "$(cat <<'EOF'
following: 首篇研究主线 review，验证 page review 章节跨重写保留

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
EOF
)"
```

---

## 完成标准

对照 spec §12 逐条核对：

- [ ] `build_roster.py` 跑通，名单 30-50 人
- [ ] 抽查 5 人非同名合并（`Yang Liu` 类被拆分或落选）
- [ ] 每人 `track_directions` 非空且与其 vault 论文主题一致
- [ ] `fetch_followed.py` 跑通，至少 1 位学者出现 vault 中尚无的新论文
- [ ] 方向过滤生效，至少 1 篇被排除并计入 `off_direction_count`
- [ ] `npx quartz build --directory ../ --output dist` 成功，Explorer 中 Following 可见
- [ ] 至少 1 篇 review 写出，且跨脚本重写存活
- [ ] `Workbench/scholars.json` 中断后可恢复（`store.load` 对损坏文件返回空结构）
- [ ] `python3 -m pytest tests/ -q` 全绿
