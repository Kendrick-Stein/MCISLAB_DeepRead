---
title: Ideas
---

## 研究想法孵化

这里存放从论文阅读和 Survey 分析中孵化出的研究想法。每个想法文件包含：

- **Hypothesis**: 可证伪的核心假设
- **Motivation**: 知识空白 + 现有方法局限
- **Proposed Method**: 核心方法设计
- **Experiments**: 验证假设的实验设计
- **Risk Analysis**: 潜在失败点和应对策略

### 想法状态

- `raw`: 初始想法，需要进一步调研验证
- `validated`: 已通过文献调研验证，有差异化空间
- `prototyping`: 正在原型验证
- `archived`: 放弃或合并到其他方向

### 当前活跃想法

| 想法 | 状态 | 来源 | 核心假设 |
|------|------|------|----------|
| [[Ideas/ForkPoint-CreditAssignment-GUI]] | raw | GUIAgent-Survey | Fork-point detection for long-horizon credit assignment |
| [[Ideas/ScaleInvariant-Grounding-GUI]] | raw | GUIAgent-Survey | FPN-like scale handling for GUI grounding |
| [[Ideas/AdversarialVerification-SelfImproving-GUI]] | raw | GUIAgent-Survey | Adversarial verifier for self-improving bias correction |
| [[Ideas/AgentFacing-WebRuntime]] | validated | AgentEnvironment-Survey | Non-oracle runtime affordances for zero-training web agents |
| [[Ideas/HybridVerifier-GUIRuntime]] | raw | GUI Environment / WeaveBench | Agent-facing cross-channel verifier to reduce reward hacking |
| [[Ideas/EvidenceDependence-GUIGrounding]] | raw | VisualFLIP / GUI grounding | Action Collapse Rate for counterfactual GUI evidence dependence |
| [[Ideas/PersonalizedSafety-CUA]] | raw | MyPCBench / BraveGuard | Task-scoped permission + trajectory privacy guard for personal CUA |
| [[Ideas/CounterfactualProbe-EvolutionGate]] | raw | SelfEvolvingAgents-Survey / ABot-AgentOS | Counterfactual invariance probe 作演化步准入判据，外推 gating frontier |
| [[Ideas/RetrievalMediated-MemoryMisevolution]] | raw | Misevolution / Memoir | Memory reward hacking 由检索正反馈介导，改检索不洗内容即可防御 |
| [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] | raw | Reliability-Survey / TRIAGE | 最优恢复动作随 mismatch 点而变，固定策略留下可测量的 recovery-selection gap（2026-07-20 算法强化：分叉标签 = 免疫 PRM-hacking 的 counterfactual 监督；train-with-fork deploy-fork-free） |
| [[Ideas/StateSufficiency-AmnesiaProbe-GUI]] | raw | EvoCUA / context management | 用遗忘探针测 GUI 任务的历史信息充分性边界 |
| [[Ideas/SelfInitiatedFork-GUI]] | veto | AgentRuntimePrimitives-Survey | ~~fork 作为可学习的 agent 动作~~（Supervisor 否决：LtE/PGTS 已覆盖调用学习，属延伸非空白） |
| [[Ideas/RestorationFidelity-BranchGains]] | veto | AgentRuntimePrimitives-Survey OP4 | ~~恢复保真度测量~~（Supervisor 否决：infra 测量问题非算法问题，无亮点） |
