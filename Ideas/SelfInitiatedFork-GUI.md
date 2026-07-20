---
title: "Self-Initiated Fork：让 GUI agent 学会何时分支"
tags: [gui-agent, computer-use, agentic-RL]
status: veto
linked_project: "[[Projects/SelfInitiatedFork]]"
date_updated: "2026-07-20"
veto_reason: "Supervisor 2026-07-20：新颖性不达标——Learning to Explore (2605.08978) 已做 GUI rollback 调用学习、PGTS (2502.06813) 已做 invocation policy RL，本 idea 是二者的延伸组合而非无人研究的空白"
---
## Hypothesis

若把 `fork(k, m)`（从当前状态分裂 k 条并行分支、各试探 m 步、按环境反馈选优提交）作为 GUI agent 动作空间中的一等动作，并训练 agent 只在高不确定/高风险决策点调用，则能以远低于全程树搜索的预算获得接近的成功率增益。

可证伪预测：

- **预算-收益**：selective fork（agent 决定调用点）相比 always-search（Agent Alpha 式全程 step 级 MCTS），以 ≤1/3 的墙钟/token 预算保留 ≥70% 的成功率增益；相比 never-fork baseline 在长程任务上 success +≥8pp。
- **调用质量**：agent 学到的 fork 调用点与外部信号（token 熵 / critique 分数）定位点的重合度 <80%——若接近 100%，说明学习调用无独立价值、外部熵触发即可，本假设不成立（这同时回答 [[Topics/AgentRuntimePrimitives-Survey]] Open Problem 3 的"agent 自主 vs 算法控制"边界问题，否证也有产出）。
- **组件归因**：fork 收益应集中在环境反馈可区分分支优劣的步骤（如提交表单前、多入口导航点）；若收益均匀分布，则说明来自变相多采样而非 deliberation，应退回 wide scaling 解释。

## Motivation

三原语的 action 化谱系（[[Topics/AgentRuntimePrimitives-Survey]] 能力语义节）中，branch 是唯一空白：

- **Recovery**：prompted（[[Papers/2504-WebRollback]]、[[Papers/2604-Crab]]）→ learned（Learning to Explore, 2605.08978：SFT 教 rollback 动作 + variational 探索奖励，text+GUI）——已闭环。
- **Parallelism**：spawn 已被 MARL 训练成动作（[[Papers/2602-WideSeekR1]] 的 `call_subagent`），但仅无状态检索域。
- **Branching**：环境交互域中 agent 自主发起 fork 无任何先例；分支全部由外部算法控制。

而"何时分支"值得学的证据链已齐：[[Papers/2602-AgentAlpha]] 证明 step 级搜索收益大（OSWorld ~77%、救回 bBoN 失败任务 33.9%）但全程搜索付出 3.6× 墙钟——大部分步骤不需要 deliberation；ARPO (2507.19849) 证明分支收益集中在高熵步；PGTS (2502.06813) 证明 invocation policy 在 reasoning 域可用 RL 学习。但 token 空间的分支零成本、可完美恢复，GUI 的 fork 有真实状态重建成本与不可逆动作约束——预算敏感性正是"学习调用"相对"全程搜索/固定触发"的价值来源，迁移非平凡。

训练侧的延伸收益：agent 的 fork 调用轨迹天然产生"同状态多后续 + 环境反馈"数据，正是 [[Ideas/ForkPoint-CreditAssignment-GUI]] 需要的 counterfactual step 信号，也是 [[Papers/2607-EvoCUA15]] 在 PRM 被 hack 后指名的替代方向（counterfactual local replay）——一套 fork 调用，inference 收益与 training 信号双消费（对应 survey Takeaway 2 的"两侧统一验证"空白）。

## Related Work

- [[Papers/2602-AgentAlpha]] / [[Papers/2407-TreeSearchLMAgents]] / [[Papers/2410-ExACT]] — 外部算法控制的树搜索：收益上界与成本痛点的来源
- [[Papers/2504-WebRollback]] / [[Papers/2604-Crab]] — recovery 的 action 化先例（prompted）
- Learning to Explore (2605.08978) — rollback 调用学习首例；其 exploration-aware reward 设计可复用
- PGTS (2502.06813) — reasoning 域的 invocation policy RL（expand/branch/backtrack/terminate 四元动作）
- [[Papers/2602-WideSeekR1]] — spawn 调用的 MARL 训练（无状态域）；同组同 advantage 的稳定性设计可借鉴
- [[Papers/2509-TreeGRPO]] / ARPO (2507.19849) — 算法控制的分支触发（随机/熵），是"外部信号 baseline"
- [[Papers/2605-MobileGym]] / [[Papers/2510-WebServ]] / [[Papers/2604-Crab]] — fork 基建就绪（JSON state fork / ZFS CoW / eBPF C/R）
- [[Papers/2512-WebOperator]] — 动作可逆性分类：不可逆动作前是 fork 的天然调用点

**Novelty**: 第一个把 fork 作为可学习的 agent 动作放进有状态 GUI 域；把"何时分支"从搜索算法超参变成策略输出；同一 fork 调用数据同时服务 inference 收益与 training 侧 counterfactual credit——三点均无先例覆盖（最近邻 PGTS 无真实状态成本，Learning to Explore 只覆盖 rollback）。

## Approach sketch

1. **环境**：MobileGym（JSON state fork，O(1) 分支）起步，AndroidWorld emulator 快照做真实性验证（与 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] 共享基建）；OSWorld VM 快照过重，留作迁移实验。
2. **动作空间扩展**：`fork(k, m)` + `commit(branch_id)` + `abort()`；不可逆动作（提交/删除/支付类，按 WebOperator 四分类）前强制评估是否 fork——GUI 特有的安全约束，也是与 PGTS 差异化的设计点。
3. **训练三阶段**：(a) prompted invocation 收集冷启动数据——fork 后各分支试探 m 步，用环境可验证信号（validator/状态差分）选优，记录"调用是否带来分支间可区分差异"；(b) SFT 教调用格式与基础判断；(c) RL——reward = 选优分支相对默认（不 fork 直走）分支的回报差 − fork 成本项；advantage 处理沿用"分解后保持组平衡"模式（STEPO/WideSeek 同构）。
4. **评测**：never-fork / always-search（Agent Alpha 复现或简化版）/ 熵触发 fork（算法控制）三 baseline；报告 success、预算（墙钟+token）、fork 精度（调用点的分支间结果方差）。

## Expected outcome

主结果：selective fork 的预算-收益 Pareto 曲线显著优于 always-search 与熵触发；副产品：(a) agent 自主 vs 算法控制分支的首个同环境对照（survey OP3）；(b) fork 调用数据上的 counterfactual credit 信号质量分析（衔接 ForkPoint idea）。单点故事完整，够一篇主会论文。

## Risk

- **基建保真度**：MobileGym 是 functional 仿真，fork 语义与真实 OS 有 gap；缓解：emulator 快照做第二环境，报告 sim-to-real 保留率。
- **学习信号弱**：fork 调用稀疏、收益延迟归因难；缓解：冷启动阶段用环境可验证的分支差异做 dense 调用标签，RL 只做精调。
- **熵触发可能已足够**：否证条件本身有产出（画出边界，回答 OP3），但会把论文从"方法"降级为"分析"——需在实验设计里预留分析深度。
- **竞争窗口**：survey Takeaway 3 预测树方法 12 个月内迁入 browser 域；Learning to Explore 已把"学习探索"推进到 GUI，扩展到 fork 是自然下一步——优先级应高，建议 3 个月内出 feasibility 数据。
