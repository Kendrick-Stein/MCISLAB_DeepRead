---
date: 2026-07-03
tags: [computer-use, gui-agent, agentic-RL, VLA, world-model]
---
# Autoresearch All-Topics Update

## State

- 当前 `agenda` 的 primary direction 仍是 **Agent-Facing Environment Runtime**；GUI Grounding Robustness 是 secondary high，RL-based GUI Agent Training 仍被 credit-assignment 拥挤度约束。
- 本轮按 all-topics recent-window pulse 执行：`fetch_and_score.py --date 2026-07-03 --days 3` 合并 HF、OpenAlex、CVF 后得到 54 篇候选。arXiv API 返回 429，Lexmount key 未设置，但 HF/OpenAlex/CVF 已足够支撑分流。
- 上轮遗留队列有 6 篇；本轮消化最高优先级的 `Dockerless`，新增 `AgenticSTS`，其余新信号进入 queue/watchlist。

## New Signal

### 1. AFE verifier 不必只能是 hidden oracle

[[Papers/2606-Dockerless]] 的核心模式是：verifier 先提出少量诊断问题，再让 read-only sub-agents 进入环境找证据，最后由 judge 聚合 verdict。它在 SWE 里用代码文件和 reference patch 工作，但对 AFE 更重要的是抽象：

- verifier 输入不该只是最终状态或一行 success label；
- verifier 可以要求环境提供可审计 evidence object；
- reward / SFT filter 可以来自 evidence-grounded verifier，而不是必须跑昂贵的 hidden test suite。

这提示 AFE-MiniSuite 应把 verifier 设计成三层：agent-safe observations、read-only verifier evidence、hidden oracle label。实验应测“evidence verifier 是否接近 oracle，同时比 prompt-only feedback 更能提升 recovery / stop / avoid-false-completion”。

### 2. Memory/context 是 runtime contract，不是越长越好

[[Papers/2607-AgenticSTS]] 对 AFE 的贡献不在 Slay the Spire 2 本身，而在 “每步 prompt 由 typed layers 组成” 这个 contract：

- L1/L2 是 protocol/schema；
- L3 是环境规则；
- L4 是 episodic summaries；
- L5 是 triggered skills；
- raw transcript 不跨决策无限追加。

GUI/CUA runtime 也需要类似分层：visible UI tree / screenshot evidence、recent failed action summary、retrieved app manual、task-progress verifier notes、stop/recovery skills。否则“给 agent 更多历史”既不可控，也难以判断收益来自哪一种证据。

### 3. 全域候选正在分化为三条后续线索

1. **Verifier / reward-source**：Dockerless、QVal、PolicyGuard、Decodable Is Not Grounded。这里最贴近 AFE 的是 evidence object 和 verifier feedback。
2. **Long-horizon memory / skill / horizon scaling**：AgenticSTS、Agents-A1、Managing Procedural Memory。这条线提醒 AFE 需要 bounded context 与可审计 skill/memory 更新，而不是无限轨迹日志。
3. **VLA / world-action / embodied transfer**：ABot-M0.5、Domain Arithmetic、Does VLA Even Know the Basics、Learning to Move Before Learning to Do。这些对 `VLA-Survey` 有价值，但不应压过当前 primary AFE。

## Collected Papers

| Status | Paper | Note / Reason |
|--------|-------|---------------|
| digested | Dockerless: Environment-Free Program Verifier for Coding Agents | [[Papers/2606-Dockerless]] |
| digested | AgenticSTS: A Bounded-Memory Testbed for Long-Horizon LLM Agents | [[Papers/2607-AgenticSTS]] |
| queued | Scaling the Horizon, Not the Parameters: Reaching Trillion-Parameter Performance with a 35B Agent | horizon scaling / long trajectory infrastructure |
| queued | Does VLA Even Know the Basics? Measuring Commonsense and World Knowledge Retention in VLA Models | VLA knowledge retention |
| queued | Managing Procedural Memory in LLM Agents | memory / skill benchmark |
| queued | QVal: Cheaply Evaluating Dense Supervision Signals for Long-Horizon LLM Agents | dense reward/verifier evaluation |
| queued-low | ABot-M0.5, Domain Arithmetic, Learning to Move Before Learning to Do | VLA/world-action, lower current priority |
| skipped duplicate | Qwen-AgentWorld, OpenRath, LUMOS, PersonaVLM, GraphVLM, ActiveVLA, CoA-VLA, MoMa-Kitchen, FedVLA | existing notes / recent reports |

## Topic Updates

### Agent-Facing Environment Runtime

Dockerless + AgenticSTS jointly push AFE from “state API” toward “bounded evidence contract”。一个 AFE observation 不应只是 DOM/UIA dump，而应回答：本步 decision 允许 agent 看到哪些 typed evidence？哪些 evidence 只能 verifier 看？哪些 evidence 会写入 long-horizon memory？哪些 recovery/stop skill 会被触发？

### GUI Grounding Robustness

本轮没有新增 grounding-only 精读，但 `Decodable Is Not Grounded` 仍是下一轮重要候选。它的 blank-image arbiter 与 [[Ideas/EvidenceDependence-GUIGrounding]] 同向，可用于区分“可线性解码”与“真实视觉依赖”。

### RL-based GUI Agent Training

`TRIAGE` 和 `QVal` 都指向 dense/process reward，但 credit assignment 子方向此前已因拥挤被降级。本轮判断：只保留 `QVal` 作为 verifier-evaluation 视角，暂不恢复 TRIAGE 深读，除非 Supervisor 明确要重启 credit assignment。

### VLA / Embodied / World Model

`Does VLA Even Know the Basics?` 比 ABot-M0.5 更值得先读，因为它不是又一个 VLA architecture，而是诊断 VLA fine-tuning 后 commonsense/world knowledge retention 的协议。对 VLA survey 来说，这更可能提供跨模型适用的 evaluation insight。

## Next Action

下一轮优先级建议：

1. `Decodable Is Not Grounded`：补强 GUI/VLM evidence-dependence 诊断。
2. `QVal`：判断 dense supervision signal 如何被 cheaply evaluated，服务 AFE verifier/reward design。
3. `Does VLA Even Know the Basics?`：更新 VLA survey 的 evaluation/retention 线索。

不要急着读 `Agents-A1`，除非需要专门整理 long-horizon trajectory scaling。它可能更像系统工程 scaling report，而不是当前 AFE 机制缺口。
