# Following：学者跟踪信道设计

- **日期**: 2026-07-30
- **状态**: 设计已确认，待实现
- **动机来源**: Supervisor 指出现有检索全部是 topic-pull，领域专家的新作会被系统性漏掉

## 1. 问题

现有全部论文发现信道集中在 `skills/1-literature/daily-papers/fetch_and_score.py`：

| 源 | 方式 |
|:---|:---|
| HuggingFace Daily/Trending | `api/daily_papers`，靠社区 upvote |
| arXiv | API 按 category（cs.CV/AI/LG/RO/CL）拉取 + 关键词打分 |
| OpenAlex 期刊 | 按 ISSN 列举 IJCV/TNNLS/TPAMI |
| CVF | 爬 openaccess listing（CVPR2026/ICCV2025/WACV2026） |

补充信道：公众号（`scripts/wechat_search`，二手线索）、`search_openalex_topic` 关键词检索。

**这些全部是 topic-pull（按关键词/venue 打分）。系统没有任何 person-pull 信道。**

关键词打分会系统性漏掉两类论文：标题不含监控关键词的（`Mind2Web 2`、`AgentNet` 这类命名）、以及 HF 上没热度且不在监控 venue 的。领域专家的新作恰恰高频落在这两类里。

## 2. 数据侦察结论

对 `Papers/` 985 篇笔记的实测，两条结论直接约束设计：

**(a) 姓名字符串不能做主键。** 5330 个 distinct author，最高频次仅 13（Sergey Levine 13 / Chelsea Finn 12 / Quan Vuong 9）——作者列表长，senior author 信号被稀释，裸频次分辨率极低。更致命的是同名污染：`Yang Liu` 11 次、`Wei Liu` 6 次、`Hao Li` 6 次，几乎肯定是多人被合并。另有 `Multiple Authors`(7)、`et al.`(6) 等脏数据。

**(b) ID 覆盖率足够建档。** 711 篇有 `arxiv_id`、194 篇有 `doi`、274 篇两者皆无（多为 CVF 与网页版报告）。arXiv 论文自带标准 DOI `10.48550/arXiv.XXXX.XXXXX`，可直接构造；OpenAlex 支持 `filter=doi:a|b|c` 批量（50 个/请求），985 篇约 20 个请求。无 ID 的 274 篇走 `title.search` 兜底。

## 3. 已确认的决策

| 决策点 | 结论 |
|:---|:---|
| 名单规模 | 30-50 人，**全自动阈值筛选**，月度重算，不手工维护 |
| 数据源 | **A+B 混合，OpenAlex author ID 为主键**；Google Scholar 只存链接不做日常抓取 |
| review 触发 | **积压 ≥3 篇新论文才重写**；平时只脚本刷新表格（零 token） |
| 论文纳入 | **方向绑定**：只收该学者在其被跟踪方向上的产出，不全盘接受 |
| 淘汰 | `last_paper_date` 超 **12 个月** → `dormant`，退出轮询但保留 page |

### 3.1 为什么不用 Google Scholar 做日常抓取

Scholar 是 Supervisor 最初指向的源（`scholar.google.com/citations?user=...`），覆盖度确实最全（含非 arXiv 产出、作者自维护）。但它没有官方 API，反爬严重，50 profile/周大概率触发 CAPTCHA。把日常信道建在反爬对抗上，会在某天**静默失效**——静默失效的信道比没有信道更糟，因为它让人以为覆盖仍在。

因此 Scholar 降级为兜底：某学者 arXiv + OpenAlex 长期无更新但怀疑有产出时，手动跑一次 `scripts/lexmount_fetch.py dump --engine chrome_cdp`。不进日常流程。

## 4. 架构

```
Following/                        # 新建 vault 顶层目录，Explorer 自动收录
  _index.md                       # 总览：按方向分组的活跃学者表 + 休眠区
  Sergey-Levine.md                # 每人一页（跨方向的人也只有一页）
  ...
Workbench/scholars.json           # 唯一状态源
skills/1-literature/scholar-track/
  SKILL.md
  build_roster.py                 # 建档 / 月度重算，零 token
  fetch_followed.py               # 日更抓取 + 刷新 page 脚本化章节，零 token
  config.json                     # 权重、阈值、inactive_months、review_trigger
```

### 4.1 状态文件 `Workbench/scholars.json`

定位对齐 `Workbench/survey-updates.json`（积压计数 + 触发阈值）。每人一条记录：

| 字段 | 用途 |
|:---|:---|
| `openalex_id` | 主键，如 `A5024...` |
| `display_name` / `aliases` | 展示与 arXiv 检索用 |
| `affiliation` / `orcid` / `scholar_url` | 档案信息，`scholar_url` 可空、可手填 |
| `track_directions` | 被跟踪的方向列表，如 `["GUI Agent", "AI Agent"]` |
| `known_coauthors` | arXiv 同名过滤用的合作者 OpenAlex ID 集合 |
| `vault_papers` | 该学者在 vault 内的笔记路径 + 角色 |
| `score` / `position_profile` | 入选分数与一作/末作/中间计数 |
| `status` | `active` \| `dormant` |
| `last_paper_date` | 淘汰判据 |
| `pending_since_review` | review 重写触发计数 |
| `seen_paper_keys` | 已收录论文的 `paper_key`，日更去重 |
| `off_direction_count` | 自上次 review 重写以来、被方向过滤排除的论文数（用于覆盖度交代），review 重写后清零 |

## 5. 名单构建 `build_roster.py`（月度 / 手动）

1. 扫 `Papers/*.md` frontmatter，收 `arxiv_id` / `doi`；arXiv id 构造 `10.48550/arXiv.<id>`
2. OpenAlex 批量反查 works（`filter=doi:a|b|c`，50/请求）；无 ID 的 274 篇走 `title.search` 兜底，匹配失败则跳过并记录
3. 每篇 work 取 `authorships` → **author ID + `author_position`（first/middle/last）+ institutions**
   > 这一步同时解决同名污染：通过论文反解人，而非姓名字符串匹配。`Yang Liu` 会被拆成若干不同 OpenAlex ID。
4. 打分：`score = 3×末作 + 2×一作 + 0.5×中间`，再乘主线聚焦度（该作者名下 vault 笔记的 tag 熵，越专注系数越高）
5. 入选条件：`score ≥ 6` 且 `vault 论文 ≥ 3` 且 至少 1 篇一作或末作
6. 拉 `api.openalex.org/authors/A...` 补机构、ORCID、works_count；收集高频合作者写入 `known_coauthors`
7. 判定 `track_directions`（见 §6）

阈值以命中 30-50 人为准，首次跑完需人工看分布再定标。

## 6. 方向绑定

跟踪单位不是「这个人」，而是「这个人在方向 D 上的产出」。

**方向判定（自动）**：该学者名下 vault 笔记的 `title + tags` 归一化后（`gui-agent` → `gui agent`，小写、连字符转空格）打到 `Workbench/config/team-config.json` 四个 `interests` 各自的 `keywords` 上；某方向命中 **≥2 篇** → 该方向进 `track_directions`。字面匹配不上的 tag 由 `config.json` 里的显式 `tag_direction_map` 兜底。

**新论文过滤**：学者 X 跟踪方向 D，其新论文只用 **D 的 keywords** 打分（title + abstract；arXiv 与 OpenAlex 均提供摘要，后者复用现有 `reconstruct_abstract`），过 `direction_min_score`（本 skill 独立配置，与 daily-papers 的全局 `min_score` 无关）才收录。

效果示例：
- Levine 的 VLA / manipulation 新作 → 收（因 Embodied AI 被跟踪）
- 同一人的纯 offline RL 理论文 → 不收
- 某 GUI 专家转做 video generation → 不收

**覆盖度交代**：page 的最新论文表下固定一行「本期另有 N 篇非跟踪方向产出（未收录）」。不收进来但不假装不存在——方向漂移是 review 最该捕捉的信号之一。

> **待验证参数**：「≥2 篇命中」的阈值。太松则每人横跨四方向、过滤形同虚设；太紧则漏掉刚转方向的人。`build_roster.py` 首跑后按实际分布调整。

## 7. 日常抓取 `fetch_followed.py`（每日，零 token）

对每个 `status: active` 的学者双路查：

**路 1 — arXiv `au:"Name"`**（当天新鲜）
用 `known_coauthors` 做同名过滤：命中 ≥1 已知合作者才直接收；零命中的进 `.suspect` 待人工判定，**不静默丢弃**。

**路 2 — OpenAlex `filter=author.id:A...,from_publication_date:`**（权威，补非 arXiv 的期刊/会议产出）

两路结果用现有 `paper_key()` 归并，与 `Workbench/daily/.history.json` 及 `seen_paper_keys` 去重，再过 §6 的方向过滤。

**下游处理**：通过方向过滤的论文全部
1. 写入该学者 page 的「最新论文」表
2. 注入 daily-papers 候选池，`source: followed:<slug>`，**绕过全局 `min_score`**（方向过滤已经把关，不再用全局关键词二次判断）
3. `pending_since_review += 1`

**流量安全阀**：`max_followed_per_day` 默认 10。超出部分按 followed-score 排序**延后到次日，不丢弃**，且在日志中显式记录延后数量——不做静默截断。

## 8. Scholar page

```markdown
---
name: Sergey Levine
openalex_id: A5024...
scholar_url: "https://scholar.google.com/citations?user=..."
affiliation: UC Berkeley
track_directions: ["Embodied AI"]
position_profile: "末作为主 (末9 / 一0 / 中4)"
status: active
tracked_since: 2026-07-30
last_refresh: 2026-07-30
review_updated: 2026-07-30
pending_since_review: 0
---
## 研究主线 review        ← LLM 写，pending ≥3 才重写

（300-500 字。主线是什么、近期转向、与本 vault 四个方向的接口、
 他工作里的内部矛盾或未解问题。不做成果罗列。）

## 最新论文               ← 脚本刷新，零 token

| date | title | 角色 | vault |
|------|-------|------|-------|
| 07-28 | Foo | 末作 | [[2607-Foo]] |
| 07-14 | Bar | 中间 | 未消化 |

自上次 review 更新以来另有 2 篇非跟踪方向产出（未收录）。

## vault 内已有笔记 (13)  ← 脚本刷新

[[2604-OpenVLA]] · [[2512-RT2]] · ...
```

review 由 subagent 基于**该学者在 vault 内的笔记全文 + 新论文摘要**撰写，遵守项目 evidence grounding 纪律：未读全文的论文不得写成定论，推测须标注。

## 9. 休眠淘汰

`last_paper_date` 超过 `inactive_months`（默认 **12**）→ `status: dormant`：

- 退出日常轮询
- page 保留，frontmatter 标 `status: dormant`
- `_index.md` 中移入「休眠」区

月度 rebuild 时若重新有产出则自动复活。**不物理删除**——学者停更一年后重新活跃是常态。

## 10. 站点集成

`website/quartz.layout.ts` 的两处 `order` 数组（`defaultContentPageLayout` 与 `defaultListPageLayout`）加入 `"Following"`，位置在 `"Papers"` 之后。`Following/` 不在 `quartz.config.ts` 的 `ignorePatterns` 内，自动上站。`_index.md` 作为 Following 首页。

## 11. 与现有 skill 的关系

| Skill | 改动 |
|:---|:---|
| `scholar-track`（新） | Step1 建档 / Step2 日更 / Step3 review 重写 / Step4 淘汰 |
| `daily-papers` | Step 1 后插一步调 `fetch_followed.py`，候选合流；`config.json` 加 `followed` 源标识 |
| `autoresearch` | 调度中加入日更抓取；有 `pending_since_review ≥ 3` 的学者时排 review 重写 |
| `paper-digest` | 不改。笔记落库后由下次 `fetch_followed.py` 自动回填 page 链接 |
| `CLAUDE.md` | 目录结构节补 `Following/`；skill 表补 `scholar-track` |

## 12. 验收标准

- [ ] `build_roster.py` 跑通 → 名单落在 30-50 人；抽查 5 人确认非同名合并（`Yang Liu` 类必须被拆分或落选）
- [ ] 每人 `track_directions` 非空且与其 vault 论文主题一致；抽查 5 人
- [ ] `fetch_followed.py` 跑通 → 至少 1 名学者出现 vault 中尚无的新论文
- [ ] 方向过滤生效 → 至少 1 篇非跟踪方向论文被正确排除并计入 `off_direction_count`
- [ ] 3 个 page 建好；`npx quartz build` 后 Explorer 中 Following 可见
- [ ] 至少 1 篇 review 写出，通过 evidence 纪律检查（无未读全文的定论）
- [ ] `Workbench/scholars.json` 在中断后可恢复（partial state 可读）

## 13. 明确不做（YAGNI）

- 不做 Google Scholar 日常抓取（理由见 §3.1）
- 不做引用数 / h-index 排序展示——与「跟踪研究主线」无关
- 不做跨学者的横向对比页面
- 不做手工名单维护 UI；名单由脚本按阈值产生，人只调阈值
