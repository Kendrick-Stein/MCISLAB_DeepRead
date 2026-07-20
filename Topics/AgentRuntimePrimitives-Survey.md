---
title: "Recovery / Branching / Parallelism 作为 Agent 运行时原语综述——web agent 从单条不可逆轨迹到可分支执行"
tags: [web-agent, survey, environment-engineering, agentic-RL, computer-use]
date_updated: "2026-07-20"
year_range: 2024-2026
papers_analyzed: 37
keywords: [rollback, backtracking, branching, fork, snapshot, checkpoint, tree search, mcts, parallel rollout, test-time scaling, speculative execution, recovery, agent runtime, trajectory generation]
domain_map: GUI-Agent
---

# Recovery / Branching / Parallelism 作为 Agent 运行时原语综述

> **核心问题**（Supervisor 2026-07-07 提出）：Existing web agents are forced into a single irreversible browser trajectory. We study whether exposing engine-level recovery, branching, and parallelism as agent/runtime primitives improves both inference-time task solving and training-time trajectory generation. 过往有哪些相关工作与尝试？

## Overview

**一句话结论**：recovery、branching、parallelism 三个原语的价值各有独立证据链证实，但每条证据链都受限于"原语由谁实现、暴露给谁"——目前的实现全部是 agent 侧浏览器技巧的近似或 trainer 侧基建，engine-level 原语刚在 shell/sandbox 域出现 agent-facing 暴露的先例（[[Papers/2604-Crab]]），web/browser 域的 agent-facing 暴露及其因果收益验证仍是空白。

三个原语的证据现状：

- **Recovery（回退/恢复）**：agent 自主调用 rollback 在 live web 上零样本 +3~6pp、卡死率 19%→7%（[[Papers/2504-WebRollback]]）；rollback 造纠正数据使下游 SFT +9.7~12.9pp（[[Papers/2606-SRC]]）；sandbox 域 agent 自调 `rollback()` 省 29% 步数（[[Papers/2604-Crab]]）。
- **Branching（分支/树搜索）**：inference-time 树搜索在 VWA 相对 +39.7%（[[Papers/2407-TreeSearchLMAgents]]）、+6~30%（[[Papers/2410-ExACT]]）、WebArena +16.6pp（[[Papers/2510-BranchAndBrowse]]）；step 级 MCTS 已把 OSWorld 推到 ~77%、超任务级 Best-of-N 与人类（[[Papers/2602-AgentAlpha]]）；training-time 树 rollout 1/4 预算超 chain-based GRPO（[[Papers/2509-TreeGRPO]]）、搜索树转 DPO 偏好对（[[Papers/2408-AgentQ]]）、branch point 转 SFT 数据工厂（[[Papers/2602-ANCHOR]]）。
- **Parallelism（并行）**：任务级 wide scaling（10 rollouts + behavior 选优）把 OSWorld 推到 72.6% 超人类（[[Papers/2510-ScalingAgents]]）；trainer 侧异步并行使环境利用率 12.2%→67.7%（[[Papers/2509-DARTGUI]]）；轨迹中段的并行分支（mid-trajectory fork）只在 sandbox 域有 speculative execution 先例（Crab，-7.9% 任务时间）；组织式并行（multi-agent 分工）的受控研究显示 naive 并行错误放大 17.2×、平均收益为负（[[Papers/2512-ScalingAgentSystems]]），需 MARL 训练解锁（[[Papers/2602-WideSeekR1]]）。

问题的结构可以用一条演进链概括：

- **2024**：inference-time 树搜索证明分支有大收益，但环境无快照——回溯只能 reset+replay 模拟（[[Papers/2407-TreeSearchLMAgents]]），live 下干脆不可行（[[Papers/2411-WebDreamer]]），live 分支的每一步都是真实副作用（[[Papers/2408-AgentQ]] 的安全自白）。
- **2025 上半年**：回退从搜索算法的控制流下放为 agent 的可调用动作（[[Papers/2504-WebRollback]]），但恢复手段仍是 URL 重定向。
- **2025 下半年**：三线并发——agent 侧树搜索卷向效率与安全（[[Papers/2510-BranchAndBrowse]]、[[Papers/2512-WebOperator]]）；training-time 树 rollout 在无状态工具环境落地（[[Papers/2509-TreeGRPO]]、ARPO 家族）；**系统社区正式认领问题**（[[Papers/2510-AgenticExplorationSystems]]：六种 snapshot 机制全部太慢，提出 fork 语义/外部副作用/原生 fork 三大挑战）；引擎侧 O(1) 容器分支就绪（[[Papers/2510-WebServ]]）。
- **2026**：sandbox 域出现完整 runtime（[[Papers/2604-Crab]]：agent-facing rollback API + speculative execution + RL 分支四场景统一）；rollback 进入训练数据管线（[[Papers/2606-SRC]]）；step 级 MCTS 在 OSWorld 超越任务级 BoN 与人类（[[Papers/2602-AgentAlpha]]）；branch point 进入 SFT 数据合成（[[Papers/2602-ANCHOR]]）；multi-agent 并行获得首个受控定量研究（[[Papers/2512-ScalingAgentSystems]]）与 MARL 训练先例（[[Papers/2602-WideSeekR1]]）。

**核心张力**：不可逆性既是技术问题也是安全问题。live web 上动作不可逆 → 分支探索被限制在沙盒/副本（realism 受损）或退化为想象模拟（[[Papers/2411-WebDreamer]] 拿到真实搜索 ~70% 收益）；引擎快照解决技术不可逆，但外部副作用（邮件、支付、第三方 API）的不可逆没有任何快照能恢复（[[Papers/2510-AgenticExplorationSystems]] Challenge 2、[[Papers/2512-WebOperator]] 可逆性四分类、[[Topics/WebEnvironment-Engine-Survey]] Open Problem 2 三方汇合）。

## 技术路线

### 路线 1：agent 侧模拟——用浏览器技巧近似 recovery/branching

环境不提供原语，agent/搜索框架自己造。实现谱系按恢复保真度递进：

- **reset+replay**：[[Papers/2407-TreeSearchLMAgents]]（best-first search，VWA 相对 +39.7%、弱模型 +119.7%）明确弃用 `go_back`（丢页内状态），回溯 = 重置环境 + 重放动作序列，O(depth) 且要求确定性，只在沙盒可行。LATS (2310.04406)、WebPilot (2408.15978, AAAI'25，MCTS+分层分解) 同谱系。
- **URL 重定向**：[[Papers/2504-WebRollback]] 把 rollback 做成 agent 每步可选动作（critique 判断 + rollback 选点 + 多步一次回退），live 站点可用，但只能恢复 URL 可编码的状态——表单、购物车、后端 session 全丢。
- **nearest-URL 混合重放**：[[Papers/2510-BranchAndBrowse]] 取最近 URL 检查点 + 局部重放，配 background reasoning（只敢预扩展有显式 URL 的确定性 click）与 page action memory，WebArena 35.8% 且时间 -40.4%。
- **可逆性感知回溯**：[[Papers/2512-WebOperator]] 动作可逆性四分类 + checkpoint URL 跳转 + 并行 tab speculative 校验，WebArena 54.6%；其消融显示 naive tree search 反而掉分（51.61% < 无搜索 53.55%），且 agent 侧启发式判断 destructive 动作确认率仅 ~37%。
- **step 级 MCTS 集大成**：[[Papers/2602-AgentAlpha]] alpha-UCT + max 回传 + 兄弟节点对比式评估 + 语义去重扩展，OSWorld ~77% 超 Agent S3 bBoN 4.71pp、同基座对照 +10pp（64.27% vs 54.29%），bBoN 失败任务救回 33.9%；恢复仍是前缀重放（O(depth)，3.6× 墙钟）——2026 年 SOTA 树搜索的状态恢复机制与 2024 年无异。
- 同谱系：[[Papers/2505-BacktrackAgent]]（EMNLP 2025，GUI 错误检测+回退）、Plan-MCTS (2602.14083，plan 层搜索)。

**天花板已清晰**：恢复保真度受限（URL ≠ 全栈状态）、串行执行（Branch-and-Browse 自认单浏览器 session、并行是 future work）、可逆性靠猜（37% 确认率）。这三条正是环境侧零成本掌握、agent 侧永远拿不到的信息与能力。

### 路线 2：模型内化与想象——把分支搬进参数空间

环境不支持分支时的第二条绕行路：让模型自己"想象"或"学会"分支。

- **想象模拟**：[[Papers/2411-WebDreamer]] 用 LLM 世界知识模拟动作后果替代真实探索（live 下唯一选择），拿到真实搜索 ~70% 收益，模拟深度 H>1 即退化；WebSynthesis (2507) 把 world-model MCTS 用于训练轨迹合成；[[Papers/2511-DreamGym]] 是训练侧同构（合成经验替代真实 rollout，Theorem 1 给出 ε_R+ε_P 替代边界）。
- **搜索行为蒸馏**：[[Papers/2410-ExACT]] Exploratory Learning 把 R-MCTS 搜索树摊平成单轨迹微调，教模型自主 explore/evaluate/backtrack——1/4 token 恢复 ~87% 搜索性能，且 test-time scaling 曲线优于 imitation learning。
- **内化的极限**：ExACT 恢复 87% 而非超越；[[Papers/2408-AgentQ]] 训练后模型 81.7% vs +search 95.4%——**训练不消除搜索的独立价值**，两代工作一致。

该路线与引擎路线竞争同一预算（[[Topics/WebEnvironment-Engine-Survey]] Takeaway 3）：引擎每把分支成本降一个数量级，想象/内化路线的必要性就削弱一分；反之内化后的 backtrack 动作在部署时仍需环境支持——两条路线长期互补而非互斥。

### 路线 3：引擎级原语——系统侧供给 snapshot/fork/checkpoint

2025-10 之后系统社区正面入场，供给侧快速成熟：

- **问题宣言**：[[Papers/2510-AgenticExplorationSystems]]（Columbia）实测 CRIU/Docker commit/Podman/AWS snapshot/checkpoint-lite/hybrid 六机制，最快 1.757s，距交互式探索需要的微秒级差 3-6 个数量级；Terminal-Bench 禁用探索 -27.2pp 是需求端最硬的数字；三大挑战（fork 语义、外部副作用、原生 fork）划定设计空间；判定"预定义逆操作"路线不可行。
- **web 容器栈**：[[Papers/2510-WebServ]] Incus + ZFS block-level CoW，1.78s 启动 / 28MiB 每实例 / 运行中容器快照分支 / 单机 200+ 并发——面向 trainer/evaluator API，未暴露给 agent。
- **sandbox runtime**：[[Papers/2604-Crab]]（HKUST）语义感知 C/R——eBPF 追踪 turn 级净变化跳过 75-87% 检查点、与 LLM 等待窗口重叠，p50 0.1s；**`sbx.rollback(ckpt)` 直接暴露为 agent 工具**，proactive rollback 省 29% 步数、speculative execution -7.9% 任务时间、RL 分支 token -40~64%。
- **轻量状态 fork**：[[Papers/2605-MobileGym]] JSON state forking（functional 仿真才可行）；[[Papers/2504-REAL]] localStorage 整存整取（未做成 API）。
- 相邻：Agent libOS (2606.03895，fork/checkpoint 的 capability 控制)、TraceGraph (2605.31308，prefix-fork 故障恢复策略)。

**关键判断**：引擎侧"能不能"已解决（秒级→亚秒级），"给谁用"未解决——除 Crab 外全部留在 trainer/evaluator 手里，且 Crab 限于 shell/FS/process 状态，browser session + 后端 DB 的 web 全栈 fork 无人做。

### 路线 4：training-time 分支与恢复——rollout 结构与数据工厂

分支/回退在训练侧的三种用法，各有独立证据：

1. **树 rollout 改变 RL 采样结构**：[[Papers/2509-TreeGRPO]] step 级节点树采样，前缀共享 = 同预算 1.5× 样本 + 分叉点兄弟子树回报差 = 免费过程信号（intra-tree GRPO ≡ step-DPO），1/4 预算超 chain GRPO、小模型 +16~69%；ARPO (2507.19849, ICLR'26) 在工具调用后的高熵步触发分支采样，一半工具调用成本超 GRPO；AEPO (2510.14545)、AT2PO (2601.04767)、GiGPO (2505.10978)、TreeRL (2506.11902) 同赛道——"**在哪分支**"的信号设计（随机/熵/value）正在成为子问题。**共同前提：环境无状态**（检索/搜索 API），分支 = 从上下文续写；有状态 browser 域无人验证。
2. **搜索树转监督信号**：[[Papers/2408-AgentQ]] 树上 Q 差 → step 偏好对 → DPO（OpenTable 18.6%→81.7%）；[[Papers/2410-ExACT]] 树遍历 → Exploratory Learning；[[Papers/2606-ENVS]] 分支搜索 + 环境 oracle 过滤 → SFT。
3. **rollback 造纠正/恢复数据**：[[Papers/2606-SRC]] K 步试探分支 + teacher 定位回退 + QD archive，WebArena-Infinity +9.7pp / OSWorld +12.9pp（恢复实现 = reset+replay，作者自列 resettable 假设为局限）；[[Papers/2605-GUIRobustEval]] 从环境侧注入 error-depth 初态合成 80 万恢复样本；[[Papers/2506-GoBrowse]] prefixed sampling 让弱模型从中间态起步贡献数据（reset 频率直接决定 URL 覆盖 183→260）。
4. **branch point 造多样性数据**：[[Papers/2602-ANCHOR]] 在种子轨迹的 UI 状态变化节点分叉新任务变体（复用已验证前缀直达深层状态），1,777 条轨迹（$0.47/条）使 Qwen3-VL-8B OSWorld +3.7pp / WAA +7.7pp、超人工数据——branch 的训练侧用途从恢复行为扩展到任务多样性；分支结构本可提供的 step 级对比信号未被利用。

基建侧的并行需求同源：[[Papers/2509-AgentGymRL]] 给 WebArena 补 full-reset、[[Papers/2606-AsyncWebRL]] 全异步 rollout、[[Papers/2509-DARTGUI]] 解耦架构 5.5× 环境利用率、[[Papers/2511-DreamGym]] "WebArena 只能开 4 并发"的第一手证词——trainer 侧对 parallel/reset 的需求已充分显影（详见 [[Topics/WebEnvironment-Engine-Survey]] 轴 3/4）。

### 路线 5：并行原语——wide scaling 与 speculative execution

并行目前有三种形态，成熟度各差一代：

- **任务级并行（wide scaling）**：[[Papers/2510-ScalingAgents]] 10 条独立 rollout + Behavior Best-of-N 选优，OSWorld 72.6% 超人类（72.36%）；基础观察是 disjoint task success（不同 rollout 成功集互补，Pass@N ≫ 单跑 SR）；瓶颈明确在**评估**——长程多模态轨迹难比较，behavior narrative 表示是关键（60.2 vs 直接看截图 56.0）。Scaling Test-time Compute for LLM Agents (2506.12928) 系统研究并行采样/list-wise 选优/多样化 rollout 的组合。
- **组织式并行（multi-agent 分工）**：[[Papers/2512-ScalingAgentSystems]] 用 260 配置的受控研究首次画出边界——MAS 平均收益 −0.3%（范围 +80.8%~−70.0%），任务可分解性决定并行收益、验证瓶颈决定错误遏制：无协调的 independent 并行错误放大 **17.2×**，centralized orchestrator 压到 4.4×；单 agent 基线 >45% 后加 agent 几乎必然负收益（架构选择 87% 可预测）；web 导航属高顺序依赖域（信息增益相关性 r=0.18），仅 decentralized +9.2%。[[Papers/2602-WideSeekR1]] 给出解锁条件：把协调本身作为 MARL 训练对象（lead-subagent 同组同 advantage + token/agent 双层重加权）——未训练时 subagent 越多分数越低，训练后 1→10 持续正 scaling、4B 追平 671B；但先发域是无状态宽检索（可分解性最高），GUI/browser 迁移未验证。同赛道摘要级：ParallelMuse (2510.24698，partial rollout 复用)、Share-More-Search-Less (2605.27030，跨分支信息共享)、Agent-as-Tool/ParaManager (2604.17009，可学习并行编排)、Mobile-Agent-v3 系（GUI multi-agent 框架，分工但未训练协调）。
- **轨迹中段并行（mid-trajectory fork / speculative）**：只在非 web 域有先例——Crab 的 speculative execution（draft model 抢跑 + fork 校验，~50% 接受率）；Speculative Actions (2510.04371，快模型预测下一动作并行预执行，20% 延迟降低)、PASTE (2603.18897，工具调用与 LLM 生成重叠，-43.5% 任务时间)、B-PASTE (2604.16469，竞争性局部分支)、Sherlock (2511.00330，speculative + 选择性验证回滚) 面向 tool-call 加速。web 域最接近的是 Branch-and-Browse 的 background reasoning（只敢预扩展确定性 click）与 WebOperator 的并行 tab 校验——都受限于无真 fork。

三种形态的差异是本质的：任务级并行只需要"多开实例"（引擎已支持）；组织式并行还需要任务可分解 + 协调能力（GUI 的顺序依赖使其最难受益，且协调需训练而非 prompt 约定）；中段并行需要"从任意中间状态 fork"（引擎刚起步）。**中段并行是三原语的合流点**——它同时需要 branching（分支）、recovery（丢弃坏分支）、parallelism（并行执行），也是收益最未开发的区域。

## 能力矩阵：谁实现原语、暴露给谁

| 工作 | 原语 | 实现机制 | 控制方/暴露对象 | 用途 | 域 | 关键数字 |
|:--|:--|:--|:--|:--|:--|:--|
| [[Papers/2407-TreeSearchLMAgents]] | branch+recover | reset+replay | 搜索算法 | inference | web 沙盒 | VWA 相对 +39.7% |
| LATS / WebPilot | branch+recover | replay/MCTS | 搜索算法 | inference | web 沙盒 | WebArena（WebPilot AAAI'25） |
| [[Papers/2504-WebRollback]] | recover | URL 重定向 | **agent 自身** | inference | live web | 零样本 +3~6pp，卡死 19%→7% |
| [[Papers/2510-BranchAndBrowse]] | branch+recover | nearest-URL 重放 | 搜索算法 | inference | web 沙盒 | WebArena 35.8%，时间 -40.4% |
| [[Papers/2512-WebOperator]] | branch+recover | 可逆性分类+checkpoint URL | 搜索算法 | inference | web 沙盒 | WebArena 54.6%；naive search 有害 |
| [[Papers/2411-WebDreamer]] | branch（想象） | LLM 世界模型 | 模型 | inference | live web | 真实搜索 ~70% 收益 |
| [[Papers/2410-ExACT]] | branch→内化 | R-MCTS→EL 蒸馏 | 模型 | inference+training | web 沙盒 | 1/4 token 恢复 87% |
| [[Papers/2408-AgentQ]] | branch | MCTS（前向，无恢复） | 搜索算法 | training | live web | OpenTable 18.6→95.4% |
| [[Papers/2509-TreeGRPO]] | branch | 上下文续写（无状态环境） | 训练框架 | training | 检索/搜索 QA | 1/4 预算超 chain |
| ARPO/AEPO/AT2PO | branch | 熵触发分支采样 | 训练框架 | training | 工具调用 QA | 一半工具成本超 GRPO |
| [[Papers/2606-SRC]] | recover | reset+replay | 数据管线 | training | web/OS 沙盒 | 下游 SFT +9.7~12.9pp |
| [[Papers/2605-GUIRobustEval]] | recover（初态注入） | 环境 init API | 数据管线 | training | GUI 沙盒 | 80 万恢复样本 |
| [[Papers/2506-GoBrowse]] | branch（中间态起步） | prefixed sampling | 数据管线 | training | web 沙盒 | reset 频率↔URL 覆盖 183→260 |
| [[Papers/2510-WebServ]] | fork+parallel | ZFS block CoW | trainer/evaluator | training | web 容器 | 28MiB/实例、200+ 并发、运行中分支 |
| [[Papers/2510-AgenticExplorationSystems]] | fork（议程） | 六机制实测 | （runtime，未定） | 两者 | shell/sandbox | 最快 1.757s vs 需要微秒级 |
| [[Papers/2604-Crab]] | recover+branch+speculative | eBPF 语义感知 C/R | **agent 自身 + trainer** | 两者 | shell/SWE 沙盒 | rollback -29% 步数；RL 分支 token -40~64% |
| [[Papers/2510-ScalingAgents]] | parallel（任务级） | 独立多 rollout + bBoN | 外层框架 | inference | OS 沙盒 | OSWorld 72.6% 超人类 |
| [[Papers/2602-AgentAlpha]] | branch+recover | step 级 MCTS + 前缀重放 | 搜索算法 | inference | OS 沙盒 | OSWorld ~77%，超 bBoN 4.71pp，3.6× 墙钟 |
| [[Papers/2602-ANCHOR]] | branch（数据工厂） | 种子轨迹 branch point 展开 | 数据管线 | training | OS 沙盒 | 8B OSWorld +3.7pp，$0.47/条 |
| [[Papers/2602-WideSeekR1]] | parallel（组织式） | lead-subagent MARL | 训练框架+agent | 两者 | 文本检索 | 4B 追平 671B；未训练则负 scaling |
| Speculative Actions / PASTE 家族 | parallel（中段） | 动作预测+预执行 | serving 系统 | inference | tool-call | -20~43.5% 延迟 |

矩阵读法：**"暴露对象"列只有两行是 agent 自身**（WebRollback：agent 侧近似实现；Crab：engine 级但非 web 域）。engine-level 实现 × agent-facing 暴露 × web 域 × success 因果验证——四个条件的交集为空。

## Datasets & Benchmarks

| Benchmark | 状态恢复支持 | 在本主题中的角色 | 代表工作 |
|:--|:--|:--|:--|
| WebArena / VisualWebArena | Docker 重启（慢）；bit-identical 使 replay 可行 | inference-time 树搜索主战场 | Tree Search、ExACT、Branch-and-Browse、WebOperator |
| Mind2Web-Live / WebVoyager | 无（live，不可逆） | agent 侧 rollback 的 live 验证 | WebRollback、WebDreamer |
| WebShop / OpenTable | 合成可 reset / live 不可逆 | 训练侧搜索树→DPO | Agent Q |
| 多跳 QA + 搜索 API（HotpotQA/GAIA 等） | 无状态（无需恢复） | training-time 树 rollout 先发域 | Tree-GRPO、ARPO 家族 |
| WebArena-Infinity / OSWorld | 可 reset+replay | rollback 数据收集 | SRC |
| Terminal-Bench / SWE-Bench | Crab 提供 O(1) checkpoint | engine-level agent-facing 先例 | Crab、AgenticExplorationSystems |
| OSWorld（wide scaling 协议） | 实例级并行 | 任务级并行选优 | Agent S3 / bBoN |

**没有任何 benchmark 把"恢复保真度"或"分支预算下的表现"作为一等评测维度**；预算维度目前只有 Tree-GRPO 的 per-prompt token/tool-call 预算协议和 Tree Search 的 step 预算曲线。

## Key Takeaways

1. **三原语的价值已分别证实，但收益上限由状态恢复保真度决定**。分支收益随保真度递增的证据线：URL 恢复（WebRollback +3~6pp）< 混合重放（Branch-and-Browse +16.6pp）< 可逆性感知（WebOperator 刷新 tree search SOTA）；而 naive 分支在不校验重放可行性时为负收益（WebOperator 消融）。推论：engine-level 全栈快照是这条收益曲线的未测上界——这正是 research statement 的可证伪空间。

2. **同一分支基建同时服务 inference 与 training，但没有任何工作统一验证两侧**。现状是分域分证：inference 侧（Tree Search/ExACT/WebRollback）与 training 侧（Tree-GRPO/SRC/Agent Q）各自成立；Crab 四场景最接近统一但只测效率不测 success。"一套 fork 原语、两侧收益"的端到端验证（同一环境同一原语，前测 task solving、后测 trajectory generation 质量）仍无人做——这是 research statement 作为一篇论文的完整性所在。

3. **树方法的落地顺序由状态重建成本决定，可用于预测下一波工作**。training-time 树 rollout 全部先发于无状态环境（检索/搜索 API：分支 = 上下文续写，零恢复成本），有状态 browser/GUI 域完全空白；Crab 已证明 checkpoint 使 RL 分支 token -40~64%。可预测：随引擎成熟（WebServ/Crab 代际），Tree-GRPO 类方法将在 12 个月内迁移到 browser 域，先到者获得"browser 域第一个树 rollout RL"的位置——这同时是 AFE 方向的机会与竞争压力。

4. **agent-facing 暴露的空白正在收窄，差异化必须落在 web 全栈状态与因果验证上**。一年前该空白是全域的；现在 Crab 已在 sandbox 域实现 agent 可调用 rollback 并给出效率数字。仍然成立的空白有三：(a) web 域的全栈状态 fork（browser session + 后端 DB，Crab 的 FS+process 捕获覆盖不了）；(b) success rate / wrong-turn recovery 的因果增益（Crab 只测步数/token/时间）；(c) prompt-only 强对照与 affordance 组合消融（无人做）。[[Ideas/AgentFacing-WebRuntime]] 的 C0-C7 设计恰好落在这三点上，但时间窗口从"无人做"变成了"系统社区已入场"（AgenticExplorationSystems 议程 + Crab 实现），优先级应上调。

5. **并行的瓶颈不在生成而在评估与 fork**。任务级并行已成熟且收益惊人（bBoN OSWorld 超人类），但其上限被两件事卡住：评估器（AgentRewardBench 显示 judge precision ≤70%，bBoN 依赖 behavior narrative 才把选优做可靠）与并行形态（只能整任务重跑，不能从中间状态 fork——中段并行同时需要三原语，是收益最未开发的区域，目前只有 tool-call 域的 speculative 家族触及）。推论：verifier affordance 与 fork affordance 在并行场景下是互相解锁的关系，AFE 把两者放在同一套 affordance 里的设计有结构优势。2026-07 两条新证据强化此论断：同预算下 step 级搜索优于任务级 BoN（[[Papers/2602-AgentAlpha]]，结构 > 数量），无验证的组织式并行主动放大错误 17.2×（[[Papers/2512-ScalingAgentSystems]]）——并行收益的分配器是验证/评估结构，不是并行度本身。

## Open Problems

1. **Web 全栈 fork 语义**：browser session（DOM、cookie、页内状态）+ 后端（DB、server session）+ 外部副作用三层状态的一致快照无人实现；WebServ 覆盖容器栈但无浏览器语义层，Crab 覆盖 FS/process 但无 web。外部副作用层被三方独立判定为不可快照（AgenticExplorationSystems / WebOperator / 引擎综述），fork-aware API（副作用版本化）是唯一被提出的系统性方向。
2. **agent-facing 暴露的因果收益**：fork/rollback 给 agent 自主调用 vs 留给外部算法，对 success/recovery/false-completion 的差异无任何对照实验；Crab 的效率数字不回答此问题。同时缺 prompt-only 强对照排除"收益来自信息展示"。
3. **分支决策信号的系统比较**：何时/何处分支——随机（Tree-GRPO）、熵（ARPO 家族）、critique（WebRollback）、value（MCTS 系）四类信号无同环境对比；agent 自主分支 vs 算法控制分支的边界未画出。
4. **恢复保真度谱系的量化**：URL / replay / 快照三档恢复的保真度-成本-收益曲线没有 benchmark；SRC 的 resettable 假设、WebRollback 的 URL 天花板都指向同一缺失度量。
5. **并行分支的评估瓶颈**：N 条中段分支的比较比 N 条完整轨迹更难（局部进展无 outcome 可查）；verifier/progress probe 与 fork 的联合设计无人研究。
6. **live 环境的分支安全边界**：Agent Q 式 live 树搜索的副作用风险无缓解方案；可逆性标注（WebOperator 方向）+ 站长声明接口（agents.txt / [[Papers/2512-PermissionManifestsWebAgents]]）+ 沙盒 fork 的组合是候选路径。

## 调研日志

- **调研日期**: 2026-07-08（autoresearch，Supervisor 指定 focus：engine-level recovery/branching/parallelism 作为 agent/runtime 原语的 related work）
- **论文统计**: vault 已有 25 篇直接相关 + 新 digest 8 篇（[[Papers/2504-WebRollback]]、[[Papers/2510-BranchAndBrowse]]、[[Papers/2410-ExACT]]、[[Papers/2408-AgentQ]]、[[Papers/2509-TreeGRPO]]、[[Papers/2510-AgenticExplorationSystems]]、[[Papers/2604-Crab]]、[[Papers/2606-SRC]]）= 33 篇深度分析
- **摘要级引用（未建 Papers/ 笔记）**: LATS (2310.04406)、WebPilot (2408.15978, AAAI'25)、Plan-MCTS (2602.14083)、BacktrackAgent (EMNLP'25)、Intelligent Go-Explore (2405.15143, ICLR'25，archive+restore 血统)、ARPO (2507.19849, ICLR'26)、AEPO (2510.14545)、AT2PO (2601.04767)、GiGPO (2505.10978)、TreeRL (2506.11902)、WebSynthesis (2507)、Speculative Actions (2510.04371)、PASTE (2603.18897)、B-PASTE (2604.16469)、Sherlock (2511.00330)、TraceGraph (2605.31308)、Agent libOS (2606.03895)、Scaling Test-time Compute for LLM Agents (2506.12928)、WebUncertainty (ACL'26 findings)
- **外部检索**: WebSearch 9 次 + OpenAlex 1 次（WebRollback/Branch-and-Browse 定位、ExACT/AgentQ/WebPilot ID 确认、Tree-GRPO/ARPO 家族、并行 scaling、speculative execution、agent-facing fork gap 核查——最后一项发现 Crab 与 AgenticExplorationSystems，推翻"完全空白"的先验）
- **与 [[Topics/WebEnvironment-Engine-Survey]] 的关系**: 该综述做需求侧推导（引擎该长什么样），本综述做 related work 正面盘点（原语已被谁以何种形式实现/使用）；轴 4"第五用途空白"的表述经本轮修正为 Takeaway 4 的三条剩余空白
- **建议加入 DomainMaps**: (a) GUI-Agent domain 增加"运行时原语三路线"（agent 侧模拟 / 模型内化 / 引擎原语）竞争框架；(b) "树方法落地顺序 = 状态重建成本排序"作为 cross-domain pattern 候选
- **仍未 digest（供后续）**: Intelligent Go-Explore（archive/restore 血统的正式笔记）、ARPO 2507.19849（熵分支的代表作）、WebPilot（MCTS 家族补全）、UI-Simulator (2510.14969)、AgentSynth (2506.14205)、WAC (2602.15384)
- **增量更新 2026-07-20**（Supervisor 重提：并行/分支/回溯，训练/测试两角度 + multi-agent + 浏览器分支）：新 digest 4 篇——[[Papers/2602-AgentAlpha]]（路线 1，step 级 MCTS 刷新 OSWorld）、[[Papers/2602-ANCHOR]]（路线 4 新增用途 4：branch point 数据工厂）、[[Papers/2512-ScalingAgentSystems]]、[[Papers/2602-WideSeekR1]]（路线 5 新增组织式并行形态）；[[Papers/2505-BacktrackAgent]] 由摘要级升级为正式笔记引用。摘要级新增：GUI Exploration Lab (2512.02423, NeurIPS'25，多轮 RL 中回溯行为自发涌现)、ParallelMuse (2510.24698)、Share-More-Search-Less (2605.27030)、Agent-as-Tool/ParaManager (2604.17009)、LAMaS (2601.10560)。外部检索：WebSearch 3 次。矩阵 +3 行，Takeaway 5 补 2026-07 证据。
