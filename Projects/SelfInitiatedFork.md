---
title: "Self-Initiated Fork：分支决策作为 GUI agent 的可学习动作"
tags: [gui-agent, computer-use, agentic-RL]
status: archived
date_started: "2026-07-20"
archived_reason: "Supervisor 2026-07-20 否决底层 idea（新颖性不达标：Learning to Explore 已做 rollback 调用学习、PGTS 已做 invocation policy，本方向属延伸组合）；替代方向见 [[Ideas/RestorationFidelity-BranchGains]]"
---
## Goal

验证"把 fork 作为 agent 的可学习动作"能否在预算-成功率 Pareto 上同时优于不分支、全程外部搜索、固定信号触发三类现状，并产出 GUI 域 agent 自主分支 vs 算法控制分支的首个同环境对照。目标一篇主会论文，~4-5 个月到投稿。

## Research Plan

### 关键问题

test-time deliberation（在真实环境中分支验证多个假设后再承诺）的**调用决策应该由谁做、在哪里做**？

可证伪形式：把 `fork(k,m)` 作为 GUI agent 动作空间中的一等动作并训练其调用策略，相比 (a) never-fork、(b) always-search（全程 step 级搜索）、(c) 固定信号触发（熵/critique 阈值），能否在预算-成功率 Pareto 曲线上占优——具体地，以 ≤1/3 预算保留 always-search ≥70% 的增益？

### Key Idea

三个组成，每个都有独立先例、组合无先例：

1. **fork 进动作空间**：`fork(k, m)`（分裂 k 条分支、各试探 m 步、按环境反馈选优）+ `commit(branch_id)` + `abort()`；不可逆动作（提交/删除/支付，按 WebOperator 可逆性分类）前强制评估是否 fork——GUI 特有约束，也是与 reasoning 域先例（PGTS）的差异化设计点。
2. **Oracle-first 实验设计**：先用强制全程 fork 测"分支价值沿轨迹的分布"，确认价值集中在少数步骤（go/no-go 门），该 oracle gap 同时是论文的 motivation 图。
3. **fork 数据双消费**：调用产生的"同状态多后续 + 环境反馈"三元组，inference 侧用于选优，training 侧直接构成 counterfactual step 信号（[[Papers/2607-EvoCUA15]] 在 PRM 被 hack 后指名的替代方向，衔接 [[Ideas/ForkPoint-CreditAssignment-GUI]]）。

### Motivation

五条证据链（详见 [[Ideas/SelfInitiatedFork-GUI]] 与 [[Topics/AgentRuntimePrimitives-Survey]] 能力语义节）：

- **收益已证 + 成本痛点**：[[Papers/2602-AgentAlpha]] step 级搜索 OSWorld ~77%、救回 bBoN 失败任务 33.9%，但 3.6× 墙钟——全程搜索为不需要 deliberation 的步骤付费。
- **价值集中有先例**：ARPO (2507.19849) 分支收益集中在高熵步；WebOperator 消融显示 naive 全程搜索可为负收益。
- **调用可学有先例**：PGTS (2502.06813) 在 reasoning 域用 RL 学 branch/backtrack 调用；Learning to Explore (2605.08978) 在 GUI 学会了 rollback 调用。
- **空白确认**：action 化谱系中 branch 是唯一空白（recovery 已 learned、spawn 已在无状态域 learned）——环境交互域的 fork 调用学习无先例。
- **基建成熟、窗口收窄**：MobileGym JSON fork / emulator 快照 / WebServ CoW 就绪；survey 预测树方法 12 个月内迁入 browser 域。

### 具体计划（5 阶段）

**Phase 0 — Oracle feasibility（2-3 周，go/no-go 门）**
- 环境：MobileGym（JSON state fork，O(1) 分支）为主，AndroidWorld emulator 快照为真实性对照。
- 实验：抽 100-200 个长程任务，每步强制 fork k=3、试探 m=3，测**分支间结果方差沿轨迹的分布**。
- Go 判据：≥60% 的分支价值集中在 ≤20% 的步骤；同时记录 oracle-selective（只在高方差步 fork）vs always-fork vs never-fork 的成功率三角。
- No-go 处理：若方差沿轨迹均匀分布，核心假设不成立，pivot 到"分支价值分布刻画 + 调用信号边界分析"（survey Open Problem 3，分析型论文）。

**Phase 1 — Prompted invocation + 数据收集（3-4 周）**
- prompted agent 自主决定 fork 点，收集（状态、调用决策、k 条分支 outcome）三元组。
- **预注册分析**：agent 调用点与熵触发/critique 触发点的重合度——<80% 才有学习空间，≈100% 即触发否证条件（转边界分析）。

**Phase 2 — 训练（5-6 周）**
- SFT：用 Phase 0 的 oracle 调用标签 + Phase 1 的格式数据教会调用。
- RL：reward = max(分支回报) − 直走回报 − λ·fork 成本；advantage 做组平衡重分配（STEPO/WideSeek 的"分解后保持组归一化"同构模式）。
- 基座：8B 级开源 CUA（EvoCUA-8B 或 Qwen3-VL-8B），预算估计数百 GPU 时（只精调 invocation，非全量 agent RL）。

**Phase 3 — 评测与消融（3-4 周）**
- Baselines：never-fork / always-search（简化 step-MCTS 复现）/ entropy-triggered / random-triggered / oracle 上界。
- 指标：success rate、token + 墙钟预算、fork precision（调用点的分支方差分位数）、预算-成功率 Pareto 曲线。
- 消融：不可逆动作前强制 fork 的贡献；k、m 敏感性；MobileGym→emulator 的 sim-to-real 保留率。
- 副产品实验：fork 数据构造的 counterfactual step 信号 vs PRM 的质量对照（复现 EvoCUA-1.5 Fig 7 式分叉曲线作对比）。

**Phase 4 — 写作（3-4 周）**：主故事"learning when to deliberate"；Phase 0 oracle 图做 motivation，Pareto 曲线做主图。

### 预期贡献

1. GUI 域第一个把 fork 作为可学习动作的方法 + 预算-收益 Pareto 主结果；
2. agent 自主分支 vs 算法控制分支的首个同环境对照（回答 survey OP3，即使否证也成立）；
3. fork 调用数据作为 counterfactual credit 信号的质量分析（PRM 替代路线的首个 GUI 实证）。

## Papers

- [[Papers/2602-AgentAlpha]] — always-search 上界与成本痛点
- [[Papers/2607-EvoCUA15]] — PRM 陷阱与 counterfactual 方向、advantage 组平衡模式
- [[Papers/2602-WideSeekR1]] — spawn 调用训练先例、MARL 稳定性设计
- [[Papers/2504-WebRollback]] / [[Papers/2604-Crab]] — recovery action 化先例
- [[Papers/2509-TreeGRPO]] / [[Papers/2512-WebOperator]] / [[Papers/2605-MobileGym]] — 分支信号 / 可逆性分类 / fork 基建

## Ideas

- [[Ideas/SelfInitiatedFork-GUI]] — 核心假设与否证条件
- [[Ideas/ForkPoint-CreditAssignment-GUI]] — 训练侧衔接
- [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] — 共享 emulator 快照基建

## Progress Log

- 2026-07-20: 立项。基于 AgentRuntimePrimitives survey 两轮增量调研（37 篇）确认空白与证据链；研究计划 v1 成文。

## TODOs

- [ ] Phase 0 环境搭建：MobileGym fork API 验证（保真度 + 延迟）
- [ ] Oracle 实验任务集选取（100-200 长程任务，覆盖不可逆动作场景）
- [ ] 与 Supervisor 确认算力预算与基座选择
- [ ] idea-evaluate 过一遍 SelfInitiatedFork-GUI（当前 developing）

## Results & Findings

## Notes

- 竞争风险：Learning to Explore 团队扩展到 fork 是自然下一步；3 个月内出 Phase 0 数据。
- 若 Phase 0 通过但 Phase 2 训练不稳，中间产物（oracle 分布 + prompted 对照）已构成 workshop 论文。
