---
title: Vision-Language-Action Models
description: 从 2022 RT-1 到 2026 π0.7 / GEN-1 的 VLA 全景——按 action 表示与 data recipe 双轴组织，覆盖 AR token / 连续 flow matching / hierarchical / latent / reasoning-augmented / hybrid / world-model-conditioned / RL-post-trained 八类技术路线，重点分析 scaling law、cross-embodiment 统一、real-world RL、reasoning-action 融合、data engine 工学术分化等前沿议题
tags: [VLA, manipulation, embodied-reasoning]
date_updated: "2026-08-05"
year_range: 2022-2026
papers_analyzed: 91
keywords: [vla, vision-language-action, robot policy]
domain_map: EmbodiedAI
---

## Overview

VLA 把预训练 VLM 扩展为端到端机器人策略，将 internet-scale 的视觉-语言知识迁移到连续高频的 motor control，目标是替代 task-specific 手工设计、走向通用 embodied agent。

**领域活跃度（2024-2026）**：

- **时间线**：[[2212-RT1|RT-1]] (2022) 奠定 AR 范式 → [[2307-RT2|RT-2]] (2023) 注入 web VLM → [[2410-Pi0|π0]] (2024) flow matching 跨 50 Hz → [[2504-Pi05|π0.5]] (2025) 家庭长程 → [[2511-PiStar06|π*0.6]] (2025-11) real-world RL → [[2604-Pi07|π0.7]] / [[2604-GEN1|GEN-1]] (2026Q1-Q2) 宣称跨越商业阈值，仅三年从概念验证走到 deployment 讨论。
- **参与格局**：工业方向 Physical Intelligence（π 系列）/ Generalist AI（GEN 系列）/ Google DeepMind（Gemini Robotics）/ NVIDIA（GR00T / DreamZero）/ Figure AI（Helix）/ AgiBot（[[2512-GenieReasoner|GenieReasoner]]）/ Xiaomi（[[2602-XiaomiRobotics0|Xiaomi-Robotics-0]]）/ Dexmal·StepFun（[[2602-DM0|DM0]]）；开源方向 [[2406-OpenVLA|OpenVLA]] / [[2506-SmolVLA|SmolVLA]] / [[2510-XVLA|X-VLA]] / LeRobot 生态持续跟进。
- **学术产出**：2025H2-2026H1 主要会议（NeurIPS / ICLR / ICRA 2026）VLA 论文密度激增，arXiv VLA survey 8+ 篇；本笔记覆盖 80 篇核心 + 4 篇 survey（[[2507-VLATokenizationSurvey]]、[[2509-PureVLA]]、[[2510-EfficientVLASurvey]]、[[2405-VLASurvey]]——广义三层 taxonomy（components / control policy / task planner）的 TNNLS 正式版，适合作领域入口，但模块划分轴与 action interface 离散/连续、data regime、control frequency 等真正决定能力的轴脱节）。

**整体趋势**：

1. **Action representation 从 discrete 到 continuous**：RT-2 token（3 Hz）→ Octo diffusion → π0 flow matching（50 Hz chunk-level），continuous path 已是默认；离散路线退守到"辅助监督"角色（[[2504-Pi05]] FAST + flow 双头、[[2512-GenieReasoner]] FACT = VQ + flow decoder）。
2. **Dual-system 成 industry default**：System 2 VLM 1-10 Hz + System 1 action 20-200 Hz 的分层解耦被 π0.5 / GR00T N1 / Gemini Robotics / Helix / NaVILA 同时采纳；hierarchical with language intermediate 的历史包袱（语义表达力不足）由 latent action / reasoning trace / 2D trajectory 等替代中间表征消化。
3. **Data recipe > model size**：[[2506-SmolVLA|SmolVLA]] 0.45B、[[2510-XVLA|X-VLA]] 0.9B、[[2602-DM0|DM0]] 2B 反复在主流 benchmark 击败 3-7B baseline；[[2511-GEN0|GEN-0]] 虽然在 7B 观察到"intelligence threshold"相变，但跨越阈值后 data scaling 的 ROI 远大于继续扩参；[[2607-XiaomiRobotics1|Xiaomi-Robotics-1]] 固定 20K hr 数据时 2.6B/5.1B/10.5B 仅 61/75/79%，而 data scaling 把 unseen-env 成功率从 26% 拉到 75%——data 是当前更强 bottleneck 的第二条独立证据。
4. **Real-world RL 和 data engine 改写 ceiling**：[[2511-PiStar06|π*0.6]] 的 advantage conditioning + HIL rollout 首次让 4B 级 flow matching VLA 真实自改进；[[2602-GigaBrain05M|GigaBrain-0.5M*]] 的 RAMP 把它推广到"latent-conditioned"；[[2511-GEN0|GEN-0]] / [[2604-GEN1|GEN-1]] 的 500K 小时 wearable 数据路线让"数据天花板"从学术共识变成工业实验室专属筹码。[[Papers/2607-HiFiUMI|HiFi-UMI]] 则显示，足够高的 pose / relative-geometry / synchronization / FoV fidelity 可让 robot-free UMI 直接承担 target-task post-training，而不只是预训练素材。
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
  - **精度-token-length 冲突**：uniform binning 精度 vs token 数线性 trade-off；[[2604-DAERT|DAERT]] 展示 VLA 对**语言层面微小 rephrase** 的脆弱性（π0 LIBERO 93%→5.85%）。归因到"离散 token 对 prompt shortcut 敏感"这一点在 2026-08 被削弱：[[2608-GSRParaVLA|GSR-ParaVLA]] 的因果干预显示 flow-matching（SmolVLA、π0.5）与 bridge-attention 融合式（VLA-Adapter）路线同样中招，脆弱点在语言特征进入动作策略的融合位置而非 action token 形态（见下文「横切议题一」）。

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
- **2026-08 增量（未来该用什么表示 + world model 移到 critic 侧）**：这条路线在 2026-08 分出两个此前没有的子问题。其一是**被预测的未来该用什么表示**：[[2607-STWAM|ST-WAM]] 观察到只在 VAE latent 空间监督未来的 WAM 在视觉分布偏移下会把预测未来"拉回"训练域外观，于是让 VAE future、DINOv3 future、action 三个 DiT 组成 Mixture-of-Transformers 联合 flow matching（DSFE），并用 Qwen3-VL 的当前多模态 hidden state 作 query 从近 4 帧 DINO history 检索意图 token 注入 action expert（CAIR）；推理时两条 future 分支被 attention mask 整体切掉，退化为 action-only policy，代价是 32 步 chunk 756.17 ms 对 Fast-WAM 609.30 ms（1.24×）。零样本 LIBERO-Plus 72.8% 对 Fast-WAM 51.5%（七个扰动维度全面提升，camera / sensor-noise 各 +39.0 / +41.8），真机 Agilex Piper 四类视觉偏移平均 61.5% 对 Fast-WAM 25.8% / π0 32.8%，compound 偏移 48.0 对 15.3。但它的消融同时给出一个负结果：只用 DINO 未来在 LIBERO-Plus 只有 39.7%，**低于纯 VAE 的 Fast-WAM 51.5%**——语义未来与像素未来是互补而非可换，"换个更鲁棒的表示去预测"这条捷径不成立。可比性边界：LIBERO-Plus 的 baseline 数字明确引自第三方 robustness study 而非本文重跑，LIBERO / RoboTwin 两表则未交代 baseline 来源；真机组是唯一能确认同示教同流程的对照。其二是**world model 从 actor 侧移到 critic 侧**：[[2607-WCM|WCM]] 把 LeJEPA 轻量骨架接成 critic，共享 trunk 同时回归 return 与预测下一帧 latent（$\mathcal{L}_{\text{value}} + \lambda\mathcal{L}_{\text{pred}} + \eta\mathcal{L}_{\text{SIGReg}}$），可直接替换 PPO / Flow-SDE / AWR / RECAP 里的 critic；LIBERO-Plus 上从 one-shot SFT 起跑约 250 步 RL 即超过 20k 轨迹的 Full-SFT（π0 72.8 vs 71.2、π0.5 73.7 vs 72.9、OpenVLA-OFT 74.0 vs 71.7），WidowX-250S 7 个真机任务全面优于 AWR / RECAP，长程 stovetop cleaning 从 1/50 提到 15/50（OpenVLA-OFT）、4/50 提到 33/50（π0.5）。其最有信息量的实验是把 critic 换成 2-5 帧历史 ViT（论文明确定义为 $\lambda=0$ 特例）仍然无效——缺的是**预测性目标**而不是时序输入。
- **优势**：
  - 突破 BC 天花板（π\*0.6 throughput 2× 不靠增量 demo）。
  - World model latent 提供 dense supervision，缓解 sparse reward。
  - 数据路线：wearable / synthetic 绕开 teleop 瓶颈。
- **痛点**：
  - **推理成本**：DreamZero 默认 5.7s/chunk，要 2× GB200 才 7 Hz；WAM 的 long-horizon drift (>200 帧) 至今未解。
  - **Reward hacking**：world model 的盲区被 policy exploit（[[2602-WorldVLALoop]] Fig 5 展示 policy 学会抓杯子背面），要 iterative close loop 才能稳住。
  - **数据壁垒**：GEN-0/1 完全 proprietary，500K 小时 wearable 数据 + 数据采集方法论不公开。学术社区系统性落后于工业实验室。

### 对照组：不含 VLM 的 V+L→A 基线

上述八条路线共享同一个前提——action policy 应当长在预训练 VLM 之上。[[2607-TurboVLA|TurboVLA]] 给了这个前提一次对照实验：执行路径上完全没有 LLM，DINOv3 编码图像、BERT 编码指令、6 层双向 cross-attention 做融合（权重初始化自 Grounding DINO，语言-视觉对齐先验来自 grounding 预训练而非 VLM），ACT decoder 出 action chunk。LIBERO 4-suite 平均 97.7%（0.2B / 0.9GB / 31.2ms，32 Hz），RoboTwin 2.0 Randomized 60.2%（0.4B / 43.4ms，≈23 Hz），真机 AgileX Piper 四任务 92.5 / 80 / 90 / 87.5%。

按上表口径，它在 LIBERO 上与 [[2510-XVLA|X-VLA]]（0.9B，98.1）、[[2602-XiaomiRobotics0|Xiaomi-Robotics-0]]（4.7B，98.7）同处噪声带，参数少一到一个半数量级、延迟低到可裸机 32 Hz 闭环。这有两种读法，而论文自己的 ablation 支持后一种：把语言指令整体替换成 task-ID embedding，LIBERO 只掉 2.3pp（97.7→95.4）。该 benchmark 的语言条件因此接近闭集任务索引，VLM 语义先验在其上本就无处发力，"去掉 VLM 不掉点"主要是 benchmark 的性质而非 VLM 无用的证据。RoboTwin 2.0 上 60.2% 与 WAM 系 92-94% 的差距也指向同一方向——脱离闭集短程设定后差异重新出现。

被这篇论文改变的不是路线排序，而是举证责任：任何"VLM 先验带来泛化"的主张，此后应当配一个语言鉴别力已被验证的评测，或至少一个同规模无 VLM 基线。TurboVLA 自身同样受此约束——全文没有 OOD、指令改写或未见物体实验，因而也不能宣称轻量架构可泛化；延迟数字未声明分辨率、数值精度与编译设置，LIBERO-Long 94.2% 在其对比表中仅第 6，无 seed 与误差棒，表中 "Emb. PT ✗" 指未做具身预训练而非从零训练。

### 横切议题一：语言鲁棒性是架构内的信息路由问题（2026-08 新增）

[[2604-DAERT|DAERT]] 把"只改写指令即崩"记录成现象（π0 LIBERO 93%→5.85%）之后，缺的是位置与机制。[[2608-GSRParaVLA|GSR-ParaVLA]] 给出两层诊断：一是**语义没丢**——行为探针在 10 个候选任务里做 Retrieval@1，π0.5 0.941、VLA-Adapter 0.675、SmolVLA 0.516，全部远超 0.1 的随机水平，语言主干仍然能把改写句归到正确任务；二是**路由坏了**——只替换进入 VLA-Adapter 最后一个 Bridge-Attention block 的语言特征、其余全部保持改写状态，消除 96.8% 的动作差异，配对成功率 60%→96%。两个独立方向的对照支持同一读法：把图像换成 dummy 图使 Full Para 从 46.82 升到 61.58（配对 +14.76，换成固定自然图像只有 +7.17），说明失效来自动作策略对 joint V-L 编码漂移的敏感；沿估计出的 32 个"措辞方向"做子空间移除把 action gap 从 0.4361 压到 0.2282（同范数随机方向 0.4386，几乎无效），闭环 55%→90%。

对应的修法（GSR）只有三步：让不看图像与状态的冻结 T5-large 承担任务语义，投影进各架构**原生的**融合位置，动作专家从头重初始化；训练只用 canonical 指令，不喂任何改写数据。Full Para 上 SmolVLA 4.47→49.12、VLA-Adapter 46.82→70.94、π0.5 73.60→75.59；PRIDE 分别为 2.6→41.4、36.7→62.0、–→70.4。"增益来自容量"被三个对照排除：三种"加可训练参数但不引入独立语言源"的变体全部落在同一个 46.82，Native 直接加 T5 也只有 47.31。

两处负结果比主表更重要。**注入位置不可移植**：在 SmolVLA 上照搬 VLA-Adapter 式的后端 sidecar，canonical 有 76% 但改写只剩 13.49%，注入到 SmolVLM 原生语言位置才得到 49.12；逐层扫描下 VLA-Adapter 的最后一个 Bridge-Attention block 能恢复 96.8% 的动作差异，SmolVLA 与 π0.5 的最佳单层只有 10.5% 与 31.3%，附录 D.3 预注册了三条判定"通用语义断点"的标准并明确声明**没有模型同时满足**——跨架构统一的语义接口目前不存在。**语义源必须与视觉编码解耦**：作者自己的 ParaVLA（0.33B active，冻结 T5 按任务缓存 + 共享 DINOv2-Large，融合只发生在 8×16-head flow-matching 动作专家内部）在 LIBERO-Goal canonical 92.0 / paraphrase 91.0、Full Para 72.51、PRIDE 66.9；同一架构把 T5 换成 SmolVLM decoder 后 canonical 尚有 85.0，paraphrase 塌到 41.0。

这条结果同时补上了上一节 [[2607-TurboVLA|TurboVLA]] 缺失的数据点：ParaVLA 是"执行路径不含 VLM"的第二个实例，且它有改写泛化证据——**去掉 VLM 未必损失语言鲁棒性，决定性变量是语义源是否与视觉编码耦合**。反过来，两篇论文也共享同一个测量学天花板：GSR 的全部仿真证据来自 LIBERO-Goal 的 10 个任务共享同一视觉场景，一个改写不变的句子编码器与一个 10 路任务码在此设定下功能上分不开，这与 TurboVLA 把指令换成 task-ID 只掉 2.3pp 是同一问题的两面。其余边界：附录 A.5 声明了 exact 双侧 McNemar 与任务分层 bootstrap 95% CI，但正文 23 页没有出现任何 p 值、置信区间、标准差或误差棒，每个配置单一固定 seed；除 π0.5 外没有把"动作专家重初始化"与"T5 注入"分开的消融，而 π0.5 恰是增益最弱的一档（+1.99）；真机 AgileX PiPER 每条路线 30 trial（6 任务 × 5 trial × 2 条件），Native 全部 0%、GSR 50% / 40%，其中 3 个任务在两种条件下都是 0%，且"OOD"改写是词汇级替换（pick up→grasp），有一个任务只调换语序。榜单意义上 [[2602-XiaomiRobotics0|Xiaomi-Robotics-0]] 报告的 Full Para 76.0 仍高于 GSR 最好的 75.59，PRIDE 69.2 与 70.4 同档——LIBERO-Para 的第一名并未易主，本文的价值在机制而非 SOTA。

### 横切议题二：触觉作为输入与预测通道（2026-08 新增）

触觉此前不在本综述的八条路线里，2026-08 有两篇同团队工作把它推成一条独立建模轴，但它们的证据互相冲突，因此这里记为**争议**而非新路线。

[[2607-N0VTLA|N0-VTLA]] 的做法是把触觉从"多一路观测"改成**预测目标**：冻结 DINOv2 编码 contact-difference 图像，轻量 predictor 连同 vision-language 上下文压成 10 个 latent tactile token，用来估计未来 H=50 步 action chunk 内的净接触变化，直接条件化 flow-matching 动作专家，触觉全程不进 VL prefix；Stage 2 屏蔽 VL prefix 迫使动作损失只能经这些 token 下降。结果为 9 个真机任务均值 47.2 对 [[2504-Pi05|π0.5]] 29.4、20 任务仿真 63.8 对 44.0、第三方 UniVTAC 83.1 对 InternVLA-A1 67.1，latent token 在约 32 个候选池里 top-1 92.3（对照组 57）。姊妹作 [[2607-N0TWAM|N0-TWAM]] 把触觉做成世界模型的一路专家，其消融却显示去掉**反应式**（observed）触觉通路比去掉**预测式**（predicted）通路损失更大（UniVTAC 70.5 vs 71.8、NeoSim 29.6 vs 41.1），而最大单因素是预训练数据量（降到 20% 掉 19.1 分）。"把触觉做成预测目标"这一核心主张因此在库内没有一致证据。

同一篇论文里更值得本综述记的是 **ALTER** ——一个不需要额外环境交互的 advantage-conditioned 离线 RL 配方，把 stage-relative progress 与轨迹事件的比较转成二值 advantage 标签，progress model 只吃多相机 RGB 与 prompt，触觉/运动学/事件信号只用于离线构造目标。它与 [[2511-PiStar06|π*0.6]] 的 advantage conditioning 同族，替换掉的是"advantage 标签从哪来"。三个长时程真机任务横着读：π0.5-SFT 40/20/5 → π0.5+ALTER 90/75/60（+50/+55/+55），换成触觉 backbone 只有 50/35/20（+10/+15/+15），且 π0.5+ALTER 全面超过 N0-VTLA-SFT。**在这三个可形变物体任务上离线 RL 是主导项、触觉预训练是二阶项**，而形变物体恰恰是触觉最该发挥作用的一类。

证据独立性的硬边界必须同时记：两篇同团队，NeoData / NeoSim / NeoReal / NeoForce 均出自公司网页报告、一手出处不可独立核查，八个基准中仅 UniVTAC 为第三方，且 N0-VTLA 在 UniVTAC 的 8 个任务里输掉 3 个（Insert HDMI 25，对照 Xiaomi-Robotics-0 的 69）；真机每任务 20 trial（分辨率 ±11%），无 seed 与方差，也没有同一 checkpoint 关掉触觉的对照。

### 横切议题三：proprioceptive state 的接口与历史深度（2026-08 新增）

八条路线按 action 表示组织，而"机器人自身的 state 怎么进模型"横跨全部路线，且长期由惯例而非证据决定——[[2504-Pi05|π0.5]] 把 state 量化成文本 token 拼进 prompt，[[2502-OpenVLA-OFT|OpenVLA-OFT]] 连续投影进语言序列，[[2503-GR00TN1|GR00T N1]] 直接喂 action head，三者从未在同一 backbone 下被单独比较。[[2608-VLAProprioception]] 把这个接线选择拆成表示形式、历史长度、注入位置三条可测量的轴，固定 π0.5 基座、数据、action 表示与评测协议，用同一 scaffold 实现五种接口在 RoboCasa365 上闭环对比（45 个 atomic 任务按控制语义事前分三族、各训一个 category expert、每任务 50 次 rollout；20 个 composite 任务单策略联合训练、每任务 25 次 rollout）。

| 接口 | 注入位置 | 新增可训练参数 | 训练 / 推理边际 GFLOPs | 单帧 45-atomic macro SR |
|:--|:--|:--|:--|:--|
| no-state | — | — | — | 54.6 |
| State Prompt (sp) | VLM prompt（每维 256 bin，约 66 token；构造上只支持当前帧） | 0 | 1114 / 282 | **57.7**（+3.1，唯一区间排除 0：[0.2, 6.1]） |
| VLM Prefix (vp) | VLM 双向 prefix | 4.26M | 16.9 / 4.3 | 56.8 |
| Action Prefix (ap) | action expert 因果后缀 | 1.08M | 3.5 / 7.6 | 55.7 |
| State Expert (se) | 独立 transformer 分支 | 199.30M | 2.6 / 0.7 | 55.7–57.7 带内 |
| Feature Modulation (fm) | action expert 每层 scale / shift 调制 | 123.84M | 45.4 / 114 | 55.7–57.7 带内 |

**当前帧 state 的平均收益很小，接口选择在平均意义上几乎无关紧要。** 五个接口的点估计全部挤在 55.7–57.7 这两个点的带子里，只有 sp 的配对 task-bootstrap 区间排除 0，其余四个只能读作一致的正向倾向。真正的信息在族内排名的翻转：rearrangement / pick-and-place 一族 sp 最优（68.7，+7.0），articulated-object 一族 vp 反超（68.8，+6.1），小工作空间高精度一族 se 领先（42.8，+3.3）且 vp 是唯一低于 baseline 的接口（38.3，−1.2）。一个 benchmark-wide 平均会把这套结构完全抹掉。算力代价则相差两个数量级——sp 的 66 个 prompt token 是最贵的设计，而 se / fm 用近乎可忽略的边际算力拿到同档点估计。

**短历史有界有益、长 raw 历史有害，且收益不能用 conditioning 容量解释。** K 从 1 扫到 96 呈明显非单调，小工作空间高精度一族在长历史下退化最重、经 VLM prefix 注入时尤甚。关键排除项是 slot-matched 对照：固定图像、语言、slot 数、expert action 与初始 flow noise，只把有序历史换成当前帧的副本，composite 从 39.0 掉到 30.8，差 +8.2 且配对区间排除 0——多出来的 conditioning slot 本身不产生收益，起作用的是时序内容。

**注入位置的偏好随时间预算翻转。** 单帧时 VLM 侧占优（composite vp1 34.4 对 ap1 28.2）；给到 8 帧历史后决定性地转向 action 侧——ap 在 composite 上 28.2→39.0（+10.8）、atomic 上 55.7→59.6（+3.9），同样的历史走 vp 只有 −0.6 与 +0.6，K=8 时 ap 在每个 panel 都是最佳入口，而它在单帧时接近最弱。定点 probe 与这个读法一致：ap1→ap8 使 flow 末端 correction 与 expert residual 的对齐从 0.079 升到 0.270、归一化幅度 0.174→0.382（45 任务配对差 +0.191 / +0.208，区间 [+0.143,+0.239] / [+0.171,+0.244]），PrepareToast 的增益集中在"回身关柜"这一后期阶段切换（该阶段达成率 30%→56%，配对区间 [+10,+42]；条件于进入前一阶段后 46.9%→82.4%），作者声明这是使用模式的关联证据而非 mediation。

这条结果与「横切议题一」构成同一个模式：**conditioning 进入网络的位置本身是一等设计变量，而它的最优解依赖其余设计，没有可移植的默认值**。语言语义的注入点在三种架构之间不可移植，state 的注入点则在同一架构内随历史长度翻转；两者都说明"接在哪里"不能从别人的配置里抄。

边界需一并记住。+10.8 是从 ap1 28.2 这个几乎无收益的起点量起的，跨设计的诚实比较是 ap8 的 39.0 对最好的单帧设计 vp1 的 34.4，即 +4.6，方向不变但幅度减半。换成 joint-angle state 后短历史的方向复现，但 K=8 时两条路线收敛（ap 36.2 对 vp 35.8，落在配对 bootstrap 噪声带内），路由规则的强度依赖 state 用的是哪套坐标。16 维 state 里有 7 维是 world frame 下的 mobile-base 位姿，作者自己点明这不能读作纯粹的内部本体感受，而 sp 增益最大的恰是大范围重定位一族——"把全局定位离散化塞进语言空间"是一条未被消融排除的替代解释。此外 se / fm 因硬件分配训练曝光偏低（作者据此声明不做 capacity-matched claim），多数对比依赖单一训练 seed，interface × depth 的 sweep 属探索性且未做多重比较校正，全部实验在仿真中完成、state 纯 kinematic 不含 force / tactile。以上数字经原文一致性核查，尚无独立复现。

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
5. **Real-world RL 范式转变**：π\*0.6 的 advantage conditioning 是"绕开 flow matching PPO 难题"的工程胜利，被 RAMP / WorldVLALoop 沿用，2026-08 又添两个变体——[[2607-N0VTLA|ALTER]] 换掉"advantage 标签从哪来"（轨迹事件 + stage-relative progress 的离线构造，零额外环境交互），[[2607-WCM|WCM]] 换掉 critic 本身（预测性表征而非更长历史）；RL 的瓶颈正从"算法"移到"世界模型保真度 + reward 引擎"。
6. **Reasoning-action 从 shallow CoT 走向 unified discrete framework**（GenieReasoner FACT / Lumo-1 spatial action tokenizer / RoboBrain 2.5 3D+temporal）；"在 action space 做 reasoning" 的激进方向仍无实证。
7. **Memory 成为 long-horizon 明确子问题**：[[2603-MEM|MEM]]（video encoder + language memory，15min 任务）、[[2511-EchoVLA]]（dual PHC+hippocampus memory）、[[2507-StreamVLN]]（streaming KV-cache + voxel pruning）都在 2025-2026 集中出现；[[2607-LaMemVLA|LaMem-VLA]] 进一步把记忆从 policy-side 外挂挪进模型 native embedding 空间（短期视觉/长期动作双 vault，latent-native 相对 policy-side 条件化 +2pp）。
8. **Deployment 工程栈成熟**：async inference（SmolVLA）、RTC（π0.7）、1-step flow matching（SnapFlow 274→83ms）、int4 量化（OpenVLA）、Λ-mask 防 shortcut（Xiaomi-Robotics-0）、paged attention（GEN-1）——"VLA 推理延迟是核心瓶颈"的共识正在推动专用优化技术涌现。
9. **执行期监控与恢复独立成层（2026-07 新 pattern）**：失败常源于"执行中途坏掉且回不来"而非"不会做"，恢复机制可与策略学习解耦。[[2606-RehearseVLA|RehearseVLA]] 的 instant reflector 暴露 VLA 评测对 oracle 终止信号的隐性依赖（禁用后 OpenVLA-OFT 掉 11.8pp）；[[2607-RobustExecAgenticRL]] 在冻结 VLA 上用 PPO 训 {Execute/Retry/Repair/Reset} 调度层、以回滚历史 nominal state 恢复执行（扰动设定 LIBERO-Long 平均 +39.2pp，但缺规则阈值 baseline、扰动类型为方法量身定做）；与 venue 回填的 [[2606-AffordanceFieldInterventio]] test-time rollback 同线。
10. **下游适配配方成为受控研究对象**：[[2607-LoRAVLA]] 给出 π0 工业微调的实证 recipe——LoRA r=32 + SigLIP 全量微调持平 FFT（VRAM 36.2→10.8 GiB），embodiment adaptation 的瓶颈在视觉 domain shift 而非动作层；[[2607-DART]] 把适配数据的价值从"重学任务"改写为"测量 domain direction"——source/target one-shot update vector 相减 + SVD subspace 过滤，一条 target demo 把 domain shift 迁移到全部任务（LIBERO viewpoint shift 79.1% vs one-shot FT 31.5%，真机 UR10e 81.7%）。
11. **UMI 从 pre-training 进入 target-task post-training，但 data equivalence 尚未成立**：[[Papers/2607-HiFiUMI|HiFi-UMI]] 在 StarVLA-QwenPI、OpenPI-π0.5、LingBot-VA 三种 backbone 上报告 UMI−teleoperation aggregate gap −2.5 / +3.1 / −0.6pp，证明整套高保真采集系统足以形成可部署 policy；然而每任务 3,200 条 UMI 对约 300 条 teleoperation，且 evaluation-scene exposure 不同，因此不能把 pipeline parity 解释为 equal-sample parity。
12. **"多预测一路未来 / 多接一路感知"的收益归因开始被自家消融反噬（2026-08 新 pattern）**：三篇彼此独立的工作给出同向负信号——[[2607-STWAM]] 的 DINO-only 未来分支在 LIBERO-Plus 只有 39.7%，**低于**纯 VAE 的 Fast-WAM 51.5%；[[2607-N0TWAM]] 去掉反应式触觉通路比去掉预测式通路损失更大，且最大单因素是预训练数据量而非任一触觉通路；[[2607-WCM]] 用 $\lambda=0$ 的历史 ViT 对照证明了"预测目标有用"，却全文没有任何 value 估计精度指标，无法排除"预测 loss 只是防表征塌缩的正则化"这条同样兼容的解释。三者的缺口是同一个：缺同 backbone、同算力、逐目标移除的对照。在补上之前，"新增预测通道 → 表征更好 → 动作更好"这条因果链在库内只有相关性证据。[[2608-VLAProprioception]] 给出这类对照的一个可搬运样板，并且同时落在天平两侧：固定 backbone / 数据 / 协议只动 state 接口，当前帧这一路"多接一路感知"在 45 个任务上五个接口只有一个区间排除 0（54.6 → 55.7–57.7）；但换成 8 帧有序历史后，相对"用当前帧副本填满同样 slot 数"的对照仍有 +8.2 且区间排除 0。通道有没有用要按其承载的内容判，而不是按"多了一路"判。

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
| HiFi-UMI / HiFi-UMI-2K | 2026 | full 20K+ hr / 4.32M+ episodes；released 2K hr / 482.1K+ episodes | UMI handheld → stationary bimanual robot | [[2607-HiFiUMI\|HiFi-UMI]] | CC BY 4.0；3 mm pose、<40 μs 同步、six-view；三 backbone 验证 target-task UMI-only post-training，但非 sample-matched |

### Manipulation sim benchmarks

| Benchmark                    | 规模 / 定位                 | Metric             | SOTA (2026-08)                                                                                                                                        |
| ---------------------------- | ----------------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| LIBERO                       | 4 suite × 10 task 短程    | 4-suite avg SR     | **99.4%** ([[2607-ABotM05\|ABot-M0.5]], WAM) <br>98.7% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]] 4.7B) <br>98.2% (EO-1) <br>98.1% ([[2510-XVLA\|X-VLA]] 0.9B)                                   |
| LIBERO-Long                  | 长程子集                    | SR                 | 97.6% ([[2512-Motus\|Motus]] / [[2510-XVLA\|X-VLA]] 并列) <br>97.2% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                       |
| LIBERO-Plus                  | 7 类扰动的鲁棒性套件（视觉/语言/布局/传感器噪声等） | overall SR | 零样本：**72.8%** ([[2607-STWAM\|ST-WAM]]，对照 Fast-WAM 51.5——baseline 引自第三方 robustness study 而非本文重跑) <br>RL 微调设定（one-shot SFT + ~250 步）：74.0 / 73.7 / 72.8 ([[2607-WCM\|WCM]] on OpenVLA-OFT / π0.5 / π0，对照各自 20k 轨迹 Full-SFT 71.7 / 72.9 / 71.2)。两组设定不同，不可直接横比 |
| LIBERO-Para                  | LIBERO-Goal 的指令改写集：4,092 条改写 episode（870 Act / 259 Obj / 2,963 Comp） | Full Para SR / PRIDE | Full Para **76.0** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]]) <br>75.59 / PRIDE **70.4** ([[2608-GSRParaVLA\|GSR]]-π0.5) <br>70.94 / 62.0 (GSR-VLA-Adapter，Native 46.82 / 36.7) <br>49.12 / 41.4 (GSR-SmolVLA，Native 4.47 / 2.6) |
| UniVTAC                      | 第三方视触觉操作基准（8 任务）      | avg SR             | **84.5** ([[2607-N0TWAM\|N0-TWAM]]) <br>83.1 ([[2607-N0VTLA\|N0-VTLA]]，8 任务中输掉 3 项) <br>67.1 (InternVLA-A1) |
| CALVIN ABCD→D                | In-dist 长程              | Avg task length /5 | **4.80** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                                                                                |
| CALVIN ABC→D                 | OOD 长程                  | Avg task length /5 | **4.75** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]], vs 次优 FLOWER 4.53)                                                                             |
| SimplerEnv Google Robot VM   | Real-to-sim             | avg SR             | **85.5%** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]]) <br>80.4% ([[2510-XVLA\|X-VLA]])                                                              |
| SimplerEnv Google Robot VA   | Real-to-sim             | avg SR             | 75.7% ([[2510-XVLA\|X-VLA]]) <br>74.7% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                                                  |
| SimplerEnv WidowX            | Real-to-sim             | avg SR             | **95.8%** ([[2510-XVLA\|X-VLA]], vs 前 SOTA MemoryVLA 71.9) <br>79.2% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                    |
| RoboCasa Kitchen Easy / Hard | 100 photorealistic 厨房任务 | SR                 | 70.0 / 39.0 ([[2510-XVLA\|X-VLA]])                                                                                                                    |
| RoboCasa365                  | 365-task 移动操作 pretraining 设置 | avg SR      | **57.4%** ([[2607-XiaomiRobotics1\|Xiaomi-Robotics-1]], Composite-Unseen 32.1%) <br>46.6% ([[2607-ABotM05\|ABot-M0.5]] +Condensed Memory, Composite-Unseen 7.9%) <br>*另一套口径*：[[2608-VLAProprioception]] 用 45 个 atomic（分三族各训 category expert）+ 20 个 composite 子集，macro 57.7% / 39.0%，与上两行的 365-task 联合训练设置不可横比 |
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
- **HiFi-UMI full / released corpus = 20K+ / 2K 小时**（[[2607-HiFiUMI]]）——4,000-hour pre-training 在 StarVLA-QwenPI 上使 10 个 unseen tasks 的 mean OOD action error −41%，并在相同 task-specific data 下把 real-robot success +18.1pp；后者只在一个 backbone 上验证。
- **[[2604-BiCoord\|BiCoord]] STI = 42.16% vs RoboTwin 2.0 / RLBench2 ~8–11%**——首次用标量同时刻画"空间近 + 时间并行"，暴露现有 bimanual benchmark 的伪协同（RLBench2 SMP 97% 但 ARD 115%——并行 ≠ 协同）。

### Benchmark 饱和度与评测 crisis

- **LIBERO 已近饱和**：4-suite avg 98.7 / 98.2 / 98.1 差距在噪声量级；long-horizon sub-suite 仍可分辨（[[2602-XiaomiRobotics0\|Xiaomi]] 97.2 vs 次优 FLOWER 94.9）。
- **LIBERO 的语言鉴别力不足（比饱和更严重）**：[[2607-TurboVLA]] 把语言指令替换为 task-ID embedding 后仅掉 2.3pp（97.7→95.4），说明该 benchmark 主要测闭集任务执行而非指令理解。凡是把收益归于语言/语义先验的方法（VLM backbone、reasoning trace、language intermediate），在 LIBERO 上的提升都不构成对该归因的支持；[[2604-DAERT]] 的 "no action" probe（π0.5 仍 54.9% 成功）与之互补——一个说语言可被无损替代，一个说语言可被直接忽略。2026-08 补上第三个方向与一条廉价补救：LIBERO-Para 只把 canonical 模板改写成同义表述（不换物体、不换场景、不换动作），就把同一批模型从 72-98% 打回 4-77%（[[2608-GSRParaVLA]]）——**鉴别力不是消失，而是被 canonical 模板掩盖**，恢复它的代价是 4,092 条改写指令而非新建环境。该协议自身的边界也随之明确：LIBERO-Goal 的 10 个任务共享同一视觉场景，改写不变的句子编码器与 10 路任务码在其上仍然分不开，因此它能证伪"语言被用到了"，不能证实"语言被理解了"。
- **鲁棒性榜单的 baseline 多为引用而非重跑**：[[2607-STWAM]] 的 LIBERO-Plus 表明确标注 baseline 数字引自第三方 robustness study，其 LIBERO / RoboTwin 两表则完全未交代 baseline 来源；这类跨表混用使"同 backbone / 同数据量"无法从原文确认。鲁棒性子集正在成为新的比较战场（LIBERO-Plus / LIBERO-Para），若沿用主表的引用习惯，饱和 benchmark 的可比性问题会原样复制到它们身上。
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
- **Fidelity 与 quantity 如何解耦？** [[2607-HiFiUMI]] 的 joint system 在三 backbone 上接近 teleoperation pipeline，但 parity 条件使用 3,200 UMI vs ~300 teleoperation trajectories；只有 Remote Insertion 报告 400→6,400 条的 UMI scaling curve，且约在 3,200 条 plateau。需要等样本、等场景暴露实验，才能区分“高保真使单条 demonstration 更有效”与“高保真允许用数量弥补 embodiment gap”。

### 2. Real-world RL for large VLAs

[[2511-PiStar06]] 的 Recap 首次在 4B+ flow matching VLA 上跑通真实 RL 自改进；[[2602-GigaBrain05M]] 把它形式化为 RAMP 的特例并加 future visual latent；[[2602-WorldVLALoop]] 用 closed-loop world model 迭代。仍未解：
- 只覆盖 episode-level sparse reward；dense / preference-based reward 未系统探索。
- **可 RL 修复 vs 结构性 failure**（hardware / perception bug）未区分。
- 与 Upside-Down RL / Decision Transformer / CFGRL 的理论联系尚不完整。
- RL 的 compute scaling 和 improvement 曲线不清楚（π\*0.6 只跑了 2 轮迭代，box assembly 第 3 轮会饱和还是继续提升？）。
- **2026-08 新增两个可调变量：critic 表征与 advantage 标签来源**。[[2607-WCM]] 把 world modeling 接进 critic 而非 actor，并用 $\lambda=0$ 的历史 ViT 对照把结论收紧到"缺的是预测性目标而非时序输入"（LIBERO-Plus 上 one-shot SFT + ~250 步 RL 即超过 20k 轨迹 Full-SFT，真机长程 stovetop cleaning 1/50→15/50）；[[2607-N0VTLA]] 的 ALTER 用轨迹事件与 stage-relative progress 离线构造二值 advantage，零额外环境交互，把 π0.5 在三个可形变物体长程任务上从 40/20/5 提到 90/75/60。二者都没有回答上述四个问题，而是各带来一个新问题：predictive critic 的收益究竟来自"更准的 value"还是"更难塌缩的表征"（WCM 全文无 value 精度指标，两种解释同样兼容），以及离线 advantage 的质量上限由只吃 RGB 与 prompt 的 progress model 决定，其误差如何传导到 policy 未被测量。
- **注意这两条仍不构成 dense reward**：ALTER 的 progress 是离线标注、WCM 的 latent 预测是辅助监督，都不是环境返回的稠密奖励——"只覆盖 episode-level sparse reward"这一判断在严格意义上未被推翻。

### 3. Cross-embodiment 的正确抽象层

- Per-embodiment action head（π0 / GR00T N1 / RDT）→ input-side soft prompt（X-VLA）→ 统一 latent action（LAPA / UniVLA）的演化线尚未收敛。
- Morphology 巨差（gripper vs dexterous hand / single-arm vs humanoid loco-manipulation）能否共享 backbone？[[2604-Pi07]] UR5e 匹配人类 top-2% 是正面信号但 case-level。
- [[2512-WholeBodyVLA]] 用**双 LAM**（manipulation LAM + locomotion LAM）解耦"camera 静止 vs 移动"的 attention 冲突——提示未来 VLA 可能需要按 motion modality 拆解 latent space。
- OXE-scale（1000+ 数据源）下 per-source soft prompt 是否仍可行未验证；分层 prompt（embodiment-level + setup-level）可能是下一步。

### 4. Reasoning-action unification

现有路线仍是"在语言空间思考 → 产生动作"（ECoT / DriveVLM / Cosmos-Reason1 / GenieReasoner）。[[2507-VLATokenizationSurvey]] 提出的 **action-token-based reasoning**（直接在动作空间做 CoT）暂无实证。[[2508-EmbodiedR1]] Table 6 发现 RL 比 Think 重要得多（Where2Place +20 vs +2.5），暗示当前 CoT 的价值可能主要是 representation shaping 而非 inference-time planning。

### 5. Evaluation / reproducibility 危机

- **Lab tabletop 饱和**：LIBERO 98+ 已在噪声量级，CALVIN ABCD→D 接近上限。
- **语言鉴别力缺失**：LIBERO 上 task-ID embedding 可近乎无损替代自然语言指令（[[2607-TurboVLA]]，−2.3pp），主流短程 suite 因此无法验证任何以语义理解为卖点的设计。需要的最小改动是加入 held-out 指令改写与同义/反义配对，使"语言真的被用到"成为可检验命题。**这条最小改动在 2026-08 被做出来了**：[[2608-GSRParaVLA]] 的 LIBERO-Para 用 4,092 条改写 episode（Act / Obj / Comp 三类）在不动环境的前提下把同批模型从 72-98% 打回 4-77%，鉴别力随之恢复。剩下的缺口是它只解决"改写"这一维：未见物体、未见动作、组合新指令与显式反义配对（要求模型在语义不成立时**拒绝执行**）都还没有对应协议；且 LIBERO-Goal 的 10 个任务共享同一视觉场景，改写不变的句子编码器与 10 路任务码在其上仍分不开。
- **自建 benchmark bias**：RoboBrain 2.5 / RynnBrain / Vlaser / ACE-Brain-0 / Pelican-VL 都在自家 benchmark 上领先——难以横向对比。
- **Metric 口径不齐**：π0 的 50 Hz 是 chunk-level，OpenVLA 的 6 Hz 是 token-level；TL（trajectory length）只算成功 episode 引入 selection bias（[[2604-BiCoord]]）。
- **OOD 定义模糊**：[[2604-Pi07]] 自己承认"训练集太大无法严格定义 unseen"，compositional generalization claim 难证伪。
- **ERIQ / BiCoord / RoboChallenge** 是 2025-2026 的新尝试（reasoning/coordination/real-robot），尚未社区采纳。
- **评测成本的两条候选出路（2026-07）**：world-model-as-evaluator（[[2607-GigaWorld1]]，paired rollout 的 outcome agreement 作为 benchmark 单位）与无 oracle 终止协议（[[2606-RehearseVLA]]）；前者的 contact-sensitive optimistic bias、后者未报告的误终止率是各自短板。[[2606-Act2Answer]] 补充第三类协议——把 VLM 知识 benchmark 改造成"用动作作答"的行为级评测，解耦知识缺失与控制失败。

### 6. Data engine 的工程 vs 学术 gap

[[2511-GEN0]] 270K hr + [[2604-GEN1]] 500K hr wearable + 10K hr/week，全 proprietary + Early Access Partner only；开源社区最大到 OXE / DROID / AgiBot World 百 K episodes 量级。若 scaling law 成立，学术社区将**系统性落后工业实验室**——类似 LLM 2023 后的 Anthropic/OpenAI/DeepMind 局面。更棘手的是 GEN 系列数据采集形态（wearable 传感器组合、action 空间对齐）完全不公开，**复现门槛不是"钱"而是"方法论本身不公开"**。

2026-07 更新：**"方法论黑箱"判断被部分削弱**——[[2607-XiaomiRobotics1]] 公开 UMI handheld gripper + state-transition 自动标注（Qwen3.5-27B captioning）的完整方法论（100K+ hr，数据/checkpoint 承诺后续发布）；[[2607-EgoSteer]] 的 EgoSmith 管线从公开 egocentric 数据集清洗出 9.6K hr 且工程细节可复用；[[2607-TAP]] 证明 30 hr autonomous play 可替代部分 expert 数据预算；[[2607-HiFiUMI]] 进一步开放 2K 小时 CC BY 4.0 子集，并给出 pose、relative geometry、hardware synchronization 与 FoV 的完整 system recipe。非遥操作数据引擎的方法论正在公开化，gap 收敛为“可复用数据本体、算力与经过因果验证的 fidelity specification”；HiFi-UMI 尚未逐项 controlled degradation，仍不知道四项 fidelity 的必要性与边际贡献。

### 7. Memory 与 long-horizon

MEM（video encoder + language memory 解耦，15min 任务）、EchoVLA（PHC+hippocampus 双 memory）、StreamVLN（streaming KV cache + voxel pruning）、Pi0.7（MEM 集成）在 2025H2-2026H1 集中出现。共同开放问题：
- Memory 的**压缩粒度**（token / frame / 语义摘要）跨任务最优策略？
- Explicit voxel 3D memory 在动态遮挡下失灵（EchoVLA OR 任务输给 baseline），explicit vs implicit memory trade-off 未系统化。
- 长于 1 小时的 memory 几乎无工作；GEN-1 "连续 200+ 次无干预"demo 未开放评测协议。
- Latent-native vs policy-side：[[2607-LaMemVLA]] 显示记忆织入 native embedding 空间优于外部条件化（+2pp），但纯仿真、top-K 检索不可微——真机稳健性与可微检索是下一步。
- **原始帧堆叠不是可扩展的记忆（2026-08）**：[[2608-VLAProprioception]] 把 state 历史深度从 1 扫到 96，收益非单调——短历史优于单帧，更深的未压缩历史不再带来收益并最终损害控制，小工作空间高精度任务退化最重且经 VLM prefix 注入时尤甚（K=8 是该论文的经验操作点而非普适最优）。这把压缩式记忆的必要性从工程优化改写成避免退化的前提。但它只测了 raw frame stack，"长 raw 历史有害"不等于"长历史无用"——压缩式历史能否在更大 K 上保住收益，以及长历史退化究竟是 copycat shortcut 还是上下文稀释，都还没有失败模式归因。

### 8. Safety / alignment for embodied intelligence

- **Linguistic fragility**：[[2604-DAERT]] 证明仅改写语言指令即可把 π0 LIBERO 93%→5.85%，且具跨架构迁移性。[[2608-GSRParaVLA]] 把它从攻击面推进到机制与部分修复：语义在语言主干里完好（探针 Retrieval@1 0.516-0.941 对随机 0.1），失效在语言特征进入动作策略的融合点，只替换该处特征即消除 96.8% 的动作差异；把语义源换成不看图像的冻结文本编码器后 SmolVLA 的改写成功率 4.47→49.12。但这是**鲁棒性修复而非安全保证**——GSR 的实验是良性同义改写，没有对抗性改写、诱导性指令或拒绝行为的评测，且注入位置不可跨架构移植（附录 D.3 预注册的三条通用语义断点判据无一模型同时满足）。
- **Emergent improvisation 的 double-edge**：GEN-1 blog 承认 emergent recovery 既是 capability 也是 alignment liability——机器人"自由解释任务"可能造成物理损害。
- **No-action probe**：DAERT 用 "no action" prompt 发现 π0.5 仍 54.9% 成功（退化成 vision-only），揭示当前 VLA 对语言依赖度的 hidden bias。
- 现有 safety 工作（ASIMOV-2.0 / Auto-Red-Teaming / Semantic Action Safety）主要围绕 semantic content，未触及物理 action 的 hazard 层面；Inference-Time Policy Steering 是可能方向。

### 9. 新增预测通道 / 感知通道的收益归因（2026-08 新增）

近一年 VLA 的主流增益手段是"再加一路"——加一路未来预测（WAM）、加一路模态（触觉）、加一路辅助目标（critic 的 latent prediction）。三篇独立工作的自家消融同时显示这条归因并不牢靠：[[2607-STWAM]] 的 DINO-only 未来分支（39.7）低于纯 VAE 基线（51.5），语义未来与像素未来互补而非可换；[[2607-N0TWAM]] 去掉反应式触觉通路比去掉预测式通路损失更大，最大单因素是预训练数据量（−19.1）；[[2607-WCM]] 证明了预测目标有用，却没有任何 value 精度指标可以排除"它只是防表征塌缩的正则化"。

要把这条链从相关性变成因果，缺的实验是共同的，也不昂贵：

- **同 backbone、同算力、逐目标移除**——把新增通道的参数量与训练步数补齐到对照组，再逐个关掉预测目标，而不是整支砍掉（ST-WAM 的 "parameter-matched" 变体方向正确，但原文未给参数量）。[[2608-VLAProprioception]] 的 slot-matched 对照是可直接搬运的样板：固定图像、语言、slot 数、expert action 与初始噪声，只抽掉时间变化，把"时序内容"与"多出来的 conditioning 容量"分开（30.8 对 39.0）。它自身仍留着 state expert / feature modulation 训练曝光不等、多数对比单 seed、sweep 未做多重比较校正的缺口。
- **中间量必须被直接测量**：value 精度（explained variance / TD error）之于 predictive critic，预测未来的保真度之于 WAM，接触事件的预测误差之于触觉——只报下游成功率无法区分"预测更准"与"梯度更稳"。
- **偏移类型要超出外观**：ST-WAM 的增益集中在 LIBERO-Plus 的 camera / sensor-noise 等外观级扰动，而它把机制归给 DINO 的表示不变性；在物理属性、动力学或物体几何偏移上重跑才能检验这条归因。

## 调研日志

### 2026-08-05 survey-refresh 增量并入 1 篇

- **来源**：[[Papers/2608-VLAProprioception|VLAProprioception]]（full-text，source-checked：18 条 evidence-ledger claim 全部 source-verified，正文只引其中的数字与负结果）。
- **结构变化**：技术路线部分新增「横切议题三：proprioceptive state 的接口与历史深度」，与既有两个横切议题并列——state 接口横跨八条路线且在既有分类里无落点；该节同时与横切议题一合并出一条模式（conditioning 的注入位置是一等设计变量，最优解依赖其余设计、无可移植默认）。convergence 观察 12 增补一句：新增通道的收益归因现在有了一个可搬运的对照样板，且同一篇论文在"当前帧 state"上给出弱信号、在"有序历史"上给出经容量对照后仍成立的正信号。Open Problem 7 新增"原始帧堆叠不是可扩展的记忆"，Open Problem 9 的第一条实验缺口补上 slot-matched 对照样板；Benchmarks 的 RoboCasa365 行加注该论文的另一套评测口径不可横比。papers_analyzed 90→91。
- **证据边界**：全部实验在仿真中完成，无真机验证，state 纯 kinematic 不含 force / tactile；五个接口在 45 atomic 上只有 State Prompt 的配对区间排除 0，其余四个只是一致的正向倾向；state expert / feature modulation 训练曝光偏低，作者据此声明不做 capacity-matched claim；多数对比单 seed，interface × depth sweep 未做多重比较校正。16 维 state 含 7 维 world-frame mobile-base 位姿，"把全局定位塞进语言空间"这条替代解释未被消融排除。composite 的 +10.8 起点接近无收益，跨设计的可比幅度是 +4.6。库内单篇证据，无独立复现。
- **domain_map**：[[DomainMaps/EmbodiedAI]]（与同轮 EmbodiedAI-Survey 的格局变化合并写入）。
- **status**：success

### 2026-08-04 survey-refresh 增量并入 5 篇

- **来源**：ledger 4 篇——[[Papers/2608-GSRParaVLA|GSR-ParaVLA]]（full-text，partial：40 条 claim 中 39 source-verified，C32 标 `unsupported` 未采用）、[[Papers/2607-STWAM|ST-WAM]]（full-text，partial：其 entanglement 机制断言标 `unsupported`，正文只引消融数字与负结果）、[[Papers/2607-WCM|WCM]]（full-text，source-checked）、[[Papers/2607-N0VTLA|N0-VTLA]]（full-text，source-checked）；另主动补入 [[Papers/2607-N0TWAM|N0-TWAM]] 作为 N0-VTLA 的反向证据——只记前者会把一条有直接反例的主张写成结论。
- **结构变化**：技术路线部分新增两个横切议题小节（一：语言鲁棒性 = 架构内的信息路由问题；二：触觉作为输入与预测通道，两篇姊妹作的相反消融记为**争议**而非共识），与既有的"对照组：不含 VLM 的 V+L→A 基线"并列；路线 8 新增 2026-08 增量段（WAM 的未来表示之争 + world model 移到 critic 侧）；路线 1 的"离散 token 导致语言脆弱"归因被削弱并标注；convergence 观察 5 增补、新增 12；Benchmarks 表 +LIBERO-Plus / LIBERO-Para / UniVTAC 三行并把 SOTA 列时间标到 2026-08；评测 crisis 的语言鉴别力条目增补 LIBERO-Para、新增"鲁棒性榜单 baseline 多为引用而非重跑"；Open Problem 2 / 5 / 8 增补，新增 Open Problem 9（新增预测/感知通道的收益归因）。papers_analyzed 85→90。未刷新配图（本 survey 无既有配图，本轮为横切小节新增而非八条路线的分类框架重构）。
- **证据边界**：GSR 的全部仿真证据来自 LIBERO-Goal 10 个任务共享同一视觉场景，句子编码器与 10 路任务码尚未分开；附录声明的 McNemar 与 bootstrap CI 全文无一数值，单 seed；除 π0.5 外未把"动作专家重初始化"与"T5 注入"分开；LIBERO-Para 榜首仍是 Xiaomi-Robotics-0（76.0 > 75.59）。ST-WAM 的 LIBERO-Plus baseline 引自第三方 robustness study，LIBERO / RoboTwin 两表未交代 baseline 来源，仅真机组可确认同示教同流程。WCM 无任何 value 估计精度指标，SIGReg 在 on-policy 关闭故仿真主结果里只有 $\mathcal{L}_{\text{pred}}$ 生效，Table 1 的 baseline 行无误差棒而部分增益仅 0.8-1.1。N0-VTLA 与 N0-TWAM 同团队，NeoData / NeoSim / NeoReal / NeoForce 出自公司网页报告不可独立核查，八个基准中仅 UniVTAC 第三方，真机 20 trial/任务无 seed 与方差，且无同 checkpoint 关掉触觉的对照。均为库内单篇（或同团队两篇）证据，无独立复现。
- **domain_map**：[[DomainMaps/EmbodiedAI]]——语言鲁棒性与触觉两条格局变化已由同轮 EmbodiedAI-Survey 写入；本轮另补 WM 进入 RL critic 侧一条。
- **status**：success

### 2026-08-02 survey-refresh 增量并入 1 篇
- **来源**：[[Papers/2607-TurboVLA|TurboVLA]]（full-text，verification_status: partial——仅使用其 evidence ledger 中 source-verified 的行）。
- **结构变化**：技术路线部分新增"对照组：不含 VLM 的 V+L→A 基线"，作为八条路线共同前提（policy 长在预训练 VLM 之上）的对照实验；评测 crisis 与 Open Problem 5 新增"语言鉴别力缺失"条目——LIBERO 上 task-ID embedding 可近乎无损替代自然语言指令，使任何以语义先验为卖点的方法在其上的收益无法被归因。
- **证据边界**：TurboVLA 无 OOD / 指令改写 / 未见物体评测，其结论只在闭集短程分布内成立；延迟数字未声明分辨率、数值精度与编译设置，无 seed 与误差棒；"Emb. PT ✗" 指未做具身预训练，不等于从零训练。RoboTwin 2.0 上 60.2% 与 WAM 系 92-94% 的差距未被论文讨论。
- **domain_map**：[[DomainMaps/EmbodiedAI]]（与同轮 EmbodiedAI-Survey 的格局变化合并写入）。
- **status**：success

### 2026-07-30 survey-refresh 增量并入 1 篇
- **来源**：[[Papers/2607-HiFiUMI|HiFi-UMI]]（full-text，11/11 evidence-ledger claims source-verified）。
- **结构变化**：新增 training dataset 与 convergence observation 11；将 data-engine 论点从“UMI 主要扩大 pre-training”推进到“高保真 UMI 可直接承担 target-task post-training”，并补充 4,000-hour initialization 的 OOD / real-robot 证据。
- **证据边界**：practical-pipeline parity 非等样本（3,200 vs ~300 trajectories）且 scene exposure 不同；pre-training real-robot gain 仅在 StarVLA-QwenPI 验证；四个 fidelity factors 无逐项 ablation。
- **domain_map**：skipped（同轮 EmbodiedAI-Survey 已将该格局变化写入 [[DomainMaps/EmbodiedAI]]）。
- **status**：success

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
