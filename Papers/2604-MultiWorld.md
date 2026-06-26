---
title: "MultiWorld: Scalable Multi-Agent Multi-View Video World Models"
authors:
  - "Haoyu Wu"
  - "Jiwen Yu"
  - "Yingtian Zou"
  - "Xihui Liu"
institute: ["The University of Hong Kong", "Sreal AI"]
date_publish: "2026-04-20"
venue: "arXiv"
tags: ["world-model", "video-understanding", "manipulation"]
url: "https://arxiv.org/abs/2604.18564"
code: "https://multi-world.github.io/"
rating: "4"
date_added: "2026-06-26"
---
## Summary

MultiWorld 把 action-conditioned video world model 从单 agent 扩展到**多 agent 多视角**：用 Multi-Agent Condition Module (MACM) 解决多 agent 可控性、用 Global State Encoder (GSE) 解决多视角一致性，并通过相对身份嵌入和全局状态压缩实现对**任意 agent 数与视角数**的弹性 scaling 与并行生成。在多人游戏（It Takes Two）与多机器人操作（RoboFactory）两类场景上，视频保真度、动作跟随、多视角一致性均优于 baseline。

## Problem & Motivation

现有 video world model 隐含假设环境里只有**单个 agent**，忽略了协作机器人、多人游戏中多 agent 同时行动的交互与相互依赖。把世界模型推广到 multi-agent / multi-view 引出三个单 agent 模型无法解决的挑战：

1. **Multi-Agent Controllability**：要把特定 action 关联到对应 agent 并同步执行——简单堆叠不同 agent 的 action 会导致身份混淆（例如 Agent1 左移+Agent2 右移 vs 反过来，模型分不清）。
2. **Multi-View Consistency**：每个 agent 从各自视角观察共享环境，模型必须保证不同视角间几何一致。
3. **Framework Scalability**：真实环境 agent 数和相机数可变，而 COMBO、并发工作 Solaris 等都假设固定 agent 数或预定义视角。其中 Solaris 把两视角沿序列维交错后共享 self-attention，因计算/显存约束无法扩展到更多视角。

## Method

基于 **Flow Matching + Transformer** backbone（具体用 Wan2.2-5B），把多视角世界模拟分解为 V 个单视角 image-action-conditioned video generation 子问题，共享一个全局环境状态、并行合成。对 action cross-attention 施加 frame-wise causal mask 保证时序因果、支持长程自回归。

**Multi-Agent Condition Module (MACM)** 解决可控性，两个组件：
- **Agent Identity Embedding (AIE)**：用 RoPE 给每个 agent 的 action token 注入**相对身份嵌入**打破多 agent action 空间的对称性，再用 self-attention 显式建模 agent 间交互。关键发现：RoPE 默认 base frequency 10000 适合 LLM 但**不适合多 agent**（相邻 agent 嵌入几乎不可区分），把 base 降到 20 才能匹配 agent 数量、显著区分。相对嵌入可外推，因此天然支持任意 agent 数。
- **Adaptive Action Weighting (AAW)**：用 MLP 为每个 action token 预测自适应权重，把活跃 agent 的 action 加权聚合成统一表示，让模型聚焦于真正驱动环境变化的动态 agent，而非把静止 agent 同等对待。

**Global State Encoder (GSE)** 解决一致性与视角 scaling：用**冻结的 VGGT**（端到端 3D 重建基础模型）作 backbone，从任意数量的多视角 partial observation 中提取 3D-aware 的隐式全局环境状态（不显式重建点云，而是利用 latent 内含的 3D 信息），再经 MLP 对齐维度后通过 cross-attention 注入 DiT。这带来三个好处：(1) 共享全局表示提升多视角一致性；(2) 把任意视角数压缩成统一全局状态，支持任意视角生成；(3) 各视角可并行生成（双视角并行相对串行约 1.x 加速）。

**自回归长程**：先生成第一个 chunk 的所有视角，用末帧更新全局状态再生成下一 chunk，可稳定外推到训练上下文 2 倍、最多 4 倍的时长。

## Key Results

数据集：It Takes Two 真人游戏 100h（21M+ 帧，下采样到 320×640）；RoboFactory 多机器人 2-4 agent 操作（每任务 1000 成功 + 2000 失败 episode，失败由对成功轨迹施加受控扰动构造）。指标：FVD / PSNR / SSIM / LPIPS（视觉），RPE（多视角一致性，基于 DROID-SLAM），IDM-based action-following（仿 VPT）。

**主实验（Table 1）**，MultiWorld vs Standard / Concat-View / COMBO：
- 多人游戏：FVD **179**（baseline 207–245），Action **89.8**（baseline 88.4–89.3），RPE **0.67**（baseline 0.72–0.75）——三项最优。
- 多机器人：FVD **96**（baseline 99–106），RPE **1.52**，PSNR 26.60，整体最优或次优（Concat-View 仅训于两视角不可比）。

**消融**：
- 主组件（Table 2）：在 Standard 上逐步加 MACM 把 FVD 245→228、Action 88.4→89.7（提升可控性）；再加 GSE，FVD 228→179、RPE 0.76→0.67（提升一致性）。
- AIE base frequency（Table 3）：base=20 优于 base=10k（FVD 234→228，Action 89.2→89.7）。
- AAW（Table 4）：加入后 FVD 245→236、Action 88.4→88.6。
- GSE backbone（Table 5）：VGGT 最优（FVD 179），优于 w/o Global State（228）、Wan VAE（256，反而更差）、DINOv2（232）——证明显式建模共享 3D 状态的必要性。

**定性**：能模拟多机器人失败轨迹（碰撞、抢位），三机器人按序堆叠且自回归外推 2×（可达 4×）训练窗口质量几乎不掉；对 zero-action 忠实生成静止视频，缓解 action bias。

## Strengths & Weaknesses

**Strengths**：
- 问题定义干净，且把 multi-agent / multi-view 分别对应到两个**正交且可独立 scaling** 的组件（MACM 管 agent、GSE 管 view），架构清晰、有实证支撑。
- AIE base frequency 的发现很有 insight：RoPE 超参在 LLM 与多 agent 之间不可照搬，base=20 的消融把"convention≠truth"落到了实处。
- 用冻结 VGGT 当全局状态编码器是聪明的复用——避免显式 3D 重建却拿到 3D-aware 一致性，并解耦了视角数与计算量。
- 失败轨迹合成对机器人训练有实用价值（失败数据难采且危险）；消融完整。

**Weaknesses**：
- 规模受限，作者自陈大规模训练因算力未做（8×A800、4 天、Wan2.2-5B）。
- 数值增益总体偏小（多机器人 FVD 99→96、Action 88.5→88.7 几乎打平），多视角一致性（RPE）增益比视觉/动作更显著，说明卖点主要在一致性。
- 失败 case：远处/小目标 agent 因分辨率不足形态模糊。
- It Takes Two 完整数据集因版权不能开源，复现受限。

## Mind Map

```mermaid
mindmap
  root((MultiWorld))
    Problem
      单 agent 假设
      多 agent 身份混淆
      多视角一致性 + 可变配置
    Method
      MACM: AIE(RoPE base=20) + AAW
      GSE: 冻结 VGGT 全局 3D 状态
      Flow Matching + Wan2.2-5B
      并行视角 + 自回归长程
    Results
      游戏 FVD 179 / RPE 0.67
      VGGT 最优 backbone
      失败轨迹 + 4x 长程外推
```

## Notes

- 与 HY-World 2.0 形成对照：MultiWorld 走"隐式 video world model"路线（动态、可控、多 agent），HY-World 走"显式 3DGS"路线（静态、可导航）。两者都用 3D-aware 表示保一致性，但 MultiWorld 把 3D 信息留在 VGGT latent 里而非显式重建。
- 核心可迁移 pattern：(1) 用相对位置编码（RoPE）做"身份/角色"嵌入以获得对数量的外推能力；(2) 把高维条件（多视角观察）压缩成 compact 全局 state 再 cross-attention 注入，从而解耦计算与条件数量。
- 失败轨迹合成连接 world model 与 VLA：可作为 RoboFactory 类多机器人协作的数据增强源，值得跟 WMPO 等 world-model-for-policy 工作对照。
- 待挖问题：GSE 把任意视角压成单一全局 state，当视角差异极大或场景大尺度时这个 compact state 是否成为瓶颈？论文未压力测试视角数上限。
