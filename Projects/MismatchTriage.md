---
title: "MismatchTriage: Measuring and Closing Recovery-Selection Regret in GUI Agents"
tags: [gui-agent, computer-use, recovery, counterfactual]
status: active
date_started: "2026-07-21"
---
## Goal

在固定 detector 的 alert 分布上，用同 checkpoint 全分叉测量 GUI agent 异质 recovery operator 的 counterfactual outcome matrix，直接量化 candidate-set oracle 与最优固定恢复协议之间的 recovery-selection headroom（\(H_{\text{fork}}\)），并在 headroom 成立时把该矩阵蒸馏为部署时无需分叉的 outcome-value selector。目标一篇主会论文；positive 与 well-powered negative 均可发表。

## Research Plan

### 关键问题

GUI agent 检测到 mismatch 后，"选哪个恢复动作"是否是一个值得学习的决策问题——即逐点最优选择相对最强固定策略的成功率差距是否 ≥8pp（CI 下界 >3pp）？

### Key Idea

三个已有先例的组合（组合无先例，novelty 3/5，双重检索验证，见 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] v4）：

1. **Matched-state counterfactual matrix**：每个 first-alert checkpoint 分叉执行全部 feasible recovery macro（含 `Continue`，共 7 个），冻结 continuation policy，以 state-based terminal verifier 估计 \(Q_i(a)\)——分叉标签免疫 EvoCUA-1.5 暴露的 PRM-hacking 通道。
2. **Headroom 先于方法**：主贡献是 \(H_{\text{fork}}\) 的直接测量 + Rescue/Harm 分解；selector 只有在 gap confirmed 后才训练。
3. **Train-with-fork, deploy-fork-free**：selector 预测完整 value vector（含 cost 与 side-effect 项），部署时零分叉开销。

### 分阶段计划（gate 见 idea 文件 Pre-registered decision rule）

| Phase | 内容 | 时长 | Gate |
|:--|:--|:--|:--|
| **P0 pilot** | 30–50 个 first-alert checkpoint 零训练试点（MobileGym JSON fork），回答四问：fork 是否等价 / `Continue` 是否频繁最优 / best-fixed vs oracle 差多少 / 区分 3pp 与 8pp 需要多少 task×seed | 2–3 周 | 任一答案不理想即 pivot，不训练 selector |
| P1 | alert state bank：两个 base agent + expected-effect detector，分层审计 precision/recall | 3 周 | detector audit 通过 |
| P2 | 全量 counterfactual matrix（AndroidWorld + AW-Extend emulator；成本按 alerts×7×suffix×replicates 预算） | 4–5 周 | fork fidelity gate |
| P3 | gap / kill 决策（零训练）：\(H_{\text{fork}}\) 主表 + fixed escalation（VLAA-GUI Loop Breaker / LongHorizonUI）强 baseline | 2 周 | Go / Kill / Inconclusive 三态 |
| P4–P5 | rule → prompted → learned selector；end-to-end deployment（\(G_{\text{deploy}}\)，paired hierarchical bootstrap） | 6–8 周 | \(R_f\ge50\%\) |
| P6 | 事后聚类（类别作为实验输出，非先验 taxonomy）+ 写作 | 3–4 周 | — |

### Motivation 证据链

- 恢复既能救回也能净伤害：[[Papers/2505-BacktrackAgent]] 救回 2.37% 但改坏 0.78% 原本正确的动作。
- 固定协议价值高度条件化：[[Papers/2607-TSR]] 跨 setting 符号翻转；[[Papers/2604-VLAA-GUI]] Loop Breaker 在 Sonnet@100 仅 +0.04pp、Flash@15 反而 −6.15pp。
- recovery 是实问题但 selection gap 未被测量：[[Papers/2605-GUIRobustEval]] 专训后 depth-5 Post-Error Success 仍只 33.2%；无工作在同 checkpoint 穷举异质 operator。
- 测量工具已就绪：[[Papers/2605-MobileGym]] JSON exact fork；[[Papers/2602-VAGEN]] 交互式 outcome verifier（94.0% precision）可作 \(Q_i(a)\) 估计的判定器。

## Papers

- [[Papers/2607-RobustExecAgenticRL]] — 最近邻（VLA 域 learned recovery selection），差异 = matched-state matrix + headroom 测量
- [[Papers/2604-VLAA-GUI]] / LongHorizonUI — fixed-escalation 最强 baseline 家族
- [[Papers/2602-VAGEN]] — 分叉测量的 outcome verifier
- [[Papers/2505-BacktrackAgent]] / [[Papers/2604-VeriGUI]] / [[Papers/2606-OSOracle]] — shared-detector fixed baselines
- [[Papers/2606-SRC]] / [[Papers/2410-ExACT]] — train-with-fork deploy-fork-free 先例
- [[Papers/2605-MobileGym]] — fork 基建与 USE 指标

## Ideas

- [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] — 核心假设、formal estimand、macro set v4、decision rule（本项目唯一权威来源）
- [[Ideas/ForkPoint-CreditAssignment-GUI]] — 分叉数据训练侧衔接（暂缓）

## Progress Log

- 2026-07-21: 立项（Supervisor 指令）。idea v4（18/25，双重检索验证）为准；P0 pilot 为第一行动项。

## TODOs

- [ ] P0-1: MobileGym fork API 环境搭建与 restore/replay 等价性验证（screenshot / AX tree / app DB 逐项比对）
- [ ] P0-2: 预注册可回滚任务子集 + expected-effect detector 的最小实现
- [ ] P0-3: 收集 30–50 个 first-alert checkpoint，跑 7-macro 分叉，出四问答案
- [ ] 与 Supervisor 确认：base agent 选择（8B 级开源 CUA vs API 模型）、emulator 算力预算
- [ ] P0 报告 → go/no-go 决策

## Results & Findings

## Notes

- 竞争风险：RobustExec 团队向 GUI 域扩展是自然下一步；VLAA-GUI 的消融已把 selection heterogeneity 摆上台面。P0 数据应在 4–6 周内产出。
- 与 [[Projects/AFE-MiniSuite]] 共享 checkpoint/restore 基建思路，但研究对象不同（recovery selection vs affordance 因果收益），保持独立。
