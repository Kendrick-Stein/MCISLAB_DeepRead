---
name: academic-slides
description: "Use this skill for creating or refining an academic slide deck and the talk built around it: structuring a conference talk, thesis defense, lab meeting, or paper-to-slides deck; deciding the narrative arc and slide breakdown; improving slide design and visual hierarchy; planning rehearsal, timing, Q&A, and backup slides; or generating the .pptx. Reach for it when the user is shaping the presentation itself. Do not use for writing the paper, producing standalone speaker notes/scripts/transcripts, making posters, creating isolated figures/charts outside a slide deck, or building non-academic presentations."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [core, writing, presentation, academic-writing]
  source: EvoScientist/EvoSkills
  license: Apache-2.0
---

> Vendored from [EvoScientist/EvoSkills](https://github.com/EvoScientist/EvoSkills) (Apache-2.0), adapted for ReadPaperMachine（工具名/交叉引用/Guard/Verify 本地化）。License: references/licenses/EvoSkills-Apache-2.0.txt

# Academic Slides

## Purpose

系统性地创建学术演讲的 slide deck 及其配套的讲述内容：叙事结构、slide 拆分、视觉设计、排练与 Q&A 准备，直至生成 `.pptx` 文件。输入是用户提供的论文或 vault 笔记（story summary、pipeline figure、实验结果等）；输出是 outline（经用户确认）以及最终的 `.pptx` 幻灯片文件。

## When to Use This Skill

- User wants to create presentation slides for a research talk
- User asks about structuring an academic presentation
- User needs to prepare for a conference talk, thesis defense, or lab meeting
- User wants to design a slide deck from a paper or research project
- User mentions "slides", "presentation", "talk", "defense", "poster talk"

---

## Before You Start: Three Questions

Before designing any slides, answer these questions clearly:

1. **What works are you presenting?**
   They must share a coherent research direction. If presenting multiple works, they should form a narrative arc — not a disconnected list.

2. **What problems do these works solve in that direction?**
   Each work should map to a specific problem. If you cannot articulate the problem in one sentence, you are not ready to present.

3. **How do you use related work to naturally introduce these problems?**
   Related work is not citation duty. It builds the motivation for YOUR problem. Each related work you mention should advance the audience toward understanding why your approach is needed.

---

## Steps

```
Step 1: Define scope and audience
Step 2: Draft narrative arc (outline)
Step 3: Design slide structure (section breakdown)
Step 4: Create individual slides (one idea per slide)
Step 5: Add visual elements (figures, diagrams, animations)
Step 6: Rehearse and time
Step 7: Prepare backup / Q&A slides
```

### Step 1: Define Scope and Audience

| Audience | Adjust |
|----------|--------|
| Domain experts | Skip basics, go deep on method and results |
| Broad CS / engineering | Explain task context, moderate technical depth |
| Interdisciplinary | Start from the application, minimize jargon |
| Industry | Lead with impact and demo, light on theory |

**Rule of thumb**: Duration in minutes = approximate slide count. A 20-minute talk needs about 20 slides.

### Step 2: Draft Narrative Arc

Use the outline template at [assets/talk-outline-template.md](assets/talk-outline-template.md) to plan your talk before making any slides. The outline forces you to articulate your key takeaway and narrative arc.

### Step 3: Design Slide Structure

Break your outline into sections with claim-style headers. See [talk-structure.md](references/talk-structure.md) for two complete talk structures and section-by-section guidance.

### Step 4: Create Individual Slides

One idea per slide. Follow the 10 design rules in [slide-design.md](references/slide-design.md) for visual hierarchy and layout.

### Step 5: Build the .pptx File

Use [slide-creation.md](references/slide-creation.md) for practical `.pptx` creation — color palettes, layout code, charts, tables, figures, and QA workflow.

### Step 6: Rehearse and Time

See [references/delivery-and-qa.md](references/delivery-and-qa.md) for the rehearsal protocol, delivery principles, and Q&A preparation.

### Step 7: Prepare Backup Slides

Backup slides go after your "Thank You" slide. They are not part of the talk — they are your safety net for Q&A:

- Full quantitative comparison table
- Failure cases (shows honesty and preparation)
- Additional ablations or analysis
- Slides addressing anticipated tough questions

---

## Artifact Sources from Other Skills

If you used these vault skills earlier in the pipeline, pull these artifacts directly:

| Source Skill | Artifact | Use In Slides |
|-------------|----------|---------------|
| `paper-planning` | Story summary (task → challenge → insight) | Motivation slides |
| `paper-planning` | Pipeline figure sketch | Method overview slide |
| `paper-planning` | Experiment plan | Results structure |
| `paper-writing` | Finalized figures and tables | Method + results slides |
| `paper-review` | Anticipated reviewer concerns | Backup Q&A slides |

See [slide-creation.md](references/slide-creation.md) for detailed layout patterns using each artifact.

---

## Counterintuitive Presentation Rules

> For the 10 design rules (one idea per slide, claim-style titles, max 6 elements, etc.), see [slide-design.md](references/slide-design.md). The rules below are higher-level mindset shifts.

### 1. Your slides are not your paper

A talk is an advertisement, not a lecture. Your goal is to make the audience interested enough to read the paper. Cut 80% of your paper's content. If someone can reconstruct your paper from your slides alone, your slides have too much.

### 2. Reading and listening compete

Text-heavy slides force the audience to choose between reading your slides and listening to you. They will read — and stop hearing you. When you put text on a slide, you are choosing to be ignored.

### 3. Enthusiasm > polish

A passionate speaker with rough slides beats a bored speaker with beautiful slides. The audience remembers your energy and clarity, not your color scheme. If you only have time to improve one thing, rehearse more — don't redesign slides.

### 4. Related work is not citation duty

Use related work to BUILD your problem motivation, not to show you have read papers. Each related work slide should advance the narrative: "This approach solved X, but Y remains open — which is exactly what we address."

---

## Guard

- 幻灯片内容（数据、结果、图表）只能来自用户提供的论文或 vault 笔记，不得虚构或外推未经验证的数字
- 生成 `.pptx` 文件之前，必须先给出 slide outline / 叙事结构供用户确认，未经确认不得直接产出成品文件
- 每页幻灯片只承载一个 idea；文字密度不得高到让观众"选择阅读而非听讲"
- 使用 Bash 执行生成脚本（`node`/`pptxgenjs`/QA 相关命令）仅限于本地 slide 生成与检查用途，不得用于与幻灯片无关的系统操作
- Backup slides 放在 "Thank You" 之后，不计入正式讲述时长

## Verify

- [ ] 每页幻灯片有且仅有一个 message（single message per slide）
- [ ] narrative arc 三问已在 outline 阶段回答（presenting what / what problem / how related work motivates it）
- [ ] 幻灯片页数与讲述时长匹配（约 1 分钟 1 页的经验法则）
- [ ] 生成 `.pptx` 后已用 QA 流程（如 markitdown / 图像检查）核实视觉效果
- [ ] Backup slides 已准备（失败案例、完整对比表、预期追问的补充材料）

## Reference Navigation

| Topic | Reference File | When to Use |
|-------|---------------|-------------|
| Talk structures | [talk-structure.md](references/talk-structure.md) | Organizing the narrative arc |
| Slide design | [slide-design.md](references/slide-design.md) | Visual design and layout rules |
| Slide creation | [slide-creation.md](references/slide-creation.md) | Building .pptx files with code |
| Delivery and Q&A | [delivery-and-qa.md](references/delivery-and-qa.md) | Rehearsal, timing, Q&A preparation |
| Talk outline template | [talk-outline-template.md](assets/talk-outline-template.md) | Starting a new presentation |
