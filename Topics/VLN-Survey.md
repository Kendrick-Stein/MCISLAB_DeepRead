---
title: Vision-Language Navigation Survey
description: 系统梳理 VLN 四条主流技术路线（graph-based、streaming VLA、zero-shot MLLM with EWR、GRPO-based RFT）及其性能对比、benchmark 格局与 open problems；作为 VLN DomainMap 的 delta 报告，重点覆盖 2025–2026 的新进展
tags: [VLN, navigation, embodied-reasoning]
date_updated: "2026-09-07"
year_range: 2022-2026
keywords: [vln, vision-language navigation, vision and language navigation, robot navigation]
papers_analyzed: 30
domain_map: EmbodiedAI
---

## Overview

**一句话定位**：VLN（Vision-and-Language Navigation）要求 agent 按自然语言指令在未见环境中导航到目标，是 embodied AI 中语言 grounding 与空间推理最成熟的落点之一。

**领域活跃度**：过去 3 年 VLN 从"discrete nav-graph + task-specific encoder-decoder"稳态跃迁到"continuous environment + streaming VLM"的新范式，R2R val-unseen SR 从 2022 年 ~50%（DUET, HAMT）抬到 2026 年的 70.9%（[[Papers/2607-ABotN1|ABot-N1]]）。其间由 graph-based 方法（Efficient-VLN、ETP-R1）划出的 64% 这道线，早在 2025-12 就被只用公开 R2R-CE/RxR-CE 数据训练的 3B panoramic-RGB 模型 [[Papers/2512-NavForesee|NavForesee]] 以 66.2 越过，2026-08 的 4B monocular 模型 [[Papers/2608-LightNav0|LightNav-0]] 做到 68.5；同时 zero-shot MLLM 路线从 <10%（NavGPT 早期尝试）追到 48.8%（GTA）。四大活跃方向并行推进：**graph-based supervised** ([[Papers/2202-DUET|DUET]] → [[Papers/2304-ETPNav|ETPNav]] → [[Papers/2512-EfficientVLN|Efficient-VLN]] / [[Papers/2512-ETPR1|ETP-R1]])、**streaming VLA** ([[Papers/2402-NaVid|NaVid]] → [[Papers/2412-NaVILA|NaVILA]] → [[Papers/2507-StreamVLN|StreamVLN]] → [[Papers/2512-NavForesee|NavForesee]] → [[Papers/2603-PROSPECT|PROSPECT]] → [[Papers/2603-DyGeoVLN|DyGeoVLN]] → [[Papers/2607-ABotN1|ABot-N1]] → [[Papers/2608-LightNav0|LightNav-0]])、**zero-shot MLLM with EWR** ([[Papers/2305-NavGPT|NavGPT]] → [[Papers/2602-GTA|GTA]] / [[Papers/2601-SpatialNav|SpatialNav]])、**GRPO-based RFT** ([[Papers/2506-VLNR1|VLN-R1]] → [[Papers/2512-ETPR1|ETP-R1]])。

**整体趋势**：
1. **Continuous > discrete**：R2R-CE / RxR-CE 已成 de facto benchmark，discrete nav-graph 上的 SOTA 主要是历史参考；R2R-CE 是 VLN 在 2025–2026 的核心战场。
2. **VLM backbone 是默认起点**：LLaVA-Video / Qwen2-VL / VILA 已取代 task-specific encoder-decoder，social 2024 survey ([[Papers/2407-VLNFoundationSurvey|VLN Foundation Survey]]) 所说的 "FM-as-agent" 已从预言变成现实。
3. **Hierarchical + language-as-action 成为部署范式**：[[Papers/2412-NaVILA|NaVILA]] 的 "language mid-level action" 把 VLA 拆成 high-level VLM（1–2 Hz）+ low-level RL locomotion（real-time），这条架构正在成为 legged / real-robot VLN 的默认模板。
4. **空间先验必须显式，但来源已有两条**：一条是外挂几何模块，从 [[Papers/2602-GTA|GTA]] 的 TSDF + BEV visual prompting，到 [[Papers/2603-PROSPECT|PROSPECT]] 的 CUT3R 3D fusion，到 [[Papers/2603-DyGeoVLN|DyGeoVLN]] 的 dynamic geometry FM，显式 3D 表示在 continuous VLN 中几乎一致地涨分；另一条由 [[Papers/2608-LightNav0|LightNav-0]] 代表，不接任何几何模块，而是把 VLM 预训练里已有的 pointing 能力扩进词表——affordance 与 object 两族 point token 共享一个 image grid，空间决策先被"指"出来再接动作，靠 embodied-reasoning mid-training 把这批先验拉起来（8 个空间 benchmark macro avg 63.1 → 67.4）。
5. **Benchmark 停滞已被识别并开始破局**：[[Papers/2512-VLNVerse|VLNVerse]] 的 Table 1 指出 R2R 之后几乎所有"新 benchmark"都在 MP3D 原 90 个场景上反复重标注（贡献 0 new scenes），Strict 物理设定下 MLLM agent SR 相对 Tel-Hop 下降 10 pp。embodied gap 开始成为新的讨论焦点（[[Papers/2507-VLNPE|VLN-PE]]、[[Papers/2510-NaviTrace|NaviTrace]]、[[Papers/2512-VLNVerse|VLNVerse]]）。

## Problem & Motivation

**核心问题**：给定自然语言指令 $I$ 和 egocentric 视觉流 $\{o_1, \ldots, o_t\}$，agent 需要输出一系列低层动作 $\{a_1, \ldots, a_T\}$ 使自己到达指令描述的目标位置。评测通常要求在终点 ≤ 3 m 处主动 STOP。

**为什么重要**：
- **Language grounding 的最具体化 benchmark**：VLN 需要把抽象语言同时 ground 到**感知**（"through the door with the red handle"）、**动作**（"turn left 30 degrees"）和**状态**（"you should be facing the kitchen"），是 embodied multimodal reasoning 的集大成场景。
- **Sim-to-real 的 accessible 训练场**：相对 manipulation，navigation 的 sim-to-real gap 可控、可量化（几何准确性远胜于接触物理），因此成为验证 VLM-based agent 真实世界可部署性的最佳起点。
- **VLA / spatial intelligence 的前哨**：VLN 是 VLA 的 navigation 子集，其 hierarchical planning + language mid-level action 的架构直接对应 VLA 的 hierarchical inference（见 VLN-VLA Unification），spatial representation 的研究结果（topological map、3D scene graph、3D fusion）对 manipulation 和 world model 同样有迁移价值。

**为什么适合现在做**：
- 开源 Video-LLM（LLaVA-Video、Qwen2-VL、VILA）已到 7–8B 规模，在单张 A100 上可跑 VLN inference；
- CUT3R / VGGT / π³ 等 feed-forward 3D 几何 FM 让 "单目 RGB + 几何 prior" 成为可行路线（[[Papers/2603-PROSPECT|PROSPECT]]、[[Papers/2603-DyGeoVLN|DyGeoVLN]]）；
- 数据 bottleneck 被部分破解——ScaleVLN（3M 轨迹）、[[Papers/2412-NaVILA|NaVILA]] 的 YouTube touring video pipeline、[[Papers/2509-NavFoM|NavFoM]] 的 Sekai + SLAM 标注把训练样本推到 12.7M 量级；
- Isaac Sim + GRUTopia + [[Papers/2512-VLNVerse|VLNVerse]] 让物理仿真成为可用 benchmark。

## 技术路线对比

VLN 当前四条主流路线在 R2R-CE val-unseen 上的代表性数字见下表，Problem framing、数据需求、训练成本、部署难度各不相同。

### 1) Graph-based Supervised（topological planner）

**思路**：在线构建拓扑图（visited / current / navigable / ghost nodes），用 cross-modal graph transformer 在全图上选 long-term goal，再用 waypoint predictor + low-level controller 执行。

**代表工作**：[[Papers/2202-DUET|DUET]]（dual-scale graph transformer，CVPR 2022 Oral）、[[Papers/2304-ETPNav|ETPNav]]（online topo map + Tryout 避障，TPAMI 2024；RxR-CE +26 SR 范式级跃升）、[[Papers/2512-EfficientVLN|Efficient-VLN]]（progressive memory + dynamic DAgger，R2R-CE 64.2% SR 以 282 H800·h 训练成本拿到 SR-vs-cost 帕累托前沿）、[[Papers/2512-ETPR1|ETP-R1]]（首次把 closed-loop GRPO 搬到 graph-based VLN-CE，R2R-CE test-unseen 64 SR）。

**核心优势**：
- 显式 global memory 支持 long-range backtracking，抑制 oscillation 失败模式（ETPNav Table 7 +3.29 SR）；
- Waypoint 级 high-level action space 等价于 RL 的 token，天然支持 closed-loop multi-turn GRPO（ETP-R1）；
- GASA（Graph-Aware Self-Attention）把 all-pair shortest distance 作为 attention bias，是轻量有效的结构先验。

**实际效果与瓶颈**：R2R-CE SR 64% 曾被视作 supervised 上限，代价是依赖 pretrained waypoint predictor（CWP）+ ground-truth pose + 预定义 navigable 节点，sim-to-real 部署仍需工程化。方法层面已比较成熟，而**被 LLM-based agent 路线部分替代**的风险已经落地：ETP-R1 用 GRPO 续命是补救策略，64% 这条线则先后被三个直接由 VLM 产出连续动作、不经预训练 waypoint predictor 与预定义节点的模型越过——[[Papers/2512-NavForesee|NavForesee]] 66.2（3B，panoramic RGB，仅用公开 R2R-CE/RxR-CE 数据）、[[Papers/2607-ABotN1|ABot-N1]] 70.9（tri-view RGB，30M 样本）、[[Papers/2608-LightNav0|LightNav-0]] 68.5（4B，monocular）。三者的观测配置与训练预算差异极大，唯一共性就是把 graph-based 路线的那套预训练组件整个拿掉。

**记忆维度的扩展**：[[Papers/2603-Memoir|Memoir]]（TPAMI 2026）把 graph-based 底座（DUET/GR-DUET）扩展到 memory-persistent 设定（IR2R：同一环境连续 episode 的 tour 内累积经验），用 language-conditioned world model 想象未来导航状态作检索 query，从跨 episode 混合记忆库（观测 + 行为轨迹双库）选择性取用——IR2R +5.4 SPL / 8.3× 训练加速 / -74% 推理显存 over GR-DUET。消融显示收益主体是"选择性检索 + 行为记忆"框架本身（全量记忆注入 69.98 SPL 甚至低于随机检索 70.34），imagination query 相对朴素 state-based query 仅 +0.61 SPL；oracle 检索 93.4 SPL 揭示记忆访问机制仍有 20 点 headroom。

### 2) Streaming VLA（Video-LLM as end-to-end navigator）

**思路**：把 VLN-CE 建模成 multi-turn dialogue，Video-LLM 吃 egocentric RGB 流直接输出动作；通过 KV cache 复用 + memory compression 控制长程上下文。动作接口本身在迁移——早期是离散 atomic action（FORWARD/LEFT/RIGHT/STOP + 可选数值参数），2026 年的模型多改为一次输出若干步连续 SE(2) waypoint（ABot-N1 的 action expert、NavForesee 的 K=5 waypoint、LightNav-0 的 3 token 解 10 步轨迹）。

**代表工作演化**：

- [[Papers/2402-NaVid|NaVid]]（RSS 2024）：首个 video-based VLM for VLN-CE，不对称 token 预算（current 64 token / history 4 token），直接输出 "FORWARD 75 cm" 而非 waypoint 坐标。
- [[Papers/2412-NaVILA|NaVILA]]（RSS 2025）：引入 language-as-mid-level-action + dual-frequency 架构，R2R-CE SR 54%，real Unitree Go2/H1/T1 跨形态 88% SR；YouTube touring video + MASt3R metric pose 是最 reusable 的数据 pipeline。
- [[Papers/2507-StreamVLN|StreamVLN]]（ICRA 2026）：slow-fast context——fast sliding-window KV（N=8 dialogue）+ slow voxel-pruned long memory，RGB-only R2R SR 56.9 / SPL 51.9；voxel pruning 剪 20% token 同时涨 1% SR。
- [[Papers/2512-NavForesee|NavForesee]]（2025-12，CVPR 2026）：Qwen2.5-VL-3B 单 backbone 交错训练两类目标——显式 hierarchical language planning（拆解长指令、汇报已完成的 sub-instruction、给出下一个）与隐式 dual-horizon 预测（短期固定 k=5 步服务局部避障，长期自适应外推到下一个 milestone，horizon 由 planning-aware hidden state 决定）；预测目标是 depth / DINOv2 / SAM 特征而非像素，规避视频生成式 world model 的推理开销。训练数据全部来自 Gemini 2.5 Pro 对公开 R2R-CE/RxR-CE 的重标注（约 1.5M 样本，清洗掉 16.7% 末 milestone 与终点错位的 case，并对占 61.79% 的直行样本下采样），R2R-CE SR 66.2 / OSR 78.4 / NE 3.94，但 SPL 59.7 低于 CorrectNav 的 62.3，RxR-CE（SR 66.3 / SPL 53.2）整体落后。
- [[Papers/2603-PROSPECT|PROSPECT]]（2026-03）：SigLIP + CUT3R 3D fusion + JEPA-style latent prediction 分支（训练时附加，推理时砍掉，零 latency 代价），R2R-CE SR 58.9 / SPL 54.0；CUT3R 因 absolute scale 优于 VGGT 系在长 episode 上。
- [[Papers/2603-DyGeoVLN|DyGeoVLN]]（2026-03）：自研 dynamic geometry FM（π³/VGGT + Depth Anything residual + DyHM3D 数据）+ pose-free occupancy voxel pruning，单目 RGB R2R-CE SR 60.8——反超 panoramic RGB-D + waypoint predictor。
- [[Papers/2509-NavFoM|NavFoM]]（2025-09）：generalist navigation VLM，TVI tokens（view angle + time step indicator）+ BATS（budget-aware token sampling），统一 VLN / OVON / tracking / autonomous driving 四类任务，RxR-CE SR 64.4。
- [[Papers/2607-ABotN1|ABot-N1]]（2026-07，高德 AMAP）：slow-fast 双系统——4B reasoner 低频输出 CoT + pixel goal（affordance/target 双像素），2B action expert 高频输出连续 SE(2) waypoints；以 pixel goal 为统一接口整合 point-goal / instruction-following / object-goal / POI-goal / person-following 五任务，30M 样本预训练 + GRPO post-training，R2R-CE SR 70.9 / SPL 67.5 刷新 supervised SOTA（仅前左右 tri-view RGB，无 depth/odometry），multi-task ≥ specialist；但全文无组件 ablation，pixel-goal 的贡献归因是叙事而非实验，自建 PointBench/POIBench 未声明训练/评测场景隔离。
- [[Papers/2608-LightNav0|LightNav-0]]（2026-08，Light Origins）：从 Qwen3-VL-4B-Instruct 直接实例化，只做 vocabulary extension——不加 waypoint predictor、task-specific action head 或 embodiment expert，affordance/object 两族 point token 与 3 个 residual-VQ action token 拼成同一条自回归序列（3 个 token 复原 10 步 SE(2) waypoint，ADE 0.72 cm，对比单层 K=4096 量化的 2.48 cm），全部输出由单一 CE loss 监督；视觉历史按指数衰减降采样与池化，近帧细、远帧粗。ER mid-training（~170 H100·h）→ SFT（~950 H100·h，含 FOV 90–130°、相机高度 0.5–1.5 m 的随机化与 DAgger）→ GRPO 三阶段，R2R Val-Unseen monocular SR 68.5 / SPL 62.8，RxR SR 73.6 / SPL 64.5，HM3D-OVON unseen split 47.0 / 24.1（此前开源最好 Uni-NaVid 39.5 / 19.8）。其 SOTA 声明限定在 monocular success rate，RxR nDTW 67.4 仍低于 DualVLN 的 70.0——成功率的领先没有均匀转化为轨迹保真度。推理约 4 ms/token（RTX 4090），代码与权重开源。

**核心优势**：
- Single-view RGB 即可竞争 panoramic RGB-D + waypoint（NaVILA、StreamVLN 早已证明，DyGeoVLN 与 LightNav-0 进一步反超），部署门槛低；
- Language-as-mid-level-action 让 VLM 可直接跨 embodiment 迁移（NaVILA Go2 → T1 零样本）；
- KV cache 复用把 per-step prefill 成本从 O(T²) 降到 O(T)（StreamVLN Figure 5）。

**实际效果与瓶颈**：
- R2R-CE val-unseen SR 一度停在 54–60% 区间、落后 graph-based 的 64%，如今区间上端已在 66–71%；越线并不以数据规模为前提——[[Papers/2512-NavForesee|NavForesee]] 用 3B backbone 和 1.5M 条公开数据重标注样本拿到 66.2，[[Papers/2608-LightNav0|LightNav-0]] 用 4B 拿到 68.5，[[Papers/2607-ABotN1|ABot-N1]] 的 70.9 才建立在 30M 样本之上；
- 训练成本高（StreamVLN 1500 A100·h / NavFoM 4032 H100·h），Efficient-VLN 证明通过 recency-aware memory 可压到 282 H800·h，LightNav-0 的 mid-training + SFT 两阶段合计约 1120 H100·h（在线 RL 阶段成本未披露）；
- Long-horizon 一致性、动态障碍下的 reactive 避障、VLM 低频推理下的闭环控制仍是限制；
- 成功率与路径质量开始分离：NavForesee 的 OSR 领先 CorrectNav 10.9 pt 而 SPL 落后 2.6 pt，LightNav-0 的 RxR nDTW 67.4 低于 DualVLN 的 70.0——两处都是"更多探索换来更高到达率"的形态，SR 单指标已不足以刻画这批模型的差别。

**预测式内部模型的作用边界**：把"预测未来"接进 policy 目前有两种接法。[[Papers/2603-PROSPECT|PROSPECT]] 的 JEPA-style 分支只在训练期存在，推理时整条删掉，收益记在表征上；[[Papers/2512-NavForesee|NavForesee]] 把 short/long 两组 dream query 留在推理路径里，解码出的环境特征直接进动作 MLP，long-horizon 预测经 structured attention mask 以 short-horizon 为条件、depth 与 semantics query 互相屏蔽。NavForesee 的 ablation 给出这条路线目前最硬的一条约束：关掉语言 planning 但保留双 horizon 预测，SR 从 66.2 掉到 48.8，而把 planning 与两级预测一起关掉反而回到 52.6——预测通路在没有语言意图 condition 时是净负资产（论文列出该行但未展开）。单独去掉 long-term 预测降到 58.6，说明预测本身确有正向贡献，前提是被 plan 锚住。至于预测目标该取 latent 还是显式模态，两篇选择相反且都没做同 backbone 对照：PROSPECT 主张 latent 目标可避免 overfit 到 texture/illumination 并把 NavForesee 归为像素/depth 监督的反例，而 NavForesee 的 RGB 侧预测的实际是 DINOv2 与 SAM 特征、只有 depth 解到 pixel level（SiLogLoss），这个对照因此从未真正成立，库内暂无独立验证。

### 3) Zero-shot MLLM with Explicit World Representation

**思路**：冻结大型 MLLM（GPT-5/Gemini/Qwen3-VL），用确定性 pipeline 维护显式 metric world representation（TSDF / topological graph / scene graph），把 spatial estimation 解耦给工程组件，semantic planning 交给 MLLM 在渲染的 BEV + ego view + coordinate grid 上选 waypoint。

**代表工作**：[[Papers/2305-NavGPT|NavGPT]]（AAAI 2024，早期 caption-based LLM-as-VLN-agent 的 existence proof，R2R val-unseen SR 34%）、[[Papers/2602-GTA|GTA]]（zero-shot VLN-CE SOTA：R2R-CE SR 48.8%，EWR plug-in 在 NavGPT/OpenNav/SmartWay 上一致涨分）、[[Papers/2601-SpatialNav|SpatialNav]]（放宽到 "允许 pre-exploration" 设定，分层 spatial scene graph + compass-style 全景 + remote object localization，GPT-5.1 后端 R2R-CE zero-shot SR 64.0%，逼近监督 SOTA）。

**核心优势**：
- **Sim-to-real gap 小**：MLLM 看的是 BEV + topo graph 这种 domain-invariant representation，不依赖 raw pixel 训练分布——GTA TurtleBot 40% / drone 42% real SR vs supervised VLN-BERT 16% / RDP 20%，是这类方法最强的卖点；
- **Plug-in reusable**：EWR 作为 substrate 跨 baseline 一致涨分，证明 "explicit metric representation > implicit linguistic memory"；
- **Backbone 越强越好**：GPT 5.1 > Gemini 2.5 Pro > Qwen3-VL-235B（GTA Table IV 单调上升），方法"半衰期"长。

**实际效果与瓶颈**：
- 与监督 SOTA 仍有 10–15 pt 绝对 SR gap（GTA 48.8 vs Efficient-VLN 64.2 on R2R-CE）；
- 核心性能依赖闭源 frontier MLLM，开源 backbone 显著掉点（GPT-5.1 → Qwen3-VL 掉 10 pt）；
- [[Papers/2601-SpatialNav|SpatialNav]] 通过允许 pre-exploration（SLAM 先扫场景）把 zero-shot 拉到 64%，但 "zero-shot" 的定义因此被 relax。

### 4) GRPO-based Reinforcement Fine-Tuning

**思路**：把 DeepSeek-R1 的 RLVR / GRPO 范式搬到 VLN——通过 verifiable reward（action correctness + path fidelity + 时间衰减）对 LVLM-based VLN agent 做 RL 微调。

**代表工作**：[[Papers/2506-VLNR1|VLN-R1]]（Qwen2-VL + Long-Short Memory + Time-Decayed Reward，R2R val-unseen 从 23.8 → 30.2 SR；2B-RFT 追上 7B-SFT；10K 样本跨域迁移超过 1.2M 完整数据）、[[Papers/2512-ETPR1|ETP-R1]]（graph-based VLN-CE 上首次 closed-loop GRPO，R2R-CE test-unseen 64 SR）。

**核心发现**：
- **Small-model lift**：RFT 让小模型追上大模型 SFT，复刻 DeepSeek-R1 现象；
- **Sample efficiency 远高于 SFT**：10K RFT > 1.2M SFT；
- **工程常识与 LLM-RL 社区有出入**（ETP-R1）：dropout 必须开，temperature scaling 有害，strict on-policy（μ=1）最好；
- **Reward design 是杠杆**：Time-Decayed Reward（γ^k 指数衰减）比 hard / uniform reward 关键。

**实际效果与瓶颈**：
- RFT 阶段显著提升，但本质上是在 SFT 强基础上的精修（cold-start RL 几乎失败，SR ~2%）；
- Graph-based（ETP-R1）上的 closed-loop GRPO 比 LVLM-based（VLN-R1）的 open-loop RFT 更自然——waypoint-level action space 天然 multi-turn。

### 路线综合对比

| 路线 | 代表方法 | R2R-CE SR | Obs | 训练成本 | Sim-to-real | 核心权衡 |
|---|---|---|---|---|---|---|
| Graph-based | [[Papers/2512-EfficientVLN\|Efficient-VLN]] | 64.2% | Pano+Depth | 282 H800·h | 需 waypoint predictor + GT pose | SOTA 上限高但依赖预训练组件 |
| Graph + GRPO | [[Papers/2512-ETPR1\|ETP-R1]] | 64.0% (test) | Pano+Depth | 较高 | 同上 | closed-loop RFT，需要三阶段训练 |
| Streaming VLA | [[Papers/2512-NavForesee\|NavForesee]] | 66.2% | Pano RGB | 未披露 | 纯 Habitat，无真机 | 预测通路必须由语言 plan 锚定；SPL 落后 CorrectNav |
| Streaming VLA | [[Papers/2603-PROSPECT\|PROSPECT]] | 58.9% | Mono RGB | ~2500 A800·h | 单 RGB 部署友好 | RxR 长指令增益大；code 未开源 |
| Streaming VLA | [[Papers/2603-DyGeoVLN\|DyGeoVLN]] | 60.8% | Mono RGB | 未披露 | 单目 + 自推 pose | 动态几何 FM 是主要变量 |
| Streaming VLA | [[Papers/2507-StreamVLN\|StreamVLN]] | 56.9% | Mono RGB | 1500 A100·h | Unitree Go2 部署 | KV cache 复用的 design pattern |
| Streaming VLA | [[Papers/2412-NaVILA\|NaVILA]] | 54.0% | Mono RGB | ~千卡时 | Go2/H1/T1 跨形态 88% SR | language-as-mid-level-action |
| Zero-shot EWR | [[Papers/2601-SpatialNav\|SpatialNav]] | **64.0%**\* | Pano + SSG | 零训 (推理) | 需 pre-exploration | framing stretch；open-model 掉点 |
| Zero-shot EWR | [[Papers/2602-GTA\|GTA]] | 48.8% | Mono RGB-D | 零训 (推理) | **wheeled 40% / drone 42% real** | sim-to-real gap 最小 |
| RFT (LVLM) | [[Papers/2506-VLNR1\|VLN-R1]] | 30.2% | Mono RGB | SFT + GRPO | 未量化 | sample-efficient cross-domain |
| Generalist | [[Papers/2509-NavFoM\|NavFoM]] | 61.7% | Multi-view | 4032 H100·h | 5 类 embodiment | VLN + OVON + tracking + driving 统一 |
| Generalist | [[Papers/2607-ABotN1\|ABot-N1]] | **70.9%** | Tri-view RGB | 30M 样本 + GRPO | 四足真机 10Hz（仅定性） | pixel-goal 统一五任务；无组件 ablation |
| Generalist | [[Papers/2608-LightNav0\|LightNav-0]] | 68.5% | Mono RGB | ~1120 H100·h + GRPO | 4 ms/token；真机 zero-shot（量化结果库内未核） | 单一 token 空间统一 pointing 与动作；SOTA 限定 monocular |

> \* SpatialNav 使用了 pre-exploration，严格来说不是纯 online zero-shot。

**关键观察**：
1. **Depth 与 waypoint predictor 都不再是 SOTA 的必要条件**：graph-based（Pano+Depth）64% 曾领先 streaming VLA（Mono RGB）60% 约 4 pt，这个差距从三个方向被抹平——[[Papers/2512-NavForesee|NavForesee]] 保留 panoramic 但去掉 depth/odometry 得 66.2，[[Papers/2607-ABotN1|ABot-N1]] 用 tri-view RGB 得 70.9，[[Papers/2608-LightNav0|LightNav-0]] 单目得 68.5。接下来该问的是视角数量本身贡献多少：单目 68.5 与 tri-view 70.9 之间的 2.4 pt，和两者相差一个量级的训练数据纠缠在一起，没有 matched 对照能把它们拆开。
2. **Closed-loop > open-loop RFT**：VLN-R1（open-loop SFT+GRPO）30.2 vs ETP-R1（closed-loop GRPO）64——RFT 要起效必须有合适的 action abstraction。
3. **Zero-shot 的真正卖点是 sim-to-real**：sim 上 zero-shot 仍比 supervised 差 4–15 pt，但 real-world 上 domain-invariant representation 让它反超（GTA real 40%+ vs supervised 16–20%）。
4. **训练策略与数据规模的杠杆之争无定论**：Efficient-VLN（0.45B 级方案）以 282 H800·h 打过 NavFoM（7B，4032 H100·h），训练策略（recency-aware memory + dynamic DAgger β）的杠杆远大于 scaling；[[Papers/2607-ABotN1|ABot-N1]] 以 30M 样本的数据工程重夺 SOTA，把天平推回数据侧；而 [[Papers/2512-NavForesee|NavForesee]] 只用公开 R2R-CE/RxR-CE 的重标注（约 1.5M 样本、3B backbone）就到 66.2，[[Papers/2608-LightNav0|LightNav-0]] 以 4B 和约 1120 H100·h 到 68.5。榜首附近的模型分处相差一到两个数量级的数据与算力 regime，更像是接口设计（pixel goal / dream query / point + action token）在决定名次而非任一条 scaling 轴；这些工作彼此没有 matched 对照，该判断是排除法的产物而非直接证据。
5. **预测信号的符号取决于它被什么 condition**：[[Papers/2512-NavForesee|NavForesee]] 的模块消融里，语言 planning 在场时去掉 long-term 预测掉 7.6 SR（66.2 → 58.6）；planning 不在场时把双 horizon 预测加回去反而掉 3.8 SR（52.6 → 48.8）。同一条预测通路的净效应可正可负，"预测未来对导航 policy 有没有用"在不指定 condition 时无法回答。单篇证据，库内暂无独立验证。

## Datasets & Benchmarks

### Training Datasets

VLN 主流训练资源（按规模）：

| Dataset | 场景 | 规模 | 用途 | 备注 |
|---|---|---|---|---|
| **R2R** (Anderson 2018) | MP3D 90 scenes | 7,189 trajectories × 3 instr | fine-grained 指令 | VLN 的 de facto 起点 |
| **R4R** (Jain 2019) | MP3D | ~30K | R2R 拼接 | 长路径 variants |
| **RxR** (Ku 2020) | MP3D | 126K instr (en/hi/te) | 多语言、长指令 (~120 词) | 平均 15 m |
| **R2R-CE** (Krantz 2020) | MP3D + Habitat | R2R 迁移 | continuous action space | 当前主 benchmark |
| **RxR-CE** | MP3D + Habitat | RxR 迁移 | 长程 continuous + sliding-forbidden | 大底盘（0.18m） |
| **REVERIE** (Qi 2020) | MP3D | 10K | goal-oriented，含 object grounding | 高层指令 |
| **SOON** (Zhu 2021) | MP3D | 4K | 目标导航 | object-oriented |
| **R2R-EnvDrop** (Tan 2019) | MP3D augmented | 大规模 | environment augmentation | NaVILA / StreamVLN 均用 |
| **ScaleVLN** | HM3D 700 scenes | 3M | 大规模 augmentation | StreamVLN 仅用 150K 子集即 SOTA |
| **YouTube touring**（NaVILA） | real urban + indoor | 2K 原 video → 20K trajectory | real-world navigation | MASt3R metric pose 关键 |
| **DyHM3D**（DyGeoVLN） | HM3D + skeletal human | ~50K | 动态障碍训练 | 人形运动数据增强 |
| **Sekai + SLAM**（NavFoM） | web video | 2.03M | navigation foundation model | VLM 标指令 + SLAM 标 trajectory |
| **Hierarchical plan 重标注**（NavForesee） | MP3D + Habitat | 30K episodes → ~1.5M 样本 | sub-instruction + milestone 监督 | Gemini 2.5 Pro 标注；清洗 16.7% 错位 case，直行样本下采样 |
| **INSIGHT-Bench train**（LightNav-0） | 1,683 scenes | 53,090 episodes | 细粒度空间指令 | Molmo2 开放集 pointing 预标注 + 多视角一致性 gate |

### Benchmarks & SOTA

**R2R-CE Val-Unseen leaderboard**（截至 2026-09 精选，含单位统一）：

| Method | Date | Obs | SR↑ | SPL↑ |
|---|---|---|---|---|
| DUET ([[Papers/2202-DUET\|2022]]) | discrete | Pano | 72.0* | 60.0 |
| ETPNav ([[Papers/2304-ETPNav\|2023]]) | CE | Pano+Depth | 57.0 | 49.0 |
| NaVid ([[Papers/2402-NaVid\|2024]]) | CE | Mono RGB | 37.4 | 35.9 |
| NavGPT ([[Papers/2305-NavGPT\|2024]]) | discrete | Text | 34.0 | 29.0 |
| Uni-NaVid (RSS25) | CE | Mono RGB | 47.0 | 42.7 |
| NaVILA ([[Papers/2412-NaVILA\|2025]]) | CE | Mono RGB | 54.0 | 49.0 |
| StreamVLN ([[Papers/2507-StreamVLN\|2025]]) | CE | Mono RGB | 56.9 | 51.9 |
| NavFoM ([[Papers/2509-NavFoM\|2025]]) | CE | Multi-view | 61.7 | 55.3 |
| PROSPECT ([[Papers/2603-PROSPECT\|2026]]) | CE | Mono RGB | 58.9 | 54.0 |
| DyGeoVLN ([[Papers/2603-DyGeoVLN\|2026]]) | CE | Mono RGB | 60.8 | 55.8 |
| Efficient-VLN ([[Papers/2512-EfficientVLN\|2025]]) | CE | Pano+Depth | 64.2 | 55.9 |
| ETP-R1 ([[Papers/2512-ETPR1\|2025]]) | CE | Pano+Depth (test) | 64.0 | 54.0 |
| NavForesee ([[Papers/2512-NavForesee\|2025]]) | CE | Pano RGB | 66.2 | 59.7 |
| LightNav-0 ([[Papers/2608-LightNav0\|2026]]) | CE | Mono RGB | 68.5 | 62.8 |
| ABot-N1 ([[Papers/2607-ABotN1\|2026]]) | CE | Tri-view RGB | **70.9** | **67.5** |
| GTA zero-shot ([[Papers/2602-GTA\|2026]]) | CE | Mono RGB-D | 48.8 | 41.8 |
| SpatialNav zero-shot ([[Papers/2601-SpatialNav\|2026]]) | CE | Pano+SSG | 64.0\* | — |

> \* Discrete nav-graph；SpatialNav 使用 pre-exploration。NavForesee 的 OSR 78.4 高出 CorrectNav 10.9 pt 而 SPL 59.7 低 2.6 pt；LightNav-0 的 SOTA 声明限定在 monocular success rate。

**RxR-CE Val-Unseen**（节选）：

| Method | SR↑ | SPL↑ | nDTW↑ |
|---|---|---|---|
| ETPNav | 54.8 | 44.9 | 61.9 |
| StreamVLN | 52.9 | 46.0 | 61.9 |
| PROSPECT | 54.6 | 46.2 | 62.1 |
| NavFoM (multi-view) | 64.4 | 56.2 | — |
| Efficient-VLN | 67.0 | 54.3 | — |
| NavForesee ([[Papers/2512-NavForesee\|2025]]) | 66.3 | 53.2 | — |
| LightNav-0 ([[Papers/2608-LightNav0\|2026]]) | 73.6 | **64.5** | 67.4 |
| ABot-N1 ([[Papers/2607-ABotN1\|2026]]) | **73.9** | 63.9 | — |

> ABot-N1 与 LightNav-0 的 RxR-CE SR 仍次于未入表的 Qwen-RobotNav-4B（75.2/65.0，后者用了更大的 in-domain RxR 数据）；LightNav-0 的 nDTW 67.4 低于 DualVLN 的 70.0。NavForesee 在 RxR-CE 上全面落后 CorrectNav（69.3/63.3），作者归因于自己只用公开数据，但未做 controlled 对照——RxR-CE 的 30° 最小转角与 79° 窄 FOV 设定下 dual-horizon 预测是否本身失效，同样未被排除。

**Memory-persistent benchmarks**（跨 episode 记忆设定）：IR2R（unseen tour 平均 71.2 个 episode）与 GSA-R2R（150 个 HM3D 场景 × 600 路径）要求 agent 在同一环境的连续 episode 中累积经验、越走越熟。[[Papers/2603-Memoir|Memoir]] IR2R 77.6 SR / 73.3 SPL vs GR-DUET 72.7 / 67.9，tour 级 t-nDTW +12.1；GSA-R2R 上仅 +2.5 SPL——方法收益对 tour 长度/episode 重叠度敏感。

**细粒度空间指令诊断**：[[Papers/2608-LightNav0|LightNav-0]] 的 INSIGHT-Bench 把 1,097 条评测 episode 按 5 类场景 × 5 类指令（base / direction / relation / extremum / ordinal）交叉切分，目的是把指令理解的失败与路径执行的失败分开。LightNav-0 自身 SR 43.7 / SPL 41.5，最好的开源 baseline JanusVLN 27.4 / 24.0；分项从 base 的 53.1 递降到 ordinal 的 32.6。该 benchmark 的 1,683 个训练场景与 210 个评测场景出自同一条 Molmo2 pointing 预标注管线，跨模型的绝对差距因此系统性偏向 LightNav-0，能直接引用的是分项递降这个内部趋势——需要在候选集内做比较的空间语言（序数、极值、关系）是当前 VLM 导航的短板，与 [[Papers/2510-NaviTrace|NaviTrace]] 的 goal localization 拆解指向同一处。

**Physical & embodied benchmarks**（关注 embodied gap）：

- **VLN-PE** ([[Papers/2507-VLNPE|2025]], ICCV 2025)：首个系统量化 embodied gap 的 physical benchmark。GRUTopia/Isaac Sim + humanoid (H1) / quadruped (Aliengo) / wheeled (Jetbot) 三类机器人 + RL locomotion controller。VLN-CE → VLN-PE 零样本 SR 相对下降 **34%**（NaVid 从 ~40 掉到 22.4）；camera height 是决定性变量；多模态融合（RGB+D）对光照退化抗性显著优于纯 RGB。
- **VLN-CE-Isaac**（NaVILA 子产品）：R2R 场景从 Habitat 抽象搬到 Isaac 物理仿真，Go2 NaVILA-Vision SR 50.2 / SPL 45.5，H1 45.3 / 40.3，接近 Oracle low-level 上界 51.3。
- **VLNVerse** ([[Papers/2512-VLNVerse|2025]])：Isaac Sim 上 **263 全新手工可交互 USD 场景**（首次真正 new scenes，Table 1 揭示 R2R 之后几乎所有 benchmark 在 MP3D 原 90 scenes 上反复重标注），Strict 物理设定下 MLLM SR 相对 Tel-Hop 下降 10 pp（25.5→16.7），foundation model 在新场景下泛化明显退化（InternNav-N1 coarse SR 仅 17.5%）。
- **HA-VLN**（dynamic-human-aware VLN）：DyGeoVLN SR 0.40 > StreamVLN 0.33，动态障碍下纯 streaming VLA 明显退化。
- **LH-VLN** ([[Papers/2412-LHVLN|2025]], CVPR 2025)：long-horizon VLN（2-4 subtask，平均 150 steps），所有 baseline 在 2-3 subtask 长度上 SR = 0；MGDM baseline ISR/CSR/CGT 也仅个位数，揭示 single-stage VLN 训练对多阶段顺序推理几乎无迁移。
- **NaviTrace** ([[Papers/2510-NaviTrace|2025]])：VQA-style 2D image-space trace 预测，1000 scenarios × 3000 expert trace × 4 embodiment（human/legged/wheeled/bicycle）。Gemini 2.5 Pro 34.4 vs Human 75.4；goal localization 是主要失败模式；VLM 几乎不根据 embodiment 调整轨迹（aggregate 分数跨 embodiment 几乎相同）。

**Outdoor / aerial benchmarks**：

- **TouchDown** (Chen 2019)：Google Street View 城市户外导航。
- **AerialVLN / ANDH / OpenUAV / OpenFly / LANI**：游戏引擎 / AirSim 的 UAV VLN。
- **AirNav** ([[Papers/2601-AirNav|2026]])：基于 SensatUrban 真实航拍点云的 143K 样本 UAV-VLN；persona-conditioned instruction（10 种社会角色）提升 naturalness；Qwen2.5-VL-7B + SFT + GRPO test-unseen SR 51.75%，real-world 仍 30%。

### Simulators

| Simulator | 场景来源 | 特点 | 代表用法 |
|---|---|---|---|
| Matterport3D (MP3D) | 90 real indoor scans | 基础场景 | R2R / REVERIE / CVDN |
| Habitat | MP3D + HM3D | 离散 / CE 仿真 | VLN-CE 主流 |
| AI2-THOR | procedural | 强交互，空间小 | ALFRED / TEACh |
| GRUTopia / Isaac Sim | MP3D + custom | 全物理 + humanoid | VLN-PE / NaVILA / VLNVerse |
| AirSim | procedural | UAV | AerialVLN |
| CARLA | urban driving | 自驾 | LCSD / CDNLI |

## Open Problems

1. **Embodied gap**：VLN-CE 上的 SR 在 Strict 物理 / 真实 embodiment 下系统性下降（VLN-PE -34%、VLNVerse -10 pp），揭示现有方法隐式 overfit 到 MP3D 默认 1.2–1.6 m 相机高度、假设无碰撞 teleport、忽视底盘。**核心问题**：如何显式建模 physical embodiment、camera height、collision dynamics？[[Papers/2507-VLNPE|VLN-PE]] 的 multi-robot co-training 是初步答案，但缺乏系统性架构贡献。

2. **Long-horizon / building-scale navigation**：现有 benchmark 路径长度多在 9–15 m（R2R / RxR），[[Papers/2412-LHVLN|LH-VLN]] 的 150-step 任务让所有 baseline 在 2-3 subtask 长度上 SR = 0；PROSPECT 在 ≥100 步任务上 +4 pp SR。当前 memory pipeline（sliding window + token pruning）在 long horizon 上仍缺乏一致性保证（StreamVLN 自承），state compression 在长 trajectory 上崩（Efficient-VLN Table 4：RxR 上 recursive memory 比 progressive memory 掉 7 pt）。

3. **Goal localization > path shaping**：[[Papers/2510-NaviTrace|NaviTrace]] 的拆解揭示 VLM 的主要失败模式是找目标而非画路径——只预测 goal 29.65 / 完整 34.38 / oracle-goal 51.89。这与 VLN-CE 的 failure 分析（"走到对的房间但错位置" 占 23%）一致。[[Papers/2608-LightNav0|LightNav-0]] 从监督侧给出同向读数：INSIGHT-Bench 分项里 relation / extremum / ordinal 三类指令的 SR 落在 32–35%，而 base 指令 53.1——目标一旦要在候选集内比较（"最靠左的那把椅子"），定位就崩，这与路径规划能力无关；该分解受训练与评测同源的限制，只能作内部趋势读。**悬而未决**：zero-shot MLLM 是否能通过更强的 open-vocabulary grounding 提升 goal localization，而不依赖更大的 backbone？

4. **动态环境（人、移动物）**：真实部署绕不开动态障碍，但 HA-VLN / Habitat 3.0 的评测仍稀缺。[[Papers/2603-DyGeoVLN|DyGeoVLN]] 表明 static geometry FM（VGGT / π³）在动态场景崩坏是主因，data-driven（DyHM3D skeletal human）可补救但非架构级解决。Dynamic 3D foundation model 是否需要 explicit 时序建模是 open。

5. **Embodiment awareness**：[[Papers/2510-NaviTrace|NaviTrace]] 显示 VLM 不根据 embodiment（人/四足/轮式/自行车）调整策略。NaVILA 的 "language-as-mid-level-action" 通过替换 low-level policy 实现跨形态，但 H1 humanoid 仍比 Go2 quadruped 低 5 pt，说明 hierarchy 不能完全掩盖 embodiment-specific 需求。**Embodiment-conditioned action space** 是被忽视的设计维度。

6. **Data recipe 的可加性边界**：StreamVLN 的 ablation 显示 DAgger +5.5 SR、RxR co-train +7.8 SR、ScaleVLN +2.9 SR、MMC4 +2.0 SR 可叠加得到 SOTA，但这些 component 是否互为替代（mutually replaceable）未被 controlled 分析。"数据规模正交增量" 是 empirical 观察而非原理性保证。

7. **Sim-to-real gap 的量化**：[[Papers/2407-VLNFoundationSurvey|2024 survey]] 已点出但至今无系统量化（"sim 60 → real 16–20% 掉幅多少由哪些因素造成"）。GTA（sim 48.8 → real 40%）和 NaVILA（sim 54 → real 88% on 不同 setup）提供了两种走向极端的 data point，但缺 controlled head-to-head。

8. **VLN ↔ VLA 的结构同构**：VLN-VLA Unification 指出 VLN 的 hierarchical planner + waypoint predictor 与 VLA 的 high-level planner + low-level action decoder 在架构上高度对应；[[Papers/2412-NaVILA|NaVILA]] 已经开始跨——把 VLN 重构为 navigation-focused VLA。但 **shared spatial representation**（topological map / 3D scene graph / voxel）能否直接服务 manipulation 仍是 open，ConceptGraphs / MTU3D 是候选但还未被系统验证。

9. **Benchmark 停滞与破局**：[[Papers/2512-VLNVerse|VLNVerse]] 直接指出 "new scenes = 0" 是 VLN 过去 5 年的真正瓶颈。263 个新场景是 first step，但能否成为 de facto 标准取决于社区采纳——目前 code 尚未完全开源，leaderboard 也未建立。

10. **GRPO on VLN 的 reward design**：VLN-R1 的 Time-Decayed Reward 是初步配方；ETP-R1 展示 GRPO 对 dropout / on-policy degree 的敏感性与 LLM-RL 常识不一致。**什么是 VLN 最合适的 verifiable reward**？action correctness、path fidelity（nDTW）、goal-reaching、collision penalty 如何组合仍缺 principled study。

11. **World model 信号进 policy 的接口条件**：[[Papers/2603-PROSPECT|PROSPECT]] 只在训练期挂预测分支、推理时整条删掉，[[Papers/2512-NavForesee|NavForesee]] 把预测留在推理路径并让 planning-aware hidden state 决定 long-horizon 的长度，两种接法都报出正增益，但后者的消融显示同一条预测通路在缺少语言 planning 时是净负资产（52.6 → 48.8）。**悬而未决**：正增益来自"多了一个预测目标"这一表征正则效应，还是来自"在线消费了预测出来的未来"？把 NavForesee 的 dream query 在推理时屏蔽、或给 PROSPECT 的预测分支补一条推理期消费路径，是分开这两者的最小对照，两篇都没做。预测目标该取 latent 还是显式模态的争论卡在同一处：PROSPECT 主张 latent 更抗 appearance 漂移却无 controlled ablation，而它用作反例的 NavForesee 实际预测的是 DINOv2/SAM 特征、仅 depth 解到 pixel level。

## DomainMap 更新建议

本次调研新增的可纳入 DomainMaps/VLN 的内容：

1. **新增 Established Knowledge 候选**：
   - "Recency-aware memory > uniform compression"（[[Papers/2512-EfficientVLN|Efficient-VLN]] ablation：R2R SR +2.6 / RxR SR +3.0）与 state-based memory 在长 trajectory 上崩（RxR -7 pt），这是 memory design 的可迁移 lesson。
   - "Closed-loop GRPO on graph-based VLN > open-loop RFT on LVLM"（[[Papers/2512-ETPR1|ETP-R1]] 64 SR vs [[Papers/2506-VLNR1|VLN-R1]] 30.2 SR），涉及 action-space-level design 与 RL 适配。
   - "Dynamic geometry FM（depth residual + skeletal-human data）显著提升动态 VLN"（[[Papers/2603-DyGeoVLN|DyGeoVLN]] HA-VLN 0.33→0.40 SR）。
   - "R2R-CE 榜首不再需要 waypoint predictor、GT pose 与 depth"——[[Papers/2512-NavForesee|NavForesee]] 66.2（Pano RGB）、[[Papers/2608-LightNav0|LightNav-0]] 68.5（Mono RGB）、[[Papers/2607-ABotN1|ABot-N1]] 70.9（Tri-view RGB）三个独立系统同向，都在 graph-based 的 64.2 之上。

2. **新增 Open Questions 候选**：
   - "Embodied gap 的量化"——VLN-CE → VLN-PE 零样本 SR -34%（相对），camera height 是决定性变量。
   - "Benchmark 的真实场景多样性"——VLNVerse Table 1 揭示几乎所有 post-R2R benchmark "new scenes = 0"。
   - "Goal localization 是 VLM navigation 的主要瓶颈"（NaviTrace 拆解；LightNav-0 的 INSIGHT-Bench 分项从 base 53.1 递降到 ordinal 32.6 是同向读数）。
   - "预测通路的净效应取决于是否被语言意图 condition"——[[Papers/2512-NavForesee|NavForesee]] 模块消融，有 planning 时 +7.6 SR、无 planning 时 −3.8 SR。

3. **Active Debate 需更新**：
   - "Mono RGB vs Pano+Depth" 的争论已经结束在 Mono 一侧（LightNav-0 单目 68.5、ABot-N1 tri-view 70.9 均在 Pano+Depth 的 64.2 之上），后续问题变成视角数与数据规模各值多少，尚无 matched 对照。
   - "预测目标取 latent 还是显式模态"仍是争议：PROSPECT 的主张无 controlled ablation，且其援引的反例 NavForesee 实际预测 DINOv2/SAM 特征而非像素。
   - "Zero-shot MLLM vs supervised" 随 MLLM 升级快速缩小（GPT 5.1 > Gemini 2.5 Pro > Qwen3-VL 单调上升；SpatialNav GPT-5.1 backbone 达到 monitored SOTA 水平，但依赖 pre-exploration）。

## 调研日志

**调研日期**: 2026-04-23
**本次 Survey 新增论文**（rating ≥ 2）：29 篇在 vault 中已收录的 VLN 相关论文笔记 + 本次 digest 的 4 篇（1 篇 survey + 3 篇新 benchmark / 方法）：
- Survey: [[Papers/2407-VLNFoundationSurvey]]
- 新 benchmark / 方法: [[Papers/2603-DyGeoVLN]], [[Papers/2512-VLNVerse]], [[Papers/2510-NaviTrace]]
- 已有 VLN 笔记: [[Papers/2202-DUET]], [[Papers/2304-ETPNav]], [[Papers/2305-NavGPT]], [[Papers/2402-NaVid]], [[Papers/2412-LHVLN]], [[Papers/2412-NaVILA]], [[Papers/2502-MapNav]], [[Papers/2502-VLNav]], [[Papers/2506-VLNR1]], [[Papers/2507-StreamVLN]], [[Papers/2507-VLNPE]], [[Papers/2507-MTU3D]], [[Papers/2509-NavFoM]], [[Papers/2509-AnywhereVLA]], [[Papers/2509-OmniEVA]], [[Papers/2512-EfficientVLN]], [[Papers/2512-ETPR1]], [[Papers/2601-AirNav]], [[Papers/2601-SpatialNav]], [[Papers/2602-GTA]], [[Papers/2603-PROSPECT]], [[Papers/2210-VLMaps]] 等

**参考 Survey**: 
- 主锚点: [[Papers/2407-VLNFoundationSurvey|Vision-and-Language Navigation Today and Tomorrow]] (TMLR 2024) — 采用其 LAW 框架（World / Human / Agent）作为结构参考，但本 Survey 由于 domain activity 以 2025-2026 为主，改按**技术路线**（4 条）而非 LAW 三分组织，以更贴合当前讨论。

**方法论说明**：
- 本 Survey 定位为 DomainMaps/VLN 的 delta 报告，DomainMap 已 Established 的内容不重述，聚焦 2025-2026 窗口内新方法、新 benchmark、新 debate；
- SR / SPL 数字来自各论文笔记已验证过的表格；因各方法数据 regime 不同（是否用 ScaleVLN / MMC4 co-train），绝对数字对比需谨慎看 footnote；
- "Zero-shot" 的定义在 [[Papers/2601-SpatialNav|SpatialNav]] 把 pre-exploration 纳入后有争议，本 Survey 保留其原标记但加 `*` 提示。

**未能获取**: none

**增量更新 2026-07-21**（survey-refresh，+2 篇）：
- [[Papers/2607-ABotN1]]：R2R-CE SR 70.9 / SPL 67.5 刷新 supervised SOTA，tri-view RGB 反超 Pano+Depth——Overview、路线 1/2 瓶颈、综合对比表、两个 leaderboard、关键观察 1/4 相应更新（"64% 上限"与"gap 正在消失"两个结论被推翻）；因其无组件 ablation 且自建 benchmark 未声明场景隔离，归因性 claim 均按叙事归因处理、不采信为实验结论。
- [[Papers/2603-Memoir]]：新增 memory-persistent VLN 覆盖（IR2R/GSA-R2R 设定 + imagination-as-query 检索式记忆访问），并入路线 1"记忆维度的扩展"与 benchmark 节；其消融（imagination 相对 state-based query 仅 +0.61 SPL）提示该方向的收益主体是选择性检索框架而非 world model 本身。

**增量更新 2026-09-07**（survey-refresh，+2 篇，`papers_analyzed` 按正文唯一 `Papers/` wikilink 数机械统计 28 + 2 = 30）：
- [[Papers/2512-NavForesee]]（CVPR 2026，2025-12 arXiv）：并入路线 2 演化链与新写的"预测式内部模型的作用边界"段。两处改写既有结论——其一，R2R-CE 66.2（3B、panoramic RGB、仅公开数据）说明 64% 这条 graph-based 上限在 ABot-N1 之前七个月就已被越过，且不需要工业级数据规模，Overview、路线 1/2 瓶颈段与关键观察 1/4 相应修正；其二，其模块消融（无 planning 时预测通路 52.6→48.8）把"world model 信号有助于导航 policy"从可加性结论降为条件性结论，新增关键观察 5 与 Open Problem 11。同时记录一条 vault 内部矛盾：PROSPECT 把 NavForesee 归为像素/显式模态监督的反例，而 NavForesee 实际预测 DINOv2/SAM 特征、仅 depth 解到 pixel level，双方均无 controlled 对照，"latent vs 显式预测目标"保留为争议。
- [[Papers/2608-LightNav0]]：并入路线 2 演化链、综合对比表 Generalist 行、两个 leaderboard，并新增 benchmark 节的"细粒度空间指令诊断"段。其单目 R2R 68.5 / SPL 62.8 与 RxR SPL 64.5（后者高于 ABot-N1 的 63.9）使 DyGeoVLN 的 mono-RGB 最优标记失效；空间先验来源由此分为"外挂几何模块"与"激发 backbone 自带 pointing 先验"两条，整体趋势 4 改写。两项限定：SOTA 声明仅覆盖 monocular success rate，RxR nDTW 67.4 低于 DualVLN 70.0；INSIGHT-Bench 的训练与评测场景出自同一条 Molmo2 预标注管线，其绝对差距（+16.3 SR over JanusVLN）不作横向比较证据，只取分项递降趋势。
