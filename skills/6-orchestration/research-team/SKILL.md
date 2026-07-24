---
name: research-team
description: >
  多 Agent 协作构建知识库。当需要持续采集论文、生成笔记、构建 survey/report 时启动。
  派发分工明确的 agents：Collector → Digest/Source-Verify → Judge → Gap Pass → Survey/Report
argument-hint: "[task: collect/digest/survey/all] [topic]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent
---

## Purpose

research-team 是一个多 Agent 协作系统，用于持续构建科研知识库。它派发多个并行 agent：
- **Paper Collector**：自动采集论文填充 queue
- **Paper Digest Preparer**：并行读取论文，返回不写共享状态的 artifact envelope
- **Source Verifier**：独立核查数字、比较、novelty、license/code 与 benchmark setting
- **Coordinator / Judge**：串行 commit，裁决分歧，维护 run manifest
- **Deep Gap Reviewer**：只针对已验证 claim graph 的缺口做 bounded search
- **Survey Generator**：跨已核查笔记生成 survey
- **Report Generator**：生成阶段性报告

角色分离是正确性约束，不只是模型路由：Finder/Digest 不得验证自己的 claim；并行 workers 不得直接写 queue、日志、BibTeX cache、survey-updates 或同一 survey。

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
5. `Workbench/runs/` — 是否有同 topic 的 partial run；有则从最近 checkpoint 恢复，不重复已完成 stage
6. `Workbench/config/team-config.json` — role policy、并发、checkpoint、预算与 fallback

生成/恢复 `run_id`，严格遵循 `references/research-run-protocol.md`；在 manifest 记录 task/topic、stage、budget、agents dispatched、prepared/committed/verified/disputed/failed、token/time（运行时可得时）、checkpoint 与 final status。

### Step 3：按 Stage 派发 Agent Teams

根据任务类型派发并行 agent：

#### Stage A: Paper Collector（低成本、只读发现）

```
派发 Agent 运行 `daily-papers --days 3 --collect-only --run-id <parent-run-id>`：
- 输出：候选、稳定 source identity、分流与要精读 IDs
- Collector 只返回候选与 source identity；由 coordinator 串行更新 Workbench/queue.json
```

#### Stage B: Paper Digest Preparer（并行、零共享写入）

```
对 queue 中 status: pending 的论文，并行派发 digest agent：
- 每篇论文一个 agent
- 执行 `paper-digest <source> --prepare-only`
- paper-digest 内部派发不同 agent 做 source verification
- 输出 artifact envelope：完整 note、proposed path、source identity、claim ledger、verification status
- 禁止直接写 Papers、queue、日志、BibTeX cache、survey-updates
```

按 `digest.prepare_parallel_limit` bounded parallel，并把 nested verifier 计入 global `digest.parallel_limit`；默认 prepare=2 / global=4，给 verifier 与 coordinator 留槽位。按 `orchestration.checkpoint_every` 分批，每批完成即更新 manifest。

#### Stage C: Coordinator Commit + Judge（单写者）

Coordinator 逐个处理 artifact：

1. 重新做 arXiv/DOI/title 去重。
2. 串行执行 paper-digest Step 5-6 commit contract。
3. `unsupported` / `contradicted` claim 已从强结论移除；高影响分歧仍 unresolved 时标 `needs-human`。
4. 只有 artifact 安全落库后才把 queue task 标 `done`。
5. 每批 commit 后更新 manifest；单篇失败不回滚已成功 artifact。

#### Stage D: Deep Gap Reviewer（Full flow only）

在已验证 claim graph 上定位缺 primary source、单一支持、缺反例、关键 comparator 缺失或 benchmark setting 不可比的 gap。最多 3 个 targeted query、1 个回环；新论文仍须回到 Stage B/C。该阶段用于补洞，不重新进行无界 discovery。

#### Stage E: Survey Generator（Foreground）

```
有足够已 commit + source-checked 的论文后，派发 Survey agent：
- 指定 topic（从 agenda 或参数获取）
- 执行 `literature-survey <topic> --run-id <parent-run-id> --resume-stage synthesize`；复用 Stage A-D artifacts，禁止重复 discovery/digest/gap pass
- 输出：Topics/{Topic}-Survey.md
```

若部分论文失败但已满足 synthesis minimum，生成带 evidence boundary 的 partial survey；不得因为尾部 agent 超时而整轮无产物。

#### Stage F: Report Generator（Optional）

```
每周或按需执行：
- 读取 Workbench/memory/ 和近期 daily 总结
- 执行 draft-section skill
- 输出：Reports/YYYY-MM-DD-Progress.md
```

### Step 4：COORDINATE

协调原则：

- 只并行无共享写入的读取、提取与 reviewer 工作。
- queue、Papers commit、日志、BibTeX、survey-updates、survey/DomainMap 均由 coordinator 串行写。
- 每个 stage 和每 `checkpoint_every` 个 artifact 更新 manifest。
- 达到 token/time/paper budget 时停止派发新工作，完成当前安全 commit，并生成 partial synthesis + unresolved gaps。
- 外部 CLI/model 出现 usage limit 时按 role policy fallback；所有 fallback 都失败则 defer 对应 artifact，不拖死全局。

### Step 5：LOG

追加到 `Workbench/logs/YYYY-MM-DD.md`：

```markdown
### [HH:MM] research-team
- **task**: {task 类型}
- **teams_dispatched**: Collector={N agents}, Digest={N agents}, Survey={1 agent}
- **papers_collected**: {数量}
- **papers_digested**: prepared N / committed N / failed N
- **verification**: source-verified claims N / downgraded N / disputed N
- **budget**: token/time/paper budget 使用情况（运行时可得项）
- **run_id**: <run_id>（completed/partial）
- **survey_generated**: {文件名或"pending"}
- **status**: completed/partial
```

## Guard

- **并行限制**：global `digest.parallel_limit` 默认 4，prepare/reviewer 默认各 2；nested verifier 计入 global limit。绝不无界派发，并行 workers 必须 prepare-only。
- **单写者**：所有共享状态只能由 coordinator 串行 commit；禁止 Digest/Verifier 直接写共享文件。
- **角色独立**：Finder/Digest 与 Verifier 必须是不同 agent；Verifier 不接收 Finder reasoning/rating。
- **优先级**：Survey 在 verified coverage 达到 synthesis minimum 后启动；不要求所有低优先级论文成功。
- **去重**：Collector 需检查 queue 中是否已有相同论文（arxiv_id）
- **超时**：单个 worker 超时按 fallback/retry policy；最终 defer/failed 记录在 manifest，不阻塞已完成结果。
- **验证语义**：source-verified 仅表示 primary source 一致，不代表独立复现。
- **Reject claim, not paper**：错误 claim 被删除/降级，paper 仍可保留其可靠贡献；只有整篇不可获取或明显越界时跳过 paper。

## Verify

- [ ] queue 有新论文（collect task）
- [ ] 新笔记已创建（digest task）
- [ ] Digest workers 全部 prepare-only；共享写入由 coordinator 串行完成
- [ ] 高风险 claim 有独立 verifier、locator 与状态；Finder 未自证
- [ ] run manifest 含 stage/checkpoint/budget/verification/failed，partial run 可恢复
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
3. Digest preparers 按配置 bounded parallel，返回 15 个 artifact；coordinator 串行 commit
4. Source verifier / Judge 降级 unsupported claims，gap reviewer 只补验证后缺口
5. Survey agent 基于已 source-check 的新笔记 + 已有证据生成 GUI Agent Survey
6. 输出：Topics/CUA-Survey.md

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
    "parallel_limit": 4,
    "prepare_parallel_limit": 2,
    "review_parallel_limit": 2,
    "timeout_minutes": 12
  },
  "orchestration": {
    "checkpoint_every": 3,
    "max_papers_per_run": 20,
    "post_verification_queries": 3
  },
  "model_policy": {
    "finder": {"tier": "cheap-fast"},
    "digest": {"tier": "balanced"},
    "verifier": {"tier": "strong", "require_different_agent": true},
    "judge": {"tier": "strongest-available", "trigger": "disputed-high-impact-only"},
    "synthesis": {"tier": "strong"}
  },
  "survey": {
    "min_papers": 20,
    "output_dir": "Topics/"
  }
}
```
