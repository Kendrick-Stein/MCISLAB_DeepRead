---
title: "Digi-Q: Learning Q-Value Functions for Training Device-Control Agents"
authors: [Hao Bai, Yifei Zhou, Li Erran Li, Sergey Levine, Aviral Kumar]
institute: [UC Berkeley, UIUC, Amazon, CMU]
date_publish: 2025-02-13
venue: "ICLR 2025"
tags: [gui-agent, agentic-RL, RL]
url: https://arxiv.org/abs/2502.15760
arxiv_id: "2502.15760"
doi: "10.48550/arXiv.2502.15760"
cite_key: ""
code: https://github.com/DigiRL-agent/digiq
rating: 4
content_scope: full-text
verification_status: unverified
date_added: 2026-07-23
---
## Summary
Digi-Q 是面向 mobile device-control（GUI）agent 的**纯离线 value-based RL**：在冻结的 VLM 中间层特征上用 offline TD-learning 训练 action-value Q-function，再以 Best-of-N policy extraction 从静态轨迹中提取策略，无需任何在线交互即在 Android-in-the-Wild 上逼近需要真机 rollout 的 online RL。

## Problem & Motivation
构建 foundation-model agent 的主流做法是 prompting 或用人类示范 SFT，但在 mobile device control 这类 dynamic、部分可观测环境中，静态示范无法覆盖策略在真实执行时会进入的状态分布，导致 error accumulation。On-policy RL 原则上能修正这一点，但在开放式 agentic 任务里每一次真机交互都有成本（时间、并行、reset、安全），online rollout 昂贵且难扩展。核心问题因此是：**能否只用已有的静态轨迹（offline data），不做任何环境交互，就得到接近 online RL 的策略提升**——这正是 CUA 综述 §7.7 所指的 offline RL from static trajectories 子问题。

## Method
三阶段 pipeline，关键是把"训练一个可靠的 GUI Q-function"拆成表示与值学习两步，再用推理时计算换取策略改进：

- **Stage 1 — Representation fine-tuning（让 VLM 特征"可动作化"）**：先用一个 binary 分类目标微调 VLM——判断动作 $a_t$ 是否引起可见状态变化（按相邻截图的 $\ell_2$ 图像距离 $d(s_t,s_{t+1})>\epsilon$ 打 0/1 标签），loss 为 yes/no token 的 BCE。目的是放大特征中"actionable information"的覆盖，使后续 Q-head 能从表示里读出动作效果。
- **Stage 2 — Offline TD-learning Q-function（冻结 backbone + 轻量 head）**：冻结 VLM 参数，只在其**中间层 frozen features** 上训练一个小 MLP Q-head，用标准 TD loss $J_Q=\mathbb{E}[(Q_\theta(f_\theta(s,a))-r-\gamma V_{\bar\psi}(f_{\bar\psi}(s')))^2]$。同时维护一个只依赖状态、不条件于动作的 V-function，直接用现成 VLM 表示（省去为状态值再微调）。冻结 backbone 相比端到端微调整个 VLM 省算力、更易扩展。
- **Stage 3 — Best-of-N policy extraction（用 inference-time compute 替代 online data）**：给定状态从 behavior-cloned policy $\pi_\beta$ 采样 $N{=}16$ 个候选动作，按 Q 值排序，让策略去 imitate 满足 $a_i=\arg\max_i Q(s,a_i)$ 且 advantage $Q(s,a_i)-V(s)>0$ 的最佳动作。相比 REINFORCE 避免 negative-gradient 不稳定，又比 AWR 更少保守，从而在不接触环境的前提下实现 policy improvement。

## Key Results
- 主结果（AitW，Table 1）：Digi-Q 在 **General test 71.2%、Web Shopping test 58.0%**；对照 offline 基线 DigiRL(offline) 59.0% / 47.6%、Filtered BC 54.5% / 43.8%；online 上界 DigiRL(online) 74.5% / 57.3%——即纯离线的 Digi-Q 已逼近甚至在 Web Shopping 上略超需要真机交互的 online RL。
- 声称对 prior best offline 方法有 **21.2% relative improvement**（在 General 由 59.0→71.2 约 +20.7%，Web Shopping 由 47.6→58.0 约 +21.8%）。
- Ablation：representation fine-tuning 带来 >10% 绝对提升（Web Shopping：off-the-shelf LLaVA 31.9% → Digi-Q 58.0%）；TD-learning 相对 Monte-Carlo return 从 37.5%→58.0%；Best-of-N 提取优于 REINFORCE(37.5%, KL 7.15) 与 AWR(19.4%, KL 2.84)，Digi-Q 58.0%(KL 3.28)；性能随 $N$ 从 1 单调升到 16。

## Evidence Ledger
| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | Digi-Q 在 AitW General/Web Shopping test 为 71.2%/58.0% | number | Table 1 | "Digi-Q 71.2% / 58.0%" | source-verified（经 WebFetch 全文抽取，未逐字复核） |
| C2 | offline 基线 DigiRL(offline) 59.0%/47.6%，online DigiRL 74.5%/57.3% | number/comparability | Table 1 | "DigiRL(offline) 59.0/47.6; (online) 74.5/57.3" | source-verified（同上抽取路径） |
| C3 | 相对 prior best offline 方法 21.2% relative improvement | number/SOTA-claim | Abstract + §Results | "21.2% improvement over prior best-performing method" | source-verified |
| C4 | Q-function 用 offline TD-learning 训在冻结 VLM 中间层特征上（MLP head）| mechanism | §Method (J_Q 公式) | "offline temporal-difference learning on frozen intermediate-layer VLM features" | source-verified |
| C5 | Stage-1 表示微调 = 判断动作是否引起 ℓ2 图像变化的 binary 分类 | mechanism | §Method (J_P 公式) | "binary classification to detect whether actions cause visual state changes" | source-verified |
| C6 | Best-of-N 用 N=16 候选、按 Q 排序 imitate 正 advantage 最佳动作 | mechanism | §Method (Stage 3) | "sample N=16 ... imitate best action with positive advantage" | source-verified |
| C7 | Q/V-function backbone 为 LLaVA-1.5；policy 用另一 device-control agent backbone | comparability | §Experiments/Setup | "LLaVa-1.5 for Q and V-function backbones" | partial（policy backbone 具体型号未在抽取中明确，需复核；DigiRL 谱系推测为 AutoUI，未证实）|
| C8 | representation fine-tuning 带来 >10% 绝对提升（31.9%→58.0%, Web Shopping）| number | Table 2 | "more than 10% absolute improvement" | source-verified（抽取路径） |

## Strengths & Weaknesses
**Strengths**：(1) 精确切中 §7.7 的核心命题——**不接触环境、只吃静态轨迹**却能逼近 online RL，把"offline learning 能高效消费已有经验"从口号变成可比数字；(2) 方法 simple & scalable：冻结 VLM + 轻量 Q-head + Best-of-N，避免端到端微调大模型；(3) 用 inference-time compute（Best-of-N）替代 online data collection 的思路 generalizable，可迁移到其他高交互成本 agent；(4) 相对 EvoCUA(step-level DPO)、GUI-Libra(KL trust region) 这类偏好/正则路线，Digi-Q 补上了 §7.7 缺失的**经典 value-based（Q-learning）代表作**。

**Weaknesses**：(1) 结论仅在 AitW 两个子集（General/Web Shopping，各约 1,008/1,296 轨迹）上验证，规模与任务多样性有限，是否迁移到 desktop/OS 级或 live web 未知；(2) Best-of-N 的收益依赖 behavior policy 候选质量，若 $\pi_\beta$ 覆盖差则 argmax 也选不出好动作——这与 §7.7 反复出现的"数据价值 policy-relative"约束一致；(3) offline TD 的 value 估计不稳定与 distributional shift 仍是根本风险，论文用 frozen features + Best-of-N 缓解而非消除；(4) reward 依赖 AitW 的 outcome 标注，partial verifiability 问题（GUI-Libra 所指）未被处理。对领域的意义：为综述 §7.7 提供"value-based offline RL from static trajectories"的锚点，与 EvoCUA/GUI-Libra 形成 offline 三条路线（value / preference / trust-region）的对照。

## Mind Map
```mermaid
mindmap
  root((Digi-Q))
    Problem
      静态示范不足以应对 dynamic device control
      online rollout 成本高
      能否纯离线逼近 online RL
    Method
      Stage1 表示微调-动作是否致视觉变化
      Stage2 冻结VLM特征上 offline TD Q-head
      Stage3 Best-of-N(N=16) policy extraction
    Results
      AitW General 71.2 / Web Shopping 58.0
      逼近 online DigiRL
      +21.2% vs prior best offline
      ablation-表示微调/TD/Best-of-N 均有效
```

## Notes
- content_scope=full-text，但**数字经 WebFetch 对 arxiv html 全文的摘要式抽取得到，未逐字复核 Table 1–3**；coordinator/verifier 若要写入 survey，请回原文 Table 1（主结果）、Table 2（表示微调/TD-vs-MC）、Table 3（Best-of-N vs REINFORCE/AWR）核对后再改 verification_status。
- C7 的 policy backbone 具体型号存疑：抽取只确认 Q/V 用 LLaVA-1.5，policy 是"separate VLM backbone"；沿 DigiRL 谱系推测为 AutoUI 但未证实，勿在 survey 中断言。
- 入库定位：CUA-Survey §7.7 Offline RL 现只有 EvoCUA（step-level DPO）与 GUI-Libra（KL trust region），缺 value-based offline RL 代表作；Digi-Q 恰补此空位，可与二者并列为 offline 三路线对照。
