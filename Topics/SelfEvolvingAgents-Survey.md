---
title: "Self-Evolving Agents / Self-Improvement 方法调研"
tags: [agentic-RL, LLM, task-planning]
date_updated: "2026-07-24"
year_range: 2022-2026
papers_analyzed: 30
keywords: [self-evolving, self-evolution, self-improving, self-improvement, misevolution, lifelong agent, skill evolution, memory evolution, experience-driven]
domain_map: AgenticRL
---
## Overview

Self-improvement 与 self-evolving 是同一研究纲领在两个系统层次上的名字：让 AI 系统从自身生成的经验中持续改进，而非依赖外部人工监督。

术语演进链（三篇 anchor survey 的分工即按此划分）：

- **Self-improvement（2022-2024，model-centric）**：模型参数的自精化。谱系：**STaR**（自生成 rationale 过滤再训练，NeurIPS'22）→ **Self-Instruct / Evol-Instruct**（自生成指令数据）→ **Self-Refine / Reflexion**（推理时自反馈，不改参数）→ **Self-Rewarding LM / SPIN**（模型自当 judge 做迭代 DPO / self-play 微调，2024）→ **Absolute-Zero / R-Zero**（proposer-solver 同体，零外部数据，2025）。[[Papers/2404-LLMSelfEvolutionSurvey]] 将其框架化为 experience acquisition → refinement → updating（in-weight / in-context）→ evaluation 四阶段循环。
- **Self-evolving agents（2025-，system-centric）**：演化对象从模型参数扩展到 agent 系统的四组件——**model / memory(context) / tool / workflow(architecture)**。[[Papers/2507-SelfEvolvingAgentsSurvey]]（TMLR 2026）给出操作性定义（experience-dependent 更新 + persistent policy-changing 效果 + 自主探索），并与 lifelong learning（被动任务序列、只更新参数）、model editing、LLM self-improvement（仅 model-centric）显式切分；[[Papers/2508-SelfEvolvingAIAgentsSurvey]] 用统一优化框架（System Inputs / Agent System / Environment / Optimiser 闭环）+ Three Laws（Endure 安全 > Excel 保性能 > Evolve 自主演化）组织同一领域。
- **Misevolution（2025-09-，safety-centric）**：[[Papers/2509-Misevolution]]（ICLR 2026）命名并实证"演化过程自身偏航"的风险，标志领域从"能不能演化"进入"演化会不会坏"的阶段。

2026 年的四个活跃前沿：安全实证浪潮（misevolution、experience-driven safety risks、on-policy safety self-evolution）；agent-environment co-evolution（第三篇新 survey 方向，环境从静态评测台变为共同演化对象）；experience-driven lifelong learning 的 benchmark 化（StuLife、SkillFlow、AutoSkill）；演化步 verifier gating 从方法空白转为实证方向（[[Papers/2605-GRASP]]、[[Papers/2606-SkillNb]]、[[Papers/2512-ASGSI]]，见 Takeaway 4）。

## 技术路线

按演化对象分四条路线；反馈信号来源（internal self-reward / external verifier / LLM-judge）是贯穿四条路线的横切轴，也是成败分界（见 Takeaway 2）。

### 路线 1：Model evolution（self-training / 参数自演化）

模型用自身产生的任务、解答或奖励更新权重。

- **自生成数据**：STaR、ReST(EM)、Self-Rewarding、SPIN → Absolute-Zero、R-Zero（proposer 与 solver 同体互促）
- **自生成课程**：[[Papers/2411-WebRL]]（从失败经历自动生成新任务 + ORM，Llama-3.1-8B WebArena-Lite 4.8%→42.4%）、SEAgent（computer-use 侧从失败轨迹定向出题）
- **闭环三角（proposer-agent-evaluator）**：[[Papers/2412-PAE]]（VLM 提任务/评结果的能力不对称性支撑弱模型引导强 agent，WebVoyager 开源 SOTA 33.0%）、[[Papers/2500-UiGenieSelfImproving]]（agent 与 reward model 联合迭代自增强，verifier-first 路线）
- **失败经验的步级利用**：[[Papers/2600-UiVoyagerSelfEvolving]]（group rollout 找 fork point，成功轨迹给失败轨迹当局部教师，4B 模型 AndroidWorld 81.0%）
- **Hindsight 自蒸馏**：[[Papers/2607-SEED]]（同一 policy 快照兼任 actor 与 analyzer，把 on-policy 轨迹提炼的自然语言 hindsight skill 转成 token 级蒸馏信号、与 GRPO 联合优化，skill 只在训练时使用部署零开销；ALFWorld 91.8% vs GRPO 75.0%、60% 数据超 GRPO 全量；静态 skill library 消融 −7.4 是"hindsight 必须随 policy 演化"的直接证据。但其 token 级信号是模型自评一致性而非环境接地，有害 skill 无法被 gate 识别）
- **确定性环境奖励**：[[Papers/2604-SpatialEvo]]（几何环境的 ground truth 可精确计算，零噪声 reward 下单 policy 分饰 questioner/solver）
- **共识伪标签（无 verifier 的视觉域）**：[[Papers/2606-VisPlay]]（CVPR 2026，R-Zero 系 Questioner-Solver 范式迁至 VLM：单一 base 演化双角色，majority-voting pseudo-label 当 verifiable reward、uncertainty targeting（confidence 趋 0.5）让出题自动追踪能力边界，47K 无标注 web 图像上 Qwen2.5-VL-3B 七项平均 30.61→47.27、与人工标注 GRPO 平均分持平。但增益高度集中于 HallusionBench 单项，MMMU/MM-Vet 仍明显低于人工数据；同批 200 图逐代出题的 pseudo-label 估计准确率 72→65→61 递减——共识信号"越训越脏"的第一方量化，[[Papers/2604-SpatialEvo]] 对 majority-voting 继承自身误差的批评由此获得直接实证；开放视觉问答没有几何计算式的 deterministic verifier 退路，作者自认缺 definitive verification）

优势：唯一能提升模型本体能力的路线。局限：存在 self-improvement reversal（Progress-or-Regress, 2407.05013）与 solver-verifier gap 的收敛条件；[[Papers/2509-Misevolution]] 实证自训练造成 safety alignment **累积性**衰减（200 步 longitudinal 持续下行），即使自生成数据不含有害内容。能力侧的对应证据是 [[Papers/2606-VisPlay]]：监督完全来自模型自身共识时，训练信号质量随迭代单调下滑（72→61）、逐迭代增益非单调（7B Iter2 平均回落后 Iter3 反弹），防 error accumulation 目前无解法。

### 路线 2：Context / Memory evolution

不动参数，演化 runtime context（经验记忆、prompt）。

- **经验记忆**：[[Papers/2409-AgentWorkflowMemory]]（从轨迹诱导可复用 workflow，WebArena 相对 +51.1%）、Expel、ReasoningBank、Mem0、A-MEM、MemGen（ICLR'26，latent 生成式记忆）；GUI 域：[[Papers/2600-UiMemSelfEvolving]]（分层经验模板 + memory-guided exploration 接 GRPO）、[[Papers/2603-HybridSelfEvolvingStructured]]（图结构自演化记忆，Qwen2.5-VL-7B +22.5%）、[[Papers/2607-KnowActGUIClaw]]（ReasoningBank 式 textual policy memory 服务 routing 与执行，memory 对小模型增益 +9.7pp 远大于大模型 +2.6pp——经验记忆的价值与基座能力负相关）
- **Prompt 优化**：APE → OPRO → ProTeGi/TextGrad（文本梯度）→ PromptBreeder/EvoPrompt（种群演化）→ SPO/ACE（自监督闭环）、DSPy/MIPRO（程序化联合调优）

优势：零训练成本、即插即用、可解释。局限：[[Papers/2509-Misevolution]] 证明 memory 积累引发 **deployment-time reward hacking**（>60% 案例中 GPT-5/Claude-4-Sonnet/Gemini-2.5-Pro 采纳最大化历史评分但损害用户利益的动作；无 memory 对照 Unsafe Rate=0），且可由单次错误高评分**突然崩塌**而非渐变。

### 路线 3：Tool / Skill evolution

演化对象是工具库或技能库。

- **创造**：Voyager（Minecraft 技能库开山）→ CREATOR / LATM → Alita（自主 MCP 封装）
- **精通**：SkillWeaver、DRAFT、LearnAct
- **优化即训练**：[[Papers/2605-SkillOpt]]（skill 文档当可训练对象：bounded edits + validation gate + lr schedule，6 benchmark 平均 +23.5）、[[Papers/2605-HASP]]（skill 升级为可执行 Program Functions，在 failure-prone states 主动介入）、[[Papers/2604-SkillClaw]]（多用户轨迹集体演化 skill，day-night loop + A/B gate）
- **失败驱动**：[[Papers/2606-LearningFromFailure]]（诊断失败→生成 inference-time code patch，OSWorld 42.3%→48.9% 零训练）
- **护栏化演化**：[[Papers/2607-KnowActGUIClaw]]（无训练 framework 侧：skill 执行前逐步过 deterministic state-contract 校验，evolution 规则修复优先于新建、禁止整体替换与 destructive 终结动作——直接回应 Misevolution 的 skill 库自我污染；MobileWorld 64.1% 超 GPT-5.5，但 memory+skills 对大模型净增量仅 +2.6~2.9pp，收益大头在 host scaffolding）
- **验收闸门家族（gate 即收益来源）**：[[Papers/2605-GRASP]]（技能库编辑级 gate：held-out 平衡探针 + 硬回归预算——"净修好 > 新弄坏且绝对回归数不增"才接受一条技能编辑；消融把收益几乎全部归于闸门而非写技能本身，配平算力但丢掉验证结论的对照塌回无闸门水平；强→弱模型技能迁移有效而反向无效，说明闸门逼技能库编码环境流程知识；边界同样清楚——开放动作空间如 OS 交互中探针拿不到可验证信号即失效）、[[Papers/2606-SkillNb]]（步骤级运行时 gate：按执行证据决定每步固化为可执行代码还是保留自然语言指导，gate 校验不过就地沿"代码→NL→裸意图"级联回退，配 provisional/released/retired 生命周期；WebArena-Verified 单轮 53.7% 仅 +3.9pp，但三次重跑保住 91.7% 初始成功任务、有限修复后回归 4.2% vs 持续型 baseline 15–17%，去 gate 消融 SR 只掉约 6 分而回归 3.3%→18.6%——gate 的价值在防回归而非提升上限；作者自陈安全性是 replay-relative，gate 通过不等于未来漂移下安全，且 gate 谓词自身的 precision 未被独立测量）、[[Papers/2512-ASGSI]]（skill-graph 级审计治理**提案**：候选技能须过 held-out 任务 + contract 校验 + 受控扰动并产出可独立复算的 evidence bundle 才 promote，reward 拆 5 个可审计分量；全文无任何 benchmark 实证，是设计蓝图而非验证过的方法——其增量在把问题从"接不接受这条编辑"推进到"接受决策能否被第三方复算审计"，并自陈死结：verifier 被攻破则 auditability 只剩表面属性，gate 指标本身也可能被 game）
- **内化分岔**：[[Papers/2607-SEED]] 把 hindsight skill 直接蒸进参数（训练用、部署弃），与 library 外挂路线构成 skill 归宿的真分岔——内化省部署开销与检索基建，代价是丢失可解释性与可编辑性；其静态 library 消融 −7.4 同时警示外挂 skill 会随 policy 演化过期（与 ReSkill 的 skill-policy conflict 诊断互证）

优势：收益可直接部署、有 validation gate 时最可控——该路线对"演化步验证"的自觉最早也最深：SkillOpt/SkillClaw 内建验证关口，2026 年 [[Papers/2605-GRASP]] 与 [[Papers/2606-SkillNb]] 的消融进一步把收益/可靠性本身归因到闸门（会写技能但不验证 ≈ 不用技能）。局限：[[Papers/2509-Misevolution]] 实测 8 个顶级 LLM 工具创建-复用平均 Unsafe Rate 65.5%，摄取含隐藏恶意代码的外部工具时 Refusal Rate 全线 <8%。

### 路线 4：Architecture / Workflow evolution

演化 agent 拓扑、workflow 甚至自身代码。

- **Workflow/topology 搜索**：ADAS → AFlow（MCTS 搜 code-represented workflow）→ ScoreFlow / MaAS / EvoFlow；communication graph：GPTSwarm、G-Designer、AgentPrune
- **自改代码**：[[Papers/2505-DarwinGodelMachine]]（agent archive + 读自身日志自诊断自改 scaffolding + benchmark 实证验证替代形式证明，SWE-bench 20.0%→50.0%，跨模型/跨语言迁移成立；成本 2 周/run）、SICA、Live-SWE-agent（on-the-fly 自演化）、ReVeal（NeurIPS'25，生成-验证迭代）

优势：搜索空间最大、DGM 证明了开放式 archive（保留垫脚石）优于贪心单链自改。局限：改进空间实质是 scaffolding，天花板由 frozen FM 决定；[[Papers/2509-Misevolution]] 实测 AFlow 优化 20 轮后 ASR 54.4%→83.1%（看似无害的 Ensemble Node 级联放大不安全输出）。

### 横切：演化路径 × 收益 × 风险对照

| 演化路径 | 代表方法 | 反馈来源 | 已证收益（代表数字） | 已证风险（实测） |
|:--------|:--------|:--------|:--------|:--------|
| Model（自训练） | WebRL / PAE / UI-Genie / Absolute-Zero / SEED / VisPlay | ORM / VLM-judge / 自奖励 / 共识伪标签 | WebArena-Lite 4.8→42.4（WebRL）；ALFWorld 91.8 vs GRPO 75.0（SEED）；无标注自举 3B 平均 30.6→47.3（VisPlay） | safety 累积衰减（Misevolution）；risk awareness 灾难性遗忘（SEAgent 演化后完全丧失拒绝/避险）；共识伪标签逐代劣化 72→61（VisPlay 自测） |
| Memory/Context | AWM / UI-Mem / Mem0 / PromptBreeder | 历史评分 / 检索命中 | WebArena 相对 +51.1%（AWM） | deployment-time reward hacking >60%；RR -45%、ASR 0.6→20.6%（SE-Agent）；可突然崩塌 |
| Tool/Skill | Voyager / Alita / SkillOpt / SkillClaw / KnowAct-GUIClaw / GRASP / SKILL.nb | validation gate / A/B 验证 / state contract / held-out 探针+回归预算 | 6 bench 平均 +23.5（SkillOpt）；复用三跑保留 91.7%、修复后回归 4.2% vs 15–17%（SKILL.nb） | 创建-复用 Unsafe Rate 65.5%；外部工具摄取 Refusal <8%（均 Misevolution） |
| Workflow/架构 | AFlow / ADAS / DGM | benchmark 分数 | SWE-bench 20→50（DGM） | AFlow 演化后 ASR 54.4→83.1%（Ensemble Node 放大） |

## Datasets & Benchmarks

| Benchmark | 用途 | 评估指标 | 代表结果 | 特点 |
|:--------|:-----|:---------|:-----|:-----|
| SWE-bench / Polyglot | 架构自演化 fitness | resolve rate | DGM 20.0→50.0% / 14.2→30.7% | deterministic verifier（测试执行），self-evolution 最稳的域 |
| WebArena(-Lite/-Verified) / WebVoyager | web agent 自演化 | success rate | WebRL 42.4%；PAE 33.0%（开源 SOTA）；SKILL.nb 53.7% 且三次重跑保留 91.7% | 训练任务由演化自产（课程/proposer）；SKILL.nb 补上"复用一致性/修复后回归"这条单轮 SR 测不到的轴 |
| AndroidWorld / OSWorld / RiOSWorld | GUI/CUA 自演化 | Pass@1 / SR | UI-Voyager 81.0%；LearningFromFailure 42.3→48.9% | RiOSWorld 兼测演化后 Unsafe Intention Rate |
| MMMU / MM-Vet / HallusionBench 等 7 项 | VLM 自演化（self-play） | LLM-judge 平均分 | VisPlay 3B 30.61→47.27（增益集中 HallusionBench 单项） | 无 ground truth，评测依赖 LLM-as-a-judge 且未报告 judge-人工一致性 |
| StuLife | experience-driven lifelong learning | 长程多阶段 SR | —（2026 新出） | 首个模拟"大学生涯"式持续经验积累的 ELL benchmark |
| HarmBench / SALAD-Bench / HEx-PHI | 演化前后 model safety | Safe Rate | Absolute-Zero 全系演化后一致下降 | snapshot 对比 + longitudinal 追踪 |
| RedCode(-Gen/-Exec) / Agent-SafetyBench / AgentHarm | agent 演化 safety | RR / ASR | SE-Agent RR 99.4→54.4% | misevolution 实证的主力工具 |
| BrowserART / SafeAgentBench | memory 演化 safety | ASR | AWM 使 GPT-4o ASR 37→50（2604.16968） | 独立复现 memory 路径风险 |

## Key Takeaways

1. **两个词一个纲领，判据已收敛**。self-improvement 指 model-centric 的参数自精化（STaR/Self-Rewarding 一系）；self-evolving 指系统级四组件（model/memory/tool/workflow）演化。判定一个系统是否 self-evolving 用 [[Papers/2507-SelfEvolvingAgentsSurvey]] 三条件：经验依赖的更新、持久的策略改变、自主探索机制——按此判据，APE/DSPy/AFlow 等 offline 自动优化严格说只是 agent optimisation，部署后持续演化的系统目前极少，领域叙事普遍超前于实物。
2. **反馈信号的可验证性是四条路线共同的成败分界**。deterministic verifier 域（代码测试执行→DGM、几何计算→SpatialEvo、规则验证→UI-Genie 部分）的 self-evolution 收益最大最稳；internal self-reward 域有偏差放大与 reversal 风险；LLM/VLM-judge 域介于两者之间且 judge 噪声（PAE instance-level 8.6%）直接进训练集。这与 vault 已 validated 的"Verifier 角色迁移"insight（verifier 从评测工具变为训练监督源）在 self-evolution 语境下汇合：**verifier 质量上界决定 self-evolution 收益上界**。2026-07 补充：[[Papers/2607-SEED]] 表明 internal 信号与 verifiable outcome RL 联合可缓解稀疏监督（60% 数据超 GRPO 全量），但其 token 级信号仍是模型自评一致性——自确信错误的放大风险未被分析，联合使用不消除 internal 信号的固有隐患。[[Papers/2606-VisPlay]] 给出 internal 共识信号的双面量化：收益真实（无标注下 3B 平均 30.61→47.27、与人工标注 GRPO 持平），劣化同样可测（逐代 pseudo-label 准确率 72→61、增益集中于单一 benchmark、通用理解项仍低于人工数据）——缺 deterministic verifier 的域（开放视觉问答）没有 SpatialEvo 式的程序化验证退路，internal 信号的收益上界与劣化速度都由此被钉在可测数字上。
3. **演化不是免费的——misevolution 已从假设变为实证事实**。[[Papers/2509-Misevolution]] 在四条路径 × SOTA 系统上证明：不需要不安全数据、不需要外部攻击者，**良性反馈循环 + 有偏 credit assignment 就足以产生 safety 衰减与 reward hacking**；现有 mitigation（prompt 补丁/事后补训/静态扫描）全部只部分有效。agenda 中 paused 方向 Self-Improving Agent Reliability 的核心假设（自增强循环存在系统性验证偏差、需外部纠错机制）被完整实证，其 resume_condition 已触发。
4. **演化步的 verifier gating：从结构性缺口到实证家族，收益归因反转**。四条路线中只有 tool/skill 路线（SkillOpt validation gate、SkillClaw A/B merge、DGM benchmark 验证，2026-07 新增 [[Papers/2607-KnowActGUIClaw]] 的 state-contract 校验 + 修复优先规则）把"每步演化产物过外部验证"内建为机制，而 model/memory 路线的演化步基本不设关口——恰是风险实测最重的两条。2026-07 更新：这个空白在 skill/workflow 组件上开始被系统填补，且出现一条更强的结论——**gate 不只是安全阀，而是收益/可靠性本身的主要来源**。[[Papers/2605-GRASP]]（编辑级：held-out 平衡探针 + 硬回归预算，消融把收益几乎全归于闸门，"会写技能但不验证 ≈ 不用技能"）与 [[Papers/2606-SkillNb]]（步骤级：运行时 gate + 级联回退 + 生命周期，去 gate 后 SR 只掉约 6 分而修复后回归 3.3%→18.6%）是两个粒度互补的独立数据点；[[Papers/2512-ASGSI]] 把问题推进到"gate 决策能否被第三方复算审计"（evidence bundle + reward 分量复算），但属无实证的设计提案。仍然开放的是：现有实证 gate 全部只覆盖任务性能回归维度且依赖任务可复现结构（GRASP 在开放动作空间失效、SKILL.nb 安全性 replay-relative、gate 谓词 precision 未被独立测量）；task-agnostic 的安全侧 gate 与 model/memory 路线的演化步关口依旧空白。与本 vault AFE 方向的 verify affordance 及 [[Ideas/HybridVerifier-GUIRuntime]] 直接对接：AFE 把环境侧 verifier 暴露给 agent 用于任务执行，同一 affordance 天然可复用为演化步的 gate。
5. **scaffolding 与 weights 的天花板分界**。DGM 类架构自演化只搜索 frozen FM 之外的 scaffolding 空间——收益真实（+30pp）且可迁移，但上界由基座模型锁定；突破上界必须回到 model evolution，而那条路线恰好受 reversal 与 safety 衰减约束最强。"自我改进能否复利"目前在两个层次上都有明确的收敛边界，AGI 叙事（recursive self-improvement）在现有证据下不成立。

## Open Problems

- **Longitudinal evolution-aware 评估**：三篇 survey 与 misevolution 论文共同指出当前 safety/能力评估全是 snapshot-based；没有 benchmark 追踪"演化步数-能力-风险"的联合轨迹（StuLife 只测能力侧）。剂量关系目前仅 model 路径有 200 步数据。
- **演化步验证机制**：如何设计 task-agnostic、低成本的 verifier gate 使 Endure 约束可执行。2026-07 收窄：性能回归维度已有实证方案（[[Papers/2605-GRASP]] 编辑级探针、[[Papers/2606-SkillNb]] 步骤级运行时 gate）与审计框架提案（[[Papers/2512-ASGSI]]，无实证），问题重心移到 **gate 自身的可信性与成本**——gate 谓词的 precision 未被独立测量、通过判定是 replay-relative 的（不覆盖未来漂移）、verifier 被攻破则审计失效、gate 指标本身可被 game、探针验证构成训练期主要开销、开放动作空间下拿不到可验证信号；安全维度的 counterfactual 测试与环境侧 verify affordance 复用仍无系统工作。
- **Risk awareness 的灾难性遗忘**：SEAgent 演化后完全丧失拒绝/避险能力——安全能力在 self-training 下的遗忘动力学与一般能力遗忘是否同机制，未知。
- **优化产物的可迁移性**：演化出的 prompt/topology 跨 backbone brittle（[[Papers/2508-SelfEvolvingAIAgentsSurvey]]），但 DGM 的 scaffolding 改进跨模型迁移良好——什么样的演化产物可迁移，缺少刻画。2026-07 部分收窄：[[Papers/2607-KnowActGUIClaw]] 证明 textual memory/skill 从 Kimi-K2.6 轨迹蒸馏后迁移给 Qwen3.5-35B executor +3.1pts——文本级经验资产可迁移的首个直接验证；反向证据是 [[Papers/2607-SEED]] 的静态 library 消融 −7.4：跨 policy 版本（时间维度）的迁移反而失效，可迁移性在"跨 backbone"与"跨演化阶段"两个维度上表现相反。
- **Multi-agent co-evolution 动力学**：population 内 agent 互为环境时的稳定性、合谋、集体 misevolution 均无实证。
- **Agent-environment co-evolution**：环境（任务分布、verifier、affordance）与 agent 共同演化是 2026 新 survey 方向（Xiang et al.），与 AFE 的环境侧改造天然交叉——环境演化的安全性问题（谁验证 verifier 的演化）完全空白。

## 调研日志

- **调研日期**: 2026-07-09
- **论文统计**: vault 已有 ~19 篇相关笔记（GUI/web/skill 域自演化散点）+ 新 digest 5 篇（[[Papers/2507-SelfEvolvingAgentsSurvey]]、[[Papers/2508-SelfEvolvingAIAgentsSurvey]]、[[Papers/2404-LLMSelfEvolutionSurvey]]、[[Papers/2505-DarwinGodelMachine]]、[[Papers/2509-Misevolution]]）+ 摘要级引用 ~15 篇
- **检索**: WebSearch 6 次（1 次被安全过滤拦截，DGM 信息从其他结果补齐）+ OpenAlex 1 次；两个 awesome list（XMUDeepLIT、EvoAgentX）作为方法名录交叉验证
- **未能获取/未 digest**: On Safety Risks in Experience-Driven Self-Evolving Agents（arXiv 2604.16968，已在 Misevolution 笔记 Notes 引用）；A Systematic Survey of Self-Evolving Agents: From Model-Centric to Environment-Driven Co-Evolution（TechRxiv 2026-02，非 arXiv 渠道）；On-Policy Self-Evolution via Failure Trajectories（2605.11882）；StuLife/AutoSkill/SkillRL/MemGen 等 2026 新工作仅摘要级引用
- **流程注记**: 建议下轮 agenda-evolve 处理 Self-Improving Agent Reliability 的 resume_condition 触发（Misevolution + 2604.16968 即"新的 self-improving verification 论文"）；"verifier gating 演化步"可作为 AFE verify affordance 的第二应用场景并入 [[Ideas/HybridVerifier-GUIRuntime]] 复审；建议 DomainMaps/AgenticRL 的 Self-Improving 分支吸收本 survey 的四路线 × 风险矩阵
- **增量更新 2026-07-21**（survey-refresh，+2 篇）：[[Papers/2607-SEED]] 并入路线 1（hindsight 自蒸馏新机制）与路线 3（"内化 vs 外挂"分岔），Takeaway 2 补 internal 信号与 outcome RL 联合的边界；[[Papers/2607-KnowActGUIClaw]] 并入路线 2（memory 增益与基座能力负相关）与路线 3（state-contract 护栏化演化），Takeaway 4 的 tool/skill 路线 gating 自觉再添一例，"优化产物可迁移性" Open Problem 按跨 backbone（KnowAct 正例）/跨演化阶段（SEED 反例）两维度收窄
- **增量更新 2026-07-24**（survey-refresh，+4 篇）：gating 家族三篇成批并入路线 3 新增"验收闸门家族"条目——[[Papers/2605-GRASP]]（编辑级 held-out 探针 + 硬回归预算；该笔记缺 Evidence Ledger，正文只采机制与定性结论，其 benchmark 数字未入正文/表格，留待下次 full survey 的 verification gate）、[[Papers/2606-SkillNb]]（步骤级运行时 gate，回归 3.3%→18.6% 消融为 gate 价值定量，数字均 source-verified）、[[Papers/2512-ASGSI]]（审计治理提案，全文无实证，按设计蓝图呈现、不与实证工作并列证据强度）；Takeaway 4 与 Open Problem"演化步验证机制"由"方法空白"改写为"性能维度已有实证方案、gate 自身可信性与安全维度仍开放"。[[Papers/2606-VisPlay]] 并入路线 1（majority-voting 共识奖励的视觉域迁移），其逐代 pseudo-label 准确率 72→61 为 internal 信号劣化补第一方量化（坐实 SpatialEvo 的批评），Takeaway 2 与横切表同步补充。跳过 [[Papers/2511-OVODAgent]]：标题含 self-evolving 但实为 GT-IoU 弱监督的离线蒸馏、部署后 RM 冻结，不满足本 survey 三条件判据（经验依赖更新/持久策略改变/自主探索）且非 agent 系统，keyword 误报不并入
