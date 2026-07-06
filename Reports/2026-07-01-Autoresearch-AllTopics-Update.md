---
date: 2026-07-01
tags: [computer-use, gui-agent, web-agent, agentic-RL]
---
# Autoresearch All-Topics Update

## State

- 当前 `agenda` 的 primary direction 仍是 **Agent-Facing Environment Runtime**；GUI Grounding Robustness 是 secondary high，RL-based GUI Agent Training 是 medium。
- `queue.json` 原为空；本轮 3 天窗口抓取后，新增 8 篇高相关候选，其中 2 篇已精读，6 篇保留为 pending backlog。
- 6/29 刚做过 all-topics pulse，因此本轮采取 delta-only 策略：剔除 `Qwen-AgentWorld`、`OpenRath`、`ArborHTR`、`OSWorld2` 等已覆盖论文，不重复 synthesis。

## New Signal

### 1. AFE 需要 stop / clarify / declare-unresolvable 作为 first-class action

[[Papers/2606-AgenticAbstention]] 的关键价值不是 CONVOLVE 本身，而是把“继续行动是否还有价值”变成可评测的 sequential decision。当前 AFE framing 多强调 observe / map / rollback / verify，但还缺一个停止维度：当环境证据已经说明任务不可解、目标不存在或用户上下文不足时，runtime 应帮助 agent 及时停止、请求澄清或声明不可解。

这会改变 AFE-MiniSuite 的设计：除了 success rate，也应测 **futile exploration rate**、**timely stop recall**、**over-abstention on solvable tasks**。否则一个 runtime 可能通过暴露更多 affordance 让 agent 更会乱试，而不是更可靠。

### 2. Semantic OS layer 是 AFE 的低成本原型路线，但必须强验证

[[Papers/2606-LUMOS]] 证据很薄，但 interface idea 很实用：用 UIA / DOM / accessibility tree 生成 semantic blueprint，agent 对 stable element id 执行 constrained visible action。它提供一个 non-oracle 中间层：不让 agent 调 hidden backend API，也不强迫它从 screenshot 里重建 OS 已经知道的语义。

真正的研究问题不是“accessibility tree 能不能被 LLM 读”，而是它在 OSWorld2 / WindowsWorld 这类 long-horizon workflow 上是否比 screenshot-only、prompt-only 和 direct-API baseline 更可靠。需要特别测 metadata 缺失、重复控件名、custom-rendered UI、动态弹窗和权限确认这些 break condition。

### 3. Verifier / reward / grounding evidence 仍在快速分化

待读队列里有三条值得跟进：

- **Dockerless**：环境免执行 verifier，用 agentic repo exploration 判断 patch correctness，可能对应 AFE 里的 low-cost verifier。
- **PolicyGuard**：sub-agent verifier 共享 dialogue context，并给 remediation feedback，不只是 block action。
- **Decodable Is Not Grounded**：用 blank-image arbiter 证明 linear probe / steering 的 latent knowledge 不等于真实 visual grounding；这和 GUI grounding 的 evidence-dependence 评估高度相关。

这些论文共同提示：AFE 不应该只做“多暴露一点状态”，而要把 evidence object、verifier feedback 和 grounding dependency 做成可审计接口。

## Collected Papers

| Status | Paper | Note |
|--------|-------|------|
| digested | Agentic Abstention: Do Agents Know When to Stop Instead of Act? | [[Papers/2606-AgenticAbstention]] |
| digested | LUMOS: A Semantic Operating-System Layer for Accessibility-Grounded AI Agents | [[Papers/2606-LUMOS]] |
| queued | Dockerless: Environment-Free Program Verifier for Coding Agents | verifier / reward-source |
| queued | GUICrafter: Weakly-Supervised GUI Agent Leveraging Massive Unannotated Screenshots | GUI grounding data |
| queued | Decodable Is Not Grounded: A Vision-Ablation Arbiter for VLM Spatial Reasoning | evidence dependence |
| queued | Xiaomi-GUI-0 Technical Report | real-device GUI agent |
| queued | PolicyGuard: A Dialogue-Grounded Sub-Agent Verifier for Policy Adherence in LLM Agents | verifier / remediation |
| queued | TRIAGE: Role-Typed Credit Assignment for Agentic Reinforcement Learning | agentic RL credit |

## Next Action

下一轮优先读 `Decodable Is Not Grounded` 或 `PolicyGuard`。前者可以直接强化 [[Ideas/EvidenceDependence-GUIGrounding]]；后者更贴近 AFE 的 agent-facing verifier / remediation design。`TRIAGE` 只在 Supervisor 决定恢复 credit assignment 子方向后再深读，否则容易回到已判定拥挤的赛道。
