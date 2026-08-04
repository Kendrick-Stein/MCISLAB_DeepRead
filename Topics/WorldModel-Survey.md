---
title: World Model Survey
tags: [world-model, agent, simulation, planning, MBRL, VLA, diffusion-policy, cross-embodiment]
date_updated: "2026-08-04"
year_range: 2024-2026
papers_analyzed: 47
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
14. **新发现**："被预测的未来该是什么表示"成为 WAM 的显式设计轴——[[2607-STWAM]] 在 VAE 未来之外并行预测 DINO 语义未来，[[2607-N0TWAM]] 把触觉与视觉一起当生成目标；但两篇的消融同向指向一个反直觉结论：新增的那条**预测**通路不是主要收益来源
15. **新发现**：world prediction 进入 RL 的 critic 侧——[[2607-WCM]] 让 critic 在预测 return 的同时预测下一帧 latent，drop-in 替换四种 VLA RL 算法的原 critic；λ=0 的 history-ViT 对照把增益与"多看几帧"分开
16. **新发现**：Levels × Laws 中长期空置的 **Social 约束域**出现第一篇正面工作——[[2607-MentalWorldModeling]] 把 belief/goal/intention 升格为随动作演化的状态变量；但其消融显示移除 physical 通道（−16.5）比移除 mental 通道（−12.1）代价更大

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
- [[2607-QQWorld]]（西安交大）：把 latent WM 的分布正则从 Epps–Pulley 特征函数检验换成 quantile–quantile 匹配。可迁移的判据藏在两条 proposition 的对比里——EP 的恢复力 $\sqrt{\pi}\,h\,e^{-h^2/4}$ 在 $h=\sqrt{2}$ 达峰后超指数衰减，偏离越远梯度越小，正好放过最该被拉回的离群点；QQ 的梯度 $2(x_n - q_\rho(n))$ 对偏差线性。**一个善于"度量"分布差异的统计量未必是好的"训练目标"，其梯度场必须处处有信息**。planning 平均 79.75→85.08（4 环境 × 6 seed），tail rate 0.315→0.123，EP 统计量 119.909→82.294。边界：只在单一 LeWM backbone 上验证，Reacher +2.66 与 OGBench +3.00 落在标准差内，相对 DINO-WM 仅 +0.33pp，三条 proposition 原文未给证明，无代码

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

**路线内分支：被预测的未来该是什么表示**。WAM 的默认答案一直是"未来 RGB 或其 VAE latent"，2026-07 出现两篇从不同方向撬动这个默认值的工作——一篇加语义通道，一篇加触觉通道——而它们的消融给出了同向的负信号。

- [[2607-STWAM]]（partial 核查）：在 VAE 未来之外并行预测冻结 DINOv3 的语义未来（Dual-Space Future Experts，三分支 MoT 联合 flow matching），并用 Qwen3-VL 抽取的当前视觉-语言语义作 query，从 4 帧 DINO history 检索 intent token 注入 action expert（CAIR）。结构化 cross-branch mask 让 action token 读不到任何 future 流，因此推理时两条 future 分支可整体切掉，代价只有 1.24× 延迟。LIBERO 98.7 / RoboTwin 2.0 92.77 都在饱和区，真正的落点是零样本 LIBERO-Plus 72.8 对 Fast-WAM 51.5、真机视觉偏移 61.5 对 25.8。**两个负结果比主结果更有信息量**：只用 DINO 未来在 LIBERO-Plus 掉到 39.7，低于纯 VAE 的 51.5——语义表示丢掉了动作需要的细粒度动力学，两者互补而非可换；无锚点的 DINO history 检索只有 56.5，低于完全不用 intent 条件的 66.4。边界：论文用来定义问题的机制断言（"pixel-generative 未来监督把 action-relevant transition 与 task-irrelevant 视觉内容纠缠"）在笔记 Evidence Ledger 中状态为 `unsupported`——原文措辞 hedged 且无任何 entanglement 度量，本 survey 只引用其消融数字与负结果，不引用该机制；LIBERO-Plus 的 baseline 数字引自第三方研究，LIBERO / RoboTwin 表未交代 baseline 来源，全文无参数量，唯一能确认同示教同流程的干净对照是真机那组；评测的偏移全部是外观级（背景/光照/视角/传感器噪声），而 DINOv3 恰好是对该类扰动不变的表示
- [[2607-N0TWAM]]（NeoteAI / Fudan TEAI）：把 touch 放进*被预测的未来*而不是当输入或外挂——video / tactile / action 三个 expert 只共享一层 self-attention，frame-id causal mask 组成 predict-then-act cascade；触觉走双通路，latent 空间里以残差形式**预测**未来触觉，force 空间里由 NeoForce encoder 经零初始化 cross-attention **观测**当前触觉。UniVTAC 84.5 对 InternVLA-A1 67.1、NeoSim 49.4 对 π0.5 45.8、真机 46.3 对 30.0。**消融削弱了它自己的新颖性叙事**：预训练规模是 UniVTAC 上最大的单一因素（84.5→65.4），大于任一触觉通路；两个 benchmark 上去掉反应式的 observed 通路（即既有 tactile policy 的做法）都比去掉前瞻式的 predicted 通路（本文的新颖处）掉得更多——70.5 vs 71.8、29.6 vs 41.1。边界：全文没有"去掉 future-vision 预测"的消融，也没有"两条触觉通路同时关闭"的联合对照，因此 predict-then-act 相对直接回归动作的增量在本文内部无 matched 对照；tactile punctuation 的 staging 机制本身无消融；real-time 主张无任何 ms / Hz / FLOPs 数字；三套件中只有 UniVTAC 是第三方公开 benchmark，NeoData / NeoSim / NeoReal / NeoForce 全部出自同一份公司网页报告，规模数字的一手出处不可独立核查；真机每任务仅 20 trials，论文自述二项标准误最高约 ±11%，且逐任务存在方向反转（NeoSim Cup Handover 全模型 14 而 w/o predicted 65）

这条分支目前的共同信号是：两篇都在扩展"未来"的表示，两篇的消融却都显示**新增的那条预测通路不是主要收益来源**——ST-WAM 的语义未来必须与 VAE 未来并存才有用、单独使用反而更差，N0-TWAM 的预测触觉输给反应式的观测触觉。这不推翻 "world models are implicit policies"，但它给"预测更多模态/更多表示的未来 → 更好的动作"这条推论加了边界条件。库内暂无独立复现，两条均为单篇证据。

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

**缺点**：仿真器质量瓶颈（video WM action-following 普遍弱）；Long-horizon 死穴（AR video drift >200 帧；RehearseVLA LIBERO-Long 仅 +0.8）；评估样本量小。

**推理期分支：WM-as-Planner**。上述用法都在训练期消费 world model（当仿真器、当 condition source），[[2607-WorldActionPlanner|WAP]] 把它整个挪到推理期：VLM agent 提出子目标，action-conditioned WM 在想象中评估，policy 降级为被调用的执行工具，构成 propose → optimize → search 闭环。让这一反转在视频骨干上可行的是 **pose-image conditioning**——候选动作先经正向运动学渲染成骨架图像、再由 VAE 编码送进 Wan-T2V-1.3B（4 视角 2×2 拼图，21 帧 @7FPS 历史 → 20 帧 @20FPS 未来），从而绕开低维动作向量与视频生成骨干之间的接口失配（与 [[2607-GigaWorld1]] 关于 channel-concat pose map 优于 cross-attention 的结论同向）。结果：compositional LIBERO-Long 四设定 72/68/78/70，对照 π0.5 的 4/0/0/0 与 cosmos-policy 全 0；新布局六设定 88/86/90/66/84/78，baseline 多为 0；zero-shot Robosuite 80/76 对纯 VLM planner 的 58/22。消融阶梯从 56/28/46/32 起，依次加入 global optimization、local search、policy rollout imagination 逐级抬升；1 次想象即胜过带 ground-truth reward 的 BoN-8（60 vs 42）——在这一设定下想象比重采样更省。

边界同样清楚：WAP 使用 URDF、相机标定与硬编码 GRASP/RELEASE 原语，"72 vs 0" 因此是"带特权信息的模块化系统 vs 端到端 policy"，不是 world model 单独的贡献，全文只有 Table 9 隔离了 world model 自身增益。世界建模指标（+11.4% ID / +16.8% 泛化）是 PSNR 与 LPIPS 的相对提升再取平均，其 limitation (g) 已自承该构造可疑。全部实验在仿真中完成、无真机，无 imagination horizon 扫描与误差累积测量，50 次 trial 无误差棒。

**critic 侧分支：WM-as-Critic**。上述用法都把 world model 放在 actor 一侧（当仿真器、当条件源、当规划器），[[2607-WCM]]（同济 / 上海创智学院 / 复旦）把它挪到 critic 一侧：critic 在预测 return 的同时预测下一帧的 LeJEPA latent，损失为 $\mathcal{L}_{\text{value}} + \lambda \mathcal{L}_{\text{pred}}$，可 drop-in 替换 PPO / Flow-SDE / AWR / RECAP 四种 VLA RL 算法的原 critic，覆盖 149 个仿真任务与 7 个 WidowX-250S 真机任务。**决定性的对照是 λ=0 的 history-ViT 变体**——同样吃多帧历史、同样多的时序建模容量，但不带世界预测目标，结果依然无效；这把"增益来自世界预测"与"增益来自多看几帧"分开了，是这条分支目前最硬的证据。另一个值得记的读数是 λ 扫描下 OOD 成绩波动 10.6pp 而 IND 只波动 2.7pp——预测权重主要影响的是分布外行为。

边界：全文没有任何 value-accuracy 指标，因此"预测目标 → 值估计更准 → 策略更好"这条因果链只有两端被测、中间未测；LIBERO-Plus 上 one-shot SFT + 约 250 步 RL 超过 20k 轨迹 Full-SFT 的结论只领先 0.8–2.3，且部分子维度回退；OFT 的 OOD 增益仅 +0.8；LeJEPA / SIGReg 为借用组件，且 SIGReg 在 on-policy 下关闭，仿真结果实际只有 $\mathcal{L}_{\text{pred}}$ 生效；baseline 无误差棒，也无训练开销对照。

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
- [[2607-MentalWorldModeling]]（MWM / Mentis）：Levels × Laws 中 **Social 约束域**在本 survey 的第一篇正面工作——把 belief / goal / intention / emotion / norm 从"事后 rationale"升格为 world state 的一等成分，状态空间因子化为 $S = S_{\text{phy}} \times S_{\text{men}}$，观测定义为从第三人称联合状态渲染出的 target 第一人称部分观测（允许与真实心理状态不符，这正是 false belief 得以被表达的形式化理由），动作写成 (physical carrier, mental content) 的耦合对，物理转移不直接条件于 mental content。实例化为 training-free 的六阶段 pipeline Mentis + 448 条 process-annotated 的 Menti-Bench（2,688 个 gold 后继状态）。最值得借用的是它的审计模板：necessity ladder（S0 options-only floor 31.3 → S1 direct 63.3 → S2 CoT 74.6 → S3 SC@6 77.9 → S4 free-text state 80.3 → S5 structured state 82.6 → S6 full MWM 87.9，human 98.5，每级只增加一个建模承诺）+ channel intervention + oracle cascade，其中 oracle 增益的 sub-additivity（四个单增益之和 8.7 > 四者组合 6.3）干净地量化了模块化 pipeline 的跨阶段误差税。边界：全文只报 final-action F1，6.2 节与 Appendix G 定义的 mental fidelity / perspective-leakage rate / process-outcome divergence 一个数值都没报，因此"涨点是因为心理状态被正确建模"没有中间证据；消融是纯信息移除、无等量非心理内容的对照，且移除 physical 通道（−16.5）比移除 mental 通道（−12.1）代价更大，与标题重心相反；S6 的调用量约为 S1 的二十几倍而全文无 token 成本表；Menti-Bench 的 gold 按 MWM 自身 taxonomy 标注、gold 动作由同一批作者裁定为"唯一可辩护最优"，S6 天然享有 schema 对齐红利；单步转移、封闭 6 选项动作空间
- [[2606-EnvEngineeringSurvey]]：以 environment lifecycle 而非单个 model 组织领域——八属性二分 × 八 domain → symbolic/neural synthesis → correctness/diversity/complexity/fidelity evaluation → agent/environment co-evolution。它补充 Levels × Laws 的“能力/约束”视角：world model 只是 neural environment synthesis 的 pixel/word/latent 三层之一；survey 自身也承认 correctness 之外三项质量维度 under-researched，co-evolution 仍是未来方向而非已完成机制

**路线间对比小结**：

| 路线 | 代表 | 主要 use case | 推理代价 | 主要 open gap |
|---|---|---|---|---|
| Pixel video diffusion | Cosmos / DreamGen / IRASim / Wonder | Data engine / Evaluator / camera exploration | 14B × 多步 → 秒级；Wonder 报 16 FPS（硬件未披露） | Action-following / physics / AR drift / total KV growth |
| Latent JEPA | V-JEPA 2 / RWM / Orca | Agent brain / MPC | 16s → ms 级 | Goal spec / cross-embodiment / 不生成像素 |
| 3D/4D generative | HY-World 2.0 / OccSora / RynnWorld-4D | Scene generation / driving sim | 分钟级/场景 | dynamics 依赖伪标注几何 / 小物体精度 |
| Unified VLA+WM | UWM / Motus / DreamZero / FlowWAM / ABot-M0.5 / ST-WAM / N0-TWAM | VLA policy backbone | 百 ms 级（工程后） | 算力门槛 / unify 必要性 / action–imagination 同步性 / 新增预测通道归因不清 |
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
| LIBERO-Plus | 10,030 例 / 七维扰动 | 零样本 Success Rate | ST-WAM 72.8（Fast-WAM 51.5） | LIBERO 的扰动版，已成为 WAM 视觉鲁棒性主力评测；ST-WAM 表中 baseline 数字引自第三方而非重跑（[[2607-STWAM]]） |
| UniVTAC | 8 个触觉操作任务 | Success Rate | N0-TWAM 84.5（InternVLA-A1 67.1） | 唯一第三方公开的触觉 manipulation 套件；纯视觉 WAM 在此反而落后 VLA（FastWAM 48.0 / LingBot-VA 31.4），该异常低水位未被解释（[[2607-N0TWAM]]） |
| Menti-Bench | 448 条（320 text / 100 image / 28 video），2,688 个 gold 后继状态 | final-action F1 | full MWM 87.9（human 98.5） | 心理-社会状态的 process-annotated 世界建模评测；只报 outcome 级指标，且 gold 与被测 pipeline schema 同源（[[2607-MentalWorldModeling]]） |

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
20. **失败/次优数据是 WM-as-simulator 的关键 ingredient 获再次确认**——[[2606-RehearseVLA]] 探索数据是最大单因素（Goal 68.4→86.4），与 World-VLA-Loop 的 SANS 结论互证
21. **Memory 必须分开讨论 storage、active compute 与 semantic faithfulness**——[[2607-Wonder]] 固定 active KV set 只解决 attention cost，不限制 full historical KV storage；[[2603-HybridMemory]] 测动态主体 exit–reentry、Wonder 只给静态 revisit qualitative case，两者尚不能互相替代
22. **Digital WM 的 grounding 开始分化为 external prior 与 executable structure 两条路线**——[[2510-RWoM]] 用 tutorial 把 imagined rollout 延长到约 3 steps，[[2607-ObjectCentricEnv]] 用 object/procedure code + re-execution gate 维护一致性；共同边界是“有依据/能执行”仍不等于环境语义真实
23. **World model 不能脱离 environment lifecycle 单独评估**——[[2606-EnvEngineeringSurvey]] 将 model 放回 modeling→synthesis→evaluation→application 闭环，并指出除 correctness 外的 diversity/complexity/fidelity 仍 under-researched；这解释了为何视觉保真、action faithfulness 与 downstream policy success 长期互不等价
24. **生成保真不蕴含物理判别**——[[2607-PhiZero]] 在 Physics-IQ 拿下 41.2（生成端第一）的同一模型，IntPhys2 Hard 只有 52.38（随机基线 50），LikePhys 流体倒数第三。Takeaway 16（evaluator 质量 ≠ 视觉保真）由此从 evaluator 场景推广为 WM 的一般性质：凡消费判别能力的用途（planner / evaluator / safety guard）都不能用生成指标验收，而分材料、分难度的判别 split 是目前唯一能暴露这一差距的手段
25. **WM 的用法从训练期扩展到推理期，且想象比重采样更省**——[[2607-WorldActionPlanner]] 把 policy 降级为工具、规划全程在想象中完成，1 次想象胜过带 ground-truth reward 的 BoN-8（60 vs 42）；但该系统带 URDF、相机标定与硬编码抓放原语，"72 vs π0.5 的 4" 是模块化+特权信息 vs 端到端的对比，仅 Table 9 隔离了 world model 自身贡献——归因清楚前不可引作 WM 的能力证据
26. **给 WAM 增加新的预测通道，收益未必来自"预测"那一半**——[[2607-STWAM]] 的语义未来必须与 VAE 未来并存（DINO-only future 39.7 < 纯 VAE 的 51.5），[[2607-N0TWAM]] 的预测触觉输给反应式的观测触觉（去 observed 掉到 70.5 / 29.6，去 predicted 只掉到 71.8 / 41.1），且预训练规模才是 UniVTAC 上最大的单一因素（84.5→65.4）。两条独立证据同向，但均为库内单篇、无独立复现，应作为 WAM 表示设计的边界条件而非定论
27. **检索式上下文的收益是有条件的，条件不满足时为负**——[[2607-STWAM]] 的三个对照（无锚点 DINO history 56.5 / 仅当前帧语义 62.3 / VAE history 64.7）全部低于完全不用 intent 条件的 66.4；收益要求 query 被当前状态锚定 **且** 被检索表示对无关扰动不变，缺一即掉点。这与 GUI / long-horizon agent 里"多喂历史反而掉点"是同一现象的不同实例
28. **正则项的好坏取决于梯度场而非统计功效**——[[2607-QQWorld]] 指出 Epps–Pulley 的恢复力在偏差超过 $\sqrt{2}$ 后超指数衰减，正好放过最该被拉回的离群点，而 quantile–quantile 匹配的梯度对偏差线性；换掉正则后 latent WM 的 planning 平均 79.75→85.08、tail rate 0.315→0.123。可迁移的判据是：一个善于**度量**分布差异的统计量未必是好的**训练目标**
29. **world prediction 也可以放在 critic 一侧**——[[2607-WCM]] 让 critic 联合预测 return 与下一帧 latent，drop-in 替换四种 VLA RL 算法的 critic；λ=0 的 history-ViT 对照（同样的时序容量、没有世界预测目标，依然无效）把增益与"多看几帧"分开。但全文无 value-accuracy 指标，中间机制未被直接测量，增益幅度也只有 0.8–2.3
30. **"世界"里缺的那一块是人在想什么**——[[2607-MentalWorldModeling]] 把心理变量升格为随动作演化的状态变量，填上 Levels × Laws 中长期空置的 Social 约束域；但它自己的消融显示移除 physical 通道代价更大（−16.5 vs −12.1），且只报 outcome 级指标——目前证据支撑的是"结构化 prompting 有效"，不是"心理状态被正确建模"

## Open Problems

1. **Action-following faithfulness**：video WM 对错 action 也生成成功，policy 一定能找到 WM 盾区做 reward hacking。SANS 式 near-success 数据 + reward head 是初步答案，但是否 scale 到 long-horizon / multi-agent / deformable 尚未验证；[[2606-RehearseVLA]] 冻结 WM 且不处理该风险，[[2607-GigaWorld1]] 观察到 contact-sensitive failure 的 optimistic bias——同一问题在 evaluator 侧同样存在
2. **Physics alignment 不随 scale 解决**：Cosmos 7B vs 14B 在 rigid-body benchmark 上 IoU 基本不变；候选方向：(a) hybrid physics (Genesis/PhysGen)；(b) RL on intuitive physics MCQ (Cosmos-Reason1)——但第二条只涨 VLM-level reasoning，不 carry over 到 video generation；(c) 离散符号中间表示 + reason-then-render（[[2607-PhiZero]]），生成端 Physics-IQ 41.2 领先，但缺同数据同算力、仅移除中间表示的对照，21.2→41.2 混淆表示/数据/训练三变量，且判别端未同步（IntPhys2 Hard 52.38）。三条候选都还没有把"物理"从"看起来像物理"里分离出来
3. **Long-horizon drift**：所有 autoregressive video WM 超过训练 horizon 都退化——GameNGen 3 秒、DIAMOND frame-stacking、World-VLA-Loop 200 帧、OccSora 离开 32 帧 FID 飙 200+。Explicit compressed memory、retrieval-based context、LLM-style KV cache + streaming 都是候选，但没有任何一种在 robot-relevant setting 上 demonstrated；[[2607-AlayaWorld]] 的 error bank + 双记忆零定量评估，[[2607-Wonder]] 的 full-fidelity sparse KV 只固定 active attention 且长期一致性仍为 qualitative evidence。后续必须同时报告 quality/control/revisit metric、latency 与 total memory 随 horizon 的曲线
4. **Latent vs pixel 的路线之争**：V-JEPA 2 给出 15× 计算优势 + success rate 反超 Cosmos；DreamZero 反过来用 14B pixel WAM 达到 62.2%。[[2607-PhiZero]] 提出第三种位置——在离散符号空间推理、再渲染回像素，兼取 latent 的低维推理与 pixel 的可视化输出，但它同时是这条路线最直接的警示：判别能力没有随生成能力一起上来（IntPhys2 Hard 52.38 落后于纯 latent 的 V-JEPA 57.42）。**真正的 open question**：long-term 哪一条路径 scale 更好？或三者按用途分工（cloud-side pixel WM 做 data engine，符号中间层做 planner，edge-side latent WM 做 on-device MPC）？
5. **Cross-embodiment transfer 真能靠 video 做到吗？**：DreamZero 的 12 min 人类 egocentric / 20 min YAM robot video → unseen task +16pp 是至今最强信号；但 humanoid 五指手 vs bimanual gripper 级的 morphology gap 尚未被 video WM 路线 attack
6. **Benchmark metric 的 unresolved confound**：video fidelity (FID/FVD) ↔ physical faithfulness (VBench-2.0, PhysBench) ↔ policy success (DreamGen Bench / LIBERO SR) 三者相关但不等价。系统化的"哪个 metric 评 WM 公平" 的框架尚未建立。[[2607-PhiZero]] 把 confound 收窄成一个可操作的判据：生成式（Physics-IQ）与判别式（IntPhys2 Hard）在同一模型上给出相反排序，因此 WM 论文至少应同时报告两类指标，并按材料/难度分层——聚合分会掩盖流体等薄弱项（LikePhys 刚体第一、流体倒数第三）
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
19. **Digital WM 的转移幻觉与 reward 审计**：[[2511-DreamGym]] 的经验模型既当转移函数又当 reward 函数、无外部审计；[[2510-RWoM]] 的 tutorial grounding 只把 compounding error 推迟到 horizon≈3，[[2607-ObjectCentricEnv]] 的 re-execution 只保证 runnable consistency。"合成转移 + 真实 verifier"的混合方案是否优于两个纯路线未验证
20. **Environment quality 的非 correctness 维度如何操作化**：[[2606-EnvEngineeringSurvey]] 明确指出 diversity、complexity、fidelity under-researched；需要把这些维度变成可重复测量，并与 agent learning progress、reward hacking 与 sim-to-real error 建立因果而非相关关系
21. **扩展"被预测的未来"，边际收益到底来自哪里**：[[2607-STWAM]] 与 [[2607-N0TWAM]] 各加了一条新的未来预测通道（语义 / 触觉），两篇的消融却都显示新增的**预测**通路不是主要收益来源；N0-TWAM 从未做"去掉 future-vision 预测"的消融，也无"两条触觉通路同时关闭"的联合对照，ST-WAM 则无参数量、主表 baseline 来源不明。需要的是在同一 backbone、同一数据与算力下逐条移除预测目标的 matched 对照，否则这条路线的收益无法与规模、额外参数与冻结 encoder 的先验分离
22. **表示的"不变性 × 可分性"在何种偏移下同时成立**：[[2607-STWAM]] 依赖 DINOv3 对外观扰动的不变性，而其评测的偏移恰好全是外观级；[[2607-N0TWAM]] 的 NeoForce 只在其预训练传感器（InTac S1）上验证，仿真因传感器不匹配直接放弃 force space。换成物理动力学、embodiment 或传感器型号级别的偏移时，什么表示能同时做到"对无关扰动不变"与"对任务状态可分"，两篇都把它列为 future work
23. **心理 / 社会状态的 world model 缺过程级验收**：[[2607-MentalWorldModeling]] 定义了 mental fidelity、perspective-leakage rate、process-outcome divergence 却一个数值都没报，benchmark 与被测 pipeline 共享 schema、gold 由同一批作者裁定为唯一可辩护最优（真正有多个可辩护答案的社会决策因此被系统性排除）。要让 Social 约束域从 position 变成技术路线，缺的是 learned transition、心理变量的不确定性表示，以及过程级保真度的独立测量

## 调研日志

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
