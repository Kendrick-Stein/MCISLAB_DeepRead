---
title: Agentic RL Survey
tags: [survey, RL, gui-agent, reinforcement-learning, credit-assignment, reward-model]
date_updated: "2026-04-28"
year_range: 2023-2026
papers_analyzed: 15
---
## Overview

Agentic RL（Agent强化学习）是指将强化学习方法应用于智能体训练的研究方向，核心目标是让 AI Agent 通过与环境交互、接收反馈信号、优化策略来提升执行能力。该领域正处于从传统 SFT（监督微调）范式向 RL-driven self-improving 范式转型的关键阶段。

**核心挑战**：Agentic RL 面临三大关键瓶颈：

1. **Credit Assignment Problem（信用分配问题）**：多步长程任务中，稀疏的终点反馈（成功/失败）无法将奖励合理分配到中间步骤，导致正确行为无法被强化、失败原因难以定位。这是 GUI Agent、Web Agent、Embodied Agent 等长程决策场景的共同痛点。

2. **Reward Signal Design（奖励信号设计）**：如何设计可验证、可程序化、可泛化的奖励信号？Outcome Reward 提供高保真但稀疏信号，Process Reward 提供密集监督但易受 bias 和 reward hacking 影响。两者的权衡是当前研究焦点。

3. **Data Efficiency & Sample Cost（数据效率与采样成本）**：Online RL 需要大量环境交互，成本高昂且训练不稳定；Offline RL 稳定但存在 distribution shift 和时序短视问题。如何在有限数据预算下实现高效学习是关键约束。

**研究趋势**：从 2023-2026 年，该领域经历了三个重要演进阶段：

- **探索阶段（2023）**：RLHF 在对话场景成熟，开始向 Agent 领域迁移；Process Reward Model (PRM) vs Outcome Reward Model (ORM) 的理论争论开始。
- **发展阶段（2024）**：Agent Q、WebVoyager 等工作尝试 MCTS + self-improvement；Outcome vs Process Supervision 的实证比较出现（arXiv 2408.02100）；DeepSeek-R1 展示 GRPO 在可验证任务上的威力。
- **成熟阶段（2025-2026）**：GUI Agent RL 成为热点（MobileRL、UI-R1、SOLAR-RL）；Self-improving Agent 框架涌现（UI-Voyager、UI-Genie）；Credit Assignment 方法百花齐放（GRSD、ADAGRPO、ADMIRE）。

---

## 技术路线

### 2.1 GRPO-based GUI Agent RL 路线

**代表论文**：[[2500-UiR1EnhancingEfficient]]、[[2025-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]]、[[2500-CraftGuiCurriculumReinforced]]、[[2604-ClawGUI]]

**核心思路**：将 DeepSeek-R1 的 GRPO（Group Relative Policy Optimization）方法适配到 GUI Agent 场景，利用任务的可程序化验证特性设计 rule-based reward，实现少量高质量样本的高效 RL 训练。

- **UI-R1**：首次将 rule-based RL 系统应用于 GUI action prediction。设计 action type + coordinate + format 三类奖励，仅用 **136 条高质量任务**在 Qwen2.5-VL-3B 上取得 ScreenSpot 22.1% 提升。核心贡献是证明"少量高质量困难样本 + rule reward > 大规模 SFT 数据"。

- **MobileRL (ADAGRPO)**：提出 Difficulty-Adaptive GRPO，通过 difficulty-adaptive positive replay 和 failure curriculum filtering 适应任务难度分布。引入 shortest-path reward adjustment 解决多步任务长度不一致问题。在 AndroidWorld 达到 **80.2%** 成功率（SOTA）。

- **CRAFT-GUI**：基于 GRPO 的课程学习框架，从简单短任务逐步过渡到复杂长任务。结合简单规则信号与模型评估的细粒度奖励机制。在 AndroidWorld 提升 7.1%，私有数据集提升 10.3%。

- **ClawGUI**：首个开源 GUI Agent RL 基础设施，集成 GiGPO + Process Reward Model 提供密集 step-level supervision。ClawGUI-2B 在 MobileWorld GUI-Only 达到 17.1%。

**优势**：数据效率极高；直接优化执行成功而非模仿文本形式；适合可程序验证的 GUI 动作空间。

**局限**：依赖 reward 可程序化定义；适用范围偏向结构化单步动作；对长程多步任务需要额外 reward shaping。

### 2.2 Self-Improving Agent + Reward Model 路线

**代表论文**：[[2500-UiGenieSelfImproving]]、[[2600-UiVoyagerSelfEvolving]]、[[2600-UiMemSelfEvolving]]、[[2604-GenericAgent]]

**核心思路**：建立数据-模型闭环，让 agent 通过自主探索、失败经验利用和迭代训练持续提升能力。核心创新是先构建可靠 verifier/reward model，再扩张数据。

- **UI-Genie**：提出统一 Reward Model（UI-Genie-RM）作为 verifier，同时处理 action-level 和 task-level reward。通过规则验证 + 轨迹扰动 + hard negative mining 构建奖励数据（UI-Genie-RM-517k）。三轮 self-improvement 后达到 SOTA。关键创新：先解决"可验证性"，再扩张数据。

- **UI-Voyager**：两阶段框架——Rejection Fine-Tuning (RFT) 自动收集筛选高质量轨迹；Group Relative Self-Distillation (GRSD) 从成组 rollout 中定位 **fork points**，用成功轨迹为失败轨迹构造稠密步级监督。4B 模型在 AndroidWorld 达到 **81.0% Pass@1**，声称超越 human-level。核心贡献：失败经验利用 + credit assignment 细化。

- **UI-Mem**：Hierarchical Experience Memory，将 workflow、subtask skill、failure pattern 抽象为参数化模板。支持跨任务迁移与 memory-guided exploration。

- **GenericAgent**：提出"上下文信息密度最大化"作为长周期 Agent 的核心原则。五层分层按需记忆 + 自我进化（轨迹 → SOP 结晶）。100% 完成率且 token 消耗仅为同类系统 15%-35%。进化的是策略而非参数，是高可行性选择。

**优势**：减少人工标注依赖；失败经验利用提升数据效率；适应动态变化环境。

**局限**：高度依赖 reward model/verifier 正确性；自增强过程可能放大系统性偏差；工程复杂度高。

### 2.3 Credit Assignment for Long-Horizon Tasks 路线

**代表论文**：[[2604-SOLAR-RL]]、[[2026-Adaptive Milestone Reward for GUI Agents]]、[[2600-ContinualGuiAgents]]

**核心思路**：直接解决多步长程任务中稀疏奖励下的 credit assignment 问题，通过失败点检测、里程碑奖励、锚定奖励等机制将终点奖励转化为步级监督。

- **SOLAR-RL**：半在线 RL 框架，核心创新是从静态离线数据中重建多样化 rollout 候选、检测 **first failure point**、通过三阶段目标对齐奖励塑形（Aggregation → Base Normalization → Total Reward Alignment）将稀疏终点奖励转化为稠密步级监督。**零在线交互成本**下达到 online RL 级训练效果。关键设计：不依赖成组 rollout 对比（vs UI-Voyager GRSD）。

- **ADMIRE (Adaptive Milestone Reward)**：构建可验证、自适应的里程碑奖励系统。通过 anchoring trajectory to milestones（从成功探索中动态提炼），结合 asymmetric credit assignment：成功轨迹降噪、失败轨迹 scaffold。AndroidWorld 上 >10% 绝对提升。核心权衡：outcome reward 保真度 vs process reward 密度。

- **Continual GUI Agents (GUI-AiF)**：提出 Anchoring Point Reward (APR-iF) 与 Anchoring Region Reward (ARR-iF)，在分布漂移（domain-in-flux / resolution-in-flux）场景下保持稳定 grounding。持续学习设定下的 RL fine-tuning。

**优势**：直接解决 credit assignment 核心痛点；适用于长程任务；减少对环境交互的依赖（SOLAR-RL）。

**局限**：依赖 ground-truth labels 做 validity 检测（SOLAR-RL）；里程碑质量依赖成功轨迹覆盖度；持续学习稳定性需更多验证。

### 2.4 Test-Time RL / Inference-Time Optimization 路线

**代表论文**：[[2500-TestTimeReinforcementLearning]]、[[2604-AdaptiveGrounding]]

**核心思路**：将 RL 从训练阶段延伸到推理阶段，利用 test-time computation 进行自校正和优化，无需额外标注。

- **GUI-RCPO**：基于 Region Consistency 的 test-time RL。多次采样预测的空间一致性作为 reward，仅用 **1,272 条无标注数据**取得 3-6% 提升。核心创新：prediction set 内部的 self-supervised reward，无需外部标注。

- **PND (Positive-and-Negative Decoding)**：training-free 推理框架，通过正向视觉放大路径与负向 counterfactual 路径对比，解决 VLM 的 attention deficit 问题。POPE benchmark 上最高 **6.5%** 提升。核心洞察：视觉特征在解码时被系统性低估。

**优势**：无标注需求；training-free；即插即用。

**局限**：依赖"正确答案附近会形成预测共识"假设；计算开销增加；适用范围偏 bbox-style grounding。

### 2.5 Principle-Constrained RL / Curriculum RL 路线

**代表论文**：[[2500-OrcustStepwiseFeedbackReinforcement]]、[[2500-GuiExplorationLabEnhancing]]

**核心思路**：通过环境可验证的原则约束或课程学习策略，提升 RL 训练的稳定性和数据效率。

- **Orcust**：Principle-Constrained Reward Modeling (PCRM) + Online Virtual Machine-based Trajectory Construction (OVTC)。环境可验证的原则 + LLM 生成的奖励信号 + 自标记子目标。ScreenSpot 提升 22.2%，ScreenSpot-Pro 提升 23.9%。

- **GUI Exploration Lab**：POMDP 框架下的多轮强化学习仿真环境引擎。单轮 RL 用于基础记忆，多轮 RL 发展探索策略。静态基准 85% 成功率，交互式环境 90%。

**优势**：奖励信号可解释性强；动态轨迹生成适应环境变化；课程学习提升适应性。

**局限**：极端动态环境下表现待验证；计算成本较高；适用范围可能受限。

---

## Datasets & Benchmarks

| Benchmark | 平台/场景 | 规模 | 评估指标 | SOTA | 特点 |
|:----------|:----------|:-----|:---------|:-----|:-----|
| **AndroidWorld** | Android Mobile | 116 任务，20 apps | Success Rate / Pass@1 | MobileRL-9B: 80.2% / UI-Voyager-4B: 81.0% | 移动端长程任务，真实 app 环境 |
| **AndroidLab** | Android Mobile | 138 任务 | Success Rate | MobileRL-9B: 53.6% | 在线交互评测 |
| **ScreenSpot** | Mobile/Desktop/Web | 多平台 grounding | Accuracy | UI-R1: +22.1% vs baseline | GUI grounding benchmark，OOD 测试 |
| **ScreenSpot-Pro** | Multi-platform | 更高难度 grounding | Accuracy | Orcust: +23.9% | OOD grounding，分辨率/布局变化 |
| **AndroidControl** | Android Mobile | Low & High complexity | Success Rate | SOLAR-RL: 超越 offline+online RL | 移动端控制任务，难度分级 |
| **GUI-Odyssey** | Android Mobile | 8,334 episodes，212 apps | Success Rate | SOLAR-RL 有效 | Cross-app 导航 benchmark |
| **MobileWorld** | Android Mobile | GUI-Only tasks | Success Rate | ClawGUI-2B: 17.1% | GUI Agent 综合评测 |
| **SOP-bench** | 通用 Agent | SOP 任务 | Completion Rate | GenericAgent: 100% | SOP 执行能力测试 |
| **Lifelong AgentBench** | 长周期 Agent | 长程任务 | Completion Rate | GenericAgent: 100% | 长周期任务评测 |
| **BrowseComp-ZH** | Web | 多跳推理 | Accuracy | GenericAgent: 0.60 (3x baseline) | 网页多跳推理 |

**Benchmark 演进趋势**：
- 从静态 grounding（ScreenSpot）到动态交互（AndroidWorld、AndroidLab）
- 从终点评估到过程级评估（Pass@1 vs step-level）
- 从离线测试到在线交互
- 从单平台到跨平台统一评测

---

## Key Takeaways

1. **GRPO 正在重塑 GUI Agent 训练范式**：UI-R1 证明 136 条高质量任务 + rule-based reward 的 RL 训练可达到或超越大规模 SFT。RL 直接优化执行成功而非模仿文本形式，数据效率显著更高。这是从"模仿学习驱动"向"可验证策略优化驱动"的关键转折。

2. **Credit Assignment 是长程 Agent RL 的核心瓶颈**：SOLAR-RL 的 first failure point detection、UI-Voyager 的 GRSD fork point 定位、ADMIRE 的 milestone reward 都是针对稀疏奖励下步级监督不足的解决方案。该方向窗口正在迅速关闭（多个 concurrent work 覆盖大部分设计空间）。

3. **Self-Improving Agent 框架强调 Verifier-First 原则**：UI-Genie 先构建可靠 reward model，再扩张数据；UI-Voyager 先 RFT 筛选高质量轨迹，再 GRSD 构造步级监督。"先解决可验证性，再放大数据"成为共识设计模式。

4. **Outcome vs Process Reward 的权衡是核心理论争论**：Outcome Reward 保真度高但稀疏，Process Reward 密集但易受 bias。ADMIRE 的 adaptive milestone、SOLAR-RL 的三阶段 alignment 都是在两者之间寻找平衡。PRM vs ORM 的实证比较（arXiv 2408.02100）显示 PRM 在需要逐步推理的任务上更优。

5. **Test-Time RL 开辟新范式**：GUI-RCPO 的 region consistency reward、PND 的 contrastive decoding 都是在推理阶段进行 RL 式优化，无需额外标注或训练。这是与 train-time scaling 并行的重要路线。

6. **开源 RL 基础设施开始出现**：ClawGUI 是首个开源 GUI Agent RL 基础设施，填补训练-评测-部署的完整闭环。这标志着该领域从论文方法创新进入工程基础设施阶段。

---

## Open Problems

### 核心技术挑战

1. **长程任务的 Credit Assignment 稳定性**：现有方法（GRSD、first failure point detection）依赖状态对齐或 ground-truth labels，在真实界面（动画、弹窗、个性化布局）中可靠性存疑。如何在高噪声、多分支、状态不完全可观测场景中稳定实现步级监督？

2. **Self-Improving 的系统性偏差风险**：Reward model/verifier 若存在错误判断，自增强过程可能放大偏差而非纠错。如何构建"可纠错"而非"可增强"的自进化系统？GenericAgent 的 SOP 结晶验证机制值得借鉴。

3. **Reward Signal 的泛化边界**：Rule-based reward 对结构化单步动作有效，但对长程规划、模糊指令、动态状态变化如何设计？Outcome reward 与 process reward 的最优组合策略是什么？

### 数据与评测挑战

4. **真实环境评测覆盖率不足**：当前 benchmark 多在仿真器测试，缺少真实设备、真实账号、真实网络环境下的系统评测。对抗性场景、隐私泄露、错误恢复等高风险情况几乎未被覆盖。

5. **过程级评估自动化难题**：如何在不引入额外人工标注的前提下，准确捕捉复杂任务中每一步的关键状态变化？Pass@1 vs step-level accuracy 的权衡。

6. **跨域/跨分辨率泛化验证**：Continual GUI Agents 提出 APR-iF/ARR-iF，但在更复杂界面变化（动画、主题切换、个性化布局）下的鲁棒性需更多验证。

### 系统与工程挑战

7. **RL 训练稳定性与采样成本**：GRPO、PPO 等方法对采样策略、超参数敏感。如何在保持稳定性的同时控制环境交互成本？Offline RL + semi-online（SOLAR-RL）是否是最佳折中？

8. **Self-Improving 工程复杂度**：UI-Genie、UI-Voyager 等框架涉及多模块协调（数据生成、筛选、蒸馏、迭代训练），实现门槛高。如何设计更简洁的自增强架构？

9. **推理效率与实时部署**：Test-time RL、multi-module framework 都增加推理开销。如何在保持长程决策质量的同时满足实时响应需求？

---

## 调研日志

### 2026-04-28 初版

- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 47 篇 RL 相关论文，本次重点分析 15 篇核心论文
- **核心发现**: GRPO 成为 GUI Agent RL 主流范式；Credit Assignment 方法百花齐放；Self-Improving 强调 Verifier-First；Test-Time RL 开辟新路线
- **未能获取**: 部分 arXiv 论文全文待补充（ADMIRE、GenericAgent 等基于 abstract）
- **status**: success

---

## 参考文献

### Credit Assignment & Long-Horizon RL
- [[2604-SOLAR-RL]] - SOLAR-RL: First failure point detection + 三阶段 reward alignment
- [[2026-Adaptive Milestone Reward for GUI Agents]] - ADMIRE: Adaptive milestone reward
- [[2600-ContinualGuiAgents]] - GUI-AiF: Anchoring reward for continual learning
- [[2600-UiVoyagerSelfEvolving]] - UI-Voyager: GRSD fork point detection

### GRPO-based GUI Agent RL
- [[2500-UiR1EnhancingEfficient]] - UI-R1: Rule-based RL (136 samples)
- [[2025-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]] - MobileRL: ADAGRPO (80.2% AndroidWorld)
- [[2500-CraftGuiCurriculumReinforced]] - CRAFT-GUI: Curriculum + GRPO
- [[2604-ClawGUI]] - ClawGUI: 首个开源 RL infrastructure

### Self-Improving Agent
- [[2500-UiGenieSelfImproving]] - UI-Genie: Unified reward model + self-improvement
- [[2600-UiMemSelfEvolving]] - UI-Mem: Hierarchical experience memory
- [[2604-GenericAgent]] - GenericAgent: Context density maximization + SOP evolution

### Test-Time RL & Inference Optimization
- [[2500-TestTimeReinforcementLearning]] - GUI-RCPO: Region consistency reward
- [[2604-AdaptiveGrounding]] - PND: Contrastive decoding for grounding

### Principle-Constrained & Curriculum RL
- [[2500-OrcustStepwiseFeedbackReinforcement]] - Orcust: PCRM + OVTC
- [[2500-GuiExplorationLabEnhancing]] - GUI Exploration Lab: Multi-turn RL

### Survey & Overview
- [[2500-SurveyReinforcementLearningOptimization]] - RL for Optimization in Automation
- [[Topics/GUIAgent-Survey]] - GUI Agent 研究综述（含 RL 路线）