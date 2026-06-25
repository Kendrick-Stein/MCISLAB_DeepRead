---
type: discovery
period: "2026-06-25"
date_created: "2026-06-25"
---
## Scope

本轮是在 [[Reports/2026-06-24-Autoresearch-AllTopics-Pulse]] 之后做的 all-topics 增量更新。重点不是重写所有 survey，而是检查 6/24 之后是否有会改变当前 research taste 的新证据，并把 paper / survey / idea 状态补齐。

## Main Update

**最高信号新增论文是 [[Papers/2606-AgentCIBench]]。** 它直接命中 6/24 生成的 [[Ideas/PersonalizedSafety-CUA]]：personal CUA 的风险不是抽象安全话题，而是 normal-use contextual disclosure。Agent 即使没有被攻击，也会因为 visual co-location、task ambiguity、recipient misalignment，把任务外个人状态带到外部输出。

这让当前 mental model 从：

> personal context makes CUA harder

推进到：

> personal context makes CUA both harder and riskier; task success can actively conflict with contextual privacy.

## Topic Updates

### GUI Agent / Computer-Use

- 新增 [[Papers/2606-AgentCIBench]]。
- 更新 [[Topics/ComputerUseAgents-Survey]]：补充 “Personal CUA Safety 从 adversarial 转向 contextual disclosure”。
- 更新 [[Topics/AgentFriendlyEnvironment-Survey]]：新增 least-disclosure affordance 原则。
- 对 agenda 的含义：primary direction 若继续从 pure grounding 扩展到 agent-facing runtime，那么 privacy-aware state API 必须成为一等约束，而不是后加 safety paragraph。

### VLM / Multimodal Grounding

- [[Ideas/EvidenceDependence-GUIGrounding]] 已补充 GUI-Perturbed 外部证据和 18/25 评估。
- 当前判断：Action Collapse Rate 仍有价值，但 novelty 必须避开 VisualFLIP / GUI-Perturbed 的 generic perturbation framing，聚焦 GUI action evidence dependence。

### Agentic RL

- 本轮没有发现足以改变 6/24 判断的新 AgenticRL 论文。
- 方向仍建议从旧的 credit assignment 子方向 pivot 到 verifier-grounded data / reward construction。[[Papers/2606-AgentCIBench]] 间接加强这个判断：agent training/evaluation 需要 context-aware verifier，而不是只优化 task completion reward。

### Embodied AI / World Model

- 本轮没有新增 digest。6/24 的 [[Papers/2601-TMoW]] 仍是主要 world-model update。
- 对 GUI/CUA 的迁移启发仍是 runtime model routing：不同 app/site/personal context 可看作不同 transition / privacy regimes。

### Hyperbolic Manifold

- 本轮未发现与 GUI/VLM/AgenticRL 主线直接相连的新信号，继续暂停主动跟进。

## Idea Status

| Idea | Update | Score |
|---|---|---|
| [[Ideas/PersonalizedSafety-CUA]] | 加入 [[Papers/2606-AgentCIBench]]，novelty 下调但 evidence/impact 上调；核心应转为 runtime intervention | 20/25 |
| [[Ideas/EvidenceDependence-GUIGrounding]] | 加入 GUI-Perturbed 外部证据；定位为 action-level paired UI flip benchmark | 18/25 |

## Key Takeaways

1. **Agent-friendly env 不能默认等于 more state**：state API 如果不受 task scope / recipient / data category 约束，会直接放大 personal disclosure risk。
2. **CUA safety 的核心对象正在变成 trajectory + externally visible output**：中途访问、最终输出、收件人语境都需要测。
3. **PersonalizedSafety-CUA 比 6/24 看起来更重要，但也更拥挤**：AgentCIBench 已经占住 evaluation；可做空间在 runtime guard / permission manifest / intervention ablation。
4. **EvidenceDependence-GUIGrounding 仍适合做轻量 pilot**：只要贡献限定在 GUI action collapse，而不是泛泛 counterfactual VLM evaluation。

## Next Actions

1. 若继续 AFE 方向，优先设计 least-disclosure `observe_state()` schema：task scope、recipient scope、data categories、source provenance。
2. 对 [[Ideas/PersonalizedSafety-CUA]] 做下一轮 experiment-design：选 AgentCIBench/OpenApps-like 环境，定义 manifest-only vs trajectory-guard ablation。
3. 对 [[Ideas/EvidenceDependence-GUIGrounding]] 做 100-pair pilot spec，先证明 ACR 是否能暴露现有模型 failure。

## External Evidence Checked

- [AgentCIBench / Capable but Careless](https://arxiv.org/abs/2606.23189)
- [GUI-Perturbed](https://arxiv.org/abs/2604.14262)
- [VisualFLIP](https://arxiv.org/abs/2606.07872)
- [MyPCBench](https://arxiv.org/abs/2606.16748)
- [BraveGuard](https://arxiv.org/abs/2606.01166)
- [Permission Manifests for Web Agents](https://arxiv.org/abs/2601.02371)
