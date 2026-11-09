---
title: "非侵入式 GUI Agent 调度：知识注入、任务分解、验证后重派的已有做法与证据边界"
tags: [survey, computer-use, task-planning, LLM, harness]
date_updated: "2026-11-06"
year_range: 2024-2026
papers_analyzed: 36
keywords: []
domain_map: GUI-Agent
scope: methodology-focused
---

## 核心结论

三种机制在文献里都有成型做法，但没有一种在真实 GUI 上拿到过"同预算对照下的净增益"。

- **知识注入**：静态文档整卡注入的净效应随 backbone 变号（AppCards GPT-5 +4.3pp、Grok-4-fast −0.9pp，Hard 任务 +21 对 −21）；按步、按状态对齐的选择性注入才有稳定增益（ExpActivator 轨迹内 +8.24 [6.51, 10.16]，四个 baseline 全跨零）；在线积累的知识模块在步数配平后输给 vanilla（SkillMemoryBudget 三个模型全败）。联网搜索只在"新任务"上有用（Resource2Skill 标准任务 +0.7、新任务 41.2→62.8）；在失败被诊断为"知识缺口"时触发是最有证据的用法，而 LearningFromFailure 里它是四个模块中增益最小的一个（41.67→44.44）。
- **任务分解**：同一套 Manager/Worker 层级在 GPT-4 时代 +4.62/+6.15（Agent S2），换成 GPT-5 后拆掉它反而 +9.1 且调用减半（Agent S3）；token 配平的 260 组实验平均 −0.3%，基线超过 ~45% 后回报转负（ScalingAgentSystems）；本地 Qwen3-VL-8B / 30B-A3B 作 planner、GTA-1-7B 作 grounder 的两段式，在有截图历史（H≥1）时低于单 agent 且 token 多 3–5 倍，无历史时则持平或略高（[[Papers/2607-LocalCUAScaling\|LocalCUAScaling]]）。唯一对冻结 executor 做干净对照的是 CES：训练 coordinator、不动 executor，在四个 executor 上都涨；而用 GPT-5 当 prompted planner 反而把 AMEX 从 43.69 拉到 35.80，把 UI-R1-3B 从 32.49 拉到 14.44。
- **验证后重派**：outcome verifier 本身已可用（IRA 86.9%、VAGEN 92.9%），但 trajectory judge 的主错误是 over-accept（OSReward 2/3 错误为"没做完却判完成"，16 步后 FP 0.20→0.37），而这正是让重派不会被触发的那类错误。"诊断后重派 vs 同预算盲重跑"只有 CUAMaster 一个对照（20/1 预算：31.5% → 83.7%），且测的是数据产出率不是部署成绩。回传内容的共识是"只描述失败和最早分歧步，不给解法"；续跑位置的证据是"错误近则倒回，错误远则注入提示"（AndroidFlux +8.76/−1.01 对 +3.41/+5.86）。显式恢复 agent 对弱 policy 为正、对 post-trained 强 policy 为负（ReTrace Qwen3.5-9B 39.38→44.26，EvoCUA-32B 54.88→51.55）。
- 三条线共享一个决定符号的变量：**注入 frozen GUI model 的信息粒度与时机**。整文档、整计划、整轨迹的注入都出现过负例；按当前步、当前状态选出的片段才稳定为正。
- 三条线也共享同一个缺口：**缺 budget-matched 对照**。这与 [[Topics/Harness-Component-Attribution]] 的结论一致：harness 增益集中在本来会失败的轨迹上，对本来会成功的轨迹为负。

## 问题设定

"非侵入式"在此指 GUI model 权重与推理接口不动；调度层可以是 prompt、工具、外置模型或训练过的外置模型（CES、[[Papers/2604-ActiveContextCurator]]、RAG-GUI 的 adapter 均属后者）。三个候选机制对应文献里三条既有线：

| 候选机制 | 文献对应 | 调度器需要决定的事 |
|:--|:--|:--|
| 知识注入 | web/tutorial/manual RAG、app card、skill library、experience memory | 何时检索、取多少、注入到 system prompt 还是当前步 |
| 任务分解 | Manager/Worker、DAG、subtask contract、state tracker | 谁拆、拆多细、子任务回报什么、何时重拆 |
| 验证后重派 | outcome verifier / judge、failure→patch、rollback retry | verifier 看什么、与 executor 的独立性、回传什么、从哪续跑 |

## 1. 知识注入

### 已有做法

| 方法 | 知识来源 | 时机 | 注入位置 | 同 backbone 结果 | 对照 |
|:--|:--|:--|:--|:--|:--|
| Agent S v1（[[Papers/2410-AgentS]]） | Perplexica 在线搜索 + narrative/episodic memory | web 搜索只在 Manager 规划时（任务开始、Worker FAIL 后重规划）；episodic 经验按 subtask 检索 | Manager/Worker prompt | OSWorld test_sub 65 题、GPT-4o、单项去除：去 web knowledge 26.15→16.80，w/o All 13.85 vs baseline 10.77；步数上限未写明 | 无预算配平；单次运行无方差 |
| [[Papers/2500-RetrievalAugmentedGuiAgents]] RAG-GUI | web tutorials | 按 query + 已执行动作检索 | 轻量 VLM 生成 guideline 给冻结 agent | +2.6%–13.3%；k=3 最优 | adapter 需 SFT+RSF 训练；笔记为 abstract 级 |
| GUIDE（[[Papers/2603-GUIDEWebVideo]]，ECCV 2026；与 CVPR 同名 benchmark 无关） | YouTube 教程视频实时检索 → VLM pairwise 标注 → Planning / Grounding 两类知识 | 任务级一次性（K≤2 条视频） | planning prompt + grounding prompt 双通道 | OSWorld 361 题 50 步：Seed-1.8 +7.48、Qwen3-VL-8B +5.83（baseline 为引用值）、Agent S3 +4.47；planning 通道占 86–91%，grounding-only 仅 +0.41；同检索源改注入原始轨迹 −1.94 | 无 budget-matched；除 120 题子集外无 seeds；k 消融只在 50 题子集 |
| [[Papers/2511-OnlineVideoLearning]]（Liu et al.，非 Watch & Learn） | 教程视频 → 轨迹 | 按步选单条轨迹 | in-context demo | +2.1–3.5；文本教程反而 46.8→44.0 | source-checked |
| MAGE（[[Papers/2610-MAGEManuals]]） | 文档 section 检索 | 一次性固定 plan | plan prompt | Calc 仅 RAP 14.47→25.53；PO 后模型上排名 6–10 section 退回无计划水平（14.89），随机 section 仍有 27.66（单次运行） | source-checked |
| [[Papers/2601-AppCards]] | 开发者文档 + 历史轨迹整理成每 app 一张卡 | 任务前按涉及 app | 整卡入 system prompt | GPT-5 84.5→88.8（Hard 57.9→78.9）；Gemini 2.5 Pro 约 +6；Grok-4-fast 61.2→60.3（Hard 52.6→31.6） | 同 harness 同步数；无 token 配平；curiosity 触发零消融 |
| [[Papers/2609-ExpActivator]] | 历史轨迹的步级经验 | 每步按状态对齐检索 | 当前步 context | Qwen3-VL-8B 轨迹内 +8.24 [6.51, 10.16]；四个 baseline −0.80~−0.07 全跨零；目标级检索只帮首步 | 四 backbone 一致 +8.24/+5.67/+3.74/+2.38 |
| [[Papers/2605-MMSkills]] | 公开轨迹生成的多模态 skill package | 按步 gated branch 加载 | 旁路返回 guidance | Gemini 3.1 Pro 44.08→50.11；Qwen3-VL-8B 10.78→25.40 | 全量直插因 context pollution 反而伤 |
| [[Papers/2606-LearningFromFailure]] Knowledge Support | `computer.search` + LibreOffice 手册 | 失败诊断后设计，运行时按需调用 | harness 工具 | OpenCUA-72B 41.67→44.44（四模块中最小）；Full 52.74 | 无盲重跑对照 |
| [[Papers/2606-Resource2Skill]] | 视频/repo/文章蒸馏的 skill wiki | 行动前 BM25+LM 选 5；覆盖不足时在线获取 | MCP 工具 | 4 backend×7 域 56.8 vs 45.0；在线获取标准任务 +0.7、新任务 41.2→62.8；dense 60.0 < BM25 66.0 | 作者自认缺 matched-token raw RAG 对照；非截图 GUI |
| [[Papers/2606-SkillMemoryBudget]]（对照研究） | AWM / ASI / ReasoningBank 在线积累 | 每任务 | actor prompt | 模块 10 步 vs Vanilla 15 步：Gemini 3 Flash 50.74 对 44.98/47.86/45.54，三模型 Vanilla 全胜 | 约半数"成功"资产来自失败轨迹；any-of-3 对 all-of-3 差 18.7pp |
| [[Papers/2607-KnowActGUIClaw]] | ReasoningBank 式经验 + 状态校验 skill | 行动前语义检索 | advisory context | Qwen3.5-35B 24.8→34.5（host）→37.9（+skills）；397B 40.7→43.3→46.2 | host 脚手架占大头；117 任务无显著性检验 |

### 证据边界

- 符号随 backbone 翻转。AppCards 同一张卡让 GPT-5 Hard +21pp、Grok-4-fast Hard −21pp（各 19 题，单 run）。MMSkills、KnowAct 上弱模型涨更多，Resource2Skill 上 Nano 涨最少，"弱模型受益更多"不是稳定规律。
- 加载方式与知识本身同等重要。MMSkills 全量直插、[[Papers/2511-OnlineVideoLearning]] 的文本教程基线、MAGE 低排名 section（退回无计划水平，属无增益而非有害）、[[Papers/2606-ViLoMem]] 跨域记忆（MMMU 69.90→65.14）都是负例；GUIDE 的 grounding 元素数 k 在 50 题 Seed-1.8 子集上 k=5 最高（53.81），k>5 回落但非单调（k=7 47.88、k=10/15 48.66），且全集主实验单模型默认 k=7；RAG-GUI 最优 k=3。
- 预算配平几乎全缺。有配平的唯一一份（SkillMemoryBudget）里在线模块全输；离线摊销库（Resource2Skill、SkillWeaver）被明确排除在该批评范围外。
- 自生成知识会被污染：SkillMemoryBudget 约半数 workflow 来自失败轨迹；[[Papers/2609-RSIAgent]] 的 verifier 误判 PASS 会把错规则固化进记忆。
- 联网搜索的边际价值集中在覆盖缺口：Resource2Skill 新任务 +21.6pp 对标准任务 +0.7；LearningFromFailure 里 Knowledge Support 增益最小。

### 对调度器的含义

- 不要默认"任务开始就搜一次、整段塞 instructions"。证据支持的形态是：按当前步/当前屏选小片段（k≤5）、与状态对齐、放在当前步而非 system prompt。
- 搜索触发应由失败诊断驱动（"知识缺口"类失败），而非常开。这把机制 1 变成机制 3 的一个分支。
- 必须有 vanilla + 等量步数/token 的对照臂，否则无法区分"知识"与"多给了预算"。

## 2. 任务分解

### 已有做法

| 方法 | 谁拆 | 传给 executor 什么 | 回传/重拆 | executor 冻结 | 结果 | 对照 |
|:--|:--|:--|:--|:--|:--|:--|
| [[Papers/2504-AgentS2]] | 通用 LLM Manager | 一个 subgoal → Worker → MoG grounding | subgoal 返回 SUCCESS/FAILURE 后重生成剩余计划 | 全 off-the-shelf | OSWorld 50 步 34.5；PHP 消融 +4.62/+6.15（65 题子集） | token 约 ×2 未报；Manager 只见 SUCCESS/FAILURE |
| [[Papers/2510-ScalingAgents]] Agent S3 | 不拆，flat policy 每步重规划 | — | — | GPT-5 | OSWorld 100 步：S2 48.8 → S2 去层级 57.9（+9.1，调用 −43.8%）→ S3 62.6 | 作者："hierarchical planning 反而会让 subgoal 变 stale" |
| [[Papers/2606-TrainingHighLevel]] CES | 训练的 Qwen2.5-VL-7B Coordinator（GRPO，奖励来自 executor 动作）+ Qwen3-4B State Tracker | 每步一条原子指令 + 语言状态 | 每步 | 冻结且可换 | GUI-Owl-32B GUI-Odyssey SR 39.60→56.75；去 Coordinator 48.48→33.27；GPT-5 当 prompted planner AMEX 35.80 < baseline 43.69；CES-P 把 UI-R1-3B 32.49→14.44 | 离线动作级指标；State Loss 14%→2%，但 executor 自身 perception 错误不变 |
| [[Papers/2508-CoAct1]] | Orchestrator（o3） | 子任务给 Programmer 或 GUI Operator，执行后清空记忆、摘要上报 | 按摘要 + 最新截图动态 | 闭源 off-the-shelf | OSWorld 60.76；GUI-only 50.68；Programmer-only 35.73；o4-mini/o4-mini 43.43 | 增益主要来自 coding 模态与 orchestrator 强度，不是粒度 |
| [[Papers/2606-MACU]] | Manager 建 DAG | 节点目标 + 关键上下文，并行子 agent | 加/删/改节点 | 未说明 | OSWorld +3.4、WebTailBench +25.5 | 无成本/调用数对照；无错误传播分析 |
| [[Papers/2608-LongHorizonHarness]] MEA | Manager 持结构化状态 | subtask contract（目标、验收标准、边界、相关历史），executor fresh context | 每轮从审计状态；executor 声明不更新状态 | Claude Code 原生 loop | Terminal-Bench 69.7→77.2（配平）；OSWorld 未配平 | 无角色消融；auditor 占 19–38% token；"误读 contract 会被自信地验证通过" |
| [[Papers/2607-StateAct]] | 主 agent 按程序状态 | 渲染类子目标给 GUI 子 agent | 每步重注入 checklist | 可换 | Opus 4.8 20.6→26.9 / 54.8→61.6；GUI 子 agent 只占 1.1% 步 | 去 act-on-state 51.3 比去 plan 58.7 伤更多 |
| [[Papers/2607-TSR]] | 同 backbone 外置 state updater（只标注不派发） | JSON：分解/已完成/当前/剩余 | 每步 | 固定 | MobileWorld Qwen +12.00、Kimi +9.00；AndroidWorld Qwen −3.45 | 过度分解超步数预算；误标"已完成"会传播 |
| [[Papers/2605-TeamBench]]（code） | Planner | 摘要 brief | 单轮 | off-the-shelf | Team−Solo +0.5（p=0.20）；Q1 +15.7，Q3–Q5 −6.8~−10.1 | 规格关键 token 召回 planner 0.79 → executor 0.24 |
| [[Papers/2512-ScalingAgentSystems]]（非 GUI） | 260 组架构 | — | — | — | token 配平均值 −0.3%；基线 >~45% 回报转负（β=−0.236）；独立 agent 错误放大 17.2× | PlanCraft 所有架构 −39~−70% |
| [[Papers/2607-LocalCUAScaling\|LocalCUAScaling]] | planner+grounder 两段 | plan | — | planner Qwen3-VL-8B/30B-A3B，grounder GTA-1-7B | H≥1 时低于单 agent、token 多 3–5 倍，H=0 时持平或略高；plan 与视觉状态不对齐、格式解析失败 | 并行 P∈(1, 2, 4) 只部分挽回；单次运行、图读数 |

### 证据边界

- 层级是否有用取决于 backbone 强弱，且证据方向冲突：S2 +4.62/+6.15 对 S3 +9.1；TeamBench 仅弱 Solo 分位为正；ScalingAgentSystems 基线 ~45% 以上转负；TSR 按 benchmark 变号。
- 丢失发生在下传与上报两端：TeamBench 规格召回 0.79→0.24；S2 Manager 只见 SUCCESS/FAILURE；CoAct-1 反思只见最后一张截图。MEA、CES、StateAct 用 contract / 语言状态 / checklist 补这一端，但 MEA 仍记录误读 contract 会被自信地验证通过。
- 几乎没有配平：S2 token ×2 未报；MACU 无成本对照；MEA OSWorld 是 GUI-only 对 GUI+CLI；只有 ScalingAgentSystems 配平，配平后均值为负。
- 并行分解放大错误（独立 17.2×、集中式 4.4×），GUI 方法无一测量。
- 分解常不是主因：CoAct-1 的增益来自 coding 模态与 o3；StateAct 的 GUI 子 agent 只占 1.1% 步。

### 对调度器的含义

- 对强 backbone（OSWorld 45–50% 量级以上）默认不做静态层级分解；分解只在 verifier 诊断为"任务过长/状态丢失"时按需触发，或只做 TSR 式的状态标注而不派发。
- prompted planner 会伤：CES-P 中是强 planner 配弱 executor，[[Papers/2607-LocalCUAScaling\|LocalCUAScaling]] 中是弱本地 planner 加严格格式依赖，两者机制不同；CES 的路径是训练 coordinator 而冻结 executor，这仍属"非侵入"（不动 GUI model），是目前唯一有干净对照的正例。
- 子任务下传必须带验收标准（MEA contract 形态），这与机制 3 的 completion conditions 可以是同一个对象。

## 3. 验证后重派

### 已有做法

| 方法 | verifier 看什么 | 与 executor 独立 | 回传给 executor | 续跑/重置 | 结果 | verifier 精度与边界 |
|:--|:--|:--|:--|:--|:--|:--|
| [[Papers/2607-InteractiveRewardAgent]] IRA | Proposer 从指令 + 首末截图写 completion conditions；Interactive Verifier 用系统/应用/GUI 工具逐条核 | 同一 VLM 做 propose+verify，与被判 agent 不同 | 无（RL reward） | — | RL：script 34.9 vs IRA 34.0；无 script 任务 33.5 | 86.9% acc vs DistRL 78.8；κ=0.84（LibreOffice 0.62）；GUI-only 消融 precision↑ recall↓；错误主要在 propose 阶段的条件错位；状态污染率未报 |
| [[Papers/2610-VeriCUA]] | Judge 写 3–5 条 check，只把 unresolved 交给冻结的 observe-only Probe | 独立 4B Judge + 独立 Probe | 无（GRPO reward） | Probe 续跑 | Actor Pass@4 43.93→47.14；K=0 74.09 → K=2 82.00 | OSWorld 上对 zero-shot GPT-5.4 仅 +0.12；Probe 可能改变 UI 状态，标签在 Probe 前记录 |
| [[Papers/2602-VAGEN]] | 轨迹记忆 + 工具三阶段（静态→回溯→主动探测） | Sonnet 4.5 独立 | 无，只做 Best-of-N 选择 | — | N=5 追平 baseline N=8 | OSWorld 人评 92.9 acc；弱 actor 下 judge precision 崩到 ~75% 而 VAGEN 88.5；副作用只靠 soft prompt |
| [[Papers/2607-OSReward]] | 末 5 张截图 + 每步 thought/action，无工具 | 独立 | — | — | 无下游实验 | Hard set 最佳 69.7 = 恒判 fail；"没做完判完成"≈2/3 错误；OSWorld 88% 错误为假阳；16 步后 FP 0.20→0.37 |
| [[Papers/2504-AgentRewardBench]] | 截图/AXTree + 轨迹 | 独立 | — | — | — | 无 judge precision >70%；副作用 precision 7–14% |
| [[Papers/2611-CUAMaster]] | annotator 读 verifier residual + 轨迹 + 环境 | "更强模型"；用 policy 自判只有有限增益 | 最早分歧步 ŝ + 只描述失败的反馈 F，不给解法 | 回滚到 ŝ 前快照，保留前缀 | 同 retry 预算对从头盲重跑：5/1 74.0→95.4；20/1 31.5→83.7；40/3 14.6→49.8；50/8 0.0→18.7 | 测的是数据产出率；detector 精度未报 |
| [[Papers/2604-VLAA-GUI]] | Completion Gate（任务改写为 1–3 条 UI 可观测标准）+ Model Judge | 同 backbone 低温 | reject 理由追加进轨迹；Loop Breaker 分级；Reflection Agent 只许 KEEP/SWITCH 不许推荐动作 | 当前状态续跑 | Opus 4.6 OSWorld 77.45；Sonnet 4.6 @100 去 Verifier −2.9pp；Flash @15 加 Verifier −11.3pp（有害）；Flash @50 去 Verifier 63.14→66.00；WAA Office 去 Verifier 32.6→11.6 | DONE precision 69.6→73.5，约 1/4 被接受的完成仍错；无盲重跑/配平对照 |
| [[Papers/2606-LearningFromFailure]] | 失败轨迹（由环境 reward 判定） | Claude 4.5 Sonnet 独立 | 跨任务 code patch，人工轻校验 | 重置 | OSWorld 42.3±2.6 → 48.9±1.2 | 无盲重跑对照；诊断精度未报 |
| [[Papers/2610-AndroidFlux]] | detector–verifier 两阶段 | 未说明 | rewind 或 inject | 两者直接对比 | 错误 ≤3 步前：rewind +8.76、inject −1.01；≥7 步：+3.41 / +5.86；差 +12.22 [4.1, 20.8] | detector precision 90.8 / recall 50.8；2B/4B 模型自救 0 例 |
| [[Papers/2610-ReTrace]]（Lost in Recovery） | error-step / recovery-step detector（Qwen3.6-Plus） | 恢复 agent 同 backbone | 显式恢复提示 | 续跑 | 显式比隐式平均 +17.86；端到端 Qwen3.5-9B 39.38→44.26，EvoCUA-32B 54.88→51.55，UI-TARS-1.5-7B 17.25→15.74 | post-trained 模型为负，但两组规模/家族/动作空间同时不同 |
| [[Papers/2505-BacktrackAgent]] | 规则 verifier + 训练 Judger | 分别训练的 7B | 已试动作 + 失败页面，强制换动作 | 单步回退 | Mobile3M +5.65；模拟页面仅 +0.70 | detection P 75.12 / R 43.58；8.48% 真错里只救回 2.37% |
| [[Papers/2609-EvoSkillGUI\|EvoSkill-GUI]] | 信息隔离的同 backbone critic | 同 backbone 但信息隔离 | 修订 skill 文件 | 重跑 | MobileWorld 三轮 69.5% vs pass@3 62.8%；去隔离 −8.57 | critic 人工审计 80.4% |
| Agent S3 bBoN（[[Papers/2510-ScalingAgents]]） | Behavior Narrative judge 比较 N 条轨迹 | 同 backbone | 无（选择） | — | 62.6→69.9（N=10） | judge 与 benchmark 一致率 78.4% |

### 证据边界

- Verifier 精度足够触发重派，但主错误类型不利于重派：over-accept 占 2/3（OSReward），VLAA-GUI 加了 verifier 后仍有 1/4 被接受的完成是错的，AndroidFlux / BacktrackAgent 的 recall 只有 50.8 / 43.58。被漏判"完成"的任务永远不会进入重派。
- 用环境探测的 verifier 比被动 judge 好（IRA 86.9 对 78.8，VAGEN 92.9），但探测本身会改状态（VeriCUA 在 Probe 前先记标签），IRA 未报状态污染率。
- "诊断后重派 vs 盲重跑"只有 CUAMaster 一个同预算对照，且是数据产出率；部署场景无一测过。VLAA-GUI 的 verifier 在 Flash @15 为 −11.3pp，说明弱模型紧预算下验证的步数开销可以压过收益。
- 回传内容的共识是"失败现象 + 最早分歧步，不给解法"（CUAMaster、VLAA-GUI Reflection 禁止推荐动作、[[Papers/2606-HiViG]] 错误类别+解释）；同 backbone 自评普遍偏弱或偏保守（[[Papers/2608-StepReflect]] GPT-5.2 零样本 neg 95.10 / pos 51.39；[[Papers/2602-CATTS]] 同模型仲裁推翻正确共识 35.0 对 46.9；BacktrackAgent 自救 2.37/8.48）。
- 续跑位置：错误近则倒回快照、错误远则在当前状态注入提示（AndroidFlux）；回退只在真实环境有效（BacktrackAgent 模拟页面 +0.70）。
- 显式恢复 agent 对强/post-trained policy 为负（ReTrace），与 [[Topics/Harness-Component-Attribution]] "增益集中在失败轨迹、对成功轨迹为负"一致。

### 对调度器的含义

- IRA 的 propose-then-verify 已经是机制 3 的 verifier 主体；缺的是 (a) 把 completion conditions 前置到执行前，让它同时做机制 2 的 subtask contract 与机制 3 的 checklist（VLAA-GUI Completion Gate、MEA acceptance criteria 已分别这样做）；(b) 重派时回传"哪条 condition 未满足 + 最早分歧步"，不回传整条轨迹或解法。
- 必须有盲重跑臂（同 retry 预算、不带诊断），即 [[Ideas/FailureConditionedRetry-GUI]] 的 A0/A1。没有它，CUAMaster 之外没有任何证据说明"带诊断"比"再跑一次"强。
- 重派前要选策略：倒回 vs 注入 vs 重拆 vs 补知识。这就是 [[Topics/CUA-Survey]] §6.13 的 "recovery policy selection" 缺口，也是 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] 的出发点。

## 跨机制：一个统一的设计

三个机制可以收敛到一个对象和一个路由：

1. **一个对象**：任务开始时由 proposer 写出 1–3 条 UI 可观测 completion conditions（IRA 的 propose 阶段、VLAA-GUI 的 Completion Gate）。它同时是子任务 contract（机制 2）、verifier checklist（机制 3）和重派反馈的坐标系（"第 2 条未满足，最早分歧在第 k 步"）。IRA 的错误主要来自 propose 阶段的条件错位，所以这个对象的质量是整个调度器的上限，值得单独评测。
2. **一个路由**：verifier 判 FAIL 后，诊断类型决定下一步。知识缺口 → 触发搜索并按步注入（机制 1）；状态丢失/任务过长 → 重拆或 TSR 式状态标注（机制 2）；局部误操作 → 倒回快照 + 失败描述续跑（机制 3）；错误久远 → 当前状态注入提示。每条路径都要有同预算的盲重跑对照。
3. **按 backbone 门控**：三条线的负例都出现在强 backbone 或 post-trained 模型上。调度器的默认目标是抬 floor 而不是抬 ceiling，实验结果应按 baseline 分位报告（TeamBench 分位表的做法）。

最小实验（冻结 executor，零训练）：A0 单跑 / A1 同预算盲重跑 / A2 诊断后重派（失败描述 + 分歧步，倒回） / A3 A2 + 诊断驱动的按步知识注入 / A4 A2 + 按需重拆。主指标是 A2–A4 相对 A1 的 Δ，按 baseline 分位拆开报。

## 未入库论文（digest 候选）

| arXiv | 简称 | 用途 |
|:--|:--|:--|
| 2410.08164 | Agent S v1 | 已入库 [[Papers/2410-AgentS]]（11-06）：26.15→16.80 核实，口径见 Evidence boundary |
| 2603.26266 | GUIDE（知识注入） | 已入库 [[Papers/2603-GUIDEWebVideo]]（11-06）：+4.47–7.48 核实；"k=5 最优"降级为子集结论 |
| 2511.04137 | [[Papers/2511-OnlineVideoLearning]] | 文本教程负例 46.8→44.0 |
| 2610.23012 | [[Papers/2610-MAGEManuals]] | 低排名 section 零增益 |
| [[Papers/2607-LocalCUAScaling\|LocalCUAScaling]] | 本地模型两段式分解 | 弱 planner + 格式依赖时为负，仅 H≥1 成立 |
| 2609.17653 | [[Papers/2609-EvoSkillGUI\|EvoSkill-GUI]] | 唯一带 pass@3 对照的 GUI reflect→retry（停止信号为同 backbone critic 自评；最终 SR 计哪次执行未说明） |
| 2605.28607 | Adaptive Multimodal Agents | verifier retry verdict，但 SR ~1%，信息量低 |

## Evidence boundary / 待核查

- 数字来自 Papers/ 笔记（已抽查核对 AppCards、SkillMemoryBudget、LearningFromFailure、MMSkills、RSIAgent、ExpActivator、CES、Agent S3、TSR、CUAMaster、VLAA-GUI、AndroidFlux、ReTrace、BacktrackAgent、CoAct-1、VeriCUA、VAGEN、OSReward、TeamBench、ScalingAgentSystems、StepReflect、CATTS）与 2026-11-06 的 web 抓取（标"未入库"者，未经全文核验）。
- RAG-GUI 笔记为 abstract 级，+2.6%–13.3% 的对照条件不明。
- Agent S v1 的 26.15→16.80 已全文核验（[[Papers/2410-AgentS]] Table 2）：OSWorld test_sub 65 题分层子集、GPT-4o、单项去除（narrative/episodic 仍在，而初始 memory 本身是"只带 web knowledge"探索构建的，消融未重建），所以它衡量的是推理期去掉在线搜索；每题最大步数论文未写明；单次运行无方差，OS 类仅 6 题。
- GUIDE 的 +4.47–7.48 已全文核验（[[Papers/2603-GUIDEWebVideo]] Table 1，OSWorld 361 题、50 步）；但 Qwen3-VL-8B 的 baseline 是引用 Qwen3-VL 报告的数字而非同 harness 复跑，Agent S3 无 planning-only 行，"planning 主导"只在两个单模型 agent 上成立；"k=5 最优"仅来自 App. C 50 题子集（一题 = 2pp，无 seeds），全集默认 k=7。
- "显式恢复对 post-trained 模型为负"在 ReTrace 内缺同一基座的前后对照。
- OSExpert（arXiv 2603.07978）经核为训练 agent 的探索式 skill 获取，不属非侵入式，未纳入。
