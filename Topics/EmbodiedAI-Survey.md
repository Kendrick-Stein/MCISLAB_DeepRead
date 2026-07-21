---
title: Embodied AI Survey
tags: [survey, VLA, manipulation, navigation, embodied-ai, robotics, embodied-reasoning, mobile-manipulation]
date_updated: "2026-07-20"
year_range: 2023-2026
papers_analyzed: 84
keywords: [embodied ai, robot learning, manipulation, embodied reasoning, spatial reasoning, mobile manipulation, language-conditioned, instruction following]
domain_map: EmbodiedAI
---

> 2026-07-20 起，本 survey 整合了原 Embodied-Reasoning-Survey（18 篇，专题一）与原 LanguageConditioned-MobileManipulation-Survey（24 篇，专题二），作为 EmbodiedAI 方向的统一沉淀文档（VLA-Survey / VLN-Survey 因体量与独立性保持单列）。原文见 git history。

## Overview

Embodied AI 是指让 AI 系统在物理或仿真环境中执行感知、决策、行动闭环的研究领域。核心是让 AI 从"理解"走向"操作"——不仅识别图像和文本，还能在 3D 世界中导航、操作物体、与人协作。这一方向处于 Vision-Language Model、Robot Learning、Reinforcement Learning、Control Theory 与 Human-Robot Interaction 的交叉地带，直接关系到家庭服务机器人、工业自动化、自动驾驶、仓储物流、辅助照护等多个真实应用场景。

**核心范式演进**：2023-2026 年，Embodied AI 经历了从"专用技能学习"到"通用 foundation model"的重大转型：

1. **Foundation Model 范式崛起（2023）**：Google DeepMind 发布 RT-2，首次证明 VLM 的 web-scale knowledge 可以直接迁移到 robot policy，开创 VLA（Vision-Language-Action）范式。同年 RT-X 发布，建立最大规模 cross-embodiment dataset（22 robots, 1M+ episodes）。

2. **开源生态成型（2024）**：OpenVLA 作为首个开源 VLA 模型发布，基于 Open X-Embodiment dataset 训练，性能媲美 RT-2-X。Diffusion Policy 被广泛采用，成为 action generation 的主流方法之一。

3. **能力边界拓展（2025-2026）**：研究从单一 manipulation 向 multi-agent、multi-view、long-horizon 场景扩展。安全与部署问题开始被系统性关注（VLA Safety Survey）。VLM→VLA 迁移的 data alignment 问题被深入分析（EmbodiedMidtrain）。

**核心挑战**：Embodied AI 面临四大关键瓶颈：

1. **数据与泛化**：真实机器人数据稀缺且昂贵，cross-embodiment transfer 需要解决 morphology gap；sim-to-real transfer 需要解决 domain gap。
2. **长时程决策**：Multi-step manipulation/navigation 任务中 reward 稀疏，credit assignment 困难，early exploration vs late success 的因果关系难以建模。
3. **安全与可靠性**：物理世界操作不可逆，错误操作可能导致财产损失或人身伤害；对抗攻击、data poisoning、prompt injection 带来新威胁。
4. **实时部署**：VLA 模型推理开销大，实时控制需要 sub-second latency，与多模态理解的计算需求存在矛盾。

---

## 技术路线

### 1. VLA Foundation Model 路线

**代表论文**：RT-2 (2023)、RT-X (2023)、OpenVLA (2024)、EmbodiedMidtrain (2026)

**核心思路**：将 robot policy learning 从 behavior cloning 转向 foundation model paradigm——利用 web-scale vision-language knowledge，通过少量 robot demonstration fine-tuning 获得可执行 policy。

**关键里程碑**：

| Model | Year | Key Innovation | Training Data |
|:------|:-----|:---------------|:--------------|
| **RT-2** | 2023 | 首次证明 VLM→VLA 直接迁移可行 | PaLM-E/VLM + robot demo |
| **RT-X** | 2023 | Cross-embodiment positive transfer | 22 robots, 1M+ episodes |
| **OpenVLA** | 2024 | 首个开源 VLA，消费级 GPU 可部署 | Open X-Embodiment |
| **π₀** | 2024 | Physical Intelligence commercial VLA | Proprietary large-scale |
| **EmbodiedMidtrain** | 2026 | VLM→VLA 数据对齐的 mid-training | VLA-aligned VLM data |

**核心发现**（来自 EmbodiedMidtrain）：
- VLA 数据占据与 VLM 分布大部分分离的紧凑区域——直接 fine-tune 会损失 generalization
- Data selection 应偏向 spatial reasoning 而非 text-centric tasks
- Mid-training 为 downstream VLA fine-tuning 提供更强初始化

**优势**：Zero-shot/few-shot task generalization；可理解自然语言指令；利用 web knowledge（如 "how to use a tool"）。  
**局限**：推理开销大；对 fine-grained manipulation（如 dexterous grasping）精度不足；real-time deployment 困难。

---

### 2. Diffusion Policy / Flow Matching 路线

**代表论文**：Diffusion Policy (Chi et al., 2023)、SeedPolicy (2026)、Action Chunking with Transformers (ACT, 2023)

**核心思路**：将 action generation 建模为 diffusion process，通过 iterative denoising 生成 multimodal action sequences，解决 behavior cloning 中的 mode collapse 问题。

**关键技术点**：

1. **Diffusion Policy**（Chi et al., 2023）：
   - 将 robot action sequence 作为 diffusion target
   - 视觉 encoder 提取 observation representation
   - 条件 diffusion decoder 生成 action trajectory
   - 在 multiple manipulation tasks 上超越 BC baselines

2. **SeedPolicy**（2026）：
   - 提出 Self-Evolving Gated Attention (SEGA) 解决 long-horizon observation 压缩
   - 在 RoboTwin 2.0 benchmark 上相对 DP 提升 36.8%（clean）/ 169%（randomized）
   - 与 RDT（1.2B VLA）competitive，但参数量少 1-2 个数量级

3. **ACT**（Action Chunking with Transformers）：
   - Transformer-based action prediction
   - Chunk action sequences而非 single step
   - Temporal attention 处理 observation history

**优势**：Multimodal action distribution modeling；适合 long-horizon tasks；无需 explicit reward function。  
**局限**：推理需要 multiple denoising steps，latency 较高；对 observation horizon 敏感。

---

### 3. World Model 路线

**代表论文**：MultiWorld (2026)、HY-World 2.0 (2026)、Agentic World Model Survey (2026)

**核心思路**：构建环境的 predictive model，通过 imagined rollouts 进行 planning，减少真实环境交互成本。

**关键工作**：

1. **MultiWorld**（2026）：
   - Multi-agent multi-view video world model
   - Multi-Agent Condition Module 实现精确多 Agent 控制
   - Global State Encoder 保证 multi-view consistency
   - 应用于 multi-player games 和 multi-robot manipulation

2. **HY-World 2.0**（2026）：
   - 多模态 3D 世界生成（text/image/video → 3DGS）
   - WorldNav 模块支持 3D scene understanding + planning
   - 开源 SOTA，与 Marble 相当

3. **World Model Survey**（2026）：
   - 提出 Levels × Laws taxonomy：L1 Predictor → L2 Simulator → L3 Evolver
   - Physical / Digital / Social / Scientific 四类 domain
   - 400+ 工作综合分析

**优势**：减少 real-world interaction cost；支持 counterfactual planning；可用于 safety verification。  
**局限**：Model accuracy 限制 planning horizon；多 Agent 交互建模复杂；与 VLA 结合的方式仍 unclear。

---

### 4. RL for Embodied Policy 路线

**代表论文**：LongNav-R1 (2026)、ARPO (2025)

**核心思路**：将 imitation learning 的 single-step supervision 转向 trajectory-level RL optimization，直接优化 long-horizon success。

**关键工作**：

1. **LongNav-R1**（2026）：
   - Multi-turn RL formulation for VLA navigation
   - Horizon-Adaptive Policy Optimization 解决不同轨迹长度 advantage 估计失真
   - 仅用 4,000 rollout 将 Qwen3-VL-2B success rate 从 64.3% 提升到 73.0%
   - Real-world zero-shot navigation 验证泛化性

2. **ARPO**（2025）：
   - End-to-End Policy Optimization with Experience Replay
   - 基于 GRPO 的 RL framework
   - 在 OSWorld benchmark 上取得 80% success rate

**优势**：直接优化 long-horizon success；credit assignment 更准确；适应 distribution shift。  
**局限**：需要大量 online interaction；RL training stability challenges；reward design sensitive。

---

### 5. Cross-Embodiment / Multi-Agent 路线

**代表论文**：RT-X (2023)、OmniActor (2025)、MultiWorld (2026)

**核心思路**：训练可跨不同 robot platform 迁移的 universal policy，或在 multi-agent 场景中实现 coordinated control。

**关键发现**：

1. **RT-X Cross-Embodiment**：
   - 在 22 种 robot 上联合训练
   - Positive transfer：cross-embodiment training 提升所有 single-robot performance
   - 统一 action representation 跨不同 morphology

2. **OmniActor GUI + Embodied Unified**：
   - Layer-heterogeneity MoE 解决 GUI 与 embodied data conflict
   - 浅层共享参数利用协同效应，深层分离参数消除冲突
   - GUI task accuracy 92%，Embodied task success rate 87%

3. **MultiWorld Multi-Agent**：
   - Multi-Agent Condition Module 实现 precise multi-agent controllability
   - Global State Encoder 确保 multi-view consistency

**优势**：减少 per-robot training cost；skill transfer between platforms；multi-robot coordination。  
**局限**：Morphology gap 难以完全消除；不同 robot 的 action space normalization 复杂。

---

### 6. Safety & Reliability 路线

**代表论文**：VLA Safety Survey (2026)

**核心思路**：系统性分析 VLA 在 physical deployment 中面临的 unique security threats，建立 training-time/inference-time defense framework。

**Threat Taxonomy**（VLA Safety Survey）：

| Timing | Threat Type | Description |
|:-------|:------------|:------------|
| Training-time | Data Poisoning | Manipulation dataset 被注入恶意轨迹 |
| Training-time | Backdoors | 特定 trigger 触发危险行为 |
| Inference-time | Adversarial Patches | 视觉输入被扰动导致错误 action |
| Inference-time | Cross-modal Perturbations | Vision + Language 多模态攻击 |
| Inference-time | Semantic Jailbreaks | 指令被精心设计绕过 safety constraint |
| Inference-time | Freezing Attacks | DoS-style attack 阻止 robot 响应 |

**Defense Mechanisms**：
- Training-time：data validation, adversarial training, certified robustness
- Runtime：safety-aware policy, monitoring & intervention, unified safety architecture

**Open Problems**（Survey 提出）：
- Certified robustness for VLA
- Physically realizable defense
- Safety-aware training procedure
- Unified runtime safety architecture
- Standardized evaluation protocol

---

## Datasets & Benchmarks

| Dataset/Benchmark | 类型 | 规模 | 评估指标 | SOTA | 特点 |
|:------------------|:-----|:-----|:---------|:-----|:-----|
| **Open X-Embodiment** | Training Data | 22 robots, 1M+ episodes, 527 skills | - | RT-X models | 最大规模 cross-embodiment dataset |
| **DROID** | Training Data | 多场景 manipulation demo | - | - | 多机构协作收集 |
| **CALVIN** | Benchmark | Long-horizon manipulation | Success Rate, Sequence Length | - | Language-conditioned，要求 compositional reasoning |
| **LIBERO** | Benchmark | Long-horizon manipulation | Success Rate, SPL | - | 多 task suite，测试 generalization |
| **RLBench** | Benchmark | 100+ manipulation tasks | Success Rate | Diffusion Policy, ACT | Simulation benchmark，多样化 task |
| **RoboTwin 2.0** | Benchmark | 50 manipulation tasks | Success Rate | SeedPolicy | Randomized settings，challenging |
| **DexGraspNet** | Benchmark | Dexterous grasping | Grasp Success Rate | - | 多物体 dexterous hand benchmark |
| **Habitat** | Benchmark | Navigation | SPL, Success Rate | - | Embodied navigation simulation |
| **AI2-THOR** | Benchmark | Navigation + Manipulation | Task Success | - | Household environment simulation |

**Benchmark 演进趋势**：
- 从 single-step evaluation（grasp success）到 long-horizon evaluation（CALVIN, LIBERO）
- 从 single-robot to cross-embodiment（Open X-Embodiment）
- 从 simulation-only to sim-to-real validation（RoboTwin 2.0 randomized settings）
- 从 task-specific to language-conditioned generalization（CALVIN）

---

## Key Takeaways

1. **VLA Foundation Model 已成为主流范式**：RT-2 证明 web-scale VLM knowledge 可直接迁移到 robot policy，RT-X 建立 cross-embodiment training 的 positive transfer 现象，OpenVLA 开源生态使研究门槛大幅降低。

2. **Diffusion Policy 是 action generation 的有效方法**：Multimodal action distribution modeling 解决 BC 的 mode collapse，在 manipulation tasks 上广泛验证。SeedPolicy 的 SEGA module 解决 long-horizon observation 压缩瓶颈。

3. **VLM→VLA 迁移需要 data alignment**：EmbodiedMidtrain 发现 VLA data 与 VLM distribution 存在显著 gap，需要 mid-training stage 通过 data selection 对齐。Spatial reasoning task 比 text-centric task 更有迁移价值。

4. **World Model 为 embodied planning 提供新路径**：MultiWorld 的 multi-agent/multi-view modeling、HY-World 的 3D scene generation + planning 都展示了 world model 在 embodied reasoning 中的潜力。

5. **RL 正从 imitation 走向 true policy optimization**：LongNav-R1 的 multi-turn RL + horizon-adaptive advantage 证明 trajectory-level optimization 比单步 SFT 更适合 long-horizon tasks。

6. **安全与可靠性开始被系统性关注**：VLA Safety Survey 定义了新问题域——VLA 的不可逆物理后果、多模态攻击面、实时约束带来区别于 LLM safety 和 classical robotic safety 的 unique challenges。

---

## Open Problems

### 核心技术挑战

1. **Sim-to-Real Gap 的系统性解决**：尽管 domain randomization、adversarial training 有进展，但真实世界的 lighting variation、material diversity、dynamic obstacle 等仍难以完全模拟。需要更 robust 的 sim-to-real transfer framework。

2. **Dexterous Manipulation 的精度瓶颈**：VLA 在 coarse manipulation（pick-and-place）表现良好，但 fine-grained dexterous manipulation（如 tool use、precision assembly）仍不如 specialized methods。

3. **Long-Horizon Credit Assignment**：Multi-step tasks 中 reward 稀疏，LongNav-R1 的 horizon-adaptive advantage 是有价值的尝试，但 generalizable solution 仍需更多验证。

4. **Real-Time Inference Constraint**：VLA 模型推理开销大，diffusion policy 需要 multiple denoising steps。如何在保持 policy quality 的同时满足 sub-second latency 是 deployment bottleneck。

### 数据与评测挑战

5. **高质量 Robot Demonstration 的获取成本**：Teleoperation data 质量高但收集成本高；autonomous collection 需要成熟 policy。如何在有限 expert data 下训练 generalist policy？

6. **Cross-Embodiment Morphology Gap**：RT-X 展示 positive transfer，但不同 robot 的 kinematics、dynamics、action space 差异仍限制 transfer efficiency。如何设计更 universal action representation？

7. **真实环境评测的覆盖率**：Benchmark 多在 simulation 或特定 lab setup，缺少真实 home/factory/outdoor 环境的 systematic evaluation。Safety-critical scenario testing 几乎空白。

### 安全与部署挑战

8. **VLA Certified Robustness**：Adversarial attack 防护需要理论上可证明的 robustness bound，但 VLA 的 multi-modal input space 和 continuous action space 使 certified defense 困难。

9. **不可逆操作的风险控制**：Physical operation 一旦执行难以撤销。如何设计 safety-aware policy、runtime monitor、emergency intervention mechanism？

10. **开放场景的 Language Understanding**：用户指令可能模糊、不一致或超出 robot capability。如何 robustly parse and ground natural language in physical context？

### 研究方向建议

- **Data-First 原则**：VLM→VLA 迁移的 data alignment 是关键瓶颈（EmbodiedMidtrain），优先解决数据选择和 distribution matching。
- **Safety-First 原则**：Physical deployment 的不可逆后果要求 safety-aware training 和 runtime defense 作为前置设计，而非事后补救。
- **Efficiency-First 原则**：Real-time inference 是 deployment bottleneck，优先考虑 policy architecture 的 inference cost。
- **Cross-Embodiment-First 原则**：Foundation model 的核心价值是 universality，优先设计跨 morphology 的 action representation。

---

## 专题一：Embodied Reasoning

> 并入自原 Embodied-Reasoning-Survey（2026-03-30，18 篇）。Embodied Reasoning 指 agent 基于感知输入进行推理并输出可执行动作的能力，是 foundation model 通用智能与具身控制之间的桥梁。三个 shift 概括 2023-2026 演进：**implicit → explicit reasoning**（端到端黑盒 → 可解释推理链）、**SFT → RL**（2025 是 RL for embodied reasoning 元年，GRPO 成 de facto 标准）、**general → in-domain**（通用 VLM 能力 → embodied-specific 数据与训练）。

### A1. Chain-of-Thought Embodied Reasoning

- **[[Papers/2407-ECoT|ECoT]]**（2024，开创性）：OpenVLA 中插入 6 步 embodied CoT（task plan → subtask → movement → gripper position → target bbox → summary），Gemini+SAM 自动生成训练数据。7B 超 RT-2-X (55B)，空间关系任务 +45%，人工纠正推理链 +48%。
- **[[Papers/2512-Lumo1|Lumo-1]]**（2025）：reasoning trace 结构化为 bbox → keypoint → trajectory + GRPO 精炼，Astribot S1 双臂验证超 π0。
- **[[Papers/2602-DM0|DM0]]**（2026）：Spatial Scaffolding（subtask → bbox → trajectory → action）coarse-to-fine 推理链 + gradient decoupling 保护 VLM reasoning 不被 action training 侵蚀。

优势：可解释、支持人工干预、推理结构可泛化。劣势：固定步骤不灵活、额外延迟、依赖复杂数据生成 pipeline。

### A2. RL-based Embodied Reasoning（GRPO 范式）

- **[[Papers/2506-RobotR1|Robot-R1]]**（NeurIPS 2025）：next-state prediction 重构为 MCQ 降低探索复杂度，7B 超 GPT-4o；SFT 0% vs RL 11.68%。
- **[[Papers/2504-EmbodiedR|Embodied-R]]**（2025）：解耦 perception (72B VLM) 与 reasoning (3B LM)，logical consistency reward；3B 超 OpenAI-o1 / Gemini-2.5-Pro，仅 5,000 样本。
- **[[Papers/2508-EmbodiedR1|Embodied-R1]]**（2025）："pointing"（2D 坐标）作 embodiment-agnostic 中间表示，两阶段 GRPO；3B 超 7B-13B baselines（65.50% vs SFT 41.25%）。
- **[[Papers/2512-ETPR1|ETP-R1]]**（2025）：GRPO 首入 graph-based VLN-CE，R2R-CE 65% SR。

**核心发现：RL 系统性优于 SFT**（三篇独立一致）；小模型 + targeted training > 大模型 + 弱训练。劣势：绝对成功率仍低（Robot-R1 11.68%）、多在仿真验证、MCQ 离散化丢失精细空间信息。

### A3. Data-Centric Embodied Reasoning

- **[[Papers/2401-SpatialVLM|SpatialVLM]]**（CVPR 2024）：10M 真实图像自动生成 20 亿 metric-space 空间 VQA。
- **[[Papers/2601-Thinker|Thinker]]**（IROS 2025）：4.8M robotics-specific 数据集，10B 超 32B baselines。
- **[[Papers/2510-VLASER|VLASER]]**（2025）：**OOD reasoning data 几乎无法迁移到 VLA performance，in-domain reasoning data 才是关键驱动力**——embodied reasoning 的 domain gap 远大于 NLP。

### A4. Explicit Spatial Representation for Reasoning

- **[[Papers/2602-GTA|GTA]]**（2026）：TSDF + topological graph 的 interactive metric world representation + counterfactual reasoning/ray-casting，SPL +16.4。
- **[[Papers/2601-SpatialNav|SpatialNav]]**（2026）：层级 Spatial Scene Graph（floor→room→object），zero-shot VLN 64.0% SR ≈ supervised SOTA。
- **[[Papers/2603-PROSPECT|PROSPECT]]**（2026）：CUT3R (3D) + SigLIP (2D) cross-attention 融合，长程任务 (100+ steps) SR +4.14%。
- **[[Papers/2507-MTU3D|MTU3D]]**（2025）：统一 3D visual grounding 与 active exploration，4 个导航 benchmark SOTA。

一致结论：**给 MLLM 显式结构化空间信息远优于让它从像素"猜"空间关系**。

### 专题一 Benchmarks

| Benchmark | 来源 | 规模 | SOTA | 特点 |
|:--|:--|:--|:--|:--|
| **ERQA** (Gemini Robotics) | Real | 400 questions / 7 categories | —（闭源） | 首个 embodied reasoning 专用 benchmark |
| **EmbodiedBench** | Sim | 1,128 tasks / 4 environments | 28.9% (GPT-4o) | 最全面的 MLLM embodied agent 评测 |
| **FoMER** | Real+Sim | 1,112 samples / 8 embodiments | 76.3% (o4-mini)；人类 84.5% | 首次分离 perceptual grounding 与 action reasoning |
| **Robot-R1 Bench** | Sim | MCQ (RLBench 基础) | 7B > GPT-4o | 为 RL-based reasoning 设计 |
| **SIMPLEREnv** | Sim | WidowX/Google Robot | 56.2% (Embodied-R1) | 标准评测平台 |

### 专题一 Open Problems

1. **Real-world transfer gap**：18 篇中仅 3 篇有 real robot 实验，RL-based reasoning 的仿真优势能否迁移真实世界未知。
2. **Reasoning 延迟 vs 实时控制**：fast/slow thinking trade-off 无系统性解法（DM0 Spatial Scaffolding、Embodied-R key-frame extraction 仅是缓解）。
3. **Long-horizon multi-step reasoning**：EmbodiedBench 最佳仅 28.9%，跨数十步的 error-robust 推理链远未达到。
4. **Reasoning 过程质量评估**：FoMER 揭示"猜对答案但推理错误"，仅看 final accuracy 不够，safety-critical 场景尤其危险。
5. **Reasoning × world model**：从 reactive perception 走向 mental simulation（预测行动后果再推理）是关键方向——与总览路线 3 交汇。

---

## 专题二：Language-Conditioned Mobile Manipulation

> 并入自原 LanguageConditioned-MobileManipulation-Survey（2026-04-02，24 篇）。LCMM = 理解自然语言指令 + 大规模环境导航 + 精细操作，是 VLN 与 VLA 的交叉地带。范式主线：**模块化 pipeline → 端到端 VLA → 统一 navigation-manipulation 架构**。核心难点：action space mismatch（底盘 ~5Hz 2-3D vs 末端 30-50Hz 6-7 DoF）、building-scale 与 object-level 空间表示割裂、10+ 步长程误差累积、数据稀缺。

### B1. 模块化 Pipeline（LLM/VLM Planning + Skill Library）

- **[[Papers/2204-SayCan|SayCan]]**（2022，开创）：LLM 候选技能 × learned affordance 打分，84% planning SR，受限 551 个预定义技能。
- **[[Papers/2305-TidyBot|TidyBot]]**（2023）：LLM 从少量示例归纳个性化偏好规则 + CLIP 泛化，真实世界 85% SR。
- **[[Papers/2401-OKRobot|OK-Robot]]**（2024）：zero-shot 组合 OWL-ViT + VoxelMap + AnyGrasp，无训练 58.5% SR。
- **[[Papers/2410-BUMBLE|BUMBLE]]**（2024）：building-scale，SoM prompting + 双层记忆；**73.7% 失败来自 VLM 推理错误**——spatial reasoning 是系统瓶颈。
- **[[Papers/2602-UniPlan|UniPlan]]**（2026）：VLM grounding → PDDL + Fast Downward 符号规划，~84% SR、仅 2 次 LLM 调用、规划 <0.7s。

### B2. 端到端 VLA 适配 Mobile Manipulation

- **[[Papers/2503-MoManipVLA|MoManipVLA]]**（CVPR 2025）：fixed-base VLA 的 EEF waypoints 经双层轨迹优化转 mobile；**GT segmentation 49.4% → Detic 11.3%**，感知而非规划是瓶颈。
- **[[Papers/2603-SGVLA|SG-VLA]]**（2026）：5 个 auxiliary spatial grounding decoder + 渐进式 3 阶段训练，ManiSkill-HAB 0.60→0.73；naive co-training 崩溃（→0.51）、temporal history 反而降性能（→0.49）。
- **[[Papers/2511-EchoVLA|EchoVLA]]**（2025）：scene memory（3D voxel + discrepancy-driven 更新）+ episodic memory，per-part diffusion policy，SR 0.31（+55% over π0.5）。
- **[[Papers/2509-AnywhereVLA|AnywhereVLA]]**（2025）：SLAM + frontier exploration + SmolVLA (450M)，Jetson Orin NX >10Hz；但实验规模极小、无 baseline。

### B3. 统一 Navigation-Manipulation 架构

- **[[Papers/2602-DM0|DM0]]**（2026）：Embodied-Native 预训练 + Spatial Scaffolding，2B 在 RoboChallenge Table30 62% SR 超 π0.5 (3B, 42.67%)；**首次同框架训练 navigation + manipulation**（导航仅 sim 验证）。
- **[[Papers/2504-Pi05|π0.5]]**（2025）：hierarchical inference（VLM 规划 → VLA 执行）+ 5 类异构数据 co-training，真实家庭 15 分钟级家务；navigation 限 room-scale。
- **[[Papers/2502-HiRobot|Hi Robot]]**（2025）：独立 VLM 指令理解 + π₀ 执行 + synthetic multi-turn 数据，超 GPT-4o baseline 40%+。
- **[[Papers/2512-WholeBodyVLA|WholeBodyVLA]]**（ICLR 2026）：无 action 标注 egocentric 视频训 Latent Action Model，dual latent codes（locomotion + manipulation），AgiBot X2 78.0% SR、8× 数据效率。
- **[[Papers/2401-MobileALOHA|Mobile ALOHA]]**（2024）：ACT 直接预测 16D 全身 action chunk，co-training +90% SR——端到端 whole-body 可行性先驱（无 language conditioning）。
- 相邻进展：[[Papers/2509-NavFoM|NavFoM]]（12.7M 样本 navigation foundation model，zero-shot 覆盖 VLN/ObjectNav/tracking/driving，multi-task 协同 tracking +49.4%）与 table-top VLA 的融合是统一系统的自然方向。

### B4. Spatial Representation 增强

- **[[Papers/2210-VLMaps|VLMaps]]**（2022）：CLIP/LSeg dense features 融合进 3D grid map，language-queryable。
- **[[Papers/2309-ConceptGraphs|ConceptGraphs]]**（2023）：2D foundation models 构建 open-vocabulary 3D scene graph，无需 3D 训练数据。
- **[[Papers/2410-DovSG|DovSG]]**（RA-L 2025）：动态可更新 scene graph（增量局部更新 13× 内存 / 20× 速度），长期任务 33.3% vs 静态 OK-Robot 5.0%——**动态更新是长期部署必要条件**。
- **[[Papers/2306-HomeRobot|HomeRobot/OVMM]]**（NeurIPS 2023）：定义 OVMM benchmark；**GT segmentation → Detic 性能断崖**。

### 专题二 Benchmarks

| Benchmark | 类型 | SOTA | 特点 |
|:--|:--|:--|:--|
| **HomeRobot OVMM** | Sim+Real | ~49.4% (MoManipVLA, GT seg) | open-vocabulary pick-and-place, unseen homes |
| **ManiSkill-HAB** | Sim | 0.73 (SG-VLA) | mobile manipulation 4 类任务 |
| **ALFRED** | Sim | ~70%+ | language-guided household |
| **BEHAVIOR-1K** | Sim | 较低 | 1000 活动，难度极高 |
| **RoboChallenge Table30** | Real | 62% (DM0) | navigation + manipulation 真机 |

没有 benchmark 完整覆盖 "open-vocabulary + building-scale navigation + dexterous manipulation + language" 全链路；**perception 是跨 benchmark 一致瓶颈**（HomeRobot / MoManipVLA / BUMBLE 三方独立证据）。

### 专题二 Key Takeaways 与 Open Problems

1. **Perception 是 LCMM 绝对瓶颈**（非 planning 非 control）：GT→learned 感知的跌落远大于任何架构改进——短期投入 open-vocabulary detection/segmentation 比改 VLA 架构更有效。
2. **Hierarchical（VLM reasoning + VLA execution）成主流**：π0.5 / Hi Robot / DM0 / UniPlan 殊途同归——高层语义推理与底层精细控制需要不同计算范式。
3. **Fixed-base → mobile 不是简单 action space 扩展**：需要 building-scale spatial understanding，table-top 预训练不能自然获得。
4. **显式空间表示是统一 nav+manip 的基础设施**，动态更新必要（DovSG 6.6×）；与端到端 VLA 的集成方式仍是 open question。
5. 未解：统一 spatial representation（topological map + 6-DoF affordance 双服务）；perception-action 闭环（边操作边主动感知）；真 open-vocabulary（复杂空间关系/模糊指令/个性化）；数据获取（heterogeneous co-training 目前最有效）；长期部署鲁棒性（continual learning / failure recovery 几乎空白）；统一 action space 设计（per-part diffusion / dual latent / shared backbone 三思路无定论）。

---

## 参考文献

### Foundation Model Papers

- **RT-2**: "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control" (arXiv 2307.15818)
- **RT-X**: "Open X-Embodiment: Robotic Learning Datasets and RT-X Models" (arXiv 2310.08864)
- **OpenVLA**: "OpenVLA: An Open-Source Vision-Language-Action Model" (arXiv 2024)
- [[Papers/2604-EmbodiedMidtrain]] - VLM→VLA Mid-training

### Diffusion Policy Papers

- **Diffusion Policy**: "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion" (Chi et al., arXiv 2303.04367)
- [[Papers/2603-SeedPolicy- Horizon Scaling via Self-Evolving Diffusion Policy for Robot Manipulation]] - SeedPolicy with SEGA
- **ACT**: "Action Chunking with transformers" (2023)

### World Model Papers

- [[Papers/2604-MultiWorld]] - Multi-agent multi-view world model
- [[Papers/2604-HYWorld2]] - 3D world generation + planning
- [[Papers/2604-AgenticWorldModel]] - World Model Survey (Levels × Laws)

### RL Papers

- [[Papers/2600-LongnavR1HorizonAdaptive]] - Multi-turn RL for VLA navigation
- [[Papers/2500-ArpoEndEndPolicy]] - ARPO for GUI/Embodied policy optimization

### Unified Agent Papers

- [[Papers/2509-OmniActor- A Generalist GUI and Embodied Agent for 2D&3D Worlds]] - GUI + Embodied unified
- [[Papers/2500-OmniactorGeneralistGuiEmbodied]] - Layer-heterogeneity MoE

### Safety Papers

- [[Papers/2604-VLASafety]] - VLA Safety Survey

### Benchmark Papers

- **CALVIN**: "CALVIN: A Benchmark for Language-Conditioned Policy Learning for Long-Horizon Robot Manipulation" (Mees et al., 2021)
- **LIBERO**: "LIBERO: Benchmark for Long-Horizon Robot Manipulation"
- **RLBench**: "RLBench: The Robot Learning Benchmark"
- **RoboTwin 2.0**: SeedPolicy paper benchmark

---

## 调研日志

### 2026-07-20 合并两份子 survey（survey 整合）
- **动因**: Supervisor 指示同方向 survey 合并。Embodied-Reasoning-Survey（2026-03-30，18 篇）与 LanguageConditioned-MobileManipulation-Survey（2026-04-02，24 篇）并入为专题一/专题二章节；两者与本 survey 论文重叠极少（DM0/MTU3D/π0.5 等数篇），papers_analyzed 45→84。
- **保留原则**: 专题章节自包含（各带 benchmarks 与 open problems），路线结构与关键数字全保留，压缩了论据展开。原始调研日志附后。
- **原 Embodied-Reasoning-Survey 日志**（2026-03-30）: vault 8 篇 + 新 digest 10 篇（ECoT, Embodied-R1, Lumo-1, Thinker, FoMER, Robot-R1, Embodied-R, SpatialVLM, VLASER, EmbodiedBench）；10 条 WebSearch query；无获取失败。
- **原 LCMM-Survey 日志**（2026-04-02）: vault 14 篇 + 新 digest 10 篇（TidyBot, HomeRobot, BUMBLE, DovSG, MoManipVLA, AnywhereVLA, EchoVLA, WholeBodyVLA, UniPlan, SG-VLA）；无获取失败。
- **status**: success

### 2026-04-28 初版

- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 8 篇直接相关（VLA/manipulation/navigation），外部搜索补充 20+ 篇核心工作
- **核心发现**: VLA Foundation Model 成为主流范式；Diffusion Policy 解决 multimodal action generation；VLM→VLA 需要 data alignment；安全与可靠性开始系统性关注
- **未能获取**: RT-2、RT-X、OpenVLA、Diffusion Policy 全文（WebFetch arxiv.org 受限），仅基于 abstract 和搜索结果整理
- **status**: success