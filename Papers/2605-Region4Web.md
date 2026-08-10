---
title: "Region4Web: Rethinking Observation Space Granularity for Web Agents"
authors: [Donguk Kwon, Dongha Lee]
institute: [Yonsei University]
date_publish: 2026-05-08
venue: arXiv
tags: [web-agent, gui-agent]
url: "https://arxiv.org/abs/2605.07134"
arxiv_id: "2605.07134"
doi:
cite_key: kwon2026region4web
code: "https://github.com/kwondu/region4web"
rating: 4
content_scope: full-text
verification_status: verified
date_added: 2026-08-10
---
## Summary

论文主张 web agent 的 observation space 不该沿用 action space 的 element-level 粒度，而应以 **functional region**（一组共享同一功能目的的元素）为单位：Region4Web 用一个约 536K 参数的 edge 分类器把 AXTree 自底向上切成 region，再用 fine-tuned Qwen3-0.6B 为每个 region 生成 purpose 与 state summary。配套的 PageDigest 推理管线在进入新页面时由 actor 自己的 backbone 挑选 task-relevant region，并在页内用增量 diff 维持这份 digest 而非逐步重建观察；WebArena 上四个 backbone 平均把每步观察从 6,437 压到 3,671 tokens（-43%）、成功率 +2.3pp。**但全文没有把 full-observation baseline 压到同等 token 预算做对照**，"更短且更好"只在各自的自然长度下成立。

## Problem & Motivation

现有 web agent 研究几乎都把注意力放在 action selection（planning、grounding、模型能力），而 page state understanding 一侧的处理方式基本是对元素做过滤或截断（ACON、LCoW、Prune4Web），全部停留在 element-level。作者指出这里藏着一个从未被审视的设计选择：**observation space 和 action space 被默认赋予了同一种粒度**。

作者认为这两个空间的职责不同。element-level 对 action space 是自然的——每个 action 精确指向一个元素并施加一种操作；但 observation space 的职责是提供理解当前页面状态所需的 context，而 context 不止于单个元素，还包括元素之间的关系。论文把这种关系收束为 functional region：一组元素，其相互关系服务于同一个目的（如站内导航、结果收窄）。在 element-level 表示下，region 及其目的只隐含在个别元素中，agent 每一步都得重新推断一遍。

论文同时区分了自己与 GUI 侧 screenshot 分区工作（Tree-of-Lens 等）：视觉上的空间邻近**不蕴含**共享功能目的，bounding box 重叠只能给出视觉分组，无法说明这组元素是否构成一个功能观察单元、以及它服务于什么目的。规则法同样不行——Figure 1 的例子是结构完全相同的 card grid：当每张卡是独立商品预览时应切成多个 region，当它们共同构成一个 showcase 时应合为一个 region，结构本身无法区分。

两条前置测量（Mind2Web，2,350 tasks / 137 sites，页均 2,473 个 DOM 节点，15,394 对连续 action，其中 78.0% 发生在同一页面内）支撑了设计：

1. **动作在页面结构里是局部的**。单页内 action 数中位 6、90 分位 13，相对上千节点可忽略；连续 action 对的 LCA depth ratio 中位 0.48，81.7% 超过 random baseline 的中位 0.22——连续动作集中在局部子树内，region 因此是自然的观察构造单元。
2. **页内观察逐步变化极小**。52.9% 的步骤 DOM 零变化，74.4% 变化率低于 5%；变化超过 90% 的只占 2.5%（归因于 SPA 的 client-side routing）。因此每步重建完整观察是冗余的。

## Method

### Region4Web：AXTree 的两阶段重组

**Hierarchical Decomposition（结构边界）**。观察建模为树 `T=(V,E)`，region partition 等价于把每条 parent-child 边二分类为 merge 或 cut——去掉 cut 边后剩下的子树即 region，root 子树构成最后一个 region。

- 节点特征 `x_v` 为 **16 维**：11 维 learned role embedding（词表 204 项 = Chromium accessibility role 枚举 203 项 + 1 个 unknown）+ 5 个数值特征（深度、子树大小、子节点数、accessible name 是否非空、child role diversity = 唯一子 role 数 / 子节点数）。
- `EdgeClassifier(x_v, r_ci, r̄)` 以 **sibling mean `r̄`** 作为上下文判定每个孩子是否切开，`ŷ ≥ τ` 则 cut。
- `RegionEncoder(x_v, mean(r_cj for cj in 合并子集))` 只聚合**留在本 region 内**的孩子来算父节点表示。
- 全过程**单次自底向上遍历**完成：每个节点的表示只在其所有孩子的边界决策解决后才计算，边界决策沿层级向上传播，不需要第二遍。作者在 Related Work 里明确点出这是与常规 tree representation learning 的差别——后者树结构事先给定、表示学习不改变父子归属，而 region partition 的边界决策会直接改变父节点要表示哪些孩子（boundary-representation dependency）。
- 两个模块均为 3 层 MLP、hidden 256、ReLU；RegionEncoder 输入 272 维，EdgeClassifier 输入 528 维；含 role embedding 表共约 **536K 参数**。

**Semantic Abstraction（语义解释）**。fine-tuned **Qwen3-0.6B** 接收每个 region 的预处理 AXTree 子树，输出两个正交维度：
- **purpose `p_i`**：这个 region 是干什么的（跨步骤稳定）；
- **state summary `s_i`**：该 region 当前的 actionable context（随步骤变化）。

选小模型是为了让 abstraction 能按 region 逐个调用而不主导推理延迟。

**AXTree 预处理**（App D，基于 BrowserGym）三处改动：(1) 用 `backendDOMNodeId` / BrowserGym `bid` 作跨步骤稳定标识，这是 §4.2 增量 diff 的基础；(2) BrowserGym 会无条件删掉无属性的 generic/none 节点，导致 DOM 中起分组作用的 wrapper 塌成扁平兄弟列表——本文保留"有 ≥2 个含可见后代的子分支"的这类节点，保住 decomposition 依赖的结构分组；(3) 空 accessible name 的 image/link 节点补上 `src`/`href`。

**训练数据**（App E）。Tranco top-1M（2026-04-01 快照）按 IAB Content Taxonomy 3.1 的 37 个 Tier-1 类中选 10 类，取排名最高的 500 站；按 sitemap 元数据打分每站最多采 100 个 URL，可访问的剩 253 站、**21,974 页**。标注器为 **gpt-5-mini-2025-08-27**，三阶段：decompose → verify → abstract。verify 阶段只保留"每一个 region 都合法"的页面，**21,967 → 2,052 页（9.3%）**、46,487 region；再剔除 1,340 个纯 none/generic 的空 region，得 **45,147 region**。总计 616,954 条边，其中 cut 边 44,116（7.15%）。作者对 90.7% 的淘汰率的解释是"被淘汰页面以真实网站噪声为主，而非标注器能力不足"。

**训练细节**（App F）。decomposition 用 teacher forcing（ground-truth 边标签决定遍历中的 cut/merge），focal loss `α=0.75, γ=2.0` 处理 merge:cut 类别失衡，140 epoch，按验证集 edge-level F1 选 epoch 125；推理阈值 τ 在 region 层面调（IoU≥0.5 判匹配），τ=0.55 取得最高 region-level F1 **0.7749**（P 0.7755 / R 0.7743）。abstraction 全参 SFT，bf16，90 epoch / 76,200 step，3×A6000 DDP，有效 batch 48，AdamW lr 5e-6，max seq 8,192（0.08% 样本超长被跳过），选 step 65,350。

### PageDigest：跨步骤持久化的页面摘要

**进入新页面时**（§4.1）：Region4Web 产出 `R` 与 `{(p_i, s_i)}`；**actor agent 自己的 backbone LLM** 接收全部 abstraction + task instruction + 已执行 action history，选出 task-relevant region。
- 选中 region → 以**完整 AXTree 子树 + purpose** 暴露，从而在 region 内保留 action space 所需的 element-level 粒度；
- 未选中 region → **只保留 purpose**，用于维持页面整体功能结构的可见性。

**页内维持时**（§4.2，这是"cache 什么"的关键）：
- **不重新调用 Region4Web**。每步把当前 AXTree 与**页面进入时**的 AXTree 比对（靠稳定 node id），得到 added / removed / modified 三类节点。
- removed / modified 节点**就地更新**页面进入时构造的那棵 AXTree（删节点或改值），仍挂在既有 region purpose 之下。
- added 节点**不并入既有 region**，而是单独列为一组、保留组内结构分组——理由是并入会改变那些 region 的 purpose。
- **跨步骤持久化的只有 region purpose，不含 state summary**。purpose 描述"这个 region 是干什么的"，页内稳定；state summary 描述当前 actionable context，只在页面进入时的 region selection 有用，不适合用于 transition management。
- **失效条件是 URL 变化**：导航到新页面时重新调用 Region4Web 并重做 region selection。

**兜底与可移植性**：额外给 actor 一个 `view_all` action，可在本页剩余步骤中展开所有 region 的完整 AXTree 子树，用于 region selection 不足时兜底。PageDigest 共享 actor 的 backbone、只作用于 observation space，不引入额外模型、不改动 actor 的 policy。

## Key Results

**实验设置**。WebArena 全量 812 任务、每任务上限 30 步，五个域；原评测器 `gpt-4-1106-preview` 已下线，替换为 **GPT-4o**；BrowserGym 环境，Map 域路由到真实 OpenStreetMap 服务；开源模型 temperature 0 且关闭 thinking，闭源模型保持默认；**observation length 定义为每步喂给 agent 的观察的 token 数**，一律用 OpenAI `o200k_base` 计。

### Table 1：按 backbone 与按 agent framework

| Actor agent | Shopping | CMS | Reddit | GitLab | Map | **Overall** | **Obs. length** |
|:--|--:|--:|--:|--:|--:|--:|--:|
| GPT-5.1 | 39.0 | 57.1 | 65.1 | 46.1 | 24.8 | **45.2** | 6,116 |
| + PageDigest | 41.1 | 54.5 | 60.5 | 50.5 | 28.4 | **47.5** | 4,302 (-30%) |
| Gemini 3.1 Flash-Lite | 33.3 | 41.2 | 54.0 | 44.7 | 22.9 | **39.4** | 6,705 |
| + PageDigest | 34.9 | 44.5 | 59.3 | 42.6 | 28.4 | **41.6** | 3,207 (-52%) |
| DeepSeek-V3.2 | 30.7 | 51.1 | 58.5 | 40.4 | 21.1 | **40.4** | 7,158 |
| + PageDigest | 33.3 | 53.7 | 61.1 | 46.5 | 21.1 | **43.4** | 4,521 (-37%) |
| Qwen3.5-27B | 22.9 | 53.8 | 58.8 | 35.3 | 22.9 | **38.2** | 5,767 |
| + PageDigest | 38.6 | 46.2 | 60.4 | 35.2 | 18.9 | **39.9** | 2,654 (-54%) |
| SteP (GPT-4o) | 32.6 | 45.7 | 71.4 | 46.9 | 12.8 | **39.5** | 7,136 |
| + PageDigest | 35.8 | 37.1 | 63.2 | 50.0 | 15.4 | **38.7** | 3,693 (-50%) |
| AgentOccam (GPT-4o) | 26.7 | 36.3 | 73.7 | 66.7 | 11.5 | **40.6** | 4,025 |
| + PageDigest | 35.6 | 40.0 | 68.4 | 50.0 | 23.1 | **41.3** | 3,365 (-16%) |

四 backbone 平均：观察长度 **6,437 → 3,671 tokens（-43%）**，成功率 **+2.3pp**（40.8 → 43.1）。逐个看：GPT-5.1 +2.3pp / -30%，Gemini +2.2pp / -52%，DeepSeek +3.0pp / -37%，Qwen +1.7pp / -54%。压缩率与 backbone 强弱无明显关系，但**削减幅度与增益幅度呈反相关**——削得最狠的 Qwen（-54%）增益最小（+1.7pp），削得最少的 GPT-5.1（-30%）增益反而居中。

两个 agent framework（backbone 均为 GPT-4o，与二者原始开发环境的 GPT-4 家族对齐）：SteP **-0.8pp**（39.5→38.7）/ -50%；AgentOccam **+0.7pp**（40.6→41.3）/ -16%。论文对这两行的措辞是 "comparable task success rate"，即**在 framework 层面本方法并不涨点，卖点只剩长度**。AgentOccam 配置下作者替换掉它自带的 observation space alignment、保留其 action space alignment，以隔离 region-level observation 的效应。

### Table 2：消融（WebArena-Lite 165 任务，GPT-5.1）

| Configuration | SR (%) | Obs. length |
|:--|--:|--:|
| GPT-5.1 | 48.5 | 5,410 |
| + Region4Web | 50.3 | 5,922 |
| + Self-ctx (LCoW) + §4.2 | 46.1 | 4,013 |
| + PageDigest | **53.9** | **3,814** |

三点读法：

1. **Region4Web 单独使用会让观察变长**（5,410 → 5,922，+9.5%），只换来 +1.8pp。region-level 表示本身不是压缩方法，全部压缩来自 PageDigest 的 region selection + 跨步骤持久化。
2. **element-level 变体（LCoW self-contextualization + §4.2 的 transition management）反而低于 baseline**：46.1 vs 48.5（-2.4pp），而它的长度 4,013 与 PageDigest 的 3,814 大致相当（-26% vs -30%）。这是全文唯一一处近似等长的对照，且被作者用来论证"是 region 粒度在起作用，element-level 处理反而有害"。
3. 完整 PageDigest 53.9（较 backbone **+5.4pp**）、长度最短。

**没有做的拆分**：全文**没有任何消融把 hierarchical decomposition 与 semantic abstraction 分开**（例如"只切 region 不写 purpose/state summary"或"用规则切分 + 学出来的 abstraction"）。cross-step persistence（§4.2）也**没有单独消融**——它同时出现在 element-level 变体和完整 PageDigest 中，只能间接推断，而 `+Region4Web` 那一行既无 selection 也无 persistence，故 selection 与 persistence 的贡献互相纠缠、无法分离。`view_all` fallback 的移除消融同样缺失。

### Token 账（§5.3，GPT-5.1）

- **step-scale 中位**：3,077 → 2,066 tokens（**-33%**）。注意这与 Table 1 的均值口径不同（Table 1 为每步平均）。
- **task-scale 中位累计**：26,707 → 19,944 tokens（**-25%**），**该数字已包含辅助开销**。
- 开销拆分：actor observation 73.9% / region selection 19.5% / `view_all` 6.6%。
- region selection 每任务平均调用 **4.8 次**（按进入新页面次数计），因为它只吃 region 级 abstraction 而非 element 级 AXTree，所以便宜；`view_all` 在 **38.1% 的任务**中至少触发一次，平均 0.64 次/任务。

**关键口径差异**：Table 1 的 "-43%" 只统计 actor 侧观察，不含 region selection 与 `view_all`；把辅助开销计入后的净收益是 task-scale 的 **-25%**。survey 里引用时不要混用这两个数。

### 失败归因（§5.3，Fig 6）

50 条 PageDigest 下的失败轨迹（每域 10 条），多因归因（故各项和 >100%）：decomposition 2.0% / abstraction 2.0% / region selection 10.0% / transition management **0%**（确定性 diff，无误差来源）/ actor-side 90.0% / environment 16.0%。作者结论："PageDigest operates as designed"，82.0% backbone 能力问题压过 8.0% PageDigest 自身回退。

## Evidence Ledger

> 状态来自一次独立 verifier pass（只给 primary source、claim package 与状态定义，不给本笔记的分析与优缺点判断）。`source-verified` 仅表示原文确实包含该信息，不表示结果已被独立复现。

> 本笔记在 prepare-only 模式下产出，**独立 verifier 尚未运行**，全部 Status 记为 `pending`；`verification_status: unverified`。全部数据取自 arXiv HTML v1 全文，非二手来源。

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 四 backbone 平均观察长度 6,437→3,671 tokens（-43%），成功率平均 +2.3pp | number | §5.2 | "reduces observation length by 43% on average, from 6,437 to 3,671 tokens, and improves task success rate by 2.3%p on average" | source-verified |
| C2 | GPT-5.1: 45.2→47.5，6,116→4,302（-30%） | number | Table 1 | "GPT-5.1 … 45.2 … 6,116 … + PageDigest … 47.5 … 4,302 (-30%)" | source-verified |
| C3 | Gemini 3.1 Flash-Lite: 39.4→41.6，6,705→3,207（-52%） | number | Table 1 | "Gemini 3.1 Flash-Lite … 39.4 … 6,705 … 41.6 … 3,207 (-52%)" | source-verified |
| C4 | DeepSeek-V3.2: 40.4→43.4，7,158→4,521（-37%） | number | Table 1 | "DeepSeek-V3.2 … 40.4 … 7,158 … 43.4 … 4,521 (-37%)" | source-verified |
| C5 | Qwen3.5-27B: 38.2→39.9，5,767→2,654（-54%） | number | Table 1 | "Qwen3.5-27B … 38.2 … 5,767 … 39.9 … 2,654 (-54%)" | source-verified |
| C6 | SteP (GPT-4o) 总体从 39.5 降到 38.7（论文只称 "comparable task success rate"），观察 7,136→3,693；论文标 -50%，实算 **-48.2%** | number | Table 1; §5.2 | "reduces observation length by 50% and 16% with comparable task success rate" | source-verified（-50% 为论文取整，独立 verifier 复算 -48.2%） |
| C7 | AgentOccam (GPT-4o): 40.6→41.3，4,025→3,365（-16%） | number | Table 1 | "AgentOccam … 40.6 … 4,025 … 41.3 … 3,365 (-16%)" | source-verified |
| C8 | 消融（WebArena-Lite 165 任务）：48.5/5,410 → +Region4Web 50.3/5,922 → +Self-ctx+§4.2 46.1/4,013 → +PageDigest 53.9/3,814 | number | Table 2; §5.3 | "improving over the backbone by 5.4%p"；"the element-level variant lowers it to 46.1" | source-verified |
| C9 | 论文**未**对 full-observation baseline 施加等 token 预算控制；唯一近似等长对照是 Table 2 中 element-level 变体（4,013）与 PageDigest（3,814） | benchmark-setting | §5.1 全节 + §5.3；全文检索 budget/matched/truncate 无对应设置 | "PageDigest reduces observation length by 30%, comparable to the element-level variant's 26% reduction" | source-verified |
| C10 | 页内只沿用 region purpose、不沿用 state summary；transition 由当前 AXTree 与页面进入时状态比对得到 added/removed/modified | causal-mechanism | §4.2 | "only the region purposes are referenced … State summaries … less suitable for page-aware observation transition management" | source-verified |
| C11 | **GPT-5.1 单 backbone 上**的 task-scale 中位累计 26,707→19,944（-25%）；拆分 actor 73.9% / selection 19.5% / view_all 6.6%；selection 平均 4.8 次/任务，view_all 在 38.1% 任务触发、平均 0.64 次。与 -43% 并列时须注明口径不同：后者是 4 backbone 的 per-step 均值之均值，GPT-5.1 自身的 step-scale 中位为 -33% | number | §5.3 | "median cumulative observation across a task drops by 25%, from 26,707 to 19,944 tokens" | source-verified（口径限定由独立 verifier 补齐） |
| C12 | 50 条失败轨迹多因归因：decomposition 2.0% / abstraction 2.0% / selection 10.0% / transition 0% / actor-side 90.0% / environment 16.0%。同段结论句写的 "82.0% backbone capacity 对 8.0% PageDigest regression" 无法由上列数字导出（pipeline 阶段合计 14.0%） | number | §5.3, Figure 6 | "Actor-side failures … account for 90.0%, with environment errors outside the pipeline adding 16.0%" | source-verified（内部数字不自洽一项由独立 verifier 发现） |
| C13 | 训练数据 21,974 页经 verify 只留 2,052 页（9.3%）、45,147 region；标注器 gpt-5-mini-2025-08-27 | number | §3.4; App E.2 | "reduces 21,967 pages to 2,052 (9.3%) with 46,487 regions"；"yielding 45,147 annotated regions" | source-verified |
| C14 | decomposition 模型约 536K 参数；τ=0.55 时 region-level P/R/F1 = 0.7755/0.7743/0.7749 | number | App F.1; Table 4 | "The model totals approximately 536K parameters including the role embedding table" | source-verified |
| C15 | Mind2Web 前置分析：15,394 对连续 action（78.0% 同页）；LCA depth ratio 中位 0.48 vs random 0.22，81.7% 超 random 中位；52.9% 步骤 DOM 零变化，74.4% <5% | number | §2, §2.1, §2.2 | "median LCA depth ratio of 0.48, with 81.7% exceeding the random baseline median of 0.22"；"52.9% of steps exhibit zero change, and 74.4% remain below 5%" | source-verified |
| C16 | Region4Web 单独使用使观察**变长**（5,410→5,922），压缩全部来自 PageDigest 的 selection + persistence | comparison | Table 2 | "Region4Web alone improves task success rate from 48.5% to 50.3% with comparable observation length" | source-verified |
| C17 | 域级回退：AgentOccam GitLab 66.7→50.0（-16.7pp）；SteP CMS 45.7→37.1、Reddit 71.4→63.2；Qwen CMS 53.8→46.2、Map 22.9→18.9 | number | Table 1 | 见 Table 1 各域列 | source-verified |
| C18 | 代码开源于 https://github.com/kwondu/region4web ；论文 CC BY 4.0 | license-code | Abstract 末尾脚注；arXiv license 行 | "Code is available at https://github.com/kwondu/region4web" | source-verified |

## Strengths & Weaknesses

### Strengths

**问题 formulation 是真的**。"observation 粒度应与 action 粒度解耦"这句话本身值一篇论文——它把一个被所有 web agent harness 默认继承下来的实现细节（AXTree 展平 → 元素列表 → 同时充当观察与动作空间）重新提为可选设计维度，并给出了一个非平凡的替代答案。这比又一个"过滤掉不相关元素"的压缩方法层次高一级：前者改变了 agent 看世界的单位，后者只改变了看多少。

**前置测量是诚实的动机来源，不是事后包装**。§2 的两条测量（动作局部性、页内变化稀疏性）分别精确对应方法的两半（region 作为构造单元、跨步骤增量维持），且用的是外部数据集（Mind2Web）而非自家评测集，避免了用结论论证动机的循环。LCA depth ratio 还带 random baseline 对照，这在这类"motivating analysis"里算规范的。

**跨步骤持久化的粒度选择有机制论证**。只 cache purpose、不 cache state summary，理由是前者跨步骤稳定而后者描述当前状态——这是从表示的语义属性推出的缓存策略，不是拍脑袋。added 节点单独成组而不并入既有 region（避免污染 purpose）也是同类推理。对 harness 设计而言，"哪部分观察可以跨步骤复用、哪部分必须每步重算"正是核心问题，本文给了一个有理由的切分点。

**架构上的小洞见**：Related Work 里指出 region partition 与常规 tree representation learning 的差别在于 boundary decision 会改变父节点要表示哪些孩子，因而必须联合计算——这解释了为什么是"单次自底向上遍历 + teacher forcing"而不是"先编码再切"。这个论证是干净的。

**开销账做到了 task scale**。多数观察压缩论文只报 per-step 长度，把自己引入的辅助 LLM 调用藏起来。本文明确给出 task-scale 累计（-25%，含 selection 与 view_all 开销）与三方拆分，并交代 selection 平均调 4.8 次、view_all 在 38.1% 任务触发。

### Weaknesses

**（1）最关键：没有 token-budget matched 的对照，"更短且更好"这个联合断言站不住。** Table 1 的每一行对比都是"完整观察 baseline（其自然长度）vs PageDigest（其自然长度）"。缺的对照有两类：

- **把 baseline 压到同等预算**：给 full-AXTree baseline 一个 3.7K token 的截断/随机 region 选择/简单启发式裁剪版本，看它掉多少。没有这个对照，就无法区分"region 粒度带来了信息增益"与"任何合理的裁剪在这个长度下都不会掉点、而 6K token 的完整 AXTree 本身就有 distraction 代价"。后一种解释与 FocusAgent、Prune4Web 一类工作的既有发现完全兼容。
- **把 PageDigest 放大到 baseline 预算**：例如永远展开全部 region（等价于常开 `view_all`），看 SR 是升是降。这能分离"压缩收益"与"结构化收益"。

论文实际施加的控制是：同 backbone、同 BrowserGym 设置、同评测器（GPT-4o）、同 tokenizer（o200k_base）、开源模型统一 temperature 0；AgentOccam 上只替换 observation alignment 而保留 action alignment。**唯一近似等长的对照存在于 Table 2**：element-level 变体 4,013 tokens vs PageDigest 3,814 tokens（-26% vs -30%），46.1 vs 53.9。这条是有说服力的，但它对的是**另一个压缩方法**，不是 full-observation baseline；而且只在 WebArena-Lite 165 任务、单一 backbone（GPT-5.1）上做。`+Region4Web` 那一行（5,922 vs baseline 5,410，+1.8pp）算是全长端的第二个准等长对照，但它同样只有一个 backbone、一个子集。

**（2）主表增益的统计地位不明。** 全文未见重复实验、随机种子、方差、置信区间或显著性检验。WebArena 单域样本量小（Map 域约 109 题、Shopping 约 187 题），+1.7pp（Qwen）这个量级在 812 题上约合 14 题，落在可能的运行间波动内。SteP 的 -0.8pp 与 AgentOccam 的 +0.7pp 论文自己也只敢称 "comparable"。因此更稳妥的读法是：**长度削减是稳健且大幅的（-16% ~ -54%），成功率不劣化是可信的，成功率提升则是弱证据。**

**（3）消融没有拆开方法自己声称的两个组件。** 论文标题级的贡献是"hierarchical decomposition + semantic abstraction"，但 Table 2 没有任何一行只保留其中一个。无法回答：如果用规则（例如 VIPS 或 landmark role）切 region、再让 Qwen3-0.6B 写 purpose，能拿到多少？如果只切 region 不写 abstraction（region selection 直接看子树），又是多少？考虑到 decomposition 模型的 region-level F1 只有 0.775（即约 1/4 的 region 边界与标注不一致），"学出来的切分"相对规则切分的增量究竟有多大，是个真问题。同理，cross-step persistence（§4.2）与 region selection（§4.1）在 PageDigest 内部无法分离。

**（4）训练数据 9.3% 的保留率可能造成方向性偏差**（本条为推测，非论文断言）。verify 阶段"任一 region 不合法即整页丢弃"淘汰了 90.7% 的页面。作者解释为"被淘汰页以真实网站噪声为主"——但这恰恰意味着训练分布偏向**结构干净、可被清晰功能分区**的页面，而现实中最需要 region 化的很可能正是那些混乱页面。Table 3 的类目分布也高度倾斜：Technology & Computing 一类占 674/2,052（32.9%），Travel 只有 29 页、Food & Drink 55 页。这可能与下一条相关。

**（5）域级回退是真实的，且集中在结构密集/导航密集的域。** Table 1 里回退不是零星噪声：AgentOccam 的 GitLab **66.7 → 50.0（-16.7pp）**是全表最大变动；SteP 的 CMS -8.6pp、Reddit -8.2pp 直接把该方法拉成净负；Reddit 在 6 个配置中有 3 个下降（GPT-5.1 -4.6、SteP -8.2、AgentOccam -5.3）；CMS 在 6 个配置中有 3 个下降。反过来，**Shopping 是唯一 6/6 全部改善的域**（Qwen 上 22.9→38.6，+15.7pp）。这个模式是可解释的：商品列表页正是"重复卡片构成的功能区"的教科书场景，而 GitLab / CMS 后台是高密度、弱语义分组、依赖精确元素定位的界面，把非选中 region 折叠成一句 purpose 就等于把 agent 需要的东西藏起来。**论文完全没有讨论这些域级回退**——§5.3 的失败分析是把 50 条轨迹按 pipeline 阶段归类，而不是分析"哪些页面类型上 region 粒度反而有害"。这是本文分析最薄弱的一处。

**（6）失败归因方法本身偏向自证。** "多因归因"下各项之和为 120%，actor-side 占 90% 几乎必然——任何失败轨迹的最后一步都是 actor 选错了动作。把 selection error 与 actor error 分开的判据未给出，而 region selection 本来就是**用 actor 的 backbone 做的**，两者在机制上不可分。作者由此得出 "PageDigest operates as designed" 的结论超出了该证据能支撑的范围。此外 `view_all` 在 38.1% 的任务中被触发，本身就是"digest 在超过三分之一的任务里至少有一次被 agent 判为不够用"的信号，论文只把它当作成本项列出，没有把它当作 digest 充分性的负面指标来讨论。

**（7）适用边界（论文自陈 + 延伸）。** App A 承认：整个方法建立在 AXTree 之上，canvas 渲染或非语义 markup 的页面提供的结构线索弱得多；评测只在 WebArena（其 AXTree fidelity 一致）上做，真实网站 fidelity 参差。延伸一层：WebArena 是 5 个自托管应用的静态镜像，**页面模板数量极为有限**，一个在 253 个真实站点上训练的 decomposition 模型在这 5 个应用上等于面对少数几种反复出现的布局；这既可能低估（分布外）也可能高估（模板简单）真实表现，方向不明。§4.2 以 URL 变化作为 digest 失效信号，在 SPA 上会漏判（§2.2 自己测到 2.5% 的步骤变化率 >90%、归因于 client-side routing——这部分正是 URL 不变但页面全换的情形，而 PageDigest 在这些步骤上不会重建 digest）。

### 对领域的意义

对 web agent harness 设计而言，本文最值得带走的不是那 43%，而是三条可迁移的设计断言：**(a) 观察单位与动作单位可以不同构**；**(b) 观察中有稳定成分（结构/功能）与易变成分（状态），二者的缓存周期应当不同**；**(c) 观察压缩的收益应该在 task-scale 记账，而不是 per-step**。第 (b) 条与 coding agent 侧的 repository context 复用、以及 GUI agent 的 screen state 缓存是同一类问题，值得横向比较。

反过来，本文也暴露了这条线上一个共性的方法论缺口：**观察压缩类工作普遍不做 budget-matched 对照**，导致"压缩带来的增益"与"长上下文本身的 distraction 代价"长期混在一起无法归因。这是 survey 里应当作为横向审计维度提出的。

## Mind Map

```mermaid
mindmap
  root((Region4Web))
    Problem
      观察粒度沿用动作粒度是未审视的默认
      element-level 让功能组织只能被隐式推断
      视觉邻近不等于共享功能目的
      前置测量 动作局部性 LCA 0.48 vs 0.22
      前置测量 页内变化稀疏 52.9% 零变化
    Method
      Hierarchical Decomposition
        边二分类 merge or cut
        单次自底向上遍历
        536K 参数 MLP 区域 F1 0.775
      Semantic Abstraction
        Qwen3-0.6B 生成 purpose 与 state summary
        训练数据 21974 页筛到 2052 页
      PageDigest
        进页面 由 actor backbone 选 region
        选中给完整子树 未选只给 purpose
        页内只沿用 purpose 不沿用 state summary
        增量 diff 而非重建 URL 变化才失效
        view all 兜底 38.1% 任务触发
    Results
      四 backbone 平均 6437 到 3671 减 43%
      成功率平均 加 2.3pp 单个 1.7 到 3.0
      SteP 减 0.8pp AgentOccam 加 0.7pp
      task scale 含开销后净减 25%
      消融 元素级变体 46.1 vs 区域级 53.9
    Caveats
      无等预算对照 只有一处近似等长
      未拆开 decomposition 与 abstraction
      域级回退 GitLab 减 16.7pp CMS Reddit
      依赖 AXTree 语义 canvas 页面失效
