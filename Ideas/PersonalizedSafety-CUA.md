---
title: Personalized Safety for Computer-Use Agents
tags: [computer-use, gui-agent]
status: raw
linked_project:
date_updated: "2026-06-24"
---
## Hypothesis

在 personal computer-use environments 中，安全风险主要来自“授权内越界”：agent 已被允许操作电脑，但在完成任务时访问、引用或泄漏了与任务无关的个人状态。我们假设结合 **task-scoped permission manifest + trajectory-level privacy guard**，可以显著降低 personalization leakage，同时不明显损害任务完成率。

## Motivation

[[Papers/2606-MyPCBench]] 指出真实 personal assistant 必须处理 logged-in-like accounts、历史数据和跨应用个人上下文；[[Papers/2606-BraveGuard]] 指出 CUA 安全风险常在多步 trajectory 中出现，prompt-level guard 看不见。两者合起来暴露一个高价值空白：personal CUA 的风险不一定是明显恶意行为，而是“看了不该看的东西”“把无关个人信息带进回答”“为完成当前任务过度搜索私有状态”。

这比通用 prompt injection 防御更接近真实部署。用户已经授权 agent 操作，但授权应当是 task-scoped，而不是全盘读写。

## Related Work

- [[Papers/2606-MyPCBench]] - personal context benchmark，暴露 logged-in-like assistant 场景。
- [[Papers/2606-BraveGuard]] - trajectory-level guard training，强调 execution trace safety。
- [[Papers/2500-PermissionManifestsWebAgents]] - permission manifest 思路，可作为 task scope 表达基础。
- [[Ideas/HybridVerifier-GUIRuntime]] - agent-facing verifier，用于减少 reward hacking；本 idea 更关注 privacy/safety。

**Novelty**: 4/5。已有 permission 和 trajectory guard，但 personal CUA 下的 task-scoped privacy leakage metric 与 guard protocol 仍是明显空白。

## Approach sketch

设计一个 lightweight personal CUA safety protocol：

1. **Task-scoped manifest**：每个任务声明 allowed apps、allowed data categories、forbidden data categories、confirmation-required actions。
2. **Trajectory annotations**：记录每一步访问的 app/window/file/url、visible sensitive entity、action purpose。
3. **Privacy guard**：基于 trajectory 判断是否发生：
   - out-of-scope access；
   - unnecessary sensitive inspection；
   - answer-time leakage；
   - irreversible or external action without confirmation。
4. **Evaluation**：在 MyPCBench-like 环境或小型模拟 personal desktop 中构造 50-100 个任务，比较 baseline agent vs manifest+guard agent。

关键不是训练大模型，而是定义可复现 metric：Personalization Leakage Rate、Task Completion Retention、False Block Rate。

## Expected outcome

预期 manifest+guard 能：

- 降低 out-of-scope personal state access；
- 降低 final answer 中的无关 personal info leakage；
- 对普通任务 completion rate 影响小于 5-10pp；
- 主要失败来自 manifest 过窄或 guard 误判 agent 的必要查询。

成功标准：在小型 benchmark 上展示 privacy leakage 明显下降，并给出 failure taxonomy，说明哪些 personal tasks 需要更细粒度 permission。

## Risk

- Manifest 编写可能变成人工规则工程，泛化性不足。
- Guard 如果太保守会破坏 agent usefulness。
- Personal data 模拟不真实时，审稿人可能质疑部署意义。需要从 MyPCBench / OpenClaw 请求中抽样构造更自然的 personal state。
