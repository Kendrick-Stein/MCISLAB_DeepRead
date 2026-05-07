---
title: "Scale-Invariant GUI Grounding via Multi-Resolution Feature Pyramid"
idea: "[[Ideas/ScaleInvariant-Grounding-GUI]]"
tags: [gui-agent, grounding, visual-representation, resolution-robustness]
status: planned
date_created: "2026-04-29"
date_updated: "2026-05-07"
date_completed:
---
## Objective

验证 multi-resolution feature pyramid (FPN) + resolution-adaptive anchors 是否能显著提升 GUI grounding 在跨分辨率场景下的鲁棒性。核心假设：架构级 multi-scale 设计可在不增加推理开销的前提下，使 grounding 模型在不同设备/分辨率下保持精度稳定。

## Setup

- **代码**: 基于 GUI-Actor (microsoft/GUI-Actor-2B-Qwen2-VL) attention-based grounding 架构，添加 FPN module
- **数据**: ScreenSpot-Pro（含多分辨率测试场景）
- **环境**: 单卡 A100 或等效 GPU
- **关键参数**: FPN levels P3-P7，resolution range [720p, 1080p, 1440p, 2K]
- **更新原因**: GoClick 代码未公开（阻塞），改用 GUI-Actor（开源、有 HuggingFace checkpoint）

## Method

### 实验步骤

1. **Baseline 架构搭建**
   - 加载 GUI-Actor-2B-Qwen2-VL checkpoint（开源，HuggingFace）
   - 验证 ScreenSpot-Pro baseline performance（预期 ~40.7）
   - GUI-Actor 架构：VLM backbone + <ACTOR> token + attention-based action head

2. **FPN 集成设计**
   - 在 Qwen2-VL visual encoder 输出端插入 FPN（自顶向下 + 横向连接）
   - FPN 输出 multi-scale feature maps → <ACTOR> token 在各 level 计算 attention
   - Multi-level attention maps 通过 scale-aware fusion 合并（加权或 max-pooling）
   - 关键：FPN 位于 visual encoder 和 <ACTOR> attention head 之间，保持 coordinate-free 设计

3. **Resolution-Adaptive Patch Supervision**
   - GUI-Actor 的 Spatial-Aware Multi-Patch Supervision 自然支持区域级监督
   - 增强：在不同分辨率下，目标元素映射到不同数量 patches，但 supervision 区域保持语义一致

4. **Multi-Resolution Training**
   - 训练时随机采样 3-5 种分辨率（720p, 1080p, 1440p, 2K）
   - 同一 screenshot resize 到不同分辨率输入
   - Consistency Loss: KL 散度约束不同分辨率下 <ACTOR> attention 分布一致

5. **Evaluation**
   - ScreenSpot-Pro 全集（含 unseen resolution/layout）
   - 分辨率压力测试：在 1080p 训练，在 720p/1440p/2K 测试
   - 对比 GUI-Actor baseline（无 FPN）在分辨率变化下的退化曲线

### Baselines

- **GUI-Actor** (`[[Papers/2500-GuiActorCoordinateFree]]`): Coordinate-free attention-based grounding，Qwen2-VL backbone（开源，主 baseline）
- **SeeClick** (`[[2400-SeeclickHarnessingGuiGrounding]]`): 单尺度 GUI grounding pre-training
- **Qwen2.5-VL (通用 VLM)**: 无专门 grounding 训练，对比专门架构 vs 通用 VLM

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

- **自变量（Independent Variable）**: 是否添加 FPN + multi-resolution training（w/ FPN vs. w/o FPN）
- **因变量（Dependent Variable）**: 
  - Grounding accuracy at different resolutions (ScreenSpot-Pro)
  - Cross-resolution accuracy degradation
- **控制变量（Controlled Variable）**:
  - Base model（GUI-Actor-2B-Qwen2-VL，冻结 backbone）
  - Training data（ScreenSpot train split）
  - FPN 新增参数量（控制在 ~50M 以内）
  - Random seeds（固定 3 个种子取均值）

### Metrics

- **Primary Metric**: Grounding accuracy on ScreenSpot-Pro (%)
  - 定义：正确定位目标元素的样本比例（coordinate-free 判定：目标 patch 被选中）
  - 细分：按分辨率分组统计（低分辨率 / 标准分辨率 / 高分辨率）
  
- **Secondary Metrics**:
  - Cross-resolution degradation: accuracy@1080p - accuracy@720p (%)
  - OOD resolution accuracy（unseen resolution layout）
  - Inference latency (ms/sample) - 验证 FPN 是否增加推理开销

### Baselines

1. **GUI-Actor** (`[[Papers/2500-GuiActorCoordinateFree]]`)
   - 2B Qwen2-VL backbone，coordinate-free attention-based grounding
   - 公平对比：相同 backbone，相同训练数据，仅增加 FPN
   
2. **SeeCLICK** (`[[2400-SeeclickHarnessingGuiGrounding]]`)
   - 单尺度 GUI grounding pre-training
   - 对比点：multi-scale architecture vs single-scale pre-training
   
3. **Qwen2.5-VL (通用 VLM)**
   - 无专门 grounding 训练
   - 对比点：专门 grounding 架构 vs 通用 VLM

### Expected Outcome

**假设成立（Hypothesis Confirmed）**:
- w/ FPN 在 ScreenSpot-Pro 上 accuracy 比 GUI-Actor baseline 提升 ≥5%（绝对值，如 40.7→45.7）
- 分辨率从 1080p 降至 720p 时，精度退化 <5%（baseline 通常退化 10-15%）
- OOD resolution accuracy 显著高于 baseline（证明 cross-resolution 泛化）
- 推理 latency 增加不超过 15%（FPN overhead acceptable）

**假设不成立（Hypothesis Refuted）**:
- 若 accuracy 提升 <2% 且退化仍 >8%，说明 FPN 对 GUI-Actor 的 coordinate-free 设计帮助有限
- 解读：GUI-Actor 的 patch-level attention 可能已经隐式处理了部分尺度变化，显式 FPN 增益不显著
- 下一步：(1) 结合 FPN 与 zoom-in（MEGA-GUI 风格）做 hybrid；(2) 或转向 resolution-aware positional encoding（如 RULER）

### Risk & Mitigation

1. **FPN 与 coordinate-free attention 不兼容**
   - 风险：FPN 设计用于 dense prediction（如检测），GUI-Actor 是 sparse attention prediction，二者可能冲突
   - 概率：medium
   - 应对：先做 minimal prototype（仅加 FPN 到 visual encoder，保持 <ACTOR> attention 不变），验证兼容性

2. **FPN 增加计算开销过高**
   - 风险：multi-scale 特征提取显著增加推理 latency
   - 概率：medium
   - 应对：使用轻量 FPN（如 BiFPN-lite）；训练时 multi-scale，推理时可选 single-scale

3. **GUI-Actor backbone frozen 导致 FPN 学习不充分**
   - 风险：冻结 VLM backbone，FPN 新参数难以学到有效的 multi-scale representation
   - 概率：low
   - 应对：先 unfreeze FPN 相关层，观察效果；必要时可 unfreeze 部分 backbone

4. **ScreenSpot 缺乏多分辨率标注**
   - 风险：难以量化 cross-resolution 泛化
   - 概率：medium
   - 应对：在线 resize 构造多分辨率测试；或补充 WindowsWorld benchmark（跨应用、多分辨率）

### Memory Reference

**From patterns.md**:
- Small specialized models can match large models on GUI grounding → 支持轻量化 baseline
- VLM capabilities are fragmented across sub-tasks → grounding 需专门架构
- Evaluation methodology shifting to multi-dimensional diagnosis → 需多维度 metric

**From insights.md**:
- VLM grounding vs captioning capability dichotomy → fine-tuning on agent data 对 grounding 有增益

**Update log**:
- 2026-05-07: GoClick code unavailable → baseline 改为 GUI-Actor（开源、有 checkpoint）