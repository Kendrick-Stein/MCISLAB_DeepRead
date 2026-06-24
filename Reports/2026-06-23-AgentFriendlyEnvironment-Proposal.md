---
title: Agent-Friendly Environment 简短 Proposal
date: 2026-06-23
tags: [proposal, gui-agent, environment, computer-use, research-idea]
sources:
  - "[[2605-MobileGym]]"
  - "[[2601-WebGym]]"
  - "[[2606-AsyncWebRL]]"
  - "[[2600-WebHarbor]]"
  - "[[2606-CUAGym]]"
  - "[[2605-SaaSBench]]"
  - "[[2605-OpenComputer]]"
  - "[[2606-WeaveBench]]"
  - "[[Reports/2026-06-23-WebGym-AsyncWebRL]]"
  - "[[Reports/2026-06-23-AgentFriendlyWebRuntime]]"
  - "[[Topics/AgentFriendlyEnvironment-Survey]]"
  - "Gym-Anything: https://arxiv.org/abs/2604.06126"
  - "Odysseys: https://arxiv.org/abs/2604.24964"
  - "[[2412-BrowserGymAgentLab]]"
---

# Agent-Friendly Environment 简短 Proposal

## 历史对话总结

我们最开始从 GUI 领域未来方向出发，判断 GUI Agent 正在从 **model-first** 走向 **environment / verifier / harness-first**：继续只做更大的 VLM 或普通 GUI agent，边际 insight 会变弱；更关键的问题是如何构建可验证、可恢复、可并行、能支持 RL 和真实任务诊断的环境 [[Reports/2026-06-23-GUI-Future-Directions]]。

随后我们讨论 [[2605-MobileGym]]。MobileGym 的关键 insight 不是把手机界面做得 pixel-perfect，而是通过 JSON state、EFSM transition、state forking 和 deterministic verifier 建一个轻量、可验证、可并行的 mobile GUI simulator。它证明 everyday mobile GUI 任务里，**interaction / state transition fidelity 比像素级仿真更重要** [[2605-MobileGym]]。

但我们进一步澄清了一个重要点：MobileGym 虽然内部有 JSON state、fork、verifier，但这些主要服务于环境构建、重置、判分和 RL。对 agent 来说，它看到的仍主要是 screenshot，并执行 tap / swipe / type 等 primitive GUI actions。因此 MobileGym 更准确地说是 **training-friendly / verifier-friendly environment**，还不是完整的 **agent-friendly environment** [[2605-MobileGym]]。

接着我们读了 [[2601-WebGym]] 和 [[2606-AsyncWebRL]]。WebGym 已经把 large-scale web tasks、rubric evaluator、online RL 和高吞吐 rollout 走通；AsyncWebRL 又通过 fully async rollout、lightweight screenshot handling 和 loss normalizer 修复提升训练效率。也就是说，“更多任务 + 更快 RL” 这条 web agent scaling 路线已经被强工作占住了 [[2601-WebGym]] [[2606-AsyncWebRL]]。

所以我们 pivot 到另一个方向：与其继续训练 agent 去适应普通 browser，不如构建 **agent-friendly browser / web server / environment**。同一个模型在 zero-training 下，如果获得 state-grounded、可执行、可恢复、可验证的环境 affordance，可能比在普通浏览器上完成得更好 [[Reports/2026-06-23-AgentFriendlyWebRuntime]]。

最后我们把 browser 扩展成更一般的 **Agent-Friendly Environment**：Web / Mobile / Desktop / Tool-use 都可以被设计成 dual-interface runtime。人类仍看正常 UI，agent 则额外获得 task-agnostic、state-grounded、executable、recoverable、verifiable、safe、cost-efficient 的 affordances [[Topics/AgentFriendlyEnvironment-Survey]]。

2026-06-24 新增调研后，判断需要进一步细化：环境路线已经快速拥挤。[[2600-WebHarbor]] 做真实网站 Docker mirror，[[2606-CUAGym]] 做 verifiable RLVR tuple 合成，[[2605-SaaSBench]] 做真实 SaaS 长程评测，Gym-Anything / CUA-World 做任意软件环境化，Odysseys 做 live open-web 长程评测，BrowserGym 做 web agent harness 标准化。这说明“构建一个新环境”本身不再足够；更清晰的空白是 **agent-facing environment protocol**：把已有环境后端的 state/reset/verifier 能力，以非作弊方式变成 agent 可使用的 runtime affordance。

## 核心判断

当前 GUI / web / mobile / OS agent 的失败，不只是模型能力不足，也来自 **环境接口不适合 agent**：

- agent 主要看到 screenshot，却看不到 hidden state；
- action space 停留在低级 click / swipe / type，步骤长且易错；
- 走错后没有可靠 rollback，长程任务一次错误会污染整条 trajectory；
- 完成状态依赖 backend / file / app state，但 agent 只能自我判断；
- 评测和训练往往缺少程序化 verifier，reward hacking 难发现；
- prompt 可以解释流程，但不能提供真实状态、可执行动作、恢复控制和状态验证。

因此，下一步不一定是“做更强 agent”，而是 **重新设计 agent 与环境之间的接口**。

更全面地看，当前 Computer-use/Web Environment 工作可以按两条轴划分：

| 类型 | 代表 | 主要解决 | 仍留下的空白 |
|:--|:--|:--|:--|
| Live/open-web eval | WebVoyager, WebCanvas, Odysseys | 真实网页、跨站、内容漂移 | 不可 reset，不适合 RL，reward 多为 rubric |
| Unified harness | BrowserGym, WorkArena++ | 统一 observation/action 与 benchmark 管理 | 不改变 app 对 agent 的 affordance |
| Self-hosted SaaS/web | WebArena, SaaS-Bench, TheAgentCompany | 可复现真实 workflow 和 backend state | verifier 多在事后，不参与 agent 执行 |
| Local mirrors | WebHarbor | 把真实网站变成本地 Docker mirror，支持快速 reset | 主要解决环境来源，不定义 agent-facing protocol |
| Synthetic/mock env | InfiniteWeb, CUA-Gym-Hub | 大规模生成可控 web apps 和 tasks | realism/transfer 需证明，state API 多给 trainer/reward |
| Verifier worlds | MobileGym, OpenComputer, Gym-Anything | 程序化 verifier、state reset/fork、partial credit | 多数 verifier 不直接帮助 agent 运行时决策 |
| Hybrid native runtime | WeaveBench, ALE, WildClawBench | GUI+CLI+Code/native harness 长程任务 | 评测强，但 agent-facing recovery/control 仍弱 |

所以 proposal 应避免和 WebHarbor/CUA-Gym/Gym-Anything 正面竞争“谁能造更多环境”。更值得做的是研究：**当环境已经有 state API、reset、verifier、action graph 后，哪些能力应该暴露给 agent，暴露到什么粒度才不是 oracle？**

## Proposal

### Title

**Agent-Friendly Environment Protocol for Computer-Use Agents**

### Motivation

MobileGym 证明 functional simulation 的价值，但它的结构化状态主要在环境后台，agent-facing observation 仍然接近普通 GUI screenshot [[2605-MobileGym]]。WebGym / AsyncWebRL 证明大规模 RL 可行，但资源重，且主要依赖 rubric evaluator，而不是 deterministic state verifier [[2601-WebGym]] [[2606-AsyncWebRL]]。OpenComputer 则说明程序化 state verifier 比 LLM judge 更可靠，verification 应该成为环境设计的一等公民 [[2605-OpenComputer]]。

新增的 WebHarbor / CUA-Gym / SaaS-Bench 强化了这个判断，但也改变了选题边界：

- [[2600-WebHarbor]] 说明 web 环境可以通过 Docker mirror 变得 stable、login-free、resettable，同时保留真实网站视觉和深功能。
- [[2606-CUAGym]] 说明 task、environment state、reward.py 可以共同合成，110 个环境和 32K+ verified tuples 已经能支撑开源 CUA RLVR。
- [[2605-SaaSBench]] 说明在真实 SaaS 中，agent 的问题不是“完全不能做”，而是 checkpoint 能推进但 resolved workflow 崩溃，核心失败是 state tracking、schema grounding 和 error recovery。
- Gym-Anything 说明“把任意软件环境化”正在被自动化，environment construction 作为 multi-agent task 也会变成一条强路线。

这些工作共同提示一个更窄但更硬的空白：**我们缺少一种跨 Web / Mobile / Desktop 的 agent-facing environment protocol，让环境把状态、动作、恢复、验证和安全边界以非作弊的方式暴露给 agent**。换句话说，环境后台已经越来越强，但 agent 运行时仍像盲人一样主要靠 screenshot / DOM / prompt 试错。

### Challenge

1. **不是 oracle**：环境可以暴露当前状态、合法动作、world map、field validity、checkpoint，但不能暴露 gold next action、gold trajectory 或 task-specific macro。
2. **不是 prompt engineering**：必须证明 runtime affordance 优于 static / dynamic prompt-only baseline；关键差异应来自可执行、可恢复、可验证的环境能力。
3. **不是 RPA**：semantic actions 和 skills 不能为每个任务手写 shortcut，应从 route、DOM、accessibility tree、app schema、file graph、API schema 等通用结构生成。
4. **跨平台统一**：Web、Mobile、Desktop 的底层状态不同，但应共享 observe / act / recover / verify / map / guard / trace 的协议抽象。
5. **安全与副作用**：agent-friendly 让 agent 更能行动，也会放大风险；必须内建 permission、sandbox、untrusted-content separation、audit log 和 rollback。
6. **不是 evaluator API 泄漏**：CUA-Gym / OpenComputer 式 verifier 可以给 reward，但若直接给 agent，就可能变成 answer oracle。需要区分 evaluator-only API、agent-safe state probe、task-specific hidden verifier 三层。

### Key Idea

构建一个 **dual-interface environment**：

- Human 看到正常网页、手机界面或桌面应用。
- Agent 除了 screenshot / DOM / accessibility tree，还可以调用一组 task-agnostic runtime affordances。

最小协议包括：

```text
observe_state()      -> structured current state + visible UI + state diff
get_world_map()      -> route graph / app graph / file graph / workflow graph
list_affordances()   -> 当前状态下可执行的 semantic actions
act(action)          -> primitive GUI action 或 semantic action
checkpoint/restore() -> 保存、回滚、分支探索
verify(probe)        -> progress signal / partial credit / consistency check
guard(action)        -> 权限、风险、副作用、安全边界检查
trace()              -> trajectory replay + state delta + action provenance
```

这不是把更多网站说明塞进 prompt，而是改变 agent 的 **observability / controllability / verifiability**。

## 最小实验

第一版可以做一个小型 **AFE-MiniSuite**：

建议从 Web-only 或 Web+Desktop-light 开始，降低工程风险：

- Web：复用 WebHarbor mirror 或 CUA-Gym-Hub mock apps，shopping + issue tracker + document/workspace app，约 40-60 tasks。
- Optional Desktop：复用 OpenComputer-style file manager / office/browser 任务，约 20 tasks。
- 暂缓 Mobile：MobileGym 已有强环境，第一版不需要跨三平台，否则 scope 过大。

对照条件：

| Condition | 描述 |
|:--|:--|
| C0 Normal | 普通 screenshot / primitive action |
| C1 Static Prompt | 写入网站 / app / OS 使用说明 |
| C2 Dynamic Prompt | 每步给当前页面摘要，但不提供特殊 action |
| C2.5 Evaluator-only API | state/verifier 只用于判分，不给 agent |
| C3 AFE-Observe | 暴露 structured state / state diff |
| C4 AFE-Map | 加 world map / app graph / file graph |
| C5 AFE-Recover | 加 checkpoint / rollback / branch |
| C6 AFE-Action | 加 task-agnostic semantic actions |
| C7 Full AFE | observe + map + recover + action + verifier + guard |

核心指标不只看 success rate，还要看：

- navigation drift rate
- repeated action / loop rate
- false completion rate
- hidden-state mismatch rate
- wrong-turn recovery rate
- verifier mismatch rate
- unsafe side-effect rate
- steps / tokens / time / cost per success
- state-probe leak rate
- semantic-action shortcut rate
- reset / rollback latency
- evaluator-only vs agent-facing gain gap

关键实验不是“Full AFE 分数最高”这么简单，而是要证明不同 affordance 对不同 failure mode 有选择性因果作用：

- Observe/state diff 应降低 hidden-state mismatch。
- Map 应降低 navigation drift 和 loops。
- Recover 应提升 wrong-turn recovery。
- Progress signals 应降低 false completion。
- Semantic action 应降低 grounding/execution error，但不能显著提高 shortcut rate。

## 预期贡献

如果实验成立，这个工作可以贡献三件事：

1. **定义**：提出什么是 Agent-Friendly Environment，并给出 allowed affordance boundary。
2. **协议**：提出跨 Web / Mobile / Desktop 的 observe / act / recover / verify / map / guard / trace runtime protocol。
3. **证据**：证明在 zero-training 条件下，agent-friendly affordances 可以显著降低 execution failure，并且这种收益不能被 prompt-only guidance 完全替代。
4. **边界**：区分 evaluator-only verifier、agent-safe state probe、oracle/cheating signal，给出可操作的安全暴露规范。

一句话总结：

> WebHarbor / CUA-Gym / OpenComputer / MobileGym 证明环境后台可以被 functional、verifiable、resettable、scalable 化；我们要进一步证明，若把这些能力以非作弊方式变成 agent-facing affordances，就能让 computer-use agent 在不训练的情况下更可靠地完成任务。

## 更新后的选题定位

更推荐把题目从泛泛的 **Agent-Friendly Environment Protocol** 收窄为：

**Agent-Facing Environment Protocol: Safe Runtime Affordances for Reliable Computer-Use Agents**

这个标题强调三点：

- **Agent-facing**：区别于 CUA-Gym / OpenComputer 的 evaluator/trainer-facing verifier。
- **Safe runtime affordances**：区别于 prompt engineering，也避免被理解成 task-specific oracle。
- **Reliable computer-use**：目标是降低 execution failure，而不是追求更大 benchmark 或更强模型。

第一篇 paper 可以只做 Web，因为 WebHarbor/CUA-Gym-Hub 已经提供足够好的环境底座。跨 Mobile/Desktop 可以作为 protocol generalization，而不是第一版实验负担。
