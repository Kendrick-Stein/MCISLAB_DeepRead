---
title: GUI Environment 近期工作调研与 Agent-Facing Runtime 选题更新
date: 2026-06-24
tags: [report, gui-agent, computer-use, environment, benchmark, verifier, research-strategy]
based_on:
  - "[[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]]"
  - "[[Reports/2026-06-23-AgentFriendlyWebRuntime]]"
  - "[[Topics/GUI-Environment-Survey]]"
sources:
  - "[[2605-MobileGym]]"
  - "[[2605-OpenComputer]]"
  - "[[2606-WeaveBench]]"
  - "[[2606-CUAGym]]"
  - "[[2605-SaaSBench]]"
  - "[[2600-WebHarbor]]"
  - "[[2604-WindowsWorld]]"
  - "[[2605-WorkspaceBench]]"
  - "[[2601-WebGym]]"
  - "[[2606-AsyncWebRL]]"
  - "[[2600-InfinitewebScalableWebEnvironment]]"
  - "[[2604-AgentWorld]]"
  - "[[2605-EnvFactory]]"
  - "[[2509-DARTGUI]]"
  - "[[2606-RHO]]"
  - "[[2606-Harness1]]"
  - "[[2508-ComputerRL]]"
  - "OSWorld: https://arxiv.org/abs/2404.07972"
  - "[[2412-BrowserGymAgentLab]]"
  - "WorkArena: https://arxiv.org/abs/2403.07718"
  - "WorkArena++: https://arxiv.org/abs/2407.05291"
  - "Gym-Anything: https://arxiv.org/abs/2604.06126"
  - "MyPCBench: https://arxiv.org/abs/2606.16748"
  - "GUI-360: https://arxiv.org/abs/2511.04307"
  - "Plan-Then-Execute Web Agents: https://arxiv.org/abs/2605.14290"
  - "EnvTrustBench: https://arxiv.org/abs/2605.08828"
  - "AUI-Gym: https://arxiv.org/abs/2511.15567"
  - "VeriEnv: https://arxiv.org/abs/2603.10505"
  - "WebFactory: https://arxiv.org/abs/2603.05044"
  - "OSWorld-Human: https://arxiv.org/abs/2506.16042"
  - "Windows Agent Arena: https://arxiv.org/abs/2409.08264"
  - "TheAgentCompany: https://arxiv.org/abs/2412.14161"
---

# GUI Environment 近期工作调研与 Agent-Facing Runtime 选题更新

## 一句话结论

近期 GUI / computer-use environment 工作正在从 **benchmark construction** 快速转向 **runtime infrastructure**：可 reset、可验证、可并行、可合成、可诊断、可审计，已经成为强工作共识。基于 [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]]，新的选题边界需要进一步收窄：

> 不要再泛泛做一个 GUI environment；更有价值的是研究 **已有环境后台的 state / verifier / reset / action graph 能力，如何以 non-oracle、agent-facing、可审计的 runtime affordance 暴露给 agent，并证明它能因果性降低特定 failure mode**。

这不是“环境更大”或“任务更多”的问题，而是 **环境能力暴露边界** 的问题。

---

## 1. 近期工作全景

### 1.1 统一 Harness / 基础 OS 环境

这一类工作解决“agent 到底在什么接口上跑”的标准化问题。

| 工作 | 核心环境 | 规模 / 特点 | 主要贡献 | 仍留下的空白 |
|:--|:--|:--|:--|:--|
| OSWorld | real computer env | 369 任务，Ubuntu/Windows/macOS | open-ended desktop task setup + execution-based eval | 早期任务较少，多应用/个人化/混合接口覆盖不足 |
| Windows Agent Arena | real Windows OS | 150+ Windows tasks，可 Azure 并行 | Windows OS 可复现评测，20 分钟级大规模 eval | 更像 OSWorld on Windows，process-level verifier 较弱 |
| BrowserGym / AgentLab | web harness | 统一 observation/action spaces，整合多 benchmark | 降低 web agent benchmark fragmentation | 标准化接口，但不改变 app 本身 affordance |
| ClawGUI | mobile/GUI full-stack | RL / Eval / Deployment 一体；跨 Android/HarmonyOS/iOS | 开源 GUI agent RL 和部署基础设施 | 更偏训练框架，环境 affordance 边界不是主问题 |

**判断**：统一 harness 是必要底座，但它通常只提供“怎么连接环境”，不解决“环境应该给 agent 暴露什么能力”。

### 1.2 真实工作流 / 专业任务环境

这一类工作把环境从 isolated tasks 推向真实工作流。

| 工作 | 场景 | 规模 / 关键数字 | 核心 insight |
|:--|:--|:--|:--|
| WindowsWorld | Windows 跨应用专业流程 | 181 tasks；78% multi-application；best multi-app <21% | 跨应用不是步数问题，而是独立瓶颈 |
| SaaS-Bench | deployable SaaS workflows | 23 SaaS systems，106 tasks；best resolved <4% | checkpoint 可推进，但 end-to-end resolved collapse |
| WorkspaceBench | large file workspace | 388 tasks，20,476 files，74 file types | heterogeneous file understanding / lineage tracing 是 workspace bottleneck |
| TheAgentCompany | software company env | 内部网站、代码、程序、通信；best 24% | 真实公司任务远未自动化 |
| MyPCBench | personalized desktop | 17 simulated web apps + Linux desktop；184 tasks；best 55.4% | personal context / logged-in accounts 是 live web benchmark 缺口 |
| Agents' Last Exam | professional workflows | GDP-relevant 长程任务 | 最难层级 full pass 极低，现实任务未饱和 |

**判断**：真实任务的难点不是“看不懂按钮”，而是 hidden state、跨应用状态维护、个人上下文、文件依赖和错误恢复。Agent-facing environment protocol 必须优先解释这些 failure，而不是只优化视觉 grounding。

### 1.3 Web 环境：从 live web 到 local mirror / synthetic web

Web 是近期最活跃的 GUI environment 子方向。

| 路线 | 代表工作 | 解决什么 | 代价 / 缺口 |
|:--|:--|:--|:--|
| Live/open web | WebVoyager, WebCanvas / Mind2Web-Live, Odysseys | 真实网页、内容漂移、跨站任务 | 不可 reset，难训练，登录/反爬/地理限制 |
| Self-hosted realistic | WebArena, WorkArena, WorkArena++ | 稳定企业/web tasks，functional correctness | 站点少，环境重，reset/scale 有成本 |
| Local mirror | WebHarbor | 把真实网站 dock 成 Docker mirror；15 WebVoyager sites；sub-second reset；计划 100+ | human review 是瓶颈，programmatic verifier 仍不系统 |
| Synthetic web generation | InfiniteWeb, VeriEnv, WebFactory | 自动生成 functional websites、tasks、evaluator/reward | realism / transfer / answer leak 需要证明 |
| RL training web env | WebGym, AsyncWebRL | 近 300K 真实网站任务，大规模 rollout 与 async RL | 资源路线强，reward 多偏 rubric / judge |
| RLVR mock web | CUA-Gym-Hub | 94/99 mock web apps，state API，session isolation，32K+ tuples | state API 主要给 trainer/reward，不是 agent-facing |

**新信号**：

- WebHarbor 证明“把 live web 镜像成本地可 reset 环境”正在成为实用路线。
- VeriEnv / WebFactory / InfiniteWeb 说明“用 agent 造 web environment”正在拥挤。
- Plan-Then-Execute Web Agents 进一步指出 web 的根本问题是 click/type/scroll 缺少 typed semantic interface，主张 typed website APIs。

**对 proposal 的影响**：如果继续说“做 web environment”，已经不够新。需要明确：我们研究的是 **WebHarbor / CUA-Gym / VeriEnv 这类环境背后的 state/verifier/action 能力，哪些可以暴露给 agent，哪些必须留在 evaluator/trainer 后台**。

### 1.4 Verifier-Centric Software Worlds

这一类工作把 verifier 从“评分脚本”提升成环境架构的一等公民。

| 工作 | Verifier 设计 | 关键数字 | 启发 |
|:--|:--|:--|:--|
| OpenComputer | app-specific state verifiers；D-Bus / UNO / SQLite / accessibility / files | 33 apps，1000 tasks；hard-coded verifier-human alignment 94.1% | verifier 是环境组织原则，不是后处理 |
| MobileGym | JSON state + AnswerSheet + deterministic judge | 416 task templates，28 apps；95.1% sim-to-real retained gain | functional state fidelity 比 pixel-perfect 更关键 |
| CUA-Gym | task / initial state / golden state / reward.py co-generation | 32,112 verified RLVR tuples，110 envs | RLVR 需要 task-env-reward 三元组一致 |
| SaaS-Bench | weighted checkpoints | checkpoint score 高，resolved score 低 | partial progress 与 end completion 必须分开 |
| AUI-Gym | programmatic verifier 检查生成 UI 是否可执行 | 52 apps，1560 tasks | UI 设计可转向 agent-native solvability |

**判断**：verifier 已经是共识，但大多数 verifier 仍是 evaluator-facing / trainer-facing。空白不在“有没有 verifier”，而在 **verifier 的 agent-facing 安全暴露方式**。

### 1.5 Hybrid GUI+CLI+Code / Cross-Channel Runtime

这一类工作说明 GUI-only 是错误抽象。

| 工作 | 核心发现 | 对环境设计的要求 |
|:--|:--|:--|
| WeaveBench | GUI-only / CLI-only 崩溃；hybrid +30pp；reward hacking 35.2% | 必须有 trajectory-aware judge、cross-channel evidence、anti-fabrication |
| ComputerRL | API-GUI paradigm；programmatic API + GUI；OSWorld 48.1% | action space 应从 primitive GUI 扩展到 API / tool |
| WorkspaceBench | 从 L2 起 harness 贡献超过 LLM | workspace state / file dependency graph 应成为环境接口 |
| Harness-1 | harness 维护外部 search state，policy 只做 semantic decisions | routine state management 应外部化到环境 |
| RHO | 用 past trajectories 自监督优化 harness；SWE-Bench Pro 59%→78% | harness 本身会演化，是 agent 性能杠杆 |

**判断**：未来 GUI env 不是“屏幕 + 点击”，而是 **GUI / CLI / API / files / logs / browser 的 multi-channel runtime**。Agent-facing protocol 若只做 browser，会少掉真实 CUA 的核心，但第一篇 paper 可以 Web-only，后续必须能解释 hybrid extension。

### 1.6 Safety / Evidence / Trust

这一类工作把环境可靠性从 task success 扩展到证据真实性与安全边界。

| 工作 | 问题定义 | 对 AFE 的约束 |
|:--|:--|:--|
| EnvTrustBench | agent 过度信任 stale / incorrect / malicious environment evidence，导致 evidence-grounding defects | agent-facing state probe 必须带 provenance、freshness、authority |
| Plan-Then-Execute Web Agents | ReAct 把不可信 web content 放进 action synthesis path，易被 prompt injection 控制 | typed / auditable website APIs，限制 runtime action synthesis |
| WeaveBench | outcome-only judge 高估，agent 会 fake render / hardcode metric | 需要 trajectory evidence 与 shortcut detection |
| MyPCBench | personal context / logged-in apps 是真实 assistant 核心 | agent-friendly 不能绕开 privacy / permission / sandbox |

**判断**：AFE 不能只是让 agent 更强；它必须让 agent 的行动更可控、更可审计。否则“友好接口”会变成更强的副作用放大器。

---

## 2. 近期工作的共同模式

### Pattern 1：环境研究从 realism vs scalability 变成四轴竞争

旧问题是：真实环境难 scale，合成环境不真实。

现在更准确的四轴是：

| 轴 | 低端 | 高端 | 代表工作 |
|:--|:--|:--|:--|
| Realism | toy/mock | professional/personal/workplace | SaaS-Bench, MyPCBench, TheAgentCompany |
| Controllability | live不可控 | deterministic reset/fork/session isolation | MobileGym, CUA-Gym, WebHarbor |
| Verifiability | LLM judge / final answer | programmatic verifier / partial credit / trajectory-aware judge | OpenComputer, WeaveBench, CUA-Gym |
| Agent-facingness | evaluator-only backend | safe runtime affordances | 目前仍稀缺 |

第四轴是当前最有机会的空白。

### Pattern 2：环境后台越来越强，但 agent 仍在盲操

大量工作已经有 backend state、reset、golden state、verifier、session isolation、trajectory logs。但这些能力大多不进入 agent 的 action loop：

- CUA-Gym 的 state API 主要用于 setup/reward/parallel rollout。
- OpenComputer 的 verifier 主要用于 task checker 和 partial reward。
- MobileGym 的 JSON state 主要用于 simulation、forking 和 AnswerSheet。
- WebHarbor 的 reset/control plane 主要用于环境管理。

这说明 proposal 的 framing 应从 “agent-friendly environment” 改成更精确的：

> **Agent-facing exposure of environment backend capabilities.**

### Pattern 3：真实 failure mode 指向 state / evidence / recovery，而不是单纯 grounding

近期 benchmark 的共同失败：

- WindowsWorld：跨应用上下文切换和 early sub-goal failure。
- SaaS-Bench：checkpoint progress 与 final resolved collapse。
- WeaveBench：reward hacking、fabricated evidence、premature halt。
- WorkspaceBench：文件依赖和 lineage tracing。
- MyPCBench：个人上下文、多应用和长轨迹。
- EnvTrustBench：环境证据过度信任。

因此 AFE 的指标不能只看 success rate。必须测：

- hidden-state mismatch
- evidence-grounding defect
- cross-channel state drift
- wrong-turn recovery
- false completion
- reward hacking / shortcut rate
- unsafe side-effect rate
- evaluator-only vs agent-facing gain gap

### Pattern 4：Semantic action / typed API 正在成为显性竞争点

Plan-Then-Execute Web Agents 已经明确指出：web agent 的问题不是一定要更 reactive，而是 click/type/scroll 太低级，缺少 typed website APIs。ComputerRL 也把 API-GUI paradigm 作为核心。

这会直接威胁 AFE proposal 的 novelty：如果只说 semantic actions，就会和 typed API 工作重叠。

需要差异化为：

- 不只是 semantic action；
- 还包括 state diff、rollback、progress verification、guard、trace provenance；
- 更关键是 allowed affordance boundary 和 causal ablation。

### Pattern 5：Personalization 是下一波 realism

MyPCBench 提醒：真实 personal assistant 要操作登录态、个人历史、私有数据和跨 app context。Live web benchmark 往往避免这些，因为不可公开、不可复现、难安全。

这给 AFE 带来新约束：

- environment state 不只是 app state，也是 user state；
- state probe 必须有 privacy tier 和 permission；
- verifier 不能泄漏个人答案；
- rollback / audit log 是 personal CUA 的部署前提。

---

## 3. 对 6/23 Proposal 的更新

### 3.1 原 proposal 仍成立的部分

[[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]] 的核心判断仍然成立：

- 继续做更大模型或更大 benchmark 的边际 insight 下降。
- environment / verifier / harness-first 是 GUI Agent 的核心趋势。
- prompt-only guidance 不能替代 state-grounded、recoverable、verifiable runtime affordances。
- evaluator-only verifier 与 agent-facing verifier 必须区分。

### 3.2 需要收窄的部分

原 proposal 仍有一点过宽：“跨 Web / Mobile / Desktop 的 Agent-Friendly Environment Protocol” 容易被理解成又一个大框架。

近期工作说明，跨平台第一版风险太大：

- Web 有 WebHarbor / CUA-Gym-Hub / VeriEnv / WebFactory / InfiniteWeb，底座最成熟。
- Mobile 有 MobileGym，functional simulator 已经强。
- Desktop 有 OpenComputer / WindowsWorld / WeaveBench / MyPCBench，但工程和评估复杂度更高。

更合理的第一篇 paper：

> **Safe Agent-Facing Web Runtime: Exposing Non-Oracle Environment Affordances for Reliable Computer-Use Agents**

Web-only 起步，贡献点不是 web environment 本身，而是：

1. allowed affordance boundary；
2. evaluator-only vs agent-facing 对照；
3. failure-mode causal ablation；
4. 安全暴露规范。

### 3.3 新增关键对照

旧 proposal 有 C0-C7 对照，但现在需要新增两个强 baseline：

| Condition | 目的 |
|:--|:--|
| C2.6 Serialized AFE Prompt | 把 AFE 返回的信息原样文本化塞进 prompt，但禁用 executable API / rollback / verifier；证明不是信息量本身 |
| C2.7 Typed API Only | 只提供 typed semantic actions，不提供 state diff / rollback / verifier；对照 Plan-Then-Execute / typed website API 路线 |
| C3.5 Agent-Facing State Probe w/ Provenance | state probe 必须返回 source、timestamp、authority、freshness；对照 EnvTrustBench |
| C5.5 Guarded Rollback | rollback 与 high-risk action guard 绑定，测 unsafe side-effect |

### 3.4 新增评估指标

除了 success rate / partial credit，建议加入：

| 指标 | 对应 failure mode |
|:--|:--|
| evidence-grounding defect rate | EnvTrustBench 式 stale / wrong / malicious evidence |
| cross-channel drift rate | WeaveBench / WorkspaceBench 式 GUI-file-CLI 不一致 |
| recovery latency | 走错后恢复所需 steps / tokens |
| state probe leak rate | agent-safe probe 是否间接泄露答案 |
| typed-action shortcut rate | typed action 是否退化为 task-specific macro |
| evaluator-agent gap | verifier 只判分 vs verifier 参与执行的收益差 |
| personalization leakage risk | MyPCBench 式个人数据场景下是否泄漏无关 state |

---

## 4. 新报告下的研究机会排序

### P0：Agent-Facing Web Runtime Boundary

**问题**：WebHarbor / CUA-Gym / VeriEnv / WebFactory 都在造 web environments，但没有系统回答哪些 environment backend capability 能安全暴露给 agent。

**最小实验**：

- 环境：WebHarbor 2-3 个 mirror 或 CUA-Gym-Hub 2-3 个 mock apps。
- 任务：40-60 个 shopping / issue tracker / document/workspace web tasks。
- 对照：Normal、Static Prompt、Dynamic Prompt、Serialized AFE Prompt、Typed API Only、Evaluator-only API、AFE Observe/Map/Recover/Action/Verifier/Guard。
- 目标：证明收益来自 executable / recoverable / verifiable affordance，而不是更多文字说明。

**为什么 P0**：这是和当前 proposal 最一致、工程可控、差异化仍清楚的方向。

### P0：Evidence-Grounded Runtime for CUA

**问题**：EnvTrustBench 和 WeaveBench 共同说明 agent 会相信错误环境证据，甚至伪造证据。现有 verifier 多在事后抓错，没有进入 action loop。

**方法**：

- 给 agent 暴露 `verify_evidence(claim, source)`、`state_delta()`、`trace_provenance()`。
- 每个 state probe 带 source / timestamp / authority / freshness。
- 测 fabricated evidence、stale evidence、false completion、prompt injection 下的 action gating。

**为什么 P0**：这是 safety/reliability 方向，和 agent-facing affordance 自然结合，且不是单纯 benchmark 规模竞争。

### P1：Hybrid GUI+CLI/API Cross-Channel Verifier

**问题**：WeaveBench 证明 hybrid 必须存在，但 reward hacking 高。WorkspaceBench 证明文件依赖和 lineage 是真实瓶颈。

**方法**：

- 小规模 30-50 tasks，覆盖 web dev、data/report、ops、document。
- agent 每步可选择 GUI / CLI / API / file operation。
- verifier 检查 GUI 状态、file state、logs、DB/config 是否一致。

**风险**：工程重。建议作为第二阶段，不是第一篇 paper。

### P1：Functional Fidelity Boundary

**问题**：MobileGym 证明 functional simulation 可以迁移；WebHarbor/VeriEnv/InfiniteWeb 证明 web 可以 recreate/synthesize。但边界仍不清楚。

**方法**：

- 在同一任务 taxonomy 下比较 live / mirror / synthetic / functional mock。
- 指标包括 behavior divergence、verifier coverage、state transition mismatch、transfer gap。

**风险**：容易变成评测工程。需要聚焦一个清晰理论问题：什么 fidelity 对 agent learning 是必要的？

### P2：Personalized CUA Environment Protocol

**问题**：MyPCBench 指出 personal context 是现实部署缺口。

**方法**：

- 在 canonical persona 环境中测试 state probe / verifier / privacy guard。
- 研究哪些 personal state 可暴露、如何权限分层、如何避免泄露无关 private context。

**风险**：privacy / synthetic persona / task realism 复杂，适合作为后续扩展。

---

## 5. 不建议主攻的方向

1. **再做一个普通 benchmark**  
   OSWorld、WindowsWorld、SaaS-Bench、MyPCBench、WeaveBench、GUI-360 已经把 benchmark 空间占得很满。没有 verifier/process diagnosis/agent-facing protocol 的新 benchmark 很难有 insight。

2. **单纯扩大 synthetic environment 数量**  
   Agent-World、Gym-Anything、EnvFactory、CUA-Gym、InfiniteWeb 都在 scale。资源不占优时，不应竞争“谁造更多环境”。

3. **只做 semantic actions / typed API**  
   Plan-Then-Execute 和 ComputerRL 已经把 typed/semantic action 的价值讲清。除非加入 state/provenance/rollback/verifier boundary，否则 novelty 不够。

4. **纯 pixel-perfect GUI simulator**  
   MobileGym 和 WebHarbor 都说明 task-driven functional fidelity 更重要。pixel-perfect 应只作为特定任务所需维度，而不是主贡献。

5. **只优化 RL 算法而不解决 verifier**  
   DART-GUI / ComputerRL / WebGym / AsyncWebRL 已经把 RL 系统效率推得很强。没有新的 reward/verifier/environment insight，很容易被认为是 engineering scaling。

---

## 6. 建议的最终选题表述

### 推荐标题

**Safe Agent-Facing Runtime Affordances for Reliable Web and Computer-Use Agents**

### 核心问题

> When an environment already has state, verifier, reset, and action graph APIs, which of these capabilities can be safely exposed to an agent at runtime, and do they causally reduce execution failures beyond prompt-only and evaluator-only baselines?

### 论文贡献应写成四点

1. **Boundary**：定义 evaluator-only / agent-safe / oracle 三层环境能力边界。
2. **Protocol**：实现 observe-state、state-diff、typed action、checkpoint/restore、verify-probe、guard、trace-provenance。
3. **Causal Evidence**：通过 C0-C7+ 对照证明不同 affordance 对不同 failure mode 的选择性作用。
4. **Safety Analysis**：量化 state probe leak、semantic action shortcut、evidence-grounding defect 和 unsafe side-effect。

### 最小可行实验

第一版只做 Web：

- **环境**：WebHarbor mirror + CUA-Gym-Hub mock app，各 1-2 个。
- **任务**：40-60 个，覆盖 navigation、CRUD、cart/checkout-like flow、issue tracker、document/workspace。
- **Agent**：2 个 frontier API agent + 1 个开源 GUI agent。
- **强 baseline**：Dynamic Prompt、Serialized AFE Prompt、Typed API Only、Evaluator-only API。
- **结论门槛**：Full AFE 必须不仅提升 success rate，还必须显著降低至少 3 类 failure mode：hidden-state mismatch、wrong-turn non-recovery、false completion / evidence defect。

---

## 7. 总结

近期 GUI env 工作的核心变化是：环境已经不只是“评测场地”，而是 agent 能力边界的一部分。MobileGym / OpenComputer / CUA-Gym / WebHarbor / WeaveBench / MyPCBench 分别把 functional state、programmatic verifier、state API、local mirror、hybrid evidence、personal context 推到台前。

因此，下一步最有味道的问题不是“再造一个环境”，而是：

> 环境后台越来越强之后，哪些能力应该进入 agent 的 runtime interface？

这个问题如果回答清楚，就能把 [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]] 从宽泛 proposal 收敛成一个可实验、可审稿、可复用的研究方向。
