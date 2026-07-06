---
title: "VQ-VLA: Improving Vision-Language-Action Models via Scaling Vector-Quantized Action Tokenizers"
authors: ["Yating Wang", "Haoyi Zhu", "Mingyu Liu", "Jiange Yang", "Hao-Shu Fang", "Tong He"]
institute: ["Shanghai AI Lab", "Tongji", "USTC", "ZJU", "NJU", "SJTU"]
date_publish: "2025-07-01"
venue: "ICCV 2025"
tags: ["VLA", "manipulation", "imitation-learning"]
url: "https://openaccess.thecvf.com/content/ICCV2025/html/Wang_VQ-VLA_Improving_Vision-Language-Action_Models_via_Scaling_Vector-Quantized_Action_Tokenizers_ICCV_2025_paper.html"
arxiv_id: "2507.01016v1"
doi: ""
cite_key: ""
code: ""
rating: 4
date_added: "2026-06-26"
---
## Summary

VQ-VLA 研究 VLA 中 action tokenization 的 scaling：用 convolutional residual VQ-VAE 把连续多步 robot action sequence 压缩成离散 action tokens，再替换 OpenVLA 的 per-dimension binning tokenizer。核心证据是，使用更大规模的 synthetic trajectory data 训练 action tokenizer 后，OpenVLA 在 LIBERO 和真实 Franka manipulation tasks 上成功率、推理频率和 long-horizon 表现都有提升。

## Problem & Motivation

OpenVLA 等 VLA models 通常把连续 action 的每个维度离散到固定 bins，再由 language-model-style next-token prediction 输出动作；这种表示简单，但会把连续、时序相关的动作拆成大量 token，既影响 inference speed，也容易在 long-horizon rollout 中累积误差。作者的动机是：action trajectory 具有 spatio-temporal continuity，理论上比图像 patch 或语言 token 更容易压缩，因此一个高质量 action tokenizer 可能同时改善 VLA 的表示精度和执行效率。

论文进一步关注 action tokenizer 的 scaling 问题，而不是只提出一个新 tokenizer。作者的关键假设是 synthetic action trajectories 与 real-world action trajectories 的 domain gap 较小，因此可以用 LIBERO、ManiSkill、RLBench 等 simulated data 扩大 tokenizer 训练集，而不必等比例收集昂贵的真实机器人数据。这个假设在文中主要由 LIBERO simulation、Franka real-world tasks 和 Sim&Real domain gap analysis 支撑。

## Method

**Overall pipeline.** VQ-VLA 分两阶段训练：第一阶段训练一个 general convolutional residual VQ-VAE action tokenizer；第二阶段冻结该 tokenizer，把它接入 OpenVLA 7B，用 LoRA fine-tuning 让 VLM 直接预测 VQ-VAE 的 discrete action tokens。VQ-VAE decoder 再把预测出的 tokens 解码成连续动作序列，包括 XYZ positions、Euler angles / orientation 和 gripper states。

**Convolutional residual VQ-VAE.** 输入是 action sequence `a_{t:t+n} in R^{n x d}`。Encoder 使用 2D temporal convolutional layers，而不是简单 MLP，把动作序列编码成 latent embedding；Residual Vector Quantization 把 latent 分解为多层 codebook residuals；Decoder 用 2D temporal deconvolutional layers 重建动作序列。训练目标由 reconstruction loss、VQ codebook loss 和 commitment loss 组成，论文实验中 loss weight `lambda=4`。

**Embedding design.** 在 action sequence 进入 encoder 前，作者加入两类 embedding：sinusoidal time embedding 用于表达不同频率的 temporal pattern；learnable action-type embedding 用于区分 action vector 中 XYZ、Euler angles、gripper states 等不同维度的语义。后续 ablation 显示 embedding 对 LIBERO-90 和真实任务有小幅正收益。

**VLA integration.** 与 OpenVLA 把动作 token 都映射到 `[0,255]` 不同，VQ-VLA 给不同 residual VQ layer 分配 non-overlapping token ID ranges：第 `i` 层 offset 为 `(i-1)*256`，避免不同层中相同 ID 被误认为同一语义。训练 OpenVLA 时，loss 仍是 next-token cross entropy，只是 ground-truth token 来自 frozen Residual VQ-VAE encoder。

**Data scaling strategy.** 论文报告了多种 tokenizer training data 组合：方法部分描述 Open X-Embodiment、Open X-Embodiment+LIBERO、Open X-Embodiment+LIBERO+ManiSkill；simulation 部分为避免 LIBERO-90 evaluation 的 in-domain inflation，又用 out-of-domain ManiSkill 与 ManiSkill+RLBench 训练 tokenizer；real-world 部分则比较 VQO、VQO+L、VQO+L+M。已知结论是更多 synthetic trajectories 通常带来更好 tokenizer；但各实验段落的数据命名不完全统一，复现时需要核对具体配置。

## Key Results

- **LIBERO-10 / LIBERO-GOAL architecture ablation.** Original OpenVLA 在 LIBERO-10 / LIBERO-GOAL 上为 **51.0% / 75.8%**。MLP Residual VQ-VAE 使用 ALL-LIBERO 训练时为 **60.0% / 75.2%**；Conv Residual VQ-VAE 在 LIBERO-10 单 suite 上为 **54.0%**，在 LIBERO-GOAL 单 suite 上为 **72.4%**。作者据此认为 temporal convolution 比 MLP 更适合作为 action tokenizer encoder/decoder，尤其在扩大到 ALL-LIBERO 时更有收益。
- **LIBERO-90 simulation scaling.** 在 LIBERO-90 上，OpenVLA baseline 为 **73.53%**；只用 ManiSkill 训练的 VQM 为 **14.38%**；用 ManiSkill+RLBench 训练的 VQM+R 达到 **80.98%**，比 baseline 高 **7.45 percentage points**。这个结果同时说明 data scale 有帮助，也暴露出只用 ManiSkill 的 tokenizer 会严重退化。
- **Real-world Franka tasks.** 真实平台为 Franka Research 3 + fixed RealSense D435，6 个 manipulation tasks，每个任务 50 demonstrations、20 trials。全任务平均 success rate 从 baseline **23%** 提升到 VQO+L+M 的 **46.25%**；"Flip the pot upright" 任务提升 **30 percentage points**；long-horizon "Put all cups in the basket" / "Put the toy into the drawer" 中，baseline 低至约 **15% / 0%**，VQO+L+M 达到 **50% / 30%**。
- **Sim&Real domain gap analysis.** 在三个真实任务上，baseline / VQO / VQL / VQO+L / VQO+L+M 的结果分别为：Put the toy into the drawer **5.0 / 15.0 / 10.0 / 10.0 / 25.0%**，Flip the pot upright **30.0 / 45.0 / 55.0 / 45.0 / 60.0%**，Put the toy into the basket **20.0 / 35.0 / 35.0 / 35.0 / 45.0%**。VQL 只用 LIBERO 训练却与 VQO、VQO+L 接近，是作者提出 synthetic-real action domain gap 较小的主要证据之一。
- **Inference speed.** 在真实实验中，VQ-VLA 的 action execution frequency 为 **11.84 Hz**，OpenVLA 为 **4.16 Hz**；论文把这个近三倍提升归因于 VQ-VAE 以 compression ratio 5 解码多步 action sequence，而不是逐步预测单个 action。
- **Action chunking ablation.** 在 LIBERO-90 / Flip the pot upright / Put the toy into the basket 三个任务上，baseline 为 **74.76% / 30.0% / 20.0%**；OpenVLA autoregressive output chunking 降到 **66.53% / 10.0% / 0.0%**；VQ-based chunking (VQO+L+M) 达到 **86.61% / 60.0% / 45.0%**。这说明收益不是简单来自输出 K=5 action chunk，而是 VQ-based action representation 本身更有效。
- **Embedding ablation.** VQO+L 不加 embeddings 时，在 LIBERO-90 / Flip the pot upright / Put the toy into the basket 上为 **85.17% / 40.0% / 35.0%**；加入 time embedding 和 action-type embedding 后为 **86.16% / 45.0% / 35.0%**。

## Strengths & Weaknesses

**已知 Strengths.** 这篇的主要价值在于把 VLA efficiency 和 long-horizon reliability 归结到 action representation/tokenization，而不是只继续扩大 VLM backbone。方法上，frozen action tokenizer + LoRA fine-tuning OpenVLA 是相对简洁的接口，能直接替换 OpenVLA 的 binning tokenization；实验也覆盖 LIBERO simulation、真实 Franka tasks、inference frequency、action chunking 和 embedding ablation。对 embodied/VLA 研究来说，"scaling action tokenizer with cheap synthetic trajectories" 是一个值得关注的问题 formulation。

**已知 Weaknesses / boundary.** Baseline 主要围绕 OpenVLA 和作者自定义的 VQ variants，没有系统比较 FAST、diffusion-policy-style action heads 或更强的 VLA action tokenizer baselines。真实实验规模仍较小：6 个 manipulation tasks、每个任务 50 demonstrations、20 evaluation trials，且平台固定为单 Franka Research 3；还不知道在 bimanual、mobile manipulation、cross-embodiment 或更开放的 household setting 下是否稳定。论文声称 synthetic-real domain gap marginal/minimal，但直接证据主要来自三个真实任务上的 success rate 接近，而不是更细的 action distribution、failure taxonomy 或跨仿真器分析。

**局限与 failure cases.** 原文明确列出未来工作：action tokenizer 可以扩展到更大规模 simulated datasets，如 RLBench/CoppeliaSim；multi-step decoding 带来的 speedup 还可与 VLM distillation、quantization 结合；tokenizer architecture 也可继续改进，例如把 action data frequency 作为额外条件。文中还报告了一个负结果：只用 ManiSkill 训练的 VQM 在 LIBERO-90 只有 **14.38%**，远低于 OpenVLA baseline **73.53%**，说明 synthetic data 并非越多越好，数据覆盖与分布组合很关键。

**推测.** 对 GUI-agent / computer-use agent 的间接启发是：如果 action space 具有强时序连续性或可组合 skill chunks，学习 action tokenizer 可能比逐 token 输出低层 action 更稳定。但这是从机器人连续控制外推，论文没有在 GUI grounding、web/mobile agent 或离散 UI action benchmark 上验证。

**不知道.** 不知道 VQ-VLA 的失败样本具体来自 perception、language grounding、tokenizer reconstruction error、VLM token prediction error 还是 low-level control mismatch；论文没有给出 systematic failure case taxonomy。也不知道 code / project website 的具体 URL，正文只出现 "Project website" 字样但未给出可摘录链接；DOI 在正文中未见。

## Mind Map

```mermaid
mindmap
  root((VQ-VLA))
    Problem
      OpenVLA binning tokenization is inefficient
      Long-horizon rollout accumulates action errors
      Action trajectories are compressible
      Synthetic action data may scale tokenizer training
    Method
      Conv Residual VQ-VAE
        Temporal convolution encoder
        Residual VQ codebooks
        Temporal deconvolution decoder
      Embeddings
        Sinusoidal time embedding
        Action-type embedding
      OpenVLA integration
        Frozen tokenizer
        Non-overlapping token ID ranges
        LoRA fine-tuning
      Data scaling
        Open X-Embodiment
        LIBERO
        ManiSkill
        RLBench
    Results
      LIBERO-90 VQM+R 80.98 vs OpenVLA 73.53 percent
      Real-world average 46.25 vs 23 percent
      VQ-VLA frequency 11.84 Hz vs OpenVLA 4.16 Hz
      VQ chunking 86.61 on LIBERO-90 vs autoregressive 66.53
```

## Notes

- 对 VLA 方向最有用的 takeaway：action tokenizer 本身可以作为可 scaling 的模块，而不必每次都扩大 policy/VLM backbone；尤其当动作轨迹可压缩、synthetic trajectories 便宜时，这条路线有工程吸引力。
- 需要谨慎的地方：论文把 "synthetic-real domain gap is minimal" 写得较强，但目前证据更多是 success rate 层面的间接证据；如果要作为后续研究假设，应补充 tokenizer reconstruction error、token usage distribution 和 failure cases。
- 复现关注点：先核对不同实验中 VQO/VQO+L/VQO+L+M、VQM/VQM+R 对应的数据组合；其次确认 action frequency、chunk length K=5、codebook layers/token ID offset 与 OpenVLA vocabulary replacement 的实现细节。
