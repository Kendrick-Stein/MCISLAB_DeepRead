---
title: "Anti-Self-Distillation for Reasoning RL via Pointwise Mutual Information"
authors: [Guobin Shen, Xiang Cheng, Chenxiao Zhao, Lei Huang, Jindong Li, Dongcheng Zhao, Xing Yu]
institute: []
date_publish: 2026-05-12
venue: arXiv
tags: [agentic-RL, LLM]
url: https://arxiv.org/abs/2605.11609
code: 
rating: 4
date_added: 2026-05-25
---
## Summary
通过 PMI 分析揭示 on-policy self-distillation 的结构性缺陷（奖励 shortcut token、惩罚 deliberation token），提出 AntiSD 方法反转梯度方向并用 JSD 上升替代 KL 下降，在数学推理任务上以 2-10 倍速度达到 GRPO 基线精度，最终提升 2.1-11.5 个点。

## Problem & Motivation
On-policy self-distillation（让模型在 privileged context 如验证过的解法上自我教学）在数学推理任务上效果不稳定。作者发现核心问题：teacher 在看到正确解法后，会对解法中已隐含的 token（结构连接词、可验证陈述）产生高置信度，同时抑制驱动多步搜索的 deliberation token（"Wait"、"Let"、"Maybe"）。标准 self-distillation 因此强化了 shortcut token、削弱了探索性 token，与推理任务需求相悖。

## Method
### PMI 诊断
将 self-distillation 的 per-token 信号形式化为条件 pointwise mutual information：

u_t = log(π_θ(y_t|x,c,y_{<t}) / π_θ(y_t|x,y_{<t})) = PMI(y_t; c | x, y_{<t})

实证发现两个关键观察：
- **(O1)** 符号错误：deliberation token 的 u_t < 0（被 privileged context 抑制），shortcut token 的 u_t > 0（被增强）
- **(O2)** 重尾分布：deliberation token 的 u_t 可达 -20，在 batch 中过采样

### AntiSD 三组件
1. **梯度反转**：不下降 divergence（拉近 student 和 teacher），而是上升 divergence，在源头翻转 per-token 符号
2. **JSD 上升**：使用 φ(u) = ½(softplus(u) - log 2) 作为 advantage 函数，提供非对称边界——deliberation 侧上限为 ½·log 2（吸收重尾尖峰），shortcut 侧保持线性。AntiSD advantage 为 A_t^AntiSD = -φ(u_t)
3. **Entropy-triggered gate**：当 teacher entropy H 低于阈值 τ_down 时禁用 AntiSD 项，H 恢复到 H_warm 时重新启用。阈值从 warmup 步自动校准（τ_down = 0.93 · H_warm）

总 advantage 为轨迹级 GRPO 信号与 per-token AntiSD 信号的加性组合：A_{i,t} = A_i^{seq} - λ · stopgrad(φ_{i,t})

## Key Results
### 主实验（5 个模型，4B-30B 参数）
在 DAPO-Math-17k 上训练 200 步，测试 AIME 2024/2025/2026、HMMT 2025、MinervaMath：

| Model | GRPO Avg | SD Avg | AntiSD Avg | 加速比 |
|-------|----------|--------|------------|--------|
| Qwen3-8B | 57.4 | 30.6 | **65.7** | 5.0× |
| Qwen3-4B-IT-2507 | 51.3 | 45.9 | **62.8** | 10.0× |
| Olmo3-7B-IT | 43.0 | 41.1 | **48.3** | 9.5× |
| Olmo3-7B-TK | 64.1 | 62.6 | **66.2** | 2.0× |
| Qwen3-30B-A3B | 59.1 | 34.5 | **66.8** | 2.9× |

- AntiSD 以 **2-10 倍更少训练步数**达到 GRPO 精度
- 最终精度提升 **+2.1 至 +11.5 点**
- 标准 self-distillation 在所有模型上均劣于 GRPO
- pass@k 分析显示增益来自覆盖范围扩展，非仅方差降低

### 代码推理
Qwen3-8B 在代码 RL 数据上：HumanEval+ +1.2，MBPP+ +2.3（相比 GRPO）

### Continual AntiSD
从 GRPO 饱和 checkpoint（step 200）继续训练，仅用 30 步达到 from-base 峰值（65.0 vs 65.7）

### Ablation
- **No-teacher**：移除 teacher 导致所有模型在 ~70 步内自我强化崩溃
- **No-gate**：移除 entropy gate 在 Qwen 模型上 step 90 左右崩溃；Olmo 因初始 entropy 更高而存活
- **JSD vs reverse-KL**：reverse-KL 上升导致崩溃（49.5 vs 62.8）
- **加性 vs 乘性组合**：乘性组合在 GRPO 信号无信息时将 AntiSD 缩放至零，性能下降 6.3 点
- **阈值敏感性**：τ_down = 0.93 在所有模型上无需重调即可迁移

## Strengths & Weaknesses
### Strengths
- **理论洞察深刻**：将 self-distillation 信号形式化为 PMI，揭示结构性偏差的根源，而非仅凭经验调参
- **方法简洁有效**：drop-in replacement，无额外计算成本，跨 5 个模型一致有效
- **实证证据充分**：加速比 2-10×，最终提升最高 11.5 点，no-teacher ablation 证明增益依赖 privileged information
- **JSD 边界设计巧妙**：非对称边界吸收 deliberation token 的重尾分布，避免梯度爆炸

### Weaknesses
- **代码推理增益较小**：HumanEval+/MBPP+ 提升仅 1-2 点，说明方法在轨迹级奖励不够稀疏时收益有限
- **Entropy gate 需要校准**：虽然 τ_down = 0.93 跨模型迁移，但仍需 warmup 步自动校准，增加了超参数复杂度
- **PMI 分析局限**：作者承认 PMI 刻画的是单步梯度贡献而非全局最优，理论保证有限
- **评估范围窄**：仅聚焦数学推理，multi-turn agentic 场景和更广泛的代码 benchmark 未覆盖

## Mind Map
```mermaid
mindmap
  root((AntiSD))
    Problem
      On-policy self-distillation 不稳定
      Privileged context 产生 shortcut bias
      奖励已隐含 token，惩罚 deliberation token
    Method
      PMI 诊断：u_t = PMI(y_t; c | x, y_{<t})
      梯度反转：上升 divergence 而非下降
      JSD 上升：φ(u) 非对称边界
      Entropy-triggered gate：H < τ_down 时禁用
    Results
      2-10× 加速达到 GRPO 基线
      最终提升 2.1-11.5 点
      代码推理增益较小
      No-teacher ablation 证明依赖 privileged info
```

## Notes
- **与 GRPO 的关系**：AntiSD 是 GRPO 的增强而非替代，两者加性组合。GRPO 提供轨迹级信号，AntiSD 提供 per-token 校正
- **Potential-based shaping 视角**：per-token u_t 值在轨迹上 telescope 为轨迹级 PMI，符合 potential-based reward shaping 框架（Ng et al., 1999），理论上不改变最优策略
- **Deliberation token 的价值**：实验强调 "Wait"、"Let"、"Maybe" 等 token 在多步推理中的关键作用，与 chain-of-thought 文献呼应
- **未来方向**：multi-turn agent 场景、更广泛的代码 benchmark、与其他 RL 方法（如 PPO、DPO）的组合
