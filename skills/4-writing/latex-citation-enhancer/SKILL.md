---
name: latex-citation-enhancer
description: >
  当 Supervisor 需要把 Papers/ 中读过的论文转成 BibTeX 引用库时，先固化每篇的稳定
  cite_key、抓取权威 BibTeX，再无幻觉地生成 references.bib。触发："生成 bibtex""把我读过的论文导成引用库"
argument-hint: "[output_bib_path]"
allowed-tools: Read, Write, Bash, Glob
version: 4.0
---

## Purpose

把 `Papers/` 中已读论文的 frontmatter（title / authors / venue / year / url）**无幻觉地**转成 BibTeX 引用库，供你在 LaTeX 写作时手动 `\cite{}`。

> **设计边界（v3 重构）**：本 skill **只做 BibTeX 生成**，不再自动决定"在哪句话插哪篇引用"。
> 原 v2 的 keyword-score auto-insert 已移除——关键词重叠 ≠ 该论文支撑这句 claim，自动插引用会引入
> 不相关甚至错误的引用，违背 evidence-driven 原则。引用位置由作者判断，工具只保证**条目准确**。

## Steps

### Step 1：固化引用身份（cite_key + 权威 BibTeX）

```bash
# 为缺 key 的论文分配稳定 cite_key（幂等，已有 key 永不变）
python3 skills/4-writing/latex-citation-enhancer/assign_cite_keys.py
# 抓取 arXiv/Crossref 权威 BibTeX 进缓存（抓不到则重建）；可加 --offline 跳过联网
python3 skills/4-writing/latex-citation-enhancer/fetch_bibtex.py
```

- `cite_key` 写入每篇 frontmatter，格式 `{lastname}{year}{firstTitleWord}`（如 `wen2026openrath`），**一旦写入永久冻结**——保证已发草稿里的 `\cite{}` 永远不失效。
- 权威 BibTeX 缓存在 `references/bibtex-cache.bib`（按 cite_key 索引，带 `source=arxiv|crossref|reconstructed` provenance）。已缓存的不重复抓网；`--upgrade` 可把旧的 reconstructed 升级为权威源。

### Step 2：构建论文索引

```bash
python3 skills/4-writing/latex-citation-enhancer/build_paper_index.py
```

扫描 `Papers/` frontmatter（pyyaml 解析，正确处理多行 authors），输出 `paper_index.json`（含 cite_key / title / authors / venue / year / arxiv_id / doi / url / tags / rating / summary / key_results）。

### Step 3：生成 references.bib

```bash
python3 skills/4-writing/latex-citation-enhancer/generate_bibtex.py
```

从 `paper_index.json` + 缓存组装 `references.bib`：
- citation key 一律用 frontmatter 里 **pinned 的 `cite_key`**（不再现场重算）。
- 每条优先取缓存里的**权威**条目（arXiv/Crossref）；缺失则从 frontmatter **无幻觉重建**。
- 覆盖前自动备份到 `references.bib.bak`。

如需只导出某主题/某几篇，先按 tag 或 title 过滤 `paper_index.json` 再生成（或手动从输出里挑 key）。

### Step 4：作者手动引用

在 LaTeX 中由作者在**需要证据支撑的具体 claim** 处插入 `\cite{key}`。本 skill 只保证条目准确，不代替"该不该引、引哪篇"的判断——后者由 `auto-cite` skill（Agent 逐条判断 + 待确认）或作者本人完成。

## Guard

- **不编造 BibTeX**：权威条目来自 arXiv/Crossref，重建条目仅取 `Papers/` frontmatter；字段缺失就留空，不猜不补。
- **不自动插入 `\cite{}`**：本 skill 不扫描 LaTeX 正文、不决定引用位置（那是 `auto-cite` 的职责，且需逐条判断 + 确认）。
- **只新增不改写身份字段**：`assign_cite_keys.py` 只为缺失的论文写 `arxiv_id`/`cite_key`，**绝不修改已有 cite_key 或论文正文**。
- 生成 `references.bib` 前自动备份到 `.bib.bak`；不手改 `bibtex-cache.bib`（下次运行会被覆盖）。

## Verify

- [ ] 全库每篇 `Papers/*.md` 的 `cite_key` 非空且唯一（`assign_cite_keys.py` 报告 0 missing / 0 duplicate）
- [ ] `paper_index.json` 生成，条目数 ≈ Papers/ 论文数
- [ ] `references.bib` 每个 entry 的 key = frontmatter 的 cite_key；权威/重建数量已打印
- [ ] 用 `bibtex`/`bibtool` 解析 `references.bib` 无语法错误

## Notes

- `cite_key` 是稳定引用契约——一旦写入 frontmatter 就不变；想改某篇的 key 需手动编辑该字段（工具不会覆盖）。
- 想要更高引用质量：先用 `paper-digest` 补全 frontmatter（authors/venue/year/arxiv_id），再 `fetch_bibtex.py --upgrade` 把重建条目升级为权威源。
- 相关 skills：`paper-digest`（补论文 + 固化身份）、`daily-papers`（拉新论文）、`auto-cite`（给草稿挂引用）。
