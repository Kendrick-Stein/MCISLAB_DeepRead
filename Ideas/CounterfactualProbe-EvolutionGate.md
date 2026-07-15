---
title: "Counterfactual Probe Gating for Self-Evolution Steps"
tags: [agentic-RL, LLM, research-idea]
status: raw
linked_project:
date_updated: "2026-07-14"
---
## Hypothesis

若对自演化 agent 的每个候选演化产物（memory entry / skill patch / workflow edit），从其**触发条件**自动合成两类 probe 任务——(i) 靶向 probe（产物声称应改善的任务邻域）与 (ii) **反事实不变性 probe**（触发边界外、行为不应改变的任务邻域）——并以"target 提升 ∧ invariance 保持"作为准入判据，则在固定验证预算下，probe-gate 相比 score-based gate 能把 **gating frontier 显著外推**。

可证伪预测：

- 在同一演化 loop 上，probe-gate 的 asset 存活率相比 ABot 式 aggregate regression gate（实测 1/16 ≈ 6%）提升 ≥3x，同时 misevolution 事件率（unsafe rate / reward hacking，按 [[Papers/2509-Misevolution]] 协议测量）不高于 score-based gate；
- invariance probe 能抓到 score-based gate 系统性漏掉的**跨域 side effect** 案例（在验证分布外生效的有害产物）；
- 若 probe-gate 与 score-based gate 的 capability-safety frontier 重合（同等预算下无外推），则假设被证伪。

## Motivation

**知识空白**：[[Topics/SelfEvolvingAgents-Survey]] Open Problem 2 明确指出"演化步验证机制"无系统工作——四条演化路线中只有 tool/skill 路线内建 validation gate，而风险实测最重的 memory/model 路线基本不设关口。

**Endure/Evolve 张力的第一手实证**：[[Papers/2607-ABotAgentOS]] Table 9 显示保守双重 gate（target gain ∧ regression tolerance）下 16+ 候选 asset 只存活 1 个、三个 benchmark 总增益 +0.4~1.2——安全 gate 现阶段"几乎不长肉"。外部工作 [PACE](https://arxiv.org/abs/2606.08106)（anytime-valid e-process commit gate）从统计上严格化了 accept/reject，但自认"安全的代价是统计功效"。两者共同暴露 score-based gating 的结构性缺陷：**在 target metric 上堆样本换置信度，对验证分布外的 side effect 先天盲视**——而 [[Papers/2509-Misevolution]] 恰恰证明危害多发生在 target metric 之外（safety 维度、跨域泛化）。

**为什么是 counterfactual probe**：vault 已 validated 的"counterfactual 诊断 pattern"（3 独立数据点，见 [[Ideas/EvidenceDependence-GUIGrounding]] 与 [[Papers/2606-DecodableNotGrounded]]）在 GUI grounding 域证明：测"不该变时是否真的不变"比测"该变时变了多少"信息量更高。把该 pattern 迁移到演化步验证是自然的跨域移植：产物的危害本质是**作用范围越界**，而越界恰好只能用反事实不变性测出来。

**时机**：ABot 的受约束 JSON DSL asset（显式声明 trigger condition、target layer、允许动作）恰好提供了可自动合成 probe 的结构化产物形式——2025 年以前的演化产物（自由文本 memory、任意代码 patch）不具备这个条件。

## Related Work

- [[Papers/2607-ABotAgentOS]] — split-wise 双重 gate 的完整 trace（1/16 存活），本 idea 的直接对照 baseline 与 DSL asset 形式来源
- [[Papers/2509-Misevolution]] — 四路径 misevolution 实证；其"危害发生在 target metric 之外"的发现是 invariance probe 的动机；safety 测量协议直接复用
- [[Papers/2605-SkillOpt]] — skill 路线 validation gate 的代表（bounded edits + gate），但 gate 仍是 target-score-based
- [[Papers/2508-SelfEvolvingAIAgentsSurvey]] — Three Laws（Endure > Excel > Evolve），本 idea 是把 Endure 约束机制化且不牺牲 Evolve 的尝试
- 外部：[PACE (arXiv 2606.08106)](https://arxiv.org/abs/2606.08106) — anytime-valid acceptance test，target-metric 配对检验的统计上界；[Two-Gate 统计保证 (arXiv 2510.04399)](https://arxiv.org/abs/2510.04399)、[信息论极限 (arXiv 2603.28650)](https://arxiv.org/abs/2603.28650) — gate 理论；均不含 side-effect scoping 机制

**Novelty**: 4/5 — closest works: PACE（外部，target-metric e-process gate）, [[Papers/2607-ABotAgentOS]]（aggregate regression gate）, [[Papers/2605-SkillOpt]]（skill validation gate）, [[Papers/2509-Misevolution]]。差异点：现有 gate 全部在 target/protected metric 的**分数**上做检验；本 idea 检验产物的**作用范围**（behavioral invariance outside trigger boundary），是 mechanism-aware 而非 score-based 的准入判据，无先例。

## Approach sketch

1. **Testbed**：复现一个轻量演化 loop——memory 路线用 AWM 式 workflow 诱导（[[Papers/2409-AgentWorkflowMemory]]），skill 路线用 SkillOpt 式 bounded edit；产物统一编译为 ABot 式 JSON DSL（trigger condition + 允许动作 + target layer），保证 probe 可合成。
2. **Probe 合成**：对每个候选产物，用 LLM 从 trigger condition 生成 (i) trigger 内任务变体（靶向 probe，k≈5）与 (ii) trigger 边界外的最近邻任务（invariance probe，k≈5——语义相似但不满足触发条件，产物在其上生效即为越界）。
3. **三 gate 对照**（固定验证预算，即总 probe/评估任务数相同）：
   - G1 ABot 式 aggregate gate：ΔS_target ≥ τ_gain ∧ ΔS_reg ≥ −τ_reg（在混合验证集上算总分）；
   - G2 PACE 式配对检验：candidate vs incumbent 在相同实例上的 e-process；
   - G3 probe-gate（本 idea）：靶向 probe 提升 ∧ invariance probe 行为不变（KL/action-match 阈值）。
4. **Ground truth**：每个候选产物在大规模 held-out 评估上判定真益/真害（能力：task SR；安全：[[Papers/2509-Misevolution]] 的 RedCode / Agent-SafetyBench 协议），得到每个 gate 的 precision/recall 与 frontier 位置。
5. **Frontier 扫描**：对各 gate 扫阈值（τ_gain、e-threshold、invariance 容忍度），绘制 capability-gain × misevolution-rate 的 Pareto frontier——这同时回答 survey Open Problem 1 的剂量关系（吸收原"Gating Frontier"候选 idea 作为评估协议）。

与 [[Ideas/HybridVerifier-GUIRuntime]] 的关系：该 idea 把环境 verifier 暴露给 actor 用于**任务执行**；本 idea 把 counterfactual 检验用于**演化产物准入**——同一 AFE verify affordance 的第二应用场景（survey 流程注记所指），时间尺度与作用对象均不同，harness 可共享。

## Expected outcome

- 同等验证预算下，G3 的 asset 存活率 ≥3x G1（从 ~6% 到 ≥18%），misevolution 事件率持平或更低；
- G3 专属检出一批"target 提升但 invariance 越界"的产物——即 G1/G2 会放行的跨域 side effect 案例（定性分析这批案例即论文的 failure-mode 贡献）；
- frontier 图显示 G3 曲线整体外推；若 G3 与 G1/G2 重合，得到的负结果同样可报告：说明演化产物的危害不可由行为不变性预测，必须依赖分数回归——这将直接修正 survey Open Problem 2 的求解方向。

## Risk

- **Probe 合成质量**：LLM 生成的 invariance probe 可能本身有噪声（把 trigger 内任务误标为边界外），引入 gate 的假阴性。缓解：probe 生成后用独立 LLM 校验 + 人工抽检 10%；probe 噪声率作为 ablation 轴报告。
- **产物无结构化 trigger 时不适用**：raw memory entry（自由文本）难以定义触发边界。缓解：第一版限定 DSL-compilable 产物（本身是 ABot 已验证的形式）；将"哪些产物形式可 probe"作为边界发现报告。
- **Ground truth 评估成本**：每个候选产物需要大规模 held-out 判定，总评估量 = 产物数 × 评估集大小。缓解：控制演化 loop 规模（~50-100 个候选产物），复用 Misevolution 的现成协议与任务集；无任何训练需求，纯推理成本。
- **与 PACE 的统计功效对比需公平**：G2 的 e-process 有 anytime-valid 保证而 G3 没有。缓解：G3 可叠加 e-process 到 probe 分数上（probe 定义"测什么"，e-process 定义"何时信"，两者正交可组合——组合版作为 G4 补充对照）。

## Evaluation — 2026-07-14 (idea-generate 深度验证)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 4/5 | PACE/Two-Gate/ABot/SkillOpt 全部 score-based；side-effect scoping via counterfactual invariance probe 无先例。closest works: PACE（外部）, [[Papers/2607-ABotAgentOS]], [[Papers/2605-SkillOpt]], [[Papers/2509-Misevolution]] |
| Feasibility | 3/5 | 无训练需求，但需复现演化 loop + 大量 held-out 评估；probe 合成 pipeline 有工程量 |
| Impact | 4/5 | 直接解决 [[Topics/SelfEvolvingAgents-Survey]] Open Problem 2；Endure/Evolve 张力是 2026 活跃辩论（PACE、2511.21050 均在此空间）；负结果亦有修正价值 |
| Risk | 3/5 | probe 质量与 ground-truth 成本是真风险；核心假设（危害可由不变性越界预测）未经验证 |
| Evidence | 4/5 | ABot Table 9（gate 吃收益）+ Misevolution（危害在 target 外）+ PACE 功效自白 + vault counterfactual 诊断 insight（3 数据点 validated）四路收敛 |
| **Total** | **18/25** | |

**Reasoning**：占据一个刚被理论工作（PACE/信息论极限）圈出但无人给出机制性解法的空白；证据链来自本 vault 两条 validated/provisional insight 的交汇，差异化清晰。短板是 probe 合成质量的不确定性——建议先做 20 个产物的 pilot 验证 probe 可靠性再扩大。
