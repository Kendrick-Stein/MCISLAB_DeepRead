---
name: mindflow-import
description: 从 MindFlow GitHub repo 提取已有的论文笔记和 Survey，去重后合并到本地 vault。当用户说"导入 MindFlow""从 MindFlow 同步""mindflow import"时触发。
argument-hint: "[--papers | --surveys | --all | topic filter like VLA/WorldModel]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

## Purpose

MindFlow (https://github.com/liqing-ustc/mindflow) 是一个结构高度相似的知识库（175 篇论文 + 12 个 Survey）。本 skill 自动提取其中的高质量内容，去重后合并到本地 vault，避免重复消化同一论文。

**格式兼容性**: 两者使用相同的命名规范（YYMM-ShortTitle.md）、wikilink 格式（`[[2410-Pi0|π0]]`）、frontmatter 结构（YAML with title/authors/tags/rating）、Obsidian callout 语法（`> [!summary]`）。

## Steps

### Step 1：解析参数

从用户输入解析任务类型：
- `--papers` — 仅导入论文笔记
- `--surveys` — 仅导入 Survey
- `--all` — 全量导入（论文 + Survey）
- `topic filter` — 按 topic 筛选（如 "VLA", "WorldModel", "EmbodiedReasoning"）

若未指定，默认 `--all`。

### Step 2：Vault 去重检查

1. 用 Glob 扫描 `Papers/*.md`，提取已知论文清单（YYMM-ShortTitle）
2. 用 Glob 扫描 `Topics/*-Survey.md`，提取已知 Survey 清单
3. 读取 `skills/1-literature/mindflow-import/config.json` 获取 tag mapping
4. 建立"已知清单" set

### Step 3：获取 MindFlow 内容清单

用 gh CLI 获取 MindFlow repo 目录列表：

```bash
# 获取 Papers 列表
gh api /repos/liqing-ustc/mindflow/contents/Papers --jq '.[].name' | grep -E '\.md$'

# 获取 Topics 列表
gh api /repos/liqing-ustc/mindflow/contents/Topics --jq '.[].name' | grep -E '\.md$'
```

与"已知清单"对比，生成**待导入列表**（跳过已存在的文件）。

### Step 4：批量导入论文

对每篇待导入论文：

1. **获取内容**:
   ```bash
   gh api /repos/liqing-ustc/mindflow/contents/Papers/{filename} --jq '.content' | base64 -d
   ```

2. **解析 frontmatter**: 提取 title, authors, institutes, tags, rating

3. **Tag 映射**:
   - 读取 config.json 中的 tag_mapping
   - 将 MindFlow tag 映射到本地等效 tag
   - 若无映射，保留原 tag

4. **去重保护**: 再次检查目标文件是否存在，若存在则跳过

5. **写入**:
   ```python
   Write Papers/{filename}
   ```

### Step 5：合并 Survey

对每个待导入 Survey：

**情况 A：本地已存在同名 Survey**
1. 读取两者内容
2. 合并策略：
   - Overview: 保留本地版本
   - 技术路线: 追加 MindFlow 中独有的路线
   - Key Takeaways: 合并两者，去重
   - Open Problems: 合并两者，去重
   - 参考文献: 合并两者，去重
   - 调研日志: 新增 MindFlow-import 记录
3. 用 Edit 增量更新

**情况 B：本地不存在该 Survey**
1. 直接 Write 新文件

### Step 6：记录导入日志

追加到 `Workbench/logs/YYYY-MM-DD.md`：

```markdown
### [HH:MM] mindflow-import
- **input**: {task type} | topic: {topic filter or "all"}
- **stats**: 导入 N 篇论文，跳过 M 篇（已存在），合并 K 个 Survey
- **papers_imported**: [list of paper filenames]
- **surveys_merged**: [list of survey filenames]
- **status**: success
```

## Guard

- **不覆盖已有笔记**: 若 `Papers/YYMM-ShortTitle.md` 已存在，跳过并记录，不得覆盖
- **Tag 映射**: MindFlow tags 与本地 tags 可能不同，优先映射到本地等效 tag（见 config.json），无法映射时保留原 tag
- **Survey 合而非覆**: 对已存在的 Survey，增量合并而非覆盖，保留本地 Overview
- **依赖 gh CLI**: 需要 `gh` 已安装且已 `auth login`（检查 `gh auth status`）
- **base64 解码**: gh API 返回 content 是 base64 编码，需 `base64 -d` 解码

## Verify

- [ ] 导入的论文笔记已出现在 `Papers/` 目录
- [ ] 无已有笔记被覆盖（检查 mtime）
- [ ] Survey 合并后内容比合并前更完整
- [ ] 日志已追加到 `Workbench/logs/YYYY-MM-DD.md`

## Examples

**示例 1：全量导入**

```
/mindflow-import --all
```

执行过程：
1. 扫描本地 Papers/（190+ 篇）和 Topics/（已有 Survey）
2. 获取 MindFlow Papers/（175 篇）和 Topics/（12 个 Survey）
3. 去重后导入 ~90 篇新论文
4. 合并 5+ 个 Survey（VLA-Survey, WorldModel-Survey 等）
5. 输出：新增 ~90 个文件，更新 5 个 Survey

**示例 2：按 topic 筛选**

```
/mindflow-import VLA
```

执行过程：
1. 获取 MindFlow Papers/ 列表
2. 过滤 tags 包含 "VLA" 的论文
3. 仅导入 VLA 相关论文 + VLA-Survey
4. 输出：新增 ~20 个文件，更新 VLA-Survey

**示例 3：仅导入 Survey**

```
/mindflow-import --surveys
```

执行过程：
1. 获取 MindFlow Topics/ 列表（12 个 Survey）
2. 逐个检查本地是否存在
3. 存在则合并，不存在则新建
4. 输出：合并/新增 12 个 Survey
