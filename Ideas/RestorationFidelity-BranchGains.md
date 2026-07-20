---
title: "Restoration Fidelity：回溯没恢复的那部分状态，及其对分支收益与训练数据的污染"
tags: [gui-agent, web-agent, computer-use]
status: veto
linked_project:
date_updated: "2026-07-20"
veto_reason: "Supervisor 2026-07-20：这是 infra/测量问题而非算法问题，无亮点；不如 MismatchTriage（错误累积恢复选择）"
---
## Hypothesis

树搜索/回溯文献隐含假设"恢复后的状态 = 原状态"，但实际三档恢复手段（URL 重定向 / reset+replay / 引擎快照）各有系统性的状态泄漏，且该泄漏从未被测量。假设：

1. 恢复误差可自动测量（fidelity metric：恢复态与 ground-truth 快照的可观测差分 + 恢复点后 k 步的行为分歧率）；
2. **分支/回溯收益随恢复保真度单调递增，且存在阈值——保真度低于阈值时搜索为负收益**（为 [[Papers/2512-WebOperator]] "naive tree search 反而掉分"提供机制解释）；
3. 恢复误差同样污染训练数据：依赖 reset+replay 的数据管线（[[Papers/2606-SRC]]、[[Papers/2506-GoBrowse]]）中，replay 误差使轨迹前缀与实际状态不符，构成 silent label noise。

可证伪预测：

- **测试侧**：同一环境、同一搜索算法，只换恢复层（URL / replay / snapshot 三档），成功率单调排序且顶底差 ≥8pp。若三档无显著差异，则 [[Topics/AgentRuntimePrimitives-Survey]] Takeaway 1 的"保真度决定收益上限"推断被推翻——agent 对恢复误差鲁棒、引擎级快照的必要性存疑，同样是可发表结论（双向都有产出）。
- **预测力**：fidelity metric 能预测单次回溯是否导致后续失败（AUC ≥0.75）。
- **可修复性**：divergence-aware search（恢复后 state-diff 自检，高误差节点重验证或局部修复）在 replay 档回收 replay 与 snapshot 档差距的 ≥50%。
- **训练侧**：用 fidelity metric 过滤 replay 噪声样本后，同量数据下游 SFT 提升 ≥2pp；若无提升，说明模型对前缀-状态失配鲁棒，同样值得报告。

## Motivation

**知识空白**（survey OP4 原文："URL / replay / 快照三档恢复的保真度-成本-收益曲线没有 benchmark"，本轮外部检索再次确认为零命中）：整个分支/回溯文献要么绕开该问题、要么承受它，无人测量它——

- [[Papers/2602-AgentAlpha]] 作者自列 state reconstruction errors 为失效来源，未测量；
- [[Papers/2504-WebRollback]] 承认 URL 恢复丢失表单/购物车/后端 session，未量化；
- [[Papers/2510-BranchAndBrowse]] 的 nearest-URL 混合重放是工程折中，未报告保真度；
- [[Papers/2512-WebOperator]] naive search 负收益（51.61% < 53.55%）是该问题最清晰的症状，论文只给了启发式规避；
- [[Papers/2606-SRC]] 自列 resettable 假设为局限，未检验 replay 误差对数据质量的影响。

**为什么现在**：基建两端刚刚成熟使三档受控对照第一次可行——引擎快照（[[Papers/2510-WebServ]] ZFS CoW、Fork-Explore-Commit (2602.08199) sub-350μs OS fork、[[Papers/2604-Crab]]）提供 ground-truth 状态参照，使"URL/replay 档没恢复的部分"第一次可被精确测量。系统社区在快速造 fork 基建，但"保真度差距值多少成功率"这一因果问题决定这些基建是否值得为 agent 而建——无人回答。

**影响**：每篇树搜索论文的结果解读都依赖这个未测量的变量；产出的 fidelity-cost-benefit 曲线为后续所有分支/回溯工作提供实验设计依据，也为引擎级原语的立项提供第一个因果数字（[[Ideas/AgentFacing-WebRuntime]] 的量化前提）。

## Related Work

- [[Papers/2407-TreeSearchLMAgents]] / [[Papers/2602-AgentAlpha]] — reset+replay 恢复的代表，依赖确定性假设
- [[Papers/2504-WebRollback]] / [[Papers/2510-BranchAndBrowse]] / [[Papers/2512-WebOperator]] — URL 系恢复的三代工程折中
- [[Papers/2510-AgenticExplorationSystems]] — 测过快照**延迟**（1.757s），没测过恢复**保真度**
- [[Papers/2606-SRC]] / [[Papers/2506-GoBrowse]] — 训练侧 replay 依赖（污染面）
- Fork-Explore-Commit (2602.08199) — OS 级 fork 基建（ground-truth 端），无 agent 侧分析
- Guided Search in Non-Serializable Environments (2505.13652) — 零保真度极端（无恢复）的搜索；本 idea 研究其间的连续谱

**Novelty**（外部检索验证记录，2026-07-20）：
- query "replay divergence state restoration error tree search web agent" → 最近命中 2606.20724（hidden-failure 诊断，与恢复保真度无关）；
- query "compensating action / semantic undo agent" → SagaLLM/DART/Revisable-by-Design/ACRFence 形成的是**补偿动作**研究线（语义恢复的另一条路），不测量状态恢复保真度；
- Fork-Explore-Commit / BranchBench (2604.17180) / WebServ 全部只报系统指标（延迟/内存），无保真度定义、无对 agent 成功率的因果实验。
- 结论：fidelity 的定义、测量、因果曲线、divergence-aware 修复、训练数据污染五个组成部分均无先例。

## Approach sketch

1. **三档恢复平台**：WebArena/VisualWebArena（Docker bit-identical reset 作 ground truth）上实现可插拔恢复层——URL 重定向 / reset+replay / 容器快照（Docker commit 慢但保真，离线实验可接受；升级选项 WebServ/Incus）；同一简化 best-first search 只换恢复层。
2. **Fidelity metric**：状态级——恢复态 vs ground-truth 快照的 DOM/AXTree 可观测差分 + 后端 DB 行差分；行为级——同一 policy 从恢复态与真实态各 rollout k 步的动作分歧率。两级互为校验。
3. **因果曲线**：保真度 × 搜索预算 × 成功率三维扫描；定位负收益区域，检验其与 WebOperator 现象的对应。
4. **Divergence-aware search**：恢复后自动 state-diff 校验，高误差节点触发重验证/局部重放修复/降权三种策略对比。
5. **训练侧**：对 SRC 式 replay 数据管线加 fidelity 过滤，对照下游 SFT。

## Expected outcome

- 主结果：领域第一条恢复保真度-分支收益因果曲线 + 负收益阈值；
- 测量工具：fidelity metric 与三档恢复的 fidelity-cost profile 表（可被后续工作直接引用）；
- 方法增量：divergence-aware search 的回收率；
- 训练侧：replay 噪声对 SFT 的影响量化。
- 双向可发表：假设不成立（三档无差）则推翻 survey 核心推断，结论同样 actionable（不必建引擎快照）。

## Risk

- **ground truth 自身噪声**：WebArena 动态内容使 bit-identical 不严格 → 选静态化子集 + 多次 reset 测底噪作为测量下界。
- **模型能力掩盖差距**：强模型可能自我修正恢复误差 → 跨 2-3 个能力档（7B 开源 / 32B / frontier API）报告，能力-保真度交互本身是有价值的结果。
- **工程量**：三恢复后端实现 → URL/replay 有开源参照（WebRollback、Branch-and-Browse），快照档用 Docker commit 起步。
- **被抢先**：系统社区（Fork-Explore-Commit 团队）做 agent 侧评估是可能的下一步，但他们的评估习惯是延迟/吞吐而非成功率因果——窗口相对安全，仍建议先做测量部分（2-3 周可出首批数字）。
