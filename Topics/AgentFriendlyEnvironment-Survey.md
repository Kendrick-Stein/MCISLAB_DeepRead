---
title: Agent-Friendly Environment 调研与研究设想
tags: [survey, gui-agent, environment-engineering, computer-use, web-agent, mobile-agent]
date_updated: "2026-06-25"
year_range: 2023-2026
papers_analyzed: 16
keywords: [agent-friendly, environment affordance, agent-facing, runtime, environment engineering]
domain_map: GUI-Agent
---

# Agent-Friendly Environment 调研与研究设想

## Overview

这次问题从 [[Reports/2026-06-23-AgentFriendlyWebRuntime]] 继续展开：如果 agent-friendly browser 是一个有价值的方向，那么能否进一步抽象成 **Agent-Friendly Environment**，覆盖 web / mobile / desktop OS / tool-use 训练环境？

我的结论是：**目前文献里还没有一个统一、成熟的 “agent-friendly environment” 概念，但已有工作已经分别做出了它的局部组件**。BrowserGym / AgentGym 做的是统一 gym-like 接口；OSWorld / AndroidWorld 做的是真实可执行环境；MobileGym / OpenComputer 做的是 state-grounded verifier 和可控 rollout；ToolEmu / AgentDojo 做的是安全 sandbox；MobileWorld / τ²-Bench 引入 user / tool / shared world 的多方动态环境。这些拼起来，正好指向一个新 framing：

> **Agent-Friendly Environment** = 面向 autonomous agents 设计的 dual-interface environment：人类仍看到正常 UI / app / OS，但 agent 额外获得一组 task-agnostic、state-grounded、executable、recoverable、verifiable、safe、cost-efficient 的环境 affordances。

这个定义很重要，因为如果不先定义什么是 agent-friendly，就很容易滑向两个 trivial 方向：

- 把网站 / 手机 / 系统说明写成更长 prompt。
- 给 agent 手写 task-specific macro action，相当于 RPA shortcut。

真正有研究价值的点在于：**不泄露任务答案，也不改变任务目标，只把环境中本来存在但对 agent 不可见、不可控、不可验证的部分结构化暴露出来**。这会改变 agent 的可观测性、可控性和可训练性，而不是简单增加提示词。

## 2026-06-25 Update：Agent-Friendly 必须同时是 Privacy-Friendly

6/24 之后新增的 [[Papers/2606-AgentCIBench]] 改变了 AFE 的安全边界判断：agent-facing state / verifier / world map 不是单向利好。它们能减少 hidden-state mismatch，也可能让 agent 更容易把 task-irrelevant personal state 带进外部输出。

这一点与 [[Papers/2606-MyPCBench]] 和 [[Papers/2606-BraveGuard]] 形成三角证据：

- [[Papers/2606-MyPCBench]]：personal context / logged-in-like state 是真实 CUA 能力轴。
- [[Papers/2606-AgentCIBench]]：即使没有 adversary，CUA 在 normal-use personal tasks 中也会发生 context-inappropriate disclosure，平均 leakage 67.9%。
- [[Papers/2606-BraveGuard]]：CUA safety 更适合做 trajectory-level monitoring，而不是 prompt-level classifier。

因此 AFE Protocol 需要新增一条设计原则：

> **Least-disclosure affordance**：环境可以暴露 state，但必须按 task scope、recipient、data category 和 action purpose 过滤；agent-facing state API 不应默认返回“所有可见个人状态”。

对实验设计的直接影响：

- `observe_state()` 需要区分 task-relevant state、visible-but-out-of-scope state、sensitive state。
- `guard(action)` 不只检查 dangerous action，也要检查 answer-time leakage 和 out-of-scope inspection。
- `trace()` 应记录 evidence provenance：agent 最终输出中的每条信息来自哪个 app/window/file/url，是否在 manifest scope 内。
- AFE ablation 中必须加入 privacy metrics：Personalization Leakage Rate、Out-of-scope Inspection Rate、False Block Rate、Task Completion Retention。

这也提示一个更窄的研究问题：**AFE 的核心不是暴露更多 state，而是暴露正确粒度、正确范围、可审计的 state**。

## 相关工作地图

### 1. Gym-like 统一接口：标准化环境入口

**代表工作**：[[2412-BrowserGymAgentLab]]、[AgentGym](https://arxiv.org/abs/2406.04151)、[[2601-WebGym]]。

BrowserGym 的核心价值是把不同 web agent benchmark 放到统一 observation / action space 中，并配合 AgentLab 做 agent 创建、测试和分析。AgentGym 则强调跨多环境的 real-time、uni-format、concurrent exploration，目标是让 LLM agents 在多类环境中自我演化。WebGym 进一步把 web tasks 扩到近 300K，并展示了 online RL scaling 的可行性。

这一路线解决的是 **interface fragmentation**：不同环境的 action space、observation、logging、evaluation 不一致，导致 agent 方法难以复用和比较。

但它们大多还不是完整的 agent-friendly env。原因是：统一接口不等于友好接口。Gym-like API 让实验能跑起来，但不一定提供 rollback、world map、state verifier、progress signal、安全权限等 agent 执行真正需要的环境支撑。

### 2. Realistic interactive environment：真实可执行世界

**代表工作**：[OSWorld](https://arxiv.org/abs/2404.07972)、[AndroidWorld](https://arxiv.org/abs/2405.14573)、[Windows Agent Arena](https://arxiv.org/abs/2409.08264)、WebArena、VisualWebArena。

OSWorld 将真实桌面 OS、应用、文件 I/O、跨应用 workflow 放进 benchmark，并用 initial state setup + execution-based evaluation script 保证任务可复现。AndroidWorld 在真实 Android emulator 上提供 116 个 programmatic tasks，每个任务包含初始化、成功检查和 teardown。Windows Agent Arena 则把 OSWorld 思路迁移到 Windows，并强调云端并行评测。

这一路线解决的是 **realism and reproducibility**：agent 必须面对真实 UI、真实软件状态和真实长程 workflow。

但它们往往仍是 **human-facing environment repurposed for agents**。agent 主要拿 screenshot / accessibility tree / primitive actions，环境没有被重新设计成更适合 agent 的 runtime。也就是说，它们真实，但未必友好。

### 3. Verifier-first / State-grounded environment：可验证世界

**代表工作**：[[2605-MobileGym]]、[[2605-OpenComputer]]、[MobileWorld](https://arxiv.org/abs/2512.19432)、AndroidWorld。

MobileGym 是最接近 agent-friendly env 的工作之一。它不追求 pixel-perfect mobile simulation，而是用 browser-hosted functional simulator、structured JSON state、state forking、deterministic state-based judging 和 AnswerSheet protocol 来保证 interaction fidelity 和 RL throughput。它报告约 400MB / instance、约 3s cold start、95.1% sim-to-real retained gain，说明 **界面转移过程的 functional fidelity 比像素级复刻更关键**。

OpenComputer 把 verifier 提升成环境构建的组织原则。它为 33 个桌面应用构建 app-specific state verifiers，通过 D-Bus、LibreOffice UNO、SQLite、accessibility tree、文件解析等多通道检查隐藏状态；hard-coded verifier 与人类判断对齐度 94.1%，显著高于 LLM-as-judge 的 79.2%。

MobileWorld 延续 AndroidWorld 的可复现路线，但进一步加入 long-horizon、cross-app、agent-user interaction、MCP-augmented tasks，并通过 snapshot container、backend DB inspection、task callback APIs 做精确功能验证。

这一路线提供了 Agent-Friendly Environment 的核心骨架：**状态可见、状态可比、状态可 fork、结果可验证**。

### 4. Harness / Hybrid interface：把低级操作外部化

**代表工作**：[[2508-ComputerRL]]、[[2606-WeaveBench]]、Harness-1、RHO、OS Agents Survey。

OS agent 的动作空间已经从 primitive GUI input 扩展到 navigation ops、extended ops、code execution、API integration。ComputerRL 的关键启发是 API-GUI unified control：agent 不必所有事情都通过 screenshot-click loop 完成，可以在合适位置使用 API / CLI 加速。[[2606-WeaveBench]] 进一步说明真实工作流往往需要 GUI + CLI + Code 混合协同，单接口在长程任务里会崩。

这一路线说明一个重要事实：**agent-friendly 不等于只改观察空间，也要改动作空间和 harness state**。很多失败并非模型不知道目标，而是被迫用错误粒度的动作通道完成任务。

### 5. Safety / Sandbox environment：安全与边界

**代表工作**：[ToolEmu](https://arxiv.org/abs/2309.15817)、[AgentDojo](https://arxiv.org/abs/2406.13352)、OS-Harm。

ToolEmu 用 LM-emulated sandbox 模拟工具执行，低成本发现高风险 tool-use failure。AgentDojo 把不可信外部数据、prompt injection、attack / defense 放进动态环境，用 realistic tasks 和 security test cases 测 agent 鲁棒性。

这一路线提醒我们：Agent-Friendly Environment 不能只追求更高成功率，还必须内建 permission、side-effect control、untrusted data separation、audit trail。否则“更友好”的环境可能只是让 agent 更容易造成不可控副作用。

### 6. Multi-actor / Shared-world environment：从单 agent 到人机共控

**代表工作**：[τ²-Bench](https://arxiv.org/abs/2506.07982)、MobileWorld。

τ²-Bench 把 conversational agent 放进 dual-control environment：agent 和 user 都可以通过工具改变同一个 shared world，任务建模为 Dec-POMDP，并用 compositional task generator 和 tightly coupled user simulator 保证可验证性。MobileWorld 也加入 agent-user interaction 和 MCP-augmented tasks。

这一路线扩展了 agent-friendly env 的边界：真实任务不是 agent 单独操控一个静态世界，而是要协调用户、工具、后端状态、权限和外部系统。

## 什么是 Agent-Friendly Environment

我建议先给一个可操作定义，否则这个方向会散。

**定义**：

> 一个环境是 agent-friendly 的，当且仅当它在不泄露任务答案、不替 agent 完成目标的前提下，向 agent 暴露任务无关但状态绑定的环境 affordances，使 agent 能更可靠地 observe、act、recover、verify、guard 和 learn。

更具体地，它需要满足以下条件。

### 条件 1：State-grounded，而非 static instruction

环境暴露的信息必须来自当前真实状态：route、DOM、app state、数据库、文件系统、session、window tree、OS setting、form validation、cart state、unsaved changes 等。静态说明 “这个网站通常这样用” 不够。

### 条件 2：Task-agnostic，而非 oracle

可以告诉 agent “当前页面有哪些合法 action / 当前 cart 有哪些 item / 当前文件是否保存”，不能告诉 agent “下一步应该点哪个按钮才能完成当前任务”。这是 friendly 和 cheating 的边界。

### 条件 3：Executable，而非只给文本建议

Agent-friendly affordance 最好对应可执行 action 或可查询 API，例如 `open_cart()`、`restore(checkpoint_id)`、`query_file_state(path)`、`inspect_form_validity(form_id)`。如果只是自然语言建议，和 prompt engineering 区分不大。

### 条件 4：Recoverable / Forkable

环境应支持 checkpoint、rollback、branch、reset、state diff。长程 GUI / web / OS 任务里，agent 最大的问题之一是走错后难以回到干净状态。MobileGym 的 state forking 是这个方向的关键证据。

### 条件 5：Verifiable

环境应提供程序化 verifier、partial credit、progress signal、consistency check，而不是只靠 final screenshot 或 LLM-as-judge。OpenComputer 说明，很多任务成功依赖 hidden state，视觉上正确并不代表功能正确。

### 条件 6：Safe and Permissioned

环境要区分 trusted instruction、untrusted content、user data、external side effects。需要权限边界、敏感动作 confirmation、sandbox、audit log、防 prompt injection。AgentDojo / ToolEmu 说明这是 agent environment 的基础需求，不是安全附加项。

### 条件 7：Cost-efficient for rollout

训练环境必须低成本并行、可快速冷启动、可复用状态快照、避免 screenshot / browser / emulator 成为瓶颈。否则 agent-friendly 只适合 demo，不能支撑 RL 或大规模评测。

## 跨平台 Agent-Friendly Env Protocol

可以把它抽象成一个统一协议：**AFE Protocol**。

```text
observe()  -> screenshot + text tree + semantic state + state diff + provenance
act()      -> primitive GUI action + semantic action + CLI/API/tool action
recover()  -> checkpoint / restore / branch / reset / undo
verify()   -> progress probes / partial credit / final checker / consistency check
map()      -> route graph / app graph / file graph / workflow graph / reachable states
guard()    -> permission / sandbox / untrusted-data boundary / side-effect policy
trace()    -> trajectory log / state delta / action provenance / replay artifact
```

这个协议的价值在于：它把 web、mobile、desktop、tool-use 的共同问题从 “怎么点屏幕” 抽象到 “如何操控一个可验证的状态转移系统”。

### Web AFE

Web 环境天然有 DOM、route、link graph、backend API、database state，因此适合做第一版。

可提供 affordances：

- route / page world map
- DOM / accessibility / component hierarchy
- form schema and validation state
- semantic actions: search, filter, sort, submit, open item, edit record
- backend verifier endpoints: record created, cart updated, permission changed
- session checkpoint / rollback
- untrusted content isolation for prompt injection

核心 failure mode：

- navigation drift
- loop / repeated visits
- hidden backend state mismatch
- form validation missed
- false completion
- prompt injection from page content

### Mobile AFE

Mobile 环境比 Web 更难，因为真实 app backend 不透明、系统权限复杂、手势和跨 app intent 多。但 MobileGym 证明可以用 browser-hosted functional model 建一个轻量 mobile-like world。

可提供 affordances：

- structured app state / OS runtime state
- screen hierarchy / accessibility tree
- app graph / deep link graph / intent graph
- permission / notification / clipboard / account state
- gesture abstraction: tap, swipe, long press, drag, type
- checkpoint / fork / compare structured JSON state
- deterministic verifier and AnswerSheet-like protocol

核心 failure mode：

- 手势 grounding 错误
- 权限弹窗 / 系统 modal 打断
- 跨 app 状态丢失
- back stack 迷路
- notification / background state 不可见

### Desktop / OS AFE

Desktop AFE 的关键不是像素，而是多应用、多文件、多进程、多窗口、多工具状态一致性。OpenComputer 是最接近的起点。

可提供 affordances：

- window tree / active app / focus state
- filesystem graph / dependency graph / recent files
- process state / app config / plugin state
- GUI + CLI + API hybrid action space
- app-specific verifiers
- VM/container snapshot restore
- trajectory replay and state diff

核心 failure mode：

- 文件改错路径
- app 内 hidden state 没保存
- GUI 看起来成功但 backend / file metadata 错误
- 多窗口焦点错误
- CLI 绕过 GUI 造成 reward hacking

### Tool-use / MCP AFE

Tool-use env 可以看作没有 GUI 的 agent-friendly environment。这里的关键是 typed schema、stateful database、user simulator、安全边界。

可提供 affordances：

- typed tool schema and state transition contract
- tool dependency graph
- stateful database inspection
- dual-control user simulator
- side-effect sandbox
- attack / defense test harness

核心 failure mode：

- tool call 参数错误
- 用户和 agent 同时修改状态导致 coordination failure
- untrusted tool output 注入恶意指令
- irreversible side effects

## Key Insight

### Insight 1：Agent-friendly env 不是“更简单的环境”，而是“更好的接口”

这个概念最容易被误解成让任务变简单。更准确地说，它保留任务目标和真实状态转移，只移除对 agent 来说非本质的摩擦：状态不可见、动作粒度过低、错误不可恢复、结果不可验证、安全边界不清。

这类似人类使用 IDE、浏览器开发者工具、undo、history、debugger、file diff，并不代表任务答案被泄露，而是环境提供了适合问题求解的 instrumentation。

### Insight 2：跨 web / mobile / OS 的共同抽象是 state transition，而不是 pixel UI

MobileGym 的核心启发可以泛化：pixel-perfect 不是首要目标，**state transition fidelity** 才是。Web 的 route / DOM / backend state，Mobile 的 app / OS runtime state，Desktop 的 file / process / app state，本质上都是状态转移系统。

因此，研究目标不应是做三个互不相干的 simulator，而是做一套跨平台 environment protocol：observe state、execute action、recover branch、verify outcome。

### Insight 3：Verifier 是环境的一部分，不是评测脚本的尾巴

OpenComputer 和 MobileGym 都说明，谁来判断成功是环境设计的核心。没有 verifier，agent-friendly affordance 很容易变成“模型自我感觉良好”。有 verifier，环境才能给 partial credit、progress signal、RL reward、debug trace。

所以 AFE 的最小闭环不是 UI + action，而是：

```text
state -> affordance -> action -> transition -> verifier -> feedback
```

### Insight 4：Friendly 的关键收益应体现在 failure-mode reduction

如果只看 task success，容易被质疑是 prompt / model / task variance。AFE 应该证明自己减少了特定失败：

- navigation drift 降低
- loop / repeated action 降低
- hidden-state mismatch 降低
- false completion 降低
- wrong-turn recovery 提升
- verifier mismatch 降低
- unsafe side effect 降低

这些 failure-mode 指标比最终成功率更能说明环境设计的因果作用。

### Insight 5：Prompt-only baseline 是必需的

这个方向必须正面对比 “直接给更多 prompt”。实验上至少需要：

- Normal env
- Static prompt with site/app/system instructions
- Dynamic prompt with current-page summary
- AFE observation-only
- AFE + world map
- AFE + rollback
- AFE + semantic action
- AFE + verifier / progress signal

如果 AFE 的收益主要来自 executable / recoverable / verifiable affordances，而 prompt-only 不能达到同样结果，才说明不是 trivial prompt engineering。

### Insight 6：资源优势来自 zero-training 和小环境闭环

WebGym / AsyncWebRL 已经把 large-scale RL 走通，但这条路资源消耗大。AFE 可以选择不同切入点：**同一批任务、同一模型、zero-training，只改变环境 affordances**。

这样第一版不需要 24 H100 或几十万任务。可以先做 3 类 self-hosted env：

- Web：shopping / issue tracker / forum，各 20-30 tasks
- Mobile：MobileGym-like functional apps，20-40 tasks
- Desktop：file / office / browser / terminal hybrid，20-40 tasks

主要成本是 per-platform adapter 和 verifier，而不是模型训练。

## 研究设想：Agent-Friendly Environment Protocol for Computer-Use Agents

### Motivation

当前 GUI / web / mobile / OS agent 的瓶颈不只是模型能力，也不是单纯缺训练数据。很多失败来自环境接口不适合 agent：

- agent 看不到 hidden state，只能根据 screenshot 猜测；
- primitive click / type / scroll action 粒度过低；
- 走错后难以恢复，长程任务一次错误毁掉 trajectory；
- 任务完成依赖 backend / file / config state，LLM 自检不可靠；
- web / mobile / desktop 的 benchmark 接口割裂，方法难复用；
- prompt injection、权限、外部副作用缺少统一安全边界。

因此可以提出：**把环境本身 agent-friendly 化，是比继续只训 agent 更高杠杆的路线**。

### Core Claim

> 在相同模型、相同任务、zero-training 条件下，Agent-Friendly Environment 通过 state-grounded affordances、recoverable control、semantic action layer 和 programmatic verification，可以显著提升 computer-use agent 的完成率与可靠性；其收益不能被 prompt-only guidance 完全替代。

### Key Idea

构建一个跨平台 AFE Protocol，在 web / mobile / desktop 三类环境中实现同构接口：

- `observe_state()`：返回 screenshot + text tree + structured state + state diff
- `get_world_map()`：返回 route / app / file / workflow graph
- `list_affordances()`：返回当前状态下合法 semantic actions
- `act(action)`：支持 primitive GUI action 与 semantic action
- `checkpoint()` / `restore()` / `branch()`：支持错误恢复和探索
- `verify(probe)`：返回 task-agnostic progress / consistency signal
- `guard(action)`：检查权限、敏感副作用、untrusted data
- `trace()`：记录可回放 trajectory 和 state deltas

Human UI 不变；agent 获得额外 runtime protocol。

### 实验设计

| Condition | 环境能力 | 目的 |
|:--|:--|:--|
| C0 Normal | screenshot / DOM / primitive actions | 普通 baseline |
| C1 Static Prompt | 静态网站 / app / OS 使用说明 | 测 prompt engineering |
| C2 Dynamic Prompt | 当前页面摘要 / 附近链接 / 当前窗口摘要 | 测动态文本观察 |
| C3 AFE-Observe | structured state / state diff | 测状态可见性 |
| C4 AFE-Map | world map / app graph / file graph | 测导航支撑 |
| C5 AFE-Recover | checkpoint / rollback / branch | 测错误恢复 |
| C6 AFE-Action | semantic actions / hybrid GUI-API-CLI | 测动作空间 |
| C7 Full AFE | observe + map + recover + action + verifier + guard | 测完整系统 |

### 指标

最终指标：

- task success rate
- partial credit
- steps / tokens / wall-clock time
- cost per successful task

failure-mode 指标：

- navigation drift rate
- loop / repeated action rate
- wrong-turn recovery rate
- false completion rate
- hidden-state mismatch rate
- verifier mismatch rate
- unsafe side-effect rate
- rollback usage and success

效率指标：

- cold start time
- memory per instance
- parallel rollout throughput
- verifier latency
- screenshot / observation bandwidth

### 最小可行版本

第一版不要贪大。建议做一个 **AFE-MiniSuite**：

1. Web env：一个 shopping + 一个 issue tracker，共 40 tasks。
2. Mobile env：基于 MobileGym 思想做 8-10 个 everyday mobile apps，共 40 tasks。
3. Desktop env：文件管理 + 文档编辑 + 浏览器 + terminal，共 30 tasks。

每个平台都实现同一组最小接口：

- state snapshot
- world / app / file map
- checkpoint / rollback
- semantic action candidates
- programmatic verifier
- trace + state diff

第一篇论文的目标不是训练 SOTA agent，而是证明：

```text
Normal < Prompt-only < AFE-observe/map/recover/action < Full AFE
```

并且提升主要来自可解释的 failure-mode reduction。

## Open Problems

### 1. Allowed Affordance Boundary 如何形式化

这是最大挑战。必须明确哪些 affordance 允许、哪些算 oracle。

允许：

- 当前状态
- 合法动作列表
- 页面 / app / 文件结构
- 状态 diff
- field validity
- undo / rollback
- task-agnostic progress probe

不允许：

- gold next action
- gold trajectory
- task-specific macro action
- direct task complete flag
- 为当前任务特制的 shortcut

这个边界需要写成协议和测试，而不是靠口头解释。

### 2. 如何证明不是 prompt engineering

必须做强 prompt-only baseline。甚至可以把 AFE 返回的信息原样序列化进 prompt，但禁用 executable API / rollback / verifier，观察是否仍不如 Full AFE。

如果收益只来自更多文字，方向就不成立；如果收益来自 action / recovery / verification，就成立。

### 3. 如何避免变成 RPA / hand-crafted skills

如果每个网站、每个 app 都手写 skill，那研究性会弱。需要让 affordance 尽量来自通用结构：

- Web：route definitions、DOM roles、form schema、API endpoints、DB schema
- Mobile：accessibility tree、app state schema、intent / deep link、OS runtime state
- Desktop：window tree、filesystem、app automation API、config DB、process state
- Tool-use：tool schema、state DB、permission spec

第一版可以半自动，但必须区分 protocol generality 和 per-env adapter。

### 4. 如何处理真实环境漂移

Live web / real app 会有广告、A/B test、登录、地理位置、推荐流、schema migration。AFE 初期不应该承诺全覆盖。更合理的是先在 self-hosted but realistic environments 证明因果，再逐步接入真实环境。

### 5. 如何同时服务 evaluation 和 training

Evaluation 需要严格、不可泄露、可复现；training 需要密集反馈、并行 rollout、partial reward。二者对 affordance 暴露程度可能不同。需要定义：

- eval mode：更少 hint，更严格 verifier
- train mode：允许 progress probes / partial credit
- debug mode：允许 richer state diff / trace

### 6. 如何设计安全边界

AFE 让 agent 更能行动，也放大了风险。因此必须内建：

- least privilege
- side-effect classification
- sensitive-action confirmation
- untrusted content separation
- prompt injection defense
- audit log
- rollback / containment

否则 agent-friendly 只是在提高危险动作的执行效率。

## 建议加入 DomainMaps

- GUI Agent DomainMap 可新增一个方向：**Environment / Harness Design**，与 Grounding / RL / Self-Improving 并列。
- WorldModel DomainMap 可补充：**AFE 把 world model 从 neural prediction 转成 executable state-transition infrastructure**，和 MobileGym / OpenComputer 形成连接。
- AgenticRL DomainMap 可补充：**Verifier-first + forkable environment 是 RL scaling 的前置条件**。

## 外部来源

- [[2412-BrowserGymAgentLab]]
- [AgentGym: Evolving Large Language Model-based Agents across Diverse Environments](https://arxiv.org/abs/2406.04151)
- [WebGym: Scaling Training Environments for Visual Web Agents with Realistic Tasks](https://arxiv.org/abs/2601.02439)
- [MobileGym: A Verifiable and Highly Parallel Simulation Platform for Mobile GUI Agent Research](https://arxiv.org/abs/2605.26114)
- [OpenComputer: Verifiable Software Worlds for Computer-Use Agents](https://arxiv.org/abs/2605.19769)
- [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972)
- [AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents](https://arxiv.org/abs/2405.14573)
- [Windows Agent Arena: Evaluating Multi-Modal OS Agents at Scale](https://arxiv.org/abs/2409.08264)
- [MobileWorld: Benchmarking Autonomous Mobile Agents in Agent-User Interactive, and MCP-Augmented Environments](https://arxiv.org/abs/2512.19432)
- [ToolEmu: Identifying the Risks of LM Agents with an LM-Emulated Sandbox](https://arxiv.org/abs/2309.15817)
- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352)
- [τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment](https://arxiv.org/abs/2506.07982)

## 调研日志

- **调研日期**: 2026-06-23
- **论文统计**: vault 已有 MobileGym / OpenComputer / OS Agents Survey / GUI Environment Survey / WebGym / AsyncWebRL 等；外部增量检索 BrowserGym、AgentGym、OSWorld、AndroidWorld、Windows Agent Arena、MobileWorld、ToolEmu、AgentDojo、τ²-Bench
- **未能获取**: 无；本轮以摘要级调研和本地已有笔记综合为主，未逐篇完整 digest
- **核心发现**: agent-friendly env 目前不是成熟术语，但已有工作共同指向一个可定义的新方向：把 web / mobile / desktop / tool-use 环境统一为 state-grounded、recoverable、verifiable、safe、cost-efficient 的 agent runtime protocol
