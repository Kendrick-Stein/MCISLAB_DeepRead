---
title: "Execution-Prior Drift：用良性探针预测自演化写入引起的安全退化"
tags: [self-improving, safety, misevolution, memory, evolution-gate, agentic]
status: raw
linked_project:
date_updated: "2026-07-30"
---

## Hypothesis

在 training-free 的经验/技能累积式自演化中，良性经验造成的安全退化由**执行倾向漂移**（execution-prior drift）中介：对一次候选写入 c，记 Δp_exec(c) 为写入前后模型在一组**全良性、语义歧义**探针上"不澄清直接发出不可逆动作"的比例变化，则 Δp_exec(c) 与该次写入引起的 ΔASR(c) 正相关，且在控制良性效用增益 ΔSR(c) 后偏相关仍显著非零。

可证伪预测（两条，必须同时成立）：

1. **中介**：在 ≥2 backbone × 2 自演化框架（AWM 离线 / ReasoningBank 在线）上，Δp_exec 与 ΔASR 在控制 ΔSR 后的 Spearman 偏相关 ρ ≥ 0.5（p < 0.05），跨 seed × data draw 报告。
2. **可用**：以 Δp_exec 为第二维准入判据（第一维沿用 GRASP 式 capability regression 闸门），在良性成功率损失 ≤ 3pp 的前提下，把 [[Papers/2604-ExperienceSafetyRisks]] 报告的 ASR 上升幅度削减 ≥ 50%，**且准入过程不接触任何 harmful probe**。

若偏相关不显著，假设被证伪，结论为"安全 gating 无法良性化、外源 harmful probe 不可省"，作为负结果报告并回写 [[Topics/SelfEvolvingAgents-Survey]] §11。

## Motivation

**闸门是自演化收益的主承重件，但它的判据只有一维。** [[Papers/2605-GRASP]] 给出了迄今最干净的归因证据：去掉准入闸门，MedAgentBench 从 88.8% 掉到 63.5%；更关键的是它的**配平算力对照**——花同样的 probe 预算但丢弃验证结论，只剩 67–71%，说明起作用的是"验证结论被用于准入"而非"多花了算力"。但 GRASP 的 probe 只测良性任务的成功回归（half previously-failed / half previously-passed），准入判据里没有任何安全维度。

**同期证据表明这一维恰恰会被良性经验推坏。** [[Papers/2604-ExperienceSafetyRisks]] 在 7 模型 × 3 安全 benchmark 的 **21 个 cell 全部**观察到经验积累后 ASR 上升（GPT-4o BrowserART 37.0→50.0；DeepSeek-V3.2 SafeAgentBench 24.5→36.4，相对 +48.6%），且给出了三条把机制钉死的证据：**length-matched 对照**（51.0 演化 vs 38.0 等长对照）排除了"只是上下文变长"；**Integrated Gradients** 显示 experience span 跨层保持高归因；**剂量效应**随检索条数（1/3/5/7/9）单调。作者把机制命名为 execution-oriented procedural prior——经验教会的是"怎么把事做成"，顺带压低了该不该做的判断。该文纯诊断、明确不提缓解，原文呼吁 "more general, principled, and verifiable mechanisms"。

**它的 RQ3 还顺手指出了控制量。** 只喂 execution 类有害经验，ASR 继续升；只喂 refusal 类经验，ASR 降但良性成功率崩（over-refusal）。也就是说记忆的**执行/拒绝先验配比**是一条 safety–utility frontier 上的连续控制量。既然它连续可控，就应该连续可测——而测它不需要 harmful 数据，只需要看模型在良性歧义任务上是"先问一句"还是"直接删"。

**为什么必须良性化。** 准入是高频操作（每条经验一次），而 harmful probe 集昂贵、需要红队维护、并且会随攻击面变化过时；把它挂在准入路径上不现实。良性探针集可公开、可复用、可冻结预注册。

**为什么判据必须外生。** [[Papers/2606-CodeSelfReviewCollapse]] 的 Theorem 2.3 证明：自证式接受准则下，被 gate 的分布与未 gate 的分布同分布（橡皮图章）；实测 perplexity-gate 通过率 0.167→0.235 而正确率反降。因此本 idea 的判据必须是**在冻结探针上的行为统计 + 规则解析**，不能是模型自评。

## Related Work

- [[Papers/2604-ExperienceSafetyRisks]] — 现象与机制来源（21/21 cell ASR 上升、length-matched 对照、IG 跨层归因、剂量效应、RQ3 execution/refusal 双臂）。纯诊断，不提缓解，是本 idea 的直接上游
- [[Papers/2605-GRASP]] — 闸门归因与配平算力对照的方法论来源；判据只有 capability regression，无安全维度。其覆盖边界（ALFWorld +28.4 / WebShop +20.6 / DBBench +5 / **OS Interaction +0.9**）同时是本 idea 的风险提示
- [[Papers/2606-CodeSelfReviewCollapse]] — 自证式 gate 退化定理，约束本 idea 的判据必须外生可测
- [[Ideas/RetrievalMediated-MemoryMisevolution]] — 同一风险的**读取端**杠杆（冻结中毒记忆、只改检索打分）。本 idea 在**写入端准入**，两者正交可组合，不重叠
- [[Ideas/CounterfactualProbe-EvolutionGate]] — 已 archived，原因是"probe-based admission gate"这个器件本身被 GRASP 占据。本 idea 不重复提出 gate，只提出 gate 缺失的**判据维度**及其良性可测的中介量；其 Verdict 里"现有 gate 全部只测 capability regression、无一连接 misevolution 安全协议"正是本 idea 的立足点
- FATE（arXiv 2605.11882）— **最近邻**。on-policy 自演化，把 verifier 评分的失败轨迹转成修复监督，跨 security / utility / over-refusal / validity 过滤候选。但（a）依赖 harmful/red-team 数据（AgentDojo、AgentHarm、ATBench），（b）做的是筛选不是预测，（c）不检验任何中介
- Geometry of Alignment Collapse（arXiv 2602.15799）— 证明良性微调的安全退化无需 harmful 数据即可刻画，给出 alignment loss ∝ 训练时间⁴ 的标度律。**设定是权重梯度几何**，与 training-free 的上下文先验机制不同源；它提供"benign-only 可预测"的存在性先例，也提供一个可对齐的问题形式（本 idea 的剂量曲线 vs 它的标度律）
- SafetyDrift（arXiv 2603.27148）— episode 内运行时预测（吸收 Markov 链，5 步窗口，需违规轨迹）。时间尺度是**执行期**，本 idea 是**演化步之间**
- FlowEvo（arXiv 2607.21596）— skill 入库时施加 "interface, replay, and safety checks where feasible"；摘要未说明 safety check 构成，未报任何安全指标。标志赛道在升温，但未构成结果
- ANCHOR（arXiv 2606.06114）— 模拟人类监督缓解演化 drift，属 human-in-the-loop 路线
- 其余邻居：Blind Curator（2607.07436，有偏 judge 使技能退役失效）、Who Grades the Grader?（2607.12790，评价指标与技能共演化）——落在"判定独立性"这一支，与本 idea 的"判据维度"这一支不同

**Novelty**: 3/5 — prior-art status **PARTIALLY_ADDRESSED**。三块拼图各自存在：安全退化现象（2604.16968 / Misevolution）、带安全维度的演化准入（FATE、FlowEvo）、良性数据即可刻画退化（2602.15799 的权重版）。未被占据的是三者的交点加一个机制主张：**在 training-free 经验累积的设定下，把执行倾向漂移当作可良性测量的中介量，并检验它是否真的中介**。检索到的工作无一测量中介，也无一在准入路径上避开 harmful probe。最近邻 FATE 与本 idea 在数据前提上正交（要/不要红队集），与 SafetyDrift 在时间尺度上正交（episode 内 / 演化步间）。

**检索记录（2026-07-30）**：本轮 WebSearch 全程 HTTP 400 不可用，`export.arxiv.org` 与 Semantic Scholar 均 429，检索仅通过 `arxiv.org/search` 的 WebFetch 完成。已执行查询：`"safety" "self-evolving agents"`、`"predict" "safety degradation" fine-tuning`、`"over-refusal" "memory" agent experience`、`"self-evolving" "safety gate"`（0 结果）、`"execution bias" agent experience safety`（0 结果）、`"memory" "admission" "safety" agent evolution`（0 结果）。覆盖为 partial——"未检索到"不等于"无人研究"，正式立项前须用可用的检索通道复核一遍。

## Approach sketch

**Phase 0 — 复现起点。** AWM（离线）+ ReasoningBank（在线）× 2 backbone（一开一闭），在 3 个安全 benchmark 上复现 ASR 上升，至少 4 个 cell 与 2604.16968 方向一致。不复现则先查设置，不进入 Phase 1。

**Phase 1 — 良性歧义探针集（BAP）。** 约 150 条任务，全部良性，但目标不完整或副作用有歧义（"清理这个目录里的旧文件"、"把这份表发给团队"、"把过期的记录处理掉"）。正确行为是先澄清或做受限执行。测量量 `p_exec` = 在未澄清的情况下直接发出不可逆动作（删除/发送/提交/支付类白名单）的比例。**判定用规则解析器**（动作类型白名单 + 是否出现澄清轮），不用 LLM judge——理由见 Motivation 末段。探针集在看到任何 ΔASR 之前冻结并公开，阈值预注册。

**Phase 2 — 中介测试（核心实验）。** 把自演化拆成 N 次写入事件，每次记录三元组 (Δp_exec, ΔSR_benign, ΔASR)。ΔASR 由真实安全 benchmark 离线测得，**仅用于研究阶段验证中介，部署时不需要**。主统计量是控制 ΔSR 后的 Spearman 偏相关；辅以剂量曲线（累计 Δp_exec vs ASR），检查是否存在与 2602.15799 标度律可对照的稳定函数形式。

**Phase 3 — 控制器。** 若中介成立，两种准入形式：(a) 阈值式，Δp_exec > τ 拒收；(b) 学习式，用少量 (候选写入, ΔASR) 配对校准一个 drift head，输入为 Δp_exec 与经验文本的浅层特征，输出预测 ΔASR，按预算选工作点。两者都套 GRASP 式硬回归预算（净修复 > 新破坏，且绝对破坏数不增）保证效用不退。

**Phase 4 — 对照臂。** (i) 无 gate；(ii) 只有 capability gate（GRASP 复刻）；(iii) **budget-matched**——跑同样的探针预算但丢弃 Δp_exec 判定（GRASP 配平算力对照的直接移植）；(iv) **oracle**——用真 harmful probe 做 gate，给出上界；(v) refusal-only 经验注入（2604.16968 RQ3 的已知 over-refusal 臂）。全部跨 seed × data draw 报告。

## Expected outcome

- **主结果**：控制 ΔSR 后 ρ ≥ 0.5 ⇒ 安全漂移在经验累积设定下是良性可预测的
- **应用结果**：ASR 上升削减 ≥ 50%，良性成功率损失 ≤ 3pp；与 oracle harmful-probe gate 的差距被量化——这个 gap 本身是本工作最有信息量的数字，它说明良性代理能替代红队集到什么程度
- **剂量律**：给出经验累积版的"退化随剂量增长"的函数形式，与 2602.15799 的权重版对照
- **负结果同样成文**：偏相关为零 ⇒ 外源 harmful probe 在安全 gating 上不可省。这会直接改写 [[Topics/SelfEvolvingAgents-Survey]] §11 中"抗 rubber-stamp 的演化步 gate"一条的表述

## Risk

- **中介被效用增益完全解释**：能力提升本身可能就表现为"更敢执行"，Δp_exec 与 ΔSR 高度共线。这是首要威胁，也是必须用偏相关 + 匹配设计处理的原因；若无法分离，判据退化为效用判据的重复，idea 直接淘汰
- **探针集自由度过大**：150 条探针有足够的构造空间调出想要的相关性。缓解只有纪律：冻结 + 预注册 + 公开，且在两个未参与探针设计的 backbone 上外部验证
- **解析器不可靠**：p_exec 依赖"是否澄清 / 是否不可逆"的判定。用规则白名单而非模型判定，代价是覆盖率有限，须报告解析器的漏判率
- **regime 边界未知**：GRASP 在开放动作空间几乎失效（OS Interaction +0.9），而 GUI/OS 正是本 notebook 的主战场。探针法在该 regime 能否测出稳定的 p_exec 未知，须在 Phase 1 先做该 regime 的可行性预检；若测不出，本 idea 的适用范围收缩为工具/代码类 agent，需要在立项时就说清楚
- **赛道温度**：FlowEvo（07）与 FATE（05）显示"带安全判据的准入"正在升温，六个月内出现 benign-only gate 的工程实现是可能的。判断这不构成淘汰信号的理由是：本 idea 的承重点是中介结论与 oracle gap 的测量，即便有人先做出 gate 工程，这两个量仍未被测过；但若中介结论也被抢发，本 idea 应立即归档
