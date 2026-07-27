---
title: "WebAgent 的 RL 训练与 Context 构造：两轴文献地图"
date: 2026-07-27
tags: [report, web-agent, agentic-RL, context-engineering, agent-interface]
related:
  - "[[Reports/2026-07-27-WebAgentRL-Loss-Formulas]]"
  - "[[Reports/2026-07-27-Agent-Friendly-Browser-Interaction-Rules]]"
  - "[[Topics/CUA-Survey]]"
---

# WebAgent 的 RL 训练与 Context 构造：两轴文献地图

## 结论

两轴已经合流成同一个问题：RL 侧的主要动作是把 credit 从轨迹级下推到回合/步骤级，Context 侧的主要动作是把"每一步喂给 agent 什么"从固定管线变成可构造、可学习的对象，而两轴交叉的 23 篇正在把后者直接当成前者的优化变量。

- **轴 A（RL 训练）58 篇中 27 篇在做 credit assignment**，且几乎全部把 GiGPO 的 anchor-state 分组当作要修的靶子——批评点高度收敛于"同一状态但历史不同的步骤不可交换"和"少量 rollout 下步骤优势统计不可靠"两条。
- **轴 B（Context / Interface）89 篇中最大一族（30 篇）是 agent-native web / API 协议提案，也是证据最薄的一族**：多为 position paper 或自建 testbed，缺乏与真实站点、真实采纳率对照的实验。真正带受控对照的集中在另外两族——constructed observation（14 篇）与 agent-authored context（18 篇）。
- **最值得先读的是交叉轴 23 篇**：它们把 context 折叠、记忆写入、观察构造本身设成动作空间并用 RL 优化（MemAct、Context-Folding、CompactionRL、FoldAct、HiMPO、ContextCurator），这是两轴唯一真正耦合的地方，也是方法论上唯一非增量的部分。
- **本地图不支持的结论**（详见 §4）：不能说记忆/skill 模块整体有效、不能说 CLI/API 接口优于 GUI、不能说 context 压缩单调有益、不能说任何一种接口设计在 WebArena 上领先——每一条都有已发表的对照实验反着说，或缺失预算匹配的控制组。

## 0. 覆盖范围与读法

两轴按用户界定拆分：**轴 A** 是 web/computer-use agent 的 RL 训练方法；**轴 B** 是 agent 每一步实际接收到的内容——排除"直接吞原始 HTML/DOM"，只收额外构造出来的界面、表示与上下文。同时命中两轴者单列。

检索规模：234 条去重候选，其中 38 条已有笔记，170 条经独立核验确认为本地图新增（confirmed 154、标题纠错后确认 16、判为离题剔除 23）。年份分布 2026 年 117 篇、2025 年 45 篇、2024 及更早 8 篇——这个分布本身说明两轴都还在高速变形期，2024 年前的工作主要作为奠基坐标而非当前基线。

**Grounding 级别**：全部条目经标题/arXiv ID/摘要级核验，方法描述来自作者自述，数值为作者自报，未做独立复现。文中标 **作者自报** 的数字均属此类。优先级标记：★★ 必读 / ★ 值得读 / · 略读。

与 [[Reports/2026-07-27-WebAgentRL-Loss-Formulas]] 的分工：那份报告逐条抄录 11 个具体系统（WebGym / AsyncWebRL / OpenWebRL / ZeroGUI / ARPO / UI-TARS 1&2 / WebRL / WebAgent-R1 / Agent Q / HiconAgent）的损失函数与超参，是**公式层**；本报告是**格局层**，给出族谱、争议点与证据边界，不重复公式。需要某篇的目标函数细节时去那边查。

---

## 1. 轴 A：RL 训练（58 篇新增）

轴 A 的重心已经从"能不能用 RL 训 web agent"转移到"稀疏的终局奖励怎么分配到中间步骤"。27 篇 credit assignment 工作构成绝对主体，其余四族——reward/verifier 设计（16）、环境与任务合成（4）、训练系统（4）、阴性结果与评测诚信（4）——本质上都在回答同一个问题的不同侧面：奖励从哪来、环境从哪来、系统怎么跑得动、以及报出来的提升是不是真的。

### 1.1 Credit assignment 与 advantage 估计（27 篇）

这一族的对话结构异常清晰：GiGPO（2505.10978，★★，作者自报 ALFWorld 较 GRPO +12%、WebShop +9%）提出 episode + anchor-state 两级无 critic 优势估计后，后续工作几乎全部针对它的两条假设发难。第一条是**可交换性**：BiPACE（2605.25556）与 HoGPO（2602.22817）都指出按 observation hash 分组会把"经不同历史到达同一 WebShop 结果页"的步骤当作可比样本，前者用 bisimulation 重划分组，后者引入层级分组恢复历史一致性。第二条是**统计可靠性**：Evidence-Calibrated PO（2606.05885）论证有限 rollout 下重复 anchor 状态处的步骤优势会给"运气好的罕见动作"分配过大权重，即更密的 credit 本身不构成更好的 credit。ProGPO（2607.04242）把这两条并成一个显式取舍——分组键放宽提升覆盖但破坏可比性，收紧则相反。

与之平行的是一条"根本别用 GRPO"的线：Turn-PPO（2512.17008）报告 GRPO 在多回合长程任务上退化、PPO 更稳健，回合级 MDP 建模进一步改善；GRPO Collapse（2512.04220）给出崩溃的机制解释——Lazy Likelihood Displacement，正确与错误响应的 likelihood 同时下降触发低置信度/梯度膨胀的自强化循环。GUI-G1（2505.15810）则在 grounding 任务上逐项拆掉 R1-Zero 式训练的三个组件，发现更长 CoT 反而损害 grounding。这三篇是这一族里对"默认配方"最有杀伤力的证据。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ GiGPO | 2505.10978 | episode + anchor-state 两级无 critic 优势估计，本族公共靶子 |
| ★★ BiPACE | 2606.25556 | 用 bisimulation 重划分组，修 observation-hash 造成的 state-action credit 错配 |
| ★★ HoGPO | 2602.22817 | 层级分组恢复历史一致性，针对 stepwise 分组的 context inconsistency |
| ★★ Evidence-Calibrated PO | 2606.05885 | 有限 rollout 下密集 step credit 统计不可靠，需按证据量校准 |
| ★★ GRPO Collapse (LLD) | 2512.04220 | Lazy Likelihood Displacement 机制解释 search agent 上的 GRPO 崩溃 |
| ★★ Cyclical Entropy Eruption | 2605.27954 | agent RL 的熵不是单调塌缩而是周期性爆发-消退，与推理 RL 定性不同 |
| ★★ Negative Advantages | 2604.18235 | 把多跳 search 的两类 GRPO 失效归因到负优势的未校准处理 |
| ★★ SGE | 2603.02045 | 先生成自然语言策略再生成环境动作，扩展探索边界 |
| ★★ Bi-level Expert RLVR | 2601.05787 | 少量专家轨迹如何安全混入 on-policy RLVR 训端到端 GUI 策略 |
| ★★ GUI-G1 | 2505.15810 | 逐项证伪 R1-Zero 式 grounding 训练的三个组件，长 CoT 反伤 grounding |
| ★★ TRACE | 2607.13988 | 以冻结参考模型的 gold-answer 对数概率导出回合级 state value 与 credit |
| ★ G2PO | 2606.22995 | 把线性 rollout 转成全局状态转移图，同观察节点合并 |
| ★ Drowning in Routine | 2606.22164 | credit 难度由 decision density 而非 horizon 长度决定 |
| ★ ARCO | 2606.21262 | 同规模开源模型双头共演化：生成逐步 rubric + 预测 rubric 条件下的步骤奖励 |
| ★ 3SPO | 2606.09961 | 动态 state score 监督下的 post-step 优化，摆脱整段 rollout 后才更新 |
| ★ StainFlow | 2606.07027 | 实体染色追踪 + 证据链接做 process reward，替代主观 milestone 分解 |
| ★ BPO | 2607.14171 | 指出 PPO/RLOO/GRPO 的 rollout 拓扑继承自 RLHF，忽略 sandbox 可回溯性 |
| ★ PRO-CUA | 2605.29119 | 解耦 on-policy 环境交互与策略优化，同状态下生成候选动作取步骤奖励 |
| ★ GAGPO | 2605.13217 | 从采样 rollout 构造非参数分组价值代理，做 TD/GAE 式时序优势 |
| ★ Turn-PPO | 2512.17008 | GRPO 在长程多回合退化，PPO 更稳；回合级 MDP 进一步改善 |
| ★ SALT | 2510.20022 | 同 prompt 轨迹图从 outcome reward 导出步骤优势，即插即用 |
| ★ Progressive Curriculum (Triton) | 2604.12666 | 590k 结构-语义困难负例 + 双 agent 共识合成 + 三阶段课程 |
| ★ Credit Assignment 综述 | 2604.09459 | 47 个方法按粒度/方法论分类，区分推理 RL 与 agentic RL 两个 regime |
| · ProGPO | 2607.04242 | 显式formalize 分组键宽窄的覆盖-可比性取舍 |
| · STAPO | 2607.04963 | 针对 trajectory neglect，质疑 Shannon 熵作为不确定性信号 |
| · RSPO | 2607.04713 | 稀疏 outcome 与稠密 process reward 之间做 reward swap |
| · Prioritized Replay | 2601.02648 | 问题级优先采样，集中在既非全对也非全错的问题上 |

### 1.2 Reward、Verifier 与 PRM（16 篇）

这一族的共同判断是：verification 而非 generation 已成瓶颈（2606.26300 直接以此为立论）。技术路线分两支——一支做 **PRM/rubric**，另一支做**评测诚信审计**，后者的信息量更大。AgentPRM（2511.08325）给出这一族的概念前提：agent 动作没有清晰对错，只能按"promise（距目标的接近度）"和"progress"打分。WebArbiter（2601.21872）把 web process reward 建模改写为文本生成——输出结构化的原则性说理再给候选动作偏好判决。The Art of Building Verifiers（2604.06240）总结了四条工程原则，其中"区分可控与不可控失败"是多数 rubric 方案缺的一环。

诚信侧三篇值得单独看：BenchJack（2605.12673）自动红队审计 10 个流行 agent benchmark 并归纳八类缺陷模式；False Success（2606.09863）在 9,876 条 tau2-bench 与 1,879 条 AppWorld 轨迹上测得"agent 宣称完成但环境状态不符"占单控制任务失败的 45–48%（**作者自报**）；CHERRL（2606.04923）通过向 LLM-as-a-Judge 注入已知偏置，把 rubric RL 的 reward hacking 变成可稳定复现的现象。这三篇合起来意味着：轴 A 里任何以 benchmark 成功率为唯一证据的提升声明，都需要先检查评测本身。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ AgentPRM | 2511.08325 | agent 动作无清晰对错，按 promise + progress 打分 |
| ★★ WebArbiter | 2601.21872 | web PRM 改写为"结构化说理 + 偏好判决"的文本生成任务 |
| ★★ Universal Verifier | 2604.06240 | 四原则构建 CUA 轨迹 verifier，含可控/不可控失败区分 |
| ★★ Autonomous Eval RL for CUA | 2606.24515 | VLM 判最终截图替代手写机器可读奖励，建模为带噪二元奖励 |
| ★★ ARBOR | 2606.03239 | 跨 query 共享的 rubric buffer 做在线 process reward |
| ★★ BenchJack | 2605.12673 | 自动红队审计 10 个 agent benchmark，归纳八类缺陷模式 |
| ★★ VeriEnv | 2603.10505 | 语言模型作为环境创建者，把真实站点克隆成可验证合成环境 |
| ★ Verification Horizon | 2606.26300 | 立论：verification 而非 generation 是 coding agent 的瓶颈 |
| ★ RuVerBench | 2606.29920 | 2,458 实例元评测 LLM-as-a-Judge 的 rubric 核验可靠性 |
| ★ False Success | 2606.09863 | 沉默失败占单控制任务失败的 45–48%（**作者自报**） |
| ★ AliyunConsoleAgent | 2606.09447 | 真实云控制台上 SFT + GRPO，双通道 outcome reward model |
| ★ AdaRubric | 2603.21362 | 任务自适应 rubric，置信度加权逐维打分产稠密偏好信号 |
| ★ PAE | 2603.03116 | 四轴（效用/效率/交互质量/流程完整性）门控，揭示"腐败式成功" |
| ★ EntWorld | 2601.17722 | 1,756 个企业任务，从底层数据库反推业务逻辑做 schema 接地生成 |
| · CHERRL | 2606.04923 | 向 judge 注入已知偏置，使 rubric RL 的 reward hacking 可稳定复现 |
| · Reward Hacking Benchmark | 2605.02964 | 多步工具任务中的自然捷径机会（跳验证/猜答案/篡改评测件） |

### 1.3 环境与任务合成（4 篇）

新增部分很薄，因为这一族的主力已在既有笔记里（见 §5）。新增四篇的共同取向是"用程序而非人力造可复现环境"：Weblica（2605.06761）把 HTTP 级缓存与 LLM 环境合成结合，在保留交互行为的前提下复现稳定视觉状态；GTA（2605.29218）把瓶颈定位为过程级监督缺失而非任务数量；Synthetic Computers（2604.28181）造带真实文件层级与内容的合成计算机；RollArt（2512.22560）把 agentic RL 的四类异构负载（compute-bound prefill / bandwidth-bound decode / CPU 重的环境执行 / 突发式奖励评估）拆到专用硬件。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ Weblica | 2605.06761 | HTTP 缓存 + LLM 环境合成，可复现的视觉 web 训练环境 |
| ★ GTA | 2605.29218 | 长程 web 任务规模化生成，瓶颈定位在过程级监督 |
| ★ Synthetic Computers | 2604.28181 | 造内容丰富的合成计算机做长程生产力任务模拟 |
| ★ RollArt | 2512.22560 | 按负载特性拆分 agentic RL 流水线到专用硬件 |

### 1.4 训练系统与异步（4 篇）

四篇里两篇是系统实现（ROLL Flash 2510.11345 的 rollout-train 解耦与环境级异步；ProRL Agent 2603.18815 的 rollout-as-a-service），一篇是立场文（2607.01120 主张企业自演化 agent 卡在 RL **系统**而非算法，缺三根支柱：标准化轨迹数据层、异步 rollout 编排、在线奖励服务）。第四篇 Rollout Cards（2605.12131）是这一族里唯一的负面证据：审计 50 个流行 agent 仓库，**无一**记录失败/报错/跳过的运行，并指出 37 处"仅报告口径本身就改变成功率"的位置（**作者自报**）。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★ Next-Gen Agentic RL Systems | 2607.01120 | 立场：瓶颈在 RL 系统三支柱而非算法 |
| ★ ProRL Agent | 2603.18815 | rollout-as-a-service，把 rollout 编排从训练循环解耦 |
| ★ ROLL Flash | 2510.11345 | 细粒度并行 + rollout-train 解耦的原生异步 RL 后训练 |
| · Rollout Cards | 2605.12131 | 50 仓库审计：无一记录失败运行；37 处报告口径改变成功率 |

### 1.5 阴性结果与评测诚信（4 篇）

四篇都直接质疑轴 A 的提升声明。PASS@(k,T)（2604.14877）同时变化采样预算 k 与交互深度 T，发现与静态推理任务下 base/RL 的 pass@k 曲线收敛不同，agent 场景下的结论不成立——这是判断"RL 是否真的扩展能力边界"最直接的工具。Statistical Diagnosis（2507.04103）是首个对 web agent 后训练做统计接地的算力分配研究，其价值在于给出"多少差异属于噪声"的量纲。Search-Time Contamination（2606.05241）把 deep research agent 的泄漏分三级并给出检测算法。WebChoreArena（2506.01952）用 532 个"繁琐但真实"的任务（大内存/计算/长期记忆）替代取巧任务。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ PASS@(k,T) | 2604.14877 | 联合变化采样预算与交互深度，检验 RL 是否真扩展能力边界 |
| ★★ Statistical Diagnosis | 2507.04103 | 首个统计接地的 web agent 后训练算力分配研究 |
| ★ WebChoreArena | 2506.01952 | 532 个繁琐真实任务，压测大内存/计算/长期记忆 |
| · Search-Time Contamination | 2606.05241 | deep research 的三级泄漏分类与检测 |

另有三篇归入其他：ARLArena（2602.21534，标准化 agentic RL 测试床 + 四维设计消融）、WebAnchor（2601.03164，"plan anchor" 现象——首个推理步不成比例地决定下游行为）、AgentHER（2603.21357，把 HER 迁移到自然语言轨迹重标注）。

---

## 2. 轴 B：Context / Interface 构造（89 篇新增）

轴 B 的定义边界是"排除原始 HTML/DOM 直吞"，剩下的工作按**谁来构造**分成两半：环境侧构造（B1 ACI/harness、B2 agent-native web/API、B3 constructed observation）与 agent 侧构造（B4 agent-authored context、B5 skill/workflow）。这个二分不是分类学偏好，而是可证伪性的分水岭——环境侧构造要求站点或系统改造，证据通常止于自建 testbed；agent 侧构造可在固定环境上做受控对照，因而证据强度显著更高。

### 2.1 Agent-Computer Interface 与 harness（12 篇）

这一族的奠基坐标是 SWE-agent（2405.15793，NeurIPS 2024，★★），其论点——"LM agent 是一类新用户，值得专门设计的软件接口"——是整个轴 B 的原始命题。AXIS（2409.17140）在同期给出 API 优先于 UI 动作的桌面版本，并自动探索应用以扩展 API 面。

2026 年的新动向是把 harness 本身变成可演化的对象：AHE（2604.25850）建三根 observability 支柱（组件级可回滚表示、经验蒸馏、结果归因）跑闭环演化；NLAH（2603.25723）把 harness 策略写成可编辑的自然语言文档，由运行时解释成 agent 调用。AOI（2606.29472）则把观察层从动作层解耦——连续自适应观察（关键帧捕获、音量门控的音频转写、CU 模型生成的视觉描述）与离散动作分离，这是本族里对"每步 context 是什么"回答得最直接的一篇。Harness-Induced Belief Divergence（2607.04528）提供了本族少见的诊断工具：在不同 harness 下抽取结构化的 K 步信念轨迹，测量 harness 如何改变 agent 的内部状态而非仅改变成功率。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ SWE-agent (ACI) | 2405.15793 | 原始命题：LM agent 是新用户，需专门设计的 agent-computer interface |
| ★★ AXIS | 2409.17140 | API 优先于 UI 动作 + 自动探索扩展 API 面（Word 上缩短完成时间） |
| ★★ AOI | 2606.29472 | 连续自适应观察与离散动作解耦的模型无关感知层 |
| ★★ Agentic Harness Engineering | 2604.25850 | 三支柱 observability 驱动 harness 自动演化闭环 |
| ★★ Auxiliary Reasoning for Grounding | 2509.11548 | VLM 有强隐式 grounding 但不会输出坐标；渲染轴/网格/标号可零样本释放 |
| ★ Belief Divergence 诊断 | 2607.04528 | 抽取结构化 K 步信念轨迹，量化 harness 如何改内部状态 |
| ★ ToolPro | 2606.19992 | 把工具意图表示为带显式 effect 类型的可执行工具程序 |
| ★ Nielsen 启发式重审 | 2605.02729 | 十条可用性启发式在 CUA 视角下哪些迁移、哪些因人类假设而失效 |
| ★ NLAH | 2603.25723 | 自然语言 harness 文档 + 智能 harness 运行时 |
| ★ OAgents | 2506.15741 | GAIA/BrowseComp 上对规划/工具/记忆/测试时扩展做公平受控消融 |
| · CLI-Anything | 2606.03854 | 立场：GUI 范式强迫 agent 模仿人类感知限制，应转 CLI harness |
| · PG-Agent | 2509.03536 | 把演示 episode 转成显式页面转移图，RAG 检索 GUI 感知指引 |

### 2.2 Agent-native web 与 API 协议（30 篇）

这是数量最大、证据最弱的一族。主线主张一致——为 agent 单独暴露一层结构化接口，而不是让 agent 去解析人类 UI——但实现层散成互不兼容的提案：VOIX（2511.11287）用声明式 HTML `<tool>` / `<context>` 标签；CI4A（2601.14790）把 UI 组件交互逻辑封装成统一工具原语；webMCP（2508.09171）把交互元数据直接嵌进页面；DMI（2510.04607，EuroSys '26，★★）把既有 GUI 抽象成 access/state/observation 三个声明式原语并做 policy-mechanism 分离；Typed Actions（2602.17245）主张用"web verbs"取代点击；AWI（2506.10953）给出六条设计原则。这些提案彼此没有共同的评测底座。

本族仅有的两处看似硬的证据在回到原文后都不成立，详见 [[Reports/2026-07-27-Agent-Friendly-Browser-Interaction-Rules]] §3.4。MCP vs RAG vs NLWeb vs HTML（2511.23281）报告的 F1 0.67→0.75–0.77、token 从约 241k 降到 47k–140k（**作者自报**，模拟环境）里，效果那一半被论文自己的 Table 4 推翻（vague 与 cheapest 两类上 HTML 反超），且三条非 HTML 臂共用作者自建的语义索引后端而 HTML 臂只有店内关键词搜索框——真正的自变量是有无语义索引，不是暴露协议；token 比值方向可信，美元比值因未开 prompt caching 不可用。Unbrowse（2604.00694）"不要求站点改造、从真实浏览流量被动学出第一方 shadow API 路由图"这条路线的加速证据同样不成立：作者发布的 benchmark 脚本给 Playwright 基线硬插了 2,000 ms 无条件 sleep 且未用论文声称的 CSS selector 定向抽取，扣掉后均值加速从 3.58× 降到 1.49×、21/94 个域名反而更慢；全文无任何 task success rate，robots.txt 检查与自动下线逻辑均自陈未实现。同族的 WebMCP Tool Surface Poisoning（2606.06387）给出该方向的第一份安全刻画，也是本族目前唯一的受控证据：第三方脚本可在会话中注入恶意工具（Mid-Session Tool Injection），注册竞态 ASR 100%，且模型从 GPT-4o 代升级到 GPT-5.4 代 ASR 变化 0%。

Search API as Decision Surface（2607.10198，★）值得单列：它论证商业搜索 API 返回的排序摘要/URL/元数据本身就是决策面——在冻结模型下改变 API 即改变 agent 是回答、再搜还是开页——这是把"每步 context"和"外部服务契约"接起来的少数实证之一。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| · Unbrowse (shadow API) | 2604.00694 | 从真实流量被动学第一方隐藏 API 做共享路由图；加速对照的基线被削弱，无成功率指标 |
| ★★ DMI | 2510.04607 | GUI 抽象成 access/state/observation 三原语，policy-mechanism 分离 |
| ★ Search API as Decision Surface | 2607.10198 | 冻结模型下搜索 API 的返回面本身决定 agent 的下一步 |
| ★ MCP vs RAG vs NLWeb vs HTML | 2511.23281 | 同商品四种暴露方式对比；token 省约 3×，但效果优势只在意图明确的检索与交易类任务上成立（模拟） |
| ★ VOIX | 2511.11287 | 声明式 `<tool>` / `<context>` 标签暴露站点能力契约 |
| ★ CI4A | 2601.14790 | UI 组件交互逻辑封装为统一工具原语 |
| ★ webMCP | 2508.09171 | 交互元数据嵌入页面，agent 消费预结构化数据而非全 HTML |
| ★ AWI | 2506.10953 | Agentic Web Interface 六条设计原则 |
| ★ Typed Actions | 2602.17245 | 用带类型输入输出的 "web verbs" 取代点击/按键/DOM 操作 |
| ★ Beyond the GUI Paradigm | 2606.19388 | 三个 coding agent 无移动端后训练直打 AndroidWorld/MobileWorld |
| ★ WebMCP Tool Poisoning | 2606.06387 | WebMCP 工具面的首份安全刻画：会话中工具注入 |
| ★ UFO2 | 2504.14603 | Windows AgentOS，UI Automation 与视觉解析混合控件检测 |
| ★ LiteCUA / AIOS 1.0 | 2505.18829 | 把计算机变成 MCP server 暴露上下文环境 |
| ★ TheMCPCompany | 2510.19286 | 真实 REST 服务包装成 18,000+ 工具的 MCP benchmark |
| ★ ANX | 2604.04820 | CLI/Skill/MCP 统一到 3EX 解耦架构的 agent-native 协议 |
| ★ VACP | 2603.29322 | 让可视分析应用显式暴露状态、可用交互与执行机制 |
| ★ 结构化链接数据记忆层 | 2603.10700 | 七条件受控实验：纯 JSON-LD 增益有限，agent 优化版才显著 |
| ★ 互操作协议综述 | 2505.02279 | MCP / ACP / A2A / ANP 四协议对比 |
| ★ Semantic UI Element Injection | 2604.07831 | 叠加无害对齐 UI 元素误导 grounding 的黑盒红队 |
| ★ Screen Recognition | 2101.04893 | 端上 UI 检测器为 4,068 个 app 的 77,637 屏自动生成无障碍元数据 |
| · Agent-First Tool API | 2605.10555 | 人类 CRUD API 与自主 agent 的五处架构错配 |
| · Schema First Tool APIs | 2603.13404 | 信息等价下对比自由文档 / JSON Schema / Schema+校验诊断 |
| · Towards an Agent-First Web | 2606.19116 | 三层十原则的 agent-first 互联网设计 |
| · Normative Infrastructure | 2606.10711 | 立场：法规与 ToS 而非技术在阻碍 agentic web |
| · SoDA | 2512.22135 | 存储/计算/交互解耦以瓦解平台数据锁定 |
| · Agentic Web | 2507.21206 | 智能/交互/经济三维度的 agentic web 框架 |
| · MCPmed | 2507.08055 | 生信 web 服务的 MCP 化倡议 |
| · Walled Gardens | 2506.23978 | 立场：agent 让互操作成本骤降从而不可避免 |
| ✕ Syntactic-Semantic Internet | 2602.00818 | 立场文，语义层平行栈，无实证 |

### 2.3 Constructed observation：每一步给什么（14 篇）

这一族最贴近用户问题的字面含义，也是证据质量最高的两族之一。核心命题由 Signal-Driven Observation（2606.06708）说得最直白：每步吞进动辄数万 token 的原始 DOM 与 accessibility tree 是**架构错误**，应由专门子调用抽取信号。围绕"抽什么、怎么抽"分出三条路线。

**结构化重组**：PageMem（WebChallenger，2606.10423，★★）从 DOM 确定性地构造出"带摘要的语义分区层级"作为共享基底，再在其上搭三个机制；Region4Web（2605.07134，★★）把 AXTree 按功能区域做层级分解与语义抽象，产出 page-level region digest；UIFormer（2512.13438，★★）更进一步，用约束优化**自动合成** UI 变换程序（受限于 UI 操作 DSL），把接口改造从手工设计变成搜索问题。

**视觉侧构造**：Set-of-Mark（2310.11441，★★）是这条线的源头——用分割模型把图像切块并叠加字母数字标记，把 grounding 从坐标回归变成选标号。Screen2AX（2507.16704，★★）从单张截图实时生成树状 accessibility 元数据；AQuaUI（2605.19260）用自适应四叉树做免训练的视觉 token 削减。

**最有信息量的是两篇反直觉发现**：Element Ordering（2409.12089，★★）报告仅打乱页面元素呈现顺序造成的性能下降，与"删掉全部可见文本"相当（**作者自报**）——这说明表示的**编排**而非**内容**可能才是主要变量；Plans Don't Persist（2606.22953）用 replay pairing 测隐状态余弦距离，显示 plan 信号在写入后一步冲到 0.453 随后迅速衰减，即"把计划写进 context"这个常见做法的作用远比预期短命。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ PageMem / WebChallenger | 2606.10423 | 从 DOM 确定性构造带摘要的语义分区层级作为共享基底 |
| ★★ Region4Web | 2605.07134 | AXTree 按功能区域层级分解 + PageDigest 压缩 |
| ★★ UIFormer | 2512.13438 | 约束优化自动合成 UI 变换程序，接口改造变成搜索问题 |
| ★★ Set-of-Mark | 2310.11441 | 分割+叠标号，把 grounding 从坐标回归变成选标 |
| ★★ Screen2AX | 2507.16704 | 从单张截图实时生成树状 macOS 无障碍元数据 |
| ★★ Element Ordering | 2409.12089 | 打乱元素顺序的伤害≈删除全部可见文本（**作者自报**） |
| ★★ MolmoWeb | 2604.08516 | 开放视觉 web agent 与数据：10 万+ 合成轨迹 + 3 万+ 人类演示 |
| ★ Signal-Driven Observation | 2606.06708 | 立论：每步吞原始 DOM/AxTree 是架构错误，改用信号抽取子调用 |
| ★ Plans Don't Persist | 2606.22953 | replay pairing 测得 plan 信号写入后一步即衰减 |
| ★ AQuaUI | 2605.19260 | 自适应四叉树免训练视觉 token 削减，保留位置编码语义 |
| ★ LineRetriever | 2507.00210 | 规划感知的观察削减，指出嵌入检索丢失页面状态与动作历史 |
| · A11y-CUA | 2602.09310 | 40.4 小时盲/低视力与视力正常用户数据；SOTA CUA 在键盘导航下 78.3%→41.67% |
| · Affordance 表示 | 2510.24459 | DOM Transduction 与 Affordance Recognition 两个架构模式 |
| · STITCH | 2601.10702 | 用潜在目标/动作类型/实体类型索引每步，按意图兼容性检索历史 |

### 2.4 Agent 自己构造 context（18 篇）

这一族与轴 A 的边界最模糊——凡是把 context 操作训练成策略动作的，都被划到了 §3 的交叉轴；留在这里的是免训练或 SFT 层面的方案。分两支：**记忆结构**（HyMEM 2603.10291 的符号节点+轨迹嵌入图；HMT 2603.07024 的 Intent/Stage/Action 三级层级；WebCoach 2511.12997 的跨会话教练）与**主动上下文管理**（AgentFold 2510.24699，★★，把 context 当作要主动雕刻的认知工作区，学习逐步 folding；SelfCompact 2606.23525 让模型自己决定何时压缩并配抑制规则；VISTA 2606.30005，★★，把工作记忆表示为带类型可寻址块并给出运行时用量看板）。

Pensieve / StateLM（2602.12108，★★）是概念上最激进的一篇：让基础模型内建推理循环去操作记忆工具（剪枝、索引、记笔记），即模型自己工程化自己的 context，而不是接受外部固定管线。

诊断类两篇提供了这一族缺少的对照：Retrieval vs Utilization（2603.02473）在 LoCoMo 上做 3×3 交叉（三种写策略 × 三种检索），平均准确率跨度达 20 个百分点（**作者自报**）——说明这一族的"提升"高度依赖具体组合而非记忆本身；How Should Agents Read Demonstrations（2606.20978）在 85 个任务上做表示消融，动作序列完全相同、仅改演示格式，发现层级分组的子目标演示在 43 个描述模糊的任务上占优。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ AgentFold | 2510.24699 | context 作为可雕刻工作区，学习逐步 folding（细粒度凝缩/深度合并） |
| ★★ VISTA | 2606.30005 | 工作记忆表示为带类型可寻址块 + 运行时用量看板，免训练 |
| ★★ Pensieve / StateLM | 2602.12108 | 模型内建推理循环操作记忆工具，自行工程化 context |
| ★★ HyMEM | 2603.10291 | 符号节点 + 轨迹嵌入的图记忆，多跳检索与自演化 |
| ★★ HMT | 2603.07024 | Intent / Stage / Action 三级记忆树，含可观察前后置条件 |
| ★★ ReUseIt | 2510.14308 | 从成功**与失败**尝试合成可复用工作流，带执行守卫 |
| ★ How Should Agents Read Demos | 2606.20978 | 动作序列固定只改格式：层级子目标演示在模糊任务上占优 |
| ★ SelfCompact | 2606.23525 | 模型自选压缩时机，配触发/抑制 rubric |
| ★ ACE | 2606.31564 | 无损消息层 + 弹性上下文编排，按步骤重分配保留粒度 |
| ★ Retrieval vs Utilization 诊断 | 2603.02473 | 3×3 写/读策略交叉，准确率跨度 20 个百分点 |
| ★ IntentCUA | 2602.17049 | Planner/Optimizer/Critic 共享记忆，多视角意图表示与 skill 抽象 |
| ★ AgeMem | 2601.01885 | store/retrieve/update/summarize/discard 作为工具动作 |
| ★ WebCoach | 2511.12997 | Condenser + 外部记忆 + Coach 的跨会话自演化 |
| ★ Agent-SAMA | 2505.23596 | 用有限状态机表示 app 导航流，替代纯反应式屏幕推理 |
| ★ WMA web agent | 2410.13232 | 世界模型预测动作后果；用转移的自然语言摘要绕开长观察预测 |
| ★ Latent State Estimation | 2405.11120 | LLM 推断 UI 潜在状态准确率 >76%，可作为显式状态注入 |
| · HIPIF | 2606.10507 | 端到端训练围绕子目标组织执行并折叠已完成历史 |
| · ARC | 2601.12030 | 反思驱动的主动上下文管理，context 作为动态内部推理状态 |

### 2.5 Skill / workflow 复用（5 篇）

PreAct（2606.17929，★★）把一次成功的 computer-use 运行编译成小型状态机程序（状态检查屏幕、转移执行动作），重放时 8.5–13 倍加速且无逐步 LM 调用（**作者自报**）；WALT（2510.01524，★★）反向工程站点的隐含功能为可调用工具（搜索/筛选/排序/发帖/增删改）。ContractSkill（2603.20340）与 ALLOY（2510.10049）分别从"可验证契约"和"用户演示"两侧补齐 skill 的可靠性与可编辑性。这一族与 §2.2 的 shadow API 路线在做同一件事，只是一个从轨迹侧、一个从流量侧提取相同的隐藏能力。

| 方法 | arXiv | 一句话 |
|:--|:--|:--|
| ★★ PreAct | 2606.17929 | 首次成功运行编译成状态机程序，重放 8.5–13× 加速且零 LM 调用 |
| ★★ WALT | 2510.01524 | 反向工程站点隐含功能为可调用工具 |
| · ContractSkill | 2603.20340 | skill 转成带契约的可执行件，支持确定性验证与最小局部修复 |
| · ALLOY | 2510.10049 | 从浏览器演示归纳工作流，产物可视化可编辑 |
| · AgentRR | 2505.17716 | 记录-回放范式，把轨迹摘要成含工作流与约束的结构化"经验" |

### 2.6 鲁棒性与安全（2 篇）

StressWeb（2604.16385）与 WAREX（2510.03285）都在做同一件事：把受控扰动（布局变动、交互语义改变、客户端/服务端/网络故障、XSS 与恶意弹窗）注入既有 benchmark。二者是检验任何"构造式观察"方案的必需对照——如果构造出的表示在扰动下崩溃，那么它在干净基准上的增益就不能外推。

另有 8 篇归入其他，其中值得点名的是 WebNavigator（2603.20366，★★），它把"拓扑盲"命名为独立问题——agent 无法访问环境的全局拓扑结构因而被迫试错——并离线构建 Interaction Graph 供检索；以及 UI-KOBE（2605.29534，★），自主探索 app 构建 UI 状态图供端侧轻量 agent 使用。这两篇与 §2.3 的页面级构造是不同层级：一个构造**页内**表示，一个构造**页间**拓扑。

---

## 3. 交叉轴：把 context 构造当成 RL 的优化对象（23 篇）

**这 23 篇是本地图方法论上唯一非增量的部分**，因为它们取消了两轴的分工：context 操作不再是预处理，而是策略动作空间的一部分，与任务动作共同接受 credit assignment。

主线由三篇奠定。MemAct（2510.12635，★★）把工作记忆管理形式化为原地编辑操作（删除、插入），与任务表现端到端联合优化，并给出 Dynamic Context Policy Optimization 解决"上下文被改写后轨迹不再是标准 MDP"的问题。Context-Folding（2510.11967，★★）让 agent 程序化地分支进子轨迹、完成后折叠，只留简洁摘要，配 FoldGRPO 用过程奖励使折叠行为可学。IterResearch（2511.07327，★★）替换 mono-contextual 范式，每轮围绕演进中的报告重建工作区。

FoldAct（2512.22733）指出了这条路线的核心理论障碍，值得单独记住：**摘要动作不是普通动作**——它改变 agent 未来的观察空间，制造策略依赖的非平稳观察分布，违反 RL 的基本假设。任何"把压缩当成一个动作扔进 GRPO"的做法都要先回答这一条。CompactionRL（2607.05378）从另一侧回应：联合优化任务执行与摘要生成，用 token 级损失归一化加跨轨迹 GAE，让 agent 从被压缩过的轨迹里学习。

第二条线是**记忆写入的 credit**。HiMPO（2606.16285）先估计一次记忆更新的局部效用——同一 pre-write 状态下，从旧记忆与新记忆分别可恢复的任务相关信息之差——再做 hindsight 归因，这是对"记忆动作的奖励从哪来"最直接的回答。ATMem + STR-GRPO（2606.31612，★★）把 GUI 记忆从被动存储改成持续更新的执行状态，并用在线 RL 对比"有记忆/无记忆"的 rollout 取奖励。Active Context Curation（2604.11462，★★）把 context 管理与任务执行彻底解耦：轻量 RL 训练的 ContextCurator 策略配冻结的 TaskExecutor，在 WebArena 上把 Gemini-3.0-flash 成功率从 36.4% 提到 41.2%、token 降 8.8%（**作者自报**）——这是本族里少见的"固定权重、只改 context"的干净对照。

第三条线是**用构造出的世界当训练环境**：DynaWeb（2601.22149）训练 web world model 预测自然网页表示并与真实专家轨迹交错；SearchGym（2601.14615）与 SearchEyes（2607.05943）都用知识图谱做可验证的模拟搜索世界，前者解决"商业 API 太贵、静态快照有错位噪声"的取舍，后者用 Perception-Knowledge Chains 采样受限多跳路径并配 Hop-Anchored 策略优化。LiteResearcher（2604.17931，★★）给出同一问题的工程答案。

| 方法 | arXiv | 交叉点 |
|:--|:--|:--|
| ★★ MemAct | 2510.12635 | 记忆编辑作为动作，DCPO 处理上下文改写后的非标准 MDP |
| ★★ Context-Folding + FoldGRPO | 2510.11967 | 分支-折叠可学习，过程奖励监督折叠质量 |
| ★★ IterResearch | 2511.07327 | 每轮围绕演进报告重建工作区 + 效率感知策略优化 |
| ★★ CompactionRL | 2607.05378 | 联合优化任务执行与摘要生成，token 级归一化 + 跨轨迹 GAE |
| ★★ ATMem + STR-GRPO | 2606.31612 | GUI 记忆改为执行状态，在线对比有/无记忆 rollout 取奖励 |
| ★★ Active Context Curation | 2604.11462 | RL 训 ContextCurator + 冻结 TaskExecutor 的干净对照 |
| ★★ Constant-Context Skill Learning | 2605.05413 | skill 存进权重，推理仅条件于当前观察 + 确定性 tracker 的状态块 |
| ★★ HarnessX | 2606.14249 | 类型化 harness 原语的替换代数 + trace 驱动演化 |
| ★★ SearchEyes | 2607.05943 | 知识图谱做统一的数据/环境/奖励，Hop-Anchored 策略优化 |
| ★★ LiteResearcher | 2604.17931 | 同时解决合成数据不真实与实时搜索不稳定两个耦合瓶颈 |
| ★★ UI-Copilot | 2604.13822 | 主 agent 执行 + 轻量 copilot 按需提供检索/计算，TIPO 分开优化 |
| ★★ LCoW | 2503.10689 | 单独训练 contextualization 模块把复杂页面改写给行动 agent |
| ★ FoldAct | 2512.22733 | **摘要动作改变未来观察空间，制造非平稳分布，违反 RL 假设** |
| ★ HiMPO | 2606.16285 | 用记忆更新的局部信息效用做 hindsight credit |
| ★ Proactive Memory Agent | 2607.08716 | 独立记忆 agent 决定何时向未改动的行动 agent 注入提醒 |
| ★ STAMP | 2605.29324 | 程序化注入确定性记忆变量，控制何时编码、何时必须检索 |
| ★ DynaWeb | 2601.22149 | 学到的 web world model 中做 MBRL，交错真实专家轨迹 |
| ★ SearchGym | 2601.14615 | 知识图谱 + 对齐语料构成可验证搜索环境，配课程式 RL |
| ★ ComAct | 2606.13239 | 以 Windows COM 为统一可执行抽象，把软件操作变成程序合成 |
| ★ Gym-Anything | 2604.06126 | coding agent 造环境 + 独立审计 agent 按清单核验证据 |
| ★ GUI-Perturbed | 2604.14262 | 域随机化：>85% 的 grounding 模型在空间/关系指令下掉 27–56 点 |
| ★ Agentic Environment Engineering 综述 | 2606.12191 | 环境八属性八领域 + 符号/神经两种合成范式 |
| ★ Web GUI Testing 实证 | 2606.16650 | 联合变化探索策略与状态抽象，无单一策略占优 |

---

## 4. 证据边界：这批文献现在还不能支持的结论

以下每条都由独立核验环节标出，理由是存在反向证据或缺失关键对照，**不应写进任何下游综述或 idea 的立论**：

| 不能说 | 为什么 |
|:--|:--|
| 记忆 / skill 模块整体有效 | 缺预算匹配对照。2606.15017 在 token 预算约束下做同类研究得到否定结论；2603.02473 显示同一记忆思路的准确率跨度达 20 个百分点，取决于读写组合 |
| CLI / API 接口优于 GUI | 2606.24551 在匹配控制下比较 screen-only 与 skill-mediated CUA，瓶颈结论不支持单向优劣；本地图内该主张几乎全部来自 position paper |
| context 压缩单调有益 | 2606.00408 给出 masking stale observation 的 regime map——有效区间之外反转；FoldAct 指出压缩动作违反 RL 平稳性假设 |
| 某种接口设计在 WebArena 上领先 | 各提案的评测底座互不相同（自建 testbed / 模拟电商 / 单一应用），没有共同基准可比 |
| agent-native web 标准已被采纳或可被采纳 | 全部提案的部署证据止于作者自建环境；2606.04769 测得真实 MCP server 的描述-代码不一致率 9.93%（**作者自报**），说明既有生态的契约可靠性尚未达标 |
| 观察削减是纯效率问题 | 2409.12089 显示纯顺序扰动的伤害≈删除全部文本，说明削减同时改变了有效性而非仅改变成本 |

**可以说的**（同一核验环节判为受支持）：固定权重下改变每步表示会实质改变 agent 行为；每步吞原始 DOM/AxTree 在 token 上是浪费的；接口改动会移动 agent 的内部状态而未必改变终局成功率（2607.04528、2606.22953 两条独立证据）；构造出的观察在扰动下鲁棒性显著下降（2604.14262、2604.16385、2510.03285）。

轴 A 另有一条量纲级警告需要一并记住：本批约十余篇声称在 ALFWorld / WebShop 上较 GiGPO 提升 3–7 个百分点，而既有笔记 [[Papers/2607-MuonAgenticRL]] 一类工作显示，仅更换优化器就能让同一 GiGPO 基线移动约 25 点。**在优化器、学习率、随机种子未对齐的情况下，这批 3–7 点的差异不可归因于算法本身。** 同方向的直接证据见 [[Papers/2607-GRPONullWebAgent]]（学习率门控下的 GRPO 失效）。

---

## 5. 与既有笔记的衔接

38 篇候选已有笔记，它们构成本地图的锚点而非空白。按两轴归位：

**轴 A 锚点** — [[Papers/2606-AsyncWebRL]]、[[Papers/2607-SAO]]（单 rollout 异步优化）、[[Papers/2607-EvoCUA15]]、[[Papers/2602-ProxMO]]（邻近度多回合 credit）、[[Papers/2604-StepLevelOptimization]]、[[Papers/2605-T2PO]]（不确定性引导探索控制）、[[Papers/2602-ADMIRE]]（自适应里程碑奖励）、[[Papers/2602-VAGEN]]、[[Papers/2510-CUARewardBench]]、[[Papers/2605-LiteGUI]]、[[Papers/2607-GRPONullWebAgent]]。

**环境与合成锚点** — [[Papers/2601-WebGym]]、[[Papers/2606-CUAGym]]、[[Papers/2600-InfinitewebScalableWebEnvironment]]、[[Papers/2604-AgentWorld]]、[[Papers/2607-SCALECUA]]。

**轴 B 锚点** — [[Papers/2605-CodeAgentHarness]]、[[Papers/2607-HarnessHandbook]]、[[Papers/2607-AgentReadyWeb]]、[[Papers/2606-LUMOS]]（语义 OS 层）、[[Papers/2510-OSWorldMCP]]、[[Papers/2500-GuiActorCoordinateFree]]、[[Papers/2602-ActionEngine]]、[[Papers/2512-AgentProg]]。

**观察削减对照组** — [[Papers/2604-ReadMoreThinkMore]] 与 [[Papers/2605-MFSCoverage]] 两篇都在重审 web agent 的观察削减，是 §2.3 全族最重要的既有对照，任何新的削减方案都应先对上这两篇的结论。

**记忆对照组** — [[Papers/2606-NaiveVisualMemory]]（朴素视觉记忆不够用的失效模式研究）、[[Papers/2602-MemGUIBench]]、[[Papers/2606-MemGUI]]、[[Papers/2605-MementoGUI]]、[[Papers/2510-MGA]]、[[Papers/2601-MAGNET]]、[[Papers/2606-AgentMemorySystem]]。§2.4 的 18 篇新增几乎全部应先对上 [[Papers/2606-NaiveVisualMemory]] 的失效分类。

**评测诚信锚点** — [[Papers/2504-OnlineMind2Web]]（对 web agent 进展的"进步幻觉"评估）、[[Papers/2607-GUIStateBelief]]（GUI agent 是否相信自己看到的）。

**安全锚点** — [[Papers/2607-UCM]]（不可信内容遮蔽的安全保证）、[[Papers/2512-PermissionManifestsWebAgents]]。

## 6. 已识别但尚未纳入的对照实验（14 篇）

以下 14 篇由独立核验环节点名为"该地图缺少的关键对照"，标题已核实，尚未纳入正文分类。前七篇是**证伪型对照**，优先级高于本地图任何一篇新增方法论文，因为它们直接决定 §4 里哪些结论能松绑：

| 论文 | arXiv | 为什么关键 |
|:--|:--|:--|
| Are Online Skill and Memory Modules Always Worth Their Tokens? | 2606.15017 | 预算匹配下的记忆/skill 空结果 |
| GUI vs. CLI: Execution Bottlenecks | 2606.24551 | screen-only 与 skill-mediated 的匹配对照 |
| Masking Stale Observations Helps Search Agents — Until It Doesn't | 2606.00408 | 给出上下文遮蔽的有效/失效 regime 边界与机制 |
| Beyond Browsing: API-Based Web Agents | 2410.16464 | API/浏览/混合三路线的原始对照 |
| ReVision | 2605.11212 | 时序视觉冗余削减 |
| Description-Code Inconsistency in Real-world MCP Servers | 2606.04769 | 真实 MCP 生态的契约可靠性测量 |
| From Question Answering to Task Completion: Agent System and Harness Design 综述 | 2606.20683 | harness 设计的系统性综述 |
| WebAgent-R1 | 2505.16421 | 已在 [[Reports/2026-07-27-WebAgentRL-Loss-Formulas]] §B2 有公式级记录 |
| HiPER | 2602.16165 | 显式 credit assignment 的层级 RL |
| Stabilizing Off-Policy Training via Turn-Level Importance Sampling | 2511.20718 | 异步下的回合级重要性采样与裁剪触发归一化 |
| Deconstructing Off-Policy Ratios | 2607.22186 | 熵缩放信任域，异步 RL 的比率拆解 |
| Search Self-play | 2510.18821 | 无监督下推进 agent 能力边界 |
| Thinking vs. Doing | 2506.07976 | 测试时**交互**扩展 vs 测试时推理扩展 |
| Dual-Modality Adversarial Safety Training | 2603.04364 | 多模态 web agent 的跨模态攻击鲁棒化 |

## 7. 建议的精读顺序

若只读十篇，按两轴耦合度而非引用量排序：MemAct（2510.12635）→ Context-Folding（2510.11967）→ FoldAct（2512.22733，读它对前两篇的理论反驳）→ Active Context Curation（2604.11462，固定权重对照）→ Element Ordering（2409.12089，表示编排 vs 内容）→ Region4Web（2605.07134）与 PageMem（2606.10423，两种页面重构）→ Evidence-Calibrated PO（2606.05885）与 BiPACE（2606.25556，两条对 GiGPO 的独立批评）→ PASS@(k,T)（2604.14877，检验前面所有提升是否真实）。

先补 §6 的前三篇（2606.15017 / 2606.24551 / 2606.00408），再读上面十篇——否则很容易把这一批文献的共识误读成已验证结论。
