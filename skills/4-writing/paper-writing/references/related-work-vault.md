# Related Work — vault 溯源起草流程

（原独立 skill `related-work`，2026-07-28 并入 paper-writing，对应其 11-step 的 Step 7。
触发：Supervisor 给出自己论文的 LaTeX 草稿并要求"写 related work""起草相关工作"。）

基于 Papers/ 已读论文与 Topics/ survey 起草英文 LaTeX Related Work 章节，
所有 `\cite{}` 来自 references.bib，evidence-driven 不编造。

与 citation 链其他环节的分工：
- `latex-citation-enhancer`：保证 references.bib 条目准确（引用身份）。
- `auto-cite`：给**已写好**的草稿逐句补引用（引用位置）。
- 本流程：从零**起草** Related Work 章节本身（叙事 + 选文 + 成文），输出英文 LaTeX。
- Draft 模式（references/draft-mode.md）：中文 vault 笔记章节，与本流程输出物不同。

参数：`<draft.tex 路径> [topic] [段落数预算，默认 4]`

## Steps

### Step 1：准备引用基础设施

```bash
python3 skills/4-writing/latex-citation-enhancer/assign_cite_keys.py
python3 skills/4-writing/latex-citation-enhancer/build_paper_index.py
python3 skills/4-writing/latex-citation-enhancer/fetch_bibtex.py --offline
```

确保 paper_index.json 最新、每篇有稳定 cite_key。若 Supervisor 的项目有独立 .bib，
询问路径；否则按 latex-citation-enhancer 流程生成/更新 `references.bib`。

### Step 2：理解草稿定位

Read draft.tex，提取：论文的核心贡献 claim、方法关键词、目标 venue 风格线索、
已有的 Related Work 章节或占位符。据此确定本文需要"对比并区隔"的 2-5 条相关工作线。

### Step 3：借 survey 取叙事结构

Grep `Topics/*-Survey.md` 找与 topic 匹配的 survey（frontmatter keywords），
Read 其分类框架与 Key Takeaways。Related Work 的段落划分优先沿用 survey 的成熟分类，
每段结尾回扣"本文与该线工作的区别"。

### Step 4：evidence-driven 选文

对每个段落主题，从 `paper_index.json`（title/tags/summary/key_results）取 5-10 篇候选，
逐篇读 summary 确认**真实支撑**该段叙事后纳入（原则同 auto-cite：关键词重叠 ≠ 支撑）。
每段收敛到 3-6 篇代表作。领域公认必引但库内没有的论文，记入 missing 清单（Step 6），
**不得凭记忆编造引用**。

### Step 5：成文

写出英文 LaTeX Related Work（默认 4 段，按参数调整）：

- 每段：主题句 → 代表工作演进（`\cite{key}` 全部来自 Step 1 的 bib/index）→
  与本文的区隔句。
- 学术英语，时态与 venue 惯例一致（一般现在时为主）。
- 每段后附注释块供 review，格式：
  `% EVIDENCE: <cite_key> ← Papers/<笔记名>（一句话支撑理由）`，Supervisor 确认后删除。

输出方式：draft.tex 中已有 Related Work 节 → 用 Edit 填入/替换（保留原有内容为注释）；
无 → 输出独立 `related_work.tex` 到草稿同目录。

### Step 6：missing citations 清单

在会话中输出库外必引论文清单（标题 + 一句话理由 + 建议的 arXiv 检索词），
建议 Supervisor 先对它们跑 paper-digest 再重跑本流程补全。

## Guard（Related Work 流程专属）

- `\cite{}` 的 key 必须存在于 references.bib / paper_index.json——禁止编造 key 或凭
  训练记忆引用库外论文。
- 每个 cite 必须有 EVIDENCE 注释（可追溯到具体 Papers/ 笔记）。
- 不改动 draft.tex 中 Related Work 以外的任何内容。
- 对 Supervisor 自己论文的贡献陈述不做修改，只写相关工作。

## Verify（Related Work 流程专属）

- [ ] 产出的所有 `\cite{key}` 均能在 .bib 中 grep 到
- [ ] 每段有与本文的区隔句（"In contrast, ..." / "Unlike ..."）
- [ ] EVIDENCE 注释完整；missing 清单已输出（可为空）
- [ ] LaTeX 可编译（至少无未闭合环境；有条件时跑 pdflatex 冒烟）

## Example

`main.tex + "agent-facing environment" + 4 段` →
借 Topics/CUA-Survey 的分类起草 4 段（GUI agents、agent 环境与 benchmark、
verifier/reward、runtime affordance），28 个 cite 全部来自 references.bib，
missing 清单 2 篇。

写作质量标准（三步流程、常见反模式）另见 [related-work-guide.md](related-work-guide.md)。
