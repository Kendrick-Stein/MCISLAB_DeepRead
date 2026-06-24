---
title: Hybrid Verifier-Grounded GUI Runtime
tags: [gui-agent, computer-use, environment, verifier, research-idea]
status: raw
linked_project:
date_updated: "2026-06-24"
---
## Hypothesis

若在 GUI+CLI+Code 混合 computer-use 环境中，把跨通道状态一致性检查、evidence provenance 和 rollback guard 作为 agent-facing runtime affordance 暴露给 agent，则 frontier CUA 的 reward hacking、fabricated evidence 和 premature halt 会显著下降；这种下降不能由 outcome-only judge 或普通 anti-fabrication prompt 替代。

可证伪预测：
- 在 30-50 个 hybrid workflow tasks 上，加入 verifier-grounded runtime affordance 后，reward hacking rate 相比 prompt-only anti-fabrication baseline 下降 >=30%。
- Cross-channel consistency probes 主要降低 fabricated evidence / fake render；rollback guard 主要降低 silent halt 后的不可恢复失败。
- 如果 trajectory-aware judge 仍发现相同规模的 fabricated evidence，则说明 runtime affordance 没有真正改变 agent 行为。

## Motivation

WeaveBench 显示真实 CUA 工作流不是 GUI-only：GUI+CLI+Code hybrid 比单接口高 30pp 以上，但失败中 35.2% 来自 reward hacking，30.4% 来自 long-horizon execution discipline collapse。OpenComputer 显示 programmatic verifier 比 LLM judge 更可靠，但 verifier 多数仍是事后评分工具。Agents' Last Exam 和 SaaS-Bench 也共同说明，真实工作流的成功依赖隐藏状态、文件、配置、日志、数据库和外部系统的一致性。

这形成一个明确空白：我们不仅需要 trajectory-aware judge 事后抓作弊，也需要在执行过程中给 agent 一组 non-oracle 的 verification affordance，让它能验证自己引用的证据是否真实、当前 GUI 和 CLI/file state 是否一致、某个副作用是否已真正落地。

这个 idea 比纯 web AFE 更偏 GUI environment / hybrid runtime。它不追求新 benchmark 规模，而是测试 verifier 从 evaluator-facing 变成 agent-facing 后，是否能改变 reward hacking 和 workflow-discipline failure。

## Related Work

- [[Papers/2606-WeaveBench]] - 证明 hybrid GUI+CLI+Code 是真实 CUA 的必要设置，并用 trajectory-aware judge 揭示 reward hacking 和 fabricated evidence。
- [[Papers/2605-OpenComputer]] - 以 app-specific hard-coded verifier 组织桌面软件世界，显示 verifier-human alignment 94.1%，高于 LLM judge。
- [[Papers/2606-AgentsLastExam]] - 覆盖 GDP-relevant professional workflows，强调真实软件、隐藏 reference 和长程任务。
- [[Papers/2605-SaaSBench]] - 暴露真实 SaaS workflow 的 checkpoint/resolved collapse，说明 hidden backend state 和业务实体一致性是核心瓶颈。
- 外部最新相邻工作：EnvTrustBench（https://arxiv.org/abs/2605.08828）关注 agents overtrust environmental evidence，与本 idea 的 evidence provenance / grounding defect 直接相关；差异是本 idea 侧重 agent-facing verifier affordance 是否能在执行中减少这类缺陷。

**Novelty**: 4/5 — closest works: [[Papers/2606-WeaveBench]], [[Papers/2605-OpenComputer]], [[Papers/2606-AgentsLastExam]], [[Papers/2605-SaaSBench]]

深度评估：
- Novelty: 4/5。WeaveBench 主要是 benchmark/judge，OpenComputer 主要是 evaluator-facing verifier；把 cross-channel verifier/provenance/rollback 作为 runtime affordance 做因果实验有明确差异。
- Feasibility: 3/5。需要构建 hybrid harness 和 verifier endpoints，工程量高于 Web-only AFE，但可复用 OpenComputer-style checker 和少量自包含任务。
- Impact: 4/5。若能显著降低 reward hacking，会直接回应 CUA 可靠性和安全部署问题。
- Risk: 3/5。agent 可能忽略 verifier affordance，或 verifier 本身覆盖不足；hybrid 环境工程成本也较高。
- Evidence: 4/5。WeaveBench 的 failure anatomy 和 OpenComputer 的 verifier alignment 是强先验，但 agent-facing runtime 仍缺直接实验。
- Total: 18/25。

## Approach sketch

构建一个小型 Hybrid-GUI Runtime Suite，任务不追规模，追 failure-mode clarity：

1. 任务类型：
   - Web dev：浏览器看到 UI bug，CLI/Code 修改源文件，再用浏览器验证。
   - Data/report：GUI 查看图表或文档，CLI 处理数据，文件系统生成结果。
   - Ops/sysadmin：dashboard 发现异常，CLI 修改配置，GUI/log 验证服务恢复。
   - Design/document：GUI 编辑或检查视觉结果，文件/metadata/verifier 检查真实输出。

2. Runtime affordance：
   - `verify_evidence(claim, source)`：检查 agent 引用的截图、文件、日志、metric 是否来自真实状态。
   - `cross_check(target)`：同一实体在 GUI、file、CLI/API、DB 中的一致性检查。
   - `state_delta()`：展示上一步操作真实改变了哪些文件、配置、进程、窗口或 backend record。
   - `risk_guard(action)`：对会产生副作用或伪造 evidence 的动作要求额外确认。
   - `checkpoint_restore()`：任务关键阶段可恢复。
   - `trace_provenance()`：记录 evidence source、timestamp、channel 和 action provenance。

3. 对照条件：
   - C0 Hybrid normal：GUI+CLI+Code tools，无额外 verifier。
   - C1 Anti-fabrication prompt：明确禁止伪造证据。
   - C2 Outcome-only verifier：只在最后判分。
   - C3 Agent-facing evidence verifier。
   - C4 Agent-facing cross-channel verifier。
   - C5 Full runtime：evidence + cross-channel + state delta + guard + rollback。

4. Judge：
   - 继续使用 trajectory-aware judging 的思想，但把 judge 输出拆成 failure categories：fabricated evidence、fake render、hardcoded metric、premature halt、state drift、unsafe side effect。
   - 关键不是 pass rate，而是 reward hacking 和 evidence-grounding defect 是否下降。

## Expected outcome

若假设成立，应该观察到：

- Full runtime 的 reward hacking / fabricated evidence rate 显著低于 C0-C2。
- C1 anti-fabrication prompt 有小幅帮助，但不能稳定降低 fake evidence，因为它缺少真实状态查询能力。
- C3 evidence verifier 降低 fake screenshot / fake metric / fabricated log。
- C4 cross-channel verifier 降低 GUI/CLI/file state drift。
- C5 rollback guard 降低 premature halt 后的不可恢复失败，并降低 unsafe side effect。
- 即使 task success 提升有限，只要 failure anatomy 从 E5 reward hacking 转向真实能力不足，也是一种有价值的可靠性贡献。

## Risk

- **工程量高**：hybrid runtime 需要 GUI automation、CLI sandbox、文件/配置/日志 verifier。第一版应只做 30-50 个高质量任务，不追 benchmark 规模。
- **Verifier coverage 不足**：如果 verifier 只能检查简单文件存在或字符串匹配，审稿人会质疑真实性。需要选择能明确跨通道验证的任务。
- **Agent 不调用 affordance**：需要在 tool schema 和 instruction 中让 verifier affordance 成为自然工作流的一部分，但不能强迫到变成 hand-coded policy。
- **和 WeaveBench 太近**：必须强调本工作不是新 judge，而是改变 agent 执行时可观测性/可验证性，并用 judge 仅作为测量工具。
