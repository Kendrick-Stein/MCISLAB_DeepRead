---
name: survey-refresh
description: >
  当 Workbench/survey-updates.json 中某 survey 积压了新消化的论文（autoresearch 检测到 ≥5 篇
  或最老条目超 7 天），或 Supervisor 说"刷新一下 XX survey"时，
  把新论文笔记增量合并进对应 Topics/*-Survey.md，并同步刷新其 DomainMap。
argument-hint: "<survey-name，如 GUIAgent-Survey>"
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

**相关性检查**：keyword 匹配存在误报。若某篇论文与本 survey 主题明显无关
（读笔记后判断），跳过它：不并入 survey，但在 Step 6 一并 clear（附一句跳过理由记入日志），
避免它永远滞留 pending。

### Step 4：增量更新 survey

用 Edit 修改 `Topics/{survey-name}.md`（遵循 literature-survey 的增量更新规则）：

1. 把每篇新论文以 `[[wikilink]]` 并入对应小节，附一句话定位（贡献 + 与既有工作的关系）。
2. 若新证据**推翻或削弱**某既有结论，修改该结论并标注新证据来源；
   未被挑战的原有内容一律保留。
3. 若多篇新论文形成新 pattern，可新增小节；更新 Key Takeaways / Open Questions。
4. 更新 frontmatter：`date_updated` 设为今天，`papers_analyzed` 增加新并入篇数。

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
- 本 skill 是 DomainMaps 的唯一自动写入方；只写 `## 近期格局变化` 小节，
  不改 DomainMap 其他部分（Established Knowledge 等仍由 Human 经 queue Review 晋升）。
- 只 clear 本轮实际处理（并入或跳过）的条目；未处理的留在 pending。

## Verify

- [ ] survey 的 `date_updated` 为今天，`papers_analyzed` 已更新（仅计并入篇数，不含跳过）
- [ ] 本轮每篇并入论文在 survey 正文中有 `[[wikilink]]`
- [ ] survey-updates.json 中本轮条目（含跳过的）已清除
- [ ] 日志已追加（merged/skipped/changes/domain_map 四项齐全）

## Examples

`survey-refresh GUIAgent-Survey` → pending 6 篇 → 并入 5 篇（2 篇进"Grounding"小节、
3 篇进"RL 训练"）+ 1 篇误报跳过（VLM 安全论文与 GUI 无关）→ 刷新 DomainMaps/GUI-Agent.md
近期格局变化 → 清账 6 篇 → 日志。
