---
title: "Agentic RL Survey（已并入 GUI 主报告）"
tags: [survey, agentic-RL, merged]
date_updated: "2026-07-21"
year_range: 2023-2026
papers_analyzed: 0
keywords: []
domain_map: AgenticRL
status: merged
merged_into: "[[Topics/CUA-Survey]]"
---

# Agentic RL Survey（已并入 GUI 主报告）

本文件原有 58 篇统计与 71 个可解析论文链接，主体证据来自 GUI、Web 与 Computer-Use Agent。2026-07-21 起，GUI-specific 的 GRPO/RLVR、credit assignment、reward/verifier、self-improvement、tree rollout、环境基础设施与阴性结果统一维护在 [[Topics/CUA-Survey]] 的“训练、RL 与持续适应”章节。

## 迁移映射

| 原内容 | Canonical 位置 |
|:--|:--|
| GUI GRPO / RLVR / credit assignment | [[Topics/GUIAgent-Survey#3. 训练、RL 与持续适应]] |
| Reward model / verifier reliability | [[Topics/GUIAgent-Survey#6. 评测与 Verifier]] |
| RL environment / rollout infrastructure | [[Topics/GUIAgent-Survey#5. 环境、基础设施与 Runtime]] |
| Task / trajectory synthesis | [[Topics/GUIAgent-Survey#4. 数据、任务与经验生成]] |
| Self-improving GUI agent | [[Topics/GUIAgent-Survey#3.4 Self-improvement：参数化与非参数化]] |

## 范围边界

SAO、RingZero、LongStraw、BRAID、DirectOPD 等不含 GUI 交互证据的通用 Agentic RL 工作不计入 GUI core；其事实与批判性分析仍保留在各自 `Papers/` 笔记中。若跨域通用 RL 证据形成稳定、独立于 GUI application 的问题结构，应另建跨域 survey，而不是恢复本文件的混合 taxonomy。

本文件不再参与 digest→survey 自动路由；GUI 论文必须带 `gui-agent`、`computer-use` 或 GUI-interaction 语义下的 `web-agent` tag，并进入 [[Topics/CUA-Survey]]。
