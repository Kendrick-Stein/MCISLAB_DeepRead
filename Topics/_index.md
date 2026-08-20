---
title: Topics
last_updated: "2026-08-20"
---

## 研究主题

`Topics/` 只维护跨论文、可持续增量更新的 canonical survey；一次性报告与项目提案放在 `Reports/`。

> 2026-07-23 升级：GUI 主报告重构为 12 节完整 [[Topics/CUA-Survey]]（180 篇）。2026-07-24 清理：GUIAgent-Survey 及 4 份 merged redirect（AgentEnvironment / AgentRuntimePrimitives / RealWorldGUIAgent-Reliability / AgenticRL）删除，全库链接已改指 CUA-Survey。2026-08-20 新增跨域算法切面 [[Topics/StepCreditAssignment-Survey]]。当前 10 份均为 active survey。

### GUI / Computer-Use Agent（当前研究重心）

| Canonical Survey | 组织结构 | Domain Map |
|:--|:--|:--|
| [[Topics/CUA-Survey]] | 12 节：定义与范围 / 问题形式化 / 任务与环境 / 数据 / 模型与架构 / 学习与 RL / 评测 / 产业部署 / 开放挑战 / Takeaways | [[DomainMaps/GUI-Agent]] |

所有 Web、Mobile、Desktop、OS 与 GUI+API/CLI 交互论文都先进入这一个主报告。每篇论文只设一个 primary section，其他章节使用 cross-link，避免为"算法/环境/可靠性"重复维护多份结论。digest→survey 路由以本文件 frontmatter keywords 为准。

同方向另有两份**专题分析**，切面与主报告正交、文件名不带 `-Survey` 后缀因而不参与自动路由：

| 专题分析 | 切面 |
|:--|:--|
| [[Topics/AgentHarness-Design]] | harness 三条设计轴（动作接口 / 执行循环 / 上下文预算）+ 预算口径审计，web agent 范围 |
| [[Topics/Harness-Component-Attribution]] | harness 增益的组件级归因：bundle 报增益、缺角色消融的证据缺口 |

### AI Agent / 非 GUI 邻接方向

| Survey | 范围 | Domain Map |
|:--|:--|:--|
| [[Topics/WebAgent-Survey]] | Deep Research / information seeking；不含 GUI navigation | [[DomainMaps/AgenticRL]] |
| [[Topics/SelfEvolvingAgents-Survey]] | 通用 self-evolution：model / memory / skill / workflow | [[DomainMaps/AgenticRL]] |
| [[Topics/StepCreditAssignment-Survey]] | 从 trajectory-level reward 反推 step-level 监督：选步 / PRM / 隐式 credit / advantage 塑形 | [[DomainMaps/AgenticRL]] |

通用 Agentic RL 的算法证据保留在 `Papers/`；只有形成独立于 GUI application 的稳定问题结构后，才重新建立跨域 survey。StepCreditAssignment 是目前唯一满足该条件的跨域切面——同一套问题（trajectory-level 0/1 信号如何分解到步）在数学推理、文本 agent 与 GUI 上共享方法族与失效模式。它是算法横切面，不改变 GUI 论文的落位：带直接 GUI 交互证据的论文仍以 [[Topics/CUA-Survey]] 为 primary section，只在步级监督机制上 cross-link 到这里。

### VLM / Multimodal

| Survey | 范围 | Domain Map |
|:--|:--|:--|
| [[Topics/VLM-Survey]] | 视觉语言模型；GUI 只保留为直接测量 UI grounding/action 的交叉证据 | [[DomainMaps/VLM]] |

### Embodied / VLA / VLN

| Survey | 范围 | Domain Map |
|:--|:--|:--|
| [[Topics/EmbodiedAI-Survey]] | Embodied AI 总览 + Embodied Reasoning + Mobile Manipulation | [[DomainMaps/EmbodiedAI]] |
| [[Topics/VLA-Survey]] | VLA 全景：action representation × data recipe | [[DomainMaps/EmbodiedAI]] |
| [[Topics/VLN-Survey]] | Vision-Language Navigation | [[DomainMaps/EmbodiedAI]] |

### World Model / 其他

| Survey | 范围 | Domain Map |
|:--|:--|:--|
| [[Topics/WorldModel-Survey]] | World Model 全景；digital-domain simulator 与 GUI 主报告 cross-link | [[DomainMaps/WorldModel]] |
| [[Topics/HyperbolicManifold-Survey]] | Hyperbolic Manifold | [[DomainMaps/HyperbolicManifold]] |
