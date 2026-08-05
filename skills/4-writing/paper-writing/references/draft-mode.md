# Draft 模式 — 从 vault 素材起草章节

（原独立 skill `draft-section`，2026-07-28 并入 paper-writing。触发："写一下 introduction"
"起草 related work""起草报告章节"，或 autoresearch 判断某 direction 已积累足够素材需要成文。）

给定目标文件、章节名和素材引用列表，从 vault 读取所有相关笔记，按学术写作规范起草指定章节
并写入目标文件。适用于 Reports/、Topics/ 报告章节与论文早期中文草稿；正式英文 LaTeX 论文
进入 Paper 模式（SKILL.md 的 11-step 流程）。

参数：`<target> <section> <sources>`

## Steps

### Step 1：读取素材

根据 `sources` 参数读取所有引用笔记：

- 用 Glob 确认文件存在，再用 Read 逐一读取每个引用文件的完整内容。
- 涵盖范围：`[[Papers/...]]`（论文笔记）、`[[Experiments/...]]`（实验记录）、
  `[[Ideas/...]]`（研究想法）、`[[Topics/...]]`（跨论文分析）。
- 对每份素材重点提取：核心论点、关键数据、方法细节、引用文献
  （如 frontmatter 中的 `title`/`authors`/`venue`）。

若某个 `[[wikilink]]` 指向的文件不存在，在执行日志中记录"未找到：{path}"，跳过该文件，
继续处理其余素材。

### Step 2：读取目标文件上下文（若已存在）

若 `target` 文件已存在：

1. Read 完整内容，了解：已有章节结构（标题层级）、内容风格（语言/术语/引用格式）、
   `section` 指定的章节是否已有占位符或草稿。
2. 确定插入位置：若目标章节已有标题但无内容，插入标题之后；若无对应标题，在文件末尾追加新章节。

若 `target` 不存在，则在 Step 5 用 Write 创建新文件。

### Step 3：读取 DomainMaps

Read `DomainMaps/_index.md`，找到与 `section` 和 `sources` 相关的 domain，再读取对应的
`DomainMaps/{Name}.md`。重点关注：

- **Established Knowledge**：在 Related Work / Introduction 中准确描述领域背景，避免过时"共识"。
- **Active Debates**：在 Introduction / Discussion 中定位贡献，或在 Related Work 中点出未解决问题。
- **Open Questions**：作为 Introduction 的 motivation 依据。

无明显相关 domain 则跳过。

### Step 4：起草章节

**语言规范**：正文中文；模型名、方法名、benchmark 名等技术术语保持英文。学术风格，避免口语化。

**结构规范**（按 `section` 类型参考，不机械套用）：

| Section | 典型结构 |
|:--------|:---------|
| Introduction | 背景 → 问题陈述 → 现有方法局限 → 本文贡献 → 章节组织 |
| Related Work | 按主题分组 → 每组综述 → 与本文关系 |
| Method | 整体框架 → 核心模块 → 关键设计选择 |
| Experiments | 设置 → 指标 → 结果分析 → 消融实验 |
| Discussion | 主要发现 → 局限性 → 未来方向 |

**引用规范**：每个 claim（事实性陈述、数据引用、方法描述）必须附 `[[wikilink]]`；
格式如 `…如 Diffusion Policy [[2303-DiffusionPolicy]] 所示…`；无法在素材中找到来源的
claim 标注 `[需引用]`，不编造。

**禁止占位符**：必须基于素材完整成文，不留 `[TODO]`、`[待补充]`。

**收尾自查**：写完后读 `references/writing-style.md`，按 §A3（语气层）与 §A4（版本层）过一遍——
这两组是自动起草最常见的残留。§A3 抓格言体、制造金句、导览铺垫、权威腔、对话残留；
§A4 抓"本节新增了""相比上一版补充了"这类只对 diff 有意义的句子。反向规则见 §B：
hedge 不删，只删跟不上条件/数字/具体检验方式的空 hedge。

### Step 5：写入目标文件

**`target` 不存在**：Write 创建，frontmatter 含 `date` / `title` / `tags: []`，
正文为 `## {section}` + 起草内容。

**`target` 已存在**：Edit 将内容插入 Step 2 确定的位置；只操作指定章节，
不修改文件中的其他任何内容。

### Step 6：追加日志

追加到 `Workbench/logs/YYYY-MM-DD.md`（文件不存在则先创建，含一级标题 `# YYYY-MM-DD`）：

```markdown
### [HH:MM] paper-writing (draft)
- **input**: target: {target} | section: {section} | sources: {sources 列表}
- **output**: [[{target}]] § {section}
- **word_count**: 约 N 字
- **missing_sources**: <未找到的 wikilinks，若无则填"无">
- **status**: success
```

## Guard（Draft 模式专属）

- **不修改其他章节**：Edit 只针对指定 `section`；不确定插入边界时停止并告知 Human。
- **不捏造引用**：所有 `[[wikilink]]` 必须指向 vault 中实际存在的文件；无来源标 `[需引用]`。
- **不覆盖完整章节**：目标章节已有实质性内容（>100 字）时不直接覆盖，停止并建议改用
  writing-refine 修订。

## Verify（Draft 模式专属）

- [ ] 指定章节已写入 `target` 且正文 >200 字
- [ ] 每个事实性陈述附有 `[[wikilink]]` 来源
- [ ] 不含 `[TODO]`、`[待补充]` 等占位符
- [ ] 已按 `references/writing-style.md` §A3/§A4 自查（语气层与版本层残留），且 §B 的 hedge 未被误删
- [ ] 未修改 `target` 中其他已有章节的内容
- [ ] 日志已追加到 `Workbench/logs/YYYY-MM-DD.md`
