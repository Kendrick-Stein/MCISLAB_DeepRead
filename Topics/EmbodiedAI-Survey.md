---
title: Embodied AI Survey
tags: [survey, VLA, manipulation, navigation, embodied-ai, robotics]
date_updated: "2026-04-28"
year_range: 2023-2026
papers_analyzed: 45
---
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

## 参考文献

### Foundation Model Papers

- **RT-2**: "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control" (arXiv 2307.15818)
- **RT-X**: "Open X-Embodiment: Robotic Learning Datasets and RT-X Models" (arXiv 2310.08864)
- **OpenVLA**: "OpenVLA: An Open-Source Vision-Language-Action Model" (arXiv 2024)
- [[Papers/2604-EmbodiedMidtrain]] - VLM→VLA Mid-training

### Diffusion Policy Papers

- **Diffusion Policy**: "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion" (Chi et al., arXiv 2303.04367)
- [[Papers/2026-SeedPolicy- Horizon Scaling via Self-Evolving Diffusion Policy for Robot Manipulation]] - SeedPolicy with SEGA
- **ACT**: "Action Chunking with transformers" (2023)

### World Model Papers

- [[Papers/2604-MultiWorld]] - Multi-agent multi-view world model
- [[Papers/2604-HYWorld2]] - 3D world generation + planning
- [[Papers/2604-AgenticWorldModel]] - World Model Survey (Levels × Laws)

### RL Papers

- [[Papers/2600-LongnavR1HorizonAdaptive]] - Multi-turn RL for VLA navigation
- [[Papers/2500-ArpoEndEndPolicy]] - ARPO for GUI/Embodied policy optimization

### Unified Agent Papers

- [[Papers/2025-OmniActor- A Generalist GUI and Embodied Agent for 2D&3D Worlds]] - GUI + Embodied unified
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

### 2026-04-28 初版

- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 8 篇直接相关（VLA/manipulation/navigation），外部搜索补充 20+ 篇核心工作
- **核心发现**: VLA Foundation Model 成为主流范式；Diffusion Policy 解决 multimodal action generation；VLM→VLA 需要 data alignment；安全与可靠性开始系统性关注
- **未能获取**: RT-2、RT-X、OpenVLA、Diffusion Policy 全文（WebFetch arxiv.org 受限），仅基于 abstract 和搜索结果整理
- **status**: success