---
title: Agent-Facing Web Runtime Affordances
tags: [gui-agent, web-agent, computer-use, environment, research-idea]
status: validated
linked_project:
date_updated: "2026-06-25"
---
## Hypothesis

若把 WebHarbor / CUA-Gym-Hub 这类环境后台已有的 state、reset、verifier 和 action graph 能力，以 task-agnostic、non-oracle 的 agent-facing affordance 暴露给 web agent，则在 zero-training 条件下，相同模型的 task success、wrong-turn recovery 和 false completion rate 会显著优于 normal browser、static prompt、dynamic prompt，以及 evaluator-only state API baseline。

可证伪预测：
- Full Agent-Facing Runtime 相比 Dynamic Prompt baseline 在 40-60 个 self-hosted web tasks 上 success rate 提升 >=10pp。
- C2.5 Evaluator-only API 只提升判分可信度，不显著改善执行过程；若它和 agent-facing API 提升相同，则本假设不成立。
- Observe/state diff 主要降低 hidden-state mismatch；map 主要降低 navigation drift；rollback 主要提升 wrong-turn recovery；semantic action 主要降低 grounding/execution error。

## Motivation

当前 web/CUA environment 路线已经快速拥挤：WebHarbor 解决真实网站 Docker mirror，CUA-Gym 解决 verifiable RLVR tuple 合成，SaaS-Bench 解决真实 SaaS 长程评测，WebGym / AsyncWebRL 解决大规模 RL 训练吞吐。继续造一个新环境或拼任务规模，容易变成工程和资源竞赛。

但这些工作共同留下一个更窄的空白：环境后台越来越强，可 reset、可 diff、可 verifier、可注入状态；agent 运行时却仍主要靠 screenshot / DOM / prompt 试错。研究价值在于回答：哪些 backend capability 可以安全地变成 agent-facing runtime affordance，而不是 evaluator-only oracle？

这个问题如果成立，会改变 web agent 的 problem formulation：不是只训练 agent 适应人类网页，而是把 web server 设计成 dual-interface environment。它直接连接 GUI Agent DomainMap 中的 long-horizon recovery、verification 和 action grounding 问题，也连接 WorldModel DomainMap 中的 executable state-transition infrastructure。

## Related Work

- [[Papers/2600-WebHarbor]] - 提供本地 Docker mirror、快速 reset、真实网站视觉和深功能，是最适合第一版实验的 web 环境底座。
- [[Papers/2606-CUAGym]] - 通过 task / environment state / reward.py 共生成构造 32K+ verified RLVR tuples；其 state API 主要服务 trainer/reward，而非 agent-facing runtime。
- [[Papers/2605-SaaSBench]] - 显示真实 SaaS 中 checkpoint 能推进但 resolved workflow 崩溃，说明 state tracking、schema grounding、error recovery 是关键 failure mode。
- [[Papers/2601-WebGym]] 和 [[Papers/2606-AsyncWebRL]] - 已经覆盖 large-scale web RL 和 rollout throughput 路线，本 idea 刻意选择 zero-training environment affordance。
- 外部最新相邻工作：Web Agents Should Adopt the Plan-Then-Execute Paradigm（https://arxiv.org/abs/2605.14290）主张 typed website APIs 和 semantic actions，和本 idea 的 semantic action 层相近；差异是本 idea 更强调 state probe、rollback、verifier boundary 和 evaluator-only 对照。

**Novelty**: 3/5 — closest works: [[Papers/2600-WebHarbor]], [[Papers/2606-CUAGym]], [[Papers/2605-SaaSBench]], [[Papers/2601-WebGym]], [[Papers/2606-AsyncWebRL]]

深度评估：
- Novelty: 3/5。typed website API / semantic action 已有相邻外部工作，但把 state diff、rollback、verifier/progress signal 和 evaluator-only control 放进同一套 causal ablation 仍有差异化。
- Feasibility: 4/5。可从 WebHarbor mirror 或 CUA-Gym-Hub mock apps 起步，不需要训练模型；主要工程是 adapter、state probe 和 verifier endpoint。
- Impact: 4/5。若成立，能为 web/CUA environment 研究补上 agent-facingness 维度，并给 benchmark / runtime 设计提供可操作边界。
- Risk: 3/5。最大风险是收益可被 dynamic prompt 复现，或 semantic action 被认为是 RPA shortcut。
- Evidence: 4/5。WebHarbor / CUA-Gym / SaaS-Bench / OpenComputer 都间接支持 state/verifier/fork 的重要性，但 agent-facing 暴露尚无直接证据。
- Total: 18/25。

## Approach sketch

构建一个 Web-only 的 AFE-MiniSuite，优先避免跨平台 scope 膨胀：

1. 环境选择：
   - 2-3 个 WebHarbor mirror：shopping、booking/search、GitHub-like workflow。
   - 或 2-3 个 CUA-Gym-Hub mock apps：commerce、issue tracker、document/workspace app。
   - 总任务量 40-60 个，每个任务有 backend verifier 和 partial checkpoints。

2. Runtime affordance 分层：
   - `observe_state()`：页面可见元素、route、form state、cart/session/app state 摘要、state diff。
   - `get_world_map()`：route graph、page affordance graph、entity schema。
   - `list_affordances()`：当前状态下合法 semantic actions，但不包含 task-specific macro。
   - `checkpoint()` / `restore()`：支持恢复和 branch exploration。
   - `verify_probe()`：task-agnostic progress / consistency probes，如 form valid、cart updated、issue exists、draft saved。
   - `guard()`：危险动作、外部副作用、permission check。

3. 对照条件：
   - C0 Normal browser。
   - C1 Static Prompt。
   - C2 Dynamic Prompt：每步给页面摘要。
   - C2.5 Evaluator-only API：state/verifier 只给 evaluator。
   - C3 Observe、C4 Map、C5 Recover、C6 Semantic Action、C7 Full AFE。

4. 防作弊边界：
   - 允许当前状态、合法动作类别、field validity、entity existence、undo/rollback。
   - 禁止 gold next action、gold trajectory、task-specific macro、direct task completion flag。
   - 记录 state-probe leak rate 和 semantic-action shortcut rate。

## Expected outcome

若假设成立，应该观察到：

- Full AFE 在 success rate、partial credit、steps/token/cost per success 上显著优于 C0-C2。
- C2.5 Evaluator-only API 的最终判分更可信，但执行行为接近 C0-C2。
- 各 affordance 对 failure mode 有选择性作用：
  - Observe/state diff 降低 hidden-state mismatch。
  - Map 降低 navigation drift 和 loop。
  - Recover 提升 wrong-turn recovery。
  - Verifier/progress signal 降低 false completion。
  - Semantic action 降低 grounding/execution error，但不显著提高 shortcut rate。
- 若 prompt-only 能复制大部分收益，则该 idea 应降级为 prompt/interface engineering，而不是 environment contribution。

## Risk

- **Prompt-only baseline 太强**：若动态摘要 + chain-of-thought 已经接近 Full AFE，说明主要收益来自信息展示而非环境能力。必须把 AFE 返回文本原样塞进 prompt 作为强 baseline。
- **被批评为 RPA / hand-crafted skills**：semantic actions 必须来自 route/schema/DOM/API/DB 等通用结构，不为单个任务手写 shortcut。
- **WebHarbor / CUA-Gym-Hub realism 边界**：mock/mirror 结果可能不迁移到 live web。第一版应明确只证明 causal mechanism，后续再做 live-web sanity check。
- **Verifier leak**：progress probe 可能间接泄露答案。需要将 evaluator-only API、agent-safe state probe、hidden task-specific verifier 三层严格分开。

## Evaluation — 2026-06-25 (idea-evaluate, autoresearch round 3)

外部检索更新（WebSearch）：
- **ARE / Gaia2**（ICLR 2026, [arxiv 2602.11964](https://arxiv.org/pdf/2602.11964)）是最接近的环境工作：提供可复用 Verifier、区分 read vs write action（read 不计入 goal、可自由探索），且 Verifier 可用于任意 ARE 环境的 RLVR 训练。但其 Verifier 是 **oracle-based**（对照人工标注），并非把 state/verifier 作为 **non-oracle agent-facing affordance** 暴露给 actor——这正是本 idea 的差异点（C2.5 evaluator-only 对照 + agent-facing affordance 的因果 ablation）。
- "non-oracle verifier" 术语目前主要出现在 PRM/ORM reasoning 文献，环境侧尚无系统把它做成 agent-facing runtime——空白仍在。

五维评估：
- **Novelty**: 3/5 — closest works: [[Papers/2600-WebHarbor]], [[Papers/2606-CUAGym]], ARE/Gaia2 (ICLR 2026), Plan-Then-Execute (typed website API)。环境/verifier 路线拥挤，但"agent-facing non-oracle affordance + evaluator-only 对照"的因果实验框架仍有区分。
- **Feasibility**: 4/5 — 可从 WebHarbor mirror 或 CUA-Gym-Hub mock apps 起步，zero-training，主要工程是 adapter / state probe / verifier endpoint。
- **Impact**: 4/5 — 若成立，为 web/CUA environment 研究补上"agent-facingness"维度，给 runtime/benchmark 设计提供可操作边界；直接支撑 agenda 的 Agent-Facing Environment Runtime 方向。
- **Risk**: 3/5 — 主要失败模式：收益被 strong dynamic-prompt baseline 复现；semantic action 被视为 RPA shortcut。两者均已在 design 中设强对照与防作弊边界。
- **Evidence**: 4/5（↑）— ARE/Gaia2 的 read/write + reusable verifier、OpenComputer 94.1% verifier alignment、ENVS 环境 oracle→SFT 共同强化"环境侧 state/verifier 重要"的先验；agent-facing 暴露仍缺直接实验。
- **Total**: 18/25。

**结论**：raw → **validated**。已通过文献调研验证差异化空间（agent-facing non-oracle affordance + evaluator-only 因果对照），feasibility 高，且是 agenda 新 #1 方向的 lead idea。下一步在 Supervisor 确认方向优先级后可进入 experiment-design（AFE-MiniSuite，C0–C7 ablation）。

**Suggestions**：(1) 实验报告必须包含 ARE/Gaia2 式 read/write action 区分作为对照维度，明确"oracle verifier vs agent-facing non-oracle probe"的差别；(2) 把 strong dynamic-prompt baseline（affordance 文本原样塞入 prompt）作为最关键的 falsification 对照；(3) 优先只做 Web-only causal mechanism，避免跨平台 scope 膨胀。

## Experiments

- [[Experiments/2026-06-25-AgentFacing-WebRuntime]] — AFE-MiniSuite C0–C7 因果 ablation，验证 agent-facing non-oracle affordance 的 success/recovery 增益是否超过 dynamic-prompt 与 evaluator-only 对照
