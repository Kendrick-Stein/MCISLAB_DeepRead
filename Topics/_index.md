---
title: Topics
last_updated: "2026-07-20"
---

## 研究主题

跨论文的综合调研报告（`*-Survey.md`）。每篇 Survey 是**沉淀性**文档，与某个 DomainMap 长期对应、持续更新。
（与 `Reports/` 区分：Reports 是某一时点生成的报告/提案，详见 `docs/SPEC.md` §5.3。）

> 2026-07-20 整合：20 份 survey 合并为 12 份，每个子方向一份。ComputerUseAgents → GUIAgent；GUI-Environment + AgentFriendlyEnvironment + WebEnvironment-Engine → AgentEnvironment；WorldActionModel → WorldModel；Embodied-Reasoning + LanguageConditioned-MobileManipulation → EmbodiedAI（专题一/二）；CloudPhone-GUI-VLA 移至 Reports/（任务书报告）。

### GUI / Computer-Use Agent（当前研究重心）

| Survey | 范围 | Domain Map |
|--------|------|------------|
| [[Topics/GUIAgent-Survey]] | 方法总览（grounding / self-improving / RL / 架构谱系，含 computer-use） | [[DomainMaps/GUI-Agent]] |
| [[Topics/WebAgent-Survey]] | web 模态方法（deep research / 安全面 / 训练范式） | [[DomainMaps/GUI-Agent]] |
| [[Topics/AgentEnvironment-Survey]] | 环境工程（需求六轴 / 跨平台引擎 / agent-friendly 接口） | [[DomainMaps/GUI-Agent]] |
| [[Topics/AgentRuntimePrimitives-Survey]] | recovery/branching/parallelism 三原语 related work | [[DomainMaps/GUI-Agent]] |
| [[Topics/RealWorldGUIAgent-Reliability-Survey]] | agent 侧真实执行可靠性 | [[DomainMaps/GUI-Agent]] |

### VLM / Agent / RL

| Survey | 范围 | Domain Map |
|--------|------|------------|
| [[Topics/VLM-Survey]] | 视觉语言模型 | [[DomainMaps/VLM]] |
| [[Topics/AgenticRL-Survey]] | agent 强化学习（credit assignment / reward model） | [[DomainMaps/AgenticRL]] |
| [[Topics/SelfEvolvingAgents-Survey]] | 自演化 agent（memory / skill / 非参数自我改进） | [[DomainMaps/AgenticRL]] |

### Embodied / VLA / VLN

| Survey | 范围 | Domain Map |
|--------|------|------------|
| [[Topics/EmbodiedAI-Survey]] | 总览 + 专题一 Embodied Reasoning + 专题二 Mobile Manipulation | [[DomainMaps/EmbodiedAI]] |
| [[Topics/VLA-Survey]] | VLA 全景（action 表示 × data recipe 双轴） | [[DomainMaps/EmbodiedAI]] |
| [[Topics/VLN-Survey]] | 视觉语言导航 | [[DomainMaps/EmbodiedAI]] |

### World Model / 其他

| Survey | 范围 | Domain Map |
|--------|------|------------|
| [[Topics/WorldModel-Survey]] | world model 全景（含 World Action Model 路线） | [[DomainMaps/WorldModel]] |
| [[Topics/HyperbolicManifold-Survey]] | 双曲流形 | [[DomainMaps/HyperbolicManifold]] |
