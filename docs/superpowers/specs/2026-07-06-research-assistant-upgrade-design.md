# ReadPaperMachine 升级设计：信息流闭环 + 写作链 + News 专栏 + 可 clone 模板化

- **日期**: 2026-07-06
- **状态**: 待 Supervisor review
- **决策记录**: DomainMaps 保留但自动化；四个 workstream 全做；产品化（人人可 clone）为近期目标；repo 策略 = 单 repo + init 脚本

---

## 1. 背景与问题

系统现状（2026-07-06 摸底）：

1. **功能已建但未激活**：`auto-cite`（给 LaTeX 提供 evidence-driven cite 建议）已实现但未 symlink 注册，无法通过 `/auto-cite` 触发。skill 注册依赖手动 `ln -sf` 到 `~/.claude/skills/`，机器绑定且易漏。
2. **write-only 冗余**：`DomainMaps/` 自 2026-04-28 后无实质更新（仅死链修复），但被 7 个 skill 引用为维护对象；`Reports/` 近半为 autoresearch 例行 pulse。维护成本在付，价值无人收。
3. **信息流断点**：`daily-papers → queue → paper-digest` 链路通，但 digest 完成后不回写 `Topics/*-Survey`。literature-survey 已有增量更新机制（SKILL.md L43/L113），但只有手动重跑 survey 才触发。
4. **能力缺口**：无英文 LaTeX Related Work 写作能力（draft-section 输出中文 vault 笔记）；无非论文信息源（新闻/博客/公众号）摄入能力。
5. **不可 clone**：研究兴趣硬编码散在 CLAUDE.md / agenda.md / team-config.json 三处；skill 注册机器绑定；个人数据与框架混合无初始化路径。

## 2. 目标

1. 新论文消化后自动驱动 survey 增量迭代（survey 越读越完善）。
2. 打通 vault → LaTeX 投稿写作链（cite list、Related Work、主题报告）。
3. 非论文信息源进入知识循环（News 专栏）。
4. 任何人 clone 本 repo 后，改一个 config + 跑一个脚本即可拥有自己的 research assistant。

**非目标（out of scope）**：PPT 生成新 skill（已有 domain-presentation/academic-slides 可后续对接）；框架 plugin 化；拆分双 repo；改动 autoresearch 核心循环结构。

---

## 3. Part 0 — 基础设施（先做，其余 Part 依赖它）

### 3.1 Skill 注册去机器化

- 在 repo 内 `.claude/skills/` 为每个 vault skill 建**相对路径 symlink**（如 `.claude/skills/paper-digest -> ../../skills/1-literature/paper-digest`），symlink 提交进 git。project-level skills 目录已被验证生效（lark-* skills 即在此）。
- 新增 `scripts/sync-skills.sh`：扫描 `skills/*/*/SKILL.md`，校验每个 skill 在 `.claude/skills/` 有有效 symlink；发现未注册（如当前的 auto-cite）或悬空 symlink 时报错列出。作为手动/CI 检查。
- 迁移后清理 `~/.claude/skills/` 中指向本 repo 的旧 symlink，避免 user-level 与 project-level 重复注册。

### 3.2 研究兴趣单源化

- `Workbench/config/team-config.json` 升级为**唯一兴趣来源**，新增/整理字段：
  - `interests`: 研究方向列表（名称 + 关键词组），供 daily-papers / news-digest / literature-survey 打分使用（替代现 `collector.keywords` 平铺列表，保留向后兼容读取）。
  - `news.sources`: News 信息源列表 `[{name, type: rss|web, url, lang}]`。
- CLAUDE.md 的"研究兴趣"段改为指向 config（保留一句概述），消除三处硬编码。
- 涉及 keywords 的 skill（daily-papers `fetch_and_score.py` 等）改为从 config 读取。

## 4. Part 1 — 信息流闭环（digest → survey 自动迭代）

### 4.1 记账：paper-digest 回写归属

- paper-digest SKILL.md 末尾新增一步：笔记写完后，将其 tags/topic 与 `Topics/*-Survey.md` 匹配（匹配依据：survey frontmatter 新增 `keywords` 字段；无匹配则静默跳过，不阻塞 digest）。
- 匹配结果追加到 `Workbench/survey-updates.json`：`{survey, paper, added_at}`。文件缺失时自动初始化。

### 4.2 消费：新 skill `survey-refresh`

- 位置 `skills/1-literature/survey-refresh/SKILL.md`，参数 `<survey-name>`。
- 流程：读 `survey-updates.json` 中该 survey 的 pending 论文 → 逐篇读笔记 → 按 literature-survey 既有增量更新规则（Edit 补充新论文、刷新分析、保留仍有效内容）更新 survey → 清除已处理条目。
- **不做外部搜索**——与 literature-survey 的分工：survey-refresh 只消化库内新增，literature-survey 负责全量调研含外部检索。
- Guard：不删除 survey 中未被新证据推翻的原有结论；单次处理论文数上限（避免超长 context）。

### 4.3 DomainMaps 自动化（保留但不再独立维护）

- survey-refresh 末步：若存在对应 `DomainMaps/{Name}.md`（映射写在 survey frontmatter `domain_map` 字段），同步刷新其"近期格局变化"小节。
- 审查现引用 DomainMaps 的 7 个 skill：将其中"维护/更新 DomainMap"的职责移除或改为只读引用，DomainMaps 的唯一写入方变为 survey-refresh。

### 4.4 autoresearch 接线

- READ STATE 增读：`Workbench/survey-updates.json`、最近的 `News/`。
- JUDGE 表增信号：某 survey pending ≥5 篇，或最老 pending 超 7 天 → 执行 survey-refresh。

## 5. Part 2 — LaTeX 写作链

### 5.1 激活 auto-cite

Part 0 的 sync-skills 覆盖。无代码改动。

### 5.2 新 skill `related-work`

- 位置 `skills/4-writing/related-work/SKILL.md`，参数 `<draft.tex 路径> [topic] [段落预算]`。
- 流程：
  1. 跑 `assign_cite_keys.py` + `build_paper_index.py` + `latex-citation-enhancer`（确保 references.bib 覆盖候选论文）。
  2. 读 draft.tex 理解论文贡献定位；读相关 `Topics/*-Survey` 提取领域分类叙事结构。
  3. Evidence-driven 选支撑论文：按叙事分组从 `paper_index.json` 取候选，读 summary 确认真实支撑后纳入（复用 auto-cite 的判断原则）。
  4. 产出**英文 LaTeX** Related Work 章节，`\cite{key}` 全部来自 references.bib；每段附注释块标注 evidence 来源，供 Supervisor review 后删除。
- Guard：不引用库外论文、不编造 cite key；若领域公认必引论文不在库内，输出 "missing citations" 清单并建议先 digest，而非硬写。
- 与 draft-section 分工：draft-section = 中文 vault 笔记章节；related-work = 英文投稿 LaTeX 章节。

### 5.3 literature-survey 增加 `--vault-only` 模式

- 跳过外部搜索步骤，仅综合库内已读论文，输出报告到 `Reports/YYYY-MM-DD-{Topic}-Report.md`。
- 覆盖"根据 paper 库生成某方面报告"需求，不新建 skill（YAGNI）。

## 6. Part 3 — News 专栏

### 6.1 新 skill `news-digest` + `News/` 目录

- 位置 `skills/1-literature/news-digest/SKILL.md`，参数 `[今日 / 过去N天]`，架构复刻 daily-papers 三段式：
  1. **抓取打分（零 token）**：新脚本 `fetch_news.py` 读 config `news.sources`（RSS 直连；网页走现有 fetch fallback；公众号由用户经 RSSHub/wechat2rss 转 RSS 后配入），按 `interests` 关键词打分，输出候选 JSON。
  2. **分流**：快扫标题+摘要，选出值得精读的条目。
  3. **精读+沉淀**：产出 `News/YYYY-MM-DD.md`（摘要 + 点评 + 原文链接）；含重要 idea/发布的条目在该文件内写成可 wikilink 的小节，并在相关 survey/agenda evidence 中回链。
- Guard：News 条目只作为线索与观点来源，**不得作为 agenda evidence 的唯一支撑**（非 peer-reviewed）；抓取失败的源跳过并记入当日 log，不阻塞。

### 6.2 接入循环

autoresearch READ STATE 读最近 News（Part 1 已列）；News 中提到的重要论文可直接入 queue 走 paper-digest。

## 7. Part 4 — 可 clone 模板化（单 repo + init 脚本）

- **`scripts/init.sh`**：交互向导——询问研究方向与关键词 → 写入 `team-config.json` → 生成 `Workbench/agenda.md` Mission 骨架。
  - `--fresh` 选项：清空个人数据目录（Papers/ Topics/ Ideas/ Reports/ Meetings/ Experiments/ News/ 及 Workbench 状态文件），保留框架（skills/ references/ Templates/ docs/ scripts/ .claude/）；执行前要求确认并提示先建 git commit。
- **README 更新**：quick-start 三步 = clone → `scripts/init.sh --fresh` → `/daily-papers` 或 `/autoresearch`。
- 本 repo 自身即模板：不 fresh 则 740 篇笔记作为参考示例保留。

---

## 8. 数据流总览（改造后）

```
外部论文源 ──daily-papers──▶ queue.json ──paper-digest──▶ Papers/笔记
                                              │
                                              ▼ (记账)
非论文源 ──news-digest──▶ News/        survey-updates.json
     │                                        │
     ▼                                        ▼ (pending≥5, autoresearch 触发)
  agenda/queue 线索                    survey-refresh ──▶ Topics/Survey 增量迭代
                                              │
                                              ▼ (自动副产品)
                                       DomainMaps/ 刷新

Topics/Survey + Papers/ + references.bib ──▶ auto-cite / related-work / --vault-only 报告
```

## 9. 错误处理原则

- 记账/匹配类步骤（4.1、6.1 抓取）失败一律**降级不阻塞**主流程，记入当日 log。
- `survey-updates.json` 损坏/缺失 → 重建空结构。
- related-work 遇 bib 覆盖不足 → 先补 bib，仍缺则列 missing citations，不编造。

## 10. 实施顺序与验收

| 顺序 | 内容 | 验收（Verify） |
|---|---|---|
| 1 | Part 0：`.claude/skills` symlink 迁移 + sync-skills.sh + config 单源化 | `/auto-cite` 可触发；sync-skills.sh 全绿；daily-papers 从 config 读关键词跑通 |
| 2 | Part 1：digest 记账 + survey-refresh + DomainMaps 自动化 + autoresearch 接线 | 消化 1 篇新论文 → survey-updates.json 出现条目 → 跑 survey-refresh 后 survey 与 DomainMap 均更新 |
| 3 | Part 2：related-work skill + literature-survey --vault-only | 对一个样例 .tex 产出可编译的 Related Work（所有 \cite 在 bib 中）；vault-only 报告落 Reports/ |
| 4 | Part 3：news-digest + News/ | 配 2 个 RSS 源跑通一期 News/YYYY-MM-DD.md |
| 5 | Part 4：init.sh + README | 临时目录 clone + `init.sh --fresh` 后跑 `/daily-papers` 成功 |

每个新/改 skill 均按 `references/skill-protocol.md` 补齐 Purpose/Steps/Guard/Verify。
