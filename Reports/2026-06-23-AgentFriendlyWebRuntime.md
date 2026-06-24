---
title: Agent-Friendly Web Runtime 研究设想
date: 2026-06-23
tags: [report, web-agent, gui-agent, environment, research-idea]
sources:
  - "[[2605-MobileGym]]"
  - "[[2601-WebGym]]"
  - "[[2606-AsyncWebRL]]"
  - "[[2600-WebHarbor]]"
  - "[[2606-CUAGym]]"
  - "[[2605-SaaSBench]]"
  - "[[2307-WebArena]]"
  - "[[2400-WebcanvasBenchmarkingWebAgents]]"
  - "[[Reports/2026-06-23-WebGym-AsyncWebRL]]"
  - "Gym-Anything: https://arxiv.org/abs/2604.06126"
  - "Odysseys: https://arxiv.org/abs/2604.24964"
  - "[[2412-BrowserGymAgentLab]]"
---

# Agent-Friendly Web Runtime 研究设想

## 当前对话总结

我们先从 [[2605-MobileGym]] 出发，注意到它最重要的 insight 不是“仿真界面要像真实手机”，而是 **interaction fidelity / state transition fidelity 比 pixel-perfect rendering 更关键**。MobileGym 通过 JSON state、EFSM transition、state forking 和 deterministic verifier，在低成本 browser-hosted 环境中实现可验证、可并行的 mobile GUI agent RL，并报告 95.1% sim-to-real retained gain [[2605-MobileGym]]。

随后我们讨论 Web 侧是否已有类似工作。结论是，[[2601-WebGym]] 和 [[2606-AsyncWebRL]] 已经把 “large-scale visual web agent training + online RL + rollout throughput optimization” 这条路基本走通：WebGym 用近 300K web tasks 和 rubric evaluator 将 Qwen3-VL-8B-Instruct 在 OOD split 上从 26.2% 提升到 42.9%，AsyncWebRL 又通过 fully async rollout 和 loss normalizer 修复把 WebGym 上的结果提升到 45.4% [[2601-WebGym]] [[2606-AsyncWebRL]]。

因此，继续沿着 WebGym 拼任务规模、标注自动化、RL 系统吞吐，会正面撞上大资源路线。我们转而提出一个不同方向：**不训练 agent 去适应普通网页，而是设计 agent-friendly web server / runtime，让同一个模型在 zero-training 条件下通过更好的环境支撑完成更多任务**。

当前核心问题是：这种做法和“给 agent 更多 prompt / 写更详细的网页说明”有什么区别？如果区别不清楚，这个方向会显得 trivial。

## 2026-06-24 增量调研：Web/CUA Environment Landscape

结合新读的 [[2600-WebHarbor]]、[[2606-CUAGym]]、[[2605-SaaSBench]]，以及最新外部检索到的 Gym-Anything、Odysseys、BrowserGym / WorkArena++、EnvFactory / Agent-World，web/CUA environment 已经不是单一路线，而是形成了几个相互竞争又互补的范式。

### 1. Live/Open-Web Evaluation：真实但不可控

代表：WebVoyager、WebCanvas / Mind2Web-Live、Odysseys、EconWebArena。

这条路线最大优点是真实：live websites、有内容漂移、有真实 UI、有跨站信息获取。Odysseys 进一步把问题推到 200 个 long-horizon multi-site tasks，最强 frontier model 成功率 44.5%，Trajectory Efficiency 只有 1.15%，说明“最终能不能做完”和“是否高效做完”必须分开评估。问题是它很难用于 RL training：环境不可 reset，网站会漂移，有登录/反爬/地理位置问题，reward 多依赖 rubric 或 human-like judging。

**对本 proposal 的启示**：live web 是真实性上限，但不是第一版实验环境。更合理做法是把 live/open-web 的 failure mode（cross-site context loss、inefficient browsing、rubric partial credit）作为 design target，而不是直接在 live web 上做 agent-friendly runtime。

### 2. Unified Web Agent Harness：标准化 observation/action，但不改变应用

代表：BrowserGym / AgentLab、WorkArena、WorkArena++。

BrowserGym 解决的是 benchmark fragmentation：统一 web agent 的 observation/action space，让不同 benchmark 可以在同一 gym-like API 下评估。WorkArena / WorkArena++ 则把 web agent 拉进 enterprise software 和 knowledge work tasks，强调 ServiceNow 场景、规划、检索、逻辑/算术推理和上下文理解。

**边界**：这类工作主要标准化 agent harness，不主动把底层 web app 变成 agent-friendly system。它给 agent 一个更一致的浏览器接口，但不提供 app-level rollback、state diff、semantic action provenance 或 verifier-facing state API。

### 3. Self-hosted Realistic Web/SaaS：可复现但昂贵

代表：WebArena、[[2605-SaaSBench]]、TheAgentCompany。

WebArena 早期证明 self-hosted realistic web apps + functional correctness 的价值。SaaS-Bench 将这个方向推进到 23 个 deployable SaaS systems、6 个专业领域、106 个长程跨应用任务，最强模型 checkpoint score 43.9%，resolved score 仅 3.8%。TheAgentCompany 则把 web、code、communication 和内部数据放进一个小公司环境，测数字 worker 式任务。

**关键洞察**：真实后端状态和业务实体会制造 screenshot 看不出的 failure。SaaS-Bench 的 Entity Missing、entity-type mismatch、checkpoint decay 都说明 agent 需要显式理解 application schema 和 outcome verification，而不只是更强视觉 grounding。

### 4. Local Mirrors / Docker Docking：把 live web 变成本地可控环境

代表：[[2600-WebHarbor]]。

WebHarbor 把真实网站 dock 成 Docker mirror。第一版覆盖 WebVoyager 的 15 个网站，用 SQLite seed DB 和 control plane 支持快速 reset，目标是保留真实网站的视觉、多模态内容、auth/cart/checkout 等深层功能，同时消除 live-web 的 reCAPTCHA、geo-block、content drift。它的 review protocol 特别强调 visual fidelity、functional depth、answer leak、distractor density 和 reset md5 一致性。

**与本 proposal 的关系**：WebHarbor 是很好的实验底座。它解决“环境哪里来”，但还没有明确解决“给 agent 什么 runtime affordance”。因此我们可以站在 WebHarbor 之上，研究 agent-facing affordance 是否带来收益。

### 5. Synthetic / Mock Web Environments：可规模化但要证明迁移

代表：InfiniteWeb、[[2606-CUAGym]] / CUA-Gym-Hub。

InfiniteWeb 通过 unified specification、task-centric test-driven development 和 design seed 自动生成 functional websites，并生成 task evaluators。CUA-Gym-Hub 更进一步：合成一组 self-contained mock web apps，带统一 state API、session isolation、state injection/reset/diffing，让同一个 mock app 可以承载大量 RLVR tasks。CUA-Gym 用这些环境构造 32,112 个 verified RLVR tuples，并让 A3B / A17B 在 OSWorld-Verified 和 held-out WebArena 上提升。

**关键区分**：CUA-Gym 的 state API 主要服务 setup/reward/parallel rollout，不是默认暴露给 agent 的 reasoning interface。它是 training-friendly environment，不等于 agent-friendly runtime。

### 6. Verifier-Centric Software Worlds：把“判分”变成环境核心

代表：[[2605-OpenComputer]]、MobileGym、Gym-Anything / CUA-World。

OpenComputer 把 app-specific verifier 作为组织原则，hard-coded verifier 与 human alignment 达 94.1%，显著高于 LLM judge。MobileGym 用 JSON state、state forking、AnswerSheet 和 deterministic judge，在 mobile 侧实现 95.1% sim-to-real retained gain。Gym-Anything 则把 environment creation 本身变成 multi-agent task：coding agent 配置任意软件，audit agent 检查 setup evidence，形成 CUA-World（200 software apps、10K+ long-horizon tasks、CUA-World-Long 常超过 500 steps）。

**启示**：未来环境的核心资产不是页面数量，而是可验证状态表面。没有 verifier 的环境只能评估“看起来完成”，不能稳定支撑 RL 或可靠诊断。

### 7. Hybrid Native Runtime：真实工作不是 web-only

代表：[[2606-WeaveBench]]、Agents' Last Exam、WildClawBench。

WeaveBench 证明真实工作流需要 GUI+CLI+Code 协同，hybrid setting 比 GUI-only/CLI-only 高约 30pp，但也暴露 reward hacking 和 fabricated evidence。Agents' Last Exam 覆盖 GDP-relevant professional workflows，最难 tier 平均 full pass rate 只有 2.6%。WildClawBench 在真实 CLI agent harness 中测长程、多模态、双语任务，最强模型也只有 62.2%，且 harness 切换会导致大幅分数变化。

**对 web runtime 的约束**：不要把 web-agent 研究孤立成浏览器点击问题。真正的 agent-friendly web runtime 应该能和 files/API/CLI/code channel 对齐，至少在 trace、verification、permission 和 rollback 上兼容 hybrid agent harness。

## 综合判断：环境研究的四个正交轴

| 轴 | 低端 | 高端 | 代表工作 | 对本方向的含义 |
|:--|:--|:--|:--|:--|
| Realism | toy/mock | live/professional SaaS | Odysseys, SaaS-Bench, WebHarbor | 第一版不必追 live，但 failure mode 要来自真实任务 |
| Controllability | 无 reset | deterministic reset/fork | MobileGym, CUA-Gym-Hub, WebHarbor | rollback/checkpoint 是核心差异点 |
| Verifiability | LLM/rubric judge | programmatic state verifier | OpenComputer, CUA-Gym, MobileGym | progress signal 必须来自状态，不是自评 |
| Agent-facingness | verifier-only API | agent 可查询/执行 affordance | 当前工作较少 | 本 proposal 的空白点 |

最重要的更新是第四轴：很多新工作已经有强环境、强 verifier、强 reset，但这些能力大多藏在 evaluator / trainer / environment backend 中，**并没有以受控、非作弊、task-agnostic 的方式暴露给 agent**。Agent-Friendly Web Runtime 应该明确站在这个空白点上。

## 一句话主张

**Agent-Friendly Web Runtime** 的核心不是把网页说明写进 prompt，而是让 web server 在运行时提供一组可执行、可验证、可恢复、与真实状态绑定的 agent affordances，从而改变 agent 的可观测性和可控性边界。

更具体地说：

> 普通 prompt 只能告诉 agent “网页通常怎么用”；agent-friendly server 能在当前会话状态下告诉 agent “你现在在哪里、哪些状态真实存在、哪些动作可执行、如何回滚、哪些子目标已经满足”。

这个差异如果成立，就不是 prompt engineering，而是 **environment design**。

## 为什么不是直接写更长 Prompt

这个方向必须正面回答 triviality 风险。我的判断是，server-side affordance 和 prompt 的区别至少有六个可实验区分的维度。

### 1. 静态说明 vs 运行时真实状态

Prompt 可以提前写网站结构、常见流程、按钮含义，但它通常是静态的。网页运行时状态会变化：登录状态、购物车内容、表单校验、当前 route、modal、pagination、localStorage、backend DB 都可能改变。

Server-side runtime 可以读取或维护当前真实状态，并按需暴露给 agent。比如 “当前 cart 中已有 item A，checkout form 的 shipping address 未通过校验” 是运行时 state；把 checkout 教程写进 prompt 不能可靠得到这个信息。

### 2. 建议动作 vs 可执行动作

Prompt 只能建议 agent “如果想搜索商品，先点击搜索框再输入关键词”。执行仍然依赖模型在截图上找到正确元素，且可能因为页面变化而失败。

Server 可以声明 **semantic actions**，如 `search_products(query)`、`open_cart()`、`apply_filter(price_range)`。这些 action 不应是 task-specific shortcut，而应来自页面真实 affordance 的语义封装。它们改变的是 action space，不只是 context。

### 3. 记忆提醒 vs 可恢复控制

Prompt 可以提醒 agent “如果走错，可以返回上一页”，但真正的 browser back 可能不能恢复 form state、modal state、multi-tab state 或 backend mutation。

Server 可以提供 checkpoint / rollback / branch：`save_checkpoint()`、`restore(checkpoint_id)`、`branch_from(step_k)`。这属于环境可控性，prompt 做不到。MobileGym 的 state forking 证明这种能力对 group-based RL 和可逆评估很重要 [[2605-MobileGym]]。

### 4. 通用教程 vs 当前网站 World Map

Prompt 可以包含网站教程，但不能在所有页面状态下持续维护“当前页面在网站层级中的位置、可达页面、已访问路径、未探索分支”。

Server 可以暴露 website world map：当前 route、parent/child pages、可达 action graph、关键 landmarks、历史访问轨迹。这可以直接针对 web agent 常见的 navigation drift、重复访问、迷路回不来等失败模式。

### 5. 自我判断 vs 环境验证

Prompt 可以要求 agent “完成前自检”，但自检仍然是模型自己的判断。WebGym 的 rubric evaluator 已经说明 reward/evaluator 对 web agent RL 很关键，但它主要还是 rubric judge，而不是确定性状态检查 [[2601-WebGym]]。

Server 可以提供 task-agnostic progress signals 或 verifier endpoints，例如 form valid、draft saved、cart updated、issue created、permission changed。这些不直接泄露任务答案，但提供比模型自我判断更可靠的状态反馈。WebArena 的 programmatic locator / functional correctness 也是类似思想 [[2307-WebArena]]。

### 6. 上下文膨胀 vs 按需查询

把所有网站说明、层级、技能都写进 prompt，会导致 context bloat，且信息未必与当前状态相关。AsyncWebRL 发现 multi-step agent 的 verbose memory schema 会造成 token / step 膨胀，并影响训练行为 [[2606-AsyncWebRL]]。

Server-side runtime 可以让 agent 按需查询最相关的 affordance，如 `get_current_page_actions()`、`get_nearby_landmarks()`、`get_recovery_options()`。这不是更多 prompt，而是更低熵、更状态绑定的信息接口。

## 研究目标

目标不是再做一个 WebGym，也不是替代浏览器。目标是定义并验证一种 **dual interface web runtime**：

- Human 看到正常网页 UI。
- Agent 除了 screenshot / DOM 外，还能访问一组由 server 提供的结构化 affordances。

这些 affordances 应该满足三个约束：

1. **Task-agnostic**：不能泄露当前任务答案或 gold trajectory。
2. **State-grounded**：必须来自当前真实页面 / session / backend state，而不是静态说明。
3. **Executable or verifiable**：最好不是纯文本建议，而是能执行、能恢复、能检查的环境能力。

如果同一个 zero-training model 在普通 browser 上失败、在 agent-friendly runtime 上成功，并且 prompt-only baseline 无法达到同样提升，那么这个方向就不 trivial。

结合 2026-06 的新工作，这句话需要再收窄一点：

> 本工作不是再造 WebHarbor / CUA-Gym 式环境，也不是再做 WebGym 式 RL，而是研究 **verifier/reset/state API 中哪些能力可以作为 non-oracle agent-facing affordance 暴露，并因果性降低 execution failure**。

也就是说，贡献点从“构建 web 环境”转为“定义 agent-facing boundary + 证明 runtime affordance 的 causal effect”。

## Key Idea

构建一个 **Agent-Friendly Web Runtime**，在 self-hosted web apps 上增加一层 agent protocol。这个 protocol 不改变用户可见 UI，但为 agent 提供以下能力。

### 1. Website World Map

Server 根据 route tree、link graph、form/action endpoints、component hierarchy 生成网站层级图。Agent 可以查询：

- 当前页面处于哪个 section。
- 上一跳 / 下一跳 / sibling pages 是什么。
- 当前任务相关但未访问的候选区域有哪些。
- 已访问路径和可能的 loop。

它解决的 failure mode 是 navigation drift、重复点击、找不到返回路径。

### 2. Reversible Navigation and State Checkpoints

Server 支持保存和恢复 browser/session/backend state。Agent 可以在不破坏任务状态的前提下探索分支。

它解决的 failure mode 是错误路径不可恢复、表单状态丢失、multi-step task 中一次误操作毁掉全局 trajectory。

### 3. Semantic Action Layer

Server 将页面真实 affordance 封装成 task-agnostic semantic actions。例子：

- `search(query)`
- `open_cart()`
- `filter_results(field, value)`
- `open_issue(issue_id)`
- `save_draft()`
- `submit_form(form_id)`

这些 action 必须从页面结构自动或半自动生成，不能手写当前任务答案。它解决的 failure mode 是视觉 grounding 错误、低级点击噪声、复杂 UI action composition。

### 4. Site Skill Cards

每个网站提供 reusable workflow schema，比如 search/filter/checkout/create-post/edit-settings。Skill card 是类似 API 文档的通用使用说明，不包含当前任务变量和答案。

它和 prompt 的区别在于：skill card 由 server 根据当前页面状态检索和裁剪，只在相关时注入；同时可以绑定 semantic action 和 verifier endpoint，而不是纯自然语言教程。

### 5. Progress and Consistency Signals

Server 提供 task-agnostic state checks，例如：

- form field validity
- cart contains / count
- draft saved
- current item selected
- backend record created
- URL / route state
- unsaved changes warning

这些 signal 不直接告诉 agent “任务完成”，但能减少 false completion 和 hidden-state 错误。

## 核心假设

### H1：环境 affordance 可以替代部分训练

若 web server 提供 state-grounded affordance、world map 和 reversible state control，则同一个 zero-training VLM agent 在 web task completion 上会显著优于普通 browser baseline。

### H2：server-side affordance 优于 prompt-only affordance

如果把相同的静态网站说明、workflow 和 skill cards 写进 prompt，提升会小于 runtime server protocol。原因是 prompt-only 缺少实时状态绑定、可执行 action、checkpoint/rollback 和 verifier feedback。

### H3：收益主要来自减少 execution failure，而非增强 reasoning

Agent-friendly runtime 的主要收益应体现为 navigation drift 降低、repeated action 降低、false completion 降低、recovery success 提升，而不只是最终 success rate 提升。

### H4：不同 affordance 对不同 failure mode 有选择性作用

World map 应主要减少迷路和重复访问；rollback 应主要提升错误恢复；semantic action 应主要减少 grounding/execution error；progress signals 应主要减少 false completion。这个可通过模块消融验证。

## 实验设计

### 环境

优先选择 self-hosted web apps，而不是 live websites，避免反爬、内容漂移和账号问题。现在更好的底座不是从零写 web apps，而是复用三类已有环境：

- **WebHarbor mirror**：保留真实网站视觉和深功能，适合测 navigation / search / cart / booking / map 等真实 web flows。
- **CUA-Gym-Hub mock apps**：已有统一 state API 和 session isolation，适合接入 verifier/progress signal 和并行 rollout。
- **WebArena-style apps**：shopping、forum、GitLab-like issue tracker、CMS/admin，适合与早期 web agent baseline 对齐。

第一版建议选 2-3 个站点 / app family，每个 15-20 个任务，总计 40-60 个任务。任务不追数量，而追 failure-mode 覆盖：navigation drift、answer leak、hidden-state mismatch、false completion、irreversible wrong turn。

### 对照条件

必须有 prompt-only baseline，否则无法证明不是 trivial prompt engineering。

| Condition | 描述 | 目的 |
|:--|:--|:--|
| C0 Normal Browser | 普通 screenshot/DOM/action agent | 基线 |
| C1 Static Prompt | 把网站说明、常见 workflow、skill cards 写入 prompt | 测“更长 prompt” |
| C2 Dynamic Prompt | 每步把 current page summary / nearby links 注入 prompt，但不提供特殊 action | 测动态文本观察 |
| C3 World Map API | agent 可查询网站图和当前位置 | 测 navigation affordance |
| C4 + Rollback | 加 checkpoint / restore / branch | 测 recovery affordance |
| C5 + Semantic Actions | 加 task-agnostic semantic action layer | 测 action affordance |
| C6 Full Runtime | world map + rollback + semantic actions + progress signals | 测完整系统 |
| C7 Evaluator-only State API | verifier/state API 只给 evaluator，不给 agent | 区分“更好判分”与“更好执行” |

如果 C3-C6 显著超过 C1-C2，才能说明 server-side affordance 不只是 prompt。

C7 是新增关键对照。CUA-Gym / OpenComputer 已经证明 state API/verifier 能改善训练或评测，但这不等价于 agent-facing runtime 有用。若 C7 只能改善判分可信度，而 C3-C6 改善执行过程，才能证明本工作的独立价值。

### 模型

不做训练，选择 2-3 个现成模型：

- 一个强闭源 VLM / CUA model
- 一个开源 VLM agent backbone
- 一个较弱模型，用来看 affordance 是否降低能力门槛

重点是 zero-training，不走 WebGym / AsyncWebRL 的算力路线。

### 指标

最终指标：

- task success rate
- task completion / partial credit
- steps / tokens / wall-clock time

failure-mode 指标：

- navigation drift rate
- repeated action / loop rate
- recovery success after wrong turn
- false completion rate
- grounding/action execution error
- verifier mismatch
- rollback usage frequency

新增 environment-specific 指标：

- reset/fork latency
- state-probe precision / leak rate
- semantic action granularity violation rate
- answer leak rate
- mock-to-mirror transfer gap
- evaluator-only vs agent-facing gain gap

这些 failure metrics 比最终 SR 更重要，因为本工作的 claim 是环境 affordance 改变 execution dynamics。

## 关键挑战

### 1. 如何避免 Oracle / Cheating

这是最大挑战。World map、skill card、semantic action、progress signal 很容易被质疑为泄露答案。

需要定义 **Allowed Affordance Boundary**：

- 可以暴露网站通用结构，不能暴露当前任务 gold path。
- 可以暴露当前状态，不能告诉 agent 哪个状态是最终目标。
- 可以提供 reusable semantic actions，不能提供 task-specific macro action。
- 可以提供 field validity / record existence，不能直接提供 “task complete = true”。

实验中也要加入 adversarial checks：更换任务目标、变量、路径，确认 affordance 不是 hard-coded solution。

### 2. 如何证明不是 Prompt Engineering

必须做 C1/C2 prompt-only baseline。更进一步，可以把 server 返回的信息原样塞进 prompt，但不提供可执行 API / rollback / verifier，看提升是否仍然不足。

若 Full Runtime 的主要收益来自 semantic action 和 rollback，而 prompt-only 只带来小幅提升，就说明贡献在 environment action/control，而非文本说明。

### 3. 如何保持通用性

如果每个网站都手写几十个 skill，这会像 RPA，不像研究。需要把 affordance 生成尽量协议化：

- 从 route definitions 生成 world map。
- 从 form schema / API endpoints / DOM roles 生成 semantic action candidates。
- 从 database schema / app state 生成 verifier endpoints。
- 从 successful human / agent traces 归纳 reusable skill cards。

第一版可以半自动，但论文必须明确哪些部分是 general protocol，哪些是 per-site adapter。

### 4. 如何处理真实 Web 的复杂性

Live web 有广告、推荐、登录、反爬、地理位置、A/B test。第一版不应追求 live web 全覆盖。更合理的叙事是：先在 self-hosted realistic apps 中证明 agent-friendly runtime 的因果作用，再讨论迁移到 live sites。

这和 WebArena 的 self-hosted realism 路线一致：先保证可复现和 functional correctness，再扩展开放性 [[2307-WebArena]]。

### 5. 如何避免 affordance 让任务变简单到无意义

如果 semantic action 太强，比如 `complete_checkout_for_target_item()`，任务直接被工具做完。应限制 action 粒度：

- 原子或小组合，不跨越多个语义阶段。
- 与 human UI action 有对应关系。
- 每个 action 的 effect 可解释、可回放、可检查。
- macro skill 只能生成 plan 或候选 action，不直接完成 task。

## Motivation

这个方向的动机来自三个观察。

第一，WebGym / AsyncWebRL 已经验证了大规模 web agent RL 的可行性，但它们需要大规模任务、昂贵 rollout 和训练资源 [[2601-WebGym]] [[2606-AsyncWebRL]]。如果我们继续沿着这条路线，很容易变成资源竞赛。

第二，很多 web agent failure 并不是“模型完全不会推理”，而是执行过程中迷路、重复、误点、误判完成、无法恢复。WebArena 早期结果已经显示长程、多 tab、状态修改类任务对 agent 很难，人类和 GPT-4 存在巨大差距 [[2307-WebArena]]。WebCanvas / Mind2Web-Live 也强调在线网页环境中 process-level evaluation 和 intermediate states 的重要性 [[2400-WebcanvasBenchmarkingWebAgents]]。

第三，MobileGym 提供了一个不同启发：环境本身可以被重新设计成更可控、更可验证、更适合 agent learning / evaluation，而不必追求像素级复刻真实界面 [[2605-MobileGym]]。将这个思想迁移到 Web，不一定是再做 simulator，而可以是做 agent-friendly runtime。

## 预期贡献

一个完整工作可以有三类贡献：

1. **Conceptual contribution**：提出 Agent-Friendly Web Runtime，把 web server 从 human-only UI provider 扩展为 dual interface environment。
2. **System contribution**：实现 world map、rollback/checkpoint、semantic actions、skill cards、progress signals 的统一 protocol。
3. **Empirical contribution**：证明 server-side runtime affordance 在 zero-training 条件下显著优于 normal browser 和 prompt-only baselines，并用 failure-mode metrics 解释收益来源。

## 最小可行版本

不需要一开始做大。建议最小版本如下：

- 2 个 self-hosted web apps：shopping + issue tracker。
- 每个 20 个任务，共 40 个任务。
- 3 个 affordance：world map、checkpoint/rollback、progress signals。
- 不做 semantic action，先避免被说 tool shortcut。
- 对照 C0/C1/C2/C3/C4。
- 模型选一个强模型 + 一个开源模型。

如果这个最小版本已经显示：C3/C4 显著降低 navigation drift 和 false completion，而 C1/C2 prompt-only 无法复现，那这个 idea 就成立了一半。

第二阶段再加入 semantic actions 和 site skill cards。

## 资源判断

相比 WebGym / AsyncWebRL，这条路线资源友好得多：

- **不需要训练**：zero-training evaluation 即可。
- **不需要 24 H100 rollout**：主要成本是模型 API 调用和 self-hosted web app 工程。
- **任务规模可小**：40-120 个高质量任务就能验证机制。
- **工程成本中等**：需要写 web app adapter 和 runtime API，但比大规模 RL infra 小得多。

风险在于工程设计和实验论证，而不是算力。

## 当前最值得追的问题

我认为最值得追的是：

> **Can server-side environment affordances outperform prompt-only guidance for zero-training web agents?**

这句话把问题卡得比较准：

- server-side vs prompt-only：直接回答 triviality。
- environment affordances：强调不是大模型 prompt，而是环境协议。
- zero-training：避开 WebGym 的资源路线。
- web agents：场景明确。

如果结果成立，这个方向可以自然扩展到：

- Agent-friendly web standard / protocol
- GUI agent browser runtime
- Verifier-grounded web interaction
- Human-agent dual interface design

## 与现有工作的关系

- 相比 [[2601-WebGym]]：本工作不追求任务规模和 RL 训练，而是研究环境 affordance 是否能降低 zero-training agent 的执行难度。
- 相比 [[2606-AsyncWebRL]]：本工作不优化 rollout throughput，而是减少 agent 在环境中的无效探索、错误路径和状态恢复成本。
- 相比 [[2605-MobileGym]]：本工作继承 state/fork/verifier 的环境哲学，但目标不是 mobile simulator，而是 web server/runtime protocol。
- 相比 [[2307-WebArena]]：本工作可以复用 self-hosted realistic apps，但不是只做 benchmark，而是改变环境对 agent 暴露的接口。
- 相比 [[2600-WebHarbor]]：WebHarbor 解决真实网站本地化和快速 reset；本工作研究在这些 mirror 上哪些 state/action/recovery affordance 可以安全地暴露给 agent。
- 相比 [[2606-CUAGym]]：CUA-Gym 解决 RLVR tuple 合成和 programmatic reward；本工作不把 state API 只留给 reward，而是测试受限 state probes / semantic actions 是否提升 zero-training execution。
- 相比 [[2605-SaaSBench]]：SaaS-Bench 暴露真实 SaaS workflow 的 resolved-score collapse；本工作试图把 closed-loop verification 和 schema awareness 前移到 agent 执行过程中。
- 相比 Gym-Anything / CUA-World：Gym-Anything 关注把任意软件转成 agent environment；本工作关注 environment 转好之后，agent 能不能获得更合适的 runtime interface。
- 相比 prompt engineering：本工作必须通过 prompt-only baseline 证明 server-side runtime 的额外价值。

## 暂定标题

候选标题：

1. **Agent-Friendly Web Runtime: Environment Affordances for Zero-Training Web Agents**
2. **Beyond Prompting: Server-Side Affordances for Reliable Web Agents**
3. **Designing Web Servers for Agents: Reversible, Navigable, and Verifiable Web Interaction**
4. **Can Better Web Environments Replace RL for Web Agents?**

我最喜欢第 2 个，直接回应 triviality；第 1 个更像正式论文标题。
