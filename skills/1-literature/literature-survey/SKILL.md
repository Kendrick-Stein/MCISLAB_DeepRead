---
name: literature-survey
description: >
  当 Supervisor 说"调研""survey""了解研究现状"，或需要系统了解某主题的文献全貌时，搜索外部文献、批量 digest、综合生成调研报告
argument-hint: "<topic> [scope] [--run-id <id> --resume-stage <stage>]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent
---

## Purpose

给定一个研究主题，主动搜索外部文献、自动调用 paper-digest 生成结构化笔记，最终综合所有论文产出一份领域调研报告。

## Steps

### Step 1：明确调研范围

解析用户输入，确定以下参数：

| 参数 | 默认值 | 说明 |
|:-----|:-------|:-----|
| `topic` | （必填） | 研究主题 |
| `year_range` | 近 3 年 | 时间范围 |
| `venue_preference` | 无 | venue 偏好 |
| `max_papers` | 20 | 最终纳入调研的论文数量上限 |
| `scope` | `full` | `full` = 外部搜索 + vault 综合；`vault-only` = 只综合库内已读论文，产出报告到 Reports/（触发词："根据已读论文写个 XX 报告""vault 里关于 XX 的综合"） |

基于 topic 生成 **搜索策略**，覆盖两组角度。

若上层传入 `--run-id`，读取并复用该 manifest；校验 topic 与 artifact paths 后，从 `--resume-stage` 或首个未完成 stage 继续，禁止重复已完成 discovery/digest。否则生成新 `run_id`（如 `survey-<topic>-YYYYMMDD-HHMM`）。所有模式均遵循 `references/research-run-protocol.md`。

**A. 覆盖角度**（建立地图）：

1. **核心主题**：topic 本身的直接搜索
2. **相关方法**：该领域的主流技术路线
3. **Survey / 综述**：搜索已有 survey 论文作为参考锚点
4. **Benchmark / 数据集**：该领域常用的评测基准
5. **应用场景**：下游应用或跨领域迁移

**B. 证据完整性角度**（区分"文献地图"与"论文列表"，至少各跑一条）：

6. **矛盾检索**：challenge / failure / limitation / counterexample / reassessment / replication——主动找与主流结论相反的证据
7. **负结果检索**：negative result / no improvement / failed to reproduce / ablation 失败——被主流叙事略过的证据
8. **邻域检索**：相邻学科是否以不同术语研究了同一问题或机制
9. **术语漂移检索**：用该问题在不同年代/学科的旧名称重新检索，避免只用当前流行词

每条策略生成 1-2 个具体的搜索 query（英文）。B 组即使产出"未发现反例/负结果"也要在综合分析中记录——"缺矛盾"本身是覆盖信号。

### Step 2：Vault-first 检索

在执行外部搜索之前，先检查 vault 中已有的相关内容：

1. 用 Grep 在 `Papers/` 的 frontmatter 和正文中搜索 topic 相关关键词（2-3 个核心关键词）。
2. 用 Grep 在 `Topics/` 中搜索是否已有相关调研或分析。
3. 收集所有匹配的 Paper 笔记，建立"**已知论文清单**"（title 列表），后续用于去重。
4. 若发现已有 Survey（如 `Topics/{Topic}-Survey.md` 已存在），先检查 frontmatter。若 `status: merged`，沿 `merged_into` 读取 canonical survey 并把后续检索、综合与写入目标全部改为 canonical；redirect 只读且不得复活。否则读取原文件作为基线，后续步骤在此基础上增量更新（补充新论文、更新分析），而非从零重建。
5. **覆盖度审计**：对照基线 survey 与已知论文清单，列出当前缺口——哪个子问题无代表作、哪条路线仅单一来源、哪个结论无独立验证、缺哪个时段/benchmark、是否只有支持证据而无反例。**Step 3 的外部检索优先针对这些缺口**（active-learning 式），而不是继续召回与已有论文相似的工作；缺口列表写入调研日志。

### Step 3：外部搜索与筛选

**`scope: vault-only` 时跳过本步与 Step 4**（不做外部搜索、不新增 digest），直接以 Step 2 的库内命中论文进入 Step 5 verification gate，再进入 Step 6 综合分析。

调研走 **两条互补检索通道**，合并候选：

**通道 A — OpenAlex 主题检索（零 token，覆盖期刊/venue）**：先对核心 query 跑 OpenAlex 搜索，捞回 WebSearch（偏 arxiv）容易漏掉的期刊/顶会论文（IJCV/TNNLS/TPAMI/CVPR 等）。每个核心 query 跑一次：

```bash
python3 skills/1-literature/daily-papers/fetch_and_score.py \
  --search "<query>" --year-from <起始年> --limit 25
# 可选 --venues 0920-5691,0162-8828 限定 ISSN（逗号分隔）
```

输出 JSON 数组（title/authors/abstract/url/doi/venue/date）。`url` 优先 arxiv 链接、否则 doi.org，可直接喂给 Step 4 的 paper-digest（doi/CVF 走 paper-digest 对应分支）。

**通道 B — WebSearch（开放网络）**：

1. 对每个 query，用 **WebSearch** 搜索（建议加 `site:arxiv.org` 或 `"论文标题" arxiv`），提取搜索结果中的论文信息。
2. 从搜索结果中收集候选论文列表，提取：title、authors、year、venue（若可判断）、url。

**合并与去重**：

3. **去重**：将每个候选论文的 title（转小写，去标点）与已知论文清单及两通道彼此对比，跳过重复（同一论文 arxiv 版与期刊版视为一篇）。
4. **搜索轮数上限**：OpenAlex 最多 5 次 `--search`、WebSearch 最多 **10 次**。若某些 query 返回结果质量低（无相关论文），提前停止该策略。

**搜索/抓取兜底**：若 WebSearch 或 WebFetch 在 arXiv / HuggingFace 上卡顿，先读取 `references/network-fetch-fallback.md`。对已知标题可构造 arXiv search URL 或 HuggingFace paper URL 后用：

```bash
python3 scripts/lexmount_fetch.py extract "<url>" --format markdown
```

该兜底只用于恢复真实页面内容，不得用来凭空扩展候选论文；纳入候选的论文仍必须有可访问来源。

搜索完成后，对所有候选论文进行筛选和排序：

- **相关性**：与 topic 的直接相关程度
- **影响力**：优先选择知名 venue 或者知名机构的论文
- **时效性**：在 year_range 内的论文优先
- **多样性**：确保覆盖不同技术路线，避免全部来自同一方向

选取 **top-N**（N = `max_papers` 减去 vault 中已有的相关论文数，最少 3 篇）作为待 digest 的论文列表。

### Step 4：批量 paper-digest

对 Step 3 筛选出的每篇论文，执行 paper-digest：

1. 读取 `skills/1-literature/paper-digest/SKILL.md`。每个并行 worker 以论文 arXiv URL（优先）或标题运行 `paper-digest --prepare-only`，返回带 Evidence Ledger 的 artifact envelope，禁止共享写入。
2. 从 `team-config.json` 读取 global / prepare 并发与 checkpoint；nested verifier 计入 global limit（默认 global=4、prepare=2），coordinator 按顺序串行执行 paper-digest Step 5-6 commit contract。
3. **跳过规则**：
   - 若 paper-digest 的去重检查发现 vault 已有该笔记，跳过。
   - 若 WebFetch 无法获取论文内容（如非 arXiv 论文、付费墙），先按 paper-digest 的 Lexmount fallback 重试；仍失败才记录为"未能获取"并跳过，不阻塞流程。
4. 每批 prepare 与每批串行 commit 后更新 run manifest；单篇失败不丢弃已成功 artifact。
5. 记录每篇论文的 digest 结果：成功（文件路径 + verification status）/ 跳过（原因）/ 失败（原因）。

### Step 5：Verification Gate + Post-verification Gap Pass

在写 survey 前建立高影响 claim matrix。优先收集：Key Results 数字、SOTA/novelty、跨论文 benchmark 比较、因果/机制结论、license/code 状态、Open Problem 的 closest-prior-art 判断。

1. 新 digest 笔记直接读取 Evidence Ledger。既有 legacy 笔记若没有 ledger，标为 `legacy-unverified`；不得因它已在 vault 就自动视为已核查。
2. 对会进入 Overview / benchmark 表 / Key Takeaways / Open Problems 的高影响 claim，派发独立 verifier。Verifier 只接收 primary source + claim matrix，不接收 Finder/Digest reasoning 或拟写 survey 结论。`scope: vault-only` 不联网，只消费现有 Evidence Ledger；缺 ledger 的 claim 保持 legacy-unverified，不临时抓外部来源。
3. 统一状态为 `source-verified / unsupported / contradicted / not-checkable / abstract-only`。只有 source-verified claim 可以无保留进入关键结论；其他状态必须删除、纠正或明确降级。
4. 跨论文比较还要核对 environment、verifier、step budget、backbone、dataset split 与 cost setting；设置不可比时禁止写成横向胜负。
5. 将 claim counts、争议项和修订记录写入 run manifest。高影响分歧不能解决时标 `needs-human`，不要用多数投票制造确定性。

**Deep research 放在验证之后**：基于已通过 gate 的 claim graph 再做一次 post-verification gap audit。`scope: full` 时最多执行 3 个定向 query，只补以下缺口：缺 primary source、只有单一支持、缺反例、关键 comparator 缺失、benchmark setting 不可比。新发现论文必须走 Step 4 digest + 本 Step verification 后才能进入综合；整个 gap loop 最多 1 次。`scope: vault-only` 时不联网，只记录 unresolved gaps。

这一阶段的目标是深化和补洞，不是重新打开无界探索。若预算用尽，带着明确 unresolved gaps 进入 partial synthesis，而不是没有产物地终止。

### Step 6：综合分析

基于 vault 中所有相关论文笔记（Step 2 已有的 + Step 4 新 digest 的），进行综合分析：

1. 用 Read 读取所有相关 Paper 笔记（重点：Summary、Method、Key Results、Strengths & Weaknesses）。
2. 读取 `DomainMaps/_index.md`（索引页）找到相关 domain，再读取对应的 `DomainMaps/{Name}.md` 了解当前认知状态。

读取`Templates/Survey.md` 按其中的 section 结构综合分析。综合时遵守证据纪律：

- **Consensus 门槛**：一个结论只有在多篇独立（非同一研究组、非高度相似实验设置）论文支持、且无未讨论反例时，才能称"领域共识"；仅单篇/仅同组/仅 benchmark 分数支撑的，表述为"某工作发现"。
- **区分四态**：显式区分 已知共识 / 活跃争议 / 作者推测 / 未知；出现冲突结果时不强行选"正确答案"，而是记录冲突并分析来源（数据分布/任务定义/指标/实现/规模/统计功效/隐含假设不同）。
- **Full-text before strong conclusion**：核心方法、实验结论、机制、失败条件必须溯到全文 Paper 笔记；仅有 abstract 的笔记不得作强结论证据。
- **引用 ≠ 继承/支持**：后续论文引用前作不等于继承或支持它；关系判断以内容为准。
- **Claim-level provenance**：关键数字与比较必须能回到 Paper Evidence Ledger 的 claim ID / source locator；wikilink 到整篇笔记不再自动满足强 claim 的可溯性要求。
- **验证边界**：`source-verified` 只表示 primary source 包含该说法，不等于结果已独立复现；涉及可复现性时必须另有独立 paper/experiment 证据。
- **Evidence Matrix**：Overview、benchmark 横向判断、Key Takeaways 与 Open Problems 的高影响 claim 必须登记到 Survey 的 Key Evidence Matrix，显式写 state、claim IDs/locators、反例与边界。

### Step 7：产出

#### 7a. 生成 Survey 文件

**`scope: vault-only` 时**输出到 `Reports/YYYY-MM-DD-{Topic}-Report.md`（报告性质，不覆盖 Topics/ 下的正式 survey），frontmatter 增加 `scope: vault-only`；以下 survey 文件规则仅适用于 `scope: full`。

Topic 名称根据主题生成（CamelCase，如 `VLA-Manipulation`、`DiffusionPolicy-Robotics`）。

- **新建**：若 `Topics/{Topic}-Survey.md` 不存在，用 Write 按 `Templates/Survey.md` 模板创建并填充各 section。新建 survey 必须填 frontmatter `keywords`（小写短语）与 `domain_map`（无对应 DomainMap 填 null），否则该 survey 无法进入 digest→survey 信息流。
- **增量更新**：若已存在且不是 `status: merged`，用 Edit 在其基础上补充新论文、刷新分析，保留原有内容中仍然有效的部分。若命中 merged redirect，只更新其 `merged_into` 指向的 canonical survey。

所有论文引用使用 `[[wikilink]]` 格式。

**写作基线（Supervisor 2026-07-07 手改确立，最基础要求）**：

1. **一句话结论就是一句话**：Overview 首句只保留单一核心论题；并列的分类/需求轴用竖排 bullet list，不塞进长句。
2. **零对话性内容**：survey 是沉淀文档，不是对 Supervisor 的回复——不写"直觉得到验证"式框架、导览铺垫、与其他 survey 的分工说明；"建议加入 DomainMaps"等流程注记只放调研日志。
3. **标题平实**：用"时间段/对象：内容"式描述性标题，不用叙事修辞（如"五幕""第 X 幕"）。
4. **每行一个论点**：拆长复合句；演进链（A→B→C）竖排分行、每级加粗。
5. **砍论据的展开，不砍论断的解释**：机制细节（文件系统原理、算法推导）留在 Paper 笔记，正文只留论断 + 关键数字 + wikilink；反之，**预测/新概念/反直觉论断必须 self-contained 展开 2-4 句**（是什么/为什么/萌芽证据）——压缩成标签再靠事后口头解释 = 写作失败。
6. **Takeaway ≤5 条且硬**：只留可操作/可预测/指向行动的结论；类比只留一句 thesis，不留论证展开。
7. **表格优先**：凡"维度 × 对象"的对比（能力矩阵/需求分层/用途分化）一律表格化——表格是 survey 最高价值资产。
8. **章节成段叙事，不做罗列**（Supervisor 2026-07-21 补充）：每章开篇设"发展进程与研究现状"叙事段，章末有待解决问题段；概念分类、发展阶段、风险面等内容写成按因果链组织的完整段落（每一步解决了什么、又暴露了什么），不做方法名的 bullet 罗列。表格保留，但每张表前需 1-3 句框架段说明它回答什么问题，重要谱系表后加综合段。第 4 条的"演进链竖排"仅适用于单一机制的紧凑 lineage，不适用于章节级发展叙事。
9. **正文零内部痕迹**（Supervisor 2026-07-24 review 确立）：(a) 给作者的写作要求不入正文（"避免按 X 罗列""以下不是质量排序"——文章要实现要求，不是写出要求）；(b) 作者论断用综述语言标示（"本文进一步论证 X；支撑证据集中于 §m/§n，尚缺独立复现"），不写"本综述提出一个作者综合论断……该论断不是领域共识"式官僚自指，hedge 保留但必须落在具体章节/证据指针上；(c) 内部工具词（vault/库内/本轮/paper-digest/verification_status/见 gaps）与比喻黑话（水位/押注/战场/收束/裸比）不入正文——内部记账只留在 Key Evidence Matrix 与调研日志；"库内暂无独立验证"的正文写法是"尚未见独立验证"，且范围限定词不可丢。

#### 7a.5 结构配图

Survey 定稿前为核心脉络配 1-3 张结构图，帮读者 5 秒抓住全貌、降低阅读时间：

- **选点**：分类总览（taxonomy 一图收拢）、方法演进时间线、RQ/证据链结构图——挑收益最大的
  1-3 处，不逐章配图。
- **工具分层**：简单结构用 Mermaid 直接内嵌；信息密度高/出版级的图调用 `academic-diagram`
  生成 TikZ，渲染 PNG 到 `assets/figures/`（命名 `{survey缩写}-{章节}-{主题}.png`），
  正文以 `![[name.png]]` 嵌入并在图下加一句 caption。
- **证据纪律同正文**：图不得引入正文没有的结论或数字；分类图的归属必须与正文表格一致。

#### 7b. 追加日志

用 Edit（若文件不存在则用 Write）将以下格式的 log entry 追加到 `Workbench/logs/YYYY-MM-DD.md`：

```markdown
### [HH:MM] literature-survey
- **input**: topic: <topic> | year_range: <year_range>
- **output**: [[Topics/{Topic}-Survey]]
- **stats**: 搜索 N 次，候选 N 篇，digest N 篇（成功 N / 跳过 N / 失败 N）
- **verification**: source-verified N / downgraded N / disputed N；post-verification query N
- **run_id**: <run_id>（completed / partial）
- **observation**: <一句话概括该领域的核心发现>
- **status**: success
```

若日志文件不存在，先创建文件（包含一级标题 `# YYYY-MM-DD`），再追加 entry。

## Guard

- **paper-digest 失败不阻塞**：单篇论文 digest 失败时记录原因并继续处理下一篇，不中断整个 survey 流程。
- **merged survey 只读**：frontmatter 含 `status: merged` 的文件只承担旧链接跳转，不得恢复 keywords、追加正文或重新参与增量更新；必须沿 `merged_into` 写入 canonical survey。
- **搜索上限**：使用 `orchestration.max_search_queries`（默认 10）；50 是任何配置都不得突破的硬上限。
- **后置深搜有界**：verification 后的 gap pass 最多 3 个 query、1 个回环；不得借“补洞”重新启动无界全量搜索。
- **不捏造论文**：所有纳入分析的论文必须来自实际搜索结果或 vault 已有笔记，不得凭记忆编造论文信息。
- **不把"未检索到"当"无人研究"**：外部检索为空只能表述为"在当前检索范围内未发现"，不得写成"尚无人研究""首次""全新方向"。
- **不直接修改 DomainMaps**：综合分析中如有值得纳入 DomainMaps 的发现，在 Survey 文件的调研日志中标注"建议加入 DomainMaps"（不放 Key Takeaways，见写作基线第 2 条），不得直接修改 `DomainMaps/` 下的任何文件。
- **Papers/ 已有笔记只读**：不得修改 vault 中已存在的 Paper 笔记，只可读取。新论文的笔记由 paper-digest 创建。
- **Finder ≠ Verifier**：提出或抽取 claim 的 agent 不得给同一 claim 判 source-verified；无法独立核查时必须降级。
- **并行只读、串行 commit**：并行 workers 只运行 paper-digest prepare-only；Papers、queue、日志、BibTeX 与 survey-updates 由 coordinator 单写者提交。

## Verify

- [ ] `Topics/*-Survey.md` 已创建
- [ ] 技术路线分类 ≥2 条
- [ ] Datasets & Benchmarks 表非空
- [ ] Key Evidence Matrix 覆盖 Overview / Key Takeaways / Open Problems 的高影响 claims
- [ ] Open Problems 节非空
- [ ] **写作基线**：Overview 首句为单一论题句；全篇无对话性内容与流程注记（后者只在调研日志）
- [ ] **展开度**：Takeaway 中每条预测/新概念/反直觉论断都有 2-4 句 self-contained 解释，可脱离对话独立读懂
- [ ] **成段叙事**：各章有发展进程/研究现状叙事段与章末待解决问题段；无孤立 bullet 罗列；每张表前有框架段
- [ ] **证据完整性**：至少跑过矛盾/负结果检索；综合中区分共识/争议/推测/未知；无未经验证的"首次/无人研究"表述
- [ ] **可溯性**：关键 claim 可溯到全文 Paper Evidence Ledger 的 claim ID + locator（非仅 abstract）；Open Problems 每条标注 Observed Tension 或 Validated Gap
- [ ] **独立验证**：高影响 claims 由不同于 Finder/Digest 的 verifier 检查；unsupported/contradicted 未进入强结论
- [ ] **后置补洞**：deep gap pass 在 verification 后执行且未超过 3 query / 1 loop；vault-only 仅记录 gaps
- [ ] **可恢复性**：run manifest 有 stage/checkpoint/claim counts；partial run 仍产出带边界的 survey/report
- [ ] **配图**：核心脉络（taxonomy/演进线）至少 1 张结构图（Mermaid 或 academic-diagram PNG），图文一致

## Examples

**示例 1：调研一个主题**

```
"调研一下 VLA for manipulation 的研究现状"
```

执行过程：

1. 解析：topic = "VLA for manipulation"，year_range = 2023-2026
2. 生成搜索策略：
   - "Vision-Language-Action models manipulation arxiv"
   - "VLA robot manipulation policy learning"
   - "VLA survey embodied AI"
   - "manipulation benchmark evaluation VLA"
3. Grep `Papers/` 搜索已有 VLA 相关笔记，发现 3 篇
4. WebSearch 执行 6 次搜索，收集 20 篇候选，去重后剩 14 篇
5. 筛选 top-5
6. 并行 prepare-only + coordinator 串行 commit：成功 4 篇，失败 1 篇（付费墙）
7. 独立 verifier 核查高影响 claims；对已验证 claim graph 做 bounded gap pass
8. 综合分析 7 篇论文（3 已有 + 4 新增），生成调研报告
9. Write `Topics/VLA-Manipulation-Survey.md` 并更新 run manifest / 日志

输出文件：`Topics/VLA-Manipulation-Survey.md`

---

**示例 2：带约束的调研**

```
"survey diffusion policy in robotics，只看 2024 年以后的 top venue 论文，最多 5 篇"
```

执行过程：

1. 解析：topic = "diffusion policy in robotics"，year_range = 2024-2026，venue_preference = top-tier
2. Grep `Papers/` 发现 1 篇已有
3. WebSearch 搜索，优先筛选 CoRL / RSS / ICRA / NeurIPS / ICML 论文
4. 筛选 top-4
5. prepare-only digest + 串行 commit，独立核查高影响 claims
6. verification 后仅针对 unresolved gaps 做 bounded search
7. 综合分析，生成报告并写 run manifest
8. Write `Topics/DiffusionPolicy-Robotics-Survey.md`

输出文件：`Topics/DiffusionPolicy-Robotics-Survey.md`
