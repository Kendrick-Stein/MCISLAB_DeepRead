### 10.1 Scalable and Verifiable Data

CUA 数据扩展已从增加 trajectory 数量，推进到联合生成 task、initial state、transition 与 validator，并根据当前 policy 的能力边界动态采样。[[Papers/2607-SCALECUA]] 展示了 task supply、frontier sampling 与 context efficiency 的联合路线；[[Papers/2607-TeachStop]] 则在其受控设置中发现，data draw 与 run nondeterminism 足以主导单次训练结论。可执行 validator 不自动保证任务有效，更多 trajectory 也不自动等于更多可靠监督。

下文将 **Observed Tension** 用于已有证据揭示的结构性冲突，将 **Validated Gap** 用于当前调研范围内被 benchmark 或系统边界明确暴露、但尚未闭合的能力缺口；后者不表示"无人研究"。

**[Observed Tension] Policy-relative task/reward 共演化与统计标准。** Task、milestone、skill 与 validator 会随 policy 提升而失去区分度；静态任务池因此会逐渐被已掌握任务与当前不可学任务占据。可扩展数据管线需要同时报告 task feasibility、validator validity、transition validity、recovery coverage、benchmark overlap 与 cross-domain transfer，而不能只报告任务数或轨迹数。高价值数据的单位应从完整 trajectory 进一步收缩为带来源、前置状态、后置状态和独立验证结果的 causal transition。

**最小决定性实验。** 在同一组 versioned tasks 上固定训练预算，使用至少三次独立 data draw，并在每个 draw 内运行多 seed；以 paired held-out trajectories 报告 end-to-end success、validator error、environment failure、task validity 与 wrong-sign probability。Frontier sampling、uniform sampling 与固定 curriculum 必须共享任务生成器、actor、verifier 和调用预算。

### 10.2 Long-Horizon Planning and State Tracking

Long-horizon 研究正从延长动作序列，转向显式建模状态依赖、动态约束、跨应用信息和中途失败。[[Papers/2607-SEE]] 说明 verified local transition 可以被组合为更长训练路径，但其证据支持的是 step-level generalization，而不是完整 live workflow；[[Papers/2607-EvoGUI]] 将 temporal ordering、inverse action 与 successor discrimination 拆成局部诊断；[[Papers/2606-OSWorld2]] 则把动态状态、隐式约束和 partial checkpoint 放进长流程评测。

**[Validated Gap] Compositional 与 causal long horizon 的统一基准。** Graph path 或 simulator rollout 只需保证局部 edge 可达；真实长程任务还要求维护跨步骤状态、处理被后续观察覆盖的约束、识别不可逆副作用，并从异常分支恢复。当前证据支持二者存在实质差异，但尚不足以证明更长的合成路径会稳定转化为真实端到端成功。

规划状态不应只是扁平 action history。它至少需要区分当前目标、已完成且可验证的 milestone、仍然有效的证据、被 supersede 的约束、未决副作用与可恢复 checkpoint；否则更长 context 只会延后错误暴露。

**最小决定性实验。** 对同一批 versioned workflows 构造 graph-composed、simulator/mirror 与真实执行三种版本，并加入可复现的 counterfactual branches。固定 policy、step budget 与 verifier，分别报告局部 transition accuracy、checkpoint completion、最终 success、environment failure、恢复率和跨 app/domain transfer；用真实小样本 audit 校准 simulator 与 mirror。

### 10.3 Robust Grounding and Dynamic Environments

Robust grounding 的核心正在从"识别哪个控件"扩展为"判断当前行动究竟由哪份证据支撑"。Pixels、DOM/AXTree、memory 与 prior 可能同时存在且彼此冲突；如果系统不记录来源、新鲜度与失效关系，hybrid observation 反而会放大 stale evidence。

[[Papers/2605-EnvTrustBench]] 在刻意注入误导 claim 的 coding/CLI 对抗压测中得到 83.3% aggregate Environmental Misgrounding Rate，并发现所测 scaffold 虽有 execution-authority gate，却没有针对 runtime feedback、evidence verification 或 provenance 的 enforceable gate。该数字不能外推为真实 GUI 部署发生率，但它验证了证据接地缺陷可以被系统化测量。[[Papers/2606-AgentTracesToTrust]] 将 execution provenance 表示为 typed graph，并要求 memory item 记录创建或更新时间、支撑证据、证据是否仍有效及是否被后续观察 supersede；这是规范性框架，尚未证明记录这些字段会自动提高 GUI success。[[Papers/2606-AlwaysOnAgents]] 转述的第三方案例进一步表明，保留 stale conclusion 却丢失 source 的记忆可能比空记忆更难纠正，source-first write policy 是一个候选修复方向。

**[Validated Gap] Provenance-aware belief fusion。** GUI 侧仍缺少把 provenance、freshness 与 uncertainty gate 落到 pixel–structure–memory 冲突上的 frozen-policy 因果实验。研究目标不应只是增加一次 consistency prompt，而应使 evidence admission、selective invalidation 与 action gating 成为可学习、可校准且可审计的 runtime contract。

**最小决定性实验。** 固定 policy、prompt、任务和总调用预算，对照 screenshot-only、hybrid observation、provenance-tagged observation 与 freshness-gated observation。注入可控的 pixel/AXTree 冲突、界面更新和 stale memory，报告真实 task success、misground rate、错误传播长度、abstention、恢复率与副作用。

### 10.4 Verification-Centric Computer Use

Verifier 已从终局截图判断，分化为 programmatic state checker、visual/rubric judge 与 interactive verifier。三类方案的困难不在同一位置：programmatic checker 可靠但覆盖窄，visual judge 可扩展却受 partial observability 与 hallucination 影响，interactive verifier 能主动取证但成本更高、绑定在线实例，并可能被 actor 操纵。[[Papers/2504-AgentRewardBench]]、[[Papers/2510-CUARewardBench]]、[[Papers/2602-VAGEN]] 与 [[Papers/2605-OpenComputer]] 分别覆盖这些边界。

**[Observed Tension] Hybrid verifier 的可测边界。** 提高 evidence access 往往会提高覆盖率，也会增加调用成本、权限范围与污染环境的风险；通过 abstention 换取 precision，则可能系统性丢弃困难但有价值的训练样本。因此不存在脱离 evidence setting 的"最佳 verifier"。

Verification-centric CUA 应把 verifier 当作与 actor、environment 同级的系统组件。每个 verdict 都应携带 evidence provenance、coverage、uncertainty、abstention reason 与环境版本；step-level reward 还需说明它评估的是 action plausibility、实际 state change，还是最终目标的因果贡献。

**最小决定性实验。** 固定 trajectory、actor 与 evidence budget，交叉比较 programmatic、visual/rubric 与 interactive verifier，统一报告 precision、recall、coverage、cost、abstention、抗操纵能力和环境污染率。只有等证据、等预算对照才能判断主动取证是否突破 verifier trade-off。

### 10.5 Error Detection and Recovery

错误恢复研究已从检测重复动作或 false completion，推进到可控 error injection、checkpoint、rollback 与局部修复。[[Papers/2605-GUIRobustEval]] 将 error depth 作为恢复难度变量；[[Papers/2604-Crab]] 则证明 agent-facing rollback 可以在 shell、filesystem 与 process 状态上实现，但没有覆盖 browser backend、账号、远程服务和 GUI application state。

**[Validated Gap] 全栈 fork 与 non-idempotent recovery。** Browser、Mobile 与 Desktop 的前端、后端、账号、文件、clipboard、back stack 和网络状态尚未形成统一 checkpoint。支付、发送、提交和删除等动作还可能部分成功；单纯 replay 或 URL backtracking 会重复副作用，需要 transaction-aware rollback、compensating action 与恢复后的 consequence verification。

恢复策略必须显式保留 `Continue / accept`：并非所有异常都应回滚，某些界面漂移可以安全接受，某些动作则已经越过不可逆边界。系统应预测每种 recovery macro 的成功概率、可行性、成本和副作用，而不是只分类一个固定"正确恢复动作"。

**最小决定性实验。** 固定 policy、prompt、任务和调用预算，对照 screenshot-only、semantic action、state-grounded feedback 与 full-stack checkpoint。对每个错误 fork 检查 screenshot、AXTree、back stack、clipboard、app database/files、OS state、verifier consistency、restore divergence 与 branch isolation，并报告 task success、错误传播、恢复率、重复副作用与 compensating-action 成功率。

### 10.6 Hybrid GUI-CLI-API Interaction

跨平台统一更可能来自共享的 `observe–ground–act–verify–checkpoint` 生命周期，而不是把 GUI、CLI 与 API 压成同一种动作。[[Papers/2508-ComputerRL]] 将 API 与 GUI 同时暴露给 policy，[[Papers/2508-CoAct1]] 由 orchestrator 在 coding action 与 GUI operation 之间路由，[[Papers/2602-ActionEngine]] 则把预构建的 GUI state-machine memory 编译成确定性程序；[[Papers/2607-Tactile]] 从另一方向把 accessibility semantics 编译成带 source、geometry、affordance 与 verification cue 的 action object。

**[Observed Tension] Cross-interface semantic equivalence 与 routing。** CLI/API 可以缩短轨迹并直接查询结构化状态，却也扩大权限、改变可观察副作用，并可能绕过用户可见 workflow；纯 GUI 保留界面语义，但更慢且更容易累积 grounding error。[[Papers/2606-MyPCBench]] 的失败分析表明，programmatic shortcut 即使取得部分目标信息，也可能遗漏用户要求的 visible artifact 或 application-side effect。

现有证据支持 hybrid action space 是重要架构方向，但不足以把其收益归因于 routing 本身：不同工作同时改变了 backbone、planner、工具库、权限和预算。接口选择器还必须区分"该接口能完成任务"与"该接口产生了语义等价、可审计且符合用户预期的状态变化"。

**最小决定性实验。** 在同一 policy、prompt、任务、权限和总时间/token budget 下，对照 GUI-only、CLI/API-only 与 hybrid routing。除 success 和 latency 外，报告 interface-selection error、user-visible state equivalence、hidden-state access、权限违规、不可逆副作用、验证成本与恢复率；hybrid 组不得获得额外未计费调用。

### 10.7 Personalization and Continual Learning

Personalization 正从一次性读取用户资料，走向长期维护偏好、历史、权限与工作流。[[Papers/2606-MyPCBench]] 将 logged-in personal context 与跨应用历史变成评测状态；[[Papers/2600-ContinualGuiAgents]] 开始研究 GUI domain 与 resolution 顺序变化下的持续适应；[[Papers/2600-UiMemSelfEvolving]] 则探索随在线训练更新的 workflow、subtask 与 failure-pattern memory。后两项在当前笔记中主要提供 problem formulation 与系统形态，尚无可用于跨论文比较的 source-verified 数字。

**[Observed Tension] Continual adaptation 与 governed persistent state。** 学习得越积极，stale preference、错误经验和越权信息就越可能进入未来决策；遗忘得越保守，又越难适应 UI 更新与用户习惯变化。[[Papers/2606-AlwaysOnAgents]] 提出的 authority、scope、mutability、provenance、recoverability 与 actionability，为这一张力提供了治理轴，但其与真实个性化 CUA 行动后果的闭环尚未建立。

Personalized CUA 不应只测当前任务准确率。评测还需要覆盖旧能力保持、偏好变更、权限撤销、删除传播、跨用户隔离、错误记忆纠正和长期存储成本；个性化收益与隐私暴露必须同时报告。

**最小决定性实验。** 构造跨 environment version、app update 与用户偏好变更的纵向任务流，对照 frozen base、episodic retrieval、parameter continual learning 与 governed memory。报告新任务适应、旧能力保持、stale-preference violation、revocation compliance、cross-user leakage、memory growth、选择性失效和恢复成本。

### 10.8 Safety, Privacy, and Human Oversight

Safety 已从 instruction screening 推进到 action-consequence prediction 与 architecture-level isolation；human oversight 也从持续盯屏，拆分为 interruption timing、plan edit、evidence presentation 与 context resumption。两条路线共享同一前提：风险必须在动作执行前预测、执行后核验，并在证据不足时允许 abstain、确认或升级给人类。

下表区分两条从原 Agenda C 迁移而来的 roadmap。它们相互依赖，但不能用"有人类在环"替代系统安全，也不能用 trust boundary 替代可用的干预界面。

| Roadmap item | 证据标签 | 已有进展 | 尚未闭合的边界 |
|:--|:--|:--|:--|
| Architecture-level safety 与 data-flow integrity | **Validated Gap** | [[Papers/2607-UCM]] 以 typed quarantine 隔离 untrusted control flow；[[Papers/2607-SeerGuard]] 在动作前预测语义后果 | trust-label error、typed-value corruption、selection hijacking、free-form untrusted content、跨应用权限与真实副作用 |
| Attention-aware human oversight | **Validated Gap** | [[Papers/2607-Sidekick]] 区分 background、resumption 与 foreground feedback；[[Papers/2607-Plover]] 将 persistent plan 变成可编辑协作对象 | 证据主要来自单 agent、受控 workflow 或专家修复上界；多 agent、多 workspace、普通用户与长期 alarm fatigue 仍缺 |

Architecture-level safety 需要把 instruction screening、least privilege、typed information flow、consequence verification 与 rollback 分层组合，并明确每层不能保证什么。Attention-aware oversight 则需要联合优化何时打断、展示什么证据、允许用户编辑哪一层计划，以及如何在修复后恢复上下文；automation bias、alarm fatigue、误报与认知负担都应成为正式指标。

**最小决定性实验。** 在能力匹配的强 agent 上联合操纵 trust boundary、interruption policy 与 plan-edit channel，测攻击成功、任务成功、隐私泄露、干预时延、误报、用户认知负担和恢复后的 context loss。安全结论必须在 agent 具备完成目标动作的条件下成立，避免把安全性建立在 agent 尚不会执行之上。

### 10.9 Efficient and On-Device CUA

效率研究已从减少 action steps，推进到压缩多轮视觉历史、KV cache 与训练 context。现有证据主要来自 GPU 上的 7B 级模型或训练管线，能够证明资源瓶颈与压缩收益，却不能直接证明真实 mobile/edge device 上的可部署性。

下表只并列各论文自身的 source-verified 设置，不据此做跨论文排名。

| 路线 | Source-verified signal | 解释边界 |
|:--|:--|:--|
| KV cache 的 spatio-temporal reweighting | [[Papers/2606-StarKV]]：UI-TARS-1.5-7B 在 40% 预算下四 benchmark 平均精度 49.94，full cache 为 49.75；ScreenSpot-Pro 的峰值显存由 37.36 GB 降至 22.97 GB（20% 预算） | 只测两个 7B 开源模型；FLOPs 不等于 wall-clock latency，且 attention redundancy 不等于 evidence freshness |
| Coordinate-aware history compression | [[Papers/2601-CompressToFocus]]：1AO→3AO 时 token 增幅约 4%，其 semi-online RL 对照为 41%；3AO 设置报告 3.5–3.8× training speedup | 长程与短程收益不均；ROI crop 可能继续保留已经过期的界面状态 |
| Uniform-budget KV compression | [[Papers/2603-STLiteKV]]：在特定长历史样本上达到 2.45× decoding acceleration，但 end-to-end 最高仅 1.40× | 该笔记为 partial verification；论文的"平均 7.3%"宣称与表格矛盾，不能采用 |

**[Observed Tension] Resource compression 与 evidential integrity。** 压缩可降低显存、token 与延迟，但 saliency、坐标或相似度启发式并不知道被保留的 observation 是否仍然反映当前 GUI state。效率优化因此需要与 provenance/freshness audit 联合设计，否则它可能更高效地保留错误证据。

**最小决定性实验。** 在真实 consumer GPU、mobile NPU 或 edge accelerator 上固定 model、quantization、policy、task set 与 verifier，对比 full context、token pruning、KV compression 和 state-aware compression。统一报告端到端 latency、峰值内存、energy、thermal throttling、任务成功、grounding、恢复率以及 stale-evidence retention；仅报 analytic FLOPs 不构成 on-device 证据。

### 10.10 Standardized and Deployment-Oriented Evaluation

CUA evaluation 已从静态终局 success，推进到 versioned environment、partial checkpoint、verifier audit、cost 与 side-effect 检查。[[Papers/2504-OnlineMind2Web]] 暴露了静态页面与不可靠 judge 带来的进步幻觉，[[Papers/2510-HAL]] 强调 cost–accuracy Pareto，[[Papers/2607-TeachStop]] 揭示 data draw 与 runtime variance，[[Papers/2606-AgentTracesToTrust]] 则明确指出跨 evidence、tool、memory 与 recovery 的 full-stack provenance evaluation 仍不成熟。

**[Validated Gap] Standardized deployment contract。** 当前 benchmark 分别覆盖 grounding、长程、recovery、privacy、personal context 或成本，但缺少能够统一描述 environment version、证据访问、预算、权限、side effect 和 human intervention 的报告协议。标准化的目标不是把所有任务压成一个总分，而是让不同系统的收益来源、适用边界和部署成本可被审计。

下表给出十条 roadmap 共享的最小评估契约。每一轴都应保留独立指标，避免一个 aggregate score 掩盖能力与风险之间的交换。

| 评估轴 | 必须报告 | 关键控制变量 |
|:--|:--|:--|
| Data | task validity、transition validity、recovery coverage、overlap | generator、data draw、policy frontier |
| Long horizon | binary success、partial checkpoints、state consistency | horizon、step budget、dynamic events |
| Grounding | belief source、freshness、conflict resolution、abstention | screenshot/DOM/AXTree/memory access |
| Verifier | precision、recall、coverage、cost、uncertainty、provenance | trajectory、actor、evidence budget |
| Recovery | awareness、recovery by depth、restore fidelity、side effect | error injection、fork state、replay policy |
| Hybrid interaction | interface usage、routing error、visible-state equivalence | GUI/CLI/API permissions and budgets |
| Personalization | adaptation、retention、revocation、deletion、leakage | user identity、version order、memory policy |
| Safety and oversight | attack success、benign utility、privacy、intervention cost | agent capability、trust boundary、UI channel |
| Efficiency | latency、memory、energy、tokens、monetary cost | hardware、quantization、context budget |
| Statistics | paired effect、confidence interval、wrong-sign probability、environment failure | crossed data draw × seed、versioned tasks |

**最小决定性实验。** 在同一批 versioned tasks 上，使用 frozen policy、相同 prompt、相同 step/token/time budget 与统一权限，交叉比较三类 verifier、三种 data draw 和多 seed；同时包含真实小样本 audit、counterfactual branches 与跨 platform/environment-version 复现。报告 held-out end-to-end success、validator error、environment failure、side effect、cost、human intervention 与 wrong-sign probability，而不能只报最佳 run。

下一阶段的决定性进展，不是再把单项 benchmark 提高几个点，而是在 frozen-policy、等预算条件下证明 state provenance、runtime、verifier、recovery 与 oversight 各自改变了真实状态转移。只有当收益能跨平台和 environment version 复现，并计入副作用、资源成本与 human cost，CUA 才能从可用 demo 进入可问责基础设施。