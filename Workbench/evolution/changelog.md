# Evolution Changelog

> Record of Domain Map updates and system evolution.

---

## 2026-04-28

- **System restructured**: Aligned with MindFlow architecture. Removed Python engine/infrastructure code. Flattened vault structure (Papers, Topics, Ideas, DomainMaps, Reports moved to root). Added references/, Projects/, evolution/.

### [2026-04-28] memory-distill

- **period**: 2026-04-21 ~ 2026-04-28
- **logs_processed**: 2
- **new_patterns**: 4
- **promoted_to_insight**: 0 (L1 → L2)
- **validated_insights**: 0 (L2 → L3)
- **queued_for_review**: 0 (L3 → L4 候选)

### [2026-04-28] agenda-evolve

- **trigger**: autoresearch 第 6 轮——survey/ideas/memory 全部完成但 agenda 为空 stub，需结构化
- **insights_reviewed**: 0（无 validated insight）
- **directions_added**: 3（GUI Grounding Robustness, RL-based GUI Agent Training, Self-Improving Agent Reliability）
- **directions_updated**: 0
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: 基于今日 survey（190 篇论文 + 6 条技术路线）、3 个 idea 评估（16/25, 12/25, 11/25）、4 个新 pattern，将 GUI Agent 研究组织为三个层级的方向：Grounding（high priority，基础瓶颈 + 最高评分 idea）、RL Training（medium priority，拥挤但重要的赛道）、Self-Improving Reliability（low priority，monitoring 模式）。添加 2 个 Discussion Topic 供 Supervisor 确认优先级。

## 2026-05-03

### [2026-05-03] memory-distill

- **period**: 2026-04-28 ~ 2026-05-03
- **logs_processed**: 4
- **new_patterns**: 3（latent-space agent communication, production deployment cost bottleneck, workflow automation <70% success rate）
- **promoted_to_insight**: 1 (L1 → L2) — evaluation methodology shift 获第3次独立来源
- **validated_insights**: 0 (L2 → L3)
- **queued_for_review**: 0 (L3 → L4 候选)

## 2026-05-04

### [2026-05-04] agenda-evolve

- **trigger**: autoresearch Round 4——新 validated insight（evaluation shift）+ provisional insight（VLM dichotomy）需反映到 agenda
- **insights_reviewed**: 2（evaluation shift validated, VLM dichotomy provisional）
- **directions_added**: 0
- **directions_updated**: 2（GUI Grounding Robustness + RL-based GUI Agent Training，添加 AutoGUI-v2 evidence）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: AutoGUI-v2 dichotomy 发现（开源 grounding 强，商业 captioning 强）支持两个现有 direction：grounding 作为专门训练能力的价值，fine-tuning on agent data 的增益。更新 evidence + confidence 微调（0.3→0.35, 0.25→0.3）。Dichotomy 是 model selection 指南而非研究 hypothesis，不新增 direction。

## 2026-05-06

### [2026-05-06] agenda-evolve

- **trigger**: autoresearch Round 3——SOLAR-RL + ProxMO 已读完，ForkPoint 从 12/25 降至 10/25，RL direction next_action 完成需更新
- **insights_reviewed**: 2（evaluation shift validated, VLM dichotomy provisional）
- **directions_added**: 0
- **directions_updated**: 2（RL-based GUI Agent Training: 更新 next_action + evidence；GUI Grounding Robustness: 更新 next_action 标注 GoClick 代码阻塞）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: ProxMO 的 PSA (TF-IDF state similarity → soft baseline) 概念上与 ForkPoint 的 state change detection 高度重叠，SOLAR-RL 的 first failure point detection 本质就是 fork point detection。Credit assignment 赛道已有 6+ concurrent works。建议暂停 credit assignment 子方向，转向 rule-based reward design。Grounding direction 因 GoClick 代码未公开被阻塞，需寻找 GUI-Actor 等替代 baseline。

## 2026-05-07

### [2026-05-07] agenda-evolve

- **trigger**: autoresearch Round 2——WindowsWorld (05-06 digest) 提供新 evidence，实验已重设计为 GUI-Actor baseline
- **insights_reviewed**: 2（evaluation shift validated, VLM dichotomy provisional）
- **directions_added**: 0
- **directions_updated**: 1（GUI Grounding Robustness: evidence 新增 WindowsWorld + next_action 更新为"实验已重设计"，confidence 0.35→0.4）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: WindowsWorld 跨应用瓶颈（L1 46% vs L2 14%）和"grounding 能力比 reasoning 更关键"的发现支持 GUI Grounding 方向的重要性。GoClick 阻塞已解决（实验重设计为 GUI-Actor baseline）。Confidence 提升 0.35→0.4。

### [2026-05-19] agenda-evolve

- **trigger**: autoresearch Round 1——近期 digested papers (WorkspaceBench, DUDE, Skill1) 提供新 evidence
- **insights_reviewed**: 2（evaluation shift validated, VLM dichotomy provisional）
- **directions_added**: 0
- **directions_updated**: 2（GUI Grounding Robustness: evidence 新增 WorkspaceBench，confidence 0.4→0.45；RL-based GUI Agent Training: evidence 新增 DUDE + Skill1，next_action 更新，confidence 0.3→0.35）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: WorkspaceBench 的 74 file types + 20K files 场景下 Heterogeneous File Understanding 和 Lineage Tracing 瓶颈进一步验证 grounding 在复杂环境中的重要性。DUDE 的 asymmetric reward (ω=10) 和 Skill1 的 frequency-based credit assignment 为 RL Training 方向的 reward design 提供新思路，虽然 credit assignment 子方向拥挤，但 reward design 角度仍有探索空间。

## 2026-06-25

### [2026-06-25] agenda-evolve

- **trigger**: autoresearch (all topics)——6/23–6/25 积累的 agent-facing environment / personal CUA safety 工作（10+ paper notes、3 survey、2 report、4 idea）未反映到 5/19 起未更新的 agenda Active Directions
- **insights_reviewed**: 0（insights.md 自 5/3 未 distill，最近一条 validated insight 已超 30 天且为 medium confidence——本轮证据主要来自 6/23–6/25 logs/reports/ideas，而非 insights.md；memory-distill 已 overdue）
- **directions_added**: 2（Agent-Facing Environment Runtime: high, conf 0.4；Personal CUA Safety & Contextual Integrity: medium, conf 0.35）
- **directions_updated**: 2（GUI Grounding Robustness: evidence 新增 EvidenceDependence-GUIGrounding + VisualFLIP，next_action 补充无训练 evidence-dependence 诊断备选；RL-based GUI Agent Training: evidence 新增 WebGym + AsyncWebRL + CUA-Gym）
- **directions_paused**: 1（Self-Improving Agent Reliability: next_action 自 5/7 起卡在不可获取的 SGV 论文，verifier 主题已被 HybridVerifier-GUIRuntime 承接）
- **directions_abandoned**: 0
- **reasoning**: 过去三天研究重心明显从"GUI grounding/RL 模型侧"迁移到"环境 runtime 侧 + CUA 安全侧"——AgentFacing-WebRuntime/HybridVerifier (各 18/25)、PersonalizedSafety-CUA (20/25)、AgentCIBench (leakage 67.9%) 等高分证据均无对应 agenda 方向。新增两个方向使 agenda 重新对齐真实研究轨迹；Self-Improving 因前置依赖（SGV 论文）长期无法满足且主题被新方向覆盖而暂停。两个新方向与 GUI Grounding 是否合并、Personal CUA Safety 是否在 Mission scope 内，已作为 Discussion Topic 留给 Supervisor 决策（不擅自改 Mission）。

### [2026-06-25] memory-distill

- **period**: 2026-05-19 ~ 2026-06-25
- **logs_processed**: 10（05-19, 05-22, 05-25, 06-07, 06-08, 06-10, 06-22, 06-23, 06-24, 06-25）
- **new_patterns**: 5（verifier→agent-facing、skill-as-first-class-object、latent/weight-space token reduction、multimodal Clever Hans、personal CUA contextual disclosure）
- **promoted_to_insight**: 3（L1→L2：verifier→agent-facing、skill-as-object 两个新 pattern 因 ≥3 独立来源即时晋升为 provisional insight；外加既有 workflow pattern 晋升）
- **validated_insights**: 1（L2→L3：真实长程工作流远未饱和——5 个独立 benchmark 跨日期一致，既有 pattern 直接升 validated，confidence medium）
- **queued_for_review**: 0（暂无 confidence>0.8 的 validated insight 触发 DomainMaps 晋升）

### [2026-06-26] agenda-evolve

- **trigger**: autoresearch round 2——daily-papers 当日消化 9 篇 GUI/agent/safety 论文，其证据未反映到方向 evidence
- **insights_reviewed**: 0（insights.md 自 6/25 无新 validated 条目；本轮证据来自当日 paper notes 而非 insights）
- **directions_added**: 0
- **directions_updated**: 3（RL-based GUI Agent Training: +MobileForge/GUIAgentExploration；Agent-Facing Environment Runtime: +OpenRath/AgentMemorySystem；Personal CUA Safety: +PrivacyAlign/OverPrivilegedTools，confidence 0.35→0.4）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: 当日 9 篇中 6 篇直接落入 3 个 active direction。最有价值的是 OverPrivilegedTools 的 negative result——safety-alignment 训练几乎不迁移到 least-privilege（Qwen OPUR 50.4%→60.7%），与 PrivacyAlign 缺 runtime baseline 互补，双双支撑 Personal CUA Safety 方向"runtime intervention 优于训练/prompt"的核心 framing，故 confidence 0.35→0.4 并把"三路对照（training/prompt/runtime）"写入 next_action。AgentMemorySystem 的"全文本/DB workload、无 GUI visual memory"反向印证 Agent-Facing Runtime 在 CUA 场景的 memory 空白。未新增方向/insight（无 experiment、无新 validated insight）。

### [2026-06-26] agenda-evolve (supervisor-triggered)

- **trigger**: Supervisor 回复 6/25 Discussion Topic 的 3 个战略问题
- **insights_reviewed**: 0
- **directions_added**: 0
- **directions_updated**: 2（Agent-Facing Environment Runtime → 标记 primary；GUI Grounding Robustness → 标记 secondary high）
- **directions_paused**: 1（Personal CUA Safety & Contextual Integrity：Supervisor 决定不在 Mission scope 内，移入 Paused，证据保留）
- **directions_abandoned**: 0
- **reasoning**: Supervisor 明确 (1) primary=Agent-Facing Environment Runtime（不与 GUI Grounding 合并，但 grounding 可观测角度并入 AFE affordance）；(2) Personal CUA Safety 不在当前 Mission scope 内 → 按协议 Pause（scope 决定而非 hypothesis 证伪，故 Paused 而非 Abandoned，可经 Mission 调整恢复）；(3) 确认 Self-Improving 继续暂停。6/25 Discussion Topic 标记 resolved。Active Directions 现为 3 个（AFE-Runtime primary、GUI Grounding secondary、RL Training）。

### [2026-07-03] memory-distill

- **period**: 2026-06-26 ~ 2026-07-03
- **logs_processed**: 5（2026-06-26, 06-29, 06-30, 07-01, 07-03）
- **new_patterns**: 2（read-only evidence sub-agent 模块原语；runtime state 一等对象化）
- **promoted_to_insight**: 4（L1 → L2：counterfactual 诊断 pattern 第 3 数据点晋升；small specialized GUI grounding 达 3 论文晋升；两条新 pattern 同批达阈值即晋升）
- **validated_insights**: 1（L2 → L3："Verifier/环境 oracle 角色迁移" 获 Dockerless[SWE 域 training supervision] + PolicyGuard[dialogue 域 runtime affordance] 两个新域复现，provisional → validated）
- **queued_for_review**: 0（"真实长程工作流未饱和" 追加 OSWorld2 20.6% 证据但 confidence 维持 medium，未达 L3 → L4 门槛）

### [2026-07-03] agenda-evolve

- **trigger**: memory-distill 产出新 validated insight（"Verifier/环境 oracle 角色迁移" L2→L3）及 4 条新 provisional insight，agenda 未反映
- **insights_reviewed**: 2（"Verifier 角色迁移" validated 今日；"真实长程工作流未饱和" validated 6/25 获 OSWorld2 新证据）
- **directions_added**: 0
- **directions_updated**: 2（Agent-Facing Environment Runtime: +PolicyGuard/Dockerless 证据 + 2 条新 insight，confidence 0.4→0.45；GUI Grounding Robustness: +DecodableNotGrounded 证据，next_action 的 Action Collapse Rate 备选路径升级为三 regime + 五 ablation protocol，confidence 0.45→0.5）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: primary 方向的核心假设由三部分组成（observe/verify affordance + 因果收益），本轮 "Verifier 角色迁移" 升 validated 确立了 verify 组件的跨域可行性（SWE + dialogue 两个新域），"runtime state 一等对象化"（5 篇论文收敛）确立了 observe 组件的接口工程形态——两者都不能替代自有实验对因果收益的验证，故 confidence 仅小幅上调。GUI Grounding 的 evidence-dependence 诊断角度获得独立方法论支撑（DecodableNotGrounded 的 arbiter 协议可直接迁移），使无训练备选路径的可行性显著上升。未新增方向：validated/developing ideas 均已被现有 direction 覆盖。

### [2026-07-15] memory-distill

- **period**: 2026-07-04 ~ 2026-07-15
- **logs_processed**: 7（2026-07-06, 07-07, 07-08, 07-09, 07-13, 07-14, 07-15）
- **new_patterns**: 7（失败轨迹一等资源化；judge/reward model 可靠性系统性不足；工业技术报告 claim-evidence 错位；agent-facing 原语暴露窗口收窄；GRPO 增益条件化；on-policy distillation 迁移 RL 增量；自演化的演化步验证空白）
- **promoted_to_insight**: 3（L1 → L2：失败轨迹资源化 6 论文跨 2 日期；judge 可靠性 4 独立日期；工业报告错位 4 独立日期——均同批达阈值即晋升）
- **validated_insights**: 1（L2 → L3："多模态表观能力需 counterfactual/intervention 诊断" 获 Video-Oasis[视频 benchmark 捷径审计] + VisualAccessBoundary[CoT 视觉访问因果掩蔽] 两个新独立日期，累计 5 日期跨模态一致，provisional → validated，confidence low → medium）
- **queued_for_review**: 0（validated 条目 confidence 均为 medium，未达 L3 → L4 门槛）
- **evidence_appended**: 3（"真实长程未饱和" +AndroidDaily/LHTB/MAG；"Verifier 角色迁移" +DreamGym/InSTA/训练信号生产系统/自演化可验证性分界；"read-only evidence sub-agent" +Vera 部分支持，维持 provisional）

### [2026-07-15] agenda-evolve

- **trigger**: memory-distill 产出 1 条新 validated insight（counterfactual/intervention 诊断）+ 3 条新 provisional insight，且 agenda 自 7/3 起未吸收期间 4 篇新 survey 与竞争情报
- **insights_reviewed**: 3（"多模态表观能力需 counterfactual/intervention 诊断" 今日升 validated；"真实长程未饱和"、"Verifier 角色迁移" validated 获新证据）
- **directions_added**: 0
- **directions_updated**: 3（AFE: +4 篇 survey 证据 + 窗口收窄竞争情报 + judge 精度约束，next_action 聚焦三条剩余空白，confidence 0.45→0.5；GUI Grounding: counterfactual 诊断 insight 升 validated 使无训练诊断路径方法论确立，confidence 0.5→0.55；RL Training: GRPO 条件化 + 失败复用形态两个可操作切入点，confidence 0.35→0.4）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **reasoning**: 三个 active direction 的证据都在累积但均未有自有实验验证，故 confidence 均小幅上调而 status 保持 exploring。AFE 的关键变化是竞争情报——Crab/AgenticExplorationSystems 入场使时间窗口收窄，差异化落点从"全面 affordance 套件"修正为三条剩余空白；judge 可靠性 insight（precision 70–85%）转化为 verify affordance 的显式设计约束。另：Self-Improving Agent Reliability 的 resume_condition 已被 Misevolution 等论文触发，新增 Discussion Topic 请 Supervisor 在 resume / 并入 AFE / 先评 idea 三选项间决策（Researcher 倾向先 idea-evaluate 再并入 AFE）。

### [2026-07-30] memory-distill

- **period**: 2026-07-16 ~ 2026-07-30
- **logs_processed**: 11（2026-07-16, 07-19, 07-20, 07-21, 07-22, 07-23, 07-24, 07-27, 07-28, 07-29, 07-30；共 1495 行）
- **new_patterns**: 5（预算/口径匹配对照系统性推翻既有增益声明；上下文/观察表示最优点是 backbone 能力 × 任务阶段的非单调函数；GUI 长程失败主导形态是"自称完成"且对策收敛到执行后状态取证；agent 内部信念缺 provenance；学术 preprint 正文级数字错误与 overclaim 同样常态）
- **promoted_to_insight**: 7（新 pattern 走情况 A 快速通道 3 条：观察表示条件化 7 source/3 日期、判定取证 7 source/3 日期、信念 provenance 3 一手 source/2 日期；既有 pattern 达阈值 4 条：GRPO headroom 条件化［PassKT 为第三独立表述］、on-policy distillation 迁移［Agents-A1 为第三数据点］、自演化闸门归因、agent-facing 原语暴露）
- **validated_insights**: 1（"预算匹配对照是当前 agent 研究信息量最高的实验设计"：8 独立 source、4 独立日期，SkillMemoryBudget/AgentOccam/GUIvsCLI/ElementOrdering 的支撑 claim row 为 source-verified，反例审计后 claim 限定为"相当比例缩水/反向"而非全称）
- **queued_for_review**: 1（上条 validated insight → 建议 DomainMaps/GUI-Agent.md，queue id 69262838；autoresearch 不得自批 DomainMap 晋升）
- **evidence_appended**: 2（"Judge/reward model 可靠性是公共上游瓶颈" +VAGEN/SeekJudge/IRA，claim 保留但记录边界修订：70–85% 是**被动判分范式**的天花板，且"精度-召回权衡未解"已被 VAGEN 94.0 P/95.2 R 局部推翻；"工业技术报告 headline 降权" +7 篇学术 preprint 正文缺陷，记录为适用范围扩展）
- **judgment_reversals**: 1（2026-07-15 pattern 判断"evolution-step verifier gating 是方法空白"被证伪——GRASP 去闸门 88.8→63.5、SKILL.nb 去 gate 回归 3.3%→18.6% 证明闸门已存在且是收益承重件；空白改判为"闸门只覆盖性能回归、安全维度缺失 + self-review 易 rubber-stamp"）
- **not_promoted**: 1（"学术 preprint 核验命中率"保留为 pattern——可操作结论已被既有工业报告 insight 覆盖，只作范围扩展，避免重复立项）

### [2026-07-30] agenda-evolve

- **trigger**: 同日 memory-distill 产出 1 条 validated + 7 条 provisional insight，agenda `last_updated` 停留在 2026-07-21，其中 4 条直接触及 primary direction 的动机论证与实验设计
- **insights_reviewed**: 8（validated "预算匹配对照是信息量最高的实验设计"；provisional 观察表示条件化 / 判定靠执行后取证 / 信念缺 provenance / 自演化闸门归因反转 / GRPO headroom 条件 / on-policy distillation 迁移 / agent-facing 原语差异化空间收窄）
- **directions_added**: 0
- **directions_updated**: 4（AFE: +4 条新 insight 证据、next_action 加三项设计修正［verify 实现为执行后取证接口不暴露 success label / observe 返回值带 provenance 字段 / 对照臂增 budget-matched arm 与 skill-repair arm］，confidence 0.5 维持；Self-Improving: hypothesis 中"evolution-step verifier gating 是方法空白"改判为闸门的判据维度与判定独立性，next_action 靶心迁移 + 建议 RetrievalMediated 补 GRASP 式配平算力对照臂，confidence 0.45 维持；RL Training: headroom 前置诊断获第三独立来源，新增强制口径［跨 seed × data draw 报告 + 声明 optimizer］，confidence 0.4 维持；GUI Grounding: +2 条新 insight，FPN 原型对照须 budget-matched、跨分辨率评估须分 regime 报告，confidence 0.55 维持）
- **directions_paused**: 0
- **directions_abandoned**: 0
- **discussion_topics_added**: 1（"AFE 的动机前提被证伪，差异化是否重锚" — 请 Supervisor 决策 hypothesis 是否从"接口低效"改锚到"执行期可验证/可恢复状态缺失"，及 MiniSuite 是否保留双模态臂、主 claim 是否退到 false-completion/recovery 指标）
- **reasoning**: 本轮四个方向全部只更新证据与实验口径、confidence 一律维持，是有意为之——新增 insight 大多是**方法论约束**（对照怎么做、指标怎么报）而非对方向核心假设的支持或反驳，这类证据提高的是未来实验的可信度门槛，不构成假设本身的置信度变化。唯一实质性判断变更有两处：(1) AFE 的动机前提被 GUIvsCLI 的 matched 对照证伪，但同期 verify/observe affordance 的具体形态首次被外部证据指定，两者方向相反，故 confidence 双向抵消维持 0.5，并把是否重写 hypothesis 上交 Supervisor 而非自行改写；(2) Self-Improving 的"gate 是方法空白"被 GRASP/SKILL.nb 的 ablation 反转，可攻面变窄（下调因素）但开放问题更锐利（上调因素），同样维持。未新增方向：validated insight 属方法论性质、不构成独立研究方向，两个相邻的 web-observation idea（AlignmentVsLength / RepresentationRegret）仍为 raw，未达开新方向的证据密度。
