---
title: World Model Survey
tags: [world-model, agent, simulation, planning, MBRL]
date_updated: "2026-04-28"
year_range: 2024-2026
papers_analyzed: 19
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

**实际效果与优点**：视觉保真度天花板高（GameNGen 人类辨真伪仅 58–60%）；天然吸收 internet video prior；和成熟 video diffusion 工程栈复用。

**缺点与未解 gap**：
- **Action-following 不可靠**：[[2602-WorldVLALoop|World-VLA-Loop]] 展示 Cosmos-Predict 2 在错 action 下仍 hallucinate 成功——policy 在此类 WM 上做 RL 会 reward-hack
- **长时序 drift**：GameNGen 3 秒 context、DIAMOND memory bottleneck、World-VLA-Loop 主动放弃 LIBERO-Long——>200 帧后视觉/几何普遍漂移
- **物理对齐不随 scale 解决**（Cosmos Tab. 20）：需 data curation 或 hybrid physics inductive bias
- **推理成本高**：典型 14B DiT naive 5.7 s/chunk，即使 38× 工程栈加速后仍需 2×GB200 才能 7 Hz 闭环

### 2. Latent-space / JEPA-style WM（implicit representation）

**核心思路**：不重建像素，只在 representation 空间做 mask-denoising / next-state prediction，让 predictor 学 "latent dynamics"，下游用 CEM / MPC 做 planning。

**代表工作**：
- [[2506-VJEPA2|V-JEPA 2]]（FAIR, 2025-06）：1M+ 小时视频 mask-denoising 预训练 → 冻结 + 62 小时 unlabeled Droid 视频训 action-conditioned predictor → CEM 在 latent 上 receding-horizon planning。Franka pick-and-place zero-shot 65–80% vs Octo 0–15%；**V-JEPA 2-AC 16 s/action vs Cosmos 4 min/action 且 success rate 反超**
- [[2501-RoboticWorldModel|RWM]]（ETH, NeurIPS 2025 Workshop Outstanding Paper）：GRU + 多步 autoregressive 训练学 legged robot dynamics；**architecture 不是关键，autoregressive training 才是**。在 ANYmal D / Unitree G1 上 zero-shot 硬件部署，reward 打平 250M-step model-free PPO 但只用 6M transitions

**优点**：计算高效（V-JEPA 2 对 Cosmos 的 15× 推理优势）；数据效率极高；与 MPC/CEM 天然兼容。

**缺点**：像素生成能力弱；Goal specification 受限；Cross-embodiment 验证薄；Latent 不可解释。

### 3. 3D / 4D Generative WM（空间侧）

**核心思路**：把 WM 绑到显式 3D 表示（occupancy grid、3DGS、point cloud）上，用 diffusion 在 4D 体素/pointcloud latent 空间做未来生成。

**代表工作**：
- [[2405-OccSora|OccSora]]：nuScenes 上 DiT + 4D VQVAE 生成 16 s 驾驶 occupancy video，但小物体（VRU）重建崩塌
- [[2604-HYWorld2|HY-World 2.0]]（Tencent Hunyuan）：四阶段 pipeline panorama → WorldNav → WorldStereo → WorldMirror → 3DGS，端到端 712 s 生成可交互 navigable 3D 场景。**核心 insight 是 keyframe-latent VDM**
- [[2604-GenWorldRenderer|Generative World Renderer]]：ReShade + RenderDoc 从 AAA 游戏截取 G-buffer，fine-tune Cosmos-DiffusionRenderer
- [[2604-SpatialEvo]] (🔥 Rating 3)：3D 空间推理的答案可以从点云和 camera pose 确定性计算（DGE），不需要 model voting；w/o Physical Grounding → VSI-Bench 从 46.1 暴跌到 18.8

**优点**：显式 3D 可验证几何；直接对接 CG 渲染 / 物理引擎。

**缺点**：Temporal dynamics / action 缺失（本质是 scene generator 而非 world model）；数据稀缺；精度-压缩权衡。

### 4. Unified Video-Action / VLA+WM Joint Models

**核心思路**：把 VLA（policy）、forward dynamics（WM）、inverse dynamics、video generation 统一进一个模型，通过 timestep / mask 切换。

**代表工作**：
- [[2504-UWM|UWM]]（RSS 2025, UW & TRI）：**"diffusion timestep ≡ soft mask"**——给 action 和 future obs 独立采样 timestep，推理时切换 policy / forward dynamics / inverse dynamics / video prediction 四个条件分布。DROID 2K 预训练 + 5 个 Franka 任务全面超 DP/PAD/GR1
- [[2512-Motus|Motus]]（Tsinghua, 2025-12）：**Mixture-of-Transformers + Tri-modal Joint Attention + UniDiffuser-style scheduler**，5-mode 真正跑通。RoboTwin 2.0 randomized +43% over π0.5
- [[2602-DreamZero|DreamZero]]（NVIDIA GEAR, 2026-02）：14B **World Action Model** 从 Wan2.1-I2V-14B 初始化，joint 预测 video + action；**38× 工程加速 + DreamZero-Flash** 做到 7 Hz 闭环。AgiBot G1 unseen-env+unseen-object 62.2% vs best pretrained VLA 27.4%（>2×）
- [[2512-GenieReasoner|GenieReasoner]]（AgiBot, 2025-12）：**FACT (Flow-matching Action Tokenizer)**——VQ-encoder 把动作压成离散 code，flow-matching decoder 重建高保真连续轨迹
- [[2604-M2VLA]]：Mixture of Layers + Meta Skill Module，保留 VLM 泛化
- [[2604-CFVLA]]：Coarse-to-fine action generation，83.0% real-robot success，-75.4% latency

**优点**：参数共享 / 部署简化；video prior 显式注入 action learning 的最自然方式。

**缺点**：算力门槛极高（Motus 18 000 GPU-hours、DreamZero 需 2×GB200）；边际收益不一定大（Motus Joint mode 比 VLA mode 只 +3pp）；高精度任务不 hold。

### 5. WM-as-RL-Simulator / WM-Conditioned VLA (Loop 路线)

**核心思路**：用 video WM 替代物理仿真器跑 GRPO / PPO，或把 WM 预测的 future latent + value 作为 VLA policy 的 inference-time condition；policy 与 WM 迭代 co-evolve。

**代表工作**：
- [[2602-WorldVLALoop|World-VLA-Loop]]（Show Lab NUS, 2026-02）：**SANS dataset + DiT reward head + co-evolving loop**。核心诊断：video WM 的 action-following 偏差让它对错 action 也生成成功 → policy reward-hack。LIBERO 三 suite +12.7% SR；real-world 13.3% → 36.7% → 50.0% 两轮迭代
- [[2602-GigaBrain05M|GigaBrain-0.5M*]]（GigaAI, 2026-02）：**RAMP** 把 RECAP 从 advantage-only 条件化推广为 (future latent, advantage) 联合条件化；WM 联合预测 future state + value 比 only-value 精度更好
- [[2501-RoboticWorldModel|RWM + MBPO-PPO]]：legged 场景证明 "long-horizon PPO + learned model" 可行

**优点**：把 WM 从"能生成什么视频"转向"能否闭环训 policy"的 actionable metric；co-evolving loop 给出 reward hacking 的实证 narrative。

**缺点**：仿真器质量瓶颈（video WM action-following 普遍弱）；Long-horizon 死穴（AR video drift >200 帧）；评估样本量小。

### 6. Robotic Policy Evaluation (新方向)

**代表工作**：[[2604-dWorldEval]] (Rating 2)

**核心思路**：用 discrete diffusion world model 作为 policy evaluation proxy

**关键创新**：
- **Progress token**: 任务完成度指示，progress=1 时判定 success
- 统一 token space: vision + language + action 全部 token 化
- Sparse keyframe memory: 维护 spatiotemporal consistency

### 7. UI/GUI World Model

**代表工作**：
- [[2600-MobiledreamerGenerativeSketchWorld]]：文本草图世界模型 + 回滚想象策略，+5.25% AndroidWorld
- [[2500-UisimInteractiveImageBased]]：两阶段 UI simulator（layout prediction → layout-to-image）

**核心思路**：预测 UI 状态转移，支持 agent planning

### 8. Planning Efficiency (相关方向)

**代表工作**：[[2604-AgenticCache]] (Rating 2)

**核心思路**：利用 plan locality，cache-based plan reuse 替代 per-step LLM calls。+22% success rate，-65% latency，-50% token usage。

### 9. Conceptual Framework (Survey)

**代表工作**：
- [[2604-AgenticWorldModel]]：Levels × Laws taxonomy（🔥 Rating 5，最系统的 Survey）
- [[2411-WorldModelSurvey|Ding et al. 2024/CSUR]]：implicit/predictive 二分 + cloud-side / edge-side 切分

**路线间对比小结**：

| 路线 | 代表 | 主要 use case | 推理代价 | 主要 open gap |
|---|---|---|---|---|
| Pixel video diffusion | Cosmos / DreamGen / IRASim | Data engine / Evaluator | 14B × 多步 → 秒级 | Action-following / physics / AR drift |
| Latent JEPA | V-JEPA 2 / RWM | Agent brain / MPC | 16s → ms 级 | Goal spec / cross-embodiment / 不生成像素 |
| 3D/4D generative | HY-World 2.0 / OccSora / SpatialEvo | Scene generation / driving sim | 分钟级/场景 | 无 dynamics / 小物体精度 |
| Unified VLA+WM | UWM / Motus / DreamZero | VLA policy backbone | 百 ms 级（工程后） | 算力门槛 / unify 必要性 |
| WM-as-RL-simulator | World-VLA-Loop / GigaBrain-0.5M | VLA RL post-train | 30 h / 任务级 | Action-following / 样本量 |

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
| RoboTwin | - | Success Rate | dWorldEval | Robotic manipulation |
| CALVIN | - | Success Rate | CF-VLA | Long-horizon manipulation |

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
12. **WM × VLA 的五种耦合方式全部被实证验证**——offline data engine → inference-time latent conditioning → joint model → RL simulator → evaluator
13. **scale 不能 alone 解决 physics**——Cosmos 7B vs 14B 在 rigid-body benchmark 上 IoU 基本不变（0.59 vs 0.60）
14. **"video model as data engine" 是可 scale 的新 sub-paradigm**——DreamGen 从单一 pick-and-place teleop 数据解锁 22 个新动词 / 10 个新环境
15. **PID > RL 在 sparse reward 场景**——RWM 的 autoregressive training + imagination-PPO 可换 250M transitions 的 model-free 水平

## Open Problems

1. **Action-following faithfulness**：video WM 对错 action 也生成成功，policy 一定能找到 WM 盾区做 reward hacking。SANS 式 near-success 数据 + reward head 是初步答案，但是否 scale 到 long-horizon / multi-agent / deformable 尚未验证
2. **Physics alignment 不随 scale 解决**：Cosmos 7B vs 14B 在 rigid-body benchmark 上 IoU 基本不变；候选方向：(a) hybrid physics (Genesis/PhysGen)；(b) RL on intuitive physics MCQ (Cosmos-Reason1)——但第二条只涨 VLM-level reasoning，不 carry over 到 video generation
3. **Long-horizon drift**：所有 autoregressive video WM 超过训练 horizon 都退化——GameNGen 3 秒、DIAMOND frame-stacking、World-VLA-Loop 200 帧、OccSora 离开 32 帧 FID 飙 200+。Explicit compressed memory、retrieval-based context、LLM-style KV cache + streaming 都是候选，但没有任何一种在 robot-relevant setting 上 demonstrated
4. **Latent vs pixel 的路线之争**：V-JEPA 2 给出 15× 计算优势 + success rate 反超 Cosmos；DreamZero 反过来用 14B pixel WAM 达到 62.2%。**真正的 open question**：long-term 哪一条路径 scale 更好？或两者互补（cloud-side pixel WM 做 data engine / policy evaluator，edge-side latent WM 做 on-device MPC）？
5. **Cross-embodiment transfer 真能靠 video 做到吗？**：DreamZero 的 12 min 人类 egocentric / 20 min YAM robot video → unseen task +16pp 是至今最强信号；但 humanoid 五指手 vs bimanual gripper 级的 morphology gap 尚未被 video WM 路线 attack
6. **Benchmark metric 的 unresolved confound**：video fidelity (FID/FVD) ↔ physical faithfulness (VBench-2.0, PhysBench) ↔ policy success (DreamGen Bench / LIBERO SR) 三者相关但不等价。系统化的"哪个 metric 评 WM 公平" 的框架尚未建立
7. **WM × VLA 耦合方式的 trade-off space**：当前 5 种耦合方式都有代表工作，但没有 head-to-head 比较。在同等 compute / data 预算下，哪种耦合方式对 sample efficiency 最敏感？
8. **开源 vs 工业化：可复现性断层**：Cosmos 10 000 H100 × 3 个月、Motus 18 000 GPU-hours、DreamZero 2×GB200——任何"主脉络" WM 都远超学术实验室预算
9. **Agent memory 与 World Model 的边界**：OpenWorldLib 把 long-term memory 写进 world model 定义，但 Memory 接口留空。LLM agent 社区的 memory 机制如何与 video WM 的 latent space 交互？
10. **L3 Evolver 实现**：当 prediction 失败时如何自主修正模型？
11. **World Model 的 failure mode 系统性分析**：RAGEN-2 发现 template collapse，但其他 failure mode 未知
12. **Deterministic vs Probabilistic 的 trade-off**：DGE 适用边界如何扩展？
13. **World Model for GUI Agent 的 grounding 问题**：如何与 grounding robustness 结合？
14. **Progress token 作为 L3 Evolver 信号**：能否用于自主修正触发？
15. **Plan locality 的适用边界**：是否适用于所有 embodied tasks？

## 调研日志

- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 4 篇（Archive）+ 2 篇（Papers）+ 新创建 6 篇 + 补充 4 篇（World-R1, dWorldEval, EmotionPose, AgenticCache）+ VLA 相关 3 篇（M²-VLA, Tube Diffusion Policy, CF-VLA）= 19 篇
- **未能获取**: 无（基于已有月度总结和 candidates.json 创建笔记）
- **MindFlow 合并**: 2026-04-30，从 MindFlow repo 合并 WorldModel-Survey，新增 5 条技术路线（Pixel video diffusion / Latent JEPA / 3D-4D generative / Unified VLA+WM / WM-as-RL-simulator）、6 条 Key Takeaways、7 条 Open Problems、路线对比小结表