---
last_updated: "2026-10-29"
updated_by: literature-survey (CUA-Survey §10.11)
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
- **evidence**: [[Topics/CUA-Survey]], [[Papers/2604-GoClick]], [[Ideas/ScaleInvariant-Grounding-GUI]], [[2500-GuiActorCoordinateFree]], [[Papers/2604-AutoGUIv2]] (dichotomy: fine-tuned grounding 强于通用 VLM), [[Papers/2604-WindowsWorld]] (跨应用是独立瓶颈 L1 46% vs L2 14%，grounding 能力比 reasoning 更关键), [[Papers/2605-WorkspaceBench]] (Heterogeneous File Understanding 和 Lineage Tracing 是 workspace agent 瓶颈，最佳 agent 68.7% vs 人类 80.7%，说明 grounding 在复杂环境中仍有显著提升空间), [[Ideas/EvidenceDependence-GUIGrounding]] (18/25, Action Collapse Rate 量化 grounding 是否真正依赖视觉证据), [[Papers/2606-VisualFLIP]] (VLM grounding 评估从单点 accuracy 转向 counterfactual evidence dependence), [[Papers/2606-DecodableNotGrounded]] (灰图 vision-ablation arbiter 推翻 probe+steering 验证的 latent-knowledge 结论，grounded/prior/inverted 三 regime——counterfactual 诊断 pattern 第 3 独立数据点，7/3 已升 provisional insight), [[Papers/2603-VideoOasis]] (捷径 ablation + 5 模型共识审计 14 个视频 benchmark：55% 样本可被无视觉/无时序捷径攻破——第 4 独立数据点), [[Papers/2607-VisualAccessBoundary]] (Visual Access Sweep 层×时间因果掩蔽：CoT 增益受 perceptual readout 制约而非延长图像访问——第 5 独立数据点，7/15 该 insight 已升 **validated**), **2 条 7/30 新 insight**（**validated** 预算匹配对照——8 源 4 日期，直接约束 FPN 原型的对照设计；provisional 观察表示最优点随 backbone 能力 × 任务阶段非单调——[[Papers/2409-ElementOrdering]] / [[Papers/2604-ReadMoreThinkMore]] / [[Papers/2605-A11yCompressor]] 等 7 源，要求跨分辨率评估分 regime 报告），**10-29**：Right Click, Wrong Box（[arXiv 2610.36831](https://arxiv.org/abs/2610.36831)，全文核验）复核 29 篇论文的 58 组比较，中位绝对差距 1.15 点、21 组落在单 seed 噪声内；同一配方换三个 seed 重训，ScreenSpot-v2 在框奖励 / 结果奖励下最多变 1.3 / 2.6 点；框内/框外判定与真实点击结果在 Gitea / Oscar 上有 17.7% / 31.2% 不一致，改用结果等价评分后头部模型差距从 2.9 缩到 1.7——既有 grounding 增强类文献的报告增益多数未超过 seed 幅度
- **next_action**: 实验已重设计为 GUI-Actor baseline（Experiments/2026-04-29-ScaleInvariantGroundingGUI 已更新），下一步：原型验证 FPN + multi-resolution training 在 ScreenSpot-Pro 上的效果（备选低成本切入：用 EvidenceDependence-GUIGrounding 的 Action Collapse Rate 做无训练 grounding evidence-dependence 诊断——方法论基础已随 counterfactual 诊断 insight 升 validated 而确立，可借 DecodableNotGrounded 三 regime 分类 + VisualAccessBoundary 的层×时间掩蔽维度升级设计，跨分辨率评估用 arbiter 对照把失败分解为 evidence loss vs prior reliance）。**7/30 两项口径约束**：(1) FPN 原型的对照组必须 **budget-matched**——multi-scale 分支引入的额外 FLOPs/token 需折算给 single-scale baseline，否则增益与"多花算力"不可分离（validated insight，8 源 4 日期）；(2) 跨分辨率评估须按 regime 分层报告而非报单一均值——观察表示的最优点是 backbone 能力 × 任务阶段的非单调函数（[[Papers/2409-ElementOrdering]] 强模型对 DOM 顺序不敏感、弱模型敏感；[[Papers/2604-ReadMoreThinkMore]] 信息量随阶段反转），把"哪个 regime 下 multi-scale 有效"当作结论而非噪声；**10-29 口径约束 (3)**：FPN 原型的 headline 差距须同时以框评分与结果等价评分报告并跨 ≥3 seed，低于 1.3–2.6 点的 seed 幅度不得作结论；CUA-Survey §10.11 把"更多 grounding 奖励设计"列为不建议方向，本方向若继续，重心落在结果等价评测与交互可见性诊断（IGG，摘要级）而非新 grounding 模型
- **confidence**: 0.5 (↓0.05——架构级 multi-scale 假设本身仍无直接反证，但 Right Click, Wrong Box 显示 grounding 文献的典型增益（中位 1.15 点）低于 seed 噪声，hypothesis 所依赖的"既有增强方法有效"的先验证据被整体折算；原型必须拿出 >2.6 点且跨 seed 稳定的差距才算正向)

### RL-based GUI Agent Training

- **priority**: medium
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: Rule-based RL（GRPO 风格）配合结构化 action reward，可以以 10x 更少的训练数据达到或超越 SFT 的 GUI action prediction 性能，且 OOD 泛化更强
- **evidence**: [[Topics/CUA-Survey]], [[2500-UiR1EnhancingEfficient]], [[Papers/2604-ClawGUI]], [[2500-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]], [[Ideas/ForkPoint-CreditAssignment-GUI]], [[Papers/2604-AutoGUIv2]] (fine-tuning on agent data 对 grounding 有显著增益), [[Papers/2604-SOLAR-RL]] (first failure point detection, 3-stage reward shaping), [[Papers/2602-ProxMO]] (PSC+PSA, 90.6% ALFWorld, state similarity credit assignment), [[Papers/2605-DUDE]] (asymmetric reward ω=10 for deception, hybrid-reward learning 减少 53.8% 欺骗易感性), [[Papers/2605-Skill1]] (unified skill selection/utilization/distillation via single policy, reward signal frequency decomposition for credit assignment), [[Papers/2601-WebGym]] + [[Papers/2606-AsyncWebRL]] (大规模 visual web agent RL：rubric evaluator + async rollout，OOD 泛化来自任务分布 scaling 而非新算法), [[Papers/2606-CUAGym]] (task/state/reward.py 共生成 32K+ verified RLVR tuples，环境侧合成 RL 监督), [[Papers/2606-MobileForge]] (hint-contextualized GRPO：corrective hint 作为 state 条件而非 reward 项，免标注 mobile 自适应，ForgeOwl-8B AndroidWorld 77.6% Pass@3——是 rule/feedback-based reward design 的具体实例), [[Papers/2606-GUIAgentExploration]] (HER 式 hindsight relabeling + TDHAF：low-level 训练无法向上泛化 80.5%→9.1%，组合泛化层级敏感), [[Papers/2607-GRPONullWebAgent]] (受控阴性结果：GRPO 仅在 sampled-policy headroom 存在时有效，18 组对照 + 双 regime 机制定位), [[Papers/2607-MAG]] (expert 轨迹注入 GRPO 使 9B SR 6.9%→13.2%——外部监督注入是无 headroom 时的补救), [[Papers/2607-UIMOPD]] + [[Papers/2607-DirectOPD]] (on-policy distillation 迁移 RL 增量：跨平台 multi-teacher / weak-to-strong log-ratio implicit reward), 7/15 新 provisional insight（失败轨迹一等资源化：恢复监督/课程/runtime patch 三种复用形态是方法区分轴），**10-29**：VeriCUA（[arXiv 2610.26469](https://arxiv.org/abs/2610.26469)，全文核验）给出"奖励 verifier 质量→policy 收益"的第一个数据点（训练中 judge false-negative 10.0→4.6，Actor Pass@4 43.93→47.14、held-out MultiApp 17.57→22.97，Actor RL 单次运行）；OS-Helix（[arXiv 2610.22234](https://arxiv.org/abs/2610.22234)，全文核验）同 SFT 起点下标准 GSPO 把代码动作占比 27.9%→40.0% 且 OSWorld-Verified 降到 60.47，按步平衡的 GSPO 保持 26.1% 并升到 66.44——动作类型配平是 reward 设计里的独立变量；Right Click, Wrong Box：把结果等价直接作为 3B 模型的 GRPO 奖励没有稳定差异（Gitea −0.18、ScreenSpot-v2 −0.08）
- **next_action**: credit assignment 暂停待 Supervisor 决策（5/6 Discussion 未回复）；rule-based reward design 子方向新增两个具体切入点：(1) 失败轨迹复用形态的 reward 化——VeriGUI/RoTS/SRC/WebRL 证据链已备（7/15 insight），GUI 域"哪种失败复用形态最有效"无系统对比；(2) GRPO headroom 前置诊断——用 GRPONullWebAgent 的 sampled-vs-greedy 判据做训练资源分配 gating，可作低成本复现起点（7/30 该判据获第三个独立表述 [[Papers/2604-PassKT]]，已升 insight，可直接作为实验前置检查）。**7/30 新增强制口径**：本方向任何 RL 实验必须跨 seed × data draw 报告（[[Papers/2607-TeachStop]]：单次 run 无法与 nondeterminism 分离）并声明 optimizer（[[Papers/2607-MuonAgenticRL]]：仅换 optimizer 即把同一 ALFWorld/GiGPO 配置从 0.320 抬到 0.633），否则结果不具可比性；**10-29 新增切入点 (3)**：CUA-Survey §10.11 D1——以自述隔离的 judge 做 RL 奖励，检验 judge 对 actor 自述的依赖是否是 policy 学会"宣称完成"的奖励通道（预测：隔离后 unhedged false completion 率下降而 clean success 不降）。基座为 VeriCUA 开源代码 + OSWorld 无网络子集，中等成本；检索未见把自述可见性作为奖励侧变量的工作。须按 7/30 口径跨 seed × data draw 报告
- **confidence**: 0.4 (维持——VeriCUA 数据点方向正确但幅度 3–5 点且单 seed，OS-Helix 显示 RL 增益对 reward 配平敏感；D1 把本方向第一次挂到 verifier 这一侧，可操作性上升，但 hypothesis 的"10x 数据效率"仍无受控支持)

### Agent-Facing Environment Runtime

- **priority**: high (**primary** — Supervisor 2026-06-26 确认为 primary direction，GUI Grounding Robustness 降为 secondary high)
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 把环境后台已有的 state / reset / verifier / fork 能力以 task-agnostic、non-oracle 的 agent-facing affordance 暴露给 GUI/web/CUA agent，可在 zero/low-training 条件下显著提升 long-horizon task success、wrong-turn recovery，并降低 reward hacking 与 false completion——且该收益不能被 prompt-only baseline 复现
- **evidence**: [[Topics/CUA-Survey]]（2026-07-20 起合并原 AgentFriendlyEnvironment / GUI-Environment / WebEnvironment-Engine 三 survey）, [[Topics/CUA-Survey]], [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]], [[Reports/2026-06-24-GUIEnvironment-RecentWorks]], [[Ideas/AgentFacing-WebRuntime]] (18/25), [[Ideas/HybridVerifier-GUIRuntime]] (18/25), [[Papers/2600-WebHarbor]] (真实网站 Docker mirror + 快速 reset), [[Papers/2606-CUAGym]] (32K+ verified RLVR tuples), [[Papers/2605-SaaSBench]] (resolved 3.8%，长程组合可靠性极低), [[Papers/2606-WeaveBench]] (hybrid GUI+CLI+Code，35.2% failure 来自 reward hacking), [[Papers/2605-OpenComputer]] (programmatic verifier 94.1% human alignment > LLM judge), [[Papers/2606-ENVS]] (环境 oracle 可作为 SFT 监督来源), [[Papers/2606-OpenRath]] (Session-as-first-class-value：把碎片化 runtime state 统一为可随程序值流动的 observable state——正是 agent-facing observable affordance 的一种工程实现，但仅 technical report 无 benchmark), [[Papers/2606-AgentMemorySystem]] (12 个 agent memory 系统系统评测；但 workload 全是文本/DB，**完全无 GUI/CUA visual memory 场景**——反向印证 agent-facing memory 在 computer-use 场景仍是空白), [[Papers/2606-PolicyGuard]] (pre-execution sub-agent verifier + 定向 remediation 在 dialogue/tool-call 域实证 runtime verifier affordance：τ²-bench airline Pass⁴ +6~12pp、block rate 减半), [[Papers/2606-Dockerless]] (evidence-grounded verifier 作为 SFT filter + RL reward，接近 test-execution RL), 2 条 7/3 memory insight（"Verifier 角色迁移" 升 **validated**；"runtime state 一等对象化" provisional：OpenRath/MemGUI/ArborHTR/LUMOS/AgenticSTS 五论文收敛——observe affordance 的接口形式有工程收敛证据）, [[Topics/CUA-Survey]] §1–2 (需求侧六轴推导：环境能力全部服务 trainer/evaluator、无人暴露给 agent), [[Topics/CUA-Survey]] (gap 核查推翻先验：Crab 已在 sandbox 域把 rollback 暴露为 agent 工具但只测效率不测 success；AgenticExplorationSystems 表明系统社区已入场——**窗口收窄**), [[Topics/CUA-Survey]] (真实长程瓶颈在 verify/recover 而非 grounding，VeriGUI 72.3% 失败为空转 timeout), [[Reports/2026-07-08-WebAgentTrainingInfra-Pulse]] (差异化应落在 agent-visible affordance contract 而非更大任务集), 2 条 7/15 新 provisional insight（judge/RM precision 普遍 70–85% → verify affordance 的精度边界设计约束；失败轨迹一等资源化 → failure evidence 应作为 affordance 暴露）, **4 条 7/30 新 insight**（[[Papers/2606-GUIvsCLI]] 440 任务 matched 对照：screen-only GUI 59.1% > original-skill CLI 48.2%，**"GUI 接口低效"这一动机前提被证伪**，真正把 CLI 推到 69.3% 的是 verifier-guided skill 修补 → 差异化须重锚到"执行期可验证/可恢复状态缺失"；[[Papers/2602-VAGEN]] 94.0 P + [[Papers/2607-InteractiveRewardAgent]] 86.9% + [[Papers/2607-SeekJudge]] → verify affordance 的形态被证据指定为**取证通道**（读文件/配置/系统状态）而非 success label，且 [[Papers/2604-VLAA-GUI]] FDF>86% 确认 false completion 是主导失败形态；[[Papers/2607-GUIStateBelief]] + [[Papers/2605-EnvTrustBench]] EMR 83.3% → observe affordance 须携带 provenance/freshness 元数据，这是与既有 typed-state 工作的差异化点；**validated** 预算匹配对照 insight → AFE-MiniSuite 的对照设计约束），**10-29 CUA-Survey §10.11（2026-09/10 arXiv 扫描，20 篇全文核验）三组证据**：(a) 动机锚到 false completion 的外部支撑——Who Verifies（[arXiv 2610.29609](https://arxiv.org/abs/2610.29609)）同 judge 同轨迹只隐去 actor 自述，危险误报召回 +43.4 pp；CUA-Recovery（[arXiv 2610.27645](https://arxiv.org/abs/2610.27645)）60.0% 的错误只在最后一步才出现证据、中位延迟 17 步；PersonaCUABench（[arXiv 2610.22990](https://arxiv.org/abs/2610.22990)）交付时被判完成的失败格经站点状态核验从 56% 降到 27%；(b) verify affordance 的精度边界被改写——VeriCUA（[arXiv 2610.26469](https://arxiv.org/abs/2610.26469)）从 4B 到 GPT-5.4 的 prompted judge 宏平均一致率全停在 68–70%，在线 Probe 轮数 K=0→2 把 OSWorld 一致率 74.09→82.00，判断策略比 judge 规模重要；AgentHorizon（[arXiv 2610.11050](https://arxiv.org/abs/2610.11050)）judge 的 harness 能把结果移动到与换模型同一量级，副作用类错误召回在十个配置上只有 0–24%；(c) fork 边界的空位——StateFork（[arXiv 2609.38648](https://arxiv.org/abs/2609.38648)）把可分支状态定义到 filesystem + shell session + process memory + local service，GUI / 显示状态与远端状态明确不支持
- **next_action**: 在 WebHarbor mirror 或 CUA-Gym-Hub mock apps 上原型化 AFE-MiniSuite（observe/map/rollback/verify affordance + C0–C7 因果对照），先验证 Web-only causal mechanism。**7/30 三项设计修正**：(1) verify affordance 实现为 post-execution 取证接口（可查询文件/配置/系统状态的只读通道），不暴露 success label；(2) observe affordance 的返回值须带 provenance 字段（来自哪个通道、何时采样、是否与像素一致）；(3) 对照臂在 prompt-only 之外必须再加 **budget-matched arm**（affordance 调用消耗的 token/步数需折算给 baseline）与 **skill-repair arm**（GUIvsCLI 显示 verifier-guided skill 修补是同一收益的竞争解释），否则增益不可归因。竞争窗口继续收窄（Crab / AgenticExplorationSystems 已入场）；待解风险：IRA 的取证式 verifier 作为 RL reward 只做到 34.0% vs script 34.9%（持平），说明"取证能提精度"不自动等于"能提 agent 能力"，AFE 的因果收益 claim 需要独立验证。**10-29 三项补充**：(4) verify affordance 的对照必须隔离 actor 自述并固定 judge harness——Who Verifies 与 AgentHorizon 把这两者证明为独立因果变量，不控制则 verify 增益与"judge 读到了自述"不可分离；(5) rollback affordance 的 fork 边界定为"正在运行的桌面 + 浏览器 + 本地数据库"，这是 StateFork（只到 local service、GUI 不支持）与 Crab 之后仍空着的位置；(6) 7/30 Discussion 的重锚问题现在有 (a) 组三份外部证据，可在 Supervisor 答复前先按"降低 unhedged false completion + 提升 wrong-turn recovery"设计主指标，task success 作次指标。CUA-Survey §10.11 的 D5（等证据预算的 programmatic / passive / interactive verifier 对照）作本方向对照组而非独立项目
- **confidence**: 0.5 (维持——动机重锚到 false completion 获三组外部证据，verify affordance 的两个控制变量（自述可见性、judge harness）被外部实验指定；下调项：VeriCUA 的在线 Probe 与 Probe-and-Resume 已把"verifier 在线取证"做成系统，agent-facing 一侧可守的差异化只剩自述隔离与全栈 fork 边界两个位置，竞争窗口再收一截)

### Self-Improving Agent Reliability

- **priority**: medium（**literature-only** — Supervisor 2026-07-21 决定 resume，scope 限定为 paper 收集 → digest → survey → idea 孵化，**不做实验**；实验侧衔接由 AFE 的 verify affordance（[[Ideas/HybridVerifier-GUIRuntime]]）承接）
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 自增强循环存在系统性验证偏差——该假设已被外部完整实证（[[Papers/2509-Misevolution]] 四路径实测：memory reward hacking >60%、workflow ASR 54→83）。**2026-07-30 开放问题改判**：原判断"evolution-step verifier gating 是方法空白"已被证伪——闸门不仅存在，还是收益的主承重件（[[Papers/2605-GRASP]] 去闸门 88.8%→63.5%，且"配平探针算力但丢弃验证结论"同样塌回 67–71%；[[Papers/2606-SkillNb]] 去 gate 回归率 3.3%→18.6%）。开放问题因此收窄为闸门的**判据维度**（现有闸门只测性能回归，安全/漂移维度空白，见 [[Papers/2604-ExperienceSafetyRisks]]）与**判定独立性**（self-review 式闸门易 rubber-stamp）
- **evidence**: [[Topics/SelfEvolvingAgents-Survey]], [[Papers/2509-Misevolution]], [[Papers/2607-ABotAgentOS]]（工业侧 8 存 1 印证）, [[Topics/CUA-Survey]], [[2500-UiGenieSelfImproving]], [[Ideas/AdversarialVerification-SelfImproving-GUI]], [[Ideas/CounterfactualProbe-EvolutionGate]] (archived 13/25，gate 赛道 3 个月 ≥6 并发被占), [[Ideas/RetrievalMediated-MemoryMisevolution]] (**validated 19/25，lead idea**，机制获 2606.23075 独立命名), 2026-07-21 survey-refresh 新证据链：「监督资产是 policy 相对的」跨域收敛（[[Papers/2607-SEED]] 静态 skill 库 −7.4 / [[Papers/2607-KnowActGUIClaw]] 跨 backbone +3.1 但跨演化阶段过期 / [[Papers/2607-EvoCUA15]] RL 数据子集 policy 相对）+ skill 路线内化 vs 外挂分岔（[[Topics/CUA-Survey]] / [[Topics/SelfEvolvingAgents-Survey]]），**10-29**：CUA-Survey §10.11 D2 并入 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]]——ReInBench（[arXiv 2610.36471](https://arxiv.org/abs/2610.36471)）给出自恢复基率（OSWorld 54.8%、web 32.8%，全部错误都恢复的轨迹完成率 60.0% 对一个都没恢复的 20.6%；ReCoF 预测自恢复宏 F1 73.53 对 68.75，干预未执行）；AndroidFlux（[arXiv 2610.34384](https://arxiv.org/abs/2610.34384)）倒回相对继续在各深度均为正（前 3 步 +8.76、7 步后 +3.41），注入增益随深度从 −1.01 到 +5.86，两者差随深度移动 12.22 点；CUA-Recovery（[arXiv 2610.27645](https://arxiv.org/abs/2610.27645)）察觉≠修复（15.6% 对 12.2%）；Lost in Recovery（[arXiv 2610.27954](https://arxiv.org/abs/2610.27954)）隐式恢复率 EvoCUA-32B <1%，推理时外挂显式恢复 agent 对 Qwen3.5-9B +4.88 但对 UI-TARS / EvoCUA 反而拖低
- **next_action**: ✅ 2026-07-29 完成——上述 8 篇（gate 家族 GRASP/SKILL.nb/ASG-SI/SEACertificates/SEVerA + memory 安全 Safety-in-SelfEvolving/MemRL/MemoryGraft）+ 另 12 篇（RSI 谱系、负结果三线、env/multi-agent co-evolution、operation-level memory、lifelong benchmark）共 20 篇一手核验后，[[Topics/SelfEvolvingAgents-Survey]] 全面重构至 12 节 CUA 标准（119→401 行，含 §6.2 五粒度 gate 家族小节、§3.6 横切表、§9 benchmark 全景表、21 行 Key Evidence Matrix；Open Problem 已更新为"gate 仅覆盖性能回归、安全维度空白 + self-review gate rubber-stamp"）。**待 Supervisor 复核 2 项**（非 autoresearch 可自批）：(1) L51 evidence 中"RetrievalMediated 机制获 2606.23075 独立命名"经本轮 gap-pass 核出有误——2606.23075 仅在 §4.2/4.3 描述、未命名 retrieval-mediated 机制，概念首发权未被占据，需据此复核 RetrievalMediated 的 novelty/lead-idea 定位；(2) [[Papers/2512-MemoryGraft]] 证据实为 retrieval-level 非其主张的 cross-agent transfer（rating 2）。复核后下一步转 survey-refresh 增量维护 + 依 gate 缺口孵化 idea（衔接 [[Ideas/HybridVerifier-GUIRuntime]]）。**2026-07-30 更新**：gate 归因反转后，idea 孵化的靶心从"给自演化加闸门"移到两处——(a) 闸门判据的安全/漂移维度（性能回归闸门对 benign 经验引起的安全漂移完全不可见），(b) 判定独立性（GRASP/SKILL.nb 的闸门都依赖 held-out 测试集或环境可观测谓词，开放任务上无此信号时闸门如何成立是无证据区）；另建议 [[Ideas/RetrievalMediated-MemoryMisevolution]] 的实验设计补一个 GRASP 式"配平算力但丢弃验证结论"对照臂，用以分离"检索干预"与"多花算力"两种解释。**10-29**：MismatchTriage 的 Phase 0–1（alert state bank、Continue 基率）与 Phase 3 gap / kill 判据改用上述外部基率预设（idea 文件 v4.1）；下一步对该 idea 跑 idea-evaluate 复核 novelty——When to Intervene 的 ReCoF 只预测不干预、AndroidFlux 只评测不做策略，"以可恢复性与深度为条件的 selector"位置检索未见被占
- **confidence**: 0.45（维持——核心假设仍被外部实证支撑；lead idea 之外，MismatchTriage 获得此前缺的基率与交叉点，可证伪性上升；下调项不变：方法空白收窄，lead idea 的 novelty 定位待 Supervisor 复核）

---

## Paused Directions

### Personal CUA Safety & Contextual Integrity

- **priority**: low
- **status**: paused
- **origin**: researcher-discovered
- **hypothesis**: personal computer-use agent 的隐私泄露主要来自 normal-use 的 contextual disclosure 而非 adversarial attack；以 task-scoped permission + trajectory-level privacy guard 作为 runtime intervention，可显著降低 inappropriate disclosure，且优于 prompt-level instruction
- **evidence**: [[Ideas/PersonalizedSafety-CUA]] (20/25), [[Papers/2606-AgentCIBench]] (leakage 67.9%), [[Papers/2606-MyPCBench]], [[Papers/2606-BraveGuard]], [[Papers/2606-PrivacyAlign]], [[Papers/2606-OverPrivilegedTools]] (safety-alignment 不迁移到 least-privilege 的 negative result)，**10-29 量化锚点（CUA-Survey §10.8 / §10.11，全文核验）**：SA-CUA（[arXiv 2610.18508](https://arxiv.org/abs/2610.18508)）按 accessibility-tree 信任规则遮蔽不可信元素，把三套注入攻击 ASR 降到 0.0 的代价是 OSWorld 完成率 58.3→30.6、token 7.5×、遮蔽误报 56–77%（integrity 非 confidentiality）；Control OSWorld（[arXiv 2610.03818](https://arxiv.org/abs/2610.03818)）整轨迹监督 TPR@1% 0.92，去可见文本 0.808，逐步监督 0.49；318 次隐蔽副任务 agent 无一主动拒绝、完成 90.3%
- **pause_reason**: Supervisor 2026-06-26 决定 Personal CUA Safety 不在当前 Mission scope 内（Mission 聚焦 grounding/operating GUI 可靠性 + Agent-Facing Environment Runtime）。已积累的证据（AgentCIBench 67.9% leakage、OverPrivilegedTools alignment-不迁移、PrivacyAlign 训练侧对齐）保留备查，不再主动推进。**10-29 补充**：效用代价与监督信号来源有了量化锚点（见 evidence），但两份工作针对 injection 与 oversight 而非 contextual disclosure，不构成 resume_condition 触发；是否重启由 Supervisor 决定
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
- **update_2026-10-29**: 未答复。CUA-Survey §10.11 新增三组外部证据支持重锚到 false completion（Who Verifies 隐去自述使危险误报召回 +43.4 pp；CUA-Recovery 60.0% 的错误只在最后一步出现证据；PersonaCUABench 交付时误判 56%→27%），并把 judge 对自述的可见性与 judge harness 证明为独立因果变量。子问题 (b) 的"降低 false completion + 提升 recovery"主 claim 现在有可对照的外部基准（Who Verifies F1、AgentHorizon 副作用召回、AndroidFlux 深度曲线）。next_action 已先按此设计主指标，等待 Supervisor 对 hypothesis 改写与双模态臂取舍的决定
