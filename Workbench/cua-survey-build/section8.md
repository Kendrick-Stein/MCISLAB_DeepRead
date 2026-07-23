### 8.1 Grounding Benchmarks

GUI grounding benchmark 已从静态点选扩展到高分辨率专业软件、长尾动作、功能理解、目标缺失与多证据冲突。它们隔离的是 perception-to-action interface，而不是完整任务能力；高 grounding accuracy 不能推出 long-horizon completion。

下表区分不同 benchmark 实际暴露的 grounding 失败，避免把所有定位任务压成同一个 element accuracy。

| Benchmark | 评测对象 | 指标 / Verifier | 解释边界 |
|:--|:--|:--|:--|
| ScreenSpot-Pro [[Papers/2504-ScreenSpotPro]] | 专业高分辨率桌面中的小目标定位 | offline 人工目标标注；执行 step budget 不适用 | 隔离定位能力，不测 action effect 或任务完成 |
| CUActSpot [[Papers/2605-CUActSpot]] | click、drag、draw、文本、表格、canvas 与图像区域等长尾动作 | Correct Region + Banned Region | 覆盖动作几何，但不测多步状态维护 |
| MMBench-GUI [[Papers/2507-MMBench-GUI- Hierarchical Multi-Platform Evaluation Framework for GUI Agents]] | content understanding、grounding、automation、collaboration 的层级能力 | offline 与 online 分层评测；EQA 同时考虑质量与效率 | 多层 aggregate 不能替代逐层 failure attribution |
| AutoGUI-v2 [[Papers/2604-AutoGUIv2]] | region function、element function 与 interaction-outcome prediction | VLM-human 标注的 offline functional evaluation | 预测界面变化不等于在真实环境中实现变化 |
| GUI-HalluBench [[Papers/2606-ExposingAndEvaluating]] | 相似元素误选与目标不存在时的坐标编造 | Localization Accuracy、Rejection Rate | 属于 grounding reliability probe；尚不能推出端到端安全性 |
| State-Belief Conflict Probes [[Papers/2607-GUIStateBelief]] | pixels 与 DOM / accessibility structure 冲突时的 belief provenance | 单通道成对干预与 PFG | 诊断 fusion failure，不是通用 task-success metric |

一个已 source-verified 的单工作结果说明 setting 为什么必须完整绑定：GUI-AIMA-3B 在 ScreenSpot-Pro 的 offline 标注口径下，经 training-free zoom-in 得到 61.5，而不使用 zoom-in 时为 53.8；这里没有 execution step budget，比较只适用于同一 3B 方法的 grounding 设置 [[Papers/2511-GuiAima]]。该结果支持 search-space reduction 对高分辨率定位有帮助，但不能写成所有 grounding model 的领域共识。

### 8.2 Offline Action/Trajectory

Offline action benchmark 将固定 trajectory 中的 action type、target、value 或 successor state 单独评分，适合低成本训练诊断。它们不允许 agent 探索替代路径，也不测试执行失败后的 recovery，因此 step-wise 高分与在线成功之间不存在自动对应关系。

下表回答每类离线协议保留了什么信号、又丢掉了什么闭环信息。

| 协议 / Benchmark | 主要信号 | 代表笔记 | 主要缺失 |
|:--|:--|:--|:--|
| AITW、AndroidControl、GUI-Odyssey | action type、grounding、step success 与 trajectory match | [[Papers/2601-CompressToFocus]]、[[Papers/2603-STLiteKV]] | 替代动作、环境反馈、恢复与副作用 |
| Multimodal-Mind2Web、MMInA | web/mobile trajectory 上的 action 与 memory-conditioned decision | [[Papers/2605-MemW]] | live drift、真实后端状态与运行时成本 |
| EvoGUI | temporal ordering、inverse action/value、logged successor discrimination | [[Papers/2607-EvoGUI]] | sampled distractor 不是 executable counterfactual |
| OS-Critic Bench | 给定 goal、memory、screenshot 与 candidate action 判断 step correctness | [[Papers/2606-OSOracle]] | candidate 分布受生成模型影响；offline critic accuracy 不保证 online gain |

source-verified 对照进一步显示 benchmark horizon 会改变方法结论。在 GUI-Odyssey 的 offline TM/GR/SR 口径中，CCPO-3B-3AO（Qwen2.5-VL-3B）为 90.6/88.5/80.9，论文对照的 UI-S1-7B 为 76.3/61.7/59.5；二者 backbone 不同，因此只能视作该论文内的 benchmark comparison。相同工作在 Android Control 上，CCPO-7B-3AO 的 SR 为 73.3、GR 为 79.7，而 UI-TARS-7B 分别为 72.5 与 80.5，说明短程 setting 下 success 与 grounding 指标甚至可能反向变化 [[Papers/2601-CompressToFocus]]。两组都是离线评分，execution step budget 不适用，不能与 real-device task success 裸比。

### 8.3 Web Agent

Web benchmark 的演进由 static trajectory 推向 self-hosted functional state，再推向 live website。三类设置分别控制诊断成本、可复现性与生态真实性；它们互补，而不是按时间顺序相互替代。

下表按环境状态与 verifier 组织 web benchmark，而非按 leaderboard 分数排序。

| Benchmark | Environment | Verifier | 能回答的问题 |
|:--|:--|:--|:--|
| WebArena [[Papers/2307-WebArena]] | self-hosted 多站点后端 | 数据库、API、locator 与文本规则 | agent 是否产生了正确 functional state |
| VisualWebArena [[Papers/2401-VisualWebArena]] | self-hosted visual web | functional state + visual task contract | 视觉信息是否为完成任务的必要条件 |
| WorkArena [[Papers/2403-WorkArena]] | ServiceNow enterprise sandbox | programmatic final-state checks | 知识工作与 compositional workflow 能力 |
| REAL [[Papers/2504-REAL]] | 确定性现代网站 replica | local state diff + semantic rubric | 可配置、可 reset 的现代 web workflow |
| Online-Mind2Web [[Papers/2504-OnlineMind2Web]] | live public websites | trajectory evidence + WebJudge | static/cached 成绩能否迁移到当前网站 |
| Odysseys [[Papers/2604-Odysseys]] | live long-horizon web | task rubric + execution audit | 长程状态维护、恢复与效率 |
| WebArena-Verified | verified task/verifier release | versioned state checks | 原始任务与 checker 修订后结论是否保持；代表使用见 [[Papers/2606-SkillNb]] |

原版 WebArena 上的 [[Papers/2410-AgentOccam]] 与 WebArena-Verified 上的 [[Papers/2606-SkillNb]] 不能仅凭同名 benchmark family 横向排序；release、checker、backbone、step cap 与 scaffold 都必须同时对齐。[[Papers/2504-OnlineMind2Web]] 提供了 static-to-live 失效的单工作证据，足以否定"静态高分自动代表 live 能力"，但尚不足以给所有 agent 估计统一折损率。

网站本身也可能是混淆变量。[[Papers/2607-AgentReadyWeb]] 用合成双站点探索结构化标记、语义 actionability 与 API/MCP 暴露对 agent 的影响，但该工作仍是单一电商 proof-of-concept；它更适合作为 website-side ablation 的起点，而不是现实 web 总体水平的估计。

【gap】当前 vault 覆盖薄弱：缺少同一 backbone、scaffold、step budget 与 verifier 下 static-to-live 的 source-verified paired rerun 数字，见 gaps。

### 8.4 Mobile Agent

Mobile benchmark 的核心张力是可验证性与真实生态：emulator/open-source app 允许读取 backend state，real-device 与闭源 app 更接近用户环境，却引入漂移、账号状态和 judge 不确定性。新一代任务还加入主动澄清、跨 app memory 与 GUI+MCP 编排，说明单 app 明确指令已不足以覆盖 mobile-use。

下表区分环境、任务扩展与判定证据。

| Benchmark | 能力扩展 | Verifier | 解释边界 |
|:--|:--|:--|:--|
| AndroidWorld | emulator 上的可重置长程操作 | app/emulator state evaluator | 适合作为稳定回归集；不能代表闭源商业 app |
| MobileWorld [[Papers/2512-MobileWorld]] | GUI-only、agent-user interaction、MCP-augmented 与跨 app 任务 | backend DB、ADB、本地状态与 callback | 开源替身提高可验证性，但与真实商业 app 仍有分布差异 |
| AmbiBench [[Papers/2602-AmbiBench]] | 不同 instruction clarity 下的主动澄清 | user simulator + outcome/process/interaction judges | interaction metric 依赖 simulator 与 judge calibration |
| AndroidDaily [[Papers/2605-AndroidDaily]] | real-device、闭源商业 app 与多约束任务 | visual trajectory evidence + guideline-grounded judge | 看不到 hidden backend；结果是时间敏感快照 |
| MemGUI-Bench [[Papers/2602-MemGUIBench]] | cross-temporal、cross-spatial 与 cross-session memory | snapshot emulator + memory-specific metrics | memory failure 与 perception failure 的归因仍可能耦合 |

这些 benchmark 不应汇总成单一 mobile SOTA 表。至少应分别报告 emulator/open-source/closed-source、single-app/cross-app、clarification 是否允许、MCP 是否可用、real-device failure policy、step cap、retry 与 verifier evidence access。

### 8.5 Desktop/Cross-App

Desktop benchmark 已从单应用 task completion 推进到 professional workflow、cross-app state 与受控错误注入。研究现状显示，桌面能力不能再由一个 OSWorld headline score 概括；任务依赖深度、应用切换、partial checkpoints 与 recovery protocol 都会改变结论。

下表说明各 benchmark 对桌面闭环增加了哪一层约束。

| Benchmark | 主要约束 | Verifier | 主要用途 |
|:--|:--|:--|:--|
| OSWorld 2.0 [[Papers/2606-OSWorld2]] | long-horizon、动态消息、隐式状态与跨源证据 | programmatic checkpoints 优先，必要时 rubric judge | binary completion + partial progress |
| WindowsWorld [[Papers/2604-WindowsWorld]] | professional persona、跨应用 workflow 与 infeasible task | intermediate/final checkpoint judge | 分离单应用能力与 cross-app coordination |
| OpenComputer [[Papers/2605-OpenComputer]] | 多桌面应用的可验证 software world | app-specific state verifier | functional correctness 与 verifier maintenance |
| GUI-RobustEval [[Papers/2605-GUIRobustEval]] | controlled error injection、awareness 与 recovery depth | 注错后状态与恢复判定 | 将恢复能力从普通 success rate 中解耦 |

一个 source-verified setting 展示了 step budget 的实际影响：[[Papers/2510-MGA]] 在 OSWorld 的 369-task、134 个 rule-based predicate 评测中，MGA w/ GPT-5 使用 GPT-5 planner、Qwen3-8B memory、Qwen2.5-VL-7B observer 与 UI-TARS grounder，overall 为 64.7；其 OS 子域为 87.5@50 steps，而同篇引用的 CoAct-1 为 75.0、最多使用 150 steps。该结果只能说明这组系统在论文给定 verifier 下的表现；不同预算使它不能被简化为"某架构无条件优于另一架构"。

### 8.6 Hybrid GUI/API/MCP

真实 CUA runtime 往往同时拥有 GUI、CLI、code、API 与 MCP，但多数 benchmark 仍固定单一 action surface。当前证据主要证明 hybrid interface 具有必要性，尚未充分回答 agent 应在什么状态下切换接口、切换是否遵守用户可见性与权限约束。

下表把真正要求接口协同的 benchmark 与仅提供工具环境的工作区分开。

| Benchmark | Interface contract | Verifier | 边界 |
|:--|:--|:--|:--|
| WeaveBench [[Papers/2606-WeaveBench]] | 同一任务必须交错使用 GUI 与 CLI/Code，单通道不可替代 | trajectory-aware judge + artifact checks + shortcut detection | Linux/英文任务；judge 与 runtime 成本高 |
| MobileWorld [[Papers/2512-MobileWorld]] | mobile GUI 与 MCP action 共存 | backend DB、ADB 与 callback | MCP 仅覆盖一个任务子集 |
| CHI-Bench [[Papers/2605-CHIBench]] | policy-rich professional workflow，经 MCP tools 操作多系统状态 | deterministic contract + rubric judge | 医疗行政模拟；更接近 MCP/service agent 而非纯视觉 CUA |
| SaaS-Bench [[Papers/2605-SaaSBench]] | browser-only 操作真实 SaaS | state/content checks + judge | 可作为 hybrid benchmark 的纯 GUI 控制组 |
| ToolVerse [[Papers/2607-ToolVerse]] | 大规模 mock MCP/tool environment | turn-level dictionary matching | 不含 GUI handoff，不能直接测跨接口 orchestration |

当前 vault 缺少 source-verified 的等预算实验：同一 task、同一 backbone、同一 verifier 下，比较 GUI-only、API-only、MCP-only 与 adaptive hybrid，并审计 UI bypass、permission escalation、state divergence 与切换成本。该缺口不能由 tool-use benchmark 或 browser-only benchmark 单独填补，见 gaps。

### 8.7 Long-Horizon/Professional

Long-horizon 的难度不等于 step 数增加。真正的专业任务把业务实体、跨源证据、不可逆交接、动态约束和最终 artifact 验证串成依赖链；局部高 checkpoint score 仍可能在最后一个关键状态上失败。

下表按 horizon 来源与完成证据区分代表 benchmark。

| Benchmark | Horizon 来源 | 完成证据 | 适用边界 |
|:--|:--|:--|:--|
| Odysseys [[Papers/2604-Odysseys]] | live website 上持续导航、状态追踪与恢复 | rubric + live execution audit | 真实但会随网站漂移 |
| OSWorld 2.0 [[Papers/2606-OSWorld2]] | desktop、self-hosted services、mid-task change 与 cross-source reasoning | 多 checkpoint functional state | 人工策展，环境维护成本高 |
| SaaS-Bench [[Papers/2605-SaaSBench]] | 跨 SaaS 业务实体与下游依赖 | Resolved + weighted checkpoint | browser-only，隔离了 API/CLI 能力 |
| WindowsWorld [[Papers/2604-WindowsWorld]] | professional persona 与跨应用 workflow | intermediate + final checks | 模拟环境与应用分布有偏 |
| Claw-Eval-Live [[Papers/2604-ClawEvalLive]] | 随 workflow demand 更新的任务信号 | trace、audit log、service state 与 workspace artifact | snapshot 可复现，信号源代表性仍需验证 |
| CHI-Bench [[Papers/2605-CHIBench]] | policy density、multi-role handoff 与多方交互 | deterministic state + rubric | 单一高风险专业域，不能外推所有职业 |

因此专业能力至少要同时报告 strict completion、partial checkpoint、dependency depth、cross-app/channel switches、run consistency、side effects、cost 与 human time。Step cap 提高只说明给了更多尝试机会；若 verifier、scaffold 或环境同时变化，就不能把增益归因于长程 reasoning。

### 8.8 Personalization

Personalization benchmark 需要区分四件事：读取个人历史、遵循稳定偏好、跨会话适应，以及在 authority/privacy 边界内使用这些状态。当前 benchmark 多覆盖前两项，对状态撤销、共享设备、多用户冲突和 least disclosure 的覆盖仍薄弱。

下表说明现有工作实际测到了哪一层。

| Benchmark / Protocol | 个性化状态 | 评测重点 | 缺失 |
|:--|:--|:--|:--|
| MyPCBench [[Papers/2606-MyPCBench]] | logged-in-like desktop、跨 app 历史与 persona data | task rubric、partial progress 与 trajectory efficiency | 单一 persona；privacy leakage 不是主指标 |
| PSPA-Bench [[Papers/2603-PSPA-Bench- A Personalized Benchmark for Smartphone GUI Agent]] | smartphone workflow preference 与 personalized instruction | structure-aware process evaluation | 当前 vault 笔记仅 abstract-level，不能承载强定量结论 |
| MemGUI-Bench [[Papers/2602-MemGUIBench]] | session 内外的任务记忆 | retention、recovery 与 memory proficiency | 记忆能力不等于用户偏好或身份治理 |
| AOEP-v0 [[Papers/2606-AlwaysOnAgents]] | persistent state 的 authority、scope、provenance 与 rollback obligation | obligation pass 与 negative-invariant pass 分离 | 通用 LLM-agent pilot，非 GUI end-to-end benchmark |

Personalization 不能只看"用了多少用户历史后成功率提高"。同一 benchmark 还应检查与任务无关的信息是否被读取或披露、撤销是否传播、偏好是否越过 user/task scope、错误个性化是否可回滚，以及 agent 能否解释某个动作由哪条个人状态授权。当前 vault 在多 persona、跨 session、带 permission/privacy verifier 的 source-verified end-to-end 结果上仍薄弱，见 gaps。

### 8.9 Safety and Security

Safety evaluation 已从恶意 prompt 检测扩展到 environmental injection、contextual privacy、证据误接地与已执行副作用。关键分界是"模型表达了危险意图"与"环境中真正出现了违规状态"；两者需要不同 verifier。

下表按 threat model 与可见证据组织代表工作。

| Benchmark / 工作 | Threat model | Verifier evidence | 解释边界 |
|:--|:--|:--|:--|
| WASP / EIA [[Papers/2504-WASP]]、[[Papers/2409-EIA]] | web/environmental injection 与 PII exfiltration | attack goal + trajectory/outcome checks | 攻击预算与 agent 能力共同决定 ASR |
| FocusAgent defense evaluation [[Papers/2510-FocusAgent]] | 与目标无关的 banner/popup injection | WebArena task outcome + attack success | 对 goal-aligned injection 不构成保证 |
| GUIGuardBench [[Papers/2601-GUIGuardBench]] | Android/PC disclosure 与 least disclosure | privacy item matching | 检测隐私存在不等于精确控制披露范围 |
| AgentCIBench [[Papers/2606-AgentCIBench]] | 无 adversary 的跨应用 contextual leakage | task completion 与 leakage 分开评分 | 正常使用分布仍受模拟环境限制 |
| EnvTrustBench [[Papers/2605-EnvTrustBench]] | stale/误导环境 claim 未核实即驱动动作 | case-specific false-path oracle | 通用 software/CLI agent 压力测试，非 GUI 真实发生率 |
| Vera-Bench [[Papers/2607-VeraSafetyTesting]] | 用户与工具通道攻击造成实际环境违规 | state-first、tool-second、response-last | coding/tool/MCP scope；verifier 本身仍需审计 |

source-verified 的 EnvTrustBench 在 55 个可机器判分 case、11 个压力场景、14 个 model-scaffold stack、共 3,850 次受控 run 中得到 83.3% aggregate EMR [[Papers/2605-EnvTrustBench]]。该协议没有可迁移的固定 GUI step budget，且论文明确测的是刻意注入误导证据后的 susceptibility；这个数字不能解释成现实部署中 83.3% 的普通行动会失误。

Safety benchmark 应至少分开报告 attack success、executed violation、benign utility、false positive intervention、side-effect severity 与 rollback success。把它们压成单一 safety score 会奖励过度拒绝，也会掩盖"任务完成但越权"的失败。

### 8.10 Efficiency and Cost

效率评测至少包含三层：agent inference/deployment cost、benchmark evaluation cost、以及训练或长期上下文的计算成本。accuracy-only 排名会奖励 retry、更长 reasoning 和更重 scaffold，却无法回答这些调用是否带来经济上或科学上有意义的改进。

下表给出三类成本证据及其正确读法。

| 工作 | 成本对象 | 指标 / Setting | 正确解释 |
|:--|:--|:--|:--|
| AI Agents That Matter [[Papers/2407-AgentsThatMatter]] | downstream agent 调用 | accuracy–dollar Pareto、holdout 与简单 retry baseline | 单一最高 accuracy 不能识别算法进步 |
| HAL [[Papers/2510-HAL]] | model × scaffold × benchmark | dollar、token、accuracy 与统一 harness | model 与 scaffold 必须联合报告；价格需要时间戳 |
| MFS Coverage [[Papers/2605-MFSCoverage]] | observation-reduction 方法的评测成本 | MFS coverage 对端到端 SR 的 proxy | 只解释关键元素缺失型失败，不能替代 planning/reasoning 评测 |
| A11y-Compressor [[Papers/2605-A11yCompressor]] | desktop observation token | token、success、trial protocol | 压缩率与 task success 必须分开报告 |
| ST-Lite / STaR-KV [[Papers/2603-STLiteKV]]、[[Papers/2606-StarKV]] | KV cache、显存与 decoding | cache budget、backbone、benchmark 与硬件指标 | FLOPs、显存与 wall-clock 不是同一成本 |
| CCPO [[Papers/2601-CompressToFocus]] | multi-turn RL 训练上下文 | token growth、训练加速与 offline task metrics | 精度比较必须绑定 history window 与 base model |

MFS Coverage 提供了 source-verified 的 evaluation-cost 例子：WorkArena L1 的 33 个任务上，11 种方法 × 32 个配置的端到端评测累计为 232.4 小时，而 coverage 评测为 48.2 分钟，约 290×；WebLINX test-iid 的对应累计时间为 117.0 小时与 28.5 分钟，约 246×。policy setting 为 Qwen3.5-122B-A10B 与 MiniMax-M2.5；Evidence Ledger 未核定统一 action step cap，因此这些数字只比较同一研究中的累计评测时间，不支持跨 agent 的 success 排名 [[Papers/2605-MFSCoverage]]。

agent-side 也需要同样严格的 setting card。A11y-Compressor 在 OSWorld 的 358-task、Qwen3-VL-32B、每任务两次且 best-of-2、OSWorld verifier 口径下，把输入 token 压到 linearized a11y 的约 22%，同时 success 从 0.156 到 0.207；Evidence Ledger 未给出 step cap，因此该结果不能与其他 OSWorld leaderboard 裸比 [[Papers/2605-A11yCompressor]]。STaR-KV 则在 ScreenSpot-Pro 的 offline setting、UI-TARS-1.5-7B、execution step budget 不适用的条件下，把 20% cache budget 的峰值显存从 37.36 GB 降到 22.97 GB [[Papers/2606-StarKV]]。

最低报告集应包含美元/任务、input/output token、wall-clock、agent steps/tool calls、retry、hardware、peak memory、verifier cost 与价格时间戳；结果应画在 cost–accuracy Pareto frontier 上，而不是只报最贵配置。

### 8.11 Evaluation Metrics

CUA 评测需要同时报告能力层级与 evidence setting。一个 task-success 数字混合了 perception、planning、execution、environment failure 与 verifier error，无法单独定位方法增益。

能力层级应至少覆盖：

1. grounding accuracy；
2. step/action correctness；
3. task outcome；
4. long-horizon / cross-app completion；
5. error awareness 与 recovery；
6. clarification、abstention 与 proactive restraint；
7. privacy、safety 与 side effect。

下表给出各层适合的互补指标。它回答的是"该指标能诊断什么"，不是建议将所有维度求平均。

| 层级 | 指标族 | 代表工作 | 不能单独推出什么 |
|:--|:--|:--|:--|
| Grounding | point/box accuracy、Localization Accuracy、Rejection Rate、PFG | [[Papers/2504-ScreenSpotPro]]、[[Papers/2606-ExposingAndEvaluating]]、[[Papers/2607-GUIStateBelief]] | action 生效与 task completion |
| Step / Process | action correctness、operation F1、critic Acc/F1、checkpoint completion | [[Papers/2606-OSOracle]]、[[Papers/2604-GUIDE- Interpretable GUI Agent Evaluation via Hierarchical Diagnosis]] | 合法替代轨迹与最终业务闭环 |
| Outcome | binary success、Resolved、weighted rubric、partial checkpoint | [[Papers/2307-WebArena]]、[[Papers/2605-SaaSBench]]、[[Papers/2606-OSWorld2]] | run consistency 与失败位置 |
| Reliability | Pass@k、Pass^k、paired rerun retention | [[Papers/2604-ClawEval]]、[[Papers/2606-SkillNb]] | 单次部署的风险分布，除非同时给 trial protocol |
| Recovery | awareness、recovery@depth、backtrack success、post-repair regression | [[Papers/2605-GUIRobustEval]]、[[Papers/2606-SkillNb]] | 原始 policy competence |
| Interaction | question precision、information gain、timely abstention、restraint | [[Papers/2602-AmbiBench]]、[[Papers/2606-AgenticAbstention]] | 用户满意度，除非有人类校准 |
| Safety | ASR、EMR、executed violation、side effects、benign utility | [[Papers/2510-FocusAgent]]、[[Papers/2605-EnvTrustBench]] | 真实发生率，除非 threat model 匹配部署 |
| Efficiency | cost/task、token、latency、steps、memory、Pareto position | [[Papers/2407-AgentsThatMatter]]、[[Papers/2510-HAL]] | 经济价值，除非价格和硬件可重算 |
| Verifier quality | precision、recall、coverage、abstention、human alignment、cost | [[Papers/2504-AgentRewardBench]]、[[Papers/2510-CUARewardBench]] | agent 能力；这里只测 evaluator |

每个 headline metric 必须附 setting card：environment/release、task split、step cap、retry、model checkpoint、scaffold、observation/action space、verifier version 与证据访问、live failure policy、价格时间戳和硬件。MMBench-GUI 的 EQA [[Papers/2507-MMBench-GUI- Hierarchical Multi-Platform Evaluation Framework for GUI Agents]] 是把 execution quality 与 efficiency 联合考虑的尝试，但任何 aggregate 都应保留原始分量。

### 8.12 Task Verifiers and Protocols

Verifier 的根本差异不在判定模型大小，而在证据访问能力。越接近 hidden functional state，判定越确定但覆盖越窄；越依赖截图和 rubric，适用范围越广但更易受 partial observability、prompt bias 与 hallucination 影响。

下表给出 verifier 谱系及其适用协议。

| Verifier | 证据访问 | 优点 | 上限 / 风险 | 代表工作 |
|:--|:--|:--|:--|:--|
| Programmatic state verifier | DB、文件、app state、event log | 确定、便宜、适合 RL | checker coverage 与 schema drift | [[Papers/2605-OpenComputer]]、[[Papers/2606-CUAGym]] |
| Hybrid checkpoint verifier | state checks + content checks + semantic rubric | 支持 partial credit 与开放 artifact | 权重和 judge 仍会改变排名 | [[Papers/2605-SaaSBench]]、[[Papers/2604-ClawEval]] |
| Passive visual/rubric judge | final screenshot、selected frames、trajectory | 可用于闭源环境 | 看不到 hidden backend，易被信息选择影响 | [[Papers/2605-AndroidDaily]] |
| Learned ORM/PRM/critic | trajectory 或 step representation | 可扩展到 outcome 与 process reward | precision/recall trade-off、训练分布偏差 | [[Papers/2504-AgentRewardBench]]、[[Papers/2510-CUARewardBench]]、[[Papers/2606-OSOracle]] |
| Hierarchical diagnostic judge | segment→subtask→overall | 降低长轨迹 context overload 并给出 failure location | segmentation error 会向后传播 | [[Papers/2604-GUIDE- Interpretable GUI Agent Evaluation via Hierarchical Diagnosis]] |
| Interactive verifier agent | screenshot、shell、Python、GUI 主动取证 | 可补 hidden/ambiguous evidence | 成本高、实例耦合、可能污染状态 | [[Papers/2602-VAGEN]] |
| Human audit | 完整语境与任务意图 | 适合最终仲裁与 calibration | 慢、贵、难以 scale | 应用于分层抽检和争议样本，而非默认在线 reward |

可信协议应按以下顺序构建：

1. 先定义 success contract、禁止副作用与允许的替代解；
2. 在 agent 运行期间记录不可由 agent 篡改的 trace、audit log、state snapshot 与 artifact provenance；
3. programmatic check 优先，只有语义维度再交给 rubric judge；
4. 在按任务类型、成功/失败、side effect 与环境故障分层的人类样本上校准 precision、recall、coverage、abstention 与 cost；
5. 冻结 verifier version，并用 shortcut、gold leakage、state tampering 与 judge-prompt variation 做对抗审计。

不存在 universal verifier。现实目标是带 evidence provenance、coverage、uncertainty 与 abstention 的 verifier stack，并明确哪些任务因证据不足而不可自动判定。

### 8.13 Reproducibility and Contamination

CUA benchmark 的不可复现性来自四个不同层面：任务/参考答案泄漏、verifier 或 scaffold 可被利用、环境和模型版本漂移、以及训练与运行本身的方差。只固定 random seed 不能覆盖这些来源。

下表把已观察到的威胁与所需协议对应起来。

| 威胁 | 现有证据 | 最低防线 |
|:--|:--|:--|
| Shortcut / hard-code | [[Papers/2407-AgentsThatMatter]] 讨论 benchmark-specific shortcut；[[Papers/2510-HAL]] 报告 scaffold 与日志中的 gaming case | task-level holdout、未见网站/任务模板、禁止 benchmark-specific branch |
| Gold / grader leakage | [[Papers/2510-HAL]] 报告 benchmark example 进入 scaffold 的单项泄漏；[[Papers/2606-WeaveBench]] 将读取 ground-truth artifact 与伪造 output 列为作弊模式 | grader 在运行后注入、reference 与 task config 分离、agent-visible filesystem 审计 |
| Original→Verified release | WebArena-Verified 的使用见 [[Papers/2606-SkillNb]]；OSWorld-Verified 与后继 release 的边界见 [[Papers/2606-OSWorld2]] | release ID、checker commit、task exclusions 与 migration table；原版和 Verified 不共用 leaderboard denominator |
| Static→Live drift | [[Papers/2504-OnlineMind2Web]]、[[Papers/2604-Odysseys]] | 时间戳、paired rerun、site-failure breakdown 与维护窗口 |
| Data draw / run nondeterminism | [[Papers/2607-TeachStop]] 的单工作 variance decomposition | data-draw × seed crossed design、paired task statistics、完整 run distribution |
| Partial evaluation bias | [[Papers/2607-AgentBenchmarkBudget]] 的 completed-record replay | 预注册 pairwise error、task-group coverage、unresolved rate 与 selection policy |
| Persistent-state contamination | [[Papers/2606-AlwaysOnAgents]]、[[Papers/2606-AgentTracesToTrust]] | provenance、freshness、deletion propagation、rollback trace 与 session isolation |

[[Papers/2607-TeachStop]] 的结论应表述为某一训练系统中的发现：evaluation noise 较小，而 data draw 与 run-to-run nondeterminism 主导结果；它尚不是 Android、desktop 与 live web 的普遍定律。对应的最低报告单位应从单次 headline gain 改为 task-level paired outcomes、多个独立 data draws、多个 runs、环境故障和完整分布形态。

Verified 重发不是对旧分数的简单修补，而是新的 benchmark release。论文必须标明原版/Verified、task exclusions、checker version、environment image、step budget、backbone/scaffold 与 verifier；无法对齐时只能并列报告，不能计算跨 release 的相对进步。

当前 vault 在 WebArena/OSWorld exploit、gold leakage 与 original-to-verified checker 修订的 primary audit Evidence Ledger 上仍薄弱，见 gaps。

### 8.14 Open Problems

**Observed Tension — transition diagnosis 与 executable causality。** [[Papers/2607-EvoGUI]] 能从 logged trajectory 诊断 temporal ordering 和 successor discrimination，但 sampled distractor 不能证明反事实状态不可达。下一步应在可 snapshot/restore 的环境中，从同一 state 执行多个 action，发布 action-conditioned reachable-state set 与 hidden-state metadata，使 world-model 分数真正对应可执行因果结构。

**Validated Gap — 等证据预算的 verifier 对照。** Programmatic、passive judge 与 interactive verifier 访问的证据不同，现有结果无法判断收益来自更好的推理还是更多取证。决定性实验应固定 actor、trajectory、environment snapshot 与 evidence budget，比较 precision、recall、coverage、abstention、cost、state pollution 和抗操纵能力，并由独立 human audit 仲裁 [[Papers/2504-AgentRewardBench]] [[Papers/2510-CUARewardBench]] [[Papers/2602-VAGEN]]。

**Validated Gap — adaptive hybrid routing。** WeaveBench 和 MobileWorld 说明多接口任务值得独立评测，但尚缺同一任务内可审计的 GUI/API/MCP routing contract。新 benchmark 应标注每个 state 下哪些接口合法、等价或禁止，并把 UI-visible side effect、permission boundary、channel-switch cost 与 state divergence 纳入 verifier，而不是只奖励最快路径 [[Papers/2606-WeaveBench]] [[Papers/2512-MobileWorld]]。

**Observed Tension — personalization utility 与 state governance。** 读取更多个人状态可提高任务可解性，也会扩大越权、stale preference 和跨用户泄漏面。评测应把 task utility 与 authority/scope/provenance/rollback 分开，加入撤销、共享设备、身份切换、冲突偏好和 least-disclosure 任务；否则 personalization score 会奖励不受控的数据暴露 [[Papers/2606-MyPCBench]] [[Papers/2606-AlwaysOnAgents]]。

**Validated Gap — benchmark lifecycle。** Static、live 与 Verified 各解决一部分问题，但缺少统一的 release lineage：任务为何失效、checker 如何变化、哪些分数可迁移、哪些模型可能见过任务。需要 versioned task graph、sealed test split、周期性 paired rerun、公开环境故障统计和 contamination disclosure，把 benchmark maintenance 变成协议的一部分 [[Papers/2504-OnlineMind2Web]] [[Papers/2604-ClawEvalLive]]。