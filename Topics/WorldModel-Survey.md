---
title: World Model Survey
tags: [world-model, agent, simulation, planning, MBRL, VLA, diffusion-policy, cross-embodiment]
date_updated: "2026-09-07"
year_range: 2024-2026
papers_analyzed: 63
keywords: [world model, video prediction, dynamics model, mbrl, world action model, action-conditioned, diffusion policy, cross-embodiment]
domain_map: WorldModel
---
## Overview

World Model 是 AI Agent 的环境建模能力——预测行动后果、模拟状态转移、支持 counterfactual planning。从 MBRL 的 transition model 到 Video Generation 的 action-conditioned prediction，再到 GUI/Web Agent 的 environment simulator，不同社区对"world model"有不同理解。

**核心洞察**：[[2604-AgenticWorldModel]] Survey 提出的 "Levels × Laws" taxonomy 是当前最系统的框架：
- **能力层级**：L1 Predictor（单步转移）→ L2 Simulator（多步 rollout）→ L3 Evolver（自主修正）
- **约束域**：Physical（物理定律）/ Digital（软件逻辑）/ Social（社会规则）/ Scientific（科学规律）

> **术语注记**：[[Papers/2608-WorldProxy]] 复用了同一套 L1/L2/L3 记号，但含义是**对 agent 的介入深度**（L1 推理期提示 / L2 训练期信号 / L3 agent-proxy 共演化），与此处的**内在能力**刻度正交（其原文自述 "rhyme without being identical"）。本文凡写 L1/L2/L3 均指 Chu 的能力刻度；需引用介入深度时写 Proxy-L1/L2/L3，避免两套刻度混淆。

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
14. **新发现**："被预测的未来该是什么表示"成为 WAM 的显式设计轴——[[2607-STWAM]] 在 VAE 未来之外并行预测 DINO 语义未来，[[2607-N0TWAM]] 把触觉与视觉一起当生成目标；但两篇的消融同向指向一个反直觉结论：新增的那条**预测**通路不是主要收益来源
15. **新发现**：world prediction 进入 RL 的 critic 侧——[[2607-WCM]] 让 critic 在预测 return 的同时预测下一帧 latent，drop-in 替换四种 VLA RL 算法的原 critic；λ=0 的 history-ViT 对照把增益与"多看几帧"分开
16. **新发现**：Levels × Laws 中长期空置的 **Social 约束域**出现第一篇正面工作——[[2607-MentalWorldModeling]] 把 belief/goal/intention 升格为随动作演化的状态变量；但其消融显示移除 physical 通道（−16.5）比移除 mental 通道（−12.1）代价更大
17. **新发现**：评测侧出现 **explicit fulfillment vs. inherent reactivity** 的切分——[[2608-WorldExam]] 把"指令写明的后果"与"须自行推断的后果"分开报告，得到一次方向反转：action 接口控制更准却让世界毫无反应，language 接口反之；同一批模型的视觉质量层几乎不含区分度（General 79.64–81.04），任务层却铺开 25 分（39.85–65.02）
18. **新发现**："world model 只当训练信号、部署期整体丢弃"在四篇独立工作上收敛为 WAM 的默认工程形态（[[2608-SimWAM]] 驾驶 / [[2608-JEPAWAM]] latent 空间 / [[2608-WorldTokens]] 表示瓶颈 / [[2608-MobileWAM]] mobile manipulation，加上此前的 [[2607-STWAM]]），且三篇的消融从不同方向指向同一耦合拓扑结论：监督应经共享表示塑形 policy，而不是把预测的未来喂给 policy（详见路线 4 分支）
19. **新发现**：digital WM 出现"内化进 policy 权重"的极端形态（[[2608-EnvACE]]）与"学出来的 RSSM 做 25ms 级 pre-execution guard"（[[2608-DreamGuard]]）；两者与 GUI 侧的 [[2608-AppDeltaWorld]] 共享同一未解缺口——彩排/渲染保真度从未被直接测量，状态等价判定缺失
20. **新发现**：诊断式评测出现第二条切法——[[2608-WorldSimProbe]] 沿"动作 → 已实现运动 → 环境响应"的因果链把 rollout 拆成两个可观测条件，得到三条跨模型一致的读数：faithfulness 随控制偏离训练分布单调退化、contact 失败在其审计样本中全部是幻觉出接触而非漏掉接触、VLM 二元 rollout judge 在 OOD control 上判 91.7% 通过而人类只判 42.2%
21. **新发现**：长时程 visual persistence 的第一约束被重新定位——[[2608-WorldTrace]] 指出记忆不是没存下而是读不到（rollout 超出训练 horizon 后 RoPE 的 query–key offset 落到训练分布外），恢复可寻址性无需重训即可在 O(1) cache 预算下拉回 revisit 一致性；同路线的 [[2607-ABotWorld0]] 用 bounded KV cache + rolling eviction 换到消费级 GPU 的实时性，代价正是 memory 成为其七个评测维度里相对最弱的一项
22. **新发现**：显式 3D 表示补上了此前缺的 action conditioning 与 scaling 证据——[[2606-PointWorld]] 把 state 与 action 统一为 3D point flow，模型（50M→1B）与数据（5%→100%）两轴都给出 log-linear 的预测误差下降；4D 生成侧则把接口从 RGB 上移到 shared VAE latent（[[2608-LatentTo4D]]）

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
- [[2607-ABotWorld0]]（partial 核查，下列均为 source-verified 行）：把"实时"的口径讲清楚的一份部署报告。动作接口是每帧 8 维键盘 multi-hot（每 4 帧打包成 32 维 token，在 patchify 阶段加性注入 Wan2.2 DiT），训练走 teacher forcing → ODE distillation → LongForcing 三段蒸馏，部署侧 LightVAE、低比特 DiT、Fast-RoPE、bounded KV cache 协同，单张 RTX 5090 上 1280×704、最高 16 FPS、按键到首帧可用 1.2 s、峰值显存 ≤19.3 GiB。逐配置的系统消融比总分更有信息量：只换注意力 kernel 仍然 OOM，第一个可跑配置由 LightVAE 给出（9.117 FPS / 20.491 GiB），16 FPS 来自最激进的 MXFP4，而作者声明的质量优先工作点 FP8 是 12.4–13.3 FPS。能力侧没有拿到任何一项第一：WorldRoamBench 七个子维度全部第二或第三，相对差距最大的一项正是 memory（0.5041 对 Genie 3 的 0.6073 与 HappyOyster 的 0.6309），而 rolling eviction 按设计就丢弃窗口外历史、reference-character memory 只覆盖可控角色的外观一致性。边界：该 benchmark 的作者与本文 Benchmark Team 重叠，"与 Genie 3 打平"应按自家评测读；表内 LingBot-World（14B）与 HY-World 1.5（8.3B）的分数只有 5B 模型的一半以下，论文未解释，更可能是配置或协议适配问题；小时级与天级 rollout 只有关键帧条、无量化指标，长程唯一的定量证据是 60 秒 LongForcing 曲线且无数值表；除 LongForcing 外的方法组件无消融，训练语料规模未披露，评测跑在哪个量化配置上也未交代

**路线内分支：reason-then-render**。[[2607-PhiZero]] 不在像素或 VAE latent 上直接做时序建模，而是先把视频压成自监督学到的离散"物理语言"（FSQ levels (8,5,5,5,5,5)、25K 词表，4 秒视频 → 256 个符号），由 Qwen3-VL-4B 在符号空间预测未来，再交给 Wan2.2-5B LoRA 扩散解码器渲染。动机是把"预测"与"渲染"解耦，让物理推理发生在低维离散空间。生成端指标支持这一设计：Physics-IQ Verified IQ-Score 41.2 > Cosmos3-Super 39.5 > Wan2.2-14B 32.2，PhyGround Physics 3.01，WorldModelBench Total 8.19。

但判别端没有同步跟上：IntPhys2 Overall 56.34、Hard split 仅 52.38（随机基线 50，V-JEPA 57.42），LikePhys 刚体 29.14 最好而流体 53.15 倒数第三，WS-IoU 27.6 落后。这直接落在路线 6（evaluator）与本表下方 planner 分支的要害上——那两种用法消费的正是判别能力，而不是画面质量。方法层的关键缺口是没有同数据同算力、仅移除中间表示的对照，21.2→41.2 的增益混淆了表示、数据与训练三个变量；离散表示本身是有损压缩（256 符号重建 PSNR 28.9，Wan2.2 VAE 用 44,800 token 达 37.7）；其 "zero-shot" 迁移仍需按源域微调 tokenizer，4 秒固定视界靠滑窗自回归外推，无代码发布。

**路线内分支：长时程失败先是寻址问题，再才是容量问题**。这条路线此前对 revisit 崩坏的处理都落在"存什么、存多少"上——[[2603-HybridMemory]] 压缩 memory latent，[[2607-Wonder]] 从全量历史 KV 中检索固定大小的 active set，[[2607-ABotWorld0]] 直接用 rolling eviction 把窗口外的历史丢掉。[[2608-WorldTrace]] 把根因挪到另一个轴：训练时 query 只见过有界的相对 offset，rollout 超出训练 horizon 后 query–key offset 落到训练分布外，快频 RoPE 分量的相位绕过 π 多圈、对 attention score 的贡献退化为噪声——内容还在 KV cache 里，attention 读不到它（附录对 MG2-1.3B 的逐频率量化：训练最大 offset 为 5 时 f≥10 的分量仍是语义载体，offset=30 时最快三个分量相位已超 3π）。与之耦合的第二个失败在内容侧：在已旋转的 RoPE 空间对 key 做平均，不同时间戳的旋转角方向相反而部分抵消，无论内容是什么该频率的信号都被削弱。

两处修法都不改权重。summary slot 的 virtual position 只由 slot rank 决定，因此与绝对 horizon 无关、恒落在训练分布内且各 slot 互异（避开 Block-relative 封顶导致的 slot 坍缩）；key 在未旋转的 canonical 空间压缩、读取时单次旋转到该 virtual position。固定压缩方式只换 position 的对照隔离出位置轴的独立贡献：TempSSIM 超 Block-relative +5.9%/+2.8%、超 Centroid-linear +9.5%/+13.8%。两个写入器分工明确——连续时间组平均的 Field 管 coherence（N=48 TempSSIM 0.545 对 sliding window 0.472，Scene Drift 同时最低），冻结 scene-entry 帧 canonical key 的 Landmark 管 episodic recall（ABA loop 上 PAC 0.864 对 0.723；N=256 时 verbatim landmark 保持 0.989，而只做 canonical 压缩的一档跌到 0.610）。开销上 Field 的峰值显存与 sliding window 完全一致，Landmark 恒定多占约 0.6 GB。

其中一个负结果的迁移价值大于主结果：把这套 position 方案单独接到 MemRoPE 的写入器上反而更差（p<0.001），因为写入与读取的 offset 分布不再一致。位置与内容写入必须在同一 offset 分布下共同设计，单独替换任一侧可能有害。边界：主结果在单一 1.3B game world model 上，14B 的 LingBot-World 只有附录级验证且 Field 在其上几乎无增益（Plücker 相机条件已提供 recall 信号），Landmark 在 2× 训练 horizon 无显著增益；LoopBench 由同一团队提出并主要用于验证自家方法，其 PAC 依赖 CLIP 相似度，对"几何一致但外观漂移"的敏感度未测；同一 ABA 配置在不同表里的绝对 PAC 差异很大（N=16 的 sliding window 分别为 0.723 / 0.540 / 0.837），论文未解释口径差异，跨表数字不可混用。Field 对 recall 几乎不帮忙、Landmark 靠 cosine-spike 阈值与 FIFO 逐出，"该记住哪些地方"仍无答案。

**实际效果与优点**：视觉保真度天花板高（GameNGen 人类辨真伪仅 58–60%）；天然吸收 internet video prior；和成熟 video diffusion 工程栈复用。

**缺点与未解 gap**：
- **Action-following 不可靠**：[[2602-WorldVLALoop|World-VLA-Loop]] 展示 Cosmos-Predict 2 在错 action 下仍 hallucinate 成功——policy 在此类 WM 上做 RL 会 reward-hack。[[2608-WorldSimProbe]] 把这条从个案变成六模型三平台上的系统读数：cross-task replay 中 fidelity 随 receiver–donor 运动失配增大而下降（平均 Spearman ρ=−0.433，RoboTwin），且即便轨迹仍是 task-directed，只要执行风格换成 early-checkpoint policy 或人类遥操作者，六个模型全部比 late-policy 低 10.8–16.1 分；action-injection 与 unified action–video 两类架构都横跨高低名次，架构本身不解释 faithfulness（详见路线 10）
- **控制被执行但世界不回应**（与上一条相互独立的失效面）：[[2608-WorldExam]] 把"指令写明的后果"与"须自行推断的后果"分开评后出现方向反转——action 接口在 Subject Control 上领先（55.47 对 language 最好的 37.28），Terrain / Object Interaction 却只有 27.49 / 33.75 对 64.39 / 75.96。动作被照做了，地形、被接触物体与附近 agent 却纹丝不动（详见路线 10）
- **长时序 drift**：GameNGen 3 秒 context、DIAMOND memory bottleneck、World-VLA-Loop 主动放弃 LIBERO-Long——>200 帧后视觉/几何普遍漂移；Wonder 用固定 active set 检索 full-fidelity historical KV 把 active attention cost 与 history length 解耦，但 total KV storage 仍增长、revisit 无定量 metric，尚不能算解决。其中静态场景 revisit 这一部分现在有了机制解释与 training-free 的对策（[[2608-WorldTrace]]：offset 越界导致的不可寻址，恢复后 O(1) 预算下 ABA loop PAC 0.864 对 0.723），但动态主体的出画-再入画（[[2603-HybridMemory]] 测的那类）与"该记住哪些地方"的写入策略都不在其覆盖内
- **物理对齐不随 scale 解决**（Cosmos Tab. 20）：需 data curation 或 hybrid physics inductive bias
- **推理成本高**：典型 14B DiT naive 5.7 s/chunk，即使 38× 工程栈加速后仍需 2×GB200 才能 7 Hz 闭环。消费级硬件的可行区间由 [[2607-ABotWorld0]] 标出：5B + 三段蒸馏 + 全栈量化在单张 RTX 5090 上 12.4–15.8 FPS，但 WorldRoamBench 七项无一第一，速度换质量的那条曲线本身没有被测（评测跑在哪个量化配置上未交代）

### 2. Latent-space / JEPA-style WM（implicit representation）

**核心思路**：不重建像素，只在 representation 空间做 mask-denoising / next-state prediction，让 predictor 学 "latent dynamics"，下游用 CEM / MPC 做 planning。

**代表工作**：
- [[2506-VJEPA2|V-JEPA 2]]（FAIR, 2025-06）：1M+ 小时视频 mask-denoising 预训练 → 冻结 + 62 小时 unlabeled Droid 视频训 action-conditioned predictor → CEM 在 latent 上 receding-horizon planning。Franka pick-and-place zero-shot 65–80% vs Octo 0–15%；**V-JEPA 2-AC 16 s/action vs Cosmos 4 min/action 且 success rate 反超**
- [[2501-RoboticWorldModel|RWM]]（ETH, NeurIPS 2025 Workshop Outstanding Paper）：GRU + 多步 autoregressive 训练学 legged robot dynamics；**architecture 不是关键，autoregressive training 才是**。在 ANYmal D / Unitree G1 上 zero-shot 硬件部署，reward 打平 250M-step model-free PPO 但只用 6M transitions
- [[2606-Orca]]（BAAI）：Next-State-Prediction 统一 world latent——unconscious（相邻帧 dense transition）+ conscious（event-conditioned）双路监督，冻结 backbone 后由 language/image/action decoder 读出。**frozen-readout probe 是"latent 是否真承载 state transition"的可反驳检验**；4B 在 OOD readout 超同量级专用 baseline，但 real-robot binary success 仅 6%
- [[2603-Memoir]]（TPAMI 2026）：contrastive RSSM world model 的 imagination 只作 **retrieval query** 而非 planning——预测不准时只是检索差一点，不会执行错误动作。IR2R +5.4 SPL + 8.3× 训练加速；但 imagination-based 检索相对朴素 state-based 仅 +0.61 SPL，主要收益来自选择性检索框架本身
- [[2607-QQWorld]]（西安交大）：把 latent WM 的分布正则从 Epps–Pulley 特征函数检验换成 quantile–quantile 匹配。可迁移的判据藏在两条 proposition 的对比里——EP 的恢复力 $\sqrt{\pi}\,h\,e^{-h^2/4}$ 在 $h=\sqrt{2}$ 达峰后超指数衰减，偏离越远梯度越小，正好放过最该被拉回的离群点；QQ 的梯度 $2(x_n - q_\rho(n))$ 对偏差线性。**一个善于"度量"分布差异的统计量未必是好的"训练目标"，其梯度场必须处处有信息**。planning 平均 79.75→85.08（4 环境 × 6 seed），tail rate 0.315→0.123，EP 统计量 119.909→82.294。边界：只在单一 LeWM backbone 上验证，Reacher +2.66 与 OGBench +3.00 落在标准差内，相对 DINO-WM 仅 +0.33pp，三条 proposition 原文未给证明，无代码

**优点**：计算高效（V-JEPA 2 对 Cosmos 的 15× 推理优势）；数据效率极高；与 MPC/CEM 天然兼容。

**缺点**：像素生成能力弱；Goal specification 受限；Cross-embodiment 验证薄；Latent 不可解释。

### 3. 3D / 4D Generative WM（空间侧）

**核心思路**：把 WM 绑到显式 3D 表示（occupancy grid、3DGS、point cloud）上，在 4D 体素/pointcloud 空间做未来生成或直接回归。这条路线内部已分成两支：一支做场景合成（生成一个可漫游的动态 3D 世界，无动作接口），一支做 action-conditioned 3D dynamics（在给定机器人动作下预测全场景几何如何变化）。

**代表工作**：
- [[2405-OccSora|OccSora]]：nuScenes 上 DiT + 4D VQVAE 生成 16 s 驾驶 occupancy video，但小物体（VRU）重建崩塌
- [[2604-HYWorld2|HY-World 2.0]]（Tencent Hunyuan）：四阶段 pipeline panorama → WorldNav → WorldStereo → WorldMirror → 3DGS，端到端 712 s 生成可交互 navigable 3D 场景。**核心 insight 是 keyframe-latent VDM**
- [[2604-GenWorldRenderer|Generative World Renderer]]：ReShade + RenderDoc 从 AAA 游戏截取 G-buffer，fine-tune Cosmos-DiffusionRenderer
- [[2604-SpatialEvo]] (🔥 Rating 3)：3D 空间推理的答案可以从点云和 camera pose 确定性计算（DGE），不需要 model voting；w/o Physical Grounding → VSI-Bench 从 46.1 暴跌到 18.8
- [[2607-RynnWorld4D]]（DAMO）：**投影式 4D = 同步预测 RGB+Depth+Flow**，三分支 DiT + Joint Cross-Modal Attention，靠相机模型隐式承载几何、绕开显式 3D 表示；蒸馏 inverse-dynamics policy 在 6 个真机任务赢 5。但 RGB imaging quality 反而低于纯 2D Wan-2.1——几何优势来自显式监督 depth 分支而非表征范式胜利，且全链路建立在伪标注（Depth Anything 3 / DPFlow）上
- [[2606-PointWorld]]（Stanford / NVIDIA, CVPR 2026）：把 state 与 action 统一进同一个 3D 模态——state 是 RGB-D 反投影出的 full-scene point cloud，action 是机器人自身几何按 URDF 正向运动学推演出的 dense 3D point flow（只采样 gripper 表面约 300–500 点），world modeling 于是变成"在 robot point 扰动下预测全场景逐点位移"。这个表示选择一次处理三件事：action conditioning 不必往视频里塞 token、动作表示不绑定具体 joint 空间因而跨 embodiment、接触即使发生在遮挡区域也能表达（想象出的 robot flow 完整可见）。PTv3 backbone + 冻结 DINOv3 特征，chunk H=10、每步 0.1 s、单次前向约 0.12 s，可直接驱动 MPPI 做 MPC。DROID 测试集 ℓ2 mover 误差 PTv3-1B 0.0312 对 GBND 0.0390，参数量差 957 倍而内存与延迟只温和增长；模型 50M→1B 与数据 5%→100% 两轴在 log 空间都近似线性下降。真机 Franka 零样本（无 demo、无 post-training、单张 in-the-wild RGB-D）成功率 Drawer 90% / Scarf 80% / Tissue Box 70% / Duster 60% / Broom 60% / Pillow 40% / Microwave 30% / Book 20%。约 2M 轨迹 / 500 小时训练数据里，真实部分靠一条无标注管线（立体深度 → 相机外参优化 → point tracking 后 lift 到 3D）从 DROID 恢复出 >60%（近 200 小时）可靠 3D point flow。边界：主指标是一秒 horizon 的逐点 ℓ2，作者自承绝对误差的小差异可能对应显著不同的 rollout 保真度，ℓ2 与任务成功率的映射未量化，模型层的 scaling 结论不可直接读作下游成功率同步 scaling；真机每类任务试验少、方差极大，task point 与目标位置仍由人或 VLM 指定；sim↔real 零样本明显退化（D→B 0.1460），需 finetune（1/20 迭代即超 from-scratch specialist）；依赖精确 URDF/FK 与 RGB-D 深度质量
- [[2608-LatentTo4D]]（ReLER, ZJU）：把 4D 生成的接口从 RGB 像素上移到 shared VAE latent——取 video DiT 的最终去噪 latent 而不解码成 RGB，经固定 trilinear resampling + 学到的 3D conv 对齐到由 4RC 初始化的 4D decoder token grid，再由 frame-wise 与 global spatiotemporal attention 交替精炼，直接输出 per-frame camera 与世界系几何。只训 alignment module、rank-16 LoRA 与 prediction heads（final stage 用 1,143 个 clip），单一 checkpoint 免调服务共享同一 frozen Wan VAE 的三个 DiT。相对固定同一 latent 的 Wan+4RC 级联，Text4D-200 DINO-F1 +2.88–3.45、I4D-200 +5.81，四维度 human preference 59.2–72.1% 且八个 95% bootstrap 区间下界全部 >50%。作者自陈的边界很硬：证据只在单一 VAE family 内，projection-based 指标不建立生成场景的 metric accuracy；模型无动作接口，仍是场景生成器

**优点**：显式 3D 可验证几何；直接对接 CG 渲染 / 物理引擎；[[2606-PointWorld]] 表明该表示在模型与数据两轴上都有可预测的回报，且预测本身可以跑到实时。

**缺点**：场景合成一支的 temporal dynamics / action 缺失依旧（HY-World / OccSora 一代本质是 scene generator，[[2608-LatentTo4D]] 也无动作接口）；[[2607-RynnWorld4D]] 的投影式 4D + policy 蒸馏与 [[2606-PointWorld]] 的 point-flow 回归各自补上 dynamics 与 action，代价分别是依赖伪标注几何与依赖 RGB-D 加精确 URDF；数据稀缺；精度-压缩权衡。两支共有的验收缺口是几何/流误差与下游任务成功率之间的映射从未被量化。

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

**路线内分支：被预测的未来该是什么表示**。WAM 的默认答案一直是"未来 RGB 或其 VAE latent"，2026-07 出现两篇从不同方向撬动这个默认值的工作——一篇加语义通道，一篇加触觉通道——而它们的消融给出了同向的负信号。

- [[2607-STWAM]]（partial 核查）：在 VAE 未来之外并行预测冻结 DINOv3 的语义未来（Dual-Space Future Experts，三分支 MoT 联合 flow matching），并用 Qwen3-VL 抽取的当前视觉-语言语义作 query，从 4 帧 DINO history 检索 intent token 注入 action expert（CAIR）。结构化 cross-branch mask 让 action token 读不到任何 future 流，因此推理时两条 future 分支可整体切掉，代价只有 1.24× 延迟。LIBERO 98.7 / RoboTwin 2.0 92.77 都在饱和区，真正的落点是零样本 LIBERO-Plus 72.8 对 Fast-WAM 51.5、真机视觉偏移 61.5 对 25.8。**两个负结果比主结果更有信息量**：只用 DINO 未来在 LIBERO-Plus 掉到 39.7，低于纯 VAE 的 51.5——语义表示丢掉了动作需要的细粒度动力学，两者互补而非可换；无锚点的 DINO history 检索只有 56.5，低于完全不用 intent 条件的 66.4。边界：论文用来定义问题的机制断言（"pixel-generative 未来监督把 action-relevant transition 与 task-irrelevant 视觉内容纠缠"）在笔记 Evidence Ledger 中状态为 `unsupported`——原文措辞 hedged 且无任何 entanglement 度量，本 survey 只引用其消融数字与负结果，不引用该机制；LIBERO-Plus 的 baseline 数字引自第三方研究，LIBERO / RoboTwin 表未交代 baseline 来源，全文无参数量，唯一能确认同示教同流程的干净对照是真机那组；评测的偏移全部是外观级（背景/光照/视角/传感器噪声），而 DINOv3 恰好是对该类扰动不变的表示
- [[2607-N0TWAM]]（NeoteAI / Fudan TEAI）：把 touch 放进*被预测的未来*而不是当输入或外挂——video / tactile / action 三个 expert 只共享一层 self-attention，frame-id causal mask 组成 predict-then-act cascade；触觉走双通路，latent 空间里以残差形式**预测**未来触觉，force 空间里由 NeoForce encoder 经零初始化 cross-attention **观测**当前触觉。UniVTAC 84.5 对 InternVLA-A1 67.1、NeoSim 49.4 对 π0.5 45.8、真机 46.3 对 30.0。**消融削弱了它自己的新颖性叙事**：预训练规模是 UniVTAC 上最大的单一因素（84.5→65.4），大于任一触觉通路；两个 benchmark 上去掉反应式的 observed 通路（即既有 tactile policy 的做法）都比去掉前瞻式的 predicted 通路（本文的新颖处）掉得更多——70.5 vs 71.8、29.6 vs 41.1。边界：全文没有"去掉 future-vision 预测"的消融，也没有"两条触觉通路同时关闭"的联合对照，因此 predict-then-act 相对直接回归动作的增量在本文内部无 matched 对照；tactile punctuation 的 staging 机制本身无消融；real-time 主张无任何 ms / Hz / FLOPs 数字；三套件中只有 UniVTAC 是第三方公开 benchmark，NeoData / NeoSim / NeoReal / NeoForce 全部出自同一份公司网页报告，规模数字的一手出处不可独立核查；真机每任务仅 20 trials，论文自述二项标准误最高约 ±11%，且逐任务存在方向反转（NeoSim Cup Handover 全模型 14 而 w/o predicted 65）

这条分支目前的共同信号是：两篇都在扩展"未来"的表示，两篇的消融却都显示**新增的那条预测通路不是主要收益来源**——ST-WAM 的语义未来必须与 VAE 未来并存才有用、单独使用反而更差，N0-TWAM 的预测触觉输给反应式的观测触觉。这不推翻 "world models are implicit policies"，但它给"预测更多模态/更多表示的未来 → 更好的动作"这条推论加了边界条件。库内暂无独立复现，两条均为单篇证据。

**路线内分支：训练期消费、部署期丢弃（world model 作纯训练信号）**。ST-WAM 靠 attention mask 在推理时切掉两条 future 分支还只是这一形态的单点；四篇独立工作把它推成 WAM 的一种默认工程选择——训练时联合建模未来，部署时把整个 world-model 分支删除、只留一个自含 policy：

- [[2608-SimWAM]]（驾驶域）：Wan2.2-5B video expert 与轻量 action DiT 经共享 attention 接口做 joint flow matching，isolated mask 让未来帧 token 与 action token 互不可见，训练后丢弃 video 分支；NAVSIM navtest 91.5 PDMS，超 imagine-then-act 的 DriveWAM（90.1）/ DriveLaW（89.1）。它的 mask ablation 是这条分支最直接的机制证据：让 action 显式 attend 未来帧不涨点（isolated 90.3 ≈ bidirectional 90.2 ≈ action→video 90.1），即 video 先验的收益完全经由共享观测表征传递，推理时的"想象"是可省的开销。边界：0.2 的差距量级在噪声内，结论的准确读法是"可丢弃性零代价"而非 isolated 更优；RL 直接优化 PDM reward 且评测同为 PDMS，+1.2 的 RL 增益无独立指标交叉验证；全部主结果限单前视 + NAVSIM 闭式评测。
- [[2608-JEPAWAM]]：在 frozen V-JEPA 2.1 表示空间做 latent WAM——把当前帧与未来帧沿时间维 stack 联合编码为 joint current–future target（借 tubelet=2 保持 24×24 patch 对应），shared predictor（Qwen2.5-0.5B）同时做 transition prediction 与 flow-matching action 生成，部署时移除 target branch 与 prediction head。0.5B、无 robot-policy pretraining 在 LIBERO-Plus 达 79.2%（其对比中无 pretraining 组最好），同一监督作辅助 loss 嫁接 π0.5 后 84.5→86.3。其 Table 4 的 Full-hidden 对照（把预测的未来表示直接喂 action expert，掉 6.1 个点到 73.1）与 π0.5 transfer 的隔离设计（action token 被 mask、不能 attend future tokens，增益只能来自 backbone 参数被塑形）共同给出与 SimWAM 同构的结论。边界：增益集中在 Camera 扰动列，Language 扰动 68.2 显著低于 ResVLA/RoVLA；RoboTwin 强 domain randomization 下辅助监督几乎失效（37.2→37.5）；code 未发布、affiliation 为匿名化残留、基线为同期工作可比性未核对。
- [[2608-WorldTokens]]：把耦合拓扑本身做成贡献——VLM 特征经 Perceiver 式 World Adapter 压成 256 个 world tokens，同时作 future-video denoiser 的条件与 action expert 的**唯一** visual-language context（排他路由），部署时移除整个 video 分支、只余约 10 ms adapter 开销（61.85 ms/chunk，π0.5 的 1.1× 内）。其 VLM bypass ablation（94.1 vs full 97.0）回答了"为什么加辅助 video loss 常常不 work"：action expert 能绕开被监督的表示时，video 目标与 action 目标竞争而非塑形；Canny 首帧反捷径的负结果同样有信息量——RGB anchor 让 denoiser 走外观捷径，91.5 低于完全不做 world modeling 的 95.0，辅助任务设计不当是净伤害。边界："best reported on SIMPLER" 仅相对其表内 baseline；LIBERO 上并非最优（Cosmos Policy 98.5 / DiT4DiT 98.6 更高）；无代码、K=256 与 λ_w=5 无 sweep。
- [[2608-MobileWAM]]（详见上方 Chain-of-Foresight 相关讨论）：CoF 串行未来链与 video 分支同样只在训练期存在，经四个 backbone tap 层的梯度把动力学压进当前观测表示，推理时 backbone 退化为可缓存的 current-frame encoder（938 ms 对 Motus 4950 / LingBot-VA 8126 ms）。其 Table 3 补上并行对串行的直接对照（并行未来监督 +2.1，MLP 串行 −3.9，transformer 串行 +8.0）——辅助头与主干的接口形状（哪些层、多宽的瓶颈）比监督量级更决定成败。

四篇与 ST-WAM 合起来，这条分支的共同结论可以写得比"部署省钱"更强：**world-model 监督的正确耦合方式是经共享表示塑形 policy，而把预测的未来作为 policy 的输入要么无益（SimWAM mask ablation）、要么有害（JEPA-WAM Full-hidden −6.1）、要么依赖排他约束才不打架（WorldTokens bypass）**。三组消融来自三个互不相识的团队、三种不同的架构接口，是本 survey 目前跨论文一致性最强的机制性 pattern 之一。它同时把路线 1 的推理成本缺点（14B DiT 秒级）在这一子族内直接消解——代价是放弃推理期的 rollout / 想象能力，因此与 WM-as-Planner（推理期消费）构成光谱的两端。未决问题：该结论目前全部来自 manipulation / 驾驶的短横幅任务，在真正需要 multi-step lookahead 的长程任务上"丢弃想象"是否仍然无损，无人测过；四篇均无独立复现。

两条限定需要与这个结论一起传播。其一，"训练期辅助监督、推理期整支剥离"这个拓扑在非 world-model 的监督目标上同样成立：[[2608-StellaVLA]] 的自回归 spatial-language expert 以 λ=0.3 辅助 loss 参与训练、推理时完全剥离，只留 backbone 与 MLP action head 走单次前向（推理时联合解码语言要 3177 ms，剥离后 88 ms）。因此这条分支眼下支持的是"辅助监督经共享表示塑形 policy"这个更宽的结论，world model 是其中一种监督来源而非必要成分；不同监督来源之间的 matched 对照无人做过。其二，跨论文的 LIBERO-Plus 排名替代不了同 backbone 消融：StellaVLA 不含任何世界建模，零样本 85.1%，而它的最大增益也落在 camera viewpoint（+23.5），正是 JEPA-WAM 增益集中的那一列。两者 backbone、数据与训练规模均不同，这不构成反例，但说明该列可由互不相干的路径攻下——把 WAM 在该列的领先归因于世界预测监督，依据只能是上述三篇的同 backbone 消融，不能是榜单位次。

**优点**：参数共享 / 部署简化；video prior 显式注入 action learning 的最自然方式。

**缺点**：算力门槛极高（Motus 18 000 GPU-hours、DreamZero 需 2×GB200）；边际收益不一定大（Motus Joint mode 比 VLA mode 只 +3pp）；高精度任务不 hold；action 与 imagination 的同步性可被攻击解耦（[[2607-BadWAM]]）——"部署前检查 imagined future 是否合理"的安全叙事失效；新增预测通道的边际收益存疑（[[2607-STWAM]] / [[2607-N0TWAM]] 的消融均显示新增的预测通路不是主要收益来源）。

### 5. WM-as-RL-Simulator / WM-Conditioned VLA (Loop 路线)

**核心思路**：用 video WM 替代物理仿真器跑 GRPO / PPO，或把 WM 预测的 future latent + value 作为 VLA policy 的 inference-time condition；policy 与 WM 迭代 co-evolve。

**代表工作**：
- [[2602-WorldVLALoop|World-VLA-Loop]]（Show Lab NUS, 2026-02）：**SANS dataset + DiT reward head + co-evolving loop**。核心诊断：video WM 的 action-following 偏差让它对错 action 也生成成功 → policy reward-hack。LIBERO 三 suite +12.7% SR；real-world 13.3% → 36.7% → 50.0% 两轮迭代
- [[2602-GigaBrain05M|GigaBrain-0.5M*]]（GigaAI, 2026-02）：**RAMP** 把 RECAP 从 advantage-only 条件化推广为 (future latent, advantage) 联合条件化；WM 联合预测 future state + value 比 only-value 精度更好
- [[2501-RoboticWorldModel|RWM + MBPO-PPO]]：legged 场景证明 "long-horizon PPO + learned model" 可行
- [[2606-RehearseVLA]]（CVPR 2026）：video WM 替代仿真器对 OpenVLA-OFT 做 RL post-training（LIBERO 5-demo 设定 79.6% vs SFT 74.85%），**VLM instant reflector 输出连续 reward**——解决 binary reward 下 RLOO advantage 塌缩，并提供实时终止信号；无 oracle 终止评测暴露 post-success 冗余动作破坏任务状态的隐性问题（OpenVLA-OFT -11.8pp）。局限：WM 训练数据仍靠 SFT policy 在仿真器内探索采集（"摆脱仿真器"存在循环依赖），且 WM 冻结、未处理 reward hacking——与 World-VLA-Loop 的 co-evolution 形成对照；"失败/次优数据是 WM 训练关键"与 SANS 结论互证

**优点**：把 WM 从"能生成什么视频"转向"能否闭环训 policy"的 actionable metric；co-evolving loop 给出 reward hacking 的实证 narrative。

**缺点**：仿真器质量瓶颈（video WM action-following 普遍弱，[[2608-WorldSimProbe]] 进一步给出它的形状——faithfulness 随控制偏离训练分布单调退化，而 RL 探索恰恰要把 policy 推到 task 分布之外；"训练数据里含失败轨迹"不等于覆盖了 task 分布外的可行动作）；Long-horizon 死穴（AR video drift >200 帧；RehearseVLA LIBERO-Long 仅 +0.8）；评估样本量小。

**推理期分支：WM-as-Planner**。上述用法都在训练期消费 world model（当仿真器、当 condition source），[[2607-WorldActionPlanner|WAP]] 把它整个挪到推理期：VLM agent 提出子目标，action-conditioned WM 在想象中评估，policy 降级为被调用的执行工具，构成 propose → optimize → search 闭环。让这一反转在视频骨干上可行的是 **pose-image conditioning**——候选动作先经正向运动学渲染成骨架图像、再由 VAE 编码送进 Wan-T2V-1.3B（4 视角 2×2 拼图，21 帧 @7FPS 历史 → 20 帧 @20FPS 未来），从而绕开低维动作向量与视频生成骨干之间的接口失配（与 [[2607-GigaWorld1]] 关于 channel-concat pose map 优于 cross-attention 的结论同向）。结果：compositional LIBERO-Long 四设定 72/68/78/70，对照 π0.5 的 4/0/0/0 与 cosmos-policy 全 0；新布局六设定 88/86/90/66/84/78，baseline 多为 0；zero-shot Robosuite 80/76 对纯 VLM planner 的 58/22。消融阶梯从 56/28/46/32 起，依次加入 global optimization、local search、policy rollout imagination 逐级抬升；1 次想象即胜过带 ground-truth reward 的 BoN-8（60 vs 42）——在这一设定下想象比重采样更省。

边界同样清楚：WAP 使用 URDF、相机标定与硬编码 GRASP/RELEASE 原语，"72 vs 0" 因此是"带特权信息的模块化系统 vs 端到端 policy"，不是 world model 单独的贡献，全文只有 Table 9 隔离了 world model 自身增益。世界建模指标（+11.4% ID / +16.8% 泛化）是 PSNR 与 LPIPS 的相对提升再取平均，其 limitation (g) 已自承该构造可疑。全部实验在仿真中完成、无真机，无 imagination horizon 扫描与误差累积测量，50 次 trial 无误差棒。

**critic 侧分支：WM-as-Critic**。上述用法都把 world model 放在 actor 一侧（当仿真器、当条件源、当规划器），[[2607-WCM]]（同济 / 上海创智学院 / 复旦）把它挪到 critic 一侧：critic 在预测 return 的同时预测下一帧的 LeJEPA latent，损失为 $\mathcal{L}_{\text{value}} + \lambda \mathcal{L}_{\text{pred}}$，可 drop-in 替换 PPO / Flow-SDE / AWR / RECAP 四种 VLA RL 算法的原 critic，覆盖 149 个仿真任务与 7 个 WidowX-250S 真机任务。**决定性的对照是 λ=0 的 history-ViT 变体**——同样吃多帧历史、同样多的时序建模容量，但不带世界预测目标，结果依然无效；这把"增益来自世界预测"与"增益来自多看几帧"分开了，是这条分支目前最硬的证据。另一个值得记的读数是 λ 扫描下 OOD 成绩波动 10.6pp 而 IND 只波动 2.7pp——预测权重主要影响的是分布外行为。

边界：全文没有任何 value-accuracy 指标，因此"预测目标 → 值估计更准 → 策略更好"这条因果链只有两端被测、中间未测；LIBERO-Plus 上 one-shot SFT + 约 250 步 RL 超过 20k 轨迹 Full-SFT 的结论只领先 0.8–2.3，且部分子维度回退；OFT 的 OOD 增益仅 +0.8；LeJEPA / SIGReg 为借用组件，且 SIGReg 在 on-policy 下关闭，仿真结果实际只有 $\mathcal{L}_{\text{pred}}$ 生效；baseline 无误差棒，也无训练开销对照。

### 6. WM-as-Policy-Evaluator（Robotic Policy Evaluation）

**核心思路**：用 learned world model 作为 robot policy 的低成本 evaluation surrogate；成功标准是 **evaluator–world agreement**（同一 policy 在 real 与 WM rollout 中的 outcome 一致性），而非生成质量。

**代表工作**：
- [[2607-GigaWorld1]] (🔥 Rating 5, GigaAI)：**WMBench**——2,989 条 paired real/WM rollout + 324K challenge rollout 的 controlled study。结论：evaluator 质量取决于 long-horizon action fidelity、可迁移 physical prior、空间对齐的 action control（channel-concat Trajectory Accuracy 0.3528 vs ControlNet 0.2566 vs cross-attention 0.1620），而非短期视频观感；综合 evaluator score 超最强通用 Wan baseline 14.9%；VLM-assisted WMES 与人类评分 exact agreement 87.80%
- [[2604-dWorldEval]] (Rating 2)：discrete diffusion WM + **progress token**（progress=1 判 success）+ 统一 token space + sparse keyframe memory

**关键 gap**：video model 对 contact-sensitive failure 有 **optimistic bias**（GigaWorld-1 closed-loop 观察）——这是 policy evaluator 最危险的误差类型，optimistic evaluator 会系统性放行危险 checkpoint；false-success rate 应作为第一汇报指标。另两条评测线独立定位到同一处，但方向并不一致。[[2608-WorldSimProbe]] 与 optimistic bias 同向且更尖锐：作者据一次 50 例审计（观察到的 grounding failure 全部是幻觉出接触、无一是漏掉接触）把 probe 限定为 simulator 验证过的 no-contact 场景，六模型三平台上三种触发的均分是 distractor 75.0 > 空间邻近 54.5 > 外观诱导的假接触 38.6——最挡不住的正是"有接触的视觉线索但没有控制支持"。[[2608-WorldExam]] 却给出相反符号的失败：Object Interaction 的典型问题是"被接触物体保持不变"或"主体直接穿过去"，最好的 action-driven 只有 33.75。两种符号不互相反驳（前者构造无接触场景考模型会不会无中生有，后者要求发生接触考模型会不会漏掉），但合起来说明 contact 目前在两个方向上都不可靠，还没有被归结成单一机制；库内尚无对它的独立解释或复现。

### 7. Digital-Domain World Model（Web/GUI）

**核心思路**：数字环境的 world model 收敛于**文本语义状态空间**（NL state delta / accessibility tree / 语义后果描述）而非像素——planning、安全判定、RL 训练依赖的是功能性状态变化而非视觉保真。理论依据是 [[2511-DreamGym]] Theorem 1：合成环境上训练的策略在真实环境的改进下界只由 reward 保真度 ε_R + 转移域一致性 ε_P 决定，与 raw-state 重建误差无关。

按用途分类：

| 用途 | 代表工作 | 关键证据 |
|---|---|---|
| Planning / lookahead | [[2411-WebDreamer]]（TMLR 2025）、[[2600-MobiledreamerGenerativeSketchWorld]]、[[2510-RWoM]] | live 网站动作不可逆 → 用 LLM 想象替代真实 tree search。R-WoM 先诊断 LLM 的 next-state/milestone 尚可、full-procedure planning 无检索很弱，再把 tutorial 注入 world-model rollout 而非 policy context；OSWorld/WebArena 子集相对 WebDreamer 最多 +23.4%/+16.3%，但增益只撑到 horizon≈3、主结果限 tutorial-covered 子集 |
| Pre-execution guard | [[2607-SeerGuard]]、[[2602-WAC]]、[[2608-DreamGuard]] | SeerGuard 重标注发现 **91% high-risk 任务是"良性指令 + 危险执行"**→ 安全评估必须下沉到 action 级；8B SFT 语义 next-state 预测超 235B 基座（Next-State-QA 0.762 vs 0.651）。WAC 通用任务纠错仅 +1.8pp / +1.3pp——guard 用途中安全判定比任务纠错收益大。DreamGuard 把 guard 的 world model 从 LLM 换成 frozen-LLM-embedding 上的 GRU-RSSM，25 ms/call 级延迟 |
| RL simulator | [[2511-DreamGym]]（Meta）、[[2608-EnvACE]] | LLM 经验模型（CoT 推理生成转移 + reward）+ reward-entropy 课程：WebArena GRPO 7.3→13.3 零真实交互，S2R 用 <10% 真实数据反超 from-scratch；第一手证词——WebArena 真实 RL 只能 4 并发 + 手动 reset。EnvACE 走到光谱另一端：不建外部 simulator，同一 policy 换 role tag 自己彩排环境响应 |
| Trajectory synthesis | [[2510-UISimulator]]、[[2507-WebSynthesis]]、[[2608-AppDeltaWorld]] | UI-Simulator：同等真实测试环境暴露下合成经验达 OS-Genesis 的 4×（WebArena），\$0.02–0.05/轨迹；WebSynthesis：WM-guided MCTS 合成轨迹，**rollback-only 训练无效（1.49%）——rollback 信号必须与成功轨迹配合**；AppDeltaWorld：transition-grounded 检索 + delta code + diffusion 混合渲染，闭环 rollout 产出 33,133 条 mobile GUI 轨迹 |
| Image-based simulation | [[2500-UisimInteractiveImageBased]] | 两阶段 UI simulator（layout prediction → layout-to-image），layout-first 符合 UI 结构化本质 |
| Online executable model / memory | [[2607-ObjectCentricEnv]] | object knowledge（Python 类）+ procedure knowledge（必须 import object model）+ episode 后全 procedure re-execution gate；三 text-interaction benchmark 平均排名 1.75，但 verification 只保证 executable consistency，不保证语义正确，且未覆盖 GUI/开放 schema |

**与 robotics WM 的分野**：digital WM 的瓶颈不在算力而在**转移幻觉与 reward 无外部审计**——DreamGym 的经验模型既当转移函数又当 reward 函数、无独立 verifier；UI-Simulator 的 LLM transition 有状态幻觉。robotics 侧的 action-following 问题在这里表现为"对不存在的页面状态过度自信"。

[[2608-AppDeltaWorld]] 是 GUI 侧对转移幻觉给出显式结构解的第一个实例（partial 核查，下列均为 source-verified 行）：app 级 action-transition index（click 落点量化到 6×12 网格）约束"当前屏加这个 action 能到达哪些页面"，检索不到受支持的 target cluster 即判 invalid——把"拒绝非法 action"从生成模型的隐式知识变成可查表结构。但它同时是"保真度排名与下游收益排名不同构"的双口径实例：CMGUIBench-500 总分 73.51 居首，功能逻辑分 S_ad/S_id（79.69/77.00）却低于图像基线 GPT-Image-2（91.73/83.40），下游 MobileGym 14.1% 落后三个同量级开源模型。两条机制性结果对整条 trajectory-synthesis 路线更有解释力：逐 action-type 拆解显示合成经验的增益在动作类型选择与停止时机（wait 14.19→72.97、click 仅 91.82→95.88）而非坐标 grounding——低保真渲染对决策层经验仍有效；consensus-reward 负结果（8 rollout 聚类，23.5% 的 group 无唯一赢家）暴露这类 world model 缺少**状态等价判定**，test-time verifier 用法目前不成立。另外 ADW-only 训练相对基座反而掉点、必须混真实数据——合成经验的多样性天花板由 world model 训练分布决定，恰好绕不开"敏感 app 缺真实轨迹"的原始动机区域。

[[2608-EnvACE]] 把 RL-simulator 用途推到"内化"的极端：同一个 policy 交替扮演 Act 与 Rehearse 两个角色，Rehearse 按 prompt 里的 whitelist / JSON schema 校验并生成 tool 执行结果，训练轨迹完全由 policy 自展开，role-wise GRPO 联合优化。归因对照做得干净但结论对卖点不利：从 standard GRPO 到 EnvACE 的 τ²-Bench +5.5 里，"存在自生成 rollout 通道"值 4.3（Per-role Policy 臂，即 DreamGym 族的外挂形态），真正的"内化"（参数共享）只值 1.2。推理期的 rehearse-before-commit（N 次私下彩排 → 一次真实提交）用 base-model 彩排对照排除了"多花算力就涨"的解释（sequential 下反而低于不彩排），但缺 budget-matched 的"真实环境试错 + 复位"对照臂——它是环境不提供 rollback 时被迫的替代方案，不是对该问题的回答。全文没有任何彩排保真度测量（$\hat o$ 与真实响应从未逐条对账），且 grounding 实际来自 prompt 注入的静态调用/返回对 + 外部 LLM judge 的 reward 通道："训练期零环境交互"只对 transition 通道成立。

[[2608-DreamGuard]] 把 guard 用途的成本结构换了个量级：DreamerV3 式 GRU-RSSM 建在 frozen Qwen3-4B 第 31 层 embedding 上，risk head 读的是**执行前预测出的 successor latent state** 而非当前态，split-conformal 标定轨迹级误报率，平均 0.025 s/call（比 SafePred 快 424×）。"打分预测后状态优于打分当前状态"有直接消融支撑（w/o successor prediction：F1 82.9→76.3、FPR 9.8→25.4），恰好补上 SeerGuard 缺的那个对照。代价同样清楚：模型只在 SafetyDrift 上训练与标定，跨 benchmark 后提前干预率 PHIR 从 96.3% 崩到 16.8–34.8%、AgentDojo FPR 29.4%——"多视野风险"主要成立于同分布内；且它推理期不产出任何可读的后状态，判决是纯 {PASS, HOLD, BLOCK} 标签，agent 被拦后拿不到修正依据。与 SeerGuard（每步 8B VLM、输出 rationale）合看，guard 一族当前的权衡曲面是延迟、证据可读性、跨分布鲁棒性三者不可兼得。三篇的共同缺口与本节开头的分野判断一致：EnvACE 无彩排保真度、AppDeltaWorld 无状态等价判定、DreamGuard 的"世界"是被风险标签塑形的潜向量——**digital WM 的 fidelity 维度仍然没有一家直接测量**。

### 8. Planning Efficiency (相关方向)

**代表工作**：[[2604-AgenticCache]] (Rating 2)

**核心思路**：利用 plan locality，cache-based plan reuse 替代 per-step LLM calls。+22% success rate，-65% latency，-50% token usage。

### 9. Conceptual Framework (Survey)

**代表工作**：
- [[2604-AgenticWorldModel]]：Levels × Laws taxonomy（🔥 Rating 5，最系统的 Survey）
- [[2411-WorldModelSurvey|Ding et al. 2024/CSUR]]：implicit/predictive 二分 + cloud-side / edge-side 切分
- [[2607-PixelsToStates]]（Alaya Lab）：用 game engine 的 **action–state–observation loop** 重构 interactive WM 版图——真正缺口在显式 state、规则驱动 transition、持久后果与 **consequence latency**（结果应在规则定义的时刻出现而非输入后立即显现），不在画面生成；附 Black Myth: Wukong 90+ 小时 frame-aligned engine-state 数据引擎，为 explicit-state WM 提供稀缺监督
- [[2607-MentalWorldModeling]]（MWM / Mentis）：Levels × Laws 中 **Social 约束域**在本 survey 的第一篇正面工作——把 belief / goal / intention / emotion / norm 从"事后 rationale"升格为 world state 的一等成分，状态空间因子化为 $S = S_{\text{phy}} \times S_{\text{men}}$，观测定义为从第三人称联合状态渲染出的 target 第一人称部分观测（允许与真实心理状态不符，这正是 false belief 得以被表达的形式化理由），动作写成 (physical carrier, mental content) 的耦合对，物理转移不直接条件于 mental content。实例化为 training-free 的六阶段 pipeline Mentis + 448 条 process-annotated 的 Menti-Bench（2,688 个 gold 后继状态）。最值得借用的是它的审计模板：necessity ladder（S0 options-only floor 31.3 → S1 direct 63.3 → S2 CoT 74.6 → S3 SC@6 77.9 → S4 free-text state 80.3 → S5 structured state 82.6 → S6 full MWM 87.9，human 98.5，每级只增加一个建模承诺）+ channel intervention + oracle cascade，其中 oracle 增益的 sub-additivity（四个单增益之和 8.7 > 四者组合 6.3）干净地量化了模块化 pipeline 的跨阶段误差税。边界：全文只报 final-action F1，6.2 节与 Appendix G 定义的 mental fidelity / perspective-leakage rate / process-outcome divergence 一个数值都没报，因此"涨点是因为心理状态被正确建模"没有中间证据；消融是纯信息移除、无等量非心理内容的对照，且移除 physical 通道（−16.5）比移除 mental 通道（−12.1）代价更大，与标题重心相反；S6 的调用量约为 S1 的二十几倍而全文无 token 成本表；Menti-Bench 的 gold 按 MWM 自身 taxonomy 标注、gold 动作由同一批作者裁定为"唯一可辩护最优"，S6 天然享有 schema 对齐红利；单步转移、封闭 6 选项动作空间
- [[2606-EnvEngineeringSurvey]]：以 environment lifecycle 而非单个 model 组织领域——八属性二分 × 八 domain → symbolic/neural synthesis → correctness/diversity/complexity/fidelity evaluation → agent/environment co-evolution。它补充 Levels × Laws 的“能力/约束”视角：world model 只是 neural environment synthesis 的 pixel/word/latent 三层之一；survey 自身也承认 correctness 之外三项质量维度 under-researched，co-evolution 仍是未来方向而非已完成机制
- [[Papers/2608-WorldProxy]]（position paper，partial 核查）：把 world modeling 从"预测物理状态转移"放宽为 Agent-Centric World Proxy——interaction step 取代物理时间步、information transition 取代 state transition，六类 proxy function（Dynamics / Spatial / Execution / Memory / Skill / Reward-Verification）× 三级介入深度（Proxy-L1 推理期提示 / Proxy-L2 训练期信号 / Proxy-L3 共演化）张成 6×3 设计空间，两个自认空格（Spatial×L3、Reward×L3）可当选题指针。按其笔记核查须带三条限定引用：全文零实验、零检索协议，分类是先验断言而非从证据聚出的结构；其头号主张"world model 应按让 agent 变好多少验收而非生成保真度"在 [[2604-AgenticWorldModel]]（共享两名作者）已作为 decision-centric evaluation 具名提出、本文未就此致谢；且存在一处 contradicted 的引用错误——把 I-JEPA / V-JEPA 2 举为 raw-pixel 预测的例子，而两者恰是 latent 预测的代表作，后续引用不得从它转录这一归类。它的真实用处是暴露本 survey 的一个覆盖习惯：我们默认把 world model 等同于像素/几何/语义转移预测，而 Memory / Skill / Reward 形态的"环境代理"（[[2603-Memoir]] 的 imagination-as-retrieval-query、[[2607-SeerGuard]] 的二值风险判定）被归到别处——这一观察成立的依据是库内已有笔记，而非其分类学本身。三套顶层切法（Ding 的 understanding/predicting、Chu 的 Levels × Laws、本文的 proxy functions × 介入深度）在 20 个月内相继出现且互不兼容、都未降级为可测量对象——taxonomy-heavy, evidence-light 是该方向 engineering-heavy, insight-light 之外的第二个症候
- [[2608-CombodiedAgents]]（position paper，22 作者 16 机构）：把建模对象从环境换成人。其 Personal World Model 的功能契约写作"在不同干预下这个特定的人的 state–event 轨迹如何展开"，输出的是校准过的未来轨迹分布——与 action-conditioned prediction 是同一个接口，只是环境位置上坐的是用户。形式化里有三处对本 survey 有迁移价值的选择：human-state transition 显式含用户自身动作与外生项（承认 agent 的干预不决定状态演化，这与机器人 WM 默认 action 完全决定 transition 恰成对照）、效用保持为向量不 scalarize、consent/safety/reversibility 写成 admissible set 硬约束而非 reward penalty，干预在该集合上做 Pareto 选择。落在 Levels × Laws 里它属 Social 约束域，与 [[2607-MentalWorldModeling]] 分工不同：MWM 建的是他人心理状态的单步转移并给了 448 条标注与消融，本文建的是长时程个体轨迹但零实验、零数据、零代码，CombodiedBench 是 8 模块蓝图，agency preservation 类指标（如 calibrated reliance）无可操作化定义。Table 1 的 12 类对比同样是作者自建的先验分类学且含 strawman 成分——这是上一条指出的第二个症候在 Social 域的又一例

### 10. 诊断式评测：把总分拆成可定位的失效环节

这条路线的共同主张是总分不可诊断：一个 aggregate score 说不出模型是没跟住动作、还是跟住了但交互不对。分歧在按什么轴拆。[[2608-WorldExam]] 按后果的来源拆——指令写明的 vs 须从场景自行推断的；[[2608-WorldSimProbe]] 按因果链的环节拆——动作是否被实现，以及环境响应是否由已实现的运动支持。两者的评测对象也不重叠（前者含闭源视频生成 API，后者全是可本地训练的 ACWM），得到的读数因此互补而非冗余。

#### 10a. 按后果来源拆：explicit fulfillment 与 inherent reactivity

**核心问题**：现有 world-model benchmark 绝大多数评的是 explicit instruction fulfillment——预先指定 layout、相机轨迹、动作序列或交互后果，再检查它是否被实现。这漏掉了一整类能力：从初始状态可以推出、但指令里完全没有描述的后果。主体走上台阶时高度应随地形变化并保持接触，靠近障碍物时应出现接触、绕行或阻挡，进入另一个 agent 的社交距离时对方应有反应——这些都不是输入的直接描绘，而是场景条件下的推论。[[2608-WorldExam]] 把它命名为 inherent reactivity，并把"评什么"从单一总分改成四个分别报告的诊断层级——Visual Quality、Control Adherence、Spatial Consistency、World Reactivity，共 8 个任务、1,474 个 case。放回 Levels × Laws 的坐标里，前两层大致仍在考 L1 Predictor，后两层才踏进 L2 Simulator；这让 [[2604-AgenticWorldModel]] 的层级框架第一次有了对应的可测量刻度，从而能回答"现有模型卡在 L1→L2 的哪一步"。

两处设计决定了它的结论能否被引用。其一是 **interface adaptation**：把可控行为写成 atomic control unit 的有序组合，再适配成 SE(3) 相机轨迹、离散动作序列或自然语言，把 camera-、action-、language-driven 三类模型放到同一批 case 上；代价是语言 prompt 只保留控制顺序、不含各段时长，其恢复轨迹须先用 change-point detection 切段再逐段比对，而另两类按预分配帧区间比对。其二是**两条 track、不出全局总分**：static-scene track（Camera Control + Scene Revisit）三类范式全跑，dynamic-interaction track（Subject Control + 五个 reactivity 任务）只跑 9 个能可靠控制第三人称主体的模型，Goal Completion 仅限 language-driven，明确拒绝把"接口不支持"记成"做得差"。camera-driven 因接口只控相机整体而全数排除在 dynamic track 之外，这与 [[2607-Wonder]] 划出的 camera-controllable renderer 与 action-conditioned simulator 之分是同一条界线，只是这次由评测口径给出。case 构造上，reaction 类任务只给一个触发用的控制、把由此诱发的场景反应整个留空，这个"留空诱因"的原则本身不限于视频生成。

**核心读数是一次方向反转**（下列数字的原文一致性已核查）：Control Adherence 上 action 接口领先，World Reactivity 上 language 接口大幅领先，且反转幅度远大于领先幅度。

| 任务 | action-driven 最好 | language-driven 最好 |
|:--|--:|--:|
| Subject Control | **55.47** | 37.28 |
| Terrain Interaction | 27.49 | **64.39** |
| Object Interaction | 33.75 | **75.96** |
| Social Interaction | 60.37 | **85.10** |
| Physical Reaction | 33.43 | **63.84** |
| Goal Completion | 接口不支持 | **85.33** |

论文对失败模式的描述是：把请求的主体运动变成相机运动或让场景静止；让被接触物体保持不变或让主体穿过去；让附近 agent 毫无反应。Terrain Interaction 这一列尤其硬——它先用 Subject Control 分数做 gate、未通过直接记 0，而 action-driven 的 Subject Control 明显更高，这个 gate 系统性地更宽容 action-driven，它们仍只有 27.49 对 64.39。"水平控制准"与"垂直地形适配"因此是两件事。

**视觉质量与其余三层解耦，且证据是多点位的**：dynamic track 上 language-driven 的 General 均值挤在 79.64–81.04 这个 1.4 分窄带里，Task 均值却从 39.85 铺到 65.02；ReCamMaster / FantasyWorld 的 General 是 80.97 / 80.23，Camera Control 只有 38.64 / 18.46；Kling 2.5 的 General 均值在 language-driven 中最高（81.04），Goal Completion 只有 48.25。三处证据分布在不同范式与不同层级上。可靠性一侧，VLM judge 与人的一致性为 Spearman 0.8614 / PLCC 0.8583（800 实例、5,793 个 checklist item、3 名标注者多数票），分任务最低是 Social Interaction 0.7019；把几何后端从 VGGT-Ω 换成 Depth Anything 3 后，static track Overall 平均绝对相对变化 3.09%（camera-driven 0.44% / action-driven 3.08% / language-driven 5.36%）、dynamic track 平均 0.57%，且 dynamic 各范式内排名全部保持。

**证据边界**（须随数字一起传播）。接口范式与模型档次共线是最主要的问题：dynamic track 上 action-driven 只有两个本地部署模型，language-driven 七个全部走 API，"action 接口 → 世界不反应"与"这两个特定模型 → 世界不反应"在这份数据里分不开，而论文自己承认闭源系统的 proprietary prompt enhancement 可能参与场景 grounding 与执行规划——这条限制未被列入 limitation。范式内方差大于范式间差距：language-driven 的 Kling 2.5 dynamic Task 均值 39.85 低于 action-driven 的 LingBot-World 39.91，范式内跨度达 25 分，"language-driven 更会反应"实际由 Veo 3.1 / Vidu Q3 / Hailuo 2.3 三个最强系统撑起。四个 checklist 任务的 ground truth 由未具名的 LLM case composer 起草、image-conditioned refiner 改写后定稿，人工介入只在候选初始图筛选；上述 human alignment 验证的是"judge 按给定 checklist 打分与人一致"，不是"checklist 抓对了该发生的反应"。judge 只看均匀采样的 10 帧，而 Social Interaction 与 Physical Reaction 要判的恰恰是时序性质，10 这个数无敏感性分析。六个动态任务的初始场景全为合成图、未说明生成模型与候选数，与 static track 的真实数据集输入分布不同源；每个 case 只跑一次生成，无重复采样方差。引用"20 个模型"时须注明那是 static-scene track 的规模，reactivity 层实际只有 9 个。数据与评测工具包写的是"will publicly release"，目前只有项目主页。

#### 10b. 按因果链环节拆：Observable Simulator Contract

**核心问题**：ACWM 要当 simulator，定义性要求不是生成一个 plausible 的未来，而是生成 supplied action 在当前场景下物理诱导的那个特定未来。[[2608-WorldSimProbe]] 把这句话写成两个可观测的连锁条件：action-realization consistency（生成的 agent motion 对应输入动作，r̂ ≈ Φ_R）与 interaction-response consistency（环境响应由已实现的 motion 与初始环境状态物理支持，ê ≈ Φ_E）。Φ_R、Φ_E 本身不可观测，做法是构造受控 intervention 去测它们的可观测后果，因此失败可以被定位到具体环节而不是记进一个总分。与之配套的是一个 coverage 论证：物理 simulator 覆盖全部可执行轨迹分布 A_phys，而 ACWM 通常只在窄得多的 A_task 上训练与评测，A_task 里含失败轨迹并不构成对 task 分布外可行动作的覆盖——这条论证直接决定了下面几个结论的适用范围。

五个 probe suite（前三测 action realization，后两测 interaction）、18,608 个实例、6 个开源 ACWM（IRASim / Ctrl-World / BWM / DreamDojo 四个 action-injection 架构 + LingBot-VA / Cosmos-3-Nano 两个 unified action–video 架构）、三个平台（RoboTwin / ManiSkill / LIBERO）。协议上最关键的是每个实例先在 simulator 里完整执行并通过 validity 过滤、manifest 在模型推理前冻结，六模型共享同一初始观测、动作流、simulator seed、reference horizon 与三个 diffusion seed——反事实因此有可执行的 ground truth，这是纯视频 benchmark 拿不到的。

读数分三层。**排名层**：跨平台 mean pairwise Spearman ρ=0.695，LingBot-VA 领先 RoboTwin（51.6）与 ManiSkill（63.5），Ctrl-World 领先 LIBERO（55.5）、其余平台第二；两类架构都横跨高低名次，架构不解释 simulator faithfulness。suite 级排名与 Overall 排名也不一致，单个环节强不代表整体 fidelity。**退化形状层**：T2 的 cross-task receiver–donor replay 中，六模型 fidelity 随 receiver 与 donor 的 motion mismatch 增大而整体下降（平均 Spearman ρ=−0.433，RoboTwin），与"偏离熟悉轨迹时模型愈发依赖 scene/task 关联的 motion prior"一致；T3 里全部六模型在 π0.5 late checkpoint 轨迹上比 early checkpoint 高 10.8–16.1 分（RoboTwin），说明即便动作仍是 task-directed，只要执行风格不熟悉 realization 就退化。T1 的 StackCube case 给出量级：simulator 的 action-failure 边界在 0.05，LingBot-VA 要到 0.374（7.48×）、Cosmos-3-Nano 要到 1.78（35.6×）才表现出失败。**交互层**：T4 三种触发的跨模型均分为 distractor 75.0 > spatial proximity 54.5 > appearance-induced false contact 38.6；T5 的 8 个 interaction primitive 上，primitive 间差异大于模型间差异——tap 40.8–56.9、shake 0.0–1.2，六模型均分区间只有 17.7–21.8，是跨模型共享的 primitive-specific 缺陷而非某个架构的问题。

**两条方法层结论对本 survey 之外的评测同样适用**。其一，下游可用性只在 OOD 控制下才能区分模型：用各 ACWM 生成的合成数据训 policy，standard 轨迹上成功率挤在 78–86%（六模型扩展后 78–89%）难以区分，OOD 轨迹上分离成 Ctrl-World 53% / BWM 34% / Cosmos-3-Nano 21% 且与 benchmark 排序一致——success-oriented 的训练评测会掩盖熟悉控制之外的 fidelity 差异。其二是 evaluator 有效性：750 条人工标注 rollout 上，Diverse/OOD controls 的 RMFA 与人类分级评分 ρ=0.750，明显高于 VLM 二元判断（一致率 0.450）与 IDM（ρ=0.284）；其中 **VLM judge 对 91.7% 的样本判 positive action following，人类只判 42.2%**。IDM 的问题被定位为 inverse-model decoding failure 而非 fidelity 信号——在正确的 simulator reference 上，IDM 误差对 OOD control source 即已升高 3.1×/5.6×。这两条对库内所有用 VLM judge 判 action-following、或只在 task 分布内报下游成功率的评测都是直接修正。

**证据边界**：全部在仿真内、单一外部视角，未触及真机 rollout、长 horizon 闭环与 deformable/多物体交互；测的是各模型在各平台官方 split 上按其 released recipe 单独 fine-tune 后的 fidelity，不能直接外推到通用 pretrain ACWM 的 zero-shot 表现；ρ=−0.433 与 late/early 10.8–16.1 两项只在 RoboTwin 上报告；downstream 只有一个 RoboTwin task，作者自称受控 case study；T5 的 primitive 标签判定仍由 VLM judge 给出（reference set 上与多数人工标签一致率 94–97%、生成样本上 93–95%），shake 这类极低分 primitive 的绝对数值受 judge 分辨力影响的程度未单独 ablate。

**路线间对比小结**：

| 路线 | 代表 | 主要 use case | 推理代价 | 主要 open gap |
|---|---|---|---|---|
| Pixel video diffusion | Cosmos / DreamGen / IRASim / Wonder / WorldTrace / ABot-World-0 | Data engine / Evaluator / camera exploration | 14B × 多步 → 秒级；ABot-World-0 5B 在单张 RTX 5090 上 12.4–15.8 FPS（口径完整） | Action-following / world reactivity / physics / AR drift；memory 已从容量问题改判为寻址问题并有 training-free 修法，但"该记住哪些位置"的写入策略仍未解 |
| Latent JEPA | V-JEPA 2 / RWM / Orca | Agent brain / MPC | 16s → ms 级 | Goal spec / cross-embodiment / 不生成像素 |
| 3D/4D generative | HY-World 2.0 / OccSora / RynnWorld-4D / Latent-to-4D / PointWorld | Scene generation / driving sim；PointWorld 分支做 action-conditioned dynamics 与 MPC | 分钟级/场景；PointWorld 单步预测实时 | 场景合成分支无 action 接口、dynamics 依赖伪标注几何；共有缺口是几何/flow 误差到下游任务成功的映射从未被量化 |
| Unified VLA+WM | UWM / Motus / DreamZero / FlowWAM / ABot-M0.5 / ST-WAM / N0-TWAM / SimWAM / JEPA-WAM / World Tokens / MobileWAM | VLA policy backbone；训练信号子族部署时删除 WM 分支 | 百 ms 级（工程后）；训练信号子族与纯 VLA 同量级 | 算力门槛 / unify 必要性 / action–imagination 同步性 / 新增预测通道归因不清 / 丢弃想象在长程任务上是否无损未测 |
| WM-as-RL-simulator | World-VLA-Loop / GigaBrain-0.5M / RehearseVLA | VLA RL post-train | 30 h / 任务级 | Action-following / 样本量 |
| WM-as-critic | WCM | VLA RL 的 critic 辅助预测目标 | 与原 critic 同量级 | 无 value-accuracy 指标 / 增益幅度小且部分子维度回退 |
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
| LIBERO-Plus | 10,030 例 / 七维扰动 | 零样本 Success Rate | π0.5+JEPA 86.3（其表内 best overall）；无 robot-policy pretraining 组 JEPA-WAM 79.2；此前 ST-WAM 72.8（Fast-WAM 51.5）；非 WM 对照 StellaVLA 85.1 | LIBERO 的扰动版，已成为 WAM 视觉鲁棒性主力评测；ST-WAM 与 JEPA-WAM 的 baseline 数字均引自第三方/同期工作而非重跑；JEPA-WAM 的领先集中在 Camera 列、Language 列落后 ResVLA/RoVLA 达 20+ 分；StellaVLA 不含任何世界建模却也把最大增益落在 camera viewpoint（+23.5），说明这一列可被无关路径攻下，跨论文名次不能替代同 backbone 消融（[[2607-STWAM]]、[[2608-JEPAWAM]]、[[2608-StellaVLA]]） |
| UniVTAC | 8 个触觉操作任务 | Success Rate | N0-TWAM 84.5（InternVLA-A1 67.1） | 唯一第三方公开的触觉 manipulation 套件；纯视觉 WAM 在此反而落后 VLA（FastWAM 48.0 / LingBot-VA 31.4），该异常低水位未被解释（[[2607-N0TWAM]]） |
| Menti-Bench | 448 条（320 text / 100 image / 28 video），2,688 个 gold 后继状态 | final-action F1 | full MWM 87.9（human 98.5） | 心理-社会状态的 process-annotated 世界建模评测；只报 outcome 级指标，且 gold 与被测 pipeline schema 同源（[[2607-MentalWorldModeling]]） |
| WorldExam | 1,474 case / 8 任务 / 4 诊断层级；static track 20 模型、dynamic track 仅 9 模型 | 四层分报（几何重建 + GPT-5.5 checklist），不出全局总分 | 各范式最好：Subject Control 55.47（action）；Object Interaction 75.96 / Goal Completion 85.33（language） | 唯一把"指令写明的后果"与"须自行推断的后果"分开报告的 WM 评测；引用"20 个模型"须注明 reactivity 层实际只有 9 个；数据与 toolkit 尚未发布（[[2608-WorldExam]]） |
| WorldSimProbe | 18,608 实例 / 5 个 probe suite / 6 个开源 ACWM；RoboTwin 5,498 + ManiSkill 6,610 + LIBERO 6,500 | 按契约两环节分报（RMFA / oracle-relative calibration / TAPNext++ 位移判据 / VLM primitive judge），不出跨环节总分 | LingBot-VA RoboTwin 51.6、ManiSkill 63.5；Ctrl-World LIBERO 55.5 | 每个实例先在 simulator 内执行并冻结 manifest，反事实有可执行 ground truth；全部在仿真内、单一外部视角、模型均为 in-domain fine-tune（[[2608-WorldSimProbe]]） |
| LoopBench | 4 个难度轴 12 配置，每条件 100 初始场景 | PAC（自参考：对照模型自己 first-visit 生成的帧，不需外部 GT 视频） | WorldTrace-Landmark ABA N=16 PAC 0.864 vs sliding window 0.723 | 专测 ABA 回访一致性；同一 ABA 配置在不同表格的绝对 PAC 差异大（0.723 / 0.540 / 0.837），跨表数字不可混用；由提出方法的同一团队构建、尚无第三方结果（[[2608-WorldTrace]]） |
| WorldRoamBench | 七个子维度（Strict/Partial Acc.、Traj.、Mechanics、Aesthetic、Imaging、Memory） | 各维度分报 | HappyOyster 领先五项；Genie 3 领 Imaging 与 Mechanics | ABot-World-0（5B）七项全为第二或第三，Memory 0.5041 对 Genie 3 0.6073 / HappyOyster 0.6309；benchmark 作者与被测方的 Benchmark Team 高度重叠，且 LingBot-World（14B）/ HY-World 1.5（8.3B）仅 0.11–0.32 的异常低分未获解释（[[2607-ABotWorld0]]） |
| PointWorld 3D dynamics 数据集 | 约 2M 轨迹 / 500 小时，DROID 真实 + BEHAVIOR-1K 仿真，覆盖 single-arm Franka 与 bimanual humanoid | 1 秒 horizon 的逐点 ℓ2 mover 误差 | B1K held-out 达 sub-centimeter mover 误差 | 3D 标注由无标注三阶段管线自动生成（FoundationStereo → VGGT 外参对齐 → CoTracker3 lift），恢复 DROID 中 >60% 的可靠 3D point flow；ℓ2 到任务成功率的映射未量化；开源为截稿时的未来式承诺（[[2606-PointWorld]]） |
| Text4D-200 / I4D-200 | 各 200 case 的 locked benchmark | DINO-F1（投影式，appearance-dependent） | Text4D-200 57.01 vs matched Wan2.1-14B+4RC 53.56；I4D-200 61.60 vs 55.79 | 直接 latent→4D 对同 latent 级联的对照；作者明确 DINO-F1 不建立 metric 4D accuracy，且全部证据在单一 Wan VAE family 内（[[2608-LatentTo4D]]） |

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
12. **WM × VLA 的七种耦合方式全部被实证验证**——offline data engine → inference-time latent conditioning → joint model → RL simulator → evaluator → test-time planner（[[2607-WorldActionPlanner]]）→ RL critic 的辅助预测目标（[[2607-WCM]]）
13. **scale 不能 alone 解决 physics**——Cosmos 7B vs 14B 在 rigid-body benchmark 上 IoU 基本不变（0.59 vs 0.60）
14. **"video model as data engine" 是可 scale 的新 sub-paradigm**——DreamGen 从单一 pick-and-place teleop 数据解锁 22 个新动词 / 10 个新环境
15. **PID > RL 在 sparse reward 场景**——RWM 的 autoregressive training + imagination-PPO 可换 250M transitions 的 model-free 水平
16. **Evaluator 质量 ≠ 视觉保真**——[[2607-GigaWorld1]] 用 paired rollout 证明 evaluator–world agreement 取决于 long-horizon action fidelity + physical prior + 空间对齐 action control；channel-concat 条件化的 Trajectory Accuracy 是 cross-attention 的 2.2×
17. **WAM 的"可检查想象"安全叙事被击穿**——[[2607-BadWAM]] 证明 black-box 视觉扰动可让 action 与 imagined future 解耦（96.5%→43.1%）；runtime monitor 应检查"action 能否实现 predicted future"而非 future realism
18. **Digital WM 不需要像素保真**——[[2607-SeerGuard]]（8B 语义预测超 235B 基座）、[[2511-DreamGym]] Theorem 1（ε_R+ε_P 与重建误差无关）、[[2510-UISimulator]]（合成经验 4× OS-Genesis）从安全/理论/训练三个角度收敛到同一结论
19. **"降级使用"是 WM 落地的普遍模式**——预测精度不足时选容错性高的用途：[[2603-Memoir]] 用 imagination 作 retrieval query（错了只是检索差一点）、[[2411-WebDreamer]] 只做 H=1 lookahead、[[2607-SeerGuard]] 只做二分类风险判定；对 WM 精度要求越低的用途落地越早
20. **失败/次优数据是 WM-as-simulator 的关键 ingredient 获再次确认，但它买到的覆盖比想象的窄**——[[2606-RehearseVLA]] 探索数据是最大单因素（Goal 68.4→86.4），与 World-VLA-Loop 的 SANS 结论互证；[[2608-WorldSimProbe]] 补上限定：物理 simulator 覆盖的是全部可执行轨迹分布 A_phys，ACWM 训练与评测都在窄得多的 A_task 上，A_task 里含失败轨迹并不构成对 task 分布外可行动作的覆盖。两条不矛盾——探索数据在任务内有效，跨任务的动作变异仍是空的
21. **Memory 必须分开讨论 storage、active compute、可寻址性与 semantic faithfulness**——[[2607-Wonder]] 固定 active KV set 只解决 attention cost，不限制 full historical KV storage；[[2603-HybridMemory]] 测动态主体 exit–reentry、Wonder 只给静态 revisit qualitative case，两者尚不能互相替代。[[2608-WorldTrace]] 加进第四个轴并把它排到前面：即使内容还在 cache 里，rollout 超出训练 horizon 后 temporal RoPE 的 query–key offset 落到训练分布外，attention 读不到它——静态场景 revisit 的第一约束是寻址而非容量。[[2607-ABotWorld0]] 从反面提供同一处的证据：它把 KV cache 设成 bounded + rolling eviction 换取消费级 GPU 实时性，代价正是 Memory 成为其七个评测维度里相对最弱的一项（0.5041 对 Genie 3 的 0.6073）
22. **Digital WM 的 grounding 开始分化为 external prior 与 executable structure 两条路线**——[[2510-RWoM]] 用 tutorial 把 imagined rollout 延长到约 3 steps，[[2607-ObjectCentricEnv]] 用 object/procedure code + re-execution gate 维护一致性；共同边界是“有依据/能执行”仍不等于环境语义真实
23. **World model 不能脱离 environment lifecycle 单独评估**——[[2606-EnvEngineeringSurvey]] 将 model 放回 modeling→synthesis→evaluation→application 闭环，并指出除 correctness 外的 diversity/complexity/fidelity 仍 under-researched；这解释了为何视觉保真、action faithfulness 与 downstream policy success 长期互不等价
24. **生成保真不蕴含物理判别**——[[2607-PhiZero]] 在 Physics-IQ 拿下 41.2（生成端第一）的同一模型，IntPhys2 Hard 只有 52.38（随机基线 50），LikePhys 流体倒数第三。Takeaway 16（evaluator 质量 ≠ 视觉保真）由此从 evaluator 场景推广为 WM 的一般性质：凡消费判别能力的用途（planner / evaluator / safety guard）都不能用生成指标验收，而分材料、分难度的判别 split 是目前唯一能暴露这一差距的手段。[[2608-WorldExam]] 从第三个角度给出同向的独立证据：同一批模型的视觉质量层几乎不含区分度（language-driven General 挤在 79.64–81.04），任务层却铺开 25 分（39.85–65.02），另有 ReCamMaster / FantasyWorld 的 General 80.97 / 80.23 配 Camera Control 38.64 / 18.46、Kling 2.5 的 General 最高配 Goal Completion 48.25。三处证据切的层不同（生成 vs 判别、视觉质量 vs 任务能力、几何类 vs checklist 类），结论同一：视觉指标不构成对 WM 能力的验收
25. **WM 的用法从训练期扩展到推理期，且想象比重采样更省**——[[2607-WorldActionPlanner]] 把 policy 降级为工具、规划全程在想象中完成，1 次想象胜过带 ground-truth reward 的 BoN-8（60 vs 42）；但该系统带 URDF、相机标定与硬编码抓放原语，"72 vs π0.5 的 4" 是模块化+特权信息 vs 端到端的对比，仅 Table 9 隔离了 world model 自身贡献——归因清楚前不可引作 WM 的能力证据
26. **给 WAM 增加新的预测通道，收益未必来自"预测"那一半**——[[2607-STWAM]] 的语义未来必须与 VAE 未来并存（DINO-only future 39.7 < 纯 VAE 的 51.5），[[2607-N0TWAM]] 的预测触觉输给反应式的观测触觉（去 observed 掉到 70.5 / 29.6，去 predicted 只掉到 71.8 / 41.1），且预训练规模才是 UniVTAC 上最大的单一因素（84.5→65.4）。两条独立证据同向，但均为库内单篇、无独立复现，应作为 WAM 表示设计的边界条件而非定论
27. **检索式上下文的收益是有条件的，条件不满足时为负**——[[2607-STWAM]] 的三个对照（无锚点 DINO history 56.5 / 仅当前帧语义 62.3 / VAE history 64.7）全部低于完全不用 intent 条件的 66.4；收益要求 query 被当前状态锚定 **且** 被检索表示对无关扰动不变，缺一即掉点。这与 GUI / long-horizon agent 里"多喂历史反而掉点"是同一现象的不同实例
28. **正则项的好坏取决于梯度场而非统计功效**——[[2607-QQWorld]] 指出 Epps–Pulley 的恢复力在偏差超过 $\sqrt{2}$ 后超指数衰减，正好放过最该被拉回的离群点，而 quantile–quantile 匹配的梯度对偏差线性；换掉正则后 latent WM 的 planning 平均 79.75→85.08、tail rate 0.315→0.123。可迁移的判据是：一个善于**度量**分布差异的统计量未必是好的**训练目标**
29. **world prediction 也可以放在 critic 一侧**——[[2607-WCM]] 让 critic 联合预测 return 与下一帧 latent，drop-in 替换四种 VLA RL 算法的 critic；λ=0 的 history-ViT 对照（同样的时序容量、没有世界预测目标，依然无效）把增益与"多看几帧"分开。但全文无 value-accuracy 指标，中间机制未被直接测量，增益幅度也只有 0.8–2.3
30. **"世界"里缺的那一块是人在想什么**——[[2607-MentalWorldModeling]] 把心理变量升格为随动作演化的状态变量，填上 Levels × Laws 中长期空置的 Social 约束域；但它自己的消融显示移除 physical 通道代价更大（−16.5 vs −12.1），且只报 outcome 级指标——目前证据支撑的是"结构化 prompting 有效"，不是"心理状态被正确建模"
31. **控制被执行不等于世界会回应**——把"指令写明的后果"与"须自行推断的后果"分开报告后会出现方向反转：[[2608-WorldExam]] 中 action 接口在 Subject Control 领先（55.47 对 37.28），却在 Terrain / Object / Physical Reaction 上落后 37 / 42 / 30 分，反转幅度远大于领先幅度；Terrain 那一列的 gate 还系统性地偏袒 action-driven，差距依然成立。这在 action-following（错动作也生成成功）之外定位了一个独立失效面——动作被照做了，世界不动。边界是接口范式与模型档次共线：dynamic track 上 action-driven 仅 2 个本地模型对 language-driven 7 个 API 系统，"接口属性"与"模型档次"在现有数据里分不开
32. **contact 是三条独立评测线共同定位的失效点，但它们指的方向不一致**——先前把 [[2607-GigaWorld1]] 的 optimistic bias 与 [[2608-WorldExam]] 读成"同向收敛"是过早的。[[2608-WorldSimProbe]] 与 optimistic bias 同向且更硬：其 50 例审计中观察到的 grounding failure 全部是幻觉出接触、无一是漏掉接触，据此构造的 no-contact probe 上六模型最挡不住外观诱导的假接触（三触发均分 distractor 75.0 / proximity 54.5 / false contact 38.6）。WorldExam 的失败却是相反符号——"被接触物体不变"或"主体穿过去"，最好的 action-driven 只有 33.75。两者不互相反驳，因为构造相反（一个考会不会无中生有，一个考会不会漏掉），但合起来说明 contact 在两个方向上都不可靠，还没有被归结成单一机制。这处**争议**比任何单向结论更值得写进 mental model：引用"contact 是 WM 的弱点"时必须带上是哪个方向，否则会把两组不可合并的证据算成两票
33. **world-model 监督的正确耦合方式是塑形共享表示，不是给 policy 喂预测的未来**——三组来自不同团队、不同架构接口的消融同向：[[2608-SimWAM]] 让 action attend 未来帧不涨点（90.3 ≈ 90.2 ≈ 90.1），[[2608-JEPAWAM]] 把预测的未来表示直接喂 action expert 掉 6.1 个点，[[2608-WorldTokens]] 的非排他路由让 video 目标与 action 目标竞争（94.1 vs 97.0）。配合 Takeaway 26（新增预测通路不是主要收益来源），"训练期消费、部署期丢弃"子族（另含 [[2608-MobileWAM]] / [[2607-STWAM]]）由此获得机制解释而不只是工程巧合；边界是四篇全为 manipulation / 驾驶短横幅任务、无独立复现，长程任务上丢弃想象是否无损未测。另一条边界来自机制的**外延**：同样的"训练期辅助监督、推理期剥离"拓扑在非世界建模的监督上也成立——[[2608-StellaVLA]] 的 spatial-language expert 以 λ=0.3 与 action 目标并行训练、推理时整支剥离（联合语言解码 3177 ms 对纯动作缓存路径 88 ms），因此当前证据支持的其实是更宽的命题"辅助监督通过共享表示塑形 policy"，world modeling 只是其中一种监督源；库内还没有一篇在同一 backbone 上横向比较不同监督源
34. **digital WM 的 fidelity 维度至今没有一家直接测量**——[[2608-EnvACE]] 从未把彩排响应与真实执行结果逐条对账（其归因还显示"内化"只值 +1.2、自生成 rollout 通道值 +4.3），[[2608-AppDeltaWorld]] 的 consensus-reward 负结果暴露状态等价判定缺失（23.5% rollout group 无唯一赢家），[[2608-DreamGuard]] 的"世界"是被风险标签塑形的潜向量、跨分布后提前干预率 96.3→16.8。三篇用途各异（RL simulator / 数据引擎 / guard）而共享同一缺口，把 [[2606-EnvEngineeringSurvey]] 点名的 fidelity under-researched 从 survey 判断落成三个可测的具体实验（彩排对账、状态等价判据、第二个长程分布的 leave-one-out）
35. **长时程 visual persistence 先受限于寻址，其次才是容量**——[[2608-WorldTrace]] 把 KV cache 里"存了读不出"落成可量化的机制：MG2-1.3B 上训练期最大 offset 为 5，rollout 到 offset=30 时最快的三个 RoPE 频率分量相位已越过 3π，贡献退化为噪声；相应地，naive 在旋转空间做平均压缩会因 phase cancellation 破坏 summary，key 必须存在 canonical 空间、读取时再单次旋转到分配好的 in-distribution virtual position。固定压缩方式只改 position 的消融给出 TempSSIM 超 Block-relative +5.9%/+2.8%、超 Centroid-linear +9.5%/+13.8%。最有信息量的是那个负结果：把 WorldTrace 的 position 方案接到 MemRoPE 的写入器上反而更差（p<0.001）——position 分配与内容写入必须在同一 offset 分布下协同设计，不能当作两个可自由组合的模块。边界是主结果只在单个 1.3B 游戏 world model 上，LingBot-World 仅附录级验证且 Field 在其上几乎无增益，且 2× horizon 处无显著增益
36. **simulator faithfulness 随控制偏离训练分布单调退化，而架构不预测它**——[[2608-WorldSimProbe]] 在六个 ACWM 上给出两处一致读数：cross-task replay 的 fidelity 随 receiver–donor motion mismatch 增大而下降（平均 Spearman ρ=−0.433），且全部六模型在不熟悉执行风格（early-policy checkpoint 轨迹）上比熟悉风格低 10.8–16.1 分——即使动作仍然 task-directed。同时 action-injection 与 unified action–video 两类架构都横跨高低名次，跨平台排名一致性却有 ρ=0.695，说明可比的是模型个体而非架构族。这条对所有把 WM 当 RL simulator 或 policy evaluator 的用途都是直接约束：探索恰恰要把 policy 推到训练控制分布之外。边界是全部在仿真内、模型均为 in-domain fine-tune，两项机制性分析只在 RoboTwin 上报告
37. **VLM 二元 rollout judge 在 OOD 控制上系统性偏乐观**——[[2608-WorldSimProbe]] 的 750 条人工标注对照中，VLM judge 对 91.7% 的样本判 positive action following，人类只判 42.2%；同一批数据上 RMFA 与人类分级评分的 ρ=0.750，VLM 一致率仅 0.450，IDM ρ=0.284（且 IDM 的误差被定位为 inverse-model decoding failure——在正确的 simulator reference 上，其误差对 OOD control source 即已升高 3.1×/5.6×）。这直接影响库内一批依赖 VLM judge 的 action-following 与 rollout 质量评测的可读性。需要同时记住的限定是它并非"VLM judge 不可用"：WorldSimProbe 自己的 T5 primitive 判定仍用 VLM judge，只是先在 human-verified reference set 上验到 94–97% 一致率——差别在于判的是有明确 checklist 的 primitive 标签，而不是"这个 rollout 跟住动作了吗"这种二元整体判断
38. **显式 3D 表示在预测误差轴上给出了 log-linear scaling，但这条曲线还没有接到任务成功率上**——[[2606-PointWorld]] 把 state 与 action 统一为 3D point flow 后，模型（50M→1B）与数据（5%→100%）两轴在 log 空间都近似线性地降低 ℓ2 mover 误差，这是本 survey 中少见的可预测投资回报曲线。但主指标是 1 秒 horizon 的逐点 ℓ2 flow 误差，作者自己也指出绝对误差的小差异可能对应显著的 rollout 保真度差异；真机成功率同时方差极大（Drawer 90% 而 Book 20% / Microwave 30%），且需人工或 VLM 指定 task point 与 target。因此它不构成对 Takeaway 13（scale 不能 alone 解决 physics）的反例——两者测的根本不是同一个量，而"ℓ2 降到多少才换来任务成功"正是这条路线缺的验收环节

## Open Problems

1. **Action-following faithfulness**：video WM 对错 action 也生成成功，policy 一定能找到 WM 盾区做 reward hacking。SANS 式 near-success 数据 + reward head 是初步答案，但是否 scale 到 long-horizon / multi-agent / deformable 尚未验证；[[2606-RehearseVLA]] 冻结 WM 且不处理该风险，[[2607-GigaWorld1]] 观察到 contact-sensitive failure 的 optimistic bias——同一问题在 evaluator 侧同样存在。[[2608-WorldSimProbe]] 把这个问题拆成两半并各给一个可测形状：动作是否被实现（六模型 fidelity 随 receiver–donor motion mismatch 下降，ρ=−0.433；不熟悉执行风格低 10.8–16.1 分），以及响应是否被已实现的 motion 支持（no-contact 场景下的幻觉接触）。由此浮出的真正 open question 是覆盖：训练分布 A_task 之外的可行动作空间没有任何一篇工作在系统性地填，而 near-success / 探索数据只在任务内加密
2. **Physics alignment 不随 scale 解决**：Cosmos 7B vs 14B 在 rigid-body benchmark 上 IoU 基本不变；候选方向：(a) hybrid physics (Genesis/PhysGen)；(b) RL on intuitive physics MCQ (Cosmos-Reason1)——但第二条只涨 VLM-level reasoning，不 carry over 到 video generation；(c) 离散符号中间表示 + reason-then-render（[[2607-PhiZero]]），生成端 Physics-IQ 41.2 领先，但缺同数据同算力、仅移除中间表示的对照，21.2→41.2 混淆表示/数据/训练三变量，且判别端未同步（IntPhys2 Hard 52.38）。三条候选都还没有把"物理"从"看起来像物理"里分离出来
3. **Long-horizon drift**：所有 autoregressive video WM 超过训练 horizon 都退化——GameNGen 3 秒、DIAMOND frame-stacking、World-VLA-Loop 200 帧、OccSora 离开 32 帧 FID 飙 200+。Explicit compressed memory、retrieval-based context、LLM-style KV cache + streaming 都是候选，但没有任何一种在 robot-relevant setting 上 demonstrated；[[2607-AlayaWorld]] 的 error bank + 双记忆零定量评估，[[2607-Wonder]] 的 full-fidelity sparse KV 只固定 active attention 且长期一致性仍为 qualitative evidence。后续必须同时报告 quality/control/revisit metric、latency 与 total memory 随 horizon 的曲线。[[2608-WorldTrace]] 把静态场景 revisit 这一子问题从"容量不够"改判为"读不到"，并在 O(1) cache 预算下用 training-free 的位置重分配拿到 ABA PAC 0.864 对 0.723——但它明确把"该记住哪些位置"留空（Landmark 靠 cosine-spike 检出的 scene-entry 帧做启发式冻结），动态主体的 exit / re-entry 也不在其范围内。剩下的问题因此变成：写入策略能否学习，以及寻址修复在动态场景与更大模型上是否还成立
4. **Latent vs pixel 的路线之争**：V-JEPA 2 给出 15× 计算优势 + success rate 反超 Cosmos；DreamZero 反过来用 14B pixel WAM 达到 62.2%。[[2607-PhiZero]] 提出第三种位置——在离散符号空间推理、再渲染回像素，兼取 latent 的低维推理与 pixel 的可视化输出，但它同时是这条路线最直接的警示：判别能力没有随生成能力一起上来（IntPhys2 Hard 52.38 落后于纯 latent 的 V-JEPA 57.42）。**真正的 open question**：long-term 哪一条路径 scale 更好？或三者按用途分工（cloud-side pixel WM 做 data engine，符号中间层做 planner，edge-side latent WM 做 on-device MPC）？
5. **Cross-embodiment transfer 真能靠 video 做到吗？**：DreamZero 的 12 min 人类 egocentric / 20 min YAM robot video → unseen task +16pp 是至今最强信号；但 humanoid 五指手 vs bimanual gripper 级的 morphology gap 尚未被 video WM 路线 attack
6. **Benchmark metric 的 unresolved confound**：video fidelity (FID/FVD) ↔ physical faithfulness (VBench-2.0, PhysBench) ↔ policy success (DreamGen Bench / LIBERO SR) 三者相关但不等价。系统化的"哪个 metric 评 WM 公平" 的框架尚未建立。[[2607-PhiZero]] 把 confound 收窄成一个可操作的判据：生成式（Physics-IQ）与判别式（IntPhys2 Hard）在同一模型上给出相反排序，因此 WM 论文至少应同时报告两类指标，并按材料/难度分层——聚合分会掩盖流体等薄弱项（LikePhys 刚体第一、流体倒数第三）。[[2608-WorldExam]] 给出两条方法层的部分答案：把"指令写明的"与"须自行推断的"分层报告，以及用两条 track 拒绝把"接口不支持"平均进总分；但它自己也承认 Task / General / Overall 都是跨异质指标（几何法 0–100 分与 checklist 满足比例）的算术平均，单个聚合分跨范式引用意义有限。一个不需复现即可做的收窄动作是把公开表里每个模型的 General 均值对其 Task 均值作回归，直接量化视觉质量对能力的解释力——原文只给了范围，未给相关系数。[[2608-WorldSimProbe]] 从下游一侧给出另一条收窄：用各 ACWM 的合成数据训 policy，standard 轨迹上成功率挤在 78–86% 无法区分模型，只有在 OOD 轨迹上才分离成 53/34/21% 并与诊断排序一致——"用下游成功率验收 WM"的做法只在评测控制分布本身足够宽时才有分辨力。同一篇的 evaluator 对照（RMFA ρ=0.750 vs VLM 0.450 vs IDM 0.284）把"用什么打分"也变成了可比较的选项。显式 3D 路线上这个 confound 尚未被触及：[[2606-PointWorld]] 的主指标是 1 秒 horizon 的逐点 ℓ2 flow 误差，几何精度到任务成功率的映射作者自陈未量化
7. **WM × VLA 耦合方式的 trade-off space**：当前 7 种耦合方式都有代表工作（offline data engine / inference-time latent conditioning / joint model / RL simulator / evaluator / test-time planner / RL critic 辅助目标），但没有 head-to-head 比较。在同等 compute / data 预算下，哪种耦合方式对 sample efficiency 最敏感？新加入的 planner 分支还带一个专属问题：[[2607-WorldActionPlanner]] 显示 1 次想象胜过 BoN-8，但没有 imagination horizon 扫描，也没有测误差累积——想象的收益在多长 horizon 上翻转成 drift 的代价，目前无数据
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
19. **Digital WM 的转移幻觉与 reward 审计**：[[2511-DreamGym]] 的经验模型既当转移函数又当 reward 函数、无外部审计；[[2510-RWoM]] 的 tutorial grounding 只把 compounding error 推迟到 horizon≈3，[[2607-ObjectCentricEnv]] 的 re-execution 只保证 runnable consistency。"合成转移 + 真实 verifier"的混合方案是否优于两个纯路线未验证。[[2608-EnvACE]] 把缺口推到更尖锐的形态：连"转移函数"都收进 policy 权重后，保真度彻底不可审计（无任何 $\hat o$ 对真实响应的对账），且 reward 通道仍依赖外部 LLM judge——"训练期零环境交互"只对 transition 通道成立；[[2608-AppDeltaWorld]] 的 transition index 是结构侧的部分解（非法转移可查表拒绝），但其 consensus-reward 负结果说明状态等价判定仍缺
20. **Environment quality 的非 correctness 维度如何操作化**：[[2606-EnvEngineeringSurvey]] 明确指出 diversity、complexity、fidelity under-researched；需要把这些维度变成可重复测量，并与 agent learning progress、reward hacking 与 sim-to-real error 建立因果而非相关关系
21. **扩展"被预测的未来"，边际收益到底来自哪里**：[[2607-STWAM]] 与 [[2607-N0TWAM]] 各加了一条新的未来预测通道（语义 / 触觉），两篇的消融却都显示新增的**预测**通路不是主要收益来源；N0-TWAM 从未做"去掉 future-vision 预测"的消融，也无"两条触觉通路同时关闭"的联合对照，ST-WAM 则无参数量、主表 baseline 来源不明。需要的是在同一 backbone、同一数据与算力下逐条移除预测目标的 matched 对照，否则这条路线的收益无法与规模、额外参数与冻结 encoder 的先验分离。这类对照已开始出现零散样本——[[2608-SimWAM]] 的 mask 拓扑消融、[[2608-WorldTokens]] 的 bypass 与 anchor 消融、[[2608-JEPAWAM]] 的 target/readout 逐项对照各自隔离了一个耦合变量——但仍没有一篇在同一 backbone 上同时覆盖"预测什么、经什么接口耦合、给多少容量"三个轴
22. **表示的"不变性 × 可分性"在何种偏移下同时成立**：[[2607-STWAM]] 依赖 DINOv3 对外观扰动的不变性，而其评测的偏移恰好全是外观级；[[2607-N0TWAM]] 的 NeoForce 只在其预训练传感器（InTac S1）上验证，仿真因传感器不匹配直接放弃 force space。换成物理动力学、embodiment 或传感器型号级别的偏移时，什么表示能同时做到"对无关扰动不变"与"对任务状态可分"，两篇都把它列为 future work
23. **心理 / 社会状态的 world model 缺过程级验收**：[[2607-MentalWorldModeling]] 定义了 mental fidelity、perspective-leakage rate、process-outcome divergence 却一个数值都没报，benchmark 与被测 pipeline 共享 schema、gold 由同一批作者裁定为唯一可辩护最优（真正有多个可辩护答案的社会决策因此被系统性排除）。要让 Social 约束域从 position 变成技术路线，缺的是 learned transition、心理变量的不确定性表示，以及过程级保真度的独立测量
24. **接口属性与模型档次如何拆开**：[[2608-WorldExam]] 的核心结论"能力沿控制接口分裂且互补"建立在 dynamic track 的 9 个模型上，其中 action-driven 只有 2 个本地部署模型、language-driven 7 个全部走 API，论文亦承认闭源系统的 proprietary prompt enhancement 可能参与场景 grounding 与执行规划。判定这是接口的属性还是模型档次的属性，需要同一生成底座分别接动作接口与语言接口的 matched 对照，目前无人做。这也意味着"三种接口能力互补"的保质期可能很短——一旦强动作接口接到强生成底座上，整张表就会重画
25. **checklist 作为 ground truth 缺独立审计**：reactivity 类任务的判定链条是"LLM 起草 checklist → VLM judge 按 checklist 打分"，[[2608-WorldExam]] 的 human alignment（Spearman 0.8614 / PLCC 0.8583，800 实例 / 5,793 item）验证的只是链条后半段；checklist 本身是否抓对了该发生的物理与社会反应无人验证，人工介入只在候选初始图筛选。judge 只看均匀采样的 10 帧，而 timely adjustment、premature onset、freezing 这类判定恰恰依赖帧序，Social Interaction 的一致性也正好最低（0.7019），10 这个数无敏感性分析。与 [[2607-GigaWorld1]] 的 WMES（与人 Spearman 0.7574）合看，VLM judge 与人的一致性目前落在 0.75–0.86 这个带子里，可作为后续报告的参照带；但一致性带子解决不了"评分标准本身对不对"。另有一条未被任何一方测过的旁路：judge 把"无法核实"记为不满足时，画面质量可能从后门渗进 reactivity 分数（推测，两篇均无相关分析）。[[2608-WorldSimProbe]] 的对照给这条带子加了一个前提：它测到 VLM 对 91.7% 的 rollout 判 positive action following 而人类只判 42.2%，一致率 0.450。这与上面 0.75–0.86 的带子不冲突——差别在判定形式，checklist 分项打分与"整体跟住了吗"的二元判断不是同一个任务，而后者在 OOD 控制上系统性偏乐观。可操作的推论是：VLM judge 应限定在有明确 checklist 的分项判定上使用，且须报告判定的控制分布
26. **契约式诊断能否推广出仿真**：[[2608-WorldSimProbe]] 的可诊断性依赖 simulator——每个反事实都要能被真实执行以提供 reference，manifest 才能在推理前冻结。这一条件在真机上不成立，而其全部结论也都在仿真内、单一外部视角、模型均为 in-domain fine-tune。三个方向各缺答案：通用 pretrain ACWM 在同协议下的 zero-shot fidelity（作者未测）；真机 rollout 上如何构造无需完美 reference 的反事实；以及契约的两个条件在长 horizon 闭环、deformable 与多物体交互上是否还能分开测量

## 调研日志

- **2026-09-07 survey-refresh**：并入 7 篇（[[2608-WorldSimProbe]] / [[2608-WorldTrace]] / [[2606-PointWorld]] / [[2608-LatentTo4D]] / [[2607-ABotWorld0]] / [[2608-CombodiedAgents]] / [[2608-StellaVLA]]），skip 1 篇（[[2608-GalaxeaG05]]，AR-VLA 架构论文、无世界建模或未来预测组件）。结构性变化：路线 10 从单一小节改为两条并列的拆分轴（10a 按后果来源 / 10b 按因果链环节），后者写入 Observable Simulator Contract 与五个 probe suite 的三层读数；路线 1 新增「长时程失败先是寻址问题，再才是容量问题」分支（WorldTrace 的 RoPE offset 越界机制 + canonical key 压缩 + 两种写入器），代表工作补 ABot-World-0；路线 3 由纯扩散改写为「场景合成」与「action-conditioned 3D dynamics」两支，分别补 Latent-to-4D 与 PointWorld；路线 4 的「训练期消费、部署期丢弃」分支加两条限定（StellaVLA 作为出族拓扑实例 + LIBERO-Plus 跨论文名次不可替代同 backbone 消融）；路线 5 / 6 缺点与 gap 更新。最重要的一处是把 Takeaway 32 从"两条证据收敛"降级为**争议**：WorldSimProbe 的幻觉接触与 WorldExam 的漏掉接触方向相反，构造也相反，不可算作两票。Overview 趋势 +20/21/22；Key Takeaways 更新 20/21/32/33、新增 35–38；Open Problems 更新 1/3/6/25、新增 26；Benchmarks 表 +5 行（WorldSimProbe / LoopBench / WorldRoamBench / PointWorld 数据集 / Text4D-200-I4D-200）并更新 LIBERO-Plus 行；路线对比表 pixel 行与 3D/4D 行改写。未刷新配图（本 survey 无配图）。
  - **证据边界**：WorldSimProbe 全部在仿真内、单一外部视角、六模型均为 in-domain fine-tune，ρ=−0.433 与 late/early 10.8–16.1 只在 RoboTwin 上报告，downstream 仅一个 RoboTwin task（作者自称受控 case study），T5 的 primitive 判定仍由 VLM judge 给出（reference set 一致率 94–97%）。WorldTrace 主结果只在单个 1.3B 游戏 world model 上，LingBot-World 仅附录级且 Field 在其上几乎无增益、2× horizon 无显著增益；LoopBench 由同一团队提出、PAC 基于 CLIP 相似度，同一 ABA 配置跨表绝对值差异大（0.723 / 0.540 / 0.837）不可混用。ABot-World-0 为 partial 核查，只引 source-verified 行；其 WorldRoamBench 结果须按"作者与 Benchmark Team 高度重叠"读，LingBot-World / HY-World 1.5 的异常低分未获解释，评测所用量化配置未披露因此拿不到速度-质量曲线，机构归属在笔记中状态为 unsupported、正文未断言。PointWorld 的主指标是 1 秒 horizon 逐点 ℓ2 flow 误差而非任务成功率，真机成功率方差极大且需人工指定 task point，开源为截稿时的未来式承诺。Latent-to-4D 的 DINO-F1 是 appearance-dependent proxy、作者明确其不建立 metric 4D accuracy，全部证据在单一 Wan VAE family 内。CombodiedAgents 零实验零数据零代码，其 12 类分类学为作者自建先验、含 strawman 成分，只用于存在性与定位。StellaVLA 仅作 LIBERO-Plus 上的非世界建模对照与拓扑外延实例，不作为世界建模证据。以上均为库内单篇证据，无独立复现。

- **2026-08-11 survey-refresh**：并入 8 篇（[[2608-SimWAM]] / [[2608-JEPAWAM]] / [[2608-WorldTokens]] / [[2608-MobileWAM]] / [[2608-AppDeltaWorld]] / [[2608-EnvACE]] / [[2608-DreamGuard]] / [[Papers/2608-WorldProxy]]；前七篇 source-checked 或 partial 均按 ledger 限权引用，WorldProxy 为 position paper、partial 核查）。结构性变化：路线 4 新增「训练期消费、部署期丢弃」分支——SimWAM / JEPA-WAM / WorldTokens / MobileWAM 四篇与既有 ST-WAM 收敛成 WAM 子族，三组独立消融（mask 拓扑 / Full-hidden / bypass）给出耦合拓扑的机制解释；路线 7 补 AppDeltaWorld（transition-grounded 结构解 + 状态等价判定缺失）、EnvACE（内化极端形态 + 归因对卖点不利）、DreamGuard（RSSM guard 的延迟/可读性/跨分布权衡曲面）三段；路线 9 补 WorldProxy 并在 Overview 加 L1/L2/L3 术语注记（Chu 能力刻度 vs Proxy 介入深度）。Overview 趋势 +18/19；Key Takeaways +33/34；Open Problems 19/21 更新；Benchmarks 表 LIBERO-Plus 行更新；路线对比表 Unified VLA+WM 行扩展。未刷新配图（本 survey 无配图；新分支为路线内分支、分类框架未重构）。剩余 pending 2 篇（WorldSimProbe / WorldTrace）留下一轮。
  - **证据边界**：SimWAM 的 mask 消融差距 0.2 在噪声量级内，结论限"可丢弃性零代价"；其延迟对比无基线数字、RL 增益与评测指标同族。JEPA-WAM code 未发布、affiliation 匿名化残留、baseline 为同期工作可比性未核对，增益集中在 Camera 扰动列。WorldTokens 的 "best reported on SIMPLER" 仅相对表内 baseline，LIBERO 非最优，无代码无超参 sweep。MobileWAM 真机 trial 数未报告、评测在训练分布内、Table 3–6 参照配置身份不明。AppDeltaWorld（partial）只引 source-verified 行，机构不可解析。EnvACE 的 "训练期零环境交互" 只对 transition 通道成立（静态参考数据 + 外部 judge），TTS 为单次 run。DreamGuard 只在 SafetyDrift 训练标定，跨分布 PHIR 崩塌为其自报数字。WorldProxy 零实验零检索协议，其 I-JEPA/V-JEPA 2 归类错误已在正文标注不得转录。以上均库内单篇证据、无独立复现；"训练信号收敛"为跨论文 pattern 而非复现。

- **2026-08-05 survey-refresh**：并入 1 篇（[[2608-WorldExam]]，full-text + source-checked，Evidence Ledger 23 行全为 source-verified）。结构性变化：新增路线 10「诊断式评测：把"指令写明的后果"与"须自行推断的后果"分开」——survey 此前只有 Open Problem 6 承载评测方法论、无对应正文小节，这一篇给了它锚点。路线 1 的缺点表新增"控制被执行但世界不回应"作为与 action-following 相互独立的失效面；路线 6 的 optimistic bias gap 补入方向一致的生成侧读数；路线对比表 pixel 行的 open gap 加入 world reactivity。Overview 趋势 +17；Key Takeaways +31/32，Takeaway 24 由单篇（Phi-Zero）扩为三个角度的同向证据；Open Problem 6 更新并新增 24/25；Benchmarks 表 +WorldExam。未刷新配图（本 survey 无配图，本轮为新增小节而非分类框架重构）。
  - **证据边界**：接口范式与模型档次共线是这篇最主要的问题——dynamic track 上 action-driven 仅 2 个本地模型对 language-driven 7 个 API 系统，"action 接口 → 世界不反应"与"这两个特定模型 → 世界不反应"在其数据里分不开，论文未将此列为 limitation。范式内方差大于范式间（Kling 2.5 的 Task 39.85 低于 LingBot-World 39.91，范式内跨度 25 分），"language-driven 更会反应"实由三个最强系统撑起。四个 checklist 任务的 ground truth 由未具名 LLM 起草、refiner 改写后定稿，人工只筛初始图；human alignment 验证的是 judge 而非 checklist。judge 只看 10 帧且无敏感性分析。六个动态任务初始图全为合成、生成模型与候选数未披露，与 static track 输入不同源；每 case 只跑一次生成。"20 个模型"仅指 static track，reactivity 层实际 9 个。数据与 toolkit 尚未发布。以上均为库内单篇证据，无独立复现；与 [[2607-GigaWorld1]] 在 contact 失效点上的收敛属跨论文 pattern，非复现。
- **2026-08-04 survey-refresh**：并入 5 篇（[[2607-QQWorld]] / [[2607-STWAM]] / [[2607-WCM]] / [[2607-MentalWorldModeling]] / [[2607-N0TWAM]]，均 full-text；ST-WAM 为 partial 核查，其余 source-checked）。结构性变化：路线 4 新增"被预测的未来该是什么表示"分支（ST-WAM 双空间未来 + N0-TWAM 触觉未来），路线 5 新增 critic 侧分支 WM-as-Critic 并在路线对比表 +1 行、Unified VLA+WM 行补 2 篇代表工作；路线 2 补 QQ-World，路线 9 补 MWM（Levels × Laws 中 Social 约束域的首篇）。Overview 趋势 +14/15/16；Key Takeaways +26–30，Takeaway 12 由六种耦合改为七种（新增 critic 侧，[[2607-WCM]]）；Open Problems 更新 7、新增 21–23；Benchmarks 表 +LIBERO-Plus / UniVTAC / Menti-Bench 三行。未刷新配图（本轮为分支新增，分类框架未重构）。
  - **证据边界**：ST-WAM 的核心机制断言（pixel-generative 未来监督造成 entanglement）在笔记 Evidence Ledger 中状态为 `unsupported`，全文无任何 entanglement 度量，本轮只引用其消融数字与负结果；其 LIBERO / RoboTwin 表未交代 baseline 来源、全文无参数量，唯一同示教同流程的干净对照是真机组。N0-TWAM 的 NeoData / NeoSim / NeoReal / NeoForce 均出自同一份公司网页报告，规模数字一手出处不可独立核查；真机每任务 20 trials，二项标准误约 ±11%，逐任务存在方向反转。WCM 全文无 value-accuracy 指标，"预测目标 → 值估计更准 → 策略更好"只有两端被测；SIGReg 在 on-policy 下关闭，仿真结果实际只有 $\mathcal{L}_{\text{pred}}$ 生效。MWM 只报 final-action F1，其自定义的过程级指标全部无数值，benchmark 与被测 pipeline schema 同源。QQ-World 只在单一 LeWM backbone 上验证，Reacher / OGBench 增益落在标准差内，三条 proposition 未给证明。以上均为库内单篇证据，无独立复现。
- **2026-08-02 survey-refresh**：并入 2 篇（[[2607-PhiZero]] / [[2607-WorldActionPlanner]]，均 full-text + source-checked）。结构性变化：路线 1 新增 reason-then-render 分支（离散"物理语言"中间表示 + 扩散渲染），路线 5 新增推理期 WM-as-Planner 分支并在路线对比表 +1 行；Overview 趋势 +12/13；Key Takeaways +24（生成保真不蕴含物理判别，把 Takeaway 16 从 evaluator 场景推广为一般性质）、+25（推理期规划）；Takeaway 12 由五种耦合改为六种；Open Problems 2/4/6/7 更新；Benchmarks 表 +Physics-IQ / IntPhys2 / LikePhys-WorldModelBench 三行。未刷新配图。
  - **证据边界**：Phi-Zero 缺同数据同算力、仅移除中间表示的对照，21.2→41.2 的增益混淆表示/数据/训练；其 "zero-shot" 迁移仍需按源域微调 tokenizer，无代码发布。WAP 全仿真无真机，使用 URDF、相机标定与硬编码抓放原语，"72 vs 0" 不可读作 world model 单独贡献（仅 Table 9 隔离）；+11.4%/+16.8% 为 PSNR 与 LPIPS 相对提升再平均，论文自承构造可疑。
- **2026-07-29 survey-refresh**：并入 4 篇（[[2510-RWoM]] / [[2607-ObjectCentricEnv]] / [[2606-EnvEngineeringSurvey]] / [[2607-Wonder]]）。路线 1 新增 camera-controllable video WM 的 control–memory–distillation co-design 与严格证据边界；路线 7 补 external-tutorial grounding 与 executable object/procedure model；路线 9 引入 environment lifecycle 视角；Benchmark +1，Key Takeaways +21–23，Open Problems 更新 3/9/19 并新增 20。无新平行 taxonomy，未刷新配图。
- **2026-07-21 survey-refresh**：并入 17 篇（WebDreamer / DreamGym / RynnWorld-Teleop / WAC / UI-Simulator / WebSynthesis / RynnWorld-4D / AlayaWorld / Memoir / FlowWAM / RehearseVLA / SeerGuard / ABot-M0.5 / BadWAM / Orca / GigaWorld-1 / PixelsToStates），skip 3 篇非 WM（LaMem-VLA / DART / Xiaomi-Robotics-1）。结构性变化：路线 6 更名 WM-as-Policy-Evaluator 并以 GigaWorld-1 为旗舰；路线 7 扩为 Digital-Domain World Model（Web/GUI）五用途表；路线对比表 +2 行；Key Takeaways +16–20；Open Problems +17–19。
- **2026-07-20 合并 WorldActionModel-Survey**（Supervisor 指示同方向 survey 整合）：该 survey 的 8 篇论文（DreamZero/UWM/Motus/DreamGen/World-VLA-Loop/IRASim/Cosmos/RWM）本已全部覆盖于路线 1/2/4/5，属完全子集。本次仅并入其独有内容：路线 4 标题补 WAM 命名与 "world models are implicit policies" 范式定义、action-free video data 优势论证；Benchmark 表 +Push-T/DreamGen Bench/TokenBench；Open Problem +16（WAM scaling laws）。原文见 git history。
- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 4 篇（Archive）+ 2 篇（Papers）+ 新创建 6 篇 + 补充 4 篇（World-R1, dWorldEval, EmotionPose, AgenticCache）+ VLA 相关 3 篇（M²-VLA, Tube Diffusion Policy, CF-VLA）= 19 篇
- **未能获取**: 无（基于已有月度总结和 candidates.json 创建笔记）
- **MindFlow 合并**: 2026-04-30，从 MindFlow repo 合并 WorldModel-Survey，新增 5 条技术路线（Pixel video diffusion / Latent JEPA / 3D-4D generative / Unified VLA+WM / WM-as-RL-simulator）、6 条 Key Takeaways、7 条 Open Problems、路线对比小结表
