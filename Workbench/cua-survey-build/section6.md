### 6.1 Specialized GUI Grounding Models

GUI grounding 从外观模板匹配演进为 instruction-conditioned localization，再分化出高分辨率编码、跨平台数据扩展、显式解析器、注意力监督与离散动作 token 等路线。它们共同改善"目标在哪里"，但静态 grounding 增益能否稳定转化为长程任务成功仍未被充分证明。

[[Papers/0910-Sikuli]] 已确立 pixels-in、keyboard/mouse-out 的跨接口路线，但其 MSER+SIFT 模板匹配只能识别已知外观。[[Papers/2400-SeeclickHarnessingGuiGrounding]] 将语义 grounding 作为视觉 GUI agent 的独立预训练目标；[[Papers/2312-CogAgent]] 通过 dual-resolution 编码保留小文字和图标；[[Papers/2410-OSAtlas]] 则以跨 Web、Mobile、Desktop 的数据与统一 action space 扩展基础动作模型。UGround 在当前 vault 中仅通过 OS-Atlas 等工作的 comparator 记录间接覆盖，缺少可独立引用的专门笔记。

| 路线 | 代表工作 | 核心机制 | 已知边界 |
|:--|:--|:--|:--|
| 高分辨率视觉编码 | [[Papers/2312-CogAgent]] | 低分辨率主干与高分辨率 cross-module 并行 | 单图定位不自动解决 history、planning 与 recovery |
| Grounding pre-training | [[Papers/2400-SeeclickHarnessingGuiGrounding]]、[[Papers/2410-OSAtlas]] | 从 GUI metadata 构造 instruction–element–coordinate 监督 | 自动标注可能遗漏密集小元素；跨平台数据不等于跨平台执行能力 |
| Expert-dense data | [[Papers/2511-GroundCUA]] | 从真人 desktop demonstration 提取 keyframe，并做密集元素标注 | 当前笔记尚无 claim-level Evidence Ledger，本节只采纳其方法定位，不使用数值比较 |
| 轻量数据配方 | [[Papers/2601-ZonUI3B]] | 跨平台、多分辨率数据与分阶段 specialization | 证据集中在 static point grounding，未证明长程收益 |
| 可插拔 parser | [[Papers/2408-OmniParser]] | detector、OCR 与 icon caption 组成外部 perception layer | parser error 会成为新的级联错误源 |
| 离散相对动作 | [[Papers/2602-ToolTok]] | coarse-to-fine tool-token pathfinding 代替一步绝对坐标 | 多步定位增加 latency，online 长程效果未知 |
| 内生注意力监督 | [[Papers/2511-GuiAima]] | `<ANCHOR>` token 的 patch attention 直接接受 grounding 监督 | 效果依赖 backbone 原生视觉定位能力与 zoom 策略 |

GUI-AIMA 提供了当前 vault 中这一方向最完整的 claim-level 证据：3B 模型用 509k 样本达到 ScreenSpot-Pro 61.5、ScreenSpot-v2 92.1；移除 training-free zoom 后 ScreenSpot-Pro 降至 53.8，而迁移到 InternVL3.5-4B 的增益仅为 1.8 个百分点。单篇结果表明，attention supervision 可以降低额外 grounding head 的需求，但最终表现仍由 backbone 与推理期视觉缩放共同决定 [[Papers/2511-GuiAima]]。

### 6.2 Vision-Language-Action Models

CUA 与 embodied VLA 共享"视觉观察与语言目标条件化动作"的形式，但数字环境的动作包含坐标、element ID、键盘快捷键、API/CLI 调用和 terminal action，不能直接套用连续机器人控制的 VLA taxonomy。当前 vault 对 GUI-specific VLA 的完整、source-verified 覆盖薄弱，见 gaps；本节暂不使用 embodied VLA 结果替代 CUA 证据。

### 6.3 Native End-to-End CUA Models

Native CUA 把 perception、grounding、reasoning、短期记忆与 action generation 收进同一可训练模型，解决模块之间无法共同学习的问题。代价是错误归因困难：同一条错误轨迹通常无法直接区分视觉漏检、错误 belief、规划偏差或动作解码失败。

| 模型家族 | Native 化路径 | 能力扩展 | 主要边界 |
|:--|:--|:--|:--|
| UI-TARS | screenshot 与有限历史直接生成 thought/action | 统一跨平台动作与 reasoning pattern [[Papers/2501-UITARS]] | 内部状态不可审计；完整 observation history 受 context 限制 |
| UI-TARS-2 | 在 native policy 上加入 multi-turn RL、分层记忆及 GUI/SDK action | 从纯 GUI 扩展到 terminal、filesystem 与工具调用 [[Papers/2509-UITARS2]] | 已跨入 hybrid architecture；收益无法只归因于模型参数 |
| ScaleCUA | 同一 VLM 支持 grounding、direct action 与 reasoned action | 跨平台数据使模型既可独立执行，也可作为 grounder [[Papers/2509-ScaleCUA]] | 强局部 grounding 未稳定转化为 desktop/mobile 长程执行 |
| GUI-Owl-1.5 | technical report 将其描述为多规模、多平台 native agent | 覆盖 grounding、automation、tool use 与 memory [[Papers/2602-Mobile-Agent-v3.5- Multi-platform Fundamental GUI Agents]] | 当前笔记为 pending、abstract-only；架构和 benchmark 数字不进入强结论 |

UI-TARS 系列说明 native model 可以形成统一的数据飞轮；ScaleCUA 则提供反向边界：扩大 grounding 与跨平台训练数据仍可能留下明显的端到端执行缺口。现有证据因此不支持"native 化自动消除系统设计"，只支持把部分系统边界从显式模块接口迁移到训练数据、context policy 与 action schema。

### 6.4 Modular Agent Systems

模块化 CUA 将 planning、execution、grounding、memory、verification 与 tool routing 分配给可替换组件，优点是能力可组合、错误可定位。其性能上限同时受到 router 稳定性、组件接口损失、额外调用成本和 cascading error 约束。

[[Papers/2504-AgentS2]] 的 Agent S2 是代表性实例：Manager 分解 subgoal，Worker 生成 atomic action，再按任务类型路由到 visual、textual 或 structural grounding expert；Manager 在每个 subgoal 后基于新 observation 主动重规划。该设计表明 grounding 并非单一坐标问题：文字 span、视觉图标和 spreadsheet cell 分别适合 OCR、视觉 grounder 与结构化 API。

| 组件 | Agent S2 中的职责 | 解决的问题 | 新引入的风险 |
|:--|:--|:--|:--|
| Manager | subgoal decomposition 与 proactive replanning | 长程目标漂移 | Manager 判断错误会重写全部下游任务 |
| Worker | atomic action 与 expert routing | 将高层意图落实为操作 | router 行为依赖 backbone 与 prompt |
| Visual grounder | 元素描述到坐标 | 通用截图操作 | 小目标与布局变化 |
| Textual expert | 文本 span 定位 | 精细文本选择 | OCR 错误与文本边界错位 |
| Structural expert | 直接更新结构化对象 | 绕过脆弱点击路径 | API 可用性、权限与环境依赖 |

Agent S2 支持"专用模块可以优于一个模型兼任所有角色"的单工作结论，但尚不能推出模块化普遍优于 native model。现有比较通常同时改变 backbone、调用预算、工具权限和 observation access，架构效应仍未被独立识别。

### 6.5 Multi-Agent Systems

Multi-agent CUA 将单 agent 的长程串行执行拆成任务分解、并行探索与状态交接。现有两类证据并不矛盾：可分解任务可能从并行中获益，而顺序依赖强、共享状态频繁变化的任务会放大协调与验证成本。

[[Papers/2606-MACU]] 用 Manager 将任务表示为 DAG，调度 ready frontier 上的 subagent 并行执行，并在结果返回后动态修改依赖图。其关键并非 agent 数量，而是显式依赖关系、关键状态传递与重新规划；没有这些机制，下游 agent 无法从局部 observation 恢复上游已经获得但不可重新观察的信息。

[[Papers/2512-ScalingAgentSystems]] 的受控研究覆盖 general agentic 与 web 场景，结论更保守：independent 并行容易传播错误，centralized orchestration 可以形成验证瓶颈，但在顺序依赖、高单 agent 基线或固定总预算下，多 agent 可能负收益。该工作未直接覆盖桌面 GUI，因此只能作为架构边界证据，而非 GUI-specific 性能结论。

| 条件 | 预期更适合的架构 | 原因 |
|:--|:--|:--|
| 子任务独立、结果可合并 | DAG-based centralized MAS | 并行节省 wall-clock time，依赖关系可显式表达 |
| UI state 强耦合、动作顺序不可交换 | 单 agent 或串行 orchestrator | 并行分支容易基于过期 state 行动 |
| 多个可逆探索分支 | 带 verifier 的并行 search | 分支可以比较并丢弃 |
| 不可逆副作用或共享账号状态 | 集中式 action gate | 必须串行化权限与后果检查 |
| 固定总 token/tool budget | 小团队或单 agent | 多 agent 会碎片化每个执行位点的有效预算 |

### 6.6 Hybrid Model-System Architectures

Hybrid architecture 保留 native policy 的统一学习能力，同时把高风险、低效率或需要精确状态访问的操作交给外部工具。它不是 native 与 modular 的临时折中，而是把"何时依赖模型、何时依赖可执行结构"提升为 routing 问题。

| Hybrid 形态 | 代表工作 | 组合方式 | 核心瓶颈 |
|:--|:--|:--|:--|
| Native policy + GUI/SDK | [[Papers/2509-UITARS2]]、[[Papers/2508-ComputerRL]] | 同一 trajectory 混合 click、terminal、filesystem 与 API | 工具权限、路由和副作用控制 |
| Planner + specialist grounder | [[Papers/2504-AgentS2]] | 强 planner 保留任务所有权，grounder 负责落点 | planner–grounder 语义对齐 |
| One model, multiple inference modes | [[Papers/2509-ScaleCUA]] | grounding、direct action、reasoned action 共用模型 | mode selection 与共享训练冲突 |
| Native policy + semantic runtime | [[Papers/2607-Tactile]] | runtime 暴露带 affordance、provenance 和 verification cue 的动作对象 | 依赖 AX/OCR 完整性 |
| Platform-conditioned policy | [[Papers/2607-UIMOPD]] | 用 platform condition 缓解 desktop/mobile convention 污染 | 新平台仍需可靠 condition 与动作映射 |

Hybrid 系统的决定性问题是 capability ownership：grounding、state、permission 与 verification 分别由谁拥有，失败后由谁修改。若 ownership 不显式，系统虽然模块更多，却仍无法回答某一步为何执行、依据是否过期以及哪个组件应承担恢复责任。

### 6.7 Perception and Grounding

Perception 已从"选择 pixels 或 structure"演进为 observation selection、alignment、compression 与 evidence consistency 的联合问题。更多 observation channel 不必然更可靠；结构通道一旦 stale，额外细节可能成为更有说服力的错误证据 [[Papers/2607-GUIStateBelief]]。

三类基本 observation 各自服务不同目标：

| Observation | 强项 | 主要失效模式 | 适用条件 |
|:--|:--|:--|:--|
| Screenshot-only | 与人类可见状态一致、跨平台 | 小目标、OCR、密集布局、视觉歧义 | remote desktop、canvas、无结构接口 |
| DOM/AXTree | token-efficient、元素语义与 ID 明确 | stale structure、canvas 缺失、树膨胀 | 结构可用且 freshness 可检查 |
| Hybrid | 结合视觉外观与结构语义 | 通道冲突、provenance 丢失、级联错误 | runtime 能比较来源、新鲜度与一致性 |

Observation reduction 的证据否定了"越短越好"的简单目标。A11yCompressor 将输入压到 linearized AXTree 的约 22%，并在其 OSWorld 设置中把整体 success 从 0.156 提到 0.207；但三个处理阶段单独使用都不超过基线，说明收益来自联合重构而非任意剪枝 [[Papers/2605-A11yCompressor]]。AgentOccam 在 WebArena 达到 43.1%，其最终每步 observation token 却由 vanilla 的 2210.2 增至 2930.9，表明预训练分布对齐与去噪可以比缩短长度更重要 [[Papers/2410-AgentOccam]]。

模型能力还会反转最优表示。WorkArena L1 上，Claude Sonnet 4.6 从 a11y 的 52.4 提升到完整 HTML 的 67.0，而 gpt-oss-20b 从 46.4 降到 27.6；同一研究还发现 diff-based history 可把输入压到约三分之一而保持相当或更好的表现 [[Papers/2604-ReadMoreThinkMore]]。因此，"完整 HTML"与"压缩结构"都不是普适答案，选择必须条件化于 model capability、thinking budget 与任务类型。

Web reduction 的独立结果进一步强化这一边界：

- Prune4Web 将候选元素减少 25–50 倍，并在其 low-level grounding 设置中把准确率从 46.8 提到 88.28；但对 GPT-4o 的 task-level 结果没有提升 [[Papers/2511-Prune4Web]]。
- FocusAgent 剪除约一半 AXTree 后，在 WebArena 上低于完整 observation，错误分析指向被删元素承载的前序动作后果与页面状态 [[Papers/2510-FocusAgent]]。

视觉 history 的效率优化则形成正交路线。STaR-KV 在 UI-TARS 的 40% cache budget 下得到 49.94，对应 full cache 的 49.75；20% budget 将 ScreenSpot-Pro 峰值显存由 37.36 GB 降至 22.97 GB [[Papers/2606-StarKV]]。Compress-to-Focus 用 action-relevant ROI 裁剪历史截图，使 observation 数从 1 增至 3 时的 token 增幅由 semi-online RL 的 41% 降至约 4%，并在 GUI-Odyssey 的三项设置之一取得 21.4pp 提升 [[Papers/2601-CompressToFocus]]。ST-Lite 在 10–20% cache budget 下报告 2.45× decoding acceleration；该笔记整体为 partial verification，本节仅采用已逐项核验的 acceleration 与"GUI attention 跨层高稀疏"结论 [[Papers/2603-STLiteKV]]。

这些工作优化的是保留哪些 token，而不是某条 evidence 是否仍然为真。Perception 的下一阶段需要把 saliency、provenance、freshness 与 action-induced invalidation 联合建模。

### 6.8 Planning and Reasoning

Planning 从扩大 history 与生成一次性计划，发展为可复用 workflow、显式 task state 和可编辑 persistent plan。演进原因是长程执行不断产生新状态；静态 plan 即使初始正确，也会因弹窗、权限、工具反馈与部分完成而失效。

Agent S2 在每个 subgoal 后主动重规划，代表 observation-conditioned hierarchical planning [[Papers/2504-AgentS2]]。[[Papers/2409-AgentWorkflowMemory]] 与 [[Papers/2504-SkillWeaver]] 则把成功轨迹分别压缩为自然语言 workflow 与可执行 skill，使 planning 从单次生成转向跨任务复用。

SKILL.nb 将两者连接为 selective formalization：每个步骤依据执行证据选择代码或自然语言表示，gate 失败时按代码、自然语言、裸意图逐级回退。其 WebArena-Verified 单轮 success 为 53.7%，三次重跑保留 91.7% 初始成功任务；有限修复回收 72.9% 失败，修复后 regression 为 4.2%，而移除 gate 后 regression 从 3.3% 升至 18.6% [[Papers/2606-SkillNb]]。这些是单工作的 source-verified 结果，支持"可靠复用依赖 execution gate"，不构成所有 skill system 的普遍定律。

Explicit task state 同样具有条件性。[[Papers/2607-TSR]] 报告其作用会随环境与 backbone 改变方向，说明额外状态只有在 horizon 与状态密度足以抵消 context 和维护误差时才有净收益。[[Papers/2607-Plover]] 把 plan 变成 persistent、inspectable、editable artifact，使局部修复可以保留已完成进度；它证明的是专家介入下的 recoverability upper bound，而非普通用户性能。

Planning 的核心对象正在从"下一步 thought"转为可检查的状态转换契约：当前 subgoal、前置条件、预期 UI 变化、完成证据、可逆性以及失败后的替代路径。缺少这些字段时，长 CoT 只是更长的不可审计内部状态。

### 6.9 Memory and State Tracking

Memory 研究已经从"是否保存历史"转向"保存什么证据、何时失效、如何影响动作"。多项独立工作共同否定 memory 越多越好的假设，但尚未形成统一的 state schema。

整屏 visual memory 会产生方向相反的效果：它降低 cognitive 与 visual-state failure，却将 hidden-operation blindness 从 67.1 提高到 78.8、grounding error 从 27.5 提高到 36.1。AGMem 改存 action-relevant crop 与 recovery memory 后，在其 OSWorld 设置中从 18.3 提升到 27.2；WebForge 上三种配置仍均为 2.0，说明机制不具普适性 [[Papers/2606-NaiveVisualMemory]]。

| Memory 设计 | 状态表示 | 优点 | 主要张力 |
|:--|:--|:--|:--|
| Raw trajectory / screenshot history | 原始 observations 与 actions | 高保真、实现简单 | context 膨胀、无关像素干扰、stale evidence |
| Validated delta chain | 双帧验证后的 `ΔS_t` | 只保存已确认状态变化 | append-only 链仍可能累积 verifier error |
| Latent memory | 压缩成 soft token | 紧凑、可端到端训练 | belief source 不可读、难审计 |
| Workflow / skill memory | 自然语言或代码化过程 | 跨任务复用 | UI drift、权限变化与回归 |
| Context-as-action | policy 主动折叠 history/state | 将保留决策内化到模型 | 需要训练 context action；错误折叠难恢复 |

MGA 用双帧验证将 observation change 分为 Success、Failure、Uncertain，只把已验证 `ΔS_t` 写入 append-only memory。其消融中，完整配置的两项指标为 56.3/36.4，移除 memory 后降至 39.0/27.7，说明 memory 与 observer 在该模块化系统中都提供独立贡献 [[Papers/2510-MGA]]。

Mem-W 则将 working 与 experiential memory 经共享 Q-Former 压成 soft token，在 MMInA-Shop 上从 18.50 提升到 48.50，在 AndroidControl-v2 High 的 Pass@1 上从 49.30 提升到 63.07；消融显示两类 memory 互补 [[Papers/2605-MemW]]。这些结果支持 latent compression 的有效性，却同时暴露可验证性张力：policy 能利用 memory，但外部系统难以判断某次动作受哪条历史证据影响。

[[Papers/2605-MementoGUI]] 代表多模态 memory controller；[[Papers/2606-MemGUI]] 则在 abstract-only 笔记中把 context management 建模为 policy action，并维护 folded action history、folded UI state 与 recent step record。后者目前只作为新问题 formulation 纳入，不采用其性能主张。

可靠 state tracking 至少需要记录 value、source、timestamp/freshness、confidence、last validating observation、supersession 和 downstream actions。仅保存摘要而丢弃这些元数据，会把 memory 从辅助信息变成不可追责的隐藏状态。

### 6.10 Verification and Error Recovery

Verification 与 recovery 不是 planning 的附属步骤，而是独立能力链：预测动作效果、观察真实变化、识别偏差、选择补救、确认恢复结果。现有工作通常只覆盖其中一段，因此"发现错误"不能等同于"恢复成功"。

| 能力 | 代表工作 | 机制 | 证据边界 |
|:--|:--|:--|:--|
| Action-effect verification | [[Papers/2604-VeriGUI]] | 执行前预测效果，下一步核验 | 对 partial transition 与不可逆副作用覆盖不足 |
| Error awareness | [[Papers/2605-GUIRobustEval]] | 区分错误发生、被识别与被恢复 | awareness 本身不提供补救策略 |
| Safe backtracking | [[Papers/2512-WebOperator]] | 根据可逆性决定是否回溯 | checkpoint 无法恢复全部后端状态 |
| Timely abstention | [[Papers/2606-AgenticAbstention]] | 在无望或高风险时提前停止 | 最终拒绝与及时停止需分别评测 |
| Repair reproducibility | [[Papers/2607-TeachStop]] | 对局部 blocker 做受控修复 | 局部修复只有在 sole-blocker 条件下才传递到 task success |
| Real-distribution recovery | [[Papers/2606-XiaomiGUI0]] | 从真机异常态与 teacher takeover 获取监督 | 工业环境昂贵、漂移且难复现 |
| Mandatory verifier + loop breaker | [[Papers/2604-VLAA-GUI]] | 完成门、外部 judge 与固定升级策略 | 同 backbone 自审和额外调用开销限制独立性 |

MGA 展示了 verification 与 memory 的紧耦合：未经双帧验证的 state delta 不进入 memory [[Papers/2510-MGA]]。SKILL.nb 则把 verification 用于 reusable skill 的发布、回退与回归控制；移除 gate 后，修复后 regression 显著上升 [[Papers/2606-SkillNb]]。两项独立证据共同支持"验证结果应改变持久状态和后续控制流"，而不仅是生成一段 critique。

恢复策略仍缺少按 failure state 自适应选择的证据。固定重试、换模态、回退、重新规划、请求人类和接受当前状态分别适用于不同后果结构；统一 escalation ladder 会在弱模型或紧预算下把恢复开销变成新的失败源。

### 6.11 Safety and Human Control

CUA safety 已从筛查用户指令，扩展到环境内容、跨应用信息流、动作后果、运行时权限和持久记忆。Human control 也不能简化为每步 confirmation；有效监督需要决定何时 act、ask、wait、abstain，以及人类介入时应看到哪些证据。

这一问题并非从 CUA 才出现。[[Papers/9905-MixedInitiative]] 已将 act、ask、wait 建模为不确定性下的效用决策；[[Papers/9706-AutomationMisuse]] 区分 use、misuse、disuse 与 abuse，并指出低 base-rate 告警会造成 cry-wolf effect。CUA 的新增难点是视觉 observation、长程副作用、跨应用隐私和多 agent 状态交接。

| 风险面 | 代表工作 | 控制位置 | 未覆盖边界 |
|:--|:--|:--|:--|
| Environmental prompt injection | [[Papers/2504-WASP]]、[[Papers/2409-EIA]] | observation filtering 与 instruction hierarchy | goal-aligned injection |
| Contextual privacy leakage | [[Papers/2606-AgentCIBench]]、[[Papers/2601-GUIGuardBench]] | disclosure policy 与 least privilege | 精确识别应隐藏字段 |
| Consequence-level risk | [[Papers/2607-SeerGuard]] | 执行前预测动作后果 | world model 与环境漂移 |
| Trust isolation | [[Papers/2607-UCM]] | privileged planner 与 quarantined content 分离 | trust-label error 与 typed value corruption |
| Clarification / confirmation | [[Papers/2602-AmbiBench]]、[[Papers/2503-OS-Kairos- Adaptive Interaction for MLLM-Powered GUI Agents]] | ambiguity detection 与 adaptive autonomy | 频繁询问造成 interaction cost |
| Proactive restraint | [[Papers/2603-PIRABench]] | 推荐前估计 false-positive risk | restraint 与 recall 的联合校准 |
| Editable intervention | [[Papers/2607-Plover]] | 修改 persistent plan 后续跑 | 专家上界不代表普通用户 |
| Background monitoring | [[Papers/2607-Sidekick]] | ambient cue、resume summary、reasoning view | alarm fatigue、attention cost 与多 agent 扩展 |

Observation reduction 可以兼作廉价安全层。FocusAgent 在单项 WebArena-Reddit 设置中将 banner injection ASR 从 32.4% 降至 0.9%、popup ASR 从 90.4% 降至 1.0%，同时保留 task-relevant AXTree 行 [[Papers/2510-FocusAgent]]。这是单工作结果，只支持"与目标无关的注入可被相关性过滤"，不能覆盖伪装成 task-relevant content 的攻击。

General agent 的 EnvTrustBench 进一步显示，安全问题不仅来自恶意指令，也来自未经核验的 stale 或错误环境 claim。在其刻意构造的压力测试中，聚合 Environmental Misgrounding Rate 为 83.3%；该数字不是现实部署发生率，但其 scaffold 审计发现 execution authority 通常有 gate，而 provenance、freshness 与 evidence verification 缺少可强制 gate [[Papers/2605-EnvTrustBench]]。对 CUA 的直接含义是：permission confirmation 不能替代证据核验。

安全控制应形成分层链条：context admission、provenance、freshness check、verification policy、consequence prediction、least-privilege execution、post-action validation 与 human escalation。任何单层防线都只能覆盖自身威胁模型。

### 6.12 Architectural Trade-offs

架构选择不是 native、modular 或 multi-agent 的静态排名，而是围绕 state ownership、latency、可诊断性、数据闭环与安全边界的联合优化。跨论文 benchmark 分数通常同时改变 backbone、工具、预算与环境版本，因此本节只比较结构属性。

| 架构 | 学习闭环 | 可诊断性 | Latency / Cost | 状态一致性 | 跨平台性 | 适合场景 |
|:--|:--|:--|:--|:--|:--|:--|
| Native end-to-end | 强；统一参数可吸收新轨迹 | 低；错误纠缠在模型内部 | 单步调用少，但模型通常更大 | history 由隐式 context 管理 | 强，若动作空间统一 | 高频、低风险、数据充足的通用操作 |
| Modular | 组件可独立训练与替换 | 高；可定位 planner/grounder/verifier | 多次调用与接口开销 | 需要显式 state contract | 取决于 parser/tool 可用性 | 专业 workflow、可审计执行 |
| Multi-agent | 可并行生成或分工学习 | 中；需跨 agent provenance | 调用量和通信开销高 | state transfer 是首要风险 | 取决于 subagent 环境隔离 | 可分解、可并行、结果可合并任务 |
| Hybrid native + tools | 模型学习与结构化执行兼得 | 中高；tool boundary 可审计 | 依赖 routing 质量 | tool state 与视觉 state 需同步 | 较强 | GUI、API、CLI 混合 workflow |
| Semantic runtime | 模型只选择可执行对象 | 高；动作带 affordance/provenance | runtime 建设成本高 | 可在执行层核验 | 受 AX/OCR 覆盖限制 | 高风险企业与辅助技术场景 |

动作表示进一步改变架构的可移植性与可验证性：

| Action interface | 优点 | 主要失败模式 | 代表工作 |
|:--|:--|:--|:--|
| Coordinate action | 平台无关、与 screenshot 对齐 | 分辨率变化、小目标、坐标生成错位 | [[Papers/2400-SeeclickHarnessingGuiGrounding]] |
| Region / action head | 直接预测 visual patch | patch 粒度与额外 head | [[Papers/2500-GuiActorCoordinateFree]] |
| Relative tool token | 跨分辨率 coarse-to-fine 定位 | 多步 latency 与累计误差 | [[Papers/2602-ToolTok]] |
| Element-ID action | 精确、token-efficient、易验证 | 依赖 stable DOM/AXTree ID | [[Papers/2307-WebArena]] |
| Structured GUI action | click/type/scroll/drag 语义明确 | 长尾 modality 覆盖不足 | [[Papers/2605-CUActSpot]] |
| Semantic action object | target、affordance、provenance 与 verification cue 一体化 | 结构缺失时退回视觉歧义 | [[Papers/2607-Tactile]] |
| GUI + API/CLI | 绕开重复操作并直接查询状态 | 权限、路由与副作用复杂 | [[Papers/2508-ComputerRL]] |

Architecture 的最小可审计单位应是一条 state transition：使用了哪些 evidence、由哪个组件选择动作、动作预期改变什么、实际改变什么、谁验证结果、失败后谁有权修改 state。没有这条契约，增加模块或 agent 数量只会增加不可见的依赖边。

### 6.13 Open Problems

当前证据最稳定的结论不是某一架构胜出，而是局部能力、长程状态与可验证执行之间仍存在断裂。以下问题均来自已观察到的跨工作张力，不应解释为"无人研究"。

| Open problem | Evidence state | 需要回答的问题 |
|:--|:--|:--|
| Grounding-to-execution transfer | Observed tension | Specialized grounder 与大规模 grounding data 可以提高局部定位，但 [[Papers/2509-ScaleCUA]] 等结果表明长程执行仍受 planning、memory 与 verification 限制。需要固定 backbone、数据与预算，测量 grounding 增益在不同 horizon 上的传递率。 |
| Accountable state belief | Validated gap | [[Papers/2607-GUIStateBelief]] 显示视觉与结构冲突会诱发 stale-evidence following；[[Papers/2510-MGA]] 只写入 verified delta。下一步需要统一表示 source、freshness、confidence、supersession 与 downstream influence。 |
| Architecture-level causal attribution | Validated gap | Native、modular 与 hybrid 比较通常同时改变模型调用量、工具权限和 observation access。需要等 backbone、等 trajectory、等 evidence budget、等 action budget 的 factorial ablation。 |
| Adaptive observation policy | Observed tension | 完整 HTML 对强模型有益、对弱模型有害；剪枝既可能改善 grounding，也可能删除动作后果。需要让 agent 按 task、model capability、risk 与 freshness 动态选择 pixels、structure 和 history。 |
| Verifiable memory lifecycle | Observed tension | Raw visual memory 会干扰 grounding，latent memory 又牺牲 provenance。Memory item 应支持 write-time source attribution、失效传播、选择性删除、回滚与对下游 action 的 influence tracking [[Papers/2606-AgentTracesToTrust]]。 |
| Recovery policy selection | Validated gap | 现有系统多用固定重试、回退或升级规则。需要在相同 detector、executor 与 verifier 下比较 continue、retry、change modality、backtrack、replan、ask human 和 abort，并显式纳入可逆性、成本与副作用。 |
| Multi-agent state isolation | Observed tension | MACU 展示 DAG 协作的潜力，受控 MAS 研究则显示无协调并行会传播错误。需要 GUI-specific、等总预算实验，区分任务分解、同任务多副本探索和异构 specialist 协作 [[Papers/2606-MACU]]、[[Papers/2512-ScalingAgentSystems]]。 |
| Consequence-aware safety | Validated gap | Instruction screening 无法覆盖良性指令触发的危险动作。Runtime 需要在执行前预测后果、执行时限制权限、执行后核验状态，并保留 parameter-level provenance。 |
| Human attention as a budget | Validated gap | Confirmation、告警、后台监控与 context resumption 都占用认知资源。未来评测应联合报告 task success、intervention timing、false alarm、恢复时间、用户遗漏与 automation bias，而非只统计询问次数。 |

这些问题指向同一架构原则：Computer-Use Agent 的核心不只是生成下一步动作，而是维护一份可追溯、可修改、可验证的执行状态。模型能力决定候选动作质量，系统架构决定错误是否被发现、隔离和恢复。