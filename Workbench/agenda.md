---
last_updated: "2026-07-30"
updated_by: agenda-evolve
active_topic: GUI Agent
---

## Mission

构建能够可靠理解、定位和操作图形用户界面的视觉 Agent 系统，重点关注 grounding robustness、高效训练范式（RL vs SFT）、以及 self-improving 系统的可靠性保障。长期目标是让 GUI Agent 在跨平台、跨分辨率、动态变化的真实界面中稳定执行长程任务。

---

## Active Directions

### GUI Grounding Robustness

- **priority**: high (secondary — 2026-06-26 起 primary 为 Agent-Facing Environment Runtime；本方向的 grounding 可观测/evidence-dependence 角度可并入 AFE 的 observe/verify affordance)
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 架构级 multi-scale 设计（FPN + multi-resolution training + consistency loss）可以在不增加推理开销的前提下，显著提升 GUI grounding 在跨分辨率/跨设备场景下的鲁棒性
- **evidence**: [[Topics/CUA-Survey]], [[Papers/2604-GoClick]], [[Ideas/ScaleInvariant-Grounding-GUI]], [[2500-GuiActorCoordinateFree]], [[Papers/2604-AutoGUIv2]] (dichotomy: fine-tuned grounding 强于通用 VLM), [[Papers/2604-WindowsWorld]] (跨应用是独立瓶颈 L1 46% vs L2 14%，grounding 能力比 reasoning 更关键), [[Papers/2605-WorkspaceBench]] (Heterogeneous File Understanding 和 Lineage Tracing 是 workspace agent 瓶颈，最佳 agent 68.7% vs 人类 80.7%，说明 grounding 在复杂环境中仍有显著提升空间), [[Ideas/EvidenceDependence-GUIGrounding]] (18/25, Action Collapse Rate 量化 grounding 是否真正依赖视觉证据), [[Papers/2606-VisualFLIP]] (VLM grounding 评估从单点 accuracy 转向 counterfactual evidence dependence), [[Papers/2606-DecodableNotGrounded]] (灰图 vision-ablation arbiter 推翻 probe+steering 验证的 latent-knowledge 结论，grounded/prior/inverted 三 regime——counterfactual 诊断 pattern 第 3 独立数据点，7/3 已升 provisional insight), [[Papers/2603-VideoOasis]] (捷径 ablation + 5 模型共识审计 14 个视频 benchmark：55% 样本可被无视觉/无时序捷径攻破——第 4 独立数据点), [[Papers/2607-VisualAccessBoundary]] (Visual Access Sweep 层×时间因果掩蔽：CoT 增益受 perceptual readout 制约而非延长图像访问——第 5 独立数据点，7/15 该 insight 已升 **validated**), **2 条 7/30 新 insight**（**validated** 预算匹配对照——8 源 4 日期，直接约束 FPN 原型的对照设计；provisional 观察表示最优点随 backbone 能力 × 任务阶段非单调——[[Papers/2409-ElementOrdering]] / [[Papers/2604-ReadMoreThinkMore]] / [[Papers/2605-A11yCompressor]] 等 7 源，要求跨分辨率评估分 regime 报告）
- **next_action**: 实验已重设计为 GUI-Actor baseline（Experiments/2026-04-29-ScaleInvariantGroundingGUI 已更新），下一步：原型验证 FPN + multi-resolution training 在 ScreenSpot-Pro 上的效果（备选低成本切入：用 EvidenceDependence-GUIGrounding 的 Action Collapse Rate 做无训练 grounding evidence-dependence 诊断——方法论基础已随 counterfactual 诊断 insight 升 validated 而确立，可借 DecodableNotGrounded 三 regime 分类 + VisualAccessBoundary 的层×时间掩蔽维度升级设计，跨分辨率评估用 arbiter 对照把失败分解为 evidence loss vs prior reliance）。**7/30 两项口径约束**：(1) FPN 原型的对照组必须 **budget-matched**——multi-scale 分支引入的额外 FLOPs/token 需折算给 single-scale baseline，否则增益与"多花算力"不可分离（validated insight，8 源 4 日期）；(2) 跨分辨率评估须按 regime 分层报告而非报单一均值——观察表示的最优点是 backbone 能力 × 任务阶段的非单调函数（[[Papers/2409-ElementOrdering]] 强模型对 DOM 顺序不敏感、弱模型敏感；[[Papers/2604-ReadMoreThinkMore]] 信息量随阶段反转），把"哪个 regime 下 multi-scale 有效"当作结论而非噪声
- **confidence**: 0.55 (维持——本轮无新证据触及架构级 multi-scale 假设本身，两条新 insight 只收紧了实验口径；validated 的 budget-matched 对照约束提高了原型出结果的可信度门槛，但也提示既有 grounding 增强类文献的报告增益需重新折算)

### RL-based GUI Agent Training

- **priority**: medium
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: Rule-based RL（GRPO 风格）配合结构化 action reward，可以以 10x 更少的训练数据达到或超越 SFT 的 GUI action prediction 性能，且 OOD 泛化更强
- **evidence**: [[Topics/CUA-Survey]], [[2500-UiR1EnhancingEfficient]], [[Papers/2604-ClawGUI]], [[2500-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]], [[Ideas/ForkPoint-CreditAssignment-GUI]], [[Papers/2604-AutoGUIv2]] (fine-tuning on agent data 对 grounding 有显著增益), [[Papers/2604-SOLAR-RL]] (first failure point detection, 3-stage reward shaping), [[Papers/2602-ProxMO]] (PSC+PSA, 90.6% ALFWorld, state similarity credit assignment), [[Papers/2605-DUDE]] (asymmetric reward ω=10 for deception, hybrid-reward learning 减少 53.8% 欺骗易感性), [[Papers/2605-Skill1]] (unified skill selection/utilization/distillation via single policy, reward signal frequency decomposition for credit assignment), [[Papers/2601-WebGym]] + [[Papers/2606-AsyncWebRL]] (大规模 visual web agent RL：rubric evaluator + async rollout，OOD 泛化来自任务分布 scaling 而非新算法), [[Papers/2606-CUAGym]] (task/state/reward.py 共生成 32K+ verified RLVR tuples，环境侧合成 RL 监督), [[Papers/2606-MobileForge]] (hint-contextualized GRPO：corrective hint 作为 state 条件而非 reward 项，免标注 mobile 自适应，ForgeOwl-8B AndroidWorld 77.6% Pass@3——是 rule/feedback-based reward design 的具体实例), [[Papers/2606-GUIAgentExploration]] (HER 式 hindsight relabeling + TDHAF：low-level 训练无法向上泛化 80.5%→9.1%，组合泛化层级敏感), [[Papers/2607-GRPONullWebAgent]] (受控阴性结果：GRPO 仅在 sampled-policy headroom 存在时有效，18 组对照 + 双 regime 机制定位), [[Papers/2607-MAG]] (expert 轨迹注入 GRPO 使 9B SR 6.9%→13.2%——外部监督注入是无 headroom 时的补救), [[Papers/2607-UIMOPD]] + [[Papers/2607-DirectOPD]] (on-policy distillation 迁移 RL 增量：跨平台 multi-teacher / weak-to-strong log-ratio implicit reward), 7/15 新 provisional insight（失败轨迹一等资源化：恢复监督/课程/runtime patch 三种复用形态是方法区分轴）
- **next_action**: credit assignment 暂停待 Supervisor 决策（5/6 Discussion 未回复）；rule-based reward design 子方向新增两个具体切入点：(1) 失败轨迹复用形态的 reward 化——VeriGUI/RoTS/SRC/WebRL 证据链已备（7/15 insight），GUI 域"哪种失败复用形态最有效"无系统对比；(2) GRPO headroom 前置诊断——用 GRPONullWebAgent 的 sampled-vs-greedy 判据做训练资源分配 gating，可作低成本复现起点（7/30 该判据获第三个独立表述 [[Papers/2604-PassKT]]，已升 insight，可直接作为实验前置检查）。**7/30 新增强制口径**：本方向任何 RL 实验必须跨 seed × data draw 报告（[[Papers/2607-TeachStop]]：单次 run 无法与 nondeterminism 分离）并声明 optimizer（[[Papers/2607-MuonAgenticRL]]：仅换 optimizer 即把同一 ALFWorld/GiGPO 配置从 0.320 抬到 0.633），否则结果不具可比性
- **confidence**: 0.4 (维持——两个切入点的可操作性上升（headroom 判据第三独立来源、on-policy distillation 三形态成型），但方向 hypothesis 本身"10x 数据效率 + 更强 OOD"在受控证据下更可疑：GRPO 增益条件化说明数据效率优势只在有 headroom 时成立，seed/optimizer 噪声说明既有 10x 类声明多数未经充分对照)

### Agent-Facing Environment Runtime

- **priority**: high (**primary** — Supervisor 2026-06-26 确认为 primary direction，GUI Grounding Robustness 降为 secondary high)
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 把环境后台已有的 state / reset / verifier / fork 能力以 task-agnostic、non-oracle 的 agent-facing affordance 暴露给 GUI/web/CUA agent，可在 zero/low-training 条件下显著提升 long-horizon task success、wrong-turn recovery，并降低 reward hacking 与 false completion——且该收益不能被 prompt-only baseline 复现
- **evidence**: [[Topics/CUA-Survey]]（2026-07-20 起合并原 AgentFriendlyEnvironment / GUI-Environment / WebEnvironment-Engine 三 survey）, [[Topics/CUA-Survey]], [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]], [[Reports/2026-06-24-GUIEnvironment-RecentWorks]], [[Ideas/AgentFacing-WebRuntime]] (18/25), [[Ideas/HybridVerifier-GUIRuntime]] (18/25), [[Papers/2600-WebHarbor]] (真实网站 Docker mirror + 快速 reset), [[Papers/2606-CUAGym]] (32K+ verified RLVR tuples), [[Papers/2605-SaaSBench]] (resolved 3.8%，长程组合可靠性极低), [[Papers/2606-WeaveBench]] (hybrid GUI+CLI+Code，35.2% failure 来自 reward hacking), [[Papers/2605-OpenComputer]] (programmatic verifier 94.1% human alignment > LLM judge), [[Papers/2606-ENVS]] (环境 oracle 可作为 SFT 监督来源), [[Papers/2606-OpenRath]] (Session-as-first-class-value：把碎片化 runtime state 统一为可随程序值流动的 observable state——正是 agent-facing observable affordance 的一种工程实现，但仅 technical report 无 benchmark), [[Papers/2606-AgentMemorySystem]] (12 个 agent memory 系统系统评测；但 workload 全是文本/DB，**完全无 GUI/CUA visual memory 场景**——反向印证 agent-facing memory 在 computer-use 场景仍是空白), [[Papers/2606-PolicyGuard]] (pre-execution sub-agent verifier + 定向 remediation 在 dialogue/tool-call 域实证 runtime verifier affordance：τ²-bench airline Pass⁴ +6~12pp、block rate 减半), [[Papers/2606-Dockerless]] (evidence-grounded verifier 作为 SFT filter + RL reward，接近 test-execution RL), 2 条 7/3 memory insight（"Verifier 角色迁移" 升 **validated**；"runtime state 一等对象化" provisional：OpenRath/MemGUI/ArborHTR/LUMOS/AgenticSTS 五论文收敛——observe affordance 的接口形式有工程收敛证据）, [[Topics/CUA-Survey]] §1–2 (需求侧六轴推导：环境能力全部服务 trainer/evaluator、无人暴露给 agent), [[Topics/CUA-Survey]] (gap 核查推翻先验：Crab 已在 sandbox 域把 rollback 暴露为 agent 工具但只测效率不测 success；AgenticExplorationSystems 表明系统社区已入场——**窗口收窄**), [[Topics/CUA-Survey]] (真实长程瓶颈在 verify/recover 而非 grounding，VeriGUI 72.3% 失败为空转 timeout), [[Reports/2026-07-08-WebAgentTrainingInfra-Pulse]] (差异化应落在 agent-visible affordance contract 而非更大任务集), 2 条 7/15 新 provisional insight（judge/RM precision 普遍 70–85% → verify affordance 的精度边界设计约束；失败轨迹一等资源化 → failure evidence 应作为 affordance 暴露）, **4 条 7/30 新 insight**（[[Papers/2606-GUIvsCLI]] 440 任务 matched 对照：screen-only GUI 59.1% > original-skill CLI 48.2%，**"GUI 接口低效"这一动机前提被证伪**，真正把 CLI 推到 69.3% 的是 verifier-guided skill 修补 → 差异化须重锚到"执行期可验证/可恢复状态缺失"；[[Papers/2602-VAGEN]] 94.0 P + [[Papers/2607-InteractiveRewardAgent]] 86.9% + [[Papers/2607-SeekJudge]] → verify affordance 的形态被证据指定为**取证通道**（读文件/配置/系统状态）而非 success label，且 [[Papers/2604-VLAA-GUI]] FDF>86% 确认 false completion 是主导失败形态；[[Papers/2607-GUIStateBelief]] + [[Papers/2605-EnvTrustBench]] EMR 83.3% → observe affordance 须携带 provenance/freshness 元数据，这是与既有 typed-state 工作的差异化点；**validated** 预算匹配对照 insight → AFE-MiniSuite 的对照设计约束）
- **next_action**: 在 WebHarbor mirror 或 CUA-Gym-Hub mock apps 上原型化 AFE-MiniSuite（observe/map/rollback/verify affordance + C0–C7 因果对照），先验证 Web-only causal mechanism。**7/30 三项设计修正**：(1) verify affordance 实现为 post-execution 取证接口（可查询文件/配置/系统状态的只读通道），不暴露 success label；(2) observe affordance 的返回值须带 provenance 字段（来自哪个通道、何时采样、是否与像素一致）；(3) 对照臂在 prompt-only 之外必须再加 **budget-matched arm**（affordance 调用消耗的 token/步数需折算给 baseline）与 **skill-repair arm**（GUIvsCLI 显示 verifier-guided skill 修补是同一收益的竞争解释），否则增益不可归因。竞争窗口继续收窄（Crab / AgenticExplorationSystems 已入场）；待解风险：IRA 的取证式 verifier 作为 RL reward 只做到 34.0% vs script 34.9%（持平），说明"取证能提精度"不自动等于"能提 agent 能力"，AFE 的因果收益 claim 需要独立验证
- **confidence**: 0.5 (维持——本轮证据双向：verify/observe affordance 的**具体形态**首次被外部证据指定（取证通道 + provenance 字段），但"GUI 接口低效"这一动机前提被 GUIvsCLI 的 matched 对照证伪，且 IRA 显示判定精度提升未必转化为能力提升；两者抵消，自有实验对因果收益的验证仍是唯一能推动 confidence 的证据)

### Self-Improving Agent Reliability

- **priority**: medium（**literature-only** — Supervisor 2026-07-21 决定 resume，scope 限定为 paper 收集 → digest → survey → idea 孵化，**不做实验**；实验侧衔接由 AFE 的 verify affordance（[[Ideas/HybridVerifier-GUIRuntime]]）承接）
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 自增强循环存在系统性验证偏差——该假设已被外部完整实证（[[Papers/2509-Misevolution]] 四路径实测：memory reward hacking >60%、workflow ASR 54→83）。**2026-07-30 开放问题改判**：原判断"evolution-step verifier gating 是方法空白"已被证伪——闸门不仅存在，还是收益的主承重件（[[Papers/2605-GRASP]] 去闸门 88.8%→63.5%，且"配平探针算力但丢弃验证结论"同样塌回 67–71%；[[Papers/2606-SkillNb]] 去 gate 回归率 3.3%→18.6%）。开放问题因此收窄为闸门的**判据维度**（现有闸门只测性能回归，安全/漂移维度空白，见 [[Papers/2604-ExperienceSafetyRisks]]）与**判定独立性**（self-review 式闸门易 rubber-stamp）
- **evidence**: [[Topics/SelfEvolvingAgents-Survey]], [[Papers/2509-Misevolution]], [[Papers/2607-ABotAgentOS]]（工业侧 8 存 1 印证）, [[Topics/CUA-Survey]], [[2500-UiGenieSelfImproving]], [[Ideas/AdversarialVerification-SelfImproving-GUI]], [[Ideas/CounterfactualProbe-EvolutionGate]] (archived 13/25，gate 赛道 3 个月 ≥6 并发被占), [[Ideas/RetrievalMediated-MemoryMisevolution]] (**validated 19/25，lead idea**，机制获 2606.23075 独立命名), 2026-07-21 survey-refresh 新证据链：「监督资产是 policy 相对的」跨域收敛（[[Papers/2607-SEED]] 静态 skill 库 −7.4 / [[Papers/2607-KnowActGUIClaw]] 跨 backbone +3.1 但跨演化阶段过期 / [[Papers/2607-EvoCUA15]] RL 数据子集 policy 相对）+ skill 路线内化 vs 外挂分岔（[[Topics/CUA-Survey]] / [[Topics/SelfEvolvingAgents-Survey]]）
- **next_action**: ✅ 2026-07-29 完成——上述 8 篇（gate 家族 GRASP/SKILL.nb/ASG-SI/SEACertificates/SEVerA + memory 安全 Safety-in-SelfEvolving/MemRL/MemoryGraft）+ 另 12 篇（RSI 谱系、负结果三线、env/multi-agent co-evolution、operation-level memory、lifelong benchmark）共 20 篇一手核验后，[[Topics/SelfEvolvingAgents-Survey]] 全面重构至 12 节 CUA 标准（119→401 行，含 §6.2 五粒度 gate 家族小节、§3.6 横切表、§9 benchmark 全景表、21 行 Key Evidence Matrix；Open Problem 已更新为"gate 仅覆盖性能回归、安全维度空白 + self-review gate rubber-stamp"）。**待 Supervisor 复核 2 项**（非 autoresearch 可自批）：(1) L51 evidence 中"RetrievalMediated 机制获 2606.23075 独立命名"经本轮 gap-pass 核出有误——2606.23075 仅在 §4.2/4.3 描述、未命名 retrieval-mediated 机制，概念首发权未被占据，需据此复核 RetrievalMediated 的 novelty/lead-idea 定位；(2) [[Papers/2512-MemoryGraft]] 证据实为 retrieval-level 非其主张的 cross-agent transfer（rating 2）。复核后下一步转 survey-refresh 增量维护 + 依 gate 缺口孵化 idea（衔接 [[Ideas/HybridVerifier-GUIRuntime]]）。**2026-07-30 更新**：gate 归因反转后，idea 孵化的靶心从"给自演化加闸门"移到两处——(a) 闸门判据的安全/漂移维度（性能回归闸门对 benign 经验引起的安全漂移完全不可见），(b) 判定独立性（GRASP/SKILL.nb 的闸门都依赖 held-out 测试集或环境可观测谓词，开放任务上无此信号时闸门如何成立是无证据区）；另建议 [[Ideas/RetrievalMediated-MemoryMisevolution]] 的实验设计补一个 GRASP 式"配平算力但丢弃验证结论"对照臂，用以分离"检索干预"与"多花算力"两种解释
- **confidence**: 0.45（维持——核心假设仍被外部实证支撑，且开放问题因 gate 归因反转而更锐利、更有据；但下调项同样明确：原方法空白消失意味着可攻面变窄，且 lead idea 的 novelty 定位待 Supervisor 复核 2606.23075 引用错误后才能确定）

---

## Paused Directions

### Personal CUA Safety & Contextual Integrity

- **priority**: low
- **status**: paused
- **origin**: researcher-discovered
- **hypothesis**: personal computer-use agent 的隐私泄露主要来自 normal-use 的 contextual disclosure 而非 adversarial attack；以 task-scoped permission + trajectory-level privacy guard 作为 runtime intervention，可显著降低 inappropriate disclosure，且优于 prompt-level instruction
- **evidence**: [[Ideas/PersonalizedSafety-CUA]] (20/25), [[Papers/2606-AgentCIBench]] (leakage 67.9%), [[Papers/2606-MyPCBench]], [[Papers/2606-BraveGuard]], [[Papers/2606-PrivacyAlign]], [[Papers/2606-OverPrivilegedTools]] (safety-alignment 不迁移到 least-privilege 的 negative result)
- **pause_reason**: Supervisor 2026-06-26 决定 Personal CUA Safety 不在当前 Mission scope 内（Mission 聚焦 grounding/operating GUI 可靠性 + Agent-Facing Environment Runtime）。已积累的证据（AgentCIBench 67.9% leakage、OverPrivilegedTools alignment-不迁移、PrivacyAlign 训练侧对齐）保留备查，不再主动推进
- **resume_condition**: Supervisor 调整 Mission 将 personal/CUA safety 重新纳入 scope；或其 contextual-integrity / least-privilege 主题被 Agent-Facing Environment Runtime 的 verifier/affordance 实验证明为必要子问题
- **confidence**: 0.4

---

## Abandoned Directions

（暂无）

---

## Discussion Topics

### GUI Agent 研究方向优先级确认 — 2026-04-28

- **raised_by**: agenda-evolve
- **context**: 今日完成 GUI Agent 全面 survey（190 篇论文）、memory-distill（4 个新 pattern）、3 个 idea 生成与评估。Grounding Robustness (16/25) 评分最高，Credit Assignment 方向被 WebSearch 发现极拥挤（5+ concurrent works），Adversarial Verification 风险最高 (11/25)
- **question**: 当前以 GUI Grounding Robustness 为 primary direction、RL Training 为 secondary、Self-Improving 为 monitoring 的优先级分配是否合理？是否需要调整？
- **related_direction**: GUI Grounding Robustness, RL-based GUI Agent Training, Self-Improving Agent Reliability

### Credit Assignment 方向是否继续 — 2026-05-06 更新

- **raised_by**: agenda-evolve
- **context**: SOLAR-RL 和 ProxMO 已读完。ForkPoint 评估从 12/25 降至 10/25——ProxMO 的 PSA (TF-IDF state similarity → soft baseline) 概念上与 ForkPoint 的 state change detection 高度重叠，SOLAR-RL 的 first failure point detection 本质就是 fork point detection。Credit assignment 赛道已有 6+ concurrent works (SOLAR-RL, GiGPO, ProxMO, ADMIRE, DAPO, GUI-Shepherd)
- **question**: 建议暂停 credit assignment 子方向，转向 rule-based reward design（更底层、更少竞争的 RL 子方向）。是否同意？或者是否有 credit assignment 的独特角度（如 GUI-specific visual state similarity）值得继续探索？
- **related_direction**: RL-based GUI Agent Training

### SGV 论文来源 — 2026-05-07

- **raised_by**: autoresearch
- **context**: Self-Improving direction next_action 指向"阅读 SGV (Self-Grounded Verification) 论文"。Vault 中 DomainMap 提到 SGV "20pp OSWorld 提升"，但无具体 paper URL 或 arxiv ID。Web search 未返回匹配结果。UI-Genie 论文已消化，未提及 SGV 论文。
- **question**: 请提供 SGV (Self-Grounded Verification) 论文的 arxiv URL 或完整标题。如果该论文未公开发表或名称不同，请告知正确来源。
- **related_direction**: Self-Improving Agent Reliability

### Autoresearch 推进受阻 — 2026-05-19

- **raised_by**: autoresearch
- **context**: Round 2 检测到所有 active directions 均被阻塞：(1) GUI Grounding Robustness 的 next_action 是"原型验证 FPN + multi-resolution training"（需实验实现，超出 autoresearch scope）；(2) RL-based GUI Agent Training 的 next_action 需要"Supervisor 决策是否完全放弃 credit assignment"；(3) Self-Improving Agent Reliability 需要 SGV 论文 URL。同时，Queue 中有 32 个 pending papers（多为 daily-papers 产生的 summarize_paper 任务），但 WebFetch 被网络限制阻塞，无法执行 paper-digest。
- **question**: 请提供以下任一指导以解除阻塞：(1) 提供可访问的论文 PDF 或替代获取方式（绕过 WebFetch 限制）；(2) 决策 RL Training 方向是否放弃 credit assignment 转向 rule-based reward design；(3) 提供 SGV 论文来源；(4) 指示 GUI Grounding 实验实现的优先级（是否应作为 autoresearch 的行动项）。
- **related_direction**: 所有 active directions

### 新方向纳入与 Self-Improving 暂停确认 — 2026-06-25

- **raised_by**: agenda-evolve
- **context**: 6/23–6/25 围绕 agent-facing environment 与 personal CUA safety 积累了 10+ 篇 paper notes、3 篇 survey（AgentFriendlyEnvironment / ComputerUseAgents / GUI-Environment）、2 篇 report 与 4 个 idea（AgentFacing-WebRuntime 18/25、HybridVerifier-GUIRuntime 18/25、EvidenceDependence-GUIGrounding 18/25、PersonalizedSafety-CUA 20/25），但 5/19 之后 agenda 的 Active Directions 未反映这些进展。本轮 agenda-evolve 新增 "Agent-Facing Environment Runtime"（high）与 "Personal CUA Safety & Contextual Integrity"（medium），并暂停 "Self-Improving Agent Reliability"。另：5/19 "Autoresearch 推进受阻" 中的 WebFetch 阻塞已通过 scripts/lexmount_fetch.py + references/network-fetch-fallback.md 解决，paper-digest 6/24–6/25 已正常运行——该 Discussion Topic 可视为已解除。
- **question**: (1) primary direction 是否从 GUI Grounding Robustness 调整为 / 并列 Agent-Facing Environment Runtime？两者是否应合并（均以"环境/grounding 的可观测、可验证能力"为核心）还是保持独立？(2) Personal CUA Safety 是否在当前 Mission scope 内（Mission 聚焦 grounding/operating GUI 可靠性），还是应降级为 monitoring？(3) 是否确认暂停 Self-Improving Agent Reliability，并将其 verifier 主题并入 Agent-Facing Environment Runtime？
- **related_direction**: Agent-Facing Environment Runtime, Personal CUA Safety & Contextual Integrity, GUI Grounding Robustness, Self-Improving Agent Reliability
- **resolved**: 2026-06-26 Supervisor 回复 — (1) **primary = Agent-Facing Environment Runtime**（GUI Grounding 降为 secondary high，两者独立不合并，但 grounding 可观测角度并入 AFE affordance）；(2) **Personal CUA Safety 不再在 Mission scope 内** → 移入 Paused；(3) **确认暂停 Self-Improving Agent Reliability**

### Self-Improving Agent Reliability 的 resume_condition 已触发 — 2026-07-15

- **raised_by**: agenda-evolve
- **context**: 该方向 6/26 确认暂停，resume_condition 之一为"出现新的 self-improving verification 论文"。7/9 [[Topics/SelfEvolvingAgents-Survey]] 确认该条件已满足：[[Papers/2509-Misevolution]]（ICLR 2026，rating 5）四路径 misevolution 实证 + Safety Risks in Experience-Driven Self-Evolving Agents (2604.16968) 正是等待中的实证论文，且完整验证了原 hypothesis（自增强循环存在系统性验证偏差、需外部纠错机制）。survey 同时定位方法空白 "evolution-step verifier gating"（四条演化路线中仅 tool/skill 内建验证关口）；7/14 已生成 2 个针对该空白的 raw idea（[[Ideas/CounterfactualProbe-EvolutionGate]]、[[Ideas/RetrievalMediated-MemoryMisevolution]]，均 18/25）；工业侧 [[Papers/2607-ABotAgentOS]] self-evolution 资产 8 存 1 亦印证
- **question**: 是否 resume 该方向？三个选项：(a) resume 为独立 active direction（假设已被外部验证，证据链完整）；(b) 不独立 resume，将 evolution-step verifier gating 并入 AFE 的 verify affordance（由 [[Ideas/HybridVerifier-GUIRuntime]] 承接为第二应用场景）；(c) 维持 paused，先对 2 个 raw idea 做 idea-evaluate 再决策。Researcher 倾向 (c)→(b)：先评估 idea 存活性，存活则作为 AFE verify affordance 的应用场景推进，避免新开独立方向分散 primary 精力
- **related_direction**: Self-Improving Agent Reliability, Agent-Facing Environment Runtime
- **resolved**: 2026-07-21 Supervisor 决定 — **resume 为 active direction（medium），但 scope 限定文献侧**：只收集 paper → digest → survey → idea，不做实验；实验侧仍由 AFE verify affordance 承接。已执行：agenda 移入 Active、team-config 关键词扩充、2 个 raw idea 进入 idea-evaluate

### AFE 的动机前提被证伪，差异化是否重锚 — 2026-07-30

- **raised_by**: agenda-evolve
- **context**: 7/30 memory-distill 产出的证据在三个点上同时冲击 primary direction 的论证结构。(1) **动机前提被证伪**：[[Papers/2606-GUIvsCLI]] 用 440 个 matched 任务做同任务同预算对照，screen-only GUI 59.1% 反而高于 original-skill CLI 48.2%，真正把 CLI 推到 69.3% 的是 verifier-guided skill 修补——"GUI 接口本身低效、给 agent 换更好的接口就能提升"这一 AFE 常用动机说法不成立，收益来源被指向 verify/repair 而非接口模态。(2) **affordance 形态被外部证据指定**：[[Papers/2602-VAGEN]] 94.0 P / 95.2 R、[[Papers/2607-InteractiveRewardAgent]] 86.9%、[[Papers/2607-SeekJudge]] 收敛到"读文件/配置/系统状态的执行后取证"这一形态，而非暴露 success label；[[Papers/2604-VLAA-GUI]] FDF>86% 确认 false completion 是主导失败形态。这意味着 AFE 的 verify affordance 设计空间比原设想窄——差异化不再在"要不要给 verifier"，而在"取证通道暴露什么、如何避免变成 oracle"。(3) **收益传导存疑**：[[Papers/2607-InteractiveRewardAgent]] 把取证式 verifier 接入 RL，最终 34.0% vs script-based 34.9%（持平），说明"判定精度提升"不自动等于"agent 能力提升"
- **question**: AFE 的 hypothesis 是否应重写——把动机从"暴露 agent-facing affordance 弥补接口低效"改为"长程失败的主导形态是 false completion，缺的是执行期可验证/可恢复状态，而这与接口模态正交"？连带两个子问题：(a) 若接口模态不是瓶颈，AFE-MiniSuite 是否还需要 GUI/CLI 双模态臂，还是应把预算集中在 observe/verify affordance 的因果对照上？(b) 鉴于 IRA 的持平结果，AFE 的主 claim 是否应从"提升 task success"退到更可辩护的"降低 false completion 率 + 提升 wrong-turn recovery"（即使 success 不变也算正向结果）？
- **related_direction**: Agent-Facing Environment Runtime
