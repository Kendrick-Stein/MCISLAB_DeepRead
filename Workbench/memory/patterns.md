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