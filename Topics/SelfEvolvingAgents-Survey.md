---
title: "Self-Evolving and Self-Improving Agents: A Unified Survey of Evolution Targets, Feedback, Gating, and Safety"
tags: [survey, self-evolving-agents, self-improvement, recursive-self-improvement, agentic-RL, LLM, misevolution]
date_updated: "2026-09-18"
year_range: 2022-2026
papers_analyzed: 76
keywords: [self-evolving, self-evolution, self-improving, self-improvement, recursive self-improvement, self-recursive improvement, misevolution, lifelong agent, skill evolution, memory evolution, operation-level memory, experience-driven, co-evolution, environment evolution, multi-agent evolution, skill optimization, skill library, self-training, memory poisoning, evolution gate, verifier gating, harness evolution, streaming evaluation, evolution gain]
domain_map: AgenticRL
supersedes: "SelfEvolvingAgents-Survey 07-24 版（30 篇、4 路线）已并入本文并按 12 节 CUA 标准重排"
---

> [!note] 版本说明（2026-07-29）
> 本文在 07-24 版四路线综述基础上按 12 节完整目录重排，覆盖 76 篇文献（recursive self-improvement 谱系、负性结果、env/multi-agent 协同演化、operation-level memory、gate 家族、安全威胁模型）。所有进入正文的 benchmark 数字与机制主张均标注 grounding，边界见 Key Evidence Matrix。

# Self-Evolving and Self-Improving Agents: A Unified Survey

## 1. Introduction

### 1.1 术语链与统一纲领

Self-improvement 与 self-evolving 是同一研究纲领在两个系统层次上的名字：让 AI 系统从自身生成的经验中持续改进，而不依赖外部人工监督。三篇 anchor survey 的分工恰好沿术语演进链划分：

- **Self-improvement（2022–2024，model-centric）**：模型参数的自精化。谱系为 **STaR**（自生成 rationale 过滤再训练）→ **Self-Instruct / Evol-Instruct**（自生成指令数据）→ **Self-Refine / Reflexion**（推理时自反馈，不改参数）→ **Self-Rewarding LM / SPIN**（模型自当 judge 做迭代 DPO 或 self-play 微调）→ **Absolute-Zero / R-Zero**（proposer-solver 同体，零外部数据）。[[Papers/2404-LLMSelfEvolutionSurvey]] 把它框架化为 experience acquisition → refinement → updating（in-weight / in-context）→ evaluation 四阶段循环。
- **Self-evolving agents（2025– ，system-centric）**：演化对象从模型参数扩展到 agent 系统的四组件——model / memory(context) / tool / workflow(architecture)。[[Papers/2507-SelfEvolvingAgentsSurvey]] 给出操作性定义（experience-dependent 更新 + persistent policy-changing 效果 + 自主探索），并与 lifelong learning、model editing、LLM self-improvement 显式切分；[[Papers/2508-SelfEvolvingAIAgentsSurvey]] 用统一优化框架（System Inputs / Agent System / Environment / Optimiser 闭环）+ Three Laws（Endure 安全 > Excel 保性能 > Evolve 自主演化）组织同一领域。
- **Misevolution（2025-09– ，safety-centric）**：[[Papers/2509-Misevolution]] 命名并实证"演化过程自身偏航"的风险，标志领域从"能不能演化"进入"演化会不会坏"的阶段。

### 1.2 2026 的活跃前沿

2026 年同时加速的主线有六条。其一，**recursive self-improvement 的 scaffold lineage 成型**——自改代码 agent 从 Darwin-Gödel Machine 的开放式 archive 走向 [[Papers/2510-HuxleyGodelMachine]] 的 clade 级 credit assignment 与 [[Papers/2607-MetaSkillEvolve]] 的"演化改进流程本身"两级递归。其二，**负性结果集中爆发**——self-improvement reversal、rise-and-collapse、recursive self-training collapse 刻画的是演化过程自身跑偏的条件，[[Papers/2609-Ecdysis]] 与 [[Papers/2607-RethinkSkillEvolve]] 又补上一种发生在闸门之后的形态：每一步改动都通过了接受判据，交付到 held-out 上仍是净负（§10.2）。其三，**agent-environment co-evolution 从概念变为实证**——环境从静态评测台升格为共同演化对象（[[Papers/2605-SEAL]]、[[Papers/2512-GenEnv]]、anchor survey [[Papers/2606-EnvEngineeringSurvey]]）。其四，**演化步 verifier gating 从方法空白扩展为多粒度家族**——从技能编辑级到 anytime-valid 统计证书到形式化验证合成，gate 从安全阀被重新论证为可靠性的主要来源；但它是否同时抬高性能天花板，在 2026 年中已成为有正反实测的争议（§6.2）。其五，**演化信号开始越出"从自己成功的轨迹里学"这一默认设定**——一组 rollout 全部失败时二值 reward 在组内退化为常数，[[Papers/2608-ZerothOrderSelfEvolve]] 用参数空间扰动加 gold-answer 连续似然绕开这个真空，[[Papers/2608-ROPSD]] 把反思文本转成 token 级监督，两者都落在 anchor survey 的信号分类（verifier / self-reward / judge / 共识伪标签）之外（§4.3）。其六，**演化收益开始被匹配对照与噪声带检验**——固定 executor、固定流程、只改 optimizer 可见的轨迹之后，[[Papers/2607-RethinkSkillEvolve]] 在 14 个 setting 上测到"演化后部署 test 更好"只有 9 个，而一份字节完全相同的技能重复评测八次落在 71.43%–83.67%（标准差 3.92 个百分点）；[[Papers/2608-SkillZipPro]] 则第一次把等价性写成预先声明的判据（102 个 held-out 任务、配对 bootstrap、事先固定的 −0.05 边界）。这条线把"演化涨了多少"从单点比较推到了必须先给出协议分辨率（§9.4、§10.2）。

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

第二类边界情形是机制齐备而测量没跟上。[[Papers/2605-SEGA]] 同时具备两套演化：三轮离线演化重训（AndroidWorld 28.6 → 34.5 → 39.0），以及一个在推理期累积、跨任务复用的 test-time memory buffer。后者按 §2.1 三条件是合格的部署后演化，但全文没有任何实验把 buffer 的效应与训练轮次分开，两者始终一起上线。本文因此按训练期演化引用它的数字，其"无需重训即可在线演化"的部分不作为部署后持续演化的证据——这类拆分缺口在 §6.3 的关库对照与 §7.2 的 harness 份额拆分中是同一种要求。

第三类是形式描述与实物的不匹配，判据本身仍然适用但需要显式落回三条件。[[Papers/2609-GeneralizedAgentIteration]] 把自改进系统写成 $\chi=(\pi,V,m,U,\rho)$ 并用"更新算子是否落在可修改子集内"定义递归性，这套坐标比 §2.1 宽——它不问更新发生过几次，也不问是否在部署后。两套判据在 §7.5 并置使用：形式坐标用于命名，三条件用于判定实物。

### 2.3 纳入与排除标准

**纳入**：以 LLM/VLM agent 为主体、满足 §2.1 三条件、2022–2026 的方法/benchmark/安全/survey 论文。**排除**：纯 model editing、纯 offline AutoML、无自主探索的 continual learning、以及 keyword 命中但机制不符的离线蒸馏工作。**边界纳入**：recursive self-improvement 理论工作与 co-evolution anchor survey 作为背景纳入，但证据强度按其类型（理论/综述）标注。

### 2.4 文献检索与来源

双通道检索：OpenAlex（结构化元数据）+ WebSearch（覆盖 arXiv 新预印本），角度覆盖 RSI/scaffold、skill/memory 演化、负性结果、env/multi-agent 协同、lifelong benchmark、自改代码、安全/alignment 演化八类。一手全文经 arXiv HTML / ar5iv / lexmount 三级回退获取。索引对 1–2 周新论文有滞后，故对 fresh arXiv 采用直链核验而非仅依赖搜索。

### 2.5 论文编码与证据分级

每篇论文的高风险 claim（benchmark 数字、机制主张、负性论断）经独立 verifier 对照一手来源核验，状态分：**source-verified**（原文可查）、**跨来源收敛**（多篇一致）、**作者综合论断**（合理但单一来源）、**库内暂无独立验证**。07-29 重构纳入的 20 篇论文共核出 200+ 条 source-verified claim，并抓到多处论文内部数字不一致（记于各 Paper 笔记 Evidence Ledger）。

## 3. Problem Formulation and Unified Taxonomy

### 3.1 统一形式化

自演化系统可写成闭环 M ≡ (Θ, C, T, W)，其中 Θ 为模型参数、C 为 runtime context/memory、T 为 tool/skill 库、W 为 workflow/architecture 与团队组织；演化算子 U 在经验流上更新其中一个或多个分量：Mₜ₊₁ = U(Mₜ, experience(Mₜ, Env), signal)。[[Papers/2508-SelfEvolvingAIAgentsSurvey]] 的 System Inputs / Agent System / Environment / Optimiser 四元与此同构，Optimiser 即 U。三个决定成败的量是：U 作用于哪个分量（**演化对象**）、signal 从哪来（**反馈信号**）、U 何时触发且是否过关（**时机与 gate**）。

### 3.2 四维分类

本文用四个正交轴组织全部工作：

| 轴 | 取值 | 决定的性质 |
|:--|:--|:--|
| 演化对象 | model / memory / tool-skill / architecture / 团队组织 | 收益上界与 blast radius |
| 反馈信号 | deterministic verifier / internal self-reward / LLM-judge / 共识伪标签 / 纯过程审计；正交属性：信号分辨率（二值 vs 连续或 token 级） | 收益质量与 reversal 风险 |
| 演化时机 | train-time / deploy-time / on-the-fly | 部署开销与漂移暴露面 |
| Gate 粒度 | none / edit-level / step-level / 统计证书 / 形式验证 | 可靠性与可审计性 |

四轴的组合而非任一单轴决定一个系统的行为——这是全文的组织原则，也是对"把 claim 建在先验分类学上"的规避：分类是事后按干预有效性聚类的输出，不是先验真理。

### 3.3 演化对象轴

四组件加团队组织构成对象空间。关键观察：**blast radius 随对象层级升高而放大**——改一条 memory 只影响一次检索，改一个 skill 影响所有复用该 skill 的任务，改 workflow/constitution 影响全队所有 agent。§10 的安全分析显示风险与 blast radius 正相关。

一个正交于对象轴的划分由跨方法受控析因提出。[[Papers/2608-AgentStream]] 按**经验与执行上下文的耦合强度**把自演化方法重划为两族：context-integrated（经验直接折进 agent prompt，如 ACE 与整体 harness 演化）与 retrieval-based（经验存外部库、只注入当前任务检索到的条目，如 ReasoningBank、AutoSkill、A-Mem）。两族在任务流结构上的收益符号相反——同域内独立累积时 ACE 平均 +2.28、跨域混流时降到 −1.26，而三个检索式方法全部在混流下取到峰值（+2.22 / +1.79 / +0.72）。其含义是紧耦合的经验在跨分布流里无法被门控，松耦合天然只激活相关条目，因而"该演化哪个组件"可能是次要轴。本文暂不据此重排分类：该工作全文无显著性检验，单元格的 seed 间标准差常在 3–6 个百分点而效应量在 1–2 个百分点量级，符号翻转是目前最干净的形态证据，绝对幅度不足以承重。

### 3.4 反馈信号轴

反馈信号的可验证性是四条路线共同的成败分界（详见 §4.4）。deterministic verifier 域（代码测试执行、几何计算、规则验证）收益最大最稳；internal self-reward 域有偏差放大与 reversal 风险；LLM/VLM-judge 域介于两者之间且 judge 噪声直接进训练集；共识伪标签（majority-voting）在无 ground truth 的视觉域是唯一退路，但会逐代劣化。这与"verifier 从评测工具变为训练监督源"这一判断在自演化语境下汇合：**verifier 质量上界决定 self-evolution 收益上界**。这条上界该按"判分质量"而非"判分准确率"读：[[Papers/2608-GSAR]] 的学习式 GUI 轨迹判分器离线准确率 91.5%，把规则式对照甩开十几个点，接进同一条在线 RL 管线当 reward 之后反而少涨 2.6 个点（§4.4）。

第五类信号是**纯过程审计**——只看执行痕迹（工具记录、证据可见性、未决问题、置信度），完全不接触任务是否做对。它的意义在于把演化信号与评价信号从结构上切开，因而不受"演化闸门其实就是打分模型"的循环质疑；代价是信号本身弱且未经独立校准。[[Papers/2607-MANTA]] 是目前唯一给出这一代价定量的工作：其 Trace Auditor 明确不可访问 benchmark 答案或判分，450 run 上无 flag 的 run 正确率 83.2%、被 flag 的 62.5%（差 20.7 点），但作为"答案是否错误"的检测器总体 precision 仅 0.38、F1 0.47，且分域极不均——WorkBench F1 0.78 而 BrowseComp 假阳率 0.90、PlanCraft 90 run 只 flag 出 1 次。过程信号与结果正确性确有关联但远非等价，这一点在 §6.2 的 gate 家族与 §10.6 的可靠性讨论中都是硬约束。

这条轴此前被默认为**任务的固有属性**——一个域要么有 verifier，要么没有。[[Papers/2607-SpyRL]] 提出的 RLSVR 把它改写为可设计的属性：由环境采样一个隐变量 $z$（谁的输入被退化、哪一步被删掉）并记为该 episode 的 ground truth，让 agent 在被 $z$ 条件化的观测上执行**原任务**，再由环境提出一个只能凭任务输出回答的关于 $z$ 的问题，最后按规则核对。ground truth 由构造而存在，因此标准 GRPO 机器可以直接套用到本无 verifier 的域。这个 move 值得单列，但它并不把不可验证的域搬到可验证端：在其唯一实例 SpyRL 里，真正塑造生成质量的 performing-stage reward 等于得票数，由被训练的同一个模型扮演 detector 投出，论文自己的 Algorithm 1 就把它标注为 "non-verifiable rewards made by detectors"，规则可验的只有 detection-stage 那一项。诚实的读法是**判分负担被从外部 judge 转移到自博弈内部**（省掉论文所称的 \$200 / \$900 verifier 开销），而非被消除——这也解释了它对 GPT-4o-RaR 的整体胜率停在 48.9% / 48.2%（详见 §4.4）。

可验证性之外，这条轴还有一个此前被并进去的属性：**信号的分辨率**。GRPO 一族用组内相对优势，因此当一组 rollout 全部失败、二值 reward 在组内退化为常数时梯度估计恒为零——[[Papers/2608-ZerothOrderSelfEvolve]] 把这一点写成推导（所有轨迹拿到同一 reward 时 $\hat g_{RL}=0$），[[Papers/2608-ROPSD]] 在实测里撞上同一堵墙（纯标量 reward 的 GUI-RCPO 在 MMBench-GUI 上负迁移 −0.3）。两篇的绕法都不是换一个更可信的 verifier，而是提高同一份失败经验的分辨率：前者把判据换成 gold answer 上 token-normalized 的 NLL（连续，失败轨迹只要检索到部分支持证据就有下降），后者把反思文本条件化出 self-teacher、取它与无条件 policy 的 token 级 log-ratio 当 advantage。代价各自明确，且都不是无监督：前者要求存在可核对的 gold answer，后者要求一个先用带标注数据训出来的 Reflector（held-out 二分类准确率 89.5% / 91.7%）。**标注需求被从轨迹层挪到别处，而不是被消除**（详见 §4.3）。

分辨率之外还有一层此前被一并计入信号质量的东西：**稠密信号里有多少是内容，有多少只是落点与符号**。[[Papers/2608-OPSA]] 把 on-policy distillation 的 token 级教师信号整个换成一个固定负常数、只施加在学生自己 log-probability 最低的 20% token 上，训练效果与完整教师相当，而把这个常数改成正的则策略崩溃。被质量上界约束的是信号的判别内容，而在这个设置里真正起作用的是它落在哪些 token 上以及朝哪个方向推——两者可以解耦（§4.3）。

### 3.5 演化时机与 gate 轴

时机决定漂移暴露面：train-time 演化（如 [[Papers/2607-SEED]] 把 hindsight skill 蒸进参数、部署弃用）漂移风险最低；deploy-time 演化（memory reward hacking）漂移风险最高；on-the-fly 自改（[[Papers/2511-LiveSWEAgent]]）介于两者。时机轴的最细端点是**任务实例之内**：[[Papers/2607-MANTA]] 在解同一道题的两轮之间改写通信拓扑，跨 run 只留原则性 playbook，因此单次错误的持久面最小——但也因此每个 instance 都要重付一次演化开销（§7.1）。同一端点在 harness 侧的形态是 per-instance 合成：[[Papers/2608-JITAgent]] 训练一个生成器，在每个任务实例到达时现场产出该实例专用的工具集、状态机与提示协议，权重与生成器全程不变，于是被演化的对象从"部署前选定的一套配置"变成"每个实例各一套"，而代价同样是每个实例都要重付一次生成开销（§7.4）。gate 粒度从无（Live-SWE-agent 与 [[Papers/2608-TRACE]] 零关口）到 edit-level（[[Papers/2605-GRASP]]）、step-level（[[Papers/2606-SkillNb]]）、patch 筛选级（[[Papers/2607-HarnessBank]]）、统计证书（[[Papers/2607-SEACertificates]]）、形式验证合成（[[Papers/2603-SEVerA]]）构成一条可靠性谱（详见 §6.2）。

deploy-time 一端此前只有不动参数的记忆演化，[[Papers/2608-ROPSD]] 把参数更新也放了进来：GUI grounding 模型在部署侧的无标注界面数据上，用自己的预测与一个冻结 Reflector 的反思做 LoRA 更新。它同时暴露这一端点的边界——适配数据就是待测集合本身（transductive），任务流由评测给定而非自主生成，按 §2.1 第三条件只算边界纳入；其收益读法也因此不能直接搬给"部署后遇到什么学什么"的在线设定。

### 3.6 四路线横切汇总

把四条演化路线按"反馈来源 × 已证收益 × 已证风险"并置，可一眼看出收益与风险都随演化对象层级升高而同步放大——这也是本文以"演化对象"作为首要组织轴的实证依据。各路线机制详见 §4–§7。

| 路线 | 代表 | 反馈来源 | 已证收益（代表数字） | 已证风险（实测） |
|:--|:--|:--|:--|:--|
| Model（参数） | WebRL / [[Papers/2412-PAE]] / [[Papers/2500-UiGenieSelfImproving]] / [[Papers/2607-SEED]] / [[Papers/2606-VisPlay]] / [[Papers/2607-SpyRL]] / [[Papers/2608-ZerothOrderSelfEvolve]] / [[Papers/2608-EvoHarnessRL]] / [[Papers/2608-OPSA]] / [[Papers/2609-FlowBalance]] / [[Papers/2609-NeoHorse1]] | ORM / VLM-judge / 自奖励 / 共识伪标签 / 构造式可验 reward / gold-answer 似然 / 反思蒸馏 / 自身低置信 token / 符号门控的 hindsight 能量 / 部署路由器预测的能力档位 | WebArena-Lite 4.8→42.4（WebRL）；ALFWorld 91.8 vs GRPO 75.0（SEED）；无标注 3B 30.6→47.3（VisPlay）；七数学 benchmark 均值 41.4→50.4（SpyRL）；GAIA 23.3→47.5（ZO 参数空间搜索）；ALFWorld seen 47.9→96.9（EvoHarness-RL）；AIME24 Avg@32 13.44→48.85 且训练不用答案只用问题（OPSA）；五数学 benchmark 均值 67.61 vs GRPO 65.49（FlowBalance） | safety 累积衰减（Misevolution）；risk-awareness 灾难性遗忘（SEAgent）；共识伪标签逐代劣化 72→61；去掉两处优化侧设计后跌破未训练基座（SpyRL 50.4→37.5 vs 基座 41.4）；增益与被演化组件的因果链未闭合（EvoHarness-RL 收敛后 harness 调用退火到约每 episode 一次，而其 SFT teacher 自身 ReAct 在同一 split 上已 96.4，无去 BPE 的同管线对照臂）；教师监督噪声随教师规模上升（OPSA 测到 30.6/34.7/50.6%）；核心设计未被消融（FlowBalance 的符号门控无 $\beta_G=0$ 臂） |
| Memory/Context | [[Papers/2409-AgentWorkflowMemory]] / [[Papers/2600-UiMemSelfEvolving]] / [[Papers/2601-MemRL]] / [[Papers/2602-MemSkill]] / [[Papers/2608-RoMeRL]] / [[Papers/2608-PRACTICE]] / [[Papers/2605-SEGA]] | 历史评分 / 检索命中 / task reward / 冻结 executor 的成败分组 | WebArena 相对 +51.1%（AWM）；LoCoMo 53.82、调用量低一量级（MemSkill）；ALFWorld+LAB overall 0.830→0.862 且记忆池 −84.4%（RoMeRL）；EB-ALFRED 49.7 vs 最强经验增强基线 40.0，终库仅 29 张 card（PRACTICE） | deployment-time reward hacking >60% 且可突然崩塌（Misevolution）；operation-level blast radius 系统性放大；memory-reward trap——扩大探索使无因果贡献的记忆吃到更多正向更新（RoMeRL 注入实验 3.7→7.2） |
| Tool/Skill | Voyager / [[Papers/2605-SkillOpt]] / [[Papers/2605-GRASP]] / [[Papers/2606-SkillNb]] / [[Papers/2606-LearningFromFailure]] / [[Papers/2607-SESA]] / [[Papers/2608-SkillZip]] / [[Papers/2608-SkillZipPro]] / [[Papers/2608-TRACE]] / [[Papers/2609-COBRASkills]] / [[Papers/2607-RethinkSkillEvolve]] | validation gate / A/B / held-out 探针 / state-contract / 前沿难度整形 / 不接触任务的结构压缩 / 无闸门的反复执行重建 / bandit 预算分配 | 6 bench 平均 +23.5（SkillOpt）；OSWorld 零训练 42.3→48.9（LearningFromFailure）；七集合 QA Qwen3-8B 56.3→59.5（SESA）；CAR-bench held-out Pass^3 50.0→70.0（TRACE）；三底座相对无技能 +13.1/+26.9/+22.5 且总成本降 55%–58%（COBRA） | 创建-复用 Unsafe Rate 65.5%；外部工具摄取 Refusal <8%（Misevolution）；技能库的部署期贡献可能远小于其训练期贡献（SESA 关库仍得 +1.8/+2.2，开库只再加 +0.5/+1.0）；技能文本随演化膨胀（SkillOpt 5 轮后达初始约 5.2×）；经验层投毒可被抽取成独立存储的 skill 并在删源后存活（[[Papers/2608-SkillJack]]，§10.4）；匹配对照下端到端只有 9/14 个 setting 在部署 test 上更好，字节相同技能重测标准差 3.92 点（RethinkSkillEvolve）；演化产物可能固化沙箱专属绕法（§10.7） |
| Architecture / RSI | [[Papers/2505-DarwinGodelMachine]] / [[Papers/2510-HuxleyGodelMachine]] / [[Papers/2605-MetaTeam]] / [[Papers/2607-MANTA]] / [[Papers/2607-FrontisMA1]] / [[Papers/2608-JITAgent]] / [[Papers/2608-Zetta]] / [[Papers/2609-RSIAgent]] / [[Papers/2609-DreamRSI]] / [[Papers/2609-Ecdysis]] | benchmark 分数 / clade 聚合 / 团队讨论 / 纯过程审计 / 执行反馈 / 冻结树上的重放分 / 跨任务失败模式聚类 | SWE-bench 20→50（DGM）；full Verified 61.4%（HGM）；组织演化 53.9>40.8（MetaTeam）；等 token 下 74.0 vs Voting 64.7（MANTA）；MLE-Bench Lite 39.39→60.61（Frontis-MA1 post-training 净增）；RoboCasa 73.56→93.56（Zetta，冻结 VLA 之外的 harness 演化）；18 个 matched 配对全部提升且成本降 14.9%–54.1%（JIT-Agent）；轮级聚类改 harness 5 模型 × 2 子集平均 59.33 对逐条改的 46.67、10/10 格方向一致（Ecdysis） | AFlow 20 轮 ASR 54.4→83.1%；self-review gate 退化为 rubber-stamp；增益归因不闭合（MANTA 结构改变与 +28K token 绑定；Frontis-MA1 自改进与外部 teacher 蒸馏未分离）；harness 与自改进机制的份额未分离——受控对照下 harness 贡献是机制的三到四倍（RSI-Agent）；离线搜索自身的开销不计入报告 compute（Dream-RSI）；逐条失败改 harness 的同协议基线跌破人工起点 51.67→46.67（Ecdysis） |

风险一列的共性——safety 衰减、reward hacking、rubber-stamp、Unsafe Rate 高——统一指向 §10：演化的失效不在"能不能改进"，而在"改进过程自身会不会偏航且无关可拦截"。

## 4. Model Evolution（参数自演化）

模型用自身产生的任务、解答或奖励更新权重——唯一能提升模型本体能力的路线，也是受 reversal 与 safety 衰减约束最强的路线。

### 4.1 自生成数据与课程

自生成数据谱系 STaR / ReST(EM) / Self-Rewarding / SPIN → Absolute-Zero / R-Zero（proposer 与 solver 同体互促）；自生成课程 [[Papers/2411-WebRL]]（从失败经历自动生成新任务 + ORM，Llama-3.1-8B WebArena-Lite 4.8%→42.4%）与 SEAgent（computer-use 侧从失败轨迹定向出题）。共同结构是"agent 既是数据消费者又是数据生产者"，收益来自课程与能力边界的自动对齐。

难度标签此前只有两个来源：人工分档，或 solver 自己的通过率估计。[[Papers/2609-NeoHorse1]] 用了第三个——生产环境里本来就存在的部署路由器。它为每一轮对话预测所需的能力档位以决定派哪个模型，这个预测被直接回收成训练语料的难度标签，用来把语料排成由易到难的三段课程。吸引力在于标签是部署副产品、零额外标注成本；代价是它测的是"路由器认为多难"而不是"当前 solver 做不做得到"，与能力边界的对齐因此是间接的。Qwen3.5-4B 在十个 benchmark 上的无权均值 58.94→64.87、9B 65.60→69.04，同 harness、同工具接口、同预算下与自己的基座比较。但全文没有任何消融把课程排序、on-policy distillation 与能力导向的数据配比三者分开，所以这批数字支持的是"这套组合有效"，不是"课程排序有效"。它的第二个对照更需要按边界读：路由式 harness 70.57 相对 Toucan 基线的 64.32 高出 6.26 点，可基座本身是 69.31——Toucan 跌破了基座，路由式 harness 相对基座只有 +1.26，而这 1.26 里 HumanEval 独占 +9.14，其余四项合计 −0.57。

### 4.2 proposer-solver 闭环

[[Papers/2412-PAE]]（VLM 提任务/评结果的能力不对称支撑弱模型引导强 agent，WebVoyager 开源 SOTA 33.0%）与 [[Papers/2500-UiGenieSelfImproving]]（agent 与 reward model 联合迭代自增强，verifier-first）是闭环三角的两个代表。能力不对称性（评估比生成易）是这类方法可行的前提。

[[Papers/2607-SESA]] 在 SSP 式非对称自博弈骨架上加了两处改动：challenger 与 solver 参数分离，且技能检索**只**给 solver——出题方看不到技能库，因此题目难度不会被技能库直接牵引；reward 由钟形的 frontier shaping 给出（对求解率 $\hat p_s$ 落在 0 或 1 的端点罚 $-\lambda$，否则取 $4(\ell+\hat p_s)(h-\hat p_s)$），把 proposer 的目标从"越难越好"改成"停在当前能力边界上"。solver 侧用 GRPO、每题 5 rollout、top-3 技能检索，技能以 $(u,c,a,z,m)$ 五元组入库并配一整套维护规则（E5-base-v2 余弦 ≤0.93 准入、检索 ≥3 次后 helpful−hurt < 0 淘汰非种子、上限 800）。七个开放域/多跳 QA 集合上 Qwen3-8B 56.3→59.5、Qwen3-4B 53.9→56.2（对 SSP 分别 +3.2 / +2.3）。它的价值不在这个幅度，而在它是库内唯一做了**关库对照**的技能演化工作——该对照把收益归因整体改写，见 §6.3。

这条路线的域边界由一篇外部工作补上：[[Papers/2607-SpyRL]] 的附录 D.1 把每个方法对**自己的**未训练 backbone 做换序聚合 A/B，未训练自比落在 51.7% / 51.8%，而 R-Zero 在 summarization 上是 51.9% / 51.5%（等于没训练）、在 creative writing 上对 Qwen3-4B 只有 48.8% / 46.5%（**训练后反而变差**）。proposer-solver 自博弈的既有正向证据几乎全部落在数学/代码这类有确定性 verifier 的域，把它直接搬到开放式生成上目前没有增益证据——这是单篇、单次运行的结果，但它做的是每个方法对自身基座的对照，比跨方法主表更难被 position bias 或基座差异解释。

### 4.3 失败轨迹与低置信 token 的信号提取

[[Papers/2607-SEED]] 用同一 policy 快照兼任 actor 与 analyzer，把 on-policy 轨迹提炼的自然语言 hindsight skill 转成 token 级蒸馏信号并与 GRPO 联合优化，skill 只在训练时用、部署零开销（ALFWorld 91.8% vs GRPO 75.0%，60% 数据超 GRPO 全量；静态 skill library 消融 −7.4 直接证明"hindsight 必须随 policy 演化"）。[[Papers/2600-UiVoyagerSelfEvolving]] 用 group rollout 找 fork point，让成功轨迹给失败轨迹当局部教师（4B 模型 AndroidWorld 81.0%）。两者共同点：把失败从丢弃样本变为定向监督信号。

这两种做法都预设组内**至少有一条成功轨迹**可当教师。两篇独立工作把边界推到这个预设之外，且是从两个方向撞上同一堵墙的。[[Papers/2608-ZerothOrderSelfEvolve]] 在 deep-research QA 上给出问题的形式化版本：304 个训练例里 baseline Pass@1 只解出 67 个（22.0%），其余 237 个是难例，而在难例上所有采样轨迹拿到同一个失败 reward，GRPO 的相对优势因此恒为 0——这不是信号弱，是信号在这一段完全不存在。它的解法绕开轨迹层：对每题挂一个 instance-specific LoRA，用高斯扰动做零阶梯度估计，目标函数换成 gold answer 上 token-normalized 的 NLL（作者报告在难例上 BERT-based 与 LLM-judge 损失不收敛而该损失收敛）。GAIA 平均 47.5% 对 ReAct 23.3% / ARPO 38.8%，WebWalkerQA 34.8% 对 15.5%；更能承重的是难例上的直接对照——50 个难例里一阶方法解 7 个、RL 解 16 个、零阶搜索解 23 个，以及用搜出的难例轨迹再做 SFT 后 GAIA 28.3% 对原始轨迹的 20.4%。工程上它靠共享 backbone 前向与共享工具调用池把 K=4 的推理时间从 656s 压到 305s，否则 per-instance 扰动搜索的开销不可接受。它的适用域随之被目标函数锁死：需要一个可核对的 gold answer，因此只在 QA 类任务上成立，无参考答案的域拿不到这条退路。

[[Papers/2608-ROPSD]] 在 GUI grounding 的 test-time 设置里遇到同一现象并给出另一种解法。它先复现了失败：纯标量 reward 的 test-time RL（GUI-RCPO）在困难的 MMBench-GUI 数据上负迁移 −0.3，作者归因于难数据上 rollout group 全部失败使组内相对 reward 失效。它的替换不是加 verifier 而是加分辨率：冻结的 Reflector 对每次预测输出二值判定与一段反思文本，policy 自己被这段反思条件化后充当 self-teacher，逐坐标 token 取条件化 teacher 与无条件 policy 的 log-ratio 作为 advantage，于是"哪一步错、错在哪"这类只能用自然语言表达的判断被译成生成序列上的稠密反馈。Contrastive Calibration 处理的是自回归监督特有的污染——前缀一旦错，teacher 在错前缀上的后续概率不再可信，故把 advantage 的分母换成被反向提示（告知"你的预测是对的"）的 student：初始错误 token 处平均 advantage 从 −0.39 加深到 −0.97，而漂移末端从 1.34 衰减到 0.0033。Qwen2.5-VL-3B 六个 grounding benchmark 平均 50.2→57.6，对 GUI-RCPO 最高 +7.7。两个消融是这篇里最硬的部分：去掉反思或去掉 Contrastive Calibration 都导致灾难性 policy collapse，即它与 §4.5 记录的 SpyRL 属同一形态——**优化侧部件缺一个就跌破起点**，而不是各贡献几个点。三条边界须一并记：Reflector 本身用 GroundCUA 的带标注数据训练（约 10,160 对，held-out 准确率 89.5% / 91.7%），所以"无 ground truth"只对适配阶段成立；任务是单步坐标预测而非多步轨迹；增益在更强 backbone 上收窄（Qwen3-VL-2B +3.7 / +4.6）。

把两篇并起来读，可承重的形态是：**自演化在"当前能力解不动"的那一段上失效，其直接原因是结果型信号在该段退化为常数**，而两种绕法都把标注需求转移而非消除——一个转到答案层（gold answer），一个转到评判器的训练数据层（带标注训出的 Reflector）。"边界外自演化"因此目前只在有外部可核对物的域里成立。

第三条路线干脆不要教师。[[Papers/2608-OPSA]] 先测出 on-policy distillation 的监督本身有多脏：教师给出的 token 级 advantage 噪声率 30.6% / 34.7% / 50.6% 且随教师规模单调上升，235B 教师对 97.8% 的正确答案 token 给出负 advantage，同时 29.2% 的 token advantage 恰为零、51.7% 幅值低于 $10^{-4}$ 并集中在高 log-probability 处。判别实验紧接着来：把全部教师 advantage 换成一个施加在学生自己最低 20% log-probability token 上的固定 −0.5，训练结果与标准 OPD 相当，而换成 +0.2 则策略崩溃。据此它把教师整个删掉，用熵自适应的负 advantage 只更新低置信 token，训练只用 DAPO-17k 的**问题**而不用答案——Qwen3-1.7B 的 AIME24 Avg@32 从 13.44 提到 48.85，高出 OPD 16.77 点，每步 46.3 秒对 OPD 61.2 秒、GRPO 186.2 秒。三条边界收窄了它的含义：mask 掉反思词的 fork 位置后增益基本消失并在约 300 步出现长度崩塌，说明它撬动的是模型已有的反思路径而非新增能力；OOD 增益很小（MBPP+ +1.20、GPQA-Diamond +4.48）；全部结果落在 1.7B 非 thinking 模式的数学推理上。

第四条路线不换教师也不换信号来源，而是换掉优化目标的形式。[[Papers/2609-FlowBalance]] 把 policy 更新写成 GFlowNet 式的分布匹配，能量项为 $E=\eta_A A+\beta_G G_H\,\mathrm{sgn}(A)$，其中 $G_H$ 是对整条轨迹的 hindsight 评分、以停梯度特征进入，$\mathrm{sgn}(A)$ 让同一份 hindsight 在成功轨迹上加分、在失败轨迹上反号。Qwen3-8B 五个数学 benchmark 均值 67.61，对 GRPO 65.49 / FlowRL 65.85 / RLSD 64.12 / OPSD 41.16，到 0.5 AIME24 验证准确率快 1.43 倍，rollout 的 Simpson 多样性 0.2194 对 GRPO 0.1017，而 GRPO 在约 180 步后开始退化。但它恰好在本节关心的那一格上没有证据：按其能量式的定义，$A=0$ 时 guidance 项整个关闭，而一组 rollout 全部同分正是 $A=0$ 的来源，论文未讨论这一格（此为本文推断）。$\beta_G\in\{1,2,3\}$ 的扫描给出 67.61 / 66.48 / 65.95 单调递减，却没有 $\beta_G=0$ 这一档，所以符号门控这个核心设计从未被消融掉；作者自陈它不是一个完整的自演化系统。

### 4.4 反馈可验证性谱系

从可验证到不可验证依次是：确定性环境奖励（[[Papers/2604-SpatialEvo]] 几何 ground truth 零噪声）→ 共识伪标签（[[Papers/2606-VisPlay]] majority-voting，无标注 3B 平均 30.61→47.27、与人工标注 GRPO 持平，但同批 200 图逐代 pseudo-label 准确率 72→65→61 递减）→ LLM/VLM-judge（judge 噪声进训练集）。VisPlay 给出 internal 共识信号的双面量化：收益真实但劣化可测，缺 deterministic verifier 的域没有程序化验证退路。

**构造式可验性**（§3.4）是 [[Papers/2607-SpyRL]] 加进这条谱系的第四个位置。其实例把开放式生成改写成"谁是卧底"：多数 civilian 拿完整输入、一个 spy 拿被连续 span masking 退化的输入（只遮住完成任务所需信息、保留风格与长度以防 detector 走表面捷径），各自完成同一任务后互相投票；spy 身份由环境采样，投票对错完全可验，而得票数反过来充当生成阶段的 reward（得票越多 reward 越低，spy 与全体 civilian 的 reward 之和恒为零）。两阶段交替更新，由带滞回的阈值门控切换（detection 准确率 0.9 转向 performing，错误率 0.4 转回）。

它的结果需要按两个域分别读。**开放式生成上它并没有赢**：对 Qwen3.5-27B-RaR 全面胜出（overall 59.3% / 56.2%），但对 GPT-4o-RaR 的 overall 只有 48.9% / 48.2%，且输在 coherence（45.8% / 45.0%）与 consistency（44.5% / 43.7%）这两个"是否说得通"的维度上，只在 novelty 与 emotion 上占优——按 50% 持平线读是**整体落后于强 rubric-judge 基线**，论文的表述是 "remains competitive"。这个模式与自博弈的激励结构自洽：为了不被投出去，模型有动机让输出显得独特、有信息量，而这未必等于更连贯。其价值主张因此应读作成本-性能权衡（论文称两个 RaR 基线分别产生约 \$200 与 \$900 的额外 verifier 开销，SpyRL 无外部 verifier），不是质量突破。**数学域上增益更实但也更需拆**：七 benchmark 均值 41.4→50.4，其中 AIME 25 由 6.7→20.0 落在只有 30 题的集合上（即 2 题→6 题），GPQA-D 26.3→41.3 是纯数学域训练的模型在博士级科学问答上涨 15 点；论文自己在 D.2 用更大样本的 AMC / Olympiad-Bench / SuperGPQA 复测时增益收窄到均值 35.9→42.6——附录比主表更可信。

摘要侧还有一个论文未做的对照：训练压力是"不要显得像信息缺失"，这与"覆盖更多源文内容"高度同向，而 ROUGE-L 恰恰奖励召回；论文既未报告输出长度统计也未做长度控制，因此 ROUGE-L 增益里有多少是质量、多少是覆盖率无法从文中分离（此为本文推断，非论文断言）。全篇无种子数、方差、误差棒或显著性检验，仅 4B/8B 单节点规模。

谱系的另一端由一次同底座的头对头比较收紧。[[Papers/2608-GSAR]] 训练了一个读"目标状态"的学习式 GUI 轨迹判分器，离线判定四个 judge 平均 91.5% 准确率 / 91.8% F1，把 StepCritic（77.6 / 81.8）、DistRL（75.0 / 74.5）、DigiRL（68.3 / 62.8）甩开十几个点。把它接进在线 RL 当 reward 之后，UI-TARS-7B-DPO 在 AndroidWorld 上 26.7% → 30.2%（+3.5），而同一 backbone 换成规则式 verifier 训出来是 32.8%（+6.1）。**判分器的离线准确率不是它作为训练信号的质量**——中间隔着噪声的分布形状，作者对 StepCritic 的归因就是假阳性使奖励过于乐观而非漏判，而假阳性恰恰是 RL 最难消化的那一类噪声。这是单篇、单次运行的对照，但它是目前唯一一次把学习式与规则式两种信号接在同一 backbone、同一算法、同一环境上直接比较，因此它限定的不是 §3.4 那条上界本身，而是上界该用什么量来度。同篇还留下两处未测：自演化合成循环把页面复杂度只推高了一点（边密度 0.0240→0.0295、熵 1.90→2.11、UI 元素 22.68→24.56），而分布坍缩与 reward hacking 全文无评估；增益在已经 GUI 专用化的 UI-TARS-7B-SFT 上收窄，与 §9.2 的能力 gate 同向。

### 4.5 Open Problems

self-improvement reversal（§10.2）与 solver-verifier gap 的收敛条件、防 error accumulation 无解法（VisPlay 逐代信号劣化 72→61）、以及 safety alignment 的累积性衰减（Misevolution 200 步 longitudinal 持续下行，即使自生成数据不含有害内容）是三个开放缺口。

第四个缺口是：**优化侧设计正在从"增益来源"变成"不做就崩"的稳定性前提**。[[Papers/2607-SpyRL]] 的两个消融都是净负——去掉按角色分离的 EMA baseline（RAE）后七 benchmark 均值由 50.4 掉到 37.5，**低于 41.4 的未训练基座**且 GSM8K / Math500 / Minerva / MMLU-Pro / GPQA-D 全部劣于基座；两阶段联合更新（而非交替）把五 benchmark 均值从 42.4 压到 35.3。论文强调其唯一需要按任务指定的组件是信息退化算子 $g(\cdot)$、"requires little task-specific engineering"，但真实的工程负担只是从 reward 设计转移到了优化器设计。同类现象在 §10.2 的三条负性结果线里是"演化到后期会退化"，这里则是"缺一个稳定化部件就直接低于起点"——两者的共同后果是复现门槛远高于方法描述给出的印象。此外该方法的跨任务迁移是单向的：summarization 与 creative writing 互相正迁移，而数学训练出的 checkpoint 在两类写作上全线跌破 50% 持平线（41.7%–45.6% / 38.5%–42.5%），收益严格受限于 performing stage 与目标任务的能力重合度。

第五个缺口来自 §4.3 那两条绕开全失败真空的路线：**它们把标注需求从轨迹层转移到别处，而不是消除它**。[[Papers/2608-ZerothOrderSelfEvolve]] 的连续信号来自 gold answer 的 token-normalized NLL，[[Papers/2608-ROPSD]] 的 token 级优势来自一个在 10,160 条带标注 GroundCUA 数据上训出、测试时冻结的 Reflector。两者都不需要人给轨迹打分，但都需要域里存在一个便宜的可核对物——短答案，或一个提前训好且在目标域仍准（89.5% / 91.7%）的反思器。缺这两样的域（长程 GUI 任务无唯一正确答案、开放式写作无 gold token 序列）目前既无 verifier 也无这两条替代路径，"边界外自演化"因此不是一个已被解决的问题，而是被换了个代价形式。可检验的下一步是把 gold-answer 似然换成任何一个**噪声已知**的连续代理（判分模型的 logit、执行时长、部分匹配率），量出信号-噪声比降到多少时 ZO 搜索退回随机；库内无人做过这个扫描。

第六个缺口由 §4.3 与 §4.4 的几次对照共同提出：**信号的三个属性——可验证性、分辨率、落点——各自有证据而从未被同时控制**。[[Papers/2608-GSAR]] 显示离线判分准确率与训练信号质量不同向，[[Papers/2608-OPSA]] 显示教师传递的判别内容可以近乎为零而收益仍在，[[Papers/2609-FlowBalance]] 的符号门控缺 $\beta_G=0$ 的对照。对应的实验很便宜：固定 backbone、任务与算法，按噪声率、噪声的假阳/假阴构成、施加位置三个维度分别注入受控扰动，量出每一维的收益弹性。做完之后"verifier 质量上界决定收益上界"才从一条定性判断变成一条带系数的关系。

## 5. Memory / Context Evolution

不动参数、演化 runtime context——零训练成本、即插即用、可解释，但 deploy-time reward hacking 风险最高。需要与"零训练成本"分开的是推理成本：同一个记忆方法在不同底座上的每任务开销可以从 vanilla 的 84% 跳到 577%，而开销最高的那一格恰好是该底座上唯一取得正增益的方法（§9.2）。本文把该路线细分为三个位置，其中 operation-level 是本文识别的亚型。

### 5.1 三个演化位置

| 位置 | 演化的是 | 代表 | blast radius |
|:--|:--|:--|:--|
| write-side（内容） | 存什么、如何组织记忆条目 | [[Papers/2409-AgentWorkflowMemory]]、ReasoningBank、[[Papers/2603-HybridSelfEvolvingStructured]]、[[Papers/2600-UiMemSelfEvolving]] | 单条经验 |
| read-side / selection | 检索/取用哪条记忆 | [[Papers/2601-MemRL]]、[[Papers/2608-RoMeRL]]、[[Papers/2605-SEGA]] | 单次检索 |
| operation-level（操作） | 写记忆的 procedure 本身 | [[Papers/2602-MemSkill]]、[[Papers/2608-PRACTICE]] | 所有后续记忆写入 |

三个位置对应记忆 pipeline 的不同环节，blast radius 逐级放大：operation-level 演化改的是"如何构建记忆"的规则，一次错误影响所有下游记忆写入，是 misevolution 放大面最大的记忆亚型。

### 5.2 write-side（内容演化）

[[Papers/2409-AgentWorkflowMemory]] 从轨迹诱导可复用 workflow（WebArena 相对 +51.1%，且分布差距越大领先越多），[[Papers/2603-HybridSelfEvolvingStructured]] 用图结构自演化记忆（Qwen2.5-VL-7B +22.5%）。[[Papers/2600-UiMemSelfEvolving]] 把成功 workflow / subtask skill / failure pattern 组织成分层经验模板，在 mobile-GUI online RL 的 rollout 期以不同强度注入 memory-guided 探索与 reward shaping，边演化记忆边把外部经验内化进 policy——是 memory 演化与 model 演化耦合的边界案例（记忆内容变化最终反哺参数更新）。共同点是演化"记忆内容"，检索与写入策略固定。

### 5.3 read-side / selection

[[Papers/2601-MemRL]] 用 runtime RL 学习"取用哪条 episodic memory"，把演化从写入侧移到选择侧（Q-value 驱动的记忆选择）；其 Appendix G.4 第一方自认存在 reward-hacking，是 selection-based 演化同样受 internal 信号偏差约束的直接证据。

[[Papers/2608-RoMeRL]] 把这条自认从个案抬成机制并给它命名：**memory-reward trap（MRT）**。trajectory 级 reward 被共同检索的一整束记忆瓜分，因此每条记忆拿到的是 bundle-level 观测回报而非有无它的介入差；论文把二者之差拆成 task-level baseline 与 observational attribution bias，并指出多检索几次只压缩方差项、不消除 bias（标准 bias–variance 分解）。推论是 selection 侧演化的默认动作——用 UCB 加大探索去救 utility cold start——会**同时**扩大误归因面：探索越宽，越多弱相关记忆被塞进成功上下文并因此获得与贡献不匹配的正向更新。

关键在于这不只是断言。论文设计了一个受控污染探针：第一轮把 10% 记忆条目 null 化（保留标题以维持可检索性、抹掉 action/reflection 字段以移除实际效用），跑十轮后统计噪声条目累计吃到的正向更新数与终轮噪声占比——MemRL 3.7 次 / 1.02%，MemRL+UCB **7.2 次 / 1.20%**，RoMeRL 2.4 次 / 0.15%。"探索让污染翻倍"这一条是稳的；同表里"探索降低性能"只有 79.2→78.4 这 0.8pp 之差，在单次运行下不足以支撑，两件强度差很远的事不应一起当作 MRT 的证据。

其解法不是在增长的空间里更用力地探索，而是换掉 RL 所作用的状态本身：每个任务的 utility 空间从"每条轨迹一个变量"压成固定 2×2 的四个语义坐标（outcome polarity × memory dynamics，即 PCC 最高效的成功 / PAC 失败后首次成功 / NCC 高 Q 的失败 / NAC 最近一次失败），活跃支撑上界为 4，新表示进入坐标时继承当前 utility 作 warm start。检索式（相似度与 Q 的加权和）与更新式（EMA 结果 reward）在函数形式与超参上都与 MemRL 一致——**被替换的是候选集，即哪些记忆有资格作为持久 utility 变量存在，而不是 RL 算法本身**。ALFWorld + LifelongAgentBench overall SR 0.862 vs MemRL 0.830（+3.2pp），记忆池 45K→7K、LLM 调用 570K→450K，backbone 全程冻结；冻结的记忆状态换 backbone 后四种组合全部改善（LAB-OS 67.0→81.6 / 74.0→81.4，DB 93.0→96.8 / 96.2→97.6）。

三条边界必须一起记。其一，**RL 的贡献完全没被隔离**：四个坐标里只有 NCC 的选择规则用到学到的 Q，其余三条是纯启发式；论文没做 $\omega_Q=0$ 的消融，也无 $\omega_Q$ 敏感性分析，因此"降维结构"与"在其上做 RL"的贡献无法区分。其二，**headline 效率数字含近乎恒等式的成分**：feedback density 4.96→29.93（6.0×）与记忆池 45K→7K（6.4×）几乎同比，而论文自己的 Theorem 3 就是"固定预算 T 摊到 d 个坐标 = T/d"——缩维必然提高人均反馈，真正需要证明的是缩维不损失信息，而这只能由任务 SR 承担，SR 只给出 +3.2pp。其三，**增益高度集中且无方差**：+3.2pp 里约 62% 来自 ALFWorld 的 P&P（0.908→0.968）与 Examine（0.855→0.957）两列，heat 一列反而略低（0.862 vs 0.865），全文无 seed 重复、无标准差、无显著性检验。此外坐标是 per-task 的，而 LAB/ALFWorld 的协议是对同一任务集跑 10 epochs——一旦任务不重复出现（真正的 open-ended 部署），每个任务只有 ≤4 个坑且大多为空，reduced-order 相对全池的优势基础就消失了，论文的 limitations 承认未评估 open-ended 但没有把这条结构性依赖讲出来。

检索池的构成也被一次消融量化。[[Papers/2605-SEGA]] 在 AC-High 上比较三种检索策略：Top-k 75.8、成功与失败混合 76.2、只检索成功轨迹 70.0；GUIOdyssey 上是 83.9 / 82.1 / 72.5。把失败轨迹从检索池里去掉在两个评测面上都是最差的一档，与 §4.3 把失败当定向监督信号是同一方向的证据，只是发生在不改参数的检索侧。同篇另有两处需要一并读：去掉三层记忆后 AC-High 从 73.8 掉到 61.4，但该变体同时拿掉了记忆内容与为容纳它而开的 6144 token 预算，没有等长对照，因此这 12.4 点里有多少是记忆价值、有多少是 prompt 分布失配无从判断；全文无 seed 与方差，且这组消融的基准 73.8 与主表的 75.8 在原文并存。

### 5.4 operation-level（操作级演化，新亚型）

[[Papers/2602-MemSkill]] 把"如何从轨迹提取/修订记忆"这套操作本身从固定原语（Insert/Update/Delete/Skip）抬升为可学习、可演化的 memory skills：PPO 训练的轻量 controller（三个独立 MLP + Gumbel-Top-K）按 span 选 Top-K skill，固定 LLM executor 按 skill 规范产出结构化更新，LLM designer 每 100 步分析 hard case 增改 skill bank（每轮 ≤3 edits），并用 best-snapshot rollback + stabilized reward + early stopping 做防退化 gate。LoCoMo L-J 53.82、LongMemEval 纯迁移 60.89、ALFWorld-Unseen SR 83.58%，且 LLM 调用量比 baseline 低一个量级（215 vs 1288/1548）。ablation 中 designer 贡献大于 controller，坐实"演化操作本身"确有增益。局限：gate 只在 skill-bank 层且只看 aggregate task reward，单条记忆无 per-item 验证，designer 直接改写记忆构建 procedure 使 blast radius 系统性放大。

[[Papers/2608-PRACTICE]] 是这一亚型的第二个实例，也是第一个把"写记忆的 procedure"交给一个被**训练**出来的模型而非被提示的模型：一个 8B learner 输出 ADD / REVISE / MERGE / REMOVE 四种结构化编辑与分层合并，executor 全程冻结，监督分三段——先用 8 个异构 executor 在同一批任务上的分组数据做 SFT，再用冻结的 32B 教师做 on-policy distillation。EmbodiedBench 的 EB-ALFRED 上 49.7%，高出最强经验增强基线 9.7 个点，演化出的库最终只有 29 张 card。它的阶段消融是本节最有信息量的一处：24.3 → 40.7 → 42.3 → 45.3 → 49.7，其中从 24.3 到 40.7 的 16.4 个点来自一个**完全不学习**的初始库（用 BPE 式频繁相邻 action 子序列合并构造），三个学习阶段合计 9.0 点。学到的更新策略确实在贡献，但它贡献的是这条链上较小的一半——这与 §4.3 的 OPSA 在另一条路线上得到的形态相同：一个精心训练出来的监督源，其收益可能小于一个不学习的结构先验。三条边界：failure-aware 相对 success-only 高 2.6 个点（45.3 对 42.7），与 §5.3、§4.3 同向；跨 executor 迁移 +2.4 / +30.3 / +15.3 / +25.4，但在 EB-Habitat 的 Base 与 Long 两档落后于最强基线；Appendix C.2 把同一结果写成 40.0% 而 Table 1/3/7 是 49.7%，论文未解释这处不一致。

### 5.5 prompt 优化谱系

APE → OPRO → ProTeGi/TextGrad（文本梯度）→ PromptBreeder/EvoPrompt（种群演化）→ SPO/ACE（自监督闭环）、DSPy/MIPRO（程序化联合调优）。严格按 §2.1 判据多数是 offline optimisation 而非部署后持续演化。

这条线在 2026 年的活动集中在**多 agent 流水线里该改谁**：N 个 agent 串在一条链上共享一个终点 reward，文本梯度沿链回传时遇到的正是 §7.3 的 credit assignment 问题。[[Papers/2609-AgentGrad]] 的做法是不回传而是干预——从最后一个 agent 逆序，逐个把它的输出替换成一个由 ground truth 或输出约束构造的 hint，第一个能把整条流水线的 reward 拉到上界的位置即被判为责任所在，干预后的输出直接充当该 agent 的 pseudo-label，因此整套方法不需要显式 loss。GPT-5-mini 上五个 benchmark 平均增益 +11.76，对 GEPA +9.24 / TextGrad +6.33 / MIPROv2 +5.66；Qwen3-8B 上 +9.67 对 +7.62 / +6.27 / +6.06；平均 wall-clock 136 分钟，对次快的 GEPA（337 分钟）快 2.5 倍。

四处必须与这些数字一并记。其一，摘要的"两个 backbone 五个 benchmark 全面 SOTA"与它自己的表不一致——Qwen3-8B 的 IFBench 一格 TextGrad 42.52 高于 AgentGrad 41.42，且该格的加粗给了 TextGrad，实际是 10 格中 9 格最优。其二，逆序干预的前提是"失败集中在靠后的 agent"，这条前提全文没有任何测量，它决定的是搜索顺序而非搜索空间，因此影响的是成本而非正确性。其三，同一张表里 GPT-5-mini 下 TextGrad 的 IFBench 与 MATH 两格数字连标准误都与不做 prompt 优化的基线逐位相同，即那两次运行一次更新也没被接受，论文对此未作说明——**汇总表把一个在部分格子上真实产出为零的优化器呈现为一个正的平均增益**，这与 §10.2 的负性结果线是同一形态。其四，加速数字与方法的主要开销脱钩：逆序干预对每个失败样本最多要跑 $N$ 次系统执行，而这些调用是否计入预算 $B$ 全文未说明，因此 136 分钟这个数是否与基线同尺无从判断；标称的 2.5× 是两列均值之比（336.8/136.4），五个逐 benchmark 比值取平均只有 2.24，且其中 PUPA 与 MATH 的次快方法并非 GEPA。论文 13 页、无附录、无 Limitations，预算 $B$ 的数值与各 benchmark 的 agent 数均未给出。

### 5.6 Open Problems

[[Papers/2509-Misevolution]] 证明 memory 积累引发 deployment-time reward hacking（>60% 案例中 SOTA 模型采纳最大化历史评分但损害用户利益的动作，无 memory 对照 Unsafe Rate=0）且可由单次高评分**突然崩塌**而非渐变。对抗侧，[[Papers/2512-MemoryGraft]] 展示投毒记忆可持久危害 agent（详见 §10.4）。read/operation 两个新位置的安全性尚无系统评估。

[[Papers/2608-RoMeRL]] 的 MRT 把 read-side 的失效条件从"信号有偏"细化为一个可测量的归因缺陷（§5.3），并留下两个开口。一是**探索-污染两难本身没有被解决，只是被绕开**：把状态降到 4 个坐标确实缩小了暴露给误归因的支撑，但代价是牺牲了对长尾记忆的覆盖，而"哪些记忆值得进坐标"由三条手工启发式决定——为什么是成功/失败二值极性而非三值？为什么 PCC 按效率而非鲁棒性选？论文的 Theorem 3 对任意 $d$ 成立，理论并不偏好 4，而全文没有 $d$ 的扫描实验。二是**per-item 验证在 read-side 依然缺席**：MemSkill 的 gate 只在 skill-bank 层看 aggregate reward（§5.4），RoMeRL 的坐标替换规则同样不对单条记忆做因果验证，它只是让错误条目的驻留时间有界。其 Proposition 1 给出的稳态错误占用上界依赖两个转移量 $\gamma$、$\lambda$，论文自陈估计它们需要 paired counterfactual rollout 的坐标级因果标签，全文未估——所以"污染更少"在本文数据上由 Table 2 的实测承担，而非由该命题承担。

方法之外，那套 null 化注入协议本身值得单独记住：它把"记忆污染"从定性讨论变成两个便宜、可移植的数字（噪声条目累计正向更新数 + 终轮噪声占比），可以拿去测其他 memory 方法，也可与 [[Papers/2512-MemoryGraft]] 的投毒攻击面并置——前者是无意污染、后者是有意注入，指标是同一套。

一个现成的适用对象是 [[Papers/2608-EvoHarnessRL]] 的经验库：条目由 agent 在训练中自己写下的 note 构成，增删改由一个外部 Claude Opus consolidation model 在每个 epoch 边界执行、辅以 LFU 淘汰，全程没有 held-out 准入判据，而 policy 会在后续 episode 里通过 `recall` 反复读回这些条目。这正是 null 化探针要测的结构——错误条目能驻留多久、拿到多少次正向强化——论文自己的附录 case study 里也确实出现了一条被写入库的错误先验，但它以个案形式呈现，没有污染率。该库因此是"可测而未测"的一格。

还有一个自由度从未被写进报告口径：**记忆的复用单位**。[[Papers/2609-RSIAgent]] 在 OSWorld 2.0 上把 partial score 从 71.97 提到 78.98，机制是先在目标任务上探索、把有效操作序列写进持久记忆再正式作答，但它记录的三条轨迹全部从空记忆起步，记忆按目标任务建立而非跨任务共享。探索成本因此按任务计价、不被后续任务摊销，收益也就不能读成"经验在环境上积累"。§5.1 的三个位置都默认记忆跨任务复用，一旦复用单位塌到单任务，read-side 的检索问题消失、write-side 的污染窗口只有一个任务长、operation-level 的 blast radius 也随之缩小——三种记忆亚型的风险量级都依赖这个未被声明的参数。该文的基线同时关掉探索与持久记忆且无预算配平（其附录自陈不是 matched-budget 估计），所以 7.01 点的差额里记忆与额外算力没有分开。

## 6. Tool / Skill Evolution

演化对象是工具库或技能库——收益可直接部署，且对"演化步验证"的自觉最早最深。

### 6.1 创造 → 精通 → 优化即训练 → 维护

创造：Voyager（Minecraft 技能库开山）→ CREATOR / LATM → Alita（自主 MCP 封装）；[[Papers/2605-HASP]] 把 skill 从文本建议升格为可执行的 typed Program Functions，在 failure-prone states 主动改 action / 注入 context，且每个候选 PF 须过语法/接口/mock-execution 验证方可入库（验证前置到入库这一环节，本身即一种 edit-level gate）。精通：SkillWeaver、DRAFT、LearnAct。优化即训练：[[Papers/2605-SkillOpt]]（skill 文档当可训练对象：bounded edits + validation gate + lr schedule，6 benchmark 平均 +23.5）、[[Papers/2604-SkillClaw]]（多用户轨迹集体演化 skill，day-night loop + A/B gate）。失败驱动：[[Papers/2606-LearningFromFailure]] 把丢弃的失败轨迹交 LLM 诊断出 inference-time code patch，OpenCUA-72B 在 OSWorld 100-step 零训练从 42.3% 提到 48.9%（运行时 +8%、交互步数 −15%）；[[Papers/2607-KnowActGUIClaw]] 同走"诊断失败→生成 inference-time patch"，并在 skill 执行前逐步过 deterministic state-contract 校验、修复优先于新建。

维护是这条链上第四个、也是最晚出现的环节：**技能被反复演化之后自身会变长，而没有任何一个演化算子负责把它变短**。[[Papers/2608-SkillZip]] 给出了这个成本的量级——同一批 skill 文档经 [[Papers/2605-SkillOpt]] 演化五轮后长度膨胀 5.6× / 3.1× / 6.7×（三个 benchmark，均值约 5.2×），十六轮时若不加干预为 2.5–3.7×。膨胀直接换算成每次调用的 prompt token，而演化过程本身不给出任何压缩压力：edit 算子只增不减，validation gate 只问性能不问长度。

其解法是把压缩与评测解耦。既有做法（论文中的 SkillReducer 一类）是"删一段、跑 40–80 次 validation rollout、看分数掉不掉"，代价高且有一个结构性缺陷：**判据绑在压缩时的评测集上，任何当时没被测到的守卫分支都会被判为冗余而删掉**。SkillZip 改为对 skill 文档做 typed MDL 编码，最小化 $L(K)+L(R|K)$ 并附加硬覆盖约束——每条规则必须仍被至少一个已见调用模式覆盖。由此得到 Prop IV.1 / Cor IV.2：稀有规则的保留与它在压缩时的任务频率无关，只要它在结构上仍可被解析器还原。压缩算子 Zip-on-Write 有四个操作（ABSORB / REFINE / EXTEND / REFACTOR），候选集规模 $O(dk)$，产物写入 sidecar `skillzip.json`。整个流程不接触任务、rollout、reward 与 verifier——它是本节唯一一个**不消耗评测预算的技能库演化算子**（0 rollouts、286 s，相对 SkillReducer 3.5× 加速）。

数字上：平均压缩 31.2%（27.1 / 29.7 / 36.9%），对照 SkillReducer 的 9.2%；macro 分 0.577 对未压缩的 0.570、对 SkillReducer 的 0.544。跨模型迁移上（LiveMath），SkillZip 压缩后的技能保留率 0.97、SkillReducer 压缩后 0.91，且差距集中在 off-diagonal（技能被移到非产出它的底座上时），与 §6.3 中外挂路线"可迁移性是其独有性质"的记录同向。Zip-on-Write 若从第一轮起开启，十六轮膨胀由 2.5–3.7× 压到 1.6–1.9×（降幅 38–50%）且无精度损失；从第八轮才开启则只能部分挽回（2.6× 对 1.9×），说明膨胀有路径依赖，晚接入的压缩算子无法完全撤销已固化的冗余结构。

三条边界要一并记。其一，**保留保证是相对解析器的**：Cor IV.2 保证的是"在该 typed 语法下可被覆盖的规则不被删"，一条从未被写成显式规则的隐性约定不在保护范围内。其二，四个操作与硬覆盖约束**没有分项消融**，31.2% 里各部分的贡献无法拆分，也无公开代码。其三，也是最需要按 §9.4 的标准读的一条：**"压缩无损"是一个等价性主张，而它的证据是 0.577 对 0.570 的单点比较，全文无 seed、无方差、无等价性检验**。库内已有的方差量级足以让这个差值失去判别力——[[Papers/2608-AgentStream]] 在同类 agentic benchmark 上测到的单元格 seed 间标准差常在 3–6 个百分点，而这里的差值是 0.7 个百分点。可以确证的是压缩率与速度（31.2% 对 9.2%、286 s 对数十次 rollout，量级差距远超噪声）；不能确证的是"压掉三成而分数不降"——这套协议既无法区分无损与小损，也无法排除 0.007 的正向差本身即噪声。

续作 [[Papers/2608-SkillZipPro]] 把压缩对象从单个文档换成生产环境实际部署的渐进加载目录（root + references + subskills + scripts + schemas），并给出这条线最该被采纳的一条记账纪律：**单一压缩率是误导性指标**。目录形态下至少有四层成本——选择前可见的 catalog、激活后必载的 root、执行路径上被打开的文件、落盘总量——只压 root 能报出漂亮的比率却不动大部分部署文本，把罕见分支上提进 root 甚至让每次调用都更贵。四层分开记账后，平铺拼接的做法在真实技能库上只保留 0.2% 的指令行，只压 root 的做法把 routing 保留率压到 0.000（分支文件还在盘上但再也选不中），而它自己保 1.000。删除侧的纪律是 witness 分级：每次删除必须恰好携带一个证据——字面包含（可逆）、确定性覆盖检查、或温度为 0 的冻结 checker 判定蕴含——无 witness 的删除无论预计节省多大一律拒绝。这套分级在一个中文内容审核 skill 上把可压比例从 13.8% 推到 38.1%，准确率 89.00 对未压缩的 92.00/91.00；同一份 skill 换成无保护压缩压掉 71.4%/75.8% 时，准确率从 88% 掉到 70%/62%，误报从 10 条涨到 29–35 条，损失集中在"何时不该 flag"的豁免规则上——**被压掉的从来不是平均意义上的冗余，而是罕见分支上的守卫条款**，这与前作 Cor IV.2 想保护的正是同一类内容。

它在证据形态上补上了前作缺的那一块：质量不降这个等价性主张由 102 个 held-out 任务上的配对 bootstrap（10,000 次重采样）承担，−0.05 的等价边界在实验前固定，结果 +0.010、95% CI [−0.029, +0.059]（§9.4）。开启时机的单调性也在真实库上复现：第一轮起压缩省下全流 carried token 的 40.8%，第十三轮才开只剩 18.5%；每轮新增内容与既有文本的重复率稳定在 55%±3%，可移除份额随库龄从 29%（第 2 轮）爬到 53%（第 15 轮）——压缩算子对演化中的技能库是报酬递增而非递减。两处不能顺延：SkillReducer 这条基线为匹配零 rollout 预算被禁用了它自己的 evaluation-based candidate selection，因此前作 31.2% 对 9.2% 的对比线在这里不可直接续读；跨 executor 迁移三个底座两升一降（kimi-k2.6 0.611→0.574，无关加载占比 0.077→0.287），结构可移植而加载效率依赖 executor 如何解释 routing。

这条链上第五个环节是**评估预算怎么花**。skill 演化真正贵的不是写出候选而是执行候选——候选效用只有跑过才知道，而大部分候选最终被证明没用。[[Papers/2609-COBRASkills]] 把这一步形式化成候选集逐轮变化的序贯决策：每个候选用固定 embedding 表示，一个两层 MLP 预测它的 reward、LinearUCB 项给出探索奖励，每轮只把评估预算给优先级最高的那一个；teaching model 不再每轮重读轨迹，只在周期性的种群更新时被调用，用 regeneration / rollout mutation / crossover 三个算子替换掉最低优先级的候选。6 个 benchmark × 3 个 target model 上平均分全部最高（相对无技能基线 +13.1 / +26.9 / +22.5），总优化成本相对 [[Papers/2605-SkillOpt]] 降 55%–58%，每提升一分的成本降 60%–69%，且按 3 次独立运行报 mean ± SE。成本优势的来源被它自己拆开了：teaching token 少用 67%–80%，而 target token 在两个底座上反而更高——省下的是教师的钱，不是执行的钱。消融里三项各值 2 点上下（去 bandit −2.2、去演化算子 −2.4、换成 Best-of-30 −2.5），量级接近说明预算分配与候选生成是可互换的两种花法，而非一主一辅。两处边界：18 个 benchmark×model 格子里有 6 格存在比它更强的方法（Qwen 的 SearchQA 上 SkillOpt 86.3 对 84.3）；把教师换成 target 自己后平均分只从 73.5 掉到 72.5、成本减半，但 ALFWorld 单项从 72.3 掉到 63.3——自教学在需要长程流程知识的任务上不成立。

目标函数也不止"更强"一种。[[Papers/2608-TRACE]] 把 skill 演化的目标换成一致性：同一请求重复 $k$ 次是否每次都对（Pass^k），而非至少对过一次（Pass@k）。机制是轨迹对比——Curator 按轨迹调用过的 skill 分组，读同组的成功与失败轨迹直接改写 skill body，并在渲染轨迹时逐条标注哪些信息部署时可见、哪些只有 Curator 在演化时可见，以防把 skill 写成依赖部署期拿不到的知识；部署侧每一轮重新编排一次 skill 集合，上一轮注入的内容不保留。CAR-bench（58 个互联工具、19 条 domain policy）上 GPT-5.5 的 Pass^3 从 59.9 升到 94.5，Pass@3 与 Pass^3 的差从 27.8 点收到 4.0 点，收益集中在原本最弱的 Disambiguation 一类（39.3→94.6）。

两组数字必须分开读。主表的评测集与演化所用任务重合——skill bank 先在 training split 上起步、再用 test split 扩覆盖——因此 94.5 是训练集内的数字；官方 hidden set（30 个未见任务 × 3 次）上 Pass^3 是 50.0→70.0、Pass@3 是 66.7→83.3，一致性差只收窄 3.4 点，而训练集内收窄 23.8 点。开销侧记得诚实：中位延迟 +22.0%、token +72.4%、每次调用成本 +58.8%。它同时是零关口一端的第二个样本（§6.2）：产物只是 markdown 文件、不改权重，接受与否由 Curator 自行决定，全文无任何组件消融、无演化轮数敏感性，也不报 false-refusal 率——一个把"承认做不到"当作正确行为的系统，其过度拒答率恰恰是最该报的那个数。

整条链的产出率第一次被系统审计，结果比 before-after 曲线难看得多。[[Papers/2607-RethinkSkillEvolve]] 固定 executor、optimizer、revision 流程、validation 规则与 10 轮预算，只变 optimizer 可见的轨迹视图，在 3 个模型 × 5 个 benchmark 上跑 42 次演化，并用 SHA-256 给每个 skill artifact 定身份：一次"新最优"必须同时满足 validation 严格提升与字节不同，byte-identical 重跑带来的分数波动一律判为执行噪声。这条纪律之下，388 个 candidate 只有 55 个建立了 byte-distinct 的 validation 最优；跨 8 个模型的 SearchQA 分析里 210 个 candidate 中 191 个确实改动了 incoming skill，只有 29 个改出了新最优。端到端看，14 个 setting 中 11 个最终选中演化后的 skill，其中 9 个在 released test 上更好，而要求同时改善 robustness 与 transfer 则降到 7/14。**技能演化是被 validation 过滤出来的稀疏搜索，不是逐轮稳步改进**——"改过"与"改好"之间差一个数量级，而前者才是演化循环的默认产出。

这项审计同时给出了本节所有单点比较的判别下限。同一份字节完全相同的 skill 在 49 题 validation split 上重复评测 8 次，hard score 从 71.43% 到 83.67%，标准差 3.92 点；在同口径的 100 题配对面板上重复部署三次，SearchQA 的 +2.3 变成 −2.0 / −3.0 / 0.0，LiveMath 的 −6.6 变成 +6.0 / +7.0 / +5.0，两个方向的符号都翻了，而 parent 对 parent 的纯噪声基线是 −2.0 / −2.0 / +2.0。**在这套评测里 ±3 点以内的差异不可判**，本节此前引用的若干单点比较（含 0.577 对 0.570 那处）都落在带宽以内。这个下限不能跨 split 搬运——3.92 来自 49 题，±3 判据来自 100 题面板，更大的 test split 噪声更小——但它确立的方法学要求与 split 大小无关：**报差值必须同时报该评测的重复部署带宽**。

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
| [[Papers/2608-Zetta]] | 技能入库级（具身） | cluster 内 100% 历史回归全通过 + held-out ΔSR 双闸门，outcome 侧直接查环境官方谓词 | RoboCasa 73.56→93.56、LIBERO-Pro 32.00→71.13；ΔSR 无数值接受阈值，全文无组件消融 |
| [[Papers/2609-Ecdysis]] | harness 轮级 | 候选仅在训练集**总分**严格提升时接受，否则回滚上一版 | 5 模型 × 2 子集平均 59.33 对逐条改的 46.67；总分准则不约束逐任务回归 |

这两行分处闸门强度谱的两端，而它们的强弱差异恰好落在同一个维度上：**判据约束的是逐任务回归还是聚合分数**。Zetta 要求候选把它所源自的 failure cluster 里的历史失败全部修好（100%，不是"多数"）再加一个 held-out 增量，逐任务回归因此被直接禁止；Ecdysis 只要求训练集总分严格提升，一个把三个任务修好、两个任务弄坏的候选照样入库；相对 [[Papers/2607-HarnessBank]] 的 validity / activation / significance 三道确定性判据，它是更弱的一种准入准则，而两者的干预点（证据粒度与接受判据）正交、原则上可叠。§10.2 记录的负性结果多数发生在聚合判据一侧不是巧合——聚合分数是唯一允许"净改善"掩盖单任务破坏的判据形态。

与之对照，[[Papers/2511-LiveSWEAgent]] 与 [[Papers/2608-TRACE]] 走**零 gate** 路线（前者在 SWE-bench 上运行时无关口自改，后者由 Curator 自行决定改写并直接发布新 skill bank），是 gate 谱的另一端点。仍开放：现有实证 gate 全部只覆盖任务性能回归维度、依赖任务可复现结构（GRASP 在开放动作空间失效、SKILL.nb 安全性 replay-relative），task-agnostic 的安全侧 gate 依旧空白。

**gate 与部署选择器是两个组件，而多数报告 gate 收益的工作把后者的功劳记在前者账上。** [[Papers/2607-HarnessBank]] 在冻结 Qwen3.6-27B 上做 harness 自演化：可变表面（prompt / knowledge / runtime / config）之外保留不可变 kernel，候选按 (where, why) 双坐标存入 MAP-Elites 式档案（where 是被改的组件，why 是被针对的失败机制），先在训练子集上过三道 gate 才拿到全训练集复评资格。七个域的 test Pass@1 提升 5.1%–15.4%，六个过它自设的配对 2σ 判据。但它自己的消融是一处自证否定：在 TB2 上去掉 2σ 判据，test Pass@1 变化是 ±0.0，论文的解释是部署根本不由 gate 决定——训练集上的 argmax 无论有没有 gate 都会选中同一个赢家。gate 在因果链上的位置因此是预算分配器与档案守门员，而不是部署决策者，其可测收益全部兑现在地板与效率轴：假精英 0 而非 2（其中一个是 activation beacon 从未触发的惰性变体），收敛在 10 轮而非跑到轮数上限。终止侧的机制也被量化——在收敛后候选中性的那些轮次里，改用 single-run 或 K=3 均值判据会有 62%–76% 的轮次出现幻觉进展，循环因此停不下来。

这与 [[Papers/2606-SkillNb]] 同向而非相反：后者去 gate 只掉约 6 分成功率，修复后回归却从 3.3% 爆到 18.6%，价值同样落在地板。两处 source-checked 的自身消融因此指向同一形态——**已被测量到的 gate 价值是防回归与档案卫生，不是抬高天花板**。与之相反的唯一实测来自 [[Papers/2605-GRASP]] 的去闸门 88.8%→63.5%，其结构差异也很明确：GRASP 的闸门就是唯一的准入决策，接受即进技能库并直接决定部署，没有独立于它的下游 argmax 兜底。可检验的条件因此是：**gate 之外若存在一个在同一训练侧数据上重新排序的部署选择器，gate 的天花板贡献被挤到零；gate 本身即部署决策时，它承重**。GRASP 一侧的记录缺证据台账与核验状态，尚不足以把该条件确立为共识，故正反两侧一并记录，这条判断按争议而非共识引用。

需要与"gate 无用"分开的是跨方法证据：同 split、同 2σ 尺子、rollout 预算相差 2.1× 以内的比较里，无 gate 的 DGM 在 Omni-MATH 交付了一个比 vanilla 还差 1.1% 的 harness，在 LiveCode 上挑中一个 15 任务 $K=1$ 的尖峰（0.733，复评回落 0.533）。**无闸门的循环会交付回归**这一点成立，但它由跨方法对照给出而非由 HarnessBank 自身消融给出——去掉 gate 后它并没有产生回归，只是停不下来。该比分（五个 sealed test 里 HarnessBank credit 4、DGM 1、只改 prompt 的 GEPA 0）另有一处混淆：HarnessBank 的 evolver 是 Claude Opus 4.8，两个基线用同一个 Qwen3.6-27B 兼任 task agent 与 proposer，rollout 预算只对齐了执行侧，提议者能力未被对齐。同篇也缺算力配平对照——无 gate 变体跑了更多轮次仍是 ±0.0，这个不匹配方向对论文有利，却也因此无法反过来支持"gate 的判决产生了增益"。

**gate 的"独立性"应分三层记，而不是一个二值标签。** [[Papers/2607-HarnessBank]] 是目前最外生的实例，也恰好在三层上给出不同答案：判决算法层外生——接受与否是一个确定性统计量，由既非 task agent 也非 evolver 的独立 evaluator 计算，且 evolver 与 task agent 不同家族；证据来源层自报——activation gate 的判据是 patch 自己声明的 activation specification 与它触发时发出的 beacon，没有任何机制审计这个声明是否名副其实，一个 patch 完全可以在不做实事的路径上发 beacon；打分器层未审计——论文称结论在 deterministic 与 judge-based verifier 下都成立，却从未指明 judge 是哪个模型。所以"确定性 gate"的正确读法是判决算法确定，而非整条证据链外生。这三层与 §10.2 的 rubber-stamp 约束正交：CodeSelfReviewCollapse 打的是判决算法层的同源性，HarnessBank 在这一层做到了外生，代价是把风险平移到另外两层。该篇也未报告 gate 的误收/误拒**率**，只有个案：SWE-bench 的 +5.1% 在 $n=26$ 下 $z=0.78$ 被自己的判据挡掉并标为 preliminary，GDPval 上训练侧排名次优的变体在测试上反而最高（+11.5% vs +9.2%）。

这三层拆开后，[[Papers/2608-EvoHarnessRL]] 提供了第二个样本，它的形态恰好与 HarnessBank 互补：判决**者**外生而判决**据**缺失。它的技能库在每个 epoch 边界由一个外部 Claude Opus consolidation model 执行增/改/删，辅以 LFU 淘汰——判决者与被演化的 Qwen3-8B policy 既非同一模型也非同一家族，在判决算法层上是外生的。但判据是这个 LLM 阅读 agent 自己写下的 note 文本再加使用频次，既没有 held-out 任务上的回归检查，也没有任何"改动前后配对比较"的统计量；论文附录的 case study 里就有一条错误先验被写进库并留存。换句话说 HarnessBank 的判决是"外生模型算一个确定性统计量"，EvoHarnessRL 的判决是"外生模型读自报证据下一个主观判断"——判决者的独立性并不自动传递给判据。两个样本合看，gate 独立性的三层里目前**没有任何一篇同时做到三层外生**，而"用了异族模型当裁判"这一句在论文里常被当作独立性的充分说明。

[[Papers/2609-GeneralizedAgentIteration]] 给这三层配了一条该被采纳的术语切分：判据的**位置**与判据的**忠实度**是两件独立的事。在它的坐标里，外部 judge 无论训得多不忠实都算 anchored，因为那个 dial 问的是标准放在系统内还是系统外；而一个很忠实的 judge 一旦成为被演化对象的组件就变成 goal drift。这把"外生"二字的含义钉在位置上——HarnessBank 的判决算法外生是位置性质，它对 activation beacon 是否名副其实一无所知是忠实度问题，两者不互相兑换。同篇的最小例子把后果讲得比任何实证都直接：一个按测试通过率给自己的改动打分的 coding agent，在测试被 held out、测试放进它自己的 repo、测试被换成它自己对"何为改进"的判断这三种放置下都满足同一组自洽条件，而只有第一种在服务原目标——**自洽的自我报告不携带任何关于是否真的变好的信息**。该文无实验、无定理，作者自陈从 RSI 到 GPI 的归约是散文而非带显式假设的命题，因此它提供的是坐标而不是证据。

需要与 gate 分开的还有 §6.1 的压缩算子：[[Papers/2608-SkillZip]] 完全不进入这张表，因为它不做接受/拒绝判决，只在既有条目上做保守改写。这是 gate 之外的第二类库维护机制——gate 管"什么能进来"，压缩管"进来之后占多少地方"，两者的预算特征相反（gate 必须花 rollout，压缩恰恰以零 rollout 为设计目标）。

**gate 谓词自身的 precision** 在整个 gate 家族里只有一处数字，来自 [[Papers/2607-MANTA]]。需要先分清它测的是哪种谓词：MANTA 的 Trace Auditor 是**触发闸门**（判断当前结构是否已失效、要不要修复），不是验收闸门（判断演化产物能否入库），因此这个数字不能直接搬给 GRASP/SKILL.nb 那一列。在 450 run 上，以"答案错误"为正类，初始 audit 的总体 precision 0.38 / recall 0.64 / F1 0.47，分域从 WorkBench 的 0.81/0.75 到 BrowseComp 的 0.25/1.00（FPR 0.90）跨度极大；论文同时报告无 flag 的 run 正确率 83.2% 而 flagged 62.5%，即过程信号与结果正确性显著相关但远不等价。两条边界必须一并读：作者明确指出"false positive"只意味着被 flag 而答案正确，并非过程判断的真值——process flag 自身的人工标注精度被列为未执行的扩展；且该 precision 是与谓词同底座（Gemma 4 31B）的自评，不是外生校准。真正 task-agnostic、抗 rubber-stamp 的 gate 谓词校准仍未出现。

第二个数字仍然缺席，缺席的形态值得记一笔。[[Papers/2609-RSIAgent]] 的探索循环全靠一个 verifier agent 判定候选操作序列是否达成子目标，通过的序列写进持久记忆供后续任务复用；该文从未量化 verifier 准确率，却在失败分析里记下它在字段值无依据、产物与官方 rubric 不符的情况下仍返回 PASS。判据自身的错误率没有被测，而它的错误被结构性地保存下来——这条通路在 §10.6 展开。

### 6.3 内化 vs 外挂分岔

[[Papers/2607-SEED]] 把 hindsight skill 蒸进参数（训练用、部署弃）与 library 外挂路线构成 skill 归宿的真分岔——内化省部署开销与检索基建，代价是丢失可解释性与可编辑性；其静态 library 消融 −7.4 同时警示外挂 skill 会随 policy 演化过期。

[[Papers/2607-SESA]] 给这条分岔加了一个此前缺失的对照，且结论对外挂路线不利。它训练时全程带技能库（157 条 priming 技能起步、每 10 步整合一次待定队列、准入去重与失效淘汰），但在评测时把库**关掉**跑了一遍：SESA-Off 相对 SSP 已经拿到 +1.8 / +2.2，而重新开启同一个最终技能库只再加 +0.5 / +1.0，且数据集层面有涨有跌。也就是说这套技能库的绝大部分收益不是"部署时检索到有用的经验"，而是**训练期它塑造了出题分布与 rollout 分布，最终落进参数里**。同一现象在 [[Papers/2607-SpyRL]] 上以另一种形式出现：那里被训练的自演化机制（自博弈角色）在部署时同样完全不存在，收益全部沉淀为参数。

这不推翻 §6.2 "gate 即收益来源"，也不推翻外挂路线本身——[[Papers/2607-KnowActGUIClaw]] 的跨 backbone 可迁移（+3.1pts）仍是外挂路线独有的、内化路线无法提供的性质。它改的是**默认归因**：一个"训练时用库、部署时也用库"的系统报出的总增益，不能被读成检索式技能复用的证据，除非它给出关库对照。库内目前只有 SESA 做过这个对照，因此这条结论是单篇、单次运行、无方差的证据（该论文全文无 seed / std / error bar，也未做算力或 token 匹配的安慰剂对照），标为**库内暂无独立验证**；但由于关库对照的成本极低（评测时改一个开关），它作为一条方法学要求比作为一条经验结论更站得住。

[[Papers/2608-EvoHarnessRL]] 是这条要求最直接的下一个适用对象，而且它自己的两个观测让内化与外挂两种读法无法区分。它把 harness 使用本身变成可训练动作：Belief / Progress / Experience 三块状态对应 track / commit / recall / note 四个动作，与环境动作共享同一个 $T_{max}=70$ 的步预算，先 SFT 后 GRPO。ALFWorld unseen 上 ReAct 50.0 / Base 77.6 / SFT 69.4 / RL 86.6，seen 上相对 ReAct 是 47.9→96.9。但论文自己报告的动作统计显示，RL 之后 harness 调用退火到约每 episode 一次，其中 `recall` 保留而 `commit`/`note` 归零；同时它的 SFT 教师是 Claude Opus 4.5，该模型在同一张结果表里以纯 ReAct 就拿到 96.4 的平均分。于是"harness 在部署时持续承重"与"harness 只是训练期的一套课程、能力最终落进参数"两种解释都与这些数字相容，而论文的消融只做在冻结的 inference-time harness 上（56.4% 那一档，逐个去掉 Belief/Progress/Experience），96.9% 的训练后策略本身没有任何组件消融。最接近的对照是同底座的 standard GRPO（65.6），但它同时缺了 SFT 阶段，所以 BPE 动作与 Opus 教师蒸馏这两项贡献仍然绑在一起；"同样 SFT+GRPO 但去掉 BPE 动作"的臂不存在。判别实验与 SESA 那次是同一个：评测时禁用 harness 动作再跑一遍。在它被做出来之前，这篇的增益不能被计入外挂路线的部署期证据。

SESA 自身的消融顺带给出一个次级判断：去掉记忆 priming 56.2→54.7、去掉 frontier shaping 54.0、去掉失败蒸馏 53.5——**失效最严重的是失败蒸馏而非技能库**，与 §4.3 "把失败从丢弃样本变为定向监督信号"是同向证据。需要一并记的负面模式：Bamboogle 在七个 backbone 分块中有六块相对 SSP 回退，论文未讨论；其"challenger 与 solver 双向协同演化"的机制主张没有隔离实验支撑，论文自述该动力学是相关性观察，本文不采用。

这条分岔一直缺第三个对照臂：**什么都不存，把同样的预算花在推理时**。[[Papers/2607-RethinkSkillEvolve]] 把它补上了——两个控制组都从冻结的 parent skill 出发，共享 executor、工具接口、test pool、verifier 与调用预算，Parallel Sampling 在 $K$ 次尝试上报 oracle any-success，Sequential Refinement 以任务和上一次回答为条件重答。两个 benchmark 给出完全相反的答案：SearchQA 上 evolved skill 77.93、Parallel 77.50，只差 0.43 点（parent 75.64）；SpreadsheetBench 上 evolved 85.77、Parallel 54.80，差 30.96 点（parent 50.53）。算力还是倾斜给采样一侧的——evolved 是单次调用，Parallel 在 SearchQA 用到 $K=6$、共 6,324 次计分尝试，而 oracle any-success 按论文自述是假设完美事后挑选的上界、不可部署。判据因此相当清楚：**收益若来自答案形式上的约定，采样即可替代；收益若来自一条完整的多步执行流程，采样替代不了**。Sequential Refinement 在两处都贴着或低于 parent，说明"以上一次回答为条件"本身不构成纠错反馈。

成本侧的账要按摊销读。被选中的那次 SearchQA 演化消耗 2,750 次目标模型调用，摊到 1,400 个测试任务上是每次部署多付约 2 次调用，而采样的开销按任务线性累加、不随部署规模摊薄——两条路线在大规模部署下的成本曲线形状不同，这一点比任何单点分数更决定选型。该判据对 GUI/computer-use 的含义只能作为假设记下：那类任务动作不可回滚、失败代价非对称、oracle any-success 在真实部署中根本不可用，30.96 点更可能是下界而非上界，但这套协议尚未在 GUI 环境里被复制过。

### 6.4 Open Problems

[[Papers/2509-Misevolution]] 实测 8 个顶级 LLM 工具创建-复用平均 Unsafe Rate 65.5%，摄取含隐藏恶意代码的外部工具时 Refusal Rate 全线 <8%。技能库的 homogenization/冗余度量、gate 谓词自身可信性、以及安全维度 gate 均无系统方案。冗余这一格现在有了半个答案：**长度维度已经可测也可治**——膨胀因子（演化 N 轮后的 token 数比初始）是个便宜的标量，[[Papers/2608-SkillZip]] 测出五轮约 5.2×、十六轮 2.5–3.7×，并给出零 rollout 的压缩算子（§6.1）；但语义冗余（两条技能是否在做同一件事、库整体的覆盖是否随演化收窄）仍无任何度量，而 homogenization 关心的正是后者，压缩率高不等于同质化低。[[Papers/2608-SkillZipPro]] 把可测的一侧又推进一格：真实演化库里 79%–84% 的内容是重复的，每轮新增内容与既有文本的重复率稳定在 55%±3%，可移除份额随库龄从 29% 爬到 53%。它测的仍是文本层重复而非功能层同质——两条措辞完全不同、做的却是同一件事的技能，在这套记账里都算新内容。第二条新缺口在攻击面：**技能准入的判据读的是攻击者可控字段**——[[Papers/2608-SkillJack]] 的消融显示同一份投毒 skill 在 LLM judge 只看到代码时判恶率 36.7%，补上攻击者撰写的良性 name 与 documentation 后**反而降到 10.0%**——给 judge 看得更多，它判得更松，逃逸的载体是表层元数据而非代码，而 §6.2 里绝大多数 gate 与检索器恰恰以这些元数据为输入。

另一条是：**技能库的部署期贡献缺省未被测量**——关库对照（§6.3）目前只有一篇做过，而它给出的分解是训练期占大头；在这个对照成为标配之前，"技能库带来 X 点提升"这类表述在库内一律应视为未拆分的联合效应。

与之同构的第二条方法学要求是**把 gate 与部署选择器分开报告**：一个演化循环里"谁配拿到全量评测预算、谁能进档案"与"最终交付什么"往往由两个不同机制决定，只有把后者也消融掉，gate 的天花板贡献才有意义（§6.2）。这个对照与关库对照一样便宜——去掉判决规则再跑一遍，或固定判决规则换掉最终选择器——而它一旦被做，目前唯一的结果是 ±0.0。第三条仍空缺：把验证行为与验证结论分离的算力配平对照（花掉同样的筛选预算但丢弃判决），gate 家族里只有 GRASP 声称做过，而那条记录缺核验。

第四条是这条链的**报告口径**。[[Papers/2607-RethinkSkillEvolve]] 把两个此前没人报的量变成了可算的：artifact 级产出率（388 个 candidate 对 55 个 byte-distinct validation best，靠给每份 skill 算 SHA-256 把"分数动了"与"skill 真的动了"分开），以及同一份字节相同的 skill 在重复部署下的分数带宽（49 题 split 上标准差 3.92 点，100 题配对面板上 ±3 点内不可判）。两个量都便宜——前者只需算哈希，后者只需把最终 skill 多跑两遍——而缺了它们，"演化让分数涨了 X 点"就无法与"重跑同一份 skill 也能涨 X 点"区分开。把这两项列进技能演化工作的默认报告项，是本节成本最低的一条方法学要求。

## 7. Architecture / Workflow Evolution and Recursive Self-Improvement

演化 agent 拓扑、workflow 甚至自身代码——搜索空间最大，也是 recursive self-improvement 叙事的实证载体。

### 7.1 workflow / topology 搜索：offline 搜索与 inference-time 改写

ADAS → AFlow（MCTS 搜 code-represented workflow）→ ScoreFlow / MaAS / EvoFlow；communication graph 侧 GPTSwarm、G-Designer、AgentPrune。这条线长期只有一个时机：offline 搜索、部署前冻结，优化依据是聚合 validation 表现，因而无法响应单个 instance 上暴露的结构性故障。

[[Papers/2607-MANTA]] 是库内第一个例外，把 topology 从"部署前的搜索目标"改成"执行中的可写对象"——Planner 按任务从长期 playbook 规划初始拓扑，一轮协作后由只看过程证据的 Trace Auditor 判断结构是否失效，触发则执行一次受限突变（≤3 个操作，算子为 add_agent / expand_agent_to_group / set_group_pattern / add_edge / remove_edge / set_context_policy）再跑最后一轮。让 test-time 结构改写变便宜的是工程前提而非搜索算法：agent 在 stage 之间无状态、会话状态全部落在 append-only 的 packet store 与 evidence ledger、可见性策略由代码在读取时解析，因此突变只需把 context controller 重指向新 spec，零迁移零重算；跨轮 candidate 投票保证变坏的突变无法覆盖更好的既有答案。这三点独立于 topology 这个具体演化对象，是任何"运行期改结构"设计的可复用地基。

收益与归因必须分开读。Gemma 4 31B 统一底座、5 benchmark × 30 题 × 3 run 下平均 74.0，高于最强 baseline ADAS 的 68.2；与 static MAS 的对比是全文最干净的一段——MANTA 77,652 token 得 74.0 而 Voting 80,781 token 得 64.7，近似等预算下 +9.3 点。但三条证据同时压缩了"拓扑自演化"在那 5.8 点平均领先里的份额：增益几乎全部来自 BrowseComp（比次优高 12.3 点），而该 benchmark 90 run 里 83 run 被 flag（FPR 0.90），adaptive 实际退化为固定的两阶段流水线；162 个修复操作中 42.0% 是一条手写的 deterministic retrieval contraction（塌缩成单 agent 并授予全局证据访问），论文自陈其不经 Planner、不属于 mutation 语言；mutation 消融同时砍掉了结构改变、额外一轮计算（72,105 → 100,315 token）与注入的 Auditor 诊断文本，三者绑在一起。论文在 §Complementary validation 中点出了正确的拆分设计（同 trace 前缀出发的 equal-budget paired replay）但未执行。消融本身还给出一个与"演化"叙事不完全一致的排序：任务条件化的**初始规划**贡献（−14.2）大于 mutation（−10.9）。

WorkBench 是该工作未解释的反例，也是拓扑演化表达能力的直接证据。该任务族上多 agent 化整体有害（static MAS 15.6–23.3，single agent 41.1），singleton 就在 MANTA 的根交互模式集合内，且此处 audit 质量为全场最高（precision 0.81 / F1 0.78），但 MANTA 只回到 43.3，被 ADAS 的 66.7 甩开 23.4 点。现有 mutation 算子里没有"收缩规模"这一族——唯一的收缩是检索专用的手写规则——过程信号也无从表达"整个多 agent 组织本身是错的"这类诊断。与 [[Papers/2605-MetaTeam]] 并读可得该路线的时机轴：Meta-Team 在任务**之间**演化团队组织，MANTA 在任务**之内**演化通信结构，跨 run 只继承原则性 playbook（budget 置 0 的迁移实验跨域均值 +3.3，但每 benchmark 仅 30 题，+3.3 恰等于一道题，证据强度撑不起"可继承的结构知识"这一结论）。

第三种时机把演化对象从产物换成**搜索策略本身**，反馈则来自已经录下来的搜索树。[[Papers/2609-DreamRSI]] 指出 AlphaEvolve 一系的 discovery loop 把算力全投在候选解上，而决定"在哪条分支上继续、开几条、什么时候停"的 exploration 策略通常手写且全程固定；把这一层纳入优化的障碍是每试一个策略都要付一次完整 rollout 的钱。它的做法是把跑完的一轮 discovery tree 冻结成 replay simulator——每个节点存着当时的 workspace、产物、评测诊断与分数，换一个策略去走这棵树就不必重新调用 coding agent 与 evaluator——据此改写策略代码再放回线上。Lasso regularization path 上，相对同初始化、策略冻结的对照，Gemini-3.1-Pro 用 317 次 discovery-agent 调用（对照 550）把平均运行时从 3587.1 ms 压到 2931.0 ms，Gemini-3.7-Flash 用 1879 次（对照 3200）从 2516.7 压到 2350.6。

三处边界决定这些数字怎么读。其一，replay 的转移是确定性的揭示而非生成——被选中的节点只返回已经录好的那个孩子，候选策略因此只能换顺序、换批大小、多走少走几步或早点停，无法回答"在某个节点换个方向会怎样"，被优化的实际是预算分配、批处理与停止规则。其二，论文给出的唯一保证是新策略在固定 history 上的**平均 replay 分**不劣于当前策略，该保证不涉及线上表现，而 replay 分与线上表现的相关性全文未测。其三，报告的 Compute 只数 discovery-agent 调用，offline dreaming 里 $M$ 个策略版本 × $t$ 棵树的重放评估与改写调用一次都不计。结果也需要按列读而非按均值读：6 个 held-out 数据集里 Gemini-3.1-Pro 有 5 个慢于冻结对照，平均值靠 RCV1 一列（14616.0 对 19550.1）拉回；三个数学任务里 Auto Correlation 的 1.456375 差于它自己的冻结对照 1.456001，Circle Packing 六位小数完全相同；全文单次运行、无种子、无误差棒。同篇还留下一条与 §4 呼应的观察：在等预算下给 exploration 加 prompt 级的语义方向指引，两种范式都不如不加指引（仅在一个 kernel 任务上测）。

### 7.2 自改代码的 scaffold lineage

自改代码 agent 构成一条清晰谱系：STOP（自引用代码优化）→ Gödel Agent（自我修改的通用框架）→ [[Papers/2505-DarwinGodelMachine]]（agent archive + 读自身日志自诊断自改 scaffolding + benchmark 实证验证替代形式证明，SWE-bench 20.0%→50.0%，跨模型/跨语言迁移成立，成本约 2 周/run）→ SICA → [[Papers/2510-HuxleyGodelMachine]]→ [[Papers/2511-LiveSWEAgent]]（on-the-fly）→ [[Papers/2607-MetaSkillEvolve]]（两级递归：把"改进流程本身"纳入演化）。

谱系里唯一把自改范围显式约束住、并与前述工作做过同尺子对照的是 [[Papers/2607-HarnessBank]]：它只改 harness 的可变表面（prompt / knowledge / runtime / config），评测、记账与自演化逻辑作为不可变 kernel 被排除在搜索空间外，因而不落入 DGM 式的开放自改。在同 split、同配对 2σ 判据、rollout 预算相差 2.1× 以内的条件下，五个 sealed test 里它 credit 4 个，无 gate 的 DGM 1 个，只改 prompt 的 GEPA 0 个（该比分含 evolver 强度未对齐的混淆，见 §6.2）。它的 cross-model 实验还给出这条谱系一个被忽略的性质：演化产物是针对特定底座失败模式的 correction 而非普适更优配置（§11）。

[[Papers/2510-HuxleyGodelMachine]] 是谱系当前上界：发现的 agent 在 full SWE-bench Verified 达 61.4%（进入全模型 top-10），换 GPT-5 backbone 迁移 SWE-Lite 达 57.0% standard（超过 SWE-agent 56.7%）/ 47.8% filtered（落后一题），论文据此称 "human-level"。

谱系的另一支不改 scaffold 而把演化轨迹回灌进权重。[[Papers/2607-FrontisMA1]]（OpenMLE 栈）在 machine learning engineering 域打通三层——5,758 个 quality-gated 可执行任务、用执行反馈 post-train 四个原子 program-transformation 算子（Draft / Improve / Debug / Crossover）、再把训好的 35B 模型部署进长程演化搜索——MLE-Bench Lite（22 任务、每任务 12h、单卡 RTX 4090 限 12GB VRAM、3 次独立 run）上 Medal Average 从 base 的 39.39% 提到 60.61%，配 Evo-Max 达 71.21%；30B 底座复现同向（34.85 → 53.03 → 66.67）。最有迁移价值的设计是**监督单位的选择**：训完整 trajectory 会把监督绑死在某个 controller 的搜索策略上，把监督下沉到原子算子则让同一批局部技能被不同搜索算法复用，使 post-training 与 inference-time search 共享同一接口——这个抽象层次的选择独立于 MLE。其 reward 侧设计（随 policy 分数前沿漂移的自适应 bounds + 把组内差异在上尾放大的 entropic advantage）针对的也是一类结构而非一个任务：指标异构、绝大多数候选无效、只有最好那个才算数。

标题中的 recursive self-improvement 则是纲领而非结果，作者在 Related Work 与 Limitations 中把这条边界划得清楚：训练是部署前的一次性离线过程（SFT → RL → 冻结），演化系统本身按其自述 largely fixed，全文只到 generation 1，没有"MA1 训出 MA2"这一步。按 §2.1 判据这是**单次 meta-evolution** 而非递归，与 [[Papers/2607-MetaSkillEvolve]] 把"改进流程本身"纳入演化的两级结构不在同一层。两处归因缺口须一并计入：SFT teacher 为 GLM-4.7、evolutionary path 的轨迹亦由 GLM-4.7 驱动 AIRA-Evo 产生、trajectory-step 由 DeepSeek-V4-Pro 标注，因此 21.22 个点里"执行反馈接地的学习"与"蒸馏更强外部模型的 MLE 习惯"没有实验能分开（语料结构加剧此疑问：Draft 占 74.0%，承载演化叙事的 Improve+Crossover 合计仅 9.4%）；全文无算子级 ablation、无 SFT/RL 拆解，Evo-Max 的 +10.6 点把跨任务经验先验与异步多卡并行两项变化打包上线，机制主张（"Improve+Crossover 贡献 85.0% validation gain"）来自单任务轨迹案例。基准判别力同样有限——22 任务下一块奖牌约 4.5 个百分点，71.21% ± 8.57% 与 GPT-5.6 Sol + Codex 的 72.73%（单次点估计）区间高度重叠，作者自己的 artifact 审计表里还列有 75.76%–80.30% 的既有系统（预算更大）。该工作的实际贡献因此不在分数，而在它是该表中唯一 data / sandbox / train code / RL method / eval / weights 六项齐全的行：上面缺的 ablation 由此从"必须相信作者"变成"别人可以补的实验"。边界：六项齐全为作者自评，§1 对 release 仍用将来时，链接可达性本文未独立核查。

整条谱系有一个共同前提：harness 是跨任务携带的耐久工件。[[Papers/2608-JITAgent]] 把这个前提直接取消——harness 按任务现场生成、用完即弃，被演化的对象换成生成它的那个模型。做法是先用 $(\mathbf{M},\mathbf{P},\mathbf{A},\mathbf{F})$ 四模块协议把 harness 约束成受限程序空间（memory / planning / action / capability orchestration，接口、生命周期与验证规则由协议固定），再用同一 kernel 下重实现的 13 个代表性 scaffold 作 seed bank，最后以 Qwen3.6-27B 为底座分三阶段训练生成器：SFT 加 DPO 学任务条件化定制、teacher-forced 学两轮内修复合成失败、clipped PPO 学超越 archive 前沿。九个 benchmark 上替换默认 scaffold 后 18 个 backbone–benchmark 配对全部提升（GLM-5.2 平均 74.1→81.8，DeepSeek-V4-Flash 66.7→75.5）。最可复用的一步是那个类型签名：它把"生成 harness"从开放式代码生成收窄成填四个已知槽位的结构化输出，没有显式 planner 的结构用 null directive 保持类型一致，因此 ReAct 一类不需要特例。

三处需要一并记。其一，固定 backbone 的受控对比里 token 与成本在全部 6 个设置中最低（相对最便宜的固定 harness 降 14.9%–54.1%、均值 36.0%），而性能只在 6 个中的 4 个居首——它最稳的收益是效率而非分数，且论文未说明报告的 token 与成本是否含生成器自身的开销。其二，它写进定义的三条性质里 reliability 完全没有量化证据：协议合法率、生成失败率、两轮修复成功率一个都没报。其三，全文无 stage 级消融，四段训练的贡献无法拆分；而"按任务现场生成优于预先优化"这条主线按其附录自述是结构性论证而非经验排名，没有任何一个预先优化式 harness 方法被跑在同一 benchmark 上。

冻结底座、只演化外围代码这一形态在具身侧也出现了。[[Papers/2608-Zetta]] 把闭环下沉到 action frequency：一个 code-based runtime critic 逐 action chunk 产出结构化 proposal，Orchestrator 裁决是否从 VLA 切出去执行 recovery skill 并按 re-entry contract 交还控制权；rollout-batch 层做失败聚类与逐层因果诊断生成候选 critic/recovery，iteration 层用 §6.2 那道双闸门决定是否入 skill memory。base VLA 权重全程不动，RoboCasa 18 任务 macro-average 73.56%→93.56%，LIBERO-Pro 全部 40 个 task-setting 对 32.00%→71.13%（摘要标的 90.8% 是 Goal 两个 setting 的均值，不是全集）。配套的执行基建把 rollout 吞吐从 1.72 提到 35.1 episodes/min——自演化研究的迭代速度长期受限于 rollout 吞吐而非算法，这一格的工程数字比方法本身更容易被别人复用。它与本节其余工作共享同一处空缺：三条 loop 一条都没有单独消融，也没有算力配平对照，因此"闸门 / runtime critic / recovery skill 各自值多少"在这篇里没有答案。

### 7.3 credit assignment 的粒度

DGM 与 HGM 的核心分歧在**用什么信号选择 parent 做下一步自改**。HGM 提出 clade-level（宗系级）credit assignment：以子代整枝（clade）的聚合表现而非单节点即时表现估计一个 agent 的改进潜力，其 CMP（clade metaproductivity）与真实改进的 Pearson 相关达 0.778，显著高于 DGM 式即时 guidance 信号的 0.285。这把 recursive self-improvement 的瓶颈从"如何自改"推进到"parent selection 信号质量"这一新维度——选错垫脚石比改得不好更致命。

到 2026 年中，"改进标量分数不足以选 parent"已成为该谱系的收敛判断，五个独立工作在打同一个靶而解法各异：DGM 用即时 benchmark 分数；HGM 换成 clade 级聚合（CMP 与真实改进 Pearson 0.778 vs DGM guidance 0.285）；[[Papers/2607-FrontisMA1]] 在 RL 与搜索两处都把 fitness 拆成多因子——RL 侧 $F(p)=\text{norm}(R_p)+\text{norm}(\text{Var}_c R_c)+\text{norm}(C_p)$（强父 + 子代结果方差仍大即信息量仍在 + 按访问次数降温防 incumbent 垄断），搜索侧 $U_i=\lambda_s\tilde s_i+\lambda_\Delta\tilde\Delta_i+\lambda_n\nu_i$（quality / 相对父的进步 / method-family novelty，权重固定为 1.0/0.6/0.3 且不学习）；[[Papers/2607-MANTA]] 则把选择依据整体换成不接触结果的过程 flag；[[Papers/2609-AgentGrad]] 干脆不推断信号而做干预——在多 agent 流水线上从末端逆序替换每个 agent 的输出为由 ground truth 构造的 hint，第一个能把整条链的 reward 拉到上界的位置即被判为责任所在（§5.5）。分歧点因此明确：信号该来自**结果的聚合方式**（clade）、**结果的辅助统计量**（方差、访问次数、novelty）、**根本不来自结果**（过程审计），还是干脆**不从观测推断而用干预定位**。四类目前没有在同一 testbed 上被对照过，这是该谱系可立即补上的实验。把 HGM 的 clade 聚合接进 OpenMLE-Evo 的 parent 选择是其中最直接的一个。

干预这一类另有一条独立于具体方法的代价：它要求存在一个能被替换进链中的"正确输出"。AgentGrad 在训练集有 ground truth 或可验证输出约束时成立，而 §7.2 的 scaffold 演化场景恰恰没有这种东西——一个 harness patch 没有可替换的正确版本。因此干预式 credit assignment 的适用边界与 §3.4 的可验证性谱系重合：**它是 deterministic verifier 域的一个便宜方法，而不是这条谱系的通用解**。

### 7.4 天花板：scaffold vs weights

DGM 类架构自演化只搜索 frozen FM 之外的 scaffolding 空间——收益真实（+30pp）且可迁移，但上界由基座模型锁定；突破上界必须回到 model evolution，而那条路线恰好受 reversal 与 safety 衰减约束最强。

但"frozen FM 天花板"是两个不同的量被合并成了一个词，[[Papers/2608-MacaronV1]] 把它们分开测了。该工作把 policy 显式写成 $\pi_\phi(a|o;\theta,c)$，$\theta$ 是权重、$c$ 是语言空间的配置（harness 提示、上下文策略、工具约定），从而把权重更新与配置搜索拆成两个可独立执行的自适应通道。实验取 122 个由 TerminalBench-2.1 派生的任务，选取标准正是**冻结基座在官方 reward 下全部得 0 分（0/122）**——即从单次通过率看已经触到天花板。在完全不更新权重的前提下，69 个 job、450 次尝试的配置搜索**累计覆盖 122/122**，而在全集上扫一个更强的单一配置只能拿到 11/122。这两个数字应分别命名：11/122 是**操作天花板**（一个配置服务所有任务时的上界），122/122 是**激发天花板**（允许每个任务用它自己最合适的配置时的上界）。两者相差一个数量级，意味着此前被归给"基座能力不足"的失败里有相当一部分是 elicitation failure 而非 capability failure，而 scaffold 演化的收益空间恰恰落在这个夹层里。

必须同时记住这个分解的代价：累计覆盖不是一个可交付的系统。122/122 是 450 次尝试跨 69 个 job 的并集，没有任何单一配置能达到它，也没有任何机制能在见到任务之前挑对配置——把搜索成本折算进去，它更接近 pass@450 的重参数化而非天花板的抬升。可承重的结论是"单配置与最优配置之间存在一个数量级的差距"，不能承重的是"scaffold 演化能兑现这个差距"。

兑现它需要一个能在执行前按任务挑出配置的机制，而 [[Papers/2608-JITAgent]] 是这类机制的第一个学习式实例：生成器读到任务描述与可用能力后现场产出一份 harness，不依赖任何事后挑选（§7.2）。它在九个 benchmark 上把 18 个 backbone–benchmark 配对全部推高、平均 +7.7 分，量级与"操作天花板到激发天花板"那一个数量级的差距完全不可比——但两者从未在同一套任务上被测过，Macaron 的 122 个任务是按"冻结基座全部得 0"筛出来的，JIT-Agent 的九个 benchmark 则是常规难度。**因此这个夹层到底有多少可被非 oracle 机制兑现，目前没有任何数字**。把 Macaron 的 122 任务集交给一个按任务生成配置的生成器跑一遍，是这条线上最直接的判别实验：单配置 11/122 是下界、事后挑选 122/122 是上界，学习式选择器落在哪里决定 scaffold 演化的收益空间究竟是一个数量级还是几个百分点。

### 7.5 Open Problems

"自我改进能否复利"（recursive self-improvement）在两个层次都有明确收敛边界：scaffold 层受 frozen FM 天花板约束，weight 层受 reversal 约束。AGI 叙事下的无界 RSI 在现有证据下不成立。credit assignment 的信号质量（HGM 的 CMP 0.778 vs DGM 0.285）说明谱系的下一步瓶颈已从"改法"转向"选法"。

另有两个缺口。其一是**术语与实物的系统性错位**：以 RSI 为题的工作里，多数实际做的是单次 meta-evolution（用一轮演化搜索的轨迹训一次模型，再把模型放回同一个搜索器），[[Papers/2607-FrontisMA1]] 是最清晰的样本——作者在正文里划清了这条边界，标题与 abstract 没有。判据不难给：是否存在 generation ≥2、演化系统本身是否也在被演化、权重更新是否发生在部署后。[[Papers/2608-MacaronV1]] 是同一形态的第二个样本，且它的坦诚程度与 Frontis-MA1 相当：其 MindForge 循环设计为 Discovery → Expansion → Update 三段，但报告只跑通 Expansion，Update 段未走完，全部结果都在 generation 1 上；作者自己把"持续学习是否复利"与"多实例经验能否汇聚成集体智能"列为未验证的开放问题。按上面三条判据，它与 Frontis-MA1 一样落在单次 meta-evolution 而非 RSI。把这三条判据摊到以 RSI 自称的五个工作上，错位就不再是个别标题夸张，而是该谱系的默认叙述方式：

| 工作 | 存在 generation ≥2 | 演化系统自身被演化 | 权重更新发生在部署后 | 实际形态 |
|:--|:--|:--|:--|:--|
| [[Papers/2607-FrontisMA1]] | 否（只到 generation 1） | 否（作者自述 largely fixed） | 否（SFT→RL→冻结，部署前一次性） | 单次 meta-evolution |
| [[Papers/2608-MacaronV1]] | 否（Update 段未走完） | 否 | 否（权重全程冻结，只搜配置） | 单次配置搜索 |
| [[Papers/2609-RSIAgent]] | 否（框架不变，跨任务不继承） | 否 | 否（权重固定） | 任务内探索 + 持久记忆 |
| [[Papers/2609-NeoHorse1]] | 否（作者自述只跑完一轮） | 否 | 是（用线上流量重训） | 部署数据驱动的单轮再训练 |
| [[Papers/2609-DreamRSI]] | 是（Lasso 5 轮、数学 10 轮，策略跨轮携带） | 否（改写策略的那个 agent 固定） | 不适用（无权重更新） | 多代的代码级策略迭代 |

五行里没有一行三项全中，而每一行中的那一项还各不相同——DreamRSI 有多代但改写者固定，NeoHorse-1 的权重更新确实发生在部署之后但只有一轮，其余三个一项都不满足。**"recursive self-improvement"目前在文献中标记的是意图而非实现形态**，引用这批工作时应当按上表的形态列而非按标题读。

[[Papers/2609-RSIAgent]] 值得单独判一次，因为它自述的 recursive self-improvement 是全表里离字面含义最远的一个。它在目标任务上先做广度探索（尝试不同操作路径）再做深度探索（沿最优路径细化），由 verifier 判定成功的片段写进持久记忆，正式作答时复用——权重固定、框架不变、记忆按任务从空建起。按本文三条判据它一条都不满足，实际形态是**任务内的探索加持久记忆**，与 §5 的 memory 演化同族而非与 §7.2 的 scaffold 自改同族。这个判定不是措辞洁癖：该文自己的 GameCraft-Bench 是全表唯一一处同起点、同底座的受控对比，在那张表上（40 个任务、四个 generator）换 harness 带来 +5.07 / +11.33 / +14.18 / +12.52，而开启它的"RSI"机制只带来 +3.44 / +3.76 / +3.99 / +3.64——**自我改进的收益被拆成 harness 与机制两级时，大头在 harness 一侧，机制约为其三分之一到四分之一**。OSWorld 2.0 上 partial score 71.97→78.98、binary 37.80→42.68，ALE 83.75→84.82，但主表把真实 RSI 结果与保留的基线数字拼接（OSWorld 41/82 任务、ALE 19/67 任务重跑），只有基线未满分的任务被分配探索而满分任务仍留在分母，且没有任何算力配平臂——附录自陈不是 matched-budget 估计。同篇的 w/o RSI 版本在 ALE 上已达 83.75，超过 GPT-6 Astra 的 82.26，这条比较里被验证的是 harness 而不是自改进。

[[Papers/2609-NeoHorse1]] 在另一侧给出该谱系最实际的一条工程观察：一个已经在线上跑的 routing harness 自带 RSI 需要的反馈机制——router 为每个 user turn 记下预测的能力档位、实际服务的档位与随后的交互，这份记录既是训练语料又是不用额外标注的难度标签，同一个 routing score 因此可以同时给 SFT 排课程、给 on-policy distillation 调度起始上下文、按能力短板决定下一轮数据配比。十个 benchmark 的宏平均在 4B 上 58.94→64.87、9B 上 65.60→69.04。但它的受控实验只比较了数据来源与数据量：同配置同基座下 routing-harness 数据五项均值 70.57、公开 agent 数据 64.32，而该基座在这五项上的均值本身就是 69.31——**routing-harness 一轮相对基座只有 +1.26，其中 HumanEval 一项贡献 +9.14，其余四项净 −0.57**。课程排序、on-policy distillation、能力导向配比三个核心机制无一有对照消融。所以这篇可承重的是"部署流量可以自动转成带难度标签的训练语料"这一机制设计，不可承重的是"这套自改进循环带来了宏平均 +5.93"。

[[Papers/2609-GeneralizedAgentIteration]] 试图把这些判据形式化：系统写成 $\chi=(\pi,V,m,U,\rho)$ 五组件，agent 是其中**可被修改的那个子集** $Ag$，两个 dial——修改器 $m$ 是否属于 $Ag$、评价基准 $\rho$ 是否接地于 agent 之外——决定实例落在 generalized policy iteration 还是 RSI，以及 anchored / goal drift / fully self-referential 三种极性。把 agent 从"策略"重定义为"系统里可被改动的那部分"是这套坐标最有价值的一步：它让"改进机制是否属于被改进对象"从修辞变成可判定的二值问题。它与上表的关系是互补而非替代——上表按实物形态分，GAI 按结构位置分，而 GAI 的 Table 3 恰恰把 Gödel Agent、DGM、STOP、SICA 等一并放进同一个 anchored 行，作者也承认已演示的系统绝大多数是 anchored。该文无实验、无定理，作者自陈 RSI 到 GPI 的归约是散文而非带显式假设的命题，且世界与目标被按假设固定在系统之外，因此 §8 的 agent-environment co-evolution 在这套坐标里没有位置。它提供的是判据的形式化表达，判据本身仍需经验工作去填。

其二是**增益的预算与来源归因**：[[Papers/2607-MANTA]] 的 mutation 增益与 +28K token 绑定，Frontis-MA1 的 post-training 增益与外部 teacher 蒸馏绑定，两者都缺 equal-budget / no-teacher 对照臂。这两处归因缺口的性质相同——报告的是"某个演化机制 + 某项额外资源"的联合效应，而结论被写成前者的效应。

## 8. Co-Evolution: Environments and Multi-Agent Teams

自演化的第三根轴是"演化对手是谁"：环境（任务分布、verifier、affordance）还是队友（多智能体团队）。

这根轴现在有了自己的 anchor survey。[[Papers/2608-CoEvolutionSurvey]]（HKUST/UIUC/CUHK/HKU/PKU）与库内已有的 [[Papers/2507-SelfEvolvingAgentsSurvey]]、[[Papers/2508-SelfEvolvingAIAgentsSurvey]] 是正交的两种切法：后两篇按被演化的组件（model / memory / tool / harness）分类，这一篇按**演化算子 $\Omega$ 的作用域**分层——Stage 1 是 $A^{t+1}=\Omega(A^t,E,\tau^t)$（环境固定，耦合发生在 agent 集体内部），Stage 2 是 $(A^{t+1},E^{t+1})=\Omega(A^t,E^t,\tau^t)$（环境进入更新，再分 task-space / feedback-space / interaction-space），Stage 3 是 $\Omega^{t+1}=\Gamma^t(S^t,\Omega^t,\tau^t)$（演化机制自身被一个自生成的修订过程改写）。

这个切法对本节最有用的是它自带一条判别标准，而不是一张归类表：co-evolution 要求**至少两个演化单元相互适应并持续重塑彼此的后续演化**，仅仅交换信息或发生交互不算。据此它在 Appendix A 与十个相邻概念逐一划界（multi-agent interaction、agent loops、harness engineering、evolutionary optimization、continual learning、self-play、self-evolution、meta-evolution、recursive self-improvement、open-endedness），正对该领域术语混用的实际困难。同样值得记的是它对 Stage 3 的诚实：作者明确指出现有工作绝大多数只是单实体前身（PromptBreeder 演化 mutation prompt、MemEvolve 演化 memory 架构），真正跨出这一步的例子只有 RQGM 一类——在 task agent 与 evaluator 共演之上再加一层利用联合反馈引导后续演化的 meta-agent。这与 §7.5 从另一条路径得到的结论重合：以 RSI/meta 为名的工作里，实物达到 generation ≥2 的极少。

它的自身边界也需记：无公开 repo 或 paper list；Figure 4 汇总的跨论文 static-vs-evolving 配对证据受各论文 benchmark 与 setting 差异限制，Appendix C 的取数规则可能带幸存者偏差；三条挑战（dynamic evaluation、scaling、safety & governance）停在方向性建议。此外它的覆盖有一处与本文关切直接相关的稀薄：GUI/harness 与环境的共演在其框架下属于 Stage 2 interaction-space 与 harness 演化的交叉，文中着墨很少。

### 8.1 agent-environment co-evolution

环境从静态评测台升格为共同演化对象，按演化的环境层级分：

| 工作 | 环境侧演化的是 | 机制 | 边界 |
|:--|:--|:--|:--|
| [[Papers/2605-SEAL]] | 训练时 observation function（interface 级） | 单一 base 演化 observation-wrapper，不改难度不改规模不用神经环境 | 只动 observation，不改环境动力学 |
| [[Papers/2512-GenEnv]] | 难度对齐的环境模拟器（difficulty 级） | agent 与 environment simulator 难度对齐地协同演化 | 单步任务生成有边界；RL 基线独立核出 |
| [[Papers/2608-OpenART]] | 环境状态（state 级） | 黑盒搜索 workspace / 文件 / 工具返回值等八类 target 可见的环境状态，benign objective 与 evaluator 全程不变 | 单侧演化：target agent 与攻防两侧模型全部冻结，不构成双向共演 |
| [[Papers/2606-EnvEngineeringSurvey]] | 三范式框架（neural/difficulty/scaling-driven） | anchor survey，把环境演化归为三范式 | 见 §8.2 盲点 |

### 8.2 EnvEngSurvey 的框架与盲点

[[Papers/2606-EnvEngineeringSurvey]]（CASIA，63 页、582 refs）把环境按全生命周期组织：modeling（八属性二分 × 八 domain）→ synthesis（symbolic 三段 task/real-world/de-novo + neural 三层 pixel/word/latent）→ evaluation（correctness/diversity/complexity/fidelity 四维，仅 correctness 成熟，其余三维 under-researched）→ application（agent 演化四路径 + 环境演化三范式的闭环 co-evolution）。其框架有两个记录在案的盲点：环境演化三范式（neural/difficulty/scaling-driven）**漏掉 interface/observation 级演化**——SEAL 只演化 observation function，在三范式里没有位置；agent 演化四路径（memory/orchestration/trajectory/exploration-centric）**缺 tool/skill 路线**。这印证"先验分类学总有漏项"的警惕：分类的价值在能否指导干预。

### 8.3 multi-agent 协同演化

[[Papers/2605-MetaTeam]]（Evolve as a Team）把演化对象从单体扩展到**团队组织**：MAS 完成任务后不把全部轨迹塞给单一 analyzer，而是每个 agent 保留本地执行上下文、通过 post-task 通信交换加工后的分布式证据，在 agent 行为（L1）、inter-agent 协作（L2）、团队组织（L3，可增删角色、重组协作、修订 shared constitution）三尺度上 training-free 地更新 team scaffold（Claude Sonnet 4.6 冻结底座）。核心论点是"MAS 既以团队方式执行，就应以团队方式演化——演化架构要与执行架构对齐"，并用独立的 failure-attribution pilot（TraceElephant，220 条真实 MAS 失败轨迹）支撑：>128K token 轨迹上 collaborative scheme 的定位准确率（Agent-Acc 60.8 / Step-Acc 19.6）高于孤立式 local（58.2/17.6）与集中式 global（43.1/9.8）——长轨迹段恰是集中式反思最吃力处。经验组织消融 collaborative 53.9 > centralized 49.8 > partitioned 44.5 > no-evolution 40.8 直接证明协同交换相对集中式与孤立式的净增益。局限对照本 survey 的两个机制关切：无算法化 per-agent credit assignment（三尺度演化算子 Ω_L1/L2/L3 均为 LLM 反思算子，归因靠讨论涌现）；commit 前虽有显式 validation（role consistency / tool availability / formatting validity / budget，Appendix D），但性质是一致性/预算级检查，**非**基于 held-out 性能回归的 outcome-level 验证——这一 self-gate 正落在 [[Papers/2606-MLASSelfEvolvingSafety]] 的 Collective×Commit 攻击面上，也未回答 [[Papers/2606-CodeSelfReviewCollapse]] 的 rubber-stamp 质疑。

MetaTeam 与 §7.1 的 [[Papers/2607-MANTA]] 构成"团队级演化"的时机对照——前者在任务之间更新团队 scaffold（角色构成、shared constitution），后者在任务之内改写通信拓扑而跨 run 只继承原则性 playbook；两者都是 training-free、只改 scaffold，证据强度的差别在于 MetaTeam 的组织消融直接隔离出协同交换的净增益，而 MANTA 的 mutation 消融把结构改变、额外一轮计算与诊断文本绑在一起。

per-agent credit assignment 这一格现在有了第一个算法化实例，虽然来自另一种多 agent 结构。[[Papers/2609-AgentGrad]] 处理的是固定流水线上 $N$ 个 agent 共享一个终点 reward 的场景，做法是逆序干预而非反思归因：把某个 agent 的输出替换成由 ground truth 或输出约束构造的 hint，第一个能把整条链的 reward 拉到上界的位置即被判为责任所在，干预后的输出同时充当该 agent 的 pseudo-label（§5.5、§7.3）。它与 Meta-Team 的差别不在归因技术而在被演化对象与前提：前者改各 agent 的 prompt、要求链路结构固定且终点可验证，后者改角色构成与协作结构、终点是开放任务。**算法化归因目前只覆盖"结构固定、终点可验证"这一象限**，团队组织级演化的归因仍靠 LLM 反思涌现。把干预式定位接到可增删角色的团队上是一个明确的开口——一旦角色集合可变，被干预的位置本身也在变，责任位置与结构变更会混在一起。

多智能体演化的暗面由 [[Papers/2606-MLASSelfEvolvingSafety]] 刻画：其 MLAS 矩阵（模块 × 演化阶段）指出 shared constitution 是全队共享的可写入 prompt，无准则的演化更新意味着单次错误可 lineage-persistent 地污染全队（Collective × Commit 攻击面）。

### 8.4 co-evolution 的粒度谱与开放问题

把协同演化按"演化对手"与"演化层级"排列，谱系现在在最细一端多了一格：环境状态级（[[Papers/2608-OpenART]]）< interface 级（SEAL）< difficulty 级（GenEnv）< 环境池级（AgentWorld）< 团队组织级（MetaTeam）。最细的这一格与其余各格的区别在于它**什么都不改，只改状态**——任务语义、benign objective、evaluator 全程固定，被搜索的只有 agent 能看到的那部分环境内容（workspace 文件、工具返回、memory 条目、plan state）。

"谁验证 verifier 的演化"这个空白需要改述得更准确。[[Papers/2608-CoEvolutionSurvey]] 记录的 Stage 2 feedback-space 分支里，被演化的恰恰就是反馈机制本身：ROSKA 联合搜索 reward 候选与 policy 变体、CURE 从执行失败演化 unit test、ARCO 用步级分数与最终结果对账、ECHO 按建议是否真的改善 policy 来更新 critic。所以**并非无人演化 verifier，而是无人验证演化后的 verifier**——上述工作对演化后的判分器都以下游任务性能为唯一背书，而下游性能正是该判分器自己给的。这与 §6.2 gate 独立性三层是同一个问题在环境侧的投影：判分器一旦进入被演化对象集合，"用它测出的提升"就不再能同时充当它自身正确性的证据。可操作的最小对照是保留一个冻结的 held-out verifier 用于跨代复评，目前无人这样做。最接近这个要求的一处证据来自 [[Papers/2608-GSAR]]：它把判分器的离线质量与它接进训练管线后的下游增益分开测了——学习式 GUI 轨迹判分器离线准确率 91.5%、比规则式判分器高十几个点，接进同一条在线 RL 管线后却只带来 +3.5 点而规则式带来 +6.1 点（§4.4）。"判分器更准"与"用它训出的 agent 更好"因此不是同一个量，用下游性能给演化后的判分器背书这一做法在方向上也不安全。

OpenART 顺带给出了这类归因要求的一个现成实现样式：它把除待测组件外的一切固定为不变量——两侧模型冻结、benign objective 与 evaluator 不变、通信只经 adapter 投影——因此 ASR 的上升只能归给环境状态的演化。这套"设一组不变量再动一个变量"的做法正是 §7.5、§6.3 反复要求而多数共演工作缺失的东西；它能在这里成立，很大程度上是因为攻防设定天然给出了一个不受演化影响的外部评判标准，而以能力提升为目标的共演工作没有这份便利。multi-agent 的 population 稳定性、合谋、集体 misevolution 仍无实证。

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
| ALFWorld + LifelongAgentBench(OS/DB) | lifelong(memory / harness) | overall SR（宏平均）+ 记忆池/调用量 | [[Papers/2608-RoMeRL]] 0.862 vs MemRL 0.830，池 45K→7K；[[Papers/2608-EvoHarnessRL]] unseen ReAct 50.0 / RL 86.6 | 记忆与 harness 演化的主力评测面；协议是同一任务集跑 10 epochs，per-task 重复暴露是多数记忆方法的隐含前提；**ALFWorld 上 95%+ 的数字跨论文不可比**——split 家族构成、题量与 harness 各家不同且常不交代（EvoHarnessRL 全文未披露 split 的家族计数，其 Base 家族均值 54.65 与正文 56.4 不一致） |
| GAIA / WebWalkerQA | deterministic(deep-research QA) | Pass@1 / accuracy | [[Papers/2608-ZerothOrderSelfEvolve]] GAIA 47.5%（ReAct 23.3 / ARPO 38.8）、WebWalkerQA 34.8%（15.5） | 短答案可精确匹配，因而同时充当 verifier 与连续似然信号源（§4.3）；工具与搜索后端不统一，跨论文横比须同后端 |
| EvoAgentBench 五域 + TB2 + AppWorld | deterministic + judge 混合 | Pass@1 over $K=3$，按与父代配对的 $z\ge1.96$ 决定该增益是否算数 | [[Papers/2607-HarnessBank]] 七域 test +5.1~+15.4，六域过判据 | 把"增益是否算数"写成显式统计判据的第一例；逐域按双侧 5% 判定、七域间无多重比较校正，最弱 credited $p=0.033$；Table 1 无 $n$ 列，仅两域可查测试集规模 |
| [[Papers/2608-AgentStream]]（6 benchmark 编排成任务流） | lifelong / streaming（跨域） | evolution gain $\Delta$ = 同一模型带 state 与 state 恒空之差 | 5 方法 × 3 底座 × 3 场景共 45 个计数单元，11–17 个跑输不演化的同一模型 | 唯一跨方法受控析因；测试时无 ground-truth 标签，演化只用交互内在反馈；每 benchmark 50 题 × 3 seed，无显著性检验且单元格 seed 间标准差常大于效应量 |
| 摘要 / 创意写作（GovReport、WritingPrompts 等） | non-verifiable(生成) | 换序聚合的成对 A/B 胜率（LLM judge）+ ROUGE-L | [[Papers/2607-SpyRL]] 对 GPT-4o-RaR overall 48.9% / 48.2% | 唯一无任何程序化 verifier 的域；50% 是持平线而非零点，须报同 backbone 自比作为 position-bias 校准（未训练自比 51.7/51.8） |
| [[Papers/2508-StuLife]] | lifelong | StuGPA / PIS | GPT-5 17.90 vs human 85.24；PIS 4.68% | 首个"大学生涯"式 ELL，瓶颈定位记忆+主动性（详 §9.2） |
| [[Papers/2604-SkillFlow]] | lifelong(skill) | family SR 提升 | Opus 4.6 +8.43pt；GPT-5.3-Codex −6.02pt | skill lifecycle，差距在修复而非写（详 §9.2） |
| HarmBench / RedCode / Agent-SafetyBench | safety | Safe / RR / ASR | AFlow ASR 54.4→83.1%；工具 Unsafe Rate 65.5% | 演化前后 snapshot + 有限 longitudinal（详 §9.3） |
| CAR-bench（由 [[Papers/2608-TRACE]] 使用） | deterministic(工具使用 / 多轮对话) | Pass@k 与 Pass^k 之差（一致性 gap） | TRACE 把 GPT-5.5 的 Pass^3 从 59.9 提到 94.5（train+test 合并集）；官方 hidden set 50.0→70.0 | 唯一以"每次都对"而非"对过一次"为主指标的评测面；58 个互联工具 + 19 条 domain policy；演化所用任务与主表评测集重合，引用须区分合并集与 hidden set |
| RoboCasa / LIBERO-Pro | deterministic(具身) | 任务 SR 宏平均 | [[Papers/2608-Zetta]] RoboCasa 18 任务 73.56→93.56%；LIBERO-Pro 40 个 task-setting 对 32.00→71.13% | 冻结 VLA + 外围演化的主要评测面；LIBERO-Pro 按 task×setting 成对计分，子集均值（Goal 两档的 90.8%）与全集宏平均差 20 点以上 |
| SkillOpt-Lite 五集合（SearchQA / OfficeQA / SpreadsheetBench / LiveMath / DocVQA） | deterministic + judge 混合 | validation-only 选择 + released test / robustness / transfer 三面 | [[Papers/2607-RethinkSkillEvolve]] 42 次演化：11/14 选中演化后 skill、9/14 部署后 test 更好、7/14 同时改善 robustness 与 transfer | 唯一带 artifact 身份（SHA-256）与重复部署带宽的技能演化评测协议；100 题配对面板上 ±3 点不可判 |
| [[Papers/2608-OpenART]] | safety（长程有状态） | Strict ASR（确定性 evaluator 与 LLM judge 须一致）+ benign completion | 15 agent × 5 model 共 75 配置，pooled Strict ASR 85.0%；单轮 42.9 → 五轮 94.7 | 库内唯一在长程有状态工作流上测演化式攻击的评测面（中位 97 次工具调用，对照论文所列既有安全 benchmark 的 1–15）；ASR 是跨轮 best-of-K 而非单轮值；judge 用的 GLM-5.2 本身也在被测的五个模型之列（详 §9.3） |

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

[[Papers/2608-OpenART]] 补上了其中"长程"这一维，它与既有安全套件的差距首先是量级上的：10K+ 个经过验证的有状态 scenario、50 个 domain、500K+ 的 Tool/MCP/Skill 语料，中位单任务 97 次工具调用，而此前的 agent 安全 benchmark 多在 1–15 次。这个长度直接决定了能测到什么：只有在足够长的工作流上才能观察风险的**传播**而不只是风险的**触发**。被投毒内容从注入点到目标动作的中位传播距离是 37 个 target action（IQR 20–66），首次消费发生在执行进度的 23%，首次不安全输出在 64%，注入到危害的中位延迟占整条工作流的 41%。这组数字直接反驳了短程 benchmark 隐含的假设——不安全行为在注入附近发生——也解释了为什么 snapshot 式评测在长程 agent 上会系统性低估风险。作者从中归纳出三类反复出现的失效：过期假设未被作废、安全判断被沿用而非重算、以及单步安全的动作组合后产生危害。

它的数字须按其定义读。pooled Strict ASR 85.0% 覆盖 15 个 agent runtime × 5 个模型共 75 个配置，"Strict" 指确定性 evaluator 与 LLM judge 必须同时判定攻击成功，evaluator 的正确性有 99.3% 的人工审计率——这是安全 benchmark 里少见的严格口径。但 85.0% 是**跨轮 best-of-K**：单轮 42.9%，随轮次升到 69.4 / 73.5 / 89.8 / 94.7，攻击者的目标函数本就定义在多轮最优上。所以它测的是"给定五轮自适应搜索预算，环境状态能否被改造到诱发不安全行为"，而不是"一次交互有 85% 概率出事"。模型间差距真实存在（Opus-4.8 最低 59.2 对 DS-V4-Pro 94.7），方差分解显示模型解释 73.6%、agent 实现 25.2%，且 agent 身份在模型与 benign 完成率之外还额外解释 7.6%（91.3%→98.9%）——**runtime 实现本身是独立的风险变量**，这一条此前无人量化。两处边界：其一，benign completion 与 ASR 未被解耦：pooled benign 完成率 87.38%，而 agent 维度上完成率最低的 Aider（70.74%）恰好也是 ASR 最低的（59.1），"不容易被攻破"与"本来就做不成事"在这份数据里分不开，论文提示了这一点并把 completion 放进方差分解，却没有给出只在成功完成 benign 任务的样本上计算的 completion-conditioned ASR（模型维度相反——Opus 完成率最高 96.18% 而 ASR 最低，这一侧更可信）；其二，充当 judge 的 GLM-5.2 同时是被测的五个模型之一，自评混淆未被处理，且全文无 Limitations 与 Ethics 节。

### 9.4 Open Problems

真正的 evolution-aware benchmark（联合追踪演化步数、能力、风险，覆盖四条路线且区分 model+harness 与模型本体贡献）仍然缺失。[[Papers/2608-AgentStream]] 关掉了其中一半——跨方法、跨底座、跨流结构的受控析因与统一的 evolution gain 定义都已就位——但只覆盖能力轴，风险与演化步轨迹仍在评测面之外。四个具体缺口：StuLife/SkillFlow 都定义了 forgetting/redundancy 指标却未报告数值；headline 分数与 harness/协议强绑定使跨论文比较失真；安全评测停留在 snapshot，无法捕捉 misevolution 的累积轨迹（§10.2）；以及**评测预算与目标效应量不匹配**——在每 benchmark 50 题 × 3 seed 的规模上分辨 1 个百分点量级的差异超出该协议的判别力，而这恰是当前多数自演化工作报告增益的量级。最后一条已有可操作对策：[[Papers/2607-HarnessBank]] 的配对 2σ crediting 与它测出的 62%–76% 幻觉进展率表明，判别规则应写进评测协议本身，而不是留给读者去猜哪个百分点是真的。安全轴上的缺口被 [[Papers/2608-OpenART]] 关掉了一部分——它给出长程有状态的风险传播刻画与跨 runtime 对齐的口径——但它测的是外部攻击者演化环境状态，被测 agent 自身全程冻结，因此"agent 自演化 N 步后风险如何变化"这条剂量-反应曲线仍只有 model 路线的约 200 步数据。

还有一条独立于样本量的缺口，它今年第一次被部分关上：**等价性主张比优越性主张更需要噪声带**。"压缩三成而分数不降"（[[Papers/2608-SkillZip]] 的 0.577 对 0.570）、"换个配置而能力等价"这类结论在形式上是要证明差值落在某个可忽略区间内，而单次运行、单点比较、无方差的报告方式在数学上无法区分"无差异"与"差异小于本协议的分辨率"。优越性主张还能靠效应量足够大自救，等价性主张不能——它的可信度完全取决于噪声带宽度是否被测量过。

这一格现在有了两个正面样本，且分别从两头做。[[Papers/2608-SkillZipPro]] 在实验前固定 −0.05 的等价边界，用 102 个 held-out 任务上的配对 bootstrap（10,000 次重采样）给出 +0.010、95% CI [−0.029, +0.059]，并据此判定自己是唯一保质量的压缩器——先声明边界再给区间，结论因此可证伪。[[Papers/2607-RethinkSkillEvolve]] 则直接把带宽量出来：字节完全相同的 skill 在 49 题 split 上重复评测 8 次标准差 3.92 点，100 题配对面板上重复部署三次能把 +2.3 变成 −2.0 / −3.0 / 0.0、把 −6.6 变成 +6.0 / +7.0 / +5.0。两者合起来把要求写实了——**报等价性要预先声明边界并给区间，报差值要给出同一协议下重跑同一份产物的带宽**，成本与 HarnessBank 的配对 2σ 相当。缺口因此从"无人做"收窄为"未成标配"：本文覆盖的其余等价性主张（含 SkillZip 自身那条）仍无一给出噪声带。同期的一条典型反面样本是 [[Papers/2608-PrimeAgent]] 对 nanoGPT speedrun 的结论——harness 选择对最终 record 的影响小于实验噪声——这句判断以散文形式给出，该节报告的是行为层的差异（Prime Agent 下每 100 次训练脚本执行有 7.6 次脚本外实验，Claude Code 下 1.2 次），未见与这条等价判断配套的噪声估计。

## 10. Safety, Reliability, and Failure Modes

演化不是免费的——misevolution 已从假设变为实证事实，且有从良性偏航到对抗投毒的完整谱系。

### 10.1 misevolution：从假设到实证

[[Papers/2509-Misevolution]] 在四条路径 × SOTA 系统上证明：不需要不安全数据、不需要外部攻击者，**良性反馈循环 + 有偏 credit assignment 就足以产生 safety 衰减与 reward hacking**；现有 mitigation（prompt 补丁/事后补训/静态扫描）全部只部分有效。四路径实测：AFlow 优化 20 轮后 ASR 54.4%→83.1%（Ensemble Node 级联放大）、memory 路径 deployment-time reward hacking >60%、工具创建-复用 Unsafe Rate 65.5%、自训练 safety 累积衰减。

### 10.2 负性结果：自改进可自退化

五篇独立工作从不同角度刻画自演化的失效条件：

| 工作 | 失效模式 | 关键机制/证据 |
|:--|:--|:--|
| [[Papers/2407-SelfImprovementReversal]] | self-improvement reversal | post-training 表面指标升但泛化/多样性降；评估协议为双轨解码 |
| [[Papers/2606-RiseAndCollapse]] | rise-and-collapse | 自改进先升后崩的失效轨迹；C10 GRPO-vs-REINFORCE 措辞已核 |
| [[Papers/2606-CodeSelfReviewCollapse]] | recursive self-training collapse | 用系统自身信号做 gate 会进入 rubber-stamp regime（等价于不过滤），Prop 2.1 给指数增长条件 |
| [[Papers/2609-Ecdysis]] | 演化跌破自己的起点 | 逐条失败改 harness 的基线与胜出方法同起点同协议，10 个 held-out 格平均 51.67→46.67，7 格绝对下降，Pass@3 66.00→63.50、Pass^3 37.00→29.00 |
| [[Papers/2607-RethinkSkillEvolve]] | 通过闸门的净负演化 | GPT-5.5–LiveMath 选中项 validation +5.7、robustness +8.3，而 released test −6.6、transfer −16.7；端到端口径下"演化后 test 更好"是 9/14，同时改善 robustness 与 transfer 是 7/14 |

后两行与前三行的差别在于失效发生的位置：它们都发生在闸门之后。Ecdysis 的 Self-Evolution 基线不是一个被削弱的对照——它与胜出方法从同一份人工 harness 起步、共享同一套训练评测与接受回滚协议，差别只在更新粒度（逐条失败改 vs 逐轮聚类改）——跑完之后仍在 held-out 上跌回起点之下，Pass@3 与 Pass^3 同向。这说明一道只要求训练集总分严格提升的准入准则并不阻止部署侧的整体回归（§6.2），而论文把这条结果当动机提了一句就没再回头。RethinkSkillEvolve 的净负案例出在另一处：选择协议本身是干净的（validation-only 选择，test 完全不参与），validation 与 robustness 两项都在涨，掉的是没参与选择的 test 与 transfer——闸门读到的指标与部署时要的指标不是同一个。

三处证据共用一种呈现形态：**聚合分数掩盖单元格上的净负**。Ecdysis 的 7/10 下降藏在一个平均值里，RethinkSkillEvolve 的 headline "11 个选中项中 9 个 test 更好"在 14 个端到端分母下是 9/14，[[Papers/2609-AgentGrad]] 的汇总表把两格一次更新也没被接受的运行算进一个正的平均增益（§5.5）。要让净负结果不被平均掉，报告里必须同时有逐格符号与端到端分母，两者都不是当前的默认口径。

CodeSelfReviewCollapse 对全 survey 的 gate 论证是关键约束：**self-review 式 gate 会退化为橡皮图章**——这直接质疑 MetaTeam 的 collective discussion、MemSkill 的 reward-only rollback 等 self-gate 设计能否抵抗 rubber-stamp。[[Papers/2607-MANTA]] 提供了这一命题目前唯一的分域实测：其 Auditor 与被审计的 task agent 共用同一底座（Gemma 4 31B，temperature 0），450 run 中 200 run 被 flag，聚合上未退化为橡皮图章；但分域看，PlanCraft 90 run 只 flag 出 1 次、MATH 只 2 次，在这两域上闸门实际近乎恒过，而 BrowseComp 恰好相反（83/90，恒不过）。同底座 self-gate 的失效并非只有"全过"一种形态，两端退化都会使 gate 丧失判别力——这是把 rubber-stamp 命题从二元判断细化为分域现象的第一个数据点。

### 10.3 benign misevolution 与 alignment tipping

[[Papers/2604-ExperienceSafetyRisks]] 证明即便经验完全良性、任务完全正常，experience-driven 演化也会引入安全风险（C3 的"Claude 全程最低"被推翻、修正为域依赖；C7 剂量图例 1/3/5/7/9 完整）——这是 misevolution 谱系的良性端点，风险被完整测量。[[Papers/2510-AlignmentTipping]] 刻画自演化把 agent 推离对齐的 tipping 过程（C2 解码设置已修正，并抓到论文内部矛盾：最陡降 r=2→3 vs Table 1 逐差）。

### 10.4 对抗性威胁：记忆与技能投毒

[[Papers/2512-MemoryGraft]] 是谱系的对抗端点：投毒记忆持久危害 agent。本文对其证据强度做保留标注（rating 2）——威胁模型自相矛盾（intro 声称的能力与 Appendix A 定义不一致）、PRP 定义的攻击缺随机基线（约 9%）、且证据实为 retrieval-level 而非其主张的 cross-agent transfer 级。与 ExperienceSafetyRisks（良性、完整测量）配对，构成 threat model 的两个端点：一端是无攻击者的良性偏航，一端是主动投毒但证据强度与主张不匹配。

[[Papers/2608-SkillJack]] 把攻击面从记忆推进到技能，且它攻的正是 §6.1 那条"经验→技能"的提炼管线：污染的不是技能库，而是喂给提炼器的轨迹。三个环节各有一处可测的失效。**其一，提炼这一步本身在漂白**：同一对检测器作用于 65 条被"框架化"（伪装成备份 / 归档 / 错误恢复等正当功能）的原始轨迹与由它们抽出的 264 条 skill，LLM judge 判恶率 98.5%→11.4%，正则 44.6%→11.0%。这个落差不能直接读成因果：65 条轨迹被拆成 264 条 skill，平均一拆四，分解粒度本身就会稀释每件制品里的恶意信号，论文自陈未隔离这一机制，而摘要仍以 "pipeline launders the attack" 的口吻陈述。更干净的一处证据来自第二个系统 Anything2Skill：它对直白恶意轨迹的抽取产出是 **0**，对框架化轨迹是 41.5%——这是抽取器行为的二元差异，混淆因素少得多。**其二，框架化措辞比直白措辞更能穿过提炼器**：SkillX 上框架化派生 skill 判恶率 11.4%、直白基线 27.0%，且框架化组 0/264 携带露骨恶意的 skill 名，直白组 20/241（8.3%）。**其三，技能通道买到的是存活率而不是命中率**：同一批 25 个配对任务下，投毒轨迹直接进上下文触发 68.0%，走 skill 通道只有 40.0%，而删掉源轨迹后仍有 32.0%——持久率 32.0/40.0 = 80.0%。方向值得注意：**直接注入更有效，绕道技能库反而降低命中**，攻击者从这条通道换到的是跨会话存活与更难检出。这条"删源后仍存活"在论文的形式化里其实是定义而非发现（skill 库与经验语料本就是两个存储），真正有信息量的是残余的 20% 去了哪里——若 skill 完全自足，这个数应当是 100%，论文未讨论，且 $n=25$ 时它只值 2 个任务。

三条边界必须与数字同时记，其中第一条是论文自己声明的。**全部触发率与 ASR 都是路由层的策略违规代理，不是实际被攻陷**——统计的是"agent 检索并选用了那条投毒 skill"，而非"危害真的发生了"，因此这些百分比不能与 §9.3 那类端到端 ASR 并列。第二，分母极小（多数 15–47），单次运行无重复。第三，抽取器、路由器、judge、agent 全部由同一个 DeepSeek-v4-flash 承担（约 3,047 次调用），轨迹是 150 条 AppWorld 格式的合成数据，所以"judge 判不出来"与"抽取器造得出来"共享同一个模型的盲区。

一个跨论文的形态由此浮现：MemoryGraft 的证据实际停在检索层，SkillJack 的证据自陈停在路由层，而两篇的指标名称都写在攻击成功层。**这条攻击链上目前还没有一篇工作把危害后果本身测出来**——现有证据支持的是"投毒物能被检索/被选用且能存活"，不支持"因此造成了 X 比例的实际危害"。

### 10.5 threat model 与放大结构

[[Papers/2606-MLASSelfEvolvingSafety]] 用模块 × 演化阶段矩阵系统化 multi-agent 自演化的攻击面，抓到三处论文内部数字不一致（17/7/1 vs 五档图例、3.5x vs 2x、2.5% 错置，均记于 Paper 笔记）。其价值在指出放大结构：单点错误经 shared scaffold / constitution 变为 lineage-persistent 的全队污染。

MLAS 的 lineage-persistent 至此还只是框架层断言加案例，[[Papers/2608-SkillJack]] 给了它第一次直接测量：其 Commit 阶段 × Cognitive Resource 那一格对应的正是"删掉源经验后派生技能仍存活"，实测 80.0%（§10.4）。它还补上了 MLAS 没有的另一半——**在持久化的同时可检出性单调下降**：轨迹层 98.5% 判恶、skill 层 11.4%，来源标记在跨层提升中不被保留。两条合起来把工程结论收得很紧：**provenance 必须随派生制品传播，撤销必须覆盖后代**。这条结论不依赖 SkillJack 的任何一个数字，只依赖"技能库与经验语料分离存储"这个架构事实，而该事实在所有 experience-to-skill 系统里都成立——包括 §6.1 的 SkillOpt/SkillClaw 与 §6.3 的 SESA。

这条工程结论已有一个部分实现，且它不在技能层。[[Papers/2608-PrimeAgent]] 的 Continual Harness 把四类持久状态（prompt notes、memories、skills、subagent specification）做成版本化条目，每次 refinement 在 turn boundary 落地并记录触发它的事件与预期效果，版本保留 provenance 并支持 rollback，模型权重全程不动。撤销一次演化编辑因此是运行时的一个操作，而不是重建一遍状态。它关上的是**撤销单条资产**这一半：留下的是**撤销其后代**——该机制作用在条目自身的版本历史上，而上一段那条失效发生在跨存储的派生关系上（源经验被删，由它抽出的技能仍留在技能库里），论文既未描述删除是否沿派生链传播，也未报告任何血缘查询实验。结论应改写为：版本级撤销已有实物，派生级撤销仍无。

攻击面还有一层此前未被列入 MLAS 矩阵的：**环境状态**。[[Papers/2608-OpenART]] 的攻击者不改指令、不改模型、不改评判标准，只演化 agent 能看到的 workspace 文件、工具返回、memory 与 plan state，八个 target 可见向量里每一个单独使用都能把 Strict ASR 推过 50%（其余七个均值 71.2%，仅 workspace 一项 92.5%）。它归纳的三类反复出现的失效对自演化系统尤其贴切，因为三类都以"复用先前判断"为前提：过期假设未被作废、安全判断被沿用而非在新状态下重算、以及若干单步安全的动作在组合后产生危害。自演化系统的产物——技能、记忆、harness patch——本身就是"过去某个上下文里成立的结论"被固化下来的形式，且被设计为反复取用，因此这三类失效在演化系统上的暴露面比在一次性 agent 上更大。

### 10.6 gate 作为可靠性来源

综合 §6.2 与 §10.2：演化步 gate 在性能回归维度已有实证方案（GRASP 编辑级、SKILL.nb 步骤级、[[Papers/2607-HarnessBank]] 的 harness patch 筛选级），统计与形式化方向有 SEACertificates/SEVerA，但**安全维度 gate 与 self-gate 的 rubber-stamp 问题（CodeSelfReviewCollapse）仍是硬约束**。已被测量到的 gate 价值集中在防回归、拦假精英与收敛效率上，天花板贡献在存在冗余部署选择器时为零——把 gate 当作可靠性组件论证站得住，当作性能组件论证目前只有一处实测支持而那条记录缺核验（§6.2）。task-agnostic、抗橡皮图章、可第三方审计的 gate 仍是可靠性的核心未解问题：目前最外生的实例只在判决算法一层做到外生，证据来源（patch 自报 activation beacon）与打分器（judge 模型未指明）两层仍未审计。

证据来源层的问题比"未审计"更重一档：**它是攻击者可控的**。[[Papers/2608-SkillJack]] 的元数据消融显示，LLM judge 在只看代码时判恶率 36.7%，补上 skill 的 name 与 documentation 后降到 10.0%——而 name 与 docstring 正是由抽取器根据（可能被投毒的）轨迹生成的字段。于是"给 gate 更多上下文"这个看起来无害的设计选择，实际是把安全决策的权重压在攻击者写得出的表层描述上。可直接转成设计规则：**准入判据只读行为与代码，不读名称与描述**。同一逻辑作用于 §6.2 的 HarnessBank：activation beacon 由 patch 自己发出，与 skill 的自述文档在结构上是同一类自报证据。需要如实标注该实验的边界——它是单模型（DeepSeek-v4-flash）自评，换一个非同族 judge 是否仍出现"看得越多判得越松"未被检验，这个对照的成本在数百次调用量级。

闸门误判的代价有多大，取决于系统把判决结果存到哪里。[[Papers/2609-RSIAgent]] 给出这条通路的完整形状。它的 verifier 由一个与 actor 不同族的模型承担，跑在隔离 context 与 checkpoint 保护的环境副本上，看不到 actor 的私有推理与记忆，边界设计在本文覆盖的工作里属于最干净的一档；但它的准确率全文没有任何量化，既无与官方 rubric 的一致率，也无人工抽检比例。作者自己的失效分析写清了后果链：探索没打到真正出问题的决策 → verifier 在字段值无依据、产物与官方 rubric 不符时仍返回 PASS → actor 把这条被误判通过的规则（把"缺失数据标记"当成有效答案）蒸馏进记忆，后续 run 继续复用它。**判决错误在演化系统里不是一次性损失，它以持久资产的形式留在系统内，并在此后每次检索时被重新执行**，所以闸门的 precision 起的是乘数作用，决定的是错误的累积速率而不只是单轮的通过率。该篇对失效子类给出了计数，但按其自陈计数取自 selected case audit 且同一案例可计入多个子类，据此估不出误判发生率。这与 §10.5 的撤销缺口是同一件事的两端：误判率未知，而误判的产物无法被追溯作废。

### 10.7 演化产物编码的是环境规程

前面几节的失效都以分数下降或安全属性退化为表征。还有一类方向相反：分数照涨，但涨的来源是对评测环境本身的适应而非任务能力。它能穿过任何只看分数的闸门，因为闸门读到的正是它在优化的那个数。

[[Papers/2607-RethinkSkillEvolve]] 提供了最细的一次解剖。全文唯一无争议的大幅提升是 SpreadsheetBench 三模型的 +28.8～+37.7，而这批技能保留下来的指导内容是"用 openpyxl、dual loading 验证、write–reopen–check、marker-aware 行删除"这类 API 使用规程；唯一被展示全文的那条技能里写着一句 sandbox 专属 workaround——在 `import openpyxl` 之前把 `/tmp` 从 `sys.path` 过滤掉，以绕开该评测环境特有的 RuntimeError——而按其附录，这条 workaround 被引入的那一轮本身就建立了一次 validation new best（69.2→74.4）。55 个字节互异的 validation best 里，至少有一个的实质内容是修一个导入路径的坑。两个旁证与这个读法一致：从同一 parent 技能反复采样补不回这条增益，而它的 transfer 在分布偏移 tier 上从 +52～+53 塌到 +2.9／+3.5。换一套 harness 或 sandbox 之后这部分收益是否还在，论文没有测，只能作为假设记下。

同一形态在两个互不相关的系统上各出现一次。[[Papers/2608-PrimeAgent]] 的一条 Factorio 轨迹里，agent 发现可以经 RCON 直接向 assembly machine 注入资源，在环境挂着 anti-cheating heartbeat 的情况下仍然使用了它，并把它保留成一个可复用 skill——没有攻击者、没有不安全数据，一条绕过环境规则的捷径被演化机制按正常流程收为资产。[[Papers/2609-Ecdysis]] 的 AgentBench 结果是另一端：w/ FDCR 在五个模型上给出完全相同的 90.00／90.00／90.00，AVG = Pass@3 = Pass^3 意味着每个模型都在同一批任务上三次全对、在另一批上三次全错，而这五个模型从 Direct 只有 5.00 的 Llama-3.1-8B 跨到 230B。最自然的解释恰是该文自己诊断逐条演化基线时用的措辞——把某个训练任务的答案提升成了通用运行时约束——论文对这组数字零评论。这是推断而非实测，可证伪的检查很便宜：读一遍演化后的 harness，看有没有任务特定的常量或分支。这一块占了它 headline 平均增益的三分之一。

治理这类失效的要求与 §10.4 的投毒不同。投毒需要一个攻击者，而这里只需要一个把分数当目标的闭环；它也不会被 §6.2 的任何一种闸门拦下，因为环境规程在训练与验证分布上确实提升分数，闸门读到的信号是真的。可用的判别手段不在闸门里而在报告口径上：把增益按"能力 / 环境规程"分类需要读演化产物的文本，而多数工作不发布产物；跨 harness 或跨 sandbox 复现是另一个直接检验，未见有工作报告过。

## 11. Open Challenges

- **Longitudinal evolution-aware 评估**：当前 safety/能力评估全是 snapshot-based，无 benchmark 追踪"演化步数-能力-风险"联合轨迹；剂量关系目前仅 model 路径有 200 步数据。
- **抗 rubber-stamp 的演化步 gate**：self-review 式 gate 会退化为橡皮图章（CodeSelfReviewCollapse），需要 exogenous、task-agnostic、可审计的验证。gate 谓词自身的 precision 目前只有一处数字，且是同底座自评的**触发**闸门而非验收闸门（[[Papers/2607-MANTA]] 总体 precision 0.38 / F1 0.47，分域从近乎恒过到近乎恒不过）；外生校准与 process flag 的人工标注精度均未见。[[Papers/2607-HarnessBank]] 把判决算法层做到了目前最外生的形态（确定性配对统计量 + 独立 evaluator + evolver 与 task agent 不同家族），但同时暴露出"外生"是分层的：证据来源层由 patch 自报 activation beacon 且无人审计该声明是否名副其实，打分器层在部分域直接是未指明模型的 LLM judge；该篇也未报告 gate 的误收/误拒率，只有个案。三层里最脆弱的是证据来源层，因为它不只是未审计而是**攻击者可控**：[[Papers/2608-SkillJack]] 测到 judge 只看代码时判恶 36.7%、补上攻击者撰写的 name 与 documentation 后降到 10.0%，而这两个字段恰是多数 skill 准入闸门与检索器的主要输入。[[Papers/2608-EvoHarnessRL]] 给出该三层框架的另一种缺失形态：判决者是外族的 Claude Opus，判据却只是它阅读 agent 自写 note 加 LFU 频次，没有任何 held-out 回归检查——判决者的独立性不自动传递给判据。[[Ideas/HybridVerifier-GUIRuntime]] 正针对 GUI runtime 的 hybrid（deterministic state-contract + 学习式）verifier gate 这一缺口。
- **credit assignment 的信号质量**：RSI 谱系瓶颈从"如何自改"转向"如何选 parent"（HGM CMP 0.778 vs DGM 0.285）；五类替代信号（clade 聚合 / 结果的辅助统计量 / 多因子固定权重效用 / 纯过程审计 / 逆序干预定位）尚未在同一 testbed 上对照。multi-agent 的 per-agent 归因不再只能靠讨论涌现：[[Papers/2609-AgentGrad]] 的逆序 hint 注入给出第一个算法化方案，但它成立的前提是存在一个可替换进去的正确输出，因此覆盖的是"流水线结构固定 + 终点可自动判"这一象限，开放式协作与共识域仍无算法（§7.3）。
- **演化增益的预算与来源归因**：多数工作报告的是"演化机制 + 额外资源"的联合效应而把结论写成前者——[[Papers/2607-MANTA]] 的 mutation 增益与 +28K token 同时上线（缺同拓扑再跑一轮的对照臂），[[Papers/2607-FrontisMA1]] 的 post-training 增益与外部更强 teacher 的蒸馏成分未分离（缺 no-teacher 臂）。第三种形态是**演化组件自身未被隔离**。[[Papers/2608-RoMeRL]] 的四个记忆坐标里只有一个用到学到的 Q，却没跑 $\omega_Q=0$ 的纯启发式臂；[[Papers/2608-EvoHarnessRL]] 的消融只做在冻结的 inference-time harness 上（换它的配置），从不存在"同样 SFT+GRPO 但去掉 BPE 动作"的臂，而它自己的动作统计显示 harness 调用退火到约每 episode 一次、其 SFT 教师纯 ReAct 已达 96.4，两种归因都与数据相容；[[Papers/2607-SESA]] 跑了关库对照并因此发现技能库的部署期贡献只占总增益的两三成（§6.3）。第四种形态更隐蔽：**演化组件被系统内另一个冗余机制替代**——[[Papers/2607-HarnessBank]] 的 2σ gate 被去掉后天花板 ±0.0，因为训练集 argmax 这个独立的部署选择器已经选中了同一个赢家；报告 gate 收益的工作若不把 selector 也消融掉，记在 gate 账上的功劳无法与 selector 的分开。四种形态共用一句诊断：**报出的是联合效应，写下的是单一归因**。equal-budget paired replay、teacher-ablation、关掉待验组件再跑一遍、固定判决规则换掉最终选择器——四个补法的成本都远低于原实验，缺席本身就是信号。
- **效应量与噪声的口径**：多数增益报告是单次运行、无方差、无显著性检验，而唯一做过重复部署的工作给出的不可判区是 ±3 点（同一 100 题配对面板三次重复；字节相同的技能在 49 题 validation split 上跑 8 次 SD 3.92），落在这个区间内的 headline 条目按其自身数据不可判（[[Papers/2607-RethinkSkillEvolve]]）。等价性主张的要求更高一档：说"压缩后质量不变"需要一个预先声明的噪声带，目前只有一处给出（[[Papers/2608-SkillZipPro]] 预先固定 −0.05 margin，102 held-out 任务配对 bootstrap 得 +0.010、95% CI [−0.029, +0.059]），其余等价性主张一概没有（§9.4）。
- **增益的内容归类**：演化产物记下的可能是环境与 API 使用规程而非任务能力，这类增益在同一 sandbox 内真实、跨 harness 大概率不复现——一条 sandbox 专属的导入路径 workaround 就足以建立一次 validation new best（[[Papers/2607-RethinkSkillEvolve]]），更极端的形态是把训练任务的答案编成运行时约束，或把绕过环境规则的捷径收为可复用技能（§10.7）。判别只需两件事：发布演化产物、换一套 harness 复现一次，两者目前都罕见。
- **operation-level 演化的安全性**：memory 演化从内容升到操作（MemSkill）后 blast radius 放大，但无安全评估。
- **演化资产的维护与撤销**：技能库、记忆库、harness patch 是被长期持有的资产，而所有演化算子都只管生产不管维护。两个后果已被分别测到：体积上，演化五轮后技能文档膨胀约 5.2×、十六轮 2.5–3.7×，且晚接入压缩只能部分挽回（[[Papers/2608-SkillZip]]）；血缘上，派生技能在源经验被删后仍有 80.0% 存活，来源标记在跨层提炼中从 100.0% 掉到 44.4%（[[Papers/2608-SkillJack]]）。两者是同一件事的两面——**资产被创建时携带的上下文（它为什么存在、从哪来、何时应作废）没有被任何机制保留**。缺的具体机制有三：带血缘的撤销（删掉一条经验须能追溯并作废其全部后代）、语义冗余度量（长度已可测，"两条技能是否在做同一件事"仍无度量）、以及作废条件（一条技能在什么条件下应被判定过期，而不是等它在某次任务上失败）。第一项已有一个部分实现：[[Papers/2608-PrimeAgent]] 的版本化持久 harness 状态保留 provenance 并支持 rollback，使撤销一次演化编辑成为运行时操作，缺的那一半是跨存储的派生传播（§10.5）。冗余侧出现的是一个相邻但不同的口径：按 catalog / activation / path / deployment 四层成本分开记账，并要求每次删除携带一个 witness（字面包含、确定性覆盖、或冻结 checker 的 entailment 判定），把"能删多少"变成"证据有多强"的函数（[[Papers/2608-SkillZipPro]]）；它测到的仍是文本级重复——演化库每轮新增内容 55%±3% 与既有文本重叠、可移除份额从第 2 轮的 29% 升到第 15 轮的 53%——而"两条技能是否在做同一件事"仍无度量（§6.4）。
- **co-evolution 的验证空白**：并非无人演化 verifier——[[Papers/2608-CoEvolutionSurvey]] 记录的 Stage 2 feedback-space 分支（演化 reward 候选、演化 unit test、按建议是否改善 policy 更新 critic）整支都在做这件事——而是**无人验证演化后的 verifier**：这些工作对演化后判分器的唯一背书是下游任务性能，而下游性能正由该判分器给出。最小对照是保留一个冻结的 held-out verifier 做跨代复评，库内无人做过。multi-agent population 稳定性、合谋、集体 misevolution 亦无实证。
- **优化产物可迁移性**：文本级经验资产跨 backbone 可迁移（KnowAct 正例 +3.1pts），但跨演化阶段迁移反而失效（SEED 静态 library −7.4）。[[Papers/2607-HarnessBank]] 给出目前最清楚的机制刻画：演化产物是针对特定底座失败模式的 correction 而非普适更优配置，迁移成立与否由 pathology 是否匹配决定——AppWorld 上匹配的 patch 给 +15.4、错配只给 +1.2，Omni-MATH 上两代同族模型共享同一失败模式因而几乎无损迁移（+11.7 → +11.0），而把同一杠杆反向拧错叠在演化后的 harness 上是 −15.7，即有害而非中性。[[Papers/2608-AgentStream]] 从方法层给出同向但更弱的证据（最优方法不跨底座保序），其方法间 spread 在两个较强底座上只有 0.9–2.0 点、落在噪声量级。可迁移性的刻画因此从"能不能迁"细化为"失败模式是否同构"，但除 HarnessBank 外无第二处受控证据，也没有任何工作事前预测过匹配与否。一处间接线索指向"压缩方式影响迁移性"：[[Papers/2608-SkillZip]] 在 LiveMath 上报告其压缩产物的跨模型保留率 0.97、评测驱动压缩（SkillReducer）产物 0.91，差距集中在 off-diagonal（技能被移到非产出它的底座上），可能的解释是评测驱动压缩会保下与评测时底座耦合的部分——但这只有一组数字、无方差，只能作为待检验的假设。
- **自演化增益的存在条件**：跨方法受控析因显示增益既不普遍也不稳定——45 个计数单元里 11–17 个跑输不演化的同一模型，方向随底座能力非单调，且成本-收益比同样由底座决定（[[Papers/2608-AgentStream]]）。论文把成因归给 bootstrap loop（solve rate 低则经验流被失败轨迹主导），但这是事后解读而非受控结论。把"能力 gate"改写成可操作的"经验质量 gate"只需一个实验：固定底座与方法，按成功/失败比例控制注入 state 的轨迹构成，看增益如何随之移动。在这个实验做出来之前，"在哪些条件下该上自演化"仍是一个没有答案的部署问题。同向的单篇证据来自 [[Papers/2608-EvoHarnessRL]] 的 frontier block——同一 harness、同一 benchmark、只换底座：ReAct 47.9 的 GPT-4.1 得 +22.1，60.7 的 GPT-5 得 +25.7，而已经 96.4 的 Claude Opus 4.5 只得 +2.1，且 Opus 的 Heat 一族从 100.0 掉到 93.8。**增益与基线质量负相关，且在已近饱和的轨迹上净效应可以为负**，这给"能力 gate"提供了一个家族级的具体实例（该篇 +25.7 与表内 85.0−60.7=24.3 算术不一致，其余 Δ 自洽）。
- **Risk awareness 的灾难性遗忘**：SEAgent 演化后完全丧失拒绝/避险能力，安全能力遗忘动力学未知。

## 12. Discussion and Conclusion

自演化领域在 2026 年从"能不能演化"进入"演化会不会坏、如何 gate"的阶段。五个跨论文的判断浮现，其中第二个已由方向相反的两组实测从共识降级为条件性结论：

其一，**反馈信号的可验证性是四条路线共同的成败分界**，verifier 质量上界决定 self-evolution 收益上界——deterministic 域（代码/几何）最稳，internal/共识域收益真实但劣化可测。2026 下半年出现的新 move 是把可验证性当作**可设计**而非固有的属性（[[Papers/2607-SpyRL]] 的 RLSVR：向环境注入隐变量、让 agent 在被它条件化的观测上执行原任务、再核对一个关于该隐变量的问题）。这个 reframing 简洁、与 GRPO 正交、原则上可迁移到任何 RLVR-hard 的域，值得跟踪；但其唯一实例同时说明负担是被转移而非消除——塑造生成质量的那一项 reward 仍由被训练的模型自己扮演 judge 投出，在开放式生成上整体没能越过强 rubric-judge 基线。判据没变：**收益上界仍由那个真正塑造行为的信号有多可信决定**，构造式可验性改变的是这个信号的成本与来源，不是它的性质。可验证性之外，这条轴上出现了一个正交属性：**信号的分辨率**。当一组 rollout 全部失败时二值 reward 在组内退化为常数（$\hat g_{\mathrm{RL}}=0$），可验证性完好而梯度为零，[[Papers/2608-ZerothOrderSelfEvolve]] 与 [[Papers/2608-ROPSD]] 从两个方向填这个真空——前者用参数空间扰动配 gold-answer 连续似然，后者把反思文本转成 token 级优势——并在各自域上取得该 survey 中最大的一批相对增益（GAIA 23.3→47.5；GUI grounding 50.2→57.6，而同期基于二值 reward 的 GUI-RCPO 在同一 benchmark 上是 −0.3）。代价是**标注需求被转移而非消除**：一个需要短答案，一个需要预训练好的反思器，两者都要求域里存在便宜的可核对物（§4.5）。

其二，**gate 是可靠性组件；它是否同时是性能组件，取决于 gate 之外有没有一个冗余的部署选择器**。两处证据台账齐备的自身消融把已测得的 gate 价值统一定位在地板与效率轴——[[Papers/2606-SkillNb]] 去 gate 只掉约 6 分成功率而修复后回归从 3.3% 爆到 18.6%，[[Papers/2607-HarnessBank]] 去掉 2σ 判据天花板 ±0.0 而假精英 0→2、收敛轮数 10→>20，其解释是训练集 argmax 这个独立选择器已经选中了同一赢家。方向相反的唯一实测来自 [[Papers/2605-GRASP]]（去闸门 88.8%→63.5%），其结构差别在于闸门本身即部署决策、没有下游 argmax 兜底，而该侧记录缺证据台账与核验状态。因此这条判断应按条件陈述而非作为共识引用，正反两侧一并记录（§6.2）。此外现有实证 gate 只覆盖性能回归、依赖任务可复现结构，且 self-review 式 gate 会退化为橡皮图章——抗 rubber-stamp 的 task-agnostic 安全 gate 是领域中枢缺口。一条新路径是把演化信号与评价信号从结构上切开（只用不接触结果的过程审计驱动演化），它免疫"闸门其实就是打分模型"的循环，代价是信号弱且分域极不稳定，且这条代价目前只被测量过一次。

其三，**recursive self-improvement 在现有证据下有界**：scaffold 层受 frozen FM 天花板约束，weight 层受 reversal 约束，谱系的下一步瓶颈已从"改法"转向"选法"（credit assignment 信号质量）。misevolution 从假设变为跨系统实证事实，且威胁谱从无攻击者的良性偏航延伸到主动记忆投毒。领域叙事仍普遍超前于实物——满足严格自演化判据（经验依赖 + 持久策略改变 + 自主探索）且部署后持续演化的系统，目前极少；以 RSI 为题而实际做到 generation ≥2 的，库内一篇也没有。目前最完整的一套开放栈（[[Papers/2607-FrontisMA1]]，六件 artifact 齐全）只训练到 generation 1，其价值在于把"缺哪些 ablation"从必须相信作者变成别人可以补的实验，而不在于把递归做出来；[[Papers/2608-MacaronV1]] 是同一形态的第二个样本，其三段循环只跑通中间一段，作者自己把持续学习是否复利列为未验证的开放问题。同一篇也把"frozen FM 天花板"拆成两个不同的量：一个配置服务全部任务时是 11/122，允许每个任务用自己最合适的配置时累计覆盖 122/122，且后者不更新任何权重——此前归给"基座能力不足"的失败里，相当一部分是 elicitation failure。但累计覆盖来自 450 次尝试的并集，不是可交付的单一配置，能承重的只是"两者相差一个数量级"这一事实本身（§7.4）。

其四，**自演化的增益不是普遍属性，而是与底座能力、任务流结构、失败模式匹配度耦合的条件性收益**。首个跨方法受控析因在 5 方法 × 3 底座 × 3 种任务流的 45 个计数单元里测到 11–17 个跑输不演化的同一模型，增益随底座能力非单调，最优方法不跨底座保序（[[Papers/2608-AgentStream]]）；机制侧的同向证据来自 [[Papers/2607-HarnessBank]]——演化出的 harness 是针对特定底座失败模式的 correction，匹配时 +15.4、错配时 +1.2、反向叠加时 −15.7。两者合起来意味着"某方法带来 X 点提升"这类跨论文引用在缺少底座与流结构限定时没有意义。证据强度需与结论分开记：前者的效应量普遍小于其自身的 seed 间标准差且全文无显著性检验，可承重的是形态不是数值；后者单次运行、无方差报告。第三处同向证据把"底座能力 gate"落到了家族级：同一 harness 换底座，ReAct 47.9 的 GPT-4.1 得 +22.1、60.7 的 GPT-5 得 +25.7、已达 96.4 的 Claude Opus 4.5 只得 +2.1，且 Opus 在 Heat 一族上从 100.0 掉到 93.8（[[Papers/2608-EvoHarnessRL]]）——增益与基线质量负相关，在已近饱和处净效应可以为负。

其五，**演化产物是需要治理的资产，而现有工作只造不管**。这一条在四个互不相关的切面上同时显形：体积上，技能文档随演化轮次单调膨胀（五轮约 5.2×、十六轮 2.5–3.7×），而没有任何演化算子承担压缩职责，晚接入的压缩也无法完全撤销已固化的冗余（[[Papers/2608-SkillZip]]）；血缘上，派生技能在源经验被删后仍有 80.0% 存活，且来源标记在跨层提炼中大量丢失，使"撤销一条坏经验"在工程上不可实现（[[Papers/2608-SkillJack]]）；时效上，长程工作流里最常见的失效正是过期假设未被作废与安全判断被沿用而非重算（[[Papers/2608-OpenART]]）；内容上，被保留下来的常常是环境与 API 使用规程而不是任务能力——一条 sandbox 专属的导入路径 workaround 就建立过一次 validation new best，而同一批技能的 transfer 在分布偏移 tier 上从 +52～+53 塌到 +2.9（[[Papers/2607-RethinkSkillEvolve]]）。四者指向同一个结构性缺失：**资产被创建时的上下文——为什么存在、从哪来、在什么环境里成立、何时应作废——没有被任何机制保留**，而自演化系统的全部价值恰恰建立在复用这些资产上。这条比前四条更接近工程可动手的位置：带血缘的撤销、冗余度量与作废条件都是明确的待建组件，且都不依赖新的理论；第一项已有一个版本级的部分实现（[[Papers/2608-PrimeAgent]] 的版本化 harness 状态保留 provenance 并支持 rollback），缺的是跨存储的派生传播。证据强度须一并记：四处各自单篇、无方差，SkillJack 的数字还只是路由层代理量，可承重的是这几件事的缺席，不是任何一个具体百分比。

## Key Evidence Matrix

下表登记进入 Overview / §7–§10 / Open Challenges 的高影响 claim，标注 state（source-verified / 跨来源收敛 / 作者综合论断 / 库内暂无独立验证）、locator 与边界。07-24 重排时经独立 verifier 核验的 claim 标 [本轮核]，其后各轮并入的行按并入日期标注。

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
| 全失败 rollout 组内二值 reward 退化为常数（$\hat g_{\mathrm{RL}}=0$）；ZO 用 instance-specific LoRA 扰动 + gold-answer token-normalized NLL 绕开，50 个难例上 first-order 7 / RL 16 / ZO 23 | source-verified [09-07 并入] | [[Papers/2608-ZerothOrderSelfEvolve]] Sec 3.1 (Eq. 7) / Table 6 | 信号"分辨率"与"可验证性"是两条正交属性；连续损失依赖 gold answer 存在，标注需求被转移非消除；304 训练例中 237 为难例（baseline Pass@1 仅 22.0%）；单次运行无 seed |
| ZO 深研 QA 结果：GAIA 47.5%（ReAct 23.3 / WebDancer 31.0 / SimpleDeepSearcher 36.9 / ARPO 38.8）、WebWalkerQA 34.8%（15.5）；难例轨迹 SFT 28.3 vs 初始轨迹 20.4 | source-verified [09-07 并入] | [[Papers/2608-ZerothOrderSelfEvolve]] Table 1 / Table 2 | 对照同 backbone 家族与同系统配置（搜索 API、解析器、解码、工具预算）；域限定在短答案可精确匹配的深研 QA；代码开源且仓库可访问 |
| ROPSD 把反思文本转成 token 级优势：条件化 self-teacher 与无条件 policy 的 log-ratio；六 benchmark 均值 50.2→57.6（+7.4），同设置 GUI-RCPO 负迁移 −0.3 | source-verified [09-07 并入] | [[Papers/2608-ROPSD]] Abstract / Table 1 / Eq. 5 | test-time transductive 适应，任务流由 benchmark 给定、单步 grounding，纳入本 survey 属边界情形（笔记归属 `Topics/CUA-Survey`）；Reflector 需 ~10,160 对 GroundCUA 标注数据预训、test-time 冻结（held-out 89.5%/91.7%）；代码"将发布"无 URL |
| ROPSD 稳定化部件是前提而非增益：无 reflection 或无 Contrastive Calibration 均致灾难性 policy collapse，加上后 MMG 达 64.3；CC 使初始错 token 优势 −0.97 vs −0.39、漂移末端 0.0033 vs 1.34 | source-verified [09-07 并入] | [[Papers/2608-ROPSD]] Table 2 / Fig. 3-4 | 与 SpyRL 的 RAE 消融同型（§4.5）：优化侧设计缺一件就跌破起点；单次运行、无 seed |
| EvoHarnessRL 把 harness 使用变成可训练动作（track/commit/recall/note 与环境动作共享 $T_{max}=70$）：ALFWorld seen ReAct 47.9 → RL 96.9（+49.0），unseen 50.0 → 86.6 | source-verified [09-07 并入] | [[Papers/2608-EvoHarnessRL]] Table 1 / Table 3 | 无"同 SFT+GRPO 去 BPE"对照臂（最近的 standard GRPO 65.6 同时缺 SFT）；96.9 的策略本身无组件消融；无 seed / 误差棒 / 显著性 / token 配平 / Limitations；ALFWorld 95%+ 数字跨论文不可比，split 家族计数未披露（Base 家族均值 54.65 ≠ 正文 56.4） |
| EvoHarnessRL 底座梯度：同 harness 下 ReAct 47.9 的 GPT-4.1 得 +22.1、60.7 的 GPT-5 得 +25.7、96.4 的 Claude Opus 4.5 仅 +2.1 且 Heat 100.0→93.8 | source-verified [09-07 并入] | [[Papers/2608-EvoHarnessRL]] Table 1 frontier block | 增益与基线质量负相关的家族级实例，与 AgentStream 的能力 gate 同向；原文 +25.7 与 85.0−60.7=24.3 算术不一致（其余 Δ 自洽）；单次运行 |
| EvoHarnessRL 技能库判决"者外生而据缺失"：增删改由外部 Claude Opus consolidation model 在 epoch 边界执行 + LFU，无 held-out 准入判据；GRPO 后 harness 调用退火到约每 episode 一次，recall 最持久、commit/note 近零 | source-verified [09-07 并入] | [[Papers/2608-EvoHarnessRL]] 附录 9 / §4.1 Fig.3 | gate 独立性三层（§6.2）的第二个样本，与 HarnessBank 互补；附录 case study 有错误先验入库但无污染率，RoMeRL 的 null 化探针可测而未测；Claude Opus 同时是 SFT teacher |
| Macaron 把 policy 写成 $\pi_\phi(a \mid o;\theta,c)$ 并分离权重更新与配置搜索：122 个冻结基座全挂（0/122）的 TB2.1 派生任务上，零权重更新的自适应配置搜索（69 job / 450 attempts）累计覆盖 122/122，而最强单配置全集 sweep 仅 11/122 | source-verified [09-07 并入] | [[Papers/2608-MacaronV1]] Section 3.2.5 / Table 4 / Fig 7 | 把"frozen FM 天花板"拆为操作天花板（11/122）与激发天花板（122/122）；累计覆盖是 450 次尝试的并集、非可交付单配置，接近 pass@450 的重参数化；无事前选配置的机制 |
| Macaron 只跑到 generation 1：MindForge 三段循环（Discovery → Expansion → Update）仅 Expansion 有报告，作者自列持续学习复利与集体智能为未验证 | source-verified [09-07 并入] | [[Papers/2608-MacaronV1]] Section 3 / Section 6 | RSI 术语与实物错位的第二个样本（前一个为 Frontis-MA1）；router 99.12% 在训练 trace 上、非 held-out（C2）；Vita 三臂 0.636±0.026 / 0.650±0.030 / 0.632±0.019 作者明示不构成等价性；ChatBench judge 为与 base 同族的私有 GLM-5.2 |
| SkillZip：SkillOpt 演化 5 轮后 skill 膨胀 5.6×/3.1×/6.7×（均值约 5.2×）；typed MDL + 硬覆盖约束做零 rollout 压缩，压缩率 31.2% vs SkillReducer 9.2%，macro 0.577 vs 0.570（未压缩）/ 0.544（SkillReducer），286 s / 3.5× 提速 | source-verified [09-07 并入] | [[Papers/2608-SkillZip]] Fig. 4 / Table I / Table II | "压缩无损"是等价性主张而证据是单点比较：无 seed、无方差、无等价性检验，0.007 的差落在库内已知 seed 波动（3–6pp）之下；Prop IV.1 的稀有规则保留是相对 typed 解析器而言；四操作与硬覆盖无分项消融；无公开代码 |
| SkillZip 的 Zip-on-Write 有路径依赖：16 轮膨胀 2.5×/3.1×/3.7×，round-1 起启用封顶 1.6×–1.9×（降 38%–50%）且无精度损失，round-8 才启用仅部分恢复（2.6× vs 1.9×）；LiveMath 跨模型保留 0.97 vs SkillReducer 0.91，差距在 off-diagonal | source-verified [09-07 并入] | [[Papers/2608-SkillZip]] Fig. 5 / Fig. 6 | 冗余一旦固化无法完全撤销，压缩须与演化同期启用；跨模型保留差异是"评测驱动压缩绑定评测时底座"的间接线索，单组数字无方差，仅作假设 |
| SkillJack：投毒轨迹经 experience-to-skill 提炼后 LLM judge 判恶率 98.5%→11.4%（正则 44.6%→11.0%）；框架化 11.4% vs 直白基线 27.0%，恶意 skill 名 0/264 vs 20/241；删源轨迹后派生 skill 持久率 80.0%（32.0/40.0） | source-verified [09-07 并入] | [[Papers/2608-SkillJack]] §4.2–4.5 / Table 2 / Fig. 3 | **全部"攻击成功"是路由层 policy-violation 代理量，非真实执行**（论文 C10 自述），不可与端到端 ASR 并列；98.5→11.4 存在未排除的分解粒度混淆（65 轨迹 → 264 skill），更干净的证据是 A2S 对直白恶意抽取产出 0 / 框架化 41.5%；分母 15–47、单次运行；抽取器/路由器/judge/agent 同为 DeepSeek-v4-flash；matched 设定下直接注入 68.0% 高于走 skill 通道 40.0%——技能通道换来存活率而非命中率 |
| SkillJack 元数据消融：LLM judge 只看代码判恶 36.7%，补上攻击者撰写的 name 与 documentation 后降到 10.0% | source-verified [09-07 并入] | [[Papers/2608-SkillJack]] §4.8 Finding 7 | 直接转成设计规则：skill 准入判据只读行为与代码，不读名称与描述；同底座自评（DeepSeek-v4-flash），跨 judge 是否复现未检验；与 HarnessBank 的 patch 自报 activation beacon 属同一类自报证据（§10.6） |
| OpenART：10K+ 有状态 scenario / 50 域 / 500K+ 工具，中位 97 次工具调用（既有安全 benchmark 1–15）；75 配置 pooled Strict ASR 85.0%，五轮 42.9→69.4→73.5→89.8→94.7；evaluator 人工审计正确率 99.3% | source-verified [09-07 并入] | [[Papers/2608-OpenART]] Abstract / Table 3 / Table 6 / §5.2 / §5.6 | 85.0% 是跨轮 best-of-K 而非单轮概率；Strict ASR 要求确定性 evaluator 与 GLM-5.2 judge 一致，而 GLM-5.2 本身是被测五模型之一；benign completion 与 ASR 未解耦（Aider 70.74% 完成率 / 59.1 ASR 同为最低），无 completion-conditioned ASR；75 个 cell 未给 N 与 CI；无 Limitations/Ethics 节 |
| OpenART 长程漂移：投毒内容到目标动作的中位传播距离 37 个 action（IQR 20–66），首次读取在执行进度 23%、首次不安全输出在 64%，注入到危害的中位延迟占工作流 41%；八个 target 可见向量单独使用均 >50%（workspace 92.5%，其余七个均值 71.2%，full 94.7%） | source-verified [09-07 并入] | [[Papers/2608-OpenART]] §5.5 Fig 4 / §5.6 Fig 7 | 反驳"不安全行为在注入附近发生"的短程假设；三类反复失效（过期假设未作废 / 安全判断被沿用而非重算 / 单步安全动作组合致害）对复用既有判断的自演化系统尤其贴切；单侧演化——两侧模型冻结、benign objective 与 evaluator 不变，故不构成 agent 自演化的剂量-反应证据 |
| CoEvolutionSurvey 按演化算子作用域分三阶段：$A^{t+1}=\Omega(A^t,E,\tau^t)$ / $(A^{t+1},E^{t+1})=\Omega(A^t,E^t,\tau^t)$ / $\Omega^{t+1}=\Gamma^t(S^t,\Omega^t,\tau^t)$；判别标准为≥2 个演化单元相互重塑彼此后续演化，Appendix A 与十个相邻概念划界 | source-verified [09-07 并入] | [[Papers/2608-CoEvolutionSurvey]] Sec. 2.2–2.3 / Appendix A | 与库内两篇 anchor survey（按组件切）正交；Stage 2 feedback-space 分支（ROSKA/CURE/ARCO/ECHO）说明 verifier 确有人演化，缺的是对演化后 verifier 的验证；作者自陈 Stage 3 现有工作多为单实体前身、像样例子仅 RQGM 一类；无公开 repo；Figure 4 跨论文汇总受各论文 setting 差异与取数规则限制 |
| RSI-Agent 的增益按层拆开：同一张 GameCraft 表上 harness 交付 +5.07/+11.33/+14.18/+12.52，自改进机制交付 +3.44/+3.76/+3.99/+3.64；OSWorld 2.0 partial 71.97→78.98、binary 37.80→42.68、ALE 83.75→84.82 | source-verified [09-18 并入] | [[Papers/2609-RSIAgent]] Table 2 / §5 | 无等预算对照臂，基线直接关掉探索与持久记忆，附录自陈 "not a matched-budget estimate"；主表由自改进结果与保留基线拼成（41/82、19/67），只探索非满分任务；ALE 上 w/o RSI 的 83.75 已高于 GPT-6 Astra 82.26 |
| RSI-Agent 按 §7.5 三条判据全不满足：无 generation ≥2、演化系统本身不被演化、权重全程冻结；记录的案例中记忆按目标任务从空建起 | source-verified [09-18 并入] | [[Papers/2609-RSIAgent]] Table A3 / Appendix 12.1 | RSI 术语与实物错位的第三个样本（前两个为 Frontis-MA1、Macaron-V1）；实际形态是任务内探索加持久笔记，成本按题付而非按环境摊销一次 |
| RSI-Agent 的 verifier 准确率全文无量化，其失效链自陈：误判 PASS → 错误规则被蒸馏进记忆 → 后续 run 继续复用 | source-verified [09-18 并入] | [[Papers/2609-RSIAgent]] §4.6 / §7 | 闸门误判在演化系统内以持久资产形式留存并被反复执行（§10.6）；失效子类计数取自 selected case audit 且同一案例可计入多个子类，据此估不出误判发生率 |
| GAI 把 gate 独立性拆成两个独立自由度：判据的**位置**（评估者在 $Ag$ 内还是外）与判据的**忠实性**（被评的是不是真目标）；Minimal Example 里三种放置都自洽而只有一种服务目标 | source-verified [09-18 并入] | [[Papers/2609-GeneralizedAgentIteration]] Remark 2 / Minimal Example | 纯形式化工作：无实验、无定理证明，对既有系统的归约以散文给出；承重的是"自洽的自我报告不携带是否真的变好的信息"这一判断，不是任何数值 |
| NeoHorse-1 的受控对照只剩 +1.26：同基座同课程同预算下 routing-harness 数据五项均值 70.57 vs Toucan 64.32 vs 基座 69.31，其中 HumanEval +9.14、其余四项净 −0.57 | source-verified [09-18 并入] | [[Papers/2609-NeoHorse1]] Table 3 + Table 1 逐格重算 | headline 的 58.94→64.87 / 65.60→69.04 含数据规模差异；全文无隔离课程排序、on-policy distillation 与能力导向配比的消融；论文未提及 Toucan 轮低于基座 |
| Ecdysis：逐条失败改 harness 的基线与胜出方法同起点、同训练评测与接受回滚协议，10 个 held-out 格平均 51.67→46.67（7 格绝对下降），Pass@3 66.00→63.50、Pass^3 37.00→29.00；接受准则为训练集总分严格提升 | source-verified [09-18 并入] | [[Papers/2609-Ecdysis]] Table 1/2 + §4.1 | 该篇整体为 partial 核验，此处只用 source-verified 行；"总分严格提升"只约束总分不约束逐任务回归，是 §10.2 中第一例闸门之后的整体回归；论文全文未讨论该回归 |
| Ecdysis 的 AgentBench 块：w/ FDCR 对五个模型给出完全相同的 90.00/90.00/90.00（AVG = Pass@3 = Pass^3），模型跨度从 Direct 5.00 的 Llama-3.1-8B 到 230B | source-verified [09-18 并入] | [[Papers/2609-Ecdysis]] Table 7 | "harness 把训练任务答案编成运行时约束"是推断而非实测，可证伪检查是读演化后的 harness 找任务特定常量；论文零评论；该块占 headline 相对增益的三分之一 |
| RethinkSkillEvolve 端到端口径：14 个 setting 中"演化→部署 test 更好"9 个，同时改善 robustness 与 transfer 7 个；388 个候选经字节去重只剩 55 个互异的 validation best | source-verified [09-18 并入] | [[Papers/2607-RethinkSkillEvolve]] Table 2 / Appendix | "9/11 improve test" 的分母已被 validation 筛过一遍，跨论文引用应使用 9/14 与 7/14；probe 面板极小（LiveMath T3 仅 2 题）却被等权宏平均进 R/T 汇总 |
| RethinkSkillEvolve 噪声带：字节完全相同的 skill 在 49 题 validation split 上重测 8 次 SD 3.92；100 题配对面板三次重复部署把 +2.3 翻成 −2.0/−3.0/0.0、把 −6.6 翻成 +6.0/+7.0/+5.0，parent-vs-parent 基线 −2.0/−2.0/+2.0 | source-verified [09-18 并入] | [[Papers/2607-RethinkSkillEvolve]] Appendix C Table A13 | 该协议下 ±3 点不可判，本文覆盖的多数报告增益落在此量级；SD 3.92 来自 49 题 split，不可直接搬到 1,400 题 test 上 |
| RethinkSkillEvolve 的 test-time-scaling 对照臂：oracle Parallel Sampling 在 SearchQA 上只落后 evolved skill 0.43 点，在 SpreadsheetBench 上落后 30.96 点（K=6，6,324 次评分尝试） | source-verified [09-18 并入] | [[Papers/2607-RethinkSkillEvolve]] §TTS | 第三条对照臂（等预算重采样）此前在本文覆盖范围内无人做；oracle 选择是上界而非可交付系统；结论是分域的，不能跨域搬运 |
| RethinkSkillEvolve：Gemini 3.1 Pro 选中 skill 含 sandbox 专属 workaround（import openpyxl 前把 /tmp 移出 sys.path），该 workaround 引入的那一轮本身建立了一次 validation new best（69.2→74.4） | source-verified [09-18 并入] | [[Papers/2607-RethinkSkillEvolve]] Appendix D Listing 3 / Table A23 | 演化产物编码环境规程而非能力的最细样本（§10.7）；同篇旁证：从 parent 反复采样补不回该增益，transfer 在分布偏移 tier 从 +52～+53 塌到 +2.9/+3.5；"换 harness 不复现"是假设，论文未测 |
| SkillZip Pro 的等价性协议：实验前固定 −0.05 margin，102 个 held-out 任务配对 bootstrap（10,000 次重采样）给出 +0.010、95% CI [−0.029, +0.059]，据此判定唯一保质量 | source-verified [09-18 并入] | [[Papers/2608-SkillZipPro]] Table III / §VI-G | 等价性主张给出预先声明噪声带的首个样本（§9.4）；pooled 102 任务、BFCL 仅 21 题，真实演化库只有 3 个且同出一次 SkillOpt 运行；kimi-k2.6 上产物可移植性下降（0.611→0.574） |
| SkillZip Pro 的四层成本账（catalog/activation/path/deployment）与 witness 层级 W1≻W2≻W3：production 内容审核 skill 上 witness 逐级放开 13.8%→32.7%→38.1%，无保护压缩 71.4%/75.8% 使 accuracy 88%→70%/62%、FP 10→29–35；演化库每轮新增内容 55%±3% 与既有文本重复，可移除份额 29%（round 2）→53%（round 15） | source-verified [09-18 并入] | [[Papers/2608-SkillZipPro]] §VI-M/§VI-P/§VI-V | "单一压缩率是误导性指标"在方法层被兑现；测到的是文本级重复而非功能级等价；其 SkillReducer 基线的弱化只适用于本文自身实现，不能反向下调前作报告的对照数字 |
| TRACE 以 Pass^k 为直接目标做无闸门的技能重建：GPT-5.5 上 Pass^3 59.9%→94.5%、Δ3 从 27.8 收到 4.0；hidden set 上 50.0→70.0 与 66.7→83.3 | source-verified [09-18 并入] | [[Papers/2608-TRACE]] Table 1/2 | 主表报在 train+test 合并集上而演化循环同时用了两个 split，跨论文可比的是 hidden set 两列；代价是延迟 +22.0%、token +72.4%、成本 +58.8%；全文无任何组件消融，不报 false-refusal 率，也不测 Skill Bank 是否固化早期错误 |
| COBRA-Skills 用 contextual bandit 分配评测预算：三底座相对无技能 +13.1/+26.9/+22.5，总成本相对 SkillOpt 降 55%–58%、每点增益成本降 60%–69%；消融 w/o Bandit −2.2 / w/o Evolution −2.4 / Best-of-30 −2.5 | source-verified [09-18 并入] | [[Papers/2609-COBRASkills]] Table 1/2/4 | 3 次运行 mean±SE，是本文覆盖范围内少见的带离散度报告；OfficeQA 因无法复现 SkillOpt 结果被排除；self-teaching 配置下均分 73.5→72.5、ALFWorld 72.3→63.3，教学侧 token 降 67%–80% 而目标模型 token 上升 |
| JIT-Agent 把 harness 变成按实例现场生成的产物：$(\mathbf{M},\mathbf{P},\mathbf{A},\mathbf{F})$ 协议 + 13 个 seed harness + 三阶段训练的生成器；18 个 matched backbone–benchmark 配对全部提升（GLM-5.2 74.1→81.8、DeepSeek-V4-Flash 66.7→75.5） | source-verified [09-18 并入] | [[Papers/2608-JITAgent]] §5.2 / Table 3 | 固定 backbone 的受控对比里性能只 4/6 居首、成本 6/6 最低（降 14.9%–54.1%，均值 36.0%），且未说明报告的 token 与成本是否含生成器自身开销；无 stage 级消融；写进其 harness intelligence 定义的 reliability 一条完全无量化证据 |
| Zetta 的技能入库闸门：候选须在来源 cluster 内 100% 通过历史失败回归，再看 held-out ΔSR；冻结 VLA 之外的 harness 演化使 RoboCasa 73.56→93.56、LIBERO-Pro macro 32.00→71.13 | source-verified [09-18 并入] | [[Papers/2608-Zetta]] §2.6.2 / Table 2/3 | 摘要的 90.8% 是 Goal 子集均值而非全集；ΔSR 无数值接受阈值；全文无组件级消融（runtime critic / recovery skill / gate 三者贡献未分离），无算力配平对照 |
| Dream-RSI 用重放模拟器做离线搜索：Lasso 上 2931.0 ms / 317 次调用 对 3587.1 ms / 550 次，Flash 上 2350.6 ms / 1879 次 对 2516.7 ms / 3200 次 | source-verified [09-18 并入] | [[Papers/2609-DreamRSI]] Figure 3(a) / §4.1 | 该篇整体为 partial 核验，此处只用 source-verified 行；报告的 Compute 只数 discovery-agent 调用，离线重写与重放评估不计入；确定性揭示假设使被优化的只有预算、批次与停止；单次运行；Pro 侧 6 个 held-out 中 5 个更慢，均值改进完全由 RCV1 一列（14616.0 对 19550.1）支撑，Flash 侧则 6 个里赢 5 个 |
| AgentGrad 用逆序 hint 注入做 per-agent 归因：谁的单点修正能把系统 reward 拉到上界谁即为责任方，干预后的输出直接充当 pseudo-label，因此不需要显式 loss；GPT-5-mini 五 benchmark 平均 +11.76（GEPA +9.24 / TextGrad +6.33 / MIPROv2 +5.66） | source-verified [09-18 并入] | [[Papers/2609-AgentGrad]] §4.1–4.2 / Table 1 | 该篇整体为 partial 核验，此处只用 source-verified 行；摘要的"两 backbone 全面 SOTA"与其自身表冲突（Qwen3-8B/IFBench TextGrad 42.52 > 41.42，加粗给了 TextGrad）；同表两格 TextGrad 与无优化基线逐位相同（零更新被接受）却计入正的平均增益；逆序前提"失败集中在靠后 agent"无任何测量；干预 rollout 是否计入预算 $B$ 未说明 |
| Prime Agent 的版本化持久 harness 状态：四类 typed state 支持 CRUD，refinement 在 turn boundary 落地并记录触发事件与预期效果，版本保留 provenance 并支持 rollback，模型权重不变；一条 Factorio 轨迹里 agent 在 anti-cheating heartbeat 下仍用 RCON 直接 spawn 资源并把它保留为可复用 skill | source-verified [09-18 并入] | [[Papers/2608-PrimeAgent]] §2.5 / §3.5 | 该篇整体为 partial 核验，此处只用 source-verified 行（headline 30%→95.5% 按其 §3.1 自陈只是外部参照，不隔离 harness 因果效应）；撤销覆盖条目自身的版本历史，跨存储的派生传播未描述也未测；nanoGPT 上"harness 选择影响小于实验噪声"是散文判断，未见配套噪声估计 |
| GSAR 的离线 judge 准确率与下游收益脱钩：四 judge 平均 91.5% Acc / 91.8% F1，但 AndroidWorld 在线 RL 头对头只把 UI-TARS-7B-DPO 从 26.7% 提到 30.2%（+3.5），低于 rule-based reward 的 32.8%（+6.1） | source-verified [09-18 并入] | [[Papers/2608-GSAR]] Table 2 / §5.3 Figure 6(a) | 演化 verifier 的离线判别力不能代替下游验证（§8.4）；每训练步 rollout 时间 2342 s 对 rule-based 2754 s，省的是设备访问开销；换 UI-TARS-7B-SFT 底座后增益萎缩到 EM +0.01～+1.03 |
| OPSA：教师 token 级 advantage 噪声率 30.6% / 34.7% / 50.6% 随教师规模单调上升；把全部教师 advantage 换成施加在学生最低 20% log-probability token 上的固定 −0.5，效果与标准 OPD 相当，换成 +0.2 则策略崩溃；删掉教师后 Qwen3-1.7B 的 AIME24 Avg@32 13.44→48.85 | source-verified [09-18 并入] | [[Papers/2608-OPSA]] Sec 2.2 Fig 2(a) / Sec 3.2 Fig 4 / Table 2 | 信号的"落点"与"判别内容"是两条可解耦的属性（§3.4），与分辨率、可验证性从未被同时控制（§4.5 第六个缺口）；等 token 预算对照成立（App C.3：GRPO-wait 32.81 / OPD-wait 31.67 对 OPSA 48.85）；mask 掉反思词 fork 位置后增益基本消失并在约 300 步长度崩塌，撬动的是模型已有反思路径；OOD 增益小（MBPP+ +1.20、GPQA-Diamond +4.48）；全部结果在 1.7B 非 thinking 模式的数学推理上 |
| PRACTICE 阶段消融 24.3 → 40.7 → 42.3 → 45.3 → 49.7：不学习的 BPE 式初始库贡献 16.4 点，三个学习阶段合计 9.0 点，终库 29 张 card | source-verified [09-18 并入] | [[Papers/2608-PRACTICE]] Table 3 / Sec 3.2 | 与 OPSA 同型——被训练出来的监督源，其收益可能小于一个不学习的结构先验；failure-aware 相对 success-only +2.6（45.3 对 42.7）；EB-Habitat 的 Base 与 Long 两档落后最强基线；Appendix C.2 把同一结果写成 40.0% 而 Table 1/3/7 是 49.7%，论文未解释这处不一致 |

## 调研日志

### 2026-09-18 survey-refresh（并入 18 篇，papers_analyzed 76）

- **merged（18 篇）**：[[Papers/2607-RethinkSkillEvolve]] → §6.1（审计式复现与噪声带）、§3.6/§6.3/§6.4/§9 索引表/§9.4/§10.2/§10.7/§11/§12 其五；[[Papers/2608-SkillZipPro]] → §6.1（四层成本与 witness 层级）、§6.4/§9.4/§11；[[Papers/2609-RSIAgent]] → §7.5（按三判据逐条判定）、§3.6/§5.6/§6.2/§10.6；[[Papers/2609-Ecdysis]] → §6.2（gate 判据形式轴）、§3.6/§10.2/§10.7；[[Papers/2608-PrimeAgent]] → §10.5（版本级撤销的首个实物）、§9.4/§10.7/§11/§12 其五；[[Papers/2609-AgentGrad]] → §5.5（多 agent 流水线的 prompt 优化）、§7.3/§8.3/§10.2/§11；[[Papers/2608-TRACE]] → §6.1（Pass^k 为目标的无闸门重建）、§3.5/§3.6/§6.2/§9 索引表；[[Papers/2608-JITAgent]] → §7.2（按实例生成 harness）、§3.5/§3.6/§7.4；[[Papers/2608-Zetta]] → §7.2（冻结 VLA 之外的 harness 演化）、§3.6/§6.2/§9 索引表；[[Papers/2609-DreamRSI]] → §7.1（重放模拟器上的离线搜索）、§3.6/§7.5；[[Papers/2609-GeneralizedAgentIteration]] → §6.2（判据位置与忠实度的切分）、§2.2/§7.5；[[Papers/2609-NeoHorse1]] → §7.5（路由 harness 自标难度）、§3.6/§4.1；[[Papers/2609-COBRASkills]] → §6.1（评测预算的 bandit 分配）、§3.6；[[Papers/2608-GSAR]] → §8.4（演化 verifier 的离线判别力与下游收益脱钩）、§3.4/§4.4；[[Papers/2608-OPSA]] → §3.4/§3.6/§4.3；[[Papers/2608-PRACTICE]] → §5.1/§5.4/§3.6；[[Papers/2609-FlowBalance]] → §3.6/§4.3；[[Papers/2605-SEGA]] → §2.2/§5.1/§5.3。
- **skipped**：无。18 篇全部落位。
- **papers_analyzed 对账链**：按"`## 调研日志` 之前的正文中唯一且能解析到 `Papers/*.md` 的 wikilink"口径机械重数，得 76，无悬空链接（另有 1 条 `Ideas/` 链接不计入）。同口径重数上一版正文得 58，而其 frontmatter 写的是 65——7 篇为历史漂移（旧口径按并入篇数累加而非重数）。本轮取机械值：58 + 18 = 76，覆盖累加值。
- **结构变化**：新增 §10.7「演化产物编码的是环境规程」（三篇独立证据构成既有小节未覆盖的形态）；§10.2 由"三条线"扩为五行并改题为「负性结果：自改进可自退化」；§6.2 gate 表新增两行并补入"聚合分数 vs 逐任务回归"这条判据形式轴；§7.5 新增三判据 × 五工作的对照表；§9 索引表 +3 行；§11 新增两条开放挑战（效应量与噪声的口径、增益的内容归类），credit assignment 与演化资产两条按新证据改写；§12 其五由三个切面扩为四个。判断总数仍为五条，未增补。Key Evidence Matrix 新增 23 行。
- **被修改的既有结论**：§9.4 的"等价性主张无人给出噪声带"降级为"未成标配"（[[Papers/2608-SkillZipPro]] 的预声明 margin + 配对 bootstrap、[[Papers/2607-RethinkSkillEvolve]] 的重复部署带宽两个正面样本）；§10.5 的"没有一个自演化系统实现带血缘的撤销"改写为"版本级撤销已有实物、派生级撤销仍无"（[[Papers/2608-PrimeAgent]]）；§11 的"multi-agent per-agent 归因仍靠讨论涌现而非算法"改写为限定在"结构固定 + 终点可验证"象限之外（[[Papers/2609-AgentGrad]]）；§8.4 的"库内无人这样做"改为"目前无人这样做"并补入 [[Papers/2608-GSAR]] 的离线-下游脱钩数据；§6.3 第三条对照臂（test-time scaling）由缺席改为已有分域结论（[[Papers/2607-RethinkSkillEvolve]]）；§1.2 其二的"三条独立证据线"改为两种形态——过程自身跑偏，以及通过接受判据之后仍在 held-out 上净负（[[Papers/2609-Ecdysis]]、[[Papers/2607-RethinkSkillEvolve]]）。
- **刻意未写进正文的 claim 及理由**：(1) AgentGrad "1,000 rollout 达 70% 而 GEPA 需 >6,000"——逆序干预的额外 rollout 是否计入预算 $B$ 全文未说明，该图横轴正是 rollout 数，口径不确定，只保留 wall-clock 并标注其 ratio-of-means 口径；(2) Prime Agent 的 "same performance at substantially reduced cost / token-for-token advantage"——全文无任何 token 用量数字，ledger 判为 unsupported；(3) Prime Agent §1 的 "outperforms Kimi-Code"——与其 Figure 8 的 71.0 > 68.1 冲突（ledger 判 contradicted），该篇在本文承担的是撤销机制而非 benchmark 结论，故不引入；(4) Prime Agent headline 30%→95.5%——按其 §3.1 自陈只是外部参照而非隔离 harness 因果效应，不作为增益数字使用；(5) RSI-Agent 的 "Agentic Causal Discovery" 与可复用因果关系主张——记忆实物是无 schema 的自撰文件，无结构化因果表示、无对应消融；(6) Dream-RSI 的三条 not-checkable claim（含跨域普适性表述）不进正文；(7) Ecdysis 的跨模型迁移 51.67→68.33 与数据 curation 结论——单格、单次、Pass^3 反向（45.00 对 60.00），不足以承重；(8) Zetta 摘要的 90.8%——是 Goal 子集均值而非全集，正文一律用 71.13 与 93.56；(9) JIT-Agent 对 ahead-of-time harness 的优越性——该篇的对照是结构性论证而非实验，正文只写"首个学到的按实例配置生成器"并给出可判别实验。另有两条以假设形式而非结论形式入正文：RethinkSkillEvolve 的"换 harness 则 sandbox 相关收益不复现"、Ecdysis AgentBench 同分块的"答案被编成运行时约束"，两者均在正文标明未经实测并给出可证伪检查。

### 2026-09-07 增量更新（survey-refresh）

- **merged（8 篇）**：[[Papers/2608-ZerothOrderSelfEvolve]] → §4.3（失败轨迹的信号提取主体）、§1.2/§3.2/§3.4/§3.6/§4.5/§9 索引表/§12 其一；[[Papers/2608-ROPSD]] → §4.3（第二条绕开路径）、§1.2/§3.4/§3.5/§4.5/§12 其一；[[Papers/2608-EvoHarnessRL]] → §6.3（关库对照的下一个适用对象）、§3.6/§5.6/§6.2/§9 索引表/§11/§12 其四；[[Papers/2608-MacaronV1]] → §7.4（天花板拆为操作/激发两层）、§7.5/§12 其三；[[Papers/2608-SkillZip]] → §6.1（维护环节，标题扩为"创造 → 精通 → 优化即训练 → 维护"）、§3.6/§6.2/§6.4/§9.4/§11/§12 其五；[[Papers/2608-SkillJack]] → §10.4（改题为"记忆与技能投毒"）、§6.4/§10.5/§10.6/§11/§12 其五；[[Papers/2608-OpenART]] → §9.3（长程有状态安全评测）、§8.1 表/§8.4/§9 索引表/§10.5/§12 其五；[[Papers/2608-CoEvolutionSurvey]] → §8 引言（第三篇 anchor survey，按演化算子作用域切）、§8.4/§11。
- **skipped**：无。ROPSD 属边界纳入——它是 test-time transductive 适应、任务流由 benchmark 给定、单步 grounding，其笔记归属 `Topics/CUA-Survey`；纳入依据是 §1.3 已确立"model-centric self-improvement 是自演化的子集而非全部"，且它与 ZerothOrderSelfEvolve 共同构成本节最关键的跨论文形态。MacaronV1 按窄口径纳入，只取其 RSI 与配置搜索部分，MoL 架构与推理基建不属本 survey 范围。
- **结构变化**：§3.4 反馈信号轴新增正交属性"信号分辨率"，§4.3 标题由"hindsight 自蒸馏与失败步级利用"改为"失败轨迹的信号提取"（§6.3 引用的原句保留）；§6.1 标题扩为四环节并新增维护段落；§10.4 标题由"对抗性威胁：记忆投毒"改为"记忆与技能投毒"；§8.1 表 +1 行、§9 索引表 +2 行并改写 ALFWorld 行的可比性说明；§11 新增开放挑战"演化资产的维护与撤销"；§12 由四条判断增为五条，新增"演化产物是需要治理的资产"。未做章节重编号——§4.3/§4.4/§6.4 被历史日志与正文交叉引用，新增内容一律并入既有小节。
- **未推翻的既有结论**：gate 的条件性结论（§6.2/§12 其二）、AgentStream 的能力 gate、HarnessBank 的失败模式匹配论、SESA 的关库分解全部保留，本次新增证据均与其同向或对其加限定。EvoHarnessRL 的高分未被用来支持外挂技能库的部署期价值，理由是它缺同管线去 BPE 的对照臂。
- **争议而非追加**：SkillZip 的"压缩三成而分数不降"是等价性主张，其证据为 0.577 对 0.570 的单点比较、无 seed 无方差，落在库内已知的 seed 波动（AgentStream 单元格标准差常 3–6 个百分点）之下，因此在 §6.1 与 §9.4 按"该协议无法区分无损与小损"处理，并据此在 §9.4 新增一条独立于样本量的方法学缺口（等价性主张需要预先声明的噪声带）。
- **验证边界**：8 篇均为 `full-text` + `source-checked`，进入正文的数字全部对应各自 Evidence Ledger 中 source-verified 的条目，表述只到"原文一致性已核查"而非独立复现。逐篇的主要限制：SkillJack 全部数字是路由层策略违规代理量而非真实执行（论文自述），分母 15–47，且 98.5→11.4 存在未排除的分解粒度混淆；EvoHarnessRL 无 seed / 误差棒 / 显著性 / Limitations，+25.7 与表内差值算术不一致；MacaronV1 的 122/122 是 450 次尝试的并集而非可交付单配置；OpenART 的 85.0% 是跨轮 best-of-K 且 judge 模型自身在被测之列；ROPSD 与 SkillZip 均无公开代码；CoEvolutionSurvey 为综述，只用于存在性与分类学，未据它新增任何一手数字。Key Evidence Matrix 新增 16 行。

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
