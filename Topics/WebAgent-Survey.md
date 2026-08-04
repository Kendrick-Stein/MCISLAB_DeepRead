---
title: "Deep Research / Information-Seeking Agent 专题"
tags: [survey, deep-research, information-seeking, agentic-RL]
date_updated: "2026-08-04"
year_range: 2023-2026
papers_analyzed: 19
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

[[Papers/2604-PassKT]] 用二维 Pass@(k,T) 把独立采样宽度 `k` 与交互深度 `T` 分开，修正“RL 是否扩展 capability boundary”的静态争论：纯推理 MATH-500 上复现 RLVR boundary 不变；组合式 bridge 检索上，RL 与 base 的 pass curve 在 `k≈4` 交叉，并在 `k=64` 达 0.81 vs 0.77，边界差集为 5:1；同 200 题 SFT 反而收缩边界。更准确的结论不是 RL 天生创造新策略，而是：当 base distribution 已稀疏含有任务奖励的组合策略时，RL 的 probability reweighting 会把有限采样下的可达能力集合扩张。边界是单 7B、10-document BM25、每类 100 题与最多 5 turns，尚不能外推到 open-web。

把可检索的 procedural skill memory 接进这条自博弈训练环的是 [[Papers/2607-SESA]]：challenger 出题、参数分离的 solver 独占技能检索权，失败 rollout 被蒸馏成带触发条件与 avoidance cue 的 skill 写回一个有上限（800 条、E5 余弦 ≤0.93 准入、helpful−hurt 负值淘汰）的非参数库，检索上下文进入 **on-policy** rollout，因而改变的是计算梯度的轨迹分布而不只是单次推理的条件。七个开放域/多跳 QA 集合的 3,125 道保留题上比 SSP 基线平均高 1.2–3.2 分。真正对本方向有校准价值的是它的 **Off/On 分解**：SESA-Off 与 SESA-On 权重完全相同、只差是否开库，Off 相对 SSP 已保留 1.8 / 2.2 分，重新开库只再加 0.5 / 1.0 分且 dataset 级效果 mixed——在这个设定下 skill memory 的收益主要通过塑形训练期分布实现，部署期检索的残值很小。证据边界必须同时记：全文无种子数、标准差或误差棒（每题 1 条 greedy rollout），效应量与噪声同量级；论文声明 SSP 与 SESA "differs only in the skill path"，但未声明训练步数、token 预算或 prompt 长度匹配，也没有注入等长无关文本的 placebo 对照，因此"增益来自 skill 内容"未被隔离；摘要主打的 bidirectional co-evolution 没有固定 challenger 只变 bank 的实验，论文自己承认动态证据是 correlational（本笔记按假说处理）。另有一条论文未讨论的 pattern：Bamboogle 在 7 个 backbone block 中有 6 个回退，而它恰是最需要新颖分解的集合——检索到的 query template 是否对非模板化分解构成负迁移，值得独立检验。

### 2. Delegation 与 Wide Search

[[Papers/2606-SearchSwarm]] 把 Deep Research 拆成 delegation 问题；[[Papers/2602-WideSeekR1]] 证明多 agent 宽度只有在协调本身经过训练后才出现正 scaling；[[Papers/2607-SearchOS]] 用共享状态结构组织搜索过程。与顺序状态强耦合的 GUI navigation 相比，information seeking 更容易分解为并行、只读、低副作用子任务。但可分解性有任务结构前提：[[Papers/2510-ContextFolding]] 的 parallel branching 实验在深度优先的 BrowseComp-Plus 上得到阴性结果（并行分支 0.6133 与单支相当），并行收益应到广度型宽检索任务中寻找——与 Takeaway 2 的条件判断一致。

### 3. Benchmark 与 Verifier

[[Papers/2504-BrowseComp]] 用“答案难找但易验证”的短答案设计减少主观 judge；[[Papers/2311-GAIA]] 覆盖工具使用、浏览与推理；[[Papers/2606-KBrowseComp]] 暴露非英语信息检索鸿沟。[[Papers/2506-DeepResearchAgents]] 提供了该方向的系统 taxonomy。过程级 audit 一侧，[[Papers/2606-AgentTracesToTrust]] 把分散的 retrieval grounding、tool-use safety、memory lineage 与 observability 统一为 execution provenance（typed graph）/ evidence tracing（support 投影）框架，并指出现有 benchmark 只覆盖孤立组件、缺 cross-component provenance、relation annotation 与 recovery-oriented 评测三类缺口——该框架是规范性主张，"记录这些字段能否真提升 audit/recovery"尚无经验验证。

### 4. Context 管理、Corpus Interaction 与长程扩展

长程 search agent 的 context 管理在 2025-2026 年从 heuristic 走向 learned，随后训练问题被形式化，构成一条完整的证据链。heuristic 端，[[Papers/2605-MaskingRegimeMap]] 的系统扫描（9 backbone × 3 retriever）证明 observation masking 的增益是 regime 依赖的：弱 retriever 低平台（+6.2~6.6）、强 retriever × 中等模型达峰（+11.7）、模型饱和时归零转负（−1.1，live-web −4.8），决定因素是 retriever recall × 模型隐式过滤能力的交互而非规模（同尺寸不同训练态增益 +11.7 vs +3.7）。learned 端出现两种 formulation：[[Papers/2510-MemAct]] 把 memory 管理做成可学习的编辑动作（Prune&Write + DCPO 段切分训练，14B 多目标 0.591 超 Qwen3-235B 且 token −51%）；[[Papers/2510-ContextFolding]] 用 branch/return 结构化折叠对齐子任务边界（FoldGRPO token 级 process reward，36B@32K×10 达 BC-Plus 0.620 超 327K ReAct+RL），其消融显示普通 GRPO 会训出反向行为（主轨迹变长、失焦）——folding 行为必须靠显式 process 信号。随后 [[Papers/2512-FoldAct]] 把这条路线的隐疾形式化到 RL 假设层：summary 由 policy 生成并进入未来 observation，使 observation 分布 policy-dependent、非平稳，带来梯度稀释与 self-conditioning 训练崩溃（实测 step 173 崩溃），修复三件套为分离 credit、full-context consistency KL 与选择性段训练（5.19× 提速的稳定版 vs 49.6× 的崩溃版）。三篇的开放问题是稳定化手段（process reward vs consistency loss vs 独立 summary credit）尚无合并对照，且 [[Papers/2512-FoldAct]] 点名批评的是 [[Papers/2510-ContextFolding]]（以 FoldAgent 之名），对 [[Papers/2510-MemAct]] 概念适用但未引用。

[[Papers/2607-RARG]] 把 relevance 从“选出哪些 top-k 内容”提升为 corpus interaction 的 execution prior：document score 决定 `rg -j1` 的扫描顺序，query-relevant paragraph 提供 entry point，match-level score 决定哪些局部片段进入有限 observation。100-query / 100K-document BrowseComp-Plus 上，GPT-5.4-mini 的 RARG++ 为 84% / 23.9 tools（RISE 78% / 28.7，DCI 78% / 99.1）；扩到 1M documents 后仍为 79%，但 BRIGHT 上更宽的 RARG+ 反而以 53.36 nDCG@10 优于 RARG++ 50.55。由此可见最佳 relevance granularity 取决于 depth-first QA 还是 breadth-first recall；tool count 也不能替代 wall-clock，因为串行 `rg` 与 embedding reranking 有隐藏 latency。

## Datasets & Benchmarks

| Benchmark | 规模 | 评估指标 | 当前证据 | 特点 |
|:--|:--|:--|:--|:--|
| GAIA ([[Papers/2311-GAIA]]) | 466 tasks | exact / graded accuracy | human 92%，早期 GPT-4+plugins 15% | 通用工具与浏览任务 |
| BrowseComp ([[Papers/2504-BrowseComp]]) | 1,266 questions | exact answer accuracy | WebSailor-72B 12.0% en；V2 35.3% | 难找、易验证、高不确定性 |
| BrowseComp-ZH | BrowseComp 中文版 | accuracy | WebSailor-72B 30.1%；V2 44.1% | 中英文难度与语料差异 |
| K-BrowseComp ([[Papers/2606-KBrowseComp]]) | 400 Korean questions | accuracy | GPT-5.5 45.67% | 非英语与本土知识鸿沟 |
| BrowseComp-Plus | BrowseComp + verified corpus | Pass@1 / accuracy | 36B folding 0.620（自切 split）；RARG++ 100-query sample 84%（GPT-5.1 judge） | 离线可控检索语料；各文 split / judge 不一，横比需谨慎 |
| 开放域 / 多跳 QA 七集合（NQ / TriviaQA / PopQA / HotpotQA / 2Wiki / MuSiQue / Bamboogle） | 3,125 保留题（前六集各 500 + Bamboogle 125） | 归一化 EM，未命中转 32B judge 语义等价，七集等权平均 | [[Papers/2607-SESA]] Qwen3-8B 59.5（SSP 56.3 / base 52.5）；Search-R1-7B 初始化 57.5 | self-play 训练环的常用评测面，难度与检索开放度远低于 BrowseComp 族；单点估计无方差，跨论文横比需同搜索后端与同 judge |

## Key Takeaways

1. **Deep Research 与 GUI operation 是两种不同的 web agent。** 前者优化搜索、证据与答案，后者优化可执行状态转移与副作用控制；把二者混合会让 benchmark、reward 与安全结论失真。
2. **现有 wide-search 证据中，多 agent 并行只在任务可分解且协调被训练时可靠。** 宽检索满足低副作用、子问题近似独立的条件，因此比 GUI navigation 更可能受益；未训练的 delegation 仍会放大错误；深度优先任务上并行分支实测无增益（[[Papers/2510-ContextFolding]]）。
3. **“易验证答案”降低了 outcome judge 难度，却没有解决证据忠实性。** exact answer 正确不保证引用链完整、时效性正确或没有遗漏冲突来源，过程级 evidence audit 仍是开放问题；[[Papers/2606-AgentTracesToTrust]] 提供了该问题的统一框架（execution provenance / evidence tracing），但落地评测尚缺。
4. **Context 管理是 regime 依赖的干预，learned 路线有效但训练脆弱。** heuristic masking 的增益随"retriever recall × 模型过滤能力"呈倒 U，模型饱和时转负（[[Papers/2605-MaskingRegimeMap]]）；learned 路线（编辑动作 [[Papers/2510-MemAct]] / 结构化折叠 [[Papers/2510-ContextFolding]]）能以小上下文超大上下文 baseline，但 summary 进入未来 observation 造成的非平稳性会导致训练崩溃，必须配显式稳定化手段（process reward / consistency 正则 / 独立 summary credit，[[Papers/2512-FoldAct]]）。
5. **Relevance 不只决定“给什么”，也可以决定 agent“先做什么、先看见什么”。** [[Papers/2607-RARG]] 的核心增量是把 ranking 变成 traversal 与 match visibility 的 control primitive；但最细粒度 guidance 并非普遍最好，RARG++ 在 BRIGHT 输给 RARG+，说明系统需要按任务结构与剩余 budget 动态选择 breadth/depth，而非固定 top-k 或固定 reranking 深度。
6. **RL capability expansion 是 task structure × policy support 的条件命题。** [[Papers/2604-PassKT]] 在静态推理上复现 boundary 不变、在组合 bridge 检索上观察到曲线分离，并与既有 headroom 判据同向；“先测 base 是否稀疏包含可奖励策略、任务是否需要交互深度”应成为投入 agentic RL 前的 gate。
7. **外部技能记忆的收益可能主要落在训练期，而非部署期检索。** [[Papers/2607-SESA]] 是本方向目前唯一做了 memory-off 对照的工作：同一份权重下关掉技能库仍保留大部分增益（1.8 / 2.2 分），开库只再加 0.5 / 1.0 分且 dataset 级 mixed。这与 §4 的 context 管理形成对照——后者的干预在推理期直接生效，前者更像一种课程/数据塑形手段。**这是单篇、无方差、无算力匹配对照的证据，不构成共识**；但它足以把"Off/On 分解"立为该类工作的默认报告项，否则无法排除"skill 只是训练期数据塑形"这一更简洁的解释。

## Open Problems

1. 证据 provenance、冲突消解与时间敏感事实的持续校准。
2. 在固定 token / latency / search budget 下训练有效 delegation，而不是无约束扩大 agent 数量。
3. 非英语、区域性网站、登录后内容与付费墙造成的系统性覆盖偏差。
4. 将答案正确性、引用忠实性和搜索成本统一成可验证且不易 reward-hack 的目标。
5. Context 管理的稳定化手段（token 级 process reward、full-context consistency 正则、分离 summary credit）来自不同论文、不同 benchmark，尚无同环境合并对照；learned 策略能否自适应定位 masking 的有效 regime（替代人工探针）亦未测。
6. 根据 query decomposition、scope uncertainty、match diversity 与剩余 budget，动态选择 document-only / entry-point / match-level relevance granularity；并用 wall-clock、embedding cost 与 answer accuracy 做同口径 Pareto，而非只数 tool calls。
7. 用 Pass@(k,T) 在 open-web、多 backbone、更长 horizon 上区分“成功率提高”“采样效率提高”与“能力边界扩张”，并报告有限 `n` 对极限集合估计的置信区间。
8. 技能记忆的收益归属需要 placebo 与算力匹配对照：注入等长但无关的结构化文本能复现多少增益？在匹配训练步数与 token 预算后，[[Papers/2607-SESA]] 的 1.2–3.2 分还剩多少？以及 procedural skill 对需要新颖分解的任务（Bamboogle 6/7 回退）是否存在系统性负迁移。

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
