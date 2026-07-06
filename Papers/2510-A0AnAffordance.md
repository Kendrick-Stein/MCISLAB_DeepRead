---
title: "A0: An Affordance-Aware Hierarchical Model for General Robotic Manipulation"
authors: [Rongtao Xu, Jian Zhang, Minghao Guo, Youpeng Wen, Haoting Yang, Min Lin, Jianzheng Huang, Zhe Li, Kaidong Zhang, Liqiong Wang, Yuxuan Kuang, Meng Cao, Feng Zheng, Xiaodan Liang]
institute: [MBZUAI, SYSU, SUSTech, Spatialtemporal AI, CMU]
date_publish: 2026-01-20
venue: "ICCV 2025"
tags: [manipulation, spatial-reasoning, VLA]
url: "https://openaccess.thecvf.com/content/ICCV2025/html/Xu_A0_An_Affordance-Aware_Hierarchical_Model_for_General_Robotic_Manipulation_ICCV_2025_paper.html"
arxiv_id: "2504.12636"
doi: ""
cite_key: ""
code: ""
rating: 4
date_added: 2026-06-26
---
## Summary

A0 把 general robotic manipulation 拆成 high-level spatial affordance understanding 和 low-level action execution：前者预测 object-centric contact point 与 post-contact trajectories，后者把 2D waypoints 投影到 3D 并执行。它的核心贡献是提出 Embodiment-Agnostic Affordance Representation，并用大规模 contact-point pre-training 与 trajectory fine-tuning 支撑跨 Franka、Kinova、Realman、Dobot 的真实机器人部署。实验显示 A0 在需要轨迹跟随的任务上显著优于 VLM/VLA baselines，但仍依赖 gripper sampler、depth map 和 VLM height/orientation 辅助。

## Problem & Motivation

机器人操作的难点不只是识别物体，而是理解交互发生在物体的哪里、以及接触之后应如何移动。作者把这称为 spatial affordance 的 "where" 和 "how"：例如 wipe board 需要持续沿可擦区域移动，stack objects 需要接触点和后续轨迹都合理。

现有路线有两类局限。Modular-based methods 如 MOKA、ReKep 依赖 large vision models 做空间理解，但缺少对物体可操作性的深层建模；end-to-end VLA methods 如 RDT、π0 直接生成动作，容易在复杂 manipulation 中忽略精确空间位置。Point-based / flow-based affordance methods 已经意识到 spatial affordance 的重要性，但作者认为 dense representation 或 embodiment-specific trajectory modeling 计算成本高、迁移性不足。

因此 A0 的 problem formulation 是：用一种 object-centric、embodiment-agnostic 的中间表示先学可操作空间，再由模块化执行器落到具体机器人动作。这个 framing 对 embodied research 有价值，因为它把 "robot policy generalization" 从直接动作空间，移到更可迁移的 contact point + post-contact trajectory 空间。

## Method

A0 是一个 hierarchical affordance-aware diffusion model。输入包括当前/上一帧 observation image、language instruction 和 diffusion timestep；输出是归一化 2D waypoint chunk，其中第一个点是 contact point，后续点是 post-contact directional cues。实验设置中模型为 A0-1B，使用 N=28 个 transformer layers，chunk size T=5，diffusion forward/backward steps 分别为 1000 和 5。

**Embodiment-Agnostic Affordance Representation** 是本文的核心表示。每条数据由 object-centric RGB image、language instruction、2D contact point 和 post-contact trajectories 组成，数据来源包括 PixMo-One-Point、HOI4D-22k、DROID-3k 和 Maniskill-5k。作者称 PixMo-One-Point 包含 1 million single-contact-point annotations；HOI4D-22k 包含 22,000 human-object interaction trajectories；DROID-3k 来自 3,056 verified manipulation trajectories；Maniskill-5k 包含 4,965 simulation trajectories。

模型结构上，A0 建在 DiT-style diffusion transformer 上。视觉侧使用 pre-trained SigLiP (400M) 编码 observation images，语言侧使用 pre-trained Qwen2.5-7B 编码 instruction，image/text tokens 通过 cross-attention 交替注入。**Position Offset Attention** 用当前帧 token 减去上一帧 token 得到 motion token，再与当前帧 token concat，用于增强 motion-aware feature；**Spatial Information Aggregation Layer** 用 nonlinear MLP decoder 从 latent space 投影回物理/坐标空间。

训练分两阶段。Pre-training 阶段只用单张图和第一个 waypoint 学 object localization，loss 是预测 contact coordinate 的 MSE；supervised fine-tuning 阶段把 text condition 从 object label 扩展为 language instruction，把输出从单点扩展到 T 个 waypoints，同样用 ground-truth waypoints 的 MSE 训练。需要注意：正文多数位置写 pre-training 使用 1 million contact-point localization samples，但 Sec. 3.1 也出现过 100,000 contact-point samples 的表述，数据规模在论文文本中不完全一致。

Action execution 是模块化的。A0 预测 2D keypoints 后，系统用 depth map 和 camera intrinsics 做 2D-to-3D deprojection；grasp pose 通过 GraspNet 或其他 grasp samplers 产生候选，再选择离 projected grasp point 最近的候选；post-contact waypoints 同样投影到 3D，height 由 VLM 从离散类别中选择，最后生成 SE(3) motion trajectory 执行。

## Key Results

- **Franka Emika / Kinova Gen3 real-world 4-task benchmark**：任务包括 Place Object、Open Drawer、Press Button、Wipe Board，每个任务 20 trials。A0-1B 在 Franka 上平均成功率 **62.50%**，高于 Molmo **43.75%** 和 Magma **16.25%**；在 Kinova 上平均成功率 **53.75%**，高于 MOKA **45.00%**、ReKep **33.75%**、RDT **11.25%**。
- **Trajectory-intensive Wipe Board / Kinova benchmark**：A0-1B 在 Wipe Board 上达到 **50%**，RDT-1B 为 **0%**，π0 为 **10%**，π0 + FAST 为 **0%**；平均成功率 A0-1B **53.75%**，π0 **20.00%**，π0 + FAST **18.75%**，RDT-1B **11.25%**。执行步数上，A0 使用 **4-5** 个 key waypoints，而 VLA baselines 需要 **25-50** steps。
- **Architecture ablation on HOI4D-22k / Maniskill-5k / DROID-3k**：A0-1B 的 MAE 为 **47.5 / 5.5 / 17.5**；去掉 Position Offset Attention 后为 **47.9 / 6.3 / 18.5**；去掉 Spatial Information Aggregation Layer 后为 **61.1 / 10.2 / 19.6**。这说明 SIAL 对 HOI4D-22k 的 waypoint MAE 影响最大，POA 对 Maniskill-5k 和 DROID-3k 也有可见贡献。
- **Pre-training ablation**：Figure 4 显示 pre-training 降低了 waypoint MAE。Real-to-Sim 的 Maniskill-5k 上，A0-1B 从 **50.4** 降到 **43.9**；Sim-to-Real 的 HOI4D-22k 上从 **172.2** 降到 **125.2**，DROID-3k 上从 **35.1** 降到 **29.1**。
- **Robopoint comparison on HOI4D / DROID**：以 first interaction pixel 的 MAE 衡量，A0 在 HOI4D 上为 **54.46**，Robopoint 为 **121.09**；在 DROID 上 A0 为 **14.13**，Robopoint 为 **27.47**。作者报告这分别对应 **55.2%** 和 **40.4%** 的 error reduction。

## Strengths & Weaknesses

**已知的 strengths**：A0 的表示选择很清晰：不直接学习 embodiment-specific action，也不输出 dense heatmap，而是学习 contact point + post-contact trajectory 这种可被不同机器人执行器复用的 object-centric affordance。这个中间层对需要 spatial reasoning 的 manipulation task 很有吸引力，尤其是 Wipe Board 这种单点抓取不足以表达任务目标的场景。实验也覆盖了 offline MAE、真实机器人 success rate、VLA baselines、affordance baselines、Robopoint 对比和结构 ablation，证据比单纯 demo 更完整。

**已知的 weaknesses / limitations**：论文明确承认 A0 的执行依赖 gripper samplers；如果 grasp pose estimator 泛化差，A0 的 high-level affordance 预测仍可能无法落地。系统还需要 depth map 估计 height，并用 VLM 做离散 height refinement；在 occluded objects 上可能不稳定。对 orientation-sensitive tasks，如 liquid pouring 和 revolute-drawer opening，作者并没有声称 A0 原生解决，而是讨论通过选择观察视角或替换 action execution module 来处理。Long-horizon planning 也不是 A0 自身解决的，作者使用 GPT-4o 等 VLM 分解为短子任务后再逐段执行。

**推测**：A0 的 contact point + post-contact trajectory 表示可能比 raw action 更适合跨 embodiment transfer，但这依赖一个前提：不同机器人共享足够相似的可见 object affordance，并且 action executor 能稳定把 2D/3D waypoints 转成可行 SE(3) motion。这个前提在 Franka/Kinova/Realman/Dobot 机械臂上有实验支持，但对于 dexterous hands、mobile manipulation 或强接触力控制任务，论文没有给出直接证据。

**不知道**：论文没有给出 DOI，也没有在正文中提供 GitHub code link。真实机器人实验每个任务 20 trials，但没有报告 confidence interval、seed 或失败类型分布，因此无法判断部分百分点差距的统计显著性。Sec. 3.1 与 abstract/conclusion 对 pre-training 数据规模存在 100,000 vs. 1 million 的文本不一致，无法仅凭论文判断哪一个是最终准确数字。

## Mind Map

```mermaid
mindmap
  root((A0))
    Problem
      Spatial affordance
        Where to contact
        How to move after contact
      VLA direct action misses precise positions
      Dense affordance can be costly or embodiment-specific
    Method
      Hierarchical model
        High-level affordance understanding
        Low-level action execution
      Embodiment-Agnostic Affordance Representation
        Contact point
        Post-contact trajectories
      DiT diffusion transformer
        SigLiP image encoder
        Qwen2.5 language encoder
        Position Offset Attention
        Spatial Information Aggregation Layer
      Execution
        Depth deprojection
        Grasp sampler
        SE(3) trajectory
    Results
      Franka avg success 62.50
      Kinova avg success 53.75
      Wipe Board Kinova 50
      A0 steps 4 to 5
      VLA steps 25 to 50
      Robopoint MAE lower on HOI4D and DROID
    Limitations
      Grasp sampler dependency
      Depth and VLM height dependency
      Occlusion sensitivity
      Long-horizon needs VLM decomposition
```

## Notes

这篇对我的主要启发是：embodied agent 的 generalization 不一定要从 "更大的 VLA 直接输出动作" 入手，也可以先找一个跨 embodiment 更稳定的中间表示。跨领域类比上，A0 的 affordance representation 有点像 GUI-agent 中的 actionable element + intended interaction trace：先定位可操作区域，再把操作序列交给 executor；这只是研究启发，不是论文实验结论。

但我不会把 A0 解读成已经解决 general robotic manipulation。已知证据主要来自四个 household-style tasks、若干真实机器人平台和 affordance waypoint MAE；论文也承认 grasp、height、orientation 和 long-horizon planning 仍靠外部模块。更稳妥的 takeaway 是：object-centric contact point + post-contact trajectory 是一个值得关注的 embodied affordance bottleneck，尤其适合研究 spatial reasoning 如何转化为 action。
