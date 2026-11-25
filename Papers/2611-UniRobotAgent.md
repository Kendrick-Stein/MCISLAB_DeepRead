---
title: "Democratizing Robot-Use Agents: A Unified Harness with Open Models"
authors: ["Yuan, Jiarui", "Zuo, Yuxin", "Huang, Xiaoyu", "Zhang, Wenbo", "Park, Kwanyoung", "Yang, Junlin", "Zhang, Tianxiang", "Chen, Ruoqu", "Ouyang, Yutao", "He, Bingxiang", "Lv, Xingtai", "Wu, Hongjin", "Liu, Jiajun", "Zhao, Jiahao", "Luo, Tianwei", "Li, Haozhan", "Qian, Cheng", "Ge, Jiaxin", "Gao, Huan-ang", "Yang, Kaisen", "Deng, Jiaqi", "Xu, Qixin", "Huang, Siqiao", "Zhou, Bowen", "Xu, Mengdi", "Liu, Zhiyuan", "Abbeel, Pieter", "Ding, Ning"]
date_publish: "2026-11-01"
date_added: "2026-11-25"
venue: "arXiv"
tags: ["embodied-reasoning", "task-planning", "manipulation"]
url: "https://arxiv.org/abs/2611.01560"
arxiv_id: "2611.01560"
code: "https://github.com/Open-RUA/uni-robot-agent"
cite_key: yuan2026democratizing
rating: 5
content_scope: "full-text"
verification_status: "source-checked"
---

## Summary

uni-robot-agent 用统一的机器人适配器和交互 harness，评估开放权重和闭源模型的执行能力。 [原文](https://arxiv.org/html/2611.01560v2)

## Problem & Motivation

不同模型往往配不同工具和运行架构，表面差距混合了模型性能与接口质量。

## Method

同一工具契约对接不同机器人，整理一致的观测、运动状态、夹爪控制与故障回报。处理并发与重复命令，并对长历史进行管理。

## Key Results

42 项 RoboDojo 仿真任务上，Qwen3.8-Flash-Next 取得 25.00% SR 和 31.39 分，同 harness 的 Astra 为 46.67% 和 51.90 分。19 项真机任务中 Qwen 53.50、Astra 80.50，所报为 100 分 rubric。真机 Agent 能用深度，对照 VLA 和 WAM 用 RGB。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 用同一接口比较开放和闭源模型，仿真 report 区分 SR 和部分成功分 | benchmark-setting | §§2, 3.1 Table 1 | Simulation Evaluation | source-verified |
| C2 | 同 harness 的 Qwen 31.39 分与 Astra 51.90 分来自 42 项仿真任务 | comparison | §3.1.1 Table 1 | Table 1 | source-verified |
| C3 | 19 项真机任务 Qwen 53.50、Astra 80.50 为综合分，Agent 有深度输入 | comparison | §3.2 Table 2, Appendix B | Table 2 | source-verified |

## Strengths & Weaknesses

同模型换 harness 的仿真比较比开放模型跨论文排名更适合归因。真机模型使用各自适配的观测和训练条件。

## Mind Map

```mermaid
mindmap
  root((uni-robot-agent))
    Agent 决策
    机器人接口
    实验与证据
```

## Notes

- [[Topics/RobotUseAgents-Survey]]
