---
title: Vision-Language-Action Models
description: 从 2022 RT-1 到 2026 π0.7 / GEN-1 的 VLA 全景——按 action 表示与 data recipe 双轴组织，覆盖 AR token / 连续 flow matching / hierarchical / latent / reasoning-augmented / hybrid / world-model-conditioned / RL-post-trained 八类技术路线，重点分析 scaling law、cross-embodiment 统一、real-world RL、reasoning-action 融合、data engine 工学术分化等前沿议题
tags: [VLA, manipulation, embodied-reasoning]
date_updated: "2026-07-21"
year_range: 2022-2026
keywords: [vla, vision-language-action, robot policy]
domain_map: EmbodiedAI
---

## Overview

VLA 把预训练 VLM 扩展为端到端机器人策略，将 internet-scale 的视觉-语言知识迁移到连续高频的 motor control，目标是替代 task-specific 手工设计、走向通用 embodied agent。

**领域活跃度（2024-2026）**：

- **时间线**：[[2212-RT1|RT-1]] (2022) 奠定 AR 范式 → [[2307-RT2|RT-2]] (2023) 注入 web VLM → [[2410-Pi0|π0]] (2024) flow matching 跨 50 Hz → [[2504-Pi05|π0.5]] (2025) 家庭长程 → [[2511-PiStar06|π*0.6]] (2025-11) real-world RL → [[2604-Pi07|π0.7]] / [[2604-GEN1|GEN-1]] (2026Q1-Q2) 宣称跨越商业阈值，仅三年从概念验证走到 deployment 讨论。
- **参与格局**：工业方向 Physical Intelligence（π 系列）/ Generalist AI（GEN 系列）/ Google DeepMind（Gemini Robotics）/ NVIDIA（GR00T / DreamZero）/ Figure AI（Helix）/ AgiBot（[[2512-GenieReasoner|GenieReasoner]]）/ Xiaomi（[[2602-XiaomiRobotics0|Xiaomi-Robotics-0]]）/ Dexmal·StepFun（[[2602-DM0|DM0]]）；开源方向 [[2406-OpenVLA|OpenVLA]] / [[2506-SmolVLA|SmolVLA]] / [[2510-XVLA|X-VLA]] / LeRobot 生态持续跟进。
- **学术产出**：2025H2-2026H1 主要会议（NeurIPS / ICLR / ICRA 2026）VLA 论文密度激增，arXiv VLA survey 8+ 篇；本笔记覆盖 79 篇核心 + 4 篇 survey（[[2507-VLATokenizationSurvey]]、[[2509-PureVLA]]、[[2510-EfficientVLASurvey]]、[[2405-VLASurvey]]——广义三层 taxonomy（components / control policy / task planner）的 TNNLS 正式版，适合作领域入口，但模块划分轴与 action interface 离散/连续、data regime、control frequency 等真正决定能力的轴脱节）。

**整体趋势**：

1. **Action representation 从 discrete 到 continuous**：RT-2 token（3 Hz）→ Octo diffusion → π0 flow matching（50 Hz chunk-level），continuous path 已是默认；离散路线退守到"辅助监督"角色（[[2504-Pi05]] FAST + flow 双头、[[2512-GenieReasoner]] FACT = VQ + flow decoder）。
2. **Dual-system 成 industry default**：System 2 VLM 1-10 Hz + System 1 action 20-200 Hz 的分层解耦被 π0.5 / GR00T N1 / Gemini Robotics / Helix / NaVILA 同时采纳；hierarchical with language intermediate 的历史包袱（语义表达力不足）由 latent action / reasoning trace / 2D trajectory 等替代中间表征消化。
3. **Data recipe > model size**：[[2506-SmolVLA|SmolVLA]] 0.45B、[[2510-XVLA|X-VLA]] 0.9B、[[2602-DM0|DM0]] 2B 反复在主流 benchmark 击败 3-7B baseline；[[2511-GEN0|GEN-0]] 虽然在 7B 观察到"intelligence threshold"相变，但跨越阈值后 data scaling 的 ROI 远大于继续扩参；[[2607-XiaomiRobotics1|Xiaomi-Robotics-1]] 固定 20K hr 数据时 2.6B/5.1B/10.5B 仅 61/75/79%，而 data scaling 把 unseen-env 成功率从 26% 拉到 75%——data 是当前更强 bottleneck 的第二条独立证据。
4. **Real-world RL 和 data engine 改写 ceiling**：[[2511-PiStar06|π*0.6]] 的 advantage conditioning + HIL rollout 首次让 4B 级 flow matching VLA 真实自改进；[[2602-GigaBrain05M|GigaBrain-0.5M*]] 的 RAMP 把它推广到"latent-conditioned"；[[2511-GEN0|GEN-0]] / [[2604-GEN1|GEN-1]] 的 500K 小时 wearable 数据路线让"数据天花板"从学术共识变成工业实验室专属筹码。
5. **评测从 lab saturation 转向 real-robot mastery**：LIBERO（98.7）/ CALVIN ABCD→D（4.80）接近饱和；战场迁移到 RoboChallenge Table30、[[2511-PiStar06|π*0.6]] 商业部署、AC-One long-horizon、[[2604-GEN1|GEN-1]] 6-task mastery suite 等 real-robot 评测——但这些评测各自为政，尚无统一 leaderboard。

## Problem & Motivation

VLA 试图解决的核心问题可以用 [[2509-PureVLA]] 的一句 framing 概括——**"understanding the instruction but failing to execute"**。大型 VLM 已具备视觉-语言理解能力，但把"懂指令"变成"真的做到"隔着**三重不对齐**：

1. **模态不对齐**：VLM 输出空间是 language token；机器人需要的是连续、高频、embodiment-specific 的 motor command。
2. **数据不对齐**：internet-scale VL 数据 ≈ 10¹² tokens，OXE 作为目前最大真实机器人数据聚合仅 ≈ 10⁷ tokens，**相差 5 个数量级**（[[2507-VLATokenizationSurvey]] §12）。
3. **时间尺度不对齐**：LLM 接受秒级延迟；机器人闭环控制需要 20-50 Hz。token-by-token 解码天然冲突（[[2307-RT2|RT-2]] 55B 只能 1-3 Hz）。

额外两个近期被放大的问题：

4. **Generalization vs compositional novelty**：VLA 即便在训练分布内指令也常需要 task-specific fine-tune；[[2604-Pi07|π0.7]] 明确指出 LLM 的 "compositional generalization" 在 VLA 上长期缺席。
5. **Reasoning-action 割裂**：VLM backbone 擅长语义推理，但 fine-tune action 会侵蚀 VLM 表征（[[2502-RoboBrain|RoboBrain]] / [[2506-VeBrain]] 的 MMVet 掉 16.3%；[[2602-XiaomiRobotics0]] w/o VL co-train 的 VL benchmark 全部归零）。

**为什么值得现在做**：

- **为什么不直接 IL / RL**：经典 IL 在开放指令和新物体上泛化差，经典 RL 在高维 + sparse reward 下样本灾难。VLM backbone 提供**语义先验**使 skill transfer 可行（RT-2 首次证明 "emergent generalization" 来自 web 知识 + co-fine-tuning）。
- **为什么不停留在 VLM + primitive planner**：SayCan / VoxPoser / Code as Policies 等 "LLM 挑 primitive" 路线在细粒度控制和新物体上受限；[[2305-TidyBot|TidyBot]] 仍依赖 predefined skill library。
- **为什么现在爆发**：(1) open-source VLM 成熟（SigLIP / Gemma3 / PaliGemma / Qwen2.5-VL / Qwen3-VL）；(2) 真实机器人数据跨过 100K episodes 门槛（OXE / DROID / AgiBot World）；(3) diffusion / flow matching 提供 scalable 的 continuous action 生成范式；(4) 2025 年起 real-world RL（π\*0.6 / RAMP）和 data engine（GEN-0/1）的突破改变了"数据 ceiling 在哪里"的判断。

## 技术路线对比

借用 [[2507-VLATokenizationSurvey]] 的 "action token 形态" 框架但合并到 8 条实际技术路线。每条路线分析核心思路、实际效果（代表数字）、优势、痛点，嵌入代表作。

### 1. Autoregressive Raw Action Token

- **核心思路**：把连续 action 离散化（uniform binning / VQ-VAE / FAST DCT），接在 VLM language token 之后做 next-token prediction，训练 loss 与 LLM pretraining 完全同构。谱系：[[2212-RT1]] → [[2307-RT2]] → [[2406-OpenVLA]] → [[2502-OpenVLA-OFT]] → FAST tokenizer → [[2512-GenieReasoner]]（FACT = VQ + flow-matching decoder）。
- **实际效果**：RT-1 130K episodes / 744 tasks / 3Hz 做出 AR VLA 首次规模化 demo；OpenVLA 7B 在 BridgeData 超 RT-2-X 55B +16.5%；OpenVLA-OFT 用 parallel decoding + action chunking 把推理从 166ms 压到 ~73ms，LIBERO 平均 97.1%（超 π0 的 94.2%）；GenieReasoner 用 FACT 在 ERIQ 拿 82.72% vs base 58.64%。
- **优势**：与 VLM 训练范式同构；可复用 LLM 生态（KV cache、speculative decoding、int4 量化——[[2406-OpenVLA|OpenVLA]] 证明 7B 直接 int4 不掉点）；token 离散便于 RL（advantage conditioning 通过 text prefix 天然可插）。
- **痛点**：
  - **推理延迟**：token-by-token AR 在 7B 上天然 1-6 Hz（RT-2 55B 只有 1-3 Hz），靠 OFT 的并行解码或 FAST tokenizer 缩短 action 序列才能进入 20+ Hz。
  - **Multi-modal action 分布丢失**：256-bin 对多峰连续分布近似差（Diffusion Policy 的核心 critique）。
  - **精度-token-length 冲突**：uniform binning 精度 vs token 数线性 trade-off；[[2604-DAERT|DAERT]] 展示 VLA 对**语言层面微小 rephrase** 的脆弱性（π0 LIBERO 93%→5.85%），部分原因即离散 token 对 prompt shortcut 敏感。

### 2. Continuous Flow-Matching / Diffusion Action Head

- **核心思路**：把 action 生成建模为 conditional DDPM 或 flow matching 的 denoising 过程，直接在 continuous space 学习轨迹分布。谱系：[[2303-DiffusionPolicy]]（奠基）→ [[2405-Octo]] → [[2410-Pi0]] → [[2504-Pi05]] → [[2506-SmolVLA]] → [[2510-XVLA]] → [[2604-Pi07]]。同族变体：[[2409-TinyVLA]]（<1.4B VLM + Diffusion Policy head, 20× 加速）、[[2503-GR00TN1]]（Eagle-2 VLM + flow matching DiT）、[[2512-Motus]]（Wan2.2 VGM + Tri-modal Joint Attention）。
- **实际效果**：π0 将 3B 模型推到 50Hz chunk-level 控制；π0.5 首次在真实 Airbnb 完成 kitchen/bedroom 15 分钟级长程任务；π0.6 上 SmolVLA 的 453M + Hugging Face LeRobot 生态验证小模型路线；X-VLA 0.9B 在 Simpler-WidowX 73.8% → 89.6%（PEFT 9M/1% 参数即可逼近全量 π0）；π0.7 zero-shot UR5e laundry folding 匹配**人类 top-2% teleoperator**（task progress 85.6% / success 80%）。
- **优势**：天然建模 multi-modal 连续分布；flow matching 1-4 步采样（比 DDPM 10+ 步快）；chunk-level 生成 + Real-Time Chunking（RTC）/async inference 解决 AR 延迟。
- **痛点**：
  - **Likelihood 不可解析**：PPO / trust region 不兼容；π\*0.6 的 "advantage conditioning"（二值 advantage 作 text prefix + CFG 推理）是目前最成熟的 RL 绕行方案。
  - **梯度污染 VLM**：Continuous flow matching loss 会侵蚀 VLM 语义（[[2504-Pi05]] Knowledge Insulation 用 stop-gradient + FAST 离散辅助监督解决；[[2512-GenieReasoner]] FACT 用离散 VQ token 学 + flow decoder 重构）。2026-07 新证据把侵蚀量化并挑战 KI 的充分性：[[2606-Act2Answer|Act2Answer]] 用"动作作答"协议测出 VLA 相比源 VLM 在语义类知识上掉 20-40 分，且知识在中层仍可线性解码、到动作通路衰减至近随机——问题是"读出通路"而非"数据遗忘"；[[2607-AnchorAlignVLA|Anchor-Align]] 证明 co-training+KI 路线存在 language-action 脱钩（LIBERO-PRO position-swap 0%），在同一 observation 上做 frozen VLM 逐层蒸馏 + 动作转方向词对齐更优（61.0→71.9，shuffle 标签控制实验排除正则化解释）。两篇一致指向：防遗忘应默认配 anchoring / VQA co-training，仅梯度隔离不够。
  - **延迟一致性**：Action chunk 边界不连续；π0.7 训练时注入 0-12 step inference delay 模拟 RTC；[[2604-SnapFlow]] 用 corrected consistency self-distillation 把 10 步 denoising 压到 1 步（π0.5 LIBERO 97.75%→98.75%，端到端 274ms→83ms 3.3×）。

### 3. Hierarchical with Language Intermediates

- **核心思路**：两层结构——上层 VLM 产出 language subtask（自然语言 / language motion / bounding box + trajectory），下层轻量 policy 条件执行。谱系：[[2204-SayCan]] / [[2303-PaLME]]（早期 LLM planner）→ [[2403-RTH]]（language motion "move arm forward 75cm"）→ [[2502-HiRobot]] / [[2412-NaVILA]] / [[2504-Pi05]] / [[2503-GR00TN1]]（近期 System 1/2 dual-rate）→ [[2502-HAMSTER]]（2D trajectory 作为 embodiment-agnostic 桥接）→ [[2512-WholeBodyVLA]]（humanoid loco-manipulation 的 dual LAM + discrete locomotion command）。
- **实际效果**：π0.5 对 unseen 家庭的 zero-shot 长程泛化；HiRobot 用 synthetic interaction data 实现 situated grounding 吊打 GPT-4o；GR00T N1 在 2.2B 参数下做 humanoid full-body；NaVILA 在 VLN-CE R2R Val-Unseen RGB-only 设置下 SR 54% / SPL 49%（ICRA 2026）；HAMSTER 相对 OpenVLA +50%。
- **优势**：
  - 语言中间表征可被 web / egocentric video co-training 增强。
  - 可解释、可 human-in-the-loop 干预（RT-H 的 language motion 可当场纠正）。
  - **数据分离**：高层 task 语义稀疏，低层 motion 稠密，缓解数据稀疏。
  - **频率分离**：高层 1-2 Hz，底层 20-50 Hz（NaVILA 的 Dual-Frequency Architecture、π0.5 的 async planning）。
- **痛点**：
  - **语言表达力不足**：contact-rich / deformable / 精细运动在语言层难表示，[[2507-VLATokenizationSurvey]] 建议 language 只做 high-level planning，细节交给 affordance / trajectory / goal video。
  - **上下层接口脆弱**：语义太窄限制下层，太宽下层难训练；上层延迟卡死整体频率。
  - **"并行但不协同"**：[[2604-BiCoord]] 的 STI 指标揭示 RLBench2 SMP 97% 但 ARD 115%——并行执行不等于紧耦合协同。

### 4. Latent Action from Unlabeled Video

- **核心思路**：从 action-free video（人类 / 跨 embodiment）无监督学 latent action space，先用 VLM 预测 latent，再以少量 action-labeled 数据做 decoder fine-tune。打开 internet-scale video 作为训练数据源。谱系：[[2402-Genie]]（generative interactive environment，VQ-VAE + ST-transformer）→ [[2410-LAPA]]（VQ-VAE 从 SSv2 人类视频预训练，7B VLM + 30-40× compute 超 OpenVLA +6.22%）→ UniVLA → [[2505-DreamGen]]（video diffusion 作为 offline data engine，log-linear NT scaling，GR00T N1 new-behavior 0% → 43%）→ [[2512-WholeBodyVLA]]（双 LAM：manipulation + locomotion）。
- **实际效果**：LAPA 用纯 human video 预训练正迁移到 Franka；DreamGen 证明 Cosmos / WAN2.1 fine-tune 后的 video 生成 + IDM 提取 pseudo-action 能在 GR1 humanoid 上实现 new behavior 43.2%（vs baseline 11.2%）、new env 28.5%（vs 0%）；[[2602-DreamZero]]（NVIDIA GEAR）把 video diffusion 14B 直接作为 VLA backbone，AgiBot unseen env+object 任务 task progress 62.2% 比最强 VLA baseline 翻倍（且 5B→14B scaling 信号明显）。
- **优势**：绕过 action-label 瓶颈；跨 embodiment 友好；VLM 预训练目标容易收敛（比 raw action 的 continuous regression 简单）。
- **痛点**：
  - **不可解释**：latent 无法像 language motion 那样被人当场纠正。
  - **Latent 混杂**：LAPA 承认 latent 把 camera motion / scene change / agent action 混在一起，对 fine-grained grasping 有害。
  - **Granularity / comprehensiveness / alignment 三道坎**：[[2507-VLATokenizationSurvey]] 明确**不推荐**把 latent 纳入未来 hierarchical 架构。
- **不走 latent 的两条平行路（2026-07 对照）**：human/play 数据不必经由 latent action 才能利用。[[2607-EgoSteer|EgoSteer]] 用 EgoSmith 管线把 in-the-wild egocentric 视频显式重建为统一 R^48 相机系 state-action（9.6K hr / 2.09M episodes，预训练呈 log-linear scaling，40 真机任务 75%），以表示一致性绕开 latent 的不可解释与混杂问题；[[2607-TAP|TAP]] 用 Inverse Dynamics 从 task-agnostic play / off-task 轨迹先学 "how to move" 再以少量 expert 对齐 "what to do"（SIMPLER 相对同架构 BC +10.2pp），代价是仍需 action label 但免语言/任务标注。

### 5. Reasoning-Augmented Action

- **核心思路**：显式把 reasoning chain 作为 meta-token 插在 action 前/间。纯语言 CoT → 空间化 reasoning → 联合 reasoning-action 优化三阶段演进。谱系：[[2407-ECoT]]（subtask → plan → bbox → gripper pixel → action 七段）→ RAD / DriveVLM / [[2503-CosmosReason1]]（Physical common sense + Embodied reasoning ontology + GRPO RL）→ [[2508-EmbodiedR1]]（"pointing" 作为 embodiment-agnostic 中间表示 + RFT）→ [[2512-GenieReasoner]]（统一 discrete reasoning + flow matching action）→ [[2601-RoboBrain25|RoboBrain 2.5]]（3D $(u,v,d)$ + hop-normalized temporal value）→ [[2602-RynnBrain]]（Chain-of-Point 交错 textual-spatial reasoning）。
- **实际效果**：ECoT 在 Bridge 上把成功率提 28%（2407）；Embodied-R1 3B 在 11 个 spatial benchmark rank 2.1 超 13B SOTA，xArm 真机 8 任务 zero-shot 87.5%（vs FSD 25%）；Cosmos-Reason1 在 intuitive physics (arrow of time, object permanence) 从 42%→81.5%（GPT-5、Gemini-2.5 几乎随机猜）；GenieReasoner 在 ERIQ 82.72%；Lumo-1 用 spatial action tokenizer + subtask completeness prediction，在 6 个 fine-tune 任务上全面超 π0/π0.5；RoboBrain 2.5 用 hop-based value 做**Reverse VOC**（time-reversed task progress prediction），把 GPT-5.2 的 reverse 10-20% 拉到 87-95%。
- **优势**：可解释、可 debug；reasoning 跨 embodiment 一致；可复用 LLM RL 栈；RL 优于 CoT 本身（[[2508-EmbodiedR1]] Table 6 RL > Think）。
- **痛点**：
  - **显著拖慢推理**：[[2407-ECoT]] 350 token/step，N-step freeze / async 摊销后仍 1-2 Hz；[[2509-AnywhereVLA]] 把 VLM 部署到云端 0.5 Hz，高频控制依赖 point tracker 15 Hz。
  - **High-quality reasoning 数据稀缺**：ECoT / RAD / Cosmos-Reason1 都用 auto-generation pipeline。
  - **"Action-token-based reasoning" 未实证**：[[2507-VLATokenizationSurvey]] 提出"不只在语言空间思考"的激进方向，目前无工作。

### 6. Hybrid Architectures

- **核心思路**：单模型内同时保留 AR discrete + continuous flow/diffusion 两条 action path，用 gating 或 CFG 融合。代表：[[2503-HybridVLA]]（diffusion noise + timestep 投影为 continuous token 放 AR token 前，共享 LLaMA-2 7B / Phi-2 2.7B）、[[2504-Pi05]] 的 discrete FAST + continuous flow matching 双监督、[[2512-GenieReasoner]] FACT tokenizer。
- **实际效果**：HybridVLA-7B 在 RLBench 10 任务超 OpenVLA +33% / CogACT +14%；π0.5 的两路设计是 "pre-train discrete / post-train continuous" 的范式化。
- **优势**：取 AR 的可解释 + continuous 的 multi-modality；共享 backbone 减少参数；discrete 分支天然抗 VLM 语义退化。
- **痛点**：
  - 工程复杂度高，两路互相干扰时难 debug。
  - Gate 阈值 / loss 权重 / 共享参数比例 设计空间大。
  - [[2510-EfficientVLASurvey]] 把 hybrid 归入 "specialized catch-all"；[[2509-PureVLA]] 把跨 paradigm 工作塞 hybrid 看作"taxonomy 崩坏"的信号。

### 7. Cross-Embodiment Soft Prompt / Unified Scaffold

- **核心思路**：把 heterogeneity 从 action output head 推到 input 端——每个数据源学一组 soft prompt embedding，或者用 spatial intelligence 作为共享 scaffold。代表：[[2510-XVLA]]（Learnable per-source soft prompt + Florence VLM + wrist encoder，ICLR 2026 接收 + LeRobot 集成）、[[2603-ACEBrain0]]（Scaffold-Specialize-Reconcile 范式：先 spatial scaffold，再分支训 AD/UAV expert，最后 data-free WUDI model merging）。
- **实际效果**：X-VLA 6/6 sim benchmark 5 个 SOTA，Simpler-WidowX 95.8% vs 71.9%，PEFT 9M 参数逼近全量 π0；T-SNE 显示 prompt 学到的是 hardware 语义而非 dataset ID；ACE-Brain-0 在 24 个 benchmark 中 20 个最佳，Gemini-3-Pro 被压过。
- **优势**：把 cross-embodiment 变成 multi-task prompt 学习问题；input-side conditioning 保留 VLM 预训练分布；prompt retrieval 为 zero-shot transfer 新 embodiment 提供 concrete 路径。
- **痛点**：
  - 每数据源一组 prompt 在 OXE-scale (1000+ 数据源) 下 scalability 未验证。
  - Action representation 仍要统一（EEF + Rotate6D），对 mobile base / humanoid / dexterous hand 等异构 morphology 的扩展未证。
  - Soft prompt 与 action head 是否真互斥？Table 1 里两者并存是最终版。

### 8. World Model Conditioning / RL Post-Training

- **核心思路**：把 world model 从"生成训练数据"（DreamGen 路线）转向"推理时 condition"——VLA policy 接收 world model 预测的未来 state 和 value，作为 planning 信号。或者用 world model 内跑 RL，闭环 refine policy。代表：[[2511-PiStar06|π*0.6]]（Recap = value function + advantage conditioning + HIL rollout）→ [[2602-GigaBrain05M]]（RAMP: RECAP 形式化为"对 z 边缘化的特例"，加 future visual latent 做条件）→ [[2602-WorldVLALoop]]（Closed-loop co-evolving world model + VLA via SANS dataset）。[[2511-GEN0]] / [[2604-GEN1]] 代表**数据-first** 路线。
- **实际效果**：π\*0.6 连续 13 小时咖啡馆做 espresso / 2 小时家庭折 laundry / 59 个巧克力包装盒工厂部署；GigaBrain-0 在 RoboChallenge 51.67%（超 π0.5 42.67%），RAMP 在 Box Packing / Espresso 长程任务上比 RECAP +30%；WorldVLALoop 在 real-world 从 SFT 13.3% → RL 第一轮 36.7% → 第二轮 50%；GEN-0 首次在 robotics 观察到 ossification 相变（≥7B "intelligence threshold"）+ power-law scaling $L(D)=(D_c/D)^{\alpha_D}$；GEN-1 把数据扩到 500K 小时 wearable、1h robot fine-tune 达 99% SR × 3× speed（blog only）；DreamZero 把 Wan2.1 14B 作为 WAM backbone，unseen env+object 62.2%，38× 推理加速后 7 Hz 部署。
- **2026-07 增量（WAM 分支细化 + 拿下 sim SOTA）**：[[2607-FlowWAM|FlowWAM]] 用 HSV 编码 optical flow 作为 video-native 统一动作表示，同一双流 DiT（Wan2.2-TI2V-5B）兼任 policy 与 world model（RoboTwin 2.0 92.94%、WorldArena TrajAcc 64.26 最佳），ablation 定位关键在"把 flow 映射进预训练视频先验的 RGB 空间"（raw flow 72.3 → HSV 89.8）而非 flow 本身；[[2607-ABotM05|ABot-M0.5]] 把 video → frame-level latent action → executable action 组织为三级生成链，Dual-level MoT 解耦 mobility/manipulation 分支、Dream Forcing 缓解 self-dreamed rollout 的 exposure bias（RoboTwin 2.0 94.1、LIBERO 99.4、RoboCasa365 40.4/46.6），首个统一移动与操作的 WAM，但 Composite-Unseen 仅 7.9%；[[2606-RehearseVLA|RehearseVLA]] 用 action-conditioned video WM 替代仿真器做 RL post-training（LIBERO 5-demo 79.6 vs SFT 74.85，与仿真器 RL 的 RIPT-VLA 持平），与 [[2602-WorldVLALoop]] 互证"失败/次优探索数据是 WM-as-simulator 的关键 ingredient"，但 WM 冻结、未设防 reward hacking；[[2606-Orca|Orca]] 把 modeling target 上移到 Next-State-Prediction 统一 world latent，冻结 backbone 后 language/image/action 三路 readout 随预训练数据 scaling 同步提升（双臂 OOD action readout 32.4 vs V-JEPA 2.1 的 17.0，但 binary success 仅 6%）——world latent 作为 VLA 上游表示的可反驳性检验。
- **优势**：
  - 突破 BC 天花板（π\*0.6 throughput 2× 不靠增量 demo）。
  - World model latent 提供 dense supervision，缓解 sparse reward。
  - 数据路线：wearable / synthetic 绕开 teleop 瓶颈。
- **痛点**：
  - **推理成本**：DreamZero 默认 5.7s/chunk，要 2× GB200 才 7 Hz；WAM 的 long-horizon drift (>200 帧) 至今未解。
  - **Reward hacking**：world model 的盲区被 policy exploit（[[2602-WorldVLALoop]] Fig 5 展示 policy 学会抓杯子背面），要 iterative close loop 才能稳住。
  - **数据壁垒**：GEN-0/1 完全 proprietary，500K 小时 wearable 数据 + 数据采集方法论不公开。学术社区系统性落后于工业实验室。

### 8 条路线的实质 trade-off

| 轴          | AR             | Flow/Diff      | Hierarchical   | Latent         | Reasoning       | Hybrid         | SoftPrompt   | WM/RL           |
| ---------- | -------------- | -------------- | -------------- | -------------- | --------------- | -------------- | ------------ | --------------- |
| 动作表达力      | 中（bin）         | 高              | 取决于低层          | 差可解            | —               | 高              | 高            | 高               |
| 推理频率       | 1-6 Hz         | 20-50 Hz       | 10-50 Hz async | 继承底层           | 显著更慢            | gate 决定        | 同 flow       | 1-7 Hz          |
| 数据利用       | action-labeled | action-labeled | VLM co-train 易 | 可用 video       | 需 CoT 数据        | action-labeled | multi-source | video/wearable  |
| 可解释性       | 中              | 低              | 高              | 低              | 高               | 中              | 中            | 部分              |
| VLM 生态复用   | 最佳             | 需 KI 隔离        | 高层复用           | 部分             | 高               | 复杂             | 好            | 中               |
| 代表作 rating | RT-2/OpenVLA 3 | π0/π0.5/π0.7 3 | SayCan/π0.5 3  | LAPA 2/Genie 3 | Cosmos-Reason 2 | HybridVLA 2    | X-VLA 3      | π\*0.6 2/GEN-0 3 |

### 2025-2026 的 convergence 观察

综合 65 篇笔记看到的几个**跨路线整合信号**：

1. **Flow matching + hierarchical + prompt expansion = 当前主流主干**（PI 系列 π0 → π0.5 → π\*0.6 → π0.7 + 追随者 GR00T N1 / X-VLA / SmolVLA / Motus）。
2. **离散 + 连续双监督成为标配**：π0.5 的 FAST discrete + flow continuous 双头、GenieReasoner 的 FACT、π0.7 的 Knowledge Insulation 都属于同一范式。
3. **Scaling law 正在浮现**：GEN-0 的 7B ossification / $L(D)=(D_c/D)^{\alpha_D}$；GEN-1 继续外推（64% → 99%）；DreamZero 5B→14B 在 VLA 上 +29pp（vs 同规模纯 VLA 仍 0%）；[[2607-XiaomiRobotics1|Xiaomi-Robotics-1]] 提供 GEN 系之外第二条独立 data-scaling 曲线（unseen-env 26%→75%）且实测 data > model size。但学术社区数据规模与工业差距正在拉大。
4. **Cross-embodiment 从 "per-embodiment head" 迁移到 "input-side soft prompt / latent action"**（X-VLA / LAPA / DreamZero / π0.7 UR5e 迁移 / 2602-DM0 的 Embodied-Native）。
5. **Real-world RL 范式转变**：π\*0.6 的 advantage conditioning 是"绕开 flow matching PPO 难题"的工程胜利，被 RAMP / WorldVLALoop 沿用；RL 的瓶颈正从"算法"移到"世界模型保真度 + reward 引擎"。
6. **Reasoning-action 从 shallow CoT 走向 unified discrete framework**（GenieReasoner FACT / Lumo-1 spatial action tokenizer / RoboBrain 2.5 3D+temporal）；"在 action space 做 reasoning" 的激进方向仍无实证。
7. **Memory 成为 long-horizon 明确子问题**：[[2603-MEM|MEM]]（video encoder + language memory，15min 任务）、[[2511-EchoVLA]]（dual PHC+hippocampus memory）、[[2507-StreamVLN]]（streaming KV-cache + voxel pruning）都在 2025-2026 集中出现；[[2607-LaMemVLA|LaMem-VLA]] 进一步把记忆从 policy-side 外挂挪进模型 native embedding 空间（短期视觉/长期动作双 vault，latent-native 相对 policy-side 条件化 +2pp）。
8. **Deployment 工程栈成熟**：async inference（SmolVLA）、RTC（π0.7）、1-step flow matching（SnapFlow 274→83ms）、int4 量化（OpenVLA）、Λ-mask 防 shortcut（Xiaomi-Robotics-0）、paged attention（GEN-1）——"VLA 推理延迟是核心瓶颈"的共识正在推动专用优化技术涌现。
9. **执行期监控与恢复独立成层（2026-07 新 pattern）**：失败常源于"执行中途坏掉且回不来"而非"不会做"，恢复机制可与策略学习解耦。[[2606-RehearseVLA|RehearseVLA]] 的 instant reflector 暴露 VLA 评测对 oracle 终止信号的隐性依赖（禁用后 OpenVLA-OFT 掉 11.8pp）；[[2607-RobustExecAgenticRL]] 在冻结 VLA 上用 PPO 训 {Execute/Retry/Repair/Reset} 调度层、以回滚历史 nominal state 恢复执行（扰动设定 LIBERO-Long 平均 +39.2pp，但缺规则阈值 baseline、扰动类型为方法量身定做）；与 venue 回填的 [[2606-AffordanceFieldInterventio]] test-time rollback 同线。
10. **下游适配配方成为受控研究对象**：[[2607-LoRAVLA]] 给出 π0 工业微调的实证 recipe——LoRA r=32 + SigLIP 全量微调持平 FFT（VRAM 36.2→10.8 GiB），embodiment adaptation 的瓶颈在视觉 domain shift 而非动作层；[[2607-DART]] 把适配数据的价值从"重学任务"改写为"测量 domain direction"——source/target one-shot update vector 相减 + SVD subspace 过滤，一条 target demo 把 domain shift 迁移到全部任务（LIBERO viewpoint shift 79.1% vs one-shot FT 31.5%，真机 UR10e 81.7%）。

## Datasets & Benchmarks

### Training Datasets

| Dataset | Year | 规模 | Embodiment | 代表使用 | 特点 |
|---|---|---|---|---|---|
| [[2212-RT1\|RT-1]] 自采 | 2022 | 130K episodes / 744 tasks | Everyday Robots mobile manip. | [[2307-RT2\|RT-2]] / [[2406-OpenVLA\|OpenVLA]] / RT-2-X | 13 机器人 × 17 月，奠定 AR-VLA 数据范式 |
| BridgeData V2 | 2023 | ~60K episodes | WidowX | [[2405-Octo\|Octo]] / [[2410-LAPA\|LAPA]] pretrain / SimplerEnv WidowX 基准 | 早期开源通用 BC |
| OXE (Open X-Embodiment) | 2024 | >1M episodes / 22 数据集聚合 | 跨 embodiment | [[2406-OpenVLA\|OpenVLA]] / [[2405-Octo\|Octo]] / [[2410-Pi0\|π0]] pretrain | 跨机构 de facto 标准 |
| DROID | 2024 | ~76K episodes | Franka 多实验室 | [[2512-Motus\|Motus]] / [[2510-XVLA\|X-VLA]] / [[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]] | Franka-centric multi-lab |
| RH20T | 2023 | 110K episodes / 147 primitive skills | 多 Franka platforms | [[2502-HAMSTER\|HAMSTER]] / [[2509-PureVLA\|PureVLA]] | Primitive skill pool |
| AgiBot World | 2024-2025 | ~728K episodes | Genie-1 / 自研 dual-arm | [[2503-GR00TN1\|GR00T-N1]] / [[2512-Motus\|Motus]] / [[2602-DM0\|DM0]] / [[2512-GenieReasoner\|GenieReasoner]] | humanoid + 双臂大规模开源 |
| EgoDex | 2024 | ~230K clips | Human egocentric | [[2512-Motus\|Motus]] latent action pretrain | action-free 人类视频，跨 embodiment 桥接 |
| Physical Intelligence 自采 | 2024-2026 | ~10K hr teleop (aggregate) | 多 robot | [[2410-Pi0\|π0]] / [[2504-Pi05\|π0.5]] / [[2511-PiStar06\|π*0.6]] / [[2604-Pi07\|π0.7]] | 私有；π0.5 训练中 97.6% 来自非目标平台 |
| Generalist AI wearable | 2025-2026 | 270K hr → 500K hr；10K hr/week | 零 robot data | [[2511-GEN0\|GEN-0]] / [[2604-GEN1\|GEN-1]] | 完全 proprietary，wearable 采集范式 |
| GigaWorld 合成视频 | 2025-2026 | ~6.65K hr 合成 | 多 embodiment | [[2602-GigaBrain05M\|GigaBrain-0.5]] pretrain（61% 合成 + 39% 真机） | synthetic data 首次在 VLA pretrain 占多数 |
| Xiaomi UMI 自采 | 2026 | 100K+ hr UMI + ~10K hr robot post-train | UMI handheld → 多 robot | [[2607-XiaomiRobotics1\|Xiaomi-Robotics-1]] | state-transition 自动标注（Qwen3.5-27B）；方法论公开、数据承诺后续发布；scaling curve 实测于 20K hr subset |
| EgoSmith（EgoSteer） | 2026 | 9.6K hr / 2.09M episodes（12 个公开 egocentric 数据集清洗） | Human egocentric → 双臂灵巧手 | [[2607-EgoSteer\|EgoSteer]] | 4D 手部轨迹重建为统一 R^48 state-action，预训练/后训练表示一致 |

### Manipulation sim benchmarks

| Benchmark                    | 规模 / 定位                 | Metric             | SOTA (2026-07)                                                                                                                                        |
| ---------------------------- | ----------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| LIBERO                       | 4 suite × 10 task 短程    | 4-suite avg SR     | **99.4%** ([[2607-ABotM05\|ABot-M0.5]], WAM) <br>98.7% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]] 4.7B) <br>98.2% (EO-1) <br>98.1% ([[2510-XVLA\|X-VLA]] 0.9B)                                   |
| LIBERO-Long                  | 长程子集                    | SR                 | 97.6% ([[2512-Motus\|Motus]] / [[2510-XVLA\|X-VLA]] 并列) <br>97.2% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                       |
| CALVIN ABCD→D                | In-dist 长程              | Avg task length /5 | **4.80** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                                                                                |
| CALVIN ABC→D                 | OOD 长程                  | Avg task length /5 | **4.75** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]], vs 次优 FLOWER 4.53)                                                                             |
| SimplerEnv Google Robot VM   | Real-to-sim             | avg SR             | **85.5%** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]]) <br>80.4% ([[2510-XVLA\|X-VLA]])                                                              |
| SimplerEnv Google Robot VA   | Real-to-sim             | avg SR             | 75.7% ([[2510-XVLA\|X-VLA]]) <br>74.7% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                                                  |
| SimplerEnv WidowX            | Real-to-sim             | avg SR             | **95.8%** ([[2510-XVLA\|X-VLA]], vs 前 SOTA MemoryVLA 71.9) <br>79.2% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                    |
| RoboCasa Kitchen Easy / Hard | 100 photorealistic 厨房任务 | SR                 | 70.0 / 39.0 ([[2510-XVLA\|X-VLA]])                                                                                                                    |
| RoboCasa365                  | 365-task 移动操作 pretraining 设置 | avg SR      | **57.4%** ([[2607-XiaomiRobotics1\|Xiaomi-Robotics-1]], Composite-Unseen 32.1%) <br>46.6% ([[2607-ABotM05\|ABot-M0.5]] +Condensed Memory, Composite-Unseen 7.9%)                                |
| VLABench                     | VLA-centric 综合          | Avg.PS             | 51.1 ([[2510-XVLA\|X-VLA]])                                                                                                                           |
| RoboTwin 2.0 Randomized      | 50-task bimanual Aloha  | avg SR             | **94.2%** ([[2607-ABotM05\|ABot-M0.5]]) <br>92.14% ([[2607-FlowWAM\|FlowWAM]]) <br>87.02% ([[2512-Motus\|Motus]]) <br>72.84% ([[2510-XVLA\|X-VLA]]) <br>43.84% ([[2504-Pi05\|π0.5]])                                                 |
| BiCoord                      | 18 bimanual 长程紧耦合       | single-task avg SR | 46.4% ([[2410-Pi0\|π0]], 次 [[2502-OpenVLA-OFT\|OpenVLA-OFT]] 40.5 / RDT 39.5 / DP 33.1) <br>27.2% ([[2410-Pi0\|π0]] multi-task, 相比 single-task −19pp) |

### Real-robot benchmarks

| Benchmark                                         | 平台                          | Metric                             | SOTA                                                                                                                                               |
| ------------------------------------------------- | --------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| RoboChallenge Table30 Specialist                  | UR5 / Franka / ARX5 / ALOHA | avg SR (30 tasks)                  | **62.00%** ([[2602-DM0\|DM0]] 2B) <br>51.67% (GigaBrain-0.1 3B, 中间版 2026-02-09 榜首) <br>51.00% (Spirit-v1.5 4B) <br>42.67% ([[2504-Pi05\|π0.5]] 3B) |
| RoboChallenge Table30 Generalist                  | 同上                          | avg SR / score                     | **37.3% / 49.08** ([[2602-DM0\|DM0]] 2B) <br>17.67% / 31.27 ([[2504-Pi05\|π0.5]]-G) <br>9.0% / 20.22 ([[2410-Pi0\|π0]]-G)                          |
| AC-One (10 long-horizon: coffee / laundry / fold) | ARX Aloha                   | partial SR (subgoal-weighted)      | **63.22%** ([[2512-Motus\|Motus]]) <br>14.79% ([[2504-Pi05\|π0.5]])                                                                                |
| Agilex-Aloha-2                                    | Agilex 双臂                   | partial SR                         | 59.30% ([[2512-Motus\|Motus]])                                                                                                                     |
| [[2604-Pi07\|π0.7]] UR5e zero-shot laundry        | 未见过的 UR5e                   | task-progress / SR                 | **85.6 / 80.0** ([[2604-Pi07\|π0.7]], 匹配人类 top-2% teleoperator)                                                                                    |
| [[2511-PiStar06\|π*0.6]] 商业部署                     | 咖啡馆 / 家庭 / 工厂               | 连续运行                               | 13 h espresso / 2 h laundry / 59 个巧克力包装盒 ([[2511-PiStar06\|π*0.6]])                                                                                |
| [[2602-GigaBrain05M\|GigaBrain-0.5M*]] RAMP       | PiPER / G1 humanoid         | 长程 task SR vs RECAP baseline       | Box Packing / Espresso 接近满分，vs RECAP **+30pp** ([[2602-GigaBrain05M\|GigaBrain-0.5M*]])                                                            |
| [[2604-GEN1\|GEN-1]] mastery suite (6 tasks)      | 多平台商用                       | avg SR (~1 h robot-data fine-tune) | **99%** ([[2604-GEN1\|GEN-1]]) <br>64% ([[2511-GEN0\|GEN-0]]) <br>19% (from-scratch)                                                               |
| [[2604-GEN1\|GEN-1]] box folding                  | 同上                          | 单任务完成时长                            | ~12 s ([[2604-GEN1\|GEN-1]], **2.8×** vs [[2410-Pi0\|π0]] / [[2511-GEN0\|GEN-0]] ~34 s)                                                            |

### Navigation benchmarks (VLN-CE Val-Unseen)

| Benchmark | 设置 | Metric | SOTA |
|---|---|---|---|
| VLN-CE R2R Val-Unseen | RGB-only | SR / SPL | **58.9 / 54.0** ([[2603-PROSPECT\|PROSPECT]]†) <br> 56.9 / 51.9 ([[2507-StreamVLN\|StreamVLN]]) <br> 54.0 / 49.0 ([[2412-NaVILA\|NaVILA]]†) |
| VLN-CE RxR Val-Unseen | RGB-only | SR / SPL | **54.6 / 46.2** ([[2603-PROSPECT\|PROSPECT]]†) <br> 52.9 / 46.0 ([[2507-StreamVLN\|StreamVLN]]) |
| ScanQA | 3D scene QA (16 frames) | Bleu-4 / CIDEr / EM | 15.7 / 19.8 / 28.8 ([[2507-StreamVLN\|StreamVLN]], 略超 [[2412-NaVILA\|NaVILA]]) |

† = 加 ScaleVLN + MMC4 训练配方；RGB-only 单视角已追平 panoramic + depth + waypoint 的 ETPNav（R2R SR ≈ 57 / SPL ≈ 49）。

### Reasoning / embodied-cognition benchmarks

| Benchmark | 定位 | Metric | SOTA |
|---|---|---|---|
| ERIQ (4 维 × 15 子任务 × 6,052 QA) | reasoning 解耦 action | avg acc | **82.72%** ([[2512-GenieReasoner\|GenieReasoner]]-3B) <br> 80.55% (Gemini-2.5-pro) <br> 77.61% (GPT-4o-mini) <br> 58.64% (Qwen2.5-VL-3B base) |
| Embodied reasoning 11-bench rank (ERQA / Where2Place / SAT / ...) | spatial / embodied reasoning | rank | rank 2.1 ([[2508-EmbodiedR1\|Embodied-R1]] 3B, 超 13B SOTA) |
| xArm 8-task real-world manipulation | zero-shot real-robot | SR | 87.5% ([[2508-EmbodiedR1\|Embodied-R1]], vs FSD baseline 25%) |
| Cosmos intuitive physics (arrow of time / object permanence) | physical reasoning | acc | 42% → **81.5%** ([[2503-CosmosReason1\|Cosmos-Reason1]], vs GPT-5 / Gemini-2.5-pro ≈ random) |
| Reverse VOC (time-reversed task progress) | temporal reasoning | acc | **87–95%** ([[2601-RoboBrain25\|RoboBrain 2.5]], vs GPT-5.2 10–20%) |

### 数据量级核心数字

- **OXE : LLM corpus ≈ 1 : 200,000**（[[2507-VLATokenizationSurvey]] §12）——VLA 与 LLM 能力鸿沟的最硬物质约束。
- **Generalist AI wearable 数据：500K hr，10K hr/week 增长**（[[2604-GEN1]]）——单家公司 proprietary 数据 ≥ 整个学术社区开源 robotics 数据总和；1 h robot data fine-tune 即可达 99% SR。
- **π0.5 co-training 中 97.6% 来自非目标平台**（[[2504-Pi05]]）——cross-embodiment 在大 mix 下成为 free transfer 而非 noise 源。
- **[[2602-GigaBrain05M\|GigaBrain-0.5]] pretraining = 61% 合成 + 39% 真机**（10,931 hr total，6,653 hr GigaWorld 合成）——合成数据首次在 VLA pretrain 占多数，边际收益尚未独立 ablate。
- **[[2604-BiCoord\|BiCoord]] STI = 42.16% vs RoboTwin 2.0 / RLBench2 ~8–11%**——首次用标量同时刻画"空间近 + 时间并行"，暴露现有 bimanual benchmark 的伪协同（RLBench2 SMP 97% 但 ARD 115%——并行 ≠ 协同）。

### Benchmark 饱和度与评测 crisis

- **LIBERO 已近饱和**：4-suite avg 98.7 / 98.2 / 98.1 差距在噪声量级；long-horizon sub-suite 仍可分辨（[[2602-XiaomiRobotics0\|Xiaomi]] 97.2 vs 次优 FLOWER 94.9）。
- **CALVIN ABC→D OOD 仍有 headroom**：Xiaomi 88.1 vs FLOWER 77.8（Task-5 列）——10pp gap 尚未收窄。
- **Real-robot 评测多样化但碎片化**：RoboChallenge、[[2511-PiStar06\|π*0.6]] business trial、AC-One long-horizon、PI UR5e 部署、[[2604-GEN1\|GEN-1]] 6-task mastery suite 各自独立；"RoboChallenge Specialist 榜首" 在月级时间尺度频繁易主。
- **自建 benchmark bias**：[[2601-RoboBrain25\|RoboBrain 2.5]] / [[2602-RynnBrain\|RynnBrain]] / [[2510-VLASER|Vlaser]] / [[2603-ACEBrain0\|ACE-Brain-0]] / [[2511-PelicanVL\|Pelican-VL]] 各自在自家 benchmark 领先——横向对比困难；[[2512-GenieReasoner\|GenieReasoner]] ERIQ 试图用 "action-decoupled reasoning benchmark" 标准化但尚未被社区采纳。
- **Metric 口径不齐**：[[2410-Pi0\|π0]] 50 Hz 是 chunk-level、[[2406-OpenVLA\|OpenVLA]] 6 Hz 是 token-level；TL（trajectory length）只算成功 episode → selection bias（[[2604-BiCoord]]）；partial SR / subgoal-weighted score 不同工作定义不同。
- **OOD 定义模糊**：[[2604-Pi07]] 自承"训练集太大无法严格定义 unseen"，compositional generalization claim 难证伪。
- **Oracle 终止信号的隐性依赖**：[[2606-RehearseVLA|RehearseVLA]] 禁用 ground-truth 终止信号（所有方法跑满 horizon）后 OpenVLA-OFT 从 74.85 掉到 63.05——post-success 冗余动作破坏已完成状态，现行 benchmark 数字系统性高估部署性能，无 oracle 评测协议值得推广。
- **World model 成为 policy evaluator**：[[2607-GigaWorld1|GigaWorld-1]] 用 WMBench 的 2,989 条 paired real/WM rollouts 把 surrogate 评测的成功标准从视频观感改为 real-world outcome agreement，综合 evaluator score 超最强 Wan baseline 14.9%；结论是 evaluator 质量取决于 long-horizon action fidelity、可迁移 physical prior 与空间对齐 action control，但 video WM 对 contact-sensitive failure 有 optimistic bias——policy evaluator 最危险的误差类型。

## Open Problems

### 1. Scaling law 的临界规模与 weight-level 机制

[[2511-GEN0]] 给出首个"robotics 有 scaling law"的可测形式 $L(D)=(D_c/D)^{\alpha_D}$ 在 16 个任务集一致；[[2604-GEN1]] 数据扩 1.85× 后 64% → 99%，验证幂律外推有 headroom。但：
- **Intelligence threshold 为何是 7B**？GEN-0 只有 1B/6B/7B 三个 size，缺 6.5B/7.5B 细扫描；是否是 data diversity 的函数？
- **Ossification 的 weight-level 机制**？当前只是行为层面观察，没有 effective rank / gradient norm 诊断。
- **Commercial threshold 的泛化性**："mastery 三元组（reliability+speed+improvisation）" 中 improvisation 完全定性，GEN-1 没给 quantitative breakdown。
- **Scaling 在学术数据上是否成立**？[[2412-RoboVLMs]] 等小规模实验反而发现 "in-domain > cross-embodiment"，与 GEN-0 大规模结论冲突——可能是 capacity 临界点问题，小模型 + 少数据下跨 embodiment 是 noise，大模型 + 长训练后变 signal。
- **第二条独立 data-scaling 曲线（2026-07）**：[[2607-XiaomiRobotics1]] 在 20K-hr UMI subset 上 unseen-env 成功率 26%→75%（12.5% 数据已达 53%），固定数据时 2.6B/5.1B/10.5B 为 61/75/79%——与 GEN-0 的 "data > size" 独立互证；但完整 100K-hr 曲线未报告、自动 caption 噪声不可外部审计。

### 2. Real-world RL for large VLAs

[[2511-PiStar06]] 的 Recap 首次在 4B+ flow matching VLA 上跑通真实 RL 自改进；[[2602-GigaBrain05M]] 把它形式化为 RAMP 的特例并加 future visual latent；[[2602-WorldVLALoop]] 用 closed-loop world model 迭代。仍未解：
- 只覆盖 episode-level sparse reward；dense / preference-based reward 未系统探索。
- **可 RL 修复 vs 结构性 failure**（hardware / perception bug）未区分。
- 与 Upside-Down RL / Decision Transformer / CFGRL 的理论联系尚不完整。
- RL 的 compute scaling 和 improvement 曲线不清楚（π\*0.6 只跑了 2 轮迭代，box assembly 第 3 轮会饱和还是继续提升？）。

### 3. Cross-embodiment 的正确抽象层

- Per-embodiment action head（π0 / GR00T N1 / RDT）→ input-side soft prompt（X-VLA）→ 统一 latent action（LAPA / UniVLA）的演化线尚未收敛。
- Morphology 巨差（gripper vs dexterous hand / single-arm vs humanoid loco-manipulation）能否共享 backbone？[[2604-Pi07]] UR5e 匹配人类 top-2% 是正面信号但 case-level。
- [[2512-WholeBodyVLA]] 用**双 LAM**（manipulation LAM + locomotion LAM）解耦"camera 静止 vs 移动"的 attention 冲突——提示未来 VLA 可能需要按 motion modality 拆解 latent space。
- OXE-scale（1000+ 数据源）下 per-source soft prompt 是否仍可行未验证；分层 prompt（embodiment-level + setup-level）可能是下一步。

### 4. Reasoning-action unification

现有路线仍是"在语言空间思考 → 产生动作"（ECoT / DriveVLM / Cosmos-Reason1 / GenieReasoner）。[[2507-VLATokenizationSurvey]] 提出的 **action-token-based reasoning**（直接在动作空间做 CoT）暂无实证。[[2508-EmbodiedR1]] Table 6 发现 RL 比 Think 重要得多（Where2Place +20 vs +2.5），暗示当前 CoT 的价值可能主要是 representation shaping 而非 inference-time planning。

### 5. Evaluation / reproducibility 危机

- **Lab tabletop 饱和**：LIBERO 98+ 已在噪声量级，CALVIN ABCD→D 接近上限。
- **自建 benchmark bias**：RoboBrain 2.5 / RynnBrain / Vlaser / ACE-Brain-0 / Pelican-VL 都在自家 benchmark 上领先——难以横向对比。
- **Metric 口径不齐**：π0 的 50 Hz 是 chunk-level，OpenVLA 的 6 Hz 是 token-level；TL（trajectory length）只算成功 episode 引入 selection bias（[[2604-BiCoord]]）。
- **OOD 定义模糊**：[[2604-Pi07]] 自己承认"训练集太大无法严格定义 unseen"，compositional generalization claim 难证伪。
- **ERIQ / BiCoord / RoboChallenge** 是 2025-2026 的新尝试（reasoning/coordination/real-robot），尚未社区采纳。
- **评测成本的两条候选出路（2026-07）**：world-model-as-evaluator（[[2607-GigaWorld1]]，paired rollout 的 outcome agreement 作为 benchmark 单位）与无 oracle 终止协议（[[2606-RehearseVLA]]）；前者的 contact-sensitive optimistic bias、后者未报告的误终止率是各自短板。[[2606-Act2Answer]] 补充第三类协议——把 VLM 知识 benchmark 改造成"用动作作答"的行为级评测，解耦知识缺失与控制失败。

### 6. Data engine 的工程 vs 学术 gap

[[2511-GEN0]] 270K hr + [[2604-GEN1]] 500K hr wearable + 10K hr/week，全 proprietary + Early Access Partner only；开源社区最大到 OXE / DROID / AgiBot World 百 K episodes 量级。若 scaling law 成立，学术社区将**系统性落后工业实验室**——类似 LLM 2023 后的 Anthropic/OpenAI/DeepMind 局面。更棘手的是 GEN 系列数据采集形态（wearable 传感器组合、action 空间对齐）完全不公开，**复现门槛不是"钱"而是"方法论本身不公开"**。

2026-07 更新：**"方法论黑箱"判断被部分削弱**——[[2607-XiaomiRobotics1]] 公开 UMI handheld gripper + state-transition 自动标注（Qwen3.5-27B captioning）的完整方法论（100K+ hr，数据/checkpoint 承诺后续发布）；[[2607-EgoSteer]] 的 EgoSmith 管线从公开 egocentric 数据集清洗出 9.6K hr 且工程细节可复用；[[2607-TAP]] 证明 30 hr autonomous play 可替代部分 expert 数据预算。非遥操作数据引擎的方法论正在公开化，gap 收敛为"数据本体与算力"而非"方法论本身"。

### 7. Memory 与 long-horizon

MEM（video encoder + language memory 解耦，15min 任务）、EchoVLA（PHC+hippocampus 双 memory）、StreamVLN（streaming KV cache + voxel pruning）、Pi0.7（MEM 集成）在 2025H2-2026H1 集中出现。共同开放问题：
- Memory 的**压缩粒度**（token / frame / 语义摘要）跨任务最优策略？
- Explicit voxel 3D memory 在动态遮挡下失灵（EchoVLA OR 任务输给 baseline），explicit vs implicit memory trade-off 未系统化。
- 长于 1 小时的 memory 几乎无工作；GEN-1 "连续 200+ 次无干预"demo 未开放评测协议。
- Latent-native vs policy-side：[[2607-LaMemVLA]] 显示记忆织入 native embedding 空间优于外部条件化（+2pp），但纯仿真、top-K 检索不可微——真机稳健性与可微检索是下一步。

### 8. Safety / alignment for embodied intelligence

- **Linguistic fragility**：[[2604-DAERT]] 证明仅改写语言指令即可把 π0 LIBERO 93%→5.85%，且具跨架构迁移性。
- **Emergent improvisation 的 double-edge**：GEN-1 blog 承认 emergent recovery 既是 capability 也是 alignment liability——机器人"自由解释任务"可能造成物理损害。
- **No-action probe**：DAERT 用 "no action" prompt 发现 π0.5 仍 54.9% 成功（退化成 vision-only），揭示当前 VLA 对语言依赖度的 hidden bias。
- 现有 safety 工作（ASIMOV-2.0 / Auto-Red-Teaming / Semantic Action Safety）主要围绕 semantic content，未触及物理 action 的 hazard 层面；Inference-Time Policy Steering 是可能方向。

## 调研日志

- **日期**：2026-04-23
- **侦察 survey**：3 篇（[[2509-PureVLA]]、[[2510-EfficientVLASurvey]]、[[2507-VLATokenizationSurvey]]）
- **候选论文清单**：
  - 需 digest（本次全部新 digest）：[[2212-RT1]]、[[2303-DiffusionPolicy]]、[[2307-VoxPoser]]、[[2409-TinyVLA]]、[[2410-LAPA]]、[[2502-HAMSTER]]、[[2503-HybridVLA]]（共 7 篇 rating ≥ 2；[[2406-RoboMamba]] rating 1 跳过）
  - 已有笔记（VLA 相关 rating ≥ 2）：~58 篇
- **新增论文数**：65 篇（全部 rating ≥ 2 均完整读过，无截断）
- **未能获取的论文**：无；重跑相对上轮补齐了 RT-1/VoxPoser/TinyVLA/HAMSTER 的 digest，RoboMamba rating=1 按 filter 自然排除
- **关键观察**：VLA 领域在 2025H2-2026H1 进入**多主线 convergence 期**——PI 系列（π0→π0.5→π\*0.6→π0.7）以 flow matching + hierarchical + prompt expansion 为主干拿下 commercial-grade 结果；cross-embodiment 正从 per-embodiment head 迁移到 soft prompt / latent action；Generalist AI 的 GEN-0/1 以完全 proprietary 的 wearable data engine 展示 scaling law 跨越 "commercial threshold"，与学术社区差距拉大；real-world RL（Recap / RAMP / WorldVLALoop）和 reasoning-action unification（GenieReasoner / Lumo-1 / RoboBrain 2.5）两条线同时突破。系统工程（SnapFlow / Xiaomi-Robotics-0 Λ-mask / MEM memory）成为必要配套。整体格局是"方法多样性未收敛，但工程底座、评测 crisis、data engine gap 三件事正在快速定型"。

## 🆕 Venue 回填增补（2026-06-26，CVF 近 3 年）

> 补收 CVF Embodied/VLA 方向 38 篇,完整清单+综合见 [[Reports/2026-06-26-VenueBackfill]]。

- **affordance grounding（主线一）**：[[2606-AffordGen]]（affordance 作 demo generation 先验）、[[2510-A0AnAffordance]]（spatial affordance + low-level execution 解耦）、[[2510-CoAVLA]]（Chain-of-Affordance）、[[2506-AffordDP]]（transferable affordance 接 diffusion policy）、[[2510-RAGNet]]（reasoning-based affordance benchmark 273k）。
- **think/reason before act（主线二）**：[[2506-CoTVLA]]（先生成 subgoal image）、[[2606-ACoTVLA]]（CoT 转到 action space）、[[2606-TRMVLA]]（keyframe-triggered reasoning + memory）、[[2606-AVAVLA]]（POMDP 历史条件策略，LIBERO 98%）、[[2606-HiFVLA]](motion vector 当低维 history)。
- **test-time 纠错**：[[2606-AffordanceFieldInterventio]] ⭐4（用 3D affordance field 检测并 rollback VLA 的 "Memory Trap"，不改参数）。
- **takeaway**：共同假设是端到端 VLA 缺显式中间结构（affordance / CoT / 3D geometry），加可解释中间表示提升 OOD 与 long-horizon;与 [[Topics/EmbodiedAI-Survey]] 专题一的 embodied CoT 线索呼应。

## 🆕 增量并入（2026-07-21，15 篇）

本批全部整合进上文各节：[[2607-XiaomiRobotics1]]、[[2607-GigaWorld1]]、[[2607-ABotM05]]、[[2607-FlowWAM]]、[[2606-RehearseVLA]]、[[2606-Orca]]、[[2607-EgoSteer]]、[[2607-TAP]]、[[2607-LaMemVLA]]、[[2607-AnchorAlignVLA]]、[[2606-Act2Answer]]、[[2607-RobustExecAgenticRL]]、[[2607-LoRAVLA]]、[[2607-DART]]、[[2405-VLASurvey]]。

结构性变化：

1. **WAM 系拿下 sim SOTA**：RoboTwin 2.0（[[2607-ABotM05]] 94.2 / [[2607-FlowWAM]] 92.14 超 Motus 87.02）、LIBERO（ABot-M0.5 99.4）、RoboCasa365（[[2607-XiaomiRobotics1]] 57.4）——video-generation-based policy 从"昂贵替代"变为 benchmark 领跑者，但 Composite-Unseen（7.9-32.1%）暴露组合泛化仍未解。
2. **表征遗忘从轶事变为可测量问题**：[[2606-Act2Answer]]（测量：语义类知识掉 20-40 分、中层可解码但动作通路读不出）+ [[2607-AnchorAlignVLA]]（干预：在线锚定优于 co-training+KI）构成同一现象的测量-干预对；Route 2 "梯度污染" 痛点的既有结论（KI 足够）被削弱。
3. **数据引擎方法论公开化**：Xiaomi UMI 100K hr / EgoSmith 9.6K hr / TAP autonomous play 削弱 Open Problem 6 的"方法论黑箱"判断。
4. **新增 convergence 观察 9（执行期监控与恢复独立成层）、10（下游适配配方受控研究）**；评测 crisis 新增 oracle 终止依赖与 world-model-as-evaluator（[[2607-GigaWorld1]]）两条。
