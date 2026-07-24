---
title: VLM Survey
tags: [survey, VLM, multimodal, vision-language-model, visual-reasoning]
date_updated: "2026-07-22"
year_range: 2023-2026
papers_analyzed: 30
keywords: [vlm, vision language model, multimodal llm, visual reasoning]
domain_map: VLM
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
- **后训练与机制分析期（2026H2）**：统一模型的 RL 后训练兴起（BRAID、SpectraReward）；因果干预式机制分析与受控诊断 benchmark（Visual Access Sweep、SynthDocBench）取代观察性分析；开源基座持续演进（Gemma 4 encoder-free、ScaleCUA 跨平台 CUA 语料）

---

## 技术路线

### 2.1 高分辨率视觉编码路线

**代表论文**：[[2312-CogAgent|CogAgent]]、[[2400-MobileflowMultimodalLlmMobile]]、[[2400-SeeclickHarnessingGuiGrounding]]

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

**代表论文**：[[2604-LLaDA2Uni]]、[[2600-UnifyAgentUnifiedMultimodal]]、[[2606-Orca]]

**核心思路**：将多模态理解和生成统一在单一框架内，避免传统系统中理解模块与生成模块的表征不对齐问题。

**关键设计**：
- **LLaDA2.0-Uni**：Discrete tokenizer + MoE dLLM backbone + diffusion decoder，实现原生统一的多模态理解+生成，支持 interleaved generation + reasoning
- **Unify-Agent**：认知缺口检测 + 多模态证据检索 + grounded recaptioning + 图像生成，将 world-grounded synthesis 重构为 agent 流程
- **VLV Auto-Encoder**：视觉编码器 + T2I diffusion decoder + LLM，通过知识蒸馏实现低成本高质量图像描述
- **Orca**：把 modeling target 从 next-token/next-frame 上移到 world state transition——unconscious（视频相邻帧 latent 预测）+ conscious（event 条件预测 + VQA）联合预训练统一 world latent，冻结 backbone 后经 language/image/action 三种 decoder 读出；4B 在 OOD readout 上超同量级专用 baseline（[[2606-Orca]]），是"统一"从理解-生成扩展到 world modeling 的信号

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

**代表论文**：[[2500-GuiKvEfficientGui]]、[[2500-LasmLayerWiseScaling]]、[[2607-Gemma4]]

**核心思路**：针对 VLM 在长序列高分辨率输入下的计算瓶颈，通过 KV cache 压缩、layer-wise scaling 等技术降低推理开销；基座侧则在训练阶段内建效率设计。

**关键设计**：
- **GUI-KV**：空间显著性引导 + 时间冗余评分，实现 38.9% 解码 FLOPs 降低 + 4.1% 步骤准确率提升
- **LaSM**：Layer-wise scaling mechanism，通过 attention + MLP 联合缩放防御 pop-up attack（defense success rate 74.8%-100%）
- **Gemma 4**：训练侧效率工程的集成样本（[[2607-Gemma4]]）——KV 共享使全局 KV cache −37.5%、int2/int4 QAT 使音频 encoder footprint −78%、MTP speculative decoding；12B 档给出 **encoder-free 统一架构**（35M 投影直接吃 raw image patch / raw audio），若该路线被证明无损，端侧多模态部署栈将大幅简化——但目前只有单一规模点，且缺"统一 vs 外挂 encoder"同规模对照

**优势**：GUI-KV/LaSM 无需重新训练、plug-and-play；Gemma 4 的效率 recipe 可复用于端侧部署
**局限**：缩放系数和关键层范围具有 model-specific 特性；对闭源模型难以应用；Gemma 4 未拆分 thinking mode 与架构本身的贡献占比

### 2.6 统一模型的 RL 后训练与 Reward 设计

**代表论文**：[[2607-BRAID]]、[[2607-SpectraReward]]、[[2607-SearchGenBoundary]]

**核心结论**：统一模型（UMM）的竞争焦点已从架构转向后训练——RL 信用分配如何贯穿异构模态、reward 如何免标注获得，且三篇工作全部收敛到 BAGEL 系 hybrid AR-diffusion 基座。

**关键设计**：
- **BRAID**：两层 MDP 把交错"文-图-文"轨迹统一为单一决策过程，trajectory-level advantage 同时驱动文本 GRPO 与图像 DiffusionNFT，policy gradient 第一次真正贯穿异构模态；BAGEL-7B 上 7 benchmark 平均 +5.73，ablation 显示图像分支 RL 的贡献大于 VLM judge 的 process reward（[[2607-BRAID]]）
- **SpectraReward**：frozen MLLM 对"生成图像条件下原 prompt 的平均 log-likelihood"（一次 teacher-forced forward pass）即为 T2I RL reward，零偏好标注零 reward 训练；Self-SpectraReward 让 BAGEL 用 understanding 分支给 generation 分支打分（GenEval 84.0→89.5），且发现 **reward-policy 分布对齐比 reward model 规模更重要**——自打分追平 30B、超过 235B 外部 reward（[[2607-SpectraReward]]）
- **SearchGen**：生成模型的 knowledge boundary（internalizable vs contextual）是 (prompt, generator) 的联合属性且随训练漂移——盲目接搜索会在模型本会做的 prompt 上倒退；teach-then-search co-training（DPO 内化可学知识 + RFT 校准 8B search reasoner）使 4B generator 达 Gemini-3-Flash oracle reasoner 水平（[[2607-SearchGenBoundary]]）

**共同弱点**：reward/裁判高度依赖闭源强模型（BRAID 用 GPT-5.2 打 process reward、SearchGen 裁判与奖励同源、SpectraReward 零人类评估），增益中 judge preference fitting 的占比未被剥离；likelihood reward 的经典退化解（把 prompt 文字渲染进图像）未被验证；均只在 4B-7B 单 backbone 验证。

### 2.7 VLM as CUA 基座：数据 Scaling、动作表示与外挂验证

**代表论文**：[[2509-ScaleCUA]]、[[2602-ToolTok]]、[[2606-HiViG]]、[[2603-SecAgent]]

**核心结论**：GUI/computer-use 场景对 VLM 的要求已从"看得清"（2.1 的高分辨率路线）推进到数据配比、动作表示、历史压缩与验证机制四个层面，且 grounding 能力与端到端 agent 能力被证明显著解耦。

**关键设计**：
- **ScaleCUA**：6 平台开源 CUA 语料（471K understanding / 17.1M grounding / 19K trajectories）+ Qwen2.5-VL 3B/7B/32B 三推理模式基座；GUI understanding/grounding 开源 SOTA（MMBench-GUI L1-Hard 94.4、ScreenSpot-v2 94.7、ScreenSpot-Pro 59.2），但端到端 OSWorld 仅 17.7%、落后 RL 训练的 agent 近一倍（[[2509-ScaleCUA]]）
- **ToolTok**：把 GUI 操作编码为可学习离散 tool token，coarse-to-fine 多步 pathfinding 替代绝对坐标一步回归；Spherical Semantic Initialization 解决新 token cold start（ScreenSpot 55.2→87.6），4B 模型 ~7K 样本达 ScreenSpot-Pro 61.1，提示 **action space 是决定 data efficiency 与分辨率鲁棒性的建模选择而非输出格式细节**（[[2602-ToolTok]]）
- **HiViG**：8B 多模态 critic 双任务——递归压缩 macro-action history + 在截图上渲染红 "X" 标记核对 policy 的实际坐标；对 frozen policy 平均 +7.3/+9.0（Qwen3-VL-32B / Gemini-3-Flash），而全部五种已有 critic baseline 对强 policy 增益近零或为负（[[2606-HiViG]]）
- **SecAgent**：自然语言 semantic context 递归压缩历史，1 帧历史 + context 接近 5 帧性能（SA 94.8 vs 95.5）而 tokens/TTFT 显著更低；附中文 CMGUI 数据集（121K 已标注 steps / 44 apps）补非英语语料缺口（[[2603-SecAgent]]）

**跨论文 pattern**：

| Pattern | 证据 |
|:--|:--|
| grounding SOTA ≠ 端到端能力 | ScaleCUA OSWorld 17.7 vs COMPUTERRL 47.3；训练分辨率 2K 升 grounding 却降 online agent |
| 像素锚定优于文字中介 | HiViG intent masking ablation 证明 verbal critic 在读文字而非看图；ToolTok/HiViG 均靠截图上渲染显式标记（crosshair / 红 X）把 VLM 拉回视觉状态 |
| GUI 专有能力与通用能力冲突 | ScaleCUA：通用多模态数据比例上升则 GUI benchmark 单调下降，需显式 data-balancing |
| 语义历史压缩缺 factuality 校验 | SecAgent/HiViG 的压缩状态由模型自述生成，silent corruption 会污染后续决策，两篇均未评测 context 本身准确率 |

### 2.8 机制分析：视觉信息"在"但"读不出"

**代表论文**：[[2607-VisualAccessBoundary]]、[[2606-Act2Answer]]、[[2607-GUIStateBelief]]、[[2607-EvoGUI]]

**核心结论**：多篇在不同域用因果干预/行为级协议独立发现同一 pattern——信息在 hidden states 里（线性 probe 可恢复）但模型行为上读不出，VLM 的瓶颈从"表征缺失"转向"读出通路"。GUI 域进一步给出跨模态与时序两个变体：结构文本与像素冲突时模型偏信过期结构（[[2607-GUIStateBelief]]），以及状态转移/时序理解不随模型规模或 GUI 专门化提升（[[2607-EvoGUI]]）。

**关键发现**：
- **Visual Access Boundary**：硬屏蔽 generated token→image token attention 的 2D 扫描（layer × time）显示，CoT 生成长度拉长约 50 倍但所需视觉访问边界与 Direct answering 相差 ≤2 层——CoT 增益来自对已写入 hidden states 的视觉信息做更长语言计算，而非持续"回看"图像；CoT 增益上限受 perceptual readout 制约，难属性存在 probe-vs-decode gap（probe 高精度、decode 显著更差）（[[2607-VisualAccessBoundary]]）
- **Act2Answer**：把知识题改造成"用动作作答"的 VLA 评测协议以剥离低层控制混淆；robotics 微调让语义类知识相比源 VLM 掉 20-40 分，layerwise probing 显示知识在中层仍可解码、到 action head 附近衰减至近随机；VQA co-training 有显著保护作用（Magma retention 86.7% vs π₀ 36.2%）（[[2606-Act2Answer]]）
- **GUIStateBelief（跨模态变体）**：735 组 Web/Mobile/Desktop paired probe——image-only 读取接近饱和时，模型在 pixel↔structure 冲突下仍跟随 stale structure（真实网页结构跟随率最高 0.88），首步注错的 MiniWoB++ episode 自恢复 ≤0.03，training-free consistency gate 才同时降 hijack 与 task error；证据"在"（像素可读）却不被采信，是 readout gap 的 modality-trust 版本（[[2607-GUIStateBelief]]）
- **EvoGUI（时序变体）**：3,000 个 state-transition diagnostic VQA（temporal ordering / inverse action / one-step successor，120 domains），最强模型仅 60.4，且 model scale 与 GUI specialization 均非稳定预测因子——VLM 的状态动态理解是端到端分数掩盖的独立缺口（[[2607-EvoGUI]]）

**含义**：对"拉长推理链提升 multimodal reasoning"和"扩数据防遗忘"两类流行方案都是警示——前者不扩张视觉访问、后者丢的不是知识而是读出。**适用边界**：VAS 的任务限于"一眼看完再算"型，visual search / 多步 grounding 上结论可能翻转；Act2Answer 的二选一格式分辨率有限。

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
| **ScreenSpot** | GUI Grounding | Multi-platform | Accuracy | ScaleCUA-32B 94.7 (v2) | GUI grounding 评测 |
| **ScreenSpot-Pro** | 高分辨率 GUI Grounding | 专业软件截图 | Accuracy | ToolTok-4B 61.1 / ScaleCUA-32B 59.2 | 高分辨率/小目标 grounding |
| **RefCOCO** | 2D Grounding | ~50K expressions | Acc@0.5 | 多模型竞争 | 经典 referring expression |
| **FactIP** | World-grounded Generation | 12 categories | Human preference | Unify-Agent 接近 closed-source | 长尾概念生成评测 |
| **SynthDocBench** | Long-context Doc VQA | 200 docs / 1,788 题 | ACC（LLM judge） | Gemini-3.1-Pro 0.725 | 全合成受控诊断；因子可独立控制 |
| **SearchGen-Bench** | Knowledge-intensive T2I | 751 test / 12 失败类 | 9 分量 judge 评分 | GPT-Image-2 71.2 | 知识密集生成；附冻结 search corpus 可离线复现 |
| **GUIGuard-Bench** | GUI Privacy | 241 轨迹 / 4,080 截图 | detection + plan fidelity | strict full match ≤8.8% | trajectory-conditioned 隐私评测 |
| **CMGUI-Bench** | 中文 Mobile GUI Navigation | 390 episodes / 2,574 steps | Step/Task Acc | SecAgent-3B 96.4/80.0 | 多合法 action 标注，减 false negative |
| **State-Belief Probes** | 跨模态证据冲突诊断 / GUI | 735 paired probes | stale-structure follow rate | 结构跟随率最高 0.88 | pixel/structure 单变量干预 + live episode |
| **EvoGUI** | GUI 状态转移诊断 VQA | 3,000 / 120 domains | ACC | best 60.4 | trajectory-derived offline probe |

**Benchmark 演进趋势**：
- 从自然图像问答（VQAv2）到文本密集场景（TextVQA、DocVQA）
- 从 2D grounding（RefCOCO）到 3D grounding（ScanRefer、Nr3D）
- 从单一模态评测到多学科综合评测（MMMU）
- 从理解任务到理解+生成统一评测（FactIP、SearchGen-Bench）
- 从覆盖式 leaderboard 到受控诊断仪器：[[2607-SynthDocBench]] 独立控制文档长度/页深/layout/模态因子，把失败归因到具体因子（长度衰减、中段位置盲区、长文档 chart 崩溃）
- 从单帧安全评测到 trajectory-conditioned 评测：[[2601-GUIGuardBench]] 把 privacy 定义为任务上下文属性（task necessity），而非静态敏感类别识别

---

## Key Takeaways

1. **高分辨率视觉编码是 VLM 在文本密集场景的关键突破**：CogAgent、MobileFlow 等证明，支持 ≥1120x1120 输入的双分辨率编码器可显著提升 GUI、文档等场景的理解能力。这解决了传统 VLM 固定分辨率（224x224）的瓶颈。

2. **Zero-shot grounding 利用 VLM agent 能力而非专门训练**：VLM-Grounder 展示了通过动态拼接 + feedback loop + multi-view ensemble，无需 3D 训练数据即可实现较强的 3D grounding。这条路线适合数据稀缺场景。

3. **理解-生成统一是 VLM 发展的明确趋势，但架构尚未定型**：LLaDA2.0-Uni、Unify-Agent 等工作将多模态理解和生成放在同一框架，避免了两阶段系统的表征不对齐问题。原版认为 discrete diffusion + MoE 是主流架构选择，但 2026H2 的 RL 后训练工作（[[2607-BRAID]]、[[2607-SpectraReward]]、[[2607-SearchGenBoundary]]）全部收敛到 BAGEL 系 hybrid AR-diffusion 基座，主流架构之争未决；[[2606-Orca]] 进一步把"统一"从理解-生成扩展到 world state transition + 多 decoder 读出。

4. **Human preference alignment 开始向多模态迁移**：将 RLHF/DPO 技术迁移到 VLM，优化真实性、安全性、推理能力，是当前 VLM 走向可靠部署的关键一步。

5. **效率优化技术（KV cache、layer-wise scaling）可在不重新训练的前提下显著降低开销**：GUI-KV、LaSM 等工作证明，通过 inference-time intervention 可实现计算效率提升和安全性增强，部署门槛低。

6. **VLM 正从被动理解器走向主动 agent backbone**：GUI Agent、3D grounding agent、world-grounded synthesis agent 等工作表明，VLM 不只是"看图说话"，而是可以成为多模态 agent 的感知与决策核心。

7. **统一模型的 RL 后训练成为新前沿，reward 转向复用 MLLM 自身能力**：[[2607-BRAID]] 让 policy gradient 第一次贯穿文本 token 与图像去噪路径；[[2607-SpectraReward]] 证明 frozen MLLM 的 prompt likelihood 一次 forward pass 即可做 T2I reward，且 reward-policy 分布对齐比 reward model 规模更重要（自打分超 235B 外部 reward）——该发现对整个 RLHF/RLAIF 都有参考价值。

8. **"Decodable ≠ used"是跨域收敛的机制发现**：[[2607-VisualAccessBoundary]] 的 probe-vs-decode gap 与 [[2606-Act2Answer]] 的"中层可解码、action head 近随机"互为印证——VLM 的瓶颈从表征缺失转向读出通路。CoT 增益来自更长的语言计算而非持续回看图像，上限受 perceptual readout 制约。

9. **GUI grounding 与端到端 agent 能力显著解耦**：[[2509-ScaleCUA]] grounding 开源 SOTA 但 OSWorld 仅 17.7%（落后 RL 系近一倍）；分辨率与数据配比对两种能力的影响方向相反——"grounding 强则 agent 强"的隐含假设不成立，data scaling（SFT）与 RL 是互补而非替代关系。

---

## Open Problems

### 5.1 核心技术挑战

1. **长上下文多模态推理的瓶颈**：当前 VLM（如 CogAgent、LLaVA）在处理长序列图像、多视角输入时面临 context window 限制。虽然 GUI-KV 等尝试压缩 KV cache，但如何在保持理解质量的前提下支持超长多模态上下文仍是开放问题。新证据加剧了该问题的紧迫性：[[2607-SynthDocBench]] 证实 lost-in-the-middle 在视觉长文档上复现（5/8 模型中段掉 5-18 pp），且长文档下 chart 理解以 visual hallucination 方式崩溃；[[2603-SecAgent]] 的自然语言 semantic context 压缩（1 帧历史接近 5 帧性能）是低成本缓解路线，但压缩状态缺 factuality 校验。

2. **理解-生成统一的表征最优设计**：LLaDA2.0-Uni 采用 discrete diffusion + MoE，Unify-Agent 采用 separate backbone + retrieval，两者架构差异显著。哪种设计在效率、质量、泛化上最优，尚无定论。RL 后训练侧 [[2607-BRAID]] 证明 advantage 可贯穿异构模态，但仅在 BAGEL-7B 单 backbone 验证，跨架构泛化未知。

3. **VLM 的细粒度 grounding 稳定性**：在高噪声、遮挡、动态布局场景下，VLM 的 grounding 能力仍不够稳定。Continual GUI Agents 提出 anchoring reward，但更鲁棒的 scale-invariant grounding 机制需要进一步研究。[[2602-ToolTok]] 的离散相对 tool token 是绝对坐标之外的一条候选路线（跨分辨率/宽高比鲁棒性显著提升），但 FAR/MID/CLO 固定 pixel delta 并非完全 scale-invariant，且未经 online 长任务验证。

4. **生成模型的 knowledge boundary 发现**：[[2607-SearchGenBoundary]] 证明"哪些知识内化、哪些外部检索"是 (prompt, generator) 的联合属性且随训练漂移——盲搜有害、边界不可先验预测、必须跑完整 co-training 才能发现。低成本的边界估计方法缺失，该问题与 agent 的"何时调工具"calibration 同构。

### 5.2 数据与评测挑战

5. **多模态偏好标注的高成本**：Human preference alignment 需要大量高质量偏好数据，但多模态场景下的标注成本远高于纯文本。如何利用 AI-assisted annotation 或 self-generated preference signal 降低成本，是关键问题。[[2607-SpectraReward]] 的 prompt-likelihood reward 提供了零标注起点，但只覆盖 alignment、不度量 aesthetics/fidelity。

6. **Benchmark saturation 与 data contamination**：MMMU、MME 等基准上模型已接近人类水平，但是否存在 data contamination、benchmark memorization 争议。需要更动态、更不可预测的评测方法。[[2607-SynthDocBench]] 的全合成受控生成是一条替代路线（ground truth by construction），但其 OCR baseline 对照暴露了新陷阱：complex multi-hop 子集 OCR 0.798 >> vision 0.360——长文档 benchmark 可能测的是文本检索而非视觉推理，OCR/text-only baseline 应成为多模态 benchmark 的标配对照。

7. **3D grounding benchmark 的规模局限**：ScanRefer、Nr3D 数据规模有限（~50K），且场景类型偏室内家居。开放世界 3D grounding、跨场景泛化评测仍缺乏。

8. **MLLM-as-reward / as-judge 的可信度**：2.6 节三篇工作的 reward 或评测均依赖闭源强模型且缺独立人评交叉验证（[[2607-SpectraReward]] 零人类评估、[[2607-SearchGenBoundary]] 裁判与奖励同源）；[[2607-SynthDocBench]] 的 rendering-familiarity confound（D3.js 渲染分布可能偏向特定模型家族）提示合成评测同样有系统性偏差。Reward hacking、judge 亲和偏差的系统性度量方法缺失。

### 5.3 系统与应用挑战

9. **VLM 作为 agent backbone 的决策可靠性**：当 VLM 用于 GUI agent、embodied agent 时，其 grounding 误差会直接影响动作执行。如何在多步任务中实现稳定的决策链，是走向实际部署的关键。[[2606-HiViG]] 给出一个反直觉证据：五种已有 critic（scalar PRM、zero-shot verbal critic、专训 critic）对强 policy 增益近零或为负——"拿通用 VLM 当 judge"在 CUA 上不成立，critic 必须专门训练且训练信号对准像素证据（visual marker + intent masking）。

10. **安全与隐私防护的系统化方案**：LaSM 针对 pop-up attack 的 layer-wise scaling 是有效局部方案，但对 instruction injection、adversarial OCR text 等其他攻击类型的系统性防御尚未成熟。隐私维度上 [[2601-GUIGuardBench]] 揭示层级断裂：binary detection 尚可（Android 89.0% / PC 63.3%）但 strict full match 仅 8.8%/0.6%，需要上下文推断的 Inferences & Profiling 类 recall 仅 2.4%——"知道有隐私"远不等于能最小化披露，selective disclosure policy 的学习尚属空白。

11. **理解-生成统一模型的推理效率**：MoE + diffusion + LLM 的组合导致显存和推理速度挑战。如何在保持统一能力的前提下实现高效推理，需要架构层面的创新。[[2607-Gemma4]] 的 encoder-free 直投路线（raw patch/audio 直接进 LLM embedding 空间）是候选方向之一，但目前只有 12B 单点、缺同规模对照。

12. **下游微调的知识侵蚀**：[[2606-Act2Answer]] 显示 robotics 微调让 VLM 语义类知识掉 20-40 分且下游 SFT 继续恶化；VQA co-training 有保护作用但 Emotion/Attribute 类仍在 chance 水平——如何系统性防止微调侵蚀预训练能力（对 VLA、GUI agent 微调同样适用）未解决。

### 5.4 研究方向建议

- **Resolution-First 原则**：在追求复杂推理能力之前，优先确保高分辨率视觉编码的基础能力。
- **Unified-First 原则**：在设计 VLM 时，优先考虑理解+生成的统一架构，而非分离模块拼接。
- **Alignment-First 原则**：在追求性能提升之前，优先完成 human preference alignment，确保安全性和可控性。
- **Efficiency-First 原则**：在部署场景中，优先考虑 inference-time efficiency optimization（KV cache、layer scaling），而非重新训练。
- **Readout-First 原则**：诊断 VLM 能力失败时，先区分"表征缺失"与"读出失败"（linear probe vs 行为对照），再决定补数据还是修读出通路（[[2607-VisualAccessBoundary]]、[[2606-Act2Answer]]）。

---

## 参考文献

### 6.1 核心方法论文

**高分辨率视觉编码**：
- [[2312-CogAgent|CogAgent]] - CogAgent: 18B VLM, 1120x1120 dual-resolution encoder
- [[2400-MobileflowMultimodalLlmMobile]] - MobileFlow: 21B multimodal LLM for mobile GUI
- [[2400-SeeclickHarnessingGuiGrounding]] - SeeClick: GUI grounding pre-training

**Zero-shot Grounding**：
- [[2400-VlmGrounderVlmAgent]] - VLM-Grounder: Zero-shot 3D visual grounding
- [[2400-TowardsVisualGroundingSurvey]] - Visual Grounding Survey

**理解-生成统一**：
- [[2604-LLaDA2Uni]] - LLaDA2.0-Uni: Unified multimodal understanding + generation
- [[2600-UnifyAgentUnifiedMultimodal]] - Unify-Agent: World-grounded image synthesis
- [[2500-VisionLanguageVisionAuto]] - VLV Auto-Encoder: Knowledge distillation from diffusion
- [[2606-Orca]] - Orca: Next-State-Prediction world foundation model, frozen latent + 多 decoder readout

**统一模型 RL 后训练**：
- [[2607-BRAID]] - BRAID: 两层 MDP 让 RL 贯穿文本 GRPO 与图像 DiffusionNFT
- [[2607-SpectraReward]] - SpectraReward: Frozen MLLM prompt likelihood 作 T2I reward
- [[2607-SearchGenBoundary]] - SearchGen: Knowledge boundary 发现与 teach-then-search co-training

**Human Preference Alignment**：
- [[2500-AligningMultimodalLlmHuman]] - Aligning Multimodal LLM with Human Preference: A Survey

**效率优化与基座**：
- [[2500-GuiKvEfficientGui]] - GUI-KV: KV cache with spatio-temporal awareness
- [[2500-LasmLayerWiseScaling]] - LaSM: Layer-wise scaling for pop-up attack defense
- [[2607-Gemma4]] - Gemma 4: 开源原生多模态基座，encoder-free 12B + 端侧效率 recipe

**机制分析**：
- [[2607-VisualAccessBoundary]] - Visual Access Sweep: CoT 视觉访问边界的因果干预
- [[2606-Act2Answer]] - Act2Answer: VLA 知识保留的行为级评测协议

### 6.2 应用与评测论文

**VLM for Object Detection**：
- [[2500-ObjectDetectionMultimodalLarge]] - Object Detection with Multimodal Large Vision-Language Models

**VLM Evaluation**：
- [[2500-EvaluatingOpenSourceVision]] - Evaluating Open-Source VLMs for Multimodal Sarcasm Detection
- [[2607-SynthDocBench]] - SynthDocBench: 长文档视觉理解的受控诊断 benchmark
- [[2601-GUIGuardBench]] - GUIGuard-Bench: Trajectory-conditioned GUI privacy 评测

**VLM for GUI Agent**：
- [[2506-ShowuiOneVisionLanguage]] - ShowUI: Vision-Language-Action model for GUI
- [[2509-ScaleCUA]] - ScaleCUA: 跨 6 平台开源 CUA 语料与三模式基座
- [[2602-ToolTok]] - ToolTok: 离散 tool token 替代绝对坐标回归
- [[2606-HiViG]] - HiViG: History-aware visually grounded critic
- [[2603-SecAgent]] - SecAgent: Semantic context 历史压缩 + 中文 CMGUI 数据集

---

## 调研日志

### 2026-04-28 初版
- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 15 篇 VLM 相关论文，本次重点分析 12 篇核心论文
- **未能获取**: 外部 WebSearch/WebFetch 工具受限，未能获取 arxiv 新论文
- **核心发现**: 高分辨率视觉编码解决文本密集场景瓶颈；理解-生成统一成为趋势；效率优化可在不重新训练前提下实现显著改进
- **status**: success
## 🆕 Venue 回填增补（2026-06-26，CVF 近 3 年）

> 补收 CVF VLM/Multimodal（29）+ Spatial/3D（22）方向论文,完整清单+综合见 [[Reports/2026-06-26-VenueBackfill]]。

- **空间智能（本批最大主题）**：⭐5 [[2606-ScalingSpatialIntelligence]]（data-centric 8M scaling）、[[2606-SpatialScore]]（49 个 MLLM 评测）、[[2606-SpaceTools]]（多轮调 pointing/depth/3D 工具）、[[2606-FromIndoorTo]]（OpenBench 户外空间推理）。三条解法并行:几何 encoder 注入（[[2606-SpatialStack]]/[[2606-S2MLLM]]/[[2606-G2VLM]]/[[2606-HiSpatial]]）、data scaling、test-time 几何先验（[[2606-Abstract3DPerception]]/[[2606-GeometricallyConstrainedAg]]）。**open question：架构注入 vs data-scaling 缺同 benchmark head-to-head。**
- **长视频理解走 agentic**：[[2606-LensWalk]]/[[2606-VideoARM]]/[[2606-SVAgent]]/[[2606-SymphonyACognitively]]/[[2606-HierarchicalLongVideo]] 普遍用 plan-observe-verify 多轮 + 检索,而非更大 video model。
- **文档/推理 agent**：[[2606-VisualDocumentUnderstandin]]（MACT）、[[2606-CodeDance]]（code as tool）、[[2606-MonoVLM]]（coarse-to-fine GRPO 解 3D grounding reward 稀疏）。

### 2026-07-21 增量更新（survey-refresh）
- 并入 13 篇：[[2607-BRAID]]、[[2607-Gemma4]]、[[2509-ScaleCUA]]、[[2607-VisualAccessBoundary]]、[[2607-SpectraReward]]、[[2607-SynthDocBench]]、[[2607-SearchGenBoundary]]、[[2606-Act2Answer]]、[[2606-HiViG]]、[[2602-ToolTok]]、[[2601-GUIGuardBench]]、[[2603-SecAgent]]、[[2606-Orca]]
- 跳过 1 篇：[[2607-GRPONullWebAgent]]（纯 RL 训练方法学的受控阴性结果，无 VLM 架构/多模态能力层贡献，归 AgenticRL/WebAgent survey）
- 结构变化：新增 2.6（统一模型 RL 后训练）、2.7（VLM as CUA 基座）、2.8（机制分析：decodable ≠ used）三个小节；Key Takeaways +3（7-9）；Open Problems 新增 knowledge boundary、MLLM-as-reward 可信度、知识侵蚀三项；benchmark 表 +5 行；修订 Takeaway 3（BAGEL 系 hybrid AR-diffusion 挑战 discrete diffusion + MoE 的"主流"论断）
- **status**: success

### 2026-07-22 增量更新（survey-refresh）
- 并入 2 篇（均 GUI 域跨域 VLM 能力证据，primary home 为 CUA-Survey）：[[2607-GUIStateBelief]]（§2.8，跨模态证据冲突=readout gap 的 modality-trust 变体）、[[2607-EvoGUI]]（§2.8 + benchmark 表，VLM 状态转移/时序理解缺口）
- 跳过：无
- 结构变化：仅增量并入——§2.8 代表论文 +2、关键发现 +2 bullet；benchmark 表 +2 行；未改 Key Takeaways / Open Problems（两篇强化既有 readout 主题，未推翻结论）
- domain_map: skipped（无格局级变化，仅强化 §2.8 "decodable ≠ used" 主题）
- **status**: success
