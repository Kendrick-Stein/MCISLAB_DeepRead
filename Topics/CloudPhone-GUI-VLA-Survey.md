---
title: 面向云手机复杂任务的高效可靠 GUI VLA 模型技术报告
tags: [survey, gui-agent, VLA, cloud-phone, reliability, efficient-inference]
date_updated: "2026-07-01"
scope: "任务书技术诉求对齐版"
evidence: "本地 notebook 论文笔记 + 远程论文/代码检索"
keywords: [cloud phone, mobile gui, android agent, gui vla]
domain_map: GUI-Agent
---

# 面向云手机复杂任务的高效可靠 GUI VLA 模型技术报告

## 0. 结论

任务书的三项诉求分别对应三条已有研究线索：

1. **高精度低时延**：不能只靠更大的 VLA。公开结果显示 native GUI VLA、online RL、history/token 压缩、API-GUI/工具化动作空间都能提升能力或效率；但没有文献直接证明“中文云手机复杂任务 >95% 且高频步 <800ms”。因此可行路径是先把高频常规动作做成 fast path，再把复杂推理、低置信和高风险动作交给 slow path。
2. **模糊指令澄清**：已有 OS-Kairos 和 Agent-Initiated Interaction 证明“何时不应继续自动执行、何时该问用户”是 GUI agent 的独立能力。云手机任务中应把澄清做成 slot/risk policy，而不是让模型自由追问。
3. **OOD/可信执行**：GEM、VeriSafe、VeriGUI、DynamicGUI 分别支撑 OOD 检测、动作前验证、动作后效果验证、动态界面处理。高风险/未知场景的人类介入指标必须用 router + guard + verifier 组合来做，单一模型置信度不够。

任务书给出的 153 例评测中，当前 best baseline 是 Qwen3-VL-235B-A22B：约 `115/153 = 75.16%`。要超过 95%，至少需要 `146/153` 成功，即还要多成功 31 例。这个缺口远大于普通 prompt 优化能稳定覆盖的范围，应优先做 failure taxonomy、可验证回放、OOD/risk gate 和高频动作 fast path。

## 1. 任务书指标拆解

| 目标 | 指标含义 | 直接工程约束 |
|---|---|---|
| 任务执行成功率 >95% | task-level 成功，不是单步 action accuracy | 必须减少长程累积错误；每步错一次都会污染后续状态 |
| 高频常规交互单步 <800ms，且占比 >80% | 大多数 step 不能调用 30B/235B 或每步 planner | 需要 fast executor、cache、短 action schema、历史/token 压缩 |
| 复杂推理规划输出 <180 tokens | slow path 也不能输出长 CoT/SOP | planner 应输出短 plan card/skill card |
| 模糊指令意图补全率 >95% | 缺规格、地址、时间、配置等关键 slot 时能问对问题 | 需要 GUI-state-aware slot policy |
| 高风险/未知人工介入触发准确率 >95%，误报 <5% | 既要拦住危险动作，又不能频繁打断 | 需要 OOD、risk、uncertainty、action-effect verifier 分层建模 |

用户给出的模型结果显示两个信号：

| 模型 | 指定场景 | 泛化场景 | 估算总成功 |
|---|---:|---:|---:|
| Qwen2.5-VL-7B | 11/54 | 31/99 | 42/153 = 27.45% |
| UI-TARS-1.5-7B | 31/54 | 65/99 | 96/153 = 62.75% |
| Qwen3-VL-8B | 34/54 | 72/99 | 106/153 = 69.28% |
| Qwen3-VL-30B-A3B | 29/54 | 70/99 | 99/153 = 64.71% |
| Qwen3-VL-235B-A22B | 40/54 | 75/99 | 115/153 = 75.16% |

判断边界：这里的“估算总成功”来自题目中百分比换算，真实总分应以华为原始 case-level 记录为准。

## 2. 历史方法与可引用证据

| 方法线 | 代表论文/代码 | 支撑点 | 对任务书的启发 |
|---|---|---|---|
| End-to-End Native GUI VLA | UI-TARS、UI-TARS-2、AutoGLM | UI-TARS 用截图输入和统一 action modeling 做 GUI agent；UI-TARS-2 用 data flywheel 和 multi-turn RL 提升 AndroidWorld/OSWorld；AutoGLM 使用 planning-grounding 中间接口 | VLA executor 必须保留，但不应独自承担规划、风险、澄清 |
| Planner + Executor | AutoGLM、UI-TARS 系列 | 规划和 grounding 解耦有利于复杂任务，但每步 planner 成本高 | planner 应按需触发，输出短 plan card，而不是每步 SOP |
| Online RL / 数据飞轮 | UI-R1、MobileRL、DART-GUI、ComputerRL、MobileGym | UI-R1 用 rule-based action reward + GRPO；MobileRL 在 mobile GUI 上做 ADAGRPO；DART-GUI 提高 rollout/training 吞吐；MobileGym 提供可验证 mobile simulator | >95% 更可能依赖可验证环境 + replay/RL，而不是只做离线 SFT |
| 高效推理/历史压缩 | GUI-KV、HiconAgent、MMBench-GUI | GUI-KV 利用 GUI 时空冗余压缩 KV cache；HiconAgent 关注历史上下文压缩；MMBench-GUI 把效率作为 GUI agent 评测维度 | 对应 <800ms 和历史多截图成本问题 |
| 动态澄清/人机协作 | OS-Kairos、Agent-Initiated Interaction | OS-Kairos 用 step confidence 决定自动执行或人工介入；Agent-Initiated Interaction 研究 phone UI automation 中何时主动问用户 | 对应模糊指令下的澄清与意图补全 |
| OOD/可信执行 | GEM、VeriSafe、VeriGUI、DynamicGUI | GEM 做 GUI agent OOD detection；VeriSafe 做动作前形式化验证；VeriGUI 做动作失败检测与恢复；DynamicGUI 用视频/动态帧处理动态页面 | 对应高风险/未知场景下的接管、二次验证和恢复 |

## 3. 技术诉求一：高精度与低时延 GUI VLA

### 3.1 可被文献支撑的判断

- **单模型扩参不足以解释能力差异**：题目中 Qwen3-VL-30B-A3B 低于 Qwen3-VL-8B，说明参数量不是唯一瓶颈；任务数据、grounding、历史状态和异常恢复同样关键。
- **GUI VLA 需要 native action 训练**：UI-TARS 证明 screenshots-only GUI agent 可通过统一 action modeling、GUI grounding、System-2 reasoning 和 online traces 获得较强 GUI 操作能力。
- **在线 RL 和可验证 reward 是主要增益来源之一**：UI-R1、MobileRL、UI-TARS-2、DART-GUI 都把多轮交互/RL/数据飞轮作为提升 GUI agent 的核心机制。
- **长上下文和多截图推理有明确效率问题**：GUI-KV 明确指出多张高分辨率 GUI 截图会让推理变慢、成本变高、显存受限，并用 plug-and-play KV compression 降低 FLOPs。
- **效率必须成为评测指标**：MMBench-GUI 提出 EQA 等效率指标，指出当前 GUI agent 往往存在冗余步骤和低效探索。

### 3.2 可行技术路径

| 路径 | 做法 | 证据来源 | 需要自验证的点 |
|---|---|---|---|
| Fast executor | 用 3B-8B/7B 级 VLA 或 action head 处理点击、输入、滚动、返回、关闭弹窗等高频动作 | UI-TARS-1.5-7B 代码/模型，UI-R1 小模型强化，MobileRL-9B | 是否能在华为云手机真实视频流下达到 p95 <800ms |
| Short action schema | 输出 `tap/swipe/type/back/wait/ask_user/handoff/finish`，默认不输出长 reasoning | UI-TARS action parser、AutoGLM intermediate interface | schema 是否覆盖京东/淘宝/美团/携程/高德核心流程 |
| Slow planner on demand | 只在任务入口、页面大跳转、低置信、缺 slot、高风险动作前调用大模型 | AutoGLM、OS-Kairos、VeriSafe | slow-call ratio 是否能压到 <20% |
| GUI history/token compression | 最近帧 + action summary + 关键 crop；引入 KV/cache 压缩 | GUI-KV、HiconAgent | 多截图压缩是否损害小控件定位 |
| Page/action cache | 对稳定页面和重复流程复用 action/plan | MMBench-GUI 对效率问题的诊断；AgenticCache 类思路仅作间接参考 | 动态页面下误命中风险 |
| API-GUI/platform signal | 若权限允许，引入 ADB、accessibility tree、包名、页面稳定性、视频质量、事件回放 | ComputerRL 的 API-GUI；MobileGym 的状态/验证器 | 云手机平台能暴露哪些不泄露答案的 runtime facts |

### 3.3 先做的实验

1. **复跑 153 例并记录 trace**：截图/视频帧、action、模型输出、延迟、token、APP 状态、失败点。
2. **做 step-level failure taxonomy**：perception、grounding、planning、history、missing_slot、dynamic_popup、risk、false_finish、environment。
3. **建立 fast-path 评估**：只统计低风险高频动作的 action accuracy、p50/p95 latency、被 verifier 截获的错误率。
4. **做 fast/slow ablation**：large-only、fast-only、fast+router、fast+router+planner、fast+router+planner+verifier。

## 4. 技术诉求二：模糊指令动态澄清与意图补全

### 4.1 可被文献支撑的判断

- **“继续执行还是询问/接管”是 GUI agent 的独立能力**：OS-Kairos 针对 over-execution 问题，让 agent 每步估计 confidence，并决定自动执行或寻求人类介入。
- **Phone UI automation 中确实存在主动询问需求**：Agent-Initiated Interaction 专门研究 agent 在手机 UI 任务中何时需要用户交互、如何生成消息。
- **澄清必须结合 GUI 状态**：同样是“买手机”，如果页面只有一个默认规格且低风险，可以继续；如果有多个存储规格、价格差异、配送地址或支付确认，就应澄清或二次确认。

### 4.2 可行技术路径

| 模块 | 做法 | 证据来源 |
|---|---|---|
| Slot schema | 为核心 APP/场景定义关键 slot：规格、数量、价格上限、地址、时间、路线偏好、房型、人数等 | Agent-Initiated Interaction 的 problem formulation；OSWorld 2.0 的 proactive/conflict/implicit-state 类任务 |
| Clarification policy | 输出 `continue/use_default/ask_user/confirm/handoff`，而不是自由问答 | OS-Kairos 的 confidence-driven interaction |
| GUI-state grounding | 澄清问题必须引用页面上可见候选项，如“256GB / 512GB” | phone UI interaction 论文方向 + UI-TARS grounding |
| 用户回答后的继续执行 | 把用户回答写回 plan card/slot state，再交给 fast executor | AutoGLM intermediate interface；UI-TARS action execution |

### 4.3 建议指标

| 指标 | 定义 |
|---|---|
| Should-ask recall | 缺关键参数或高风险偏好时，系统是否发起澄清 |
| Over-ask rate | 页面可安全自动推进时，是否过度询问 |
| Clarification resolution rate | 用户回答后是否能正确继续执行 |
| Task success delta | 加入澄清后对最终 task success 的净提升 |

## 5. 技术诉求三：OOD、不确定性感知与可信执行

### 5.1 可被文献支撑的判断

- **OOD 不等于普通低置信**：GEM 把 GUI agent 的 OOD 指令定义为超出环境约束或能力边界，并用 embedding distance/Gaussian mixture 建模。
- **动作前验证可降低越权执行**：VeriSafe 将自然语言意图转成可验证规范，并在执行前做 action verification。
- **动作后验证对真实 GUI 很重要**：VeriGUI 指出真实 GUI 存在延迟、渲染、系统中断等导致 action failure 的问题，需要检测失败和恢复。
- **动态界面不能只依赖单张截图**：DynamicGUI 指出单步截图会造成 partially observable 问题，使用屏幕录制视频和关键帧选择处理动态 GUI。

### 5.2 风险类型与处理

| 风险类型 | 例子 | 处理 |
|---|---|---|
| 感知 OOD | 视频压缩、模糊、遮挡、低帧率、动画中间态 | 降级到 slow vision、等待稳定帧、请求无损关键帧 |
| 界面 OOD | 新版本 UI、登录过期、系统权限弹窗、广告弹窗 | ask_slow 或 handoff；记录 OOD 样本 |
| 任务 OOD | 指令缺关键参数、目标与当前页面冲突 | ask_user 或重新规划 |
| 高风险动作 | 支付、下单、授权、删除、发送消息、提交隐私 | pre-action guard + 二次确认或人工接管 |
| 状态转移异常 | 点击后无变化、跳错页、重复点击、误判完成 | post-action verifier + retry/back/recovery |

### 5.3 可行技术路径

| 模块 | 做法 | 证据来源 | 验证目标 |
|---|---|---|---|
| OOD detector | GEM-like embedding distance + 页面/任务分布特征 | GEM 论文和开源仓库 | 未知/长尾场景 recall >95% |
| Risk ontology | 标注支付、删除、授权、发送、提交等动作类型 | VeriSafe/AgentTrust 类 safety framing | 高风险 false negative 优先降到最低 |
| Pre-action guard | 动作执行前检查是否违反用户目标、slot、风险规则 | VeriSafe | 高风险动作前必须可解释 |
| Post-action verifier | 检查点击/输入后的页面变化是否符合预期 | VeriGUI、MobileGym verifier | 减少重复错点和 false finish |
| Human handoff router | 输出 `allow_fast/ask_slow/ask_user/handoff/block` | OS-Kairos、GEM | 高风险/未知触发准确率 >95%，正常误报 <5% |

## 6. 开源代码与可复用技术方案

| 项目 | 链接 | 可复用部分 | 与任务书关系 |
|---|---|---|---|
| UI-TARS | [GitHub](https://github.com/bytedance/UI-TARS) | action parser、prompt templates、mobile/desktop use、UI-TARS-1.5-7B、UI-TARS-desktop | 作为 native GUI VLA baseline 和 action schema 参考 |
| MobileGym | [GitHub](https://github.com/Purewhiter/mobilegym) | browser-hosted mobile env、state verifier、runner、RL code、416 task templates | 参考可验证 mobile 训练环境和 sim-to-real 评估 |
| OS-Kairos | [GitHub](https://github.com/Wuzheng02/OS-Kairos) | Android ADB、人机协同模式、single-step/trajectory/test modes | 参考澄清/接管原型 |
| GEM | [GitHub](https://github.com/Wuzheng02/GEM-OODforGUIagents) | GUI agent OOD detection 代码、数据、SFT 目录 | 参考 OOD detector |
| ComputerRL | [GitHub](https://github.com/THUDM/ComputerRL) | API-GUI action paradigm、异步 RL、OfficeWorld | 参考平台侧 API/GUI 混合动作，但其主要是 desktop |
| MobileRL | [GitHub](https://github.com/THUDM/MobileRL) | AndroidWorld/AndroidLab Docker eval、mobile RL 方法 | 参考 mobile online RL 和评测 |
| DART-GUI | [GitHub](https://github.com/computer-use-agents/dart-gui) | 异步 rollout/data/training 架构 | 参考高吞吐 RL 基础设施，需迁移到 mobile/cloud phone |

## 7. 建议验证路线

### Phase 0：先把现有评测变成可诊断数据集

- 复跑 153 例，保存完整 trace。
- 每例标注失败类别、关键 checkpoint、是否需要澄清、是否高风险、是否 OOD。
- 得到每 APP failure profile，而不是只看总成功率。

### Phase 1：高频动作 fast path

- 基于 UI-TARS/Qwen baseline 生成 teacher action，人工修正失败例。
- 训练或蒸馏 fast executor/action head。
- 加短 action schema、页面稳定判断、历史压缩和 cache。
- 验证：fast-path 占比、p95 latency、fast-path 错误率、被 verifier 截获率。

### Phase 2：澄清与 OOD/risk router

- 做核心 APP slot schema 和高风险 action ontology。
- 接入 GEM-like OOD score、模型不确定性、视觉质量、页面稳定性、动作风险。
- 输出 allow_fast / ask_slow / ask_user / handoff / block。
- 验证：should-ask recall、over-ask rate、高风险/未知 recall、正常误报率。

### Phase 3：可验证环境与 RL

- 参考 MobileGym，把核心流程做成可 reset/fork/verify 的云手机或仿真环境。
- 用 programmatic checkpoint/reward 训练 fast executor、router、recovery policy。
- 参考 DART-GUI/ComputerRL 做并行 rollout 和数据筛选。
- 验证：相对 baseline 的 task success delta、sim-to-real retained gain、异常恢复率。

### Phase 4：真实云手机/物理手机验收

- 冻结测试集和 held-out APP/版本。
- 分桶报告：指定场景、泛化场景、模糊指令、OOD、高风险、视频压缩、网络延迟、系统弹窗。
- 只有当 held-out 上也稳定，才能认为 >95% 不是 153 例过拟合。

## 8. 不建议优先投入的方向

| 方向 | 原因 |
|---|---|
| 每步调用大 planner 生成完整 SOP | 与 <800ms、高频步占比 >80%、规划输出 <180 tokens 冲突 |
| 只做 prompt engineering | 当前 best 到 >95% 还差至少 31/153，缺口过大 |
| 只用单一 confidence 分数接管 | OOD、动作风险、页面稳定性、用户偏好缺失是不同问题 |
| 直接把 AutoFocus/GUI-Eyes 类多轮感知放进默认路径 | 可能提升 hard grounding，但多次 VLM 调用不适合作为高频默认路径 |
| 没有 verifier 就做 RL | reward 不可靠会放大错误策略；MobileGym/UI-R1/MobileRL 都强调可验证信号或 rule-based reward |

## 9. 证据边界

**已知**：

- 任务书给出的当前 best baseline 约为 75.16%，离 >95% 至少差 31 个成功 case。
- 本地 notebook 已有 UI-TARS、OS-Kairos、MobileGym、ComputerRL、UI-R1、MobileRL、DART-GUI、GEM、VeriSafe、DynamicGUI 等相关论文笔记。
- 远程检索确认多个项目有开源代码，可直接支持 baseline、OOD、human-in-loop、mobile environment、RL infra 的原型尝试。

**推测，但有文献间接支撑**：

- 云手机如果能暴露页面稳定性、视频质量、输入事件、APP 包名/版本、权限弹窗、action effect 等 runtime facts，会比 screenshot-only agent 更容易做可靠闭环。
- >95% 更可能来自 fast executor + router + clarification + verifier + RL flywheel 的组合，而不是单模型扩参。

**不知道，需要华为数据验证**：

- 153 例的逐例失败类型、真实 latency/token 分布、各 APP 的账号/网络/后端状态。
- 云手机平台能否合法稳定地暴露 ADB/accessibility tree、无损帧、页面栈、包版本等信号。
- 高风险/未知场景的标注规范，以及“人工介入触发准确率”的正负样本定义。

## References

本报告只保留与三项技术诉求直接相关的来源。`[[...]]` 是本地 notebook 论文笔记，URL 是远程核对的一手论文或代码。

- [[2500-UI-TARS- Pioneering Automated GUI Interaction with Native Agents]] / [arXiv 2501.12326](https://arxiv.org/abs/2501.12326) / [GitHub](https://github.com/bytedance/UI-TARS)
- UI-TARS-2 / [arXiv 2509.02544](https://arxiv.org/abs/2509.02544)
- AutoGLM / [arXiv 2411.00820](https://arxiv.org/abs/2411.00820)
- [[2500-UiR1EnhancingEfficient]] / [arXiv 2503.21620](https://arxiv.org/abs/2503.21620)
- [[2500-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]] / [arXiv 2509.18119](https://arxiv.org/abs/2509.18119) / [GitHub](https://github.com/THUDM/MobileRL)
- [[2509-DARTGUI]] / [arXiv 2509.23866](https://arxiv.org/abs/2509.23866) / [GitHub](https://github.com/computer-use-agents/dart-gui)
- [[2508-ComputerRL]] / [arXiv 2508.14040](https://arxiv.org/abs/2508.14040) / [GitHub](https://github.com/THUDM/ComputerRL)
- [[2605-MobileGym]] / [arXiv 2605.26114](https://arxiv.org/abs/2605.26114) / [GitHub](https://github.com/Purewhiter/mobilegym)
- [[2500-GuiKvEfficientGui]] / [arXiv 2510.00536](https://arxiv.org/abs/2510.00536)
- [[2606-HiconAgent]] / [CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Zhou_HiconAgent_History_Context-aware_Policy_Optimization_for_GUI_Agents_CVPR_2026_paper.html)
- [[2507-MMBench-GUI- Hierarchical Multi-Platform Evaluation Framework for GUI Agents]] / [arXiv 2507.19478](https://arxiv.org/abs/2507.19478)
- [[2503-OS-Kairos- Adaptive Interaction for MLLM-Powered GUI Agents]] / [arXiv 2503.16465](https://arxiv.org/abs/2503.16465) / [GitHub](https://github.com/Wuzheng02/OS-Kairos)
- [[2500-AgentInitiatedInteractionPhone]] / [arXiv 2503.19537](https://arxiv.org/abs/2503.19537)
- [[2505-GEM- Gaussian Embedding Modeling for Out-of-Distribution Detection in GUI Agents]] / [arXiv 2505.12842](https://arxiv.org/abs/2505.12842) / [GitHub](https://github.com/Wuzheng02/GEM-OODforGUIagents)
- [[2500-VerisafeAgentSafeguardingMobile]] / [arXiv 2503.18492](https://arxiv.org/abs/2503.18492)
- VeriGUI / [arXiv 2604.05477](https://arxiv.org/abs/2604.05477)
- [[2604-DynamicGUI]] / [arXiv 2604.25380](https://arxiv.org/abs/2604.25380)

## 调研日志

- **原始调研**: 2026-06-30，基于本地 vault 论文笔记和远程论文/代码检索生成长版报告。
- **简化修订**: 2026-07-01，按用户反馈重写为“技术诉求 -> 文献/代码证据 -> 可验证路径”的版本，删除无法直接被文献或代码支撑的展开。
