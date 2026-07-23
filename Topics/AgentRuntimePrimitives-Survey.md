---
title: "Agent Runtime Primitives Survey（已并入 GUI 主报告）"
tags: [survey, gui-agent, runtime, merged]
date_updated: "2026-07-21"
year_range: 2024-2026
papers_analyzed: 0
keywords: []
domain_map: GUI-Agent
status: merged
merged_into: "[[Topics/CUA-Survey]]"
---

# Agent Runtime Primitives Survey（已并入 GUI 主报告）

Recovery、branching、parallelism、checkpoint、rollback 与 replay 不再作为独立 GUI survey 维护。它们分别是 Agent 架构、训练 rollout 与 environment runtime 的原语，已按控制方重新归入 [[Topics/CUA-Survey]]。

## 迁移映射

| 原语控制方 | Canonical 位置 |
|:--|:--|
| Agent/search 控制的 planning、memory、rollback action | [[Topics/GUIAgent-Survey#2.4 Planning、Memory 与 Search]] |
| Trainer 控制的 tree rollout / branch data | [[Topics/GUIAgent-Survey#3. 训练、RL 与持续适应]] |
| Environment 提供的 checkpoint / fork / replay / parallel | [[Topics/GUIAgent-Survey#5. 环境、基础设施与 Runtime]] |
| 部署期 error recovery / safe backtracking | [[Topics/GUIAgent-Survey#7. 真实部署可靠性、Safety 与 HCI]] |

本文件不再参与 digest→survey 自动路由。
