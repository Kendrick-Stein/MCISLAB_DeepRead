---
title: "OpenRath: Session-Centered Runtime State for Agent Systems"
authors:
  - Fukang Wen
  - Zhijie Wang
  - Ruilin Xu
institute:
  - Tsinghua University
date_publish: 2026-06-17
venue: arXiv
tags:
  - LLM
  - task-planning
url: "https://arxiv.org/abs/2606.19409"
cite_key: wen2026openrath
arxiv_id: "2606.19409"
code:
rating: 2
date_added: "2026-06-26"
---
## Summary

OpenRath 提出以 `Session` 为核心的 agent 运行时状态抽象，将对话历史、工具调用证据、沙箱放置、分支血缘、内存事件等碎片化状态统一为一个可分支、可检查、可重放的程序值，采用类 PyTorch 的编程模型（`Agent`/`Workflow`/`Tool`/`Memory`/`Selector` 均遵循 `Session -> Session` 接口），主张 "first-class runtime state" 是多 agent 系统可审计性的基础。

## Problem & Motivation

现代 agent 系统的运行时状态高度碎片化：对话记录、工具日志、内存事件、沙箱效果、分支血缘分散在不同侧信道，导致一个完成的 run 几乎无法回答"哪个分支产生了最终答案""哪段内存被召回""压缩时丢弃了哪些证据"等基本审计问题。随着 agent 产品从 demo 走向长周期工作流，这一问题日益成为工程合约而非实现细节——没有可重放的运行时状态，debug、发布审查和系统评测都难以可靠进行。

## Method

OpenRath 的核心设计围绕一个小而自洽的对象词汇表：

- **Session**：流动的运行时值，承载对话 chunk、沙箱放置意图、血缘元数据、token 使用量、待处理工作、工具证据和内存边界记录。支持 `fork`（保留亲缘关系）、`detach`（切断血缘）、`merge`（合并两个 session）操作，以及 `session.to(backend)` 的显式放置语法（类比 `tensor.to(device)`）。
- **Agent**：可复用的 `Session -> Session` 变换层，类比 `nn.Module`；拥有局部 prompt、provider 配置、tools 列表和 memory policy，但不拥有整条对话图。
- **Tool**：向模型暴露 JSON schema 的可调用操作，副作用通过 session 的 sandbox dispatch 执行并以 tool-result chunk 形式返回，不会消失进 executor 日志。
- **Sandbox**：文件/命令/代码执行的放置边界，提供能力声明和资源生命周期管理；当前实现了 local backend，OpenSandbox 为可选。
- **Memory**：预期的持久状态平面，recall/commit 操作以显式运行时事件形式记录在 Session 上，而非作为隐式 prompt 文本；当前实现为 evidence-gated（本地模块尚无 source anchor，尚未通过测试验证）。
- **Workflow**：可复用的组合容器，嵌套 agents、tools、分支、压缩器和子 workflow；同样遵循 `forward(session) -> session` 契约，不引入第二套私有编排状态。
- **Selector**：运行时路由器，从当前 session 动态选取下一个 workflow，使控制流决策成为可检查的运行时记录，而非硬编码逻辑。

**生命周期**：Create → Place → Transform → Branch → Persist → Release，每个阶段均有对应的可审计字段（lineage JSONL、usage counter、证据 chunk 等）。

**发布协议**：claim-ledger 驱动的 audit-first 发布——每个 claim 必须映射到可重现的 evidence packet（命令 + manifest + session JSONL + 输出产物），当前 10 个 claim 中 5 个有 operational packet 支撑，1 个 partially supported，1 个 evidence-gated（memory）。

## Key Results

OpenRath 是一份技术报告而非实验论文，**没有 benchmark 数字**。当前经过验证的 claim 均为确定性 runtime claim：

- Session lineage 导出（`lineage_export`）：pass，确定性
- 本地沙箱放置（`local_sandbox`）：pass；OpenSandbox 为 skip
- Workflow 组合（`workflow_transcript`）：pass，确定性
- 聚焦实现契约测试（`pytest_report`）：pass
- Provider 前置条件安全披露（`live_provider_manifest`）：pass，已脱敏
- Memory 实现（`memory_local`）：skip，evidence-gated

作者明确将 benchmark 数字、人类偏好评测、leaderboard 对比均留到后续工作，当前仅声明"runtime 语义正确且可审计"。

## Strengths & Weaknesses

**亮点**：
- 问题定位清晰——将 agent 系统的可审计性问题归结为"运行时状态在哪里流动"，比 trace/span 方案有更好的程序性（evidence 随值流动而非事后重建）
- 类 PyTorch 的编程模型是好的界面设计选择：`forward(session) -> session` 的均匀契约极大简化了组合和嵌套
- 发布诚实度高：claim ledger、evidence-gated 机制、以及对 memory/benchmark 局限的明确承认，是少见的"诚实的技术报告"

**局限**：
- 这是一篇**系统设计报告**，不是实验论文。核心贡献是编程模型和架构，没有可量化的性能对比
- Memory 模块明确 evidence-gated——这是框架的核心功能之一，但当前实现不完整
- 生态定位偏窄且防御性强："我只解决 crossing object 问题"——这既是诚实，也可能意味着缺乏 killer use case 来驱动采用
- 与 LangGraph（checkpoint）和 OpenAI Agents SDK（trace spans）的区分是概念性的，缺乏实证对比；实际上 LangGraph 的 thread state 与 Session 的功能重叠非常高，论文避而不谈

**潜在影响**：对多 agent framework 设计有参考价值，尤其是"memory/tool 证据应该随 session 值流动而非作为 prompt 副作用"这一设计原则；但作为开源工具是否能与 LangGraph/AutoGen 生态竞争存疑。

## Mind Map

```mermaid
mindmap
  root((OpenRath))
    Problem
      Agent runtime state fragmented
      Transcripts hide lineage/tool/memory
      Cannot audit or replay runs
    Method
      Session as first-class runtime value
      fork / detach / merge operations
      session.to(backend) placement
      Agent / Tool / Workflow / Selector
      Memory as session-visible plane
      Claim ledger + evidence packets
    Results
      No benchmark numbers
      Deterministic runtime claims verified
      lineage_export pass
      local_sandbox pass
      workflow_transcript pass
      memory_local evidence-gated
```

## Notes

- 作者来自清华大学，论文 arXiv 分类为 cs.SE
- 这是一份 technical report 而非会议/期刊论文，论文本身明确说明 "broad quantitative comparisons... are left for follow-on evaluation"
- 与 [[2602-DM0]] 等 agent framework 工作的对比值得关注；OpenRath 更像是 runtime substrate 而非完整框架
- "如果深度学习时代让 tensor 成为网络围绕的核心值，下一代 agent 系统需要同样的一步" ——这个类比是本文最有力的 pitch
