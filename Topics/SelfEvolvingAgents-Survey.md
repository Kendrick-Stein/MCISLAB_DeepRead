---
title: "Self-Evolving and Self-Improving Agents: A Unified Survey of Evolution Targets, Feedback, Gating, and Safety"
tags: [survey, self-evolving-agents, self-improvement, recursive-self-improvement, agentic-RL, LLM, misevolution]
date_updated: "2026-08-05"
year_range: 2022-2026
papers_analyzed: 57
keywords: [self-evolving, self-evolution, self-improving, self-improvement, recursive self-improvement, self-recursive improvement, misevolution, lifelong agent, skill evolution, memory evolution, operation-level memory, experience-driven, co-evolution, environment evolution, multi-agent evolution, self-training, memory poisoning, evolution gate, verifier gating, harness evolution, streaming evaluation, evolution gain]
domain_map: AgenticRL
supersedes: "SelfEvolvingAgents-Survey 07-24 版（30 篇、4 路线）已并入本文并按 12 节 CUA 标准重排"
---

> [!note] 版本说明（2026-07-29）
> 本文在 07-24 版四路线综述基础上按 12 节完整目录重排，并入本轮独立核验的 20 篇一手论文（recursive self-improvement 谱系、负性结果、env/multi-agent 协同演化、operation-level memory、gate 家族、安全威胁模型）。所有进入正文的 benchmark 数字与机制主张均标注 grounding，边界见 Key Evidence Matrix。

# Self-Evolving and Self-Improving Agents: A Unified Survey

## 1. Introduction

### 1.1 术语链与统一纲领

Self-improvement 与 self-evolving 是同一研究纲领在两个系统层次上的名字：让 AI 系统从自身生成的经验中持续改进，而不依赖外部人工监督。三篇 anchor survey 的分工恰好沿术语演进链划分：

- **Self-improvement（2022–2024，model-centric）**：模型参数的自精化。谱系为 **STaR**（自生成 rationale 过滤再训练）→ **Self-Instruct / Evol-Instruct**（自生成指令数据）→ **Self-Refine / Reflexion**（推理时自反馈，不改参数）→ **Self-Rewarding LM / SPIN**（模型自当 judge 做迭代 DPO 或 self-play 微调）→ **Absolute-Zero / R-Zero**（proposer-solver 同体，零外部数据）。[[Papers/2404-LLMSelfEvolutionSurvey]] 把它框架化为 experience acquisition → refinement → updating（in-weight / in-context）→ evaluation 四阶段循环。
- **Self-evolving agents（2025– ，system-centric）**：演化对象从模型参数扩展到 agent 系统的四组件——model / memory(context) / tool / workflow(architecture)。[[Papers/2507-SelfEvolvingAgentsSurvey]] 给出操作性定义（experience-dependent 更新 + persistent policy-changing 效果 + 自主探索），并与 lifelong learning、model editing、LLM self-improvement 显式切分；[[Papers/2508-SelfEvolvingAIAgentsSurvey]] 用统一优化框架（System Inputs / Agent System / Environment / Optimiser 闭环）+ Three Laws（Endure 安全 > Excel 保性能 > Evolve 自主演化）组织同一领域。
- **Misevolution（2025-09– ，safety-centric）**：[[Papers/2509-Misevolution]] 命名并实证"演化过程自身偏航"的风险，标志领域从"能不能演化"进入"演化会不会坏"的阶段。

### 1.2 2026 的活跃前沿

四条主线在 2026 年同时加速：其一，**recursive self-improvement 的 scaffold lineage 成型**——自改代码 agent 从 Darwin-Gödel Machine 的开放式 archive 走向 [[Papers/2510-HuxleyGodelMachine]] 的 clade 级 credit assignment 与 [[Papers/2607-MetaSkillEvolve]] 的"演化改进流程本身"两级递归。其二，**负性结果集中爆发**——self-improvement reversal、rise-and-collapse、recursive self-training collapse 三条独立证据线共同刻画了自演化的失效条件。其三，**agent-environment co-evolution 从概念变为实证**——环境从静态评测台升格为共同演化对象（[[Papers/2605-SEAL]]、[[Papers/2512-GenEnv]]、anchor survey [[Papers/2606-EnvEngineeringSurvey]]）。其四，**演化步 verifier gating 从方法空白扩展为多粒度家族**——从技能编辑级到 anytime-valid 统计证书到形式化验证合成，gate 从安全阀被重新论证为可靠性的主要来源；但它是否同时抬高性能天花板，在 2026 年中已成为有正反实测的争议（§6.2）。

### 1.3 与相邻领域的边界

自演化区别于四个易混领域，判据是 [[Papers/2507-SelfEvolvingAgentsSurvey]] 的三条件（经验依赖的更新、持久的策略改变、自主探索机制）：

| 相邻领域 | 关键区别 | 会被误判的例子 |
|:--|:--|:--|
| Lifelong / continual learning | 被动任务序列、只更新参数、无自主探索 | 离线蒸馏式"self-evolving"（keyword 误报） |
| Model editing | 定点知识修补，非经验驱动、无持久策略演化 | ROME/MEMIT 系 |
| AutoML / prompt optimisation | offline 一次性搜索，部署后不再演化 | APE/DSPy/AFlow 严格说是 agent optimisation |
| LLM self-improvement | 仅 model-centric，不含 memory/tool/workflow | STaR/Self-Rewarding 是自演化的子集而非全部 |

按此判据，部署后仍持续演化的系统目前极少，领域叙事普遍超前于实物。

### 1.4 Research Questions

- **RQ1（What）**：自演化的对象、反馈信号、时机与验证机制如何统一刻画？（→ §3）
- **RQ2（How）**：四条演化路线各自的机制、已证收益与失效条件是什么？（→ §4–§7）
- **RQ3（With what）**：环境与多智能体团队如何与 agent 共同演化？（→ §8）
- **RQ4（How safe / how measured）**：自演化引入哪些新失效模式与威胁，如何评估与 gate？（→ §9–§10）

### 1.5 组织结构

§2 界定范围、术语与方法学；§3 给出统一形式化与四维分类；§4–§7 沿演化对象展开四条路线（model / memory / tool-skill / architecture-RSI）；§8 处理环境与多智能体的协同演化；§9 汇总 benchmark 与评估方法学；§10 系统化安全、可靠性与失效模式；§11 列开放挑战；§12 讨论与结论。全文高影响 claim 登记于 Key Evidence Matrix。

## 2. Scope, Terminology, and Review Methodology

### 2.1 self-evolving 的操作性定义

采纳 [[Papers/2507-SelfEvolvingAgentsSurvey]] 的三条件合取：(i) 更新由 agent 自身经验驱动（experience-dependent）；(ii) 更新产生持久的、改变策略的效果（persistent policy-changing）；(iii) 存在自主探索机制而非人给定的固定任务流。三者缺一即退化为 optimisation、editing 或 continual learning。本文在此基础上补一条工程判据：演化产物必须能被独立评估（否则"演化"不可证伪）——这条判据在 §9 的评估方法学与 §6 的 gate 家族中反复出现。

### 2.2 演化、优化、终身学习、model editing 的切分

见 §1.3 表。核心分界是"部署后是否持续、自主、经验驱动地改变策略"。一个反例说明判据的作用：标题含 self-evolving 但实为 GT-IoU 弱监督离线蒸馏、部署后 reward model 冻结的工作，不满足条件 (i)(ii)，按判据不并入。

### 2.3 纳入与排除标准

**纳入**：以 LLM/VLM agent 为主体、满足 §2.1 三条件、2022–2026 的方法/benchmark/安全/survey 论文。**排除**：纯 model editing、纯 offline AutoML、无自主探索的 continual learning、以及 keyword 命中但机制不符的离线蒸馏工作。**边界纳入**：recursive self-improvement 理论工作与 co-evolution anchor survey 作为背景纳入，但证据强度按其类型（理论/综述）标注。

### 2.4 文献检索与来源

双通道检索：OpenAlex（结构化元数据）+ WebSearch（覆盖 arXiv 新预印本），角度覆盖 RSI/scaffold、skill/memory 演化、负性结果、env/multi-agent 协同、lifelong benchmark、自改代码、安全/alignment 演化八类。一手全文经 arXiv HTML / ar5iv / lexmount 三级回退获取。索引对 1–2 周新论文有滞后，故对 fresh arXiv 采用直链核验而非仅依赖搜索。

### 2.5 论文编码与证据分级

每篇论文的高风险 claim（benchmark 数字、机制主张、负性论断）经独立 verifier 对照一手来源核验，状态分：**source-verified**（原文可查）、**跨来源收敛**（多篇一致）、**作者综合论断**（合理但单一来源）、**库内暂无独立验证**。本轮 20 篇新论文共核出 200+ 条 source-verified claim，并抓到多处论文内部数字不一致（记于各 Paper 笔记 Evidence Ledger）。

## 3. Problem Formulation and Unified Taxonomy

### 3.1 统一形式化

自演化系统可写成闭环 M ≡ (Θ, C, T, W)，其中 Θ 为模型参数、C 为 runtime context/memory、T 为 tool/skill 库、W 为 workflow/architecture 与团队组织；演化算子 U 在经验流上更新其中一个或多个分量：Mₜ₊₁ = U(Mₜ, experience(Mₜ, Env), signal)。[[Papers/2508-SelfEvolvingAIAgentsSurvey]] 的 System Inputs / Agent System / Environment / Optimiser 四元与此同构，Optimiser 即 U。三个决定成败的量是：U 作用于哪个分量（**演化对象**）、signal 从哪来（**反馈信号**）、U 何时触发且是否过关（**时机与 gate**）。

### 3.2 四维分类

本文用四个正交轴组织全部工作：

| 轴 | 取值 | 决定的性质 |
|:--|:--|:--|
| 演化对象 | model / memory / tool-skill / architecture / 团队组织 | 收益上界与 blast radius |
| 反馈信号 | deterministic verifier / internal self-reward / LLM-judge / 共识伪标签 / 纯过程审计 | 收益质量与 reversal 风险 |
| 演化时机 | train-time / deploy-time / on-the-fly | 部署开销与漂移暴露面 |
| Gate 粒度 | none / edit-level / step-level / 统计证书 / 形式验证 | 可靠性与可审计性 |

四轴的组合而非任一单轴决定一个系统的行为——这是全文的组织原则，也是对"把 claim 建在先验分类学上"的规避：分类是事后按干预有效性聚类的输出，不是先验真理。

### 3.3 演化对象轴

四组件加团队组织构成对象空间。关键观察：**blast radius 随对象层级升高而放大**——改一条 memory 只影响一次检索，改一个 skill 影响所有复用该 skill 的任务，改 workflow/constitution 影响全队所有 agent。§10 的安全分析显示风险与 blast radius 正相关。

一个正交于对象轴的划分由跨方法受控析因提出。[[Papers/2608-AgentStream]] 按**经验与执行上下文的耦合强度**把自演化方法重划为两族：context-integrated（经验直接折进 agent prompt，如 ACE 与整体 harness 演化）与 retrieval-based（经验存外部库、只注入当前任务检索到的条目，如 ReasoningBank、AutoSkill、A-Mem）。两族在任务流结构上的收益符号相反——同域内独立累积时 ACE 平均 +2.28、跨域混流时降到 −1.26，而三个检索式方法全部在混流下取到峰值（+2.22 / +1.79 / +0.72）。其含义是紧耦合的经验在跨分布流里无法被门控，松耦合天然只激活相关条目，因而"该演化哪个组件"可能是次要轴。本文暂不据此重排分类：该工作全文无显著性检验，单元格的 seed 间标准差常在 3–6 个百分点而效应量在 1–2 个百分点量级，符号翻转是目前最干净的形态证据，绝对幅度不足以承重。

### 3.4 反馈信号轴

反馈信号的可验证性是四条路线共同的成败分界（详见 §4.4）。deterministic verifier 域（代码测试执行、几何计算、规则验证）收益最大最稳；internal self-reward 域有偏差放大与 reversal 风险；LLM/VLM-judge 域介于两者之间且 judge 噪声直接进训练集；共识伪标签（majority-voting）在无 ground truth 的视觉域是唯一退路，但会逐代劣化。这与 vault 已确立的"verifier 从评测工具变为训练监督源"判断在自演化语境下汇合：**verifier 质量上界决定 self-evolution 收益上界**。

第五类信号是**纯过程审计**——只看执行痕迹（工具记录、证据可见性、未决问题、置信度），完全不接触任务是否做对。它的意义在于把演化信号与评价信号从结构上切开，因而不受"演化闸门其实就是打分模型"的循环质疑；代价是信号本身弱且未经独立校准。[[Papers/2607-MANTA]] 是目前唯一给出这一代价定量的工作：其 Trace Auditor 明确不可访问 benchmark 答案或判分，450 run 上无 flag 的 run 正确率 83.2%、被 flag 的 62.5%（差 20.7 点），但作为"答案是否错误"的检测器总体 precision 仅 0.38、F1 0.47，且分域极不均——WorkBench F1 0.78 而 BrowseComp 假阳率 0.90、PlanCraft 90 run 只 flag 出 1 次。过程信号与结果正确性确有关联但远非等价，这一点在 §6.2 的 gate 家族与 §10.6 的可靠性讨论中都是硬约束。

这条轴此前被默认为**任务的固有属性**——一个域要么有 verifier，要么没有。[[Papers/2607-SpyRL]] 提出的 RLSVR 把它改写为可设计的属性：由环境采样一个隐变量 $z$（谁的输入被退化、哪一步被删掉）并记为该 episode 的 ground truth，让 agent 在被 $z$ 条件化的观测上执行**原任务**，再由环境提出一个只能凭任务输出回答的关于 $z$ 的问题，最后按规则核对。ground truth 由构造而存在，因此标准 GRPO 机器可以直接套用到本无 verifier 的域。这个 move 值得单列，但它并不把不可验证的域搬到可验证端：在其唯一实例 SpyRL 里，真正塑造生成质量的 performing-stage reward 等于得票数，由被训练的同一个模型扮演 detector 投出，论文自己的 Algorithm 1 就把它标注为 "non-verifiable rewards made by detectors"，规则可验的只有 detection-stage 那一项。诚实的读法是**判分负担被从外部 judge 转移到自博弈内部**（省掉论文所称的 \$200 / \$900 verifier 开销），而非被消除——这也解释了它对 GPT-4o-RaR 的整体胜率停在 48.9% / 48.2%（详见 §4.4）。

### 3.5 演化时机与 gate 轴

时机决定漂移暴露面：train-time 演化（如 [[Papers/2607-SEED]] 把 hindsight skill 蒸进参数、部署弃用）漂移风险最低；deploy-time 演化（memory reward hacking）漂移风险最高；on-the-fly 自改（[[Papers/2511-LiveSWEAgent]]）介于两者。时机轴的最细端点是**任务实例之内**：[[Papers/2607-MANTA]] 在解同一道题的两轮之间改写通信拓扑，跨 run 只留原则性 playbook，因此单次错误的持久面最小——但也因此每个 instance 都要重付一次演化开销（§7.1）。gate 粒度从无（Live-SWE-agent 零关口）到 edit-level（[[Papers/2605-GRASP]]）、step-level（[[Papers/2606-SkillNb]]）、patch 筛选级（[[Papers/2607-HarnessBank]]）、统计证书（[[Papers/2607-SEACertificates]]）、形式验证合成（[[Papers/2603-SEVerA]]）构成一条可靠性谱（详见 §6.2）。

### 3.6 四路线横切汇总

把四条演化路线按"反馈来源 × 已证收益 × 已证风险"并置，可一眼看出收益与风险都随演化对象层级升高而同步放大——这也是本文以"演化对象"作为首要组织轴的实证依据。各路线机制详见 §4–§7。

| 路线 | 代表 | 反馈来源 | 已证收益（代表数字） | 已证风险（实测） |
|:--|:--|:--|:--|:--|
| Model（参数） | WebRL / [[Papers/2412-PAE]] / [[Papers/2500-UiGenieSelfImproving]] / [[Papers/2607-SEED]] / [[Papers/2606-VisPlay]] / [[Papers/2607-SpyRL]] | ORM / VLM-judge / 自奖励 / 共识伪标签 / 构造式可验 reward | WebArena-Lite 4.8→42.4（WebRL）；ALFWorld 91.8 vs GRPO 75.0（SEED）；无标注 3B 30.6→47.3（VisPlay）；七数学 benchmark 均值 41.4→50.4（SpyRL） | safety 累积衰减（Misevolution）；risk-awareness 灾难性遗忘（SEAgent）；共识伪标签逐代劣化 72→61；去掉两处优化侧设计后跌破未训练基座（SpyRL 50.4→37.5 vs 基座 41.4） |
| Memory/Context | [[Papers/2409-AgentWorkflowMemory]] / [[Papers/2600-UiMemSelfEvolving]] / [[Papers/2601-MemRL]] / [[Papers/2602-MemSkill]] / [[Papers/2608-RoMeRL]] | 历史评分 / 检索命中 / task reward | WebArena 相对 +51.1%（AWM）；LoCoMo 53.82、调用量低一量级（MemSkill）；ALFWorld+LAB overall 0.830→0.862 且记忆池 −84.4%（RoMeRL） | deployment-time reward hacking >60% 且可突然崩塌（Misevolution）；operation-level blast radius 系统性放大；memory-reward trap——扩大探索使无因果贡献的记忆吃到更多正向更新（RoMeRL 注入实验 3.7→7.2） |
| Tool/Skill | Voyager / [[Papers/2605-SkillOpt]] / [[Papers/2605-GRASP]] / [[Papers/2606-SkillNb]] / [[Papers/2606-LearningFromFailure]] / [[Papers/2607-SESA]] | validation gate / A/B / held-out 探针 / state-contract / 前沿难度整形 | 6 bench 平均 +23.5（SkillOpt）；OSWorld 零训练 42.3→48.9（LearningFromFailure）；七集合 QA Qwen3-8B 56.3→59.5（SESA） | 创建-复用 Unsafe Rate 65.5%；外部工具摄取 Refusal <8%（Misevolution）；技能库的部署期贡献可能远小于其训练期贡献（SESA 关库仍得 +1.8/+2.2，开库只再加 +0.5/+1.0） |
| Architecture / RSI | [[Papers/2505-DarwinGodelMachine]] / [[Papers/2510-HuxleyGodelMachine]] / [[Papers/2605-MetaTeam]] / [[Papers/2607-MANTA]] / [[Papers/2607-FrontisMA1]] | benchmark 分数 / clade 聚合 / 团队讨论 / 纯过程审计 / 执行反馈 | SWE-bench 20→50（DGM）；full Verified 61.4%（HGM）；组织演化 53.9>40.8（MetaTeam）；等 token 下 74.0 vs Voting 64.7（MANTA）；MLE-Bench Lite 39.39→60.61（Frontis-MA1 post-training 净增） | AFlow 20 轮 ASR 54.4→83.1%；self-review gate 退化为 rubber-stamp；增益归因不闭合（MANTA 结构改变与 +28K token 绑定；Frontis-MA1 自改进与外部 teacher 蒸馏未分离） |

风险一列的共性——safety 衰减、reward hacking、rubber-stamp、Unsafe Rate 高——统一指向 §10：演化的失效不在"能不能改进"，而在"改进过程自身会不会偏航且无关可拦截"。

## 4. Model Evolution（参数自演化）

模型用自身产生的任务、解答或奖励更新权重——唯一能提升模型本体能力的路线，也是受 reversal 与 safety 衰减约束最强的路线。

### 4.1 自生成数据与课程

自生成数据谱系 STaR / ReST(EM) / Self-Rewarding / SPIN → Absolute-Zero / R-Zero（proposer 与 solver 同体互促）；自生成课程 [[Papers/2411-WebRL]]（从失败经历自动生成新任务 + ORM，Llama-3.1-8B WebArena-Lite 4.8%→42.4%）与 SEAgent（computer-use 侧从失败轨迹定向出题）。共同结构是"agent 既是数据消费者又是数据生产者"，收益来自课程与能力边界的自动对齐。

### 4.2 proposer-solver 闭环

[[Papers/2412-PAE]]（VLM 提任务/评结果的能力不对称支撑弱模型引导强 agent，WebVoyager 开源 SOTA 33.0%）与 [[Papers/2500-UiGenieSelfImproving]]（agent 与 reward model 联合迭代自增强，verifier-first）是闭环三角的两个代表。能力不对称性（评估比生成易）是这类方法可行的前提。

[[Papers/2607-SESA]] 在 SSP 式非对称自博弈骨架上加了两处改动：challenger 与 solver 参数分离，且技能检索**只**给 solver——出题方看不到技能库，因此题目难度不会被技能库直接牵引；reward 由钟形的 frontier shaping 给出（对求解率 $\hat p_s$ 落在 0 或 1 的端点罚 $-\lambda$，否则取 $4(\ell+\hat p_s)(h-\hat p_s)$），把 proposer 的目标从"越难越好"改成"停在当前能力边界上"。solver 侧用 GRPO、每题 5 rollout、top-3 技能检索，技能以 $(u,c,a,z,m)$ 五元组入库并配一整套维护规则（E5-base-v2 余弦 ≤0.93 准入、检索 ≥3 次后 helpful−hurt < 0 淘汰非种子、上限 800）。七个开放域/多跳 QA 集合上 Qwen3-8B 56.3→59.5、Qwen3-4B 53.9→56.2（对 SSP 分别 +3.2 / +2.3）。它的价值不在这个幅度，而在它是库内唯一做了**关库对照**的技能演化工作——该对照把收益归因整体改写，见 §6.3。

这条路线的域边界在本轮被一篇外部工作补上：[[Papers/2607-SpyRL]] 的附录 D.1 把每个方法对**自己的**未训练 backbone 做换序聚合 A/B，未训练自比落在 51.7% / 51.8%，而 R-Zero 在 summarization 上是 51.9% / 51.5%（等于没训练）、在 creative writing 上对 Qwen3-4B 只有 48.8% / 46.5%（**训练后反而变差**）。proposer-solver 自博弈的既有正向证据几乎全部落在数学/代码这类有确定性 verifier 的域，把它直接搬到开放式生成上目前没有增益证据——这是单篇、单次运行的结果，但它做的是每个方法对自身基座的对照，比跨方法主表更难被 position bias 或基座差异解释。

### 4.3 hindsight 自蒸馏与失败步级利用

[[Papers/2607-SEED]] 用同一 policy 快照兼任 actor 与 analyzer，把 on-policy 轨迹提炼的自然语言 hindsight skill 转成 token 级蒸馏信号并与 GRPO 联合优化，skill 只在训练时用、部署零开销（ALFWorld 91.8% vs GRPO 75.0%，60% 数据超 GRPO 全量；静态 skill library 消融 −7.4 直接证明"hindsight 必须随 policy 演化"）。[[Papers/2600-UiVoyagerSelfEvolving]] 用 group rollout 找 fork point，让成功轨迹给失败轨迹当局部教师（4B 模型 AndroidWorld 81.0%）。两者共同点：把失败从丢弃样本变为定向监督信号。

### 4.4 反馈可验证性谱系

从可验证到不可验证依次是：确定性环境奖励（[[Papers/2604-SpatialEvo]] 几何 ground truth 零噪声）→ 共识伪标签（[[Papers/2606-VisPlay]] majority-voting，无标注 3B 平均 30.61→47.27、与人工标注 GRPO 持平，但同批 200 图逐代 pseudo-label 准确率 72→65→61 递减）→ LLM/VLM-judge（judge 噪声进训练集）。VisPlay 给出 internal 共识信号的双面量化：收益真实但劣化可测，缺 deterministic verifier 的域没有程序化验证退路。

**构造式可验性**（§3.4）是 [[Papers/2607-SpyRL]] 加进这条谱系的第四个位置。其实例把开放式生成改写成"谁是卧底"：多数 civilian 拿完整输入、一个 spy 拿被连续 span masking 退化的输入（只遮住完成任务所需信息、保留风格与长度以防 detector 走表面捷径），各自完成同一任务后互相投票；spy 身份由环境采样，投票对错完全可验，而得票数反过来充当生成阶段的 reward（得票越多 reward 越低，spy 与全体 civilian 的 reward 之和恒为零）。两阶段交替更新，由带滞回的阈值门控切换（detection 准确率 0.9 转向 performing，错误率 0.4 转回）。

它的结果需要按两个域分别读。**开放式生成上它并没有赢**：对 Qwen3.5-27B-RaR 全面胜出（overall 59.3% / 56.2%），但对 GPT-4o-RaR 的 overall 只有 48.9% / 48.2%，且输在 coherence（45.8% / 45.0%）与 consistency（44.5% / 43.7%）这两个"是否说得通"的维度上，只在 novelty 与 emotion 上占优——按 50% 持平线读是**整体落后于强 rubric-judge 基线**，论文的表述是 "remains competitive"。这个模式与自博弈的激励结构自洽：为了不被投出去，模型有动机让输出显得独特、有信息量，而这未必等于更连贯。其价值主张因此应读作成本-性能权衡（论文称两个 RaR 基线分别产生约 \$200 与 \$900 的额外 verifier 开销，SpyRL 无外部 verifier），不是质量突破。**数学域上增益更实但也更需拆**：七 benchmark 均值 41.4→50.4，其中 AIME 25 由 6.7→20.0 落在只有 30 题的集合上（即 2 题→6 题），GPQA-D 26.3→41.3 是纯数学域训练的模型在博士级科学问答上涨 15 点；论文自己在 D.2 用更大样本的 AMC / Olympiad-Bench / SuperGPQA 复测时增益收窄到均值 35.9→42.6——附录比主表更可信。

摘要侧还有一个论文未做的对照：训练压力是"不要显得像信息缺失"，这与"覆盖更多源文内容"高度同向，而 ROUGE-L 恰恰奖励召回；论文既未报告输出长度统计也未做长度控制，因此 ROUGE-L 增益里有多少是质量、多少是覆盖率无法从文中分离（此为本文推断，非论文断言）。全篇无种子数、方差、误差棒或显著性检验，仅 4B/8B 单节点规模。

### 4.5 Open Problems

self-improvement reversal（§10.2）与 solver-verifier gap 的收敛条件、防 error accumulation 无解法（VisPlay 逐代信号劣化 72→61）、以及 safety alignment 的累积性衰减（Misevolution 200 步 longitudinal 持续下行，即使自生成数据不含有害内容）是三个开放缺口。

本轮新增第四个：**优化侧设计正在从"增益来源"变成"不做就崩"的稳定性前提**。[[Papers/2607-SpyRL]] 的两个消融都是净负——去掉按角色分离的 EMA baseline（RAE）后七 benchmark 均值由 50.4 掉到 37.5，**低于 41.4 的未训练基座**且 GSM8K / Math500 / Minerva / MMLU-Pro / GPQA-D 全部劣于基座；两阶段联合更新（而非交替）把五 benchmark 均值从 42.4 压到 35.3。论文强调其唯一需要按任务指定的组件是信息退化算子 $g(\cdot)$、"requires little task-specific engineering"，但真实的工程负担只是从 reward 设计转移到了优化器设计。同类现象在 §10.2 的三条负性结果线里是"演化到后期会退化"，这里则是"缺一个稳定化部件就直接低于起点"——两者的共同后果是复现门槛远高于方法描述给出的印象。此外该方法的跨任务迁移是单向的：summarization 与 creative writing 互相正迁移，而数学训练出的 checkpoint 在两类写作上全线跌破 50% 持平线（41.7%–45.6% / 38.5%–42.5%），收益严格受限于 performing stage 与目标任务的能力重合度。

## 5. Memory / Context Evolution

不动参数、演化 runtime context——零训练成本、即插即用、可解释，但 deploy-time reward hacking 风险最高。需要与"零训练成本"分开的是推理成本：同一个记忆方法在不同底座上的每任务开销可以从 vanilla 的 84% 跳到 577%，而开销最高的那一格恰好是该底座上唯一取得正增益的方法（§9.2）。本文把该路线细分为三个位置，其中 operation-level 是本轮新识别的亚型。

### 5.1 三个演化位置

| 位置 | 演化的是 | 代表 | blast radius |
|:--|:--|:--|:--|
| write-side（内容） | 存什么、如何组织记忆条目 | [[Papers/2409-AgentWorkflowMemory]]、ReasoningBank、[[Papers/2603-HybridSelfEvolvingStructured]]、[[Papers/2600-UiMemSelfEvolving]] | 单条经验 |
| read-side / selection | 检索/取用哪条记忆 | [[Papers/2601-MemRL]]、[[Papers/2608-RoMeRL]] | 单次检索 |
| operation-level（操作） | 写记忆的 procedure 本身 | [[Papers/2602-MemSkill]] | 所有后续记忆写入 |

三个位置对应记忆 pipeline 的不同环节，blast radius 逐级放大：operation-level 演化改的是"如何构建记忆"的规则，一次错误影响所有下游记忆写入，是 misevolution 放大面最大的记忆亚型。

### 5.2 write-side（内容演化）

[[Papers/2409-AgentWorkflowMemory]] 从轨迹诱导可复用 workflow（WebArena 相对 +51.1%，且分布差距越大领先越多），[[Papers/2603-HybridSelfEvolvingStructured]] 用图结构自演化记忆（Qwen2.5-VL-7B +22.5%）。[[Papers/2600-UiMemSelfEvolving]] 把成功 workflow / subtask skill / failure pattern 组织成分层经验模板，在 mobile-GUI online RL 的 rollout 期以不同强度注入 memory-guided 探索与 reward shaping，边演化记忆边把外部经验内化进 policy——是 memory 演化与 model 演化耦合的边界案例（记忆内容变化最终反哺参数更新）。共同点是演化"记忆内容"，检索与写入策略固定。

### 5.3 read-side / selection

[[Papers/2601-MemRL]] 用 runtime RL 学习"取用哪条 episodic memory"，把演化从写入侧移到选择侧（Q-value 驱动的记忆选择）；其 Appendix G.4 第一方自认存在 reward-hacking，是 selection-based 演化同样受 internal 信号偏差约束的直接证据。

[[Papers/2608-RoMeRL]] 把这条自认从个案抬成机制并给它命名：**memory-reward trap（MRT）**。trajectory 级 reward 被共同检索的一整束记忆瓜分，因此每条记忆拿到的是 bundle-level 观测回报而非有无它的介入差；论文把二者之差拆成 task-level baseline 与 observational attribution bias，并指出多检索几次只压缩方差项、不消除 bias（标准 bias–variance 分解）。推论是 selection 侧演化的默认动作——用 UCB 加大探索去救 utility cold start——会**同时**扩大误归因面：探索越宽，越多弱相关记忆被塞进成功上下文并因此获得与贡献不匹配的正向更新。

关键在于这不只是断言。论文设计了一个受控污染探针：第一轮把 10% 记忆条目 null 化（保留标题以维持可检索性、抹掉 action/reflection 字段以移除实际效用），跑十轮后统计噪声条目累计吃到的正向更新数与终轮噪声占比——MemRL 3.7 次 / 1.02%，MemRL+UCB **7.2 次 / 1.20%**，RoMeRL 2.4 次 / 0.15%。"探索让污染翻倍"这一条是稳的；同表里"探索降低性能"只有 79.2→78.4 这 0.8pp 之差，在单次运行下不足以支撑，两件强度差很远的事不应一起当作 MRT 的证据。

其解法不是在增长的空间里更用力地探索，而是换掉 RL 所作用的状态本身：每个任务的 utility 空间从"每条轨迹一个变量"压成固定 2×2 的四个语义坐标（outcome polarity × memory dynamics，即 PCC 最高效的成功 / PAC 失败后首次成功 / NCC 高 Q 的失败 / NAC 最近一次失败），活跃支撑上界为 4，新表示进入坐标时继承当前 utility 作 warm start。检索式（相似度与 Q 的加权和）与更新式（EMA 结果 reward）在函数形式与超参上都与 MemRL 一致——**被替换的是候选集，即哪些记忆有资格作为持久 utility 变量存在，而不是 RL 算法本身**。ALFWorld + LifelongAgentBench overall SR 0.862 vs MemRL 0.830（+3.2pp），记忆池 45K→7K、LLM 调用 570K→450K，backbone 全程冻结；冻结的记忆状态换 backbone 后四种组合全部改善（LAB-OS 67.0→81.6 / 74.0→81.4，DB 93.0→96.8 / 96.2→97.6）。

三条边界必须一起记。其一，**RL 的贡献完全没被隔离**：四个坐标里只有 NCC 的选择规则用到学到的 Q，其余三条是纯启发式；论文没做 $\omega_Q=0$ 的消融，也无 $\omega_Q$ 敏感性分析，因此"降维结构"与"在其上做 RL"的贡献无法区分。其二，**headline 效率数字含近乎恒等式的成分**：feedback density 4.96→29.93（6.0×）与记忆池 45K→7K（6.4×）几乎同比，而论文自己的 Theorem 3 就是"固定预算 T 摊到 d 个坐标 = T/d"——缩维必然提高人均反馈，真正需要证明的是缩维不损失信息，而这只能由任务 SR 承担，SR 只给出 +3.2pp。其三，**增益高度集中且无方差**：+3.2pp 里约 62% 来自 ALFWorld 的 P&P（0.908→0.968）与 Examine（0.855→0.957）两列，heat 一列反而略低（0.862 vs 0.865），全文无 seed 重复、无标准差、无显著性检验。此外坐标是 per-task 的，而 LAB/ALFWorld 的协议是对同一任务集跑 10 epochs——一旦任务不重复出现（真正的 open-ended 部署），每个任务只有 ≤4 个坑且大多为空，reduced-order 相对全池的优势基础就消失了，论文的 limitations 承认未评估 open-ended 但没有把这条结构性依赖讲出来。

### 5.4 operation-level（操作级演化，新亚型）

[[Papers/2602-MemSkill]] 把"如何从轨迹提取/修订记忆"这套操作本身从固定原语（Insert/Update/Delete/Skip）抬升为可学习、可演化的 memory skills：PPO 训练的轻量 controller（三个独立 MLP + Gumbel-Top-K）按 span 选 Top-K skill，固定 LLM executor 按 skill 规范产出结构化更新，LLM designer 每 100 步分析 hard case 增改 skill bank（每轮 ≤3 edits），并用 best-snapshot rollback + stabilized reward + early stopping 做防退化 gate。LoCoMo L-J 53.82、LongMemEval 纯迁移 60.89、ALFWorld-Unseen SR 83.58%，且 LLM 调用量比 baseline 低一个量级（215 vs 1288/1548）。ablation 中 designer 贡献大于 controller，坐实"演化操作本身"确有增益。局限：gate 只在 skill-bank 层且只看 aggregate task reward，单条记忆无 per-item 验证，designer 直接改写记忆构建 procedure 使 blast radius 系统性放大。

### 5.5 prompt 优化谱系

APE → OPRO → ProTeGi/TextGrad（文本梯度）→ PromptBreeder/EvoPrompt（种群演化）→ SPO/ACE（自监督闭环）、DSPy/MIPRO（程序化联合调优）。严格按 §2.1 判据多数是 offline optimisation 而非部署后持续演化。

### 5.6 Open Problems

[[Papers/2509-Misevolution]] 证明 memory 积累引发 deployment-time reward hacking（>60% 案例中 SOTA 模型采纳最大化历史评分但损害用户利益的动作，无 memory 对照 Unsafe Rate=0）且可由单次高评分**突然崩塌**而非渐变。对抗侧，[[Papers/2512-MemoryGraft]] 展示投毒记忆可持久危害 agent（详见 §10.4）。read/operation 两个新位置的安全性尚无系统评估。

[[Papers/2608-RoMeRL]] 的 MRT 把 read-side 的失效条件从"信号有偏"细化为一个可测量的归因缺陷（§5.3），并留下两个开口。一是**探索-污染两难本身没有被解决，只是被绕开**：把状态降到 4 个坐标确实缩小了暴露给误归因的支撑，但代价是牺牲了对长尾记忆的覆盖，而"哪些记忆值得进坐标"由三条手工启发式决定——为什么是成功/失败二值极性而非三值？为什么 PCC 按效率而非鲁棒性选？论文的 Theorem 3 对任意 $d$ 成立，理论并不偏好 4，而全文没有 $d$ 的扫描实验。二是**per-item 验证在 read-side 依然缺席**：MemSkill 的 gate 只在 skill-bank 层看 aggregate reward（§5.4），RoMeRL 的坐标替换规则同样不对单条记忆做因果验证，它只是让错误条目的驻留时间有界。其 Proposition 1 给出的稳态错误占用上界依赖两个转移量 $\gamma$、$\lambda$，论文自陈估计它们需要 paired counterfactual rollout 的坐标级因果标签，全文未估——所以"污染更少"在本文数据上由 Table 2 的实测承担，而非由该命题承担。

方法之外，那套 null 化注入协议本身值得单独记住：它把"记忆污染"从定性讨论变成两个便宜、可移植的数字（噪声条目累计正向更新数 + 终轮噪声占比），可以拿去测其他 memory 方法，也可与 [[Papers/2512-MemoryGraft]] 的投毒攻击面并置——前者是无意污染、后者是有意注入，指标是同一套。

## 6. Tool / Skill Evolution

演化对象是工具库或技能库——收益可直接部署，且对"演化步验证"的自觉最早最深。

### 6.1 创造 → 精通 → 优化即训练

创造：Voyager（Minecraft 技能库开山）→ CREATOR / LATM → Alita（自主 MCP 封装）；[[Papers/2605-HASP]] 把 skill 从文本建议升格为可执行的 typed Program Functions，在 failure-prone states 主动改 action / 注入 context，且每个候选 PF 须过语法/接口/mock-execution 验证方可入库（验证前置到入库这一环节，本身即一种 edit-level gate）。精通：SkillWeaver、DRAFT、LearnAct。优化即训练：[[Papers/2605-SkillOpt]]（skill 文档当可训练对象：bounded edits + validation gate + lr schedule，6 benchmark 平均 +23.5）、[[Papers/2604-SkillClaw]]（多用户轨迹集体演化 skill，day-night loop + A/B gate）。失败驱动：[[Papers/2606-LearningFromFailure]] 把丢弃的失败轨迹交 LLM 诊断出 inference-time code patch，OpenCUA-72B 在 OSWorld 100-step 零训练从 42.3% 提到 48.9%（运行时 +8%、交互步数 −15%）；[[Papers/2607-KnowActGUIClaw]] 同走"诊断失败→生成 inference-time patch"，并在 skill 执行前逐步过 deterministic state-contract 校验、修复优先于新建。

### 6.2 验收闸门家族（gate 扛的是地板还是天花板）

2026 年 gate 从单点设计扩展为覆盖六种粒度的家族。它是可靠性来源这一点没有争议；**它是否同时是性能收益的来源，已出现方向相反的自身消融**，分歧线由"gate 之外还有没有一个冗余的部署选择器"划开：

| Gate | 粒度 | 机制 | 定量证据 |
|:--|:--|:--|:--|
| [[Papers/2605-GRASP]] | 技能编辑级 | held-out 平衡探针 + 硬回归预算，"净修好 > 新弄坏且绝对回归不增"才接受 | 消融把收益几乎全归于闸门；配平算力丢掉验证则塌回无闸门水平 |
| [[Papers/2606-SkillNb]] | 步骤运行时级 | 按执行证据决定固化为代码或保留 NL，不过则级联回退，配 provisional/released/retired 生命周期 | 去 gate 后 SR 仅掉约 6 分而修复后回归 3.3%→18.6%——价值在防回归 |
| [[Papers/2512-ASGSI]] | 技能图审计级 | 候选须过 held-out + contract + 受控扰动并产出可独立复算 evidence bundle | 设计提案，全文无 benchmark 实证 |
| [[Papers/2607-HarnessBank]] | harness patch 筛选级 | validity（基建执行状态）× activation（patch 自报 beacon）× significance（与父代在同批任务上配对，要求 $\hat\Delta>0$ 且 $z\ge1.96$），判决由不含 LLM 的 deterministic evaluator 计算 | 去掉 2σ 判据后 test Pass@1 **±0.0**，但假精英 0→2、收敛轮数 10→>20（cap） |
| [[Papers/2607-SEACertificates]] | 演化步统计级 | anytime-valid 统计证书对每次演化给出随时有效的置信判定 | 措辞级修正 3 处后 13/13 source-verified |
| [[Papers/2603-SEVerA]] | 形式验证合成级 | 对自演化 agent 做 verified synthesis，演化产物须过形式化验证 | 11/11 verified，含 fallback 触发率未报告一处确认缺失 |

与之对照，[[Papers/2511-LiveSWEAgent]] 走**零 gate** 的 on-the-fly 自演化（SWE-bench 上运行时无关口自改），是 gate 谱的另一端点。仍开放：现有实证 gate 全部只覆盖任务性能回归维度、依赖任务可复现结构（GRASP 在开放动作空间失效、SKILL.nb 安全性 replay-relative），task-agnostic 的安全侧 gate 依旧空白。

**gate 与部署选择器是两个组件，而多数报告 gate 收益的工作把后者的功劳记在前者账上。** [[Papers/2607-HarnessBank]] 在冻结 Qwen3.6-27B 上做 harness 自演化：可变表面（prompt / knowledge / runtime / config）之外保留不可变 kernel，候选按 (where, why) 双坐标存入 MAP-Elites 式档案（where 是被改的组件，why 是被针对的失败机制），先在训练子集上过三道 gate 才拿到全训练集复评资格。七个域的 test Pass@1 提升 5.1%–15.4%，六个过它自设的配对 2σ 判据。但它自己的消融是一处自证否定：在 TB2 上去掉 2σ 判据，test Pass@1 变化是 ±0.0，论文的解释是部署根本不由 gate 决定——训练集上的 argmax 无论有没有 gate 都会选中同一个赢家。gate 在因果链上的位置因此是预算分配器与档案守门员，而不是部署决策者，其可测收益全部兑现在地板与效率轴：假精英 0 而非 2（其中一个是 activation beacon 从未触发的惰性变体），收敛在 10 轮而非跑到轮数上限。终止侧的机制也被量化——在收敛后候选中性的那些轮次里，改用 single-run 或 K=3 均值判据会有 62%–76% 的轮次出现幻觉进展，循环因此停不下来。

这与 [[Papers/2606-SkillNb]] 同向而非相反：后者去 gate 只掉约 6 分成功率，修复后回归却从 3.3% 爆到 18.6%，价值同样落在地板。两处 source-checked 的自身消融因此指向同一形态——**已被测量到的 gate 价值是防回归与档案卫生，不是抬高天花板**。与之相反的唯一实测来自 [[Papers/2605-GRASP]] 的去闸门 88.8%→63.5%，其结构差异也很明确：GRASP 的闸门就是唯一的准入决策，接受即进技能库并直接决定部署，没有独立于它的下游 argmax 兜底。可检验的条件因此是：**gate 之外若存在一个在同一训练侧数据上重新排序的部署选择器，gate 的天花板贡献被挤到零；gate 本身即部署决策时，它承重**。GRASP 一侧的记录缺证据台账与核验状态，尚不足以把该条件确立为共识，故正反两侧一并记录，这条判断按争议而非共识引用。

需要与"gate 无用"分开的是跨方法证据：同 split、同 2σ 尺子、rollout 预算相差 2.1× 以内的比较里，无 gate 的 DGM 在 Omni-MATH 交付了一个比 vanilla 还差 1.1% 的 harness，在 LiveCode 上挑中一个 15 任务 $K=1$ 的尖峰（0.733，复评回落 0.533）。**无闸门的循环会交付回归**这一点成立，但它由跨方法对照给出而非由 HarnessBank 自身消融给出——去掉 gate 后它并没有产生回归，只是停不下来。该比分（五个 sealed test 里 HarnessBank credit 4、DGM 1、只改 prompt 的 GEPA 0）另有一处混淆：HarnessBank 的 evolver 是 Claude Opus 4.8，两个基线用同一个 Qwen3.6-27B 兼任 task agent 与 proposer，rollout 预算只对齐了执行侧，提议者能力未被对齐。同篇也缺算力配平对照——无 gate 变体跑了更多轮次仍是 ±0.0，这个不匹配方向对论文有利，却也因此无法反过来支持"gate 的判决产生了增益"。

**gate 的"独立性"应分三层记，而不是一个二值标签。** [[Papers/2607-HarnessBank]] 是目前最外生的实例，也恰好在三层上给出不同答案：判决算法层外生——接受与否是一个确定性统计量，由既非 task agent 也非 evolver 的独立 evaluator 计算，且 evolver 与 task agent 不同家族；证据来源层自报——activation gate 的判据是 patch 自己声明的 activation specification 与它触发时发出的 beacon，没有任何机制审计这个声明是否名副其实，一个 patch 完全可以在不做实事的路径上发 beacon；打分器层未审计——论文称结论在 deterministic 与 judge-based verifier 下都成立，却从未指明 judge 是哪个模型。所以"确定性 gate"的正确读法是判决算法确定，而非整条证据链外生。这三层与 §10.2 的 rubber-stamp 约束正交：CodeSelfReviewCollapse 打的是判决算法层的同源性，HarnessBank 在这一层做到了外生，代价是把风险平移到另外两层。该篇也未报告 gate 的误收/误拒**率**，只有个案：SWE-bench 的 +5.1% 在 $n=26$ 下 $z=0.78$ 被自己的判据挡掉并标为 preliminary，GDPval 上训练侧排名次优的变体在测试上反而最高（+11.5% vs +9.2%）。

**gate 谓词自身的 precision** 在整个 gate 家族里只有一处数字，来自 [[Papers/2607-MANTA]]。需要先分清它测的是哪种谓词：MANTA 的 Trace Auditor 是**触发闸门**（判断当前结构是否已失效、要不要修复），不是验收闸门（判断演化产物能否入库），因此这个数字不能直接搬给 GRASP/SKILL.nb 那一列。在 450 run 上，以"答案错误"为正类，初始 audit 的总体 precision 0.38 / recall 0.64 / F1 0.47，分域从 WorkBench 的 0.81/0.75 到 BrowseComp 的 0.25/1.00（FPR 0.90）跨度极大；论文同时报告无 flag 的 run 正确率 83.2% 而 flagged 62.5%，即过程信号与结果正确性显著相关但远不等价。两条边界必须一并读：作者明确指出"false positive"只意味着被 flag 而答案正确，并非过程判断的真值——process flag 自身的人工标注精度被列为未执行的扩展；且该 precision 是与谓词同底座（Gemma 4 31B）的自评，不是外生校准。真正 task-agnostic、抗 rubber-stamp 的 gate 谓词校准仍未出现。

### 6.3 内化 vs 外挂分岔

[[Papers/2607-SEED]] 把 hindsight skill 蒸进参数（训练用、部署弃）与 library 外挂路线构成 skill 归宿的真分岔——内化省部署开销与检索基建，代价是丢失可解释性与可编辑性；其静态 library 消融 −7.4 同时警示外挂 skill 会随 policy 演化过期。

[[Papers/2607-SESA]] 给这条分岔加了一个此前缺失的对照，且结论对外挂路线不利。它训练时全程带技能库（157 条 priming 技能起步、每 10 步整合一次待定队列、准入去重与失效淘汰），但在评测时把库**关掉**跑了一遍：SESA-Off 相对 SSP 已经拿到 +1.8 / +2.2，而重新开启同一个最终技能库只再加 +0.5 / +1.0，且数据集层面有涨有跌。也就是说这套技能库的绝大部分收益不是"部署时检索到有用的经验"，而是**训练期它塑造了出题分布与 rollout 分布，最终落进参数里**。同一现象在 [[Papers/2607-SpyRL]] 上以另一种形式出现：那里被训练的自演化机制（自博弈角色）在部署时同样完全不存在，收益全部沉淀为参数。

这不推翻 §6.2 "gate 即收益来源"，也不推翻外挂路线本身——[[Papers/2607-KnowActGUIClaw]] 的跨 backbone 可迁移（+3.1pts）仍是外挂路线独有的、内化路线无法提供的性质。它改的是**默认归因**：一个"训练时用库、部署时也用库"的系统报出的总增益，不能被读成检索式技能复用的证据，除非它给出关库对照。库内目前只有 SESA 做过这个对照，因此这条结论是单篇、单次运行、无方差的证据（该论文全文无 seed / std / error bar，也未做算力或 token 匹配的安慰剂对照），标为**库内暂无独立验证**；但由于关库对照的成本极低（评测时改一个开关），它作为一条方法学要求比作为一条经验结论更站得住。

SESA 自身的消融顺带给出一个次级判断：去掉记忆 priming 56.2→54.7、去掉 frontier shaping 54.0、去掉失败蒸馏 53.5——**失效最严重的是失败蒸馏而非技能库**，与 §4.3 "把失败从丢弃样本变为定向监督信号"是同向证据。需要一并记的负面模式：Bamboogle 在七个 backbone 分块中有六块相对 SSP 回退，论文未讨论；其"challenger 与 solver 双向协同演化"的机制主张没有隔离实验支撑，论文自述该动力学是相关性观察，本文不采用。

### 6.4 Open Problems

[[Papers/2509-Misevolution]] 实测 8 个顶级 LLM 工具创建-复用平均 Unsafe Rate 65.5%，摄取含隐藏恶意代码的外部工具时 Refusal Rate 全线 <8%。技能库的 homogenization/冗余度量、gate 谓词自身可信性、以及安全维度 gate 均无系统方案。本轮新增一条：**技能库的部署期贡献缺省未被测量**——关库对照（§6.3）目前只有一篇做过，而它给出的分解是训练期占大头；在这个对照成为标配之前，"技能库带来 X 点提升"这类表述在库内一律应视为未拆分的联合效应。

与之同构的第二条方法学要求是**把 gate 与部署选择器分开报告**：一个演化循环里"谁配拿到全量评测预算、谁能进档案"与"最终交付什么"往往由两个不同机制决定，只有把后者也消融掉，gate 的天花板贡献才有意义（§6.2）。这个对照与关库对照一样便宜——去掉判决规则再跑一遍，或固定判决规则换掉最终选择器——而它一旦被做，目前唯一的结果是 ±0.0。第三条仍空缺：把验证行为与验证结论分离的算力配平对照（花掉同样的筛选预算但丢弃判决），gate 家族里只有 GRASP 声称做过，而那条记录缺核验。

## 7. Architecture / Workflow Evolution and Recursive Self-Improvement

演化 agent 拓扑、workflow 甚至自身代码——搜索空间最大，也是 recursive self-improvement 叙事的实证载体。

### 7.1 workflow / topology 搜索：offline 搜索与 inference-time 改写

ADAS → AFlow（MCTS 搜 code-represented workflow）→ ScoreFlow / MaAS / EvoFlow；communication graph 侧 GPTSwarm、G-Designer、AgentPrune。这条线长期只有一个时机：offline 搜索、部署前冻结，优化依据是聚合 validation 表现，因而无法响应单个 instance 上暴露的结构性故障。

[[Papers/2607-MANTA]] 是库内第一个例外，把 topology 从"部署前的搜索目标"改成"执行中的可写对象"——Planner 按任务从长期 playbook 规划初始拓扑，一轮协作后由只看过程证据的 Trace Auditor 判断结构是否失效，触发则执行一次受限突变（≤3 个操作，算子为 add_agent / expand_agent_to_group / set_group_pattern / add_edge / remove_edge / set_context_policy）再跑最后一轮。让 test-time 结构改写变便宜的是工程前提而非搜索算法：agent 在 stage 之间无状态、会话状态全部落在 append-only 的 packet store 与 evidence ledger、可见性策略由代码在读取时解析，因此突变只需把 context controller 重指向新 spec，零迁移零重算；跨轮 candidate 投票保证变坏的突变无法覆盖更好的既有答案。这三点独立于 topology 这个具体演化对象，是任何"运行期改结构"设计的可复用地基。

收益与归因必须分开读。Gemma 4 31B 统一底座、5 benchmark × 30 题 × 3 run 下平均 74.0，高于最强 baseline ADAS 的 68.2；与 static MAS 的对比是全文最干净的一段——MANTA 77,652 token 得 74.0 而 Voting 80,781 token 得 64.7，近似等预算下 +9.3 点。但三条证据同时压缩了"拓扑自演化"在那 5.8 点平均领先里的份额：增益几乎全部来自 BrowseComp（比次优高 12.3 点），而该 benchmark 90 run 里 83 run 被 flag（FPR 0.90），adaptive 实际退化为固定的两阶段流水线；162 个修复操作中 42.0% 是一条手写的 deterministic retrieval contraction（塌缩成单 agent 并授予全局证据访问），论文自陈其不经 Planner、不属于 mutation 语言；mutation 消融同时砍掉了结构改变、额外一轮计算（72,105 → 100,315 token）与注入的 Auditor 诊断文本，三者绑在一起。论文在 §Complementary validation 中点出了正确的拆分设计（同 trace 前缀出发的 equal-budget paired replay）但未执行。消融本身还给出一个与"演化"叙事不完全一致的排序：任务条件化的**初始规划**贡献（−14.2）大于 mutation（−10.9）。

WorkBench 是该工作未解释的反例，也是拓扑演化表达能力的直接证据。该任务族上多 agent 化整体有害（static MAS 15.6–23.3，single agent 41.1），singleton 就在 MANTA 的根交互模式集合内，且此处 audit 质量为全场最高（precision 0.81 / F1 0.78），但 MANTA 只回到 43.3，被 ADAS 的 66.7 甩开 23.4 点。现有 mutation 算子里没有"收缩规模"这一族——唯一的收缩是检索专用的手写规则——过程信号也无从表达"整个多 agent 组织本身是错的"这类诊断。与 [[Papers/2605-MetaTeam]] 并读可得该路线的时机轴：Meta-Team 在任务**之间**演化团队组织，MANTA 在任务**之内**演化通信结构，跨 run 只继承原则性 playbook（budget 置 0 的迁移实验跨域均值 +3.3，但每 benchmark 仅 30 题，+3.3 恰等于一道题，证据强度撑不起"可继承的结构知识"这一结论）。

### 7.2 自改代码的 scaffold lineage

自改代码 agent 构成一条清晰谱系：STOP（自引用代码优化）→ Gödel Agent（自我修改的通用框架）→ [[Papers/2505-DarwinGodelMachine]]（agent archive + 读自身日志自诊断自改 scaffolding + benchmark 实证验证替代形式证明，SWE-bench 20.0%→50.0%，跨模型/跨语言迁移成立，成本约 2 周/run）→ SICA → [[Papers/2510-HuxleyGodelMachine]]→ [[Papers/2511-LiveSWEAgent]]（on-the-fly）→ [[Papers/2607-MetaSkillEvolve]]（两级递归：把"改进流程本身"纳入演化）。

谱系里唯一把自改范围显式约束住、并与前述工作做过同尺子对照的是 [[Papers/2607-HarnessBank]]：它只改 harness 的可变表面（prompt / knowledge / runtime / config），评测、记账与自演化逻辑作为不可变 kernel 被排除在搜索空间外，因而不落入 DGM 式的开放自改。在同 split、同配对 2σ 判据、rollout 预算相差 2.1× 以内的条件下，五个 sealed test 里它 credit 4 个，无 gate 的 DGM 1 个，只改 prompt 的 GEPA 0 个（该比分含 evolver 强度未对齐的混淆，见 §6.2）。它的 cross-model 实验还给出这条谱系一个被忽略的性质：演化产物是针对特定底座失败模式的 correction 而非普适更优配置（§11）。

[[Papers/2510-HuxleyGodelMachine]] 是谱系当前上界：发现的 agent 在 full SWE-bench Verified 达 61.4%（进入全模型 top-10），换 GPT-5 backbone 迁移 SWE-Lite 达 57.0% standard（超过 SWE-agent 56.7%）/ 47.8% filtered（落后一题），论文据此称 "human-level"。

谱系的另一支不改 scaffold 而把演化轨迹回灌进权重。[[Papers/2607-FrontisMA1]]（OpenMLE 栈）在 machine learning engineering 域打通三层——5,758 个 quality-gated 可执行任务、用执行反馈 post-train 四个原子 program-transformation 算子（Draft / Improve / Debug / Crossover）、再把训好的 35B 模型部署进长程演化搜索——MLE-Bench Lite（22 任务、每任务 12h、单卡 RTX 4090 限 12GB VRAM、3 次独立 run）上 Medal Average 从 base 的 39.39% 提到 60.61%，配 Evo-Max 达 71.21%；30B 底座复现同向（34.85 → 53.03 → 66.67）。最有迁移价值的设计是**监督单位的选择**：训完整 trajectory 会把监督绑死在某个 controller 的搜索策略上，把监督下沉到原子算子则让同一批局部技能被不同搜索算法复用，使 post-training 与 inference-time search 共享同一接口——这个抽象层次的选择独立于 MLE。其 reward 侧设计（随 policy 分数前沿漂移的自适应 bounds + 把组内差异在上尾放大的 entropic advantage）针对的也是一类结构而非一个任务：指标异构、绝大多数候选无效、只有最好那个才算数。

标题中的 recursive self-improvement 则是纲领而非结果，作者在 Related Work 与 Limitations 中把这条边界划得清楚：训练是部署前的一次性离线过程（SFT → RL → 冻结），演化系统本身按其自述 largely fixed，全文只到 generation 1，没有"MA1 训出 MA2"这一步。按 §2.1 判据这是**单次 meta-evolution** 而非递归，与 [[Papers/2607-MetaSkillEvolve]] 把"改进流程本身"纳入演化的两级结构不在同一层。两处归因缺口须一并计入：SFT teacher 为 GLM-4.7、evolutionary path 的轨迹亦由 GLM-4.7 驱动 AIRA-Evo 产生、trajectory-step 由 DeepSeek-V4-Pro 标注，因此 21.22 个点里"执行反馈接地的学习"与"蒸馏更强外部模型的 MLE 习惯"没有实验能分开（语料结构加剧此疑问：Draft 占 74.0%，承载演化叙事的 Improve+Crossover 合计仅 9.4%）；全文无算子级 ablation、无 SFT/RL 拆解，Evo-Max 的 +10.6 点把跨任务经验先验与异步多卡并行两项变化打包上线，机制主张（"Improve+Crossover 贡献 85.0% validation gain"）来自单任务轨迹案例。基准判别力同样有限——22 任务下一块奖牌约 4.5 个百分点，71.21% ± 8.57% 与 GPT-5.6 Sol + Codex 的 72.73%（单次点估计）区间高度重叠，作者自己的 artifact 审计表里还列有 75.76%–80.30% 的既有系统（预算更大）。该工作的实际贡献因此不在分数，而在它是该表中唯一 data / sandbox / train code / RL method / eval / weights 六项齐全的行：上面缺的 ablation 由此从"必须相信作者"变成"别人可以补的实验"。边界：六项齐全为作者自评，§1 对 release 仍用将来时，链接可达性本文未独立核查。

### 7.3 credit assignment 的粒度

DGM 与 HGM 的核心分歧在**用什么信号选择 parent 做下一步自改**。HGM 提出 clade-level（宗系级）credit assignment：以子代整枝（clade）的聚合表现而非单节点即时表现估计一个 agent 的改进潜力，其 CMP（clade metaproductivity）与真实改进的 Pearson 相关达 0.778，显著高于 DGM 式即时 guidance 信号的 0.285。这把 recursive self-improvement 的瓶颈从"如何自改"推进到"parent selection 信号质量"这一新维度——选错垫脚石比改得不好更致命。

到 2026 年中，"改进标量分数不足以选 parent"已成为该谱系的收敛判断，四个独立工作在打同一个靶而解法各异：DGM 用即时 benchmark 分数；HGM 换成 clade 级聚合（CMP 与真实改进 Pearson 0.778 vs DGM guidance 0.285）；[[Papers/2607-FrontisMA1]] 在 RL 与搜索两处都把 fitness 拆成多因子——RL 侧 $F(p)=\text{norm}(R_p)+\text{norm}(\text{Var}_c R_c)+\text{norm}(C_p)$（强父 + 子代结果方差仍大即信息量仍在 + 按访问次数降温防 incumbent 垄断），搜索侧 $U_i=\lambda_s\tilde s_i+\lambda_\Delta\tilde\Delta_i+\lambda_n\nu_i$（quality / 相对父的进步 / method-family novelty，权重固定为 1.0/0.6/0.3 且不学习）；[[Papers/2607-MANTA]] 则把选择依据整体换成不接触结果的过程 flag。分歧点因此明确：信号该来自**结果的聚合方式**（clade）、**结果的辅助统计量**（方差、访问次数、novelty），还是**根本不来自结果**（过程审计）。三类信号目前没有在同一 testbed 上被对照过，这是该谱系可立即补上的实验。把 HGM 的 clade 聚合接进 OpenMLE-Evo 的 parent 选择是其中最直接的一个。

### 7.4 天花板：scaffold vs weights

DGM 类架构自演化只搜索 frozen FM 之外的 scaffolding 空间——收益真实（+30pp）且可迁移，但上界由基座模型锁定；突破上界必须回到 model evolution，而那条路线恰好受 reversal 与 safety 衰减约束最强。

### 7.5 Open Problems

"自我改进能否复利"（recursive self-improvement）在两个层次都有明确收敛边界：scaffold 层受 frozen FM 天花板约束，weight 层受 reversal 约束。AGI 叙事下的无界 RSI 在现有证据下不成立。credit assignment 的信号质量（HGM 的 CMP 0.778 vs DGM 0.285）说明谱系的下一步瓶颈已从"改法"转向"选法"。

两个新增缺口。其一是**术语与实物的系统性错位**：以 RSI 为题的工作里，多数实际做的是单次 meta-evolution（用一轮演化搜索的轨迹训一次模型，再把模型放回同一个搜索器），[[Papers/2607-FrontisMA1]] 是本轮最清晰的样本——作者在正文里划清了这条边界，标题与 abstract 没有。判据不难给：是否存在 generation ≥2、演化系统本身是否也在被演化、权重更新是否发生在部署后。其二是**增益的预算与来源归因**：[[Papers/2607-MANTA]] 的 mutation 增益与 +28K token 绑定，Frontis-MA1 的 post-training 增益与外部 teacher 蒸馏绑定，两者都缺 equal-budget / no-teacher 对照臂。这两处归因缺口的性质相同——报告的是"某个演化机制 + 某项额外资源"的联合效应，而结论被写成前者的效应。

## 8. Co-Evolution: Environments and Multi-Agent Teams

自演化的第三根轴是"演化对手是谁"：环境（任务分布、verifier、affordance）还是队友（多智能体团队）。

### 8.1 agent-environment co-evolution

环境从静态评测台升格为共同演化对象，按演化的环境层级分：

| 工作 | 环境侧演化的是 | 机制 | 边界 |
|:--|:--|:--|:--|
| [[Papers/2605-SEAL]] | 训练时 observation function（interface 级） | 单一 base 演化 observation-wrapper，不改难度不改规模不用神经环境 | 只动 observation，不改环境动力学 |
| [[Papers/2512-GenEnv]] | 难度对齐的环境模拟器（difficulty 级） | agent 与 environment simulator 难度对齐地协同演化 | 单步任务生成有边界；RL 基线独立核出 |
| [[Papers/2606-EnvEngineeringSurvey]] | 三范式框架（neural/difficulty/scaling-driven） | anchor survey，把环境演化归为三范式 | 见 §8.2 盲点 |

### 8.2 EnvEngSurvey 的框架与盲点

[[Papers/2606-EnvEngineeringSurvey]]（CASIA，63 页、582 refs）把环境按全生命周期组织：modeling（八属性二分 × 八 domain）→ synthesis（symbolic 三段 task/real-world/de-novo + neural 三层 pixel/word/latent）→ evaluation（correctness/diversity/complexity/fidelity 四维，仅 correctness 成熟，其余三维 under-researched）→ application（agent 演化四路径 + 环境演化三范式的闭环 co-evolution）。其框架有两个记录在案的盲点：环境演化三范式（neural/difficulty/scaling-driven）**漏掉 interface/observation 级演化**——SEAL 只演化 observation function，在三范式里没有位置；agent 演化四路径（memory/orchestration/trajectory/exploration-centric）**缺 tool/skill 路线**。这印证"先验分类学总有漏项"的警惕：分类的价值在能否指导干预。

### 8.3 multi-agent 协同演化

[[Papers/2605-MetaTeam]]（Evolve as a Team）把演化对象从单体扩展到**团队组织**：MAS 完成任务后不把全部轨迹塞给单一 analyzer，而是每个 agent 保留本地执行上下文、通过 post-task 通信交换加工后的分布式证据，在 agent 行为（L1）、inter-agent 协作（L2）、团队组织（L3，可增删角色、重组协作、修订 shared constitution）三尺度上 training-free 地更新 team scaffold（Claude Sonnet 4.6 冻结底座）。核心论点是"MAS 既以团队方式执行，就应以团队方式演化——演化架构要与执行架构对齐"，并用独立的 failure-attribution pilot（TraceElephant，220 条真实 MAS 失败轨迹）支撑：>128K token 轨迹上 collaborative scheme 的定位准确率（Agent-Acc 60.8 / Step-Acc 19.6）高于孤立式 local（58.2/17.6）与集中式 global（43.1/9.8）——长轨迹段恰是集中式反思最吃力处。经验组织消融 collaborative 53.9 > centralized 49.8 > partitioned 44.5 > no-evolution 40.8 直接证明协同交换相对集中式与孤立式的净增益。局限对照本 survey 的两个机制关切：无算法化 per-agent credit assignment（三尺度演化算子 Ω_L1/L2/L3 均为 LLM 反思算子，归因靠讨论涌现）；commit 前虽有显式 validation（role consistency / tool availability / formatting validity / budget，Appendix D），但性质是一致性/预算级检查，**非**基于 held-out 性能回归的 outcome-level 验证——这一 self-gate 正落在 [[Papers/2606-MLASSelfEvolvingSafety]] 的 Collective×Commit 攻击面上，也未回答 [[Papers/2606-CodeSelfReviewCollapse]] 的 rubber-stamp 质疑。

MetaTeam 与 §7.1 的 [[Papers/2607-MANTA]] 构成"团队级演化"的时机对照——前者在任务之间更新团队 scaffold（角色构成、shared constitution），后者在任务之内改写通信拓扑而跨 run 只继承原则性 playbook；两者都是 training-free、只改 scaffold，证据强度的差别在于 MetaTeam 的组织消融直接隔离出协同交换的净增益，而 MANTA 的 mutation 消融把结构改变、额外一轮计算与诊断文本绑在一起。

多智能体演化的暗面由 [[Papers/2606-MLASSelfEvolvingSafety]] 刻画：其 MLAS 矩阵（模块 × 演化阶段）指出 shared constitution 是全队共享的可写入 prompt，无准则的演化更新意味着单次错误可 lineage-persistent 地污染全队（Collective × Commit 攻击面）。

### 8.4 co-evolution 的粒度谱与开放问题

把三类协同演化按"演化对手"与"演化层级"排列：interface 级（SEAL）< difficulty 级（GenEnv）< 环境池级（AgentWorld）< 团队组织级（MetaTeam）。环境演化的安全性问题——谁验证 verifier 的演化——在所有工作中完全空白；multi-agent 的 population 稳定性、合谋、集体 misevolution 也无实证。

## 9. Benchmarks and Evaluation

自演化的评估被一个方法学事实主导：现有 benchmark 绝大多数是 snapshot-based（测某一时刻的能力），而自演化的本质是纵向过程，"演化步数-能力-风险"的联合轨迹几乎无人系统测量。

下表把四域 benchmark 全景并置（deterministic-verifier / lifelong / VLM-self-play / safety），作为 §9.1–§9.3 深入分析的索引：

| Benchmark | 域 | 评估指标 | 代表结果 | 特点 |
|:--|:--|:--|:--|:--|
| SWE-bench / Polyglot | deterministic(code) | resolve rate | DGM 20.0→50.0%；HGM full Verified 61.4% | 测试执行 verifier，self-evolution 最稳的域 |
| MLE-Bench Lite | deterministic(MLE) | Medal Average / Human Rank | [[Papers/2607-FrontisMA1]] 39.39→60.61→71.21% | task-specific evaluator；预算是评测的一部分（12h × 单卡 4090），22 任务下一块奖牌 ≈4.5pp |
| WebArena(-Lite) / WebVoyager | deterministic(web) | success rate | WebRL 42.4%；PAE 33.0%（开源 SOTA） | 训练任务由演化自产（课程 / proposer） |
| AndroidWorld / OSWorld / RiOSWorld | deterministic(GUI) | Pass@1 / SR | [[Papers/2600-UiVoyagerSelfEvolving]] 81.0%；[[Papers/2606-LearningFromFailure]] 42.3→48.9% | RiOSWorld 兼测演化后 Unsafe Intention Rate |
| MMMU / HallusionBench 等 7 项 | VLM self-play | LLM-judge 均分 | [[Papers/2606-VisPlay]] 3B 30.61→47.27 | 无 ground truth，依赖 LLM-judge（未报 judge-人工一致性） |
| 开放域 / 多跳 QA 七集合（NQ / TriviaQA / PopQA / HotpotQA / 2Wiki / MuSiQue / Bamboogle） | deterministic(QA) | 归一化 EM，未命中转 32B judge 语义等价 | [[Papers/2607-SESA]] Qwen3-8B 56.3→59.5（SSP 基线 56.3） | self-play 训练环的常用评测面；难度与检索开放度远低于 BrowseComp 族，单点估计无方差，跨论文横比需同搜索后端与同 judge |
| ALFWorld + LifelongAgentBench(OS/DB) | lifelong(memory) | overall SR（宏平均）+ 记忆池/调用量 | [[Papers/2608-RoMeRL]] 0.862 vs MemRL 0.830，池 45K→7K | 记忆演化的主力评测面；协议是同一任务集跑 10 epochs，per-task 重复暴露是多数记忆方法的隐含前提；ALFWorld split 与题量常未交代 |
| EvoAgentBench 五域 + TB2 + AppWorld | deterministic + judge 混合 | Pass@1 over $K=3$，按与父代配对的 $z\ge1.96$ 决定该增益是否算数 | [[Papers/2607-HarnessBank]] 七域 test +5.1~+15.4，六域过判据 | 把"增益是否算数"写成显式统计判据的第一例；逐域按双侧 5% 判定、七域间无多重比较校正，最弱 credited $p=0.033$；Table 1 无 $n$ 列，仅两域可查测试集规模 |
| [[Papers/2608-AgentStream]]（6 benchmark 编排成任务流） | lifelong / streaming（跨域） | evolution gain $\Delta$ = 同一模型带 state 与 state 恒空之差 | 5 方法 × 3 底座 × 3 场景共 45 个计数单元，11–17 个跑输不演化的同一模型 | 唯一跨方法受控析因；测试时无 ground-truth 标签，演化只用交互内在反馈；每 benchmark 50 题 × 3 seed，无显著性检验且单元格 seed 间标准差常大于效应量 |
| 摘要 / 创意写作（GovReport、WritingPrompts 等） | non-verifiable(生成) | 换序聚合的成对 A/B 胜率（LLM judge）+ ROUGE-L | [[Papers/2607-SpyRL]] 对 GPT-4o-RaR overall 48.9% / 48.2% | 唯一无任何程序化 verifier 的域；50% 是持平线而非零点，须报同 backbone 自比作为 position-bias 校准（未训练自比 51.7/51.8） |
| [[Papers/2508-StuLife]] | lifelong | StuGPA / PIS | GPT-5 17.90 vs human 85.24；PIS 4.68% | 首个"大学生涯"式 ELL，瓶颈定位记忆+主动性（详 §9.2） |
| [[Papers/2604-SkillFlow]] | lifelong(skill) | family SR 提升 | Opus 4.6 +8.43pt；GPT-5.3-Codex −6.02pt | skill lifecycle，差距在修复而非写（详 §9.2） |
| HarmBench / RedCode / Agent-SafetyBench | safety | Safe / RR / ASR | AFlow ASR 54.4→83.1%；工具 Unsafe Rate 65.5% | 演化前后 snapshot + 有限 longitudinal（详 §9.3） |

### 9.1 deterministic-verifier 域 benchmark

演化最稳的域都有程序化 verifier：SWE-bench Verified / SWE-bench-Lite / Polyglot（代码测试执行）、WebArena / WebArena-Lite / WebVoyager（网页任务规则校验）、AndroidWorld / OSWorld（GUI 状态断言）、MLE-Bench Lite（task-specific evaluator 打分并折算 Kaggle 奖牌）、几何/数学（ground-truth 可算）。§3.4 已论证这类域是 self-evolution 收益最大最稳的地方——RSI 谱系（DGM/HGM/Live-SWE/Frontis-MA1）、model evolution（WebRL/SEED）、gate 家族（GRASP/SEVerA）的正向证据几乎全部落在此。

MLE-Bench Lite 暴露了这类 benchmark 的一个特有陷阱：**沙箱预算本身是评测配置的一部分**，同一个百分比在 12h × 单卡 RTX 4090 与 24h × A800/H200 下不是同一件事。[[Papers/2607-FrontisMA1]] 的 artifact 审计表里同时出现自身的 71.21% 与预算更大的既有系统 75.76%–80.30%，两者不可直接比；跨论文引用"MLE-Bench Lite 百分比"必须带上 backbone、预算与 run 数，否则数字无意义。同一篇工作示范了正确的对照结构——固定 harness 换模型与固定模型换 harness 两条正交对照都跑，且训练数据构建期即排除与 MLE-Bench 重叠的竞赛。共同局限：verifier 覆盖的是"任务是否通过"，不覆盖"演化是否引入长期漂移"。

有 verifier 不等于报告的增益就算数，[[Papers/2607-HarnessBank]] 把这一步也写成了判据：候选与父代在同一批任务上配对，要求均值差为正且 $z\ge1.96$ 才被 credit，判决由不含 LLM 的确定性 evaluator 计算。它同时量化了不这么做的代价——在演化收敛后候选实际中性的那些轮次里，single-run 或 $K=3$ 均值判据有 62%–76% 的轮次报出幻觉进展。这个数字解释了自演化文献里大量"这一轮又涨了"为什么不可采信，也解释了同篇 SWE-bench 的 +5.1% 为何在 $n=26$（$z=0.78$）下被作者自己标为 preliminary——尽管摘要的 "5.1% to 15.4%" 仍把这个数当作下界，这是全文最不一致的一处。判据自身的边界须一并记：七个域各按双侧 5% 判定，域间无多重比较校正，最弱的 credited $p=0.033$ 在 Bonferroni 下会掉出来；误拒侧只有个案而无率（GDPval 上训练侧排名次优者在测试上最高，+11.5% vs +9.2%）。

### 9.2 experience-driven lifelong benchmark

三个 2026 评测把对象从"单任务能力"移到"经验驱动的 lifelong 演化本身"，且都以负性/分化结果为主要信息：

| Benchmark | 测什么 | 规模/协议 | 头部结果 | 关键局限 |
|:--|:--|:--|:--|:--|
| [[Papers/2508-StuLife]] | 长程记忆（LTRR）+ 自发主动性（PIS） | 1,284 任务 / 10 scenario / 单学期 stateful 轨迹；默认协议每任务孤立呈现，跨任务保留全靠 agent 用工具外化 | GPT-5 StuGPA 17.90 vs human 85.24；PIS 4.68% vs 88.13%；perfect-context 下同类任务 98.18% | headline 数字与协议强绑定（同底座加 All-in-One prompt 即 21.07）；§3.3 定义的 FGT/BWT/FWT 等 forgetting 指标未实际报告 |
| [[Papers/2604-SkillFlow]] | skill 的发现-修复-维护 lifecycle | 166 任务 / 20 family / 5 域；family 内按难度顺序，每题 执行→verifier rubric→skill patch；family reset | Opus 4.6 62.65→71.08%（+8.43pt），终库 1.05 skill；GPT 5.3 Codex 反降 6.02pt；full-history control 仅 51.04% | "lifelong" 名不副实（8-9 题/family、跨 family 不携带）；无 skill 冗余/退化度量 |
| [[Papers/2608-AgentStream]] | 任务流结构 × 演化方法 × 底座能力的联合效应 | 6 benchmark × 50 题 × 3 seed（只改任务到达顺序）；Isolated / Sequential / Interleaved 三场景；5 方法 × 3 frontier 底座；测试时无标签，演化只用交互内在反馈 | Isolated 34/45 为正、+1.37±0.80；Sequential 28/45、+0.75±0.48；Interleaved 28/45、+0.90±0.34；GPT-5.4 三场景平均增益全负 | 效应量 0.6–1.6 点而单元格 seed 间标准差常 3–6 点（Tau2 达 ±36.2），全文无显著性检验；能力刻度高度依赖 HLE 一列；Sequential 只跑一个固定顺序 |

StuLife 与 SkillFlow 共同刻画了自演化的两个反直觉事实：其一，StuLife 的 perfect-context 98.18% vs 默认 17.90 说明当前瓶颈不在任务理解而在**自主记忆管理与主动性**——即"演化机制本身"，而非底座能力；其二，SkillFlow 的模型分化（Opus +8.43 vs GPT-5.3-Codex −6.02、Kimi 高使用率零收益）说明 skill evolution 不是免费午餐，关键差距在"**修复坏 skill**"而非"写 skill"，且错误 skill 入库会造成 systematic downstream drift（把局部错误放大为序列级 pattern）。SkillFlow 的 full-history control（51.04% < vanilla）还给"skill 抽象优于原始经验堆积"提供了对照证据点，与 [[Papers/2601-MemRL]] 的 selection 侧演化形成对读。

[[Papers/2608-AgentStream]] 把评测对象再推一步：不问某个方法能涨多少，而问自演化的收益在什么条件下存在。它把六个 agentic benchmark 编排成任务流，用同域独立累积（Isolated，每 benchmark 独立实例与独立 state）、跨域有序迁移（Sequential，单 agent 依固定顺序走完全部 benchmark 且 state 跨域保留）、无域边界混流（Interleaved，全部任务 shuffle 共享单一 state）三种场景，对五个自演化方法 × 三个 frontier 底座做受控析因，收益一律以同一模型 state 恒空时的表现为对照。三条结论都是限定性的。**场景**上同域独立累积最可靠（34/45 为正），而混流反而优于有序流（15 个配置里 10 胜 5 负），即有序的域切换比无序的干扰更伤，这推翻了"混得越乱越难"的默认直觉。**底座**上收益被能力 gate 住且非单调——GPT-5.4 三个场景的平均增益全为负（−0.35 / −0.78 / −0.62，15 个配置只有 4 个超过自身 vanilla），而 vanilla 更弱的 Gemini 3.1 Pro 平均 +2.37 反而高于更强的 Claude Opus 4.7 的 +1.23，且这个反差在混流下从约 0.95 点扩大到 1.51 点。**方法**上无一占优：方法间 spread 随底座能力从 5.3 点单调收缩到 0.9 点，最优方法不跨模型迁移（A-Mem 在 GPT-5.4 最好却在 Gemini 垫底），按方法平均自演化还把最弱与最强底座的差距从 18.1 点拉大到 20.0 点。成本一侧同样由底座决定：Gemini 上四个方法比 vanilla 更便宜（64%–84%），而 GPT-5.4 上唯一取得正增益的 A-Mem（+3.2%）要付 577% 的成本。

这套结论的证据强度必须与它的量级一起读。头条差异在 0.6–1.6 个百分点，而单元格的 seed 间标准差常在 3–6 个百分点、Tau2 上达 ±36.2——同一配置仅因任务到达顺序不同就能从 12.0 跳到 84.0，全文无显著性检验或置信区间，Isolated 的 +1.37±0.80 与 Interleaved 的 +0.90±0.34 区间重叠。能力刻度也被单列绑架：GPT-5.4 被定为最弱底座主要因为 vanilla 均值 45.8，而它在 HLE 上只有 2.0（同列 Gemini 52.0、Claude 38.0），这种分数通常是解析或 harness 失败而非能力差距的信号，论文未做诊断。其机制解释——solve rate 低则经验流被失败轨迹主导、抽不出可迁移知识——是事后解读，全文没有任何操纵经验质量的对照。因此可承重的是形态而非数值：**自演化的增益不是普遍属性，在相当一部分配置上它就是净亏损**（45 个计数单元里 11–17 个跑输不演化的同一模型）。这与 §10 的安全侧结论互补——后者说演化会朝有害方向漂移，这里说即便不涉安全，演化本身也常常不划算。

### 9.3 演化 safety benchmark

安全侧评测目前借用静态 red-teaming 套件（HarmBench / SALAD-Bench / RedCode / Agent-SafetyBench / BrowserART）在演化前后做 snapshot 对比，或如 [[Papers/2509-Misevolution]]、[[Papers/2510-AlignmentTipping]] 做有限步数的 longitudinal 追踪。剂量-反应关系目前只有 model 演化路径有约 200 步的连续数据（Misevolution / ExperienceSafetyRisks），memory/tool/architecture 路线的纵向安全轨迹尚无 benchmark。

### 9.4 Open Problems

真正的 evolution-aware benchmark（联合追踪演化步数、能力、风险，覆盖四条路线且区分 model+harness 与模型本体贡献）仍然缺失。[[Papers/2608-AgentStream]] 关掉了其中一半——跨方法、跨底座、跨流结构的受控析因与统一的 evolution gain 定义都已就位——但只覆盖能力轴，风险与演化步轨迹仍在评测面之外。四个具体缺口：StuLife/SkillFlow 都定义了 forgetting/redundancy 指标却未报告数值；headline 分数与 harness/协议强绑定使跨论文比较失真；安全评测停留在 snapshot，无法捕捉 misevolution 的累积轨迹（§10.2）；以及**评测预算与目标效应量不匹配**——在每 benchmark 50 题 × 3 seed 的规模上分辨 1 个百分点量级的差异超出该协议的判别力，而这恰是当前多数自演化工作报告增益的量级。最后一条已有可操作对策：[[Papers/2607-HarnessBank]] 的配对 2σ crediting 与它测出的 62%–76% 幻觉进展率表明，判别规则应写进评测协议本身，而不是留给读者去猜哪个百分点是真的。

## 10. Safety, Reliability, and Failure Modes

演化不是免费的——misevolution 已从假设变为实证事实，且有从良性偏航到对抗投毒的完整谱系。

### 10.1 misevolution：从假设到实证

[[Papers/2509-Misevolution]] 在四条路径 × SOTA 系统上证明：不需要不安全数据、不需要外部攻击者，**良性反馈循环 + 有偏 credit assignment 就足以产生 safety 衰减与 reward hacking**；现有 mitigation（prompt 补丁/事后补训/静态扫描）全部只部分有效。四路径实测：AFlow 优化 20 轮后 ASR 54.4%→83.1%（Ensemble Node 级联放大）、memory 路径 deployment-time reward hacking >60%、工具创建-复用 Unsafe Rate 65.5%、自训练 safety 累积衰减。

### 10.2 负性结果三条线

三篇独立工作从不同角度刻画自演化的失效条件，共同结论是"自改进可自退化"：

| 工作 | 失效模式 | 关键机制/证据 |
|:--|:--|:--|
| [[Papers/2407-SelfImprovementReversal]] | self-improvement reversal | post-training 表面指标升但泛化/多样性降；评估协议为双轨解码 |
| [[Papers/2606-RiseAndCollapse]] | rise-and-collapse | 自改进先升后崩的失效轨迹；C10 GRPO-vs-REINFORCE 措辞已核 |
| [[Papers/2606-CodeSelfReviewCollapse]] | recursive self-training collapse | 用系统自身信号做 gate 会进入 rubber-stamp regime（等价于不过滤），Prop 2.1 给指数增长条件 |

CodeSelfReviewCollapse 对全 survey 的 gate 论证是关键约束：**self-review 式 gate 会退化为橡皮图章**——这直接质疑 MetaTeam 的 collective discussion、MemSkill 的 reward-only rollback 等 self-gate 设计能否抵抗 rubber-stamp。[[Papers/2607-MANTA]] 提供了这一命题目前唯一的分域实测：其 Auditor 与被审计的 task agent 共用同一底座（Gemma 4 31B，temperature 0），450 run 中 200 run 被 flag，聚合上未退化为橡皮图章；但分域看，PlanCraft 90 run 只 flag 出 1 次、MATH 只 2 次，在这两域上闸门实际近乎恒过，而 BrowseComp 恰好相反（83/90，恒不过）。同底座 self-gate 的失效并非只有"全过"一种形态，两端退化都会使 gate 丧失判别力——这是把 rubber-stamp 命题从二元判断细化为分域现象的第一个数据点。

### 10.3 benign misevolution 与 alignment tipping

[[Papers/2604-ExperienceSafetyRisks]] 证明即便经验完全良性、任务完全正常，experience-driven 演化也会引入安全风险（C3 的"Claude 全程最低"被推翻、修正为域依赖；C7 剂量图例 1/3/5/7/9 完整）——这是 misevolution 谱系的良性端点，风险被完整测量。[[Papers/2510-AlignmentTipping]] 刻画自演化把 agent 推离对齐的 tipping 过程（C2 解码设置已修正，并抓到论文内部矛盾：最陡降 r=2→3 vs Table 1 逐差）。

### 10.4 对抗性威胁：记忆投毒

[[Papers/2512-MemoryGraft]] 是谱系的对抗端点：投毒记忆持久危害 agent。本文对其证据强度做保留标注（rating 2）——威胁模型自相矛盾（intro 声称的能力与 Appendix A 定义不一致）、PRP 定义的攻击缺随机基线（约 9%）、且证据实为 retrieval-level 而非其主张的 cross-agent transfer 级。与 ExperienceSafetyRisks（良性、完整测量）配对，构成 threat model 的两个端点：一端是无攻击者的良性偏航，一端是主动投毒但证据强度与主张不匹配。

### 10.5 threat model 与放大结构

[[Papers/2606-MLASSelfEvolvingSafety]] 用模块 × 演化阶段矩阵系统化 multi-agent 自演化的攻击面，抓到三处论文内部数字不一致（17/7/1 vs 五档图例、3.5x vs 2x、2.5% 错置，均记于 Paper 笔记）。其价值在指出放大结构：单点错误经 shared scaffold / constitution 变为 lineage-persistent 的全队污染。

### 10.6 gate 作为可靠性来源

综合 §6.2 与 §10.2：演化步 gate 在性能回归维度已有实证方案（GRASP 编辑级、SKILL.nb 步骤级、[[Papers/2607-HarnessBank]] 的 harness patch 筛选级），统计与形式化方向有 SEACertificates/SEVerA，但**安全维度 gate 与 self-gate 的 rubber-stamp 问题（CodeSelfReviewCollapse）仍是硬约束**。已被测量到的 gate 价值集中在防回归、拦假精英与收敛效率上，天花板贡献在存在冗余部署选择器时为零——把 gate 当作可靠性组件论证站得住，当作性能组件论证目前只有一处实测支持而那条记录缺核验（§6.2）。task-agnostic、抗橡皮图章、可第三方审计的 gate 仍是可靠性的核心未解问题：目前最外生的实例只在判决算法一层做到外生，证据来源（patch 自报 activation beacon）与打分器（judge 模型未指明）两层仍未审计。

## 11. Open Challenges

- **Longitudinal evolution-aware 评估**：当前 safety/能力评估全是 snapshot-based，无 benchmark 追踪"演化步数-能力-风险"联合轨迹；剂量关系目前仅 model 路径有 200 步数据。
- **抗 rubber-stamp 的演化步 gate**：self-review 式 gate 会退化为橡皮图章（CodeSelfReviewCollapse），需要 exogenous、task-agnostic、可审计的验证。gate 谓词自身的 precision 目前只有一处数字，且是同底座自评的**触发**闸门而非验收闸门（[[Papers/2607-MANTA]] 总体 precision 0.38 / F1 0.47，分域从近乎恒过到近乎恒不过）；外生校准与 process flag 的人工标注精度均未见。[[Papers/2607-HarnessBank]] 把判决算法层做到了目前最外生的形态（确定性配对统计量 + 独立 evaluator + evolver 与 task agent 不同家族），但同时暴露出"外生"是分层的：证据来源层由 patch 自报 activation beacon 且无人审计该声明是否名副其实，打分器层在部分域直接是未指明模型的 LLM judge；该篇也未报告 gate 的误收/误拒率，只有个案。[[Ideas/HybridVerifier-GUIRuntime]] 正针对 GUI runtime 的 hybrid（deterministic state-contract + 学习式）verifier gate 这一缺口。
- **credit assignment 的信号质量**：RSI 谱系瓶颈从"如何自改"转向"如何选 parent"（HGM CMP 0.778 vs DGM 0.285）；四类替代信号（clade 聚合 / 结果的辅助统计量 / 多因子固定权重效用 / 纯过程审计）尚未在同一 testbed 上对照；multi-agent 的 per-agent 归因仍靠讨论涌现而非算法。
- **演化增益的预算与来源归因**：多数工作报告的是"演化机制 + 额外资源"的联合效应而把结论写成前者——[[Papers/2607-MANTA]] 的 mutation 增益与 +28K token 同时上线（缺同拓扑再跑一轮的对照臂），[[Papers/2607-FrontisMA1]] 的 post-training 增益与外部更强 teacher 的蒸馏成分未分离（缺 no-teacher 臂）。本轮补上第三种形态：**演化组件自身未被隔离**。[[Papers/2608-RoMeRL]] 的四个记忆坐标里只有一个用到学到的 Q，却没跑 $\omega_Q=0$ 的纯启发式臂；[[Papers/2607-SESA]] 跑了关库对照并因此发现技能库的部署期贡献只占总增益的两三成（§6.3）。第四种形态更隐蔽：**演化组件被系统内另一个冗余机制替代**——[[Papers/2607-HarnessBank]] 的 2σ gate 被去掉后天花板 ±0.0，因为训练集 argmax 这个独立的部署选择器已经选中了同一个赢家；报告 gate 收益的工作若不把 selector 也消融掉，记在 gate 账上的功劳无法与 selector 的分开。四种形态共用一句诊断：**报出的是联合效应，写下的是单一归因**。equal-budget paired replay、teacher-ablation、关掉待验组件再跑一遍、固定判决规则换掉最终选择器——四个补法的成本都远低于原实验，缺席本身就是信号。
- **operation-level 演化的安全性**：memory 演化从内容升到操作（MemSkill）后 blast radius 放大，但无安全评估。
- **co-evolution 的验证空白**：环境/verifier 自身演化的安全性（谁验证 verifier 的演化）完全空白；multi-agent population 稳定性、合谋、集体 misevolution 无实证。
- **优化产物可迁移性**：文本级经验资产跨 backbone 可迁移（KnowAct 正例 +3.1pts），但跨演化阶段迁移反而失效（SEED 静态 library −7.4）。[[Papers/2607-HarnessBank]] 给出目前最清楚的机制刻画：演化产物是针对特定底座失败模式的 correction 而非普适更优配置，迁移成立与否由 pathology 是否匹配决定——AppWorld 上匹配的 patch 给 +15.4、错配只给 +1.2，Omni-MATH 上两代同族模型共享同一失败模式因而几乎无损迁移（+11.7 → +11.0），而把同一杠杆反向拧错叠在演化后的 harness 上是 −15.7，即有害而非中性。[[Papers/2608-AgentStream]] 从方法层给出同向但更弱的证据（最优方法不跨底座保序），其方法间 spread 在两个较强底座上只有 0.9–2.0 点、落在噪声量级。可迁移性的刻画因此从"能不能迁"细化为"失败模式是否同构"，但除 HarnessBank 外无第二处受控证据，也没有任何工作事前预测过匹配与否。
- **自演化增益的存在条件**：跨方法受控析因显示增益既不普遍也不稳定——45 个计数单元里 11–17 个跑输不演化的同一模型，方向随底座能力非单调，且成本-收益比同样由底座决定（[[Papers/2608-AgentStream]]）。论文把成因归给 bootstrap loop（solve rate 低则经验流被失败轨迹主导），但这是事后解读而非受控结论。把"能力 gate"改写成可操作的"经验质量 gate"只需一个实验：固定底座与方法，按成功/失败比例控制注入 state 的轨迹构成，看增益如何随之移动。在这个实验做出来之前，"在哪些条件下该上自演化"仍是一个没有答案的部署问题。
- **Risk awareness 的灾难性遗忘**：SEAgent 演化后完全丧失拒绝/避险能力，安全能力遗忘动力学未知。

## 12. Discussion and Conclusion

自演化领域在 2026 年从"能不能演化"进入"演化会不会坏、如何 gate"的阶段。四个跨论文的判断浮现，其中第二个已由方向相反的两组实测从共识降级为条件性结论：

其一，**反馈信号的可验证性是四条路线共同的成败分界**，verifier 质量上界决定 self-evolution 收益上界——deterministic 域（代码/几何）最稳，internal/共识域收益真实但劣化可测。2026 下半年出现的新 move 是把可验证性当作**可设计**而非固有的属性（[[Papers/2607-SpyRL]] 的 RLSVR：向环境注入隐变量、让 agent 在被它条件化的观测上执行原任务、再核对一个关于该隐变量的问题）。这个 reframing 简洁、与 GRPO 正交、原则上可迁移到任何 RLVR-hard 的域，值得跟踪；但其唯一实例同时说明负担是被转移而非消除——塑造生成质量的那一项 reward 仍由被训练的模型自己扮演 judge 投出，在开放式生成上整体没能越过强 rubric-judge 基线。判据没变：**收益上界仍由那个真正塑造行为的信号有多可信决定**，构造式可验性改变的是这个信号的成本与来源，不是它的性质。

其二，**gate 是可靠性组件；它是否同时是性能组件，取决于 gate 之外有没有一个冗余的部署选择器**。两处证据台账齐备的自身消融把已测得的 gate 价值统一定位在地板与效率轴——[[Papers/2606-SkillNb]] 去 gate 只掉约 6 分成功率而修复后回归从 3.3% 爆到 18.6%，[[Papers/2607-HarnessBank]] 去掉 2σ 判据天花板 ±0.0 而假精英 0→2、收敛轮数 10→>20，其解释是训练集 argmax 这个独立选择器已经选中了同一赢家。方向相反的唯一实测来自 [[Papers/2605-GRASP]]（去闸门 88.8%→63.5%），其结构差别在于闸门本身即部署决策、没有下游 argmax 兜底，而该侧记录缺证据台账与核验状态。因此这条判断应按条件陈述而非作为共识引用，正反两侧一并记录（§6.2）。此外现有实证 gate 只覆盖性能回归、依赖任务可复现结构，且 self-review 式 gate 会退化为橡皮图章——抗 rubber-stamp 的 task-agnostic 安全 gate 是领域中枢缺口。一条新路径是把演化信号与评价信号从结构上切开（只用不接触结果的过程审计驱动演化），它免疫"闸门其实就是打分模型"的循环，代价是信号弱且分域极不稳定，且这条代价目前只被测量过一次。

其三，**recursive self-improvement 在现有证据下有界**：scaffold 层受 frozen FM 天花板约束，weight 层受 reversal 约束，谱系的下一步瓶颈已从"改法"转向"选法"（credit assignment 信号质量）。misevolution 从假设变为跨系统实证事实，且威胁谱从无攻击者的良性偏航延伸到主动记忆投毒。领域叙事仍普遍超前于实物——满足严格自演化判据（经验依赖 + 持久策略改变 + 自主探索）且部署后持续演化的系统，目前极少；以 RSI 为题而实际做到 generation ≥2 的，库内一篇也没有。本轮最完整的一套开放栈（[[Papers/2607-FrontisMA1]]，六件 artifact 齐全）同样只训练到 generation 1，其价值在于把"缺哪些 ablation"从必须相信作者变成别人可以补的实验，而不在于把递归做出来。

其四，**自演化的增益不是普遍属性，而是与底座能力、任务流结构、失败模式匹配度耦合的条件性收益**。首个跨方法受控析因在 5 方法 × 3 底座 × 3 种任务流的 45 个计数单元里测到 11–17 个跑输不演化的同一模型，增益随底座能力非单调，最优方法不跨底座保序（[[Papers/2608-AgentStream]]）；机制侧的同向证据来自 [[Papers/2607-HarnessBank]]——演化出的 harness 是针对特定底座失败模式的 correction，匹配时 +15.4、错配时 +1.2、反向叠加时 −15.7。两者合起来意味着"某方法带来 X 点提升"这类跨论文引用在缺少底座与流结构限定时没有意义。证据强度需与结论分开记：前者的效应量普遍小于其自身的 seed 间标准差且全文无显著性检验，可承重的是形态不是数值；后者单次运行、无方差报告。

## Key Evidence Matrix

下表登记进入 Overview / §7–§10 / Open Challenges 的高影响 claim，标注 state（source-verified / 跨来源收敛 / 作者综合论断 / 库内暂无独立验证）、locator 与边界。本轮 20 篇新论文经独立 verifier 核验的 claim 均标 [本轮核]。

| Claim | State | Locator | 边界 / 修订 |
|:--|:--|:--|:--|
| HGM full SWE-bench Verified 61.4%、迁移 SWE-Lite 57.0% standard 称 "human-level" | source-verified [本轮核] | [[Papers/2510-HuxleyGodelMachine]] §4.3, Table 4 | 57.0 超 SWE-agent 56.7；filtered 47.8 落后一题；"human-level" 是论文自述口径 |
| HGM clade-level CMP 与真实改进 Pearson 0.778 > DGM guidance 0.285 | source-verified [本轮核] | [[Papers/2510-HuxleyGodelMachine]] | credit assignment 信号质量是 RSI 新瓶颈维度 |
| DGM SWE-bench 20.0%→50.0%，跨模型/语言迁移成立 | source-verified | [[Papers/2505-DarwinGodelMachine]] | 收益在 scaffold 空间，上界由 frozen FM 锁定 |
| MANTA inference-time topology 演化：5 benchmark 平均 74.0 vs ADAS 68.2；等 token 下 77,652 得 74.0 vs Voting 80,781 得 64.7 | source-verified [08-02 并入] | [[Papers/2607-MANTA]] Table 1/4 | 平均领先几乎全部来自 BrowseComp（+12.3）；162 个修复操作 42.0% 为不经 Planner 的手写 retrieval contraction；mutation 消融与 +28K token 及注入诊断文本绑定，无 equal-budget 对照臂；单一 backbone、每 benchmark 30 题 |
| MANTA 过程审计信号：无 flag run 正确率 83.2% vs flagged 62.5%；作为错误检测器 precision 0.38 / recall 0.64 / F1 0.47 | source-verified [08-02 并入] | [[Papers/2607-MANTA]] Table 8/9 | gate 谓词 precision 的首个数字，但测的是**触发**闸门非验收闸门；同底座（Gemma 4 31B）自评；分域从 PlanCraft 1/90 到 BrowseComp 83/90；process flag 的人工标注精度论文列为未执行扩展 |
| Frontis-MA1 同 harness 下 MLE-Bench Lite 39.39%→60.61%，Evo-Max 71.21% ± 8.57% | source-verified [08-02 并入] | [[Papers/2607-FrontisMA1]] §6.2 Table 1 | 与 GPT-5.6 Sol + Codex 的 72.73%（单次点估计）区间重叠；作者自建审计表内另有 75.76–80.30% 的更大预算系统；无算子级 ablation、无 SFT/RL 拆解；SFT teacher 为 GLM-4.7，自改进与外部蒸馏未分离 |
| Frontis-MA1 未实现 RSI：演化系统本身 largely fixed，全文只到 generation 1 | source-verified [08-02 并入] | [[Papers/2607-FrontisMA1]] §7/§8 Limitations | 作者在 Related Work 与 Limitations 明确不 claim RSI；"搜索期不更新权重"由训练与评测配置推出而非作者直述；标题与 abstract 未带此限定 |
| MemSkill operation-level：LoCoMo 53.82 / LongMemEval 纯迁移 60.89 / 调用量低一量级 | source-verified [本轮核] | [[Papers/2602-MemSkill]] Table 1/3 | gate 只在 skill-bank 层、只看 aggregate reward；designer blast radius 系统性 |
| MemRL selection-based 演化，G.4 第一方自认 reward-hacking | source-verified [本轮核] | [[Papers/2601-MemRL]] App G.4 | selection 侧同受 internal 信号偏差约束 |
| MetaTeam collaborative 组织演化：消融 53.9>49.8>44.5>40.8 | source-verified [本轮核] | [[Papers/2605-MetaTeam]] Table 2 | 无算法化 per-agent credit assignment；commit 前 gate 仅一致性/预算级（App D），非 outcome-level；GAIA=77.3 非 87.9（后者 LOCA） |
| SEAL interface-级 co-evolution 不在 EnvEngSurvey 三范式内 | 作者综合论断 [本轮核] | [[Papers/2605-SEAL]] / [[Papers/2606-EnvEngineeringSurvey]] §VII | 分类学盲点：三范式漏 interface/observation 级 |
| GenEnv 难度对齐 co-evolution；单步任务生成有边界 | source-verified [本轮核] | [[Papers/2512-GenEnv]] | C13 单步边界 + C14 RL 基线独立核出 |
| EnvEngSurvey：质量四维仅 correctness 成熟，其余 under-researched；582 refs | source-verified [本轮核] | [[Papers/2606-EnvEngineeringSurvey]] §V,I | C8/C9 原稿两处 contradicted 已修正（de-novo 归类 / refs 582） |
| Misevolution：良性反馈 + 有偏 credit assignment 即致 safety 衰减；AFlow ASR 54.4→83.1% | source-verified | [[Papers/2509-Misevolution]] | 四路径 × SOTA 实测；mitigation 全部部分有效 |
| self-review 式 gate 退化为 rubber-stamp（Prop 2.1 指数增长条件） | source-verified [本轮核] | [[Papers/2606-CodeSelfReviewCollapse]] | 约束所有 self-gate 设计（MetaTeam/MemSkill） |
| self-improvement reversal：表面指标升而泛化/多样性降 | source-verified [本轮核] | [[Papers/2407-SelfImprovementReversal]] | 评估协议双轨解码（C7 归属已修正） |
| rise-and-collapse 失效轨迹 | source-verified [本轮核] | [[Papers/2606-RiseAndCollapse]] | C10 GRPO-vs-REINFORCE 措辞已核 |
| experience-driven benign misevolution 完整测量；Claude 域依赖非全程最低 | source-verified [本轮核] | [[Papers/2604-ExperienceSafetyRisks]] | C3 全程最低被推翻→域依赖；C7 剂量 1/3/5/7/9 |
| alignment tipping：自演化推离对齐 | source-verified [本轮核] | [[Papers/2510-AlignmentTipping]] | C2 解码已修；抓到内部矛盾（最陡降 r=2→3 vs Table1） |
| MemoryGraft 记忆投毒持久危害 | 库内暂无独立验证 [本轮核] | [[Papers/2512-MemoryGraft]] | rating 2：威胁模型自相矛盾、PRP 无随机基线(~9%)、证据实为 retrieval-level 非 cross-agent transfer |
| MLAS 攻击面：单点错误经 shared scaffold 变全队 lineage-persistent 污染 | source-verified [本轮核] | [[Papers/2606-MLASSelfEvolvingSafety]] | 三处论文内部数字不一致已记录 |
| gate 家族五粒度：edit/step/audit/统计证书/形式验证；Live-SWE 零 gate | 跨来源收敛 [本轮核] | GRASP/SKILL.nb/ASGSI/[[Papers/2607-SEACertificates]]/[[Papers/2603-SEVerA]]/[[Papers/2511-LiveSWEAgent]] | 实证 gate 仅覆盖性能回归；安全维度空白 |
| VisPlay 共识伪标签逐代劣化 72→65→61 | source-verified | [[Papers/2606-VisPlay]] | internal 信号劣化第一方量化；缺 deterministic verifier 退路 |
| MetaSkill-Evolve 两级递归：演化改进流程本身 | source-verified [本轮核] | [[Papers/2607-MetaSkillEvolve]] | 13/13 verified |
| StuLife：GPT-5 StuGPA 17.90 vs human 85.24；perfect-context 98.18% 定位瓶颈在记忆+主动性 | source-verified（headline 自核） | [[Papers/2508-StuLife]] Table 3/7 | headline 数字经 curl 直核；其余 claim digest 级（本轮 verifier 因额度中断）；分数与协议强绑定 |
| SkillFlow：Opus 4.6 +8.43pt / GPT-5.3-Codex −6.02pt；差距在修复而非写 skill | source-verified（headline 自核） | [[Papers/2604-SkillFlow]] Table 1 | headline 经 curl 直核；其余 digest 级；"lifelong" 实为 within-family 8-9 题短程演化 |
| RLSVR：可验证性可由 task transformation 构造（隐变量注入 → 条件化执行原任务 → 仅凭输出回答关于隐变量的问题 → 规则核对） | source-verified [08-04 并入] | [[Papers/2607-SpyRL]] §3 / Algorithm 1 | schema 层贡献；但塑造生成质量的 performing reward 由被训练模型自任 detector 产生，论文 Algorithm 1 自标 "non-verifiable rewards made by detectors"——判分负担被转移非消除 |
| SpyRL 在开放式生成上整体未过持平线：对 GPT-4o-RaR overall 48.9% / 48.2%，coherence 45.8/45.0、consistency 44.5/43.7 | source-verified [08-04 并入] | [[Papers/2607-SpyRL]] Table 5 | 论文表述为 "remains competitive"；其价值主张应读作成本权衡（RaR 基线约 \$200 / \$900 verifier 开销）；D.1 显示 R-Zero 在同域等于未训练甚至负增益 |
| SpyRL 两个消融净负、跌破未训练基座：去 RAE 七 benchmark 均值 50.4→37.5（基座 41.4）；两阶段联合更新 42.4→35.3 | source-verified [08-04 并入] | [[Papers/2607-SpyRL]] Table 9 / App D.3 Table 16 | 优化侧设计是稳定性前提而非增益来源；全文无 seed / std / 误差棒；仅 4B/8B 单节点；数学 checkpoint 对两类写作全线负迁移 |
| SESA 关库对照：SESA-Off 相对 SSP 已 +1.8/+2.2，重新开启同一最终技能库只再加 +0.5/+1.0 | 库内暂无独立验证 [08-04 并入] | [[Papers/2607-SESA]] Table 2 | 库内唯一做过部署期关库对照的技能演化工作；单次运行、无方差、无算力/token 匹配对照；Bamboogle 在七个 backbone 分块中六块相对 SSP 回退且论文未讨论；其"双向协同演化"机制主张无隔离实验，论文自述为相关性观察，正文未采用 |
| RoMeRL memory-reward trap：bundle-level credit 下加大探索同时放大误归因——注入 10% null 化记忆后噪声条目正向更新 MemRL 3.7 → +UCB 7.2 → RoMeRL 2.4，终轮噪声占比 1.02%/1.20%/0.15% | source-verified [08-04 并入] | [[Papers/2608-RoMeRL]] Table 2 / App B.5 | "探索放大污染"稳；同表"探索降低性能"仅 79.2→78.4（0.8pp，单次运行）不足以支撑，两者强度不同不应并列为证据 |
| RoMeRL reduced-order 状态：per-task 四坐标（上界 4），overall SR 0.862 vs MemRL 0.830，记忆池 45K→7K、调用 570K→450K，backbone 冻结 | source-verified [08-04 并入] | [[Papers/2608-RoMeRL]] Table 1 / §6.1 | 四坐标中仅 NCC 用到学到的 Q，无 $\omega_Q=0$ 消融，RL 与降维结构的贡献未分离；+3.2pp 中约 62% 来自 ALFWorld 两列、heat 列反降；无多 seed / 方差；feedback density 6.0× 与池 6.4× 近乎同比，是 Thm 3（T/d）的算术后果；Prop 1 依赖的 γ/λ 论文自陈未估计 |
| HarnessBank gate 消融：去掉 2σ 判据后 TB2 test Pass@1 **±0.0**、假精英 +2、轮数 >20(cap)，对照 45.4 / 0 / 10.0；论文解释为 train-argmax 已选中同一赢家 | source-verified [08-05 并入] | [[Papers/2607-HarnessBank]] Table 3 / §4.7 | 把"gate 即收益来源"降为条件性结论的直接反例；gate 的可测价值在地板与效率轴；无算力配平对照（无 gate 变体反而多跑轮次）；"无闸门循环会交付回归"由跨方法对照（DGM 在 Omni-MATH 交付 −1.1%）给出，非其自身消融 |
| HarnessBank 主结果：七域 test Pass@1 +5.1~+15.4，六域过配对 $z\ge1.96$（$p$ 从 <1e-4 到 0.033，AppWorld 最强 $z=6.44,n=168$）；收敛后中性轮次用 single-run 或 K=3 均值判据有 62–76% 报出幻觉进展 | source-verified [08-05 并入] | [[Papers/2607-HarnessBank]] Table 1 / §4.2 / §4.4 / §4.7 | SWE-bench 的 +5.1% 在 $n=26$ 下 $z=0.78$ 未过判据、作者自标 preliminary，而摘要区间下界仍用它；七域逐域按双侧 5% 判定、域间无多重比较校正；Table 1 无 $n$ 列；轮数上限 $R$ 与耐心 $P$ 正文未给值；代码 upon acceptance |
| HarnessBank gate 独立性分三层：判决算法外生（确定性配对统计量 + 独立 evaluator + evolver 与 task agent 异族）/ activation 证据由 patch 自报 beacon / 部分域打分器为未指明的 LLM judge | source-verified [08-05 并入] | [[Papers/2607-HarnessBank]] §3.2–3.3 / §4.1 / §4.5 | "确定性 gate"仅指判决算法确定，非整条证据链外生；未报告误收/误拒率，只有个案（SWE-bench $z=0.78$；GDPval 训练次优者测试最优 +11.5 vs +9.2）；与基线比较存在 proposer 强度混淆（evolver 为 Claude Opus 4.8，GEPA/DGM 用 Qwen3.6-27B 兼任 proposer） |
| HarnessBank cross-model dissociation：演化产物是 model-specific correction——AppWorld 匹配 patch +15.4 / 错配 +1.2，Omni-MATH 同族迁移 +11.7→+11.0，反向杠杆叠加演化后 harness −15.7 | source-verified [08-05 并入] | [[Papers/2607-HarnessBank]] Table 2 / §4.6 | 把"可迁移性"细化为"失败模式是否同构"；非对称性（匹配有效 / 错配近零 / 反向有害）难用"随便改点什么都有用"解释；单次运行、无方差 |
| AgentStream 场景轴：Isolated 34/45 为正、+1.37±0.80；Sequential 28/45、+0.75±0.48；Interleaved 28/45、+0.90±0.34；逐对比较 Interleaved 10 胜 Sequential 5 | source-verified [08-05 并入] | [[Papers/2608-AgentStream]] Table 2 / §5.1 | 正文的 75.7% / 62.3% 与表内 34/45、28/45 各差 0.1；Sequential 一行 28+16=44 分母不齐、论文未说明；gain 区间重叠且全文无显著性检验；Sequential 只跑一个固定顺序，顺序效应与跨域干扰混杂 |
| AgentStream 能力 gating 且非单调：GPT-5.4 三场景平均 gain 全负（−0.35/−0.78/−0.62，仅 4/15 超自身 vanilla）；vanilla 更弱的 Gemini +2.37 高于更强的 Claude +1.23 | source-verified [08-05 并入] | [[Papers/2608-AgentStream]] Table 3 / §5.2 | 能力刻度高度依赖 HLE 一列（GPT-5.4 仅 2.0，Gemini 52.0 / Claude 38.0），该分数更像解析或 harness 失败而论文未诊断；bootstrap loop 为事后解读，全文无操纵经验质量的对照；闭源模型档位不可复现 |
| AgentStream 耦合强度二分：context-integrated 吃同域（ACE Isolated +2.28 → Interleaved −1.26，Harness +1.91→+1.01），retrieval-based 吃混流（A-Mem/ReasoningBank/AutoSkill 均在 Interleaved 峰值 +2.22/+1.79/+0.72） | source-verified [08-05 并入] | [[Papers/2608-AgentStream]] Table 5 / §5.4 | 符号翻转是最干净的形态证据；单元格 seed 间标准差常 3–6 点、Tau2 达 ±36.2（同配置仅因到达顺序即 12.0↔84.0），绝对幅度不足以承重；本文据此未重排分类轴 |
| AgentStream 成本：GPT-5.4 上唯一正 gain 的 A-Mem（+3.2%）成本为 vanilla 的 577%；Gemini 上四个方法反而更便宜（64%–84%） | source-verified [08-05 并入] | [[Papers/2608-AgentStream]] Appendix A | "不更新参数"不等于"不花钱"，成本-收益比由底座决定；该组数字基于单次评测而非三 seed 平均；论文印出的 code 链接 404，canonical 路径当前仅含 README |

## 调研日志

### 2026-08-05 增量更新（survey-refresh）

- **merged（2 篇）**：[[Papers/2607-HarnessBank]] → §6.2（gate 家族第六种粒度 + gate/部署选择器分离 + gate 独立性三层）、§6.4/§7.2/§9.1/§10.6/§11/§12；[[Papers/2608-AgentStream]] → §9.2（流式评测第三个条目）、§3.3/§5/§9 索引表/§9.4/§11/§12。
- **skipped**：无。
- **被降级的结论**：§6.2 的"gate 不只是安全阀，而是收益/可靠性的主要来源"由共识降为**争议**，推动者是 [[Papers/2607-HarnessBank]] Table 3——去掉 2σ 判据后 TB2 test Pass@1 ±0.0，因为训练集 argmax 这个独立的部署选择器已经选中同一赢家，gate 的可测价值全在假精英 2→0 与收敛轮数 >20→10。该结果与 [[Papers/2606-SkillNb]] 同向（去 gate 只掉约 6 分而回归 3.3%→18.6%），两处证据台账齐备的自身消融共同把已测得的 gate 价值定位在地板与效率轴；方向相反的 [[Papers/2605-GRASP]]（去闸门 88.8%→63.5%）结构不同——其闸门即部署决策、无下游 argmax 兜底，且该侧记录缺证据台账与核验状态。正反两侧并列保留，条件变量记为"gate 之外是否存在冗余的部署选择器"。§1.2、§10.6、§12 其二同步改为条件性表述，原有数字与结论一处未删。
- **结构变化**：§6.2 标题由"gate 即收益来源"改为"gate 扛的是地板还是天花板"，表扩为六粒度并新增三段（选择器分离 / 跨方法与自身消融的区别 / 独立性三层）；§9.2 由两个 benchmark 扩为三个并新增流式评测两段；§3.3 新增耦合强度这一正交划分（记为观察而非新分类轴）；§9 索引表 +2 行；§11 新增开放挑战"自演化增益的存在条件"，并把归因缺口补到第四种形态（组件被冗余机制替代）；§12 新增第四条判断（增益是条件性的）。
- **验证边界**：两篇均为 `full-text` + `source-checked`，进入正文的数字全部对应 source-verified 的台账条目，表述只到"原文一致性已核查"而非独立复现。两篇均单次或小样本运行：HarnessBank 无算力配平对照、无误收/误拒率、与基线比较存在 proposer 强度混淆；AgentStream 全文无显著性检验且效应量普遍小于其单元格 seed 间标准差，其结论按形态而非数值采用。[[Papers/2605-GRASP]] 缺 Evidence Ledger 与核验状态，本次未据它新增任何数字或升级任何结论，仅保留其既有引用作为争议的一侧。Key Evidence Matrix 新增 8 行。

### 2026-08-04 增量更新（survey-refresh）

- **merged（3 篇）**：[[Papers/2607-SpyRL]] → §3.4（反馈信号轴新增"构造式可验性"）、§4.2/§4.4/§4.5/§9/§12；[[Papers/2607-SESA]] → §4.2（proposer-solver 闭环的技能库变体）、§6.3（关库对照）、§6.4/§9；[[Papers/2608-RoMeRL]] → §5.3（read-side 主体）、§5.1 表 / §5.6/§9/§11。
- **skipped**：无。
- **结构变化**：§3.4 新增一段把可验证性从任务固有属性改述为可设计属性，并当场标出该 move 在其唯一实例上的失真处（performing reward 仍是自任 judge）；§4.4 由三级谱系扩为四个位置；§4.5 新增第四个开放缺口"优化侧设计从增益来源变成稳定性前提"（SpyRL 两个净负消融跌破未训练基座）；§5.3 由一段扩为完整的 memory-reward trap + reduced-order 状态分析；§5.6 新增 read-side 的两个开口与可复用的 null 化污染探针；§6.3 内化 vs 外挂分岔补上部署期关库对照并改写默认归因；§9 benchmark 索引表 +3 行（七集合 QA / ALFWorld+LAB / 开放式生成）；§11 "演化增益归因" 补第三种形态（演化组件自身未被隔离）；§12 其一补构造式可验性的定位与边界。
- **未推翻既有结论**：本轮无原有结论被推翻。§4.2 中 proposer-solver 自博弈的正向证据保留原样，但补入 SpyRL 附录 D.1 的域边界数据（R-Zero 在开放式生成上对自身基座等于未训练甚至负增益）——这是对适用域的限定，不是对既有数字的否定。§6.3 的"真分岔"表述保留，改的是外挂路线总增益的默认归因方式。
- **验证边界**：SpyRL 与 RoMeRL 为 `source-checked`（26/26、20/20 由独立 verifier 核过），SESA 为 `partial`——其协同演化机制、算力/token 匹配对照、seed 与误差棒三项标 `unsupported`，正文只采用 Off/On 分解与消融数字，机制主张未采用。三篇全部单次运行、无方差报告；SESA 的关库对照标"库内暂无独立验证"。Key Evidence Matrix 新增 6 行。
- **domain_map**：刷新 [[DomainMaps/AgenticRL]] 近期格局变化 2 条。

### 2026-08-02 增量更新（survey-refresh）

- **merged（2 篇）**：[[Papers/2607-MANTA]] → §7.1（新增 inference-time topology 改写分支）、§3.4/§3.5/§6.2/§8.3/§10.2；[[Papers/2607-FrontisMA1]] → §7.2（scaffold lineage 的权重回灌支）、§7.3/§9.1。
- **skipped**：无。
- **结构变化**：§7.1 由一句 offline 搜索概述扩为"offline 搜索 vs inference-time 改写"三段；§3.4 反馈信号轴新增第五类**纯过程审计**（不接触结果的演化信号），四维分类表相应扩值；§6.2 新增 gate 谓词 precision 的首个数字并区分触发闸门与验收闸门；§7.3 把"改进标量分数不足以选 parent"确立为四工作收敛判断（DGM 即时分数 / HGM clade 聚合 / Frontis-MA1 多因子固定权重效用 / MANTA 纯过程 flag），并指出三类信号从未同 testbed 对照；§7.5 与 §11 各新增一条 open challenge（RSI 术语与实物错位的判据；演化增益的预算与来源归因）；§9 benchmark 索引表增 MLE-Bench Lite 行。
- **未改**：Key Evidence Matrix 新增 4 行，原有行未修订——本轮两篇均未推翻既有结论，MANTA 是 §7.1"这类工作多为 offline 搜索"的例外而非反证（原表述作为对该路线主流的描述保留并显式标为例外）。
- **domain_map**：刷新 [[DomainMaps/AgenticRL]] 近期格局变化 2 条。

### 2026-07-29 全面重构（20 篇一手核验 + 12 节 CUA 标准重排）

- **规模**：07-24 版（30 篇、4 路线）→ 本版（约 50 篇、12 节）。本轮独立 digest + verifier 核验 20 篇一手论文，200+ 条 source-verified claim，0 条 unsupported 进入正文。
- **结构升级**：四路线（§4–§7）保留并各成章；新增 §3 四维分类（对象×信号×时机×gate）、§8 协同演化（env + multi-agent）独立成章、§9 benchmark 与评估方法学、§10 安全失效模式系统化（misevolution + 负性三线 + 威胁谱 + gate 可靠性）。
- **基础保留（完善而非替换）**：07-24 版的两张核心表——route×收益×风险横切表、Datasets & Benchmarks 全景表——重排后分别落位 §3.6 与 §9 索引表并用本轮数字刷新（StuLife/SkillFlow 行补全）；旧版已 digest 但被压缩的 4 篇（[[Papers/2500-UiGenieSelfImproving]] §4.2、[[Papers/2600-UiMemSelfEvolving]] §5.2、[[Papers/2605-HASP]] §6.1、[[Papers/2606-LearningFromFailure]] §6.1/§9）全部复位并与新机制线索缝合，未丢一篇一表。
- **本轮新机制/判断**：(1) memory 演化细分为 write-side/read-side/**operation-level** 三位置，MemSkill 确立操作级为新亚型（blast radius 最大）；(2) RSI 谱系补 HGM 的 **clade-level credit assignment**（CMP 0.778 vs DGM 0.285），瓶颈从"改法"转"选法"；(3) gate 扩为**五粒度家族**（edit/step/audit/统计证书/形式验证）对 Live-SWE 零 gate；(4) 负性结果三线（reversal/rise-and-collapse/recursive collapse）——CodeSelfReviewCollapse 的 rubber-stamp 定理成为所有 self-gate 设计的硬约束；(5) 威胁谱两端点：ExperienceSafetyRisks（良性完整测量）↔ MemoryGraft（对抗但证据强度不匹配，rating 2）。
- **核验修订实锤**：EnvEngSurvey C8/C9（AutoEnv/AgentWorldModel 误归 task/real-world-driven → de-novo；refs 382→582）；MemSkill affiliation 补全 NTU+UIUC+UIC+Tsinghua、controller 三独立 MLP；HGM 53.2% 语义（调整后初始 agent full-Verified 起点 ≠ Verified-60 的 40%）；MetaTeam 四处修订（GAIA=77.3 非 87.9/后者是 LOCA、failure-attribution pilot 六数字全错已改为 Fig 1b 实读值、跨语言迁移幅度 digest 高估、Appendix D 存在一致性/预算级 gate 非"无 gate"）；多篇抓到论文内部数字不一致（AlignmentTipping、MLAS、SEAL 词表）。
- **verifier 额度中断处置**：末两篇 benchmark（StuLife 2508.19005 / SkillFlow 2604.17308）派出的独立 verifier 子代理因账户月度额度上限终止；改由 main-loop curl 直取 arXiv HTML 自核 headline 数字（StuLife 1284/17.90/4.68/85.24/98.18、SkillFlow 166/62.65/71.08/52.41/46.39 全部命中），其余 claim 保留 digest 级并在两篇笔记 Evidence Ledger 与 §9/Matrix 明确标注核验边界，未 overclaim 为 source-verified。
- **gap pass 结论**：On-Policy Self-Evolution via Failure Trajectories = **2605.11882**（FATE，Yin/Li/Wang，safety-alignment），baseline survey 原引正确；搜索误配的 2601.08584 是 Ministral 3 无关论文，已弃。
- **keyword 扩展**：frontmatter 补 co-evolution / recursive self-improvement / self-training / memory poisoning / environment evolution / multi-agent evolution / operation-level memory / evolution gate，修复 SEAL/LiveSWE/SkillFlow 等未被 survey_updates 自动匹配、本轮手动纳入的缺口。
- **待 Supervisor 复核**：[[Ideas/RetrievalMediated-MemoryMisevolution]] 的 07-21 检索记录有误——2606.23075 未命名 retrieval-mediated 机制（仅 §4.2/4.3 描述），概念首发权未被占据；本轮未改 Ideas/。

*07-24 及更早的四路线细节增量记录见 git history；本次重排已吸收其全部有效内容。*
