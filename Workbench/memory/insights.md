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
- **evidence**: [[Workbench/logs/2026-05-03]] (Claw-Eval-Live 66.7%), [[Workbench/logs/2026-04-28]] (Odysseys 44.5%), [[Workbench/logs/2026-05-25]] (CHIBench 28.0% pass@1), [[Workbench/logs/2026-06-10]] (SpatialWorld GPT-5 17.4%, SWEExplore line-recall 0.14-0.19), [[Workbench/logs/2026-06-24]] (SaaSBench resolved 3.8%), [[Workbench/logs/2026-06-29]] (OSWorld 2.0: 108 个人类小时级工作流上最强 Claude Opus 4.8 仅 20.6% binary completion，瓶颈为隐式状态维护/动态约束/验证/自我修复), [[Workbench/logs/2026-07-06]] (AndroidDaily 真实闭源 app 最强 Gemini 3 Flash 仅 62.0%；Online-Mind2Web：live 站点上多数 agent 退回 SeeAct 水平、仅 Operator ~61%), [[Workbench/logs/2026-07-14]] (Long-Horizon-Terminal-Bench 最强 28.3%@R≥0.95、全模型均值 4.3%；MAG frontier 最高仅 37.4%)
- **confidence**: medium
- **source**: cross-validation
- **impact**: Agent benchmark 设计（应转向真实长程组合任务）、Agent-Facing Environment Runtime 方向（执行期可观测/可恢复/可验证能力是提升长程可靠性的杠杆）、问题 framing（成功率天花板说明这是 capability gap 而非评测噪声）
- **status**: validated (≥3 独立来源 + 跨日期 + 跨任务类型一致，从 provisional 升级)

### [2026-06-25] Verifier/环境 oracle 正从 evaluator-only 扩展为 training supervision 与 agent-facing runtime affordance

- **claim**: programmatic verifier / environment oracle 的价值不止于事后判分——它可作为高质量训练监督来源，并可（在 non-oracle 边界内）暴露为 agent-facing runtime affordance；这一角色迁移是 GUI/CUA environment 研究从 benchmark construction 转向 runtime infrastructure 的核心
- **evidence**: [[Workbench/logs/2026-05-22]] (OpenComputer verifier 94.1% vs LLM judge 79.2%), [[Workbench/logs/2026-06-22]] (GUI-Environment-Survey: Verification 作为组织原则), [[Workbench/logs/2026-06-23]] (AgentFriendlyEnvironment-Proposal), [[Workbench/logs/2026-06-24]] (ENVS: 环境 oracle → SFT 监督), [[Workbench/logs/2026-07-03]] (Dockerless: evidence-grounded verifier 同时做 SFT filter 与 GRPO reward，接近 test-execution RL; PolicyGuard: pre-execution sub-agent verifier 作为 runtime affordance，Pass⁴ +6~12pp), [[Workbench/logs/2026-07-07]] (DreamGym: CoT 经验模型合成转移+reward 追平 80K 真实交互; InSTA: $521→2.2M 轨迹任务工厂), [[Workbench/logs/2026-07-08]] (WAC/AgentSynth/UI-Simulator/WebSynthesis: environment/verifier/simulator 已成训练信号生产系统而非仅 evaluation backend), [[Workbench/logs/2026-07-09]] (SelfEvolvingAgents-Survey: 反馈信号可验证性是四条自演化路线共同的成败分界)
- **confidence**: medium
- **source**: cross-validation
- **impact**: Agent-Facing Environment Runtime 方向（直接是其核心假设的证据基础）、[[Ideas/AgentFacing-WebRuntime]]、[[Ideas/HybridVerifier-GUIRuntime]]、verifier leak 边界设计（evaluator-only vs agent-safe probe vs hidden verifier 三层分离）
- **status**: validated (2026-07-03 升级：Dockerless 在 SWE 域实证 training supervision 角色、PolicyGuard 在 dialogue/tool-call 域实证 runtime affordance 角色，两个新域独立复现角色迁移)

### [2026-06-25] Agent skill 正成为可治理/可训练/可执行/可编译的一等对象

- **claim**: agent "skill" 正从 prompt 中的自然语言建议演化为有独立生命周期的一等对象——可被治理（evidence-gated update）、训练（optimizer/RL-in-loop）、执行（program function）、编译（latent/weight space），多数声称零/低部署成本；这开辟了"在不更新基座模型的前提下持续提升 frozen agent"的工程路径
- **evidence**: [[Workbench/logs/2026-05-22]] (SkillsVote, MMSkills, HASP), [[Workbench/logs/2026-05-25]] (SkillOpt +23.5, ColleagueSkill), [[Workbench/logs/2026-06-07]] (ReSkill +12.7%), [[Workbench/logs/2026-06-10]] (LatentSkill 零 token overhead)
- **confidence**: medium
- **source**: cross-validation
- **impact**: training-free agent improvement 路径、skill 治理与负迁移风险（ColleagueSkill 警示）、与 Agent-Facing Environment Runtime 的连接（skill 作为可执行 affordance 的一种形式）
- **status**: provisional

---

*Last distilled: 2026-07-03 (period 2026-06-26 ~ 2026-07-03)*

### [2026-07-03] 多模态表观能力需 counterfactual/intervention 诊断，accuracy 与 probe/steering 均会高估 grounding

- **claim**: 评测 accuracy、linear probing、steering recovery 都会系统性高估多模态模型对感知证据的真实依赖；只有 counterfactual/intervention 对照（音频置换、图像 ablation、灰图 arbiter）能区分 grounded / prior / inverted 三种 regime——其中 inverted（可解码但符号用反、低于 chance）是 probing 和 steering 结构性看不见的失败模式
- **evidence**: [[Workbench/logs/2026-05-25]] (VisionSpeaksSound: 视频模型"音频理解"实为视觉驱动，Thud 反事实诊断), [[Workbench/logs/2026-06-24]] (VisualFLIP: 评估从单点 accuracy 转向 counterfactual evidence dependence), [[Workbench/logs/2026-07-03]] (DecodableNotGrounded: 灰图 arbiter 揭示 vertical 是 prior、depth inverted，training-free "recovery" 是 prior amplification), [[Workbench/logs/2026-07-13]] (Video-Oasis: 无视觉/无时序捷径 ablation + 5 模型共识审计 14 个视频 benchmark，55% 样本可被捷径攻破，剔除后 SOTA 仅略高于随机；oracle grounding 对照定位时序瓶颈), [[Workbench/logs/2026-07-15]] (VisualAccessBoundary: Visual Access Sweep 层×时间因果掩蔽定位 CoT 的视觉访问边界，CoT 增益受 perceptual readout 制约而非延长图像访问)
- **confidence**: medium (↑ from low，2026-07-15：5 个独立日期的 intervention 诊断结论一致)
- **source**: cross-validation
- **impact**: [[Ideas/EvidenceDependence-GUIGrounding]]（Action Collapse Rate 即 GUI 版 arbiter，可升级为三 regime 分类 + 五 ablation protocol）、GUI Grounding Robustness 评估协议（分辨率鲁棒性可分解为 evidence loss vs prior reliance）、对一切 "unlocked latent capability" claim 的默认审查要求
- **status**: validated (2026-07-15 升级：音频置换/灰图 arbiter/捷径 ablation 共识/视觉访问因果掩蔽等 5 个独立日期、跨模态的 intervention 诊断均揭示 accuracy 系统性高估真实 evidence dependence)

### [2026-07-03] 小型专门化模型可达大模型级 GUI grounding

- **claim**: GUI grounding 不需要通用大规模 VLM 的推理容量：0.2B–4B 的专门化模型（GoClick 230M encoder-decoder、ZonUI-3B 3B+LoRA+24K 样本、AFRAgent 4B feature renormalization）通过数据多样性、分辨率专门化和架构适配即可达到或接近大模型 grounding accuracy，且推理成本显著更低
- **evidence**: [[Workbench/logs/2026-04-28]] (GoClick 230M), [[Workbench/logs/2026-06-26]] (ZonUI-3B ScreenSpot 84.9 单卡可训; AFRAgent 低 FLOPs/latency 强 action prediction)
- **confidence**: low
- **source**: cross-validation
- **impact**: GUI Grounding Robustness 方向的实验预算假设（原型验证可用 3B 级模型）、grounding 与 reasoning 的能力分解（与 AutoGUI-v2 dichotomy insight 互证）、production 部署成本 pattern
- **status**: provisional

### [2026-07-03] Read-only evidence sub-agent 成为 agent 系统的通用模块原语

- **claim**: 把 exploration/verification 拆给 read-only sub-agent 生成结构化中间证据（file-line evidence、verification QA、checklist 判定），再由主模型/judge 聚合，能同时降低主模型 token 成本并提升可靠性；verifier 的可靠性来自 evidence decomposition 而非端到端模型能力
- **evidence**: [[Workbench/logs/2026-06-29]] (FastContext: read-only 小模型 subagent 返回 file-line evidence，SWE 成功率升 + token 降), [[Workbench/logs/2026-07-03]] (Dockerless: verification questions → read-only repo sub-agents → judge，81.0 AUC 超最强 frontier LLM judge; PolicyGuard: checklist 逐条判定 + remediation，recall 100% 且 block rate 减半), [[Workbench/logs/2026-07-08]] (Vera: evidence-grounded verification 以环境状态证据为准的 state⊳tool⊳resp 非对称判定消除 false positive——支持 evidence-decomposition 半边，非 sub-agent 形态)
- **confidence**: low
- **source**: cross-validation
- **impact**: [[Ideas/HybridVerifier-GUIRuntime]] 与 AFE-MiniSuite 的 verify affordance 设计（verifier 子代理回答固定类别问题再聚合，而非直接给 success label）、与 "Verifier 角色迁移" validated insight 互补（那条讲角色，这条讲实现形态）
- **status**: provisional

### [2026-07-03] Agent runtime state 正被提升为有类型契约的一等对象

- **claim**: agent 的 runtime state（session、context、memory、UI semantic state、research state）正从隐式 prompt 内容收敛为一等、可编程、有类型契约的对象——typed、bounded、可重放、可随程序值流动；这为 agent-facing observable affordance 提供了工程收敛证据
- **evidence**: [[Workbench/logs/2026-06-26]] (OpenRath: Session as first-class runtime value; MemGUI: Context-as-Action), [[Workbench/logs/2026-06-29]] (ArborHTR: hypothesis/artifact/evidence/insight 持久研究状态), [[Workbench/logs/2026-07-01]] (LUMOS: UIA/DOM → semantic blueprint + stable element id), [[Workbench/logs/2026-07-03]] (AgenticSTS: memory as bounded typed contract)
- **confidence**: medium
- **source**: cross-validation
- **impact**: Agent-Facing Environment Runtime 的 observe/map affordance 设计（state contract 是 affordance 的接口形式）、[[Ideas/AgentFacing-WebRuntime]]、agent memory 研究（[[Papers/2606-AgentMemorySystem]] 显示 GUI/CUA visual memory 仍空白）
- **status**: provisional

---

*Last distilled: 2026-07-15 (period 2026-07-04 ~ 2026-07-15)*

### [2026-07-15] 失败轨迹是一等训练/改进资源，复用形态是新的方法区分轴

- **claim**: 失败 rollout 含可系统复用的监督信号，丢弃它等于浪费 verifiable environment 的构建成本；把失败转化为**恢复监督**（VeriGUI/RoTS/Xiaomi-GUI-0/SRC）、**课程**（WebRL）或 **inference-time patch**（LearningFromFailure，OSWorld +6.6 零训练）均获显著增益——"如何复用失败"（步级监督 / 任务生成 / runtime harness）正成为区分方法的关键轴
- **evidence**: [[Workbench/logs/2026-07-06]] (VeriGUI 合成失败恢复轨迹; RoTS 80 万恢复样本; Xiaomi-GUI-0 error-driven flywheel; LearningFromFailure runtime patch; WebRL 失败→curriculum; Reliability-Survey 判定"造失败→学恢复"为跨路线共同范式), [[Workbench/logs/2026-07-08]] (SRC: rollback 造纠正数据，下游 SFT +9.7~12.9pp)
- **confidence**: medium
- **source**: cross-validation
- **impact**: RL-based GUI Agent Training（reward/数据设计的低竞争切入点）、Agent-Facing Environment Runtime（环境应暴露 failure evidence 作为 affordance，使 harness 能把错误转成可执行恢复策略）、[[Topics/GUIAgent-Survey]] Takeaway 15、[[Topics/RealWorldGUIAgent-Reliability-Survey]]
- **status**: provisional

### [2026-07-15] Judge/reward model 可靠性是 agent 评测与 RL 的公共上游瓶颈

- **claim**: LLM judge / reward model 的 precision 普遍落在 70–85% 区间（AgentRewardBench ≤70%、WebJudge ~85%、CUARewardBench 最佳 ORM 82.9%），不足以支撑可信评测排行或干净 RL 信号；judge 误差是"进步幻觉"与 reward noise 的共同上游成因。当前两条改进路径：蒸馏特化小 judge（OpenWebRL 89.8% 超 GPT-4o）与投票+弃权聚合（UPE precision 89.8% 但 recall 56.8%）——精度-召回权衡仍未解决
- **evidence**: [[Workbench/logs/2026-07-06]] (Online-Mind2Web: judge 不可靠是进步幻觉成因，WebJudge ~85%), [[Workbench/logs/2026-07-07]] (AgentRewardBench: 12 judge precision ≤70%), [[Workbench/logs/2026-07-08]] (OpenWebRL 蒸馏 judge; 任务合成家族 judge 噪声 8.6–19%), [[Workbench/logs/2026-07-15]] (CUARewardBench: general VLM 反超 CUA 专用模型，UPE 权衡)
- **confidence**: medium
- **source**: cross-validation
- **impact**: [[Ideas/HybridVerifier-GUIRuntime]] 与 AFE verify affordance（verifier 精度边界必须显式设计）、评测协议（报告分数须附 judge 方法与精度）、与 validated insight "Verifier 角色迁移" 互补——角色在扩张而可靠性欠账未清
- **status**: provisional

### [2026-07-15] 工业技术报告的 headline 数字应默认降权，工程细节比性能叙事更有复利价值

- **claim**: 工业/大厂技术报告系统性存在 claim-evidence 错位（零 ablation、自建非公开 benchmark、贡献未拆解、正文自相矛盾），headline 数字在独立复现前应默认降权；其可信价值集中在数据管线、基建配方、负结果细节（如 ABot-AgentOS self-evolution 资产 8 存 1、ScaleCUA 数据侧 ablation）
- **evidence**: [[Workbench/logs/2026-07-06]] (Xiaomi-GUI-0 无 ablation + 私有 benchmark), [[Workbench/logs/2026-07-13]] (AlayaWorld 零定量; AgenticAISupervisor 无量化; Gemma4 thinking 未拆解; daily 总结"claim 与证据错位是本周通病"), [[Workbench/logs/2026-07-14]] (ABot-AgentOS; LongHorizonTerminalBench 正文自相矛盾), [[Workbench/logs/2026-07-15]] (ABot-N1 零 ablation + 自建 benchmark 无隔离声明; AgentReadyWeb 自建 baseline strawman 风险)
- **confidence**: medium
- **source**: cross-validation
- **impact**: paper-digest 评分校准（rating 应对证据强度敏感而非 headline 敏感）、survey 写作（引用工业报告需标注证据等级）、daily-papers 锐评基线
- **status**: provisional