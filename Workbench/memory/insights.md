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
- **impact**: RL-based GUI Agent Training（reward/数据设计的低竞争切入点）、Agent-Facing Environment Runtime（环境应暴露 failure evidence 作为 affordance，使 harness 能把错误转成可执行恢复策略）、[[Topics/CUA-Survey]] Takeaway 15、[[Topics/CUA-Survey]]
- **status**: provisional

### [2026-07-15] Judge/reward model 可靠性是 agent 评测与 RL 的公共上游瓶颈

- **claim**: LLM judge / reward model 的 precision 普遍落在 70–85% 区间（AgentRewardBench ≤70%、WebJudge ~85%、CUARewardBench 最佳 ORM 82.9%），不足以支撑可信评测排行或干净 RL 信号；judge 误差是"进步幻觉"与 reward noise 的共同上游成因。当前两条改进路径：蒸馏特化小 judge（OpenWebRL 89.8% 超 GPT-4o）与投票+弃权聚合（UPE precision 89.8% 但 recall 56.8%）——精度-召回权衡仍未解决
- **evidence**: [[Workbench/logs/2026-07-06]] (Online-Mind2Web: judge 不可靠是进步幻觉成因，WebJudge ~85%), [[Workbench/logs/2026-07-07]] (AgentRewardBench: 12 judge precision ≤70%), [[Workbench/logs/2026-07-08]] (OpenWebRL 蒸馏 judge; 任务合成家族 judge 噪声 8.6–19%), [[Workbench/logs/2026-07-15]] (CUARewardBench: general VLM 反超 CUA 专用模型，UPE 权衡), [[Workbench/logs/2026-07-20]] (VAGEN 交互取证 94.0 P / 92.9 Acc), [[Workbench/logs/2026-07-28]] (SeekJudge 蒸馏 9B 四角色判分), [[Workbench/logs/2026-07-29]] (IRA post-execution 工具核验 86.9%)
- **confidence**: medium
- **source**: cross-validation
- **impact**: [[Ideas/HybridVerifier-GUIRuntime]] 与 AFE verify affordance（verifier 精度边界必须显式设计）、评测协议（报告分数须附 judge 方法与精度）、与 validated insight "Verifier 角色迁移" 互补——角色在扩张而可靠性欠账未清
- **status**: provisional
- **status_history**: [2026-07-30] 保留 claim 与 provisional 状态，但记录边界修订：70–85% 的天花板现已被证明是**被动判分范式**的天花板而非判定任务本身的上界——VAGEN 94.0 P、IRA 86.9%、SeekJudge 9B 均在被动 baseline 之上，且 VAGEN 在弱 actor 的不平衡设定下仍守住 88.5 P（judge 类崩到 ~75%）。原 claim 中"精度-召回权衡仍未解决"这一句已被 VAGEN 的 94.0 P / 95.2 R 局部推翻。机制层结论另立 insight [2026-07-30]「GUI 判定可靠性来自执行后状态取证」

### [2026-07-15] 工业技术报告的 headline 数字应默认降权，工程细节比性能叙事更有复利价值

- **claim**: 工业/大厂技术报告系统性存在 claim-evidence 错位（零 ablation、自建非公开 benchmark、贡献未拆解、正文自相矛盾），headline 数字在独立复现前应默认降权；其可信价值集中在数据管线、基建配方、负结果细节（如 ABot-AgentOS self-evolution 资产 8 存 1、ScaleCUA 数据侧 ablation）
- **evidence**: [[Workbench/logs/2026-07-06]] (Xiaomi-GUI-0 无 ablation + 私有 benchmark), [[Workbench/logs/2026-07-13]] (AlayaWorld 零定量; AgenticAISupervisor 无量化; Gemma4 thinking 未拆解; daily 总结"claim 与证据错位是本周通病"), [[Workbench/logs/2026-07-14]] (ABot-AgentOS; LongHorizonTerminalBench 正文自相矛盾), [[Workbench/logs/2026-07-15]] (ABot-N1 零 ablation + 自建 benchmark 无隔离声明; AgentReadyWeb 自建 baseline strawman 风险)
- **confidence**: medium
- **source**: cross-validation
- **impact**: paper-digest 评分校准（rating 应对证据强度敏感而非 headline 敏感）、survey 写作（引用工业报告需标注证据等级）、daily-papers 锐评基线
- **status**: provisional
- **status_history**: [2026-07-30] 适用范围扩展（claim 不变）：同期 7 篇学术 preprint 被 verifier pass 抓出正文级数字错误或 overclaim（STLiteKV/Prune4Web/OVOD-Agent/MetaTeam/ActiveContextCurator/ElementOrdering/FoldAct），说明 claim-evidence 错位不是工业报告独有属性，独立核验步骤对所有来源都不可省——见 pattern [2026-07-30]「学术 preprint 的正文级数字错误与 overclaim 同样是常态」

---

*Last distilled: 2026-07-30 (period 2026-07-16 ~ 2026-07-30)*

### [2026-07-30] 预算匹配对照是当前 agent 研究信息量最高的实验设计，未做对照的增强增益应默认视为未测量

- **claim**: agent 增强模块（memory/skill 库、观察削减、context 治理、优化器替换）的报告增益中，有相当比例来自未被计入的额外推理预算或不可比的实验口径；一旦补上"总预算固定 / 同目标同初态同 verifier / matched run"这类对照，增益普遍缩水甚至反向。因此**"是否给出预算与口径匹配对照"应作为判断一项 agent 方法是否成立的首要筛选条件**，而不是审稿时的附加要求；反过来，做对照本身已成为本期最高价值的一类贡献
- **evidence**:
  - [[Workbench/logs/2026-07-22]] (AgentsThatMatter：accuracy 可被 retry 这类"科学上无意义"的手段刷高，主张 cost–accuracy Pareto；HAL：21,730 rollout / 9 benchmark / ~$40,000，最贵模型极少落在 Pareto 前沿)
  - [[Workbench/logs/2026-07-23]] (AgentOccam：per-step token 2930.9 > vanilla 2210.2，增益来自动作空间对齐而非省上下文；TeachStop：多数 agentic RL 只报单次 run，无法与 data draw/seed/nondeterminism 分离)
  - [[Workbench/logs/2026-07-27]] (MuonAgenticRL：matched run 下仅换 optimizer 即把 ALFWorld/GiGPO final checkpoint 从 0.320 抬到 0.633——跨论文比数字在优化器不统一时无效)
  - [[Workbench/logs/2026-07-28]] (SkillMemoryBudget：等 token 预算下 Vanilla-IB 在三模型 × 三 WebArena 域全面追平/反超 AWM/ASI/ReasoningBank；GUIvsCLI：440 任务 matched 对照下 screen-only GUI 59.1% 反高于 original-skill CLI 48.2%，推翻"CLI/API 优于 GUI"；ActiveContextCurator：token 计数未含 curator 自身开销，节省数字非端到端)
- **source_ids**: `paper:arxiv:2606.15017`, `paper:arxiv:2410.13825`, `paper:arxiv:2606.24551`, `paper:arxiv:2407.01502`, `paper:arxiv:2510.11977`, `paper:arxiv:2607.16169`, `paper:arxiv:2607.17136`, `paper:arxiv:2604.11462`
- **audit_logs**: [[Workbench/logs/2026-07-22]], [[Workbench/logs/2026-07-23]], [[Workbench/logs/2026-07-27]], [[Workbench/logs/2026-07-28]]
- **confidence**: medium
- **source**: cross-validation
- **impact**: 所有自有实验设计（AFE-MiniSuite、[[Ideas/MismatchTriage-LongHorizonRecovery-GUI]]、[[Ideas/AlignmentVsLength-WebObservation]]）必须内置 budget-matched arm 与 seed × data-draw 交叉，否则结果不可信；paper-digest 评分应把"有无匹配对照"提到与 novelty 同权；survey 引用增强类方法需标注对照口径
- **status**: validated（8 个独立 source、4 个独立日期，其中 SkillMemoryBudget / AgentOccam / GUIvsCLI / ElementOrdering 的支撑 claim row 为 source-verified）
- **contradiction_audit**: 存在增益在对照下**存活**的案例——MHLC 在 −90.7% 成本下仍把成功率 0.47→0.60；GUIvsCLI 中 verifier-guided skill 修补把 CLI 从 48.2% 推到 69.3%。故 claim 限定为"相当比例缩水/反向"与"对照是筛选条件"，**不主张所有增强都是预算假象**。另一边界：本条是对文献计量规律的归纳，非受控复现，不能用于反驳任何单篇具体工作
- **status_history**: [2026-07-30] created as validated（新 pattern 当轮达 ≥3 source-verified + 通过反例审计，走 memory-distill 情况 A 快速通道）；已 enqueue human review，DomainMap 晋升待 Supervisor 批准。[2026-08-02] Supervisor 批准 review_insight `69262838` → L3 → L4，已写入 [[DomainMaps/GUI-Agent]] §关键洞察 Pattern 4（含反例边界与操作含义），queue 任务置 done

### [2026-07-30] 上下文/观察表示的最优点是 backbone 能力 × 任务阶段的函数，"压缩单调有益"已被证伪

- **claim**: web/GUI agent 的观察与上下文削减不存在与模型无关的最优点：同一削减干预在强 backbone 上为负、弱 backbone 上为正（或相反），在检索质量与任务饱和度上呈不对称倒 U，且在单条长程轨迹**内部**也是非平稳的。任何只在单一 backbone × 单一 setting 报告的削减收益都不可外推；正确的报告单位是 regime map 而非单点增益
- **evidence**:
  - [[Workbench/logs/2026-07-20]] (HiViG：五种既有 critic 对强 policy 增益近零或为负，需视觉锚定 + 历史压缩才在 Qwen3-VL-32B 上重新拿到增益)
  - [[Workbench/logs/2026-07-23]] (ReadMoreThinkMore：WorkArena L1 上 gpt-5.1 high 用原始 HTML +17.5、claude-sonnet-4-6 +14.6，而 gpt-oss-20b −18.8、Llama-3.1-70B −14.6；NaiveVisualMemory：整屏视觉记忆降 state-level 失败却放大 action-level 失败；A11yCompressor：token 压到 22% 但精度增益小且脆)
  - [[Workbench/logs/2026-07-28]] (MaskingRegimeMap：9 backbone × 多 retriever 网格，弱 retriever +6.2~6.6、强 retriever × 中等模型峰值 +11.7、饱和时 +0.1 与 live-web −4.8；FoldAct：folding 在 step 173 崩溃，长程内部非平稳)
- **source_ids**: `paper:arxiv:2604.01535`, `paper:arxiv:2606.00408`, `paper:arxiv:2512.22733`, `paper:arxiv:2606.14106`, `paper:arxiv:2606.11078`, `paper:arxiv:2605.00551`, `paper:arxiv:2604.11462`
- **audit_logs**: [[Workbench/logs/2026-07-20]], [[Workbench/logs/2026-07-23]], [[Workbench/logs/2026-07-28]]
- **confidence**: medium
- **source**: cross-validation
- **impact**: [[Ideas/RepresentationRegret-WebObservation]] 与 [[Ideas/AlignmentVsLength-WebObservation]] 的问题定式直接被这条支撑（regret / 对齐-长度分解正是 regime 的可学习形式）；[[Topics/WebAgent-Survey]] 与 [[Topics/CUA-Survey]] 的 observation reduction 节须以 regime 而非排行呈现；自有实验最少需要"强/弱 backbone × 早/晚阶段"两维
- **status**: provisional
- **contradiction_audit**: 无方向一致的反例，但证据集中在 web/search 域（WorkArena、WebArena、search agent），移动端与桌面 OS 域尚无同类网格实验；FoldAct 的非平稳证据来自单一崩溃点，尚未在其他 folding 方法上复现
- **status_history**: [2026-07-30] pattern → provisional insight（7 source、3 日期）

### [2026-07-30] GUI 判定的可靠性来自执行后状态取证，而非更强的被动判分

- **claim**: GUI/CUA 长程失败的主导形态是 agent"自称完成"而非动作做错——即便强制每步自检，False Done/Failed 仍 >86%。而近期唯一有效突破 judge 精度天花板的路线有共同机制：让 verifier 在执行结束后**回到环境里主动取证**（调工具读文件/配置/系统状态、渲染坐标做视觉核对、多角色定位再抽取），而不是被动读截图或读轨迹文本。判定可靠性因此是环境可访问性问题，不是模型规模问题——这直接支持把 verify 做成 agent-facing runtime affordance
- **evidence**:
  - [[Workbench/logs/2026-07-20]] (VLAA-GUI：OSWorld-Verified 上加 Completeness Verifier 后 FDF 仍 >86%，被接受的完成宣告约 1/4 是错的；OS-Marathon：三大失败模式之一为"做完头几条 sub-workflow 就自行终止"；VAGEN：verifier agent 主动调截图/shell/python 探测环境，94.0 P / 92.9 Acc vs 最强 passive baseline 84.7 Acc，弱 actor 不平衡设定下仍 88.5 P 而 judge 类崩到 ~75%；HiViG：在截图上渲染红 X 做坐标视觉核验)
  - [[Workbench/logs/2026-07-28]] (StateAct：独立 finish gate 只看原始指令与机器访问权，看不到 trajectory/plan/rationale，重新定位并读取真实 deliverable；SeekJudge：localization/extraction 四角色蒸馏进单个 9B backbone)
  - [[Workbench/logs/2026-07-29]] (IRA：propose-then-verify + system/application/GUI 三类工具在 post-execution 环境逐条核验，GUI-RewardBench 86.9% 超全部 passive evaluator，增益 +6.2~9.1pp)
- **source_ids**: `paper:arxiv:2604.21375`, `paper:arxiv:2601.20650`, `paper:arxiv:2607.22798`, `paper:arxiv:2602.00575`, `paper:arxiv:2607.25904`, `paper:arxiv:2607.23263`, `paper:arxiv:2606.11078`
- **audit_logs**: [[Workbench/logs/2026-07-20]], [[Workbench/logs/2026-07-28]], [[Workbench/logs/2026-07-29]]
- **confidence**: medium
- **source**: cross-validation
- **impact**: Agent-Facing Environment Runtime 的 verify affordance 从"设计选项"升级为"被证据指定的形态"——要暴露的是**取证通道**（读文件/配置/系统状态）而非 success label；[[Ideas/HybridVerifier-GUIRuntime]] 应据此重写为 post-execution 取证接口而非 judge 集成；[[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] 的 recovery 触发器可直接挂在取证结果上；[[Topics/CUA-Survey]] 判定/验证节
- **status**: provisional
- **contradiction_audit**: 取证式 verifier 的**评测**精度提升是硬的，但**训练闭环收益尚未兑现**——IRA 作为 RL reward 只做到 34.0% vs script reward 34.9%（持平而非超越），VAGEN 未做 RL 训练实验。故不可推论"取证式 verifier 能提升 agent 能力"，只能推论"能提升判定精度"。另：VLAA-GUI 与 HiViG 的笔记未标注 source-checked，VAGEN 为 partial，本条不满足 validated 的核验门槛
- **status_history**: [2026-07-30] pattern → provisional insight（7 source、3 日期）；同时作为既有 insight「Judge/reward model 可靠性是公共上游瓶颈」的边界修订来源

### [2026-07-30] Agent 内部信念缺少 provenance，构成可被环境注入且自身无法纠正的失败面

- **claim**: agent 无法追踪"我为什么相信这条状态"——分不清结论来自像素还是过期结构化文本，也分不清来自可信 workspace 还是环境注入的 claim。后果不是偶发错误而是结构性的：丢弃来源的 stale 记忆会变得"confidently uncorrectable，且严格劣于空记忆"。现有缓解手段都在精度与可用性间硬取舍，说明 provenance 需要作为一等状态字段被环境/runtime 提供，而不是靠 prompt 提醒
- **evidence**:
  - [[Workbench/logs/2026-07-21]] (GUIStateBelief：735 个 probe，含 38 个真实网站的 225 个零编辑 divergence 与 250 个 mobile stale-node candidate，Cohen's kappa 0.86；pixel-priority prompt 在 belief probe 上有效却几乎不降 action 层 hijack，certificate check 阻断 59%–77% 的冲突动作，training-free consistency gate 是唯一同时降 hijack 与 task error 的方案)
  - [[Workbench/logs/2026-07-23]] (EnvTrustBench：evidence-grounding defect 形式化，6 backbone × 5 scaffold = 14 stack、3,850 次 run 聚合 EMR 83.3%；AlwaysOnAgents 转述 RECLAIM：保留 stale 结论但丢弃来源 → confidently uncorrectable，source-first write policy 可修复；NaiveVisualMemory：整屏视觉记忆引入的 state 误判)
- **source_ids**: `paper:arxiv:2607.04334`, `paper:arxiv:2605.08828`, `paper:arxiv:2606.30306`, `paper:arxiv:2606.14106`
- **audit_logs**: [[Workbench/logs/2026-07-21]], [[Workbench/logs/2026-07-23]]
- **confidence**: low
- **source**: cross-validation
- **impact**: Agent-Facing Environment Runtime 的 observe affordance 需要携带 provenance/freshness 元数据（哪个通道、何时采样、是否与像素一致），这是与既有 typed-state 工作的差异化点；[[Ideas/AgentFacing-WebRuntime]]、[[Ideas/StateSufficiency-AmnesiaProbe-GUI]]（amnesia probe 可扩展为 provenance probe）、[[Ideas/RetrievalMediated-MemoryMisevolution]]（source-first write policy 是可比对照）
- **source_boundary**: RECLAIM 的结论来自 AlwaysOnAgents 的转述而非该 survey 自跑实验，本条不把它当作独立一手来源；一手来源为 GUIStateBelief 与 EnvTrustBench 两篇 + NaiveVisualMemory 的间接支持
- **status**: provisional
- **status_history**: [2026-07-30] 新 pattern 当轮直接晋升 provisional（3 个一手 source、2 个日期）

### [2026-07-30] 自演化的收益主要来自验收闸门，而非资产生成——原"缺闸门"判断被证伪

- **claim**: skill/memory 自演化方法的性能增益，其承重件是**接受/拒绝的判断**而非"会写技能"。GRASP 去掉验收闸门从 88.8% 塌到 63.5%（K=4）/40.1%（K=1），且"花同样探针预算但丢弃验证结论"同样塌回 67–71%；SKILL.nb 去 gate 对成功率只掉约 6 分，但回归率从 3.3% 爆到 18.6%——闸门的价值在"防越改越坏"而非抬上限。反面同构：SkillMemoryBudget 显示自带验收环节不足的 online 增强（约半数失败轨迹污染资产）在等预算下被 vanilla 追平。**这推翻了 2026-07-15 的判断"evolution-step verifier gating 是方法空白"**：闸门不是空白，空白在于闸门只覆盖性能回归、不覆盖安全维度，且 self-review 式闸门易 rubber-stamp
- **evidence**:
  - [[Workbench/logs/2026-07-20]] (SEED：换静态 skill library −7.4 为全文最大降幅，on-policy 现场生成 + 演化步筛选才有效)
  - [[Workbench/logs/2026-07-22]] (GRASP：净修好 > 新弄坏 且 绝对弄坏数不增加 的双条件闸门；去闸门 88.8→63.5/40.1；配平算力丢结论 → 67–71)
  - [[Workbench/logs/2026-07-23]] (SKILL.nb：No gates 32.6%/18.6% vs 完整 38.4%/3.3%，三次重跑保住 91.7% 初始成功任务；ASG-SI：audited skill graph 提案，零实证)
  - [[Workbench/logs/2026-07-28]] (SkillMemoryBudget：约 50% 失败轨迹污染资产，等预算下增强方法全面失守)
  - [[Workbench/logs/2026-07-29]] (SelfEvolvingAgents-Survey 20 篇重构：Open Problem 改写为"闸门覆盖面不足 + self-review rubber-stamp"；ExperienceSafetyRisks：benign 经验也会产生安全漂移，性能闸门看不见)
- **source_ids**: `paper:arxiv:2605.29668`, `paper:arxiv:2606.08049`, `paper:arxiv:2606.15017`, `paper:arxiv:2607.14777`, `paper:arxiv:2604.16968`, `paper:arxiv:2512.23760`
- **audit_logs**: [[Workbench/logs/2026-07-20]], [[Workbench/logs/2026-07-22]], [[Workbench/logs/2026-07-23]], [[Workbench/logs/2026-07-28]], [[Workbench/logs/2026-07-29]]
- **confidence**: medium
- **source**: cross-validation
- **impact**: Self-Improving Agent Reliability 方向的 gap 定式必须改写——不再是"给自演化加闸门"，而是"闸门的判据维度（安全/漂移）与独立性（谁来判）"；[[Ideas/CounterfactualProbe-EvolutionGate]] 与 [[Ideas/AdversarialVerification-SelfImproving-GUI]] 的 novelty 论证需据此重估（前者已于 07-21 归档，本条给出归档的机制依据）；[[Ideas/RetrievalMediated-MemoryMisevolution]] 的对照组应含 GRASP 式"配平算力但丢弃验证结论"臂
- **status**: provisional
- **contradiction_audit**: GRASP 笔记为 legacy 状态（只采机制不采数字口径），ASG-SI 无实证，故 source-verified 的一手支撑为 SKILL.nb 与 SkillMemoryBudget 两篇，未达 validated 门槛。另一未解问题：GRASP/SKILL.nb 的闸门都依赖留出测试集或环境可观测谓词，在无 held-out 信号的开放任务上是否仍成立，无证据
- **status_history**: [2026-07-30] pattern「自演化收益受演化步验证缺失所限」→ provisional insight，且**归因方向反转**（gap 从"缺闸门"改为"闸门维度不足"）

### [2026-07-30] GRPO 的增益条件是 base 分布中已稀疏含有被奖励策略，否则需外部监督注入

- **claim**: GRPO 类 on-policy RL 不创造新能力，只重塑分布：增益出现的充要条件是被奖励的策略已能被 base policy 采样到（sampled policy 成功率高于 greedy 即为 headroom 信号）。无 headroom 时中高学习率反而 degrade/collapse；要越过这条边界必须注入外部监督（expert 轨迹、teacher 增量）。三个独立来源从训练收益侧、能力边界侧、数据注入侧给出同一判据
- **evidence**: [[Workbench/logs/2026-07-14]] (MAG：纯 GRPO 不足，注入 expert 轨迹才把 9B SR 从 6.9% 翻到 13.2%), [[Workbench/logs/2026-07-15]] (GRPONullWebAgent：18 组控制网格证明对已 mastered 任务无可信提升), [[Workbench/logs/2026-07-28]] (PassKT：base/SFT/RL 三臂在同 200 条 HotPotQA 上隔离学习信号，"RL 扩展 vs 只重分布"之争的条件被机制化为 base 分布是否稀疏含被奖励策略)
- **source_ids**: `paper:arxiv:2607.12640`, `paper:arxiv:2607.10079`, `paper:arxiv:2604.14877`
- **audit_logs**: [[Workbench/logs/2026-07-14]], [[Workbench/logs/2026-07-15]], [[Workbench/logs/2026-07-28]]
- **confidence**: medium
- **source**: cross-validation
- **impact**: RL-based GUI Agent Training 方向的立项前置检查——任何 GRPO 实验必须先测 sampled-vs-greedy gap，否则可能在无 headroom 区间做无效训练；[[Ideas/ForkPoint-CreditAssignment-GUI]] 的实验设计需含 headroom 分层；与本期 MuonAgenticRL 的量纲警告叠加，说明 agentic RL 的可比性问题同时来自 headroom 与优化器两个维度
- **status**: provisional
- **contradiction_audit**: PassKT 在 QA/检索域、GRPONullWebAgent 在 web agent 域、MAG 在 GUI 域——跨域一致，但三者的 headroom 度量方式不同（sampled-greedy gap / Pass@(k,T) / 专家轨迹需求），尚未有统一可操作指标
- **status_history**: [2026-07-30] pattern → provisional insight（第三个独立 source 达阈值）

### [2026-07-30] On-policy distillation 已成为复用 RL 成果的标准迁移机制

- **claim**: 迁移对象正从"最终模型分布"转向"RL 诱导的 policy shift"：三种独立形态——platform-conditioned multi-teacher（UI-MOPD）、log-ratio implicit dense reward（Direct-OPD）、domain-routed multi-teacher + salient vocabulary alignment（Agents-A1）——都在 student 的 on-policy 状态分布上迁移 teacher 的 RL 增量，而非拟合 teacher 的静态输出。这为"用小模型吃下多个 domain expert 的 RL 成果"提供了可复现路径
- **evidence**: [[Workbench/logs/2026-07-13]] (UI-MOPD：desktop/mobile 两个 32B expert 蒸进共享 8B student，缓解跨平台行为混淆与遗忘), [[Workbench/logs/2026-07-15]] (Direct-OPD：teacher RL 前后 checkpoint 的 log-ratio 当 implicit dense reward，Qwen3-1.7B AIME24 48.3→58.3，4h×8 A100), [[Workbench/logs/2026-07-19]] (Agents-A1：Stage 3 按 domain 硬路由到对应 teacher，在 teacher top-k token 集上重归一化算 reverse KL)
- **source_ids**: `paper:arxiv:2607.04425`, `paper:arxiv:2607.05394`, `paper:arxiv:2606.30616`
- **audit_logs**: [[Workbench/logs/2026-07-13]], [[Workbench/logs/2026-07-15]], [[Workbench/logs/2026-07-19]]
- **confidence**: medium
- **source**: cross-validation
- **impact**: RL-based GUI Agent Training 的算力约束缓解路径（不必自己跑大规模 RL，可迁移已有 expert 增量）；与 insight「GRPO 增益条件化」互补——OPD 正是"注入外部监督"的一种低成本形态
- **status**: provisional
- **contradiction_audit**: 三篇均为方法论文各自报告增益，无第三方复现；Agents-A1 的整体收益混杂 Knowledge-Action Graph 数据基建与 SFT 阶段，OPD 的独立贡献未单独 ablate
- **status_history**: [2026-07-30] pattern → provisional insight（第三个独立 source 达阈值）

### [2026-07-30] Agent-facing 原语的差异化空间已收窄到"暴露什么"，且受控对照显示接口模态不是瓶颈

- **claim**: "把引擎级能力暴露给 agent"已从提案阶段进入可证伪阶段：什么该暴露、暴露后是否真有因果增益，开始有受控答案。关键的反直觉证据是**接口模态本身不是执行瓶颈**——matched 对照下 screen-only GUI（59.1%）反而高于 original-skill CLI（48.2%），真正把 CLI 推到 69.3% 的是 verifier-guided 的 skill 修补。这意味着 AFE 的价值主张不应落在"给 agent 换个更好的接口"，而应落在"暴露可验证/可恢复的执行期状态"
- **evidence**: [[Workbench/logs/2026-07-07]] (WebEnvironment-Engine-Survey：六轴环境能力全部服务 trainer/evaluator), [[Workbench/logs/2026-07-08]] (AgentRuntimePrimitives-Survey gap 核查：Crab 已在 sandbox 域把 rollback 暴露为 agent 工具但只测效率), [[Workbench/logs/2026-07-23]] (ObjectCentricEnv：把环境经验固化为可执行 object model，state/affordance/constraint/transition 编成 Python 类并强制 procedure 复用), [[Workbench/logs/2026-07-27]] (Agent-Friendly-Browser-Interaction-Rules 报告：22 条规则分三个证据层、4 条被推翻), [[Workbench/logs/2026-07-28]] (GUIvsCLI 440 任务 matched 对照；ProtocolValidity：protocol 层的 score-relevant shortcut 会让能力 claim 失效)
- **source_ids**: `paper:arxiv:2607.02846`, `paper:arxiv:2606.24551`, `paper:arxiv:2607.22368`
- **audit_logs**: [[Workbench/logs/2026-07-07]], [[Workbench/logs/2026-07-08]], [[Workbench/logs/2026-07-23]], [[Workbench/logs/2026-07-27]], [[Workbench/logs/2026-07-28]]
- **confidence**: medium
- **source**: cross-validation
- **impact**: Agent-Facing Environment Runtime 的差异化论证需重写——不能再以"GUI 接口低效"为动机，应以"执行期可验证/可恢复状态缺失"为动机（与本期 verify 取证 insight 与 provenance insight 合流）；[[Ideas/AgentFacing-WebRuntime]]、[[Ideas/SelfInitiatedFork-GUI]] 的 baseline 必须含 prompt-only 与 skill-repair 两个对照臂
- **status**: provisional
- **contradiction_audit**: GUIvsCLI 只覆盖 440 个桌面任务 × 18 应用，其 CLI 侧使用的是 original skill（非为该 benchmark 优化），"模态不是瓶颈"这一推论在 skill 质量更高的部署环境下未必成立
- **status_history**: [2026-07-30] pattern「Engine-level 原语的 agent-facing 暴露空白正被快速填补」→ provisional insight，并加入受控对照带来的方向修正