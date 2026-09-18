---
title: Vision-Language-Action Models
description: 从 2022 RT-1 到 2026 π0.7 / GEN-1 的 VLA 全景——按 action 表示与 data recipe 双轴组织，覆盖 AR token / 连续 flow matching / hierarchical / latent / reasoning-augmented / hybrid / world-model-conditioned / RL-post-trained 八类技术路线，重点分析 scaling law、cross-embodiment 统一、real-world RL、reasoning-action 融合、data engine 工学术分化等前沿议题
tags: [VLA, manipulation, embodied-reasoning]
date_updated: "2026-09-18"
year_range: 2022-2026
papers_analyzed: 118
keywords: [vla, vision-language-action, robot policy]
domain_map: EmbodiedAI
---

## Overview

VLA 把预训练 VLM 扩展为端到端机器人策略，将 internet-scale 的视觉-语言知识迁移到连续高频的 motor control，目标是替代 task-specific 手工设计、走向通用 embodied agent。

**领域活跃度（2024-2026）**：

- **时间线**：[[2212-RT1|RT-1]] (2022) 奠定 AR 范式 → [[2307-RT2|RT-2]] (2023) 注入 web VLM → [[2410-Pi0|π0]] (2024) flow matching 跨 50 Hz → [[2504-Pi05|π0.5]] (2025) 家庭长程 → [[2511-PiStar06|π*0.6]] (2025-11) real-world RL → [[2604-Pi07|π0.7]] / [[2604-GEN1|GEN-1]] (2026Q1-Q2) 宣称跨越商业阈值，仅三年从概念验证走到 deployment 讨论。
- **参与格局**：工业方向 Physical Intelligence（π 系列）/ Generalist AI（GEN 系列）/ Google DeepMind（Gemini Robotics）/ NVIDIA（GR00T / DreamZero）/ Figure AI（Helix）/ AgiBot（[[2512-GenieReasoner|GenieReasoner]]）/ Xiaomi（[[2602-XiaomiRobotics0|Xiaomi-Robotics-0]]）/ Dexmal·StepFun（[[2602-DM0|DM0]]）/ Galaxea（[[2608-GalaxeaG05|G0.5]]）；开源方向 [[2406-OpenVLA|OpenVLA]] / [[2506-SmolVLA|SmolVLA]] / [[2510-XVLA|X-VLA]] / LeRobot 生态持续跟进。
- **学术产出**：2025H2-2026H1 主要会议（NeurIPS / ICLR / ICRA 2026）VLA 论文密度激增，arXiv VLA survey 8+ 篇；本笔记覆盖 114 篇核心 + 4 篇 survey（[[2507-VLATokenizationSurvey]]、[[2509-PureVLA]]、[[2510-EfficientVLASurvey]]、[[2405-VLASurvey]]——广义三层 taxonomy（components / control policy / task planner）的 TNNLS 正式版，适合作领域入口，但模块划分轴与 action interface 离散/连续、data regime、control frequency 等真正决定能力的轴脱节）。

**整体趋势**：

1. **Action representation 从 discrete 到 continuous，但"离散只配做辅助监督"这一判断已是争议**：RT-2 token（3 Hz）→ Octo diffusion → π0 flow matching（50 Hz chunk-level），continuous path 在采纳率上仍是默认，离散路线在 [[2504-Pi05]]（FAST + flow 双头）与 [[2512-GenieReasoner]]（FACT = VQ + flow decoder）里确实只承担辅助角色。反例来自 [[2608-GalaxeaG05|G0.5]]：单个 decoder 在共享 vocabulary 上以单一 next-token cross-entropy 同时产出 CoT 与 RVQ 动作码，在同数据、同算力（各 16 H20、同 wall-clock）、同观测与控制栈的真机微调对照里拿到 76.7% 对 π0.5 的 53.3%，并在 BEHAVIOR Challenge 上用 1 个 post-training epoch 超过冠军方案。它的取舍同样清楚——半透明低对比度抽屉上 60% 对 π0.5 的 90%，贴高对比 marker 后回到 100%。纯离散 AR 是否只在特定视觉条件下劣于连续头，目前只有这一组受控证据。这条路线的另一侧边界由 [[2609-PhysBrain15|PhysBrain 1.5]] 划出：语言、动作、视觉三套词表合并成单一 $V$，在 8B 上只用一个 masked next-token 目标训练，28 个具身 benchmark overall 72.5 是开源最高，但动作侧没有任何仿真或真机闭环成功率，全部证据是以 ground-truth 前 16 步为条件的离线轨迹可视化与 action-token perplexity（分布内 17.12→5.07、held-out RoboDojo 12.39→6.57）。统一离散接口能训到 8B，与它能不能闭环控制机器人是两件事。
2. **Dual-system 成 industry default**：System 2 VLM 1-10 Hz + System 1 action 20-200 Hz 的分层解耦被 π0.5 / GR00T N1 / Gemini Robotics / Helix / NaVILA 同时采纳；hierarchical with language intermediate 的历史包袱（语义表达力不足）由 latent action / reasoning trace / 2D trajectory 等替代中间表征消化。
3. **Data recipe > model size**：[[2506-SmolVLA|SmolVLA]] 0.45B、[[2510-XVLA|X-VLA]] 0.9B、[[2602-DM0|DM0]] 2B 反复在主流 benchmark 击败 3-7B baseline；[[2511-GEN0|GEN-0]] 虽然在 7B 观察到"intelligence threshold"相变，但跨越阈值后 data scaling 的 ROI 远大于继续扩参；[[2607-XiaomiRobotics1|Xiaomi-Robotics-1]] 固定 20K hr 数据时 2.6B/5.1B/10.5B 仅 61/75/79%，而 data scaling 把 unseen-env 成功率从 26% 拉到 75%——data 是当前更强 bottleneck 的第二条独立证据。这个判断的适用范围止于长在 action-labeled 数据上的 VLA。生成式主干一侧仍在按参数量买分：[[2609-OpenWAM|OpenWAM]] 固定数据与配方只换 video backbone，RoboTwin 2.0 上 1.3B 90.14 / 2B 91.64 / 5B 92.39 / 14B 93.79 单调上升；同一套实验里最好的两档 visual encoder 只差 0.12（Wan2.2-VAE 90.30 对 DINOv3+S-VAE 90.18）。"扩数据还是扩参数"的答案依赖被扩的是哪一段。
4. **Real-world RL 和 data engine 改写 ceiling**：[[2511-PiStar06|π*0.6]] 的 advantage conditioning + HIL rollout 首次让 4B 级 flow matching VLA 真实自改进；[[2602-GigaBrain05M|GigaBrain-0.5M*]] 的 RAMP 把它推广到"latent-conditioned"；[[2511-GEN0|GEN-0]] / [[2604-GEN1|GEN-1]] 的 500K 小时 wearable 数据路线让"数据天花板"从学术共识变成工业实验室专属筹码。[[Papers/2607-HiFiUMI|HiFi-UMI]] 则显示，足够高的 pose / relative-geometry / synchronization / FoV fidelity 可让 robot-free UMI 直接承担 target-task post-training，而不只是预训练素材。
5. **评测从 lab saturation 转向 real-robot mastery**：LIBERO（98.7）/ CALVIN ABCD→D（4.80）接近饱和；比较重心迁移到 RoboChallenge Table30、[[2511-PiStar06|π*0.6]] 商业部署、AC-One long-horizon、[[2604-GEN1|GEN-1]] 6-task mastery suite 等 real-robot 评测——但这些评测各自为政，尚无统一 leaderboard。
6. **辅助分支退到训练期，接口取代模块成为设计变量**：world model、reasoning trace、检索到的 demonstration 这些原本要在推理时运行的东西，正被改造成只在训练期消费梯度、部署时整体删除的分支——[[2608-WorldTokens|World Tokens]] 61.85 ms、[[2608-JEPAWAM|JEPA-WAM]] 85 ms、[[2608-MobileWAM|MobileWAM]] 938 ms（对推理期生成的 Motus 4950 ms）都靠 attention mask 或排他路由保证删除前后当前观测表示不变。随之改变的是讨论的对象：这批工作的负结果不落在"要不要这一路"，而落在这一路接在哪、以什么形状接（RGB anchor 91.5 低于不接的 95.0；MLP 递归 46.3 低于不递归的 50.2），[[2608-GSRParaVLA|GSR-ParaVLA]]、[[2608-VLAProprioception]]、[[2608-InContextVLA|VLA-Talker]] 从语言、本体感受、证据注入三个互不相干的方向得到同形状的结论。"某模态对 VLA 有没有用"这个问法因此不再成立——必须连接口一起问。2026-09 的 [[2609-LatentInterfaceTraining|LIT]] 把这条推进到视觉通路本身：让 K=100 个 latent token 成为 action expert 唯一的视觉入口，并用 action chunk 末端位姿重建来监督它，四种架构的 LIBERO-Plus 全部上升（π0.5 68.97→79.67、MolmoAct2 63.62→71.92、FAST-WAM 51.44→60.63、ImageWAM 83.02→86.89），而同样 30K 步预算下只加位姿监督得 65.45、照搬分阶段训练得 65.46。决定收益的是有没有这道瓶颈，不是监督信号本身。

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

- **核心思路**：把连续 action 离散化（uniform binning / VQ-VAE / FAST DCT），接在 VLM language token 之后做 next-token prediction，训练 loss 与 LLM pretraining 完全同构。谱系：[[2212-RT1]] → [[2307-RT2]] → [[2406-OpenVLA]] → [[2502-OpenVLA-OFT]] → FAST tokenizer → [[2512-GenieReasoner]]（FACT = VQ + flow-matching decoder）→ [[2608-GalaxeaG05|G0.5]]（RVQ ActionCodec + 原生 CoT，单流 decoder 回到 foundation 规模）→ [[2609-PhysBrain15|PhysBrain 1.5]]（ActionPiece 512 词表与语言、视觉码并入同一个词表）。
- **实际效果**：RT-1 130K episodes / 744 tasks / 3Hz 做出 AR VLA 首次规模化 demo；OpenVLA 7B 在 BridgeData 超 RT-2-X 55B +16.5%；OpenVLA-OFT 用 parallel decoding + action chunking 把推理从 166ms 压到 ~73ms，LIBERO 平均 97.1%（超 π0 的 94.2%）；GenieReasoner 用 FACT 在 ERIQ 拿 82.72% vs base 58.64%；G0.5 以 Qwen3.5 2B 为起点、14 个 embodiment 单阶段预训练，真机微调 76.7%（π0.5 53.3% / GR00T-N1.7 24.4%，同数据同算力）、BEHAVIOR Challenge 0.3136 超冠军 0.2605、不在预训练混合里的 DROID 上零样本 82.5%（π0.5-DROID 57.5%，10/10 任务胜出）、LIBERO 98.9%、RoboTwin 2.0 平均 93.3%、SimplerEnv-Bridge 87.3%。
- **动作离散化重新变成 cross-embodiment 的载体**：G0.5 把每个机器人拆成独立 motion part、pad 到共享维度后训练 RVQ（附 temporal contrastive 目标），全部数据源映射进单一 27 维动作空间（left_control 9 / left_gripper 1 / right_control 9 / right_gripper 1 / lower_body 7），推理时只预测被激活的部件。相比 FAST 的固定 DCT 管线，codec 端到端学习且按设计跨本体——这把离散化从"为了套 LLM 训练范式付出的近似代价"改写成"异构本体的统一接口"。该主张目前只有这一篇的单一 2B 规模证据，无 scaling 曲线。
- **换 tokenizer 的收益取决于拿什么数据训它，而不是换成哪种量化器**：[[2510-VQVLA|VQ-VLA]]（ICCV 2025）把 OpenVLA 的 uniform binning 换成卷积残差 VQ-VAE，LIBERO-90 上 binning baseline 73.53%，只用 ManiSkill 合成轨迹训 tokenizer 崩到 14.38%，再补 RLBench 才到 80.98%；真机 6 任务均值 23%→46.25%，控制频率 4.16→11.84 Hz。补充材料里埋着决定性的一格：只用真实 OXE 训的 tokenizer 在 LIBERO-90 是 71.93%，**低于原始 binning 的 73.53%**——语料最大的那一档反而最差，正文"linear scaling"的措辞没有对应曲线。chunking 混淆也只被排除了一半：让 binning 自回归吐 5 个动作掉到 66.53%，这说明的是该自回归实现差，并行解码的 binning chunk 从未跑过。全文没有 reconstruction 误差、codebook 利用率或平滑度指标，tokenizer 只经下游策略被间接评价。以上数字经 camera-ready 与补充材料逐条核查，该笔记尚无 evidence ledger，也无独立复现。
- **统一离散词表已经训到 8B，执行侧证据仍为零**：[[2609-PhysBrain15|PhysBrain 1.5]] 在 Qwen3-VL-Instruct 8B 上把语言、ActionPiece 动作码（512 词表、每腕 32 token、H=16、10 维 EEF，在 28.7M 段 16 步轨迹上训练）与 RGB+depth+robot-mask 的视觉码合并成单一词表，一个 masked next-token 目标通训；具身预训练监督全部来自约 30,000 小时人类视频，机器人数据只出现在 SFT。它明确拒绝跨本体统一坐标系，改用近期动作历史做隐式 system identification——这与 G0.5 的 27 维定长分区是同一问题的两种相反答案。28 个具身 benchmark overall 72.5 为开源最高、开源内 14 项第一，但仍低于按最低 thinking 档评测的 GPT-6-Astra 73.3 与 Gemini 3.6 Flash 73.0。它不能被当作这条路线可行性的支持证据：全文零消融，没有任何实验分离动作与未来状态联合训练对理解能力的贡献；动作侧无仿真也无真机闭环成功率；理解侧的 SFT 混合含多个被评测 benchmark 的同族训练数据。
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
  - **Likelihood 不可解析**：PPO / trust region 不兼容；π\*0.6 的 "advantage conditioning"（二值 advantage 作 text prefix + CFG 推理）是目前最成熟的 RL 绕行方案。[[2608-GalaxeaG05|G0.5]] 把这一条从"待绕开的工程障碍"提为架构选型论据：AR head 直接暴露 token-level log-probability，GRPO 无需改写即可套用，而 flow-matching head 必须先按 RLinf 引入 SDE 把去噪当 Markov 过程近似出 log-prob；在 4 个 LIBERO 任务（每任务 1 条演示的 post-train 起点、初始成功率相当）上 AR 收敛更快、终值更高、跨 seed 方差更低。证据规模是 4 个仿真任务，不足以推广到真机长程，但它把"用什么参数化生成动作"与"能不能做 RL"这两件事绑在了一起。
  - **梯度污染 VLM**：Continuous flow matching loss 会侵蚀 VLM 语义（[[2504-Pi05]] Knowledge Insulation 用 stop-gradient + FAST 离散辅助监督解决；[[2512-GenieReasoner]] FACT 用离散 VQ token 学 + flow decoder 重构）。2026-07 新证据把侵蚀量化并挑战 KI 的充分性：[[2606-Act2Answer|Act2Answer]] 用"动作作答"协议测出 VLA 相比源 VLM 在语义类知识上掉 20-40 分，且知识在中层仍可线性解码、到动作通路衰减至近随机——问题是"读出通路"而非"数据遗忘"；[[2607-AnchorAlignVLA|Anchor-Align]] 证明 co-training+KI 路线存在 language-action 脱钩（LIBERO-PRO position-swap 0%），在同一 observation 上做 frozen VLM 逐层蒸馏 + 动作转方向词对齐更优（61.0→71.9，shuffle 标签控制实验排除正则化解释）。两篇一致指向：防遗忘应默认配 anchoring / VQA co-training，仅梯度隔离不够。驾驶侧的 [[2608-QwenDrive|Qwen-Drive-1.0]]（Qwen3.5-4B + BEV 感知头 + flow-matching 规划专家）把代价量到了另一个方向：只开视觉-语言训练时 Driving QA 70.07 / General VQA 63.18，再打开 3D 感知监督后变成 69.43 / 62.26，换回来的规划分是 RFS 7.91→7.96，而作者自己声明这组消融不能确立显式 3D 监督是提升的来源。同一篇顺带量出 VLM 表征的边界——冻结主干只训检测头的探针 35.60 mAP，落后用同一 SigLIP-Qwen 编码器训练的 BEVFormerV2\* 6.34 mAP 与 6.91 RayIoU，解冻主干后 mAP 再涨 10.46 而 head 在冻结阶段已收敛。视觉-语言预训练给的是好的视觉初始化，不是现成的 3D 结构；"给 VLM 挂个几何头"这条捷径在这组对照里不成立。
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
- **接口带宽可以做成组合式的坐标契约，但它买到的是进程推进而非语义终止（2026-09）**：[[2609-2AM|2AM]] 把整个任务记忆挪到 Agent 侧，下层 Action Model（Qwen3-VL-4B + flow-matching expert，16 步 chunk）逐 episode 无状态、只看 RGB 与 robot state，上下层之间只传一个 $(\ell, q^{grasp}, q^{place}, q^{move})$ 的四元组——子任务语言加三个 $[0,1000]^2$ 像素点，监督目标由示教确定性反推，训练时用条件 dropout、高斯噪声与时间抖动防止策略只认某一路。LIBERO-Mem 上相对同 backbone、同观测、同 chunk 长度的自建 π0 复现：completion 70.79→76.29、relaxed SR 37.42→63.00，而 strict SR 12.25→11.83 略降，论文自陈证据不支持一致的成功率提升。真正定位机制的是只留语言、去掉 2D hint 的消融（7.25 / 19.42 / 53.72）：加回坐标提示在 relaxed 上 +43.58、在 strict 上只有 +4.58，近 9.5 倍的落差说明 grounded hint 推动的是"把记住的意图执行下去"，按序终止与重复计数不在这条接口的能力范围内。边界很硬：语言-only 一档在三项指标上全部低于 π0 复现，说明这些增益中有一部分是在补插入 Agent 本身带来的损失；摘要里"相对 14.8% 提升 61.5 点"比的是论文自己否定过的已发表 SlotSSM 数字；全文单点估计，无 seed、无误差棒，也未报告每任务 trial 数。

### 4. Latent Action from Unlabeled Video

- **核心思路**：从 action-free video（人类 / 跨 embodiment）无监督学 latent action space，先用 VLM 预测 latent，再以少量 action-labeled 数据做 decoder fine-tune。打开 internet-scale video 作为训练数据源。谱系：[[2402-Genie]]（generative interactive environment，VQ-VAE + ST-transformer）→ [[2410-LAPA]]（VQ-VAE 从 SSv2 人类视频预训练，7B VLM + 30-40× compute 超 OpenVLA +6.22%）→ UniVLA → [[2505-DreamGen]]（video diffusion 作为 offline data engine，log-linear NT scaling，GR00T N1 new-behavior 0% → 43%）→ [[2512-WholeBodyVLA]]（双 LAM：manipulation + locomotion）。
- **实际效果**：LAPA 用纯 human video 预训练正迁移到 Franka；DreamGen 证明 Cosmos / WAN2.1 fine-tune 后的 video 生成 + IDM 提取 pseudo-action 能在 GR1 humanoid 上实现 new behavior 43.2%（vs baseline 11.2%）、new env 28.5%（vs 0%）；[[2602-DreamZero]]（NVIDIA GEAR）把 video diffusion 14B 直接作为 VLA backbone，AgiBot unseen env+object 任务 task progress 62.2% 比最强 VLA baseline 翻倍（且 5B→14B scaling 信号明显）。
- **优势**：绕过 action-label 瓶颈；跨 embodiment 友好；VLM 预训练目标容易收敛（比 raw action 的 continuous regression 简单）。
- **痛点**：
  - **不可解释**：latent 无法像 language motion 那样被人当场纠正。
  - **Latent 混杂**：LAPA 承认 latent 把 camera motion / scene change / agent action 混在一起，对 fine-grained grasping 有害。
  - **Granularity / comprehensiveness / alignment 三道坎**：[[2507-VLATokenizationSurvey]] 明确**不推荐**把 latent 纳入未来 hierarchical 架构。
- **不走 latent 的三条平行路**：human/play 与 action-free 视频不必经由 latent action 才能利用。[[2607-EgoSteer|EgoSteer]] 用 EgoSmith 管线把 in-the-wild egocentric 视频显式重建为统一 R^48 相机系 state-action（9.6K hr / 2.09M episodes，预训练呈 log-linear scaling，40 真机任务 75%），以表示一致性绕开 latent 的不可解释与混杂问题；[[2607-TAP|TAP]] 用 Inverse Dynamics 从 task-agnostic play / off-task 轨迹先学 "how to move" 再以少量 expert 对齐 "what to do"（SIMPLER 相对同架构 BC +10.2pp），代价是仍需 action label 但免语言/任务标注。第三条把桥接直接放进生成主干：[[2608-ZimaBlue|ZimaBlue]] 的第一阶段只在无动作的视频上训 video DiT，动作与状态流仅作 null placeholder 且 Slow 端动作损失关闭，第二阶段靠一个 100 维统一 state-action 接口上的联合 flow matching 完成 grounding，既不学 latent action 也不训 inverse dynamics（详见路线 8 的 2026-09 增量）。

### 5. Reasoning-Augmented Action

- **核心思路**：显式把 reasoning chain 作为 meta-token 插在 action 前/间。纯语言 CoT → 空间化 reasoning → 联合 reasoning-action 优化三阶段演进。谱系：[[2407-ECoT]]（subtask → plan → bbox → gripper pixel → action 七段）→ RAD / DriveVLM / [[2503-CosmosReason1]]（Physical common sense + Embodied reasoning ontology + GRPO RL）→ [[2508-EmbodiedR1]]（"pointing" 作为 embodiment-agnostic 中间表示 + RFT）→ [[2512-GenieReasoner]]（统一 discrete reasoning + flow matching action）→ [[2601-RoboBrain25|RoboBrain 2.5]]（3D $(u,v,d)$ + hop-normalized temporal value）→ [[2602-RynnBrain]]（Chain-of-Point 交错 textual-spatial reasoning）。
- **实际效果**：ECoT 在 Bridge 上把成功率提 28%（2407）；Embodied-R1 3B 在 11 个 spatial benchmark rank 2.1 超 13B SOTA，xArm 真机 8 任务 zero-shot 87.5%（vs FSD 25%）；Cosmos-Reason1 在 intuitive physics (arrow of time, object permanence) 从 42%→81.5%（GPT-5、Gemini-2.5 几乎随机猜）；GenieReasoner 在 ERIQ 82.72%；Lumo-1 用 spatial action tokenizer + subtask completeness prediction，在 6 个 fine-tune 任务上全面超 π0/π0.5；RoboBrain 2.5 用 hop-based value 做**Reverse VOC**（time-reversed task progress prediction），把 GPT-5.2 的 reverse 10-20% 拉到 87-95%。
- **优势**：可解释、可 debug；reasoning 跨 embodiment 一致；可复用 LLM RL 栈；RL 优于 CoT 本身（[[2508-EmbodiedR1]] Table 6 RL > Think）。
- **痛点**：
  - **显著拖慢推理**：[[2407-ECoT]] 350 token/step，N-step freeze / async 摊销后仍 1-2 Hz；[[2509-AnywhereVLA]] 把 VLM 部署到云端 0.5 Hz，高频控制依赖 point tracker 15 Hz。
  - **High-quality reasoning 数据稀缺**：ECoT / RAD / Cosmos-Reason1 都用 auto-generation pipeline。
  - **"Action-token-based reasoning" 未实证**：[[2507-VLATokenizationSurvey]] 提出"不只在语言空间思考"的激进方向，目前无工作。[[2608-GalaxeaG05|G0.5]] 走的仍是语言空间的 CoT（Subtask / BBox / Trace / ActionHint 四类 target 组成 8 种 format 按权重随机采样），但它让 CoT 与动作码共享同一个 likelihood 参数化，于是 CoT 可以直接改写下一步动作分布而不只是改写条件——它在长程 stage-conditioned 任务上的推理时开关增益（Air Fryer progress score 2.4→3.8、Bacon 1.5→3.4）与单阶段任务上的近噪声增益（约 1.6pp）之间的落差，与这个机制读法一致。
- **推理时不生成语言（2026-08）**：本路线长期把"显著拖慢推理"当作可摊销的代价，两组 matched-evidence 对照把它改写成收益归属问题——语言的价值在输入结构化与训练期表征塑形，不在推理时自回归生成。[[2608-InContextVLA|VLA-Talker]] 把证据获取外包给只读感知工具链（GroundingDino 定位、DepthAnything 相对深度、由 proprioception 与相机内外参解析投影的 gripper 像素、Qwen2.5-VL-7B fallback），产出结构化 evidence tuple 后以 `<spatial>` 标签注入 prompt，loss 只覆盖 action token。它的承重实验是同一批 evidence tuple、同一 backbone、只改注入还是生成与 loss 掩码的三行：生成并监督文本 81.5%（4.6× 延迟）→ 注入但仍对证据计 loss 89.7% → 注入且只监督 action 97.4%，第二行单独隔离出监督掩码值 7.7 分。把工具链换成模型自猜掉到 84.3%，低于不注入任何证据的 backbone 90.4%——证据不可靠时，多这一路输入比没有更差。25 demo/task 的数据效率（92.8%）超过 50 demo 的 BC（90.4%），未见物体与加干扰物下 97.4→85.1→80.3（BC 90.4→54.8→47.6）。[[2608-StellaVLA|StellaVLA]] 从另一侧收敛到同一结论：把 expert demonstration 离线压成结构化语言前缀（VLM 分段出 sub-goal + 确定性 verbalizer 把 action span 映射成 `Δx/Δy/Δz` 位移文本及其 2D 投影，零人工标注），test time 按指令 embedding 的 cosine similarity 检索 top-1 注入，训练时并行一个自回归 spatial-language head（λ=0.3），推理时把该 head 整支剥离、单次前向出 action chunk。若改为推理时联合解码语言，单次代价从 88 ms（cached）涨到 3177 ms，约 36 倍。两篇的边界也一致：VLA-Talker 的 Gen-CoT 是作者自建基线且在每个数据预算上都低于纯 BC，"生成式 CoT 有害"这一断言完全压在它身上，最小检验是拿一个已发表 CoT-VLA 权重在同 backbone 同数据上重训后再比；StellaVLA 去掉 demo 只剩 62.4%、检索到错任务 demo 更掉到 44.9%，任务知识被大量外包进上下文通路，检索栈成为部署单点。纯语言检索带来的副产品是跨本体兼容——human-hand XR 录制与 XR-retargeted 轨迹无需视觉对齐即可被机器人 episode 检索到，三种来源给出的动作预测几乎一致（125 条遥操作 71,702 帧 + 各 26 条 XR 与 retargeted 各 10,996 帧）。

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
  - **"zero-shot 迁移到新本体"这句话此前没有统一口径**：[[2609-ZETA|ZETA]] 把它拆成 strict（目标本体既不在预训练也不在后训练里）与 pretrain-exposed（目标本体在预训练混合中出现过，只是没做目标后训练）两档，并按此把 LAP / Cloak / RDT2 归入 strict，Octo / π0.7 / Qwen-RobotManip / OpenVLA / Gemini Robotics 1.5 归入 pretrain-exposed。这个区分不是措辞洁癖：同一套设定下只把 5% 的目标本体数据放进预训练，14 个 held-out 本体的平均任务进度就涨 13.4 分（UR5eUMI 69.3→78.6、GoogleRobot 51.4→68.9）。凡未声明目标本体是否出现在预训练混合里的迁移结果，都无法确定测的是哪一档。

### 8. World Model Conditioning / RL Post-Training

- **核心思路**：把 world model 从"生成训练数据"（DreamGen 路线）转向"推理时 condition"——VLA policy 接收 world model 预测的未来 state 和 value，作为 planning 信号。或者用 world model 内跑 RL，闭环 refine policy。代表：[[2511-PiStar06|π*0.6]]（Recap = value function + advantage conditioning + HIL rollout）→ [[2602-GigaBrain05M]]（RAMP: RECAP 形式化为"对 z 边缘化的特例"，加 future visual latent 做条件）→ [[2602-WorldVLALoop]]（Closed-loop co-evolving world model + VLA via SANS dataset）。[[2511-GEN0]] / [[2604-GEN1]] 代表**数据-first** 路线。
- **实际效果**：π\*0.6 连续 13 小时咖啡馆做 espresso / 2 小时家庭折 laundry / 59 个巧克力包装盒工厂部署；GigaBrain-0 在 RoboChallenge 51.67%（超 π0.5 42.67%），RAMP 在 Box Packing / Espresso 长程任务上比 RECAP +30%；WorldVLALoop 在 real-world 从 SFT 13.3% → RL 第一轮 36.7% → 第二轮 50%；GEN-0 首次在 robotics 观察到 ossification 相变（≥7B "intelligence threshold"）+ power-law scaling $L(D)=(D_c/D)^{\alpha_D}$；GEN-1 把数据扩到 500K 小时 wearable、1h robot fine-tune 达 99% SR × 3× speed（blog only）；DreamZero 把 Wan2.1 14B 作为 WAM backbone，unseen env+object 62.2%，38× 推理加速后 7 Hz 部署。
- **2026-07 增量（WAM 分支细化 + 拿下 sim SOTA）**：[[2607-FlowWAM|FlowWAM]] 用 HSV 编码 optical flow 作为 video-native 统一动作表示，同一双流 DiT（Wan2.2-TI2V-5B）兼任 policy 与 world model（RoboTwin 2.0 92.94%、WorldArena TrajAcc 64.26 最佳），ablation 定位关键在"把 flow 映射进预训练视频先验的 RGB 空间"（raw flow 72.3 → HSV 89.8）而非 flow 本身；[[2607-ABotM05|ABot-M0.5]] 把 video → frame-level latent action → executable action 组织为三级生成链，Dual-level MoT 解耦 mobility/manipulation 分支、Dream Forcing 缓解 self-dreamed rollout 的 exposure bias（RoboTwin 2.0 94.1、LIBERO 99.4、RoboCasa365 40.4/46.6），首个统一移动与操作的 WAM，但 Composite-Unseen 仅 7.9%；[[2606-RehearseVLA|RehearseVLA]] 用 action-conditioned video WM 替代仿真器做 RL post-training（LIBERO 5-demo 79.6 vs SFT 74.85，与仿真器 RL 的 RIPT-VLA 持平），与 [[2602-WorldVLALoop]] 互证"失败/次优探索数据是 WM-as-simulator 的关键 ingredient"，但 WM 冻结、未设防 reward hacking；[[2606-Orca|Orca]] 把 modeling target 上移到 Next-State-Prediction 统一 world latent，冻结 backbone 后 language/image/action 三路 readout 随预训练数据 scaling 同步提升（双臂 OOD action readout 32.4 vs V-JEPA 2.1 的 17.0，但 binary success 仅 6%）——world latent 作为 VLA 上游表示的可反驳性检验。
- **2026-08 增量（未来该用什么表示 + world model 移到 critic 侧）**：这条路线在 2026-08 分出两个此前没有的子问题。其一是**被预测的未来该用什么表示**：[[2607-STWAM|ST-WAM]] 观察到只在 VAE latent 空间监督未来的 WAM 在视觉分布偏移下会把预测未来"拉回"训练域外观，于是让 VAE future、DINOv3 future、action 三个 DiT 组成 Mixture-of-Transformers 联合 flow matching（DSFE），并用 Qwen3-VL 的当前多模态 hidden state 作 query 从近 4 帧 DINO history 检索意图 token 注入 action expert（CAIR）；推理时两条 future 分支被 attention mask 整体切掉，退化为 action-only policy，代价是 32 步 chunk 756.17 ms 对 Fast-WAM 609.30 ms（1.24×）。零样本 LIBERO-Plus 72.8% 对 Fast-WAM 51.5%（七个扰动维度全面提升，camera / sensor-noise 各 +39.0 / +41.8），真机 Agilex Piper 四类视觉偏移平均 61.5% 对 Fast-WAM 25.8% / π0 32.8%，compound 偏移 48.0 对 15.3。但它的消融同时给出一个负结果：只用 DINO 未来在 LIBERO-Plus 只有 39.7%，**低于纯 VAE 的 Fast-WAM 51.5%**——语义未来与像素未来是互补而非可换，"换个更鲁棒的表示去预测"这条捷径不成立。可比性边界：LIBERO-Plus 的 baseline 数字明确引自第三方 robustness study 而非本文重跑，LIBERO / RoboTwin 两表则未交代 baseline 来源；真机组是唯一能确认同示教同流程的对照。其二是**world model 从 actor 侧移到 critic 侧**：[[2607-WCM|WCM]] 把 LeJEPA 轻量骨架接成 critic，共享 trunk 同时回归 return 与预测下一帧 latent（$\mathcal{L}_{\text{value}} + \lambda\mathcal{L}_{\text{pred}} + \eta\mathcal{L}_{\text{SIGReg}}$），可直接替换 PPO / Flow-SDE / AWR / RECAP 里的 critic；LIBERO-Plus 上从 one-shot SFT 起跑约 250 步 RL 即超过 20k 轨迹的 Full-SFT（π0 72.8 vs 71.2、π0.5 73.7 vs 72.9、OpenVLA-OFT 74.0 vs 71.7），WidowX-250S 7 个真机任务全面优于 AWR / RECAP，长程 stovetop cleaning 从 1/50 提到 15/50（OpenVLA-OFT）、4/50 提到 33/50（π0.5）。其最有信息量的实验是把 critic 换成 2-5 帧历史 ViT（论文明确定义为 $\lambda=0$ 特例）仍然无效——缺的是**预测性目标**而不是时序输入。
- **2026-09 增量（设计空间被系统扫过一遍 + 视频小时数成为可买的尺度轴 + RL 把延迟写进目标）**：
  - **WAM 的设计空间被受控扫了一遍，而扫出来的最优解随训练阶段变化**：[[2609-OpenWAM|OpenWAM]] 把 WAM 形式化为 $C(E, S, M)$ 三元组——visual encoder $E$、system 组合 $S$、attention mask $M$——固定数据与训练配方逐轴消融。四个结论对本综述有约束力：backbone 参数量在固定数据下单调买分（1.3B 90.14 / 2B 91.64 / 5B 92.39 / 14B 93.79，RoboTwin 2.0），而 encoder 一档从 76.42 到 90.30 跨度极大、最好的两档只差 0.12；四种 attention mask 里 action-sees-video 92.39 与 mutual 92.15 明显高于 isolated 87.41 与 video-sees-action 87.63（缺口约 5 分），但**最优 mask 在具身预训练前后翻转**（预训练后 mutual 相对 action-sees-video 转为 ID +0.70 / OOD +0.72）；16 种异步去噪配置（variance-shift 与 linear-offset 各 8 档）落在 88.5–92.3，无一超过同步去噪的 93.0——"让 world 分支与 action 分支错开去噪步"这条直觉在这组扫描里不成立（该图未点名评测 split，只能作方向性结论）；具身预训练的收益几乎全在分布外（ID 87.00→约 88.5，OOD 14.50→23.80–26.62）。它同时暴露了这条路线的共同弱点：α 在 LIBERO-Plus 总分 69.2，而 Camera 33.8 与 Noise 39.8 两列是全表垫底区，与 Fast-WAM、ABot-M0.5 同形——**以 pixel latent 为预测目标的 WAM 在视角与噪声扰动上系统性脆弱**，这与 [[2607-STWAM|ST-WAM]] 的出发点是同一观察的两次独立记录。可比性边界很多：论文自称的"single→dual→tri 随容量持续提升"被同表 MoE 84.63 低于 Vanilla 85.50 推翻；架构表与 mask 表对同一配置给出 92.36 与 92.39/92.15 两套数且全文无调和；RoboCasa365 上自称"与最佳仅边际差距"实为落后 19.2 分、榜上第 3；Avg 列按试次加权而表头未说明；对 ID/OOD 分化给出的两条机制解释都没有对应实验；baseline 分数是复跑还是引用，全文未交代。真正可复用的产出是 Apache-2.0 代码与 HF 上 46 个覆盖**每一个消融臂**的 checkpoint，使这套扫描可被独立重跑——占预训练 30.1% 的自采第一人称语料不在释出范围内。
  - **视频小时数成为 WAM 的第三条可买尺度轴，买到的主要是扰动鲁棒性**：[[2608-ZimaBlue|ZimaBlue]] 的四档累加式预训练（共享同一份 DROID 后训练）在 12 个 held-out Franka 真机任务上给出 36.1 → 46.1（加 6K 多形态动作数据）→ 66.9（加 60K 视频）→ 77.8（加到 120K 视频）的阶梯；最后一档拆开看，视频 60K→120K 在 Standard 上只有 +5.0，在 Perturbed 上是 +22.5。**这与 OpenWAM 的"预训练收益几乎全在 OOD"是两套数据、同一形状。** 它的部署侧把 Slow（5B video DiT）与 Fast（0.5B，由 Slow 前 12 层初始化、cross-attend 前 12 层 video K/V）解耦异步：449.6 → 145.6 → 33.0 ms，整体 13.6×，蒸馏档保留 75.0% 总体成功率（比未蒸馏低 2.8 分）——未来帧一帧不实例化，Fast 消费的是 K/V 缓存。两条边界必须同记：全文没有把总小时数或算力配平后用 action-free 视频替换 action-labeled 数据的对照，因此"视频比动作标注更划算"不成立，阶梯只说明加视频在既有配方上有增益；也没有"保留 Fast 但移除或破坏 Slow video K/V"的消融，Fast 究竟消费到了什么未被隔离。零样本 LIBERO-Plus 86.7 分里 Camera 一列 58.1 低于 π0.5 的 78.4，再次落在上一条的 pixel-latent 脆弱性上。
  - **RL 后训练开始把推理延迟写进优化目标，而非事后用 chunk 平滑补偿**：[[2609-RealTimeExpoFT|Real-Time EXPO-FT]] 的设定是动作在生成完成时环境已前进 $d$ 步，于是让一个零延迟的 edit policy 在执行时刻以最新观测修正 base policy 的 chunk，并异步生成多个候选交由 Q 函数挑选（作者论证 edit 以最新观测为条件使 base+edit 组合在延迟下仍是 Markov 的）。真机 DROID 单臂（π0.5+LoRA，三个任务人为注入额外 100 ms 使总延迟约 167 ms）四任务 30 试次的阶梯把贡献拆得很干净：只给 SFT 加 RTC 12.5→18.0，在此之上做 EXPO-FT RL 18.0→25.0，再换成执行时刻 edit 加 Q 选择 25.0→29.0；作为参照，**延迟无关的 RL 在同一起点只从 18.0 到 18.8**。延迟不是可以留给 RTC 之类推理期平滑去吸收的实现细节，它改变了 RL 该优化的对象。摘要"42% → 97%"比的是 SFT 而非最强对照，真实边际是 29 对 25；abstract 宣称在 10/10 环境取得最佳与其表注的 0.95× 加粗规则不一致；真机每格单次 30 试次、无 seed 无误差棒；仿真的 Kinetix 部分完全不含 VLA；无代码释出，且所基于的 EXPO / EXPO-FT / FASTER 均为同一第一作者前作。
- **优势**：
  - 突破 BC 天花板（π\*0.6 throughput 2× 不靠增量 demo）。
  - World model latent 提供 dense supervision，缓解 sparse reward。
  - 数据路线：wearable / synthetic 绕开 teleop 瓶颈。
- **痛点**：
  - **推理成本**：DreamZero 默认 5.7s/chunk，要 2× GB200 才 7 Hz；WAM 的 long-horizon drift (>200 帧) 至今未解。
  - **Reward hacking**：world model 的盲区被 policy exploit（[[2602-WorldVLALoop]] Fig 5 展示 policy 学会抓杯子背面），要 iterative close loop 才能稳住。
  - **数据壁垒**：GEN-0/1 完全 proprietary，500K 小时 wearable 数据 + 数据采集方法论不公开。学术社区系统性落后于工业实验室。

### 路线 8 的分叉：world model 退到训练期（2026-08）

上文两种用法——world model 当离线数据引擎（DreamGen 路线）、当推理时条件（RECAP / RAMP 路线）——都把生成或预测留在部署链路上，代价是 [[2602-DreamZero|DreamZero]] 5.7 s/chunk、Cosmos Policy 610 ms、Fast-WAM 182 ms 这一档延迟。2026-08 有四组工作走通了第三种用法：world modeling 只作为训练期的梯度来源塑造 policy 消费的表征，训练一结束整条预测分支被删掉，部署延迟回到普通 VLA 量级。[[2607-STWAM|ST-WAM]] 用 attention mask 整体切掉两条 future 分支已属此列，另三组把它做成了明确的设计目标。

[[2608-WorldTokens|World Tokens]] 的机制最直白：Qwen3-VL-2B 的特征经 12 层 Perceiver resampler 压成 256 个 world token，这些 token 同时条件化 Cosmos Predict2.5-2B 的未来视频去噪分支，**并且是 action expert 唯一的 visual-language 入口**。排他路由是全文承重件——允许 action expert 旁路 world token 直接读 VLM 特征后，LIBERO-Long 从 97.0 掉到 94.1，video 目标由"塑造表征"退化成"与动作目标竞争"。第二个设计是反捷径：video 分支的首帧条件用 Canny edge map 而非 RGB，换回 RGB 后掉到 91.5，**低于完全不做 world modeling 的 95.0**——辅助任务设计错了是净损害而非零收益。部署删掉整条 video 分支后 61.85 ms/chunk，在 π0.5 的 1.1× 以内；LIBERO 平均 98.2%（非该表最优，Cosmos Policy 98.5、DiT4DiT 98.6 更高，后者为跨硬件数字），SIMPLER WidowX 71.5% / GoogleRobot 82.1%，Galaxea R1 Pro 真机四个抓放任务各 24 trial 共 96 次 76.0% 对 matched Qwen-GR00T baseline 59.4%。注意力熵从 5.22 bits 降到 3.29 bits（均匀分布为 6 bits）给了一条超出成功率的表征证据。

[[2608-JEPAWAM|JEPA-WAM]] 换掉预测目标的构造方式：把当前帧与 δ 步后的未来帧沿时间维 stack 后交给冻结的 V-JEPA 2.1 联合编码，得到一个逐 patch 对齐的 joint current–future target（V-JEPA 的 tubelet=2 使双帧输入仍产出 24×24 grid），一个 Qwen2.5-0.5B shared predictor 同时做 latent transition 预测与 flow-matching 动作生成。它的 design analysis 把预测目标的每一处构造都拆成了独立对照：joint target 79.2 对 future-only 77.3，对只用 V-JEPA 表示而不做 transition 预测的 77.0，对换成 DINOv2+SigLIP 的 73.2；破坏 patch 对应的 iREPA 式卷积变换掉到 74.7；去掉 action placeholder、改用全部 hidden state 条件化 action expert 掉到 73.1。同一条 transition supervision 作为辅助 loss 嫁接到 pretrained π0.5 时，64 个 future token 被 attention mask 挡在 action token 的可见范围之外，于是增益只能经共享 backbone 参数传导——LIBERO-Plus 84.5%→86.3%，LIBERO 96.9%→97.8%，真机双臂 ID 77.5%→90.3% / OOD 72.5%→84.7%。边界有两处硬的：RoboTwin 2.0 只在 Clean 上训练，π0.5+JEPA 在 Clean 上 +9.2 分而在 Random 上只从 37.2 到 37.5，transition 监督对强 appearance randomization 几乎不起作用；LIBERO-Plus 的均值领先主要来自 camera 扰动一列，语言扰动一列落后于同表两个 baseline（该分列数字未进笔记的 evidence ledger，只能作方向性观察），与其 0.5B 语言主干和 language-agnostic 的预测目标一致，作者自己把 language-conditioned target 列为后续工作。

[[2608-MobileWAM|MobileWAM]] 把这套配方搬到 whole-body mobile manipulation，主张 mobile manipulation 的长程性来自因果深度而非帧数：Wan 系 video DiT 与轻量 action expert 做逐层 joint attention，action expert 的每个 FFN 换成 shared / locomotion / manipulation 三专家软路由，再加一条只在训练期存在的 Chain-of-Foresight——第 k 步去噪第 k 个未来 latent 并把 belief 串行传给第 k+1 步，梯度经四个 backbone tap 层反压主干。不对称 attention mask 保证没有任何 video token 看得到 action token，于是推理时 backbone 退化为可缓存的 current-frame encoder，未来帧一帧都不实例化，单周期 938 ms 对 Motus 4950 ms、LingBot-VA 8126 ms。ManiSkill-HAB SetTable 七子任务平均 73.0%（AC-DiT 55.6%），真机 ARX Lift2 五任务 55/35/25/20/15% 对同数据微调的 π0.5 的 35/25/10/10/0%。

**这条分叉真正的产出不是三个 SOTA，而是给「多接一路预测 → 表征更好 → 动作更好」这条此前只有相关性证据的因果链补上了一批同 backbone 的受控对照。** 三组各自的负结果指向同一件事——辅助监督与主干的接口形状比监督量重要：World Tokens 的 RGB anchor（91.5）低于不做 world modeling（95.0），非排他路由（94.1）低于排他路由（97.0）；MobileWAM 用 MLP 做串行递归得 46.3，比完全不加 foresight 的 50.2 还低 3.9，换成 transformer 才转正到 58.2，而把 belief 从全部 30 层拼出来只有 37.1、稀疏均匀取 4 层 58.2；JEPA-WAM 的 full-hidden 条件化 73.1 与 action placeholder readout 79.2 相差 6.1 分。可比性边界要一并记住：三篇的 baseline 数字均未声明由本文重跑，MobileWAM 全文除自身 ≈6.5B 外不报任何 baseline 参数量（因此真机上比的是 WAM 配方还是更大的视频预训练主干无法区分）、真机每任务 trial 数与示教条数均未报告、abstract 的 "strong generalization" 与附录"评测在训练分布内随机化初始条件"的协议对不上；World Tokens 无代码、K=256 与 λ_w=5 无 sweep；JEPA-WAM 代码标 "Coming soon"、真机每任务仅 10 rollout、δ 为逐 benchmark 手调且未报敏感性。

### 两端的对照组：不含 VLM 的 V+L→A，与不含动作接口的 VLM 直控

上述八条路线共享同一个前提——action policy 应当长在预训练 VLM 之上。[[2607-TurboVLA|TurboVLA]] 给了这个前提一次对照实验：执行路径上完全没有 LLM，DINOv3 编码图像、BERT 编码指令、6 层双向 cross-attention 做融合（权重初始化自 Grounding DINO，语言-视觉对齐先验来自 grounding 预训练而非 VLM），ACT decoder 出 action chunk。LIBERO 4-suite 平均 97.7%（0.2B / 0.9GB / 31.2ms，32 Hz），RoboTwin 2.0 Randomized 60.2%（0.4B / 43.4ms，≈23 Hz），真机 AgileX Piper 四任务 92.5 / 80 / 90 / 87.5%。

按上表口径，它在 LIBERO 上与 [[2510-XVLA|X-VLA]]（0.9B，98.1）、[[2602-XiaomiRobotics0|Xiaomi-Robotics-0]]（4.7B，98.7）同处噪声带，参数少一到一个半数量级、延迟低到可裸机 32 Hz 闭环。这有两种读法，而论文自己的 ablation 支持后一种：把语言指令整体替换成 task-ID embedding，LIBERO 只掉 2.3pp（97.7→95.4）。该 benchmark 的语言条件因此接近闭集任务索引，VLM 语义先验在其上本就无处发力，"去掉 VLM 不掉点"主要是 benchmark 的性质而非 VLM 无用的证据。RoboTwin 2.0 上 60.2% 与 WAM 系 92-94% 的差距也指向同一方向——脱离闭集短程设定后差异重新出现。

被这篇论文改变的不是路线排序，而是举证责任：任何"VLM 先验带来泛化"的主张，此后应当配一个语言鉴别力已被验证的评测，或至少一个同规模无 VLM 基线。TurboVLA 自身同样受此约束——全文没有 OOD、指令改写或未见物体实验，因而也不能宣称轻量架构可泛化；延迟数字未声明分辨率、数值精度与编译设置，LIBERO-Long 94.2% 在其对比表中仅第 6，无 seed 与误差棒，表中 "Emb. PT ✗" 指未做具身预训练而非从零训练。

另一端的极简基线是把动作接口也一并去掉。[[2609-DroneCATS|DroneCATS]] 让 go / rotate / think / finished 四个动作**只在 prompt 里用自然语言声明**——没有 action head、没有 action tokenizer、没有 function-calling schema，观测是单目 RGB、深度由模型自估——9 个 MLLM 插进同一个 agent scaffold 在 AirSim 飞 100 个 episode。它对本综述的价值不在成绩表，而在把"任务已完成"的判定权交还给模型之后暴露出的落差：最好的模型 Approaching 阶段 SR 65%，而 Qwen3.5-9B 的 oracle 成功率 90%（高于任何 frontier 模型）只转化出 35% 的 SR，平均在起始距离的 0.63 处就宣告到达；Qwen3.5-2B 在 1.28 倍起始距离宣告，四格 SR 全为 0。**把飞机带到目标附近与判断"我到了"是两种能力，可以完全解耦。** 这与路线 3 中 [[2609-2AM|2AM]] 的 relaxed +43.58 对 strict +4.58 是同一现象在两个平台上的记录——推进任务进程的接口不自动带来语义终止能力。另两条观察同向：具身特化的 Gemini Robotics-ER 2 四格均值 47.5% 低于通用的 Gemini 3.7 Flash 57.5%；单机排序不迁移到指挥 4 机（GPT-5 单机 60% 而指挥 20%，Claude Opus 5 单机 35% 而指挥 0%），小模型在四机同步指令上大量复制同一坐标（Qwen3.5-9B 70%、27B 58%，frontier 模型均为 0–1%）。

这套设定的证据边界比多数 benchmark 更硬，而论文自己把它们量了出来。它**没有跑任何非 MLLM 基线**——无经典 visual servoing、无训练过的 RL 或 VLA policy——因此不能用来排"VLM 直控"与"训练出来的 policy"的高下，只能读作 MLLM 之间的横向比较。同一模型三次重飞得 46 / 50 / 35（满分 80，43.7±7.8），单格标准差约 9–13 个百分点，小于这个幅度的模型间差距不可解读。成功判据本身是可选的：只按首次宣告计分会把 182 个成功中的 95 个翻成失败，只按末次翻掉 58 个，而 337 个从不宣告的失败里有 61 个曾进入 δ 半径。scaffold 与 prompt 本身没有消融，且 scaffold 不执行 prompt 自己声明的每步 ±90° 旋转上限（6401 次旋转越界 215 次），history 里的坐标是像素而 prompt 定义模型坐标为 0–1000，每往返一次被缩放 1.28 / 0.72 倍而代价未被度量；全部结果在仿真中，无实机飞行。

### 横切议题一：语言鲁棒性是架构内的信息路由问题（2026-08 新增）

[[2604-DAERT|DAERT]] 把"只改写指令即崩"记录成现象（π0 LIBERO 93%→5.85%）之后，缺的是位置与机制。[[2608-GSRParaVLA|GSR-ParaVLA]] 给出两层诊断：一是**语义没丢**——行为探针在 10 个候选任务里做 Retrieval@1，π0.5 0.941、VLA-Adapter 0.675、SmolVLA 0.516，全部远超 0.1 的随机水平，语言主干仍然能把改写句归到正确任务；二是**路由坏了**——只替换进入 VLA-Adapter 最后一个 Bridge-Attention block 的语言特征、其余全部保持改写状态，消除 96.8% 的动作差异，配对成功率 60%→96%。两个独立方向的对照支持同一读法：把图像换成 dummy 图使 Full Para 从 46.82 升到 61.58（配对 +14.76，换成固定自然图像只有 +7.17），说明失效来自动作策略对 joint V-L 编码漂移的敏感；沿估计出的 32 个"措辞方向"做子空间移除把 action gap 从 0.4361 压到 0.2282（同范数随机方向 0.4386，几乎无效），闭环 55%→90%。

对应的修法（GSR）只有三步：让不看图像与状态的冻结 T5-large 承担任务语义，投影进各架构**原生的**融合位置，动作专家从头重初始化；训练只用 canonical 指令，不喂任何改写数据。Full Para 上 SmolVLA 4.47→49.12、VLA-Adapter 46.82→70.94、π0.5 73.60→75.59；PRIDE 分别为 2.6→41.4、36.7→62.0、–→70.4。"增益来自容量"被三个对照排除：三种"加可训练参数但不引入独立语言源"的变体全部落在同一个 46.82，Native 直接加 T5 也只有 47.31。

两处负结果比主表更重要。**注入位置不可移植**：在 SmolVLA 上照搬 VLA-Adapter 式的后端 sidecar，canonical 有 76% 但改写只剩 13.49%，注入到 SmolVLM 原生语言位置才得到 49.12；逐层扫描下 VLA-Adapter 的最后一个 Bridge-Attention block 能恢复 96.8% 的动作差异，SmolVLA 与 π0.5 的最佳单层只有 10.5% 与 31.3%，附录 D.3 预注册了三条判定"通用语义断点"的标准并明确声明**没有模型同时满足**——跨架构统一的语义接口目前不存在。**语义源必须与视觉编码解耦**：作者自己的 ParaVLA（0.33B active，冻结 T5 按任务缓存 + 共享 DINOv2-Large，融合只发生在 8×16-head flow-matching 动作专家内部）在 LIBERO-Goal canonical 92.0 / paraphrase 91.0、Full Para 72.51、PRIDE 66.9；同一架构把 T5 换成 SmolVLM decoder 后 canonical 尚有 85.0，paraphrase 塌到 41.0。

这条结果同时补上了上一节 [[2607-TurboVLA|TurboVLA]] 缺失的数据点：ParaVLA 是"执行路径不含 VLM"的第二个实例，且它有改写泛化证据——**去掉 VLM 未必损失语言鲁棒性，决定性变量是语义源是否与视觉编码耦合**。反过来，两篇论文也共享同一个测量学天花板：GSR 的全部仿真证据来自 LIBERO-Goal 的 10 个任务共享同一视觉场景，一个改写不变的句子编码器与一个 10 路任务码在此设定下功能上分不开，这与 TurboVLA 把指令换成 task-ID 只掉 2.3pp 是同一问题的两面。其余边界：附录 A.5 声明了 exact 双侧 McNemar 与任务分层 bootstrap 95% CI，但正文 23 页没有出现任何 p 值、置信区间、标准差或误差棒，每个配置单一固定 seed；除 π0.5 外没有把"动作专家重初始化"与"T5 注入"分开的消融，而 π0.5 恰是增益最弱的一档（+1.99）；真机 AgileX PiPER 每条路线 30 trial（6 任务 × 5 trial × 2 条件），Native 全部 0%、GSR 50% / 40%，其中 3 个任务在两种条件下都是 0%，且"OOD"改写是词汇级替换（pick up→grasp），有一个任务只调换语序。榜单意义上 [[2602-XiaomiRobotics0|Xiaomi-Robotics-0]] 报告的 Full Para 76.0 仍高于 GSR 最好的 75.59，PRIDE 69.2 与 70.4 同档——LIBERO-Para 的第一名并未易主，本文的价值在机制而非 SOTA。

**同月出现的相反定位使"语义保住了、只是路由坏了"这一读法降级为争议。** [[2608-CofactVLA|CofactVLA]] 面对同一现象（VLA 无视指令、抓最显著的物体）给出的假设是语义根本没进来：图像经一个 latent visual confounder 打开 backdoor path 绕过语义意图直接决定动作。它的修法相应地在输出端做减法——额外跑一条把语言 mask 掉的前向作为纯视觉偏置估计，动作层把 factual velocity 中与之共线的分量投影掉再按 γ=2 放大残差（OPG），特征层把两分支协方差差的正特征空间从第 15、16 层的 KV 特征里减掉（CCR）。两种定位不互斥——语义可以既在语言主干里保住、又在融合处被视觉压倒——但它们指向完全不同的干预点：GSR 换语义源与注入位置，CofactVLA 在 velocity field 与 KV 特征上做减法。判据是一个双方都没做的实验：在真机 OOD 场景下跑 GSR 那套行为层 Retrieval@1 探针。

CofactVLA 自身的证据不足以裁决这场分歧，而它输掉的恰是最该赢的那一轴。LIBERO-Plus 上 total 69.1%（π0 53.6%、OpenVLA-OFT_m 67.9%），但唯一直接测量语言扰动的 Language 列只有 71.8%，落后 OpenVLA-OFT_m 的 81.0% 达 9.2 分；Camera 列 44.7% 也落后 π0-Fast 的 65.1%；69.1 这个总分靠 Robot（49.7）与 Layout（70.2）两轴撑起，而这两轴与"语言因果性"关系最远。表内还缺席它自己的底座 π0.5，于是"显著超过 π0"的 +15.5 分里混着底座升级与干预两件事。评测预算与断言精度也不匹配：标准 suite 每 suite 10 episode、LIBERO-Plus 每任务 1 episode，全文无 seed 无误差棒。唯一样本量像样的是真机——AgileX PiPer 四任务各约 100 条示教、各 100 次 trial，标准环境 90.8% 对 π0.5 的 71.0%，作者自设 OOD 环境 75.8% 对 23.5%；π0.5 在这四个任务上的 OOD 表现是崩塌式的（0 / 25 / 29 / 40，其中一项由 100% 直接归零），CofactVLA 则保持在 67–83 的窄带内。这个"方差收窄"的形状比 +52.3pp 的均值差更能说明干预移除了某个会整体失效的依赖，但组件消融只在分布内的标准 LIBERO 上做过，OOD 与真机都没有——最抓眼球的数字恰是证据链最薄的一处，而这里的 OOD 是对同样四个训练任务施加背景纹理、干扰物与指令改写，测的是 nuisance invariance 而非未见任务泛化，且论文未说明 π0.5 baseline 是否在同样约 400 条轨迹上以同样步数微调。

无论哪种定位成立，裁决它都受制于一个更基础的障碍：现有评测里语言本来就接近可有可无——GSR 的全部仿真证据来自共用同一场景的 10 个 LIBERO-Goal 任务，而 TurboVLA 把整条指令换成 task-ID 只掉 2.3pp。[[2608-InstructMove|InstructMove]] 把"指令不可省"提成 benchmark 的构造约束：每个 episode 必须包含至少两个物理上可执行的候选，只有一个与指令一致，于是正确动作无法纯由视觉推断。它在 Isaac Lab 上按这条约束造了四个任务族（跨类干扰 / 同类属性 / 空间关系 / 组合式取放），1,757 个经尺度与抓取可行性双重质检的 asset，示范由脚本合成而非遥操。最有用的设计决定是指标：分阶段分数里的 Reach 相对**指令一致的目标**定义，于是"物理上完成了一次干净的抓取，但抓错了物体"记为失败——多数 manipulation benchmark 的成功率定义恰恰会把这种情况记成成功。按此口径，四个策略在 100 条示范微调后的表现与常规榜单差距极大：空间关系一族是全表最低，π0.5 / GR00T N1.7 / Motus 的 Reach 只有 0.46 / 0.50 / 0.51，而该任务场上只有一个同类干扰物。

它的 counterfactual 诊断给这场"语义有没有进来"的分歧添了一个具体形状的数据点，但不能裁决它。场景不动、只把指令改指向另一个可见物体并以该物体为新目标，π0.5 的 target-conditioned 分数 0.72/0.53 与原指令下的 0.74/0.48 基本持平——**语言确实能改写"选哪个"**。而把指令换成泛称、清空、或点名一个场景里不存在的物体时，any-object Reach 是 0.99–1.00——**语言不能门控"要不要动手"**。失败模式与之一致：π0.5 的 18 次 Reach 失败里有 15 次抓的干扰物与目标共享颜色、形状或 affordance，像是响应了指称短语里的某一个显著属性而没有绑定整个短语。这既不是 GSR 式的"语义保住了只是路由坏了"，也不是 CofactVLA 式的"语义根本没进来"，而是语义进到了目标选择这一路、没进到动作发起这一路。裁决仍然缺席：该诊断只在 π0.5 一个模型、一个 split 上做过，且三条无效指令条件只报 any-object 比例，**全文没有报过"去掉语言后 target-conditioned Reach 是否掉到随机水平（6 选 1 约 0.17）"**——这个成本极低的数字才能把 text-indispensable 从构造性主张变成可测量属性。另两条边界：它对既有 benchmark"不 text-indispensable"的指控靠的是一张设计目标对照表加引用 LIBERO-CF，作者没有在任何既有 benchmark 上自己跑 language-blind 策略；每任务仅 100 条示范、统一 5,000 步且不做 checkpoint 选择，Lift 普遍落在 0.01–0.17，把 Reach-Lift 落差解读成"grounding 与控制的分工"之前得先排除训练不足；作者自陈仿真排名与真机表现的相关性未被建立。

### 横切议题二：触觉作为输入与预测通道（2026-08 新增）

触觉此前不在这八条路线里，2026-08 有两篇同团队工作把它推成一条独立建模轴，但它们的证据互相冲突，因此这里记为**争议**而非新路线。

[[2607-N0VTLA|N0-VTLA]] 的做法是把触觉从"多一路观测"改成**预测目标**：冻结 DINOv2 编码 contact-difference 图像，轻量 predictor 连同 vision-language 上下文压成 10 个 latent tactile token，用来估计未来 H=50 步 action chunk 内的净接触变化，直接条件化 flow-matching 动作专家，触觉全程不进 VL prefix；Stage 2 屏蔽 VL prefix 迫使动作损失只能经这些 token 下降。结果为 9 个真机任务均值 47.2 对 [[2504-Pi05|π0.5]] 29.4、20 任务仿真 63.8 对 44.0、第三方 UniVTAC 83.1 对 InternVLA-A1 67.1，latent token 在约 32 个候选池里 top-1 92.3（对照组 57）。姊妹作 [[2607-N0TWAM|N0-TWAM]] 把触觉做成世界模型的一路专家，其消融却显示去掉**反应式**（observed）触觉通路比去掉**预测式**（predicted）通路损失更大（UniVTAC 70.5 vs 71.8、NeoSim 29.6 vs 41.1），而最大单因素是预训练数据量（降到 20% 掉 19.1 分）。"把触觉做成预测目标"这一核心主张因此没有一致证据。

同一篇论文里更值得记的是 **ALTER** ——一个不需要额外环境交互的 advantage-conditioned 离线 RL 配方，把 stage-relative progress 与轨迹事件的比较转成二值 advantage 标签，progress model 只吃多相机 RGB 与 prompt，触觉/运动学/事件信号只用于离线构造目标。它与 [[2511-PiStar06|π*0.6]] 的 advantage conditioning 同族，替换掉的是"advantage 标签从哪来"。三个长时程真机任务横着读：π0.5-SFT 40/20/5 → π0.5+ALTER 90/75/60（+50/+55/+55），换成触觉 backbone 只有 50/35/20（+10/+15/+15），且 π0.5+ALTER 全面超过 N0-VTLA-SFT。**在这三个可形变物体任务上离线 RL 是主导项、触觉预训练是二阶项**，而形变物体恰恰是触觉最该发挥作用的一类。

证据独立性的硬边界必须同时记：两篇同团队，NeoData / NeoSim / NeoReal / NeoForce 均出自公司网页报告、一手出处不可独立核查，八个基准中仅 UniVTAC 为第三方，且 N0-VTLA 在 UniVTAC 的 8 个任务里输掉 3 个（Insert HDMI 25，对照 Xiaomi-Robotics-0 的 69）；真机每任务 20 trial（分辨率 ±11%），无 seed 与方差，也没有同一 checkpoint 关掉触觉的对照。

### 横切议题三：proprioceptive state 的接口、历史深度与参照系

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

**同一变量的第三条轴是 state 与 action 用什么参照系表达，它对跨本体迁移的影响比注入位置大一个量级。** [[2609-ZETA|ZETA]] 固定 π0.5 式 MoT 主干、固定数据与评测，只改 state 与 action 的表示，在 14 个 held-out 本体（7 仿真 + 7 真机）上评：(绝对末端位姿 state, 世界系 delta action) 的平均任务进度 60.3±1.1，(末端系 delta, 末端系 delta) 为 75.7±1.3，相差约 15 分；拆到最难的两档，只换手臂的 target 从 38.5–39.9 升到 69.8–74.3，整机替换从 33.9–38.6 升到 58.4–60.4。**均值掩盖的结构比均值本身更有信息量**：绝对末端位姿的失败高度平台特异——两个 GoogleRobot 平台 target 在 18 个单次运行格里最高只有 10.0，而同一列的 UR5e 平台 target 最低也有 58.6。它不是"略差的表示"，是在某些平台上完全不可迁移。同时它也不是可以照抄的默认值：gripper-only 一档换成末端系 delta state 是负收益（82.6→77.2、88.2→78.3），真机表上 (绝对末端位姿, 末端系 delta) 的整机迁移 16.3 低于 (绝对末端位姿, 世界系 delta) 的 21.3。另两条同向结果：固定 640K 轨迹预算下把 source 本体从 1 个铺到 512 个高约 18 分，但真机上这条曲线非单调（8 个 source 时手臂与整机迁移均低于单 source，到 512 才恢复）；在动作损失之外加 task-conditioned BBox 一类辅助目标把平均从 75.7 提到 77.7–82.3（BBox 最高），该组只在仿真上做过。

ZETA 的设定边界必须一并记，否则很容易把它读成比实际更强的结论：512 个 source 本体由**单一 Franka 式模板**按连杆缩放 0.7–1.3 程序化生成，不是 512 台真实机器人；评测物体就是 post-training 用的同一批实例，仿真场景与相机跨机器人严格一致；三个移动平台的底盘状态与底盘指令被排除在模型输入输出之外，"整机迁移"因此不含底盘控制；真机实验的预训练数据全部来自仿真，真机数据只用于 post-training（2 任务 × 50 demo）与评测，且真机每格 10 次 rollout、无重复训练、无标准差；任务进度被离散为 {0, 0.5, 1} 三档；无公开代码。

边界需一并记住。+10.8 是从 ap1 28.2 这个几乎无收益的起点量起的，跨设计的诚实比较是 ap8 的 39.0 对最好的单帧设计 vp1 的 34.4，即 +4.6，方向不变但幅度减半。换成 joint-angle state 后短历史的方向复现，但 K=8 时两条路线收敛（ap 36.2 对 vp 35.8，落在配对 bootstrap 噪声带内），路由规则的强度依赖 state 用的是哪套坐标。16 维 state 里有 7 维是 world frame 下的 mobile-base 位姿，作者自己点明这不能读作纯粹的内部本体感受，而 sp 增益最大的恰是大范围重定位一族——"把全局定位离散化塞进语言空间"是一条未被消融排除的替代解释。此外 se / fm 因硬件分配训练曝光偏低（作者据此声明不做 capacity-matched claim），多数对比依赖单一训练 seed，interface × depth 的 sweep 属探索性且未做多重比较校正，全部实验在仿真中完成、state 纯 kinematic 不含 force / tactile。以上数字经原文一致性核查，尚无独立复现。

### 横切议题四：冻结权重之上的适配层

八条路线共享一个默认假设——改进最终要落进权重。一批 2026 年的工作绕开了它：底座 VLA 全程不微调，改进落在权重之外的一层。此前已有三个实例：[[2607-RobustExecAgenticRL]] 在冻结 VLA 上用 PPO 训一个 {Execute/Retry/Repair/Reset} 调度层，[[2606-AffordanceFieldInterventio]] 做 test-time rollback，[[2608-HyMeS|HyMeS]] 把 memory 逻辑整体挪成一段可执行程序。2026-08 有两篇把这条线推到两个更极端的位置——把 critic 做到动作频率上，以及把记忆做成部署期在线更新的 in-context 证据。

[[2608-Zetta|Zetta]] 在冻结的 π0.5（LIBERO-Pro）与 GR00T N1.5（RoboCasa）外面套一层代码化的运行时 critic：监控在动作频率上读谓词信号，触发后交给 bounded retry 与恢复技能，而恢复程序本身由一个 evolutionary agent 从失败聚类里迭代生成，必须通过"在原簇内 100% 复现修复 + held-out ΔSR"的闸门才合入。RoboCasa 18 任务 macro-average 从 73.56% 升到 93.56%；LIBERO-Pro 总体 32.00%→71.13%，40 个 task-setting pair 里 32 对提升、8 对持平、无一回退；迁移到未参与演化的任务组仍有 64%→84%（取放）与 64%→80%（articulated）。

**这套数字的归因是空的，而且空得可以被一个便宜的实验补上。** 全文没有任何 component-level 消融，运行时 critic、恢复技能、验证闸门三者的贡献从未分离；baseline 没有拿到同等的额外执行步数、bounded retry 或外部工具（GraspGen、运动规划器、分割模型），于是"比冻结底座高 20 分"里有多少来自执行预算、多少来自演化出的程序，现有证据无法区分。两张成功率表里除它自己之外只有自家冻结底座，没有任何已发表方法或其他 harness 入表，而摘要宣称 SOTA；摘要的 headline 90.8% 是 Goal 两档的均值，同一实验的总体 macro-average 是 71.13%。监控信号里包含官方 grasp predicate，两个算法直接用官方任务谓词判定成功——这类信号在真机上不可得，论文未讨论。演化消耗的 rollout 总数、LLM 调用数与 GPU-hours 全文未报，而摘要用了"under our current rollout budget"这样的措辞。加速数字也不自洽：摘要的 11.1× 与实验节的 11.9× 互不一致，20.6× 吞吐是跨并发度比较（对照 @16 对自家 @64），同并发度下是 7.7× 与 12.8×。

[[2608-Zeva|Zeva]] 是同一条路的另一端：策略（Cosmos3 rectified-flow 动作头）在部署期全参数冻结，只有一份双时间尺度的因果记忆在线更新，把机器人自身交互的成败转成可检索的 in-context 证据（作者自称是首个在冻结策略下从自身物理交互做 in-context learning 的框架，尚未见独立验证）。真实化学实验室 ChemLab-Evo 三级难度上 83.3 / 70.0 / 57.32，分别领先各自的次优方法 6.6 / 5.0 / 12.59 分（三个次优各不相同）；RoboCasa365-Atomic5 平均 76.8% 对 Fast-WAM 72.4%。更有信息量的是两组内部对照：累计成功率从第 1 轮演化的 26% 升到第 4 轮的 73% 后走平；把检索到的经验换成跨任务最近邻，两个任务从 100% / 80% 变成 95% / 80%，而换成随机替换则掉到 55% / 45%——**起作用的是检索到的具体内容，不是"多给一段上下文"**。去掉两个记忆组件分别掉 10–20 分与 15–30 分。它与 Zetta 共享同一个缺口：没有把交互轮次配平的对照，因此在线记忆机制与额外交互预算这两个解释分不开。评测规模也小，ChemLab-Evo 每任务 20 个 episode，Atomic5 每任务 50 个。

这一族的共同形状是**改进不进权重，而进入权重之外一层可检查、可回滚的结构**——一段程序、一个调度器、或一份可检索的记忆。它的吸引力在于底座可以随时换新而适配层的逻辑是可读的；它的举证责任也因此比常规方法更重：适配层几乎总是同时带来额外的执行步数或交互轮次，而 Zetta 与 Zeva 都没有让冻结底座拿到同样的预算再比一次，RobustExecAgenticRL 则缺一个规则阈值 baseline。在这条对照补上之前，这一族的收益数字不能与"改权重"的方法直接并排读。

### 8 条路线的实质 trade-off

| 轴          | AR             | Flow/Diff      | Hierarchical   | Latent         | Reasoning       | Hybrid         | SoftPrompt   | WM/RL           |
| ---------- | -------------- | -------------- | -------------- | -------------- | --------------- | -------------- | ------------ | --------------- |
| 动作表达力      | 中（bin）<br>RVQ 后升 | 高              | 取决于低层          | 差可解            | —               | 高              | 高            | 高               |
| 推理频率       | 1-6 Hz         | 20-50 Hz       | 10-50 Hz async | 继承底层           | 显著更慢            | gate 决定        | 同 flow       | 1-7 Hz          |
| 数据利用       | action-labeled | action-labeled | VLM co-train 易 | 可用 video       | 需 CoT 数据        | action-labeled | multi-source | video/wearable  |
| 可解释性       | 中              | 低              | 高              | 低              | 高               | 中              | 中            | 部分              |
| VLM 生态复用   | 最佳             | 需 KI 隔离        | 高层复用           | 部分             | 高               | 复杂             | 好            | 中               |
| 代表作 rating | RT-2/OpenVLA 3<br>G0.5 3 | π0/π0.5/π0.7 3 | SayCan/π0.5 3  | LAPA 2/Genie 3 | Cosmos-Reason 2 | HybridVLA 2    | X-VLA 3      | π\*0.6 2/GEN-0 3 |

### 2025-2026 的 convergence 观察

跨路线可以读出几个**整合信号**：

1. **Flow matching + hierarchical + prompt expansion = 当前主流主干**（PI 系列 π0 → π0.5 → π\*0.6 → π0.7 + 追随者 GR00T N1 / X-VLA / SmolVLA / Motus）。
2. **离散 + 连续双监督成为标配，但纯离散路线并未出局**：π0.5 的 FAST discrete + flow continuous 双头、GenieReasoner 的 FACT、π0.7 的 Knowledge Insulation 都属于同一范式。[[2608-GalaxeaG05|G0.5]] 是同期唯一取消连续头的 foundation 规模工作——单个 decoder、共享 vocabulary、单一 next-token cross-entropy，把 CoT 与 RVQ 动作码放进同一条流，并在同数据同算力的真机对照上超过 π0.5 23.4 分。双监督究竟是必需的还是当前配方的产物，取决于 G0.5 这条路线能否在更大规模与更精细的视觉伺服上重复——它已知的短板正在后者（半透明低对比度表面 60% 对 π0.5 90%）。
3. **Scaling law 正在浮现**：GEN-0 的 7B ossification / $L(D)=(D_c/D)^{\alpha_D}$；GEN-1 继续外推（64% → 99%）；DreamZero 5B→14B 在 VLA 上 +29pp（vs 同规模纯 VLA 仍 0%）；[[2607-XiaomiRobotics1|Xiaomi-Robotics-1]] 提供 GEN 系之外第二条独立 data-scaling 曲线（unseen-env 26%→75%）且实测 data > model size。但学术社区数据规模与工业差距正在拉大。
4. **Cross-embodiment 从 "per-embodiment head" 迁移到 "input-side soft prompt / latent action"**（X-VLA / LAPA / DreamZero / π0.7 UR5e 迁移 / 2602-DM0 的 Embodied-Native）。
5. **Real-world RL 范式转变**：π\*0.6 的 advantage conditioning 是"绕开 flow matching PPO 难题"的工程胜利，被 RAMP / WorldVLALoop 沿用，2026-08 又添两个变体——[[2607-N0VTLA|ALTER]] 换掉"advantage 标签从哪来"（轨迹事件 + stage-relative progress 的离线构造，零额外环境交互），[[2607-WCM|WCM]] 换掉 critic 本身（预测性表征而非更长历史）；RL 的瓶颈正从"算法"移到"世界模型保真度 + reward 引擎"。
6. **Reasoning-action 从 shallow CoT 走向 unified discrete framework**（GenieReasoner FACT / Lumo-1 spatial action tokenizer / RoboBrain 2.5 3D+temporal / [[2608-GalaxeaG05|G0.5]] 的原生 CoT 与动作码同流）；"在 action space 做 reasoning" 的激进方向仍无实证——G0.5 让 CoT 与动作共享 likelihood 参数化，但推理本身仍发生在语言空间。与此同时另一个方向在收紧：语言在推理时不必被生成（[[2608-InContextVLA|VLA-Talker]] 注入 97.4 对生成 81.5、[[2608-StellaVLA|StellaVLA]] 推理时剥离语言 head，联合解码要付 36× 延迟），两条线合起来说明"reasoning 要不要在推理时展开"与"reasoning 用什么表示"是两个独立的设计选择。
7. **Memory 成为 long-horizon 明确子问题**：[[2603-MEM|MEM]]（video encoder + language memory，15min 任务）、[[2511-EchoVLA]]（dual PHC+hippocampus memory）、[[2507-StreamVLN]]（streaming KV-cache + voxel pruning）都在 2025-2026 集中出现；[[2607-LaMemVLA|LaMem-VLA]] 进一步把记忆从 policy-side 外挂挪进模型 native embedding 空间（短期视觉/长期动作双 vault，latent-native 相对 policy-side 条件化 +2pp）。[[2608-HyMeS|HyMeS]] 从相反方向切：记忆逻辑是离散组合式的，本就不适合在 weight space 学——motor skill 用 flow matching 模仿学习学进权重后冻结，memory 策略交给 coding agent 在**代码空间**通过 rollout 反馈迭代出一个可执行程序（constraint 选择 / 事件验证 / 记忆更新三类规则 + 显式 symbolic state），推理时由 symbolic memory 选出的可微 constraint 以梯度注入冻结 VLA 的 velocity field 实现 steering。示教预算因此随可复用 motor skill 数扩展而非随 history-dependent 配置数扩展，换目标颜色或按键次数只改代码。
8. **Deployment 工程栈成熟**：async inference（SmolVLA）、RTC（π0.7）、1-step flow matching（SnapFlow 274→83ms）、int4 量化（OpenVLA）、Λ-mask 防 shortcut（Xiaomi-Robotics-0）、paged attention（GEN-1）——"VLA 推理延迟是核心瓶颈"的共识正在推动专用优化技术涌现。2026-08 添上一类结构性做法：把整条辅助分支设计成推理时可整体删除，用 attention mask 或排他路由保证删除前后当前观测的表示一致（[[2608-WorldTokens|World Tokens]] 61.85 ms、[[2608-JEPAWAM|JEPA-WAM]] 85 ms、[[2608-MobileWAM|MobileWAM]] 938 ms 对 Motus 4950 ms、[[2608-StellaVLA|StellaVLA]] 的 demo 前缀 KV cache 把 183 ms 摊到 91 ms）。延迟不再靠事后压缩，而是在训练阶段就被架构约束住。[[2608-ZimaBlue|ZimaBlue]] 把这条推到 5B 视频主干上——Slow / Fast 异步解耦加蒸馏后 449.6 → 33.0 ms（13.6×），代价是 2.8 分成功率。而 [[2609-RealTimeExpoFT|Real-Time EXPO-FT]] 把延迟从工程指标改成优化目标本身：在 4 步延迟下，延迟无关的 RL 只把真机成功率从 18.0/30 推到 18.8/30，把执行时刻的 edit 写进 RL 后才到 29.0/30。**延迟到了某个量级就不再是可以事后补偿的成本，而是改变了应该优化什么。**
9. **执行期监控与恢复独立成层（2026-07 新 pattern）**：失败常源于"执行中途坏掉且回不来"而非"不会做"，恢复机制可与策略学习解耦。[[2606-RehearseVLA|RehearseVLA]] 的 instant reflector 暴露 VLA 评测对 oracle 终止信号的隐性依赖（禁用后 OpenVLA-OFT 掉 11.8pp）；[[2607-RobustExecAgenticRL]] 在冻结 VLA 上用 PPO 训 {Execute/Retry/Repair/Reset} 调度层、以回滚历史 nominal state 恢复执行（扰动设定 LIBERO-Long 平均 +39.2pp，但缺规则阈值 baseline、扰动类型为方法量身定做）；与 venue 回填的 [[2606-AffordanceFieldInterventio]] test-time rollback 同线。[[2608-Zetta|Zetta]] 把这一层做到动作频率上（谓词监控 + bounded retry + 由 evolutionary agent 从失败聚类迭代出的恢复程序，RoboCasa 73.56%→93.56%、LIBERO-Pro 32.00%→71.13%），[[2608-Zeva|Zeva]] 则把它做成部署期在线更新的因果记忆。这一族已有五个实例，共同的证据缺口是预算配平（见「横切议题四」）。
10. **下游适配配方成为受控研究对象**：[[2607-LoRAVLA]] 给出 π0 工业微调的实证 recipe——LoRA r=32 + SigLIP 全量微调持平 FFT（VRAM 36.2→10.8 GiB），embodiment adaptation 的瓶颈在视觉 domain shift 而非动作层；[[2607-DART]] 把适配数据的价值从"重学任务"改写为"测量 domain direction"——source/target one-shot update vector 相减 + SVD subspace 过滤，一条 target demo 把 domain shift 迁移到全部任务（LIBERO viewpoint shift 79.1% vs one-shot FT 31.5%，真机 UR10e 81.7%）。
11. **UMI 从 pre-training 进入 target-task post-training，但 data equivalence 尚未成立**：[[Papers/2607-HiFiUMI|HiFi-UMI]] 在 StarVLA-QwenPI、OpenPI-π0.5、LingBot-VA 三种 backbone 上报告 UMI−teleoperation aggregate gap −2.5 / +3.1 / −0.6pp，证明整套高保真采集系统足以形成可部署 policy；然而每任务 3,200 条 UMI 对约 300 条 teleoperation，且 evaluation-scene exposure 不同，因此不能把 pipeline parity 解释为 equal-sample parity。
12. **"多预测一路未来 / 多接一路感知"的收益归因开始被自家消融反噬（2026-08 新 pattern）**：三篇彼此独立的工作给出同向负信号——[[2607-STWAM]] 的 DINO-only 未来分支在 LIBERO-Plus 只有 39.7%，**低于**纯 VAE 的 Fast-WAM 51.5%；[[2607-N0TWAM]] 去掉反应式触觉通路比去掉预测式通路损失更大，且最大单因素是预训练数据量而非任一触觉通路；[[2607-WCM]] 用 $\lambda=0$ 的历史 ViT 对照证明了"预测目标有用"，却全文没有任何 value 估计精度指标，无法排除"预测 loss 只是防表征塌缩的正则化"这条同样兼容的解释。三者的缺口是同一个：缺同 backbone、同算力、逐目标移除的对照。在补上之前，"新增预测通道 → 表征更好 → 动作更好"这条因果链目前只有相关性证据。[[2608-VLAProprioception]] 给出这类对照的一个可搬运样板，并且同时落在天平两侧：固定 backbone / 数据 / 协议只动 state 接口，当前帧这一路"多接一路感知"在 45 个任务上五个接口只有一个区间排除 0（54.6 → 55.7–57.7）；但换成 8 帧有序历史后，相对"用当前帧副本填满同样 slot 数"的对照仍有 +8.2 且区间排除 0。通道有没有用要按其承载的内容判，而不是按"多了一路"判。同月的三篇 world-model 训练期工作把这个缺口补上了一段：[[2608-WorldTokens|World Tokens]] 在同 backbone 下只改瓶颈的排他性（VLM 旁路 97.0 → 94.1）与 anchor 的构造（Canny anchor 91.5 反而低于不接 world model 的 95.0），[[2608-JEPAWAM|JEPA-WAM]] 逐目标拆开当前帧与未来帧两项预测（joint 79.2 / 只预测未来 77.3 / 只对齐当前 77.0），[[2608-MobileWAM|MobileWAM]] 把 belief 的传递方式当变量（MLP 传 46.3 低于完全不传的 50.2，transformer 传 58.2；30 层全接 37.1 低于均匀 4 层的 58.2）。这些消融都指向同一件事：负结果不出现在"要不要多一路"上，而出现在这一路以什么形状、在哪一层接进主干。不过三篇的比较基线仍沿用论文报数而非重跑，因果链的另一半——同算力下把预测目标换成等参数量的无意义正则——还是没人做。
13. **接口的位置与形状升格为一等设计变量（2026-08 新 pattern）**：过去一年的 VLA 设计讨论集中在"用什么模块"，2026-08 有六篇彼此无引用关系的工作把变量换成了"模块接在哪一层、以什么形状接、推理时留不留"，并且各自给出同 backbone 的对照。[[2608-GSRParaVLA|GSR-ParaVLA]] 定位到语言语义在架构内被动作通路读不出；[[2608-VLAProprioception]] 只动 state 接口就分出当前帧无效、有序历史有效；[[2608-WorldTokens|World Tokens]] 让 256 个 world token 成为 VLM 通往 action expert 的**唯一**入口，开一条旁路就掉 2.9 分；[[2608-MobileWAM|MobileWAM]] 用非对称 mask 让 video token 看不见 action token，从而把重型 backbone 降格成可缓存的当前帧编码器；[[2608-InContextVLA|VLA-Talker]] 只把 loss mask 从"证据 + 动作"改成"仅动作"就换来 7.7 分；[[2608-CofactVLA|CofactVLA]] 把干预放在梯度与第 15/16 层的协方差上而不是新增模块。共同的方法论后果是，"某模态/某信号对 VLA 有没有用"这个问法本身不成立——同一路信息接在不同位置会给出相反结论，报告结论时必须连接口一起报。2026-09 有两组把这条推得更远：[[2609-LatentInterfaceTraining|LIT]] 把瓶颈从"多模态入口"移到视觉入口本身，让 K=100 个 latent token 成为 action expert 唯一的视觉来源并用动作块末端位姿重建监督它，四种架构的 LIBERO-Plus 全部上升，而同预算下只加位姿监督或只照搬分阶段训练分别只有 65.45 与 65.46；[[2609-OpenWAM|OpenWAM]] 把 attention mask 当作可扫描的设计变量，发现最优 mask 在具身预训练前后会翻转——接口的最优解不只依赖架构，还依赖训练阶段。
14. **受控设计空间扫描本身成为一类产出（2026-09 新 pattern）**：与"提一个新方法刷一个榜"并行，出现了一批把自己定位为"扫一遍设计空间并公开每一条臂"的工作。[[2608-VLAProprioception]] 固定 π0.5 只动 state 接口；[[2609-OpenWAM|OpenWAM]] 固定数据与配方逐轴扫 encoder / system 组合 / attention mask / 去噪同步性 / 预训练策略，并以 Apache-2.0 释出 46 个覆盖**每一条消融臂**的 checkpoint；[[2609-ZETA|ZETA]] 固定 backbone 与评测协议只改 state/action 参照系与 source 本体数量，且先把"zero-shot 跨本体"拆成 strict 与 pretrain-exposed 两档口径再开测。这类工作的产出不是排名而是**条件化的结论**——最优 mask 在具身预训练前后翻转、最优 state 接口随历史长度翻转、最优参照系在 gripper-only 一族上反号——因而比同期多数 SOTA 论文更能被后人复用。它们的共同弱点也一致：扫描本身多为单点估计、无 seed 与误差棒（OpenWAM 全文无任何误差棒，ZETA 的真机档不做重复训练），于是若干格上的"翻转"究竟是结构还是噪声仍然存疑。

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
| LIBERO                       | 4 suite × 10 task 短程    | 4-suite avg SR     | **99.4%** ([[2607-ABotM05\|ABot-M0.5]], WAM) <br>98.9% ([[2608-GalaxeaG05\|G0.5]]，纯 AR) <br>98.8% ([[2608-StellaVLA\|StellaVLA]]) <br>98.7% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]] 4.7B) <br>98.5% ([[2608-CofactVLA\|CofactVLA]]，每 suite 仅 10 episode) <br>98.2% ([[2608-WorldTokens\|World Tokens]] 2B 无 embodied pretrain / EO-1) <br>98.1% ([[2510-XVLA\|X-VLA]] 0.9B) <br>97.4% ([[2608-InContextVLA\|VLA-Talker]]，3 seed) <br>96.7% ([[2608-JEPAWAM\|JEPA-WAM]] 0.5B；作辅助 loss 加到 π0.5 上 96.9→97.8) |
| LIBERO-Long                  | 长程子集                    | SR                 | 97.6% ([[2512-Motus\|Motus]] / [[2510-XVLA\|X-VLA]] 并列) <br>97.2% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                       |
| LIBERO-Plus                  | 7 类扰动的鲁棒性套件（视觉/语言/布局/传感器噪声等） | overall SR | 零样本：**72.8%** ([[2607-STWAM\|ST-WAM]]，对照 Fast-WAM 51.5——baseline 引自第三方 robustness study 而非本文重跑) <br>RL 微调设定（one-shot SFT + ~250 步）：74.0 / 73.7 / 72.8 ([[2607-WCM\|WCM]] on OpenVLA-OFT / π0.5 / π0，对照各自 20k 轨迹 Full-SFT 71.7 / 72.9 / 71.2)。两组设定不同，不可直接横比 <br>2026-08 零样本组：**86.3** ([[2608-JEPAWAM\|π0.5+JEPA]]，对照 π0.5 84.5) <br>85.1 ([[2608-StellaVLA\|StellaVLA]]，camera viewpoint 轴 +23.5) <br>79.2 ([[2608-JEPAWAM\|JEPA-WAM]] 0.5B，无 robot-policy pretrain 组最好) <br>69.1 ([[2608-CofactVLA\|CofactVLA]]；每任务 1 episode，Language 轴 71.8 落后 OpenVLA-OFT_m 81.0) <br>2026-09 组：**92.0** ([[2608-ZimaBlue\|ZimaBlue]] SFT 后；零样本 86.7，Camera 轴 58.1 低于 π0.5 78.4) <br>79.67 ([[2609-LatentInterfaceTraining\|LIT]] on π0.5，对照同预算的 68.97；另三架构 71.92 / 60.63 / 86.89，28 组"架构×扰动"中 26 组提升) <br>69.2 ([[2609-OpenWAM\|OpenWAM]]-α，Camera 33.8 / Noise 39.8 为全表垫底区) <br>**口径警告**：LIT 的 Overall 是七轴非加权均值（仓库自陈 task-weighted 约低 2 分），OpenWAM 的 Avg 按试次加权且表头未说明，两者不可相减；LIT 明写不微调预训练 checkpoint，故其 baseline 与已发表的微调结果不可直接比 |
| LIBERO-Para                  | LIBERO-Goal 的指令改写集：4,092 条改写 episode（870 Act / 259 Obj / 2,963 Comp） | Full Para SR / PRIDE | Full Para **76.0** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]]) <br>75.59 / PRIDE **70.4** ([[2608-GSRParaVLA\|GSR]]-π0.5) <br>70.94 / 62.0 (GSR-VLA-Adapter，Native 46.82 / 36.7) <br>49.12 / 41.4 (GSR-SmolVLA，Native 4.47 / 2.6) |
| UniVTAC                      | 第三方视触觉操作基准（8 任务）      | avg SR             | **84.5** ([[2607-N0TWAM\|N0-TWAM]]) <br>83.1 ([[2607-N0VTLA\|N0-VTLA]]，8 任务中输掉 3 项) <br>67.1 (InternVLA-A1) |
| CALVIN ABCD→D                | In-dist 长程              | Avg task length /5 | **4.80** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                                                                                |
| CALVIN ABC→D                 | OOD 长程                  | Avg task length /5 | **4.75** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]], vs 次优 FLOWER 4.53)                                                                             |
| SimplerEnv Google Robot VM   | Real-to-sim             | avg SR             | **85.5%** ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]]) <br>80.4% ([[2510-XVLA\|X-VLA]])                                                              |
| SimplerEnv Google Robot VA   | Real-to-sim             | avg SR             | 75.7% ([[2510-XVLA\|X-VLA]]) <br>74.7% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]])                                                                  |
| SimplerEnv GoogleRobot（未拆 VM/VA） | Real-to-sim，BridgeV2+Fractal 联合训练 | avg SR | 82.1% ([[2608-WorldTokens\|World Tokens]]，对照 Qwen-GR00T 75.3 / SpatialVLA 75.1)——原文未按 VM/VA 拆分，不与上两行同口径 |
| ManiSkill-HAB SetTable       | 7 子任务 whole-body mobile manipulation | avg SR（3 次评测均值） | **73.0%** ([[2608-MobileWAM\|MobileWAM]]，对照 AnchorVLA 64.0 / AC-DiT 55.6) <br>注：[[2603-SGVLA\|SG-VLA]] 在同 benchmark 报 0.73 但子任务切分与观测模态不同（multi-view RGB+D），两个 73 不可相减；MobileWAM 未把它列入主表 |
| VLA-Arena                    | 公开榜单（截至 2026-08-01）  | overall score      | **0.63** ([[2608-StellaVLA\|StellaVLA]]) <br>0.44 ([[2504-Pi05\|π0.5]]) <br>0.41 (Evo-Depth) / 0.39 ([[2502-OpenVLA-OFT\|OpenVLA-OFT]]) |
| RoboMemArena（作者修正 12-task protocol） | memory-dependent 操作四类：transferring / counting / sequence / occlusion | CSR / TSR | **66.2 / 60.1** ([[2608-HyMeS\|HyMeS]]，同权重 π0.5 52.5 / 41.3) <br>61.7 / 45.6 (PrediMem；occlusion 类 CSR 38.3 **低于** reactive π0.5 的 50.4) <br>协议由作者按"π0.5 有 motor skill 但因缺 history 失败"重筛，天然偏向记忆注入类方法 |
| RoboCasa-GR1                 | 24 桌面任务（论文只展示 4 项代表） | avg SR             | 59.5 ([[2608-InContextVLA\|VLA-Talker]]；展示的 Bottle / Cup / Milk 三项均非最优) |
| SimplerEnv WidowX            | Real-to-sim             | avg SR             | **95.8%** ([[2510-XVLA\|X-VLA]], vs 前 SOTA MemoryVLA 71.9) <br>87.3% ([[2608-GalaxeaG05\|G0.5]]，SimplerEnv-Bridge 4 任务；其 abstract 只对比 π0.5 57.1) <br>79.2% ([[2602-XiaomiRobotics0\|Xiaomi-Robotics-0]]) <br>71.5% ([[2608-WorldTokens\|World Tokens]]，BridgeV2+Fractal 联合训练；stacking 仅 32.0) <br>*另一子集*：72.4% ([[2608-InContextVLA\|VLA-Talker]]，4 个 held-out WidowX 任务，Carrot 56.3 低于四个基线) |
| RoboCasa Kitchen Easy / Hard | 100 photorealistic 厨房任务 | SR                 | 70.0 / 39.0 ([[2510-XVLA\|X-VLA]])                                                                                                                    |
| RoboCasa365                  | 365-task 移动操作 pretraining 设置 | avg SR      | **57.4%** ([[2607-XiaomiRobotics1\|Xiaomi-Robotics-1]], Composite-Unseen 32.1%) <br>49.5% ([[2608-ZimaBlue\|ZimaBlue]]，Composite-Unseen 16.5 对 ABot-M0.6 的 7.9；多数 baseline 取自官方 leaderboard 而非作者复跑) <br>46.6% ([[2607-ABotM05\|ABot-M0.5]] +Condensed Memory, Composite-Unseen 7.9%) <br>38.2% ([[2609-OpenWAM\|OpenWAM]]-α，实为该榜第 3；论文自称"与最佳仅边际差距"而实际落后 19.2 分) <br>*Atomic 子集口径*：76.8% ([[2608-Zeva\|Zeva]] 在 Atomic5 五任务上，对照 Fast-WAM 72.4%，每任务 50 episode) <br>*另一套口径*：[[2608-VLAProprioception]] 用 45 个 atomic（分三族各训 category expert）+ 20 个 composite 子集，macro 57.7% / 39.0%，与上两行的 365-task 联合训练设置不可横比 |
| VLABench                     | VLA-centric 综合          | Avg.PS             | 51.1 ([[2510-XVLA\|X-VLA]])                                                                                                                           |
| RoboTwin 2.0 Randomized      | 50-task bimanual Aloha  | avg SR             | **94.3%** ([[2608-ZimaBlue\|ZimaBlue]]，Clean 94.7 / 平均 94.5) <br>94.2% ([[2607-ABotM05\|ABot-M0.5]]) <br>92.8% ([[2608-GalaxeaG05\|G0.5]]，clean 93.7 / 平均 93.3) <br>92.14% ([[2607-FlowWAM\|FlowWAM]]) <br>87.02% ([[2512-Motus\|Motus]]) <br>72.84% ([[2510-XVLA\|X-VLA]]) <br>43.84% ([[2504-Pi05\|π0.5]]) <br>*另一套口径*：[[2608-JEPAWAM\|JEPA-WAM]] 只在 Clean 上训练、20 任务，Clean 79.9 / Random 36.9（π0.5+JEPA 84.6 / 37.5，对照 π0.5 75.4 / 37.2）——Random 列几乎不动，与上面的 randomized-训练数字不可横比 <br>*设计空间扫描口径*：[[2609-OpenWAM\|OpenWAM]] 固定数据与配方只换 video backbone 得 1.3B 90.14 / 2B 91.64 / 5B 92.39 / 14B 93.79，四种 attention mask 得 87.41 / 87.63 / 92.39 / 92.15；这些是消融臂而非最优配置，不入 SOTA 排序 |
| BiCoord                      | 18 bimanual 长程紧耦合       | single-task avg SR | 46.4% ([[2410-Pi0\|π0]], 次 [[2502-OpenVLA-OFT\|OpenVLA-OFT]] 40.5 / RDT 39.5 / DP 33.1) <br>27.2% ([[2410-Pi0\|π0]] multi-task, 相比 single-task −19pp) |
| InstructMove                 | 构造上 text-indispensable 的取放：每 episode ≥2 个可执行候选、仅 1 个与指令一致；四任务族（跨类 / 同类属性 / 空间关系 / 组合） | 分阶段分数（Reach 相对**指令一致**目标定义） | 每任务 100 条示教微调后：[[2504-Pi05\|π0.5]] 0.69 / 0.71 / 0.30 / 0.52（四族），GR00T N1.7 0.47 / 0.41 / 0.25 / 0.19，Motus 0.26 / 0.43 / 0.26 / 0.16，[[2410-Pi0\|π0]] 0.19 / 0.24 / 0.19 / 0.19（[[2608-InstructMove\|InstructMove]]）<br>空间关系一族最低；Lift 普遍 0.01–0.17，训练充分性未排除 |
| LIBERO-Mem                   | memory-dependent 操作，区分 completion / relaxed SR / strict SR | 三项 | **76.29 / 63.00 / 11.83** ([[2609-2AM\|2AM]]，对照同 backbone 同观测的自建 π0 复现 70.79 / 37.42 / **12.25**——strict 略降) <br>53.72 / 19.42 / 7.25（同方法只留语言、去掉 2D 坐标提示）：坐标提示在 relaxed 上 +43.58、strict 上仅 +4.58 |
| LIBERO-Pro                   | LIBERO 任务在 T / S 两种设定下各自扰动，40 个 task-setting pair | macro-avg SR | **71.13%** ([[2608-Zetta\|Zetta]]，冻结 π0.5 基线 32.00%；32 对提升、8 对持平、无回退) <br>同篇 RoboCasa 18 任务 73.56%→93.56%（冻结 GR00T N1.5）<br>两组 baseline 均未获得同等额外执行步数、bounded retry 与外部工具，增益无法归因到具体组件 |

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
| [[2608-GalaxeaG05\|G0.5]] matched-compute 微调     | Galaxea R1-Lite / R1-Pro，6 个 task-embodiment 设定 | avg SR / process score | **76.7% / 129.2** ([[2608-GalaxeaG05\|G0.5]]) <br>53.3% / 105.2 ([[2504-Pi05\|π0.5]]) <br>24.4% / 68.9 (GR00T-N1.7)——三者同数据、各 16 H20、同 wall-clock 4-10 h、同观测与控制栈，是本表唯一算力对齐的架构对照 |
| 2025 BEHAVIOR Challenge（50 长程家务移动操作）        | 仿真挑战赛                       | challenge score                    | **0.3136** ([[2608-GalaxeaG05\|G0.5]] 4 epoch；1 epoch 已 0.2904) <br>0.2626 ([[2504-Pi05\|π0.5]] 4 epoch) <br>0.2605 (冠军方案 RLC) |
| DROID held-out zero-shot（10 任务）                | Franka                        | SR                                 | **82.5%** ([[2608-GalaxeaG05\|G0.5]]，DROID 不在预训练；10/10 任务胜) <br>57.5% (π0.5-DROID) <br>52.0% (MolmoAct2-DROID)；反例见半透明低对比抽屉 60% vs π0.5 90% |
| Galaxea R1 Pro 单臂抓放（4 任务 × 24 trial）         | R1 Pro 右臂 + 头戴 fisheye        | SR (96 trials)                     | **76.0%** ([[2608-WorldTokens\|World Tokens]]) vs 59.4% (matched Qwen-GR00T) |
| AgileX Cobot Magic 双臂 5 任务 ID / OOD            | 双臂                            | normalized completion              | **90.3 / 84.7** ([[2608-JEPAWAM\|π0.5+JEPA]]，对照 π0.5 77.5 / 72.5) <br>59.8 / 54.2 ([[2608-JEPAWAM\|JEPA-WAM]] 0.5B，对照 π0 51.8 / 22.5)；每任务仅 10 rollout |
| AgileX PiPer 4 任务标准 / 自设 OOD                   | 单臂                            | SR (~100 trial)                    | **90.8% / 75.8%** ([[2608-CofactVLA\|CofactVLA]]) vs 71.0% / 23.5% ([[2504-Pi05\|π0.5]])；OOD 为同四任务上的 nuisance 变化，且该 setting 无任何组件消融 |
| ARX Lift2 whole-body 5 任务（horizon 递增）         | 移动双臂                          | SR                                 | 55 / 35 / 25 / 20 / 15% ([[2608-MobileWAM\|MobileWAM]]) vs 35 / 25 / 10 / 10 / 0% (同数据微调的 [[2504-Pi05\|π0.5]])；论文未报 trial 数与示教条数，初始条件在训练分布内随机化 |
| SO-101 memory-dependent 3 任务                     | 单臂                            | TSR (35 trials/方法)                | **57.1%** ([[2608-HyMeS\|HyMeS]]) vs 25.7% (冻结的同权重 π0.5) |
| AgiBot G1 桌面 8 子任务                             | 双臂（backbone 换 JoyAI-RA-0.1）  | 单任务 / 多任务 avg SR（20 trial/子任务） | 58.1 / 45.0 ([[2608-InContextVLA\|VLA-Talker]]) <br>41.9 / 29.4（同证据但生成 CoT） <br>41.9 / 28.1 (baseline)——生成臂相对 baseline 单任务零增益 |
| Franka 12 任务（对 DROID 后训练全部 held-out）      | 7-DoF Franka                   | task-macro SR（10 rollout/任务）    | **77.8%** ([[2608-ZimaBlue\|ZimaBlue]] 全配置) <br>66.9%（去掉 120K 视频档）<br>46.1%（再去掉 60K 视频档）<br>36.1%（仅 Wan2.2-TI2V-5B 初始化基线）——四档为累加式预训练，非小时数或算力配平的替换对照 |
| 单臂真机 6 任务（每任务 100 条示教微调）             | 单臂                            | 成功试次 /120（20 trial × 6）        | **99/120（82.5%）** ([[2609-OpenWAM\|OpenWAM]]-α) <br>93/120（77.5%，LingBot-VA） <br>66/120（55.0%，[[2504-Pi05\|π0.5]]）；灵巧手平台（本体与 action space 均不在预训练混合中）四任务 × ID/OOD × 两指标共 16 组全面超过 π0.5 |
| YAM 双臂 3 任务 ID / 光照 / 相机 / 干扰物            | 双臂（底座为 MolmoAct2）          | aggregate SR                      | ID 74.7→88.0、光照 53.3→70.0、相机 30.0→46.7、干扰物 50.0→63.3（[[2609-LatentInterfaceTraining\|LIT]] 对架构匹配的 MolmoAct2）；300 条示教训单一多任务策略，ID 每任务 25 rollout、每个 OOD 条件每任务 10 rollout |
| DROID 单臂 4 任务在线 RL（在线数据 ≤10 min）        | Franka（π0.5+LoRA，三任务人为注入 100 ms 延迟） | 成功试次 /30                | **29/30** ([[2609-RealTimeExpoFT\|Real-Time EXPO-FT]]) <br>25/30 (EXPO-FT w/RTC) <br>18.8/30（延迟无关的 EXPO-FT）<br>18.0/30 (SFT w/RTC) <br>12.5/30 (SFT)；每格单次 30 trial，无 seed 无误差棒 |
| ChemLab-Evo（真实化学实验室，三级难度）              | ARX 单臂                        | atomic / short / process（20 episode/任务） | **83.3 / 70.0 / 57.32** ([[2608-Zeva\|Zeva]]，冻结策略 + 在线更新的因果记忆；三项的次优各为 Fast-WAM / LingBot-VA / Cosmos3-Nano，领先 6.6 / 5.0 / 12.59) <br>累计成功率第 1 轮 26% → 第 4 轮 73% 后走平；无交互轮次配平的对照 |

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
| 28 个具身 benchmark 合集（作者重跑全部对照） | 空间 / affordance / 点定位 / 具身问答 | overall average | **72.5** ([[2609-PhysBrain15\|PhysBrain 1.5]] 8B，开源最高，开源内 14 项第一) <br>73.3 (GPT-6-Astra) / 73.0 (Gemini 3.6 Flash)——闭源按各自最低官方 thinking 档评测 <br>67.9 (Claude Opus 5) / 66.0 (Hy-Embodied-VLM-1.0 30A3B，开 thinking) <br>10 个点定位 benchmark 改用自研 micro-averaged F1，分数与原论文口径不同；SFT 混合含多个被评测 benchmark 的同族训练数据 |

### 数据量级核心数字

- **OXE : LLM corpus ≈ 1 : 200,000**（[[2507-VLATokenizationSurvey]] §12）——VLA 与 LLM 能力鸿沟的最硬物质约束。
- **Generalist AI wearable 数据：500K hr，10K hr/week 增长**（[[2604-GEN1]]）——单家公司 proprietary 数据 ≥ 整个学术社区开源 robotics 数据总和；1 h robot data fine-tune 即可达 99% SR。
- **π0.5 co-training 中 97.6% 来自非目标平台**（[[2504-Pi05]]）——cross-embodiment 在大 mix 下成为 free transfer 而非 noise 源。
- **[[2602-GigaBrain05M\|GigaBrain-0.5]] pretraining = 61% 合成 + 39% 真机**（10,931 hr total，6,653 hr GigaWorld 合成）——合成数据首次在 VLA pretrain 占多数，边际收益尚未独立 ablate。
- **HiFi-UMI full / released corpus = 20K+ / 2K 小时**（[[2607-HiFiUMI]]）——4,000-hour pre-training 在 StarVLA-QwenPI 上使 10 个 unseen tasks 的 mean OOD action error −41%，并在相同 task-specific data 下把 real-robot success +18.1pp；后者只在一个 backbone 上验证。
- **视频段数作为第三条尺度轴：60K → 120K 段无动作视频**（[[2608-ZimaBlue]]）——12 个真机任务上 Standard 只 +5.0 而 Perturbed +22.5，买到的主要是扰动鲁棒性；全文没有把总小时数或算力配平后用 action-free 视频替换 action-labeled 数据的对照，因此不能读成"视频比动作标注更划算"。
- **具身预训练监督可以完全不含机器人数据：约 30,000 小时人类视频**（[[2609-PhysBrain15]]）——机器人轨迹（约 2,620 小时）只出现在 SFT 阶段；该配置能把统一离散接口训到 8B 并拿下开源最高的具身理解分，但动作侧没有任何闭环成功率。
- **[[2604-BiCoord\|BiCoord]] STI = 42.16% vs RoboTwin 2.0 / RLBench2 ~8–11%**——首次用标量同时刻画"空间近 + 时间并行"，暴露现有 bimanual benchmark 的伪协同（RLBench2 SMP 97% 但 ARD 115%——并行 ≠ 协同）。

### Benchmark 饱和度与评测 crisis

- **LIBERO 已近饱和**：4-suite avg 98.7 / 98.2 / 98.1 差距在噪声量级；long-horizon sub-suite 仍可分辨（[[2602-XiaomiRobotics0\|Xiaomi]] 97.2 vs 次优 FLOWER 94.9）。2026-08 并入的 6 篇全部落在 96.7-98.9 这个 2.2 分区间里，架构差异之大（纯 AR 的 G0.5、demo 检索的 StellaVLA、训练期 world model 的 World Tokens、0.5B 的 JEPA-WAM）与名次之近形成反差——这个 benchmark 已经不能分辨它们在分辨什么。
- **评测预算与断言精度脱钩**：[[2608-CofactVLA|CofactVLA]] 把这条推到极端——标准 suite 每 suite 10 episode、LIBERO-Plus 每任务 1 episode、全文无 seed 无误差棒，却据此声明 98.5 对 X-VLA 98.1 的 +0.4pp 与 LIBERO-Plus 69.1 对 67.9 的 +1.2pp。在这个预算下 1pp 约等于每 suite 一次 trial 的翻转，"最高 total" 只在自选 baseline 集合内成立（已记录的 [[2606-ERVLA]] 86.9、[[2607-STWAM]] 72.8、[[2606-MergeVLA]] 72.4 均更高，训练协议各不相同）。同一个 π0 baseline 在两篇论文里记成 53.6 与 56.3，说明 LIBERO-Plus 的数字在流通中没有统一协议。对照面是 [[2608-InContextVLA|VLA-Talker]] 的 3 seed + Welch 检验，它自己也承认这套统计只覆盖自建的三条臂，表内其余方法仍无方差。
- **LIBERO 的语言鉴别力不足（比饱和更严重）**：[[2607-TurboVLA]] 把语言指令替换为 task-ID embedding 后仅掉 2.3pp（97.7→95.4），说明该 benchmark 主要测闭集任务执行而非指令理解。凡是把收益归于语言/语义先验的方法（VLM backbone、reasoning trace、language intermediate），在 LIBERO 上的提升都不构成对该归因的支持；[[2604-DAERT]] 的 "no action" probe（π0.5 仍 54.9% 成功）与之互补——一个说语言可被无损替代，一个说语言可被直接忽略。2026-08 补上第三个方向与一条廉价补救：LIBERO-Para 只把 canonical 模板改写成同义表述（不换物体、不换场景、不换动作），就把同一批模型从 72-98% 打回 4-77%（[[2608-GSRParaVLA]]）——**鉴别力不是消失，而是被 canonical 模板掩盖**，恢复它的代价是 4,092 条改写指令而非新建环境。该协议自身的边界也随之明确：LIBERO-Goal 的 10 个任务共享同一视觉场景，改写不变的句子编码器与 10 路任务码在其上仍然分不开，因此它能证伪"语言被用到了"，不能证实"语言被理解了"。
- **构造性的补救已经出现，但它自己也需要被测量**：[[2608-InstructMove|InstructMove]] 把"指令不可省"从事后诊断改成 benchmark 的构造约束（每 episode ≥2 个可执行候选、仅 1 个与指令一致），并把 Reach 定义在指令一致的目标上，于是"抓得漂亮但抓错物体"被记为失败。这是目前最直接的修法。但它的 text-indispensability 仍是构造性主张而非测量结果——全文没有报过去掉语言后 target-conditioned Reach 是否掉到 6 选 1 的随机水平；对既有 benchmark 的指控也只靠一张设计目标对照表加引用他人结果，作者没有在任何既有 benchmark 上自跑 language-blind 策略。
- **同一指标的聚合口径在论文之间不一致**：LIBERO-Plus 的 Overall，[[2609-LatentInterfaceTraining|LIT]] 用七轴非加权均值（其仓库自陈按 task 加权约低 2 分），[[2609-OpenWAM|OpenWAM]] 按试次加权且表头完全不说明（α 的七列非加权均值 71.33 而印出 69.2）。跨论文相减这个总分是无效操作，而目前几乎所有鲁棒性对比表都在这么做。
- **开环领先与闭环落后可以出现在同一篇论文里**：[[2608-QwenDrive|Qwen-Drive-1.0]] 在开环 WOD-E2E 上 RFS 7.91 高于对照的 RL 版本，同一篇的闭环 AlpaSim 却只有 0.16 / 0.37，低于 Alpamayo-R1 的 0.36 / 0.58 与 Alpamayo-1.5 的 0.23 / 0.45；其 RL 把 off-road 从 24.0% 砍到 12.0%，代价是 progress 54.0%→48.0%、all-event 因果事件率 38.0%→41.0%。**开环指标上的名次不预测闭环名次**，而 VLA 侧大量 real-to-sim 与轨迹误差评测与这里的开环指标同构。
- **自宣告终止是一个尚未被计价的能力**：[[2609-DroneCATS|DroneCATS]] 把任务结束的判定权交给模型后，最好模型的 oracle 成功率与实际成功率差出 55 个百分点（90% 对 35%）；成功判据本身可选——只按首次宣告计分会把 182 个成功中的 95 个翻成失败。现行 manipulation benchmark 普遍用环境谓词判定成功，因此从未测过这项能力，而它在部署中是必需的。同篇的重复实验给出另一个量级参照：同一模型三次重飞 46 / 50 / 35（满分 80），单格标准差约 9–13 个百分点。
- **鲁棒性榜单的 baseline 多为引用而非重跑**：[[2607-STWAM]] 的 LIBERO-Plus 表明确标注 baseline 数字引自第三方 robustness study，其 LIBERO / RoboTwin 两表则完全未交代 baseline 来源；这类跨表混用使"同 backbone / 同数据量"无法从原文确认。[[2609-OpenWAM|OpenWAM]] 把这条推到极端——一篇以"公开全栈、可复现"为卖点的 study，八个 benchmark 的全部 baseline 分数既未说明是复跑也未说明是引用。正面样板是 [[2609-LatentInterfaceTraining|LIT]]：它明写自己不微调预训练 checkpoint、action expert 随机初始化，因此自家 baseline 与已发表的微调结果不可直接比——这一句话就让它的 79.67 不会被误读成对 [[2606-ERVLA]] 86.9 的挑战。鲁棒性子集（LIBERO-Plus / LIBERO-Para）正在承接主表的比较功能，若沿用主表的引用习惯，饱和 benchmark 的可比性问题会原样复制到它们身上。
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
- **第三条尺度轴出现，而"data > size"的适用范围随之收窄（2026-09）**：[[2608-ZimaBlue]] 把无动作视频段数当独立尺度轴，60K→120K 在 12 个真机任务上 Standard 只 +5.0 而 Perturbed +22.5；[[2609-OpenWAM]] 则显示固定数据与配方时生成式视频主干仍按参数量单调买分（1.3B 90.14 → 14B 93.79）。"扩数据比扩参数划算"这个判断长在 action-labeled 数据上，换成视频主干这一段就不成立。两边共同缺的实验是同一个：没有任何一篇做过小时数或算力配平后的**替换**对照——用 X 小时 action-free 视频顶掉 Y 小时 action-labeled 数据再看分数。在此之前"视频更便宜"是价格常识而不是测量结果。

### 2. Real-world RL for large VLAs

[[2511-PiStar06]] 的 Recap 首次在 4B+ flow matching VLA 上跑通真实 RL 自改进；[[2602-GigaBrain05M]] 把它形式化为 RAMP 的特例并加 future visual latent；[[2602-WorldVLALoop]] 用 closed-loop world model 迭代。仍未解：
- 只覆盖 episode-level sparse reward；dense / preference-based reward 未系统探索。
- **可 RL 修复 vs 结构性 failure**（hardware / perception bug）未区分。
- 与 Upside-Down RL / Decision Transformer / CFGRL 的理论联系尚不完整。
- RL 的 compute scaling 和 improvement 曲线不清楚（π\*0.6 只跑了 2 轮迭代，box assembly 第 3 轮会饱和还是继续提升？）。
- **2026-08 新增两个可调变量：critic 表征与 advantage 标签来源**。[[2607-WCM]] 把 world modeling 接进 critic 而非 actor，并用 $\lambda=0$ 的历史 ViT 对照把结论收紧到"缺的是预测性目标而非时序输入"（LIBERO-Plus 上 one-shot SFT + ~250 步 RL 即超过 20k 轨迹 Full-SFT，真机长程 stovetop cleaning 1/50→15/50）；[[2607-N0VTLA]] 的 ALTER 用轨迹事件与 stage-relative progress 离线构造二值 advantage，零额外环境交互，把 π0.5 在三个可形变物体长程任务上从 40/20/5 提到 90/75/60。二者都没有回答上述四个问题，而是各带来一个新问题：predictive critic 的收益究竟来自"更准的 value"还是"更难塌缩的表征"（WCM 全文无 value 精度指标，两种解释同样兼容），以及离线 advantage 的质量上限由只吃 RGB 与 prompt 的 progress model 决定，其误差如何传导到 policy 未被测量。
- **注意这两条仍不构成 dense reward**：ALTER 的 progress 是离线标注、WCM 的 latent 预测是辅助监督，都不是环境返回的稠密奖励——"只覆盖 episode-level sparse reward"这一判断在严格意义上未被推翻。
- **第三条路是换掉 policy 的参数化本身**：上述所有工作都在绕开 flow-matching head 不给解析 likelihood 这个约束，[[2608-GalaxeaG05|G0.5]] 指出纯 AR policy 根本不需要绕——token-level log-probability 精确可得，GRPO 原样套用，而 flow-matching 要按 RLinf 引入 SDE 把去噪当 Markov 过程近似。它的支持证据只有 4 个 LIBERO 任务（每任务 1 条演示起步、初始成功率相当）上 AR 收敛更快、终点更高、跨 seed 方差更小，没有真机、没有长程、没有与 advantage conditioning 的同预算对照。若这条在规模上成立，"RL 难做" 就从算法问题退回架构选择问题，架构选型与 post-training 方案不能再分开评估——此前把二者绑在一起讨论的先例只有 Knowledge Insulation 那类训练稳定性论证。
- **第四个可调变量是推理延迟本身（2026-09）**：上列工作都把延迟当环境常数，[[2609-RealTimeExpoFT]] 把它写进 RL 的目标——策略学的是"若以零延迟执行应当如何改写 base chunk"的编辑量，再由 Q 在候选间选择。DROID 4 个真机任务上同一条 SFT 起点：12.5/30 → 加 RTC 时序对齐 18.0 → 叠在线 RL 25.0 → 延迟进目标后 29.0；而不感知延迟的在线 RL 只从 18.0 走到 18.8。这把"可 RL 修复 vs 结构性 failure"的分界线往前挪了一格：一部分此前会被归到硬件的失败，其实是优化目标没写对。但证据强度不足以支撑更强的读法——每格只有 30 次试验、无重复无误差棒，另一半实验在没有 VLA 的 Kinetix 上做，摘要用 42%→97% 概括收益而同预算对照的真实差距是 29 对 25，代码未放出。

### 3. Cross-embodiment 的正确抽象层

- Per-embodiment action head（π0 / GR00T N1 / RDT）→ input-side soft prompt（X-VLA）→ 统一 latent action（LAPA / UniVLA）的演化线尚未收敛。
- Morphology 巨差（gripper vs dexterous hand / single-arm vs humanoid loco-manipulation）能否共享 backbone？[[2604-Pi07]] UR5e 匹配人类 top-2% 是正面信号但 case-level。
- [[2512-WholeBodyVLA]] 用**双 LAM**（manipulation LAM + locomotion LAM）解耦"camera 静止 vs 移动"的 attention 冲突——提示未来 VLA 可能需要按 motion modality 拆解 latent space。
- OXE-scale（1000+ 数据源）下 per-source soft prompt 是否仍可行未验证；分层 prompt（embodiment-level + setup-level）可能是下一步。
- **第四种候选抽象：把动作离散化本身当共享层（2026-08）**。[[2608-GalaxeaG05|G0.5]] 不做 per-embodiment head 也不学 latent action，而是把 14 个 embodiment 的动作按运动部件铺进一个 27 维定长空间（left_control 9 / left_gripper 1 / right_control 9 / right_gripper 1 / lower_body 7），缺失部件填零并由一个 active-part 预测头显式声明本步哪些部件参与，再用 RVQ + temporal contrastive 把这个空间量化成共享 vocabulary。与 soft prompt 的差别在于共享发生在 tokenizer 而非条件输入，与 latent action 的差别在于维度语义是人工指定的而非学出来的。目前只有 2B 一个规模点、没有 scaling 曲线，也没有把"27 维分区"与"等维度无语义分区"分开的消融，因此还不知道起作用的是部件语义还是仅仅是定长对齐。
- **第五条不是新抽象层，而是先统一迁移口径（2026-09）**：上列四种候选一直在同一个含混的"zero-shot 迁移到新本体"下比较，[[2609-ZETA]] 把它拆成 strict（目标本体既不在预训练也不在后训练里）与 pretrain-exposed（在预训练混合里出现过、只是没做目标后训练）两档，并量出两个此前没被单独量过的量。一是 state 与 action 的参照系选择值约 15 分（60.3±1.1 对 75.7±1.3），比这一节讨论的多数架构选择更大——抽象层之间的比较若不先固定参照系，读到的可能是坐标系差异。二是把 5% 的目标本体数据放进预训练，14 个 held-out 本体的平均任务进度涨 13.4 分（UR5eUMI 69.3→78.6、GoogleRobot 51.4→68.9），因此 pretrain-exposed 一档的数字不能与 strict 并排引用。它的边界要一并读：512 个本体是从**一个** Franka 模板程序化改出来的（连杆缩放 0.7–1.3），"morphology 巨差能否共享 backbone"这条主线它没有回答；base 的状态与指令被排除在动作空间外，所谓 full-embodiment 不含底盘控制；真机侧的预训练数据全部来自仿真，每格 10 次 rollout 无重复无误差棒。

### 4. Reasoning-action unification

现有路线仍是"在语言空间思考 → 产生动作"（ECoT / DriveVLM / Cosmos-Reason1 / GenieReasoner）。[[2507-VLATokenizationSurvey]] 提出的 **action-token-based reasoning**（直接在动作空间做 CoT）暂无实证。[[2508-EmbodiedR1]] Table 6 发现 RL 比 Think 重要得多（Where2Place +20 vs +2.5），暗示当前 CoT 的价值可能主要是 representation shaping 而非 inference-time planning。

2026-08 把这个问题拆成了两问。一问是表示：[[2608-GalaxeaG05|G0.5]] 让 CoT 与 RVQ 动作码共享 vocabulary 与 likelihood 参数化，是目前最接近 unification 的形态，但推理链本身仍是语言，action-token-based reasoning 仍无实证；它的增益分布也支持 representation shaping 一侧——长程任务 Air Fryer 2.4→3.8、Bacon 1.5→3.4，单阶段任务只有约 1.6pp。另一问是时机：[[2608-InContextVLA|VLA-Talker]] 在证据完全相同的三行对照里显示，把空间证据**生成**出来只有 81.5%（且付 4.6× 延迟），**注入**且只监督动作 token 是 97.4%，其中监督掩码单独值 7.7 分；[[2608-StellaVLA|StellaVLA]] 沿同一方向把语言 head 训完后在推理时整个剥离。两者合起来指向一个尚未被正面检验的可能：CoT 的价值若真在 representation shaping，那它就不该在推理时被展开——但两篇的"生成"基线都是自建的（VLA-Talker 的 Gen-CoT 在每个数据预算上都低于纯 BC），最小检验是拿一个已发表的 CoT-VLA 权重在同 backbone 同数据上重训后再比。

2026-09 给这个问题添的是一个负面数据点。[[2609-PhysBrain15|PhysBrain 1.5]] 把语言、末端动作与未来视觉状态三类输出统一成离散 token，挂在 Qwen3-VL 8B 的同一套 embedding 与 LM head 上，用单一带 loss mask 的 next-token 目标联合训练，28 个 embodied understanding benchmark 的 overall 做到 72.5（开源第一，次优 66.0）。但全文没有一处 ablation，也没有一个闭环成功率——动作与未来帧这两根支柱只有离线轨迹可视化与 action-token perplexity（ID 17.12→5.07、held-out RoboDojo 12.39→6.57，两条曲线起点不同不可跨源比），论文在 §5.3.1 与 Fig. 4 图注两次主动写明这是离线预测而非执行。它因此支持的是"这套理解数据配方有效"，而不是 unification 假设：72.5 无法区分收益来自 24.3M 感知预训练、6.61M 理解 SFT，还是来自动作与未来帧监督。相对 [[2608-GalaxeaG05|G0.5]] 的实质增量只有一条——把未来视觉状态也折进同一个 LM head——而这条恰好是零量化证据的那条。一个完整的离散统一接口被实现并训到 8B 规模却交不出执行侧数字，不能被引作该路线可行性的支持。

### 5. Evaluation / reproducibility 危机

- **Lab tabletop 饱和**：LIBERO 98+ 已在噪声量级，CALVIN ABCD→D 接近上限。
- **语言鉴别力缺失**：LIBERO 上 task-ID embedding 可近乎无损替代自然语言指令（[[2607-TurboVLA]]，−2.3pp），主流短程 suite 因此无法验证任何以语义理解为卖点的设计。需要的最小改动是加入 held-out 指令改写与同义/反义配对，使"语言真的被用到"成为可检验命题。**这条最小改动在 2026-08 被做出来了**：[[2608-GSRParaVLA]] 的 LIBERO-Para 用 4,092 条改写 episode（Act / Obj / Comp 三类）在不动环境的前提下把同批模型从 72-98% 打回 4-77%，鉴别力随之恢复。剩下的缺口是它只解决"改写"这一维：未见物体、未见动作、组合新指令与显式反义配对（要求模型在语义不成立时**拒绝执行**）都还没有对应协议；且 LIBERO-Goal 的 10 个任务共享同一视觉场景，改写不变的句子编码器与 10 路任务码在其上仍分不开。2026-09 出现的是另一条补法——不改指令而改场景：[[2608-InstructMove]] 要求每个场景至少有两个可执行候选、只有一个与指令一致，并把 Reach 定义在与指令一致的那个目标上，于是"不看语言随便抓"的期望分数被压到 chance；π0.5 / GR00T N1.7 / Motus 在 pick_spatial 上的 Reach 分别只有 0.46 / 0.50 / 0.51。两条补法的组合仍留一个洞，见横切议题一末段。
- **自建 benchmark bias**：RoboBrain 2.5 / RynnBrain / Vlaser / ACE-Brain-0 / Pelican-VL 都在自家 benchmark 上领先——难以横向对比。2026-08 出现一个更细的变体：[[2608-HyMeS|HyMeS]] 用的是 RoboMemArena 的作者修正版 12-task protocol，筛选标准是"π0.5 已有 motor skill、只因缺 history 而失败"，声明筛选不看本方法结果，但这个标准本身就朝记忆注入类方法倾斜，PrediMem 的发表数字因此不可直接引用而须信任作者复评。
- **评测预算不足以支撑名次**：[[2608-CofactVLA|CofactVLA]] 在每 suite 10 episode、LIBERO-Plus 每任务 1 episode、无 seed 无误差棒的条件下报 +0.4pp 与 +1.2pp 的领先；同一 π0 baseline 在不同论文里记成 53.6 与 56.3。鲁棒性子集正在替代主表承担名次功能，若沿用主表的引用与预算习惯，饱和 benchmark 的可比性问题会原样搬过去。
- **Metric 口径不齐**：π0 的 50 Hz 是 chunk-level，OpenVLA 的 6 Hz 是 token-level；TL（trajectory length）只算成功 episode 引入 selection bias（[[2604-BiCoord]]）。2026-09 在 LIBERO-Plus 上出现同名指标口径分叉的第二例：[[2609-LatentInterfaceTraining|LIT]] 的 Overall 是 7 个扰动轴的未加权均值（其 repo 自报的 task-weighted 口径低约 2 分），[[2609-OpenWAM]] 的 Avg 按 trial 数加权且表内未标注（α 的未加权 7 列均值 71.33 对印出的 69.2）。两篇都没写错，但两列 Overall 不能相减，而鲁棒性子集正在承担名次功能。
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
- **记忆不一定要学在权重里（2026-08）**：上列全部方案都在扩充或压缩神经记忆，[[2608-HyMeS|HyMeS]] 把 memory 逻辑整体挪出网络——冻结微调后的 π0.5 只负责 motor skill，coding agent 用 rollout 反馈迭代出一段包含显式 symbolic state 与 constraint 选择规则的可执行程序，推理时由该程序选出的可微 constraint 以梯度注入 velocity field。这条路线的吸引力在成本结构：示教预算随可复用 motor skill 数扩展而非随 history-dependent 配置数扩展，改需求只改代码。它同时暴露一个此前不显眼的风险——不可靠的记忆比没有记忆更糟：occlusion 类里 PrediMem 的 CSR 38.3 低于纯反应式 π0.5 的 50.4，HyMeS 靠 k-of-w 验证把 CSR 拉回持平（50.6）才换来 TSR +7.0。开放的是它的适用边界：heuristic learning 依赖开发阶段的 stage 级 ground-truth 反馈（仿真里免费，真实开放场景怎么来论文没说），counting 类的 CSR 反而低于 PrediMem（60.3 vs 72.2）提示 guidance 注入会干扰早期 motor 执行，且程序能否跨任务复用未交代。
- **同一主张的第二种传递方式：token 级接口（2026-09）**。[[2609-2AM]] 与 HyMeS 一样把 memory 移出 policy，但传下去的东西相反——不是梯度而是 subtask language 加可选的 2D grasp/place/move 点，底层 Action Model 纯 RGB 输入、episode 内无状态。LIBERO-Mem 十任务上 completion 76.29 / relaxed SR 63.00 / strict SR 11.83，相对同 backbone 的自建 π0 复现（70.79 / 37.42 / 12.25）completion +5.50、relaxed +25.58，而 strict 反而略低，论文自陈证据不支持一致的成功率提升。承重的是 language-only 消融：同 Agent 同 policy 同观测只去掉 2D 点，三项掉到 53.72 / 19.42 / 7.25，加回后 relaxed +43.58 而 strict 只 +4.58。约 9.5 倍的不对称给这一节添了一条区分——grounded hint 把记住的意图推过有序进程，但"该在哪一步停"不在接口带宽能解决的范围内，记忆方案的评价因此不能只看 completion。边界：它的 π0 复现比 LIBERO-Mem 已发表的 π0（5.0% completion）高一个量级，摘要里 61.5 点的领先比的是已发表 SlotSSM 而非这个更强的复现；11.83 的 strict SR 里有 7.33 点来自 T9 / T10 两个 occlusion 任务，T1–T6 全面落后。
- **记忆也可以整个长在部署期（2026-08）**。[[2608-Zeva]] 冻结 Cosmos3 的 rectified-flow 动作头，部署期只在线更新一套双时间尺度的因果记忆，累计成功率随四轮演化从 26% 升到 73%，ChemLab-Evo 三级难度 83.3 / 70.0 / 57.32。对本节有用的是它的检索控制那一格：跨任务用最近邻 signal 时成功率 100→95 与 80 维持，随机替换掉到 55 / 45——起作用的是检索到相关经验，而不是多喂了上下文。它自称是冻结策略下从自身物理交互做 in-context learning 的首个框架，尚未见独立验证；每任务 20（ChemLab-Evo）或 50（Atomic5）episode，组件移除只给 10–20 与 15–30 的区间而非逐任务数字。与同族方法共同的举证缺口见横切议题四。

### 8. Safety / alignment for embodied intelligence

- **Linguistic fragility**：[[2604-DAERT]] 证明仅改写语言指令即可把 π0 LIBERO 93%→5.85%，且具跨架构迁移性。[[2608-GSRParaVLA]] 把它从攻击面推进到机制与部分修复：语义在语言主干里完好（探针 Retrieval@1 0.516-0.941 对随机 0.1），失效在语言特征进入动作策略的融合点，只替换该处特征即消除 96.8% 的动作差异；把语义源换成不看图像的冻结文本编码器后 SmolVLA 的改写成功率 4.47→49.12。但这是**鲁棒性修复而非安全保证**——GSR 的实验是良性同义改写，没有对抗性改写、诱导性指令或拒绝行为的评测，且注入位置不可跨架构移植（附录 D.3 预注册的三条通用语义断点判据无一模型同时满足）。
- **Emergent improvisation 的 double-edge**：GEN-1 blog 承认 emergent recovery 既是 capability 也是 alignment liability——机器人"自由解释任务"可能造成物理损害。
- **No-action probe**：DAERT 用 "no action" prompt 发现 π0.5 仍 54.9% 成功（退化成 vision-only），揭示当前 VLA 对语言依赖度的 hidden bias。
- 现有 safety 工作（ASIMOV-2.0 / Auto-Red-Teaming / Semantic Action Safety）主要围绕 semantic content；物理 action 的 hazard 层面在 2026-08 被攻击侧先一步占住，防御侧还是空的。[[2608-TrapVLA]] 把 VLA 后门的目标从"让任务失败"改成"指定怎么失败"：触发器是一句读起来正常的自然语言前缀，不改图像、不在执行期介入，被激活的是四种由 $\Delta \in \mathbb{R}^3$ 参数化的可配置失败（Early Close / Early Open / Grasp Deviation / Release Deviation），四种可共存于同一个模型。Trap-LIBERO + OpenVLA-OFT 上四模式 C-ASR 98.7 / 98.9 / 95.8 / 94.1，clean SR 96.8 / 98.8 / 92.9 / 92.4 对未投毒的 98.4 / 97.6 / 97.9 / 94.5。
- **这条威胁把三类常用筛查同时废掉**，这是它相对语言脆弱性那一支的实质差别。干净成功率的跌幅（Object 98.4→96.8、Long 94.5→92.4）落在种子噪声量级，回归测试无分辨力；输入侧 ONION 默认阈值在 148 条触发指令里只报 4 条（2.7%）且无一条触发词被完整移除，降到 t=−5 能报 56.8% 但同时改写 94.6% 的干净指令，零样本 LLM judge 在 185 条指令上全判 CLEAN；触发前缀换一个同义实词，聚合 C-ASR 只降 0.8–1.6pp，字符串黑名单同样无效。可用的防御面被压到权重/激活侧扫描与部署期行为审计，而论文一条防御都没试——最直接的抓手（同一观测下加/不加前缀的动作分布差分）恰好就是它自己训练时用的监督信号。
- **基线结构比头条数字更有信息**：朴素文本触发在两个空间偏移模式上已有 97.4 / 97.8，但 Early Close 只有 23.4、Early Open 是 0.0——控制"在哪个时刻失手"远难于控制"往哪个方向偏"，而前者才是造成物理伤害的那一类。边界一并读：π0.5 上朴素基线 95.3 与本方法 95.8 几乎持平（作者归因于连续 action flow），因此"可配置失败模式"在 flow-matching 策略上是否同样成立尚未定；投毒比例的响应非单调（68.6 / 82.4 / 10.2 / 86.8 / 93.2）且论文未解释；无防御方案、无 ethics statement、无 limitations 章节，代码 coming soon。Inference-Time Policy Steering 仍是可能的防御方向，但尚未见任何工作在"语言触发 + 时序精确的物理偏移"这类威胁上测过。

### 9. 新增预测通道 / 感知通道的收益归因（2026-08 新增）

近一年 VLA 的主流增益手段是"再加一路"——加一路未来预测（WAM）、加一路模态（触觉）、加一路辅助目标（critic 的 latent prediction）。三篇独立工作的自家消融同时显示这条归因并不牢靠：[[2607-STWAM]] 的 DINO-only 未来分支（39.7）低于纯 VAE 基线（51.5），语义未来与像素未来互补而非可换；[[2607-N0TWAM]] 去掉反应式触觉通路比去掉预测式通路损失更大，最大单因素是预训练数据量（−19.1）；[[2607-WCM]] 证明了预测目标有用，却没有任何 value 精度指标可以排除"它只是防表征塌缩的正则化"。

要把这条链从相关性变成因果，缺的实验是共同的，也不昂贵：

- **同 backbone、同算力、逐目标移除**——把新增通道的参数量与训练步数补齐到对照组，再逐个关掉预测目标，而不是整支砍掉（ST-WAM 的 "parameter-matched" 变体方向正确，但原文未给参数量）。[[2608-VLAProprioception]] 的 slot-matched 对照是可直接搬运的样板：固定图像、语言、slot 数、expert action 与初始噪声，只抽掉时间变化，把"时序内容"与"多出来的 conditioning 容量"分开（30.8 对 39.0）。它自身仍留着 state expert / feature modulation 训练曝光不等、多数对比单 seed、sweep 未做多重比较校正的缺口。
- **中间量必须被直接测量**：value 精度（explained variance / TD error）之于 predictive critic，预测未来的保真度之于 WAM，接触事件的预测误差之于触觉——只报下游成功率无法区分"预测更准"与"梯度更稳"。
- **偏移类型要超出外观**：ST-WAM 的增益集中在 LIBERO-Plus 的 camera / sensor-noise 等外观级扰动，而它把机制归给 DINO 的表示不变性；在物理属性、动力学或物体几何偏移上重跑才能检验这条归因。

2026-08 的三篇训练期 world-model 工作把第一条缺口补上了一部分。[[2608-JEPAWAM|JEPA-WAM]] 在同 backbone 同协议下逐目标拆开当前帧对齐与未来帧预测（joint 79.2 / 只预测未来 77.3 / 只对齐当前 77.0 / 换成 DINOv2+SigLIP 表示 73.2），[[2608-WorldTokens|World Tokens]] 固定架构只改瓶颈的排他性（VLM 旁路 97.0→94.1）与 anchor 的构造（Canny anchor 91.5 反而低于完全不接 world model 的 95.0），[[2608-MobileWAM|MobileWAM]] 把 belief 的传递结构当变量（MLP 递归 46.3 低于完全不传的 50.2，transformer 递归 58.2；30 层全接 37.1 低于稀疏取样 4 层的 58.2；并行监督 52.3 低于串行 58.2）。这批消融的共同指向不是"多一路有没有用"，而是这一路以什么形状、在哪一层接进主干——负结果全部落在接口，正结果也只在特定接口下成立。

剩下的缺口有三处，都不因这三篇而关闭：第二条（中间量必须被直接测量）仍然空着，三篇都只报下游成功率，没有一篇报告未来预测本身的保真度或它与成功率的相关性；参数量与算力对齐依然缺失（MobileWAM 全表除自身 ≈6.5B 外没有任何 baseline 的参数量，与 ST-WAM 是同一个毛病）；比较基线仍是引用而非重跑。另外 [[2608-JEPAWAM|JEPA-WAM]] 给出一个新的边界事实：同一条 transition 监督在 RoboTwin Clean 上带来 +9.2，在 Random 强 appearance randomization 上只有 37.2→37.5——预测监督对相机位姿偏移与对外观随机化的作用并不同源，把它们合并成"提升鲁棒性"会掩盖这个分裂。

2026-09 两篇把这条缺口的两端分别推了一步，方向相反。[[2609-LatentInterfaceTraining|LIT]] 给出的是可以直接搬运的消融结构：除了逐组件移除，它另加三行"替代设计"，分别实例化三种会让整套解释塌掉的简单说法——只是个 Q-Former 式 latent 聚合（65.70）、只是两阶段训练（65.46）、只是多加了一路通用辅助监督（65.45），三者都停在比 baseline 高约 2pp 处，离完整方法的 71.92 差 6pp 以上。这把"组合才有效"从一句话变成可证伪的命题，也顺带给出了分解：瓶颈本身只占总增益的约 25%（+2.08 of +8.30），重头是瓶颈与空间先验、瓶颈与位姿监督这两个组合。[[2609-OpenWAM]] 则在设计空间的广度上做到了这一节一直在要的受控扫描（主干、编码器、mask、调度、预训练阶段各自单独变动），却在最关键的一条归因上完全没有干预：它把 ID 侧 WAM 更贴合训练分布归因于 video-latent 监督注入额外优化信息、把 OOD 侧劣势归因于长时域误差累积，而 $\lambda_v$ 全文恒为 1.0 从未被扫过，horizon 从未被变动，它自己的 Infra 里也根本没有 action-only 家族，这两条结论实际建立在外部榜单数字上。而它恰好是最有条件补上这个对照的一篇——Single-System Vanilla 已经把 action token 并进 video 序列，加一条"去掉 video 流"的变体即可得到同 Infra 下的 action-only 对照。

第二条缺口（中间量必须被直接测量）在这两篇之后依然空着，而且现在有了更具体的形状：LIT 用位姿重建当监督却从不报重建保真度，也没扫过瓶颈宽度 K（Table III 六个变体无一行改 K），因此分不开"瓶颈窄"与"监督信号对"；OpenWAM 报了满盘下游分数却没有一格未来预测质量的数字。两篇加起来说明这条缺口不是没人做得起，而是没人把它当成必报项。

## 调研日志

### 2026-09-18 survey-refresh（并入 14 篇，99 → 118）

- **并入清单**：[[Papers/2609-OpenWAM|OpenWAM]]（路线 8 / 整体趋势 3 / OP1 / OP9 / 四张 benchmark 行）、[[Papers/2608-ZimaBlue|ZimaBlue]]（路线 4 与 8 / convergence 8 / OP1 / RoboTwin 2.0 Randomized 榜首 / 真机 Franka 12 任务行）、[[Papers/2609-RealTimeExpoFT|Real-Time EXPO-FT]]（路线 8 / convergence 8 / OP2 / DROID 在线 RL 行）、[[Papers/2609-ZETA|ZETA]]（路线 7 / 横切议题三 / OP3）、[[Papers/2609-PhysBrain15|PhysBrain 1.5]]（整体趋势 1 / 路线 1 / OP4 / 28-benchmark 理解类行）、[[Papers/2609-LatentInterfaceTraining|LIT]]（整体趋势 6 / convergence 13 / OP5 / OP9 / LIBERO-Plus 与 YAM 双臂行）、[[Papers/2608-InstructMove|InstructMove]]（横切议题一 / OP5 / 新建 InstructMove 行）、[[Papers/2609-DroneCATS|DroneCATS]]（对照组小节 / 评测 crisis）、[[Papers/2608-Zetta|Zetta]]（新建横切议题四 / convergence 9 / LIBERO-Pro 行）、[[Papers/2608-Zeva|Zeva]]（横切议题四 / convergence 9 / OP7 / ChemLab-Evo 行）、[[Papers/2609-2AM|2AM]]（路线 3 / OP7 / LIBERO-Mem 行）、[[Papers/2608-TrapVLA|TrapVLA]]（OP8）、[[Papers/2608-QwenDrive|QwenDrive]]（路线 2 / 评测 crisis）、[[Papers/2510-VQVLA|VQ-VLA]]（路线 1）。无跳过。QwenDrive 与 DroneCATS 虽属自动驾驶与无人机场景，但前者是 VLM 主干梯度污染的直接证据、后者是动作空间由 prompt 声明这一接口形态的唯一样本，按动作接口视角保留。
- **结构变化**：新增小节「横切议题四：冻结权重之上的适配层」——Zetta 的代码化运行时 critic 与 Zeva 的部署期因果记忆，与既有 HyMeS / RobustExecAgenticRL / AffordanceFieldIntervention 构成同一族（改进落在权重之外的可检视结构里），共同的举证缺口是预算配平。convergence 新增第 14 条（受控设计空间扫描本身成为一类产出）并改写 8 / 9 / 13。两处小节标题改名：对照组一节扩为「两端的对照组」以容纳 prompt 声明动作空间的 MLLM 直控；横切议题三加入"参照系"一维。整体趋势 1 / 3 / 6、路线 1 / 2 / 3 / 4 / 7 / 8 各增段，路线 4 的分支数由两条改三条。Benchmarks 扩充 LIBERO-Plus / RoboTwin 2.0 / RoboTwin 2.0 Randomized / RoboCasa365 四行并加口径注，新增 InstructMove / LIBERO-Mem / LIBERO-Pro 三行仿真、五行真机与一行理解类；数据量级增两条，评测 crisis 增四条。Open Problem 1 / 2 / 3 / 4 / 5 / 7 / 8 / 9 各增条目。本表无 Key Evidence Matrix 节，故不涉及。
- **被修改的既有结论**：(1) OP8 末条"现有 safety 工作未触及物理 action 的 hazard 层面"被 [[Papers/2608-TrapVLA|TrapVLA]] 改写为"攻击侧已到达该层面、防御侧仍空"，并记入其废掉三类常用筛查的证据。(2) 整体趋势 3 的"data > model size"被 [[Papers/2609-OpenWAM|OpenWAM]] 的主干阶梯限定到 action-labeled 数据这一段——收窄适用范围而非推翻。(3) 路线 7 的"zero-shot 迁移到新本体"被 [[Papers/2609-ZETA|ZETA]] 拆成 strict 与 pretrain-exposed 两档，此前跨论文并排的 zero-shot 数字随之失去可比性。(4) RoboTwin 2.0 Randomized 榜首由 ABot-M0.5 94.2% 换为 ZimaBlue 94.3%。(5) OP5 的"Metric 口径不齐"新增 LIBERO-Plus Overall 同名指标的口径分叉。本轮无共识降级为争议的条目。
- **刻意未写进正文的 claim 及理由**：OpenWAM 的 C33 / C34 两条机制解释（video-latent 监督注入优化信息、长时域误差累积）无任何受控干预，只记"归因缺干预"而不采纳结论；其 C27 baseline 来源全文未交代，故不引其 baseline 数字做横比；C4 / C6 / C10 三处内部数值不调和未采用，只有 C16（RoboCasa365"边际差距"实为 19.2pp）以"论文自身数据与其论断不一致"的形式写入表格注。ZimaBlue 的 C18 / C19 意味着既无小时或算力配平的替换对照、也无 Slow 分支 K/V 移除消融，因此正文明写"视频更便宜"不是测量结果，也不把收益归给 Slow-Fast 的某个组件。Real-Time EXPO-FT 摘要的 42%→97% 与 10/10 被判 contradicted，未采纳为收益幅度；其 Kinetix 实验不含 VLA，结论不外推。DroneCATS 全部在仿真中、无非 MLLM 基线、复现三轮 46/50/35、判据审计翻转 182 例中的 95 例，因此只写"声明式终止未被计价"，不写模型能力排名。InstructMove 的 C13 指控建立在设计目标表而非实测上，未采纳为对其他 benchmark 的实证批评；100 条示教 / 5,000 步 / 无 checkpoint selection，故 Lift 的 0.01–0.17 未写成模型能力结论；sim-real 相关性未建立。ZETA 的 512 个本体由单一 Franka 模板程序化改出，未写成 morphology 多样性结论。Zetta 无组件消融、无预算配平、表内只有自家冻结底座，其 SOTA 表述未采纳，头条 90.8%（两格均值）未用，正文取 71.13 宏平均；11.1× / 11.9× 与 20.6× 的加速口径不一致，全部加速倍数未引。Zeva 的"首个"为自述，正文标注尚未见独立验证；组件移除只给 10–20 / 15–30 区间，未拆到任务级。LIT 的 baseline 不从预训练 policy checkpoint 微调（作者自陈），79.67 未与其他 LIBERO-Plus 数字排序；K 未扫描，未写瓶颈宽度结论；无参数量与延迟数字，未采纳其 parameter efficiency 表述。PhysBrain 1.5 零 ablation、零闭环成功率，未写入任何策略能力结论；其 SFT 混合含若干被评 benchmark 的同族训练数据，72.5 未写成纯 held-out 结果；笔记中"据本笔记所见是第一次"的表述未进正文。QwenDrive 的开环领先与闭环落后只作口径反例，未写成方法优劣判断。TrapVLA 在 π0.5 上与朴素文本触发几乎持平，"可配置失败模式"未外推到 flow-matching 策略；投毒比例响应非单调且论文未解释，未写剂量-反应结论。2AM 的 strict SR 优势集中在 T9 / T10 两个任务，未写成一致提升；其摘要 61.5 点领先比的是已发表 SlotSSM 而非自建更强复现，未引。全部为单篇证据，无独立复现，未做外部检索，未写任何"首次 / 无人研究"表述。
- **papers_analyzed**：机械复核编辑后正文唯一的 `Papers/` wikilink 为 118 个（114 篇核心 + 4 篇 survey），全部指向存在的笔记。旧值 99 与编辑前的机械值 104 之间存在 +5 的历史差额，成因在本轮之前，未追溯逐条来源；本次按机械值记 118。
- **domain_map**：判定有格局级变化，候选条目随本轮报告返回，由主会话统一去重合并写入。
- **status**：success

### 2026-09-07 survey-refresh 增量并入 8 篇

- **来源**：全部 full-text。source-checked 7 篇——[[Papers/2608-GalaxeaG05|G0.5]]、[[Papers/2608-CofactVLA|CofactVLA]]、[[Papers/2608-MobileWAM|MobileWAM]]、[[Papers/2608-HyMeS|HyMeS]]、[[Papers/2608-JEPAWAM|JEPA-WAM]]、[[Papers/2608-WorldTokens|World Tokens]]、[[Papers/2608-StellaVLA|StellaVLA]]；partial 1 篇——[[Papers/2608-InContextVLA|VLA-Talker]]，只采其 C1–C19，C20（作者把 84.3 说成"退化到 BC 水平"，实际 BC 为 90.4）与 C21（与 OpenVLA-OFT 95.3 的可比性）标为 contradicted / not-checkable 未采用。G0.5 的 C15（Conclusion 声称零样本 LF 超过 post-trained π0.5，与 Fig 10 的 68.8 > 65.6 矛盾）同样未采用。JEPA-WAM 的逐扰动列（Language 68.2 对 ResVLA 88.5）不在其 ledger 内，正文只作定性方向记录并标注。
- **结构变化**：技术路线部分新增「路线 8 的分叉：world model 退到训练期」小节（World Tokens / JEPA-WAM / MobileWAM，与推理期条件化的 DreamZero / Cosmos Policy / Fast-WAM 形成延迟-机制对照）。两处共识降级为**争议**：整体趋势 1 与 convergence 2 的"离散只配做辅助监督"被 G0.5 的同数据同算力真机对照推翻为争议；横切议题一的"语义保住了、只是路由坏了"被 CofactVLA 的相反定位（语义根本没进来）降级为争议，两侧证据与判别实验一并记录。整体趋势新增第 6 条（辅助分支退到训练期、接口取代模块成为设计变量），convergence 新增第 13 条并改写 6/7/8/12，路线 1 / 路线 2 / 路线 5 各增段。Benchmarks 表 LIBERO / LIBERO-Plus / RoboTwin 2.0 / SimplerEnv WidowX 四行扩充，新增 SimplerEnv GoogleRobot（未拆 VM/VA）、ManiSkill-HAB SetTable、VLA-Arena、RoboMemArena、RoboCasa-GR1 五行与 8 行真机条目；评测 crisis 新增"评测预算与断言精度脱钩"。Open Problem 2 / 3 / 4 / 5 / 7 / 9 各增一条。papers_analyzed 91→99。
- **证据边界**：G0.5 的 LIBERO 优势仅 0.2pp、RoboTwin 1.1pp，abstract 在 Bridge 上只对比 π0.5 57.1 而实际次优是 79.2；其 RL 主张只有 4 个仿真任务，27 维统一动作空间只有 2B 一个规模点、无 scaling 曲线也无"等维度无语义分区"对照。CofactVLA 每 suite 10 episode、LIBERO-Plus 每任务 1 episode、无 seed 无误差棒，Table 2 缺自家底座 π0.5 使 +15.5 混着底座升级，头条的 OOD 与 LIBERO-Plus 两个 setting 都无组件消融，Language 轴 71.8 落后 OpenVLA-OFT_m 81.0。MobileWAM 全表除自身 ≈6.5B 外无 baseline 参数量，真机未报 trial 数与示教条数，abstract 的 "strong generalization" 与附录"训练分布内随机化"不符，部署实际跑在远程双 A800。World Tokens 无代码、无 K 与 λ_w 敏感性，LIBERO 上并非最优且 DiT4DiT 的延迟是跨硬件数字。JEPA-WAM 代码 "Coming soon"，真机每任务 10 rollout，δ 为逐 benchmark 手调且无敏感性报告，RoboTwin Random 列几乎不动。VLA-Talker 的 SOTA 表基线未 matched，Gen-CoT 是自建且每档都低于纯 BC，仿真只用单第三人称 RGB。StellaVLA 依赖检索基础设施，no-demo 62.4 / wrong-demo 44.9。HyMeS 的 12-task protocol 由作者重筛且偏向记忆注入类方法，heuristic learning 依赖开发期 stage 级 ground-truth，样本量每任务 10-20 episode。全部为库内单篇证据，无独立复现；本轮不做外部检索，未写任何"首次/无人研究"表述。
- **domain_map**：判定有格局级变化，提案写入 `Workbench/.survey-refresh-staging/VLA-Survey.domainmap.md`（TARGET: DomainMaps/EmbodiedAI.md），由 coordinator 合并。
- **status**：success

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
