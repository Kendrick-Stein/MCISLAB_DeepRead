---
name: daily-papers
description: 每日论文总结。抓取 HuggingFace Daily/Trending + arXiv + venue 源（OpenAlex 期刊 IJCV/TNNLS/TPAMI、CVF 顶会 CVPR/ICCV/WACV）最新论文，按研究方向打分筛选， 生成论文笔记后基于深度阅读写出有态度的总结锐评。 触发词："今日论文总结""过去3天论文总结""过去一周论文总结""看看最近有什么论文"
argument-hint: "[今日 / 过去N天 / 过去一周] [--collect-only --run-id <parent>]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

## Purpose

自动发现与研究方向相关的最新论文，生成候选列表。分三步：

1. **Python 脚本**抓取 + 打分（零 token）
2. **快速分流** → 确定必读论文
3. **每篇必读论文**：Digest preparer 生成已 source-check 的 draft → coordinator 串行 commit → 独立 reviewer 基于笔记写点评 → 主 agent 汇总

> **关键设计**：Finder / Digest / Reviewer 分离。Reviewer 只接收已落库笔记及其 Evidence Ledger，不接收 digest agent 的推理过程；context 节省通过 `paper-digest --prepare-only` 的紧凑 artifact envelope 和 bounded batch 实现，不以作者自审替代独立判断。

## Steps

### Step 0：解析时间范围

从用户输入中解析天数：
- "今日论文总结"、"今日论文"、"每日总结" → 当天（`--days 1`）
- "过去3天"、"最近三天" → `--days 3`
- "过去一周"、"最近7天" → `--days 7`
- "过去两周" → `--days 14`
- 无特殊指定 → 默认当天

将解析出的天数存为 `DAYS` 变量。

`--collect-only` 供 `research-team` Collector 使用：接收 parent `run_id`，执行抓取、去重、分流后返回候选与“要精读”IDs；不更新 queue、不创建嵌套 manifest、不派发 digest/reviewer、不写 daily summary/log。Parent coordinator 负责 checkpoint 与后续串行 enqueue。

普通模式生成本次 `run_id`（如 `daily-20260723-0930`），按 `references/research-run-protocol.md` 创建或更新 `Workbench/runs/{run_id}.json`。每完成一个 stage 或一批 commit 就原子更新；即使后续失败，也必须保留可读的 partial state。

### Step 1：抓取 + 打分（Python 脚本，零 token）

运行 `fetch_and_score.py`，输出到 `Workbench/daily/.candidates.json`：

```bash
python3 skills/1-literature/daily-papers/fetch_and_score.py \
  --days {DAYS} \
  --output Workbench/daily/.candidates.json
```

脚本抓取四类源（均零 token，纯 stdlib，配置见 `config.json`）：

- **HuggingFace Daily/Trending** + **arXiv**：每日预印本主力，`source` 为 `hf-daily`/`hf-trending`/`arxiv`。
- **OpenAlex 期刊**（`openalex_venues`，按 ISSN）：IJCV/TNNLS/TPAMI 等，`source` 为 `openalex:{Venue}`。期刊出得稀疏，故用独立的 `openalex_lookback_days` 窗口（默认 60 天）而非 `--days`；许多 IEEE/Springer 论文在 OpenAlex 中**无摘要**，此时退化为 title-only 打分，仅标题命中关键词者入选。由于 title 打分（3-7）远低于 HF 高赞（9999）/ CVF（9），会被挤出 top_n，故用 `reserve_per_source`（默认 openalex:5）**保底名额**——保证每次纳入若干篇过 min_score 的期刊论文。
- **CVF 顶会**（`cvf_proceedings`）：CVPR/ICCV/WACV 论文集，`source` 为 `cvf:{Proc}`，携带 `pdf_url`（免费全文，供 paper-digest 读正文）。listing 页无摘要 → title-only 打分。论文集为一次性发布，"新" = 不在 history；首次启用某 proceeding 会有一批 backlog，由 `max_per_source`（cvf/openalex 每日条数上限）逐日泄洪，避免淹没 arxiv/HF。

跨源去重以稳定主键 `paper_key`（arxiv id → doi → cvf id → 标题哈希）合并：同一论文若 arxiv 与期刊均收录，会归并为一条。

**检查输出**：确认文件存在且包含有效 JSON 数组。如果为空数组，检查 stderr 诊断问题（可能是周末 arXiv 无更新、网络问题等），告知用户原因后停止。

**网络兜底**：`fetch_and_score.py` 的 HuggingFace Daily/Trending 与 arXiv API 抓取会先走本地 `urlopen`。若本地网络卡顿、超时或返回空内容，脚本会在存在 `LEXMOUNT_API_KEY` 时自动通过 Lexmount DOM dump 重试。key 只能来自环境变量或被 `.gitignore` 忽略的 `.env`，不得写入日志或总结文件。详细协议见 `references/network-fetch-fallback.md`。

**历史去重**：脚本在 output 同目录维护 `.history.json`，单天模式自动过滤已总结过的论文（30 天窗口），多天模式跳过去重。每次运行后自动更新历史。

### Step 1.5：公众号 AI 动态（可选，若 config `news.wechat.enabled`）

抓关注公众号（机器之心/量子位/新智元/PaperWeekly 等，配置见 `team-config.json` `news.wechat`）
在时间窗内的相关文章，作为**论文线索的补充信道**——很多号就是在第一时间解读新论文。

```bash
python3 scripts/wechat_search/fetch_wechat.py --days {DAYS} \
  --output Workbench/daily/.wechat-candidates.json
```

Read `candidates`（已按关注账号 + 关键词打分排序）。对每条：

- **是在解读某篇具体论文**（标题/摘要出现明确论文名、"XX 团队提出"、arXiv/会议名等）→
  用 WebSearch 反查该论文的 arXiv id，若查到且 vault 无笔记，按 Step 2c 的方式
  `queue_ops.py enqueue` 入队（`source` 记为 `wechat`），让 paper-digest 后续消化**原文**。
- **是行业动态/观点**（发布、融资、综述、访谈）→ 不入论文队列，留到 Step 4 的「公众号动态」小节一句话带过。

**Guard**：公众号是**二手线索**，只用来发现论文和感知风向；真正入库的证据永远是它指向的原始
论文。搜狗限流导致候选为空或 `errors` 非空时，跳过本步不阻塞。**不要**把公众号解读当论文点评写。

### Step 2：快速分流

读取 `Workbench/daily/.candidates.json`，做**轻量级分类**，不写详细点评。

#### 2a：兜底过滤

参照研究兴趣判断论文相关性，如果发现某篇论文与所有研究兴趣均无关，而且 score 不高，直接跳过。

#### 2b：分流

基于摘要和 score，将论文分流为：
- **要精读**：强相关 + 方法有新意或结果显著
- **可跳过**：其他论文（弱相关，limited novelty，marginal improvement 等）

每篇论文只需**一句话分流理由**，不写详细点评。

#### 2c：入队必读论文（持久 backlog）

把"要精读"论文写入 `Workbench/queue.json`，作为持久 backlog——这样即使本次 inline digest 未全部完成（论文太多 / 网络中断），剩余论文仍会留存，由 autoresearch 的 `paper-digest` 继续消费。

若为 `--collect-only`，此处只返回分流结果与稳定 `paper_key` / arXiv IDs，然后停止；禁止执行 enqueue 与后续 Step 3-5。

收集"要精读"论文的 arXiv id（从 `.candidates.json` 的 url 中提取，如 `2605.21573`），运行：

```bash
python3 skills/1-literature/daily-papers/queue_ops.py enqueue \
  --candidates Workbench/daily/.candidates.json \
  --ids <id1> <id2> ...
```

脚本自动去重（已有笔记或已在队列的跳过）、自清理历史遗留的“已有笔记但仍 pending”任务，并按 `max_queue_size` 裁剪。正常路径由 Step 3 coordinator 在 artifact 安全 commit 后调用 `queue_ops.py complete` 标记 done。

### Step 3：每篇要精读论文 → Prepare、串行 Commit、独立点评

从 `Workbench/config/team-config.json` 读取 `digest.parallel_limit`、`prepare_parallel_limit`、`review_parallel_limit`、`orchestration.checkpoint_every` 与 role policy。默认 global=4 / prepare=2 / reviewer=2 / checkpoint=3。Global limit 包含 nested verifier；必须给 verifier 和 coordinator 留槽位，不得把所有候选无界并发派发。

#### Phase A：并行 Prepare（无共享写入）

**每篇要精读论文派发一个 digest preparer**，指示它：

1. 调用 `paper-digest <source> --prepare-only`。
2. 按 paper-digest 内部协议由独立 verifier 检查高风险 claim。
3. 返回 artifact envelope：proposed path、完整 note、verification、claim counts、duplicate precondition。
4. 禁止写 Papers、queue、日志、BibTeX cache、survey-updates 与 daily 文件。

每批最多 `prepare_parallel_limit` 个 preparer，且所有 preparer + nested verifier 不得突破 global `parallel_limit`。每批结束更新 run manifest；单篇失败记录原因并继续，不丢失已完成 artifact。

#### Phase B：Coordinator 串行 Commit

主 agent 按候选优先级逐个处理 artifact envelope：

1. commit 前重新做 title / arXiv / DOI 去重；重复则不写并记录。
2. 严格执行 `paper-digest` Step 5-6 direct commit contract：写笔记 → YAML/contract 校验 → cite key/BibTeX → queue complete → survey 记账 → 日志。
3. 每 commit `checkpoint_every` 篇更新 manifest；共享状态一次只允许一个 writer。
4. 某篇 commit 失败时不得回滚已成功论文；manifest 标 `partial` 并继续安全项。

#### Phase C：独立 Reviewer

对每篇已 commit 或已存在的必读论文，派发**不同于 digest preparer 的 reviewer agent**：

1. 只提供 Paper note、Evidence Ledger、研究兴趣；不提供 Finder/Digest 的 reasoning、rating 或原点评。
2. 基于全文笔记而非候选摘要，按点评原则生成点评。
3. Evidence Ledger 中 `unsupported` / `contradicted` / `not-checkable` 的 claim 不得包装成肯定结论；必要时在锐评中明确指出 evidence boundary。
4. Reviewer 不修改 Paper note 或共享状态，只返回点评块。

**范围控制**：仅对"要精读" 论文执行，"可跳过"不派发 subagent。

Reviewer 最多 `review_parallel_limit` 个并行；不要等待所有论文成功后才首次产出。只要有已 commit 论文就能形成 partial summary，最终再合并剩余结果。

#### 点评模板

```markdown
### {短标题}
- **Title**: {完整标题}
- **Institutes**: {institutes}
- **Source**: [link]({url})  {来源徽章：📰 HF Daily ⬆️ N / 🔥 HF Trending ⬆️ N / 📄 arXiv / 🏛 {Venue}（OpenAlex）/ 🎓 {Proc}}   **📒 论文笔记**: [[{笔记文件名}]]
- **核心**: 3-5 句，核心 idea + 主要结果，避免黑话
- **锐评**: 方法有没有硬伤？claim 和证据匹配吗？跟已有工作本质区别在哪？哪些数字亮眼、哪些
  暴露问题？
- **Rating**: `3` 🔥 / `2` 👀 / `1` 💤 ，{一句话理由}
```

#### 点评原则

- **点评人设**: 毒舌但眼光极准的 AI 论文审稿人，见多识广、对灌水零容忍的 senior researcher。
- **语气要求**：毒舌、尖锐、精炼、有态度。不和稀泥，不说"总体还行"。明确判断好/坏。
- **内容具体：** 夸要具体（哪个数字、哪个设计），骂要更具体（哪个假设不成立、哪个实验缺了、哪个 claim 站不住脚）
- **来源格式**：
  - `hf-daily` → `📰 HF Daily ⬆️ {hf_upvotes}`
  - `hf-trending` → `🔥 HF Trending ⬆️ {hf_upvotes}`
  - `arxiv` → `📄 arXiv`
  - `openalex:{Venue}` → `🏛 {Venue}（OpenAlex）`，如 `🏛 IJCV（OpenAlex）`
  - `cvf:{Proc}` → `🎓 {Proc}`，如 `🎓 CVPR2026`

> **重要‼️**：Subagent prompt 必须包含以上完整的`点评模板` 和 `点评原则`，**不要省略**

### Step 4：汇总点评 + 生成总结文件

汇总独立 reviewer 的点评，生成总结文件，保存到 `Workbench/daily/YYYY-MM-DD.md`（日期为目标日期）。若部分论文失败，仍输出可用总结，并在开头标 `run_status: partial` 与失败清单；不得因最后一个 agent 超时而让整轮无产物。若文件已存在，覆盖写入。

写入后执行 YAML 前置校验：检查 frontmatter 中含冒号的字段值是否已加双引号，若未加则立即用 Edit 修复。

**总结文件模版：**

```markdown
---
date: YYYY-MM-DD
tags: [daily-papers, tag1, tag2, ...]
---
# 🔪 今日总结

{2-3句总结}

## 评分表

| Rating | 论文 |
|--------|------|
| 🔥 `3 - Foundation` | [[#{短标题}]]（理由）· [[#{短标题}]]（理由） |
| 👀 `2 - Frontier` | [[#{短标题}]]（理由）· ... |
| 💤 `1 - Archived` | [[#{短标题}]]（理由） |

## 论文点评

{按评分表顺序，原样拼接 Step 3 返回的各单篇点评块}

## 已跳过论文

| 论文 | 跳过原因 |
|------|----------|
| ... | ... |

## 公众号动态

<仅在 Step 1.5 有相关候选时保留本节；无则整节省略>

| 公众号 | 标题 | 一句话 / 已入队论文 |
|--------|------|--------------------|
| {source} | [{标题}]({link}) | {动态摘要，或"→ 已入队 arXiv:xxxx 待 digest"} |
```

**Tag 选择**：阅读 vault 目录下的 `{vault_root}/references/tags.md`，按照规范选择 tag。

### Step 5：追加工作日志

将以下格式的 log entry 追加到 `Workbench/logs/YYYY-MM-DD.md`（日期为今天）：

```markdown
### [HH:MM] daily-papers
- **input**: {DAYS} 天
- **output**: [[Workbench/daily/YYYY-MM-DD]]
- **observation**: 抓取 K 篇，精读 N 篇（rating 3: X / 2: Y / 1: Z），跳过 M 篇
- **verification**: source-checked / partial / unverified 各 N 篇；高风险 claims verified/total
- **run_id**: <run_id>（manifest: Workbench/runs/<run_id>.json）
```

若日志文件不存在，先创建文件（包含一级标题 `# YYYY-MM-DD`），再追加 entry。

**告知用户**：抓取 K 篇，精读 N 篇（rating 3: X / 2: Y / 1: Z），跳过 M 篇

## Verify

- [ ] `Workbench/daily/.candidates.json` 存在且非空
- [ ] `Workbench/daily/YYYY-MM-DD.md` 已创建
- [ ] 评分表中的 `[[#{短标题}]]` 链接与论文点评的 `### {短标题}` 完全匹配
- [ ] 要精读论文笔记已生成，论文点评基于笔记内容
- [ ] Digest preparer 使用 `--prepare-only`，共享状态由 coordinator 串行 commit
- [ ] 每篇点评由不同于 Digest/Finder 的 reviewer 生成，且只依赖笔记 + Evidence Ledger
- [ ] run manifest 包含 stage/checkpoint/失败清单；partial run 仍有可读总结
- [ ] 日志已追加到 `Workbench/logs/YYYY-MM-DD.md`
