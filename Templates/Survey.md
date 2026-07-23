---
title:
tags: [tag1, tag2, ...]
date_updated: "{{date}}"
year_range: YYYY-YYYY
papers_analyzed:
keywords: []  # 小写短语，供 survey_updates.py 匹配论文（如 [gui-agent, web agent]）
domain_map: null  # 对应 DomainMaps/{Name}.md，无则 null
---
## Overview
%% 领域概览：核心问题、研究现状、整体趋势，3-5 段。首句=单一核心论题（真正的一句话）；并列分类用竖排 bullet；禁对话性内容与流程注记（写作基线见 literature-survey SKILL Step 6a） %%

## 技术路线
%% 按方法论聚类（2-4 个路线），每个路线含代表论文、核心思路、优劣势。每章成段叙事：开篇发展进程/研究现状段、章末待解决问题段；概念分类/发展阶段写因果链段落（解决了什么、暴露了什么），不做方法名 bullet 罗列；表格前加 1-3 句框架段说明它回答什么问题。每条路线显式写出：继承的假设（数据/评价/环境）+ 遗留的研究债；转折点解释"前一路线为何不足、新工作改了什么、什么证据促使社区转向"，而非只按年份罗列 %%

## Datasets & Benchmarks

| Dataset | 规模 | 评估指标 | SOTA | 特点 |
|:--------|:-----|:---------|:-----|:-----|
|         |      |          |      |      |

%% 该领域主要数据集和评测基准，SOTA 列填当前最优结果及方法（如 "98.7% (Xiaomi-Robotics-0)"），可根据具体情况调整Table格式 %%

## 失败模式与负证据
%% 单列：已知失败条件、无效/被放弃的路线、无法复现的结论、对资源/实现高度敏感的结果、被主流叙事略过的负结果。没有则写"本轮未检索到系统性负证据（覆盖信号，非不存在）"。只放证据，不放推测 %%

## Key Evidence Matrix
%% 只列会影响 Overview / benchmark 横向结论 / Key Takeaways / Open Problems 的高影响 claim。State 使用 consensus / disputed / single-source / unknown；Evidence 写 Paper wikilink + Claim ID/locator；source-verified 仅表示原文一致性，不表示独立复现。 %%

| Survey claim | State | Evidence objects | Claim IDs / locators | Contradictions / boundary |
|:--|:--|:--|:--|:--|
|  |  |  |  |  |

## Key Takeaways
%% ≤5 条核心结论，只留可操作/可预测/指向行动的；预测/新概念/反直觉论断必须自带 2-4 句 self-contained 解释（砍论据的展开，不砍论断的解释）。称"共识"须多篇独立（非同组/非同实验设置）支持且无未讨论反例，否则表述为"某工作发现"；有冲突结论时并列呈现而非强行选一个 %%

## Open Problems
%% 每条标注分层：**Observed Tension**（有证据显示矛盾/失败/未解释现象）/ **Validated Gap**（经 prior-art 检索确认现有工作未充分解决）。每条给：问题表述（具体可证伪，非口号）+ 支持证据 + 最接近的已有工作（closest prior art）+ 为什么重要。只有 Validated Gap 才进入 idea-generate 管线；未做 prior-art 检索的一律标 Observed Tension，不写"首次/无人研究" %%

## 调研日志
- **调研日期**: YYYY-MM-DD
- **论文统计**: vault 已有 N 篇 + 新 digest N 篇 + 跳过 N 篇
- **未能获取**: <列出未能 digest 的论文及原因>
