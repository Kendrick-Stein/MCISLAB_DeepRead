---
name: memory-distill
description: >
  当积累了多天工作日志、或 Supervisor 说"整理记忆""蒸馏"时，从日志中提取 pattern 和 insight 到记忆库。也可被 autoresearch 在合适时机自动调用
argument-hint: "[period]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Purpose

memory-distill 是 MindFlow 记忆演化体系的基础技能。它定期扫描 `Workbench/logs/` 中的原始工作日志，从中提取跨日期重复出现的 pattern 和意外发现，并将有价值的 observation 提升为结构化的记忆条目，写入 `Workbench/memory/patterns.md` 和 `Workbench/memory/insights.md`。

该技能实现了 `references/memory-protocol.md` 中定义的 Insight Promotion Hierarchy 的底层两级跃迁：从 Level 0（Raw Log）提升至 Level 1（Pattern），再进一步触发 Level 1 → Level 2（Provisional Insight）和 Level 2 → Level 3（Validated Insight）的升级。它将"散落的日常观察"转化为"可复用的研究经验"，是 MindFlow 自我进化机制的核心入口。

输入为时间范围内的日志文件（`Workbench/logs/YYYY-MM-DD.md`），输出为更新后的记忆文件和 changelog 条目。

## Steps

### Step 1：收集日志

1. 解析 `period` 参数，确定起止日期。若未提供，默认为今天往前 7 天（含今天）。
2. 用 Glob 列出 `Workbench/logs/YYYY-MM-DD.md` 格式的所有日志文件。
3. 根据文件名中的日期过滤，保留落在 `period` 范围内的文件。
4. 用 Read 逐一读取全部匹配的日志文件，记录每个文件的日期和内容。
5. 若范围内无任何日志文件，输出提示"指定时间段内无日志，跳过蒸馏"，终止执行。

### Step 2：提取候选 Pattern

通读所有收集到的日志内容，重点扫描每条 log entry 的 `observation` 字段及其他叙述性文字，寻找以下三类候选 pattern：

1. **跨日期重复观察**：同一现象、规律或结论在两个或更多不同日期的日志中均有提及。即使措辞不同，只要语义相似，均视为同一 pattern 的多次出现。
2. **意外发现（anomaly）**：某个结果或行为与 `DomainMaps/` 中记录的已有知识相悖，或日志中明确标注为"出乎意料"、"与预期不符"的观察。
3. **关联线索（correlation clue）**：日志中提示两篇论文、两个实验或两个概念之间存在潜在联系，且该联系尚未在任何记忆文件中被明确记录。

对每个候选 pattern，记录：
- 核心 observation 的一句话概括
- 来源日志文件列表（`Workbench/logs/YYYY-MM-DD.md`）
- 日志指向的**真实 evidence objects**：Paper note、原始论文 arXiv/DOI、Experiment、Dataset、代码 commit 等
- 每个 evidence object 的 canonical `source_id`，格式优先为 `paper:arxiv:<id>`、`paper:doi:<doi>`、`experiment:<path>`、`dataset:<name>:<version>`、`code:<repo>@<commit>`

日志只是 discovery/audit pointer，不是独立学术证据。若 observation 无法解析到真实 evidence object，可记录为低置信度 pattern，但不得用于 insight 晋升。

### Step 3：检查已有记忆

1. 用 Read 读取 `Workbench/memory/patterns.md`，逐条对比 Step 2 提取的候选 pattern 与已记录条目的语义相似度。判断每个候选是：
   - **全新 pattern**：记忆库中无对应条目
   - **已有 pattern 的新证据**：与某条已有 pattern 高度相似，新日志提供了额外的 occurrence

2. 用 Read 读取 `Workbench/memory/insights.md`，检查是否存在与候选 pattern 相关的 `provisional` insight。若有，候选的新证据将用于支持该 insight 的升级。

比较“新证据”时按 canonical `source_id` 去重，而不是按日志日期或 agent run 去重。同一论文的 arXiv/会议版、同一实验的多条日志、同一数据集上的重复摘要只算一个 source。

### Step 4：更新记忆

根据 Step 3 的分类结果，分三种情况处理：

**情况 A：全新 pattern**

用 Edit 将以下格式的条目 append 到 `Workbench/memory/patterns.md` 末尾：

```markdown
### [YYYY-MM-DD] <Pattern 描述>

- **observation**: <一句话描述跨源观察到的规律或现象>
- **occurrences**: [[Workbench/logs/YYYY-MM-DD]], [[Workbench/logs/YYYY-MM-DD]], ...
- **evidence**: [[Papers/YYMM-Name]], [[Experiments/YYYY-MM-DD-Name]], ...
- **source_ids**: paper:arxiv:xxxx.xxxxx, experiment:Experiments/...
- **confidence**: low
- **needs_verification**: yes
```

日期填写今天（执行蒸馏的日期）。

若全新 pattern 在本轮已经解析到 ≥2 个 unique source_ids，不必等待下一次蒸馏：立即按情况 B 创建 provisional insight；若同时达到 ≥3 且通过情况 C 的 verification/contradiction quality gate，可在同轮继续晋升 validated，并完整记录 status_history。

**情况 B：已有 pattern 获得新证据**

1. 用 Read 再次确认目标 pattern 条目的当前 `occurrences` 列表。
2. 用 Edit 在该条目的 `occurrences` 行末 append 新日志 pointer，并在 `evidence` / `source_ids` 追加去重后的真实来源。
3. 统计 unique canonical `source_ids`：
   - 若独立 source_ids **< 2**：仅更新，不晋升。
   - 若独立 source_ids **≥ 2**：触发 L1 → L2 晋升。不同日志日期本身不增加 source count。

   晋升时：
   - 用 Edit 在该 pattern 条目的 `needs_verification` 行后追加一行：`- **status**: → promoted to insight ([YYYY-MM-DD])`
   - 用 Edit 将以下格式的条目 append 到 `Workbench/memory/insights.md` 末尾：

     ```markdown
     ### [YYYY-MM-DD] <Insight 标题（与 pattern 描述一致）>

     - **claim**: <从 pattern observation 提炼的可证伪的一句话断言>
     - **evidence**: [[Papers/...]], [[Experiments/...]], ...
     - **source_ids**: paper:arxiv:..., experiment:...
     - **audit_logs**: [[Workbench/logs/YYYY-MM-DD]], [[Workbench/logs/YYYY-MM-DD]], ...
     - **confidence**: low
     - **source**: cross-validation
     - **impact**: <该 insight 可能影响的研究方向，若暂不明确可填"待评估">
     - **status**: provisional
     - **status_history**: [YYYY-MM-DD] created provisional from <N> canonical sources
     ```

**情况 C：已有 provisional insight 获得新证据**

1. 用 Read 确认目标 insight 条目当前的 `evidence` 列表和 `confidence`。
2. 用 Edit 在该 insight 的 `evidence` / `source_ids` 追加去重后的真实来源；日志只追加到 `audit_logs`。
3. 统计 unique canonical `source_ids` 与证据质量：
   - 若独立 source_ids **< 3**：保持 `status: provisional`。
   - 若独立 source_ids **≥ 3**，且支撑 claim 的 Paper claim row 为 `source-verified`（或 Experiment 有完整结果记录），并且无未解决反例：触发 L2 → L3，设 `status: validated`、`confidence: medium`，并追加 dated `status_history`。
   - `confidence: high` 不能仅靠数量获得；还需要至少一个独立复现/受控实验，或两个方法与数据设置显著独立的直接证据，并显式记录 contradiction audit。

`source-verified` 只说明 primary source 包含该 claim，不等于复现。`partial` Paper 只有对应 source-verified claim row 可计数；`unverified` / legacy note 不能把 insight 晋升到 validated。

   若晋升后 `status: validated` 且 `confidence: high`，用 queue helper 创建 Human review；不得直接修改 DomainMap：

   ```bash
   python3 skills/1-literature/daily-papers/queue_ops.py enqueue-review \
     --insight-ref "Workbench/memory/insights.md#<heading>" \
     --claim "<insight claim>" \
     --suggested-map "DomainMaps/<Name>.md"
   ```

### Step 5：记录变更

用 Edit 将以下格式的条目 append 到 `Workbench/evolution/changelog.md` 末尾（若文件不存在，先用 Write 创建并加一级标题 `# Evolution Changelog`）：

```markdown
### [YYYY-MM-DD] memory-distill

- **period**: <YYYY-MM-DD ~ YYYY-MM-DD>
- **logs_processed**: <数量>
- **new_patterns**: <数量>
- **promoted_to_insight**: <数量>（L1 → L2）
- **validated_insights**: <数量>（L2 → L3）
- **queued_for_review**: <数量>（L3 → L4 候选）
```

## Guard

- **保留历史、受控更新**：不得删除或改写既有 claim/observation/evidence；允许对 `status`、`confidence`、`evidence`、`source_ids`、`audit_logs` 做本协议规定的更新。每次晋升同时追加 dated `status_history`，使旧状态可审计。
- **不直接修改 DomainMaps**：memory-distill 无权写入 `DomainMaps/`；高置信 validated insight 只能通过 `Workbench/queue.json` 的 `review_insight` 任务请求 Human 晋升。
- **日志不是证据**：`occurrences` / `audit_logs` 用于审计流程；真正支撑 claim 的对象必须写在 `evidence` + `source_ids`，并能解析到 Paper/Experiment/Dataset/Code。
- **不捏造 pattern**：只有在日志中确实出现的 observation 才能被提取为候选 pattern，不得基于推断或联想凭空生成。若某规律听起来合理但日志中找不到明确依据，不记录。
- **晋升需引用具体证据**：晋升时必须列出所有 canonical source_ids、对应 wikilink 与 verification boundary；只有日志链接不得晋升。
- **独立来源的判断**：按 canonical source identity 而非日期/agent/run；同一论文不同版本、同一实验多次记录、同一来源的二手转述都只算一个。
- **高置信度需强证据**：source count 本身不能产生 high confidence；必须有复现/受控实验或足够独立的直接证据，并完成 contradiction audit。

## Verify

- [ ] `Workbench/evolution/changelog.md` 已追加本次蒸馏记录
- [ ] 蒸馏结果已记录（新增 pattern 数 + 晋升 insight 数，允许为 0 但须明确记录）
- [ ] 所有晋升均按 unique source_ids 计数；日志日期没有被当作独立 evidence
- [ ] DomainMap 晋升候选已写入 queue.json 的 review_insight task，未使用 legacy Markdown queue

## Examples

**示例：指定时间段蒸馏**

```
/memory-distill --period "2026-03-20 ~ 2026-03-26"
```

执行过程：

1. 解析 period，确定范围为 2026-03-20 至 2026-03-26
2. Glob `Workbench/logs/` 找到 `2026-03-20.md`、`2026-03-22.md`、`2026-03-24.md`、`2026-03-26.md` 共 4 个文件，逐一读取
3. 扫描 observation 字段，发现：
   - "reward shaping 在 sparse-reward 环境中显著提升收敛速度" 在两个日志出现，但都指向同一篇论文 → 1 个 source_id，只记录 pattern，不晋升
   - "基于 diffusion 的策略对 action chunk size 高度敏感" 指向两篇不同论文与一个受控实验 → 3 个 source_ids，可进入 provisional/validated 判断
   - "cross-attention 替代 concatenation 更有效" 的新日志仍指向 patterns.md 已记录的同一实验 → 只是新 audit pointer，不增加独立 evidence
4. 读取 patterns.md：按 arXiv/DOI/experiment path 归一化 source_ids；不按 occurrences 或日期计数
5. 读取 insights.md：无与新候选直接相关的 provisional insight
6. 写入：
   - patterns.md 新增 2 条 pattern（reward shaping、diffusion chunk size）
   - patterns.md 中 cross-attention pattern 只更新 audit_logs，不晋升
   - diffusion chunk size pattern 以 3 个独立 source_ids 晋升；若证据质量满足且无反例，可标 validated/medium
7. 追加 changelog 条目

最终输出摘要：

```
memory-distill 完成（2026-03-20 ~ 2026-03-26）
- 处理日志：4 个文件
- patterns.md 新增 2 条 pattern
- insights.md 中 1 条 insight 基于 3 个 canonical source_ids 完成晋升；重复日志未计为新证据
- changelog 已更新
```
