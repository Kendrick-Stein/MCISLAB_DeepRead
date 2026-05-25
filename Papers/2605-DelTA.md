---
title: "DelTA: Discriminative Token Credit Assignment for Reinforcement Learning from Verifiable Rewards"
authors: [Kaiyi Zhang, Wei Wu, Yankai Lin]
institute: []
date_publish: 2026-05
venue: arXiv
tags: [agentic-RL, LLM]
url: https://arxiv.org/abs/2605.21467
code: 
rating: 4
date_added: 2026-05-25
---
## Summary
提出 discriminator view 解释 RLVR 的 token-level credit assignment 机制，发现标准方法的 side-wise centroids 被共享模式主导而削弱判别性，通过 DelTA 方法基于 discriminative signal 重加权 token 贡献，在 7 个数学 benchmark 上平均提升 3.26 (8B) 和 2.62 (14B) 个点。

## Problem & Motivation
RLVR（Reinforcement Learning from Verifiable Rewards）用 response-level 奖励优化 LLM 推理能力，但存在 granularity mismatch：单个 scalar advantage 需分配到 token-level 更新。现有工作发现 RLVR 会产生稀疏的 token-level 分布变化，但缺乏对"哪些 token 概率被增加/减少"以及"什么决定这些变化"的理论解释。标准 RLVR 方法隐式构建的 token credit assignment 机制可能次优。

## Method
**核心洞察**：RLVR 的 policy-gradient 更新方向隐式地充当了 token-gradient vectors 上的线性判别器。对于候选 token，其 log-probability 局部变化由其 token-gradient 与更新方向的内积决定。

**问题诊断**：标准 RLVR（如 DAPO）的更新方向由 positive/negative advantage 样本的 token-gradient centroids 决定（Δθ ∝ M₊·μ̄₊ − M₋·μ̄₋）。这些 centroids 是 within-side 的 advantage-weighted 平均，但被用于 between-side 判别。由于 positive 和 negative 响应共享大量高频模式（格式 token、问题实体等），这些共享模式会主导两侧 centroids，稀释真正有判别性的方向。**"好的 within-side summary 不一定是好的 between-side discriminator"**。

**DelTA 方法**（Discriminative signal-guided Token Credit Assignment）：
1. **初始化**：从标准 advantage-weighted 平均初始化 side-wise centroids（μ̄₊ 和 μ̄₋）
2. **迭代精炼**（K 轮 stop-gradient 迭代）：
   - 为每个 token 计算 soft discriminative score αᵢₜ，基于其 token-gradient 到两侧 centroids 的 squared-distance margin
   - 用 score-weighted 平均重新计算 centroids
   - Score 公式：αᵢₜ = σ((‖vᵢₜ − μ₋‖² − ‖vᵢₜ − μ₊‖²) / γ₊)，使用 entropy-regularized assignment 和 side-specific temperature γ
3. **系数映射**：将最终 scores 映射到有界系数 λᵢₜ ∈ [λ_min, λ_max]，用于重加权 self-normalized DAPO surrogate

**实现细节**：由于 LLM 规模下全参数梯度计算成本过高，DelTA 使用 layer-restricted LM-head gradient proxy `(1−pₜ(yₜ))·hₜ` 仅用于系数估计，加权目标仍优化全部 policy 参数。

## Key Results
**主要结果**（7 个数学 benchmark：AIME24/25/26, HMMT25 Feb/Nov, HMMT26 Feb, Brumo25）：
- **Qwen3-8B-Base**：DelTA 28.40 vs 最强 baseline (SAPO) 25.14，提升 **3.26 个点**
- **Qwen3-14B-Base**：DelTA 39.91 vs 最强 baseline (FIPO) 37.29，提升 **2.62 个点**
- DelTA 在所有 benchmark 和两个规模上均取得最佳结果

**训练动态**：DelTA 和 DAPO 早期奖励相似，随后分化——DAPO 平台期而 DelTA 持续提升。DelTA 维持更长响应、更低 entropy、更高奖励，表明"更稳定和自信的长推理行为"。

**Ablation 研究**：
1. **Opposite-side comparison 必要性**：仅用 within-side centrality 的变体表现*差于* DAPO baseline，证明 own-side 中心性单独使用会误导（共享模式主导 centroids）
2. **λᵢₜ 信号有效性**：
   - Top-50% by λ：优于使用全部 token 的 DAPO
   - Random 50%：与 DAPO 相似
   - Bottom-50%：训练快速崩溃
   - 说明"低 λ tokens 不仅无信息，其梯度方向会主动损害 RLVR 更新"
3. **组件贡献**：去除 refinement 导致最大性能下降（23.27 → 19.97），证明初始 centroids 不足；其他组件（range map、entropy regularizer、adaptive γ、λ-norm）各贡献 1-2 个点

**泛化性**：
- 在代码生成任务上有效（Appendix L.3）
- 在 Olmo3-7B-Base 上有效（Appendix L.2）
- OOD benchmark 上泛化良好（Appendix L.5）
- 计算开销适中（Appendix L.1）

## Strengths & Weaknesses
**Strengths**：
1. **理论贡献扎实**：discriminator view 提供了 RLVR token credit assignment 的新理论视角，清晰解释了"为什么标准方法次优"（within-side summary ≠ between-side discriminator）
2. **方法设计优雅**：DelTA 通过迭代精炼 centroids 直接针对问题根源，无需外部 dense reward 或启发式规则
3. **实验全面**：7 个数学 benchmark、两个规模、多个 baseline、详尽 ablation、OOD 评估、代码/其他架构验证，结果一致且显著
4. **实用性强**：使用 layer-restricted proxy 平衡效果与计算成本，K=1 即有效，易于集成到现有 RLVR pipeline

**Weaknesses**：
1. **Proxy 近似**：使用 LM-head gradient proxy 而非全参数梯度，理论上可能损失信息（虽然实验显示 robust）
2. **评估范围**：主要聚焦数学推理，代码生成和其他领域为补充实验，泛化性需更多验证
3. **计算开销**：虽然"适中"，但仍引入额外系数估计成本，大规模部署时需权衡
4. **理论深度**：discriminator view 是局部线性近似，未探讨非线性效应或多步更新的累积影响

**潜在影响**：为 RLVR 的 token-level credit assignment 提供了新的优化方向，discriminative reweighting 思路可能启发其他 sequence-level RL 场景（如 multi-turn agent RL、tool-use RL）。方法的简洁性和有效性可能推动其成为 RLVR 训练的标准组件。

## Mind Map
```mermaid
mindmap
  root((DelTA))
    Problem
      RLVR granularity mismatch
      Token credit assignment 机制不明
      Standard centroids 被共享模式主导
    Method
      Discriminator view of RLVR
      Iterative centroid refinement
      Discriminative score αᵢₜ
      Bounded coefficient λᵢₜ ∈ [0.8, 1.2]
      LM-head gradient proxy
    Results
      +3.26 pts (8B) / +2.62 pts (14B)
      7 math benchmarks 全胜
      Top-50% tokens 优于 full DAPO
      Bottom-50% tokens 导致崩溃
```

## Notes
- **与 process reward 的区别**：DelTA 不依赖外部 dense annotation，discriminative signal 完全从 RLVR 更新本身推导
- **Forking Tokens 对比**：DAPO w/ Forking Tokens 也做 token reweighting，但基于启发式规则（branching points），DelTA 基于 discriminative structure，效果更优
- **未来方向**：
  1. 探索 full-parameter gradient 的高效近似（如 low-rank projection）
  2. 将 discriminator view 扩展到 multi-turn agent RL（response-level → trajectory-level）
  3. 研究 DelTA 与 process reward model 的结合
