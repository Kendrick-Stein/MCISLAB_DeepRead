---
title: "MiMo-Embodied: X-Embodied Foundation Model Technical Report"
authors: [Xiaomi Embodied Intelligence Team]
institutes: [Xiaomi]
date_publish: 2025-11-20
venue: arXiv 2511.16518
tags: [VLM, embodied-reasoning, spatial-reasoning]
paper: https://arxiv.org/abs/2511.16518
website:
github: https://github.com/XiaomiMiMo/MiMo-Embodied
rating: 2
date_added: 2026-04-21
---

## Summary

> [!summary] MiMo-Embodied: X-Embodied Foundation Model Technical Report
> - **核心**: 一个 7B VLM 同时覆盖 Embodied AI（室内机器人）与 Autonomous Driving（户外车）两个传统上各自训练的 domain，通过四阶段渐进训练（Embodied SFT → +Driving SFT → CoT SFT → GRPO RL）得到在 17+12 个 benchmark 上的综合 SOTA
> - **方法**: 基于 MiMo-VL-7B-SFT-2508 初始化（ViT + MLP projector + LLM）；四阶段 SFT/RL 全参数训练，bs=512 / lr=2e-6（SFT）+ bs=32 / lr=1e-6（RL）；GRPO reward = 多选 exact match + grounding IoU + format check
> - **结果**: 17 embodied + 12 driving benchmark 综合领先 GPT-4o / Gemini2.5-Pro / Qwen2.5-VL / InternVL3.5 / [[2502-RoboBrain|RoboBrain]]-2.0 / VeBrain / RoboTron-Drive / DriveLMM-o1；Table 7 消融显示多阶段训练比简单联合训练在两域都有 +4~8 pts 提升；NAVSIM 规划 PDMS 87.4 (IL) / 91.0 (RL) 超过 ReCogDrive-Large
> - **Sources**: [paper](https://arxiv.org/abs/2511.16518) | [github](https://github.com/XiaomiMiMo/MiMo-Embodied)
> - **Rating**: 2 - Frontier（方法层无新意，但 Table 7 消融呈现了有意义的非对称跨域迁移证据——embodied SFT 强化 AD 比反向更有效，联合训练会伤 AD；NAVSIM + 自有数据上是真规划 deployment 而非纯 VQA）

**Key Takeaways:**
1. **"Cross-embodied" = cross-domain, 不是 cross-morphology**：这里的 "embodiment" 指 indoor robot vs. outdoor self-driving 两类场景，不是不同机器人形态。与 [[2503-GR00TN1|GR00T N1]]、[[2406-OpenVLA|OpenVLA]] 等 cross-embodiment VLA 的"跨形态"含义不同，是命名层的术语重叠
2. **非对称跨域迁移是真发现**：Table 7 表明 embodied-only 训练让 AD 从 32.2 → 57.6（+25 pts），但 AD-only 训练反而让 embodied 从 46.76 → 43.2（-3.5 pts）。空间理解能力从室内迁移到室外远比反向有效
3. **简单联合训练会失衡**：Embodied+AD 单阶段联合训练在 AD 上（55.2）反而低于 AD-only（57.5）——存在 task interference。多阶段课程（先 embodied，后 AD，再 CoT，再 RL）是弥合手段，最终达到 62.4 / 63.3
4. **NAVSIM 规划是真 deployment**：Table 6 把 MiMo-Embodied 接 diffusion regression（复用 ReCogDrive 的 IL+DiffGRPO stack），在 4-秒未来轨迹上 PDMS 达 91.0，超过 8B ReCogDrive-Large，用更少 token（796 vs 2304）
5. **架构零创新**：ViT、projector、LLM 全部继承 MiMo-VL-7B-SFT-2508；本工作本质是数据 curation + 多阶段训练 recipe。数据层同样无新数据集，除一批"self-curated 3D grounding data"未开源

**Teaser. 雷达图：MiMo-Embodied 在两组 benchmark 的 envelope 同时覆盖 closed-source（GPT-4o、Gemini）、open-source general（Qwen2.5-VL、InternVL3）与 specialized models。**

![](https://arxiv.org/html/2511.16518v1/x1.png)

---

## 1. Motivation

现有的 embodied VLM 各自专精于一个 narrow 场景：
- **Indoor robotics**：[[2502-RoboBrain|RoboBrain]] / VeBrain 等，强调 task planning + spatial understanding
- **Autonomous driving**：RoboTron-Drive / DriveLMM-o1 等，强调 environmental perception + status prediction + driving planning

作者认为 indoor vs. outdoor 的割裂导致：
1. **Lack of unified embodied VLMs**：空间推理能力无法跨域泛化
2. **Absence of comprehensive cross-embodiment evaluation**：缺少统一的评测把两个 domain 放一起看

**Figure 2. 能力概览**：MiMo-Embodied 同时覆盖 Autonomous Driving 的 Environmental Perception / Status Prediction / Driving Planning，以及 Embodied AI 的 Affordance / Task Planning / Spatial Understanding。

![](https://arxiv.org/html/2511.16518v1/x2.png)

> ❓ "Cross-embodiment" 用词和真正意义上的 cross robot embodiment（同一 policy 跨不同 robot form factor，如 [[2503-GR00TN1|GR00T N1]]、[[2406-OpenVLA|OpenVLA]]）容易混淆。本工作实际是 cross-**domain**（indoor↔outdoor），属于 dataset mix / curriculum 问题，与 morphology generalization 是不同的轴。文献内术语 inflation 值得警惕。

---

## 2. Architecture

**Figure 3. 三件套架构**：(1) ViT 编码视觉输入（支持 single image / multi image / video）；(2) MLP projector 把视觉 token 映射到 LLM 的 latent space；(3) LLM 做文本理解与推理。ViT、projector、LLM 全部从 MiMo-VL-7B-SFT-2508 初始化。

![](https://arxiv.org/html/2511.16518v1/x3.png)

> 架构本身无任何创新——本工作所有差异化都在数据与训练 recipe 上。注意 base 是 MiMo-VL 的 2508 SFT checkpoint，而非原 MiMo-VL 技术报告里的 2505 checkpoint。

---

## 3. Training Dataset

**Figure 4. 三大类训练数据**：General Dataset（奠基多模态能力）、Embodied AI Dataset（affordance / planning / spatial）、Autonomous Driving Dataset（perception / prediction / planning）。

![](https://arxiv.org/html/2511.16518v1/x4.png)

### 3.1 General Dataset

继承 MiMo-VL 训练语料，含 visual grounding、document/chart 理解、video understanding、multimodal reasoning 四类。

### 3.2 Embodied AI Dataset

| 能力 | 数据源 |
|---|---|
| Affordance Prediction | PixMo-Points, RoboAfford, RoboRefIt |
| High-level Task Planning | [[2503-CosmosReason1\|Cosmos-Reason1]], EgoPlan-IT, RoboVQA |
| Spatial Understanding | SQA3D + 自构建 3D 数据, VLM-3R, RefSpatial, EmbSpatial-SFT |

值得注意的几点：
- **3D grounding 自构建**：基于现有数据集批量生成 "RGB image + spatial query → camera coordinate 3D box" 样本，用于 monocular 3D 理解。这批数据未开源
- **CoT 推理链来自 DeepSeek-R1**：Cosmos-Reason1 的 long-chain reasoning trace 是 R1 生成——本质是 R1 在 embodied domain 的蒸馏
- **RoboRefIt 强调 referential ambiguity**：187 个 cluttered indoor 场景，多实例同类别需靠 attribute / spatial relation 区分

### 3.3 Autonomous Driving Dataset

| 能力 | 主要数据源 |
|---|---|
| Environmental Perception - General Scene | CODA-LM, DriveLM, nuScenes-QA, MAPLM, MME-RealWorld, IDKB, LingoQA scenery |
| Environmental Perception - Regional Object | CODA-LM, DriveLM, DriveAction, MME-RealWorld, nuScenes-QA, IDKB |
| Environmental Perception - Object Localization | DRAMA-style critical-object 2D 定位 |
| Status Prediction (Intent) | DriveLM, MME-RealWorld |
| Driving Planning - Action Decision | DriveLM, MME-RealWorld, IDKB |
| Driving Planning - Driving Reasoning | CODA-LM, NuInstruct, LingoQA, BDD-X, DriveLM, IDKB |

> ❓ 数据章节完全是清单式陈述——每个数据集的样本数、配比、采样策略均未披露。对强调 "data construction" 的 technical report 是显著缺失。

---

## 4. Training Strategy

四阶段渐进式训练，每阶段在前一阶段权重上继续，数据累积（"Previous + ..."），配比未公开。

**Table 1. 四阶段训练配置。**

| Stage | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Dataset | General + Embodied | Previous + Driving | Previous + CoT | RL Data |
| Batch Size | 512 | 512 | 512 | 32 |
| Learning Rate | 2e-6 | 2e-6 | 2e-6 | 1e-6 |
| Optimizer | AdamW | AdamW | AdamW | AdamW |
| Weight Decay | 0.05 | 0.05 | 0.05 | 0.0 |
| LR Schedule | Cosine | Cosine | Cosine | Cosine |
| Max Seq Len | 32768 | 32768 | 32768 | 32768 |
| Trainable | All | All | All | All |

- **Stage 1 (Embodied SFT)**：建立 affordance / planning / spatial 基本能力，同时混入 general 语料维持多模态底座
- **Stage 2 (Driving SFT)**：在 Stage 1 权重上加入驾驶数据，重点是多视角空间推理、temporal consistency、safety-critical 感知
- **Stage 3 (CoT SFT)**：在前面数据子集上加 explicit reasoning chain，教会"先分析再决策"的输出格式
- **Stage 4 (RL with GRPO)**：基于 DeepSeek-R1-style GRPO，reward 设计：
  - Multi-choice：exact answer matching
  - Spatial grounding / pointing：IoU（box）或 point-in-mask
  - 所有任务：format compliance（template check）

> Stage 顺序是 Embodied 先、Driving 后——这个顺序后面 Table 7 的消融证明是有讲究的：反向顺序或联合训练会 degrade AD。

---

## 5. Evaluation

### 5.1 Embodied AI Benchmarks (17)

| 类别 | Benchmarks |
|---|---|
| Affordance | RoboRefIt, Where2Place, VABench-Point, Part-Afford, RoboAfford-Eval |
| Planning | EgoPlan2, RoboVQA, Cosmos-Reason1 |
| Spatial Understanding | CV-Bench, ERQA, EmbSpatial, SAT, RoboSpatial, RefSpatial, CRPE, MetaVQA, VSI-Bench |

**Table 2（节选）. Affordance + Planning。**

| Model | Params | RoboRefIt | Where2Place | VABench-Point | Part-Afford | RoboAfford-Eval | EgoPlan2 | RoboVQA | Cosmos |
|---|---|---|---|---|---|---|---|---|---|
| MiMo-VL | 7B | 68.92 | 29.60 | 35.13 | 15.98 | 43.88 | 34.14 | 35.27 | 50.91 |
| Qwen2.5-VL | 7B | 80.42 | 42.00 | 24.50 | 42.65 | 16.10 | 39.67 | 57.17 | 53.70 |
| GPT-4o | – | 14.15 | 20.41 | 13.67 | 13.25 | 20.50 | 41.79 | 34.50 | 53.30 |
| Gemini2.5-Pro | – | 38.44 | 42.38 | 27.92 | 25.53 | 23.40 | 42.85 | 33.90 | 48.64 |
| Qwen-VL-Max | – | 70.31 | 18.92 | 41.50 | 65.35 | 37.92 | 44.68 | 54.37 | 66.36 |
| RoboBrain-2.0 | 7B | 70.40 | 63.59 | 26.67 | 31.20 | 51.46 | 33.23 | 46.32 | 33.82 |
| **MiMo-Embodied** | **7B** | **82.30** | **63.60** | **46.93** | **65.50** | **69.81** | **43.00** | **61.99** | 56.80 |

在 Affordance 5 个 benchmark 上全部 SOTA；Planning 上 RoboVQA SOTA、EgoPlan2 接近 SOTA、Cosmos 输给 Qwen-VL-Max（66.36 vs 56.80）。

**Table 3（节选）. Spatial Understanding。**

| Model | CV-Bench | ERQA | EmbSpatial | SAT | RoboSpatial | RefSpatial | CRPE | MetaVQA | VSI-Bench |
|---|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL 7B | 75.40 | 38.80 | 70.25 | 52.00 | 49.33 | 38.00 | 76.40 | 58.63 | 35.90 |
| Gemini2.5-Pro | 84.59 | **51.02** | **78.74** | **79.33** | 59.87 | 38.16 | 72.17 | **69.47** | 47.81 |
| RoboBrain-2.0 7B | 85.75 | 30.31 | 76.32 | 75.33 | 54.23 | 32.50 | 71.58 | 61.11 | 36.10 |
| **MiMo-Embodied 7B** | **88.82** | 46.75 | 76.24 | 78.67 | **61.76** | **48.00** | **77.15** | 67.33 | **48.49** |

在 9 项里 5 项 SOTA（CV-Bench / RoboSpatial / RefSpatial / CRPE / VSI-Bench），另外几项接近 Gemini2.5-Pro。注意 VSI-Bench（长视频空间推理）上 48.49 已超过 Gemini2.5-Pro 的 47.81——是本工作比较突出的一个结果。

### 5.2 Autonomous Driving Benchmarks (12)

**Table 4. 4 single-view image + 2 multi-view video benchmark（节选）。**

| Model | CODA-LM | DRAMA | MME-RW | IDKB | OmniDrive | NuInstruct |
|---|---|---|---|---|---|---|
| Qwen2.5-VL 7B | 35.75 | 54.32 | 58.60 | 13.44 | 10.07 | 0.43 |
| Qwen2.5-VL 72B | 35.80 | 0.00 | 50.78 | 18.41 | 7.32 | 5.67 |
| GPT-4o | 34.18 | 0.00 | 58.00 | 20.65 | 19.22 | 7.08 |
| Gemini2.5-Pro | 53.21 | 0.24 | **67.00** | **23.21** | 10.87 | 53.20 |
| Specialist | 45.46 | 68.40 | – | – | 40.97 | 35.20 |
| RoboTron-Drive 8B | 58.10 | 0.00 | 41.30 | 8.32 | **48.76** | 83.00 |
| **MiMo-Embodied 7B** | **58.55** | **76.14** | 60.25 | **43.42** | 45.21 | **83.58** |

**Table 5. 3 multi-view image + 3 single-view video benchmark（节选）。**

| Model | DriveLM | MAPLM | nuScenes-QA | LingoQA | BDD-X | DriveAction |
|---|---|---|---|---|---|---|
| Qwen2.5-VL 7B | 25.39 | 24.76 | 25.78 | 55.60 | 11.45 | 73.40 |
| Gemini2.5-Pro | 39.92 | 26.12 | 16.12 | 64.10 | 4.80 | 73.53 |
| Specialist | **57.00** | – | 53.40 | 60.80 | 48.61 | – |
| RoboTron-Drive 8B | **61.30** | 74.34 | 21.15 | 69.20 | 12.80 | 58.87 |
| **MiMo-Embodied 7B** | 57.85 | **74.52** | **56.71** | **69.90** | **52.18** | **80.99** |

Driving 上 12 个 benchmark 里大部分 SOTA；落后项主要是：
- **DriveLM** 57.85 < RoboTron-Drive 61.30 / Specialist 57.00 — 多视角综合 benchmark 上略输 specialist
- **MME-RealWorld** 60.25 < Gemini2.5-Pro 67.00 — 真实世界 QA 仍被 Gemini 压制
- **OmniDrive** 45.21 < RoboTron-Drive 48.76

> "SOTA on 12 benchmarks" 的说法要打折——是 average win / 大多数 benchmark win，不是每项都赢。

### 5.3 Qualitative Real-world Tasks

#### Embodied Navigation
基于 NavA³ 的 long-horizon 导航任务：给高层指令（"I want to sleep"），模型在 top-down map 上标区域、在 egocentric 视图里标目标对象。对比 GPT-4o / Qwen2.5-VL / RoboBrain-2.0，MiMo-Embodied 的 center localization 更精确，能正确处理 "plants"（复数）这类 compositional query。

**Figure 5. 四个室内导航场景（卧室找床、餐厅找吸尘器、书房找植物、浴室找马桶）上 MiMo-Embodied 的 keypoint 预测结果。**

![](https://arxiv.org/html/2511.16518v1/x5.png)

#### Embodied Manipulation
分层 pick-and-place 任务：affordance（锅盖 vs. 勺柄）、ordinal 计数（"第一排左数第三个橙子"）、关系定位（"放在底排橙子之间"）、高度比较（多盘子中选择）。

> 注意：这里都是 keypoint / interaction point visualization，**没有接到控制器执行成功率**——"embodied" claim 停留在 perception+reasoning 层。真机/仿真 manipulation success rate 缺席。

#### Trajectory Planning (NAVSIM)

把 MiMo-Embodied 作为 scene encoder，接 ReCogDrive-style denoising policy 做 4 秒未来轨迹预测：

**Table 6. NAVSIM 规划评测。**

| Model | Params | Token | NC↑ | DAC↑ | TTC↑ | Conf↑ | EP↑ | PDMS↑ |
|---|---|---|---|---|---|---|---|---|
| InternVL3 | 8B | 4096 | 97.4 | 93.7 | 93.2 | 100 | 81.2 | 86.0 |
| MiMo-Embodied | 7B | 796 | 97.9 | 94.3 | 93.8 | 100 | 81.7 | 86.5 |
| ReCogDrive-Large-IL | 8B | 2304 | 98.1 | 94.5 | 94.2 | 100 | 80.9 | 86.5 |
| MiMo-Embodied-IL | 7B | 796 | 98.2 | 94.7 | 94.1 | 100 | 82.0 | **87.4** |
| ReCogDrive-Large-RL | 8B | 2304 | 97.9 | 97.3 | 94.9 | 100 | 86.9 | 90.4 |
| **MiMo-Embodied+RL** | **7B** | **796** | **98.3** | **98.1** | **95.5** | 100 | 86.3 | **91.0** |

Token 数从 2304/4096 压到 796（作者归因 3D conv 替代 patch），PDMS 反而更高。是这篇论文除 benchmark 外最实质的 deployment 结果。

#### Trajectory Planning (Proprietary)
自有大规模驾驶数据上，MiMo-Embodied 对比 Qwen2.5-VL 7B baseline，在 turns / nudges / lane changes 等 interactive 场景 L2 误差显著降低（Figure 10，未给绝对数）。

### 5.4 Ablation Study — 这是本文最重要的一节

**Table 7. 训练策略消融。Embodied Avg 跨 affordance+spatial+plan 三项；AD 是驾驶 12 benchmark 平均。**

| Model | Embodied | AD | Multi-Stage | Affordance↑ | Spatial↑ | Plan↑ | Embodied Avg↑ | AD Avg↑ |
|---|---|---|---|---|---|---|---|---|
| MiMo-VL (Baseline) | ✗ | ✗ | ✗ | 38.7 | 55.3 | 46.2 | 46.76 | 32.2 |
| MiMo-VL w/ Embodied | ✓ | ✗ | ✗ | 58.9 | 61.0 | 51.0 | 56.9 | **57.6** |
| MiMo-VL w/ AD | ✗ | ✓ | ✗ | 26.3 | 56.3 | 47.0 | 43.2 | 57.5 |
| MiMo-VL w/ Embodied + AD | ✓ | ✓ | ✗ | 59.6 | 62.0 | 53.8 | 58.4 | 55.2 |
| **MiMo-Embodied (Ours)** | ✓ | ✓ | ✓ | **65.6** | **66.0** | **55.6** | **62.4** | **63.3** |

**这张表的三个关键发现**，也是本论文最有信息量的 signal：

1. **跨域迁移是非对称的**：
   - Embodied-only（第 2 行）：AD 从 32.2 → 57.6（**+25.4 pts**），在 AD 评测上甚至逼近 AD-only 训练
   - AD-only（第 3 行）：Embodied 从 46.76 → 43.2（**-3.5 pts**），反而倒退
   - 解读：室内空间推理（3D grounding、affordance、referential spatial reasoning）对室外驾驶 benchmark 有 strong positive transfer；而驾驶数据对室内任务不但没帮助，可能还会挤占 capacity
2. **简单联合训练会伤 AD**：Embodied+AD 单阶段（第 4 行）AD Avg 55.2 **低于** AD-only（57.5）和 Embodied-only（57.6）。混合训练在 AD 上有 task interference
3. **多阶段课程是弥合手段**：先 Embodied 再 Driving 再 CoT 再 RL，在 embodied（62.4 vs 58.4，+4.0）和 AD（63.3 vs 55.2，+8.1）上同时超过联合训练。curriculum 让两个域都能进一步提升

> ❓ **这个 ablation 没做的几件事**：(1) 阶段拆分——CoT-SFT 和 RL 各自贡献多少；(2) 反向课程——AD 先、Embodied 后会如何（会验证顺序是否真的关键）；(3) replay ratio——多阶段训练是全部累积数据、还是纯增量；(4) 逐 benchmark 的 breakdown（只给了三大类平均）。

> ❓ **为什么 embodied→AD transfer 这么强？** 文章没解释。可能原因：(a) embodied 数据里的 3D grounding / monocular depth / 空间关系推理，与驾驶场景的几何理解高度共享；(b) driving benchmark 本身更偏语义+常识（OCR、交通规则、意图判断），VLM base 就擅长，embodied 训练不会破坏这些能力；(c) driving 数据多为 QA 文本任务，反而没给 VLM 多少新的空间信息——所以 AD-only 训练提升也有限（57.5 ≈ embodied-only 57.6）。这是 follow-up 分析的好切入点。

---

## 关联工作

### 基于
- **MiMo-VL-7B-SFT-2508** (arXiv 2506.03569 的后续 checkpoint): ViT+projector+LLM 三件套权重完整继承；本工作可视为其 embodied+driving domain SFT/RL 续训
- [[2503-CosmosReason1|Cosmos-Reason1]]: 提供 task planning 训练数据（含 R1 生成 reasoning trace）
- **DeepSeek-R1**: GRPO 算法源头；CoT 数据蒸馏 teacher
- **ReCogDrive** (arXiv 2506.xxxxx): NAVSIM 部署阶段的 denoising policy + DiffGRPO 直接复用

### 对比
- **Embodied VLM 线**：[[2502-RoboBrain|RoboBrain]] / [[2507-RoboBrain2|RoboBrain-2.0]] / [[2601-RoboBrain25|RoboBrain-2.5]] / VeBrain / Magma / [[2503-CosmosReason1|Cosmos-Reason1]]
- **Driving VLM 线**：RoboTron-Drive / DriveLMM-o1 / Specialist 模型们（DRAMA、nuScenes-QA 任务专家）
- **通用 VLM**：GPT-4o / Claude-Sonnet-4 / Gemini2.5-Pro / Qwen-VL-Max / Qwen2.5-VL 7B&72B / InternVL3.5 8B&38B
- **Closed-source robotics**：[[2503-GeminiRobotics|Gemini Robotics]] / [[2510-GeminiRobotics15|Gemini Robotics 1.5]]（未在 benchmark 表中出现，但是定义方向的 reference point）

### 方法相关
- **GRPO + rule-based reward** (IoU / exact match / format check): 与 [[2506-VLNR1|VLN-R1]]、[[2604-OpenSpatial|OpenSpatial]] 等 spatial RL 工作的 reward 设计思路一致
- **多阶段 SFT → CoT → RL pipeline**: 与 [[2506-VLNR1|VLN-R1]] 及近期 reasoning VLM 的 standard recipe 同构；本文独到之处是把 Embodied / Driving 两个域的 SFT 分成两个 stage 而非一次混入
- **NAVSIM diffusion planner with DiffGRPO**: 与 ReCogDrive 复用，只换 VLM encoder

---

## 论文点评

### Strengths

1. **完整的 evaluation suite 开源**：基于 lmms-eval 的 mivllm wrapper + 29 个 benchmark 配置文件全部开源，是"reproducible eval"的实质贡献；覆盖面在同类开源工作里是最广的
2. **Ablation 提供了一个非平凡的实证发现**：Table 7 呈现出清晰的非对称跨域迁移——embodied→AD 强（+25 pts），AD→embodied 弱甚至负（-3.5 pts）。这本身就值得作为 follow-up 的起点
3. **多阶段训练真的比联合训练好**：Table 7 显示 multi-stage 在两个域各自都超过 single-stage 联合训练（+4.0 / +8.1 pts），不是噱头。课程顺序（先广义空间理解，后驾驶）是可复用的 recipe
4. **NAVSIM 不是纯 VQA**：接 diffusion regression + DiffGRPO 后 PDMS 达 91.0（超过 ReCogDrive-Large 90.4），且用更少 token（796 vs 2304）。证明 embodied SFT 学到的表征对下游 action regression 也有用
5. **Recipe 透明度尚可**：四阶段超参表完整披露（bs / lr / wd / schedule），RL stage 的 bs=32、lr=1e-6 都说清楚

### Weaknesses

1. **"Cross-embodied" 命名误导**：文献里 cross-embodiment 通常指跨机器人形态（[[2503-GR00TN1|GR00T N1]]、[[2406-OpenVLA|OpenVLA]]），这里实际是 cross-domain (indoor↔outdoor)。这是 terminology inflation
2. **数据细节极不透明**：每个 sub-dataset 的样本数、四阶段的 mixing ratio、replay ratio、RL 样本量**全部未披露**。对"data construction is our core contribution"的 report 非常致命——别人无法复现训练，只能做 inference
3. **没有真机 manipulation 部署**：qualitative 部分只有 keypoint / interaction point visualization，**缺 success rate 数字**。相较 [[2503-GeminiRobotics|Gemini Robotics]] / [[2406-OpenVLA|OpenVLA]] 这种真的能 close the loop 到 action 的工作，本文 embodied claim 停留在 perception+reasoning
4. **Ablation 粒度不够细**：只有 base / +Embodied / +AD / +Both / +Multi-Stage 五行，但 multi-stage 内部 CoT-SFT 和 RL 各自贡献多少、反向课程（AD 先 Embodied 后）是否同样有效——都未单独 report
5. **RL stage 对 benchmark 的边际收益未量化**：GRPO 的 reward 设计清楚，但 +RL vs +CoT-SFT 的 delta 没单独拆出
6. **部分 driving benchmark 上仍落后 specialist**：DriveLM 57.85 < 61.30 (RoboTron-Drive)、MME-RealWorld 60.25 < 67.00 (Gemini)、OmniDrive 45.21 < 48.76 (RoboTron-Drive)。"SOTA on 12 AD benchmarks" 的说法要打折

### 可信评估

#### Artifact 可获取性
- **代码**: inference + evaluation only — README 明确写 "does **not** contain model training code"
- **模型权重**: `XiaomiMiMo/MiMo-Embodied-7B` 已在 HuggingFace 发布
- **训练细节**: 仅高层超参（Table 1）；数据配比、样本量、CoT 子集选取策略、RL sample pool 全部未披露
- **数据集**: 绝大部分是已开源 benchmark 组合（PixMo-Points / RoboAfford / Cosmos-Reason1 / DriveLM / nuScenes-QA / ... 共 ~20+ 数据源）；作者"self-curated 3D grounding data"未公开

#### Claim 可验证性
- ✅ **"29 个 benchmark 上的 reported 数字"**：lmms-eval mivllm wrapper + 开源 checkpoint 可独立复现（前提是 benchmark 数据自己获取）
- ✅ **"positive transfer between embodied and driving"**：Table 7 有 leave-one-domain-out ablation 支持；不再是纯 claim
- ✅ **"multi-stage > joint training"**：Table 7 数字明确（62.4/63.3 vs 58.4/55.2）
- ⚠️ **"achieves SOTA on 17 embodied + 12 driving benchmarks"**：是 average win 和 majority win，不是 universal win。DriveLM、MME-RealWorld、OmniDrive、Cosmos 上有可识别的落后项
- ⚠️ **"first cross-embodied foundation model"**：取决于 "cross-embodied" 定义。按论文自己的 indoor↔outdoor 定义可能算 first，但按文献主流的 cross-morphology 定义完全不是
- ⚠️ **NAVSIM PDMS 91.0 vs ReCogDrive-Large 90.4**：token 数显著更少（796 vs 2304）是真优势，但 0.6 PDMS 的差距在单一 benchmark 上需独立复现才能 calibrate
- ❌ **"Sets a new standard for integrating diverse competencies, paving the way for more intelligent and adaptable systems"**：marketing 修辞，非技术 claim

### Notes

- **最大的信号是 Table 7**：非对称跨域迁移是实证发现，值得被 follow。未来要论证 "single-VLM for embodied + driving viable"，这是第一条开源 evidence trail。**推论**：如果要构建 unified embodied foundation model，先广义 indoor spatial data、再 driving，比反向课程或混合训练都更稳
- **对我研究兴趣的相关性**：方法无原创，但作为 multi-domain VLM training 的 empirical data point 有引用价值。具体场景：
  - 写 VLM 跨域 transfer 论文时引用 Table 7
  - 做 VLA / spatial-VLM 数据 curation 时把 "indoor spatial pretrain → domain-specific finetune" 作为对照 recipe
  - 讨论 "VSI-Bench 上 48.49 超 Gemini2.5-Pro" 时可 cite
- **为什么 embodied→AD 迁移这么强，值得深挖**：如果本质是 monocular 3D / spatial reasoning 的共享，那意味着 indoor 3D-rich 训练可以低成本为 driving 场景 bootstrap VLM 能力。这对 data-scarce 场景（新车型、新地理区域）有 practical implication
- **警惕 "cross-embodied" 命名**：未来读到带此字样的论文要先看其定义——indoor↔outdoor / cross-morphology / multi-dataset 三种含义完全不同
- **论文没做 Gemini Robotics 的对比**：closed-source 的 [[2503-GeminiRobotics|Gemini Robotics]] 线才是真正的 cross-morphology baseline，但未出现在表格里——可能是因为没有 public benchmark 对齐的条件

### Rating

**Metrics** (as of 2026-04-24): citation=11, influential=0 (0.0%), velocity=2.16/mo; HF upvotes=26; github 380⭐ / forks=15 / 90d commits=2 / pushed 8d ago

**分数**：2 - Frontier
**理由**：方法层无创新（架构继承 MiMo-VL、训练是 standard SFT→CoT-SFT→GRPO pipeline），但本工作的 Table 7 消融给出了**非平凡的实证发现**（embodied→AD 迁移 +25 pts、反向 -3.5 pts、多阶段课程 +4~8 pts over joint training），加上 NAVSIM 规划上 7B+796 token 达 PDMS 91.0 超过 8B+2304 token 的 ReCogDrive-Large，属于真正的 deployment 而非纯 benchmark 打榜——这些是我做 unified VLM / spatial-VLM 方向时会主动引用的 data point。不够 Foundation 的原因：方法无范式贡献、cross-embodiment 命名存在 inflation、数据细节不透明阻碍复现、真机 manipulation success 缺席。比起 [[2503-GeminiRobotics|Gemini Robotics]] / [[2502-RoboBrain|RoboBrain]] 这种定义方向或奠基 eval 的工作要低一档。2026-04 复核：5.1mo 发布、cite=11/vel=2.16/mo（发布不到半年就达 Frontier 区间的 citation 节奏）、HF=26、仓库 active（8d）；inf=0 反映被引但尚无实质继承，与方法无原创的判断一致——保留 2 合理。
