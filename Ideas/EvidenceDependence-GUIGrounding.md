---
title: Evidence-Dependent GUI Grounding
tags: [gui-agent, VLM]
status: raw
linked_project:
date_updated: "2026-06-25"
---
## Hypothesis

如果一个 GUI grounding 模型真正依赖 task-critical UI evidence，那么在保持 instruction 不变、仅最小修改目标元素证据的 paired UI screenshots 中，它应当随证据变化更新 action；我们假设 **Action Collapse Rate** 能比单点 ScreenSpot accuracy 更早暴露模型的 spurious grounding 和 layout prior。

## Motivation

[[Papers/2606-VisualFLIP]] 说明 VLM 即使答对单张图，也可能不依赖关键视觉证据；当 paired evidence flip 后，模型仍复读原答案。GUI grounding 也有同类问题：模型可能依赖按钮常见位置、文本先验或历史 action pattern，而不是真正识别当前 UI 元素。

这个问题比 +0.3% ScreenSpot SOTA 更重要，因为真实 UI 会个性化、改版、换主题、插入相似 distractor。若模型只是学了位置 prior，长程 agent 会在 UI drift 时稳定犯错。

## Related Work

- [[Papers/2606-VisualFLIP]] - paired perturbation + Collapse Rate，用于测试 evidence dependence。
- [GUI-Perturbed](https://arxiv.org/abs/2604.14262) - domain randomization 测 GUI grounding brittleness，发现 relational instructions 下 accuracy drop 27-56pp，说明单点 GUI grounding benchmark 会隐藏系统性脆弱性。
- [[Papers/2604-AutoGUIv2]] - functional grounding/captioning dichotomy，说明 GUI capability 需要细粒度诊断。
- [[Papers/2504-ScreenSpotPro]] - 更难 OOD grounding benchmark，但仍主要是单点 correctness。
- [[Ideas/ScaleInvariant-Grounding-GUI]] - 关注跨尺度鲁棒性，本 idea 关注 counterfactual evidence dependence。

**Novelty**: 3/5。closest works 已有 VisualFLIP、GUI-Perturbed 和 ScreenSpot-Pro，但把 paired flip 系统化迁移到 GUI action，并定义 Action Collapse Rate，仍有明确差异化。

## Evaluation — 2026-06-25

**Novelty**: 3/5 — closest works: [[Papers/2606-VisualFLIP]], [[Papers/2604-AutoGUIv2]], [[Papers/2504-ScreenSpotPro]]

VisualFLIP 已经定义 paired evidence flip + Collapse Rate；GUI-Perturbed 已经用 controlled perturbation 暴露 GUI grounding brittleness。因此 novelty 不在“用 perturbation 评估 grounding”，而在 action-level paired UI flip、Action Collapse Rate、以及对 GUI element semantics / disabled state / distractor swap 的专门 taxonomy。

**Feasibility**: 4/5 — 可以从 ScreenSpot-Pro / OSWorld-G / synthetic UI variants 抽样构造 200-500 pairs，不需要训练新模型。难点是保证 perturbation minimal、gold action deterministic、编辑 artifact 不成为 confound。

**Impact**: 4/5 — GUI Agent DomainMap 的核心 open question 是 robust grounding；Action Collapse Rate 能解释 single accuracy 高但长程点击失败的问题，比继续追 ScreenSpot 小幅 SOTA 更有诊断价值。

**Risk**: 3/5 — 风险在于 paired UI 构造被质疑不自然，或模型 collapse 不显著。需要用真实 UI edits、人工 ambiguity check、以及 VisualFLIP-style pair accuracy / collapse 双指标降低风险。

**Evidence**: 4/5 — [[Papers/2606-VisualFLIP]] 直接证明 MLLM 会在 task-critical evidence flip 后 collapse；GUI-Perturbed 证明 GUI grounding 对 relation / zoom perturbation 系统脆弱；[[Papers/2604-AutoGUIv2]] 的 plausible distractor failure 进一步支持 GUI-specific diagnostic benchmark 的必要性。

**Total**: 18/25。

**Reasoning**: 这是一个清晰、低成本、能产出 diagnostic insight 的 benchmark idea，但相邻工作已经很近。要成立，必须把贡献从“又一个 perturbation benchmark”收窄到 GUI action evidence dependence：同一 instruction 下，目标证据变化时 action 是否跟着变化。

**Suggestions**:

- 不要先做大数据集；先做 100 pair pilot，按 text swap / position swap / icon-label conflict / disabled state / distractor insertion 五类分层。
- 直接复用 VisualFLIP 的 pair accuracy + Collapse Rate 结构，但把 answer bucket 改成 element/action bucket。
- 与 ScreenSpot-Pro 的 high-resolution / small-target cases 交叉，验证 ACR 是否比 single accuracy 更能预测专业 GUI failure。

## Approach sketch

构建一个小规模 paired GUI grounding benchmark：

1. 从 ScreenSpot-Pro / OSWorld-G / GUI screenshots 中选择目标元素。
2. 生成 paired UI variants，保持 instruction 不变，只最小修改关键 evidence：
   - 交换两个相似按钮的文本；
   - 移动目标与 distractor 的位置；
   - 替换 icon label；
   - 改变 disabled/enabled state；
   - 插入视觉相似但语义错误的控件。
3. 对每个 pair 定义 gold action flip。
4. 评估模型：
   - pair action accuracy：两侧都点对；
   - Action Collapse Rate：至少一侧正确时，两侧是否预测同一 action bucket；
   - evidence sensitivity：action change 是否落在正确 UI element 上。

先不追求大规模，目标是证明现有强 GUI models 在 paired UI evidence 下 collapse 明显，并分析 collapse 类型。

## Expected outcome

预期观察：

- 现有 GUI grounding 模型的 single accuracy 高于 pair accuracy；
- 对相似 icon、位置交换、disabled state 的 Action Collapse Rate 最高；
- 具有 element-level semantic grounding 或 multi-resolution consistency 的模型 collapse 较低；
- Action Collapse Rate 能解释部分 OSWorld/AndroidWorld 长程失败中的错误点击。

成功标准：在 200-500 个 paired cases 上，至少两个强模型表现出明显 single-vs-pair gap，并且 ACR 与人工标注的 grounding failure type 有相关性。

## Risk

- Paired UI 构造可能引入不自然 artifact，导致测到的是编辑痕迹而非 grounding。
- Gold action flip 需要严格验证，否则 benchmark 本身会有 ambiguity。
- 如果模型已经非常 sensitive，ACR 可能不显著；此时可以转向 harder perturbations，例如 text/icon conflict 或 personalized UI state。
