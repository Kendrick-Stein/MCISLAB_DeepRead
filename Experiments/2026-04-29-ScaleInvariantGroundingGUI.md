---
title: "Scale-Invariant GUI Grounding via Multi-Resolution Feature Pyramid"
idea: "[[Ideas/ScaleInvariant-Grounding-GUI]]"
tags: [gui-agent, grounding, visual-representation, resolution-robustness]
status: planned
date_created: "2026-04-29"
date_completed:
---
## Objective

验证 multi-resolution feature pyramid (FPN) + resolution-adaptive anchors 是否能显著提升 GUI grounding 在跨分辨率场景下的鲁棒性。核心假设：架构级 multi-scale 设计可在不增加推理开销的前提下，使 grounding 模型在不同设备/分辨率下保持精度稳定。

## Setup

- **代码**: 基于 GoClick encoder-decoder 架构，添加 FPN module
- **数据**: ScreenSpot-Pro 跨分辨率子集（需确认是否存在，否则构造）
- **环境**: 单卡 A100 或等效 GPU
- **关键参数**: FPN levels P3-P7，resolution range [720p, 1080p, 1440p, 2K]

## Method

### 实验步骤

1. **Baseline 架构搭建**
   - 复现 GoClick encoder-decoder（230M 参数）
   - 在 ScreenSpot train split 上训练，获得 baseline checkpoint

2. **FPN 添加**
   - 在 GoClick encoder 输出端添加 FPN（自顶向下 + 横向连接）
   - FPN levels: P3-P7（对应 1/8 到 1/128 stride）
   - Grounding head 在每个 level 独立预测，scale-aware fusion 合并

3. **Resolution-Adaptive Anchors**
   - Anchor 尺寸以屏幕相对坐标表示（宽度的 2%-80%）
   - 替代固定像素值 anchor

4. **Multi-Resolution Training**
   - 训练时随机采样 3-5 种分辨率
   - 同一 screenshot 以不同分辨率输入
   - Consistency Loss: KL 散度约束不同分辨率预测一致

5. **Evaluation**
   - ScreenSpot-Pro 跨分辨率 test set
   - 分辨率压力测试：在 1080p 训练，在 720p/1440p/2K 测试

### Baselines

- **GoClick** (`[[Papers/Archive/2604-GoClick]]`): 单尺度 encoder-decoder，230M 参数
- **MEGA-GUI** (`[[Papers/2500-MegaGuiMultiStage]]`): zoom-in pipeline，multi-stage
- **GUI-Actor** (`[[2500-GuiActorCoordinateFree]]`): patch-level attention prediction

## Results

（待实验完成后填写）

## Analysis

（待实验完成后填写）

## Insights

（待实验完成后填写）

## Next Steps

若假设不成立（精度退化仍 >10%），考虑：
1. 修改 FPN level 配置（增加更高分辨率 level）
2. 结合 MEGA-GUI 的 zoom-in pipeline 与 FPN（hybrid approach）
3. 重新审视 consistency loss 设计

---

## Design Notes

### Variables

- **自变量（Independent Variable）**: 是否添加 FPN + resolution-adaptive anchors（w/ FPN vs. w/o FPN）
- **因变量（Dependent Variable）**: 
  - Grounding accuracy at different resolutions
  - Cross-resolution accuracy degradation
- **控制变量（Controlled Variable）**:
  - Base model（GoClick encoder-decoder，230M）
  - Training data（ScreenSpot train split）
  - Training epochs（固定）
  - Random seeds（固定 3 个种子取均值）

### Metrics

- **Primary Metric**: Grounding accuracy on cross-resolution test set (%)
  - 定义：正确定位目标元素的样本比例
  - 细分：720p accuracy / 1080p accuracy / 1440p accuracy / 2K accuracy
  
- **Secondary Metrics**:
  - Cross-resolution degradation: accuracy@1080p - accuracy@720p (%)
  - Inference latency (ms/sample) - 验证 FPN 是否增加推理开销
  - Model size (MB) - 确认参数量仍在 on-device 范围

### Baselines

1. **GoClick** (`[[Papers/Archive/2604-GoClick]]`)
   - 230M encoder-decoder，单尺度
   - 公平对比：相同参数规模、相同训练数据
   
2. **MEGA-GUI** (`[[Papers/2500-MegaGuiMultiStage]]`)
   - Zoom-in pipeline，推理时多阶段
   - 对比点：架构级 FPN vs inference-time zoom
   
3. **GUI-Actor** (`[[2500-GuiActorCoordinateFree]]`)
   - Patch-level attention，coordinate-free
   - 对比点：multi-scale architecture vs coordinate-free approach

### Expected Outcome

**假设成立（Hypothesis Confirmed）**:
- w/ FPN 在 ScreenSpot-Pro 跨分辨率子集上 accuracy 比 GoClick baseline 提升 ≥20%（绝对值，如 50%→70%）
- 分辨率从 1080p 降至 720p 时，精度退化 <5%（baseline 通常退化 15-20%）
- 推理 latency 增加不超过 10%（FPN overhead minimal）

**假设不成立（Hypothesis Refuted）**:
- 若 accuracy 提升 <10% 且退化仍 >10%，说明 FPN 对 GUI grounding 的 resolution invariance 问题帮助有限
- 解读：GUI 元素的尺度分布可能与自然图像不同，FPN level 分配需要专门调优
- 下一步：分析 ScreenSpot 元素尺度分布，重新设计 FPN level；或结合 zoom-in 与 FPN

### Risk & Mitigation

1. **FPN 增加计算开销**
   - 风险：multi-scale 特征提取可能抵消小模型的延迟优势
   - 概率：medium
   - 应对：使用轻量 FPN 变体（BiFPN-lite）；训练时 multi-scale 作为正则化，推理时 single-scale
   
2. **ScreenSpot 跨分辨率子集不存在**
   - 风险：需构造数据，增加实验成本
   - 概率：medium
   - 应对：在线 resize 即可，无需预生成；可先用 ScreenSpot 验证单尺度 baseline
   
3. **FPN 对 GUI 元素尺度分布不适配**
   - 风险：GUI 元素尺度差异可能超出 FPN designed range（如 16×16 icon vs 全屏 banner）
   - 概率：medium
   - 应对：先分析 ScreenSpot 元素尺度分布，调整 anchor 和 FPN level 配置

### Memory Reference

**From patterns.md**:
- Small specialized models can match large models on GUI grounding（GoClick 230M ≈ large VLM）→ 支持轻量化 baseline 选择
- VLM capabilities are fragmented across sub-tasks → grounding 可能需要专门架构而非通用 VLM

**No specific effective-methods/failed-directions memory file exists** - this experiment design is based on idea evaluation and paper analysis.