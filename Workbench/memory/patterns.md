# Patterns

> Memory file for observed patterns in research

## Architectural Patterns

### Pattern 1: Multimodal LLM Core
- Most GUI Agents use VLM/LLM as central reasoning component
- Screen understanding → Planning → Action execution pipeline
- Examples: CogAgent, MobileFlow, SeeClick

### Pattern 2: Hierarchical Planning
- High-level task decomposition + low-level action grounding
- Reduces complexity by separating task-level from action-level
- Examples: MobileUse, AmapAgent

### Pattern 3: Self-Improving Loop
- Collect execution traces → Learn from failures → Improve policy
- Requires memory and reflection mechanisms
- Examples: UI-Genie, Continual GUI Agents

## Evaluation Patterns

### Dataset Types
- Static benchmark datasets (GUIOdyssey, GUIWorld)
- Interactive environments (WebCanvas, mobile simulators)
- Real-world deployment tests

### Metrics
- Task completion rate (primary)
- Action efficiency (steps taken)
- Grounding accuracy

## Research Gaps Patterns

- Few works on cross-platform transfer
- Limited exploration of multi-agent coordination
- Safety/privacy concerns rarely addressed → now emerging as systematic area (VLASafety survey, EVA red-teaming), [[Workbench/logs/2026-04-28]]

---

### [2026-04-28] RL methods show high data efficiency for GUI Agent training

- **observation**: RL-based GUI Agent training (GRPO-style) achieves competitive results with surprisingly small datasets — UI-R1 uses only 136 tasks, ClawGUI shows +6.0% over baseline with rule-based rewards
- **occurrences**: [[Workbench/logs/2026-04-28]]
- **confidence**: low
- **needs_verification**: yes

### [2026-04-28] Evaluation methodology shifting from binary success to multi-dimensional diagnosis

- **observation**: New benchmarks (AutoGUIv2, ProBench, ReVSI) move beyond binary success/failure to process-level evaluation, multi-dimensional capability diagnosis, and systematic failure mode analysis
- **occurrences**: [[Workbench/logs/2026-04-28]], [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 四路证据 triangulation, Visual Generation Taxonomy critique of perceptual-only evaluation)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-05-03])

### [2026-04-28] VLM capabilities are fragmented across sub-tasks

- **observation**: AutoGUIv2 reveals that different VLMs have complementary strengths — Qwen3-VL excels at grounding while Gemini excels at captioning — suggesting no single model dominates all GUI Agent sub-tasks
- **occurrences**: [[Workbench/logs/2026-04-28]]
- **confidence**: low
- **needs_verification**: yes

### [2026-04-28] Small specialized models can match large models on GUI grounding

- **observation**: GoClick (230M parameters, encoder-decoder architecture) achieves grounding accuracy comparable to much larger VLMs, suggesting grounding may not require general-purpose reasoning capacity
- **occurrences**: [[Workbench/logs/2026-04-28]], [[Workbench/logs/2026-06-26]] (ZonUI-3B: 3B+LoRA+24K 样本达 ScreenSpot 84.9，数据多样性+分辨率专门化可部分替代规模; AFRAgent: 4B feature renormalization 达强 GUI action prediction 且 FLOPs/latency 显著低于 CogAgent)
- **confidence**: low
- **needs_verification**: yes
- **status**: → promoted to insight ([2026-07-03])

---
*Last distilled: 2026-05-03*

### [2026-05-03] Latent-space agent communication significantly reduces token overhead

- **observation**: Multi-agent systems using latent-space (而非 text-based) communication 可实现 75%+ token reduction，同时保持 accuracy 提升——latent transfer 避免了中间 agent 的文本生成解码开销
- **occurrences**: [[Workbench/logs/2026-05-03]] (RecursiveMAS +8.3% accuracy, 75.6% token reduction)
- **confidence**: low
- **needs_verification**: yes

### [2026-05-03] Production deployment cost becoming primary bottleneck for computer-use agents

- **observation**: Computer-use/GUI agent 研究焦点从"提升成功率"转向"降低部署成本"——Step-level cascade 用 event-driven escalation 实现 74.6% cost reduction，production 视角的 real problem framing
- **occurrences**: [[Workbench/logs/2026-05-03]] (Step-level Optimization), [[Workbench/logs/2026-04-28]] (ClawGUI infrastructure)
- **confidence**: low
- **needs_verification**: yes

### [2026-05-03] Workflow automation on real-world tasks has <70% success rate

- **observation**: Workflow automation benchmark 显示 frontier models 最高 pass rate 仅 66.7%，live Internet long-horizon tasks 仅 44.5%——远未 saturation，真实场景远比 curated benchmark 更难
- **occurrences**: [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 66.7%), [[Workbench/logs/2026-04-28]] (Odysseys 44.5%), [[Workbench/logs/2026-05-25]] (CHIBench 28.0% pass@1，pass^3 无 agent >20%), [[Workbench/logs/2026-06-10]] (SpatialWorld GPT-5 17.4%, SWEExplore line-recall 0.14-0.19), [[Workbench/logs/2026-06-24]] (SaaSBench resolved 3.8%)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-06-25])

---
*Last distilled: 2026-06-25 (period 2026-05-19 ~ 2026-06-25)*

### [2026-06-25] Verifier/environment oracle 正从 evaluator-only 扩展为 training supervision 与 agent-facing runtime affordance

- **observation**: programmatic verifier / environment oracle 不再只是最终判分器——OpenComputer 显示硬编码 verifier 与人类对齐 94.1% 远超 LLM judge 79.2%；ENVS 用环境 oracle 的 verified search 直接产出 SFT 监督；GUI-Environment-Survey 与 AFE proposal 进一步提出把 state/fork/verifier 以 non-oracle 方式暴露为 agent-facing runtime affordance。verifier 的角色从"事后评测"向"训练监督 + 执行期可观测/可验证能力"迁移
- **occurrences**: [[Workbench/logs/2026-05-22]] (OpenComputer 94.1% vs 79.2%), [[Workbench/logs/2026-06-22]] (GUI-Environment-Survey: Verification 作为组织原则), [[Workbench/logs/2026-06-23]] (AgentFriendlyEnvironment-Proposal: 后台 state/fork/verifier → agent-facing affordance), [[Workbench/logs/2026-06-24]] (ENVS: 环境 oracle 作为 SFT 监督来源)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-06-25])

### [2026-06-25] Agent skill 正从静态文本提示演化为可治理/可训练/可执行/可编译的一等对象

- **observation**: 多篇工作把 "skill" 从 prompt 里的自然语言建议升级为有独立生命周期的对象：SkillsVote 做 evidence-gated 治理、MMSkills 用多模态 skill package + branch loading、HASP 把 skill 编成可执行 Program Functions、SkillOpt 把 skill 文档当可训练对象施加 deep-learning 式 optimizer、ColleagueSkill 做 trace-to-skill 蒸馏、ReSkill 在 RL loop 内创建 skill、LatentSkill 把 skill 编译进 weight space。共同信号是 skill 成为可被治理、训练、执行、编译的一等模块，且多数声称零/低部署成本
- **occurrences**: [[Workbench/logs/2026-05-22]] (SkillsVote, MMSkills, HASP), [[Workbench/logs/2026-05-25]] (SkillOpt +23.5, ColleagueSkill), [[Workbench/logs/2026-06-07]] (ReSkill +12.7%), [[Workbench/logs/2026-06-10]] (LatentSkill 零 token overhead)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-06-25])

### [2026-06-25] Latent/weight-space 表示降低 reasoning 与 skill 的 token overhead

- **observation**: 把显式文本（CoT、skill 描述）迁移到 latent / weight space 可在保持性能的同时大幅削减 token：MIRAGE 将 explicit CoT 迁到 latent space，3-5x token reduction 下匹配显式 CoT；LatentSkill 用 hypernetwork 把文本 skill 编译为 LoRA adapter，实现零 token overhead 的可插拔 skill。机制都是避免中间文本的生成/解码开销
- **occurrences**: [[Workbench/logs/2026-06-07]] (MIRAGE 3-5x token reduction), [[Workbench/logs/2026-06-10]] (LatentSkill hypernetwork→LoRA, 零 token overhead)
- **confidence**: low
- **needs_verification**: yes

### [2026-06-25] 多模态模型的表观能力常由 spurious shortcut 驱动，需 counterfactual/intervention 诊断真实 evidence dependence

- **observation**: 评测中"看起来会"的多模态能力可能是 Clever Hans 式捷径：VisionSpeaksSound 揭示视频模型的"音频理解"实为视觉驱动，并用 Thud 反事实框架诊断；VisualFLIP / 近期 GUI grounding 讨论把评估从单点 accuracy 转向 counterfactual evidence dependence（grounding 是否真正依赖视觉证据）。说明诊断真实能力需要反事实/干预而非单点正确率
- **occurrences**: [[Workbench/logs/2026-05-25]] (VisionSpeaksSound, Thud 反事实诊断), [[Workbench/logs/2026-06-24]] (VisualFLIP: accuracy → counterfactual evidence dependence), [[Workbench/logs/2026-07-03]] (DecodableNotGrounded: 灰图 vision-ablation arbiter 推翻 probe+steering 验证的 latent-knowledge 结论，grounded/prior/inverted 三 regime)
- **confidence**: low
- **needs_verification**: yes
- **status**: → promoted to insight ([2026-07-03])

### [2026-06-25] Personal/professional CUA 的隐私风险主要来自 normal-use 的 contextual disclosure 而非 adversarial attack

- **observation**: personal computer-use agent 在正常使用中即会发生 inappropriate disclosure：AgentCIBench 以 contextual integrity framing 测得 frontier CUA 平均 leakage 67.9%；MyPCBench / BraveGuard 把个人桌面场景的隐私/安全作为系统性问题。风险来源从 adversarial attack 转向 normal-use contextual disclosure，指向 runtime intervention（task-scoped permission / trajectory privacy guard）而非单纯对抗防御
- **occurrences**: [[Workbench/logs/2026-06-24]] (MyPCBench, BraveGuard), [[Workbench/logs/2026-06-25]] (AgentCIBench leakage 67.9%)
- **confidence**: low
- **needs_verification**: yes

---
*Last distilled: 2026-07-03 (period 2026-06-26 ~ 2026-07-03)*

### [2026-07-03] Read-only evidence sub-agent 成为 agent 系统的通用模块原语

- **observation**: 多篇工作把 exploration/verification 拆给 read-only sub-agent 生成结构化中间证据，再由主模型/judge 聚合：FastContext 用 read-only 小模型 subagent 返回 file-line evidence 做 repository exploration（降 token 且提升 SWE 成功率）；Dockerless 派 read-only repository sub-agents 回答 verification questions 产出 evidence-backed answer，judge 聚合成 correctness score（SFT filter + RL reward）；PolicyGuard 用 sub-agent verifier 对 per-tool checklist 逐条判定 Met/Not Met 再决定 PASS/BLOCK+remediation。共同信号：verifier/context 的可靠性来自 evidence decomposition（结构化中间证据 + 聚合判断），而非端到端模型能力
- **occurrences**: [[Workbench/logs/2026-06-29]] (FastContext), [[Workbench/logs/2026-07-03]] (Dockerless, PolicyGuard)
- **confidence**: low
- **needs_verification**: yes
- **status**: → promoted to insight ([2026-07-03]，3 篇独立论文即达阈值)

### [2026-07-03] Agent runtime state 正被提升为有类型契约的一等对象

- **observation**: session / context / memory / UI semantic state 正从隐式 prompt 内容升级为一等、可编程、有 contract 的对象：OpenRath 把 Session 做成可随程序值流动的 first-class runtime value；MemGUI 的 Context-as-Action 把上下文压缩管理内化为与 UI 操作同策略的 first-class action；ArborHTR 用 Hypothesis Tree 维护 hypothesis/artifact/evidence/insight 的持久研究状态；LUMOS 把 UIA/DOM/accessibility tree 抽象成 semantic blueprint（stable element id + constrained action）；AgenticSTS 把 long-horizon memory 定义为 bounded typed contract。共同信号：runtime state 的显式对象化（typed、bounded、可重放）是 agent 基础设施的收敛方向
- **occurrences**: [[Workbench/logs/2026-06-26]] (OpenRath, MemGUI), [[Workbench/logs/2026-06-29]] (ArborHTR), [[Workbench/logs/2026-07-01]] (LUMOS), [[Workbench/logs/2026-07-03]] (AgenticSTS)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-03]，4 个独立日期 5 篇论文即达阈值)

---
*Last distilled: 2026-07-15 (period 2026-07-04 ~ 2026-07-15)*

### [2026-07-15] 失败轨迹正成为一等训练/改进资源，复用形态多样化

- **observation**: 多篇工作不再把失败 rollout 当废料，且复用形态分化为三类——**恢复监督**：VeriGUI 合成失败恢复轨迹、RoTS fragility-driven 分支合成 80 万恢复样本、Xiaomi-GUI-0 error-driven flywheel（teacher takeover 产出 deviation-diagnosis-recovery 段）、SRC 用 rollback 造纠正数据（下游 SFT +9.7~12.9pp）；**课程生成**：WebRL 把失败轨迹自动转成下一轮训练任务；**runtime patch**：LearningFromFailure 把失败轨迹经 LLM 诊断转成 inference-time code patch（OSWorld +6.6 零训练且跨 benchmark 迁移）。RealWorldGUIAgent-Reliability-Survey 已将"造失败→学恢复"标注为跨路线共同范式
- **occurrences**: [[Workbench/logs/2026-07-06]] (VeriGUI, RoTS, Xiaomi-GUI-0, LearningFromFailure, WebRL, Reliability-Survey), [[Workbench/logs/2026-07-08]] (SRC)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-15]，6 篇独立论文跨 2 日期即达阈值)

### [2026-07-15] Judge/reward model 可靠性被系统性测量且普遍不足

- **observation**: LLM judge / reward model 的可靠性正被专门 benchmark 量化，结果普遍不足：AgentRewardBench 12 个 judge precision ≤70%（rule-based 评测 recall 仅 55.9%）；Online-Mind2Web 诊断旧 benchmark judge 与人工一致性低是"进步幻觉"成因之一，自家 WebJudge 也仅 ~85%；任务合成家族共同软肋是 judge 噪声 8.6–19%；CUARewardBench 最佳单模型 ORM precision 仅 82.9%（general VLM 反超 CUA 专用模型），UPE 聚合换 precision 89.8% 的代价是 recall 56.8%。改进路径有二：蒸馏特化小 judge（OpenWebRL 89.8% 超 GPT-4o）与投票+弃权聚合（UPE）
- **occurrences**: [[Workbench/logs/2026-07-06]] (Online-Mind2Web), [[Workbench/logs/2026-07-07]] (AgentRewardBench), [[Workbench/logs/2026-07-08]] (OpenWebRL 蒸馏 judge、任务合成家族 judge 噪声), [[Workbench/logs/2026-07-15]] (CUARewardBench)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-15]，4 个独立日期即达阈值)

### [2026-07-15] 工业系统技术报告 claim-evidence 错位成常态

- **observation**: 近期工业/大厂技术报告的 headline 数字系统性缺乏支撑：Xiaomi-GUI-0（无 ablation + RealMobile 非公开）、AlayaWorld（零定量 benchmark/消融）、AgenticAISupervisor（仅 case study 无量化）、Gemma4（thinking 贡献未拆解、几乎不与同代竞品对表）、ABot-AgentOS（self-evolution 8-split 仅存活 1 asset 但叙事为亮点）、ABot-N1（全文零 ablation + 自建 benchmark 未声明 train/test 隔离）、AgentReadyWeb（自建 baseline 有 strawman 风险）、LongHorizonTerminalBench（正文自相矛盾）；07-13 daily 已总结为"本周通病：claim 与证据错位"
- **occurrences**: [[Workbench/logs/2026-07-06]] (Xiaomi-GUI-0), [[Workbench/logs/2026-07-13]] (AlayaWorld, AgenticAISupervisor, Gemma4, daily 总结), [[Workbench/logs/2026-07-14]] (ABot-AgentOS, LongHorizonTerminalBench), [[Workbench/logs/2026-07-15]] (ABot-N1, AgentReadyWeb)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-15]，4 个独立日期即达阈值)

### [2026-07-15] Engine-level 原语的 agent-facing 暴露空白正被快速填补

- **observation**: WebEnvironment-Engine-Survey 确认六轴环境能力全部服务 trainer/evaluator、无人把 fork/verify 暴露给 agent 本身；但次日 AgentRuntimePrimitives-Survey 的 gap 核查推翻该先验——系统社区已入场（AgenticExplorationSystems 议程），Crab 已在 sandbox 域把 rollback 暴露为 agent 工具（但只测效率不测 success 因果增益）。AFE 差异化空间收窄至三点：web 全栈状态 fork、success/recovery 因果增益 + prompt-only 对照、affordance 组合消融
- **occurrences**: [[Workbench/logs/2026-07-07]] (WebEnvironment-Engine-Survey Takeaway 6), [[Workbench/logs/2026-07-08]] (AgentRuntimePrimitives-Survey gap 核查, Crab, AgenticExplorationSystems), [[Workbench/logs/2026-07-23]] (ObjectCentricEnv：把环境经验固化为可执行 object model——state/affordance/constraint/transition 编成 Python 类，是 agent-facing 状态暴露的一种具体实现), [[Workbench/logs/2026-07-27]] (Reports/2026-07-27-Agent-Friendly-Browser-Interaction-Rules：22 条规则分三个证据层 + 4 条被推翻，说明"什么该暴露"已进入可证伪阶段而非提案阶段), [[Workbench/logs/2026-07-28]] (GUIvsCLI 440 任务 matched 对照：模态本身不是瓶颈——screen-only GUI 59.1% > original-skill CLI 48.2%，但 verifier-guided skill 修补把 CLI 推到 69.3%)
- **source_ids**: `paper:arxiv:2607.02846` (ObjectCentricEnv), `paper:arxiv:2606.24551` (GUIvsCLI), `paper:arxiv:2607.22368` (ProtocolValidity)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30])

### [2026-07-15] GRPO 增益条件化：需要 headroom 或外部监督注入

- **observation**: GRPO 的适用条件正被受控实验界定：GRPONullWebAgent 用 18 组控制网格证明 GRPO 对已 mastered 任务无可信提升（增益条件 = reward 可由采样到达，即 sampled policy 成功率高于 greedy；无 headroom 时中高学习率反而 degrade/collapse）；MAG 中纯 GRPO 不够、需 expert 轨迹注入才能把 9B SR 从 6.9% 翻倍到 13.2%
- **occurrences**: [[Workbench/logs/2026-07-14]] (MAG expert-augmented GRPO), [[Workbench/logs/2026-07-15]] (GRPONullWebAgent 受控阴性结果), [[Workbench/logs/2026-07-28]] (PassKT 受控三臂 base/SFT/RL 同 200 题：RL 是否"扩展能力"取决于 base 分布是否稀疏含被奖励策略——与 GRPONullWebAgent 的 sampled-policy-support 判据是同一结论的第三个独立表述，从能力边界侧而非训练收益侧)
- **source_ids**: `paper:arxiv:2607.12640` (GRPONullWebAgent), `paper:arxiv:2607.10079` (MAG), `paper:arxiv:2604.14877` (PassKT)
- **confidence**: medium (↑ from low，第三个独立 source 从正交侧面给出同一 headroom 判据)
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30])

### [2026-07-15] On-policy distillation 成为复用 RL 成果的迁移机制

- **observation**: 迁移对象正从"最终模型分布"转向"RL 诱导的 policy shift"：UI-MOPD 用 platform-conditioned multi-teacher on-policy distillation 把 desktop/mobile 两个 32B expert 蒸进共享 8B student（缓解跨平台行为混淆与遗忘）；Direct-OPD 把 teacher RL 前后 checkpoint 的 log-ratio 当 implicit dense reward 在 student on-policy 状态上迁移 RL 增量（weak-to-strong，Qwen3-1.7B AIME24 48.3→58.3，4h×8 A100）
- **occurrences**: [[Workbench/logs/2026-07-13]] (UI-MOPD platform-conditioned multi-teacher), [[Workbench/logs/2026-07-15]] (Direct-OPD log-ratio implicit dense reward), [[Workbench/logs/2026-07-19]] (Agents-A1 Stage 3 multi-teacher domain-routed OPD + salient vocabulary alignment，把 domain expert 增量蒸进 35B MoE student——第三个独立数据点)
- **source_ids**: `paper:arxiv:2607.04425` (UI-MOPD), `paper:arxiv:2607.05394` (Direct-OPD), `paper:arxiv:2606.30616` (Agents-A1)
- **confidence**: medium (↑ from low，三种不同 routing/reward 形态收敛到同一迁移对象)
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30])

### [2026-07-15] 自演化收益受演化步验证缺失所限

- **observation**: SelfEvolvingAgents-Survey 发现"反馈信号可验证性是四条演化路线共同的成败分界"，且四路线中仅 tool/skill 路线内建演化步验证关口——evolution-step verifier gating 是方法空白；Misevolution (ICLR'26) 实证四路径演化偏航；工业侧 ABot-AgentOS 的 split-wise gated self-evolution 8 个 split 仅存活 1 个 asset（增益 +0.4~1.2），印证无验证关口时演化资产存活率极低。07-14 idea-generate 已产出 2 个针对该空白的 idea（probe-gate 准入 + 检索正反馈干预）
- **occurrences**: [[Workbench/logs/2026-07-09]] (SelfEvolvingAgents-Survey, Misevolution), [[Workbench/logs/2026-07-14]] (ABot-AgentOS, idea-generate), [[Workbench/logs/2026-07-22]] (GRASP：去验收闸门 88.8%→63.5%/40.1%，且"配平探针算力但丢弃验证结论"塌回 67–71%), [[Workbench/logs/2026-07-23]] (SKILL.nb：No gates 32.6%SR/18.6%回归 vs 完整 38.4%/3.3%；ASG-SI 提出 audited skill graph 但零实证), [[Workbench/logs/2026-07-28]] (SkillMemoryBudget：AWM/ASI/ReasoningBank 在等 token 预算下被 vanilla 追平/反超，其自带验收环节不足以过滤约半数失败轨迹资产), [[Workbench/logs/2026-07-29]] (SelfEvolvingAgents-Survey 20 篇重构把该 Open Problem 从"方法空白"改写为"闸门已存在但只覆盖性能回归，安全维度空白且 self-review gate 易 rubber-stamp")
- **source_ids**: `paper:arxiv:2605.29668` (GRASP), `paper:arxiv:2606.08049` (SKILL.nb), `paper:arxiv:2606.15017` (SkillMemoryBudget), `paper:arxiv:2607.14777` (SEED 静态 skill library −7.4), `paper:arxiv:2512.23760` (ASG-SI，设计提案无实证), `paper:arxiv:2604.16968` (ExperienceSafetyRisks)
- **confidence**: medium (↑ from low)
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30])，且归因方向发生反转：原判断"缺闸门"已被证伪为"闸门存在且是收益主承重件"，见 insight [2026-07-30]

---
*Last distilled: 2026-07-30 (period 2026-07-16 ~ 2026-07-30)*

### [2026-07-30] 预算/口径匹配对照正在系统性推翻 agent 增强方法的既有增益声明

- **observation**: 本期出现一批以"补上对照"为核心贡献的工作，且结论高度一致——增强模块的报告增益有相当比例来自未被计入的额外预算或不可比的口径。SkillMemoryBudget 给 vanilla actor 等 token 预算（10→15 步 + 规则化 AXTree 剪枝），三模型 × 三 WebArena 域下 AWM/ASI/ReasoningBank 被全面追平或反超；AgentOccam 的 per-step token 反而高于 vanilla（2930.9 vs 2210.2），说明其增益来自动作空间对齐而非"省上下文"；AgentsThatMatter 指出不控 cost 时 retry 即可刷高 accuracy，HAL 用 21,730 rollout 证明最贵模型极少落在 accuracy–cost Pareto 前沿；GUIvsCLI 用 440 任务、同目标/同初态/同 verifier 的 matched 对照推翻"CLI/API 优于 GUI"这一高频主张；MuonAgenticRL 显示仅换 optimizer 就能在同一 ALFWorld/GiGPO 配置上把 final checkpoint 从 0.320 抬到 0.633（单 seed、0.5B），意味着跨论文比数字在优化器不统一时无效；TeachStop 直接指出多数 agentic RL 只报单次 run，无法与 data draw / seed / runtime nondeterminism 分离
- **occurrences**: [[Workbench/logs/2026-07-22]] (AgentsThatMatter, HAL), [[Workbench/logs/2026-07-23]] (AgentOccam, TeachStop), [[Workbench/logs/2026-07-27]] (MuonAgenticRL 量纲警告写入 WebAgent-RL 报告), [[Workbench/logs/2026-07-28]] (SkillMemoryBudget, GUIvsCLI, ActiveContextCurator 的 token 计数未含 curator 自身开销)
- **evidence**: token-matched vanilla 追平三种 online 增强；AgentOccam per-step token 2930.9 > 2210.2；GUI 59.1% vs CLI 48.2%（matched）→ verifier-guided skill 修补后 CLI 69.3%；Muon/AdamW matched run 0.633 vs 0.320
- **source_ids**: `paper:arxiv:2606.15017` (SkillMemoryBudget), `paper:arxiv:2410.13825` (AgentOccam), `paper:arxiv:2606.24551` (GUIvsCLI), `paper:arxiv:2407.01502` (AgentsThatMatter), `paper:arxiv:2510.11977` (HAL), `paper:arxiv:2607.16169` (MuonAgenticRL), `paper:arxiv:2607.17136` (TeachStop), `paper:arxiv:2604.11462` (ActiveContextCurator)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30]，8 个独立 source、4 个独立日期)

### [2026-07-30] 上下文/观察表示的最优点是 backbone 能力 × 任务阶段的非单调函数，而非单调"越少越好"

- **observation**: "压缩/削减观察普遍有益"在本期被三类独立实验否定，且否定方向一致地指向"条件化 + 非平稳"。ReadMoreThinkMore 在 WorkArena L1 上交叉 backbone × thinking budget：强模型用原始 HTML 反而大幅优于 a11y tree（gpt-5.1 high +17.5、claude-sonnet-4-6 +14.6），弱模型则严重退化（gpt-oss-20b −18.8、Llama-3.1-70B −14.6）；MaskingRegimeMap 用 9 个 backbone × 多 retriever 网格测出不对称倒 U——弱 retriever 下 +6.2~6.6、强 retriever × 中等模型达峰 +11.7、模型饱和时塌到 +0.1 甚至 live-web −4.8；FoldAct 显示 folding 策略在长程内部非平稳（step 173 处崩溃）；NaiveVisualMemory 拆出整屏视觉记忆降低 state-level 失败却放大 action-level 失败；HiViG 报告五种既有 critic 对强 policy 增益近零或为负。共同结构是：增益方向随"底座能力 / 检索质量 / 任务进行到第几步"翻转，任何只在单一 setting 报告的削减收益都不可外推
- **occurrences**: [[Workbench/logs/2026-07-20]] (HiViG：既有 critic 对强 policy 近零/负增益), [[Workbench/logs/2026-07-23]] (ReadMoreThinkMore, NaiveVisualMemory, A11yCompressor 效率大而精度小且脆), [[Workbench/logs/2026-07-28]] (MaskingRegimeMap 倒 U 网格, FoldAct 非平稳崩溃, ActiveContextCurator 用分工替代统一动作空间)
- **evidence**: +17.5/−18.8 的同一干预反向；倒 U 从 +11.7 到 −4.8；FoldAct step 173 collapse
- **source_ids**: `paper:arxiv:2604.01535` (ReadMoreThinkMore), `paper:arxiv:2606.00408` (MaskingRegimeMap), `paper:arxiv:2512.22733` (FoldAct), `paper:arxiv:2606.14106` (NaiveVisualMemory), `paper:arxiv:2606.11078` (HiViG), `paper:arxiv:2605.00551` (A11yCompressor), `paper:arxiv:2604.11462` (ActiveContextCurator)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30]，7 个独立 source、3 个独立日期)

### [2026-07-30] GUI 长程失败的主导形态是"自称完成"，有效对策收敛到执行后状态取证而非文本判分

- **observation**: 失败模式侧与判定方法侧在本期对上了。失败侧：VLAA-GUI 在 OSWorld-Verified 上量到即便强制每步 Completeness Verifier，False Done/Failed 仍 >86%（被接受的完成宣告约 1/4 是错的）；OS-Marathon 把"做完头几条 sub-workflow 就自行终止"列为三大失败模式之一；StateAct 把独立 finish gate（只看原始指令与机器访问权，看不到 trajectory/plan/rationale）作为 harness 的承重组件。方法侧：能突破 judge 精度天花板的三项工作都放弃了"被动读截图/读文本"——VAGEN 让 verifier agent 在轨迹结束后主动调截图/shell/python 探测环境，OSWorld-Verified 人评 GT 上 94.0 P / 92.9 Acc（最强 passive baseline 84.7 Acc），弱 actor 的不平衡设定下仍守住 88.5 P 而 judge 类崩到 ~75%；IRA 用 propose-then-verify + system/application/GUI 三类工具在 post-execution 环境逐条核验，GUI-RewardBench 86.9% 超全部 passive evaluator；SeekJudge 把长轨迹判分拆成 localization/extraction 四角色并蒸馏进单个 9B backbone。共同机制：判定可靠性来自"能不能回到环境里取证"，而不是模型更大或 prompt 更严
- **occurrences**: [[Workbench/logs/2026-07-20]] (VLAA-GUI FDF>86%, VAGEN 94.0 P, OS-Marathon 过早终止, HiViG 视觉锚定 critic), [[Workbench/logs/2026-07-28]] (StateAct 独立 finish gate, SeekJudge 9B 蒸馏), [[Workbench/logs/2026-07-29]] (IRA 86.9% + RL 闭环 34.0 vs script 34.9)
- **evidence**: FDF >86%（加 verifier 后仍然）；VAGEN 94.0 P/92.9 Acc vs FullTrajEval 84.7 Acc；IRA 86.9% vs 最佳 passive 78.8%
- **source_ids**: `paper:arxiv:2604.21375` (VLAA-GUI), `paper:arxiv:2601.20650` (OS-Marathon), `paper:arxiv:2607.22798` (StateAct), `paper:arxiv:2602.00575` (VAGEN), `paper:arxiv:2607.25904` (IRA), `paper:arxiv:2607.23263` (SeekJudge), `paper:arxiv:2606.11078` (HiViG)
- **confidence**: medium
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30]，7 个独立 source、3 个独立日期)

### [2026-07-30] Agent 的内部信念缺 provenance，是一个可被环境注入、且自身无法纠正的失败面

- **observation**: 三项独立工作从不同入口测到同一件事：agent 无法追踪"我为什么相信这条状态"，因而既分不清结论来自像素还是过期结构化文本，也分不清来自可信 workspace 还是环境注入。GUIStateBelief 用 735 个 probe（含 38 个真实网站挖出的 225 个零编辑 divergence、250 个 mobile stale-node candidate）证明 screenshot 与 DOM/AXTree 冲突时 agent 大量走结构化文本捷径；EnvTrustBench 把"把环境里看到的 claim 当证据、不与真实状态核对"形式化为 evidence-grounding defect，14 个 stack × 3,850 次 run 聚合 EMR 83.3%；AlwaysOnAgents 转述的 RECLAIM 结果给出机制解释——保留 stale 结论却丢弃来源的记忆会变得"confidently uncorrectable，且严格劣于空记忆"，而 source-first write policy 可修复。缓解手段目前都有硬代价：pixel-priority prompt 在 belief probe 上有效但几乎不降 action 层 hijack，certificate check 会阻断 59%–77% 的冲突动作
- **occurrences**: [[Workbench/logs/2026-07-21]] (GUIStateBelief 735 probes / consistency gate 是唯一同时降 hijack 与 task error 的方案), [[Workbench/logs/2026-07-23]] (EnvTrustBench EMR 83.3%, AlwaysOnAgents/RECLAIM provenance 失败, NaiveVisualMemory 视觉记忆引入的 state 误判)
- **evidence**: EMR 83.3%（3,206/3,850 run 误接地）；certificate check 阻断率 59%–77%；"confidently uncorrectable 且严格劣于空记忆"
- **source_ids**: `paper:arxiv:2607.04334` (GUIStateBelief), `paper:arxiv:2605.08828` (EnvTrustBench), `paper:arxiv:2606.30306` (AlwaysOnAgents，RECLAIM 为其转述被引工作，非自跑实验), `paper:arxiv:2606.14106` (NaiveVisualMemory)
- **confidence**: low
- **needs_verification**: no
- **status**: → promoted to insight ([2026-07-30]，3 个独立一手 source)

### [2026-07-30] 学术 preprint 的正文级数字错误与 overclaim 同样是常态，独立核验命中率稳定非零

- **observation**: 本期例行 verifier pass 在学术 preprint（非工业技术报告）上持续命中论文自身正文的数字/表述缺陷，跨 4 个独立日期无一次空手：STLiteKV 的"7.3% average"实为单 cell 最大值；Prune4Web 把非可执行产物称作 "executable Python scripts"；OVOD-Agent 有 3 处内部数字互相矛盾；MetaTeam 有 4 处 contradicted（GAIA 实为 77.3 而非正文的 87.9）；ActiveContextCurator 域数自相矛盾（四域 vs 五域）且 token 计数未含 curator 开销；ElementOrdering 存在跨数据集过度推断；FoldAct 的 p_drop 消融非均匀。这是既有 insight"工业技术报告 headline 应默认降权"的**范围扩展**——错位不是工业报告独有，而是同行评议前文本的普遍状态，意味着 digest 流程里的独立核验步骤不是可选优化项
- **occurrences**: [[Workbench/logs/2026-07-23]] (STLiteKV, Prune4Web；CUA-Survey codex 交叉核查另抓 9 处 overclaim), [[Workbench/logs/2026-07-24]] (OVOD-Agent 3 处), [[Workbench/logs/2026-07-28]] (ActiveContextCurator, ElementOrdering, FoldAct), [[Workbench/logs/2026-07-29]] (MetaTeam 4 处)
- **evidence**: 7 篇被点名的正文级缺陷，全部由 digest 时的独立核验步骤而非作者声明发现
- **source_ids**: `paper:arxiv:2603.00188` (STLiteKV), `paper:arxiv:2511.21398` (Prune4Web), `paper:arxiv:2511.21064` (OVOD-Agent), `paper:arxiv:2605.29790` (MetaTeam), `paper:arxiv:2604.11462` (ActiveContextCurator), `paper:arxiv:2409.12089` (ElementOrdering), `paper:arxiv:2512.22733` (FoldAct)
- **confidence**: medium
- **needs_verification**: no
- **status**: 保留为 pattern——可操作结论已被既有 insight「工业技术报告 headline 降权」覆盖，本条只扩展其适用范围，暂不单独立 insight