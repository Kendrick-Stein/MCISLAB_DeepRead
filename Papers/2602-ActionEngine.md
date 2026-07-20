---
title: "ActionEngine: From Reactive to Programmatic GUI Agents via State Machine Memory"
authors: [Hongbin Zhong, Fazle Faisal, Luis França, Tanakorn Leesatapornwongsa, Adriana Szekeres, Kexin Rong, Suman Nath]
institute: [Georgia Tech, Microsoft Research]
date_publish: 2026-02-24
venue: arXiv
tags: [gui-agent, web-agent, task-planning]
url: https://arxiv.org/abs/2602.20502
arxiv_id: "2602.20502"
doi:
cite_key: zhong2026actionengine
code:
rating: 4
date_added: 2026-07-20
---
## Summary

针对 reactive GUI agent 每步调 VLM 导致的 O(N) 成本与误差累积问题，用离线 Crawling Agent 构建应用级 state-machine memory（SMG），在线 Execution Agent 单次 LLM 调用合成 Python 程序并确定性执行，在 WebArena Reddit 子集上以平均 1.8 次 LLM 调用达到 95% 成功率（vs AgentOccam 66%），成本降 11.8x、延迟降 2x。

## Problem & Motivation

主流 GUI agent 采用 reactive 的 observe-reason-act 循环：N 步任务需要 O(N) 次 VLM 调用，既贵又慢；且每步视觉推理都引入 hallucination 风险，单步出错即破坏整条轨迹，对含算术/过滤逻辑的 multi-step reasoning 任务尤其致命。根本原因是这类架构缺乏对已访问页面的持久记忆，agent 跨任务反复重新发现同一应用的结构。作者主张把"理解应用结构"从在线执行中剥离出来，一次性离线摊销。

## Method

**两 Agent 架构**：

- **Crawling Agent（离线）**：系统性探索目标 GUI 应用，构建并持续维护 state-machine graph（SMG）。MLLM 只用于识别 state 和验证 operation，不参与逐步执行。
- **Execution Agent（在线）**：接收用户任务 + 预构建 SMG，**单次 LLM 推理**合成完整 Python 程序（O(1) vs O(N)），之后确定性执行，仅失败时再调模型。

**State-Machine Memory** M = (S, O, T)：

- **State（节点）**：GUI 的 distinct "view"（如 Home Page、Forum List），由一组 *atoms*（原子出现的 UI 元素组）定义。
- **Operation（边）**：UI manipulation operations（click/type/navigate，触发状态转移）与 data collection operations（读文本/抽取信息，自环）。
- **防状态爆炸**：区分 static atoms（不变 UI）与 dynamic atoms（数据依赖），用类型化集合（如 `List[[PostDetails]]`）表示同结构的无界实例；Reddit 域最终仅约 20-30 states、100-150 transitions。
- **构建**：从 seed home state 出发的半自动 pipeline；对 dynamic atoms 推断 selector-based rules 而非抽取活数据；operation 严格按 affordance（UI 结构）定义，不绑定任务语义；序列化为 YAML 供 planner 消费。

**程序合成三阶段**：

1. **Sketch Generation**：LLM 基于任务 + SMG 中可达 operations 生成含 `UI_CALL: [OpID]` 占位符、符号变量（`@username`）和固定控制流的高层 Python 程序。
2. **Static Linking**：把抽象 UI_CALL 解析为 SMG 上的具体路径——BFS 搜索、loop invariant enforcement（循环内 UI_CALL 须回到循环入口 state）、LLM heuristic recovery 三级策略；无法解析的节点标记给 runtime fallback。
3. **Compilation**：展开为 Playwright 原语动作，编译成含 UI / Python / Control Flow 三类节点的 MixedActionPlan。

**Vision-based fallback**：执行失败（selector 失效、timeout）或 linking 无法解析时，暂停执行，vision agent 抓取 DOM + screenshot 定位正确交互点，修复后**回写 SMG** 供后续复用——首次失败付延迟代价，之后走更新过的路径。

## Key Results

WebArena Reddit（Postmill）子集 106 个任务，ActionEngine（Claude 4.5 Sonnet）vs AgentOccam（GPT-4-Turbo + vision）：

| 指标 | AgentOccam | ActionEngine | 改善 |
|:--|:--|:--|:--|
| Success Rate | 66% | **95%** | +29pp |
| 平均延迟 | 237s | **118s** | 2.0x |
| 平均成本/任务 | $0.71 | **$0.06** | 11.8x |
| 平均 LLM 调用 | 10.2 | **1.8** | 5.7x |

- **Multi-step reasoning**（统计某作者 downvotes>upvotes 的评论数）：AgentOccam 17.8 次调用、60% 成功；ActionEngine 1 次调用、100% 成功（65s vs 343s）。
- **Vision-dependent 循环任务**（逐帖抽取书籍信息）：AgentOccam 0% → ActionEngine 100%（确定性循环内嵌 LLM 调用）。
- **失败分析**：6/106 失败几乎全部源于任务措辞歧义（如 "machine learning" vs "MachineLearning" 论坛名、"new york" vs "nyc"），而非架构缺陷。

## Strengths & Weaknesses

**亮点**：

- 把 "amortized offline indexing + one-shot programmatic planning" 这条 code-as-policy 路线落到 GUI agent 上，问题切分干净：应用结构理解（可摊销、可复用）与任务执行（确定性）解耦。
- SMG 的 static/dynamic atom 区分 + 类型化集合是控制状态爆炸的关键设计；affordance-based operation 定义保证了跨任务复用性。
- Fallback 不只是兜底，还回写 memory，形成 self-healing 循环。
- 成本/延迟数字对 agent 产品化有直接意义：95% @ $0.06 是质变而非增量。

**局限（作者承认 + 隐含假设）**：

- **单站点评测**：只在 WebArena Reddit 106 任务上验证，SMG per-application 构建、无跨域迁移；baseline 也只有 AgentOccam 一个（且用了不同底座模型，成功率对比混杂了模型差异）。
- **离线探索成本未量化**：论文未报告 Reddit 爬取的时间/费用，摊销论证缺一半数据。
- 假设 UI 增量变化；大规模改版需全量重爬。半自动 crawling 仍需人工给 seed 和验证 affordance。
- 结构化模板型 GUI（论坛类）最适配；高度个性化/自由形态界面下 state 抽象可能失效。弱模型（GPT-4o）合成程序需 20-30% 的验证/热修补开销。
- 无图像理解工具（Task 617 失败）。

**影响推测**：与 skill/API 归纳类工作（把 GUI 轨迹沉淀为可复用程序）同属"GUI agent 去 reactive 化"趋势；SMG 作为显式 world model of an app，是介于纯 vision agent 与官方 API 之间的中间态，值得关注其在多站点、动态 web 上的 scaling 证据。

## Mind Map

```mermaid
mindmap
  root((ActionEngine))
    Problem
      Reactive agent O(N) LLM 调用
      每步视觉推理误差累积
      无跨任务持久记忆
    Method
      Crawling Agent 离线建 SMG
        atoms / static vs dynamic
        affordance-based operations
      Execution Agent 单次合成程序
        Sketch → Static Linking → Compile
        MixedActionPlan
      Vision fallback 回写 memory
    Results
      WebArena Reddit 106 任务
      95% vs 66% 成功率
      成本 11.8x / 延迟 2x 下降
      失败多为任务歧义
```

## Notes

- 与 AgentRuntimePrimitives survey 的关系：SMG 本质是 environment-side memory primitive，可对照 survey 中并行/回溯原语讨论——程序化执行天然支持 replan（重新 linking）而非逐步回溯。
- 待验证问题：SMG 构建成本在真实多站点场景下能否摊销？站点 A/B test 或个性化布局会不会让 selector-based rules 大面积失效？
