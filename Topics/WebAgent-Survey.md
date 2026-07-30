---
title: "Deep Research / Information-Seeking Agent 专题"
tags: [survey, deep-research, information-seeking, agentic-RL]
date_updated: "2026-07-29"
year_range: 2023-2026
papers_analyzed: 18
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

## Key Takeaways

1. **Deep Research 与 GUI operation 是两种不同的 web agent。** 前者优化搜索、证据与答案，后者优化可执行状态转移与副作用控制；把二者混合会让 benchmark、reward 与安全结论失真。
2. **现有 wide-search 证据中，多 agent 并行只在任务可分解且协调被训练时可靠。** 宽检索满足低副作用、子问题近似独立的条件，因此比 GUI navigation 更可能受益；未训练的 delegation 仍会放大错误；深度优先任务上并行分支实测无增益（[[Papers/2510-ContextFolding]]）。
3. **“易验证答案”降低了 outcome judge 难度，却没有解决证据忠实性。** exact answer 正确不保证引用链完整、时效性正确或没有遗漏冲突来源，过程级 evidence audit 仍是开放问题；[[Papers/2606-AgentTracesToTrust]] 提供了该问题的统一框架（execution provenance / evidence tracing），但落地评测尚缺。
4. **Context 管理是 regime 依赖的干预，learned 路线有效但训练脆弱。** heuristic masking 的增益随"retriever recall × 模型过滤能力"呈倒 U，模型饱和时转负（[[Papers/2605-MaskingRegimeMap]]）；learned 路线（编辑动作 [[Papers/2510-MemAct]] / 结构化折叠 [[Papers/2510-ContextFolding]]）能以小上下文超大上下文 baseline，但 summary 进入未来 observation 造成的非平稳性会导致训练崩溃，必须配显式稳定化手段（process reward / consistency 正则 / 独立 summary credit，[[Papers/2512-FoldAct]]）。
5. **Relevance 不只决定“给什么”，也可以决定 agent“先做什么、先看见什么”。** [[Papers/2607-RARG]] 的核心增量是把 ranking 变成 traversal 与 match visibility 的 control primitive；但最细粒度 guidance 并非普遍最好，RARG++ 在 BRIGHT 输给 RARG+，说明系统需要按任务结构与剩余 budget 动态选择 breadth/depth，而非固定 top-k 或固定 reranking 深度。
6. **RL capability expansion 是 task structure × policy support 的条件命题。** [[Papers/2604-PassKT]] 在静态推理上复现 boundary 不变、在组合 bridge 检索上观察到曲线分离，并与既有 headroom 判据同向；“先测 base 是否稀疏包含可奖励策略、任务是否需要交互深度”应成为投入 agentic RL 前的 gate。

## Open Problems

1. 证据 provenance、冲突消解与时间敏感事实的持续校准。
2. 在固定 token / latency / search budget 下训练有效 delegation，而不是无约束扩大 agent 数量。
3. 非英语、区域性网站、登录后内容与付费墙造成的系统性覆盖偏差。
4. 将答案正确性、引用忠实性和搜索成本统一成可验证且不易 reward-hack 的目标。
5. Context 管理的稳定化手段（token 级 process reward、full-context consistency 正则、分离 summary credit）来自不同论文、不同 benchmark，尚无同环境合并对照；learned 策略能否自适应定位 masking 的有效 regime（替代人工探针）亦未测。
6. 根据 query decomposition、scope uncertainty、match diversity 与剩余 budget，动态选择 document-only / entry-point / match-level relevance granularity；并用 wall-clock、embedding cost 与 answer accuracy 做同口径 Pareto，而非只数 tool calls。
7. 用 Pass@(k,T) 在 open-web、多 backbone、更长 horizon 上区分“成功率提高”“采样效率提高”与“能力边界扩张”，并报告有限 `n` 对极限集合估计的置信区间。

## 调研日志

### 2026-07-21 与 GUI 主 survey 解耦

- **迁移**：GUI navigation、browser interaction、web environment、rollback、verification 与 web safety 已并入 [[Topics/CUA-Survey]]。
- **保留**：Deep Research / information-seeking 作为非 GUI 邻接方向，保留 11 篇代表论文与独立 routing keywords。

### 2026-07-29 增量更新（survey-refresh）

- **并入**：[[Papers/2604-PassKT]]（RL capability boundary 的 `k×T` 条件化测量）与 [[Papers/2607-RARG]]（relevance as execution control）。
- **变化**：§1 把 RL 增益改写为 task structure × policy support 条件命题；§4 扩为 Context + Corpus Interaction，补 traversal/visibility 控制；Takeaways +2、Open Problems +2；无新平行 taxonomy。
- **验证边界**：两篇均 source-checked；PassKT 限单 7B/小 corpus/短 horizon，RARG 主表限 100-query + GPT-5.1 judge，未外推为 open-web 共识。
