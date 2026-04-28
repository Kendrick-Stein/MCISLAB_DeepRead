---
title: "Scale-Invariant GUI Grounding via Multi-Resolution Feature Pyramid"
tags: [gui-agent, grounding, visual-representation, resolution-robustness]
status: raw
linked_project:
date_updated: "2026-04-28"
---

## Hypothesis

若在 GUI grounding 模型中引入 multi-resolution feature pyramid 和 resolution-adaptive anchor points，使模型在训练时暴露于多种分辨率和缩放尺度，则 grounding 精度在分辨率/布局变化场景下的退化幅度将显著减小。可证伪预测：在 ScreenSpot-Pro 的跨分辨率子集上，scale-invariant 模型的 grounding accuracy 相比同参数量的标准 grounding 模型提升 >20%（绝对），且在高分辨率场景下不损失精度。

## Motivation

**知识空白**：GUIAgent-Survey 指出 Grounding 是 GUI Agent 的"基础瓶颈"，而跨域/跨分辨率稳定性是 grounding 的核心未解决问题。Continual GUI Agents 提出了 Anchoring Point Reward (APR-iF) 在分布漂移中保持 grounding，但该方法在 RL 训练层面工作，未从模型架构层面解决分辨率不变性问题。GoClick 展示了小模型（230M）可达大模型精度，但其 encoder-decoder 架构未显式建模多尺度特征。

**为什么重要**：真实部署中，同一 app 在不同设备（手机/平板/桌面）、不同分辨率、不同 DPI 下呈现截然不同的像素布局。若 grounding 模型对分辨率敏感，则每换一个设备就需要重新适配——这与"跨平台统一 agent"的趋势矛盾。架构级的 scale invariance 是 grounding 泛化的基础。

**时机**：GoClick 证明了专门设计的 grounding 架构（而非通用 VLM）可以高效解决 grounding；GUI-Actor 证明了 patch-level 预测优于 text-coordinate 生成。Multi-resolution feature pyramid 在目标检测中成熟（FPN, 2017），但在 GUI grounding 中未被系统探索。

## Related Work

- [[Papers/2604-GoClick]] - 轻量级 GUI element grounding (230M), encoder-decoder, Progressive Data Refinement
- [[2500-GuiActorCoordinateFree]] - Coordinate-free grounding, patch-level attention prediction
- [[2400-SeeclickHarnessingGuiGrounding]] - GUI grounding pre-training, screen-only input
- [[2600-ContinualGuiAgents]] - Anchoring Point Reward for grounding under distribution shift
- [[Papers/2604-AutoGUIv2]] - 揭示 VLM 在 grounding vs captioning 上的二分性
- [[2025-MMBench-GUI- Hierarchical Multi-Platform Evaluation Framework for GUI Agents]] - 跨平台评测框架

**Novelty**: 将成熟的目标检测架构（FPN + multi-scale anchors）适配到 GUI grounding 的独特需求：(1) GUI 元素尺度差异极大（图标 16×16 到全屏 banner）；(2) 文本元素需要 sub-pixel 精度；(3) 需要在不同设备的极端分辨率变化下保持鲁棒。现有 GUI grounding 工作（GoClick, GUI-Actor, SeeClick）均未显式设计 multi-scale 架构。

## Approach sketch

**Architecture Design**
- Backbone: 轻量级 vision encoder（如 MobileNetV4 或 SigLIP-small），输出 multi-scale feature maps (P3-P7)
- Feature Pyramid Network (FPN): 自顶向下路径 + 横向连接，融合高语义低分辨率与低语义高分辨率特征
- Grounding Head: 参考 GUI-Actor 的 attention-based prediction，但在每个 FPN level 上独立预测，最后通过 scale-aware fusion 合并
- Resolution-Adaptive Anchors: anchor 尺寸不再固定像素值，而是以屏幕相对坐标表示（如宽度的 2%-80%）

**Training Strategy**
- **Multi-Resolution Training**: 每个 batch 中随机采样 3-5 种分辨率（如 720p, 1080p, 1440p, 2K），同一 screenshot 以不同分辨率输入
- **Scale Augmentation**: 在训练中随机 crop + resize，模拟不同设备上的元素尺度变化
- **Consistency Loss**: 同一 screenshot 在不同分辨率下的 grounding 预测应一致，添加 KL 散度或 L2 consistency loss

**Evaluation Protocol**
- ScreenSpot-Pro 跨分辨率子集（已有多种分辨率的 grounding 标注）
- 构造分辨率压力测试：在标准分辨率训练，在低分辨率/高分辨率/非标准比例下测试
- 对比 GoClick（单尺度）、GUI-Actor（单尺度）、通用 VLM（Qwen2.5-VL）在分辨率变化下的精度退化曲线

## Expected outcome

- ScreenSpot-Pro 跨分辨率子集 accuracy 比 GoClick baseline 提升 >20%（绝对）
- 分辨率从 1080p 降至 720p 时，精度退化 <5%（baseline 通常退化 15-20%）
- 模型参数量控制在 <500M，保持 on-device 部署可行性
- Consistency loss 的 ablation 证明其对跨分辨率泛化的关键作用

## Risk

- **FPN 增加计算开销**：multi-scale 特征提取可能抵消小模型的延迟优势。缓解：使用轻量级 FPN 变体（如 BiFPN-lite），仅在推理时使用 single-scale（训练时 multi-scale 作为正则化）。
- **GUI 特有的尺度分布**：GUI 元素的尺度分布可能与自然图像不同，FPN level 分配需要专门调优。缓解：先在 ScreenSpot 上统计分析元素尺度分布，再设计 anchor 和 FPN level 配置。
- **训练数据构造**：需要同一 screenshot 的多种分辨率版本，可能增加数据准备成本。缓解：在线 resize 即可，无需预生成。

## Evaluation (2026-04-28)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 3/5 | FPN approach underexplored in GUI grounding. Competitors use zoom-in (MEGA-GUI), data strategy (Qwen-GUI-3B), positional encoding (RULER/I-MRoPE), Gaussian (GUI-G²) — none are FPN. But FPN itself is mature CV tech (2017). Closest works: Qwen-GUI-3B, MEGA-GUI, RULER/I-MRoPE, GUI-G² |
| Feasibility | 4/5 | FPN mature, GoClick provides baseline architecture, online resize eliminates data bottleneck. Low engineering complexity. |
| Impact | 3/5 | If FPN provides "free" cross-resolution robustness (no zoom-in overhead), meaningful. Competitive space. |
| Risk | 3/5 | FPN may not beat data augmentation alone. But complementary to zoom-in approaches (can be combined). |
| Evidence | 3/5 | GoClick proves specialized grounding architectures work. FPN proven in CV. GUI-G² shows element scale variance is real. Indirectly supportive. |
| **Total** | **16/25** | |

**Novelty**: 3/5 — closest works: Qwen-GUI-3B (cross-resolution data strategy), MEGA-GUI (zoom-in pipeline), RULER/I-MRoPE (positional encoding fix), GUI-G² (Gaussian scale modeling). None use FPN for GUI grounding.

**Reasoning**: Better positioned than the Credit Assignment idea. FPN has a clear technical niche — no competitor uses explicit feature pyramids for GUI grounding, though many attack cross-resolution robustness from other angles. Lower engineering complexity and complementary nature reduce risk. Main weakness: FPN novelty is limited (mature CV technique), and it may not beat data augmentation alone. Start with minimal prototype: add FPN to GoClick + consistency loss.

**Suggested next action**: Prototype FPN + GoClick on ScreenSpot multi-resolution subset to validate the architectural prior hypothesis.
