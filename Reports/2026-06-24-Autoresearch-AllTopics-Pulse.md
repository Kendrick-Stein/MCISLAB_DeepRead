---
type: discovery
period: "2026-06-24"
date_created: "2026-06-24"
---
## Highlights

1. **Computer-use evaluation 正从 generic benchmark 走向 situated deployment**：[[Papers/2606-MyPCBench]] 加入 personal context/logged-in-like state，[[Papers/2606-LabOSBench]] 加入 scientific instrument control，说明真实 CUA 的难点是多应用、个人上下文、专业参数反馈，而不只是屏幕点击。
2. **可靠性评估正在从结果正确转向证据依赖与轨迹安全**：[[Papers/2606-VisualFLIP]] 用 paired flip 测 VLM 是否依赖关键视觉证据，[[Papers/2606-BraveGuard]] 用 trajectory-level supervision 训练 computer-use guard。两者共同指向 counterfactual/trajectory evaluation。
3. **Agentic RL 和 World Model 都在系统化**：[[Papers/2606-AgentJet]] 说明 agent RL 进入 distributed swarm infrastructure 阶段，[[Papers/2601-TMoW]] 则说明 world model adaptation 可通过 test-time mixture routing 处理，而不只是继续堆 video model scale。

## Progress by Direction

### GUI Agent / Computer-Use

- **本轮做了什么**: 新增 [[Papers/2606-MyPCBench]]、[[Papers/2606-LabOSBench]]、[[Papers/2606-BraveGuard]]，并将已有 [[Papers/2606-ENVS]] 纳入本轮综合。
- **关键发现**: GUI/CUA frontier 正从 OSWorld-style general desktop 转向三类高价值环境：personal assistant、多应用专业工作流、trajectory-level safety。benchmark 的 realism 不再只是 live vs simulated，而是是否包含 personal state、permission boundary、feedback-driven adjustment 和 recoverable perturbation。
- **下一步**: 把 MyPCBench 的 personalization leakage 与 BraveGuard 的 trajectory safety 合并成一个可评估 runtime protocol。
- **需要 Human 决策**: 是。是否把 primary direction 从纯 grounding robustness 扩展为 “agent-facing runtime + safety/privacy verifier”？

### VLM / Multimodal Grounding

- **本轮做了什么**: 新增 [[Papers/2606-VisualFLIP]]。
- **关键发现**: 单点 accuracy 不足以证明模型真的 grounded；paired perturbation + Collapse Rate 是更强的证据依赖测试。这个 formulation 可直接迁移到 GUI grounding：同一 instruction 下最小改动 UI 证据，如果模型仍点击同一位置，就是 action collapse。
- **下一步**: 在 [[Ideas/ScaleInvariant-Grounding-GUI]] 之外新增 “Action Collapse Rate” 类 counterfactual grounding idea。
- **需要 Human 决策**: 否。

### Agentic RL

- **本轮做了什么**: 新增 [[Papers/2606-AgentJet]] 和 [[Papers/2606-ENVS]]。
- **关键发现**: ENVS 证明 verified search + balanced SFT 可以绕开部分 online RL 不稳定性；AgentJet 则证明如果继续做 RL training，会越来越像 distributed systems problem。没有新的 reward/verifier insight，单纯做 training framework 竞争会很重。
- **下一步**: 优先研究 verifier-grounded data construction 和 trajectory selection，而不是再造 RL framework。
- **需要 Human 决策**: 是。是否同意放弃旧的 credit assignment 子方向，转向 verifier-grounded reward/data construction？

### Embodied AI / World Model

- **本轮做了什么**: 新增 [[Papers/2601-TMoW]]，作为 WorldModel 与 Embodied Agent 的交叉补充。
- **关键发现**: TMoW 的 test-time mixture routing 说明 world model adaptation 不必完全依赖单模型 scale。对 GUI/desktop agent 也有启发：不同 app/site 可以视作不同 transition regimes，runtime 可根据 state/domain 选择或混合 app-specific transition/verifier models。
- **下一步**: 在 Agent-Friendly Environment proposal 中加入 “runtime model routing” 作为长期 extension，而不是当前最小实验。
- **需要 Human 决策**: 否。

### Hyperbolic Manifold

- **本轮做了什么**: 做了轻量检索，未发现与当前 GUI/VLM/AgenticRL 主线直接相关的高信号 2026-06 新论文。
- **关键发现**: 当前主线产出更集中在 CUA environment、安全、VLM counterfactual grounding 和 agent RL infrastructure；Hyperbolic 方向本轮不应强行跟进。
- **下一步**: 暂停，除非出现能服务 GUI hierarchy / UI graph / memory routing 的明确连接。
- **需要 Human 决策**: 否。

## New Discoveries

| Paper | Why it matters | Direction |
|---|---|---|
| [[Papers/2606-MyPCBench]] | personal context / logged-in-like state 是 real assistant 缺口 | GUI/CUA |
| [[Papers/2606-LabOSBench]] | scientific instrument control 把 CUA 接到 auto-research execution | GUI/CUA, AutoResearch |
| [[Papers/2606-BraveGuard]] | trajectory-level guard 比 prompt-level safety 更贴合 CUA | GUI/CUA Safety |
| [[Papers/2606-VisualFLIP]] | paired flip + Collapse Rate 可迁移为 GUI Action Collapse Rate | VLM, Grounding |
| [[Papers/2606-AgentJet]] | agent RL 正进入 swarm infrastructure 路线 | AgenticRL |
| [[Papers/2601-TMoW]] | test-time mixture routing 是 world model adaptation 的简洁路径 | WorldModel |
| [[Papers/2606-ENVS]] | verified search + balanced SFT 是比直接 online RL 更稳定的数据路线 | AgenticRL, GUI |

## Synthesis

这轮横向扫描后的 mental model 更新是：**GUI/CUA 的下一阶段不是单纯更强模型，而是 environment-native evidence loop**。这里的 evidence 有四种形式：

1. **State evidence**: MyPCBench 里的 personal context、LabOSBench 里的 instrument state。
2. **Counterfactual evidence**: VisualFLIP 的 same-question visual flip，可迁移到 GUI action flip。
3. **Trajectory evidence**: BraveGuard 的 trajectory-level risk supervision，ENVS 的 successful-leaf filtering。
4. **System evidence**: AgentJet/AsyncWebRL 这类 infrastructure 说明 agent training 的瓶颈在 runtime heterogeneity、fault tolerance、context overhead。

因此，比起继续问“模型如何从截图中预测下一个动作”，更重要的问题是：**环境能否以 non-oracle、privacy-aware、actionable 的方式暴露足够证据，让 agent 学会、验证并安全恢复？**

## Candidate Ideas Spawned

- [[Ideas/EvidenceDependence-GUIGrounding]]: 将 VisualFLIP 的 paired flip 改造成 GUI Action Collapse Rate，测 grounding 是否真的依赖 UI 证据。
- [[Ideas/PersonalizedSafety-CUA]]: 结合 MyPCBench 与 BraveGuard，研究 personal CUA 中的 privacy-aware trajectory guard。

## Questions for Human

1. 是否同意把 GUI primary direction 从 “grounding robustness” 扩展为 “evidence-dependent grounding + agent-facing runtime verifier”？
2. RL Training 是否正式从 credit assignment pivot 到 “verified search / balanced data construction / runtime verifier”？
3. 对 personal assistant safety 方向，是否愿意优先做小规模 benchmark/protocol，而不是等完整环境？

## Resource Usage

- Papers read: 6 篇新增 abstract-level digest + 1 篇已有 ENVS 纳入综合。
- Reports created: 1。
- Ideas created: 2。
- API tokens consumed: 未统计。
