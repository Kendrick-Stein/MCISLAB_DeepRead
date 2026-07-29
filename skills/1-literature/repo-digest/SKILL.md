---
name: repo-digest
description: >
  当已 digest 的论文带代码库（frontmatter `code` 非空 / 日志有 repo_candidate 标记），
  且属于系统/环境/基建类工作（贡献主要在实现里，如 CUA-Gym、WebHarbor、OpenRath、Crab），
  或 Supervisor 说"把代码库也读了""分析一下这个 repo"时：git clone 代码库、
  并行派发多个 codex subagent 做静态分析，结合论文内容把实现细节写回 Papers/ 笔记。
argument-hint: "<Papers/笔记路径 或 repo URL> [--passes architecture,mechanism,repro,affordance]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# Repo Digest — 论文代码库分析

## Purpose

论文有 paper-digest，代码库没有对应物——但 CUA/AFE 方向的关键工作（环境 runtime、
benchmark、训练基建）贡献主要在系统实现里，论文正文往往只给 high-level 描述。
本 skill 把代码库 clone 下来做一次**静态分析**（不执行代码），将"论文怎么说 ↔ 代码怎么做"
的对照、论文没写的实现细节、复现路径写回对应 Papers/ 笔记，丰富报告细节、
为后续实验设计提供 grounding。

分析是重活，采用 **workflow + 多 codex subagent 并行**编排（复用 backfill 已验证的
`codex exec` 模式）：Codex 写各分析 pass，Claude 独立抽查核对后才入笔记
（Codex 写 / Claude 查，同 daily-papers codex digest 的分工纪律）。

## Steps

### Step 1：定位 repo 与论文笔记

- 输入是 `Papers/` 笔记路径 → 读 frontmatter `code` 字段取 repo URL。
- 输入是 repo URL → Grep `Papers/` 找对应笔记；**无笔记则先跑 paper-digest**（本 skill
  不替代论文消化，代码分析必须有论文笔记作对照基准）。
- 读取笔记的 Summary / Method / Key Results / Evidence Ledger，抽出 3-8 个
  「要到代码里核对的点」：核心机制、关键超参、benchmark 生成/评测逻辑、
  论文声称的系统能力。

### Step 2：Clone 到 staging + 规模概览

```bash
mkdir -p Workbench/tmp/repo-digest && cd Workbench/tmp/repo-digest
git clone --depth 1 <repo_url> <repo-name>
cd <repo-name> && git rev-parse HEAD   # 记录 commit sha
find . -name "*.py" -o -name "*.ts" -o -name "*.js" | grep -v test | head -50
```

- **>2GB 或含大量数据/权重文件**：停下向 Supervisor 确认（或用 sparse-checkout 只取代码目录）。
- 记录 commit sha——所有分析结论锚定到这个版本。

### Step 3：生成分析任务清单（pass 划分）

默认 3 个 pass，环境/benchmark 类 repo 加第 4 个：

| Pass | 回答什么 | 输出 |
|:--|:--|:--|
| `architecture` | 目录结构、模块划分、入口、核心抽象、代码规模、外部依赖 | `analysis/architecture.md` |
| `mechanism` | Step 1 的核对点逐条定位到 file:line；论文没写的实现细节（trick、默认超参、fallback、hardcode） | `analysis/mechanism.md` |
| `repro` | 环境依赖、怎么跑起来、训练/评测脚本入口、数据准备、明显的算力/API 要求 | `analysis/repro.md` |
| `affordance`（环境类） | 环境暴露给 agent/trainer 的接口面：obs/action 空间、reset/state/fork、verifier/reward 的实现与精度边界 | `analysis/affordance.md` |

### Step 4：并行派发 codex subagent

对每个 pass 起一个 codex 进程（并行，Bash `run_in_background` 或 `&`；600s 超时轮询）：

```bash
codex exec -s workspace-write --add-dir "Workbench/tmp/repo-digest/<repo-name>" \
  "你在分析论文《<title>》的官方代码库（只读分析，不执行任何代码/不安装依赖）。
   任务：<该 pass 的问题清单，含 Step 1 的核对点>。
   要求：每个结论必须给出 file path 与行号区间；不确定就写不确定，禁止编造。
   把结果写入 <staging>/analysis/<pass>.md。"
```

- **codex 不可用时的 fallback**：用 Agent 工具并行派发同等数量的分析 subagent
  （Explore 型，只读），prompt 同上。
- 单 pass 失败/超时：重试一次，仍失败则记录并降级（该 pass 缺失不阻塞其他 pass）。

### Step 5：Claude 独立核查（Codex 写 / Claude 查）

对每个 pass 的输出：

1. 抽查 **3-5 个 file:line 引用**：用 Read 打开对应文件行，确认引用真实且支撑结论。
2. 抽查发现编造/错位 → 该 pass 整体降级为 `unverified`，关键结论不入笔记，或重跑该 pass。
3. 与论文笔记对照：实现与论文描述**不一致**的点（论文说 A 代码做 B）单独列出——
   这是最有信息量的发现，须给出双方证据（paper locator + file:line）。

### Step 6：写回 Papers/ 笔记

用 Edit 在对应笔记**末尾追加**（不动已有章节）：

```markdown
## Implementation Analysis

> repo: <url> @ <commit sha 前 7 位>，分析日期 YYYY-MM-DD，静态分析未执行代码

**架构**：<2-4 句：模块划分与核心抽象>

**论文 ↔ 代码对照**：

| 论文 claim | 代码位置 | 一致性 |
|:--|:--|:--|
| <claim> | `path/file.py:L120-145` | 一致 / 论文未提 X / 不一致：<说明> |

**论文没写的实现细节**：<trick、默认超参、fallback、hardcode，各带 file:line>

**复现路径**：<依赖、入口脚本、数据准备、算力要求，2-4 句>

**Affordance 面**（环境类）：<接口清单 + verifier 实现方式，各带 file:line>
```

frontmatter 追加 `repo_analyzed: "<commit sha 前 7 位> YYYY-MM-DD"`。
若发现改变对论文判断的重大不一致，在 Strengths & Weaknesses 不改写原文，
而是由 Supervisor 决定是否修订（在会话中明确报告该发现）。

### Step 7：清理 + 记录

```bash
rm -rf Workbench/tmp/repo-digest/<repo-name>
```

追加日志到 `Workbench/logs/YYYY-MM-DD.md`：

```markdown
### [HH:MM] repo-digest
- **input**: [[Papers/YYMM-ShortTitle]] | <repo url> @ <sha>
- **passes**: architecture ✓ / mechanism ✓ / repro ✓ / affordance ✓|skip
- **spot_check**: 抽查 N 处 file:line，M 处属实（M<N 时说明降级处理）
- **findings**: <一句话：最有信息量的发现，尤其论文↔代码不一致点>
- **status**: success / partial
```

## Guard

- **只读静态分析，禁止执行 repo 代码**：不 pip install、不跑训练/评测脚本、不下载数据集/
  权重。执行类复现不在本 skill scope（属实验侧，需 Supervisor 单独授权）。
- **不 clone 私有 repo**、不在任何输出里留 token/凭证；staging 目录已 gitignore，
  **禁止把外部代码 commit 进 vault**。
- **入笔记的每个关键结论必须带 file path（+行号）grounding**；Codex 输出未经 Step 5
  抽查不得入笔记；抽查失败的 pass 降级或重跑，不得带病写入。
- **只追加 `## Implementation Analysis` 节**，不修改笔记其他章节；重跑时替换该节而非重复追加。
- 代码分析结论表述为"该版本实现如此"（锚定 commit sha），不外推为"论文结果由此复现"。
- 论文↔代码不一致点必须双方证据齐全才可写"不一致"；单边证据写"待核"。

## Verify

- [ ] 笔记含 `## Implementation Analysis` 节，头部有 repo URL + commit sha + 分析日期
- [ ] 对照表每行有 file:line；抽查记录在日志（N 处抽查、M 处属实）
- [ ] frontmatter `repo_analyzed` 已写入
- [ ] staging 下该 repo 目录已删除；`git status` 无外部代码文件混入
- [ ] 日志 entry 五项齐全；重大不一致发现已在会话中向 Supervisor 明确报告

## Examples

`/repo-digest Papers/2606-CUAGym.md` → frontmatter code 取 GitHub URL → shallow clone
（sha a1b2c3d）→ 4 pass 并行（含 affordance）→ 抽查 12 处 file:line 全属实 →
笔记追加 Implementation Analysis：task/state/reward.py 的 RLVR tuple 生成逻辑定位到
`cua_gym/reward.py:L88-140`，发现论文未提的 reward clip 与 retry fallback；
affordance 面确认 reset/fork 只暴露给 trainer 未暴露给 agent（支撑 AFE gap 判断）→
清理 staging + 日志。
