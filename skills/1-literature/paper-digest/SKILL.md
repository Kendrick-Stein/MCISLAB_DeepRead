---
name: paper-digest
description: >
  当 Supervisor 给出论文或 blog 的 URL/标题/PDF/DOI，或阅读队列中有待处理条目时，消化内容并生成结构化笔记到 Papers/
argument-hint: "[arXiv URL / blog URL / PDF path / title / DOI] [--prepare-only]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent
---

## Purpose

给定一篇论文或技术 blog 的来源（URL、PDF 路径、标题或 DOI），它自动获取内容、提炼核心信息，并按照 `Templates/Paper.md` 格式生成结构化笔记保存至 `Papers/`。

支持两种内容类型：
- **论文**：arXiv、PDF、DOI 等学术论文
- **Blog**：技术博客文章（如 Google Research Blog、Lilian Weng、公司技术博客等）

支持两种提交模式：

- **direct（默认）**：单篇任务直接完成 source check、落库、引用身份、日志与 survey 记账。
- **`--prepare-only`**：供 `daily-papers` / `research-team` 并行使用；只返回完整 draft + verification report，禁止写 `Papers/`、queue、日志、BibTeX cache 或 `survey-updates.json`。由 coordinator 串行执行 Step 5-6 commit contract。

## Steps

### Step 1：获取论文内容

根据 `source` 的类型选择获取方式：

- **arXiv URL**（如 `https://arxiv.org/abs/2603.08127`）：用 WebFetch 抓取该页面。若需要正文，同时抓取对应的 HTML 全文页（如 `https://arxiv.org/html/2603.08127`）。
- **CVF Open Access URL**（如 `https://openaccess.thecvf.com/content/CVPR2026/html/..._paper.html`）：**全文** 走同名 PDF（把路径中的 `/html/` 换成 `/papers/`、`.html` 换成 `.pdf`，即 `.../content/CVPR2026/papers/..._paper.pdf`）。⚠️ **thecvf.com 对 WebFetch 的 UA 返回 403**，必须用 Bash + curl 带浏览器 UA 下载 PDF 再用 Read 读取：
  ```bash
  curl -s --max-time 90 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
    -o /tmp/cvf_paper.pdf "<pdf_url>"
  ```
  然后 `Read /tmp/cvf_paper.pdf`（>10 页需指定 `pages`）。abstract、作者等元数据可同样用 curl 抓 html 页解析（`id="abstract"` / `id="authors"`），或直接从 PDF 首页提取。`venue` 字段按 proceeding 填，如 `CVPR 2026`、`ICCV 2025`。CVF 论文 PDF 免费且完整，应获取全文而非停留在 abstract。若候选来自 daily-papers，其 `pdf_url` 字段已给出 PDF 直链。
- **PDF 路径**（如 `/path/to/paper.pdf`）：用 Read 读取文件内容。
- **论文标题或关键词**：用 WebSearch 搜索（建议加上 `site:arxiv.org` 或 `filetype:pdf`），从结果中定位最可能的论文页面，再用 WebFetch 获取内容。
- **DOI**（如 `10.1145/...`）：用 WebFetch 抓取 `https://doi.org/<DOI>`，跟随重定向到出版商页面。
- **Blog URL**（非 arXiv/DOI 的普通网页链接）：用 WebFetch 抓取页面内容。从页面中提取作者、发布日期等元数据。

**网络兜底协议**：若 WebFetch / WebSearch 卡住、返回空内容、只拿到 abstract、或 arXiv / HuggingFace 页面无法完整读取，读取 `references/network-fetch-fallback.md` 并启用 Lexmount fallback。关键约束：

1. 不把 API key 写入笔记、日志、frontmatter 或可提交文件；只从 `LEXMOUNT_API_KEY` 或已被 `.gitignore` 忽略的 `.env` 读取。
2. arXiv 全文优先尝试 `https://arxiv.org/html/<arxiv_id>`，再尝试 `https://ar5iv.labs.arxiv.org/html/<arxiv_id>`；用：
   ```bash
   python3 scripts/lexmount_fetch.py extract "<url>" --format markdown
   ```
3. 若 `extract` 结果仍不完整，再用 DOM dump 检查：
   ```bash
   python3 scripts/lexmount_fetch.py dump "<url>" --engine lightmount_domstable --format text
   ```
4. HuggingFace papers / model / dataset 页面或动态页面卡顿时，先 `extract` 公共页面；仍失败再 `dump --engine chrome_cdp`。
5. Lexmount 也失败时，明确记录"未获取全文"，不得补写正文细节。

从获取到的内容中提取以下元数据（如果全文无法获取，至少要获取 abstract）：

| 字段             | 说明                                      |
| :------------- | :-------------------------------------- |
| `title`        | 完整论文标题                                  |
| `authors`      | 作者列表（字符串数组）                             |
| `institute`    | 作者所属机构（字符串数组，从 affiliation 提取）          |
| `date_publish` | 发表日期，格式 `YYYY-MM-DD`、`YYYY-MM` 或 `YYYY` |
| `venue`        | 发表场所，如 `NeurIPS 2025`、`arXiv`；blog 填来源名如 `Google DeepMind Blog`、`Lilian Weng Blog` |
| `url`          | 论文链接（优先用论文主页，无则用 arXiv abstract 页）     |
| `arxiv_id`     | arXiv id，如 `2606.19409`（非 arXiv 论文留空）        |
| `doi`          | DOI，如 `10.1109/TPAMI...`（期刊/会议有则填，否则留空）  |
| `code`         | GitHub 代码链接（若论文中提及）                     |

### Step 2：阅读并理解

**Read Critically**——论文不是圣经。找出隐含假设和适用边界，ablation、failure case、baseline 选择往往比 main result 更有信息量。对高引论文同样保持批判。

通读获取到的内容，重点提炼以下四个维度：

1. **Problem & Motivation**：作者要解决什么问题？现有方法有什么局限？为什么这个问题重要？
2. **Method**：核心方法/架构是什么？关键设计选择有哪些？用简洁的中文描述，保留必要的英文术语。对于 blog，此处提炼文章的核心论点或技术方案。
3. **Key Results**：主要实验结果是什么？在哪些 benchmark 上取得了什么指标？核心 takeaway 是什么？对于 blog，提炼关键结论、数据或 demo 效果。
4. **Strengths & Weaknesses**：方法的亮点与局限，以及对该领域的潜在影响。严格区分已知、推测、不知道——不 overclaim，不掩盖方法的局限。

如果只能获取 abstract 而非全文，在所有内容区块开头加注：`> [未获取全文，仅基于 abstract]`

### Step 2.5：建立高风险 Claim Package

在起草笔记前，把会进入 Summary / Key Results / Strengths & Weaknesses 的高风险信息提取为紧凑 claim package：

| 字段 | 要求 |
|:--|:--|
| `claim_id` | `C1`、`C2`…，在本笔记内稳定 |
| `claim` | 可独立判断真假的一句话，不把多个断言揉在一起 |
| `type` | number / comparison / sota-novelty / benchmark-setting / license-code / causal-mechanism |
| `expected_locator` | page / section / table / figure；暂时找不到填 `unknown` |
| `source` | primary source URL 或本地 PDF 路径 |

普通背景、作者明确标注的 speculation、以及个人评价不必逐句建 claim。高风险数字不得只从搜索摘要、二手报道或既有 Paper note 复制。

### Step 3：确定文件名和 tags

**文件名格式**：`YYMM-ShortTitle.md`

- `YYMM`：取自 `date_publish` 的年份后两位 + 月份，如 `2603`（2026年3月）
- `ShortTitle`：标题的 CamelCase 缩写，2-4 个关键词，如 `EvoScientist`、`RoboClaw`、`DiffusionPolicy`
- Blog 同理，如一篇 2026 年 2 月的 blog 关于 scaling laws → `2602-ScalingLaws.md`

**去重检查**：用 Glob 扫描 `Papers/` 目录，检查是否已存在同名或同主题笔记（搜索标题关键词）。若发现重复，停止并告知 Human，不创建新文件。

**Tag 选择**：阅读 `references/tags.md`，按照规范选择 tag。

### Step 4：生成笔记

读取 `Templates/Paper.md`，按模板中的字段和 `%%` 注释指导填写所有内容。

补充规则（模板未涵盖的）：
- **rating**：必填，按模板中的 1-5 分制评分，基于内容质量和与当前研究方向的相关性综合判断
- **未获取全文**：在受影响的章节开头加注 `> [未获取全文，仅基于 abstract]`，不得推测正文内容
- **content_scope**：全文已读填 `full-text`；否则填 `abstract-only`
- **verification_status**：由 Step 4.5 的结果填写；不得把 source check 写成“独立复现”或“结论已被验证”
- **Evidence Ledger**：每个高风险 claim 一行；原文短摘录最多 25 words，并保留 page/section/table/figure locator
- **date_added**：填写今天日期，格式 `YYYY-MM-DD`
- **配图**：Mind Map 一律用 Mermaid（笔记内原生渲染）；若论文架构复杂、Supervisor 明确要
  出版级结构图，则在 digest 完成后另行调用 `academic-diagram`（不并入本轮，保持原子性）

### Step 4.5：独立 Source Verification

Finder / digest 作者不得自行给自己的 claim 判 `source-verified`。派发一个**独立 verifier agent**，只给它：primary source、Step 2.5 claim package、允许的状态定义；不要给 Finder 的推理过程、rating 或 Strengths & Weaknesses。

Verifier 对每个 claim 独立定位原文，返回：

```text
claim_id | status | source_locator | evidence_excerpt | correction
```

状态只能是：

- `source-verified`：primary source 明确支持；仅表示 source consistency，不表示独立复现。
- `unsupported`：没有找到足够支持，或证据比 claim 弱。
- `contradicted`：primary source 与 claim 冲突。
- `not-checkable`：付费墙、缺页、图表无法读取等导致无法核查。
- `abstract-only`：只能在 abstract 层确认，不能支撑机制、失败条件或强比较。

根据 verifier 结果修订 draft：

1. `unsupported` / `contradicted` claim 不得继续以事实口吻留在 Summary / Key Results；删除、纠正或明确降级。
2. `not-checkable` / `abstract-only` 必须就地标明 evidence boundary。
3. `verification_status`：全部高风险 claim 为 `source-verified` → `source-checked`；部分不可核查但已降级 → `partial`；没有完成独立 source check → `unverified`。
4. verifier 与 Finder 有分歧时，由主 agent 只基于 source locator 裁决；高影响分歧无法解决则保留 `not-checkable`，不得多数投票硬判真。

### Step 5：保存与引用身份

**`--prepare-only` 分支**：到此不落库，返回以下 artifact envelope 后停止：

```text
proposed_path: Papers/YYMM-ShortTitle.md
source_identity: arxiv_id / DOI / canonical URL
note_markdown: <完整笔记>
verification: source-checked / partial / unverified
claim_counts: total / source-verified / downgraded / disputed
commit_preconditions: duplicate check passed / failed
```

禁止在 prepare-only 模式执行下面的共享写入。Coordinator 必须按 artifact envelope 顺序**串行**执行 direct commit contract：落笔记 → YAML/contract 校验 → cite key/BibTeX → queue 完成 → survey 记账 → 日志。单篇 direct 模式同样执行此 contract。

1. **写入文件**：用 Write 将笔记保存到 `Papers/YYMM-ShortTitle.md`。

2. **YAML 前置校验**：写入后立即用 Bash 执行以下检查，确保 frontmatter 可被 Quartz 正确解析：

   ```bash
   f="Papers/YYMM-ShortTitle.md"
   # 检查 title 等字段值中含冒号但未加引号的情况
   awk '/^---$/{n++; next} n==1 && /^[a-z_]+:/{print}' "$f" | while read -r line; do
     value=$(echo "$line" | sed 's/^[a-z_]*: *//')
     if echo "$value" | grep -q ':' && ! echo "$value" | grep -q '^"'; then
       echo "YAML ERROR: unquoted colon in value: $line"
     fi
   done
   ```

   若发现未加引号的字段，立即用 Edit 为该值加上双引号后重新检查。

3. **固化引用身份**：用 Bash 为该论文分配稳定 cite_key 并缓存权威 BibTeX：

   ```bash
   python3 skills/4-writing/latex-citation-enhancer/assign_cite_keys.py Papers/YYMM-ShortTitle.md
   python3 skills/4-writing/latex-citation-enhancer/fetch_bibtex.py Papers/YYMM-ShortTitle.md
   ```

   第一条从 url 抽 `arxiv_id` 并写回 `cite_key`（幂等，已有 key 不变）；第二条把 arXiv/Crossref 权威 BibTeX 存入 `references/bibtex-cache.bib`（抓不到则从 frontmatter 重建）。两条都安全可重复执行。

4. **阅读队列**：若 source 来自 `Workbench/queue.json` 的 `summarize_paper` 任务，在笔记、YAML 与引用身份均成功后运行：

   ```bash
   python3 skills/1-literature/daily-papers/queue_ops.py complete \
     --task-id <task_id> --output-path Papers/YYMM-ShortTitle.md
   ```

   不直接手改 queue JSON；未完成落库前不得提前把任务标为 done。

### Step 6：survey 归属记账与日志

笔记保存后，运行记账脚本把它挂到相关 survey 的待更新队列：

```bash
python3 scripts/survey_updates.py record "Papers/{文件名}.md"
```

- 脚本按 `Topics/*-Survey.md` frontmatter 的 `keywords` 与本笔记 tags/标题匹配（大小写与连字符已归一化），输出匹配到的 survey 列表（JSON）。
- 匹配为空是正常情况（论文不属于任何已有 survey 主题），静默继续。
- 脚本报错时不阻塞 digest：在当日 log 记一条 `survey-updates 记账失败` 即可。
- pending 的消费由 `survey-refresh` skill 负责（GUI canonical 在 ≥1 篇时触发；其他 survey 在 ≥5 篇或最老条目超 7 天时触发）。
- 若输出列表含 `CUA-Survey`，该 pending 是下一 skill round 的强制优先项：在执行任何其他研究任务、或宣告一个包含 digest+整合的多步请求完成前，必须先运行 `survey-refresh`。独立的单篇 digest 可以在本轮结束，但必须明确报告“GUI survey integration pending”；这保留“一轮一个 skill”的原子性，同时保证下一轮立即整合。
- **GUI canonical 特例**：若输出包含 `CUA-Survey`，不等待 5 篇 / 7 天阈值；保持本轮
  paper-digest 原子性，并由下一轮优先执行 `survey-refresh CUA-Survey`。GUI 论文的 tag
  必须遵守 `references/tags.md` 的 umbrella 规则，避免只标 `agentic-RL` 或宽泛 `environment`
  而漏记账。
- **代码库标记**：若 frontmatter `code` 非空且论文属于系统/环境/基建类工作（runtime、
  benchmark 环境、训练基建等——贡献主要在实现里），在日志 entry 末尾附一行
  `repo_candidate: <code URL>`，供 Supervisor / autoresearch 决定是否另起一轮
  `repo-digest` 深挖实现细节（保持本轮原子性，不在 digest 内执行）。

记账结束后，用 Edit（或 Write 若文件不存在）把以下 entry 追加到 `Workbench/logs/YYYY-MM-DD.md`：

```markdown
### [HH:MM] paper-digest
- **input**: <source 的原始内容>
- **output**: [[Papers/YYMM-ShortTitle]]
- **observation**: <一句话描述论文核心贡献>
- **verification**: <source-checked / partial / unverified；verified/total claim 数>
- **survey_updates**: <匹配列表 / none / failed>
- **run_id**: <由上层 orchestrator 传入；独立调用填 standalone-YYYYMMDD-HHMM>
- **status**: success / partial
```

若日志文件不存在，先创建文件（包含一级标题 `# YYYY-MM-DD`）。survey 记账失败不撤销已落库笔记，但必须在 `survey_updates` 和 status 中明确记录 partial。

## Guard

- **不覆盖已有笔记**：若 `Papers/YYMM-ShortTitle.md` 已存在，停止执行并告知 Human，不得覆盖或修改已有文件。
- **不捏造信息**：所有字段必须来自论文原文。无法获取全文时，在受影响的章节开头标注 `> [未获取全文，仅基于 abstract]`，不得推测正文内容填充 Method / Key Results 等节。
- **Finder ≠ Verifier**：生成 claim 的 agent 不得给同一 claim 判 `source-verified`。若无法派发独立 verifier，笔记只能标 `verification_status: unverified`，强 claim 必须降级。
- **验证不等于复现**：`source-verified` 只说明 primary source 确实包含该 claim；不得写成结果已被独立复现或领域已形成共识。
- **prepare-only 零共享写入**：prepare-only agent 禁止改 Papers、queue、日志、BibTeX cache 与 survey-updates；共享写入只由 coordinator 串行 commit。
- **语言规范**：正文用中文撰写，英文技术术语（模型名、方法名、benchmark 名）保持英文，不做翻译。

## Verify

- [ ] **direct 模式**：`Papers/YYMM-ShortTitle.md` 已创建且正文 >200 字；**prepare-only**：artifact envelope 含完整 `note_markdown` 且未发生共享写入
- [ ] frontmatter 的 title、authors、date_publish 字段非空
- [ ] frontmatter 的 `content_scope` 与 `verification_status` 合法
- [ ] **YAML 前置校验通过**：所有含冒号的字段值已加双引号（title、venue 等）
- [ ] **direct 模式引用身份已固化**：frontmatter 的 `cite_key` 非空，`references/bibtex-cache.bib` 含该 key；prepare-only 保留空 cite_key 供 coordinator commit
- [ ] **Evidence Ledger 完整**：Summary / Key Results 中的高风险数字与比较均有 claim row、locator 和状态
- [ ] **独立性**：source-verified claim 由不同于 Finder 的 verifier 检查；否则状态为 unverified
- [ ] Summary 节非空且不超过 3 句话
- [ ] **direct 模式**日志与 survey 记账已完成；**prepare-only** 未修改日志、queue、BibTeX 或 survey-updates

## Examples

**示例 1：从 arXiv URL 消化论文**

```
/paper-digest "https://arxiv.org/abs/2603.08127"
```

执行过程：
1. WebFetch `https://arxiv.org/abs/2603.08127` 获取 abstract、作者、日期等元数据
2. WebFetch `https://arxiv.org/html/2603.08127` 获取 HTML 全文
3. 提炼 Problem / Method / Results / Strengths & Weaknesses
4. Glob `Papers/2603-*.md` 检查是否重复
5. 读取 `references/tags.md` 选取合适 tags
6. Grep `Papers/` 和 `Ideas/` 搜索相关笔记
7. 写入 `Papers/2603-EvoScientist.md`
8. 追加日志到 `Workbench/logs/2026-03-26.md`

输出文件：`Papers/2603-EvoScientist.md`

---

**示例 2：从论文标题搜索**

```
/paper-digest "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion"
```

执行过程：
1. WebSearch `"Diffusion Policy: Visuomotor Policy Learning via Action Diffusion" site:arxiv.org`
2. 获取 arXiv 链接，WebFetch 抓取内容
3. 后续步骤同示例 1

输出文件：`Papers/2303-DiffusionPolicy.md`

---

**示例 3：从本地 PDF 消化**

```
/paper-digest "/Users/qingli/Downloads/roboclaw_2025.pdf"
```

执行过程：
1. Read `/Users/qingli/Downloads/roboclaw_2025.pdf` 读取 PDF 内容
2. 从内容中提取元数据（title、authors、date、venue）
3. 后续步骤同示例 1

---

**示例 4：从 blog URL 消化**

```
/paper-digest "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/"
```

执行过程：
1. WebFetch 抓取 blog 页面内容
2. 提取元数据：title、author（Lilian Weng）、date_publish、venue 填 `Lilian Weng Blog`
3. institute、code 无法确定则留空
4. 提炼 Problem / Method（核心论点）/ Key Results（关键结论）/ Strengths & Weaknesses
5. 后续去重、tag 选择、Connections 搜索、保存、日志同论文流程

输出文件：`Papers/2411-RewardHacking.md`
