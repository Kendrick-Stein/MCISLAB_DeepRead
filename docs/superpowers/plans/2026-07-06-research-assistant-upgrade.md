# ReadPaperMachine 升级实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 spec `docs/superpowers/specs/2026-07-06-research-assistant-upgrade-design.md`：skill 注册去机器化 + 兴趣配置单源化、digest→survey 信息流闭环、LaTeX 写作链（related-work + vault-only 报告）、News 专栏、可 clone 的 init 向导。

**Architecture:** 本 repo 是 Obsidian vault + Markdown skill 系统：可执行逻辑分两层——机械部分是 `scripts/`/skill 目录下的 Python 脚本（pytest 测试在 `tests/`），判断部分写在各 skill 的 `SKILL.md`（协议见 `references/skill-protocol.md`：frontmatter + Purpose/Steps/Guard/Verify）。skill 通过 repo 内 `.claude/skills/` 的相对 symlink 注册为斜杠命令。

**Tech Stack:** Python 3.10+（仅标准库，测试用 pytest）、Bash、Markdown skill 协议。

**约定（所有 task 适用）：**
- 运行测试：`python3 -m pytest tests/<file> -v`（在 repo 根目录）。
- repo 有 pre-commit hook 校验全库 markdown frontmatter，commit 失败时先看 hook 输出。
- 新建/修改 SKILL.md 后，frontmatter 必须含 `name`（与目录名一致）、`description`（pushy trigger 风格）、`allowed-tools`；正文必须含 `## Purpose`、`## Steps`、`## Guard`，推荐 `## Verify`。
- 中文撰写，技术术语保持英文。

---

## Phase 0：基础设施

### Task 1: sync_skills.py — skill 注册校验与修复脚本

**Files:**
- Create: `scripts/sync_skills.py`
- Test: `tests/test_sync_skills.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_sync_skills.py
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from sync_skills import find_vault_skills, check_registration, fix_registration


def make_skill(vault: Path, category: str, name: str) -> Path:
    d = vault / "skills" / category / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n## Purpose\n")
    return d


def test_find_vault_skills(tmp_path):
    make_skill(tmp_path, "1-literature", "paper-digest")
    make_skill(tmp_path, "4-writing", "auto-cite")
    skills = find_vault_skills(tmp_path)
    assert {s.name for s in skills} == {"paper-digest", "auto-cite"}


def test_check_reports_missing_and_broken(tmp_path):
    make_skill(tmp_path, "4-writing", "auto-cite")
    reg = tmp_path / ".claude" / "skills"
    reg.mkdir(parents=True)
    os.symlink("../../skills/nonexistent", reg / "ghost")
    missing, broken = check_registration(tmp_path)
    assert [s.name for s in missing] == ["auto-cite"]
    assert [p.name for p in broken] == ["ghost"]


def test_fix_creates_relative_symlinks(tmp_path):
    skill_dir = make_skill(tmp_path, "4-writing", "auto-cite")
    fix_registration(tmp_path)
    link = tmp_path / ".claude" / "skills" / "auto-cite"
    assert link.is_symlink()
    assert not os.path.isabs(os.readlink(link))
    assert link.resolve() == skill_dir.resolve()
    missing, broken = check_registration(tmp_path)
    assert missing == [] and broken == []
```

- [ ] **Step 2: 运行确认失败**

Run: `python3 -m pytest tests/test_sync_skills.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'sync_skills'`）

- [ ] **Step 3: 实现脚本**

```python
#!/usr/bin/env python3
"""校验/修复 vault skill 在 .claude/skills/ 的注册（相对 symlink）。

用法:
    python3 scripts/sync_skills.py          # 校验，发现问题 exit 1
    python3 scripts/sync_skills.py --fix    # 为缺失的 skill 创建相对 symlink
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_vault_skills(root: Path) -> list[Path]:
    """skills/<category>/<name>/SKILL.md → 返回 skill 目录列表。"""
    return sorted(p.parent for p in root.glob("skills/*/*/SKILL.md"))


def check_registration(root: Path) -> tuple[list[Path], list[Path]]:
    """返回 (未注册的 skill 目录, .claude/skills 下悬空的 symlink)。"""
    reg = root / ".claude" / "skills"
    missing = []
    for skill in find_vault_skills(root):
        link = reg / skill.name
        if not (link.is_symlink() and link.resolve() == skill.resolve()):
            missing.append(skill)
    broken = []
    if reg.is_dir():
        for link in sorted(reg.iterdir()):
            if link.is_symlink() and not link.resolve().exists():
                broken.append(link)
    return missing, broken


def fix_registration(root: Path) -> None:
    reg = root / ".claude" / "skills"
    reg.mkdir(parents=True, exist_ok=True)
    for skill in check_registration(root)[0]:
        link = reg / skill.name
        if link.is_symlink():
            link.unlink()
        link.symlink_to(Path(os.path.relpath(skill, reg)))


def main() -> int:
    fix = "--fix" in sys.argv
    if fix:
        fix_registration(ROOT)
    missing, broken = check_registration(ROOT)
    for s in missing:
        print(f"MISSING: {s.relative_to(ROOT)} 未注册到 .claude/skills/")
    for b in broken:
        print(f"BROKEN: {b} 指向不存在的目标")
    if missing or broken:
        print("提示: 运行 python3 scripts/sync_skills.py --fix 修复缺失注册；悬空 symlink 请人工确认后删除")
        return 1
    print(f"OK: {len(find_vault_skills(ROOT))} 个 skill 全部已注册")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 测试通过**

Run: `python3 -m pytest tests/test_sync_skills.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/sync_skills.py tests/test_sync_skills.py
git commit -m "feat(scripts): sync_skills.py 校验/修复 skill 注册"
```

### Task 2: 执行注册迁移（.claude/skills symlink 入库 + 清理 ~/.claude/skills）

**Files:**
- Create: `.claude/skills/<18 个 skill symlink>`（由脚本生成）
- Modify: `~/.claude/skills/` 下指向本 repo 的旧 symlink（删除，不入库）

- [ ] **Step 1: 生成 symlink 并校验**

```bash
python3 scripts/sync_skills.py --fix && python3 scripts/sync_skills.py
```

Expected: `OK: 18 个 skill 全部已注册`。`ls -la .claude/skills/` 应看到 18 个新相对 symlink（auto-cite、paper-digest、survey-refresh 尚不存在——此时是 18 个现有 skill），与原有 lark-* 条目并存。

- [ ] **Step 2: 清理 user-level 旧 symlink（避免重复注册）**

```bash
for link in ~/.claude/skills/*; do
  if [ -L "$link" ] && readlink "$link" | grep -q "Code/ReadPaperMachine"; then
    echo "removing $link -> $(readlink "$link")"; rm "$link"
  fi
done
```

Expected: 删除的均为指向本 repo 的 symlink（paper-digest、daily-papers、literature-survey、idea-generate、idea-evaluate、research-team、domain-presentation、autoresearch、agenda-evolve、memory-distill、memory-retrieve、draft-section、latex-citation-enhancer、writing-refine、experiment-design、experiment-track、result-analysis 等）。**不删除**非本 repo 来源的条目（如 guizang-ppt-skill、officecli）。

- [ ] **Step 3: 确认 git 能追踪 symlink 并 commit**

```bash
git add .claude/skills/ && git status --short .claude/skills/ | head -20
git commit -m "feat(skills): skill 注册迁移到 repo 内 .claude/skills（clone 即用）"
```

Expected: 每个 symlink 显示为新增文件（mode 120000）。

### Task 3: 兴趣配置单源化 — team-config.json + CLAUDE.md

**Files:**
- Modify: `Workbench/config/team-config.json`
- Modify: `CLAUDE.md`（"## 研究兴趣"段）

- [ ] **Step 1: 升级 team-config.json**

在现有 JSON 顶层新增 `interests` 与 `news` 字段（保留现有 collector/digest/survey/report 字段不动；`collector.keywords` 保留作向后兼容，内容以 interests 展开为准）：

```json
{
  "interests": [
    {
      "name": "GUI Agent",
      "keywords": ["GUI agent", "computer use", "computer-use", "web agent", "browser agent", "mobile agent", "GUI grounding", "agent benchmark"]
    },
    {
      "name": "VLM / Multimodal",
      "keywords": ["VLM", "vision language model", "vision-language model", "multimodal LLM", "visual reasoning", "visual grounding", "video understanding"]
    },
    {
      "name": "AI Agent",
      "keywords": ["LLM agent", "agentic RL", "agentic reinforcement learning", "tool use", "world model"]
    },
    {
      "name": "Embodied AI",
      "keywords": ["Embodied AI", "VLA", "vision-language-action", "diffusion policy", "imitation learning", "manipulation", "navigation", "sim-to-real"]
    }
  ],
  "news": {
    "sources": [
      {"name": "HuggingFace Blog", "type": "rss", "url": "https://huggingface.co/blog/feed.xml", "lang": "en"},
      {"name": "Anthropic News", "type": "web", "url": "https://www.anthropic.com/news", "lang": "en"},
      {"name": "机器之心", "type": "rss", "url": "https://www.jiqizhixin.com/rss", "lang": "zh"}
    ],
    "days": 3,
    "min_score": 1,
    "top_n": 20
  }
}
```

（用 Edit 在现有文件中插入这两个顶层 key，勿覆盖其余内容。）

- [ ] **Step 2: 校验 JSON 合法**

Run: `python3 -m json.tool Workbench/config/team-config.json > /dev/null && echo OK`
Expected: OK

- [ ] **Step 3: CLAUDE.md 研究兴趣段指向 config**

将 `CLAUDE.md` 的 `## 研究兴趣` 三行列表替换为：

```markdown
## 研究兴趣

研究兴趣的唯一权威来源是 `Workbench/config/team-config.json` 的 `interests` 字段
（当前涵盖 GUI Agent、VLM/Multimodal、AI Agent、Embodied AI 四个方向）。
daily-papers / news-digest / literature-survey 的关键词打分均从该文件读取；
调整兴趣只改这一个文件。
```

- [ ] **Step 4: Commit**

```bash
git add Workbench/config/team-config.json CLAUDE.md
git commit -m "feat(config): 研究兴趣单源化到 team-config.json，新增 interests 与 news.sources"
```

### Task 4: daily-papers 从 team-config 读取关键词

**Files:**
- Modify: `skills/1-literature/daily-papers/fetch_and_score.py`（约 L30-37 的 config 加载处）
- Test: `tests/test_daily_papers_fetch.py`（追加）

- [ ] **Step 1: 写失败测试（追加到现有测试文件）**

先读 `tests/test_daily_papers_fetch.py` 了解现有 import 方式，然后追加：

```python
def test_load_config_merges_team_interests(tmp_path, monkeypatch):
    """team-config.json 存在 interests 时，keywords = 本地 keywords ∪ interests 展开。"""
    import fetch_and_score as fs
    team = tmp_path / "team-config.json"
    team.write_text('{"interests": [{"name": "X", "keywords": ["quantum gui"]}]}')
    monkeypatch.setattr(fs, "TEAM_CONFIG_PATH", team)
    cfg = fs.load_config()
    assert "quantum gui" in cfg["keywords"]
```

- [ ] **Step 2: 运行确认失败**

Run: `python3 -m pytest tests/test_daily_papers_fetch.py -k team_interests -v`
Expected: FAIL（`AttributeError: ... has no attribute 'TEAM_CONFIG_PATH'`）

- [ ] **Step 3: 修改 fetch_and_score.py**

在 `CONFIG_PATH` 定义（L30 附近）后新增，并在 `load_config()` 里合并：

```python
TEAM_CONFIG_PATH = Path(__file__).resolve().parents[3] / "Workbench" / "config" / "team-config.json"
```

`load_config()` 末尾（return 前）加入：

```python
    if TEAM_CONFIG_PATH.exists():
        try:
            team = json.loads(TEAM_CONFIG_PATH.read_text())
            extra = [kw for it in team.get("interests", []) for kw in it.get("keywords", [])]
            seen = {k.lower() for k in config.get("keywords", [])}
            config["keywords"] = config.get("keywords", []) + [
                k for k in extra if k.lower() not in seen
            ]
        except (json.JSONDecodeError, OSError):
            pass  # team config 损坏时降级用本地 keywords，不阻塞抓取
```

（变量名以实际 `load_config()` 内部命名为准，保持局部风格一致。）

- [ ] **Step 4: 全部测试通过**

Run: `python3 -m pytest tests/test_daily_papers_fetch.py -v`
Expected: 全部 PASS（含原有用例）

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/daily-papers/fetch_and_score.py tests/test_daily_papers_fetch.py
git commit -m "feat(daily-papers): 关键词合并读取 team-config interests"
```

---

## Phase 1：信息流闭环

### Task 5: Topics survey frontmatter 增加 keywords / domain_map

**Files:**
- Modify: `Topics/*.md`（15 篇 Survey，`_index.md` 除外）

- [ ] **Step 1: 逐篇编辑 frontmatter**

为每篇 survey 的 frontmatter 增加两个字段。`keywords` 从该篇 tags 与主题派生（小写短语，供 survey_updates.py 匹配论文笔记的 tags/标题）；`domain_map` 按下表（无对应 DomainMap 的填 `null`）：

| Survey | domain_map | keywords（基准，可按该篇 tags 微调补充） |
|---|---|---|
| GUIAgent-Survey | GUI-Agent | gui-agent, gui grounding, computer-use, web agent, mobile agent |
| ComputerUseAgents-Survey | GUI-Agent | computer-use, cua, desktop agent, os agent |
| GUI-Environment-Survey | GUI-Agent | gui environment, agent environment, web environment, sandbox |
| AgentFriendlyEnvironment-Survey | GUI-Agent | agent-friendly, environment affordance, agent-facing, runtime |
| CloudPhone-GUI-VLA-Survey | GUI-Agent | cloud phone, mobile gui, android agent |
| AgenticRL-Survey | AgenticRL | agentic rl, agent reinforcement learning, grpo, rlvr |
| EmbodiedAI-Survey | EmbodiedAI | embodied ai, robot learning, manipulation |
| Embodied-Reasoning-Survey | EmbodiedAI | embodied reasoning, spatial reasoning |
| LanguageConditioned-MobileManipulation-Survey | EmbodiedAI | mobile manipulation, language-conditioned |
| VLA-Survey | EmbodiedAI | vla, vision-language-action, robot policy |
| VLN-Survey | EmbodiedAI | vln, vision-language navigation |
| VLM-Survey | VLM | vlm, vision language model, multimodal llm |
| HyperbolicManifold-Survey | HyperbolicManifold | hyperbolic, manifold, poincare |
| WorldModel-Survey | WorldModel | world model, video prediction, dynamics model |
| WorldActionModel-Survey | WorldModel | world action model, action-conditioned |

frontmatter 追加格式（以 GUIAgent-Survey 为例）：

```yaml
keywords: [gui-agent, gui grounding, computer-use, web agent, mobile agent]
domain_map: GUI-Agent
```

- [ ] **Step 2: 校验**

```bash
python3 scripts/validate-yaml.py 2>/dev/null || python3 - <<'EOF'
import yaml, glob
for f in glob.glob("Topics/*-Survey.md"):
    fm = open(f).read().split("---")[1]
    d = yaml.safe_load(fm)
    assert "keywords" in d and "domain_map" in d, f
print("OK: 15 surveys annotated")
EOF
```

Expected: OK

- [ ] **Step 3: Commit**

```bash
git add Topics/
git commit -m "feat(topics): survey frontmatter 增加 keywords/domain_map 供信息流匹配"
```

### Task 6: survey_updates.py — 记账脚本

**Files:**
- Create: `scripts/survey_updates.py`
- Test: `tests/test_survey_updates.py`

数据文件 `Workbench/survey-updates.json` 结构：`{"version": 1, "pending": [{"survey": "GUIAgent-Survey", "paper": "Papers/2607-Foo.md", "added_at": "2026-07-06"}]}`。

- [ ] **Step 1: 写失败测试**

```python
# tests/test_survey_updates.py
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from survey_updates import match_surveys, record, load_pending, clear


def make_vault(tmp_path):
    (tmp_path / "Topics").mkdir()
    (tmp_path / "Papers").mkdir()
    (tmp_path / "Workbench").mkdir()
    (tmp_path / "Topics" / "GUIAgent-Survey.md").write_text(
        "---\ntitle: GUI Agent Survey\nkeywords: [gui-agent, web agent]\ndomain_map: GUI-Agent\n---\n"
    )
    (tmp_path / "Topics" / "VLM-Survey.md").write_text(
        "---\ntitle: VLM Survey\nkeywords: [vlm]\ndomain_map: VLM\n---\n"
    )
    paper = tmp_path / "Papers" / "2607-FooAgent.md"
    paper.write_text("---\ntitle: FooAgent web agent benchmark\ntags: [gui-agent, benchmark]\n---\n")
    return paper


def test_match_by_tag_and_title(tmp_path):
    paper = make_vault(tmp_path)
    assert match_surveys(paper, tmp_path) == ["GUIAgent-Survey"]


def test_record_appends_and_dedups(tmp_path):
    paper = make_vault(tmp_path)
    record(paper, tmp_path)
    record(paper, tmp_path)  # 幂等
    pending = load_pending(tmp_path)
    assert len(pending) == 1
    assert pending[0]["survey"] == "GUIAgent-Survey"
    assert pending[0]["paper"] == "Papers/2607-FooAgent.md"


def test_clear_removes_processed(tmp_path):
    paper = make_vault(tmp_path)
    record(paper, tmp_path)
    clear("GUIAgent-Survey", ["Papers/2607-FooAgent.md"], tmp_path)
    assert load_pending(tmp_path) == []


def test_missing_json_initialized(tmp_path):
    make_vault(tmp_path)
    assert load_pending(tmp_path) == []
```

- [ ] **Step 2: 运行确认失败**

Run: `python3 -m pytest tests/test_survey_updates.py -v`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现**

```python
#!/usr/bin/env python3
"""digest→survey 记账：论文笔记按 keywords 匹配 survey，写入 Workbench/survey-updates.json。

用法:
    python3 scripts/survey_updates.py record <paper-note.md>
    python3 scripts/survey_updates.py pending [--survey NAME]
    python3 scripts/survey_updates.py clear --survey NAME --papers a.md,b.md
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _frontmatter(path: Path) -> dict:
    """轻量 frontmatter 解析：只取 title/tags/keywords（避免 yaml 依赖差异）。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm, out = m.group(1), {}
    for key in ("title", "tags", "keywords"):
        km = re.search(rf"^{key}:\s*(.+)$", fm, re.MULTILINE)
        if km:
            val = km.group(1).strip()
            if val.startswith("["):
                out[key] = [v.strip().strip("'\"") for v in val.strip("[]").split(",") if v.strip()]
            else:
                out[key] = val.strip("'\"")
    return out


def _json_path(root: Path) -> Path:
    return root / "Workbench" / "survey-updates.json"


def _load(root: Path) -> dict:
    p = _json_path(root)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass  # 损坏时重建空结构（spec §9）
    return {"version": 1, "pending": []}


def _save(root: Path, data: dict) -> None:
    _json_path(root).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_pending(root: Path = ROOT) -> list[dict]:
    return _load(root)["pending"]


def match_surveys(paper: Path, root: Path = ROOT) -> list[str]:
    fm = _frontmatter(paper)
    tags = [t.lower() for t in fm.get("tags", [])]
    title = str(fm.get("title", "")).lower()
    haystack = " ".join(tags) + " " + title
    matched = []
    for survey in sorted(root.glob("Topics/*-Survey.md")):
        kws = [k.lower() for k in _frontmatter(survey).get("keywords", [])]
        if any(kw in haystack for kw in kws):
            matched.append(survey.stem)
    return matched


def record(paper: Path, root: Path = ROOT) -> list[str]:
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


def clear(survey: str, papers: list[str], root: Path = ROOT) -> None:
    data = _load(root)
    drop = {(survey, p) for p in papers}
    data["pending"] = [e for e in data["pending"] if (e["survey"], e["paper"]) not in drop]
    _save(root, data)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_rec = sub.add_parser("record"); p_rec.add_argument("paper")
    p_pen = sub.add_parser("pending"); p_pen.add_argument("--survey")
    p_clr = sub.add_parser("clear"); p_clr.add_argument("--survey", required=True); p_clr.add_argument("--papers", required=True)
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
        clear(args.survey, args.papers.split(","))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 测试通过**

Run: `python3 -m pytest tests/test_survey_updates.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/survey_updates.py tests/test_survey_updates.py
git commit -m "feat(scripts): survey_updates.py digest→survey 记账"
```

### Task 7: paper-digest 末尾接入记账

**Files:**
- Modify: `skills/1-literature/paper-digest/SKILL.md`（在 "### Step 5：保存并记录"（L97）小节末尾、`## Guard`（L139）之前）

- [ ] **Step 1: 插入新步骤**

在 Step 5 小节末尾追加：

```markdown
### Step 6：survey 归属记账

笔记保存后，运行记账脚本把它挂到相关 survey 的待更新队列：

​```bash
python3 scripts/survey_updates.py record "Papers/{文件名}.md"
​```

- 脚本按 `Topics/*-Survey.md` frontmatter 的 `keywords` 与本笔记 tags/标题匹配，输出匹配到的 survey 列表（JSON）。
- 匹配为空是正常情况（论文不属于任何已有 survey 主题），静默继续。
- 脚本报错时不阻塞 digest：在当日 log 记一条 `survey-updates 记账失败` 即可。
- pending 的消费由 `survey-refresh` skill 负责（autoresearch 在某 survey 积压 ≥5 篇时触发）。
```

（注意：实际写入时代码块围栏不带 `​` 零宽字符——此处仅为嵌套转义。）

- [ ] **Step 2: 验证结构**

Run: `grep -n "Step 6：survey 归属记账" skills/1-literature/paper-digest/SKILL.md`
Expected: 命中一行，且位于 `## Guard` 之前。

- [ ] **Step 3: 端到端验证**

任选一篇已有笔记试跑（只写 JSON 不改笔记，可安全执行后还原）：

```bash
python3 scripts/survey_updates.py record "Papers/1700-PoincareEmbeddings.md"
python3 scripts/survey_updates.py pending
git checkout -- Workbench/survey-updates.json 2>/dev/null; rm -f Workbench/survey-updates.json
```

Expected: record 输出含 `HyperbolicManifold-Survey`；pending 列出对应条目；最后清理测试产物。

- [ ] **Step 4: Commit**

```bash
git add skills/1-literature/paper-digest/SKILL.md
git commit -m "feat(paper-digest): 消化完成后记账所属 survey"
```

### Task 8: 新 skill survey-refresh

**Files:**
- Create: `skills/1-literature/survey-refresh/SKILL.md`
- Create: `.claude/skills/survey-refresh`（symlink，跑 sync_skills --fix）

- [ ] **Step 1: 写 SKILL.md**

```markdown
---
name: survey-refresh
description: >
  当 Workbench/survey-updates.json 中某 survey 积压了新消化的论文（autoresearch 检测到 ≥5 篇
  或最老条目超 7 天），或 Supervisor 说"刷新一下 XX survey"时，
  把新论文笔记增量合并进对应 Topics/*-Survey.md，并同步刷新其 DomainMap。
argument-hint: "<survey-name，如 GUIAgent-Survey>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Purpose

信息流闭环的消费端：paper-digest 只记账（survey-updates.json），本 skill 负责把积压的新论文
增量合并进 survey，让 survey 随日常阅读越来越完善，而不必重跑完整 literature-survey。
与 literature-survey 的分工：本 skill **不做任何外部搜索**，只消化库内已 digest 的新笔记；
全量调研（含外部检索）仍由 literature-survey 承担。

## Steps

### Step 1：取 pending 列表

​```bash
python3 scripts/survey_updates.py pending --survey {survey-name}
​```

- 为空则终止：向调用方报告"无待处理条目"。
- 超过 8 篇时只取最早的 8 篇（按 added_at），其余留给下一轮——避免单次 context 过长。

### Step 2：读取 survey 现状

用 Read 读取 `Topics/{survey-name}.md` 全文，记住其章节结构、分类框架、已覆盖的论文集合、
Key Takeaways / Open Questions。

### Step 3：逐篇读新论文笔记

对 pending 中每篇，用 Read 读取 `Papers/` 笔记全文，提取：核心贡献、关键数据、
与 survey 现有分类的关系（落入哪个既有小节？是否挑战某个既有结论？是否开辟新分类？）。

### Step 4：增量更新 survey

用 Edit 修改 `Topics/{survey-name}.md`（遵循 literature-survey 的增量更新规则）：

1. 把每篇新论文以 `[[wikilink]]` 并入对应小节，附一句话定位（贡献 + 与既有工作的关系）。
2. 若新证据**推翻或削弱**某既有结论，修改该结论并标注新证据来源；
   未被挑战的原有内容一律保留。
3. 若多篇新论文形成新 pattern，可新增小节；更新 Key Takeaways / Open Questions。
4. 更新 frontmatter：`date_updated` 设为今天，`papers_analyzed` 增加新并入篇数。

### Step 5：刷新 DomainMap（若有）

读 survey frontmatter 的 `domain_map` 字段：

- 为 `null` 或对应 `DomainMaps/{name}.md` 不存在 → 跳过本步。
- 否则用 Edit 更新该 DomainMap：在文件末尾维护一个 `## 近期格局变化` 小节
  （不存在则创建），追加/合并本轮变化的 2-4 条要点（新 pattern、被修正的结论），
  每条附 survey 与论文的 `[[wikilink]]`。仅当本轮确有格局级变化时才写；
  单纯"多了几篇论文"不算。

### Step 6：清账并记录

​```bash
python3 scripts/survey_updates.py clear --survey {survey-name} --papers "Papers/a.md,Papers/b.md"
​```

（papers 为本轮实际并入的条目。）然后在 `Workbench/logs/YYYY-MM-DD.md` 追加：

​```markdown
### [HH:MM] survey-refresh — {survey-name}
- **merged**: <N 篇：[[...]], [[...]]>
- **changes**: <survey 结构性变化一句话；无则"仅增量并入">
- **domain_map**: <刷新了哪个 / skipped>
​```

## Guard

- 禁止外部搜索（WebSearch/WebFetch 不在 allowed-tools 中，这是设计而非疏漏）。
- 不删除 survey 中未被新证据推翻的原有结论；修改结论必须标注推翻它的论文 wikilink。
- 单轮最多并入 8 篇；不一次清空大积压。
- 本 skill 是 DomainMaps 的唯一自动写入方；只写 `## 近期格局变化` 小节，
  不改 DomainMap 其他部分（Established Knowledge 等仍由 Human 经 queue Review 晋升）。
- 只 clear 本轮实际并入的条目；跳过/失败的留在 pending。

## Verify

- [ ] survey 的 `date_updated` 为今天，`papers_analyzed` 已更新
- [ ] 本轮每篇论文在 survey 正文中有 `[[wikilink]]`
- [ ] survey-updates.json 中本轮条目已清除
- [ ] 日志已追加

## Examples

`survey-refresh GUIAgent-Survey` → pending 6 篇 → 并入 6 篇（2 篇进"Grounding"小节、
3 篇进"RL 训练"、1 篇新开"环境侧监督"小节）→ 刷新 DomainMaps/GUI-Agent.md 近期格局变化
→ 清账 → 日志。
```

（写入时把 `​`​`` 围栏中的零宽字符去掉，用正常三反引号嵌套四反引号外围。）

- [ ] **Step 2: 注册并校验**

```bash
python3 scripts/sync_skills.py --fix && python3 scripts/sync_skills.py
```

Expected: `OK: 19 个 skill 全部已注册`

- [ ] **Step 3: 审查 DomainMaps 写入权（spec §4.3）**

```bash
grep -rn "DomainMap" skills/*/*/SKILL.md | grep -v "survey-refresh"
```

逐条确认命中的引用均为**只读**（读取上下文）或**显式禁写**（memory-distill、literature-survey 已明确"不直接修改 DomainMaps"，经 queue Review 建议晋升的路径保留不动）。2026-07-06 调查结论：现有 7 个引用 skill 全部只读/禁写，预期无需改动；若发现例外（某 skill 的 Steps 指示直接 Edit/Write DomainMaps/），把该步骤改为"在 queue Review 提建议"，并入本 task 的 commit。

- [ ] **Step 4: Commit**

```bash
git add skills/1-literature/survey-refresh/ .claude/skills/survey-refresh
git commit -m "feat(skills): survey-refresh——digest→survey 增量迭代 + DomainMap 自动刷新"
```

### Task 9: autoresearch 接线

**Files:**
- Modify: `skills/6-orchestration/autoresearch/SKILL.md`（READ STATE 列表 + JUDGE 表）

- [ ] **Step 1: READ STATE 增读两项**

在 READ STATE 编号列表（现有 5 项，`Workbench/agenda.md` 至 logs）末尾追加：

```markdown
6. `Workbench/survey-updates.json` — 各 survey 积压的新论文（信息流闭环的消费信号）
7. 用 Glob 列出最近的 `News/YYYY-MM-DD.md`（若目录存在），了解非论文信息源的最新动态线索
```

- [ ] **Step 2: JUDGE 表增加两行**

在 JUDGE 表（"| agenda 中某 direction 缺乏文献支撑..." 所在表）中、literature-survey 两行之后插入：

```markdown
| survey-updates.json 中某 survey pending ≥5 篇，或最老条目 added_at 距今 >7 天 | 读取 `skills/1-literature/survey-refresh/SKILL.md` 并执行 |
| News/ 最新一期超过 config `news.days` 天数（且 Supervisor 未禁用） | 读取 `skills/1-literature/news-digest/SKILL.md` 并执行 |
```

- [ ] **Step 3: 验证**

Run: `grep -n "survey-refresh\|news-digest\|survey-updates" skills/6-orchestration/autoresearch/SKILL.md`
Expected: READ STATE 2 处 + JUDGE 表 2 处命中。

- [ ] **Step 4: Commit**

```bash
git add skills/6-orchestration/autoresearch/SKILL.md
git commit -m "feat(autoresearch): 接线 survey-refresh 与 news-digest 触发信号"
```

---

## Phase 2：LaTeX 写作链

### Task 10: 新 skill related-work

**Files:**
- Create: `skills/4-writing/related-work/SKILL.md`
- Create: `.claude/skills/related-work`（symlink）

- [ ] **Step 1: 写 SKILL.md**

```markdown
---
name: related-work
description: >
  当 Supervisor 给出自己论文的 LaTeX 草稿（.tex）并要求"写 related work""起草相关工作"时，
  基于 Papers/ 已读论文与 Topics/ survey 起草英文 LaTeX Related Work 章节，
  所有 \cite{} 来自 references.bib，evidence-driven 不编造。
argument-hint: "<draft.tex 路径> [topic] [段落数预算，默认 4]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

## Purpose

LaTeX 投稿写作链的成文端。与既有 skill 的分工：
- `latex-citation-enhancer`：保证 references.bib 条目准确（引用身份）。
- `auto-cite`：给**已写好**的草稿逐句补引用（引用位置）。
- 本 skill：从零**起草** Related Work 章节本身（叙事 + 选文 + 成文），输出英文 LaTeX。
- `draft-section`：中文 vault 笔记章节，与本 skill 输出物不同。

## Steps

### Step 1：准备引用基础设施

​```bash
python3 skills/4-writing/latex-citation-enhancer/assign_cite_keys.py
python3 skills/4-writing/latex-citation-enhancer/build_paper_index.py
python3 skills/4-writing/latex-citation-enhancer/fetch_bibtex.py --offline
​```

确保 paper_index.json 最新、每篇有稳定 cite_key。若 Supervisor 的项目有独立 .bib，
询问路径；否则按 latex-citation-enhancer 流程生成/更新 `references.bib`。

### Step 2：理解草稿定位

用 Read 读取 draft.tex，提取：论文的核心贡献 claim、方法关键词、目标 venue 风格线索、
已有的 Related Work 章节或占位符。据此确定本文需要"对比并区隔"的 2-5 条相关工作线。

### Step 3：借 survey 取叙事结构

用 Grep 在 `Topics/*-Survey.md` 中找与 topic 匹配的 survey（frontmatter keywords），
Read 其分类框架与 Key Takeaways。Related Work 的段落划分优先沿用 survey 的成熟分类，
每段结尾回扣"本文与该线工作的区别"。

### Step 4：evidence-driven 选文

对每个段落主题，从 `paper_index.json`（title/tags/summary/key_results）取 5-10 篇候选，
逐篇读 summary 确认**真实支撑**该段叙事后纳入（原则同 auto-cite：关键词重叠 ≠ 支撑）。
每段收敛到 3-6 篇代表作。领域公认必引但库内没有的论文，记入 missing 清单（Step 6），
**不得凭记忆编造引用**。

### Step 5：成文

写出英文 LaTeX Related Work（默认 4 段，按参数调整）：

- 每段：主题句 → 代表工作演进（`\cite{key}` 全部来自 Step 1 的 bib/index）→
  与本文的区隔句。
- 学术英语，时态与 venue 惯例一致（一般现在时为主）。
- 每段后附注释块供 review，格式：
  `% EVIDENCE: <cite_key> ← Papers/<笔记名>（一句话支撑理由）`，Supervisor 确认后删除。

输出方式：draft.tex 中已有 Related Work 节 → 用 Edit 填入/替换（保留原有内容为注释）；
无 → 输出独立 `related_work.tex` 到草稿同目录。

### Step 6：missing citations 清单

在会话中输出库外必引论文清单（标题 + 一句话理由 + 建议的 arXiv 检索词），
建议 Supervisor 先对它们跑 paper-digest 再重跑本 skill 补全。

## Guard

- `\cite{}` 的 key 必须存在于 references.bib / paper_index.json——禁止编造 key 或凭
  训练记忆引用库外论文。
- 每个 cite 必须有 EVIDENCE 注释（可追溯到具体 Papers/ 笔记）。
- 不改动 draft.tex 中 Related Work 以外的任何内容。
- 对 Supervisor 自己论文的贡献陈述不做修改，只写相关工作。

## Verify

- [ ] 产出的所有 `\cite{key}` 均能在 .bib 中 grep 到
- [ ] 每段有与本文的区隔句（"In contrast, ..." / "Unlike ..."）
- [ ] EVIDENCE 注释完整；missing 清单已输出（可为空）
- [ ] LaTeX 可编译（至少无未闭合环境；有条件时跑 pdflatex 冒烟）

## Examples

`/related-work ~/papers/afe/main.tex "agent-facing environment" 4` →
借 Topics/AgentFriendlyEnvironment-Survey 的分类起草 4 段（GUI agents、agent 环境与
benchmark、verifier/reward、runtime affordance），28 个 cite 全部来自 references.bib，
missing 清单 2 篇。
```

（同 Task 8：写入时处理好嵌套代码围栏。）

- [ ] **Step 2: 注册并校验**

```bash
python3 scripts/sync_skills.py --fix && python3 scripts/sync_skills.py
```

Expected: `OK: 20 个 skill 全部已注册`

- [ ] **Step 3: Commit**

```bash
git add skills/4-writing/related-work/ .claude/skills/related-work
git commit -m "feat(skills): related-work——英文 LaTeX Related Work 起草"
```

### Task 11: literature-survey 增加 vault-only 模式

**Files:**
- Modify: `skills/1-literature/literature-survey/SKILL.md`（Step 1 参数表 L15-36、Step 3 L45、Step 6a L108）

- [ ] **Step 1: Step 1 参数表增加一行**

在参数表（topic/year_range/venue_preference/max_papers）后追加：

```markdown
| `scope` | `full` | `full` = 外部搜索 + vault 综合；`vault-only` = 只综合库内已读论文，产出报告到 Reports/（触发词："根据已读论文写个 XX 报告""vault 里关于 XX 的综合"） |
```

- [ ] **Step 2: Step 3 开头加分支**

在 "### Step 3：外部搜索与筛选" 标题下第一行插入：

```markdown
**`scope: vault-only` 时跳过本步与 Step 4**（不做外部搜索、不新增 digest），直接以 Step 2 的库内命中论文进入 Step 5 综合分析。
```

- [ ] **Step 3: Step 6a 输出路径加分支**

在 "#### 6a. 生成 Survey 文件" 小节开头插入：

```markdown
**`scope: vault-only` 时**输出到 `Reports/YYYY-MM-DD-{Topic}-Report.md`（报告性质，不覆盖 Topics/ 下的正式 survey），frontmatter 增加 `scope: vault-only`；以下 survey 文件规则仅适用于 `scope: full`。
```

- [ ] **Step 4: 验证 + Commit**

Run: `grep -n "vault-only" skills/1-literature/literature-survey/SKILL.md`
Expected: 3 处命中。

```bash
git add skills/1-literature/literature-survey/SKILL.md
git commit -m "feat(literature-survey): vault-only 模式——纯库内综合产出报告"
```

---

## Phase 3：News 专栏

### Task 12: fetch_news.py — RSS 抓取打分（零 token）

**Files:**
- Create: `skills/1-literature/news-digest/fetch_news.py`
- Test: `tests/test_fetch_news.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_fetch_news.py
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "1-literature" / "news-digest"))
from fetch_news import parse_feed, score_item

RSS2 = """<?xml version="1.0"?>
<rss version="2.0"><channel><title>Blog</title>
<item><title>New GUI agent benchmark released</title>
<link>https://x.test/a</link>
<description>A benchmark for computer-use agents.</description>
<pubDate>{date}</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Blog</title>
<entry><title>Quantum knitting</title>
<link href="https://x.test/b"/>
<summary>Nothing relevant.</summary>
<updated>{date}</updated></entry>
</feed>"""


def test_parse_rss2_and_atom():
    now = datetime.now(timezone.utc)
    items = parse_feed(RSS2.format(date=now.strftime("%a, %d %b %Y %H:%M:%S +0000")))
    assert items[0]["title"] == "New GUI agent benchmark released"
    assert items[0]["link"] == "https://x.test/a"
    assert items[0]["published"] is not None
    items = parse_feed(ATOM.format(date=now.strftime("%Y-%m-%dT%H:%M:%SZ")))
    assert items[0]["link"] == "https://x.test/b"


def test_score_counts_keyword_hits():
    kws = ["gui agent", "computer-use", "vlm"]
    hit = {"title": "New GUI agent benchmark", "summary": "for computer-use agents"}
    miss = {"title": "Quantum knitting", "summary": "nothing"}
    assert score_item(hit, kws) == 2
    assert score_item(miss, kws) == 0
```

- [ ] **Step 2: 运行确认失败**

Run: `python3 -m pytest tests/test_fetch_news.py -v`
Expected: FAIL（ModuleNotFoundError）

- [ ] **Step 3: 实现（仅标准库）**

```python
#!/usr/bin/env python3
"""按 team-config news.sources 抓取 RSS/Atom，按 interests 关键词打分，输出候选 JSON。

用法: python3 skills/1-literature/news-digest/fetch_news.py \
        [--days 3] [--output Workbench/daily/.news-candidates.json]
type=web 的源不在此抓取（脚本只列出其 URL，由 agent 用 WebFetch/lexmount 处理）。
"""
import argparse
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEAM_CONFIG = ROOT / "Workbench" / "config" / "team-config.json"
UA = {"User-Agent": "ReadPaperMachine-news/1.0"}


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def _parse_date(s: str):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)  # RFC822 (RSS2)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))  # ISO (Atom)
    except ValueError:
        return None


def parse_feed(xml_text: str) -> list[dict]:
    """解析 RSS2 <item> 与 Atom <entry>，返回 {title, link, summary, published}。"""
    root = ET.fromstring(xml_text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for it in root.iter("item"):  # RSS2
        items.append({
            "title": _text(it.find("title")),
            "link": _text(it.find("link")),
            "summary": _text(it.find("description")),
            "published": _parse_date(_text(it.find("pubDate"))),
        })
    for it in root.findall(".//a:entry", ns):  # Atom
        link_el = it.find("a:link", ns)
        items.append({
            "title": _text(it.find("a:title", ns)),
            "link": link_el.get("href", "") if link_el is not None else "",
            "summary": _text(it.find("a:summary", ns)) or _text(it.find("a:content", ns)),
            "published": _parse_date(_text(it.find("a:updated", ns)) or _text(it.find("a:published", ns))),
        })
    return items


def score_item(item: dict, keywords: list[str]) -> int:
    hay = (item.get("title", "") + " " + item.get("summary", "")).lower()
    return sum(1 for kw in keywords if kw.lower() in hay)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--output", default="Workbench/daily/.news-candidates.json")
    args = ap.parse_args()

    cfg = json.loads(TEAM_CONFIG.read_text(encoding="utf-8"))
    news_cfg = cfg.get("news", {})
    days = args.days or news_cfg.get("days", 3)
    keywords = [kw for it in cfg.get("interests", []) for kw in it.get("keywords", [])]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    candidates, web_sources, errors = [], [], []
    for src in news_cfg.get("sources", []):
        if src.get("type") == "web":
            web_sources.append(src)
            continue
        try:
            with urllib.request.urlopen(
                urllib.request.Request(src["url"], headers=UA), timeout=30
            ) as resp:
                items = parse_feed(resp.read().decode("utf-8", errors="replace"))
        except Exception as e:  # 单源失败跳过，不阻塞（spec §9）
            errors.append({"source": src["name"], "error": str(e)})
            continue
        for it in items:
            pub = it.pop("published")
            if pub and pub < cutoff:
                continue
            score = score_item(it, keywords)
            if score >= news_cfg.get("min_score", 1):
                candidates.append({**it, "source": src["name"],
                                   "published": pub.isoformat() if pub else None,
                                   "score": score})

    candidates.sort(key=lambda c: c["score"], reverse=True)
    out = {"fetched_at": datetime.now(timezone.utc).isoformat(),
           "days": days,
           "candidates": candidates[: news_cfg.get("top_n", 20)],
           "web_sources": web_sources,
           "errors": errors}
    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(out['candidates'])} candidates, {len(web_sources)} web sources, {len(errors)} errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 测试通过**

Run: `python3 -m pytest tests/test_fetch_news.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add skills/1-literature/news-digest/fetch_news.py tests/test_fetch_news.py
git commit -m "feat(news): fetch_news.py RSS/Atom 抓取打分（零 token，仅标准库）"
```

### Task 13: 新 skill news-digest + News/ 目录

**Files:**
- Create: `skills/1-literature/news-digest/SKILL.md`
- Create: `News/_index.md`
- Create: `.claude/skills/news-digest`（symlink）

- [ ] **Step 1: 写 SKILL.md**

```markdown
---
name: news-digest
description: >
  当 Supervisor 说"看看最近有什么 AI 新闻""news 总结"，或 autoresearch 检测到
  News/ 超期未更新时，抓取 config 中的博客/新闻/公众号源，按研究兴趣筛选点评，
  产出 News/YYYY-MM-DD.md 并把重要线索回链进 vault。
argument-hint: "[今日 / 过去N天，默认取 config news.days]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
---

## Purpose

非论文信息源（官方博客、技术媒体、公众号）的摄入端，架构与 daily-papers 相同的三段式：
脚本抓取打分（零 token）→ 分流 → 精读点评。产出周报式 News 摘要；真正有信息量的条目
（新工具/重要发布/研究 idea 线索）沉淀为可 wikilink 的小节回链进 survey/agenda，
让网络信息也进入知识复利循环。

## Steps

### Step 0：解析时间范围

"今日" → `--days 1`；"过去N天/一周" → 对应天数；未指定 → 省略参数（用 config news.days）。

### Step 1：抓取打分（零 token）

​```bash
python3 skills/1-literature/news-digest/fetch_news.py --days {DAYS} \
  --output Workbench/daily/.news-candidates.json
​```

Read 输出 JSON：`candidates`（RSS 已打分排序）、`web_sources`（需 agent 抓取的网页源）、
`errors`（失败源）。对每个 web_source 用 WebFetch（或 `scripts/lexmount_fetch.py` fallback，
见 references/network-fetch-fallback.md）抓首页，人工筛出时间范围内的条目并入候选。

### Step 2：分流

扫 title + summary，把候选分为：**精读**（与 interests 强相关、含新方法/新产品/新数据点，
通常 3-8 条）、**一句话带过**（相关但无增量）、**忽略**。

### Step 3：精读并产出

对精读条目用 WebFetch 读原文。产出 `News/YYYY-MM-DD.md`：

​```markdown
---
title: "News {YYYY-MM-DD}"
tags: [news]
date: "{YYYY-MM-DD}"
sources_ok: {N}
sources_failed: [{失败源名}]
---

# News {YYYY-MM-DD}

## 精读

### {条目标题}
- **source**: [{源名}]({url})
- **what**: <发生了什么，2-3 句>
- **so-what**: <对我们研究方向的含义/态度，1-2 句；无关痛痒的不硬写>
- **action**: <无 / 建议 digest 论文 arXiv:xxxx / 关联 [[Topics/...]] 或 [[Ideas/...]]>

## 一句话

- [{标题}]({url}) — <一句话> （source）
​```

### Step 4：回链与记录

1. action 中"建议 digest"的论文：追加 summarize_paper 任务到 `Workbench/queue.json`
   （结构参照队列中现有条目）。
2. 与某 direction 强相关的条目：在 `Workbench/agenda.md` 对应 direction 不做改动，
   仅在当日 log 中提示（agenda 只由 agenda-evolve/Supervisor 改）。
3. 追加当日 log：`### [HH:MM] news-digest — N 精读 / M 一句话 / K 源失败`。

## Guard

- News 条目是线索与观点来源，**不得作为 agenda evidence 的唯一支撑**（非 peer-reviewed）。
- 抓取失败的源跳过并记入 frontmatter `sources_failed` 与当日 log，不阻塞。
- 不直接修改 agenda.md / Topics/（只回链与提示，改动走各自 owner skill）。
- so-what 必须诚实：没有含义就写"与当前方向无直接关联"，不硬编。

## Verify

- [ ] News/YYYY-MM-DD.md 存在且精读条目均有 source/what/so-what/action
- [ ] 建议 digest 的论文已入 queue.json
- [ ] 当日 log 已追加
```

（写入时处理嵌套代码围栏，同 Task 8。）

- [ ] **Step 2: 建 News/_index.md**

```markdown
---
title: News Index
tags: [index, news]
---

# News 专栏

非论文信息源（博客/媒体/公众号）的定期摘要，由 `news-digest` skill 产出。
信息源配置在 `Workbench/config/team-config.json` 的 `news.sources`
（公众号建议经 RSSHub / wechat2rss 转成 RSS 后配入）。

## 期数

（由 news-digest 追加，格式：`- [[News/YYYY-MM-DD]] — 一句话亮点`）
```

并在 news-digest SKILL.md Step 4 的记录项之后确保每期在此追加一行（已含在上文 Step 4 语义中，若遗漏请在 Step 4 补一条"更新 News/_index.md 期数列表"）。

- [ ] **Step 3: 注册、校验、Commit**

```bash
python3 scripts/sync_skills.py --fix && python3 scripts/sync_skills.py
git add skills/1-literature/news-digest/ News/ .claude/skills/news-digest
git commit -m "feat(skills): news-digest——非论文信息源摄入 + News/ 专栏"
```

Expected: `OK: 21 个 skill 全部已注册`

- [ ] **Step 4: 端到端冒烟（需网络，失败不阻塞本 task）**

```bash
python3 skills/1-literature/news-digest/fetch_news.py --days 7
head -30 Workbench/daily/.news-candidates.json
```

Expected: 输出 `N candidates, 1 web sources, K errors`；JSON 有内容。网络不可用时记录到当日 log，跳过。

---

## Phase 4：可 clone 模板化

### Task 14: scripts/init.sh — 初始化向导

**Files:**
- Create: `scripts/init.sh`（chmod +x）

- [ ] **Step 1: 写脚本**

```bash
#!/usr/bin/env bash
# ReadPaperMachine 初始化向导。
#   scripts/init.sh            交互设置研究兴趣（写 team-config.json + agenda Mission 骨架）
#   scripts/init.sh --fresh    先清空示例个人数据再进入向导
#   --yes                      非交互（--fresh 不再确认；向导用占位默认值，供测试）
set -euo pipefail
cd "$(dirname "$0")/.."

FRESH=0; YES=0
for arg in "$@"; do
  case "$arg" in
    --fresh) FRESH=1 ;;
    --yes) YES=1 ;;
    *) echo "unknown arg: $arg"; exit 2 ;;
  esac
done

if [ "$FRESH" = 1 ]; then
  echo "将清空个人数据: Papers/ Topics/ Ideas/ Reports/ Meetings/ Experiments/ News/ Projects/ 及 Workbench 状态"
  echo "框架保留: skills/ references/ Templates/ docs/ scripts/ .claude/ CLAUDE.md"
  if [ "$YES" != 1 ]; then
    read -r -p "确认？建议先 git commit 当前状态 [y/N] " ok
    [ "$ok" = "y" ] || { echo "已取消"; exit 1; }
  fi
  for d in Papers Topics Ideas Reports Meetings Experiments News Projects DomainMaps; do
    [ -d "$d" ] && find "$d" -mindepth 1 -not -name "_index.md" -delete
    mkdir -p "$d"
    [ -f "$d/_index.md" ] || printf -- '---\ntitle: %s Index\ntags: [index]\n---\n\n# %s\n' "$d" "$d" > "$d/_index.md"
  done
  rm -rf Workbench/logs Workbench/daily Workbench/evolution Workbench/backfill
  mkdir -p Workbench/logs Workbench/daily Workbench/memory Workbench/config
  printf '{\n  "queue": [],\n  "version": 2,\n  "updated_at": "%s",\n  "settings": {}\n}\n' "$(date +%F)" > Workbench/queue.json
  rm -f Workbench/survey-updates.json Workbench/redigest-manifest.md
  : > Workbench/memory/insights.md; : > Workbench/memory/patterns.md
  echo "个人数据已清空。"
fi

if [ "$YES" = 1 ]; then
  DIRECTIONS="My Research Topic"; KEYWORDS="my topic, my method"
else
  read -r -p "研究方向（逗号分隔，如: GUI Agent, VLM）: " DIRECTIONS
  read -r -p "打分关键词（逗号分隔，如: gui agent, computer use, vlm）: " KEYWORDS
fi

python3 - "$DIRECTIONS" "$KEYWORDS" "$FRESH" <<'EOF'
import json, sys, datetime
from pathlib import Path
directions = [d.strip() for d in sys.argv[1].split(",") if d.strip()]
keywords = [k.strip() for k in sys.argv[2].split(",") if k.strip()]
cfg_path = Path("Workbench/config/team-config.json")
cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
cfg["interests"] = [{"name": d, "keywords": keywords} for d in directions] or cfg.get("interests", [])
cfg.setdefault("news", {"sources": [], "days": 3, "min_score": 1, "top_n": 20})
cfg_path.parent.mkdir(parents=True, exist_ok=True)
cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

agenda = Path("Workbench/agenda.md")
if not agenda.exists() or sys.argv[3] == "1" or not agenda.read_text().strip():
    today = datetime.date.today().isoformat()
    agenda.write_text(f'''---
last_updated: "{today}"
updated_by: init
---

## Mission

（用 1-3 句描述长期研究目标；方向: {", ".join(directions)}）

---

## Active Directions

（由 agenda-evolve / Supervisor 逐步填充）

## Paused Directions

（暂无）

## Discussion Topics

（暂无）
''')
print("team-config.json / agenda.md 已就绪")
EOF

python3 scripts/sync_skills.py || true
echo "完成。下一步: 在 Claude Code 中运行 /daily-papers 或 /autoresearch"
```

- [ ] **Step 2: 语法检查 + 非破坏测试**

```bash
chmod +x scripts/init.sh && bash -n scripts/init.sh && echo SYNTAX-OK
```

Expected: SYNTAX-OK

- [ ] **Step 3: 在临时 clone 中全流程测试（不碰真实 vault）**

```bash
TMP=$(mktemp -d) && git clone -q . "$TMP/rpm" && cd "$TMP/rpm" \
  && bash scripts/init.sh --fresh --yes \
  && ls Papers/ && python3 -m json.tool Workbench/config/team-config.json > /dev/null \
  && grep -q "My Research Topic" Workbench/config/team-config.json && echo E2E-OK; \
cd - && rm -rf "$TMP"
```

Expected: `Papers/` 只剩 `_index.md`；输出 E2E-OK。

- [ ] **Step 4: Commit**

```bash
git add scripts/init.sh
git commit -m "feat(scripts): init.sh 初始化向导（--fresh 一键模板化）"
```

### Task 15: README quick-start + SPEC.md 收尾更新

**Files:**
- Modify: `README.md`（新增/更新 Quick Start 小节）
- Modify: `docs/SPEC.md`（目录结构、Skill List、DomainMaps 写入权、Last updated）

- [ ] **Step 1: README 增加 Quick Start**

在 README 开头部分（先 Read 现有内容找合适位置）加入：

```markdown
## Quick Start（把它变成你自己的 research assistant）

​```bash
git clone <this-repo> && cd ReadPaperMachine
bash scripts/init.sh --fresh   # 清空示例数据，向导设置你的研究方向与关键词
​```

然后在 Claude Code 中：
- `/daily-papers` — 抓取并锐评最新论文
- `/paper-digest <arXiv URL>` — 消化一篇论文
- `/autoresearch` — 自主研究循环（读论文 → 迭代 survey → 生成 idea）
- `/news-digest` — 非论文信息源摘要（先在 `Workbench/config/team-config.json` 配 `news.sources`）
- `/related-work <draft.tex>` / `/auto-cite <draft.tex>` — LaTeX 写作链

个性化只需改一个文件：`Workbench/config/team-config.json`（interests + news.sources）。
不跑 `--fresh` 则保留本库 700+ 篇笔记作为参考示例。
```

（Quick Start 中仅 `git clone ... init.sh --fresh` 两行是 bash 代码块，其余为普通 markdown 列表。）

- [ ] **Step 2: SPEC.md 更新四处**

1. `Last updated` 改为实施当天日期。
2. 目录结构图：`Reports/` 行后加 `├── News/               # 非论文信息源摘要（news-digest 产出）`；`Workbench/` 下加 `│   ├── survey-updates.json  # digest→survey 记账`。
3. Skill List 表：`1-literature` 组加 `survey-refresh`（digest 积压增量并入 survey + 刷新 DomainMap）与 `news-digest`（非论文信息源摘要）；`4-writing` 组加 `related-work`（英文 LaTeX Related Work 起草）——先 Read 该表确认现有格式再插入。
4. DomainMaps 目录注释改为：`# 核心认知地图（survey-refresh 自动维护"近期格局变化"；结构性内容经 queue Review 由 Human 晋升）`。

- [ ] **Step 3: 全量回归 + Commit**

```bash
python3 -m pytest tests/ -v && python3 scripts/sync_skills.py
git add README.md docs/SPEC.md
git commit -m "docs: README quick-start 与 SPEC 同步升级后的系统结构"
```

Expected: 测试全绿；`OK: 21 个 skill 全部已注册`。

---

## 验收总表（对应 spec §10）

| Spec 验收项 | 覆盖 Task |
|---|---|
| `/auto-cite` 可触发；sync-skills 全绿 | Task 1, 2 |
| daily-papers 从 config 读关键词 | Task 3, 4 |
| digest → 记账 → survey-refresh → survey/DomainMap 更新 | Task 5, 6, 7, 8 |
| autoresearch 自动触发 | Task 9 |
| related-work 产出可编译 LaTeX；vault-only 报告 | Task 10, 11 |
| News 一期跑通 | Task 12, 13 |
| 临时 clone + init --fresh 后可用 | Task 14, 15 |
