---
title: World Model Survey
tags: [world-model, agent, simulation, planning, MBRL, VLA, diffusion-policy, cross-embodiment]
date_updated: "2026-08-02"
year_range: 2024-2026
papers_analyzed: 42
keywords: [world model, video prediction, dynamics model, mbrl, world action model, action-conditioned, diffusion policy, cross-embodiment]
domain_map: WorldModel
---
## Overview

World Model 是 AI Agent 的环境建模能力——预测行动后果、模拟状态转移、支持 counterfactual planning。从 MBRL 的 transition model 到 Video Generation 的 action-conditioned prediction，再到 GUI/Web Agent 的 environment simulator，不同社区对"world model"有不同理解。

**核心洞察**：[[2604-AgenticWorldModel]] Survey 提出的 "Levels × Laws" taxonomy 是当前最系统的框架：
- **能力层级**：L1 Predictor（单步转移）→ L2 Simulator（多步 rollout）→ L3 Evolver（自主修正）
- **约束域**：Physical（物理定律）/ Digital（软件逻辑）/ Social（社会规则）/ Scientific（科学规律）

**整体趋势**（2024-2026）：
1. Engineering-heavy，insight-light。HybridMemory、MultiWorld、GenerativeWorldRenderer 都是工程整合，缺少改变问题 formulation 的核心 idea
2. 唯一亮点是 SpatialEvo 的 DGE 设计——用确定性几何替代 model voting
3. **新发现**：World-R1 用 RL（Flow-GRPO）对齐 video generation 与 3D 约束；dWorldEval 用 progress token 编码任务完成状态
4. **新发现**：AgenticCache 发现 plan locality，cache-based plan reuse 降低 65% latency
5. Agentic RL 的 failure mode 诊断（如 RAGEN-2 template collapse）开始受关注
6. L3 Evolver 层级仍是 open problem——现有系统无法自主修正模型
7. **新发现**：[[2607-GigaWorld1]] 把 WM-as-evaluator 的成功标准从视觉保真改写为 evaluator–world outcome agreement；[[2607-BadWAM]] 揭示 WAM 的 action–imagination 解耦攻击面
8. **新发现**：digital domain（web/GUI）的 world model 生态成型，收敛于文本语义状态空间而非像素（[[2411-WebDreamer]]/[[2511-DreamGym]]/[[2510-UISimulator]]/[[2607-SeerGuard]]）
9. **新发现**：实时 video WM 的关键转向 control–memory–distillation co-design；但 camera-controllable renderer 与 action-conditioned simulator 必须分开，16 FPS 不等于物理或决策可用（[[2607-Wonder]]）
10. **新发现**：digital WM 出现两条显式 grounding 路线——外部 tutorial ground imagined rollout（[[2510-RWoM]]）与 executable object/procedure model（[[2607-ObjectCentricEnv]]）；前者延缓 compounding error，后者用代码执行保证内部一致性，但都没有解决语义正确性的外部审计
11. **新发现**：Environment Engineering 把 world model 从单一模型提升为 environment lifecycle 的一个组件，正确性以外的 diversity / complexity / fidelity 仍缺成熟评估（[[2606-EnvEngineeringSurvey]]）
12. **新发现**：生成保真与物理判别在同一模型上可以背离——[[2607-PhiZero]] 在 Physics-IQ 生成端第一却在 IntPhys2 Hard 接近随机基线，"视觉像 → 懂物理"的推定被直接反驳
13. **新发现**：WM 的用法从训练期扩展到推理期——[[2607-WorldActionPlanner]] 把 policy 降级为工具、规划全程在想象中完成，1 次想象胜过带 ground-truth reward 的 BoN-8

## 技术路线

### 1. Pixel-space Video Diffusion WM（future prediction 主脉）

**核心思路**：直接在 RGB（或其 VAE latent）空间用 diffusion/flow matching 建 $p(o_{t+1:} \mid o_{\le t}, c)$，$c$ 可以是 text / action / trajectory / camera / goal。backbone 迅速从 U-Net 迁向 DiT/MMDiT。

**代表工作与证据**：
- [[2408-GameNGen]]（ICLR 2025）：fine-tune SD 1.4，20 FPS 实时模拟 DOOM，**noise augmentation 解决 auto-regressive drift** 成为此后 AR video WM 的标配 trick
- [[2405-DIAMOND]]（NeurIPS 2024 Spotlight）：EDM-flavored 像素空间 diffusion WM 在 Atari 100k 拿 mean HNS 1.46，**EDM vs DDPM 的 $c_{\text{skip}}$ 稳定性分析**对所有长时序自回归生成都 transferable
- [[2501-Cosmos]]（NVIDIA, 2025-01）：**20M hour 视频 → 100M clips 的 industrial data curation + causal wavelet tokenizer**。**物理对齐（Isaac Sim 8 rigid-body scenes）大小模型基本不变**，首次给出 "scale 不能 alone 解决 physics" 的 negative evidence
- [[2405-Vista]] / [[2405-OccSora]]：自动驾驶 WM 的 video vs occupancy 两端
- [[2406-IRASim]]（ICCV 2025）：**Frame-level AdaLN conditioning**——把 text-to-video 的 video-level embedding 改为 per-frame action embedding
- [[2604-MultiWorld]]：Multi-agent multi-view video world model，用 MACM + GSE 保证多视角一致性
- [[2604-HYWorld2]]：多模态到 3D 世界的流水线（HY-Pano → WorldNav → WorldStereo → WorldMirror）
- [[2603-HybridMemory]]：动态主体出画再入画的 memory 机制，用 HyDRA 压缩 memory latent
- [[2604-WorldR1]]：RL（Flow-GRPO）对齐 video generation 与 3D 约束，不修改底层架构
- [[2505-DreamGen]]：明确把 video WM 定位为 offline data engine，从单一 pick-and-place teleop 数据 + neural trajectory 解锁 22 个新动词 / 10 个新环境
- [[2607-RynnWorldTeleop]]（DAMO）："数字遥操作"data engine——hand-pose 流实时驱动 40+ FPS action-conditioned WM 合成机器人 egocentric 视频，合成数据可零样本迁移真机；但 headline 质量（FVD 550, 2.8 FPS 双向版）与速度（40 FPS causal 版, FVD 1226）来自两个不同模型，且 Stage 2 仍需 1,800 条真机 MoCap 数据——是窄分布内的数据放大器而非"替代真机"
- [[2607-AlayaWorld]]：LTX-2.3 微调的可实时游玩视频世界（720p/24fps/1s chunk），双记忆（3D cache 几何持久 + 压缩帧历史）+ error bank（训练时注入 rollout 残差 artifact）应对长时程稳定性；零定量评估，处于 teaser 阶段
- [[2607-Wonder]]：以 Pixel-Space Coordinate Field 把 camera trajectory 渲染成 frame-aligned visual evidence，结合 full-fidelity sparse KV retrieval、Sparse Context Forcing 与 few-step autoregressive distillation；作者报告 minute-scale 16 FPS，I2V average/RPE 为 0.8558 / 0.0132 / 0.0784，但未交代 inference GPU/分辨率、无 component ablation，long-term memory 只靠 Figure 9 qualitative revisit。它证明的是 camera-controllable navigable renderer，不是 agent-action simulator

**路线内分支：reason-then-render**。[[2607-PhiZero]] 不在像素或 VAE latent 上直接做时序建模，而是先把视频压成自监督学到的离散"物理语言"（FSQ levels (8,5,5,5,5,5)、25K 词表，4 秒视频 → 256 个符号），由 Qwen3-VL-4B 在符号空间预测未来，再交给 Wan2.2-5B LoRA 扩散解码器渲染。动机是把"预测"与"渲染"解耦，让物理推理发生在低维离散空间。生成端指标支持这一设计：Physics-IQ Verified IQ-Score 41.2 > Cosmos3-Super 39.5 > Wan2.2-14B 32.2，PhyGround Physics 3.01，WorldModelBench Total 8.19。

但判别端没有同步跟上：IntPhys2 Overall 56.34、Hard split 仅 52.38（随机基线 50，V-JEPA 57.42），LikePhys 刚体 29.14 最好而流体 53.15 倒数第三，WS-IoU 27.6 落后。这直接落在路线 6（evaluator）与本表下方 planner 分支的要害上——那两种用法消费的正是判别能力，而不是画面质量。方法层的关键缺口是没有同数据同算力、仅移除中间表示的对照，21.2→41.2 的增益混淆了表示、数据与训练三个变量；离散表示本身是有损压缩（256 符号重建 PSNR 28.9，Wan2.2 VAE 用 44,800 token 达 37.7）；其 "zero-shot" 迁移仍需按源域微调 tokenizer，4 秒固定视界靠滑窗自回归外推，无代码发布。

**实际效果与优点**：视觉保真度天花板高（GameNGen 人类辨真伪仅 58–60%）；天然吸收 internet video prior；和成熟 video diffusion 工程栈复用。

**缺点与未解 gap**：
- **Action-following 不可靠**：[[2602-WorldVLALoop|World-VLA-Loop]] 展示 Cosmos-Predict 2 在错 action 下仍 hallucinate 成功——policy 在此类 WM 上做 RL 会 reward-hack
- **长时序 drift**：GameNGen 3 秒 context、DIAMOND memory bottleneck、World-VLA-Loop 主动放弃 LIBERO-Long——>200 帧后视觉/几何普遍漂移；Wonder 用固定 active set 检索 full-fidelity historical KV 把 active attention cost 与 history length 解耦，但 total KV storage 仍增长、revisit 无定量 metric，尚不能算解决
- **物理对齐不随 scale 解决**（Cosmos Tab. 20）：需 data curation 或 hybrid physics inductive bias
- **推理成本高**：典型 14B DiT naive 5.7 s/chunk，即使 38× 工程栈加速后仍需 2×GB200 才能 7 Hz 闭环

### 2. Latent-space / JEPA-style WM（implicit representation）

**核心思路**：不重建像素，只在 representation 空间做 mask-denoising / next-state prediction，让 predictor 学 "latent dynamics"，下游用 CEM / MPC 做 planning。

**代表工作**：
- [[2506-VJEPA2|V-JEPA 2]]（FAIR, 2025-06）：1M+ 小时视频 mask-denoising 预训练 → 冻结 + 62 小时 unlabeled Droid 视频训 action-conditioned predictor → CEM 在 latent 上 receding-horizon planning。Franka pick-and-place zero-shot 65–80% vs Octo 0–15%；**V-JEPA 2-AC 16 s/action vs Cosmos 4 min/action 且 success rate 反超**
- [[2501-RoboticWorldModel|RWM]]（ETH, NeurIPS 2025 Workshop Outstanding Paper）：GRU + 多步 autoregressive 训练学 legged robot dynamics；**architecture 不是关键，autoregressive training 才是**。在 ANYmal D / Unitree G1 上 zero-shot 硬件部署，reward 打平 250M-step model-free PPO 但只用 6M transitions
- [[2606-Orca]]（BAAI）：Next-State-Prediction 统一 world latent——unconscious（相邻帧 dense transition）+ conscious（event-conditioned）双路监督，冻结 backbone 后由 language/image/action decoder 读出。**frozen-readout probe 是"latent 是否真承载 state transition"的可反驳检验**；4B 在 OOD readout 超同量级专用 baseline，但 real-robot binary success 仅 6%
- [[2603-Memoir]]（TPAMI 2026）：contrastive RSSM world model 的 imagination 只作 **retrieval query** 而非 planning——预测不准时只是检索差一点，不会执行错误动作。IR2R +5.4 SPL + 8.3× 训练加速；但 imagination-based 检索相对朴素 state-based 仅 +0.61 SPL，主要收益来自选择性检索框架本身

**优点**：计算高效（V-JEPA 2 对 Cosmos 的 15× 推理优势）；数据效率极高；与 MPC/CEM 天然兼容。

**缺点**：像素生成能力弱；Goal specification 受限；Cross-embodiment 验证薄；Latent 不可解释。

### 3. 3D / 4D Generative WM（空间侧）

**核心思路**：把 WM 绑到显式 3D 表示（occupancy grid、3DGS、point cloud）上，用 diffusion 在 4D 体素/pointcloud latent 空间做未来生成。

**代表工作**：
- [[2405-OccSora|OccSora]]：nuScenes 上 DiT + 4D VQVAE 生成 16 s 驾驶 occupancy video，但小物体（VRU）重建崩塌
- [[2604-HYWorld2|HY-World 2.0]]（Tencent Hunyuan）：四阶段 pipeline panorama → WorldNav → WorldStereo → WorldMirror → 3DGS，端到端 712 s 生成可交互 navigable 3D 场景。**核心 insight 是 keyframe-latent VDM**
- [[2604-GenWorldRenderer|Generative World Renderer]]：ReShade + RenderDoc 从 AAA 游戏截取 G-buffer，fine-tune Cosmos-DiffusionRenderer
- [[2604-SpatialEvo]] (🔥 Rating 3)：3D 空间推理的答案可以从点云和 camera pose 确定性计算（DGE），不需要 model voting；w/o Physical Grounding → VSI-Bench 从 46.1 暴跌到 18.8
- [[2607-RynnWorld4D]]（DAMO）：**投影式 4D = 同步预测 RGB+Depth+Flow**，三分支 DiT + Joint Cross-Modal Attention，靠相机模型隐式承载几何、绕开显式 3D 表示；蒸馏 inverse-dynamics policy 在 6 个真机任务赢 5。但 RGB imaging quality 反而低于纯 2D Wan-2.1——几何优势来自显式监督 depth 分支而非表征范式胜利，且全链路建立在伪标注（Depth Anything 3 / DPFlow）上

**优点**：显式 3D 可验证几何；直接对接 CG 渲染 / 物理引擎。

**缺点**：Temporal dynamics / action 缺失（HY-World / OccSora 一代本质是 scene generator；[[2607-RynnWorld4D]] 的投影式 4D + policy 蒸馏部分补上 dynamics 与 action，代价是依赖伪标注几何）；数据稀缺；精度-压缩权衡。

### 4. Unified Video-Action / VLA+WM Joint Models（即 World Action Model, WAM）

**核心思路**：把 VLA（policy）、forward dynamics（WM）、inverse dynamics、video generation 统一进一个模型，通过 timestep / mask 切换。这条路线在 2026 被正式命名为 **World Action Model（WAM）**（DreamZero 定义），核心 claim 是 "world models are implicit policies"——video generation 天然具备的时空动态理解可直接转化为 motor control；WAM 不是 VLA 的替代而是演进，差异化优势在于能自然利用海量 action-free video 数据（UWM cotraining / DreamGen neural trajectories / Motus optical-flow latent action 各自验证了这一点），DreamZero unseen tasks 上比最优 VLA 高 2 倍以上的泛化正来自 world modeling。

**代表工作**：
- [[2504-UWM|UWM]]（RSS 2025, UW & TRI）：**"diffusion timestep ≡ soft mask"**——给 action 和 future obs 独立采样 timestep，推理时切换 policy / forward dynamics / inverse dynamics / video prediction 四个条件分布。DROID 2K 预训练 + 5 个 Franka 任务全面超 DP/PAD/GR1
- [[2512-Motus|Motus]]（Tsinghua, 2025-12）：**Mixture-of-Transformers + Tri-modal Joint Attention + UniDiffuser-style scheduler**，5-mode 真正跑通。RoboTwin 2.0 randomized +43% over π0.5
- [[2602-DreamZero|DreamZero]]（NVIDIA GEAR, 2026-02）：14B **World Action Model** 从 Wan2.1-I2V-14B 初始化，joint 预测 video + action；**38× 工程加速 + DreamZero-Flash** 做到 7 Hz 闭环。AgiBot G1 unseen-env+unseen-object 62.2% vs best pretrained VLA 27.4%（>2×）
- [[2512-GenieReasoner|GenieReasoner]]（AgiBot, 2025-12）：**FACT (Flow-matching Action Tokenizer)**——VQ-encoder 把动作压成离散 code，flow-matching decoder 重建高保真连续轨迹
- [[2604-M2VLA]]：Mixture of Layers + Meta Skill Module，保留 VLM 泛化
- [[2604-CFVLA]]：Coarse-to-fine action generation，83.0% real-robot success，-75.4% latency
- [[2607-FlowWAM]]（CASIA 等）：**HSV 编码 optical flow 作统一动作表示**——同时满足 video-native、稠密跨帧运动编码、可逆解码三性质；ablation 证明关键在"把 flow 映射进预训练 RGB 空间"（HSV vs raw (u,v) 差 17.5pt）；同一表示双向服务 policy mode 与 world-model mode，WorldArena Trajectory Accuracy 64.26 全场最佳
- [[2607-ABotM05]]（AMAP）：mobility + manipulation 统一 WAM，**frame-level latent action** 弥合粗粒度 video chunk 与控制频率的时间粒度错配（RoboTwin 87.60%→94.00%）；**Dream Forcing** 让 inverse dynamics 基于 self-dreamed video 而非 GT future 训练，直接缩小 train-test rollout gap；Composite-Unseen 仅 7.9%——长程组合泛化未解决
- [[2607-BadWAM]]（NUS）：WAM 的新攻击面——black-box 有界视觉扰动即可让 action 与 imagined future 解耦（LIBERO 96.5%→43.1%），imagination-preserving 变体在诱导错误 action 的同时保持想象接近 clean，简单 detector 召回仅 13–21%

**优点**：参数共享 / 部署简化；video prior 显式注入 action learning 的最自然方式。

**缺点**：算力门槛极高（Motus 18 000 GPU-hours、DreamZero 需 2×GB200）；边际收益不一定大（Motus Joint mode 比 VLA mode 只 +3pp）；高精度任务不 hold；action 与 imagination 的同步性可被攻击解耦（[[2607-BadWAM]]）——"部署前检查 imagined future 是否合理"的安全叙事失效。

### 5. WM-as-RL-Simulator / WM-Conditioned VLA (Loop 路线)

**核心思路**：用 video WM 替代物理仿真器跑 GRPO / PPO，或把 WM 预测的 future latent + value 作为 VLA policy 的 inference-time condition；policy 与 WM 迭代 co-evolve。

**代表工作**：
- [[2602-WorldVLALoop|World-VLA-Loop]]（Show Lab NUS, 2026-02）：**SANS dataset + DiT reward head + co-evolving loop**。核心诊断：video WM 的 action-following 偏差让它对错 action 也生成成功 → policy reward-hack。LIBERO 三 suite +12.7% SR；real-world 13.3% → 36.7% → 50.0% 两轮迭代
- [[2602-GigaBrain05M|GigaBrain-0.5M*]]（GigaAI, 2026-02）：**RAMP** 把 RECAP 从 advantage-only 条件化推广为 (future latent, advantage) 联合条件化；WM 联合预测 future state + value 比 only-value 精度更好
- [[2501-RoboticWorldModel|RWM + MBPO-PPO]]：legged 场景证明 "long-horizon PPO + learned model" 可行
- [[2606-RehearseVLA]]（CVPR 2026）：video WM 替代仿真器对 OpenVLA-OFT 做 RL post-training（LIBERO 5-demo 设定 79.6% vs SFT 74.85%），**VLM instant reflector 输出连续 reward**——解决 binary reward 下 RLOO advantage 塌缩，并提供实时终止信号；无 oracle 终止评测暴露 post-success 冗余动作破坏任务状态的隐性问题（OpenVLA-OFT -11.8pp）。局限：WM 训练数据仍靠 SFT policy 在仿真器内探索采集（"摆脱仿真器"存在循环依赖），且 WM 冻结、未处理 reward hacking——与 World-VLA-Loop 的 co-evolution 形成对照；"失败/次优数据是 WM 训练关键"与 SANS 结论互证

**优点**：把 WM 从"能生成什么视频"转向"能否闭环训 policy"的 actionable metric；co-evolving loop 给出 reward hacking 的实证 narrative。

**缺点**：仿真器质量瓶颈（video WM action-following 普遍弱）；Long-horizon 死穴（AR video drift >200 帧；RehearseVLA LIBERO-Long 仅 +0.8）；评估样本量小。

**推理期分支：WM-as-Planner**。上述用法都在训练期消费 world model（当仿真器、当 condition source），[[2607-WorldActionPlanner|WAP]] 把它整个挪到推理期：VLM agent 提出子目标，action-conditioned WM 在想象中评估，policy 降级为被调用的执行工具，构成 propose → optimize → search 闭环。让这一反转在视频骨干上可行的是 **pose-image conditioning**——候选动作先经正向运动学渲染成骨架图像、再由 VAE 编码送进 Wan-T2V-1.3B（4 视角 2×2 拼图，21 帧 @7FPS 历史 → 20 帧 @20FPS 未来），从而绕开低维动作向量与视频生成骨干之间的接口失配（与 [[2607-GigaWorld1]] 关于 channel-concat pose map 优于 cross-attention 的结论同向）。结果：compositional LIBERO-Long 四设定 72/68/78/70，对照 π0.5 的 4/0/0/0 与 cosmos-policy 全 0；新布局六设定 88/86/90/66/84/78，baseline 多为 0；zero-shot Robosuite 80/76 对纯 VLM planner 的 58/22。消融阶梯从 56/28/46/32 起，依次加入 global optimization、local search、policy rollout imagination 逐级抬升；1 次想象即胜过带 ground-truth reward 的 BoN-8（60 vs 42）——在这一设定下想象比重采样更省。

边界同样清楚：WAP 使用 URDF、相机标定与硬编码 GRASP/RELEASE 原语，"72 vs 0" 因此是"带特权信息的模块化系统 vs 端到端 policy"，不是 world model 单独的贡献，全文只有 Table 9 隔离了 world model 自身增益。世界建模指标（+11.4% ID / +16.8% 泛化）是 PSNR 与 LPIPS 的相对提升再取平均，其 limitation (g) 已自承该构造可疑。全部实验在仿真中完成、无真机，无 imagination horizon 扫描与误差累积测量，50 次 trial 无误差棒。

### 6. WM-as-Policy-Evaluator（Robotic Policy Evaluation）

**核心思路**：用 learned world model 作为 robot policy 的低成本 evaluation surrogate；成功标准是 **evaluator–world agreement**（同一 policy 在 real 与 WM rollout 中的 outcome 一致性），而非生成质量。

**代表工作**：
- [[2607-GigaWorld1]] (🔥 Rating 5, GigaAI)：**WMBench**——2,989 条 paired real/WM rollout + 324K challenge rollout 的 controlled study。结论：evaluator 质量取决于 long-horizon action fidelity、可迁移 physical prior、空间对齐的 action control（channel-concat Trajectory Accuracy 0.3528 vs ControlNet 0.2566 vs cross-attention 0.1620），而非短期视频观感；综合 evaluator score 超最强通用 Wan baseline 14.9%；VLM-assisted WMES 与人类评分 exact agreement 87.80%
- [[2604-dWorldEval]] (Rating 2)：discrete diffusion WM + **progress token**（progress=1 判 success）+ 统一 token space + sparse keyframe memory

**关键 gap**：video model 对 contact-sensitive failure 有 **optimistic bias**（GigaWorld-1 closed-loop 观察）——这是 policy evaluator 最危险的误差类型，optimistic evaluator 会系统性放行危险 checkpoint；false-success rate 应作为第一汇报指标。

### 7. Digital-Domain World Model（Web/GUI）

**核心思路**：数字环境的 world model 收敛于**文本语义状态空间**（NL state delta / accessibility tree / 语义后果描述）而非像素——planning、安全判定、RL 训练依赖的是功能性状态变化而非视觉保真。理论依据是 [[2511-DreamGym]] Theorem 1：合成环境上训练的策略在真实环境的改进下界只由 reward 保真度 ε_R + 转移域一致性 ε_P 决定，与 raw-state 重建误差无关。

按用途分类：

| 用途 | 代表工作 | 关键证据 |
|---|---|---|
| Planning / lookahead | [[2411-WebDreamer]]（TMLR 2025）、[[2600-MobiledreamerGenerativeSketchWorld]]、[[2510-RWoM]] | live 网站动作不可逆 → 用 LLM 想象替代真实 tree search。R-WoM 先诊断 LLM 的 next-state/milestone 尚可、full-procedure planning 无检索很弱，再把 tutorial 注入 world-model rollout 而非 policy context；OSWorld/WebArena 子集相对 WebDreamer 最多 +23.4%/+16.3%，但增益只撑到 horizon≈3、主结果限 tutorial-covered 子集 |
| Pre-execution guard | [[2607-SeerGuard]]、[[2602-WAC]] | SeerGuard 重标注发现 **91% high-risk 任务是"良性指令 + 危险执行"**→ 安全评估必须下沉到 action 级；8B SFT 语义 next-state 预测超 235B 基座（Next-State-QA 0.762 vs 0.651）。WAC 通用任务纠错仅 +1.8pp / +1.3pp——guard 用途中安全判定比任务纠错收益大 |
| RL simulator | [[2511-DreamGym]]（Meta） | LLM 经验模型（CoT 推理生成转移 + reward）+ reward-entropy 课程：WebArena GRPO 7.3→13.3 零真实交互，S2R 用 <10% 真实数据反超 from-scratch；第一手证词——WebArena 真实 RL 只能 4 并发 + 手动 reset |
| Trajectory synthesis | [[2510-UISimulator]]、[[2507-WebSynthesis]] | UI-Simulator：同等真实测试环境暴露下合成经验达 OS-Genesis 的 4×（WebArena），\$0.02–0.05/轨迹；WebSynthesis：WM-guided MCTS 合成轨迹，**rollback-only 训练无效（1.49%）——rollback 信号必须与成功轨迹配合** |
| Image-based simulation | [[2500-UisimInteractiveImageBased]] | 两阶段 UI simulator（layout prediction → layout-to-image），layout-first 符合 UI 结构化本质 |
| Online executable model / memory | [[2607-ObjectCentricEnv]] | object knowledge（Python 类）+ procedure knowledge（必须 import object model）+ episode 后全 procedure re-execution gate；三 text-interaction benchmark 平均排名 1.75，但 verification 只保证 executable consistency，不保证语义正确，且未覆盖 GUI/开放 schema |

**与 robotics WM 的分野**：digital WM 的瓶颈不在算力而在**转移幻觉与 reward 无外部审计**——DreamGym 的经验模型既当转移函数又当 reward 函数、无独立 verifier；UI-Simulator 的 LLM transition 有状态幻觉。robotics 侧的 action-following 问题在这里表现为"对不存在的页面状态过度自信"。

### 8. Planning Efficiency (相关方向)

**代表工作**：[[2604-AgenticCache]] (Rating 2)

**核心思路**：利用 plan locality，cache-based plan reuse 替代 per-step LLM calls。+22% success rate，-65% latency，-50% token usage。

### 9. Conceptual Framework (Survey)

**代表工作**：
- [[2604-AgenticWorldModel]]：Levels × Laws taxonomy（🔥 Rating 5，最系统的 Survey）
- [[2411-WorldModelSurvey|Ding et al. 2024/CSUR]]：implicit/predictive 二分 + cloud-side / edge-side 切分
- [[2607-PixelsToStates]]（Alaya Lab）：用 game engine 的 **action–state–observation loop** 重构 interactive WM 版图——真正缺口在显式 state、规则驱动 transition、持久后果与 **consequence latency**（结果应在规则定义的时刻出现而非输入后立即显现），不在画面生成；附 Black Myth: Wukong 90+ 小时 frame-aligned engine-state 数据引擎，为 explicit-state WM 提供稀缺监督
- [[2606-EnvEngineeringSurvey]]：以 environment lifecycle 而非单个 model 组织领域——八属性二分 × 八 domain → symbolic/neural synthesis → correctness/diversity/complexity/fidelity evaluation → agent/environment co-evolution。它补充 Levels × Laws 的“能力/约束”视角：world model 只是 neural environment synthesis 的 pixel/word/latent 三层之一；survey 自身也承认 correctness 之外三项质量维度 under-researched，co-evolution 仍是未来方向而非已完成机制

**路线间对比小结**：

| 路线 | 代表 | 主要 use case | 推理代价 | 主要 open gap |
|---|---|---|---|---|
| Pixel video diffusion | Cosmos / DreamGen / IRASim / Wonder | Data engine / Evaluator / camera exploration | 14B × 多步 → 秒级；Wonder 报 16 FPS（硬件未披露） | Action-following / physics / AR drift / total KV growth |
| Latent JEPA | V-JEPA 2 / RWM / Orca | Agent brain / MPC | 16s → ms 级 | Goal spec / cross-embodiment / 不生成像素 |
| 3D/4D generative | HY-World 2.0 / OccSora / RynnWorld-4D | Scene generation / driving sim | 分钟级/场景 | dynamics 依赖伪标注几何 / 小物体精度 |
| Unified VLA+WM | UWM / Motus / DreamZero / FlowWAM / ABot-M0.5 | VLA policy backbone | 百 ms 级（工程后） | 算力门槛 / unify 必要性 / action–imagination 同步性 |
| WM-as-RL-simulator | World-VLA-Loop / GigaBrain-0.5M / RehearseVLA | VLA RL post-train | 30 h / 任务级 | Action-following / 样本量 |
| WM-as-planner（推理期） | WAP | test-time 子目标搜索，policy 作工具 | 每候选一次视频生成 | 增益未与特权信息分离 / 无真机 / 无 horizon 扫描 |
| WM-as-evaluator | GigaWorld-1 / dWorldEval | Policy checkpoint 筛选 | 视频生成级 | contact-sensitive failure 的 optimistic bias |
| Digital text/code-space WM | DreamGym / UI-Simulator / WebDreamer / SeerGuard / R-WoM / OCM | Planning / RL sim / 轨迹合成 / safety guard / executable memory | LLM 推理级（\$0.02–1/轨迹） | 转移幻觉 / reward 无外部审计 / executable≠correct |

## Datasets & Benchmarks

| Dataset | 规模 | 评估指标 | SOTA | 特点 |
|:--------|:-----|:---------|:-----|:-----|
| HM-World | 59K 视频 | Subject Consistency, Background Consistency | HyDRA 0.926/0.932 | UE5 渲染，exit-entry 场景 |
| Agent-World | 1,978 环境 / 19,822 工具 | MCP-Mark | 14B 13.3% | MCP servers + PRD 采集 |
| GenerativeWorldRenderer | 4M 帧 RGB+G-buffer | FID, LPIPS | DiffusionRenderer | 游戏截取 |
| VSI-Bench | - | Spatial Reasoning | SpatialEvo 46.1 | 3D 空间推理 |
| ItTakesTwo | 多人游戏 | FVD, PSNR | MultiWorld | Multi-agent gaming |
| RoboFactory | 多机械臂 | Action Accuracy | Concat-View 92.0 | Robot manipulation |
| LIBERO | - | Success Rate | dWorldEval, CF-VLA 83.0% | Robotic policy evaluation |
| RoboTwin | - | Success Rate | 87.02% (Motus，超 π0.5 45%) | Robotic manipulation |
| CALVIN | - | Success Rate | CF-VLA | Long-horizon manipulation |
| Push-T | 推块任务 | IoU | 0.961 (IRASim model-based planning) | Planar manipulation，policy evaluation 与 GT simulator 相关度 0.99 |
| DreamGen Bench | 22 novel behaviors | Success Rate | DreamGen | World model 泛化评测（新动词/新环境解锁） |
| TokenBench | Video tokenizer | PSNR / FVD | PSNR 35.85 (Cosmos) | Video tokenizer 质量评测 |
| WMBench | 2,989 paired real/WM rollouts, 8 任务类 | WMES / evaluator–world agreement | GigaWorld-1-Plus 0.6834 | policy evaluation 专用，episode-disjoint split（[[2607-GigaWorld1]]） |
| WorldArena | 121 帧 @24fps | EWMScore / Trajectory Accuracy | FlowWAM 63.71 / TrajAcc 64.26 | action-conditioned 视频 WM 评测 |
| MobileSafetyBench | 250 任务（150 high-risk） | RCS / SUS | SeerGuard RCS 0.130 | GUI agent 安全；91% 风险在 action 级而非 instruction 级 |
| Black Myth: Wukong data engine | 90+ 小时 30FPS | - | - | frame-aligned engine state + raw control + RGB/depth（[[2607-PixelsToStates]]） |
| Wonder I2V / V2V | 1,000 images×5 trajectories / 500 videos×6 trajectories | VBench average + translational/rotational RPE | I2V 0.8558 / 0.0132 / 0.0784；V2V 0.8527 / 0.0187 / 0.1119 | 作者自建、未给 release URL；V2V 仅一 baseline；camera control 非 agent action（[[2607-Wonder]]） |
| Physics-IQ | 生成式物理一致性 | Verified IQ-Score | 41.2（[[2607-PhiZero]]，> Cosmos3-Super 39.5 / Wan2.2-14B 32.2） | 评的是"生成得像不像物理"，与判别类指标可给出相反排序 |
| IntPhys2 | 判别式直觉物理（violation-of-expectation） | Accuracy | Overall 56.34 / Hard 52.38（[[2607-PhiZero]]；随机 50，V-JEPA 57.42） | 生成端 SOTA 在 Hard split 逼近随机——WM 用作 planner/evaluator 时应以此类指标验收 |
| LikePhys / WorldModelBench | 分材料物理合理性 / 综合 | 各自 score | Rigid 29.14 最佳、Fluid 53.15 倒数第三；Total 8.19（[[2607-PhiZero]]） | 物理能力按材料分层，聚合分掩盖流体等薄弱项 |

## Key Takeaways

1. **SpatialEvo 的 DGE 是唯一真正的 insight**——确定性几何替代 model voting，但适用场景极窄
2. **L3 Evolver 层级仍是 open problem**——现有 world model 无法自主修正
3. **Video World Model 的 memory 机制有问题**——HybridMemory 发现动态主体出画再入画会消失/扭曲
4. **Agent-World 的 environment scaling 有价值**，但 MCP-Mark 绝对分数暴露问题
5. **UI World Model 的 layout-first 设计是对的**——UISim 的 decomposition 符合 UI 结构化本质
6. **Progress token 是有趣的新 idea**——dWorldEval 将任务完成状态编码进 world model，与 L3 Evolver 概念关联
7. **RL for World Model 正在兴起**——World-R1（Flow-GRPO）、SpatialEvo（GRPO）都用 RL 而非架构修改
8. **Plan locality 有价值**——AgenticCache 发现 embodied tasks 的 plan locality，cache-based reuse 显著降低 latency
9. **VLA efficiency 优化显著**——CF-VLA 83.0% success + -75.4% latency
10. **Action-following 是 video WM 的致命伤**——World-VLA-Loop 证明 video WM 对错 action 也生成成功 → policy reward-hack，SANS 式 near-success 数据 + reward head 是初步答案
11. **Latent vs pixel 路线之争进入可比较阶段**——V-JEPA 2 给出 15× 计算优势 + success rate 反超 Cosmos；DreamZero 反过来用 14B pixel WAM 达到 62.2% task progress
12. **WM × VLA 的六种耦合方式全部被实证验证**——offline data engine → inference-time latent conditioning → joint model → RL simulator → evaluator → test-time planner（[[2607-WorldActionPlanner]]）
13. **scale 不能 alone 解决 physics**——Cosmos 7B vs 14B 在 rigid-body benchmark 上 IoU 基本不变（0.59 vs 0.60）
14. **"video model as data engine" 是可 scale 的新 sub-paradigm**——DreamGen 从单一 pick-and-place teleop 数据解锁 22 个新动词 / 10 个新环境
15. **PID > RL 在 sparse reward 场景**——RWM 的 autoregressive training + imagination-PPO 可换 250M transitions 的 model-free 水平
16. **Evaluator 质量 ≠ 视觉保真**——[[2607-GigaWorld1]] 用 paired rollout 证明 evaluator–world agreement 取决于 long-horizon action fidelity + physical prior + 空间对齐 action control；channel-concat 条件化的 Trajectory Accuracy 是 cross-attention 的 2.2×
17. **WAM 的"可检查想象"安全叙事被击穿**——[[2607-BadWAM]] 证明 black-box 视觉扰动可让 action 与 imagined future 解耦（96.5%→43.1%）；runtime monitor 应检查"action 能否实现 predicted future"而非 future realism
18. **Digital WM 不需要像素保真**——[[2607-SeerGuard]]（8B 语义预测超 235B 基座）、[[2511-DreamGym]] Theorem 1（ε_R+ε_P 与重建误差无关）、[[2510-UISimulator]]（合成经验 4× OS-Genesis）从安全/理论/训练三个角度收敛到同一结论
19. **"降级使用"是 WM 落地的普遍模式**——预测精度不足时选容错性高的用途：[[2603-Memoir]] 用 imagination 作 retrieval query（错了只是检索差一点）、[[2411-WebDreamer]] 只做 H=1 lookahead、[[2607-SeerGuard]] 只做二分类风险判定；对 WM 精度要求越低的用途落地越早
20. **失败/次优数据是 WM-as-simulator 的关键 ingredient 获再次确认**——[[2606-RehearseVLA]] 探索数据是最大单因素（Goal 68.4→86.4），与 World-VLA-Loop 的 SANS 结论互证
21. **Memory 必须分开讨论 storage、active compute 与 semantic faithfulness**——[[2607-Wonder]] 固定 active KV set 只解决 attention cost，不限制 full historical KV storage；[[2603-HybridMemory]] 测动态主体 exit–reentry、Wonder 只给静态 revisit qualitative case，两者尚不能互相替代
22. **Digital WM 的 grounding 开始分化为 external prior 与 executable structure 两条路线**——[[2510-RWoM]] 用 tutorial 把 imagined rollout 延长到约 3 steps，[[2607-ObjectCentricEnv]] 用 object/procedure code + re-execution gate 维护一致性；共同边界是“有依据/能执行”仍不等于环境语义真实
23. **World model 不能脱离 environment lifecycle 单独评估**——[[2606-EnvEngineeringSurvey]] 将 model 放回 modeling→synthesis→evaluation→application 闭环，并指出除 correctness 外的 diversity/complexity/fidelity 仍 under-researched；这解释了为何视觉保真、action faithfulness 与 downstream policy success 长期互不等价
24. **生成保真不蕴含物理判别**——[[2607-PhiZero]] 在 Physics-IQ 拿下 41.2（生成端第一）的同一模型，IntPhys2 Hard 只有 52.38（随机基线 50），LikePhys 流体倒数第三。Takeaway 16（evaluator 质量 ≠ 视觉保真）由此从 evaluator 场景推广为 WM 的一般性质：凡消费判别能力的用途（planner / evaluator / safety guard）都不能用生成指标验收，而分材料、分难度的判别 split 是目前唯一能暴露这一差距的手段
25. **WM 的用法从训练期扩展到推理期，且想象比重采样更省**——[[2607-WorldActionPlanner]] 把 policy 降级为工具、规划全程在想象中完成，1 次想象胜过带 ground-truth reward 的 BoN-8（60 vs 42）；但该系统带 URDF、相机标定与硬编码抓放原语，"72 vs π0.5 的 4" 是模块化+特权信息 vs 端到端的对比，仅 Table 9 隔离了 world model 自身贡献——归因清楚前不可引作 WM 的能力证据

## Open Problems

1. **Action-following faithfulness**：video WM 对错 action 也生成成功，policy 一定能找到 WM 盾区做 reward hacking。SANS 式 near-success 数据 + reward head 是初步答案，但是否 scale 到 long-horizon / multi-agent / deformable 尚未验证；[[2606-RehearseVLA]] 冻结 WM 且不处理该风险，[[2607-GigaWorld1]] 观察到 contact-sensitive failure 的 optimistic bias——同一问题在 evaluator 侧同样存在
2. **Physics alignment 不随 scale 解决**：Cosmos 7B vs 14B 在 rigid-body benchmark 上 IoU 基本不变；候选方向：(a) hybrid physics (Genesis/PhysGen)；(b) RL on intuitive physics MCQ (Cosmos-Reason1)——但第二条只涨 VLM-level reasoning，不 carry over 到 video generation；(c) 离散符号中间表示 + reason-then-render（[[2607-PhiZero]]），生成端 Physics-IQ 41.2 领先，但缺同数据同算力、仅移除中间表示的对照，21.2→41.2 混淆表示/数据/训练三变量，且判别端未同步（IntPhys2 Hard 52.38）。三条候选都还没有把"物理"从"看起来像物理"里分离出来
3. **Long-horizon drift**：所有 autoregressive video WM 超过训练 horizon 都退化——GameNGen 3 秒、DIAMOND frame-stacking、World-VLA-Loop 200 帧、OccSora 离开 32 帧 FID 飙 200+。Explicit compressed memory、retrieval-based context、LLM-style KV cache + streaming 都是候选，但没有任何一种在 robot-relevant setting 上 demonstrated；[[2607-AlayaWorld]] 的 error bank + 双记忆零定量评估，[[2607-Wonder]] 的 full-fidelity sparse KV 只固定 active attention 且长期一致性仍为 qualitative evidence。后续必须同时报告 quality/control/revisit metric、latency 与 total memory 随 horizon 的曲线
4. **Latent vs pixel 的路线之争**：V-JEPA 2 给出 15× 计算优势 + success rate 反超 Cosmos；DreamZero 反过来用 14B pixel WAM 达到 62.2%。[[2607-PhiZero]] 提出第三种位置——在离散符号空间推理、再渲染回像素，兼取 latent 的低维推理与 pixel 的可视化输出，但它同时是这条路线最直接的警示：判别能力没有随生成能力一起上来（IntPhys2 Hard 52.38 落后于纯 latent 的 V-JEPA 57.42）。**真正的 open question**：long-term 哪一条路径 scale 更好？或三者按用途分工（cloud-side pixel WM 做 data engine，符号中间层做 planner，edge-side latent WM 做 on-device MPC）？
5. **Cross-embodiment transfer 真能靠 video 做到吗？**：DreamZero 的 12 min 人类 egocentric / 20 min YAM robot video → unseen task +16pp 是至今最强信号；但 humanoid 五指手 vs bimanual gripper 级的 morphology gap 尚未被 video WM 路线 attack
6. **Benchmark metric 的 unresolved confound**：video fidelity (FID/FVD) ↔ physical faithfulness (VBench-2.0, PhysBench) ↔ policy success (DreamGen Bench / LIBERO SR) 三者相关但不等价。系统化的"哪个 metric 评 WM 公平" 的框架尚未建立。[[2607-PhiZero]] 把 confound 收窄成一个可操作的判据：生成式（Physics-IQ）与判别式（IntPhys2 Hard）在同一模型上给出相反排序，因此 WM 论文至少应同时报告两类指标，并按材料/难度分层——聚合分会掩盖流体等薄弱项（LikePhys 刚体第一、流体倒数第三）
7. **WM × VLA 耦合方式的 trade-off space**：当前 6 种耦合方式都有代表工作（offline data engine / inference-time latent conditioning / joint model / RL simulator / evaluator / test-time planner），但没有 head-to-head 比较。在同等 compute / data 预算下，哪种耦合方式对 sample efficiency 最敏感？新加入的 planner 分支还带一个专属问题：[[2607-WorldActionPlanner]] 显示 1 次想象胜过 BoN-8，但没有 imagination horizon 扫描，也没有测误差累积——想象的收益在多长 horizon 上翻转成 drift 的代价，目前无数据
8. **开源 vs 工业化：可复现性断层**：Cosmos 10 000 H100 × 3 个月、Motus 18 000 GPU-hours、DreamZero 2×GB200——任何"主脉络" WM 都远超学术实验室预算
9. **Agent memory 与 World Model 的边界**：OpenWorldLib 把 long-term memory 写进 world model 定义，但 Memory 接口留空。[[2603-Memoir]] 用 imagination 作 retrieval query，[[2607-Wonder]] 用 query-summary 选 full-resolution historical KV，[[2607-ObjectCentricEnv]] 则把 object/procedure memory 直接做成 executable environment model；三者分别是“想象→检索”“生成→记忆”“记忆→模型”，尚无统一接口或同任务比较
10. **L3 Evolver 实现**：当 prediction 失败时如何自主修正模型？
11. **World Model 的 failure mode 系统性分析**：RAGEN-2 发现 template collapse，但其他 failure mode 未知
12. **Deterministic vs Probabilistic 的 trade-off**：DGE 适用边界如何扩展？
13. **World Model for GUI Agent 的 grounding 问题**：如何与 grounding robustness 结合？
14. **Progress token 作为 L3 Evolver 信号**：能否用于自主修正触发？
15. **Plan locality 的适用边界**：是否适用于所有 embodied tasks？
16. **WAM 的 scaling laws 未知**：DreamGen 展示 log-linear scaling 趋势，但 Motus/DreamZero 的 scaling behavior 未被系统研究；video vs action 之间的 optimal compute allocation 无结论——这决定 WAM 范式是否值得学术实验室以外的算力投入（参见 Open Problem 8 可复现性断层）。
17. **WAM 的 action–imagination 同步性**：[[2607-BadWAM]] 证明两条 pathway 可被有界视觉扰动解耦，简单 augmentation-consistency detector 召回仅 13–21%；action-conditioned consistency verifier / 可执行 inverse-dynamics check 是候选方向，但无实现
18. **Explicit state 如何驱动生成**：[[2607-PixelsToStates]] 指出 accumulated-condition outcome、out-of-view consequence persistence、rule-defined consequence timing 三类缺失都指向被隐式化的 game state，但"explicit state 闭环驱动 video generation"仍是留白；迁移到真实世界还需 state estimator
19. **Digital WM 的转移幻觉与 reward 审计**：[[2511-DreamGym]] 的经验模型既当转移函数又当 reward 函数、无外部审计；[[2510-RWoM]] 的 tutorial grounding 只把 compounding error 推迟到 horizon≈3，[[2607-ObjectCentricEnv]] 的 re-execution 只保证 runnable consistency。"合成转移 + 真实 verifier"的混合方案是否优于两个纯路线未验证
20. **Environment quality 的非 correctness 维度如何操作化**：[[2606-EnvEngineeringSurvey]] 明确指出 diversity、complexity、fidelity under-researched；需要把这些维度变成可重复测量，并与 agent learning progress、reward hacking 与 sim-to-real error 建立因果而非相关关系

## 调研日志

- **2026-08-02 survey-refresh**：并入 2 篇（[[2607-PhiZero]] / [[2607-WorldActionPlanner]]，均 full-text + source-checked）。结构性变化：路线 1 新增 reason-then-render 分支（离散"物理语言"中间表示 + 扩散渲染），路线 5 新增推理期 WM-as-Planner 分支并在路线对比表 +1 行；Overview 趋势 +12/13；Key Takeaways +24（生成保真不蕴含物理判别，把 Takeaway 16 从 evaluator 场景推广为一般性质）、+25（推理期规划）；Takeaway 12 由五种耦合改为六种；Open Problems 2/4/6/7 更新；Benchmarks 表 +Physics-IQ / IntPhys2 / LikePhys-WorldModelBench 三行。未刷新配图。
  - **证据边界**：Phi-Zero 缺同数据同算力、仅移除中间表示的对照，21.2→41.2 的增益混淆表示/数据/训练；其 "zero-shot" 迁移仍需按源域微调 tokenizer，无代码发布。WAP 全仿真无真机，使用 URDF、相机标定与硬编码抓放原语，"72 vs 0" 不可读作 world model 单独贡献（仅 Table 9 隔离）；+11.4%/+16.8% 为 PSNR 与 LPIPS 相对提升再平均，论文自承构造可疑。
- **2026-07-29 survey-refresh**：并入 4 篇（[[2510-RWoM]] / [[2607-ObjectCentricEnv]] / [[2606-EnvEngineeringSurvey]] / [[2607-Wonder]]）。路线 1 新增 camera-controllable video WM 的 control–memory–distillation co-design 与严格证据边界；路线 7 补 external-tutorial grounding 与 executable object/procedure model；路线 9 引入 environment lifecycle 视角；Benchmark +1，Key Takeaways +21–23，Open Problems 更新 3/9/19 并新增 20。无新平行 taxonomy，未刷新配图。
- **2026-07-21 survey-refresh**：并入 17 篇（WebDreamer / DreamGym / RynnWorld-Teleop / WAC / UI-Simulator / WebSynthesis / RynnWorld-4D / AlayaWorld / Memoir / FlowWAM / RehearseVLA / SeerGuard / ABot-M0.5 / BadWAM / Orca / GigaWorld-1 / PixelsToStates），skip 3 篇非 WM（LaMem-VLA / DART / Xiaomi-Robotics-1）。结构性变化：路线 6 更名 WM-as-Policy-Evaluator 并以 GigaWorld-1 为旗舰；路线 7 扩为 Digital-Domain World Model（Web/GUI）五用途表；路线对比表 +2 行；Key Takeaways +16–20；Open Problems +17–19。
- **2026-07-20 合并 WorldActionModel-Survey**（Supervisor 指示同方向 survey 整合）：该 survey 的 8 篇论文（DreamZero/UWM/Motus/DreamGen/World-VLA-Loop/IRASim/Cosmos/RWM）本已全部覆盖于路线 1/2/4/5，属完全子集。本次仅并入其独有内容：路线 4 标题补 WAM 命名与 "world models are implicit policies" 范式定义、action-free video data 优势论证；Benchmark 表 +Push-T/DreamGen Bench/TokenBench；Open Problem +16（WAM scaling laws）。原文见 git history。
- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 4 篇（Archive）+ 2 篇（Papers）+ 新创建 6 篇 + 补充 4 篇（World-R1, dWorldEval, EmotionPose, AgenticCache）+ VLA 相关 3 篇（M²-VLA, Tube Diffusion Policy, CF-VLA）= 19 篇
- **未能获取**: 无（基于已有月度总结和 candidates.json 创建笔记）
- **MindFlow 合并**: 2026-04-30，从 MindFlow repo 合并 WorldModel-Survey，新增 5 条技术路线（Pixel video diffusion / Latent JEPA / 3D-4D generative / Unified VLA+WM / WM-as-RL-simulator）、6 条 Key Takeaways、7 条 Open Problems、路线对比小结表
