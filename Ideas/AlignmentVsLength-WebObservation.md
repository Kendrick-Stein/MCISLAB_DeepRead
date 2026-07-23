---
title: "Alignment-vs-Length：web agent 观察优化的杠杆是"对齐"还是"变短"？"
tags: [gui-agent, web-agent, research-idea]
status: raw
linked_project:
date_updated: "2026-07-23"
---
## Hypothesis

整个 web-agent observation-reduction 子领域默认"更短=更好"。但 [[Papers/2410-AgentOccam]] 给了一个未被解释的悖论：它把页面重构成 Markdown/降噪表示后 WebArena 做到 43.1%，可每步观察 token **反而从 vanilla 2210 升到 2930**——收益来自表示对齐/降噪，而非缩短。假设：**在固定 policy、固定 token 预算下，越接近该模型预训练分布的表示（length-normalized policy perplexity 越低）step accuracy 越高；"对齐"轴解释的方差大于"长度"轴；一个只优化对齐（不再缩短）的 rewriter 能在等预算下追平甚至超过激进 pruning。**

可证伪设计：构造 2×2 表示变体——长度 {full, reduced} × 对齐 {raw-format, aligned}，**四格 token 数配平**。预测：

- 固定模型下，aligned 的 step-accuracy 主效应显著且大于 length 主效应；
- 跨表示变体，length-normalized policy perplexity 与 step accuracy 负相关（控制长度后仍成立）；
- 一个训练来最小化 length-normalized policy perplexity（受 element-recall 约束）的 alignment rewriter，在**等 token 预算**下 ≥ FocusAgent/Prune4Web 式 length-matched pruning。
- **Kill criterion**：若配平预算后 length 主效应 ≥ alignment 主效应，或 alignment 效应的 CI 含 0，则"对齐是主杠杆"被证伪——AgentOccam 悖论归因于 action-space/planning 而非观察对齐。

## Motivation

### 问题为什么重要

若"对齐 > 长度"成立，这条子领域的优化目标是错的：大家在刷 compression ratio，而真正的杠杆是**把观察改写成模型见过的分布**。这会把"再压 10% token"的工程竞赛，换成"最小化观察在 policy 下的 perplexity（受可操作元素保全约束）"的新目标函数——一个可直接落地、可训练的方向，而不是又一个测量。actionability 明确。

### 机制假设

LLM 对 in-distribution 文本处理更可靠，对 formatting-heavy 的 DOM/a11y token（大量 role/attribute/结构标记）则是 OOD 噪声，稀释 attention。因此在相同长度下，把同样的信息用更"自然文本/Markdown"的形式承载，会降低有效噪声、提高 grounding/step 正确率。这解释了 AgentOccam 为何在 token 更多时仍更好——它换的是分布不是长度。[[Papers/2511-Prune4Web]] 的 0.5B=3B 打平（剪枝后小模型追平大模型）是旁证：瓶颈是 candidate 噪声/表示质量，而非模型容量。

### 已知 / 未被证明

- **已知**：AgentOccam 断言"对齐 observation space 到 LLM"是杠杆，但把它与 action-space 精简、planning（branch/prune）**捆绑**，且没有在配平长度下隔离对齐；LLMLingua 等用 per-token perplexity 做**压缩**（删低 perplexity token），方向相反。
- **尚未被证明**：在配平 token 预算、隔离观察通道（不动 action space / planning）下，"对齐"独立于"长度"对 step accuracy 有主效应且更大。这需要一个受控 2×2，不能由 AgentOccam 的端到端数字推断。

## Related Work
- [[Papers/2410-AgentOccam]] - 悖论来源与最近邻先验：token 反增仍提升，断言对齐是杠杆；但对齐与 action-space/planning 捆绑、未配平长度隔离对齐。本工作是对它的**受控解耦**。
- [[Papers/2511-Prune4Web]] - 0.5B=3B 打平，支持"表示质量 > 模型容量"的机制侧证据。
- [[Papers/2510-FocusAgent]]、[[Papers/2605-A11yCompressor]] - length-reduction / 结构重构方法，作为"等预算 pruning"对照臂。
- [[Papers/2604-ReadMoreThinkMore]] - 表示richness × capability，间接支持"formatting/长输入伤弱模型"；但它比的是 a11y↔HTML 整块，不做 length×alignment 配平解耦。
- [[Papers/2605-MFSCoverage]] - 提供 element-recall 约束（保证 rewriter 不丢可操作元素）的现成度量。
- [LLMLingua](https://arxiv.org/abs/2310.06839) - per-token perplexity 驱动 prompt 压缩（删 token），与本工作的"配平长度下优化对齐、不缩短"正交且方向相反。
- [Rethinking Perplexity: Input Length on Perplexity](https://arxiv.org/abs/2602.04099) - 证明 perplexity 有长度偏置；本工作必须用 length-normalized per-token perplexity + 配平预算来规避（见 Risk）。

**Novelty**: 3/5 — closest works: [[Papers/2410-AgentOccam]]、[[Papers/2604-ReadMoreThinkMore]]、[LLMLingua](https://arxiv.org/abs/2310.06839)。可守新颖性：**在配平 token 预算、隔离观察通道下，把 web-agent 观察增益分解为 alignment vs length 两个可测轴，并用 length-normalized policy perplexity 作对齐 proxy + alignment-only rewriter 验证**。不声称"对齐重要"是新观点（AgentOccam 已提），而是首次做受控解耦并给出可训练的 alignment-optimizing 目标。

## Approach sketch

**Phase 1（受控 2×2）**：固定一个 frozen policy，构造四类观察变体，四格 token 数配平（用等预算的 selection/padding-equivalent 控制长度）：
- full-raw（原 a11y/HTML）、reduced-raw（FocusAgent/Prune4Web 式剪枝）、full-aligned（不缩短、只改写成 Markdown/自然文本降噪）、reduced-aligned（既短又对齐，≈AgentOccam）。
- 度量：step accuracy / element grounding（WorkArena L1、Mind2Web）；对齐 proxy = length-normalized per-token NLL under frozen policy（显式做长度校正）。

**Phase 2（方差分解）**：把 step accuracy 对 (length, alignment) 做回归 / ANOVA，报主效应与交互；跨变体测 perplexity↔accuracy 相关（partial，控长度）。这是 Go/Kill 的核心证据。

**Phase 3（alignment rewriter，可学习组件）**：训练一个小 LM（或 prompt+蒸馏）把 raw DOM → aligned 表示，目标 = 最小化 length-normalized policy perplexity，**约束** = 保全可操作元素（用 [[Papers/2605-MFSCoverage]] 的 MFS/coverage 作 element-recall 约束，防止 rewriter 丢按钮/输入框）。

**Phase 4（等预算对照）**：固定 token 预算，比较 {reduced-raw pruning、full-aligned rewriter、reduced-aligned}，看"对齐但不更短"能否追平/超过激进剪枝；跨强/弱两个 base model 验证对齐收益是否对弱模型更大（机制预测）。

## Expected outcome

- 配平预算下 alignment 主效应显著且大于 length 主效应；length-normalized policy perplexity 与 step accuracy 稳健负相关；
- full-aligned（不缩短）在等预算下 ≥ reduced-raw pruning，复现并解释 AgentOccam 悖论的观察侧来源；
- alignment 收益对弱模型更大（弱模型对 OOD formatting 更敏感），与 Read-More 的 capability 依赖方向一致；
- 产出一个可复用的 alignment-optimizing 目标（perplexity + element-recall 约束），把 reduction 研究从"压比率"重指向"对齐 + 保全"。

成功标准：两个 base model 上 alignment 主效应 CI 下界 >0 且 > length 主效应；rewriter 在等预算下不劣于 pruning。

## Risk

- **Perplexity 长度偏置（首要方法学风险）**：perplexity 天然偏向长文本 / 特定 tokenizer（[2602.04099] 已证）。必须用 length-normalized per-token perplexity + 严格配平 token 预算；即便如此，"对齐"用 perplexity 操作化仍可能被质疑混入内容差异。需加人工/对比校验对齐是否真是"分布接近"而非"信息更多"。
- **AgentOccam 的增益不只来自观察**：它同时改了 action space（删 scroll/hover、加 branch/prune）与 planning。本工作必须**只动观察通道**、冻结 policy 与 action space，否则分解无效。
- **配平长度困难**：full-aligned 与 reduced-raw 精确等 token 需要工程（截断/选择等价），配平不干净会成 confound。
- **"对齐"操作化争议**：若审稿人不接受 perplexity=对齐，需要备用度量（如 n-gram overlap with pretraining-like corpora、或 held-out human-naturalness rating）。
- **so-what 取决于效应量**：若 alignment 效应虽显著但很小，贡献退为"科学解释"而非"新目标函数"。用 rewriter 的等预算对照臂把它拉回 actionable。

## Evaluation — 2026-07-23（首轮，novelty-verified）

| Dimension | Score | Notes |
|:--|:--:|:--|
| Novelty | 3/5 | AgentOccam 已提"对齐重要"；可守的是配平预算下 alignment vs length 的**受控解耦** + alignment-only rewriter；LLMLingua 方向相反不构成冲突 |
| Feasibility | 3/5 | 2×2 测量与回归可做；配平 token 预算 + 训练 alignment rewriter 工程量中等；perplexity 长度校正需谨慎 |
| Impact | 3/5 | 若成立则重指向子领域优化目标（从压比率→对齐+保全），actionable；但若效应小则退为科学解释 |
| Risk | 3/5 | perplexity 长度偏置 + "对齐"操作化 + AgentOccam 增益隔离是三处硬风险 |
| Evidence | 4/5 | AgentOccam token 反增悖论是强直接动机；Prune4Web 0.5B=3B 旁证"表示质量>容量" |
| **Total** | **16/25** | 机制清晰、动机强，但操作化与配平的方法学风险高于 [[Ideas/RepresentationRegret-WebObservation]] |

**Reasoning**：这是把 AgentOccam 的一个具体悖论（token 更多却更好）升级为可证伪的受控解耦，并给出可训练的 alignment 目标。风险集中在"对齐"能否被干净地操作化与配平；若 Phase 1 的 2×2 就显示 length 主效应不弱于 alignment，应立即改问"是什么第三因素（如 action space）驱动 AgentOccam"，不硬撑。

**Suggested next action**：先做最小 2×2 pilot（单模型、~100 页、手工构造 full-aligned vs reduced-raw 各配平预算），只回答：配平长度后 aligned 是否仍显著更好、perplexity 长度校正后相关是否稳健。若否，pivot 到 [[Ideas/RepresentationRegret-WebObservation]]。

## Novelty search log — 2026-07-23

- `representation alignment vs length reduction LLM agent controlled decomposition perplexity in-distribution observation formatting tokens` → 无统一论文把 perplexity/in-distribution 与 agent 的 observation formatting token 绑定；关键警告：perplexity 有长度偏置（[2602.04099]）、LLMLingua 用 per-token perplexity 做压缩（反方向）。
- 复用本轮 digest 的 [[Papers/2410-AgentOccam]]（token 反增悖论）、[[Papers/2511-Prune4Web]]（0.5B=3B）作机制证据。
- 结论：alignment vs length 的**受控配平解耦** + alignment-only rewriter 未被占据；"对齐重要"本身已被 AgentOccam 提出，故 claim 收窄到解耦与可训练目标。
