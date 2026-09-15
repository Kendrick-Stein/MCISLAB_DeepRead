---
title: Embodied AI Survey
tags: [survey, VLA, manipulation, navigation, embodied-ai, robotics, embodied-reasoning, mobile-manipulation]
date_updated: "2026-09-11"
year_range: 2023-2026
papers_analyzed: 129
keywords: [embodied ai, robot learning, manipulation, embodied reasoning, spatial reasoning, mobile manipulation, language-conditioned, instruction following, 3d scene, scene graph, slam, spatial memory, 3d reconstruction, real-to-sim, sim-to-real]
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

6. **归因方式本身成为研究对象（2026-08）**：当"多喂一路输入 / 多预测一种未来"成为通行加法，增益归属开始被单独测量。[[Papers/2608-VLAProprioception|VLAProprioception]] 用 slot-matched 对照把"时序内容"与"多出来的条件容量"分开，[[Papers/2608-WorldExam|WorldExam]] 用"只给触发、把该发生的反应留空"的构造把"按指令执行"与"推断后果"分开，并在 20 个视频世界模型上显示视觉质量与其余能力层解耦。两者对象不同，做的却是同一件事——把被总分掩盖的混淆变量拆成可测量的对照（路线 1、3，Open Problem 11）。

7. **world model 从推理期部件退回训练期信号（2026-08）**：WAM 路线最大的部署阻力是每出一个 action chunk 就要跑一次视频去噪。[[Papers/2608-WorldTokens|World Tokens]]、[[Papers/2608-JEPAWAM|JEPA-WAM]] 与 [[Papers/2608-MobileWAM|MobileWAM]] 走同一条替代路线——world modeling 的梯度只在训练期塑造 policy 消费的表征，未来分支在部署时整体移除，推理开销退回到不含未来分支的水平（61.85 ms/chunk 在 π0.5 的 1.1× 以内；85 ms 对 ABot-M0 的 125 ms；938 ms 对同类 WAM 的 4950/8126 ms）。三者的消融同时给出一个更硬的读数：收益取决于监督如何接进主干（是否排他路由、目标是否保留空间对应、从哪些层取信号、承载递归的模块多宽），接口设计错了就是负收益（路线 3，Open Problem 11）。

8. **接口成为独立于模型能力的竞争维度（2026-08）**：同一批能力可以挂在不同接口上，而接口选择正在产生比模型规模更大的性能差。动作侧，[[Papers/2608-GalaxeaG05|Galaxea G0.5]] 用跨本体 RVQ 把 27 维统一动作空间离散成与语言共享词表的 token、[[Papers/2608-Hydra0|Hydra-0]] 把动作写成图像平面上的稀疏点轨迹、[[Papers/2608-DreamXPhi|DreamX-Phi]] 按注意力头分组注入每臂 SE(3) 相对变换，与既有的 optical flow（FlowWAM）、3D point flow（PointWorld）构成五种互不兼容的取法。语义侧，指令可以走冻结文本编码器（GSR）、只读工具链注入（In-Context VLA）或检索来的示范前缀（[[Papers/2608-StellaVLA|StellaVLA]]），而 G0.5 反向主张连推理带动作都收进同一条自回归流。闭环治理侧，[[Papers/2608-Zetta|Zetta]] 与 [[Papers/2608-HyMeS|HyMeS]] 把 VLA 权重整体冻结、把可靠性逻辑挪到 harness 的代码空间（路线 6、8）。这些取法之间基本没有交叉实验（路线 3、Open Problem 6）。

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
| **[[Papers/2608-GalaxeaG05|Galaxea G0.5]]** | 2026 | 单一自回归流同时产出 CoT 与离散动作码，取消独立动作专家 | 跨本体 RVQ（27 维统一动作空间）+ 原生 CoT 标注 |

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

**同一失效的第二种定位：视觉混淆压倒语义，而非语义进不来动作端**。[[Papers/2608-CofactVLA|CofactVLA]]（2026）针对同一批现象——VLA 看见什么抓什么、无视指令——却把病因写成另一张因果图：图像经一个 latent visual confounder 打开 backdoor path `I⇢C→A`，绕过语义意图直接决定动作。据此的干预全在推理与特征路径上做减法，不改数据也不加外部模块：额外跑一条把语言 mask 掉的 counterfactual 分支，动作层把 flow-matching 的 factual velocity 中与该分支共线的分量投影掉再放大残差（OPG，γ=2），特征层把两分支协方差差的正特征空间从第 15、16 层的 KV 特征里减掉（CCR，β=0.15）。以 π0.5 为底座微调 6K step 后，LIBERO 四 suite 平均 98.5%、零样本 LIBERO-Plus total 69.1%、AgileX PiPer 真机四任务（各约 100 条示教、100 次 trial）标准环境 90.8% 对 π0.5 的 71.0%、作者自设 OOD 环境 75.8% 对 23.5%。

两种定位目前不能并列为已确立结论，因为证据等级不同。GSR 一侧有直接测量（行为层探针显示任务语义在语言主干里保留完好，因果干预只换语言特征即消掉 96.8% 的动作差异）；CofactVLA 的 backdoor path 是设定而非测得——Theorem 1 完全依赖 Assumption 2（contrastive eigengap），而全文没有特征谱、eigengap 或任何经验检验，CCR 单独的贡献也只有 97.0→97.5。分轴结果与其主张相左：LIBERO-Plus 上唯一直接测语言扰动的那一列 CofactVLA 71.8，落后 OpenVLA-OFT_m 的 81.0 达 9.2pp，69.1 的 total 由 Robot（49.7）与 Layout（70.2）撑起，这两轴与"语言因果性"关系最远。评测预算也撑不住断言精度：标准 suite 每 suite 10 episode、LIBERO-Plus 每任务 1 episode，全文无 seed 与误差棒，98.5 对 X-VLA 98.1 的 +0.4pp 不构成排序证据；Table 2 里缺它自己的底座 π0.5，头条的 +15.5pp 中混着 π0→π0.5 的底座升级；而唯一有 100 trial 支撑的真机 OOD 恰恰没有任何组件消融，"增益来自反事实去混淆"这一归因未被隔离。可带走的是一处结构而非数值：真机 OOD 下 π0.5 是崩塌式失败（逐任务 0 / 25 / 29 / 40），CofactVLA 落在 67–83 的窄带内，方差收窄的形状比 +52.3pp 的均值差更像"移除了一个会整体失效的依赖"。要在两种定位之间做判决，最低成本的实验是把 GSR 那套行为层 Retrieval@1 探针搬到真机 OOD 场景上跑一遍，双方都没做。

**证据的获取与使用被拆开：注入而非生成**。前两条分支处理指令怎么进模型，[[Papers/2608-InContextVLA|In-Context VLA]]（方法名 VLA-Talker，2026）处理的是推理该不该由 policy 自己说出来。它把生成式 CoT 混在一起的两件事分开——获取证据外包给只读感知工具链（GroundingDino 开放词表定位、DepthAnything 相对深度、由 proprioception 经相机内外参解析投影得到的 gripper 像素位置、Qwen2.5-VL-7B fallback），使用证据留给 policy 学。结构化 evidence tuple 以 `<spatial>` 标签注入 prompt，只在关键帧注入，loss 只作用在 action token 上，指令与证据 token 全部 mask，再用 GRPO 做轨迹级对齐。

承重证据是证据完全相同、只改"生成 vs 注入"与"监督掩码"的三行对照（LIBERO 四 suite 平均，同一 OpenVLA-OFT backbone，3 seed）：生成并监督文本 81.5%、延迟 4.6×；注入但仍对证据计 loss 89.7%；注入且只监督 action 97.4%。第二行把监督掩码单独隔离出 7.7 分，与 Gen-CoT 的差异经双尾 Welch t 检验 p<0.01。配套两条对照同样 backbone-matched：把工具链换成让模型自猜证据掉到 84.3，低于完全不注入的 backbone 90.4——起作用的是证据的内容而非"有上下文"这个形式，且**不可靠的证据比没有证据更糟**；三方法从同一初始化重训时，25 demo/task 的注入版拿到 92.8%，超过 50 demo 的纯 BC（90.4%）。延迟上注入版 78 ms / 12.8 Hz，生成式 CoT 因每步多出约 256 个 rationale token 掉到 359 ms / 2.8 Hz。真机 AgiBot G1 八个桌面子任务（每任务 20 trial，backbone 换成 JoyAI-RA-0.1）上，同一批证据的 +CoT 臂几乎不涨（单任务 41.9→41.9、多任务 28.1→29.4），注入臂到 58.1 / 45.0——这条跨 backbone 的方向一致性比仿真 SOTA 表更有说服力。

三处边界须一起记。"生成式 CoT 有害"这一断言压在作者自建的 Gen-CoT 基线上，而它在每个数据预算上都低于纯 BC（seen 分布 87.6 对 90.4）；一个连 BC 都跑不过的 CoT 实现更可能是没调好，要立住这条需要拿已发表的 CoT-VLA 权重在同 backbone 同数据上重训后再比。跨方法的 SOTA 对照全不 matched，LIBERO 上 97.4 对 VLA-Thinker 97.0 落在噪声内，且该笔记记录了一处未核的口径疑点（其 backbone 行 90.4 低于库内记录的 OpenVLA-OFT 单视角配置约 5 分，标 `not-checkable`，本文不据此下结论）。"语言 token 数量压倒 action token、梯度被叙述主导"被写成机制解释，但全文没有测过梯度分配，也没报语言/动作 token 比例——目前最接近的间接证据只是那 7.7 分。

**同一模板的第三种用法：语言只在训练期存在**。In-Context VLA 把推理外包给工具链，[[Papers/2608-StellaVLA|StellaVLA]]（2026）把它外包给检索——测试时从示范库取回最近邻的一条专家轨迹，由现成 VLM 加一个确定性 verbalizer 把它写成结构化前缀（task plan、sub-goal 关键帧描述、语言化的 3D 运动），全程无人工标注，前缀拼进 Qwen3-VL 的上下文。训练用双头：MLP 动作专家走 L1，自回归的空间-语言专家走交叉熵、权重 λ=0.3；推理时语言分支整支剥离，只跑一次前向，示范前缀的 KV 可缓存。结果为 VLA-Arena overall 0.63（π0.5 0.44）、LIBERO 平均 98.8%、LIBERO-Plus 零样本 85.1%（StarVLA-OFT 75.0，最大增益在 camera viewpoint 一轴 +23.5）。

承重的是两组消融而非榜单。示范依赖性三段对照给出 98.8 → 去掉示范 62.4 → 换成错任务示范 44.9，既证明增益确实来自前缀条件化而非参数记忆，也直接写出部署风险——检索错比不检索更糟。示范模态对照则指出起作用的是什么：text-only 98.8/84.4 与 image+text 98.8/85.1 几乎持平，image-only 掉到 92.9/75.7，语言化的运动结构而非示范像素承载了绝大部分有效信息。延迟一侧与 In-Context VLA 的读数同向且更极端：无示范 64 ms、带缓存的 image+text 示范 91 ms，而若在推理时真的联合自回归解码语言则是 3177 ms，约 36 倍。

边界有三处。"test-time adaptation" 在主评测里并未被真正检验——检索池就是训练示范池，"新任务只插一条新示范、不动权重" 这个最有想象力的用法没有对应实验，真机 OOD-L2（未见任务）的进度分只有 1.9/4。no-demo 的 62.4% 远低于压根不用示范训练的 StarVLA-OFT（LIBERO 96.6%），说明任务知识被大量搬进了上下文通路，检索基础设施因此成为部署单点；该数字是"训练带示范、测试去掉"的失配条件，不能读作无示范范式的上界。此外自动标注的分段与 sub-goal 描述没有人工质检或噪声敏感性分析，而纯语言检索在同指令不同布局时无法区分场景——与 wrong-demo 的 44.9% 合看，这是主要风险面。abstract 把 LingBot-VLA 0.22 与 π0.5 并列为 "strong prior models"，而它是表中 overall 最低的一档（OpenVLA-OFT 0.39、Evo-Depth 0.41 均更高），对 π0.5 的 +0.19 才是实质差距。原文一致性已核查，库内暂无独立复现。

**架构层的正面交锋：一条自回归流 vs 编码器加动作专家**。上面几条分支都默认了同一个底层结构——预训练 VLM 做编码、另挂一个 flow-matching 动作专家——分歧只在语义与证据从哪个口子进来。[[Papers/2608-GalaxeaG05|Galaxea G0.5]]（2026）否定的正是这个结构本身：单个 transformer decoder、语言与动作共享同一词表，一次 next-token 交叉熵同时生成 CoT 与离散动作码。使这件事在跨本体数据上可行的有三个部件——把 27 维统一动作空间压成离散码的跨本体 RVQ tokenizer（附带 active-part 预测，用来指明该本体哪些自由度参与）、原生的 CoT 流（Subtask / BBox / Trace / ActionHint 四类）、以及 ViT 内部按时空因子分解注意力实现的视觉记忆。

论据里最硬的一块不是榜单而是同条件微调：在同数据、同算力、同控制栈下，真机微调 76.7% 对 π0.5 的 53.3% 与 GR00T-N1.7 的 24.4%，这个差距因此可归到架构而非训练预算。外部信号来自 BEHAVIOR Challenge——1 个 epoch 拿到 0.3136，超过用了四个 checkpoint 的挑战赛冠军方案。其余为 DROID 零样本 82.5%、LIBERO 98.9%、RoboTwin 2.0 93.3%、SimplerEnv-Bridge 87.3%。作者把"自回归接口的红利是结构性的"拆成三条：CoT 在长程任务上有推理期增益、GRPO 因为 likelihood 参数化现成可用而不必重构、零样本语言跟随有更强先验。

这些红利的适用区间比主张窄。Conclusion 里"零样本语言跟随超过 post-trained π0.5"与自家 Fig 10 相矛盾——π0.5 在 50H post-training 后 LF 为 68.8%，高于 G0.5 零样本的 65.6%，该说法只在 1H/10H 规模上成立（笔记判为 contradicted，本 survey 不采用其原表述）。仿真侧的领先落在饱和区（LIBERO 对次优 0.2pp、RoboTwin 1.1pp），abstract 在 Bridge 上只引 π0.5 的 57.1% 作对比而实际次优是 79.2%。CoT 的增益集中在长程 stage-conditioned 场景，单阶段任务上约 1.6pp、接近噪声。低对比度与半透明表面上 60% 对 π0.5 的 90%，论文归因于预训练数据分布而未做机制分析（离散动作码是否在精细视觉伺服上弱于连续 head，属推测）。只有 2B 单一规模，无 scaling 分析，逐 token 解码的实时代价未在笔记核查范围内。可带走的是这条路线被摆上了台面并配了同条件对照，而不是它已经赢了——真机、BEHAVIOR 与 DROID 三个 regime 是有区分度的，仿真两项不是。

**Proprioceptive state 的接口：一条被惯例决定的设计轴被单独测量**。几乎所有近期 VLA 都吃 proprioceptive state，但接法互不兼容——[[Papers/2504-Pi05|π0.5]] 把 state 量化成文本 token 拼进 prompt，OpenVLA-OFT 连续投影进语言序列，GR00T-N1 直喂 action head——而这些差异从未与 backbone、预训练、数据、评测协议分离过。[[Papers/2608-VLAProprioception|VLAProprioception]]（2026）把它拆成表示形式、历史长度、注入位置三条轴，在 π0.5 单一基座下实现 5 种 state interface（state prompt / VLM prefix / action prefix / state expert / feature modulation），共享数据管线、动作表示与训练预算，在 RoboCasa365 的 45 个 atomic 任务（按控制语义事前分三族、每族单训 category expert、每任务 50 次闭环 rollout）与 20 个 composite 任务上对比。

| 设计轴 | 结论 | 关键数字 |
|:--|:--|:--|
| 接口选择 | 当前帧 state 收益小，且不存在任务无关的最优接口 | no-state 54.6%，五个接口全部落在 55.7–57.7 的两点带内，只有 state prompt 的 +3.1 其配对 task-bootstrap 95% 区间 [0.2, 6.1] 排除 0；族内排名直接翻转——A 族（重定位/取放）sp 68.7、B 族（articulated object）vp 68.8、C 族（小工作空间高精度）se 42.8，且 vp 是 C 族唯一低于 baseline 的接口（38.3，−1.2） |
| 历史长度 | 短历史有界有益，长 raw 历史有害（K 从 1 扫到 96，非单调） | composite 上 action prefix K=1→8 为 28.2→39.0，同样的历史走 VLM prefix 为 34.4→33.8；C 族在长历史下退化最重，经 VLM prefix 注入时尤甚 |
| 注入位置 | 偏好随时间预算翻转：单帧走 VLM 侧，短历史走 action 侧 | 单帧时 composite vp 34.4 > ap 28.2；K=8 时 ap 在 atomic 与 composite 都是最佳入口（59.6 / 39.0），而它在单帧时接近最弱 |

方法上最值得复用的是那个 slot-matched 对照：固定图像、语言、state slot 数、专家动作与初始噪声，只把有序历史换成当前帧的重复副本，得到 30.8 对 39.0（+8.2，配对区间排除 0）——短历史的收益因此不能用"多了几个 conditioning slot"解释。这套构造对本 survey 记录的另一类归因难题（路线 3、9 的"新增预测通道的增益来自哪一半"）是直接可用的模板，见 Open Problem 11。

三条边界须随数字一起传播。其一，+10.8 的起点偏低——论文自陈 composite 上单帧 action prefix 与 no-state 基线几乎持平，跨设计的诚实比较是 ap8（39.0）对最好的单帧设计 vp1（34.4），即 +4.6；换成 joint-angle state 重跑后，K=8 时两条路线收敛到 36.2 vs 35.8、落在配对 bootstrap 噪声带内，路由规则的强度本身依赖 state 坐标系。其二，16 维 state 中有 7 维是 world frame 下的 mobile-base 位姿，属全局定位而非本体感受，而 sp 增益最大的恰是大范围重定位的 A 族——"proprioception 有用"与"把全局定位离散化塞进语言空间有用"这两个机制未被去除 base pose 的消融分开（作者点出该边界但未做该实验）。其三，唯一拿到区间支持的 sp 也是边际算力最贵的接口（约 66 个 prompt token，训练侧 +1114 GFLOPs/sample，而 state expert 只要 2.6），且因构造上只支持当前帧被排除在全部历史实验之外；加上多数对比单 seed、无真机、state 纯 kinematic（无 force / tactile），这套设计规则应读作 RoboCasa365 + π0.5 组合下的先验。原文一致性已核查，库内暂无独立复现。

**优势**：Zero-shot/few-shot task generalization；可理解自然语言指令；利用 web knowledge（如 "how to use a tool"）。  
**局限**：推理开销大；对 fine-grained manipulation（如 dexterous grasping）精度不足；real-time deployment 困难——但"大"是否为能力所必需，目前缺少能鉴别的评测（TurboVLA）。"VLM 编码器 + 独立动作专家"这一惯例本身也不再是唯一选项：[[Papers/2608-GalaxeaG05|G0.5]] 在同数据同算力的真机微调上以单条自回归流取得 76.7% 对 π0.5 的 53.3%，但其优势只在真机、BEHAVIOR 与 DROID 三个 regime 上有区分度，仿真两项落在饱和区。

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

**2026-07/08 更新——机器人 world model 的角色分化**：world model 与 VLA 的结合方式已不再 unclear，而是分化为五种明确角色，外加一个新暴露的攻击面：

| 角色 | 代表工作 | 定位 |
|:-----|:---------|:-----|
| Policy（WAM） | [[Papers/2607-FlowWAM|FlowWAM]]、[[Papers/2607-ABotM05|ABot-M0.5]]、[[Papers/2607-RynnWorld4D|RynnWorld-4D]]、[[Papers/2607-STWAM|ST-WAM]]、[[Papers/2608-MobileWAM|MobileWAM]] | world modeling 与 action generation 共享同一生成骨干，RoboTwin 2.0 上已超纯 VLA baseline；2026-08 起分化出"被预测的未来该用什么表示"的子问题 |
| 训练期表征塑造（推理期删除） | [[Papers/2608-WorldTokens|World Tokens]]、[[Papers/2608-JEPAWAM|JEPA-WAM]]、[[Papers/2608-MobileWAM|MobileWAM]] | 预测性监督只经梯度改写 policy 消费的表征，未来分支在部署时整体移除，推理开销回到 VLA 量级 |
| Planner / 搜索基底 | [[Papers/2607-WorldActionPlanner|WAP]]、[[Papers/2606-PointWorld|PointWorld]]、[[Papers/2608-DALeWM|DA-LeWM]] | 规划在想象中完成；policy 或降级为被调用的执行工具（WAP），或整个缺席、由 MPC 直接在预测的动力学上求解（PointWorld）。该角色对表征的要求也随之与其他角色分岔——planner 消费的是 latent 之间的距离，因此 latent 是否编码了任务量（信息充分性）与该距离能否把候选按真实进展排序（decision-metric alignment）是两条逻辑独立的性质（DA-LeWM） |
| 数据引擎 | [[Papers/2607-RynnWorldTeleop|RynnWorld-Teleop]] | action-conditioned 实时视频生成替代真机采数（"数字遥操作"） |
| Policy Evaluator | [[Papers/2607-GigaWorld1|GigaWorld-1]] | 以 evaluator-world outcome agreement 为标准的低成本 policy 评估 surrogate |
| 攻击面 | [[Papers/2607-BadWAM|BadWAM]] | action 与 imagined future 可被视觉扰动解耦——"梦得合理、做得错误" |

**WAM 作为 policy**：
- **[[Papers/2607-FlowWAM|FlowWAM]]**：HSV 编码 optical flow 作 WAM 统一动作表示（video-native、稠密跨帧运动、可逆解码回机器人动作），同一模型双模式运行（policy / motion-conditioned 视频生成），RoboTwin 2.0 92.94%、真机 75.7% vs π₀.₅ 61.4%；ablation 表明关键不是 flow 本身而是"把 flow 映射进预训练视频先验的 RGB 空间"（HSV vs raw flow 差 17.5pt）。
- **[[Papers/2607-ABotM05|ABot-M0.5]]**：video → frame-level latent action → executable action 三级生成链，Dual-level MoT 拆分 mobility/manipulation 分支消除频率与动力学干扰，Dream Forcing 让 inverse dynamics 基于 self-dreamed video 学习以消 exposure bias；RoboTwin 2.0 94.1%、RoboCasa365 46.6%（Composite-Unseen 仅 7.9%——长程组合泛化远未解决）。
- **[[Papers/2607-RynnWorld4D|RynnWorld-4D]]**：投影式 4D（RGB+Depth+Flow 三分支 DiT + Joint Cross-Modal Attention）回避显式 3D 表示，Depth δ₁ 近乎翻倍 4DNeX，蒸馏出的 policy 6 个真机任务赢 5；但 RGB 观感反输纯 2D Wan-2.1，且 depth/flow 全为伪标注（Depth Anything 3 / DPFlow），几何指标是在与伪标对齐。
- **[[Papers/2607-STWAM|ST-WAM]]**：把"被预测的未来"从单一 VAE 像素空间扩为**双空间**——VAE future DiT（5B，源自 Wan2.2）+ DINO future DiT（1B）+ action DiT（1B）以 MoT 联合 flow matching 训练；另加 Current-Anchored Intent Retrieval，用 Qwen3-VL 的当前语义作 query 检索 4 帧 DINO 历史、压成 8 个 intent token 只喂动作专家。结构化 cross-branch mask 使 action token 从不读取未来流，因此两条未来分支在推理时可整体移除，延迟仅为 Fast-WAM 的 1.24×（756.17 ms vs 609.30 ms）。收益集中在鲁棒性而非 in-distribution：LIBERO 98.7 / RoboTwin 2.0 92.77 与既有 WAM 同量级，而 zero-shot LIBERO-Plus 72.8 vs Fast-WAM 51.5（camera +39.0、sensor noise +41.8），真机 nominal 79.3、shifted 61.5（Fast-WAM 25.8 / π₀ 32.8）、compound 48.0（15.3）。归因上有两处需要注意：**其消融显示新增的 DINO 未来分支单独使用反而更差**（DINO Future Only 在 LIBERO-Plus 只有 39.7，低于纯 VAE 的 Fast-WAM 51.5），且所测 shift 全为 appearance 级，而 DINO 类特征本身对这类扰动近似不变——增益有多少来自"预测未来"、多少来自"把 DINO 表征引进条件通路"，论文没有分离。笔记核查为 partial：其"joint V-L 编码使措辞/外观与任务语义纠缠"的机制断言标为 `unsupported`（全文无纠缠度量），本 survey 只引用其消融数字与负结果；Table 3 的 baseline 数字系引用他文而非重跑，全文无参数量统计。

- **[[Papers/2608-MobileWAM|MobileWAM]]**：把 WAM 配方从固定底座 tabletop 搬到 whole-body mobile manipulation。pretrained video DiT 与 action expert 做 layerwise joint attention，action expert 的每个 FFN 换成 shared / locomotion / manipulation 三专家软路由（Mobile MoE）；另加一条只在训练期存在的 Chain-of-Foresight——从 backbone 第 4/12/20/30 层取当前观测隐状态拼成初始 belief，深度专属 transformer 模块沿未来 latent 串行展开，belief 是相邻步之间唯一的通道。ManiSkill-HAB SetTable 七子任务平均 73.0%（对照的 AnchorVLA 64.0 只覆盖其中 6 项），真机 ARX Lift2 五任务 55/35/25/20/15% 对同数据微调 π0.5 的 35/25/10/10/0%；组件消融 WAM only 65.4 → +CoF 68.9 → +Mobile MoE 73.0，其中 CoF 使 Open Drawer 从 89.7 掉到 87.0。边界：真机未报 trial 数、评测场景在训练分布内而摘要写的是 strong generalization；全文无任何视频预测质量指标，用来解释 CoF 为何有效的是一张肉眼比对的定性图；Table 3–6 共用的参照点 58.2 在两张表里被分别标注为含 Mobile MoE 与不含，两种读法对 CoF 的归因完全不同，论文未澄清。

**训练期消费、推理期删除：world model 退回成一路梯度**。WAM 作为 policy 的部署阻力集中在一处——每出一个 action chunk 就要跑一次视频去噪。[[Papers/2607-STWAM|ST-WAM]] 已经给出过一个绕法：用不对称 cross-branch mask 保证 action token 从不读取未来流，于是两条未来 DiT 在推理时可整体移除。[[Papers/2608-WorldTokens|World Tokens]]、[[Papers/2608-JEPAWAM|JEPA-WAM]] 与 [[Papers/2608-MobileWAM|MobileWAM]] 把同一模板推到三种不同的接口上，共同点是 world modeling 的梯度只在训练期塑造 policy 消费的表征，未来分支在部署时不实例化：World Tokens 61.85 ms/chunk（π0.5 为 56.32，即 1.1× 以内，而 Cosmos Policy 610 / Fast-WAM 182 / DiT4DiT 136），JEPA-WAM 85 ms / 11.76 Hz（ABot-M0 为 125 ms），MobileWAM 938 ms（Motus 4950、LingBot-VA 8126）。

三者接的位置各不相同。World Tokens 用 Perceiver 式 World Adapter（L=12，K=256，d=2048）把 VLM 的视觉-语言隐状态压成 256 个 world token，并规定这 256 个 token 是 action expert 唯一能看到的 VL 上下文，视频损失以 5× 权重压在这条通道上（L = L_act + 5·L_vid），首帧用 Canny 边缘而非 RGB 作锚。JEPA-WAM 冻结 V-JEPA 2.1 作 latent 目标，让一个共享的 predictor 同时回归当前帧与未来帧的 latent，tubelet=2 使双帧联合编码仍保住 24×24 空间网格，λ_wm=0.5。MobileWAM 把未来沿时间串成 belief 链，只从 4 个稀疏跨深度的 tap 层取信号。

消融给出的读数比成功率更值得记：**收益取决于监督怎么接进主干，而不是"预测了未来"这件事本身**。World Tokens 把 world token 从排他上下文改成可旁路（VLM bypass），LIBERO-Long 从 97.0 掉到 94.1，低于完全不做 world modeling 的 95.0；首帧锚点从 Canny 换成 RGB 更掉到 91.5，即净损。JEPA-WAM 的目标构造同样敏感：joint current–future 79.2 > future-only 77.3 > 只对齐当前帧表征的 V-JEPA-only 77.0 > DINOv2+SigLIP 目标 73.2，而取 backbone 全部隐藏层的 73.1 低于只取 Lower-16 的 76.5。MobileWAM 三张表最直白：并行预测多个未来 52.3 而串行 belief 链 58.2，把递归模块从 transformer 换成 MLP 掉到 46.3——低于完全不加 foresight 的 50.2；tap 层从均匀 4 层改成全部 30 层，58.2 崩到 37.1；按动作维度硬拆专家 44.6–48.8 而软路由 58.2。

这与路线 9 已记的归因困难互补。[[Papers/2607-STWAM|ST-WAM]] 与 [[Papers/2607-N0TWAM|N0-TWAM]] 的消融说明新加的那条预测通路不是主要收益来源，上面三组则说明同一条通路的效果可以在净损与显著增益之间摆动，摆动幅度由排他性、目标是否保留空间对应、从哪些层取信号、承载递归的模块多宽决定。合起来的意思是：把"预测未来"当成一个可加模块来报告增益，在当前证据下不构成有效归因（见 Open Problem 11）。

绝对分数不支持更强的说法。World Tokens 的 LIBERO 平均 98.2 是在 2B、无 embodied 预训练下取得，但并非表内最好（Cosmos Policy 98.5、DiT4DiT 98.6）；SIMPLER 上 WidowX 71.5 / GoogleRobot 82.1 领先 Qwen-GR00T 与 StarVLA，真机 Galaxea R1 Pro 96 trials 76.0% 对 59.4%，但无代码与模型发布。JEPA-WAM 的 LIBERO-Plus 79.2 是"不含大规模 robot-policy 预训练"这一档里最好，接到 π0.5 上把 84.5 提到 86.3 才是全表最好（迁移时 action token 被禁止 attend future token，隔离干净）；短板同样清楚——逐列读 Table 2，Language 扰动一列只有 68.2，明显低于 ResVLA 88.5 与 RoVLA 92.9，平均分掩盖了这个 tradeoff（论文正文未讨论该列，其 task-shared 目标与语言无关是作者自陈的结构性局限）；RoboTwin 2.0 Random 上 π0.5 加与不加该分支是 37.5 对 37.2，在这一档难度上没有效果。三篇各出自一个团队，主评测基准两两不重合，无交叉复现，消融全部在各自的 in-domain 设定内完成；World Tokens 无代码，JEPA-WAM 的仓库标 "Coming soon"。

**World model 作为数据引擎**：[[Papers/2607-RynnWorldTeleop|RynnWorld-Teleop]] 用 40+ FPS 的 action-conditioned world model 实现"数字遥操作"——操作者 hand-pose 流实时驱动机器人 egocentric 视频合成，合成数据训练的 π₀ 可零样本迁移真机，数据饥饿的精细任务增强 +20pts。实际边界：仍需 1,800 条真机 demo 启动、跨 embodiment 需 per-platform 微调，是窄任务分布内的数据放大器而非"替代真机"；且高质量（FVD 550 / 2.8 FPS）与实时（40 FPS / FVD 1226）来自两个不同模型。

**World model 作为 policy evaluator**：[[Papers/2607-GigaWorld1|GigaWorld-1]] 把 surrogate 评估的成功标准从视频观感改为 **evaluator-world agreement**（同一 policy 在 real 与 world model 中 outcome / ranking / failure profile 是否一致），WMBench 2,989 对 paired rollout + 324K challenge rollout 的受控研究给出设计结论：evaluator 质量取决于 long-horizon action fidelity、可迁移物理先验与空间对齐 control（channel-concat pose map 的 Trajectory Accuracy 0.353 远超 ControlNet 0.257 / cross-attention 0.162），而非短期视频指标。关键警示：video model 对 contact-sensitive failure 有 optimistic bias——这是 policy evaluator 最危险的误差类型，false-success rate 应成必报指标。

**World model 作为 planner**：[[Papers/2607-WorldActionPlanner|WAP]] 把执行主体反转——VLM agent 提出子目标，action-conditioned world model 在想象中评估，policy 只作为被调用的工具执行已选中的方案，构成 propose → optimize → search 闭环。使这一反转在视频骨干上可行的是 pose-image conditioning：候选动作先经正向运动学渲染为骨架图像、再由 VAE 编码送入 Wan-T2V-1.3B（4 视角 2×2 拼图，21 帧 @7FPS 历史 → 20 帧 @20FPS 未来），从而绕开低维动作向量与视频生成骨干之间的接口失配。结果上，compositional LIBERO-Long 四设定 72/68/78/70，对照 π0.5 的 4/0/0/0 与 cosmos-policy 全 0；新布局六设定 88/86/90/66/84/78，baseline 多为 0；zero-shot Robosuite 80/76 对纯 VLM planner 的 58/22。消融阶梯从 56/28/46/32 起，依次加入 global optimization、local search、policy rollout imagination 逐级抬升；且 1 次想象即胜过带 ground-truth reward 的 BoN-8（60 vs 42）——在这一设定下想象比重采样更省。

这些数字的可比性有明确边界：WAP 使用 URDF、相机标定与硬编码 GRASP/RELEASE 原语，"72 vs 0" 因此是"带特权信息的模块化系统 vs 端到端 policy"的对比，而非 world model 单独的贡献；全文只有 Table 9 隔离了 world model 本身的增益。世界建模指标（+11.4% ID / +16.8% 泛化）是 PSNR 与 LPIPS 相对提升再取平均，论文自己的 limitation (g) 已承认该构造可疑。全部实验在仿真中完成，无真机；无 imagination horizon 扫描与误差累积测量；50 次 trial 无误差棒。

同一角色下的另一种取法是把 policy 整个拿掉。[[Papers/2606-PointWorld|PointWorld]]（CVPR 2026）保留"在预测里搜索"的结构，接口选择却与 WAP 相反：不预测像素、也不调用 policy，而是把 state 与 action 收进同一空间的 3D point flow——场景点的未来位移是 state，机器人自身点的未来位移是 action，后者由 URDF 经正向运动学生成（每个 gripper 约 300–500 点），于是动作表示与关节数、自由度、夹爪构型脱钩。骨干为 PTv3 + 冻结 DINOv3，H=10、每步 0.1 s，单次批量前向约 0.12 s，可直接充当 MPPI-MPC 的动力学模型。训练用约 2M trajectories / 500 小时（DROID + BEHAVIOR-1K，标注管线在 DROID 上恢复出超过 60% 的可靠 3D point flow）；DROID 测试集 ℓ2 mover 误差 PTv3-1B 0.0312 对 GBND 0.0390，而两者参数量差 957×；模型规模（50M–1B）与数据量（5%–100%）两条轴在 log 空间均近似线性；跨域迁移用 1/20 的迭代微调即超过 from-scratch specialist。真机 Franka 零样本 MPC 成功率从 Drawer 90 / Scarf 80 / Tissue Box 70 一直铺到 Book 20。

这条路线的边界与 WAP 不同类。主指标是 ℓ2 flow error 而非任务成功率，仿真 B1K 上已达 sub-centimeter mover 误差而真机零样本成功率仍散布在 20–90，"预测得准"与"做得成"没有在同一张表上闭合。任务点由人或 VLM 指定，系统不自行决定该跟踪哪些点。gripper-only flow 优于 whole-body flow，说明收益不随建模点数单调增长——这与 World Tokens 的排他路由、JEPA-WAM 的取层消融指向同一件事：预测什么、喂给谁，比预测得多更要紧。

**跨本体的接口之争：被预测的世界该以什么坐标接受动作**。上一条的读数（预测什么、喂给谁比预测得多更要紧）在动作这一侧有一个对称的问题：动作以什么形式进入视频骨干。现有取法已有五种且互不兼容——optical flow（[[Papers/2607-FlowWAM|FlowWAM]]）、3D point flow（[[Papers/2606-PointWorld|PointWorld]]）、图像平面稀疏点轨迹（[[Papers/2608-Hydra0|Hydra-0]]）、按注意力头分组的每臂 SE(3) 相对变换（[[Papers/2608-DreamXPhi|DreamX-Phi]]），以及把动作离散成与语言共享词表的码（[[Papers/2608-GalaxeaG05|G0.5]]，不经视频骨干）。

[[Papers/2608-Hydra0|Hydra-0]] 的诊断是：action-conditioned video world model 绑死在训练本体上，根因在于它们直接吃 native robot command——joint-space 指令本身编码机器人结构，同一条末端指令在运动学不同的机器人上产生不同的关节轨迹与可见连杆运动，两种表示都没有指定"图像平面上会发生什么运动"。它的接口是 N 条轨迹、每条含 H+1 个时刻的像素位置与可见性标记：有 URDF 与标定时由表面采样点经 link transform 传播再投影（部署时唯一路线，link transform 由 Isaac Lab 跑候选指令的 controller 与 physics rollout 产生），缺 URDF 的大规模数据上改用 AllTracker 稠密 track 加 SAM 3 grounded mask 切成 embodiment/object/unassigned 三类。训练期按 (None, Embodiment, Object, All) = (0.05, 0.40, 0.40, 0.15) 采样条件模式，Object 模式在推理时改喂"期望物体运动"就把同一接口反转成 world action model——只给 object flow，模型生成兼容的机器人运动，再由 action head 从 DiT latent 读出可执行指令。

这条线上最该带走的不是名次而是一处度量陷阱。作者自建的 baseline 是 Cosmos 2.5 原生 6D 末端动作，头条的 gripper EPE −90.40% / object EPE −60.16% 同时换掉了动作表示、video backbone（Cosmos 2.5 2B → Wan2.2 A14B）与 4-step 蒸馏三样东西；只换表示的受控对照是 34.28→13.80（约 −59.7%）与 13.23→6.27（约 −52.6%），量级小得多。更关键的是同表里零样本的 ATI 与 Wan-Move 在 gripper EPE 上分别是 4.62 与 4.67，比作者精调过的 Cosmos 2.5（34.28）好一个数量级，而它们唯一的优势是轨迹条件本来就以像素坐标给出——**gripper EPE 在相当程度上度量的是模型有没有照抄条件，跨表示比较这一列结构性地偏袒 flow 类接口**，object EPE 才是有信息量的那列。其 RoboLab 评测（5 policy × 6 task × 10 rollout，Pearson r=0.96 / Spearman 0.93 / MAE 5.7pp，按任务平均后复现全部五个 policy 排名）不能读作"world model 已可用于 policy evaluation"：action flow 来自录制好的真实末端轨迹（achieved-trajectory replay），policy 从不在生成的观测上被 query，作者在 Limitations 里也把评测限定为 open-loop；进入相关系数的点数 n 全文不自洽（正文写 "across policy-task pairs" 暗示 30，摘要与 contributions 读作 5），每点只有 10 次 rollout 使成功率被量化到 10% 步长、MAE 5.7pp 不到一个量化步。inverse mode 同样需要按原文而非摘要读：摘要称 "emergent"，而 object 条件是以 0.40 概率训出来的四种模式之一，world action model 还另做了 rank-32 LoRA 与 action/state head 的 post-train，真机只有单个 flexible-pipe-bending 任务的定性演示、无成功率与试验次数，contributions 一节自称 proof-of-concept。

[[Papers/2608-DreamXPhi|DreamX-Phi]] 走的是相反的抽象层次：把 PRoPE 的 group-action attention 机制从相机相对位姿迁到末端执行器，注意力头划成固定连续组、每臂一组，采用 identity intrinsic 使投影矩阵退化为纯 SE(3) 相对变换，于是同帧同臂的 patch 通过相对运动而非绝对坐标耦合；夹爪标量不能作 SE(3) 元素，另走 per-arm bias 注入，整条分支与预训练 self-attention 并行、adapter 与输出投影 zero-init。辅助监督（depth 分支、SAM3 mask 重加权、frozen V-JEPA 的 Gram 矩阵关系对齐）全部只在训练期作用，推理不需要 mask。值得注意的是它把 FlowWAM 式的 flow 接口降格为两个互补条件通道之一（robot-only optical-flow cue），主通道换成 PRoPE——这是对"optical flow 作为统一动作表示"的直接不同意见，而两者建在同一个 Wan2.2-TI2V-5B 底座上、识别出同一个"背景主导 loss"的问题（FlowWAM 用运动幅度加权、DreamX-Phi 用物体语义加权），却没有任何交叉实验。其结果为 WorldArena 2.0 Track 1 的 2026-08-12 快照上 31 个条目排第一（EWMScore-P 60.65），Track 2 的 Adjust Bottle 67.19% 并列第二。

三处边界必须与数字一起传播。其一，**论文自陈全文没有 matched ablation**——PRoPE、robot-only flow、depth 分支、SAM3 重加权、V-JEPA 关系损失、DMD 蒸馏六个组件一个都没被隔离，因此"结构化几何接口优于 token 化接口"这一最响亮的方法论主张目前只有整系统的 leaderboard 名次作支撑。其二，WorldArena 的分数必须连版本与快照一起引用：WA2.0 在聚合前按 ground-truth 参考值对 Dynamic Degree、Flow Score、Motion Smoothness 三项封顶（原文明载），而同一模型这两项在 WA1.0 下是 88.71 / 100.00、在 WA2.0 下变成 22.90 / 5.81；库内另有一处口径分歧的直接观察——FlowWAM 笔记记录的 WorldArena EWMScore 与 DreamX-Phi 表中同名条目相差 3.5–3.7 分，而两边的 Trajectory Accuracy 完全一致（CtrlWorld 48.20、IRASim 35.92），说明同一 benchmark 名下至少流通着两套聚合口径。跨版本或跨论文直接比 EWMScore 因此不成立（"WA1.0 与 WA2.0 不可比"是库内对上述封顶事实的推断，论文未作此陈述）。其三，Track 2 对 world model 质量的区分度明显低于 Track 1：Track 1 上 15.68 分的 EWMScore-P 差距只换来 Track 2 上 5.86 个百分点的策略成功率差距，而 Track 1 垫底的 IRASim 仍能拿到 61.33%——用 leaderboard 名次论证"该 world model 可作 policy 训练环境"需要格外小心。相机静止也是隐含前提：intrinsic 置为 identity 后通道里没有为相机运动留位置，移动/手眼相机未验证。笔记核查为 partial，其"WA1.0 与 WA2.0 不可比"一条标 `unsupported`，本 survey 只按上述方式记为操作建议。

这四种接口之间没有任何交叉实验——没有一篇在固定骨干、固定数据、固定评测的条件下把两种动作表示放在一起比。合起来的状态是**开放分歧而非收敛**：PointWorld 的 gripper-only flow 优于 whole-body flow、Hydra-0 的 gripper EPE 偏袒 flow 条件、DreamX-Phi 把 flow 降为辅助通道，三处读数指向的设计方向并不一致，而衡量它们的指标本身还未中立（见 Open Problem 6、7）。

**Planner 角色的第二个必要条件：latent 的度量结构**。把 world model 当搜索基底时，planner 消费的其实不是 latent 本身而是 latent 之间的距离。[[Papers/2608-DALeWM|DA-LeWM]]（2026）把这件事与通行的 latent 质量判据切开：latent 能否解码出任务量是 **information sufficiency**，planner 用的欧氏 goal distance 能否把候选动作序列按真实任务进展排序是 **decision-metric alignment**，后者是序性质而非数值性质，两者逻辑独立。据此给出两个可测诊断——Plan-Real Spearman（每个 held-out (start, goal) 对采 N=64 条候选，同时算 latent cost 与 simulator rollout 的真实 cost，取 rank correlation 后对 n=30 对求均值）与 CEM 分阶段 Spearman。方法侧只加 inverse-dynamics 与 demonstration-conditioned goal-action 两个**只在训练期存在**的辅助头，评测时丢弃，推理算力严格相同。

分离性证据很干净：PushT 一 epoch matched budget 下，四个非坍缩变体的 state / action / goal-action probe R² 分别挤在 0.89–0.90、0.86–0.89、0.77–0.80（差异 ≤0.03），online success 却跨 43 个百分点（LeWM 49.3±12.2 → DA-LeWM 92.7±1.2，中间 inverse-only 64.0±7.2、all-heads 71.3±4.2）。去掉 SIGReg 的坍缩对照从反面确认了 probe 的盲区：latent cost 的 max/min dynamic range 从 3–30× 塌到约 1.005×，planner 对每条 plan 拿到几乎相同的目标值，success 49.3→2.0、Plan-Real Spearman +0.280→+0.031，而 probe 只在这种彻底的信息丢失上才有反应（state R² 掉到 −6.14）。

但**这两个诊断解释不了这次提升的主要部分，论文自己把这写在正文里**。inverse-only 的 Plan-Real Spearman 最高（+0.420，30/30 为正）却只有 64.0% 成功率；CEM 的 elite 阶段所有变体的 Spearman 都在零附近（LeWM +0.036、inverse-only −0.089、DA-LeWM −0.011），Appendix 的局部几何检查同向（elite 邻域内 log 距离的 Pearson 只有 +0.050 到 +0.092）。增益的量级也依赖基线所处的位置：一 epoch 下 LeWM 在 PushT 只有 49.3%，而 published LeWM 是 96，到 epoch 10 时差距已缩到 2.7pp；对已发表基线的比较（Table 5）用的是 published 数字而非同预算复跑，DA-LeWM 只在 PushT 与 Reacher 排第一，Cube 落后 DINO-WM 5.3pp、TwoRoom 同时落后 DINO-WM 与 PLDM，而 Table 1 里 LeWM 一 epoch 的 TwoRoom（98.0）已高于 DA-LeWM 十 epoch 的 96.0。两个诊断本身也不可部署——它们需要在真实 simulator 里 rollout 每一条候选来拿真实 cost（PushT 上是 30 对 × 64 条，CEM 分阶段更是 15 对 × 300 候选 × 30 迭代），是评测期才有的特权信息；评测 goal 取自 held-out demonstration 中固定偏移的一帧，作者明说这保证 goal latent 落在数据分布内且可达，把"goal 是否可达"整块难度移到了方法之外。β 也非无条件有益：Reacher 上 β=0.3 回退到 78.0%，低于 LeWM 基线的 82.0%。可带走的是那条切分与那套内部对照纪律（同 backbone、同 CEM 预算、matched training randomness、辅助头评测期丢弃、失败的 R/V proxy 主动标注为 bug、Cube 上因大量并列而放弃 Spearman 而非硬报），不是 43.4pp 这个数。笔记核查为 partial。

**表示层与物理保真度**：上述角色都默认 world model "懂物理"，[[Papers/2607-PhiZero|Phi-Zero]] 直接测这个假设并给出分离性证据。其做法是 reason-then-render 而非直接生成像素——先用自监督学到的离散"物理语言"推理（FSQ levels (8,5,5,5,5,5)、25K 词表，4 秒视频压成 256 个符号，Qwen3-VL-4B 作 reasoner），再由 Wan2.2-5B LoRA 扩散解码器渲染。生成端指标领先：Physics-IQ Verified IQ-Score 41.2 > Cosmos3-Super 39.5 > Wan2.2-14B 32.2，PhyGround Physics 3.01，WorldModelBench Total 8.19。判别端却没有同步：IntPhys2 Overall 56.34 而 Hard split 仅 52.38（随机基线 50，V-JEPA 57.42），LikePhys 上刚体 29.14 最好而流体 53.15 倒数第三，WS-IoU 27.6 落后。"生成得像"与"判得对"在同一模型上分离，对把 world model 当 planner 或 evaluator 的两条路线都是直接风险——它们消费的正是判别能力。方法层的关键缺口是没有同数据同算力、仅移除中间表示的对照，21.2→41.2 的增益混淆了表示、数据与训练三个变量；该表示本身是有损压缩（256 符号重建 PSNR 28.9，Wan2.2 VAE 用 44,800 token 达 37.7）；其 "zero-shot" 迁移仍需按源域微调 tokenizer，4 秒固定视界靠滑窗自回归外推，且无代码发布。

**评测层：把"指令写明的"与"必须自行推断的"分开**。上述角色都默认 world model 会正确回应场景，而现有 world-model benchmark 绝大多数评的是 explicit instruction fulfillment——先指定 layout、相机轨迹、动作序列或交互后果，再检查它是否被实现。[[Papers/2608-WorldExam|WorldExam]]（2026）把"从初始状态可以推出、但指令里没有描述的后果"单列成一层：反应类任务只给一个触发用的 atomic control，刻意不写明场景应当如何回应（走上台阶时高度应随地形变化并保持接触、靠近障碍物应出现接触或绕行、进入他人社交距离对方应有反应）。全套为四个诊断层级（Visual Quality / Control Adherence / Spatial Consistency / World Reactivity）、8 个任务、1,474 个 case，覆盖 20 个模型（6 camera-driven / 7 action-driven / 7 language-driven）。跨范式可比性靠 interface adaptation 实现——同一控制意图分别适配成 SE(3) 相机轨迹、离散动作序列与自然语言；且只出两条 track、不出总榜，以免把"接口不支持"记成"做得差"。

两组结论值得进 mental model。其一，**能力沿接口分裂且互补**：dynamic-interaction track 上 action 接口的主体控制明显更准（Subject Control 55.47 / 49.75 对 language 最好的 37.28），却在反应类任务上大幅落后（Terrain 27.49 对 64.39、Object 33.75 对 75.96、Social 60.37 对 85.10、Physical 33.43 对 63.84），反转幅度远大于领先幅度。其二，**视觉质量与其余三层解耦**，且证据是多点位的：language-driven 一族的视觉质量均值挤在 79.64–81.04 的窄带里，任务均值却从 39.85 铺到 65.02；ReCamMaster / FantasyWorld 的视觉均值 80.97 / 80.23 对应的 Camera Control 只有 38.64 / 18.46；Kling 2.5 视觉均值最高（81.04）而 Goal Completion 仅 48.25。这与 [[Papers/2607-PhiZero|Phi-Zero]] 的"生成保真不蕴含物理判别"独立同向，并把它从单模型现象扩到跨范式规模。反应类的典型失败被描述为"被接触物体保持不变"或"主体直接穿过去"，与 [[Papers/2607-GigaWorld1|GigaWorld-1]] 从 policy evaluation 角度观察到的 contact-sensitive optimistic bias 落在同一处环节（contact），而两者的团队、数据与评测目标均不同。两者的失效方向是否一致，下面的 [[Papers/2608-WorldSimProbe|WorldSimProbe]] 给出了相反的读数。

适用边界同样清楚。最主要的问题是**接口范式与模型档次共线**：dynamic track 上的 action-driven 只有两个本地部署模型，7 个 language-driven 全部走 API backend，"action 接口 → 世界不反应"与"这两个特定模型 → 世界不反应"在这份数据里分不开。范式内方差还大于范式间差距（language-driven 的 Kling 2.5 任务均值 39.85 低于 action-driven 的 LingBot-World 39.91），"language 接口更会反应"实际由三个最强系统撑起。四个反应类任务的 ground truth 是 checklist，由 LLM 起草、image-conditioned refiner 改写后定稿，人工只筛初始图、未审核 checklist 本身；judge（GPT-5.5）只看 10 帧均匀采样，且"无法核实"一律记为不满足，而画质更差的模型更容易触发这条规则。两项可靠性检查（与人一致性 Spearman 0.8614、换重建后端后范式内排名不变）做了，但分任务最弱的 Social Interaction 只有 0.7019。此外 reactivity 层实际只有 9 个模型、Goal Completion 只有 7 个，每个 case 只生成一次，数据与评测工具包尚未发布。原文一致性已核查，库内暂无独立复现。

**同一层的第二把尺子：把"动作是否被实现"从"世界是否反应"里拆出来**。[[Papers/2608-WorldExam|WorldExam]] 问世界会不会对没写明的事作出反应，[[Papers/2608-WorldSimProbe|WorldSimProbe]]（2026）问那个反应有没有被真实执行的动作在物理上支撑，并把两件事写成一条可检验的契约（Observable Simulator Contract）：生成的 agent motion 要对应 supplied action（action-realization），environment response 要由已实现的 motion 与初始环境状态支持（interaction-response）。两条都不可直接观测，于是全部改写成受控干预下的可观测后果——五个 probe suite、18,608 个 instance（RoboTwin 5,498 / ManiSkill 6,610 / LIBERO 6,500）、6 个开源 ACWM，每个 instance 六模型共享同一初始观测、动作流、simulator seed 与三个 diffusion seed。

先说契约的前一半。action realization 本身就在退化，而这一层在既有 world-model benchmark 里基本没有位置。把 donor task 的动作流放进 receiver 场景执行，六个模型的 fidelity 随 receiver–donor 运动失配整体下降（平均 Spearman ρ=−0.433）；同一 episode 换执行风格——expert、5 名 human teleoperator、π0.5 的 early 与 late checkpoint——六个模型在 late checkpoint 上一律比 early 高 10.8–16.1 分。两者指向同一机制：动作一旦偏离熟悉轨迹，模型就滑回 scene/task 关联的运动先验。跨平台排名一致性 ρ=0.695，且 action-injection 与 unified action–video 两类架构都横跨高低名次，说明这不是某种接法特有的问题。

契约的后一半与 WorldExam 撞出一处方向冲突。WorldSimProbe 在 simulator 验证过的**无接触**场景里追踪目标物体是否被移动，三种触发的跨模型均分为 distractor 75.0、spatial proximity 54.5、appearance-induced false contact 38.6；支撑其设计的 audit 更硬——50 个 grounding failure 里 50/50 全是 false positive，无一例 omission。WorldExam 记录的典型反应类失败恰恰是 omission（被接触物体保持不变）。方向相反，而相反的来源是可以指出来的：**两个基准按构造只能看见对方看不见的那一半**——WorldExam 的 case 是"接触应当发生"，只能罚漏；WorldSimProbe 的 case 是"接触不应发生"，只能罚编。模型群体也不同：WorldExam 的 reactivity 层混入大量 API 通用视频模型，WorldSimProbe 的六个全是按各 simulator 官方 split 微调的 in-domain ACWM。因此能保留的共识只有"contact 是共同失效环节"，"world model 倾向于漏掉接触"这一条应记为争议。对下游用途，两个方向的含义并不相同：漏掉接触会让 planner 低估动作后果，编造接触会让 evaluator 高估成功——后者与 [[Papers/2607-GigaWorld1|GigaWorld-1]] 的 contact-sensitive optimistic bias 同向。

judge 的判定规则本身也参与结果。在 750 个人工标注 rollout 上，RMFA 这类基于光流的自动指标与人工分级的 ρ=0.750，而 VLM 二元判断只有 0.450——VLM 对 91.7% 的样本判"动作被跟随"，人类只判 42.2%。与 WorldExam 那条"无法核实一律记为不满足"的保守规则放在一起，同一批生成结果的分数可以被判定规则推向两端。这不等于"VLM 不能做 judge"：WorldSimProbe 自己在 T5 用 Qwen3-VL-8B 判 interaction primitive，与多数人工标签一致率 94–97%。区别在任务粒度——细粒度的二元 action-following 判断上 VLM 系统性乐观，primitive 识别则可靠。

对评测口径最直接有用的一条在下游：用各 ACWM 生成的数据训 policy，standard 轨迹下成功率挤在 78–86% 难以区分，OOD 轨迹下分离成 53 / 34 / 21% 且与 probe 排序一致——以成功率为导向的评测会把熟悉控制之外的 fidelity 差异整个抹掉（见 Open Problem 7）。边界：T4 的接触判据依赖 TAPNext++ 追踪与位移阈值；T5 的 shake 一项六模型全在 0.0–1.2，在当前模型档次上区分度接近于零，而模型间均分区间仅 17.7–21.8，primitive 之间的差异大于模型之间；六个被测模型均为开源 ACWM，不含闭源与通用视频模型；下游实验只在单个 RoboTwin task 上完成。原文一致性已核查，库内暂无独立复现。

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
**局限**：Model accuracy 限制 planning horizon；多 Agent 交互建模复杂；WAM 推理开销大且普遍回避报告（RynnWorld-4D 前向 890ms / 9Hz，FlowWAM 无 latency 数字）——"训练期消费、推理期删除"的接法已给出一条可行答案（World Tokens 61.85 ms、JEPA-WAM 85 ms、MobileWAM 938 ms），代价是放弃推理期的想象与搜索；action 与 imagination 的同步性可被攻击（[[Papers/2607-BadWAM|BadWAM]]，见路线 6）；evaluator 用途下对 contact-sensitive failure 有 optimistic bias（GigaWorld-1）；planner 用途下增益尚未与特权信息（URDF / 相机标定 / 硬编码抓放原语）分离（[[Papers/2607-WorldActionPlanner|WAP]]）；生成保真与物理判别可在同一模型上背离（[[Papers/2607-PhiZero|Phi-Zero]] 于 Physics-IQ 领先却在 IntPhys2 Hard 接近随机）；视觉观感与控制/反应能力在跨范式 20 模型规模上解耦，且 contact 与场景反应是共同失效点（[[Papers/2608-WorldExam|WorldExam]]）；**动作是否被忠实实现是比"世界是否反应"更靠前的一层，且同样在退化**——动作偏离熟悉轨迹时六个 ACWM 一致滑回运动先验（[[Papers/2608-WorldSimProbe|WorldSimProbe]]，ρ=−0.433 / late-early 10.8–16.1），而 contact 失效的**方向**在库内存有争议（WorldExam 记录 omission，WorldSimProbe 的 audit 是 50/50 全为 hallucination，两者的 case 构造只允许各自看见一半）；自动判定规则本身影响结论（VLM 二元 action-following 判断对 91.7% 的样本判正，人类 42.2%）；**新增预测通道的边际收益归因不清**——[[Papers/2607-STWAM|ST-WAM]]（DINO 未来）与 [[Papers/2607-N0TWAM|N0-TWAM]]（触觉未来）的消融同向显示新加的那条预测通路不是主要收益来源（见路线 9）；**动作以什么坐标进入视频骨干仍是开放分歧**，optical flow、3D point flow、图像平面稀疏点轨迹与每臂 SE(3) 四种接口之间无任何固定骨干、固定数据的交叉实验，且衡量它们的指标本身偏向特定接口（[[Papers/2608-Hydra0|Hydra-0]] 的零样本轨迹条件模型在 gripper EPE 上优于精调的原生动作 baseline 一个数量级，说明该列主要度量"有没有照抄条件"），[[Papers/2608-DreamXPhi|DreamX-Phi]] 更是自陈零 ablation、五个组件的贡献一个都未隔离；planner 用途下还多一层要求——latent 编码了任务量不蕴含 planner 消费的那个距离能把候选按真实进展排序，而现有的 linear probe 只对彻底坍缩有反应（[[Papers/2608-DALeWM|DA-LeWM]]：四个非坍缩变体 probe R² 差异 ≤0.03，online success 跨 43pp）。~~与 VLA 结合的方式仍 unclear~~——2026 年已由 WAM 路线给出可行答案，RoboTwin 2.0 上 WAM（ABot-M0.5 94.1 / FlowWAM 92.9）超过纯 VLA baseline。

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

[[Papers/2608-Zetta|Zetta]]（2026）把同一处（冻结 policy + 高层调度）推到 action 频率，并且换了监控者的载体：RobustExec 的调度器是一个学出来的 MLP，Zetta 的 critic 是一段由离线 agent 写出来的代码，逐 action chunk 产出结构化 proposal，Orchestrator 裁决是否切出 VLA 执行 recovery skill，并按 re-entry contract 交还控制权。这样 critic 的开销与 VLA 推理开销解耦——对照的 RPent 每个决策点调一次 LLM，392–513 s/episode，而 Zetta 把 agent 整体挪到离线。critic 与 recovery 本身由 rollout-batch 层生成：失败聚类加逐层因果诊断产出候选，iteration 层用 cluster 全通过与 held-out ΔSR 双闸门决定是否入 skill memory，其中 outcome 侧接的是环境官方谓词而非 LLM 自评。配套的 Z-Infra 把 agent 逻辑与环境/模型 worker 池解耦（VLM 与 action expert 拆进程、中间激活走 CUDA IPC，平均推理延迟降 53%），吞吐从 1.72 提到 35.1 episodes/min——把"演化速率受限于采样而非 idea"这个判断当成工程问题来解，这条线上少见。结果为 RoboCasa 18 任务 macro-average 73.56%→93.56%（冻结 GR00T N1.5）、LIBERO-Pro 全部 40 个 task-setting pair 32.00%→71.13%（冻结 π0.5）。

该结果不支持"增益来自闭环治理"这一归因。两张成功率表里唯一的非 Zetta 行就是自家的 frozen base policy，既没有把自己降级成 episode 级反思跑一遍，也没有任何既有 open-loop harness 入表；三条 loop 一条都没有单独消融，全文无 ablation 章节。更关键的是没有 budget-matched 对照：Zetta 相对 pure VLA 至少多了额外执行步数与 bounded retry、以及 base policy 之外的外部工具（GraspGen 抓取位姿、CAP 稳定放置、motion planner、segmentation），baseline 一样都没拿到，而演化消耗的 rollout 数、agent 调用数与 wall-clock 一概未报。摘要标的 90.8% 是 Goal 两个 setting 的均值，全量口径 71.13% 写在正文里；本该最能证明这套方法的 LIBERO-10 恰恰最弱（S setting 40.0%，四对任务从 0% 停在 0%）。还有一处决定它能否离开 simulator 的设定：critic 监控的信号包含 benchmark 提供的官方谓词（official grasp predicate），成功判定直接查 official task predicate——这些量在真机上不存在，而把 critic 换成纯感知估计后会掉多少，论文没有讨论。可带走的是那个 formulation——把在线可靠性检查编译成廉价代码谓词、把大模型赶到离线，从而让延迟与可靠性解耦——而不是那两个百分点数。与路线 8 的 [[Papers/2608-HyMeS|HyMeS]] 合看，两者共享同一结构（技能留在冻结权重里、治理逻辑活在代码空间），分歧在接管方式：HyMeS 以梯度注入速度场做连续 steering，Zetta 直接切断 VLA 换成 recovery skill。

**Open Problems**（Survey 提出）：
- Certified robustness for VLA
- Physically realizable defense
- Safety-aware training procedure
- Unified runtime safety architecture
- Standardized evaluation protocol
- Action-imagination consistency verification（BadWAM 补充：WAM 的安全属性应包含 action 与预测未来的同步性，可执行 inverse-dynamics check 是候选方向）
- Runtime 谓词的去特权化（[[Papers/2608-Zetta|Zetta]] 补充：code-space critic 目前读的是 simulator 提供的官方 grasp / success 谓词，这类量在真机上不存在；把判据换成纯感知估计后系统掉多少，是这类 harness 能否离开仿真的前置问题）

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

**代表论文**：LaMem-VLA (2026)、ABot-AgentOS (2026)、HyMeS (2026)

**核心思路**：主流 VLA 是 Markovian（只看当前观测），长时程任务需要记忆。2026 年出现从 policy 内部 latent memory 到 agent 系统层显式 graph memory 的完整谱系，两端各有一个代表实例：

- **Implicit 端——[[Papers/2607-LaMemVLA|LaMem-VLA]]**：把历史重构成 context-native latent memory token（short-term 视觉 vault + long-term 动作语义 vault，top-K 检索后压成定长 token）直接编织进 VLA embedding 序列参与 self-attention，而非 policy-side 外部条件；latent-native vs policy-side 对照 +2pt（73.9 vs 71.9，SimplerEnv-Bridge），LIBERO 均值 97.6%。边界：纯仿真无真机、离散 top-K 检索不可微、超参甜点窄。
- **Explicit 端——[[Papers/2607-ABotAgentOS|ABot-AgentOS]]**：agent 系统层 typed graph memory（video/对话/session 统一 schema + hybrid retrieval + 子图扩展）+ verification-aware harness + split-wise gated self-evolution；EgoLifeQA 上 1 帧 65.4 击败 50 帧 EGAgent-Gemini2.5Pro（57.5），证明 graph memory 对长时程 egocentric 经验的结构化压缩有效。边界：full context 放得下时 memory pipeline 全面落后（Mem-Gallery 88.6 vs 92.6）；保守 gate 下 self-evolution 几乎不长肉（8 splits 仅 1 asset 存活）——安全 vs 演化效率 trade-off 的诚实数据点；零真机实验。

**为什么必须压缩**：[[Papers/2608-VLAProprioception|VLAProprioception]] 不引入任何记忆机制，直接扫描 raw observation history 的深度（K=1→96），结果非单调——短历史优于单帧，更深的未压缩历史不再带来收益并最终损害控制，小工作空间高精度任务族退化最重、经 VLM prefix 注入时尤甚；作者取 K=8 为经验操作点而非普适最优。这把压缩式 memory 从"工程优化"改写成"避免退化的必需品"，也给下面的 crossover point 提供了一个量级参考：raw frame stack 在 K≈8 附近就已越过收益峰值。口径不同但方向一致的旁证来自专题二的 [[Papers/2603-SGVLA|SG-VLA]]——加入 temporal history 反而使 ManiSkill-HAB 从 0.73 掉到 0.49。边界是该证据只覆盖 raw 堆叠，"长 raw 历史有害"不等于"长历史无用"，压缩式记忆能否在更大 K 上保住收益尚未被测。

**中间形态：技能留在权重里，记忆策略活在代码空间**。[[Papers/2608-HyMeS|HyMeS]]（2026）既不给 VLA 加记忆模块，也不把记忆抬到 agent 系统层，而是按载体把两件事分开：运动技能留在冻结的 π0.5 权重里，记忆策略是一段可读代码，由 coding agent（Opus 4.8）经 heuristic learning 迭代得到（P^(n+1)=Edit(P^(n), ξ_n, b_n)），既不用梯度也不用 expert action label，评测时策略冻结。代码里的阶段约束不经 prompt 或额外 token 传给 policy，而是以梯度形式注入冻结 VLA 的 flow-matching velocity field（v̂ = v_θ* + λ_t ∇R），随 sigmoid 调度衰减，全程不更新权重；阶段何时推进由 PACE 判定——proprioception 判据或 Qwen3-VL-8B 多帧判断，最近 5 次里有 3 次同意才切换。

RoboMemArena 12 任务上 CSR 52.5→66.2、TSR 41.3→60.1，相对 PrediMem 是 +4.5 CSR / +14.5 TSR。分项比总分更有信息量：遮挡类里 PrediMem 的 CSR 38.3 低于纯反应式 π0.5 的 50.4——预测式记忆在这一类上是净损，而 HyMeS 持平（50.6）且 TSR 高 7.0；计数类里 HyMeS 的 TSR 50.0 高于 PrediMem 36.7，CSR 却更低（60.3 vs 72.2），失败集中在早期 stage，换来的是"走得更远"而非"每步更稳"。消融方向一致：学到的 P* 相对初始 P^(0) 值 +8.5 CSR / +18.4 TSR；PACE 拆成单模态后 vision-only 掉 16.0/21.7、proprio-only 掉 8.8/8.4，两种信号都无法单独承担阶段判定。真机 SO-101 三任务各 35 trials，TSR 25.7→57.1。边界：PrediMem 是在作者自定的 12 任务协议上重评而非引用其发表的 26 任务结果，任务筛选依据只有 protocol check 与 π0.5 的行为表现；真机 35 trials 摊到三任务后每项样本量很小（分任务为 2/10→7/10 这一量级）；记忆策略由闭源 coding agent 产出，复现依赖该模型。

**Open question**：memory 的价值边界（context 多长时 memory 开始占优的 crossover point）未被系统刻画。"memory 应活在 embedding 空间还是符号空间"已不再是二选一——[[Papers/2608-HyMeS|HyMeS]] 的消费者仍是 action head，载体却是可读代码，两者靠梯度注入速度场连起来。代价随之明确：这种接法引入了一个判断"阶段是否推进"的外部环路，而 PACE 的单模态消融显示该环路正是系统最脆弱的一环。空白因此转移到获取端——符号策略依赖闭源 coding agent 产出，其成本、可复现性与在新任务族上的迁移都还没有独立评估。同一载体上还分出了第二种接管方式：[[Papers/2608-Zetta|Zetta]]（路线 6）同样把逻辑写成代码、把权重整个冻结，但不做连续 steering，而是逐 action chunk 判定后直接切出 VLA 换成 recovery skill，再按 re-entry contract 交还控制权。两者都没有与对方比过，也都没有把自己降级成 episode 级反思做对照，因此"代码空间的治理逻辑该以什么粒度介入 policy"目前没有可比证据。

---

### 9. 触觉进入 VLA：预测式 vs 反应式（2026-08 新增）

**代表论文**：N0-VTLA (2026)、N0-TWAM (2026)

主流 VLA 的输入只有 RGB + 语言 + 本体感受，contact-rich 任务缺少接触信息——路线 7 已把"human 视频无触觉与力"列为数据引擎路线的固有短板。NeoteAI / Fudan TEAI 的两篇姊妹作在同一批数据与基准上给出把触觉写进模型的两种方式，且**结论彼此相左**，这是这条路线上最值得记的信号。

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
| **LIBERO** | Benchmark | Long-horizon manipulation | Success Rate, SPL | [[Papers/2608-GalaxeaG05\|G0.5]] 98.9；[[Papers/2608-StellaVLA\|StellaVLA]] 98.8；Xiaomi-Robotics-0 98.7 | 多 task suite；语言鉴别力存疑——把指令换成 task-ID embedding 仅掉 2.3pp（[[Papers/2607-TurboVLA\|TurboVLA]]），且 LIBERO-Goal 的 10 个任务共享同一视觉场景，句子编码器与 10 路任务码难以区分（[[Papers/2608-GSRParaVLA\|GSR]]）。榜首一档已挤进 98-99% 的 0.2pp 带宽内，名次不再承载信息量 |
| **LIBERO-Para** | Benchmark | 4,092 改写 episode（870 Act / 259 Obj / 2,963 Comp） | Full Para SR / PRIDE | Full Para 76.0（Xiaomi-Robotics-0）；PRIDE 70.4（[[Papers/2608-GSRParaVLA\|GSR]]-π0.5） | 只改指令措辞，物理任务/初始状态/成功判据不变；主流 VLA 掉 19-68pp。测的是 paraphrastic invariance，不含新物体/新动作/新组合 |
| **LIBERO-Plus** | Benchmark | LIBERO 的扰动泛化集，多轴（相机、光照、传感器噪声、语言改写等） | Zero-shot Success Rate | π0.5+[[Papers/2608-JEPAWAM\|JEPA-WAM]] 86.3；[[Papers/2608-StellaVLA\|StellaVLA]] 85.1（对照 StarVLA-OFT 75.0，增益集中在 Camera 轴 +23.5）；JEPA-WAM 79.2（不含大规模 robot-policy 预训练一档最好）；[[Papers/2607-STWAM\|ST-WAM]] 72.8（对照 Fast-WAM 51.5）；[[Papers/2608-CofactVLA\|CofactVLA]] 69.1 | 平均分掩盖轴间 tradeoff：JEPA-WAM 的领先主要来自 Camera 一列，Language 一列只有 68.2（ResVLA 88.5 / RoVLA 92.9）。用 appearance 类轴论证"预测未来带来鲁棒性"存在归因风险——DINO 类特征对这类扰动本就近似不变（ST-WAM）。各文的 baseline 多为引用而非重跑，跨论文分数不可直接比 |
| **LIBERO-Pro** | Benchmark | LIBERO 的 40 个 task-setting pair（Object / Spatial / Goal / Long × 多 setting） | Success Rate | [[Papers/2608-Zetta\|Zetta]] 71.13（冻结 π0.5 基座 32.00） | 分 setting 后鉴别力远高于原版 LIBERO；读数须认口径——Zetta 摘要标的 90.8% 只是 Goal 两个 setting 的均值，全量 40 对为 71.13，LIBERO-10 的 S setting 仅 40.0%（四对任务停在 0%） |
| **VLA-Arena** | Benchmark | 分级泛化评测（含真机 OOD-L2 分级） | Normalized Score / Progress | [[Papers/2608-StellaVLA\|StellaVLA]] 0.63（π0.5 0.44、Evo-Depth 0.41、OpenVLA-OFT 0.39、LingBot-VLA 0.22） | 原文"超过 strong prior models"的表述以最低基线为参照；对次强基线的实质差距是 +0.19。真机 OOD-L2 一档所有方法都低（StellaVLA progress 1.9/4） |
| **UniVTAC** | Benchmark | 视触觉操作，8 任务 | Success Rate | [[Papers/2607-N0TWAM\|N0-TWAM]] 84.5 / [[Papers/2607-N0VTLA\|N0-VTLA]] 83.1（InternVLA-A1 67.1） | 触觉路线唯一的第三方公开基准；两篇总分领先但均有任务级输给基线（N0-VTLA 输 3/8） |
| **Physics-IQ / IntPhys2** | Benchmark | 视频物理一致性（生成 / 判别） | IQ-Score / Accuracy | [[Papers/2607-PhiZero|Phi-Zero]] 41.2（Physics-IQ） | 两类指标可给出相反排序：Phi-Zero 生成端第一，IntPhys2 Hard 52.38 却近随机基线 50 |
| **RLBench** | Benchmark | 100+ manipulation tasks | Success Rate | Diffusion Policy, ACT | Simulation benchmark，多样化 task |
| **RoboTwin 2.0** | Benchmark | 50 manipulation tasks | Success Rate | ABot-M0.5 94.1%；[[Papers/2608-GalaxeaG05\|G0.5]] 93.3（clean 93.7 / randomized 92.8，对次优 LingBot-VA 领先 1.1pp）；WAM 类 92-94% 已入饱和区 | Randomized settings，challenging；榜首一档的名次差已小于多数论文的 seed 抖动 |
| **RoboCasa365** | Benchmark | 365 任务（Atomic + Composite） | Success Rate | Xiaomi-Robotics-1 57.4% | Composite-Unseen 极难（SOTA 仅 32.1%），长程组合泛化探针；受控研究常只取 45 atomic + 20 composite 子集并按族单训 category expert（[[Papers/2608-VLAProprioception\|VLAProprioception]]），该口径的分数与全 365 任务不可比 |
| **BEHAVIOR Challenge (2025)** | Benchmark | 50 个长程家务移动操作任务 | 第三方 ranking metric | [[Papers/2608-GalaxeaG05\|G0.5]] 0.3136（4 epoch）/ 0.2904（1 epoch）；π0.5 0.2626；挑战赛冠军 RLC 0.2605 | 少数几个未进饱和区、且带第三方评分口径的长程基准；1 个 post-training epoch 即超过四 checkpoint 的冠军方案，是预训练先验质量的外部信号 |
| **WMBench** | Benchmark | 2,989 对 paired real/world-model rollouts | WMES / evaluator agreement | GigaWorld-1 | 首个以 evaluator-world outcome agreement 为标准的 world model 评测 |
| **WorldExam** | Benchmark | 1,474 case / 8 任务 / 20 个视频世界模型 | 四层诊断分数（Visual Quality / Control Adherence / Spatial Consistency / World Reactivity） | 分范式两条 track，不出总榜 | 反应类任务只给触发控制、不写明该发生的反应；同一控制意图适配为 SE(3) 轨迹 / 离散动作 / 语言以跨范式可比；reactivity 层实际只有 9 个模型，Goal Completion 只有 7 个 |
| **WorldSimProbe** | Benchmark | 18,608 controlled instances / 5 个 probe suite / 6 个开源 ACWM（RoboTwin 5,498 + ManiSkill 6,610 + LIBERO 6,500） | 按 Observable Simulator Contract 分解的 probe 分数（action-realization / interaction-response） | 无统一冠军：LingBot-VA 领先 RoboTwin 与 ManiSkill，Ctrl-World 领先 LIBERO | 把"动作是否被忠实实现"独立成层，是 world-model 评测里此前缺席的一环；六模型共享同一初始观测 / 动作流 / simulator seed / diffusion seed；跨平台排名一致性 ρ=0.695，但 suite 级排名与总分不一致；被测模型全为开源 ACWM，不含闭源与通用视频模型 |
| **WorldArena** | Benchmark | 公开 leaderboard，Track 1 生成质量 + Track 2 下游 policy 成功率 | EWMScore-P / Trajectory Accuracy / 任务成功率 | Track 1 [[Papers/2608-DreamXPhi\|DreamX-Phi]] EWMScore-P 60.65（2026-08-12 快照，31 个参赛条目第 1）；Track 2 Adjust Bottle 67.19% 并列第 2 | 引用时必须带版本与快照日期：WA2.0 在聚合前用 ground truth 给 Dynamic Degree / Flow Score / Motion Smoothness 设上限，同一模型的两项分量从 WA1.0 的 88.71 / 100.00 变成 WA2.0 的 22.90 / 5.81；库内另观察到 [[Papers/2607-FlowWAM\|FlowWAM]] 记录的 EWMScore 与 DreamX-Phi 表中同名条目差 3.5–3.7 而 Trajectory Accuracy 完全一致（CtrlWorld 48.20、IRASim 35.92），即同一基准名下至少流通两套聚合口径。Track 2 的鉴别力远低于 Track 1——Track 1 上 15.68 的 EWMScore-P 差只换来 5.86pp 的 policy 成功率差，Track 1 垫底的 IRASim 在 Track 2 仍有 61.33% |
| **LeWM 规划四件套（PushT / Reacher / Cube / TwoRoom）** | Benchmark | latent world model 的在线规划评测 | Online Success Rate | 已发表口径（Table 5，10 epoch）：[[Papers/2608-DALeWM\|DA-LeWM]] 98.7 / 87.3 / 80.7 / 96.0；LeWM 96 / 86 / 74 / 87；DINO-WM 74 / 79 / 86 / 100；PLDM 78 / 78 / 65 / 97 | 无单一冠军，四个环境上的排名互不一致；跨表读会碰到反例——DA-LeWM 自家 Table 1 里 LeWM 一 epoch 的 TwoRoom 98.0 就高于 DA-LeWM 十 epoch 的 96.0。已发表数字与同预算复跑混排是这套基准的主要口径风险 |
| **RoboMemArena** | Benchmark | 12 任务（本文采用的协议） | CSR（累计阶段成功） / TSR（任务成功） | [[Papers/2608-HyMeS\|HyMeS]] 66.2 / 60.1（π0.5 52.5 / 41.3） | 按遮挡、计数等类别分组，能暴露"预测式记忆在某些类别上是净损"——PrediMem 遮挡类 CSR 38.3 低于纯反应式 π0.5 的 50.4；12 任务协议为该文自定，与 PrediMem 发表的 26 任务口径不可比 |
| **SIMPLER / SimplerEnv** | Benchmark | WidowX + GoogleRobot 的真机对齐仿真评测 | Success Rate | [[Papers/2608-WorldTokens\|World Tokens]] WidowX 71.5 / GoogleRobot 82.1；Bridge 四任务 [[Papers/2608-GalaxeaG05\|G0.5]] 87.3（次优 Xiaomi-Robotics-0 79.2，G0.5 摘要只引 π0.5 的 57.1） | 各文所取任务子集与训练数据不同——World Tokens 用 BridgeV2+Fractal 训练，[[Papers/2608-InContextVLA\|In-Context VLA]] 报 4 个 held-out WidowX 任务均值 72.4 且其中 Carrot 一项 56.3 低于四个基线——跨论文分数不可比；专题一表内同名行的 56.2%（Embodied-R1）取自另一套任务子集 |
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
- 从检查显式指令是否被实现，到考察指令未写明、但可从初始场景推出的后果（[[Papers/2608-WorldExam|WorldExam]] 的 World Reactivity 层只给触发控制，把该发生的反应留空）
- 在"世界是否反应"之前再加一层"动作是否被忠实实现"（[[Papers/2608-WorldSimProbe|WorldSimProbe]] 的 Observable Simulator Contract），并把 judge 的判定规则本身当作必须报告的实验条件——同一批 rollout 上 VLM 二元 action-following 判断判正 91.7%，人工只判 42.2%
- 鉴别力可以靠换轨迹分布而非换任务取回：用同一批 ACWM 生成的数据训 policy，standard 轨迹下成功率挤在 78–86% 分不开，OOD 轨迹下分离成 53 / 34 / 21%
- 反向趋势：主力 suite 的鉴别力在下降。LIBERO 上语言指令可被 task-ID 近乎无损替代、RoboTwin 2.0 已进 92-94% 饱和区，"更强"的边际证据越来越薄
- 同一基准名下已经流通多套聚合口径，引用必须带版本与快照日期：WorldArena 2.0 用 ground truth 给三项分量设上限后，同一模型的两项分量从 WA1.0 的 88.71 / 100.00 变成 22.90 / 5.81，而两篇论文记录的同名条目 EWMScore 相差 3.5–3.7、Trajectory Accuracy 却完全一致（[[Papers/2608-DreamXPhi|DreamX-Phi]] 与 [[Papers/2607-FlowWAM|FlowWAM]]）
- 与基准无关、只与报告方式有关的第二类失真同样常见：选择规则不对称（[[Papers/2608-SpatialMemoryAgent|SMA]] 每个数字取 10 次 pass 的 best checkpoint，baseline 无同等规则）、指标本身偏向条件复制（[[Papers/2608-Hydra0|Hydra-0]] 的 gripper EPE 上零样本模型比微调基线低一个数量级）、摘要口径窄于正文（[[Papers/2608-Zetta|Zetta]] 的 90.8% 对全量 71.13%）
- 但鉴别力未必是消失，可能只是被 canonical 模板掩盖：LIBERO-Para 只改写措辞就把同一批模型从 72-98% 打回 4-77%（[[Papers/2608-GSRParaVLA|GSR]]），说明"换一套指令表述"这一最低成本的扰动即可重新拉开差距。饱和区的正确读法是评测协议过窄，而非任务已被解决

---

## Key Takeaways

1. **VLA Foundation Model 已成为主流范式**：RT-2 证明 web-scale VLM knowledge 可直接迁移到 robot policy，RT-X 建立 cross-embodiment training 的 positive transfer 现象，OpenVLA 开源生态使研究门槛大幅降低。

2. **Diffusion Policy 是 action generation 的有效方法**：Multimodal action distribution modeling 解决 BC 的 mode collapse，在 manipulation tasks 上广泛验证。SeedPolicy 的 SEGA module 解决 long-horizon observation 压缩瓶颈。

3. **VLM→VLA 迁移需要 data alignment 与表征保持**：EmbodiedMidtrain 发现 VLA data 与 VLM distribution 存在显著 gap；[[Papers/2606-Act2Answer|Act2Answer]] 进一步测得 robotics 微调使语义类知识掉 20-40 分（知识中层仍可解码、动作头读不出——问题在读出通路），[[Papers/2607-AnchorAlignVLA|Anchor-Align]] 证明 frozen VLM 锚定可低成本修复且不牺牲动作性能——防遗忘机制（co-training / anchoring）应成 VLA 训练默认件。

4. **World Model 已分化出五种角色并成为 competitive policy 范式**：policy（WAM：[[Papers/2607-ABotM05|ABot-M0.5]] / [[Papers/2607-FlowWAM|FlowWAM]] 在 RoboTwin 2.0 超纯 VLA）、训练期表征塑造（[[Papers/2608-WorldTokens|World Tokens]] / [[Papers/2608-JEPAWAM|JEPA-WAM]] / [[Papers/2608-MobileWAM|MobileWAM]] 让未来分支只经梯度起作用、推理时整体删除）、planner（[[Papers/2607-WorldActionPlanner|WAP]] 把 policy 降级为工具，compositional LIBERO-Long 72 对 π0.5 的 4；[[Papers/2606-PointWorld|PointWorld]] 干脆不要 policy，由 MPPI-MPC 直接在 3D point flow 的预测动力学上求解）、数据引擎（[[Papers/2607-RynnWorldTeleop|RynnWorld-Teleop]] 数字遥操作）、policy evaluator（[[Papers/2607-GigaWorld1|GigaWorld-1]] evaluator-world agreement）；代价是推理开销与新攻击面（[[Papers/2607-BadWAM|BadWAM]] 的 action-imagination 解耦）同步出现。planner 与 evaluator 两个角色消费的是判别能力，而 [[Papers/2607-PhiZero|Phi-Zero]] 表明生成保真度不蕴含判别正确性——这两条路线不能靠视频质量指标验收。[[Papers/2608-WorldExam|WorldExam]] 把这条判断扩到跨范式 20 个模型：language-driven 一族的视觉质量均值只跨 79.64–81.04，同族任务均值却从 39.85 铺到 65.02；其反应类任务的典型失败（被接触物体不变、主体穿过去）与 [[Papers/2607-GigaWorld1|GigaWorld-1]] 的 contact-sensitive optimistic bias 出自不同团队、数据与评测目标，却落在同一处环节。这处失效的**方向**则记为争议：[[Papers/2608-WorldSimProbe|WorldSimProbe]] 在 simulator 验证过的无接触场景里做的 audit 是 50/50 全为 contact hallucination、无一例 omission，与 WorldExam 记录的 omission 相反，而两个基准的 case 构造决定了各自只能看见一半（前者只罚编、后者只罚漏）。能保留的共识止于"contact 是共同失效环节"；对下游的含义则相反——漏接触让 planner 低估后果，编接触让 evaluator 高估成功。planner 角色还有第二个独立的必要条件：[[Papers/2608-DALeWM|DA-LeWM]] 把"latent 是否编码了任务量"与"latent 之间的距离能否把候选按真实进展排序"拆成两条逻辑独立的性质，并给出四个 probe R² 只差 0.03 而在线成功率相差 43pp 的对照——表征探针测不出可规划性。而这些角色各自消费什么坐标的动作，眼下是开放分歧：optical flow、3D point flow、图像平面稀疏点轨迹、每臂 SE(3) 相对变换、与语言共享词表的离散码，五种接口之间没有任何交叉实验（路线 3）。

5. **RL 正从 imitation 走向 true policy optimization**：LongNav-R1 的 multi-turn RL + horizon-adaptive advantage 证明 trajectory-level optimization 比单步 SFT 更适合 long-horizon tasks；[[Papers/2607-REAL|REAL]] 补充了 BC 过拟合的直接观察（SFT 第 2 epoch 在开放词表 split 倒退、RL 修复并超越）。

6. **安全与可靠性开始被系统性关注**：VLA Safety Survey 定义了新问题域——VLA 的不可逆物理后果、多模态攻击面、实时约束带来区别于 LLM safety 和 classical robotic safety 的 unique challenges；[[Papers/2607-BadWAM|BadWAM]] 补充 WAM 特有的 world-action drift 威胁，[[Papers/2607-RobustExecAgenticRL|RobustExec]] 给出 runtime 执行监控 + 回滚恢复的廉价方案（proprioception-only 指标，无需 VLM）。同一结构正在往代码空间迁移：[[Papers/2608-Zetta|Zetta]] 把监控者换成离线 agent 写出的 critic 代码，逐 action chunk 判定并按 re-entry contract 切出/交还 VLA，从而把可靠性开销与 policy 推理开销解耦（对照的 RPent 每决策点调一次 LLM，392–513 s/episode）。冻结 GR00T N1.5 在 RoboCasa 从 73.56% 到 93.56%、冻结 π0.5 在 LIBERO-Pro 从 32.00% 到 71.13%，但增益归因未被隔离——无 ablation 章节，两张表里唯一的非 Zetta 行就是自家基座，且 baseline 拿不到额外执行步数、bounded retry 与外部工具。可带走的是 formulation 而非百分点。

7. **数据瓶颈的答案正收敛到 human/手持视频 + 强 curation + 可部署 fidelity**：[[Papers/2607-EgoSteer|EgoSteer]]（9.6K 小时 egocentric，scaling log-linear）与 [[Papers/2607-XiaomiRobotics1|Xiaomi-Robotics-1]]（100K+ 小时 UMI，data scale 边际收益大于 model size）给出 data scaling 直接证据；[[Papers/2607-HiFiUMI|HiFi-UMI]] 则表明 3 mm pose、原生双夹爪相对位姿、硬件同步与 wide FoV 的联合 fidelity 足以让 UMI 承担 target-task post-training。跨工作共同点不是“任意视频都可用”，而是 curation、表示一致性与 capture fidelity 共同构成数据引擎。

8. **实时性与能力未必互斥，但现有 benchmark 对二者都在丧失鉴别力**：[[Papers/2607-TurboVLA|TurboVLA]] 移除 LLM 后以 0.2B / 32 Hz 在 LIBERO 拿到 97.7%，同时自证 LIBERO 的语言条件近似闭集分类（task-ID 替换仅 −2.3pp）；[[Papers/2607-PhiZero|Phi-Zero]] 在生成类物理 benchmark 领先而在 IntPhys2 Hard 接近随机。两处的共同含义是，饱和或低鉴别力的评测让"更快"与"更懂"都难以证伪；效率与物理理解的下一步进展，前置条件是先造出能区分它们的评测，而不是继续在现有 suite 上刷分。LIBERO-Para 给出了造这类评测的一个廉价样板——不动物理任务、只改指令措辞，就把同一批模型从 72-98% 打回 4-77%（[[Papers/2608-GSRParaVLA|GSR]]）；但它自身也划出边界：LIBERO-Goal 的 10 个任务共享同一视觉场景，它测出的是 paraphrastic invariance，仍不足以把"语言条件化"与"任务索引"分开。

9. **VLA 的语言鲁棒性首先是架构问题，不是数据问题**：[[Papers/2608-GSRParaVLA|GSR]] 用因果干预把失效位置定位到动作策略对 joint vision-language 编码漂移的敏感性——任务语义在语言主干里保留完好（Retrieval@1 0.941 / 0.675 / 0.516，chance 0.1），只替换最后一个融合 block 的语言特征即消除 96.8% 的动作差异；把指令语义改由一条不看图像的冻结文本编码器承担，只用 canonical demonstration 就把 SmolVLA 的 Full Para 从 4.47 提到 49.12。竞争解释（容量、多一个语言编码器）被三个落在同一数值上的对照排除。适用范围须同时记住：全部仿真证据来自 10 任务共享场景的闭集设定，且无统计区间与多 seed，因此这条结论支持的是"扩数据不是唯一解"，不是"语义泛化已被解决"。同一批现象还有第二种定位在竞争：[[Papers/2608-CofactVLA|CofactVLA]] 把病因写成 latent visual confounder 经 backdoor path 绕过语义意图直接决定动作，靠推理期的反事实分支做减法拿到零样本 LIBERO-Plus 69.1 与真机 OOD 75.8 对 π0.5 的 23.5。两者的证据强度并不对称——GSR 有行为层探针与因果干预直接支持其定位，而 CofactVLA 的 backdoor 假设全程未被经验检验，且其最弱的一列恰好是 Language（71.8，低于 OpenVLA-OFT_m 的 81.0）。最小鉴别实验是把 GSR 的行为层 Retrieval@1 探针搬到真机 OOD 设定下重跑。

10. **触觉进入 VLA 已成事实，但"预测式触觉"的收益归属未定**：[[Papers/2607-N0VTLA|N0-VTLA]] 把触觉做成预测目标并给出可信的表征探针（latent `z` 在 32 候选池 top-1 92.3，chance 3.2），[[Papers/2607-N0TWAM|N0-TWAM]] 的消融却显示去掉**反应式** observed 通路比去掉**预测式** predicted 通路损失更大，且最大单因素是预训练数据量而非任何触觉设计；N0-VTLA 自己的 ALTER 结果也显示 offline RL 是主导项、触觉预训练是二阶项。两篇同团队、共享私有数据与基准，本 survey 记为争议而非共识。与路线 3 的 [[Papers/2607-STWAM|ST-WAM]]（新增 DINO 未来分支，单独使用反而低于纯 VAE 基线）合看，2026-08 的两组证据指向同一个方法论问题：**给模型加一条"预测更多模态/更多表示的未来"的通路时，增益常常不来自"预测"这一半**。

11. **"训练期消费、推理期删除"跑通了，而收益归接口形状、不归"预测未来"本身**：[[Papers/2608-WorldTokens|World Tokens]]、[[Papers/2608-JEPAWAM|JEPA-WAM]]、[[Papers/2608-MobileWAM|MobileWAM]] 三组各自采用同一模板——用注意力掩码或冻结目标切断 action 对未来 token 的可见性，使未来分支在部署时不实例化，推理开销退回到不含该分支的水平（61.85 ms 在 π0.5 的 1.1× 以内、85 ms 对 ABot-M0 的 125 ms、938 ms 对同类 WAM 的 4950/8126 ms）。三者的消融合起来给出比成功率更硬的读数：同一条预测通路的效果可以从净损摆到显著增益，取决于监督如何接进主干——World Tokens 把 world token 从排他上下文改成可旁路即 97.0→94.1（低于完全不做 world modeling 的 95.0），首帧锚点由 Canny 换成 RGB 更掉到 91.5；JEPA-WAM 取 backbone 全部隐藏层 73.1 低于只取 Lower-16 的 76.5；MobileWAM 把递归模块从 transformer 换成 MLP 得 46.3，低于完全不加 foresight 的 50.2，tap 层从均匀 4 层改成全部 30 层则 58.2 崩到 37.1。这与 #10 互补：不控制接口形状而报告"加了未来预测所以更好"，在当前证据下不构成有效归因。三篇各出自一个团队、主基准两两不重合、无交叉复现，消融均在各自 in-domain 设定内完成。被删掉的也不限于"未来"这一种东西：[[Papers/2608-StellaVLA|StellaVLA]] 把检索来的示范前缀与语言化的空间推理挂在一条只活在训练期的自回归分支上，推理时整条语言分支摘掉、示范前缀的 KV 缓存复用，单步从推理期联合解码语言的 3177 ms 回到 91 ms（约 36×）。代价是依赖被换到了检索端——去掉示范 LIBERO 从 98.8 掉到 62.4，给错任务的示范掉到 44.9，而同表的 StarVLA-OFT 在无示范设定下是 96.6。

12. **"VLM 编码器 + 独立动作专家"不再是唯一可行的 foundation 配方**：[[Papers/2608-GalaxeaG05|Galaxea G0.5]] 让单个 transformer decoder 在共享 token vocabulary 上以单一 next-token cross-entropy 同时产出 CoT 与离散动作码，在同数据、同算力、同控制栈的真机微调上拿到 76.7%，对照 π0.5 的 53.3% 与 GR00T-N1.7 的 24.4%；2025 BEHAVIOR Challenge 上 1 个 post-training epoch（0.2904）即超过四 checkpoint 的冠军方案（0.2605）。让这条路在 foundation 规模上可行的是三个组件而非架构本身——跨本体 RVQ action tokenizer（27 维统一动作空间 + active-part 预测）、原生 CoT 流、ViT 内插的 factorized spatio-temporal visual memory；单条自回归流带来的结构性红利也很具体：CoT 可在推理期换成本换收益、GRPO 无需改架构即可接入、零样本指令跟随有语言先验兜底。但它的区分度只在真机、BEHAVIOR 与 DROID 三个 regime 上成立，LIBERO 对次优 +0.2pp、RoboTwin 2.0 +1.1pp 都落在饱和带；原文"零样本指令跟随超过 post-train 过的 π0.5"这句与自家 Fig 10 相反（π0.5 在 50H post-training 下 68.8% 高于 G0.5 零样本 65.6%），本 survey 不采纳该表述；低对比度与半透明物体上 60% 对 π0.5 的 90%；模型只训了 2B 一个尺寸，无 scaling 证据。

---

## Open Problems

### 核心技术挑战

1. **Sim-to-Real Gap 的系统性解决**：尽管 domain randomization、adversarial training 有进展，但真实世界的 lighting variation、material diversity、dynamic obstacle 等仍难以完全模拟。需要更 robust 的 sim-to-real transfer framework。

2. **Dexterous Manipulation 的精度瓶颈**：VLA 在 coarse manipulation（pick-and-place）表现良好，但 fine-grained dexterous manipulation（如 tool use、precision assembly）仍不如 specialized methods。

3. **Long-Horizon Credit Assignment**：Multi-step tasks 中 reward 稀疏，LongNav-R1 的 horizon-adaptive advantage 是有价值的尝试，但 generalizable solution 仍需更多验证。

4. **Real-Time Inference Constraint**：VLA 模型推理开销大，diffusion policy 需要 multiple denoising steps。如何在保持 policy quality 的同时满足 sub-second latency 是 deployment bottleneck。WAM 路线加剧此矛盾——每次出 action chunk 需跑 5B 级视频去噪（RynnWorld-4D 890ms 前向 / 9Hz），且多数 WAM 论文回避报告 latency（FlowWAM）。反向证据来自 [[Papers/2607-TurboVLA|TurboVLA]]：完全不含 LLM 的 V+L→A 架构以 0.2B / 32 Hz 在 LIBERO 与 RoboTwin 2.0 保持竞争力，说明至少在闭集任务分布上 latency 与成功率不构成硬 trade-off。真正未解的是开放指令与 OOD 条件下这一 trade-off 是否重新出现——该文没有相应实验，问题从"能不能又快又准"变成"快的代价落在哪类泛化上"。WAM 侧的部分答案已经出现：把 world modeling 降为训练期信号、推理时删除未来分支，可以把开销压回不含该分支的水平（[[Papers/2608-WorldTokens|World Tokens]] 61.85 ms、[[Papers/2608-JEPAWAM|JEPA-WAM]] 85 ms、[[Papers/2608-MobileWAM|MobileWAM]] 938 ms）。但这条答案是有代价的——推理期的想象、搜索与重规划一并被放弃，planner 与 evaluator 两个角色不能这样做；剩下的问题是"训练期塑造的表征"能否替代"推理期的显式前瞻"，目前没有任何工作在同一任务上直接对比这两种用法。同一 trade-off 的第三个落点是语言分支本身：[[Papers/2608-StellaVLA|StellaVLA]] 若在推理期联合解码语言，单步 3177 ms；把整条语言分支摘掉、只留它在训练期塑造出的动作表征，回到 91 ms（示范前缀 KV 缓存复用），代价约 36×。这与路线 1 的三行对照（生成并监督文本 / 注入但对证据计 loss / 注入且只监督 action token）指向同一个量——推理期生成文本的开销与它带来的动作增益至今没有在同一 backbone 上被正面核算过。

### 数据与评测挑战

5. **高质量 Robot Demonstration 的获取成本**：Teleoperation data 质量高但收集成本高；autonomous collection 需要成熟 policy。Human 视频与手持采集路线（EgoSteer / Do as I Do / Xiaomi UMI / HiFi-UMI）已给出部分答案，但瓶颈从“有没有数据”转移到 curation、fidelity specification 与验证：在线视频仅 ~5% 直接可用于灵巧学习；HiFi-UMI 的 parity 依赖约十倍 task-specific trajectory 数且没有逐因素 ablation。下一步需要固定 sample count 与 scene coverage，正交降级 pose、synchronization、relative-pose 与 FoV，才可形成可迁移的 deployment specification。

6. **Cross-Embodiment Morphology Gap**：RT-X 展示 positive transfer，但不同 robot 的 kinematics、dynamics、action space 差异仍限制 transfer efficiency。如何设计更 universal action representation？候选正在收敛：相机系相对 state-action（EgoSteer）、end-effector delta pose（Xiaomi-Robotics-1）、optical flow（FlowWAM）、frame-level latent action（ABot-M0.5）、由 URDF 经正向运动学生成的 3D point flow（[[Papers/2606-PointWorld|PointWorld]]，每个 gripper 约 300–500 点，state 与 action 落在同一空间因而与关节数、自由度、夹爪构型脱钩）——共同点是 embodiment-agnostic 的中间表示，但无定论。PointWorld 还给出一个反直觉的方向性证据：gripper-only flow 优于 whole-body flow，说明这类表示的收益不随建模点数单调增长；其未闭合处在于主指标是 ℓ2 flow error 而非任务成功率。2026-08 又添了三种互不兼容的取法：图像平面上的稀疏点轨迹（[[Papers/2608-Hydra0|Hydra-0]]，N 条轨迹 × H+1 个像素位置 + 可见性，几何路线由 URDF 投影生成、纯视频路线由 tracker + 分割掩码分配）、按注意力头分组注入的每臂 SE(3) 相对变换（[[Papers/2608-DreamXPhi|DreamX-Phi]]，把 PRoPE 的相机位姿换成末端执行器位姿，夹爪开合作为 per-arm bias）、与语言共享词表的 RVQ 离散码（[[Papers/2608-GalaxeaG05|G0.5]]，27 维统一动作空间 + active-part 预测）。这是分歧扩大而非收敛：五种接口之间没有任何交叉实验，且各文对"哪一路信息更重要"的方向性结论互相矛盾——PointWorld 报 gripper-only 优于 whole-body，Hydra-0 的 gripper EPE 被证明主要测条件复制，DreamX-Phi 则把 optical flow 从主通道降为两条互补通道之一。现有指标还不中立，所以连一个能把这些接口排序的公共评测都尚不存在。

7. **真实环境评测的覆盖率与鉴别力**：Benchmark 多在 simulation 或特定 lab setup，缺少真实 home/factory/outdoor 环境的 systematic evaluation。Safety-critical scenario testing 几乎空白。World model surrogate 评估（GigaWorld-1 / WMBench）提供低成本替代路径，但对 contact-sensitive failure 的 optimistic bias 未解——false-success 会系统性放行危险 checkpoint，false-success rate 应成必报指标。覆盖率之外还有鉴别力：LIBERO 上把语言指令换成 task-ID embedding 只掉 2.3pp（[[Papers/2607-TurboVLA|TurboVLA]]），意味着它主要测闭集任务执行而非语言理解，"语言条件化"类方法的收益在其上无法被验证；物理侧同构——生成类指标（Physics-IQ）与判别类指标（IntPhys2 Hard）在 [[Papers/2607-PhiZero|Phi-Zero]] 上给出相反排序，而 [[Papers/2608-WorldExam|WorldExam]] 给出同规模证据：language-driven 一族的视觉质量均值只跨 1.4 分（79.64–81.04），任务均值却跨 25 分（39.85–65.02），用 FVD / aesthetic 类指标论证 world model 质量在这份数据里没有支撑。需要的是带 held-out 指令改写、未见物体与显式判别项的评测设计。其中"指令改写"这一项已被 LIBERO-Para 做出来（4,092 条改写 episode，物理任务与成功判据不变，同一批模型从 72-98% 回落到 4-77%），证明这类协议成本极低且立刻恢复鉴别力；仍缺的是未见物体、新动作、新组合与显式判别项——而 LIBERO-Goal 的 10 个任务共享同一视觉场景这一事实，使它连"语言条件化 vs 任务索引"都还分不开。[[Papers/2608-WorldSimProbe|WorldSimProbe]] 在 world-model 侧给出两条可直接照搬的做法。其一，换评测轨迹分布而非换任务就能恢复鉴别力——同一批 ACWM 生成的数据训 policy，standard 轨迹下成功率挤在 78–86% 分不开，OOD 轨迹下分离成 53 / 34 / 21% 且与 probe 排序一致。其二，judge 的判定规则必须作为实验条件报告：750 个人工标注 rollout 上，基于光流的 RMFA 与人工分级 ρ=0.750，VLM 二元判断只有 0.450（VLM 判 91.7% 的样本"动作被跟随"，人类 42.2%），而 [[Papers/2608-WorldExam|WorldExam]] 那条"无法核实一律记为不满足"的保守规则会把同一批结果推向相反方向。VLA 侧的评测预算问题同样具体：[[Papers/2608-CofactVLA|CofactVLA]] 的 LIBERO 每 suite 10 episodes、LIBERO-Plus 每任务 1 episode、无 seed 与误差棒，这种预算下 98.5 与 98.2 之类的差距不可解释；而它在真机 OOD 上把 π0.5 的逐任务 0/25/29/40 收窄到 67–83，说明被改善的主要是失败方差而不只是均值——把逐任务分布连同均值一起报告，是比再加一个任务更便宜的鉴别力来源。第三层问题落在基准之外的报告约定上：同一基准名下已经流通多套聚合口径——WorldArena 2.0 用 ground truth 给三项分量设上限后，同一模型的两项分量从 88.71 / 100.00 变成 22.90 / 5.81，而两篇论文记录的同名条目 EWMScore 相差 3.5–3.7、Trajectory Accuracy 却完全一致（[[Papers/2608-DreamXPhi|DreamX-Phi]] 与 [[Papers/2607-FlowWAM|FlowWAM]]）；报告方式本身也能制造领先幅度——best-of-10 选择只施于自家行而 baseline 无同等规则（[[Papers/2608-SpatialMemoryAgent|SMA]]）、摘要取有利子集（[[Papers/2608-Zetta|Zetta]] 的 90.8% 对全量 71.13%）、指标偏向条件复制（[[Papers/2608-Hydra0|Hydra-0]] 的 gripper EPE 上零样本模型比微调基线低一个数量级）。最低要求是引用 leaderboard 分数时带版本与快照日期，并把选择规则是否对称写进表注。

### 安全与部署挑战

8. **VLA Certified Robustness**：Adversarial attack 防护需要理论上可证明的 robustness bound，但 VLA 的 multi-modal input space 和 continuous action space 使 certified defense 困难。BadWAM 新增 WAM 特有攻击面：action 与 imagination 的同步性本身需要防护，"检查生成未来是否合理"不构成安全保障。

9. **不可逆操作的风险控制**：Physical operation 一旦执行难以撤销。如何设计 safety-aware policy、runtime monitor、emergency intervention mechanism？RobustExec 的 {Execute, Retry, Repair, Reset} 调度是一次尝试，但回滚只恢复机器人不恢复世界状态，不可逆失效（液体、易碎物、物体位移）仍无解。

10. **开放场景的 Language Understanding**：用户指令可能模糊、不一致或超出 robot capability。如何 robustly parse and ground natural language in physical context？目前的位置比预想的靠后——连"同义改写"这一最弱的语言变化都尚未解决（主流 VLA 在 LIBERO-Para 上掉 19-68pp），而 [[Papers/2608-GSRParaVLA|GSR]] 的诊断表明瓶颈不在语言理解本身，而在动作策略与 joint V-L 编码之间的信息路由。这意味着"模糊指令""个性化偏好"这类更高阶目标的前置条件，是先把措辞不变性做成架构性质而非数据性质。

### 归因与评测基础设施挑战（2026-08 新增）

11. **新增预测通道的增益来自哪一半**：WAM 路线正在往"预测更多东西"的方向扩（[[Papers/2607-STWAM|ST-WAM]] 的 DINO 未来、[[Papers/2607-N0TWAM|N0-TWAM]] 的触觉未来），但两篇的消融同向显示新增的预测通路不是主要收益来源——ST-WAM 的 DINO Future Only 在 LIBERO-Plus 只有 39.7、低于纯 VAE 基线的 51.5；N0-TWAM 去掉反应式 observed 通路的损失大于去掉预测式 predicted 通路。需要的对照是**同 backbone、同算力、逐预测目标移除**，并配以非 appearance 级的扰动集——否则"多预测一种未来 → 动作更好"这条推论无法与"多引入一种表征/多一路条件输入"区分。[[Papers/2608-VLAProprioception|VLAProprioception]] 已给出这类对照的一个现成模板：固定图像、语言、条件槽位数、专家动作与初始噪声，只把有序历史替换成当前帧的重复副本，从而只抽掉时间变化本身（composite 30.8 对 39.0，配对区间排除 0）。同样的 slot-matched 构造可直接搬去审计任何"多喂一路信息所以更好"的 VLA / WAM 消融——把新增信息的**内容**与新增的**条件容量**分开，本就是这类 claim 的最低举证要求。这个问题已从"缺少对照"推进到"部分答案在手"：[[Papers/2608-WorldTokens|World Tokens]]（排他路由 97.0 / 可旁路 94.1 / 不做 world modeling 95.0 / RGB 锚点 91.5）、[[Papers/2608-JEPAWAM|JEPA-WAM]]（joint 79.2 / future-only 77.3 / 仅当前帧表征 77.0 / Lower-16 76.5 / 全隐藏层 73.1）与 [[Papers/2608-MobileWAM|MobileWAM]]（串行 58.2 / 并行 52.3 / MLP 递归 46.3 / 不加 foresight 50.2 / 全 30 层 37.1）都在同 backbone 同数据下只改接口，结果是"预测未来"的净效应可以为负，真正的自变量是排他性、目标是否保留空间对应、取层位置与递归容量。仍缺的是跨这三种接口的统一对照——三篇各在自己的基准上做，没有任何一组把它们放进同一实验。2026-08 的负面样本同样集中：[[Papers/2608-DreamXPhi|DreamX-Phi]] 自陈没有做任何匹配消融（PRoPE、robot-only flow、depth 分支、SAM3 掩码重加权、V-JEPA 关系对齐、DMD 蒸馏一项都未隔离），于是"结构化几何接口优于 tokenized 接口"只有整机 leaderboard 排名作支撑；[[Papers/2608-Zetta|Zetta]] 三条 loop 一条都没单独消融，也没有 budget-matched 对照。正面模板来自 [[Papers/2608-DALeWM|DA-LeWM]]：SIGReg 移除带来的崩塌对照（latent 动态范围 3–30× 压到约 1.005×、在线成功率 49.3→2.0、state probe R² 掉到 −6.14）把"辅助 loss 是不是真的在起作用"变成可证伪的。但它也划出这类纪律的上限——它自己的两个诊断都解释不了主要增益：inverse-only 变体的 Plan-Real Spearman 最高（+0.420，30/30 全正）却只有 64.0% 成功率，而 CEM elite 阶段所有变体的 Spearman 都在 0 附近（+0.036 / −0.089 / −0.011）。

12. **触觉路线的评测基础设施几乎不存在**：现有触觉 VLA 证据的八个基准中只有 UniVTAC 是第三方公开基准，其余数据集、仿真器、真机套件与力觉编码器均出自同一公司的网页报告，一手出处不可独立核查；真机普遍 20 trials/task 量级（binomial SE 可达 ±11%），且缺同 checkpoint 的触觉关断对照。在这套条件下，"触觉带来多少增益"这个问题在库内无法被证伪。

13. **可规划性还没有可部署的诊断**：把 latent world model 当 planner 用时，"latent 是否编码了任务量"与"latent 之间的距离能否把候选按真实进展排序"是两条逻辑独立的性质，而常用的线性 probe 只测前者——[[Papers/2608-DALeWM|DA-LeWM]] 的四个未崩塌变体 probe R² 互差不超过 0.03，在线成功率却铺开 43pp（49.3 到 92.7）。它提出的两个替代诊断都要求对每个候选做 simulator rollout（Plan-Real 相关性是每对 (start, goal) 采 64 个候选 × 30 对，CEM 阶段诊断是 15×300×30），在真机上不可得；评测 goal 又取自 held-out demonstration 的固定偏移，保证了目标在分布内且可达。于是"这个 latent 能不能拿来规划"眼下只能靠把规划跑一遍来回答，没有更便宜的前置判据——而这恰是 planner 与 evaluator 两个角色（Key Takeaway #4）往真机扩时最先缺的工具。

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

- **[[Papers/2608-InContextVLA|In-Context VLA]]**（2026，反向对照）：把"生成推理"换成"注入证据"——空间线索由只读感知工具链产出、以 `<spatial>` 标签注入 prompt，policy 不再自己说出推理链。同 backbone 同证据的三行对照拉开 15.9 分：生成并监督文本 81.5%（延迟 4.6×）、注入但仍对证据计 loss 89.7%、注入且只监督 action token 97.4%。另一条反向读数是把工具链换成模型自猜，84.3% 反低于同表 backbone 的 90.4%——证据不可靠时比不给证据更差。详见路线 1。

优势：可解释、支持人工干预、推理结构可泛化。劣势：固定步骤不灵活、额外延迟、依赖复杂数据生成 pipeline；"让 policy 生成推理链"这一步本身是否贡献增益，在同 backbone 同证据的对照下未得到支持（In-Context VLA），可解释性与成功率增益需要分开论证。该对照的边界是其 Gen-CoT 为自建基线且在每个数据预算上都跑不过纯 BC，最小检验是拿已发表 CoT-VLA 权重在同 backbone 同数据上重训后再比。

### A2. RL-based Embodied Reasoning（GRPO 范式）

- **[[Papers/2506-RobotR1|Robot-R1]]**（NeurIPS 2025）：next-state prediction 重构为 MCQ 降低探索复杂度，7B 超 GPT-4o；SFT 0% vs RL 11.68%。
- **[[Papers/2504-EmbodiedR|Embodied-R]]**（2025）：解耦 perception (72B VLM) 与 reasoning (3B LM)，logical consistency reward；3B 超 OpenAI-o1 / Gemini-2.5-Pro，仅 5,000 样本。
- **[[Papers/2508-EmbodiedR1|Embodied-R1]]**（2025）："pointing"（2D 坐标）作 embodiment-agnostic 中间表示，两阶段 GRPO；3B 超 7B-13B baselines（65.50% vs SFT 41.25%）。
- **[[Papers/2512-ETPR1|ETP-R1]]**（2025）：GRPO 首入 graph-based VLN-CE，R2R-CE 65% SR。
- **[[Papers/2607-BRAID|BRAID]]**（2026）：把 GRPO 范式扩展到交错「文-图-文」推理——两层 MDP 使同一 trajectory advantage 同时驱动文本 token（GRPO）与图像去噪路径（DiffusionNFT），7B UMM 在 7 个 spatial/perception benchmark 平均 +5.73、反超 GPT-4o；无具身执行环节，但为"生成中间图像辅助空间思考"（mental imagery）提供了 RL 可训的首个证据，与本专题 Open Problem 5（reasoning × world model）交汇。注意其收益偏向"找细节/放大 ROI"（CV-Bench 3D 反而 −1.24），且 reward 依赖 GPT-5.2 judge。

- **[[Papers/2608-SpatialMemoryAgent|SMA]]**（2026，范式外对照）：不更新任何参数——在带 ground-truth verifier 的 environment split 上把每次 rollout 反思成一条 transferable lesson 写入外部 memory bank，每条 lesson 带一个由后续检索结果校准的 Transfer Reliability Score (TRS)，deployment 时按 semantic filter + (相似度, TRS) 排序取 top-3 注入 prompt。5 benchmark × 4 冻结 VLM 的主表上每个 base-model block 的 macro average 最高，较最强非 SMA baseline +1.7~+2.9。

SMA 把这一格的问题换了个提法。它的 environment split 就是目标 benchmark 的另一半（per-category 50/50，带 verified answer 与 verifier reward），所以它省掉的是梯度更新而非同分布标注，真正的对比轴是"同样的标注数据，写进权重还是写进外部文本"。最有信息量的一处不在主表：相对纯相似度检索的 MemP，SMA 把检索卡片的平均相似度从 0.792 **降到** 0.698，macro accuracy 却从 66.8% 升到 69.8%，且每个 benchmark 方向一致——最近邻不等于最有用。但主表不能按 selection-matched 读：每个 SMA 数字取自 10 次 pass 的 best checkpoint（Appendix C.6 的 Pass 值在 2–10 间无规律跳动），全文没有任何一处说明 baseline 享有同等选择规则；deployment split 最大的两个 benchmark（SITE-image 2224、ViewSpatial 2856）被放进附录，MemRL-GT 在 ViewSpatial 上两次反超。与 training-based 方法的 63.5 vs SpatialEvo-7B 47.1 跨了 backbone 世代——同一 Qwen3.5-9B 在 no-memory 下已经是 60.6。消融把 semantic filter 排在最大贡献项（RoboSpatial −5.8、Omni3D −7.2），而 TRS 权重只有 sensitivity sweep、没有 η=0 的对照行，因此 TRS 相对纯相似度检索的净贡献在表里是缺失的；token / latency 开销全文未核算。

**核心发现：RL 系统性优于 SFT**（三篇独立一致）；小模型 + targeted training > 大模型 + 弱训练。劣势：绝对成功率仍低（Robot-R1 11.68%）、多在仿真验证、MCQ 离散化丢失精细空间信息。这条结论的对照面是 SFT 而不是"不训练"：SMA 在冻结权重上只靠外部 memory 拿到同量级的 macro 增益，说明"提升必须写进参数"这个前提从未被单独检验过，缺的是同标注预算下 RL、SFT 与外部记忆的三方对照。

### A3. Data-Centric Embodied Reasoning

- **[[Papers/2401-SpatialVLM|SpatialVLM]]**（CVPR 2024）：10M 真实图像自动生成 20 亿 metric-space 空间 VQA。
- **[[Papers/2601-Thinker|Thinker]]**（IROS 2025）：4.8M robotics-specific 数据集，10B 超 32B baselines。
- **[[Papers/2510-VLASER|VLASER]]**（2025）：**OOD reasoning data 几乎无法迁移到 VLA performance，in-domain reasoning data 才是关键驱动力**——embodied reasoning 的 domain gap 远大于 NLP。

### A4. Explicit Spatial Representation for Reasoning

- **[[Papers/2602-GTA|GTA]]**（2026）：TSDF + topological graph 的 interactive metric world representation + counterfactual reasoning/ray-casting，SPL +16.4。
- **[[Papers/2601-SpatialNav|SpatialNav]]**（2026）：层级 Spatial Scene Graph（floor→room→object），zero-shot VLN 64.0% SR ≈ supervised SOTA。
- **[[Papers/2603-PROSPECT|PROSPECT]]**（2026）：CUT3R (3D) + SigLIP (2D) cross-attention 融合，长程任务 (100+ steps) SR +4.14%。
- **[[Papers/2507-MTU3D|MTU3D]]**（2025）：统一 3D visual grounding 与 active exploration，4 个导航 benchmark SOTA。

- **[[Papers/2608-GroundingIsntKnowing|Grounding Isn't Knowing]]**（2026，机制侧反问）：这条路线隐含"先定位、再推关系"是必经的计算链条，该文用 token ablation 直接检验它——把 target 物体内部的 visual token 换成常量 embedding，target localization accuracy 掉 5.37 / 27.90 / 64.93 点（LLaVA-1.5-7B / 13B / Qwen2.5-VL-7B），relation accuracy 最多只掉 1.32；把 mask 向外扩一格、吃进周边 context 时 relation 才开始塌（13B 掉 12.38）。侵蚀与膨胀的响应不对称，把关系推理所依赖的证据从"物体内部"推到了"物体周边的粗布局"，限定结论是 VLM 需要 object grounding 但不需要 precise localization。全层 attention 阻断把定位打到接近零、关系打到接近 chance，这个 positive control 排除了"关系判断根本不用 object token"这个更廉价的解释。

这个反问的证据强度受限于真正在做这个任务的只有一个模型：LLaVA-1.5-7B 的 relation baseline 24.82% 正压在 four-way 的 25% chance 上，所有 ΔRel. ≤0.40 是地板效应的产物，13B 的 40.23% 也只略高于 chance，承重的是 Qwen2.5-VL-7B 的 96.11%——而这个数贴着天花板，−1.32 难与噪声分开，全文未报任何显著性。更要紧的是 ablation 保留了物体的轮廓与位置：常量 embedding 覆盖的是按 segmentation mask 选出的连通区域，抹掉的是外观身份，"此处有一块统计异常区域"及其精确位置仍在，而这恰是它想否定的那个粗粒度 anchor；等量随机 token 对照散布全图，形状与位置都不匹配，缺的是一个形状匹配、位置平移的对照。position probe 解码的是每个 image token 的网格位置、训练在 ImageNet 上，与 [[Papers/2606-DecodableNotGrounded|Decodable ≠ Grounded]] 指出的是同一个陷阱。

一致结论：**给 MLLM 显式结构化空间信息远优于让它从像素"猜"空间关系**——这条在任务成功率口径上不受挑战，上述四项工作分属导航与长程操作，增益都是端到端的。但"显式"要精确到什么粒度是另一个问题：在两物体关系判断上，物体级精确定位可以大幅退化而不伤关系准确率，承重的是周边布局。两条读数不冲突——前者说的是给不给结构化信息，后者说的是结构化到哪一层为止；后者只测过 What's Up 这一个单帧、两物体、无遮挡的 benchmark，能否外推到需要 metric 距离与 3D 关系的导航/操作场景未知。

### 专题一 Benchmarks

| Benchmark | 来源 | 规模 | SOTA | 特点 |
|:--|:--|:--|:--|:--|
| **ERQA** (Gemini Robotics) | Real | 400 questions / 7 categories | —（闭源） | 首个 embodied reasoning 专用 benchmark |
| **EmbodiedBench** | Sim | 1,128 tasks / 4 environments | 28.9% (GPT-4o) | 最全面的 MLLM embodied agent 评测 |
| **FoMER** | Real+Sim | 1,112 samples / 8 embodiments | 76.3% (o4-mini)；人类 84.5% | 首次分离 perceptual grounding 与 action reasoning |
| **Robot-R1 Bench** | Sim | MCQ (RLBench 基础) | 7B > GPT-4o | 为 RL-based reasoning 设计 |
| **SIMPLEREnv** | Sim | WidowX/Google Robot | 56.2% (Embodied-R1) | 标准评测平台 |
| **What's Up** | Real（单帧图像） | 614 images / 两物体 / four-way 空间关系 | Qwen2.5-VL-7B 96.11%；LLaVA-1.5-13B 40.23%；LLaVA-1.5-7B 24.82% | 用于机制分析而非排名（[[Papers/2608-GroundingIsntKnowing\|Grounding Isn't Knowing]] 的 token ablation 载体）。作诊断基底时须注意两端都不可用：7B 压在 25% chance 的地板上、Qwen 贴在天花板上，中间没有第三个模型。无遮挡、无 3D、无时序 |
| **空间 VQA 组合（RoboSpatial / ERQA / SAT / EmbSpatial / Omni3D，+附录 SITE-image / ViewSpatial）** | Sim+Real | 主表五项中有三项只有 175 / 200 / 250 题；附录两项 deployment split 为 2224 / 2856 | [[Papers/2608-SpatialMemoryAgent\|SMA]] 每个 base-model block macro 第一（122B 68.8 / 35B-A3B 66.7 / 27B 69.8 / 9B 63.5） | 读数须带两条限定：SMA 每个数字取 10 次 pass 的 best checkpoint 而 baseline 无同等规则；deployment split 最大的两个 benchmark 被放进附录，MemRL-GT 在 ViewSpatial 上两次反超 |

### 专题一 Open Problems

1. **Real-world transfer gap**：18 篇中仅 3 篇有 real robot 实验，RL-based reasoning 的仿真优势能否迁移真实世界未知。
2. **Reasoning 延迟 vs 实时控制**：fast/slow thinking trade-off 无系统性解法（DM0 Spatial Scaffolding、Embodied-R key-frame extraction 仅是缓解）。
3. **Long-horizon multi-step reasoning**：EmbodiedBench 最佳仅 28.9%，跨数十步的 error-robust 推理链远未达到。
4. **Reasoning 过程质量评估**：FoMER 揭示"猜对答案但推理错误"，仅看 final accuracy 不够，safety-critical 场景尤其危险。机制侧的工具已经出现——token ablation、attention knockout 与因果中介分析可以直接问"这一步中间量是不是必需的"，[[Papers/2608-GroundingIsntKnowing|Grounding Isn't Knowing]] 用它测出精确定位对关系判断并非必需。但这类方法的门槛在对照设计而非工具本身：等量随机 token 对照不匹配形状与位置，probe 又只证明"可解码"而非"被使用"（同 [[Papers/2606-DecodableNotGrounded|Decodable ≠ Grounded]]），而当前证据大多只在 2-3 个模型、单个 benchmark 上取得。
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
- **[[Papers/2608-MobileWAM|MobileWAM]]**（2026）：同一条 WAM 路线对 action space mismatch 的另一种接法——不按分支硬拆，而是把 action expert 的每个 FFN 换成 shared / locomotion / manipulation 三专家**软路由**（Mobile MoE），并用一条只在训练期存在的 Chain-of-Foresight 把多步未来压进当前观测表示（推理时删除，详见路线 3）。ManiSkill-HAB SetTable 七子任务平均 73.0%（对照 AnchorVLA 64.0 只覆盖其中 6 项），真机 ARX Lift2 五任务 55/35/25/20/15% 对同数据微调 π0.5 的 35/25/10/10/0%；组件消融里 Mobile MoE 的最大跳变落在 Place Apple（+11.4），正是底盘重定位与精确释放交织的那一项。它与 ABot-M0.5 的 Dual-level MoT 之间有一处未解分歧：MobileWAM 的消融显示按动作维度硬拆专家只有 44.6–48.8 而软路由 58.2，但那是在缩减训练预算下对自己实现的硬拆变体所测，并非与 ABot-M0.5 的直接对照（后者的结果在 RoboTwin 2.0 与 RoboCasa365 上）。两种解耦方式孰优，库内证据不足以判定。
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
| **ManiSkill-HAB** | Sim | 0.73（SG-VLA，4 类任务口径）；[[Papers/2608-MobileWAM\|MobileWAM]] SetTable 七子任务均值 73.0 | mobile manipulation；两个口径的任务集不同不可直接比，MobileWAM 表内对照的 AnchorVLA 64.0 也只覆盖七项中的六项 |
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
- [[Papers/2608-VLAProprioception]] - proprioceptive state 接口的受控研究（表示 / 历史深度 / 注入位置三轴 + slot-matched 对照）
- [[Papers/2608-CofactVLA]] - 反事实干预去混淆（OPG 动作层投影 + CCR 特征层去相关）
- [[Papers/2608-InContextVLA]] - 只读感知工具链注入空间证据（注入 vs 生成 + 监督掩码的三行对照）
- [[Papers/2608-StellaVLA]] - 检索示范前缀 + 语言化空间推理作训练期辅助分支（推理期整条摘除）
- [[Papers/2608-GalaxeaG05]] - 单条自回归流同产 CoT 与离散动作码（跨本体 RVQ + 原生 CoT + ViT 内视觉记忆）

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
- [[Papers/2608-WorldExam]] - 四层诊断 benchmark（explicit fulfillment vs inherent reactivity，跨 camera / action / language 三类接口）
- [[Papers/2608-WorldSimProbe]] - Observable Simulator Contract 与五个受控 probe suite（action-realization / interaction-response 分层）
- [[Papers/2608-WorldTokens]] - World Adapter 压出 256 个 world token 作 action expert 的排他 VL 上下文
- [[Papers/2608-JEPAWAM]] - 冻结 V-JEPA latent 目标 + current–future 联合预测的 WAM
- [[Papers/2608-MobileWAM]] - mobile manipulation WAM（Mobile MoE 软路由 + 训练期 Chain-of-Foresight）
- [[Papers/2606-PointWorld]] - state 与 action 统一为 3D point flow 的 embodiment-agnostic 动力学模型（CVPR 2026）
- [[Papers/2608-Hydra0]] - 图像平面稀疏点轨迹作跨本体动作接口（几何路线 / 纯视频路线双供给 + 条件反转的 world action model）
- [[Papers/2608-DreamXPhi]] - 每臂 SE(3) 相对变换经分组注意力注入（PRoPE 从相机位姿改挂末端执行器）
- [[Papers/2608-DALeWM]] - latent planner 的第二必要条件（信息充分性 vs decision-metric alignment，训练期辅助头推理期丢弃）

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
- [[Papers/2608-HyMeS]] - 技能在冻结权重、记忆策略在代码空间（约束梯度 steering + PACE 阶段判定）
- [[Papers/2608-Zetta]] - action-chunk 级 code-space critic + recovery skill 切换（离线演化 critic/skill，Z-Infra 吞吐 1.72→35.1 episodes/min）
- [[Papers/2608-SpatialMemoryAgent]] - 冻结 VLM 上的 parameter-update-free 空间自演化（transferable lesson + TRS 校准检索）

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

### 表征与机制分析 Papers

- [[Papers/2608-GroundingIsntKnowing]] - token ablation 检验"先定位再推关系"是否必经（侵蚀 / 膨胀的不对称响应）
- [[Papers/2606-DecodableNotGrounded]] - 可解码 ≠ 被使用（probe 类证据的归因边界）

### Safety Papers

- [[Papers/2604-VLASafety]] - VLA Safety Survey

### Benchmark Papers

- **CALVIN**: "CALVIN: A Benchmark for Language-Conditioned Policy Learning for Long-Horizon Robot Manipulation" (Mees et al., 2021)
- **LIBERO**: "LIBERO: Benchmark for Long-Horizon Robot Manipulation"
- **RLBench**: "RLBench: The Robot Learning Benchmark"
- **RoboTwin 2.0**: SeedPolicy paper benchmark

---

## 调研日志

### 2026-09-11 survey-refresh 增量并入 8 篇
- **来源**：[[Papers/2608-StellaVLA|StellaVLA]]、[[Papers/2608-GalaxeaG05|Galaxea G0.5]]、[[Papers/2608-Hydra0|Hydra-0]]、[[Papers/2608-Zetta|Zetta]]、[[Papers/2608-SpatialMemoryAgent|SMA]]（full-text / source-checked）；[[Papers/2608-DreamXPhi|DreamX-Phi]]、[[Papers/2608-DALeWM|DA-LeWM]]、[[Papers/2608-GroundingIsntKnowing|Grounding Isn't Knowing]]（full-text / **partial**，仅采用 source-verified 行）。
- **结构变化**：Overview 新增第 8 条（接口成为独立于模型能力的竞争维度）；路线 1 milestone 表增 G0.5 行，正文新增两组对照（StellaVLA 的"语言只在训练期存在"、G0.5 的单条自回归流 vs 编码器加动作专家）并重写局限段；路线 3 角色表 Planner 行补 decision-metric alignment 这一条独立性质，新增「跨本体的接口之争」小节（Hydra-0 / DreamX-Phi，含五种互不兼容动作接口的分歧记录）与「Planner 角色的第二个必要条件」小节（DA-LeWM），局限段相应增补；路线 6 Runtime 执行鲁棒性并入 Zetta 并补一条 Open Problem（runtime 谓词的去特权化），路线 8 Open question 增记第二种接管粒度；专题一 A2 并入 SMA 作范式外对照并修正核心发现的对照面，A4 并入 Grounding Isn't Knowing 并把"显式空间信息远优于猜"由无条件结论限定为"给不给"与"精确到哪一层"两问，Open Problem 4 补机制分析工具与其对照设计门槛。Benchmarks 表更新 LIBERO / LIBERO-Plus / RoboTwin 2.0 / SIMPLER 四行，新增 LIBERO-Pro / VLA-Arena / BEHAVIOR Challenge / WorldArena / LeWM 规划四件套五行，演进趋势新增两条（同名基准多套聚合口径、与基准无关的报告方式失真）；专题一 Benchmarks 表新增 What's Up 与空间 VQA 组合两行。Key Takeaway 4 / 6 / 11 增补、新增第 12 条（AR 单流架构不再是唯一配方）；Open Problem 4 / 6 / 7 / 11 增补、新增第 13 条（可规划性缺可部署诊断）。参考文献新增 8 条并新建「表征与机制分析 Papers」小节。papers_analyzed 121→129。
- **跳过**：无。
- **证据边界**：全部为原文一致性核查，非独立复现；库内暂无任一篇的第三方复现。G0.5 的"零样本指令跟随超过 post-trained π0.5"被笔记判为 contradicted（自家 Fig 10 中 π0.5 在 50H post-training 下 68.8% 高于 G0.5 零样本 65.6%），本 survey 不采用其原表述。DreamX-Phi 为 partial，其"WA1.0 与 WA2.0 不可比"是库内推断（笔记标 `unsupported`），只作引用口径建议记录，未写成论文结论；该文自陈无任何匹配消融，故其接口优势只有整机排名支撑。DA-LeWM 为 partial，Table 5 对照为已发表数字而非同预算复跑，其两个诊断均解释不了主要增益，本 survey 采用的是切分与内部对照纪律而非 43.4pp 这个数。Hydra-0 的 headline EPE 降幅混淆了动作表示、backbone 更换与蒸馏三项，正文只采用受控对照列，并记下 gripper EPE 系统性偏向条件复制。Zetta 无 ablation 章节、无 budget-matched 对照，其 critic 读取 simulator 官方谓词。SMA 主表非 selection-matched（每个 SMA 数字取 10 次 pass 的 best checkpoint），deployment split 最大的两个 benchmark 在附录且有基线反超。Grounding Isn't Knowing 的三个模型中两个的 relation baseline 贴近 four-way chance，实际承重的只有 Qwen2.5-VL-7B 且贴近天花板；全文未报显著性，缺形状匹配、位置平移的对照。
- **status**: success

### 2026-09-07 survey-refresh 增量并入 8 篇
- **来源**：[[Papers/2608-CofactVLA|CofactVLA]]、[[Papers/2608-MobileWAM|MobileWAM]]、[[Papers/2608-HyMeS|HyMeS]]、[[Papers/2608-JEPAWAM|JEPA-WAM]]、[[Papers/2608-WorldSimProbe|WorldSimProbe]]、[[Papers/2608-WorldTokens|World Tokens]]、[[Papers/2606-PointWorld|PointWorld]]（均为 full-text / source-checked）；[[Papers/2608-InContextVLA|In-Context VLA]]（full-text / **partial**，仅采用 source-verified 行）。
- **结构变化**：路线 1 新增两条分支（CofactVLA 的第二种失效定位、In-Context VLA 的"注入而非生成"）；路线 3 角色表由四角色扩为五角色（新增"训练期表征塑造（推理期删除）"，Planner 行并入 PointWorld），新增「训练期消费、推理期删除」小节（World Tokens / JEPA-WAM / MobileWAM）、Planner 小节增补 PointWorld、评测层新增 WorldSimProbe 小节并把 WorldExam 的 contact 失效由"同一处失效"改记为"同一环节、方向争议"，局限段相应重写；路线 8 并入 HyMeS 并重写 Open question（"中间形态尚无工作"已被占位，空白转移到符号策略的获取端）；专题一 A1 补入 In-Context VLA 反向对照并修正优劣势段；专题二 B3 并入 MobileWAM 并记下与 ABot-M0.5 的软/硬解耦分歧；Benchmarks 表更新 LIBERO-Plus 行（SOTA 与"扰动均为 appearance 级"的口径修正）、新增 WorldSimProbe / RoboMemArena / SIMPLER 三行、专题二 ManiSkill-HAB 行补口径注记、演进趋势新增两条；Overview 新增第 7 条；Key Takeaway 4 改写、9 补竞争解释、新增第 11 条；Open Problem 4 / 6 / 7 / 11 增补。papers_analyzed 113→121。
- **跳过**：无。
- **证据边界**：全部为原文一致性核查，非独立复现；库内暂无任一篇的第三方复现。In-Context VLA 为 partial，其 C20（"去 tool loop 退回 BC 水平"）已被笔记判为 contradicted、C21（backbone 90.4 与既有 OpenVLA-OFT 记录的 95.3 之差）为 not-checkable，两者均未进入本 survey 的任何结论。JEPA-WAM 的 Language 列 68.2 系笔记对 Table 2 的逐列读数，论文正文未讨论该列，已在正文标注出处。MobileWAM 的 Table 3–6 参照点 58.2 在两张表里被分别标为含/不含 Mobile MoE，CoF 的归因因此有两种读法，正文已记。CofactVLA 的评测预算偏低（LIBERO 每 suite 10 episodes、LIBERO-Plus 每任务 1 episode、无 seed 与误差棒），其 backdoor-path 假设全程未经验检验。WorldSimProbe 的六个被测模型全为开源 ACWM，下游实验只在单个 RoboTwin task 上完成。HyMeS 的 PrediMem 对照是在其自定 12 任务协议上重评，与 PrediMem 发表的 26 任务口径不可比；记忆策略由闭源 coding agent 产出。PointWorld 主指标为 ℓ2 flow error 而非任务成功率。World Tokens 无代码，JEPA-WAM 代码标 "Coming soon"。
- **status**: success

### 2026-08-05 survey-refresh 增量并入 2 篇
- **来源**：[[Papers/2608-VLAProprioception|VLAProprioception]]（full-text / source-checked）、[[Papers/2608-WorldExam|WorldExam]]（full-text / source-checked）。
- **结构变化**：路线 1 新增「proprioceptive state 的接口」分支（三条设计轴表 + slot-matched 对照）；路线 3 新增「评测层：把'指令写明的'与'必须自行推断的'分开」分支，局限段补记视觉观感与控制/反应能力解耦；路线 8 补入"为什么必须压缩"的外部证据与 crossover 量级参考；Overview 新增第 6 条（归因方式本身成为研究对象）；Benchmarks 表新增 WorldExam 行、RoboCasa365 行补子集口径注记、演进趋势新增一条；Key Takeaway 4 增补跨范式解耦与 contact 收敛证据；Open Problem 7 增补，Open Problem 11 补入 slot-matched 对照模板。papers_analyzed 111→113。未刷新配图（本 survey 无既有配图，本轮为既有章节内新增分支而非分类框架重构）。
- **跳过**：无。
- **证据边界**：两篇均为 full-text / source-checked，Evidence Ledger 全部 source-verified，仅表示原文一致性已核查，不等于独立复现。VLAProprioception 多数对比单 seed、无真机、state 纯 kinematic（无 force / tactile），16 维 state 含 world-frame mobile-base 位姿，"proprioception 有用"与"全局定位有用"未被去除 base pose 的消融分开；state prompt 因构造上只支持当前帧被排除在全部历史实验之外；joint-angle 坐标系下 K=8 时两条路由收敛到噪声带内。WorldExam 的接口范式与模型档次共线（dynamic track 上 action-driven 仅两个本地模型、language-driven 7 个全为 API backend），范式内方差大于范式间，四个反应类任务的 checklist 未经人工审核（人工只筛初始图），judge 只看 10 帧且"无法核实记为不满足"，reactivity 层实际只有 9 个模型、每 case 只生成一次，数据与工具包尚未发布。
- **status**: success

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
