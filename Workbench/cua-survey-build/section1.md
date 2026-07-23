### 1.1 Background and Motivation

Computer-Use Agents（CUA）将自然语言目标转化为对现有数字界面的连续操作，使 agent 能够在缺少专用 API 的网页、移动应用、桌面软件与遗留系统中完成任务。相较于固定 selector 与脚本驱动的 GUI automation，CUA 面向动态界面、开放指令和跨应用工作流，其研究对象不是孤立的点击预测，而是部分可观测环境中的长程状态控制。

现有综述共享两组主要组织轴：平台轴覆盖 Web、Mobile、Desktop 与跨平台系统，组件轴覆盖 observation、grounding、planning、memory、action、execution feedback 与 verifier。Microsoft 的综述以平台 × pipeline 的 cookbook 组织领域，OS Agents 进一步区分环境、观察空间、动作空间以及 understanding、planning、grounding 能力，technology-agnostic 的 ACU survey 则补入 domain、interaction 与 learning 视角 [[Papers/2411-GUIAgentSurvey]] [[Papers/2508-OSAgentsSurvey]] [[Papers/2501-ACUSurvey]]。本综述沿用这一公共坐标，研究范围包括 GUI-only 与 GUI+API/CLI hybrid agent，但排除不直接研究 UI observation、GUI action、computer-use environment、GUI verifier 或部署期监督的通用 Agent、VLM 与 World Model 工作。

本综述在公共坐标之上提出一个作者综合论断：CUA 的优化单元正在从屏幕识别与动作生成，扩展为来源可追溯、结果可核验、失败可恢复的状态转移；environment、runtime、verifier 与 human oversight 因而成为与模型同等重要的系统层。该论断不是已知领域共识，其主要直接证据来自 2026 年的新近工作，尚缺跨系统因果验证与独立复现。

### 1.2 Research Significance

CUA 的研究意义不由单一 benchmark 分数决定，而来自通用数字接口、序列决策、系统基础设施与人类监督四个层面的耦合。局部 grounding、长程执行和真实部署采用不同证据设置，任何一层的改进都不能自动外推为完整 computer-use 能力。

| 层面 | 核心价值 | 主要研究约束 |
|:--|:--|:--|
| 通用接口 | GUI 是大量 Web、Mobile、Desktop 与遗留软件共同暴露的人机接口 | UI drift、平台碎片化、无稳定 selector 或 API |
| 序列决策 | 将视觉理解、语言目标、规划与动作执行放入同一闭环 | partial observability、误差累积、长程 credit assignment |
| 系统基础设施 | environment、reset、parallel rollout、runtime 与 verifier 决定训练和评测上限 | 状态污染、不可复现、验证器偏差与高 rollout 成本 |
| 人机协作 | agent 会接触账号、文件、通信和不可逆操作 | privacy、prompt injection、权限边界、澄清与人工接管 |

OSWorld 同时展示了能力水位的快速上升与横向比较的脆弱性。下表只列当前 vault 中能够定位到原文表格或 claim verification 的锚点；它们不是同一受控实验，不能被解释为单一模型能力的纯时间曲线。

| 时间 | 系统与 OSWorld 设置 | Success Rate | 证据边界 |
|:--|:--|--:|:--|
| 2024-10 | GPT-4o + OS-Atlas-Base-7B | 14.63% | 只替换 grounding 模块；同表 human baseline 为 72.36%，直接说明 grounding 并非全部瓶颈 [[Papers/2410-OSAtlas]] |
| 2025-08 | OpenCUA-72B，OSWorld-Verified，100 steps | 45.0% | 三次运行并由 OSWorld 团队独立评测；属于当时开源系统锚点 [[Papers/2508-OpenCUA]] |
| 2025-10 | BJudge，100 steps | 72.6% | GPT-5 与 Opus 4.5 各生成 5 条 rollout，再由 GPT-5 选优；相对 72.36% human baseline 的 0.24 点差约等于一个任务，不能据此宣称稳定超越人类 [[Papers/2510-ScalingAgents]] |

高分辨率专业软件又暴露出另一种边界：在普通 grounding benchmark 上的能力不能直接迁移到密集工具栏、小图标和多窗口界面，ScreenSpot-Pro 因此把评测从通用页面推进到专业桌面场景 [[Papers/2504-ScreenSpotPro]]。这些结果共同说明，benchmark 水位上升并未消除 setting、cost、verifier 与长程可靠性的差异；可发表的 CUA 综述必须同时报告能力与证据条件。

### 1.3 Development of Computer-Use Agents

CUA 的发展不是模型名称的顺序更替，而是连续五次系统抽象升级。每一阶段解决上一阶段最明显的可扩展性问题，同时把瓶颈推向更长的 horizon、更隐蔽的状态或更严格的验证条件。

| 阶段 | 主导抽象 | 解决的旧问题 | 新暴露的瓶颈 | 代表证据 |
|:--|:--|:--|:--|:--|
| 2017–2023：结构化接口 | DOM/AXTree + element action + self-hosted Web | 将自然语言目标映射为可执行 navigation | 依赖网页结构，难迁移到 canvas、Mobile 与 Desktop | [[Papers/2307-WebArena]] |
| 2023–2024：Screenshot-native | 高分辨率视觉 + coordinate grounding + OS/Mobile benchmark | 绕过不完整或不可用的结构化接口，获得跨平台观察能力 | 局部 grounding 与长程成功脱节 | [[Papers/2312-CogAgent]]、[[Papers/2408-OmniParser]] |
| 2024–2025：Agent-system 化 | grounder、planner、memory、critic 与 tool router | 将 perception、planning 和 execution 分给专用模块 | 模块误差级联、成本上升、状态所有权不清 | [[Papers/2504-AgentS2]] |
| 2025–2026 上半年：闭环学习 | task/state/verifier 共生成 + online RL + environment factory | 让真实交互产生可学习的 reward 与新任务 | task validity、rollout 吞吐、reset 成本与 verifier 偏差成为上限 | [[Papers/2601-EvoCUA]]、[[Papers/2511-DreamGym]] |
| 2026 年 7 月：可问责系统（萌芽） | belief provenance + explicit task state + semantic action + oversight | 将端到端成功拆为可检查的状态转移 | 跨层因果证据、安全边界和人类注意力分配尚未闭合 | [[Papers/2607-GUIStateBelief]]、[[Papers/2607-Tactile]] |

结构化接口首先获得可执行性，却把 agent 绑定在特定平台；screenshot-native 提供通用观察后，错误从元素识别转移到长程状态维护；模块化 agent 为长程任务引入规划与记忆，又产生跨模块误差和隐式状态；闭环学习利用真实 interaction 改进 policy，却要求可重置环境与可信 reward。第五阶段据此把 provenance、task state、verification、recovery 与 oversight 提为一等对象，但其证据主要来自距本文编写时间很近的 preprint，应理解为前瞻性研究假设，而非已经完成的范式转折。

### 1.4 Limitations of Existing Surveys

现有 survey 已建立平台、组件、能力和学习范式的基础 taxonomy，但其截稿时间与组织方式不足以覆盖 2025–2026 年 environment、Agentic RL、verifier、runtime 和可靠部署的快速发展。以下差异不是对既有工作的质量排序，而是说明本综述需要补齐的分析层。

| Survey | 主要覆盖 | 可复用价值 | 对完整 CUA 综述的局限 |
|:--|:--|:--|:--|
| Large Language Model-Brained GUI Agents [[Papers/2411-GUIAgentSurvey]] | Web/Mobile/Desktop/跨平台；perception、prompt、inference、action、memory、data、model、evaluation | 覆盖面广，提供平台 × pipeline 的 living cookbook | 平台切分使同一方法分散在多章；缺少 setting-aware quantitative meta-analysis；2025 年下半年后的 RL、runtime 与 verifier 进展未被系统吸收 |
| OS Agents [[Papers/2508-OSAgentsSurvey]] | 环境/观察/动作三组件，understanding/planning/grounding 三能力，以及 foundation model、framework、benchmark | component taxonomy 清晰，适合作为 OS Agent 检索入口 | 文献窗口主要反映 2024 年末；RL 覆盖偏轻；表格以 categorical label 为主，缺少 benchmark 数字与 failure-mode 综合；safety defense 和 personalization 较薄 |
| A Comprehensive Survey of Agents for Computer Use [[Papers/2501-ACUSurvey]] | domain、interaction、agent 与 learning 的 technology-agnostic taxonomy | 能把早期 specialized/RL agent 与 foundation agent 放入同一坐标 | 关键证据多为 illustrative cross-paper comparison；缺少统一再评测和定量 meta-analysis；GUI grounding、商业系统及后续 Agentic RL 覆盖不足 |

三类 survey 的共同缺口是：taxonomy 强于机制归因，静态模型与 framework 强于 environment/runtime，任务成功率汇总强于 verifier 可信度，成功案例强于 failure、recovery、abstention 与 human oversight。完整 CUA 综述因而需要把模型、学习、数据、环境、评测和部署放入同一状态转移闭环，并在每项横向比较中显式报告 harness、step budget、backbone、verifier、cost 与数据分布。

### 1.5 Research Questions

后续十二节由十二个研究问题组织。问题从定义与感知逐步推进到学习基础设施、可靠部署和开放研究议程，避免按平台或模型名称重复罗列工作。

| RQ | 对应后续主题 | 核心问题 |
|:--|:--|:--|
| RQ1 | §2 Definition and Taxonomy | CUA 的必要组成、能力边界与平台 × 组件坐标应如何定义？GUI-only、OS Agent 与 GUI+API/CLI hybrid system 如何区分？ |
| RQ2 | §3 Perception and Grounding | screenshot、DOM、AXTree、OCR、SoM 与 hybrid observation 在什么条件下有效，又在何种 UI 分布上失效？ |
| RQ3 | §4 Action and Interface | coordinate、element、semantic action、code、API 与 MCP 如何统一，动作抽象如何影响可迁移性和安全性？ |
| RQ4 | §5 Model and Agent Architecture | native end-to-end model、compositional framework 与 multi-agent system 的性能、成本和误差传播边界是什么？ |
| RQ5 | §6 Planning, Memory and Tool Use | planning、search、memory、reflection 与 tool routing 如何维护长程 task state，而不放大陈旧信息和模块误差？ |
| RQ6 | §7 Training and Reinforcement Learning | pretraining、SFT、offline/online RL、RLVR 与 self-improvement 分别需要什么 reward、headroom 和稳定性条件？ |
| RQ7 | §8 Data, Tasks and Experience | instruction、initial state、trajectory、failure、validator 与 curriculum 如何生成、过滤和组合？ |
| RQ8 | §9 Environment and Runtime | reset、snapshot、fork、parallel rollout、isolation 与 reproducibility 如何同时满足 realism、controllability 和 scalability？ |
| RQ9 | §10 Evaluation and Verifier | grounding、step、trajectory 与 task success 应如何评测？programmatic verifier、LLM judge 与 interactive verifier 的误差边界是什么？ |
| RQ10 | §11 Reliability and Recovery | agent 如何检测 false completion、定位失败、选择 recovery、abstain，并恢复到可验证状态？ |
| RQ11 | §12 Safety, Privacy and Human Oversight | 权限、隐私、prompt injection、不可逆动作、clarification、confirmation 与 human handoff 应如何共同设计？ |
| RQ12 | §13 Deployment and Future Directions | cost、latency、personalization、continual adaptation 与真实组织工作流如何改变 CUA 的研究目标和开放问题？ |

### 1.6 Contributions

本综述的贡献包括：

- **统一研究对象。** 以平台 × 组件为基础坐标，同时纳入 GUI-only、跨平台与 GUI+API/CLI hybrid system，并给出与相邻 Agent、VLM、World Model 研究的纳排边界。

- **重建因果演进。** 将 CUA 组织为结构化接口、screenshot-native、agent-system、闭环学习与可问责系统五个阶段，解释每次升级解决的问题及其新暴露的瓶颈。

- **执行 setting-aware 证据综合。** 对关键数字同时记录 environment、task split、step budget、backbone、verifier、rollout scaling 与 cost，避免把不可比设置压成单一 leaderboard。

- **贯通模型与基础设施。** 在同一闭环中分析 observation、action、architecture、learning、data、environment、runtime、evaluation、recovery、safety 与 HCI，突出跨层依赖而非孤立模块增益。

- **提出可证伪的 accountable-state thesis。** 将 provenance、explicit task state、semantic action、verification、recovery 与 oversight 视为长程可靠性的候选共同接口，同时明确该观点属于作者综合假设，仍需独立复现和因果实验。

- **形成十二问题研究议程。** 后续章节以十二个 RQ 覆盖从基础定义到真实部署的完整链路，并将缺乏来源、设置不可比和证据冲突保留为显式 gaps，而非转写为确定结论。