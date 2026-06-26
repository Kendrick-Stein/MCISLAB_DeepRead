---
title: Re-digest Manifest — cited abstract-only papers
created: "2026-06-26"
completed: "2026-06-26"
purpose: 把 agenda/idea 引用为证据、但仅基于 abstract 的 21 篇论文重抓全文升级为完整笔记
status: done
---

## 结果

51 篇 abstract-only 中 30 篇未被引用已删除；这 21 篇被引用的改为重抓全文升级。
执行：5 个并行 paper-digest subagent，全文走 `arxiv.org/html/<id>`，404 时 fallback `ar5iv.labs.arxiv.org/html/<id>`（无需 LEXMOUNT_API_KEY）。

**19 / 21 升级成功**，2 篇无法升级：

| 笔记 | 状态 | 说明 |
|------|------|------|
| 2604-GoClick / VisualFLIP / AdaptiveGrounding / MyPCBench / BraveGuard / Skill1 / GenericAgent / HybridMemory / SpatialEvo / VLASafety（active 方向证据） | ✅ done | 全文重写，已去除 abstract-only marker |
| 2604-AgenticWorldModel / HYWorld2 / MultiWorld / AgentWorld / Externalization / GenerativeWorldRenderer / Odysseys（World Model） | ✅ done | 全文重写 |
| 2604-EmbodiedMidtrain / LLaDA2Uni（Archive/off-focus） | ✅ done | 全文重写 |
| **2606-Harness1** | ⚠️ blocked | arxiv/html 与 ar5iv 均只渲染 ~800 词（abstract 级），无可用全文，保留原 abstract-only 笔记，未捏造 |
| **2500-GuiAgentsSurvey** | ⚠️ blocked | 笔记无 arXiv id，无法定位来源；建议 Supervisor 提供 URL，或因 off-focus 直接删除 |

## 待 Supervisor 决策

- **Harness1**：全文不可得。是否：(a) 保留 abstract-only，(b) 删除并从 agenda Env Runtime evidence 解除引用，(c) 提供可访问全文来源。
- **GuiAgentsSurvey**：Archive/off-focus + 无 arxiv id。是否删除（并清其 DomainMap 引用）。
