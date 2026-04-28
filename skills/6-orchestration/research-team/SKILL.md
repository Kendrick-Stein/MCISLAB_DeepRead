---
name: research-team
description: >
  多 Agent 协作构建知识库。当需要持续采集论文、生成笔记、构建 survey/report 时启动。
  派发多个并行 agent：Paper Collector → Paper Digest → Survey/Report Generator
argument-hint: "[task: collect/digest/survey/all] [topic]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent
---

## Purpose

research-team 是一个多 Agent 协作系统，用于持续构建科研知识库。它派发多个并行 agent：
- **Paper Collector**：自动采集论文填充 queue
- **Paper Digest**：消化 queue 中的论文生成笔记
- **Survey Generator**：跨笔记生成 survey
- **Report Generator**：生成阶段性报告

## Steps

### Step 1：解析任务类型

从 `task` 参数解析任务：
- `collect` — 仅采集论文
- `digest` — 仅消化现有 queue
- `survey` — 仅生成 survey（基于已有笔记）
- `all` — 全流程（采集 + 消化 + survey）

若未指定，默认 `all`。

### Step 2：READ STATE

读取当前状态：
1. `Workbench/queue.json` — 待处理队列
2. `Workbench/agenda.md` — 当前研究方向
3. `Workbench/memory/` — 近期 insight/pattern
4. `Papers/` 目录 — 已有笔记数量（用 Glob 统计）

### Step 3：派发 Agent Teams

根据任务类型派发并行 agent：

#### Team A: Paper Collector（Background）

```
派发 Agent 运行 daily-papers skill：
- 参数：--days 3（过去 3 天）
- 输出：更新 Workbench/daily/.candidates.json
- 同时更新 Workbench/queue.json（新增 summarize_paper 任务）
```

#### Team B: Paper Digest（Background）

```
对 queue 中 status: pending 的论文，并行派发 digest agent：
- 每篇论文一个 agent
- 执行 paper-digest skill
- 输出：Papers/YYMM-ShortTitle.md
- 完成后更新 queue 中对应任务为 completed
```

#### Team C: Survey Generator（Foreground）

```
等 Team B 完成后，派发 Survey agent：
- 指定 topic（从 agenda 或参数获取）
- 执行 literature-survey skill
- 输出：Topics/{Topic}-Survey.md
```

#### Team D: Report Generator（Optional）

```
每周或按需执行：
- 读取 Workbench/memory/ 和近期 daily 总结
- 执行 draft-section skill
- 输出：Reports/YYYY-MM-DD-Progress.md
```

### Step 4：COORDINATE

等待所有 background agent 完成：
- 用 ScheduleWakeup 或轮询检查状态
- 记录每个 team 的完成情况到日志

### Step 5：LOG

追加到 `Workbench/logs/YYYY-MM-DD.md`：

```markdown
### [HH:MM] research-team
- **task**: {task 类型}
- **teams_dispatched**: Collector={N agents}, Digest={N agents}, Survey={1 agent}
- **papers_collected**: {数量}
- **papers_digested**: {数量}
- **survey_generated**: {文件名或"pending"}
- **status**: completed/partial
```

## Guard

- **并行限制**：Digest team 最多同时 10 个 agent（避免 API rate limit）
- **优先级**：Survey agent 在 Digest 完成后才启动
- **去重**：Collector 需检查 queue 中是否已有相同论文（arxiv_id）
- **超时**：单个 Digest agent 超时 5 分钟则标记 failed

## Verify

- [ ] queue 有新论文（collect task）
- [ ] 新笔记已创建（digest task）
- [ ] Survey 文件存在且非空（survey task）
- [ ] 日志已追加

## Examples

**示例：全流程构建 GUI Agent 知识库**

```
/research-team all GUI Agent
```

执行过程：
1. Collector 抓取过去 3 天 GUI Agent 相关论文（HF Daily + arXiv）
2. 更新 queue（新增 15 篇）
3. Digest team 并行消化（10 agent 同时，共 15 篇）
4. Survey agent 基于 15 篇新笔记 + 已有 50 篇笔记生成 GUI Agent Survey
5. 输出：Topics/GUIAgent-Survey.md

---

## Agent Team 配置

可在 `Workbench/config/team-config.json` 配置：

```json
{
  "collector": {
    "sources": ["hf-daily", "arxiv"],
    "keywords": ["GUI agent", "VLM", "agentic RL"],
    "days": 3
  },
  "digest": {
    "parallel_limit": 10,
    "timeout_minutes": 5
  },
  "survey": {
    "min_papers": 20,
    "output_dir": "Topics/"
  }
}
```