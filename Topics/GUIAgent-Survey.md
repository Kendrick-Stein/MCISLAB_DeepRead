---
title: GUI Agent Survey
tags: [survey, gui-agent, vlm, rl, computer-use]
date_updated: "2026-05-04"
year_range: 2023-2026
papers_analyzed: 205
---

# GUI Agent 研究综述

## 1. Overview

GUI Agent 是指能够理解图形用户界面（GUI）、执行人类指令、完成自动化操作任务的智能系统。其核心是让 AI 从"会说"走向"会做"——不仅理解屏幕内容，还能像人类一样进行点击、输入、滑动、导航等交互操作。这一方向处于 Multimodal LLM、Agent、HCI、Computer Vision 与 NLP 的交叉地带，直接关系到 Computer-Use Agent、手机自动化助理、Web Navigation、RPA、无障碍交互、自动化测试等多个真实应用场景。

**核心挑战**：GUI Agent 面临三大关键瓶颈：

1. **Grounding 精度问题**：理解界面元素并将其映射到准确的操作坐标是最基础的挑战。真实界面中存在小图标、密集布局、动态变化、分辨率差异、视觉噪声等多种干扰因素。
2. **长程决策与 Credit Assignment**：多步任务的成功往往只在最后一步得到稀疏反馈，中间正确操作无法被强化，失败操作难以定位追责。
3. **泛化与持续适应**：界面布局、应用版本、平台差异（mobile/desktop/web）持续变化，静态训练的模型难以稳定泛化。

**研究趋势**：从 2023-2026 年，该领域经历了三个重要演进阶段：
- **早期阶段（2023）**：以基于 HTML/DOM/VH 的 text-based agent 为主，依赖结构化界面信息。
- **发展阶段（2024）**：Visual GUI Agent 崛起（SeeClick、Ponder & Press），强调纯视觉输入的 grounding 能力；大规模数据集开始涌现（GUIOdyssey、ScreenSpot）。
- **成熟阶段（2025-2026）**：Self-improving Agent 成为热点（UI-TARS、UI-Genie、UI-Voyager、UI-Mem），强化学习方法广泛应用（MobileRL、UI-R1），跨平台统一代理出现（OmniActor、MMBench-GUI）。

---

## 2. 技术路线

### 2.1 Visual Grounding 路线

**代表论文**：[[2400-SeeclickHarnessingGuiGrounding]]、[[2024-Ponder & Press- Advancing Visual GUI Agent towards General Computer Control]]、[[2500-GuiActorCoordinateFree]]、[[2400-ImprovedGuiGroundingVia]]

**核心思路**：将 GUI grounding 作为独立的基础能力进行专门训练，而非依赖通用 VLM 的隐式定位能力。主要方法包括：

- **Screen-only 输入**：放弃 HTML/DOM/VH，仅用截图作为输入，实现跨平台统一（SeeClick、Ponder & Press）。
- **Grounding Pre-training**：大规模自动构造 grounding 数据（instruction-element 配对），强化模型对界面元素的定位能力。
- **Coordinate-Free 设计**：GUI-Actor 提出 <ACTOR> token + attention-based action head，在 patch 级别直接预测可交互区域，避免文本生成坐标的语义错位问题。
- **Grounding Verifier**：多候选区域生成后进行二次筛选，提升精度的同时保持 single-pass efficiency。

**优势**：跨平台通用性强，不依赖特定环境的结构化接口；训练目标与推理形式一致，减少表示错配。  
**局限**：纯视觉路线丢失了 DOM 中的精准语义信息；小元素、遮挡、动态布局等场景下仍不够稳定。

### 2.2 Self-Improving Agent 路线

**代表论文**：[[2025-UI-TARS- Pioneering Automated GUI Interaction with Native Agents]]、[[2500-UiGenieSelfImproving]]、[[2600-UiVoyagerSelfEvolving]]、[[2600-UiMemSelfEvolving]]

**核心思路**：建立数据-模型闭环，让 agent 通过自主探索、失败经验利用和迭代训练持续提升能力，而非依赖静态人工标注数据。

- **UI-TARS**：Iterative Training with Reflective Online Traces，在数百虚拟机上自动收集轨迹、筛选、反思修正，形成自增强循环。
- **UI-Genie**：提出统一 Reward Model（UI-Genie-RM）作为 verifier，再通过 agent/RM 联合迭代自增强。关键创新是先解决"可验证性"问题，再扩张数据。
- **UI-Voyager**：两阶段框架——Rejection Fine-Tuning (RFT) 筛选高质量轨迹，Group Relative Self-Distillation (GRSD) 从成组 rollout 中定位 fork points，用成功轨迹为失败轨迹构造稠密步级监督。
- **UI-Mem**：Hierarchical Experience Memory，将 workflow、subtask skill、failure pattern 抽象为参数化模板，支持跨任务迁移与 memory-guided exploration。

**优势**：减少对人工标注的依赖；失败经验利用显著提升数据效率；适应动态变化的界面环境。  
**局限**：高度依赖 reward model/verifier 的正确性；自增强过程中可能放大系统性偏差；工程复杂度高。

### 2.3 Reinforcement Learning 路线

**代表论文**：[[2025-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]]、[[2500-UiR1EnhancingEfficient]]、[[2600-ContinualGuiAgents]]

**核心思路**：将 GUI agent 训练从纯 SFT 转向可验证的 RL 优化，利用规则奖励或环境反馈直接优化可执行行为。

- **MobileRL**：提出 Difficulty-Adaptive GRPO (ADAGRPO)，通过 difficulty-adaptive positive replay 和 failure curriculum filtering 适应任务难度分布，并在 AndroidWorld 达到 80.2% 成功率。
- **UI-R1**：基于 rule-based action reward（action type + coordinate + format），仅用 136 条高质量任务进行 GRPO 式强化微调，在 ScreenSpot 上取得 22.1% 提升。强调 efficient reasoning而非冗长 CoT。
- **Continual GUI Agents**：提出 GUI-AiF 框架，通过 Anchoring Point Reward (APR-iF) 与 Anchoring Region Reward (ARR-iF) 在分布漂移中保持稳定 grounding。

**优势**：数据效率高；直接优化执行成功而非模仿文本形式；适合可程序验证的 GUI 动作空间。  
**局限**：RL 训练稳定性依赖采样策略；适用范围偏向结构化、单步可验证的动作类型；对长程多步任务需要额外 reward shaping。

### 2.4 多模态融合与层次规划路线

**代表论文**：[[2025-OmniActor- A Generalist GUI and Embodied Agent for 2D&3D Worlds]]、[[2500-MegaGuiMultiStage]]、[[2500-MobileuseGuiAgentHierarchical]]、[[2400-GuiodysseyComprehensiveDatasetCross]]

**核心思路**：结合视觉、语言、历史上下文多模态信息，建立分层规划架构，从高层任务分解到低层动作执行。

- **OmniActor**：Layer-heterogeneity MoE，分离深层参数以消除 GUI 与 embodied 数据冲突，共享浅层参数利用协同效应，实现跨 2D/3D 环境的统一代理。
- **MEGA-GUI**：Multi-stage modular framework，bidirectional ROI zoom + grounding agent，在 ScreenSpot-Pro 达到 73.18% accuracy。
- **GUIOdyssey**：Cross-app 数据集（8,334 episodes，212 apps），引入 History Resampler 压缩长序列视觉历史，提升跨应用任务性能。
- **InfiGUIAgent**：Two-stage SFT pipeline，Stage 1 强化 grounding，Stage 2 引入 hierarchical reasoning 与 expectation-reflection reasoning。

**优势**：适合复杂长程任务；层次结构可解释性强；支持多应用、多平台迁移。  
**局限**：模块间协调可能引入 cascading errors；历史建模增加推理开销；训练数据需覆盖跨应用流程。

### 2.5 知识驱动与检索增强路线

**代表论文**：[[2500-WebCogreasonerTowardsKnowledge]]、[[2500-RetrievalAugmentedGuiAgents]]、[[2600-SynergyNextGenerationGeneral]]

**核心思路**：引入外部知识框架（如 Bloom’s Taxonomy）或检索机制，为 agent 提供结构化推理指导或历史经验复用。

- **Web-CogReasoner**：Knowledge-driven reasoning，结合认知框架与 chain-of-thought 提升任务泛化。
- **Retrieval-Augmented GUI Agents**：从外部数据库检索相关轨迹或示例，指导当前任务的执行决策。
- **Memory-Augmented Agents**：Graph-structured 或 self-evolving memory，管理长期工作流与动态环境。

**优势**：增强泛化到未见任务的能力；显式知识结构可解释性强。  
**局限**：依赖高质量知识框架与检索库；可扩展性受知识覆盖度限制。

---

## 3. Datasets & Benchmarks

| Dataset/Benchmark | 平台 | 规模 | 评估指标 | SOTA | 特点 |
|:------------------|:-----|:-----|:---------|:-----|:-----|
| **ScreenSpot** | Mobile/Desktop/Web | 多平台 grounding 任务 | Accuracy | SeeClick 显著优于 baseline | 首个系统性 GUI grounding benchmark |
| **ScreenSpot-Pro** | Multi-platform | 更高难度 grounding | Accuracy | GUI-Actor-7B: 44.6 (Qwen2.5-VL) | OOD grounding 测试，分辨率/布局变化 |
| **OSWorld** | Desktop (Linux/Windows/macOS) | 369 个真实任务 | Success Rate | UI-TARS: 24.6 (50 steps) | 通用桌面操作系统控制 benchmark |
| **AndroidWorld** | Android Mobile | 116 个真实任务 | Success Rate | MobileRL-9B: 80.2% / UI-Voyager: 81.0% | 移动端长程任务 benchmark |
| **AndroidLab** | Android Mobile | 138 个任务 | Success Rate | MobileRL-9B: 53.6% | 移动端在线交互评测 |
| **GUIOdyssey** | Android Mobile | 8,334 episodes, 212 apps, 1,357 app组合 | Success Rate | OdysseyAgent + History Resampler | Cross-app navigation，语义推理标注 |
| **MMBench-GUI** | Windows/macOS/Linux/iOS/Android/Web | 四层级评测 | EQA (Efficiency-Quality Area) | 多模型评测 | 层级化多平台评估框架 |
| **Mind2Web** | Web | 2,000+ 任务 | Success Rate | SeeClick 提升 | 真实网页导航任务 |
| **MiniWob** | Web | 小型网页交互 | Success Rate | SeeClick 提升 | 经典 web agent benchmark |
| **AITW** | Android | 多任务 | Action Accuracy | SeeClick 提升 | 移动端操作 benchmark |
| **Odysseys** | Web (Live Internet) | 200 个真实长时域任务 | Success Rate / Efficiency | Claude-Opus: 44.5%, Efficiency: 1.15% | 首个 live Internet + long-horizon + rubric-based 评测 |
| **ProBench** | Mobile | 200+ 挑战性任务 | 过程级评估 | 需验证 | 引入过程信息提供者，精确过程评估 |
| **A3 (Android Arena)** | Android | 真实应用任务 | Success Rate | UI-Genie SOTA | 真实 app 交互评测 |
| **GUI-Testing Arena** | Multi-platform | 自动化测试任务 | Test Coverage | 需验证 | GUI 自动化测试专用 benchmark |
| **AutoGUI-v2** | Multi-platform (6 OS) | 2,753 tasks | Region/Element-level Accuracy, Interaction Outcome Prediction | Qwen3-VL (grounding), Gemini-2.5-Pro (captioning) | Deep functionality understanding + state prediction，发现 VLM dichotomy |

**Benchmark 演进趋势**：
- 从静态 grounding（ScreenSpot）到动态交互（AndroidWorld、OSWorld）
- 从单平台到跨平台统一评测（MMBench-GUI）
- 从终点评估到过程级评估（ProBench）
- 从离线测试到在线交互（AndroidLab）
- 从静态 snapshot 到 live Internet 真实环境（Odysseys 44.5% 成功率暴露 frontier models 在真实场景的惨淡表现）
- 效率首次成为 first-class concern（Odysseys Trajectory Efficiency 指标）

---

## 4. Key Takeaways

1. **Grounding 是 GUI Agent 的基础瓶颈**：SeeClick、GUI-Actor 等工作证明，准确定位界面元素是成功执行的前提。将 grounding 作为独立能力训练（而非隐式依赖 VLM）可显著提升下游任务性能。Coordinate-free 设计（patch-level attention）优于文本生成坐标范式。**AutoGUI-v2 发现 VLM dichotomy**：开源模型（Qwen3-VL）在功能性 grounding 上超越商业模型，但商业模型（Gemini-2.5-Pro）在功能性 captioning 上更强——说明 fine-tuning on agent data 对 grounding 有显著价值，但 deep functional understanding（transition logic、uncommon actions）仍是所有模型的短板。

2. **Self-improving 框架正在成为主流范式**：UI-TARS、UI-Genie、UI-Voyager 展示了"数据-模型闭环"的强大潜力。先构建可靠 verifier/reward model，再通过自主探索迭代提升，可显著减少对人工标注的依赖。失败经验利用（GRSD、fork point 定位）是关键创新。

3. **RL 正在重塑 GUI Agent 训练方法**：MobileRL、UI-R1 证明，少量高质量任务 + 规则奖励的 RL 训练可达到或超越大规模 SFT。RL 直接优化执行成功而非模仿文本形式，数据效率更高。Continual GUI Agents 指出 RL 在分布漂移场景下的持续适应优势。

4. **跨平台统一是明确趋势**：OmniActor、MMBench-GUI、UI-TARS 都在探索 mobile/desktop/web 乃至 embodied 环境的统一代理。视觉-only 输入是实现跨平台统一的关键设计。

5. **评测从终点评估走向过程级评估**：ProBench、MMBench-GUI 的 EQA 指标表明，仅看终点状态不足以准确评估 agent 能力。过程信息、效率指标、层级化诊断成为新的评测方向。

6. **信任与安全开始被系统性关注**：Towards Trustworthy GUI Agents 提出感知-推理-交互三层信任框架，指出 Execution Gap 是核心挑战。不可逆操作、多步计划一致性、对抗性攻击防护成为新的研究方向。SnapGuard 针对 screenshot-based web agent 提出 lightweight prompt injection 检测（F1=0.75），但精度仍不足以支撑"安全"claim。

7. **Live Internet 评测揭示真实能力缺口**：Odysseys 在真实开放互联网上评测 200 个长时域任务，最强 frontier model 仅达 44.5% 成功率、1.15% 效率——彻底戳穿 WebArena/WebVoyager 在 static snapshot 上"饱和"的假象。Long-horizon + live environment 是 distinct capability frontier。

8. **VLM Grounding 可视化验证有启发**：SketchVLM 的 coordinate prompting + SVG overlay 设计可迁移到 GUI grounding 验证——"show me where you would click"的可视化 debug 为 grounding 错误诊断提供新思路。>94% annotation-text faithfulness 证明视觉输出和文本输出一致性。

9. **RL 训练瓶颈在系统效率而非算法**：DART-GUI 揭示 GUI agent RL 的被低估 insight——解耦异步架构将环境利用率从 12.2% 提升到 67.7%（5.5×），7B 模型 OSWorld 42.13% 超越 Claude-4-Sonnet。**RL 框架的工程效率可能比算法创新更关键**。

10. **API-GUI 统一是效率突破口**：ComputerRL 的 API-GUI 范式和 UI-TARS-2 的 GUI-SDK 扩展表明，单纯模拟人类 GUI 操作效率低下，让 agent 同时掌握程序化 API 调用可减少 3× 步数。9B 模型在 OSWorld 达 48.9% 超越 o3。

11. **Training-time 与 Test-time scaling 正交互补**：UI-TARS-2/ComputerRL 代表训练时 RL scaling，Agent S3/BJudge 代表推理时 compute scaling（OSWorld 72.6% 超人类）。两者可组合——用 RL 训练的强模型作为 base，再用 test-time scaling 提升可靠性。

12. **数据合成成本急剧下降**：从 CogAgent 时代的人工标注，到 AgentTrek（$0.55/trajectory）、OS-Genesis（逆向任务合成）、TongUI（143K trajectories from tutorials），数据获取成本下降 20×。OpenCUA 的 reflective CoT augmentation 证明 CoT 质量比 trajectory 数量更重要（+32%）。

13. **感知 pipeline 质量是被低估因素**：WindowsAgentArena 发现 SoM annotation 质量造成 15-57% 性能波动，OmniParser 证明 local semantics 提升 23.3%。比起 reasoning 能力，感知质量对最终性能的影响可能更大。

---

## 5. Open Problems

### 5.1 核心技术挑战

1. **长程任务的 Credit Assignment**：多步任务中，稀疏反馈导致中间正确操作无法被强化。UI-Voyager 的 GRSD 提出了 fork point 定位思路，但如何在高噪声、多分支、状态不完全可观测的真实界面中稳定实现，仍是开放问题。

2. **跨域/跨分辨率的稳定 Grounding**：Continual GUI Agents 提出了 APR-iF/ARR-iF，但真实场景中界面变化更复杂（动画、个性化布局、主题切换）。如何设计更鲁棒的 scale-invariant、layout-invariant grounding 机制需要进一步研究。

3. **Self-improving 的系统性偏差风险**：UI-Genie 的 RM、UI-Mem 的 experience template 若存在错误抽象，自增强过程可能放大偏差而非纠错。如何构建"可纠错"而非"可增强"的自进化系统是关键问题。

### 5.2 数据与评测挑战

4. **大规模高质量交互数据的获取成本**：尽管 self-improving 方法减少了人工标注依赖，但初始高质量种子数据、验证器训练数据、跨平台覆盖数据仍需大量人工投入。GUIOdyssey 的语义标注成本、ScreenSpot 的自动构造质量上限都反映了这一矛盾。

5. **真实环境评测的覆盖率不足**：当前 benchmark 多在仿真器或特定应用集合上测试，缺少真实设备、真实账号、真实网络环境下的系统性评测。对抗性场景、隐私泄露、错误恢复等高风险情况几乎未被覆盖。

6. **过程级评估的自动化难题**：ProBench 提出过程信息提供者，但如何在不引入额外人工标注的前提下，准确捕捉复杂任务中每一步的关键状态变化，仍是技术挑战。

### 5.3 系统与应用挑战

7. **推理效率与实时部署**：History Resampler、multi-module framework 都增加了推理开销。Mobile 环境对延迟敏感，如何在保持长程决策质量的同时满足实时响应需求，需要更轻量化的设计。

8. **不可逆操作的风险控制**：删除数据、支付转账、发送消息等不可逆操作一旦出错后果严重。如何设计确认机制、撤销能力、风险检测与阻断机制，是可信 GUI Agent 的关键要求。

9. **隐私与安全攻击防护**：Fine-print injection、indirect prompt injection、恶意界面元素等攻击手段已被识别（EVA、Obvious Invisible Threat），但系统性防御方案尚未成熟。SnapGuard 提出轻量级检测（VSI + APD），但 F1=0.75 漏检率对安全场景 unacceptable——lightweight 但不够 accurate。

10. **Live Internet 评测的可复现性困境**：Odysseys 在真实开放互联网上评测，真实性最高但不可复现——网站更新、内容变化，每次评测结果可能不同。如何在 realism 与 reproducibility 之间取得平衡，是 benchmark design 的 fundamental trade-off。

### 5.4 研究方向建议

- **Grounding-First 原则**：在追求复杂规划能力之前，优先确保基础 grounding 的稳定与精确。
- **Verifier-First 原则**：在数据扩张之前，优先构建可靠的验证器/奖励模型，避免自增强中的偏差放大。
- **Continual-First 原则**：在设计训练框架时，优先考虑分布漂移场景下的持续适应能力，而非静态最优。
- **Trust-First 原则**：在追求性能提升之前，优先分析不可逆操作的风险边界与防护机制。

## 6. 参考文献

### 6.1 核心方法论文

**Visual Grounding**：
- [[2400-SeeclickHarnessingGuiGrounding]] - SeeClick: GUI grounding pre-training
- [[2024-Ponder & Press- Advancing Visual GUI Agent towards General Computer Control]] - Ponder & Press: Interpreter + Locator 框架
- [[2500-GuiActorCoordinateFree]] - GUI-Actor: Coordinate-free grounding

**Self-Improving Agent**：
- [[2025-UI-TARS- Pioneering Automated GUI Interaction with Native Agents]] - UI-TARS: Native agent + iterative training
- [[2500-UiGenieSelfImproving]] - UI-Genie: Reward model + self-improvement
- [[2600-UiVoyagerSelfEvolving]] - UI-Voyager: RFT + GRSD
- [[2600-UiMemSelfEvolving]] - UI-Mem: Hierarchical experience memory

**Reinforcement Learning**：
- [[2025-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]] - MobileRL: ADAGRPO
- [[2500-UiR1EnhancingEfficient]] - UI-R1: Rule-based RL
- [[2600-ContinualGuiAgents]] - Continual GUI Agents: Anchoring reward

**多模态与层次规划**：
- [[2025-OmniActor- A Generalist GUI and Embodied Agent for 2D&3D Worlds]] - OmniActor: GUI + Embodied unified
- [[2500-MegaGuiMultiStage]] - MEGA-GUI: Multi-stage grounding
- [[2400-GuiodysseyComprehensiveDatasetCross]] - GUIOdyssey: Cross-app dataset
- [[2025-InfiGUIAgent- A Multimodal Generalist GUI Agent with Native Reasoning and Reflection]] - InfiGUIAgent: Native reasoning

### 6.2 Survey 与综述

- [[2500-GuiAgentsSurvey]] - GUI Agents: A Survey (ACL Findings 2025)
- [[2500-TowardsTrustworthyGuiAgents]] - Towards Trustworthy GUI Agents

### 6.3 Benchmark 论文

- [[2025-MMBench-GUI- Hierarchical Multi-Platform Evaluation Framework for GUI Agents]] - MMBench-GUI
- [[2500-ProbenchBenchmarkingGuiAgents]] - ProBench: Process-level evaluation
- [[2604-Odysseys]] - Odysseys: Live Internet long-horizon benchmark（Rating 3 🔥）

### 6.4 安全与防护

- [[2604-SnapGuard]] - SnapGuard: Lightweight prompt injection detection for screenshot-based web agents

### 6.5 Grounding 可视化验证

- [[2604-SketchVLM]] - SketchVLM: VLM visual annotation for grounding verification

### 6.6 RL Training Infrastructure

- [[2509-DARTGUI]] - DART-GUI: 解耦异步 RL，5.5× 环境利用率
- [[2508-ComputerRL]] - ComputerRL: API-GUI 统一 + Entropulse，9B 超 o3
- [[2509-UITARS2]] - UI-TARS-2: Data flywheel + PPO 变体

### 6.7 Data Synthesis

- [[2412-AgentTrek]] - AgentTrek: Tutorial→trajectory，$0.55/trajectory
- [[2412-OSGenesis]] - OS-Genesis: 逆向任务合成
- [[2504-TongUI]] - TongUI: 多模态教程→143K trajectories

### 6.8 Foundation Models

- [[2410-OSAtlas]] - OS-Atlas: 13.58M grounding corpus，7B 超 GPT-4o
- [[2411-ShowUI]] - ShowUI: UI-guided token selection，2B 接近 7B
- [[2511-GroundCUA]] - GroundCUA: Dense annotation，3B 超 72B agentic
- [[2508-OpenCUA]] - OpenCUA: 开源 pipeline + Reflective CoT
- [[2510-ScalingAgents]] - Agent S3: BJudge + wide scaling，OSWorld 72.6% 超人类

---

## 调研日志

### 2026-04-28 更新
- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 190+ 篇，本次重点分析 25 篇核心论文
- **核心发现**: Self-improving Agent 成为主流范式；RL 路线展示高数据效率；Grounding 被确认为基础瓶颈
- **status**: success

### 2026-04-29 增量更新
- **调研日期**: 2026-04-29
- **新增论文**: 3 篇（Odysseys/SnapGuard/SketchVLM）
- **核心发现**: 
  - Odysseys (Rating 3) 揭示 frontier models 在 live Internet + long-horizon 真实场景仅达 44.5% 成功率，彻底戳穿 static benchmark "饱和"假象
  - SnapGuard 提出 lightweight prompt injection 检测但 F1=0.75 精度不足
  - SketchVLM 的 coordinate prompting + SVG overlay 可迁移到 GUI grounding 验证
- **新增 Benchmark**: Odysseys（首个 live Internet 评测）
- **新增 Open Problems**: Live Internet 评测可复现性困境
- **status**: success

### 2026-04-30 MindFlow 合并
- **调研日期**: 2026-04-30
- **来源**: MindFlow ComputerUseAgents-Survey（23 篇论文）合并
- **新增 Takeaways**: 5 条（RL 系统效率瓶颈 / API-GUI 统一 / Training-time vs Test-time scaling / 数据合成成本下降 / 感知 pipeline 质量）
- **新增 References**: 12 篇（DART-GUI, ComputerRL, UI-TARS-2, AgentTrek, OS-Genesis, TongUI, OS-Atlas, ShowUI, GroundCUA, OpenCUA, Agent S3, ClawGUI）
- **status**: success

### 2026-04-21 初版
- **调研日期**: 2026-04-21
- **论文统计**: vault 已有 190 篇
- **分析论文**: 30 篇核心论文
