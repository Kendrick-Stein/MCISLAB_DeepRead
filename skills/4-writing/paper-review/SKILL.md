---
name: paper-review
description: "Guides self-review of YOUR OWN academic paper before submission with adversarial stress-testing. Core method: 5-aspect checklist (contribution sufficiency, writing clarity, results quality, testing completeness, method design), counterintuitive protocol (reject-first simulation, delete unsupported claims, score trust, promote limitations, attack novelty), reverse-outlining, and figure/table quality checks. Use when: user wants to self-review or self-check their own paper draft before submission, stress-test their claims, prepare for reviewer criticism, or mentions 'self-review', 'check my draft', 'is my paper ready'. Do NOT use for writing a peer review of someone else's paper, and do NOT use after receiving actual reviews (use paper-rebuttal instead)."
allowed-tools: Read, Write, Edit, Glob, Grep
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [core, writing, academic-writing, peer-review]
  source: EvoScientist/EvoSkills
  license: Apache-2.0
---

> Vendored from [EvoScientist/EvoSkills](https://github.com/EvoScientist/EvoSkills) (Apache-2.0), adapted for ReadPaperMachine（工具名/交叉引用/Guard/Verify 本地化）。License: references/licenses/EvoSkills-Apache-2.0.txt

# Paper Review

## Purpose

系统性地自我评审(self-review)一篇尚未投稿的学术论文草稿，以对抗性视角提前发现审稿人会指出的问题。输入是用户自己的完整论文草稿（已完成 `paper-writing` 的 handoff checklist）；核心方法是 5-aspect checklist（contribution sufficiency / writing clarity / results quality / testing completeness / method design）加上 reject-first simulation 等 counterintuitive protocol；输出是逐条问题及其 fix 或 defense，以及供 `paper-rebuttal` 复用的 reject-first 摘要与 claim-evidence 审计表。

## When to Use This Skill

- User wants to review or check a paper draft before submission
- User asks for feedback on paper quality or completeness
- User wants to prepare for potential reviewer criticism
- User mentions "review paper", "check my draft", "self-review"

> If the user has already received reviewer comments and needs to write a rebuttal, use the `paper-rebuttal` skill instead.

## Prerequisites

Before starting review, confirm the `paper-writing` handoff checklist is satisfied: all sections drafted, claims anchored to evidence, limitation section present, figures finalized, and no unresolved `\todo{}` markers. If any item is incomplete, finish writing before reviewing.

---

## Steps

Work through the review in this order: perfectionist self-critique → counterintuitive protocol → 5-aspect checklist → claim-evidence audit → reverse-outlining → figure/table checks → conclusion/limitation check → pre-submission checks.

## The Perfectionist Approach

> Strive for perfection: review your own paper, consider every question a reviewer might ask, and address them one by one.

The best defense against negative reviews is a thorough self-review:
1. **Adversarial review**: Read your own paper as a critical reviewer would
2. **Seek advisor feedback**: Ask your advisor to review — the more feedback, the better
3. **Address everything**: For every potential weakness you find, either fix it or prepare a defense

## Counterintuitive Review Protocol

Run this protocol before final polishing:

1. **Reject-first simulation**: Force yourself to write a one-paragraph reject summary before writing any positive comments.
2. **Delete one unsupported strong claim**: If a strong claim lacks direct evidence, remove it instead of defending it.
3. **Score trust, not only score gains**: Papers with slightly lower gains but higher fairness and reproducibility often receive better review outcomes.
4. **Promote one explicit limitation**: Move one meaningful limitation from hidden notes into the paper; transparency can increase confidence.
5. **Attack your novelty claim**: Ask "Could a strong PhD derive this in one afternoon?" If yes, narrow and sharpen the novelty statement.

See [references/counterintuitive-review.md](references/counterintuitive-review.md)

---

## 5-Aspect Self-Review Checklist

### Aspect 1: Contribution Sufficiency

> The paper does not provide readers with new knowledge.

Ask these questions to evaluate whether the contribution is sufficient:

- [ ] **Are the failure cases common?** If the failure cases are frequent and obvious, reviewers may question whether the method is ready for publication.
- [ ] **Is the proposed technique well-explored?** If the technique is already widely studied, what new insight or improvement do we bring?
- [ ] **Is the improvement foreseeable / well-known?** If the improvement was predictable from combining known ideas, the novelty may be questioned.
- [ ] **Is the technique too straightforward?** A straightforward application of existing techniques may lack sufficient contribution.

**Red flag**: If "yes" to any of these, strengthen the contribution narrative or add more technical depth.

### Aspect 2: Writing Clarity

> Missing technical details, not reproducible; a method module lacks motivation.

- [ ] **Missing technical details?** Would a reader be able to reproduce the method from the paper alone?
- [ ] **Missing module motivation?** Does every module in the Method section explain *why* it exists, not just *what* it does?
- [ ] **Paragraph structure**: Does each paragraph have a clear topic? Does the first sentence state the point?
- [ ] **Flow**: Is the logical flow between paragraphs and sections smooth?
- [ ] **Terminology**: Are terms used consistently throughout?

**Red flag**: If reproducibility is in doubt, add implementation details or supplementary material.

### Aspect 3: Experimental Results Quality

> Only slightly better than previous methods; or better than previous methods but still not good enough.

- [ ] **Marginal improvement?** If the improvement over SOTA is very small, is it statistically significant?
- [ ] **Absolute quality insufficient?** Even if better than baselines, is the output quality good enough for the application?
- [ ] **Visual quality**: Do qualitative results look convincing? Are improvements visible?

**Red flag**: If improvements are marginal, emphasize other advantages (speed, generalizability, simplicity) or add more challenging test cases.

### Aspect 4: Experimental Testing Completeness

> Missing ablation studies; missing important baselines; missing important evaluation metrics; data too simple.

- [ ] **Missing ablation studies?** Is every core contribution ablated?
- [ ] **Missing important baselines?** Are recent SOTA methods included?
- [ ] **Missing evaluation metrics?** Are all standard metrics for this task reported?
- [ ] **Datasets too simple?** Do the benchmarks truly test the method's capabilities?
- [ ] **No failure case analysis?** Honest failure analysis increases credibility.

**Red flag**: Missing ablations or baselines is one of the most common reasons for rejection.

### Aspect 5: Method Design Issues

> Experimental setting is impractical; method has technical flaws; method is not robust; new method's costs outweigh its benefits.

- [ ] **Impractical experimental setting?** Are assumptions realistic for the intended use case?
- [ ] **Technical flaws?** Does the method have theoretical or conceptual weaknesses?
- [ ] **Not robust?** Does the method require per-scene hyperparameter tuning?
- [ ] **Benefit < Limitation?** Does the new module introduce limitations that outweigh its benefits?

**Red flag**: If the method requires significant tuning per scenario, add robustness experiments or acknowledge and address the limitation.

---

## Critical Reminder: Claims Must Have Support

> Every claim in the paper (especially in the Abstract and Introduction) must be correct and supported by experiments. Some reviewers will reject a paper directly for unsupported claims.

Go through every claim in the Abstract and Introduction. For each claim:
- [ ] Is it factually correct?
- [ ] Is there an experiment or analysis that supports it?
- [ ] Is the supporting experiment clearly referenced?

An unsupported claim — especially in the Abstract or Introduction — can be grounds for rejection.

---

## Reverse-Outlining Technique

> Extract the writing plan from finished paragraphs and check whether the flow is smooth.

After writing a section (or the entire paper):

1. **Read each paragraph** one at a time
2. **Write down the main message** of each paragraph in one sentence
3. **Read the sequence of messages** — does it flow logically?
4. **Identify breaks**: Where does the flow feel abrupt or illogical?
5. **Fix**: Reorganize paragraphs, add transitions, or split/merge paragraphs

Apply this to:
- Introduction (check narrative flow)
- Method (check if modules are presented in logical order)
- Experiments (check if results are presented in a meaningful sequence)

---

## Figure and Table Quality Checklist

### Figures
- [ ] Pipeline figure highlights novelty (not just explanation)
- [ ] Pipeline figure looks distinct from prior work
- [ ] Teaser figure is compelling and self-contained
- [ ] All figures have clear captions
- [ ] Resolution is high enough for print
- [ ] Color-blind friendly (avoid red-green only distinctions)
- [ ] Figures are referenced in the text

### Tables
- [ ] Captions are above the table
- [ ] No vertical lines
- [ ] Using booktabs (`\toprule`, `\midrule`, `\bottomrule`)
- [ ] Best results highlighted (bold/color)
- [ ] Metric direction indicated (↑/↓)
- [ ] Captions describe setup/notation, not results
- [ ] All tables are referenced in the text

---

## Conclusion and Limitation Check

- [ ] Conclusion summarizes contributions and key results
- [ ] **Limitation section is present** (reviewers frequently flag its absence)
- [ ] Limitations are about task/setting scope (like future work), not technical defects
  > Rule: "If our method does not fall below SOTA metrics, it is not a technical defect"
- [ ] Limitations are honest but not self-defeating

---

## Pre-Submission Final Checks

- [ ] All references are complete (no "?" or missing entries)
- [ ] Author information matches venue requirements
- [ ] Page count is within limits
- [ ] Supplementary material is properly referenced
- [ ] No TODO markers remain in the paper
- [ ] Acknowledgments section is appropriate
- [ ] No accidental double-blind violations (for anonymous review)
- [ ] All cited works have complete bibliographic entries (authors, title, venue, year)
- [ ] No self-citations that break anonymity (for double-blind venues)
- [ ] Key related works cited — missing a prominent baseline paper can trigger rejection

---

## Guard

- 只评审用户自己的论文草稿（self-review），不得将本 skill 用于对他人论文的同行评审
- 对每个发现的问题，必须给出具体的 fix 方案或站得住脚的 defense，不能只罗列问题而不给出处置
- 执行 reject-first simulation 时必须先写出完整的拒稿摘要，再写任何正面评价——顺序不可颠倒
- 不得在缺乏直接证据支持的情况下保留 Abstract/Introduction 中的强 claim；无证据支持的强 claim 应删除或弱化，而非默认保留
- 不擅自大幅重写用户论文正文；仅标注问题、给出建议，或经用户确认后再编辑

## Verify

- [ ] 5-aspect checklist（contribution sufficiency / writing clarity / results quality / testing completeness / method design）逐项过审，无跳项
- [ ] reject-first simulation 已写成一段完整的拒稿摘要
- [ ] Abstract/Introduction 中每条 claim 都标注了对应证据（图/表/实验）或已被处置（弱化/删除）
- [ ] Limitation 章节存在，且内容为 scope 限制而非隐藏的技术缺陷
- [ ] reverse-outline 结果已给出，确认段落逻辑流顺畅

## Handoff to Rebuttal

When reviews come back, use the `paper-rebuttal` skill for:
- Score diagnosis and review color-coding
- Champion strategy (arming your positive reviewer for discussion)
- 18 tactical rules for structure, content, and tone
- Counterintuitive rebuttal principles

Your self-review artifacts (reject-first simulation, claim-evidence audit, prebuttal drafts from the counterintuitive protocol) feed directly into the rebuttal process.

---

See [references/review-checklist.md](references/review-checklist.md) for an expanded version of the 5-aspect checklist with more detailed sub-questions.

For adversarial stress testing and reject-risk thresholds, see [references/counterintuitive-review.md](references/counterintuitive-review.md).
