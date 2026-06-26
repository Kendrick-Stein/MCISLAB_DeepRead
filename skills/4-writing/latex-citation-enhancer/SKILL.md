---
name: latex-citation-enhancer
description: >
  当 Supervisor 需要把 Papers/ 中读过的论文转成 BibTeX 引用库时，从论文笔记
  frontmatter 无幻觉地生成 references.bib。触发："生成 bibtex""把我读过的论文导成引用库"
argument-hint: "[output_bib_path]"
allowed-tools: Read, Write, Bash, Glob
version: 3.0
---

## Purpose

把 `Papers/` 中已读论文的 frontmatter（title / authors / venue / year / url）**无幻觉地**转成 BibTeX 引用库，供你在 LaTeX 写作时手动 `\cite{}`。

> **设计边界（v3 重构）**：本 skill **只做 BibTeX 生成**，不再自动决定"在哪句话插哪篇引用"。
> 原 v2 的 keyword-score auto-insert 已移除——关键词重叠 ≠ 该论文支撑这句 claim，自动插引用会引入
> 不相关甚至错误的引用，违背 evidence-driven 原则。引用位置由作者判断，工具只保证**条目准确**。

## Steps

### Step 1：构建论文索引

```bash
python3 skills/4-writing/latex-citation-enhancer/build_paper_index.py
```

扫描 `Papers/` 所有笔记的 frontmatter，输出 `paper_index.json`（含 title / authors / venue / year / url / tags / rating）。

### Step 2：生成 BibTeX

```bash
python3 skills/4-writing/latex-citation-enhancer/generate_bibtex.py
```

从 `paper_index.json` 生成 `references.bib`：
- citation key = `{FirstAuthorLastName}{Year}`，冲突自动加后缀 `a/b/c`
- venue 含 arxiv → `@article` + `journal={arXiv preprint arXiv:XXXX.XXXXX}`；会议 → `@inproceedings`
- 所有字段直接取自 frontmatter，**不调用外部 API、不编造**

如需只导出某主题/某几篇，先按 tag 或 title 过滤 `paper_index.json` 再生成（或手动从输出里挑 key）。

### Step 3：作者手动引用

在 LaTeX 中由作者在**需要证据支撑的具体 claim** 处插入 `\cite{key}`。工具不代替这一判断。

## Guard

- **不编造 BibTeX**：所有条目必须来自 `Papers/` 笔记 frontmatter；作者/年份缺失则填 `{Unknown}` / 标注，不猜。
- **不自动插入 `\cite{}`**：不扫描 LaTeX 正文、不按关键词决定引用位置。
- **不修改 Papers/ 笔记**。
- 覆盖已有 `references.bib` 前先确认（或写到新路径）。

## Verify

- [ ] `paper_index.json` 生成，条目数 ≈ Papers/ 论文数
- [ ] `references.bib` 中每个 entry 字段来自 frontmatter，无占位幻觉数字
- [ ] citation key 无重复（冲突已加后缀）
- [ ] 标注了 author/year 缺失的条目供手动补全

## Notes

- `paper_index.json` 每次运行重建，始终反映最新 Papers/。
- 想要更高引用质量：先用 `paper-digest` 补全相关论文的 frontmatter（authors/venue/year），再重跑本 skill。
- 相关 skills：`paper-digest`（补论文）、`daily-papers`（拉新论文）。
