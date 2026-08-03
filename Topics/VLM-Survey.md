---
title: VLM Survey
tags: [survey, VLM, multimodal, vision-language-model, visual-reasoning]
date_updated: "2026-08-02"
year_range: 2023-2026
papers_analyzed: 41
keywords: [vlm, vision language model, multimodal llm, visual reasoning]
domain_map: VLM
---

## Overview

Vision Language Model (VLM) / Multimodal Large Language Model (MLLM) 是当前 AI 研究中最活跃的方向之一，旨在让模型同时理解视觉和语言信息，实现跨模态的推理、问答、生成和决策能力。自 2023 年以来，该领域经历了从单一图文匹配到复杂多模态推理、从闭源系统到开源生态、从纯理解到理解-生成统一的快速演进。

**核心挑战**：VLM 面临三大关键瓶颈：

1. **视觉表征与语言对齐**：如何让视觉编码器的输出与 LLM 的语义空间有效对齐，实现细粒度的图文理解（尤其是文本密集场景如文档、GUI）
2. **分辨率与细节感知**：传统 VLM 使用固定分辨率输入（如 224x224），难以识别 GUI 中的小字号文本、图标等细粒度元素
3. **理解与生成的统一**：多数 VLM 只做理解任务，生成任务依赖独立的 diffusion 模型，两者之间存在表征不对齐问题

**研究趋势**：2023-2026 年 VLM 领域经历了四个重要演进阶段：
- **基础架构探索（2023）**：CLIP、BLIP 等视觉-语言对齐框架成熟；LLaVA 开启 instruction-following VLM 路线
- **能力扩展期（2024）**：高分辨率 VLM（CogAgent 1120x1120）、专业领域 VLM（MobileFlow）、VLM for grounding 成为热点
- **统一模型期（2025）**：理解+生成统一模型涌现（LLaDA2.0-Uni、Unify-Agent）；VLM 作为 agent backbone 广泛应用
- **效率与对齐优化期（2026）**：KV cache 优化（GUI-KV）、codec-native pre-encoder sparsification（Mage-VL）、human preference alignment、安全防御（LaSM）
- **后训练与机制分析期（2026H2）**：统一模型的 RL 后训练兴起（BRAID、SpectraReward）；因果干预式机制分析与受控诊断 benchmark（Visual Access Sweep、SynthDocBench）取代观察性分析；开源基座持续演进（Gemma 4 encoder-free、ScaleCUA 跨平台 CUA 语料）

---

## 技术路线

### 2.1 高分辨率视觉编码路线

**代表论文**：[[2312-CogAgent|CogAgent]]、[[2400-MobileflowMultimodalLlmMobile]]、[[2400-SeeclickHarnessingGuiGrounding]]

**核心思路**：针对 GUI、文档等文本密集场景，引入高分辨率视觉编码器（≥1120x1120），实现对小字号文本、细图标、密集控件的精准识别。

**关键设计**：
- **CogAgent**：双分辨率图像编码器（low-res + high-res），18B 参数，支持 1120x1120 输入，在 9 个 VQA benchmark 和 Mind2Web/AITW GUI 导航上达到 SOTA
- **MobileFlow**：Hybrid visual encoder + MoE 扩展，21B 参数，专为移动端 GUI 设计，强调中文/多语言支持
- **SeeClick**：Grounding pre-training + screen-only 输入，实现跨平台 GUI grounding

**优势**：解决传统 VLM 在文本密集场景的分辨率瓶颈；跨平台通用性强（不依赖 DOM/HTML）
**局限**：高分辨率输入导致计算开销显著增加；训练和推理资源消耗大

### 2.2 Zero-shot / Agent-based Grounding 路线

**代表论文**：[[2400-VlmGrounderVlmAgent]]、[[2400-TowardsVisualGroundingSurvey]]、[[2511-OVODAgent]]

**核心思路**：利用 VLM 的 zero-shot 能力，通过 agent 式交互（grounding-and-feedback）逐步定位目标，无需专门训练 3D grounding 网络。

**关键设计**：
- **VLM-Grounder**：动态拼接多视角图像 + grounding-and-feedback 机制 + multi-view ensemble projection，实现 zero-shot 3D visual grounding（ScanRefer 51.6% Acc@0.25）
- **Visual Grounding Survey**：系统梳理 fully supervised、weakly supervised、zero-shot、multi-task、generalized grounding 等多种研究设定
- **OVOD-Agent**：把"迭代细化定位"的 agent loop 做成 LLM-free——针对 OVOD 推理时退化为静态类别名匹配的问题，用 7 个原语视觉操作（颜色/纹理/几何/空间关系等）逐步改写类别描述，训练期 UCB Bandit 采样轨迹 + GT-IoU 弱奖励，蒸馏成 20MB 双头 Reward-Policy MLP 在推理期引导 prompt 细化；LVIS val rare-category AP_r 对 4 个 OVOD backbone 一致提升 +1.2~+2.7、common/frequent 不受损（[[2511-OVODAgent]]）。注意其"self-evolving"实为离线弱监督蒸馏（部署后 RM 冻结），且论文存在多处内部数字不一致（引言 <100ms vs 实测 ΔLatency +90~155ms），精确数字引用需谨慎

**优势**：无需 3D 标注数据；充分利用现有 VLM 的 2D 理解能力；适合数据稀缺场景
**局限**：多阶段 pipeline 存在误差传播；计算开销不低（多视角处理 + 多轮 VLM 调用）

### 2.3 理解-生成统一路线

**代表论文**：[[2604-LLaDA2Uni]]、[[2600-UnifyAgentUnifiedMultimodal]]、[[2606-Orca]]

**核心思路**：将多模态理解和生成统一在单一框架内，避免传统系统中理解模块与生成模块的表征不对齐问题。

**关键设计**：
- **LLaDA2.0-Uni**：Discrete tokenizer + MoE dLLM backbone + diffusion decoder，实现原生统一的多模态理解+生成，支持 interleaved generation + reasoning
- **Unify-Agent**：认知缺口检测 + 多模态证据检索 + grounded recaptioning + 图像生成，将 world-grounded synthesis 重构为 agent 流程
- **VLV Auto-Encoder**：视觉编码器 + T2I diffusion decoder + LLM，通过知识蒸馏实现低成本高质量图像描述
- **Orca**：把 modeling target 从 next-token/next-frame 上移到 world state transition——unconscious（视频相邻帧 latent 预测）+ conscious（event 条件预测 + VQA）联合预训练统一 world latent，冻结 backbone 后经 language/image/action 三种 decoder 读出；4B 在 OOD readout 上超同量级专用 baseline（[[2606-Orca]]），是"统一"从理解-生成扩展到 world modeling 的信号

**优势**：理解与生成能力可互相增强；支持 interleaved multimodal reasoning；更接近 AGI 范式
**局限**：MoE + diffusion 组合的显存和推理速度挑战；训练复杂度高

### 2.4 Human Preference Alignment 路线

**代表论文**：[[2500-AligningMultimodalLlmHuman]]

**核心思路**：将 LLM alignment 技术（如 RLHF、DPO）迁移到多模态场景，优化 VLM 在真实性、安全性、推理能力上的表现。

**关键设计**：
- 对齐数据集构建：数据来源、模型响应、偏好标注
- 应用场景：一般图像理解、多图像、视频、音频等
- 评估基准：多模态场景下的对齐效果评测

**优势**：提升 VLM 与人类意图的一致性；改善安全性和可控性
**局限**：多模态偏好标注成本高；跨模态对齐信号难以精确定义

### 2.5 效率优化路线

**代表论文**：[[2500-GuiKvEfficientGui]]、[[2606-StarKV]]、[[2603-STLiteKV]]、[[2500-LasmLayerWiseScaling]]、[[2607-Gemma4]]、[[2607-MageVL]]、[[Papers/2607-KimiK3]]

**核心思路**：针对 VLM 在长序列高分辨率输入下的计算瓶颈，通过 KV cache 压缩、layer-wise scaling 等技术降低推理开销；基座侧则在训练阶段内建效率设计。

**关键设计**：
- **GUI-KV**：空间显著性引导 + 时间冗余评分，实现 38.9% 解码 FLOPs 降低 + 4.1% 步骤准确率提升
- **STaR-KV**：对 GUIKV 等方法"单一共享 saliency map + 固定 top-B 截断"两个结构性假设的直接反驳——pilot 测量显示空间专门化发生在 attention subspace 层级（同层最强/最弱 subspace 与屏幕坐标的互信息差 3-7×、主导 subspace 逐层迁移），且注意力熵沿轨迹单调漂移；以在线空间 MI prior + 时间稳定性折扣 + 熵驱动温度三轴校准替代，training-free、压缩阶段 FLOPs 净 -0.07%；UI-TARS-1.5-7B 40% 预算平均精度 49.94 略超 full cache 49.75，20% 预算峰值显存降约 38.5%（[[2606-StarKV]]）
- **ST-Lite**：诊断出 GUI attention 在所有 transformer 层均匀高稀疏——与 PyramidKV/VL-Cache 分层预算分配的前提冲突（低预算下分层方法灾难性衰减，1% 预算 ST-Lite 7.3 vs VL-Cache 1.1）；Component-centric 空间显著性（3×3 邻域均匀度）+ 轨迹冗余门控双分支，10-20% 预算 decoding 加速 2.45×，AITW 上压缩历史反超全历史（less-is-more，归因于过滤 stale 视觉历史抑制 context poisoning）（[[2603-STLiteKV]]）。注意：其"平均超 baseline 7.3%"宣称经笔记核查为单格最优值（真实均值约 2.2-2.4%），且存在跨表数字不一致——less-is-more 定性结论在两表均成立，但精确增益幅度可信度有限
- **LaSM**：Layer-wise scaling mechanism，通过 attention + MLP 联合缩放防御 pop-up attack（defense success rate 74.8%-100%）
- **Gemma 4**：训练侧效率工程的集成样本（[[2607-Gemma4]]）——KV 共享使全局 KV cache −37.5%、int2/int4 QAT 使音频 encoder footprint −78%、MTP speculative decoding；12B 档给出 **encoder-free 统一架构**（35M 投影直接吃 raw image patch / raw audio），若该路线被证明无损，端侧多模态部署栈将大幅简化——但目前只有单一规模点，且缺"统一 vs 外挂 encoder"同规模对照
- **Mage-VL**：把压缩点前移到 ViT 之前——用 codec motion vector 与 residual energy 只编码高信息 patches，再用 event gate 决定是否调用 language decoder；64-frame 设置约减 75% visual tokens，NExT-QA 报告 80.8/415s（Qwen3-VL-4B 79.8/1460s），但 TempCompass/VSI-Bench 反由 Qwen 更快，且 spatial/long-video 增益与自建 Mage-ViT、350M recaptioning、五阶段 curriculum 混在一起，不能归因于 codec sparsity（[[2607-MageVL]]）

- **Kimi K3**：3T-class 的 native multimodal MoE 基座（2.8T 总参 / 104B 激活 / 1M context），视觉侧的取舍与本节主题直接相关——MoonViT-V2（27 层 / ~401M）**完全从零用 next-token prediction 训练**，放弃 SigLIP 对比学习初始化，文本与视觉从第一步就联合优化、无 post-hoc 对齐阶段；论文给出的理由是训练稳定性（SigLIP-init 变体梯度范数持续更高且频繁 spike），并称视觉评测上与 SigLIP-init baseline 持平。效率侧 MXFP4 权重 / MXFP8 激活的 QAT 贯穿全部 post-training（rollout 与训练共享量化方案以消除 train–inference mismatch），长上下文全程 NoPE、靠 KDA 的 recurrent decay 隐式携带位置从而免去 RoPE 外推补丁（[[Papers/2607-KimiK3]]）。**引用时须打折**：所谓 2.5× scaling efficiency 是架构+数据+训练配方**同时变动**下的聚合自报值，无逐组件 ablation，且全文不披露预训练 token 量 / 总 FLOPs / GPU-hours；"与 SigLIP-init 持平"只给了梯度范数曲线与一句定性表述，未给对照分数——该反转（同团队 K2.5 主张 SigLIP 初始化）的证据强度弱于其结论强度，库内暂无独立验证

**跨论文 pattern（视觉塔初始化）**：视觉侧"必须从对比学习预训练 encoder 出发"这一默认前提，正被两条互不相同的路线同时削弱——[[2607-Gemma4]] 的 encoder-free 直投（35M 投影吃 raw patch）取消 encoder 本身，[[Papers/2607-KimiK3]] 保留 ViT 但取消对比学习初始化。两者都只有单一规模点、都缺"统一/从零 vs 外挂 CLIP-init encoder"的同规模同数据对照，故目前只能记为**默认前提被质疑**，而非已被推翻。

**跨论文 pattern（GUI KV 压缩支线）**：[[2606-StarKV]] 与 [[2603-STLiteKV]] 从不同诊断出发（subspace 级空间 MI 异质性 vs 全层均匀高稀疏）独立得到两个收敛结论——(1) 通用 LLM/VLM KV 压缩的结构先验（共享 saliency、分层预算）在 GUI attention 结构下失效；(2) 中等预算压缩可精度不降甚至略超 full cache，指向 GUI 历史 visual token 存在系统性冗余、stale 视觉历史会污染 context。但两者"反超"的幅度都很小（+0.19 / ~2 分）且均无方差报告，两者的 stale 判据也都是注意力/相似度启发式而非"证据是否仍反映当前界面状态"；该结论目前仅在 7B 开源模型（UI-TARS-1.5 / OpenCUA）上成立。

**优势**：GUI-KV/STaR-KV/ST-Lite/LaSM 无需重新训练、plug-and-play；Gemma 4 的效率 recipe 可复用于端侧部署
**局限**：缩放系数和关键层范围具有 model-specific 特性；对闭源模型难以应用；Gemma 4 未拆分 thinking mode 与架构本身的贡献占比；GUI KV 压缩支线均只报 analytic FLOPs 或受限样本上的加速比。Mage-VL 虽补了端到端 wall-clock，但 3.5× 只是 8×B200 上的峰值案例、跨 benchmark 非单调，效率结论必须同时报告 token budget、source-frame horizon、latency breakdown 与 matched hardware

### 2.6 多模态 RL 后训练与 Reward 设计

**代表论文**：[[2607-BRAID]]、[[2607-SpectraReward]]、[[2607-SearchGenBoundary]]、[[2606-VisPlay]]、[[2607-HyGAE]]

**核心结论**：统一模型（UMM）的竞争焦点已从架构转向后训练——RL 信用分配如何贯穿异构模态、reward 如何免标注获得，且三篇 UMM 工作全部收敛到 BAGEL 系 hybrid AR-diffusion 基座。免标注 reward 的探索同时延伸到理解侧：[[2606-VisPlay]] 用完全自含的 self-play（自身 majority-voting 伪标签 + 不确定性课程）替代人工标注与外部裁判。

**关键设计**：
- **BRAID**：两层 MDP 把交错"文-图-文"轨迹统一为单一决策过程，trajectory-level advantage 同时驱动文本 GRPO 与图像 DiffusionNFT，policy gradient 第一次真正贯穿异构模态；BAGEL-7B 上 7 benchmark 平均 +5.73，ablation 显示图像分支 RL 的贡献大于 VLM judge 的 process reward（[[2607-BRAID]]）
- **SpectraReward**：frozen MLLM 对"生成图像条件下原 prompt 的平均 log-likelihood"（一次 teacher-forced forward pass）即为 T2I RL reward，零偏好标注零 reward 训练；Self-SpectraReward 让 BAGEL 用 understanding 分支给 generation 分支打分（GenEval 84.0→89.5），且发现 **reward-policy 分布对齐比 reward model 规模更重要**——自打分追平 30B、超过 235B 外部 reward（[[2607-SpectraReward]]）
- **SearchGen**：生成模型的 knowledge boundary（internalizable vs contextual）是 (prompt, generator) 的联合属性且随训练漂移——盲目接搜索会在模型本会做的 prompt 上倒退；teach-then-search co-training（DPO 内化可学知识 + RFT 校准 8B search reasoner）使 4B generator 达 Gemini-3-Flash oracle reasoner 水平（[[2607-SearchGenBoundary]]）
- **VisPlay**：理解侧的 label-free RL——单一 base VLM 演化 Questioner/Reasoner 双角色交替 GRPO：Questioner 以 frozen Reasoner 的答案不确定性（confidence→0.5）为 reward 生成贴着能力边界的问题，Reasoner 以自身 majority-voting 伪标签作 verifiable reward；47K 无标注 web 图像、3 个 backbone 平均分随迭代上升（Qwen2.5-VL-3B 30.61→47.27），与人工标注数据 + standard GRPO 平均相当。但拆分显示优势几乎全在 HallusionBench 单项，MMMU/MM-Vet 反而更低；且同批图像的伪标签估计准确率逐代 72.0→61.0 下滑——自我共识监督随迭代自噬，是该范式（而非实现）的根本约束，论文自认缺 definitive verification（[[2606-VisPlay]]）
- **HyGAE**：把 multi-turn VLM agent 的 turn-wise 与 token-wise GAE 线性混合，并在特定 discount relation 下用单一 critic 同时提供两级 value；Qwen2.5-VL-3B 在五类受控 benchmark 的平均成功率 0.91（Token-PPO 0.81），但环境最多 3–7 turns、VIRL 只执行与 ground-truth trajectory 对齐的动作，支持的是短 horizon credit-assignment 稳定性，不是开放式 long-horizon 泛化（[[2607-HyGAE]]）

**共同弱点**：UMM 三篇的 reward/裁判高度依赖闭源强模型（BRAID 用 GPT-5.2 打 process reward、SearchGen 裁判与奖励同源、SpectraReward 零人类评估），增益中 judge preference fitting 的占比未被剥离；likelihood reward 的经典退化解（把 prompt 文字渲染进图像）未被验证；均只在 4B-7B 单 backbone 验证。[[2606-VisPlay]] 换掉了外部裁判依赖，代价是 majority-voting 伪标签继承模型自身系统性偏差、无外部纠错通路。[[2607-HyGAE]] 换成显式 actor-critic，却只在 3B、3–7 turn 受控环境验证；两类路线共同缺少 long-horizon、distribution shift 与 failure-type 分解。

### 2.7 VLM as CUA 基座：数据 Scaling、动作表示与外挂验证

**代表论文**：[[2509-ScaleCUA]]、[[2602-ToolTok]]、[[2511-GuiAima]]、[[2606-HiViG]]、[[2603-SecAgent]]、[[2607-MHLC]]

**核心结论**：GUI/computer-use 场景对 VLM 的要求已从"看得清"（2.1 的高分辨率路线）推进到数据配比、动作表示、历史压缩与验证机制四个层面，且 grounding 能力与端到端 agent 能力被证明显著解耦。

**关键设计**：
- **ScaleCUA**：6 平台开源 CUA 语料（471K understanding / 17.1M grounding / 19K trajectories）+ Qwen2.5-VL 3B/7B/32B 三推理模式基座；GUI understanding/grounding 开源 SOTA（MMBench-GUI L1-Hard 94.4、ScreenSpot-v2 94.7、ScreenSpot-Pro 59.2），但端到端 OSWorld 仅 17.7%、落后 RL 训练的 agent 近一倍（[[2509-ScaleCUA]]）
- **ToolTok**：把 GUI 操作编码为可学习离散 tool token，coarse-to-fine 多步 pathfinding 替代绝对坐标一步回归；Spherical Semantic Initialization 解决新 token cold start（ScreenSpot 55.2→87.6），4B 模型 ~7K 样本达 ScreenSpot-Pro 61.1，提示 **action space 是决定 data efficiency 与分辨率鲁棒性的建模选择而非输出格式细节**（[[2602-ToolTok]]）
- **GUI-AIMA**：与 ToolTok 同攻"文本生成坐标"范式的第二条独立路线——不新增 grounding head，在 [V,Q] 后追加可学习 `<ANCHOR>` token，用 KL loss 把它对 visual patch 的**内生**注意力分布直接对齐为 grounding 信号（visual-sink query token 选头 + overlap-aware/center-biased 软标签）；仅 509k 样本（约 101k 截图）使 3B 达 ScreenSpot-Pro 61.5（含 training-free zoom-in，无 zoom 为 53.8）/ ScreenSpot-v2 92.1 / OSWorld-G 68.1 的 3B 级 SOTA。跨 backbone 迁移增益有限（InternVL3.5-4B 仅 18.1→19.9），提示"点燃内生 grounding"的前提是 backbone 内生能力已足够强（[[2511-GuiAima]]）
- **HiViG**：8B 多模态 critic 双任务——递归压缩 macro-action history + 在截图上渲染红 "X" 标记核对 policy 的实际坐标；对 frozen policy 平均 +7.3/+9.0（Qwen3-VL-32B / Gemini-3-Flash），而全部五种已有 critic baseline 对强 policy 增益近零或为负（[[2606-HiViG]]）
- **SecAgent**：自然语言 semantic context 递归压缩历史，1 帧历史 + context 接近 5 帧性能（SA 94.8 vs 95.5）而 tokens/TTFT 显著更低；附中文 CMGUI 数据集（121K 已标注 steps / 44 apps）补非英语语料缺口（[[2603-SecAgent]]）
- **MHLC**：把 generated-token hidden-state trajectory 读成两个 execution control signal——Capability Head 决定是否 handoff，Resolution Head 在 Clarification / Tool Use / Abstention / Direct Answering 间选择；AndroidWorld 的 Qwen3-VL-4B→32B routing 从 0.47 提至 0.60、按其“本地模型免费”口径 paid API cost 减 90.7%。它把 latent self-assessment 变成可执行接口，但监督来自外部 LLM judge、每个 backbone 需单独训练，且 hidden-state access 使其不能直接包装 closed API（[[2607-MHLC]]）

**跨论文 pattern**：

| Pattern | 证据 |
|:--|:--|
| grounding SOTA ≠ 端到端能力 | ScaleCUA OSWorld 17.7 vs COMPUTERRL 47.3；训练分辨率 2K 升 grounding 却降 online agent |
| 像素锚定优于文字中介 | HiViG intent masking ablation 证明 verbal critic 在读文字而非看图；ToolTok/HiViG 均靠截图上渲染显式标记（crosshair / 红 X）把 VLM 拉回视觉状态；GUI-AIMA 直接监督内生 anchor→patch 注意力分布替代文本坐标生成，ablation 较 vanilla attention 聚合 +5.88（43.39 vs 37.51） |
| GUI 专有能力与通用能力冲突 | ScaleCUA：通用多模态数据比例上升则 GUI benchmark 单调下降，需显式 data-balancing |
| 语义历史压缩缺 factuality 校验 | SecAgent/HiViG 的压缩状态由模型自述生成，silent corruption 会污染后续决策，两篇均未评测 context 本身准确率 |

### 2.8 机制分析：视觉信息"在"但"读不出"

**代表论文**：[[2607-VisualAccessBoundary]]、[[2606-Act2Answer]]、[[2607-GUIStateBelief]]、[[2607-EvoGUI]]

**核心结论**：多篇在不同域用因果干预/行为级协议独立发现同一 pattern——信息在 hidden states 里（线性 probe 可恢复）但模型行为上读不出，VLM 的瓶颈从"表征缺失"转向"读出通路"。GUI 域进一步给出跨模态与时序两个变体：结构文本与像素冲突时模型偏信过期结构（[[2607-GUIStateBelief]]），以及状态转移/时序理解不随模型规模或 GUI 专门化提升（[[2607-EvoGUI]]）。

**关键发现**：
- **Visual Access Boundary**：硬屏蔽 generated token→image token attention 的 2D 扫描（layer × time）显示，CoT 生成长度拉长约 50 倍但所需视觉访问边界与 Direct answering 相差 ≤2 层——CoT 增益来自对已写入 hidden states 的视觉信息做更长语言计算，而非持续"回看"图像；CoT 增益上限受 perceptual readout 制约，难属性存在 probe-vs-decode gap（probe 高精度、decode 显著更差）（[[2607-VisualAccessBoundary]]）
- **Act2Answer**：把知识题改造成"用动作作答"的 VLA 评测协议以剥离低层控制混淆；robotics 微调让语义类知识相比源 VLM 掉 20-40 分，layerwise probing 显示知识在中层仍可解码、到 action head 附近衰减至近随机；VQA co-training 有显著保护作用（Magma retention 86.7% vs π₀ 36.2%）（[[2606-Act2Answer]]）
- **GUIStateBelief（跨模态变体）**：735 组 Web/Mobile/Desktop paired probe——image-only 读取接近饱和时，模型在 pixel↔structure 冲突下仍跟随 stale structure（真实网页结构跟随率最高 0.88），首步注错的 MiniWoB++ episode 自恢复 ≤0.03，training-free consistency gate 才同时降 hijack 与 task error；证据"在"（像素可读）却不被采信，是 readout gap 的 modality-trust 版本（[[2607-GUIStateBelief]]）
- **EvoGUI（时序变体）**：3,000 个 state-transition diagnostic VQA（temporal ordering / inverse action / one-step successor，120 domains），最强模型仅 60.4，且 model scale 与 GUI specialization 均非稳定预测因子——VLM 的状态动态理解是端到端分数掩盖的独立缺口（[[2607-EvoGUI]]）

**含义**：对"拉长推理链提升 multimodal reasoning"和"扩数据防遗忘"两类流行方案都是警示——前者不扩张视觉访问、后者丢的不是知识而是读出。**适用边界**：VAS 的任务限于"一眼看完再算"型，visual search / 多步 grounding 上结论可能翻转；Act2Answer 的二选一格式分辨率有限。

### 2.9 Agentic visual reasoning 的工具忠实性与自适应性

**代表论文**：[[Papers/2607-Beacon]]、[[Papers/2607-FaithEyes]]、[[2606-CodeDance]]

**核心结论**：thinking-with-images 路线的 aggregate accuracy 掩盖了两类结构性退化——模型的调用模式基本锁死在"几乎必调"或"几乎不调"的一端而非按题自适应，且工具在难题上的收益被易题上新引入的错误大部分抵消。两篇 2026-07 的工作分别补上诊断口径与 reward 侧修复，把该路线的评价单位从"平均准确率"改写为"调用时机 × 工具净效应"的分解。

**诊断口径**：

| 维度 | 定义 | 退化基线 | 出处 |
|:--|:--|:--|:--|
| Mode Adaptiveness（MA_text / MA_tool） | 易题上不调工具的比例 / 难题上调工具的比例；难易由 5 次纯文本采样投票判定（≥4 次对为 text-easy、≤1 次对为 text-hard，2–3 次判 ambiguous 剔除） | 恒调或恒不调的模型 MA_mean 恰为 50% | [[Papers/2607-Beacon]] |
| Tool Effect（Tool-Gain / Tool-Harm / ΔTE） | 被工具解出的难题比例 − 被工具做错的易题比例 | ΔTE ≈ 0 | [[Papers/2607-Beacon]] |
| Tool faithfulness ratio | 答对且含 process image 的轨迹中，是否存在真正呈现所问证据的图 | — | [[Papers/2607-FaithEyes]] |

用这套口径重测既有方法，退化立刻显影：Thyme 的 MA_text 92.95 / MA_tool 4.28（几乎不调）、DeepEyesV2 的 MA_tool 99.71 / MA_text 0.63（几乎必调），两者 MA_mean 分别 48.61 与 50.17，与掷硬币无异；四个 baseline 的 ΔTE 均在 +0.04~+1.74 之间，即工具的净效应接近零。

**两条修复路线**：

- **Beacon（reward 内化"何时该调"）**：Necessity-Aware Adaptive Reward——rollout group 内已存在正确的纯文本回答时，正确的 code 回答 reward 从 1 降到 0.25；"这题需不需要工具"的标签由当前 policy 的组内表现在线决定，而非外部 teacher 打标，规避了 teacher-policy 分布错配与 teacher 工具能力封顶。配套 Hint-Guided Capability Expansion 处理 RLVR 在全错组上无 group-relative 信号的结构缺陷：对全错组注入 expert 生成的 answer-free hint 重采样，策略更新时从输入抽掉 hint、只在 old policy 的 importance-sampling 分母保留，约 40% 的全错组被回收为有效信号。Qwen3-VL-8B 基座，13 benchmark 平均 58.98、MA_mean 58.83（全场最高）、ΔTE +3.14（[[Papers/2607-Beacon]]）
- **FaithEyes（reward + observation 同时补"有没有用上"）**：同一 VLM 换 prompt 兼任 subagent，只看 `(Q, I_t)` 逐张判定 process image 是否呈现所问证据；判词一物两用——注入 observation（判为无用时直接丢图只留判词）并作为 tool reward 的缩放因子 `r_tool = 1 − (n_fail + n_unhelpful)/n_tool`。两处机制选择可脱离本文迁移：reward 用**比例而非计数**，数学上封死"多调工具刷 bonus"（λ_tool 消融全程平均调用次数稳定在约 1 次）；reward **不以答案正确为门**，因为挂钩答案会使难题上失去维持代码可执行性的梯度压力——对照实验中该变体的执行失败率峰值约 18%、调用次数一路掉向零且不再恢复。Qwen2.5-VL-7B 基座，V\*/HR-4K/HR-8K 达 87.4/77.8/72.9（[[Papers/2607-FaithEyes]]）

**必须打折的地方**：

| 问题 | 证据 |
|:--|:--|
| 增益的主要来源不是新 RL 组件 | Beacon 相对 base 的 6.07 点中约 4.00 来自 SFT、整个 RL 阶段约 2.07，其中 vanilla GRPO 仅 +0.19；这恰好复现了它自己引用的"提升主要来自 SFT"的既有诊断 |
| 基座代差混入主表 | Beacon 建在 Qwen3-VL-8B 上而四个 agentic baseline 为 Qwen2.5-VL-7B——未经任何 agentic 训练的 base 在其 Table 2 六项平均（43.97）已高于全部 7B agentic baseline（33.76~38.11）；同量级对照只有 Metis-8B，优势收窄到 +1.48 / +3.27 |
| "省算力"的动机与实际行为相反 | Beacon 的 MA_text 仅 22.91，五个数据集实际调用率 70.65%~95.36%，高于被它批评为"缺自适应性"的 Metis（15.72%~54.32%）；其 MA_mean 优势几乎全部来自 MA_tool 一侧 |
| Tool-Harm 未被控制 | Beacon 平均 Tool-Harm 6.15 为全表最高（Metis 仅 1.10），ΔTE 优势全来自 Tool-Gain；MathVista 上 ΔTE −0.38，按其自身口径工具净有害 |
| 评测轴与训练目标同源 | FaithEyes 的评测 faithfulness rubric 是训练 subagent rubric 的加严版（同一概念"所问目标是否出现在处理图中"，差别在信息集与严格度），只有 FaithEyes 被直接优化到该轴上，baseline 从未见过 |
| 只证到 action level | 两篇诊断问题时用的是"移除 process image 后预测几乎不变"这类反事实证据，验证自身修复时却换成 judge 打分的比例指标；FaithEyes 自认 answer-level reliance gap 未关闭 |
| 无预算匹配对照 | FaithEyes 每次工具调用多一次 subagent forward，全文不报 latency 或 token 开销；其 Table 1 显示仅在推理期给 Thyme 插一个外部 32B 判词、不做任何训练，V\* 即从 82.7 升到 85.8（距 FaithEyes 87.4 仅 1.6 分），暗示相当部分增益来自"多一次带视觉的复核"这一通用机制。Beacon 调用频率远高于 baseline，等推理预算下的对比同样缺失 |
| 强 teacher 依赖未被剥离 | Beacon 的 SFT 轨迹合成、RL hint 生成与答案判分兜底同为 Gemini 3.1 Pro；FaithEyes 的判定 rationale 由 Qwen3-VL-32B 生成、accuracy/consistency 兜底由 Qwen2.5-VL-72B、faithfulness 评测由 Qwen3-VL-235B-A22B。两篇均无 teacher 消融，"机制有效"与"强 teacher 蒸馏有效"无法分开 |
| baseline 数字跨论文不一致 | 同一 DeepEyes-7B 在 [[2606-CodeDance]] 记 V\* 90.4 / MathVerse 47.3，在 [[Papers/2607-FaithEyes]] 记 84.3 / 44.3——这批 benchmark 的评测协议（分辨率上限、温度、答案抽取）远未统一，1.6~2.6 分的领先须在同一 harness 下复现才成立 |

**与 §2.8 的关系**：这是 "decodable ≠ used" 在工具层的同构变体——process image 被生成（证据在）但答案并不依赖它（读不出）。差别在于 §2.8 的证据藏在 hidden states、只能靠 probe 与注意力屏蔽间接检验，而此处证据就在 observation 通道里，本可以直接做干预（移除或替换被判 helpful 的裁图，看答案是否改变），两篇却都停在 judge 打分的代理指标上。

**适用边界**：全部结论建立在"工具 = 沙箱内确定性、无副作用、可回滚的 Python 代码"这一设定上。工具自身带噪声（检索、真实 GUI 操作、物理执行）时，NAAR 依赖的"组内是否存在正确纯文本回答"这一在线标签会被工具噪声污染，text-easy/text-hard 的划分也不再稳定——这是把该框架迁移到 GUI 或 embodied 场景时最先断裂的地方。

---

## Datasets & Benchmarks

| Dataset/Benchmark | 任务类型 | 规模 | 评估指标 | SOTA | 特点 |
|:------------------|:---------|:-----|:---------|:-----|:-----|
| **VQAv2** | Visual QA | ~200K questions | Accuracy | GPT-4V 领先 | 自然图像问答基准 |
| **TextVQA** | Text-rich QA | ~28K questions | Accuracy | CogAgent SOTA | 文本密集场景问答 |
| **DocVQA** | Document QA | ~50K questions | ANLS | CogAgent SOTA | 文档理解基准 |
| **MM-Vet** | Multimodal evaluation | ~2K tasks | MM-Vet score | GPT-4V 领先 | 综合多模态评测 |
| **POPE** | Hallucination | ~3K images | Accuracy | CogAgent SOTA | 幻觉检测基准 |
| **MME** | Multimodal evaluation | 14 subtasks | Perception + Cognition | 多模型评测 | 感知+认知分离评测 |
| **MMMU** | Multi-discipline | ~12K questions | Accuracy | GPT-4V 领先 | 大学级多学科问答 |
| **ScanRefer** | 3D Grounding | ~51K descriptions | Acc@0.25 | VLM-Grounder: 51.6% | 3D visual grounding |
| **Nr3D** | 3D Grounding | ~41K descriptions | Acc | VLM-Grounder: 48.0% | 3D referring expression |
| **Mind2Web** | Web Navigation | ~2K tasks | Success Rate | CogAgent SOTA | Web agent benchmark |
| **AITW** | Android Navigation | ~560K episodes | Action Accuracy | CogAgent SOTA | 移动端操作 benchmark |
| **ScreenSpot** | GUI Grounding | Multi-platform | Accuracy | ScaleCUA-32B 94.7 (v2) | GUI grounding 评测 |
| **ScreenSpot-Pro** | 高分辨率 GUI Grounding | 专业软件截图 | Accuracy | GUI-AIMA-3B 61.5（含 zoom-in）/ ToolTok-4B 61.1 / ScaleCUA-32B 59.2 | 高分辨率/小目标 grounding |
| **RefCOCO** | 2D Grounding | ~50K expressions | Acc@0.5 | 多模型竞争 | 经典 referring expression |
| **FactIP** | World-grounded Generation | 12 categories | Human preference | Unify-Agent 接近 closed-source | 长尾概念生成评测 |
| **SynthDocBench** | Long-context Doc VQA | 200 docs / 1,788 题 | ACC（LLM judge） | Gemini-3.1-Pro 0.725 | 全合成受控诊断；因子可独立控制 |
| **SearchGen-Bench** | Knowledge-intensive T2I | 751 test / 12 失败类 | 9 分量 judge 评分 | GPT-Image-2 71.2 | 知识密集生成；附冻结 search corpus 可离线复现 |
| **GUIGuard-Bench** | GUI Privacy | 241 轨迹 / 4,080 截图 | detection + plan fidelity | strict full match ≤8.8% | trajectory-conditioned 隐私评测 |
| **CMGUI-Bench** | 中文 Mobile GUI Navigation | 390 episodes / 2,574 steps | Step/Task Acc | SecAgent-3B 96.4/80.0 | 多合法 action 标注，减 false negative |
| **State-Belief Probes** | 跨模态证据冲突诊断 / GUI | 735 paired probes | stale-structure follow rate | 结构跟随率最高 0.88 | pixel/structure 单变量干预 + live episode |
| **EvoGUI** | GUI 状态转移诊断 VQA | 3,000 / 120 domains | ACC | best 60.4 | trajectory-derived offline probe |

**Benchmark 演进趋势**：
- 从自然图像问答（VQAv2）到文本密集场景（TextVQA、DocVQA）
- 从 2D grounding（RefCOCO）到 3D grounding（ScanRefer、Nr3D）
- 从单一模态评测到多学科综合评测（MMMU）
- 从理解任务到理解+生成统一评测（FactIP、SearchGen-Bench）
- 从覆盖式 leaderboard 到受控诊断仪器：[[2607-SynthDocBench]] 独立控制文档长度/页深/layout/模态因子，把失败归因到具体因子（长度衰减、中段位置盲区、长文档 chart 崩溃）
- 从单帧安全评测到 trajectory-conditioned 评测：[[2601-GUIGuardBench]] 把 privacy 定义为任务上下文属性（task necessity），而非静态敏感类别识别

---

## Key Takeaways

1. **高分辨率视觉编码是 VLM 在文本密集场景的关键突破**：CogAgent、MobileFlow 等证明，支持 ≥1120x1120 输入的双分辨率编码器可显著提升 GUI、文档等场景的理解能力。这解决了传统 VLM 固定分辨率（224x224）的瓶颈。

2. **Zero-shot grounding 利用 VLM agent 能力而非专门训练**：VLM-Grounder 展示了通过动态拼接 + feedback loop + multi-view ensemble，无需 3D 训练数据即可实现较强的 3D grounding。这条路线适合数据稀缺场景。

3. **理解-生成统一是 VLM 发展的明确趋势，但架构尚未定型**：LLaDA2.0-Uni、Unify-Agent 等工作将多模态理解和生成放在同一框架，避免了两阶段系统的表征不对齐问题。原版认为 discrete diffusion + MoE 是主流架构选择，但 2026H2 的 RL 后训练工作（[[2607-BRAID]]、[[2607-SpectraReward]]、[[2607-SearchGenBoundary]]）全部收敛到 BAGEL 系 hybrid AR-diffusion 基座，主流架构之争未决；[[2606-Orca]] 进一步把"统一"从理解-生成扩展到 world state transition + 多 decoder 读出。

4. **Human preference alignment 开始向多模态迁移**：将 RLHF/DPO 技术迁移到 VLM，优化真实性、安全性、推理能力，是当前 VLM 走向可靠部署的关键一步。

5. **效率优化技术（KV cache、layer-wise scaling）可在不重新训练的前提下显著降低开销**：GUI-KV、LaSM 等工作证明，通过 inference-time intervention 可实现计算效率提升和安全性增强，部署门槛低。2026 年两篇 GUI 场景 KV 压缩工作（[[2606-StarKV]]、[[2603-STLiteKV]]）从不同诊断独立发现：通用压缩的结构先验（共享 saliency map、分层预算）在 GUI attention 结构下失效，且中等预算压缩可精度不降甚至略超 full cache——GUI 历史 visual token 存在系统性冗余，压缩从纯有损 trade-off 变为可能的净增益（反超幅度小、仅 7B 开源模型验证）。

6. **VLM 正从被动理解器走向主动 agent backbone**：GUI Agent、3D grounding agent、world-grounded synthesis agent 等工作表明，VLM 不只是"看图说话"，而是可以成为多模态 agent 的感知与决策核心。

7. **多模态 RL 后训练成为新前沿，reward 转向复用 MLLM 自身能力**：[[2607-BRAID]] 让 policy gradient 第一次贯穿文本 token 与图像去噪路径；[[2607-SpectraReward]] 证明 frozen MLLM 的 prompt likelihood 一次 forward pass 即可做 T2I reward，且 reward-policy 分布对齐比 reward model 规模更重要（自打分超 235B 外部 reward）——该发现对整个 RLHF/RLAIF 都有参考价值。理解侧 [[2606-VisPlay]] 把 reward 推到零外部依赖（自身 majority-voting 伪标签 + 不确定性课程），但伪标签质量逐代下滑（72.0→61.0）表明纯自我共识的监督会自噬——免标注 reward 尚无同时摆脱"闭源裁判"与"自我偏差"的方案。

8. **"Decodable ≠ used"是跨域收敛的机制发现**：[[2607-VisualAccessBoundary]] 的 probe-vs-decode gap 与 [[2606-Act2Answer]] 的"中层可解码、action head 近随机"互为印证——VLM 的瓶颈从表征缺失转向读出通路。CoT 增益来自更长的语言计算而非持续回看图像，上限受 perceptual readout 制约。

9. **GUI grounding 与端到端 agent 能力显著解耦**：[[2509-ScaleCUA]] grounding 开源 SOTA 但 OSWorld 仅 17.7%（落后 RL 系近一倍）；分辨率与数据配比对两种能力的影响方向相反——"grounding 强则 agent 强"的隐含假设不成立，data scaling（SFT）与 RL 是互补而非替代关系。

10. **VLM agent 的新瓶颈是把内部信号变成可靠控制接口**：[[2607-MHLC]] 从 hidden-state trajectory 读出 handoff/tool/abstention 决策，[[2607-HyGAE]] 则把 token/turn credit 统一进同一 critic；两者分别处理 inference-time control 与 training-time credit assignment，但都只在可控、短 horizon setting 中成立。下一阶段不能只报 aggregate success，必须报告 false-retain/false-handoff、wrong intervention、trajectory 长度与 calibration drift。

11. **"有没有调工具"必须与"调了有没有用"分开测量**：[[Papers/2607-Beacon]] 给出的 MA_mean = 50% 退化基线立刻暴露出现有 agentic VLM 基本锁死在"几乎必调"（DeepEyesV2 MA_tool 99.71）或"几乎不调"（Thyme MA_text 92.95）的一端，四个 baseline 的 Tool-Gain 减 Tool-Harm 净效应均在 +0.04~+1.74；[[Papers/2607-FaithEyes]] 从另一侧证明"答对但 process image 与问题无关"是常态，并给出两条可迁移的 reward 设计（按有用比例而非调用计数计分、不以答案正确为门）。这套分解可直接搬到 GUI agent 的"何时该截图放大"与 deep research agent 的"何时该检索"。但两篇都只证到 action level（裁得准），未证到 evidence-dependence level（答案真的靠它），且都缺等推理预算对照。

12. **开源基座的视觉侧默认前提正在松动，但证据强度不足**：[[2607-Gemma4]] 取消视觉 encoder（encoder-free 直投）、[[Papers/2607-KimiK3]] 保留 ViT 但取消对比学习初始化（MoonViT-V2 从零 NTP 训练），两条路线同时质疑"必须从 CLIP/SigLIP 预训练 encoder 出发"。两者都只有单一规模点，且都未给同规模同数据的对照分数——Kimi K3 对该反转只提供了梯度范数曲线与一句"视觉评测持平"的定性表述，而它自己上一代 K2.5 的结论恰恰相反。

---

## Open Problems

### 5.1 核心技术挑战

1. **长上下文多模态推理的瓶颈**：当前 VLM（如 CogAgent、LLaVA）在处理长序列图像、多视角输入时面临 context window 限制。虽然 GUI-KV 等尝试压缩 KV cache，但如何在保持理解质量的前提下支持超长多模态上下文仍是开放问题。新证据加剧了该问题的紧迫性：[[2607-SynthDocBench]] 证实 lost-in-the-middle 在视觉长文档上复现（5/8 模型中段掉 5-18 pp），且长文档下 chart 理解以 visual hallucination 方式崩溃；[[2603-SecAgent]] 的自然语言 semantic context 压缩（1 帧历史接近 5 帧性能）是低成本缓解路线，但压缩状态缺 factuality 校验。KV 侧 [[2606-StarKV]]/[[2603-STLiteKV]] 显示 GUI 历史 KV 可在 20-40% 预算下基本无损甚至略超 full cache，但两者的 stale 判据都是注意力/相似度启发式——不检验被保留的证据是否仍反映当前真实界面状态，"按证据时效性而非注意力冗余淘汰历史"仍是空白。

2. **理解-生成统一的表征最优设计**：LLaDA2.0-Uni 采用 discrete diffusion + MoE，Unify-Agent 采用 separate backbone + retrieval，两者架构差异显著。哪种设计在效率、质量、泛化上最优，尚无定论。RL 后训练侧 [[2607-BRAID]] 证明 advantage 可贯穿异构模态，但仅在 BAGEL-7B 单 backbone 验证，跨架构泛化未知。

3. **VLM 的细粒度 grounding 稳定性**：在高噪声、遮挡、动态布局场景下，VLM 的 grounding 能力仍不够稳定。Continual GUI Agents 提出 anchoring reward，但更鲁棒的 scale-invariant grounding 机制需要进一步研究。[[2602-ToolTok]] 的离散相对 tool token 是绝对坐标之外的一条候选路线（跨分辨率/宽高比鲁棒性显著提升），但 FAR/MID/CLO 固定 pixel delta 并非完全 scale-invariant，且未经 online 长任务验证。

4. **生成模型的 knowledge boundary 发现**：[[2607-SearchGenBoundary]] 证明"哪些知识内化、哪些外部检索"是 (prompt, generator) 的联合属性且随训练漂移——盲搜有害、边界不可先验预测、必须跑完整 co-training 才能发现。低成本的边界估计方法缺失，该问题与 agent 的"何时调工具"calibration 同构。

### 5.2 数据与评测挑战

5. **多模态偏好标注的高成本**：Human preference alignment 需要大量高质量偏好数据，但多模态场景下的标注成本远高于纯文本。如何利用 AI-assisted annotation 或 self-generated preference signal 降低成本，是关键问题。[[2607-SpectraReward]] 的 prompt-likelihood reward 提供了零标注起点，但只覆盖 alignment、不度量 aesthetics/fidelity。[[2606-VisPlay]] 展示了完全免标注的 self-play 路线（47K 无标注图像自举出训练信号），但 majority-voting 伪标签继承模型自身系统性偏差且逐代变脏（72.0→61.0）——"不依赖模型自我共识的自生成 verifier"仍缺失，与 agent 的"何时该信外部验证"问题同构。

6. **Benchmark saturation 与 data contamination**：MMMU、MME 等基准上模型已接近人类水平，但是否存在 data contamination、benchmark memorization 争议。需要更动态、更不可预测的评测方法。[[2607-SynthDocBench]] 的全合成受控生成是一条替代路线（ground truth by construction），但其 OCR baseline 对照暴露了新陷阱：complex multi-hop 子集 OCR 0.798 >> vision 0.360——长文档 benchmark 可能测的是文本检索而非视觉推理，OCR/text-only baseline 应成为多模态 benchmark 的标配对照。

7. **3D grounding benchmark 的规模局限**：ScanRefer、Nr3D 数据规模有限（~50K），且场景类型偏室内家居。开放世界 3D grounding、跨场景泛化评测仍缺乏。

8. **MLLM-as-reward / as-judge 的可信度**：2.6 节三篇工作的 reward 或评测均依赖闭源强模型且缺独立人评交叉验证（[[2607-SpectraReward]] 零人类评估、[[2607-SearchGenBoundary]] 裁判与奖励同源）；[[2607-SynthDocBench]] 的 rendering-familiarity confound（D3.js 渲染分布可能偏向特定模型家族）提示合成评测同样有系统性偏差。Reward hacking、judge 亲和偏差的系统性度量方法缺失。§2.9 把该问题推到极端形态：[[Papers/2607-FaithEyes]] 的 tool reward 完全由与 policy **共享权重**的 subagent 给出，RL 全程只在训练结束后做过一次外部 judge 检查，而稳步上升的 tool reward 恰恰是被 hack 时同样会上升的量；该 subagent 的判定质量从未被独立测量（无人工标注一致率、无相对 235B judge 的混淆矩阵），其 SFT 判定标签还建立在"两次调用轨迹的第一次必然无用"这一未核验的结构性假设上。可行的最小检验是记录 RL 全程 subagent True-rate 与外部 judge 判定的偏离曲线，成本不高但尚无人做。

### 5.3 系统与应用挑战

9. **VLM 作为 agent backbone 的决策可靠性**：当 VLM 用于 GUI agent、embodied agent 时，其 grounding 误差会直接影响动作执行。如何在多步任务中实现稳定的决策链，是走向实际部署的关键。[[2606-HiViG]] 给出一个反直觉证据：五种已有 critic（scalar PRM、zero-shot verbal critic、专训 critic）对强 policy 增益近零或为负——"拿通用 VLM 当 judge"在 CUA 上不成立，critic 必须专门训练且训练信号对准像素证据（visual marker + intent masking）。[[2607-MHLC]] 进一步说明 even when latent control works，judge-derived labels、fixed threshold、per-backbone head 与未计 hidden-state extraction 的成本会成为新依赖；[[2607-HyGAE]] 则把训练期稳定性问题推进到 token/turn 混合 credit，但 long-horizon 证据仍空白。

10. **安全与隐私防护的系统化方案**：LaSM 针对 pop-up attack 的 layer-wise scaling 是有效局部方案，但对 instruction injection、adversarial OCR text 等其他攻击类型的系统性防御尚未成熟。隐私维度上 [[2601-GUIGuardBench]] 揭示层级断裂：binary detection 尚可（Android 89.0% / PC 63.3%）但 strict full match 仅 8.8%/0.6%，需要上下文推断的 Inferences & Profiling 类 recall 仅 2.4%——"知道有隐私"远不等于能最小化披露，selective disclosure policy 的学习尚属空白。

11. **理解-生成统一模型的推理效率**：MoE + diffusion + LLM 的组合导致显存和推理速度挑战。如何在保持统一能力的前提下实现高效推理，需要架构层面的创新。[[2607-Gemma4]] 的 encoder-free 直投路线（raw patch/audio 直接进 LLM embedding 空间）是候选方向之一，但目前只有 12B 单点、缺同规模对照。

12. **下游微调的知识侵蚀**：[[2606-Act2Answer]] 显示 robotics 微调让 VLM 语义类知识掉 20-40 分且下游 SFT 继续恶化；VQA co-training 有保护作用但 Emotion/Attribute 类仍在 chance 水平——如何系统性防止微调侵蚀预训练能力（对 VLA、GUI agent 微调同样适用）未解决。

13. **工具忠实性缺 answer-level 干预检验**：§2.9 两篇诊断问题时用的是干预式证据（移除 process image 后预测几乎不变），验证自身修复时却退回 judge 打分的比例指标，因此"faithful tool use"目前只被证到裁得准、未被证到答案真的依赖它。可直接借用的范式已在库内——[[2606-VisualFLIP]] 的 same-question paired perturbation 让 gold answer 确定性翻转，用 Pair Accuracy / Collapse Rate 度量证据依赖；把它套到被判 helpful 的裁图上（扰动该图看答案是否更新）就是缺失的决定性实验。同一层问题还有"等推理预算"这一侧：[[Papers/2607-FaithEyes]] 的 Table 1 显示纯推理期插一个外部判词就能让 Thyme 从 82.7 涨到 85.8，而多出的 subagent forward 从未被计入任何开销表。

### 5.4 研究方向建议

- **Resolution-First 原则**：在追求复杂推理能力之前，优先确保高分辨率视觉编码的基础能力。
- **Unified-First 原则**：在设计 VLM 时，优先考虑理解+生成的统一架构，而非分离模块拼接。
- **Alignment-First 原则**：在追求性能提升之前，优先完成 human preference alignment，确保安全性和可控性。
- **Efficiency-First 原则**：在部署场景中，优先考虑 inference-time efficiency optimization（KV cache、layer scaling），而非重新训练。
- **Readout-First 原则**：诊断 VLM 能力失败时，先区分"表征缺失"与"读出失败"（linear probe vs 行为对照），再决定补数据还是修读出通路（[[2607-VisualAccessBoundary]]、[[2606-Act2Answer]]）。

---

## 参考文献

### 6.1 核心方法论文

**高分辨率视觉编码**：
- [[2312-CogAgent|CogAgent]] - CogAgent: 18B VLM, 1120x1120 dual-resolution encoder
- [[2400-MobileflowMultimodalLlmMobile]] - MobileFlow: 21B multimodal LLM for mobile GUI
- [[2400-SeeclickHarnessingGuiGrounding]] - SeeClick: GUI grounding pre-training

**Zero-shot Grounding**：
- [[2400-VlmGrounderVlmAgent]] - VLM-Grounder: Zero-shot 3D visual grounding
- [[2400-TowardsVisualGroundingSurvey]] - Visual Grounding Survey

**理解-生成统一**：
- [[2604-LLaDA2Uni]] - LLaDA2.0-Uni: Unified multimodal understanding + generation
- [[2600-UnifyAgentUnifiedMultimodal]] - Unify-Agent: World-grounded image synthesis
- [[2500-VisionLanguageVisionAuto]] - VLV Auto-Encoder: Knowledge distillation from diffusion
- [[2606-Orca]] - Orca: Next-State-Prediction world foundation model, frozen latent + 多 decoder readout

**多模态 RL 后训练**：
- [[2607-BRAID]] - BRAID: 两层 MDP 让 RL 贯穿文本 GRPO 与图像 DiffusionNFT
- [[2607-SpectraReward]] - SpectraReward: Frozen MLLM prompt likelihood 作 T2I reward
- [[2607-SearchGenBoundary]] - SearchGen: Knowledge boundary 发现与 teach-then-search co-training
- [[2606-VisPlay]] - VisPlay: 双角色 self-play 免标注 RL，majority-voting 伪标签 + 不确定性课程
- [[2607-HyGAE]] - HyGAE: Turn-wise + token-wise GAE 与 unified critic

**Human Preference Alignment**：
- [[2500-AligningMultimodalLlmHuman]] - Aligning Multimodal LLM with Human Preference: A Survey

**效率优化与基座**：
- [[2500-GuiKvEfficientGui]] - GUI-KV: KV cache with spatio-temporal awareness
- [[2606-StarKV]] - STaR-KV: subspace 级空间 MI + 时间稳定性折扣 + 熵温度的三轴 KV 校准
- [[2603-STLiteKV]] - ST-Lite: GUI attention 全层均匀高稀疏诊断 + CSS/TSG 双分支压缩
- [[2500-LasmLayerWiseScaling]] - LaSM: Layer-wise scaling for pop-up attack defense
- [[2607-Gemma4]] - Gemma 4: 开源原生多模态基座，encoder-free 12B + 端侧效率 recipe
- [[2607-MageVL]] - Mage-VL: Codec-native pre-encoder sparsification + event-gated streaming generation
- [[Papers/2607-KimiK3]] - Kimi K3: 3T-class native multimodal MoE，MoonViT-V2 从零 NTP 训练（无 SigLIP 初始化）+ 全程 NoPE 1M context + MXFP4 QAT

**Agentic visual reasoning 的工具使用**：
- [[Papers/2607-Beacon]] - Beacon: Mode Adaptiveness / Tool Effect 诊断口径 + NAAR 在线自适应奖励 + HCE 全错组回收
- [[Papers/2607-FaithEyes]] - FaithEyes: 自判 subagent 的 process-image 有用性判词双用（observation 反馈 + tool reward 缩放）

**机制分析**：
- [[2607-VisualAccessBoundary]] - Visual Access Sweep: CoT 视觉访问边界的因果干预
- [[2606-Act2Answer]] - Act2Answer: VLA 知识保留的行为级评测协议

### 6.2 应用与评测论文

**VLM for Object Detection**：
- [[2500-ObjectDetectionMultimodalLarge]] - Object Detection with Multimodal Large Vision-Language Models
- [[2511-OVODAgent]] - OVOD-Agent: LLM-free 迭代 prompt 细化，Bandit 轨迹蒸馏成 20MB Reward-Policy MLP

**VLM Evaluation**：
- [[2500-EvaluatingOpenSourceVision]] - Evaluating Open-Source VLMs for Multimodal Sarcasm Detection
- [[2607-SynthDocBench]] - SynthDocBench: 长文档视觉理解的受控诊断 benchmark
- [[2601-GUIGuardBench]] - GUIGuard-Bench: Trajectory-conditioned GUI privacy 评测

**VLM for GUI Agent**：
- [[2506-ShowuiOneVisionLanguage]] - ShowUI: Vision-Language-Action model for GUI
- [[2509-ScaleCUA]] - ScaleCUA: 跨 6 平台开源 CUA 语料与三模式基座
- [[2602-ToolTok]] - ToolTok: 离散 tool token 替代绝对坐标回归
- [[2511-GuiAima]] - GUI-AIMA: anchor token + KL 对齐内生注意力的 coordinate-free grounding
- [[2606-HiViG]] - HiViG: History-aware visually grounded critic
- [[2603-SecAgent]] - SecAgent: Semantic context 历史压缩 + 中文 CMGUI 数据集
- [[2607-MHLC]] - MHLC: Hidden-state trajectory 驱动 handoff / tool / clarification / abstention

---

## 调研日志

### 2026-04-28 初版
- **调研日期**: 2026-04-28
- **论文统计**: vault 已有 15 篇 VLM 相关论文，本次重点分析 12 篇核心论文
- **未能获取**: 外部 WebSearch/WebFetch 工具受限，未能获取 arxiv 新论文
- **核心发现**: 高分辨率视觉编码解决文本密集场景瓶颈；理解-生成统一成为趋势；效率优化可在不重新训练前提下实现显著改进
- **status**: success
## 🆕 Venue 回填增补（2026-06-26，CVF 近 3 年）

> 补收 CVF VLM/Multimodal（29）+ Spatial/3D（22）方向论文,完整清单+综合见 [[Reports/2026-06-26-VenueBackfill]]。

- **空间智能（本批最大主题）**：⭐5 [[2606-ScalingSpatialIntelligence]]（data-centric 8M scaling）、[[2606-SpatialScore]]（49 个 MLLM 评测）、[[2606-SpaceTools]]（多轮调 pointing/depth/3D 工具）、[[2606-FromIndoorTo]]（OpenBench 户外空间推理）。三条解法并行:几何 encoder 注入（[[2606-SpatialStack]]/[[2606-S2MLLM]]/[[2606-G2VLM]]/[[2606-HiSpatial]]）、data scaling、test-time 几何先验（[[2606-Abstract3DPerception]]/[[2606-GeometricallyConstrainedAg]]）。**open question：架构注入 vs data-scaling 缺同 benchmark head-to-head。**
- **长视频理解走 agentic**：[[2606-LensWalk]]/[[2606-VideoARM]]/[[2606-SVAgent]]/[[2606-SymphonyACognitively]]/[[2606-HierarchicalLongVideo]] 普遍用 plan-observe-verify 多轮 + 检索,而非更大 video model。
- **文档/推理 agent**：[[2606-VisualDocumentUnderstandin]]（MACT）、[[2606-CodeDance]]（code as tool）、[[2606-MonoVLM]]（coarse-to-fine GRPO 解 3D grounding reward 稀疏）。

### 2026-07-21 增量更新（survey-refresh）
- 并入 13 篇：[[2607-BRAID]]、[[2607-Gemma4]]、[[2509-ScaleCUA]]、[[2607-VisualAccessBoundary]]、[[2607-SpectraReward]]、[[2607-SynthDocBench]]、[[2607-SearchGenBoundary]]、[[2606-Act2Answer]]、[[2606-HiViG]]、[[2602-ToolTok]]、[[2601-GUIGuardBench]]、[[2603-SecAgent]]、[[2606-Orca]]
- 跳过 1 篇：[[2607-GRPONullWebAgent]]（纯 RL 训练方法学的受控阴性结果，无 VLM 架构/多模态能力层贡献，归 AgenticRL/WebAgent survey）
- 结构变化：新增 2.6（统一模型 RL 后训练）、2.7（VLM as CUA 基座）、2.8（机制分析：decodable ≠ used）三个小节；Key Takeaways +3（7-9）；Open Problems 新增 knowledge boundary、MLLM-as-reward 可信度、知识侵蚀三项；benchmark 表 +5 行；修订 Takeaway 3（BAGEL 系 hybrid AR-diffusion 挑战 discrete diffusion + MoE 的"主流"论断）
- **status**: success

### 2026-07-22 增量更新（survey-refresh）
- 并入 2 篇（均 GUI 域跨域 VLM 能力证据，primary home 为 CUA-Survey）：[[2607-GUIStateBelief]]（§2.8，跨模态证据冲突=readout gap 的 modality-trust 变体）、[[2607-EvoGUI]]（§2.8 + benchmark 表，VLM 状态转移/时序理解缺口）
- 跳过：无
- 结构变化：仅增量并入——§2.8 代表论文 +2、关键发现 +2 bullet；benchmark 表 +2 行；未改 Key Takeaways / Open Problems（两篇强化既有 readout 主题，未推翻结论）
- domain_map: skipped（无格局级变化，仅强化 §2.8 "decodable ≠ used" 主题）
- **status**: success

### 2026-07-24 增量更新（survey-refresh）
- 并入 5 篇：[[2606-StarKV]]（§2.5，三轴 KV 校准反驳共享 saliency/固定截断假设）、[[2603-STLiteKV]]（§2.5，全层均匀高稀疏诊断 + less-is-more；verification partial，仅采用 source-verified 结论并标注其 +7.3% 宣称被证伪）、[[2606-VisPlay]]（§2.6，理解侧免标注 self-play RL 及伪标签自噬证据）、[[2511-GuiAima]]（§2.7 + benchmark 表，内生注意力对齐的 coordinate-free grounding，SS-Pro 3B SOTA）、[[2511-OVODAgent]]（§2.2，LLM-free 迭代 prompt 细化蒸馏）
- 跳过 1 篇：[[2606-Resource2Skill]]（skill library 系统层贡献，agent 走 programmatic 接口不做视觉观察，无 VLM 架构/多模态能力层增量；主场 CUA-Survey 已并入）
- 结构变化：§2.6 更名"多模态 RL 后训练与 Reward 设计"（原限定统一模型，VisPlay 把免标注 reward 主题延伸到理解侧）；§2.5 新增"GUI KV 压缩支线"跨论文 pattern 段（两篇独立工作收敛于"通用压缩先验在 GUI 失效 + 中等预算压缩可反超 full cache"）；Takeaways 5/7、Open Problems 1/5 增量修订；ScreenSpot-Pro SOTA 更新为 GUI-AIMA-3B 61.5
- domain_map: 更新 DomainMaps/VLM.md 近期格局变化（GUI KV 压缩 less-is-more 证据收敛；"文本生成坐标"范式受两条独立路线挑战）
- **status**: success

### 2026-07-29 增量更新（survey-refresh）
- 并入 3 篇：[[2607-MageVL]]（§2.5，codec-native pre-encoder sparsification + event-gated streaming）、[[2607-HyGAE]]（§2.6，token/turn hybrid credit assignment）、[[2607-MHLC]]（§2.7，hidden-state latent control interface）
- 跳过 1 篇：[[2409-ElementOrdering]]（GUI observation 表示编排工作，已完整并入 canonical [[Topics/CUA-Survey]] §4.5/§6.7.2；对 VLM 架构或多模态能力无独立增量）
- 结构变化：未新增平行 taxonomy；扩展 §2.5/2.6/2.7，并新增 Takeaway 10（内部信号→可靠控制接口）与 Open Problem 9 的 calibration/long-horizon 边界
- domain_map: [[DomainMaps/VLM]] 新增 2 条格局变化（pre-encoder sparsification；latent control + hybrid credit）
- **status**: success

### 2026-08-02 增量更新（survey-refresh）
- 并入 3 篇：[[Papers/2607-KimiK3]]（§2.5，3T-class native multimodal 基座 + MoonViT-V2 从零 NTP 训练）、[[Papers/2607-Beacon]]（新增 §2.9，MA/TE 诊断口径 + NAAR/HCE）、[[Papers/2607-FaithEyes]]（新增 §2.9，process-image 有用性判词双用）
- 跳过：无
- 结构变化：新增 §2.9「Agentic visual reasoning 的工具忠实性与自适应性」（两篇独立工作形成新 pattern：aggregate accuracy 掩盖调用模式退化与工具净效应近零，且该主题是 §2.8 "decodable ≠ used" 在工具层的同构变体）；§2.5 新增"视觉塔初始化"跨论文 pattern 段（encoder-free 与 contrastive-init-free 两条路线同时质疑 CLIP/SigLIP-init 默认前提，但均缺同规模对照）；Key Takeaways +2（11、12）；Open Problem 8 追加自判自奖闭环的漂移监测缺口、新增 Open Problem 13（answer-level 干预检验与等预算对照）
- domain_map: 更新 [[DomainMaps/VLM]] 近期格局变化（开放基座推进到 3T-class native multimodal；工具使用的忠实性/自适应性成为独立评价轴）
- **status**: success
