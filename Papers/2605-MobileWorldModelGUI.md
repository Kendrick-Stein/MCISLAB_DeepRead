---
title: "How Mobile World Model Guides GUI Agents?"
authors: ["Weikai Xu", "Kun Huang", "Yunren Feng", "Jiaxing Li", "Yuhan Chen", "Yuxuan Liu", "Zhizheng Jiang", "Heng Qu", "Pengzhi Gao", "Wei Liu", "Jian Luan", "Xiaolin Hu", "Bo An"]
institute: ["Tsinghua University", "Nanyang Technological University"]
date_publish: 2026-05
venue: arXiv
tags: [gui-agent, world-model, VLM]
url: https://arxiv.org/abs/2605.10347v1
code:
rating: "2"
date_added: 2026-05-12
---
## Summary

系统比较 delta text / full text / diffusion image / renderable code 四种模态的 mobile world model，发现 renderable code 分布内保真度高且能提供多模态训练监督，text-based feedback 在 OOD 线上执行更鲁棒。World model 生成的轨迹可作为训练数据提升 agent 性能，但对 overconfident agent 做 post-hoc self-reflection 效果有限——world model 更适合做 prior perception 而非 test-time verifier。

## Problem & Motivation

GUI agents 在执行任务时面临环境理解的挑战——如何准确感知 UI 状态变化？现有方法主要依赖 text-based state representation（如 accessibility tree），但这种表示可能丢失视觉信息。World model 作为"环境模拟器"可以提供更丰富的状态预测，但如何选择合适的模态表示（text vs image vs code）以及如何有效利用 world model 的预测仍是一个开放问题。

## Method

核心比较框架：

1. **Delta Text**：预测状态变化的文本描述（如 "button X was clicked"）
2. **Full Text**：预测完整的下一状态文本表示（如完整 accessibility tree）
3. **Diffusion Image**：用 diffusion model 预测下一帧的视觉图像
4. **Renderable Code**：预测可渲染的 UI 代码（如 HTML/SwiftUI）

评估维度：
- 分布内保真度（in-distribution fidelity）
- OOD 鲁棒性（out-of-distribution robustness）
- 训练数据增强效果（作为 training data augmentation）
- Test-time reflection 效果（作为 verifier）

## Key Results

| 表示模态 | 分布内保真度 | OOD 鲁棒性 | 适用场景 |
|:---------|:------------|:----------|:---------|
| Delta Text | 中 | 中 | 轻量级反馈 |
| Full Text | 高 | 中 | 详细状态监控 |
| Diffusion Image | 高 | 低 | 视觉密集场景 |
| Renderable Code | 最高 | 中 | 训练数据生成 |

核心发现：
- **Renderable code** 在分布内保真度最高，且能提供多模态训练监督
- **Text-based feedback** 在 OOD 线上执行更鲁棒
- **World model 生成的轨迹**可作为训练数据提升 agent 性能
- **Post-hoc self-reflection** 对 overconfident agent 效果有限——world model 更适合做 prior perception 而非 test-time verifier

## Strengths & Weaknesses

**Strengths:**

- **系统性的模态比较**：四种模态的横向对比提供了清晰的选型指导
- **实用性强**：直接给出了不同场景下的推荐方案
- **发现有价值**：renderable code 的优势和 post-hoc reflection 的局限性是有意义的发现

**Weaknesses:**

- **方法论创新有限**：本质是 engineering ablation 而非方法论突破
- **Renderable code 假设过强**：非标准 UI（游戏、动态 Web）上可渲染性存疑
- **Diffusion image 计算开销未讨论**：mobile 场景下是否 practical？
- **Post-hoc reflection 结论下得太快**：可能是 reflection 策略设计粗糙，而非 world model 本身不适合做 verifier
- **Benchmark 受限**：AITZ/AndroidControl/AndroidWorld 都是相对受限的 setting，真正 OOD 的 wild 场景未触及

## Notes

- 与 `2604-AgenticWorldModel` 形成对比：后者侧重 world model 架构设计，本文侧重表示模态的实证比较
- Finding 3（post-hoc reflection 无效）与 "world model as verifier" 的主流叙事形成张力——如果不适合做 post-hoc 验证，最大价值在 training data augmentation 和 reward shaping
- Xiaolin Hu（清华）+ Bo An（NTU）组合在 GUI agent 领域持续产出
- 一篇扎实但 uninspiring 的实证工作，对后续研究有参考价值但不会改变方向
