---
name: auto-cite
description: >
  当 Supervisor 在写 LaTeX 论文、需要用知识库（Papers/）里读过的论文给草稿加引用时，
  逐条判断 claim 是否真被某篇论文支撑，给出带理由的 \cite{} 建议，确认后再插入。
  触发："给这篇 tex 加引用""用我读过的论文 cite 一下"
argument-hint: "[draft.tex 路径]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

## Purpose

给定一篇 LaTeX 草稿，用知识库里**已读过**的论文为它添加引用。核心原则：**evidence-driven，不按关键词盲插**——关键词重叠 ≠ 这篇论文真的支撑这句话。脚本只负责"缩小候选 + 机械校验"，**"该不该引、引哪篇"的判断由 Agent 读 summary 后做出，并经 Supervisor 确认后才写入**。

与 `latex-citation-enhancer` 的分工：后者把读过的论文导成准确的 `references.bib`（条目正确）；本 skill 决定**在哪句话引哪篇**（引用位置正确）。

## Steps

### Step 1：同步引用身份与索引

```bash
python3 skills/4-writing/latex-citation-enhancer/assign_cite_keys.py
python3 skills/4-writing/latex-citation-enhancer/build_paper_index.py
```

确保全库每篇都有稳定 `cite_key`，且 `paper_index.json` 是最新的（含 summary/key_results 供检索）。

### Step 2：解析草稿，定位"值得引用的 claim"

用 Read 读取 `.tex`。**由 Agent 判断**哪些句子需要引用支撑，典型信号：

- attributive：归因于已有工作（"prior work shows""X et al. propose""following [prior]"）。
- 实证断言：具体方法名、数据集名、benchmark 名、可被某篇论文证实的数字/结论。
- 背景陈述：领域内已被确立的事实（"GUI agents remain brittle on long-horizon tasks"）。

**不**需要引用的：作者自己的贡献陈述、纯过渡句、定义性陈述。

用 `tex_cite_ops.py existing <tex>` 列出**已有** `\cite{}` 的 key，对应句子默认跳过（除非 Supervisor 要求补充）。

### Step 3：候选生成（脚本，仅缩小范围）

对每条 claim，把该句（必要时加上下文短语）作为 query 取候选：

```bash
python3 skills/4-writing/auto-cite/retrieve_candidates.py "claim 文本……" --k 6 --json
```

返回 top-K 论文（cite_key / title / summary / matched_terms / score）。**这只是候选，不是结论。**

### Step 4：Agent 逐条判断（关键，evidence-driven）

对每个候选，Agent **读它的 Summary / Key Results**（候选里已带，必要时 Read 该 `Papers/*.md` 全文），判断：

> 这篇论文是否**真正支撑 / 是这句 claim 的正确归属来源**？

- 真支撑 → 保留，写一句 **grounding 理由**（"该文在 ScreenSpot-Pro 上报告 X，正好支撑'跨分辨率 grounding 退化'这句"）+ confidence（high/medium/low）。
- 仅关键词撞上但并不支撑 → **丢弃**（这是本 skill 与"关键词自动插引用"的根本区别）。
- 知识库无任何候选真正支撑 → 标记该 claim "**无支撑——需先 paper-digest 相关论文 / 用外部引用**"，绝不硬凑。

### Step 5：输出审阅表（不直接插入）

给 Supervisor 一张可勾选的表，每行一条 claim：

```
| # | claim（截断） | 建议 \cite | 论文标题 | 为什么支撑 | confidence |
|---|---|---|---|---|---|
| 1 | "...long-horizon GUI tasks remain brittle" | \cite{xu2025saasbench} | SaaSBench | resolved 仅 3.8%，直接量化长程脆弱性 | high |
| 2 | "...verifier 比 LLM judge 更可靠" | \cite{...} | OpenComputer | 94.1% vs 79.2% human alignment | high |
| 3 | "...privacy leakage 普遍" | — | — | 知识库无真正支撑，建议 paper-digest AgentCIBench | — |
```

**停在这里，等 Supervisor 确认 / 增删。** 这是 evidence-driven 的确认闸门。

### Step 6：确认后插入 + 校验

Supervisor 勾定后：

1. 用 Edit 把通过的 `\cite{key}`（多篇用 `\cite{a,b}`）插到对应 claim 的**句末标点前**；不动未确认项与已有 `\cite{}`。
2. 补全并校验 bib：

   ```bash
   # 把用到的 key 从缓存补进 references.bib（若尚未在内）
   python3 skills/4-writing/auto-cite/tex_cite_ops.py ensure-bib key1 key2 ... --bib <draft 用的 .bib>
   # 校验 .tex 里所有 \cite 的 key 都在 bib 里
   python3 skills/4-writing/auto-cite/tex_cite_ops.py verify <draft.tex> --bib <draft 用的 .bib>
   ```

   若 `ensure-bib` 报告某 key 不在缓存，先跑 `fetch_bibtex.py` 补该论文，或确认其 frontmatter 有 cite_key。

## Guard

- **禁止纯关键词插引用**：未经 Step 4 的 Agent 判断（读过 summary、确认真支撑），不得把任何候选写成 `\cite{}`。
- **确认闸门**：默认只产出审阅表；未经 Supervisor 明确确认，不写入 `.tex`。
- **不编造**：只引知识库中**已有 cite_key** 的论文；不臆造 key，不臆造 bib 条目。
- **诚实标注空白**：知识库无法支撑的 claim 必须**显式标出**，不得用勉强相关的论文充数。
- **不动已有引用**：除非 Supervisor 要求，不修改/删除草稿里已存在的 `\cite{}`。

## Verify

- [ ] 每条被插入的 `\cite{}` 都有 Step 4 的 grounding 理由（可追溯到论文 Summary/Key Results）
- [ ] 审阅表里"无支撑"的 claim 已如实列出，未被硬凑
- [ ] `tex_cite_ops.py verify` 通过：`.tex` 中所有 `\cite` key 均在 bib 内
- [ ] 未改动未经确认的 claim 与已有 `\cite{}`

## Notes

- 检索是 recall 工具，判断是 precision 闸门——宁可漏引（标"无支撑"）也不错引。
- 草稿引用密集时，可分节处理：一次只过一节的 claim，逐节出审阅表。
- 相关 skills：`latex-citation-enhancer`（生成/维护 references.bib）、`paper-digest`（补知识库缺的论文）。
