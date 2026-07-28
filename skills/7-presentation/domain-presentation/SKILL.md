---
name: domain-presentation
description: >
  使用 guizang-ppt-skill 生成 Domain Map 的 HTML 可视化展示，可在网站直接浏览。
  当用户要求为某个 domain map 生成 PPT/可视化展示，或说"做个 domain presentation"、
  "生成领域地图网页"时使用。
argument-hint: "<DomainName，对应 DomainMaps/{DomainName}.md>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Domain Map Presentation

## Purpose

将 `DomainMaps/{DomainName}.md` 转化为可视化 HTML 演示文稿（10-15 页），发布到 Quartz 站
`static/presentations/` 下供直接浏览。输入是已有的 Domain Map 笔记，输出是 HTML 演示 +
一条待 Human 审核的导航链接建议（经 queue）。

## Steps

### Step 1 · 选择 Domain Map

读取目标 Domain Map 文件：

```
DomainMaps/{DomainName}.md
```

确认 Domain Map 包含：
- 核心定义
- 技术架构（mindmap）
- 研究路线
- Benchmarks
- 关键洞察
- 待解决问题

### Step 2 · 规划演示结构

基于 Domain Map 内容规划 PPT 页数和布局：

| Domain Map 章节 | 推荐布局 | 页数 |
|:----------------|:---------|:-----|
| 核心定义 | 开场封面 / 数据大字报 | 1-2 |
| 技术架构 | 章节幕封 + Pipeline | 2-3 |
| 研究路线 | 左文右图 / 图文混排 | 3-5 |
| Benchmarks | 数据大字报 / 图片网格 | 1-2 |
| 关键洞察 | 大引用 / 悬念问题 | 1-2 |
| 待解决问题 | 悬念收束 / 问题页 | 1 |

**页数估算**: 10-15 页（约 15-20 分钟浏览）

### Step 3 · 准备输出目录

```bash
mkdir -p website/content/static/presentations/{DomainName}/images
```

**注意**: 必须放在 `static/presentations/` 目录下，因为 Quartz 会处理 `content/` 目录的 `.html` 文件去掉扩展名。

### Step 4 · 调用 guizang-ppt-skill

读取 `~/.claude/skills/guizang-ppt-skill/SKILL.md`，按其工作流执行：

1. **拷贝模板**: `assets/template.html` → `website/content/static/presentations/{DomainName}/index.html`
2. **选择主题**: 推荐 🌊 靛蓝瓷（科技/研究风格）
3. **填充内容**: 使用 layouts.md 的骨架，填入 Domain Map 内容
4. **自检**: 对照 checklist.md
5. **预览**: 本地浏览器测试

### Step 5 · 集成到网站

1. 确认 HTML 文件位于 `website/content/static/presentations/{DomainName}/index.html`
2. Rebuild 网站: `npx quartz build`

### Step 6 · 在 queue Review 提建议

不直接修改 Domain Map 文件（DomainMaps 的直接编辑仅由 survey-refresh 的 `## 近期格局变化`
小节或 Human 完成）。通过 queue helper 把建议写入 `Workbench/queue.json` 的 Human review：

```bash
python3 skills/1-literature/daily-papers/queue_ops.py enqueue-review \
  --insight-ref "website/content/static/presentations/{DomainName}/index.html" \
  --title "Add DomainMap presentation link: {DomainName}" \
  --claim "建议在 DomainMaps/{DomainName}.md 增加已生成 HTML 演示的导航链接" \
  --suggested-map "DomainMaps/{DomainName}.md" \
  --source "domain-presentation"
```

Human 批准后再补入：`[🌐 在线浏览 HTML 演示](/static/presentations/{DomainName}/index.html)`。

## Guard

- **不直接修改 DomainMaps/ 文件**——导航链接建议只经 queue review 提交，Human 批准后才补入
  （DomainMaps 的直接编辑仅由 survey-refresh 或 Human 完成）。
- HTML 必须放在 `website/content/static/presentations/` 下——`content/` 里的 `.html` 会被
  Quartz 处理掉扩展名，导致路径失效。
- 演示内容只基于 Domain Map 已有内容组织重排，**不新增/虚构领域结论**。

## Verify

- [ ] `website/content/static/presentations/{DomainName}/index.html` 存在且本地可打开
- [ ] `npx quartz build` 通过，无构建错误
- [ ] queue.json 中已有对应的 Human review 条目
- [ ] 页数在 10-15 页区间，封面/架构/路线/数据/问题五类页齐备

## 输出位置

- **HTML 文件**: `website/content/static/presentations/{DomainName}/index.html`
- **图片目录**: `website/content/static/presentations/{DomainName}/images/`

## 质量标准

1. **封面页**: Domain 名称 + 核心定义一句话
2. **架构页**: Mindmap 转化为 Pipeline/两列布局
3. **研究路线**: 每条路线 1 页，关键洞察突出
4. **数据页**: Benchmarks 用表格或数据大字报展示
5. **问题页**: Open problems 作为悬念收束

## 示例调用

```
/domain-presentation HyperbolicManifold
```

生成 `static/presentations/HyperbolicManifold/index.html`
