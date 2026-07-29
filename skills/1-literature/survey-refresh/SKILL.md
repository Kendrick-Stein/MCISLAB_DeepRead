---
name: survey-refresh
description: >
  当 Workbench/survey-updates.json 中某 survey 积压了新消化的论文（autoresearch 检测到 ≥5 篇
  或最老条目超 7 天），或 Supervisor 说"刷新一下 XX survey"时，
  把新论文笔记增量合并进对应 Topics/*-Survey.md，并同步刷新其 DomainMap。
argument-hint: "<survey-name，如 CUA-Survey>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Purpose

信息流闭环的消费端：paper-digest 只记账（survey-updates.json），本 skill 负责把积压的新论文
增量合并进 survey，让 survey 随日常阅读越来越完善，而不必重跑完整 literature-survey。
与 literature-survey 的分工：本 skill **不做任何外部搜索**，只消化库内已 digest 的新笔记；
全量调研（含外部检索）仍由 literature-survey 承担。

## Steps

### Step 1：取 pending 列表

```bash
python3 scripts/survey_updates.py pending --survey {survey-name}
```

- 为空则终止：向调用方报告"无待处理条目"。
- 超过 8 篇时只取最早的 8 篇（按 added_at），其余留给下一轮——避免单次 context 过长。

### Step 2：读取 survey 现状

用 Read 读取 `Topics/{survey-name}.md` 全文，记住其章节结构、分类框架、已覆盖的论文集合、
Key Takeaways / Open Questions。

### Step 3：逐篇读新论文笔记

对 pending 中每篇，用 Read 读取 `Papers/` 笔记全文，提取：核心贡献、关键数据、
与 survey 现有分类的关系（落入哪个既有小节？是否挑战某个既有结论？是否开辟新分类？）。

同时读取 `content_scope`、`verification_status` 与 `## Evidence Ledger`：

- `source-checked`：可使用 ledger 中 `source-verified` 的 claim，但仍只能表述为“原文一致性已核查”，不能写成独立复现。
- `partial`：只使用 source-verified 行；其他 claim 必须降级或省略。
- `unverified` / 缺少字段的 legacy note：可作为论文存在性与主题归类证据，但不得凭它新增关键数字、共识、Key Takeaway 或 Validated Gap。
- `abstract-only`：不得支撑机制、失败条件、benchmark 横向比较或强 novelty claim。

处理 `CUA-Survey` 时，额外建立一行分类记录再决定落点：

| 字段 | 允许值 / 判断 |
|:--|:--|
| `platform` | web / mobile / desktop / cross-platform / hybrid GUI+API/CLI |
| `task_level` | grounding / step / app workflow / cross-app long-horizon / interactive-proactive |
| `primary_section` | model-architecture / training-RL / data-task / environment-runtime / evaluation-verifier / reliability-safety-HCI |
| `environment_setting` | offline / self-hosted / live / real-device |
| `verifier_type` | programmatic / interactive agent / visual-rubric judge / human / none |
| `evidence_strength` | direct end-to-end / component-only / adjacent transferable evidence |

每篇论文只能有一个 `primary_section`；最多在 1-2 个其他章节 cross-link。纯 Deep Research、
通用 Agentic RL、通用 VLM/World Model 或 terminal/tool sandbox 若没有直接 GUI 交互证据，
不得因共享模型、算法或 environment 术语硬并入 GUI core。

**相关性检查**：keyword 匹配存在误报。若某篇论文与本 survey 主题明显无关
（读笔记后判断），跳过它：不并入 survey，但在 Step 6 一并 clear（附一句跳过理由记入日志），
避免它永远滞留 pending。

### Step 4：增量更新 survey

用 Edit 修改 `Topics/{survey-name}.md`（遵循 literature-survey 的增量更新规则）：

1. 把每篇新论文以 `[[wikilink]]` 并入对应小节，附一句话定位（贡献 + 与既有工作的关系）。
2. 若新证据**推翻或削弱**某既有结论，修改该结论并标注新证据来源；未被挑战的原有内容一律保留。若新论文是既有"共识"的独立反例，把该结论从共识**降级为争议**并记录冲突双方，而非只追加一句。
3. 若多篇新论文形成新 pattern，可新增小节；更新 Key Takeaways / Open Questions。
4. 更新 frontmatter：`date_updated` 设为今天，`papers_analyzed` 增加新并入篇数。
5. 若本轮改变 Overview、benchmark 横向判断、Key Takeaways 或 Open Problems，同步更新 `## Key Evidence Matrix` 的 state、claim IDs/locators 与 contradiction boundary；普通增量无需新增矩阵行。

`CUA-Survey` 的额外更新规则：

- 按 canonical 六层结构落位，不新建按单篇论文或临时热词命名的平行 taxonomy。
- Benchmark 数字必须对应 Evidence Ledger 中 `source-verified` 的 claim row，并同时写清 environment setting、verifier、step budget（笔记有记录时）与是否同 backbone 对照。
- 只有新论文改变已有判断时才修改 Key Takeaways / Open Problems；普通增量只更新 primary subsection 或矩阵。
- `papers_analyzed` 按唯一 `Papers/` wikilink 口径机械复核，不把 redirect survey 的旧统计相加。

### Step 4.5：配图刷新（条件触发，可选）

仅当本轮发生**结构性变化**时执行——新增小节、分类框架重构、多篇论文形成新 pattern、
时间线/族谱延长到需要重画：

- 调用 `academic-diagram` skill 为变化的章节新增或重画脉络图（分类总览、方法演进时间线、
  对比结构图），渲染 PNG 到 `assets/figures/`（命名沿用 `{survey缩写}-{章节}-{主题}.png`），
  在 survey 对应小节以 `![[name.png]]` 嵌入。
- 已有配图与新结构矛盾（分类变了、论文归属变了）→ 必须重画或撤下，不得让图文不一致过夜。
- 普通增量（论文并入既有小节、无新 pattern）**不画图**——配图服务结构理解，不是装饰。

### Step 5：刷新 DomainMap（若有）

读 survey frontmatter 的 `domain_map` 字段：

- 为 `null` 或对应 `DomainMaps/{name}.md` 不存在 → 跳过本步。
- 否则用 Edit 更新该 DomainMap：在文件末尾维护一个 `## 近期格局变化` 小节
  （不存在则创建），追加/合并本轮变化的 2-4 条要点（新 pattern、被修正的结论），
  每条附 survey 与论文的 `[[wikilink]]`。仅当本轮确有格局级变化时才写；
  单纯"多了几篇论文"不算。

### Step 6：清账并记录

```bash
python3 scripts/survey_updates.py clear --survey {survey-name} --papers "Papers/a.md" "Papers/b.md"
```

（`--papers` 为空格分隔的多个路径，包含本轮**实际并入的**与**判定无关而跳过的**条目。）
然后在 `Workbench/logs/YYYY-MM-DD.md` 追加：

```markdown
### [HH:MM] survey-refresh — {survey-name}
- **merged**: <N 篇：[[...]], [[...]]>
- **skipped**: <M 篇及一句话理由；无则"无">
- **changes**: <survey 结构性变化一句话；无则"仅增量并入">
- **domain_map**: <刷新了哪个 / skipped>
```

## Guard

- 禁止外部搜索（WebSearch/WebFetch 不在 allowed-tools 中，这是设计而非疏漏）。
- 不删除 survey 中未被新证据推翻的原有结论；修改结论必须标注推翻它的论文 wikilink。
- 单轮最多并入 8 篇；不一次清空大积压。
- 与 survey 主题明显无关的 pending 论文：跳过不并入，但必须 clear 并记录理由——不得硬并入，也不得留在 pending。
- `status: merged` 或 `keywords: []` 的 redirect survey 不得恢复为独立更新目标；其内容统一写入 `merged_into` 指向的 canonical survey。
- 本 skill 是 DomainMaps 的唯一自动写入方；只写 `## 近期格局变化` 小节，
  不改 DomainMap 其他部分（Established Knowledge 等仍由 Human 经 queue Review 晋升）。
- 只 clear 本轮实际处理（并入或跳过）的条目；未处理的留在 pending。
- **引用 ≠ 继承/支持**：并入新论文时，其与既有工作的关系以内容判断（introduces/extends/contradicts/fails-to-reproduce…），不因它引用了某篇就自动记为支持或继承。
- **不升格未验证结论**：本 skill 不做外部检索；库内无独立验证的结论标"库内暂无独立验证"，不得表述为共识或写"首次/无人研究"。
- **Legacy note 限权**：缺 Evidence Ledger 的旧笔记可以保持既有引用，但本轮不得仅据它升级共识、关键数字或 Validated Gap；需要升级时交由下一次 full literature-survey 的 verification gate。

## Verify

- [ ] survey 的 `date_updated` 为今天，`papers_analyzed` 已更新（仅计并入篇数，不含跳过）
- [ ] 本轮每篇并入论文在 survey 正文中有 `[[wikilink]]`
- [ ] survey-updates.json 中本轮条目（含跳过的）已清除
- [ ] 日志已追加（merged/skipped/changes/domain_map 四项齐全）
- [ ] 并入的关键结论可溯到全文笔记；未把仅 abstract 或单篇支持的结论表述为共识
- [ ] 新增关键数字均对应 source-verified claim row；partial/unverified/legacy note 未被用于升级强结论
- [ ] 若高层判断发生变化，Key Evidence Matrix 已同步；普通增量未制造冗余 claim rows
- [ ] 若本轮有结构性变化：受影响章节的配图已新增/重画/撤下，无图文不一致

## Examples

`survey-refresh CUA-Survey` → pending 6 篇 → 并入 5 篇（2 篇进"Grounding"小节、
3 篇进"RL 训练"）+ 1 篇误报跳过（VLM 安全论文与 GUI 无关）→ 刷新 DomainMaps/GUI-Agent.md
近期格局变化 → 清账 6 篇 → 日志。
