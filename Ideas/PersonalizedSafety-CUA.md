---
title: Personalized Safety for Computer-Use Agents
tags: [computer-use, gui-agent]
status: raw
linked_project:
date_updated: "2026-06-25"
---
## Hypothesis

在 personal computer-use environments 中，安全风险主要来自“授权内越界”：agent 已被允许操作电脑，但在完成任务时访问、引用或泄漏了与任务无关的个人状态。我们假设结合 **task-scoped permission manifest + trajectory-level privacy guard**，可以显著降低 personalization leakage，同时不明显损害任务完成率。

## Motivation

[[Papers/2606-MyPCBench]] 指出真实 personal assistant 必须处理 logged-in-like accounts、历史数据和跨应用个人上下文；[[Papers/2606-BraveGuard]] 指出 CUA 安全风险常在多步 trajectory 中出现，prompt-level guard 看不见。两者合起来暴露一个高价值空白：personal CUA 的风险不一定是明显恶意行为，而是“看了不该看的东西”“把无关个人信息带进回答”“为完成当前任务过度搜索私有状态”。

这比通用 prompt injection 防御更接近真实部署。用户已经授权 agent 操作，但授权应当是 task-scoped，而不是全盘读写。

## Related Work

- [[Papers/2606-MyPCBench]] - personal context benchmark，暴露 logged-in-like assistant 场景。
- [[Papers/2606-BraveGuard]] - trajectory-level guard training，强调 execution trace safety。
- [[Papers/2606-AgentCIBench]] - contextual integrity benchmark，证明 normal-use CUA 会发生 context-inappropriate disclosure，平均 leakage 67.9%。
- [[Papers/2512-PermissionManifestsWebAgents]] - permission manifest 思路，可作为 task scope 表达基础。
- [[Ideas/HybridVerifier-GUIRuntime]] - agent-facing verifier，用于减少 reward hacking；本 idea 更关注 privacy/safety。

**Novelty**: 3/5。AgentCIBench 已直接覆盖 personal CUA 的 contextual disclosure evaluation，因此“发现这个风险 / 定义 leakage benchmark”不再新；仍有差异化的是 task-scoped permission manifest + trajectory privacy guard 作为 runtime intervention，而不是离线评测。

## Evaluation — 2026-06-25

**Novelty**: 3/5 — closest works: [[Papers/2606-AgentCIBench]], [[Papers/2606-MyPCBench]], [[Papers/2606-BraveGuard]], [[Papers/2512-PermissionManifestsWebAgents]]

AgentCIBench 明确提出 CUA contextual integrity / inappropriate disclosure benchmark，直接压低 novelty。剩余创新空间在于把 AgentCIBench 的 disclosure taxonomy 变成 agent-facing permission / guard protocol，并测 runtime intervention 对 leakage 和 task utility 的因果作用。

**Feasibility**: 4/5 — 可用 MyPCBench/OpenApps-like simulated apps 或小型 web workspace 起步，不需要训练 base CUA。主要工程是 manifest schema、trajectory annotation、guard integration 和 leakage scorer；比构建完整 OSWorld 规模 benchmark 可控。

**Impact**: 5/5 — AgentCIBench 证明 task completion 不是 privacy safety proxy，personal CUA 正在进入真实产品场景；如果能降低 leakage 且保持 utility，会直接服务部署前 safety evaluation 和 runtime policy。

**Risk**: 3/5 — 主要风险是与 AgentCIBench mitigation 过近、manifest 变成人工规则工程、guard 过保守导致 utility drop。可通过强 baseline（AgentCIBench mitigations / prompt-only / output-only guard）和 process-level trajectory metric 区分。

**Evidence**: 5/5 — [[Papers/2606-MyPCBench]] 证明 personal context 是 CUA 能力轴，[[Papers/2606-AgentCIBench]] 直接证明 contextual disclosure 高发，[[Papers/2606-BraveGuard]] 支持 trajectory-level guard 比 prompt-level guard 更合适，[[Papers/2512-PermissionManifestsWebAgents]] 提供 permission manifest 设计先例。

**Total**: 20/25。

**Reasoning**: 这个 idea 的问题重要性被 AgentCIBench 强力验证，但 novelty 从“定义问题”转移到“runtime intervention”。最值得做的版本不是再造一个 AgentCIBench，而是在其 failure modes 上加入 task-scoped manifest、trajectory guard、confirmation / rollback policy，验证 leakage 是否下降、utility 是否保持、以及哪些 context norms 无法由静态 manifest 表达。

**Suggestions**:

- 先把 AgentCIBench 的 VCL / TAO / RMA 三类 failure mode 映射到 manifest fields：allowed data categories、recipient scope、shareable fields、confirmation-required outputs。
- 用 output-only guard、prompt-only mitigation、manifest-only、manifest+trajectory guard 做四组 ablation。
- 增加 process-level metric：out-of-scope inspection rate，避免只看 final answer leakage。

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
