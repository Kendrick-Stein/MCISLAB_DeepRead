# Insights

> Memory file for distilled research insights

## Key Insights

- GUI Agent field is rapidly evolving with 2024-2025 seeing significant advances
- Most systems use multimodal LLMs as the core reasoning engine
- Evaluation benchmarks vary significantly (WebCanvas, GUIOdyssey, etc.)

## Method Observations

- Action grounding is a core challenge across approaches
- Some systems use coordinate-based actions, others use semantic/element-based
- Self-improving agents (UI-Genie) show promise for continual learning

## Performance Insights

- Dataset quality significantly impacts agent performance
- Screen understanding (OCR, element detection) is a bottleneck
- Cross-app transfer remains challenging

---

*Last distilled: 2026-05-03*

### [2026-05-03] GUI Agent evaluation shifting from binary success to process-level multi-dimensional diagnosis

- **claim**: GUI Agent/Workflow automation benchmark 正从 binary success/failure 演进为 process-level evaluation、multi-dimensional capability diagnosis、和 systematic failure mode analysis——这种 shift 是 field mature 的必要阶段
- **evidence**: 
  - [[Workbench/logs/2026-04-28]] (AutoGUIv2 multi-dimensional, ReVSI frame budget variant)
  - [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 四路证据 triangulation, Visual Generation Taxonomy critique of perceptual-only metrics)
  - [[Workbench/logs/2026-05-04]] (AutoGUI-v2 VLM dichotomy: grounding vs captioning 能力分离，irregular region + complex interaction 失败分析，plausible distractors trick 模型)
- **confidence**: medium (↑ from low，AutoGUI-v2 提供 dichotomy + failure mode 分析的细粒度 evidence)
- **source**: cross-validation
- **impact**: GUI Agent benchmark design，evaluation protocol 标准化，model selection（开源 grounding 强，商业 captioning 强）
- **status**: validated (↑ from provisional，AutoGUI-v2 的 systematic failure mode 分析证实 multi-dimensional diagnosis 的必要性)

### [2026-05-04] VLM grounding vs captioning capability dichotomy

- **claim**: Open-source models fine-tuned on agent data（Qwen3-VL）在功能性 grounding（"where"）上超越商业模型，但商业模型（Gemini-2.5-Pro）在功能性 captioning（"what"）上更强——说明 fine-tuning 的 value proposition 对 grounding task 有显著增益，但 deep functional understanding（transition logic、uncommon actions）仍是所有模型的短板
- **evidence**: [[Papers/2604-AutoGUIv2]] (AutoGUI-v2 benchmark evaluation on 2,753 tasks across 6 OS)
- **confidence**: medium
- **source**: single-paper
- **impact**: Model selection for GUI Agent（开源模型更适合 grounding-heavy task，商业模型更适合 reasoning-heavy task），training strategy（fine-tuning on agent data 对 grounding 有利）
- **status**: provisional

---

*Last distilled: 2026-06-25 (period 2026-05-19 ~ 2026-06-25)*

### [2026-06-25] 真实长程/组合工作流远未饱和，frontier model 成功率极低

- **claim**: 在真实、长程、可执行的专业/组合工作流上，frontier model 的端到端成功率远低于 curated benchmark——多数场景 <30%，最难场景接近个位数；真实场景的难度被静态 benchmark 系统性低估
- **evidence**: [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 66.7%), [[Workbench/logs/2026-04-28]] (Odysseys 44.5%), [[Workbench/logs/2026-05-25]] (CHIBench 28.0% pass@1), [[Workbench/logs/2026-06-10]] (SpatialWorld GPT-5 17.4%, SWEExplore line-recall 0.14-0.19), [[Workbench/logs/2026-06-24]] (SaaSBench resolved 3.8%)
- **confidence**: medium
- **source**: cross-validation
- **impact**: Agent benchmark 设计（应转向真实长程组合任务）、Agent-Facing Environment Runtime 方向（执行期可观测/可恢复/可验证能力是提升长程可靠性的杠杆）、问题 framing（成功率天花板说明这是 capability gap 而非评测噪声）
- **status**: validated (≥3 独立来源 + 跨日期 + 跨任务类型一致，从 provisional 升级)

### [2026-06-25] Verifier/环境 oracle 正从 evaluator-only 扩展为 training supervision 与 agent-facing runtime affordance

- **claim**: programmatic verifier / environment oracle 的价值不止于事后判分——它可作为高质量训练监督来源，并可（在 non-oracle 边界内）暴露为 agent-facing runtime affordance；这一角色迁移是 GUI/CUA environment 研究从 benchmark construction 转向 runtime infrastructure 的核心
- **evidence**: [[Workbench/logs/2026-05-22]] (OpenComputer verifier 94.1% vs LLM judge 79.2%), [[Workbench/logs/2026-06-22]] (GUI-Environment-Survey: Verification 作为组织原则), [[Workbench/logs/2026-06-23]] (AgentFriendlyEnvironment-Proposal), [[Workbench/logs/2026-06-24]] (ENVS: 环境 oracle → SFT 监督)
- **confidence**: medium
- **source**: cross-validation
- **impact**: Agent-Facing Environment Runtime 方向（直接是其核心假设的证据基础）、[[Ideas/AgentFacing-WebRuntime]]、[[Ideas/HybridVerifier-GUIRuntime]]、verifier leak 边界设计（evaluator-only vs agent-safe probe vs hidden verifier 三层分离）
- **status**: provisional

### [2026-06-25] Agent skill 正成为可治理/可训练/可执行/可编译的一等对象

- **claim**: agent "skill" 正从 prompt 中的自然语言建议演化为有独立生命周期的一等对象——可被治理（evidence-gated update）、训练（optimizer/RL-in-loop）、执行（program function）、编译（latent/weight space），多数声称零/低部署成本；这开辟了"在不更新基座模型的前提下持续提升 frozen agent"的工程路径
- **evidence**: [[Workbench/logs/2026-05-22]] (SkillsVote, MMSkills, HASP), [[Workbench/logs/2026-05-25]] (SkillOpt +23.5, ColleagueSkill), [[Workbench/logs/2026-06-07]] (ReSkill +12.7%), [[Workbench/logs/2026-06-10]] (LatentSkill 零 token overhead)
- **confidence**: medium
- **source**: cross-validation
- **impact**: training-free agent improvement 路径、skill 治理与负迁移风险（ColleagueSkill 警示）、与 Agent-Facing Environment Runtime 的连接（skill 作为可执行 affordance 的一种形式）
- **status**: provisional