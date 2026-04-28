---
title: VLM Survey
tags: [survey, VLM, multimodal, vision-language-model, visual-reasoning]
date_updated: "2026-04-28"
year_range: 2023-2026
papers_analyzed: 15
---

## Overview

Vision Language Model (VLM) / Multimodal Large Language Model (MLLM) 是当前 AI 研究中最活跃的方向之一，旨在让模型同时理解视觉和语言信息，实现跨模态的推理、问答、生成和决策能力。自 2023 年以来，该领域经历了从单一图文匹配到复杂多模态推理、从闭源系统到开源生态、从纯理解到理解-生成统一的快速演进。

**核心挑战**：VLM 面临三大关键瓶颈：

1. **视觉表征与语言对齐**：如何让视觉编码器的输出与 LLM 的语义空间有效对齐，实现细粒度的图文理解（尤其是文本密集场景如文档、GUI）
2. **分辨率与细节感知**：传统 VLM 使用固定分辨率输入（如 224x224），难以识别 GUI 中的小字号文本、图标等细粒度元素
3. **理解与生成的统一**：多数 VLM 只做理解任务，生成任务依赖独立的 diffusion 模型，两者之间存在表征不对齐问题

**研究趋势**：2023-2026 年 VLM 领域经历了四个重要演进阶段：
- **基础架构探索（2023）**：CLIP、BLIP 等视觉-语言对齐框架成熟；LLaVA 开启 instruction-following VLM 路线
- **能力扩展期（2024）**：高分辨率 VLM（CogAgent 1120x1120）、专业领域 VLM（MobileFlow）、VLM for grounding 成为热点
- **统一模型期（2025）**：理解+生成统一模型涌现（LLaDA2.0-Uni、Unify-Agent）；VLM 作为 agent backbone 广泛应用
- **效率与对齐优化期（2026）**：KV cache 优化（GUI-KV）、human preference alignment、安全防御（LaSM）

---

## 技术路线

### 2.1 高分辨率视觉编码路线

**代表论文**：[[2312-CogagentVisualLanguageModel]]、[[2400-MobileflowMultimodalLlmMobile]]、[[2400-SeeclickHarnessingGuiGrounding]]

**核心思路**：针对 GUI、文档等文本密集场景，引入高分辨率视觉编码器（≥1120x1120），实现对小字号文本、细图标、密集控件的精准识别。

**关键设计**：
- **CogAgent**：双分辨率图像编码器（low-res + high-res），18B 参数，支持 1120x1120 输入，在 9 个 VQA benchmark 和 Mind2Web/AITW GUI 导航上达到 SOTA
- **MobileFlow**：Hybrid visual encoder + MoE 扩展，21B 参数，专为移动端 GUI 设计，强调中文/多语言支持
- **SeeClick**：Grounding pre-training + screen-only 输入，实现跨平台 GUI grounding

**优势**：解决传统 VLM 在文本密集场景的分辨率瓶颈；跨平台通用性强（不依赖 DOM/HTML）
**局限**：高分辨率输入导致计算开销显著增加；训练和推理资源消耗大

### 2.2 Zero-shot / Agent-based Grounding 路线

**代表论文**：[[2400-VlmGrounderVlmAgent]]、[[2400-TowardsVisualGroundingSurvey]]

**核心思路**：利用 VLM 的 zero-shot 能力，通过 agent 式交互（grounding-and-feedback）逐步定位目标，无需专门训练 3D grounding 网络。

**关键设计**：
- **VLM-Grounder**：动态拼接多视角图像 + grounding-and-feedback 机制 + multi-view ensemble projection，实现 zero-shot 3D visual grounding（ScanRefer 51.6% Acc@0.25）
- **Visual Grounding Survey**：系统梳理 fully supervised、weakly supervised、zero-shot、multi-task、generalized grounding 等多种研究设定

**优势**：无需 3D 标注数据；充分利用现有 VLM 的 2D 理解能力；适合数据稀缺场景
**局限**：多阶段 pipeline 存在误差传播；计算开销不低（多视角处理 + 多轮 VLM 调用）

### 2.3 理解-生成统一路线

**代表论文**：[[2604-LLaDA2Uni]]、[[2600-UnifyAgentUnifiedMultimodal]]

**核心思路**：将多模态理解和生成统一在单一框架内，避免传统系统中理解模块与生成模块的表征不对齐问题。

**关键设计**：
- **LLaDA2.0-Uni**：Discrete tokenizer + MoE dLLM backbone + diffusion decoder，实现原生统一的多模态理解+生成，支持 interleaved generation + reasoning
- **Unify-Agent**：认知缺口检测 + 多模态证据检索 + grounded recaptioning + 图像生成，将 world-grounded synthesis 重构为 agent 流程
- **VLV Auto-Encoder**：视觉编码器 + T2I diffusion decoder + LLM，通过知识蒸馏实现低成本高质量图像描述

**优势**：理解与生成能力可互相增强；支持 interleaved multimodal reasoning；更接近 AGI 范式
**局限**：MoE + diffusion 组合的显存和推理速度挑战；训练复杂度高

### 2.4 Human Preference Alignment 路线

**代表论文**：[[2500-AligningMultimodalLlmHuman]]

**核心思路**：将 LLM alignment 技术（如 RLHF、DPO）迁移到多模态场景，优化 VLM 在真实性、安全性、推理能力上的表现。

**关键设计**：
- 对齐数据集构建：数据来源、模型响应、偏好标注
- 应用场景：一般图像理解、多图像、视频、音频等
- 评估基准：多模态场景下的对齐效果评测

**优势**：提升 VLM 与人类意图的一致性；改善安全性和可控性
**局限**：多模态偏好标注成本高；跨模态对齐信号难以精确定义

### 2.5 效率优化路线

**代表论文**：[[2500-GuiKvEfficientGui]]、[[2500-LasmLayerWiseScaling]]

**核心思路**：针对 VLM 在长序列高分辨率输入下的计算瓶颈，通过 KV cache 压缩、layer-wise scaling 等技术降低推理开销。

**关键设计**：
- **GUI-KV**：空间显著性引导 + 时间冗余评分，实现 38.9% 解码 FLOPs 降低 + 4.1% 步骤准确率提升
- **LaSM**：Layer-wise scaling mechanism，通过 attention + MLP 联合缩放防御 pop-up attack（defense success rate 74.8%-100%）

**优势**：无需重新训练；plug-and-play；低部署成本
**局限**：缩放系数和关键层范围具有 model-specific 特性；对闭源模型难以应用

---

## Datasets & Benchmarks

| Dataset/Benchmark | 任务类型 | 规模 | 评估指标 | SOTA | 特点 |
|:------------------|:---------|:-----|:---------|:-----|:-----|
| **VQAv2** | Visual QA | ~200K questions | Accuracy | GPT-4V 领先 | 自然图像问答基准 |
| **TextVQA** | Text-rich QA | ~28K questions | Accuracy | CogAgent SOTA | 文本密集场景问答 |
| **DocVQA** | Document QA | ~50K questions | ANLS | CogAgent SOTA | 文档理解基准 |
| **MM-Vet** | Multimodal evaluation | ~2K tasks | MM-Vet score | GPT-4V 领先 | 综合多模态评测 |
| **POPE** | Hallucination | ~3K images | Accuracy | CogAgent SOTA | 幻觉检测基准 |
| **MME** | Multimodal evaluation | 14 subtasks | Perception + Cognition | 多模型评测 | 感知+认知分离评测 |
| **MMMU** | Multi-discipline | ~12K questions | Accuracy | GPT-4V 领先 | 大学级多学科问答 |
| **ScanRefer** | 3D Grounding | ~51K descriptions | Acc@0.25 | VLM-Grounder: 51.6% | 3D visual grounding |
| **Nr3D** | 3D Grounding | ~41K descriptions | Acc | VLM-Grounder: 48.0% | 3D referring expression |
| **Mind2Web** | Web Navigation | ~2K tasks | Success Rate | CogAgent SOTA | Web agent benchmark |
| **AITW** | Android Navigation | ~560K episodes | Action Accuracy | CogAgent SOTA | 移动端操作 benchmark |
| **ScreenSpot** | GUI Grounding | Multi-platform | Accuracy | SeeClick/GUI-Actor SOTA | GUI grounding 评测 |
| **RefCOCO** | 2D Grounding | ~50K expressions | Acc@0.5 | 多模型竞争 | 经典 referring expression |
| **FactIP** | World-grounded Generation | 12 categories | Human preference | Unify-Agent 接近 closed-source | 长尾概念生成评测 |

**Benchmark 演进趋势**：
- 从自然图像问答（VQAv2）到文本密集场景（TextVQA、DocVQA）
- 从 2D grounding（RefCOCO）到 3D grounding（ScanRefer、Nr3D）
- 从单一模态评测到多学科综合评测（MMMU）
- 从理解任务到理解+生成统一评测（FactIP）

---

## Key Takeaways

1. **高分辨率视觉编码是 VLM 在文本密集场景的关键突破**：CogAgent、MobileFlow 等证明，支持 ≥1120x1120 输入的双分辨率编码器可显著提升 GUI、文档等场景的理解能力。这解决了传统 VLM 固定分辨率（224x224）的瓶颈。

2. **Zero-shot grounding 利用 VLM agent 能力而非专门训练**：VLM-Grounder 展示了通过动态拼接 + feedback loop + multi-view ensemble，无需 3D 训练数据即可实现较强的 3D grounding。这条路线适合数据稀缺场景。

3. **理解-生成统一是 VLM 发展的明确趋势**：LLaDA2.0-Uni、Unify-Agent 等工作将多模态理解和生成放在同一框架，避免了两阶段系统的表征不对齐问题。Discrete diffusion + MoE 是当前主流架构选择。

4. **Human preference alignment 开始向多模态迁移**：将 RLHF/DPO 技术迁移到 VLM，优化真实性、安全性、推理能力，是当前 VLM 走向可靠部署的关键一步。

5. **效率优化技术（KV cache、layer-wise scaling）可在不重新训练的前提下显著降低开销**：GUI-KV、LaSM 等工作证明，通过 inference-time intervention 可实现计算效率提升和安全性增强，部署门槛低。

6. **VLM 正从被动理解器走向主动 agent backbone**：GUI Agent、3D grounding agent、world-grounded synthesis agent 等工作表明，VLM 不只是"看图说话"，而是可以成为多模态 agent 的感知与决策核心。

---

## Open Problems

### 5.1 核心技术挑战

1. **长上下文多模态推理的瓶颈**：当前 VLM（如 CogAgent、LLaVA）在处理长序列图像、多视角输入时面临 context window 限制。虽然 GUI-KV 等尝试压缩 KV cache，但如何在保持理解质量的前提下支持超长多模态上下文仍是开放问题。

2. **理解-生成统一的表征最优设计**：LLaDA2.0-Uni 采用 discrete diffusion + MoE，Unify-Agent 采用 separate backbone + retrieval，两者架构差异显著。哪种设计在效率、质量、泛化上最优，尚无定论。

3. **VLM 的细粒度 grounding 稳定性**：在高噪声、遮挡、动态布局场景下，VLM 的 grounding 能力仍不够稳定。Continual GUI Agents 提出 anchoring reward，但更鲁棒的 scale-invariant grounding 机制需要进一步研究。

### 5.2 数据与评测挑战

4. **多模态偏好标注的高成本**：Human preference alignment 需要大量高质量偏好数据，但多模态场景下的标注成本远高于纯文本。如何利用 AI-assisted annotation 或 self-generated preference signal 降低成本，是关键问题。

5. **Benchmark saturation 与 data contamination**：MMMU、MME 等基准上模型已接近人类水平，但是否存在 data contamination、benchmark memorization 争议。需要更动态、更不可预测的评测方法。

6. **3D grounding benchmark 的规模局限**：ScanRefer、Nr3D 数据规模有限（~50K），且场景类型偏室内家居。开放世界 3D grounding、跨场景泛化评测仍缺乏。

### 5.3 系统与应用挑战

7. **VLM 作为 agent backbone 的决策可靠性**：当 VLM 用于 GUI agent、embodied agent 时，其 grounding 误差会直接影响动作执行。如何在多步任务中实现稳定的决策链，是走向实际部署的关键。

8. **安全攻击防护的系统化方案**：LaSM 针对 pop-up attack 的 layer-wise scaling 是有效局部方案，但对 instruction injection、adversarial OCR text 等其他攻击类型的系统性防御尚未成熟。

9. **理解-生成统一模型的推理效率**：MoE + diffusion + LLM 的组合导致显存和推理速度挑战。如何在保持统一能力的前提下实现高效推理，需要架构层面的创新。

### 5.4 研究方向建议

- **Resolution-First 原则**：在追求复杂推理能力之前，优先确保高分辨率视觉编码的基础能力。
- **Unified-First 原则**：在设计 VLM 时，优先考虑理解+生成的统一架构，而非分离模块拼接。
- **Alignment-First 原则**：在追求性能提升之前，优先完成 human preference alignment，确保安全性和可控性。
- **Efficiency-First 原则**：在部署场景中，优先考虑 inference-time efficiency optimization（KV cache、layer scaling），而非重新训练。

---

## 参考文献

### 6.1 核心方法论文

**高分辨率视觉编码**：
- [[2312-CogagentVisualLanguageModel]] - CogAgent: 18B VLM, 1120x1120 dual-resolution encoder
- [[2400-MobileflowMultimodalLlmMobile]] - MobileFlow: 21B multimodal LLM for mobile GUI
- [[2400-SeeclickHarnessingGuiGrounding]] - SeeClick: GUI grounding pre-training

**Zero-shot Grounding**：
- [[2400-VlmGrounderVlmAgent]] - VLM-Grounder: Zero-shot 3D visual grounding
- [[2400-TowardsVisualGroundingSurvey]] - Visual Grounding Survey

**理解-生成统一**：
- [[2604-LLaDA2Uni]] - LLaDA2.0-Uni: Unified multimodal understanding + generation
- [[2600-UnifyAgentUnifiedMultimodal]] - Unify-Agent: World-grounded image synthesis
- [[2500-VisionLanguageVisionAuto]] - VLV Auto-Encoder: Knowledge distillation from diffusion

**Human Preference Alignment**：
- [[2500-AligningMultimodalLlmHuman]] - Aligning Multimodal LLM with Human Preference: A Survey

**效率优化**：
- [[2500-GuiKvEfficientGui]] - GUI-KV: KV cache with spatio-temporal awareness
- [[2500-LasmLayerWiseScaling]] - LaSM: Layer-wise scaling for pop-up attack defense

### 6.2 应用与评测论文

**VLM for Object Detection**：
- [[2500-ObjectDetectionMultimodalLarge]] - Object Detection with Multimodal Large Vision-Language Models

**VLM Evaluation**：
- [[2500-EvaluatingOpenSourceVision]] - Evaluating Open-Source VLMs for Multimodal Sarcasm Detection

**VLM for GUI Agent**：
- [[2506-ShowuiOneVisionLanguage]] - ShowUI: Vision-Language-Action model for GUI

---

## 调研日志

### 2026-04-28 初版
- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 15 篇 VLM 相关论文，本次重点分析 12 篇核心论文
- **未能获取**: 外部 WebSearch/WebFetch 工具受限，未能获取 arxiv 新论文
- **核心发现**: 高分辨率视觉编码解决文本密集场景瓶颈；理解-生成统一成为趋势；效率优化可在不重新训练前提下实现显著改进
- **status**: success