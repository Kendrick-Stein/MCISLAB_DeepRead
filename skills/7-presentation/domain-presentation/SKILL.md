---
name: domain-presentation
description: 使用 guizang-ppt-skill 生成 Domain Map 的 HTML 可视化展示，可在网站直接浏览。当用户要求为某个 domain map 生成 PPT/可视化展示，或说"做个 domain presentation"、"生成领域地图网页"时使用。
---

# Domain Map Presentation

将 Domain Map 转化为可视化 HTML 演示文稿，可在 Quartz 站直接浏览。

## 工作流

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

### Step 6 · 创建导航链接

在 Domain Map 文件中添加演示链接：

```markdown
## 可视化演示

[🌐 在线浏览 HTML 演示](/static/presentations/{DomainName}/index.html) — 杂志风格翻页展示
```

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