---
title: Embodied AI Survey
tags: [survey, VLA, manipulation, navigation, embodied-ai, robotics, embodied-reasoning, mobile-manipulation]
date_updated: "2026-08-04"
year_range: 2023-2026
papers_analyzed: 111
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

4. **数据引擎与 world model 角色分化（2026）**：human/手持视频数据引擎给出 data scaling 直接证据（[[Papers/2607-EgoSteer|EgoSteer]] 9.6K 小时 egocentric、[[Papers/2607-XiaomiRobotics1|Xiaomi-Robotics-1]] 100K+ 小时 UMI）；[[Papers/2607-HiFiUMI|HiFi-UMI]] 进一步把高保真 UMI 从 pre-training 辅助源推进到无需 target-task real-robot teleoperation 的 post-training 数据源。world model 则分化为 policy（WAM）、数据引擎、policy evaluator 三种角色（详见路线 3、7）。

5. **模态轴与鲁棒性轴同时打开（2026-08）**：触觉从"额外传感器"上升为 VLA 的一条建模轴——[[Papers/2607-N0VTLA|N0-VTLA]] 把触觉做成预测目标、[[Papers/2607-N0TWAM|N0-TWAM]] 把触觉做成世界模型的一路专家；但两篇姊妹作的消融彼此相左，预测式触觉与反应式触觉谁承担主要收益尚未定论（路线 9）。同期 [[Papers/2608-GSRParaVLA|GSR / ParaVLA]] 把"指令改写就崩"从数据覆盖问题重述为**模型内部的信息路由问题**——任务语义在语言主干里保留完好，失效发生在动作策略对 joint vision-language 编码引入的漂移过度敏感（路线 1）。

**核心挑战**：Embodied AI 面临四大关键瓶颈：

1. **数据与泛化**：真实机器人数据稀缺且昂贵，cross-embodiment transfer 需要解决 morphology gap；sim-to-real transfer 需要解决 domain gap。
2. **长时程决策**：Multi-step manipulation/navigation 任务中 reward 稀疏，credit assignment 困难，early exploration vs late success 的因果关系难以建模。
3. **安全与可靠性**：物理世界操作不可逆，错误操作可能导致财产损失或人身伤害；对抗攻击、data poisoning、prompt injection 带来新威胁。
4. **实时部署**：VLA 模型推理开销大，实时控制需要 sub-second latency，与多模态理解的计算需求存在矛盾。

---

## 技术路线

### 1. VLA Foundation Model 路线

**代表论文**：RT-2 (2023)、RT-X (2023)、OpenVLA (2024)、EmbodiedMidtrain (2026)、Xiaomi-Robotics-1 (2026)；领域索引见 [[Papers/2405-VLASurvey|VLA Survey (TNNLS)]]（components / low-level control policy / high-level task planner 三层 taxonomy）

**核心思路**：将 robot policy learning 从 behavior cloning 转向 foundation model paradigm——利用 web-scale vision-language knowledge，通过少量 robot demonstration fine-tuning 获得可执行 policy。

**关键里程碑**：

| Model | Year | Key Innovation | Training Data |
|:------|:-----|:---------------|:--------------|
| **RT-2** | 2023 | 首次证明 VLM→VLA 直接迁移可行 | PaLM-E/VLM + robot demo |
| **RT-X** | 2023 | Cross-embodiment positive transfer | 22 robots, 1M+ episodes |
| **OpenVLA** | 2024 | 首个开源 VLA，消费级 GPU 可部署 | Open X-Embodiment |
| **π₀** | 2024 | Physical Intelligence commercial VLA | Proprietary large-scale |
| **EmbodiedMidtrain** | 2026 | VLM→VLA 数据对齐的 mid-training | VLA-aligned VLM data |
| **[[Papers/2607-XiaomiRobotics1|Xiaomi-Robotics-1]]** | 2026 | 100K+ 小时 UMI state-transition 预训练，系统 scaling 证据 | UMI 100K+ h + cross-embodiment robot 10K h |

**核心发现**（来自 EmbodiedMidtrain）：
- VLA 数据占据与 VLM 分布大部分分离的紧凑区域——直接 fine-tune 会损失 generalization
- Data selection 应偏向 spatial reasoning 而非 text-centric tasks
- Mid-training 为 downstream VLA fine-tuning 提供更强初始化

**Data scaling 证据**（[[Papers/2607-XiaomiRobotics1|Xiaomi-Robotics-1]]）：data scale 的边际收益大于 billion 级 model size——同一 5B 模型下 action 预训练数据从 0 到 20K 小时把 unseen 环境真机成功率从 26% 提到 75%；固定 20K 小时数据时 2B/5B/10B 仅 61%/75%/79%。RoboCasa365 57.4% 超前 SOTA 10.8pt。注意：正式 scaling curve 只用了 ~20K 小时 subset，100K+ 全量的 scaling law 结论仍有限。

**Finetuning 的表征侵蚀与修复**（2026 三篇独立证据收敛）：

| 工作 | 角色 | 关键证据 |
|:-----|:-----|:---------|
| [[Papers/2606-Act2Answer|Act2Answer]] | 测量 | 把 VLM 知识题改造成"用动作作答"的 episode（剥离低层控制混淆），VLA 相比源 VLM 语义类知识普遍掉 20-40 分；layerwise probing 显示知识中层仍可解码、动作头附近衰减至近随机——问题在"读出通路"而非"数据删除"；VQA co-training 有保护作用（Magma retention 86.7% vs π₀ 36.2%） |
| [[Papers/2607-AnchorAlignVLA|Anchor-Align]] | 修复 | BC finetuning 10K 步内使 backbone GQA 掉 94%；frozen VLM 逐层蒸馏锚定 + 动作转方向词对齐 frozen language head，LIBERO-PRO 61.0→71.9、xArm7 实机相对 +91%；shuffle 标签控制实验排除"辅助任务正则化"解释。但 position swap 仅 22.6%——修复的是语义 grounding 而非空间 grounding |
| [[Papers/2607-LoRAVLA|LoRA-VLA]] | 微调配方 | π₀ 上 LoRA r=32 持平 FFT（ATP 0.74 vs 0.76）、VRAM 降 70%；vision encoder 必须全量微调（LoRA 化后崩到 0.43）——embodiment adaptation 瓶颈在视觉 domain shift 而非语义/动作层 |

结论：防遗忘机制（VQA co-training / representation anchoring）与 EmbodiedMidtrain 的 data alignment 指向同一命题——保留预训练表征与动作学习不冲突，应成 VLA 训练默认件。

**效率端的反向证据——去 LLM 的 V+L→A 架构**：[[Papers/2607-TurboVLA|TurboVLA]]（2026）表明在闭集任务分布上，把 VLM backbone 整个移出执行路径不损失成功率。架构为 DINOv3 视觉编码 + BERT 文本编码 + 6 层双向 cross-attention（权重初始化自 Grounding DINO）+ ACT decoder；LIBERO 平均 97.7%，0.2B 参数 / 0.9GB 显存 / 31.2ms（32 Hz），RoboTwin 2.0 60.2%（0.4B / 43.4ms / ≈23 Hz），真机 AgileX Piper 四任务 92.5 / 80 / 90 / 87.5%。

该结论的边界由论文自身的 ablation 划定：把语言指令替换成 task-ID embedding 只掉 2.3pp（97.7→95.4），说明 LIBERO 的语言条件接近闭集任务分类，并不构成对语义理解的真实要求。全文没有 OOD、指令改写或未见物体的泛化评测，因此可支持的命题是"闭集任务分布下 LLM 不是必需品"，而非"VLA 不需要语义先验"——后者才是路线 1 的 foundation model 主张，本文并未触及。其余待补：LIBERO-Long 94.2% 在其对比表中仅列第 6，延迟数字未声明分辨率、数值精度与编译设置，无 seed 与误差棒；表中 "Emb. PT ✗" 指未做具身预训练，不等于从零训练。

**语言鲁棒性：从数据覆盖问题重述为信息路由问题**。[[Papers/2608-GSRParaVLA|GSR / ParaVLA]]（2026）针对的是"指令换个说法 VLA 就崩"——SmolVLA 从 canonical Goal SR 72.0 掉到改写集 Full Para 4.47，VLA-Adapter 从 98.2 掉到 46.82。主流应对是扩语言数据（instruction relabeling、counterfactual 标注、consistency training），本文先追问这笔成本是否必要，并用两级实验把失效位置钉住：行为层探针固定观测、比对 paraphrase 与全部 canonical action chunk 的最近邻，Retrieval@1 为 0.675 / 0.516 / 0.941（chance 0.1），说明任务语义在语言主干里保留完好；因果干预只替换进入 VLA-Adapter 最后一个 Bridge-Attention block 的语言特征、视觉与状态一律不动，就消掉 96.8% 的动作差异，配对成功率 60%→96%。再往下两个控制实验定位漂移来源：把辅助分支的图像换成固定 dummy image（主视觉通路仍为真实观测）使 Full Para 46.82→61.58；用 5-fold task-disjoint 交叉验证估出的 32 个"措辞方向"删除后 action gap 0.4361→0.2282，而同范数随机方向只到 0.4386，闭环成功率 55%→90%。结论是**把动态图像与指令措辞喂进同一编码过程**才是漂移来源，措辞不破坏任务语义、只引入一个系统性且可分离的偏移。

据此的改造（GSR）是三步：冻结 T5-large 单独编码指令（不接收图像与机器人状态）→ 投影注入目标架构原生的多模态融合点 → 动作专家从随机初始化重训。只用 canonical demonstration、无任何 paraphrase 蒸馏或一致性损失，Full Para 做到 46.82→70.94（VLA-Adapter）、4.47→49.12（SmolVLA）、73.60→75.59（π0.5，PRIDE 70.4）。其容量对照做得比同类论文干净：只加可训练参数而不加语言模型、把 T5 换成 Qwen-VL，Full Para 都是同一个 46.82%，保留原生指令只挂 T5 也只有 47.31%——"增益来自容量"这条竞争解释被排除。注入点必须随架构走这一主张由负结果支撑：对 SmolVLA 套用 VLA-Adapter 式后端 sidecar 时 paraphrase 只有 13.49%，改注入 SmolVLM 原生 language 位置才升到 49.12%。

边界比结论更值得记：**全部仿真实验只跑在 LIBERO-Goal 的 10 个任务上，而这 10 个任务共享同一视觉场景**——一个 paraphrase-invariant 的句子编码器在 10 个固定任务上，功能与一个 10 路任务码难以区分（关掉 T5 源掉到 10%、恰为 1/10；喂错误源掉到 0%），而论文的 learned-token 对照并不读指令，因此不是 task-ID 对照。实测到的是 paraphrastic invariance，新物体、新动作、新组合一个都没测；真机所谓 OOD 改写是 "pick up"→"grasp" 这一级的词汇替换。统计口径写了但没执行：附录声明 exact McNemar 与 task-stratified bootstrap 95% CI，全文无任何 p 值、区间或误差棒，每配置单 seed——在此口径下 π0.5 的 +1.99 点与噪声无法区分，而 π0.5 恰是唯一把"动作专家重初始化"控制为常量（三配置均重初始化）、归属最干净的对照，也是效应最弱的那个；VLA-Adapter / SmolVLA 上"注入 T5"与"重初始化"始终未拆开。同表中 [[Papers/2602-XiaomiRobotics0|Xiaomi-Robotics-0]] 的 Full Para 76.0 高于 π0.5 GSR 的 75.59，论文正文自认，领先只在 PRIDE 一项，而 PRIDE 的对照链本身不完整（π0.5 Native 行的 PRIDE 为 "–"，70.4 只能与被引用的 reported 65.4 比，且训练翻倍后的 GSR\* 反而降到 70.3）。真机部分每路线 30 trial，GSR 的 50%/40% 实为 15/30 与 12/30 且 6 个任务中 3 个两种条件全 0%，Native baseline 6 任务两条件全 0%——分母侧崩塌使该对比信息量有限。

附带的 **ParaVLA**（0.33B，冻结 T5 + 共享 DINOv2-Large，二者只在 flow-matching action expert 内各走独立 attention 通路汇合）正好补上 [[Papers/2607-TurboVLA|TurboVLA]] 缺的那个数据点：**原生解耦架构确实把 canonical/paraphrase 落差压到 1 个百分点**（92.0 / 91.0），同架构内把 T5 换成 SmolVLM decoder 则 canonical 仍有 85.0 而 paraphrase 塌到 41.0——解耦本身不够，语义源必须是纯文本编码器。但两篇也共同暴露同一天花板：TurboVLA 的 task-ID 消融只掉 2.3pp，ParaVLA 放大视觉主干后不再出现 VLM 式 scaling（作者自陈）。合起来看，去 LLM 的解耦架构在**任务集合封闭**时既够用又稳定，其是否还有语义泛化能力，两篇都没测。

**优势**：Zero-shot/few-shot task generalization；可理解自然语言指令；利用 web knowledge（如 "how to use a tool"）。  
**局限**：推理开销大；对 fine-grained manipulation（如 dexterous grasping）精度不足；real-time deployment 困难——但"大"是否为能力所必需，目前缺少能鉴别的评测（TurboVLA）。

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

**代表论文**：MultiWorld (2026)、HY-World 2.0 (2026)、Agentic World Model Survey (2026)、FlowWAM / ABot-M0.5 / RynnWorld-4D / GigaWorld-1 (2026)

**核心思路**：构建环境的 predictive model，通过 imagined rollouts 进行 planning，减少真实环境交互成本。

**2026-07/08 更新——机器人 world model 的角色分化**：world model 与 VLA 的结合方式已不再 unclear，而是分化为四种明确角色，外加一个新暴露的攻击面：

| 角色 | 代表工作 | 定位 |
|:-----|:---------|:-----|
| Policy（WAM） | [[Papers/2607-FlowWAM|FlowWAM]]、[[Papers/2607-ABotM05|ABot-M0.5]]、[[Papers/2607-RynnWorld4D|RynnWorld-4D]]、[[Papers/2607-STWAM|ST-WAM]] | world modeling 与 action generation 共享同一生成骨干，RoboTwin 2.0 上已超纯 VLA baseline；2026-08 起分化出"被预测的未来该用什么表示"的子问题 |
| Planner / 搜索基底 | [[Papers/2607-WorldActionPlanner|WAP]] | 规划在想象中完成，policy 降级为被调用的执行工具 |
| 数据引擎 | [[Papers/2607-RynnWorldTeleop|RynnWorld-Teleop]] | action-conditioned 实时视频生成替代真机采数（"数字遥操作"） |
| Policy Evaluator | [[Papers/2607-GigaWorld1|GigaWorld-1]] | 以 evaluator-world outcome agreement 为标准的低成本 policy 评估 surrogate |
| 攻击面 | [[Papers/2607-BadWAM|BadWAM]] | action 与 imagined future 可被视觉扰动解耦——"梦得合理、做得错误" |

**WAM 作为 policy**：
- **[[Papers/2607-FlowWAM|FlowWAM]]**：HSV 编码 optical flow 作 WAM 统一动作表示（video-native、稠密跨帧运动、可逆解码回机器人动作），同一模型双模式运行（policy / motion-conditioned 视频生成），RoboTwin 2.0 92.94%、真机 75.7% vs π₀.₅ 61.4%；ablation 表明关键不是 flow 本身而是"把 flow 映射进预训练视频先验的 RGB 空间"（HSV vs raw flow 差 17.5pt）。
- **[[Papers/2607-ABotM05|ABot-M0.5]]**：video → frame-level latent action → executable action 三级生成链，Dual-level MoT 拆分 mobility/manipulation 分支消除频率与动力学干扰，Dream Forcing 让 inverse dynamics 基于 self-dreamed video 学习以消 exposure bias；RoboTwin 2.0 94.1%、RoboCasa365 46.6%（Composite-Unseen 仅 7.9%——长程组合泛化远未解决）。
- **[[Papers/2607-RynnWorld4D|RynnWorld-4D]]**：投影式 4D（RGB+Depth+Flow 三分支 DiT + Joint Cross-Modal Attention）回避显式 3D 表示，Depth δ₁ 近乎翻倍 4DNeX，蒸馏出的 policy 6 个真机任务赢 5；但 RGB 观感反输纯 2D Wan-2.1，且 depth/flow 全为伪标注（Depth Anything 3 / DPFlow），几何指标是在与伪标对齐。
- **[[Papers/2607-STWAM|ST-WAM]]**：把"被预测的未来"从单一 VAE 像素空间扩为**双空间**——VAE future DiT（5B，源自 Wan2.2）+ DINO future DiT（1B）+ action DiT（1B）以 MoT 联合 flow matching 训练；另加 Current-Anchored Intent Retrieval，用 Qwen3-VL 的当前语义作 query 检索 4 帧 DINO 历史、压成 8 个 intent token 只喂动作专家。结构化 cross-branch mask 使 action token 从不读取未来流，因此两条未来分支在推理时可整体移除，延迟仅为 Fast-WAM 的 1.24×（756.17 ms vs 609.30 ms）。收益集中在鲁棒性而非 in-distribution：LIBERO 98.7 / RoboTwin 2.0 92.77 与既有 WAM 同量级，而 zero-shot LIBERO-Plus 72.8 vs Fast-WAM 51.5（camera +39.0、sensor noise +41.8），真机 nominal 79.3、shifted 61.5（Fast-WAM 25.8 / π₀ 32.8）、compound 48.0（15.3）。归因上有两处需要注意：**其消融显示新增的 DINO 未来分支单独使用反而更差**（DINO Future Only 在 LIBERO-Plus 只有 39.7，低于纯 VAE 的 Fast-WAM 51.5），且所测 shift 全为 appearance 级，而 DINO 类特征本身对这类扰动近似不变——增益有多少来自"预测未来"、多少来自"把 DINO 表征引进条件通路"，论文没有分离。笔记核查为 partial：其"joint V-L 编码使措辞/外观与任务语义纠缠"的机制断言标为 `unsupported`（全文无纠缠度量），本 survey 只引用其消融数字与负结果；Table 3 的 baseline 数字系引用他文而非重跑，全文无参数量统计。

**World model 作为数据引擎**：[[Papers/2607-RynnWorldTeleop|RynnWorld-Teleop]] 用 40+ FPS 的 action-conditioned world model 实现"数字遥操作"——操作者 hand-pose 流实时驱动机器人 egocentric 视频合成，合成数据训练的 π₀ 可零样本迁移真机，数据饥饿的精细任务增强 +20pts。实际边界：仍需 1,800 条真机 demo 启动、跨 embodiment 需 per-platform 微调，是窄任务分布内的数据放大器而非"替代真机"；且高质量（FVD 550 / 2.8 FPS）与实时（40 FPS / FVD 1226）来自两个不同模型。

**World model 作为 policy evaluator**：[[Papers/2607-GigaWorld1|GigaWorld-1]] 把 surrogate 评估的成功标准从视频观感改为 **evaluator-world agreement**（同一 policy 在 real 与 world model 中 outcome / ranking / failure profile 是否一致），WMBench 2,989 对 paired rollout + 324K challenge rollout 的受控研究给出设计结论：evaluator 质量取决于 long-horizon action fidelity、可迁移物理先验与空间对齐 control（channel-concat pose map 的 Trajectory Accuracy 0.353 远超 ControlNet 0.257 / cross-attention 0.162），而非短期视频指标。关键警示：video model 对 contact-sensitive failure 有 optimistic bias——这是 policy evaluator 最危险的误差类型，false-success rate 应成必报指标。

**World model 作为 planner**：[[Papers/2607-WorldActionPlanner|WAP]] 把执行主体反转——VLM agent 提出子目标，action-conditioned world model 在想象中评估，policy 只作为被调用的工具执行已选中的方案，构成 propose → optimize → search 闭环。使这一反转在视频骨干上可行的是 pose-image conditioning：候选动作先经正向运动学渲染为骨架图像、再由 VAE 编码送入 Wan-T2V-1.3B（4 视角 2×2 拼图，21 帧 @7FPS 历史 → 20 帧 @20FPS 未来），从而绕开低维动作向量与视频生成骨干之间的接口失配。结果上，compositional LIBERO-Long 四设定 72/68/78/70，对照 π0.5 的 4/0/0/0 与 cosmos-policy 全 0；新布局六设定 88/86/90/66/84/78，baseline 多为 0；zero-shot Robosuite 80/76 对纯 VLM planner 的 58/22。消融阶梯从 56/28/46/32 起，依次加入 global optimization、local search、policy rollout imagination 逐级抬升；且 1 次想象即胜过带 ground-truth reward 的 BoN-8（60 vs 42）——在这一设定下想象比重采样更省。

这些数字的可比性有明确边界：WAP 使用 URDF、相机标定与硬编码 GRASP/RELEASE 原语，"72 vs 0" 因此是"带特权信息的模块化系统 vs 端到端 policy"的对比，而非 world model 单独的贡献；全文只有 Table 9 隔离了 world model 本身的增益。世界建模指标（+11.4% ID / +16.8% 泛化）是 PSNR 与 LPIPS 相对提升再取平均，论文自己的 limitation (g) 已承认该构造可疑。全部实验在仿真中完成，无真机；无 imagination horizon 扫描与误差累积测量；50 次 trial 无误差棒。

**表示层与物理保真度**：上述角色都默认 world model "懂物理"，[[Papers/2607-PhiZero|Phi-Zero]] 直接测这个假设并给出分离性证据。其做法是 reason-then-render 而非直接生成像素——先用自监督学到的离散"物理语言"推理（FSQ levels (8,5,5,5,5,5)、25K 词表，4 秒视频压成 256 个符号，Qwen3-VL-4B 作 reasoner），再由 Wan2.2-5B LoRA 扩散解码器渲染。生成端指标领先：Physics-IQ Verified IQ-Score 41.2 > Cosmos3-Super 39.5 > Wan2.2-14B 32.2，PhyGround Physics 3.01，WorldModelBench Total 8.19。判别端却没有同步：IntPhys2 Overall 56.34 而 Hard split 仅 52.38（随机基线 50，V-JEPA 57.42），LikePhys 上刚体 29.14 最好而流体 53.15 倒数第三，WS-IoU 27.6 落后。"生成得像"与"判得对"在同一模型上分离，对把 world model 当 planner 或 evaluator 的两条路线都是直接风险——它们消费的正是判别能力。方法层的关键缺口是没有同数据同算力、仅移除中间表示的对照，21.2→41.2 的增益混淆了表示、数据与训练三个变量；该表示本身是有损压缩（256 符号重建 PSNR 28.9，Wan2.2 VAE 用 44,800 token 达 37.7）；其 "zero-shot" 迁移仍需按源域微调 tokenizer，4 秒固定视界靠滑窗自回归外推，且无代码发布。

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
**局限**：Model accuracy 限制 planning horizon；多 Agent 交互建模复杂；WAM 推理开销大且普遍回避报告（RynnWorld-4D 前向 890ms / 9Hz，FlowWAM 无 latency 数字）；action 与 imagination 的同步性可被攻击（[[Papers/2607-BadWAM|BadWAM]]，见路线 6）；evaluator 用途下对 contact-sensitive failure 有 optimistic bias（GigaWorld-1）；planner 用途下增益尚未与特权信息（URDF / 相机标定 / 硬编码抓放原语）分离（[[Papers/2607-WorldActionPlanner|WAP]]）；生成保真与物理判别可在同一模型上背离（[[Papers/2607-PhiZero|Phi-Zero]] 于 Physics-IQ 领先却在 IntPhys2 Hard 接近随机）；**新增预测通道的边际收益归因不清**——[[Papers/2607-STWAM|ST-WAM]]（DINO 未来）与 [[Papers/2607-N0TWAM|N0-TWAM]]（触觉未来）的消融同向显示新加的那条预测通路不是主要收益来源（见路线 9）。~~与 VLA 结合的方式仍 unclear~~——2026 年已由 WAM 路线给出可行答案，RoboTwin 2.0 上 WAM（ABot-M0.5 94.1 / FlowWAM 92.9）超过纯 VLA baseline。

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
| Inference-time | World-Action Drift（[[Papers/2607-BadWAM|BadWAM]]，2026 新增） | 有界视觉扰动使 WAM 的 action 与 imagined future 解耦，black-box query 攻击把 LIBERO 成功率 96.5%→43.1%；imagination-preserving 变体保持"梦境正常"实现隐蔽攻击，简单 augmentation-consistency detector 召回仅 13-21% |

**Defense Mechanisms**：
- Training-time：data validation, adversarial training, certified robustness
- Runtime：safety-aware policy, monitoring & intervention, unified safety architecture

**Runtime 执行鲁棒性**（2026 新证据）：[[Papers/2607-RobustExecAgenticRL|RobustExec]] 在冻结 policy（OpenVLA/π₀/π₀.₅/DP 均适用）之上用 PPO 训练轻量高层 MLP，依据 proprioception-only 执行质量指标（短期卡滞/抖动 + 对成功参考轨迹的长期漂移）在 {Execute, Retry, Repair, Reset} 中调度、回滚到历史 nominal state；LIBERO 扰动设定平均最高 +39.2。边界：纯仿真、缺规则阈值 baseline，且回滚只恢复机器人不恢复世界状态——不可逆失效（物体打翻、液体）仍无解。[[Papers/2607-BadWAM|BadWAM]] 的对应启示：WAM 的 runtime monitor 应检查"当前 action 能否实现 predicted future"（action-imagination consistency），而非给 future video 打 realism 分。

**Open Problems**（Survey 提出）：
- Certified robustness for VLA
- Physically realizable defense
- Safety-aware training procedure
- Unified runtime safety architecture
- Standardized evaluation protocol
- Action-imagination consistency verification（BadWAM 补充：WAM 的安全属性应包含 action 与预测未来的同步性，可执行 inverse-dynamics check 是候选方向）

---

### 7. Human Video / 数据引擎路线（2026-07 新增）

**代表论文**：EgoSteer (2026)、Do as I Do (2026)、Xiaomi-Robotics-1 (2026)、HiFi-UMI (2026)、RynnWorld-Teleop (2026)

**核心思路**：绕开真机遥操作的吞吐瓶颈（每条 demo 绑死一台真机 + 操作者工时），从 human egocentric 视频、手持采集设备或生成式 world model 中规模化获取训练数据。

| 工作 | 数据源 | 规模 | 关键机制 | 核心证据 |
|:-----|:-------|:-----|:---------|:---------|
| [[Papers/2607-EgoSteer|EgoSteer]] | in-the-wild egocentric 视频 | 9.6K 小时 / 1.04B 帧 | EgoSmith 4 阶段 curation + 统一 R^48 相机系相对 state-action 表示 + DAgger | 40 任务 75% SR；预训练量 0→9.6K 小时 log-linear 提升 |
| [[Papers/2606-DoAsIDo|Do as I Do]] | 普通单目 RGB human 视频 | 500 条 human-verified 灵巧轨迹 | 4D hand-object 重建（SAM 3/3D + MoGe）+ physics-aware sampling retargeting | retarget 成功率 25%→71%（warmup 主增益）；22-DoF 双手真机部署 10 类任务 |
| [[Papers/2607-XiaomiRobotics1|Xiaomi-Robotics-1]] | UMI 手持夹爪 | 100K+ 小时 | state-transition 自动标注（两周完成）+ cross-embodiment delta pose 归一 | unseen 真机 26%→75%（data scaling）；data > model size |
| [[Papers/2607-HiFiUMI|HiFi-UMI]] | 高保真 UMI 手持双夹爪 | full 20K+ 小时 / released 2K 小时、482.1K+ episodes | pose、双夹爪相对位姿、<40 μs 同步与 six-view FoV 的 hardware-software co-design | 三 backbone 的 UMI−teleop aggregate gap 为 −2.5 / +3.1 / −0.6pp；但 3,200 vs ~300 trajectories，非等样本比较 |
| [[Papers/2607-RynnWorldTeleop|RynnWorld-Teleop]] | world model 合成 | 40+ FPS 实时生成 | 数字遥操作（hand-pose 驱动视频生成） | π₀ 零样本迁移真机；数据饥饿任务 +20pts |

**一致发现**：

1. **Curation 比堆量重要**：EgoSteer noisy-data ablation（44%→33%）、Do as I Do 的在线视频仅 ~5% 直接可用、Xiaomi 的自动标注 infrastructure——三方独立指向数据质量管线是承重结构，不是把任意 human video 当可执行示范。
2. **表示一致性是 human→robot 迁移的关键杠杆**：EgoSteer 统一相机系相对 R^48、Xiaomi 统一 end-effector delta pose、FlowWAM 用 flow 表示吃 EgoDex 无动作数据——共同点是回避 embodiment-specific 动作空间，使预训练与后训练共享同一表示。
3. **Data scaling 的边际收益目前大于 model scaling**（Xiaomi-Robotics-1 的受控 scaling curve，见路线 1）。
4. **Fidelity 可以改变 UMI 的训练阶段角色**：HiFi-UMI 的四任务、三 backbone、960 次 real-robot rollout 表明，联合提高 pose、relative geometry、synchronization 与 FoV 后，robot-free data 可以承担 target-task post-training；但现有比较没有匹配 sample count 或 scene exposure，且四个 fidelity factors 未做逐项降级，因此只能归因于整套系统，不能推出 equal-sample efficiency 或单因素因果贡献。

**局限**：human 视频缺触觉与力信息，contact-rich 任务受限；机器人 DoF 上限使高灵巧 human 知识不能完全迁移；生成数据路线仍需真机种子数据启动；轨迹验证成本（human verification）尚未入账。HiFi-UMI 的 “zero-robot post-training” 仅表示 target-task 阶段不用 real-robot teleoperation；base checkpoint 仍可能含 robot data，最终证据也来自 real-robot evaluation。

---

### 8. Memory 机制路线（2026-07 新增）

**代表论文**：LaMem-VLA (2026)、ABot-AgentOS (2026)

**核心思路**：主流 VLA 是 Markovian（只看当前观测），长时程任务需要记忆。2026 年出现从 policy 内部 latent memory 到 agent 系统层显式 graph memory 的完整谱系，两端各有一个代表实例：

- **Implicit 端——[[Papers/2607-LaMemVLA|LaMem-VLA]]**：把历史重构成 context-native latent memory token（short-term 视觉 vault + long-term 动作语义 vault，top-K 检索后压成定长 token）直接编织进 VLA embedding 序列参与 self-attention，而非 policy-side 外部条件；latent-native vs policy-side 对照 +2pt（73.9 vs 71.9，SimplerEnv-Bridge），LIBERO 均值 97.6%。边界：纯仿真无真机、离散 top-K 检索不可微、超参甜点窄。
- **Explicit 端——[[Papers/2607-ABotAgentOS|ABot-AgentOS]]**：agent 系统层 typed graph memory（video/对话/session 统一 schema + hybrid retrieval + 子图扩展）+ verification-aware harness + split-wise gated self-evolution；EgoLifeQA 上 1 帧 65.4 击败 50 帧 EGAgent-Gemini2.5Pro（57.5），证明 graph memory 对长时程 egocentric 经验的结构化压缩有效。边界：full context 放得下时 memory pipeline 全面落后（Mem-Gallery 88.6 vs 92.6）；保守 gate 下 self-evolution 几乎不长肉（8 splits 仅 1 asset 存活）——安全 vs 演化效率 trade-off 的诚实数据点；零真机实验。

**Open question**：memory 的价值边界（context 多长时 memory 开始占优的 crossover point）未被系统刻画；memory 应活在 embedding 空间还是符号空间，取决于消费者是 action head（LaMem-VLA）还是 planner（ABot-AgentOS），两端之间的中间形态尚无工作。

---

### 9. 触觉进入 VLA：预测式 vs 反应式（2026-08 新增）

**代表论文**：N0-VTLA (2026)、N0-TWAM (2026)

主流 VLA 的输入只有 RGB + 语言 + 本体感受，contact-rich 任务缺少接触信息——路线 7 已把"human 视频无触觉与力"列为数据引擎路线的固有短板。NeoteAI / Fudan TEAI 的两篇姊妹作在同一批数据与基准上给出把触觉写进模型的两种方式，且**结论彼此相左**，这是本轮最值得记的信号。

- **[[Papers/2607-N0VTLA|N0-VTLA]]——触觉作为预测目标**。冻结 DINOv2 编码 contact-difference 图像（每视角 10 token = 1 class + 3×3 pooled）；predictor 把当前触觉与 VL prefix 蒸馏成 latent `z`，用对称 InfoNCE 加上对未来 H=50 步触觉差分的粗重建来监督；`z` 只条件化 flow-matching 动作专家，从不进入 VL prefix，当前接触 token 也从不直达动作专家。底座为 PaliGemma + 由公开 π0.5 权重初始化的动作专家；三阶段上机，其中 **Stage 2 在动作专家的 attention 里屏蔽 VL prefix，使动作损失只能经 `z` 下降**——这是把"触觉必须被用上"写进训练结构而非损失权重的做法。另配 ALTER：从轨迹事件与时长校准的相对进度中标注 advantage，成对进度模型**只看多相机 RGB 与 prompt**，二值 Advantage token 拼进 prompt、训练时以 p=0.3 丢弃、部署时恒为正。结果：NeoReal 9 任务 47.2 vs π0.5 29.4，仿真 20 任务 63.8 vs 44.0，UniVTAC 83.1 vs InternVLA-A1 67.1；表征探针给出该路线最硬的一块证据——`z` 在 ~32 候选池中 top-1 达 92.3（chance 3.2），当前触觉对照仅 57，扰动触觉使 `z` 移动约 0.9 而扰动 RGB+prompt ≤0.2。
- **[[Papers/2607-N0TWAM|N0-TWAM]]——触觉作为世界模型的一路专家**。video / tactile / action 三专家 MoT 共享一层 self-attention，frame-id 因果掩码构成 predict-then-act 级联；触觉走**双通路**：predicted（残差 latent 前瞻，仅预训练）与 observed（NeoForce 力空间编码器，零初始化 cross-attention，仅后训练）。7.16B 可训练参数（video 5.00B / action 1.13B / tactile 1.03B）。结果：UniVTAC 84.5 vs InternVLA-A1 67.1，NeoSim 49.4 vs π0.5 45.8，真机 46.3 vs 30.0（LingBot-VA 21.9 / FastWAM 14.4）。

**争议点（不作共识记录）**：N0-VTLA 的核心押注是"把触觉做成可预测的 latent 前瞻"，而 N0-TWAM 的消融给出反向证据——**去掉反应式的 observed 通路比去掉预测式的 predicted 通路损失更大**，两个基准上都是（UniVTAC 70.5 vs 71.8、NeoSim 29.6 vs 41.1，完整模型 84.5 / 49.4）。更值得注意的是其最大单因素并非任何触觉设计：预训练数据降到 20% 使 UniVTAC 掉到 65.4（−19.1）。逐任务还有反向翻转（NeoSim Cup Handover 完整模型 14 而 w/o predicted 65；Cup Stack 12 而 w/o observed 38；UniVTAC Pull-out Key 79 而两个消融变体均为 86），说明总分掩盖了任务级的相互抵消。N0-VTLA 侧也有同向的自证：ALTER 在 3 个长程任务上把 π0.5-SFT 的 40/20/5 抬到 90/75/60，而 N0-VTLA-SFT 只到 50/35/20——**offline RL 是主导项、触觉预训练是二阶项**，且两者叠加后 SFT 阶段的 10/15/15 差距收窄到 5/5/15。因此"触觉表征预训练带来多少增益"这个问题，库内现有证据尚不足以定论，两篇的记法应为争议而非共识。

**证据独立性的硬边界**：两篇出自同一团队，NeoData / NeoSim / NeoReal / NeoForce 均来自公司网页报告，一手出处不可独立核查；八个基准里只有 UniVTAC 是第三方公开基准，而 N0-VTLA 在其上虽总分领先却输掉 8 个任务中的 3 个（Insert HDMI 25，对照 [[Papers/2602-XiaomiRobotics0|Xiaomi-Robotics-0]] 的 69），且 UniVTAC 的仿真 episode 进入了训练、与被评测任务的重叠未声明。N0-TWAM 真机为每任务 20 trials（论文自陈 binomial SE 可达 ±11%）；N0-VTLA 全文无 trial 数、seed 与方差，无同 checkpoint 的触觉关断对照，也未说明 π0.5 baseline 是否同样吃了 NeoData 预训练。库内暂无独立复现。

---

## Datasets & Benchmarks

| Dataset/Benchmark | 类型 | 规模 | 评估指标 | SOTA | 特点 |
|:------------------|:-----|:-----|:---------|:-----|:-----|
| **Open X-Embodiment** | Training Data | 22 robots, 1M+ episodes, 527 skills | - | RT-X models | 最大规模 cross-embodiment dataset |
| **DROID** | Training Data | 多场景 manipulation demo | - | - | 多机构协作收集 |
| **HiFi-UMI-2K** | Training Data | 2K 小时 / 482.1K+ episodes / 110+ scenes | - | [[Papers/2607-HiFiUMI|HiFi-UMI]] | CC BY 4.0；synchronized multi-view + calibrated bimanual trajectories，完整 processed corpus 为 20K+ 小时 |
| **CALVIN** | Benchmark | Long-horizon manipulation | Success Rate, Sequence Length | - | Language-conditioned，要求 compositional reasoning |
| **LIBERO** | Benchmark | Long-horizon manipulation | Success Rate, SPL | - | 多 task suite；语言鉴别力存疑——把指令换成 task-ID embedding 仅掉 2.3pp（[[Papers/2607-TurboVLA\|TurboVLA]]），且 LIBERO-Goal 的 10 个任务共享同一视觉场景，句子编码器与 10 路任务码难以区分（[[Papers/2608-GSRParaVLA\|GSR]]） |
| **LIBERO-Para** | Benchmark | 4,092 改写 episode（870 Act / 259 Obj / 2,963 Comp） | Full Para SR / PRIDE | Full Para 76.0（Xiaomi-Robotics-0）；PRIDE 70.4（[[Papers/2608-GSRParaVLA\|GSR]]-π0.5） | 只改指令措辞，物理任务/初始状态/成功判据不变；主流 VLA 掉 19-68pp。测的是 paraphrastic invariance，不含新物体/新动作/新组合 |
| **LIBERO-Plus** | Benchmark | LIBERO 的扰动泛化集（相机、光照、传感器噪声等） | Zero-shot Success Rate | [[Papers/2607-STWAM\|ST-WAM]] 72.8（对照 Fast-WAM 51.5，baseline 系引用未重跑） | 扰动均为 appearance 级，DINO 类特征对其近似不变——用它论证"预测未来带来鲁棒性"存在归因风险 |
| **UniVTAC** | Benchmark | 视触觉操作，8 任务 | Success Rate | [[Papers/2607-N0TWAM\|N0-TWAM]] 84.5 / [[Papers/2607-N0VTLA\|N0-VTLA]] 83.1（InternVLA-A1 67.1） | 触觉路线唯一的第三方公开基准；两篇总分领先但均有任务级输给基线（N0-VTLA 输 3/8） |
| **Physics-IQ / IntPhys2** | Benchmark | 视频物理一致性（生成 / 判别） | IQ-Score / Accuracy | [[Papers/2607-PhiZero|Phi-Zero]] 41.2（Physics-IQ） | 两类指标可给出相反排序：Phi-Zero 生成端第一，IntPhys2 Hard 52.38 却近随机基线 50 |
| **RLBench** | Benchmark | 100+ manipulation tasks | Success Rate | Diffusion Policy, ACT | Simulation benchmark，多样化 task |
| **RoboTwin 2.0** | Benchmark | 50 manipulation tasks | Success Rate | ABot-M0.5 94.1%（WAM 类 92-94% 已入饱和区） | Randomized settings，challenging |
| **RoboCasa365** | Benchmark | 365 任务（Atomic + Composite） | Success Rate | Xiaomi-Robotics-1 57.4% | Composite-Unseen 极难（SOTA 仅 32.1%），长程组合泛化探针 |
| **WMBench** | Benchmark | 2,989 对 paired real/world-model rollouts | WMES / evaluator agreement | GigaWorld-1 | 首个以 evaluator-world outcome agreement 为标准的 world model 评测 |
| **REAL-Bench** | Benchmark | 241 任务 / 4 族（含用户交互） | Success Rate | REAL 8B（SUL 56.9%） | Privilege-free（无 oracle 感知 API）+ simulated user 模糊指令 |
| **DexGraspNet** | Benchmark | Dexterous grasping | Grasp Success Rate | - | 多物体 dexterous hand benchmark |
| **Habitat** | Benchmark | Navigation | SPL, Success Rate | - | Embodied navigation simulation |
| **AI2-THOR** | Benchmark | Navigation + Manipulation | Task Success | - | Household environment simulation |

**Benchmark 演进趋势**：
- 从 single-step evaluation（grasp success）到 long-horizon evaluation（CALVIN, LIBERO）
- 从 single-robot to cross-embodiment（Open X-Embodiment）
- 从 simulation-only to sim-to-real validation（RoboTwin 2.0 randomized settings）
- 从 task-specific to language-conditioned generalization（CALVIN）
- 从特权感知接口到 privilege-free 可部署接口（REAL-Bench：无 oracle object list / teleport 工具）
- 评测对象从 policy 扩展到 world model evaluator 本身（WMBench：paired real/WM rollout 的 outcome agreement）
- 反向趋势：主力 suite 的鉴别力在下降。LIBERO 上语言指令可被 task-ID 近乎无损替代、RoboTwin 2.0 已进 92-94% 饱和区，"更强"的边际证据越来越薄
- 但鉴别力未必是消失，可能只是被 canonical 模板掩盖：LIBERO-Para 只改写措辞就把同一批模型从 72-98% 打回 4-77%（[[Papers/2608-GSRParaVLA|GSR]]），说明"换一套指令表述"这一最低成本的扰动即可重新拉开差距。饱和区的正确读法是评测协议过窄，而非任务已被解决

---

## Key Takeaways

1. **VLA Foundation Model 已成为主流范式**：RT-2 证明 web-scale VLM knowledge 可直接迁移到 robot policy，RT-X 建立 cross-embodiment training 的 positive transfer 现象，OpenVLA 开源生态使研究门槛大幅降低。

2. **Diffusion Policy 是 action generation 的有效方法**：Multimodal action distribution modeling 解决 BC 的 mode collapse，在 manipulation tasks 上广泛验证。SeedPolicy 的 SEGA module 解决 long-horizon observation 压缩瓶颈。

3. **VLM→VLA 迁移需要 data alignment 与表征保持**：EmbodiedMidtrain 发现 VLA data 与 VLM distribution 存在显著 gap；[[Papers/2606-Act2Answer|Act2Answer]] 进一步测得 robotics 微调使语义类知识掉 20-40 分（知识中层仍可解码、动作头读不出——问题在读出通路），[[Papers/2607-AnchorAlignVLA|Anchor-Align]] 证明 frozen VLM 锚定可低成本修复且不牺牲动作性能——防遗忘机制（co-training / anchoring）应成 VLA 训练默认件。

4. **World Model 已分化出四种角色并成为 competitive policy 范式**：policy（WAM：[[Papers/2607-ABotM05|ABot-M0.5]] / [[Papers/2607-FlowWAM|FlowWAM]] 在 RoboTwin 2.0 超纯 VLA）、planner（[[Papers/2607-WorldActionPlanner|WAP]] 把 policy 降级为工具，compositional LIBERO-Long 72 对 π0.5 的 4）、数据引擎（[[Papers/2607-RynnWorldTeleop|RynnWorld-Teleop]] 数字遥操作）、policy evaluator（[[Papers/2607-GigaWorld1|GigaWorld-1]] evaluator-world agreement）；代价是推理开销与新攻击面（[[Papers/2607-BadWAM|BadWAM]] 的 action-imagination 解耦）同步出现。planner 与 evaluator 两个角色消费的是判别能力，而 [[Papers/2607-PhiZero|Phi-Zero]] 表明生成保真度不蕴含判别正确性——这两条路线不能靠视频质量指标验收。

5. **RL 正从 imitation 走向 true policy optimization**：LongNav-R1 的 multi-turn RL + horizon-adaptive advantage 证明 trajectory-level optimization 比单步 SFT 更适合 long-horizon tasks；[[Papers/2607-REAL|REAL]] 补充了 BC 过拟合的直接观察（SFT 第 2 epoch 在开放词表 split 倒退、RL 修复并超越）。

6. **安全与可靠性开始被系统性关注**：VLA Safety Survey 定义了新问题域——VLA 的不可逆物理后果、多模态攻击面、实时约束带来区别于 LLM safety 和 classical robotic safety 的 unique challenges；[[Papers/2607-BadWAM|BadWAM]] 补充 WAM 特有的 world-action drift 威胁，[[Papers/2607-RobustExecAgenticRL|RobustExec]] 给出 runtime 执行监控 + 回滚恢复的廉价方案（proprioception-only 指标，无需 VLM）。

7. **数据瓶颈的答案正收敛到 human/手持视频 + 强 curation + 可部署 fidelity**：[[Papers/2607-EgoSteer|EgoSteer]]（9.6K 小时 egocentric，scaling log-linear）与 [[Papers/2607-XiaomiRobotics1|Xiaomi-Robotics-1]]（100K+ 小时 UMI，data scale 边际收益大于 model size）给出 data scaling 直接证据；[[Papers/2607-HiFiUMI|HiFi-UMI]] 则表明 3 mm pose、原生双夹爪相对位姿、硬件同步与 wide FoV 的联合 fidelity 足以让 UMI 承担 target-task post-training。跨工作共同点不是“任意视频都可用”，而是 curation、表示一致性与 capture fidelity 共同构成数据引擎。

8. **实时性与能力未必互斥，但现有 benchmark 对二者都在丧失鉴别力**：[[Papers/2607-TurboVLA|TurboVLA]] 移除 LLM 后以 0.2B / 32 Hz 在 LIBERO 拿到 97.7%，同时自证 LIBERO 的语言条件近似闭集分类（task-ID 替换仅 −2.3pp）；[[Papers/2607-PhiZero|Phi-Zero]] 在生成类物理 benchmark 领先而在 IntPhys2 Hard 接近随机。两处的共同含义是，饱和或低鉴别力的评测让"更快"与"更懂"都难以证伪；效率与物理理解的下一步进展，前置条件是先造出能区分它们的评测，而不是继续在现有 suite 上刷分。LIBERO-Para 给出了造这类评测的一个廉价样板——不动物理任务、只改指令措辞，就把同一批模型从 72-98% 打回 4-77%（[[Papers/2608-GSRParaVLA|GSR]]）；但它自身也划出边界：LIBERO-Goal 的 10 个任务共享同一视觉场景，它测出的是 paraphrastic invariance，仍不足以把"语言条件化"与"任务索引"分开。

9. **VLA 的语言鲁棒性首先是架构问题，不是数据问题**：[[Papers/2608-GSRParaVLA|GSR]] 用因果干预把失效位置定位到动作策略对 joint vision-language 编码漂移的敏感性——任务语义在语言主干里保留完好（Retrieval@1 0.941 / 0.675 / 0.516，chance 0.1），只替换最后一个融合 block 的语言特征即消除 96.8% 的动作差异；把指令语义改由一条不看图像的冻结文本编码器承担，只用 canonical demonstration 就把 SmolVLA 的 Full Para 从 4.47 提到 49.12。竞争解释（容量、多一个语言编码器）被三个落在同一数值上的对照排除。适用范围须同时记住：全部仿真证据来自 10 任务共享场景的闭集设定，且无统计区间与多 seed，因此这条结论支持的是"扩数据不是唯一解"，不是"语义泛化已被解决"。

10. **触觉进入 VLA 已成事实，但"预测式触觉"的收益归属未定**：[[Papers/2607-N0VTLA|N0-VTLA]] 把触觉做成预测目标并给出可信的表征探针（latent `z` 在 32 候选池 top-1 92.3，chance 3.2），[[Papers/2607-N0TWAM|N0-TWAM]] 的消融却显示去掉**反应式** observed 通路比去掉**预测式** predicted 通路损失更大，且最大单因素是预训练数据量而非任何触觉设计；N0-VTLA 自己的 ALTER 结果也显示 offline RL 是主导项、触觉预训练是二阶项。两篇同团队、共享私有数据与基准，本 survey 记为争议而非共识。与路线 3 的 [[Papers/2607-STWAM|ST-WAM]]（新增 DINO 未来分支，单独使用反而低于纯 VAE 基线）合看，2026-08 的两组证据指向同一个方法论问题：**给模型加一条"预测更多模态/更多表示的未来"的通路时，增益常常不来自"预测"这一半**。

---

## Open Problems

### 核心技术挑战

1. **Sim-to-Real Gap 的系统性解决**：尽管 domain randomization、adversarial training 有进展，但真实世界的 lighting variation、material diversity、dynamic obstacle 等仍难以完全模拟。需要更 robust 的 sim-to-real transfer framework。

2. **Dexterous Manipulation 的精度瓶颈**：VLA 在 coarse manipulation（pick-and-place）表现良好，但 fine-grained dexterous manipulation（如 tool use、precision assembly）仍不如 specialized methods。

3. **Long-Horizon Credit Assignment**：Multi-step tasks 中 reward 稀疏，LongNav-R1 的 horizon-adaptive advantage 是有价值的尝试，但 generalizable solution 仍需更多验证。

4. **Real-Time Inference Constraint**：VLA 模型推理开销大，diffusion policy 需要 multiple denoising steps。如何在保持 policy quality 的同时满足 sub-second latency 是 deployment bottleneck。WAM 路线加剧此矛盾——每次出 action chunk 需跑 5B 级视频去噪（RynnWorld-4D 890ms 前向 / 9Hz），且多数 WAM 论文回避报告 latency（FlowWAM）。反向证据来自 [[Papers/2607-TurboVLA|TurboVLA]]：完全不含 LLM 的 V+L→A 架构以 0.2B / 32 Hz 在 LIBERO 与 RoboTwin 2.0 保持竞争力，说明至少在闭集任务分布上 latency 与成功率不构成硬 trade-off。真正未解的是开放指令与 OOD 条件下这一 trade-off 是否重新出现——该文没有相应实验，问题从"能不能又快又准"变成"快的代价落在哪类泛化上"。

### 数据与评测挑战

5. **高质量 Robot Demonstration 的获取成本**：Teleoperation data 质量高但收集成本高；autonomous collection 需要成熟 policy。Human 视频与手持采集路线（EgoSteer / Do as I Do / Xiaomi UMI / HiFi-UMI）已给出部分答案，但瓶颈从“有没有数据”转移到 curation、fidelity specification 与验证：在线视频仅 ~5% 直接可用于灵巧学习；HiFi-UMI 的 parity 依赖约十倍 task-specific trajectory 数且没有逐因素 ablation。下一步需要固定 sample count 与 scene coverage，正交降级 pose、synchronization、relative-pose 与 FoV，才可形成可迁移的 deployment specification。

6. **Cross-Embodiment Morphology Gap**：RT-X 展示 positive transfer，但不同 robot 的 kinematics、dynamics、action space 差异仍限制 transfer efficiency。如何设计更 universal action representation？候选正在收敛：相机系相对 state-action（EgoSteer）、end-effector delta pose（Xiaomi-Robotics-1）、optical flow（FlowWAM）、frame-level latent action（ABot-M0.5）——共同点是 embodiment-agnostic 的中间表示，但无定论。

7. **真实环境评测的覆盖率与鉴别力**：Benchmark 多在 simulation 或特定 lab setup，缺少真实 home/factory/outdoor 环境的 systematic evaluation。Safety-critical scenario testing 几乎空白。World model surrogate 评估（GigaWorld-1 / WMBench）提供低成本替代路径，但对 contact-sensitive failure 的 optimistic bias 未解——false-success 会系统性放行危险 checkpoint，false-success rate 应成必报指标。覆盖率之外还有鉴别力：LIBERO 上把语言指令换成 task-ID embedding 只掉 2.3pp（[[Papers/2607-TurboVLA|TurboVLA]]），意味着它主要测闭集任务执行而非语言理解，"语言条件化"类方法的收益在其上无法被验证；物理侧同构——生成类指标（Physics-IQ）与判别类指标（IntPhys2 Hard）在 [[Papers/2607-PhiZero|Phi-Zero]] 上给出相反排序。需要的是带 held-out 指令改写、未见物体与显式判别项的评测设计。其中"指令改写"这一项已被 LIBERO-Para 做出来（4,092 条改写 episode，物理任务与成功判据不变，同一批模型从 72-98% 回落到 4-77%），证明这类协议成本极低且立刻恢复鉴别力；仍缺的是未见物体、新动作、新组合与显式判别项——而 LIBERO-Goal 的 10 个任务共享同一视觉场景这一事实，使它连"语言条件化 vs 任务索引"都还分不开。

### 安全与部署挑战

8. **VLA Certified Robustness**：Adversarial attack 防护需要理论上可证明的 robustness bound，但 VLA 的 multi-modal input space 和 continuous action space 使 certified defense 困难。BadWAM 新增 WAM 特有攻击面：action 与 imagination 的同步性本身需要防护，"检查生成未来是否合理"不构成安全保障。

9. **不可逆操作的风险控制**：Physical operation 一旦执行难以撤销。如何设计 safety-aware policy、runtime monitor、emergency intervention mechanism？RobustExec 的 {Execute, Retry, Repair, Reset} 调度是一次尝试，但回滚只恢复机器人不恢复世界状态，不可逆失效（液体、易碎物、物体位移）仍无解。

10. **开放场景的 Language Understanding**：用户指令可能模糊、不一致或超出 robot capability。如何 robustly parse and ground natural language in physical context？目前的位置比预想的靠后——连"同义改写"这一最弱的语言变化都尚未解决（主流 VLA 在 LIBERO-Para 上掉 19-68pp），而 [[Papers/2608-GSRParaVLA|GSR]] 的诊断表明瓶颈不在语言理解本身，而在动作策略与 joint V-L 编码之间的信息路由。这意味着"模糊指令""个性化偏好"这类更高阶目标的前置条件，是先把措辞不变性做成架构性质而非数据性质。

### 归因与评测基础设施挑战（2026-08 新增）

11. **新增预测通道的增益来自哪一半**：WAM 路线正在往"预测更多东西"的方向扩（[[Papers/2607-STWAM|ST-WAM]] 的 DINO 未来、[[Papers/2607-N0TWAM|N0-TWAM]] 的触觉未来），但两篇的消融同向显示新增的预测通路不是主要收益来源——ST-WAM 的 DINO Future Only 在 LIBERO-Plus 只有 39.7、低于纯 VAE 基线的 51.5；N0-TWAM 去掉反应式 observed 通路的损失大于去掉预测式 predicted 通路。需要的对照是**同 backbone、同算力、逐预测目标移除**，并配以非 appearance 级的扰动集——否则"多预测一种未来 → 动作更好"这条推论无法与"多引入一种表征/多一路条件输入"区分。

12. **触觉路线的评测基础设施几乎不存在**：现有触觉 VLA 证据的八个基准中只有 UniVTAC 是第三方公开基准，其余数据集、仿真器、真机套件与力觉编码器均出自同一公司的网页报告，一手出处不可独立核查；真机普遍 20 trials/task 量级（binomial SE 可达 ±11%），且缺同 checkpoint 的触觉关断对照。在这套条件下，"触觉带来多少增益"这个问题在库内无法被证伪。

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
- **[[Papers/2607-BRAID|BRAID]]**（2026）：把 GRPO 范式扩展到交错「文-图-文」推理——两层 MDP 使同一 trajectory advantage 同时驱动文本 token（GRPO）与图像去噪路径（DiffusionNFT），7B UMM 在 7 个 spatial/perception benchmark 平均 +5.73、反超 GPT-4o；无具身执行环节，但为"生成中间图像辅助空间思考"（mental imagery）提供了 RL 可训的首个证据，与本专题 Open Problem 5（reasoning × world model）交汇。注意其收益偏向"找细节/放大 ROI"（CV-Bench 3D 反而 −1.24），且 reward 依赖 GPT-5.2 judge。

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
- **[[Papers/2607-REAL|REAL]]**（ECCV 2026）：去 oracle 感知（仅 receptacle 先验 + RGB/SoM 多级探索 toolchain）+ simulated user 主动澄清意图，Qwen3-VL-8B 经 SFT+GSPO 训练；MCP 统一工具接口使 sim 策略零改动换 backend 迁移 Ark LIFT2 真机（60 episodes 78.3%、零崩溃）。把"特权感知不可部署"与"完整指令假设"两个被主流 benchmark 系统性回避的 deployment gap 作为一等公民；但泛化证据薄（单 held-out 场景），真机任务分布比仿真 benchmark 简单。

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
- **[[Papers/2607-ABotM05|ABot-M0.5]]**（2026）：统一 mobility-manipulation 的 World Action Model（详见总览路线 3）——frame-level latent action + Dual-level MoT 分支处理底盘与机械臂的频率/动力学差异，对本专题"action space mismatch"核心难点给出 WAM 侧答案；RoboCasa365 46.6%，但 Composite-Unseen 仅 7.9%。
- 相邻进展：[[Papers/2509-NavFoM|NavFoM]]（12.7M 样本 navigation foundation model，zero-shot 覆盖 VLN/ObjectNav/tracking/driving，multi-task 协同 tracking +49.4%）与 table-top VLA 的融合是统一系统的自然方向；[[Papers/2607-ABotN1|ABot-N1]]（2026）在导航侧给出统一接口的最新实例——slow-fast 双系统以 affordance/target 双 pixel goal 为通用接口，把 point-goal / instruction-following / object-goal / POI / person-following 五任务收进单一 checkpoint（R2R-CE SR 70.9 SOTA，multi-task ≥ specialist 证明 pixel-goal 接口下正向迁移），但全文无组件 ablation、自建 benchmark 未声明 train/test 隔离。

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
- [[Papers/2607-XiaomiRobotics1]] - 100K+ 小时 UMI data scaling
- [[Papers/2405-VLASurvey]] - VLA Survey（TNNLS，三层 taxonomy 领域索引）
- [[Papers/2607-AnchorAlignVLA]] - 表征锚定 + 语言-动作对齐
- [[Papers/2607-LoRAVLA]] - LoRA finetuning 实证（r=32 recipe）
- [[Papers/2606-Act2Answer]] - VLA 知识保留测量协议
- [[Papers/2607-TurboVLA]] - 去 LLM 的轻量 V+L→A 架构（0.2B / 32 Hz）
- [[Papers/2608-GSRParaVLA]] - 指令改写鲁棒性的因果诊断 + 语义源解耦（GSR / ParaVLA）

### Diffusion Policy Papers

- **Diffusion Policy**: "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion" (Chi et al., arXiv 2303.04367)
- [[Papers/2603-SeedPolicy- Horizon Scaling via Self-Evolving Diffusion Policy for Robot Manipulation]] - SeedPolicy with SEGA
- **ACT**: "Action Chunking with transformers" (2023)

### World Model Papers

- [[Papers/2604-MultiWorld]] - Multi-agent multi-view world model
- [[Papers/2604-HYWorld2]] - 3D world generation + planning
- [[Papers/2604-AgenticWorldModel]] - World Model Survey (Levels × Laws)
- [[Papers/2607-FlowWAM]] - Optical flow 统一动作表示的 WAM
- [[Papers/2607-ABotM05]] - 统一 mobility-manipulation WAM（Dream Forcing）
- [[Papers/2607-RynnWorld4D]] - 投影式 4D（RGB-D-Flow）world model
- [[Papers/2607-RynnWorldTeleop]] - 数字遥操作数据引擎（40+ FPS）
- [[Papers/2607-GigaWorld1]] - World model as policy evaluator（WMBench）
- [[Papers/2607-BadWAM]] - World-Action Drift 攻击
- [[Papers/2607-WorldActionPlanner]] - World model as planner（propose → optimize → search，pose-image conditioning）
- [[Papers/2607-PhiZero]] - 离散物理语言 + reason-then-render 世界模型（生成保真 vs 物理判别的分离）
- [[Papers/2607-STWAM]] - 双空间未来（VAE + DINO）+ 当前锚定意图检索的 WAM

### 触觉 / 多模态感知 Papers

- [[Papers/2607-N0VTLA]] - 触觉作为预测目标的 latent token + ALTER offline RL
- [[Papers/2607-N0TWAM]] - 三专家 MoT 触觉世界模型（predicted / observed 双通路）

### Data Engine Papers

- [[Papers/2607-EgoSteer]] - 9.6K 小时 egocentric 视频 full-stack 系统
- [[Papers/2606-DoAsIDo]] - 单目 human 视频 → 灵巧轨迹（physics-aware retargeting）
- [[Papers/2607-HiFiUMI]] - 高保真 UMI 从 pre-training 推进到 target-task post-training

### Memory & Agent 系统层 Papers

- [[Papers/2607-LaMemVLA]] - VLA 内 latent memory token
- [[Papers/2607-ABotAgentOS]] - Robotic Agent OS + graph memory + gated self-evolution

### RL Papers

- [[Papers/2600-LongnavR1HorizonAdaptive]] - Multi-turn RL for VLA navigation
- [[Papers/2500-ArpoEndEndPolicy]] - ARPO for GUI/Embodied policy optimization
- [[Papers/2607-RobustExecAgenticRL]] - 执行监控 + 回滚恢复的高层 RL 调度
- [[Papers/2607-REAL]] - Privilege-free 具身 agent 的 SFT+GSPO 训练
- [[Papers/2607-BRAID]] - 交错文-图推理的统一 RL（GRPO + DiffusionNFT）

### Navigation Papers

- [[Papers/2607-ABotN1]] - 五任务统一 VLN foundation model（pixel goal 接口）

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

### 2026-08-04 survey-refresh 增量并入 4 篇、跳过 1 篇
- **来源**：[[Papers/2607-STWAM|ST-WAM]]（full-text / partial）、[[Papers/2607-N0VTLA|N0-VTLA]]（full-text / source-checked）、[[Papers/2607-N0TWAM|N0-TWAM]]（full-text / source-checked）、[[Papers/2608-GSRParaVLA|GSR / ParaVLA]]（full-text / partial）。
- **结构变化**：新增路线 9「触觉进入 VLA：预测式 vs 反应式」，并把两篇姊妹作的相反消融结论记为**争议**而非共识；路线 1 新增「语言鲁棒性：从数据覆盖问题重述为信息路由问题」分支，并用 ParaVLA 补上 TurboVLA 缺失的改写泛化数据点；路线 3 policy 角色新增 ST-WAM 与"被预测的未来该用什么表示"子问题，局限段增补"新增预测通道归因不清"；Overview 新增第 5 条范式演进；Benchmarks 表新增 LIBERO-Para / LIBERO-Plus / UniVTAC 三行并改写 LIBERO 行注记与演进趋势；Key Takeaway 8 增补、新增 9-10；Open Problem 7 与 10 增补，新增「归因与评测基础设施挑战」小节（11-12）。papers_analyzed 107→111。未刷新配图（本 survey 无既有配图，且本轮为新增分支而非分类框架重构）。
- **跳过 1 篇**：[[Papers/2607-SafeKeep|SafeKeep]] —— LLM agent 的 tool specification（JSON schema）安全研究，tags 为 `[LLM, instruction-following]`，无任何具身内容，属 keyword 误报；与路线 6 的 VLA 物理安全不同域，硬并入会污染 threat taxonomy。处理方式与 2026-07-21 跳过 ProceduralMemoryAFTER / ContextFailsFirst 一致。
- **证据边界**：ST-WAM 为 partial 核查，其"joint V-L 编码使措辞/外观与任务语义纠缠"的机制断言标 `unsupported`（全文无纠缠度量），只引用消融数字与负结果；其 LIBERO-Plus baseline 系引用他文未重跑，扰动全为 appearance 级。N0-VTLA / N0-TWAM 出自同一团队，NeoData / NeoSim / NeoReal / NeoForce 均来自公司网页报告不可独立核查，仅 UniVTAC 为第三方公开基准；N0-TWAM 真机 20 trials/task（自陈 SE 达 ±11%），N0-VTLA 无 trial 数、seed 与方差，无同 checkpoint 触觉关断对照。GSR 为 partial 核查，其 C32（无 GSR 绑错语义的 failure-case 分析）标 `unsupported`，正文未采用；全部仿真证据来自 LIBERO-Goal 10 任务共享场景，附录声明的 McNemar 与 bootstrap CI 全文未给出任何数值，单 seed，故 π0.5 的 +1.99 点不可读作显著。以上均为库内单篇证据，无独立复现。
- **status**: success

### 2026-08-02 survey-refresh 增量并入 3 篇
- **来源**：[[Papers/2607-TurboVLA|TurboVLA]]（full-text / partial）、[[Papers/2607-PhiZero|Phi-Zero]]（full-text / source-checked）、[[Papers/2607-WorldActionPlanner|WAP]]（full-text / source-checked）。
- **结构变化**：路线 3 的角色分化从三种扩为四种，新增 planner / 搜索基底（WAP）与"表示层与物理保真度"讨论（Phi-Zero）；路线 1 新增"效率端的反向证据"分支（TurboVLA）；Key Takeaway 4 改写并新增 Takeaway 8（评测鉴别力）；Open Problem 4 增补反向证据、Open Problem 7 由"覆盖率"扩为"覆盖率与鉴别力"；Benchmarks 表 LIBERO 行补语言鉴别力注记并新增 Physics-IQ / IntPhys2 行。
- **证据边界**：TurboVLA 无任何 OOD / 指令改写评测，其结论只在闭集任务分布内成立，且 LIBERO 语言鉴别力问题正来自它自己的 ablation；WAP 全仿真、使用 URDF 与相机标定等特权信息且硬编码抓放原语，"72 vs 0" 不可读作 world model 单独贡献（仅 Table 9 隔离）；Phi-Zero 缺同数据同算力、仅移除中间表示的对照，21.2→41.2 混淆表示/数据/训练三变量。
- **status**: success

### 2026-07-30 survey-refresh 增量并入 1 篇
- **来源**：[[Papers/2607-HiFiUMI|HiFi-UMI]]（full-text，11/11 evidence-ledger claims source-verified）。
- **结构变化**：路线 7 新增高保真 UMI 分支与 HiFi-UMI-2K dataset；将既有“human/手持视频 + curation”结论细化为“curation + 表示一致性 + capture fidelity”，并把 UMI 的适用边界从 pre-training 推进到 target-task post-training。
- **证据边界**：三 backbone aggregate parity 来自 3,200 UMI vs ~300 teleoperation trajectories，非 sample-matched；四项 fidelity 因素联合实现但未做逐项 controlled degradation。“zero-robot post-training”不等于 base model 历史无 robot data，也不等于无需 real-robot evaluation。
- **status**: success

### 2026-07-21 survey-refresh 增量并入 19 篇
- **来源**: 2026-06/07 消化的 backlog 23 篇，相关性检查后并入 19 篇：world model 角色分化 6 篇（FlowWAM / ABot-M0.5 / RynnWorld-4D / RynnWorld-Teleop / GigaWorld-1 / BadWAM）、VLA foundation & finetuning 5 篇（Xiaomi-Robotics-1 / Anchor-Align / LoRA-VLA / Act2Answer / VLA Survey）、数据引擎 2 篇（EgoSteer / Do as I Do）、memory 2 篇（LaMem-VLA / ABot-AgentOS）、RL/agent 3 篇（RobustExec / REAL / BRAID）、导航 1 篇（ABot-N1）。
- **结构变化**: 新增路线 7（Human Video / 数据引擎）与路线 8（Memory 机制）；路线 3 重构为"world model 三角色分化"（policy / 数据引擎 / evaluator）并撤销"与 VLA 结合仍 unclear"的旧结论；路线 1 增加 data scaling 与"表征侵蚀-修复"证据链；路线 6 威胁表新增 World-Action Drift；Key Takeaways 3/4/5/6 更新、新增 7；Datasets 表新增 RoboCasa365 / WMBench / REAL-Bench，RoboTwin 2.0 SOTA 更新为 ABot-M0.5 94.1%。
- **跳过 4 篇**: AmbiBench、PIRA-Bench（纯 mobile GUI agent benchmark）；ProceduralMemoryAFTER、ContextFailsFirst（纯 LLM agent 基建）。
- **status**: success

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
