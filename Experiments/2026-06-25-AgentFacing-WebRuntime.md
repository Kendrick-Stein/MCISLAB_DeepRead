---
title: "AFE-MiniSuite: Causal Ablation of Agent-Facing Web Runtime Affordances"
idea: "[[Ideas/AgentFacing-WebRuntime]]"
tags: [gui-agent, web-agent, computer-use, environment, agent-facing-runtime]
status: planned
date_created: "2026-06-25"
date_completed:
---
## Objective

验证：把环境后台已有的 state / map / rollback / verifier 能力以 **task-agnostic、non-oracle 的 agent-facing affordance** 暴露给同一个 frozen web agent，能在 zero-training 条件下显著提升 task success、wrong-turn recovery 并降低 false completion——且该收益**不能被等强度的 prompt-only baseline 复现**，也**不等同于只把 verifier 给 evaluator（evaluator-only oracle）**。

这是 agenda 方向 **Agent-Facing Environment Runtime**（priority: high）的 lead 实验。

## Setup

- **代码**: 待建 `AFE-MiniSuite` adapter（包裹 [[Papers/2600-WebHarbor]] mirror 或 [[Papers/2606-CUAGym]]-Hub mock apps；harness 复用 [[Papers/2412-BrowserGymAgentLab]] 的 observation/action API 与并行/trace 设施）
- **数据**: 2-3 个 self-hosted web 环境（shopping、booking/search、GitHub-like workflow），共 **40-60 个任务**，每个任务有 backend verifier + partial checkpoints；hidden task-specific verifier 仅用于判分，不暴露给 agent
- **环境**: 单一 frozen 基座 VLM（固定一个 frontier 模型 + 固定 decoding 温度），zero-training；CPU/GPU 仅用于推理与并行 rollout
- **关键参数**: 9 个 runtime 条件 C0–C7（见 Variables）；每条件 × 40-60 任务 × 3 seeds；固定 max-steps / token 预算；除 affordance 文本/工具外，prompt scaffold 完全一致

## Method

### 实验步骤

1. **环境与任务**：搭建 2-3 个 WebHarbor mirror（或 CUA-Gym-Hub mock apps），编写 40-60 个任务，每个任务定义 backend verifier 与 partial checkpoints；冻结一个 hidden evaluator verifier 用于判分。
2. **Affordance 层**：实现 task-agnostic、non-oracle 的 adapter——`observe_state()` + state diff、`get_world_map()`（route/affordance/entity schema）、`list_affordances()`（当前合法 semantic actions，**不含 task-specific macro**）、`checkpoint()/restore()`、`verify_probe()`（form valid / cart updated / issue exists 等 progress probe）、`guard()`。同时埋点记录 **state-probe leak rate** 与 **semantic-action shortcut rate**。
3. **9 个对照条件**：C0–C7 共享同一 frozen 基座与 prompt scaffold，仅 affordance 工具/文本不同。**关键**：C2 Dynamic Prompt 把 affordance 返回文本原样注入 prompt（强 baseline），C2.5 把 state/verifier 仅给 evaluator（不给 actor）。
4. **运行**：所有条件 × 任务 × 3 seeds 全量 rollout；记录 trajectory、backend-verified outcome、cost、anti-cheat 审计。
5. **统计**：计算 primary + secondary metrics（bootstrap CI）；做 per-affordance ablation delta（C3→C4→C5→C6→C7）并映射到目标 failure mode。
6. **Falsification 检查**：对比 C7 vs C2（Dynamic Prompt）、C7 vs C2.5（Evaluator-only）；审计 leak/shortcut rate 是否接近 0。

### Baselines

- **C0 Normal browser**（screenshot/DOM only）— [[Papers/2600-WebHarbor]] / [[Papers/2412-BrowserGymAgentLab]] harness，无任何 affordance
- **C2 Dynamic Prompt**（affordance 文本注入 prompt，无可执行 affordance）— **最关键的 falsification 对照**，隔离"信息展示 vs 环境能力"
- **C2.5 Evaluator-only API**（state/verifier 仅给 evaluator）— ARE/Gaia2 式 oracle verifier，隔离"agent-facingness"
- **(可选) Plan-Then-Execute typed-website-API**（arxiv 2605.14290）— 对照 semantic-action 层

## Results

（实验完成后由 experiment-track 填写）

## Analysis

（待填）

## Insights

（待填）

## Next Steps

- 若**假设不成立**（C2 ≈ C7，gap <3pp，或 C2.5 复现 agent-facing 收益）：本方向应从 "environment contribution" 降级为 **prompt/interface engineering**，并据此修正 [[Ideas/AgentFacing-WebRuntime]] 的 framing；不投入 live-web 扩展。
- 若 semantic action 收益伴随 shortcut rate 上升：判为 RPA，移除 macro 类 affordance，仅保留来自 route/schema/DOM/API/DB 的通用结构动作后重测。
- 若**成立**：扩展到 live-web sanity check（少量真实网站），并把 verifier affordance 与 [[Ideas/HybridVerifier-GUIRuntime]] 的 cross-channel verifier 合并到 hybrid GUI+CLI runtime。

---

## Design Notes

### Variables

- **自变量 (IV)**：runtime 条件（单一维度，基座模型与 prompt scaffold 固定）：
  - C0 Normal browser｜C1 Static Prompt｜C2 Dynamic Prompt（affordance 文本注入）｜C2.5 Evaluator-only API｜C3 +Observe/state-diff｜C4 +Map｜C5 +Recover/rollback｜C6 +Semantic action｜C7 Full AFE
- **因变量 (DV)**：task success rate、partial-credit（checkpoint 进度）、wrong-turn recovery rate、false-completion rate、cost per success、per-affordance failure-mode 计数
- **控制变量 (CV)**：基座模型与温度、40-60 任务集、3 seeds、max-steps/token 预算、环境与 hidden verifier、除 affordance 外的 prompt scaffold

### Metrics

- **主指标 (primary)**：**task success rate**（backend-verifier resolved %，40-60 self-hosted tasks，3 seeds 均值 + bootstrap CI）
- **辅助指标 (secondary)**：
  - **wrong-turn recovery rate**（检测到错误动作后仍完成任务的任务比例 %）
  - **false-completion rate**（agent 声称成功但 hidden verifier 判否的比例 %，越低越好）
  - **cost per success**（tokens×price + steps，归一到每个成功任务）
  - **state-probe leak rate / semantic-action shortcut rate**（anti-cheat 审计，必须 ≈ 0；非性能指标而是有效性门槛）

### Expected Outcome

- **假设成立 (Confirmed)**：
  - C7 Full AFE 的 success rate 相对 **C2 Dynamic Prompt ≥ +10pp（绝对）**；
  - C2.5 Evaluator-only 只提升判分可信度，execution 接近 C0–C2（success rate 无显著提升）；
  - 各 affordance 选择性降低目标 failure mode：Observe/state-diff↓ hidden-state mismatch；Map↓ navigation drift/loop；Recover↑ wrong-turn recovery；Verifier/progress↓ false completion；Semantic action↓ grounding/execution error 且 shortcut rate 不显著上升；
  - leak rate / shortcut rate ≈ 0。
- **假设不成立 (Refuted)**：
  - 若 C2 Dynamic Prompt 与 C7 差距 <3pp → 收益主要来自信息展示，本方向降级为 prompt/interface engineering；
  - 若 C2.5 Evaluator-only 与 agent-facing 条件提升相当 → "agent-facingness" 不成立，假设被否；
  - 若 semantic action 收益伴随 shortcut rate 显著上升 → 判为 RPA shortcut，需重设计 affordance。
  - 三种情形均对应 Next Steps 中的具体修正路径，而非简单放弃。

### Risk & Mitigation

- **风险 1：prompt-only baseline 太强**（medium）→ C2 必须把 affordance 返回文本**原样**注入 prompt；分 failure-mode 报告，证明 executable/stateful 能力（rollback/verify_probe）而非纯信息展示才是增益来源。
- **风险 2：verifier/probe leak 间接泄露答案**（medium）→ 严格三层分离：evaluator-only API / agent-safe non-oracle probe / hidden task-specific verifier；监控 leak rate，超阈值即移除该 probe 重测。
- **风险 3：mock/mirror realism 不迁移 live web**（medium）→ 第一版只证明 causal mechanism，scope 限定 Web-only；成立后再做少量 live-web sanity check。
- **风险 4：近孪生 grader-facing verifier**（"Agentic Reward Modeling: Verifying GUI Agent", arxiv 2602.00575）（low-medium）→ 强调本实验测的是 **actor 自用 agent-facing affordance** 改变执行行为，与 grader-facing 在线核查做因果区分（与 [[Ideas/HybridVerifier-GUIRuntime]] 共享该对照）。

### Memory Reference

- 无专门的 `effective-methods.md` / `failed-directions.md` 文件；参考本会话 2026-06-25 distill 的记忆：
  - insight「Verifier/环境 oracle 正从 evaluator-only 扩展为 agent-facing runtime affordance」([[Workbench/memory/insights]]) — 直接支撑核心假设
  - insight「真实长程工作流远未饱和」([[Workbench/memory/insights]]) — 动机：runtime levers 是提升长程可靠性的杠杆
  - [[Ideas/AgentFacing-WebRuntime]] 自带 Risk Analysis（prompt-only baseline、RPA、verifier leak）已并入上方 Risk & Mitigation

### 2026-06-26 证据更新（daily-papers 折叠）

- **`observe_state()` / C3 Observe affordance 的工程参照**：[[Papers/2606-OpenRath]] 的 "Session-as-first-class-value"——把碎片化 runtime state（transcript / tool effects / sandbox / lineage / memory events）统一为可随程序值流动的 observable `Session`，正是 AFE "observe" affordance 在框架层的具体实现。可借其 `forward(session)->session` 契约设计 `observe_state()` 的返回 schema 与 state-diff；但 OpenRath 仅 technical report、无 benchmark，恰恰说明"暴露 observable state 的因果收益"尚未被实证——即本实验要回答的问题。
- **memory affordance 的空白佐证**：[[Papers/2606-AgentMemorySystem]] 系统评测 12 个 agent memory 系统，但 workload 全为文本/DB、**完全无 GUI/CUA visual memory 场景**——反向印证 agent-facing memory/state 在 computer-use 环境仍是空白，强化本方向的 motivation。若 C3 Observe 成立，可考虑把 state-diff 记忆作为后续独立 affordance 扩展。
- **不改主设计**：以上为 C3 Observe 的实现参照与 motivation 补强，C0–C7 对照结构与 falsification 检查（C2 dynamic-prompt / C2.5 evaluator-only）保持不变。
