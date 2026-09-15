---
title: "Deep Research / Information-Seeking Agent 专题"
tags: [survey, deep-research, information-seeking, agentic-RL]
date_updated: "2026-09-07"
year_range: 2023-2026
papers_analyzed: 23
keywords: [deep research, information seeking, browsecomp, research agent, search agent]
exclude_tags: [gui-agent, computer-use]
exclude_override_keywords: [browsecomp]
domain_map: AgenticRL
scope: adjacent-non-gui
---

# Deep Research / Information-Seeking Agent 专题

## Overview

Deep Research Agent 的核心任务是持续检索、验证并综合开放网络信息，而不是通过 GUI state transition 完成事务性操作。

原 Web Agent survey 中的 DOM/screenshot observation、web navigation、browser action、web environment、rollback、live execution 与 prompt injection 已并入 [[Topics/CUA-Survey]]。本专题只保留 BrowseComp / GAIA 一类 information-seeking 路线；二者共享浏览器和 Agentic RL 技术，但任务状态、动作空间、verifier 与安全边界不同，不再混成一个 GUI 子方向。

## 技术路线

### 1. Persistent Search + Agentic RL

[[Papers/2507-WebSailor]] 用高不确定性任务合成与 agentic RL 训练 persistent information seeking；[[Papers/2505-WebDancer]]、[[Papers/2508-WebWatcher]] 与 [[Papers/2509-WebSailorV2]] 延续了长程搜索、证据聚合与自我验证路线。该家族的主要瓶颈不是 coordinate grounding，而是搜索空间爆炸、证据冲突、长上下文信用分配和答案可验证性。

把可检索的 procedural skill memory 接进这条自博弈训练环的是 [[Papers/2607-SESA]]：challenger 出题、参数分离的 solver 独占技能检索权，失败 rollout 被蒸馏成带触发条件与 avoidance cue 的 skill 写回一个有上限（800 条、E5 余弦 ≤0.93 准入、helpful−hurt 负值淘汰）的非参数库，检索上下文进入 **on-policy** rollout，因而改变的是计算梯度的轨迹分布而不只是单次推理的条件。七个开放域/多跳 QA 集合的 3,125 道保留题上比 SSP 基线平均高 1.2–3.2 分。真正对本方向有校准价值的是它的 **Off/On 分解**：SESA-Off 与 SESA-On 权重完全相同、只差是否开库，Off 相对 SSP 已保留 1.8 / 2.2 分，重新开库只再加 0.5 / 1.0 分且 dataset 级效果 mixed——在这个设定下 skill memory 的收益主要通过塑形训练期分布实现，部署期检索的残值很小。证据边界必须同时记：全文无种子数、标准差或误差棒（每题 1 条 greedy rollout），效应量与噪声同量级；论文声明 SSP 与 SESA "differs only in the skill path"，但未声明训练步数、token 预算或 prompt 长度匹配，也没有注入等长无关文本的 placebo 对照，因此"增益来自 skill 内容"未被隔离；摘要主打的 bidirectional co-evolution 没有固定 challenger 只变 bank 的实验，论文自己承认动态证据是 correlational（本笔记按假说处理）。另有一条论文未讨论的 pattern：Bamboogle 在 7 个 backbone block 中有 6 个回退，而它恰是最需要新颖分解的集合——检索到的 query template 是否对非模板化分解构成负迁移，值得独立检验。

### 2. 训练信号：outcome 的稀疏性、step credit 与参数空间搜索

长程搜索的监督瓶颈在粒度：一条轨迹上百步，标签只有末端答案的对错。已有工作分三层处理——测 outcome 信号覆盖多大的能力集合、把末端标签拆到步级、在 outcome 完全无信号处另找梯度来源。

[[Papers/2604-PassKT]] 用二维 Pass@(k,T) 把独立采样宽度 `k` 与交互深度 `T` 分开，修正“RL 是否扩展 capability boundary”的静态争论：纯推理 MATH-500 上复现 RLVR boundary 不变；组合式 bridge 检索上，RL 与 base 的 pass curve 在 `k≈4` 交叉，并在 `k=64` 达 0.81 vs 0.77，边界差集为 5:1；同 200 题 SFT 反而收缩边界。更准确的结论不是 RL 天生创造新策略，而是：当 base distribution 已稀疏含有任务奖励的组合策略时，RL 的 probability reweighting 会把有限采样下的可达能力集合扩张。边界是单 7B、10-document BM25、每类 100 题与最多 5 turns，尚不能外推到 open-web。

[[Papers/2608-ABSeeker]] 把“轨迹的标签等于轨迹内每一步的标签”这个默认假设直接测了一遍：8.5K 条训练轨迹上，成功轨迹约 4% 的步骤得分低于基线分，失败轨迹近 10% 的步骤高于基线分，即 outcome-only 监督一边强化成功轨迹里的错步、一边惩罚失败轨迹里真正取到关键证据的步。它的干预利用了搜索任务的一个结构性质——答案一旦已知，任务就是可回溯的：从已验证答案出发跑一个带真实 web search 与 page visit 的反向 ReAct loop，取回一组锚定在实际网页上的 clue，再按固定 rubric 逐步打分（发现或验证正确 clue +0.8、正确排除错误候选 +0.4、误弃正确 clue −0.8，基线 1.0，clip 到 [0, 2.0]），同一份分数既做 SFT 的 loss 权重也做 GRPO 的折扣 step advantage（γ=0.25）。锚点每题离线算一次、训练全程不动，因而不像用模型自身 likelihood 做步级信号那样随 policy 漂移。Qwen3.5-4B 上 BrowseComp 无 context management 37.3、有 55.3；消融里 ABC-GRPO 相对 standard GRPO 是 33.5→37.3（+3.8），ABC-SFT 相对 standard SFT 在 BrowseComp +2.3、xbench-2510 +8.0，但 xbench-2505 反降 1.0。这套信号链的可信度目前压在一个未经校验的评分器上：clue recovery、step scoring 与 benchmark 最终判分共用 DeepSeek-V4-Flash，全文没有人工抽检、标注一致性或 clue precision 分析，rubric 的五个常数与 γ 也没有敏感性分析；两行 GRPO 消融同从 ABC-SFT checkpoint 起跑，standard-SFT × ABC-GRPO 一格缺失。适用前提同样要写清：ABC 成立于“唯一可验证答案 + 约束隐式定义一条有效证据路径”，这正是 BrowseComp 的构造方式。

信号稀疏的极端一端是根本采不出正样本。[[Papers/2608-ZerothOrderSelfEvolve]] 把 self-evolution 的梯度拆成 g_fixed（把轨迹当固定输入的显式 answer-loss 项）与 g_traj（参数变化如何重塑轨迹分布），并指出当一组 rollout 全部失败、reward 取同一常数时 ĝ_RL = 0——难例上 trajectory-level RL 不是效率低，是没有信号。它换的来源是参数空间：每个难例挂一个专属 LoRA，加 Gaussian 扰动后用扰动策略与基线策略在 answer perplexity loss 上的差分估计梯度，越界找到的成功轨迹回填 buffer 做 SFT。关键使能件是把不连续的 correctness reward 换成只在 ground-truth answer token 上的 token-normalized NLL：难例上 BERT-based loss 与 LLM-as-a-Judge loss 都不下降，该 loss 仍收敛。50 个难例上 fixed-trajectory first-order 解出 7 个、RL 解出 16 个、ZO 解出 23 个；304 道训练题中基线 Pass@1 只答对 67 道。同 backbone family、同 search API/parser/decoding/tool budget 的 controlled 设定下，GAIA 平均 47.5（ReAct 23.3、ARPO 38.8），WebWalkerQA 34.8（ReAct 15.5）。两条边界是硬的：answer perplexity loss 需要 gold answer，只有参考答案型 QA 能用；每个难例独立跑 30 轮优化，共享 backbone 前向与 tool-call 缓存之后单例仍在数百秒量级。它与 [[Papers/2604-PassKT]] 不冲突而是接在后面——PassKT 描述的是 base 分布已稀疏含有可奖励策略时的重排，ZO 处理的正是这个前提不成立的那一端。

把总增益拆到组件上的工作目前有三处，三处的结论都对头条组件不利。[[Papers/2606-SenseSearch]] 把 text search、reverse image search 与 image crop 放进同一个 RL 训练的 policy（Qwen2.5-VL-7B + 约 3,000 条 cold-start SFT + BN-GSPO），七个 search-oriented benchmark 平均 57.43；同一张表里还有未训练但同工具集的 agentic zero-shot（35.50）与 Direct Answer（27.70），据此可把增益分解为工具 scaffold +7.80、cold-start SFT +17.56、RL +4.37，RL 只占约 15%。同表另有一条论文未讨论的对照：training-free 的 RAG workflow 对表中每一个模型都优于 agentic workflow（GPT-4o 63.47 vs 60.93、Qwen2.5-VL-7B 50.04 vs 35.50），且 GPT-4o 的 RAG 63.47 高于本文全部 agentic 结果——在这套 benchmark 上，“让 policy 自己决定何时检索”相对固定检索管线是负收益。[[Papers/2608-ABSeeker]] 的头条 55.3 里，+18.0 来自与 credit assignment 完全正交的 context management，ABC 自身的净增益是 +3.8。[[Papers/2607-SESA]] 的 memory-off 对照把技能库增益的大头判给训练期分布塑形。这三次拆分的成本都很低（关掉组件重跑一次，或把未训练但同工具集的 scaffold 摆进同一张表），因此没做拆分的工作，其头条归因应按未验证处理。需要同时记住证据的模态边界：SenseSearch 的对照全在多模态视觉搜索上，本方向其余证据几乎全在纯文本检索，RAG 与 agentic 的这个排序是否在 BrowseComp 族上复现尚未测。

### 3. Delegation 与 Wide Search

[[Papers/2606-SearchSwarm]] 把 Deep Research 拆成 delegation 问题；[[Papers/2602-WideSeekR1]] 证明多 agent 宽度只有在协调本身经过训练后才出现正 scaling；[[Papers/2607-SearchOS]] 用共享状态结构组织搜索过程。与顺序状态强耦合的 GUI navigation 相比，information seeking 更容易分解为并行、只读、低副作用子任务。但可分解性有任务结构前提：[[Papers/2510-ContextFolding]] 的 parallel branching 实验在深度优先的 BrowseComp-Plus 上得到阴性结果（并行分支 0.6133 与单支相当），并行收益应到广度型宽检索任务中寻找——与 Takeaway 2 的条件判断一致。

### 4. Benchmark 与 Verifier

[[Papers/2504-BrowseComp]] 用“答案难找但易验证”的短答案设计减少主观 judge；[[Papers/2311-GAIA]] 覆盖工具使用、浏览与推理；[[Papers/2606-KBrowseComp]] 暴露非英语信息检索鸿沟。[[Papers/2506-DeepResearchAgents]] 提供了该方向的系统 taxonomy。过程级 audit 一侧，[[Papers/2606-AgentTracesToTrust]] 把分散的 retrieval grounding、tool-use safety、memory lineage 与 observability 统一为 execution provenance（typed graph）/ evidence tracing（support 投影）框架，并指出现有 benchmark 只覆盖孤立组件、缺 cross-component provenance、relation annotation 与 recovery-oriented 评测三类缺口——该框架是规范性主张，"记录这些字段能否真提升 audit/recovery"尚无经验验证。

### 5. Context 管理、Corpus Interaction 与长程扩展

长程 search agent 的 context 管理在 2025-2026 年从 heuristic 走向 learned，随后训练问题被形式化，构成一条完整的证据链。heuristic 端，[[Papers/2605-MaskingRegimeMap]] 的系统扫描（9 backbone × 3 retriever）证明 observation masking 的增益是 regime 依赖的：弱 retriever 低平台（+6.2~6.6）、强 retriever × 中等模型达峰（+11.7）、模型饱和时归零转负（−1.1，live-web −4.8），决定因素是 retriever recall × 模型隐式过滤能力的交互而非规模（同尺寸不同训练态增益 +11.7 vs +3.7）。learned 端出现两种 formulation：[[Papers/2510-MemAct]] 把 memory 管理做成可学习的编辑动作（Prune&Write + DCPO 段切分训练，14B 多目标 0.591 超 Qwen3-235B 且 token −51%）；[[Papers/2510-ContextFolding]] 用 branch/return 结构化折叠对齐子任务边界（FoldGRPO token 级 process reward，36B@32K×10 达 BC-Plus 0.620 超 327K ReAct+RL），其消融显示普通 GRPO 会训出反向行为（主轨迹变长、失焦）——folding 行为必须靠显式 process 信号。随后 [[Papers/2512-FoldAct]] 把这条路线的隐疾形式化到 RL 假设层：summary 由 policy 生成并进入未来 observation，使 observation 分布 policy-dependent、非平稳，带来梯度稀释与 self-conditioning 训练崩溃（实测 step 173 崩溃），修复三件套为分离 credit、full-context consistency KL 与选择性段训练（5.19× 提速的稳定版 vs 49.6× 的崩溃版）。三篇的开放问题是稳定化手段（process reward vs consistency loss vs 独立 summary credit）尚无合并对照，且 [[Papers/2512-FoldAct]] 点名批评的是 [[Papers/2510-ContextFolding]]（以 FoldAgent 之名），对 [[Papers/2510-MemAct]] 概念适用但未引用。

第三条路线既不调 heuristic 也不训练压缩函数，而是在几个既有静态策略之间按状态路由。[[Papers/2603-AgentSwing]] 在每个 context 溢出触发点（当前长度超过 128k 上限的比例 r，取 0.2 或 0.4）并行展开 Keep-Last-N（N=5）/ Summary / Discard-All 三条分支，各自在真实环境再走 K 个 turn，然后把三条候选续接连同原始 raw context 交给 agent 自身选一条；路由器就是 agent，没有训练专门的 router，候选集里也没有 folding 或 masking 分支。它配套的 Pass@1 = η·ρ 分解——η 是资源耗尽前抵达终止点的概率、ρ 是抵达后答对的条件概率——解释了静态策略各自的位置：Discard-All 靠小 context 换高 ρ，损失的 η 靠多次 reset 补回；Keep-Last-N 与 Summary 拿 η 输 ρ。其中三件事的校准价值高于方法自身的增量。其一，最好的静态策略随 backbone 与 benchmark 换人：GPT-OSS-120B 的 BrowseComp 上是 Keep-Last-N（52.5），DeepSeek-v3.2 与 Tongyi-DR-30B-A3B 上是 Discard-All（58.0），DeepSeek-v3.2 的 HLE 上又变成 Summary（43.5）。其二，增益不来自“手里有多个候选”：随机路由 51.0 / 56.5 与去掉 lookahead 的 50.0 / 57.0 都低于各自最好的静态策略，k=1 恰好持平，只有 k=3 拉开到 60.0 / 60.5，k=5 回落（作者归因于触碰长度上限）。其三，成本没有被测量：每个触发点是 3 分支 × 3 轮外加一次含全部候选与原始 raw context（按定义 ≥25.6k 或 ≥51.2k token）的路由调用，而全文的成本证据只有一张散点图与“overhead remains modest”，没有 token 计数、触发频次或口径定义，也没有 token-matched / compute-matched 对照；lookahead 的 9 个轮次是否计入 400 轮预算与 Table 2 的平均轮数未说明，因此“190.3 轮 vs Discard-All 297.2 轮”不能直接读作效率证据。增益的统计基础也偏薄：HLE 上三个 backbone 相对最好静态策略只有 +0.7 / +0.9 / +0.4（500 题上 2–5 题之差），aligned 子集只有 122 / 73 / 45 题，全文无置信区间与重复运行。

[[Papers/2607-RARG]] 把 relevance 从“选出哪些 top-k 内容”提升为 corpus interaction 的 execution prior：document score 决定 `rg -j1` 的扫描顺序，query-relevant paragraph 提供 entry point，match-level score 决定哪些局部片段进入有限 observation。100-query / 100K-document BrowseComp-Plus 上，GPT-5.4-mini 的 RARG++ 为 84% / 23.9 tools（RISE 78% / 28.7，DCI 78% / 99.1）；扩到 1M documents 后仍为 79%，但 BRIGHT 上更宽的 RARG+ 反而以 53.36 nDCG@10 优于 RARG++ 50.55。由此可见最佳 relevance granularity 取决于 depth-first QA 还是 breadth-first recall；tool count 也不能替代 wall-clock，因为串行 `rg` 与 embedding reranking 有隐藏 latency。

## Datasets & Benchmarks

| Benchmark | 规模 | 评估指标 | 当前证据 | 特点 |
|:--|:--|:--|:--|:--|
| GAIA ([[Papers/2311-GAIA]]) | 466 tasks | exact / graded accuracy | human 92%，早期 GPT-4+plugins 15%；[[Papers/2608-ZerothOrderSelfEvolve]] Qwen-3-8B 47.5（L1 56.4 / L2 42.3 / L3 41.6，controlled 同工具配置）；GAIA-text 子集上 [[Papers/2608-ABSeeker]] 4B 81.6 | 通用工具与浏览任务；GAIA 与 GAIA-text 不是同一评测面，各文所用 split 也未必一致，跨论文不可直接并列 |
| BrowseComp ([[Papers/2504-BrowseComp]]) | 1,266 questions | exact answer accuracy | WebSailor-72B 12.0% en；V2 35.3%；[[Papers/2608-ABSeeker]] 4B 37.3（无 context management）/ 55.3（有）；[[Papers/2603-AgentSwing]] 200 题随机子集 60.0 / 62.5 / 60.5（三 backbone，LLM judge） | 难找、易验证、高不确定性；是否启用 context management 与是否全量评测都会移动十几个点，横比须先对齐这两项 |
| BrowseComp-ZH | BrowseComp 中文版 | accuracy | WebSailor-72B 30.1%；V2 44.1%；[[Papers/2608-ABSeeker]] 4B 39.1（无 CM）/ 52.9（有）；[[Papers/2603-AgentSwing]] 全量 289 题 38.0 / 71.3 / 56.7 | 中英文难度与语料差异；backbone 差异在此列比方法差异更大 |
| HLE（text-only 子集） | 500 道 text-only 题 | LLM-as-a-Judge accuracy | [[Papers/2603-AgentSwing]] 三 backbone 35.1 / 44.4 / 33.1，相对最好静态 CM 策略仅 +0.7 / +0.9 / +0.4 | 非检索主导的难题；额外配 Google Scholar 与 Python interpreter，context 管理类干预在此增益最小 |
| HR-MMSearch ([[Papers/2606-SenseSearch]]) | 305 张 4K 图像，8 domain，取自 2025 年事件 | GPT-4o judge Pass@1 | SenseSearch-RL 7B 38.52（自身 SFT 29.80、MMSearch-R1 20.33、未训练同工具集 base 19.34） | 多模态检索与小目标细粒度感知压在同一题上；未报题目总数、标注一致性与人类上限，分差无法换算成题数 |
| K-BrowseComp ([[Papers/2606-KBrowseComp]]) | 400 Korean questions | accuracy | GPT-5.5 45.67% | 非英语与本土知识鸿沟 |
| BrowseComp-Plus | BrowseComp + verified corpus | Pass@1 / accuracy | 36B folding 0.620（自切 split）；RARG++ 100-query sample 84%（GPT-5.1 judge） | 离线可控检索语料；各文 split / judge 不一，横比需谨慎 |
| 开放域 / 多跳 QA 七集合（NQ / TriviaQA / PopQA / HotpotQA / 2Wiki / MuSiQue / Bamboogle） | 3,125 保留题（前六集各 500 + Bamboogle 125） | 归一化 EM，未命中转 32B judge 语义等价，七集等权平均 | [[Papers/2607-SESA]] Qwen3-8B 59.5（SSP 56.3 / base 52.5）；Search-R1-7B 初始化 57.5 | self-play 训练环的常用评测面，难度与检索开放度远低于 BrowseComp 族；单点估计无方差，跨论文横比需同搜索后端与同 judge |

## Key Takeaways

1. **Deep Research 与 GUI operation 是两种不同的 web agent。** 前者优化搜索、证据与答案，后者优化可执行状态转移与副作用控制；把二者混合会让 benchmark、reward 与安全结论失真。
2. **现有 wide-search 证据中，多 agent 并行只在任务可分解且协调被训练时可靠。** 宽检索满足低副作用、子问题近似独立的条件，因此比 GUI navigation 更可能受益；未训练的 delegation 仍会放大错误；深度优先任务上并行分支实测无增益（[[Papers/2510-ContextFolding]]）。
3. **“易验证答案”降低了 outcome judge 难度，却没有解决证据忠实性。** exact answer 正确不保证引用链完整、时效性正确或没有遗漏冲突来源，过程级 evidence audit 仍是开放问题；[[Papers/2606-AgentTracesToTrust]] 提供了该问题的统一框架（execution provenance / evidence tracing），但落地评测尚缺。
4. **Context 管理是 regime 依赖的干预，learned 路线有效但训练脆弱，而静态策略之间没有单一赢家。** heuristic masking 的增益随"retriever recall × 模型过滤能力"呈倒 U，模型饱和时转负（[[Papers/2605-MaskingRegimeMap]]）；learned 路线（编辑动作 [[Papers/2510-MemAct]] / 结构化折叠 [[Papers/2510-ContextFolding]]）能以小上下文超大上下文 baseline，但 summary 进入未来 observation 造成的非平稳性会导致训练崩溃，必须配显式稳定化手段（process reward / consistency 正则 / 独立 summary credit，[[Papers/2512-FoldAct]]）。第三条路线不训练任何东西，只在既有静态策略之间按状态路由：[[Papers/2603-AgentSwing]] 的三分支 lookahead 在 BrowseComp 上超过各自最好的静态策略（60.0 / 62.5 / 60.5），而最好的静态策略本身随 backbone 与 benchmark 换人（Keep-Last-N / Discard-All / Summary 各有胜出场景）——这是“全程固定一种压缩函数”不成立的直接证据。但它的增益只在 k=3 前瞻下出现，随机路由与去掉 lookahead 都跌回最好静态策略之下，而每个触发点把推理量放大近一个数量级却无任何 token 或 compute 对齐对照，因此当前只能引为“静态策略无单一赢家”，不能引为“自适应路由划算”。
5. **Relevance 不只决定“给什么”，也可以决定 agent“先做什么、先看见什么”。** [[Papers/2607-RARG]] 的核心增量是把 ranking 变成 traversal 与 match visibility 的 control primitive；但最细粒度 guidance 并非普遍最好，RARG++ 在 BRIGHT 输给 RARG+，说明系统需要按任务结构与剩余 budget 动态选择 breadth/depth，而非固定 top-k 或固定 reranking 深度。
6. **RL capability expansion 是 task structure × policy support 的条件命题。** [[Papers/2604-PassKT]] 在静态推理上复现 boundary 不变、在组合 bridge 检索上观察到曲线分离，并与既有 headroom 判据同向；“先测 base 是否稀疏包含可奖励策略、任务是否需要交互深度”应成为投入 agentic RL 前的 gate。这个条件的极端一端由 [[Papers/2608-ZerothOrderSelfEvolve]] 补上：当一组 rollout 全部失败、reward 同为常数时 trajectory-level 梯度严格为 0，难例上 RL 不是收敛慢而是无信号；改从参数空间取信号（instance-specific LoRA 扰动 + answer perplexity 差分）后，50 个难例解出 23 个，对照 RL 16 个、fixed-trajectory first-order 7 个。代价是必须有 gold answer，且每题独立优化。
7. **外部技能记忆的收益可能主要落在训练期，而非部署期检索。** [[Papers/2607-SESA]] 是本方向目前唯一做了 memory-off 对照的工作：同一份权重下关掉技能库仍保留大部分增益（1.8 / 2.2 分），开库只再加 0.5 / 1.0 分且 dataset 级 mixed。这与 §5 的 context 管理形成对照——后者的干预在推理期直接生效，前者更像一种课程/数据塑形手段。**这是单篇、无方差、无算力匹配对照的证据，不构成共识**；但它足以把"Off/On 分解"立为该类工作的默认报告项，否则无法排除"skill 只是训练期数据塑形"这一更简洁的解释。
8. **末端标签在步级上确实错，错的比例可测；但修正它目前买到的增益小于上下文管理。** [[Papers/2608-ABSeeker]] 在 8.5K 条训练轨迹上量出成功轨迹约 4% 的步骤低于基线分、失败轨迹近 10% 高于基线分，把“outcome-only 监督在强化错步、惩罚有效取证步”从直觉变成数字；按回溯 clue 打的 step reward 让 ABC-GRPO 相对 standard GRPO 在 BrowseComp 得 +3.8。但同一系统上，与 credit assignment 正交的 context management 贡献 +18.0（37.3→55.3），[[Papers/2603-AgentSwing]] 一侧从无 CM 的 39.5 到最好静态策略 52.5 也是同量级。两处都是系统内自比、都集中在 BrowseComp，不构成跨方法排序；能立住的只是排预算顺序时的先验：长程 search 的边际瓶颈目前更靠近上下文而非步级信用。
9. **头条组件的增益份额要拆一次才知道，而已有的三次拆分都对头条不利。** [[Papers/2606-SenseSearch]] 的表里工具 scaffold +7.80、cold-start SFT +17.56、RL +4.37，RL 只占约 15%，而标题与摘要以 RL 为中心；同表 training-free 的 RAG workflow 对每一个模型都优于 agentic workflow（GPT-4o 63.47 vs 60.93），说明“让 policy 自己决定何时检索”在该 benchmark 组上是负收益，论文未讨论。[[Papers/2608-ABSeeker]] 的头条 55.3 里 +18.0 归 context management。[[Papers/2607-SESA]] 的 memory-off 对照把技能库增益大头归训练期塑形。三次拆分的成本都只是关掉组件重跑一次或多摆一条 baseline，因此没有拆分的工作，其头条归因应按未验证处理。SenseSearch 的对照限于多模态视觉搜索，纯文本检索上是否同样 RAG 压过 agentic 未测。

## Open Problems

1. 证据 provenance、冲突消解与时间敏感事实的持续校准。
2. 在固定 token / latency / search budget 下训练有效 delegation，而不是无约束扩大 agent 数量。
3. 非英语、区域性网站、登录后内容与付费墙造成的系统性覆盖偏差。
4. 将答案正确性、引用忠实性和搜索成本统一成可验证且不易 reward-hack 的目标。
5. Context 管理的稳定化手段（token 级 process reward、full-context consistency 正则、分离 summary credit）来自不同论文、不同 benchmark，尚无同环境合并对照；learned 策略能否自适应定位 masking 的有效 regime（替代人工探针）亦未测。
6. 根据 query decomposition、scope uncertainty、match diversity 与剩余 budget，动态选择 document-only / entry-point / match-level relevance granularity；并用 wall-clock、embedding cost 与 answer accuracy 做同口径 Pareto，而非只数 tool calls。
7. 用 Pass@(k,T) 在 open-web、多 backbone、更长 horizon 上区分“成功率提高”“采样效率提高”与“能力边界扩张”，并报告有限 `n` 对极限集合估计的置信区间。
8. 技能记忆的收益归属需要 placebo 与算力匹配对照：注入等长但无关的结构化文本能复现多少增益？在匹配训练步数与 token 预算后，[[Papers/2607-SESA]] 的 1.2–3.2 分还剩多少？以及 procedural skill 对需要新颖分解的任务（Bamboogle 6/7 回退）是否存在系统性负迁移。
9. Context-management 路由需要一次算力对齐审计：把静态策略的预算提到与 [[Papers/2603-AgentSwing]] 同一水平（更大触发比例 r、更多 reset、或对同一策略并行多轨迹取优）后，60.0 是否仍领先；以及 lookahead 的价值来自“看到了下游环境反馈”还是仅仅“多跑了 9 轮探索”——k=1 持平、k=3 拉开这个形状同时符合两种解释。
10. 步级 reward 的评分器本身缺校验：[[Papers/2608-ABSeeker]] 的 clue recovery、step scoring 与 benchmark 判分共用同一个 LLM，全文无人工抽检、无 clue precision、无 rubric 常数与 γ 的敏感性分析。另一个未测的风险是回溯锚点只是一条事后合理化的证据路径，“误弃正确 clue −0.8”会不会惩罚那些经另一条路径到达同一答案的轨迹。
11. 无 gold answer 的场景如何构造连续 surrogate 信号：[[Papers/2608-ZerothOrderSelfEvolve]] 的越界搜索依赖 answer perplexity，开放式 research、无参考答案的综合任务与只有环境 reward 的操作型任务都不能直接照搬；此外 instance-specific LoRA 蒸馏回主模型的损失有多大，论文未量化。
12. 多模态 information seeking 在本方向近乎空白：[[Papers/2606-SenseSearch]] 观察到的“training-free RAG 全面优于 agentic workflow”是否在 BrowseComp 族这类纯文本、深度优先的任务上复现？若复现，agentic 自主 routing 相对固定检索管线的必要性需要重新论证；若不复现，则说明该现象由视觉检索的工具收益结构决定。

## 调研日志

### 2026-07-21 与 GUI 主 survey 解耦

- **迁移**：GUI navigation、browser interaction、web environment、rollback、verification 与 web safety 已并入 [[Topics/CUA-Survey]]。
- **保留**：Deep Research / information-seeking 作为非 GUI 邻接方向，保留 11 篇代表论文与独立 routing keywords。

### 2026-07-29 增量更新（survey-refresh）

- **并入**：[[Papers/2604-PassKT]]（RL capability boundary 的 `k×T` 条件化测量）与 [[Papers/2607-RARG]]（relevance as execution control）。
- **变化**：§1 把 RL 增益改写为 task structure × policy support 条件命题；§4 扩为 Context + Corpus Interaction，补 traversal/visibility 控制；Takeaways +2、Open Problems +2；无新平行 taxonomy。
- **验证边界**：两篇均 source-checked；PassKT 限单 7B/小 corpus/短 horizon，RARG 主表限 100-query + GPT-5.1 judge，未外推为 open-web 共识。

### 2026-08-04 增量更新（survey-refresh）

- **并入**：[[Papers/2607-SESA]]（self-play 搜索 agent + 可检索 procedural skill memory）。
- **变化**：§1 补一段 SESA 及其 Off/On 分解；Benchmarks 表新增"开放域/多跳 QA 七集合"一行（与 BrowseComp 族的难度与开放度差异写明）；Takeaways +1（技能记忆的收益归属）、Open Problems +1（placebo 与算力匹配对照）。无新平行 taxonomy。
- **验证边界**：SESA 为 `partial` 核查——C10（bidirectional co-evolution 有隔离实验）与 C11（增益经算力/token 匹配隔离）判为 `unsupported`，正文均未采用，只写成架构描述与未隔离的假说；C16 显示全文无种子/标准差/误差棒，1.2–3.2 分的效应量与噪声同量级；Table 4 对 SkillRL 的 +0.9 是单 family、单 checkpoint、单次运行。Off/On 分解结论标注为单篇证据，未升格为共识。
- **domain_map**：skipped（单篇、且其核心机制断言未被隔离，不构成 [[DomainMaps/AgenticRL]] 的格局级变化）。

### 2026-09-07 增量更新（survey-refresh）

- **并入**：[[Papers/2608-ABSeeker]]（answer-backtracked step credit）、[[Papers/2608-ZerothOrderSelfEvolve]]（参数空间 ZO 越界搜索）、[[Papers/2606-SenseSearch]]（多模态 search-crop 统一 policy，含增益分解与 RAG 对照）、[[Papers/2603-AgentSwing]]（context management 的状态路由）。
- **结构变化**：新建 §2「训练信号」——把原 §1 的 [[Papers/2604-PassKT]] 段落移入，与 ABSeeker、ZerothOrderSelfEvolve、SenseSearch 的归因分解合成一条完整链（测能力集合 → 拆步级信用 → outcome 无信号时换来源 → 组件归因），原 §2–§4 顺延为 §3–§5；Takeaway 7 内的 §4 交叉引用改为 §5。AgentSwing 进 §5 并把该节从"heuristic / learned"两条路线扩为三条（增加"不训练、按状态路由"）。Benchmarks 表新增 HLE 与 HR-MMSearch 两行，并给 GAIA / BrowseComp / BrowseComp-ZH 三行补当前证据与 setting 对齐提示。Takeaways 4 与 6 改写，新增 8、9；Open Problems 新增 9–12。
- **验证边界**：ABSeeker、ZerothOrderSelfEvolve、SenseSearch 为 `source-checked`，AgentSwing 为 `partial`（本轮所用行均为 `source-verified`）。ABSeeker 的 +3.8 与 +18.0、AgentSwing 的静态策略漂移与 k 消融、ZO 的 23/16/7 与 GAIA 47.5、SenseSearch 的 +7.80/+17.56/+4.37 与 RAG 对照均对应 ledger 中 source-verified 行。SenseSearch 的 HR-Bench 8K（69.8 < GPT-4o 70.4）与 tool-call "~4→2"（RL 训练曲线而非推理效率，评测期调用数为 base 的 1.6–49×）两处旧误未进正文。AgentSwing 与 SenseSearch 的成本论断一律按"未测量"写，不写成已被排除。
- **domain_map**：候选写入 staging——三条格局级变化（trajectory-level RL 在难例上梯度严格为零，参数空间成为第三个信号源；组件归因分解在本方向连续三次对头条组件不利，并新增"对照就摆在同一张表里却未被讨论"这一形态；context management 的问题形态从"学哪个压缩函数"变为"选择本身是对象"，但自适应路由的成本仍未审计）。
