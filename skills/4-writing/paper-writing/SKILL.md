---
name: paper-writing
description: "统一写作技能：从 vault 素材起草章节（Draft 模式）到英文 LaTeX 论文分节写作（11-step Paper 模式，含 Related Work 溯源起草）。Use when: 用户说'写一下 introduction''起草 related work''起草报告章节''write introduction''draft method''paper writing'，需要 LaTeX 模板、优化学术写作质量或 novelty framing，或 autoresearch 判断某 direction 已积累足够素材需要成文。Do NOT use for: pre-submission review (paper-review)、experiment execution (experiment-design/track/result-analysis)、paper planning/story design (paper-planning)、打磨已有文稿 (writing-refine)。"
argument-hint: "[draft: <target> <section> <sources>] 或 [paper: <draft.tex 路径> <section>]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [core, research, writing, academic-writing, latex]
  source: EvoScientist/EvoSkills
  license: Apache-2.0
---

> Paper 模式 vendored from [EvoScientist/EvoSkills](https://github.com/EvoScientist/EvoSkills) (Apache-2.0), adapted for ReadPaperMachine（工具名/交叉引用/Guard/Verify 本地化）。License: references/licenses/EvoSkills-Apache-2.0.txt
> Draft 模式与 Related Work 流程来自本 vault 原 `draft-section` / `related-work` skill（2026-07-28 并入）。

# Paper Writing

## Purpose

MindFlow 的统一写作技能，覆盖"先 draft 再 paper"的完整成文链：

- **Draft 模式**：从 vault 素材（Papers/Experiments/Ideas/Topics 笔记）起草报告或论文的
  指定章节，中文成文、claim 全部带 `[[wikilink]]`。详细流程见 [references/draft-mode.md](references/draft-mode.md)。
- **Paper 模式**：按 11 步工作流撰写英文 LaTeX 论文各 section（Abstract、Introduction、
  Method、Experiments、Related Work、Conclusion、Supplementary），配套模板与写作原则。
  输入是 `paper-planning` 产出的 story/experiment plan artifact 与 `Experiments/` 实验结果；
  输出是可编译的 LaTeX 草稿，供 `paper-review` 做 self-review。
  其中 Related Work 一节用 vault 溯源流程起草（`\cite` 全部可溯到 references.bib），
  见 [references/related-work-vault.md](references/related-work-vault.md)。

## Mode Selection

| 情形 | 走哪个模式 |
|------|-----------|
| 起草 Reports/、Topics/ 报告章节；论文早期中文草稿；autoresearch 素材成文 | **Draft 模式**（references/draft-mode.md） |
| 英文 LaTeX 论文分节写作 / 全文推进 | **Paper 模式**（下方 11-step） |
| 只写 Related Work（给定 .tex 草稿） | **Related Work 流程**（references/related-work-vault.md，即 Paper 模式 Step 7） |

先 draft 再 paper：中文草稿在 Draft 模式打磨清楚 story 后，再进 Paper 模式英文化与 LaTeX 化。

## Artifact Sources

If you used upstream vault skills, pull these artifacts before writing:

| Source Skill | Artifact | Used In |
|-------------|----------|---------|
| `paper-planning` | Story summary (task → challenge → insight → contribution → advantage) | Steps 1-2 (Introduction writing plan) |
| `paper-planning` | Module Motivation Mapping table | Step 3 (Method subsections) |
| `paper-planning` | Experiment plan (comparisons + ablations + demos) | Step 5 (Experiments section) |
| `paper-planning` | Pipeline figure sketch | Steps 1, 6 (Method overview figure) |
| `paper-planning` | Claim-to-experiment mapping | Steps 2, 5 (Abstract, Introduction, Experiments) |
| `paper-planning` | Fallback narrative (if planned) | Steps 7-8 (Introduction / Conclusion pivot) |
| `experiment-track` / `result-analysis` | Experiment results, ablation tables, and failure analysis recorded in `Experiments/` | Step 5 (write experiments), Step 9 (limitations) |
| `experiment-design` | Implementation tricks and design rationale captured during experiment planning | Step 3 (Method section) |

## Steps

The 11-step writing process. Follow these steps in order — each step builds on the previous one.

1. **Draw a pipeline figure sketch** — Sketch the method's pipeline figure to clarify the overall approach. The figure highlights novelty, not just explanation.
2. **Design the story and plan experiments** — Outline the paper's story (core contribution, module motivations). List comparison experiments and ablation studies. Draft an Introduction writing plan.
3. **Write Method** — Organize the Method writing plan, then draft Method. Run experiments in parallel.
4. **Revise Introduction and Method** — Iterate on both sections while experiments continue.
5. **Write Experiments** — Once experiments are mostly done, organize the Experiments writing plan, then draft.
6. **Polish figures** — Finalize the pipeline figure. Create the teaser figure.
7. **Write Related Work** — List related papers, group into topics, write paragraphs. Draft this section with the vault-grounded procedure in [references/related-work-vault.md](references/related-work-vault.md) so citations trace to `references.bib`.
8. **Review the paper** — Self-review Introduction, Method, and Experiments. Use the `paper-review` skill.
9. **Write Abstract** — Organize the Abstract writing plan, then draft.
10. **Choose the title** — List important keywords, then compose an informative title.
11. **Iterate** — Repeatedly review and revise the entire paper.

## Counterintuitive Writing Rules

Apply these rules when aiming for higher acceptance probability:

1. **Underclaim in prose, overdeliver in evidence**: Reduce adjective intensity in Abstract/Introduction; let tables and figures carry the strength.
2. **State one meaningful limitation early**: A controlled limitation statement increases credibility and lowers reviewer suspicion.
3. **Lead with mechanism, not only metric**: Explain why the method works before listing numbers; reviewers trust causal logic more than isolated gains.
4. **Prefer one decisive figure over many average figures**: Build one "cannot-ignore" figure that validates the central claim under hard conditions.
5. **Remove weak but flashy claims**: Any claim without direct evidence should be deleted, even if it sounds impressive.
6. **Declare scope boundaries explicitly**: One sentence in Introduction and Conclusion stating what your method targets reduces reviewer fear of hidden assumptions.
7. **Show one failure case**: Include one representative failure with diagnosis — it signals competence, not weakness.

See [references/counterintuitive-writing.md](references/counterintuitive-writing.md) for all 7 tactics with before/after examples.

## Section Quick Reference

### Abstract

Answer these questions before drafting:
1. What technical problem do we solve, and why is there no well-established solution?
2. What is our technical contribution?
3. Why does our method fundamentally work?
4. What is our technical advantage / new insight?

Three template versions: challenge-first, insight-bridge, multi-contribution.
See [references/abstract-templates.md](references/abstract-templates.md)

### Introduction

**Thinking process** (reverse then forward):
- Reverse: (1) What is the technical problem? (2) What are our contributions? (3) Benefits and new insights? (4) How to lead into the challenge?
- Forward: (1) Task → (2) Previous methods → challenge → (3) Our contributions → (4) Technical advantages and insights

Four ways to introduce the task, three ways to present challenges, four ways to describe the pipeline.
See [references/introduction-templates.md](references/introduction-templates.md)

**Anti-pattern**: Never write "here is a naive solution, then our improvement" — this makes the work appear incremental.

### Method

Every pipeline module needs three elements:
1. **Module design** — Data structure, network design, forward process (given X input, step 1..., step 2..., output Y)
2. **Motivation** — Why this module exists (problem-driven: "A remaining challenge is...")
3. **Technical advantages** — Why this module works well

Start with an Overview paragraph (setting + core contribution + section roadmap), then one subsection per module.
See [references/method-templates.md](references/method-templates.md)

### Experiments

Three key questions to answer:
1. How to prove our method is better → comparison experiments
2. How to prove our modules are effective → ablation studies
3. How to showcase the method's upper limit → demos on challenging data

Ablation studies need: one big table (core contributions) + several small tables (design choices, hyperparameters).
See [references/experiments-guide.md](references/experiments-guide.md)

### Related Work

Three-step process:
1. List papers closely related to our method (most important — missing key references can cause rejection)
2. Determine topics based on research direction and algorithm techniques
3. Organize writing plan based on listed papers

> 该节按 [references/related-work-vault.md](references/related-work-vault.md) 的 vault 溯源流程起草——它能确保每个 `\cite` 都可溯源到 `references.bib` 中的真实 cite_key。本节及 [references/related-work-guide.md](references/related-work-guide.md) 作为写作质量的参考标准（三步流程、常见反模式），而非替代该溯源流程的执行。

### Conclusion

- Must include **Limitation** section (reviewers frequently cite "no limitation" as a weakness)
- Limitation = task goal / setting limitations (like future work), NOT technical defects
- Rule: "If our method does not fall below current SOTA metrics, it is not a technical defect"

### Supplementary Material

For page-limited venues, decide what goes in main paper vs. supplementary:
- Core evidence for claims must stay in the main paper
- Implementation details, extra ablations, full visual galleries go in supplementary
- Reference supplementary at the point of need, not as a blanket statement

See [references/supplementary-guide.md](references/supplementary-guide.md)

## Core Writing Principles

1. **One message per paragraph** — Each paragraph conveys exactly one point
2. **Topic sentence first** — The first sentence tells readers what this paragraph is about
3. **Plan before writing** — Outline the writing plan, refine each part, then write English sentences
4. **Flow between sentences** — Ensure logical continuity between consecutive sentences
5. **Terminology consistency** — Use the same term throughout; do not alternate names
6. **Reverse-outlining** — After writing, extract the outline from paragraphs; check if the flow is smooth
7. **Iterate relentlessly** — Polish repeatedly, asking whether readers can follow

See [references/writing-principles.md](references/writing-principles.md)

## Key Insight

Visual polish directly influences review outcomes. See the `paper-planning` skill's [figure-design.md](../paper-planning/references/figure-design.md) for the full visual quality guide.

## Paper Title Guidelines

- The title attracts specific reviewers — choose keywords carefully
- Before writing the title, list important keywords, then compose
- Title must be **informative**: include the technique, task, or problem solved
- Avoid generic titles; specific phrases are more memorable

## LaTeX Assets

- [assets/paper-skeleton.tex](assets/paper-skeleton.tex) — Annotated LaTeX skeleton with section structure
- [assets/table-style.tex](assets/table-style.tex) — Booktabs table macros with color highlighting

## Guard

- 所有引用一律走 vault 的 citation 链——Paper 模式的 cite_key 必须来自 `references.bib`，
  Draft 模式的 `[[wikilink]]` 必须指向 vault 中实际存在的文件；禁止编造文献或引用信息
- Related Work 一节按 [related-work-vault.md](references/related-work-vault.md) 的溯源流程起草；[related-work-guide.md](references/related-work-guide.md) 仅作为写作质量参考
- **Draft 模式**：只操作指定章节，不修改目标文件其他内容；目标章节已有实质性内容（>100 字）时不覆盖，停止并建议 writing-refine（完整 Guard 见 references/draft-mode.md）
- 不修改用户论文中已有的作者贡献陈述（author contribution statement）
- 不为了"读起来更强"而在 Abstract/Introduction 中加入没有实验支撑的 claim；underclaim in prose, overdeliver in evidence
- Limitation 章节必须诚实反映 scope 边界，不得用它掩盖真实的技术缺陷或省略已知失败案例

## Verify

Paper 模式：

- [ ] 全文无残留 `\todo{}` 标记
- [ ] 每条 claim（尤其 Abstract/Introduction）都锚定到具体的图/表/实验证据
- [ ] LaTeX 可编译（无语法错误、无未闭合环境、引用/标签无悬空）
- [ ] Related Work 中引用的 cite_key 均可在 `references.bib` 中找到
- [ ] Method 每个模块都包含 design / motivation / advantage 三要素

Draft 模式：见 [references/draft-mode.md](references/draft-mode.md) 的专属 Verify
（章节写入 + wikilink 溯源 + 无占位符 + 未动其他章节 + 日志）。

## Handoff to Review

Before invoking `paper-review`, verify this checklist:

- [ ] All sections (Abstract, Introduction, Method, Experiments, Related Work, Conclusion) drafted
- [ ] Every claim in Abstract/Introduction anchored to a table or figure
- [ ] Limitation section present in Conclusion
- [ ] Pipeline figure and teaser figure finalized
- [ ] All `\todo{}` markers resolved or removed

---

## Section Navigation

| Section | Reference File | When to Load |
|---------|---------------|--------------|
| Draft 模式全流程 | [draft-mode.md](references/draft-mode.md) | 从 vault 素材起草报告/论文章节时 |
| Related Work 溯源流程 | [related-work-vault.md](references/related-work-vault.md) | Step 7: 起草 Related Work |
| Abstract | [abstract-templates.md](references/abstract-templates.md) | Step 9: Writing abstract |
| Introduction | [introduction-templates.md](references/introduction-templates.md) | Step 2: Story design |
| Method | [method-templates.md](references/method-templates.md) | Step 3: Writing method |
| Experiments | [experiments-guide.md](references/experiments-guide.md) | Step 5: Writing experiments |
| Related Work | [related-work-guide.md](references/related-work-guide.md) | Step 7: Writing related work |
| Writing Principles | [writing-principles.md](references/writing-principles.md) | Any time during writing |
| Supplementary | [supplementary-guide.md](references/supplementary-guide.md) | Deciding main vs. supplementary content |
| Counterintuitive strategy | [counterintuitive-writing.md](references/counterintuitive-writing.md) | Improving reviewer trust and novelty perception |
| Writing Practice | [writing-practice.md](references/writing-practice.md) | Building writing ability through deliberate practice |
