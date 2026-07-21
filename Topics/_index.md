---
title: Topics
last_updated: "2026-07-21"
---

## 研究主题

`Topics/` 只维护跨论文、可持续增量更新的 canonical survey；一次性报告与项目提案放在 `Reports/`。

> 2026-07-21 整合：GUIAgent、Web GUI operation、AgentEnvironment、AgentRuntimePrimitives、RealWorldGUIAgent-Reliability，以及 AgenticRL 中直接面向 GUI/Web/CUA 的内容，统一并入 `GUIAgent-Survey`。当前 13 个 `*-Survey.md` 文件中有 9 份 active survey、4 份兼容旧链接的 merged redirect；redirect 不再参与 digest→survey 路由。

### GUI / Computer-Use Agent（当前研究重心）

| Canonical Survey | 组织结构 | Domain Map |
|:--|:--|:--|
| [[Topics/GUIAgent-Survey]] | 模型与 Agent 架构 / 训练与 RL / 数据与任务生成 / 环境与 runtime / 评测与 verifier / 可靠性、安全与 HCI | [[DomainMaps/GUI-Agent]] |

所有 Web、Mobile、Desktop、OS 与 GUI+API/CLI 交互论文都先进入这一个主报告。每篇论文只设一个 primary section，其他章节使用 cross-link，避免为“算法/环境/可靠性”重复维护多份结论。

### AI Agent / 非 GUI 邻接方向

| Survey | 范围 | Domain Map |
|:--|:--|:--|
| [[Topics/WebAgent-Survey]] | Deep Research / information seeking；不含 GUI navigation | [[DomainMaps/AgenticRL]] |
| [[Topics/SelfEvolvingAgents-Survey]] | 通用 self-evolution：model / memory / skill / workflow | [[DomainMaps/AgenticRL]] |

原 [[Topics/AgenticRL-Survey]] 已成为 merged redirect。通用 Agentic RL 的算法证据保留在 `Papers/`；只有形成独立于 GUI application 的稳定问题结构后，才重新建立跨域 survey。

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

### Merged Redirects

- [[Topics/AgentEnvironment-Survey]] → [[Topics/GUIAgent-Survey#5. 环境、基础设施与 Runtime]]
- [[Topics/AgentRuntimePrimitives-Survey]] → [[Topics/GUIAgent-Survey#2.4 Planning、Memory 与 Search]] / [[Topics/GUIAgent-Survey#5. 环境、基础设施与 Runtime]]
- [[Topics/RealWorldGUIAgent-Reliability-Survey]] → [[Topics/GUIAgent-Survey#7. 真实部署可靠性、Safety 与 HCI]]
- [[Topics/AgenticRL-Survey]] → [[Topics/GUIAgent-Survey#3. 训练、RL 与持续适应]]
